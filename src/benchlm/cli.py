"""Command-line interface: ./bench <command>  (see README.md)."""
from __future__ import annotations

import argparse
import csv
import sys
import time
from typing import List

from . import VERSION, db as dbm, hygiene, machine as machine_mod
from .config import LOG_DIR, SECRETS_PATH, Secrets, ensure_dirs, load_profile, prompt_secret
from .engines import connect

STATUS_ICON = {"done": "✓ done", "new": "○ new", "stale": "⚠ settings changed", "partial": "◐ incomplete"}


class Tee:
    def __init__(self, stream, path):
        self.stream = stream
        self.file = open(path, "a", encoding="utf-8")

    def write(self, s):
        self.stream.write(s)
        self.file.write(s)
        self.file.flush()

    def flush(self):
        self.stream.flush()

    def isatty(self):
        return self.stream.isatty()


def _gb(b):
    return f"{b / 1024 ** 3:.1f} GB" if b else "—"


def _matches(model: dict, patterns: List[str]) -> bool:
    if not patterns:
        return True
    hay = " ".join(str(model.get(k) or "") for k in ("model_uid", "key", "display_name")).lower()
    return any(p.lower() in hay for p in patterns)


def _discover(engines):
    models = []
    for e in engines:
        try:
            for m in e.list_models():
                models.append((e, m))
        except Exception as ex:
            print(f"  ! could not list models in {e.name}: {ex}")
    return models


def _sync_module():
    """`bench sync` is a maintainer tool that the public copy leaves out; everything else works without it."""
    try:
        from . import sync
        return sync
    except ImportError:
        return None


def _sync_hint():
    mod = _sync_module()
    if mod:
        mod.print_sync_hint()


def _header(title):
    print(f"\nbenchlm {VERSION} — {title}\n")


# ---------------------------------------------------------------- commands
def cmd_setup(args):
    _header("setup")
    ensure_dirs()
    secrets = Secrets()
    if not secrets.exists:
        print(f"  Creating {SECRETS_PATH.name} (git-ignored) for engine URLs and API keys.")
        secrets.save()
    print("  Engines:")
    engines = connect(secrets, interactive=True)
    if sys.stdin.isatty():
        if not secrets.get("huggingface", "token"):
            print("\n  Optional: a Hugging Face token (read-only) raises API rate limits.")
            tok = prompt_secret("  Hugging Face token")
            if tok:
                secrets.set("huggingface", "token", tok)
                secrets.save()
        if not secrets.get("artificial_analysis", "api_key"):
            print("\n  Optional: an Artificial Analysis API key (free) adds their benchmark data.")
            tok = prompt_secret("  Artificial Analysis API key")
            if tok:
                secrets.set("artificial_analysis", "api_key", tok)
                secrets.save()
    m = machine_mod.detect()
    print(f"\n  Machine: {m['label']}  ({m.get('chip')}, {m.get('cpu_cores')} CPU cores"
          f"{' (' + m['cpu_cores_detail'] + ')' if m.get('cpu_cores_detail') else ''}, "
          f"{m.get('gpu_cores') or '?'} GPU cores, {_gb(m.get('memory_bytes'))} RAM, {m['os']} {m['os_version']})")
    db = dbm.load()
    dbm.upsert_machine(db, m)
    dbm.save(db)
    print(f"\n  {len(_discover(engines))} downloaded LLM(s) found. Next: ./bench list   then   ./bench run")
    return 0


def cmd_status(args):
    _header("engine status")
    secrets = Secrets()
    engines = connect(secrets, interactive=not args.no_input)
    loaded = hygiene.all_loaded(engines)
    print("\n  Loaded right now:" if loaded else "\n  No models are loaded.")
    for i in loaded:
        cfg = i.get("config") or {}
        print(f"    • {i['engine']}: {i['model_key']} ({i.get('type')}, ctx {cfg.get('context_length', '?')})")
    return 0


