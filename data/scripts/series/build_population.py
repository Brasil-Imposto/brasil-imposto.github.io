"""Population by UF and by municipality of the chosen states (default Santa Catarina), every year 2019 to 2026
-> data/series/population.json (one block per state: sc_municipalities, rs_municipalities)

Sources (IBGE, no key):
  estimates: SIDRA table 6579, variable 9324 (2019, 2020, 2021, 2024, 2025, 2026)
  2022: Censo 2022, SIDRA table 4709, variable 93 (populacao residente)
  2023: IBGE published no estimate (table 6579 has no 2023 period) -> null with the reason.
Usage: build_population.py <workdir> [--uf SC,RS] [--out PATH] [--collected-at YYYY-MM-DD]
"""
import json, os, subprocess, sys
from datetime import date
from pathlib import Path

def opt(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default
W = Path(sys.argv[1]) / "pop"; W.mkdir(parents=True, exist_ok=True)
OUT = Path(opt("--out") or Path(__file__).resolve().parents[2] / "series" / "population.json")
MUNI_UFS = opt("--uf", "SC").upper().split(",")
API = "https://servicodados.ibge.gov.br/api/v3/agregados"
EST = f"{API}/6579/periodos/2019|2020|2021|2024|2025|2026/variaveis/9324"
CEN = f"{API}/4709/periodos/2022/variaveis/93"
UFS = {'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO','21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE',
       '29':'BA','31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS','50':'MS','51':'MT','52':'GO','53':'DF'}

def fetch(url, name):
    p = W / name
    subprocess.run(["curl", "-g", "-sS", "-m", "300", "-o", str(p), url], check=True)
    return json.load(open(p))

def series(d):
    out = {}
    for r in d:
        for x in r["resultados"]:
            for s in x["series"]:
                out.setdefault(s["localidade"]["id"], {"name": s["localidade"]["nome"], "values": {}})["values"].update(
                    {y: (int(v) if v not in ("-", "...", "..", "X", None) else None) for y, v in s["serie"].items()})
    return out

CODE = {u: c for c, u in UFS.items()}
urls = {"est_uf": f"{EST}?localidades=N1[all]|N3[all]", "cen_uf": f"{CEN}?localidades=N1[all]|N3[all]"}
for u in MUNI_UFS:
    urls[f"est_{u.lower()}"] = f"{EST}?localidades=N6[N3[{CODE[u]}]]"
    urls[f"cen_{u.lower()}"] = f"{CEN}?localidades=N6[N3[{CODE[u]}]]"
data = {k: series(fetch(u, k + ".json")) for k, u in urls.items()}
YEARS = [str(y) for y in range(2019, 2027)]
REASON_2023 = "IBGE não publicou estimativa de população para 2023: a tabela 6579 pula de 2021 para 2024 e o Censo 2022 é a referência de 2022."

def build(est, cen, ids):
    res = {}
    for i in ids:
        v = dict(est.get(i, {}).get("values", {}))
        v.update(cen.get(i, {}).get("values", {}))
        res[i] = {"name": (est.get(i) or cen.get(i))["name"], "population": {y: v.get(y) for y in YEARS}}
    return res

uf_ids = ["1"] + sorted(UFS)
uf = build(data["est_uf"], data["cen_uf"], uf_ids)
uf_out = {("BR" if i == "1" else UFS[i]): {"ibge_code": i, **uf[i]} for i in uf_ids}
muni_out = {}
for u in MUNI_UFS:
    est, cen = data[f"est_{u.lower()}"], data[f"cen_{u.lower()}"]
    muni_out[u] = build(est, cen, sorted(set(est) | set(cen)))

checks = {}
for y in YEARS:
    if y == "2023": continue
    s = sum(uf_out[u]["population"][y] for u in UFS.values())
    checks[y] = {"sum_27_ufs": s, "brasil": uf_out["BR"]["population"][y]}
    for u, mo in muni_out.items():
        checks[y].update({f"{u.lower()}_sum_municipalities": sum(m["population"][y] or 0 for m in mo.values()),
                          f"{u.lower()}_state": uf_out[u]["population"][y],
                          f"{u.lower()}_municipalities_with_value": sum(m["population"][y] is not None for m in mo.values())})
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    "years": [int(y) for y in YEARS],
    "method": {"2019-2021, 2024-2026": "IBGE, Estimativas da População (1º de julho), SIDRA 6579, variável 9324",
               "2022": "IBGE, Censo Demográfico 2022, população residente (data de referência 1º de agosto de 2022), SIDRA 4709, variável 93",
               "2023": "null: " + REASON_2023},
    "null_reasons": {"2023": REASON_2023},
    "uf": uf_out, **{f"{u.lower()}_municipalities": mo for u, mo in muni_out.items()},
    "sources": [{"field": "population (estimativas)", "url": EST + "?localidades=N1[all]|N3[all]|" + "|".join(f"N6[N3[{CODE[u]}]]" for u in MUNI_UFS)},
                {"field": "population 2022 (Censo)", "url": CEN + "?localidades=N1[all]|N3[all]|" + "|".join(f"N6[N3[{CODE[u]}]]" for u in MUNI_UFS)}],
    "collected_at": opt("--collected-at") or date.today().isoformat(), "checks": checks,
}, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(checks, indent=1))
