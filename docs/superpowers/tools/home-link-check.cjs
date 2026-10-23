// Every link to Início lands on the site's root, and the old Início address forwards there (D160), measured on a served copy of
// the assembled _site (python3 -m http.server), never file://.
//   links    from each of the three pages, a click on the header logo, "Início" in the header, the footer logo (1440 px) and
//            "Início" in the phone menu (420 px) lands on "/" with no file name in the address; every navigation the click starts
//            is recorded, so a link left on the old name fails even though the forward would take it to "/" in the end
//   rede     "Rede do dinheiro (prévia)" in the footer of Os 3 Poderes and Como o dinheiro anda lands on "/#rede"
//   forward  the old address with a query and a hash, /<old name>?open=SC#rede, ends at /?open=SC#rede with the SC modal open
//   noscript with JavaScript off, the old address still ends at "/" (the meta refresh)
// Usage: node home-link-check.cjs <base url of the served _site> [--control]
// --control plants a failure for every check: the footer logo of each page and "Início" in the header and the phone menu left
// on the old name, the Rede link too, a forwarding page that drops the hash, and one without its fallback; every check must
// then fail, or the probe is blind.
// Env: PW_CORE (path to playwright-core), CHROME_HEADLESS (chrome-headless-shell binary), CDN_MIRROR (optional, as site-check.cjs).
const path = require('path');
const OLD = 'BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html';
const PAGES = { inicio: '', 'tres-poderes': 'BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html',
  dinheiro: 'BRASIL-IMPOSTO_DESIGN_como-o-dinheiro-anda-round-1_2026-10-21.html' };
const LINKS = [
  { name: 'header logo', width: 1440, sel: '.bi-header a.bi-brand' },
  { name: 'header Início', width: 1440, sel: '.bi-links a', text: 'Início' },
  { name: 'footer logo', width: 1440, sel: '.bi-footer a.bi-brand' },
  { name: 'phone menu Início', width: 420, menu: true, sel: '.bi-sheet a', text: 'Início' },
];

