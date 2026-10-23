// Checks the site header (D152) on the published pages as a visitor gets them, at 1440 and 420 px, and saves screenshots.
// Per page and width: one header, 62 px tall, still at the top after scrolling; "Rede (prévia)" not in it; the current page
// marked; the header the same on every page apart from that mark. Desktop: the four links shown, no Menu. Phone: the Menu
// opens the sheet (aria-expanded, "Fechar", focus inside), Esc closes it and returns focus, a tap outside closes it.
// Footer: once per page, the last block of the page, the five links in order with "Rede do dinheiro (prévia)" once; on
// Início that link scrolls to the network card without leaving the page, elsewhere it goes to Início's #rede.
// Usage: node site-chrome-check.cjs <outDir> <url> [<url> ...] [--control | --control-footer]
// --control serves each page with the header broken (not sticky, "Rede (prévia)" added, the menu script removed): every
//   run must then fail.
// --control-footer serves each page with only the footer broken (a second Rede link and a block after the footer).
// Env: PW_CORE, CHROME_HEADLESS, CDN_MIRROR (as site-check.cjs).
const fs = require('fs');
const path = require('path');

(async () => {
  const args = process.argv.slice(2), controlFooter = args.includes('--control-footer'), control = args.includes('--control') || controlFooter;
  const [outDir, ...urls] = args.filter((a) => !a.startsWith('--control'));
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--no-sandbox'] });
  fs.mkdirSync(outDir, { recursive: true });
  let runs = 0, failed = 0;
  const shapes = new Set();
  try {
    for (const url of urls) {
      for (const width of [1440, 420]) {
        runs++;
        const bad = [];
        const ctx = await browser.newContext({ viewport: { width, height: 900 } });
        await ctx.route('**/*', async (route) => {
          const u = route.request().url();
          const mirror = process.env.CDN_MIRROR && u.startsWith('https://cdn.jsdelivr.net/npm/') && path.join(process.env.CDN_MIRROR, u.slice(29).split('?')[0]);
          if (mirror) return route.fulfill({ path: mirror, contentType: mirror.endsWith('.js') ? 'text/javascript' : undefined });
          if (control && route.request().resourceType() === 'document') {
            const res = await route.fetch(); let body = await res.text();
            if (controlFooter) {
              body = body.replace('<nav class="bi-footer-links" aria-label="Mais sobre o projeto">', '<nav class="bi-footer-links" aria-label="Mais sobre o projeto"><a href="#rede">Rede do dinheiro (prévia)</a>')
                .replace('<!-- /site-chrome:footer -->', '<!-- /site-chrome:footer --><div style="height:40px">planted</div>');
            } else {
              body = body.replace(/<script id="bi-chrome-js">[\s\S]*?<\/script>/, '')
                .replace('<nav class="bi-links" aria-label="Páginas">', '<nav class="bi-links" aria-label="Páginas"><a href="#rede">Rede (prévia)</a>')
                .replace('</head>', '<style>.bi-header{position:static!important}</style></head>');
            }
            return route.fulfill({ response: res, body });
          }
          return route.continue();
        });
        const page = await ctx.newPage();
        const errors = []; page.on('pageerror', (e) => errors.push(e.message));
        await page.goto(url, { timeout: 180000 });
        await page.waitForSelector('body[data-ready="1"]', { timeout: 180000 });
        await page.waitForTimeout(800);
        const name = `${new URL(url).pathname.replace(/^\/$/, '/index.html').split('/').pop().replace(/\.html$/, '')}-${width}${control ? '-control' : ''}`;
        const h = await page.evaluate(() => {
          const hs = document.querySelectorAll('.bi-header');
          const el = hs[0]; if (!el) return { count: 0 };
          const r = el.getBoundingClientRect();
          const cur = [...el.querySelectorAll('[aria-current="page"]')].map((a) => ({ text: a.textContent, color: getComputedStyle(a).color, shadow: getComputedStyle(a).boxShadow }));
          const links = [...el.querySelectorAll('.bi-links a')].filter((a) => a.getClientRects().length).map((a) => a.textContent);
          const btn = el.querySelector('.bi-menu-btn');
          const shape = (el.outerHTML + document.getElementById('bi-sheet').outerHTML).replace(/ aria-current="page"/g, '');
          return { count: hs.length, height: r.height, text: el.innerText, cur, links, menuShown: !!(btn && btn.getClientRects().length && getComputedStyle(btn).display !== 'none'), shape };
        });
        if (h.count !== 1) bad.push(`headers: ${h.count}`);
        else {
          shapes.add(h.shape);
          if (Math.abs(h.height - 62) > 0.5) bad.push(`height ${h.height}`);
          if (/Rede\s*\(prévia\)/.test(h.text)) bad.push('"Rede (prévia)" in the header');
          if (h.cur.length !== 1 || h.cur[0].color !== 'rgb(20, 32, 43)') bad.push(`current mark ${JSON.stringify(h.cur)}`);
          if (width === 1440 && (h.links.join('|') !== 'Início|Os 3 Poderes|Como o dinheiro anda|Código aberto' || h.menuShown)) bad.push(`desktop links ${h.links.join('|')} menu=${h.menuShown}`);
          if (width === 420 && (h.links.length || !h.menuShown)) bad.push(`phone links ${h.links.length} menu=${h.menuShown}`);
          await page.screenshot({ path: path.join(outDir, `${name}-header.png`), clip: { x: 0, y: 0, width, height: 130 } });
          await page.evaluate(() => window.scrollTo(0, 1500)); await page.waitForTimeout(300);
          const top = await page.evaluate(() => document.querySelector('.bi-header').getBoundingClientRect().top);
          if (Math.abs(top) > 0.5) bad.push(`not at the top after scrolling: ${top}`);
          await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(200);
          if (width === 420) {
            await page.click('.bi-menu-btn'); await page.waitForTimeout(250);
            const o = await page.evaluate(() => ({ hidden: document.getElementById('bi-sheet').hidden, exp: document.querySelector('.bi-menu-btn').getAttribute('aria-expanded'), label: document.querySelector('.bi-menu-btn').innerText.trim(), focusIn: document.getElementById('bi-sheet').contains(document.activeElement), links: [...document.querySelectorAll('#bi-sheet a')].map((a) => a.textContent).join('|') }));
            if (o.hidden || o.exp !== 'true' || o.label !== 'Fechar' || !o.focusIn) bad.push(`menu open ${JSON.stringify(o)}`);
            await page.screenshot({ path: path.join(outDir, `${name}-menu-open.png`), clip: { x: 0, y: 0, width, height: 420 } });
            await page.keyboard.press('Escape'); await page.waitForTimeout(150);
            const c = await page.evaluate(() => ({ hidden: document.getElementById('bi-sheet').hidden, label: document.querySelector('.bi-menu-btn').innerText.trim(), focusBtn: document.activeElement === document.querySelector('.bi-menu-btn') }));
            if (!c.hidden || c.label !== 'Menu' || !c.focusBtn) bad.push(`Esc ${JSON.stringify(c)}`);
            await page.click('.bi-menu-btn'); await page.waitForTimeout(150);
            await page.mouse.click(width / 2, 860); await page.waitForTimeout(150);
            if (!(await page.evaluate(() => document.getElementById('bi-sheet').hidden))) bad.push('a tap outside did not close the menu');
          }
        }
        const f = await page.evaluate(() => {
          const fs = document.querySelectorAll('.bi-footer'); const el = fs[0]; if (!el) return { count: 0 };
          const links = [...el.querySelectorAll('.bi-footer-links a')].map((a) => a.textContent);
          const rede = (el.innerText.match(/Rede do dinheiro \(prévia\)/g) || []).length;
          return { count: fs.length, links, rede, hasCard: !!document.getElementById('rede') };
        });
        if (f.count !== 1) bad.push(`footers: ${f.count}`);
        else {
          if (f.rede !== 1) bad.push(`"Rede do dinheiro (prévia)" ${f.rede} times in the footer`);
          if (f.links.join('|') !== 'Rede do dinheiro (prévia)|Código aberto no GitHub|Decisões do projeto|Como ajudar|Licenças') bad.push(`footer links ${f.links.join('|')}`);
          // Scrolled to the end, in viewport coordinates (zoom-proof): the footer ends at the bottom and is what is there.
          await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight)); await page.waitForTimeout(400);
          const end = await page.evaluate(() => { const r = document.querySelector('.bi-footer').getBoundingClientRect(); const at = document.elementFromPoint(innerWidth / 2, innerHeight - 2); return { gap: innerHeight - r.bottom, isFooter: !!(at && at.closest('.bi-footer')) }; });
          if (Math.abs(end.gap) > 2 || !end.isFooter) bad.push(`footer is not the last block: ${end.gap.toFixed(1)} px below it, bottom element is footer: ${end.isFooter}`);
          const fb = await page.evaluate(() => { const r = document.querySelector('.bi-footer').getBoundingClientRect(); return { y: r.top, h: r.height }; });
          await page.screenshot({ path: path.join(outDir, `${name}-footer.png`), clip: { x: 0, y: Math.max(0, fb.y - 60), width, height: Math.min(900 - Math.max(0, fb.y - 60), fb.h + 60) } });
          if (f.hasCard && !controlFooter) {
            const before = page.url();
            await page.click('.bi-footer a[data-here]'); await page.waitForTimeout(1200);
            const r = await page.evaluate(() => ({ url: location.href, top: document.getElementById('rede').getBoundingClientRect().top, inner: innerHeight, atEnd: Math.abs(scrollY - (document.documentElement.scrollHeight - innerHeight)) < 2 }));
            // the card is the last section, so the page may end before it reaches the top: it must be in view, with the page
            // scrolled as far as it goes or the card at the top, and the address the same page
            if (r.url.split('#')[0] !== before.split('#')[0] || !(r.top >= -1 && r.top < r.inner) || !(Math.abs(r.top) < 80 || r.atEnd)) bad.push(`Rede link on Início: ${JSON.stringify(r)}`);
          } else if (!f.hasCard) {
            const href = await page.evaluate(() => document.querySelector('.bi-footer a[data-here]').getAttribute('href'));
            if (href !== './#rede') bad.push(`Rede link goes to ${href}`);   // Início lives at the site's root, never at the design file's name
          }
        }
        if (errors.length) bad.push(`page errors: ${errors.slice(0, 2).join(' | ')}`);
        if (bad.length) failed++;
        console.log(`${bad.length ? 'FAIL' : 'PASS'} ${width}px ${url}${bad.length ? ': ' + bad.join('; ') : ''}`);
        await ctx.close();
      }
    }
  } finally { await browser.close(); }
  const same = shapes.size === 1;
  if (!control) console.log(same ? `header identical on the ${urls.length} pages apart from the current-page mark` : `HEADERS DIFFER: ${shapes.size} shapes`);
  if (control) console.log(failed === runs ? `control: all ${runs} broken runs failed, as they must` : `CONTROL BLIND: ${runs - failed} of ${runs} broken runs passed`);
  process.exitCode = control ? (failed === runs ? 0 : 1) : (failed || !same ? 1 : 0);
})();
