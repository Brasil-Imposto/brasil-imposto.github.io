// DF alternatives (phase 1 complement): the DF and União balances under four ways of counting the tax registered in the DF,
// computed with the map's own functions (periods.js, serieslayer.js) over the map's data. Run: node docs/research/fase-1-complemento-2026-10-24/df_alternatives.cjs docs/superpowers/previews/assets (after build-cases.py and build-standalone-data.py)
const fs = require('fs'), vm = require('vm'), path = require('path');
const A = process.argv[2];
const ctx = { console, Map, Set, Math, JSON, Object, Number, String, Array, Date }; ctx.window = ctx; vm.createContext(ctx);
for (const f of ['bi-data.js', 'periods.js', 'serieslayer.js']) vm.runInContext(fs.readFileSync(path.join(A, f), 'utf8'), ctx);
const BI = ctx.BI, BIT = ctx.BIT, BIL = ctx.BIL;
const latest = BI.series.union.latest.nominal_result;
const per = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026].map((y) => ({ mode: 'year', year: y })).concat([{ mode: 'mandate', mandate: '2019-2022' }, { mode: 'mandate', mandate: '2023-2026' }]);
const G = BI.df_gdp_share, gdp = G.share;
const pop = BI.series.population.uf; // the population file has a national row (BR); the share is the DF over BR, the year's estimate, 2022 (Censo) when the year has none
const popShare = (y) => { const yy = String(Math.min(y, 2026)); const v = (u) => pop[u].population[yy] ?? pop[u].population['2022']; return v('DF') / v('BR'); };
const bi = (v) => (v == null ? 'n/d' : (v / 1e9).toFixed(1));
const rows = [];
for (const p of per) {
  const r = BIT.resolve({ year: +latest.slice(0, 4), month: latest, mandate: '2023-2026', ...p }, latest);
  const run = (share) => { G.share = share; const f = BIL.federalAt('DF', r); G.share = gdp; return f; };
  const now = run(gdp);
  const noCap = { sent: now.sentRegistered, bal: now.sentRegistered != null && now.received != null ? now.sentRegistered - now.received : null };
  // control: a cap of 100% must leave the registered value, so its balance equals the balance without a cap
  const full = run(1); if (Math.abs(full.balance - noCap.bal) > 0.005) throw new Error(`control failed for ${r.label}`);
  const y = p.year || 2026; const ps = popShare(y); const byPop = run(ps);
  rows.push({ period: r.label, received: bi(now.received), sent_registered: bi(now.sentRegistered), excess_gdp: bi(now.dfEstimate && now.dfEstimate.excess),
    bal_registered: bi(noCap.bal), bal_gdp_cap: bi(now.balance), bal_pop_cap: bi(byPop.balance), pop_share: (ps * 100).toFixed(2), ok: now.ok });
}
console.log(JSON.stringify({ gdp_share_pct: (gdp * 100).toFixed(2), gdp_year: G.year, rows }, null, 1));
