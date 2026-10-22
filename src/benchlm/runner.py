"""Benchmark orchestration: clean machine → cold/warm loads → tests → memory → DB."""
from __future__ import annotations

import re
import time
import traceback
from typing import List, Optional

from . import VERSION, answers, db as dbm, http, hygiene
from .config import OPERATIONAL_KEYS
from .engines.base import Engine
from .memory import Sampler, method_name, system_memory
from .suite import Suite

TEST_ORDER = ["short", "extraction", "long"]
HEADROOM_GB = 8   # memory the pre-flight check wants free beyond the model's size (as the dashboard's safe context)


def log(msg: str = "") -> None:
    print(msg, flush=True)


def fmt_s(v):
    return f"{v:.2f}s" if isinstance(v, (int, float)) else "—"


def _dur(seconds) -> str:
    return f"{seconds / 60:.1f} min" if seconds >= 90 else f"{seconds:.0f} s"


def fmt_tps(v):
    return f"{v:.1f} tok/s" if isinstance(v, (int, float)) else "—"


class CleanMachineError(Exception):
    def __init__(self, instances):
        super().__init__("models still loaded")
        self.instances = instances


class IntruderPersists(Exception):
    """Another model kept being loaded during a test, even after the maximum number of restarts."""

    def __init__(self, test: str, intruders: List[str], restarts: int):
        super().__init__(f"{test} stopped: another model was loaded again after {restarts} restart(s), the limit "
                         f"({', '.join(intruders) or 'unknown'})")
        self.test = test
        self.intruders = intruders
        self.restarts = restarts


