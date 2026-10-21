// Case views (round 8): the case cards on the state modal, the case page and the comparison page.
// Classic script, shared by the proposals page and the home simulation. Reads window.BI and window.BIP.
(function () {
  const { bi, reais, esc } = window.BIP.helpers;
  const icon = (name, size = 20) => (window.BI.icons[name] || '').replace(/<!--.*?-->/s, '').replace(/class="[^"]*"/, '')
    .replace(/width="24"/, `width="${size}"`).replace(/height="24"/, `height="${size}"`);
  const num = (v) => Math.round(v).toLocaleString('pt-BR');
  const money = (v) => (Math.abs(v) >= 1e9 ? bi(v) : Math.abs(v) >= 1e6 ? `R$ ${(v / 1e6).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} mi` : `R$ ${num(v)}`);
  const initials = (n) => n.split(' ').filter((w) => w.length > 2).slice(0, 2).map((w) => w[0]).join('');
  const link = (l, cls = 'lnk') => `<a class="${cls}" href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label)} <span aria-hidden="true">↗</span></a>`;
  const KIND = { obra: 'Obra pública', preco: 'Preço pago' };

  // ---------- case cards on the state modal ----------
  // "carta": a vertical trading card (Super Trunfo style: picture, name, four stats).
  // "cartao": a horizontal card (picture on the left, stats on the right).
  function cards(v) {
    if (!v.cases.length) return '';
    const pic = (c) => (c.card && c.card.image ? `<img src="${esc(c.card.image)}" alt="">` : `<span class="pic-icon">${icon((c.card && c.card.icon) || 'receipt', 44)}</span>`);
    const stats = (c) => (c.card ? c.card.stats : []).map(([k, val]) => `<li><span>${esc(k)}</span><b>${esc(val)}</b></li>`).join('');
    return `<section class="cc8"><h3>Casos com dados oficiais neste estado</h3><p class="lead">obras e gastos conferidos em documentos oficiais; toque para abrir</p>
      <div class="cc8-grid carta">${v.cases.map((c, i) => `<button type="button" class="cc8-card carta ${c.kind}" data-case="${i}">
        <span class="pic">${pic(c)}<em>${KIND[c.kind]}</em>${c.stage ? `<i class="stage ${esc(c.stage.kind)}">${esc(c.stage.label)}</i>` : ''}</span>
        <span class="info"><strong>${esc(c.title)}</strong><span class="tease">${esc(c.teaser)}</span><ul>${stats(c)}</ul>
        <span class="go">Ver o caso ›</span></span></button>`).join('')}</div></section>`;
  }

  // ---------- case page ----------
  function gallery(media) {
    if (!media || !media.length) return '';
    const [main, ...rest] = media;
    const fig = (m, cls) => `<figure class="${cls}"><img src="${esc(m.src)}" alt="${esc(m.caption)}"><figcaption><span>${esc(m.caption)}</span>
      <a href="${esc(m.link)}" target="_blank" rel="noopener">Foto: ${esc(m.credit)}</a></figcaption></figure>`;
    return `<div class="cp-gallery">${fig(main, 'main')}<div class="side">${rest.map((m) => fig(m, 'thumb')).join('')}</div></div>`;
  }
  function people(list, note) {
    if (!list || !list.length) return '';
    return `<section class="cp-sec"><h3>Quem assinou e quem governava</h3><p class="lead">papéis registrados em documentos oficiais; não é acusação</p>
      <div class="pp-grid">${list.map((p) => `<article class="pp">
        ${p.photo ? `<a class="ph" href="${esc(p.photo_link)}" target="_blank" rel="noopener" title="Foto: ${esc(p.photo_credit)}"><img src="${esc(p.photo)}" alt="${esc(p.name)}"></a>`
          : `<span class="ph init">${esc(initials(p.name))}</span>`}
        <div class="pp-body"><strong>${esc(p.name)}</strong><span class="role">${esc(p.role)}</span><span class="det">${esc(p.detail)}</span>
          ${p.party ? `<span class="party"><b>${esc(p.party)}</b>${esc(p.party_name)}<small>${esc(p.party_note)}</small></span>` : ''}
          <span class="links">${p.links.map((l) => link(l)).join('')}</span></div></article>`).join('')}</div>
      <p class="fine">${esc(note || 'Partido na época do ato, segundo a biografia oficial na Assembleia Legislativa de SC. Fotos do Wikimedia Commons, com autor e licença no link de cada foto.')}</p></section>`;
  }
  function companies(list, lead) {
    if (!list || !list.length) return '';
    const max = Math.max(...list.map((c) => c.value || 0), 1);
    return `<section class="cp-sec"><h3>Empresas contratadas</h3><p class="lead">${esc(lead || 'valor atual dos contratos, com aditivos')}</p>
      <div class="co-grid">${list.map((c) => `<article class="co">
        <div class="co-top"><span class="co-ic">${icon('building-2', 20)}</span><div><strong>${esc(c.name)}</strong>
          ${c.trade_name && c.trade_name.toUpperCase() !== c.name.toUpperCase() ? `<small>nome fantasia na Receita: ${esc(c.trade_name)}</small>` : ''}${c.note ? `<small>${esc(c.note)}</small>` : ''}</div></div>
        <div class="co-val"><b class="${c.value ? '' : 'na'}">${c.value ? money(c.value) : esc(c.value_note || 'valor não publicado')}</b>${c.status ? `<span class="st ${/Rescind/.test(c.status) ? 'r' : ''}">${esc(c.status)}</span>` : ''}</div>
        <span class="bar"><i style="width:${c.value ? Math.max(2, (c.value / max) * 100).toFixed(1) : 0}%"></i></span>
        <div class="co-meta">${c.cnpj ? `<button type="button" class="copy" data-copy="${esc(c.cnpj)}">CNPJ ${esc(c.cnpj)} <span>copiar</span></button>` : `<span class="nocnpj">${esc(c.cnpj_note || 'CNPJ não publicado no registro')}</span>`}
          <span class="ctr">${[].concat(c.contracts).map((x) => `<em>${esc(x)}</em>`).join('')}</span></div>
        <div class="co-links">${c.links.map((l) => link(l, 'btn')).join('')}</div></article>`).join('')}</div></section>`;
  }
  function findings(list) {
    if (!list || !list.length) return '';
    return `<section class="cp-sec"><h3>O que os órgãos de controle disseram</h3><p class="lead">nas palavras de cada órgão, com a situação de hoje</p>
      <ol class="tl">${list.map((f) => `<li><span class="dot"></span><div><b>${esc(f.body)}</b><p>${esc(f.text)}</p>
        <span class="status">${esc(f.status)}</span>${f.url ? link({ label: 'documento', url: f.url }) : ''}</div></li>`).join('')}</ol></section>`;
  }
  function page(c) {
    const facts = c.facts.map((f) => `<div class="fact"><span>${esc(f.label)}</span><b>${esc(f.value)}</b>${f.note ? `<small>${esc(f.note)}</small>` : ''}</div>`).join('');
    const hero = c.media && c.media.length ? gallery(c.media) : `<div class="cp-illus ${c.kind}">${icon((c.card && c.card.icon) || 'receipt', 64)}</div>`;
    const extra = (c.sections || []).map((s) => `<section class="cp-sec"><h3>${esc(s.title)}</h3><ul class="rec">${s.items.map((i) =>
      `<li><b>${esc(i.head)}</b><p>${esc(i.text)}</p>${i.url ? link({ label: 'documento', url: i.url }) : ''}</li>`).join('')}</ul></section>`).join('');
    return `<div class="cp">${hero}
      <div class="cp-title"><span class="kind ${c.kind}">${KIND[c.kind]}</span><h2>${esc(c.title)}</h2><p>${esc(c.subtitle)}</p></div>
      ${c.verdict ? `<div class="cp-verdict"><b>${esc(c.verdict.label)}</b><p>${esc(c.verdict.text)}</p></div>` : ''}
      <div class="cp-facts">${facts}</div>
      ${people(c.people, c.people_note)}${companies(c.company_cards, c.company_lead)}${findings(c.findings)}${extra}
      ${c.compare ? `<div class="cp-cta"><button type="button" class="cta8">${c.kind === 'obra' ? 'Comparar com obras parecidas' : 'Comparar com o preço real'} ›</button></div>` : ''}
      ${(c.sources || []).length ? `<p class="cp-src"><b>Fontes:</b> ${c.sources.map((s) => link(s)).join(' ')}</p>` : ''}</div>`;
  }

  // ---------- comparison ----------
  function compare(c) {
    const cmp = c.compare;
    let body;
    if (c.compare_details) {
      const d = c.compare_details;
      const maxArea = Math.max(...d.map((x) => x.area_m2));
      const maxPer = Math.max(...d.map((x) => x.per_m2));
      body = `<div class="bc-grid">${d.map((x) => {
        // Square side proportional to the square root of the area, so the square's AREA is to scale.
        const side = Math.sqrt(x.area_m2 / maxArea) * 120;
        return `<article class="bc ${x.self ? 'self' : ''}">
          <header><strong>${esc(x.label)}</strong><small>${esc(x.country)} · ${esc(x.years)}</small></header>
          <p class="scope">${esc(x.scope)}</p>
          <div class="deck"><span class="sq" style="width:${side.toFixed(1)}px;height:${side.toFixed(1)}px"></span><em>${num(x.area_m2)} m²</em><small>${num(x.length_m)} m de comprimento × ${String(x.width_m).replace('.', ',')} m de largura</small></div>
          <dl><div><dt>Área do tabuleiro</dt><dd>${num(x.area_m2)} m²</dd></div><div><dt>Custo total (em reais de 2024)</dt><dd>${money(x.total_brl_2024)}</dd></div>
            <div class="per"><dt>Custo por m²</dt><dd>R$ ${num(x.per_m2)}</dd></div></dl>
          <span class="bar"><i style="width:${((x.per_m2 / maxPer) * 100).toFixed(1)}%"></i></span>
          <a class="lnk" href="${esc(x.source)}" target="_blank" rel="noopener">fonte ↗</a></article>`;
      }).join('')}</div>
      <p class="fine">Os quadrados estão na mesma escala: a área de cada um é proporcional à área do tabuleiro da ponte. Custo por m² = custo total ÷ área.</p>`;
    } else {
      const top = Math.max(...cmp.items.map((i) => i.value));
      body = `<ol class="cmp-bars">${cmp.items.map((i) => `<li class="${i.self ? 'self' : ''}"><span class="l">${esc(i.label)}<small>${esc(i.detail || '')}</small></span>
        <b>${esc(i.display)}</b><span class="bar"><i style="width:${Math.max(1.5, (i.value / top) * 100).toFixed(1)}%"></i></span></li>`).join('')}</ol>`;
    }
    return `<div class="cp"><div class="cp-title"><span class="kind ${c.kind}">Comparação</span><h2>${esc(cmp.title)}</h2><p>${esc(cmp.subtitle)}</p></div>
      ${body}
      ${cmp.gap ? `<div class="gap8 ${cmp.gap.positive ? 'alert' : 'ok'}"><p>${esc(cmp.gap.text)}</p></div>` : ''}
      <p class="fine">${esc(cmp.reading)}</p>
      ${(cmp.sources || []).length ? `<p class="cp-src"><b>Fontes:</b> ${cmp.sources.map((s) => link(s)).join(' ')}</p>` : ''}</div>`;
  }

  // Copy buttons (CNPJ) work anywhere the case page is shown.
  document.addEventListener('click', (e) => {
    const b = e.target.closest('[data-copy]');
    if (!b) return;
    navigator.clipboard && navigator.clipboard.writeText(b.dataset.copy.replace(/\D/g, ''));
    b.classList.add('done'); setTimeout(() => b.classList.remove('done'), 1400);
  });

  window.BIC = { cards, page, compare };
})();
