// Checks published pages as a visitor gets them: every request answers below 400, no page error and no console error,
// the ready flag (body[data-ready="1"]) set, and no horizontal scroll, at each width; saves a screenshot of each.
// Usage: node site-check.cjs <outDir> <url> [<url> ...] [--control]
// --control breaks each page on purpose (a script error, a request that answers 404 and an element wider than the
//   screen); every page must then fail, or the check is blind.
// Env: PW_CORE (path to playwright-core), CHROME_HEADLESS (chrome-headless-shell binary), SC_WIDTHS (default 1440,420),
//      CDN_MIRROR (folder with the pinned npm packages, served in place of cdn.jsdelivr.net where the network blocks it).
// A request the local network refuses (ERR_TUNNEL_CONNECTION_FAILED) is listed apart as not verified, never as a pass.
const fs = require('fs');
const path = require('path');

(async () => {
  const args = process.argv.slice(2), control = args.includes('--control');
  const [outDir, ...urls] = args.filter((a) => a !== '--control');
  const widths = (process.env.SC_WIDTHS || '1440,420').split(',').map(Number);
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_HEADLESS,
    args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--no-sandbox'],
  });
  fs.mkdirSync(outDir, { recursive: true });
  let failures = 0;
  try {
    for (const url of urls) {
      for (const width of widths) {
        const r = { url, width, requests: 0, bad: [], unverified: [], errors: [], ready: false, scroll: null, shot: null };
        const ctx = await browser.newContext({ viewport: { width, height: 900 } });
        await ctx.route('**/*', (route) => {
          const u = route.request().url();
          const mirror = process.env.CDN_MIRROR && u.startsWith('https://cdn.jsdelivr.net/npm/') && path.join(process.env.CDN_MIRROR, u.slice(29).split('?')[0]);
          if (mirror) return route.fulfill({ path: mirror, contentType: mirror.endsWith('.js') ? 'text/javascript' : undefined });
          return route.continue();
        });
        const page = await ctx.newPage();
        page.on('response', (res) => { r.requests++; if (res.status() >= 400) r.bad.push(`${res.status()} ${res.url()}`); });
        page.on('requestfailed', (q) => {
          const e = q.failure()?.errorText || '';
          if (/ERR_TUNNEL_CONNECTION_FAILED|ERR_PROXY/.test(e)) r.unverified.push(new URL(q.url()).host);
          else { r.requests++; r.bad.push(`${e} ${q.url()}`); }
        });
        page.on('pageerror', (e) => r.errors.push(`pageerror: ${e.message}`));
        page.on('console', (m) => { if (m.type() === 'error' && !/net::ERR_TUNNEL_CONNECTION_FAILED|net::ERR_PROXY/.test(m.text())) r.errors.push(`console: ${m.text()}`); });
        if (control) {
          await page.addInitScript(() => document.addEventListener('DOMContentLoaded', () => {
            const wide = document.createElement('div'); wide.style.cssText = 'width:3000px;height:4px'; document.body.append(wide);
            const img = document.createElement('img'); img.src = 'assets/planted-missing-file.png'; document.body.append(img);
            setTimeout(() => { throw new Error('planted error'); }, 0);
          }));
        }
        try {
          await page.goto(url, { waitUntil: 'load', timeout: 180000 });
          await page.waitForSelector('body[data-ready="1"]', { timeout: 180000 });
          r.ready = true;
        } catch (e) { r.errors.push(`not ready: ${e.message.split('\n')[0]}`); }
        await page.waitForTimeout(2000);
        r.scroll = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth }));
        const name = `${new URL(url).pathname.replace(/^\/$/, '/index.html').split('/').pop().replace(/\.html$/, '')}-${width}${control ? '-control' : ''}.png`;
        await page.screenshot({ path: path.join(outDir, name), fullPage: false });
        r.shot = name;
        const hscroll = r.scroll.scrollWidth > r.scroll.innerWidth;
        const ok = !r.bad.length && !r.errors.length && r.ready && !hscroll;
        if (!ok) failures++;
        r.unverified = [...new Set(r.unverified)];
        console.log(`${ok ? 'PASS' : 'FAIL'} ${width}px ${url}: ${r.requests} requests, ${r.bad.length} bad, ${r.errors.length} errors, ready=${r.ready}, scrollWidth=${r.scroll.scrollWidth}/${r.scroll.innerWidth}${r.unverified.length ? `, NOT VERIFIED (blocked by this network): ${r.unverified.join(' ')}` : ''}`);
        [...r.bad, ...r.errors].slice(0, 6).forEach((x) => console.log(`   ${x.slice(0, 200)}`));
        await ctx.close();
      }
    }
  } finally { await browser.close(); }
  const total = urls.length * widths.length;
  if (control) console.log(failures === total ? `control: all ${total} broken runs failed, as they must` : `CONTROL BLIND: ${total - failures} of ${total} broken runs passed`);
  process.exitCode = control ? (failures === total ? 0 : 1) : (failures ? 1 : 0);
})();
