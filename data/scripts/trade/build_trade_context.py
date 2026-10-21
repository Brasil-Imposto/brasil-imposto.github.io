"""Context for the export section, 2000 to 2025 -> data/trade/trade-context.json.

1. Exports and imports of goods and services as a share of GDP: IBGE, Contas Nacionais Trimestrais, SIDRA table 1846 (valores a
   preços correntes, R$ milhões), the four quarters of each year added up.
2. Exports by Secex "fator agregado" (básicos, semimanufaturados, manufaturados, operações especiais): Comex Stat API by NCM for
   each year, classified with the official NCM table (https://balanca.mdic.gov.br/balanca/bd/tabelas/NCM.csv, column CO_FAT_AGREG,
   names in NCM_FAT_AGREG.csv). Secex stopped publishing this split when it adopted ISIC (Nota Metodológica ISIC v1.1, Feb 2020),
   so from 2020 on it is computed here with the code the official table still carries.
3. Exports by ISIC section (Agropecuária, Indústria Extrativa, Indústria de Transformação, Outros Produtos), the split Secex
   publishes today: Comex Stat API, details ISICSection, by year.
Checks (nothing is written unless they pass): in every quarter household + government consumption + investment + change in
inventories + exports - imports = GDP, to the R$ million (rounding tolerance 3); the yearly GDP from the quarters matches the
annual national accounts (SIDRA 6784) within rounding or 0,2% (2017 to 2019 differ by about 0,1%, listed in the output); each year the NCM rows (fator
agregado) and the ISIC sections add up to the official MDIC conference total (EXP_TOTAIS_CONFERENCIA.csv) to the dollar.
--control drops the "básicos" of one year; the check must fail.
Run: python3 data/scripts/trade/build_trade_context.py [--control]
"""
import csv, io, json, sys
from collections import defaultdict
from trade_common import ROOT, comexstat, fetch_bytes, no_dash, write_json

OUT = ROOT / "data" / "trade" / "trade-context.json"
CONTROL = "--control" in sys.argv
Y0, Y1 = 2000, 2025
SIDRA_Q = (f"https://apisidra.ibge.gov.br/values/t/1846/n1/all/v/585/p/{Y0}01-{Y1}04/c11255/90707,93404,93405,93406,102880,93407,93408")
SIDRA_A = f"https://apisidra.ibge.gov.br/values/t/6784/n1/all/v/9808/p/{Y0}-{Y1}"
NCM_URL = "https://balanca.mdic.gov.br/balanca/bd/tabelas/NCM.csv"
FAT_URL = "https://balanca.mdic.gov.br/balanca/bd/tabelas/NCM_FAT_AGREG.csv"
TOTALS_URL = "https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_TOTAIS_CONFERENCIA.csv"
KEY = {"90707": "gdp", "93404": "households", "93405": "government", "93406": "investment", "102880": "inventories",
       "93407": "exports", "93408": "imports"}
fails = []

# 1. National accounts
q = defaultdict(dict)
for r in json.loads(fetch_bytes(SIDRA_Q))[1:]:
    q[r["D3C"]][KEY[r["D4C"]]] = int(r["V"])
years = defaultdict(lambda: defaultdict(int))
for qt, v in sorted(q.items()):
    if len(v) != 7:
        fails.append(f"{qt}: {len(v)} of 7 national accounts components"); continue
    s = v["households"] + v["government"] + v["investment"] + v["inventories"] + v["exports"] - v["imports"]
    if abs(s - v["gdp"]) > 3:
        fails.append(f"{qt}: components {s} != GDP {v['gdp']}")
    for k, x in v.items():
        years[int(qt[:4])][k] += x
    years[int(qt[:4])]["quarters"] += 1
annual = {int(r["D3C"]): int(r["V"]) for r in json.loads(fetch_bytes(SIDRA_A))[1:] if r["V"] not in ("...", "-", "X")}
# The quarterly values are rounded to the R$ million, so a year can differ from the annual table by a few millions; 2017 to 2019
# differ by about 0,1% (the two IBGE tables carry different vintages for those years). Each difference is kept in the output.
annual_diff = {}
for y, g in annual.items():
    d = years[y]["gdp"] - g
    if d:
        annual_diff[str(y)] = {"quarterly_sum": years[y]["gdp"], "annual_table": g, "difference": d}
    if abs(d) > 3 and abs(d) / g > 0.002:
        fails.append(f"{y}: quarterly GDP {years[y]['gdp']} != annual national accounts {g}")
gdp = [{"year": y, "gdp_brl_million": v["gdp"], "exports_brl_million": v["exports"], "imports_brl_million": v["imports"],
        "exports_share_of_gdp": round(v["exports"] / v["gdp"], 4), "imports_share_of_gdp": round(v["imports"] / v["gdp"], 4),
        "annual_accounts_check": y in annual}
       for y, v in sorted(years.items()) if v["quarters"] == 4]

# 2 and 3. Comex Stat, year by year
official = {int(r["CO_ANO"]): int(r["VL_FOB"]) for r in csv.DictReader(io.StringIO(fetch_bytes(TOTALS_URL).decode("latin-1")), delimiter=";")}
fat_of = {r["CO_NCM"]: r["CO_FAT_AGREG"] for r in csv.DictReader(io.StringIO(fetch_bytes(NCM_URL).decode("latin-1")), delimiter=";")}
fat_name = {r["CO_FAT_AGREG"]: r for r in csv.DictReader(io.StringIO(fetch_bytes(FAT_URL).decode("latin-1")), delimiter=";")}
KEYS = {"01": "basic", "02": "semi_manufactured", "03": "manufactured", "04": "special_transactions", "05": "ship_stores",
        "06": "re_export", "NA": "unclassified", None: "outside_ncm_table"}
