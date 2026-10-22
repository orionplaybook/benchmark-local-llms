"""Public data sources: Hugging Face Hub, Artificial Analysis (optional key), web search fallback."""
from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
from typing import List, Optional

from .. import http
from ..config import CACHE_DIR
from .cardparse import match_score, name_tokens

HF = "https://huggingface.co"
QUANTIZER_ORGS = {"lmstudio-community", "mlx-community", "unsloth", "bartowski", "thebloke", "ggml-org",
                  "redhatai", "nvidia", "cyankiwi", "second-state", "quantfactory", "mradermacher",
                  "optimum-intel-internal-testing", "radixark"}
VARIANT_PENALTY = re.compile(r"(gguf|mlx|awq|gptq|fp8|nvfp4|int4|int8|bnb|exl2|w4a16|uncensored|abliterated|heretic|"
                             r"assistant|draft|eagle|mtp|tiny|random|lora|adapter|merge|splash|litert|onnx|"
                             r"japan|docreader|roleplay|finetune|fine-tune)", re.I)
# Publisher names as LM Studio / Ollama report them -> the model maker's Hugging Face organisations.
PUBLISHER_ORGS = {"qwen": {"qwen"}, "google": {"google"}, "nvidia": {"nvidia"}, "mistralai": {"mistralai"},
                  "mistral": {"mistralai"}, "zai-org": {"zai-org", "thudm"}, "meta": {"meta-llama", "meta-models", "facebook"},
                  "openai": {"openai"}, "microsoft": {"microsoft"}, "ibm": {"ibm-granite"}, "deepseek": {"deepseek-ai"},
                  "moonshotai": {"moonshotai"}, "baidu": {"baidu"}, "openbmb": {"openbmb"}, "allenai": {"allenai"}}
REPACKAGED_FORMATS = {"splash", "yuzu"}   # engine-specific packages of someone else's model


def is_repackaged(model: dict) -> bool:
    return str(model.get("format") or "").lower() in REPACKAGED_FORMATS or "splash" in (model.get("key") or "").lower()


def publisher_orgs(model: dict) -> set:
    """HF organisations of the model's maker (empty for engine repackagers like Splash)."""
    if is_repackaged(model):
        return set()
    key = model.get("key") or ""
    pub = (model.get("publisher") or (key.split("/")[0] if "/" in key else "")).lower()
    return PUBLISHER_ORGS.get(pub, {pub} if pub else set())
TRUSTED_WEB = ("huggingface.co", "artificialanalysis.ai", "llm-stats.com", "github.com", "github.io",
               "ai.google.dev", "deepmind.google", "blog.google", "qwenlm.github.io", "qwen.ai", "ai.meta.com",
               "mistral.ai", "openai.com", "anthropic.com", "lmarena.ai", "epoch.ai", "vellum.ai",
               "microsoft.com", "nvidia.com", "ibm.com", "deepseek.com", "moonshot.ai", "z.ai")


def _cache_get(key: str, max_age_s: float = 7 * 86400):
    p = CACHE_DIR / (re.sub(r"[^A-Za-z0-9._-]+", "_", key)[:180] + ".json")
    if p.exists() and time.time() - p.stat().st_mtime < max_age_s:
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            return None
    return None


def _cache_put(key: str, value) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = CACHE_DIR / (re.sub(r"[^A-Za-z0-9._-]+", "_", key)[:180] + ".json")
    p.write_text(json.dumps(value), encoding="utf-8")


def _hf_headers(token: str):
    return {"Authorization": f"Bearer {token}"} if token else {}


# ---------------------------------------------------------------- Hugging Face
def search_names(model: dict) -> List[str]:
    """Search strings for a local model (most specific first)."""
    key = (model.get("key") or "").split("/")[-1]
    disp = model.get("display_name") or ""
    base = re.sub(r"[-_ ](qat|gguf|mlx|instruct|it|\d+bit|q\d\w*)$", "", key, flags=re.I)
    base = re.sub(r"[-_ ](qat|gguf|mlx)\b", "", base, flags=re.I)
    if is_repackaged(model):     # "qwen3.8-27b-splash" -> the base model "qwen3.8-27b"
        base = re.sub(r"[-_ ]?splash\b", "", base, flags=re.I)
        disp = re.sub(r"\s*splash\b", "", disp, flags=re.I)
        key = base
    names = []
    for n in (base, key, disp):
        n = n.strip()
        if n and n.lower() not in [x.lower() for x in names]:
            names.append(n)
    return names


