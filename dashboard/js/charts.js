/* Chart.js helpers: theme-aware defaults, a registry so charts are destroyed on re-render,
   and small factories (bar, line, radar) that follow one visual style. */
(function () {
  "use strict";
  const BL = window.BL;
  const live = new Set();

  function applyDefaults() {
    if (!window.Chart) return;
    const C = window.Chart;
    C.defaults.font.family = getComputedStyle(document.body).fontFamily;
    C.defaults.font.size = 11.5;
    C.defaults.color = BL.cssVar("--text-2");
    C.defaults.borderColor = BL.cssVar("--grid");
    C.defaults.animation = false;
    C.defaults.maintainAspectRatio = false;
    C.defaults.plugins.legend.display = false; // HTML legends instead
    const tt = C.defaults.plugins.tooltip;
    tt.backgroundColor = BL.cssVar("--surface");
    tt.titleColor = BL.cssVar("--text");
    tt.bodyColor = BL.cssVar("--text-2");
    tt.borderColor = BL.cssVar("--border-strong");
    tt.borderWidth = 1;
    tt.padding = 8;
    tt.boxPadding = 4;
    tt.usePointStyle = true;
  }

  function destroyAll() {
    for (const c of live) {
      try { c.destroy(); } catch (e) { /* ignore */ }
    }
    live.clear();
  }

  function make(canvas, config) {
    if (!window.Chart || !canvas) return null;
    const c = new window.Chart(canvas, config);
    live.add(c);
    return c;
  }

  // HTML legend; items: [{label, color, kind: "box"|"line"|"dash"}]
  function legendHtml(items) {
    return (
      '<div class="legend">' +
      items
        .map((it) => '<span><span class="sw ' + (it.kind || "") + '" style="background:' + it.color + '"></span>' + BL.esc(it.label) + "</span>")
        .join("") +
      "</div>"
    );
  }

  function scaleY(opts) {
    const s = {
      type: opts.log ? "logarithmic" : "linear",
      beginAtZero: !opts.log,
      grid: { color: BL.cssVar("--grid") },
      border: { display: false },
      ticks: { maxTicksLimit: 6 },
      title: opts.yTitle ? { display: true, text: opts.yTitle, color: BL.cssVar("--text-3") } : undefined,
    };
    if (opts.log) {
      s.ticks.callback = function (v, i, ticks) {
        const r = Math.round((v / Math.pow(10, Math.floor(Math.log10(v)))) * 1000) / 1000;
        const show = ticks.length <= 10 || r === 1 || r === 2 || r === 5;
        return show ? String(Number(v.toPrecision(2))) : "";
      };
      s.ticks.maxTicksLimit = undefined;
    }
    return s;
  }

  /* Grouped bar chart.
     opts: { labels, datasets: [{label, data, color}], yTitle, fmt, log, horizontal } */
  function bar(canvas, opts) {
    const surface = BL.cssVar("--surface");
    const datasets = opts.datasets.map((d) => ({
      label: d.label,
      data: d.data.map((v) => (BL.isNum(v) && (!opts.log || v > 0) ? v : null)),
      backgroundColor: d.color,
      hoverBackgroundColor: d.color,
      borderColor: surface,
      borderWidth: { top: 0, bottom: 0, left: 1, right: 1 },
      borderRadius: 4,
      borderSkipped: "start",
      maxBarThickness: 34,
      categoryPercentage: 0.72,
      barPercentage: 0.92,
    }));
    const f = opts.fmt || ((v) => v);
    const valueAxis = scaleY(opts);
    if (opts.log) {
      // Anchor log bars at the power of ten below the smallest value so every bar has visible length.
      const vals = datasets.flatMap((d) => d.data).filter((v) => BL.isNum(v) && v > 0);
      if (vals.length) valueAxis.min = Math.pow(10, Math.floor(Math.log10(Math.min(...vals))));
    }
    const catAxis = { grid: { display: false }, border: { color: BL.cssVar("--border-strong") }, ticks: { autoSkip: false, maxRotation: 0, color: BL.cssVar("--text-2") } };
    return make(canvas, {
      type: "bar",
      data: { labels: opts.labels, datasets },
      options: {
        indexAxis: opts.horizontal ? "y" : "x",
        interaction: { mode: "index", intersect: false },
        scales: opts.horizontal ? { x: valueAxis, y: catAxis } : { x: catAxis, y: valueAxis },
        plugins: {
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const v = opts.horizontal ? ctx.parsed.x : ctx.parsed.y;
                return " " + ctx.dataset.label + ": " + (BL.isNum(v) ? f(v) : BL.DASH);
              },
            },
          },
        },
      },
    });
  }

  /* Radar chart. opts: { labels, datasets: [{label, data, color}] } (0..100) */
  function radar(canvas, opts) {
    const surface = BL.cssVar("--surface");
    const datasets = opts.datasets.map((d) => ({
      label: d.label,
      data: d.data.map((v) => (BL.isNum(v) ? v : null)),
      borderColor: d.color,
      backgroundColor: hexA(d.color, 0.14),
      pointBackgroundColor: d.color,
      pointBorderColor: surface,
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
      borderWidth: 2,
      spanGaps: true,
    }));
    return make(canvas, {
      type: "radar",
      data: { labels: opts.labels, datasets },
      options: {
        scales: {
          r: {
            min: 0, max: 100,
            ticks: { stepSize: 25, backdropColor: "transparent", color: BL.cssVar("--text-3"), font: { size: 10 } },
            grid: { color: BL.cssVar("--grid") },
            angleLines: { color: BL.cssVar("--grid") },
            pointLabels: { color: BL.cssVar("--text-2"), font: { size: 11.5, weight: "600" } },
          },
        },
        plugins: {
          tooltip: { callbacks: { label: (ctx) => " " + ctx.dataset.label + ": " + (BL.isNum(ctx.raw) ? ctx.raw.toFixed(1) : BL.DASH) } },
        },
      },
    });
  }

  /* Memory timeline: engine GB coloured by phase + system used (dashed, muted).
     points: [{t, engine_bytes, system_used_bytes, phase}] */
  function memoryTimeline(canvas, points, phaseColor) {
    const GB = BL.GB;
    const step = Math.max(1, Math.ceil(points.length / 1500));
    const pts = points.filter((_, i) => i % step === 0);
    const eng = pts.map((p) => ({ x: p.t, y: BL.isNum(p.engine_bytes) ? p.engine_bytes / GB : null, phase: p.phase }));
    const sys = pts.map((p) => ({ x: p.t, y: BL.isNum(p.system_used_bytes) ? p.system_used_bytes / GB : null }));
    const hasSys = sys.some((p) => p.y != null);
    const datasets = [
      {
        label: "Engine memory",
        data: eng,
        parsing: false,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderColor: (ctx) => (ctx.raw ? phaseColor(ctx.raw.phase) : BL.cssVar("--series-1")),
        segment: { borderColor: (ctx) => phaseColor(eng[ctx.p1DataIndex] && eng[ctx.p1DataIndex].phase) },
        spanGaps: false,
      },
    ];
    if (hasSys) {
      datasets.push({
        label: "System used",
        data: sys,
        parsing: false,
        borderWidth: 1.5,
        borderDash: [5, 4],
        pointRadius: 0,
        pointHoverRadius: 3,
        borderColor: BL.cssVar("--series-muted"),
      });
    }
    return make(canvas, {
      type: "line",
      data: { datasets },
      options: {
        interaction: { mode: "nearest", axis: "x", intersect: false },
        scales: {
          x: { type: "linear", title: { display: true, text: "seconds since run start", color: BL.cssVar("--text-3") }, grid: { color: BL.cssVar("--grid") }, border: { display: false }, ticks: { maxTicksLimit: 10 } },
          y: { beginAtZero: true, title: { display: true, text: "GB", color: BL.cssVar("--text-3") }, grid: { color: BL.cssVar("--grid") }, border: { display: false } },
        },
        plugins: {
          tooltip: {
            callbacks: {
              title: (items) => (items.length ? "t = " + items[0].parsed.x.toFixed(1) + " s" + (items[0].raw.phase ? " · " + items[0].raw.phase : "") : ""),
              label: (ctx) => " " + ctx.dataset.label + ": " + BL.fmt.gb(ctx.parsed.y) + " GB",
            },
          },
        },
      },
    });
  }

  function hexA(color, a) {
    const m = /^#?([0-9a-f]{6})$/i.exec((color || "").trim());
    if (!m) return color;
    const n = parseInt(m[1], 16);
    return "rgba(" + ((n >> 16) & 255) + "," + ((n >> 8) & 255) + "," + (n & 255) + "," + a + ")";
  }

  BL.charts = { applyDefaults, destroyAll, make, bar, radar, memoryTimeline, legendHtml, hexA };
})();
