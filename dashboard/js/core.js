/* Core: formatting, storage, data loading, derived rows, metrics, fit score.
   Everything hangs off the global `BL` namespace (no build step, no modules). */
(function () {
  "use strict";
  const BL = (window.BL = window.BL || {});
  const GB = 1024 ** 3;
  const DASH = "—";

  // ---------------------------------------------------------------- utils
  const isNum = (v) => typeof v === "number" && isFinite(v);
  const esc = (s) =>
    String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const get = (obj, path) => {
    let o = obj;
    for (const p of path.split(".")) {
      if (o == null) return undefined;
      o = o[p];
    }
    return o;
  };
  const mean = (arr) => {
    const v = arr.filter(isNum);
    return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null;
  };

  const fmt = {
    tps: (v) => (isNum(v) ? v.toFixed(1) : DASH),
    sec: (v) => (isNum(v) ? v.toFixed(2) : DASH),
    gb: (v) => (isNum(v) ? v.toFixed(1) : DASH),
    bytesGB: (b) => (isNum(b) ? (b / GB).toFixed(1) + " GB" : DASH),
    pct01: (v) => (isNum(v) ? Math.round(v * 100) + "%" : DASH),
    score: (v) => (isNum(v) ? v.toFixed(1) : DASH),
    int: (v) => (isNum(v) ? Math.round(v).toLocaleString("en-US") : DASH),
    fit: (v) => (isNum(v) ? Math.round(v).toString() : DASH),
    text: (v) => (v == null || v === "" ? DASH : esc(v)),
    bool: (v) => (v === true ? "yes" : v === false ? "no" : DASH),
    date: (s) => {
      if (!s) return DASH;
      const d = new Date(s);
      if (isNaN(d)) return esc(s);
      return d.toLocaleString(undefined, { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
    },
    // With the time zone, e.g. "Oct 21, 2026, 16:49 EDT" (the viewer's local zone). Times use the 24-hour clock:
    // browsers pick 12/24 h from their language, not from the system's clock setting, so it can't follow it.
    dateTz: (s) => {
      if (!s) return DASH;
      const d = new Date(s);
      if (isNaN(d)) return esc(s);
      return d.toLocaleString(undefined, { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZoneName: "short" });
    },
    dateShort: (s) => {
      if (!s) return DASH;
      const d = new Date(s);
      return isNaN(d) ? esc(s) : d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
    },
    ago: (s) => {
      const d = new Date(s);
      if (!s || isNaN(d)) return "";
      const m = Math.round((Date.now() - d.getTime()) / 60000);
      if (m < 1) return "just now";
      if (m < 60) return m + " min ago";
      const h = Math.round(m / 60);
      if (h < 48) return h + " h ago";
      return Math.round(h / 24) + " days ago";
    },
  };

  const store = {
    get(key, dflt) {
      try {
        const raw = localStorage.getItem("llmbench." + key);
        return raw == null ? dflt : JSON.parse(raw);
      } catch (e) {
        return dflt;
      }
    },
    set(key, val) {
      try {
        localStorage.setItem("llmbench." + key, JSON.stringify(val));
      } catch (e) {
        /* storage unavailable: ignore */
      }
    },
  };

  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const seriesColor = (i) => cssVar("--series-" + ((i % 8) + 1));

  // ---------------------------------------------------------------- data

  async function fetchJson(url) {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) {
      const err = new Error("HTTP " + res.status + " for " + url);
      err.status = res.status;
      throw err;
    }
    return res.json();
  }

  // Data sources: "live" = served by `./bench dashboard` (api/db, api/raw/<id>);
  // "static" = a folder made by `./bench publish` on any web server (data/results.json, data/raw/<id>.json);
  BL.dataMode = null;
  async function loadDb() {
    // Folders written by `./bench publish` carry <meta name="bench-static">: skip probing for the live API.
    if (!BL.dataMode && document.querySelector('meta[name="bench-static"]')) BL.dataMode = "static";
    if (BL.dataMode !== "static") {
      try {
        const db = await fetchJson("api/db");
        BL.dataMode = "live";
        return db;
      } catch (e) {
        // no API here (404, or a static host answering with an HTML page): try the published snapshot
      }
    }
    // Static copy: fetch the JSON on a web server; on file:// browsers block fetch(), so load data/results.js instead.
    try {
      const db = location.protocol === "file:" ? await loadScriptData("data/results.js", () => window.BENCH_DB)
                                              : await fetchJson("data/results.json").catch(() => loadScriptData("data/results.js", () => window.BENCH_DB));
      BL.dataMode = "static";
      return db;
    } catch (e) {
      BL.dataMode = null;
      throw new Error("No data found: neither api/db (./bench dashboard --live) nor data/results.json (./bench publish / ./bench dashboard) is available here.");
    }
  }

  // Loads a data script (works on file://) and returns what `pick` reads from window afterwards.
  function loadScriptData(src, pick) {
    return new Promise((resolve, reject) => {
      const el = document.createElement("script");
      el.src = src + "?t=" + Date.now();   // cache-buster so Refresh sees a regenerated copy
      el.onload = () => { el.remove(); const v = pick(); v ? resolve(v) : reject(new Error("No data in " + src)); };
      el.onerror = () => { el.remove(); reject(new Error("Could not load " + src)); };
      document.head.appendChild(el);
    });
  }

  const rawCache = new Map();
  async function loadRaw(runId) {
    if (rawCache.has(runId)) return rawCache.get(runId);
    const id = encodeURIComponent(runId);
    const url = BL.dataMode === "static" ? "data/raw/" + id + ".json" : "api/raw/" + id;
    const fromScript = () => loadScriptData("data/raw/" + id + ".js", () => (window.BENCH_RAW || {})[runId]);
    const p = (BL.dataMode === "static" && location.protocol === "file:" ? fromScript()
      : fetchJson(url).catch((e) => (BL.dataMode === "static" ? fromScript() : Promise.reject(e)))).catch((e) => {
      rawCache.delete(runId);
      throw e;
    });
    rawCache.set(runId, p);
    return p;
  }

  // ---------------------------------------------------------------- run values
  // Prefer run.summary.<key>; fall back to values derived from tests/memory if missing.
  function tmed(run, test, mode, turnIdx, field) {
    const t = get(run, "tests." + test + "." + mode);
    if (!t || !Array.isArray(t.turns)) return null;
    const turn = turnIdx === "last" ? t.turns[t.turns.length - 1] : t.turns[turnIdx];
    const v = turn && turn[field];
    if (isNum(v)) return v;
    return v && isNum(v.median) ? v.median : null;
  }
  const FALLBACK = {
    short_off_ttft_s: (r) => tmed(r, "short", "off", 0, "ttft_s"),
    short_off_decode_tps: (r) => tmed(r, "short", "off", 0, "decode_tps"),
    short_off_prefill_tps: (r) => tmed(r, "short", "off", 0, "prefill_tps"),
    short_high_ttft_s: (r) => tmed(r, "short", "high", 0, "ttft_s"),
    short_high_first_visible_s: (r) => tmed(r, "short", "high", 0, "first_visible_s"),
    short_high_decode_tps: (r) => tmed(r, "short", "high", 0, "decode_tps"),
    long_off_ttft_s: (r) => tmed(r, "long", "off", 0, "ttft_s"),
    long_off_prefill_tps: (r) => tmed(r, "long", "off", 0, "prefill_tps"),
    long_off_decode_tps: (r) => tmed(r, "long", "off", 1, "decode_tps"),
    long_off_followup_ttft_s: (r) => tmed(r, "long", "off", 1, "ttft_s"),
    long_off_recall: (r) => get(r, "tests.long.off.quality.recall"),
    long_high_first_visible_s: (r) => tmed(r, "long", "high", 0, "first_visible_s"),
    long_high_decode_tps: (r) => tmed(r, "long", "high", 1, "decode_tps"),
    long_high_recall: (r) => get(r, "tests.long.high.quality.recall"),
    extraction_off_accuracy: (r) => get(r, "tests.extraction.off.quality.accuracy"),
    extraction_off_total_s: (r) => tmed(r, "extraction", "off", 0, "total_s"),
    extraction_high_accuracy: (r) => get(r, "tests.extraction.high.quality.accuracy"),
    extraction_high_total_s: (r) => tmed(r, "extraction", "high", 0, "total_s"),
    cold_load_s: (r) => get(r, "cold_start.cycles.0.load_time_s"),
    warm_load_s: (r) => get(r, "cold_start.cycles.1.load_time_s"),
    cold_first_ttft_s: (r) => get(r, "cold_start.cycles.0.first_ttft_s"),
    warm_ttft_s: (r) => get(r, "cold_start.warm_ttft_s"),
    mem_loaded_gb: (r) => {
      const b = get(r, "memory.snapshots.loaded_empty");
      return isNum(b) ? b / GB : null;
    },
    mem_long_gb: (r) => {
      const b = get(r, "memory.snapshots.after_long_prompt");
      return isNum(b) ? b / GB : null;
    },
    mem_peak_gb: (r) => {
      const b = get(r, "memory.peak_bytes");
      return isNum(b) ? b / GB : null;
    },
  };
  function sv(run, key) {
    if (!run) return null;
    const v = run.summary ? run.summary[key] : undefined;
    if (isNum(v)) return v;
    const f = FALLBACK[key];
    const d = f ? f(run) : null;
    return isNum(d) ? d : null;
  }

  // Scored answers (recall questions, the extraction answer) that never arrived because thinking used the whole
  // output budget, for one test/mode: { n, total, text } or null. Those count as wrong, so the score then reflects
  // the thinking budget rather than wrong answers.
  function noAnswer(run, test, mode) {
    const n = sv(run, test + "_" + mode + "_no_answer_scored");
    if (!isNum(n) || n <= 0) return null;
    const total = sv(run, test + "_" + mode + "_scored_answers");
    return { n, total, text: n + (isNum(total) ? " of " + total : "") + " answer" + (n === 1 && !isNum(total) ? "" : "s") + " never arrived: ran out of thinking budget" };
  }

  // ---------------------------------------------------------------- public scores
  const CATEGORIES = ["reasoning", "coding", "agentic", "math", "vision", "knowledge"];
  const CATEGORY_LABEL = {
    reasoning: "Reasoning", coding: "Coding", agentic: "Agentic", math: "Math", vision: "Vision", knowledge: "Knowledge",
    long_context: "Long context", instruction_following: "Instruction following", other: "Other",
  };
  // Benchmarks usable for averaging: percentage-like scores 0..100.
  function isPctScore(b) {
    return b && isNum(b.score) && (b.unit == null || b.unit === "%" || b.unit === "") && b.score >= 0 && b.score <= 100;
  }
  // One entry per benchmark name; "exact" (this quant) wins over "base". Low-effort scores (effort_end "min", kept
  // beside the main highest-effort score when a source ran several reasoning efforts) are left out here.
  function dedupeBenchmarks(list) {
    const byName = new Map();
    for (const b of list || []) {
      if (!b || !b.name || b.effort_end === "min") continue;
      const prev = byName.get(b.name);
      if (!prev || (prev.applies_to !== "exact" && b.applies_to === "exact")) byName.set(b.name, b);
    }
    return [...byName.values()];
  }
  // Low-effort scores by benchmark name (see dedupeBenchmarks).
  function lowEffortScores(list) {
    return new Map((list || []).filter((b) => b && b.name && b.effort_end === "min").map((b) => [b.name, b]));
  }
  function categoryScores(pub) {
    const out = {};
    const all = [...CATEGORIES, "long_context", "instruction_following", "other"];
    const bms = dedupeBenchmarks(pub && pub.benchmarks).filter(isPctScore);
    for (const c of all) {
      const m = mean(bms.filter((b) => b.category === c).map((b) => b.score));
      out[c] = m;
    }
    return out;
  }

  // ---------------------------------------------------------------- index
  // Builds rows: one per (model_uid, machine_id) using the latest complete run
  // (falls back to the latest partial run, flagged). Models with no runs get one row.
  function buildIndex(db) {
    db = db || {};
    const models = db.models || {};
    const machines = db.machines || {};
    const runs = Array.isArray(db.runs) ? db.runs.slice() : [];
    const pub = db.public || {};
    const ts = (r) => r.started_at || r.finished_at || "";
    runs.sort((a, b) => (ts(a) < ts(b) ? 1 : ts(a) > ts(b) ? -1 : 0)); // newest first

    const runsByModel = new Map();
    for (const r of runs) {
      if (!r || !r.model_uid) continue;
      if (!runsByModel.has(r.model_uid)) runsByModel.set(r.model_uid, []);
      runsByModel.get(r.model_uid).push(r);
    }
    const uids = new Set([...Object.keys(models), ...runsByModel.keys()]);
    const rows = [];
    for (const uid of uids) {
      const model = models[uid] || { model_uid: uid, display_name: uid };
      const mruns = runsByModel.get(uid) || [];
      const p = pub[uid] || null;
      const cats = categoryScores(p);
      const byMachine = new Map();
      for (const r of mruns) {
        const k = r.machine_id || "";
        if (!byMachine.has(k)) byMachine.set(k, []);
        byMachine.get(k).push(r);
      }
      if (byMachine.size === 0) {
        rows.push({ key: uid + "|", uid, model, machineId: null, machine: null, run: null, runStatus: "none", pub: p, cats });
        continue;
      }
      for (const [mid, list] of byMachine) {
        const complete = list.find((r) => r.status === "complete");
        const partial = list.find((r) => r.status === "partial");
        const run = complete || partial || null;
        rows.push({
          key: uid + "|" + mid, uid, model, machineId: mid || null, machine: machines[mid] || null,
          run, runStatus: complete ? "complete" : partial ? "partial" : "failed", pub: p, cats,
        });
      }
    }
    const machineIds = [...new Set(runs.map((r) => r.machine_id).filter(Boolean))];
    return { db, models, machines, runs, pub, runsByModel, rows, machineIds };
  }

  const MAX_COMPARE = 8;   // the categorical palette has 8 distinct colours
  const PLATFORM = { macos: "Mac", darwin: "Mac", windows: "Win", linux: "Linux" };
  function platformText(row) {
    const m = row && row.machine;
    if (!m || !m.os) return DASH;
    return esc(PLATFORM[String(m.os).toLowerCase()] || m.os);
  }
  // Legend label that tells otherwise-identical names apart: name · engine · format (· machine when several).
  function seriesLabel(row, rows) {
    const m = row.model || {};
    const parts = [modelName(m), ENGINE_LABEL[m.engine] || m.engine, m.format ? formatName(m.format) : null];
    const same = (rows || []).filter((r) => r !== row && modelName(r.model) === modelName(m) && r.model.engine === m.engine &&
      String(r.model.format) === String(m.format));
    if (same.length && same.some((r) => r.uid !== row.uid) && m.quantization && m.quantization.name) parts.push(m.quantization.name);
    const machines = new Set((rows || []).map((r) => r.machineId));
    if (machines.size > 1 && row.machine) parts.push(row.machine.label || row.machineId);
    return parts.filter(Boolean).join(" · ");
  }
  // A name the engine used earlier for the same file (merged server-side) maps to its current name.
  function canonicalUid(idx, uid) {
    const a = (idx.db && idx.db.aliases) || {};
    return a[uid] || uid;
  }
  // Selection keys identify a model on a machine ("<uid>|<machine_id>"); bare uids are still accepted.
  function rowForKey(idx, key, machine) {
    const [u, ...rest] = key.split("|");
    key = [canonicalUid(idx, u), ...rest].join("|");
    if (key.includes("|")) {
      const exact = idx.rows.find((r) => r.key === key);
      if (exact) return exact;
      key = key.split("|")[0];
    }
    const cands = idx.rows.filter((r) => r.uid === key);
    return cands.find((r) => machine && r.machineId === machine) || cands.find((r) => r.runStatus === "complete") || cands[0] || null;
  }

  function machineLabel(idx, id) {
    if (!id) return DASH;
    const m = idx.machines[id];
    return (m && m.label) || id;
  }

  // ---------------------------------------------------------------- metrics
  // better: "high" | "low" | null (not ranked)
  const M = (key, label, opts) => Object.assign({ key, label, better: null, fmt: fmt.text, unit: "" }, opts);
  const sum = (k) => (row) => sv(row.run, k);
  // Thousands of tokens the way context windows are configured (32k = 32,768; 112k = 114,688; 128k = 131,072).
  const fmtTok = (v) => (!isNum(v) ? DASH : v === 0 ? "none" : v >= 1024 ? Math.round(v / 1024) + "k" : String(Math.round(v)));

  // Safe max context: the long-context test gives (tokens, peak memory while handling them); memory above
  // "loaded" is scaled linearly with context (KV cache + the temporary reading spike). Peaks before the long
  // test don't depend on context and act as a floor. Extrapolations beyond the tested length are flagged.
  // Memory budgets for the safe-context estimate. The headline value leaves a fixed amount for the
  // operating system and apps (RAM − 8 GB); the percentages are shown alongside for comparison.
  const SAFE_HEADROOM_GB = 8;
  const SAFE_MAIN = { freeGB: SAFE_HEADROOM_GB };
  const SAFE_BUDGETS = [0.6, 0.75, 0.85, SAFE_MAIN];
  const budgetLabel = (spec, ram) => (typeof spec === "number" ? Math.round(spec * 100) + "% of RAM" : "RAM − " + spec.freeGB + " GB") +
    (isNum(ram) ? " (" + (typeof spec === "number" ? ram * spec : ram - spec.freeGB).toFixed(0) + " GB)" : "");

  // Inputs of the context/memory model from a run: memory above "loaded" grows linearly with context
  // (KV cache + temporary reading spike), measured at the long-document test; earlier peaks are a floor.
  function ctxModel(row) {
    const s = (k) => sv(row && row.run, k);
    const loaded = s("mem_loaded_gb"), lp = s("mem_long_peak_gb"), lt = s("long_context_tokens"), floor = s("mem_other_peak_gb");
    const ram = row && row.machine && row.machine.memory_bytes ? row.machine.memory_bytes / GB : null;
    if (![loaded, lp, lt, ram].every(isNum) || lt <= 0) return null;
    return { loaded, lt, floor, ram, slope: Math.max(0, (lp - loaded) / lt), max: (row.model && row.model.max_context_length) || null };
  }
  // Estimated peak memory (GB) with `tokens` of context.
  function memAtContext(row, tokens) {
    const m = ctxModel(row);
    if (!m) return null;
    const est = m.loaded + m.slope * tokens;
    return isNum(m.floor) ? Math.max(est, m.floor) : est;
  }

  const WINDOW_128K = 131072, WINDOW_256K = 262144;

  function safeContext(row, spec) {
    const m = ctxModel(row);
    if (!m) return null;
    const label = budgetLabel(spec, m.ram);
    const budget = typeof spec === "number" ? m.ram * spec : m.ram - spec.freeGB;
    if (isNum(m.floor) && m.floor > budget) return { tokens: 0, budget, reason: "other", floor: m.floor, label };
    if (m.loaded >= budget) return { tokens: 0, budget, reason: "loaded", label };
    let tokens = m.slope > 0 ? (budget - m.loaded) / m.slope : Infinity;
    let capped = false;
    if (m.max && tokens > m.max) { tokens = m.max; capped = true; }
    if (!isFinite(tokens)) tokens = WINDOW_256K;
    tokens = Math.floor(tokens / 1024) * 1024;
    return { tokens, budget, capped, extrapolated: tokens > m.lt * 1.05, tested: m.lt, label };
  }
  // Table/compare display: "128k+" once a 128k window fits, else the estimate (e.g. "80k").
  function safeContextText(x) {
    if (!x) return DASH;
    return x.tokens >= WINDOW_128K ? "128k+" : fmtTok(x.tokens);
  }
  // Whether a standard window fits under the headline budget (RAM − 8 GB).
  function windowCheck(row, window) {
    const m = ctxModel(row);
    if (!m) return null;
    const name = fmtTok(window);
    if (m.max && m.max < window) return { name, text: name + " window: beyond the model's maximum (" + fmtTok(m.max) + ")", fits: null };
    const gb = memAtContext(row, window), budget = m.ram - SAFE_HEADROOM_GB;
    return { name, gb, fits: gb <= budget,
      text: name + " window: ~" + gb.toFixed(1) + " GB peak, " + (gb <= budget ? "fits" : "doesn't fit") + " within RAM − " + SAFE_HEADROOM_GB + " GB (" + budget.toFixed(0) + " GB) · estimated" };
  }
  function safeContextTip(row) {
    const all = SAFE_BUDGETS.map((spec) => safeContext(row, spec)).filter(Boolean);
    if (!all.length) return "";
    const one = (x) => (x.label === all[all.length - 1].label ? "▶ " : "   ") + x.label + ": " +
      (x.tokens === 0 ? (x.reason === "other" ? "doesn't fit (a non-context peak of " + x.floor.toFixed(1) + " GB already exceeds it)" : "doesn't fit") :
        "~" + fmtTok(x.tokens) + " tokens" + (x.capped ? " (the model's maximum)" : "") +
        (x.extrapolated ? " (estimated beyond the ~" + fmtTok(x.tested) + " tested)" : ""));
    const wins = [WINDOW_128K, WINDOW_256K].map((w) => windowCheck(row, w)).filter(Boolean).map((w) => "   " + w.text);
    return "Largest context keeping peak memory under:\n" + all.map(one).join("\n") + (wins.length ? "\n\nStandard windows:\n" + wins.join("\n") : "");
  }
  const METRICS = {
    short_decode: M("short_decode", "Decode", { get: sum("short_off_decode_tps"), better: "high", fmt: fmt.tps, unit: "tok/s", title: "Short test, reasoning off: decode tokens/s (turn 1 median)" }),
    short_ttft: M("short_ttft", "TTFT", { get: sum("short_off_ttft_s"), better: "low", fmt: fmt.sec, unit: "s", title: "Short test, reasoning off: time to first token" }),
    long_prefill: M("long_prefill", "Prefill", { get: sum("long_off_prefill_tps"), better: "high", fmt: fmt.tps, unit: "tok/s", title: "Long (64k+) test: prompt-processing tokens/s on the full document" }),
    long_ttft: M("long_ttft", "TTFT", { get: sum("long_off_ttft_s"), better: "low", fmt: fmt.sec, unit: "s", title: "Long (64k+) test: time to first token for the full document" }),
    long_decode: M("long_decode", "Decode", { get: sum("long_off_decode_tps"), better: "high", fmt: fmt.tps, unit: "tok/s", title: "Long test: decode tokens/s with full context" }),
    high_visible: M("high_visible", "1st visible", { get: sum("short_high_first_visible_s"), better: "low", fmt: fmt.sec, unit: "s", title: "Short test, thinking High: time until the first visible (non-reasoning) token" }),
    recall: M("recall", "Recall", {
      get: (r) => { const v = sv(r.run, "long_off_recall"); return isNum(v) ? v : sv(r.run, "long_high_recall"); },
      better: "high", fmt: fmt.pct01, title: "Long test: planted facts recalled (reasoning off)",
    }),
    extraction: M("extraction", "Extract acc.", {
      get: (r) => { const v = sv(r.run, "extraction_off_accuracy"); return isNum(v) ? v : sv(r.run, "extraction_high_accuracy"); },
      better: "high", fmt: fmt.pct01, title: "Extraction test: share of JSON fields correct (reasoning off)",
    }),
    mem_loaded: M("mem_loaded", "Loaded", { get: sum("mem_loaded_gb"), better: "low", fmt: fmt.gb, unit: "GB", title: "Engine memory with the model loaded and an empty context" }),
    ctx_peak: M("ctx_peak", "Ctx @ peak", { get: sum("peak_context_tokens"), better: null, fmt: fmtTok, unit: "tok", title: "Tokens in the model's context when memory peaked" }),
    safe_ctx: M("safe_ctx", "Safe ctx", { get: (r) => { const x = safeContext(r, SAFE_MAIN); return x ? x.tokens : null; }, better: "high", fmt: fmtTok, unit: "tok",
      title: "Estimated largest context that keeps peak memory below this machine's RAM minus " + SAFE_HEADROOM_GB + " GB (hover a value for 60%, 75% and 85%)" }),
    mem_peak: M("mem_peak", "Peak", { get: sum("mem_peak_gb"), better: "low", fmt: fmt.gb, unit: "GB", title: "Peak engine memory during the run" }),
  };
  for (const c of CATEGORIES) {
    METRICS["cat_" + c] = M("cat_" + c, CATEGORY_LABEL[c], {
      get: (r) => r.cats[c], better: "high", fmt: fmt.score, title: "Mean public " + CATEGORY_LABEL[c].toLowerCase() + " score (0–100)",
    });
  }

  // ---------------------------------------------------------------- fit score
  const FIT_DIMS = [
    { id: "speed", label: "Speed", desc: "Short decode tok/s, short TTFT", subs: [["short_decode", "high"], ["short_ttft", "low"]], dflt: 6 },
    { id: "long", label: "Long context", desc: "64k prefill, TTFT, decode, recall", subs: [["long_prefill", "high"], ["long_ttft", "low"], ["long_decode", "high"], ["recall", "high"]], dflt: 4 },
    { id: "intel", label: "Intelligence", desc: "Public reasoning, coding, math, knowledge", subs: [["cat_reasoning", "high"], ["cat_coding", "high"], ["cat_math", "high"], ["cat_knowledge", "high"]], dflt: 6 },
    { id: "agentic", label: "Agentic", desc: "Public agentic score, extraction accuracy", subs: [["cat_agentic", "high"], ["extraction", "high"]], dflt: 7 },
    { id: "memory", label: "Memory efficiency", desc: "Lower peak memory", subs: [["mem_peak", "low"]], dflt: 3 },
  ];

  function computeFit(rows, weights, penalizeMissing) {
    const subKeys = [...new Set(FIT_DIMS.flatMap((d) => d.subs.map((s) => s[0])))];
    const ranges = {};
    for (const k of subKeys) {
      const vals = rows.map((r) => METRICS[k].get(r)).filter(isNum);
      ranges[k] = vals.length ? [Math.min(...vals), Math.max(...vals)] : null;
    }
    const norm = (k, dir, v) => {
      const rg = ranges[k];
      if (!isNum(v) || !rg) return null;
      const [lo, hi] = rg;
      if (hi === lo) return 1;
      const t = (v - lo) / (hi - lo);
      return dir === "low" ? 1 - t : t;
    };
    const out = new Map();
    for (const r of rows) {
      let num = 0, den = 0, covered = 0, active = 0;
      const dims = {};
      for (const d of FIT_DIMS) {
        const w = Number(weights[d.id]) || 0;
        const v = mean(d.subs.map(([k, dir]) => norm(k, dir, METRICS[k].get(r))));
        dims[d.id] = v;
        if (w <= 0) continue;
        active++;
        if (isNum(v)) {
          num += w * v; den += w; covered++;
        } else if (penalizeMissing) {
          den += w;
        }
      }
      out.set(r.key, { score: den > 0 ? (num / den) * 100 : null, dims, covered, active });
    }
    return out;
  }

  // ---------------------------------------------------------------- misc helpers
  function modelName(m) {
    return (m && (m.display_name || m.key || m.model_uid)) || DASH;
  }
  function paramsText(m) {
    if (!m) return DASH;
    const tot = isNum(m.params_total_b) ? m.params_total_b : null;
    const act = isNum(m.params_active_b) ? m.params_active_b : null;
    const f = (x) => (x >= 10 ? Math.round(x) : x.toFixed(1)) + "B";
    const est = String(m.params_active_source || "").startsWith("estimated") ? "~" : "";   // estimate from the config
    if (m.is_moe || act != null) {
      if (tot != null && act != null) return f(tot) + " · " + est + f(act) + " active";
      if (act != null) return est + f(act) + " active";
    }
    if (tot != null) return f(tot);
    return m.params_string ? esc(m.params_string) : DASH;
  }
  function quantText(m) {
    if (!m) return DASH;
    const q = m.quantization || {};
    const parts = [];
    if (q.name) parts.push(esc(q.name));
    if (isNum(q.bits) && !(q.name && String(q.name).toLowerCase().includes(String(q.bits)))) parts.push(q.bits + "-bit");
    if (!parts.length && m.variant) parts.push(esc(m.variant));
    return parts.length ? parts.join(" · ") : DASH;
  }
  // Display name of a file format ("yuzu" is how LM Studio reports Splash packages).
  const formatName = (f) => (!f ? "" : ["yuzu", "splash"].includes(String(f).toLowerCase()) ? "Splash" : String(f).toUpperCase());
  function formatBadge(f) {
    if (!f) return '<span class="muted">' + DASH + "</span>";
    const k = String(f).toLowerCase();
    const cls = k === "mlx" ? "mlx" : k === "gguf" ? "gguf" : k === "splash" || k === "yuzu" ? "splash" : "";
    return '<span class="badge ' + cls + '">' + esc(formatName(f)) + "</span>";
  }
  const ENGINE_LABEL = { lmstudio: "LM Studio", ollama: "Ollama" };
  const engineText = (e) => (e ? esc(ENGINE_LABEL[e] || e) : DASH);

  const modelHref = (uid, runId) => "#/model/" + encodeURIComponent(uid) + (runId ? "?run=" + encodeURIComponent(runId) : "");
  const compareHref = (uids, machine) =>
    "#/compare?m=" + uids.map(encodeURIComponent).join(",") + (machine ? "&machine=" + encodeURIComponent(machine) : "");

  Object.assign(BL, {
    GB, DASH, isNum, esc, get, mean, fmt, store, cssVar, seriesColor, loadDb, loadRaw, sv, noAnswer,
    CATEGORIES, CATEGORY_LABEL, categoryScores, dedupeBenchmarks, lowEffortScores, isPctScore, buildIndex, machineLabel,
    METRICS, FIT_DIMS, computeFit, modelName, MAX_COMPARE, platformText, seriesLabel, rowForKey, canonicalUid, formatName, fmtTok, safeContext, safeContextTip, safeContextText, windowCheck, memAtContext, SAFE_MAIN, SAFE_BUDGETS, SAFE_HEADROOM_GB, paramsText, quantText, formatBadge, engineText, modelHref, compareHref,
    views: BL.views || {},
  });
})();
