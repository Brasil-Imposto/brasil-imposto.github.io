"""The site header and footer shared by the three published pages (D152, spec header-footer-loader, sections 1 and 2),
from one source.

build-platform-preview.py puts it into the Início page at build time; build-site-chrome.py writes it into Os 3 Poderes and
Como o dinheiro anda, between markers, so no page carries a copy edited by hand. tests in pipelines/tests/test_site_chrome.py
fail when a page's copy differs from this module.
"""
import re

import apoie
import features
import support_data

REPO_URL = "https://github.com/Brasil-Imposto/brasil-imposto.github.io"
HOME = "BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html"
# every link to Início points at the site's root, never at the design file's name (production has no preview); relative, so the
# same pages work under a sub-path. The old address forwards to "./" (pages.yml, "Assemble the site").
HOME_HREF = "./"
PAGES = {
    "inicio": (HOME, "Início"),
    "tres-poderes": ("BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html", "Os 3 Poderes"),
    "dinheiro": ("BRASIL-IMPOSTO_DESIGN_como-o-dinheiro-anda-round-1_2026-10-21.html", "Como o dinheiro anda"),
}

CSS = """<style id="bi-chrome-css">
.bi-header { position: sticky; top: 0; z-index: 1000; height: 62px; box-sizing: border-box; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 0 22px; background: rgba(255,255,255,.94); -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px); border-bottom: 1px solid #E3E7EC; font-family: Manrope, system-ui, sans-serif; }
.bi-brand { display: inline-flex; align-items: center; gap: 9px; color: #14202B; text-decoration: none; font-weight: 800; font-size: 15px; letter-spacing: -.01em; white-space: nowrap; }
.bi-brand img { width: 30px; height: 30px; }
.bi-brand i { font-style: normal; color: #12803F; }
.bi-links { display: flex; align-items: center; gap: 18px; }
.bi-links a { font-weight: 700; font-size: 13px; color: #5B6773; text-decoration: none; padding-bottom: 3px; }
.bi-links a:hover { color: #14202B; }
.bi-links a[aria-current="page"] { color: #14202B; box-shadow: 0 2px 0 #14202B; }
.bi-menu-btn { display: none; align-items: center; gap: 8px; height: 34px; padding: 0 14px; border: 1px solid #E3E7EC; border-radius: 99px; background: #fff; color: #14202B; font: 700 13px Manrope, system-ui, sans-serif; cursor: pointer; }
.bi-menu-btn svg { width: 16px; height: 16px; }
.bi-sheet { position: fixed; left: 0; right: 0; top: 62px; z-index: 999; padding: 6px 14px 16px; background: rgba(255,255,255,.98); border-bottom: 1px solid #E3E7EC; box-shadow: 0 10px 30px rgba(20,32,43,.08); font-family: Manrope, system-ui, sans-serif; }
.bi-sheet[hidden] { display: none; }
/* every in-page jump lands below the header (62 px) with a gap; a page's overlays sit above it (z-index 1100) and lock the page */
:where([id]) { scroll-margin-top: 80px; }
html.bi-locked, html.bi-locked body { overflow: hidden; }
.bi-sheet a { display: block; padding: 11px 0; border-bottom: 1px solid #E3E7EC; font-weight: 700; font-size: 17px; color: #14202B; text-decoration: none; }
.bi-sheet a[aria-current="page"] { color: #12803F; }
.bi-sheet p { margin: 12px 0 0; font-size: 12.5px; color: #5B6773; }
.bi-footer { background: #fff; border-top: 1px solid #E3E7EC; font-family: Manrope, system-ui, sans-serif; }
.bi-footer-in { box-sizing: border-box; max-width: 1180px; margin: 0 auto; padding: 22px 24px; display: flex; align-items: center; justify-content: space-between; gap: 18px 28px; flex-wrap: wrap; }
.bi-footer-id { flex: 1 1 280px; min-width: 0; }
.bi-footer-id p { margin: 6px 0 0; font-size: 12.5px; color: #5B6773; text-wrap: balance; }
.bi-footer-links { display: flex; flex-wrap: wrap; gap: 10px 18px; flex: 0 1 auto; }
.bi-footer-links a { font-weight: 700; font-size: 13.5px; color: #5B6773; text-decoration: none; }
.bi-footer-links a:hover { color: #14202B; }
@media (max-width: 820px) {
  .bi-footer-in { flex-direction: column; align-items: flex-start; padding: 22px 14px; }
  .bi-footer-id, .bi-footer-links { flex: none; }
  .bi-footer-links { flex-direction: column; gap: 12px; }
}
@media (max-width: 820px) {
  .bi-header { padding: 0 14px; }
  .bi-header .bi-links { display: none; }
  .bi-menu-btn { display: inline-flex; }
}
</style>"""