LABEL = {"01": "Produtos básicos", "02": "Produtos semimanufaturados", "03": "Produtos manufaturados", "04": "Transações especiais",
         "05": "Consumo de bordo", "06": "Reexportação", "NA": "Sem fator agregado na tabela NCM", None: "NCM fora da tabela NCM"}
fat, unclassified = [], defaultdict(dict)
for y in range(Y0, Y1 + 1):
    agg = defaultdict(int)
    for r in comexstat({"flow": "export", "monthDetail": False, "period": {"from": f"{y}-01", "to": f"{y}-12"}, "filters": [],
                        "details": ["ncm"], "metrics": ["metricFOB"]}):
        f = fat_of.get(r["coNcm"])
        f = f if f in LABEL else None
        if CONTROL and y == 2010 and f == "01":
            continue
        agg[f] += int(r["metricFOB"])
        if f in ("NA", None):
            unclassified[y][r["coNcm"]] = unclassified[y].get(r["coNcm"], 0) + int(r["metricFOB"])
    if sum(agg.values()) != official[y]:
        fails.append(f"{y}: fator agregado groups US$ {sum(agg.values()):,} != official total US$ {official[y]:,}")
    t = sum(agg.values())
    fat.append({"year": y, "total_usd_fob": t, "groups": [{"key": KEYS[k], "code": k, "label": LABEL[k], "usd_fob": v, "share": round(v / t, 4)}
                                                       for k, v in sorted(agg.items(), key=lambda x: str(x[0]))]})
isic = defaultdict(dict)
for r in comexstat({"flow": "export", "monthDetail": False, "period": {"from": f"{Y0}-01", "to": f"{Y1}-12"}, "filters": [],
                    "details": ["ISICSection"], "metrics": ["metricFOB"]}):
    isic[int(r["year"])][no_dash(r["ISICSection"])] = int(r["metricFOB"])
for y in range(Y0, Y1 + 1):
    if sum(isic[y].values()) != official[y]:
        fails.append(f"{y}: ISIC sections US$ {sum(isic[y].values()):,} != official total US$ {official[y]:,}")

if fails:
    print("CHECK FAILED:\n- " + "\n- ".join(fails[:12]) + ("\n- ..." if len(fails) > 12 else "")); sys.exit(1)
if CONTROL:
    print("control run passed the checks: the identity check is not working"); sys.exit(2)

out = {
    "title": "Contexto: peso das exportações no PIB e tipo de produto exportado",
    "gdp_share": {"source": "IBGE, Contas Nacionais Trimestrais, SIDRA tabela 1846, valores a preços correntes (R$ milhões), soma dos 4 trimestres",
                  "url": SIDRA_Q, "annual_check_url": SIDRA_A,
                  "note": "Exportação e importação de bens e serviços, como nas contas nacionais (inclui serviços; não é o mesmo número do Comex Stat, que só mede bens).",
                  "annual_differences": annual_diff, "years": gdp},
    "value_added_factor": {"name": "fator agregado (classificação da Secex)", "source": "Comex Stat (MDIC/Secex), API por NCM e ano; classificação pela tabela oficial NCM.csv (coluna CO_FAT_AGREG)",
                       "urls": [NCM_URL, FAT_URL, TOTALS_URL],
                       "note": ("A Secex deixou de divulgar o fator agregado ao adotar a ISIC (Nota Metodológica ISIC, versão 1.1, fevereiro de 2020, "
                                "https://balanca.mdic.gov.br/balanca/metodologia/Nota_ISIC-CUCI.pdf). A partir de 2020 a divisão é calculada aqui com o código "
                                "que a tabela NCM oficial ainda traz, não é número publicado pela Secex. Semimanufaturados incluem, por exemplo, celulose, "
                                "açúcar bruto, ferro-ligas e semimanufaturados de aço."),
                       "years": fat,
                       "unclassified_ncm": {str(y): dict(sorted(v.items(), key=lambda x: -x[1])[:10]) for y, v in sorted(unclassified.items())}},
    "isic": {"source": "Comex Stat (MDIC/Secex), API details ISICSection, por ano; é a divisão que a Secex divulga hoje",
             "years": [{"year": y, "total_usd_fob": sum(isic[y].values()), "sections": [{"label": k, "usd_fob": v, "share": round(v / sum(isic[y].values()), 4)}
                        for k, v in sorted(isic[y].items(), key=lambda x: -x[1])]} for y in range(Y0, Y1 + 1)]},
    "check": {"identity": "em cada trimestre, consumo das famílias + consumo do governo + investimento + estoques + exportação - importação = PIB",
              "annual": "o PIB somado dos trimestres bate com o das contas anuais (SIDRA 6784) em todos os anos que ela tem: até R$ 3 milhões de arredondamento, ou 0,2% (2017 a 2019 diferem cerca de 0,1%; diferenças em annual_differences)",
              "official": "fator agregado e ISIC somam o total oficial de conferência do MDIC ao dólar em todos os anos",
              "control": "--control tira os produtos básicos de 2010; a checagem tem de falhar"},
}
size = write_json(OUT, out)
print(f"wrote {OUT.relative_to(ROOT)}: {size // 1024} KB; GDP years {gdp[0]['year']} to {gdp[-1]['year']}, annual check on {sorted(annual)[0]} to {sorted(annual)[-1]}")
for g in gdp[-6:]:
    print(g["year"], "exports/GDP", g["exports_share_of_gdp"], "imports/GDP", g["imports_share_of_gdp"])
for f in fat[::5] + [fat[-1]]:
    print(f["year"], {g["key"]: g["share"] for g in f["groups"]})
for y in (2000, 2010, 2020, 2025):
    print(y, {k: round(v / sum(isic[y].values()), 3) for k, v in isic[y].items()})
