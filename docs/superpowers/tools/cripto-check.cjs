// The crypto send (spec cripto-no-site, section 8, item 4) in a real browser with fake wallets: nothing leaves the machine. For every coin
// and network open in the build, the request the wallet receives must hold the address, contract, value and chain of data/support.json;
// the moments of the drawing (round cripto-envio-r1): connected, confirm in the wallet, sent; and the cases of section 3.3: refusals, a
// wrong network, a double click, several wallets, no wallet, the QR and the links on a phone.
// Usage: node cripto-check.cjs <base url of a served build> [--control] [--staging]
// --staging says the build is the staging profile, where the networks on "soon" open (the first XRP goes through the test site).
// --control swaps the address in the page's data block for another one: every send check must then fail.
// Env: PW_CORE, CHROME_HEADLESS, BI_SUPPORT_JSON (optional).
const fs = require('fs');
const path = require('path');
const SUPPORT = JSON.parse(fs.readFileSync(process.env.BI_SUPPORT_JSON || path.join(__dirname, '..', '..', '..', 'data', 'support.json'), 'utf8'));
const FROM = '0x1111111111111111111111111111111111111111';
const fakeWallets = () => {
  window.__calls = []; window.__fake = { chain: '0x1', reject: null, noChain: false, fail: null, hold: false, account: '0x1111111111111111111111111111111111111111' };
  const f = window.__fake, refuse = () => Object.assign(new Error('refused'), { code: 4001 });
  const evm = { request: async ({ method, params }) => {
    window.__calls.push({ method, params });
    if (f.reject === method) throw refuse();
    if (f.fail && f.fail.method === method) throw Object.assign(new Error('x'), { code: f.fail.code });
    if (method === 'eth_requestAccounts') return [f.account];
    if (method === 'eth_chainId') return f.chain;
    if (method === 'wallet_switchEthereumChain') { if (f.noChain) { f.noChain = false; throw Object.assign(new Error('x'), { code: 4902 }); } f.chain = params[0].chainId; return null; }
    if (method === 'wallet_addEthereumChain') return null;
    if (method === 'eth_sendTransaction') { if (f.hold) await new Promise((ok) => { f.release = ok; }); return '0xabc'; }
    throw new Error('unexpected ' + method);
  }, on: () => {} };
  addEventListener('eip6963:requestProvider', () => dispatchEvent(new CustomEvent('eip6963:announceProvider', { detail: {
    info: { uuid: 'u1', name: 'Fake', icon: 'data:image/gif;base64,R0lGODlhAQABAAAAACw=', rdns: 'x.fake' }, provider: evm } })));
  if (window.__twoWallets) addEventListener('eip6963:requestProvider', () => dispatchEvent(new CustomEvent('eip6963:announceProvider', { detail: {
    info: { uuid: 'u2', name: 'Second', icon: 'data:image/gif;base64,R0lGODlhAQABAAAAACw=', rdns: 'x.second' }, provider: { request: async (a) => { window.__calls.push({ second: true, ...a }); return evm.request(a); }, on: () => {} } } })));
  const tronWeb = { transactionBuilder: { triggerSmartContract: async (contract, fn, opts, params, from) => { window.__calls.push({ method: 'trigger', contract, fn, params, from }); return { transaction: { txID: 'tx1' } }; } },
    trx: { sign: async (t) => { window.__calls.push({ method: 'sign' }); if (f.reject === 'sign') throw 'Confirmation declined by user'; return t; }, sendRawTransaction: async () => ({ result: true, txid: 'tx1' }) } };
  window.tron = { isTronLink: true, tronWeb, request: async ({ method }) => { window.__calls.push({ method: 'tron:' + method }); return ['TQ7vFakeFakeFakeFakeFakeFakeFakek2Pd']; } };
  window.unisat = { requestAccounts: async () => ['bc1qfake'], sendBitcoin: async (to, sats) => { window.__calls.push({ method: 'sendBitcoin', to, sats }); return 'btctx'; } };
};
const nets = () => SUPPORT.crypto.groups.flatMap((g) => g.networks.filter((n) => process.argv.includes('--staging') || n.status === 'live').map((n) => ({ ...n, address: g.address, family: g.format })));
const units = (text, decimals) => { const [w, f = ''] = text.split('.'); return BigInt(w + f.padEnd(decimals, '0')); };

