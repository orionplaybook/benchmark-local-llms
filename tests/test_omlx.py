"""oMLX adapter, without a server:  python3 -m unittest discover -s tests   (run from benchmark-local-llms/)."""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from benchlm import http  # noqa: E402
from benchlm.engines import omlx as om  # noqa: E402

PROFILE = {"context_length": 114688, "temperature": 0, "top_p": 1, "top_k": 1, "min_p": 0, "repeat_penalty": 1,
           "seed": 42, "request_timeout_s": 60}


def engine():
    return om.OMLX("http://127.0.0.1:8000", "k")


class NormalizeTests(unittest.TestCase):
    def test_gpt_oss_reasoning_levels(self):
        m = engine()._normalize({"id": "gpt-oss-20b-MXFP4-Q8", "model_type": "llm", "model_format": "mlx",
                                 "source_repo_id": "mlx-community/gpt-oss-20b-MXFP4-Q8", "estimated_size": 12e9,
                                 "model_context_length": 131072, "reasoning_efforts": [],
                                 "reasoning_levels": ["low", "medium", "high"]})
        self.assertEqual(m["model_uid"], "omlx:gpt-oss-20b-MXFP4-Q8")
        self.assertEqual(m["publisher"], "mlx-community")
        self.assertEqual(m["quantization"]["name"], "MXFP4-Q8")
        self.assertEqual(m["params_total_b"], 20)
        self.assertEqual(m["max_context_length"], 131072)
        eng = engine()
        self.assertEqual(eng.resolve_reasoning(m, "off"), "low")
        self.assertEqual(eng.resolve_reasoning(m, "high"), "high")

    def test_thinking_toggle_and_moe_name(self):
        m = engine()._normalize({"id": "gemma-4-26B-A4B-it-QAT-MLX-4bit", "model_type": "vlm",
                                 "model_path": "/x/lmstudio-community/gemma-4-26B-A4B-it-QAT-MLX-4bit",
                                 "thinking_default": False})
        self.assertEqual((m["params_total_b"], m["params_active_b"], m["is_moe"]), (26, 4, True))
        self.assertTrue(m["qat"])
        self.assertTrue(m["capabilities"]["vision"])
        self.assertEqual(m["publisher"], "lmstudio-community")
        self.assertEqual(m["quantization"]["bits"], 4)
        self.assertEqual(engine().resolve_reasoning(m, "off"), "off")
        self.assertEqual(engine().resolve_reasoning(m, "high"), "on")

    def test_no_thinking(self):
        m = engine()._normalize({"id": "plain-7b-4bit", "model_type": "llm"})
        self.assertIsNone(m["capabilities"]["reasoning"])
        self.assertIsNone(engine().resolve_reasoning(m, "off"))
        with self.assertRaises(ValueError):
            engine().resolve_reasoning(m, "high")

    def test_lists_only_language_models(self):
        eng = engine()
        rows = [{"id": "a-4bit", "model_type": "llm"}, {"id": "bge-m3", "model_type": "embedding"},
                {"id": "draft", "model_type": "llm", "is_helper": True}, {"id": "v", "model_type": "vlm"}]
        with mock.patch.object(eng, "_models", return_value=rows):
            self.assertEqual([m["key"] for m in eng.list_models()], ["a-4bit", "v"])


class LifecycleTests(unittest.TestCase):
    def test_context_raised_for_the_run_and_restored_on_unload(self):
        eng = engine()
        calls = []

        def fake(method, path, payload=None, timeout=60):
            calls.append((method, path, payload))
            return {}
        with mock.patch.object(eng, "_call", side_effect=fake), \
                mock.patch.object(eng, "_settings", return_value={"max_context_window": None}):
            inst = eng.load({"key": "org model", "_load_key": "org model"}, PROFILE)
            eng.unload(inst)
        self.assertEqual(calls[0], ("PUT", "/admin/api/models/org%20model/settings", {"max_context_window": 114688}))
        self.assertEqual(calls[1][:2], ("POST", "/v1/models/org%20model/load"))
        self.assertEqual(calls[2][:2], ("POST", "/v1/models/org%20model/unload"))
        self.assertEqual(calls[3], ("PUT", "/admin/api/models/org%20model/settings", {"max_context_window": None}))
        self.assertEqual(inst["load_config"]["context_length"], 114688)

    def test_context_left_alone_when_already_set(self):
        eng = engine()
        with mock.patch.object(eng, "_call", return_value={}) as call, \
                mock.patch.object(eng, "_settings", return_value={"max_context_window": 114688}):
            eng.unload(eng.load({"key": "m"}, PROFILE))
        self.assertEqual([c.args[0] for c in call.call_args_list], ["POST", "POST"])


class ChatTests(unittest.TestCase):
    def test_stream_parsing_and_history(self):
        events = [
            ("message", {"choices": [{"delta": {"role": "assistant"}}]}),
            ("message", {"prompt_progress": {"processed": 10, "total": 20}}),
            ("message", {"choices": [{"delta": {"reasoning_content": "think "}}]}),
            ("message", {"choices": [{"delta": {"content": "Hello"}}]}),
            ("message", {"choices": [{"delta": {"content": " there"}, "finish_reason": "stop"}]}),
            ("message", {"choices": [], "usage": {
                "prompt_tokens": 100, "completion_tokens": 7, "prompt_tokens_details": {"cached_tokens": 40},
                "completion_tokens_details": {"reasoning_tokens": 2}, "time_to_first_token": 0.5,
                "prompt_tokens_per_second": 120.0, "generation_tokens_per_second": 55.5}}),
        ]
        sent = {}

        def fake_stream(url, payload, headers=None, timeout=0, cancel=None):
            sent.clear()
            sent.update(payload)
            yield from events
        eng = engine()
        with mock.patch.object(http, "stream_sse", side_effect=fake_stream):
            t = eng.chat("m", {}, "sys", "hi", None, "off", 50, PROFILE)
        self.assertEqual(sent["messages"], [{"role": "system", "content": "sys"}, {"role": "user", "content": "hi"}])
        self.assertIs(sent["chat_template_kwargs"]["enable_thinking"], False)
        self.assertTrue(sent["stream_options"]["include_usage"])
        self.assertEqual((t.text, t.reasoning_text), ("Hello there", "think "))
        self.assertEqual((t.prompt_tokens, t.new_prompt_tokens, t.completion_tokens, t.reasoning_tokens), (100, 60, 7, 2))
        self.assertEqual((t.prefill_tps, t.decode_tps, t.finish_reason), (120.0, 55.5, "stop"))
        self.assertEqual(t.state[-1], {"role": "assistant", "content": "Hello there"})

        with mock.patch.object(http, "stream_sse", side_effect=fake_stream):
            eng.chat("m", {}, "sys", "next", t.state, "high", 50, PROFILE)
        self.assertEqual(len(sent["messages"]), 4)
        self.assertEqual(sent["reasoning_effort"], "high")
        self.assertNotIn("chat_template_kwargs", sent)


if __name__ == "__main__":
    unittest.main()