def cmd_list(args):
    _header("downloaded models")
    secrets = Secrets()
    engines = connect(secrets, interactive=not args.no_input)
    profile = load_profile()
    from .suite import Suite
    suite = Suite()
    m = machine_mod.detect()
    db = dbm.load()
    rows = _discover(engines)
    if not rows:
        print("\n  No LLMs found. Download models in LM Studio or Ollama first.")
        return 0
    print(f"\n  {'STATUS':<20} {'ENGINE':<9} {'FORMAT':<6} {'QUANT':<8} {'SIZE':>8}  MODEL")
    next_up = None
    swap_gb = float(profile.get("swap_warning_gb", 1))
    for e, mod in sorted(rows, key=lambda r: r[1]["model_uid"]):
        st = dbm.status_for(db, mod, m["machine_id"], profile, suite.version)
        if next_up is None and st in ("new", "partial"):
            next_up = mod["display_name"]
        q = (mod.get("quantization") or {}).get("name") or ""
        alias = dbm.equivalent_done(db, mod, m["machine_id"], profile, suite.version) if st == "done" else None
        print(f"  {STATUS_ICON[st]:<20} {e.id:<9} {(mod.get('format') or '?'):<6} {q:<8} "
              f"{_gb(mod.get('size_bytes')):>8}  {mod['display_name']}  [{mod['model_uid']}]"
              + (f"\n  {'':<20} (same file, benchmarked as {alias.split('@')[-1] and '@' + alias.split('@')[-1]})" if alias else ""))
        runs = [r for r in dbm.runs_for(db, mod["model_uid"], m["machine_id"]) if r.get("status") == "complete"]
        last = max(runs, key=lambda r: r["started_at"]) if runs else None
        if last and dbm.swap_warning(last, swap_gb):
            print(f"  {'':<20} ⚠ swap grew by {last['memory']['swap_used_delta_bytes'] / 1024 ** 3:.1f} GB in the last run: "
                  "speeds may be lower than usual (free memory and re-test with --force)")
    print("\n  ./bench run         benchmarks every model that isn't ✓ done (use --force to re-test)")
    if next_up:
        print(f"  ./bench run --next  benchmarks only the next one: {next_up}")
    return 0


def cmd_enrich(args):
    _header("collect public data")
    from .enrich import enrich_model
    secrets = Secrets()
    engines = connect(secrets, interactive=not args.no_input)
    db = dbm.load()
    for e, mod in _discover(engines):
        if not _matches(mod, args.models):
            continue
        if mod["model_uid"] in db["public"] and not args.refresh:
            print(f"  ✓ {mod['display_name']}: already collected (use --refresh)")
            continue
        print(f"  ▶ {mod['display_name']}")
        pub = enrich_model(mod, secrets, refresh=args.refresh, web=not args.no_web)
        pub.pop("_pages", None)
        old = db["public"].get(mod["model_uid"]) or {}
        for k in ("llm_extracted", "llm_extraction_run"):
            if k in old:
                pub[k] = old[k]
        # values the model extracted itself during a run can't be collected again here: keep them
        have = {b["name"].lower() for b in pub["benchmarks"]}
        pub["benchmarks"] += [b for b in old.get("benchmarks") or []
                              if str(b.get("method", "")).startswith("local-llm") and b["name"].lower() not in have]
        db["public"][mod["model_uid"]] = pub
        dbm.upsert_model(db, mod)     # also fills MoE fields from the public record
        dbm.save(db)
    return 0


