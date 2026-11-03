// P1 (spec seguranca-doacoes, section 14): poisoned data in every text, and nothing it carries may become an element on any page.
// Run: node docs/superpowers/tools/poison-check.cjs <poisoned site> [--control]
const { chromium } = require('playwright-core');
const { spawn } = require('child_process'), fs = require('fs'), path = require('path');
const [site, mode] = process.argv.slice(2), PORT = 8792, base = `http://127.0.0.1:${PORT}/`;
const PAGES = [['os-3-poderes.html', 300], ['como-o-dinheiro-anda.html', 120], ['como-ler-o-mapa.html', 60], ['index.html', 150],
  ['index.html?open=SC', 150], ['index.html?open=DF', 150], ['index.html?modal=brasil', 80], ['index.html#apoie-cripto?moeda=USDT&rede=tron&valor=10', 20]];
const MUST_SHOW = ['os-3-poderes.html', 'como-o-dinheiro-anda.html', 'index.html?open=SC'];   // the poison has to reach these screens as text
if (mode === '--control') {   // the planted hole: Os 3 Poderes stops escaping
  const esc = /const esc = \(s\) => [^\n]*;/;
  const f = [path.join(site, 'assets', 'tres-poderes-page.js'), path.join(site, 'os-3-poderes.html')].find((x) => fs.existsSync(x) && esc.test(fs.readFileSync(x, 'utf8')));
  if (!f) throw new Error('control: the esc() of Os 3 Poderes was not found');
  const t = fs.readFileSync(f, 'utf8');
  fs.writeFileSync(f, t.replace(esc, "const esc = (s) => String(s == null ? '' : s);"));
}
(async () => {
  const server = spawn(process.execPath, [path.join(__dirname, 'static-server.cjs'), site, String(PORT)], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 400));
  let injected = 0, failedShow = 0, total = 0;
  try {
    for (const [u, nClicks] of PAGES) {
      const b = await chromium.launch({ args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--js-flags=--max-old-space-size=4096'] });
      try {
        const c = await b.newContext({ viewport: { width: 1280, height: 860 } });
        await c.route('**/*', (r) => (r.request().url().startsWith(base) || /cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net/.test(r.request().url()) ? r.continue() : r.abort()));
        const p = await c.newPage();
        await p.addInitScript(() => { window.__sinks = 0; new MutationObserver((ms) => { for (const m of ms) for (const n of m.addedNodes) if (n.nodeType === 1 && (n.matches?.('img[src="x"]') || n.querySelector?.('img[src="x"]'))) window.__sinks++; }).observe(document, { childList: true, subtree: true }); });
        await p.goto(base + u, { waitUntil: 'domcontentloaded', timeout: 120000 });
        await p.waitForFunction(() => !document.querySelector('script[type="text/x-bi-deferred"]') || document.querySelector('.bi-loader[data-state="error"]'), null, { timeout: 90000 }).catch(() => {});
        await p.waitForTimeout(2500);
        await p.evaluate(async (max) => { let n = 0; const all = [...document.querySelectorAll('button, [role="button"], summary, a[href^="#"], [data-id], [data-uf], [data-case], tr[data-id], li[data-id]')].filter((e) => e.getClientRects().length && !e.closest('header') && !e.closest('.bi-header')).slice(0, max);
          for (const e of all) { try { e.click(); n++; } catch (_) {} if (n % 10 === 0) await new Promise((r) => setTimeout(r, 30)); } }, nClicks);
        await p.waitForTimeout(1500);
        const r = await p.evaluate(() => ({ xss: !!window.__xss, added: window.__sinks, now: document.querySelectorAll('img[src="x"]').length, shown: (document.body.innerText.match(/<img src="x"/g) || []).length }));
        const bad = r.xss || r.added || r.now;
        injected += bad ? 1 : 0; total += r.shown;
        if (MUST_SHOW.includes(u) && !r.shown) failedShow++;
        console.log(`${bad ? 'INJECTED' : 'clean   '} ${u.padEnd(52)} ${JSON.stringify(r)}`);
      } finally { await b.close().catch(() => {}); }
    }
  } finally { server.kill(); }
  console.log(`${injected} of ${PAGES.length} pages injected; ${total} poisoned texts shown as text`);
  // with the planted hole the poison on Os 3 Poderes becomes elements, not text, so the control is judged on injection alone
  if (mode === '--control') { console.log(injected ? 'control caught' : 'BROKEN CONTROL: the planted hole was not seen'); process.exit(injected ? 0 : 1); }
  if (failedShow) { console.log('BROKEN PROBE: the poison did not reach a screen it must reach'); process.exit(2); }
  process.exit(injected ? 1 : 0);
})();
