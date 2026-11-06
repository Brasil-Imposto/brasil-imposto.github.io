// Phase 6 of spec seguranca-doacoes (section 14): real wallet extensions against a local test build on test networks, with the
// page's CSP on. Each case starts a donation, answers the wallet's requests, reads the wallet's own confirmation screen, which must
// name the test build's destination and amount, then refuses it and reads the page's message. Every CSP violation the page reports
// fails the run. --control serves the pages with the destination swapped: the wallet must then show the planted address and the
// case must fail, or the check is blind.
//
// Run: node docs/superpowers/tools/wallets-check.cjs metamask <extension folder> <test site folder> [--control | --mainnet-bsc]
// --mainnet-bsc runs against a build with the real data (BNB Smart Chain, network 56): it stops at the wallet's add-network or
// switch-network screen, prints what the wallet says there, and refuses; nothing is approved.
// The test site comes from testnet-support.py and build-site.py (BI_SUPPORT_JSON), built in a copy of the tree; the keys come from
// wallet-keys.py, read from the Keychain at use time and typed into the extension, never printed. The probe prints test ids, short
// labels and addresses only, and nothing at all on a recovery-phrase screen.
//
// Chrome for Testing no longer side-loads extensions from the command line, so the extension is loaded over the debugging pipe
// (Extensions.loadUnpacked, with --enable-unsafe-extension-debugging) and Playwright attaches through a port to the same browser.
// MetaMask 13 shows its requests in Chrome's side panel; the same route renders in a tab, which the probe opens.
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');
const { chromium } = require('playwright-core');
const PORT = 9341, SITE_PORT = 8797, PLANTED = '0x2222222222222222222222222222222222222222';
const keychain = (s) => execFileSync('security', ['find-generic-password', '-a', 'pegaso', '-s', s, '-w']).toString().trim();
const strip = (u) => u.replace(/^chrome-extension:\/\/[a-p]{32}/, '').replace(/[A-Za-z0-9_-]{16,}/g, '<id>');

