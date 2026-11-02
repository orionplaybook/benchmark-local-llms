"""Where each tested model was downloaded from:  python3 -m unittest discover -s tests   (from benchmark-local-llms/)."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from benchlm import db as dbm  # noqa: E402
from benchlm.engines import lmstudio  # noqa: E402
from benchlm.engines.ollama import ollama_source  # noqa: E402
from benchlm.engines.omlx import OMLX  # noqa: E402

HUB_YAML = """model: openai/gpt-oss-20b
base:
  - key: lmstudio-community/gpt-oss-20b-gguf
    sources:
      - type: huggingface
        user: lmstudio-community
        repo: gpt-oss-20b-GGUF
  - key: mlx-community/gpt-oss-20b-mxfp4-q8
    sources:
      - type: huggingface
        user: mlx-community
        repo: gpt-oss-20b-MXFP4-Q8
"""


class LMStudioSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.models = root / "models"
        for repo, files in {"mlx-community/gpt-oss-20b-MXFP4-Q8": ["model.safetensors", "config.json"],
                            "lmstudio-community/gpt-oss-20b-GGUF": ["gpt-oss-20b-MXFP4.gguf"],
                            "incoai/Qwen3.8-27B-Splash": ["model.yuzu"],
                            "unsloth/gemma-4-31b-it-GGUF": ["gemma-4-31b-it-Q4_K_M.gguf", "gemma-4-31b-it-Q8_0.gguf",
                                                            "mmproj-F16.gguf"]}.items():
            (self.models / repo).mkdir(parents=True)
            for f in files:
                (self.models / repo / f).write_text("x")
        hub = root / "hub" / "models" / "openai" / "gpt-oss-20b"
        hub.mkdir(parents=True)
        (hub / "model.yaml").write_text(HUB_YAML)
        self.patch = mock.patch.object(lmstudio, "LMS_HOME", str(root))
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def find(self, *args):
        return lmstudio.find_source(*args, models_dir=str(self.models))

    def test_catalog_model_picks_the_downloaded_format(self):
        self.assertEqual(self.find("openai/gpt-oss-20b", "mxfp4", "mlx", "MXFP4")["repo"], "mlx-community/gpt-oss-20b-MXFP4-Q8")
        g = self.find("openai/gpt-oss-20b", "mxfp4", "gguf", "MXFP4")
        self.assertEqual((g["repo"], g["file"]), ("lmstudio-community/gpt-oss-20b-GGUF", "gpt-oss-20b-MXFP4.gguf"))

    def test_repo_download_matched_by_name(self):
        s = self.find("qwen3.8-27b-splash", None, "splash", "4bit")
        self.assertEqual(s["url"], "https://huggingface.co/incoai/Qwen3.8-27B-Splash")

    def test_gguf_file_picked_by_quantization(self):
        s = self.find("unsloth/gemma-4-31b-it-GGUF", "q8_0", "gguf", "Q8_0")
        self.assertEqual(s["file"], "gemma-4-31b-it-Q8_0.gguf")
        self.assertTrue(s["url"].endswith("/blob/main/gemma-4-31b-it-Q8_0.gguf"))

    def test_not_downloaded(self):
        self.assertIsNone(self.find("someone/missing-model", None, "mlx", None))


class OtherEngineSourceTests(unittest.TestCase):
    def test_ollama(self):
        self.assertEqual(ollama_source("gpt-oss:20b")["url"], "https://ollama.com/library/gpt-oss:20b")
        self.assertEqual(ollama_source("user/model:tag")["url"], "https://ollama.com/user/model:tag")
        s = ollama_source("hf.co/unsloth/gemma-4-31b-it-GGUF:Q4_K_M")
        self.assertEqual((s["kind"], s["repo"], s["tag"]), ("huggingface", "unsloth/gemma-4-31b-it-GGUF", "Q4_K_M"))

    def test_omlx(self):
        s = OMLX._source({"model_path": "/u/.omlx/models/mlx-community/gpt-oss-20b-MXFP4-Q8",
                          "display_name": "mlx-community/gpt-oss-20b-MXFP4-Q8"})
        self.assertEqual(s["repo"], "mlx-community/gpt-oss-20b-MXFP4-Q8")
        self.assertEqual(OMLX._source({"source_repo_id": "a/b", "model_path": "/x/b"})["repo"], "a/b")
        self.assertIsNone(OMLX._source({"model_path": "/u/.omlx/models/plain", "display_name": "plain"}))


class SharedNameTests(unittest.TestCase):
    def test_same_model_rows_share_public_scores(self):
        b = lambda n, sc, meth: {"name": n, "category": "math", "score": sc, "method": meth}
        db = {"models": {u: {"model_uid": u} for u in ("lmstudio:a", "omlx:b", "lmstudio:other")},
              "public": {
                  "lmstudio:a": {"hf_repo": "maker/m", "benchmarks": [b("AIME", 80, "api"), b("CharXiv", 90, "local-llm:x")],
                                 "links": [{"url": "https://artificialanalysis.ai/"}]},
                  "omlx:b": {"hf_repo": "mlx-community/m-4bit", "base_model": "maker/m",
                             "benchmarks": [b("AIME", 81, "card-table")], "links": [],
                             "llm_extraction_run": {"extracted": 0}},
                  "lmstudio:other": {"hf_repo": "maker/other", "benchmarks": [b("AIME", 10, "api")]}}}
        dbm.share_public(db)
        got = lambda u: {x["name"]: (x["score"], x["method"]) for x in db["public"][u]["benchmarks"]}
        self.assertEqual(got("lmstudio:a"), {"AIME": (81, "card-table"), "CharXiv": (90, "local-llm:x")})
        self.assertEqual(got("omlx:b"), got("lmstudio:a"))
        self.assertEqual(db["public"]["omlx:b"]["links"], [{"url": "https://artificialanalysis.ai/"}])
        self.assertEqual(db["public"]["omlx:b"]["llm_extraction_run"], {"extracted": 0})   # per-row result kept
        self.assertEqual(got("lmstudio:other"), {"AIME": (10, "api")})

    def test_one_name_across_engines(self):
        db = {"models": {
            "lmstudio:openai/gpt-oss-20b@mxfp4": {"model_uid": "lmstudio:openai/gpt-oss-20b@mxfp4", "engine": "lmstudio",
                                                  "display_name": "GPT-OSS 20B"},
            "ollama:gpt-oss:20b": {"model_uid": "ollama:gpt-oss:20b", "engine": "ollama", "display_name": "gpt-oss:20b"},
            "omlx:gpt-oss-20b-MXFP4-Q8": {"model_uid": "omlx:gpt-oss-20b-MXFP4-Q8", "engine": "omlx",
                                          "display_name": "mlx-community/gpt-oss-20b-MXFP4-Q8"},
            "ollama:gemma4:26b-qat": {"model_uid": "ollama:gemma4:26b-qat", "engine": "ollama", "qat": True,
                                      "display_name": "gemma4:26b-qat"},
            "ollama:gemma4:26b": {"model_uid": "ollama:gemma4:26b", "engine": "ollama", "display_name": "gemma4:26b"},
            "lmstudio:nvidia/nemotron-3-nano-4b": {"model_uid": "lmstudio:nvidia/nemotron-3-nano-4b", "engine": "lmstudio",
                                                   "display_name": "Nemotron 3 Nano 4B"},
        }, "public": {
            "lmstudio:openai/gpt-oss-20b@mxfp4": {"hf_repo": "openai/gpt-oss-20b"},
            "ollama:gpt-oss:20b": {"hf_repo": "openai/gpt-oss-20b"},
            "omlx:gpt-oss-20b-MXFP4-Q8": {"hf_repo": "mlx-community/gpt-oss-20b-MXFP4-Q8", "base_model": "openai/gpt-oss-20b"},
            "ollama:gemma4:26b-qat": {"hf_repo": "google/gemma-4-26B-A4B-it"},
            "ollama:gemma4:26b": {"hf_repo": "google/gemma-4-26B-A4B-it"},
            # a maker repo whose base model is another model: not a repackaged copy, keeps its own identity
            "lmstudio:nvidia/nemotron-3-nano-4b": {"hf_repo": "nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16",
                                                   "base_model": "nvidia/NVIDIA-Nemotron-Nano-9B-v2"},
        }}
        dbm.share_names(db)
        names = {uid: m["display_name"] for uid, m in db["models"].items()}
        self.assertEqual(names["ollama:gpt-oss:20b"], "GPT-OSS 20B")
        self.assertEqual(names["omlx:gpt-oss-20b-MXFP4-Q8"], "GPT-OSS 20B")
        self.assertEqual(db["models"]["omlx:gpt-oss-20b-MXFP4-Q8"]["engine_name"], "mlx-community/gpt-oss-20b-MXFP4-Q8")
        self.assertEqual(names["ollama:gemma4:26b-qat"], "gemma4:26b-qat")   # QAT and non-QAT stay apart
        self.assertEqual(names["lmstudio:nvidia/nemotron-3-nano-4b"], "Nemotron 3 Nano 4B")
        self.assertEqual(dbm.model_origin({"hf_repo": "google/gemma-4-26B-A4B-it-QAT"}), "google/gemma-4-26b-a4b-it")

    def test_active_params_from_the_model_card(self):
        card = {"model_uid": "l", "engine": "lmstudio", "display_name": "GPT-OSS 20B", "is_moe": True,
                "params_active_b": 3.6, "params_active_source": "model card", "moe_experts": 32}
        est = {"model_uid": "o", "engine": "omlx", "display_name": "x", "is_moe": True,
               "params_active_b": 4.2, "params_active_source": "estimated from config.json"}
        named = {"model_uid": "n", "engine": "ollama", "display_name": "y", "params_active_b": 3.0,
                 "params_active_source": "name"}
        db = {"models": {"l": card, "o": est}, "public": {"l": {"hf_repo": "a/b"}, "o": {"hf_repo": "a/b"}}}
        dbm.share_active_params(db)
        self.assertEqual((est["params_active_b"], est["params_active_source"], est["moe_experts"]), (3.6, "model card", 32))
        db = {"models": {"l": dict(card), "n": named}, "public": {"l": {"hf_repo": "a/b"}, "n": {"hf_repo": "a/b"}}}
        dbm.share_active_params(db)
        self.assertEqual(db["models"]["l"]["params_active_b"], 3.0)   # a value from the model's own name ranks first

    def test_manual_name_wins(self):
        db = {"models": {"a": {"model_uid": "a", "engine": "lmstudio", "display_name": "Nice"},
                         "b": {"model_uid": "b", "engine": "ollama", "display_name": "My own name"}},
              "public": {"a": {"hf_repo": "x/y"}, "b": {"hf_repo": "x/y"}}}
        dbm.share_names(db, keep={"b"})
        self.assertEqual(db["models"]["b"]["display_name"], "My own name")


if __name__ == "__main__":
    unittest.main()
