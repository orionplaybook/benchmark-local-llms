"""Fixes from the 2026-10-20/21 overnight run: reasoning-channel answers, stored answers and per-fact recall,
the watchdog during a slow load, MoE metadata, cache-hit with forced thinking, swap warnings.
Run from benchmark-local-llms/:  python3 -m unittest discover -s tests"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchlm import answers, db as dbm, hygiene, publish  # noqa: E402
from benchlm.config import load_profile, profile_hash  # noqa: E402
from benchlm.engines.base import Engine, Turn, moe_active_estimate  # noqa: E402
from benchlm.engines.lmstudio import LMStudio  # noqa: E402
from benchlm.enrich import sources  # noqa: E402
from benchlm.suite import Suite  # noqa: E402
from test_watchdog import FakeSampler, MODEL, PROFILE, run_quiet  # noqa: E402

from benchlm.runner import ModelRunner  # noqa: E402

SUITE = Suite()
ALL_ANSWERS = " ".join(f["answers"][0] for f in SUITE.facts.values())


class AnsweringEngine(Engine):
    """Answers every recall question correctly; `channel` decides where the answer is written in Thinking High."""
    id = "fake"
    name = "Fake"
    stops_on_disconnect = True

    def __init__(self, channel="visible", off_level=None):
        super().__init__("http://fake")
        self.channel = channel
        self.off_level = off_level     # e.g. "low": the model can't turn thinking off (gpt-oss)
        self.labels = []

    def info(self):
        return {}

    inst = None

    def loaded(self):
        return [{"engine": "fake", "model_key": "model", "instance_id": self.inst, "type": "llm"}] if self.inst else []

    def load(self, model, profile):
        self.inst = "inst"
        return {"instance_id": "inst", "load_time_s": 0.01, "client_load_time_s": 0.01, "load_config": {}}

    def unload(self, instance):
        self.inst = None

    def resolve_reasoning(self, model, mode):
        return "high" if mode == "high" else self.off_level

    def chat(self, instance_id, model, system_prompt, user_text, state, reasoning, max_tokens, profile,
             on_phase=None, cancel=None):
        self.labels.append(self.current_label())
        t = Turn()
        t.ttft_s, t.total_s, t.prompt_tokens, t.completion_tokens, t.finish_reason = 0.01, 0.02, 100, 10, "stop"
        if reasoning == "high" and self.channel == "reasoning":
            t.text, t.reasoning_text = "", "Answers: " + ALL_ANSWERS
        else:
            t.text = "Answers: " + ALL_ANSWERS
            t.reasoning_text = "thinking..." if reasoning else ""
        return t


def runner_for(eng, tests=("long",), modes=("off", "high"), **kw):
    r = ModelRunner([eng], eng, dict(MODEL, capabilities={"reasoning": {"allowed_options": ["off", "high"]}}),
                    dict(PROFILE), SUITE, {"machine_id": "m"}, list(modes), list(tests), repeats=1, **kw)
    r.sampler = FakeSampler()
    r.watchdog = hygiene.Watchdog([eng], interval=60)
    eng.current_label = lambda: r.current_label
    return r


class ReasoningChannelTests(unittest.TestCase):
    def test_outcome(self):
        self.assertEqual(answers.outcome("", "the answer", "stop"), answers.IN_REASONING)
        self.assertIsNone(answers.outcome("visible", "thinking", "stop"))
        self.assertEqual(answers.outcome("", "still thinking", "length"), answers.NO_ANSWER_BUDGET)
        self.assertEqual(answers.outcome("", "", "length", reasoning_tokens=9000), answers.NO_ANSWER_BUDGET)
        self.assertIsNone(answers.outcome("partial ans", "thinking", "length"), "an answer started: just cut off")
        self.assertIsNone(answers.outcome("", "", "length"), "no thinking: not a thinking-budget problem")
        self.assertIsNone(answers.outcome("", "", "stop"))

    def test_answer_in_reasoning_is_flagged_and_scored_separately(self):
        run, raw = run_quiet(runner_for(AnsweringEngine(channel="reasoning")))
        hi, off = run["tests"]["long"]["high"], run["tests"]["long"]["off"]
        self.assertEqual(hi["quality"]["recall"], 0.0, "official score uses the visible answer")
        self.assertEqual(hi["quality"]["recall_reasoning"], 1.0, "secondary score on the reasoning text")
        self.assertEqual(hi["answer_in_reasoning_turns"], len(SUITE.tests()["long"]["turns"]))
        self.assertEqual(off["answer_in_reasoning_turns"], 0)
        self.assertTrue(any("reasoning channel" in w and w.startswith("long/high") for w in run["warnings"]))
        self.assertEqual(run["summary"]["long_high_answer_in_reasoning_turns"], 4)
        self.assertEqual(run["summary"]["long_high_recall_reasoning"], 1.0)
        recs = [r for r in raw["requests"] if r["label"].startswith("long/high/")]
        self.assertTrue(all(r["outcome"] == answers.IN_REASONING for r in recs))

    def test_no_secondary_score_when_answers_are_visible(self):
        run, _ = run_quiet(runner_for(AnsweringEngine(channel="visible"), tests=("long", "extraction")))
        self.assertNotIn("recall_reasoning", run["tests"]["long"]["high"]["quality"])
        self.assertNotIn("accuracy_reasoning", run["tests"]["extraction"]["high"]["quality"])
        self.assertIsNone(run["summary"]["long_high_recall_reasoning"])

    def test_extraction_and_short_are_checked_too(self):
        run, _ = run_quiet(runner_for(AnsweringEngine(channel="reasoning"), tests=("short", "extraction")))
        for test in ("short", "extraction"):
            self.assertGreater(run["tests"][test]["high"]["answer_in_reasoning_turns"], 0)
            self.assertEqual(run["tests"][test]["off"]["answer_in_reasoning_turns"], 0)
        self.assertIn("accuracy_reasoning", run["tests"]["extraction"]["high"]["quality"])

    def test_backfill_from_old_raw_counts(self):
        run = {"tests": {"long": {"high": {"turns": [{}, {}]}, "off": {"turns": [{}, {}]}}}, "warnings": []}
        raw = {"requests": [
            {"label": "long/high/r0/t1", "text_chars": 0, "reasoning_chars": 383, "finish_reason": "stop"},
            {"label": "long/high/r0/t2", "text_chars": 0, "reasoning_chars": 61, "finish_reason": "stop"},
            {"label": "long/high/r0/cache-hit", "text_chars": 0, "reasoning_chars": 61, "finish_reason": "stop"},
            {"label": "long/off/r0/t1", "text_chars": 379, "reasoning_chars": 0, "finish_reason": "stop"},
            {"label": "long/off/r0/t2", "text_chars": 0, "reasoning_chars": 9, "finish_reason": "stop", "discarded": True},
        ]}
        self.assertTrue(answers.backfill(run, raw))
        self.assertEqual(run["tests"]["long"]["high"]["answer_in_reasoning_turns"], 2)
        self.assertEqual(run["tests"]["long"]["off"]["answer_in_reasoning_turns"], 0)
        self.assertEqual(len(run["warnings"]), 1)
        self.assertFalse(answers.backfill(run, raw), "idempotent")
        self.assertEqual(len(run["warnings"]), 1)

    def test_out_of_budget_backfill_and_summary(self):
        # gpt-oss extraction/high from the 2026-10-22 run: one answer, two that ran out of thinking budget.
        run = {"tests": {"extraction": {"high": {"turns": [{"label": "Extract benchmark JSON"}], "repeats": 3,
                                                 "answer_in_reasoning_turns": 0, "truncated_turns": 2}}},
               "warnings": [answers.truncated_warning("extraction", "high", 2, True)]}
        raw = {"requests": [
            {"label": "extraction/high/r0/t1", "text_chars": 816, "reasoning_chars": 17739, "finish_reason": "stop", "outcome": None},
            {"label": "extraction/high/r1/t1", "text_chars": 0, "reasoning_chars": 32325, "finish_reason": "length", "outcome": None},
            {"label": "extraction/high/r2/t1", "text_chars": 0, "reasoning_chars": 27522, "finish_reason": "length", "outcome": None},
        ]}
        self.assertTrue(answers.backfill(run, raw))
        hi = run["tests"]["extraction"]["high"]
        self.assertEqual((hi["no_answer_budget_turns"], hi["answers_total"]), (2, 3))
        self.assertEqual(hi["turns"][0]["no_answer_budget"], 2)
        self.assertEqual(hi["answer_in_reasoning_turns"], 0, "already-set counts are left alone")
        self.assertEqual(run["warnings"], [answers.budget_warning("extraction", "high", 2, 3)],
                         "the older output-limit warning for the same turns is replaced")
        self.assertFalse(answers.backfill(run, raw), "idempotent")
        s = dbm.summarize(run)
        self.assertEqual((s["extraction_high_no_answer_scored"], s["extraction_high_scored_answers"]), (2, 3))

    def test_only_scored_turns_label_the_score(self):
        # Qwen3.5 9B long/high: the 3 missing answers were all in the unscored overview turn.
        res = {"repeats": 3, "no_answer_budget_turns": 3, "turns": [
            {"label": "Load document + overview", "no_answer_budget": 3},
            {"label": "Recall: start of document", "no_answer_budget": 0},
            {"label": "Recall: middle of document", "no_answer_budget": 0},
            {"label": "Recall: end of document", "no_answer_budget": 0}]}
        self.assertEqual(answers.no_answer_scored("long", res), (0, 9))
        res["turns"][2]["no_answer_budget"] = 3
        self.assertEqual(answers.no_answer_scored("long", res), (3, 9))
        self.assertEqual(answers.no_answer_scored("short", res), (None, None), "short isn't scored")
        self.assertEqual(answers.no_answer_scored("long", {"turns": res["turns"]}), (None, None), "not checked")


class StoredAnswerTests(unittest.TestCase):
    def test_answers_kept_reasoning_only_on_request_prompts_never(self):
        _, raw = run_quiet(runner_for(AnsweringEngine()))
        rec = next(r for r in raw["requests"] if r["label"] == "long/off/r0/t2")
        self.assertIn("TANGERINE-4471", rec["text"])
        self.assertNotIn("reasoning_text", rec)
        doc_start = SUITE.document[:200]
        self.assertFalse(any(doc_start in json.dumps(r) for r in raw["requests"]), "no prompt text in raw")
        _, raw = run_quiet(runner_for(AnsweringEngine(), store_reasoning=True))
        self.assertIn("reasoning_text", next(r for r in raw["requests"] if r["label"] == "long/high/r0/t2"))

    def test_per_fact_recall_by_section(self):
        run, _ = run_quiet(runner_for(AnsweringEngine(), modes=("off",)))
        q = run["tests"]["long"]["off"]["quality"]
        self.assertEqual(len(q["facts"]), len(SUITE.facts))
        f1 = next(f for f in q["facts"] if f["id"] == "f1")
        self.assertEqual((f1["section"], f1["expected"], f1["hits"], f1["of"]), ("start", "TANGERINE-4471", 1, 1))
        self.assertEqual(q["recall_by_section"], {"start": 1.0, "middle": 1.0, "end": 1.0})
        self.assertEqual(run["summary"]["long_off_recall_middle"], 1.0)

    def test_old_runs_show_not_available(self):
        s = dbm.summarize({"tests": {"long": {"off": {"turns": [{"ttft_s": {"median": 1}}],
                                                       "quality": {"recall": 0.5}}}}})
        self.assertIsNone(s["long_off_recall_start"])
        self.assertIsNone(s["long_off_recall_reasoning"])
        self.assertIsNone(s["long_off_answer_in_reasoning_turns"])

    def test_publish_strips_answers_unless_asked(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "raw").mkdir()
            raw = {"run_id": "r1", "memory_timeline": [],
                   "requests": [{"label": "long/off/r0/t1", "text": "secret answer", "reasoning_text": "x", "ttft_s": 1}]}
            (tmp / "raw" / "r1.json").write_text(json.dumps(raw))
            db = {"models": {}, "machines": {}, "public": {}, "runs": [{"run_id": "r1", "memory": {"raw_file": "raw/r1.json"}}]}
            for include, expect in ((False, False), (True, True)):
                out = tmp / f"site{include}"
                with mock.patch.object(publish, "RAW_DIR", tmp / "raw"), mock.patch.object(publish.dbm, "load", return_value=db):
                    publish.publish(str(out), quiet=True, internal=True, include_answers=include)
                text = (out / "data" / "raw" / "r1.json").read_text() + (out / "data" / "raw" / "r1.js").read_text()
                self.assertEqual("secret answer" in text, expect)
                self.assertIn('"ttft_s"', text)


class LoadingWatchdogTests(unittest.TestCase):
    def test_model_under_test_while_loading_is_not_an_intruder(self):
        class E:
            id = "lmstudio"
            name = "LM Studio"
            instances = []

            def loaded(self):
                return self.instances
        e = E()
        wd = hygiene.Watchdog([e])
        wd.allow("lmstudio", None)
        wd.allow_loading("lmstudio", {"qwen3.8-27b-splash"})
        e.instances = [{"engine": "lmstudio", "model_key": "qwen3.8-27b-splash", "instance_id": "qwen3.8-27b-splash"}]
        self.assertEqual(wd.intruders(), [], "half-loaded model under test")
        e.instances.append({"engine": "lmstudio", "model_key": "google/gemma-4-26b-a4b-qat", "instance_id": "g"})
        self.assertEqual([i["instance_id"] for i in wd.intruders()], ["g"], "other models are still caught")
        wd.allow("lmstudio", "qwen3.8-27b-splash")       # load returned: exact instance from now on
        e.instances.append({"engine": "lmstudio", "model_key": "qwen3.8-27b-splash", "instance_id": "qwen3.8-27b-splash:2"})
        self.assertEqual({i["instance_id"] for i in wd.intruders()}, {"g", "qwen3.8-27b-splash:2"},
                         "a second instance of the same model is an intruder")

    def test_runner_allows_during_cold_load(self):
        eng = AnsweringEngine()
        seen = []
        orig = eng.load

        def slow_load(model, profile):     # the instance is listed before load() returns; the watchdog polls
            eng.inst = "inst"
            seen.append(r.watchdog.intruders())
            return orig(model, profile)
        eng.load = slow_load
        r = runner_for(eng, tests=("short",), modes=("off",))
        run, _ = run_quiet(r)
        self.assertEqual(seen, [[]] * PROFILE["cold_cycles"])
        self.assertEqual(run["contamination_events"], [])


class MoeTests(unittest.TestCase):
    GPT_OSS = {"num_local_experts": 32, "num_experts_per_tok": 4, "experts_per_token": 4, "hidden_size": 2880,
               "intermediate_size": 2880, "num_hidden_layers": 24}
    QWEN_DENSE = {"text_config": {"hidden_size": 5120, "intermediate_size": 17408, "num_hidden_layers": 64}}

    def test_config(self):
        m = sources.moe_from_config(self.GPT_OSS, 20.91)
        self.assertEqual((m["experts"], m["experts_per_token"]), (32, 4))
        self.assertAlmostEqual(m["params_active_b"], 4.2, places=1)
        nested = sources.moe_from_config({"text_config": {"num_experts": 256, "num_experts_per_tok": 8}}, 35)
        self.assertEqual(nested["experts"], 256)
        self.assertIsNone(sources.moe_from_config(self.QWEN_DENSE, 27.8))

    def test_card_picks_this_size(self):
        card = ("- `gpt-oss-120b` (117B parameters with 5.1B active parameters)\n"
                "- `gpt-oss-20b` (21B parameters with 3.6B active parameters)")
        self.assertEqual(sources.active_from_card(card, 20.91), 3.6)
        self.assertEqual(sources.active_from_card("GLM-4.7-Flash is a 30B-A3B MoE model.", 31.2), 3.0)
        self.assertIsNone(sources.active_from_card("a 235B-A22B sibling", 30))

    def test_apply_precedence(self):
        model = {"is_moe": False, "params_active_b": None}
        dbm.apply_moe(model, {"moe": {"experts": 32, "experts_per_token": 4, "params_active_b": 3.6, "active_source": "model card"}})
        self.assertEqual((model["is_moe"], model["params_active_b"], model["moe_experts"]), (True, 3.6, 32))
        est = {"params_active_b": 4.2, "params_active_source": "estimated from GGUF metadata"}
        dbm.apply_moe(est, {"moe": {"experts": 32, "params_active_b": 3.6, "active_source": "model card"}})
        self.assertEqual(est["params_active_b"], 3.6, "a card value replaces an estimate")
        named = {"params_active_b": 3.0, "params_active_source": "name"}
        dbm.apply_moe(named, {"moe": {"experts": 64, "params_active_b": 5.2, "active_source": "estimated from config.json"}})
        self.assertEqual(named["params_active_b"], 3.0, "the name wins")
        dense = {"is_moe": False}
        dbm.apply_moe(dense, {})
        self.assertFalse(dense["is_moe"])

    def test_engine_signals(self):
        n = LMStudio("http://x")._normalize({"key": "zai-org/glm-4.7-flash", "architecture": "glm4_moe_lite", "params_string": "30B"})
        self.assertTrue(n["is_moe"])
        n = LMStudio("http://x")._normalize({"key": "qwen/qwen3.8-27b", "architecture": "qwen3_5", "params_string": "27B"})
        self.assertFalse(n["is_moe"])
        self.assertAlmostEqual(moe_active_estimate(20.91, 24, 2880, 2880, 32, 4), 4.2, places=1)


class CacheHitTests(unittest.TestCase):
    def test_measured_when_off_runs_with_thinking(self):
        eng = AnsweringEngine(off_level="low")       # gpt-oss: "off" is thinking level low
        run, _ = run_quiet(runner_for(eng))
        self.assertIsNotNone(run["tests"]["long"]["off"].get("cache_hit_ttft_s"))
        self.assertIsNotNone(run["summary"]["long_off_cache_hit_ttft_s"])
        self.assertIn("long/off/cache-hit", eng.labels)
        self.assertNotIn("long/high/cache-hit", eng.labels)


class RecallScoringTests(unittest.TestCase):
    def test_unicode_hyphens_and_spaces_match(self):
        # what gpt-oss actually wrote (U+2011 non-breaking hyphens, U+202F narrow no-break spaces)
        texts = ["overview", "1. TANGERINE\u20114471  \n2. Halcyon\u202fDrift  \n3. x",
                 "1. BLUE\u2011HERON\u201182  \n2. x\n3. The **Copper\u202fAlbatross\u202fPrize**\n4. x",
                 "1. Old\u00a0Biscuit\n2. x\n3. x"]
        r = SUITE.recall(texts, SUITE.tests()["long"]["turns"])
        ok = {d["id"] for d in r["details"] if d["ok"]}
        self.assertTrue({"f1", "f2", "f4", "f6", "f8"} <= ok, ok)
        self.assertEqual(answers.normalize("A\u2014B \u00a0 C"), "a-b c")

    def test_no_false_matches(self):
        r = SUITE.recall(["", "TANGERINE 4471", "", ""], SUITE.tests()["long"]["turns"])
        self.assertFalse(next(d for d in r["details"] if d["id"] == "f1")["ok"], "a space is not a hyphen")


class PreflightTests(unittest.TestCase):
    GB = 1024 ** 3

    def preflight(self, readings, size_gb):
        eng = AnsweringEngine()
        r = runner_for(eng)
        r.profile = dict(r.profile, cleanup_wait_s=30)
        r.model = dict(r.model, size_bytes=int(size_gb * self.GB))
        it = iter(readings)
        last = [None]

        def mem():
            last[0] = next(it, last[0])
            return last[0]
        with mock.patch("benchlm.runner.system_memory", side_effect=mem), mock.patch("benchlm.runner.time.sleep"), \
                mock.patch("benchlm.runner.log"):
            return r._preflight(), r.warnings

    def test_waits_until_memory_stops_dropping(self):
        drop = [{"total": 64 * self.GB, "used": u * self.GB, "swap_used": 0} for u in (40, 30, 22, 20, 20, 20, 20, 20)]
        pre, warnings = self.preflight(drop, 15)
        self.assertEqual(pre["free_gb"], 44.0)
        self.assertEqual(warnings, [])

    def test_warns_about_swap_and_too_little_free_memory(self):
        busy = [{"total": 64 * self.GB, "used": 50 * self.GB, "swap_used": 3 * self.GB}] * 5
        pre, warnings = self.preflight(busy, 17.6)
        self.assertEqual((pre["free_gb"], pre["swap_used_gb"]), (14.0, 3.0))
        self.assertEqual(len(warnings), 2)
        self.assertIn("swap already in use", warnings[0])
        self.assertIn("only 14.0 GB of memory free", warnings[1])


class ReasoningEffortTests(unittest.TestCase):
    def test_effort_ends(self):
        ends = sources.effort_ends([("medium", 2), ("low", 1), ("high", 3)])
        self.assertEqual(ends, [("high", "max", 3), ("low", "min", 1)])
        self.assertEqual(sources.effort_ends([("high", 3)]), [("high", None, 3)])
        same = sources.effort_ends([("high", 3), ("thinking", 4)])
        self.assertEqual((len(same), same[0][1]), (1, None), "same level: one main score")
        self.assertEqual([e[:2] for e in sources.effort_ends([("reasoning", 1), ("non-reasoning", 0)])],
                         [("reasoning", "max"), ("non-reasoning", "min")])

    def test_artificial_analysis_keeps_both_variants(self):
        rows = [{"name": "gpt-oss-20b (Low)", "slug": "gpt-oss-20b-low", "evaluations": {"tau2": 0.5029, "lcr": 0.31}},
                {"name": "gpt-oss-20b (High)", "slug": "gpt-oss-20b", "evaluations": {"tau2": 0.6023}},
                {"name": "gpt-oss-120b (High)", "slug": "gpt-oss-120b", "evaluations": {"tau2": 0.7}}]
        model = {"key": "openai/gpt-oss-20b", "display_name": "GPT-OSS 20B", "model_uid": "lmstudio:openai/gpt-oss-20b@mxfp4"}
        with mock.patch.object(sources, "_cache_get", return_value={"data": rows}):
            got = sources.artificial_analysis(model, "key")
        got = {(b["raw_name"], b["effort"], b["effort_end"]): b["score"] for b in got}
        self.assertEqual(got, {("tau2", "high", "max"): 60.23, ("tau2", "low", "min"): 50.29, ("lcr", "low", "min"): 31.0})

    def test_merge_keeps_low_beside_main_and_promotes_low_only(self):
        from benchlm.enrich import _merge
        e = lambda name, score, effort=None, end=None, method="api": {"name": name, "category": "agentic", "score": score,
                                                                       "method": method, "effort": effort, "effort_end": end}
        out = _merge([e("τ²-bench", 60.2, "high", "max"), e("τ²-bench", 50.3, "low", "min"), e("AA-LCR", 31, "low", "min")])
        got = {(b["name"], b["effort_end"]): b["score"] for b in out}
        self.assertEqual(got, {("τ²-bench", "max"): 60.2, ("τ²-bench", "min"): 50.3, ("AA-LCR", None): 31})
        mixed = _merge([e("Terminal-Bench", 3.4, method="leaderboard"), e("Terminal-Bench", 4.55, "low", "min")])
        self.assertEqual([(b["score"], b["effort_end"]) for b in mixed], [(3.4, None)], "no cross-source pairing")


class SyncGuardTests(unittest.TestCase):
    def test_editor_copies_of_the_key_file_are_refused(self):
        try:
            from benchlm.sync import _forbidden     # maintainer-only module (not in the public copy)
        except ImportError:
            self.skipTest("bench sync not included")
        for p in ("benchmark-local-llms/.secrets.local.json.swp", "secrets.local.json", "secrets.local.json~",
                  "secrets.local.json.bak", ".env"):
            self.assertTrue(_forbidden(p), p)
        for p in ("benchmark-local-llms/data/results.json", "src/benchlm/sync.py", "README.md"):
            self.assertFalse(_forbidden(p), p)


class SwapTests(unittest.TestCase):
    def run_with_swap(self, gb):
        return {"memory": {"swap_used_delta_bytes": int(gb * 1024 ** 3)}, "warnings": ["other"]}

    def test_threshold_and_idempotent(self):
        r = self.run_with_swap(15.0)
        dbm.set_swap_warning(r, 1)
        dbm.set_swap_warning(r, 1)
        self.assertEqual(len([w for w in r["warnings"] if w.startswith("swap grew by 15.0 GB")]), 1)
        dbm.set_swap_warning(r, 20)
        self.assertEqual(r["warnings"], ["other"], "re-applied with a higher threshold: gone")
        small = self.run_with_swap(0.5)
        dbm.set_swap_warning(small, 1)
        self.assertEqual(small["warnings"], ["other"])
        self.assertEqual(dbm.summarize(self.run_with_swap(2.21))["swap_growth_gb"], 2.21)

    def test_settings_do_not_change_profile_hash(self):
        p = load_profile()
        self.assertEqual(p["hash"], "dcb9a321")
        self.assertEqual(profile_hash(dict(p, swap_warning_gb=5, max_test_restarts=9)), "dcb9a321")


class RenamedModelTests(unittest.TestCase):
    def test_renamed_variant_shows_once_per_machine(self):
        base = {"engine": "lmstudio", "key": "openai/gpt-oss-20b", "format": "mlx",
                "quantization": {"name": "MXFP4"}, "size_bytes": 12104314420}
        gguf = dict(base, model_uid="lmstudio:openai/gpt-oss-20b@gguf-mxfp4", format="gguf", size_bytes=12109664217)
        old = dict(base, model_uid="lmstudio:openai/gpt-oss-20b@mlx-mxfp4", first_seen="2026-10-19T21:22:43Z")
        new = dict(base, model_uid="lmstudio:openai/gpt-oss-20b@mxfp4", first_seen="2026-10-21T01:43:04Z")
        run = lambda uid, mid, t: {"run_id": t, "model_uid": uid, "machine_id": mid, "started_at": t}
        db = {"models": {m["model_uid"]: m for m in (gguf, old, new)},
              "public": {old["model_uid"]: {"benchmarks": [1]}},
              "runs": [run(old["model_uid"], "mac", "2026-10-19"), run(new["model_uid"], "mac", "2026-10-22"),
                       run(old["model_uid"], "pc", "2026-10-20"), run(gguf["model_uid"], "mac", "2026-10-19")]}
        out = dbm.collapse_renamed(db)
        self.assertEqual(set(out["models"]), {gguf["model_uid"], new["model_uid"]})
        self.assertEqual(out["models"][new["model_uid"]]["aliases"], [old["model_uid"]])
        self.assertEqual(out["models"][new["model_uid"]]["first_seen"], "2026-10-19T21:22:43Z")
        self.assertEqual(out["aliases"], {old["model_uid"]: new["model_uid"]})
        self.assertEqual(out["public"][new["model_uid"]], {"benchmarks": [1]})
        moved = [r for r in out["runs"] if r.get("listed_as")]
        self.assertEqual([(r["machine_id"], r["model_uid"]) for r in moved],
                         [("mac", new["model_uid"]), ("pc", new["model_uid"])])
        self.assertEqual(dbm.runs_for(out, gguf["model_uid"])[0]["model_uid"], gguf["model_uid"])


if __name__ == "__main__":
    unittest.main()
