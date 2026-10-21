// Period model (round 10): one month, one year, or a 4-year presidential mandate. Every component resolves the chosen
// period against what its source really publishes and labels what it shows (a month-only view never hides that a
// number is annual). Classic script. Exposes window.BIT.
(function () {
  const MONTHS = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
  const SHORT = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
  const MANDATES = [['2019-2022', 2019, 2022], ['2023-2026', 2023, 2026]];
  const ym = (s) => [+s.slice(0, 4), +s.slice(5, 7)];
  const fmtMonth = (s, short) => { const [y, m] = ym(s); return short ? `${SHORT[m - 1]}/${y}` : `${MONTHS[m - 1]} de ${y}`; };

  // p = { mode: 'month' | 'year' | 'mandate', month: 'YYYY-MM', year: YYYY, mandate: '2023-2026' }; latest = 'YYYY-MM'
  function resolve(p, latest) {
    const [ly, lm] = ym(latest);
    const monthsOf = (y0, y1) => { const out = []; for (let y = y0; y <= y1; y++) for (let m = 1; m <= 12; m++) { const s = `${y}-${String(m).padStart(2, '0')}`; if (s <= latest) out.push(s); } return out; };
    if (p.mode === 'month') { const [y] = ym(p.month); return { mode: 'month', months: [p.month], years: [y], partial: false, label: fmtMonth(p.month), short: fmtMonth(p.month, true) }; }
    if (p.mode === 'year') {
      const months = monthsOf(p.year, p.year); const partial = p.year === ly && lm < 12;
      return { mode: 'year', months, years: [p.year], partial, label: partial ? `${p.year} (janeiro a ${MONTHS[lm - 1]})` : `${p.year}`, short: partial ? `${p.year} até ${SHORT[lm - 1]}` : `${p.year}` };
    }
    const [key, y0, y1] = MANDATES.find(([k]) => k === p.mandate);
    const months = monthsOf(y0, y1); const partial = y1 > ly || (y1 === ly && lm < 12);
    const years = []; for (let y = y0; y <= Math.min(y1, ly); y++) years.push(y);
    return { mode: 'mandate', months, years, partial, key, label: `mandato ${y0} a ${y1}${partial ? ` (até ${fmtMonth(latest, true)})` : ''}`, short: `${y0} a ${y1}${partial ? ` até ${SHORT[lm - 1]}/${ly}` : ''}` };
  }

  // A monthly flow summed over the period. Returns { value, n, of } so a partial sum is never silent.
  function sum(months, arr, r) {
    if (!arr) return { value: null, n: 0, of: r.months.length };
    const idx = new Map(months.map((m, i) => [m, i]));
    let value = 0, n = 0;
    for (const m of r.months) { const i = idx.get(m); if (i != null && arr[i] != null) { value += arr[i]; n++; } }
    return { value: n ? value : null, n, of: r.months.length };
  }
  // A stock (debt) at the last month of the period that has data.
  function stock(months, arr, r) {
    if (!arr) return { value: null, at: null };
    const idx = new Map(months.map((m, i) => [m, i]));
    for (let k = r.months.length - 1; k >= 0; k--) { const i = idx.get(r.months[k]); if (i != null && arr[i] != null) return { value: arr[i], at: r.months[k] }; }
    return { value: null, at: null };
  }
  // An annual figure: a year reads its own value; a mandate sums its years; a single month cannot be shown.
  function annual(byYear, r) {
    if (!byYear) return { value: null, years: [] };
    if (r.mode === 'month') return { value: byYear[r.years[0]] ?? null, years: [r.years[0]], wider: true };
    const ys = r.years.filter((y) => byYear[y] != null);
    return { value: ys.length ? ys.reduce((a, y) => a + byYear[y], 0) : null, years: ys, missing: r.years.filter((y) => byYear[y] == null) };
  }

  // The selector: [Mês | Ano | 4 anos] and the value picker for the chosen mode.
  function selector(p, latest, first = '2019-01', cls = '') {
    const [ly] = ym(latest); const [fy] = ym(first);
    const years = []; for (let y = ly; y >= fy; y--) years.push(y);
    const months = []; for (let y = ly; y >= fy; y--) for (let m = 12; m >= 1; m--) { const s = `${y}-${String(m).padStart(2, '0')}`; if (s <= latest && s >= first) months.push(s); }
    const seg = [['month', 'Mês'], ['year', 'Ano'], ['mandate', '4 anos']].map(([k, l]) => `<button type="button" data-pmode="${k}" aria-pressed="${p.mode === k}">${l}</button>`).join('');
    let pick = '';
    if (p.mode === 'month') pick = `<select data-pmonth aria-label="Mês">${months.map((s) => `<option value="${s}"${s === p.month ? ' selected' : ''}>${fmtMonth(s)}</option>`).join('')}</select>`;
    // The year is a dropdown, like the month.
    if (p.mode === 'year') pick = `<select data-pyear aria-label="Ano">${years.map((y) => `<option value="${y}"${y === p.year ? ' selected' : ''}>${y}</option>`).join('')}</select>`;
    if (p.mode === 'mandate') pick = `<div class="pchips">${MANDATES.slice().reverse().map(([k, a, b]) => `<button type="button" data-pmandate="${k}" aria-pressed="${k === p.mandate}">${a} a ${b}</button>`).join('')}</div>`;
    return `<div class="period ${cls}"><span class="plab">Período</span><div class="pseg">${seg}</div>${pick}</div>`;
  }
  // Wires a selector rendered inside root; onChange receives the new period object.
  function bind(root, p, latest, onChange) {
    root.querySelectorAll('[data-pmode]').forEach((b) => { b.onclick = () => onChange({ ...p, mode: b.dataset.pmode }); });
    root.querySelectorAll('[data-pyear]').forEach((s) => { s.onchange = () => onChange({ ...p, year: +s.value }); });
    root.querySelectorAll('[data-pmandate]').forEach((b) => { b.onclick = () => onChange({ ...p, mandate: b.dataset.pmandate }); });
    root.querySelectorAll('[data-pmonth]').forEach((s) => { s.onchange = () => onChange({ ...p, month: s.value }); });
  }
  const initial = (latest) => ({ mode: 'year', year: +latest.slice(0, 4) - (latest.slice(5, 7) === '12' ? 0 : 1), month: latest, mandate: '2023-2026' });

  window.BIT = { resolve, sum, stock, annual, selector, bind, initial, fmtMonth, MONTHS };
})();
