"""Download free-license photos from Wikimedia Commons, resized to at most 1000 px wide (macOS sips), and write credits.json,
in the format of docs/superpowers/previews/assets/cases/hercilio-luz/credits.json.

Usage: python3 media_fetch.py <slug> <local-name>=<Commons file title> [...]
Example: python3 media_fetch.py ete-insular "baia-sul.jpg=File:Baía Sul de Florianópolis.jpg"
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
UA = {"User-Agent": "BrasilImpostoResearch/0.1 (civic research; open-source project)"}
API = "https://commons.wikimedia.org/w/api.php"


def clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def main(slug, *pairs):
    outdir = os.path.join(REPO, "docs", "superpowers", "previews", "assets", "cases", slug)
    os.makedirs(outdir, exist_ok=True)
    credits = {}
    for pair in pairs:
        local, title = pair.split("=", 1)
        q = urllib.parse.urlencode({"action": "query", "titles": title, "prop": "imageinfo",
                                    "iiprop": "url|size|extmetadata", "iiurlwidth": 1000, "format": "json"})
        d = json.load(urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers=UA), timeout=60))
        page = next(iter(d["query"]["pages"].values()))
        ii = page["imageinfo"][0]
        em = ii.get("extmetadata", {})
        url = ii["thumburl"] if ii.get("width", 0) > 1000 else ii["url"]
        for attempt in range(6):
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or attempt == 5:
                    raise
                time.sleep(20 * (attempt + 1))
        path = os.path.join(outdir, local)
        open(path, "wb").write(data)
        if ii.get("width", 0) > 1000 or len(data) > 700_000:
            # macOS sips: resample to 1000 px wide (or keep width) and recompress, to keep the page light
            w = min(1000, ii.get("width", 1000))
            subprocess.run(["sips", "--resampleWidth", str(w), "-s", "formatOptions", "82", path], capture_output=True, check=True)
            data = open(path, "rb").read()
        credits[local] = {
            "file": local,
            "commons": ii["descriptionurl"],
            "license": clean(em.get("LicenseShortName", {}).get("value")),
            "license_url": clean(em.get("LicenseUrl", {}).get("value")) or None,
            "author": clean(em.get("Artist", {}).get("value")),
            "date": clean(em.get("DateTimeOriginal", {}).get("value")),
            "description": clean(em.get("ImageDescription", {}).get("value"))[:300],
            "bytes": len(data),
        }
        print(local, len(data), credits[local]["license"], flush=True)
        time.sleep(3)
    json.dump(credits, open(os.path.join(outdir, "credits.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:])
