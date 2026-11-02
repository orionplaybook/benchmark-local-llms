/* Glossary view (#/glossary[?t=id]): searchable lexicon of every term, grouped by category. */
(function () {
  "use strict";
  const BL = window.BL;
  const { esc } = BL;

  function entryHtml(g) {
    const see = (g.see || []).map((id) => BL.glossaryById(id)).filter(Boolean);
    return (
      '<div class="g-entry" id="g-' + g.id + '" data-search="' + esc((g.term + " " + (g.aka || []).join(" ") + " " + g.short.replace(/<[^>]+>/g, "")).toLowerCase()) + '">' +
      '<h3><a class="g-anchor" href="#/glossary?t=' + encodeURIComponent(g.id) + '">' + esc(g.term) + "</a></h3>" +
      "<p>" + g.short + "</p>" + (g.long ? '<p class="g-long">' + g.long + "</p>" : "") +
      (see.length ? '<p class="g-see">See also: ' + see.map((s) => '<a href="#/glossary?t=' + encodeURIComponent(s.id) + '">' + esc(s.term) + "</a>").join(" · ") + "</p>" : "") +
      "</div>"
    );
  }

  BL.views.glossary = function (app, ctx) {
    const cats = BL.GLOSSARY_CATS;
    const q0 = ctx.params.q || "";
    app.innerHTML =
      '<div class="glossary-page"><div class="page-head"><h1>Glossary</h1>' +
      '<p class="muted">Every term used in this dashboard, in plain language. ' + BL.GLOSSARY.length + ' entries. For how the pieces fit together, see <a href="#/explain">Explain</a>.</p>' +
      '<div class="g-tools"><input type="search" id="g-q" placeholder="Search terms (e.g. QAT, prefill, τ²-bench)…" aria-label="Search the glossary" value="' + esc(q0) + '">' +
      '<span class="g-jump">' + cats.map((c) => '<a href="#/glossary?c=' + c.id + '">' + esc(c.label) + "</a>").join("") + "</span></div></div>" +
      cats.map((c) => {
        const items = BL.GLOSSARY.filter((g) => g.cat === c.id).sort((a, b) => a.term.localeCompare(b.term));
        return '<section class="card g-cat" id="gc-' + c.id + '"><h2>' + esc(c.label) + ' <span class="muted small">' + items.length + "</span></h2>" +
          '<div class="g-grid">' + items.map(entryHtml).join("") + "</div></section>";
      }).join("") +
      '<p class="muted small g-none" hidden>No terms match your search.</p></div>';

    const input = app.querySelector("#g-q");
    const filter = () => {
      const q = input.value.trim().toLowerCase();
      let any = false;
      app.querySelectorAll(".g-cat").forEach((sec) => {
        let shown = 0;
        sec.querySelectorAll(".g-entry").forEach((e) => {
          const ok = !q || e.dataset.search.includes(q);
          e.hidden = !ok;
          shown += ok;
        });
        sec.hidden = !shown;
        any = any || shown > 0;
      });
      app.querySelector(".g-none").hidden = any;
    };
    input.addEventListener("input", filter);
    filter();

    const target = ctx.params.t ? document.getElementById("g-" + ctx.params.t) : ctx.params.c ? document.getElementById("gc-" + ctx.params.c) : null;
    if (target) {
      requestAnimationFrame(() => {
        target.scrollIntoView({ block: "center" });
        if (ctx.params.t) { target.classList.add("flash"); setTimeout(() => target.classList.remove("flash"), 1800); }
      });
    } else if (!q0) {
      input.focus({ preventScroll: true });
    }
  };
})();
