// The page's own computation of the DF (trust spec, A1): runs periods.js and serieslayer.js, the published map's code, over its
// built data bundle (assets/bi-data.js) and writes, for every period the selector offers, every DF figure the map shows and each
// state's revenue and period. Read by test_df_balance.py. Usage: node df_page.cjs <assets folder> <out.json>
const fs = require('fs'), vm = require('vm'), path = require('path');
const [dir, out] = process.argv.slice(2);
const ctx = { window: {}, console };
ctx.window.window = ctx.window;
vm.createContext(ctx);
for (const f of ['bi-data.js', 'periods.js', 'serieslayer.js']) vm.runInContext(fs.readFileSync(path.join(dir, f), 'utf8'), ctx, { filename: f });
const W = ctx.window, BIT = W.BIT, BIL = W.BIL, U = W.BI.series.union;
const latest = U.latest.nominal_result;
const periods = [];
for (const m of W.BI.series.federal_by_uf_monthly.months) if (m <= latest) periods.push({ mode: 'month', month: m });
for (let y = 2019; y <= +latest.slice(0, 4); y++) periods.push({ mode: 'year', year: y });
for (const k of ['2019-2022', '2023-2026']) periods.push({ mode: 'mandate', mandate: k });
const UFS = Object.keys(W.BI.series.federal_by_uf_monthly.uf);
const res = { latest, periods: {} };
for (const p of periods) {
  const r = BIT.resolve(p, latest);
  const key = p.mode === 'month' ? `month:${p.month}` : p.mode === 'year' ? `year:${p.year}` : `mandate:${p.mandate}`;
  const df = BIL.federalAt('DF', r);
  const all = Object.fromEntries(UFS.map((u) => { const f = BIL.federalAt(u, r); return [u, { sent: f.sent, sentRegistered: f.sentRegistered, received: f.received, ok: f.ok, months: f.months }]; }));
  res.periods[key] = { r_months: r.months, df: { ...df, fedSpendingParts: undefined }, all };
}
fs.writeFileSync(out, JSON.stringify(res));
