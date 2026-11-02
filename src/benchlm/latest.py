"""`bench export --latest`: the latest complete run per (model, machine) as a compact Markdown + JSON digest.

Meant to be read by people or other AI conversations choosing a model; refreshed with the dashboard copy.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import db as dbm
from .config import DATA_DIR

LATEST_DIR = DATA_DIR / "latest"

INTRO = """# Local LLM benchmarks: latest results

Generated {generated} by `./bench export --latest` (refreshed after every run, merge and recompute).
One row per model and machine, from its most recent complete run. Older runs are left out.

What these numbers are:
- **Measured on this machine:** speed, memory and simple correctness checks. They show how fast and how
  reliably a model runs locally. They do not measure how intelligent it is.
- **Public scores** (bottom section) come from model cards and Artificial Analysis. They were not measured here.
- `off` = reasoning off, `high` = reasoning/thinking on at high effort.
- Short chat: about 100-token prompt. Long context: a ~{long_k}k-token document, then questions about its start,
  middle and end ("recall" 1.0 = all found). Extraction: JSON field extraction, accuracy 0-1.
- First visible (s): time until the first answer text appears, after any hidden thinking.
- Peak memory: highest memory the engine used during the run (machine RAM is in the machine line).
- `benchmarks-latest.json` has every metric for each row, plus the full public score list.
"""


def _f(v, digits=1):
    if v is None or v == "":
        return "–"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, (int, float)):
        return f"{v:.{digits}f}" if isinstance(v, float) else str(v)
    return str(v)


def latest_rows(db: dict) -> list:
    view = dbm.merged_view(db)
    best = {}
    for r in view["runs"]:
        if r.get("status") != "complete" or r.get("subset") or not r.get("model_uid"):
            continue
        k = (r["model_uid"], r["machine_id"])
        if k not in best or r["started_at"] > best[k]["started_at"]:
            best[k] = r
    rows = []
    for (uid, mid), r in best.items():
        m = view["models"].get(uid, {})
        mach = view["machines"].get(mid, {})
        pub = (view.get("public") or {}).get(uid) or {}
        caps = m.get("capabilities") or {}
        rows.append({
            "model_uid": uid,
            "display_name": m.get("display_name") or m.get("key") or uid,
            "engine": m.get("engine"),
            "format": m.get("format"),
            "quantization": (m.get("quantization") or {}).get("name"),
            "size_gb": round(m["size_bytes"] / 1e9, 1) if m.get("size_bytes") else None,
            "params_total_b": m.get("params_total_b"),
            "params_active_b": m.get("params_active_b"),
            "is_moe": m.get("is_moe"),
            "max_context_length": m.get("max_context_length"),
            "tool_use": caps.get("tool_use"),
            "vision": caps.get("vision"),
            "reasoning": bool(caps.get("reasoning")),
            "also_listed_as": m.get("aliases") or [],
            "source": m.get("source"),      # the exact download: Hugging Face repo (+ GGUF file) or Ollama tag
            "machine_id": mid,
            "machine": mach.get("label") or mid,
            "machine_memory_gb": round(mach["memory_bytes"] / 2**30) if mach.get("memory_bytes") else None,
            "tested_at": r["started_at"],
            "engine_info": r.get("engine_info"),
            "warnings": r.get("warnings") or [],
            "summary": r.get("summary") or {},
            "public": {
                "license": pub.get("license"),
                "release_date": pub.get("release_date"),
                "benchmarks": [
                    {k: b.get(k) for k in ("name", "category", "score", "unit", "effort", "source_url")}
                    for b in pub.get("benchmarks") or []
                ],
            },
        })
    rows.sort(key=lambda x: (x["machine"], x["display_name"].lower(), x["engine"] or "", x["model_uid"]))
    return rows


def _speed_table(rows: list) -> list:
    out = [
        "| Model | Engine | Format | Size GB | Params (active) | Tools | Short decode tok/s off / high | "
        "First visible s off / high | Long prefill tok/s | Long decode tok/s | Long recall off / high | "
        "Extraction off / high | Peak mem GB | Swap GB | Tested |",
        "|" + "---|" * 15,
    ]
    for x in rows:
        s = x["summary"]
        params = _f(x["params_total_b"], 0) + "B"
        if x["is_moe"] and x["params_active_b"]:
            params += f" ({_f(x['params_active_b'])}B)"
        out.append("| " + " | ".join([
            x["display_name"], x["engine"] or "–", f"{x['format'] or '–'} {x['quantization'] or ''}".strip(),
            _f(x["size_gb"]), params, _f(x["tool_use"]),
            f"{_f(s.get('short_off_decode_tps'), 0)} / {_f(s.get('short_high_decode_tps'), 0)}",
            f"{_f(s.get('short_off_first_visible_s'))} / {_f(s.get('short_high_first_visible_s'))}",
            _f(s.get("long_off_prefill_tps"), 0), _f(s.get("long_off_decode_tps"), 0),
            f"{_f(s.get('long_off_recall'), 2)} / {_f(s.get('long_high_recall'), 2)}",
            f"{_f(s.get('extraction_off_accuracy'), 2)} / {_f(s.get('extraction_high_accuracy'), 2)}",
            _f(s.get("mem_peak_gb")), _f(s.get("swap_growth_gb")), x["tested_at"][:10],
        ]) + " |")
    return out


def render_markdown(rows: list) -> str:
    long_tokens = next((x["summary"].get("long_off_prompt_tokens") for x in rows
                        if x["summary"].get("long_off_prompt_tokens")), 64000)
    parts = [INTRO.format(generated=dbm.now_iso(), long_k=round(long_tokens / 1000))]
    for mach in sorted({x["machine"] for x in rows}):
        group = [x for x in rows if x["machine"] == mach]
        mem = group[0]["machine_memory_gb"]
        parts.append(f"\n## Measured on {mach}" + (f" ({mem} GB RAM)" if mem else "") + "\n")
        parts.extend(_speed_table(group))
        srcs = [(x["display_name"], x["engine"], x["source"]) for x in group if x.get("source")]
        if srcs:
            parts.append("\nExact files tested (to download the same one elsewhere):")
            parts.extend(f"- {n} ({e}): {s['repo']}" + (f" / {s['file']}" if s.get("file") else "") + f" <{s['url']}>"
                         for n, e, s in srcs)
        notes = [(x["display_name"], x["engine"], w) for x in group for w in x["warnings"]]
        if notes:
            parts.append("\nWarnings from these runs:")
            parts.extend(f"- {n} ({e}): {w}" for n, e, w in notes)
    parts.append("\n## Public scores (not measured here)\n")
    seen = set()
    for x in rows:
        name = x["display_name"]
        bench = x["public"]["benchmarks"]
        if not bench or name in seen:
            continue
        seen.add(name)
        items = []
        for b in sorted(bench, key=lambda b: (b["category"] or "", b["name"] or "")):
            effort = f", {b['effort']}" if b.get("effort") else ""
            items.append(f"{b['name']} {_f(b['score'])}{b.get('unit') or ''} ({b['category']}{effort})")
        parts.append(f"- **{name}**: " + "; ".join(items))
    return "\n".join(parts) + "\n"


def write_latest(out: Path = LATEST_DIR, db: dict = None) -> Path:
    db = db if db is not None else dbm.load()
    rows = latest_rows(db)
    out.mkdir(parents=True, exist_ok=True)
    (out / "benchmarks-latest.md").write_text(render_markdown(rows), encoding="utf-8")
    with open(out / "benchmarks-latest.json", "w", encoding="utf-8") as f:
        json.dump({"generated_at": dbm.now_iso(), "rows": rows}, f, indent=1, ensure_ascii=False)
    return out / "benchmarks-latest.md"
