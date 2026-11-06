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
// The XRP Ledger through Crossmark (spec seguranca-doacoes, section 11): the result of the submit and the network it reports, set by the
// test. Shaped as the real extension (Crossmark 0.2.19, measured on 2026-11-05 in phase 6): the SDK the wallet injects is
// window.xrpl.crossmark (Crossmark's docs, "installing", option 3); window.crossmark exists but its methods are empty; the network is
// session.network, filled by the sign-in (docs, "session"); getNetwork answers nothing.
const fakeCrossmark = () => {
  const session = { network: null };
  window.crossmark = { methods: undefined };
  window.xrpl = { isCrossmark: true, crossmark: { session, methods: {
    signInAndWait: async () => { session.network = { protocol: 'xrpl', type: window.__fake.xrpNet || 'main' };
      return { response: { data: { address: 'rFakeFakeFakeFakeFakeFakeFakeFake' } } }; },
    getNetwork: () => undefined,
    signAndSubmitAndWait: async (tx) => { window.__calls.push({ method: 'xrp:submit', tx });
      return { response: { data: { resp: { result: { hash: 'ABCDEF0123456789', meta: { TransactionResult: window.__fake.xrpResult || 'tesSUCCESS' } } } } } }; } } } };
};
// P7 (spec seguranca-doacoes, section 14): wallets announcing an icon that is not a data:image (a javascript: link, an outside
// address, markup) and the control, a valid PNG
const hostileWallets = () => {
  const provider = { request: async ({ method }) => (method === 'eth_requestAccounts' ? ['0x1111111111111111111111111111111111111111'] : method === 'eth_chainId' ? '0x1' : null), on: () => {} };
  const icons = { Js: 'javascript:window.__p7=1', Remote: 'https://example.invalid/track.png', Markup: '<img src=x onerror=window.__p7=1>',
    Png: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==' };
  for (const [name, icon] of Object.entries(icons)) addEventListener('eip6963:requestProvider', () => dispatchEvent(new CustomEvent('eip6963:announceProvider', { detail: {
    info: { uuid: 'h-' + name, name, icon, rdns: 'x.' + name.toLowerCase() }, provider } })));
};
const fakeWallets = () => {
  window.__calls = []; window.__fake = { chain: '0x1', reject: null, noChain: false, fail: null, hold: false, account: '0x1111111111111111111111111111111111111111' };
  const f = window.__fake, refuse = () => Object.assign(new Error('refused'), { code: 4001 });
  const evm = { request: async ({ method, params }) => {
    window.__calls.push({ method, params });
    if (f.reject === method) throw refuse();
    if (f.fail && f.fail.method === method) throw Object.assign(new Error('x'), { code: f.fail.code });
    if (method === 'eth_requestAccounts') { if (f.holdConnect) await new Promise((ok) => { f.releaseConnect = ok; }); return [f.account]; }
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
  const tronWeb = { transactionBuilder: { triggerSmartContract: async (contract, fn, opts, params, from) => { window.__calls.push({ method: 'trigger', contract, fn, params, from }); return window.__fake.tronRefuse ? { result: { result: false, message: '5245564552542f6f70636f6465' }, transaction: { txID: 'tx1' } } : { result: { result: true }, transaction: { txID: 'tx1' } }; } },
    trx: { sign: async (t) => { window.__calls.push({ method: 'sign' }); if (f.reject === 'sign') throw 'Confirmation declined by user'; return t; }, sendRawTransaction: async () => ({ result: true, txid: 'tx1' }) } };
  window.tron = { isTronLink: true, tronWeb, request: async ({ method }) => { window.__calls.push({ method: 'tron:' + method }); return ['TQ7vFakeFakeFakeFakeFakeFakeFakek2Pd']; } };
  window.unisat = { requestAccounts: async () => ['bc1qfake'], getChain: async () => ({ enum: window.__fake.btcChain || 'BITCOIN_MAINNET' }), getNetwork: async () => (window.__fake.btcChain && window.__fake.btcChain !== 'BITCOIN_MAINNET' ? 'testnet' : 'livenet'),
    sendBitcoin: async (to, sats) => { window.__calls.push({ method: 'sendBitcoin', to, sats }); return 'btctx'; } };
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
    if (how === 'hostile') await ctx.addInitScript(hostileWallets);
    if (how === 'xrp') await ctx.addInitScript(fakeCrossmark);
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
  // moment 3 (round seguranca-r1, option 1b, D220): the whole address, read back from its groups of 4 in their own block
  const sum = await m.p.$eval('[data-confirm]', (e) => ({ text: e.textContent, groups: [...e.querySelectorAll('.bi-ap-addrblock .bi-ap-groups span')].map((s) => s.textContent),
    label: (e.querySelector('.bi-ap-addrblock .bi-ap-lab') || {}).textContent || '', shown: e.getClientRects().length > 0 }));
  const others = await m.p.$$eval('[data-view="crypto"] > *', (es) => es.filter((e) => e.getClientRects().length && !e.matches('h2, [data-confirm]')).map((e) => e.className));
  report('moment 3, the whole address in groups of 4', sum.shown && others.length === 0 && sum.groups.join('') === eth.address && sum.groups.every((g, k) => g.length === 4 || k === sum.groups.length - 1)
    && sum.label === 'Para: endereço do Brasil-Imposto, rede Ethereum' && sum.text.includes('0,5 ETH') && sum.text.includes('Compare o endereço inteiro com o da carteira, grupo por grupo.')
    && !sum.text.includes('termina em'), `${sum.groups.length} groups; ${sum.text.slice(0, 120)}`);
  await m.p.evaluate(() => window.__fake.release()); await m.p.waitForTimeout(200);
  const end = await m.p.$eval('[data-done]', (e) => ({ text: e.textContent, href: (e.querySelector('a') || {}).href, shown: e.getClientRects().length > 0 }));
  report('moment 4, sent by the wallet and checking the network (option 3c)', end.shown && end.text.includes('Doação enviada. Obrigado!') && end.text.includes('Enviada pela sua carteira') && end.text.includes('0,5 ETH pela rede Ethereum') && end.text.includes('Conferindo na rede Ethereum...') && end.text.includes('Ver a transação no Etherscan') && end.href === eth.tx_url.replace('{tx}', '0xabc'), end.text.slice(0, 120)); await m.ctx.close();
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
  // spec seguranca-doacoes, section 11: the defects of the send, each against a well-behaved control
  const msgOf = (p) => p.$eval('[data-msg]', (e) => (e.hidden ? '' : e.textContent));
  const stepOf = (p) => p.evaluate(() => document.querySelector('.bi-ap-view[data-view="crypto"]').dataset.step || '');
  for (const [name, result, ok] of [['an XRP payment the network refuses (tec) is not "sent"', 'tecUNFUNDED_PAYMENT', false], ['control: tesSUCCESS reaches the sent step', 'tesSUCCESS', true]]) {
    const x = await open('xrp'); await x.p.evaluate((r) => { window.__fake.xrpResult = r; }, result); await pick(x.p, 'XRP', 'xrp-ledger'); await send(x.p, '2');
    const step = await stepOf(x.p), m = await msgOf(x.p);
    report(name, ok ? step === 'done' : step !== 'done' && /recusou/.test(m), `step ${step || 'none'}, message ${m.slice(0, 90)}`); await x.ctx.close();
  }
  for (const [name, change] of [['switching network while the wallet connects cancels the connection', true], ['control: without switching, the wallet connects', false]]) {
    const s = await open(false); await pick(s.p, 'USDT', 'ethereum'); await s.p.evaluate(() => { window.__fake.holdConnect = true; });
    await s.p.fill('#bi-ap-amount', '10'); await s.p.click('[data-send]'); await s.p.waitForTimeout(150);
    if (change) { await s.p.click('.bi-ap-coin[data-coin="USDT"] [data-net-btn="bsc"]'); await s.p.waitForTimeout(150); }
    await s.p.evaluate(() => window.__fake.releaseConnect && window.__fake.releaseConnect()); await s.p.waitForTimeout(250);
    const conn = await shown(s.p, '[data-conn]'), net = await s.p.evaluate(() => document.querySelector('.bi-ap-view[data-view="crypto"]').dataset.net || '');
    report(name, change ? !conn : conn, `connected ${conn}, network ${net}`); await s.ctx.close();
  }
  for (const [name, plant] of [['an error before the confirmation does not lock the button', true], ['control: no error, the send reaches the sent step', false]]) {
    const e = await open(false); await pick(e.p, 'ETH', 'ethereum'); await e.p.fill('#bi-ap-amount', '0.1'); await e.p.click('[data-send]'); await e.p.waitForTimeout(200);
    // the planted error fires once; then the same button has to work again (before the fix the page stayed busy and ignored it)
    if (plant) await e.p.evaluate(() => { const box = document.querySelector('[data-confirm]'); box.replaceChildren = () => { delete box.replaceChildren; throw new Error('planted'); }; });
    await e.p.click('[data-send]'); await e.p.waitForTimeout(300);
    if (plant && (await stepOf(e.p)) !== 'done' && !(await e.p.$eval('[data-send]', (b) => b.hidden))) { await e.p.click('[data-send]'); await e.p.waitForTimeout(300); }
    const step = await stepOf(e.p);
    report(name, step === 'done', `step ${step || 'none'} after ${plant ? 'the error and a second click' : 'one click'}`); await e.ctx.close();
  }
  for (const [name, refuse] of [['Tron: a contract call the node refuses is explained, never sent', true], ['control: an accepted call goes on to the wallet', false]]) {
    const r = await open(false); await r.p.evaluate((v) => { window.__fake.tronRefuse = v; }, refuse); await pick(r.p, 'USDT', 'tron'); await send(r.p, '10');
    const m = await msgOf(r.p), signed = (await r.p.evaluate(() => window.__calls)).some((c) => c.method === 'sign');
    report(name, refuse ? /recusou/.test(m) && !/saldo insuficiente/.test(m) && !signed && (await stepOf(r.p)) !== 'done' : (await stepOf(r.p)) === 'done', `message ${m.slice(0, 80)}, step ${await stepOf(r.p) || 'none'}`); await r.ctx.close();
  }
  for (const [name, chain, ok] of [['UniSat on a test network: nothing is asked', 'BITCOIN_TESTNET4', false], ['control: UniSat on the main network sends', 'BITCOIN_MAINNET', true]]) {
    const u = await open(false); await u.p.evaluate((c) => { window.__fake.btcChain = c; }, chain); await pick(u.p, 'BTC', 'bitcoin'); await send(u.p, '0.001');
    const sent = (await u.p.evaluate(() => window.__calls)).some((c) => c.method === 'sendBitcoin'), m = await msgOf(u.p);
    report(name, ok ? sent : !sent && /rede de testes/.test(m), `sent ${sent}, message ${m.slice(0, 80)}`); await u.ctx.close();
  }
  for (const [name, net, ok] of [['Crossmark on a test network: nothing is submitted', 'test', false], ['control: Crossmark on the main network submits', 'main', true]]) {
    const x = await open('xrp'); await x.p.evaluate((n) => { window.__fake.xrpNet = n; }, net); await pick(x.p, 'XRP', 'xrp-ledger'); await send(x.p, '2');
    const sent = (await x.p.evaluate(() => window.__calls)).some((c) => c.method === 'xrp:submit'), m = await msgOf(x.p);
    report(name, ok ? sent : !sent && /rede de testes/.test(m), `submitted ${sent}, message ${m.slice(0, 80)}`); await x.ctx.close();
  }
  // spec seguranca-doacoes, section 14, attack C6: after the wallet takes the send, the page reads the transaction on the network's public
  // node. The node is answered here: the transfer reaching the project (the control), going to another address, not there yet, down.
  const ethNet = nets().find((n) => n.id === 'ethereum'), usdt = ethNet.coins.find((c) => c.coin === 'USDT').contract;
  const pad32 = (a) => '0x' + a.toLowerCase().replace(/^0x/, '').padStart(64, '0'), OTHER = '0x2222222222222222222222222222222222222222';
  const receipt = (to) => ({ status: '0x1', to: usdt, logs: [{ address: usdt, topics: ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', pad32(FROM), pad32(to)], data: pad32((10000000).toString(16)) }] });
  const node = (ctx, answer) => ctx.route('https://ethereum-rpc.publicnode.com/**', (r) => {
    const cors = { 'access-control-allow-origin': '*', 'access-control-allow-headers': 'content-type', 'access-control-allow-methods': 'POST' };
    if (r.request().method() === 'OPTIONS') return r.fulfill({ status: 204, headers: cors });
    if (answer === 'down') return r.fulfill({ status: 503, headers: cors, body: 'down' });
    return r.fulfill({ status: 200, contentType: 'application/json', headers: cors, body: JSON.stringify({ jsonrpc: '2.0', id: 1, result: answer }) });
  });
  for (const [name, answer, wait, check] of [
    ['C6 control: the transfer reached the project, "Confirmada na rede"', receipt(ethNet.address), 1500, (d) => d.text.includes('Doação confirmada. Obrigado!') && d.text.includes('Confirmada na rede Ethereum') && d.text.includes('Chegou ao endereço do Brasil-Imposto')],
    ['C6: the transfer went to another address, the donor is warned with it whole', receipt(OTHER), 1500, (d) => d.text.includes('A transação não foi para o Brasil-Imposto') && d.groups === OTHER && !d.text.includes('Confirmada')],
    ['C6: not on the network yet, still checking', null, 1500, (d) => d.text.includes('Conferindo na rede Ethereum...') && !d.text.includes('Confirmada')],
    ['C5 in the page: the node down three times, "Não deu para conferir agora"', 'down', 12500, (d) => d.text.includes('Não deu para conferir agora') && d.text.includes('Veja a transação no Etherscan')],
  ]) {
    const k = await open(false); await node(k.ctx, answer); await pick(k.p, 'USDT', 'ethereum'); await send(k.p, '10'); await k.p.waitForTimeout(wait);
    const d = await k.p.$eval('[data-done]', (e) => ({ text: e.textContent, groups: [...e.querySelectorAll('.bi-ap-groups span')].map((s) => s.textContent).join('') }));
    report(name, check(d), d.text.slice(0, 140)); await k.ctx.close();
  }
  const c14 = await open('hostile'); await pick(c14.p, 'ETH', 'ethereum'); await c14.p.fill('#bi-ap-amount', '0.1'); await c14.p.click('[data-send]'); await c14.p.waitForTimeout(250);
  const icons = await c14.p.$$eval('[data-wallets] button', (bs) => bs.map((b) => ({ name: b.textContent.trim(), img: b.querySelector('img') ? (b.querySelector('img').getAttribute('src') || '').slice(0, 24) : null })));
  const byName = (n) => icons.find((x) => x.name.includes(n));
  report('P7: a wallet icon that is not a data:image is not shown', ['Js', 'Remote', 'Markup'].every((n) => byName(n) && byName(n).img === null) && !(await c14.p.evaluate(() => window.__p7)), JSON.stringify(icons));
  report('P7 control: a data:image icon is shown', !!byName('Png') && !!byName('Png').img, JSON.stringify(byName('Png') || null));
  await c14.ctx.close();
  await browser.close();
  for (const r of rows) console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.name}: ${r.detail}`);
  const bad = rows.filter((r) => !r.ok), sends = rows.filter((r) => /^(send|link) /.test(r.name));
  console.log(`${rows.length} checks, ${bad.length} failed${control ? ' (control run)' : ''}`);
  if (control) { const passed = sends.filter((r) => r.ok); console.log(passed.length ? `BROKEN CONTROL: ${passed.map((r) => r.name).join(', ')}` : 'control: every send check failed, as it must'); process.exit(passed.length ? 1 : 0); }
  process.exit(bad.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
