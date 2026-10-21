// Modal proposals (round 5), shared by the proposals page and the home simulation, so the two never drift.
// Classic script (no modules) so both pages open straight from the file path. Reads window.BI.
(function () {
  const BI = window.BI;
  const nf = (v, d = 1) => v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const bi = (v) => (Math.abs(v) >= 1e9 ? `R$ ${nf(v / 1e9)} bi` : `R$ ${nf(v / 1e6)} mi`);
  const reais = (v) => `R$ ${Math.round(v).toLocaleString('pt-BR')}`;
  // Small per-person amounts keep their cents, so nothing rounds down to a misleading R$ 0.
  const perMonth = (v) => (Math.abs(v) < 10 ? `R$ ${nf(v, 2)}` : reais(v));
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const REGION = { N: 'Região Norte', NE: 'Região Nordeste', CO: 'Região Centro-Oeste', SE: 'Região Sudeste', S: 'Região Sul' };

  // Spending colour follows the kind of area (validated categorical palette; green and red stay reserved
  // for "sends more" and "receives more"). Revenue uses one teal family, darkest for the biggest source.
  const GROUPS = {
    prev: { label: 'Previdência', color: '#2a78d6', fns: ['Previdência Social'] },
    saude: { label: 'Saúde e assistência', color: '#e87ba4', fns: ['Saúde', 'Assistência Social'] },
    edu: { label: 'Educação e cultura', color: '#4a3aa7', fns: ['Educação', 'Cultura', 'Desporto e Lazer', 'Ciência e Tecnologia'] },
    seg: { label: 'Segurança e justiça', color: '#eb6834', fns: ['Segurança Pública', 'Judiciária', 'Essencial à Justiça', 'Legislativa', 'Defesa Nacional', 'Direitos da Cidadania'] },
    infra: { label: 'Infraestrutura', color: '#1baf7a', fns: ['Transporte', 'Urbanismo', 'Saneamento', 'Habitação', 'Energia', 'Comunicações', 'Gestão Ambiental'] },
    divida: { label: 'Dívidas e encargos', color: '#eda100', fns: ['Encargos Especiais'] },
    outros: { label: 'Administração e outros', color: '#8A95A1', fns: [] },
  };
  const groupOf = (fn) => (Object.entries(GROUPS).find(([, g]) => g.fns.includes(fn)) || ['outros'])[0];
  const REV_SHADES = ['#0B5F5A', '#117A73', '#1C958B', '#3AAEA3', '#67C6BB', '#98DAD1', '#C6ECE6'];
  // Colour law: money coming in is green, money going out is red, darkest for the
  // largest item. Icons keep their own colour, which follows the item (never its rank).
  const GREEN_RAMP = ['#0E6B3A', '#86CC9C'];
  const RED_RAMP = ['#961620', '#EE9483'];
  const hexLerp = (a, b, t) => '#' + [1, 3, 5].map((i) => Math.round(parseInt(a.slice(i, i + 2), 16) * (1 - t) + parseInt(b.slice(i, i + 2), 16) * t)
    .toString(16).padStart(2, '0')).join('');
  const shade = (ramp, i, n) => hexLerp(ramp[0], ramp[1], n > 1 ? i / (n - 1) : 0);

  const ICON_FN = {
    'Previdência Social': 'piggy-bank', 'Saúde': 'heart-pulse', 'Educação': 'graduation-cap', 'Segurança Pública': 'siren',
    'Judiciária': 'gavel', 'Essencial à Justiça': 'scale', 'Legislativa': 'landmark', 'Administração': 'building-2',
    'Encargos Especiais': 'percent', 'Transporte': 'bus', 'Assistência Social': 'hand-heart', 'Saneamento': 'droplets',
    'Agricultura': 'wheat', 'Habitação': 'house', 'Urbanismo': 'building', 'Cultura': 'palette', 'Desporto e Lazer': 'trophy',
    'Gestão Ambiental': 'leaf', 'Ciência e Tecnologia': 'flask-conical', 'Trabalho': 'briefcase', 'Comércio e Serviços': 'store',
    'Energia': 'zap', 'Comunicações': 'radio', 'Indústria': 'factory', 'Organização Agrária': 'tractor',
    'Relações Exteriores': 'globe', 'Defesa Nacional': 'shield', 'Direitos da Cidadania': 'users', 'Demais áreas': 'receipt',
  };
  const ICON_REV = {
    'Parte das prefeituras': 'building', 'Contribuição ao Fundeb': 'school',
    'ICMS': 'shopping-cart', 'IPVA': 'car', 'ITCD (heranças e doações)': 'scroll-text', 'Imposto de renda retido na fonte': 'wallet',
    'Fundo de Participação dos Estados (União)': 'landmark', 'Fundeb': 'school', 'Outras transferências': 'arrow-left-right',
    'IPI exportação (União)': 'ship', 'Contribuições (previdência dos servidores)': 'users', 'Receita patrimonial': 'coins',
    'Receita de serviços': 'wrench', 'Outras receitas correntes': 'coins', 'Outros impostos e taxas': 'receipt', 'Demais receitas': 'coins',
    'ISS': 'wrench', 'IPTU': 'house', 'ITBI': 'building', 'Fundo de Participação dos Municípios (União)': 'landmark', 'Cota-parte do ICMS (estado)': 'shopping-cart',
    'Cota-parte do IPVA (estado)': 'car', 'Cota-parte do ITR (União)': 'tractor', 'Contribuições': 'users', 'Tributos federais': 'landmark',
    'Imposto de renda dos servidores municipais': 'wallet', 'Taxas municipais': 'receipt',
  };
  // One plain-language line per item, so a child can tell what each name means.
  const DESC_FN = {
    'Previdência Social': 'aposentadorias e pensões dos servidores', 'Educação': 'escolas e professores da rede estadual',
    'Saúde': 'hospitais, postos e remédios', 'Judiciária': 'Tribunal de Justiça e juízes', 'Segurança Pública': 'polícias e bombeiros',
    'Transporte': 'estradas, pontes e transporte', 'Administração': 'servidores públicos da área administrativa e o funcionamento do governo', 'Encargos Especiais': 'pagamento de dívidas e outros encargos',
    'Legislativa': 'Assembleia Legislativa e Tribunal de Contas', 'Essencial à Justiça': 'Ministério Público, Defensoria e Procuradoria',
    'Assistência Social': 'apoio a famílias e pessoas vulneráveis', 'Saneamento': 'água e esgoto', 'Agricultura': 'apoio ao campo',
    'Urbanismo': 'obras nas cidades', 'Habitação': 'moradia', 'Gestão Ambiental': 'meio ambiente', 'Ciência e Tecnologia': 'pesquisa e inovação',
    'Cultura': 'cultura e patrimônio', 'Desporto e Lazer': 'esporte e lazer', 'Trabalho': 'emprego e renda', 'Direitos da Cidadania': 'direitos e cidadania',
    'Comércio e Serviços': 'comércio e turismo', 'Indústria': 'indústria', 'Energia': 'energia', 'Comunicações': 'comunicações',
    'Organização Agrária': 'terra e reforma agrária', 'Relações Exteriores': 'relações com outros países', 'Defesa Nacional': 'defesa',
    'Demais áreas': 'todas as outras áreas somadas',
  };
  const DESC_REV = {
    'ICMS': 'imposto sobre o que se compra: produtos, energia, combustível', 'IPVA': 'imposto anual dos veículos',
    'ITCD (heranças e doações)': 'imposto sobre heranças e doações', 'Imposto de renda retido na fonte': 'descontado dos servidores do estado; fica com o estado',
    'Fundo de Participação dos Estados (União)': 'parte do imposto de renda e do IPI que a União divide com os estados',
    'Fundeb': 'fundo que reparte o dinheiro da educação básica', 'Outras transferências': 'outros repasses, como os do SUS',
    'IPI exportação (União)': 'compensação pelas exportações', 'Contribuições (previdência dos servidores)': 'contribuição dos servidores para a aposentadoria',
    'Receita patrimonial': 'rendimentos e aluguéis do estado', 'Receita de serviços': 'serviços prestados pelo estado',
    'Outros impostos e taxas': 'taxas e outros impostos', 'Outras receitas correntes': 'multas e outras receitas', 'Demais receitas': 'todas as outras receitas somadas',
    'ISS': 'imposto sobre serviços, da prefeitura', 'IPTU': 'imposto anual dos imóveis urbanos', 'ITBI': 'imposto na compra e venda de imóveis',
    'Fundo de Participação dos Municípios (União)': 'parte do imposto de renda e do IPI que a União divide com as cidades',
    'Cota-parte do ICMS (estado)': 'um quarto do ICMS vai para as cidades', 'Cota-parte do IPVA (estado)': 'metade do IPVA fica com a cidade onde o carro está',
    'Contribuições': 'contribuição dos servidores e de iluminação pública',
  };
  const SHORT = {
    'Fundo de Participação dos Estados (União)': 'Fundo de Participação', 'Imposto de renda retido na fonte': 'Imposto de renda retido',
    'Contribuições (previdência dos servidores)': 'Contribuição dos servidores', 'ITCD (heranças e doações)': 'ITCD',
    'Encargos Especiais': 'Dívidas e encargos', 'IPI exportação (União)': 'IPI exportação',
  };
  const short = (l) => SHORT[l] || l;

  const icon = (name, size = 20) => (BI.icons[name] || '').replace(/<!--.*?-->/s, '').replace(/class="[^"]*"/, '')
    .replace(/width="24"/, `width="${size}"`).replace(/height="24"/, `height="${size}"`);
  const fnIcon = (fn, s) => icon(ICON_FN[fn] || 'receipt', s);
  const revIcon = (r, s) => icon(ICON_REV[r] || 'coins', s);

  // "Demais" rows name their three largest members, so the reader knows what is inside.
  // Plain names for the examples inside a "Demais" row (official names like "Essencial à Justiça" mean little to most people).
  const PLAIN = {
    'Encargos Especiais': 'dívidas e encargos', 'Essencial à Justiça': 'Ministério Público e Defensoria', 'Direitos da Cidadania': 'direitos e cidadania',
    'Legislativa': 'Assembleia Legislativa', 'Judiciária': 'Judiciário', 'Previdência Social': 'previdência', 'Segurança Pública': 'segurança pública',
    'Assistência Social': 'assistência social', 'Gestão Ambiental': 'meio ambiente', 'Desporto e Lazer': 'esporte e lazer', 'Comércio e Serviços': 'comércio e turismo',
    'Organização Agrária': 'reforma agrária', 'Defesa Nacional': 'defesa', 'Ciência e Tecnologia': 'ciência e tecnologia',
    'Outros impostos e taxas': 'taxas estaduais', 'Contribuições (previdência dos servidores)': 'contribuição dos servidores', 'Receita patrimonial': 'rendimentos e aluguéis',
    'Receita de serviços': 'serviços prestados pelo estado', 'Fundo de Participação dos Estados (União)': 'Fundo de Participação', 'IPI exportação (União)': 'IPI exportação',
    'ITCD (heranças e doações)': 'imposto sobre heranças', 'Outras receitas correntes': 'multas e outras receitas', 'Outras transferências': 'outros repasses',
    'Imposto de renda retido na fonte': 'imposto de renda retido',
  };
  const lower = (l, P = PLAIN) => P[l] || (/^[A-Z]{2,}/.test(l) ? l : l.charAt(0).toLowerCase() + l.slice(1));
  function examples(members, noun, withRemainder = false, P = PLAIN) {
    const named = [...members].sort((a, b) => b.value - a.value).filter((m) => m.value > 0);
    if (!named.length) return `outras ${noun} menores`;
    const top = named.slice(0, 3).map((m) => lower(m.label, P));
    const more = named.length - top.length;
    // Separated by dots: the names themselves contain "e", so commas would blur where one ends.
    return `inclui ${top.join(' · ')}${more > 0 ? ` · e mais ${more} ${noun}` : withRemainder ? ` · e outras ${noun} menores` : ''}`;
  }

  function view(uf, opts = {}) {
    let s = BI.states.find((x) => x.uf === uf);
    let b = BI.budgets[uf];
    // Round 10: with a period, the state budget and the federal balance come from the time series.
    const r = opts.r; let fed = null;
    if (r && window.BIL) {
      const sb = window.BIL.stateAt(uf, r); if (sb) b = sb;
      fed = window.BIL.federalAt(uf, r);
      if (fed) s = { ...s, population: fed.population, sent: fed.sent, received: fed.received, transfers: fed.transfers,
        direct: (fed.bolsa || 0) + (fed.inss || 0) + (fed.bpc || 0) + (fed.fcdf || 0) + (fed.fedSpending || 0), balance: fed.balance ?? 0 };
    }
    // D116: "Recebeu" is what stays with the state
    // government, so the municipalities' share and the Fundeb contribution (deductions in RREO Anexo 3) are lines that go
    // out; "Gastou" is the government's own spending, so what it books as a transfer (Encargos Especiais, subfunction
    // "Transferências"; in SP and AM most of it is the municipalities' share of ICMS and IPVA) leaves the column.
    const toMun = b.to_municipalities || 0, fundebOut = b.fundeb_deduction || 0;
    let trOut = 0;
    const enc = b.spending_by_function.find((f) => f.label === 'Encargos Especiais');
    trOut = enc ? ((enc.sub || []).find((x) => x.label === 'Transferências') || { value: 0 }).value : 0;
    if (trOut > 0) {
      const fns = b.spending_by_function.map((f) => (f !== enc ? f : { ...f, value: f.value - trOut, sub: f.sub.filter((x) => x.label !== 'Transferências') }))
        .filter((f) => f.value > 0).sort((x, y) => y.value - x.value);
      b = { ...b, spending_by_function: fns, spending_total: b.spending_total - trOut };
    }
    const revTop = b.revenue_top.slice(0, 6);
    const revRest = b.revenue_current_total - revTop.reduce((a, r) => a + r.value, 0);
    const spTop = b.spending_by_function.slice(0, 7);
    const spRest = b.spending_total - spTop.reduce((a, r) => a + r.value, 0);
    const revFolded = b.revenue_top.slice(6);
    const spFolded = b.spending_by_function.slice(7);
    // Brasília has no prefeitura: in the DF the GDF collects the city taxes and receives the city fund.
    const DF_DESC = { 'ISS': 'imposto sobre serviços; em Brasília quem cobra é o GDF', 'IPTU': 'imposto dos imóveis urbanos; em Brasília quem cobra é o GDF',
      'ITBI': 'imposto na compra e venda de imóveis; em Brasília quem cobra é o GDF', 'Fundo de Participação dos Municípios (União)': 'a parte de Brasília no fundo que a União divide com as cidades' };
    let revenue = [...revTop, ...(revRest > 0 ? [{ label: 'Demais receitas', value: revRest, desc: examples(revFolded, 'receitas', true), members: revFolded }] : [])]
      .map((r, i) => ({ ...r, ...(uf === 'DF' && DF_DESC[r.label] ? { desc: DF_DESC[r.label] } : {}), color: REV_SHADES[Math.min(i, REV_SHADES.length - 1)] }));
    let spending = [...spTop.map((f) => ({ label: f.label, value: f.value })), ...(spRest > 0 ? [{ label: 'Demais áreas', value: spRest, desc: examples(spFolded, 'áreas'), members: spFolded }] : [])]
      .map((f) => ({ ...f, group: groupOf(f.label), color: GROUPS[groupOf(f.label)].color }));
    // Everything strictly from largest to smallest, the "Demais" rows included.
    const desc = (a) => [...a].sort((x, y) => y.value - x.value);
    // In round 7 the icon colour means origin, the same code as the yellow column: the state's own tax or the União.
    const ORIGIN = { 'ICMS': 'estado', 'IPVA': 'estado', 'ITCD (heranças e doações)': 'estado', 'Imposto de renda retido na fonte': 'estado',
      'Outros impostos e taxas': 'estado', 'Fundo de Participação dos Estados (União)': 'uniao', 'IPI exportação (União)': 'uniao',
      'ISS': 'municipios', 'IPTU': 'municipios', 'ITBI': 'municipios', 'Fundo de Participação dos Municípios (União)': 'uniao', 'Cota-parte do ITR (União)': 'uniao' };
    const iconOf = (l) => (ORIGIN[l] ? DEST[ORIGIN[l]].color : '#5B6773');
    revenue = desc(revenue).map((r, i, a) => ({ ...r, color: shade(GREEN_RAMP, i, a.length), iconColor: iconOf(r.label) }));
    spending = desc(spending).map((s, i, a) => ({ ...s, color: shade(RED_RAMP, i, a.length), iconColor: GROUPS[s.group].color }));
    // The lines that go out sit under the lines that come in, each group from the largest to the smallest (D73).
    revenue = [...revenue, ...[['Parte das prefeituras', toMun, 'o que a Constituição manda o estado passar às prefeituras, como parte do ICMS e do IPVA'],
      ['Contribuição ao Fundeb', fundebOut, 'parte dos impostos e repasses que vai para o fundo da educação básica; o que volta do fundo está em Fundeb']]
      .filter(([, x]) => x > 0).sort((x, y) => y[1] - x[1]).map(([label, value, desc]) => ({ label, value, desc, gone: true, color: '#8A95A1', iconColor: '#5B6773' }))];
    const out = {
      uf, name: s.name, region: REGION[BI.regions[uf]],
      pop: s.population, year: b.year, sent: s.sent, received: s.received, transfers: s.transfers, direct: s.direct, sends: s.balance >= 0,
      revenueTotal: b.revenue_current_total - toMun - fundebOut, spendingTotal: b.spending_total,
      revenueGross: b.revenue_current_total, toMunicipalities: toMun, fundeb: fundebOut, transfersOutOfSpending: trOut,
      revenue, spending, cases: BI.cases.filter((c) => c.uf === uf), sources: b.sources,
      // State budget values cover the months the state has reported (b.months), which can end before the period.
      month: (v) => v / s.population / (b.months || (r ? r.months.length : 12)), budgetMonths: b.months || (r ? r.months.length : 12),
      budgetLabel: b.coverLabel || (r ? r.label : String(b.year)),
      period: r || null, periodLabel: r ? r.label : String(b.year), fed, b,
      // The federal side can end earlier than the period (the current year is partial): its own label and month count.
      fedLabel: fed ? fed.label : null, monthFed: (v) => v / s.population / (fed && fed.months ? fed.months : r ? r.months.length : 12),
    };
    out.paid = paidView(out);
    return out;
  }

  // ---------- shared pieces ----------
  const METRICS = [['perPerson', 'Por pessoa'], ['total', 'Total'], ['proportion', 'Proporção']];
  const per100 = (x, total) => Math.round((x / total) * 100);
  const valueOf = (v, metric, x, total) => (metric === 'perPerson' ? `${perMonth(v.month(x))}<small>/mês</small>`
    : metric === 'total' ? bi(x) : `R$ ${per100(x, total)}<small> de cada 100</small>`);
  const miniSwitch = (metric) => `<div class="mini-switch" role="group" aria-label="Medida">${METRICS.map(([k, l]) =>
    `<button type="button" data-metric="${k}" aria-pressed="${k === metric}">${l}</button>`).join('')}</div>`;

  function head(v, metric) {
    return `<div class="bp-head">
      <img class="bp-flag" src="assets/state-flags/${v.uf}.svg" alt="Bandeira de ${esc(v.name)}">
      <div class="bp-id"><h2>${esc(v.name)}</h2><p>${v.region} · ${nf(v.pop / 1e6)} milhões de habitantes · ${esc(v.periodLabel || v.year)}</p></div>
      <div class="bp-ctl">${v.periodHtml || ''}${miniSwitch(metric)}</div></div>`;
  }

  // The federal balance drawn as two bars a child can compare: what went to the União and what came back.
  function union(v, metric) {
    if (v.fed && !v.fed.ok) {
      const why = v.fed.badMonths.length
        ? `De fevereiro de 2025 a janeiro de 2026 a Receita Federal atribuiu ao Distrito Federal até 25% de toda a arrecadação do país, sem nota explicativa. Com isso, o valor por estado desses ${v.fed.badMonths.length} meses não é confiável e não é mostrado. O total do Brasil está correto.`
        : v.fed && !v.fed.twoStepComplete ? 'O gasto federal pela regra em duas etapas ainda não foi calculado para todos os meses deste período.'
        : 'Os repasses da União ainda não foram publicados para todos os meses deste período.';
      return `<div class="bp-union na"><div class="u-title">O estado e a União · ${esc(v.periodLabel)}</div><p class="u-na">${why}</p></div>`;
    }
    const max = Math.max(v.sent, v.received);
    const estNote = v.fed && v.fed.estimatedMonths && v.fed.estimatedMonths.length && window.BIL.estimateNote ? window.BIL.estimateNote() : null;
    const pm = v.monthFed || v.month; const lab = v.fedLabel || v.periodLabel || v.year;
    const amount = (x) => (metric === 'perPerson' ? `${perMonth(pm(x))}<small>/mês por pessoa</small>`
      : metric === 'total' ? bi(x) : `R$ ${per100(x, v.sent)}<small> de cada 100 que foram</small>`);
    // D146: the DF shows the estimate (head-office tax above the DF's share of GDP leaves the DF), marked in the verdict.
    const review = false;
    const verdict = review ? 'Posição do DF em revisão: a conta que separa os dois lados ainda está em construção'
      : metric === 'proportion'
      ? `Para cada R$ 100 que foram para a União, voltaram R$ ${per100(v.received, v.sent)}`
      : `${v.sends ? 'Enviou' : 'Recebeu'} ${metric === 'perPerson' ? `${perMonth(pm(Math.abs(v.sent - v.received)))} a mais por pessoa, por mês` : `${bi(Math.abs(v.sent - v.received))} a mais (${lab})`}${v.uf === 'DF' ? ' (estimativa)' : ''}`;
    return `<div class="bp-union">
      <div class="u-title">O estado e a União · ${esc(lab)}</div>
      ${[[v.sent, `<div class="u-row"><span class="u-lab">Foi para a União</span><span class="u-bar"><i class="out" style="width:${(v.sent / max) * 100}%"></i></span><b>${amount(v.sent)}</b></div>`], [v.received, `<div class="u-row"><span class="u-lab">Voltou para o estado</span><span class="u-bar"><i class="back" style="width:${(v.received / max) * 100}%"></i></span><b>${amount(v.received)}</b></div>`]].sort((x, y) => (y[0] || 0) - (x[0] || 0)).map((x) => x[1]).join('')}
      <div class="u-verdict ${review ? '' : v.sends ? 'g' : 'r'}">${verdict}</div>
      ${v.fed ? `<p class="u-what">Voltou = ${[['repasses da União', v.fed.transfers || 0], ['INSS', v.fed.inss || 0], ['BPC', v.fed.bpc || 0], ['Bolsa Família', v.fed.bolsa || 0], ['Fundo Constitucional do DF', v.fed.fcdf || 0], ['gasto federal no estado', v.fed.fedSpending || 0]].filter(([, x]) => x > 0).sort((a, b) => b[1] - a[1]).map(([l, x]) => `${l} ${bi(x)}${l === 'gasto federal no estado' && v.fed.fedSpendingParts.length ? ` (${v.fed.fedSpendingParts.slice(0, 5).map((p) => `${p.label} ${bi(p.value)}`).join(', ')}${v.fed.fedSpendingParts.length > 5 ? ' e outros' : ''})` : ''}${l === 'Fundo Constitucional do DF' && v.fed.fcdfPersonnel ? ` (${bi(v.fed.fcdfPersonnel)} em pessoal: polícias, bombeiros, saúde e educação do DF)` : ''}`).join(' · ')}.</p>
      <p class="u-caveat">Gasto federal pela regra em duas etapas: vale o estado onde o dinheiro foi aplicado; quando o arquivo não diz, o gasto é da União, e não do estado da unidade que pagou (só a folha dos ex-territórios do Amapá, de Rondônia e de Roraima conta no estado, pela divisão de pessoal de cada um). Benefícios pagos a pessoas do país inteiro por uma unidade central (seguro-desemprego, abono, auxílio emergencial, BEm) contam no estado quando o arquivo diz qual é; seguro-desemprego e abono, também no ano inteiro em que o Ministério do Trabalho publica por estado (hoje, 2024)${v.fed.centralWithoutState ? `; neste período, ${bi(v.fed.centralWithoutState)} do país ficam com a União` : ''}.</p>` : ''}
      ${v.uf === 'DF' || v.uf === 'RJ' ? '<p class="u-caveat">A folha militar paga pelas pagadorias centrais (Exército no DF, Marinha e Aeronáutica no RJ), as compras do Ministério da Saúde e os outros programas nacionais que o arquivo não põe em nenhum estado não contam aqui: são da União (bloco "União" na legenda do mapa).</p>' : ''}
      ${v.uf === 'DF' ? '<p class="u-caveat">A Receita registra o imposto onde fica a sede de quem paga. Por isso a arrecadação do DF inclui impostos de empresas e órgãos com sede em Brasília, que vêm de clientes e operações do país inteiro.</p>' : ''}
      ${estNote ? `<p class="u-caveat est">${esc(estNote.text)}</p>` : ''}
    </div>`;
  }

  const foot = (v) => `<p class="bp-foot">${v.toMunicipalities > 0 ? `Das receitas, ${bi(v.toMunicipalities)} são repassados aos municípios e ${bi(v.fundeb)} vão para o Fundeb.` : `Brasília é o único município do DF e o GDF faz o papel da prefeitura, por isso não há repasse a municípios. ${bi(v.fundeb)} vão para o Fundeb.`} "Por pessoa" é uma média: o total dividido pela população (IBGE ${v.year}) e por 12 meses.</p>`;

  // ---------- Round 6: the same component on both sides, green in, red out ----------
  const sideTotal = (v, side) => (side === 'in' ? v.revenueTotal : v.spendingTotal);
  const sideHead = (v, metric, side, cls = '') => {
    const total = sideTotal(v, side);
    const amount = metric === 'proportion' ? 'R$ 100' : metric === 'total' ? bi(total) : `${reais(v.month(total))}<small>/mês</small>`;
    // D116: when the lines that go out are drawn, the total is what stays with the state, and the header says so.
    const net = side === 'in' && v.revenueGross != null && v.revenueGross !== v.revenueTotal;
    return `<div class="side-h ${side} ${cls}"><span class="side-k">${side === 'in' ? (net ? 'Recebeu' : 'Entrou') : 'Saiu'}</span>
      <span class="side-t">${side === 'in' ? (net ? `O que fica com ${v.uf === 'DF' ? 'o GDF' : 'o estado'}` : 'De onde vem o dinheiro') : 'Para onde vai o dinheiro'}</span><b>${amount}</b></div>`;
  };
  const item6 = (v, metric, it, side, width, variant) => {
    const drill = side === 'out' && it.label !== 'Demais áreas';
    const tag = drill ? 'button type="button"' : 'div';
    return `<${tag} class="it6 ${side}${it.gone ? ' gone' : ''} ${variant}"${drill ? ` data-drill data-label="${esc(it.label)}"` : ''} style="--s:${it.color};--ic:${it.iconColor}">
      <span class="ico">${side === 'in' ? revIcon(it.label, 20) : fnIcon(it.label, 20)}</span>
      <span class="txt"><span class="nm">${esc(short(it.label))}${it.gone ? ' <em class="gone-tag">sai</em>' : ''}</span><span class="ds">${esc(it.desc || (side === 'in' ? DESC_REV : DESC_FN)[it.label] || '')}</span></span>
      <b class="val">${it.gone ? '−' : ''}${valueOf(v, metric, it.value, sideTotal(v, side))}</b>
      <span class="bar"><i style="width:${width.toFixed(1)}%"></i></span></${drill ? 'button' : 'div'}>`;
  };
  // ---------- Round 7: the taxes the people of the state paid, to the União, the state and the municipalities ----------
  const DEST = { uniao: { label: 'União', color: '#2a78d6' }, estado: { label: 'Estado', color: '#4a3aa7' }, municipios: { label: 'Prefeituras', color: '#eb6834' } };
  const YELLOW_RAMP = ['#8C5E00', '#F2C94C'];
  // Federal taxes grouped into names people know. Keys are the Receita Federal per-state file columns.
  const FED = [
    ['INSS', ['social_security_contributions_rgps'], 'contribuição sobre os salários, do trabalhador e da empresa', 'users'],
    ['Imposto de renda', ['irpf', 'irpj', 'irrf'], 'sobre salários, lucros das empresas e aplicações', 'wallet'],
    ['COFINS e PIS', ['cofins', 'pis_pasep'], 'sobre o faturamento das empresas; vêm embutidos nos preços', 'receipt'],
    ['CSLL', ['csll'], 'sobre o lucro das empresas', 'briefcase'],
    ['IPI', ['ipi'], 'sobre produtos industrializados', 'factory'],
    ['Imposto de importação', ['import_tax'], 'sobre produtos que vêm de outros países', 'ship'],
    ['IOF', ['iof'], 'sobre empréstimos, câmbio e seguros', 'banknote'],
    ['Previdência dos servidores federais', ['civil_servant_social_security_pss'], 'contribuição dos servidores da União', 'landmark'],
    ['Outros tributos federais', ['itr', 'export_tax', 'cide_fuels', 'other_rfb_revenue'], 'imposto territorial rural, CIDE dos combustíveis e outros', 'coins'],
  ];
  const STATE_TAX = {
    'ICMS': ['ICMS', 'sobre o que se compra: produtos, energia, combustível', 'shopping-cart'],
    'IPVA': ['IPVA', 'imposto anual dos veículos', 'car'],
    'ITCD (heranças e doações)': ['ITCD', 'sobre heranças e doações', 'scroll-text'],
    'Imposto de renda retido na fonte': ['Imposto de renda dos servidores estaduais', 'retido na folha; fica com o estado', 'wallet'],
    'Outros impostos e taxas': ['Taxas estaduais', 'taxas e outros tributos do estado', 'receipt'],
    // Only the DF reports these: Brasília has no prefeitura, so the GDF charges the city taxes too.
    'ISS': ['ISS', 'sobre serviços: consertos, consultas, escolas, aplicativos', 'wrench', 'municipios'],
    'IPTU': ['IPTU', 'imposto anual dos imóveis urbanos', 'house', 'municipios'],
    'ITBI': ['ITBI', 'sobre a compra e venda de imóveis', 'building', 'municipios'],
  };
  const MUNI_TAX = [
    ['iss', 'ISS', 'sobre serviços: consertos, consultas, escolas, aplicativos', 'wrench'],
    ['iptu', 'IPTU', 'imposto anual dos imóveis urbanos', 'house'],
    ['itbi', 'ITBI', 'sobre a compra e venda de imóveis', 'building'],
    ['irrf', 'Imposto de renda dos servidores municipais', 'retido na folha; fica com a prefeitura', 'wallet'],
    ['other_taxes_fees', 'Taxas municipais', 'taxas e contribuições das prefeituras', 'receipt'],
  ];
  function paidView(v) {
    const F = v.fed ? { by_tax: v.fed.sentOk ? v.fed.byTax : {} } : BI.federal[v.uf];
    const items = FED.map(([label, keys, desc, ic]) => ({ label, value: keys.reduce((a, k) => a + (F.by_tax[k] || 0), 0), desc, ic, dest: 'uniao' }));
    const stateLines = (v.b ? v.b.revenue_top : BI.budgets[v.uf].revenue_top).filter((r) => STATE_TAX[r.label]);
    for (const r of stateLines) {
      const [label, desc, ic, dest = 'estado'] = STATE_TAX[r.label];
      items.push({ label, value: r.value, desc, ic, dest });
    }
    // Municipal taxes: SC comes from the municipal series; other states only have 2024 in this preview.
    const M = v.period ? (window.BIL.muniTaxesAt ? window.BIL.muniTaxesAt(v.uf, v.period) : null)
      : (BI.municipal && BI.municipal[v.uf]);
    if (M) for (const [key, label, desc, ic] of MUNI_TAX) items.push({ label, value: M[key], desc, ic, dest: 'municipios' });
    const kept = items.filter((i) => i.value > 0).sort((a, b) => b.value - a.value);
    // Three spheres give up to 19 taxes; 12 cards keep IPTU and ITBI visible and the "Demais" row small.
    const TOP = 12;
    const shown = kept.slice(0, TOP);
    const folded = kept.slice(TOP);
    if (folded.length) shown.push({ label: 'Demais tributos', value: folded.reduce((a, i) => a + i.value, 0), ic: 'coins', dest: null,
      desc: `inclui ${folded.slice(0, 3).map((i) => lower(i.label)).join(' · ')}${folded.length > 3 ? ` · e mais ${folded.length - 3}` : ''}` });
    // Each tax is averaged over the months its own source covers: federal taxes over the federal months, state and city
    // taxes over the months of the last report (a state files every two months).
    const MO = { uniao: v.fed && v.fed.months ? v.fed.months : v.budgetMonths, estado: v.budgetMonths, municipios: (M && M.months) || v.budgetMonths };
    const pmOf = (it) => (it.dest ? it.value / v.pop / MO[it.dest] : (it.members || []).reduce((a, x) => a + x.value / v.pop / MO[x.dest], 0));
    if (folded.length) shown[shown.length - 1].members = folded;
    const list = shown.map((it) => ({ ...it, pm: pmOf(it) })).sort((a, b) => b.pm - a.pm).map((it, i, a) => ({ ...it, color: shade(YELLOW_RAMP, i, a.length), iconColor: it.dest ? DEST[it.dest].color : '#5B6773' }));
    const byDest = { uniao: 0, estado: 0, municipios: 0 }, byDestPM = { uniao: 0, estado: 0, municipios: 0 };
    for (const i of kept) { byDest[i.dest] += i.value; byDestPM[i.dest] += i.value / v.pop / MO[i.dest]; }
    return { list, total: kept.reduce((a, i) => a + i.value, 0), byDest, byDestPM, totalPM: Object.values(byDestPM).reduce((a, x) => a + x, 0), months: MO,
      municipal: M || null, otherAgencies: F.by_tax.administered_by_other_agencies || 0, federalMissing: Boolean(v.fed && !v.fed.sentOk) };
  }

  const scaler7 = (v, metric) => {
    const tot = { paid: v.paid.totalPM, in: v.revenueTotal, out: v.spendingTotal };
    const sv = (it, side) => (side === 'paid' ? (metric === 'total' ? it.value : metric === 'proportion' ? it.pm / tot.paid : it.pm)
      : metric === 'proportion' ? it.value / tot[side] : metric === 'perPerson' ? v.month(it.value) : it.value);
    const max = Math.max(...v.paid.list.map((p) => sv(p, 'paid')), ...v.revenue.map((r) => sv(r, 'in')), ...v.spending.map((s) => sv(s, 'out')));
    return (it, side) => Math.max(1.5, (sv(it, side) / max) * 100);
  };
  const paidList = (v, metric) => v.paid.list.slice().sort((a, b) => (metric === 'total' ? b.value - a.value : b.pm - a.pm))
    .map((it, i, a) => ({ ...it, color: shade(YELLOW_RAMP, i, a.length) }));
  const paidHead = (v, metric, cls = '') => {
    const amount = metric === 'proportion' ? 'R$ 100' : metric === 'total' ? bi(v.paid.total) : `${reais(v.paid.totalPM)}<small>/mês</small>`;
    return `<div class="side-h paid ${cls}"><span class="side-k">Pagou</span><span class="side-t">Impostos pagos por quem vive aqui</span><b>${amount}</b></div>`;
  };
  // In the DF the city taxes are Brasília's: the GDF charges them because the DF has no prefeitura (CF art. 32).
  const destName = (v, k) => (v.destLabel && v.destLabel[k]) || (v.uf === 'DF' && k === 'municipios' ? 'Brasília' : DEST[k].label);
  const paidItem = (v, metric, it, width, variant) => `<div class="it6 paid ${variant}" style="--s:${it.color};--ic:${it.iconColor}">
      <span class="ico">${icon(it.ic, 20)}</span>
      <span class="txt"><span class="nm">${esc(it.label)}${it.dest ? ` <em class="dest" style="--d:${DEST[it.dest].color}">${destName(v, it.dest)}</em>` : ''}</span><span class="ds">${esc(it.desc || '')}</span></span>
      <b class="val">${metric === 'perPerson' ? `${perMonth(it.pm)}<small>/mês</small>` : metric === 'total' ? bi(it.value) : `R$ ${per100(it.pm, v.paid.totalPM)}<small> de cada 100</small>`}</b>
      <span class="bar"><i style="width:${width.toFixed(1)}%"></i></span></div>`;
  // Where the taxes went: one bar split into União, state and municipalities.
  const destBar = (v, metric) => {
    const key = metric === 'total' ? v.paid.byDest : v.paid.byDestPM, all = metric === 'total' ? v.paid.total : v.paid.totalPM;
    const parts = Object.entries(key).filter(([, x]) => x > 0).sort((a, b) => b[1] - a[1]); // D73
    const amt = (x) => (metric === 'perPerson' ? `${reais(x)}/mês` : metric === 'total' ? bi(x) : `R$ ${per100(x, all)} de cada 100`);
    // A thin bar plus a legend underneath, so a small share (the municipalities) never loses its label.
    return `<div class="dest-bar">${parts.map(([k, x]) => `<span style="--d:${DEST[k].color};width:${(x / all) * 100}%"></span>`).join('')}</div>
      <div class="dest-legend">${parts.map(([k, x]) => `<span style="--d:${DEST[k].color}"><i></i><b>${destName(v, k)}</b> ${amt(x)}</span>`).join('')}</div>`;
  };
  function headline7(v, metric) {
    const chip = (cls, html) => `<span class="chip ${cls}">${html}</span>`;
    // Per person: each destination over its own months (paid.byDestPM); per 100: shares of those monthly averages.
    const d = metric === 'total' ? v.paid.byDest : v.paid.byDestPM, all = metric === 'total' ? v.paid.total : v.paid.totalPM, hasM = d.municipios > 0;
    if (metric === 'proportion') {
      return `<p class="bp-headline">De cada R$ 100 que quem vive em ${esc(v.name)} ${chip('paid', 'pagou em impostos')}, R$ ${per100(d.uniao, all)} foram para a União, R$ ${per100(d.estado, all)} para o ${v.uf === 'DF' ? 'GDF como estado' : 'estado'}${hasM ? ` e R$ ${per100(d.municipios, all)} para ${v.uf === 'DF' ? 'o GDF como prefeitura de Brasília' : 'as prefeituras'}` : ''}. Do que o ${v.uf === 'DF' ? 'GDF' : 'governo estadual'} ${chip('in', 'recebeu')}, ele ${chip('spent', `gastou R$ ${per100(v.spendingTotal, v.revenueTotal)} de cada 100`)}.</p>`;
    }
    const f = metric === 'perPerson' ? reais : bi;           // for values already per person and month (paid) or totals
    const g = metric === 'perPerson' ? (x) => reais(v.month(x)) : bi; // for the state budget totals
    const lead = metric === 'perPerson' ? 'Por pessoa, por mês, quem vive em' : `Em ${v.year}, quem vive em`;
    const toLocal = v.uf === 'DF' && hasM
      ? `${f(d.uniao)} para a União e ${f(d.estado + d.municipios)} para o GDF, que é o governo do estado (${f(d.estado)} em impostos de estado) e também a prefeitura de Brasília (${f(d.municipios)} em ISS, IPTU e ITBI)`
      : `${f(d.uniao)} para a União, ${f(d.estado)} para o estado${hasM ? ` e ${f(d.municipios)} para as prefeituras` : ''}`;
    const passed = [v.toMunicipalities > 0 ? `${g(v.toMunicipalities)} às prefeituras` : '', v.fundeb > 0 ? `${g(v.fundeb)} ao Fundeb` : ''].filter(Boolean).join(' e ');
    return `<p class="bp-headline">${lead} ${esc(v.name)} ${chip('paid', `pagou ${f(all)} em impostos`)}: ${toLocal}. ${v.uf === 'DF' ? 'O GDF' : 'O governo estadual'} ${chip('in', `recebeu ${g(v.revenueTotal)}`)}, o que fica com ele dos impostos, dos repasses da União e das outras receitas${passed ? ` depois de passar ${passed}` : ''}, e ${chip('spent', `gastou ${g(v.spendingTotal)}`)}.</p>`;
  }
  const foot7 = (v) => {
    const M = v.paid.municipal;
    const cov = M ? (M.reported < M.municipalities ? `Impostos municipais: dados de ${M.reported} das ${M.municipalities} prefeituras que enviaram o relatório ao Tesouro. ` : `Impostos municipais: soma das ${M.municipalities} prefeituras. `) : (v.uf === 'DF' ? '' : 'Impostos municipais: coleta em andamento. ');
    const other = v.paid.otherAgencies > 0 ? `Além disso, ${bi(v.paid.otherAgencies)} foram arrecadados por outros órgãos federais (não são impostos) e entram no saldo com a União. ` : '';
    // D116: what "Recebeu" and "Gastou" leave out, in the state's own numbers.
    const gov = v.uf === 'DF' ? 'o GDF' : 'o governo estadual';
    const d116 = v.revenueGross != null && v.revenueGross !== v.revenueTotal
      ? `Em "Recebeu", ${v.toMunicipalities > 0 ? 'a parte das prefeituras e a contribuição ao Fundeb aparecem como linhas que saem' : 'a contribuição ao Fundeb aparece como linha que sai'}: o total é o que fica com ${gov} (${bi(v.revenueGross)} entraram antes ${v.toMunicipalities > 0 ? 'desses repasses' : 'dessa contribuição'}). Em "Gastou" fica só o gasto do próprio ${v.uf === 'DF' ? 'GDF' : 'governo estadual'}${v.transfersOutOfSpending > 0 ? `: ${bi(v.transfersOutOfSpending)} que o estado registra como despesa de transferência (Encargos Especiais, subfunção Transferências) saíram da conta, porque repasse não é gasto do estado` : ''}.${v.uf === 'DF' ? '' : ' Repasses a prefeituras dentro de Saúde, Educação e outras áreas (convênios e fundo a fundo) continuam nessas áreas, porque o relatório por área não os separa.'} `
      : '';
    return `<p class="bp-foot">Os tributos federais são contados onde a empresa que paga tem sede, o que aumenta estados com muitas sedes. ${cov}${other}${d116}Os salários de professores, médicos e policiais contam dentro de Educação, Saúde e Segurança. ${perPersonNote(v)}</p>`;
  };
  // "Per person" divides by the population and by the months each source really covers inside the period.
  const perPersonNote = (v) => {
    if (!v.period) return `"Por pessoa" é uma média: o total dividido pela população (IBGE ${v.year}) e por 12 meses.`;
    const fed = v.fedLabel || v.periodLabel, own = v.budgetLabel || v.periodLabel;
    return fed === own ? `"Por pessoa" é uma média: o total dividido pela população (IBGE) e pelos meses de ${esc(own)}.`
      : `"Por pessoa" é uma média mensal de cada fonte no período que ela cobre: impostos federais, ${esc(fed)}; contas e impostos ${v.uf === 'DF' ? 'do GDF' : 'do estado'}, ${esc(own)} (último relatório entregue). Em "Total", cada valor soma os meses da sua fonte.`;
  };
  // ---------- D109 (2026-10-07): "Vendeu ao exterior", the 4th column of the state modal ----------
  // Exports are the money of the companies that sell, not of the government, so the column keeps its own scale and always
  // shows totals, in US$ and in R$ (PTAX). Its colour is the project's ink, not the yellow, green or red of the money columns.
  // Comex Stat counts an export in the state that produced the good, wherever the exporting company is (MDIC FAQ, question 10).
  const INK_RAMP = ['#14202B', '#A9B3BD'];
  const usd = (x) => (x >= 1e9 ? `US$ ${nf(x / 1e9, 2)} bi` : x >= 1e6 ? `US$ ${nf(x / 1e6)} mi` : `US$ ${nf(x / 1e3, 0)} mil`);
  const brl2 = (x) => (x >= 1e9 ? `R$ ${nf(x / 1e9, 2)} bi` : `R$ ${nf(x / 1e6)} mi`);
  const pc = (s) => (s * 100 >= 0.05 ? `${nf(s * 100)}%` : 'menos de 0,1%');
  // An icon by the chapter of the Harmonized System (first two digits of the product code).
  const chapterIcon = (sh2) => { const c = +sh2; return c <= 5 ? 'tractor' : c <= 24 ? 'wheat' : c <= 27 ? 'droplets' : c <= 38 ? 'flask-conical' : c <= 43 ? 'factory'
    : c <= 49 ? 'leaf' : c <= 67 ? 'store' : c <= 83 ? 'wrench' : c <= 85 ? 'zap' : c <= 89 ? 'car' : 'globe'; };
  function exportsCol(v) {
    const T = BI.trade, S = T && T.by_uf && T.by_uf[v.uf]; if (!S) return null;
    const ys = v.period ? v.period.years : [];
    const y = ys.includes(2026) ? '2026' : '2025', D = S[y]; if (!D) return null;
    const label = y === '2025' ? '2025, o ano inteiro' : '2026, de janeiro a setembro';
    // the source cuts long official names at 255 letters
    const list = D.top.map(([sh4, name, x, sState, sBr]) => ({ name: name.length >= 254 ? `${name}…` : name, x, ic: chapterIcon(sh4.slice(0, 2)),
      desc: `${pc(sState)} do que o estado vendeu · ${pc(sBr)} do que o Brasil vendeu deste produto` }));
    const rest = D.usd - list.reduce((a, it) => a + it.x, 0);
    if (rest > 0) list.push({ name: 'Demais produtos', x: rest, ic: 'coins', desc: `todos os outros produtos que o estado vendeu ao exterior, ${pc(rest / D.usd)} do total` });
    list.sort((a, b) => b.x - a.x);  // D73, the "Demais" row included
    const items = list.map((it, i, a) => `<div class="it6 exp row" style="--s:${shade(INK_RAMP, i, a.length)};--ic:#14202B">
      <span class="ico">${icon(it.ic, 20)}</span><span class="txt"><span class="nm" title="${esc(it.name)}">${esc(it.name)}</span><span class="ds">${esc(it.desc)}</span></span>
      <b class="val">${usd(it.x)}</b><span class="bar"><i style="width:${Math.max(1.5, (it.x / list[0].x) * 100).toFixed(1)}%"></i></span></div>`).join('');
    const head = `<div class="side-h exp"><span class="side-k">Vendeu</span><span class="side-t">Ao exterior · ${label}</span><b>${usd(D.usd)}<small> ${brl2(D.brl)}</small></b></div>`;
    const note = `<p class="exp-note">Dinheiro das empresas que venderam, não do governo: ${pc(D.share)} de tudo o que o Brasil vendeu ao exterior.${ys.includes(+y) ? '' : ` Não há este dado por estado antes de 2025; aqui está ${label}.`}</p>`;
    const foot = `<p class="exp-foot">O Comex Stat conta cada venda no estado que produziu a mercadoria, não onde fica a empresa que exporta. Valores FOB (no porto de embarque); reais pela PTAX média de cada mês. Fonte: <a href="${esc(T.source.docs)}" target="_blank" rel="noopener">Comex Stat (MDIC/Secex) ↗</a></p>`;
    return { html: head + note + items + foot, tab: usd(D.usd) };
  }
  // D116 (2026-10-07): "Sobrou ou faltou" reads the Balanço Orçamentário, where a state that books the municipalities' share
  // as spending (Encargos Especiais, subfunction Transferências; SP above all) counts it in "Entrou" and again in "Saiu",
  // while "Gastou" already leaves it out. The same amount leaves both sides, so the official result does not change.
  // A single month reads the two-month report, whose spending by area is averaged (x 0.5): the bimester amount is twice it.
  function contasNet(v) {
    const c = v.b.contas, x = (v.transfersOutOfSpending || 0) * (v.period.mode === 'month' ? 2 : 1);
    if (!(x > 0) || c.revenueTotal == null || c.spending == null) return window.BIL.stateContas(v.name, v.b, v.period);
    const html = window.BIL.stateContas(v.name, { ...v.b, contas: { ...c, revenueTotal: c.revenueTotal - x, spending: c.spending - x } }, v.period);
    const IN = 'Entrou (todas as receitas do governo estadual)', OUT = 'Saiu (despesas do governo estadual)', SRC = '<p class="ct-src">';
    if (![IN, OUT, SRC].every((s) => html.split(s).length === 2)) { console.error(`stateContas ${v.uf}: os rótulos do bloco mudaram`); return html; }
    const gov = v.uf === 'DF' ? 'o GDF' : 'o governo estadual';
    return html.replace(IN, 'Entrou (receitas do governo estadual, sem os repasses que ele lança como despesa)').replace(OUT, 'Saiu (despesas do governo estadual, sem esses repasses)')
      .replace(SRC, `<ul class="ct-notes"><li>${bi(x)} de repasses que ${gov} registra como despesa (Encargos Especiais, subfunção Transferências) saíram dos dois lados, como em "Gastou": repasse não é gasto do estado. O resultado oficial não muda.</li></ul>${SRC}`);
  }

  // ---------- Round 8: desktop = three columns (7A); on a narrow screen the same markup becomes one of three
  // mobile layouts (stack, tabs, carousel). Container queries decide, so a phone frame on a desktop page works too.
  let uid8 = 0;
  // The three columns (pagou, recebeu, gastou), shared by the state modal and the municipality panel.
  function tri8(v, metric, opts = {}) {
    const w = scaler7(v, metric);
    const id = `t8-${++uid8}`;
    const total = { paid: v.paid.total, in: v.revenueTotal, out: v.spendingTotal };
    const amt = (x, k) => (metric === 'proportion' ? 'R$ 100' : metric === 'total' ? bi(x) : `${reais(k === 'paid' ? v.paid.totalPM : v.month(x))}<small>/mês</small>`);
    const who = opts.who || 'o estado';
    const cols = [
      ['paid', 'Pagou', paidHead(v, metric) + destBar(v, metric) + paidList(v, metric).map((it) => paidItem(v, metric, it, w(it, 'paid'), 'row')).join('')],
      ['in', 'Recebeu', sideHead(v, metric, 'in') + v.revenue.map((it) => item6(v, metric, it, 'in', w(it, 'in'), 'row')).join('')],
      ['out', 'Gastou', sideHead(v, metric, 'out') + v.spending.map((it) => item6(v, metric, it, 'out', w(it, 'out'), 'row')).join('')],
    ];
    const X = opts.exports;  // D109: the state modal adds "Vendeu ao exterior"; the municipality panel does not
    if (X) cols.push(['exp', 'Vendeu', X.html]);
    return `<div class="tri8 mv-tabs${X ? ' x4' : ''}">
        ${cols.map(([k], i) => `<input type="radio" class="t8" name="${id}" id="${id}-${k}"${i === 0 ? ' checked' : ''}>`).join('')}
        <div class="tabbar8">${cols.map(([k, l]) => `<label for="${id}-${k}" class="${k}"><span>${l}</span><b>${k === 'exp' ? X.tab : amt(total[k], k)}</b></label>`).join('')}</div>
        <div class="cols8">${cols.map(([k, , html]) => `<section class="c8 ${k}">${html}</section>`).join('')}</div>
        <p class="swipe8">arraste para o lado para ver o que ${who} recebeu e gastou ›</p>
      </div>`;
  }
  function renderStateModal(v, metric, opts = {}) {
    const cases8 = window.BIC.cards(v);
    const contas = v.period && v.b && v.b.contas && window.BIL ? contasNet(v) : '';
    const who = v.period && window.BIG ? window.BIG.stateSection(v.uf, v.name, v.period) : '';
    return `<div class="bp bp6 bp7 bp8">${head(v, metric)}${opts.afterHead || ''}${union(v, metric)}${contas}${who}${headline7(v, metric)}
      ${tri8(v, metric, { ...opts, exports: exportsCol(v) })}${v.b && v.b.spendingNote ? `<p class="bp-foot">${esc(v.b.spendingNote)}</p>` : ''}${foot7(v)}${cases8}</div>`;
  }

  // Municipality view (round 10): the city government's own budget and the taxes paid there, in the same shape as a state.
  // The state wording ("rede estadual", "Assembleia") is replaced by the prefeitura's own.
  const MUNI_FN = {
    'Educação': 'escolas e creches da prefeitura, com os professores', 'Saúde': 'postos de saúde e atendimento da prefeitura',
    'Administração': 'servidores da área administrativa e o funcionamento da prefeitura', 'Previdência Social': 'aposentadorias e pensões dos servidores municipais',
    'Urbanismo': 'ruas, praças, iluminação e obras na cidade', 'Saneamento': 'água, esgoto e drenagem', 'Legislativa': 'Câmara de Vereadores',
    'Judiciária': 'gastos que a prefeitura classificou como Judiciário', 'Segurança Pública': 'guarda municipal e defesa civil', 'Transporte': 'transporte e estradas do município',
  };
  const MUNI_REV = { 'Receita patrimonial': 'rendimentos e aluguéis da prefeitura', 'Receita de serviços': 'serviços prestados pela prefeitura', 'Contribuições': 'contribuição dos servidores e da iluminação pública' };
  const MUNI_PLAIN = { ...PLAIN, 'Legislativa': 'Câmara de Vereadores', 'Judiciária': 'Judiciário', 'Receita de serviços': 'serviços da prefeitura', 'Receita patrimonial': 'rendimentos e aluguéis' };
  function muniView(code, r) {
    const B = window.BIL.muniBudgetAt(code, r); const F = window.BIL.municipalAt(code, r);
    if (!B || !F) return null;
    const desc = (a) => [...a].sort((x, y) => y.value - x.value);
    const top = (arr, n, noun) => { const d = desc(arr); const keep = d.slice(0, n), rest = d.slice(n); const sum = rest.reduce((a, x) => a + x.value, 0);
      return sum > 0 ? [...keep, { label: noun === 'áreas' ? 'Demais áreas' : 'Demais receitas', value: sum, desc: examples(rest, noun, noun !== 'áreas', MUNI_PLAIN), members: rest }] : keep; };
    const revenue = desc(top(B.revenue_top, 7, 'receitas')).map((x, i, a) => ({ ...x, desc: x.desc || MUNI_REV[x.label], color: shade(GREEN_RAMP, i, a.length), iconColor: x.origin ? DEST[x.origin].color : '#5B6773' }));
    const spending = desc(top(B.spending_by_function, 7, 'áreas')).map((f, i, a) => ({ ...f, desc: f.desc || MUNI_FN[f.label], group: groupOf(f.label), color: shade(RED_RAMP, i, a.length), iconColor: GROUPS[groupOf(f.label)].color }));
    const paidItems = [];
    if (F.federal_revenue != null && !F.revenueWider) paidItems.push({ label: 'Tributos federais', value: F.federal_revenue, desc: 'registrados no município pela Receita Federal (imposto de renda, INSS, COFINS e outros)', ic: 'landmark', dest: 'uniao' });
    for (const x of B.taxes) paidItems.push({ ...x, dest: 'municipios' });
    const kept = desc(paidItems.filter((x) => x.value > 0));
    const months = r.mode === 'month' ? r.months.length : B.months;
    // One window for every item here: the federal figure is shown only when it covers the same year as the budget.
    const list = kept.map((it, i, a) => ({ ...it, pm: it.value / F.population / months, color: shade(YELLOW_RAMP, i, a.length), iconColor: DEST[it.dest].color }));
    const byDest = { uniao: 0, estado: 0, municipios: 0 }; for (const x of kept) byDest[x.dest] += x.value;
    const byDestPM = Object.fromEntries(Object.entries(byDest).map(([k, x]) => [k, x / F.population / months]));
    const total = kept.reduce((a, x) => a + x.value, 0);
    return {
      name: F.name, pop: F.population, revenue, spending, revenueTotal: B.revenue_current_total, spendingTotal: B.spending_total,
      paid: { list, total, byDest, byDestPM, totalPM: total / F.population / months, municipal: null, otherAgencies: 0 },
      month: (x) => x / F.population / months, period: r, b: B, fed: null, cases: [], destLabel: { municipios: 'Prefeitura' },
    };
  }
  function muniColumns(code, r, metric, opts = {}) {
    const mv = muniView(code, r);
    if (!mv || (!mv.revenue.length && !mv.spending.length)) return `<p class="mun-none">Não há relatório desta prefeitura para ${esc(r.label)}. As contas das prefeituras de SC começam em 2021 neste site.</p>`;
    const note = mv.b.spendingNote ? `<p class="bp-foot">${esc(mv.b.spendingNote)}</p>` : '';
    return `<div class="bp bp6 bp7 bp8 muni8">${tri8(mv, metric, { ...opts, who: 'a prefeitura' })}${note}<p class="bp-foot">Pagou: tributos federais registrados no município (Receita Federal, dado anual) e os impostos da própria prefeitura. Recebeu e Gastou: relatório da prefeitura ao Tesouro (SICONFI, RREO). "Por pessoa" divide pela população (IBGE) e pelos meses do período.</p></div>`;
  }

  window.BIP = { view, muniView, render: { renderStateModal, muniColumns }, helpers: { bi, reais, perMonth, esc, short, fnIcon, revIcon, GROUPS, DESC_FN } };
})();
