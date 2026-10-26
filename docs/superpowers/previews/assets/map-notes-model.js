// The map's notes ("Como ler o mapa") and the pieces the map and the notes share (spec home-trim, D159, section 5): the
// formatters, the União block, the rows of the 27 states, the colour scale and the facts about the DF. The map on Início
// uses them for its card and legend; build-map-notes.cjs runs notes() for every period and measure and writes
// assets/map-notes.js, which the notes page reads without the map's data. Classic script; exposes window.BIMN.
(function () {
  const bi = (v) => `R$ ${(v / 1e9).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} bi`;
  const reais = (v) => `R$ ${Math.round(v).toLocaleString('pt-BR')}`;
  const cents = (v) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  // D94, D115: values in tenths of a billion that add up by hand. Largest remainder: each part is rounded down, and the
  // tenths still missing for the rounded total go to the parts that lost the most, so the parts always sum to the total.
  const tenths = (vals, total) => {
    const raw = vals.map((x) => x / 1e8), out = raw.map(Math.floor); let left = Math.round(total / 1e8) - out.reduce((a, x) => a + x, 0);
    const order = raw.map((x, i) => [x - out[i], i]).sort((a, b) => b[0] - a[0]);
    for (let k = 0; left > 0 && k < order.length; k++, left--) out[order[k][1]]++;
    for (let k = order.length - 1; left < 0 && k >= 0; k--, left++) out[order[k][1]]--;
    return out;
  };
  const num1 = (n) => `${n < 0 ? '−' : ''}${(Math.abs(n) / 10).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}`;
  const biT = (n) => `${n < 0 ? '−' : ''}R$ ${num1(Math.abs(n))} bi`;
  const tri = (v) => `R$ ${(v / 1e12).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} tri`;
  // D115: the União block for the map's months. Sent: the Receita national total minus the 27 states. Paid: RTN line 2
  // plus line 4 minus what returned to the 27 states, with its parts (data/series/federal-spending-two-step-by-uf.json,
  // built by pipelines/ug/build_two_step_balance.py, which checks 27 states + União = total to the cent).
  const unionAt = (rows, currentR) => {
    const S = window.BI.series || {}, TS = S.federal_spending_two_step_by_uf;
    if (!currentR || !TS || !TS.union || !rows.length || !rows.every((s) => s.ok && s.months === rows[0].months)) return null;
    const broken = TS.broken_months || {}, ms = currentR.months.filter((m) => !broken[m]).slice(0, rows[0].months);
    const ti = new Map(TS.months.map((m, i) => [m, i]));
    if (!ms.every((m) => ti.has(m) && TS.union.official_returned_rtn[ti.get(m)] != null)) return null;
    const sum = (a) => ms.reduce((x, m) => x + (a[ti.get(m)] || 0), 0), st = (k) => rows.reduce((x, s) => x + (s[k] || 0), 0);
    let central = sum(TS.no_state.central_benefits);
    for (const y of new Set(ms.map((m) => m.slice(0, 4)))) {
      const M = TS.mte_annual[y], my = ms.filter((m) => m.startsWith(y));
      if (M && my.length === 12) central += M.no_state;
      else if (M) central += my.reduce((x, m) => x + (TS.union.unemployment_and_wage_bonus_portal_mte_year[ti.get(m)] || 0), 0);
    }
    const sent = { official: sum(TS.union.official_revenue), states: st('sent') }; sent.union = sent.official - sent.states;
    const ret = { official: sum(TS.union.official_returned_rtn), states: st('received') }; ret.union = ret.official - ret.states;
    const parts = [
      ['programas nacionais que o arquivo do gasto não põe em nenhum estado (como as folhas das Forças Armadas e as compras do Ministério da Saúde)', sum(TS.no_state.executive)],
      ['aposentadorias e pensões do INSS pagas além do que o boletim põe por estado', sum(TS.union.inss_rtn) - st('inss')],
      ['seguro-desemprego, abono e auxílios pagos sem estado', central],
      ['sentenças judiciais, precatórios e outros pagamentos que só a base do Tesouro traz', sum(TS.union.tesouro_base_executive_not_in_portal)],
      ['inversões financeiras, como os fundos constitucionais emprestados pelos bancos regionais', sum(TS.union.financial_investments_group_5)],
      ['pagamentos a entidades privadas, organismos internacionais e ao exterior', sum(TS.union.private_international_abroad)],
      ['repasses a governos estaduais e municipais que o Portal não põe em nenhum estado', sum(TS.union.public_transfers_tesouro) - st('transfers')],
      ['Legislativo, Judiciário, MPU e DPU sem estado (Justiça Federal, MPF, DPU)', sum(TS.no_state.other_branches)],
      ['BPC pago além da série do MDS por estado', sum(TS.union.bpc_rtn) - st('bpc')],
    ].map(([label, value]) => ({ label, value }));
    parts.push({ label: 'diferença entre as bases (Tesouro, Portal, MDS e Previdência)', value: ret.union - parts.reduce((a, x) => a + x.value, 0) });
    ret.parts = parts;
    return { sent, ret, months: ms.length, population: rows.reduce((a, s) => a + s.population, 0), label: rows[0].label };
  };
  const DF_REVIEW = false;  // D146: the DF shows the estimate (BIL.federalAt), marked as such
  const rowsAt = (states, currentR) => states.map((s) => { const f = window.BIL.federalAt(s.uf, currentR); return { uf: s.uf, name: s.name, ...f, returned_per_real: f.ok ? f.received / f.sent : null, label: f.label || currentR.label, inReview: DF_REVIEW && s.uf === 'DF' }; });
  const scale26 = (value) => (rows) => {
    const vs = rows.filter((s) => s.ok && s.uf !== 'DF').map(value); const df = rows.find((s) => s.uf === 'DF');
    const hi = Math.max(...vs, 1e-9), lo = Math.min(...vs, -1e-9), d = df && df.ok && !df.inReview ? value(df) : null;
    return { maxPositive: Math.max(hi, 1e-9), maxNegative: Math.max(-lo, 1e-9), dfOut: d != null && (d > hi || d < lo) };
  };
  // The value each measure colours the map by (the same as METRICS in the map's script).
  const VALUE = { perCapita: (s) => s.perPersonMonth, total: (s) => s.balance, ratio: (s) => Math.log(s.sent / s.received) };
  function dfFacts(rowsNow, dfRow) {
    let dfFacts = [];
    // Facts about the DF from the period's own numbers (D114: what the União pays with no state is no longer in the DF).
    const okRows = rowsNow.filter((s) => s.ok), backPP = (s) => s.received / s.population / s.months;
    const topBack = okRows.reduce((a, s) => (backPP(s) > backPP(a) ? s : a), okRows[0]);
    const tax = (s, k) => ((s.byTax || {})[k] || 0), pss = okRows.reduce((a, s) => a + tax(s, 'civil_servant_social_security_pss'), 0);
    const pssShare = pss > 0 ? Math.round((tax(dfRow, 'civil_servant_social_security_pss') / pss) * 100) : null;
    dfFacts = [
      topBack && topBack.uf === 'DF' ? `o DF é também o estado para onde mais volta dinheiro da União por pessoa: ${reais(backPP(dfRow))} por mês${dfRow.fcdf ? `, dos quais ${reais(dfRow.fcdf / dfRow.population / dfRow.months)} do Fundo Constitucional do DF` : ''}` : '',
      pssShare != null ? `${pssShare}% da contribuição previdenciária dos servidores federais do país foi registrada no DF, porque a Receita conta o imposto retido onde fica a sede de quem paga` : '',
    ].filter(Boolean);
    return { facts: dfFacts, pssShare };
  }
  // GD33: every number shows the last date the government published it (data/release-dates.json, read at the source).
  const relDate = (id) => { const r = window.BI.releases[id]; if (!r.date) return r.unchecked ? 'data a conferir' : 'sem data publicada'; const d = r.date; return d.length === 7 ? `${d.slice(5, 7)}/${d.slice(0, 4)}` : `${d.slice(8, 10)}/${d.slice(5, 7)}/${d.slice(0, 4)}`; };
  const SRC = [['receita', 'Receita'], ['portal_exec', 'Portal, gastos'], ['portal_transfers', 'Portal, repasses'], ['tesouro_base', 'Tesouro'], ['beps', 'Previdência'], ['ibge', 'IBGE'], ['mds', 'MDS']];
  const dates = () => SRC.map(([id, l]) => [l, window.BI.releases[id].what, relDate(id)]);
  // The notes of the map for the rows of a period and a measure, as Início showed them under the map until D159.
  function notes(rowsNow, currentR, metric) {
    const est = rowsNow.some((s) => s.estimatedMonths && s.estimatedMonths.length);
    const note = window.BIL && window.BIL.estimateNote ? window.BIL.estimateNote() : null;
    const sda = rowsNow.find((s) => s.ok && s.centralWithoutState);
    const U = unionAt(rowsNow, currentR);
    const [sS, sU] = U ? tenths([U.sent.states, U.sent.union], U.sent.official) : [], [rS, rU] = U ? tenths([U.ret.states, U.ret.union], U.ret.official) : [];
    const scaleNow = scale26(VALUE[metric])(rowsNow);
    const dfRow = rowsNow.find((s) => s.uf === 'DF');
    const dfFacts = scaleNow.dfOut ? dfFactsOf(rowsNow, dfRow).facts : [];
    const notes = [];
    if (est && note) notes.push(note.text);
    if (sda) notes.push(`Benefícios pagos a pessoas do país inteiro por uma unidade central (seguro-desemprego, abono e, em 2020 e 2021, auxílio emergencial e BEm) contam no estado quando o arquivo diz qual é; seguro-desemprego e abono, também no ano inteiro em que o Ministério do Trabalho publica por estado (hoje, 2024). Neste período, ${bi(sda.centralWithoutState)} ficam com a União.`);
    if (U) {
      const P = U.ret.parts.slice().sort((a, b) => b.value - a.value); const pt = tenths(P.map((x) => x.value), rU * 1e8);
      notes.push(`União, ${U.label}: o que não tem estado é da União. Entrou sem estado ${biT(sU)}: arrecadação federal que o arquivo da Receita não põe em nenhum estado. Pago sem estado ${biT(rU)} = ${P.map((x, i) => `${x.label} ${biT(pt[i])}`).join(' + ')}. Somados aos 27 estados, os dois lados dão o total oficial: a arrecadação da Receita Federal e a despesa mais os repasses do Tesouro (RTN, o mesmo de "As contas do Brasil").`);
    }
    if (scaleNow.dfOut) notes.push('A escala de cor é feita com os outros 26 estados. O DF fica muito além de todos eles e aparece na cor mais escura, com o próprio número na legenda.');
    if (dfFacts.length) notes.push(`DF, ${dfRow.label}: ${dfFacts.join('; ')}.`);
    if (dfRow && dfRow.dfEstimate) notes.push(`DF, estimativa: a Receita registra no DF o imposto que órgãos e empresas com sede em Brasília retêm ou pagam pelo país inteiro (Lei 9.779/1999, art. 15), inclusive o dos salários que a própria União paga. Em cada imposto, o DF conta no máximo a sua parte no PIB do Brasil (${(dfRow.dfEstimate.share * 100).toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%, IBGE, PIB dos Municípios ${dfRow.dfEstimate.year}); o que passa disso (${bi(dfRow.dfEstimate.excess)} em ${dfRow.label}) vai para a União na tabela abaixo. É uma estimativa: nenhum arquivo aberto separa esse imposto por estado.`);
    if (dfRow && dfRow.inReview) notes.push('DF em revisão: o DF fica sem cor e fora da comparação entre os estados. A Receita registra no DF o imposto retido por órgãos e empresas com sede em Brasília, inclusive o dos salários que a própria União paga; para saber quanto o DF de fato gera e quanto recebe, os dois lados precisam ser separados, e essa conta (o livro de fluxos) ainda está em construção. Os números do DF continuam somados aos 27 estados na tabela da União.');
    const dropped = (rowsNow.find((s) => s.droppedMonths && s.droppedMonths.length) || {}).droppedMonths;
    if (dropped) notes.push(`O arquivo do Portal da Transparência de ${dropped.map((m) => window.BIT.fmtMonth(m)).join(', ')} veio com todos os valores zerados (gerado pela CGU em 01/10/2026). O período é calculado sem esse mês, na arrecadação e no que voltou.`);
    notes.push('"Voltou" soma os repasses da União, INSS, BPC, Bolsa Família, o Fundo Constitucional do DF e o gasto federal no estado pela regra em duas etapas: vale o estado onde o dinheiro foi aplicado; quando o arquivo não diz, o gasto é da União, e não do estado da unidade que pagou (só a folha dos ex-territórios do Amapá, de Rondônia e de Roraima conta no estado, pela divisão de pessoal de cada um).');
    notes.push('Por essa regra, a folha militar paga pelas pagadorias centrais (Exército no DF, Marinha e Aeronáutica no RJ), as compras do Ministério da Saúde e os outros programas nacionais que o arquivo não põe em nenhum estado são da União; até 06/10/2026 contavam no DF e no RJ.');
    notes.push('A Receita registra o imposto onde fica a sede de quem paga: a arrecadação do DF, de SP e do RJ inclui impostos de empresas e órgãos com sede ali.');
    return notes;
  }
  const dfFactsOf = dfFacts;
  // The notes page and the links to it from the map: the period and the measure the reader had (D159).
  const NOTES_PAGE = 'como-ler-o-mapa.html';
  const periodId = (r) => (r.mode === 'month' ? `month-${r.months[0]}` : r.mode === 'year' ? `year-${r.years[0]}` : `mandate-${r.key}`);
  const notesHref = (r, metric) => `${NOTES_PAGE}?period=${encodeURIComponent(periodId(r))}&metric=${encodeURIComponent(metric)}`;
  window.BIMN = { bi, reais, cents, tenths, num1, biT, tri, unionAt, rowsAt, scale26, VALUE, dfFacts, relDate, SRC, dates, notes, NOTES_PAGE, periodId, notesHref };
})();
