// Runs the network graph's model (previews/assets/ledger-graph-model.js) over every period of the map's selector (each
// month, each year, both mandates), in Node over the same bundle the map reads, and fails unless every period with full
// data passes every check. Then plants the two controls (R$ 1 more in the Cofins of SC; a point with no link), which must
// fail. Every console.error the map code raises (serieslayer.js guards such as "as linhas de receita somam") is counted and
// fails the check too, with its own planted control. Usage: node docs/superpowers/tools/ledger-graph-periods-check.cjs "$PWD"
const fs = require('fs'), vm = require('vm'), path = require('path');
const A = path.join(process.argv[2], 'docs/superpowers/previews/assets');
const raised = [];
const sandboxConsole = { log: console.log, warn: console.warn, info: console.info, error: (...a) => raised.push(a.join(' ')) };
const ctx = { console: sandboxConsole, Map, Set, Math, JSON, Object, Number, String, Array, Date }; ctx.window = ctx;
ctx.document = { addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; } };
vm.createContext(ctx);
for (const f of ['bi-data.js', 'bi-geo.js', 'periods.js', 'serieslayer.js', 'bi-ledger-interest.js', 'ledger-graph-model.js']) vm.runInContext(fs.readFileSync(path.join(A, f), 'utf8'), ctx, { filename: f });
const latest = ctx.BI.series.union.latest.nominal_result;
const periods = [];
for (let y = 2019; y <= +latest.slice(0, 4); y++) for (let m = 1; m <= 12; m++) { const s = `${y}-${String(m).padStart(2, '0')}`; if (s <= latest) periods.push({ mode: 'month', month: s }); }
for (let y = 2019; y <= +latest.slice(0, 4); y++) periods.push({ mode: 'year', year: y });
periods.push({ mode: 'mandate', mandate: '2019-2022' }, { mode: 'mandate', mandate: '2023-2026' });
let failed = 0, drawn = 0, empty = [];
const row = (g) => g.checks.map((c) => (c.ok === true ? 'ok' : c.ok === false ? 'FAIL' : 'n/a')).join(' ');
for (const p of periods) {
  const r = ctx.BIT.resolve(p, latest), g = ctx.BILG.build(r);
  if (!g.ok) { empty.push(`${r.short}: ${g.missing.length} estados`); continue; }
  drawn += 1;
  const bad = g.checks.filter((c) => c.ok === false);
  if (bad.length) { failed += 1; console.log('FAIL', r.label, bad.map((c) => c.detail).join(' | ')); }
  if (p.mode !== 'month' || p.month.endsWith('-01')) console.log(`${g.label.padEnd(26)} ${String(g.nodes.length).padStart(5)} pontos ${String(g.links.length).padStart(5)} ligações | ${row(g)}${g.estimated ? ` | ${g.estimated.months.length} meses estimados` : ''}`);
}
console.log(`\n${drawn} períodos desenhados, ${failed} com falha; sem dados completos: ${empty.join('; ') || 'nenhum'}`);
let controlsOk = true;
for (const p of [{ mode: 'year', year: 2024 }, { mode: 'mandate', mandate: '2023-2026' }, { mode: 'month', month: '2026-03' }]) {
  const r = ctx.BIT.resolve(p, latest);
  for (const kind of ['tax', 'loose']) {
    const g = ctx.BILG.build(r, kind), caught = g.checks.find((c) => c.id === (kind === 'tax' ? 'taxes' : 'connected')).ok === false;
    console.log(`controle ${kind} em ${r.short}: ${caught ? 'falhou, como deve' : 'PASSOU (a conferência está cega)'}`);
    if (!caught) controlsOk = false;
  }
}
// Guards raised by the map code while drawing the periods (each state-month once).
const guard = [...new Set(raised)];
console.log(`\n${guard.length} alertas do código do mapa${guard.length ? ':' : ''}`);
const amount = (s) => Math.abs(+((s.match(/R\$ (-?[\d.]+)/) || [])[1] || 0));
guard.slice().sort((a, b) => amount(b) - amount(a)).slice(0, 5).forEach((s) => console.log('  ' + s));
// Control for the counter: R$ 10 mi more in one clean state-month's current revenue must raise a guard.
const rm = ctx.BI.series.state_budgets.uf.SC.revenue_monthly, CUR = 'RECEITAS CORRENTES (I)';
const month = rm.months.find((m) => m >= '2024-01' && !guard.some((s) => s.includes('SC ' + ctx.BIT.resolve({ mode: 'month', month: m }, latest).label + ':')));
const i = rm.months.indexOf(month), before = raised.length, kept = rm.lines[CUR][i];
rm.lines[CUR][i] = kept + 1e7;
ctx.BIL.stateAt('SC', ctx.BIT.resolve({ mode: 'month', month }, latest));
rm.lines[CUR][i] = kept;
const guardCaught = raised.length > before && raised[raised.length - 1].includes('SC ');
console.log(`controle alerta em SC ${month}: ${guardCaught ? 'falhou, como deve' : 'PASSOU (o contador está cego)'}`);
if (!guardCaught) controlsOk = false;
if (failed || guard.length || !controlsOk || !drawn) { console.log('CHECK FAILED'); process.exit(1); }
console.log('ALL CHECKS PASSED');
