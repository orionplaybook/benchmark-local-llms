#!/usr/bin/env python3
"""Score a model's JSON extraction output against answer_key.json.

    from score_extraction import score
    result = score(output_text, answer_key)

Returns {"json_valid", "fields_correct", "fields_total", "accuracy", "details"}.
Each top-level field in answer_key["fields"] and each benchmark in
answer_key["benchmarks"] counts as one field.

Robustness:
- removes <think>...</think> reasoning (and anything before a lone </think>)
- ignores ```json fences and surrounding prose
- uses the first balanced top-level JSON object that parses
- numbers: absolute tolerance 0.051; numeric strings like "71.2%", "14.8B",
  "131,072" are accepted
- strings: case-insensitive after trimming; an answer-key list means any of
  the listed strings is accepted
- benchmark names match case-insensitively after trimming and Unicode NFKC
  normalisation (so "τ²-bench" and "τ2-bench" are the same name)

Python 3.9 standard library only.
"""

import json
import os
import re
import sys
import unicodedata

NUM_TOL = 0.051


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def _strip_reasoning(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S | re.I)
    # Some chat templates emit only the closing tag.
    if re.search(r"</think>", text, flags=re.I):
        text = re.split(r"</think>", text, flags=re.I)[-1]
    # An unterminated <think> block (truncated output) contains no answer.
    text = re.sub(r"<think>.*\Z", "", text, flags=re.S | re.I)
    text = re.sub(r"```[a-zA-Z0-9_-]*", "", text)
    return text


