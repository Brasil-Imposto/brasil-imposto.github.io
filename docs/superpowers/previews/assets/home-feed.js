// Home side panels: "Maiores escândalos" (largest cases 2019 to 2026 by public money in an official finding, D65) on the
// left; on the right, two lists that follow the period selector (D88, D89): the largest spending moves and the largest
// income moves of the chosen period, renúncia de receita counted as spending. Classic script; reads window.BI.home =
// { moves, scandals } (data/home/*.json). Each card opens a detail sheet with every source. An item's date is the day or
// month the money moved (moved_on) or, without it, the date of its act; the card shows that date.
(function () {
  const nf = (v, d = 0) => v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const money = (v) => (v == null ? 'valor não publicado pela fonte' : Math.abs(v) >= 1e12 ? `R$ ${nf(v / 1e12, 2)} tri` : Math.abs(v) >= 1e9 ? `R$ ${nf(v / 1e9, 1)} bi` : `R$ ${nf(v / 1e6, 1)} mi`);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  const dt = (s) => (!s ? '' : s.length === 7 ? `${s.slice(5, 7)}/${s.slice(0, 4)}` : `${s.slice(8, 10)}/${s.slice(5, 7)}/${s.slice(0, 4)}`);
  const KIND = { spending: ['Gasto', 'out'], revenue_waiver: ['Renúncia de receita', 'out'], debt_renegotiation: ['Renegociação de dívidas', 'out'],
    guarantee: ['Garantia do Tesouro', 'out'], extraordinary_credit: ['Crédito extraordinário', 'out'], revenue: ['Receita', 'in'],
    revenue_loss: ['Perda de receita (estimativa do governo)', 'out'] };
  const kindOf = (k) => KIND[k] || [String(k || '').replace(/_/g, ' '), 'out'];
  const initials = (n) => n.split(/\s+/).filter((w) => w.length > 2).slice(0, 2).map((w) => w[0]).join('').toUpperCase();
  const face = (p) => (p && p.photo && p.photo.url ? `<img class="hf-face" src="${esc(p.photo.url)}" alt="${esc(p.name)}" loading="lazy">` : `<span class="hf-face hf-ini">${esc(initials((p && p.name) || '?'))}</span>`);
  const ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17h.01"/></svg>';

  const dateOf = (it) => it.moved_on || (it.act && it.act.date) || '';
  // Audit of 2026-10-06: a card dated after the latest month of the União account is not inside that account; a loan the
  // government itself classifies as financial spending is outside the primary "Despesas" line.
  const AFTER_TAG = 'Depois desta conta', FIN_TAG = 'Empréstimo: despesa financeira, fora da conta de despesas';
  const lastAccount = () => { const U = window.BI && window.BI.series && window.BI.series.union; return (U && U.latest && U.latest.revenue) || null; };
  const tagsOf = (it) => { const last = lastAccount();
    return (it.tags || []).concat(it.fiscal_nature === 'financial' ? [FIN_TAG] : [], last && dateOf(it).slice(0, 7) > last ? [AFTER_TAG] : []); };
  const tagCls = (t) => (t === 'Fora da soma' || t === AFTER_TAG ? 'off' : t === FIN_TAG ? 'fin' : '');
  const sideOf = (it) => (it.kind === 'revenue' ? 'in' : 'out');
  const MON = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
  // Covered months as words: "jul a out/2026", or one stretch per year.
  const span = (ms) => { const by = {}; for (const m of ms) (by[m.slice(0, 4)] = by[m.slice(0, 4)] || []).push(+m.slice(5, 7));
    return Object.entries(by).map(([y, a]) => (a.length === 12 ? y : `${MON[Math.min(...a) - 1]} a ${MON[Math.max(...a) - 1]}/${y}`)).join(', '); };
  // A year or a 4-year term means its whole calendar years here (moves of September count in "2026" even when the federal
  // accounts only reach August); a month means that month.
  const movesMonths = (r) => (!r ? null : r.mode === 'month' ? r.months : r.years.flatMap((y) => Array.from({ length: 12 }, (_, i) => `${y}-${String(i + 1).padStart(2, '0')}`)));
  const movesLabel = (r) => (!r ? '' : r.mode === 'month' ? r.label : r.mode === 'year' ? String(r.years[0]) : `${r.years[0]} a ${r.years[r.years.length - 1]}`);
  function sideList(H, side, r) {
    const ms = movesMonths(r), cov = (H.moves.coverage || {})[side] || [];
    const list = H.moves.items.filter((it) => sideOf(it) === side && (!ms || ms.includes(dateOf(it).slice(0, 7)))).sort((a, b) => (b.amount_brl || 0) - (a.amount_brl || 0));
    const covered = ms ? ms.filter((m) => cov.includes(m)) : cov;
    const future = ms ? ms.filter((m) => m > H.moves.as_of) : [];  // months after the latest collection are not "missing"
    const due = ms ? ms.filter((m) => !future.includes(m)) : [];
    const note = ms && !covered.length ? 'Ainda não coletado para este período.' : ms && covered.length < due.length ? `Coletado até agora: ${span(covered)}.` : '';
    const title = side === 'out' ? 'Maiores gastos do período' : 'Maiores receitas do período';
    return `<section class="hf-sec hf-${side}"><div class="hf-h"><span>${title}</span><small>${esc(movesLabel(r))}</small></div>
      ${note ? `<p class="hf-note">${esc(note)}</p>` : ''}
      <div class="hf-list">${list.map(recentCard).join('') || (covered.length ? '<p class="hf-note">Nenhum movimento com valor oficial coletado neste período.</p>' : '')}</div></section>`;
  }
  // D92, D94: the conta of the period is everything the União received and spent (Tesouro RTN; interest and the
  // official result from the Banco Central), the same numbers as "As contas do Brasil". The cards above are the
  // largest single decisions and payments; adding the cards alone left out every ordinary tax.
  function sumRow(H, r) {
    const U = window.BI.series && window.BI.series.union; if (!U || !r) return '';
    const T = window.BIT, S = (k) => T.sum(U.months, U[k], r);
    // Always in bi with one decimal, so the lines can be added by hand and close to the result (tri with two decimals
    // rounds each line by up to R$ 5 bi).
    // D95: a trillion reads as "tri"; the exact value in bi stays beside it so the lines still add up by hand.
    const bi1 = (v) => (Math.abs(v) >= 1e12 ? `R$ ${nf(v / 1e12, 2)} tri <small class="hf-exact">R$ ${nf(v / 1e9, 1)} bi</small>` : `R$ ${nf(v / 1e9, 1)} bi`);
    const rev = S('revenue'), tr = S('transfers_to_subnationals'), sp = S('primary_spending'), it = S('nominal_interest'), res = S('nominal_result'), pr = S('primary_result');
    if (rev.value == null || res.value == null) return `<div class="hf-sum"><small>As contas da União deste período ainda não foram publicadas.</small></div>`;
    const gap = res.value - (pr.value + it.value);  // Tesouro (above the line) and Banco Central (below the line) differ slightly
    const months = rev.n < rev.of ? `, ${rev.n} de ${rev.of} meses publicados` : '';
    const last = lastAccount(), after = !!last && (movesMonths(r) || []).some((m) => m > last);  // the cards of this period reach past the account
    const item = (label, v, cls, op) => `<div class="hf-line"><span class="hf-op">${op}</span><span>${label}</span><b class="${cls}">${bi1(Math.abs(v))}</b></div>`;
    return `<div class="hf-sum"><div class="hf-sum-h">A conta da União · ${esc(r.label)}${months}</div>
      <div class="hf-eq">${item('Receitas: impostos, contribuições e demais receitas (sem as financeiras)', rev.value, 'in', '')}${item('Repasses obrigatórios a estados, municípios e fundos regionais', tr.value, 'out', '−')}${item('Despesas primárias: salários, aposentadorias, saúde, educação e demais (sem juros e sem amortização da dívida)', sp.value, 'out', '−')}${item('Juros da dívida', -it.value, 'out', '−')}${Math.abs(gap) >= 5e7 ? item('Diferença entre as medições do Tesouro e do Banco Central', gap, 'muted', gap < 0 ? '−' : '+') : ''}
        <div class="hf-line hf-total"><span class="hf-op">=</span><span>Resultado: ${res.value >= 0 ? 'sobrou dinheiro' : 'faltou dinheiro'}</span><b class="${res.value >= 0 ? 'in' : 'out'}">${res.value >= 0 ? '+' : '−'}${bi1(Math.abs(res.value))}</b></div></div>
      <small>Antes dos juros: ${pr.value >= 0 ? '+' : '−'}${bi1(Math.abs(pr.value))}. Fontes: Tesouro Nacional (Resultado do Tesouro Nacional) e Banco Central; os mesmos números de "As contas do Brasil". Os cartões acima são decisões e pagamentos do período; os valores são tetos ou estimativas, salvo os marcados como pagos${after ? `, e os cartões depois de ${esc(window.BIT.fmtMonth(last))} ainda não estão nesta conta` : ''}.</small></div>`;
  }
  function recentCard(it) {
    const [kl, dir] = kindOf(it.kind); const who = (it.signed_by || [])[0];
    return `<button type="button" class="hf-card" data-hf="move:${esc(it.id)}">${face(who)}
      <span class="hf-body"><span class="hf-kind ${dir}">${esc(kl)}</span><b class="hf-title">${esc(it.short_title || it.title)}</b>
      <span class="hf-who">${who ? `${esc(who.name.split(' ').slice(0, 2).join(' '))} · ` : ''}${dt(dateOf(it))}</span>
      ${tagsOf(it).length ? `<span class="hf-tags">${tagsOf(it).map((t) => `<i class="${tagCls(t)}">${esc(t)}</i>`).join('')}</span>` : ''}</span>
      <span class="hf-amt ${dir}${it.in_total === false ? ' off' : ''}">${money(it.amount_brl)}</span></button>`;
  }
  // D92: how much came back and how much has not, where money has to come back (recovery.applies).
  const recovered = (R) => R.money_recovered_min_brl || R.money_recovered_brl || 0;
  const bi2 = (v) => (Math.abs(v) >= 1e9 ? `R$ ${nf(v / 1e9, 2)} bi` : money(v));
  function recoveryLine(R) {
    const rec = recovered(R), C = R.recovery || {};
    if (!C.applies) return 'Sem valor oficial a recuperar';
    const got = rec ? `Recuperado: ${R.money_recovered_min_brl ? 'pelo menos ' : ''}${bi2(rec)}` : 'Recuperado: nada publicado';
    return C.base_brl ? `${got} · Falta: ${bi2(C.base_brl - rec)}` : `${got} · Falta: ${esc(C.base_label || 'valor não calculado pela fonte oficial')}`;
  }
  function scandalCard(it, i) {
    const p = it.period || {};
    return `<button type="button" class="hf-card" data-hf="scandal:${i}"><span class="hf-face hf-ico">${ICON}</span>
      <span class="hf-body"><b class="hf-title">${esc(it.short_title || it.title)}</b>${it.resolution ? `<span class="hf-tags"><i class="${it.resolution.resolved ? 'ok' : 'off'}">${esc(it.resolution.tag)}</i></span><span class="hf-who">${esc(recoveryLine(it.resolution))}</span>` : ''}</span>
      <span class="hf-amt out">${it.public_money_brl == null ? '<span class="hf-na">valor não publicado</span>' : money(it.public_money_brl)}<small>${esc([p.start, p.end].filter(Boolean).map((x) => x.slice(0, 4)).filter((x, k, a) => a.indexOf(x) === k).join(' a '))}</small></span></button>`;
  }
  const src = (s) => (s && s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.body || s.document || 'fonte')}${s.date ? `, ${dt(s.date)}` : ''} ↗</a>` : '');
  function detail(kind, it) {
    if (kind === 'move') {
      const [kl] = kindOf(it.kind);
      return `<div class="hf-dh"><span class="hf-kind">${esc(kl)}</span><h3>${esc(it.title)}</h3></div>
        <p class="hf-big${it.kind === 'revenue' ? ' in' : ''}">${money(it.amount_brl)}<small>${esc({ paid: 'valor pago', expected_revenue: 'receita prevista', cap: 'teto autorizado no próprio ato (valor máximo, não valor pago)', estimated_cost: 'estimativa oficial do governo' }[it.amount_kind] || 'valor oficial')}</small></p>
        ${tagsOf(it).length ? `<p class="hf-tags big">${tagsOf(it).map((t) => `<i class="${tagCls(t)}">${esc(t)}</i>`).join('')}</p>` : ''}
        ${it.in_total === false ? `<p class="hf-offnote"><b>Fora da soma:</b> ${esc(it.not_in_total_reason || '')}</p>` : ''}
        ${it.fiscal_nature === 'financial' && it.fiscal_nature_source ? `<p class="hf-offnote"><b>${esc(FIN_TAG)}.</b> ${esc(it.fiscal_nature_source.note || '')}</p><blockquote>"${esc(it.fiscal_nature_source.quote)}"</blockquote><p class="hf-src">${src(it.fiscal_nature_source)}</p>` : ''}
        <p>${esc(it.summary)}</p>
        ${it.amount_source && it.amount_source.quote ? `<blockquote>"${esc(it.amount_source.quote)}"</blockquote><p class="hf-src">${src(it.amount_source)}</p>` : ''}
        ${(it.merged || []).length ? `<div class="hf-merged"><b>Na mesma medida</b> (contados uma vez só, neste cartão):<ul>${it.merged.map((m) => `<li>${esc(m.title)}: <b>${money(m.amount_brl)}</b>${m.moved_on || (m.act && m.act.date) ? `, ${dt(m.moved_on || m.act.date)}` : ''} ${src(m.amount_source)}</li>`).join('')}</ul></div>` : ''}
        <ul class="hf-people">${(it.signed_by || []).map((p) => `<li>${face(p)}<span><b>${esc(p.name)}</b><small>${esc(p.office || '')}</small></span></li>`).join('')}</ul>
        <p class="hf-src">${it.act ? `${esc(it.act.type)} ${esc(it.act.number || '')}, ${dt(it.act.date)} ${it.act.url ? `<a href="${esc(it.act.url)}" target="_blank" rel="noopener">${/in\.gov\.br/.test(it.act.url) ? 'Diário Oficial' : 'Fonte'} ↗</a>` : ''}` : ''}${it.status ? ` · ${esc(it.status)}` : ''}</p>`;
    }
    const R = it.resolution, rec = R && (R.money_recovered_min_brl || R.money_recovered_brl);
    const resolution = R ? `<p class="hf-tags big"><i class="${R.resolved ? 'ok' : 'off'}">${esc(R.tag)}</i></p>
      <p class="hf-offnote"><b>${esc(R.tag)}</b> (situação conferida em ${dt(R.checked_on)}): ${esc(R.why)}</p>
      ${rec ? `<p class="hf-src"><b>Recuperado até agora:</b> ${R.money_recovered_min_brl ? 'pelo menos ' : ''}${bi2(rec)}${R.money_recovered_min_note ? ` (${esc(R.money_recovered_min_note)})` : ''} ${src(R.money_recovered_source)}</p>` : '<p class="hf-src"><b>Recuperado até agora:</b> nenhum valor publicado em fonte oficial.</p>'}
      ${R.recovery ? `<p class="hf-src"><b>Ainda não recuperado:</b> ${R.recovery.applies && R.recovery.base_brl ? `${bi2(R.recovery.base_brl - (rec || 0))} (${esc(R.recovery.base_label)}${rec ? ', menos o recuperado' : ''}). ` : ''}${esc(R.recovery.note)}</p>` : ''}` : '';
    return `<div class="hf-dh"><span class="hf-kind">Escândalo</span><h3>${esc(it.title)}</h3></div>${resolution}
      <p class="hf-big">${it.public_money_brl == null ? 'Valor não publicado pela fonte' : money(it.public_money_brl)}<small>${esc(it.public_money_label || 'dinheiro público, segundo o achado oficial')}</small></p>
      ${it.private_money_brl ? `<p class="hf-big sm">${money(it.private_money_brl)}<small>dinheiro privado</small></p>` : ''}
      <p>${esc(it.summary)}</p>
      ${it.public_money_source && it.public_money_source.quote ? `<blockquote>"${esc(it.public_money_source.quote)}"</blockquote><p class="hf-src">${src(it.public_money_source)}</p>` : ''}
      ${it.status && !R ? `<p class="hf-src"><b>Situação:</b> ${esc(it.status.text)}${it.status.date ? ` (${dt(it.status.date)})` : ''} ${src(it.status)}</p>` : ''}
      ${(it.official_acts || []).length ? `<ul class="hf-acts">${it.official_acts.map((a) => `<li>${esc(a.body)}: ${esc(a.act)}${a.date ? `, ${dt(a.date)}` : ''} ${a.url ? `<a href="${esc(a.url)}" target="_blank" rel="noopener">↗</a>` : ''}</li>`).join('')}</ul>` : ''}`;
  }
  // D95: the "cake" of where the União's money goes, the same total as the account's spending
  // (transfers, primary spending and interest). D99: nothing unrelated shares a slice, every area has
  // its own color, and the list is a set of cards; a card opens the detail of that spending (month by month, the budget
  // actions inside it and, for a program, the ministries that paid). Slices from data/series/union-spending-slices.json
  // (Tesouro base), interest from the Banco Central.
  const CAKE_COLOR = { inss: '#2a78d6', health: '#e87ba4', education: '#4a3aa7', interest: '#eda100', transfers: '#5b6f86', social: '#f2a7c4',
    unemployment: '#9fc3ec', active: '#eb6834', retirees: '#f3a37d', courts: '#6d7d8c', congress: '#14202B', parties: '#8a5a00' };
  const EXTRA = ['#0f8b8d', '#7a5195', '#3d7ea6', '#f28e2b', '#9c755f', '#b07aa1', '#4e79a7', '#76b7b2', '#d4a400', '#ff9da7', '#499894',
    '#d37295', '#a0cbe8', '#ffbe7d', '#86bcb6', '#6a51a3', '#c49c94', '#8c6d31', '#5f9ed1', '#c85200', '#a3acb9', '#57606c', '#fabfd2', '#b6992d'];
  const POLITICS = new Set(['congress', 'parties']);
  const SHOW = 16;
  let cakeOpen = false, cakeState = null;
  const nfb = (v) => `R$ ${nf(v / 1e9, 2)} bi`;
  // Largest remainder: every card shows R$ bi with two decimals and the cards add up to the total shown, by hand (D94).
  function shown(list, total) {
    const unit = 1e7, target = Math.round(total / unit), base = list.map((x) => Math.floor(x.v / unit));
    let left = target - base.reduce((a, b) => a + b, 0);
    list.map((x, i) => [i, x.v / unit - base[i]]).sort((a, b) => b[1] - a[1]).forEach(([i]) => { if (left > 0) { base[i]++; left--; } });
    return { cards: base.map((u) => u * unit), total: target * unit };
  }
  function cakeData(r) {
    const C = window.BI.series && window.BI.series.union_spending_slices, U = window.BI.series && window.BI.series.union;
    if (!C || !U || !r) return null;
    const T = window.BIT, sumC = (a) => T.sum(C.months, a, r), sumU = (k) => T.sum(U.months, U[k], r);
    const color = {}; let ex = 0;
    for (const k of Object.keys(C.slices)) color[k] = CAKE_COLOR[k] || EXTRA[ex++ % EXTRA.length];
    color.interest = CAKE_COLOR.interest;
    const rows = Object.entries(C.slices).map(([k, s]) => ({ k, s, label: s.label, v: sumC(s.values).value || 0 }));
    const it = sumU('nominal_interest');
    if (it.value != null) rows.push({ k: 'interest', s: null, label: 'Juros da dívida (apropriados, líquidos; Governo Central com Banco Central, inclui swaps cambiais)', v: -it.value });
    const covered = sumC(C.base_total);
    const list = rows.filter((x) => x.v > 0).sort((a, b) => b.v - a.v), neg = rows.filter((x) => x.v < 0).sort((a, b) => a.v - b.v);
    const total = list.reduce((a, x) => a + x.v, 0);
    const ix = new Set(r.months.map((m) => C.months.indexOf(m)).filter((i) => i >= 0));
    return { C, U, r, color, list, neg, total, covered, ix, sumC, sumU };
  }
  function cake(r) {
    const D = cakeData(r); cakeState = D;
    if (!D) return '';
    if (!D.covered.n) return `<div class="hf-cake-in"><div class="hf-h"><span>Para onde vai o dinheiro da União</span></div><p class="hf-note">Ainda sem dados para este período.</p></div>`;
    const { C, U, list, neg, total, color, sumU } = D;
    const rtn = (sumU('primary_spending').value || 0) + (sumU('transfers_to_subnationals').value || 0), gap = rtn - D.covered.value;
    // Donut: largest slice first, clockwise from the top.
    let a0 = -Math.PI / 2; const R = 120, r0 = 72, cx = 130, cy = 130;
    const arcs = list.map((x) => { const a1 = a0 + (x.v / total) * Math.PI * 2, big = a1 - a0 > Math.PI ? 1 : 0;
      const p = (a, rr) => `${(cx + rr * Math.cos(a)).toFixed(2)} ${(cy + rr * Math.sin(a)).toFixed(2)}`;
      const d = `M ${p(a0, R)} A ${R} ${R} 0 ${big} 1 ${p(a1, R)} L ${p(a1, r0)} A ${r0} ${r0} 0 ${big} 0 ${p(a0, r0)} Z`; a0 = a1;
      return `<path d="${d}" fill="${color[x.k]}" data-slice="${esc(x.k)}"><title>${esc(x.label)}: ${nfb(x.v)}</title></path>`; }).join('');
    const tri = (v) => `R$ ${nf(v / 1e12, 2)} tri`;
    const S = shown(list, total);
    const share = (v) => { const p = (v / total) * 100; return p >= 0.01 ? `R$ ${nf(p, 2)}` : 'menos de R$ 0,01'; };
    const sub = (x) => (POLITICS.has(x.k) ? 'quem faz as leis e os partidos' : x.s && x.s.former ? x.s.former : x.s && x.s.group === 'ministry' ? 'sem salários de servidores'
      : x.k === 'health' || x.k === 'education' ? 'sem salários e aposentadorias de servidores'
      : x.k === 'interest' ? 'o que a dívida cresceu em juros no período, não só o que foi pago; fonte: Banco Central' : '');
    const cards = list.map((x, i) => `<button type="button" class="hf-slice${POLITICS.has(x.k) ? ' pol' : ''}${i >= SHOW ? ' extra' : ''}" data-slice="${esc(x.k)}">
        <i style="background:${color[x.k]}"></i><span class="hf-slice-t">${esc(x.label)}${sub(x) ? `<small>${esc(sub(x))}</small>` : ''}</span>
        <b>${S.cards[i] ? nfb(S.cards[i]) : 'menos de R$ 0,01 bi'}</b><em>${share(x.v)}<small>de cada R$ 100</small></em></button>`).join('');
    const pol = list.filter((x) => POLITICS.has(x.k)).reduce((a, x) => a + x.v, 0), hl = list.find((x) => x.k === 'health'), ed = list.find((x) => x.k === 'education');
    const back = neg.length ? `<p class="hf-cake-neg">Devoluções no período, fora do bolo: ${neg.map((x) => `${esc(x.label)}, ${nfb(-x.v)}`).join('; ')}. Com elas, o gasto líquido fica em ${nfb(total + neg.reduce((a, x) => a + x.v, 0))}.</p>` : '';
    return `<div class="hf-cake-in"><div class="hf-h"><span>Para onde vai o dinheiro da União</span><small>${esc(D.r.label)}</small></div>
      <p class="hf-cake-lead">De cada R$ 100 da conta da União (pagamentos e juros apropriados)${hl ? `, R$ ${nf((hl.v / total) * 100, 2)} foram para a saúde` : ''}${ed ? `, R$ ${nf((ed.v / total) * 100, 2)} para a educação, fora os salários de professores federais,` : ''} e R$ ${nf((pol / total) * 100, 2)} para a Câmara, o Senado e os partidos. Clique numa área para ver em que o dinheiro foi gasto.</p>
      <div class="hf-cake-grid"><figure><svg viewBox="0 0 260 260" role="img" aria-label="Divisão dos gastos da União">${arcs}
        <text x="130" y="122" text-anchor="middle" class="t1">${tri(S.total)}</text><text x="130" y="142" text-anchor="middle" class="t2">${nfb(S.total)}</text><text x="130" y="160" text-anchor="middle" class="t2">gastos da União</text></svg>
        <figcaption>${list.length} áreas, cada uma com a sua cor. A soma dos cartões dá ${nfb(S.total)}.</figcaption></figure>
        <div class="hf-slices${cakeOpen ? ' open' : ''}">${cards}
        ${list.length > SHOW ? `<button type="button" class="hf-slice-more" data-slice-more>${cakeOpen ? 'Mostrar só as 16 maiores' : `Mostrar as outras ${list.length - SHOW} áreas`}</button>` : ''}</div></div>
      ${back}
      <small class="hf-cake-note">${esc(C.rule)} Valores correntes, sem correção pela inflação. Total do bolo: a mesma conta acima (repasses, despesas e juros)${Math.abs(gap) >= 5e8 ? `; as duas publicações do Tesouro diferem em ${money(Math.abs(gap))} no período` : ''}. Fontes: Tesouro Nacional (Despesas e Transferências Totais da União) e Banco Central.</small></div>`;
  }
  // The detail of one slice for the chosen period: total, share, month by month (year by year for long periods), the
  // budget actions inside it and, for a program, the ministries that paid. Every list adds up to the slice.
  function sliceDetail(k) {
    const D = cakeState; if (!D) return '';
    const x = D.list.find((y) => y.k === k) || D.neg.find((y) => y.k === k); if (!x) return '';
    const { C, U, r, ix } = D, rel = window.BI.releases || {};
    const months = r.months.filter((m) => C.months.includes(m) || (k === 'interest' && U.months.includes(m)));
    const valAt = (m) => (k === 'interest' ? -(U.nominal_interest[U.months.indexOf(m)] || 0) : x.s.values[C.months.indexOf(m)] || 0);
    const byYear = months.length > 24;
    const buckets = []; for (const m of months) { const key = byYear ? m.slice(0, 4) : m; const b = buckets.find((z) => z.key === key); if (b) b.v += valAt(m); else buckets.push({ key, v: valAt(m) }); }
    const mx = Math.max(...buckets.map((b) => Math.abs(b.v)), 1);
    const lab = (key) => (byYear ? key : window.BIT.fmtMonth(key, true));
    const series = `<ol class="hf-bars">${buckets.map((b) => `<li><span>${esc(lab(b.key))}</span><i><b style="width:${Math.max(0.5, (Math.abs(b.v) / mx) * 100).toFixed(1)}%;background:${D.color[k]}"></b></i><em>${nfb(b.v)}</em></li>`).join('')}</ol>`;
    const sumSparse = (pairs) => pairs.reduce((a, [i, v]) => a + (ix.has(i) ? v : 0), 0);
    const listOf = (items, n) => {
      const rows = items.map(([code, name, pairs]) => ({ code, name, v: sumSparse(pairs) })).filter((y) => Math.abs(y.v) >= 0.005).sort((a, b) => b.v - a.v);
      const top = rows.slice(0, n), rest = rows.slice(n), restV = x.v - top.reduce((a, y) => a + y.v, 0);
      return `<ol class="hf-acts-list">${top.map((y) => `<li><span>${esc(y.name)}<small>${esc(y.code)}</small></span><b>${money2(y.v)}</b></li>`).join('')}
        ${rest.length ? `<li class="rest"><span>Mais ${rest.length} ${rest.length === 1 ? 'item' : 'itens'} desta área</span><b>${money2(restV)}</b></li>` : ''}</ol>`;
    };
    const money2 = (v) => (Math.abs(v) >= 1e9 ? nfb(v) : `R$ ${nf(v / 1e6, 2)} mi`);
    const share = (x.v / D.total) * 100;
    const src = k === 'interest'
      ? `Fonte: Banco Central do Brasil, juros nominais do Governo Central (série mensal; o Banco Central não publica data de divulgação).`
      : `Valores pagos no período, inclusive restos a pagar de anos anteriores. Fonte: Tesouro Nacional, Despesas e Transferências Totais da União (pagamentos totais), divulgado em ${rel.tesouro_base && rel.tesouro_base.date ? dt(rel.tesouro_base.date) : 'data não publicada'}. <a href="${esc(C.source.url)}" target="_blank" rel="noopener">base aberta ↗</a>`;
    return `<p class="hf-kicker">Para onde vai o dinheiro da União · ${esc(r.label)}</p>
      <h3>${esc(x.label)}</h3>${x.s && x.s.former ? `<p class="hf-src">Nome ${esc(x.s.former)}.</p>` : ''}
      <p class="hf-big out">${money2(x.v)}<small>${x.v > 0 ? `${share >= 0.01 ? `R$ ${nf(share, 2)}` : 'menos de R$ 0,01'} de cada R$ 100 gastos pela União no período` : 'devolução no período, fora do bolo'}</small></p>
      ${x.s && x.s.note ? `<p>${esc(x.s.note)}</p>` : ''}
      <h4>${byYear ? 'Ano a ano' : 'Mês a mês'}</h4>${series}<p class="hf-src">Valores correntes, sem correção pela inflação.</p>
      ${x.s ? `<h4>Em que foi gasto (ações do orçamento)</h4>${listOf(x.s.actions, 10)}` : ''}
      ${x.s && x.s.ministries && x.s.ministries.length > 1 ? `<h4>Quem pagou</h4>${listOf(x.s.ministries, 8)}` : ''}
      <p class="hf-src">${src}</p>`;
  }
  // ---------- Two sections under "Maiores escândalos" (2026-10-07) ----------
  // Largest remainder at a given unit: the parts shown add up by hand to the total shown (D94), each within one unit of its
  // exact value.
  function lr(parts, total, unit) {
    const target = Math.round(total / unit), base = parts.map((x) => Math.floor(x / unit + 1e-9));
    let left = target - base.reduce((a, b) => a + b, 0);
    parts.map((x, i) => [i, x / unit - base[i]]).sort((a, b) => b[1] - a[1]).forEach(([i]) => { if (left > 0) { base[i]++; left--; } });
    return { parts: base.map((b) => b * unit), total: target * unit };
  }
  const link = (url, label) => (url ? `<a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)} ↗</a>` : esc(label));
  // R$ with one decimal in bi; a trillion reads "tri" with the exact bi beside it (D95).
  const rb = (v) => (Math.abs(v) >= 1e12 ? `R$ ${nf(v / 1e12, 2)} tri <small class="hf-exact">R$ ${nf(v / 1e9, 1)} bi</small>` : `R$ ${nf(v / 1e9, 1)} bi`);
  const pct = (v, d = 1) => `${nf(v, d)}%`;

  // D110: "Por que falta dinheiro", six blocks answering why the União runs short. Facts from
  // data/economy/union-shortfall-explained.json (BI.shortfall). The first block reads the União account itself for January to
  // August 2026 (BI.series.union), so its lines are the ones of "A conta da União". "Cartões" reads as bank cards
  // (D110): these are "blocos", and that word never appears in this section.
  const WHY_R = { months: ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08'] };
  function whySection() {
    const SF = window.BI && window.BI.shortfall, U = window.BI && window.BI.series && window.BI.series.union;
    if (!SF || !U || !window.BIT) return '';
    const F = (k) => SF.facts[k], M = (k) => F(k).v * 1e6;  // facts in R$ milhões
    const src = (k, label) => link(F(k).url, label || F(k).body);
    const block = (n, title, sentence, body, foot) => `<article class="hw-b"><div class="hw-bh"><span class="hw-n">${n}</span><h4>${title}</h4></div>
      <p class="hw-s">${sentence}</p>${body}<p class="hw-src">${foot}</p></article>`;
    const line = (op, label, v, cls, dot) => `<div class="hf-line"><span class="hf-op">${op}</span><span>${dot ? `<i class="hw-dot ${dot}"></i>` : ''}${label}</span><b class="${cls}">${v}</b></div>`;
    const total = (label, v, cls) => `<div class="hf-line hf-total"><span class="hf-op">=</span><span>${label}</span><b class="${cls}">${v}</b></div>`;
    // 1. Interest is most of what was missing. Faltou = interest + the primary gap (Tesouro) + the measurement difference.
    const S = (k) => -(window.BIT.sum(U.months, U[k], WHY_R).value || 0);
    const it = S('nominal_interest'), res = S('nominal_result'), pr = S('primary_result'), gap = res - it - pr;
    if (gap < 0) console.error('Por que falta dinheiro: a diferença entre as medições ficou negativa; o bloco 1 supõe que ela soma');
    const T1 = lr([it, pr, Math.max(gap, 0)], res, 1e8);
    const share = (x) => (x / T1.total) * 100;
    const b1 = block(1, 'Os juros são a maior parte do que faltou',
      `De janeiro a agosto de 2026 faltaram ${rb(T1.total)} na conta da União. Desse total, ${rb(T1.parts[0])} são juros da dívida.`,
      `<div class="hw-big"><b>${nf(F('interest_share_of_nominal_deficit_2026ytd').v, 0)}%</b><span>do que faltou são juros</span></div>
      <div class="hw-stack" role="img" aria-label="Juros ${nf(share(T1.parts[0]), 0)}% do que faltou">${T1.parts.map((x, i) => `<i class="s${i + 1}" style="width:${share(x).toFixed(2)}%"></i>`).join('')}</div>
      <div class="hw-eq">${line('', 'Juros da dívida', rb(T1.parts[0]), 'out', 's1')}${line('+', 'Antes dos juros, as despesas passaram as receitas em', rb(T1.parts[1]), 'out', 's2')}${line('+', 'Diferença entre as medições do Tesouro e do Banco Central', rb(T1.parts[2]), 'muted', 's3')}
        ${total('Faltou', rb(T1.total), 'out')}</div>`,
      `Janeiro a agosto de 2026, os mesmos números de "A conta da União" acima com 2026 no seletor. Fontes: ${src('central_interest_2026ytd', 'Banco Central, estatísticas fiscais de 30/09/2026')} e ${link((U.sources && U.sources[0] && U.sources[0].page) || '', 'Tesouro Nacional, Resultado do Tesouro Nacional')}.`);
    // 2. Why interest is so large, and who holds the debt.
    const H = [['dpmfi_holder_financial_institutions_aug2026', 'Bancos e outras instituições financeiras', 'inclui os bancos públicos e o BNDES'],
      ['dpmfi_holder_pension_aug2026', 'Previdência', 'fundos de pensão, previdência privada e regimes dos servidores'],
      ['dpmfi_holder_investment_funds_aug2026', 'Fundos de investimento', 'fundos regidos pela CVM, onde pessoas e empresas aplicam'],
      ['dpmfi_holder_non_residents_aug2026', 'Investidores de fora do Brasil', 'pessoas e empresas com sede no exterior'],
      ['dpmfi_holder_others_aug2026', 'Outros', 'contas de pessoas físicas residentes, capitalização e outros'],
      ['dpmfi_holder_insurers_aug2026', 'Seguradoras', 'seguradoras e resseguradoras'],
      ['dpmfi_holder_tesouro_direto_aug2026', 'Tesouro Direto', 'pessoas que compram títulos pelo programa do Tesouro'],
      ['dpmfi_holder_government_aug2026', 'Fundos do próprio governo', 'como FAT e FGTS']]
      .map(([k, l, d]) => ({ k, l, d, v: M(k) })).sort((a, b) => b.v - a.v);
    const tot = M('dpmfi_total_aug2026'), P2 = lr(H.map((h) => (h.v / tot) * 100), 100, 0.01);
    const rates = [['Taxa Selic', 'ao ano, agosto de 2026', F('selic_annualized_aug2026').v, 'selic_annualized_aug2026', 'Banco Central'],
      ['Custo médio da dívida bruta', 'ao ano, 12 meses até agosto de 2026', F('gross_debt_implicit_rate_12m_aug2026').v, 'gross_debt_implicit_rate_12m_aug2026', 'Banco Central'],
      ['Inflação (IPCA)', 'em 12 meses até agosto de 2026', F('ipca_12m_aug2026').v, 'ipca_12m_aug2026', 'IBGE']].sort((a, b) => b[2] - a[2]);
    const rmax = rates[0][2];
    const b2 = block(2, 'Por que os juros são tão altos, e quem recebe',
      `O governo deve muito, e a maior parte da dívida paga a taxa Selic: ${pct(F('selic_annualized_aug2026').v, 2)} ao ano em agosto de 2026, com a inflação em ${pct(F('ipca_12m_aug2026').v, 2)} em 12 meses.`,
      `<div class="hw-stats"><div><b>${rb(M('gross_debt_dbgg_aug2026'))}</b><span>dívida bruta do governo geral (União, estados e municípios), ${pct(F('gross_debt_dbgg_pct_gdp_aug2026').v, 2)} do PIB, agosto de 2026</span></div>
        <div><b>${pct(F('gross_debt_selic_share_aug2026').v, 2)}</b><span>da dívida bruta acompanha a Selic</span></div></div>
      <ol class="hw-rates">${rates.map(([l, w, x]) => `<li><span>${l}<small>${w}</small></span><i><b style="width:${((x / rmax) * 100).toFixed(1)}%"></b></i><em>${pct(x, 2)}</em></li>`).join('')}</ol>
      <h5 class="hw-sub">Quem recebe os juros: de cada R$ 100 em títulos da dívida no mercado interno (${rb(tot)}, agosto de 2026)</h5>
      <ol class="hw-bars">${H.map((h, i) => `<li><span>${h.l}<small>${h.d}</small></span><i><b style="width:${((P2.parts[i] / P2.parts[0]) * 100).toFixed(1)}%"></b></i><em>R$ ${nf(P2.parts[i], 2)}</em></li>`).join('')}</ol>`,
      `Agosto de 2026. Fontes: ${src('gross_debt_dbgg_aug2026', 'Banco Central, dívida e custo')}, ${src('dpmfi_total_aug2026', 'Tesouro Nacional, Relatório Mensal da Dívida')}, ${src('selic_annualized_aug2026', 'Banco Central, Selic')} e ${src('ipca_12m_aug2026', 'IBGE, IPCA')}.`);
    // 3. Before interest: the Tesouro has a surplus, the INSS a larger deficit (Banco Central split of the Governo Federal).
    const tr = M('treasury_without_inss_primary_surplus_2026ytd'), inss = M('inss_primary_deficit_2026ytd');
    const fedGap = Math.round((inss - tr) / 1e8) * 1e8, gc = Math.round(M('central_primary_deficit_below_line_2026ytd') / 1e8) * 1e8;
    const bc = gc - fedGap;  // the Banco Central's own primary result, the remainder up to the Governo Central
    const T3 = lr([M('rgps_net_revenue_2025'), M('inss_primary_deficit_2025')], M('rgps_benefits_2025'), 1e8);
    const b3 = block(3, 'Antes dos juros: a Previdência (INSS)',
      `Sem contar os juros, o Tesouro teve sobra. A Previdência (INSS) pagou mais em aposentadorias e benefícios do que arrecadou, e essa falta foi maior que a sobra.`,
      `<div class="hw-div">
        <div class="hw-dv in"><span>Tesouro, sem a Previdência</span><i><b style="width:${((tr / inss) * 100).toFixed(1)}%"></b></i><em>sobrou ${rb(tr)}</em></div>
        <div class="hw-dv out"><span>Previdência (INSS)</span><i><b style="width:100%"></b></i><em>faltou ${rb(inss)}</em></div></div>
      <div class="hw-eq">${line('', 'Sobra do Tesouro', `+${rb(tr)}`, 'in')}${line('−', 'Falta da Previdência (INSS)', rb(inss), 'out')}${total('Faltou antes dos juros (governo federal)', rb(fedGap), 'out')}</div>
      <p class="hw-note">Em 2025 o INSS pagou ${rb(T3.total)} em benefícios e arrecadou ${rb(T3.parts[0])}: faltaram ${rb(T3.parts[1])}.</p>
      <p class="hw-fine">Divisão do Banco Central. Com o próprio Banco Central (faltou ${rb(bc)}, diferença calculada aqui), o Governo Central fica em ${rb(gc)} antes dos juros: os ${rb(T1.parts[1])} de "A conta da União" mais os ${rb(T1.parts[2])} de diferença entre as medições.</p>`,
      `Janeiro a agosto de 2026; a linha de 2025 é do ano inteiro. Fontes: ${src('inss_primary_deficit_2026ytd', 'Banco Central, estatísticas fiscais')} e ${src('rgps_benefits_2025', 'Tesouro Nacional, Resultado do Tesouro Nacional')}.`);
    if (Math.abs(Math.round((gc - T1.parts[1] - T1.parts[2]) / 1e8)) > 0) console.error('Por que falta dinheiro: o bloco 3 não fecha com o bloco 1');
    // 4. What is sold abroad pays almost no tax, by the Constitution; what the União collects from those sectors.
    const nr = M('natural_resources_revenue_2026ytd'), nrt = M('natural_resources_transfers_2026ytd'), T4 = lr([nrt, nr - nrt], nr, 1e8);
    const ie25 = F('export_tax_2025').v;  // R$ milhões
    const b4 = block(4, 'O que é vendido ao exterior quase não paga imposto',
      `A Constituição manda não cobrar IPI, ICMS e PIS/Cofins sobre o que o Brasil vende ao exterior. O dinheiro da venda é de quem vende, não do governo.`,
      `<div class="hw-stats"><div><b>R$ ${nf(ie25, 1)} milhão</b><span>de Imposto de Exportação em 2025, o ano inteiro</span></div>
        <div><b>${rb(M('export_tax_2026_jan_jul'))}</b><span>de janeiro a julho de 2026, de um imposto temporário de 12% sobre o petróleo bruto (Medida Provisória 1.340/2026)</span></div></div>
      <h5 class="hw-sub">O que a União recebe pela exploração de recursos naturais (royalties e participações do petróleo, CFEM da mineração e outras), janeiro a agosto de 2026</h5>
      <div class="hw-eq">${line('', 'Arrecadou', rb(T4.total), 'in')}${line('−', 'Repassou a estados e municípios', rb(T4.parts[0]), 'out')}${total('Ficou com a União', rb(T4.parts[1]), 'in')}</div>
      <p class="hw-note">Dividendos da Petrobras à União no mesmo período: ${rb(M('dividends_petrobras_2026ytd'))}. O único benefício do demonstrativo da Receita ligado à exportação é a contribuição previdenciária que a exportação rural não paga: ${rb(M('export_rural_tax_expenditure_2026'))} previstos para 2026.</p>${window.BIHT ? window.BIHT.whyLink : ''}`,
      `2025, janeiro a julho e janeiro a agosto de 2026. Fontes: ${link('https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm', 'Constituição, arts. 149, 153 e 155')}, ${src('export_tax_2025', 'Receita Federal, arrecadação por estado')} e ${src('natural_resources_revenue_2026ytd', 'Tesouro Nacional, Resultado do Tesouro Nacional')}.`);
    // 5. Subsidies: most of it is tax that is not collected (an estimate), not money paid.
    const TE = [['tax_expenditure_simples_2026', 'Simples Nacional', 'impostos menores para micro e pequenas empresas'],
      ['tax_expenditure_agro_2026', 'Agricultura e agroindústria', `inclui ${rb(M('tax_expenditure_basic_basket_2026'))} da cesta básica`],
      ['tax_expenditure_irpf_exempt_income_2026', 'Rendimentos isentos do imposto de renda', 'rendas que a lei deixa sem imposto'],
      ['tax_expenditure_nonprofits_2026', 'Entidades sem fins lucrativos', 'imunes ou isentas por lei'],
      ['tax_expenditure_irpf_deductions_2026', 'Deduções do imposto de renda', 'saúde, educação, dependentes e outras'],
      ['tax_expenditure_zfm_2026', 'Zona Franca de Manaus e áreas de livre comércio', '']].map(([k, l, d]) => ({ l, d, v: M(k) }));
    const teTot = M('tax_expenditure_total_2026');
    TE.push({ l: 'Demais benefícios', d: 'todos os outros itens do demonstrativo da Receita', v: teTot - TE.reduce((a, x) => a + x.v, 0) });
    TE.sort((a, b) => b.v - a.v);
    const T5 = lr(TE.map((x) => x.v), teTot, 1e8), t5max = Math.max(...T5.parts);
    const b5 = block(5, 'Subsídios: a maior parte é imposto que deixa de entrar',
      `A maior parte dos subsídios não é dinheiro pago: é imposto que a lei deixa de cobrar de algumas atividades e pessoas.`,
      `<div class="hw-stats"><div><b>${rb(T5.total)}</b><span>em benefícios tributários previstos para 2026, estimativa da Receita Federal</span></div>
        <div><b>${pct((M('subsidies_tax_2024') / M('subsidies_total_2024')) * 100, 1)}</b><span>de todos os subsídios da União em 2024 foram desse tipo</span></div></div>
      <ol class="hw-bars">${TE.map((x, i) => `<li><span>${x.l}${x.d ? `<small>${x.d}</small>` : ''}</span><i><b style="width:${((T5.parts[i] / t5max) * 100).toFixed(1)}%"></b></i><em>${rb(T5.parts[i])}</em></li>`).join('')}</ol>
      <p class="hw-note">Pagos em dinheiro de janeiro a agosto de 2026 (subsídios, subvenções e Proagro): ${rb(M('cash_subsidies_rtn_2026ytd'))}, já dentro das despesas de "A conta da União". O valor de cada benefício é uma estimativa de quanto entraria sem ele; por isso não se soma à conta.</p>`,
      `2026 (previsão para o ano), 2024 e janeiro a agosto de 2026. Fontes: ${src('tax_expenditure_total_2026', 'Receita Federal, Demonstrativo dos Gastos Tributários 2026')}, ${src('subsidies_total_2024', 'Ministério do Planejamento, Orçamento de Subsídios da União 2024')} e ${src('cash_subsidies_rtn_2026ytd', 'Tesouro Nacional')}.`);
    // 6. The order of magnitude: every tax paid in the country in 2025, by who collects it.
    const L6 = [['Governo Central', M('tax_burden_central_2025'), 'g1'], ['Estados', M('tax_burden_states_2025'), 'g2'], ['Municípios', M('tax_burden_municipalities_2025'), 'g3']];
    const T6 = lr(L6.map((x) => x[1]), M('tax_burden_total_2025'), 1e8);
    const b6 = block(6, 'O tamanho de cada parte',
      `Em 2025 o país pagou ${rb(T6.total)} em tributos, ${pct(F('tax_burden_pct_gdp_2025').v, 1)} do PIB. ${pct(F('central_share_of_tax_burden_2025').v, 1)} disso ficou com o Governo Central, que passa uma parte a estados e municípios.`,
      `<div class="hw-stack" role="img" aria-label="Tributos de 2025 por quem arrecada">${L6.map((x, i) => `<i class="${x[2]}" style="width:${((T6.parts[i] / T6.total) * 100).toFixed(2)}%"></i>`).join('')}</div>
      <div class="hw-eq">${L6.map((x, i) => line(i ? '+' : '', x[0], rb(T6.parts[i]), '', x[2])).join('')}${total('Todos os tributos do país', rb(T6.total), '')}</div>
      <p class="hw-note">Do que arrecadou, o Governo Central passou ${rb(M('revenue_sharing_transfers_2025'))} a estados e municípios, como o FPE e o FPM. Os juros dele no ano foram ${rb(M('central_interest_2025'))}, o mesmo que ${pct((M('central_interest_2025') / M('tax_burden_central_2025')) * 100, 1)} dos tributos que ele arrecadou.</p>`,
      `2025, o ano inteiro. Fontes: ${src('tax_burden_total_2025', 'Tesouro Nacional, carga tributária de 2025')}, ${src('revenue_sharing_transfers_2025', 'Tesouro Nacional, Resultado do Tesouro Nacional')} e ${src('central_interest_2025', 'Banco Central')}.`);
    return `<div class="hw-in"><div class="hf-h"><span>Por que falta dinheiro</span><small>janeiro a agosto de 2026</small></div>
      <p class="hw-lead">Pagamos muito imposto e o Brasil vende muito ao exterior. Por que ainda falta dinheiro na conta da União? Seis respostas, com os números oficiais.</p>
      <p class="hw-per">Período: janeiro a agosto de 2026, o mesmo de "A conta da União" com 2026 no seletor. Quando um número é de outro ano, o bloco diz qual.</p>
      <div class="hw-grid">${b1}${b2}${b3}${b4}${b5}${b6}</div></div>`;
  }

  // D159: "Por que falta dinheiro" goes right under "Para onde vai o dinheiro da União", once. "O que o Brasil vende" (D109)
  // follows it only where the trade switch builds it: its code and style are assets/home-trade.js and home-trade.css, which
  // only the staging build loads (data/features.json), so the production page carries none of it.
  function mountSections() {
    if (document.querySelector('[data-why]')) return;
    const strip = document.getElementById('recentes-e-escandalos'), cake = document.querySelector('[data-cake]');
    if (!strip && !cake) return;
    const mk = (id, cls, key, label) => { const s = document.createElement('section'); s.id = id; s.className = cls; s.setAttribute(key, ''); s.setAttribute('aria-label', label); return s; };
    const why = mk('por-que-falta-dinheiro', 'hw', 'data-why', 'Por que falta dinheiro');
    const trade = window.BIHT ? window.BIHT.section(mk) : null;
    const parts = trade ? [why, trade] : [why];
    if (cake) cake.after(...parts); else strip.after(...parts);
    why.innerHTML = whySection(); why.hidden = !why.innerHTML;
    if (trade) window.BIHT.draw(trade);
  }
  // r: the period chosen in the selector (periods.js); both money lists follow it.
  function render(root, r) {
    mountSections();
    const ck = document.querySelector('[data-cake]'); if (ck) ck.innerHTML = cake(r);
    const H = window.BI && window.BI.home; if (!H) return;
    const right = root.querySelector('[data-recent]'), left = root.querySelector('[data-scandals]');
    const S = (H.scandals && H.scandals.items) || [], M = H.moves && H.moves.items ? H.moves.items : [];
    if (right) right.innerHTML = M.length ? `<div class="hf-cols">${sideList(H, 'out', r)}${sideList(H, 'in', r)}</div>${sumRow(H, r)}` : '';
    if (left) left.innerHTML = S.length ? `<div class="hf-h"><span>Maiores escândalos</span><small>2019 a 2026, por dinheiro público</small></div><div class="hf-list">${S.map(scandalCard).join('')}</div>` : '';
    right && right.toggleAttribute('hidden', !M.length); left && left.toggleAttribute('hidden', !S.length);
    let sheet = document.querySelector('.hf-sheet');
    if (!sheet) {
      sheet = document.createElement('div'); sheet.className = 'hf-sheet'; sheet.hidden = true;
      sheet.innerHTML = '<div class="hf-back" data-hf-close></div><div class="hf-panel" role="dialog" aria-modal="true"><button type="button" class="hf-x" data-hf-close aria-label="Fechar">✕</button><div class="hf-content"></div></div>';
      document.body.appendChild(sheet);
      // the page behind does not scroll while the sheet is open; focus goes to its close button and back to what opened it
      sheet.show = (html) => {
        sheet.querySelector('.hf-content').innerHTML = html;
        if (sheet.hidden) sheet.opener = document.activeElement;
        sheet.hidden = false; document.documentElement.classList.add('bi-locked');
        sheet.querySelector('.hf-x').focus({ preventScroll: true });
      };
      sheet.hide = () => {
        if (sheet.hidden) return;
        sheet.hidden = true; document.documentElement.classList.remove('bi-locked');
        if (sheet.opener && sheet.opener.isConnected) sheet.opener.focus({ preventScroll: true });
        sheet.opener = null;
      };
      sheet.querySelectorAll('[data-hf-close]').forEach((b) => (b.onclick = () => sheet.hide()));
      document.addEventListener('keydown', (e) => { if (e.key === 'Escape') sheet.hide(); });
    }
    root.querySelectorAll('[data-hf]').forEach((b) => (b.onclick = () => {
      const [k, i] = b.dataset.hf.split(/:(.*)/); const it = k === 'move' ? M.find((x) => x.id === i) : S[+i];
      sheet.show(detail(k, it));
    }));
    if (ck) {
      ck.querySelectorAll('[data-slice]').forEach((b) => (b.onclick = () => sheet.show(sliceDetail(b.dataset.slice))));
      const more = ck.querySelector('[data-slice-more]');
      if (more) more.onclick = () => { cakeOpen = !cakeOpen; ck.innerHTML = cake(r); render(root, r); };
    }
  }
  // nf, esc, dt, pct and link also serve assets/home-trade.js (staging), which loads right after this file.
  window.BIHF = { render, nf, esc, dt, pct, link };
})();
