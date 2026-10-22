// Drill-down modal stack: state -> spending area -> case (public work or price) -> comparison.
// Every number rendered here comes from the JSON files passed in; nothing is typed into the markup.
// The state level is drawn by the shared proposals renderer (window.BIP, a classic script loaded first), so the
// home simulation and the proposals page always show the same modal.
const { short } = window.BIP.helpers;
const METRICS = [['perPerson', 'Por pessoa'], ['total', 'Total'], ['proportion', 'Proporção']];
const FROM_MAP = { perCapita: 'perPerson', total: 'total', ratio: 'proportion' };

const bi = (v) => `R$ ${(v / 1e9).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} bi`;
const mi = (v) => `R$ ${(v / 1e6).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} mi`;
const money = (v) => (Math.abs(v) >= 1e9 ? bi(v) : Math.abs(v) >= 1e6 ? mi(v) : `R$ ${Math.round(v).toLocaleString('pt-BR')}`);
const reais = (v) => `R$ ${Math.round(v).toLocaleString('pt-BR')}`;
// Per-person monthly values: small amounts keep their cents, so nothing rounds down to a misleading R$ 0.
const perMonth = (v) => (Math.abs(v) < 10 ? `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : reais(v));
const pct = (v) => `${(v * 100).toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`;
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function bars(items, { max, clickable = false, key = 'label', fmt = money } = {}) {
  const top = max ?? Math.max(...items.map((i) => i.value));
  return `<ol class="bars">${items.map((i, n) => `
    <li${clickable ? ` class="clickable" tabindex="0" role="button" data-i="${n}"` : ''}>
      <span class="bar-label">${esc(i[key])}</span>
      <span class="bar-value">${fmt(i.value)}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${Math.max(1.5, (i.value / top) * 100).toFixed(1)}%"></span></span>
      ${clickable ? '<span class="chev" aria-hidden="true">›</span>' : ''}
    </li>`).join('')}</ol>`;
}

const sourceLinks = (sources) => sources.length
  ? `<footer class="modal-sources"><strong>Fontes:</strong> ${sources.map((s) => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)}</a>`).join(' · ')}</footer>`
  : '';

export function createModals(root, { states, budgets, cases, geo, colorOf, onClose }) {
  const layer = document.createElement('div');
  layer.className = 'modal-layer';
  layer.innerHTML = '<div class="modal-backdrop"></div><div class="modal-panel" role="dialog" aria-modal="true"></div>';
  root.appendChild(layer);
  const panel = layer.querySelector('.modal-panel');
  const stack = [];
  let metric = 'perPerson';
  let cleanup = null; // disposes the state map's WebGL context before the panel is redrawn
  let period = null, latest = null; // shared by every level; set by the hero's period selector
  const stateName = (uf) => states.find((s) => s.uf === uf).name;
  const miniSwitch = () => `<div class="mini-switch" role="group" aria-label="Medida">${METRICS.map(([k, l]) =>
    `<button type="button" data-metric="${k}" aria-pressed="${k === metric}">${l}</button>`).join('')}</div>`;
  const bindSwitch = (p) => p.querySelectorAll('.mini-switch button').forEach((btn) => {
    btn.onclick = () => { metric = btn.dataset.metric; render(); };
  });

  let opener = null; // focus returns here when the last level closes
  const render = () => {
    if (cleanup) { cleanup(); cleanup = null; }
    const top = stack[stack.length - 1];
    if (!top) {
      const was = root.classList.contains('modal-open');
      root.classList.remove('modal-open'); document.documentElement.classList.remove('bi-locked'); onClose();
      if (was && opener && opener.isConnected) opener.focus({ preventScroll: true });
      opener = null; return;
    }
    if (!root.classList.contains('modal-open')) opener = document.activeElement;
    root.classList.add('modal-open'); document.documentElement.classList.add('bi-locked');
    const crumbs = ['Brasil', ...stack.map((l) => l.crumb)];
    panel.innerHTML = `
      <header class="modal-head">
        <nav class="crumbs">${crumbs.map((c, i) => i < crumbs.length - 1
          ? `<button type="button" data-depth="${i}">${esc(c)}</button><span aria-hidden="true">›</span>`
          : `<span class="here">${esc(c)}</span>`).join('')}</nav>
        <div class="modal-actions">
          ${stack.length > 1 ? '<button type="button" class="back" aria-label="Voltar">‹ Voltar</button>' : ''}
          <button type="button" class="close" aria-label="Fechar">✕</button>
        </div>
      </header>
      <div class="modal-body">${typeof top.html === 'function' ? top.html() : top.html}</div>`;
    panel.scrollTop = 0;
    panel.querySelector('.close').onclick = () => { stack.length = 0; render(); };
    panel.querySelector('.close').focus({ preventScroll: true });
    const back = panel.querySelector('.back');
    if (back) back.onclick = () => { stack.pop(); render(); };
    panel.querySelectorAll('.crumbs button').forEach((b) => { b.onclick = () => { stack.length = +b.dataset.depth; render(); }; });
    const c = top.bind?.(panel);
    if (typeof c === 'function') cleanup = c;
  };
  const push = (level) => { stack.push(level); render(); };
  layer.querySelector('.modal-backdrop').onclick = () => { stack.length = 0; render(); };
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && stack.length) { stack.pop(); render(); }
  });
  const onActivate = (el, fn) => {
    el.addEventListener('click', fn);
    el.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fn(); } });
  };

  function stateLevel(uf) {
    const mapState = { onCase: (c) => push(caseLevel(c)) };
    const withMap = window.BIH && window.BIH.has(uf);
    let v = null, r = null;
    const build = () => {
      r = period && latest ? window.BIT.resolve(period, latest) : null;
      v = window.BIP.view(uf, { r });
      if (r) v.periodHtml = window.BIT.selector(period, latest, '2019-01', 'modal-period');
    };
    const html = () => { build(); return `${window.BIP.render.renderStateModal(v, metric, { afterHead: withMap ? window.BIH.hero(uf, metric, r) : '' })}
      ${sourceLinks([
        { label: 'Receitas e despesas do estado: SICONFI (RREO)', url: 'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo' },
        { label: 'Dívida do estado: SICONFI (RGF)', url: 'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf' },
        { label: 'Arrecadação federal por estado: Receita Federal', url: 'https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv' },
        { label: 'Repasses da União: Portal da Transparência', url: 'https://portaldatransparencia.gov.br/download-de-dados/transferencias' },
        { label: 'Impostos municipais: SICONFI, RREO Anexo 3 de cada prefeitura', url: 'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo' },
        { label: 'Bandeira: Wikimedia Commons', url: 'https://commons.wikimedia.org/wiki/Category:Flags_of_states_of_Brazil' },
      ])}`; };
    return {
      crumb: stateName(uf), html,
      bind(p) {
        bindSwitch(p);
        const pp = p.querySelector('.modal-period'); if (pp) window.BIT.bind(pp.parentNode, period, latest, (np) => { period = np; if (window.__onPeriod) window.__onPeriod(np); render(); });
        p.querySelectorAll('[data-drill]').forEach((el) => onActivate(el, () => push(functionLevel(uf, v.b.spending_by_function.find((x) => x.label === el.dataset.label), v))));
        p.querySelectorAll('.cc8 .cc8-card[data-case], .case-chip').forEach((btn) => { btn.onclick = () => push(caseLevel(v.cases[+btn.dataset.case])); });
        // The state map mounts last, so its municipality panel owns the clicks on its own case cards.
        return withMap ? window.BIH.mount(p, uf, metric, v, mapState, r) : null;
      },
    };
  }

  function functionLevel(uf, fn, v) {
    const b = v && v.b ? v.b : budgets[uf];
    const pop = v ? v.pop : states.find((x) => x.uf === uf).population;
    const perPersonMonth = (x) => (v ? v.month(x) : x / pop / 12);
    const related = cases.filter((c) => c.uf === uf && c.function === fn.label);
    const fmt = (x) => (metric === 'perPerson' ? `${perMonth(perPersonMonth(x))}/mês por pessoa` : metric === 'total' ? money(x) : `R$ ${Math.round((x / fn.value) * 100)} de cada 100`);
    const html = () => `
      <div class="st-head">
        <img class="st-flag sm" src="assets/state-flags/${uf}.svg" alt="Bandeira de ${esc(stateName(uf))}">
        <div class="st-id"><h2>${esc(short(fn.label))} · ${esc(stateName(uf))}</h2>
        <p>Despesa liquidada · ${v && v.b.spendingPeriod ? v.b.spendingPeriod : b.year}: ${bi(fn.value)}, ${pct(fn.value / b.spending_total)} de tudo o que o governo estadual gastou</p></div>
        ${miniSwitch()}
      </div>
      <div class="cols one">
        <section><h3>Em que parte de ${esc(fn.label.toLowerCase())}</h3>${bars(fn.sub.slice(0, 10), { fmt })}
        <p class="note">O relatório fiscal (SICONFI) mostra a despesa por área. O detalhe por obra e por contrato vem do sistema de contratos de cada governo.</p></section>
      </div>
      ${related.length ? `<section class="cases"><h3>Obras e casos nesta área</h3><div class="case-cards">${related.map((c, i) => `
        <button type="button" class="case-card ${c.kind}" data-case="${i}">
          <span class="case-kind">${c.kind === 'obra' ? 'Obra pública' : 'Preço pago'}</span>${c.stage ? `<i class="case-stage ${esc(c.stage.kind)}">${esc(c.stage.label)}</i>` : ''}
          <strong>${esc(c.title)}</strong><span>${esc(c.teaser)}</span></button>`).join('')}</div></section>` : ''}
      ${sourceLinks([{ label: 'SICONFI, RREO Anexo 2', url: b.sources[1].url }])}`;
    return {
      crumb: fn.label, html,
      bind(p) { bindSwitch(p); p.querySelectorAll('.case-card').forEach((btn) => { btn.onclick = () => push(caseLevel(related[+btn.dataset.case])); }); },
    };
  }

  function caseLevel(c) {
    return {
      crumb: c.short || c.title, html: () => window.BIC.page(c),
      bind(p) { const cta = p.querySelector('.cta8'); if (cta) cta.onclick = () => push(compareLevel(c)); },
    };
  }

  function compareLevel(c) {
    return { crumb: 'Comparação', html: () => window.BIC.compare(c) };
  }

  // Country level (round 10): the federal government's accounts for the chosen period.
  function countryLevel() {
    const U = window.BI.series.union;
    const html = () => {
      const r = window.BIT.resolve(period, latest);
      return `<div class="bp-head"><img class="bp-flag" src="assets/flags/br.svg" alt="Bandeira do Brasil" onerror="this.style.display='none'">
          <div class="bp-id"><h2>Brasil</h2><p>As contas do governo federal · ${r.label}</p></div>
          <div data-period-modal>${window.BIT.selector(period, latest, U.months[0])}</div></div>
        ${window.BIK.mandates ? window.BIK.mandates(U, window.BI.series.public_sector_primary, r) : ''}
        ${window.BIK.uniao(U, r)}
        ${window.BIG ? window.BIG.unionSection(r) : ''}
        ${window.BIK.years(U, 'nominal_result', 'Ano a ano: sobrou ou faltou, contando os juros', 'Resultado nominal do Governo Central, soma de cada ano', r)}
        ${window.BIK.years(U, 'primary_result', 'Ano a ano, sem contar os juros', 'Resultado primário do Governo Central, soma de cada ano', r)}`;
    };
    return {
      crumb: 'Contas do Brasil', html,
      bind(p) { window.BIT.bind(p.querySelector('[data-period-modal]'), period, latest, (np) => { period = np; if (window.__onPeriod) window.__onPeriod(np); render(); }); },
    };
  }

  return {
    setPeriod: (p, l) => { period = p; latest = l; if (stack.length) render(); },
    openCountry: () => { stack.length = 0; push(countryLevel()); },
    openState: (uf, mapMetric) => { if (mapMetric) metric = FROM_MAP[mapMetric] || metric; stack.length = 0; push(stateLevel(uf)); },
    openFunction: (uf, label) => { const fn = budgets[uf].spending_by_function.find((x) => x.label === label); if (fn) push(functionLevel(uf, fn)); },
    setMetric: (m) => { metric = m; if (stack.length) render(); },
  };
}
