"""Assembles the published site in one of two profiles (spec BRASIL-IMPOSTO_SPEC_staging_2026-10-23, section 3).

  production  what https://brasil-imposto.github.io serves: the pages as committed (index.html is Início), assets/, the
              forwarding page at Início's old address (D160), .nojekyll and robots.txt (staging stays out of search)
  staging     what https://brasil-imposto.github.io/staging/ serves: the same pages built with every switch of data/features.json
              that staging turns on, a strip at the top of each page saying it is the test site, and noindex

Both run the page builders first (the four pages.yml ran, the notes page and the map's notes, D159). The staging build writes only to the output folder: the committed pages
are the production ones, so `git status` stays clean after it (pipelines/tests/test_build_site.py).

Run: python3 docs/superpowers/tools/build-site.py --profile {production,staging} --out <folder>
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PREVIEWS = TOOLS.parent / "previews"
sys.path.insert(0, str(TOOLS))
import features  # noqa: E402
import map_loader  # noqa: E402
import site_chrome  # noqa: E402

BUILDERS = ("build-cases.py", "build-standalone-data.py", "build-simulation.py", "build-platform-preview.py", "build-notes-page.py")
# the notes of the map for Como ler o mapa (D159), made from the map's data once build-standalone-data.py has written it
NODE_BUILDERS = ("build-map-notes.cjs",)
def script_tags(path):
    """The script elements of one of our own source files, read line by line (no HTML parsing): a whole line
    <script src="..."></script>, or a <script> line, its body and a </script> line. Anything else stops the build."""
    lines, tags, i = path.read_text(encoding="utf-8").strip().split("\n"), [], 0
    while i < len(lines):
        if lines[i].startswith('<script src="') and lines[i].endswith('"></script>'):
            tags.append(lines[i])
            i += 1
        elif lines[i] == "<script>" and "</script>" in lines[i:]:
            j = lines.index("</script>", i)
            tags.append("\n".join(lines[i:j + 1]))
            i = j + 1
        else:
            raise SystemExit(f"build-site: {path.name}: unexpected line {lines[i][:60]}")
    return tags


# What each switch of data/features.json adds to a page, after the anchor it follows, and the files only it uses. A switch that
# is off leaves the page as committed and its files out of assets/ (features.py: absent, never hidden).
FEATURES = {
    # rede comes first: its stylesheet then lands after home-trade.css, where the published page had it before the switch
    "rede": {  # the money network preview on Início, staging only until it is approved for production (D172, Q-A2)
        "page": "inicio",
        "after": [('<link rel="stylesheet" href="assets/home-feed.css">', '<link rel="stylesheet" href="assets/platform.css">'),
                  ('<section class="hf-cake" id="para-onde-vai" data-cake aria-label="Para onde vai o dinheiro da União"></section>',
                   "\n" + (PREVIEWS / "src" / "platform-sections.html").read_text(encoding="utf-8").strip()),
                  ("<!-- /site-chrome:js -->", "\n".join(map_loader.hold(tag) for tag in script_tags(PREVIEWS / "src" / "platform-script.html")))],
        "files": ("platform.css", "bi-ledger-interest.js", "ledger-graph-model.js", "ledger-graph-view.js"),
    },
    "trade": {  # O que o Brasil vende, under Por que falta dinheiro on Início (D159)
        "page": "inicio",
        "after": [('<link rel="stylesheet" href="assets/home-feed.css">', '<link rel="stylesheet" href="assets/home-trade.css">'),
                  ('<script type="text/x-bi-deferred" data-src="assets/home-feed.js"></script>',
                   '<script type="text/x-bi-deferred" data-src="assets/home-trade.js"></script>')],
        "files": ("home-trade.js", "home-trade.css"),
    },
}
OFFICIAL = "https://brasil-imposto.github.io"
STRIP_TEXT = ("Ambiente de testes: inclui ideias ainda não aprovadas. O site oficial é "
              f'<a href="{OFFICIAL}">brasil-imposto.github.io</a>.')
STRIP = ('<style id="bi-staging-css">.bi-staging { margin: 0; padding: 8px 16px; background: #FFF4D6; border-bottom: 1px solid #E8D9A8; '
         'color: #14202B; font: 600 13px/1.45 Manrope, system-ui, sans-serif; text-align: center; } '
         '.bi-staging a { color: #14202B; text-decoration: underline; }</style>'
         f'<p class="bi-staging" role="note">{STRIP_TEXT}</p>'
         # the phone menu sits at the header's height (62 px) under a header at the top; with the strip above, the header starts
         # lower until the page scrolls, so the menu follows the header's real bottom
         "<script>document.addEventListener('DOMContentLoaded', () => { const h = document.querySelector('.bi-header'), "
         "s = document.getElementById('bi-sheet'); if (!h || !s) return; const f = () => { s.style.top = "
         "Math.max(0, h.getBoundingClientRect().bottom) + 'px'; }; f(); addEventListener('scroll', f, { passive: true }); "
         "addEventListener('resize', f); });</script>")
NOINDEX = '<meta name="robots" content="noindex">'
ROBOTS = "User-agent: *\nDisallow: /staging/\n"
# Início lives at the root. Its old address, already shared, forwards there with its query (?open=, ?metric=, ?modal=, ?area=)
# and its hash; the meta refresh is the fallback without JavaScript (D160).
FORWARD = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Brasil-Imposto</title><meta name="robots" content="noindex"><link rel="canonical" href="./">
<script>location.replace('./' + location.search + location.hash);</script>
<noscript><meta http-equiv="refresh" content="0; url=./"></noscript>
</head><body><p>Esta página mudou de endereço: <a href="./">ir para o Início</a>.</p></body></html>
"""


