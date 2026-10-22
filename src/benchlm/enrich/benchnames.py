"""Canonical benchmark names, aliases and categories (used to normalise scraped tables)."""
from __future__ import annotations

import re
from typing import Optional, Tuple

# (canonical name, category, [alias regexes]) — aliases are matched against a normalised raw name.
BENCHMARKS = [
    # reasoning / knowledge
    ("MMLU-Pro", "knowledge", [r"^mmlu ?pro"]),
    ("MMLU", "knowledge", [r"^mmlu$", r"^mmlu \(?\d+.shot"]),
    ("MMMLU", "knowledge", [r"^mmmlu", r"multilingual mmlu"]),
    ("GPQA Diamond", "reasoning", [r"^gpqa"]),
    ("HLE", "reasoning", [r"^hle", r"humanity.?s last exam"]),
    ("BigBench Extra Hard", "reasoning", [r"big ?bench extra hard", r"^bbeh"]),
    ("BBH", "reasoning", [r"^bbh", r"big ?bench hard"]),
    ("SuperGPQA", "reasoning", [r"^supergpqa"]),
    ("SimpleQA", "knowledge", [r"^simpleqa"]),
    ("ARC-AGI", "reasoning", [r"^arc.?agi"]),
    # math
    ("AIME 2026", "math", [r"^aime ?(20)?26"]),
    ("AIME 2025", "math", [r"^aime ?(20)?25"]),
    ("AIME 2024", "math", [r"^aime ?(20)?24"]),
    ("HMMT", "math", [r"^hmmt"]),
    ("MATH-500", "math", [r"^math ?500"]),
    ("MATH", "math", [r"^math$"]),
    ("GSM8K", "math", [r"^gsm ?8k"]),
    # coding
    ("LiveCodeBench", "coding", [r"^livecodebench", r"^lcb"]),
    ("SWE-bench Verified", "coding", [r"^swe.?bench verified"]),
    ("SWE-bench Pro", "coding", [r"^swe.?bench pro"]),
    ("SWE-bench Multilingual", "coding", [r"^swe.?bench multilingual"]),
    ("Terminal-Bench", "agentic", [r"^terminal.?bench"]),
    ("Codeforces", "coding", [r"^codeforces"]),
    ("HumanEval", "coding", [r"^humaneval"]),
    ("MBPP", "coding", [r"^mbpp"]),
    ("SciCode", "coding", [r"^scicode"]),
    ("Aider Polyglot", "coding", [r"aider"]),
    # agentic / tool use
    ("BFCL", "agentic", [r"^bfcl", r"berkeley function"]),
    ("τ³-Banking", "agentic", [r"^(tau|τ|𝛕) ?3", r"^τ³", r"^tau.?banking"]),
    ("τ²-bench", "agentic", [r"^(tau|τ|𝛕) ?2", r"^τ²", r"^tau.?bench", r"^τ.?bench"]),
    ("τ³-bench", "agentic", [r"^(tau|τ|𝛕) ?3"]),
    ("MCP Atlas", "agentic", [r"^mcp.?atlas"]),
    ("OSWorld", "agentic", [r"^osworld"]),
    ("BrowseComp", "agentic", [r"^browsecomp"]),
    ("GAIA", "agentic", [r"^gaia"]),
    ("DeepSearch QA", "agentic", [r"^deepsearch"]),
    ("GDPval", "agentic", [r"^gdp ?val"]),
    ("Agentic Index", "agentic", [r"agentic index"]),
    # instruction following
    ("IFEval", "instruction_following", [r"^ifeval"]),
    ("IFBench", "instruction_following", [r"^ifbench"]),
    ("Arena-Hard", "instruction_following", [r"^arena.?hard"]),
    ("Arena Elo", "instruction_following", [r"arena (elo|score)", r"^lmarena", r"^chatbot arena"]),
    # vision
    ("MMMU Pro", "vision", [r"^mmmu.?pro"]),
    ("MMMU", "vision", [r"^mmmu$", r"^mmmu \(", r"^mmmu val"]),
    ("MathVista", "vision", [r"^mathvista"]),
    ("MATH-Vision", "vision", [r"^math.?vision"]),
    ("ChartQA", "vision", [r"^chartqa"]),
    ("CharXiv", "vision", [r"^charxiv"]),
    ("DocVQA", "vision", [r"^docvqa"]),
    ("OmniDocBench", "vision", [r"^omnidocbench"]),
    ("ScreenSpot Pro", "vision", [r"^screenspot"]),
    ("Video-MME", "vision", [r"^video.?mme"]),
    # long context
    ("RULER", "long_context", [r"^ruler"]),
    ("MRCR", "long_context", [r"^mrcr"]),
    ("LongBench", "long_context", [r"^longbench"]),
    ("AA-LCR", "long_context", [r"^aa.?lcr", r"^lcr$"]),
    ("Beam128K", "long_context", [r"^beam ?128"]),
    ("OTIS Mock AIME", "math", [r"^otis"]),
    ("FrontierMath", "math", [r"^frontiermath"]),
    ("ProofBench", "math", [r"^proofbench"]),
    ("Surface Evolver Bench", "math", [r"surface evolver"]),
    ("WeirdML", "coding", [r"^weirdml"]),
    ("APEX-Agents", "agentic", [r"^apex.?agents"]),
    ("METR Time Horizon", "agentic", [r"^metr"]),
    ("LiveBench", "reasoning", [r"^livebench"]),
    ("SimpleBench", "reasoning", [r"^simplebench"]),
    ("Fiction.LiveBench", "long_context", [r"^fiction.?livebench"]),
    # composite indexes
    ("Intelligence Index", "reasoning", [r"intelligence index"]),
    ("Coding Index", "coding", [r"coding index"]),
    ("Math Index", "math", [r"math index"]),
]

_COMPILED = [(name, cat, [re.compile(a) for a in aliases]) for name, cat, aliases in BENCHMARKS]

CATEGORIES = ["reasoning", "knowledge", "math", "coding", "agentic", "vision", "long_context",
              "instruction_following"]


def normalise(raw: str) -> str:
    s = re.sub(r"<[^>]+>", " ", raw)
    s = re.sub(r"[*_`\\]", "", s)
    s = s.replace(" ", " ").lower()
    s = re.sub(r"[\-–—]", "-", s)
    s = s.replace("-", " ").replace("–", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def canonical(raw: str) -> Tuple[Optional[str], str]:
    """(canonical_name or None, category). Unknown names keep None + 'other'."""
    n = normalise(raw)
    n2 = n.replace(" ", "")
    for name, cat, pats in _COMPILED:
        for p in pats:
            if p.search(n) or p.search(n2):
                return name, cat
    return None, "other"


SECTION_CATEGORY = [
    (r"agent|tool", "agentic"), (r"cod", "coding"), (r"vision|multimodal|visual|image", "vision"),
    (r"math", "math"), (r"long|context", "long_context"), (r"reason|stem|knowledge|general", "reasoning"),
    (r"instruct|alignment|chat", "instruction_following"),
]


def category_from_section(section: str) -> Optional[str]:
    s = (section or "").lower()
    for pat, cat in SECTION_CATEGORY:
        if re.search(pat, s):
            return cat
    return None
