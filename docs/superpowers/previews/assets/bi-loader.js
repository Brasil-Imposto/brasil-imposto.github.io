// D152, L1: download the map's data with the true percentage, then run the page's scripts in their order.
(function () {
  const card = document.getElementById('bi-loader');
  const size = +card.dataset.size || 0;
  const bar = card.querySelector('.bi-loader-bar i'), pct = card.querySelector('[data-pct]');
  const err = card.querySelector('.bi-loader-err'), retry = card.querySelector('button');
  let shown = 0, bytes = 0, unknown = !size;
  const state = (s) => { card.dataset.state = s; };
  const show = (n) => {                       // never backwards, never 100 before the page is ready
    if (unknown) { pct.textContent = ''; bar.style.width = ''; return; }
    n = Math.max(shown, Math.min(n, 99)); shown = n;
    pct.textContent = n + '%'; bar.style.width = n + '%';
  };
  const giveUpNumber = () => { unknown = true; state('unknown'); show(0); };
  if (unknown) state('unknown'); else state('loading');
  const runDeferred = () => {                 // the page's scripts, in document order; the module last, as it was deferred
    const held = [...document.querySelectorAll('script[type="text/x-bi-deferred"]')];
    const classic = held.filter((s) => !s.hasAttribute('data-module')), modules = held.filter((s) => s.hasAttribute('data-module'));
    const run = (s) => new Promise((ok, fail) => {
      const n = document.createElement('script');
      if (s.hasAttribute('data-module')) n.type = 'module';
      if (s.dataset.integrity) { n.integrity = s.dataset.integrity; n.crossOrigin = 'anonymous'; }
      if (s.dataset.src) { n.src = s.dataset.src; n.async = false; n.onload = ok; n.onerror = () => fail(new Error(s.dataset.src)); }
      else n.textContent = s.textContent;
      s.replaceWith(n);
      if (!s.dataset.src) ok();
    });
    return [...classic, ...modules].reduce((p, s) => p.then(() => run(s)), Promise.resolve());
  };
  const runData = (src) => new Promise((ok, fail) => {
    const n = document.createElement('script'); n.src = src; n.onload = ok; n.onerror = () => fail(new Error('bi-data.js'));
    document.head.appendChild(n);
  });
  const finish = () => {                      // the card leaves when the page marks itself ready
    const done = () => { if (!unknown) { shown = 99; pct.textContent = '100%'; bar.style.width = '100%'; } state('done'); setTimeout(() => { card.hidden = true; }, 250); };
    if (document.body.dataset.ready === '1') return done();
    new MutationObserver((m, o) => { if (document.body.dataset.ready === '1') { o.disconnect(); done(); } }).observe(document.body, { attributes: true, attributeFilter: ['data-ready'] });
  };
  const load = async () => {
    err.hidden = true; retry.hidden = true;
    if (location.protocol === 'file:') { unknown = true; state('file'); show(0); await runData('assets/bi-data.js'); return; }
    if (!unknown) state('loading');
    const res = await fetch('assets/bi-data.js', { cache: 'no-cache' });
    if (!res.ok || !res.body) throw new Error('HTTP ' + res.status);
    const reader = res.body.getReader(); bytes = 0;
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      bytes += value.length; card.dataset.bytes = bytes;
      if (!unknown && bytes > size) giveUpNumber();   // a file of another size: no invented number
      show(Math.floor(bytes * 100 / (size || 1)));
    }
    if (!unknown && bytes !== size) giveUpNumber();
    // the bytes counted, the file runs by its own address, which the browser serves from its cache (Pages sends max-age=600): a
    // blob: address would need blob: in the CSP's script-src (spec seguranca-doacoes, section 8)
    await runData('assets/bi-data.js');
  };
  const start = () => load().then(() => { finish(); return runDeferred(); }).catch(() => {
    state('error'); err.hidden = false; retry.hidden = false; retry.focus();
  });
  retry.addEventListener('click', start);
  start();
})();
