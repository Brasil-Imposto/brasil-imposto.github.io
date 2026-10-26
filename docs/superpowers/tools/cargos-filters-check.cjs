// The filters drawer of the cargos list on Os 3 Poderes, driven with real clicks (spec filtros-cargos, D187). For each width:
//   closed  at load the drawer and its backdrop are hidden and the list opens by Nome (A a Z);
//   open    the Filtros tab opens the drawer, focus lands on its close button, and that button is the element at its own centre
//           (nothing, the site header included, covers it);
//   orders  each of the eight orders puts the first 24 cards in order by the value it names (names compared here, in Node, not
//           in the page); "Menor total por mês" opens with José Nobre Guimarães at R$ 0 showing the "parcial" chip;
//   filter  Estado SC: the tab shows 1, "Ver N pessoas" says the list's number, and after closing a tag "SC" sits under the bar;
//           its x removes the filter (722 people again, no number on the tab);
//   close   Escape, the backdrop, the x and "Ver N pessoas" each close it, and focus returns to the Filtros tab;
//   lock    while it is open a wheel turn over the backdrop does not scroll the page;
//   fit     no horizontal scroll, and no control in the open drawer cuts its text.
// Usage: node cargos-filters-check.cjs <base url of the served previews folder> [--control] [--widths=1440,420]
// --control plants a failure for every check (the drawer shown while hidden, the drawer under the header and at the window's
// top but above its backdrop, so the clicks still land on its controls, every sort of the list reversed, the tab's number frozen, focus() disabled, Escape swallowed, the page left free to
// scroll, a control too narrow for its text) and must then report every check as FAIL; a check that still passes is blind.
// Env: PW_CORE (path to playwright-core), CHROME_HEADLESS (chrome-headless-shell binary).
const PAGE = 'os-3-poderes.html';
const PLANT = `.fdrawer[hidden], .fback[hidden] { display:flex !important; } .fdrawer { z-index:999 !important; top:0 !important; bottom:auto !important; } .fback { z-index:998 !important; }
  html, body { overflow:visible !important; } .fdrawer select { width:60px !important; }`;
const ORDERS = [['name', true, 'name', 'asc'], ['name', false, 'name', 'desc'], ['total', true, 'total', 'desc'], ['total', false, 'total', 'asc'],
  ['own', true, 'own', 'desc'], ['own', false, 'own', 'asc'], ['ceap', true, 'ceap', 'desc'], ['ceap', false, 'ceap', 'asc']];
const plain = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const inOrder = (xs, dir, cmp = (a, b) => a - b) => xs.every((v, i) => i === 0 || (dir === 'asc' ? cmp(xs[i - 1], v) <= 0 : cmp(xs[i - 1], v) >= 0));
if (inOrder([3, 2, 1], 'asc') || !inOrder([1, 2, 2], 'asc') || inOrder(['b', 'a'], 'asc', (a, b) => a.localeCompare(b))) throw new Error('the order check is blind');

