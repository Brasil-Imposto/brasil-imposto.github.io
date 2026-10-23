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


def insert(page, anchor, new, before=True):
    if not (page.count(anchor) == 1):
        raise SystemExit(f"anchor not unique: {anchor[:60]}")
    return page.replace(anchor, new + anchor if before else anchor + new)


def build(author_notes):
    src = lambda name: (SRC / name).read_text(encoding="utf-8")
    page = SIM.read_text(encoding="utf-8")
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
    else:
        sections = src("platform-sections.html") + "\n"
    page = insert(page, '<script src="assets/bi-data.js"></script>', sections)
    script = src("platform-script.html")
    if author_notes:  # the support block's handlers go in before the script's closing lines
        script = insert(script, "})();\n</script>", src("platform-support-script.html"))
    page = insert(page, "</body>", script)
    # D152, L1: the map's data arrives through the loader, with the true percentage; every script after it waits for it.
    page, held, size = map_loader.apply(page, PREVIEWS / "assets" / "bi-data.js")
    if not (held >= 15):
        raise SystemExit(f"only {held} scripts held back")
    if not (chr(0x2014) not in page and chr(0x2013) not in page):
        raise SystemExit("dash found")
    if not author_notes:
        for banned in ('id="apoie"', 'id="fale"', 'Só na prévia', 'class="doc"', 'data-contact'):
            if not (banned not in page):
                raise SystemExit(f"author material in the published page: {banned}")
    return page


author_notes = "--author-notes" in sys.argv[1:]
out = OUT_AUTHOR if author_notes else OUT
out.write_text(build(author_notes), encoding="utf-8")
print(out.name, round(out.stat().st_size / 1024), "KB")