def find_hf_repo(model: dict, token: str = "", refresh: bool = False) -> Optional[dict]:
    """Pick the original (non-quantized) repo for a local model. Returns {'repo', 'score', 'candidates'}."""
    names = search_names(model)
    cands = {}
    for q in names[:2]:
        ck = f"hfsearch_{q}"
        res = None if refresh else _cache_get(ck)
        if res is None:
            try:
                url = f"{HF}/api/models?search={urllib.parse.quote(q)}&sort=downloads&direction=-1&limit=30"
                res = http.get_json(url, _hf_headers(token), timeout=20)
                _cache_put(ck, res)
            except Exception:
                res = []
        for m in res:
            cands[m["id"]] = m
    if not cands:
        return None
    return score_candidates(model, names, cands)


def score_candidates(model: dict, names: List[str], cands: dict) -> Optional[dict]:
    """Rank Hugging Face search results for a local model (pure function, unit-tested)."""
    scored = []
    want = names + ([] if is_repackaged(model) else [model.get("key") or ""])
    makers = publisher_orgs(model)
    size_tokens = {t for n in want for t in name_tokens(n) if re.fullmatch(r"a?\d+(p\d+)?b", t)}
    for rid, m in cands.items():
        org, _, repo = rid.partition("/")
        s = match_score(repo, want)
        if s < 0.5:
            continue
        rtoks = name_tokens(repo)
        rs = {t for t in rtoks if re.fullmatch(r"a?\d+(p\d+)?b", t)}
        if size_tokens and rs and not (rs & size_tokens):
            continue
        extra = len(rtoks - set().union(*[name_tokens(n) for n in want]))
        score = s - 0.08 * extra
        if org.lower() in makers:
            score += 0.7               # the model maker's own page: original weights + benchmark tables
        elif org.lower() in QUANTIZER_ORGS:
            score -= 0.6
        if VARIANT_PENALTY.search(repo):
            score -= 0.5
        if re.search(r"(-it$|-instruct|chat)", repo, re.I):
            score += 0.15              # instruct cards carry the benchmark tables
        score += min(m.get("downloads") or 0, 5e6) / 5e7
        scored.append((round(score, 4), rid))
    if not scored:
        return None
    scored.sort(reverse=True)
    return {"repo": scored[0][1], "score": scored[0][0], "candidates": [r for _, r in scored[:5]]}


def hf_model_info(repo: str, token: str = "", refresh: bool = False) -> dict:
    ck = f"hfinfo_{repo}"
    info = None if refresh else _cache_get(ck)
    if info is None:
        info = http.get_json(f"{HF}/api/models/{repo}", _hf_headers(token), timeout=20)
        _cache_put(ck, info)
    return info


def hf_readme(repo: str, token: str = "", refresh: bool = False) -> str:
    ck = f"hfreadme_{repo}"
    cached = None if refresh else _cache_get(ck)
    if cached is not None:
        return cached.get("text", "")
    try:
        text, _ = http.get_text(f"{HF}/{repo}/raw/main/README.md", _hf_headers(token), timeout=30)
    except Exception:
        text = ""
    _cache_put(ck, {"text": text})
    return text


def hf_config(repo: str, token: str = "", refresh: bool = False) -> dict:
    """The repo's config.json ({} when there is none, e.g. GGUF-only repos)."""
    ck = f"hfconfig_{repo}"
    cached = None if refresh else _cache_get(ck)
    if cached is not None:
        return cached
    try:
        cfg = http.get_json(f"{HF}/{repo}/raw/main/config.json", _hf_headers(token), timeout=20)
    except Exception:
        cfg = {}
    cfg = cfg if isinstance(cfg, dict) else {}
    _cache_put(ck, cfg)
    return cfg


def _first(cfg: dict, *keys):
    for k in keys:
        if cfg.get(k) is not None:
            return cfg[k]
    return None


