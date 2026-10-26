// The overlays and in-page jumps of the three published pages, measured as a reader meets them (spec interface-fixes,
// 2026-10-22). For each width:
//   - every overlay (Os 3 Poderes: the person sheet and the filters drawer; Início: the "Ver as contas do Brasil" modal and the home feed's detail
//     sheet), opened by clicking its button after scrolling the button into view:
//       close  the close button's centre is inside the window and document.elementFromPoint there is the button itself, and a
//              real mouse click there closes the overlay;
//       esc    Escape closes it;
//       lock   while it is open the page behind does not scroll (a wheel turn over the backdrop leaves window.scrollY alone);
//       focus  after it closes, focus is back on the button that opened it;
//   - every in-page jump (links to "#id" and the buttons that jump, such as "Ver cada um ↓"): after the jump, the target's top
//     sits below the site header's bottom edge.
// Usage: node overlay-check.cjs <base url of the served previews folder> [--control] [--widths=1440,420]
// --control plants a failure for every check (the overlays' old z-index, the feed's panel moved up to the window's top so the
// header can cover it at every width, scroll-margin-top 0, focus() disabled, Escape swallowed, the page left free to scroll) and must then report every check as FAIL; a check that still passes is a blind check.
// Env: PW_CORE (path to playwright-core), CHROME_HEADLESS (chrome-headless-shell binary), CDN_MIRROR (as in site-check.cjs).
const PAGES = {
  inicio: 'BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html',
  'tres-poderes': 'BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html',
  dinheiro: 'BRASIL-IMPOSTO_DESIGN_como-o-dinheiro-anda-round-1_2026-10-21.html',
};
const OVERLAYS = [
  { page: 'tres-poderes', name: 'ficha da pessoa', opener: '[data-grid] [data-open]', open: '[data-back]:not([hidden])', close: '[data-sheet] [data-close]' },
  { page: 'tres-poderes', name: 'gaveta dos filtros', opener: '[data-ftab]', open: '[data-fdrawer]:not([hidden])', close: '[data-fdrawer] [data-fx]' },
  { page: 'inicio', name: 'contas do Brasil', opener: '[data-open-brasil]', open: '.modal-open .modal-layer', close: '.modal-panel .close' },
  { page: 'inicio', name: 'detalhe do feed', opener: '[data-hf]', open: '.hf-sheet:not([hidden])', close: '.hf-sheet .hf-x' },
];
const PLANT = `
  .back { z-index: 40 !important; } .fdrawer, .fback { z-index: 40 !important; } .fdrawer { top: 0 !important; bottom: auto !important; } .modal-layer { z-index: 30 !important; } .hf-sheet { z-index: 60 !important; }
  .hf-panel { top: 0 !important; transform: translate(-50%, 0) !important; }
  [id] { scroll-margin-top: 0 !important; } html, body { overflow: visible !important; }`;

