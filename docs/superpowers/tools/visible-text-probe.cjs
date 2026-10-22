// Records the visible text of the platform page so a change that must not touch the screen can be proven not to.
// Usage: node visible-text-probe.cjs <page.html | https://url> <out.json> [--audit] [--plant]
//        node visible-text-probe.cjs --compare <a.json> <b.json>
// A URL is opened as served (the published site); requests to its own origin are allowed.
// --audit counts what the published site must never show (internal codes D, Q or GD, "Só na prévia", "a coletar", the
//   Apoie and Fale com a gente controls) and exits 1 when any count is above 0.
// --plant is the audit's control: it plants one of each before the page runs, so every count must come out at least 1.
// Env: PW_CORE (path to playwright-core, default "playwright-core"), CHROME_HEADLESS (chrome-headless-shell binary),
//      CDN_MIRROR (folder with the pinned npm packages, served in place of cdn.jsdelivr.net),
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

const CODE = /\b(?:GD|D|Q)\d{1,3}\b/g;
const BANNED_CONTROLS = /^(apoie|apoiar|fale com a gente)\b/i;
// What the published site must not show, counted in one captured text.
function audit(text) {
  return {
    codes: (text.match(CODE) || []).length,
    so_na_previa: (text.match(/s[óo] na pr[ée]via/gi) || []).length,
    a_coletar: (text.match(/a coletar/gi) || []).length,
  };
}

async function capture(pagePath, outPath, opts = {}) {
  const isUrl = /^https?:\/\//.test(pagePath);
  const aborted = new Set();
  const origin = isUrl ? new URL(pagePath).origin : null;
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_HEADLESS,
    args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--no-sandbox'],
  });
  const out = { page: isUrl ? pagePath : path.basename(pagePath), texts: {}, errors: [], blocked: 0, failed: [], controls: [] };
  try {
    const ctx = await browser.newContext({ viewport: { width: +(process.env.VT_WIDTH || 1100), height: 900 } });
    await ctx.route('**/*', (r) => {
      const u = r.request().url();
      // CDN_MIRROR: a folder holding the same pinned npm packages, for machines whose network blocks the CDN.
      const mirror = process.env.CDN_MIRROR && u.startsWith('https://cdn.jsdelivr.net/npm/') && path.join(process.env.CDN_MIRROR, u.slice(29).split('?')[0]);
      if (mirror) return r.fulfill({ path: mirror, contentType: mirror.endsWith('.js') ? 'text/javascript' : undefined });
      if (u.startsWith('file:') || (origin && u.startsWith(origin)) || ALLOWED.some((a) => u.startsWith(a))) return r.continue();
      out.blocked++; aborted.add(u); return r.abort();
    });
    const page = await ctx.newPage();
    page.on('pageerror', (e) => out.errors.push(`pageerror: ${e.message}`));
    page.on('console', (m) => { if (m.type() === 'error' && !/ERR_FAILED|net::/.test(m.text())) out.errors.push(`console: ${m.text()}`); });
    page.on('response', (r) => { if (r.status() >= 400) out.failed.push(`${r.status()} ${r.url()}`); });
    page.on('requestfailed', (r) => { if (!aborted.has(r.url())) out.failed.push(`failed ${r.url()} ${r.failure()?.errorText}`); });
    if (opts.plant) {
      await page.addInitScript(() => document.addEventListener('DOMContentLoaded', () => {
        const p = document.createElement('p');
        p.textContent = 'Nota plantada (D999). Só na prévia: valor a coletar.';
        const a = document.createElement('a'); a.href = '#apoie'; a.textContent = 'Apoie';
        document.body.prepend(p, a);
      }));
    }
    await page.goto(isUrl ? pagePath : 'file://' + path.resolve(pagePath));
    await page.waitForSelector('body[data-ready="1"]', { timeout: 120000 });
    if (await page.evaluate(() => document.visibilityState) !== 'visible') throw new Error('page not visible');
    out.controls = await page.evaluate((re) => {
      const rx = new RegExp(re, 'i');
      const vis = (el) => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
      return [...document.querySelectorAll('a, button, [role="button"]')].filter((el) => vis(el) && rx.test(el.textContent.trim())).map((el) => el.textContent.trim());
    }, BANNED_CONTROLS.source);
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
  if (out.failed.length) console.log(`failed requests: ${out.failed.length}`, out.failed.slice(0, 5).join(' | '));
  if (opts.audit) {
    const total = { codes: 0, so_na_previa: 0, a_coletar: 0 }, where = {};
    for (const [k, v] of Object.entries(out.texts)) {
      const a = audit(v);
      for (const n of Object.keys(total)) total[n] += a[n];
      if (a.codes) where[k] = [...new Set(v.match(CODE))].join(' ');
    }
    console.log(`audit over ${Object.keys(out.texts).length} texts: codes=${total.codes} so_na_previa=${total.so_na_previa} a_coletar=${total.a_coletar} banned_controls=${out.controls.length} errors=${out.errors.length} failed_requests=${out.failed.length} empty=${empty.length}`);
    if (out.controls.length) console.log('banned controls:', out.controls.join(' | '));
    const codes = [...new Set(Object.values(where).join(' ').split(' ').filter(Boolean))];
    if (codes.length) console.log(`distinct codes (${codes.length}):`, codes.join(' '));
    const bad = total.codes + total.so_na_previa + total.a_coletar + out.controls.length + out.errors.length + out.failed.length + empty.length;
    process.exitCode = opts.plant ? (total.codes && total.so_na_previa && total.a_coletar && out.controls.length ? 0 : 1) : (bad ? 1 : 0);
    if (opts.plant) console.log(process.exitCode ? 'CONTROL BLIND: a planted note was not counted' : 'control caught every planted note');
  }
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
else capture(process.argv[2], process.argv[3], { audit: process.argv.includes('--audit'), plant: process.argv.includes('--plant') }).catch((e) => { console.error(e); process.exitCode = 2; });
