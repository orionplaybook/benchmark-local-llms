"""Minimal stdlib HTTP helpers: JSON requests, SSE and NDJSON streaming."""
from __future__ import annotations

import http.client
import json
import socket
import threading
import urllib.error
import urllib.request
from typing import Iterator, Optional, Tuple

USER_AGENT = "benchlm/0.1 (+local benchmark tool)"


class HTTPError(Exception):
    def __init__(self, status: int, body: str, url: str):
        super().__init__(f"HTTP {status} for {url}: {body[:300]}")
        self.status = status
        self.body = body
        self.url = url


class Cancelled(Exception):
    """A streaming request was aborted with Cancel.fire()."""


class Cancel:
    """Lets another thread abort a streaming request. fire() shuts the request's socket down, so a read that is
    blocked waiting for the server (e.g. during a long prefill, before any byte has arrived) returns at once and
    the stream raises Cancelled. Once fired it stays fired: a later request made with it is refused unsent."""

    def __init__(self):
        self._lock = threading.Lock()
        self._sock = None
        self.fired = threading.Event()
        self.reason = ""

    def fire(self, reason: str = "") -> None:
        with self._lock:
            if not self.fired.is_set():
                self.reason = reason
                self.fired.set()
            sock = self._sock
        _shutdown(sock)

    def check(self) -> None:
        if self.fired.is_set():
            raise Cancelled(self.reason)

    def _attach(self, sock) -> None:
        with self._lock:
            self._sock = sock
        if self.fired.is_set():
            _shutdown(sock)

    def _detach(self) -> None:
        with self._lock:
            self._sock = None


def _shutdown(sock) -> None:
    if sock is None:
        return
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass


def _open_stream(url: str, payload, headers: Optional[dict], timeout: float, cancel: Optional[Cancel]):
    """POST with http.client so the socket is known from the start (a cancel must work even while the server
    hasn't sent its response headers yet). Returns (connection, response)."""
    from urllib.parse import urlsplit
    if cancel is not None:
        cancel.check()
    u = urlsplit(url)
    cls = http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection
    conn = cls(u.hostname or "localhost", u.port, timeout=timeout)
    hdrs = {"User-Agent": USER_AGENT, "Accept": "*/*", "Content-Type": "application/json"}
    if headers:
        hdrs.update({k: v for k, v in headers.items() if v})
    try:
        conn.connect()
        if cancel is not None:
            cancel._attach(conn.sock)
        conn.request("POST", (u.path or "/") + ("?" + u.query if u.query else ""),
                     body=json.dumps(payload).encode("utf-8"), headers=hdrs)
        resp = conn.getresponse()
    except (OSError, http.client.HTTPException):
        conn.close()
        if cancel is not None:
            cancel._detach()
            cancel.check()
        raise
    if resp.status >= 400:
        body = resp.read().decode("utf-8", "replace")
        conn.close()
        if cancel is not None:
            cancel._detach()
        raise HTTPError(resp.status, body, url)
    return conn, resp


def _stream_lines(url, payload, headers, timeout, cancel):
    """Yield raw response lines; the error/EOF caused by Cancel.fire() becomes Cancelled."""
    conn, resp = _open_stream(url, payload, headers, timeout, cancel)
    try:
        try:
            for raw in resp:
                if cancel is not None and cancel.fired.is_set():
                    break
                yield raw
        except (OSError, ValueError, http.client.HTTPException):
            if cancel is None or not cancel.fired.is_set():
                raise
        if cancel is not None:
            cancel.check()
    finally:
        conn.close()
        if cancel is not None:
            cancel._detach()


def _request(url: str, method: str = "GET", payload=None, headers: Optional[dict] = None,
             timeout: float = 30.0):
    data = None
    hdrs = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if headers:
        hdrs.update({k: v for k, v in headers.items() if v})
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            body = ""
        raise HTTPError(e.code, body, url) from None


def get_json(url: str, headers: Optional[dict] = None, timeout: float = 30.0):
    with _request(url, headers=headers, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def post_json(url: str, payload, headers: Optional[dict] = None, timeout: float = 600.0):
    with _request(url, "POST", payload, headers, timeout) as r:
        raw = r.read().decode("utf-8")
        return json.loads(raw) if raw.strip() else {}


def get_text(url: str, headers: Optional[dict] = None, timeout: float = 30.0,
             max_bytes: int = 4_000_000) -> Tuple[str, str]:
    """Returns (text, final_url)."""
    with _request(url, headers=headers, timeout=timeout) as r:
        raw = r.read(max_bytes)
        charset = r.headers.get_content_charset() or "utf-8"
        return raw.decode(charset, "replace"), r.geturl()


def stream_sse(url: str, payload, headers: Optional[dict] = None, timeout: float = 1800.0,
               cancel: Optional[Cancel] = None) -> Iterator[Tuple[str, dict]]:
    """POST and yield (event_name, data_dict) from a text/event-stream response."""
    event, data_lines = "message", []
    for raw in _stream_lines(url, payload, headers, timeout, cancel):
        line = raw.decode("utf-8", "replace").rstrip("\r\n")
        if not line:
            if data_lines:
                blob = "\n".join(data_lines)
                data_lines = []
                if blob.strip() == "[DONE]":
                    break
                try:
                    yield event, json.loads(blob)
                except ValueError:
                    yield event, {"raw": blob}
            event = "message"
            continue
        if line.startswith(":"):
            continue
        if line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            data_lines.append(line[5:].lstrip())
    if data_lines:
        try:
            yield event, json.loads("\n".join(data_lines))
        except ValueError:
            pass


def stream_ndjson(url: str, payload, headers: Optional[dict] = None, timeout: float = 1800.0,
                  cancel: Optional[Cancel] = None) -> Iterator[dict]:
    for raw in _stream_lines(url, payload, headers, timeout, cancel):
        line = raw.strip()
        if line:
            yield json.loads(line.decode("utf-8"))


def port_open(base_url: str, timeout: float = 1.5) -> bool:
    from urllib.parse import urlparse
    u = urlparse(base_url)
    try:
        with socket.create_connection((u.hostname or "localhost", u.port or 80), timeout=timeout):
            return True
    except OSError:
        return False
