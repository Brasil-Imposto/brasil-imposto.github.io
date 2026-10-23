// The Apoie button and its modal (spec apoie), measured as a visitor meets them, on a build with data/support.json turned on.
// For each page and width:
//   header   the header fits the window: nothing in it passes the right edge, the button and Menu do not overlap
//   top      with the modal open, the close button's centre is inside the window and is the topmost element there
//   bottom   the same after the panel is scrolled to its end (the close button stays pinned)
//   hscroll  no horizontal scroll: on the page (measured before the modal opens, since it locks the page) and inside the panel,
//            in every view and with every coin
//   views    each card opens its focused view, the only view displayed (computed display), and Voltar comes back
//   coins    each coin button displays only its own panel (computed display, not the hidden attribute), with its networks:
//            BTC 1, ETH 1, SOL 1, USDT 4, USDC 3, XRP 1, BNB 1
//   escape   Escape closes the modal
//   focus    after closing, the focus is back on the Apoie button
//   outside  a click outside the panel closes it
// Usage: node apoie-check.cjs <base url of a served test build> [--control] [--widths=1440,420,320]
// --control plants a failure for every check (the hidden coin panels and views displayed, the close button not pinned, the
// modal under the header, a header wider than the window, Escape swallowed, focus() disabled, the backdrop not clickable);
// every check must then fail, or the probe is blind.
// Env: PW_CORE (path to playwright-core), CHROME_HEADLESS (chrome-headless-shell binary).
const PAGES = ['BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html', 'BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html',
  'BRASIL-IMPOSTO_DESIGN_como-o-dinheiro-anda-round-1_2026-10-21.html'];
const NETWORKS = { BTC: 1, ETH: 1, SOL: 1, USDT: 4, USDC: 3, XRP: 1, BNB: 1 };
const PLANT = `
  .bi-apoie .bi-ap-coin.bi-ap-coin, .bi-apoie .bi-ap-view.bi-ap-view { display: block !important; }
  .bi-ap-top { position: static !important; }
  .bi-apoie { z-index: 500 !important; }
  .bi-end { min-width: 150vw !important; }
  .bi-ap-coins { min-width: 150vw !important; }
  .bi-ap-backdrop { pointer-events: none !important; }`;