def moe_from_config(cfg: dict, total_b: Optional[float]) -> Optional[dict]:
    """Experts and experts-per-token from a Hugging Face config.json (nested text_config for multimodal models),
    plus an estimate of the active parameters. None when the model isn't a mixture of experts."""
    c = cfg.get("text_config") if isinstance(cfg.get("text_config"), dict) else cfg
    experts = _first(c, "num_local_experts", "num_experts", "n_routed_experts", "moe_num_experts")
    used = _first(c, "num_experts_per_tok", "experts_per_token", "top_k_experts", "num_experts_per_token", "moe_k")
    if not isinstance(experts, int) or experts <= 1 or not isinstance(used, int):
        return None
    from ..engines.base import moe_active_estimate
    ffn = _first(c, "moe_intermediate_size", "expert_intermediate_size") or c.get("intermediate_size")
    est = moe_active_estimate(total_b, c.get("num_hidden_layers"), c.get("hidden_size"), ffn, experts, used,
                              _first(c, "first_k_dense_replace", "num_dense_layers") or 0)
    return {"experts": experts, "experts_per_token": used, "params_active_b": est,
            "active_source": "estimated from config.json" if est is not None else None}


_ACTIVE_PATTERNS = [
    re.compile(r"(\d+(?:\.\d+)?)\s*B[- ]?A(\d+(?:\.\d+)?)B\b", re.I),                     # 30B-A3B
    re.compile(r"(\d+(?:\.\d+)?)\s*B(?:illion)?\s+(?:total\s+)?param\w*[^.\n]{0,60}?"
               r"(\d+(?:\.\d+)?)\s*B(?:illion)?\s+(?:active|activated)", re.I),               # 21B parameters with 3.6B active
]


def active_from_card(readme: str, total_b: Optional[float]) -> Optional[float]:
    """Active parameters stated in a model card, for the size matching this model (cards often list siblings)."""
    if not readme or not total_b:
        return None
    for pat in _ACTIVE_PATTERNS:
        for m in pat.finditer(readme):
            tot, act = float(m.group(1)), float(m.group(2))
            if abs(tot - total_b) / total_b <= 0.2 and 0 < act < tot:
                return act
    return None


def model_index_results(info: dict) -> List[dict]:
    """Structured eval results from the card's model-index (if any)."""
    out = []
    for entry in info.get("model-index") or (info.get("cardData") or {}).get("model-index") or []:
        for res in entry.get("results") or []:
            ds = (res.get("dataset") or {}).get("name") or (res.get("dataset") or {}).get("type")
            for met in res.get("metrics") or []:
                v = met.get("value")
                if isinstance(v, (int, float)) and ds:
                    out.append({"raw_name": f"{ds} ({met.get('name') or met.get('type')})", "score": float(v)})
    return out


# ---------------------------------------------------------------- Artificial Analysis (optional)
def artificial_analysis(model: dict, api_key: str) -> List[dict]:
    if not api_key:
        return []
    ck = "aa_models"
    data = _cache_get(ck, 86400)
    if data is None:
        try:
            data = http.get_json("https://artificialanalysis.ai/api/v2/data/llms/models",
                                 {"x-api-key": api_key}, timeout=30)
            _cache_put(ck, data)
        except Exception as e:
            print(f"      ! Artificial Analysis API: {e}")
            return []
    rows = data.get("data", data) if isinstance(data, dict) else data
    names = search_names(model)
    # The same model is often listed once per reasoning effort ("gpt-oss-20b (Low)", "(High)"): match on the name
    # without the effort, then keep the lowest and the highest effort.
    scored = []
    for r in rows or []:
        m = _AA_EFFORT.search(r.get("name") or "")
        base = _AA_EFFORT.sub("", r.get("name") or "")
        slug = EFFORT_SUFFIX.sub("", r.get("slug") or "")
        s = max(match_score(base, names), match_score(slug, names))
        scored.append((s, base, (m.group(1).lower() if m else ""), r))
    best = max((x[0] for x in scored), default=0.0)
    if best < 0.75:
        return []
    top_base = next(x[1] for x in scored if x[0] == best)
    variants = [(effort, r) for s, base, effort, r in scored if s == best and base == top_base]
    out = []
    for effort, end, row in effort_ends(variants):
        for k, v in (row.get("evaluations") or {}).items():
            if isinstance(v, (int, float)):
                score = v * 100 if 0 < v <= 1 and "index" not in k else v
                out.append({"raw_name": k.replace("_", " "), "score": round(score, 2),
                            "source_url": f"https://artificialanalysis.ai/models/{row.get('slug', '')}",
                            "column": row.get("name"), "effort": effort, "effort_end": end})
    return out


