"""Union (Governo Central) monthly series, 2019-01 to the latest published month -> data/series/union.json

Fiscal flows: Tesouro Nacional, Resultado do Tesouro Nacional (RTN), Serie Historica, Tabela 1.1 (R$ milhoes,
valores correntes). Gross debt: Banco Central, SGS series 13761 (R$ milhoes) and 13762 (% do PIB), both
"Divida bruta do governo geral, metodologia utilizada a partir de 2008" (names verified with the SGS web service).
All money values are converted from R$ milhoes to R$ (x 1,000,000); percentages are kept as published.
Needs openpyxl.  Run: python3 pipelines/series/build_union_series.py
"""
import json
import urllib.request
from datetime import date
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path(__file__).resolve().parent / "cache" / "union"
OUT = ROOT / "data" / "series" / "union.json"
FIRST = (2019, 1)
RTN_PAGE = "https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/8"
RTN_URL = "https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326"  # serie_historica_ago26.xlsx, published 2026-09-29
RTN_FILE = "serie_historica_ago26.xlsx"
SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial=01/12/2018&dataFinal=31/12/2026"
SGS_NAMES = {13761: "Dívida bruta do governo geral - Saldos em R$ milhões - Metodologia utilizada a partir de 2008",
             13762: "Dívida bruta do governo geral (% PIB) - Metodologia utilizada a partir de 2008"}
RTN_ROWS = {  # output key -> label prefix of the row in Tabela 1.1
    "revenue": "1. RECEITA TOTAL",
    "transfers_to_subnationals": "2. TRANSF. POR REPARTIÇÃO DE RECEITA",
    "revenue_net": "3. RECEITA LÍQUIDA",
    "primary_spending": "4. DESPESA TOTAL",
    "primary_result": "5. RESULTADO PRIMÁRIO GOVERNO CENTRAL - ACIMA DA LINHA",
    "primary_result_below_line": "8. RESULTADO PRIMÁRIO DO GOVERNO CENTRAL - ABAIXO DA LINHA",
    "nominal_interest": "9. JUROS NOMINAIS",
    "nominal_result": "10. RESULTADO NOMINAL DO GOVERNO CENTRAL",
}


def download(url, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=180) as r:
            path.write_bytes(r.read())
    return path


def month_key(d):
    return f"{d.year:04d}-{d.month:02d}"


def rtn_series():
    wb = openpyxl.load_workbook(download(RTN_URL, CACHE / RTN_FILE), read_only=True, data_only=True)
    rows = list(wb["1.1"].iter_rows(values_only=True))
    if not str(rows[1][0]).startswith("Tabela 1.1.") or "R$ Milhões" not in str(rows[2][0]):
        raise ValueError("RTN Tabela 1.1 layout changed")
    header = rows[4]
    cols = {month_key(d): j for j, d in enumerate(header) if hasattr(d, "year") and (d.year, d.month) >= FIRST}
    found = {}
    for key, prefix in RTN_ROWS.items():
        hits = [r for r in rows if isinstance(r[0], str) and r[0].strip().startswith(prefix)]
        if len(hits) != 1:
            raise ValueError(f"row {prefix!r} found {len(hits)} times")
        found[key] = {m: (None if hits[0][j] is None else round(hits[0][j] * 1e6, 2)) for m, j in cols.items()}
    return found, sorted(cols)


def sgs(code):
    raw = download(SGS.format(code=code), CACHE / f"sgs-{code}-from-2018-12.json")
    out = {}
    for item in json.loads(raw.read_text(encoding="utf-8")):
        d, m, y = item["data"].split("/")
        out[f"{y}-{m}"] = float(item["valor"])
    return out


def main():
    rtn, rtn_months = rtn_series()
    debt_brl, debt_pct = sgs(13761), sgs(13762)
    last = max(rtn_months[-1], max(debt_brl), max(debt_pct))
    months, (y, m) = [], FIRST
    while f"{y:04d}-{m:02d}" <= last:
        months.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    payload = {"months": months}
    for key in RTN_ROWS:
        payload[key] = [rtn[key].get(mk) for mk in months]
    payload["gross_debt_brl"] = [round(debt_brl[mk] * 1e6, 2) if mk in debt_brl else None for mk in months]
    payload["gross_debt_pct_gdp"] = [debt_pct.get(mk) for mk in months]
    payload["baseline"] = {"month": "2018-12", "gross_debt_brl": round(debt_brl["2018-12"] * 1e6, 2),
                           "gross_debt_pct_gdp": debt_pct["2018-12"],
                           "note": "saldo de dezembro de 2018, ponto de partida do mandato 2019 a 2022 (mesmas séries do SGS)"}
    payload["unit"] = "BRL (reais correntes); gross_debt_pct_gdp em % do PIB"
    payload["sign"] = "resultado positivo = sobrou dinheiro (superávit); negativo = faltou (déficit)"
    payload["aggregation"] = {k: "sum" for k in RTN_ROWS} | {"gross_debt_brl": "end_of_period",
                                                             "gross_debt_pct_gdp": "end_of_period"}
    payload["latest"] = {k: next((mk for mk, v in zip(reversed(months), reversed(payload[k])) if v is not None), None)
                         for k in list(RTN_ROWS) + ["gross_debt_brl", "gross_debt_pct_gdp"]}
    payload["nulls"] = {k: [mk for mk, v in zip(months, payload[k]) if v is None]
                        for k in list(RTN_ROWS) + ["gross_debt_brl", "gross_debt_pct_gdp"]}
    payload["null_reason"] = "mês ainda não publicado pela fonte na data da coleta"
    payload["sources"] = [
        {"fields": ["revenue", "transfers_to_subnationals", "revenue_net", "primary_spending", "primary_result"],
         "source": "Tesouro Nacional, Resultado do Tesouro Nacional (RTN), Série Histórica, Tabela 1.1, linhas 1, 2, 3, 4 e 5 "
                   "(resultado primário do Governo Central acima da linha), R$ milhões correntes convertidos para R$",
         "url": RTN_URL, "page": RTN_PAGE, "file": RTN_FILE, "published": "2026-09-29"},
        {"fields": ["primary_result_below_line", "nominal_interest", "nominal_result"],
         "source": "Mesma Tabela 1.1, linhas 8, 9 e 10: apuração abaixo da linha do Banco Central, reproduzida pelo Tesouro "
                   "(o resultado nominal não considera desvalorização cambial, nota 8/ da tabela)",
         "url": RTN_URL, "page": RTN_PAGE, "file": RTN_FILE, "published": "2026-09-29"},
        {"fields": ["gross_debt_brl"], "source": f"Banco Central do Brasil, SGS 13761: {SGS_NAMES[13761]}",
         "url": SGS.format(code=13761)},
        {"fields": ["gross_debt_pct_gdp"], "source": f"Banco Central do Brasil, SGS 13762: {SGS_NAMES[13762]}",
         "url": SGS.format(code=13762)},
    ]
    payload["scope_note"] = ("Governo Central = Tesouro Nacional, Previdência Social (RGPS) e Banco Central. A dívida bruta é do "
                             "Governo Geral (União, estados e municípios, sem Banco Central e estatais), o conceito usado nas "
                             "comparações oficiais.")
    payload["collected_at"] = date.today().isoformat()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print("months", months[0], "to", months[-1], "| latest", payload["latest"])


if __name__ == "__main__":
    main()