(async () => {
  const args = process.argv.slice(2), base = args.find((a) => !a.startsWith('--')).replace(/\/?$/, '/');
  const control = args.includes('--control');
  const widths = ((args.find((a) => a.startsWith('--widths=')) || '--widths=1440,1024,768,420,360').split('=')[1]).split(',').map(Number);
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox'] });
  const rows = [];
  const report = (w, check, ok, detail = '') => rows.push({ w, check, ok: !!ok, detail });
  for (const w of widths) {
    const ctx = await browser.newContext({ viewport: { width: w, height: w <= 420 ? 800 : 900 } });
    await ctx.route('**/*', (r) => (r.request().url().startsWith(base) ? r.continue() : r.abort()));
    if (control) {
      await ctx.addInitScript((css) => {
        HTMLElement.prototype.focus = function () {};
        addEventListener('keydown', (e) => { if (e.key === 'Escape') e.stopImmediatePropagation(); }, true);
        const sort = Array.prototype.sort; Array.prototype.sort = function (c) { const r = sort.call(this, c); return c && this.length > 100 ? r.reverse() : r; };
        document.addEventListener('DOMContentLoaded', () => {
          const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);
          const fn = document.querySelector('[data-fn]');
          if (fn) new MutationObserver(() => { if (fn.textContent !== '7') fn.textContent = '7'; }).observe(fn, { childList: true, characterData: true, subtree: true });
        });
        const keep = setInterval(() => { if (document.body) document.body.style.setProperty('overflow', 'visible', 'important'); }, 50);
        setTimeout(() => clearInterval(keep), 60000);
      }, PLANT);
    }
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(String(e)));
    await p.goto(base + PAGE); await p.waitForSelector('body[data-ready="1"]', { timeout: 120000 }); await p.waitForTimeout(300);
    const cards = () => p.$$eval('[data-grid] [data-card]', (cs) => cs.map((c) => ({ name: c.querySelector('strong').textContent, total: +c.dataset.total,
      own: +c.dataset.own, ceap: c.dataset.ceap === '' ? null : +c.dataset.ceap, chip: [...c.querySelectorAll('.chip')].some((x) => x.textContent.trim() === 'parcial') })));
    const count = () => p.$eval('[data-count] b', (b) => +b.textContent.replace(/\D/g, ''));
    const isOpen = () => p.$eval('[data-fdrawer]', (d) => getComputedStyle(d).display !== 'none' && d.getBoundingClientRect().height > 0);
    const focusOn = (sel) => p.evaluate((s) => document.activeElement === document.querySelector(s), sel);
    const open = async () => { if (!(await isOpen())) { await p.locator('[data-ftab]').scrollIntoViewIfNeeded(); await p.click('[data-ftab]', { force: control }); } await p.waitForTimeout(150); };
    // closed
    const c0 = await cards();
    report(w, 'closed', !(await isOpen()) && (await p.$eval('[data-fback]', (b) => getComputedStyle(b).display === 'none'))
      && inOrder(c0.map((c) => plain(c.name)), 'asc', (a, b) => a.localeCompare(b)), `${c0.length} cards`);
    // open
    await open();
    const xOk = await p.evaluate(() => { const x = document.querySelector('[data-fx]'), r = x.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
      return cx > 0 && cy > 0 && cx < innerWidth && cy < innerHeight && x.contains(document.elementFromPoint(cx, cy)); });
    report(w, 'open', (await isOpen()) && xOk && (await focusOn('[data-fx]')), `close button clear: ${xOk}`);
    // orders
    const bad = [];
    for (const [key, first, field, dir] of ORDERS) {
      await p.click(`[data-fdrawer] [data-key="${key}"]`, { force: control });
      const pressedFirst = await p.$eval('[data-dir]', (d) => d.dataset.first === 'true');
      if (pressedFirst !== first) await p.click('[data-fdrawer] [data-dir]', { force: control });
      const cs = await cards();
      const vals = field === 'name' ? cs.map((c) => plain(c.name)) : field === 'ceap' ? cs.map((c) => (c.ceap == null || (dir === 'desc' && c.ceap === 0) ? (dir === 'asc' ? 1e12 : -1) : c.ceap)) : cs.map((c) => c[field]);
      if (!inOrder(vals, dir, field === 'name' ? (a, b) => a.localeCompare(b) : undefined)) bad.push(`${key} ${dir}`);
      // people without a cota (the Executive, the courts) come last in both directions, so the first card must have one
      if (field === 'ceap' && cs[0].ceap == null) bad.push(`${key} ${dir}: the first card has no cota`);
      if (key === 'total' && dir === 'asc' && !(cs[0].name === 'José Nobre Guimarães' && cs[0].total === 0 && cs[0].chip)) bad.push('Menor total: the first card is not José Nobre Guimarães at R$ 0 with "parcial"');
    }
    report(w, 'orders', !bad.length, bad.join('; '));
    await p.click('[data-fdrawer] [data-key="name"]', { force: control });
    // fit (drawer open)
    const fit = await p.evaluate(() => ({ x: document.documentElement.scrollWidth - innerWidth,
      cut: [...document.querySelectorAll('[data-fdrawer] select, [data-fdrawer] button, .tools button')].filter((e) => e.offsetParent && e.scrollWidth > e.clientWidth + 1).map((e) => (e.textContent || e.value).trim().slice(0, 24)) }));
    report(w, 'fit', fit.x <= 0 && !fit.cut.length, `x ${fit.x}; cut: ${fit.cut.join(', ')}`);
    // lock
    const y0 = await p.evaluate(() => scrollY); await p.mouse.move(10, w <= 620 ? 60 : 300); await p.mouse.wheel(0, 600); await p.waitForTimeout(300);
    report(w, 'lock', (await p.evaluate(() => scrollY)) === y0, `scrollY ${y0} -> ${await p.evaluate(() => scrollY)}`);
    // filter
    await p.selectOption('[data-fdrawer] [data-uf]', 'SC'); await p.waitForTimeout(100);
    const nSC = await count(), fn = await p.$eval('[data-fn]', (x) => (getComputedStyle(x).display === 'none' ? '' : x.textContent));
    const seen = await p.$eval('[data-fseen]', (b) => b.textContent);
    await p.click('[data-fseen]', { force: control }); await p.waitForTimeout(150);
    const tags = await p.$$eval('[data-active] [data-rm]', (bs) => bs.map((b) => b.textContent.trim()));
    if (tags.length) await p.click('[data-active] [data-rm="uf"]', { force: control }); await p.waitForTimeout(100);
    const nAfter = await count(), fnAfter = await p.$eval('[data-fn]', (x) => (getComputedStyle(x).display === 'none' ? '' : x.textContent));
    report(w, 'filter', nSC > 0 && nSC < 722 && fn === '1' && seen === `Ver ${nSC} pessoas` && tags.join() === 'SC' && nAfter === 722 && fnAfter === '',
      `SC ${nSC}, tab "${fn}", "${seen}", tags [${tags}], after x: ${nAfter} "${fnAfter}"`);
    // close: Escape, backdrop, x, "Ver N pessoas"
    const how = [];
    for (const [label, act] of [['Escape', () => p.keyboard.press('Escape')], ['fundo', () => p.mouse.click(8, w <= 620 ? 40 : 400)],
      ['x', () => p.click('[data-fx]', { force: control })], ['Ver', () => p.click('[data-fseen]', { force: control })]]) {
      await open(); await act(); await p.waitForTimeout(150);
      if ((await isOpen()) || !(await focusOn('[data-ftab]'))) how.push(label);
    }
    report(w, 'close', !how.length, how.length ? `failed: ${how.join(', ')}` : '');
    if (errs.length) report(w, 'errors', false, errs.slice(0, 2).join(' | '));
    await ctx.close();
  }
  await browser.close();
  for (const r of rows) console.log(`${r.ok ? 'ok  ' : 'FAIL'} ${String(r.w).padEnd(5)} ${r.check.padEnd(7)} ${r.detail}`);
  const fails = rows.filter((r) => !r.ok).length;
  console.log(control ? `control: ${fails} of ${rows.length} checks failed (every one must)` : `${rows.length - fails} of ${rows.length} checks pass`);
  process.exit(control ? (fails === rows.length ? 0 : 1) : (fails ? 1 : 0));
})().catch((e) => { console.error(e); process.exit(2); });
