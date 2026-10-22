"""Stdlib unit tests:  python3 -m unittest discover -s tests   (run from benchmark-local-llms/)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from benchlm import db as dbm  # noqa: E402
from benchlm.engines.base import parse_params, has_qat, bits_from_quant  # noqa: E402
from benchlm.engines.lmstudio import LMStudio  # noqa: E402
from benchlm.enrich.benchnames import canonical  # noqa: E402
from benchlm.enrich.cardparse import extract_benchmarks, match_score  # noqa: E402
from benchlm.enrich.sources import score_candidates, search_names, strict_name_match  # noqa: E402

MD_CARD = """
|  | Acme 2  30B | Acme 2  20B A3B | Other 9B |
| :---- | :---- | :---- | :---- |
| MMLU Pro | 80.1% | 75.0% | 60.0% |
| GPQA Diamond | 70.5% | 66.0% | 40.0% |
| **Vision** |  |  |  |
| MMMU Pro | 61.0% | 58.0% | - |
"""

HTML_CARD = """<table><thead><tr><th></th><th>Acme2-30B</th><th>Rival-30B</th></tr></thead><tbody>
<tr><td colspan="3">Coding</td></tr>
<tr><td><div>Agentic coding</div><div>SWE-bench Verified</div></td><td><strong>65.2</strong></td><td>60.1</td></tr>
<tr><td><div>Function calling</div><div>BFCL v3</div></td><td>70.0</td><td>71.0</td></tr>
</tbody></table>"""

# Category column + vertical tab inside a header cell (seen in real cards).
CAT_CARD = ("| Category | Benchmark | Acme 2-30B\x0bHigh Reasoning | Rival |\n| :-- | :-- | :-: | :-: |\n"
            "| *Agentic* | Tau2 bench | **55.5** | 50 |\n|  | IFBench | 77.0 | 70 |\n")


class ParserTests(unittest.TestCase):
    def test_markdown_picks_right_column(self):
        b = {x["name"]: x for x in extract_benchmarks(MD_CARD, ["acme/acme-2-20b-a3b-qat", "Acme 2 20B A3B"])}
        self.assertEqual(b["MMLU-Pro"]["score"], 75.0)
        self.assertEqual(b["GPQA Diamond"]["score"], 66.0)
        self.assertEqual(b["MMMU Pro"]["category"], "vision")

    def test_size_must_agree(self):
        self.assertLess(match_score("Acme 2 30B", ["acme-2-20b"]), 0.5)

    def test_html_table_and_sections(self):
        b = {x["name"]: x for x in extract_benchmarks(HTML_CARD, ["Acme2 30B"])}
        self.assertEqual(b["SWE-bench Verified"]["score"], 65.2)
        self.assertEqual(b["BFCL"]["category"], "agentic")

    def test_category_column_and_vertical_tab(self):
        b = {x["name"]: x for x in extract_benchmarks(CAT_CARD, ["acme-2", "Acme 2 30B"])}
        self.assertEqual(b["τ²-bench"]["score"], 55.5)
        self.assertEqual(b["IFBench"]["score"], 77.0)

    def test_canonical_names(self):
        self.assertEqual(canonical("GPQA-Diamond (0-shot)")[0], "GPQA Diamond")
        self.assertEqual(canonical("LiveCodeBench v6")[0], "LiveCodeBench")
        self.assertEqual(canonical("AIME 2026 no tools")[0], "AIME 2026")

    def test_strict_name_match(self):
        names = ["qwen3.8-27b", "Qwen3.8 27B"]
        self.assertTrue(strict_name_match("qwen3.8-27b", names))
        self.assertFalse(strict_name_match("qwen3.8-max", names))
        self.assertTrue(strict_name_match("gemma-4-31b-it", ["gemma-4-31b"]))


class RepoMatchTests(unittest.TestCase):
    def pick(self, model, ids):
        cands = {i: {"id": i, "downloads": d} for i, d in ids}
        return score_candidates(model, search_names(model), cands)["repo"]

    def test_prefers_publisher_over_fine_tunes(self):
        m = {"key": "nvidia/nemotron-3-nano-omni", "display_name": "Nemotron 3 Nano Omni", "publisher": "nvidia", "format": "gguf"}
        self.assertEqual(self.pick(m, [("nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16", 249267),
                                       ("stockmark/Stockmark-Nemotron-3-Nano-Omni-JapanDocReader", 675),
                                       ("lmstudio-community/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-GGUF", 31738)]),
                         "nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16")

    def test_splash_maps_to_base_model(self):
        m = {"key": "qwen3.8-27b-splash", "display_name": "Qwen3.8 27B Splash", "publisher": "incoai", "format": "splash"}
        self.assertEqual(search_names(m)[0], "qwen3.8-27b")
        self.assertEqual(self.pick(m, [("Qwen/Qwen3.8-27B", 7458401), ("incoai/Qwen3.8-27B-Splash", 10),
                                       ("tokenfires/Qwen3.8-27B-Splash", 5)]), "Qwen/Qwen3.8-27B")


class ModelInfoTests(unittest.TestCase):
    def test_params(self):
        self.assertEqual(parse_params("26B", "gemma-4-26b-a4b-qat"), (26.0, 4.0))
        self.assertEqual(parse_params("", "qwen3-30b-a3b"), (30.0, 3.0))
        self.assertTrue(has_qat("google/gemma-4-31b-qat"))
        self.assertFalse(has_qat("meta/muse-glimmer"))
        self.assertEqual(bits_from_quant("Q4_K_M"), 4.0)
        self.assertEqual(bits_from_quant("6bit"), 6.0)

    def test_reasoning_mapping(self):
        lm = LMStudio("http://x")
        mk = lambda opts: {"capabilities": {"reasoning": {"allowed_options": opts}}}
        self.assertEqual(lm.resolve_reasoning(mk(["off", "on"]), "high"), "on")
        self.assertEqual(lm.resolve_reasoning(mk(["low", "medium", "high", "xhigh"]), "off"), "low")
        self.assertEqual(lm.resolve_reasoning(mk(["off", "low", "medium", "xhigh", "on"]), "high"), "on")
        self.assertIsNone(lm.resolve_reasoning({"capabilities": {}}, "off"))
        with self.assertRaises(ValueError):
            lm.resolve_reasoning({"capabilities": {}}, "high")


class DbTests(unittest.TestCase):
    def test_status(self):
        db = dbm.empty_db()
        model = {"model_uid": "x:m", "fingerprint": "f"}
        prof = {"hash": "h"}
        self.assertEqual(dbm.status_for(db, model, "mac", prof, "1"), "new")
        db["runs"].append({"model_uid": "x:m", "machine_id": "mac", "status": "complete", "subset": True,
                           "suite_version": "1", "profile_hash": "h", "model_fingerprint": "f"})
        self.assertEqual(dbm.status_for(db, model, "mac", prof, "1"), "new")   # quick runs don't count
        db["runs"].append({"model_uid": "x:m", "machine_id": "mac", "status": "complete",
                           "suite_version": "1", "profile_hash": "h", "model_fingerprint": "f"})
        self.assertEqual(dbm.status_for(db, model, "mac", prof, "1"), "done")
        self.assertEqual(dbm.status_for(db, model, "mac", {"hash": "other"}, "1"), "stale")

    def test_renamed_variant_is_done(self):
        db = dbm.empty_db()
        base = {"engine": "lmstudio", "key": "openai/gpt-oss-20b", "format": "mlx",
                "quantization": {"name": "MXFP4"}, "size_bytes": 12104314420}
        db["models"]["lmstudio:openai/gpt-oss-20b@mlx-mxfp4"] = dict(base, model_uid="lmstudio:openai/gpt-oss-20b@mlx-mxfp4")
        db["runs"].append({"model_uid": "lmstudio:openai/gpt-oss-20b@mlx-mxfp4", "machine_id": "mac", "status": "complete",
                           "suite_version": "1", "profile_hash": "h", "model_fingerprint": "old"})
        renamed = dict(base, model_uid="lmstudio:openai/gpt-oss-20b@mxfp4", fingerprint="new")
        self.assertEqual(dbm.status_for(db, renamed, "mac", {"hash": "h"}, "1"), "done")
        self.assertEqual(dbm.status_for(db, renamed, "other-pc", {"hash": "h"}, "1"), "new")
        other_file = dict(renamed, size_bytes=12109664217, format="gguf")   # the GGUF is a different file
        self.assertEqual(dbm.status_for(db, other_file, "mac", {"hash": "h"}, "1"), "new")

    def test_agg(self):
        self.assertEqual(dbm.agg([3, 1, 2])["median"], 2)
        self.assertIsNone(dbm.agg([None]))


if __name__ == "__main__":
    unittest.main()
