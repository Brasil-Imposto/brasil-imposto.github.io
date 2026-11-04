// The pure part of the crypto send (spec cripto-no-site): no page and no wallet, so node can test it. Every value in whole units is a
// BigInt: never a floating point number.
(function (root, make) {
  if (typeof module === 'object' && module.exports) module.exports = make(); else root.BiCriptoCore = make();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const fail = (code, extra) => Object.assign({ ok: false, code }, extra);

  // "10", "0,005" or ".5" to whole units. More decimal places than the coin has is an error, never a rounding.
  function toUnits(text, decimals) {
    const s = String(text).trim().replace(',', '.');
    if (!/^(\d+(\.\d+)?|\.\d+)$/.test(s)) return fail('invalid');
    const [whole, frac = ''] = s.split('.');
    if (frac.length > decimals) return fail('too_many_decimals', { decimals });
    const units = BigInt((whole || '0') + frac.padEnd(decimals, '0'));
    return units > 0n ? { ok: true, units } : fail('invalid');
  }
  const belowMin = (units, min, decimals) => min !== undefined && units < toUnits(min, decimals).units;
  const pad = (hex) => hex.padStart(64, '0');
  const erc20Transfer = (to, units) => '0xa9059cbb' + pad(to.slice(2).toLowerCase()) + pad(units.toString(16));
  const hex = (units) => '0x' + units.toString(16);

  function decimalText(units, decimals) {
    const s = units.toString().padStart(decimals + 1, '0');
    const frac = s.slice(s.length - decimals).replace(/0+$/, '');
    return s.slice(0, s.length - decimals) + (frac ? '.' + frac : '');
  }
  // A link the wallet itself turns into the transaction (Solana Pay, BIP-321, Xaman's payment request); null where a network has none.
  // Every value that goes into a link is encoded, even those a valid address or amount leaves unchanged.
  function paymentLink(family, address, units, decimals, token) {
    const a = encodeURIComponent(address), n = encodeURIComponent(decimalText(units, decimals));
    if (family === 'solana') return `solana:${a}?amount=${n}${token ? `&spl-token=${encodeURIComponent(token)}` : ''}&label=Brasil-Imposto`;
    if (family === 'bitcoin') return `bitcoin:${a}?amount=${n}&label=Brasil-Imposto`;
    if (family === 'xrp') return `https://xaman.app/detect/request:${a}?amount=${n}&network=XRPL`;
    return null;
  }
  const siteLink = (base, coin, net, amount) => `${base}#apoie-cripto?moeda=${encodeURIComponent(coin)}&rede=${encodeURIComponent(net)}&valor=${encodeURIComponent(amount)}`;
  function openInApp(wallet, url, coinId) {
    if (wallet === 'metamask') return 'https://link.metamask.io/dapp/' + url.replace(/^https?:\/\//, '');
    if (wallet === 'trust') return `https://link.trustwallet.com/open_url?coin_id=${encodeURIComponent(coinId)}&url=${encodeURIComponent(url)}`;
    return null;
  }
  // The site's own link only ever chooses: the coin and the network must exist in the page's data, and nothing else in it is read.
  function parseEntry(hash, networks) {
    const m = /^#apoie-cripto\?(.*)$/.exec(hash || '');
    if (!m) return null;
    const q = new URLSearchParams(m[1]), coin = q.get('moeda'), net = q.get('rede'), valor = q.get('valor') || '';
    const n = networks.find((x) => x.id === net);
    if (!n || !Object.prototype.hasOwnProperty.call(n.coins, coin)) return null;
    return { coin, net, amount: /^[\d.,]{1,30}$/.test(valor) ? valor : '' };
  }
  // The whole address in groups of 4 (spec seguranca-doacoes, section 12; Trezor Suite shows "chunks of 4 characters").
  const groupsOf4 = (a) => String(a).match(/.{1,4}/g) || [];

  // Tron addresses: base58 (T...) on screen, 20 bytes of hex in a node's logs.
  const B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
  function tronHex(address) {
    let n = 0n;
    for (const ch of String(address)) { const i = B58.indexOf(ch); if (i < 0) return null; n = n * 58n + BigInt(i); }
    const h = n.toString(16).padStart(50, '0');
    return h.length === 50 && h.startsWith('41') ? h.slice(2, 42) : null;
  }
  async function tronBase58(hex20) {   // base58check: 0x41, the 20 bytes, the first 4 bytes of a double SHA-256
    const bytes = Uint8Array.from(('41' + hex20).match(/../g).map((x) => parseInt(x, 16)));
    const sha = async (b) => new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', b));
    const check = (await sha(await sha(bytes))).slice(0, 4);
    let n = BigInt('0x' + [...bytes, ...check].map((b) => b.toString(16).padStart(2, '0')).join('')), out = '';
    while (n > 0n) { out = B58[Number(n % 58n)] + out; n /= 58n; }
    return out;
  }

  // Where the money of one transaction went, read from a public node (spec seguranca-doacoes, sections 8 and 14, attack C6). The
  // states: confirmed (it reached the address; units is what arrived), wrong (it went elsewhere; to, or toHex on Tron), pending
  // (not on the network yet, or not final), failed (the network refused it), unknown (an answer this code cannot read).
  // Solana Pay: finding the transaction "doesn't guarantee that a valid transfer with the expected amount and recipient happened".
  const TRANSFER = 'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
  const low = (s) => String(s || '').toLowerCase().replace(/^0x/, '');
  const word = (topic) => low(topic).slice(-40);   // the address in a 32-byte topic
  const transfers = (logs, contractHex) => (logs || []).filter((l) => low(l.address).slice(-40) === contractHex && low(l.topics && l.topics[0]) === TRANSFER);
  function checkTransfer(family, r, x) {
    if (family === 'evm') {
      const rec = r && r.receipt;
      if (!rec) return { state: 'pending' };
      if (rec.status !== '0x1') return { state: 'failed' };
      if (x.contract) {
        const logs = transfers(rec.logs, low(x.contract)), ours = logs.find((l) => word(l.topics[2]) === low(x.to));
        if (ours) return { state: 'confirmed', units: BigInt('0x' + (low(ours.data) || '0')) };
        return { state: 'wrong', to: logs.length ? '0x' + word(logs[0].topics[2]) : rec.to };
      }
      if (!r.tx) return { state: 'pending' };
      return low(r.tx.to) === low(x.to) ? { state: 'confirmed', units: BigInt(r.tx.value) } : { state: 'wrong', to: r.tx.to };
    }
    if (family === 'tron') {
      if (!r || !r.id) return { state: 'pending' };
      if (!r.receipt || r.receipt.result !== 'SUCCESS') return { state: 'failed' };
      const logs = transfers(r.log, tronHex(x.contract)), ours = logs.find((l) => word(l.topics[2]) === tronHex(x.to));
      if (ours) return { state: 'confirmed', units: BigInt('0x' + (low(ours.data) || '0')) };
      return { state: 'wrong', toHex: logs.length ? word(logs[0].topics[2]) : null };
    }
    if (family === 'bitcoin') {
      if (!r || !Array.isArray(r.vout)) return { state: 'pending' };
      const paid = r.vout.filter((o) => o.scriptpubkey_address === x.to).reduce((s, o) => s + BigInt(o.value), 0n);
      if (!paid) return { state: 'wrong', to: (r.vout.find((o) => o.scriptpubkey_address) || {}).scriptpubkey_address || null };
      return r.status && r.status.confirmed ? { state: 'confirmed', units: paid } : { state: 'pending' };
    }
    if (family === 'xrp') {
      const t = r && r.result;
      if (!t || t.error === 'txnNotFound' || !t.validated) return { state: 'pending' };
      if (!t.meta || t.meta.TransactionResult !== 'tesSUCCESS') return { state: 'failed' };
      if (t.Destination !== x.to) return { state: 'wrong', to: t.Destination };
      return typeof t.meta.delivered_amount === 'string' ? { state: 'confirmed', units: BigInt(t.meta.delivered_amount) } : { state: 'unknown' };
    }
    return { state: 'unknown' };
  }
  return { toUnits, belowMin, erc20Transfer, hex, decimalText, paymentLink, siteLink, openInApp, parseEntry, groupsOf4, tronHex, tronBase58, checkTransfer };
}));
