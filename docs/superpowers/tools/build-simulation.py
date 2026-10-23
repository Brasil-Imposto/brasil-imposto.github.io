"""Builds the home simulation as one HTML that opens straight from the file path.

Chrome refuses local ES-module imports on file:// pages, so the site's own modules (hero3d.js, modals.js) are
inlined into the page's module script, each wrapped in its own scope. three.js still comes from the CDN through
the import map, which file:// pages may load. Data arrives through classic scripts (bi-data.js, bi-geo.js).
Run: python3 docs/superpowers/tools/build-simulation.py
"""
import re
from pathlib import Path

PREVIEWS = Path(__file__).resolve().parents[1] / "previews"
SOURCE = PREVIEWS / "BRASIL-IMPOSTO_DESIGN_hero-mapa-3d-round-2_2026-09-29.html"
TARGET = PREVIEWS / "BRASIL-IMPOSTO_DESIGN_home-simulacao_2026-09-29.html"
MODULES = [("hero3d", PREVIEWS / "assets" / "hero3d.js"), ("modals", PREVIEWS / "assets" / "modals.js")]

hoisted, bundles = [], []
for name, path in MODULES:
    code = path.read_text(encoding="utf-8")
    for line in re.findall(r"^import .* from '[^.][^']*';$", code, flags=re.M):
        hoisted.append(line)
    if not (not re.search(r"^import .* from '\.", code, flags=re.M)):
        raise SystemExit(f"{name}: local imports are not supported by this bundler")
    code = re.sub(r"^import .* from '[^']*';\n", "", code, flags=re.M)
    exports = re.findall(r"^export (?:async )?(?:function|const) (\w+)", code, flags=re.M)
    code = re.sub(r"^export ", "", code, flags=re.M)
    bundles.append(f"const __{name} = (() => {{\n{code}\nreturn {{ {', '.join(exports)} }};\n}})();")

page = SOURCE.read_text(encoding="utf-8")
m = re.search(r'<script type="module">\n(.*?)</script>', page, flags=re.S)
body = m.group(1)
for name, _ in MODULES:
    body, n = re.subn(rf"  import \{{ ([^}}]+) \}} from '\./assets/{name}\.js\?v=[^']*';\n", rf"  const {{ \1 }} = __{name};\n", body)
    if not (n == 1):
        raise SystemExit(f"page import of {name} not found")
bundle = "\n".join(dict.fromkeys(hoisted)) + "\n" + "\n".join(bundles) + "\n" + body
out = page[:m.start()] + '<script type="module">\n// Built by docs/superpowers/tools/build-simulation.py; edit the sources, not this file.\n' + bundle + "</script>" + page[m.end():]
out = out.replace("<title>Hero Mapa 3D</title>", "<title>Brasil-Imposto</title>")
# The simulation is the home page only; the design notes below the hero belong to the review documents.
out, n = re.subn(r'\n<main class="doc">.*?</main>\n', "\n", out, flags=re.S)
if not (n == 1):
    raise SystemExit("design-notes block not found")
TARGET.write_text(out, encoding="utf-8")
print(TARGET.name, round(TARGET.stat().st_size / 1024), "KB; hoisted imports:", len(dict.fromkeys(hoisted)))
