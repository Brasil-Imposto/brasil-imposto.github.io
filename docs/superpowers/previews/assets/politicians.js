// Who held office in the chosen period (round 11, D39). Reads window.BI.politicians_view, a normalized shape built by
// tools/build-standalone-data.py from data/politicians/*.json:
//   person = { name, role, start: 'YYYY-MM-DD', end: 'YYYY-MM-DD' | null, parties: [{ party, from }], photo: { url, credit, link } | null, links: [{ label, url }] }
//   union = { president: [person], vice: [person], economy: [person] }
//   uf[UF] = { governor: [person], vice: [person], senators: [person], federal_deputies: [person], state_deputies: { 2018: [person], 2022: [person] } }
//   mayors[ibge] = [person]   (every state with a municipal map)
// Same treatment for everyone: role, dates, party at the time, official source. Classic script; exposes window.BIG.
(function () {
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const V = () => (window.BI && window.BI.politicians_view) || null;
  const fmt = (d) => (d ? `${d.slice(8, 10)}/${d.slice(5, 7)}/${d.slice(0, 4)}` : 'hoje');
  const initials = (n) => String(n || '').split(' ').filter((w) => w.length > 2).slice(0, 2).map((w) => w[0]).join('');
  // Period bounds as dates: first day of the first month, last day of the last month.
  const bounds = (r) => { const a = r.months[0], b = r.months[r.months.length - 1]; const [y, m] = [+b.slice(0, 4), +b.slice(5, 7)];
    return [`${a}-01`, `${b}-${String(new Date(y, m, 0).getDate()).padStart(2, '0')}`]; };
  // People in office at any time in the period. Someone with several stretches (a senator who left and came back)
  // becomes one entry whose `spans` lists each stretch.
  const inOffice = (list, r) => {
    const [a, b] = bounds(r); const by = new Map();
    // An office's end date is the day the successor starts (01/01/2023 for one president, start of the next), so a
    // person counts in the period only if the office ends after the period's first day.
    for (const p of (list || []).filter((x) => (!x.start || x.start <= b) && (!x.end || x.end > a))) {
      const k = `${p.name}|${p.role}`; const q = by.get(k);
      if (q) { q.spans.push([p.start, p.end]); if (p.start < q.start) q.start = p.start; if (!p.end || (q.end && p.end > q.end)) q.end = p.end; }
      else by.set(k, { ...p, spans: [[p.start, p.end]] });
    }
    return [...by.values()].sort((x, y) => ((x.start || '') < (y.start || '') ? -1 : 1));
  };
  const spansText = (p) => (p.spans || [[p.start, p.end]]).sort((x, y) => (x[0] < y[0] ? -1 : 1)).map(([s, e]) => `${fmt(s)} a ${fmt(e)}`).join('; ');
  // Parties held during the period, in order.
  function partiesIn(p, r) {
    const [a, b] = bounds(r); const ps = (p.parties || []).slice().sort((x, y) => (x.from < y.from ? -1 : 1));
    const out = ps.filter((x, i) => x.from <= b && (!ps[i + 1] || ps[i + 1].from > a)).map((x) => x.party);
    return out.length ? out : ps.length ? [ps[ps.length - 1].party] : [];
  }
  const photo = (p, cls = 'pg-ph') => (p.photo && p.photo.url
    ? `<a class="${cls}" href="${esc(p.photo.link || p.photo.url)}" target="_blank" rel="noopener" title="Foto: ${esc(p.photo.credit || '')}"><img src="${esc(p.photo.url)}" alt="${esc(p.name)}" loading="lazy" referrerpolicy="no-referrer"></a>`
    : `<span class="${cls} init">${esc(initials(p.name))}</span>`);
  const party = (p, r) => partiesIn(p, r).map((x) => `<b class="pg-party">${esc(x)}</b>`).join('<span class="pg-then">depois</span>');
  // D62, the "Influência" bar: length = bills as main author since 2019 (relative to the 95th percentile of all federal
  // legislators), green = approved, red = rejected or vetoed, grey = the rest (in progress, archived, withdrawn).
  function influence(p, slim) {
    const a = p.activity, ref = V() && V().activity_ref; if (!a || !ref) return '';
    const m = a.main_author, len = Math.min(m.total / ref, 1) * 100, seg = (x) => (m.total ? (x / m.total) * 100 : 0);
    const tip = `${m.total} projetos como autor principal desde 2019: ${m.approved} aprovados, ${m.rejected} rejeitados ou vetados, ${m.other} em tramitação, arquivados ou retirados. Coautor em mais ${a.co_author.total}.`;
    return `<span class="pg-inf${slim ? ' slim' : ''}" title="${esc(tip)}">${slim ? '' : '<small>Influência</small>'}<span class="pg-inf-bar"><i style="width:${len}%"><b class="ok" style="width:${seg(m.approved)}%"></b><b class="no" style="width:${seg(m.rejected)}%"></b></i></span>${slim ? '' : `<em>${m.total} projetos · <b class="ok">${m.approved} aprovados</b> · <b class="no">${m.rejected} rejeitados</b></em>`}</span>`;
  }
  // A vacant post (the vice took over as governor) has no person: show the vacancy, its dates and the official reason.
  const vacantCard = (p, role) => `<article class="pg-card pg-vacant"><span class="pg-ph init"></span><div><strong>Cargo vago</strong><span class="pg-role">${esc(role || p.role)}</span>
      <span class="pg-dates">${p.start ? spansText(p) : ''}</span><span class="pg-dates">${esc(p.reason || '')}</span>
      <span class="pg-links">${(p.links || []).slice(0, 2).map((l) => `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label)} ↗</a>`).join('')}</span></div></article>`;
  const card = (p, r, role) => p.vacant ? vacantCard(p, role) : `<article class="pg-card">${photo(p)}<div><strong>${esc(p.name)}</strong><span class="pg-role">${esc(role || p.role)}${p.verified === false ? ' <em class="pg-check">a conferir</em>' : ''}</span>
      <span class="pg-dates">${p.start ? spansText(p) : ''}</span><span class="pg-parties">${party(p, r)}</span>${influence(p)}${/^Presidente da Rep/.test(role || p.role || '') ? mpBar(r) : ''}
      <span class="pg-links">${(p.links || []).slice(0, 2).map((l) => `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label)} ↗</a>`).join('')}</span></div></article>`;

  // For the President, the same idea with the medidas provisórias issued in the period: converted into law (green),
  // rejected (red), lost efficacy or still in progress (grey). Source: Senado/Congresso open data.
  function mpBar(r) {
    const v = V(); const M = v && v.president_mps; if (!M) return '';
    const t = { converted_into_law: 0, rejected: 0, lost_efficacy: 0, in_progress: 0, other: 0 };
    for (const y of r.years) for (const [k, n] of Object.entries(M[y] || {})) t[k in t ? k : 'other'] += n;
    const tot = Object.values(t).reduce((a, b) => a + b, 0); if (!tot) return '';
    const seg = (x) => (x / tot) * 100;
    return `<span class="pg-inf" title="Medidas provisórias editadas no período e o destino de cada uma no Congresso Nacional"><small>Influência</small><span class="pg-inf-bar"><i style="width:100%"><b class="ok" style="width:${seg(t.converted_into_law)}%"></b><b class="no" style="width:${seg(t.rejected)}%"></b></i></span><em>${tot} medidas provisórias · <b class="ok">${t.converted_into_law} viraram lei</b> · <b class="no">${t.rejected} rejeitadas</b> · ${t.lost_efficacy} perderam a validade</em></span>`;
  }
  // The home card line: the president(s) in office during the period.
  function presidentLine(r) {
    const v = V(); if (!v || !v.union) return '';
    const ps = inOffice(v.union.president, r); if (!ps.length) return '';
    return `<div class="pg-line">${ps.map((p) => `${photo(p, 'pg-mini')}<span><small>Presidente no período</small><b>${esc(p.name)}</b> ${party(p, r)}</span>`).join('')}</div>`;
  }
  // The Brasil modal: president, vice and the minister in charge of the economy.
  function unionSection(r) {
    const v = V(); if (!v || !v.union) return '';
    const rows = [['president', 'Presidente da República'], ['vice', 'Vice-presidente'], ['economy', 'Ministro da economia']]
      .flatMap(([k, role]) => inOffice(v.union[k], r).map((p) => card(p, r, p.role || role)));
    return rows.length ? `<section class="pg-sec"><h3>Quem governava o Brasil · ${esc(r.label)}</h3><p class="pg-lead">cargos e datas oficiais; partido na época</p><div class="pg-grid">${rows.join('')}</div>${sourcesNote()}</section>` : '';
  }
  // Grouped list: deputies by party, with counts, each name with its photo.
  function grouped(list, r, title, note) {
    if (!list || !list.length) return '';
    const by = new Map(); for (const p of list) { const k = partiesIn(p, r).slice(-1)[0] || 'sem partido'; by.set(k, [...(by.get(k) || []), p]); }
    const groups = [...by].sort((a, b) => b[1].length - a[1].length || (a[0] < b[0] ? -1 : 1));
    return `<details class="pg-group"><summary><b>${esc(title)}</b><span>${list.length}</span><em>${groups.slice(0, 6).map(([k, ps]) => `${esc(k)} ${ps.length}`).join(' · ')}${groups.length > 6 ? ' · …' : ''}</em></summary>
      ${note ? `<p class="pg-note">${esc(note)}</p>` : ''}
      <div class="pg-parties-list">${groups.map(([k, ps]) => `<div class="pg-pgrp"><h5>${esc(k)} <span>${ps.length}</span></h5><ul>${ps.sort((a, b) => (a.name < b.name ? -1 : 1)).map((p) => `<li>${photo(p, 'pg-xs')}<span>${esc(p.name)}${p.start ? `<small>${spansText(p)}</small>` : ''}${influence(p, true)}</span></li>`).join('')}</ul></div>`).join('')}</div></details>`;
  }
  function stateSection(uf, name, r) {
    const v = V(); const s = v && v.uf && v.uf[uf]; if (!s) return '';
    const heads = [...inOffice(s.governor, r).map((p) => card(p, r, p.role || 'Governador')), ...inOffice(s.vice, r).map((p) => card(p, r, p.role || 'Vice-governador'))];
    const senators = inOffice(s.senators, r);
    const deputies = inOffice(s.federal_deputies, r);
    const [, b] = bounds(r); const electedYear = b >= '2023-02-01' ? 2022 : 2018;
    const state = (s.state_deputies || {})[electedYear] || [];
    return `<section class="pg-sec"><h3>Quem governava ${esc(name)} · ${esc(r.label)}</h3><p class="pg-lead">cargos e datas oficiais; partido na época</p>
      ${heads.length ? `<div class="pg-grid">${heads.join('')}</div>` : '<p class="pg-note">Governadores deste estado ainda não carregados.</p>'}
      ${heads.length && s.governors_curated === false ? '<p class="pg-note">Neste estado, governador e vice vêm do resultado das eleições (TSE). Trocas no cargo durante o mandato ainda não foram conferidas.</p>' : ''}
      ${senators.length ? `<h4 class="pg-h">Senadores no período</h4><div class="pg-grid sm">${senators.map((p) => card(p, r, p.role || 'Senador')).join('')}</div>` : ''}
      ${grouped(deputies, r, 'Deputados federais no período', 'Quem exerceu o mandato em algum momento do período, pela Câmara dos Deputados.')}
      ${grouped(state, r, `Deputados estaduais eleitos em ${electedYear}`, 'Eleitos segundo o TSE; suplentes que assumiram não aparecem.')}
      ${sourcesNote()}</section>`;
  }
  // D81: notes on by-elections and on cycles with nobody elected, shown when they overlap the period.
  function mayorLine(code, r) {
    const v = V(); const ms = (v && v.mayors && inOffice(v.mayors[code], r)) || [];
    const [a, b] = bounds(r); const notes = ((v && v.mayor_notes && v.mayor_notes[code]) || []).filter((n) => n.from <= b && n.to > a);
    if (!ms.length && !notes.length) return '';
    return `${ms.length ? `<div class="pg-grid sm">${ms.map((p) => card(p, r, p.role || 'Prefeito')).join('')}</div>` : ''}${notes.map((n) => `<p class="pg-note">${esc(n.text)}</p>`).join('')}`;
  }
  const sourcesNote = () => { const v = V(); return v && v.note ? `<p class="pg-note">${esc(v.note)}${v.activity_note ? ` Barra "Influência": ${esc(v.activity_note)} Para governadores, deputados estaduais e prefeitos não há fonte aberta uniforme.` : ''}</p>` : ''; };

  window.BIG = { inOffice, partiesIn, presidentLine, unionSection, stateSection, mayorLine };
})();
