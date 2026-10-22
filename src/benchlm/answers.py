"""What came back as the answer: the visible answer vs. the reasoning ("thinking") channel.

Scores always use the visible answer, because that is what an agent receives. A model that writes its whole
answer in the reasoning channel (visible answer empty, generation finished normally) is recorded as a distinct
outcome, with a secondary score computed on the reasoning text, so it isn't mistaken for a plain wrong answer."""
from __future__ import annotations

import re
import unicodedata
from typing import List, Optional

IN_REASONING = "answer_in_reasoning_channel"
# Thinking used the whole output budget before any visible answer: the model never answered. Scored as wrong,
# but shown as its own outcome so a low score isn't read as wrong answers.
NO_ANSWER_BUDGET = "no_answer_thinking_budget"
TEXT_FIELDS = ("text", "reasoning_text")    # answer texts in raw request records


def outcome(text: Optional[str], reasoning: Optional[str], finish_reason: Optional[str],
            reasoning_tokens: Optional[int] = None) -> Optional[str]:
    if (text or "").strip():
        return None
    thought = bool((reasoning or "").strip()) or (reasoning_tokens or 0) > 0
    if thought and finish_reason == "stop" and (reasoning or "").strip():
        return IN_REASONING
    if thought and finish_reason == "length":
        return NO_ANSWER_BUDGET
    return None


def record_outcome(rec: dict) -> Optional[str]:
    """Outcome of a raw request record. Works on older raw files too (they keep the character counts)."""
    if rec.get("discarded") or rec.get("abandoned"):
        return None
    if rec.get("outcome"):
        return rec["outcome"]
    if rec.get("text_chars") is None:
        return None
    if rec.get("text_chars") != 0:
        return None
    if (rec.get("reasoning_chars") or 0) > 0 and rec.get("finish_reason") == "stop":
        return IN_REASONING
    if ((rec.get("reasoning_chars") or 0) > 0 or (rec.get("reasoning_tokens") or 0) > 0) \
            and rec.get("finish_reason") == "length":
        return NO_ANSWER_BUDGET
    return None


def warning(test: str, mode: str, n: int, total: int) -> str:
    return (f"{test}/{mode}: {n} of {total} answer(s) were written only in the reasoning channel (visible answer "
            f"empty); scores use the visible answer")


def truncated_warning(test: str, mode: str, n: int, thinking: bool) -> str:
    return (f"{test}/{mode}: {n} turn(s) hit the output limit "
            f"({'thinking used the whole budget' if thinking else 'answer cut off'})")


def budget_warning(test: str, mode: str, n: int, total: int) -> str:
    return (f"{test}/{mode}: {n} of {total} answer(s) never arrived: thinking used the whole output budget before "
            f"any visible answer")


# Typographic variants some models write (gpt-oss: "BLUE‑HERON‑82" with U+2011 non-breaking hyphens and U+202F
# narrow no-break spaces). They must not turn a correct answer into a miss.
_DASHES = dict.fromkeys(map(ord, "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe58\ufe63\uff0d"), "-")


def normalize(text: Optional[str]) -> str:
    """Text for answer matching: compatibility forms folded (NFKC: no-break spaces become spaces), every dash
    variant a plain hyphen, runs of whitespace one space, lower case."""
    t = unicodedata.normalize("NFKC", text or "").translate(_DASHES)
    return re.sub(r"\s+", " ", t).lower()


_TURN_LABEL = re.compile(r"^(short|extraction|long)/(\w+)/r\d+/t(\d+)$")


