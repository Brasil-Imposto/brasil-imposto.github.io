// Checks the map loader of Início (D152, L1) under a throttled network, at 1440 and 420 px.
// - The size written into the page (data-size) is the byte length of assets/bi-data.js as served.
// - Sampled every 50 ms, the percentage only rises, moves through at least 10 values, never reads 100 before
//   body[data-ready="1"], and the card is gone once the page is ready; at the end the bytes received equal the size.
// - A failed download shows "Não foi possível carregar os dados." and "Tentar de novo", and the retry loads the page.
// - With no size in the page the card shows no number at all, and the page still loads.
// Saves a screenshot with the card halfway (between 40% and 60%) at each width.
// Usage: node loader-check.cjs <outDir> <url> [--control]   (--control writes a wrong size into the page: must fail)
// Env: PW_CORE, CHROME_HEADLESS, CDN_MIRROR (as site-check.cjs); LC_RATE (bytes per second, default 15000000).
const fs = require('fs');
const path = require('path');

(async () => {
  const args = process.argv.slice(2), control = args.includes('--control');
  const [outDir, url] = args.filter((a) => a !== '--control');
  const rate = +(process.env.LC_RATE || 15e6);
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--no-sandbox'] });
  fs.mkdirSync(outDir, { recursive: true });
  const dataUrl = new URL('assets/bi-data.js', url).href;
  const realSize = (await (await fetch(dataUrl)).arrayBuffer()).byteLength;
  const failures = [];
  const open = async (width, { rewrite, failFirst, throttle = true } = {}) => {
    const ctx = await browser.newContext({ viewport: { width, height: 900 } });
    let failed = 0;
    await ctx.route('**/*', async (route) => {
      const u = route.request().url();
      const mirror = process.env.CDN_MIRROR && u.startsWith('https://cdn.jsdelivr.net/npm/') && path.join(process.env.CDN_MIRROR, u.slice(29).split('?')[0]);
      if (mirror) return route.fulfill({ path: mirror, contentType: mirror.endsWith('.js') ? 'text/javascript' : undefined });
      if (u === dataUrl && failFirst && !failed++) return route.abort('connectionreset');
      if (rewrite && route.request().resourceType() === 'document') { const res = await route.fetch(); return route.fulfill({ response: res, body: rewrite(await res.text()) }); }
      return route.continue();
    });
    const page = await ctx.newPage();
    const errors = []; page.on('pageerror', (e) => errors.push(e.message));
    if (throttle) {
      const cdp = await ctx.newCDPSession(page);
      await cdp.send('Network.enable');
      await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 20, downloadThroughput: rate, uploadThroughput: 1e6 });
    }
    await page.addInitScript(() => {
      window.__samples = [];
      const tick = () => {
        const c = document.getElementById('bi-loader');
        if (c) {
          const n = c.querySelector('[data-pct]');
          window.__samples.push({ pct: n ? n.textContent.trim() : null, shown: !!c.getClientRects().length && getComputedStyle(c).display !== 'none', state: c.dataset.state, bytes: +c.dataset.bytes || 0, size: c.dataset.size, ready: document.body && document.body.dataset.ready === '1' });
        } else window.__samples.push({ gone: true, ready: !!(document.body && document.body.dataset.ready === '1') });
      };
      setInterval(tick, 50);
    });
    return { ctx, page, errors };
  };
  const control_rewrite = (html) => html.replace(/data-size="(\d+)"/, (m, n) => `data-size="${Math.round(n / 2)}"`);

  for (const width of [1440, 420]) {
    const bad = [];
    const { ctx, page, errors } = await open(width, control ? { rewrite: control_rewrite } : {});
    await page.goto(url, { waitUntil: 'commit', timeout: 180000 });
    let shot = false;
    for (let i = 0; i < 6000; i++) {
      const s = await page.evaluate(() => { const c = document.getElementById('bi-loader'); const n = c && c.querySelector('[data-pct]'); return { pct: n ? parseInt(n.textContent, 10) : NaN, ready: document.body && document.body.dataset.ready === '1' }; }).catch(() => ({}));
      if (!shot && s.pct >= 40 && s.pct <= 60) { await page.screenshot({ path: path.join(outDir, `loader-halfway-${width}${control ? '-control' : ''}.png`) }); shot = true; }
      if (s.ready) break;
      await page.waitForTimeout(40);
    }
    await page.waitForTimeout(900);
    const sm = await page.evaluate(() => window.__samples);
    const size = +(sm.find((x) => x.size) || {}).size;
    const nums = sm.filter((x) => x.pct !== null && x.pct !== undefined && x.pct !== '').map((x) => parseInt(x.pct, 10));
    if (size !== realSize) bad.push(`data-size ${size} is not the file's ${realSize} bytes`);
    for (let i = 1; i < nums.length; i++) if (nums[i] < nums[i - 1]) { bad.push(`went back from ${nums[i - 1]} to ${nums[i]}`); break; }
    const early = sm.find((x) => !x.ready && parseInt(x.pct, 10) >= 100);
    if (early) bad.push('100% before the page was ready');
    const distinct = new Set(nums).size;
    if (distinct < 10) bad.push(`only ${distinct} distinct percentages`);
    const last = sm[sm.length - 1];
    if (!last.gone && last.shown) bad.push('the card is still shown after the page is ready');
    const loaded = sm.filter((x) => x.bytes).pop();
    if (!loaded || loaded.bytes !== realSize) bad.push(`bytes received ${loaded && loaded.bytes}, file ${realSize}`);
    if (sm.some((x) => x.state === 'unknown')) bad.push('the size was treated as unknown');
    if (!shot) bad.push('no sample between 40% and 60% to photograph');
    if (errors.length) bad.push(`page errors: ${errors.slice(0, 2).join(' | ')}`);
    console.log(`${bad.length ? 'FAIL' : 'PASS'} ${width}px progress: ${nums.length} samples, ${distinct} distinct, ${nums[0]} → ${nums[nums.length - 1]}${bad.length ? ': ' + bad.join('; ') : ''}`);
    if (bad.length) failures.push(width);
    await ctx.close();
  }
  if (!control) {
    { // a failed download, then the retry
      const bad = [];
      const { ctx, page, errors } = await open(1440, { failFirst: true, throttle: false });
      await page.goto(url, { waitUntil: 'commit', timeout: 180000 });
      await page.waitForSelector('#bi-loader[data-state="error"]', { timeout: 60000 }).catch(() => bad.push('no error state'));
      const t = await page.evaluate(() => document.getElementById('bi-loader').innerText).catch(() => '');
      if (!/Não foi possível carregar os dados\./.test(t) || !/Tentar de novo/.test(t)) bad.push(`error card text: ${t.replace(/\s+/g, ' ')}`);
      await page.screenshot({ path: path.join(outDir, 'loader-error-1440.png') });
      await page.click('#bi-loader button').catch(() => bad.push('no retry button'));
      await page.waitForSelector('body[data-ready="1"]', { timeout: 180000 }).catch(() => bad.push('the retry did not load the page'));
      if (errors.length) bad.push(`page errors: ${errors.slice(0, 2).join(' | ')}`);
      console.log(`${bad.length ? 'FAIL' : 'PASS'} failed download and retry${bad.length ? ': ' + bad.join('; ') : ''}`);
      if (bad.length) failures.push('retry');
      await ctx.close();
    }
    { // no size in the page: no number, ever
      const bad = [];
      const { ctx, page, errors } = await open(1440, { rewrite: (h) => h.replace(/ data-size="\d+"/, ''), throttle: true });
      await page.goto(url, { waitUntil: 'commit', timeout: 180000 });
      await page.waitForSelector('body[data-ready="1"]', { timeout: 300000 }).catch(() => bad.push('the page did not load'));
      const sm = await page.evaluate(() => window.__samples);
      const shown = sm.filter((x) => x.pct && /\d/.test(x.pct));
      if (shown.length) bad.push(`a number was shown: ${shown[0].pct}`);
      if (!sm.some((x) => x.shown)) bad.push('the card never showed');
      if (errors.length) bad.push(`page errors: ${errors.slice(0, 2).join(' | ')}`);
      console.log(`${bad.length ? 'FAIL' : 'PASS'} size unknown: no number${bad.length ? ': ' + bad.join('; ') : ''}`);
      if (bad.length) failures.push('unknown');
      await ctx.close();
    }
  }
  await browser.close();
  if (control) console.log(failures.length === 2 ? 'control: both runs with a wrong size failed, as they must' : `CONTROL BLIND: ${2 - failures.length} of 2 runs passed`);
  process.exitCode = control ? (failures.length === 2 ? 0 : 1) : (failures.length ? 1 : 0);
})();
