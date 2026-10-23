// "O que o Brasil vende" on Início (D109, D111), built only where the trade switch of data/features.json is on (D159, staging):
// build-site.py loads this file right after home-feed.js, which then places the section under "Por que falta dinheiro" and
// shows the link of its block 4. Classic script; exposes window.BIHT.
(function () {
  const { nf, esc, dt, pct, link } = window.BIHF;
  // D109, D111: "O que o Brasil vende", every exported product (posição SH4) from the largest to the smallest, with its own
  // period switch, since trade data has all of 2025 and 2026 up to September and does not follow the map's selector.
  // BI.trade comes from data/trade/ (Comex Stat, IBGE, Conab, ANP, ANM, World Bank). Neutral wording: the data speaks.
  const SHOW_TRADE = 20, TOP_DEST = 50;
  let tradeYear = '2025', tradeAll = false;
  const usd = (v) => (v >= 1e9 ? `US$ ${nf(v / 1e9, 2)} bi` : v >= 1e6 ? `US$ ${nf(v / 1e6, 1)} mi` : v >= 1e3 ? `US$ ${nf(v / 1e3, 0)} mil` : `US$ ${nf(v, 0)}`);
  const brl = (v) => (v >= 1e12 ? `R$ ${nf(v / 1e12, 2)} tri` : v >= 1e9 ? `R$ ${nf(v / 1e9, 2)} bi` : v >= 1e6 ? `R$ ${nf(v / 1e6, 1)} mi` : v >= 1e3 ? `R$ ${nf(v / 1e3, 0)} mil` : `R$ ${nf(v, 0)}`);
  const share100 = (s) => (s * 100 >= 0.005 ? `${nf(s * 100, 2)}%` : 'menos de 0,01%');
  const qty = (x) => (x[0] == null ? 'sem número oficial' : `${nf(+x[0], Number.isInteger(+x[0]) ? 0 : 1)} ${x[1]}`);
  // World Bank series names, in Portuguese.
  const REF_PT = { 'Crude oil, Brent': 'petróleo Brent', 'Soybeans': 'soja', 'Iron ore, cfr spot': 'minério de ferro entregue na China', 'Coffee, Arabica': 'café arábica',
    'Coffee, Robusta': 'café robusta', 'Beef': 'carne bovina', 'Sugar, world': 'açúcar, mercado mundial', 'Chicken': 'frango', 'Maize': 'milho',
    'Soybean meal': 'farelo de soja', 'Cotton, A Index': 'algodão, índice A', 'Banana, US': 'banana nos EUA', 'Banana, Europe': 'banana na Europa' };
  const PRICE_UNIT = { 'US$/barril': ['por barril', 2], 'US$/t': ['por tonelada', 0], 'US$/kg': ['por kg', 2] };
  function shareBlock(s) {
    if (s.out == null) return `<p class="ht-sh na"><b>${esc(s.name)}:</b> a parte da produção que vai para fora não é calculada; ${esc((s.note || '').replace(/^Não calculado: /, ''))}</p>`;
    const out = Math.round(s.out * 1000) / 10, stay = Math.round((100 - out) * 10) / 10;
    // D73: the larger part first.
    const parts = [['out', s.lower ? `vai para fora, pelo menos ${pct(out)}` : `vai para fora ${pct(out)}`, out], ['stay', s.lower ? `fica no Brasil, no máximo ${pct(stay)}` : `fica no Brasil ${pct(stay)}`, stay]].sort((a, b) => b[2] - a[2]);
    return `<div class="ht-sh"><div class="ht-sh-h"><b>${esc(s.name)}:</b> quanto da produção</div>
      <div class="ht-split">${parts.map(([k, , w]) => `<i class="${k}" style="width:${w}%"></i>`).join('')}</div>
      <p class="ht-sh-l">${parts.map(([k, l]) => `<span class="${k}"><i></i>${l}</span>`).join('')}</p>
      <p class="ht-sh-s">Produção: ${qty(s.prod)}, ${esc(s.prod[2])} (${link(s.prod[4], s.prod[3])}). Exportação: ${qty(s.exp)}, ${esc(s.exp[2])} (${link(s.exp[4], s.exp[3])}).${s.lower ? ` ${esc(s.note || '')}` : ''}</p></div>`;
  }
  function priceLine(pr) {
    if (!pr.refs.length) return `<p class="ht-price"><b>Preço:</b> ${esc(pr.comp)}</p>`;
    const [u, d] = PRICE_UNIT[pr.unit] || ['', 2];
    const refs = pr.refs.map(([series, , val, ratio]) => `o preço de referência do Banco Mundial (${esc(REF_PT[series] || series)}) foi US$ ${nf(val, d)}, e o do Brasil ficou em ${nf(ratio * 100, 0)}% dele`);
    return `<p class="ht-price"><b>Preço em 2025:</b> o Brasil vendeu a US$ ${nf(pr.bz, d)} ${u}; ${refs.join('; ')}. <small>${esc(pr.comp)}</small></p>`;
  }
  function tradeItem(T, p, y, i, max) {
    const q = p[y], name = p.name.length >= 254 ? `${p.name}…` : p.name;  // the source cuts long names at 255 letters
    return `<li class="ht-it"><span class="ht-rk">${nf(i + 1, 0)}</span><div class="ht-main">
      <div class="ht-row"><b class="ht-nm">${esc(name)}</b><span class="ht-v"><b>${usd(q[0])}</b><small>${brl(q[1])}</small></span></div>
      <div class="ht-bar"><i><b style="width:${Math.max(0.4, (q[2] / max) * 100).toFixed(2)}%"></b></i><em>${share100(q[2])} de tudo o que o Brasil vendeu</em></div>
      ${q[4] ? `<p class="ht-dest"><b>Para onde:</b> ${q[4].map(([c, s]) => `${esc(c)} ${pct(s * 100)}`).join(' · ')}</p>` : ''}
      ${(T.share[p.sh4] || []).map(shareBlock).join('')}${T.prices[p.sh4] ? priceLine(T.prices[p.sh4]) : ''}</div></li>`;
  }
  function tradeSection() {
    const T = window.BI && window.BI.trade; if (!T) return '';
    const y = tradeYear, P = T.periods[y], C = T.context;
    const list = T.products.filter((p) => p[y]).sort((a, b) => b[y][0] - a[y][0]);
    const shown = tradeAll ? list : list.slice(0, SHOW_TRADE), max = list[0][y][2];
    // The balance is shown as the difference of the two rounded values, so it adds up by hand (D94).
    const r1 = (v) => Math.round(v / 1e8) / 10, bal = Math.round((r1(P.usd) - r1(P.imports_usd)) * 10) / 10;
    if (Math.abs(bal - r1(P.balance_usd)) > 0.05) console.error('O que o Brasil vende: o saldo arredondado não fecha');
    const per = y === '2025' ? '2025, o ano inteiro' : '2026, de janeiro a setembro';
    const noShare = T.share_none.map((s) => `${s.name.split(' (')[0].toLowerCase()} (${esc(s.note.replace(/^Não calculado: /, '').split(/\.\s/)[0].replace(/\.$/, ''))})`).join('; ');
    return `<div class="ht-in"><div class="hf-h"><span>O que o Brasil vende</span><small>todos os produtos, do maior para o menor</small></div>
      <div class="ht-ctl"><div class="ht-seg" role="group" aria-label="Período do comércio exterior">${[['2025', '2025 (ano inteiro)'], ['2026', '2026 (janeiro a setembro)']].map(([k, l]) => `<button type="button" data-ty="${k}" aria-pressed="${k === y}">${l}</button>`).join('')}</div>
        <p class="ht-per">Estes números não seguem o seletor de período do mapa: o comércio exterior tem 2025 inteiro e 2026 até setembro.</p></div>
      <div class="ht-ctx">
        <div><span>Vendeu ao exterior</span><b>US$ ${nf(r1(P.usd), 1)} bi</b><small>${brl(P.brl)} <span class="hf-exact">R$ ${nf(P.brl / 1e9, 1)} bi</span> · ${per}</small></div>
        <div><span>Comprou do exterior</span><b>US$ ${nf(r1(P.imports_usd), 1)} bi</b><small>${per}</small></div>
        <div><span>Sobrou</span><b>US$ ${nf(bal, 1)} bi</b><small>a venda menos a compra, ${per}</small></div>
        <div><span>Peso no PIB, ${C.gdp_year}</span><b>${pct(C.exports_gdp * 100)}</b><small>do PIB foi vendido ao exterior em bens e serviços; a compra foi ${pct(C.imports_gdp * 100)}</small></div>
        <div><span>Produtos básicos</span><b>${pct(C.basic['2000'] * 100)} → ${pct(C.basic['2025'] * 100)}</b><small>do valor vendido, em 2000 e em 2025</small></div>
      </div>
      <p class="ht-lead">${nf(P.products, 0)} produtos vendidos em ${per}. Para cada um: quanto vendeu em dólar e em reais, a parte de tudo o que o Brasil vendeu e, nos ${TOP_DEST} maiores, os 3 países que mais compraram. Onde há produção oficial medida, quanto dela fica no Brasil e quanto vai para fora; nos maiores produtos, o preço de venda ao lado do preço de referência internacional.</p>
      <ol class="ht-list">${shown.map((p, i) => tradeItem(T, p, y, i, max)).join('')}</ol>
      <button type="button" class="ht-more" data-tmore>${tradeAll ? `Mostrar só os ${SHOW_TRADE} maiores` : `Mostrar todos os ${nf(list.length, 0)} produtos`}</button>
      <p class="ht-foot">Valores FOB: o preço no porto de embarque, sem frete e seguro. Reais: cada mês convertido pela PTAX média do mês (${esc(T.source.fx.split(',')[0])}). Nomes oficiais das posições de 4 dígitos do Sistema Harmonizado; a fonte corta alguns nomes em 255 letras (…). Produção que vai para fora: fonte e ano em cada produto; sem conta possível para ${noShare}. Produtos básicos: fator agregado da Secex calculado com a tabela oficial NCM, porque a Secex deixou de publicar essa divisão em 2020 (${link(T.source.vaf_url, 'tabela NCM')}). Peso no PIB: ${link(T.source.gdp_url, 'IBGE, Contas Nacionais')}. Fontes: ${link(T.source.docs, `Comex Stat (MDIC/Secex), atualizado em ${dt(T.source.updated)}`)} e ${link('https://www.worldbank.org/en/research/commodity-markets', 'Banco Mundial, preços de referência')}.</p></div>`;
  }
  function drawTrade(el) {
    el.innerHTML = tradeSection();
    el.querySelectorAll('[data-ty]').forEach((b) => (b.onclick = () => { tradeYear = b.dataset.ty; drawTrade(el); }));
    const more = el.querySelector('[data-tmore]');
    if (more) more.onclick = () => { const was = tradeAll; tradeAll = !tradeAll; drawTrade(el); if (was) el.scrollIntoView({ block: 'start' }); };
  }
  const section = (mk) => mk('o-que-o-brasil-vende', 'ht', 'data-trade', 'O que o Brasil vende');
  const draw = (el) => { drawTrade(el); el.hidden = !el.innerHTML; };
  const whyLink = `\n      <p class="hw-note"><a href="#o-que-o-brasil-vende">O que o Brasil vende ao exterior, produto por produto ↓</a></p>`;
  window.BIHT = { section, draw, whyLink };
})();
