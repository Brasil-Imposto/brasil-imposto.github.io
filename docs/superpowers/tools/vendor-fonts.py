"""The site's fonts served by the site itself (spec seguranca-doacoes, section 8; Signal and ethereum.org do the same): the
woff2 files Google Fonts serves to a current Chrome for the two stylesheets the pages used, with the same @font-face blocks
and unicode ranges, so the letters do not change. Both families are under the SIL Open Font License 1.1; the license text
comes from the Google Fonts repository, beside the files.

Run once per change of family or weight: python3 docs/superpowers/tools/vendor-fonts.py
"""
import re
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "previews" / "assets" / "fonts"
CHROME = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
FAMILIES = {   # the stylesheet each page asked Google for until 2026-11-03, and the license of the family
    "manrope": ("https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap",
                "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/OFL.txt"),
    "jetbrains-mono": ("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@600;800&display=swap",
                       "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/OFL.txt"),
}


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": CHROME}), timeout=60) as r:
        return r.read()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (css_url, license_url) in FAMILIES.items():
        css = fetch(css_url).decode("utf-8")
        files = {}
        for subset, url in re.findall(r"/\* ([\w-]+) \*/\s*@font-face \{[^}]*?src: url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", css):
            files.setdefault(url, f"{name}-{subset}.woff2")
        if not files:
            raise SystemExit(f"vendor-fonts: no woff2 in the stylesheet of {name}")
        for url, local in files.items():
            (OUT / local).write_bytes(fetch(url))
            css = css.replace(url, local)
        if "fonts.gstatic.com" in css:
            raise SystemExit(f"vendor-fonts: {name} still points at Google")
        (OUT / f"{name}.css").write_text(f"/* {name}: the files Google Fonts serves, kept by the site (vendor-fonts.py); SIL OFL 1.1, OFL-{name}.txt */\n" + css,
                                         encoding="utf-8")
        (OUT / f"OFL-{name}.txt").write_bytes(fetch(license_url))
        print(f"{name}: {len(files)} files")


if __name__ == "__main__":
    main()