# The tab icons (D153, spec logo-no-site): drawn for 16 and 32 px in favicon.ico, and the Apple touch icon. They share the head block
# with the CSS, between the site-chrome:css markers.
ICONS = ('<link rel="icon" href="assets/brand/favicon.ico" sizes="16x16 32x32">\n'
         '<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">')
# The social preview (D153, spec social-preview): the image and the description a shared link shows; each page's <title> stays its title.
DESCRIPTION = "Para onde vai o imposto, com dados oficiais e a fonte de cada número."
SOCIAL = "\n".join([
    '<meta property="og:site_name" content="Brasil-Imposto">',
    '<meta property="og:type" content="website">',
    '<meta property="og:locale" content="pt_BR">',
    f'<meta property="og:description" content="{DESCRIPTION}">',
    '<meta property="og:image" content="https://brasil-imposto.github.io/assets/brand/og-image.png">',
    '<meta property="og:image:width" content="1200">',
    '<meta property="og:image:height" content="630">',
    f'<meta property="og:image:alt" content="A marca do Brasil-Imposto, o nome e a frase: {DESCRIPTION}">',
    '<meta name="twitter:card" content="summary_large_image">',
])
HEAD = ICONS + "\n" + SOCIAL + "\n" + CSS
LOGO = '<img src="assets/brand/brasil-imposto-logo.svg" alt="">'  # the name follows in text, so the mark needs no alt of its own

ICON = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" fill="none"/></svg>'

SCRIPT = """<script id="bi-chrome-js">
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
// The footer's "Rede do dinheiro (prévia)": on Início the card is on this page, so the link only scrolls to it.
(function () {
  const a = document.querySelector('.bi-footer a[data-here]'), target = document.getElementById('rede');
  if (a && target) a.addEventListener('click', (e) => { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); history.replaceState(null, '', '#rede'); });
})();
</script>"""


def _links(current, cls=""):
    out = []
    for key, (href, label) in PAGES.items():
        href = HOME_HREF if key == "inicio" else href
        cur = ' aria-current="page"' if key == current else ""
        out.append(f'<a href="{href}"{cur}>{label}</a>')
    out.append(f'<a href="{REPO_URL}">Código aberto</a>')
    return "".join(out)


def header(current):
    """The header for one page; `current` is a key of PAGES. The pages differ only in aria-current."""
    if not (current in PAGES):
        raise SystemExit(current)
    return ('<header class="bi-header">'
            f'<a class="bi-brand" href="{HOME_HREF}">{LOGO}<span>Brasil<i>·</i>Imposto</span></a>'
            f'<nav class="bi-links" aria-label="Páginas">{_links(current)}</nav>'
            f'<button type="button" class="bi-menu-btn" aria-expanded="false" aria-controls="bi-sheet">{ICON}<span>Menu</span></button>'
            '</header>'
            f'<nav class="bi-sheet" id="bi-sheet" aria-label="Páginas" hidden>{_links(current)}'
            '<p>Rede do dinheiro (prévia), decisões e licenças ficam no rodapé.</p></nav>')


