"""`bench publish --out <folder>`: a self-contained static copy of the dashboard for any web server."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import answers, db as dbm
from .config import DASHBOARD_DIR, RAW_DIR, ROOT, SITE_DIR

MARKER = ".bench-publish"
README = """This folder is a published snapshot of a benchlm dashboard (made with `./bench publish`).

Upload everything in it to any static web server (your own server, GitHub Pages, Netlify,
an S3 bucket...) and open index.html through http(s). You can also simply double-click index.html:
the data is included as scripts (data/*.js), which browsers allow from local files.

Contents: index.html, app.js, js/, styles.css, vendor/ (Chart.js) and data/ (results.json plus
memory timelines in data/raw/). No API keys, hostnames or prompts are included, and no answer texts
unless the snapshot was made with --include-answers.
Re-run `./bench publish --out <this folder>` after new benchmarks to refresh it.
"""


def _size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _write_js(path: Path, statement_prefix: str, obj) -> None:
    """Data as a script, so the dashboard also works when opened from file:// (browsers block fetch there)."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(statement_prefix)
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")


def publish(out: str, include_raw: bool = True, force: bool = False, quiet: bool = False, internal: bool = False,
            include_answers: bool = False) -> int:
    dest = Path(out).expanduser().resolve()
    root = ROOT.resolve()
    if not internal and (dest == root or root in dest.parents and dest.relative_to(root).parts[0] in ("dashboard", "data", "src", "benchmarks", "config")):
        print(f"  ! Choose a folder outside the tool's own dashboard/data/source folders (got {dest}).")
        return 2
    if dest.exists() and any(dest.iterdir()):
        if (dest / MARKER).exists() or force:
            for child in dest.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        else:
            print(f"  ! {dest} is not empty and wasn't created by `bench publish`.")
            print("    Pick an empty or new folder, or add --force to replace its contents.")
            return 2
    dest.mkdir(parents=True, exist_ok=True)

    shutil.copytree(DASHBOARD_DIR, dest, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("sample", ".DS_Store", "*.map"))

    index = dest / "index.html"
    html = index.read_text(encoding="utf-8")
    if 'name="bench-static"' not in html:
        html = html.replace("<head>", '<head>\n  <meta name="bench-static" content="1">', 1)
        index.write_text(html, encoding="utf-8")

    db = dbm.merged_view(dbm.load())
    db["published_at"] = dbm.now_iso()
    data_dir = dest / "data"
    (data_dir / "raw").mkdir(parents=True, exist_ok=True)
    with open(data_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, separators=(",", ":"))
    _write_js(data_dir / "results.js", "window.BENCH_DB=", db)

    copied = missing = 0
    if include_raw:
        for run in db.get("runs", []):
            raw = (run.get("memory") or {}).get("raw_file")
            src = RAW_DIR / Path(raw).name if raw else None
            if src and src.exists():
                with open(src, "r", encoding="utf-8") as f:
                    raw_obj = json.load(f)
                if not include_answers:
                    raw_obj = answers.strip_texts(raw_obj)   # the models' answer texts stay private by default
                with open(data_dir / "raw" / src.name, "w", encoding="utf-8") as f:
                    json.dump(raw_obj, f, ensure_ascii=False, separators=(",", ":"))
                _write_js(data_dir / "raw" / (src.stem + ".js"),
                          "(window.BENCH_RAW=window.BENCH_RAW||{})[" + json.dumps(run["run_id"]) + "]=", raw_obj)
                copied += 1
            elif raw:
                missing += 1

    (dest / ".nojekyll").write_text("", encoding="utf-8")   # GitHub Pages: serve files as-is
    (dest / "README.txt").write_text(README, encoding="utf-8")
    (dest / MARKER).write_text(db["published_at"] + "\n", encoding="utf-8")

    if quiet:
        return 0
    runs = [r for r in db.get("runs", []) if r.get("status") == "complete"]
    print(f"\n  Published to {dest}")
    print(f"  {len(db.get('models', {}))} models, {len(runs)} complete runs, "
          f"{copied} memory timelines{f' ({missing} missing)' if missing else ''}"
          f"{'' if include_raw else ' (timelines skipped: --no-raw)'} · {_size(dest) / 1e6:.1f} MB")
    print("\n  Upload the whole folder to any static web server and open its address in a browser.")
    print(f"  Preview locally: open {dest / 'index.html'} in your browser (double-click works).")
    print("  Re-run this command after new benchmarks to refresh the snapshot.\n")
    return 0


def refresh_site(quiet: bool = True) -> Path:
    """Regenerate the local dashboard copy in data/site/ (opened from file:// by `bench dashboard`)."""
    publish(str(SITE_DIR), quiet=quiet, internal=True, force=True)
    return SITE_DIR / "index.html"
