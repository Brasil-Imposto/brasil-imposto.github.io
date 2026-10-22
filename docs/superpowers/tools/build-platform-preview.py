"""Builds the platform page (D134): the approved home simulation plus the money network for every period of the map.
Nothing in the simulation is removed (D59): the builder only inserts, each insertion at an anchor that must appear
exactly once.

Two builds from the same sources:
- the published page (default), what GitHub Pages serves: no author notes and nothing that does nothing. The support
  block, its nav buttons and "Fale com a gente" stay out until D125's bar is met (D123, D124), and so do the notes for
  the author and the nav items with no destination.
- the author's preview (--author-notes): everything above included, written to its own file, which git ignores.

Run: .venv/bin/python docs/superpowers/tools/build-platform-preview.py [--author-notes]
     (after build-ledger-interest-asset.py; check the periods first with ledger-graph-periods-check.cjs)
"""
import sys
from pathlib import Path

PREVIEWS = Path(__file__).resolve().parents[1] / "previews"
SIM = PREVIEWS / "BRASIL-IMPOSTO_DESIGN_home-simulacao_2026-09-29.html"
OUT = PREVIEWS / "BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html"
OUT_AUTHOR = PREVIEWS / "BRASIL-IMPOSTO_AUTHOR_platform-preview_2026-10-09.html"
SRC = PREVIEWS / "src"
REPO = "https://github.com/Brasil-Imposto/brasil-imposto.github.io"
PAGES = ('<a href="BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html">Os 3 Poderes</a>'
         '<a href="BRASIL-IMPOSTO_DESIGN_como-o-dinheiro-anda-round-1_2026-10-21.html">Como o dinheiro anda</a>')


def insert(page, anchor, new, before=True):
    assert page.count(anchor) == 1, f"anchor not unique: {anchor[:60]}"
    return page.replace(anchor, new + anchor if before else anchor + new)


def build(author_notes):
    src = lambda name: (SRC / name).read_text(encoding="utf-8")
    page = SIM.read_text(encoding="utf-8")
    page = insert(page, '<link rel="stylesheet" href="assets/home-feed.css">', '\n<link rel="stylesheet" href="assets/platform.css">', before=False)
    nav = '<nav><span>Como funciona</span><span>Fontes</span><span>Código aberto</span></nav>'
    assert page.count(nav) == 1
    if author_notes:
        new_nav = (f'<nav>{PAGES}<span>Fontes</span><span>Código aberto</span><a href="#rede">Rede (prévia)</a>'
                   '<a href="#fale">Fale com a gente</a><a class="pf-cta" href="#apoie">Apoie</a></nav>')
        sections = src("platform-sections.html") + "\n" + src("platform-support.html") + "\n" + src("platform-notes.html") + "\n"
    else:
        new_nav = f'<nav>{PAGES}<a href="{REPO}">Código aberto</a><a href="#rede">Rede (prévia)</a></nav>'
        sections = src("platform-sections.html") + "\n"
    page = page.replace(nav, new_nav)
    page = insert(page, '<script src="assets/bi-data.js"></script>', sections)
    script = src("platform-script.html")
    if author_notes:  # the support block's handlers go in before the script's closing lines
        script = insert(script, "})();\n</script>", src("platform-support-script.html"))
    page = insert(page, "</body>", script)
    assert chr(0x2014) not in page and chr(0x2013) not in page, "dash found"
    if not author_notes:
        for banned in ('id="apoie"', 'id="fale"', 'Só na prévia', 'class="doc"', 'data-contact'):
            assert banned not in page, f"author material in the published page: {banned}"
    return page


author_notes = "--author-notes" in sys.argv[1:]
out = OUT_AUTHOR if author_notes else OUT
out.write_text(build(author_notes), encoding="utf-8")
print(out.name, round(out.stat().st_size / 1024), "KB")
