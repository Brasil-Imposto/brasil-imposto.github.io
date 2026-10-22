// Counts what "Os 3 Poderes" still shows as not collected (D143: nothing stays "a coletar" in v1): the text "a coletar" and
// the "?" status mark, in the tree (both modes) and in the sheet of every person.
// Usage: node tres-poderes-unknown-probe.cjs <page.html | https://url> [--control]
// A URL is opened as served (the published site); requests to its own origin are allowed, the rest refused as with a file.
// The "?" mark means "não publicado" (the legend says so); "a coletar" must count 0 everywhere.
// --control removes one senator's office data before the page reads it; that sheet must then show one more "?" mark than
// the real run, so a control run with the same count as the real one means the probe is blind.
// Env: PW_CORE (path to playwright-core), CHROME_HEADLESS (chrome-headless-shell binary), VT_WIDTH (default 1440).
const path = require('path');

(async () => {
  const pagePath = process.argv[2], control = process.argv.includes('--control');
  const origin = /^https?:\/\//.test(pagePath) ? new URL(pagePath).origin : null;
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox'] });
  const errors = [];
  try {
    const ctx = await browser.newContext({ viewport: { width: +(process.env.VT_WIDTH || 1440), height: 900 } });
    await ctx.route('**/*', (r) => { const u = r.request().url(); return u.startsWith('file:') || (origin && u.startsWith(origin)) ? r.continue() : r.abort(); });
    const page = await ctx.newPage();
    page.on('pageerror', (e) => errors.push(e.message));
    if (control) {
      await page.addInitScript(() => {
        let v;
        Object.defineProperty(window, 'TP3', { configurable: true, get: () => v, set: (d) => {
          const s = d.people.find((p) => p.house === 'senado' && p.office);
          s.office = null; window.__planted = s.id; v = d;
        } });
      });
    }
    await page.goto(origin ? pagePath : 'file://' + path.resolve(pagePath));
    await page.waitForSelector('body[data-ready="1"]', { timeout: 120000 });
    if (await page.evaluate(() => document.visibilityState) !== 'visible') throw new Error('page not visible');
    const count = () => page.evaluate(() => {
      const vis = (el) => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
      const t = document.body.innerText;
      return { text: (t.match(/a coletar/gi) || []).length, marks: [...document.querySelectorAll('.st.unknown')].filter(vis).length };
    });
    const out = { tree: {}, sheets: { people: 0, with_unknown: [] } };
    for (const mode of ['cargo', 'pessoa']) {
      await page.click(`[data-mode="${mode}"]`);
      await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
      out.tree[mode] = await count();
    }
    const ids = await page.evaluate(() => window.TP3.people.map((p) => p.id));
    for (const id of ids) {
      await page.evaluate((i) => { location.hash = '#p=' + encodeURIComponent(i); }, id);
      await page.waitForFunction(() => { const b = document.querySelector('[data-sheet] [data-bl]'); return !b || !/Carregando/.test(b.textContent); }, null, { timeout: 15000 });
      const c = await page.evaluate(() => {
        const s = document.querySelector('[data-sheet]'), t = s.innerText;
        return { text: (t.match(/a coletar/gi) || []).length, marks: s.querySelectorAll('.st.unknown').length };
      });
      out.sheets.people++;
      if (c.text || c.marks) out.sheets.with_unknown.push({ id, ...c });
      await page.evaluate(() => history.replaceState(null, '', location.pathname));
    }
    if (control) out.planted = await page.evaluate(() => window.__planted);
    out.errors = errors;
    console.log(JSON.stringify(out, null, 1));
  } finally { await browser.close(); }
})();
