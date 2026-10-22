"""`bench merge <path>`: combine results benchmarked on other computers into this database."""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Optional, Tuple

from . import db as dbm
from .config import DATA_DIR, DB_PATH, RAW_DIR


def _locate(path: str) -> Tuple[Optional[Path], Optional[Path]]:
    """Accepts a results.json, a data/ folder, or a benchmark-local-llms/ folder. Returns (results.json, raw dir)."""
    p = Path(path).expanduser().resolve()
    for cand in ([p] if p.is_file() else [p / "results.json", p / "data" / "results.json"]):
        if cand.is_file():
            raw = cand.parent / "raw"
            return cand, raw if raw.is_dir() else None
    return None, None


def _newer(a: Optional[str], b: Optional[str]) -> bool:
    return (a or "") > (b or "")


def merge(paths, dry_run: bool = False) -> int:
    db = dbm.load()
    total = {"runs": 0, "models": 0, "machines": 0, "public": 0, "raw": 0}
    for path in paths:
        src, raw_dir = _locate(path)
        if not src:
            print(f"  ! No results.json found at {path} (give the other computer's results.json, its data/ folder,"
                  " or its benchmark-local-llms/ folder).")
            return 2
        if src.resolve() == DB_PATH.resolve():
            print(f"  ! {src} is this computer's own database, nothing to merge.")
            return 2
        with open(src, "r", encoding="utf-8") as f:
            other = json.load(f)
        if other.get("schema_version", 1) > db.get("schema_version", 1):
            print(f"  ! {src} was written by a newer version of the tool (schema {other['schema_version']}). Update this copy first.")
            return 2
        n = {"runs": 0, "models": 0, "machines": 0, "public": 0, "raw": 0}

        for mid, m in (other.get("machines") or {}).items():
            if mid not in db["machines"]:
                db["machines"][mid] = m
                n["machines"] += 1
            else:   # keep manual specs from both sides
                extra = {**(m.get("specs_extra") or {}), **(db["machines"][mid].get("specs_extra") or {})}
                db["machines"][mid] = {**m, **db["machines"][mid], "specs_extra": extra}

        for uid, m in (other.get("models") or {}).items():
            mine = db["models"].get(uid)
            if not mine:
                db["models"][uid] = m
                n["models"] += 1
            else:
                keep = m if _newer(m.get("last_seen"), mine.get("last_seen")) else mine
                keep = dict(keep)
                keep["first_seen"] = min(x for x in (m.get("first_seen"), mine.get("first_seen")) if x) \
                    if (m.get("first_seen") or mine.get("first_seen")) else None
                db["models"][uid] = keep

        have = {r["run_id"] for r in db["runs"]}
        for r in other.get("runs") or []:
            if r.get("run_id") in have:
                continue
            db["runs"].append(r)
            have.add(r["run_id"])
            n["runs"] += 1
            raw = (r.get("memory") or {}).get("raw_file")
            if raw and raw_dir:
                s = raw_dir / Path(raw).name
                d = RAW_DIR / Path(raw).name
                if s.exists() and not d.exists():
                    if not dry_run:
                        RAW_DIR.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(s, d)
                    n["raw"] += 1

        for uid, p in (other.get("public") or {}).items():
            mine = db["public"].get(uid)
            if not mine or _newer(p.get("updated_at"), mine.get("updated_at")):
                db["public"][uid] = p
                n["public"] += not mine

        machines = sorted({r.get("machine_id") for r in other.get("runs") or []})
        print(f"  ▶ {src}")
        print(f"    machines in that file: {', '.join(machines) or '—'}")
        print(f"    added {n['runs']} run(s), {n['models']} model(s), {n['machines']} machine(s), "
              f"{n['public']} public record(s), {n['raw']} memory timeline(s)")
        for k in total:
            total[k] += n[k]

    if dry_run:
        print("\n  Dry run: nothing was written.")
        return 0
    if total["runs"] or total["models"] or total["machines"] or total["public"]:
        backup = DATA_DIR / f"results.backup-{time.strftime('%Y%m%d-%H%M%S')}.json"
        if DB_PATH.exists():
            shutil.copy2(DB_PATH, backup)
            print(f"\n  Backup of the previous database: {backup.name}")
        dbm.save(db)
        try:
            from .publish import refresh_site
            refresh_site()
        except Exception as ex:
            print(f"  ! could not refresh the dashboard copy: {ex}")
        print(f"  Merged. The database now has {len(db['runs'])} runs from {len(db['machines'])} machine(s). "
              "Open it with:  ./bench dashboard")
    else:
        print("\n  Nothing new to merge: every run in that file is already here.")
    return 0
