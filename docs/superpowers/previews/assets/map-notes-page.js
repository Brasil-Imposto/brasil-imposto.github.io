// Como ler o mapa: the notes. A file, not inline code: the site's CSP refuses inline scripts (spec seguranca-doacoes, section 8).
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
