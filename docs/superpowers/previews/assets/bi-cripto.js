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
  // spec seguranca-doacoes, section 12, item 1 (round seguranca-r1, option 1b): the whole address, never its last 4 characters
  const COMPARE = 'Compare o endereço inteiro com o da carteira, grupo por grupo. Se a carteira encurtar o endereço, abra o endereço inteiro nela.';
  const groupLine = (a) => { const d = el('div', 'bi-ap-groups'); C.groupsOf4(a).forEach((g) => d.append(el('span', '', g))); return d; };
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
        note.textContent += ` Se a carteira não trouxer o valor, digite ${text} ${name}. ${COMPARE}`;
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

  // Moment 3: what goes to the wallet while the wallet asks; the whole address in groups of 4, in its own block (option 1b).
  function showConfirm(n, c, units) {
    const name = root.dataset.coin, netName = $('.bi-ap-coin:not([hidden]) [aria-pressed="true"]').textContent;
    const row = (label, ...value) => { const d = el('div'), b = el('b'); b.append(...value); d.append(el('span', '', label), b); return d; };
    const sum = el('div', 'bi-ap-sum');
    sum.append(row('Moeda', name), row('Rede', netName), row('Valor', `${shownValue(units, c)} ${name}`));
    const to = el('div', 'bi-ap-addrblock');
    to.append(el('span', 'bi-ap-lab', `Para: endereço do Brasil-Imposto, rede ${netName}`), groupLine(n.address));
    const wait = el('div', 'bi-ap-wait');
    wait.append(el('span', 'bi-ap-spin'), el('span', '', `Confirme ${phone ? 'no app' : 'na janela'} da sua carteira. ${COMPARE}`));
    confirmBox.replaceChildren(sum, to, wait);
    if (c.contract) confirmBox.append(el('p', 'bi-ap-note', `Você vai precisar de um pouco de ${n.native_symbol} na carteira para a taxa da rede.`));
    confirmBox.hidden = false; view.dataset.step = 'confirm';
  }

  // Moment 4 (option 3c): sent by the wallet, then confirmed on the network, with the destination and the value read on a public node
  // (spec seguranca-doacoes, sections 8 and 12; Solana Pay: finding the transaction "doesn't guarantee that a valid transfer with the
  // expected amount and recipient happened"). Solana is sent in the wallet app, so the site never has its transaction.
  function txLink(hash, n) {
    const a = el('a', '', `Ver a transação no ${n.explorer}`), p = el('p');
    a.href = encodeURI(n.tx_url).replace('%7Btx%7D', encodeURIComponent(hash)); a.target = '_blank'; a.rel = 'noopener';
    p.append(a); return p;
  }
  function step(state, text, sub) {
    const li = el('li', state), dot = el('span', 'bi-ap-dot ' + state, state === 'ok' ? '✓' : state === 'none' ? '-' : ''), d = el('div');
    if (state === 'wait') dot.append(el('span', 'bi-ap-spin'));
    d.append(el('b', '', text)); if (sub) d.append(el('small', '', sub)); li.append(dot, d); return li;
  }
  function drawDone(hash, n, c, units, st, to) {
    const name = root.dataset.coin, value = `${shownValue(units, c)} ${name}`;
    if (st === 'wrong') {
      const ck = el('div', 'bi-ap-ck bi-ap-ck-bad', '!'), parts = [ck, el('h3', '', 'A transação não foi para o Brasil-Imposto')];
      parts.push(el('p', '', `A rede mostra que a sua carteira enviou ${value} para outro endereço, que não é o do projeto${to ? ':' : '.'}`));
      if (to) { const box = el('div', 'bi-ap-addrblock bi-ap-badaddr'); box.append(groupLine(to)); parts.push(box); }
      parts.push(el('p', '', 'A sua carteira ou o seu aparelho pode ter sido adulterado. Não envie de novo por esta carteira.'), txLink(hash, n));
      done.replaceChildren(...parts);
    } else {
      const list = el('ol', 'bi-ap-chk');
      list.append(step('ok', 'Enviada pela sua carteira', `${value} pela rede ${n.name}`));
      if (st === 'ok') list.append(step('ok', `Confirmada na rede ${n.name}`, 'Chegou ao endereço do Brasil-Imposto'));
      if (st === 'wait') list.append(step('wait', `Conferindo na rede ${n.name}...`, 'Costuma levar menos de um minuto'));
      if (st === 'late') list.append(step('wait', 'Ainda não apareceu na rede', 'Pode levar alguns minutos. Seguimos conferindo por até 30 minutos.'));
      if (st === 'none') list.append(step('none', 'Não deu para conferir agora', `Veja a transação no ${n.explorer}`));
      if (st === 'failed') list.append(step('none', 'A rede recusou a transação', 'O valor não chegou ao Brasil-Imposto.'));
      const settled = st === 'ok' || st === 'none', ck = el('div', 'bi-ap-ck' + (st === 'failed' ? ' bi-ap-ck-bad' : settled ? '' : ' bi-ap-ck-wait'), settled ? '✓' : st === 'failed' ? '!' : '');
      if (!settled && st !== 'failed') ck.append(el('span', 'bi-ap-spin'));
      const title = st === 'ok' ? 'Doação confirmada. Obrigado!' : st === 'failed' ? 'A rede recusou a doação' : 'Doação enviada. Obrigado!';
      done.replaceChildren(ck, el('h3', '', title), list, txLink(hash, n));
    }
    confirmBox.hidden = true; done.hidden = false; view.dataset.step = 'done';
  }
  // The node of the network (data/support.json, "node"), asked for one transaction, answered as BiCriptoCore.checkTransfer reads it.
  async function ask(n, c, hash) {
    const post = (body) => fetch(n.node, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) })
      .then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); });
    if (n.family === 'evm') {
      const rpc = (method) => post({ jsonrpc: '2.0', id: 1, method, params: [hash] }).then((r) => r.result || null);
      const receipt = await rpc('eth_getTransactionReceipt');
      return { receipt, tx: receipt && !c.contract ? await rpc('eth_getTransactionByHash') : null };
    }
    if (n.family === 'tron') return post({ value: hash });
    if (n.family === 'xrp') return post({ method: 'tx', params: [{ transaction: hash }] });
    const r = await fetch(`${n.node}/${encodeURIComponent(hash)}`);   // bitcoin: not found yet is 404 or 400
    if (r.status === 404 || r.status === 400) return null;
    if (!r.ok) throw new Error(String(r.status));
    return r.json();
  }
  let watching = 0;
  async function watch(hash, n, c, units) {
    const id = ++watching, started = Date.now(), sleep = (ms) => new Promise((ok) => setTimeout(ok, ms));
    let misses = 0;
    while (id === watching) {
      const age = Date.now() - started;
      if (age > 30 * 60000) return drawDone(hash, n, c, units, 'none');
      let r;
      try { r = C.checkTransfer(n.family, await ask(n, c, hash), { to: n.address, contract: c.contract }); misses = 0; } catch (_) { misses++; r = { state: misses >= 3 ? 'none' : 'pending' }; }
      if (id !== watching) return;
      if (r.state === 'confirmed') return drawDone(hash, n, c, units, 'ok');
      if (r.state === 'wrong') return drawDone(hash, n, c, units, 'wrong', r.to || (r.toHex ? await C.tronBase58(r.toHex) : null));
      if (r.state === 'failed') return drawDone(hash, n, c, units, 'failed');
      if (r.state !== 'pending') return drawDone(hash, n, c, units, 'none');   // no answer three times, or one this code cannot read
      const late = age > 3 * 60000;
      drawDone(hash, n, c, units, late ? 'late' : 'wait');
      await sleep(late ? 30000 : 5000);
    }
  }

  function backToStart() {
    watching++;
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
      const built = await t.transactionBuilder.triggerSmartContract(c.contract, 'transfer(address,uint256)', { feeLimit: 100000000 },
        [{ type: 'address', value: n.address }, { type: 'uint256', value: units.toString() }], state.account);
      if (!(built && built.result && built.result.result === true)) {   // spec seguranca-doacoes, section 11: the refusal, explained
        const m = built && built.result && built.result.message;
        throw { code: 'tron_refused', detail: m ? String(m).match(/../g).map((x) => String.fromCharCode(parseInt(x, 16))).join('').replace(/[^ -~]/g, '') : '' };
      }
      const { transaction } = built;
      const r = await t.trx.sendRawTransaction(await t.trx.sign(transaction));
      if (!r.result) throw { code: 'refused' };
      return r.txid || transaction.txID;
    }
    if (n.family === 'bitcoin') {
      const u = w.provider, chain = u.getChain ? await u.getChain() : null;
      if (chain ? chain.enum !== 'BITCOIN_MAINNET' : u.getNetwork && (await u.getNetwork()) !== 'livenet') throw { code: 'test_network' };
      return u.sendBitcoin(n.address, Number(units));
    }
    const xnet = window.crossmark.methods.getNetwork && window.crossmark.methods.getNetwork();
    if (xnet && /test|dev/i.test(String(xnet.type || xnet.label || ''))) throw { code: 'test_network' };
    const r = await window.crossmark.methods.signAndSubmitAndWait({ TransactionType: 'Payment', Account: state.account, Destination: n.address, Amount: units.toString() });
    const res = r.response.data.resp.result, code = (res.meta && res.meta.TransactionResult) || res.engine_result;
    if (code !== 'tesSUCCESS') throw { code: 'xrp_refused', detail: String(code || '') };   // spec seguranca-doacoes, section 11
    return res.hash;
  }

  const refused = (e) => e === 'Confirmation declined by user' || (e && e.code === 4001);
  const walletIsOn = (hex) => { const k = data.networks.find((x) => x.chain_id !== undefined && C.hex(BigInt(x.chain_id)) === hex); return k ? `na rede ${k.name}` : 'em outra rede'; };
  function explain(e, n, step) {
    if (e && e.code === -32002) return 'Abra a carteira: há um pedido esperando a sua resposta.';
    if (e && e.code === 'test_network') return `A carteira está numa rede de testes. Troque para a rede principal ${n.name} para enviar.`;
    if (e && e.code === 'xrp_refused') return `O XRP Ledger recusou o envio${e.detail ? ` (${e.detail})` : ''}. O valor não foi enviado.`;
    if (e && e.code === 'tron_refused') return `A rede Tron recusou o envio${e.detail ? ` (${e.detail})` : ''}. Nada foi enviado.`;
    if (e && e.code === 'wrong_chain') return `A carteira continua ${walletIsOn(state.chainNow)}. Troque para ${n.name} para enviar.`;
    if (step === 'connect') return refused(e) ? 'Conexão recusada na carteira. Nada foi enviado.' : 'Desbloqueie a carteira e tente de novo.';
    return refused(e) ? 'Envio cancelado na carteira. Nada foi enviado.' : 'A carteira recusou o envio: saldo insuficiente para o valor e a taxa.';
  }

  let picks = 0;   // a connection belongs to the network it started on: choosing another network cancels it (spec seguranca-doacoes, section 11)
  async function pickWallet(w, n) {
    const pick = picks;
    state.busy = true; state.notice = ''; render();
    try {
      const account = await connect(w, n);
      if (pick !== picks) return;
      state.account = account; state.wallet = w;
      if (w.provider && w.provider.on && !listening.has(w.provider)) {
        listening.add(w.provider);
        w.provider.on('accountsChanged', (a) => { state.account = a[0]; if (!a[0]) state.wallet = null; render(); });
      }
    } catch (e) { if (pick === picks) state.notice = explain(e, n, 'connect'); } finally { state.busy = false; state.choosing = false; render(); }
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
    state.busy = true; state.notice = '';
    try {
      showConfirm(n, c, units);
      const hash = await transfer(state.wallet, n, c, units);
      drawDone(hash, n, c, units, 'wait'); watch(hash, n, c, units);
    } catch (e) { backToStart(); state.notice = explain(e, n, 'send'); } finally { state.busy = false; render(); }
  });

  $('[data-change]').addEventListener('click', () => {
    state.wallet = null; state.account = null; state.notice = ''; state.choosing = found(net().family).length > 1; render();
  });
  payLink.addEventListener('click', () => setTimeout(() => {
    if (document.visibilityState === 'visible') { state.notice = 'Nenhum app abriu? Use o QR em outro aparelho ou copie o endereço acima.'; render(); }
  }, 2500));
  input.addEventListener('input', () => { state.notice = ''; render(); });
  root.addEventListener('bi-cripto-pick', () => {
    picks++; watching++;
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
