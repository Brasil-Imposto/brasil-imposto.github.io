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
  function paymentLink(family, address, units, decimals, token) {
    const n = decimalText(units, decimals);
    if (family === 'solana') return `solana:${address}?amount=${n}${token ? `&spl-token=${token}` : ''}&label=Brasil-Imposto`;
    if (family === 'bitcoin') return `bitcoin:${address}?amount=${n}&label=Brasil-Imposto`;
    if (family === 'xrp') return `https://xaman.app/detect/request:${address}?amount=${n}&network=XRPL`;
    return null;
  }
  const siteLink = (base, coin, net, amount) => `${base}#apoie-cripto?moeda=${encodeURIComponent(coin)}&rede=${encodeURIComponent(net)}&valor=${encodeURIComponent(amount)}`;
  function openInApp(wallet, url, coinId) {
    if (wallet === 'metamask') return 'https://link.metamask.io/dapp/' + url.replace(/^https?:\/\//, '');
    if (wallet === 'trust') return `https://link.trustwallet.com/open_url?coin_id=${coinId}&url=${encodeURIComponent(url)}`;
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
  return { toUnits, belowMin, erc20Transfer, hex, decimalText, paymentLink, siteLink, openInApp, parseEntry };
}));
