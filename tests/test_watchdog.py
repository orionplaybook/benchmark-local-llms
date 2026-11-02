"""Intruder handling: cancel the in-flight request, discard the attempt, restart, cap restarts (fake engine).
Run from benchmark-local-llms/:  python3 -m unittest discover -s tests"""
import http.server
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from benchlm import http as bhttp, hygiene  # noqa: E402
from benchlm.engines.base import Engine, Turn  # noqa: E402
from benchlm.peakctx import analyze  # noqa: E402
from benchlm.runner import IntruderPersists, ModelRunner  # noqa: E402
from benchlm.suite import Suite  # noqa: E402

REQUEST_S = 5.0          # a fake request takes this long unless it is cancelled
POLL_S = 0.05            # watchdog interval in tests

PROFILE = {"name": "test", "hash": "t", "context_length": 8192, "warmup": 1, "cold_cycles": 1, "repeats": 1,
           "temperature": 0, "top_p": 1, "top_k": 1, "reasoning_modes": ["off"], "reasoning_extra_tokens": 0,
           "min_long_prompt_tokens": 0, "settle_timeout_s": 0, "cleanup_wait_s": 0}
MODEL = {"model_uid": "fake:model", "key": "model", "display_name": "Fake", "format": "gguf"}


class FakeEngine(Engine):
    id = "fake"
    name = "Fake"

    def __init__(self, stops_on_disconnect=True, intrude_at=None, intrude_always=False):
        super().__init__("http://fake")
        self.stops_on_disconnect = stops_on_disconnect
        self.intrude_at = set(intrude_at or [])   # request labels during which an intruder gets loaded
        self.intrude_always = intrude_always      # an agent keeps reloading it
        self.instance = None
        self.intruders = []
        self.loads = 0
        self.unloaded = []
        self.labels = []
        self.prompts = []

    def info(self):
        return {"name": "Fake"}

    def loaded(self):
        out = [{"engine": "fake", "model_key": "intruder", "instance_id": i, "type": "llm"} for i in self.intruders]
        if self.instance:
            out.append({"engine": "fake", "model_key": "model", "instance_id": self.instance, "type": "llm"})
        return out

    def load(self, model, profile):
        self.loads += 1
        self.instance = f"inst{self.loads}"
        return {"instance_id": self.instance, "load_time_s": 0.01, "client_load_time_s": 0.01, "load_config": {}}

    def unload(self, instance):
        self.unloaded.append(instance["instance_id"])
        if instance["instance_id"] in self.intruders:
            self.intruders.remove(instance["instance_id"])
        elif instance["instance_id"] == self.instance:
            self.instance = None

    def resolve_reasoning(self, model, mode):
        return None

    def chat(self, instance_id, model, system_prompt, user_text, state, reasoning, max_tokens, profile,
             on_phase=None, cancel=None):
        label = self.current_label()
        self.labels.append(label)
        self.prompts.append((label, system_prompt))
        quick = label.startswith("probe:cold") or label.startswith("probe:warm")
        if self.intrude_always and not quick or label in self.intrude_at:
            self.intrude_at.discard(label)
            self.intruders.append(f"intruder{len(self.unloaded)}")
        duration = 0.01 if quick or not self.slow(label) else REQUEST_S
        self._slow = self._slow - {label}            # only the first try of a request is slow
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < duration:
            if cancel is not None and cancel.fired.is_set():
                raise bhttp.Cancelled(cancel.reason)
            time.sleep(0.005)
        t = Turn()
        t.ttft_s, t.total_s, t.prompt_tokens, t.completion_tokens = 0.005, 0.01, 100, 10
        t.text, t.finish_reason = "ok", "stop"
        return t

    def slow(self, label):
        return self.intrude_always or label in self._slow

    _slow = set()
    current_label = None   # set by the test to read the runner's current label