def cmd_run(args):
    ensure_dirs()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    sys.stdout = Tee(sys.stdout, LOG_DIR / f"run-{stamp}.log")
    _header("benchmark run")
    from .enrich import enrich_model, make_live_extractor
    from .runner import CleanMachineError, ModelRunner
    from .suite import Suite

    secrets = Secrets()
    print("  Engines:")
    engines = connect(secrets, only=[args.engine] if args.engine else None, interactive=not args.no_input)
    all_engines = engines if not args.engine else connect(secrets, interactive=False, quiet=True)
    if not engines:
        print("\n  No engine available. Start LM Studio (server on) or Ollama and try again.")
        return 2
    profile = load_profile()
    if args.context:
        profile["context_length"] = args.context
        profile["hash"] = profile["hash"] + f"-ctx{args.context}"
    suite = Suite()
    m = machine_mod.detect()
    db = dbm.load()
    dbm.upsert_machine(db, m)

    modes = {"off": ["off"], "high": ["high"], "both": ["off", "high"]}[args.reasoning]
    tests = args.only.split(",") if args.only else ["short", "extraction", "long"]
    repeats = 1 if args.quick else (args.repeats or int(profile.get("repeats", 3)))

    todo = []
    for e, mod in sorted(_discover(engines), key=lambda r: r[1]["model_uid"]):
        if not _matches(mod, args.models):
            continue
        st = dbm.status_for(db, mod, m["machine_id"], profile, suite.version)
        if st in ("done", "stale") and not args.force:
            note = "" if st == "done" else " — benchmark settings changed since; use --force to re-test"
            print(f"  ✓ skip {mod['display_name']} ({STATUS_ICON[st]}{note})")
            continue
        todo.append((e, mod))
    if not todo:
        print("\n  Nothing to do: every matching model is already benchmarked (use --force to re-test).")
        dbm.save(db)
        return 0
    limit = 1 if args.next else args.limit
    later = []
    if limit and len(todo) > limit:
        todo, later = todo[:limit], todo[limit:]

    print(f"\n  Machine: {m['label']} · profile {profile['name']} ({profile['hash']}) · suite v{suite.version}")
    print(f"  Plan: {len(todo)} model(s), tests {', '.join(tests)}, reasoning {'/'.join(modes)}, "
          f"{repeats} repeat(s) each:")
    for e, mod in todo:
        print(f"    • {mod['display_name']}  [{mod['model_uid']}]")
    if later:
        print(f"  Left for later ({len(later)}): " + ", ".join(m["display_name"] for _, m in later))
    if args.dry_run:
        print("\n  Dry run: nothing was loaded or benchmarked.")
        return 0

    previously_loaded = hygiene.all_loaded(all_engines)
    if previously_loaded:
        print("\n  Models currently loaded (they'll be unloaded now and reloaded at the end):")
        for i in previously_loaded:
            print(f"    • {i['engine']}: {i['model_key']}")
    left = hygiene.unload_everything(all_engines, verbose=False)
    if left:
        hygiene.print_manual_instructions(all_engines, left)
        return 3

    results, t_start = [], time.time()
    try:
        for n, (e, mod) in enumerate(todo, 1):
            print(f"\n━━ [{n}/{len(todo)}] {mod['display_name']}  ({e.name}, {mod.get('format')}, "
                  f"{(mod.get('quantization') or {}).get('name')}) ━━")
            dbm.upsert_model(db, mod)
            pages_pub = None
            if not args.no_enrich:
                try:
                    # cached for 7 days, so this is cheap when public data was already collected
                    pages_pub = enrich_model(mod, secrets, refresh=args.refresh_public, web=True)
                except Exception as ex:
                    print(f"    ! public data collection failed: {ex}")
            live = None if args.no_live_extract or not pages_pub else make_live_extractor(db, pages_pub)
            prev = [r for r in dbm.runs_for(db, mod["model_uid"], m["machine_id"]) if r.get("tests")]
            runner = ModelRunner(all_engines, e, mod, profile, suite, m, modes, tests, repeats, live,
                                 max_restarts=args.max_restarts, store_reasoning=args.store_reasoning,
                                 previous_tests=max(prev, key=lambda r: r["started_at"])["tests"] if prev else None)
            t0 = time.time()
            try:
                run = runner.run()
            except CleanMachineError as ce:
                hygiene.print_manual_instructions(all_engines, ce.instances)
                return 3
            except KeyboardInterrupt:
                raise
            dbm.add_run(db, run)
            if pages_pub is not None:
                pages_pub.pop("_pages", None)
                db["public"][mod["model_uid"]] = pages_pub
                dbm.apply_moe(db["models"][mod["model_uid"]], pages_pub)
            dbm.save(db)
            try:
                from .publish import refresh_site
                refresh_site()
            except Exception as ex:
                print(f"    ! could not refresh the dashboard copy: {ex}")
            results.append((mod, run, time.time() - t0))
            s = run["summary"]

            def num(k, nd=1):
                v = s.get(k)
                return f"{v:.{nd}f}" if isinstance(v, (int, float)) else "—"
            print(f"  → {run['status'].upper()} in {(time.time() - t0) / 60:.1f} min · "
                  f"short decode {num('short_off_decode_tps')} tok/s · "
                  f"64k prefill {num('long_off_prefill_tps', 0)} tok/s · "
                  f"peak {num('mem_peak_gb')} GB")
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Completed models are saved; the current one will be re-run next time.")
        if not args.no_restore:
            hygiene.restore(all_engines, previously_loaded)
        return 130
    if not args.no_restore:
        hygiene.restore(all_engines, previously_loaded)

    print(f"\n━━ Summary ({(time.time() - t_start) / 60:.1f} min) ━━")
    for mod, run, dt in results:
        print(f"  {run['status']:<9} {mod['display_name']:<32} {dt / 60:5.1f} min"
              + (f"  ({run['error']})" if run.get("error") else ""))
    if later:
        print(f"\n  {len(later)} model(s) still to benchmark — next up: {later[0][1]['display_name']}.")
        print("  Run  ./bench run --next  again when you're ready.")
    print("\n  Dashboard updated. Open it with:  ./bench dashboard\n")
    _sync_hint()
    return 0 if all(r["status"] == "complete" for _, r, _ in results) else 1


