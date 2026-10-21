// Records the visible text of the platform page so a change that must not touch the screen can be proven not to.
// Usage: node visible-text-probe.cjs <page.html> <out.json>
//        node visible-text-probe.cjs --compare <a.json> <b.json>
// Env: PW_CORE (path to playwright-core, default "playwright-core"), CHROME_HEADLESS (chrome-headless-shell binary),
//      VT_WIDTH (viewport width, default 1100), VT_STATES (comma-separated subset of states, default all 27).
// Captures body text in 19 hero periods and the state panel of the 27 states in year 2026, mandate 2019-2022 and month 2025-06.
const fs = require('fs');
const path = require('path');

const HERO_PERIODS = [
  ...[2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026].map((y) => ({ mode: 'year', year: y })),
  { mode: 'mandate', mandate: '2019-2022' }, { mode: 'mandate', mandate: '2023-2026' },
  ...['2019-01', '2020-04', '2021-04', '2022-12', '2024-03', '2024-09', '2025-02', '2025-06', '2026-08'].map((m) => ({ mode: 'month', month: m })),
];
const MODAL_PERIODS = [{ mode: 'year', year: 2026 }, { mode: 'mandate', mandate: '2019-2022' }, { mode: 'month', month: '2025-06' }];
const ALLOWED = ['https://cdn.jsdelivr.net/npm/three@', 'https://cdn.jsdelivr.net/npm/3d-force-graph@', 'https://fonts.googleapis.com/', 'https://fonts.gstatic.com/'];
const key = (p) => p.mode === 'year' ? `year:${p.year}` : p.mode === 'mandate' ? `mandate:${p.mandate}` : `month:${p.month}`;

async function capture(pagePath, outPath) {
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_HEADLESS,
    args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--no-sandbox'],
  });
  const out = { page: path.basename(pagePath), texts: {}, errors: [], blocked: 0 };
  try {
    const ctx = await browser.newContext({ viewport: { width: +(process.env.VT_WIDTH || 1100), height: 900 } });
    await ctx.route('**/*', (r) => {
      const u = r.request().url();
      if (u.startsWith('file:') || ALLOWED.some((a) => u.startsWith(a))) return r.continue();
      out.blocked++; return r.abort();
    });
    const page = await ctx.newPage();
    page.on('pageerror', (e) => out.errors.push(`pageerror: ${e.message}`));
    page.on('console', (m) => { if (m.type() === 'error' && !/ERR_FAILED|net::/.test(m.text())) out.errors.push(`console: ${m.text()}`); });
    await page.goto('file://' + path.resolve(pagePath));
    await page.waitForSelector('body[data-ready="1"]', { timeout: 120000 });
    if (await page.evaluate(() => document.visibilityState) !== 'visible') throw new Error('page not visible');
    const settle = () => page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
    const base = { year: 2026, month: '2026-07', mandate: '2023-2026' };
    for (const p of HERO_PERIODS) {
      await page.evaluate((np) => window.__onPeriod(np), { ...base, ...p });
      await settle();
      out.texts[`hero:${key(p)}`] = await page.evaluate(() => document.body.innerText);
    }
    const ufs = process.env.VT_STATES ? process.env.VT_STATES.split(',') : ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'];
    for (const p of MODAL_PERIODS) {
      await page.evaluate((np) => window.__onPeriod(np), { ...base, ...p });
      for (const uf of ufs) {
        await page.evaluate((u) => window.__openState(u), uf);
        await settle();
        out.texts[`modal:${key(p)}:${uf}`] = await page.evaluate(() => (document.querySelector('.modal-panel') || {}).innerText || '');
      }
    }
  } finally {
    await browser.close();
  }
  fs.writeFileSync(outPath, JSON.stringify(out, null, 1));
  const empty = Object.entries(out.texts).filter(([, v]) => !v.trim()).map(([k]) => k);
  console.log(`captured ${Object.keys(out.texts).length} texts, ${empty.length} empty, ${out.errors.length} errors, ${out.blocked} requests blocked`);
  if (empty.length) console.log('empty:', empty.join(' '));
  out.errors.slice(0, 5).forEach((e) => console.log(e));
}

function compare(a, b) {
  const A = JSON.parse(fs.readFileSync(a, 'utf8')).texts, B = JSON.parse(fs.readFileSync(b, 'utf8')).texts;
  const keys = [...new Set([...Object.keys(A), ...Object.keys(B)])];
  const diff = keys.filter((k) => A[k] !== B[k]);
  console.log(`${keys.length} texts compared, ${diff.length} differ`);
  for (const k of diff.slice(0, 12)) {
    const x = (A[k] || '').split('\n'), y = (B[k] || '').split('\n');
    const i = x.findIndex((l, n) => l !== y[n]);
    console.log(`  ${k}: line ${i + 1}\n    a: ${(x[i] || '<none>').slice(0, 160)}\n    b: ${(y[i] || '<none>').slice(0, 160)}`);
  }
  process.exitCode = diff.length ? 1 : 0;
}

if (process.argv[2] === '--compare') compare(process.argv[3], process.argv[4]);
else capture(process.argv[2], process.argv[3]).catch((e) => { console.error(e); process.exitCode = 2; });