class ModelRunner:
    def __init__(self, engines: List[Engine], engine: Engine, model: dict, profile: dict, suite: Suite,
                 machine: dict, modes: List[str], tests: List[str], repeats: Optional[int] = None,
                 live_extract=None, max_restarts: Optional[int] = None, previous_tests: Optional[dict] = None,
                 store_reasoning: bool = False):
        self.engines = engines
        self.eng = engine
        self.model = model
        self.profile = profile
        self.suite = suite
        self.machine = machine
        self.modes = modes
        self.tests = [t for t in TEST_ORDER if t in tests]
        self.repeats = repeats or int(profile.get("repeats", 3))
        self.live_extract = live_extract
        # restarts allowed per test when another model gets loaded (CLI flag, else profile, else 3)
        self.max_restarts = int(max_restarts if max_restarts is not None else profile.get("max_test_restarts", 3))
        self.previous_tests = previous_tests or {}   # tests of this model's last run, to estimate time saved
        self.store_reasoning = store_reasoning       # keep reasoning texts in the raw file (they can be large)
        maxctx = model.get("max_context_length")
        if maxctx and maxctx < int(profile["context_length"]):
            # small-context model: load at its maximum; the long test is skipped if the document can't fit
            self.profile = dict(profile, context_length=int(maxctx))
            if maxctx < 90000 and "long" in self.tests:
                self.tests = [t for t in self.tests if t != "long"]
                self.skipped_long = f"max context {maxctx} tokens is too small for the long-context test"
        self.sampler = Sampler(engine.process_match, profile.get("memory_sample_interval_s", 0.25))
        self.watchdog = hygiene.Watchdog(engines)
        self.instance = None
        self.snapshots = {}
        self.requests = []    # raw per-request records
        self.warnings = []
        self.cancel: Optional[http.Cancel] = None   # set while a test is running; fired by the watchdog
        self.current_label = None
        self.attempt = 0              # restarts of the current test so far
        self.discarded_windows = []   # memory-timeline spans that don't count (another model was loaded)
        self.reloads = []             # reloads after an abandoned request (never counted as load times)
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        slug = re.sub(r"[^a-z0-9]+", "-", model["model_uid"].lower()).strip("-")
        self.run_id = f"{stamp}-{slug}"[:120]

    # ------------------------------------------------------------------ utils
    def _snap(self, name):
        s = self.sampler.snapshot()
        self.snapshots[name] = s.get("engine_bytes")
        return s

    def _unload_others(self):
        keep = (self.eng.id, self.instance)
        by_id = {e.id: e for e in self.engines}
        for inst in hygiene.all_loaded(self.engines):
            if (inst["engine"], inst["instance_id"]) != keep:
                try:
                    by_id[inst["engine"]].unload(inst)
                    log(f"      unloaded intruder {inst['engine']}:{inst['model_key']}")
                except Exception as ex:
                    log(f"      ! could not unload intruder {inst['model_key']}: {ex}")

    def _chat(self, system_prompt, user, state, reasoning, max_tokens, label):
        coarse = ("cold_start" if label.startswith("probe:cold") else
                  "warmup" if label.startswith("probe:") else label.split("/")[0])
        self.sampler.set_phase(coarse)
        self.current_label = label
        t_start = self.sampler.elapsed()
        try:
            t = self.eng.chat(self.instance, self.model, system_prompt, user, state, reasoning, max_tokens,
                              self.profile, on_phase=lambda p: self.sampler.set_phase(coarse, p), cancel=self.cancel)
        except http.Cancelled:
            self.requests.append({"label": label, "t_start": t_start, "t_end": self.sampler.elapsed(),
                                  "abandoned": True})
            raise
        rec = t.to_dict()
        rec["label"] = label
        rec["text"] = t.text          # the visible answer (prompts are never stored)
        if self.store_reasoning:
            rec["reasoning_text"] = t.reasoning_text
        rec["outcome"] = answers.outcome(t.text, t.reasoning_text, t.finish_reason, t.reasoning_tokens)
        rec["t_start"], rec["t_end"] = t_start, self.sampler.elapsed()   # aligns requests with the memory timeline
        self.requests.append(rec)
        return t

    def _probe(self, tag, reasoning):
        p = self.suite.probe()
        return self._chat(f"[session {tag}] {p['system_prompt']}", p["user"], None, reasoning,
                          p["max_tokens"], f"probe:{tag}")

    # ------------------------------------------------------------------ main
    def run(self) -> dict:
        m, prof = self.model, self.profile
        run = {"run_id": self.run_id, "model_uid": m["model_uid"], "machine_id": self.machine["machine_id"],
               "started_at": dbm.now_iso(), "finished_at": None, "status": "partial", "error": None,
               "tool_version": VERSION, "suite_version": self.suite.version, "suite_hash": self.suite.hash,
               "profile_name": prof["name"], "profile_hash": prof["hash"],
               "profile": {k: v for k, v in prof.items() if k not in OPERATIONAL_KEYS},
               "model_fingerprint": m.get("fingerprint"),
               # quick / partial-suite runs are kept and shown but don't count as "benchmarked"
               "subset": (self.repeats < int(prof.get("repeats", 3))
                          or [t for t in TEST_ORDER if t in self.tests or getattr(self, "skipped_long", None)] != TEST_ORDER
                          or list(self.modes) != list(prof.get("reasoning_modes", ["off", "high"]))),
               "repeats": self.repeats, "tests_run": self.tests, "modes_run": list(self.modes),
               "engine_info": self.eng.info(), "load_config": {}, "cold_start": {}, "memory": {},
               "tests": {}, "summary": {}, "warnings": [], "contamination_events": []}
        rt = (run["engine_info"].get("runtimes") or {}).get(m.get("format") or "")
        run["engine_info"]["runtime"] = rt or {"gguf": "llama.cpp", "mlx": "mlx-engine"}.get(m.get("format"), m.get("format"))
        try:
            self._run_inner(run)
            run["status"] = "complete"
        except KeyboardInterrupt:
            run["error"] = "interrupted by user"
            raise
        except CleanMachineError:
            raise
        except IntruderPersists as ex:
            run["status"] = "partial"   # shown as incomplete: the model is re-tested on the next run
            run["error"] = str(ex)
            run["stopped_by_intruders"] = ex.intruders
            log(f"    ! {ex}.")
            log("      Stopping this model. Pause whatever keeps loading them (e.g. Hermes or n8n schedules),")
            log("      then run this model again; it shows as incomplete until then.")
        except Exception as ex:
            run["status"] = "failed" if not run["tests"] else "partial"
            run["error"] = f"{type(ex).__name__}: {ex}"
            log(f"    ! {run['error']}")
            log("      " + traceback.format_exc().strip().splitlines()[-1])
        finally:
            self._finish(run)
        return run

    def _finish(self, run):
        self.watchdog.stop()
        try:
            self._snap("end")
        except Exception:
            pass
        if self.instance:
            try:
                self.eng.unload({"instance_id": self.instance, "model_key": self.model["key"]})
            except Exception:
                pass
        self.sampler.stop()
        peaks = self.sampler.peaks()
        sysmem = self.machine.get("memory_bytes")
        run["memory"] = {"method": method_name(), "system_total_bytes": sysmem,
                         "snapshots": {k: self.snapshots.get(k) for k in
                                       ("idle", "loaded_empty", "after_short", "after_long_prompt", "end")},
                         **peaks}
        run["warnings"] = list(dict.fromkeys(run.get("warnings", []) + self.warnings))
        dbm.set_swap_warning(run, float(self.profile.get("swap_warning_gb", 1)))
        run["contamination_events"] = [{k: v for k, v in e.items() if k not in ("instance", "instances")}
                                       for e in self.watchdog.events]
        if self.reloads:
            run["reloads"] = self.reloads
        run["finished_at"] = dbm.now_iso()
        raw = {"run_id": self.run_id, "memory_timeline": self.sampler.timeline, "requests": self.requests}
        if self.discarded_windows:
            raw["discarded_windows"] = self.discarded_windows
        run["memory"]["raw_file"] = dbm.save_raw(self.run_id, raw)
        try:
            from .peakctx import analyze
            run["memory"]["context_analysis"] = analyze(run, raw)
        except Exception as ex:
            run["warnings"].append(f"context-at-peak analysis failed: {ex}")
        run["summary"] = dbm.summarize(run)

    def _run_inner(self, run):
        prof = self.profile
        log("    • clearing loaded models…")
        left = hygiene.unload_everything(self.engines, verbose=True)
        if left:
            raise CleanMachineError(left)
        run["preflight"] = self._preflight()
        self.sampler.start()
        self.sampler.set_phase("idle")
        idle = self.sampler.settle(prof.get("settle_timeout_s", 30))
        self.snapshots["idle"] = idle.get("engine_bytes")
        self.watchdog.allow(self.eng.id, None)
        self.watchdog.start()

        off_reason = self._resolve("off")
        cycles = []
        n_cycles = int(prof.get("cold_cycles", 2))
        for c in range(1, n_cycles + 1):
            if c > 1 and self.instance:
                self.sampler.set_phase("unload")
                self.eng.unload({"instance_id": self.instance, "model_key": self.model["key"]})
                self.instance = None
                self.sampler.settle(15)
            self.sampler.set_phase("load", f"cycle{c}")
            self.watchdog.allow_loading(self.eng.id, self._own_names())
            li = self.eng.load(self.model, prof)
            self.instance = li["instance_id"]
            self.watchdog.allow(self.eng.id, self.instance)
            run["load_config"] = li.get("load_config") or {}
            self.sampler.set_phase("loaded")
            snap = self.sampler.settle(15)
            if c == n_cycles:
                self.snapshots["loaded_empty"] = snap.get("engine_bytes")
            t = self._probe(f"cold{c}", off_reason)
            cycles.append({"cycle": c, "load_time_s": round(li["load_time_s"], 3),
                           "client_load_time_s": round(li["client_load_time_s"], 3),
                           "first_ttft_s": t.ttft_s, "loaded_footprint_bytes": snap.get("engine_bytes")})
            log(f"    • cold cycle {c}: load {fmt_s(li['load_time_s'])}, first token {fmt_s(t.ttft_s)}")
        warm = [self._probe(f"warm{i}", off_reason).ttft_s for i in range(3)]
        run["cold_start"] = {"cycles": cycles, "warm_ttft_s": dbm.med(dbm.agg(warm))}
        log(f"    • warm first token {fmt_s(run['cold_start']['warm_ttft_s'])}")

        if getattr(self, "skipped_long", None):
            run["warnings"].append(self.skipped_long)
            run["tests"]["long"] = {m: {"reasoning_requested": m, "skipped": True, "reason": self.skipped_long,
                                        "reasoning_applied": "n/a"} for m in self.modes}
        for test in self.tests:
            run["tests"].setdefault(test, {})
            for mode in self.modes:
                res = self._run_test_guarded(test, mode, run)
                if res is not None:
                    run["tests"][test][mode] = res
                    self._log_result(test, mode, res)
            if test == "short":
                self._snap("after_short")

        if self.live_extract:
            try:
                self.sampler.set_phase("extraction", "live")
                self.live_extract(self)
                run["live_extraction"] = getattr(self, "live_result", None)
            except Exception as ex:
                run["warnings"].append(f"live extraction failed: {ex}")

    def _preflight(self) -> dict:
        """After the unloads: give the system time to release the memory (no sudo, no extra tools), then check
        that the model fits and that swap isn't already in use. Only warns: an unattended run never stops here."""
        prof, gb = self.profile, 1024 ** 3
        limit = float(prof.get("cleanup_wait_s", 30))
        t0 = time.perf_counter()
        last, stable, mem = None, 0, {}
        while time.perf_counter() - t0 < limit:
            mem = system_memory()
            used = mem.get("used")
            if used is None:
                break
            if last and abs(used - last) / last <= 0.005:   # three steady readings 1 s apart: done
                stable += 1
                if stable >= 3:
                    break
            else:
                stable = 0
            last = used
            time.sleep(1.0)
        waited = round(time.perf_counter() - t0, 1)
        total, used, swap = mem.get("total"), mem.get("used"), mem.get("swap_used")
        free = (total - used) if total and used is not None else None
        size = self.model.get("size_bytes") or 0
        need = size + HEADROOM_GB * gb
        pre = {"waited_s": waited, "free_gb": round(free / gb, 1) if free is not None else None,
               "swap_used_gb": round(swap / gb, 1) if swap is not None else None,
               "model_gb": round(size / gb, 1) if size else None}
        log(f"    • memory before loading: {pre['free_gb'] if free is not None else '?'} GB free, swap "
            f"{pre['swap_used_gb'] if swap is not None else '?'} GB in use (waited {waited:.0f} s for the system to settle)")
        if swap is not None and swap > float(prof.get("swap_warning_gb", 1)) * gb:
            w = (f"started with {swap / gb:.1f} GB of swap already in use: speeds may be lower than usual "
                 f"(restarting the computer before a long run clears it)")
            self.warnings.append(w)
            log(f"    ! {w}")
        if free is not None and size and free < need:
            w = (f"only {free / gb:.1f} GB of memory free before loading, less than the model ({size / gb:.1f} GB) plus "
                 f"{HEADROOM_GB} GB: other apps are using memory, so swapping is likely")
            self.warnings.append(w)
            log(f"    ! {w}")
        return pre

    def thinking_budget(self, test: str) -> int:
        """Extra output tokens allowed for thinking (per turn), from the profile (int or per-test dict)."""
        b = self.profile.get("reasoning_extra_tokens", 3072)
        return int(b.get(test, b.get("short", 3072)) if isinstance(b, dict) else b)

    def _resolve(self, mode):
        try:
            return self.eng.resolve_reasoning(self.model, mode)
        except ValueError:
            return "__unsupported__"

    def _log_result(self, test, mode, res):
        if res.get("skipped"):
            log(f"    • {test}/{mode}: skipped ({res.get('reason')})")
            return
        t1 = res["turns"][0]
        extra = ""
        q = res.get("quality") or {}
        if "recall" in q:
            extra = f", recall {q['recall_correct']}/{q['recall_total']}"
        if "accuracy" in q:
            extra = f", accuracy {q['accuracy']:.0%}" if q["accuracy"] is not None else ", invalid JSON"
        log(f"    • {test}/{mode} [{res['reasoning_applied']}]: first token {fmt_s(dbm.med(t1.get('ttft_s')))}, "
            f"prefill {fmt_tps(dbm.med(t1.get('prefill_tps')))}, decode {fmt_tps(dbm.med(t1.get('decode_tps')))}{extra}")

    def _run_test_guarded(self, test, mode, run):
        """Run one test; if another model gets loaded meanwhile, abandon it at once and start it again.

        The watchdog fires the test's Cancel, which closes the in-flight request; nothing else is sent. Everything
        the attempt produced (requests, memory samples, snapshots, warnings) is discarded, the intruders are
        unloaded and the test restarts from its warm-up probe. Earlier tests are kept. After max_restarts, the
        model is stopped (IntruderPersists)."""
        name = f"{test}/{mode}"
        names: List[str] = []
        restarts = 0
        while True:
            self.attempt = restarts
            self._clear_intruders(name)
            mark, warn_mark, snaps_before = len(self.requests), len(self.warnings), set(self.snapshots)
            t0 = self.sampler.elapsed()
            cancel = self.cancel = http.Cancel()
            hit = {}

            def on_intruder(event, cancel=cancel):
                hit["event"] = event
                cancel.fire(f"another model was loaded during {name}")

            self.watchdog.arm(name, on_intruder)
            res = None
            try:
                res = self._run_test(test, mode)
                self.watchdog.check()     # a model loaded since the last poll also spoils the test
            except http.Cancelled:
                pass
            finally:
                self.watchdog.disarm()
                self.cancel = None
            if not cancel.fired.is_set():
                if restarts:
                    res["contamination_retries"] = restarts
                return res

            # ---- interrupted: throw the attempt away
            event = hit.get("event") or {}
            found = list(event.get("intruders") or [])
            names += [n for n in found if n not in names]
            reason = f"another model was loaded during {name}: {', '.join(found) or 'unknown'}"
            attempt = self.requests[mark:]
            for r in attempt:
                r["discarded"] = True
                r["discard_reason"] = reason
            del self.warnings[warn_mark:]
            for k in set(self.snapshots) - snaps_before:
                del self.snapshots[k]
            abandoned = res is None
            planned = self._planned_requests(test, mode)
            saved = self._time_saved(test, mode, attempt, self.sampler.elapsed() - t0) if abandoned else 0.0
            restarts += 1
            give_up = restarts > self.max_restarts
            if abandoned:
                where = (f"interrupted at request {len(attempt)} of {planned} ({self.current_label}) "
                         f"after {_dur(self.sampler.elapsed() - t0)}")
                gain = (f"about {_dur(saved)} saved versus finishing it" if saved is not None
                        else f"{planned - len(attempt)} remaining request(s) skipped")
            else:
                where, gain = "spoiled at its very end (found by the final check)", "nothing left to save"
            log(f"    ! {name} {where}: another model was loaded ({', '.join(found) or 'unknown'}); {gain}; "
                + ("restart limit reached." if give_up else f"restarting (attempt {restarts + 1} of {self.max_restarts + 1})."))
            action = self._recover(name, abandoned and not give_up)
            self.discarded_windows.append({"t_from": t0, "t_to": self.sampler.elapsed(), "reason": reason})
            self.sampler.discard(t0, self.sampler.elapsed())
            if event:
                event["test"] = name
                event["action"] = (f"{'abandoned at ' + str(self.current_label) if abandoned else 'discarded after the final check'}"
                                   f"; {action}; " + ("restart limit reached, model stopped" if give_up
                                                       else f"restarted (restart {restarts} of {self.max_restarts})"))
                event["detail"] = f"other model loaded during {name}: {', '.join(found)} — {event['action']}"
            if give_up:
                raise IntruderPersists(name, names, self.max_restarts)
            run["warnings"].append(f"{name}: interrupted and restarted because another model was loaded "
                                   f"({', '.join(found) or 'unknown'})")

    def _own_names(self):
        """Names the engine may list the model under test by while it is loading."""
        m = self.model
        return {m.get("key"), m.get("_load_key"), m["model_uid"].split(":", 1)[-1]}

    def _clear_intruders(self, name):
        """Before a test (attempt): unload anything loaded since the last check, so the test starts clean."""
        if not self.watchdog.intruders():
            return
        event = self.watchdog.check()
        log(f"      another model is loaded before {name}; unloading it first")
        self._unload_others()
        self.watchdog.forget()
        if event and not event.get("action"):
            event["action"] = f"unloaded before {name} started"
        self.sampler.settle(15)

    def _recover(self, name, abandoned) -> str:
        """After an interruption: make sure the engine is no longer busy, then unload the intruders."""
        actions = []
        self._unload_others()
        self.watchdog.forget()
        actions.append("intruders unloaded")
        if abandoned and not getattr(self.eng, "stops_on_disconnect", False):
            # The engine may still be working on the abandoned request: reload the model under test (same
            # profile). Timed separately; it never counts as a measured load time.
            self.sampler.set_phase("reload")
            t = time.perf_counter()
            try:
                self.eng.unload({"instance_id": self.instance, "model_key": self.model["key"]})
            except Exception as ex:
                log(f"      ! could not unload {self.model['key']} before reloading it: {ex}")
            self.instance = None
            self.watchdog.allow_loading(self.eng.id, self._own_names())
            li = self.eng.load(self.model, self.profile)
            self.instance = li["instance_id"]
            self.watchdog.allow(self.eng.id, self.instance)
            secs = round(time.perf_counter() - t, 3)
            self.reloads.append({"t": dbm.now_iso(), "test": name, "reason": "engine may still be busy with the "
                                 "abandoned request", "unload_load_s": secs,
                                 "load_time_s": round(li.get("load_time_s") or 0, 3)})
            log(f"      reloaded {self.model['key']} in {_dur(secs)} (not counted as a load time)")
            actions.append("model reloaded")
        self.sampler.set_phase("loaded")
        self.sampler.settle(15)
        return ", ".join(actions)

    def _planned_requests(self, test, mode) -> int:
        n = 1 if self.profile.get("warmup") else 0
        n += self.repeats * len(self.suite.tests()[test]["turns"])
        if test in ("short", "long") and mode == "off":
            n += 1   # cache-hit request
        return n

    def _time_saved(self, test, mode, attempt, elapsed) -> Optional[float]:
        """Estimated time the interrupted test would still have taken. Uses this model's last run of the same
        test, else the conversations this attempt completed; None when there's nothing to go on."""
        per_conv = (((self.previous_tests.get(test) or {}).get(mode) or {}).get("totals") or {}).get("conversation_s")
        if not per_conv:
            convs = {}
            for r in attempt:
                m = re.search(r"/r(\d+)/t\d+$", r.get("label") or "")
                if m and not r.get("abandoned"):
                    convs.setdefault(m.group(1), []).append(r["t_end"] - r["t_start"])
            n_turns = len(self.suite.tests()[test]["turns"])
            full = [sum(v) for v in convs.values() if len(v) == n_turns]
            per_conv = sum(full) / len(full) if full else None
        if not per_conv:
            return None
        return max(0.0, per_conv * self.repeats - elapsed)

    def _run_test(self, test, mode) -> Optional[dict]:
        reasoning = self._resolve(mode)
        if reasoning == "__unsupported__":
            return {"reasoning_requested": mode, "reasoning_applied": "unsupported", "skipped": True,
                    "reason": "model has no configurable reasoning"} if mode != "off" else None
        if mode != "off" and reasoning == self._resolve("off"):
            return {"reasoning_requested": mode, "reasoning_applied": str(reasoning), "skipped": True,
                    "reason": "same as off"}
        applied = "default" if reasoning is None else ("off" if reasoning is False else str(reasoning))
        thinking = reasoning not in (None, False, "off")
        extra = self.thinking_budget(test) if thinking else 0
        spec = self.suite.tests()[test]
        turn_defs = spec["turns"]
        per_turn = [[] for _ in turn_defs]
        quality_runs = []
        reasoning_runs = []   # the same scoring applied to the reasoning text (secondary)
        conv_times = []
        last_tag = None
        if self.profile.get("warmup"):
            self._probe(f"warmup-{test}-{mode}", reasoning)
        for r in range(self.repeats):
            tag = f"{self.run_id[-8:]}-{test}-{mode}-r{r}"
            if self.attempt:
                # A restart must not reuse what the engine cached from the abandoned attempt's prompt
                # (LM Studio does: TTFT 17.6 s instead of 26 s after a cancel 8 s into the prefill).
                tag += f"-a{self.attempt}"
            last_tag = tag
            sys_prompt = f"[session {tag}] {spec['system_prompt']}"
            state, prev_total, texts, rtexts = None, 0, [], []
            t_conv = time.perf_counter()
            for i, td in enumerate(turn_defs):
                t = self._chat(sys_prompt, td["user"], state, reasoning, td["max_tokens"] + extra,
                               f"{test}/{mode}/r{r}/t{i + 1}")
                if t.new_prompt_tokens is None and t.prompt_tokens is not None:
                    t.new_prompt_tokens = max(1, t.prompt_tokens - prev_total) if state else t.prompt_tokens
                if t.prompt_tokens is not None:
                    prev_total = t.prompt_tokens + (t.completion_tokens or 0) - (t.reasoning_tokens or 0)
                per_turn[i].append(t)
                texts.append(t.text)
                rtexts.append(t.reasoning_text)
                state = t.state
                if test == "long" and i == 0 and "after_long_prompt" not in self.snapshots:
                    self._snap("after_long_prompt")
            conv_times.append(time.perf_counter() - t_conv)
            has_reasoning = any((x or "").strip() for x in rtexts)
            if test == "long":
                quality_runs.append(self.suite.recall(texts, turn_defs))
                if has_reasoning:
                    reasoning_runs.append(self.suite.recall(rtexts, turn_defs))
            elif test == "extraction":
                q = self.suite.score_extraction(texts[0], self.suite.answer_key)
                q.pop("details", None)
                quality_runs.append(q)
                if has_reasoning:
                    q = self.suite.score_extraction(rtexts[0], self.suite.answer_key)
                    q.pop("details", None)
                    reasoning_runs.append(q)
        turns = []
        for i, (td, ts) in enumerate(zip(turn_defs, per_turn)):
            turns.append({
                "turn": i + 1, "label": td.get("label"),
                "prompt_tokens": dbm.med(dbm.agg([t.prompt_tokens for t in ts])),
                "new_prompt_tokens": dbm.med(dbm.agg([t.new_prompt_tokens for t in ts])),
                "completion_tokens": dbm.med(dbm.agg([t.completion_tokens for t in ts])),
                "reasoning_tokens": dbm.med(dbm.agg([t.reasoning_tokens for t in ts])) or 0,
                "ttft_s": dbm.agg([t.ttft_s for t in ts]),
                "first_visible_s": dbm.agg([t.first_visible_s for t in ts]),
                "prefill_tps": dbm.agg([t.prefill_tps for t in ts]),
                "decode_tps": dbm.agg([t.decode_tps for t in ts]),
                "total_s": dbm.agg([t.total_s for t in ts]),
                "truncated": sum(1 for t in ts if t.finish_reason == "length"),
                "answer_in_reasoning": sum(1 for t in ts if answers.outcome(t.text, t.reasoning_text, t.finish_reason,
                                                                             t.reasoning_tokens) == answers.IN_REASONING),
                "no_answer_budget": sum(1 for t in ts if answers.outcome(t.text, t.reasoning_text, t.finish_reason,
                                                                          t.reasoning_tokens) == answers.NO_ANSWER_BUDGET),
            })
        res = {"reasoning_requested": mode, "reasoning_applied": applied, "repeats": self.repeats,
               "turns": turns,
               "totals": {"conversation_s": dbm.med(dbm.agg(conv_times)),
                          "output_tokens": sum((t["completion_tokens"] or 0) for t in turns)}}
        total = sum(len(ts) for ts in per_turn)
        res["answers_total"] = total
        in_reasoning = sum(t["answer_in_reasoning"] for t in turns)
        res["answer_in_reasoning_turns"] = in_reasoning
        if in_reasoning:
            self.warnings.append(answers.warning(test, mode, in_reasoning, total))
        no_answer = sum(t["no_answer_budget"] for t in turns)
        res["no_answer_budget_turns"] = no_answer
        if no_answer:
            self.warnings.append(answers.budget_warning(test, mode, no_answer, total))
        cut = sum(t["truncated"] for t in turns)
        if cut:
            res["truncated_turns"] = cut   # answer cut off by max tokens (often: thinking used the budget)
            if cut > no_answer:            # those with no answer at all already have their own warning
                self.warnings.append(answers.truncated_warning(test, mode, cut - no_answer, thinking))
        if test == "long":
            pt = turns[0].get("prompt_tokens") or 0
            if pt and pt < int(self.profile.get("min_long_prompt_tokens", 64000)):
                self.warnings.append(f"long/{mode}: document is only {pt} tokens for this tokenizer (< 64k)")
        if not thinking and any((t["reasoning_tokens"] or 0) > 0 for t in turns):
            res["reasoning_observed"] = True   # model reasoned although reasoning was off/unset
        if quality_runs:
            res["quality"] = self._merge_quality(test, quality_runs)
            if reasoning_runs and in_reasoning:
                # secondary score, only where an answer actually landed in the reasoning channel (otherwise the
                # thinking just doesn't contain the answer, and a low score there would mean nothing)
                rq = self._merge_quality(test, reasoning_runs)
                if test == "long":
                    res["quality"]["recall_reasoning"] = rq.get("recall")
                    res["quality"]["recall_reasoning_correct"] = rq.get("recall_correct")
                else:
                    res["quality"]["accuracy_reasoning"] = rq.get("accuracy")
        # Prompt-cache hit: re-send turn 1 with the same session tag as the last repeat. Measured in the "off" mode
        # even when the model can't turn thinking off (gpt-oss runs "off" as "low"): TTFT counts the first token
        # of any kind, so the thinking doesn't change what is measured.
        if test in ("short", "long") and mode == "off" and last_tag:
            t = self._chat(f"[session {last_tag}] {spec['system_prompt']}", turn_defs[0]["user"], None,
                           reasoning, turn_defs[0]["max_tokens"], f"{test}/{mode}/cache-hit")
            res["cache_hit_ttft_s"] = t.ttft_s
        return res

    @staticmethod
    def _merge_quality(test, runs):
        if test == "long":
            c = sum(r["recall_correct"] for r in runs)
            n = sum(r["recall_total"] for r in runs)
            facts = answers.merge_facts(runs)
            return {"recall_correct": round(c / len(runs), 2), "recall_total": runs[0]["recall_total"],
                    "recall": round(c / n, 3) if n else None, "per_repeat": [r["recall"] for r in runs],
                    "facts": facts, "recall_by_section": answers.recall_by_section(facts)}
        accs = [r.get("accuracy") for r in runs if r.get("accuracy") is not None]
        return {"json_valid": all(r.get("json_valid") for r in runs),
                "accuracy": round(sum(accs) / len(accs), 3) if accs else 0.0,
                "fields_correct": runs[-1].get("fields_correct"), "fields_total": runs[-1].get("fields_total"),
                "per_repeat": [r.get("accuracy") for r in runs]}
