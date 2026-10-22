"""Fetch company registry records (Receita Federal open CNPJ base) through public mirrors.

The official servers (arquivos.receitafederal.gov.br, dadosabertos.rfb.gov.br) refuse connections from
outside Brazil (see the Hercilio Luz research diary). Mirrors tried in order:
  1. https://minhareceita.org/<cnpj>        (open-source republication of the Receita base)
  2. https://publica.cnpj.ws/cnpj/<cnpj>    (public tier of CNPJ.ws, also derived from the Receita base; rate-limited, hence the pause)
Both are derived sources, not the official server. Partner CPFs are masked by the Receita itself.

Usage: python3 cnpj_fetch.py <outdir> <cnpj> [<cnpj> ...]
"""
import json
import os
import sys
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
MIRRORS = [("minhareceita.org", "https://minhareceita.org/{}"), ("publica.cnpj.ws", "https://publica.cnpj.ws/cnpj/{}")]


def fetch(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            return json.load(r)
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


def main(outdir, *cnpjs):
    os.makedirs(outdir, exist_ok=True)
    for c in cnpjs:
        for name, pattern in MIRRORS:
            url = pattern.format(c)
            d = fetch(url)
            ok = "_error" not in d and not d.get("message")
            if ok:
                d["_mirror"] = name
                d["_url"] = url
                json.dump(d, open(os.path.join(outdir, f"{c}.json"), "w"), ensure_ascii=False, indent=1)
                print(c, "ok", name, flush=True)
                break
            print(c, "fail", name, d.get("_error") or d.get("message"), flush=True)
            time.sleep(2)
        time.sleep(22)


if __name__ == "__main__":
    main(*sys.argv[1:])
