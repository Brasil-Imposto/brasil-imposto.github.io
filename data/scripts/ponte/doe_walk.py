"""Walk DOE-SC editions by date and internal id, download PDFs, extract text.

The public repository serves https://portal.doe.sea.sc.gov.br/repositorio/{YYYY}/{YYYYMMDD}/Jornal/{cd}.pdf
where cd is a sequential internal id (about one per edition). The edition-list API needs login, so
this walks forward from a known (date, cd) pair and probes cd..cd+window for each calendar day.
Usage: python3 doe_walk.py <start YYYY-MM-DD> <start cd> <days> <outdir>
Note: the server's TLS chain lacks an intermediate certificate; verification is disabled for these
read-only downloads of public PDFs.
"""
import datetime
import os
import ssl
import subprocess
import sys
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
BASE = "https://portal.doe.sea.sc.gov.br/repositorio/{y}/{d}/Jornal/{cd}{suf}.pdf"


def fetch(url):
    try:
        with urllib.request.urlopen(url, context=CTX, timeout=60) as r:
            data = r.read()
            return data if data[:4] == b"%PDF" else None
    except Exception:
        return None


def main(start, cd, days, out):
    os.makedirs(out, exist_ok=True)
    day = datetime.date.fromisoformat(start)
    cd = int(cd)
    for _ in range(int(days)):
        d = day.strftime("%Y%m%d")
        if day.weekday() < 5:
            for c in range(cd, cd + 4):
                for suf in ("", "-A", "-B"):
                    url = BASE.format(y=day.year, d=d, cd=c, suf=suf)
                    data = fetch(url)
                    if data:
                        fn = os.path.join(out, f"{d}_{c}{suf}.pdf")
                        open(fn, "wb").write(data)
                        subprocess.run(["pdftotext", "-layout", fn, fn[:-4] + ".txt"], check=False)
                        print(d, c, suf, len(data), url, flush=True)
                        cd = max(cd, c + 1) if suf == "" else cd
        day += datetime.timedelta(days=1)


if __name__ == "__main__":
    main(*sys.argv[1:5])
