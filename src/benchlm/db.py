"""JSON database (data/results.json): load, atomic save, upserts, summaries."""
from __future__ import annotations

import json
import os
import statistics
from datetime import datetime, timezone
from typing import List, Optional

from . import SCHEMA_VERSION, VERSION, answers
from .config import DB_PATH, OVERRIDES_PATH, RAW_DIR, ensure_dirs


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def agg(values) -> Optional[dict]:
    vals = [v for v in values if isinstance(v, (int, float))]
    if not vals:
        return None
    return {"median": round(statistics.median(vals), 4), "min": round(min(vals), 4),
            "max": round(max(vals), 4), "n": len(vals)}


def med(d) -> Optional[float]:
    return d.get("median") if isinstance(d, dict) else None


def empty_db() -> dict:
    return {"schema_version": SCHEMA_VERSION, "tool_version": VERSION, "updated_at": now_iso(),
            "machines": {}, "models": {}, "runs": [], "public": {}}


def load() -> dict:
    if not DB_PATH.exists():
        return empty_db()
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    for k, v in empty_db().items():
        db.setdefault(k, v)
    return db


def save(db: dict) -> None:
    ensure_dirs()
    db["updated_at"] = now_iso()
    db["tool_version"] = VERSION
    tmp = DB_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, DB_PATH)


def save_raw(run_id: str, raw: dict) -> str:
    ensure_dirs()
    path = RAW_DIR / f"{run_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False)
    return f"raw/{run_id}.json"


def upsert_machine(db: dict, machine: dict) -> None:
    existing = db["machines"].get(machine["machine_id"], {})
    extra = existing.get("specs_extra") or {}
    merged = dict(existing)
    merged.update(machine)
    merged["specs_extra"] = {**(machine.get("specs_extra") or {}), **extra}
    db["machines"][machine["machine_id"]] = merged


def upsert_model(db: dict, model: dict) -> None:
    clean = {k: v for k, v in model.items() if not k.startswith("_")}
    existing = db["models"].get(clean["model_uid"])
    clean["first_seen"] = existing.get("first_seen") if existing else now_iso()
    clean["last_seen"] = now_iso()
    apply_moe(clean, (db.get("public") or {}).get(clean["model_uid"]))
    db["models"][clean["model_uid"]] = clean


# Where params_active_b came from, most trusted first.
ACTIVE_SOURCES = ["name", "model card", "estimated from config.json", "estimated from GGUF metadata"]


def apply_moe(model: dict, public: Optional[dict]) -> None:
    """Complete a model's MoE fields from its public record (Hugging Face config.json / model card). A value from
    the model's own name is kept; a card value replaces an estimate. data/overrides.json still wins on top."""
    moe = (public or {}).get("moe") or {}
    if not moe.get("experts"):
        return
    model["is_moe"] = True
    model["moe_experts"] = model.get("moe_experts") or moe.get("experts")
    model["moe_experts_per_token"] = model.get("moe_experts_per_token") or moe.get("experts_per_token")
    new = moe.get("params_active_b")
    if new is None:
        return
    rank = lambda s: ACTIVE_SOURCES.index(s) if s in ACTIVE_SOURCES else len(ACTIVE_SOURCES)
    if model.get("params_active_b") is None or rank(moe.get("active_source")) < rank(model.get("params_active_source")):
        model["params_active_b"] = new
        model["params_active_source"] = moe.get("active_source")


def runs_for(db: dict, model_uid: str, machine_id: Optional[str] = None) -> List[dict]:
    return [r for r in db["runs"] if r["model_uid"] == model_uid and
            (machine_id is None or r["machine_id"] == machine_id)]


