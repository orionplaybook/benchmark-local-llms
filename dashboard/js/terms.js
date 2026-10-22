/* Term definitions: marks known labels with data-term and shows a popover on hover, focus or tap.
   Labels are matched against BL.GLOSSARY (see js/glossary.js); views don't need to change. */
(function () {
  "use strict";
  const BL = window.BL;

  // Elements whose whole label may be a glossary term.
  const CANDIDATES = "th, dt, .kpi .k, .badge, h2, h3, .slider label, .legend > span, table.data td:first-child";
  const STRIP = ".arrow, .val, .muted, small, .hint, input, select";

  function labelOf(el) {
    const c = el.cloneNode(true);
    c.querySelectorAll(STRIP).forEach((n) => n.remove());
    return c.textContent.replace(/\s+/g, " ").trim();
  }

  function annotate(root) {
    if (!root || !BL.glossaryLookup) return;
    root.querySelectorAll(CANDIDATES).forEach((el) => {
      if (el.dataset.term || el.closest("[data-term]") || el.closest(".glossary-page, .term-pop")) return;
      const label = labelOf(el);
      if (!label) return;
      let id = null;
      if (el.closest(".slider, .fit-panel, .fit")) id = BL.glossaryLookup("fit: " + label);
      if (!id) id = BL.glossaryLookup(label);
      if (!id) return;
      el.dataset.term = id;
      el.classList.add("has-term");
      if (!el.hasAttribute("tabindex") && !/^(A|BUTTON|INPUT|SELECT)$/.test(el.tagName)) el.setAttribute("tabindex", "0");
      if (el.hasAttribute("title")) { el.dataset.termTitle = el.getAttribute("title"); el.removeAttribute("title"); }
    });
  }

  // ---------------------------------------------------------------- popover
  let pop = null;
  let current = null;
  let showTimer = 0, hideTimer = 0;

  function ensurePop() {
    if (pop) return pop;
    pop = document.createElement("div");
    pop.className = "term-pop";
    pop.setAttribute("role", "tooltip");
    pop.id = "term-pop";
    pop.hidden = true;
    pop.addEventListener("mouseenter", () => clearTimeout(hideTimer));
    pop.addEventListener("mouseleave", () => scheduleHide());
    document.body.appendChild(pop);
    return pop;
  }

  function catLabel(id) {
    const c = (BL.GLOSSARY_CATS || []).find((x) => x.id === id);
    return c ? c.label : "";
  }

  function show(el) {
    const g = BL.glossaryById(el.dataset.term);
    if (!g) return;
    const p = ensurePop();
    current = el;
    const extra = el.dataset.termTitle ? '<div class="term-pop-ctx">' + BL.esc(el.dataset.termTitle) + "</div>" : "";
    p.innerHTML =
      '<div class="term-pop-head"><b>' + BL.esc(g.term) + '</b><span class="term-pop-cat">' + BL.esc(catLabel(g.cat)) + "</span></div>" +
      '<div class="term-pop-body">' + g.short + "</div>" + extra +
      '<a class="term-pop-more" href="#/glossary?t=' + encodeURIComponent(g.id) + '">More in the Glossary →</a>';
    p.hidden = false;
    el.setAttribute("aria-describedby", "term-pop");
    position(el);
  }

  function position(el) {
    const r = el.getBoundingClientRect();
    const pw = pop.offsetWidth, ph = pop.offsetHeight;
    const vw = document.documentElement.clientWidth, vh = window.innerHeight;
    let left = Math.min(Math.max(8, r.left + r.width / 2 - pw / 2), vw - pw - 8);
    let top = r.bottom + 8;
    if (top + ph > vh - 8 && r.top - ph - 8 > 8) top = r.top - ph - 8;
    pop.style.left = left + window.scrollX + "px";
    pop.style.top = top + window.scrollY + "px";
  }

  function hide() {
    if (!pop) return;
    pop.hidden = true;
    if (current) current.removeAttribute("aria-describedby");
    current = null;
  }
  function scheduleHide() { clearTimeout(showTimer); clearTimeout(hideTimer); hideTimer = setTimeout(hide, 180); }

  const termEl = (t) => (t && t.closest ? t.closest("[data-term]") : null);

  document.addEventListener("mouseover", (e) => {
    const el = termEl(e.target);
    if (!el) return;
    clearTimeout(hideTimer);
    if (el === current) return;
    clearTimeout(showTimer);
    showTimer = setTimeout(() => show(el), 250);
  });
  document.addEventListener("mouseout", (e) => {
    const el = termEl(e.target);
    if (el && !el.contains(e.relatedTarget)) scheduleHide();
  });
  document.addEventListener("focusin", (e) => { const el = termEl(e.target); if (el) show(el); });
  document.addEventListener("focusout", (e) => { if (termEl(e.target)) scheduleHide(); });
  // Tap / click: toggle on plain labels (sortable headers and links keep their own click action).
  document.addEventListener("click", (e) => {
    if (pop && pop.contains(e.target)) { if (e.target.closest("a")) hide(); return; }
    const el = termEl(e.target);
    if (!el) { hide(); return; }
    if (el.matches("[data-sort], a, button") || e.target.closest("a, button, input, select")) return;
    if (current === el && !pop.hidden) hide(); else show(el);
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") hide(); });
  window.addEventListener("scroll", () => { if (current && pop && !pop.hidden) position(current); }, { passive: true });
  window.addEventListener("hashchange", hide);

  // Re-annotate whenever views add content (charts, async sections, re-renders).
  let pending = 0;
  function observe(root) {
    annotate(root);
    new MutationObserver(() => {
      if (pending) return;
      pending = requestAnimationFrame(() => { pending = 0; annotate(root); });
    }).observe(root, { childList: true, subtree: true });
  }

  BL.terms = { annotate, observe, hide };
})();
