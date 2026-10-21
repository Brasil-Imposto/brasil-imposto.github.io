"""Joinville open-data API (e-Publica): contracts and spending records for one supplier/contract.

Endpoints (documented by the portal itself at dadosAbertos/contrato and dadosAbertos/despesa, no login):
  {API}/contrato?periodo_inicial=dd/mm/aaaa&periodo_final=dd/mm/aaaa&codigo_unidade=0   (same fiscal year)
  {API}/despesa?periodo_inicial=mm/aaaa&periodo_final=mm/aaaa&codigo_unidade=0          (~10 MB per month)
Each despesa record is one empenho with its movements (emissao, liquidacao, pagamento, anulacao).
Only records whose supplier CNPJ or contract number match are kept.

Usage: python3 joinville_payments.py <outdir> <cnpj> <contract> <first yyyy-mm> <last yyyy-mm> [contract_years...]
Example: python3 joinville_payments.py work 03.184.733/0001-11 366/2023 2023-01 2026-09 2023
"""
import json
import os
import sys
import time
import urllib.request

API = "https://transparencia.joinville.sc.gov.br/epublica-portal/rest/joinville/api/v1"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def get(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            print("retry", attempt, e, file=sys.stderr, flush=True)
            time.sleep(5 + 5 * attempt)
    raise SystemExit("failed " + url)


def months(a, b):
    y, m = map(int, a.split("-"))
    y2, m2 = map(int, b.split("-"))
    while (y, m) <= (y2, m2):
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def main(outdir, cnpj, contract, first, last, *contract_years):
    os.makedirs(outdir, exist_ok=True)
    out = {"api": API, "cnpj": cnpj, "contract": contract, "contracts": [], "despesa": [], "queries": []}
    for y in contract_years:
        url = f"{API}/contrato?periodo_inicial=01/01/{y}&periodo_final=31/12/{y}&codigo_unidade=0"
        d = get(url)
        out["queries"].append({"url": url, "total": d.get("totalRegistros"), "updated": d.get("ultimaAtualizacao")})
        for r in d.get("registros", []):
            reg = r["registro"]
            if reg["contrato"]["numero"] == contract or (reg.get("fornecedor") or {}).get("pessoa", {}).get("cpfCnpj") == cnpj:
                out["contracts"].append(reg)
    for y, m in months(first, last):
        url = f"{API}/despesa?periodo_inicial={m:02d}/{y}&periodo_final={m:02d}/{y}&codigo_unidade=0"
        d = get(url)
        n = 0
        for r in d.get("registros", []):
            reg = r["registro"]
            emp = reg.get("empenho") or {}
            if emp.get("contrato") == contract or (reg.get("fornecedor") or {}).get("pessoa", {}).get("cpfCnpj") == cnpj:
                reg["_query_month"] = f"{y}-{m:02d}"
                out["despesa"].append(reg)
                n += 1
        out["queries"].append({"url": url, "total": d.get("totalRegistros"), "updated": d.get("ultimaAtualizacao"), "kept": n})
        print(y, m, d.get("totalRegistros"), "kept", n, flush=True)
        json.dump(out, open(os.path.join(outdir, "joinville_raw.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(out, open(os.path.join(outdir, "joinville_raw.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:])
