"""How much context was in use when memory peaked, and the inputs for a "safe max context" estimate.

Memory during a run has three parts: the weights (≈ loaded − idle), the context itself (KV cache, grows
with tokens) and a temporary working-memory spike while a long prompt is being read. The long-context
test gives one well-defined point (document tokens, peak memory while handling it); peaks outside that
test don't grow with context and act as a floor."""
from __future__ import annotations

from typing import Optional


def _turn_tokens(run: dict, test: str, field: str = "prompt_tokens") -> Optional[int]:
    vals = []
    for mode in ((run.get("tests") or {}).get(test) or {}).values():
        for t in (mode or {}).get("turns") or []:
            v = t.get(field)
            if isinstance(v, (int, float)):
                vals.append(v)
    return int(max(vals)) if vals else None


def _tokens_for_phase(run: dict, phase: str, detail: Optional[str]) -> Optional[int]:
    """Fallback for runs recorded before requests were timestamped."""
    if phase == "long":
        return _turn_tokens(run, "long")
    if phase in ("short", "cold_start", "warmup"):
        return _turn_tokens(run, "short")
    if phase == "extraction":
        if detail == "live" or phase == "live-extract":
            return (run.get("live_extraction") or {}).get("prompt_tokens") or _turn_tokens(run, "extraction")
        return _turn_tokens(run, "extraction")
    if phase == "live-extract":
        return (run.get("live_extraction") or {}).get("prompt_tokens")
    if phase in ("idle", "load", "loaded", "unload"):
        return 0
    return None


def analyze(run: dict, raw: dict) -> dict:
    # Samples and requests discarded because another model was loaded never count.
    timeline = [s for s in (raw or {}).get("memory_timeline") or [] if s.get("engine_bytes") and not s.get("discarded")]
    if not timeline:
        return {}
    requests = [r for r in (raw or {}).get("requests") or []
                if r.get("t_start") is not None and not r.get("discarded")]

    def tokens_at(sample) -> Optional[int]:
        t = sample.get("t")
        for r in requests:   # exact: the request running at that moment
            if r["t_start"] <= t <= (r.get("t_end") or r["t_start"]):
                n = r.get("prompt_tokens") or 0
                if sample.get("detail") == "decode":
                    n += r.get("completion_tokens") or 0
                return int(n)
        return _tokens_for_phase(run, sample.get("phase") or "", sample.get("detail"))

    peak = max(timeline, key=lambda s: s["engine_bytes"])
    long_samples = [s for s in timeline if s.get("phase") == "long"]
    # Peaks that don't depend on context length: only samples *before* the long test, because some engines
    # keep the long document's memory afterwards (which would otherwise look like a context-independent floor).
    first_long = next((i for i, s in enumerate(timeline) if s.get("phase") == "long"), len(timeline))
    other = timeline[:first_long]
    return {
        "peak_context_tokens": tokens_at(peak),
        "peak_phase": (peak.get("phase") or "") + ("/" + peak["detail"] if peak.get("detail") else ""),
        "long_peak_bytes": max(s["engine_bytes"] for s in long_samples) if long_samples else None,
        "long_context_tokens": _turn_tokens(run, "long"),
        "other_peak_bytes": max(s["engine_bytes"] for s in other) if other else None,
        "exact": bool(requests),
    }
