"""Builds the notes page "Como ler o mapa" (spec home-trim, D159, section 5): the two blocks that lived under the map on Início,
"Como ler o mapa" (the notes) and "Última divulgação de cada fonte" (the table), with the same titles, text and order, for the
period and the measure the reader had on the map (?period=<id>&metric=<perCapita|total|ratio>; without them, the map's own
default). The page reads assets/map-notes.js (build-map-notes.cjs), never the map's data, and changes the notes without
reloading. The header and footer are the common ones (site_chrome.py); the page is not in the header's list.

Run: python3 docs/superpowers/tools/build-notes-page.py
"""
from pathlib import Path

import site_chrome

PREVIEWS = Path(__file__).resolve().parents[1] / "previews"
OUT = PREVIEWS / site_chrome.NOTES_PAGE

PAGE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Como ler o mapa · Brasil-Imposto</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root { --ink: #14202B; --muted: #5B6773; --faint: #8A95A1; --line: #E3E7EC; --paper: #FFFFFF; --soft: #F6F8FA; --green: #12803F; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink); font-family: 'Manrope', system-ui, sans-serif; -webkit-font-smoothing: antialiased; }
  a { color: var(--muted); }
  /* The period and the measure, as on the map (periods.js; the map's measure switch). */
  /* the same left edge as the notes below: their block is 1180 px inside the section's 24 px (16 px on a phone) */
  .notes-ctl { max-width: 1228px; margin: 0 auto; padding: 22px 24px 4px; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 18px; }
  @media (max-width: 760px) { .notes-ctl { padding: 18px 16px 4px; } }
  .notes-ctl .period { margin: 0; }
  .period { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 8px; margin-bottom: 12px; }
  .period .plab { font-size: 11px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: var(--faint, #8A95A1); }
  .pseg { display: inline-flex; gap: 2px; padding: 3px; background: #EDF0F3; border-radius: 99px; }
  .pseg button, .pchips button { font: inherit; font-size: 12px; font-weight: 700; color: #5B6773; background: none; border: 0; border-radius: 99px; padding: 5px 11px; cursor: pointer; }
  .pseg button[aria-pressed="true"] { background: #fff; color: #14202B; box-shadow: 0 1px 3px rgba(20,32,43,.14); }
  .pchips { display: flex; flex-wrap: wrap; gap: 4px; } .pchips button { border: 1px solid #E3E7EC; background: #fff; }
  .pchips button[aria-pressed="true"] { background: #14202B; color: #fff; border-color: #14202B; }
  .period select { font: inherit; font-size: 12.5px; font-weight: 700; border: 1px solid #E3E7EC; border-radius: 99px; padding: 5px 10px; background: #fff; color: #14202B; }
  .metric-switch { display: inline-flex; gap: 2px; padding: 3px; background: #EDF0F3; border-radius: 99px; }
  .metric-switch button { font: inherit; font-size: 12px; font-weight: 700; color: var(--muted); background: none; border: 0; border-radius: 99px; padding: 6px 13px; cursor: pointer; }
  .metric-switch button[aria-pressed="true"] { background: #fff; color: var(--ink); box-shadow: 0 1px 3px rgba(20,32,43,.14); }
  /* The two blocks that lived under the map on Início (their style moved with them). */
  .map-notes { background: #fff; border-top: 1px solid var(--line); padding: 26px 24px 30px; }
  .map-notes .in { max-width: 1180px; margin: 0 auto; display: grid; grid-template-columns: 1.1fr 1fr; gap: 28px; }
  .map-notes h3 { margin: 0 0 8px; font-size: 15px; }
  .map-notes ul { margin: 0; padding-left: 18px; color: var(--muted); font-size: 13px; line-height: 1.6; }
  .map-notes li + li { margin-top: 4px; }
  .map-notes table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  .map-notes td { padding: 5px 6px; border-bottom: 1px solid var(--line); color: var(--muted); vertical-align: top; }
  .map-notes td:first-child { color: var(--ink); font-weight: 700; white-space: nowrap; }
  .map-notes td.d { text-align: right; white-space: nowrap; color: var(--ink); font-weight: 700; }
  @media (max-width: 760px) { .map-notes { padding: 22px 16px; } .map-notes .in { grid-template-columns: 1fr; gap: 18px; } }
  .map-notes { border-top: 0; }
  .map-notes h1, .map-notes h2 { margin: 0 0 8px; font-size: 15px; }
  .map-notes h1 { font-size: 22px; letter-spacing: -.01em; }
  .notes-err { max-width: 1180px; margin: 24px auto; padding: 0 24px; color: var(--muted); }
</style>
<!-- site-chrome:css -->
<!-- /site-chrome:css -->
</head>
<body>
<!-- site-chrome:header -->
<!-- /site-chrome:header -->
<main>
<div class="notes-ctl"><div data-period></div>
  <div class="metric-switch" role="group" aria-label="Medida">
    <button type="button" data-metric="perCapita" aria-pressed="true">Por habitante</button>
    <button type="button" data-metric="total" aria-pressed="false">Total</button>
    <button type="button" data-metric="ratio" aria-pressed="false">Proporção</button>
  </div>
</div>
<section class="map-notes" id="como-ler-o-mapa"><div class="in">
  <div><h1>Como ler o mapa</h1><ul data-map-notes></ul></div>
  <div><h2>Última divulgação de cada fonte</h2><table data-map-dates></table></div>
</div></section>
</main>
<script src="assets/periods.js"></script>
<script src="assets/map-notes.js"></script>
<script>
// The notes for the period and the measure in the address (D159), read from assets/map-notes.js; the selector and the measure
// switch change them without reloading, and the address follows, so a link keeps what the reader sees.
(function () {
  const N = window.BI_NOTES, BIT = window.BIT;
  if (!N || !BIT) {
    document.querySelector('main').insertAdjacentHTML('afterbegin', '<p class="notes-err" role="alert">As notas não carregaram. Recarregue a página.</p>');
    return;
  }
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  const METRICS = ['perCapita', 'total', 'ratio'];
  const base = { year: +N.default.period.slice(5), month: N.default.month, mandate: '2023-2026' };
  const parse = (id) => {
    const m = /^(month|year|mandate)-(.+)$/.exec(id || '');
    if (!m || !N.periods[id]) return null;
    return m[1] === 'month' ? { ...base, mode: 'month', month: m[2] } : m[1] === 'year' ? { ...base, mode: 'year', year: +m[2] } : { ...base, mode: 'mandate', mandate: m[2] };
  };
  const idOf = (p) => (p.mode === 'month' ? `month-${p.month}` : p.mode === 'year' ? `year-${p.year}` : `mandate-${p.mandate}`);
  const params = new URLSearchParams(location.search);
  let period = parse(params.get('period')) || parse(N.default.period);
  let metric = METRICS.includes(params.get('metric')) ? params.get('metric') : N.default.metric;
  const ctl = document.querySelector('[data-period]');
  const draw = () => {
    const id = idOf(period), set = N.periods[id] || N.periods[N.default.period];
    document.querySelector('[data-map-notes]').innerHTML = set[metric].map((i) => `<li>${esc(N.strings[i])}</li>`).join('');
    document.querySelector('[data-map-dates]').innerHTML = N.dates.map(([l, what, d]) => `<tr><td>${l}</td><td>${esc(what)}</td><td class="d">${d}</td></tr>`).join('');
    ctl.innerHTML = BIT.selector(period, N.latest, N.first, 'notes-period');
    BIT.bind(ctl, period, N.latest, (np) => { period = { ...base, ...np }; draw(); });
    document.querySelectorAll('.metric-switch button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.metric === metric)));
    const q = new URLSearchParams(location.search); q.set('period', id); q.set('metric', metric);
    history.replaceState(null, '', `${location.pathname}?${q}${location.hash}`);
  };
  document.querySelectorAll('.metric-switch button').forEach((b) => b.addEventListener('click', () => { metric = b.dataset.metric; draw(); }));
  window.__showNotes = (id, m) => { period = parse(id) || period; metric = METRICS.includes(m) ? m : metric; draw(); };
  draw();
  document.body.dataset.ready = '1';
})();
</script>
<!-- site-chrome:js -->
<!-- /site-chrome:js -->
<!-- site-chrome:footer -->
<!-- /site-chrome:footer -->
</body>
</html>
"""


def build():
    model = (PREVIEWS / "BRASIL-IMPOSTO_DESIGN_hero-mapa-3d-round-2_2026-09-29.html").read_text(encoding="utf-8")
    if not ("map-notes" not in model.replace("map-notes-model", "")):
        raise SystemExit("the notes style is still on Início")
    page = site_chrome.inject(PAGE, "notas")
    if not (chr(0x2014) not in page and chr(0x2013) not in page):
        raise SystemExit("dash found")
    return page


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(OUT.name, round(OUT.stat().st_size / 1024), "KB")