def cmd_dashboard(args):
    _header("dashboard")
    if args.live:
        from .server import serve
        serve(args.port, open_browser=not args.no_browser)
        return 0
    import webbrowser
    from .publish import refresh_site
    index = refresh_site()
    url = index.resolve().as_uri()
    print(f"  Dashboard generated from the latest results: {index}")
    print("  It opens straight from disk, so no server is running and there's nothing to stop.")
    print("  (`bench run` regenerates it after each model; press Refresh in the browser to see new results.)")
    if args.no_browser:
        print(f"\n  Open this address in your browser:  {url}\n")
    else:
        webbrowser.open(url)
        print("\n  Opened in your browser.\n")
    return 0


def cmd_publish(args):
    from .publish import publish
    _header("publish dashboard")
    return publish(args.out, include_raw=not args.no_raw, force=args.force, include_answers=args.include_answers)


def cmd_merge(args):
    from .merge import merge
    _header("merge results from other computers")
    rc = merge(args.paths, dry_run=args.dry_run)
    if rc == 0 and not args.dry_run:
        print()
        _sync_hint()
    return rc


def cmd_sync(args):
    mod = _sync_module()
    _header("sync with GitHub")
    if args.reset_public_history and not args.public:
        print("  ! --reset-public-history only works together with --public.")
        return 2
    rc = mod.sync(args.message, dry_run=args.dry_run, push=not args.no_push)
    if rc == 0 and not args.dry_run:
        if args.public:
            rc = mod.publish_public(args.public_dir, push=not args.no_push, reset_history=args.reset_public_history)
        else:
            mod.print_public_hint(args.public_dir)
    return rc


def cmd_recompute(args):
    """Re-derive summaries (incl. context at peak) from stored tests and memory timelines."""
    import json as _json
    from .config import DATA_DIR
    from .answers import backfill
    from .peakctx import analyze
    _header("recompute summaries")
    db = dbm.load()
    swap_gb = float(load_profile().get("swap_warning_gb", 1))
    n = 0
    for run in db["runs"]:
        raw_file = (run.get("memory") or {}).get("raw_file")
        path = DATA_DIR / raw_file if raw_file else None
        if path and path.exists():
            with open(path, "r", encoding="utf-8") as f:
                raw = _json.load(f)
            run["memory"]["context_analysis"] = analyze(run, raw)
            backfill(run, raw)    # reasoning-channel answers, from the stored character counts
        dbm.set_swap_warning(run, swap_gb)
        run["summary"] = dbm.summarize(run)
        n += 1
    # MoE fields from the public records, also for rows whose name is no longer installed (renamed variants):
    # those use the record of another row with the same engine and key.
    by_key = {}
    for uid, mod in db["models"].items():
        if (db["public"].get(uid) or {}).get("moe"):
            by_key.setdefault((mod.get("engine"), mod.get("key")), db["public"][uid])
    for uid, mod in db["models"].items():
        pub = db["public"].get(uid) or {}
        dbm.apply_moe(mod, pub if pub.get("moe") else by_key.get((mod.get("engine"), mod.get("key"))))
    dbm.save(db)
    from .publish import refresh_site
    refresh_site()
    print(f"  Recomputed {n} run(s); dashboard regenerated.\n")
    _sync_hint()
    return 0


