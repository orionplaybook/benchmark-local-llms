"""Memory sampling (engine process footprint + system memory), cross-platform."""
from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import threading
import time
from typing import Callable, Dict, List, Optional

SYSTEM = platform.system()


def _run(cmd, timeout=10) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def list_processes() -> List[tuple]:
    """[(pid, cmdline)]"""
    me = os.getpid()
    out = []
    if SYSTEM == "Windows":
        raw = _run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process | Select ProcessId,CommandLine,ExecutablePath | ConvertTo-Json -Compress"], 30)
        try:
            for p in json.loads(raw):
                cmd = p.get("CommandLine") or p.get("ExecutablePath") or ""
                out.append((int(p["ProcessId"]), cmd))
        except (ValueError, TypeError):
            pass
    else:
        for line in _run(["ps", "-axo", "pid=,command="]).splitlines():
            line = line.strip()
            if not line:
                continue
            pid, _, cmd = line.partition(" ")
            if pid.isdigit():
                out.append((int(pid), cmd.strip()))
    return [(p, c) for p, c in out if p != me]


def process_bytes(pids: List[int]) -> Dict[int, int]:
    """Physical memory per pid. macOS: phys_footprint (includes GPU/Metal allocations)."""
    if not pids:
        return {}
    res = {}
    if SYSTEM == "Darwin":
        cmd = ["footprint", "-f", "bytes", "--noCategories"]
        for p in pids:
            cmd += ["-p", str(p)]
        cur = None
        for line in _run(cmd, 10).splitlines():
            m = re.search(r"\[(\d+)\]:.*Footprint:\s*(\d+)\s*B", line)
            if m:
                cur = int(m.group(1))
                res[cur] = int(m.group(2))
        # llama.cpp maps GGUF weights from disk: they count in RSS but not in phys_footprint,
        # while MLX/Metal allocations show in phys_footprint but not RSS. Take the larger of the two.
        for line in _run(["ps", "-o", "pid=,rss=", "-p", ",".join(map(str, pids))]).splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit():
                pid, rss = int(parts[0]), int(parts[1]) * 1024
                res[pid] = max(res.get(pid, 0), rss)
    elif SYSTEM == "Windows":
        ids = ",".join(map(str, pids))
        raw = _run(["powershell", "-NoProfile", "-Command",
                    f"Get-Process -Id {ids} -ErrorAction SilentlyContinue | Select Id,PrivateMemorySize64,WorkingSet64 | ConvertTo-Json -Compress"], 15)
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                data = [data]
            for p in data:
                res[int(p["Id"])] = int(max(p.get("PrivateMemorySize64") or 0, p.get("WorkingSet64") or 0))
        except (ValueError, TypeError):
            pass
    else:
        for p in pids:
            try:
                with open(f"/proc/{p}/status") as f:
                    m = re.search(r"VmRSS:\s*(\d+)", f.read())
                    if m:
                        res[p] = int(m.group(1)) * 1024
            except OSError:
                pass
    return res


def system_memory() -> dict:
    """{'total','used','swap_used'} bytes (best effort)."""
    if SYSTEM == "Darwin":
        out = _run(["vm_stat"])
        page = 16384
        m = re.search(r"page size of (\d+)", out)
        if m:
            page = int(m.group(1))
        v = {k.strip().lower(): int(n) for k, n in re.findall(r"^(.+?):\s+(\d+)\.", out, re.M)}
        used = (v.get("pages wired down", 0) + v.get("anonymous pages", 0) - v.get("pages purgeable", 0)
                + v.get("pages occupied by compressor", 0)) * page
        sw = _run(["sysctl", "-n", "vm.swapusage"])
        m = re.search(r"used\s*=\s*([\d.]+)M", sw)
        total = _run(["sysctl", "-n", "hw.memsize"]).strip()
        return {"total": int(total) if total.isdigit() else None, "used": used,
                "wired": v.get("pages wired down", 0) * page,
                "swap_used": int(float(m.group(1)) * 1024 * 1024) if m else None}
    if SYSTEM == "Windows":
        raw = _run(["powershell", "-NoProfile", "-Command",
                    "$o=Get-CimInstance Win32_OperatingSystem;@{t=$o.TotalVisibleMemorySize;f=$o.FreePhysicalMemory}|ConvertTo-Json"])
        try:
            d = json.loads(raw)
            return {"total": d["t"] * 1024, "used": (d["t"] - d["f"]) * 1024, "swap_used": None}
        except (ValueError, KeyError, TypeError):
            return {"total": None, "used": None, "swap_used": None}
    try:
        with open("/proc/meminfo") as f:
            d = {k: int(v) * 1024 for k, v in re.findall(r"^(\w+):\s+(\d+)", f.read(), re.M)}
        return {"total": d.get("MemTotal"), "used": d.get("MemTotal", 0) - d.get("MemAvailable", 0),
                "swap_used": d.get("SwapTotal", 0) - d.get("SwapFree", 0)}
    except OSError:
        return {"total": None, "used": None, "swap_used": None}


