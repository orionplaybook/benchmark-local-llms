"""Loads the versioned benchmark suite from benchmarks/."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from .answers import normalize, section_of
from .config import BENCH_DIR


def _json(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _read(p: Path) -> str:
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


class Suite:
    def __init__(self, root: Path = BENCH_DIR):
        self.root = root
        self.short = _json(root / "short_conversation.json")
        lc = root / "long_context"
        self.long = _json(lc / "conversation.json")
        self.document = _read(lc / "document.md")
        self.facts = {f["id"]: f for f in _json(lc / "facts.json")}
        ex = root / "extraction"
        self.extraction = _json(ex / "prompt.json")
        self.page1 = _read(ex / "page_model_card.md")
        self.page2 = _read(ex / "page_leaderboard.md")
        self.answer_key = _json(ex / "answer_key.json")
        spec = importlib.util.spec_from_file_location("score_extraction", ex / "score_extraction.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.score_extraction = mod.score
        self.version = str(self.short.get("suite_version", "1"))
        h = hashlib.sha1()
        for p in sorted(root.rglob("*")):
            if p.is_file() and p.suffix in (".json", ".md", ".py") and p.name != "README.md":
                h.update(p.name.encode())
                h.update(p.read_bytes())
        self.hash = h.hexdigest()[:10]

    # --- tests as uniform turn lists --------------------------------------
    def tests(self) -> dict:
        """{name: {system_prompt, turns:[{label, user, max_tokens, fact_ids?}]}}"""
        long_turns = []
        for t in self.long["turns"]:
            user = t.get("user") or t.get("user_template", "")
            user = user.replace("<<DOCUMENT>>", self.document)
            long_turns.append({"label": t.get("label"), "user": user, "max_tokens": t.get("max_tokens", 300),
                               "fact_ids": t.get("fact_ids") or []})
        ex = self.extraction
        ex_user = ex["user_template"].replace("<<PAGE1>>", self.page1).replace("<<PAGE2>>", self.page2)
        return {
            "short": {"system_prompt": self.short.get("system_prompt", ""),
                      "turns": [{"label": t.get("label"), "user": t["user"], "max_tokens": t.get("max_tokens", 256)}
                                for t in self.short["turns"]]},
            "extraction": {"system_prompt": ex.get("system_prompt", ""),
                           "turns": [{"label": "Extract benchmark JSON", "user": ex_user,
                                      "max_tokens": ex.get("max_tokens", 900)}]},
            "long": {"system_prompt": self.long.get("system_prompt", ""), "turns": long_turns},
        }

    def probe(self) -> dict:
        t = self.short["turns"][0]
        return {"system_prompt": self.short.get("system_prompt", ""), "user": t["user"], "max_tokens": 48}

    def recall(self, turns_text: list, turn_defs: list) -> dict:
        correct = total = 0
        details = []
        for text, td in zip(turns_text, turn_defs):
            low = normalize(text)   # Unicode hyphens/spaces count as plain ones
            for fid in td.get("fact_ids") or []:
                fact = self.facts.get(fid)
                if not fact:
                    continue
                total += 1
                ok = any(normalize(a) in low for a in fact["answers"])
                correct += ok
                details.append({"id": fid, "ok": ok, "section": section_of(td.get("label")),
                                "position_pct": fact.get("position_pct"), "expected": fact["answers"][0]})
        return {"recall_correct": correct, "recall_total": total,
                "recall": round(correct / total, 3) if total else None, "details": details}
