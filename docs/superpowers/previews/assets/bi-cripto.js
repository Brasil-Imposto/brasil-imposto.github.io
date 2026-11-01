// The crypto send inside the Apoie modal (spec cripto-no-site). The destination only ever comes from the block the page carries
// (#bi-cripto-data, built from data/support.json): a link, a field or a wallet never supplies it.
(function () {
  'use strict';
  const C = window.BiCriptoCore, root = document.getElementById('bi-apoie');
  const data = JSON.parse(document.getElementById('bi-cripto-data').textContent);
  const $ = (s) => root.querySelector(s);
  const block = $('.bi-ap-send'), input = $('#bi-ap-amount'), unit = $('[data-unit]'), msg = $('[data-msg]'), note = $('[data-note]');
  const issuer = $('[data-issuer]'), sendBtn = $('[data-send]'), exchangeNet = $('[data-exchange-net]');
  let lastCoin = root.dataset.coin;

  const net = () => data.networks.find((n) => n.id === root.dataset.net);
  const coin = () => net() && net().coins[root.dataset.coin];
  const say = (text) => { msg.textContent = text || ''; msg.hidden = !text; };

  // The value in whole units, or null with the message of section 3.3 of the spec.
  function amount() {
    const n = net(), c = coin();
    if (!input.value.trim()) { say(''); return null; }
    const r = C.toUnits(input.value, c.decimals);
    if (!r.ok) { say(r.code === 'too_many_decimals' ? `${root.dataset.coin} aceita até ${c.decimals} casas depois da vírgula.` : 'Informe um valor maior que zero.'); return null; }
    if (C.belowMin(r.units, n.first_min, c.decimals)) { say(`O primeiro envio para esta conta precisa ser de ${n.first_min} ${root.dataset.coin} ou mais (a reserva da rede).`); return null; }
    say('');
    return r.units;
  }

  function render() {
    const n = net(), c = coin();
    block.hidden = !c;
    if (!c) return;
    unit.textContent = root.dataset.coin;
    exchangeNet.textContent = n.name;
    note.textContent = `A taxa da rede ${n.name} é paga em ${n.native_symbol}, pela sua carteira.`;
    issuer.hidden = c.issuer_listed;
    sendBtn.disabled = amount() === null;
  }

  input.addEventListener('input', render);
  root.addEventListener('bi-cripto-pick', () => {
    if (root.dataset.coin !== lastCoin) { lastCoin = root.dataset.coin; input.value = ''; }   // 10 USDT must never become 10 BTC
    render();
  });
  const entry = C.parseEntry(location.hash, data.networks);
  if (entry && entry.amount) input.value = entry.amount;
  render();
  window.BiCripto = { ready: true };
})();
