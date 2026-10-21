// The state hero (round 9): the municipal map under the modal header, the municipality panel, and the ranking.
// Classic script, shared by the round 9 proposals page and the home simulation. Reads window.BI, BI_GEO_SC, BIS, BIC.
(function () {
  const { bi, reais, esc } = window.BIP.helpers;
  const nf = (v, d = 0) => v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const perMonth = (v) => (Math.abs(v) < 10 ? `R$ ${nf(v, 2)}` : reais(v));
  const money = (v) => (Math.abs(v) >= 1e9 ? bi(v) : Math.abs(v) >= 1e6 ? `R$ ${nf(v / 1e6, 1)} mi` : `R$ ${nf(v)}`);
  const icon = (name, size = 16) => (window.BI.icons[name] || '').replace(/<!--.*?-->/s, '').replace(/class="[^"]*"/, '')
    .replace(/width="24"/, `width="${size}"`).replace(/height="24"/, `height="${size}"`);
  const GEO = { SC: () => window.BI_GEO_SC, RS: () => window.BI_GEO_RS, DF: () => window.BI_GEO_DF };
  const DATA = { SC: () => window.BI.sc, RS: () => window.BI.rs, DF: () => window.BI.df_regions };
  const series = (uf) => window.BI.series && window.BI.series[`${uf.toLowerCase()}_municipal_federal`];
  // D66, D77: the DF has one municipality, Brasília; its map shows the 37 Regiões Administrativas (GDF boundaries), all in
  // the DF's own colour, because the tax flow with the Union is published only for the whole DF.
  const isRegions = (uf) => uf === 'DF';
  const dfRows = () => window.BI.df_regions.regions;
  const dfLabels = () => ['RA-I', 'RA-II', 'RA-III', 'RA-VI', 'RA-IX', 'RA-XII', 'RA-XIII', 'RA-XIV', 'RA-XX', 'RA-X'].filter((c) => dfRows()[c]);
  // The DF's balance with the Union for the period: the same row and the same 26-state scale as the country map (GD18).
  const VALUE = { perPerson: (s) => s.perPersonMonth, total: (s) => s.balance, proportion: (s) => Math.log(s.sent / s.received) };
  // D138: the DF's position is in review: no colour and no verdict here either.
  const DF_REVIEW = false;  // D146: the DF shows the estimate, marked as such
  function dfFlow(metric, r) {
    const rows = window.BI.states.map((s) => ({ uf: s.uf, name: s.name, ...window.BIL.federalAt(s.uf, r) }));
    const val = VALUE[metric] || VALUE.perPerson;
    const vs = rows.filter((s) => s.ok && s.uf !== 'DF').map(val), row = rows.find((s) => s.uf === 'DF');
    return { row, value: row.ok && !DF_REVIEW ? val(row) : null, scale: { maxPos: Math.max(...vs, 1e-9), maxNeg: Math.max(-Math.min(...vs, -1e-9), 1e-9) } };
  }
  const dfAmount = (s, metric, x) => (metric === 'proportion' ? `R$ ${nf((x / s.sent) * 100)}` : metric === 'perPerson' ? `${perMonth(x / s.population / s.months)}<small>/mês por pessoa</small>` : money(x));
  function dfVerdict(s, metric) {
    if (DF_REVIEW) return 'Posição do DF em revisão';
    if (metric === 'proportion') return `Para cada R$ 100 que foram para a União, voltaram R$ ${nf((s.received / s.sent) * 100)}`;
    const gap = Math.abs(s.balance);
    return `${s.balance >= 0 ? 'Enviou' : 'Recebeu'} ${metric === 'perPerson' ? `${perMonth(gap / s.population / s.months)} a mais por pessoa, por mês` : `${money(gap)} a mais no período`}`;
  }
  // Largest first (D73): whichever of "foi" and "voltou" is bigger comes first.
  const dfFlowRows = (s, metric) => [[s.sent, 'Foi para a União', 'out'], [s.received, 'Voltou para o DF', 'back']].sort((a, b) => b[0] - a[0]);
  function dfLegend(metric, r) {
    const s = dfFlow(metric, r).row;
    return `<div class="st-legend"><div class="lg-title">Saldo com a União · Brasília, o DF inteiro · ${esc(s.label || '')}</div>
      <div class="lg-bar" style="background:${window.BIS.legendGradient()}"></div>
      <div class="lg-ends"><span class="g">Envia mais do que recebe</span><span class="r">Recebe mais do que envia</span><span class="lg-case">★ Brasília, a capital do país, no Plano Piloto</span></div>
      <p class="lg-note">O imposto federal é publicado por município, e o DF tem um só: Brasília. Por isso as 37 Regiões Administrativas têm a mesma cor, a do DF no mapa do Brasil, na mesma escala. Nenhuma fonte oficial divide por região o imposto pago nem o dinheiro que volta.${DF_REVIEW ? ' A posição do DF está em revisão, por isso ele fica sem cor aqui e no mapa do Brasil.' : s.ok ? '' : ' Neste período o DF fica sem cor também no mapa do Brasil.'}</p></div>`;
  }
  const dfDescribe = (metric, r) => { const s = dfFlow(metric, r).row; return (code) => { const g = dfRows()[code];
    return `<strong>${esc(g.name)}</strong><span class="t-pop">Região Administrativa ${esc(String(g.number))} de Brasília</span>
      ${s.ok ? `${dfFlowRows(s, metric).map(([x, l]) => `<div class="row"><span>${l}</span><b>${metric === 'proportion' && l.startsWith('Foi') ? 'R$ 100' : dfAmount(s, metric, x)}</b></div>`).join('')}
      <div class="verdict ${DF_REVIEW ? '' : s.balance >= 0 ? 'g' : 'r'}">${dfVerdict(s, metric)}</div>` : '<div class="click">Sem dado completo do DF neste período</div>'}
      <div class="click">A cor e os números são do DF inteiro. Clique para ver a região</div>`; }; };
  function dfUnionBox(metric, r) {
    const s = dfFlow(metric, r).row;
    if (!s.ok) return '<div class="mun-box"><h4>Com a União</h4><p class="mun-none">Sem dado completo para este período.</p></div>';
    const max = Math.max(s.sent, s.received, 1);
    return `<div class="mun-box"><h4>Com a União · ${esc(s.label)}</h4>
        ${dfFlowRows(s, metric).map(([x, l, c]) => `<div class="u-row"><span class="u-lab">${l}</span><span class="u-bar"><i class="${c}" style="width:${(x / max) * 100}%"></i></span><b>${metric === 'proportion' && c === 'out' ? 'R$ 100' : dfAmount(s, metric, x)}</b></div>`).join('')}
        <div class="u-verdict ${DF_REVIEW ? '' : s.balance >= 0 ? 'g' : 'r'}">${dfVerdict(s, metric)}</div>
        <p class="mun-fine">O mesmo número do DF no mapa do Brasil. Voltou = repasses da União, INSS, BPC, Bolsa Família, o Fundo Constitucional do DF e o gasto federal no DF pela regra em duas etapas.</p></div>`;
  }
  // Brasília's city taxes for the period: the DF files them in the same report as the state taxes (RREO Anexo 3).
  const CITY_TAX = [['ISS', 'sobre serviços: consertos, consultas, escolas, aplicativos'], ['IPTU', 'imposto anual dos imóveis urbanos'], ['ITBI', 'sobre a compra e venda de imóveis']];
  function cityTaxes(v, r) {
    const b = r && window.BIL ? window.BIL.stateAt('DF', r) : window.BI.budgets.DF;
    if (!b) return null;
    const items = CITY_TAX.map(([k, d]) => ({ label: k, desc: d, value: (b.revenue_top.find((x) => x.label === k) || {}).value || 0 })).filter((x) => x.value > 0).sort((a, b2) => b2.value - a.value);
    return { items, total: items.reduce((a, x) => a + x.value, 0), label: b.coverLabel || b.periodLabel || String(b.year) };
  }
  const perMonthOf = (v, x) => (v && v.month ? `${perMonth(v.month(x))}<small>/mês por pessoa</small>` : money(x));
  // D84: how the DF and Brasília work, in plain words, on the site.
  const dfExplain = (n) => `<div class="mun-box df-explain"><h4>Como funcionam o DF e Brasília</h4><ol>
      <li><b>O DF é um estado e uma cidade ao mesmo tempo.</b> Nos outros estados há dois governos: o do estado, com o governador, e o de cada cidade, com o prefeito. No DF há um governo só, o GDF, chefiado pelo governador, que faz os dois papéis: cobra os impostos de estado (ICMS, IPVA) e os de prefeitura (ISS, IPTU, ITBI).</li>
      <li><b>Brasília é a única cidade do DF.</b> A Constituição (art. 32) proíbe dividir o DF em municípios. Por isso, para o IBGE, para a Receita Federal e para o Tesouro, Brasília é o DF inteiro. Ceilândia, Taguatinga, Gama e as outras não são cidades com prefeito: são partes de Brasília.</li>
      <li><b>Essas partes são as ${n} Regiões Administrativas.</b> Cada uma tem um administrador regional nomeado pelo governador, sem eleição, sem câmara de vereadores e sem imposto próprio. É parecido com as subprefeituras da cidade de São Paulo.</li>
      <li><b>O Plano Piloto (Região I) é a Brasília do dia a dia:</b> o desenho de Lúcio Costa, onde ficam a Esplanada dos Ministérios, o Congresso e a Praça dos Três Poderes. Por isso a estrela ★ Brasília fica nele.</li>
      <li><b>Por que o mapa do DF tem uma cor só.</b> Nos outros estados, a cor de cada município vem do imposto federal pago ali e do dinheiro da União que volta para ele. A Receita Federal publica esse imposto por município, e o DF tem um só. Nenhum órgão publica quanto Ceilândia ou o Lago Sul pagam de imposto, nem o GDF, cujo relatório de arrecadação divide por tributo e por atividade econômica, nunca por região. Então as regiões têm a cor do DF inteiro, a mesma do mapa do Brasil, e cada uma abre o próprio painel com o dinheiro que traz o nome dela.</li></ol>
      <table><thead><tr><th></th><th>Santa Catarina</th><th>Distrito Federal</th></tr></thead><tbody>
        <tr><td>Municípios</td><td>295</td><td>1 (Brasília)</td></tr>
        <tr><td>Quem governa a cidade</td><td>295 prefeitos e câmaras de vereadores</td><td>O GDF, com o governador e a Câmara Legislativa</td></tr>
        <tr><td>Divisões dentro da cidade</td><td>Bairros (não aparecem no mapa)</td><td>${n} Regiões Administrativas, com administrador nomeado</td></tr>
        <tr><td>Cor no mapa</td><td>Uma por município: o saldo de cada um com a União</td><td>Uma só: o saldo do DF inteiro com a União</td></tr></tbody></table></div>`;
  // D71: with nothing selected the panel is Brasília itself, the DF's only municipality (CF art. 32).
  function brasiliaPanel(v, r, metric) {
    const T = cityTaxes(v, r);
    const taxes = T && T.items.length ? `<div class="mun-box paid"><h4>Impostos de prefeitura de Brasília · ${esc(T.label)}</h4>
        <ul>${T.items.map((x) => `<li><span><b>${x.label}</b><small>${esc(x.desc)}</small></span><em>${perMonthOf(v, x.value)}</em><i style="width:${(x.value / T.items[0].value) * 100}%"></i></li>`).join('')}</ul>
        <p class="mun-fine">${money(T.total)} no período. Cobrados pelo GDF, que faz o papel da prefeitura; também entram na coluna "Pagou" abaixo, marcados "Brasília".</p></div>` : '';
    const D = window.BI.df_regions;
    return `<section class="mun-panel"><header><span class="mun-mark">B</span><div><small>O único município do DF</small><h3>Brasília</h3>${v && v.pop ? `<p>${nf(v.pop)} habitantes (IBGE)</p>` : ''}</div></header>
      <div class="mun-grid">${dfUnionBox(metric, r)}${taxes}</div>
      ${dfExplain(Object.keys(D.regions).length)}
      ${dfMoneyOverview(r)}
      <div class="mun-hint" style="margin:14px 0 0">${icon('building', 18)}<span>Clique numa Região Administrativa do mapa para ver quem a administra e o dinheiro do GDF gasto lá.</span></div></section>`;
  }
  // GDF money per region (data/df/region-money.json, Portal da Transparência do DF). Annual: the period reads its years.
  const DM = () => window.BI.df_money;
  const dmYears = (r) => { const all = Object.keys(DM().check.years).map(Number); const ys = (r ? r.years : [Math.max(...all)]).filter((y) => all.includes(y)); return ys.length ? ys : [Math.max(...all)]; };
  const dmDate = () => DM().regions['RA-I'].published_on.split('-').reverse().join('/');
  const dmLabel = (ys) => (ys.length > 1 ? `${ys[0]} a ${ys[ys.length - 1]}${ys.includes(2026) ? ` (2026 até ${dmDate()})` : ''}` : `${ys[0]}${ys[0] === 2026 ? `, até ${dmDate()}` : ''}`);
  const dmMoney = (v) => (Math.abs(v) >= 1e6 ? money(v) : `R$ ${nf(v / 1e3, 1)} mil`);
  const sumY = (byYear, ys) => ys.reduce((a, y) => a + ((byYear || {})[y] || 0), 0);
  const budgetOf = (g, ys) => { const out = {}; for (const y of ys) { const b = (g.administration_budget || {})[y]; if (!b) continue; for (const [k, x] of Object.entries(b)) if (x != null) out[k] = (out[k] || 0) + x; } return out; };
  const LOWER = new Set(['da', 'de', 'do', 'das', 'dos', 'e']);
  // GDF names come in capitals; acronyms stay in capitals, the rest becomes a normal name.
  const ACR = new Set(['DF', 'GDF', 'DER', 'TCDF', 'FHB', 'PAC', 'SLU', 'CEB', 'CAESB', 'NOVACAP', 'DETRAN', 'BRT', 'UPA', 'UBS', 'SIA', 'SCIA', 'CLDF', 'PMDF', 'CBMDF', 'PCDF', 'SEDUH', 'TERRACAP', 'METRÔ', 'EMATER', 'II', 'III', 'IV']);
  const word = (w, i) => { const u = w.toUpperCase(); if (ACR.has(u)) return u; const l = w.toLowerCase(); return i && LOWER.has(l) ? l : l.charAt(0).toUpperCase() + l.slice(1); };
  const proper = (s) => s.trim().split(/\s+/).map((w, i) => w.split(/([-\/])/).map((p, j) => (p === '-' || p === '/' ? p : word(p, i + j))).join('')).join(' ');
  const yrs = (a) => (a.length > 1 ? `${a.slice(0, -1).join(', ')} e ${a[a.length - 1]}` : String(a[0]));
  function dfMoneyOverview(r) {
    if (!DM()) return '';
    const ys = dmYears(r), regs = DM().regions;
    const rows = Object.entries(regs).map(([c, g]) => [c, g.name, budgetOf(g, ys).liquidated || 0]).filter((x) => x[2] > 0).sort((a, b) => b[2] - a[2]);
    const tot = ys.reduce((a, y) => a + DM().check.years[y].portal_total_liquidated, 0);
    const loc = ys.reduce((a, y) => a + Object.values(regs).reduce((s, g) => s + ((g.localized_gdf_spending || {})[y] || 0), 0), 0);
    const max = rows.length ? rows[0][2] : 1;
    return `<div class="mun-box df-rank"><h4>Orçamento de cada Administração Regional · ${esc(dmLabel(ys))}</h4>
        <p class="mun-fine" style="margin:0 0 8px">Valor liquidado por cada Administração: despesa com o serviço já entregue e conferido. É uma parte pequena do dinheiro do GDF: a saúde, a educação, a segurança e as grandes obras são pagas pelas secretarias e empresas do GDF, não pelas Administrações.</p>
        <ol>${rows.map(([c, n, x]) => `<li><button type="button" data-select="${c}"><span>${esc(n)}</span><b>${dmMoney(x)}</b><i style="width:${(x / max) * 100}%"></i></button></li>`).join('')}</ol>
        <p class="mun-fine">O GDF liquidou ${money(tot)} no período. Só ${nf((loc / tot) * 100, 1)}% disso traz o nome de uma região; o resto vem marcado "Distrito Federal". Por isso esse dinheiro aparece aqui, região por região, e não na cor do mapa. Fonte: Portal da Transparência do DF, atualizado em ${DM().regions['RA-I'].published_on.split('-').reverse().join('/')}.</p></div>`;
  }
  function dfPanel(code, v, r, metric) {
    if (!code) return brasiliaPanel(v, r, metric);
    const g = dfRows()[code];
    const pop = g.population && g.population.value ? `<p>${nf(g.population.value)} moradores (PDAD-A ${g.population.year}, IPEDF)</p>` : '<p>Região criada em 2026: a pesquisa de 2024 ainda não a separa</p>';
    return `<section class="mun-panel"><header><span class="mun-mark">${esc(String(g.number))}</span><div><small>Região Administrativa ${esc(String(g.number))} de Brasília</small><h3>${esc(g.name)}${code === 'RA-I' ? ' <span class="mun-sub">o centro de Brasília</span>' : ''}</h3>${pop}</div>
        <button type="button" class="mun-clear" data-clear>Ver Brasília inteira ✕</button></header>
      ${dfRegionMoney(code, v, r)}</section>`;
  }
  function dfRegionMoney(code, v, r) {
    const tail = '<p class="mun-fine">O saldo com a União, as contas do GDF e os impostos aparecem para Brasília inteira, logo abaixo: nenhuma fonte os divide por região.</p>';
    if (!DM() || !DM().regions[code]) return tail;
    const g = DM().regions[code], ys = dmYears(r), lab = esc(dmLabel(ys));
    const A = g.administrator;
    const holders = A && A.payroll_holders && A.payroll_holders.length > 1 ? A.payroll_holders.map((h) => proper(h.name)) : A && A.name ? [proper(A.name)] : [];
    const ref = A && A.payroll_reference ? `${window.BIT.MONTHS[+A.payroll_reference.slice(5, 7) - 1]} de ${A.payroll_reference.slice(0, 4)}` : '';
    const who = `<div class="mun-box"><h4>Quem administra</h4>${holders.length
      ? `<div class="df-admin"><span class="df-ini">${holders[0].split(' ').filter((w) => !LOWER.has(w)).slice(0, 2).map((w) => w.charAt(0)).join('')}</span><div><b>${holders.map(esc).join(' e ')}</b><small>${holders.length > 1 ? 'duas pessoas na função' : 'Administrador(a) regional'}, nomeado(a) pelo governador</small></div></div>
        <p class="mun-fine">Nome da folha de pagamento do GDF (${ref}, função "Administrador Regional"). A data e o ato de nomeação no Diário Oficial do DF ainda não foram conferidos.</p>`
      : `<p class="mun-fine" style="margin:0">Ninguém aparece na função "Administrador Regional" desta região na folha do GDF de ${ref || 'agosto de 2026'}.</p>`}</div>`;
    const B = budgetOf(g, ys);
    const stages = [['Aprovado no orçamento', B.initial], ['Autorizado', B.authorized], ['Empenhado', B.committed], ['Liquidado', B.liquidated], ['Pago', B.paid]].filter(([, x]) => x != null && x > 0).sort((a, b) => b[1] - a[1]);
    const bmax = stages.length ? stages[0][1] : 1;
    const budget = `<div class="mun-box"><h4>Orçamento da Administração Regional · ${lab}</h4>${stages.length
      ? `<ul class="df-bars">${stages.map(([l, x]) => `<li><span>${l}</span><b>${dmMoney(x)}</b><i style="width:${(x / bmax) * 100}%"></i></li>`).join('')}</ul>
        <p class="mun-fine">${g.administration_ug ? `Unidade ${esc(proper(g.administration_ug.name))}. ` : ''}Pago vem do painel "Despesas Regionais" e pode incluir contas de anos anteriores pagas neste ano${B.paid == null ? '; para esta região o painel não traz o pago' : ''}.</p>`
      : '<p class="mun-fine" style="margin:0">Esta região ainda não tem orçamento próprio no período.</p>'}</div>`;
    const L = sumY(g.localized_gdf_spending, ys), LA = sumY(g.localized_of_which_administration, ys);
    const top = (g.top_localized_items_2025 || []).slice().sort((a, b) => b.liquidated - a.liquidated).slice(0, 5);
    const localized = `<div class="mun-box"><h4>Gasto do GDF que cita ${esc(g.name)} · ${lab}</h4>
      <div class="fbig-df">${dmMoney(L)}<small>liquidado em ações do GDF cujo nome traz esta região${LA ? `, dos quais ${dmMoney(LA)} da própria Administração` : ''}</small></div>
      ${top.length ? `<p class="df-cap">Maiores em 2025</p><ul class="df-list">${top.map((x) => `<li><span>${esc(proper(x.action))}<small>${esc(proper(x.ug))}</small></span><b>${dmMoney(x.liquidated)}</b></li>`).join('')}</ul>` : ''}
      <p class="mun-fine">A maior parte do gasto do GDF não diz a região (vem marcada "Distrito Federal"), e parte do que diz é a sede de um órgão${code === 'RA-I' ? ': aqui, a folha do Tribunal de Contas do DF, do DER e do Hemocentro' : ''}. Não é tudo o que o GDF gasta na região.</p></div>`;
    const works = (g.works || []).slice().sort((a, b) => b.liquidated - a.liquidated).slice(0, 6);
    const obras = `<div class="mun-box"><h4>Obras com o nome da região · 2019 a 2026</h4>${works.length
      ? `<ul class="df-list">${works.map((w) => `<li><span>${esc(proper(w.action))}<small>${esc(proper(w.ug))} · ${yrs(w.years)}</small></span><b>${dmMoney(w.liquidated)}</b></li>`).join('')}</ul>
        <p class="mun-fine">Valor liquidado somado nos anos indicados, pelo orçamento do GDF. A empresa contratada não sai nesta fonte.</p>`
      : '<p class="mun-fine" style="margin:0">Nenhuma obra do orçamento do GDF traz o nome desta região no período.</p>'}</div>`;
    return `<div class="mun-grid df-grid">${who}${budget}${localized}${obras}</div>${tail}`;
  }

  const has = (uf) => Boolean(GEO[uf] && GEO[uf]() && DATA[uf] && DATA[uf]());
  // Rows for the period. Municipal federal revenue is annual, so a single month is shown as its whole year.
  let cache = { key: null, rows: null, r: null };
  // D46 (GD33): when the period reaches a year whose municipal revenue is not published yet (today, 2026), the map shows
  // the last published year (2025, estimated by D40) and says so.
  function effective(uf, r) {
    if (!r) return null;
    const S = series(uf), last = S.months.slice(-1)[0];
    const annual = Object.values(S.municipalities)[0].federal_revenue_annual;
    const lastYear = Math.max(...Object.keys(annual).filter((y) => annual[y] != null).map(Number));
    const e = r.mode === 'month' ? window.BIT.resolve({ mode: 'year', year: r.years[0] }, last) : r;
    if (e.years.every((y) => y <= lastYear)) return e;
    return { ...window.BIT.resolve({ mode: 'year', year: lastYear }, last), fallbackFrom: r.label };
  }
  function rowsOf(uf, r) {
    const S = series(uf);
    if (!r || !S || !window.BIL) return Object.fromEntries(DATA[uf]().municipalities.map((m) => [m.code, m]));
    const e = effective(uf, r); const key = `${uf}|${e.label}`;
    if (cache.key === key) return cache.rows;
    const rows = {};
    for (const m of DATA[uf]().municipalities) {
      const x = window.BIL.municipalAt(m.code, e);
      rows[m.code] = { ...m, ...x, name: m.name, months: e.months.length,
        balance_per_capita: x && x.balance != null ? (x.balance / x.population) * (12 / e.months.length) : null };
    }
    cache = { key, rows, r: e };
    return rows;
  }
  const periodOf = (uf, r) => (r ? effective(uf, r) : null);

  const months = (m) => m.months || 12;
  const value = (m, metric) => (m.balance == null ? null : metric === 'perPerson' ? m.balance / m.population / months(m) : metric === 'total' ? m.balance : Math.log(m.federal_revenue / Math.max(m.received, 1)));
  const amount = (m, metric, x) => (metric === 'perPerson' ? `${perMonth(x / m.population / months(m))}<small>/mês por pessoa</small>` : metric === 'total' ? money(x) : '');
  function verdict(m, metric) {
    if (m.balance == null) return 'sem dado';
    if (metric === 'proportion') return `Para cada R$ 100 que foram para a União, voltaram R$ ${nf((m.received / m.federal_revenue) * 100)}`;
    const gap = Math.abs(m.balance);
    return `${m.balance >= 0 ? 'Enviou' : 'Recebeu'} ${metric === 'perPerson' ? `${perMonth(gap / m.population / months(m))} a mais por pessoa, por mês` : `${money(gap)} a mais no período`}`;
  }
  const describe = (uf, metric, r, v) => {
    const rows = rowsOf(uf, r); const nCases = v ? casesBy(v) : new Map();
    return (code) => {
      const m = rows[code]; const n = nCases.get(code) || 0;
      return `<strong>${esc(m.name)}</strong><span class="t-pop">${nf(m.population)} habitantes</span>
        ${m.balance == null ? '<div class="click">Sem dado completo para este período</div>' : ''}<div class="row"><span>Foi para a União</span><b>${metric === 'proportion' ? 'R$ 100' : amount(m, metric, m.federal_revenue)}</b></div>
        <div class="row"><span>Voltou para o município</span><b>${metric === 'proportion' ? `R$ ${nf((m.received / m.federal_revenue) * 100)}` : amount(m, metric, m.received)}</b></div>
        <div class="verdict ${m.balance >= 0 ? 'g' : 'r'}">${verdict(m, metric)}</div>${n ? `<div class="t-cases">${n} ${n > 1 ? 'obras ou casos' : 'obra ou caso'} aqui</div>` : ''}<div class="click">Clique para ver o município</div>`;
    };
  };

  // Labels: the ten most populous municipalities. In RS the Porto Alegre metro area packs four of the ten together, so a
  // city whose label box would overlap one already placed is skipped for the next (box in map units, [dx, dy]).
  const LABEL_GAP = { RS: [16, 4] };
  function labelCodes(uf) {
    if (isRegions(uf)) return dfLabels();
    const byPop = DATA[uf]().municipalities.slice().sort((a, b) => b.population - a.population), gap = LABEL_GAP[uf];
    if (!gap) return byPop.slice(0, 10).map((m) => m.code);
    const at = new Map(GEO[uf]().municipalities.map((m) => [m.code, m.label])), out = [];
    for (const m of byPop) {
      if (out.length === 10) break;
      const p = at.get(m.code);
      if (p && !out.some((c) => Math.abs(at.get(c)[0] - p[0]) < gap[0] && Math.abs(at.get(c)[1] - p[1]) < gap[1])) out.push(m.code);
    }
    return out;
  }
  // One small dot per municipality with cases (D60); how many cases shows in the municipality's balloon.
  const casesBy = (v) => { const by = new Map(); for (const c of v.cases.filter((x) => x.municipality)) by.set(c.municipality, (by.get(c.municipality) || 0) + 1); return by; };
  const pinsOf = (v) => [...casesBy(v).keys()].map((code) => ({ code }));

  // Facts that hold for one state's map only.
  const LEGEND_EXTRA = { SC: ' Cidades com porto (Itajaí, Navegantes, Itapoá) registram o imposto de importação de mercadorias do país inteiro.' };
  function legend(uf, r) {
    const d = DATA[uf](); const e = periodOf(uf, r);
    const label = e ? `${e.label}${e.fallbackFrom ? `, estimado (a arrecadação por município de ${e.fallbackFrom} ainda não foi publicada)` : r.mode === 'month' ? ' (a arrecadação por município é anual)' : ''}` : d.year;
    return `<div class="st-legend"><div class="lg-title">Saldo com a União, por município · ${label}</div>
      <div class="lg-bar" style="background:${window.BIS.legendGradient()}"></div>
      <div class="lg-ends"><span class="g">Envia mais do que recebe</span><span class="r">Recebe mais do que envia</span><span class="lg-case"><i></i>obra ou caso no município</span></div>
      <p class="lg-note">Voltou = repasses da União à prefeitura + Bolsa Família + BPC pagos no município. Ainda não entram as aposentadorias do INSS (o INSS publica o dado por município, e ele vai ser carregado) nem a folha federal.${LEGEND_EXTRA[uf] || ''}</p></div>`;
  }


  function munPanel(uf, code, metric, v, r) {
    if (!code) return `<div class="mun-hint">${icon('building', 18)}<span>Clique num município do mapa para ver os números dele e as obras e gastos de lá.</span></div>`;
    const m = rowsOf(uf, r)[code];
    const top = `<header><span class="mun-mark">${esc(m.name.charAt(0))}</span><div><small>Município selecionado</small><h3>${esc(m.name)}</h3><p>${nf(m.population)} habitantes (IBGE)</p></div>
        <button type="button" class="mun-clear" data-clear>Ver o estado inteiro ✕</button></header>`;
    const max = Math.max(m.federal_revenue || 0, m.received || 0, 1);
    const union = m.balance == null ? `<div class="mun-box"><h4>Com a União</h4><p class="mun-none">Sem dado completo para este período.</p></div>`
      : `<div class="mun-box"><h4>Com a União · ${esc(periodOf(uf, r) ? periodOf(uf, r).label : '2024')}</h4>
          ${[[m.federal_revenue, `<div class="u-row"><span class="u-lab">Foi para a União</span><span class="u-bar"><i class="out" style="width:${(m.federal_revenue / max) * 100}%"></i></span><b>${metric === 'proportion' ? 'R$ 100' : amount(m, metric, m.federal_revenue)}</b></div>`], [m.received, `<div class="u-row"><span class="u-lab">Voltou</span><span class="u-bar"><i class="back" style="width:${(m.received / max) * 100}%"></i></span><b>${metric === 'proportion' ? `R$ ${nf((m.received / m.federal_revenue) * 100)}` : amount(m, metric, m.received)}</b></div>`]].sort((x, y) => (y[0] || 0) - (x[0] || 0)).map((x) => x[1]).join('')}
          <div class="u-verdict ${m.balance >= 0 ? 'g' : 'r'}">${verdict(m, metric)}</div>
          <p class="mun-fine">Voltou = transferências da União à prefeitura (${money(m.federal_transfers)}) + Bolsa Família (${money(m.bolsa_familia)})${m.bpc != null ? ` + BPC (${money(m.bpc)})` : ''} pagos aqui.</p></div>`;
    // Round 10: the prefeitura's own accounts and the same three columns as a state (needs the period layer).
    const B = r && window.BIL && window.BIL.muniBudgetAt ? window.BIL.muniBudgetAt(code, r) : null;
    const contas = B ? window.BIL.muniContas(m.name, B, r) : '';
    const cols = B ? window.BIP.render.muniColumns(code, r, metric) : '<p class="mun-none">O orçamento desta prefeitura ainda não foi carregado para este período.</p>';
    const cases = v.cases.filter((c) => c.municipality === code);
    return `<section class="mun-panel">${top}
      ${r && window.BIG ? window.BIG.mayorLine(code, r) : ''}
      <div class="mun-grid">${union}${contas}</div>
      <h4 class="mun-h">O dinheiro da prefeitura de ${esc(m.name)}</h4>${cols}
      ${cases.length ? window.BIC.cards({ cases }).replace('Casos com dados oficiais neste estado', `Casos com dados oficiais em ${esc(m.name)}`) : `<p class="mun-none">Ainda não há obras ou gastos de ${esc(m.name)} conferidos neste site.</p>`}
    </section>`;
  }

  // The state map, in 3D at full width.
  function hero(uf, metric, r) {
    if (!has(uf)) return `<div class="st-soon">${icon('building', 18)} O mapa dos municípios está pronto para Santa Catarina, o Rio Grande do Sul e o DF nesta prévia.</div>`;
    if (isRegions(uf)) return `<section class="st-hero v-maquete"><div class="st-mapwrap"><div class="st-map" data-map></div></div>${dfLegend(metric, r)}</section><div data-mun-panel></div>`;
    return `<section class="st-hero v-maquete"><div class="st-mapwrap"><div class="st-map" data-map></div></div>${legend(uf, r)}</section><div data-mun-panel></div>`;
  }

  // Mounts the map and wires selection. Returns a disposer.
  function mount(root, uf, metric, v, state = {}, r = null) {
    if (!has(uf)) return () => {};
    const el = root.querySelector('[data-map]'); const panel = root.querySelector('[data-mun-panel]');
    const create = !window.T3 ? window.BIS.createFlat : window.BIS.create3d;
    if (isRegions(uf)) {
      const sel = (code) => { state.selected = code; dmap.setSelected(code); panel.innerHTML = dfPanel(code, v, r, metric); const c = panel.querySelector('[data-clear]'); if (c) c.onclick = () => sel(null);
        panel.querySelectorAll('[data-select]').forEach((b) => { b.onclick = () => sel(b.dataset.select); }); };
      const F = dfFlow(metric, r);
      const dmap = create(el, { geo: GEO[uf](), labels: dfLabels(), pins: [], onSelect: sel,
        labelHtml: (c) => (c === 'RA-I' ? '<span class="sm-cap">★ Brasília</span><small>Plano Piloto</small>' : null),
        labelText: (c) => (c === 'RA-I' ? '★ Brasília (Plano Piloto)' : null) });
      dmap.setData(Object.fromEntries(Object.keys(dfRows()).map((c) => [c, F.value])), dfDescribe(metric, r), false, F.scale);
      panel.__select = sel; sel(state.selected || null);
      return () => dmap.dispose();
    }
    const select = (code) => {
      state.selected = code; map.setSelected(code); panel.innerHTML = munPanel(uf, code, metric, v, r);
      const clear = panel.querySelector('[data-clear]'); if (clear) clear.onclick = () => select(null);
      panel.querySelectorAll('.cc8-card[data-case]').forEach((b) => { b.onclick = () => state.onCase && state.onCase(v.cases.filter((c) => c.municipality === code)[+b.dataset.case]); });
    };
    const map = create(el, { geo: GEO[uf](), labels: labelCodes(uf), pins: pinsOf(v), onSelect: select });
    const rows = rowsOf(uf, r);
    map.setData(Object.fromEntries(Object.entries(rows).map(([c, m]) => [c, value(m, metric)])), describe(uf, metric, r, v));
    root.querySelectorAll('[data-select]').forEach((b) => { b.onclick = () => select(b.dataset.select); });
    panel.__select = select; // lets the headless probe pick a municipality without synthesising pointer events
    select(state.selected || null);
    return () => map.dispose();
  }

  window.BIH = { hero, mount, has };
})();
