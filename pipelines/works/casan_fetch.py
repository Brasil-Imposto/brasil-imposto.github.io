"""Download the official Casan records used for data/works/ete-insular.json.

Sources (no login; the Casan transparency portal is an Angular app over these JSON endpoints):
  {T}/data/contrato?ano=<year>&objeto=<text>&page=<n>   contract register with amendments (PNTP view)
  {T}/data/contratos?empresafiltro[]=<supplier id>&dtinivigenciainifiltro=...&dtinivigenciafimfiltro=...
                                                     SAP view: contract value, amount consumed, balance
  {T}/data/contratos/dataAtualizacao                 date of the last SAP load
  {T}/data/contrato/arquivo/<id>                     amendment PDFs listed in the PNTP view
  {T}/data/subareainteresse?url=obras                "Obras de expansao" table (CSV link id)
  {T}/data/download/<link id>/2                      that CSV
T = https://transparencia.casan.com.br

Usage: python3 casan_fetch.py <outdir>
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

T = "https://transparencia.casan.com.br"
H = {"X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0"}
PNTP_QUERIES = [(y, "INSULAR") for y in range(2012, 2027)] + [(y, "POTECAS") for y in range(2020, 2027)]
SAP_SUPPLIERS = {
    "2000009269": "CONSORCIO ITAJUI/CONSTRUTAMI ETE INSULAR",
    "2000004932": "ITAJUI ENGENHARIA DE OBRAS LTDA",
    "2000004715": "TRIX ENGENHARIA CIVIL LTDA",
    "2000005225": "INFRACON ENG. E COM. LTDA",
    "2000003662": "CONSTRUTORA CFO LTDA",
}
KEEP = ("EOC1151/2018", "EOC1246/2020", "EOC1534/2026", "EOC1119/2017", "EOC1314/2022", "EOC1377/2024", "EOC1399/2024")


def get(url, binary=False):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=180) as r:
                data = r.read()
            return data if binary else json.loads(data)
        except Exception as e:  # noqa: BLE001
            print("retry", attempt, url, e, file=sys.stderr)
            time.sleep(4 + 4 * attempt)
    raise SystemExit("failed " + url)


def main(out):
    os.makedirs(os.path.join(out, "pdf"), exist_ok=True)
    res = {"collected_from": T, "pntp": {}, "sap": {}, "sap_updated": None, "obras_csv": None}
    for year, text in PNTP_QUERIES:
        page = 1
        while True:
            url = f"{T}/data/contrato?" + urllib.parse.urlencode({"ano": year, "objeto": text, "page": page})
            d = get(url)
            for rec in d.get("data", []):
                if rec["contrato"].startswith(KEEP):
                    res["pntp"][rec["contrato"]] = {"query_url": url, "record": rec}
            if page >= d.get("last_page", 1):
                break
            page += 1
    res["sap_updated"] = get(f"{T}/data/contratos/dataAtualizacao")
    for sid, name in SAP_SUPPLIERS.items():
        url = f"{T}/data/contratos?" + urllib.parse.urlencode(
            {"empresafiltro[]": sid, "dtinivigenciainifiltro": "2000-01-01", "dtinivigenciafimfiltro": "2026-12-31", "page": 1})
        res["sap"][sid] = {"name": name, "query_url": url, "rows": get(url)["lista"]["data"]}
    sub = get(f"{T}/data/subareainteresse?url=obras")
    link = sub["grupolink"][0]["link"][0]
    csv_url = f"{T}/data/download/{link['id']}/2"
    open(os.path.join(out, "casan_obras_expansao.csv"), "wb").write(get(csv_url, binary=True))
    res["obras_csv"] = {"url": csv_url, "label": link.get("texto"), "file": link.get("arquivo2")}
    for num in ("EOC1246/2020/MAT", "EOC1534/2026/MAT"):
        rec = res["pntp"].get(num, {}).get("record", {})
        files = list(rec.get("arquivos") or [])
        for a in rec.get("aditivos") or []:
            files += a.get("arquivos") or []
        for f in files:
            path = os.path.join(out, "pdf", f"{f['id']}.pdf")
            if not os.path.exists(path):
                open(path, "wb").write(get(f"{T}/data/contrato/arquivo/{f['id']}", binary=True))
    json.dump(res, open(os.path.join(out, "casan_raw.json"), "w"), ensure_ascii=False, indent=1)
    print("pntp", sorted(res["pntp"]), "sap", {k: len(v["rows"]) for k, v in res["sap"].items()})


if __name__ == "__main__":
    main(sys.argv[1])