def _balanced_objects(text):
    """Yield every balanced {...} substring that starts at a top level, in order."""
    i, n = 0, len(text)
    while i < n:
        start = text.find("{", i)
        if start < 0:
            return
        depth, in_str, esc = 0, False, False
        end = None
        for j in range(start, n):
            c = text[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = j
                    break
        if end is None:
            return
        yield text[start:end + 1]
        i = end + 1


def extract_json(output_text):
    """Return the first top-level JSON object in the output, or None."""
    text = _strip_reasoning(output_text or "")
    for cand in _balanced_objects(text):
        try:
            obj = json.loads(cand)
        except ValueError:
            # Tolerate trailing commas, a common small-model mistake.
            try:
                obj = json.loads(re.sub(r",\s*([}\]])", r"\1", cand))
            except ValueError:
                continue
        if isinstance(obj, dict):
            return obj
    return None


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------

def _norm_str(s):
    return unicodedata.normalize("NFKC", str(s)).strip().casefold()


def _to_number(v):
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        m = re.search(r"-?\d+(?:\.\d+)?", v.replace(",", "").replace(" ", "").replace(" ", ""))
        if m:
            return float(m.group(0))
    return None


def _matches(expected, got):
    if isinstance(expected, list):
        return any(_matches(e, got) for e in expected)
    if isinstance(expected, bool):
        return got is expected
    if isinstance(expected, (int, float)):
        g = _to_number(got)
        return g is not None and abs(g - float(expected)) <= NUM_TOL
    if expected is None:
        return got is None
    if got is None or isinstance(got, (dict, list)):
        return False
    return _norm_str(expected) == _norm_str(got)


def _benchmark_map(raw):
    """Accept [{"name","score"}, ...] or {"name": score, ...}; first occurrence wins."""
    out = {}
    if isinstance(raw, dict):
        items = list(raw.items())
    elif isinstance(raw, list):
        items = []
        for e in raw:
            if isinstance(e, dict) and "name" in e:
                items.append((e.get("name"), e.get("score")))
    else:
        items = []
    for name, val in items:
        if name is None:
            continue
        key = _norm_str(name)
        if key not in out:
            out[key] = val
    return out


def score(output_text, answer_key):
    fields = answer_key.get("fields", {})
    benches = answer_key.get("benchmarks", {})
    total = len(fields) + len(benches)
    obj = extract_json(output_text)
    details = []
    correct = 0

    if obj is None:
        for k, v in fields.items():
            details.append({"field": k, "expected": v, "got": None, "correct": False})
        for k, v in benches.items():
            details.append({"field": "benchmarks." + k, "expected": v, "got": None, "correct": False})
        return {"json_valid": False, "fields_correct": 0, "fields_total": total,
                "accuracy": 0.0, "details": details}

    lowered = {_norm_str(k): v for k, v in obj.items()}
    for k, expected in fields.items():
        got = obj.get(k, lowered.get(_norm_str(k)))
        ok = _matches(expected, got)
        correct += ok
        details.append({"field": k, "expected": expected, "got": got, "correct": ok})

    bmap = _benchmark_map(obj.get("benchmarks", lowered.get("benchmarks")))
    for name, expected in benches.items():
        got = bmap.get(_norm_str(name))
        ok = _matches(expected, got)
        correct += ok
        details.append({"field": "benchmarks." + name, "expected": expected, "got": got, "correct": ok})

    return {"json_valid": True, "fields_correct": correct, "fields_total": total,
            "accuracy": round(correct / total, 4) if total else 0.0, "details": details}


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

def _perfect_output(key):
    first = lambda v: v[0] if isinstance(v, list) else v  # noqa: E731
    obj = {k: first(v) for k, v in key["fields"].items()}
    obj["benchmarks"] = [{"name": n, "score": s} for n, s in key["benchmarks"].items()]
    return obj


def _self_test():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "answer_key.json"), encoding="utf-8") as fh:
        key = json.load(fh)
    n_total = len(key["fields"]) + len(key["benchmarks"])

    perfect = json.dumps(_perfect_output(key), ensure_ascii=False)
    r = score(perfect, key)
    assert r["json_valid"] and r["accuracy"] == 1.0, r
    print("perfect output:          accuracy %.3f (%d/%d)" % (r["accuracy"], r["fields_correct"], r["fields_total"]))

    wrapped = ("<think>The card says 14.8B parameters {not json}.</think>\nSure! Here it is:\n```json\n"
               + json.dumps(_perfect_output(key), ensure_ascii=False, indent=2) + "\n```\nHope this helps.")
    r = score(wrapped, key)
    assert r["accuracy"] == 1.0, r
    print("think + fenced output:   accuracy %.3f" % r["accuracy"])

    bad_obj = _perfect_output(key)
    bad_obj["params_b"] = "13.9B"                   # wrong (non-embedding count)
    bad_obj["context_window"] = 32768               # wrong (native length)
    bad_obj["license"] = " apache 2.0 "             # right (case/whitespace)
    bad_obj["benchmarks"][0]["score"] = 68.9        # wrong (preview checkpoint)
    bad_obj["benchmarks"][2]["score"] = "62.70%"    # right (string with %)
    bad_obj["benchmarks"] = bad_obj["benchmarks"][:-2]  # two benchmarks missing
    r = score(json.dumps(bad_obj, ensure_ascii=False) + ", trailing text", key)
    assert r["json_valid"] and r["fields_correct"] == n_total - 5, r
    print("partly wrong output:     accuracy %.3f (%d/%d)" % (r["accuracy"], r["fields_correct"], r["fields_total"]))

    r = score("I could not find the model on these pages.", key)
    assert not r["json_valid"] and r["accuracy"] == 0.0, r
    print("no JSON:                 accuracy %.3f json_valid=%s" % (r["accuracy"], r["json_valid"]))

    r = score("<think>still thinking about {\"model_name\": ", key)
    assert not r["json_valid"], r
    print("truncated reasoning:     json_valid=%s" % r["json_valid"])
    print("self-test OK")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        with open(sys.argv[1], encoding="utf-8") as fh:
            out = fh.read()
        with open(sys.argv[2], encoding="utf-8") as fh:
            ak = json.load(fh)
        print(json.dumps(score(out, ak), indent=2, ensure_ascii=False))
    else:
        _self_test()
