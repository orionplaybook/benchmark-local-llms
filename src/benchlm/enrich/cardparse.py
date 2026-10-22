"""Deterministic extraction of benchmark scores from model-card tables (Markdown and HTML)."""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from typing import List, Optional

from .benchnames import canonical, category_from_section

STOP_TOKENS = {"it", "instruct", "chat", "qat", "gguf", "mlx", "the", "model", "mode", "thinking", "reasoning",
               "high", "low", "medium", "non", "no", "think", "base", "dense", "moe", "unified", "preview"}


def name_tokens(s: str) -> set:
    s = s.lower()
    s = re.sub(r"[@:].*$", "", s) if "/" in s or "@" in s else s
    s = s.split("/")[-1]
    s = re.sub(r"(\d)\.(\d)", r"\1p\2", s)                 # 3.8 -> 3p8 keeps versions together
    s = re.sub(r"([a-z])(\d)", r"\1 \2", s)                 # qwen3p8 -> qwen 3p8
    s = re.sub(r"(\d)b([a-z])", r"\1b \2", s)                # 30bhigh -> 30b high
    toks = set(t for t in re.split(r"[^a-z0-9]+", s) if t)
    toks = {t for t in toks if t not in STOP_TOKENS and not re.fullmatch(r"q\d.*|\d+bit|fp\d+|bf16|nvfp4", t)}
    return toks


def match_score(header: str, model_names: List[str]) -> float:
    h = name_tokens(header)
    if not h:
        return 0.0
    best = 0.0
    for n in model_names:
        m = name_tokens(n)
        if not m:
            continue
        inter = len(h & m)
        # size tokens (31b, a4b) must agree when both present
        hs = {t for t in h if re.fullmatch(r"a?\d+(p\d+)?b", t)}
        ms = {t for t in m if re.fullmatch(r"a?\d+(p\d+)?b", t)}
        if hs and ms and not (hs & ms):
            continue
        score = inter / max(len(m), 1) + 0.25 * inter / max(len(h), 1)
        best = max(best, score)
    return best


# ---------------------------------------------------------------- table readers
def _cells_md(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def markdown_tables(text: str) -> List[List[List[str]]]:
    tables, cur = [], []
    text = re.sub(r"[\v\f\u2028\u2029\x85]", " ", text)   # splitlines() would break rows on these
    for line in text.split("\n"):
        if line.strip().startswith("|"):
            cells = _cells_md(line)
            if all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) or c == "" for c in cells):
                continue  # separator
            cur.append(cells)
        else:
            if len(cur) >= 2:
                tables.append(cur)
            cur = []
    if len(cur) >= 2:
        tables.append(cur)
    return tables


class _HTMLTables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.stack = [], []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.stack.append([])
        elif tag == "tr" and self.stack:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
            self._colspan = int(dict(attrs).get("colspan") or 1)
        elif tag in ("br", "div", "p") and self.cell is not None:
            self.cell.append(" | " if tag == "div" else " ")

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None and self.row is not None:
            txt = re.sub(r"\s+", " ", "".join(self.cell)).strip(" |")
            self.row.append(txt)
            for _ in range(self._colspan - 1):
                self.row.append("\x00span")
            self.cell = None
        elif tag == "tr" and self.row is not None and self.stack:
            if self.row:
                self.stack[-1].append(self.row)
            self.row = None
        elif tag == "table" and self.stack:
            t = self.stack.pop()
            if len(t) >= 2:
                self.tables.append(t)

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)


def html_tables(text: str) -> List[List[List[str]]]:
    p = _HTMLTables()
    try:
        p.feed(text)
    except Exception:
        pass
    return p.tables


NUM = re.compile(r"^[~≈]?\s*(-?\d+(?:[.,]\d+)?)\s*(%|pts?)?(?:\s*[\*†‡]+|\s*\^?\*?)?$")


def parse_value(cell: str) -> Optional[tuple]:
    c = html.unescape(re.sub(r"<[^>]+>", "", cell)).replace("*", "").replace("\\", "").strip()
    c = re.sub(r"\s+", " ", c)
    m = NUM.match(c)
    if not m:
        return None
    v = float(m.group(1).replace(",", ".")) if m.group(1).count(",") == 1 and "." not in m.group(1) else float(m.group(1).replace(",", ""))
    return v, ("%" if m.group(2) == "%" else "")


