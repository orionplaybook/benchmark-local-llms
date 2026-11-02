"""Make sure nothing else is loaded while benchmarking, and restore afterwards."""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Callable, List, Optional

from .engines.base import Engine


def all_loaded(engines: List[Engine]) -> List[dict]:
    out = []
    for e in engines:
        try:
            out.extend(e.loaded())
        except Exception as ex:
            print(f"  ! could not list loaded models in {e.name}: {ex}")
    return out


def unload_everything(engines: List[Engine], verbose: bool = True) -> List[dict]:
    """Unload every loaded model in every engine. Returns instances that could NOT be unloaded."""
    by_id = {e.id: e for e in engines}
    failed = []
    for inst in all_loaded(engines):
        eng = by_id[inst["engine"]]
        try:
            eng.unload(inst)
            if verbose:
                print(f"    unloaded {eng.name}: {inst['model_key']}")
        except Exception as ex:
            print(f"    ! failed to unload {eng.name}: {inst['model_key']} ({ex})")
            failed.append(inst)
    # verify
    time.sleep(1.0)
    still = [i for i in all_loaded(engines)]
    return still if still else failed


def print_manual_instructions(engines: List[Engine], instances: List[dict]) -> None:
    by_id = {e.id: e for e in engines}
    print("\n  The benchmark needs a clean machine, but these models are still loaded:")
    for inst in instances:
        print(f"    • {by_id[inst['engine']].unload_hint(inst)}")
    print("  Unload them (and pause anything that reloads them, e.g. Hermes / n8n), then re-run `./bench run`.\n")


def restore(engines: List[Engine], instances: List[dict]) -> None:
    by_id = {e.id: e for e in engines}
    if not instances:
        return
    print("\n  Restoring models that were loaded before the benchmark…")
    for inst in instances:
        eng = by_id.get(inst["engine"])
        if not eng:
            continue
        try:
            eng.restore(inst)
            print(f"    ✓ reloaded {eng.name}: {inst['model_key']}")
        except Exception as ex:
            print(f"    ! could not reload {eng.name}: {inst['model_key']} ({ex})")


def intruder_name(inst: dict) -> str:
    return f"{inst['engine']}:{inst['model_key']}"


class Watchdog:
    """Polls engines every `interval` seconds and records any loaded model that isn't the one under test.

    While a test is armed (arm()), finding an intruder calls the test's on_intruder(event) at once, from the
    watchdog thread, so the test can abandon its in-flight request instead of running to completion."""

    def __init__(self, engines: List[Engine], interval: float = 10.0):
        self.engines = engines
        self.interval = interval
        self.allowed: set = set()
        self.events: List[dict] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._seen: set = set()          # intruders already recorded (until they are unloaded)
        self._armed = None               # (test label, on_intruder callback)
        self._loading = None             # (engine id, names of the model under test) while it is being loaded
        self.counter = 0

    def allow(self, engine_id: str, instance_id: Optional[str]):
        """The model under test, by its exact instance id (known once its load has returned)."""
        self.allowed = {(engine_id, instance_id)} if instance_id else set()
        self._loading = None

    def allow_loading(self, engine_id: str, names) -> None:
        """While the model under test is loading, its instance already shows up in the engine (LM Studio lists it
        while a slow load is still running, e.g. 45 s for a Splash model) but its id isn't known yet: accept an
        instance of this engine whose model key or id is one of `names`. allow() ends this window."""
        self._loading = (engine_id, {n for n in names if n})

    def _is_allowed(self, inst: dict) -> bool:
        if (inst["engine"], inst["instance_id"]) in self.allowed:
            return True
        loading = self._loading
        return bool(loading and inst["engine"] == loading[0]
                    and (inst.get("model_key") in loading[1] or inst.get("instance_id") in loading[1]))

    def arm(self, test: str, on_intruder: Callable[[dict], None]) -> None:
        with self._lock:
            self._armed = (test, on_intruder)

    def disarm(self) -> None:
        with self._lock:
            self._armed = None

    def forget(self) -> None:
        """Call after unloading intruders, so a model loaded again later is recorded as a new event."""
        with self._lock:
            self._seen = set()

    def intruders(self) -> List[dict]:
        return [i for i in all_loaded(self.engines) if not self._is_allowed(i)]

    def check(self) -> Optional[dict]:
        """Look once. Returns the event (new or already recorded) when an intruder is loaded, else None."""
        found = self.intruders()
        if not found:
            return None
        with self._lock:
            keys = {(i["engine"], i["instance_id"]) for i in found}
            armed = self._armed
            test = armed[0] if armed else None
            if keys <= self._seen and self.events:
                event = self.events[-1]
            else:
                self._seen |= keys
                self.counter += 1
                names = [intruder_name(i) for i in found]
                event = {"t": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                         "detail": f"other model loaded{' during ' + test if test else ''}: {', '.join(names)}",
                         "test": test, "intruders": names, "action": None, "instances": found}
                self.events.append(event)
            if armed:
                self._armed = None       # one signal per test attempt
        if armed:
            armed[1](event)
        return event

    def _loop(self):
        while not self._stop.wait(self.interval):
            try:
                self.check()
            except Exception:
                pass

    def start(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
