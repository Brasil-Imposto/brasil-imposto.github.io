// Series layer (round 10): turns the time series in window.BI.series into the shapes the modal already draws, for any
// period chosen in the selector. Every value says which period it really covers. Classic script. Exposes window.BIL.
(function () {
  const S = () => window.BI.series || {};
  // State revenue lines (RREO Anexo 03 monthly lines) and the names people read.
  const REV = [
    ['ICMS', 'ICMS'], ['IPVA', 'IPVA'], ['ITCD', 'ITCD (heranças e doações)'], ['IRRF', 'Imposto de renda retido na fonte'],
    ['Outros Impostos, Taxas e Contribuições de Melhoria', 'Outros impostos e taxas'], ['Cota-Parte do FPE', 'Fundo de Participação dos Estados (União)'],
    ['Transferências do FUNDEB', 'Fundeb'], ['Transferências da LC nº 61/1989', 'IPI exportação (União)'], ['Transferências da LC nº 87/1996', 'Compensação da Lei Kandir (União)'],
    ['Outras Transferências Correntes', 'Outras transferências'], ['Contribuições', 'Contribuições (previdência dos servidores)'],
    ['Receita Patrimonial', 'Receita patrimonial'], ['Receita de Serviços', 'Receita de serviços'], ['Outras Receitas Correntes', 'Outras receitas correntes'],
    // The DF reports the city taxes of Brasília (ISS, IPTU, ITBI) and the city funds (FPM, ITR) in the same annex; leaving them
    // out dropped about R$ 6 bi a year from the DF. The small agricultural and industrial lines close every state to the cent.
    ['ISS', 'ISS'], ['IPTU', 'IPTU'], ['ITBI', 'ITBI'], ['Cota-Parte do FPM', 'Fundo de Participação dos Municípios (União)'],
    ['Cota-Parte do ITR', 'Cota-parte do ITR (União)'], ['Receita Agropecuária', 'Receita agropecuária'], ['Receita Industrial', 'Receita industrial'],
    ['IBS', 'IBS'],
  ];
  const bimOf = (m) => Math.ceil(+m.slice(5, 7) / 2);

  // Cumulative bimester reports -> the period: a closed year reads B6, the current year its latest bimester,
  // a mandate sums its years, a month reads the bimester that contains it (reported as that bimester).
  function periodKeys(st, r) {
    const latest = st.latest.rreo; const [ly, lb] = [+latest.slice(0, 4), +latest.slice(6)];
    const yearKey = (y) => (y < ly ? `${y}-B6` : y === ly ? latest : null);
    if (r.mode === 'month') { const y = +r.months[0].slice(0, 4), b = bimOf(r.months[0]); return { kind: 'bimester', y, b, key: `${y}-B${b}`, prev: b > 1 ? `${y}-B${b - 1}` : null }; }
    return { kind: 'years', keys: r.years.map(yearKey).filter(Boolean), partial: r.years.includes(ly) && lb < 6 };
  }
  const quad = (k) => `${k.slice(6)}º quadrimestre de ${k.slice(0, 4)}`; // '2026-Q2' -> '2º quadrimestre de 2026'
  const addFns = (acc, fns, sign = 1) => { for (const f of fns || []) { const a = acc.get(f.label) || { label: f.label, value: 0, sub: new Map() }; a.value += sign * f.value; for (const s of f.sub || []) a.sub.set(s.label, (a.sub.get(s.label) || 0) + sign * s.value); acc.set(f.label, a); } };
  // k scales the values: a single month reads a two-month bimester report as its monthly average (k = 0.5).
  const finishFns = (acc, k = 1) => [...acc.values()].map((f) => ({ label: f.label, value: f.value * k, sub: [...f.sub].map(([label, value]) => ({ label, value: value * k })).filter((s) => s.value > 0).sort((a, b) => b.value - a.value) }))
    .filter((f) => f.value > 0).sort((a, b) => b.value - a.value);

  function stateAt(uf, r) {
    const st = S().state_budgets && S().state_budgets.uf[uf];
    if (!st) return null;
    const T = window.BIT; const rm = st.revenue_monthly;
    const line = (k) => T.sum(rm.months, rm.lines[k], r).value;
    const revenue_top = REV.map(([k, label]) => ({ label, value: line(k) })).filter((x) => x.value > 0).sort((a, b) => b.value - a.value);
    // The lines must add up to the annex's own current revenue; a line missing from REV shows here, not on screen.
    const gap = line('RECEITAS CORRENTES (I)') - revenue_top.reduce((a, x) => a + x.value, 0);
    if (Math.abs(gap) > 1) console.error(`BIL.stateAt ${uf} ${r.label}: as linhas de receita somam R$ ${gap.toFixed(2)} a menos que a receita corrente`);
    const pk = periodKeys(st, r); const P = st.periods;
    let fns = new Map(), spending, revenueTotal, result, resultBasis, primary, spendingLabel;
    if (pk.kind === 'bimester') {
      const cur = P[pk.key], prev = pk.prev ? P[pk.prev] : null;
      if (cur) { addFns(fns, cur.spending_by_function); if (prev) addFns(fns, prev.spending_by_function, -1); }
      spending = cur ? cur.spending_liquidated_in_bimester : null; revenueTotal = cur ? cur.revenue_in_bimester : null;
      result = cur ? revenueTotal - spending : null; resultBasis = 'liquidadas'; primary = null;
      spendingLabel = `${pk.b}º bimestre de ${pk.y}`;
    } else {
      const ps = pk.keys.map((k) => P[k]).filter(Boolean);
      for (const p of ps) addFns(fns, p.spending_by_function);
      revenueTotal = ps.reduce((a, p) => a + p.revenue_total, 0);
      spending = ps.reduce((a, p) => a + (p.budget_result_basis === 'despesas empenhadas' ? p.spending_committed : p.spending_liquidated), 0);
      result = ps.reduce((a, p) => a + (p.budget_result ?? (p.revenue_total - p.spending_liquidated)), 0);
      primary = ps.every((p) => p.primary_result != null) ? ps.reduce((a, p) => a + p.primary_result, 0) : null;
      resultBasis = 'empenhadas no ano fechado, liquidadas no ano corrente';
      spendingLabel = r.label;
    }
    const spending_by_function = finishFns(fns, pk.kind === 'bimester' ? 0.5 : 1);
    // The months the state's reports really cover inside the period. A state files every two months, so the current year
    // usually ends before the period does: per-month values divide by these months, and the label says which they are.
    const cur = rm.lines['RECEITAS CORRENTES (I)'], at = new Map(rm.months.map((m, i) => [m, i]));
    const covered = r.months.filter((m) => at.has(m) && cur[at.get(m)] != null);
    const lastCov = covered[covered.length - 1];
    let coverLabel = null;
    if (pk.kind !== 'bimester' && lastCov && covered.length < r.months.length) {
      coverLabel = r.mode === 'year' ? `${r.years[0]} (janeiro a ${T.MONTHS[+lastCov.slice(5, 7) - 1]})` : `${r.label.replace(/ \(até .*\)$/, '')} (até ${T.fmtMonth(lastCov, true)})`;
    }
    // Debt: the last four-month report at or before the end of the period.
    const end = r.months[r.months.length - 1]; const q = (k) => { const [y, n] = [+k.slice(0, 4), +k.slice(6)]; return `${y}-${String(n * 4).padStart(2, '0')}`; };
    const dk = Object.keys(st.debt).filter((k) => q(k) <= end).sort().pop();
    return {
      year: r.label, periodLabel: r.label, months: pk.kind === 'bimester' ? r.months.length : (covered.length || r.months.length), coverLabel, spendingPeriod: coverLabel || spendingLabel, spendingNote: pk.kind === 'bimester' ? `Gastos: média mensal do ${spendingLabel} (o relatório de gastos é bimestral).` : null,
      revenue_top, revenue_current_total: line('RECEITAS CORRENTES (I)'),
      to_municipalities: line('Transferências Constitucionais e Legais'), fundeb_deduction: line('Dedução de Receita para Formação do FUNDEB'),
      spending_by_function, spending_total: spending_by_function.reduce((a, f) => a + f.value, 0),
      contas: { revenueTotal, spending, result, resultBasis, primary, debt: dk ? { ...st.debt[dk], at: dk } : null },
      sources: [{ url: 'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo' }, { url: 'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo' }],
    };
  }

  // "Sobrou ou faltou" for a state government.
  function stateContas(name, b, r) {
    const c = b.contas; const K = window.BIK;
    const rcl = c.debt && c.debt.dcl_pct_rcl != null ? `${c.debt.dcl_pct_rcl.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}% da receita corrente líquida` : '';
    return K.card({
      period: r.mode === 'month' ? `${b.spendingPeriod} (o relatório é bimestral)` : b.coverLabel ? `${b.coverLabel}, último relatório do governo` : r.label,
      inLabel: 'Entrou (todas as receitas do governo estadual)', outLabel: 'Saiu (despesas do governo estadual)',
      inValue: c.revenueTotal, outValue: c.spending, result: c.result,
      resultWhat: `Receitas menos despesas do governo de ${name} no período (Balanço Orçamentário, despesas ${c.resultBasis}).`,
      second: c.primary != null ? { label: 'Sem contar juros e empréstimos (resultado primário)', value: c.primary } : null,
      debt: c.debt ? { value: c.debt.dc, pct: c.debt.dcl_pct_rcl, what: `Dívida consolidada no fim do ${quad(c.debt.at)}. Descontado o que tem em caixa: ${K.money(c.debt.dcl)}${rcl ? `, ${rcl}` : ''}.` } : null,
      sources: [{ label: 'SICONFI, RREO Anexos 1, 2, 3 e 6', url: 'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo' }, { label: 'SICONFI, RGF Anexo 2', url: 'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf' }],
    });
  }

  // Population of the period's last year, or the nearest year IBGE published (2023 had no estimate).
  function popOf(byYear, r) {
    const want = r.years[r.years.length - 1]; const ys = Object.keys(byYear).map(Number).filter((y) => byYear[y] != null);
    const y = ys.sort((a, b) => Math.abs(a - want) - Math.abs(b - want) || b - a)[0];
    return { value: byYear[y], year: y };
  }

  // Federal balance of a state for the period (D37, D45). Revenue in the months of the Receita's broken UF split comes
  // from the estimate (federal-revenue-uf-estimated.json). "Received" counts transfers, Bolsa Família, INSS, BPC, the FCDF
  // and the federal spending in the state by the two-step rule (twoStepAt). The period stops at the last month that every
  // component has, so a partial current year is labelled with its real end.
  const lastIn = (months, a) => { for (let i = a.length - 1; i >= 0; i--) if (a[i] != null) return months[i]; return null; };
  function withEstimate(F, arr, estArr) {
    const E = S().federal_revenue_uf_estimated; if (!E || !estArr) return arr;
    const eix = new Map(E.months.map((m, i) => [m, i]));
    return F.months.map((m, i) => (eix.has(m) ? estArr[eix.get(m)] : arr[i]));
  }
  // Federal spending in the state by the two-step rule (D45, GD16; data/series/federal-spending-two-step-by-uf.json):
  // the UF where the money was applied, otherwise the UF of the paying unit; the Legislative, Judiciary, MPU and DPU by the
  // seat of the unit; the FCDF in the DF. Benefits paid to people nationwide by one central unit (unemployment insurance,
  // wage bonus, emergency aid, BEm) count by the UF of the localizer when present, otherwise without a state; unemployment
  // insurance and wage bonus by the UF of who receives them where the MTE publishes it (annual): a whole year inside the
  // period. It counts only when every month of the period is computed, so a partial sum never tilts a state.
  const KIND = { civil_active_and_other: 'servidores civis ativos', civil_retirees_and_pensions: 'aposentadorias e pensões de servidores civis',
    military: 'militares', operating_costs: 'custeio (serviços, materiais e contratos)', investment: 'investimento (obras e equipamentos)',
    benefits_to_people: 'benefícios e auxílios a pessoas', special_charges: 'encargos especiais', economic_subsidies: 'subvenções econômicas' };
  const BRANCH = { legislative: 'Legislativo', judiciary: 'Judiciário', mpu: 'Ministério Público da União', dpu: 'Defensoria Pública da União' };
  function twoStepAt(uf, r) {
    const TS = S().federal_spending_two_step_by_uf; if (!TS) return { complete: false };
    const T = window.BIT; const u = TS.uf[uf]; const full = (x) => x.value != null && x.n === x.of;
    const ex = T.sum(TS.months, u.executive, r), ot = T.sum(TS.months, u.other_branches, r), fc = T.sum(TS.months, u.fcdf, r);
    if (!full(ex) || !full(ot) || !full(fc)) return { complete: false };
    let central = 0, centralWithoutState = 0; const mteYears = [];
    for (const y of [...new Set(r.months.map((m) => m.slice(0, 4)))]) {
      const ms = r.months.filter((m) => m.startsWith(y)); const M = TS.mte_annual[y];
      if (M && ms.length === 12) { central += M.uf[uf].unemployment_insurance + M.uf[uf].wage_bonus; mteYears.push(y); }
      central += T.sum(TS.months, u.central_benefits_localized, { ...r, months: ms }).value || 0;
      centralWithoutState += T.sum(TS.months, TS.no_state.central_benefits, { ...r, months: ms }).value || 0;
    }
    const parts = Object.entries(u.executive_by_kind).map(([k, a]) => ({ label: KIND[k], value: T.sum(TS.months, a, r).value || 0 }));
    if (central) parts.push({ label: 'seguro-desemprego, abono e auxílios pagos a pessoas', value: central });
    for (const [k, a] of Object.entries(u.other_branches_by_branch)) parts.push({ label: BRANCH[k], value: T.sum(TS.months, a, r).value || 0 });
    return { complete: true, value: ex.value + ot.value + central, fcdf: fc.value, mteYears, centralWithoutState,
      parts: parts.filter((x) => x.value > 0).sort((a, b) => b.value - a.value) };
  }
  // FCDF personnel (police, firefighters, health and education of the DF), for the note under the DF; from the payroll series.
  const fcdfPersonnel = (r) => { const P = S().federal_payroll_by_uf; if (!P || !P.fcdf || !P.fcdf.by_group) return null;
    const pe = P.fcdf.by_group.personnel_and_charges; const x = pe ? window.BIT.sum(P.months, pe, r) : null; return x && x.n === x.of ? x.value : null; };
  // The DF estimate (D146): the Receita registers in the DF the tax that head offices and federal bodies in Brasília withhold
  // or pay for the whole country (Lei 9.779/1999, art. 15). In each tax the DF counts at most its share of Brazil's GDP
  // (IBGE) of that tax in the 27 states; the excess leaves the DF and so lands in the União block, which is the official
  // total minus the 27 states. Nothing else changes: the "voltou" side keeps the two-step rule.
  function dfCapped(F, E, rr) {
    const G = window.BI.df_gdp_share; if (!G) return null;
    const T = window.BIT, sumK = (uf, k) => T.sum(F.months, withEstimate(F, F.uf[uf].federal_revenue.by_tax[k], E && E.uf[uf].by_tax[k]), rr).value || 0;
    let registered = 0, capped = 0;
    for (const k of Object.keys(F.uf.DF.federal_revenue.by_tax)) {
      const df = sumK('DF', k), br = Object.keys(F.uf).reduce((a, u) => a + sumK(u, k), 0);
      registered += df; capped += Math.min(df, G.share * br);
    }
    return { excess: registered - capped, share: G.share, year: G.year };
  }
  function federalAt(uf, r) {
    const F = S().federal_by_uf_monthly; if (!F) return null;
    const T = window.BIT; const u = F.uf[uf]; const status = F.national.federal_revenue_month_status;
    const idx = new Map(F.months.map((m, i) => [m, i]));
    const E = S().federal_revenue_uf_estimated; const est = new Set(E ? E.months : []);
    const TS = S().federal_spending_two_step_by_uf;
    const end = [lastIn(F.months, u.federal_revenue.total), lastIn(F.months, u.transfers.total), lastIn(F.months, u.inss), lastIn(F.months, u.bolsa_familia), ...(TS ? [lastIn(TS.months, TS.uf[uf].executive)] : [])].sort()[0];
    // A month whose Portal file is broken (2025-06 came with every value zeroed) leaves the period on both sides.
    const brokenTS = TS && TS.broken_months ? TS.broken_months : {};
    const dropped = r.months.filter((m) => brokenTS[m]);
    const months = r.months.filter((m) => m <= end && !brokenTS[m]);
    const rr = { ...r, months };
    const rev = withEstimate(F, u.federal_revenue.total, E && E.uf[uf].total);
    const sum = (a) => T.sum(F.months, a, rr);
    const sentRegistered = sum(rev), tr = sum(u.transfers.total), bf = sum(u.bolsa_familia), inss = sum(u.inss), bpc = sum(u.bpc);
    const dfEstimate = uf === 'DF' && sentRegistered.value != null ? dfCapped(F, E, rr) : null;
    const sent = dfEstimate ? { ...sentRegistered, value: sentRegistered.value - dfEstimate.excess } : sentRegistered;
    const two = twoStepAt(uf, rr);
    const bad = months.filter((m) => idx.has(m) && String(status[idx.get(m)]).includes('broken') && !est.has(m));
    const estimatedMonths = months.filter((m) => est.has(m));
    const complete = (x) => x.value != null && x.n === x.of;
    const pop = popOf(S().population.uf[uf].population, r);
    const received = tr.value != null && two.complete ? tr.value + (bf.value || 0) + (inss.value || 0) + (bpc.value || 0) + two.fcdf + two.value : null;
    const ok = months.length > 0 && !bad.length && complete(sent) && complete(tr) && two.complete;
    const cut = months.length && months[months.length - 1] < r.months.filter((m) => !brokenTS[m]).slice(-1)[0] ? months[months.length - 1] : null;
    const base = cut ? (r.mode === 'year' ? `${r.years[0]} (janeiro a ${window.BIT.MONTHS[+cut.slice(5, 7) - 1]})` : `${r.label.split(' (')[0]} (até ${window.BIT.fmtMonth(cut, true)})`) : r.label;
    const label = dropped.length ? `${base}, sem ${dropped.map((m) => window.BIT.fmtMonth(m, true)).join(', ')}` : base;
    return {
      sent: sent.value, sentRegistered: sentRegistered.value, dfEstimate, sentOk: !bad.length, badMonths: bad, estimatedMonths, transfers: tr.value, bolsa: bf.value, inss: inss.value, bpc: bpc.value,
      fcdf: two.complete && uf === 'DF' ? two.fcdf : null, fcdfPersonnel: uf === 'DF' ? fcdfPersonnel(rr) : null,
      fedSpending: two.complete ? two.value : null, fedSpendingParts: two.complete ? two.parts : [], twoStepComplete: two.complete,
      mteYears: two.mteYears || [], centralWithoutState: two.centralWithoutState || 0, droppedMonths: dropped, received, label,
      complete: { sent: complete(sent), transfers: complete(tr), bolsa: complete(bf), inss: complete(inss) }, ok,
      population: pop.value, balance: ok ? sent.value - received : null, months: months.length,
      perPersonMonth: ok ? (sent.value - received) / pop.value / months.length : null,
      byTax: Object.fromEntries(Object.entries(u.federal_revenue.by_tax).map(([k, a]) => [k, sum(withEstimate(F, a, E && E.uf[uf].by_tax[k])).value])),
    };
  }
  // The latest month for which the whole state balance can be drawn (revenue, estimated where needed, transfers, INSS).
  function latestComplete() {
    const F = S().federal_by_uf_monthly; if (!F) return null; const sc = F.uf.SC;
    const TS = S().federal_spending_two_step_by_uf;
    return [lastIn(F.months, sc.federal_revenue.total), lastIn(F.months, sc.transfers.total), lastIn(F.months, sc.inss), lastIn(F.months, sc.bolsa_familia), ...(TS ? [lastIn(TS.months, TS.uf.SC.executive)] : [])].sort()[0];
  }
  // How good the estimate is, for the notes on screen.
  const estimateNote = () => {
    const E = S().federal_revenue_uf_estimated; if (!E) return null;
    const b = E.backtest[0]; const nf = (v) => v.toLocaleString('pt-BR', { maximumFractionDigits: 1 });
    return { first: E.months[0], last: E.months[E.months.length - 1], median: nf(b.median_abs_error_pct), max: nf(b.max_abs_error_pct),
      text: `De ${window.BIT.fmtMonth(E.months[0])} a ${window.BIT.fmtMonth(E.months[E.months.length - 1])}, a Receita Federal lançou no Distrito Federal uma parte grande do que foi pago nos outros estados. Nesses meses, a parte de cada estado é estimada: cada estado fica com a sua participação em cada imposto no mesmo mês do ano anterior, e o total do Brasil é o publicado. Testado em 2024, o método erra ${nf(b.median_abs_error_pct)}% por estado na mediana (até ${nf(b.max_abs_error_pct)}% em estados pequenos).` };
  };

  // Default year: the latest full year with every source complete and no month of the broken UF split.
  function lastSoundYear() {
    const F = S().federal_by_uf_monthly; if (!F) return null;
    const st = F.national.federal_revenue_month_status; const sc = F.uf.SC; const idx = new Map(F.months.map((m, i) => [m, i]));
    const ok = (m) => { const i = idx.get(m); return i != null && !String(st[i]).includes('broken') && st[i] !== 'not_published' && sc.transfers.total[i] != null && sc.inss[i] != null && sc.federal_revenue.total[i] != null; };
    for (let y = +F.months[F.months.length - 1].slice(0, 4); y >= +F.months[0].slice(0, 4); y--) {
      let all = true; for (let m = 1; m <= 12; m++) if (!ok(`${y}-${String(m).padStart(2, '0')}`)) { all = false; break; }
      if (all) return y;
    }
    return null;
  }

  // States with municipal series, by the first two digits of the IBGE code (D71: SC, then RS).
  const ufOf = (code) => ({ 42: 'sc', 43: 'rs' })[String(code).slice(0, 2)];
  // A municipality for the period: federal revenue is annual (Receita), transfers, Bolsa Família and BPC monthly.
  function municipalAt(code, r) {
    const u = ufOf(code); const M = u && S()[`${u}_municipal_federal`]; if (!M) return null; const m = M.municipalities[code]; if (!m) return null;
    const T = window.BIT; const sum = (a) => T.sum(M.months, a, r);
    const E = S().federal_revenue_uf_estimated; const k = E && E[`${u}_municipal_2025`] ? E[`${u}_municipal_2025`].scale : null;
    // 2025 suffers the same DF break in the Receita's municipal file: each city keeps its share of its state, scaled to the state estimate.
    const byYear = k ? { ...m.federal_revenue_annual, 2025: m.federal_revenue_annual[2025] != null ? m.federal_revenue_annual[2025] * k : null } : m.federal_revenue_annual;
    const rev = T.annual(byYear, r);
    const tr = sum(m.transfers_monthly), bf = sum(m.bolsa_familia_monthly), bpc = sum(m.bpc_monthly);
    const pop = popOf(m.population, r);
    const received = tr.value != null ? tr.value + (bf.value || 0) + (bpc.value || 0) : null;
    const yearsOk = rev.value != null && (!rev.missing || !rev.missing.length);
    return { name: m.name, population: pop.value, federal_revenue: rev.value, revenueYears: rev.years, revenueEstimated: Boolean(k && rev.years.includes(2025)), revenueWider: Boolean(rev.wider), revenueMissing: rev.missing || [],
      federal_transfers: tr.value, bolsa_familia: bf.value, bpc: bpc.value, received, transfersComplete: tr.n === tr.of,
      balance: yearsOk && received != null && !rev.wider ? rev.value - received : null };
  }

  // Municipal budget lines (RREO Anexo 03 of each prefeitura) with the name people read and where the money came from.
  const MREV = [
    ['ISS', 'ISS', 'tax'], ['IPTU', 'IPTU', 'tax'], ['ITBI', 'ITBI', 'tax'], ['IRRF', 'Imposto de renda dos servidores municipais', 'tax'],
    ['Outros Impostos, Taxas e Contribuições de Melhoria', 'Taxas municipais', 'tax'],
    ['Cota-Parte do FPM', 'Fundo de Participação dos Municípios (União)', 'uniao'], ['Cota-Parte do ITR', 'Cota-parte do ITR (União)', 'uniao'],
    ['Transferências da LC nº 87/1996', 'Compensação da Lei Kandir (União)', 'uniao'],
    ['Cota-Parte do ICMS', 'Cota-parte do ICMS (estado)', 'estado'], ['Cota-Parte do IPVA', 'Cota-parte do IPVA (estado)', 'estado'],
    ['Transferências da LC nº 61/1989', 'IPI exportação (repasse do estado)', 'estado'],
    ['Transferências do FUNDEB', 'Fundeb', null], ['Outras Transferências Correntes', 'Outras transferências', null],
    ['Contribuições', 'Contribuições', null], ['Receita Patrimonial', 'Receita patrimonial', null], ['Receita de Serviços', 'Receita de serviços', null],
    ['Outras Receitas Correntes', 'Outras receitas correntes', null],
  ];
  const TAX_INFO = {
    'ISS': ['sobre serviços: consertos, consultas, escolas, aplicativos', 'wrench'], 'IPTU': ['imposto anual dos imóveis urbanos', 'house'],
    'ITBI': ['sobre a compra e venda de imóveis', 'building'], 'Imposto de renda dos servidores municipais': ['retido na folha; fica com a prefeitura', 'wallet'],
    'Taxas municipais': ['taxas e contribuições da prefeitura', 'receipt'],
  };
  function muniBudgetAt(code, r) {
    const u = ufOf(code); const M = u && S()[`${u}_municipal_budgets`]; if (!M) return null; const m = M.municipalities[code]; if (!m || !m.revenue_monthly) return null;
    const T = window.BIT; const rm = m.revenue_monthly;
    const line = (k) => (rm.lines[k] ? T.sum(rm.months, rm.lines[k], r).value : null);
    const lines = MREV.map(([k, label, kind]) => ({ label, value: line(k), origin: kind === 'tax' ? 'municipios' : kind, kind })).filter((x) => x.value > 0);
    const keys = Object.keys(m.periods).sort(); const latestKey = keys[keys.length - 1];
    const st = { latest: { rreo: latestKey } };
    const pk = periodKeys(st, r); const P = m.periods;
    let fns = new Map(), spending, revenueTotal, result, primary, spendingLabel, monthsCovered = r.months.length, k = 1, spendingNote = null;
    // The municipal series keeps each closed year (B6) and the latest bimester, so a single month reads its own
    // bimester only when both it and the one before are stored; otherwise it reads the year so far, as a monthly average.
    const cumKey = pk.kind === 'bimester' ? (P[`${pk.y}-B6`] ? `${pk.y}-B6` : latestKey.startsWith(`${pk.y}-`) ? latestKey : null) : null;
    if (pk.kind === 'bimester' && P[pk.key] && (pk.b === 1 || P[pk.prev])) {
      const cur = P[pk.key], prev = pk.prev ? P[pk.prev] : null;
      addFns(fns, cur.spending_by_function); if (prev) addFns(fns, prev.spending_by_function, -1);
      spending = cur.spending_liquidated_in_bimester; revenueTotal = cur.revenue_in_bimester;
      result = revenueTotal != null ? revenueTotal - spending : null; spendingLabel = `${pk.b}º bimestre de ${pk.y}`; k = 0.5;
      spendingNote = `Gastos: média mensal do ${spendingLabel} (o relatório de gastos é bimestral).`;
    } else if (pk.kind === 'bimester') {
      const cur = cumKey ? P[cumKey] : null; const n = cur ? +cumKey.slice(6) * 2 : 12;
      if (cur) { addFns(fns, cur.spending_by_function); spending = cur.budget_result_basis === 'despesas empenhadas' ? cur.spending_committed : cur.spending_liquidated;
        revenueTotal = cur.revenue_total; result = cur.budget_result ?? (cur.revenue_total - cur.spending_liquidated); primary = cur.primary_result; }
      spendingLabel = cur ? `${pk.y}${n < 12 ? ` (janeiro a ${window.BIT.MONTHS[n - 1]})` : ''}` : `${pk.y} (sem dado)`; k = 1 / n;
      spendingNote = `Gastos: média mensal de ${spendingLabel}. Para as prefeituras, este site guarda o ano fechado e o último bimestre publicado.`;
    } else {
      const ps = pk.keys.map((k) => P[k]).filter(Boolean);
      for (const p of ps) addFns(fns, p.spending_by_function);
      revenueTotal = ps.reduce((a, p) => a + p.revenue_total, 0);
      spending = ps.reduce((a, p) => a + (p.budget_result_basis === 'despesas empenhadas' ? p.spending_committed : p.spending_liquidated), 0);
      result = ps.length ? ps.reduce((a, p) => a + (p.budget_result ?? (p.revenue_total - p.spending_liquidated)), 0) : null;
      primary = ps.length && ps.every((p) => p.primary_result != null) ? ps.reduce((a, p) => a + p.primary_result, 0) : null;
      spendingLabel = r.label;
      const missing = r.years.filter((y) => !keys.some((k) => k.startsWith(`${y}-`)));
      if (missing.length) spendingLabel += ` (sem dados de ${missing.join(', ')})`;
    }
    const spending_by_function = finishFns(fns, k);
    const end = r.months[r.months.length - 1]; const q = (k) => `${k.slice(0, 4)}-${String(+k.slice(6) * 4).padStart(2, '0')}`;
    const dk = Object.keys(m.debt || {}).filter((k) => q(k) <= end).sort().pop();
    return {
      revenue_top: lines.map(({ label, value, origin }) => ({ label, value, origin })),
      taxes: lines.filter((x) => x.kind === 'tax').map((x) => ({ label: x.label, value: x.value, desc: TAX_INFO[x.label][0], ic: TAX_INFO[x.label][1] })),
      revenue_current_total: line('RECEITAS CORRENTES (I)'), spending_by_function, spending_total: spending_by_function.reduce((a, f) => a + f.value, 0),
      months: monthsCovered, spendingPeriod: spendingLabel, spendingNote,
      contas: { revenueTotal, spending, result, resultBasis: 'empenhadas no ano fechado, liquidadas no ano corrente', primary, debt: dk ? { ...m.debt[dk], at: dk } : null },
    };
  }
  // Municipal taxes paid in a state for the period: SC and RS from every prefeitura's report; other states only 2024.
  function muniTaxesAt(uf, r) {
    const MB = S()[`${uf.toLowerCase()}_municipal_budgets`];
    if (MB) {
      const out = { iss: 0, iptu: 0, itbi: 0, irrf: 0, other_taxes_fees: 0, reported: 0, municipalities: 0 };
      const K = { iss: 'ISS', iptu: 'IPTU', itbi: 'ITBI', irrf: 'IRRF', other_taxes_fees: 'Outros Impostos, Taxas e Contribuições de Melhoria' };
      for (const m of Object.values(MB.municipalities)) {
        out.municipalities++; if (!m.revenue_monthly) continue; let any = false;
        for (const [k, line] of Object.entries(K)) { const a = m.revenue_monthly.lines[line]; if (!a) continue; const s = window.BIT.sum(m.revenue_monthly.months, a, r); if (s.value != null) { out[k] += s.value; any = true; out.months = Math.max(out.months || 0, s.n); } }
        if (any) out.reported++;
      }
      return out;
    }
    return r.mode === 'year' && r.years[0] === 2024 ? (window.BI.municipal && window.BI.municipal[uf]) : null;
  }
  // "Sobrou ou faltou" for a prefeitura.
  function muniContas(name, b, r) {
    const c = b.contas; const K = window.BIK;
    return K.card({
      period: r.mode !== 'month' ? b.spendingPeriod : /bimestre/.test(b.spendingPeriod) ? `${b.spendingPeriod} (o relatório é bimestral)` : `${b.spendingPeriod} (a prefeitura não publica o mês isolado)`,
      inLabel: 'Entrou (todas as receitas da prefeitura)', outLabel: 'Saiu (despesas da prefeitura)',
      inValue: c.revenueTotal, outValue: c.spending, result: c.result,
      resultWhat: `Receitas menos despesas da prefeitura de ${name} no período (Balanço Orçamentário).`,
      second: c.primary != null ? { label: 'Sem contar juros e empréstimos (resultado primário)', value: c.primary } : null,
      debt: c.debt ? { value: c.debt.dc, pct: c.debt.dcl_pct_rcl, what: `Dívida consolidada no fim do ${quad(c.debt.at)}. Descontado o que tem em caixa: ${K.money(c.debt.dcl)}.` } : null,
      sources: [{ label: 'SICONFI, relatórios da prefeitura (RREO e RGF)', url: 'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo' }],
    });
  }

  window.BIL = { stateAt, stateContas, federalAt, latestComplete, lastSoundYear, estimateNote, municipalAt, muniBudgetAt, muniTaxesAt, muniContas, popOf, REV };
})();
