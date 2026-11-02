"""Third-party files the dashboard needs. They aren't committed: the first `bench setup`, `bench dashboard`,
`bench publish` or `bench run` downloads the pinned version and checks its SHA-256. After that the
dashboard works offline. To upgrade, change the version, URL and hash together (see dashboard/vendor/README.md)."""
from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

from . import http
from .config import DASHBOARD_DIR

CHARTJS_VERSION = "4.4.1"
CHARTJS_URL = f"https://cdnjs.cloudflare.com/ajax/libs/Chart.js/{CHARTJS_VERSION}/chart.umd.min.js"
CHARTJS_SHA256 = "81ffafe13c37e1b25793b020d446f4d9739b949dadb7f9f79d709a0cad781c2f"
CHARTJS_PATH = DASHBOARD_DIR / "vendor" / "chart.umd.min.js"

_failed = False   # one download attempt per process: an offline overnight run shouldn't retry after every model


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_chartjs(quiet: bool = False, path: Path = CHARTJS_PATH) -> bool:
    """True when the pinned Chart.js is in place. Never raises: without it the dashboard shows tables but no charts."""
    global _failed
    try:
        if path.exists():
            if _sha256(path) == CHARTJS_SHA256:
                return True
            path.unlink()   # never serve or publish a file that failed the check, even if no replacement arrives
    except OSError:
        pass
    if _failed:
        return False
    if not quiet:
        print(f"  Downloading Chart.js {CHARTJS_VERSION} for the dashboard (once)...")
    try:
        data = http.get_bytes(CHARTJS_URL, timeout=30)
    except Exception as e:   # offline, DNS, HTTP error...
        _failed = True
        print(f"  ! Couldn't download Chart.js ({e}). The dashboard works without charts until the next try.")
        return False
    if hashlib.sha256(data).hexdigest() != CHARTJS_SHA256:
        _failed = True
        print(f"  ! The downloaded Chart.js doesn't match the expected SHA-256; not using it ({CHARTJS_URL}).")
        return False
    tmp = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".part")   # unique per process
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
        return True
    except OSError as e:   # read-only folder, disk full...
        _failed = True
        print(f"  ! Couldn't save Chart.js to {path} ({e}). The dashboard works without charts.")
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass
        return False
