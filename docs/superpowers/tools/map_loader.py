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

# The loader itself is assets/bi-loader.js, a file and not inline code: the site's CSP refuses inline scripts (spec
# seguranca-doacoes, section 8). The id stays on the tag, as before.
SCRIPT = '<script id="bi-loader-js" src="assets/bi-loader.js"></script>'


def card(size):
    attr = f' data-size="{size}"' if size else ""
    return (f'<div class="bi-loader" id="bi-loader" role="status" aria-live="polite"{attr} data-state="loading">'
            '<b>Carregando os dados oficiais do mapa</b><div class="bi-loader-bar"><i></i></div>'
            '<div class="bi-loader-row"><span>27 estados, desde 2019</span><span data-pct></span></div>'
            '<p class="bi-loader-err" hidden>Não foi possível carregar os dados.</p><button type="button" hidden>Tentar de novo</button></div>')


def hold(tag, allow_inline=False):
    """One script element held back unchanged until the data has run. An outside script keeps its hash: integrity with
    crossorigin="anonymous" becomes data-integrity, which the loader puts back (spec apoie, section 10.2, item 4)."""
    m = re.fullmatch(r'<script( [^>]*)?>(.*)</script>', tag, flags=re.S)
    attrs, body = m.group(1) or "", m.group(2)
    src = re.search(r' src="([^"]+)"', attrs)
    if src:
        module = attrs.strip().startswith('type="module" ')
        rest = attrs.strip()[len('type="module" '):] if module else attrs.strip()
        sri = re.fullmatch(f'src="{re.escape(src.group(1))}"' + r'(?: integrity="([^"]+)" crossorigin="anonymous")?', rest)
        if not (body == "" and sri):
            raise SystemExit(tag[:80])
        integrity = f' data-integrity="{sri.group(1)}"' if sri.group(1) else ""
        return f'<script type="text/x-bi-deferred" data-src="{src.group(1)}"{integrity}{" data-module" if module else ""}></script>'
    if allow_inline and attrs == "":   # the author's local preview only (build-platform-preview.py --author-notes), never published
        return f'<script type="text/x-bi-deferred">{body}</script>'
    # the site's CSP refuses inline code (spec seguranca-doacoes, section 8): every script is a file
    raise SystemExit(f"map_loader: inline script, put it in a file under assets/: {tag[:80]}")


def apply(page, data_file, allow_inline=False):
    """The page with the loader; data_file is assets/bi-data.js, whose size goes into the page (absent: no number)."""
    data_file = Path(data_file)
    size = data_file.stat().st_size if data_file.exists() else 0
    if not (page.count(DATA_TAG) == 1 and page.count('<div class="hero-map"></div>') == 1):
        raise SystemExit('check failed: page.count(DATA_TAG) == 1 and page.count(\'<div class="hero-map"></div>\') == 1')
    head, tail = page.split(DATA_TAG)
    keep = re.compile(r'<script id="bi-chrome-js"[ >]')
    out, n = [], 0
    pos = 0
    for m in re.finditer(r'<script\b[^>]*>.*?</script>', tail, flags=re.S):
        out.append(tail[pos:m.start()])
        out.append(m.group(0) if keep.match(m.group(0)) else hold(m.group(0), allow_inline))
        n += not keep.match(m.group(0))
        pos = m.end()
    out.append(tail[pos:])
    head = head.replace('<div class="hero-map"></div>', f'<div class="hero-map">{card(size)}</div>')
    head = head.replace("</head>", CSS + "\n</head>", 1)
    return head + SCRIPT + "".join(out), n, size
