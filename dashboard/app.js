/* App shell: data loading, hash routing, refresh, theme toggle.
   Views live in js/view-*.js; shared helpers in js/core.js and js/charts.js. */
(function () {
  "use strict";
  const BL = window.BL;
  const app = document.getElementById("app");
  let idx = null;
  let loadError = null;
  BL.renderToken = 0;

  function parseRoute() {
    const raw = location.hash.replace(/^#/, "") || "/";
    const qi = raw.indexOf("?");
    const path = qi >= 0 ? raw.slice(0, qi) : raw;
    const query = new URLSearchParams(qi >= 0 ? raw.slice(qi + 1) : "");
    const params = {};
    for (const [k, v] of query) params[k] = v;
    const parts = path.split("/").filter(Boolean);
    if (parts[0] === "model" && parts.length > 1) {
      let uid = parts.slice(1).join("/");
      try { uid = decodeURIComponent(uid); } catch (e) { /* keep raw */ }
      return { name: "model", params: Object.assign(params, { uid }) };
    }
    if (parts[0] === "compare") return { name: "compare", params };
    if (parts[0] === "explain") return { name: "explain", params };
    if (parts[0] === "glossary") return { name: "glossary", params };
    return { name: "table", params };
  }

  function setNav(name) {
    document.querySelectorAll("#nav a").forEach((a) => a.classList.toggle("active", a.dataset.route === (name === "model" ? "table" : name)));
    const cmp = document.querySelector('#nav a[data-route="compare"]');
    const sel = [...BL.tableState.selected];
    cmp.href = sel.length ? BL.compareHref(sel) : "#/compare";
  }

  function emptyState() {
    return (
      '<div class="empty"><h2>No benchmark data yet</h2>' +
      "<p>Run <code>./bench run</code> to collect data, then open it again with <code>./bench dashboard</code>.</p></div>"
    );
  }

  function errorState(err) {
    return (
      '<div class="empty"><h2>Could not load the database</h2>' +
      '<p class="mono small">' + BL.esc(err && err.message ? err.message : String(err)) + "</p>" +
      "<p>Start the dashboard with <code>./bench dashboard</code> (or <code>./bench dashboard --live</code>), " +
      "or upload a folder made with <code>./bench publish --out &lt;folder&gt;</code> to a web server.</p></div>"
    );
  }

  function render() {
    const token = ++BL.renderToken;
    BL.charts.destroyAll();
    BL.charts.applyDefaults();
    const route = parseRoute();
    setNav(route.name);
    // Explain and Glossary work without data (the estimator just shows a hint).
    const docs = route.name === "explain" || route.name === "glossary";
    if (!docs) {
      if (loadError) { app.innerHTML = errorState(loadError); return; }
      if (!idx) { app.innerHTML = '<div class="loading">Loading…</div>'; return; }
      if (!idx.rows.length) { app.innerHTML = emptyState(); return; }
    }
    const ctx = { idx: idx || { rows: [], runs: [] }, params: route.params, token, rerender: render };
    try {
      BL.views[route.name](app, ctx);
      if (route.name === "table" && !idx.runs.length) {
        app.insertAdjacentHTML("afterbegin", BL.dataMode === "static"
          ? '<div class="notice">This snapshot lists the models but contains no benchmark results yet.</div>'
          : '<div class="notice">Models are known but nothing has been benchmarked yet. Run <code>./bench run</code> to collect data.</div>');
      }
    } catch (e) {
      console.error(e);
      app.innerHTML = '<div class="empty"><h2>Something went wrong rendering this page</h2><p class="mono small">' + BL.esc(e.message) + '</p><p><a href="#/">Back to models</a></p></div>';
    }
    setNav(route.name);
  }

  function showUpdated(db) {
    document.getElementById("snapshot-pill").hidden = BL.dataMode !== "static";
    // A static copy only changes when it's regenerated; Refresh is for `./bench dashboard --live`.
    document.getElementById("refresh").hidden = BL.dataMode === "static";
    const el = document.getElementById("updated");
    // "Updated": for a static copy (./bench dashboard or ./bench publish) when it was generated; for the live server
    // when the results last changed. Local time zone.
    const gen = BL.dataMode === "static" && db && db.published_at;
    const when = gen ? db.published_at : db && db.updated_at;
    if (when) {
      el.textContent = "Updated " + BL.fmt.dateTz(when);
      el.title = BL.fmt.ago(when) + (db.tool_version ? " · tool " + db.tool_version : "");
    } else el.textContent = "";
  }

  async function load() {
    const btn = document.getElementById("refresh");
    btn.disabled = true;
    try {
      const db = await BL.loadDb();
      idx = BL.buildIndex(db);
      loadError = null;
      showUpdated(db);
    } catch (e) {
      console.warn("Database load failed:", e);
      loadError = e;
      idx = null;
      showUpdated(null);
    } finally {
      btn.disabled = false;
    }
    render();
  }

  // ---- theme
  function effectiveDark() {
    const t = document.documentElement.getAttribute("data-theme");
    if (t) return t === "dark";
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  document.getElementById("theme").addEventListener("click", () => {
    const next = effectiveDark() ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("llmbench.theme", next); } catch (e) { /* ignore */ }
    render();
  });
  if (window.matchMedia) {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => { if (!document.documentElement.getAttribute("data-theme")) render(); };
    if (mq.addEventListener) mq.addEventListener("change", onChange);
  }

  // The Compare tab always opens the current selection (checkboxes ticked after the page rendered included).
  document.querySelector('#nav a[data-route="compare"]').addEventListener("click", (e) => {
    const sel = [...BL.tableState.selected];
    if (!sel.length) return;            // nothing selected: plain #/compare (shows the picker)
    e.preventDefault();
    const target = BL.compareHref(sel);
    if (location.hash === target) render(); else location.hash = target;
  });
  document.getElementById("refresh").addEventListener("click", load);
  window.addEventListener("hashchange", () => { window.scrollTo(0, 0); render(); });
  BL.terms.observe(app);
  load();
})();