# ---------------------------------------------------------------- web search (no API key)
def web_search(query: str, limit: int = 8) -> List[str]:
    ck = f"ddg_{query}"
    cached = _cache_get(ck, 3 * 86400)
    if cached is not None:
        return cached
    urls = []
    try:
        body, _ = http.get_text("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query), timeout=20)
        if "anomaly" in body and "result__a" not in body:
            return []   # bot challenge: respect it, don't retry or work around it
        for href in re.findall(r'class="result__a"[^>]*href="([^"]+)"', body):
            href = html.unescape(href)
            m = re.search(r"uddg=([^&]+)", href)
            url = urllib.parse.unquote(m.group(1)) if m else href
            if url.startswith("http") and url not in urls:
                urls.append(url)
    except Exception:
        pass
    _cache_put(ck, urls[:limit])
    return urls[:limit]


def trusted(url: str) -> bool:
    host = urllib.parse.urlparse(url).hostname or ""
    return any(host == d or host.endswith("." + d) or host.endswith(d) for d in TRUSTED_WEB)


def fetch_page(url: str) -> str:
    ck = f"page_{url}"
    cached = _cache_get(ck, 3 * 86400)
    if cached is not None:
        return cached.get("text", "")
    try:
        text, _ = http.get_text(url, timeout=25)
    except Exception:
        text = ""
    _cache_put(ck, {"text": text})
    return text


def html_to_text(raw: str, limit: int = 60000) -> str:
    """Readable text that keeps tables as Markdown-ish rows (for LLM extraction)."""
    s = re.sub(r"(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>", " ", raw)
    s = re.sub(r"(?is)<tr[^>]*>", "\n|", s)
    s = re.sub(r"(?is)</t[dh]>", " |", s)
    s = re.sub(r"(?is)<br\s*/?>|</p>|</div>|</h\d>|</li>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip()[:limit]


# ---------------------------------------------------------------- Epoch AI benchmarking hub (keyless, CC-BY)
EPOCH_URL = "https://epoch.ai/data/benchmark_data.zip"
EFFORT_SUFFIX = re.compile(r"[_-](minimal|low|medium|high|xhigh|max|none|thinking|nothinking|default)$", re.I)
# Reasoning effort, lowest to highest. "" / default sits in the middle (unknown); thinking/reasoning ≈ high.
EFFORT_LEVEL = {"none": 0, "nothinking": 0, "non-reasoning": 0, "minimal": 1, "low": 2, "medium": 3, "default": 3,
                "": 3, "high": 4, "thinking": 4, "reasoning": 4, "xhigh": 5, "max": 6}
_AA_EFFORT = re.compile(r"\s*\((minimal|low|medium|high|xhigh|max|reasoning|non-reasoning|thinking|non-thinking)\)\s*$", re.I)


def effort_ends(found: List[tuple]) -> List[tuple]:
    """found: [(effort, payload)] for one benchmark of one model, one entry per effort the source ran. Returns
    [(effort, end, payload)]: the highest effort with end "max" and the lowest with end "min" when the source has
    several efforts, else the single entry with end None."""
    by = {}
    for effort, payload in found:
        by.setdefault(effort, payload)
    if len(by) < 2:
        return [(e, None, p) for e, p in by.items()]
    order = sorted(by, key=lambda e: EFFORT_LEVEL.get(e, 3))
    lo, hi = order[0], order[-1]
    if EFFORT_LEVEL.get(lo, 3) == EFFORT_LEVEL.get(hi, 3):          # e.g. "high" and "thinking": same level
        return [(hi, None, by[hi])]
    return [(hi, "max", by[hi]), (lo, "min", by[lo])]
ALLOWED_EXTRA = {"it", "instruct", "chat", "open", "preview"}


def _epoch_zip(refresh: bool = False):
    import zipfile
    path = CACHE_DIR / "epoch_benchmark_data.zip"
    if refresh or not path.exists() or time.time() - path.stat().st_mtime > 7 * 86400:
        try:
            import urllib.request
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(EPOCH_URL, headers={"User-Agent": http.USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
                f.write(r.read(50_000_000))
        except Exception as e:
            if not path.exists():
                print(f"      ! Epoch AI data unavailable: {e}")
                return None
    try:
        return zipfile.ZipFile(path)
    except Exception:
        return None


def strict_name_match(candidate: str, names: List[str]) -> bool:
    """Candidate must contain every core token of a local name and add nothing but allowed extras."""
    c = name_tokens(candidate)
    for n in names:
        core = name_tokens(n)
        if len(core) < 2:
            continue
        if core <= c and not (c - core - ALLOWED_EXTRA):
            return True
    return False


def epoch_benchmarks(model: dict, refresh: bool = False) -> List[dict]:
    import csv
    import io
    zf = _epoch_zip(refresh)
    if not zf:
        return []
    names = search_names(model)
    try:
        meta = list(csv.DictReader(io.TextIOWrapper(zf.open("benchmark_metadata.csv"), encoding="utf-8")))
    except KeyError:
        return []
    out = []
    for bm in meta:
        if bm.get("superseded_by"):
            continue
        fname, col = bm.get("source_file"), bm.get("score_column")
        try:
            rows = list(csv.DictReader(io.TextIOWrapper(zf.open(fname), encoding="utf-8")))
        except KeyError:
            continue
        found = []
        for r in rows:
            mv = (r.get("Model version") or "").split("/")[-1]
            m = EFFORT_SUFFIX.search(mv)
            effort = m.group(1).lower() if m else ""
            base = EFFORT_SUFFIX.sub("", mv)
            if not strict_name_match(base, names):
                continue
            try:
                val = float(r.get(col) or r.get("mean_score") or "")
            except ValueError:
                continue
            found.append((effort, (val, mv)))
        scale = float(bm.get("scale") or 1) or 1
        for effort, end, (val, mv) in effort_ends(found):   # both ends when Epoch ran several efforts
            score = val / scale * 100 if scale == 1.0 and val <= 1.0 else val
            out.append({"raw_name": bm["benchmark"], "score": round(score, 2), "unit": "%" if scale == 1.0 else "",
                        "column": mv, "effort": effort, "effort_end": end,
                        "source_url": "https://epoch.ai/benchmarks"})
    return out


# ---------------------------------------------------------------- links from the model card
def card_links(readme: str, limit: int = 3) -> List[str]:
    urls = []
    for u in re.findall(r"https?://[^\s)\"'<>\]]+", readme or ""):
        u = u.rstrip(".,;")
        host = urllib.parse.urlparse(u).hostname or ""
        if host.endswith("huggingface.co") or re.search(r"\.(png|jpe?g|gif|svg|pdf|webp|mp4)$", u, re.I):
            continue
        if trusted(u) and re.search(r"blog|research|news|report|eval|benchmark|qwen|gemma|release|model", u, re.I):
            if u not in urls:
                urls.append(u)
    return urls[:limit]


# ---------------------------------------------------------------- optional keyed / self-hosted search
def search(query: str, secrets) -> List[str]:
    brave = secrets.get("brave_search", "api_key")
    if brave:
        try:
            d = http.get_json("https://api.search.brave.com/res/v1/web/search?count=10&q=" + urllib.parse.quote(query),
                              {"X-Subscription-Token": brave, "Accept": "application/json"}, timeout=20)
            return [r["url"] for r in (d.get("web") or {}).get("results", []) if r.get("url")]
        except Exception as e:
            print(f"      ! Brave search: {e}")
    searx = secrets.get("searxng", "base_url")
    if searx:
        try:
            d = http.get_json(searx.rstrip("/") + "/search?format=json&q=" + urllib.parse.quote(query), timeout=20)
            return [r["url"] for r in d.get("results", []) if r.get("url")]
        except Exception as e:
            print(f"      ! SearXNG search: {e}")
    return web_search(query)