def staging_page(page, key):
    """One committed page as the staging build serves it: its chrome rebuilt with the staging switches, the strip first in the
    body and noindex in the head."""
    page = site_chrome.inject(page, key, "staging")
    if not (page.count("</head>") == 1 and len(re.findall(r"<body[^>]*>", page)) == 1 and 'name="robots"' not in page):
        raise SystemExit(f"build-site: {key}: one </head>, one <body> and no robots meta expected")
    page = page.replace("</head>", NOINDEX + "\n</head>")
    body = re.search(r"<body[^>]*>", page)
    return page[:body.end()] + "\n" + STRIP + page[body.end():]


def with_features(page, key, profile):
    """A page with what each switch turned on for the profile adds to it; with every switch off, the page as it came."""
    for name, f in FEATURES.items():
        if f["page"] != key or not features.on(name, profile):
            continue
        for anchor, tag in f["after"]:
            if page.count(anchor) != 1:
                raise SystemExit(f"build-site: {name}: {anchor} expected once in {key}")
            page = page.replace(anchor, anchor + "\n" + tag)
    return page


def build(profile, out):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for b in BUILDERS:
        subprocess.run([sys.executable, str(TOOLS / b)], check=True, stdout=subprocess.DEVNULL)
    for b in NODE_BUILDERS:
        subprocess.run(["node", str(TOOLS / b)], check=True, stdout=subprocess.DEVNULL)
    off = {fn for name, f in FEATURES.items() if not features.on(name, profile) for fn in f["files"]}
    shutil.copytree(PREVIEWS / "assets", out / "assets", ignore=lambda d, names: [n for n in names if Path(d) == PREVIEWS / "assets" and n in off])
    for key, (name, _label) in site_chrome.ALL_PAGES.items():
        target = out / ("index.html" if key == "inicio" else name)
        committed = (PREVIEWS / name).read_bytes().decode("utf-8")
        page = with_features(committed, key, profile)
        if profile == "production" and page == committed:
            shutil.copyfile(PREVIEWS / name, target)   # the committed page, byte for byte
        elif profile == "production":
            target.write_bytes(page.encode("utf-8"))
        else:
            target.write_bytes(staging_page(page, key).encode("utf-8"))
    (out / site_chrome.HOME).write_text(FORWARD, encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    if profile == "production":
        (out / "robots.txt").write_text(ROBOTS, encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--profile", required=True, choices=("production", "staging"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a.profile, a.out)
    print(f"{a.profile}: {a.out}")
