// Writes assets/map-notes.js, the notes of the map for the notes page (spec home-trim, D159, section 5): for every period of
// the map's selector (each month, each year, both mandates) and every measure (perCapita, total, ratio), the notes that
// map-notes-model.js builds from the map's own functions (periods.js, serieslayer.js) over the map's data (bi-data.js), and
// the table of each source's last release. Each distinct note is stored once, so the page reads a small file instead of the
// map's data. Run after build-standalone-data.py: node docs/superpowers/tools/build-map-notes.cjs [assets folder]
const fs = require('fs'), vm = require('vm'), path = require('path');
const A = process.argv[2] || path.join(__dirname, '..', 'previews', 'assets');
const ctx = { console, Map, Set, Math, JSON, Object, Number, String, Array, Date }; ctx.window = ctx;
vm.createContext(ctx);
for (const f of ['bi-data.js', 'periods.js', 'serieslayer.js', 'map-notes-model.js']) vm.runInContext(fs.readFileSync(path.join(A, f), 'utf8'), ctx, { filename: f });
const BI = ctx.BI, BIT = ctx.BIT, BIL = ctx.BIL, BIMN = ctx.BIMN;
const U = BI.series.union, latest = U.latest.nominal_result, first = U.months[0];
// The periods the selector offers, in its own order (periods.js, selector()).
const periods = [];
for (let y = +latest.slice(0, 4); y >= +first.slice(0, 4); y--) for (let m = 12; m >= 1; m--) { const s = `${y}-${String(m).padStart(2, '0')}`; if (s <= latest && s >= first) periods.push({ mode: 'month', month: s }); }
for (let y = +latest.slice(0, 4); y >= +first.slice(0, 4); y--) periods.push({ mode: 'year', year: y });
periods.push({ mode: 'mandate', mandate: '2023-2026' }, { mode: 'mandate', mandate: '2019-2022' });
const METRICS = ['perCapita', 'total', 'ratio'];
const strings = [], index = new Map(), byPeriod = {};
const idOf = (s) => { if (!index.has(s)) { index.set(s, strings.length); strings.push(s); } return index.get(s); };
for (const p of periods) {
  const r = BIT.resolve({ year: +latest.slice(0, 4), month: latest, mandate: '2023-2026', ...p }, latest);
  const rows = BIMN.rowsAt(BI.states, r);
  byPeriod[BIMN.periodId(r)] = Object.fromEntries(METRICS.map((m) => [m, BIMN.notes(rows, r, m).map(idOf)]));
}
// The map opens on the current year up to the last month every source has, by habitant (the map's own default).
const lc = BIL.latestComplete();
// Like the map, the month the selector starts on is that last complete month (Início: period.month = lc || latest).
const out = { latest, first, default: { period: `year-${lc ? +lc.slice(0, 4) : +latest.slice(0, 4)}`, month: lc || latest, metric: 'perCapita' },
  strings, periods: byPeriod, dates: BIMN.dates() };
const text = `// Built by docs/superpowers/tools/build-map-notes.cjs from the map's data; do not edit.\nwindow.BI_NOTES = ${JSON.stringify(out)};\n`;
fs.writeFileSync(path.join(A, 'map-notes.js'), text);
console.log(`map-notes.js ${Math.round(text.length / 1024)} KB; ${Object.keys(byPeriod).length} periods, ${METRICS.length} measures, ${strings.length} distinct notes`);