class FakeSampler:
    def __init__(self):
        self.timeline, self.t0 = [], time.perf_counter()

    def elapsed(self):
        return round(time.perf_counter() - self.t0, 3)

    def _sample(self):
        s = {"t": self.elapsed(), "engine_bytes": 1000 + len(self.timeline), "phase": "x"}
        self.timeline.append(s)
        return s

    def set_phase(self, *a):
        self._sample()

    def settle(self, *a):
        return self._sample()

    snapshot = settle

    def start(self):
        pass

    def stop(self):
        pass

    def discard(self, a, b):
        for s in self.timeline:
            if a <= s["t"] <= b:
                s["discarded"] = True

    def peaks(self):
        kept = [s["engine_bytes"] for s in self.timeline if not s.get("discarded")]
        return {"peak_bytes": max(kept) if kept else None}


def make_runner(eng, tests=("short",), max_restarts=3):
    r = ModelRunner([eng], eng, dict(MODEL), dict(PROFILE), Suite(), {"machine_id": "m"}, ["off"], list(tests),
                    repeats=1, max_restarts=max_restarts)
    r.sampler = FakeSampler()
    r.watchdog = hygiene.Watchdog([eng], interval=POLL_S)
    eng.current_label = lambda: r.current_label
    return r


def run_quiet(runner):
    saved = {}
    with mock.patch("benchlm.runner.dbm.save_raw", side_effect=lambda rid, raw: saved.update(raw) or "raw/x.json"), \
            mock.patch("benchlm.runner.log"):
        run = runner.run()
    return run, saved