def footer():
    """The footer, the same on every page."""
    links = [(f"{HOME_HREF}#rede", "Rede do dinheiro (prévia)", ' data-here'), (REPO_URL, "Código aberto no GitHub", ""),
             (f"{REPO_URL}/blob/main/docs/decisions/README.md", "Decisões do projeto", ""),
             (f"{REPO_URL}/blob/main/CONTRIBUTING.md", "Como ajudar", ""), (f"{REPO_URL}#licenças", "Licenças", "")]
    return ('<footer class="bi-footer"><div class="bi-footer-in"><div class="bi-footer-id">'
            f'<a class="bi-brand" href="{HOME_HREF}">{LOGO}<span>Brasil<i>·</i>Imposto</span></a>'
            '<p>Dados oficiais, com fonte em cada número. Código AGPL-3.0, dados CC BY 4.0.</p></div>'
            '<nav class="bi-footer-links" aria-label="Mais sobre o projeto">'
            + "".join(f'<a href="{h}"{x}>{t}</a>' for h, t, x in links) + '</nav></div></footer>')


MARK = {"css": ("<!-- site-chrome:css -->", "<!-- /site-chrome:css -->"),
        "header": ("<!-- site-chrome:header -->", "<!-- /site-chrome:header -->"),
        "footer": ("<!-- site-chrome:footer -->", "<!-- /site-chrome:footer -->"),
        "js": ("<!-- site-chrome:js -->", "<!-- /site-chrome:js -->")}


def with_support(head, data, keyless=False):
    """The header with the Apoie button after the page links (next to Menu on phones) and its modal after the bar (spec apoie).
    The modal sits outside <header>: the bar's backdrop-filter would make it the box a fixed child is placed in."""
    a, b = '<nav class="bi-links"', "</header>"
    if not (head.count(a) == 1 and head.count(b) == 1):
        raise SystemExit("site_chrome: the header changed; place the Apoie button again")
    head = head.replace(a, '<div class="bi-end">' + a).replace(b, "</div>" + b)
    return head.replace('<button type="button" class="bi-menu-btn"', apoie.BUTTON + '<button type="button" class="bi-menu-btn"', 1) \
        + apoie.modal(data, keyless)


def parts(current, profile="production"):
    """Everything the markers carry on one page, for one build (spec staging): the Apoie button and its modal come in only when
    the apoie switch of data/features.json is on for the profile, and production only with the data its rule asks for
    (support_data.problems); off, the pages are what they were."""
    on = features.on("apoie", profile)
    data = support_data.load()
    wrong = support_data.problems(data)
    if wrong:
        raise SystemExit("data/support.json: " + "; ".join(wrong))
    if not on:
        return {"css": HEAD, "header": header(current), "footer": footer(), "js": SCRIPT}
    return {"css": HEAD + "\n" + apoie.CSS, "header": with_support(header(current), data, keyless=profile == "staging"), "footer": footer(),
            "js": SCRIPT.replace("\n</script>", "\n" + apoie.SCRIPT + "</script>", 1)}


def block(name, body):
    a, b = MARK[name]
    return f"{a}\n{body}\n{b}"


def inject(page, current, profile="production"):
    """Writes the parts between their markers; a page without markers gets them inserted once: the css before </head>, the
    header right after <body>, the footer and then the script before the last </body>."""
    for name, body in parts(current, profile).items():
        a, b = MARK[name]
        if page.count(a) == 1 and page.count(b) == 1:
            page = page[:page.index(a)] + block(name, body) + page[page.index(b) + len(b):]
            continue
        if not (page.count(a) == 0 and page.count(b) == 0):
            raise SystemExit(f"broken {name} markers")
        if name == "css":
            if not (page.count("</head>") == 1):
                raise SystemExit("check failed: page.count('</head>') == 1")
            page = page.replace("</head>", block(name, body) + "\n</head>")
        elif name == "header":
            m = list(re.finditer(r"<body[^>]*>", page))
            if not (len(m) == 1):
                raise SystemExit('check failed: len(m) == 1')
            page = page[:m[0].end()] + "\n" + block(name, body) + page[m[0].end():]
        else:
            i = page.rindex("</body>")
            page = page[:i] + block(name, body) + "\n" + page[i:]
    return page


def extract(page, name):
    a, b = MARK[name]
    if not (page.count(a) == 1 and page.count(b) == 1):
        raise SystemExit(f"{name} markers")
    return page[page.index(a) + len(a):page.index(b)].strip("\n")
