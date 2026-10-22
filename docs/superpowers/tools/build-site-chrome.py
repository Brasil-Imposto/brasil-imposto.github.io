"""Writes the site header shared by the three published pages (site_chrome.py, D152) into Os 3 Poderes and Como o dinheiro
anda, between its markers. Início gets it from build-platform-preview.py. Running it twice changes nothing.

Run: python3 docs/superpowers/tools/build-site-chrome.py
"""
import re
from pathlib import Path

import site_chrome

PREVIEWS = Path(__file__).resolve().parents[1] / "previews"

for key in ("tres-poderes", "dinheiro"):
    path = PREVIEWS / site_chrome.PAGES[key][0]
    page = path.read_text(encoding="utf-8")
    # the page's own header, from before D152, leaves once
    page, n = re.subn(r'<header class="nav">.*?</header>\n', "", page, count=1, flags=re.S)
    assert n <= 1
    new = site_chrome.inject(page, key)
    if new != path.read_text(encoding="utf-8"):
        path.write_text(new, encoding="utf-8")
    print(path.name, "removed old header" if n else "", "ok")