class InterruptTests(unittest.TestCase):
    def test_intruder_cancels_request_and_test_restarts(self):
        eng = FakeEngine(intrude_at={"short/off/r0/t2"})
        eng._slow = {"short/off/r0/t2"}
        t0 = time.perf_counter()
        run, raw = run_quiet(make_runner(eng))
        self.assertLess(time.perf_counter() - t0, REQUEST_S / 2, "the in-flight request was not abandoned")
        self.assertEqual(run["status"], "complete")
        self.assertEqual(run["tests"]["short"]["off"].get("contamination_retries"), 1)
        # Abandoned at t2: no further request of that attempt was started; the restart begins with the warm-up.
        i = eng.labels.index("short/off/r0/t2")
        self.assertEqual(eng.labels[i + 1], "probe:warmup-short-off")
        self.assertEqual(eng.intruders, [])
        self.assertEqual(eng.loads, 1, "no reload: this engine stops on disconnect")
        bad = [r for r in raw["requests"] if r.get("discarded")]
        self.assertEqual([r["label"] for r in bad], ["probe:warmup-short-off", "short/off/r0/t1", "short/off/r0/t2"])
        self.assertTrue(bad[-1].get("abandoned"))
        self.assertTrue(all("intruder" in r["discard_reason"] for r in bad))
        ev = run["contamination_events"][0]
        self.assertEqual(ev["test"], "short/off")
        self.assertEqual(ev["intruders"], ["fake:intruder"])
        self.assertIn("restarted (restart 1 of 3)", ev["action"])
        self.assertNotIn("instances", ev)
        self.assertTrue(raw.get("discarded_windows"))
        # The restart's prompts differ from the abandoned ones from the first token (no prompt-cache reuse).
        t1 = [p for lbl, p in eng.prompts if lbl == "short/off/r0/t1"]
        self.assertEqual(len(t1), 2)
        self.assertNotEqual(t1[0][:40], t1[1][:40])

    def test_discarded_data_is_excluded_from_figures(self):
        eng = FakeEngine(intrude_at={"short/off/r0/t2"})
        eng._slow = {"short/off/r0/t2"}
        run, raw = run_quiet(make_runner(eng))
        kept = [r for r in raw["requests"] if not r.get("discarded") and r["label"].startswith("short/")]
        self.assertEqual(len(kept), len(Suite().tests()["short"]["turns"]) + 1)   # turns + cache-hit
        n = run["tests"]["short"]["off"]["turns"][0]["ttft_s"]["n"]
        self.assertEqual(n, 1, "medians must only use the clean attempt")
        # Memory peak ignores discarded samples; so does the context-at-peak analysis.
        clean_max = max(s["engine_bytes"] for s in raw["memory_timeline"] if not s.get("discarded"))
        self.assertEqual(run["memory"]["peak_bytes"], clean_max)
        for s in raw["memory_timeline"]:
            if s.get("discarded"):
                s["engine_bytes"] = 10 ** 12           # a huge spike there must not become the peak
        self.assertEqual(analyze(run, raw)["other_peak_bytes"], clean_max)

    def test_engine_that_keeps_working_is_reloaded(self):
        eng = FakeEngine(stops_on_disconnect=False, intrude_at={"short/off/r0/t1"})
        eng._slow = {"short/off/r0/t1"}
        run, _ = run_quiet(make_runner(eng))
        self.assertEqual(run["status"], "complete")
        self.assertEqual(eng.loads, 2)
        self.assertEqual(len(run["reloads"]), 1)
        self.assertEqual(run["reloads"][0]["test"], "short/off")
        self.assertEqual(len(run["cold_start"]["cycles"]), 1, "the reload is not a measured load")
        self.assertIn("model reloaded", run["contamination_events"][0]["action"])

    def test_restart_cap_stops_model_and_keeps_earlier_tests(self):
        eng = FakeEngine()
        runner = make_runner(eng, tests=("short", "extraction"), max_restarts=2)
        orig = eng.chat

        def chat(*a, **k):   # the intruder only comes back during the extraction test
            eng.intrude_always = (runner.current_label or "").startswith(("extraction", "probe:warmup-extraction"))
            return orig(*a, **k)
        eng.chat = chat
        run, raw = run_quiet(runner)
        self.assertEqual(run["status"], "partial")
        self.assertIn("fake:intruder", run["error"])
        self.assertEqual(run["stopped_by_intruders"], ["fake:intruder"])
        self.assertIn("off", run["tests"]["short"], "the clean short test is kept")
        self.assertNotIn("off", run["tests"].get("extraction", {}))
        self.assertEqual(len(run["contamination_events"]), 3)   # first attempt + 2 restarts
        self.assertIn("restart limit reached", run["contamination_events"][-1]["action"])
        self.assertFalse([r for r in raw["requests"] if r["label"].startswith("extraction") and not r.get("discarded")])

    def test_cap_raises_from_guard(self):
        eng = FakeEngine(intrude_always=True)
        runner = make_runner(eng, max_restarts=0)
        runner.instance = eng.load(MODEL, PROFILE)["instance_id"]
        runner.watchdog.allow("fake", runner.instance)
        runner.watchdog.start()
        try:
            with mock.patch("benchlm.runner.log"), self.assertRaises(IntruderPersists) as cm:
                runner._run_test_guarded("short", "off", {"warnings": []})
        finally:
            runner.watchdog.stop()
        self.assertEqual(cm.exception.intruders, ["fake:intruder"])


class _SlowHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        time.sleep(3)          # like a long prefill: nothing is sent back yet
        self.send_response(200)
        self.end_headers()

    def log_message(self, *a):
        pass


class CancelTests(unittest.TestCase):
    def test_cancel_before_response_headers(self):
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _SlowHandler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        cancel = bhttp.Cancel()
        threading.Timer(0.2, cancel.fire, args=("test",)).start()
        t0 = time.perf_counter()
        try:
            with self.assertRaises(bhttp.Cancelled):
                list(bhttp.stream_ndjson(f"http://127.0.0.1:{srv.server_port}/x", {}, cancel=cancel))
            self.assertLess(time.perf_counter() - t0, 1.5)
            with self.assertRaises(bhttp.Cancelled):   # a fired Cancel refuses new requests
                list(bhttp.stream_sse(f"http://127.0.0.1:{srv.server_port}/x", {}, cancel=cancel))
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
