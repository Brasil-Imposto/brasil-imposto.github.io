"""Scan editions of the Joinville official gazette (Diario Oficial Eletronico do Municipio) for a text pattern.

The listing https://www.joinville.sc.gov.br/jornal/index/page/<N> links each edition PDF
(/public/portaladm/pdf/jornal/<hash>.pdf) and its annexes (/jornal/visualizaranexos?...).
No text search is offered by the site, so edition PDFs are downloaded and searched with pdftotext.

Usage: python3 joinville_gazette_scan.py <outdir> <first_page> <last_page> <regex> [<regex> ...]
Set DELETE_PDFS=1 to delete each edition after it is searched.
"""
import os
import re
import subprocess
import sys
import urllib.request

BASE = "https://www.joinville.sc.gov.br"
UA = {"User-Agent": "Mozilla/5.0"}


def fetch(url, path=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
        data = r.read()
    if path:
        open(path, "wb").write(data)
    return data


def main(outdir, first, last, *patterns):
    os.makedirs(outdir, exist_ok=True)
    regs = [re.compile(p, re.I) for p in patterns]
    for page in range(int(first), int(last) + 1):
        html = fetch(f"{BASE}/jornal/index/page/{page}").decode("utf-8", "ignore")
        pdfs = sorted(set(re.findall(r'/public/portaladm/pdf/jornal/[0-9a-f]+\.pdf', html)))
        for rel in pdfs:
            path = os.path.join(outdir, os.path.basename(rel))
            if not os.path.exists(path):
                fetch(BASE + rel, path)
            txt = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout
            if os.environ.get("DELETE_PDFS") == "1":
                os.remove(path)
            head = " ".join(txt.split())[:160]
            for rg in regs:
                for m in rg.finditer(txt):
                    s = max(0, m.start() - 600)
                    print(f"== page {page} {BASE + rel} | {head}")
                    print(" ".join(txt[s:m.end() + 1600].split()))
        print("page", page, "pdfs", len(pdfs), flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
