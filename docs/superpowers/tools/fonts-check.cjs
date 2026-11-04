// P9 (spec seguranca-doacoes, section 14): no page asks fonts.googleapis.com or fonts.gstatic.com, the crypto view included.
// --control plants the Google Fonts link in the served Início, and the probe must see it.
// Run: node docs/superpowers/tools/fonts-check.cjs <built site> [--control]
const { chromium } = require('playwright-core');
const { spawn } = require('child_process'), fs = require('fs'), os = require('os'), path = require('path');
let [site, mode] = process.argv.slice(2);
const PORT = 8794, live = /^https:\/\//.test(site), base = live ? site.replace(/\/?$/, '/') : `http://127.0.0.1:${PORT}/`, GOOGLE = /fonts\.(googleapis|gstatic)\.com/;
const PAGES = ['index.html', 'como-ler-o-mapa.html', 'como-o-dinheiro-anda.html', 'os-3-poderes.html', 'index.html#apoie-cripto?moeda=USDT&rede=tron&valor=10'];
if (mode === '--control') {
  if (/^https:\/\//.test(site)) throw new Error('the control runs against a local folder');
  const copy = fs.mkdtempSync(path.join(os.tmpdir(), 'fonts-control-'));
  fs.cpSync(site, copy, { recursive: true });
  const f = path.join(copy, 'index.html');
  fs.writeFileSync(f, fs.readFileSync(f, 'utf8').replace('</head>', '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope"></head>'));
  site = copy;
}
(async () => {
  const server = live ? { kill() {} } : spawn(process.execPath, [path.join(__dirname, 'static-server.cjs'), site, String(PORT)], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 400));
  let asked = 0;
  try {
    const b = await chromium.launch({ args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
    for (const u of PAGES) {
      const c = await b.newContext({ viewport: { width: 1280, height: 860 } }), seen = [];
      c.on('request', (r) => { if (GOOGLE.test(r.url())) seen.push(r.url()); });
      await c.route(GOOGLE, (r) => r.abort());   // seen, never fetched
      const p = await c.newPage();
      await p.goto(base + u, { waitUntil: 'load', timeout: 120000 });
      await p.waitForTimeout(3000);
      asked += seen.length;
      console.log(`${seen.length ? 'ASKED' : 'ok   '} ${u.padEnd(60)} ${seen.length} Google Fonts requests`);
      await c.close();
    }
    await b.close();
  } finally { server.kill(); }
  if (mode === '--control') { console.log(asked ? 'control caught' : 'BROKEN CONTROL: the planted link was not seen'); process.exit(asked ? 0 : 1); }
  process.exit(asked ? 1 : 0);
})();
