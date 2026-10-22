"""`bench enrich`: collect public model info + benchmark scores (no cloud LLM)."""
from __future__ import annotations

import json
import re
import time
from typing import List, Optional

from ..db import now_iso
from . import sources
from .benchnames import canonical
from .cardparse import extract_benchmarks, extract_facts

METHOD_RANK = {"manual": 0, "card-table": 1, "model-index": 2, "leaderboard": 3, "api": 4, "card-link": 5, "web": 6}


def _norm_entry(b: dict, method: str, url: str, applies_to: str) -> dict:
    name, cat = canonical(b.get("raw_name") or b.get("name") or "")
    return {"name": name or b.get("name") or b.get("raw_name"), "raw_name": b.get("raw_name") or b.get("name"),
            "category": b.get("category") if b.get("category") not in (None, "other") else cat,
            "score": b.get("score"), "unit": b.get("unit", ""), "applies_to": applies_to, "method": method,
            "source_url": b.get("source_url") or url, "source_column": b.get("column"),
            # reasoning effort the source ran it at; effort_end "max"/"min" when the source has several efforts
            # (both ends are kept; "max" is the one used for category scores and comparisons)
            "effort": b.get("effort") or None, "effort_end": b.get("effort_end"),
            "retrieved_at": now_iso()}


def _merge(benchmarks: List[dict]) -> List[dict]:
    best = {}
    for b in benchmarks:
        if b.get("score") is None:
            continue
        k = (b["name"].lower(), b.get("effort_end") == "min")   # the low-effort score is kept beside the main one
        if k not in best or METHOD_RANK.get(b["method"], 9) < METHOD_RANK.get(best[k]["method"], 9):
            best[k] = b
    # A benchmark that only has a low-effort score (e.g. listed only for the non-reasoning variant) keeps it as
    # its main score, so it still counts in the category scores.
    # A low-effort score is only shown beside a main score from the same source (efforts of different sources
    # aren't comparable); without a main score it becomes the main one.
    main = {k[0]: b for k, b in best.items() if not k[1]}
    for (name, low), b in list(best.items()):
        if not low:
            continue
        if name not in main:
            b["effort_end"] = None
        elif main[name]["method"] != b["method"]:
            del best[(name, low)]
    return sorted(best.values(), key=lambda b: (b["category"], b["name"], b.get("effort_end") == "min"))