def cmd_show(args):
    db = dbm.load()
    runs = [r for r in db["runs"] if any(p.lower() in r["model_uid"].lower() for p in args.models)]
    if not runs:
        print("No runs match.")
        return 1
    for r in sorted(runs, key=lambda r: r["started_at"]):
        mod = db["models"].get(r["model_uid"], {})
        print(f"\n{mod.get('display_name', r['model_uid'])}  —  {r['started_at']}  [{r['status']}]  on {r['machine_id']}")
        for k, v in r.get("summary", {}).items():
            if v is not None:
                print(f"  {k:<32} {v}")
        pub = db["public"].get(r["model_uid"]) or {}
        if pub.get("benchmarks"):
            print("  public benchmarks:")
            for b in pub["benchmarks"]:
                print(f"    {b['category']:<22} {b['name']:<28} {b['score']}{b.get('unit') or ''}  ({b['method']})")
    return 0


def cmd_export(args):
    db = dbm.load()
    keys = sorted({k for r in db["runs"] for k in (r.get("summary") or {})})
    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model_uid", "display_name", "engine", "format", "quant", "machine", "date", "status"] + keys)
        for r in db["runs"]:
            mod = db["models"].get(r["model_uid"], {})
            w.writerow([r["model_uid"], mod.get("display_name"), mod.get("engine"), mod.get("format"),
                        (mod.get("quantization") or {}).get("name"), r["machine_id"], r["started_at"], r["status"]]
                       + [(r.get("summary") or {}).get(k) for k in keys])
    print(f"Wrote {len(db['runs'])} run(s) to {args.csv}")
    return 0


