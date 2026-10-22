/* Compare view (#/compare?m=uid1,uid2,uid3[&machine=id]). */
(function () {
  "use strict";
  const BL = window.BL;
  const { esc, fmt, isNum, DASH, get } = BL;

  const sv = (k) => (row) => BL.sv(row.run, k);
  const pctMetric = (k1, k2) => (row) => { const v = BL.sv(row.run, k1); return isNum(v) ? v : BL.sv(row.run, k2); };
  // Note for a quality score lowered by answers that never arrived (thinking ran out of budget). With a fallback
  // (off, else High) the note follows the mode the value came from.
  const naNote = (test, metric) => (row) => {
    const mode = metric && !isNum(BL.sv(row.run, test + "_off_" + metric)) ? "high" : metric ? "off" : "high";
    return BL.noAnswer(row.run, test, mode);
  };
  const ROWS = [
    { section: "Model" },
    { label: "Engine", html: (r) => BL.engineText(r.model.engine) },
    { label: "Platform", html: (r) => BL.platformText(r) + (r.machine ? ' <span class="muted small">' + esc(r.machine.label || r.machineId) + "</span>" : "") },
    { label: "Format", html: (r) => BL.formatBadge(r.model.format) },
    { label: "Quantization", html: (r) => BL.quantText(r.model) + (r.model.qat ? ' <span class="badge good">QAT</span>' : "") },
    { label: "Params", html: (r) => BL.paramsText(r.model) },
    { label: "Size", get: (r) => (isNum(r.model.size_bytes) ? r.model.size_bytes / BL.GB : null), fmt: fmt.gb, unit: "GB", better: "low" },
    { label: "Max context", get: (r) => r.model.max_context_length, fmt: fmt.int, better: "high" },
    { label: "Run", html: (r) => (r.run ? fmt.dateShort(r.run.started_at) + " · " + esc(r.run.status || "") : '<span class="muted">no runs yet</span>') },
    { section: "Speed — short conversation" },
    { label: "Decode (off)", get: sv("short_off_decode_tps"), fmt: fmt.tps, unit: "tok/s", better: "high" },
    { label: "Decode (High)", get: sv("short_high_decode_tps"), fmt: fmt.tps, unit: "tok/s", better: "high" },
    { label: "Prefill", get: sv("short_off_prefill_tps"), fmt: fmt.tps, unit: "tok/s", better: "high" },
    { label: "TTFT", get: sv("short_off_ttft_s"), fmt: fmt.sec, unit: "s", better: "low" },
    { label: "High: first visible token", get: sv("short_high_first_visible_s"), fmt: fmt.sec, unit: "s", better: "low" },
    { label: "High: reasoning tokens", get: sv("short_high_reasoning_tokens"), fmt: fmt.int, better: "low" },
    { section: "Speed — long context (64k+)" },
    { label: "Prefill", get: sv("long_off_prefill_tps"), fmt: fmt.tps, unit: "tok/s", better: "high" },
    { label: "TTFT (full document)", get: sv("long_off_ttft_s"), fmt: fmt.sec, unit: "s", better: "low" },
    { label: "Follow-up TTFT", get: sv("long_off_followup_ttft_s"), fmt: fmt.sec, unit: "s", better: "low" },
    { label: "Decode (off)", get: sv("long_off_decode_tps"), fmt: fmt.tps, unit: "tok/s", better: "high" },
    { label: "Decode (High)", get: sv("long_high_decode_tps"), fmt: fmt.tps, unit: "tok/s", better: "high" },
    { label: "High: first visible token", get: sv("long_high_first_visible_s"), fmt: fmt.sec, unit: "s", better: "low" },
    { section: "Load" },
    { label: "Cold load", get: sv("cold_load_s"), fmt: fmt.sec, unit: "s", better: "low" },
    { label: "Reload (cycle 2)", get: sv("warm_load_s"), fmt: fmt.sec, unit: "s", better: "low" },
    { label: "Cold first TTFT", get: sv("cold_first_ttft_s"), fmt: fmt.sec, unit: "s", better: "low" },
    { label: "Warm TTFT", get: sv("warm_ttft_s"), fmt: fmt.sec, unit: "s", better: "low" },
    { section: "Quality checks" },
    { label: "Recall (64k)", get: pctMetric("long_off_recall", "long_high_recall"), fmt: fmt.pct01, better: "high", note: naNote("long", "recall") },
    { label: "Recall (64k, High)", get: sv("long_high_recall"), fmt: fmt.pct01, better: "high", note: naNote("long") },
    { label: "Extraction accuracy", get: pctMetric("extraction_off_accuracy", "extraction_high_accuracy"), fmt: fmt.pct01, better: "high", note: naNote("extraction", "accuracy") },
    { label: "Extraction accuracy (High)", get: sv("extraction_high_accuracy"), fmt: fmt.pct01, better: "high", note: naNote("extraction") },
    { label: "Extraction time", get: sv("extraction_off_total_s"), fmt: fmt.sec, unit: "s", better: "low" },
    { section: "Memory" },
    { label: "Loaded (empty context)", get: sv("mem_loaded_gb"), fmt: fmt.gb, unit: "GB", better: "low" },
    { label: "After 64k prompt", get: sv("mem_long_gb"), fmt: fmt.gb, unit: "GB", better: "low" },
    { label: "Peak", get: sv("mem_peak_gb"), fmt: fmt.gb, unit: "GB", better: "low" },
    { label: "Context at peak", get: sv("peak_context_tokens"), fmt: BL.fmtTok, unit: "tokens" },
    { label: "Safe context (RAM − 8 GB)", get: (r) => { const x = BL.safeContext(r, BL.SAFE_MAIN); return x ? Math.min(x.tokens, 131072) : null; }, fmt: (v) => (v >= 131072 ? "128k+" : BL.fmtTok(v)), unit: "tokens", better: "high" },
    { label: "Peak at a 128k window", get: (r) => { const w = BL.windowCheck(r, 131072); return w && w.fits !== null ? w.gb : null; }, fmt: fmt.gb, unit: "GB (est.)", better: "low" },
    { label: "Peak at a 256k window", get: (r) => { const w = BL.windowCheck(r, 262144); return w && w.fits !== null ? w.gb : null; }, fmt: fmt.gb, unit: "GB (est.)", better: "low" },
    { label: "Safe context (75% RAM)", get: (r) => { const x = BL.safeContext(r, 0.75); return x ? x.tokens : null; }, fmt: BL.fmtTok, unit: "tokens", better: "high" },
    { section: "Public scores (mean, 0–100)" },
    ...BL.CATEGORIES.map((c) => ({ label: BL.CATEGORY_LABEL[c], get: (r) => r.cats[c], fmt: fmt.score, better: "high" })),
  ];

  function render(el, ctx) {
    const idx = ctx.idx;
    const keys = [...new Set((ctx.params.m || "").split(",").map((s) => s.trim()).filter(Boolean))].slice(0, BL.MAX_COMPARE);
    const machine = ctx.params.machine || null;
    const found = keys.map((k) => ({ k, r: BL.rowForKey(idx, k, machine) }));
    const rows = [...new Map(found.filter((f) => f.r).map((f) => [f.r.key, f.r])).values()];
    const color = (i) => BL.seriesColor(i);
    const missing = found.filter((f) => !f.r).map((f) => f.k.split("|")[0]);
    const lab = (r) => BL.seriesLabel(r, rows);

    const others = idx.rows.filter((r) => !rows.some((x) => x.key === r.key));
    const uniq = others.slice().sort((a, b) => BL.seriesLabel(a, idx.rows).localeCompare(BL.seriesLabel(b, idx.rows)));
    const addSel = rows.length < BL.MAX_COMPARE && uniq.length
      ? '<select id="add-model" aria-label="Add a model"><option value="">+ Add model…</option>' + uniq.map((r) => '<option value="' + esc(r.key) + '">' + esc(BL.seriesLabel(r, idx.rows)) + "</option>").join("") + "</select>"
      : "";

    let h = '<div class="page-head"><div><div class="small"><a href="#/">← Models</a></div><h1>Compare</h1><div class="sub">Up to ' + BL.MAX_COMPARE + ' models side by side' +
      (machine ? " · " + esc(BL.machineLabel(idx, machine)) : "") + "</div></div></div>" +
      '<div class="toolbar"><div class="model-chips">' +
      rows.map((r, i) => '<span class="model-chip"><span class="dot" style="background:' + color(i) + '"></span><a href="' + BL.modelHref(r.uid) + '">' + esc(lab(r)) +
        '</a><button type="button" data-remove="' + esc(r.key) + '" title="Remove" aria-label="Remove ' + esc(lab(r)) + '">×</button></span>').join("") +
      "</div>" + addSel + "</div>";
    if (missing.length) h += '<div class="notice">Not in the database: ' + missing.map((u) => '<span class="mono">' + esc(u) + "</span>").join(", ") + "</div>";

    if (rows.length < 2) {
      h += '<div class="empty"><h2>' + (rows.length ? "Add one more model" : "Pick models to compare") + "</h2><p>Select 2–' + BL.MAX_COMPARE + ' models with the checkboxes in the <a href=\"#/\">models table</a>, or use “Add model” above.</p></div>";
      el.innerHTML = h;
      bind(el, rows, machine);
      return;
    }

    // Key-metric table
    h += '<section class="card"><div class="card-head"><h2>Key metrics</h2><span class="hint">best value in each row highlighted</span></div><div class="table-wrap"><table class="data"><thead><tr><th>Metric</th>' +
      rows.map((r, i) => '<th class="model-col"><span class="swatch" style="background:' + color(i) + '"></span>' + esc(lab(r)) + "</th>").join("") + "</tr></thead><tbody>";
    for (const row of ROWS) {
      if (row.section) {
        h += '<tr><td colspan="' + (rows.length + 1) + '" style="background:var(--surface-2);font-weight:600;font-size:11.5px;color:var(--text-2)">' + esc(row.section) + "</td></tr>";
        continue;
      }
      let best = null;
      if (row.get && row.better) {
        const vals = rows.map(row.get).filter(isNum);
        if (vals.length > 1 && new Set(vals).size > 1) best = row.better === "high" ? Math.max(...vals) : Math.min(...vals);
      }
      h += "<tr><td>" + esc(row.label) + (row.unit ? ' <span class="muted">' + esc(row.unit) + "</span>" : "") + "</td>";
      for (const r of rows) {
        if (row.html) { h += '<td class="num">' + row.html(r) + "</td>"; continue; }
        const v = row.get(r);
        const na = row.note && isNum(v) ? row.note(r) : null;
        h += '<td class="num' + (best != null && v === best ? " best" : "") + (isNum(v) ? "" : " dim") + '">' + row.fmt(v) +
          (na ? ' <span class="badge warn" title="' + esc(na.text) + '. These count as wrong, so the score reflects the thinking budget rather than wrong answers.">' + na.n + (isNum(na.total) ? "/" + na.total : "") + " no answer</span>" : "") + "</td>";
      }
      h += "</tr>";
    }
    h += "</tbody></table></div></section>";

    const legend = BL.charts.legendHtml(rows.map((r, i) => ({ label: lab(r), color: color(i) })));
    h += '<div class="grid-2 section">' +
      '<section class="card"><div class="card-head"><h2>Decode speed</h2><span class="hint">tok/s, higher is better</span></div>' + legend + '<div class="chart-box"><canvas id="cc-dec"></canvas></div></section>' +
      '<section class="card"><div class="card-head"><h2>Prompt processing</h2><span class="hint">tok/s, higher is better</span></div>' + legend + '<div class="chart-box"><canvas id="cc-pre"></canvas></div></section>' +
      '<section class="card"><div class="card-head"><h2>Latency</h2><span class="hint">seconds, lower is better · log scale</span></div>' + legend + '<div class="chart-box"><canvas id="cc-lat"></canvas></div></section>' +
      '<section class="card"><div class="card-head"><h2>Memory</h2><span class="hint">GB, lower is better</span></div>' + legend + '<div class="chart-box"><canvas id="cc-mem"></canvas></div></section>' +
      "</div>";

    // Intelligence
    const allCats = [...BL.CATEGORIES, "long_context", "instruction_following"];
    const radarCats = allCats.filter((c) => rows.some((r) => isNum(r.cats[c])));
    const noPub = rows.filter((r) => !r.pub || !(r.pub.benchmarks || []).length);
    h += '<div class="section"><h2>Intelligence (public benchmarks)</h2></div>';
    if (noPub.length) h += '<div class="notice">No public benchmark data for: ' + noPub.map((r) => esc(lab(r))).join(", ") + ".</div>";

    const bmMaps = rows.map((r) => new Map(BL.dedupeBenchmarks(r.pub && r.pub.benchmarks).map((b) => [b.name, b])));
    const names = [...new Set(bmMaps.flatMap((m) => [...m.keys()]))];
    const catOf = (n) => { for (const m of bmMaps) if (m.has(n)) return m.get(n).category; return "other"; };
    const order = (c) => { const i = [...allCats, "other"].indexOf(c); return i < 0 ? 99 : i; };
    names.sort((a, b) => order(catOf(a)) - order(catOf(b)) || a.localeCompare(b));
    // "Shared" is judged among models that have any public data, so one model without data doesn't empty it.
    const withData = bmMaps.filter((m) => m.size > 0);
    const isShared = (n) => withData.length > 0 && withData.every((m) => m.has(n));
    const shared = withData.length >= 2 ? names.filter(isShared) : [];
    const partial = names.filter((n) => !shared.includes(n));

    const bmTable = (list, highlight) =>
      '<div class="table-wrap"><table class="data compact"><thead><tr><th>Benchmark</th><th>Category</th>' +
      rows.map((r, i) => '<th class="model-col"><span class="swatch" style="background:' + color(i) + '"></span>' + esc(lab(r)) + "</th>").join("") + "</tr></thead><tbody>" +
      list.map((n) => {
        const vals = bmMaps.map((m) => (m.has(n) ? m.get(n).score : null));
        const nums = vals.filter(isNum);
        const best = highlight && nums.length > 1 && new Set(nums).size > 1 ? Math.max(...nums) : null;
        return "<tr><td><b>" + esc(n) + '</b></td><td class="small muted">' + esc(BL.CATEGORY_LABEL[catOf(n)] || catOf(n)) + "</td>" +
          bmMaps.map((m, i) => {
            const b = m.get(n);
            if (!b) return '<td class="num dim">' + DASH + "</td>";
            const v = vals[i];
            const link = b.source_url ? ' <a href="' + esc(b.source_url) + '" target="_blank" rel="noopener" title="' + esc((b.method || "") + " · " + b.source_url) + '">↗</a>' : "";
            const ap = b.applies_to === "exact" ? ' <span class="badge good" title="Measured on this quantization">exact</span>' : "";
            return '<td class="num' + (best != null && v === best ? " best" : "") + '">' + (isNum(v) ? v.toFixed(1) : DASH) + ap + link + "</td>";
          }).join("") + "</tr>";
      }).join("") + "</tbody></table></div>";

    // Speed vs. intelligence: x = short-chat writing speed, y = mean public score over the categories every
    // compared model (with public data) has, bubble size = peak memory.
    const pubRows = rows.filter((r) => allCats.some((c) => isNum(r.cats[c])));
    const commonCats = pubRows.length ? allCats.filter((c) => pubRows.every((r) => isNum(r.cats[c]))) : [];
    const intel = (r) => (commonCats.length ? BL.mean(commonCats.map((c) => r.cats[c])) : null);
    const pts = rows.map((r, i) => ({ r, i, x: BL.sv(r.run, "short_off_decode_tps"), y: intel(r), m: BL.sv(r.run, "mem_peak_gb") }));
    const plotted = pts.filter((p) => isNum(p.x) && isNum(p.y));
    const notPlotted = pts.filter((p) => !(isNum(p.x) && isNum(p.y))).map((p) => esc(lab(p.r)));

    h += '<div class="grid-2"><section class="card"><div class="card-head"><h2>By category</h2><span class="hint">mean score, 0–100</span></div>' + legend +
      (radarCats.length >= 3 ? '<div class="chart-box tall"><canvas id="cc-radar"></canvas></div>' : '<div class="nodata">' + (radarCats.length ? "Not enough categories for a radar chart." : "No data yet") + "</div>") +
      "</section>" +
      '<section class="card"><div class="card-head"><h2>Speed vs. intelligence</h2><span class="hint">top-right is best · bubble size = peak memory</span></div>' + legend +
      (plotted.length ? '<div class="chart-box tall"><canvas id="cc-bubble"></canvas></div>' +
        '<p class="small muted">Horizontal: writing speed in the short chat (tok/s, thinking off). Vertical: average public score over the categories every compared model has (' +
        (commonCats.map((c) => esc(BL.CATEGORY_LABEL[c])).join(", ") || "none") + ').' + (notPlotted.length ? " Not plotted (missing speed or public scores): " + notPlotted.join(", ") + "." : "") + "</p>"
        : '<div class="nodata">Needs both speed results and public scores in a category all compared models share.</div>') +
      "</section></div>" +
      '<section class="card section"><div class="card-head"><h2>Shared benchmarks</h2><span class="hint">scored for every compared model that has public data · best highlighted</span></div>' +
      (shared.length ? bmTable(shared, true) : '<div class="nodata">No benchmark is shared by all compared models.</div>') + "</section>";
    h += '<section class="card section"><div class="card-head"><h2>Benchmarks only some models have</h2><span class="hint">not directly comparable</span></div>' +
      (partial.length ? bmTable(partial, false) : '<div class="nodata">None — all benchmarks are shared.</div>') + "</section>";

    el.innerHTML = h;
    bind(el, rows, machine);

    // ---- charts
    const ds = (fn) => rows.map((r, i) => ({ label: lab(r), data: fn(r), color: color(i) }));
    const s = (r, k) => BL.sv(r.run, k);
    BL.charts.bar(el.querySelector("#cc-dec"), {
      labels: [["Short", "off"], ["Short", "High"], ["64k", "off"], ["64k", "High"]],
      datasets: ds((r) => [s(r, "short_off_decode_tps"), s(r, "short_high_decode_tps"), s(r, "long_off_decode_tps"), s(r, "long_high_decode_tps")]),
      fmt: (v) => fmt.tps(v) + " tok/s",
    });
    BL.charts.bar(el.querySelector("#cc-pre"), {
      labels: [["Short", "prompt"], ["64k", "document"]],
      datasets: ds((r) => [s(r, "short_off_prefill_tps"), s(r, "long_off_prefill_tps")]),
      fmt: (v) => fmt.tps(v) + " tok/s",
    });
    BL.charts.bar(el.querySelector("#cc-lat"), {
      labels: [["Short", "TTFT"], ["High", "1st visible"], ["64k", "TTFT"], ["64k", "follow-up"], ["Cold", "load"], ["Reload"]],
      datasets: ds((r) => [s(r, "short_off_ttft_s"), s(r, "short_high_first_visible_s"), s(r, "long_off_ttft_s"), s(r, "long_off_followup_ttft_s"), s(r, "cold_load_s"), s(r, "warm_load_s")]),
      fmt: (v) => fmt.sec(v) + " s", log: true,
    });
    BL.charts.bar(el.querySelector("#cc-mem"), {
      labels: [["Loaded", "(empty)"], ["After", "64k prompt"], ["Peak"]],
      datasets: ds((r) => [s(r, "mem_loaded_gb"), s(r, "mem_long_gb"), s(r, "mem_peak_gb")]),
      fmt: (v) => fmt.gb(v) + " GB",
    });
    if (radarCats.length >= 3) {
      BL.charts.radar(el.querySelector("#cc-radar"), {
        labels: radarCats.map((c) => BL.CATEGORY_LABEL[c]),
        datasets: ds((r) => radarCats.map((c) => r.cats[c])),
      });
    }
    const bubbleCanvas = el.querySelector("#cc-bubble");
    if (bubbleCanvas && plotted.length) {
      const mems = plotted.map((p) => p.m).filter(isNum);
      const lo = mems.length ? Math.min(...mems) : 0, hi = mems.length ? Math.max(...mems) : 0;
      const radius = (m) => (!isNum(m) ? 8 : hi > lo ? 7 + 15 * (m - lo) / (hi - lo) : 12);
      const xs = plotted.map((p) => p.x), ys = plotted.map((p) => p.y);
      const pad = (a, b, f) => [Math.max(0, a - (b - a) * f - 2), b + (b - a) * f + 2];
      const nice = ([a, b], step) => [Math.max(0, Math.floor(a / step) * step), Math.ceil(b / step) * step];
      const [x0, x1] = nice(pad(Math.min(...xs), Math.max(...xs), 0.15), 10), [y0, y1] = nice(pad(Math.min(...ys), Math.max(...ys), 0.2), 5);
      const axis = (title, min, max) => ({ min, max, title: { display: true, text: title, color: BL.cssVar("--text-2"), font: { size: 11.5 } },
        grid: { color: BL.cssVar("--grid") }, ticks: { color: BL.cssVar("--text-3") } });
      BL.charts.make(bubbleCanvas, {
        type: "bubble",
        data: { datasets: plotted.map((p) => ({ label: lab(p.r), data: [{ x: p.x, y: p.y, r: radius(p.m), mem: p.m }],
          backgroundColor: BL.charts.hexA(color(p.i), 0.4), borderColor: color(p.i), borderWidth: 2 })) },
        options: {
          maintainAspectRatio: false,
          scales: { x: axis("Writing speed, short chat (tok/s)", x0, x1), y: axis("Average public score (0–100)", y0, Math.min(100, y1)) },
          plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => " " + c.dataset.label + ": " + c.raw.x.toFixed(1) + " tok/s · score " +
            c.raw.y.toFixed(1) + (isNum(c.raw.mem) ? " · peak " + c.raw.mem.toFixed(1) + " GB" : "") } } },
        },
      });
    }
  }

  function bind(el, rows, machine) {
    const go = (uids) => { location.hash = BL.compareHref(uids, machine); };
    el.querySelectorAll("[data-remove]").forEach((b) =>
      b.addEventListener("click", () => {
        const u = b.dataset.remove;
        BL.tableState.selected.delete(u);
        BL.store.set("selected", [...BL.tableState.selected]);
        go(rows.map((r) => r.key).filter((x) => x !== u));
      })
    );
    const add = el.querySelector("#add-model");
    if (add) add.addEventListener("change", () => { if (add.value) go([...rows.map((r) => r.key), add.value]); });
    // Keep the table's selection in sync with what is being compared.
    BL.tableState.selected = new Set(rows.map((r) => r.key));
    BL.store.set("selected", [...BL.tableState.selected]);
  }

  BL.views.compare = render;
})();
