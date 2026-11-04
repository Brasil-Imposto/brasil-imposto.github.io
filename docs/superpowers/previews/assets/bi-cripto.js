// The crypto send inside the Apoie modal (spec cripto-no-site). The destination only ever comes from the block the page carries
// (#bi-cripto-data, built from data/support.json): a link, a field or a wallet never supplies it. Only plain transfers: the wallet
// methods used here are a closed list, checked by pipelines/tests/test_support.py.
(function () {
  'use strict';
  const C = window.BiCriptoCore, root = document.getElementById('bi-apoie');
  const data = JSON.parse(document.getElementById('bi-cripto-data').textContent);
  const $ = (s) => root.querySelector(s);
  const view = $('[data-view="crypto"]'), block = $('.bi-ap-send'), input = $('#bi-ap-amount'), unit = $('[data-unit]'), msg = $('[data-msg]');
  const note = $('[data-note]'), issuer = $('[data-issuer]'), conn = $('[data-conn]'), account = $('[data-account]'), connNet = $('[data-conn-net]');
  const wallets = $('[data-wallets]'), qrBox = $('[data-qr]'), qrCode = $('[data-qr-code]'), hint = $('[data-qr-hint]'), sendBtn = $('[data-send]');
  const payLink = $('[data-pay]'), after = $('[data-after]'), exchange = $('[data-exchange]'), exchangeNet = $('[data-exchange-net]');
  const confirmBox = $('[data-confirm]'), done = $('[data-done]');
  const phone = navigator.maxTouchPoints > 0 && /Android|iPhone|iPad/.test(navigator.userAgent);
  const state = { wallet: null, account: null, busy: false, choosing: false, notice: '', chainNow: null };
  const listening = new WeakSet(), evmFound = [], tronFound = [];
  let lastCoin = root.dataset.coin, problem = '';

  const net = () => data.networks.find((n) => n.id === root.dataset.net);
  const coin = () => net() && net().coins[root.dataset.coin];
  const say = (text) => { msg.textContent = text || ''; msg.hidden = !text; };
  const shownValue = (units, c) => C.decimalText(units, c.decimals).replace('.', ',');   // on screen, the Brazilian comma; in a link, the point
  const short = (a) => `${a.slice(0, 4)}...${a.slice(-4)}`;
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; };
  const hasLink = (family) => family === 'solana' || family === 'bitcoin' || family === 'xrp';
  // a wallet's icon only as a data:image, the rule of MetaMask's EIP-6963 library and RainbowKit (spec seguranca-doacoes, section 8)
  const iconOk = (icon) => typeof icon === 'string' && icon.replace(/\n/g, '').startsWith('data:image');

  addEventListener('eip6963:announceProvider', (e) => { if (!evmFound.some((w) => w.info.uuid === e.detail.info.uuid)) { evmFound.push(e.detail); render(); } });
  addEventListener('TIP6963:announceProvider', (e) => { if (!tronFound.some((w) => w.info.uuid === e.detail.info.uuid)) { tronFound.push(e.detail); render(); } });

  // The wallets of this browser for a network: announced ones first, then what older wallets and app browsers inject.
  function found(family) {
    if (family === 'evm') return evmFound.length ? evmFound : window.ethereum ? [{ info: { uuid: 'injected', name: 'Carteira deste navegador' }, provider: window.ethereum }] : [];
    if (family === 'tron') return tronFound.length ? tronFound : window.tron ? [{ info: { uuid: 'tron', name: 'TronLink' }, provider: window.tron }] : [];
    if (family === 'bitcoin') return window.unisat ? [{ info: { uuid: 'unisat', name: 'UniSat' }, provider: window.unisat }] : [];
    if (family === 'xrp') return window.xrpl && window.xrpl.isCrossmark ? [{ info: { uuid: 'crossmark', name: 'Crossmark' }, provider: null }] : [];
    return [];
  }

  // The value in whole units, or null, leaving the message of section 3.3 of the spec in `problem`.
  function amount() {
    const n = net(), c = coin(), name = root.dataset.coin;
    problem = '';
    if (!input.value.trim()) return null;
    const r = C.toUnits(input.value, c.decimals);
    if (!r.ok) { problem = r.code === 'too_many_decimals' ? `${name} aceita até ${c.decimals} casas depois da vírgula.` : 'Informe um valor maior que zero.'; return null; }
    if (C.belowMin(r.units, n.first_min, c.decimals)) { problem = `O primeiro envio para esta conta precisa ser de ${n.first_min} ${name} ou mais (a reserva da rede).`; return null; }
    return r.units;
  }

  function render() {
    const n = net(), c = coin();
    block.hidden = !c;
    if (!c) return;
    const name = root.dataset.coin, units = amount(), text = units === null ? '' : shownValue(units, c);
    const here = found(n.family), link = units === null ? null : C.paymentLink(n.family, n.address, units, c.decimals, c.contract);
    let line = problem || state.notice;
    unit.textContent = name;
    exchangeNet.textContent = n.name;
    issuer.hidden = c.issuer_listed;
    note.textContent = `A taxa da rede ${n.name} é paga em ${n.native_symbol}, pela sua carteira.`;
    [qrBox, payLink, wallets, conn, after, hint, sendBtn].forEach((x) => { x.hidden = true; });
    exchange.hidden = false;
    const button = (label, on) => { sendBtn.hidden = false; sendBtn.textContent = label; sendBtn.disabled = !on || state.busy; };
    if (state.wallet) {                                                     // moment 2 of the drawing: connected, the last step
      conn.hidden = false; account.textContent = short(state.account); connNet.textContent = ` · ${n.name}`;
      button(text ? `Confirmar doação de ${text} ${name}` : 'Confirmar doação', units !== null);
      after.hidden = false; exchange.hidden = true;
    } else if (state.choosing) {                                            // several wallets: the donor picks one
      wallets.replaceChildren(...here.map((w) => {
        const b = el('button', '', w.info.name); b.type = 'button';
        if (iconOk(w.info.icon)) { const i = el('img'); i.src = w.info.icon; i.alt = ''; b.prepend(i); }
        b.addEventListener('click', () => pickWallet(w, n));
        return b;
      }));
      wallets.hidden = false;
    } else if (here.length) {                                               // a wallet in this browser
      button('Conectar carteira', units !== null);
    } else if (phone && hasLink(n.family)) {                                // the wallet app, filled in by a payment link
      if (link) {
        payLink.hidden = false; payLink.textContent = `Confirmar doação de ${text} ${name}`; payLink.href = link;
        note.textContent += ` Se a carteira não trouxer o valor, digite ${text} ${name}. Confira se o endereço termina em ${n.address.slice(-4)}.`;
      } else button('Confirmar doação', false);
    } else if (phone) {                                                     // the site inside the wallet app, where the same flow runs
      wallets.replaceChildren(...appLinks(n));
      wallets.hidden = !wallets.children.length;
      if (!wallets.children.length) line = line || 'Abra esta página no navegador do app da sua carteira, ou copie o endereço acima.';
    } else if (hasLink(n.family)) {                                         // a computer with no wallet: a QR code for the phone
      if (n.family !== 'solana') line = line || `Nenhuma carteira de ${n.name} neste navegador.`;   // Solana by extension is outside version 1
      if (link) { qrBox.hidden = false; drawQr(link); } else { hint.hidden = false; hint.textContent = 'Digite o valor para ver o QR para o celular.'; }
    } else {
      line = line || `Nenhuma carteira de ${n.name} neste navegador. Instale uma extensão ou copie o endereço acima.`;
    }
    say(line);
  }

  function appLinks(n) {
    const url = C.siteLink(location.href.split('#')[0], root.dataset.coin, n.id, input.value.trim());
    return [['metamask', 'Abrir na MetaMask'], ['trust', 'Abrir na Trust Wallet']].filter(() => n.family === 'evm').map(([id, label]) => {
      const a = el('a', '', label); a.href = C.openInApp(id, url, n.trust_coin_id); return a;
    });
  }

  let qrLoading = null;
  function drawQr(link) {
    if (qrCode.dataset.link === link && qrCode.firstChild) return;
    qrCode.dataset.link = link;
    qrLoading = qrLoading || new Promise((ok, no) => { const s = el('script'); s.src = 'assets/vendor/qrcode.js'; s.onload = ok; s.onerror = no; document.head.appendChild(s); });
    qrLoading.then(() => {
      if (qrCode.dataset.link !== link) return;
      const q = window.qrcode(0, 'M'); q.addData(link); q.make();
      qrCode.innerHTML = q.createSvgTag({ cellSize: 4, margin: 2, scalable: true });
    }).catch(() => { qrBox.hidden = true; });
  }

  // Moment 3 of the drawing: what goes to the wallet, the whole address with its last 4 characters marked, while the wallet asks.
  function showConfirm(n, c, units) {
    const name = root.dataset.coin, end = n.address.slice(-4), em = el('em', '', end);
    const row = (label, ...value) => { const d = el('div'), b = el('b'); b.append(...value); d.append(el('span', '', label), b); return d; };
    const sum = el('div', 'bi-ap-sum');
    sum.append(row('Moeda', name), row('Rede', $('.bi-ap-coin:not([hidden]) [aria-pressed="true"]').textContent), row('Valor', `${shownValue(units, c)} ${name}`), row('Para', n.address.slice(0, -4), em));
    const wait = el('div', 'bi-ap-wait');
    wait.append(el('span', 'bi-ap-spin'), el('span', '', `Confirme ${phone ? 'no app' : 'na janela'} da sua carteira. Confira se o endereço termina em ${end}.`));
    confirmBox.replaceChildren(sum, wait);
    if (c.contract) confirmBox.append(el('p', 'bi-ap-note', `Você vai precisar de um pouco de ${n.native_symbol} na carteira para a taxa da rede.`));
    confirmBox.hidden = false; view.dataset.step = 'confirm';
  }

  // Moment 4: the result, with the link to the transaction. The site only knows the wallet took it (spec, section 3.3).
  function finished(hash, n, c, units) {
    const a = el('a', '', `Ver a transação no ${n.explorer}`), p = el('p'), ck = el('span', 'bi-ap-ck', '✓');
    a.href = encodeURI(n.tx_url).replace('%7Btx%7D', encodeURIComponent(hash)); a.target = '_blank'; a.rel = 'noopener';
    p.append(a);
    done.replaceChildren(ck, el('h3', '', 'Doação enviada. Obrigado!'), el('p', '', `${shownValue(units, c)} ${root.dataset.coin} pela rede ${n.name}.`), p, el('p', '', 'Pode levar alguns minutos para aparecer.'));
    confirmBox.hidden = true; done.hidden = false; view.dataset.step = 'done';
  }

  function backToStart() {
    delete view.dataset.step;
    confirmBox.hidden = true; done.hidden = true;
  }

  async function ensureChain(p, n) {
    const want = C.hex(BigInt(n.chain_id));
    state.chainNow = await p.request({ method: 'eth_chainId' });
    if (state.chainNow === want) return;
    const change = () => p.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: want }] });
    const notMoved = (e) => { if (e && e.code === -32002) throw e; throw { code: 'wrong_chain' }; };
    try { await change(); } catch (e) {
      if (!(e && e.code === 4902 && n.add_chain)) notMoved(e);
      try { await p.request({ method: 'wallet_addEthereumChain', params: [Object.assign({ chainId: want }, n.add_chain)] }); await change(); } catch (x) { notMoved(x); }
    }
    if (await p.request({ method: 'eth_chainId' }) !== want) throw { code: 'wrong_chain' };
  }

  async function connect(w, n) {
    if (n.family === 'evm' || n.family === 'tron') return (await w.provider.request({ method: 'eth_requestAccounts' }))[0];
    if (n.family === 'bitcoin') return (await w.provider.requestAccounts())[0];
    await new Promise((ok, no) => { const s = el('script'); s.src = 'assets/vendor/crossmark-sdk.js'; s.onload = ok; s.onerror = no; document.head.appendChild(s); });
    for (let i = 0; i < 40 && !(window.crossmark && window.crossmark.methods); i++) await new Promise((ok) => setTimeout(ok, 100));
    const r = await window.crossmark.methods.signInAndWait();
    return r.response.data.address;
  }

  async function transfer(w, n, c, units) {
    if (n.family === 'evm') {
      const p = w.provider;
      state.account = (await p.request({ method: 'eth_requestAccounts' }))[0];   // the account and the network, read again right before the send
      await ensureChain(p, n);
      const tx = c.contract ? { from: state.account, to: c.contract, data: C.erc20Transfer(n.address, units) } : { from: state.account, to: n.address, value: C.hex(units) };
      return p.request({ method: 'eth_sendTransaction', params: [tx] });
    }
    if (n.family === 'tron') {
      const t = w.provider.tronWeb;   // false until the donor authorizes, so it is read only here
      const { transaction } = await t.transactionBuilder.triggerSmartContract(c.contract, 'transfer(address,uint256)', { feeLimit: 100000000 },
        [{ type: 'address', value: n.address }, { type: 'uint256', value: units.toString() }], state.account);
      const r = await t.trx.sendRawTransaction(await t.trx.sign(transaction));
      if (!r.result) throw { code: 'refused' };
      return r.txid || transaction.txID;
    }
    if (n.family === 'bitcoin') return w.provider.sendBitcoin(n.address, Number(units));
    const r = await window.crossmark.methods.signAndSubmitAndWait({ TransactionType: 'Payment', Account: state.account, Destination: n.address, Amount: units.toString() });
    return r.response.data.resp.result.hash;
  }

  const refused = (e) => e === 'Confirmation declined by user' || (e && e.code === 4001);
  const walletIsOn = (hex) => { const k = data.networks.find((x) => x.chain_id !== undefined && C.hex(BigInt(x.chain_id)) === hex); return k ? `na rede ${k.name}` : 'em outra rede'; };
  function explain(e, n, step) {
    if (e && e.code === -32002) return 'Abra a carteira: há um pedido esperando a sua resposta.';
    if (e && e.code === 'wrong_chain') return `A carteira continua ${walletIsOn(state.chainNow)}. Troque para ${n.name} para enviar.`;
    if (step === 'connect') return refused(e) ? 'Conexão recusada na carteira. Nada foi enviado.' : 'Desbloqueie a carteira e tente de novo.';
    return refused(e) ? 'Envio cancelado na carteira. Nada foi enviado.' : 'A carteira recusou o envio: saldo insuficiente para o valor e a taxa.';
  }

  async function pickWallet(w, n) {
    state.busy = true; state.notice = ''; render();
    try {
      state.account = await connect(w, n); state.wallet = w;
      if (w.provider && w.provider.on && !listening.has(w.provider)) {
        listening.add(w.provider);
        w.provider.on('accountsChanged', (a) => { state.account = a[0]; if (!a[0]) state.wallet = null; render(); });
      }
    } catch (e) { state.notice = explain(e, n, 'connect'); } finally { state.busy = false; state.choosing = false; render(); }
  }

  sendBtn.addEventListener('click', async () => {
    const n = net(), c = coin(), units = amount();
    if (units === null || state.busy) return;
    if (!state.wallet) {
      const here = found(n.family);
      if (here.length > 1) { state.choosing = true; render(); return; }
      pickWallet(here[0], n);
      return;
    }
    state.busy = true; state.notice = ''; showConfirm(n, c, units);
    try { finished(await transfer(state.wallet, n, c, units), n, c, units); } catch (e) { backToStart(); state.notice = explain(e, n, 'send'); } finally { state.busy = false; render(); }
  });

  $('[data-change]').addEventListener('click', () => {
    state.wallet = null; state.account = null; state.notice = ''; state.choosing = found(net().family).length > 1; render();
  });
  payLink.addEventListener('click', () => setTimeout(() => {
    if (document.visibilityState === 'visible') { state.notice = 'Nenhum app abriu? Use o QR em outro aparelho ou copie o endereço acima.'; render(); }
  }, 2500));
  input.addEventListener('input', () => { state.notice = ''; render(); });
  root.addEventListener('bi-cripto-pick', () => {
    if (root.dataset.coin !== lastCoin) { lastCoin = root.dataset.coin; input.value = ''; }   // 10 USDT must never become 10 BTC
    state.wallet = null; state.account = null; state.choosing = false; state.notice = '';
    render();
  });
  // Nothing is sent again by itself: coming back to the view after a send starts from the beginning (spec, section 3.3).
  root.addEventListener('bi-cripto-view', () => { if (view.dataset.step && !state.busy) { backToStart(); input.value = ''; render(); } });

  dispatchEvent(new Event('eip6963:requestProvider'));
  dispatchEvent(new Event('TIP6963:requestProvider'));
  const entry = C.parseEntry(location.hash, data.networks);
  if (entry && entry.amount) input.value = entry.amount;
  render();
  window.BiCripto = { ready: true };
})();