def equivalent_uids(db: dict, model: dict) -> List[str]:
    """Other model_uids that are the same file under another name.

    LM Studio renames variants as you add or remove downloads (e.g. `@mlx-mxfp4` becomes `@mxfp4`
    once the GGUF variant is deleted), so the same file is recognised by engine + key + format +
    quantization + exact size instead of by name."""
    q = (model.get("quantization") or {}).get("name")
    out = []
    for uid, m in db.get("models", {}).items():
        if uid == model["model_uid"]:
            continue
        if (m.get("engine") == model.get("engine") and m.get("key") == model.get("key")
                and str(m.get("format")) == str(model.get("format"))
                and (m.get("quantization") or {}).get("name") == q
                and m.get("size_bytes") and m.get("size_bytes") == model.get("size_bytes")):
            out.append(uid)
    return out


def equivalent_done(db: dict, model: dict, machine_id: str, profile: dict, suite_version: str) -> Optional[str]:
    """The renamed uid under which this exact file was already fully benchmarked, if any."""
    for uid in equivalent_uids(db, model):
        for r in runs_for(db, uid, machine_id):
            if (r.get("status") == "complete" and not r.get("subset") and r.get("suite_version") == suite_version
                    and r.get("profile_hash") == profile["hash"]):
                return uid
    return None


def status_for(db: dict, model: dict, machine_id: str, profile: dict, suite_version: str) -> str:
    """'done' | 'new' | 'stale' (suite/profile changed or model re-downloaded) | 'partial'."""
    runs = [r for r in runs_for(db, model["model_uid"], machine_id) if not r.get("subset")]
    complete = [r for r in runs if r.get("status") == "complete"]
    if not complete:
        if equivalent_done(db, model, machine_id, profile, suite_version):
            return "done"
        return "partial" if runs else "new"
    for r in complete:
        if (r.get("suite_version") == suite_version and r.get("profile_hash") == profile["hash"]
                and r.get("model_fingerprint", model.get("fingerprint")) == model.get("fingerprint")):
            return "done"
    return "stale"


def add_run(db: dict, run: dict) -> None:
    db["runs"] = [r for r in db["runs"] if r["run_id"] != run["run_id"]]
    db["runs"].append(run)


