// A sweep of the three published pages for the interface defects of spec interface-fixes (2026-10-22), at each width:
//   hscroll  the page is wider than the window (horizontal scroll);
//   covered  a visible control (link, button, select, input), scrolled to the middle of the window, is not the element on top
//            at its centre (something covers it: the header, an overlay, a neighbour);
//   cut      a control's own text (not a cropped photo) does not fit inside it (scrollWidth past clientWidth; a select's chosen option wider than
//            its box).
// Os 3 Poderes' filter bar (.tools) is left out: it is being redesigned in its own round.
// Usage: node ui-sweep.cjs <base url of the served previews folder> [--control] [--widths=1440,420]
// --control plants one defect of each kind (a page twice the window's width, which lands under the home's 90% zoom too, a fixed box over the middle of the window, a header link
// squeezed to 12 px) and each kind must then be reported on every page and width.
// Env: PW_CORE, CHROME_HEADLESS, CDN_MIRROR (as in site-check.cjs).
const path = require('path');
const PAGES = {
  inicio: 'BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html',
  'tres-poderes': 'BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html',
  dinheiro: 'BRASIL-IMPOSTO_DESIGN_como-o-dinheiro-anda-round-1_2026-10-21.html',
};
const PLANT = `body::after { content: ''; display: block; width: 200vw; height: 1px; }
  #oc-cover { position: fixed; left: 0; right: 0; top: 35%; height: 30%; z-index: 5000; }
  .bi-header .bi-links a:first-child, .bi-brand { display: inline-block; width: 12px; overflow: hidden; white-space: nowrap; }`;

(async () => {
  const args = process.argv.slice(2), base = args.find((a) => !a.startsWith('--')).replace(/\/?$/, '/');
  const control = args.includes('--control');
  const widths = ((args.find((a) => a.startsWith('--widths=')) || '--widths=1440,1024,768,420,360').split('=')[1]).split(',').map(Number);
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox'] });
  const found = [];
  for (const w of widths) {
    for (const [key, file] of Object.entries(PAGES)) {
      const ctx = await browser.newContext({ viewport: { width: w, height: w <= 420 ? 800 : 900 } });
      await ctx.route('**/*', (r) => {
        const u = r.request().url();
        const mirror = process.env.CDN_MIRROR && u.startsWith('https://cdn.jsdelivr.net/npm/') && path.join(process.env.CDN_MIRROR, u.slice(29).split('?')[0]);
        if (mirror) return r.fulfill({ path: mirror, contentType: mirror.endsWith('.js') ? 'text/javascript' : undefined });
        return u.startsWith(base) ? r.continue() : r.abort();
      });
      const p = await ctx.newPage();
      await p.goto(base + file);
      await p.waitForSelector('body[data-ready="1"]', { timeout: 120000 });
      if (control) await p.evaluate((css) => { const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);
        const d = document.createElement('div'); d.id = 'oc-cover'; document.body.appendChild(d); }, PLANT);
      await p.waitForTimeout(400);
      const r = await p.evaluate(() => {
        const out = [], seen = new Set();
        const name = (e) => `${e.tagName.toLowerCase()}${e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/)[0] : ''} "${(e.innerText || e.value || e.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 40)}"`;
        const de = document.documentElement;
        if (de.scrollWidth > innerWidth + 1) out.push(['hscroll', `page ${de.scrollWidth}px wide in a ${innerWidth}px window`]);
        const vis = (e) => { const s = getComputedStyle(e); return e.getClientRects().length && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity !== 0 && !e.closest('[hidden], [aria-hidden="true"], .tools'); };
        const ctl = [...document.querySelectorAll('a[href], button, select, input:not([type=hidden]), [role=button]')].filter(vis);
        const canvas = document.createElement('canvas').getContext('2d');
        for (const e of ctl.slice(0, 600)) {
          const k = name(e); if (seen.has(k)) continue; seen.add(k);
          const r0 = e.getBoundingClientRect(); if (r0.width < 2 || r0.height < 2) continue;
          e.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
          // a link that wraps has one box per line; the union's centre can fall on a neighbour, so take its first line
          const r = e.getClientRects()[0], x = r.left + r.width / 2, y = r.top + r.height / 2;
          if (x >= 0 && y >= 0 && x <= innerWidth && y <= innerHeight) {
            const t = document.elementFromPoint(x, y);
            if (t && !(t === e || e.contains(t) || t.contains(e))) out.push(['covered', `${name(e)} at ${Math.round(x)},${Math.round(y)} under ${name(t)}`]);
          }
          const s = getComputedStyle(e);
          if (e.tagName === 'SELECT') {
            canvas.font = `${s.fontWeight} ${s.fontSize} ${s.fontFamily}`;
            const txt = e.options[e.selectedIndex] ? e.options[e.selectedIndex].text : '', need = canvas.measureText(txt).width + parseFloat(s.paddingLeft) + 18;
            if (need > e.clientWidth + 1) out.push(['cut', `${name(e)}: "${txt}" needs ${Math.round(need)}px, box ${e.clientWidth}px`]);
          } else if (e.tagName !== 'INPUT' && (e.innerText || '').trim() && e.scrollWidth > e.clientWidth + 1 && s.display !== 'inline') {
            out.push(['cut', `${name(e)}: text ${e.scrollWidth}px in a ${e.clientWidth}px box`]);
          }
        }
        scrollTo({ top: 0, behavior: 'instant' });
        return out;
      });
      for (const [kind, what] of r) found.push({ w, key, kind, what });
      await ctx.close();
    }
  }
  await browser.close();
  for (const f of found) console.log(`${f.kind.padEnd(7)} ${f.w}px ${f.key}: ${f.what}`);
  console.log(`${found.length} findings on ${Object.keys(PAGES).length} pages x ${widths.length} widths${control ? ' (control run)' : ''}`);
  if (control) {
    const miss = [];
    for (const w of widths) for (const key of Object.keys(PAGES)) for (const kind of ['hscroll', 'covered', 'cut'])
      if (!found.some((f) => f.w === w && f.key === key && f.kind === kind)) miss.push(`${kind} ${w}px ${key}`);
    console.log(miss.length ? `BROKEN CONTROL: not caught: ${miss.join(', ')}` : 'control: every planted defect caught on every page and width');
    process.exit(miss.length ? 1 : 0);
  }
  process.exit(found.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
