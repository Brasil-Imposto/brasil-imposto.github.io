"""Query SC Transparency Portal (Poder Executivo) supplier payments for the bridge contractors.

API behind https://www.transparencia.sc.gov.br/fornecedores (Solr-backed, no login):
  credor lookup: {API}/busca/documento?tipofiltro=credorfiltro&query=<CNPJ>
  totals:        {API}/pgtocredor?anomesinifiltro=YYYYMM&anomesfimfiltro=YYYYMM&credorfiltro[]=<id>
                 &tipopagamentocredorfiltro=1&totais=1&page=1&indicador=0[&unidadegestorafiltro[]=<ug>]
tipopagamentocredorfiltro=1 is the default the portal page itself sends. Portal coverage starts in 2011.
Usage: python3 payments.py <out.json>
"""
import json
import sys
import urllib.parse
import urllib.request

API = "https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api"
COMPANIES = {
    "24447770000145": "Teixeira Duarte",
    "17159856000107": "EMPA",
    "10769406000197": "Consorcio Florianopolis Monumento",
    "38738381000183": "RMG Engenharia",
    "80996861000100": "Prosul",
    "33146648000391": "Concremat (filial 0003)",
    "52573623000157": "Fares & Associados",
    "01956161000116": "Geoarqueologia",
    "24055348000144": "SDF Engenharia",
}
UGS = {"530025": "DEINFRA", "530001": "SIE"}


def get(path, params):
    url = f"{API}/{path}?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"Referer": "https://www.transparencia.sc.gov.br/"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r), url


def totals(credor, y0, y1, ug=None):
    p = {"anomesinifiltro": f"{y0}01", "anomesfimfiltro": f"{y1}12", "credorfiltro[]": credor,
         "tipopagamentocredorfiltro": 1, "totais": 1, "page": 1, "indicador": 0}
    if ug:
        p["unidadegestorafiltro[]"] = ug
    d, url = get("pgtocredor", p)
    tot = d.get("totais") or {}
    return (tot if isinstance(tot, dict) else {}), url


def main(out):
    res = {"api": API, "collected_on": None, "companies": []}
    for cnpj, name in COMPANIES.items():
        d, surl = get("busca/documento", {"page": 1, "tipofiltro": "credorfiltro", "query": cnpj})
        docs = [x for x in d["response"]["docs"] if x.get("cnpj") == cnpj or x.get("identificacao") == cnpj]
        entry = {"cnpj": cnpj, "name": name, "credor_ids": [x["id"] for x in docs],
                 "credor_names": [x["descricao"].strip() for x in docs], "lookup_url": surl, "by_year": []}
        for cid in entry["credor_ids"]:
            for y in range(2011, 2027):
                row = {"credor_id": cid, "year": y}
                t, url = totals(cid, y, y)
                row["all_units"] = t
                row["url_all_units"] = url
                for ug, ugname in UGS.items():
                    t2, url2 = totals(cid, y, y, ug)
                    row[f"ug_{ug}_{ugname}"] = t2
                if any(float(v or 0) for v in t.values()):
                    entry["by_year"].append(row)
        res["companies"].append(entry)
        print(name, entry["credor_ids"], len(entry["by_year"]), flush=True)
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