(async () => {
  const args = process.argv.slice(2), base = args.find((a) => !a.startsWith('--')).replace(/\/?$/, '/');
  const control = args.includes('--control');
  const widths = ((args.find((a) => a.startsWith('--widths=')) || '--widths=1440,420,320').split('=')[1]).split(',').map(Number);
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox'] });
  const rows = [];
  const report = (w, page, check, ok, detail) => rows.push({ w, page, check, ok, detail });
  const shown = (p, sel) => p.$$eval(sel, (es) => es.filter((e) => getComputedStyle(e).display !== 'none').map((e) => e.dataset.view || e.dataset.coin || e.className));
  const hit = (p) => p.$eval('.bi-ap-x', (btn) => { const r = btn.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
    const inside = x >= 0 && y >= 0 && x <= innerWidth && y <= innerHeight, top = inside ? document.elementFromPoint(x, y) : null;
    return { ok: inside && !!top && (top === btn || btn.contains(top)), at: `${x.toFixed(0)},${y.toFixed(0)}`, on: top ? String(top.className || top.tagName).slice(0, 30) : 'off screen' }; });
  // clicks inside the page go through the DOM: whether a real click would reach a control is what `top` and `bottom` measure
  const tap = (p, sel) => p.$eval(sel, (e) => e.click());
  const isOpen = (p) => p.$eval('#bi-apoie', (e) => getComputedStyle(e).display !== 'none');
  for (const w of widths) {
    for (const page of PAGES) {
      const key = page.split('_')[2];
      const ctx = await browser.newContext({ viewport: { width: w, height: w <= 420 ? 800 : 900 } });
      await ctx.route('**/*', (r) => (r.request().url().startsWith(base) ? r.continue() : r.abort()));
      if (control) {
        await ctx.addInitScript((css) => {
          HTMLElement.prototype.focus = function () {};
          addEventListener('keydown', (e) => { if (e.key === 'Escape') e.stopImmediatePropagation(); }, true);
          document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s); });
        }, PLANT);
      }
      const p = await ctx.newPage();
      await p.goto(base + page);
      await p.waitForSelector('.bi-apoie-btn', { timeout: 120000 });
      await p.waitForTimeout(300);
      const h = await p.evaluate(() => {
        const hd = document.querySelector('.bi-header'), btn = document.querySelector('.bi-apoie-btn').getBoundingClientRect();
        const menu = document.querySelector('.bi-menu-btn').getBoundingClientRect(), menuShown = menu.width > 0;
        const past = [...hd.querySelectorAll('*')].filter((e) => e.getClientRects().length && e.getBoundingClientRect().right > innerWidth + 0.5).length;
        const overlap = menuShown && btn.right > menu.left + 0.5;
        return { ok: past === 0 && !overlap && btn.width > 0, detail: `${past} parts past the right edge, button and Menu ${overlap ? 'overlap' : 'apart'}` };
      });
      report(w, key, 'header', h.ok, h.detail);
      // the page is measured before the modal opens: an open modal locks the page with overflow hidden, which hides its width
      const pageWide = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      await tap(p, '.bi-apoie-btn');
      await p.waitForTimeout(250);
      const t = await hit(p);
      report(w, key, 'top', t.ok, `close button centre ${t.at}, on top there: ${t.ok ? 'the button' : t.on}`);
      await p.$eval('.bi-ap-panel', (e) => { e.scrollTop = e.scrollHeight; });
      await p.waitForTimeout(150);
      const bt = await hit(p);
      report(w, key, 'bottom', bt.ok, `after scrolling to the end: centre ${bt.at}, on top there: ${bt.ok ? 'the button' : bt.on}`);
      const hs = await p.evaluate(() => { const pn = document.querySelector('.bi-ap-panel');
        return { doc: 0, panel: pn.scrollWidth - pn.clientWidth }; });
      hs.doc = pageWide;
      // views
      const v = [];
      for (const [go, label] of [['sponsors', 'Apoiar pelo GitHub Sponsors'], ['crypto', 'Apoiar com cripto'], ['contact', 'Fale com a gente']]) {
        await p.$eval('.bi-ap-panel', (e) => { e.scrollTop = 0; });
        const btn = await p.$(`.bi-ap-view[data-view="main"] [data-go="${go}"]`);
        if (!btn) { v.push(`${go}: no button`); continue; }
        await btn.evaluate((e) => e.click()); await p.waitForTimeout(120);
        const s = await shown(p, '.bi-ap-view');
        if (!(s.length === 1 && s[0] === go)) v.push(`${label}: displayed ${JSON.stringify(s)}`);
        if (go === 'crypto') {
          const bad = [];
          for (const [coin, n] of Object.entries(NETWORKS)) {
            await tap(p, `[data-coin-btn="${coin}"]`); await p.waitForTimeout(60);
            const c = await shown(p, '.bi-ap-coin');
            const nets = await p.$$eval(`.bi-ap-coin[data-coin="${coin}"] .bi-ap-net`, (es) => es.filter((e) => e.getClientRects().length).length);
            if (!(c.length === 1 && c[0] === coin && nets === n)) bad.push(`${coin}: panels ${JSON.stringify(c)}, ${nets} networks`);
            const pn = await p.$eval('.bi-ap-panel', (e) => e.scrollWidth - e.clientWidth); hs.panel = Math.max(hs.panel, pn);
          }
          report(w, key, 'coins', bad.length === 0, bad.length ? bad.join('; ') : 'each coin alone, with its networks');
        }
        const back = await p.$('.bi-ap-back');
        if (back && await back.isVisible()) { await back.evaluate((e) => e.click()); await p.waitForTimeout(80); }
        const m = await shown(p, '.bi-ap-view');
        if (!(m.length === 1 && m[0] === 'main')) v.push(`Voltar from ${go}: displayed ${JSON.stringify(m)}`);
      }
      report(w, key, 'views', v.length === 0, v.length ? v.join('; ') : 'each focused view alone, and back');
      report(w, key, 'hscroll', hs.doc <= 0 && hs.panel <= 0, `page ${hs.doc}px, panel ${hs.panel}px past the width`);
      await p.keyboard.press('Escape'); await p.waitForTimeout(150);
      report(w, key, 'escape', !(await isOpen(p)), 'Escape');
      if (!(await isOpen(p))) { await tap(p, '.bi-apoie-btn'); await p.waitForTimeout(150); }
      await tap(p, '.bi-ap-x'); await p.waitForTimeout(150);
      const focus = await p.evaluate(() => document.activeElement && document.activeElement.classList.contains('bi-apoie-btn'));
      report(w, key, 'focus', !(await isOpen(p)) && focus, `focus on ${await p.evaluate(() => String(document.activeElement.className || document.activeElement.tagName).slice(0, 30))}`);
      await p.$eval('.bi-apoie-btn', (b) => b.click()); await p.waitForTimeout(150);
      await p.mouse.click(3, (await p.evaluate(() => innerHeight)) - 3); await p.waitForTimeout(150);
      report(w, key, 'outside', !(await isOpen(p)), 'a click at the window corner, outside the panel');
      await ctx.close();
    }
  }
  await browser.close();
  for (const r of rows) console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.w}px ${r.page} | ${r.check}: ${r.detail}`);
  const bad = rows.filter((r) => !r.ok).length;
  console.log(`${rows.length} checks, ${bad} failed${control ? ' (control run)' : ''}`);
  if (control) {
    const blind = [...new Set(rows.filter((r) => r.ok).map((r) => r.check))];
    console.log(blind.length ? `BROKEN CONTROL: checks that passed with every failure planted: ${blind.join(', ')}` : 'control: every check failed, as it must');
    process.exit(blind.length ? 1 : 0);
  }
  process.exit(bad ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
