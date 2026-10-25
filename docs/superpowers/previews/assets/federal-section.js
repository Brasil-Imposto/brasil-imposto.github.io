// Federal section below the map (D44, GD24): Union accounts, federal servants, cost of the elected, amendments by author.
// Classic script (the page opens from the file path). Reads window.BI.federal_section and window.BI.releases.
// Exposes window.BIFED.render(root, form) with form A (cards), B (statement) or C (tabs): the variable of the round.
(function () {
  const nf = (v, d = 0) => v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const bi = (v) => `R$ ${nf(v / 1e9, 1)} bi`, tri = (v) => `R$ ${nf(v / 1e12, 2)} tri`, mi = (v) => `R$ ${nf(v / 1e6, 1)} mi`;
  const money = (v) => (Math.abs(v) >= 1e12 ? tri(v) : Math.abs(v) >= 1e9 ? bi(v) : mi(v));
  const MON3 = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
  const dt = (s) => (!s ? null : s.length === 7 ? `${MON3[+s.slice(5, 7) - 1]}/${s.slice(0, 4)}` : `${s.slice(8, 10)}/${s.slice(5, 7)}/${s.slice(0, 4)}`);
  const MONTHS = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
  const monthFull = (s) => `${MONTHS[+s.slice(5, 7) - 1]} de ${s.slice(0, 4)}`;
  // Audit of 2026-10-06: every money card says the months its numbers cover (the account above may cover others).
  const periodOf = (ms) => { if (!ms || !ms.length) return ''; const a = ms[0], b = ms[ms.length - 1];
    return a.slice(0, 4) === b.slice(0, 4) ? `${a.slice(0, 4)}, ${MONTHS[+a.slice(5, 7) - 1]} a ${MONTHS[+b.slice(5, 7) - 1]}` : `${monthFull(a)} a ${monthFull(b)}`; };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  const norm = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase();
  const icon = (path, bg, fg) => `<span class="ico" style="background:${bg};color:${fg}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${path}</svg></span>`;
  const IC = {
    contas: icon('<path d="M3 10h18M5 10V20M19 10V20M9 10v10M15 10v10M3 20h18M12 3l9 5H3z"/>', '#EAF2FB', '#1F4E8C'),
    serv: icon('<circle cx="9" cy="8" r="3.2"/><path d="M3.5 20c.6-3.4 2.8-5.4 5.5-5.4s4.9 2 5.5 5.4"/><circle cx="17" cy="9" r="2.4"/><path d="M15.5 14.4c2.4.2 4.2 2 4.8 5.1"/>', '#F1ECFA', '#5B3A9E'),
    eleitos: icon('<path d="M4 20h16M6 20V11M10 20V11M14 20V11M18 20V11M3 11h18M12 4l8 4H4z"/>', '#FDF1E7', '#B4570F'),
    emendas: icon('<path d="M4 7h16M4 12h10M4 17h7"/><path d="M16 15l2 2 4-4"/>', '#EAF6EF', '#12803F'),
  };
  const PBL = { executive_civil: ['Executivo civil', 'ministérios, universidades, agências, INSS, Receita, Polícia Federal'], executive_military: ['Militares', 'Exército, Marinha e Aeronáutica'],
    judiciary: ['Judiciário', 'tribunais e Justiça Federal'], fcdf_df_security_health_education: ['Fundo Constitucional do DF', 'polícias, bombeiros, saúde e educação do DF'],
    legislative: ['Legislativo', 'Câmara, Senado e TCU'], mpu: ['Ministério Público da União', ''], dpu: ['Defensoria Pública da União', ''] };
  const typeName = (t) => ({ 'Emenda Individual - Transferências com Finalidade Definida': 'Individuais, com finalidade definida', 'Emenda Individual - Transferências Especiais': 'Individuais, transferências especiais', 'Emenda de Comissão': 'De comissão', 'Emenda de Bancada': 'De bancada' })[t] || t;

  function blocksOf(F, R) {
    const U = F.union_accounts, PB = F.federal_payroll_by_branch, CG = F.congress_cost, Q = F.parliamentary_quota, AM = F.amendments, PER = periodOf(F.months);
    // D73: every list from the largest to the smallest value; the scale is the largest value of the list.
    const bars = (items, _max, color, fmt = money) => { items = items.slice().sort((a, b) => b[2] - a[2]); const max = items.length ? items[0][2] : 1; return `<ul class="fbars">${items.map(([l, s, v]) => `<li><span>${l}${s ? `<small>${s}</small>` : ''}</span><b>${fmt(v)}</b><i style="--w:${Math.max(0.6, (v / max) * 100)}%;--c:${color}"></i></li>`).join('')}</ul>`; };
    const brl = (v) => `R$ ${nf(v)}`, mil = (v) => `R$ ${nf(v / 1000, 1)} mil`;
    const srcLine = (ids) => `<p class="dchip-s">${ids.map(([id, lab]) => { const r = R[id]; const d = dt(r.date); return `${lab}: <b>${d ? 'divulgado em ' + d : r.unchecked ? 'data a conferir' : 'sem data publicada'}</b>`; }).join(' · ')}</p>`;
    const pbItems = Object.entries(PB).map(([k, v]) => [PBL[k][0], PBL[k][1], v]);
    const PK = F.federal_payroll_by_kind || {}, PKT = F.federal_payroll_kind_totals || {};
    // D72: who is paid, from the actuarial bases (civil: RPPS, July 2025; military: May 2025; DPU: its own table, July 2026).
    const SV = (window.BI && window.BI.federal_servants) || null, SB = SV ? SV.branches : {};
    const MON = (s) => dt(s);
    const asOf = (b, x) => (b === 'executive_military' ? `base de ${monthFull(x.as_of)}` : MON(x.as_of));  // the military base is May 2025 extrapolated to December
    const headcount = (k, b) => { const x = SB[b]; if (!x) return '';
      if (k === 'active') return b === 'dpu' ? `${nf(x.active_breakdown.public_defenders)} defensores e ${nf(x.active_breakdown.own_career_staff_pccdpu)} servidores (${MON(x.as_of)})` : `${nf(x.active)} na ativa (${asOf(b, x)})`;
      return `${nf(x.retired)} ${b === 'executive_military' ? 'na reserva ou reformados' : 'aposentados'} e ${nf(x.pensioners)} pensionistas (${asOf(b, x)})`; };
    const kindItems = (k) => Object.entries(PK[k] || {}).map(([b, v]) => [PBL[b][0], headcount(k, b), v]);
    const CIVIL = [['legislative', 'Legislativo', 'Câmara, Senado e TCU'], ['mpu', 'Ministério Público da União', ''], ['judiciary', 'Judiciário', 'juízes e servidores'], ['executive_civil', 'Executivo civil', 'inclui a DPU']];
    const avgItems = (k) => CIVIL.filter(([b]) => SB[b]).map(([b, l, s]) => [l, s, SB[b].average_monthly_brl[k]]);
    const MIL = SB.executive_military ? SB.executive_military.average_monthly_brl : null;
    const CNJ = SV && SV.judiciary_cost_per_person_cnj;
    // Three groups side by side in a full-width card: the same ruler for every civil branch, then the military by rank,
    // then the CNJ all-in cost of a judge, which has no equivalent for the other branches and is not ranked against them.
    const top = SV ? avgItems('active').sort((a, b) => b[2] - a[2])[0] : null;
    const perPerson = !SV ? '' : `<div class="fcols">
      <div><h4 class="fsub">Na ativa, por mês</h4>
        <p class="fnote">Remuneração média do quadro efetivo em julho de 2025, a mesma régua para todos os Poderes civis, com juízes, procuradores e ministros dentro. Não inclui indenizações e auxílios.</p>
        ${bars(avgItems('active'), 0, '#5B3A9E', brl)}
        ${MIL ? `<p class="fnote">Militares (base de ${monthFull(SB.executive_military.as_of)}), por posto: ${[['oficial de carreira', MIL.active_career_officer], ['oficial temporário', MIL.active_temporary_officer], ['praça de carreira', MIL.active_career_enlisted], ['praça temporária', MIL.active_temporary_enlisted]].sort((a, b) => b[1] - a[1]).map(([l, v]) => `${l} ${brl(v)}`).join(' · ')}.</p>` : ''}</div>
      <div><h4 class="fsub">Aposentados, por mês</h4>
        <p class="fnote">Provento médio, mesma fonte e mesmo mês. Pago pela União no regime próprio dos servidores, não pelo INSS.</p>
        ${bars(avgItems('retired'), 0, '#8A6BB8', brl)}
        ${MIL ? `<p class="fnote">Militares na reserva ou reformados: ${[['oficial', MIL.retired_officer], ['praça', MIL.retired_enlisted]].sort((a, b) => b[1] - a[1]).map(([l, v]) => `${l} ${brl(v)}`).join(' · ')}.</p>` : ''}</div>
      ${CNJ ? `<div><h4 class="fsub">Juízes dos tribunais federais, com tudo somado</h4>
        <p class="fnote">Conta do CNJ para ${CNJ.as_of}: salário, indenizações, encargos, imposto de renda e viagens, incluindo o que se paga a aposentados e pensionistas. Não é o salário. Para o Legislativo e o Executivo não há conta igual publicada, então estes valores não se comparam com as outras médias deste cartão.</p>
        ${bars(['superior_courts', 'federal_justice', 'labor_justice'].map((c) => [CNJ.courts[c].name, `por servidor: ${mil(CNJ.courts[c].per_servant)}`, CNJ.courts[c].per_magistrate]), 0, '#5B3A9E', mil)}</div>` : ''}</div>`;
    const collective = AM.authors.filter((a) => !a.type.startsWith('Emenda Individual')).slice(0, 3);
    return {
      U, F, CG, Q, AM, pbItems, srcLine, kindItems, PKT, PER,
      contas: { title: 'As contas da União', sub: `Tesouro Nacional e Banco Central · ${PER}`, icon: IC.contas, tab: `${U.nominal_result >= 0 ? 'Sobrou' : 'Faltou'} ${bi(Math.abs(U.nominal_result))}`,
        big: `<div class="fbig ${U.nominal_result >= 0 ? 'g' : 'r'}">${U.nominal_result >= 0 ? 'Sobrou' : 'Faltou'} ${bi(Math.abs(U.nominal_result))}<small>contando os juros da dívida; antes dos juros, ${U.primary_result >= 0 ? 'sobrou' : 'faltou'} ${bi(Math.abs(U.primary_result))}</small></div>`,
        body: bars([['Entrou', 'receita total da União', U.revenue], ['Foi para estados e prefeituras', 'repasses obrigatórios', U.transfers_to_subnationals], ['Gastou', 'despesa primária: benefícios, salários, saúde, educação, obras', U.primary_spending], ['Juros da dívida', '', -U.nominal_interest]], U.revenue, '#1F4E8C')
          + `<div class="fstats"><div><span>Deve</span><b>${tri(U.gross_debt_brl)}</b><small>${nf(U.gross_debt_pct_gdp, 1)}% do PIB, ${dt(U.gross_debt_at)}</small></div><div><span>Devia em dez/${+U.gross_debt_at.slice(0, 4) - 1}</span><b>${tri(U.gross_debt_at_start)}</b><small>dívida bruta do governo geral</small></div></div>`,
        src: [['rtn', 'Tesouro'], ['bcb', 'Banco Central']] },
      serv: { title: 'Pessoal pago pela União (servidores federais e pessoal do DF pago pelo Fundo Constitucional)', sub: `quem trabalha hoje e quem já se aposentou, separados; sem as contribuições intraorçamentárias · ${PER}`, icon: IC.serv, tab: bi(F.federal_payroll_total),
        big: `<div class="fbig">${bi(F.federal_payroll_total)}<small>${bi(PKT.active)} para quem trabalha hoje · ${bi(PKT.retired_and_pensioners)} para aposentados e pensionistas · ${bi(PKT.court_orders)} em sentenças judiciais</small></div>`,
        body: `<h4 class="fsub">Quem trabalha hoje (servidores e militares na ativa)</h4>` + bars(kindItems('active'), 0, '#5B3A9E')
          + `<h4 class="fsub">Aposentados e pensionistas</h4><p class="fnote">Pagos pela União no regime próprio dos servidores, não pelo INSS. Nos militares: reserva, reforma e pensões.</p>` + bars(kindItems('retired_and_pensioners'), 0, '#8A6BB8')
          + `<p class="fnote">Mais ${bi(PKT.court_orders)} em sentenças judiciais de pessoal (Executivo).</p>`
          + `<div class="fstats"><div><span>Servidores civis do Executivo</span><b>${nf(F.executive_civil_servants.total)}</b><small>em exercício em ${dt(F.executive_civil_servants.month)}; ${nf(F.executive_civil_servants.df)} no DF</small></div><div><span>Acima do teto</span><div class="missing">Não publicado: remuneração mensal dos servidores, Portal da Transparência.</div></div></div>`
          + (SB.executive_civil ? `<p class="fnote">Os dois números de servidores civis do Executivo vêm de fontes diferentes: ${nf(SB.executive_civil.active)} na ativa é a contagem do regime próprio de previdência em ${monthFull(SB.executive_civil.as_of)}, que inclui órgãos fora do SIAPE (DPU, ABIN e Banco Central); ${nf(F.executive_civil_servants.total)} é o SIAPE do Ministério da Gestão, servidores em exercício em ${monthFull(F.executive_civil_servants.month)}.</p>` : ''),
        src: [['tesouro_base', 'Tesouro'], ['siape', 'Ministério da Gestão']].concat(SV ? [['rpps_actuarial', 'quantidades: Previdência e Defesa']] : []) },
      pessoa: { title: 'Quanto ganha cada pessoa', sub: 'por mês, em média, em cada Poder', icon: IC.serv, wide: true, tab: top ? `${brl(top[2])}, ${top[0]}` : '',
        big: top ? `<div class="fbig">${brl(top[2])}<small>a maior remuneração média na ativa, no ${top[0]}, entre os Poderes civis medidos na mesma régua</small></div>` : '',
        body: perPerson, src: [['rpps_actuarial', 'Previdência e Defesa'], ['cnj_jn', 'CNJ']] },
      eleitos: { title: 'Quanto custam os eleitos federais', sub: `Câmara dos Deputados e Senado Federal · ${PER}`, icon: IC.eleitos, tab: bi(CG.chamber.total + CG.senate.total),
        big: `<div class="fbig">${bi(CG.chamber.total + CG.senate.total)}<small>toda a despesa da Câmara e do Senado: pessoal ativo e aposentado, gabinetes, cota, prédios</small></div>`,
        body: `<div class="fstats"><div><span>Câmara · 513 deputados</span><b>${bi(CG.chamber.total)}</b><small>${mi(CG.chamber.per_member_month)} por deputado, por mês</small></div><div><span>Senado · 81 senadores</span><b>${bi(CG.senate.total)}</b><small>${mi(CG.senate.per_member_month)} por senador, por mês</small></div></div>`
          + bars([['Cota parlamentar, Câmara', 'passagens, escritório, divulgação, combustível', Q.chamber.total], ['Cota parlamentar, Senado', '', Q.senate.total]], Q.chamber.total, '#B4570F')
          + '<p class="fnote">Custo da Casa dividido pelo número de cadeiras; inclui servidores e aposentados da Casa. O salário e a ficha de cada parlamentar vêm na rodada da ficha.</p>',
        src: [['tesouro_base', 'Tesouro'], ['camara_ceap', 'Câmara'], ['senado_ceaps', 'Senado']] },
      emendas: { title: 'Emendas parlamentares', sub: 'para onde os parlamentares mandaram dinheiro federal', icon: IC.emendas, tab: bi(AM.paid_total),
        big: `<div class="fbig g">${bi(AM.paid_total)}<small>pagos em emendas de ${AM.year}, até ${dt(AM.file_generated)} (o arquivo não tem mês)</small></div>`,
        body: bars(Object.entries(AM.paid_by_type).map(([k, v]) => [typeName(k), '', v]), Object.values(AM.paid_by_type)[0], '#12803F')
          + `<div class="search"><input type="search" placeholder="Buscar deputado ou senador (${nf(AM.individual_authors_count)} autores)" aria-label="Buscar autor de emenda" data-search><ul data-results></ul><span class="fhint">Maiores autores coletivos, como o Portal escreve: ${collective.map((a) => `${esc(a.author)} ${bi(a.paid)}`).join('; ')}.</span></div>`,
        src: [['amendments', 'Portal da Transparência']] },
    };
  }
  const ORDER = ['contas', 'serv', 'pessoa', 'eleitos', 'emendas'];

  function render(root, form) {
    const F = window.BI && window.BI.federal_section, R = window.BI && window.BI.releases;
    if (!F || !R) { root.innerHTML = '<p class="fnote">Dados da seção federal não carregados.</p>'; return; }
    const B = blocksOf(F, R), { U, CG, Q, AM, srcLine, kindItems, PKT, PER } = B;
    const card = (k) => { const b = B[k]; if (!b.body) return ''; return `<article class="fcard${b.wide ? ' fwide' : ''}"><div class="fcard-h">${b.icon}<div><h3>${b.title}</h3><small>${b.sub}</small></div></div>${b.big}${b.body}${srcLine(b.src)}</article>`; };
    if (form === 'A') root.innerHTML = `<div class="fa-grid">${ORDER.map(card).join('')}</div>`;
    if (form === 'B') {
      const row = (cls, op, lab, sub, v) => `<div class="fb-row ${cls}"><span class="op">${op}</span><span class="lab">${lab}${sub ? `<small>${sub}</small>` : ''}</span><span class="val">${v}</span></div>`;
      const inner = (lab, sub, v, cls = 'inner') => `<div class="fb-row ${cls}"><span class="lab">${lab}${sub ? `<small>${sub}</small>` : ''}</span><span class="val">${v}</span></div>`;
      root.innerHTML = `<div class="fb"><div class="fb-sec">${PER} · conta da União</div>
        ${row('in', '+', 'Entrou', 'receita total da União', bi(U.revenue))}
        ${row('', '−', 'Foi para estados e prefeituras', 'repasses obrigatórios', bi(U.transfers_to_subnationals))}
        ${row('', '=', 'Ficou com a União', '', bi(U.revenue_net))}
        ${row('', '−', 'Gastou', 'despesa primária', bi(U.primary_spending))}
        ${inner('Dentro do que gastou, entre outros:', '', '')}
        ${inner('Salários de quem trabalha hoje, todos os Poderes', `${nf(F.executive_civil_servants.total)} servidores civis do Executivo em exercício (${dt(F.executive_civil_servants.month)}); acima do teto: não publicado`, bi(PKT.active))}
        ${kindItems('active').sort((a, b) => b[2] - a[2]).map(([l, , v]) => inner(l, '', bi(v), 'inner2')).join('')}
        ${inner('Aposentadorias e pensões de servidores e militares', 'regime próprio dos servidores, não é o INSS', bi(PKT.retired_and_pensioners))}
        ${kindItems('retired_and_pensioners').sort((a, b) => b[2] - a[2]).map(([l, , v]) => inner(l, '', bi(v), 'inner2')).join('')}
        ${inner('Sentenças judiciais de pessoal', '', bi(PKT.court_orders))}
        ${inner('Câmara e Senado, toda a despesa', `${mi(CG.chamber.per_member_month)} por deputado e ${mi(CG.senate.per_member_month)} por senador, por mês; cota parlamentar ${mi(Q.chamber.total + Q.senate.total)}`, bi(CG.chamber.total + CG.senate.total))}
        ${inner('Emendas parlamentares pagas', `emendas de ${AM.year}, pagas até ${dt(AM.file_generated)} (outro período: o arquivo não tem mês)`, bi(AM.paid_total))}
        ${row('res', '=', `Antes dos juros: ${U.primary_result >= 0 ? 'sobrou' : 'faltou'}`, '', bi(Math.abs(U.primary_result)))}
        ${row('', '−', 'Juros da dívida', '', bi(-U.nominal_interest))}
        ${row('res', '=', `Com os juros: ${U.nominal_result >= 0 ? 'sobrou' : 'faltou'}`, `pela conta do Banco Central, que parte de ${bi(Math.abs(U.primary_result_below_line))} antes dos juros`, bi(Math.abs(U.nominal_result)))}
        <div class="fb-sec">Quanto a União deve</div>
        ${row('', '', 'Dívida bruta do governo geral', `${nf(U.gross_debt_pct_gdp, 1)}% do PIB em ${dt(U.gross_debt_at)}; em dez/${+U.gross_debt_at.slice(0, 4) - 1}: ${tri(U.gross_debt_at_start)}`, tri(U.gross_debt_brl))}
        <div class="fb-foot"><div class="search"><input type="search" placeholder="Buscar emendas de um deputado ou senador" aria-label="Buscar autor de emenda" data-search><ul data-results></ul></div>
        ${srcLine([['rtn', 'Tesouro'], ['bcb', 'Banco Central'], ['tesouro_base', 'Tesouro, folha'], ['siape', 'Ministério da Gestão'], ['camara_ceap', 'Câmara'], ['senado_ceaps', 'Senado'], ['amendments', 'Portal, emendas']])}</div></div>`;
    }
    if (form === 'C') {
      root.innerHTML = `<div class="fc"><div class="fc-tabs" role="tablist">${ORDER.map((k, i) => `<button type="button" role="tab" aria-selected="${i === 0}" data-tab="${k}">${B[k].title}<small>${B[k].tab}</small></button>`).join('')}</div><div data-tabpanel></div></div>`;
      const draw = (k) => { const b = B[k];
        root.querySelector('[data-tabpanel]').innerHTML = `<div class="fc-panel"><div><div class="fcard-h">${b.icon}<div><h3>${b.title}</h3><small>${b.sub}</small></div></div><div style="margin-top:12px">${b.big}</div>${srcLine(b.src)}</div><div class="fc-body">${b.body}</div></div>`;
        root.querySelectorAll('[data-tab]').forEach((t) => t.setAttribute('aria-selected', String(t.dataset.tab === k))); wire(root); };
      root.querySelectorAll('[data-tab]').forEach((t) => (t.onclick = () => draw(t.dataset.tab)));
      draw('contas');
    }
    wire(root);
    function wire(el) {
      el.querySelectorAll('[data-search]').forEach((inp) => {
        const out = inp.parentElement.querySelector('[data-results]');
        inp.oninput = () => { const q = norm(inp.value.trim()); if (q.length < 2) { out.innerHTML = ''; return; }
          const hits = AM.individual_authors.filter((a) => norm(a.author).includes(q)).slice(0, 5);
          out.innerHTML = hits.length ? hits.map((a) => `<li><span>${esc(a.author)}<small>${a.amendments} emendas · empenhado ${money(a.committed)}</small></span><b>${money(a.paid)} pago</b></li>`).join('') : `<li><span>Nenhum autor com esse nome em ${AM.year}</span></li>`; };
      });
    }
  }
  window.BIFED = { render };
})();
