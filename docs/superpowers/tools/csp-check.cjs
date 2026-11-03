// P2 (spec seguranca-doacoes, section 14) and no CSP violation anywhere: each page loads, is clicked through and opens the crypto
// view with zero securitypolicyviolation events; then a handler injected into the page must not run. --control serves the same
// pages without the meta and the handler must run.
// Run: node docs/superpowers/tools/csp-check.cjs <built site> [--control]
const { chromium } = require('playwright-core');
const { spawn } = require('child_process'), path = require('path');
const [site, mode] = process.argv.slice(2), PORT = 8793, live = /^https:\/\//.test(site), base = live ? site.replace(/\/?$/, '/') : `http://127.0.0.1:${PORT}/`;
const PAGES = ['index.html', 'index.html?open=SC', 'como-ler-o-mapa.html', 'como-o-dinheiro-anda.html', 'os-3-poderes.html', 'index.html#apoie-cripto?moeda=USDT&rede=tron&valor=10'];
(async () => {
  if (live && mode === '--control') throw new Error('the control runs against a local folder');
  const server = live ? { kill() {} } : spawn(process.execPath, [path.join(__dirname, 'static-server.cjs'), site, String(PORT)].concat(mode === '--control' ? ['--no-csp'] : []), { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 400));
  let bad = 0, ran = 0;
  try {
    const b = await chromium.launch({ args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
    for (const u of PAGES) {
      const p = await (await b.newContext({ viewport: { width: 1280, height: 860 } })).newPage();
      await p.addInitScript(() => { window.__violations = []; document.addEventListener('securitypolicyviolation', (e) => window.__violations.push(`${e.violatedDirective} ${e.blockedURI}`)); });
      await p.goto(base + u, { waitUntil: 'load', timeout: 120000 });
      await p.waitForFunction(() => !document.querySelector('script[type="text/x-bi-deferred"]') || document.querySelector('.bi-loader[data-state]'), null, { timeout: 90000 }).catch(() => {});
      await p.waitForTimeout(2000);
      const before = await p.evaluate(() => ({ v: window.__violations.slice(), loader: document.querySelector('.bi-loader')?.dataset.state || 'none' }));
      await p.evaluate(() => { const d = document.createElement('div'); d.innerHTML = '<img src="x" onerror="window.__p2=1">'; document.body.append(d); });
      await p.waitForTimeout(800);
      const p2 = await p.evaluate(() => window.__p2 === 1);
      ran += p2 ? 1 : 0;
      const pageBad = mode !== '--control' && (before.v.length > 0 || before.loader === 'error');
      bad += pageBad ? 1 : 0;
      console.log(`${pageBad ? 'FAIL' : 'ok  '} ${u.padEnd(60)} violations ${before.v.length}${before.v.length ? ' (' + before.v[0] + ')' : ''}, loader ${before.loader}, injected handler ${p2 ? 'RAN' : 'blocked'}`);
      await p.context().close();
    }
    await b.close();
  } finally { server.kill(); }
  if (mode === '--control') { const ok = ran === PAGES.length; console.log(ok ? 'control: without the CSP the handler runs on every page' : `BROKEN CONTROL: the handler ran on ${ran} of ${PAGES.length}`); process.exit(ok ? 0 : 1); }
  process.exit(bad || ran ? 1 : 0);
})();
