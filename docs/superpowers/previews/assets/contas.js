// "Sobrou ou faltou?" (round 10): whether the government of the country, a state or a municipality spent less or more
// than it collected in the chosen period, and how much it owes. One component for the three levels. Classic script.
(function () {
  const nf = (v, d = 1) => v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const money = (v) => {
    const a = Math.abs(v);
    if (a >= 1e12) return `R$ ${nf(v / 1e12, 2)} tri`;
    if (a >= 1e9) return `R$ ${nf(v / 1e9, 1)} bi`;
    if (a >= 1e6) return `R$ ${nf(v / 1e6, 1)} mi`;
    return `R$ ${Math.round(v).toLocaleString('pt-BR')}`;
  };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // o = { period, inLabel, outLabel, inValue, outValue, result, resultWhat, second: { label, value } , debt: { value, what, pct }, perPerson, sources, notes }
  function card(o) {
    const has = o.result != null;
    const pos = has && o.result >= 0;
    const max = Math.max(o.inValue || 0, o.outValue || 0, 1);
    const pp = (v) => (o.perPerson ? `<small>${o.perPerson(v)}</small>` : '');
    return `<section class="ct ${has ? (pos ? 'pos' : 'neg') : 'na'}">
      <header class="ct-h"><h3>Sobrou ou faltou dinheiro?</h3><span class="ct-p">${esc(o.period)}</span></header>
      <div class="ct-grid">
        <div class="ct-verdict">
          <span class="ct-k">${has ? (pos ? 'Sobrou' : 'Faltou') : 'Sem dado'}</span>
          <b>${has ? money(Math.abs(o.result)) : 'ainda não publicado'}</b>${has ? pp(Math.abs(o.result)) : ''}
          <p>${esc(o.resultWhat || '')}</p>
        </div>
        <div class="ct-bars">
          ${[[o.inLabel, 'in', o.inValue], [o.outLabel, 'out', o.outValue]].sort((a, b) => (b[2] || 0) - (a[2] || 0)).map(([l, cls, x]) => `<div class="ct-row"><span>${esc(l)}</span><i class="${cls}" style="width:${((x || 0) / max) * 100}%"></i><b>${x != null ? money(x) : 'sem dado'}</b></div>`).join('')}
          ${o.second ? `<p class="ct-second">${esc(o.second.label)}: <b class="${o.second.value >= 0 ? 'g' : 'r'}">${o.second.value >= 0 ? 'sobrou' : 'faltou'} ${money(Math.abs(o.second.value))}</b></p>` : ''}
        </div>
        ${o.debt ? `<div class="ct-debt"><span class="ct-k">Quanto deve</span><b>${o.debt.value != null ? money(o.debt.value) : 'sem dado'}</b>
          ${o.debt.pct != null ? `<div class="ct-gauge"><i style="width:${Math.min(100, o.debt.pct)}%"></i></div>` : ''}<p>${esc(o.debt.what || '')}</p></div>` : ''}
      </div>
      ${(o.notes || []).length ? `<ul class="ct-notes">${o.notes.map((n) => `<li>${esc(n)}</li>`).join('')}</ul>` : ''}
      ${(o.sources || []).length ? `<p class="ct-src">Fontes: ${o.sources.map((s) => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)} ↗</a>`).join(' ')}</p>` : ''}
    </section>`;
  }

  // Country level, from data/series/union.json (Governo Central results, Governo Geral gross debt).
  function uniao(U, r) {
    const T = window.BIT;
    const S = (k) => T.sum(U.months, U[k], r).value;
    const debt = T.stock(U.months, U.gross_debt_brl, r), pct = T.stock(U.months, U.gross_debt_pct_gdp, r);
    return card({
      period: r.label, inLabel: 'Entrou (depois dos repasses a estados e municípios)', outLabel: 'Saiu (despesas, sem os juros)',
      inValue: S('revenue_net'), outValue: S('primary_spending'), result: S('nominal_result'),
      resultWhat: 'Conta completa do governo federal, incluindo os juros da dívida (resultado nominal do Governo Central).',
      second: { label: 'Sem contar os juros da dívida (resultado primário)', value: S('primary_result') },
      debt: { value: debt.value, pct: pct.value, what: pct.value != null ? `${nf(pct.value)}% de tudo o que o país produz em um ano (PIB), em ${window.BIT.fmtMonth(debt.at)}. Dívida bruta de União, estados e municípios.` : '' },
      notes: [`Só de juros da dívida, os juros que correram no período somaram ${money(Math.abs(S('nominal_interest') || 0))} (juros nominais do Governo Central, Banco Central; não é o valor pago em dinheiro).`],
      sources: [{ label: 'Tesouro Nacional, Resultado do Tesouro Nacional', url: U.sources[0].page || U.sources[0].url },
        { label: 'Banco Central, dívida bruta (SGS 13761 e 13762)', url: U.sources.find((s) => (s.fields || []).includes('gross_debt_brl')).url }],
    });
  }

  // Compact version for the home hero.
  function uniaoMini(U, r) {
    const T = window.BIT; const res = T.sum(U.months, U.nominal_result, r).value;
    const prim = T.sum(U.months, U.primary_result, r).value;
    const PS = window.BI.series.public_sector_primary; const psx = PS ? T.sum(PS.months, PS.primary_result, r) : null;
    const ps = psx && psx.n === psx.of ? psx.value : null;
    const debt = T.stock(U.months, U.gross_debt_brl, r), pct = T.stock(U.months, U.gross_debt_pct_gdp, r);
    // Two different things, labelled so they cannot be read as one another: the deficit of the period (a flow, federal
    // government) and the debt at the end of the period (a stock, Union, states and municipalities together).
    const atM = debt.at ? window.BIT.fmtMonth(debt.at, true) : '';
    return `<div class="ctm ${res >= 0 ? 'pos' : 'neg'}"><span class="ctm-t">As contas do Brasil · ${esc(r.short)}</span>
      <span class="ctm-v"><b>${res >= 0 ? 'Superávit' : 'Déficit'} de ${money(Math.abs(res))}</b>no período, o governo federal ${res >= 0 ? 'arrecadou mais do que gastou' : 'gastou mais do que arrecadou'}, contando os juros</span>
      <span class="ctm-d">Antes dos juros: <b class="${prim >= 0 ? 'g' : 'r'}">${prim >= 0 ? 'superávit' : 'déficit'} de ${money(Math.abs(prim))}</b><small>governo federal; ${ps != null ? `todo o setor público: ${ps >= 0 ? 'superávit' : 'déficit'} de ${money(Math.abs(ps))}` : ''}</small></span>
      <span class="ctm-d">Dívida acumulada: ${money(debt.value)}, ${nf(pct.value)}% do PIB, em ${atM}<small>União, estados e municípios juntos</small></span>${window.BIG ? window.BIG.presidentLine(r) : ''}<button type="button" class="ctm-go" data-open-brasil>Ver as contas do Brasil ›</button></div>`;
  }

  // Year-by-year bars (green up = sobrou, red down = faltou), the selected years outlined.
  function years(U, key, title, sub, r) {
    const ys = [...new Set(U.months.map((m) => +m.slice(0, 4)))];
    const val = ys.map((y) => U.months.reduce((a, m, i) => (m.startsWith(String(y)) && U[key][i] != null ? a + U[key][i] : a), 0));
    const max = Math.max(...val.map(Math.abs), 1);
    const last = U.months[U.months.length - 1];
    // The zero line sits where the data needs it: an all-deficit series gets almost all of the height below zero.
    const up = Math.max(...val, 0), dn = Math.max(...val.map((v) => -v), 0);
    const rows = `${Math.max(up / (up + dn), 0.06)}fr ${Math.max(dn / (up + dn), 0.06)}fr auto`;
    return `<section class="yr"><h3>${esc(title)}</h3><p>${esc(sub)}</p><div class="yr-chart" style="--rows:${rows}">${ys.map((y, i) => {
      const v = val[i], h = (Math.abs(v) / (v >= 0 ? (up || 1) : (dn || 1))) * 100, sel = r.years.includes(y);
      const partial = String(y) === last.slice(0, 4) && last.slice(5, 7) !== '12';
      return `<div class="yr-col${sel ? ' sel' : ''}"><div class="up">${v >= 0 ? `<i style="height:${h}%"></i>` : ''}</div><div class="dn">${v < 0 ? `<i style="height:${h}%"></i>` : ''}</div>
        <b>${y}${partial ? '*' : ''}<small>${v >= 0 ? '+' : '-'}${money(Math.abs(v)).replace('R$ ', '')}</small></b></div>`;
    }).join('')}</div><p>* ${last.slice(0, 4)} até ${window.BIT.fmtMonth(last)}.</p></section>`;
  }

  // "Mandato a mandato": the same measures for every presidential mandate, side by side, so a surplus
  // year or the growth of the debt is visible without hunting for it. Debt = everything owed, accumulated (a stock);
  // deficit or surplus = one period's result (a flow). Central government from the Tesouro (RTN); the whole public sector
  // (Union, states, municipalities and state companies) and the debt from the Banco Central.
  function mandates(U, PS, current) {
    const T = window.BIT, last = U.latest.nominal_result;
    const MAND = [['2019-2022', 2019, 2022], ['2023-2026', 2023, 2026]];
    const sumY = (months, arr, y) => months.reduce((a, m, i) => (m.startsWith(String(y)) && arr[i] != null ? a + arr[i] : a), 0);
    const debtAt = (m) => { const i = U.months.indexOf(m); return i >= 0 ? { v: U.gross_debt_brl[i], p: U.gross_debt_pct_gdp[i], at: m } : null; };
    const sign = (v) => (v >= 0 ? 'sobrou' : 'faltou');
    const cols = MAND.map(([key, y0, y1]) => {
      const r = T.resolve({ mode: 'mandate', mandate: key, year: y0, month: last }, last);
      const startDebt = y0 === 2019 ? { v: U.baseline.gross_debt_brl, p: U.baseline.gross_debt_pct_gdp, at: U.baseline.month } : debtAt(`${y0 - 1}-12`);
      const endM = r.months[r.months.length - 1], endDebt = debtAt(endM);
      const years = []; for (let y = y0; y <= Math.min(y1, +last.slice(0, 4)); y++) years.push(y);
      const fedPrim = years.reduce((a, y) => a + sumY(U.months, U.primary_result, y), 0);
      const nominal = years.reduce((a, y) => a + sumY(U.months, U.nominal_result, y), 0);
      const psY = years.map((y) => ({ y, v: PS ? sumY(PS.months, PS.primary_result, y) : null, partial: String(y) === last.slice(0, 4) && last.slice(5, 7) !== '12' }));
      const psSum = PS ? psY.reduce((a, x) => a + x.v, 0) : null;
      const max = Math.max(...psY.map((x) => Math.abs(x.v || 0)), 1);
      const bars = psY.map((x) => `<div class="mm-bar${x.v >= 0 ? ' pos' : ''}"><span class="mm-track"><i style="height:${(Math.abs(x.v) / max) * 100}%"></i></span><b>${x.v >= 0 ? '+' : '-'}${money(Math.abs(x.v)).replace('R$ ', '')}</b><small>${x.y}${x.partial ? '*' : ''}</small></div>`).join('');
      const dv = endDebt.v - startDebt.v, dp = endDebt.p - startDebt.p;
      return `<article class="mm-col${current && r.years.some((y) => current.years.includes(y)) ? ' cur' : ''}">
        <header><h4>${y0} a ${y1}${r.partial ? ` <small>(até ${T.fmtMonth(endM, true)})</small>` : ''}</h4>${window.BIG ? window.BIG.presidentLine(r) : ''}</header>
        <div class="mm-debt"><span class="mm-k">Dívida bruta (tudo o que o governo deve)</span>
          <div class="mm-from"><b>${money(startDebt.v)}</b><small>${nf(startDebt.p)}% do PIB, ${T.fmtMonth(startDebt.at, true)}</small></div>
          <span class="mm-arrow">→</span>
          <div class="mm-from"><b>${money(endDebt.v)}</b><small>${nf(endDebt.p)}% do PIB, ${T.fmtMonth(endDebt.at, true)}</small></div>
          <p class="mm-chg">${dv >= 0 ? '+' : '-'}${money(Math.abs(dv))} · ${dp >= 0 ? '+' : '-'}${nf(Math.abs(dp))} ponto${Math.abs(dp) >= 2 ? 's' : ''} do PIB</p></div>
        <div class="mm-res"><span class="mm-k">Antes dos juros, todo o setor público (União, estados, municípios e estatais)</span>
          <p class="mm-big ${psSum >= 0 ? 'g' : 'r'}">${sign(psSum)} ${money(Math.abs(psSum))} no mandato</p>
          <div class="mm-bars">${bars}</div></div>
        <ul class="mm-list">
          <li><span>Antes dos juros, só o governo federal</span><b class="${fedPrim >= 0 ? 'g' : 'r'}">${sign(fedPrim)} ${money(Math.abs(fedPrim))}</b></li>
          <li><span>Com os juros da dívida, governo federal</span><b class="${nominal >= 0 ? 'g' : 'r'}">${sign(nominal)} ${money(Math.abs(nominal))}</b></li>
        </ul></article>`;
    });
    // Debt as a share of GDP, month by month, with the mandates marked: the fairest way to compare debt across years.
    const ms = [U.baseline.month, ...U.months.filter((m, i) => U.gross_debt_pct_gdp[i] != null)];
    const ps = [U.baseline.gross_debt_pct_gdp, ...U.months.map((m, i) => U.gross_debt_pct_gdp[i]).filter((x) => x != null)];
    const W = 640, H = 150, lo = 60, hi = 95, x = (i) => 36 + (i / (ms.length - 1)) * (W - 76), y = (v) => 10 + (1 - (v - lo) / (hi - lo)) * (H - 30);
    const iSplit = ms.indexOf('2022-12'), iPeak = ps.indexOf(Math.max(...ps));
    const pt = (i, cls, txt, dy = -8) => `<circle cx="${x(i)}" cy="${y(ps[i])}" r="3.5" class="${cls}"/><text x="${x(i)}" y="${y(ps[i]) + dy}" class="${cls}" text-anchor="middle">${txt}</text>`;
    const chart = `<svg viewBox="0 0 ${W} ${H}" class="mm-svg" role="img" aria-label="Dívida bruta em porcentagem do PIB, mês a mês">
      <rect x="${x(0)}" y="6" width="${x(iSplit) - x(0)}" height="${H - 26}" class="b1"/><rect x="${x(iSplit)}" y="6" width="${x(ms.length - 1) - x(iSplit)}" height="${H - 26}" class="b2"/>
      ${[70, 80, 90].map((g) => `<line x1="36" x2="${W - 40}" y1="${y(g)}" y2="${y(g)}" class="grid"/><text x="30" y="${y(g) + 4}" text-anchor="end" class="ax">${g}%</text>`).join('')}
      <polyline points="${ps.map((v, i) => `${x(i)},${y(v)}`).join(' ')}" class="line"/>
      ${pt(0, 'p', `${nf(ps[0])}%`, 17)}${pt(iPeak, 'p', `pico ${nf(ps[iPeak])}%`)}${pt(iSplit, 'p', `${nf(ps[iSplit])}%`, 16)}${pt(ps.length - 1, 'p', `${nf(ps[ps.length - 1])}%`)}
      <text x="${(x(0) + x(iSplit)) / 2}" y="${H - 6}" text-anchor="middle" class="ax">2019 a 2022</text><text x="${(x(iSplit) + x(ms.length - 1)) / 2}" y="${H - 6}" text-anchor="middle" class="ax">2023 a 2026</text></svg>`;
    return `<section class="mm"><h3>Mandato a mandato</h3>
      <p class="mm-lead">Os mesmos números para cada mandato presidencial. <b>Déficit ou superávit</b> é o resultado de um período: gastou mais ou menos do que arrecadou. <b>Dívida</b> é tudo o que o governo deve, acumulado ao longo dos anos.</p>
      <div class="mm-grid">${cols.join('')}</div>
      <div class="mm-chart"><span class="mm-k">Dívida bruta em % do PIB, mês a mês (Banco Central)</span>${chart}</div>
      <p class="mm-note">* ano até ${T.fmtMonth(last)}. Dívida bruta do governo geral (União, estados e municípios), Banco Central, SGS 13761 e 13762. Antes dos juros: resultado primário; setor público consolidado pelo Banco Central (SGS 4649), governo federal pelo Tesouro (Resultado do Tesouro Nacional). Com os juros: resultado nominal do Governo Central.</p></section>`;
  }

  window.BIK = { card, uniao, uniaoMini, years, money, mandates };
})();