def load_overrides() -> dict:
    if not OVERRIDES_PATH.exists():
        return {}
    try:
        with open(OVERRIDES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        print(f"! overrides.json ignored: {e}")
        return {}


def merged_view(db: dict) -> dict:
    """Database with data/overrides.json applied (used by the dashboard).

    overrides.json format:
      {"public": {"<model_uid>": {"benchmarks": [{name, category, score, unit, source_url}], "license": "..."}},
       "machines": {"<machine_id>": {"specs_extra": {...}}},
       "models": {"<model_uid>": {"display_name": "..."}}}
    Manual benchmarks replace automatic ones with the same name.
    Renamed copies of the same file are shown as one model (see collapse_renamed).
    """
    ov = load_overrides()
    out = json.loads(json.dumps(db))
    for section in ("machines", "models"):
        for k, patch in (ov.get(section) or {}).items():
            if k in out[section]:
                for pk, pv in patch.items():
                    if isinstance(pv, dict) and isinstance(out[section][k].get(pk), dict):
                        out[section][k][pk].update(pv)
                    else:
                        out[section][k][pk] = pv
    for uid, patch in (ov.get("public") or {}).items():
        pub = out["public"].setdefault(uid, {"benchmarks": []})
        for pk, pv in patch.items():
            if pk == "benchmarks":
                names = {b["name"].lower() for b in pv}
                pub["benchmarks"] = [b for b in pub.get("benchmarks", []) if b["name"].lower() not in names]
                for b in pv:
                    b = dict(b)
                    b.setdefault("method", "manual")
                    b.setdefault("applies_to", "base")
                    pub["benchmarks"].append(b)
            else:
                pub[pk] = pv
    return collapse_renamed(out)


def collapse_renamed(db: dict) -> dict:
    """Merge models that are the same file under different names (see equivalent_uids), in place.

    The name with the newest run wins; the other names' runs move to it (keeping `listed_as`),
    so the dashboard shows only the latest run per machine and keeps the rest as history.
    Runs on different machines stay apart because rows are per (model, machine)."""
    models = db.get("models") or {}
    last = {}
    for r in db.get("runs") or []:
        uid = r.get("model_uid")
        last[uid] = max(last.get(uid, ""), r.get("started_at") or "")
    aliases = {}
    for uid in sorted(models):
        if uid in aliases:
            continue
        group = [uid] + [u for u in equivalent_uids(db, models[uid]) if u not in aliases]
        if len(group) < 2:
            continue
        keep = max(group, key=lambda u: (last.get(u, ""), models[u].get("last_seen") or "", u))
        for u in group:
            if u != keep:
                aliases[u] = keep
    if not aliases:
        return db
    pub = db.setdefault("public", {})
    for old, keep in aliases.items():
        m, k = models.pop(old), models[keep]
        k.setdefault("aliases", []).append(old)
        if (m.get("first_seen") or "~") < (k.get("first_seen") or "~"):
            k["first_seen"] = m["first_seen"]
        if old in pub:
            p = pub.pop(old)
            if keep not in pub:
                pub[keep] = p
    for r in db.get("runs") or []:
        if r.get("model_uid") in aliases:
            r["listed_as"] = r["model_uid"]
            r["model_uid"] = aliases[r["model_uid"]]
    db["aliases"] = aliases
    return db


# ---------------------------------------------------------------- summaries
def summarize(run: dict) -> dict:
    T = run.get("tests") or {}
    s = {}

    def turn(test, mode, idx):
        tr = ((T.get(test) or {}).get(mode) or {})
        turns = tr.get("turns") or []
        return turns[idx] if len(turns) > idx else {}

    def mean_med(test, mode, key, start=0):
        tr = ((T.get(test) or {}).get(mode) or {})
        vals = [med(t.get(key)) for t in (tr.get("turns") or [])[start:]]
        vals = [v for v in vals if v is not None]
        return round(statistics.mean(vals), 3) if vals else None

    for mode in ("off", "high"):
        tr = (T.get("short") or {}).get(mode) or {}
        if tr.get("turns"):
            s[f"short_{mode}_ttft_s"] = mean_med("short", mode, "ttft_s")
            s[f"short_{mode}_first_visible_s"] = mean_med("short", mode, "first_visible_s")
            s[f"short_{mode}_decode_tps"] = mean_med("short", mode, "decode_tps")
            s[f"short_{mode}_prefill_tps"] = med(turn("short", mode, 0).get("prefill_tps"))
            s[f"short_{mode}_reasoning_tokens"] = sum((t.get("reasoning_tokens") or 0) for t in tr["turns"])
            s[f"short_{mode}_total_s"] = (tr.get("totals") or {}).get("conversation_s")
        tr = (T.get("long") or {}).get(mode) or {}
        if tr.get("turns"):
            t1 = turn("long", mode, 0)
            s[f"long_{mode}_prompt_tokens"] = t1.get("prompt_tokens")
            s[f"long_{mode}_ttft_s"] = med(t1.get("ttft_s"))
            s[f"long_{mode}_first_visible_s"] = med(t1.get("first_visible_s"))
            s[f"long_{mode}_prefill_tps"] = med(t1.get("prefill_tps"))
            s[f"long_{mode}_decode_tps"] = mean_med("long", mode, "decode_tps")
            s[f"long_{mode}_followup_ttft_s"] = mean_med("long", mode, "ttft_s", start=1)
            q = tr.get("quality") or {}
            s[f"long_{mode}_recall"] = q.get("recall")
            s[f"long_{mode}_cache_hit_ttft_s"] = tr.get("cache_hit_ttft_s")
            # per-section recall and the secondary score on the reasoning text: None for runs recorded before
            # answers were kept (not available)
            for sec in ("start", "middle", "end"):
                s[f"long_{mode}_recall_{sec}"] = (q.get("recall_by_section") or {}).get(sec)
            s[f"long_{mode}_recall_reasoning"] = q.get("recall_reasoning")
        tr = (T.get("extraction") or {}).get(mode) or {}
        if tr.get("turns"):
            t1 = turn("extraction", mode, 0)
            s[f"extraction_{mode}_total_s"] = med(t1.get("total_s"))
            s[f"extraction_{mode}_decode_tps"] = med(t1.get("decode_tps"))
            q = tr.get("quality") or {}
            s[f"extraction_{mode}_accuracy"] = q.get("accuracy")
            s[f"extraction_{mode}_json_valid"] = q.get("json_valid")
            s[f"extraction_{mode}_accuracy_reasoning"] = q.get("accuracy_reasoning")
    for test in ("short", "extraction", "long"):
        for mode in ("off", "high"):
            tr = (T.get(test) or {}).get(mode) or {}
            if tr.get("turns"):
                s[f"{test}_{mode}_truncated_turns"] = tr.get("truncated_turns", 0)
                # answers written only in the reasoning channel (None: not checked, e.g. no raw file)
                s[f"{test}_{mode}_answer_in_reasoning_turns"] = tr.get("answer_in_reasoning_turns")
                # scored answers that never arrived: thinking used the whole output budget (None: not checked)
                s[f"{test}_{mode}_no_answer_scored"], s[f"{test}_{mode}_scored_answers"] = answers.no_answer_scored(test, tr)
    cs = run.get("cold_start") or {}
    cyc = cs.get("cycles") or []
    if cyc:
        s["cold_load_s"] = cyc[0].get("load_time_s")
        s["cold_first_ttft_s"] = cyc[0].get("first_ttft_s")
        if len(cyc) > 1:
            s["warm_load_s"] = cyc[1].get("load_time_s")
            s["reload_first_ttft_s"] = cyc[1].get("first_ttft_s")
    s["warm_ttft_s"] = cs.get("warm_ttft_s")
    mem = run.get("memory") or {}
    snaps = mem.get("snapshots") or {}
    gb = lambda b: round(b / 1024 ** 3, 2) if b else None
    s["mem_idle_gb"] = gb(snaps.get("idle"))
    s["mem_loaded_gb"] = gb(snaps.get("loaded_empty"))
    s["mem_long_gb"] = gb(snaps.get("after_long_prompt"))
    s["mem_peak_gb"] = gb(mem.get("peak_bytes"))
    if snaps.get("idle") and snaps.get("loaded_empty"):
        s["mem_model_gb"] = gb(snaps["loaded_empty"] - snaps["idle"])
    if snaps.get("loaded_empty") and snaps.get("after_long_prompt"):
        s["mem_kv_long_gb"] = gb(snaps["after_long_prompt"] - snaps["loaded_empty"])
    ca = mem.get("context_analysis") or {}
    s["peak_context_tokens"] = ca.get("peak_context_tokens")
    s["peak_phase"] = ca.get("peak_phase")
    s["long_context_tokens"] = ca.get("long_context_tokens")
    s["mem_long_peak_gb"] = gb(ca.get("long_peak_bytes"))
    s["mem_other_peak_gb"] = gb(ca.get("other_peak_bytes"))
    swap = mem.get("swap_used_delta_bytes")
    s["swap_growth_gb"] = round(swap / 1024 ** 3, 2) if isinstance(swap, (int, float)) else None
    return s


SWAP_WARNING_PREFIX = "swap grew by "


def swap_warning(run: dict, threshold_gb: float) -> Optional[str]:
    swap = (run.get("memory") or {}).get("swap_used_delta_bytes")
    if not isinstance(swap, (int, float)) or swap <= threshold_gb * 1024 ** 3:
        return None
    return (f"{SWAP_WARNING_PREFIX}{swap / 1024 ** 3:.1f} GB during the run (more than {threshold_gb:g} GB): memory ran "
            f"short, so speeds may be lower than usual and not comparable")


def set_swap_warning(run: dict, threshold_gb: float) -> None:
    """(Re)apply the swap warning with the current threshold. Idempotent."""
    ws = [w for w in run.get("warnings") or [] if not w.startswith(SWAP_WARNING_PREFIX)]
    w = swap_warning(run, threshold_gb)
    run["warnings"] = ws + ([w] if w else [])
