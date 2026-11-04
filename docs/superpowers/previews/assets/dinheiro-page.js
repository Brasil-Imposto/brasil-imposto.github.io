// Como o dinheiro anda: the page. A file, not inline code: the site's CSP refuses inline scripts (spec seguranca-doacoes, section 8).
(function () {
  const D = window.BIM, U = D.union, S = D.states;
  const nf = (v, d = 2) => v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const bi = (v) => `R$ ${nf(v, 1)} bi`, brl = (v) => `R$ ${nf(v)}`;
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const DEST = { uniao: ['União', 'var(--d-uniao)', 'fica com a União'], estados: ['Governo do estado', 'var(--d-estados)', 'vai ao governo do estado'],
    prefeituras: ['Prefeituras', 'var(--d-prefeituras)', 'vai às prefeituras'], fundeb: ['Fundo da educação (Fundeb)', 'var(--d-fundeb)', 'vai ao fundo da educação do estado'],
    regional: ['Bancos do Norte, Nordeste e Centro-Oeste', 'var(--d-regional)', 'vai aos fundos regionais'] };
  const WHY = { uniao: 'Paga a previdência, a folha federal, a saúde, o Bolsa Família, os ministérios e os juros da dívida.',
    estados: 'Paga educação, previdência dos servidores do estado, saúde, segurança e os outros Poderes do estado.',
    prefeituras: 'Paga escola, posto de saúde, coleta de lixo, transporte e obras da cidade; pelo menos 25% em educação e 15% em saúde.',
    fundeb: 'Volta às escolas do estado e das prefeituras pelo número de alunos matriculados; a União completa o fundo.',
    regional: 'Vira empréstimo a empresas do Norte, do Nordeste e do Centro-Oeste (FNO, FNE e FCO).' };

  // ---------- C: follow R$ 100
  const outlays = [['4.1', 'Aposentadorias e pensões do INSS'], ['9', 'Juros da dívida'], ['4.4', 'Saúde, Bolsa Família e os ministérios'], ['4.2', 'Pessoal (folha federal)'], ['4.3', 'Outras obrigatórias (BPC, abono, seguro-desemprego, Fundeb, precatórios)']]
    .map(([k, l]) => [l, Math.abs(U[k].bi), k]);
  // the official totals (RTN 4 and 9) for the headline; the parts only split it
  const outTotal = outlays.reduce((a, [, v]) => a + v, 0), net = U['3'].bi, perHundred = ((U['4'].bi + Math.abs(U['9'].bi)) / net) * 100;
  const stOut = D.states_spending.slice(0, 6), stTotal = D.states_spending_total;
  let tax = 'ir';
  function drawC() {
    const t = D.taxes.find((x) => x.id === tax);
    document.querySelector('[data-taxes]').innerHTML = D.taxes.map((x) => `<button type="button" data-tax="${x.id}" aria-pressed="${x.id === tax}">${esc(x.label)}</button>`).join('');
    document.querySelector('[data-bill]').innerHTML = `R$ 100 de ${esc(t.phrase)} <small>cobrado ${t.collector === 'uniao' ? 'pela União' : t.collector === 'estados' ? 'pelo governo do estado' : 'pela prefeitura'}</small>`;
    document.querySelector('[data-stack]').innerHTML = t.split.map(([d, p]) => `<i style="width:${p}%;background:${DEST[d][1]}" title="${esc(DEST[d][0])}: ${brl(p)}"><span>${p >= 9 ? brl(p).replace(',00', '') : ''}</span></i>`).join('');
    document.querySelector('[data-dests]').innerHTML = t.split.map(([d, p]) => `<div class="dest"><i style="background:${DEST[d][1]}"></i><b>${esc(DEST[d][0])}</b><span class="v num">${brl(p)}</span><p>${esc(WHY[d])}</p></div>`).join('')
      + (t.note ? `<div class="note">${esc(t.note)}</div>` : '');
    document.querySelector('[data-taxsrc]').innerHTML = `Regra: ${esc(t.art)}; fundo da educação: CF art. 212-A e Lei 14.113/2020, art. 3. <a href="${esc(D.sources[0].url)}">Constituição</a>`;
    const u = (t.split.find(([d]) => d === 'uniao') || [0, 0])[1], e = (t.split.find(([d]) => d === 'estados') || [0, 0])[1];
    let h = '';
    if (u) h += `<h3>A parte da União: ${brl(u)}</h3><p class="lead2">Em 2025, a União gastou ${brl(perHundred)} para cada R$ 100 que ficaram com ela, contando os juros da dívida; os ${brl(perHundred - 100)} a mais vieram de dívida nova. Os seus ${brl(u)} se dividem como o gasto dela:</p>`
      + `<div class="bars2">${outlays.map(([l, v]) => `<div class="row"><span>${esc(l)}</span><b class="num">${brl((u * v) / outTotal)}</b><div class="bar"><i style="width:${(v / outlays[0][1]) * 100}%"></i></div></div>`).join('')}</div>`;
    if (e) h += `<h3 style="margin-top:16px">A parte do governo do estado: ${brl(e)}</h3><p class="lead2">Pela soma do gasto dos 27 estados em 2025 (${bi(stTotal)}):</p>`
      + `<div class="bars2">${stOut.map(([l, v]) => `<div class="row"><span>${esc(l)}</span><b class="num">${brl((e * v) / stTotal)}</b><div class="bar"><i style="width:${(v / stOut[0][1]) * 100}%;background:var(--d-estados)"></i></div></div>`).join('')}</div>`;
    if (!u && !e) h += `<h3>A parte das prefeituras</h3><p class="lead2">Cada prefeitura gasta a sua parte; pela Constituição, pelo menos 25% da receita de impostos vai para a educação e 15% para a saúde.</p>`;
    h += `<p class="src">Gasto da União: RTN do Tesouro, 2025 (linhas 4.1 a 4.4 e 9). Gasto dos estados: RREO dos 27 estados, 2025, por função, sem as transferências às prefeituras.</p>`;
    document.querySelector('[data-then]').innerHTML = h;
  }
  document.querySelector('[data-taxes]').addEventListener('click', (e) => { const b = e.target.closest('[data-tax]'); if (b) { tax = b.dataset.tax; drawC(); } });

  // ---------- A: six steps
  function drawA() {
    const L = (rows, max, color) => `<div class="lines">${rows.map(([l, v]) => `<div class="row"><span>${esc(l)}</span><b>${bi(v)}</b><div class="bar"><i style="width:${(v / max) * 100}%;background:${color}"></i></div></div>`).join('')}</div>`;
    const own = S.icms + S.ipva + S.itcmd;
    const steps = [
      ['Quem paga, e a quem', 'Pessoas e empresas pagam tributos a três governos; cada um só cobra o que a Constituição lhe dá (arts. 153, 155, 156 e 195).',
        `<div class="trio"><div class="card" style="--c:var(--d-uniao)"><h4>União</h4><div class="big">${bi(U['1'].bi)}</div><p>imposto de renda, IPI, IOF e as contribuições da seguridade (INSS, Cofins, PIS, CSLL), mais royalties e dividendos</p></div>`
        + `<div class="card" style="--c:var(--d-estados)"><h4>Estados</h4><div class="big">${bi(own)}</div><p>ICMS ${bi(S.icms)}, IPVA ${bi(S.ipva)}, ITCMD ${bi(S.itcmd)}</p></div>`
        + `<div class="card" style="--c:var(--d-prefeituras)"><h4>Prefeituras</h4><div class="big">ISS, IPTU, ITBI</div><p>o total das 5.570 prefeituras ainda não está no projeto (decisão 3)</p></div></div>`],
      ['Quem passa para quem, por regra', 'Partes fixas da arrecadação mudam de dono antes de alguém gastar. Nenhuma depende do governo do momento.',
        `<div class="two"><div>${L([['FPM, FPE e IPI-exportação', U['2.1'].bi], ['Royalties de petróleo, gás e minérios', U['2.4'].bi], ['Salário-educação', U['2.3'].bi], ['Fundos regionais (FNO, FNE, FCO)', U['2.2'].bi], ['CIDE e demais', U['2.5'].bi + U['2.6'].bi]], U['2.1'].bi, 'var(--d-uniao)')}`
        + `<p class="src">Da União a estados e prefeituras em 2025: ${bi(U['2'].bi)} (RTN, linha 2). Dos estados às prefeituras: ${bi(S.to_municipalities)} (25% do ICMS e 50% do IPVA, RREO).</p></div>`
        + `<div class="rules">${D.rules.slice(0, 8).map((r) => `<div class="rule"><b>${esc(r.what)}</b><span class="pct">${esc(r.pct)}</span>, ${esc(r.route)}<small>${esc(r.art)}</small></div>`).join('')}</div></div>`],
      ['O fundo da educação', 'Em cada estado, 20% de vários impostos vão para um fundo que volta às escolas pelo número de alunos (Fundeb).',
        `<div class="trio"><div class="card" style="--c:var(--d-fundeb)"><h4>Os estados puseram</h4><div class="big">${bi(S.fundeb_out)}</div><p>dedução para o Fundeb, RREO 2025</p></div>`
        + `<div class="card" style="--c:var(--d-fundeb)"><h4>E receberam de volta</h4><div class="big">${bi(S.fundeb_in)}</div><p>a diferença foi para as escolas das prefeituras, que têm mais alunos</p></div>`
        + `<div class="card" style="--c:var(--d-uniao)"><h4>A União completou com</h4><div class="big">${bi(U['4.3.10'].bi)}</div><p>no mínimo 23% do fundo em 2026 (ADCT art. 60); RTN 4.3.10</p></div></div>`],
      ['O mínimo de saúde e educação', 'O governo também não escolhe quanto gastar em educação e saúde: a Constituição fixa o mínimo.',
        `<div class="rules">${D.minimums.map((m) => `<div class="rule"><b>${esc(m.what)}</b>${esc(m.rule)}<small>${esc(m.art)}</small></div>`).join('')}</div>`],
      ['Quem gasta o quê', 'Cada governo gasta o que ficou com ele: salário, aposentadoria, benefício, compra, obra.',
        `<div class="two"><div><b>União, ${bi(U['4'].bi)}</b>${L([['Aposentadorias e pensões do INSS', U['4.1'].bi], ['Saúde, Bolsa Família e ministérios', U['4.4'].bi], ['Pessoal', U['4.2'].bi], ['Outras obrigatórias (BPC, abono, seguro-desemprego, Fundeb)', U['4.3'].bi]], U['4.1'].bi, 'var(--d-uniao)')}</div>`
        + `<div><b>27 estados, ${bi(stTotal)}</b>${L(D.states_spending.slice(0, 6), D.states_spending[0][1], 'var(--d-estados)')}</div></div>`],
      ['O que falta vira dívida', 'Quando o gasto passa da receita, o governo pega emprestado, e a dívida cobra juros.',
        `<div class="trio"><div class="card" style="--c:var(--d-uniao)"><h4>Ficou com a União</h4><div class="big">${bi(U['3'].bi)}</div><p>receita líquida, depois das repartições (RTN 3)</p></div>`
        + `<div class="card" style="--c:var(--d-divida)"><h4>Juros da dívida</h4><div class="big">${bi(Math.abs(U['9'].bi))}</div><p>juros nominais do ano (RTN 9)</p></div>`
        + `<div class="card" style="--c:var(--red)"><h4>Resultado</h4><div class="big">${bi(U['10'].bi)}</div><p>resultado nominal: o que faltou e virou dívida (RTN 10)</p></div></div>`],
    ];
    document.querySelector('[data-steps]').innerHTML = steps.map(([h, p, body], i) => `<div class="step"><div class="n">${i + 1}</div><div><h3>${esc(h)}</h3><p>${esc(p)}</p>${body}</div></div>`).join('');
  }

  // ---------- B: the flow (d3-sankey); two bands are differences between sources and say so
  let drawnB = false;
  function drawB() {
    if (drawnB || !window.d3 || !d3.sankey) return; drawnB = true;
    const debt = outTotal - net, stIn = S.fpe + S.ipi_exp, stOwn = S.icms + S.ipva + S.itcmd;
    const stOther = Math.max(0, S.to_municipalities + stTotal - stOwn - stIn), restShare = U['2'].bi - stIn;
    const big = D.states_spending.slice(0, 5), small = stTotal - big.reduce((a, [, v]) => a + v, 0);
    const N = ['Pessoas e empresas', 'Royalties, dividendos e concessões', 'Dívida nova', 'União', 'Repartição por regra', 'Governos dos estados', 'Outras receitas dos estados',
      'Prefeituras, fundos regionais e outros', 'Aposentadorias do INSS', 'Pessoal federal', 'Outras obrigatórias', 'Saúde, Bolsa Família e ministérios', 'Juros da dívida',
      ...big.map(([l]) => `${l} (estados)`), 'Demais funções (estados)'];
    const ix = (n) => N.indexOf(n);
    const L = [
      ['Pessoas e empresas', 'União', U['1.1'].bi + U['1.3'].bi, 'Tributos e contribuições federais (RTN 1.1 e 1.3)'],
      ['Royalties, dividendos e concessões', 'União', U['1.4'].bi, 'Receitas não administradas pela Receita (RTN 1.4)'],
      ['Pessoas e empresas', 'Governos dos estados', stOwn, 'ICMS, IPVA e ITCMD dos 27 estados (RREO)'],
      ['União', 'Repartição por regra', U['2'].bi, 'Transferências por repartição de receita (RTN 2): FPE, FPM, IPI-exportação, royalties, salário-educação, fundos regionais, CIDE'],
      ['Repartição por regra', 'Governos dos estados', stIn, 'FPE e IPI-exportação que os estados registram (RREO)'],
      ['Repartição por regra', 'Prefeituras, fundos regionais e outros', restShare, 'Diferença: o resto da linha 2 do RTN (FPM, royalties, salário-educação, fundos regionais)'],
      ['Governos dos estados', 'Prefeituras, fundos regionais e outros', S.to_municipalities, '25% do ICMS e 50% do IPVA passados às prefeituras (RREO)'],
      ['Outras receitas dos estados', 'Governos dos estados', stOther, 'Diferença entre o que os estados gastaram e as receitas mostradas: contribuições, SUS, outras transferências e empréstimos'],
      ['Dívida nova', 'União', debt, 'Diferença entre o gasto com juros e a receita líquida; o RTN mostra resultado nominal de ' + bi(U['10'].bi) + ', com ajustes de metodologia'],
      ['União', 'Aposentadorias do INSS', U['4.1'].bi, 'RTN 4.1'], ['União', 'Pessoal federal', U['4.2'].bi, 'RTN 4.2'], ['União', 'Outras obrigatórias', U['4.3'].bi, 'RTN 4.3: BPC, abono e seguro-desemprego, complemento do Fundeb, precatórios'],
      ['União', 'Saúde, Bolsa Família e ministérios', U['4.4'].bi, 'RTN 4.4'], ['União', 'Juros da dívida', Math.abs(U['9'].bi), 'Juros nominais (RTN 9)'],
      ...big.map(([l, v]) => ['Governos dos estados', `${l} (estados)`, v, 'Gasto liquidado dos 27 estados, RREO 2025']),
      ['Governos dos estados', 'Demais funções (estados)', small, 'Gasto liquidado dos 27 estados nas outras funções'],
    ];
    const COL = { 'União': '#14202B', 'Governos dos estados': '#1E5FAF', 'Repartição por regra': '#14202B', 'Pessoas e empresas': '#5B6773', 'Dívida nova': '#8A95A1',
      'Royalties, dividendos e concessões': '#5B6773', 'Outras receitas dos estados': '#8A95A1', 'Prefeituras, fundos regionais e outros': '#1C958B' };
    const W = 1140, H = 780, svg = d3.select('[data-flow]').attr('viewBox', `0 0 ${W} ${H}`).attr('width', '100%');
    const sk = d3.sankey().nodeWidth(14).nodePadding(22).extent([[230, 10], [W - 290, H - 10]]).nodeSort(null);
    const g = sk({ nodes: N.map((name) => ({ name })), links: L.map(([s, t, v, why]) => ({ source: ix(s), target: ix(t), value: v, why })) });
    const color = (n) => COL[n.name] || (n.name.includes('(estados)') ? '#1E5FAF' : '#3C4A57');
    const tip = document.querySelector('[data-tip]');
    svg.append('g').selectAll('path').data(g.links).join('path').attr('class', 'lk').attr('d', d3.sankeyLinkHorizontal())
      .attr('stroke', (l) => color(l.source)).attr('stroke-width', (l) => Math.max(1, l.width))
      .on('mousemove', (ev, l) => { tip.hidden = false; tip.innerHTML = `<b>${esc(l.source.name)} → ${esc(l.target.name)}</b><br>${bi(l.value)}<br>${esc(l.why)}`; tip.style.left = Math.min(ev.clientX + 14, innerWidth - 330) + 'px'; tip.style.top = ev.clientY + 14 + 'px'; })
      .on('mouseleave', () => { tip.hidden = true; });
    const nd = svg.append('g').selectAll('g').data(g.nodes).join('g');
    nd.append('rect').attr('x', (n) => n.x0).attr('y', (n) => n.y0).attr('width', (n) => n.x1 - n.x0).attr('height', (n) => Math.max(1, n.y1 - n.y0)).attr('rx', 3).attr('fill', color);
    nd.append('text').attr('x', (n) => (n.x0 < W / 2 ? n.x0 - 8 : n.x1 + 8)).attr('y', (n) => (n.y0 + n.y1) / 2).attr('text-anchor', (n) => (n.x0 < W / 2 ? 'end' : 'start'))
      .attr('dominant-baseline', 'middle').attr('font-size', 12).attr('font-weight', 700).attr('fill', '#14202B')
      .attr('paint-order', 'stroke').attr('stroke', '#fff').attr('stroke-width', 4).attr('stroke-linejoin', 'round')
      .text((n) => n.name).append('tspan').attr('x', (n) => (n.x0 < W / 2 ? n.x0 - 8 : n.x1 + 8)).attr('dy', 15).attr('font-weight', 600).attr('fill', '#5B6773').text((n) => bi(Math.max(n.value, 0)));
    document.querySelector('[data-flownote]').innerHTML = `União: RTN do Tesouro, 2025. Estados: RREO dos 27 estados, 2025 (receita por mês do Anexo 3; gasto liquidado por função do Anexo 2, sem as transferências às prefeituras). Duas faixas são diferenças entre fontes e dizem isso no texto: "Prefeituras, fundos regionais e outros" a partir da repartição e "Outras receitas dos estados". As prefeituras de todo o país ainda não estão no projeto.`;
  }

  // ---------- options
  document.querySelectorAll('[data-opt]').forEach((b) => b.addEventListener('click', () => {
    document.querySelectorAll('[data-opt]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    document.querySelectorAll('[data-view]').forEach((v) => { v.hidden = v.dataset.view !== b.dataset.opt; });
    if (b.dataset.opt === 'b') drawB();
  }));
  drawC(); drawA();
  document.body.dataset.ready = '1';
})();