(async () => {
  const args = process.argv.slice(2), base = args.find((a) => !a.startsWith('--')).replace(/\/?$/, '/');
  const control = args.includes('--control'), root = new URL(base).pathname;
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox'] });
  const rows = [];
  const report = (check, where, ok, detail) => rows.push({ check, where, ok, detail });

  // the control rewrites the served pages on their way to the browser: the old name back in the links, a broken forward
  const plant = async (ctx, opts = {}) => {
    await ctx.route('**/*', async (route) => {
      const req = route.request(), u = req.url();
      // the map's libraries come from jsDelivr; where that host is blocked, CDN_MIRROR serves the same files (as site-check.cjs)
      const mirror = process.env.CDN_MIRROR && u.startsWith('https://cdn.jsdelivr.net/npm/') && path.join(process.env.CDN_MIRROR, u.slice(29).split('?')[0]);
      if (mirror) return route.fulfill({ path: mirror, contentType: mirror.endsWith('.js') ? 'text/javascript' : undefined });
      if (!control || req.resourceType() !== 'document') return route.continue();
      const res = await route.fetch(), url = new URL(req.url());
      let body = await res.text();
      if (url.pathname.endsWith('/' + OLD)) {
        body = opts.noFallback ? body.replace(/<noscript>.*?<\/noscript>/s, '') : body.replace(' + location.hash', '');
      } else {
        body = body.replace(/(<footer class="bi-footer">.*?<a class="bi-brand" href=")\.\/"/s, `$1${OLD}"`)
          .replace(/<a href="\.\/"( aria-current="page")?>Início<\/a>/g, `<a href="${OLD}"$1>Início</a>`)
          .replace('href="./#rede"', `href="${OLD}#rede"`);
      }
      return route.fulfill({ response: res, body, headers: { ...res.headers(), 'content-length': String(Buffer.byteLength(body)) } });
    });
  };

  const visits = (page) => {
    const seen = [];
    page.on('request', (r) => { if (r.isNavigationRequest() && r.frame() === page.mainFrame()) seen.push(r.url()); });
    return seen;
  };

  for (const [key, file] of Object.entries(PAGES)) {
    for (const l of LINKS) {
      const ctx = await browser.newContext({ viewport: { width: l.width, height: 900 } });
      await plant(ctx);
      const page = await ctx.newPage();
      await page.goto(base + file, { waitUntil: 'load' });
      await page.waitForTimeout(400);
      if (l.menu) { await page.click('.bi-menu-btn'); await page.waitForTimeout(200); }
      const seen = visits(page);
      const a = l.text ? page.locator(l.sel, { hasText: l.text }).first() : page.locator(l.sel).first();
      await a.scrollIntoViewIfNeeded();
      await a.click();
      await page.waitForLoadState('load'); await page.waitForTimeout(1200);
      const u = new URL(page.url()), bad = seen.filter((s) => s.includes('.html'));
      const ok = u.pathname === root && u.search === '' && seen.length > 0 && bad.length === 0;
      report('links', `${key} ${l.name} ${l.width}px`, ok, ok ? u.pathname : `ended at ${u.pathname}${u.search}${u.hash}, went through ${seen.join(' > ') || 'nothing'}`);
      await ctx.close();
    }
    if (file) {
      const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
      await plant(ctx);
      const page = await ctx.newPage();
      await page.goto(base + file, { waitUntil: 'load' });
      const seen = visits(page);
      const a = page.locator('.bi-footer a[data-here]');
      await a.scrollIntoViewIfNeeded(); await a.click();
      await page.waitForLoadState('load'); await page.waitForTimeout(1200);
      const u = new URL(page.url()), ok = u.pathname === root && u.hash === '#rede' && !seen.some((s) => s.includes('.html'));
      report('rede', `${key} footer Rede do dinheiro`, ok, ok ? `${u.pathname}${u.hash}` : `ended at ${u.pathname}${u.hash}, went through ${seen.join(' > ')}`);
      await ctx.close();
    }
  }

  for (const width of [1440, 420]) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 } });
    await plant(ctx);
    const page = await ctx.newPage();
    await page.goto(`${base}${OLD}?open=SC#rede`, { waitUntil: 'load' });
    await page.waitForURL((u) => !u.pathname.endsWith('.html'), { timeout: 8000 }).catch(() => {});
    await page.waitForLoadState('load');
    await page.waitForSelector('body[data-ready="1"]', { timeout: 180000 }).catch(() => {});   // Início's map renders before ?open= runs
    await page.waitForTimeout(1500);
    const u = new URL(page.url());
    const modal = await page.evaluate(() => {
      const panel = document.querySelector('.modal-panel');
      return panel && panel.getBoundingClientRect().height > 0 ? (panel.innerText || '').slice(0, 400) : '';
    });
    const ok = u.pathname === root && u.search === '?open=SC' && u.hash === '#rede' && /Santa Catarina/.test(modal);
    report('forward', `${OLD}?open=SC#rede ${width}px`, ok, ok ? `${u.pathname}${u.search}${u.hash}, SC modal open`
      : `ended at ${u.pathname}${u.search}${u.hash}, modal: ${modal ? modal.split('\n')[0] : 'none'}`);
    await ctx.close();
  }

  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, javaScriptEnabled: false });
    await plant(ctx, { noFallback: true });
    const page = await ctx.newPage();
    await page.goto(base + OLD, { waitUntil: 'load' });
    await page.waitForURL((u) => !u.pathname.endsWith('.html'), { timeout: 5000 }).catch(() => {});
    const u = new URL(page.url()), ok = u.pathname === root;
    report('noscript', `${OLD} without JavaScript`, ok, `ended at ${u.pathname}`);
    await ctx.close();
  }
  await browser.close();

  for (const r of rows) console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.check} ${r.where}: ${r.detail}`);
  const failed = rows.filter((r) => !r.ok).length;
  if (control) {
    console.log(failed === rows.length ? `control: all ${rows.length} planted failures caught` : `BROKEN CONTROL: ${rows.length - failed} of ${rows.length} still pass`);
    process.exit(failed === rows.length ? 0 : 1);
  }
  console.log(`${rows.length - failed} of ${rows.length} pass`);
  process.exit(failed ? 1 : 0);
})();