(async () => {
  const args = process.argv.slice(2), base = args.find((a) => !a.startsWith('--')).replace(/\/?$/, '/'), control = args.includes('--control');
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox'] });
  const rows = [], report = (name, ok, detail) => rows.push({ name, ok, detail });
  const open = async (how) => {
    const phone = how === true, none = how === 'none', two = how === 'two';
    const ctx = await browser.newContext(phone ? { viewport: { width: 390, height: 800 }, isMobile: true, hasTouch: true,
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1' } : { viewport: { width: 1280, height: 860 } });
    await ctx.route('**/*', async (r) => {
      const u = r.request().url();
      if (!u.startsWith(base)) return r.abort();
      if (control && r.request().resourceType() === 'document') {
        const res = await r.fetch();
        return r.fulfill({ response: res, body: (await res.text()).replaceAll(SUPPORT.crypto.groups[1].address, '0x2222222222222222222222222222222222222222').replaceAll(SUPPORT.crypto.groups[3].address, 'TQ7vFakeFakeFakeFakeFakeFakeFakek2Pd').replaceAll(SUPPORT.crypto.groups[0].address, 'bc1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq').replaceAll(SUPPORT.crypto.groups[2].address, '1'.repeat(32)).replaceAll(SUPPORT.crypto.groups[4].address, 'rrrrrrrrrrrrrrrrrrrrBZbvji') });
      }
      return r.continue();
    });
    if (two) await ctx.addInitScript(() => { window.__twoWallets = true; });
    if (!phone && !none) await ctx.addInitScript(fakeWallets);
    const p = await ctx.newPage();
    await p.goto(base + 'como-ler-o-mapa.html'); await p.waitForSelector('.bi-apoie-btn');
    await p.$eval('.bi-apoie-btn', (e) => e.click()); await p.waitForTimeout(150);
    await p.$eval('.bi-ap-view[data-view="main"] [data-go="crypto"]', (e) => e.click()); await p.waitForTimeout(150);
    return { ctx, p };
  };
  const pick = async (p, coin, net) => { await p.click(`[data-coin-btn="${coin}"]`); await p.click(`.bi-ap-coin[data-coin="${coin}"] [data-net-btn="${net}"]`);
    await p.waitForFunction(() => window.BiCripto && window.BiCripto.ready); };
  const send = async (p, amount) => { await p.fill('#bi-ap-amount', amount); await p.click('[data-send]'); await p.waitForTimeout(150);
    if (await p.$('[data-wallets] button')) { await p.click('[data-wallets] button'); await p.waitForTimeout(150); }
    await p.click('[data-send]'); await p.waitForTimeout(250); };
  // every coin and network with a browser wallet
  for (const n of nets().filter((x) => ['evm', 'tron', 'bitcoin'].includes(x.family))) {
    for (const c of n.coins) {
      const { ctx, p } = await open(false);
      await pick(p, c.coin, n.id); await send(p, '1.5');
      const calls = await p.evaluate(() => window.__calls);
      const done = await p.$eval('[data-done]', (e) => e.textContent).catch(() => '');
      const want = units('1.5', c.decimals);
      let ok;
      if (n.family === 'evm') {
        const tx = (calls.find((x) => x.method === 'eth_sendTransaction') || { params: [{}] }).params[0];
        const pad = (h) => h.padStart(64, '0');
        ok = c.contract ? tx.to === c.contract && tx.data === '0xa9059cbb' + pad(n.address.slice(2).toLowerCase()) + pad(want.toString(16)) && !tx.value
          : tx.to === n.address && tx.value === '0x' + want.toString(16) && !tx.data;
        ok = ok && tx.from === FROM && calls.some((x) => x.method === 'wallet_switchEthereumChain' || n.chain_id === 1);
      } else if (n.family === 'tron') {
        const t = calls.find((x) => x.method === 'trigger') || { params: [] };
        ok = t.contract === c.contract && t.params[0].value === n.address && t.params[1].value === want.toString();
      } else {
        const b = calls.find((x) => x.method === 'sendBitcoin') || {};
        ok = b.to === n.address && BigInt(b.sats || 0) === want;
      }
      report(`send ${c.coin} on ${n.id}`, !!ok && /Doação enviada/.test(done), JSON.stringify(calls.slice(-1)).slice(0, 160));
      await ctx.close();
    }
  }
  // the links on a phone (no wallet injected): Solana, Bitcoin, XRP Ledger
  for (const n of nets().filter((x) => ['solana', 'bitcoin', 'xrp'].includes(x.family))) {
    for (const c of n.coins) {
      const { ctx, p } = await open(true);
      await pick(p, c.coin, n.id); await p.fill('#bi-ap-amount', '1.5'); await p.waitForTimeout(150);
      const href = await p.$eval('[data-pay]', (a) => a.getAttribute('href') || '');
      report(`link ${c.coin} on ${n.id}`, href.includes(n.address) && href.includes('amount=1.5') && (!c.contract || href.includes(c.contract)), href.slice(0, 120));
      await ctx.close();
    }
  }
  // section 3.3
  const c1 = await open(false); await pick(c1.p, 'ETH', 'ethereum');
  await c1.p.evaluate(() => { window.__fake.reject = 'eth_sendTransaction'; }); await send(c1.p, '0.1');
  report('refused on the wallet', /Envio cancelado na carteira/.test(await c1.p.$eval('[data-msg]', (e) => e.textContent)), 'message'); await c1.ctx.close();
  const c2 = await open(false); await pick(c2.p, 'BNB', 'bsc');
  await c2.p.evaluate(() => { window.__fake.reject = 'wallet_switchEthereumChain'; }); await send(c2.p, '0.1');
  const noSend = await c2.p.evaluate(() => !window.__calls.some((x) => x.method === 'eth_sendTransaction'));
  report('a refused network change sends nothing', noSend && /Troque para BNB Smart Chain/.test(await c2.p.$eval('[data-msg]', (e) => e.textContent)), `no send: ${noSend}`); await c2.ctx.close();
  const c3 = await open(false); await pick(c3.p, 'BNB', 'bsc');
  await c3.p.evaluate(() => { window.__fake.noChain = true; }); await send(c3.p, '0.1');
  report('a missing network is added', await c3.p.evaluate(() => window.__calls.some((x) => x.method === 'wallet_addEthereumChain')), 'add'); await c3.ctx.close();
  const c4 = await open(false); await pick(c4.p, 'USDT', 'tron'); await c4.p.fill('#bi-ap-amount', '0.0000001'); await c4.p.waitForTimeout(100);
  report('too many decimals', /até 6 casas/.test(await c4.p.$eval('[data-msg]', (e) => e.textContent)) && await c4.p.$eval('[data-send]', (b) => b.disabled), 'message and disabled'); await c4.ctx.close();
  const c5 = await open(false); await pick(c5.p, 'ETH', 'ethereum'); await c5.p.fill('#bi-ap-amount', '0.1'); await c5.p.click('[data-send]'); await c5.p.waitForTimeout(150);
  await c5.p.evaluate(() => { const b = document.querySelector('[data-send]'); b.click(); b.click(); }); await c5.p.waitForTimeout(250);
  report('a double click sends once', (await c5.p.evaluate(() => window.__calls.filter((x) => x.method === 'eth_sendTransaction').length)) === 1, 'once'); await c5.ctx.close();
  const msg = (p) => p.$eval('[data-msg]', (e) => e.textContent);
  // the button follows the value
  const v = await open(false); await pick(v.p, 'USDT', 'tron');
  const off = (p) => p.$eval('[data-send]', (b) => b.disabled);
  const empty = await off(v.p); await v.p.fill('#bi-ap-amount', '0'); const zero = await off(v.p); await v.p.fill('#bi-ap-amount', '2,5'); const good = await off(v.p);
  report('the button only with a valid value', empty && zero && !good, `empty ${empty}, zero ${zero}, 2,5 ${good}`); await v.ctx.close();
  // the moments of the drawing
  const m = await open(false); await pick(m.p, 'ETH', 'ethereum'); await m.p.fill('#bi-ap-amount', '0,5'); await m.p.click('[data-send]'); await m.p.waitForTimeout(150);
  const shown = (p, sel) => p.$eval(sel, (e) => e.getClientRects().length > 0);
  const bar = await m.p.$eval('[data-conn]', (e) => e.textContent), label = await m.p.$eval('[data-send]', (e) => e.textContent);
  report('moment 2, connected', bar.includes('Carteira conectada') && bar.includes('0x11...1111') && bar.includes('Ethereum') && label === 'Confirmar doação de 0,5 ETH' && await shown(m.p, '[data-after]') && !(await shown(m.p, '[data-exchange]')), `${bar} / ${label}`);
  const eth = nets().find((n) => n.id === 'ethereum');
  await m.p.evaluate(() => { window.__fake.hold = true; }); await m.p.click('[data-send]'); await m.p.waitForTimeout(200);
  const sum = await m.p.$eval('[data-confirm]', (e) => ({ text: e.textContent, last: e.querySelector('em').textContent, shown: e.getClientRects().length > 0 }));
  const others = await m.p.$$eval('[data-view="crypto"] > *', (es) => es.filter((e) => e.getClientRects().length && !e.matches('h2, [data-confirm]')).map((e) => e.className));
  report('moment 3, confirm in the wallet', sum.shown && others.length === 0 && sum.text.includes(eth.address) && sum.last === eth.address.slice(-4) && sum.text.includes('0,5 ETH') && sum.text.includes(`Confira se o endereço termina em ${eth.address.slice(-4)}`), `others shown: ${others.join()}; ${sum.text.slice(0, 120)}`);
  await m.p.evaluate(() => window.__fake.release()); await m.p.waitForTimeout(200);
  const end = await m.p.$eval('[data-done]', (e) => ({ text: e.textContent, href: (e.querySelector('a') || {}).href, shown: e.getClientRects().length > 0 }));
  report('moment 4, sent', end.shown && end.text.includes('Doação enviada. Obrigado!') && end.text.includes('0,5 ETH pela rede Ethereum.') && end.text.includes('Ver a transação no Etherscan') && end.text.includes('Pode levar alguns minutos para aparecer.') && end.href === eth.tx_url.replace('{tx}', '0xabc'), end.text.slice(0, 120)); await m.ctx.close();
  // the other cases of section 3.3
  const c6 = await open(false); await pick(c6.p, 'ETH', 'ethereum'); await c6.p.evaluate(() => { window.__fake.reject = 'eth_requestAccounts'; }); await c6.p.fill('#bi-ap-amount', '0.1'); await c6.p.click('[data-send]'); await c6.p.waitForTimeout(150);
  report('a refused connection', (await msg(c6.p)) === 'Conexão recusada na carteira. Nada foi enviado.', await msg(c6.p)); await c6.ctx.close();
  const c7 = await open(false); await pick(c7.p, 'ETH', 'ethereum'); await c7.p.evaluate(() => { window.__fake.fail = { method: 'eth_requestAccounts', code: -32002 }; }); await c7.p.fill('#bi-ap-amount', '0.1'); await c7.p.click('[data-send]'); await c7.p.waitForTimeout(150);
  report('a request already open', (await msg(c7.p)) === 'Abra a carteira: há um pedido esperando a sua resposta.', await msg(c7.p)); await c7.ctx.close();
  const c8 = await open(false); await pick(c8.p, 'ETH', 'ethereum'); await c8.p.evaluate(() => { window.__fake.fail = { method: 'eth_sendTransaction', code: -32603 }; }); await send(c8.p, '0.1');
  report('too little balance', (await msg(c8.p)) === 'A carteira recusou o envio: saldo insuficiente para o valor e a taxa.', await msg(c8.p)); await c8.ctx.close();
  const c9 = await open('two'); await pick(c9.p, 'ETH', 'ethereum'); await c9.p.fill('#bi-ap-amount', '0.1'); await c9.p.click('[data-send]'); await c9.p.waitForTimeout(150);
  const list = await c9.p.$$eval('[data-wallets] button', (bs) => bs.map((b) => b.textContent));
  await c9.p.click('[data-wallets] button:nth-of-type(2)'); await c9.p.waitForTimeout(150); await c9.p.click('[data-send]'); await c9.p.waitForTimeout(200);
  report('several wallets: the chosen one sends', list.join() === 'Fake,Second' && await c9.p.evaluate(() => window.__calls.some((x) => x.second && x.method === 'eth_sendTransaction')), list.join()); await c9.ctx.close();
  const c10 = await open(false); await pick(c10.p, 'ETH', 'ethereum'); await c10.p.fill('#bi-ap-amount', '0.1'); await c10.p.click('[data-send]'); await c10.p.waitForTimeout(150);
  await c10.p.evaluate(() => { window.__fake.account = '0x3333333333333333333333333333333333333333'; window.__fake.chain = '0x38'; }); await c10.p.click('[data-send]'); await c10.p.waitForTimeout(250);
  const seq = await c10.p.evaluate(() => window.__calls.map((x) => x.method)), last = await c10.p.evaluate(() => window.__calls.filter((x) => x.method === 'eth_sendTransaction')[0]);
  report('the account and the network are read again just before sending', !!last && last.params[0].from === '0x3333333333333333333333333333333333333333' && seq.lastIndexOf('wallet_switchEthereumChain') < seq.indexOf('eth_sendTransaction') && seq.includes('wallet_switchEthereumChain'), seq.slice(-5).join()); await c10.ctx.close();
  const c11 = await open('none'); await pick(c11.p, 'ETH', 'ethereum');
  report('no wallet in this browser', (await msg(c11.p)).startsWith('Nenhuma carteira de Ethereum neste navegador.') && !(await shown(c11.p, '[data-send]')), await msg(c11.p)); await c11.ctx.close();
  const c12 = await open('none'); await pick(c12.p, 'SOL', 'solana');
  const noQr = !(await shown(c12.p, '[data-qr]')), hint = await c12.p.$eval('[data-qr-hint]', (e) => e.textContent); await c12.p.fill('#bi-ap-amount', '1.5'); await c12.p.waitForFunction(() => document.querySelector('[data-qr-code] svg'), null, { timeout: 4000 }).catch(() => {});
  const qr = await c12.p.$eval('[data-qr-code]', (e) => ({ link: e.dataset.link || '', svg: !!e.querySelector('svg') })), sol = nets().find((n) => n.id === 'solana');
  report('a computer with no wallet: the QR, and never "no wallet" on Solana', noQr && hint.includes('valor') && qr.svg && qr.link.startsWith(`solana:${sol.address}?amount=1.5`) && !(await msg(c12.p)).includes('Nenhuma carteira'), qr.link.slice(0, 80)); await c12.ctx.close();
  const c13 = await open(true); await pick(c13.p, 'USDT', 'bsc'); await c13.p.fill('#bi-ap-amount', '10'); await c13.p.waitForTimeout(150);
  const apps = await c13.p.$$eval('[data-wallets] a', (as) => as.map((a) => a.href));
  report('a phone on EVM: the links open the site in the wallet app, never with an address', apps.length === 2 && apps.every((a) => decodeURIComponent(a).includes('moeda=USDT&rede=bsc&valor=10') && !a.toLowerCase().includes(nets().find((n) => n.id === 'bsc').address.toLowerCase())), apps.join(' ').slice(0, 150)); await c13.ctx.close();
  await browser.close();
  for (const r of rows) console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.name}: ${r.detail}`);
  const bad = rows.filter((r) => !r.ok), sends = rows.filter((r) => /^(send|link) /.test(r.name));
  console.log(`${rows.length} checks, ${bad.length} failed${control ? ' (control run)' : ''}`);
  if (control) { const passed = sends.filter((r) => r.ok); console.log(passed.length ? `BROKEN CONTROL: ${passed.map((r) => r.name).join(', ')}` : 'control: every send check failed, as it must'); process.exit(passed.length ? 1 : 0); }
  process.exit(bad.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