def method_name() -> str:
    return {"Darwin": "max(footprint,rss)", "Windows": "process-private-bytes"}.get(SYSTEM, "process-rss")


class Sampler:
    """Background sampler. Measures processes whose command line matches `match`."""

    def __init__(self, match: Callable[[str], bool], interval: float = 0.25):
        self.match = match
        self.interval = max(interval, 1.0 if SYSTEM == "Windows" else 0.1)
        self.timeline: List[dict] = []
        self.phase = "idle"
        self.detail = None
        self._pids: List[int] = []
        self._pid_refresh = 0.0
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._t0 = time.perf_counter()
        self._lock = threading.Lock()

    def _refresh_pids(self, force=False):
        now = time.perf_counter()
        if force or now - self._pid_refresh > 3.0:
            self._pids = [p for p, c in list_processes() if self.match(c)]
            self._pid_refresh = now

    def measure(self) -> dict:
        self._refresh_pids()
        per = process_bytes(self._pids)
        sysm = system_memory()
        return {"t": round(time.perf_counter() - self._t0, 3), "engine_bytes": sum(per.values()) if per else None,
                "system_used_bytes": sysm.get("used"), "swap_used_bytes": sysm.get("swap_used"),
                "wired_bytes": sysm.get("wired"),
                "phase": self.phase, "detail": self.detail}

    def _loop(self):
        while not self._stop.is_set():
            start = time.perf_counter()
            try:
                s = self.measure()
                with self._lock:
                    self.timeline.append(s)
            except Exception:
                pass
            self._stop.wait(max(0.0, self.interval - (time.perf_counter() - start)))

    def start(self):
        self._refresh_pids(force=True)
        self._t0 = time.perf_counter()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def elapsed(self) -> float:
        return round(time.perf_counter() - self._t0, 3)

    def set_phase(self, phase: str, detail: Optional[str] = None):
        self.phase = phase
        self.detail = detail

    def snapshot(self) -> dict:
        self._refresh_pids(force=True)
        return self.measure()

    def settle(self, timeout: float = 30.0, tolerance: float = 0.01) -> dict:
        """Wait until engine memory stops changing (3 consecutive readings within tolerance)."""
        deadline = time.perf_counter() + timeout
        last, stable = None, 0
        snap = self.snapshot()
        while time.perf_counter() < deadline:
            snap = self.snapshot()
            cur = snap.get("engine_bytes") or 0
            if last is not None and last > 0 and abs(cur - last) / last <= tolerance:
                stable += 1
                if stable >= 3:
                    break
            else:
                stable = 0
            last = cur
            time.sleep(0.5)
        return snap

    def discard(self, t_from: float, t_to: float) -> int:
        """Flag samples in [t_from, t_to] as discarded (taken while another model was loaded). Returns the count."""
        n = 0
        with self._lock:
            for s in self.timeline:
                if t_from <= s.get("t", -1) <= t_to:
                    s["discarded"] = True
                    n += 1
        return n

    def peaks(self) -> dict:
        """Peaks over the samples that count (discarded ones excluded)."""
        with self._lock:
            kept = [s for s in self.timeline if not s.get("discarded")]
        eng = [s["engine_bytes"] for s in kept if s.get("engine_bytes")]
        sysu = [s["system_used_bytes"] for s in kept if s.get("system_used_bytes")]
        swap = [s["swap_used_bytes"] for s in kept if s.get("swap_used_bytes") is not None]
        return {"peak_bytes": max(eng) if eng else None,
                "system_used_peak_bytes": max(sysu) if sysu else None,
                "swap_used_delta_bytes": (max(swap) - swap[0]) if swap else None}
