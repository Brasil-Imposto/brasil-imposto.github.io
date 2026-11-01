// The pure part of the crypto send (spec cripto-no-site, section 8, items 1 to 3). BI_CORE points at another copy for the control.
const test = require('node:test');
const assert = require('node:assert');
const path = require('path');
const C = require(process.env.BI_CORE || path.join(__dirname, '..', '..', 'docs', 'superpowers', 'previews', 'assets', 'bi-cripto-core.js'));

test('a typed value becomes whole units, with comma or point, and never rounds', () => {
  assert.strictEqual(C.toUnits('10', 6).units, 10000000n);
  assert.strictEqual(C.toUnits('0,005', 8).units, 500000n);
  assert.strictEqual(C.toUnits('1.5', 18).units, 1500000000000000000n);
  assert.strictEqual(C.toUnits('.5', 6).units, 500000n);
  assert.strictEqual(C.toUnits('0.0000001', 6).code, 'too_many_decimals');
  for (const bad of ['', ' ', 'abc', '0', '0,00', '-1', '1.000,50', '1e3', '0x10']) assert.strictEqual(C.toUnits(bad, 6).code, 'invalid', bad);
});

test('the same value differs between chains: 1 USDT is 6 places on Tron and 18 on BNB Smart Chain', () => {
  assert.strictEqual(C.toUnits('1', 6).units, 1000000n);
  assert.strictEqual(C.toUnits('1', 18).units, 1000000000000000000n);
});

test('the minimum of the first XRP', () => {
  assert.strictEqual(C.belowMin(C.toUnits('0.5', 6).units, '1', 6), true);
  assert.strictEqual(C.belowMin(C.toUnits('1', 6).units, '1', 6), false);
  assert.strictEqual(C.belowMin(C.toUnits('0.5', 6).units, undefined, 6), false);
});

test('the transfer call data', () => {
  assert.strictEqual(C.erc20Transfer('0xb947cC8445841cf40AFCA723804d06855bea7bc7', 1000000n),
    '0xa9059cbb000000000000000000000000b947cc8445841cf40afca723804d06855bea7bc7'
    + '00000000000000000000000000000000000000000000000000000000000f4240');
  assert.strictEqual(C.hex(255n), '0xff');
});

test('whole units back to plain decimal text', () => {
  assert.strictEqual(C.decimalText(1500000n, 6), '1.5');
  assert.strictEqual(C.decimalText(1000000n, 6), '1');
  assert.strictEqual(C.decimalText(5n, 8), '0.00000005');
});

test('payment links in each standard form', () => {
  const sol = 'FUYqFTFwvF8fgm1NmbRXAEERtRLDry1DCQfNgbZyFv8f', btc = 'bc1qevkvnl6rvpfyyyjzk08lckz9xn3936qhp86zna', xrp = 'rwJXvMdap5E7C49ZkfAjpeAMLd15UmEch2';
  assert.strictEqual(C.paymentLink('solana', sol, 1500000000n, 9, null), `solana:${sol}?amount=1.5&label=Brasil-Imposto`);
  assert.strictEqual(C.paymentLink('solana', sol, 2000000n, 6, 'MINT'), `solana:${sol}?amount=2&spl-token=MINT&label=Brasil-Imposto`);
  assert.strictEqual(C.paymentLink('bitcoin', btc, 500000n, 8, null), `bitcoin:${btc}?amount=0.005&label=Brasil-Imposto`);
  assert.strictEqual(C.paymentLink('xrp', xrp, 1000000n, 6, null), `https://xaman.app/detect/request:${xrp}?amount=1&network=XRPL`);
  assert.strictEqual(C.paymentLink('evm', '0x', 1n, 18, null), null);
});

test('opening the site inside a wallet app carries the choice and never an address', () => {
  const url = C.siteLink('https://brasil-imposto.github.io/', 'USDT', 'bsc', '10');
  assert.strictEqual(url, 'https://brasil-imposto.github.io/#apoie-cripto?moeda=USDT&rede=bsc&valor=10');
  assert.strictEqual(C.openInApp('metamask', url, 20000714), 'https://link.metamask.io/dapp/brasil-imposto.github.io/#apoie-cripto?moeda=USDT&rede=bsc&valor=10');
  assert.strictEqual(C.openInApp('trust', url, 20000714), 'https://link.trustwallet.com/open_url?coin_id=20000714&url=' + encodeURIComponent(url));
  assert.strictEqual(C.openInApp('outra', url, 60), null);
});

test('the entry link is read with care: only coin, network and value, each checked', () => {
  const nets = [{ id: 'tron', coins: { USDT: {} } }];
  assert.deepStrictEqual(C.parseEntry('#apoie-cripto?moeda=USDT&rede=tron&valor=10', nets), { coin: 'USDT', net: 'tron', amount: '10' });
  assert.deepStrictEqual(C.parseEntry('#apoie-cripto?moeda=USDT&rede=tron&valor=10&address=rGolpe', nets), { coin: 'USDT', net: 'tron', amount: '10' });
  assert.strictEqual(C.parseEntry('#apoie-cripto?moeda=DOGE&rede=tron', nets), null);
  assert.strictEqual(C.parseEntry('#apoie-cripto?moeda=USDT&rede=marte', nets), null);
  assert.deepStrictEqual(C.parseEntry('#apoie-cripto?moeda=USDT&rede=tron&valor=<script>', nets), { coin: 'USDT', net: 'tron', amount: '' });
  assert.strictEqual(C.parseEntry('#outra', nets), null);
});