def cmd_machine(args):
    db = dbm.load()
    m = machine_mod.detect()
    dbm.upsert_machine(db, m)
    rec = db["machines"][m["machine_id"]]
    for kv in args.set or []:
        k, _, v = kv.partition("=")
        try:
            v = float(v) if "." in v else int(v)
        except ValueError:
            pass
        rec.setdefault("specs_extra", {})[k.strip()] = v
    dbm.save(db)
    import json
    print(json.dumps(rec, indent=2))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="bench", description="Local LLM performance benchmark (LM Studio / Ollama).")
    p.add_argument("--version", action="version", version=f"benchlm {VERSION}")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("setup", help="detect engines, store API keys, detect this machine")
    s.set_defaults(fn=cmd_setup)

    s = sub.add_parser("status", help="show engines and currently loaded models")
    s.add_argument("--no-input", action="store_true", help="never prompt for keys")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("list", help="list downloaded models and their benchmark status")
    s.add_argument("--no-input", action="store_true")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("run", help="benchmark new models (skips ones already done)")
    s.add_argument("models", nargs="*", help="only models whose name/key contains one of these strings")
    s.add_argument("--force", action="store_true", help="re-test even if already benchmarked")
    s.add_argument("--next", action="store_true", help="benchmark only the next untested model, then stop")
    s.add_argument("--limit", type=int, metavar="N", help="benchmark at most N untested models, then stop")
    s.add_argument("--dry-run", action="store_true", help="show what would be benchmarked, then exit")
    s.add_argument("--engine", choices=["lmstudio", "ollama"], help="only this engine")
    s.add_argument("--only", help="comma list of tests: short,extraction,long")
    s.add_argument("--reasoning", choices=["off", "high", "both"], default="both")
    s.add_argument("--repeats", type=int, default=None, help="override repeats (default from profile: 3)")
    s.add_argument("--quick", action="store_true", help="1 repeat (fast smoke test; results still saved)")
    s.add_argument("--context", type=int, help="override context length (changes the profile hash)")
    s.add_argument("--no-restore", action="store_true", help="don't reload previously loaded models at the end")
    s.add_argument("--store-reasoning", action="store_true",
                   help="also keep the reasoning (thinking) texts in data/raw (can be large; answers are always kept)")
    s.add_argument("--max-restarts", type=int, default=None, metavar="N",
                   help="restarts per test when another model gets loaded, before the model is stopped "
                        "(default: max_test_restarts in config/profile.json, 3)")
    s.add_argument("--no-enrich", action="store_true", help="skip public data collection")
    s.add_argument("--no-live-extract", action="store_true", help="skip the live extraction by the tested model")
    s.add_argument("--refresh-public", action="store_true", help="re-download public data (ignore cache)")
    s.add_argument("--no-input", action="store_true", help="never prompt (for unattended runs)")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("enrich", help="collect public model info + benchmark scores only")
    s.add_argument("models", nargs="*")
    s.add_argument("--refresh", action="store_true")
    s.add_argument("--no-web", action="store_true", help="Hugging Face only, no web search")
    s.add_argument("--no-input", action="store_true")
    s.set_defaults(fn=cmd_enrich)

    s = sub.add_parser("dashboard", help="open the web dashboard (from disk; --live runs a local server)")
    s.add_argument("--live", action="store_true", help="serve the dashboard from a local web server instead (Ctrl+C to stop)")
    s.add_argument("--port", type=int, default=8765, help="port for --live")
    s.add_argument("--no-browser", action="store_true", help="don't open the browser, just print the address")
    s.set_defaults(fn=cmd_dashboard)

    s = sub.add_parser("publish", help="write a static copy of the dashboard + data for any web server")
    s.add_argument("--out", required=True, help="destination folder (created if needed)")
    s.add_argument("--no-raw", action="store_true", help="leave out memory timelines (smaller upload)")
    s.add_argument("--force", action="store_true", help="replace the contents of a non-empty folder")
    s.add_argument("--include-answers", action="store_true",
                   help="keep the models' answer texts in the published raw files (left out by default)")
    s.set_defaults(fn=cmd_publish)

    s = sub.add_parser("merge", help="add results benchmarked on other computers (their results.json or data/ folder)")
    s.add_argument("paths", nargs="+", help="the other computer's results.json, data/ folder or benchmark-local-llms/ folder")
    s.add_argument("--dry-run", action="store_true", help="show what would be added without writing anything")
    s.set_defaults(fn=cmd_merge)

    if _sync_module():   # maintainer copy only
        s = sub.add_parser("sync", help="commit everything in this project and push to main (--public: also publish the public snapshot)")
        s.add_argument("-m", "--message", help="commit message (default: describes the new runs)")
        s.add_argument("--dry-run", action="store_true", help="show what would be committed, without doing it")
        s.add_argument("--no-push", action="store_true", help="commit only, don't push")
        s.add_argument("--public", action="store_true", help="also rebuild the public snapshot (scripts/export-public.sh) and push it")
        s.add_argument("--public-dir", help="local clone of the public repository (default: ~/code/public-repositories/benchmark-local-llms)")
        s.add_argument("--reset-public-history", action="store_true",
                       help="with --public, one-off: make this snapshot the only commit of the public repository (force push)")
        s.set_defaults(fn=cmd_sync)

    s = sub.add_parser("recompute", help="re-derive run summaries from stored data (after a tool update)")
    s.set_defaults(fn=cmd_recompute)

    s = sub.add_parser("show", help="print results for a model")
    s.add_argument("models", nargs="+")
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("export", help="export run summaries to CSV")
    s.add_argument("--csv", default="results.csv")
    s.set_defaults(fn=cmd_export)

    s = sub.add_parser("machine", help="show this machine; --set key=value adds manual specs")
    s.add_argument("--set", action="append", help="e.g. --set memory_bandwidth_gbps=307")
    s.set_defaults(fn=cmd_machine)

    args = p.parse_args(argv)
    if not getattr(args, "fn", None):
        p.print_help()
        return 0
    try:
        return args.fn(args) or 0
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
