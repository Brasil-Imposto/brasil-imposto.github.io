"""Fetch pre-2012 DOE-SC editions from the Arquivo Publico do Estado (AtoM catalogue).

Edition pages use the slug diario-oficial-do-estado-de-santa-catarina-ano-{ano}-n-{n}-de-{dd}-{mm}-{yyyy};
each page links one PDF under /uploads/. The server returns intermittent HTTP 502, so every request retries.
Usage: python3 apesc_doe.py <ano> <start YYYY-MM-DD> <start n> <days> <outdir>
Walks business days, probing n..n+6 per day, and keeps the n pointer in sync with hits.
"""
import datetime
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

BASE = "https://acervo.arquivopublico.sc.gov.br"


def get(url, tries=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=90) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, b""
            time.sleep(4 + 4 * i)
        except Exception:
            time.sleep(4 + 4 * i)
    return 0, b""


def main(ano, start, n, days, out):
    os.makedirs(out, exist_ok=True)
    day = datetime.date.fromisoformat(start)
    n = int(n)
    for _ in range(int(days)):
        if day.weekday() < 5:
            for c in range(n, n + 7):
                slug = f"diario-oficial-do-estado-de-santa-catarina-ano-{ano}-n-{c}-de-{day:%d-%m-%Y}"
                st, body = get(f"{BASE}/index.php/{slug}")
                if st != 200:
                    continue
                m = re.search(rb'href="(https://acervo\.arquivopublico\.sc\.gov\.br/uploads/[^"]+\.pdf)"', body)
                if not m:
                    print(day, c, "page-without-pdf", flush=True)
                    continue
                pdf_url = m.group(1).decode()
                st2, pdf = get(pdf_url)
                fn = os.path.join(out, f"{day:%Y%m%d}_{c}.pdf")
                if st2 == 200 and pdf[:4] == b"%PDF":
                    open(fn, "wb").write(pdf)
                    subprocess.run(["pdftotext", fn, fn[:-4] + ".raw.txt"], check=False)
                    print(day, c, len(pdf), pdf_url, flush=True)
                else:
                    print(day, c, "pdf-failed", pdf_url, flush=True)
                n = c + 1
                break
        day += datetime.timedelta(days=1)


if __name__ == "__main__":
    main(*sys.argv[1:6])
