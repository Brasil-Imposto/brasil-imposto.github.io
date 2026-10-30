"""Builds the platform page (D134): the approved home simulation plus the money network for every period of the map.
Nothing in the simulation is removed (D59): the builder only inserts, each insertion at an anchor that must appear
exactly once.

Two builds from the same sources:
- the published page (default), what GitHub Pages serves: no author notes and nothing that does nothing. The support
  block and "Fale com a gente" stay out until D125's bar is met (D123, D124), and so do the notes for the author. The
  header is the site header shared by the three pages (site_chrome.py, D152).
- the author's preview (--author-notes): everything above included, written to its own file, which git ignores.

Run: uv run python docs/superpowers/tools/build-platform-preview.py [--author-notes]
     (after build-ledger-interest-asset.py; check the periods first with ledger-graph-periods-check.cjs)
"""
import re
import sys
from pathlib import Path

import map_loader
import site_chrome

PREVIEWS = Path(__file__).resolve().parents[1] / "previews"
SIM = PREVIEWS / "BRASIL-IMPOSTO_DESIGN_home-simulacao_2026-09-29.html"
OUT = PREVIEWS / "BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html"
OUT_AUTHOR = PREVIEWS / "BRASIL-IMPOSTO_AUTHOR_platform-preview_2026-10-09.html"
SRC = PREVIEWS / "src"
# The three.js modules Início loads from the CDN through its import map, each with its hash (spec apoie, section 10.2, item 4): the
# five the page's code imports and the two Line2 imports. Computed from the files and matched with jsDelivr's own file hashes on
# 2026-10-29. Browsers check them from Chrome 127, Firefox 138 and Safari 18 (MDN); an older one ignores the list and runs the
# modules unchecked. Another three.js version stops the build until its hashes are here.
IMPORTMAP = '"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"\n}'
THREE_INTEGRITY = {
    "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js":
        "sha384-GY5FqjttLCFRt/McQbyaVdCk2O1IQtOeX8Py6NfD89BIAsIyJFRl4UgSXrk2vXAk",
    "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/lines/Line2.js":
        "sha384-svIqR2W/RlXb3d4T+bDn3JO+LXLbacA7GpMAUDJxTOFyZmVogvDRaOS7KZBRxcxc",
    "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/lines/LineGeometry.js":
        "sha384-nfFqbe33KO97I7jZXjW73quBqqskqqj64WZycLNDzn0GGGI3aoWLZzuy8i0jeYmU",
    "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/lines/LineMaterial.js":
        "sha384-bLpiIpNrFJ+EMb4Upzkap/Bc9Ul2wLoUMEfFm0PmZfyywMUYUsc5X98AuAYwwjq1",
    "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/lines/LineSegments2.js":
        "sha384-nm+9Od/cYIb15jGaA1U2Geoo18K/i9fF2fZ4KbI2rZydtfYxqwtWRlbvdVfiECU5",
    "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/lines/LineSegmentsGeometry.js":
        "sha384-2bbjHgEUXo9c3VW3OaZV638VYLXKhlNhNStU2D1Jm77zamWSQVYZak2p/Z0bZrmh",
    "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/renderers/CSS2DRenderer.js":
        "sha384-9CXQqRjuKfYvfHem9p/LPU6b7PaeeiDuC/gp1qRz3bEV9txWG5wi9XhrkE/0/Dn9"
}


def insert(page, anchor, new, before=True):
    if not (page.count(anchor) == 1):
        raise SystemExit(f"anchor not unique: {anchor[:60]}")
    return page.replace(anchor, new + anchor if before else anchor + new)


def build(author_notes):
    src = lambda name: (SRC / name).read_text(encoding="utf-8")
    page = SIM.read_text(encoding="utf-8")
    page = insert(page, IMPORTMAP, ',\n"integrity": {\n' + ",\n".join(f'  "{u}": "{h}"' for u, h in THREE_INTEGRITY.items()) + "\n}",
                  before=False)
    # The money network (its section, its scripts and platform.css) is in the author's preview only; the site build adds it to the
    # staging Início through the rede switch (build-site.py, D172, Q-A2), so the published page has nothing of it.
    if author_notes:
        page = insert(page, '<link rel="stylesheet" href="assets/home-feed.css">', '\n<link rel="stylesheet" href="assets/platform.css">', before=False)
    # D152: the hero's own header leaves; the site header shared by the three pages (site_chrome) takes its place.
    old, n = re.subn(r'\n  <header class="hero-nav">\n.*?\n  </header>', '', page, count=1, flags=re.S)
    if not (n == 1 and 'class="hero-nav"' not in old):
        raise SystemExit("hero header not found")
    page = site_chrome.inject(old, "inicio")
    # The home renders at 90% from 1063 px (D96, html { zoom: .9 }); the site header cancels it to keep its size on every page.
    zoom = "    html { zoom: .9; }\n"
    if not (page.count(zoom) == 1):
        raise SystemExit("the D96 zoom rule moved")
    page = page.replace(zoom, zoom + "    .bi-header, .bi-sheet, .bi-footer { zoom: 1.11111; } /* D152: the site header and footer keep their size */\n")
    # Tablets and phones reserved room at the top of the hero for its own header, now gone: keep only that header's margin.
    for old_pad, new_pad in (('column-gap: 16px; padding: 70px 24px 24px; }', 'column-gap: 16px; padding: 22px 24px 24px; }'),
                             ('flex-direction: column; padding-top: 58px; }', 'flex-direction: column; padding-top: 16px; }')):
        if not (page.count(old_pad) == 1):
            raise SystemExit(old_pad)
        page = page.replace(old_pad, new_pad)
    if author_notes:
        sections = src("platform-sections.html") + "\n" + src("platform-support.html") + "\n" + src("platform-notes.html") + "\n"
        page = insert(page, '<script src="assets/bi-data.js"></script>', sections)
        # the support block's handlers go in before the network script's closing lines
        page = insert(page, "</body>", insert(src("platform-script.html"), "})();\n</script>", src("platform-support-script.html")))
    # D152, L1: the map's data arrives through the loader, with the true percentage; every script after it waits for it.
    page, held, size = map_loader.apply(page, PREVIEWS / "assets" / "bi-data.js")
    if not (held >= 10):
        raise SystemExit(f"only {held} scripts held back")
    if not (chr(0x2014) not in page and chr(0x2013) not in page):
        raise SystemExit("dash found")
    if not author_notes:
        for banned in ('id="apoie"', 'id="fale"', 'Só na prévia', 'class="doc"', 'data-contact', 'id="rede"', 'data-graph', 'platform.css'):
            if not (banned not in page):
                raise SystemExit(f"author material in the published page: {banned}")
    return page


author_notes = "--author-notes" in sys.argv[1:]
out = OUT_AUTHOR if author_notes else OUT
out.write_text(build(author_notes), encoding="utf-8")
print(out.name, round(out.stat().st_size / 1024), "KB")