def backfill(run: dict, raw: dict) -> bool:
    """Add reasoning-channel and out-of-budget counts to a run recorded before they existed, from its raw request records.
    Idempotent; returns True when something was added."""
    counts = {}
    for rec in (raw or {}).get("requests") or []:
        m = _TURN_LABEL.match(rec.get("label") or "")
        if not m or rec.get("discarded"):
            continue
        key = (m.group(1), m.group(2))
        c = counts.setdefault(key, {"total": 0, IN_REASONING: {"n": 0, "turns": {}},
                                    NO_ANSWER_BUDGET: {"n": 0, "turns": {}}})
        c["total"] += 1
        o = record_outcome(rec)
        if o in (IN_REASONING, NO_ANSWER_BUDGET):
            c[o]["n"] += 1
            i = int(m.group(3)) - 1
            c[o]["turns"][i] = c[o]["turns"].get(i, 0) + 1
    changed = False
    fields = ((IN_REASONING, "answer_in_reasoning", warning), (NO_ANSWER_BUDGET, "no_answer_budget", budget_warning))
    for (test, mode), c in counts.items():
        res = ((run.get("tests") or {}).get(test) or {}).get(mode)
        if not res or res.get("skipped"):
            continue
        if "answers_total" not in res:
            res["answers_total"] = c["total"]
            changed = True
        for o, field, warn in fields:
            if field + "_turns" in res:
                continue
            res[field + "_turns"] = c[o]["n"]
            for i, t in enumerate(res.get("turns") or []):
                t.setdefault(field, c[o]["turns"].get(i, 0))
            if c[o]["n"]:
                w = warn(test, mode, c[o]["n"], c["total"])
                if w not in run.setdefault("warnings", []):
                    run["warnings"].append(w)
            if o == NO_ANSWER_BUDGET and c[o]["n"]:
                # The older "hit the output limit" warning covered the same turns: keep only the turns that did
                # start an answer.
                old_w = truncated_warning(test, mode, res.get("truncated_turns") or 0, True)
                if old_w in run["warnings"]:
                    i = run["warnings"].index(old_w)
                    rest = (res.get("truncated_turns") or 0) - c[o]["n"]
                    if rest > 0:
                        run["warnings"][i] = truncated_warning(test, mode, rest, True)
                    else:
                        del run["warnings"][i]
            changed = True
    return changed


def strip_texts(raw: dict) -> dict:
    """Copy of a raw trace without answer texts (for `bench publish` unless --include-answers)."""
    out = dict(raw)
    out["requests"] = [{k: v for k, v in r.items() if k not in TEXT_FIELDS} for r in raw.get("requests") or []]
    return out


def scored_turn(test: str, label: Optional[str]) -> bool:
    """Whether a turn's answer is scored: the extraction answer and the long test's recall questions."""
    return test == "extraction" or (test == "long" and section_of(label) is not None)


def no_answer_scored(test: str, res: dict) -> tuple:
    """(scored answers that never arrived because thinking ran out of budget, scored answers) for one test/mode,
    or (None, None) when not checked."""
    turns = res.get("turns") or []
    if "no_answer_budget_turns" not in res or not turns:
        return None, None
    scored = [t for t in turns if scored_turn(test, t.get("label"))]
    if not scored:
        return None, None
    reps = res.get("repeats") or (res.get("answers_total") or 0) // len(turns) or 1
    return sum(t.get("no_answer_budget") or 0 for t in scored), reps * len(scored)


def section_of(label: Optional[str]) -> Optional[str]:
    """'Recall: start of document' -> 'start'."""
    m = re.search(r"\b(start|middle|end)\b", (label or "").lower())
    return m.group(1) if m else None


def merge_facts(runs: List[dict]) -> List[dict]:
    """Per-fact hits over repeats, from Suite.recall() details."""
    facts = {}
    for r in runs:
        for d in r.get("details") or []:
            f = facts.setdefault(d["id"], {k: d.get(k) for k in ("id", "section", "position_pct", "expected")})
            f["hits"] = f.get("hits", 0) + (1 if d["ok"] else 0)
            f["of"] = f.get("of", 0) + 1
    return sorted(facts.values(), key=lambda f: (f.get("position_pct") is None, f.get("position_pct") or 0))


def recall_by_section(facts: List[dict]) -> dict:
    out = {}
    for sec in ("start", "middle", "end"):
        fs = [f for f in facts if f.get("section") == sec]
        hits, of = sum(f["hits"] for f in fs), sum(f["of"] for f in fs)
        if of:
            out[sec] = round(hits / of, 3)
    return out