def enrich_model(model: dict, secrets, refresh: bool = False, web: bool = True, verbose: bool = True) -> dict:
    """Returns a 'public' record (see docs/SCHEMA.md) plus '_pages' (texts kept for LLM extraction)."""
    hf_token = secrets.get("huggingface", "token")
    pub = {"benchmarks": [], "links": [], "updated_at": now_iso(), "sources_tried": []}
    pages = []
    names = sources.search_names(model)
    found = sources.find_hf_repo(model, hf_token, refresh)
    if verbose:
        print(f"    • Hugging Face: {found['repo'] if found else 'no matching repo found'}")
    collected = []
    if found:
        repo = found["repo"]
        pub["hf_repo"] = repo
        pub["hf_candidates"] = found["candidates"]
        try:
            info = sources.hf_model_info(repo, hf_token, refresh)
        except Exception as e:
            info = {}
            pub["sources_tried"].append(f"hf-info error: {e}")
        card = info.get("cardData") or {}
        base = card.get("base_model")
        pub["base_model"] = base[0] if isinstance(base, list) and base else base
        pub["license"] = card.get("license") or next((t[8:] for t in info.get("tags", []) if t.startswith("license:")), None)
        pub["release_date"] = (info.get("createdAt") or "")[:10] or None
        st = (info.get("safetensors") or {}).get("total")
        pub["params_b"] = round(st / 1e9, 2) if st else model.get("params_total_b")
        pub["pipeline_tag"] = info.get("pipeline_tag")
        pub["modalities"] = ["text"] + (["image"] if (model.get("capabilities") or {}).get("vision") or
                                        "image" in (info.get("pipeline_tag") or "") else [])
        pub["downloads"] = info.get("downloads")
        pub["likes"] = info.get("likes")
        url = f"https://huggingface.co/{repo}"
        pub["links"].append({"label": "Hugging Face model card", "url": url})
        readme = sources.hf_readme(repo, hf_token, refresh)
        if readme:
            pages.append({"url": url, "text": readme})
            card_names = names + [repo.split("/")[-1], model.get("display_name") or ""]
            for b in extract_benchmarks(readme, card_names):
                collected.append(_norm_entry(b, "card-table", url, "base"))
            facts = extract_facts(readme)
            if facts.get("context_window"):
                pub["context_window"] = facts["context_window"]
        # Mixture of experts: config.json gives experts / experts per token; the card may state active params.
        moe = sources.moe_from_config(sources.hf_config(repo, hf_token, refresh), pub.get("params_b"))
        if moe:
            card_active = sources.active_from_card(readme, pub.get("params_b"))
            if card_active is not None:
                moe["params_active_b"], moe["active_source"] = card_active, "model card"
            moe["source_url"] = f"https://huggingface.co/{repo}/blob/main/config.json"
            pub["moe"] = moe
        for b in sources.model_index_results(info):
            collected.append(_norm_entry(b, "model-index", url, "base"))
        disp = (model.get("display_name") or "").split(":")[0]
        pub["family"] = re.sub(r"[-_ ]?\d+(\.\d+)?[bB].*$", "", disp).strip(" -_:") or None
        # pages linked from the card (official blog / tech report / GitHub) often carry the score tables
        if readme and len([b for b in collected if b["category"] != "other"]) < 6:
            for u in sources.card_links(readme):
                raw = sources.fetch_page(u)
                if not raw:
                    continue
                pages.append({"url": u, "text": raw})
                n0 = len(collected)
                for b in extract_benchmarks(raw, card_names):
                    if b.get("known"):
                        collected.append(_norm_entry(b, "card-link", u, "base"))
                if len(collected) > n0:
                    pub["links"].append({"label": u.split("/")[2], "url": u})
            pub["sources_tried"].append("card links")
    try:
        ep = sources.epoch_benchmarks(model, refresh)
    except Exception as e:
        ep = []
        pub["sources_tried"].append(f"epoch error: {e}")
    pub["sources_tried"].append(f"epoch-ai: {len(ep)} values")
    for b in ep:
        e = _norm_entry(b, "leaderboard", b["source_url"], "base")
        e["source_column"] = b.get("column")
        e["note"] = f"Epoch AI, reasoning effort: {b.get('effort') or 'default'}"
        collected.append(e)
    if ep:
        pub["links"].append({"label": "Epoch AI benchmarking hub (CC-BY)", "url": "https://epoch.ai/benchmarks"})
    aa_key = secrets.get("artificial_analysis", "api_key")
    if aa_key:
        aa = sources.artificial_analysis(model, aa_key)
        pub["sources_tried"].append(f"artificial-analysis: {len(aa)} values")
        if aa:   # the free API requires attribution wherever its data is shown
            pub["links"].append({"label": "Artificial Analysis (data source)", "url": "https://artificialanalysis.ai/"})
        for b in aa:
            collected.append(_norm_entry(b, "api", b.get("source_url"), "base"))
    if web and len([b for b in collected if b["category"] != "other"]) < 6:
        q = f"{names[0]} benchmark results GPQA MMLU-Pro LiveCodeBench"
        urls = [u for u in sources.search(q, secrets) if sources.trusted(u)][:4]
        pub["sources_tried"].append(f"web search: {len(urls)} trusted results")
        for u in urls:
            raw = sources.fetch_page(u)
            if not raw:
                continue
            pages.append({"url": u, "text": raw})
            for b in extract_benchmarks(raw, names):
                if b.get("known"):
                    collected.append(_norm_entry(b, "web", u, "base"))
            pub["links"].append({"label": u.split("/")[2], "url": u})
    pub["benchmarks"] = _merge(collected)
    efforts = {}
    for b in pub["benchmarks"]:
        if b.get("effort"):
            efforts.setdefault(b["method"], set()).add(b["effort"])
    # which reasoning efforts each source's scores were measured at (e.g. {"api": ["low", "high"]})
    pub["efforts"] = {k: sorted(v, key=lambda e: sources.EFFORT_LEVEL.get(e, 3)) for k, v in efforts.items()}
    pub["_pages"] = pages
    if verbose:
        cats = {}
        for b in pub["benchmarks"]:
            cats[b["category"]] = cats.get(b["category"], 0) + 1
        print(f"    • public benchmarks: {len(pub['benchmarks'])} " +
              (f"({', '.join(f'{k} {v}' for k, v in sorted(cats.items()))})" if cats else ""))
    return pub


