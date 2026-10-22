/* Models table view (#/) with the fit-score panel. */
(function () {
  "use strict";
  const BL = window.BL;
  const { esc, fmt, isNum, METRICS, DASH } = BL;

  const state = (BL.tableState = BL.tableState || {
    q: "", engine: "", format: "", cap: "", machine: null,
    sort: BL.store.get("sort", { key: "fit", dir: "desc" }),
    selected: new Set(BL.store.get("selected", [])),
  });

  function weights() {
    const saved = BL.store.get("fitWeights", {}) || {};
    const w = {};
    for (const d of BL.FIT_DIMS) w[d.id] = isNum(saved[d.id]) ? saved[d.id] : d.dflt;
    return w;
  }
  function penalize() {
    return BL.store.get("fitPenalizeMissing", true) !== false;
  }

  // Columns: [id, header, group, metric|null, extra]
  const COLS = [
    { id: "check", group: "", head: "", cls: "check sticky-col", sortable: false },
    { id: "name", group: "Model", head: "Name", cls: "name sticky-col2", sort: (r) => BL.modelName(r.model).toLowerCase() },
    { id: "fit", group: "Model", head: "Fit", cls: "num", sort: (r, ctx) => ctx.fit.get(r.key).score, better: "high", title: "Weighted fit score (0–100) from the sliders above" },
    { id: "engine", group: "Model", head: "Engine", sort: (r) => r.model.engine || "" },
    { id: "platform", group: "Model", head: "Platform", sort: (r) => (r.machine && r.machine.os) || "", title: "Operating system of the computer the benchmark ran on" },
    { id: "format", group: "Model", head: "Format", sort: (r) => r.model.format || "" },
    { id: "quant", group: "Model", head: "Quant", sort: (r) => (r.model.quantization && r.model.quantization.bits) || null, title: "Quantization name, bits and QAT" },
    { id: "params", group: "Model", head: "Params", cls: "num", sort: (r) => (isNum(r.model.params_active_b) ? r.model.params_active_b : r.model.params_total_b), title: "Total parameters (active for MoE). Sorts by active params." },
    { id: "size", group: "Model", head: "Size", cls: "num", sort: (r) => r.model.size_bytes, title: "Model file size" },
    { id: "short_decode", group: "Short", metric: true, g: true },
    { id: "short_ttft", group: "Short", metric: true },
    { id: "long_prefill", group: "Long 64k", metric: true, g: true },
    { id: "long_ttft", group: "Long 64k", metric: true },
    { id: "long_decode", group: "Long 64k", metric: true },
    { id: "high_visible", group: "Thinking High", metric: true, g: true },
    { id: "recall", group: "Quality", metric: true, g: true },
    { id: "extraction", group: "Quality", metric: true },
    { id: "mem_loaded", group: "Memory", metric: true, g: true },
    { id: "mem_peak", group: "Memory", metric: true },
    { id: "ctx_peak", group: "Memory", metric: true },
    { id: "safe_ctx", group: "Memory", metric: true },
    ...BL.CATEGORIES.map((c, i) => ({ id: "cat_" + c, group: "Public scores", metric: true, g: i === 0 })),
  ];
  for (const c of COLS) {
    if (c.metric) {
      const m = METRICS[c.id];
      c.head = m.label + (m.unit ? ' <span class="muted">' + m.unit + "</span>" : "");
      c.cls = "num";
      c.sort = (r) => m.get(r);
      c.better = m.better;
      c.title = m.title;
    }
    if (c.sortable === undefined) c.sortable = true;
  }

  // Memory columns, coloured against the RAM of the machine the run happened on, matching the safe-context
  // rule: amber above 75% of RAM, red when less than SAFE_HEADROOM_GB (8 GB) would be left for everything else.
  const MEM_COLS = new Set(["mem_loaded", "mem_peak"]);
  const MEM_TIGHT = 0.75;
  function memLimit(r, gb) {
    const ram = r.machine && r.machine.memory_bytes ? r.machine.memory_bytes / BL.GB : null;
    if (!isNum(gb) || !ram) return null;
    const share = gb / ram;
    const tip = gb.toFixed(1) + " GB = " + Math.floor(share * 100) + "% of the " + Math.round(ram) + " GB RAM of " + (r.machine.label || r.machineId);
    const free = ram - gb;
    if (free < BL.SAFE_HEADROOM_GB) return { cls: "mem-danger", tip: tip + ": only " + free.toFixed(1) + " GB left for the system and apps (less than " + BL.SAFE_HEADROOM_GB + " GB); other apps or longer contexts may cause swapping" };
    if (share >= MEM_TIGHT) return { cls: "mem-tight", tip: tip + ": tight; " + free.toFixed(1) + " GB left for the system and apps" };
    return null;
  }

  function filteredRows(idx) {
    const q = state.q.trim().toLowerCase();
    return idx.rows.filter((r) => {
      const m = r.model;
      if (state.machine && r.machineId && r.machineId !== state.machine) return false;
      if (state.engine && m.engine !== state.engine) return false;
      if (state.format && String(m.format || "").toLowerCase() !== state.format) return false;
      if (state.cap) {
        const caps = m.capabilities || {};
        if (state.cap === "vision" && !caps.vision) return false;
        if (state.cap === "tool_use" && !caps.tool_use) return false;
        if (state.cap === "reasoning" && !caps.reasoning) return false;
        if (state.cap === "moe" && !m.is_moe) return false;
        if (state.cap === "public" && !(r.pub && r.pub.benchmarks && r.pub.benchmarks.length)) return false;
      }
      if (q) {
        const hay = [m.display_name, m.key, m.model_uid, m.publisher, m.architecture, m.variant, r.pub && r.pub.family].join(" ").toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }

  function cellHtml(col, r, ctx) {
    const m = r.model;
    switch (col.id) {
      case "check": {
        const on = state.selected.has(r.key);
        const dis = !on && state.selected.size >= BL.MAX_COMPARE;
        return '<input type="checkbox" class="pick" data-uid="' + esc(r.key) + '"' + (on ? " checked" : "") + (dis ? " disabled" : "") +
          ' aria-label="Select ' + esc(BL.modelName(m)) + ' for comparison">';
      }
      case "name": {
        const badges = [];
        if (r.runStatus === "none") badges.push('<span class="badge">no runs yet</span>');
        else if (r.runStatus === "partial") badges.push('<span class="badge warn">partial run</span>');
        else if (r.runStatus === "failed") badges.push('<span class="badge bad">failed</span>');
        if (m.is_moe) badges.push('<span class="badge">MoE</span>');
        const caps = m.capabilities || {};
        if (caps.vision) badges.push('<span class="badge" title="Vision input">vision</span>');
        if (caps.reasoning) badges.push('<span class="badge" title="Reasoning control">think</span>');
        const machine = ctx.showMachine && r.machineId ? '<span class="uid">' + esc(BL.machineLabel(ctx.idx, r.machineId)) + "</span>" : "";
        return '<a href="' + BL.modelHref(r.uid) + '">' + esc(BL.modelName(m)) + "</a> " + '<span class="badges">' + badges.join("") + "</span>" +
          '<span class="uid" title="' + esc(r.uid) + '">' + esc(r.uid) + "</span>" + machine;
      }
      case "fit": {
        const f = ctx.fit.get(r.key);
        if (!f || !isNum(f.score)) return DASH;
        const partial = f.covered < f.active ? ' title="Based on ' + f.covered + " of " + f.active + ' weighted dimensions (others have no data)"' : "";
        return '<span class="fit-cell"' + partial + ">" + Math.round(f.score) + (f.covered < f.active ? '<span class="muted">*</span>' : "") +
          '<span class="fit-bar"><span style="width:' + Math.max(2, f.score).toFixed(0) + '%"></span></span></span>';
      }
      case "engine": return BL.engineText(m.engine);
      case "platform": return BL.platformText(r);
      case "safe_ctx": {
        return BL.safeContextText(BL.safeContext(r, BL.SAFE_MAIN));
      }
      case "format": return BL.formatBadge(m.format);
      case "quant": return '<span class="nowrap">' + BL.quantText(m) + (m.qat ? ' <span class="badge good">QAT</span>' : "") + "</span>";
      case "params": return BL.paramsText(m);
      case "size": return isNum(m.size_bytes) ? fmt.gb(m.size_bytes / BL.GB) + ' <span class="muted">GB</span>' : DASH;
      default: {
        const met = METRICS[col.id];
        return met ? met.fmt(met.get(r)) : DASH;
      }
    }
  }

  function render(el, ctx0) {
    const idx = ctx0.idx;
    if (state.machine && !idx.machineIds.includes(state.machine)) state.machine = null;   // null/"" = all machines
    // Selections are row keys (model|machine); drop ones that no longer exist (also old uid-only entries).
    for (const k of [...state.selected]) if (!idx.rows.some((r) => r.key === k)) state.selected.delete(k);

    const engines = [...new Set(idx.rows.map((r) => r.model.engine).filter(Boolean))].sort();
    const formats = [...new Set(idx.rows.map((r) => String(r.model.format || "").toLowerCase()).filter(Boolean))].sort();
    const w = weights();

    const opt = (v, label, cur) => '<option value="' + esc(v) + '"' + (v === cur ? " selected" : "") + ">" + esc(label) + "</option>";
    el.innerHTML =
      '<div class="page-head"><div><h1>Models</h1><div class="sub" id="tbl-sub"></div></div></div>' +
      '<section class="card fit-card"><div class="fit-panel">' +
      '<div class="fit-intro"><h2>Fit score</h2><p>Weight what matters for your agent workload (Hermes, n8n…). Each metric is min–max normalized across the models shown; lower-is-better metrics are inverted. Score is 0–100.</p></div>' +
      '<div><div class="sliders">' +
      BL.FIT_DIMS.map((d) =>
        '<div class="slider"><label for="w-' + d.id + '">' + esc(d.label) + ' <span class="val" id="wv-' + d.id + '">' + w[d.id] + "</span></label>" +
        '<input type="range" min="0" max="10" step="1" id="w-' + d.id + '" data-dim="' + d.id + '" value="' + w[d.id] + '">' +
        '<div class="desc">' + esc(d.desc) + "</div></div>").join("") +
      "</div>" +
      '<div class="fit-options"><label class="inline"><input type="checkbox" id="fit-penalize"' + (penalize() ? " checked" : "") +
      '> Missing data counts as 0</label><button type="button" id="fit-reset">Reset weights</button><span class="muted">* = some weighted dimensions have no data</span></div>' +
      '<div class="fit-top" id="fit-top"></div></div></div></section>' +
      '<div class="toolbar">' +
      '<input type="search" id="f-q" placeholder="Filter by name, key, publisher…" value="' + esc(state.q) + '" aria-label="Filter models">' +
      '<select id="f-engine" aria-label="Engine">' + opt("", "All engines", state.engine) + engines.map((e) => opt(e, BL.ENGINE_LABEL_TEXT(e), state.engine)).join("") + "</select>" +
      '<select id="f-format" aria-label="Format">' + opt("", "All formats", state.format) + formats.map((f) => opt(f, BL.formatName(f), state.format)).join("") + "</select>" +
      '<select id="f-cap" aria-label="Capability">' + opt("", "Any capability", state.cap) + opt("tool_use", "Tool use", state.cap) + opt("reasoning", "Reasoning control", state.cap) +
      opt("vision", "Vision", state.cap) + opt("moe", "MoE", state.cap) + opt("public", "Has public scores", state.cap) + "</select>" +
      (idx.machineIds.length > 1
        ? '<select id="f-machine" aria-label="Machine">' + opt("", "All machines", state.machine || "") + idx.machineIds.map((id) => opt(id, BL.machineLabel(idx, id), state.machine)).join("") + "</select>"
        : "") +
      '<span class="spacer"></span><span class="count" id="sel-count"></span>' +
      '<button type="button" id="clear-sel">Clear</button><button type="button" class="primary" id="go-compare">Compare</button>' +
      "</div>" +
      '<div class="table-wrap" id="tbl"></div>' +
      '<div class="cell-legend"><span><i class="best"></i>best in column</span><span><i class="worst"></i>worst in column</span>' +
      '<span><i class="mem-tight"></i>memory above 75% of the machine\'s RAM</span><span><i class="mem-danger"></i>less than ' + BL.SAFE_HEADROOM_GB + ' GB of RAM left: close to the limit</span>' +
      '<span class="muted">Among the models shown; hover a memory value for its exact share.</span></div>';

    const update = () => {
      const rows = filteredRows(idx);
      const fit = BL.computeFit(rows, weights(), penalize());
      const ctx = { idx, fit, showMachine: idx.machineIds.length > 1 && !state.machine };
      const col = COLS.find((c) => c.id === state.sort.key) || COLS[2];
      const dir = state.sort.dir === "asc" ? 1 : -1;
      const sorted = rows.slice().sort((a, b) => {
        const va = col.sort(a, ctx), vb = col.sort(b, ctx);
        const na = va == null || va === "" || (typeof va === "number" && !isFinite(va));
        const nb = vb == null || vb === "" || (typeof vb === "number" && !isFinite(vb));
        if (na && nb) return 0;
        if (na) return 1; // missing always last
        if (nb) return -1;
        return (va < vb ? -1 : va > vb ? 1 : 0) * dir;
      });
      // Best value per metric column among shown rows.
      // Best (green) and worst (red) per column, among the rows shown. Memory columns are coloured by how
      // close they came to the RAM of the machine they ran on instead of worst (see memLimit below).
      const best = {}, worst = {};
      for (const c of COLS) {
        if (!c.better || c.id === "fit") continue;
        const vals = rows.map((r) => c.sort(r, ctx)).filter(isNum);
        if (vals.length > 1 && Math.max(...vals) !== Math.min(...vals)) {
          best[c.id] = c.better === "high" ? Math.max(...vals) : Math.min(...vals);
          if (!MEM_COLS.has(c.id) && vals.length > 2) worst[c.id] = c.better === "high" ? Math.min(...vals) : Math.max(...vals);
        }
      }

      document.getElementById("tbl-sub").textContent =
        rows.length + " of " + idx.rows.length + " models" +
        (state.machine ? " · " + BL.machineLabel(idx, state.machine) : idx.machineIds.length === 1 ? " · " + BL.machineLabel(idx, idx.machineIds[0]) : "") +
        " · latest complete run per model";

      // Top 3 by fit.
      const top = rows.filter((r) => isNum(fit.get(r.key).score)).sort((a, b) => fit.get(b.key).score - fit.get(a.key).score).slice(0, 3);
      document.getElementById("fit-top").innerHTML = top.length
        ? '<span class="muted small" style="align-self:center">Best fit:</span>' +
          top.map((r, i) => '<a class="fit-chip" href="' + BL.modelHref(r.uid) + '"><span class="muted">#' + (i + 1) + "</span> " + esc(BL.modelName(r.model)) + " <b>" + Math.round(fit.get(r.key).score) + "</b></a>").join("")
        : "";

      // Header
      const groups = [];
      for (const c of COLS) {
        const last = groups[groups.length - 1];
        if (last && last.name === c.group) last.span++;
        else groups.push({ name: c.group, span: 1, g: c.g, first: c });
      }
      let html = '<table class="data"><thead><tr class="group">' +
        groups.map((g) => '<th colspan="' + g.span + '" class="' + (g.g ? "g " : "") + (g.first.id === "check" ? "sticky-col" : g.first.id === "name" ? "" : "") + '">' + esc(g.name) + "</th>").join("") +
        "</tr><tr>";
      for (const c of COLS) {
        const active = state.sort.key === c.id;
        const arrow = active ? (state.sort.dir === "asc" ? "▲" : "▼") : "";
        html += '<th class="' + [c.cls || "", c.g ? "g" : "", c.sortable ? "sortable" : ""].join(" ") + '"' +
          (c.sortable ? ' data-sort="' + c.id + '" tabindex="0" aria-sort="' + (active ? (state.sort.dir === "asc" ? "ascending" : "descending") : "none") + '"' : "") +
          (c.title ? ' title="' + esc(c.title) + '"' : "") + ">" +
          (c.id === "check" ? "" : c.head) + (c.sortable ? ' <span class="arrow">' + arrow + "</span>" : "") + "</th>";
      }
      html += "</tr></thead><tbody>";
      if (!sorted.length) {
        html += '<tr><td colspan="' + COLS.length + '" class="nodata">No models match these filters.</td></tr>';
      }
      for (const r of sorted) {
        html += '<tr class="' + (state.selected.has(r.uid) ? "selected" : "") + '">';
        for (const c of COLS) {
          let cls = [c.cls || "", c.g ? "g" : ""];
          const v = c.sort ? c.sort(r, ctx) : null;
          const lim = MEM_COLS.has(c.id) ? memLimit(r, v) : null;
          if (lim) cls.push(lim.cls);                                   // close to this machine's RAM
          else if (best[c.id] != null && v === best[c.id]) cls.push("best");
          else if (worst[c.id] != null && v === worst[c.id]) cls.push("worst");
          let tipText = lim ? lim.tip : "";
          if (c.id === "safe_ctx") tipText = BL.safeContextTip(r);
          if (c.id === "ctx_peak" && isNum(v)) tipText = "Memory peaked at " + BL.fmt.gb(BL.sv(r.run, "mem_peak_gb")) + " GB with ~" + BL.fmtTok(v) +
            " tokens in context (" + ((r.run.summary || {}).peak_phase || "?") + "); loaded with a " + BL.fmtTok((r.run.load_config || {}).context_length) + " window";
          const tip = tipText ? ' title="' + esc(tipText) + '"' : "";
          html += '<td class="' + cls.join(" ") + '"' + tip + ">" + cellHtml(c, r, ctx) + "</td>";
        }
        html += "</tr>";
      }
      html += "</tbody></table>";
      document.getElementById("tbl").innerHTML = html;

      const n = state.selected.size;
      document.getElementById("sel-count").textContent = n ? n + " of " + BL.MAX_COMPARE + " selected" : "Select up to " + BL.MAX_COMPARE + " to compare";
      document.getElementById("go-compare").disabled = n < 2;
      document.getElementById("clear-sel").hidden = n === 0;
    };

    // ---- events
    el.querySelectorAll('input[type="range"]').forEach((inp) =>
      inp.addEventListener("input", () => {
        const w2 = weights();
        w2[inp.dataset.dim] = Number(inp.value);
        BL.store.set("fitWeights", w2);
        document.getElementById("wv-" + inp.dataset.dim).textContent = inp.value;
        update();
      })
    );
    el.querySelector("#fit-penalize").addEventListener("change", (e) => {
      BL.store.set("fitPenalizeMissing", e.target.checked);
      update();
    });
    el.querySelector("#fit-reset").addEventListener("click", () => {
      const d = {};
      for (const x of BL.FIT_DIMS) {
        d[x.id] = x.dflt;
        el.querySelector("#w-" + x.id).value = x.dflt;
        el.querySelector("#wv-" + x.id).textContent = x.dflt;
      }
      BL.store.set("fitWeights", d);
      update();
    });
    el.querySelector("#f-q").addEventListener("input", (e) => { state.q = e.target.value; update(); });
    el.querySelector("#f-engine").addEventListener("change", (e) => { state.engine = e.target.value; update(); });
    el.querySelector("#f-format").addEventListener("change", (e) => { state.format = e.target.value; update(); });
    el.querySelector("#f-cap").addEventListener("change", (e) => { state.cap = e.target.value; update(); });
    const fm = el.querySelector("#f-machine");
    if (fm) fm.addEventListener("change", (e) => { state.machine = e.target.value; update(); });

    const tbl = el.querySelector("#tbl");
    const doSort = (th) => {
      const k = th.dataset.sort;
      if (state.sort.key === k) state.sort.dir = state.sort.dir === "asc" ? "desc" : "asc";
      else {
        const c = COLS.find((x) => x.id === k);
        state.sort = { key: k, dir: c && c.better === "low" ? "asc" : c && (c.better === "high" || c.id === "size" || c.id === "params") ? "desc" : "asc" };
      }
      BL.store.set("sort", state.sort);
      update();
    };
    tbl.addEventListener("click", (e) => {
      const th = e.target.closest("th[data-sort]");
      if (th) doSort(th);
    });
    tbl.addEventListener("keydown", (e) => {
      const th = e.target.closest("th[data-sort]");
      if (th && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); doSort(th); }
    });
    tbl.addEventListener("change", (e) => {
      const cb = e.target.closest("input.pick");
      if (!cb) return;
      if (cb.checked) { if (state.selected.size < BL.MAX_COMPARE) state.selected.add(cb.dataset.uid); }
      else state.selected.delete(cb.dataset.uid);
      BL.store.set("selected", [...state.selected]);
      update();
    });
    el.querySelector("#go-compare").addEventListener("click", () => {
      location.hash = BL.compareHref([...state.selected]);
    });
    el.querySelector("#clear-sel").addEventListener("click", () => {
      state.selected.clear();
      BL.store.set("selected", []);
      update();
    });

    update();
  }

  BL.ENGINE_LABEL_TEXT = (e) => ({ lmstudio: "LM Studio", ollama: "Ollama" }[e] || e);
  BL.views.table = render;
})();
