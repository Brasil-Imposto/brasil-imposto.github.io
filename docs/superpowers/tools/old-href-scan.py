"""No href to the old Início address (BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html) in the assembled _site outside its
forwarding page (D160). --plant puts the old name back in one link of index.html; the scan must then find it.
Usage: python3 docs/superpowers/tools/old-href-scan.py <_site> [--plant]"""
import re, sys
from pathlib import Path
OLD = "BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html"
site = Path(sys.argv[1]); hits = []
for f in sorted(site.rglob("*")):
    if not f.is_file() or f.suffix not in {".html", ".js", ".css", ".json", ".svg", ".txt", ".xml"} or f.name == OLD and f.parent == site:
        continue
    t = f.read_text(encoding="utf-8", errors="replace")
    if "--plant" in sys.argv and f.name == "index.html":
        t = t.replace('href="./"', f'href="{OLD}"', 1)
    hits += [f"{f.relative_to(site)}: {m}" for m in re.findall(r'href\s*=\s*["\']?[^"\'> ]*' + re.escape(OLD), t)]
print("\n".join(hits[:10])); print(f"{len(hits)} hrefs to the old name outside the forwarding page"); sys.exit(1 if hits else 0)
