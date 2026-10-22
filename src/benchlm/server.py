"""`bench dashboard --live`: tiny local web server (127.0.0.1 only)."""
from __future__ import annotations

import json
import re
import socket
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from . import db as dbm
from .config import DASHBOARD_DIR, RAW_DIR


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quiet
        pass

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/db":
            return self._json(dbm.merged_view(dbm.load()))
        m = re.fullmatch(r"/api/raw/([A-Za-z0-9._-]+)", path)
        if m:
            f = RAW_DIR / f"{m.group(1)}.json"
            if f.exists():
                with open(f, "r", encoding="utf-8") as fh:
                    return self._json(json.load(fh))
            return self._json({"error": "not found"}, 404)
        return super().do_GET()

    def end_headers(self):
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def _free_port(preferred: int) -> int:
    for port in [preferred] + list(range(preferred + 1, preferred + 20)):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return 0


def serve(port: int = 8765, open_browser: bool = True) -> None:
    port = _free_port(port)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(DASHBOARD_DIR)))
    url = f"http://127.0.0.1:{httpd.server_address[1]}/"
    print(f"\n  Dashboard running at {url}")
    print("  It always shows the latest data/results.json (use the Refresh button after a new run).")
    print("\n  ▶ Press Ctrl+C to stop the server and exit.\n", flush=True)
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopping dashboard server… done. Bye!")
    finally:
        httpd.server_close()
