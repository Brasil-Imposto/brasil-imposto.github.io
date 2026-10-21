"""Builds the platform preview (D134): the approved home simulation plus the money network for every period of the map,
the support block and "Fale com a gente", and the notes for the author. Nothing in the simulation is removed (D59): the
builder only inserts, each insertion at an anchor that must appear exactly once.

Run: .venv/bin/python docs/superpowers/tools/build-platform-preview.py
     (after build-ledger-interest-asset.py; check the periods first with ledger-graph-periods-check.cjs)
"""
from pathlib import Path

PREVIEWS = Path(__file__).resolve().parents[1] / "previews"
SIM = PREVIEWS / "BRASIL-IMPOSTO_DESIGN_home-simulacao_2026-09-29.html"
OUT = PREVIEWS / "BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html"
SRC = PREVIEWS / "src"


def insert(page, anchor, new, before=True):
    assert page.count(anchor) == 1, f"anchor not unique: {anchor[:60]}"
    return page.replace(anchor, new + anchor if before else anchor + new)


page = SIM.read_text(encoding="utf-8")
page = insert(page, '<link rel="stylesheet" href="assets/home-feed.css">', '\n<link rel="stylesheet" href="assets/platform.css">', before=False)
nav = '<nav><span>Como funciona</span><span>Fontes</span><span>Código aberto</span></nav>'
assert page.count(nav) == 1
page = page.replace(nav, '<nav><a href="BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html">Os 3 Poderes</a><a href="BRASIL-IMPOSTO_DESIGN_como-o-dinheiro-anda-round-1_2026-10-21.html">Como o dinheiro anda</a><span>Fontes</span><span>Código aberto</span><a href="#rede">Rede (prévia)</a>'
                         '<a href="#fale">Fale com a gente</a><a class="pf-cta" href="#apoie">Apoie</a></nav>')
page = insert(page, '<script src="assets/bi-data.js"></script>',
              (SRC / "platform-sections.html").read_text(encoding="utf-8") + "\n" + (SRC / "platform-notes.html").read_text(encoding="utf-8") + "\n")
page = insert(page, "</body>", (SRC / "platform-script.html").read_text(encoding="utf-8"))
assert chr(0x2014) not in page and chr(0x2013) not in page, "dash found"
OUT.write_text(page, encoding="utf-8")
print(OUT.name, round(OUT.stat().st_size / 1024), "KB")
