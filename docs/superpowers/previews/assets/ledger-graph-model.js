// The network graph's model (D133, D134). For any period of the map's selector it builds the União, the 27 states, the
// fan around each state (each federal tax paid there, what came back) and, in SC and RS, every prefeitura, using only the
// map's own functions (serieslayer.js: BIL.federalAt, BIL.stateAt, BIL.municipalAt) over the bundle the map reads, so the
// graph shows the map's number for the same period. Interest comes from the ledger (bi-ledger-interest.js).
// The checks are computed here, shown under the graph, and run over every period by tools/ledger-graph-periods-check.cjs.
(function () {
  const UFS = 'AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO'.split(' ');
  const TAX = { import_tax: 'Imposto de importação', export_tax: 'Imposto de exportação', ipi: 'IPI', irpf: 'IR pessoa física',
    irpj: 'IR pessoa jurídica', irrf: 'IR retido na fonte', iof: 'IOF', itr: 'ITR', cofins: 'Cofins', pis_pasep: 'PIS/Pasep',
    csll: 'CSLL', cide_fuels: 'CIDE combustíveis', civil_servant_social_security_pss: 'Contribuição dos servidores (PSS)',
    other_rfb_revenue: 'Outras receitas da Receita', social_security_contributions_rgps: 'Contribuição ao INSS',
    administered_by_other_agencies: 'Receitas de outros órgãos' };
  const STATE_TAXES = new Set(['ICMS', 'IPVA', 'ITCD (heranças e doações)', 'Outros impostos e taxas', 'ISS', 'IPTU', 'ITBI', 'IBS']);
  const CITY_SERIES = { SC: 'sc_municipal_federal', RS: 'rs_municipal_federal' };
  const TOL = 0.5; // reais: the worst real gap over every period is R$ 0,08 (source cents); the R$ 1 control must fail

  // The map's city period, copied from statehero.js effective() (D46): a single month reads its whole year, and a period
  // that reaches a year whose municipal revenue is not published yet falls back to the last published year, labelled.
  function cityPeriod(S, r) {
    const last = S.months.slice(-1)[0];
    const annual = Object.values(S.municipalities)[0].federal_revenue_annual;
    const lastYear = Math.max(...Object.keys(annual).filter((y) => annual[y] != null).map(Number));
    const e = r.mode === 'month' ? window.BIT.resolve({ mode: 'year', year: r.years[0] }, last) : r;
    if (e.years.every((y) => y <= lastYear)) return e;
    return { ...window.BIT.resolve({ mode: 'year', year: lastYear }, last), fallbackFrom: r.label };
  }
  const monthsOfSpan = ([a, b]) => { const out = []; let [y, m] = [+a.slice(0, 4), +a.slice(5, 7)];
    for (;;) { const s = `${y}-${String(m).padStart(2, '0')}`; out.push(s); if (s === b) return out; [y, m] = m === 12 ? [y + 1, 1] : [y, m + 1]; } };

  // control: 'tax' adds R$ 1 to the Cofins of SC, 'loose' adds a point with no link; each must fail its check.
  function build(r, control = null) {
    const S = window.BI.series, T = window.BIT, L = window.BIL;
    const F = S.federal_by_uf_monthly, TS = S.federal_spending_two_step_by_uf;
    const rows = Object.fromEntries(UFS.map((uf) => [uf, L.federalAt(uf, r)]));
    const missing = UFS.filter((uf) => !rows[uf] || !rows[uf].ok);
    if (missing.length) {
      const lc = L.latestComplete();
      return { ok: false, label: r.label, missing, reason: `${r.label[0].toUpperCase()}${r.label.slice(1)} ainda não tem todos os dados em ${missing.length} estados. O último mês com todos os dados é ${T.fmtMonth(lc)}.` };
    }
    const f0 = rows.SC;
    const broken = TS.broken_months || {};
    const ms = r.months.filter((m) => !broken[m]).slice(0, f0.months); // federalAt's own months: the cut, without broken files
    const rr = { ...r, months: ms };
    const geo = Object.fromEntries(window.BI_GEO.brazil.map((g) => [g.uf, g]));
    const nodes = [], links = [], fails = { tax: [], branch: [], city: [] }, cities = {};
    nodes.push({ id: 'uniao', label: 'União', kind: 'uniao', fx: 0, fy: 150, fz: 40 });
    nodes.push({ id: 'credores', label: 'Credores da dívida', kind: 'credores', fx: 430, fy: 110, fz: 150 });
    for (const uf of UFS) {
      const f = rows[uf], s = L.stateAt(uf, r), u = F.uf[uf], g = geo[uf], hub = `uf:${uf}`;
      const sum = (a) => T.sum(F.months, a, rr).value || 0;
      nodes.push({ id: hub, label: uf, name: g.name, kind: 'state', color: uf === 'DF' ? 'none' : f.balance > 0 ? 'green' : 'red',
        fx: Math.round((g.label[0] - 2) * 62) / 10, fy: 0, fz: Math.round(-(g.label[1] + 44) * 62) / 10,
        sent: f.sent, received: f.received, balance: f.balance, population: f.population, per_person_month: f.perPersonMonth });
      const taxes = Object.fromEntries(Object.entries(f.byTax).filter(([, v]) => v));
      if (control === 'tax' && uf === 'SC') taxes.cofins += 1;
      if (Math.abs(Object.values(taxes).reduce((a, v) => a + v, 0) - f.sent) > TOL) fails.tax.push(uf);
      for (const [k, v] of Object.entries(taxes)) {
        nodes.push({ id: `${hub}:tax:${k}`, label: TAX[k], kind: 'tax', state: uf, v });
        links.push({ source: `${hub}:tax:${k}`, target: hub, kind: 'tax', v });
      }
      links.push({ source: hub, target: 'uniao', kind: 'paid', v: f.sent });
      links.push({ source: 'uniao', target: hub, kind: 'back', v: f.received });
      const parts = [['benefits', 'Benefícios (INSS, BPC, Bolsa Família)', (f.inss || 0) + (f.bpc || 0) + (f.bolsa || 0)],
        ['federal_spending', 'Gasto federal no estado', f.fedSpending || 0],
        ['gov', 'Governo do estado (repasses)', sum(u.transfers.to_state_government)], ['mun', 'Prefeituras (repasses)', sum(u.transfers.to_municipalities)]];
      if (f.fcdf) parts.push(['fcdf', 'Fundo Constitucional do DF', f.fcdf]);
      if (Math.abs(parts.reduce((a, p) => a + p[2], 0) - f.received) > TOL) fails.branch.push(uf);
      for (const [k, label, v] of parts) {
        if (!v) continue;
        nodes.push({ id: `${hub}:b:${k}`, label, kind: 'branch', state: uf, v });
        links.push({ source: hub, target: `${hub}:b:${k}`, kind: 'back_leaf', v });
      }
      const has = (k) => parts.some((p) => p[0] === k && p[2]);
      if (s && has('gov')) {
        const tax = s.revenue_top.filter((x) => STATE_TAXES.has(x.label)).reduce((a, x) => a + x.value, 0);
        const extra = { cover: s.coverLabel || null };
        if (tax) links.push({ source: hub, target: `${hub}:b:gov`, kind: 'state', v: tax, label: 'impostos estaduais', ...extra });
        if (s.to_municipalities && has('mun')) links.push({ source: `${hub}:b:gov`, target: `${hub}:b:mun`, kind: 'state', v: s.to_municipalities, label: 'parte das prefeituras', ...extra });
      }
      const key = CITY_SERIES[uf];
      if (key && S[key] && has('mun')) {
        const CS = S[key], e = cityPeriod(CS, r);
        let total = 0, n = 0;
        for (const code of Object.keys(CS.municipalities)) {
          const a = L.municipalAt(code, rr), c = L.municipalAt(code, e);
          const v = a && a.federal_transfers;
          if (!v) continue;
          total += v; n += 1;
          const bal = c ? c.balance : null;
          nodes.push({ id: `mun:${code}`, label: a.name, kind: 'municipality', state: uf, v,
            federal_revenue: c ? c.federal_revenue : null, received: c ? c.received : null, balance: bal, population: c ? c.population : null,
            per_person_month: bal != null && c.population ? bal / c.population / e.months.length : null });
          links.push({ source: `${hub}:b:mun`, target: `mun:${code}`, kind: 'municipal', v });
        }
        const stateTotal = parts.find((p) => p[0] === 'mun')[2];
        cities[uf] = { state_total: stateTotal, municipal_series: total, gap: stateTotal - total, municipalities: n,
          color_label: `${e.label}${e.fallbackFrom ? `, estimado (a arrecadação por município de ${e.fallbackFrom} ainda não foi publicada)` : r.mode === 'month' ? ' (a arrecadação por município é anual)' : ''}`,
          estimated: Boolean(e.fallbackFrom || e.years.includes(2025)) };
        if (total - stateTotal > TOL) fails.city.push(uf); // the cities cannot add up to more than the state total
      }
    }
    // The União totals for the same months, the formula of the map's União block (unionAt in the home).
    const ti = new Map(TS.months.map((m, i) => [m, i]));
    const usum = (a) => ms.reduce((x, m) => x + (a[ti.get(m)] || 0), 0);
    const unionOk = ms.every((m) => ti.has(m) && TS.union.official_returned_rtn[ti.get(m)] != null);
    const st = (k) => UFS.reduce((a, uf) => a + rows[uf][k], 0);
    const I = window.BI_LEDGER_INTEREST, ii = new Map(I.months.map((m, i) => [m, i]));
    const interestOk = ms.every((m) => ii.has(m));
    const isum = (a) => ms.reduce((x, m) => x + a[ii.get(m)], 0);
    const union = { sent_total: unionOk ? usum(TS.union.official_revenue) : null, returned_total: unionOk ? usum(TS.union.official_returned_rtn) : null,
      sent_states: st('sent'), received_states: st('received'),
      interest_accrual: interestOk ? isum(I.accrual) : null, interest_cash: interestOk ? isum(I.cash) : null, interest_sources: I.sources };
    union.returned_without_state = unionOk ? union.returned_total - union.received_states : null;
    if (union.interest_accrual) links.push({ source: 'uniao', target: 'credores', kind: 'interest', v: union.interest_accrual });
    if (control === 'loose') nodes.push({ id: 'control:loose', label: 'ponto de controle', kind: 'tax', state: 'SC', v: 1 });

    // Checks. The official split by state is the annual table of the two-step balance (build_two_step_balance.py,
    // checked to the cent there); it is compared when the period is made of whole years with the same months.
    const ids = new Set(nodes.map((n) => n.id)), deg = new Map(nodes.map((n) => [n.id, 0]));
    const dangling = links.filter((l) => !ids.has(l.source) || !ids.has(l.target)).length;
    for (const l of links) { if (deg.has(l.source)) deg.set(l.source, deg.get(l.source) + 1); if (deg.has(l.target)) deg.set(l.target, deg.get(l.target) + 1); }
    const loose = [...deg].filter(([, d]) => !d).map(([id]) => id);
    let official = { ok: null, detail: 'o total oficial dividido por estado é anual; neste período a conferência é a dos leques' };
    const yrs = r.mode === 'month' ? [] : r.years.map(String);
    if (yrs.length && yrs.every((y) => TS.years[y] && TS.years[y].check_passed)) {
      const span = yrs.flatMap((y) => monthsOfSpan(TS.years[y].months));
      if (span.length === ms.length && span.every((m, i) => m === ms[i])) {
        const ub = (side) => yrs.reduce((a, y) => a + TS.years[y].union_block[side].states, 0);
        const ds = union.sent_states - ub('sent'), dr = union.received_states - ub('returned');
        const cents = (v) => (Math.abs(v) < 0.005 ? 0 : v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        official = { ok: Math.abs(ds) <= TOL && Math.abs(dr) <= TOL, detail: `os 27 estados somam o total oficial dividido por estado (diferença de R$ ${cents(ds)} no que foi pago e R$ ${cents(dr)} no que voltou)` };
      } else {
        official = { ok: null, detail: `o total oficial por estado cobre ${span.length} meses e este período ${ms.length}; a conferência é a dos leques` };
      }
    }
    const checks = [
      { id: 'taxes', ok: !fails.tax.length, detail: fails.tax.length ? `impostos que não somam o que o estado pagou: ${fails.tax.join(', ')}` : 'em cada estado, os impostos somam o que ele pagou à União' },
      { id: 'branches', ok: !fails.branch.length, detail: fails.branch.length ? `o que voltou não fecha em: ${fails.branch.join(', ')}` : 'em cada estado, as partes somam o que voltou da União' },
      { id: 'cities', ok: !fails.city.length, detail: fails.city.length ? `prefeituras somam mais que o estado em: ${fails.city.join(', ')}` : 'as prefeituras nunca somam mais que o repasse do estado' },
      { id: 'connected', ok: !dangling && !loose.length, detail: dangling || loose.length ? `${dangling} ligações sem ponto e ${loose.length} pontos sem ligação` : `${nodes.length} pontos e ${links.length} ligações, nenhum ponto solto` },
      { id: 'official', ok: official.ok, detail: official.detail },
    ];
    return { ok: true, label: f0.label, mode: r.mode, months: ms, nodes, links, union, cities, checks,
      estimated: f0.estimatedMonths.length ? { months: f0.estimatedMonths, note: L.estimateNote() } : null,
      dropped: f0.droppedMonths || [], passed: checks.every((c) => c.ok !== false) };
  }
  window.BILG = { build, UFS };
})();
