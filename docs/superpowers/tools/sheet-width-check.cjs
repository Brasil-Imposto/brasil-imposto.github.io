// Os 3 Poderes, the person sheet with the longest "Outros" line (Gilmar Mendes, "No TSE": Ministro substituto do TSE ...), from
// 820 to 1280 px every 20 px: no card runs past the sheet's right edge and no card is wider than itself (spec interface-fixes,
// 2026-10-22, item 5; the maintainer saw the card about 185 px past the sheet at about 1000 px, before #40 let long values wrap).
// Usage: node sheet-width-check.cjs <base url of the served previews folder> [--control]
// --control puts back the old rule (.others li b { white-space: nowrap }) and must fail.
// Env: PW_CORE, CHROME_HEADLESS.
const { chromium } = require(process.env.PW_CORE || "playwright-core");
(async () => { const b = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS }); const bad = [];
  const base = process.argv[2], plant = process.argv.includes('--control');
  for (let w = 820; w <= 1280; w += 20) {
    const p = await b.newPage({ viewport: { width: w, height: 900 } });
    await p.route('**/*', (r) => r.request().url().startsWith(base) ? r.continue() : r.abort());
    await p.goto(base + 'BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html#p=stf%3Agilmar-mendes');
    await p.waitForSelector('[data-back]:not([hidden]) .others');
    if (plant) await p.addStyleTag({ content: '.others li b { white-space: nowrap !important; }' });
    const r = await p.evaluate(() => { const sh = document.querySelector('[data-sheet]').getBoundingClientRect();
      return [...document.querySelectorAll('[data-sheet] .box')].map((x) => { const q = x.getBoundingClientRect(); return { over: Math.round(q.right - sh.right), wide: x.scrollWidth - x.clientWidth }; }); });
    const worst = r.reduce((a, x) => Math.max(a, x.over, x.wide), -999);
    if (worst > 0) bad.push(`${w}px: ${worst}px past`);
    await p.close(); }
  console.log(bad.length ? 'FAIL ' + bad.join('; ') : 'PASS 820 to 1280 px, every 20 px: no card past the sheet, no card wider than itself');
  await b.close(); process.exit(bad.length ? 1 : 0); })();
