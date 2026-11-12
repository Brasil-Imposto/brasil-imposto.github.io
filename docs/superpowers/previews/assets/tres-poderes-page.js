// Os 3 Poderes: the page. A file, not inline code: the site's CSP refuses inline scripts (spec seguranca-doacoes, section 8).
(function () {
  const D = window.TP3, P = D.positions, byId = Object.fromEntries(P.map((p) => [p.id, p]));
  const PEOPLE = D.people, person = Object.fromEntries(PEOPLE.map((x) => [x.id, x]));
  const R = D.rules, AVG = D.avg_months;
  const nf = (v, d = 2) => v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
  const brl = (v) => `R$ ${nf(v)}`;
  const int = (v) => v.toLocaleString('pt-BR');
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const plain = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase();
  const MON = ['', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
  const MONTHS = ['', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
  const HOUSE = { camara: 'Câmara', senado: 'Senado', executivo: 'Executivo', judiciario: 'Judiciário' };
  const HOUSE_FULL = { camara: 'Câmara dos Deputados', senado: 'Senado Federal', executivo: 'Poder Executivo', judiciario: 'Poder Judiciário' };
  const PARL = (x) => x.house === 'camara' || x.house === 'senado';
  const place = (x) => (x.house === 'judiciario' ? x.court : x.house === 'executivo' ? 'Executivo' : HOUSE[x.house]);
  const POWER = { 'Executivo': 'var(--exe)', 'Legislativo': 'var(--leg)', 'Judiciário': 'var(--jud)' };
  const SIL = '<svg viewBox="0 0 40 46" aria-hidden="true"><circle cx="20" cy="15" r="9" fill="#5B6773"/><path d="M2 46c0-11 8-17 18-17s18 6 18 17z" fill="#5B6773"/></svg>';
  const ph = (x, lazy) => `<span class="ph">${SIL}${x && x.photo ? `<img src="${esc(x.photo)}" alt="" ${lazy ? 'loading="lazy"' : ''} data-fallback="remove">` : ''}</span>`;
  const flag = (uf) => `<span class="uf"><img src="assets/state-flags/${esc(uf)}.svg" alt="">${esc(uf)}</span>`;
  const mark = (s) => `<i class="st ${s}" aria-label="${s === 'yes' ? 'usa' : s === 'no' ? 'não usa' : s === 'info' ? 'informação' : s === 'zero' ? 'sem valor na folha publicada' : 'não publicado'}">${s === 'yes' ? '✓' : s === 'no' ? '✗' : s === 'info' ? 'i' : s === 'zero' ? '0' : '?'}</i>`;
  const status = (v) => (v === true ? 'yes' : v === false ? 'no' : 'unknown');

  // ---------- a minister or judge: each component the institution publishes, as published (a negative is a discount)
  function genericModel(x) {
    const rows = x.items.map((it) => {
      if (it.info) {  // shown for context, never summed (net pay, the presidency's card, a discount)
        const has = it.monthly != null && it.monthly !== 0;
        return { k: it.key, label: it.label, s: 'info', v: has ? `<span>${brl(it.monthly)}</span><small>por mês</small>` : '', m: 0, own: it.own,
                 nt: [(it.note || '').split('. ')[0], has ? 'não entra no total' : ''].filter(Boolean).join('; '), src: it.source };
      }
      const s = it.state === 'zero_payroll' ? 'zero' : it.uses === true || (it.monthly || 0) < 0 ? (it.monthly < 0 ? 'no' : 'yes') : it.uses === false ? 'no' : 'unknown';
      const v = it.monthly ? `<span>${it.monthly < 0 ? '−' : ''}${brl(Math.abs(it.monthly))}</span><small>por mês</small>` : s === 'zero' ? 'sem valor na folha publicada' : s === 'no' ? 'não recebe' : s === 'yes' ? 'sem valor publicado' : '';
      const nt = it.monthly ? [it.year_total != null ? `${brl(it.year_total)} em 2026` : '', it.months ? `média de ${it.months}` : ''].filter(Boolean).join(', ')
        : s === 'unknown' ? (it.note || '').split('. ')[0] : '';
      return { k: it.key, label: it.label, s, v, m: it.monthly || 0, own: it.own, nt, chip: 'não publicado', src: it.source, block: it.block || null };
    });
    const total = rows.reduce((a, r) => a + r.m, 0), own = rows.filter((r) => r.own).reduce((a, r) => a + r.m, 0);
    return { rows, total, own, partial: rows.some((r) => r.s === 'unknown'), generic: true, totalLabel: x.total_label || null, totalNote: x.total_note || null, tseMonths: x.tse_months || null };
  }

  // ---------- one parliamentarian: salary and each allowance, with what is used and the monthly total
  function model(x) {
    if (!PARL(x)) return genericModel(x);
    const cam = x.house === 'camara', rows = [], last = AVG[x.house];
    const period = x.avg_months ? `média de ${x.avg_months < last ? MONTHS[last - x.avg_months + 1] : 'janeiro'} a ${MONTHS[last]}` : '';
    rows.push({ k: 'salary', label: 'Salário', s: 'yes', v: brl(x.salary), m: x.salary, own: true, nt: cam ? 'bruto, todo mês' : 'valor do cargo, todo mês' });
    const hv = cam ? R.housing_camara : R.housing_senado, hs = status(x.housing.uses);
    rows.push({ k: 'housing', label: 'Auxílio-moradia', s: hs, v: hs === 'yes' ? brl(hv) : hs === 'no' ? 'não recebe' : '', m: hs === 'yes' ? hv : 0, own: true,
                nt: hs === 'yes' ? (x.housing.received ? `recebeu ${brl(x.housing.received)} em 2026` : 'por mês') : '' });
    // the housing complement is paid out of the cota and the Câmara counts it there; it is housing for the person, so it
    // gets its own row on the person's side and leaves the cota row (the total does not change)
    const hc = x.housing_complement, hcAvg = hc && hc.avg ? hc.avg : 0;
    if (hc) rows.push({ k: 'housing_complement', label: 'Complementação do auxílio-moradia', s: 'yes', v: `<span>${brl(hcAvg)}</span><small>por mês</small>`, m: hcAvg, own: true,
                        nt: `paga pela cota: ${brl(hc.year_total)} em 2026; ${period}` });
    const fs = status(x.flat.uses);
    const past = fs === 'yes' && x.flat.now === false;
    rows.push({ k: 'flat', label: 'Imóvel funcional', s: fs, v: fs === 'yes' ? (past ? 'usou' : 'usa') : fs === 'no' ? 'não usa' : '', m: 0,
                nt: fs === 'yes' ? `${past ? 'até ' + x.flat.until + '; ' : x.flat.since ? 'desde ' + x.flat.since + '; ' : ''}sem valor em reais publicado` : '' });
    const c = x.ceap;
    if (c && c.used > 0 && c.avg == null) rows.push({ k: 'ceap', label: cam ? 'Cota parlamentar' : 'Cota (CEAPS)', s: 'yes', v: `<span>${brl(c.used)}</span><small>em 2026</small>`, m: 0, own: false, noavg: true,
                nt: `sem média por mês: os registros começam depois de ${MONTHS[last]}` });
    else if (c && c.used > 0) rows.push({ k: 'ceap', label: cam ? 'Cota parlamentar' : 'Cota (CEAPS)', s: 'yes', v: `<span>${brl(c.avg - hcAvg)}</span><small>por mês</small>`, m: c.avg - hcAvg, own: false,
                nt: `usou ${brl(c.used)} em 2026${cam ? ` (${nf(c.pct, 1)}% do que podia no ano)` : `, lançado até ${x.updated} (${nf(c.pct, 1)}% do limite do ano)`}${hc ? `, incluindo ${brl(hc.year_total)} da complementação da moradia, mostrada na linha própria` : ''}; ${period}` });
    else rows.push({ k: 'ceap', label: cam ? 'Cota parlamentar' : 'Cota (CEAPS)', s: c && c.used === 0 ? 'no' : 'unknown', v: c && c.used === 0 ? 'não usou' : '', m: 0,
                nt: c ? `${x.exercise_since && x.exercise_since >= '2026-01-01' ? `em exercício desde ${dmy(x.exercise_since)}; ` : ''}nenhum gasto registrado em 2026 até agora` : 'nenhum lançamento no arquivo de 2026' });
    const o = x.office;
    if (o && o.kind === 'staff') {
      if (o.avg != null) rows.push({ k: 'office', label: 'Equipe do gabinete', s: 'yes', v: `<span>${brl(o.avg)}</span><small>por mês</small>`, m: o.avg, own: false,
                nt: `salários brutos de ${int(o.staff)} pessoas do gabinete e dos escritórios, média de ${o.months_label}; inclui servidores de carreira (na Câmara, a verba de gabinete paga só os secretários parlamentares)` });
      else rows.push({ k: 'office', label: 'Equipe do gabinete', s: 'info', chip: 'sem mês inteiro', v: '', m: 0, noavg: true, nt: `${int(o.staff)} pessoas na equipe; ${o.none_reason}` });
    } else if (o && o.used > 0 && o.avg == null) rows.push({ k: 'office', label: 'Verba de gabinete', s: 'yes', v: `<span>${brl(o.used)}</span><small>em 2026</small>`, m: 0, own: false, noavg: true,
                nt: `sem média por mês: os registros começam depois de ${MONTHS[last]}` });
    else if (o && o.used > 0) rows.push({ k: 'office', label: 'Verba de gabinete', s: 'yes', v: `<span>${brl(o.avg)}</span><small>por mês</small>`, m: o.avg, own: false,
                nt: `usou ${brl(o.used)} em 2026 (${nf(o.pct, 1)}% do que podia) para pagar a equipe; ${period}` });
    else rows.push({ k: 'office', label: 'Verba de gabinete', s: o && o.used === 0 ? 'no' : 'unknown', v: o && o.used === 0 ? 'não usou' : '', m: 0,
                nt: o ? `nenhum gasto registrado em 2026 até ${MONTHS[last]}` : 'sem registro no arquivo do Senado' });
    const total = rows.reduce((a, r) => a + r.m, 0), own = rows.filter((r) => r.own).reduce((a, r) => a + r.m, 0);
    return { rows, total, own, partial: rows.some((r) => (r.s === 'unknown' && r.k !== 'flat') || r.noavg) };
  }
  function dmy(d) { return d ? d.split('-').reverse().join('/') : ''; }
  const rowHTML = (r, notes = true) => `<div class="r person${r.s === 'no' || r.s === 'zero' ? ' off' : ''}"><span class="lb">${esc(r.label)}</span><span class="vl">${r.s === 'unknown' ? `<span class="chip">${esc(r.chip || 'não publicado')}</span>` : r.v}</span>${mark(r.s)}${notes && r.nt ? `<span class="nt">${esc(r.nt)}</span>` : ''}</div>`;
  const splitHTML = (M) => {
    if (M.total - M.own < 0.005) return '';  // nothing pays an office: the whole total goes to the person
    const a = M.total ? (M.own / M.total) * 100 : 100;
    return `<div class="split" aria-hidden="true"><i class="own" style="width:${a}%"></i><i class="mand" style="width:${100 - a}%"></i></div>`
      + `<div class="split-lg"><span><i class="own"></i>para a pessoa <b>${brl(M.own)}</b></span><span><i class="mand"></i>mandato e equipe <b>${brl(M.total - M.own)}</b></span></div>`;
  };
  const totHTML = (M, label = 'Total por mês') => `<div class="tot"><span>${esc(M.totalLabel || label)}</span><b>${brl(M.total)}</b></div>${M.totalNote ? `<div class="tnote">${esc(M.totalNote)}</div>` : ''}${M.partial ? '<div class="tnote"><span class="chip">parcial</span> falta parte do dado; nunca uma estimativa</div>' : ''}${splitHTML(M)}`;

  // ---------- bills: the outcome of each one, as the shared rules classify it (bill_outcomes.py)
  const OUTC = { law: ['Virou lei', 'law'], approved: ['Aprovado, ainda sem lei', 'ok'], approved_with_another_bill: ['Aprovado junto com outro projeto', 'ok'],
    in_progress: ['Em tramitação', 'prog'], archived_end_of_term: ['Arquivado no fim do mandato', 'stop'], archived_reason_not_stated: ['Arquivado', 'stop'],
    prejudged: ['Prejudicado', 'stop'], withdrawn: ['Retirado pelo autor', 'stop'], returned_to_author: ['Devolvido ao autor', 'stop'],
    rejected: ['Rejeitado', 'no'], vetoed: ['Vetado', 'no'], status_not_published: ['Situação não publicada', 'unk'] };
  const ORDER = Object.keys(OUTC);
  const billKey = (b) => (b.law ? 'law' : b.o);
  // per role counts by display key, from the summary built with the data (laws are a subset of "approved")
  const billCounts = (x, role) => { const s = x.bills && x.bills[role]; if (!s) return null; const c = Object.assign({}, s.counts); return c; };
  const barHTML = (c) => { const n = ORDER.reduce((a, k) => a + (c[k] || 0), 0); return n ? `<div class="bl-bar" aria-hidden="true">${ORDER.filter((k) => c[k]).map((k) => `<i class="o-${OUTC[k][1]}" style="width:${(c[k] / n) * 100}%"></i>`).join('')}</div>` : ''; };
  function billsLine(x) {
    const c = billCounts(x, 'main'); if (!c) return '';
    const n = ORDER.reduce((a, k) => a + (c[k] || 0), 0), co = billCounts(x, 'co'), nco = co ? ORDER.reduce((a, k) => a + (co[k] || 0), 0) : 0;
    const ok = (c.approved || 0) + (c.approved_with_another_bill || 0);
    return `<div class="r"><span class="lb">Projetos como autor principal</span><span class="vl">${int(n)}</span>`
      + `<span class="nt">${int(c.law || 0)} viraram lei · ${int(ok)} aprovados ainda sem lei · ${int(c.in_progress || 0)} em tramitação · ${int((c.rejected || 0) + (c.vetoed || 0))} rejeitados ou vetados${nco ? ` · coautor de mais ${int(nco)}` : ''}</span></div>${barHTML(c)}`;
  }
  const loaded = {};
  function loadBills(id) {
    if (window.TP3B && window.TP3B[id]) return Promise.resolve(window.TP3B[id]);
    if (loaded[id]) return loaded[id];
    return (loaded[id] = new Promise((ok, fail) => { const s = document.createElement('script'); s.src = `assets/tres-poderes-bills/${id.replace(':', '-')}.js`;
      s.onload = () => ok((window.TP3B || {})[id] || []); s.onerror = () => fail(new Error('bills not found')); document.head.appendChild(s); }));
  }
  const billLink = (x, b) => (x.house === 'camara' ? `https://www.camara.leg.br/propostas-legislativas/${b.id}` : `https://www25.senado.leg.br/web/atividade/materias/-/materia/${b.id}`);
  function billsSection(x) {
    const st = { role: 'main', key: '', q: '', shown: 20 }, box = document.createElement('div'); box.className = 'box bills'; box.dataset.bills = x.id;
    box.innerHTML = `<div class="head2"><h3>Projetos apresentados</h3><div class="mini-switch" role="group" aria-label="Autoria"><button type="button" data-role="main" aria-pressed="true">Autor principal</button><button type="button" data-role="co" aria-pressed="false">Coautor</button></div></div><div data-bl>Carregando os projetos...</div>`;
    loadBills(x.id).then((all) => {
      const body = box.querySelector('[data-bl]');
      const draw = () => {
        const mine = all.filter((b) => b.r === (st.role === 'main' ? 'm' : 'c')), c = {};
        mine.forEach((b) => { c[billKey(b)] = (c[billKey(b)] || 0) + 1; });
        const q = plain(st.q).trim(), hit = mine.filter((b) => (!st.key || billKey(b) === st.key) && (!q || plain(`${b.t} ${b.n}/${b.y} ${b.e}`).includes(q)));
        const years = all.map((b) => +b.y).filter(Boolean), span = years.length ? `${Math.min(...years)}${Math.max(...years) > Math.min(...years) ? ` a ${Math.max(...years)}` : ''}` : '';
        body.innerHTML = `<div class="bl-sum"><span><b>${int(mine.length)}</b> ${st.role === 'main' ? 'como autor principal' : 'como coautor'}</span><span>${x.house === 'camara' ? 'na Câmara' : 'no Senado'}${span ? `, de ${span}` : ''}</span></div>${barHTML(c)}`
          + `<div class="bl-filters">${ORDER.filter((k) => c[k]).map((k) => `<button type="button" class="o-${OUTC[k][1]}" data-okey="${k}" aria-pressed="${st.key === k}"><i></i>${OUTC[k][0]} ${int(c[k])}</button>`).join('')}</div>`
          + `<input class="bl-q" type="search" data-blq placeholder="Buscar no texto dos projetos" value="${esc(st.q)}">`
          + `<ul class="bl-list">${hit.slice(0, st.shown).map((b) => { const k = billKey(b), cls = OUTC[k] ? OUTC[k][1] : 'stop';
              return `<li class="o-${cls}"><div class="bl-top"><span><b>${esc(b.t)} ${esc(b.n)}/${esc(b.y)}</b><span class="bl-pill">${esc(OUTC[k] ? OUTC[k][0] : b.o)}</span></span><time>apresentado em ${dmy(b.d)}</time></div>`
              + `<p class="bl-e" data-clamp>${esc(b.e) || 'Sem ementa publicada.'}</p>`
              + `<p class="bl-st">Última situação${b.u ? ` (${dmy(b.u)})` : ''}: ${esc(b.s || 'não publicada')}${b.norma ? ` · ${esc(b.norma)}` : ''}${b.tr && b.tr !== b.s ? ` · ${esc(b.tr)}` : ''} · <a href="${billLink(x, b)}" target="_blank" rel="noopener">ver no site ${x.house === 'camara' ? 'da Câmara' : 'do Senado'} ↗</a></p></li>`; }).join('')}</ul>`
          + (hit.length > st.shown ? `<div class="bl-more"><button class="btn" type="button" data-blmore>Mostrar mais 20 de ${int(hit.length - st.shown)}</button></div>` : '')
          + (hit.length ? '' : '<div class="bl-note">Nenhum projeto com esse filtro.</div>')
          + `<div class="bl-note">Projetos de lei, de lei complementar, de emenda à Constituição e de decreto legislativo (PL, PLP, PEC, PDL e os códigos antigos PDC, PLS e PDS). A situação é a última publicada pela ${x.house === 'camara' ? 'Câmara' : 'Senado'}; "aprovado, ainda sem lei" inclui projeto aprovado numa Casa e parado na outra.</div>`;
      };
      box.addEventListener('click', (e) => {
        const r = e.target.closest('[data-role]'); if (r) { st.role = r.dataset.role; st.key = ''; st.shown = 20; box.querySelectorAll('[data-role]').forEach((b) => b.setAttribute('aria-pressed', String(b === r))); draw(); return; }
        const k = e.target.closest('[data-okey]'); if (k) { st.key = st.key === k.dataset.okey ? '' : k.dataset.okey; st.shown = 20; draw(); return; }
        if (e.target.closest('[data-blmore]')) { st.shown += 20; draw(); return; }
        const cl = e.target.closest('[data-clamp]'); if (cl) cl.classList.toggle('open');
      });
      box.addEventListener('input', (e) => { if (e.target.matches('[data-blq]')) { st.q = e.target.value; st.shown = 20; const pos = e.target.selectionStart; draw(); const i = box.querySelector('[data-blq]'); i.focus(); i.setSelectionRange(pos, pos); } });
      draw();
    }, () => { box.querySelector('[data-bl]').innerHTML = '<div class="bl-note"><span class="chip">indisponível</span> os projetos desta pessoa não abriram; recarregue a página</div>'; });
    return box;
  }

  // ---------- the tree
  let mode = 'cargo';
  function cargoRows(p) {
    let total = 0, partial = false;
    const rows = (p.items || []).map((it) => {
      let v = '';
      if (it.value != null) {
        v = it.value_min != null ? `<span>${brl(it.value_min)}</span><span>a ${brl(it.value)}</span>` : brl(it.value);
        if (it.monthly !== false) total += it.value;
      } else if (it.todo) { v = '<span class="chip">não publicado</span>'; partial = true; }
      else v = '<span style="color:var(--faint);font-weight:600">sem valor</span>';
      const note = [it.note, it.law].filter(Boolean).join(' · ');
      return `<div class="r"><span class="lb">${esc(it.label)}</span><span class="vl">${v}</span>${note ? `<span class="nt">${esc(note)}</span>` : ''}</div>`;
    }).join('');
    const ceil = (p.items || []).some((it) => it.value_min != null || it.cap);
    return `<div class="rows">${rows}</div><div class="tot"><span>${(p.count || 1) > 1 ? 'Por pessoa, por mês' : 'Total do cargo por mês'}</span><b>${ceil ? 'até ' : ''}${brl(total)}</b></div>`
      + `<div class="tnote">${partial ? '<span class="chip">parcial</span> ' : ''}${ceil ? ((p.items || []).some((it) => it.cap) ? 'Com o teto de cada auxílio. ' : 'Com a cota do estado de valor mais alto. ') : ''}${(p.items || []).some((it) => it.monthly === false) ? 'Sem a ajuda de custo, paga só no início e no fim do mandato.' : ''}</div>`;
  }
  // people of the Executive and the STF come from the positions file (no directory for them yet)
  function otherPersonRows(p, x) {
    const I = x.items; let total = 0, partial = false;
    const rows = (p.items || []).map((it) => {
      if (it.monthly === false) return '';
      const u = I[it.key], s = (u && (u.status || u)) || 'unknown'; let v = '';
      if (it.key === 'salary') { v = brl(it.value); total += it.value; }
      else if (it.key === 'residence' || it.key === 'flat') v = s === 'yes' ? 'usa' : s === 'no' ? 'não usa' : '';
      if (s === 'unknown') partial = true;
      return rowHTML({ label: it.label, s, v, nt: it.key === 'residence' && s === 'yes' ? 'residência oficial, sem valor em reais publicado' : '' });
    }).join('');
    return `<div class="rows">${rows}</div><div class="tot"><span>Total que usa por mês</span><b>${brl(total)}</b></div>${partial ? '<div class="tnote"><span class="chip">parcial</span> falta parte do dado</div>' : ''}`;
  }
  // ---------- public spending tied to the President's post and to his spouse (never personal income)
  const COST_SHORT = { trips_entourage: 'Viagens da equipe que acompanha, prepara e protege as viagens dele', cpgf_president_units: 'Cartão corporativo das unidades que o atendem',
    trips_support: 'Viagens da equipe que apoia a agenda dela' };
  const costValue = (c) => (c.year_total != null ? c.year_total : c.confidential_total);
  const costSum = (x) => (x.office_costs || []).filter((c) => c.summed).reduce((a, c) => a + (c.year_total || 0), 0);
  const SPOUSE = () => PEOPLE.find((x) => x.position === 'conjuge');
  function costBlock(x, short) {  // the small block on a card
    const s = costSum(x), sp = x.position === 'presidente' ? SPOUSE() : null;
    return `<div class="cost"><div class="cost-h">Gasto público ligado ${x.position === 'conjuge' ? 'a ela' : 'ao cargo'}, ${esc(x.costs_months)}</div>`
      + (x.office_costs || []).filter((c) => c.summed).map((c) => `<div class="r"><span class="lb">${esc(short ? COST_SHORT[c.key] || c.label : c.label)}</span><span class="vl">${brl(c.year_total)}</span></div>`).join('')
      + `<div class="tot"><span>Somado</span><b>${brl(s)}</b></div>`
      + `<div class="tnote">não é renda pessoal${sp ? `; com a cônjuge: ${brl(s + costSum(sp))}` : ''}</div></div>`;
  }
  function spouseNode(spouse) {
    if (mode !== 'pessoa' || !spouse) return `<div class="node spouse" data-node="conjuge" style="--pc:var(--exe)"><div class="hd">${ph(null)}<div><div class="pw">Cônjuge</div><div class="ttl">Cônjuge do Presidente</div><div class="sub">sem cargo público</div></div></div>`
      + `<div class="rows"><div class="r"><span class="lb">Salário</span><span class="vl">não há</span></div></div><div class="tnote">O Decreto 12.604/2025 manda o Gabinete Pessoal do Presidente apoiar o cônjuge; o custo desse apoio não é publicado.</div></div>`;
    return `<div class="node spouse" data-node="conjuge" style="--pc:var(--exe)"><div class="hd">${ph(spouse)}<div><div class="pw">Cônjuge</div><div class="ttl">${esc(spouse.known_as || spouse.name)}</div><div class="sub">${esc(spouse.name)} · sem cargo público</div></div></div>`
      + `<div class="rows">${rowHTML({ label: 'Salário', s: 'no', v: 'não recebe' }, false)}</div>${costBlock(spouse, true)}<button class="go" type="button" data-open="${spouse.id}">Ver a ficha</button></div>`;
  }

  // who holds each Executive and Judiciary node, from the collected files
  const SINGLE_OF = { presidente: (x) => x.position === 'presidente', vice: (x) => x.position === 'vice', 'presidente-stf': (x) => x.court === 'STF' && x.role === 'Presidente' };
  const GROUP_OF = { ministros: (x) => x.position === 'ministros', 'ministros-stf': (x) => x.court === 'STF', tribunais: (x) => x.house === 'judiciario' && x.court !== 'STF' };
  const COUNTED = [['housing', 'Recebem auxílio-moradia'], ['jetons', 'Recebem jetons de conselhos'], ['jeton', 'Recebem jetons'], ['permanence_bonus', 'Recebem abono de permanência'], ['cumulative_jurisdiction', 'Recebem gratificação por acúmulo']];
  function membersStats(p, xs) {
    const n = xs.length, ms = xs.map(model), sum = ms.reduce((a, m) => a + m.total, 0), sumOwn = ms.reduce((a, m) => a + m.own, 0);
    const r = (l, v) => `<div class="r"><span class="lb">${esc(l)}</span><span class="vl">${v}</span></div>`;
    const counts = COUNTED.filter(([k]) => xs.some((x) => x.items.some((it) => it.key === k)))
      .map(([k, l]) => r(l, `${int(xs.filter((x) => x.items.some((it) => it.key === k && it.monthly > 0)).length)} de ${int(n)}`)).join('');
    const courts = [...new Set(xs.map((x) => x.court).filter(Boolean))];
    return `<div class="stats">${r('Com ficha', `${int(n)} ${n === 1 ? 'pessoa' : 'pessoas'}`)}${courts.length > 1 ? r('Tribunais', courts.join(', ')) : ''}${counts}</div>`
      + `<div class="tot" data-group-sum="${p.id}"><span>Os ${int(n)} juntos, por mês</span><b>${brl(sum)}</b></div><div class="tot sub"><span>Média por pessoa</span><b>${brl(sum / n)}</b></div>`
      + (ms.some((m) => m.partial) ? '<div class="tnote"><span class="chip">parcial</span> parte do dado não é publicada</div>' : '')
      + splitHTML({ total: sum, own: sumOwn }) + `<button class="go" type="button" data-goto-group="${p.id}">Ver cada um ↓</button>`;
  }
  // A group shows the sum of all its members first and the average per person second, each labelled as such.
  function groupStats(house) {
    const xs = PEOPLE.filter((x) => x.house === house), n = xs.length, who = house === 'camara' ? 'deputado' : 'senador';
    const cnt = (f) => xs.filter(f).length, ms = xs.map(model);
    const sum = ms.reduce((a, m) => a + m.total, 0), sumOwn = ms.reduce((a, m) => a + m.own, 0);
    const avgC = xs.reduce((a, x) => a + ((x.ceap && x.ceap.avg) || 0), 0) / n, avgO = xs.reduce((a, x) => a + ((x.office && x.office.avg) || 0), 0) / n;
    const r = (l, v, nt) => `<div class="r"><span class="lb">${esc(l)}</span><span class="vl">${v}</span>${nt ? `<span class="nt">${esc(nt)}</span>` : ''}</div>`;
    return `<div class="stats">${r('Recebem auxílio-moradia', `${int(cnt((x) => x.housing.uses === true))} de ${int(n)}`)}${r('Usam imóvel funcional', `${int(cnt((x) => x.flat.uses === true))} de ${int(n)}`)}`
      + `${r(`Cota, média por ${who}`, `<span>${brl(avgC)}</span><small>por mês</small>`)}`
      + (house === 'camara' ? r(`Verba de gabinete, média por ${who}`, `<span>${brl(avgO)}</span><small>por mês</small>`) : '') + '</div>'
      + `<div class="tot" data-group-sum="${house}"><span>Os ${int(n)} juntos, por mês</span><b>${brl(sum)}</b></div>`
      + `<div class="tot sub"><span>Média por ${who}</span><b>${brl(sum / n)}</b></div>`
      + (house === 'senado' ? '<div class="tnote"><span class="chip">parcial</span> sem a verba de gabinete</div>' : '')
      + splitHTML({ total: sum, own: sumOwn })
      + `<button class="go" type="button" data-goto="${house}">Ver cada um dos ${int(n)} ↓</button>`;
  }
  function nodeHTML(p) {
    if (p.kind === 'root') return `<div class="node root" data-node="${p.id}" style="grid-column:1 / -1"><div class="ttl">${esc(p.title)}</div><div class="rootnote">${esc(p.note)}</div></div>`;
    const col = `grid-column:${p.col[0]} / ${p.col[1] + 1};grid-row:${p.row + 1};--pc:${POWER[p.power] || 'var(--ink)'}`, head = p.row === 1;
    const house = p.id === 'deputado' ? 'camara' : p.id === 'senador' ? 'senado' : null;
    const members = GROUP_OF[p.id] ? PEOPLE.filter(GROUP_OF[p.id]) : [];
    const single = SINGLE_OF[p.id] ? PEOPLE.find(SINGLE_OF[p.id]) : null;
    const first = (p.people || [])[0] || {}, dir = single || person[first.id];
    const who = mode === 'pessoa' && !house && !p.group && !members.length ? (dir || (first.name ? first : null)) : null;
    const paired = p.id === 'presidente';
    let h = `<div class="node${head ? ' head' : ''}" data-node="${p.id}" style="${paired ? `--pc:${POWER[p.power]}` : col}"><div class="hd">${ph(who)}<div style="min-width:0">`
      + `<div class="pw">${esc(p.power)}</div><div class="ttl">${esc(p.title)}</div>`;
    if (who) h += `<div class="sub"><b>${esc(who.name)}</b>${who.party ? ` <span class="party">${esc(who.party)}</span>` : ''}${who.uf ? ' ' + esc(who.uf) : ''}${(who.role || first.role) && !p.title.toLowerCase().includes((who.role || first.role).toLowerCase()) ? ` · ${esc(who.role || first.role)}` : ''}${((who.office && who.office.since) || who.since || first.since) ? ` · desde ${dmy((who.office && who.office.since) || who.since || first.since)}` : ''}</div>`;
    else if (p.count) h += `<div class="sub">${int(p.count)} ${p.count === 1 ? 'pessoa' : 'pessoas'}${p.count_note ? ' · ' + esc(p.count_note) : ''}</div>`;
    h += '</div></div>';
    if (p.group) h += `<div class="rows">${p.averages.map(([l, v]) => `<div class="r"><span class="lb">${esc(l)}</span><span class="vl">${brl(v)}</span></div>`).join('')}</div>`
      + `<div class="tnote">${mode === 'pessoa' ? '<span class="chip grp">grupo</span> ' : ''}${esc(p.averages_note || 'Média do que cada pessoa recebe por mês.')} ${p.count_detail ? esc(p.count_detail) + '.' : ''} Posição de ${esc(p.as_of)}.</div>`;
    else if (mode === 'pessoa' && house) h += groupStats(house);
    else if (mode === 'pessoa' && members.length) h += membersStats(p, members);
    else if (who && dir) { const M = model(dir); h += `<div class="rows">${(M.generic ? cardRows(M) : M.rows).map((r) => rowHTML(r, false)).join('')}</div>${totHTML(M, 'Salário e auxílios por mês')}${dir.office_costs ? costBlock(dir, true) : ''}<button class="go" type="button" data-open="${dir.id}">Ver a ficha completa</button>`; }
    else if (who) h += otherPersonRows(p, who);
    else {
      h += cargoRows(p);
      if (mode === 'pessoa') h += '<div class="tnote"><span class="chip">não publicado</span> quem ocupa e o que usa</div>';
      if (house && mode === 'cargo') h += `<button class="go" type="button" data-goto="${house}">Ver cada um dos ${int(p.count)} ↓</button>`;
    }
    h += '</div>';
    return paired ? `<div class="pair" style="${col}">${h}<div class="tie" aria-hidden="true"></div>${spouseNode(SPOUSE())}</div>` : h;
  }
  const tree = document.querySelector('[data-tree]');
  function drawEdges() {
    const svg = tree.querySelector('.edges'), T = tree.getBoundingClientRect();
    const box = (id) => tree.querySelector(`[data-node="${id}"]`).getBoundingClientRect();
    svg.setAttribute('width', tree.scrollWidth); svg.setAttribute('height', tree.scrollHeight);
    let s = '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#8A95A1"/></marker></defs>';
    P.filter((p) => p.parent).forEach((p) => {
      const a = box(p.parent), b = box(p.id);
      const x1 = a.left + a.width / 2 - T.left, y1 = a.bottom - T.top, x2 = b.left + b.width / 2 - T.left, y2 = b.top - T.top - 3;
      s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#8A95A1" stroke-width="1.6" marker-end="url(#ah)"/>`;
      if (p.count > 1) {
        const mx = x1 + (x2 - x1) * 0.6, my = y1 + (y2 - y1) * 0.6;
        s += `<text x="${mx + (x2 >= x1 ? 9 : -9)}" y="${my}" text-anchor="${x2 >= x1 ? 'start' : 'end'}" font-family="Manrope, system-ui" font-size="13" font-weight="800" fill="#5B6773">× ${int(p.count)}</text>`;
      }
    });
    svg.innerHTML = s;
  }
  function drawTree() { tree.innerHTML = '<svg class="edges" aria-hidden="true"></svg>' + P.map(nodeHTML).join(''); drawEdges(); }
  document.querySelector('[data-ico-cargo]').innerHTML = SIL;
  document.querySelector('[data-ico-pessoa]').innerHTML = SIL + `<img src="${esc(byId.presidente.people[0].photo)}" alt="">`;
  document.querySelectorAll('[data-mode]').forEach((b) => b.addEventListener('click', () => {
    mode = b.dataset.mode; document.querySelectorAll('[data-mode]').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); drawTree();
  }));
  window.addEventListener('resize', drawEdges);
  tree.addEventListener('load', drawEdges, true);
  if (document.fonts) document.fonts.ready.then(drawEdges);
  const stage = document.querySelector('[data-stage]'), hint = document.querySelector('[data-hint]');
  const hintState = () => { hint.hidden = stage.scrollWidth <= stage.clientWidth + 2; };
  stage.addEventListener('scroll', () => { hint.hidden = true; });
  window.addEventListener('resize', hintState);

  // ---------- the directory
  const F = { q: '', house: 'all', uf: '', party: '', sort: 'name' }; let shown = 24;
  const cmp = [];
  const housesEl = document.querySelector('[data-houses]');
  const nOf = (h) => PEOPLE.filter((x) => h === 'all' || x.house === h).length;
  housesEl.innerHTML = [['all', 'Todos'], ['camara', 'Câmara'], ['senado', 'Senado'], ['executivo', 'Executivo'], ['judiciario', 'Judiciário']].filter(([k]) => nOf(k))
    .map(([k, l]) => `<button type="button" data-house="${k}" aria-pressed="${k === 'all'}">${l} ${int(nOf(k))}</button>`).join('');
  const ufs = [...new Set(PEOPLE.map((x) => x.uf).filter(Boolean))].sort(), parties = [...new Set(PEOPLE.map((x) => x.party).filter(Boolean))].sort((a, b) => plain(a).localeCompare(plain(b)));
  document.querySelector('[data-uf]').innerHTML = '<option value="">Todos os estados</option>' + ufs.map((u) => `<option>${u}</option>`).join('');
  document.querySelector('[data-party]').innerHTML = '<option value="">Todos os partidos</option>' + parties.map((u) => `<option>${esc(u)}</option>`).join('');
  const IDX = PEOPLE.map((x) => ({ x, words: plain(`${x.name} ${x.known_as || ''} ${x.court || ''} ${x.ministry || ''}`).split(/\s+/), name: plain(x.name), party: plain(x.party), uf: x.uf, M: model(x) }));
  function matches(e) {
    if (F.house !== 'all' && e.x.house !== F.house) return false;
    if (F.uf && e.uf !== F.uf) return false;
    if (F.party && e.x.party !== F.party) return false;
    const toks = plain(F.q).split(/\s+/).filter(Boolean);
    return toks.every((t) => e.party === t || e.uf === t || e.words.some((w) => w.startsWith(t)) || (t.length > 3 && e.name.includes(t)));
  }
  function cardHTML(e) {
    const x = e.x, M = e.M, on = cmp.includes(x.id);
    return `<article class="pc${on ? ' cmp' : ''}" data-card="${x.id}" data-total="${M.total}" data-own="${M.own}" data-ceap="${x.ceap && x.ceap.used != null ? x.ceap.used : ''}"><div class="who">${ph(x, true)}<div style="min-width:0"><strong>${esc(x.name)}</strong>`
      + `<div class="meta">${metaHTML(x)}</div></div></div>`
      + `<div class="rows">${(M.generic ? cardRows(M) : M.rows).map((r) => rowHTML(r, !M.generic)).join('')}</div>${M.generic && M.rows.length > cardRows(M).length ? `<div class="tnote">mais ${int(M.rows.length - cardRows(M).length)} componentes sem valor em 2026 na ficha completa</div>` : ''}${totHTML(M)}`
      + (x.bills ? `<div class="rows">${billsLine(x)}</div>` : '')
      + (x.office_costs ? costBlock(x, true) : '')
      + `<div class="pc-ft"><button class="btn dark" type="button" data-open="${x.id}">Ver ficha completa</button><label class="cmpbox"><input type="checkbox" data-cmp="${x.id}"${on ? ' checked' : ''}>Comparar</label></div></article>`;
  }
  // a minister's or judge's card shows what was paid in 2026, plus the housing line either way
  const SHORT = { salary: 'Salário bruto', christmas_bonus: '13º salário', vacation: 'Férias', other_pay: 'Outras remunerações', indemnities: 'Verbas indenizatórias', ceiling_cut: 'Abate-teto' };
  const cardRows = (M) => M.rows.filter((r) => r.m || r.k === 'salary' || r.k === 'housing').map((r) => (M.generic && SHORT[r.k] ? Object.assign({}, r, { label: SHORT[r.k] }) : r));
  const metaHTML = (x) => (PARL(x) ? `<span class="party">${esc(x.party)}</span>${flag(x.uf)}<span>${HOUSE[x.house]}</span>`
    : `${x.party ? `<span class="party">${esc(x.party)}</span>` : ''}<span>${esc(place(x))}</span><span>${esc(x.role || '')}${x.ministry && !(x.role || '').includes(x.ministry) ? ', ' + esc(x.ministry) : ''}</span>`);
  const grid = document.querySelector('[data-grid]'), moreBtn = document.querySelector('[data-more]');
  function drawList() {
    let xs = IDX.filter(matches);
    const by = { name: (a, b) => a.name.localeCompare(b.name), 'name-desc': (a, b) => b.name.localeCompare(a.name), total: (a, b) => b.M.total - a.M.total, 'total-asc': (a, b) => a.M.total - b.M.total,
                 'own-desc': (a, b) => b.M.own - a.M.own, 'own-asc': (a, b) => a.M.own - b.M.own,
                 'ceap-desc': (a, b) => ((b.x.ceap && b.x.ceap.used) || -1) - ((a.x.ceap && a.x.ceap.used) || -1),
                 'ceap-asc': (a, b) => ((a.x.ceap && a.x.ceap.used != null ? a.x.ceap.used : 1e12)) - ((b.x.ceap && b.x.ceap.used != null ? b.x.ceap.used : 1e12)) };
    xs.sort(by[F.sort]);
    document.querySelector('[data-count]').innerHTML = `<b>${int(xs.length)}</b> ${xs.length === 1 ? 'pessoa' : 'pessoas'}`; paintFilters(xs.length);
    grid.innerHTML = xs.length ? xs.slice(0, shown).map(cardHTML).join('') : '<div class="empty">Ninguém com esse nome, partido ou estado. Confira a grafia ou limpe os filtros.</div>';
    moreBtn.hidden = xs.length <= shown; moreBtn.textContent = `Mostrar mais ${Math.min(24, xs.length - shown)} de ${int(xs.length - shown)}`;
  }
  const qEl = document.querySelector('[data-q]');
  qEl.addEventListener('input', () => { F.q = qEl.value; shown = 24; drawList(); });
  housesEl.addEventListener('click', (e) => { const b = e.target.closest('[data-house]'); if (!b) return; F.house = b.dataset.house; shown = 24;
    housesEl.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); drawList(); });
  [['uf', '[data-uf]'], ['party', '[data-party]']].forEach(([k, s]) => document.querySelector(s).addEventListener('change', (e) => { F[k] = e.target.value; shown = 24; drawList(); }));
  // ---------- the filters drawer (spec filtros-cargos, D187): the house buttons and the two selects above live in it
  const ORDER_LABEL = { name: ['Nome (A a Z)', 'Nome (Z a A)'], total: ['Maior total por mês', 'Menor total por mês'],
    own: ['Mais para a pessoa por mês', 'Menos para a pessoa por mês'], ceap: ['Maior uso da cota em 2026', 'Menor uso da cota em 2026'] };
  const SORT_OF = { name: ['name', 'name-desc'], total: ['total', 'total-asc'], own: ['own-desc', 'own-asc'], ceap: ['ceap-desc', 'ceap-asc'] };
  const fdrawer = document.querySelector('[data-fdrawer]'), fback = document.querySelector('[data-fback]'), ftab = document.querySelector('[data-ftab]');
  const ufSel = document.querySelector('[data-uf]'), partySel = document.querySelector('[data-party]'), factive = document.querySelector('[data-active]');
  const TAG_X = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
  const sortState = { key: 'name', first: true };
  function setSort() { F.sort = SORT_OF[sortState.key][sortState.first ? 0 : 1]; shown = 24; drawList(); }
  function paintFilters(n) {
    fdrawer.querySelectorAll('[data-key]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.key === sortState.key)));
    const dir = fdrawer.querySelector('[data-dir]'); dir.dataset.first = String(sortState.first);
    dir.querySelector('[data-dirtxt]').textContent = sortState.key === 'name' ? (sortState.first ? 'A a Z' : 'Z a A') : (sortState.first ? 'Maior primeiro' : 'Menor primeiro');
    document.querySelector('[data-ordlab]').innerHTML = ` · ordenadas por <b>${ORDER_LABEL[sortState.key][sortState.first ? 0 : 1]}</b>`;
    const on = [];
    if (F.house !== 'all') { const b = housesEl.querySelector(`[data-house="${F.house}"]`); on.push(['house', b ? b.textContent.replace(/\s*[\d.]+$/, '') : F.house]); }
    if (F.uf) on.push(['uf', F.uf]); if (F.party) on.push(['party', F.party]);
    const fn = ftab.querySelector('[data-fn]'); fn.hidden = !on.length; fn.textContent = on.length;
    ftab.setAttribute('aria-label', on.length ? `Filtros, ${on.length} ${on.length === 1 ? 'ligado' : 'ligados'}` : 'Filtros');
    factive.innerHTML = on.map(([k, l]) => `<button type="button" data-rm="${k}" aria-label="Tirar o filtro ${esc(l)}">${esc(l)}${TAG_X}</button>`).join('');
    fdrawer.querySelector('[data-fseen]').textContent = n ? `Ver ${int(n)} ${n === 1 ? 'pessoa' : 'pessoas'}` : 'Nenhuma pessoa';
  }
  function showFilters(v) {
    fdrawer.hidden = fback.hidden = !v; ftab.setAttribute('aria-expanded', String(v)); document.body.style.overflow = v ? 'hidden' : '';
    (v ? fdrawer.querySelector('[data-fx]') : ftab).focus({ preventScroll: true });
  }
  ftab.addEventListener('click', () => showFilters(true));
  fback.addEventListener('click', () => showFilters(false));
  fdrawer.querySelectorAll('[data-fclose]').forEach((b) => b.addEventListener('click', () => showFilters(false)));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !fdrawer.hidden) showFilters(false); });
  fdrawer.querySelector('[data-keys]').addEventListener('click', (e) => { const b = e.target.closest('[data-key]'); if (!b) return; sortState.key = b.dataset.key; sortState.first = true; setSort(); });
  fdrawer.querySelector('[data-dir]').addEventListener('click', () => { sortState.first = !sortState.first; setSort(); });
  fdrawer.querySelector('[data-fclear]').addEventListener('click', () => {
    F.house = 'all'; F.uf = ''; F.party = ''; ufSel.value = ''; partySel.value = '';
    housesEl.querySelectorAll('[data-house]').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.house === 'all')));
    sortState.key = 'name'; sortState.first = true; setSort();
  });
  factive.addEventListener('click', (e) => { const b = e.target.closest('[data-rm]'); if (!b) return;
    if (b.dataset.rm === 'house') housesEl.querySelector('[data-house="all"]').click();
    else { const s = b.dataset.rm === 'uf' ? ufSel : partySel; s.value = ''; s.dispatchEvent(new Event('change')); }
    ftab.focus({ preventScroll: true }); });
  moreBtn.addEventListener('click', () => { shown += 24; drawList(); });

  // ---------- compare
  const tray = document.querySelector('[data-tray]');
  function drawTray() {
    tray.hidden = !cmp.length;
    document.querySelector('[data-faces]').innerHTML = cmp.map((id) => `<span>${person[id].photo ? `<img src="${esc(person[id].photo)}" alt="">` : ''}</span>`).join('');
    document.querySelector('[data-tray-label]').textContent = `${cmp.length} de 3 para comparar`;
    document.querySelector('[data-cmp-open]').disabled = cmp.length < 2;
    document.querySelector('[data-cmp-open]').style.opacity = cmp.length < 2 ? .55 : 1;
  }
  document.addEventListener('change', (e) => {
    const c = e.target.closest('[data-cmp]'); if (!c) return;
    const id = c.dataset.cmp, i = cmp.indexOf(id);
    if (c.checked && i < 0) { if (cmp.length >= 3) { c.checked = false; return; } cmp.push(id); }
    if (!c.checked && i >= 0) cmp.splice(i, 1);
    const card = c.closest('.pc'); if (card) card.classList.toggle('cmp', c.checked);
    drawTray();
  });
  document.querySelector('[data-cmp-clear]').addEventListener('click', () => { cmp.length = 0; drawTray(); drawList(); });

  // ---------- the sheet: one parliamentarian in full, or the comparison
  const back = document.querySelector('[data-back]'), sheet = document.querySelector('[data-sheet]');
  // "Pedir correção" opens the data-correction issue form, prefilled with the sheet's link and the person's name.
  const FIX_FORM = 'https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/new';
  const fixUrl = (x) => `${FIX_FORM}?${new URLSearchParams({ template: 'data-correction.yml', title: `Correção: ${x.name}`,
    page: `${location.origin}${location.pathname}#p=${encodeURIComponent(x.id)}`, item: `Ficha de ${x.name}` })}`;
  function bars(by, last, label) {
    const vals = Object.entries(by || {}).map(([m, v]) => [+m, v]), max = Math.max(1, ...vals.map(([, v]) => v));
    const get = (m) => (vals.find(([k]) => k === m) || [m, null])[1];
    const top = Math.max(...vals.map(([m]) => m), last);
    let h = `<div class="bars" role="img" aria-label="${esc(label)} mês a mês">`;
    for (let m = 1; m <= 12; m++) {
      const v = get(m), cls = m > top ? 'zero' : m > last ? 'part' : v ? '' : 'zero';
      h += `<div class="${cls}" title="${MON[m]}: ${v != null ? brl(v) : 'sem lançamento'}"><i style="height:${v ? Math.max(3, (v / max) * 96) : 2}px"></i><small>${MON[m]}</small></div>`;
    }
    return h + `</div><div class="bars-max"><span>maior mês: ${brl(max)}</span><span>${vals.some(([m]) => m > last) ? `listras: depois de ${MONTHS[last]}, ainda chegando` : ''}</span></div>`;
  }
  function openGeneric(x, M) {
    // the sources of every number the sheet shows: the pay components and the spending tied to the post (D235)
    const srcs = [...new Set([...x.items, ...(x.office_costs || []), ...(x.trips || [])].map((it) => it.source).filter(Boolean))];
    return `<div class="crumb">Os 3 Poderes › ${HOUSE_FULL[x.house]}${x.court ? ' › ' + esc(x.court) : ''} › <b>${esc(x.name)}</b></div>`
      + `<div class="p-head">${ph(x)}<div><h2>${esc(x.name)}</h2><div class="meta">${metaHTML(x)}</div>`
      + `<div class="links">${x.page ? `<a href="${esc(x.page)}" target="_blank" rel="noopener">Página oficial ↗</a>` : ''}<button type="button" data-copy>Copiar link</button><a class="fix" href="${esc(fixUrl(x))}" target="_blank" rel="noopener">Pedir correção</a></div></div></div>`
      + `<div class="p-cols"><div class="box"><h4>Salário e cada componente pago em 2026</h4><div class="rows">${M.rows.filter((r) => r.block !== 'tse').map((r) => rowHTML(r)).join('')}</div>`
      + (M.rows.some((r) => r.block === 'tse') ? `<div class="blk">Pago pelo TSE <span>· média de ${esc(M.tseMonths)}</span></div><div class="rows">${M.rows.filter((r) => r.block === 'tse').map((r) => rowHTML(Object.assign({}, r, { label: r.label.replace(/^TSE: /, '') }))).join('')}</div>` : '')
      + `<div class="big"><span>${esc(M.totalLabel || 'Total por mês')}</span><b>${brl(M.total)}</b></div>${M.totalNote ? `<div class="tnote">${esc(M.totalNote)}</div>` : ''}${M.partial ? '<div class="tnote"><span class="chip">parcial</span> parte do dado não é publicada; nunca uma estimativa</div>' : ''}${splitHTML(M)}</div>`
      + `<div style="display:grid;gap:14px;align-content:start"><div class="box"><h4>Outros</h4><ul class="others">`
      + `${x.role ? `<li><span>Cargo</span><b>${esc(x.role)}</b></li>` : ''}${x.tse_role ? `<li><span>No TSE</span><b>${esc(x.tse_role)}</b></li>` : ''}`
      + `${x.court_since ? `<li><span>No ${esc(x.court)} desde</span><b>${dmy(x.court_since)}</b></li>` : ''}${x.office ? `<li><span>${esc(x.office.label)} desde</span><b><a href="${esc(x.office.source)}" target="_blank" rel="noopener">${dmy(x.office.since)}</a></b></li>` : ''}`
      + `${x.since ? `<li><span>No cargo desde</span><b>${dmy(x.since)}</b></li>` : ''}${x.data_as_of ? `<li><span>Último mês publicado</span><b>${esc(x.data_as_of.split('-').reverse().join('/'))}</b></li>` : ''}</ul>`
      + `${x.note ? `<p class="bars-note">${esc(x.note)}</p>` : ''}</div></div></div>`
      + (x.office_costs ? costsSection(x) : '')
      + `<p class="srcs">Fontes: ${srcs.map((u, i) => { const h = new URL(u).hostname.replace(/^www\./, ''), n = srcs.filter((v) => new URL(v).hostname.replace(/^www\./, '') === h);
          return `<a href="${esc(u)}">${esc(h)}${n.length > 1 ? ` (${n.indexOf(u) + 1})` : ''}</a>`; }).join(', ')}. A média por mês é o total de 2026 dividido pelos meses que a instituição publicou.</p>`;
  }
  function costsSection(x) {
    const her = x.position === 'conjuge', s = costSum(x), sp = x.position === 'presidente' ? SPOUSE() : null;
    // a summed item says so; a valued item left out says why; an item with no value is information only
    const row = (c) => { const v = costValue(c), why = c.key.includes('confidential') ? 'motivo sob sigilo' : 'ligação mais fraca no motivo da viagem';
      const tag = c.summed ? '<span class="tag">somado</span>' : c.part_of || v == null ? '' : `<span class="tag out">não somado: ${why}</span>`;
      return `<div class="cost-row${c.part_of ? ' sub' : ''}"><span>${esc(c.label.replace(/ \(gasto público ligado[^)]*\)/, ''))}${tag}</span>`
        + `<b>${v != null ? brl(v) : 'sem valor publicado'}</b>${c.note ? `<span class="nt">${esc(c.note.split('. ').slice(0, c.part_of ? 1 : 2).join('. '))}</span>` : ''}</div>`; };
    const by = {}; (x.office_costs || []).filter((c) => c.summed && c.by_month).forEach((c) => Object.entries(c.by_month).forEach(([m, v]) => { by[m] = (by[m] || 0) + v; }));
    const trips = (x.trips || []).slice().sort((a, b) => (b.total || 0) - (a.total || 0));
    const tripLi = (tr) => `<li><div class="tl-top"><span>${esc(tr.destinations || 'destino sob sigilo')}</span><b>${tr.total != null ? brl(tr.total) : 'sem valor'}</b></div>`
      + `<small>${dmy(tr.start)}${tr.end && tr.end !== tr.start ? ' a ' + dmy(tr.end) : ''}${tr.travellers ? ` · ${int(tr.travellers)} ${tr.travellers === 1 ? 'viajante' : 'viajantes'}` : ''}${tr.traveller ? ` · ${esc(tr.traveller)}` : ''}${tr.confidential ? ' · sigilosa' : ''}</small>`
      + (her && tr.purpose ? `<small>Motivo: ${esc(tr.purpose)}</small>` : '') + '</li>';
    return `<div class="full2"><div class="box"><h4>Gasto público ligado ${her ? 'a ela' : 'ao cargo'}, ${esc(x.costs_months)}</h4>`
      + `<p class="bars-note" style="margin-top:0">Não é renda pessoal: é o que órgãos federais gastaram ${her ? 'com viagens de servidores para apoiar a agenda dela' : 'com viagens de servidores ligadas às viagens dele e com o cartão corporativo das unidades que o atendem'}, pelos arquivos do Portal da Transparência.</p>`
      + (x.office_costs || []).map(row).join('')
      + `<div class="big"><span>Somado em 2026</span><b>${brl(s)}</b></div>${sp ? `<div class="tnote">Com a cônjuge: <b>${brl(s + costSum(sp))}</b> em 2026.</div>` : ''}`
      + (Object.keys(by).length ? bars(by, 12, 'Gasto somado') : '') + '</div>'
      + `<div class="box"><h4>${her ? 'Viagens de apoio a ela' : 'Viagens identificadas'} (${int(trips.length)})</h4>`
      + `<p class="bars-note" style="margin-top:0">${her ? 'Cada viagem com o motivo escrito pelo órgão.' : 'Viagens de servidores agrupadas por destino e datas; as datas são as da equipe, não as dele. O Portal não publica a lista das viagens do presidente.'}</p>`
      + `<ul class="trip-list">${trips.slice(0, 10).map(tripLi).join('')}</ul>${trips.length > 10 ? `<details><summary class="bars-note" style="cursor:pointer">ver as outras ${int(trips.length - 10)}</summary><ul class="trip-list">${trips.slice(10).map(tripLi).join('')}</ul></details>` : ''}</div></div>`
      + `<div class="full2">${(x.structure || x.other_units) ? `<div class="box"><h4>${her ? 'Estrutura e documentos oficiais' : 'Outras unidades da Presidência, fora do total'}</h4><ul class="others">`
      + (her ? x.structure.map((d) => `<li><span>${esc(d.what)}${d.source ? ` <a href="${esc(d.source)}">fonte</a>` : ''}</span><b>${d.cost != null ? brl(d.cost) : 'sem valor'}</b></li>`).join('')
             : x.other_units.map((u) => `<li><span>${esc(u.unit)}</span><b>${brl(u.year_total)}</b></li>`).join('')) + '</ul></div>' : ''}`
      + `${(x.unpublished || []).length ? `<div class="box"><h4>O que não é publicado</h4><ul class="others">${x.unpublished.map((n) => `<li><span>${esc(n.what)}</span><b>não publicado</b></li>`).join('')}</ul></div>` : ''}</div>`;
  }
  function openPerson(id, push = true) {
    const x = person[id]; if (!x) return; const M = model(x), cam = x.house === 'camara';
    if (!PARL(x)) {
      sheet.className = 'sheet'; sheet.innerHTML = `<button class="x" type="button" data-close aria-label="Fechar">✕</button>` + openGeneric(x, M);
      opener = opener || document.activeElement; back.hidden = false; document.body.style.overflow = 'hidden'; focusClose();
      if (push) history.replaceState(null, '', '#p=' + encodeURIComponent(id));
      return;
    }
    sheet.className = 'sheet';
    const others = cam ? `<ul class="others"><li><span>Passaporte diplomático</span><b>${x.passport.uses ? 'possui' : 'não possui'}</b></li><li><span>Viagens em missão oficial em 2026</span><b>${x.missions != null ? int(x.missions) : 'não publicado'}</b></li><li><span>Página da Câmara atualizada em</span><b>${esc(x.updated)}</b></li></ul>`
      : `<ul class="others"><li><span>Passaporte diplomático</span><b>não publicado</b></li><li><span>Em exercício desde</span><b>${dmy(x.exercise_since)}</b></li><li><span>Arquivo da cota atualizado em</span><b>${esc(x.updated)}</b></li></ul><p class="bars-note">O direito ao passaporte diplomático está no Decreto 5.978/2006, mas nem o Senado nem o Itamaraty publicam a lista de quem tem.</p>`;
    sheet.innerHTML = `<button class="x" type="button" data-close aria-label="Fechar">✕</button>`
      + `<div class="crumb">Os 3 Poderes › ${HOUSE_FULL[x.house]} › <b>${esc(x.name)}</b></div>`
      + `<div class="p-head">${ph(x)}<div><h2>${esc(x.name)}</h2><div class="meta"><span class="party">${esc(x.party)}</span>${flag(x.uf)}<span>${cam ? 'Deputado(a) federal' : 'Senador(a)'}</span></div>`
      + `<div class="links"><a href="${esc(x.page)}" target="_blank" rel="noopener">Página oficial ↗</a><button type="button" data-copy>Copiar link</button><a class="fix" href="${esc(fixUrl(x))}" target="_blank" rel="noopener">Pedir correção</a></div></div></div>`
      + `<div class="p-cols"><div class="box"><h4>Salário e auxílios</h4><div class="rows">${M.rows.map((r) => rowHTML(r)).join('')}</div>`
      + `<div class="big"><span>Total por mês</span><b>${brl(M.total)}</b></div>${M.partial ? '<div class="tnote"><span class="chip">parcial</span> falta parte do dado; nunca uma estimativa</div>' : ''}${splitHTML(M)}</div>`
      + `<div style="display:grid;gap:14px;align-content:start"><div class="box soft"><h4>${cam ? 'Cota parlamentar' : 'Cota (CEAPS)'}, mês a mês em 2026</h4>${x.ceap ? bars(x.ceap.by_month, AVG[x.house], 'Cota') + `<div class="bars-note">Total em 2026: <b>${brl(x.ceap.used)}</b>${x.ceap.pct != null ? `, ${nf(x.ceap.pct, 1)}% do que podia usar no ano` : ''}.</div>` : '<div class="bars-note"><span class="chip">sem lançamento</span> nenhum lançamento no arquivo de 2026</div>'}</div>`
      + (cam && x.office ? `<div class="box soft"><h4>Verba de gabinete, mês a mês em 2026</h4>${bars(x.office.by_month, AVG.camara, 'Verba de gabinete')}<div class="bars-note">Total em 2026: <b>${brl(x.office.used)}</b>, ${nf(x.office.pct, 1)}% do que podia usar.</div></div>` : '')
      + (!cam && x.office && x.office.avg != null ? `<div class="box soft"><h4>Equipe do gabinete, mês a mês em 2026</h4>${bars(x.office.by_month, 12, 'Equipe do gabinete')}<div class="bars-note">Total em 2026: <b>${brl(x.office.used)}</b>, salários brutos de ${int(x.office.staff)} pessoas (sem diárias, auxílios e encargos, que o Senado não publica por gabinete).</div></div>` : '')
      + `<div class="box"><h4>Outros</h4>${others}</div></div></div>`
      + `<div data-bills-slot></div>`
      + `<p class="srcs">Fontes: ${cam ? `<a href="${esc(x.page)}">a página do deputado na Câmara</a> (salário, imóvel funcional, auxílio-moradia, cota, verba de gabinete, passaporte, missões)` : `<a href="${esc(D.urls.sen_moradia)}">Senado, auxílio-moradia e imóveis funcionais</a> e o arquivo de despesas da cota do Senado (atualizado em ${esc(x.updated)})`}; valores dos auxílios: ${cam ? `<a href="${esc(D.urls.posse)}">Câmara, exercício do mandato</a>` : `<a href="${esc(D.urls.sen_verbas)}">Senado, verbas além do subsídio</a>`}; salário: <a href="${esc(D.urls.dl172)}">Decreto Legislativo 172/2022</a>.</p>`;
    sheet.querySelector('[data-bills-slot]').appendChild(billsSection(x));
    opener = opener || document.activeElement; back.hidden = false; document.body.style.overflow = 'hidden'; focusClose();
    if (push) history.replaceState(null, '', '#p=' + encodeURIComponent(id));
  }
  function openCompare() {
    sheet.className = 'sheet wide';
    const xs = cmp.map((id) => person[id]), Ms = xs.map(model);
    sheet.innerHTML = `<button class="x" type="button" data-close aria-label="Fechar">✕</button><div class="crumb">Os 3 Poderes › Parlamentares federais › <b>Comparação</b></div>`
      + `<div class="cmp-grid" style="grid-template-columns:repeat(${xs.length}, minmax(250px, 1fr))">${xs.map((x, i) => `<div class="cmp-col box"><div class="who">${ph(x)}<div><strong>${esc(x.name)}</strong><div class="meta">${metaHTML(x)}</div></div></div>`
      + `<div class="rows">${Ms[i].rows.map((r) => rowHTML(r)).join('')}</div>${totHTML(Ms[i])}</div>`).join('')}</div>`;
    opener = opener || document.activeElement; back.hidden = false; document.body.style.overflow = 'hidden'; focusClose();
  }
  // focus goes to the sheet's close button when it opens and back to what opened it when it closes
  let opener = null;
  const focusClose = () => { if (back.hidden || !opener) opener = document.activeElement; const x = sheet.querySelector('[data-close]'); if (x) x.focus({ preventScroll: true }); };
  function close() { back.hidden = true; document.body.style.overflow = ''; if (location.hash) history.replaceState(null, '', location.pathname); if (opener && opener.isConnected) opener.focus({ preventScroll: true }); opener = null; }
  document.addEventListener('click', (e) => {
    const o = e.target.closest('[data-open]'); if (o) { openPerson(o.dataset.open); return; }
    const gg = e.target.closest('[data-goto-group]'); if (gg) { const h = gg.dataset.gotoGroup === 'ministros' ? 'executivo' : 'judiciario'; F.house = h; F.q = gg.dataset.gotoGroup === 'ministros-stf' ? 'STF' : '';
      qEl.value = F.q; shown = 24; housesEl.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.house === F.house))); drawList(); document.getElementById('parlamentares').scrollIntoView({ behavior: 'smooth' }); return; }
    const g = e.target.closest('[data-goto]'); if (g) { F.house = g.dataset.goto; shown = 24; housesEl.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.house === F.house))); drawList(); document.getElementById('parlamentares').scrollIntoView({ behavior: 'smooth' }); return; }
    if (e.target.closest('[data-close]') || e.target === back) { close(); return; }
    if (e.target.closest('[data-cmp-open]') && cmp.length >= 2) { openCompare(); return; }
    const c = e.target.closest('.links [data-copy]'); if (c) { const u = location.href; (navigator.clipboard ? navigator.clipboard.writeText(u) : Promise.reject()).then(() => { c.textContent = 'Link copiado'; }, () => { c.textContent = u; }); }
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !back.hidden) close(); });

  // ---------- head facts and sources
  const nDep = nOf('camara'), nSen = nOf('senado');
  document.querySelector('[data-facts]').innerHTML = [
    [brl(D.salary), 'salário por mês do presidente, dos ministros de Estado, dos deputados, dos senadores e dos ministros do STF'],
    [int(PEOPLE.length), `fichas: ${int(nDep)} deputados, ${int(nSen)} senadores, ${int(PEOPLE.filter((x) => x.house === 'executivo' && x.position !== 'conjuge').length)} no Executivo, ${int(nOf('judiciario'))} nos tribunais superiores${SPOUSE() ? ' e a cônjuge do presidente' : ''}`],
    ['21/10/2026', 'dia em que os valores foram lidos nas páginas oficiais da Câmara, do Senado, do Planalto e do STF'],
  ].map(([b, s]) => `<div class="fact"><b>${esc(b)}</b><span>${esc(s)}</span></div>`).join('');
  document.querySelector('[data-asof]').textContent = `Câmara: páginas lidas em 21/10/2026 · Senado: cota até ${PEOPLE.find((x) => x.house === 'senado').updated}`;
  const U = D.urls;
  document.querySelector('[data-sources]').innerHTML = [
    ['Salário do presidente, do vice, dos ministros, dos deputados e dos senadores: Decreto Legislativo 172/2022', U.dl172],
    ['Salário dos ministros do STF: Lei 14.520/2023; tribunais superiores: 95% dele (CF art. 93, V)', U.l14520],
    ['Auxílio-moradia, verba de gabinete e cota de cada estado dos deputados: Câmara, "Exercício do mandato"', U.camara_mandate],
    ['O que cada deputado usa em 2026: a página de cada deputado na Câmara, lida em 21/10/2026', 'https://www.camara.leg.br/deputados/quem-sao'],
    ['Auxílio-moradia e imóvel funcional de cada senador: dados abertos do Senado', U.sen_housing],
    ['O que cada senador usou da cota em 2026: arquivo de despesas da cota do Senado', 'https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_2026.csv'],
    ['Senadores em exercício, partido e foto: dados abertos do Senado', 'https://legis.senado.leg.br/dadosabertos/senador/lista/atual'],
    ['Deputados em exercício, partido e foto: dados abertos da Câmara', 'https://dadosabertos.camara.leg.br/api/v2/deputados'],
  ].map(([t, u]) => `<li>${esc(t)}. <a href="${esc(u)}">fonte</a></li>`).join('');

  drawTree(); hintState(); drawList(); drawTray();
  if (stage.scrollWidth > stage.clientWidth) stage.scrollLeft = (stage.scrollWidth - stage.clientWidth) / 2;
  const fromHash = () => { const h = decodeURIComponent(location.hash || '').match(/^#p=(.+)$/); if (h && person[h[1]]) openPerson(h[1], false); };
  window.addEventListener('hashchange', fromHash); fromHash();
  document.body.dataset.ready = '1';
})();