async function launch(ext, profile) {
  const proc = spawn(chromium.executablePath(), ['--headless=new', '--remote-debugging-pipe', `--remote-debugging-port=${PORT}`,
    '--enable-unsafe-extension-debugging', `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check', 'about:blank'],
  { stdio: ['ignore', 'ignore', 'ignore', 'pipe', 'pipe'] });
  let buf = '';
  const answer = new Promise((ok) => proc.stdio[4].on('data', (d) => { buf += d; const i = buf.indexOf('\0'); if (i >= 0) ok(JSON.parse(buf.slice(0, i))); }));
  proc.stdio[3].write(JSON.stringify({ id: 1, method: 'Extensions.loadUnpacked', params: { path: ext } }) + '\0');
  const r = await answer;
  if (r.error) { proc.kill(); throw new Error('loadUnpacked: ' + r.error.message); }
  for (let i = 0; i < 50; i++) { try { await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json(); break; } catch { await new Promise((ok) => setTimeout(ok, 200)); } }
  const browser = await chromium.connectOverCDP(`http://127.0.0.1:${PORT}`);
  return { proc, browser, ctx: browser.contexts()[0], id: r.result.id };
}

async function controls(page, max = 30) {
  if (await page.locator('[data-testid*="recovery-phrase"], [data-testid*="srp-word"], [data-testid*="srp-chip"]').count()) return ['(recovery-phrase screen: not listed)'];
  const out = [];
  for (const el of await page.locator('[data-testid]').all()) {
    if (!(await el.isVisible().catch(() => false))) continue;
    out.push(`[${await el.getAttribute('data-testid')}] ${((await el.innerText().catch(() => '')) || '').trim().slice(0, 50).replace(/\s+/g, ' ')}`);
    if (out.length >= max) break;
  }
  return [...new Set(out)];
}

const metamask = {
  async setup(ctx, id) {
    let page = await ctx.newPage();
    await page.goto(`chrome-extension://${id}/home.html`); await page.waitForTimeout(3000);
    const pw = keychain('bi-test-wallet-password');
    const act = async (kind, sel, val) => {
      const l = page.locator(sel).first();
      if (kind === 'click') await l.click({ timeout: 20000 });
      if (kind === 'check') await l.check({ timeout: 20000, force: true });
      if (kind === 'fill') await l.fill(val, { timeout: 20000 });
      if (kind === 'uncheck') { const box = l.locator('input[type=checkbox]'); const t = (await box.count()) ? box.first() : l; if (await t.isChecked().catch(() => false)) await t.click({ force: true }); }
      await page.waitForTimeout(1200);
    };
    // a new wallet whose recovery phrase is never revealed ("remind me later"), then the test key imported as an account
    for (const s of [['click', '[data-testid="onboarding-create-wallet"]'], ['click', '[data-testid="onboarding-create-with-srp-button"]'],
      ['fill', '[data-testid="create-password-new-input"]', pw], ['fill', '[data-testid="create-password-confirm-input"]', pw],
      ['check', '[data-testid="create-password-terms"]'], ['click', '[data-testid="create-password-submit"]'], ['click', '[data-testid="passkey-maybe-later-button"]'],
      ['click', '[data-testid="recovery-phrase-remind-later"]'], ['uncheck', '[data-testid="metametrics-checkbox"]'],
      ['uncheck', '[data-testid="metametrics-data-collection-checkbox"]'], ['click', '[data-testid="metametrics-i-agree"]'],
      ['click', '[data-testid="onboarding-complete-done"]']]) await act(...s);
    await page.waitForTimeout(3000);
    page = ctx.pages().filter((x) => x.url().endsWith('home.html#/')).pop();
    for (const s of [['click', '[data-testid="account-menu-icon"]'], ['click', '[data-testid="account-list-add-wallet-button"]'],
      ['click', '[data-testid="choose-wallet-type-import-account"]'], ['fill', '#private-key-box', keychain('bi-test-evm-donor')],
      ['click', '[data-testid="import-account-confirm-button"]']]) await act(...s);
    await page.waitForTimeout(2000);
    for (const x of ctx.pages()) if (x.url().startsWith('chrome-extension://')) await x.close();   // requests then go to the side panel
  },
  // the network the page proposes (wallet_addEthereumChain): the only screen with this sentence, and never one with a recipient
  addNetwork: { screen: '[data-testid="parent-selector-confirmation-page"]:has-text("A site is suggesting")', approve: '[data-testid="confirm-footer-button"]' },
  // the cases: coin, network id, amount typed, and what the wallet's confirmation must say
  cases: [
    { coin: 'ETH', net: 'ethereum', amount: '0.001', network: 'Sepolia', shows: '0,001' },
    { coin: 'USDC', net: 'ethereum', amount: '1.25', network: 'Sepolia', shows: '1,25' },
    { coin: 'BNB', net: 'bsc', amount: '0.002', network: 'BNB Smart Chain Testnet', shows: '0,002' },
  ],
};

// UniSat (spec seguranca-doacoes, section 11): the page must refuse a wallet on a Bitcoin test network before anything is signed, and let
// the main network through. UniSat builds its controls from plain elements, so the steps click by visible text. The test key goes in by
// the single-key route (#/account/create-simple-wallet); the recovery-phrase route is never opened.
const unisat = {
  async setup(ctx, id) {
    const page = await ctx.newPage(), base = `chrome-extension://${id}/index.html`, pw = keychain('bi-test-wallet-password');
    const text = async (s) => { await page.getByText(s, { exact: true }).first().click({ timeout: 20000 }); await page.waitForTimeout(1500); };
    await page.goto(base + '#/welcome'); await page.waitForTimeout(3000);
    await text('I already have a wallet');
    for (const l of await page.locator('input[type=password]').all()) await l.fill(pw);
    await text('Continue');
    await page.goto(base + '#/account/create-simple-wallet'); await page.waitForTimeout(2500);
    await page.locator('input[placeholder*="WIF Private Key"]').fill(keychain('bi-test-btc-donor'));
    await text('Continue'); await text('Native Segwit (P2WPKH)'); await text('Continue');
    await page.waitForTimeout(3000); this.page = page; this.base = base;
  },
  async testnet4() {   // Settings, the network item, Bitcoin Testnet, Bitcoin Testnet4
    const page = this.page; await page.goto(this.base + '#/settings'); await page.waitForTimeout(2500);
    for (const s of ['Bitcoin', 'Bitcoin Testnet', 'Bitcoin Testnet4 (Beta)']) { await page.getByText(s, { exact: true }).last().click({ timeout: 20000 }); await page.waitForTimeout(1500); }
  },
  cases: [{ name: 'BTC, UniSat on the main network: the page lets it through', test: false }, { name: 'BTC, UniSat on Testnet4: refused before signing', test: true }],
};

async function runUnisat(ctx, id, control) {
  const rows = [], csp = [];
  await unisat.setup(ctx, id);
  for (const c of unisat.cases) {
    if (c.test) await unisat.testnet4();
    const chain = await (async () => { const q = await ctx.newPage(); await q.goto(`http://127.0.0.1:${SITE_PORT}/como-ler-o-mapa.html`); await q.waitForTimeout(1500);
      const v = await q.evaluate(async () => (window.unisat && window.unisat.getChain ? (await window.unisat.getChain()).enum : null)); await q.close(); return v; })();
    const p = await ctx.newPage();
    p.on('console', (m) => { if (/Content Security Policy|Refused to (load|execute|connect|apply)/.test(m.text())) csp.push(m.text().slice(0, 160)); });
    if (control) await p.route('**/assets/bi-cripto.js*', async (r) => { const res = await r.fetch(); const was = await res.text(), body = was.replace("throw { code: 'test_network' };\n      return u.sendBitcoin", 'return u.sendBitcoin'); if (body === was) rows.push({ name: 'control plant landed', ok: false, detail: 'the network check was not found in bi-cripto.js' }); r.fulfill({ response: res, body }); });
    await p.goto(`http://127.0.0.1:${SITE_PORT}/como-ler-o-mapa.html`); await p.waitForSelector('.bi-apoie-btn');
    await p.locator('.bi-apoie-btn').first().click(); await p.waitForTimeout(300);
    await p.locator('.bi-ap-view[data-view="main"] [data-go="crypto"]').click(); await p.waitForTimeout(300);
    await p.click('[data-coin-btn="BTC"]'); await p.click('.bi-ap-coin[data-coin="BTC"] [data-net-btn="bitcoin"]');
    await p.waitForFunction(() => window.BiCripto && window.BiCripto.ready);
    await p.fill('#bi-ap-amount', '0.0001');
    const signing = [];
    ctx.on('page', (np) => { if (/notification\.html#\/(?!approval)/.test(np.url())) signing.push(np.url()); });
    for (let k = 0; k < 3; k++) {
      await p.click('[data-send]'); await p.waitForTimeout(1200);
      const w = p.locator('[data-wallets] button', { hasText: 'UniSat' }); if (await w.count()) await w.first().click();
      await p.waitForTimeout(3000);
      const ask = ctx.pages().find((x) => /notification\.html#\/approval/.test(x.url()));
      if (ask) { await ask.getByText('Connect', { exact: true }).first().click({ timeout: 10000 }).catch(() => {}); await p.waitForTimeout(2500); continue; }
      if ((await p.locator('[data-msg]').innerText().catch(() => '')).trim()) break;
    }
    for (const x of ctx.pages()) if (/notification\.html/.test(x.url())) { signing.push(x.url()); await x.close().catch(() => {}); }
    const msg = (await p.locator('[data-msg]').innerText().catch(() => '')).trim();
    const refused = /rede de testes/.test(msg);
    rows.push({ name: c.name, ok: c.test ? refused && !signing.length : !refused && /saldo insuficiente|Envio cancelado|sendBitcoin/.test(msg + signing.join(' ')) || (!c.test && signing.length > 0),
      detail: `wallet reports ${chain || '?'}; page: ${msg.slice(0, 90) || '(no message)'}; signing windows: ${signing.length}` });
    await p.close();
  }
  rows.push({ name: 'no CSP violation on the page', ok: csp.length === 0, detail: csp.slice(0, 3).join(' || ') || '0' });
  return rows;
}

async function reloadSidePanel() {   // the side panel can stay on a request already answered; a reload routes it to the oldest pending one
  const t = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find((x) => /sidepanel\.html/.test(x.url));
  if (!t) return;
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((ok, no) => { ws.onopen = ok; ws.onerror = no; });
  await new Promise((ok) => { ws.onmessage = ok; ws.send(JSON.stringify({ id: 1, method: 'Page.reload' })); setTimeout(ok, 3000); });
  ws.close();
}

async function pending(ctx, seen) {   // the next request in the side panel, opened in a tab (the same route renders there)
  for (let i = 0; i < 40; i++) {
    const t = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find((x) => /sidepanel\.html#\/(connect|confirm-transaction|confirmation)\b/.test(x.url) && !seen.has(x.url));
    if (t) { seen.add(t.url); const tab = await ctx.newPage(); await tab.goto(t.url.replace('sidepanel.html', 'home.html')); await tab.waitForTimeout(2500); return tab; }
    if (i % 10 === 9) await reloadSidePanel().catch(() => {});
    await new Promise((ok) => setTimeout(ok, 500));
  }
  return null;
}

(async () => {
  const args = process.argv.slice(2), control = args.includes('--control'), mainnetBsc = args.includes('--mainnet-bsc');
  const [wallet, ext, site] = args.filter((a) => !a.startsWith('--'));
  if (!['metamask', 'unisat'].includes(wallet)) throw new Error('wallets: metamask, unisat (TronLink and Crossmark come next)');
  const W = mainnetBsc ? { ...metamask, cases: [{ coin: 'BNB', net: 'bsc', amount: '0.002', network: 'BNB Smart Chain', shows: '0,002' }] } : metamask, want = JSON.parse(fs.readFileSync(path.join(site, 'index.html'), 'utf8').match(/id="bi-cripto-data">(.*?)<\/script>/s)[1]).networks;
  const server = spawn(process.execPath, [path.join(__dirname, 'static-server.cjs'), site, String(SITE_PORT)], { stdio: 'ignore' });
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'bi-wallet-'));
  const { proc, browser, ctx, id } = await launch(path.resolve(ext), profile);
  const rows = [], csp = [], alerts = [];
  if (wallet === 'unisat') {   // its own steps; --control removes the page's Bitcoin network check: the Testnet4 case must then fail
    let out = [];
    try { out = await runUnisat(ctx, id, control); } catch (e) { out = [{ name: 'the UniSat probe ran', ok: false, detail: String(e).split('\n')[0].slice(0, 160) }]; }
    await browser.close().catch(() => {}); const gone = new Promise((ok) => proc.on('exit', ok)); proc.kill(); await Promise.race([gone, new Promise((ok) => setTimeout(ok, 5000))]);
    server.kill(); try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch {}
    for (const r of out) console.log(`${r.ok ? 'ok  ' : 'FAIL'} ${r.name}: ${r.detail}`);
    if (control) { const t4 = out.find((r) => /Testnet4/.test(r.name)); const caught = !!t4 && !t4.ok && !out.some((r) => r.name === 'control plant landed');
      console.log(`control: ${caught ? 'with the check removed, the Testnet4 case fails' : 'NOT caught'}`); process.exit(caught ? 0 : 1); }
    process.exit(out.every((r) => r.ok) ? 0 : 1);
  }
  try {
    await W.setup(ctx, id);
    for (const c of W.cases) for (let attempt = 1; attempt <= 2; attempt++) { let stage = 'start'; try {
      const dest = want.find((n) => n.id === c.net).address, shown = control ? PLANTED : dest;
      const p = await ctx.newPage(), seen = new Set();
      p.on('console', (m) => { if (/Content Security Policy|Refused to (load|execute|connect|apply)/.test(m.text())) csp.push(`${c.coin}/${c.net}: ${m.text().slice(0, 160)}`); });
      if (control) await p.route('**/*.html*', async (r) => { const res = await r.fetch(); r.fulfill({ response: res, body: (await res.text()).replaceAll(dest, PLANTED) }); });
      stage = 'open the page'; await p.goto(`http://127.0.0.1:${SITE_PORT}/como-ler-o-mapa.html`); await p.waitForSelector('.bi-apoie-btn');
      await p.locator('.bi-apoie-btn').first().click(); await p.waitForTimeout(300);
      await p.locator('.bi-ap-view[data-view="main"] [data-go="crypto"]').click(); await p.waitForTimeout(300);
      stage = 'choose coin and network'; await p.click(`[data-coin-btn="${c.coin}"]`); await p.click(`.bi-ap-coin[data-coin="${c.coin}"] [data-net-btn="${c.net}"]`);
      await p.waitForFunction(() => window.BiCripto && window.BiCripto.ready);
      stage = 'amount and first click'; await p.fill('#bi-ap-amount', c.amount); await p.click('[data-send]'); await p.waitForTimeout(800);
      if (await p.locator('[data-wallets] button').count()) { await p.locator('[data-wallets] button').first().click(); await p.waitForTimeout(500); }
      stage = 'wallet requests'; let confirm = null, steps = [];
      for (let k = 0; k < 5 && !confirm; k++) {
        const tab = await pending(ctx, seen);
        if (!tab) { const b = p.locator('[data-send]'); if (await b.isVisible().catch(() => false) && !(await b.isDisabled().catch(() => true))) { await b.click(); continue; } break; }
        const route = (tab.url().split('#/')[1] || '').split(/[/?]/)[0];
        // settle first: a send confirmation can take seconds to show its recipient, and must never be taken for an approval
        let kind = null;
        for (let w = 0; w < 20 && !kind; w++) {
          if (await tab.locator('[data-testid="recipient-address"]').count()) kind = 'send';
          else if (await tab.locator('[data-testid="confirm-btn"]').count()) kind = 'connect';
          else if (await tab.locator('[data-testid="page-container-footer-next"]').count()) kind = 'switch network';
          else if (W.addNetwork && await tab.locator(W.addNetwork.screen).count()) kind = 'add network';
          else await tab.waitForTimeout(500);
        }
        if (kind === 'send') { confirm = tab; steps.push(`confirmation (${route})`); break; }
        if (!kind) { steps.push(`unknown screen (${route}): ` + (await controls(tab, 12)).join(' ; ')); await tab.close().catch(() => {}); break; }
        steps.push(`${kind} (${route})`);
        if (mainnetBsc && (kind === 'add network' || kind === 'switch network')) {
          const said = ((await tab.locator('body').innerText().catch(() => '')) || '').replace(/\s+/g, ' ');
          const warn = said.match(/(According to our records[^.]*\.|does not match a known provider[^.]*\.|De acordo com nossos registros[^.]*\.)/);
          const rpc = (said.match(/https:\/\/[a-z0-9.-]+[^ ]*/i) || [''])[0];
          rows.push({ name: `network 56 screen (${kind})`, ok: !warn, detail: `rpc shown ${rpc || '(none)'}; wallet warning: ${warn ? warn[0] : 'none'}` });
          await tab.locator('[data-testid="confirmation-footer-cancel-button"], [data-testid="confirm-footer-cancel-button"], [data-testid="page-container-footer-cancel"]').first().click().catch(() => {});
          await tab.close().catch(() => {}); break;
        }
        if (kind === 'add network' && await tab.locator(W.addNetwork.approve).first().isDisabled()) {   // MetaMask's alerts, read then acknowledged
          await tab.locator('[data-testid="inline-alert"]').first().click().catch(() => {}); await tab.waitForTimeout(1000);
          for (let a = 0; a < 5 && await tab.locator('[role="dialog"]').count(); a++) {
            const said = ((await tab.locator('[data-testid="alert-modal__selected-alert"]').first().innerText().catch(() => '')) || '').trim().replace(/\s+/g, ' ');
            if (said) alerts.push(`${c.coin}/${c.net}: ${said.slice(0, 140)}`);
            const box = tab.locator('[role="dialog"] input[type="checkbox"]'); if (await box.count()) await box.first().check({ force: true }).catch(() => {});
            const next = tab.locator('[data-testid="alert-modal-next-button"]:not([disabled])');
            if (await next.count() && await next.first().isVisible()) await next.first().click(); else await tab.locator('[data-testid="alert-modal-button"]').first().click();
            await tab.waitForTimeout(800);
          }
        }
        if (kind === 'add network') {   // MetaMask keeps Confirm off until its scroll-down arrow is used
          const arrow = tab.locator('button[aria-label="Role para baixo"], button[aria-label="Scroll down"]');
          if (await arrow.count()) { await arrow.first().click(); await tab.waitForTimeout(800); }
        }
        await tab.locator({ connect: '[data-testid="confirm-btn"]', 'switch network': '[data-testid="page-container-footer-next"]',
          'add network': W.addNetwork ? W.addNetwork.approve : 'none' }[kind]).first().click({ timeout: 5000 });
        await tab.waitForTimeout(1500); await tab.close().catch(() => {});
      }
      if (mainnetBsc) {   // no network screen came first: say what came, and the network on the confirmation, then refuse
        if (!rows.some((r) => r.name.startsWith('network 56'))) {
          const net = confirm ? (await confirm.locator('[data-testid="confirmation__details-network-name"]').first().innerText().catch(() => '')).trim() : '';
          rows.push({ name: 'network 56: no add-network or switch screen', ok: true, detail: `steps: ${steps.join(' > ') || 'none'}; confirmation network: ${net || '(no confirmation)'}` });
        }
        if (confirm) { await confirm.locator('[data-testid="confirm-footer-cancel-button"]').click().catch(() => {}); await confirm.close().catch(() => {}); }
        await p.close(); break;
      }
      if (!confirm) {
        const said = (await p.locator('[data-msg]').innerText().catch(() => '')).trim().slice(0, 120);
        rows.push({ name: `${c.coin} on ${c.net}`, ok: false, detail: `no confirmation screen (${steps.join(' > ')}); page: ${said || '(no message)'}` }); await p.close(); continue;
      }
      stage = 'read the confirmation'; const text = (await controls(confirm, 40)).join(' | ');
      const recipient = (await confirm.locator('[data-testid="recipient-address"]').first().innerText().catch(() => '')).trim();
      const network = (await confirm.locator('[data-testid="confirmation__details-network-name"]').first().innerText().catch(() => '')).trim();
      const right = recipient.toLowerCase() === dest.toLowerCase() && network === c.network && text.includes(c.shows);
      await confirm.locator('[data-testid="confirm-footer-cancel-button"]').click(); await confirm.waitForTimeout(1500); await confirm.close().catch(() => {});
      await p.waitForTimeout(1500);
      const msg = (await p.locator('[data-msg]').innerText().catch(() => '')).trim();
      rows.push({ name: `${c.coin} on ${c.net}`, ok: right && /Envio cancelado na carteira/.test(msg),
        detail: `recipient ${recipient || '?'} (${recipient.toLowerCase() === shown.toLowerCase() ? 'the address served' : 'NOT the address served'}), network ${network || '?'}, amount ${text.includes(c.shows) ? c.shows : 'not found'}; page: ${msg.slice(0, 60)}; steps: ${steps.join(' > ')}` });
      await p.close();
      break;
    } catch (e) {   // a stopped probe (a timing flake) is tried once more; a case that failed on what the wallet showed never is
      if (attempt === 1) { console.log(`note: ${c.coin} on ${c.net} stopped once at "${stage}", tried again`); for (const x of ctx.pages()) if (!x.url().startsWith('about:')) await x.close().catch(() => {}); continue; }
      rows.push({ name: `${c.coin} on ${c.net}`, ok: false, detail: `the probe stopped at "${stage}": ${String(e).split('\n')[0].slice(0, 120)}` });
    } }
  } finally {
    await browser.close().catch(() => {});
    const gone = new Promise((ok) => proc.on('exit', ok)); proc.kill(); await Promise.race([gone, new Promise((ok) => setTimeout(ok, 5000))]);
    server.kill();
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch (e) { console.log(`note: the test profile ${profile} was not removed (${e.code})`); }
  }
  rows.push({ name: 'no CSP violation on the page', ok: csp.length === 0, detail: csp.slice(0, 3).join(' || ') || '0' });
  for (const a of alerts) console.log(`wallet alert ${a}`);
  for (const r of rows) console.log(`${r.ok ? 'ok  ' : 'FAIL'} ${r.name}: ${r.detail}`);
  const failed = rows.filter((r) => !r.ok && !r.name.startsWith('no CSP'));
  if (control) {   // every case must fail, each because the wallet showed the planted address
    // the wallet may shorten or label the address ("Null: 0x222...222"); what counts is that it showed the planted one
    const caught = failed.length === W.cases.length && failed.every((r) => /^recipient [^(]*0x222/.test(r.detail));
    console.log(`control: ${caught ? 'every case caught the planted destination' : 'NOT caught'}`);
    process.exit(caught ? 0 : 1);
  }
  process.exit(rows.every((r) => r.ok) ? 0 : 1);
})().catch((e) => { console.error('error:', String(e).slice(0, 400)); process.exit(1); });
