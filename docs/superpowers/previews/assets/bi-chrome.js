// The header's Menu on phones: opens the sheet under the bar, closes with Esc, a tap outside or a link.
(function () {
  const btn = document.querySelector('.bi-menu-btn'), sheet = document.getElementById('bi-sheet');
  if (!btn || !sheet) return;
  const label = btn.querySelector('span');
  const set = (open, focusBack) => {
    sheet.hidden = !open; btn.setAttribute('aria-expanded', String(open)); label.textContent = open ? 'Fechar' : 'Menu';
    if (open) sheet.querySelector('a').focus(); else if (focusBack) btn.focus();
  };
  btn.addEventListener('click', () => set(sheet.hidden, true));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !sheet.hidden) set(false, true); });
  document.addEventListener('click', (e) => { if (!sheet.hidden && !sheet.contains(e.target) && !btn.contains(e.target)) set(false, false); });
  window.matchMedia('(min-width: 821px)').addEventListener('change', (m) => { if (m.matches && !sheet.hidden) set(false, false); });
})();
// Images that fail to load: data-fallback="hide" hides the image, data-fallback="remove" removes it (no handler attributes:
// the site's CSP blocks them). The error event does not bubble, so the listener captures it.
document.addEventListener('error', (e) => {
  const img = e.target;
  if (!(img instanceof HTMLImageElement) || !img.dataset.fallback) return;
  if (img.dataset.fallback === 'remove') img.remove(); else img.style.display = 'none';
}, true);
// The Apoie modal: opens from the header button, one view at a time, closes with the X, Escape or a click outside, and gives the
// focus back to the button.
(function () {
  const root = document.getElementById('bi-apoie'), opener = document.querySelector('.bi-apoie-btn');
  if (!root || !opener) return;
  const panel = root.querySelector('.bi-ap-panel'), back = root.querySelector('.bi-ap-back');
  const views = [...root.querySelectorAll('[data-view]')];
  let monoAsked = false;
  const mono = () => {   // the crypto view's mono font: nobody who stays out of that view downloads it
    if (monoAsked) return; monoAsked = true;
    const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = 'assets/fonts/jetbrains-mono.css'; document.head.appendChild(l);
  };
  const show = (name) => {
    if (name === 'crypto') mono();
    views.forEach((v) => { v.hidden = v.dataset.view !== name; });
    back.hidden = name === 'main'; panel.scrollTop = 0;
    const h = root.querySelector(`[data-view="${name}"] h2`); if (h) h.focus({ preventScroll: true });
    if (name === 'crypto') root.dispatchEvent(new CustomEvent('bi-cripto-view'));
  };
  const open = () => {
    root.hidden = false; document.documentElement.classList.add('bi-locked'); opener.setAttribute('aria-expanded', 'true'); show('main');
  };
  const close = () => {
    if (root.hidden) return;
    root.hidden = true; document.documentElement.classList.remove('bi-locked'); opener.setAttribute('aria-expanded', 'false'); opener.focus();
  };
  opener.addEventListener('click', open);
  root.querySelector('.bi-ap-x').addEventListener('click', close);
  root.querySelector('.bi-ap-backdrop').addEventListener('click', close);
  back.addEventListener('click', () => show('main'));
  root.addEventListener('click', (e) => { const go = e.target.closest('[data-go]'); if (go) show(go.dataset.go); });
  document.addEventListener('keydown', (e) => {
    if (root.hidden) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    if (e.key !== 'Tab') return;  // the focus stays inside the modal
    const f = [...root.querySelectorAll('button, a[href], input, textarea')].filter((x) => !x.disabled && x.getClientRects().length && x.tabIndex >= 0);
    if (!f.length) return;
    if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
    else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
  });
  // The crypto view: a coin shows only its network buttons; tapping one shows its address, and the send (assets/bi-cripto.js, loaded when
  // a coin is picked) shows the value and the button. If those files fail, the choice and "Copiar" still work.
  let sendAsked = false;
  const loadSend = () => {
    if (sendAsked) return; sendAsked = true;
    ['assets/bi-cripto-core.js', 'assets/bi-cripto.js'].reduce((p, src) => p.then(() => new Promise((ok, no) => {
      const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = no; document.head.appendChild(s);
    })), Promise.resolve()).catch(() => {});
  };
  const picked = (coin, net) => { root.dataset.coin = coin; root.dataset.net = net || ''; root.dispatchEvent(new CustomEvent('bi-cripto-pick')); };
  const pickNet = (panel, id) => {
    panel.querySelectorAll('[data-net-btn]').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.netBtn === id)));
    panel.querySelectorAll('.bi-ap-net').forEach((r) => { r.hidden = r.dataset.net !== id; });
    picked(panel.dataset.coin, id);
  };
  root.querySelectorAll('[data-net-btn]').forEach((b) => b.addEventListener('click', () => pickNet(b.closest('.bi-ap-coin'), b.dataset.netBtn)));
  const pickCoin = (b, net) => {
    const c = b.dataset.coinBtn;
    root.querySelectorAll('[data-coin-btn]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    root.querySelectorAll('.bi-ap-coin').forEach((p) => { p.hidden = p.dataset.coin !== c; });
    const panel = root.querySelector(`.bi-ap-coin[data-coin="${c}"]`);
    panel.querySelectorAll('[data-net-btn]').forEach((x) => x.setAttribute('aria-pressed', 'false'));
    panel.querySelectorAll('.bi-ap-net').forEach((r) => { r.hidden = true; });
    picked(c, '');
    loadSend();
    if (net) pickNet(panel, net);   // only the site's own link chooses a network for the donor
  };
  root.querySelectorAll('[data-coin-btn]').forEach((b) => b.addEventListener('click', () => pickCoin(b)));
  // The site's own link (#apoie-cripto?moeda=USDT&rede=tron&valor=10), used to open the site inside a wallet app: it only chooses.
  const entry = /^#apoie-cripto\?(.*)$/.exec(location.hash);
  if (entry) {
    const q = new URLSearchParams(entry[1]);
    const b = [...root.querySelectorAll('[data-coin-btn]')].find((x) => x.dataset.coinBtn === q.get('moeda'));
    if (b) {
      const net = [...root.querySelectorAll(`.bi-ap-coin[data-coin="${b.dataset.coinBtn}"] [data-net-btn]`)].find((x) => x.dataset.netBtn === q.get('rede'));
      open(); show('crypto'); pickCoin(b, net && net.dataset.netBtn);
    }
  }
  root.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    const text = b.dataset.copy; if (!text) return;
    try { await navigator.clipboard.writeText(text); } catch (_) {
      const r = document.createRange(); r.selectNodeContents(b.closest('.bi-ap-net').querySelector('code'));
      const s = getSelection(); s.removeAllRanges(); s.addRange(r); document.execCommand('copy');
    }
    b.classList.add('done'); setTimeout(() => b.classList.remove('done'), 1800);
  }));
  // The contact form (D124): checked here, then sent as JSON to Web3Forms. A checked honeypot or a send faster than the minimum
  // time after the view opens is dropped without a request.
  const form = root.querySelector('.bi-ap-form');
  if (form) {
    const sent = root.querySelector('.bi-ap-sent'), fail = form.querySelector('.bi-ap-fail'), send = form.querySelector('[type="submit"]');
    const label = send.textContent, minMs = Number(form.dataset.minMs), f = form.elements;
    let openedAt = 0;
    const setError = (name, text) => {
      const p = form.querySelector(`#bi-ap-${name}-err`); p.textContent = text || ''; p.hidden = !text;
      if (text) f[name].setAttribute('aria-invalid', 'true'); else f[name].removeAttribute('aria-invalid');
    };
    const reset = () => {
      openedAt = Date.now(); form.hidden = false; sent.hidden = true; fail.hidden = true;
      ['name', 'email', 'message'].forEach((n) => setError(n, ''));
    };
    const done = () => { form.reset(); form.hidden = true; sent.hidden = false; sent.focus({ preventScroll: true }); };
    root.addEventListener('click', (e) => { const go = e.target.closest('[data-go="contact"]'); if (go) reset(); });
    form.addEventListener('submit', (e) => {
      e.preventDefault(); fail.hidden = true;
      const v = { name: f.name.value.trim(), email: f.email.value.trim(), message: f.message.value.trim() };
      const bad = {
        name: v.name ? '' : form.dataset.required,
        email: !v.email ? form.dataset.required : (/^[^@ ]+@[^@ ]+[.][^@ ]{2,}$/.test(v.email) ? '' : form.dataset.badEmail),
        message: v.message ? '' : form.dataset.required,
      };
      Object.entries(bad).forEach(([n, t]) => setError(n, t));
      const first = Object.keys(bad).find((n) => bad[n]);
      if (first) { f[first].focus(); return; }
      if (f.botcheck.checked || Date.now() - openedAt < minMs) { done(); return; }
      send.disabled = true; send.textContent = form.dataset.sending;
      fetch(form.dataset.endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ access_key: form.dataset.key, ...v, subject: form.dataset.subject, from_name: form.dataset.fromName, botcheck: false }),
      }).then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
        .then((j) => { if (j && j.success === true) done(); else throw new Error('not sent'); })
        .catch(() => { fail.hidden = false; })
        .finally(() => { send.disabled = false; send.textContent = label; });
    });
  }
})();
