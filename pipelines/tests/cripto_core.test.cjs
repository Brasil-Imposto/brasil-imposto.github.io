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

test('a value that is not what a valid address looks like cannot break out of the link', () => {
  assert.strictEqual(C.paymentLink('bitcoin', 'a?b=c', 1n, 8, null), 'bitcoin:a%3Fb%3Dc?amount=0.00000001&label=Brasil-Imposto');
  assert.strictEqual(C.openInApp('trust', 'https://x.org/', '1&url=y'), 'https://link.trustwallet.com/open_url?coin_id=1%26url%3Dy&url=https%3A%2F%2Fx.org%2F');
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

// Spec seguranca-doacoes, section 12, item 1: the whole address in groups of 4, nothing dropped.
test('the address in groups of 4, the whole of it', () => {
  assert.deepStrictEqual(C.groupsOf4('TLoXMf8yCEtRJcbR3tqidYd76f1hiAr6cU'), ['TLoX', 'Mf8y', 'CEtR', 'JcbR', '3tqi', 'dYd7', '6f1h', 'iAr6', 'cU']);
  for (const a of ['bc1qevkvnl6rvpexample0000000000000000000', '0xb9472F3cbDBb2B4fC8a4CE4dbC2C3d0f6ab2ff', 'rwJXvM']) assert.strictEqual(C.groupsOf4(a).join(''), a);
  assert.deepStrictEqual(C.groupsOf4(''), []);
});

// Spec seguranca-doacoes, sections 8 and 14 (attack C6): the page reads the transaction on a public node and checks where the money
// went. The answers in fixtures/chain/ are real, recorded from the same nodes; each case has its control (the same answer read
// against another destination must say "wrong").
const fx = (name) => JSON.parse(require('fs').readFileSync(path.join(__dirname, 'fixtures', 'chain', name), 'utf8'));
const PROJECT_EVM = '0x1111111111111111111111111111111111111111';
test('Tron: an address to its 20-byte hex and back, against what the node answers for the USDT contract', async () => {
  assert.strictEqual(C.tronHex('TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'), 'a614f803b6fd780986a42c78ec9c7f77e6ded13c');
  assert.strictEqual(fx('tron-token-info.json').contract_address, '41' + C.tronHex('TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'));
  assert.strictEqual(await C.tronBase58('a614f803b6fd780986a42c78ec9c7f77e6ded13c'), 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t');
  assert.strictEqual(C.tronHex('TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6O'), null);   // O is not in base58
});
test('EVM token: confirmed when a Transfer of the contract reaches the address; wrong otherwise', () => {
  const rec = fx('ethereum-token-receipt.json'), usdt = '0xdAC17F958D2ee523a2206206994597C13D831ec7';
  const log = rec.logs.find((l) => l.address.toLowerCase() === usdt.toLowerCase() && l.topics[0].startsWith('0xddf252ad'));
  const to = '0x' + log.topics[2].slice(-40), units = BigInt(log.data);
  assert.deepStrictEqual(C.checkTransfer('evm', { receipt: rec }, { to, contract: usdt }), { state: 'confirmed', units });
  const wrong = C.checkTransfer('evm', { receipt: rec }, { to: PROJECT_EVM, contract: usdt });
  assert.strictEqual(wrong.state, 'wrong');
  assert.strictEqual(wrong.to.toLowerCase(), to.toLowerCase());
  assert.deepStrictEqual(C.checkTransfer('evm', { receipt: null }, { to, contract: usdt }), { state: 'pending' });
  assert.deepStrictEqual(C.checkTransfer('evm', { receipt: { ...rec, status: '0x0' } }, { to, contract: usdt }), { state: 'failed' });
});
test('EVM token on BNB Smart Chain, from its own recorded answer', () => {
  const rec = fx('bsc-token-receipt.json'), usdt = '0x55d398326f99059fF775485246999027B3197955';
  const log = rec.logs.find((l) => l.address.toLowerCase() === usdt.toLowerCase() && l.topics[0].startsWith('0xddf252ad'));
  assert.strictEqual(C.checkTransfer('evm', { receipt: rec }, { to: '0x' + log.topics[2].slice(-40), contract: usdt }).state, 'confirmed');
  assert.strictEqual(C.checkTransfer('evm', { receipt: rec }, { to: PROJECT_EVM, contract: usdt }).state, 'wrong');
});
test('EVM native coin: the transaction\'s recipient and value', () => {
  const tx = fx('ethereum-native-tx.json'), receipt = fx('ethereum-native-receipt.json');
  assert.deepStrictEqual(C.checkTransfer('evm', { receipt, tx }, { to: tx.to }), { state: 'confirmed', units: BigInt(tx.value) });
  assert.deepStrictEqual(C.checkTransfer('evm', { receipt, tx }, { to: PROJECT_EVM }), { state: 'wrong', to: tx.to });
});
test('Tron TRC-20: the Transfer log of the contract, addresses as 20-byte hex', async () => {
  const info = fx('tron-token-info.json'), ev = fx('tron-token-event.json');
  const to = await C.tronBase58(ev.result.to.slice(2));
  assert.deepStrictEqual(C.checkTransfer('tron', info, { to, contract: 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t' }), { state: 'confirmed', units: BigInt(ev.result.value) });
  const wrong = C.checkTransfer('tron', info, { to: 'TLoXMf8yCEtRJcbR3tqidYd76f1hiAr6cU', contract: 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t' });
  assert.strictEqual(wrong.state, 'wrong');
  assert.strictEqual(await C.tronBase58(wrong.toHex), to);
  assert.deepStrictEqual(C.checkTransfer('tron', {}, { to, contract: 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t' }), { state: 'pending' });
  assert.deepStrictEqual(C.checkTransfer('tron', { ...info, receipt: { result: 'REVERT' } }, { to, contract: 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t' }), { state: 'failed' });
});
test('Bitcoin: an output paying the address, confirmed only once in a block', () => {
  const tx = fx('bitcoin-tx.json'), out = tx.vout[0];
  assert.deepStrictEqual(C.checkTransfer('bitcoin', tx, { to: out.scriptpubkey_address }), { state: 'confirmed', units: BigInt(out.value) });
  assert.deepStrictEqual(C.checkTransfer('bitcoin', { ...tx, status: { confirmed: false } }, { to: out.scriptpubkey_address }), { state: 'pending' });
  const wrong = C.checkTransfer('bitcoin', tx, { to: 'bc1qevkvnl6rvp0000000000000000000000000000' });
  assert.strictEqual(wrong.state, 'wrong');
  assert.strictEqual(wrong.to, out.scriptpubkey_address);
  assert.deepStrictEqual(C.checkTransfer('bitcoin', null, { to: out.scriptpubkey_address }), { state: 'pending' });
});
test('XRP Ledger: validated, tesSUCCESS, the destination and the delivered amount', () => {
  const r = fx('xrp-tx.json'), x = r.result;
  assert.deepStrictEqual(C.checkTransfer('xrp', r, { to: x.Destination }), { state: 'confirmed', units: BigInt(x.meta.delivered_amount) });
  assert.deepStrictEqual(C.checkTransfer('xrp', r, { to: 'rwJXvMProjectProjectProjectProjec' }), { state: 'wrong', to: x.Destination });
  assert.deepStrictEqual(C.checkTransfer('xrp', fx('xrp-not-found.json'), { to: x.Destination }), { state: 'pending' });
  assert.deepStrictEqual(C.checkTransfer('xrp', { result: { ...x, validated: false } }, { to: x.Destination }), { state: 'pending' });
  assert.deepStrictEqual(C.checkTransfer('xrp', { result: { ...x, meta: { ...x.meta, TransactionResult: 'tecUNFUNDED_PAYMENT' } } }, { to: x.Destination }), { state: 'failed' });
});
