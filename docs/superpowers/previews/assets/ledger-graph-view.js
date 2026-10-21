// The network graph's view (D133, D134): a 3D force network (3d-force-graph) drawn from ledger-graph-model.js for the
// chosen period, with the map's colour rule, a panel per point, the checks under the stage and a light or dark ground.
// BILGV.mount(stage) returns { update(model) }; the stage is an empty element sized by CSS.
(function () {
  const NF = (d) => new Intl.NumberFormat('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const f0 = NF(0), f1 = NF(1), f2 = NF(2);
  const brl = (v) => { if (v == null) return 'sem dado'; const a = Math.abs(v), s = v < 0 ? '-' : '';
    if (a >= 1e12) return `${s}R$ ${f2.format(a / 1e12)} tri (R$ ${f1.format(a / 1e9)} bi)`; if (a >= 1e9) return `${s}R$ ${f1.format(a / 1e9)} bi`;
    if (a >= 1e6) return `${s}R$ ${f1.format(a / 1e6)} mi`; return `${s}R$ ${f0.format(a)}`; };
  const short = (v) => brl(v).split(' (')[0];
  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const sid = (x) => (x && typeof x === 'object' ? x.id : x);

  // The map's colour rule (hero3d.js, statemap.js): each side normalised by its own extreme, gamma 0.75.
  const GREEN = ['#E6E3D6', '#BFDDB8', '#7CC287', '#35A05E', '#12803F', '#06592B'], RED = ['#E6E3D6', '#F5C4B6', '#EE8D76', '#DA4A3C', '#B41E25', '#7A0710'];
  const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const lerp = (stops, x) => { const y = Math.min(Math.max(x, 0), 1) * (stops.length - 1), i = Math.min(Math.floor(y), stops.length - 2), f = y - i, a = hex(stops[i]), b = hex(stops[i + 1]);
    return '#' + a.map((v, k) => Math.round(v + (b[k] - v) * f).toString(16).padStart(2, '0')).join(''); };
  const colorFor = (v, sc) => (v == null ? '#C4CCD6' : v >= 0 ? lerp(GREEN, Math.pow(Math.min(v / sc.maxPos, 1), 0.75)) : lerp(RED, Math.pow(Math.min(-v / sc.maxNeg, 1), 0.75)));
  const scaleOf = (vs) => ({ maxPos: Math.max(...vs, 1e-9), maxNeg: Math.max(-Math.min(...vs, -1e-9), 1e-9) });

  const THEMES = {
    light: { bg: '#F3F6F9', paid: '#35A05E', back: '#DA4A3C', state: '#9AA5B1', interest: '#7B5EA7', part: '#C3CBD3', uniao: '#14202B', credores: '#7B5EA7', df: '#9AA5B1', dim: 'rgba(160,172,184,0.12)' },
    dark: { bg: '#04070C', paid: '#3CCB7F', back: '#FF6B5E', state: '#5A6878', interest: '#B48CFF', part: '#3A4656', uniao: '#F2C14E', credores: '#B48CFF', df: '#8A96A6', dim: 'rgba(90,110,140,0.10)' },
  };
  const MAJOR = new Set(['paid', 'back', 'interest']);

  function mount(stage, checkEl) {
    stage.innerHTML = `<div class="n4-graph"></div><div class="n4-labels"></div>
      <div class="n4-title"><b></b><span>A mesma regra do mapa: verde envia mais à União do que recebe, vermelho recebe mais; quanto mais forte, maior a diferença por pessoa por mês.</span><em class="n4-est" hidden></em></div>
      <div class="n4-bar">
        <span><i class="ln" style="width:46px;height:9px;background:linear-gradient(90deg,#E6E3D6,#7CC287,#12803F,#06592B)"></i>envia mais à União</span>
        <span><i class="ln" style="width:46px;height:9px;background:linear-gradient(90deg,#E6E3D6,#EE8D76,#B41E25,#7A0710)"></i>recebe mais da União</span>
        <span><i class="ln" data-lg="paid"></i>indo para a União</span><span><i class="ln" data-lg="back"></i>voltando da União</span>
        <span><i class="ln" data-lg="interest"></i>juros</span><span><i data-lg="part"></i>partes (cada imposto, o que voltou)</span>
      </div>
      <div class="n4-tools"><button type="button" class="z" data-zoom="0.65" aria-label="Aproximar">+</button><button type="button" class="z" data-zoom="1.5" aria-label="Afastar">−</button><button type="button" data-home>Ver o Brasil</button><button type="button" data-theme>Fundo escuro</button></div>
      <div class="n4-panel hide"></div><div class="n4-empty" hidden></div><div class="n4-hovertip" hidden></div>`;
    const el = stage.querySelector('.n4-graph'), layer = stage.querySelector('.n4-labels'), panel = stage.querySelector('.n4-panel'), empty = stage.querySelector('.n4-empty');
    let T = THEMES.light, D = null, byId = new Map(), hover = null, sel = null, labelled = [];
    let maxMajor = 1, maxLeafLink = 1, maxMun = 1, maxVol = 1, leafMax = {}, STATE_SCALE = null, CITY_SCALE = {};
    const setLegend = () => stage.querySelectorAll('[data-lg]').forEach((i) => { i.style.background = T[i.dataset.lg]; });

    // The clicked point keeps its links lit while its panel is open; the point under the mouse lights its own on top
    // (after the camera flies, the mouse often rests on another point, which must not hide the clicked one).
    const near = (f, n) => Boolean(f) && (n === f || f.nb.has(n.id));
    const lit = (n) => (!hover && !sel) || near(hover, n) || near(sel, n);
    const litLink = (l) => (!hover && !sel) || Boolean(hover && hover.ln.has(l)) || Boolean(sel && sel.ln.has(l));
    const entityColor = (n) => (n.kind === 'state' ? (n.color === 'none' ? T.df : colorFor(n.per_person_month, STATE_SCALE)) : colorFor(n.per_person_month, CITY_SCALE[n.state]));
    const nodeColor = (n) => (!lit(n) ? T.dim : n.kind === 'state' || n.kind === 'municipality' ? entityColor(n) : n.kind === 'uniao' ? T.uniao : n.kind === 'credores' ? T.credores : T.part);
    const baseLinkColor = (l) => ({ paid: T.paid, tax: T.paid, back: T.back, back_leaf: T.back, municipal: T.back, state: T.state, interest: T.interest }[l.kind]);
    const linkColor = (l) => (litLink(l) ? baseLinkColor(l) : T.dim);
    const linkWidth = (l) => (MAJOR.has(l.kind) ? 0.6 + 7 * l.v / maxMajor : l.kind === 'municipal' ? 0.15 + 1.6 * l.v / maxMun : 0.25 + 2.2 * l.v / maxLeafLink);
    // Read again on every colour update (a linkColor change re-runs the library's whole link update), so unlit links drop
    // their particles without this accessor being set again.
    const particles = (l) => (MAJOR.has(l.kind) && litLink(l) ? 2 + Math.round(6 * l.v / maxMajor) : 0);
    const val = (n) => (n.kind === 'uniao' ? 260 : n.kind === 'credores' ? 60 : n.kind === 'state' ? 10 + 240 * (n.sent + n.received) / maxVol
      : n.kind === 'municipality' ? 0.35 + 5 * n.v / maxMun : 0.6 + 14 * n.v / leafMax[n.kind]);

    const perPerson = (v) => `R$ ${f0.format(Math.abs(v))} a mais por pessoa, por mês`;
    const tip = (n) => {
      const U = D.union;
      if (n.kind === 'uniao') return `<div class="n4-tip"><b>União</b><br>entrou ${short(U.sent_total)} · saiu ${short(U.returned_total)}</div>`;
      if (n.kind === 'credores') return `<div class="n4-tip"><b>Credores da dívida</b><br>juros que correram: ${short(U.interest_accrual)}</div>`;
      if (n.kind === 'state') return `<div class="n4-tip"><b>${esc(n.name)}</b><br>pagou ${short(n.sent)} · recebeu ${short(n.received)}</div>`;
      if (n.kind === 'municipality') return `<div class="n4-tip"><b>${esc(n.label)} (${n.state})</b><br>pagou ${short(n.federal_revenue)} · recebeu ${short(n.received)}${n.per_person_month == null ? '' : `<br>${n.balance >= 0 ? 'envia' : 'recebe'} ${perPerson(n.per_person_month)}`}</div>`;
      return `<div class="n4-tip"><b>${esc(n.label)}</b> (${n.state})<br>${short(n.v)}</div>`;
    };
    const rows = (pairs) => `<table>${pairs.map(([a, b]) => `<tr><td>${a}</td><td>${b}</td></tr>`).join('')}</table>`;
    function panelFor(n) {
      const U = D.union;
      let h = '<button type="button" class="n4-close" data-close aria-label="Fechar">×</button>';
      if (n.kind === 'state') {
        const tag = n.color === 'none' ? '<span class="pill none">em revisão</span>' : n.balance >= 0 ? '<span class="pill in">envia mais do que recebe</span>' : '<span class="pill red">recebe mais do que envia</span>';
        h += `<h3>${esc(n.name)}</h3>${tag}${rows([['Pagou à União', brl(n.sent)], ['Recebeu da União', brl(n.received)], ['Diferença', brl(n.balance)], ['Por pessoa, por mês', `R$ ${f0.format(n.per_person_month)}`]])}`;
        h += `<h4>Impostos federais pagos no estado</h4>${rows(D.nodes.filter((x) => x.kind === 'tax' && x.state === n.label).sort((a, b) => b.v - a.v).map((t) => [esc(t.label), short(t.v)]))}`;
        h += `<h4>O que voltou ao estado</h4>${rows(D.nodes.filter((x) => x.kind === 'branch' && x.state === n.label).sort((a, b) => b.v - a.v).map((t) => [esc(t.label), short(t.v)]))}`;
        const st = D.links.filter((l) => l.kind === 'state' && (sid(l.source) === `uf:${n.label}` || sid(l.source) === `uf:${n.label}:b:gov`));
        if (st.length) h += `<h4>Dentro do estado</h4>${rows(st.map((l) => [esc(l.label), short(l.v)]))}${st[0].cover ? `<p class="src">Relatórios do estado de ${esc(st[0].cover)}.</p>` : ''}`;
        const c = D.cities[n.label];
        if (c) h += `<p class="src">O leque das prefeituras tem ${c.municipalities} prefeituras, que somam ${short(c.municipal_series)}; o total do estado é ${short(c.state_total)}. A diferença de ${short(c.gap)} é entre as duas fontes e fica anunciada até a fase 4.</p>`;
      } else if (n.kind === 'municipality') {
        const c = D.cities[n.state];
        const tag = n.balance == null ? '<span class="pill none">sem saldo no período</span>' : n.balance >= 0 ? '<span class="pill in">envia mais do que recebe</span>' : '<span class="pill red">recebe mais do que envia</span>';
        h += `<h3>${esc(n.label)} (${n.state})</h3>${tag}${rows([['Imposto federal arrecadado na cidade', brl(n.federal_revenue)], ['Recebeu da União (repasses à prefeitura, Bolsa Família, BPC)', brl(n.received)],
          ['Diferença', brl(n.balance)], ['Por pessoa, por mês', n.per_person_month == null ? 'sem dado' : `R$ ${f0.format(n.per_person_month)}`], ['População', n.population ? f0.format(n.population) : 'sem dado']])}
          <p class="src">A mesma conta do mapa da cidade, em ${esc(c.color_label)}. A ligação no leque mostra os repasses à prefeitura em ${esc(D.label)} (${short(n.v)}).</p>`;
      } else if (n.kind === 'uniao' || n.kind === 'credores') {
        const src = (U.interest_sources.accrual || []).concat(U.interest_sources.cash || []);
        h += `<h3>União</h3><span class="pill in">o Governo Central</span>${rows([['Entrou', brl(U.sent_total)], ['Saiu (repasses e gastos)', brl(U.returned_total)],
          ['dos quais para um estado', short(U.received_states)], ['saiu sem estado informado', short(U.returned_without_state)],
          ['Juros que correram, aos credores', short(U.interest_accrual)], ['Juros pagos em dinheiro', short(U.interest_cash)]])}
          <p class="src">O que saiu sem estado informado não é um ponto da rede: o dinheiro saiu da União, e o que falta é o estado, num nível mais fundo dos dados (D130).</p>
          <h4>De onde vêm os juros (livro de fluxos)</h4>${src.slice(0, 3).map((s) => `<p class="src"><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a>, ${esc(s.publisher)}. SHA-256 ${esc(s.sha256.slice(0, 16))}…, baixado em ${esc(s.fetched_at)}.</p>`).join('')}${src.length > 3 ? `<p class="src">e mais ${src.length - 3} arquivos do Tesouro, um por ano.</p>` : ''}`;
      } else {
        const st = byId.get(`uf:${n.state}`);
        h += `<h3>${esc(n.label)}</h3><span class="pill none">${n.kind === 'tax' ? 'imposto pago' : 'voltou ao estado'} · ${esc(st.name)}</span>${rows([[`Valor em ${esc(D.label)}`, brl(n.v)],
          [`Parte do que o estado ${n.kind === 'tax' ? 'pagou' : 'recebeu'}`, `${f1.format(100 * n.v / (n.kind === 'tax' ? st.sent : st.received))}%`]])}`;
      }
      panel.innerHTML = `${h}<p class="src" style="margin-top:8px">Números do mapa para ${esc(D.label)}, ainda fora do livro de fluxos e em revisão (D120).</p>`;
      panel.classList.remove('hide');
    }
    panel.addEventListener('click', (e) => { if (e.target.closest('[data-close]')) closePanel(); });

    let G;
    try { G = new ForceGraph3D(el, { controlType: 'orbit' }); } catch (e) { G = ForceGraph3D({ controlType: 'orbit' })(el); }
    const refresh = () => G.nodeColor(nodeColor).linkColor(linkColor);
    G.width(stage.clientWidth).height(stage.clientHeight).backgroundColor(T.bg).showNavInfo(false)
      .nodeRelSize(3.2).nodeVal(val).nodeColor(nodeColor).nodeOpacity(0.95).nodeResolution(14)
      .linkColor(linkColor).linkWidth(linkWidth).linkOpacity(0.55).linkCurvature((l) => (MAJOR.has(l.kind) ? 0.22 : 0.12))
      .linkDirectionalParticles(particles).linkDirectionalParticleWidth((l) => (MAJOR.has(l.kind) ? 2.4 : 1.4)).linkDirectionalParticleSpeed(0.005)
      .linkDirectionalParticleColor(baseLinkColor).warmupTicks(160).cooldownTime(9000).enableNodeDrag(false)
      .enablePointerInteraction(false); // picking is done here, in screen space (see pickAt)
    G.d3Force('charge').strength((n) => (n.kind === 'municipality' ? -6 : n.kind === 'state' || n.kind === 'uniao' ? -60 : -14));
    G.d3Force('link').distance((l) => (l.kind === 'municipal' ? 24 : l.kind === 'tax' ? 34 : l.kind === 'back_leaf' || l.kind === 'state' ? 40 : 260))
      .strength((l) => (MAJOR.has(l.kind) ? 0 : 0.7));
    // A narrow (portrait) stage sees less across, so the camera starts farther back and the whole country fits.
    const far = Math.max(1, 760 / Math.max(stage.clientWidth, 1));
    const HOME = { pos: { x: 40 * far, y: 560 * far, z: 860 * far }, look: { x: 0, y: 0, z: 70 } };
    G.cameraPosition(HOME.pos, HOME.look, 0);
    const ctl = G.controls(); ctl.autoRotate = !matchMedia('(prefers-reduced-motion: reduce)').matches; ctl.autoRotateSpeed = 0.35;
    // The camera moves, the points never do: smooth orbit, zoom toward the pointer, pan with the right button or two fingers.
    ctl.enableDamping = true; ctl.dampingFactor = 0.12; ctl.zoomToCursor = true; ctl.rotateSpeed = 0.7;
    ctl.addEventListener('start', () => { ctl.autoRotate = false; });
    el.addEventListener('pointerenter', () => { ctl.autoRotate = false; }); // a turning scene moves the point away from the mouse
    // Smoothing off for the flight: leftover drag momentum would otherwise keep turning the camera after it lands.
    const fly = (pos, look, ms) => { ctl.enableDamping = false; G.cameraPosition(pos, look, ms); setTimeout(() => { ctl.enableDamping = true; }, ms + 30); };
    function select(n) {
      sel = n; panelFor(n); refresh(); ctl.autoRotate = false;
      const d = n.kind === 'state' ? 280 : n.kind === 'uniao' ? 380 : n.kind === 'credores' ? 200 : 150; // the point and its fan in view, not filling it
      fly({ x: n.x + d * 0.35, y: n.y + d * 0.75, z: n.z + d }, { x: n.x, y: n.y, z: n.z }, 1200);
    }
    function closePanel() { sel = null; panel.classList.add('hide'); refresh(); }
    // Picking done here. The library's ray also caught the faded, nearly invisible points in front of the one under the
    // mouse, and tested every curved link on each move. Here each move tests only the points' spheres, takes the nearest
    // lit one on the line of sight, and gives small points a few pixels of slack.
    const REL = 3.2; // nodeRelSize: the library draws each point with radius cbrt(val) * REL
    function pickAt(px, py) {
      if (!D || !D.ok) return null;
      // The line of sight through the cursor pixel, tested against every point's sphere (the exact geometry, no links).
      const cam = G.camera(), o = cam.position, q = G.screen2GraphCoords(px, py, 1000), f = (el.clientHeight / 2) / Math.tan((cam.fov * Math.PI) / 360);
      let dx = q.x - o.x, dy = q.y - o.y, dz = q.z - o.z; const L = Math.hypot(dx, dy, dz); dx /= L; dy /= L; dz /= L;
      let best = null, bestLit = null, close = null;
      for (const n of D.nodes) {
        if (n.x == null) continue;
        const vx = n.x - o.x, vy = n.y - o.y, vz = n.z - o.z, tc = vx * dx + vy * dy + vz * dz;
        if (tc <= 1) continue;
        const r = Math.cbrt(val(n)) * REL, perp2 = vx * vx + vy * vy + vz * vz - tc * tc;
        // Only a real hit competes on depth; slack around a nearer point must never beat the point under the cursor.
        if (perp2 <= r * r) {
          const hit = tc - Math.sqrt(r * r - perp2);
          if (!best || hit < best.t) best = { n, t: hit };
          if (lit(n) && (!bestLit || hit < bestLit.t)) bestLit = { n, t: hit };
        } else {
          const offPx = ((Math.sqrt(perp2) - r) * f) / tc; // nothing hit: the nearest point within 6 px still counts (small points)
          if (offPx <= 6 && (!close || offPx < close.off)) close = { n, off: offPx };
        }
      }
      return (bestLit || best || close || {}).n || null;
    }
    const tipEl = stage.querySelector('.n4-hovertip');
    let ptr = null, queued = false, recolor = 0, down = null, dragging = false;
    function setHover(n) {
      if (n === hover) return;
      hover = n; el.style.cursor = n ? 'pointer' : 'grab';
      // The name shows at once; the highlight waits until the pointer rests on one point. Each highlight recolours the
      // whole scene, and doing it for every city crossed jammed the page and made the scene flash.
      clearTimeout(recolor); recolor = setTimeout(refresh, 220);
    }
    function showTip() {
      if (!hover || !ptr) { tipEl.hidden = true; return; }
      tipEl.innerHTML = tip(hover); tipEl.hidden = false;
      tipEl.style.transform = `translate(${Math.min(ptr.x + 14, el.clientWidth - tipEl.offsetWidth - 8)}px, ${ptr.y + 16}px)`;
    }
    const queuePick = () => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false;
      setHover(ptr && !dragging ? pickAt(ptr.x, ptr.y) : null); showTip(); }); };
    el.addEventListener('pointermove', (e) => { const r = el.getBoundingClientRect(); ptr = { x: e.clientX - r.left, y: e.clientY - r.top };
      if (down && Math.hypot(e.clientX - down.x, e.clientY - down.y) > 6) dragging = true; queuePick(); });
    el.addEventListener('pointerleave', () => { ptr = null; queuePick(); });
    ctl.addEventListener('change', () => { if (ptr) queuePick(); }); // the camera moved under a still mouse
    // A press and release within 6px and 700 ms opens the point that was under the mouse at the press; anything longer was
    // a camera move (the library itself cancels a click on any 1px movement while pressed).
    el.addEventListener('pointerdown', (e) => { const r = el.getBoundingClientRect(); ptr = { x: e.clientX - r.left, y: e.clientY - r.top };
      down = { x: e.clientX, y: e.clientY, t: performance.now(), node: pickAt(ptr.x, ptr.y) }; });
    el.addEventListener('pointerup', (e) => {
      const was = down; down = null; dragging = false; queuePick();
      if (!was || e.button !== 0) return;
      if (Math.hypot(e.clientX - was.x, e.clientY - was.y) > 6 || performance.now() - was.t >= 700) return;
      if (was.node) select(was.node); else closePanel();
    });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && sel) closePanel(); });
    stage.querySelectorAll('[data-zoom]').forEach((b) => { b.onclick = () => { const k = +b.dataset.zoom, c = G.camera().position, tg = ctl.target;
      ctl.autoRotate = false; fly({ x: tg.x + (c.x - tg.x) * k, y: tg.y + (c.y - tg.y) * k, z: tg.z + (c.z - tg.z) * k }, { x: tg.x, y: tg.y, z: tg.z }, 450); }; });
    stage.querySelector('[data-home]').onclick = () => { closePanel(); fly(HOME.pos, HOME.look, 1400); };
    stage.querySelector('[data-theme]').onclick = (e) => { const dark = !stage.classList.contains('dark'); stage.classList.toggle('dark', dark); T = dark ? THEMES.dark : THEMES.light;
      e.target.textContent = dark ? 'Fundo claro' : 'Fundo escuro'; G.backgroundColor(T.bg).linkDirectionalParticleColor(baseLinkColor); refresh(); setLegend(); };
    setLegend();
    new ResizeObserver(() => G.width(stage.clientWidth).height(stage.clientHeight)).observe(stage);
    // Off screen, the graph stops drawing (battery and the other 3D scene on the page).
    let onScreen = true;
    new IntersectionObserver(([e]) => { onScreen = e.isIntersecting; if (onScreen) G.resumeAnimation(); else G.pauseAnimation(); }).observe(stage);

    function place() {
      if (onScreen && document.visibilityState === 'visible' && labelled.length) {
        const cam = G.camera(), dir = cam.getWorldDirection(cam.position.clone().set(0, 0, 0));
        for (const n of labelled) { if (n.x == null) continue; const p = G.graph2ScreenCoords(n.x, n.y + 6, n.z);
          const ahead = (n.x - cam.position.x) * dir.x + (n.y - cam.position.y) * dir.y + (n.z - cam.position.z) * dir.z > 0;
          n.tag.style.opacity = ahead && lit(n) ? 1 : ahead ? 0.25 : 0; n.tag.style.transform = `translate(${(p.x - n.tag.offsetWidth / 2).toFixed(1)}px, ${(p.y - n.tag.offsetHeight - 6).toFixed(1)}px)`; }
      }
      requestAnimationFrame(place);
    }
    requestAnimationFrame(place);

    function renderChecks(m) {
      if (!checkEl) return;
      if (!m.ok) { checkEl.innerHTML = ''; return; }
      checkEl.innerHTML = `<b>Conferência de ${esc(m.label)}</b><ul>${m.checks.map((c) => `<li class="${c.ok === true ? 'ok' : c.ok === false ? 'bad' : 'na'}"><i></i>${esc(c.detail)}</li>`).join('')}</ul>`;
    }
    function update(m) {
      D = m; hover = null; sel = null; panel.classList.add('hide'); layer.innerHTML = ''; labelled = [];
      renderChecks(m);
      if (!m.ok || !m.passed) {
        empty.hidden = false; empty.textContent = m.ok ? 'Uma conferência falhou neste período; o grafo não é desenhado com números que não fecham.' : m.reason;
        stage.querySelector('.n4-title b').textContent = m.label; G.graphData({ nodes: [], links: [] }); return;
      }
      empty.hidden = true;
      byId = new Map(m.nodes.map((n) => [n.id, n]));
      for (const n of m.nodes) { n.nb = new Set(); n.ln = new Set(); }
      for (const l of m.links) { const a = byId.get(sid(l.source)), b = byId.get(sid(l.target)); a.nb.add(b.id); b.nb.add(a.id); a.ln.add(l); b.ln.add(l); }
      const states = m.nodes.filter((n) => n.kind === 'state');
      maxVol = Math.max(...states.map((n) => n.sent + n.received));
      maxMajor = Math.max(...m.links.filter((l) => MAJOR.has(l.kind)).map((l) => l.v));
      maxLeafLink = Math.max(...m.links.filter((l) => !MAJOR.has(l.kind) && l.kind !== 'municipal').map((l) => l.v));
      maxMun = Math.max(1, ...m.links.filter((l) => l.kind === 'municipal').map((l) => l.v));
      leafMax = { tax: Math.max(...m.nodes.filter((n) => n.kind === 'tax').map((n) => n.v)), branch: Math.max(...m.nodes.filter((n) => n.kind === 'branch').map((n) => n.v)), municipality: maxMun };
      STATE_SCALE = scaleOf(states.filter((n) => n.color !== 'none').map((n) => n.per_person_month)); // the DF out of the scale, as on the map
      CITY_SCALE = {};
      for (const uf of Object.keys(m.cities)) CITY_SCALE[uf] = scaleOf(m.nodes.filter((n) => n.kind === 'municipality' && n.state === uf && n.per_person_month != null).map((n) => n.per_person_month));
      const U = m.union;
      stage.querySelector('.n4-title b').textContent = U.sent_total != null ? `${m.label}: ${short(U.sent_total)} entraram na União e ${short(U.returned_total)} saíram` : `${m.label}: os 27 estados pagaram ${short(U.sent_states)} e receberam ${short(U.received_states)}`;
      const est = stage.querySelector('.n4-est');
      est.hidden = !m.estimated;
      // One line on the stage; the reason opens on click, so the note never covers the graph.
      if (m.estimated) est.innerHTML = `<details><summary>${m.estimated.months.length} ${m.estimated.months.length === 1 ? 'mês' : 'meses'} com a parte de cada estado estimada, como no mapa</summary>${esc(m.estimated.note ? m.estimated.note.text : '')}</details>`;
      G.graphData({ nodes: m.nodes, links: m.links });
      labelled = m.nodes.filter((n) => n.kind === 'state' || n.kind === 'uniao' || n.kind === 'credores' || (n.kind === 'branch' && n.id.endsWith(':b:mun') && m.cities[n.state]));
      for (const n of labelled) { const d = document.createElement('div'); d.className = 'n4-label' + (n.kind === 'uniao' ? ' uniao' : '');
        d.textContent = n.kind === 'branch' ? `Prefeituras de ${n.state}` : n.label;
        if (n.kind === 'state') d.style.color = n.color === 'none' ? '#6B7785' : n.balance >= 0 ? '#12803F' : '#B41E25';
        layer.append(d); n.tag = d; }
    }
    return { update, graph: G };
  }
  window.BILGV = { mount };
})();
