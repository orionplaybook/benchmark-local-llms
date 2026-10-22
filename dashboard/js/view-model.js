/* Model detail view (#/model/<model_uid>[?run=<run_id>]). */
(function () {
  "use strict";
  const BL = window.BL;
  const { esc, fmt, isNum, DASH, get } = BL;

  const TESTS = [
    { id: "short", label: "Short multi-turn conversation", logTtft: true },
    { id: "long", label: "Long context (64k+ document)", logTtft: true },
    { id: "extraction", label: "Web-data extraction", logTtft: true },
  ];
  const SNAPSHOTS = [
    ["idle", "Idle"], ["loaded_empty", "Loaded (empty)"], ["after_short", "After short"],
    ["after_long_prompt", "After 64k prompt"], ["end", "End"],
  ];
  const KNOWN_PHASES = ["load", "cold_start", "short", "long", "extraction", "unload", "warmup"];

  function pickRun(idx, uid, runId) {
    const list = idx.runsByModel.get(uid) || [];
    if (runId) {
      const r = list.find((x) => x.run_id === runId);
      if (r) return r;
    }
    const pref = BL.tableState && BL.tableState.machine;
    const onPref = pref ? list.filter((r) => r.machine_id === pref) : [];
    for (const pool of [onPref, list]) {
      const r = pool.find((x) => x.status === "complete") || pool.find((x) => x.status === "partial");
      if (r) return r;
    }
    return list[0] || null;
  }

  const kv = (pairs) =>
    '<dl class="kv">' + pairs.map(([k, v]) => "<dt>" + esc(k) + "</dt><dd>" + (v == null || v === "" ? DASH : v) + "</dd>").join("") + "</dl>";
  const t = (v) => (v == null || v === "" ? DASH : esc(typeof v === "object" ? JSON.stringify(v) : String(v)));

  function statusBadge(s) {
    if (s === "complete") return '<span class="badge good">complete</span>';
    if (s === "partial") return '<span class="badge warn">partial</span>';
    if (s === "failed") return '<span class="badge bad">failed</span>';
    return '<span class="badge">' + esc(s || "unknown") + "</span>";
  }

  function identityCard(idx, m, run) {
    const caps = m.capabilities || {};
    const reas = caps.reasoning ? (caps.reasoning.allowed_options || []).join(", ") + (caps.reasoning.default ? " (default " + caps.reasoning.default + ")" : "") : null;
    const mach = run && idx.machines[run.machine_id];
    const ei = (run && run.engine_info) || {};
    const lc = (run && run.load_config) || {};
    const prof = (run && run.profile) || {};
    const maxTok = prof.max_tokens && typeof prof.max_tokens === "object"
      ? Object.entries(prof.max_tokens).map(([k, v]) => esc(k) + " " + esc(v)).join(", ") : t(prof.max_tokens);
    return (
      '<section class="card"><div class="card-head"><h2>Identity &amp; configuration</h2></div><div class="idgrid">' +
      "<div><h3>Model</h3>" + kv([
        ["Model UID", '<span class="mono">' + esc(m.model_uid) + "</span>" +
          ((m.aliases || []).length ? '<br><span class="muted" title="Same file (format, quantization and exact size); the engine reported it under another name in earlier runs">also listed as ' +
            m.aliases.map((a) => '<span class="mono">' + esc(a) + "</span>").join(", ") + "</span>" : "")],
        ["Engine", BL.engineText(m.engine)], ["Key", t(m.key)], ["Variant", t(m.variant)],
        ["Publisher", t(m.publisher)], ["Architecture", t(m.architecture)],
        ["Params", BL.paramsText(m) + (m.params_string && m.params_string !== BL.paramsText(m) ? ' <span class="muted">(' + esc(m.params_string) + ")</span>" : "")],
        ["MoE", moeText(m)], ["Format", BL.formatBadge(m.format)],
        ["Quantization", BL.quantText(m)], ["QAT", fmt.bool(m.qat)],
        ["Size", isNum(m.size_bytes) ? fmt.bytesGB(m.size_bytes) : DASH],
        ["Max context", fmt.int(m.max_context_length)],
        ["Vision", fmt.bool(caps.vision)], ["Tool use", fmt.bool(caps.tool_use)], ["Reasoning", reas ? esc(reas) : "none"],
        ["Fingerprint", m.fingerprint ? '<span class="mono" title="' + esc(m.fingerprint) + '">' + esc(String(m.fingerprint).slice(0, 12)) + "…</span>" : DASH],
        ["First / last seen", fmt.dateShort(m.first_seen) + " / " + fmt.dateShort(m.last_seen)],
      ]) + "</div>" +
      "<div><h3>Run &amp; engine</h3>" + (run ? kv([
        ["Run ID", '<span class="mono">' + esc(run.run_id) + "</span>"], ["Status", statusBadge(run.status)],
        ["Started", fmt.date(run.started_at)], ["Finished", fmt.date(run.finished_at)],
        ["Engine", t(ei.name) + (ei.version ? " " + esc(ei.version) : "")], ["Runtime", t(ei.runtime)], ["Base URL", t(ei.base_url)],
        ["Tool version", t(run.tool_version)], ["Suite version", t(run.suite_version)],
      ]) : '<p class="muted">No runs yet.</p>') + "</div>" +
      "<div><h3>Load config</h3>" + (run ? kv([
        ["Context length", fmt.int(lc.context_length)], ["Flash attention", fmt.bool(lc.flash_attention)],
        ["Eval batch size", t(lc.eval_batch_size)], ["KV cache on GPU", fmt.bool(lc.offload_kv_cache_to_gpu)],
        ["Experts", t(lc.num_experts)], ["Parallel", t(lc.parallel)],
        ...Object.entries(lc).filter(([k]) => !["context_length", "flash_attention", "eval_batch_size", "offload_kv_cache_to_gpu", "num_experts", "parallel"].includes(k)).map(([k, v]) => [k, t(v)]),
      ]) : '<p class="muted">—</p>') + "</div>" +
      "<div><h3>Profile &amp; machine</h3>" + (run ? kv([
        ["Profile", t(run.profile_name) + (run.profile_hash ? ' <span class="muted mono">' + esc(run.profile_hash) + "</span>" : "")],
        ["Context", fmt.int(prof.context_length)],
        ["Sampling", "temp " + t(prof.temperature) + ", top_p " + t(prof.top_p) + ", top_k " + t(prof.top_k) + ", seed " + t(prof.seed)],
        ["Repeats / warmup", t(prof.repeats) + " / " + t(prof.warmup)], ["Max tokens", maxTok],
        ["Machine", mach ? esc(mach.label || mach.machine_id) : t(run.machine_id)],
        ["Chip", mach ? t(mach.chip) : DASH],
        ["CPU / GPU cores", mach ? t(mach.cpu_cores) + (mach.cpu_cores_detail ? " (" + esc(mach.cpu_cores_detail) + ")" : "") + " / " + t(mach.gpu_cores) : DASH],
        ["Memory", mach && isNum(mach.memory_bytes) ? fmt.bytesGB(mach.memory_bytes) : DASH],
        ["Bandwidth", mach && get(mach, "specs_extra.memory_bandwidth_gbps") ? esc(mach.specs_extra.memory_bandwidth_gbps) + " GB/s" : DASH],
        ["OS", mach ? t([mach.os, mach.os_version, mach.arch].filter(Boolean).join(" ")) : DASH],
      ]) : '<p class="muted">—</p>') + "</div>" +
      "</div></section>"
    );
  }

  function kpis(run) {
    const sv = (k) => BL.sv(run, k);
    const recall = isNum(sv("long_off_recall")) ? sv("long_off_recall") : sv("long_high_recall");
    const tiles = [
      ["Short decode", fmt.tps(sv("short_off_decode_tps")), "tok/s"],
      ["Short TTFT", fmt.sec(sv("short_off_ttft_s")), "s"],
      ["64k prefill", fmt.tps(sv("long_off_prefill_tps")), "tok/s"],
      ["64k TTFT", fmt.sec(sv("long_off_ttft_s")), "s"],
      ["Peak memory", fmt.gb(sv("mem_peak_gb")), "GB"],
      ["Recall (64k)", fmt.pct01(recall), ""],
    ];
    return '<div class="kpis">' + tiles.map(([k, v, u]) => '<div class="kpi"><div class="k">' + k + '</div><div class="v">' + v + (v !== DASH && u ? "<small>" + u + "</small>" : "") + "</div></div>").join("") + "</div>";
  }

  function testTurnsTable(test) {
    const modes = ["off", "high"].filter((m) => test[m]);
    let h = '<div class="table-wrap"><table class="data compact"><thead><tr><th>Mode</th><th>Turn</th><th class="num">Prompt tok</th><th class="num">Completion</th><th class="num">Reasoning</th><th class="num">TTFT s</th><th class="num">1st visible s</th><th class="num">Prefill tok/s</th><th class="num">Decode tok/s</th><th class="num">Total s</th></tr></thead><tbody>';
    for (const mode of modes) {
      for (const tu of test[mode].turns || []) {
        const md = (f) => (tu[f] && isNum(tu[f].median) ? tu[f].median : isNum(tu[f]) ? tu[f] : null);
        h += "<tr><td>" + esc(mode) + "</td><td>" + esc(tu.turn) + ". " + esc(tu.label || "") + '</td><td class="num">' + fmt.int(tu.prompt_tokens) +
          '</td><td class="num">' + fmt.int(tu.completion_tokens) + '</td><td class="num">' + fmt.int(tu.reasoning_tokens) +
          '</td><td class="num">' + fmt.sec(md("ttft_s")) + '</td><td class="num">' + fmt.sec(md("first_visible_s")) +
          '</td><td class="num">' + fmt.tps(md("prefill_tps")) + '</td><td class="num">' + fmt.tps(md("decode_tps")) + '</td><td class="num">' + fmt.sec(md("total_s")) + "</td></tr>";
      }
    }
    return h + "</tbody></table></div>";
  }

  function moeText(m) {
    if (!m.is_moe) return fmt.bool(m.is_moe);
    const bits = ["yes"];
    if (isNum(m.moe_experts)) bits.push(m.moe_experts + " experts" + (isNum(m.moe_experts_per_token) ? ", " + m.moe_experts_per_token + " per token" : ""));
    if (isNum(m.params_active_b)) bits.push(m.params_active_b + "B active" + (m.params_active_source ? " (" + m.params_active_source + ")" : ""));
    return esc(bits.join(" · "));
  }

  // Per-fact recall of the long test (which planted facts were found, by position in the document).
  function factRecall(test) {
    const rows = [];
    for (const mode of ["off", "high"]) {
      const q = (test[mode] && test[mode].quality) || null;
      if (!q || !isNum(q.recall)) continue;
      if (!Array.isArray(q.facts) || !q.facts.length) {
        rows.push('<tr><td><span class="badge">' + esc(mode) + '</span></td><td colspan="4" class="muted">Not available for this run: answer texts are only kept for runs from 2026-10-21 on.</td></tr>');
        continue;
      }
      const sec = q.recall_by_section || {};
      const facts = q.facts.map((f) => '<span class="fact ' + (f.hits === f.of ? "ok" : f.hits ? "part" : "miss") + '" title="' + esc((f.section || "") + " · " + (isNum(f.position_pct) ? f.position_pct + "% into the document" : "") + " · expected: " + (f.expected || "")) + '">' +
        esc(f.id) + " " + f.hits + "/" + f.of + "</span>").join(" ");
      rows.push('<tr><td><span class="badge">' + esc(mode) + "</span></td>" + ["start", "middle", "end"].map((k) => '<td class="num">' + (isNum(sec[k]) ? fmt.pct01(sec[k]) : DASH) + "</td>").join("") + "<td>" + facts + "</td></tr>");
    }
    if (!rows.length) return "";
    return '<details class="turns"><summary>Recall per fact (start / middle / end of the document)</summary><div class="table-wrap"><table class="data compact"><thead><tr><th>Mode</th><th class="num">Start</th><th class="num">Middle</th><th class="num">End</th><th>Facts (found / repeats; hover for the expected answer)</th></tr></thead><tbody>' + rows.join("") + "</tbody></table></div></details>";
  }

  function qualityBadges(test, testName, run) {
    const out = [];
    for (const mode of ["off", "high"]) {
      const tr = test[mode];
      if (!tr) continue;
      const q = tr.quality || {};
      const applied = tr.reasoning_applied && tr.reasoning_applied !== mode ? ' <span class="muted">(applied: ' + esc(tr.reasoning_applied) + ")</span>" : "";
      const bits = [];
      if (isNum(q.recall)) bits.push("recall " + (isNum(q.recall_correct) ? q.recall_correct + "/" + q.recall_total : fmt.pct01(q.recall)));
      if (isNum(q.accuracy)) bits.push("accuracy " + fmt.pct01(q.accuracy) + (isNum(q.fields_correct) ? " (" + q.fields_correct + "/" + q.fields_total + " fields)" : ""));
      if (q.json_valid === true || q.json_valid === false) bits.push("JSON " + (q.json_valid ? "valid" : "invalid"));
      if (isNum(q.recall_reasoning)) bits.push("recall in reasoning text " + fmt.pct01(q.recall_reasoning));
      if (isNum(q.accuracy_reasoning)) bits.push("accuracy of reasoning text " + fmt.pct01(q.accuracy_reasoning));
      if (isNum(tr.cache_hit_ttft_s)) bits.push("cache-hit TTFT " + fmt.sec(tr.cache_hit_ttft_s) + " s");
      if (tr.totals && isNum(tr.totals.wall_s)) bits.push("wall " + fmt.sec(tr.totals.wall_s) + " s");
      const inR = tr.answer_in_reasoning_turns;
      const inRBadge = isNum(inR) && inR > 0 ? ' <span class="badge bad" title="The visible answer was empty and the whole answer was written in the reasoning (thinking) channel. Scores use the visible answer, which is what an agent receives.">' + inR + " answer(s) only in the reasoning channel</span>" : "";
      const na = run && BL.noAnswer(run, testName, mode);
      const naBadge = na ? ' <span class="badge warn" title="Thinking used the whole output budget before the model wrote a visible answer, so these count as wrong. A low score here says the model thinks longer than the budget allows, not that its answers were wrong.">' + esc(na.text) + "</span>" : "";
      out.push('<span class="badge">' + esc(mode) + "</span> " + (bits.length ? esc(bits.join(" · ")) : '<span class="muted">no quality data</span>') + applied + inRBadge + naBadge);
    }
    return '<div class="quality">' + out.map((x) => "<span>" + x + "</span>").join('<span class="muted">|</span>') + "</div>";
  }

  // Memory split into weights / context / reading spike, plus the suggested maximum context.
  function contextBreakdown(row) {
    if (!row || !row.run) return "";
    const s = (k) => BL.sv(row.run, k);
    const idle = s("mem_idle_gb"), loaded = s("mem_loaded_gb"), after = s("mem_long_gb"), lp = s("mem_long_peak_gb"), lt = s("long_context_tokens");
    const items = [];
    if (isNum(loaded) && isNum(idle)) items.push(["Weights + engine", fmt.gb(loaded - (idle || 0)) + " GB"]);
    if (isNum(after) && isNum(loaded) && isNum(lt) && lt > 0) items.push(["Context (KV cache)", "~" + fmt.gb((after - loaded) / lt * 10000) + " GB per 10k tokens"]);
    if (isNum(lp) && isNum(after)) items.push(["Reading spike at " + BL.fmtTok(lt), "+" + fmt.gb(Math.max(0, lp - after)) + " GB while the document was processed"]);
    if (isNum(s("peak_context_tokens"))) items.push(["Context at peak", "~" + BL.fmtTok(s("peak_context_tokens")) + " tokens (" + esc(((row.run.summary || {}).peak_phase || "").replace("/", ", ") || "?") + ")"]);
    for (const spec of BL.SAFE_BUDGETS) {
      const x = BL.safeContext(row, spec);
      if (x) items.push([(spec === BL.SAFE_MAIN ? "<b>Safe context, " : "Safe context, ") + esc(x.label) + (spec === BL.SAFE_MAIN ? "</b>" : ""), x.tokens === 0 ? "doesn't fit" :
        "~" + BL.fmtTok(x.tokens) + " tokens" + (x.capped ? " (model maximum)" : "") +
        (x.extrapolated ? " · estimated beyond the ~" + BL.fmtTok(x.tested) + " tested" : "")]);
    }
    for (const w of [131072, 262144].map((n) => BL.windowCheck(row, n)).filter(Boolean)) {
      items.push([esc(w.name) + " window", w.fits === null ? w.text.split(": ").slice(1).join(": ") :
        "~" + fmt.gb(w.gb) + " GB peak · " + (w.fits ? '<span class="badge good">fits</span>' : '<span class="badge bad">doesn&#39;t fit</span>') + " within RAM − " + BL.SAFE_HEADROOM_GB + " GB (estimated)"]);
    }
    if (!items.length) return "";
    return '<dl class="kv ctx-kv">' + items.map(([k, v]) => "<dt>" + k + "</dt><dd>" + v + "</dd>").join("") + "</dl>" +
      '<p class="small muted">Estimate: memory above “loaded” scaled linearly with context, from this run’s long-document test. Values beyond the tested length are extrapolations.</p>';
  }

  function render(el, ctx) {
    const idx = ctx.idx;
    const uid = BL.canonicalUid(idx, ctx.params.uid);
    const model = idx.models[uid] || (idx.runsByModel.has(uid) ? { model_uid: uid, display_name: uid } : null);
    if (!model) {
      el.innerHTML = '<div class="empty"><h2>Model not found</h2><p class="mono">' + esc(uid) + '</p><p><a href="#/">Back to models</a></p></div>';
      return;
    }
    const run = pickRun(idx, uid, ctx.params.run);
    const pub = idx.pub[uid] || null;
    const runs = idx.runsByModel.get(uid) || [];
    const sel = BL.tableState.selected;
    const selKey = uid + "|" + ((run && run.machine_id) || "");   // this model on this run's machine
    const inCompare = sel.has(selKey);

    let h = '<div class="page-head"><div><div class="small"><a href="#/">← Models</a></div><h1>' + esc(BL.modelName(model)) + "</h1>" +
      '<div class="sub"><span class="mono">' + esc(uid) + '</span> <span class="badges">' + BL.formatBadge(model.format) +
      (model.is_moe ? '<span class="badge">MoE</span>' : "") + (model.qat ? '<span class="badge good">QAT</span>' : "") +
      (run ? statusBadge(run.status) : "") + "</span>" +
      (run ? ' <span class="muted">· ' + esc(BL.machineLabel(idx, run.machine_id)) + " · " + fmt.date(run.started_at) + "</span>" : "") + "</div></div>" +
      '<div class="actions"><button type="button" id="toggle-compare"' + (!inCompare && sel.size >= BL.MAX_COMPARE ? " disabled" : "") + ">" +
      (inCompare ? "✓ In compare list" : "+ Add to compare") + "</button>" +
      (sel.size >= 2 || (sel.size >= 1 && !inCompare) ? '<a class="btn" href="' + BL.compareHref([...new Set([...sel, selKey])].slice(0, BL.MAX_COMPARE)) + '">Compare →</a>' : "") +
      "</div></div>";

    if (!run) {
      h += '<div class="notice">No runs yet for this model. Run <code>./bench run</code> to collect performance data.</div>';
    } else if (run.status !== "complete") {
      h += '<div class="notice ' + (run.status === "failed" ? "bad" : "") + '">This run is <b>' + esc(run.status) + "</b>" + (run.error ? ": " + esc(run.error) : "") + ". Some sections may be empty.</div>";
    }
    if (run) h += kpis(run);
    h += identityCard(idx, model, run);

    if (run) {
      h += '<div class="grid-2 stack-md section">' +
        '<section class="card"><div class="card-head"><h2>Cold vs. warm</h2><span class="hint">seconds</span></div>' +
        '<div class="grid-2"><div><div class="chart-title">Load time</div><div class="chart-box short"><canvas id="c-load"></canvas></div></div>' +
        '<div><div class="chart-title">Time to first token</div><div class="chart-box short"><canvas id="c-ttft"></canvas></div></div></div></section>' +
        '<section class="card"><div class="card-head"><h2>Memory snapshots</h2><span class="hint">engine footprint, GB' +
        (get(run, "memory.method") ? " · method: " + esc(run.memory.method) : "") + '</span></div><div class="chart-box short" id="mem-snap-box"><canvas id="c-memsnap"></canvas></div>' +
        '<div class="small muted" id="mem-extra"></div><div id="mem-ctx"></div></section></div>';

      h += '<section class="card section"><div class="card-head"><h2>Memory timeline</h2><span class="hint">sampled every ~250 ms, coloured by phase</span></div>' +
        '<div id="mem-tl"><div class="nodata">Loading timeline…</div></div></section>';

      h += '<section class="card section"><div class="card-head"><h2>Per-turn speed</h2><span class="hint">median of repeats</span><span class="right">' +
        BL.charts.legendHtml([{ label: "Reasoning off", color: BL.seriesColor(0) }, { label: "Thinking High", color: BL.seriesColor(1) }, { label: "High · first visible token", color: BL.seriesColor(2) }]) + "</span></div>";
      let anyTest = false;
      for (const T of TESTS) {
        const test = get(run, "tests." + T.id);
        if (!test || (!test.off && !test.high)) {
          h += '<div class="test-block"><h3>' + esc(T.label) + '</h3><div class="nodata">No data yet</div></div>';
          continue;
        }
        anyTest = true;
        h += '<div class="test-block"><h3>' + esc(T.label) + (test.high ? "" : ' <span class="badge">no Thinking High run</span>') + "</h3>" + qualityBadges(test, T.id, run) +
          '<div class="grid-2"><div><div class="chart-title">Time to first token (s)' + (T.logTtft ? ' <span class="muted">· log scale</span>' : "") + "</div>" +
          '<div class="chart-box short"><canvas id="c-' + T.id + '-ttft"></canvas></div></div>' +
          '<div><div class="chart-title">Decode (tok/s)</div><div class="chart-box short"><canvas id="c-' + T.id + '-dec"></canvas></div></div></div>' +
          '<details class="turns"><summary>Turn details</summary>' + testTurnsTable(test) + "</details>" + (T.id === "long" ? factRecall(test) : "") + "</div>";
      }
      if (!anyTest) h += '<div class="nodata">No test results in this run.</div>';
      h += "</section>";
    }

    // Intelligence
    h += '<div class="section"><h2>Intelligence (public benchmarks)</h2></div>';
    const bms = (pub && Array.isArray(pub.benchmarks) && pub.benchmarks) || [];
    if (!pub || !bms.length) {
      h += '<div class="card"><div class="nodata">No public benchmark data for this model yet.</div></div>';
    } else {
      const cats = BL.categoryScores(pub);
      const radarCats = [...BL.CATEGORIES, "long_context", "instruction_following"].filter((c) => isNum(cats[c]));
      h += '<div class="grid-2"><section class="card"><div class="card-head"><h2>By category</h2><span class="hint">mean score, 0–100</span></div>' +
        (radarCats.length >= 3 ? '<div class="chart-box tall"><canvas id="c-radar"></canvas></div>'
          : '<div class="table-wrap"><table class="data compact"><tbody>' + radarCats.map((c) => "<tr><td>" + esc(BL.CATEGORY_LABEL[c]) + '</td><td class="num">' + fmt.score(cats[c]) + "</td></tr>").join("") + "</tbody></table></div>" +
            '<p class="muted small">Radar needs at least 3 categories.</p>') +
        "</section>" +
        '<section class="card"><div class="card-head"><h2>Source model</h2></div>' + kv([
          ["Family", t(pub.family)], ["HF repo", pub.hf_repo ? '<a href="https://huggingface.co/' + esc(pub.hf_repo) + '" target="_blank" rel="noopener">' + esc(pub.hf_repo) + "</a>" : DASH],
          ["Base model", t(pub.base_model)], ["License", t(pub.license)], ["Released", t(pub.release_date)],
          ["Params", isNum(pub.params_b) ? esc(pub.params_b) + "B" : DASH], ["Context window", fmt.int(pub.context_window)],
          ["Modalities", t((pub.modalities || []).join(", "))],
          ["Links", (pub.links || []).map((l) => '<a href="' + esc(l.url) + '" target="_blank" rel="noopener">' + esc(l.label || l.url) + "</a>").join(" · ") || DASH],
          ["Updated", fmt.date(pub.updated_at)],
        ]) + '<div class="table-wrap"><table class="data compact"><thead><tr><th>Category</th><th class="num">Mean</th><th class="num">N</th></tr></thead><tbody>' +
        Object.keys(cats).filter((c) => isNum(cats[c])).map((c) => "<tr><td>" + esc(BL.CATEGORY_LABEL[c] || c) + '</td><td class="num">' + fmt.score(cats[c]) +
          '</td><td class="num">' + BL.dedupeBenchmarks(bms).filter((b) => b.category === c && BL.isPctScore(b)).length + "</td></tr>").join("") +
        "</tbody></table></div></section></div>";

      const order = (c) => { const i = [...BL.CATEGORIES, "long_context", "instruction_following", "other"].indexOf(c); return i < 0 ? 99 : i; };
      const low = BL.lowEffortScores(bms);
      const main = bms.filter((b) => b.effort_end !== "min");
      const sorted = main.slice().sort((a, b) => order(a.category) - order(b.category) || String(a.name).localeCompare(String(b.name)));
      const SOURCE_NAME = { api: "Artificial Analysis", leaderboard: "Epoch AI" };
      const eff = (pub && pub.efforts) || {};
      const effLine = Object.keys(eff).filter((k) => (eff[k] || []).length).map((k) => esc(SOURCE_NAME[k] || k) + ": " + esc(eff[k].join(", "))).join(" · ");
      const pct = (b) => (isNum(b.score) ? b.score.toFixed(1) + (b.unit && b.unit !== "%" ? " " + esc(b.unit) : b.unit === "%" ? "%" : "") : DASH);
      const effortCell = (b) => {
        const lo = low.get(b.name);
        return (b.effort ? esc(b.effort) : '<span class="muted">' + DASH + "</span>") +
          (lo ? ' <span class="muted small" title="' + esc("Lowest reasoning effort the source ran (" + (lo.source_column || "") + "); compare with your 'off' results") + '">· ' + esc(lo.effort || "low") + ": " + pct(lo) + "</span>" : "");
      };
      h += '<section class="card section"><div class="card-head"><h2>All benchmarks</h2><span class="hint">' + main.length + " scores · “exact” = this quantization, “base” = the unquantized model</span></div>" +
        (effLine ? '<p class="muted small">Reasoning effort of the public scores — ' + effLine + ". When a source ran several efforts, the main score is the highest (compare it with your Thinking High results) and the lowest is shown next to it (compare with your “off” results). Category scores use the main score.</p>" : "") +
        '<div class="table-wrap"><table class="data"><thead><tr><th>Category</th><th>Benchmark</th><th class="num">Score</th><th>Effort</th><th>Applies to</th><th>Method</th><th>Source</th><th>Retrieved</th></tr></thead><tbody>' +
        sorted.map((b) => "<tr><td>" + esc(BL.CATEGORY_LABEL[b.category] || b.category || DASH) + "</td><td><b>" + esc(b.name) + "</b>" +
          (b.raw_name && b.raw_name !== b.name ? ' <span class="muted small">' + esc(b.raw_name) + "</span>" : "") +
          '</td><td class="num">' + pct(b) + "</td><td>" + effortCell(b) +
          "</td><td>" + (b.applies_to === "exact" ? '<span class="badge good">exact</span>' : b.applies_to === "base" ? '<span class="badge">base</span>' : t(b.applies_to)) +
          '</td><td class="small">' + t(b.method) + "</td><td>" +
          (b.source_url ? '<a href="' + esc(b.source_url) + '" target="_blank" rel="noopener" title="' + esc(b.source_url) + '">' + esc(hostOf(b.source_url)) + " ↗</a>" : DASH) +
          '</td><td class="small muted">' + fmt.dateShort(b.retrieved_at) + "</td></tr>").join("") +
        "</tbody></table></div></section>";
    }

    // Run history + warnings
    h += '<div class="section"><section class="card"><div class="card-head"><h2>Run history</h2><span class="hint">' + runs.length + " run" + (runs.length === 1 ? "" : "s") + "</span></div>";
    if (!runs.length) h += '<div class="nodata">No runs yet. Run <code>./bench run</code> to collect data.</div>';
    else {
      h += '<div class="table-wrap"><table class="data compact"><thead><tr><th>Started</th><th>Status</th><th>Machine</th><th>Profile</th><th>Tool</th><th class="num">Decode</th><th class="num">64k prefill</th><th class="num">Peak GB</th></tr></thead><tbody>' +
        runs.map((r) => '<tr class="' + (run && r.run_id === run.run_id ? "selected" : "") + '"><td><a href="' + BL.modelHref(uid, r.run_id) + '">' + fmt.date(r.started_at) + "</a></td><td>" + statusBadge(r.status) +
          "</td><td>" + esc(BL.machineLabel(idx, r.machine_id)) + "</td><td>" + t(r.profile_name) + "</td><td>" + t(r.tool_version) +
          '</td><td class="num">' + fmt.tps(BL.sv(r, "short_off_decode_tps")) + '</td><td class="num">' + fmt.tps(BL.sv(r, "long_off_prefill_tps")) +
          '</td><td class="num">' + fmt.gb(BL.sv(r, "mem_peak_gb")) + "</td></tr>").join("") + "</tbody></table></div>";
    }
    h += "</section>";
    const warns = (run && run.warnings) || [];
    const cont = (run && run.contamination_events) || [];
    h += '<section class="card"><div class="card-head"><h2>Warnings &amp; contamination</h2><span class="hint">selected run</span></div>' +
      "<h3>Warnings</h3>" + (warns.length ? '<ul class="events">' + warns.map((w) => "<li>" + esc(w) + "</li>").join("") + "</ul>" : '<p class="muted">None.</p>') +
      '<h3 style="margin-top:10px">Contamination events</h3>' +
      (cont.length ? '<ul class="events">' + cont.map((c) => '<li><span class="muted mono">' + esc(c.t || "") + "</span> " + esc(c.detail || JSON.stringify(c)) + "</li>").join("") + "</ul>" : '<p class="muted">None recorded.</p>') +
      "</section></div>";

    el.innerHTML = h;

    // ---- events
    el.querySelector("#toggle-compare").addEventListener("click", () => {
      if (sel.has(selKey)) sel.delete(selKey);
      else if (sel.size < BL.MAX_COMPARE) sel.add(selKey);
      BL.store.set("selected", [...sel]);
      ctx.rerender();
    });

    // ---- charts
    if (run) drawRunCharts(el, run, { run, model, machine: idx.machines[run.machine_id] });
    if (pub && bms.length) {
      const cats = BL.categoryScores(pub);
      const radarCats = [...BL.CATEGORIES, "long_context", "instruction_following"].filter((c) => isNum(cats[c]));
      if (radarCats.length >= 3) {
        BL.charts.radar(el.querySelector("#c-radar"), {
          labels: radarCats.map((c) => BL.CATEGORY_LABEL[c]),
          datasets: [{ label: BL.modelName(model), data: radarCats.map((c) => cats[c]), color: BL.seriesColor(0) }],
        });
      }
    }
    if (run) drawTimeline(el, run, ctx);
  }

  function drawRunCharts(el, run, row) {
    const c1 = BL.seriesColor(0), c2 = BL.seriesColor(1);
    const cyc = get(run, "cold_start.cycles") || [];
    const cy = (n, f) => { const c = cyc.find((x) => x.cycle === n) || cyc[n - 1]; return c ? c[f] : null; };
    const loadVals = [cy(1, "load_time_s"), cy(2, "load_time_s")];
    if (loadVals.some(isNum)) {
      BL.charts.bar(el.querySelector("#c-load"), { labels: ["Cycle 1 (cold)", "Cycle 2"], datasets: [{ label: "Load time", data: loadVals, color: c1 }], fmt: (v) => fmt.sec(v) + " s" });
    } else el.querySelector("#c-load").parentElement.innerHTML = '<div class="nodata">No data yet</div>';
    const ttftVals = [cy(1, "first_ttft_s"), cy(2, "first_ttft_s"), get(run, "cold_start.warm_ttft_s"), get(run, "tests.short.off.cache_hit_ttft_s"), get(run, "tests.long.off.cache_hit_ttft_s")];
    if (ttftVals.some(isNum)) {
      BL.charts.bar(el.querySelector("#c-ttft"), {
        labels: [["First", "cycle 1"], ["First", "cycle 2"], ["Warm"], ["Cache hit", "short"], ["Cache hit", "64k"]],
        datasets: [{ label: "TTFT", data: ttftVals, color: c1 }], fmt: (v) => fmt.sec(v) + " s",
      });
    } else el.querySelector("#c-ttft").parentElement.innerHTML = '<div class="nodata">No data yet</div>';

    const snaps = get(run, "memory.snapshots") || {};
    const snapVals = SNAPSHOTS.map(([k]) => (isNum(snaps[k]) ? snaps[k] / BL.GB : null));
    if (snapVals.some(isNum)) {
      BL.charts.bar(el.querySelector("#c-memsnap"), { labels: SNAPSHOTS.map((s) => s[1]), datasets: [{ label: "Engine memory", data: snapVals, color: c1 }], fmt: (v) => fmt.gb(v) + " GB" });
    } else el.querySelector("#mem-snap-box").innerHTML = '<div class="nodata">No data yet</div>';
    const mem = run.memory || {};
    const extra = [];
    if (isNum(mem.peak_bytes)) extra.push("peak " + fmt.bytesGB(mem.peak_bytes));
    if (isNum(mem.system_used_peak_bytes)) extra.push("system used peak " + fmt.bytesGB(mem.system_used_peak_bytes) + (isNum(mem.system_total_bytes) ? " of " + fmt.bytesGB(mem.system_total_bytes) : ""));
    const swapWarn = (run.warnings || []).find((w) => w.startsWith("swap grew by"));
    if (isNum(mem.swap_used_delta_bytes)) extra.push("swap Δ " + fmt.bytesGB(mem.swap_used_delta_bytes));
    el.querySelector("#mem-extra").innerHTML = esc(extra.join(" · ")) + (swapWarn ? ' <span class="badge bad" title="' + esc(swapWarn) + '">swap: speeds may be lower than usual</span>' : "");
    const ctxBox = el.querySelector("#mem-ctx");
    if (ctxBox) ctxBox.innerHTML = contextBreakdown(row);

    for (const T of TESTS) {
      const test = get(run, "tests." + T.id);
      if (!test || (!test.off && !test.high)) continue;
      const base = test.off || test.high;
      const turns = (base.turns || []).map((tu) => tu.turn);
      const labels = (base.turns || []).map((tu) => ["T" + tu.turn, shorten(tu.label || "", 18)]);
      const series = (mode, field) => {
        const tr = test[mode];
        if (!tr) return null;
        return turns.map((n) => {
          const tu = (tr.turns || []).find((x) => x.turn === n);
          const v = tu && tu[field];
          return v && isNum(v.median) ? v.median : isNum(v) ? v : null;
        });
      };
      const ttftDs = [];
      if (test.off) ttftDs.push({ label: "Off · TTFT", data: series("off", "ttft_s"), color: c1 });
      if (test.high) ttftDs.push({ label: "High · TTFT", data: series("high", "ttft_s"), color: c2 });
      if (test.high) ttftDs.push({ label: "High · first visible", data: series("high", "first_visible_s"), color: BL.seriesColor(2) });
      BL.charts.bar(el.querySelector("#c-" + T.id + "-ttft"), { labels, datasets: ttftDs, log: T.logTtft, fmt: (v) => fmt.sec(v) + " s" });
      const decDs = [];
      if (test.off) decDs.push({ label: "Off", data: series("off", "decode_tps"), color: c1 });
      if (test.high) decDs.push({ label: "High", data: series("high", "decode_tps"), color: c2 });
      BL.charts.bar(el.querySelector("#c-" + T.id + "-dec"), { labels, datasets: decDs, fmt: (v) => fmt.tps(v) + " tok/s" });
    }
  }

  async function drawTimeline(el, run, ctx) {
    const box = el.querySelector("#mem-tl");
    let raw;
    try {
      raw = await BL.loadRaw(run.run_id);
    } catch (e) {
      if (!box.isConnected) return;
      box.innerHTML = '<div class="nodata">' + (e && e.status === 404 ? "No memory timeline recorded for this run." : "Could not load the raw trace (" + esc(e.message) + ").") + "</div>";
      return;
    }
    if (!box.isConnected || ctx.token !== BL.renderToken) return;
    // Samples taken while another model was loaded (the test was abandoned and restarted) don't count: shown as a gap.
    const pts = (raw && Array.isArray(raw.memory_timeline) ? raw.memory_timeline : []).filter((p) => p && isNum(p.t))
      .map((p) => (p.discarded ? { t: p.t, phase: p.phase, engine_bytes: null, system_used_bytes: null } : p));
    if (!pts.length) {
      box.innerHTML = '<div class="nodata">No memory timeline recorded for this run.</div>';
      return;
    }
    const phases = [];
    for (const p of pts) if (p.phase && !phases.includes(p.phase)) phases.push(p.phase);
    // Fixed slot per known phase (colour follows the phase, not its order); "idle" is muted.
    const extraPhases = phases.filter((p) => p !== "idle" && !KNOWN_PHASES.includes(p));
    const colorOf = (ph) => {
      if (!ph || ph === "idle") return BL.cssVar("--series-muted");
      const k = KNOWN_PHASES.indexOf(ph);
      if (k >= 0) return BL.seriesColor(k);
      return BL.seriesColor((KNOWN_PHASES.length + extraPhases.indexOf(ph)) % 8);
    };
    const legend = phases.map((p) => ({ label: p.replace(/_/g, " "), color: colorOf(p), kind: "line" }));
    if (pts.some((p) => isNum(p.system_used_bytes))) legend.push({ label: "system used", color: "transparent", kind: "dash" });
    box.innerHTML = BL.charts.legendHtml(legend) + '<div class="chart-box tall"><canvas id="c-memtl"></canvas></div>';
    BL.charts.memoryTimeline(box.querySelector("#c-memtl"), pts, colorOf);
  }

  function shorten(s, n) {
    return s.length > n ? s.slice(0, n - 1) + "…" : s;
  }
  function hostOf(u) {
    try { return new URL(u).hostname.replace(/^www\./, ""); } catch (e) { return u; }
  }

  BL.views.model = render;
})();
