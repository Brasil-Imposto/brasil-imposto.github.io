"""The map loader of Início (D152, spec header-footer-loader, section 3, option L1): the true download percentage of the
map's data while it arrives.

build-platform-preview.py calls apply(): the classic script that loaded assets/bi-data.js becomes a loader that downloads the
file with fetch and reads it in parts; the percentage is the bytes received over the file's size, written into the page at
build time (the browser counts bytes after decompression, and Pages compresses the file, so Content-Length cannot be used).
Every script after it is held back unchanged (type text/x-bi-deferred) and runs, in the same order, once the data has run;
the module script runs last, as a deferred module did. Never 100% before body[data-ready="1"], never backwards; a failed
download offers a retry; with no size in the page (or a file of another size) the card shows no number at all. Opened from
the file path, where fetch cannot read files, the data loads as a plain script, with the bar and no number.
"""
import re
from pathlib import Path

DATA_TAG = '<script src="assets/bi-data.js"></script>'

CSS = """<style id="bi-loader-css">
.bi-loader { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); z-index: 6; box-sizing: border-box; width: min(300px, 86%); padding: 16px 18px; background: #fff; border: 1px solid #E3E7EC; border-radius: 14px; box-shadow: 0 10px 30px rgba(20,32,43,.08); font-family: Manrope, system-ui, sans-serif; color: #14202B; }
.bi-loader[hidden] { display: none; }
.bi-loader b { display: block; font-weight: 800; font-size: 14px; }
.bi-loader-bar { position: relative; height: 8px; margin: 12px 0 8px; border-radius: 99px; background: #EDF1F4; overflow: hidden; }
.bi-loader-bar i { position: absolute; left: 0; top: 0; bottom: 0; width: 0; border-radius: 99px; background: #12803F; transition: width .2s linear; }
.bi-loader[data-state="unknown"] .bi-loader-bar i, .bi-loader[data-state="file"] .bi-loader-bar i { width: 34%; animation: bi-loader-slide 1.3s ease-in-out infinite; }
@keyframes bi-loader-slide { from { left: -34%; } to { left: 100%; } }
@media (prefers-reduced-motion: reduce) { .bi-loader-bar i { animation: none !important; } }
.bi-loader-row { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; font-size: 12.5px; color: #5B6773; }
.bi-loader-row [data-pct] { font-weight: 800; color: #14202B; font-variant-numeric: tabular-nums; }
.bi-loader-err { margin: 10px 0 0; font-size: 12.5px; color: #5B6773; }
.bi-loader button { margin-top: 10px; height: 32px; padding: 0 14px; border: 1px solid #E3E7EC; border-radius: 99px; background: #fff; color: #14202B; font: 700 13px Manrope, system-ui, sans-serif; cursor: pointer; }
</style>"""

SCRIPT = r"""<script id="bi-loader-js">
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
    const reader = res.body.getReader(), parts = []; bytes = 0;
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      parts.push(value); bytes += value.length; card.dataset.bytes = bytes;
      if (!unknown && bytes > size) giveUpNumber();   // a file of another size: no invented number
      show(Math.floor(bytes * 100 / (size || 1)));
    }
    if (!unknown && bytes !== size) giveUpNumber();
    const url = URL.createObjectURL(new Blob(parts, { type: 'text/javascript' }));
    try { await runData(url); } finally { URL.revokeObjectURL(url); }
  };
  const start = () => load().then(() => { finish(); return runDeferred(); }).catch(() => {
    state('error'); err.hidden = false; retry.hidden = false; retry.focus();
  });
  retry.addEventListener('click', start);
  start();
})();
</script>"""


def card(size):
    attr = f' data-size="{size}"' if size else ""
    return (f'<div class="bi-loader" id="bi-loader" role="status" aria-live="polite"{attr} data-state="loading">'
            '<b>Carregando os dados oficiais do mapa</b><div class="bi-loader-bar"><i></i></div>'
            '<div class="bi-loader-row"><span>27 estados, desde 2019</span><span data-pct></span></div>'
            '<p class="bi-loader-err" hidden>Não foi possível carregar os dados.</p><button type="button" hidden>Tentar de novo</button></div>')


def hold(tag):
    """One script element held back unchanged until the data has run."""
    m = re.fullmatch(r'<script( [^>]*)?>(.*)</script>', tag, flags=re.S)
    attrs, body = m.group(1) or "", m.group(2)
    src = re.search(r' src="([^"]+)"', attrs)
    if src:
        if not (body == "" and attrs.strip() == f'src="{src.group(1)}"'):
            raise SystemExit(tag[:80])
        return f'<script type="text/x-bi-deferred" data-src="{src.group(1)}"></script>'
    if attrs.strip() == 'type="module"':
        return f'<script type="text/x-bi-deferred" data-module>{body}</script>'
    if not (attrs == ""):
        raise SystemExit(tag[:80])
    return f'<script type="text/x-bi-deferred">{body}</script>'


def apply(page, data_file):
    """The page with the loader; data_file is assets/bi-data.js, whose size goes into the page (absent: no number)."""
    data_file = Path(data_file)
    size = data_file.stat().st_size if data_file.exists() else 0
    if not (page.count(DATA_TAG) == 1 and page.count('<div class="hero-map"></div>') == 1):
        raise SystemExit('check failed: page.count(DATA_TAG) == 1 and page.count(\'<div class="hero-map"></div>\') == 1')
    head, tail = page.split(DATA_TAG)
    keep = re.compile(r'<script id="bi-chrome-js">')
    out, n = [], 0
    pos = 0
    for m in re.finditer(r'<script\b[^>]*>.*?</script>', tail, flags=re.S):
        out.append(tail[pos:m.start()])
        out.append(m.group(0) if keep.match(m.group(0)) else hold(m.group(0)))
        n += not keep.match(m.group(0))
        pos = m.end()
    out.append(tail[pos:])
    head = head.replace('<div class="hero-map"></div>', f'<div class="hero-map">{card(size)}</div>')
    head = head.replace("</head>", CSS + "\n</head>", 1)
    return head + SCRIPT + "".join(out), n, size
