// Text out of its box, in every state a visitor can open on a served build (D235): each page at rest, the Apoie modal, every
// person's sheet on Os 3 Poderes (opened through the page's own data-open click) and every state window on Início (?open=UF).
// Two defects, measured on the rendered page:
//   out      a box that does not scroll (overflow-x visible) whose content passes its right edge; only the innermost such box is
//            reported, so a defect inside another can hide it until the inner one is fixed: sweep again after every fix
//   stacked  a text box narrower than 1.6 em, 0 px included, holding a word of more than 3 letters, so its letters stack
// and, per state, a page wider than the window. ui-sweep.cjs measures the pages as they load; this one opens what they hide.
// Usage: node overflow-check.cjs <base url of a served build> [--control] [--widths=1440,1280,1024,420] [--limit=N]
// --control plants, in every state, a box whose text cannot wrap, a word in a 9 px box and a value squeezed to 0 px by its row;
// every state must then report all three, or the probe is blind. --limit=N opens only the first N sheets (a quick control run).
// Env: PW_CORE (path to playwright-core), CHROME_HEADLESS (chrome-headless-shell), IDS (only these sheets, comma separated),
// OUT (write the full report as JSON there). Exit 1 on any defect or page that did not settle (or, with --control, a missed plant).
const fs = require('fs');
const args = process.argv.slice(2), base = args.find((a) => !a.startsWith('--')).replace(/\/?$/, '/');
const control = args.includes('--control');
const widths = ((args.find((a) => a.startsWith('--widths=')) || '--widths=1440,1280,1024,420').split('=')[1]).split(',').map(Number);
const limit = Number((args.find((a) => a.startsWith('--limit=')) || '--limit=100000').split('=')[1]);
const UFS = 'AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO'.split(' ');
const PAGES = ['index.html', 'os-3-poderes.html', 'como-o-dinheiro-anda.html', 'como-ler-o-mapa.html', 'livro-caixa.html'];
const MEASURE = ({ rootSel, plant }) => {
  const root = document.querySelector(rootSel) || document.body;
  if (plant) {
    const d = document.createElement('div'); d.id = 'oc-plant';
    d.innerHTML = '<div style="width:120px"><span style="display:inline-block;white-space:nowrap">texto plantado que nao cabe na caixa de jeito nenhum</span></div>'
      + '<div style="width:9px;overflow-wrap:anywhere">publicado</div>'
      + '<div style="display:flex;width:60px"><span style="flex:none">rotulo longo demais</span><b style="min-width:0;overflow-wrap:anywhere">publicado</b></div>';
    root.appendChild(d);
  }
  const path = (el) => { const p = []; for (let e = el; e && e !== document.body && p.length < 4; e = e.parentElement) p.unshift(e.tagName.toLowerCase() + (e.classList.length ? '.' + [...e.classList].slice(0, 2).join('.') : '')); return p.join(' > '); };
  const flagged = [];
  for (const el of root.querySelectorAll('*')) {
    if (el.closest('svg, canvas, script, style, noscript')) continue;
    if (!el.getClientRects().length) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'inline' || cs.display === 'contents') continue;
    const r = el.getBoundingClientRect(); if (r.width < 1 && r.height < 1) continue;   // a box squeezed to 0 px wide still counts
    if (r.width >= 1 && cs.overflowX === 'visible' && el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 2) flagged.push({ el, kind: 'out', px: el.scrollWidth - el.clientWidth });
    const own = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join('').trim();
    const fsz = parseFloat(cs.fontSize);
    if (own.replace(/\s/g, '').length > 3 && r.width < fsz * 1.6 && (r.height > fsz * 3 || el.scrollHeight > fsz * 3)) flagged.push({ el, kind: 'stacked', px: Math.round(r.width) });
  }
  const outs = flagged.filter((f) => f.kind === 'out');
  const keep = flagged.filter((f) => f.kind === 'stacked' || !outs.some((o) => o !== f && f.el.contains(o.el)));
  return { doc: document.documentElement.scrollWidth - innerWidth,
    items: keep.map((f) => ({ kind: f.kind, px: f.px, where: path(f.el), text: (f.el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 70), planted: !!f.el.closest('#oc-plant') })) };
};
(async () => {
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
  const rows = [], states = [], unsettled = [];
  const record = (w, page, state, res) => {
    states.push({ w, page, state, doc: res.doc, planted: res.items.filter((i) => i.planted).map((i) => i.kind) });
    for (const i of res.items) if (!i.planted) rows.push({ w, page, state, ...i });
  };
  // the page's own ready signal: Início's loading line is gone (about 25 s under software WebGL), then the animations settle
  const settle = async (p, label) => {
    const ok = await p.waitForFunction(() => !document.body.innerText.includes('Carregando os dados oficiais'), null, { timeout: 45000 }).then(() => true, () => false);
    if (!ok) unsettled.push(label);
    await p.waitForTimeout(1200);
  };
  for (const w of widths) {
    const ctx = await browser.newContext({ viewport: { width: w, height: w <= 420 ? 800 : 900 } });
    const p = await ctx.newPage();
    for (const page of PAGES) {
      await p.goto(base + page); await settle(p, `${w} ${page}`);
      record(w, page, 'rest', await p.evaluate(MEASURE, { rootSel: 'body', plant: control }));
      if (await p.$('.bi-apoie-btn')) {
        await p.$eval('.bi-apoie-btn', (b) => b.click()); await p.waitForTimeout(300);
        record(w, page, 'apoie:main', await p.evaluate(MEASURE, { rootSel: '.bi-ap-panel', plant: control }));
        await p.keyboard.press('Escape'); await p.waitForTimeout(150);
      }
    }
    await p.goto(base + 'os-3-poderes.html'); await settle(p, `${w} sheets`);
    const only = process.env.IDS ? process.env.IDS.split(',') : null;
    const ids = (await p.evaluate(() => window.TP3.people.map((x) => x.id))).filter((id) => !only || only.includes(id)).slice(0, limit);
    for (const id of ids) {
      await p.evaluate((id) => { const a = document.createElement('button'); a.dataset.open = id; a.style.display = 'none'; document.body.appendChild(a); a.click(); a.remove(); }, id);
      let last = -1, same = 0;   // the sheet is drawn once its markup stops changing (a parliamentarian's bills arrive later)
      for (let k = 0; k < 25 && same < 2; k++) { await p.waitForTimeout(40); const h = await p.$eval('.sheet', (s) => s.innerHTML.length); same = h === last ? same + 1 : 0; last = h; }
      record(w, 'os-3-poderes.html', 'p=' + id, await p.evaluate(MEASURE, { rootSel: '.sheet', plant: control }));
      await p.keyboard.press('Escape');
    }
    for (const uf of UFS) {
      await p.goto(base + 'index.html?open=' + uf); await settle(p, `${w} open=${uf}`);
      record(w, 'index.html', 'open=' + uf, await p.evaluate(MEASURE, { rootSel: 'body', plant: control }));
    }
    await ctx.close();
    console.error(`width ${w} done: ${states.length} states so far`);
  }
  await browser.close();
  if (process.env.OUT) fs.writeFileSync(process.env.OUT, JSON.stringify({ rows, states, unsettled }, null, 1));
  const wide = states.filter((s) => s.doc > 0);
  for (const r of rows.slice(0, 40)) console.log(`${r.kind.padEnd(7)} ${r.w}px ${r.page} ${r.state}: ${r.px}px, ${r.where}, "${r.text}"`);
  for (const s of wide.slice(0, 20)) console.log(`wide    ${s.w}px ${s.page} ${s.state}: the page is ${s.doc}px wider than the window`);
  console.log(`${states.length} states measured; ${rows.length} defects (${rows.filter((r) => r.kind === 'out').length} out, ${rows.filter((r) => r.kind === 'stacked').length} stacked); ${wide.length} states wider than the window${control ? ' (control run)' : ''}`);
  if (unsettled.length) console.log(`NOT SETTLED (measured anyway): ${unsettled.join(', ')}`);
  if (control) {
    const blind = states.filter((s) => !(s.planted.includes('out') && s.planted.filter((k) => k === 'stacked').length >= 2));
    console.log(blind.length ? `BROKEN CONTROL: ${blind.length} states missed a plant, e.g. ${JSON.stringify(blind.slice(0, 3))}` : 'control: every plant found in every state, as it must');
    process.exit(blind.length ? 1 : 0);
  }
  process.exit(rows.length || wide.length || unsettled.length ? 1 : 0);
})().catch((e) => { console.error('ERR', e.message); process.exit(2); });