(async () => {
  const args = process.argv.slice(2), base = args.find((a) => !a.startsWith('--')).replace(/\/?$/, '/');
  const control = args.includes('--control');
  const widths = ((args.find((a) => a.startsWith('--widths=')) || '--widths=1440,1024,768,420,360').split('=')[1]).split(',').map(Number);
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox'] });
  const rows = [];
  const report = (w, page, what, check, ok, detail) => rows.push({ w, page, what, check, ok, detail });
  const settle = async (p) => { let last = -1, same = 0; for (let i = 0; i < 60 && same < 4; i++) { const y = await p.evaluate(() => scrollY); same = y === last ? same + 1 : 0; last = y; await p.waitForTimeout(100); } };
  const newPage = async (w, key) => {
    const ctx = await browser.newContext({ viewport: { width: w, height: w <= 420 ? 800 : 900 }, hasTouch: false });
    await ctx.route('**/*', (r) => {
      const u = r.request().url();
      const mirror = process.env.CDN_MIRROR && u.startsWith('https://cdn.jsdelivr.net/npm/') && require('path').join(process.env.CDN_MIRROR, u.slice(29).split('?')[0]);
      if (mirror) return r.fulfill({ path: mirror, contentType: mirror.endsWith('.js') ? 'text/javascript' : undefined });
      return u.startsWith(base) || u.startsWith('https://cdn.jsdelivr.net/') ? r.continue() : r.abort();
    });
    if (control) {
      await ctx.addInitScript((css) => {
        HTMLElement.prototype.focus = function () {};
        addEventListener('keydown', (e) => { if (e.key === 'Escape') e.stopImmediatePropagation(); }, true);
        document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s); });
        const keep = setInterval(() => { if (document.body) { document.body.style.setProperty('overflow', 'visible', 'important'); } }, 50);
        setTimeout(() => clearInterval(keep), 60000);
      }, PLANT);
    }
    const p = await ctx.newPage();
    await p.goto(base + PAGES[key]);
    await p.waitForSelector('body[data-ready="1"]', { timeout: 120000 });
    await p.waitForTimeout(300);
    return p;
  };
  for (const w of widths) {
    for (const o of OVERLAYS) {
      const p = await newPage(w, o.page);
      const opener = await p.$(o.opener);
      if (!opener) { report(w, o.page, o.name, 'open', false, `no ${o.opener}`); await p.context().close(); continue; }
      await opener.evaluate((e) => e.setAttribute('data-oc-opener', ''));
      const open = async () => {
        if (await p.$(o.open)) return;
        await opener.evaluate((e) => e.scrollIntoView({ block: 'center' })); await settle(p);
        await opener.click(); await p.waitForSelector(o.open, { timeout: 10000 }).catch(() => null);
        await p.waitForTimeout(600);  // let any opening animation end
      };
      await open();
      const b = await p.$eval(o.close, (btn) => { const r = btn.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
        // the centre and four points 30% of the size away from it (inside a round button too): the whole button must be on top,
        // not only its middle
        const dx = r.width * 0.3, dy = r.height * 0.3, pts = [[x, y], [x - dx, y - dy], [x + dx, y - dy], [x - dx, y + dy], [x + dx, y + dy]];
        const inside = pts.every(([a, c]) => a >= 0 && c >= 0 && a <= innerWidth && c <= innerHeight);
        const tops = inside ? pts.map(([a, c]) => document.elementFromPoint(a, c)) : [];
        const cover = tops.find((t) => !t || !(t === btn || btn.contains(t)));
        return { x, y, top: r.top, inside, hit: inside && !cover, on: !inside ? 'off screen' : cover ? (cover.className || cover.tagName).toString().slice(0, 40) : 'the button' };
      }).catch(() => null);
      if (!b) report(w, o.page, o.name, 'close', false, 'overlay did not open');
      else {
        report(w, o.page, o.name, 'close', b.hit, `button centre at ${b.x.toFixed(0)},${b.y.toFixed(0)} (top ${b.top.toFixed(0)}); on top of it: ${b.on}`);
        if (b.hit) { await p.mouse.click(b.x, b.y); await p.waitForTimeout(300); }  // a covered button is not clicked: the click would land on what covers it
        const shut = !(await p.$(o.open));
        if (b.hit && !shut) report(w, o.page, o.name, 'close', false, 'clicked, still open');
        report(w, o.page, o.name, 'focus', shut && await p.evaluate(() => !!document.activeElement && document.activeElement.hasAttribute('data-oc-opener')),
          `focus after closing on ${await p.evaluate(() => document.activeElement ? (document.activeElement.className || document.activeElement.tagName).toString().slice(0, 40) : 'none')}`);
      }
      // lock: open again; a wheel turn near the window's left edge, below the header, must not move the page
      await open();
      const header = await p.$eval('.bi-header', (h) => h.getBoundingClientRect().bottom);
      const y0 = await p.evaluate(() => scrollY);
      await p.mouse.move(3, Math.round(header + 20)); await p.mouse.wheel(0, 600); await p.waitForTimeout(300);
      const moved = (await p.evaluate(() => scrollY)) - y0;
      // a backdrop that scrolls by itself takes the wheel even when the page is free, so the page's own overflow is read too
      const held = await p.evaluate(() => [document.documentElement, document.body].some((e) => getComputedStyle(e).overflowY === 'hidden'));
      report(w, o.page, o.name, 'lock', moved === 0 && held, `page moved ${moved}px under the open overlay; page overflow ${held ? 'hidden' : 'free'}`);
      // Escape
      await open();
      await p.keyboard.press('Escape'); await p.waitForTimeout(250);
      report(w, o.page, o.name, 'esc', !(await p.$(o.open)), 'Escape');
      await p.context().close();
    }
    for (const key of Object.keys(PAGES)) {
      const p = await newPage(w, key);
      const jumps = await p.evaluate(() => {
        const vis = (e) => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden';
        const out = [];
        document.querySelectorAll('a[href^="#"]').forEach((a, i) => { const id = decodeURIComponent(a.getAttribute('href').slice(1));
          if (id && document.getElementById(id) && vis(a)) { a.setAttribute('data-oc-jump', 'a' + i); out.push({ sel: `[data-oc-jump="a${i}"]`, target: id, label: a.innerText.trim().slice(0, 30) }); } });
        document.querySelectorAll('[data-goto],[data-goto-group]').forEach((b, i) => { if (vis(b)) { b.setAttribute('data-oc-jump', 'b' + i); out.push({ sel: `[data-oc-jump="b${i}"]`, target: null, label: b.innerText.trim().slice(0, 30) }); } });
        return out;
      });
      for (const j of jumps.slice(0, 12)) {
        await p.evaluate(() => scrollTo(0, 0)); await settle(p);
        const el = await p.$(j.sel); if (!el) continue;
        await el.evaluate((e) => e.scrollIntoView({ block: 'center' })); await settle(p);
        await el.click().catch(() => null); await settle(p);
        const r = await p.evaluate((t) => { const h = document.querySelector('.bi-header').getBoundingClientRect().bottom;
          const tg = t ? document.getElementById(t) : [...document.querySelectorAll('[id]')].filter((e) => e.getClientRects().length).sort((a, b) => Math.abs(a.getBoundingClientRect().top - 70) - Math.abs(b.getBoundingClientRect().top - 70))[0];
          return tg ? { id: tg.id, top: tg.getBoundingClientRect().top, h } : null; }, j.target);
        if (r) report(w, key, `salto "${j.label}" → #${r.id}`, 'jump', r.top >= r.h - 0.5, `target top ${r.top.toFixed(1)}px, header bottom ${r.h.toFixed(1)}px`);
      }
      await p.context().close();
    }
  }
  await browser.close();
  for (const r of rows) console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.w}px ${r.page} | ${r.what} | ${r.check}: ${r.detail}`);
  const bad = rows.filter((r) => !r.ok).length;
  console.log(`${rows.length} checks, ${bad} failed${control ? ' (control run)' : ''}`);
  if (control) { const blind = rows.filter((r) => r.ok); console.log(blind.length ? `BROKEN CONTROL: ${blind.length} checks passed with every failure planted` : 'control: every check failed, as it must'); process.exit(blind.length ? 1 : 0); }
  process.exit(bad ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