# ---------------------------------------------------------------- live extraction by the tested model
EXTRACT_SYSTEM = "You are a precise data extraction engine. Output only JSON."
EXTRACT_PROMPT = """Extract metadata and benchmark scores for the model "{name}" from the web page below.
Use only values stated for this exact model (ignore other models' columns). If a value is not present, use null.
Return JSON matching this schema:
{{"model_name": string, "params_b": number, "context_window": integer, "license": string,
  "benchmarks": [{{"name": string, "score": number}}]}}
Use the benchmark names as written on the page. Scores are plain numbers without "%".
Output only the JSON object, with no explanation and no Markdown.

=== PAGE ({url}) ===
{page}"""


def _first_json(text: str):
    t = re.sub(r"(?is)<think>.*?</think>", "", text or "")
    t = re.sub(r"```(?:json)?", "", t)
    start = t.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(t)):
            c = t[i]
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
                    try:
                        return json.loads(t[start:i + 1])
                    except ValueError:
                        break
        start = t.find("{", start + 1)
    return None


def _focus(text: str, limit: int) -> str:
    """Keep the parts of a page around benchmark tables, up to `limit` characters."""
    clean = sources.html_to_text(text, limit=10 ** 7) if "<" in text else text
    if len(clean) <= limit:
        return clean
    idx = [m.start() for m in re.finditer(r"(?i)benchmark|evaluation|gpqa|mmlu|livecodebench|swe-bench", clean)]
    if not idx:
        return clean[:limit]
    start = max(0, idx[0] - 2000)
    return clean[start:start + limit]


def make_live_extractor(db: dict, public_record: Optional[dict], page_limit: int = 24000):
    """Returns a callback for ModelRunner: the model under test extracts its own public data."""

    def run(runner):
        if not public_record or not public_record.get("_pages"):
            return
        kw = re.compile(r"(?i)gpqa|mmlu|livecodebench|swe-bench|aime|bfcl|tau2|τ²|ifeval|mmmu|hle|benchmark")
        page = max(public_record["_pages"], key=lambda p: len(kw.findall(p["text"][:200000])))
        m = runner.model
        prompt = EXTRACT_PROMPT.format(name=m.get("display_name") or m["key"], url=page["url"],
                                       page=_focus(page["text"], page_limit))
        reasoning = runner._resolve("off")
        if reasoning == "__unsupported__":
            reasoning = None
        thinking = reasoning not in (None, False, "off")
        t0 = time.perf_counter()
        t = runner._chat(EXTRACT_SYSTEM, prompt, None, reasoning,
                         2000 + (runner.thinking_budget("live_extract") if thinking else 0),
                         "live-extract")
        data = _first_json(t.text)
        result = {"source_url": page["url"], "ttft_s": t.ttft_s, "total_s": round(time.perf_counter() - t0, 3),
                  "prompt_tokens": t.prompt_tokens, "completion_tokens": t.completion_tokens,
                  "decode_tps": t.decode_tps, "json_valid": isinstance(data, dict), "extracted": 0,
                  "agreement": None, "compared": 0, "reasoning_applied": str(reasoning)}
        llm_values = []
        if isinstance(data, dict):
            for b in data.get("benchmarks") or []:
                if isinstance(b, dict) and isinstance(b.get("score"), (int, float)):
                    llm_values.append(_norm_entry({"raw_name": str(b.get("name")), "score": float(b["score"])},
                                                  f"local-llm:{m['model_uid']}", page["url"], "base"))
            result["extracted"] = len(llm_values)
            ref = {b["name"].lower(): b["score"] for b in public_record.get("benchmarks", [])
                   if b["method"] == "card-table"}
            hits = comp = 0
            for b in llm_values:
                k = b["name"].lower()
                if k in ref:
                    comp += 1
                    hits += abs(ref[k] - b["score"]) <= 0.051
            result["compared"] = comp
            result["agreement"] = round(hits / comp, 3) if comp else None
        public_record["llm_extracted"] = llm_values
        public_record["llm_extraction_run"] = result
        # fill gaps: values only the model found (and the deterministic parser missed)
        have = {b["name"].lower() for b in public_record.get("benchmarks", [])}
        for b in llm_values:
            if b["name"].lower() not in have and canonical(b["raw_name"])[0]:
                public_record["benchmarks"].append(b)
        runner.live_result = result
        print(f"    • live extraction by this model: {result['extracted']} values, "
              f"agreement with parser {result['agreement'] if result['agreement'] is not None else '—'}, "
              f"{result['total_s']:.1f}s")

    return run