def _is_numeric_col(rows, j):
    vals = [r[j] for r in rows[1:] if j < len(r) and r[j] and r[j] != "\x00span"]
    if not vals:
        return False
    return sum(1 for v in vals if parse_value(v) or v.strip() in ("-", "--", "—", "N/A", "n/a")) >= 0.6 * len(vals)


def extract_from_table(rows: List[List[str]], model_names: List[str]) -> List[dict]:
    """Model-as-columns tables: header row lists models, first text column(s) list benchmarks."""
    header = rows[0]
    width = max(len(r) for r in rows)
    numeric = [j for j in range(width) if _is_numeric_col(rows, j)]
    if not numeric:
        return []
    scores = [(match_score(header[j] if j < len(header) else "", model_names), j) for j in numeric]
    scores.sort(key=lambda x: (-x[0], x[1]))
    best, col = scores[0]
    if best < 0.5:
        return []
    text_cols = [j for j in range(width) if j not in numeric]
    out, section = [], ""
    for r in rows[1:]:
        cells = [c for c in r]
        texts = [cells[j] for j in text_cols if j < len(cells) and cells[j] and cells[j] != "\x00span"]
        # section rows: a single text cell, nothing numeric
        if col >= len(cells) or cells[col] in ("", "\x00span"):
            if texts and all(not parse_value(c) for c in cells if c and c != "\x00span"):
                section = re.sub(r"[*_]", "", texts[0]).strip()
            continue
        v = parse_value(cells[col])
        if not v or not texts:
            continue
        # prefer the most specific name: last text column, then "a | b" pieces
        cand = []
        for t in reversed(texts):
            cand += [p.strip() for p in reversed(t.split(" | ")) if p.strip()]
        name, cat, raw = None, "other", cand[0]
        for c in cand:
            n, k = canonical(c)
            if n:
                name, cat, raw = n, k, c
                break
        if texts and len(texts) > 1:
            first = re.sub(r"[*_]", "", texts[0]).strip()
            if first:
                section = first
        if cat == "other":
            cat = category_from_section(section) or "other"
        out.append({"name": name or re.sub(r"[*_`\\]", "", raw).strip(), "raw_name": re.sub(r"\s+", " ", raw),
                    "category": cat, "score": v[0], "unit": v[1], "column": header[col] if col < len(header) else "",
                    "known": bool(name)})
    return out


def extract_transposed(rows: List[List[str]], model_names: List[str]) -> List[dict]:
    """Benchmarks-as-columns tables: each row is a model."""
    header = rows[0]
    best, row = 0.0, None
    for r in rows[1:]:
        s = match_score(r[0] if r else "", model_names)
        if s > best:
            best, row = s, r
    if best < 0.5 or not row:
        return []
    out = []
    for j, h in enumerate(header[1:], start=1):
        if j >= len(row):
            break
        v = parse_value(row[j])
        name, cat = canonical(h)
        if v and name:
            out.append({"name": name, "raw_name": h, "category": cat, "score": v[0], "unit": v[1],
                        "column": row[0], "known": True})
    return out


def extract_benchmarks(text: str, model_names: List[str]) -> List[dict]:
    tables = markdown_tables(text) + html_tables(text)
    found = []
    for t in tables:
        rows = extract_from_table(t, model_names)
        if not rows:
            rows = extract_transposed(t, model_names)
        found.extend(rows)
    # dedupe by name: keep first (card's primary table usually first)
    seen, out = set(), []
    for b in found:
        k = b["name"].lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(b)
    return out


def extract_facts(text: str) -> dict:
    """Context length / params from spec tables (best effort)."""
    facts = {}
    m = re.search(r"context (?:length|window)[^|\n]*\|\s*\**\s*([\d,.]+)\s*([kK])?", text, re.I)
    if m:
        n = float(m.group(1).replace(",", ""))
        facts["context_window"] = int(n * 1024) if m.group(2) else int(n)
    return facts
