"""Monthly lines of the Tesouro's RTN (Tabela 1.1) that the Union block of the map needs (D115), as one small JSON.

Usage: uv run python pipelines/ug/extract_rtn_lines.py [--control]   (needs openpyxl)
Input: pipelines/series/cache/union/serie_historica_ago26.xlsx, the same RTN file data/series/union.json is built from
       (https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326, published 2026-09-29). Nothing is downloaded.
Output: data/ug/rtn-lines-monthly.json, money in reais with cents (R$ milhões x 1.000.000, rounded to the cent, the same
        conversion as build_union_series.py).
Check, in whole cents: line 2 plus line 4 of this file equals transfers_to_subnationals plus primary_spending of
data/series/union.json in every month (the map's official total is the one "As contas do Brasil" shows). --control moves
one cent in one month after reading and must fail.
"""
import json, os, sys
from decimal import Decimal
import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
SRC = P("pipelines/series/cache/union/serie_historica_ago26.xlsx")
LINES = {  # key -> exact label prefix in Tabela 1.1
    "transfers_to_subnationals": "2. TRANSF. POR REPARTIÇÃO DE RECEITA",
    "primary_spending": "4. DESPESA TOTAL",
    "social_security_benefits": "4.1  Benefícios Previdenciários",
    "unemployment_insurance_and_wage_bonus": "4.3.01 Abono e Seguro Desemprego",
    "bpc": "4.3.05  Benefícios de Prestação Continuada da LOAS/RMV",
    "other_branches_operating_and_capital": "4.3.12  Legislativo/Judiciário/MPU/DPU (Custeio e Capital)",
    "court_ordered_operating_and_capital": "4.3.14  Sentenças Judiciais e Precatórios (Custeio e Capital)",
    "constitutional_funds": "2.2  Fundos Constitucionais",
}
wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
rows = list(wb["1.1"].iter_rows(values_only=True))
if not (str(rows[1][0]).startswith("Tabela 1.1.") and "R$ Milhões" in str(rows[2][0])):
    raise SystemExit("RTN Tabela 1.1 layout changed")
cols = {f"{d.year:04d}-{d.month:02d}": j for j, d in enumerate(rows[4]) if hasattr(d, "year") and d.year >= 2019}
months = sorted(cols)
cents = lambda x: None if x is None else int((Decimal(repr(x)) * 1000000 * 100).quantize(Decimal(1)))  # R$ milhões -> cents
out = {}
for key, prefix in LINES.items():
    hits = [r for r in rows if isinstance(r[0], str) and r[0].strip().startswith(prefix.strip()) and r[0].strip()[:len(prefix.strip())] == prefix.strip()]
    if not (len(hits) == 1):
        raise SystemExit((prefix, len(hits)))
    out[key] = [cents(hits[0][cols[m]]) for m in months]
if "--control" in sys.argv:
    out["primary_spending"][-1] += 1
U = json.load(open(P("data/series/union.json")))
ui = {m: i for i, m in enumerate(U["months"])}
c2 = lambda v: int(round(v * 100))
diff = {m: out["transfers_to_subnationals"][i] + out["primary_spending"][i] - c2(U["transfers_to_subnationals"][ui[m]]) - c2(U["primary_spending"][ui[m]])
        for i, m in enumerate(months) if m in ui and out["primary_spending"][i] is not None}
bad = {m: d for m, d in diff.items() if d != 0}
print("months", months[0], months[-1], "| months off union.json (cents):", bad or "none")
if bad:
    raise SystemExit("CHECK FAILED")
if "--control" not in sys.argv:
    R = lambda v: None if v is None else round(v / 100, 2)
    json.dump({"title": "RTN Tabela 1.1, monthly lines used by the Union block of the map (D115)",
               "source": {"file": "serie_historica_ago26.xlsx", "url": "https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326",
                          "page": "https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/8",
                          "published": "2026-09-29", "table": "1.1", "unit": "R$ milhões converted to reais"},
               "labels": LINES, "months": months, "lines": {k: [R(v) for v in a] for k, a in out.items()},
               "check": {"transfers_plus_primary_spending_equals_union_json_every_month": True}},
              open(P("data/ug/rtn-lines-monthly.json"), "w"), ensure_ascii=False, indent=1)
