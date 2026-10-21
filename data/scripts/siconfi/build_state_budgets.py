"""Top revenues and spending by function of each state government, 2024 (SICONFI, RREO 6th bimester).

Revenues: RREO Anexo 03 (Receita Corrente Liquida), column 'TOTAL (ULTIMOS 12 MESES)'.
Spending: RREO Anexo 02 (Despesa por Funcao/Subfuncao), column 'DESPESAS LIQUIDADAS ATE O BIMESTRE (d)',
excluding intra-budget spending. Invariant checked per state: sum of functions == declared total.
Run: python3 data/scripts/siconfi/build_state_budgets.py
"""
import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_DATA = ROOT / "data" / "state-budgets-2024.json"
OUT_PREVIEW = ROOT / "docs" / "superpowers" / "previews" / "assets" / "state-budgets.json"
YEAR = 2024
API = ("https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio={y}&nr_periodo=6"
       "&co_tipo_demonstrativo=RREO&co_esfera=E&id_ente={ente}&no_anexo={anexo}")
UF_CODES = {11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO", 21: "MA", 22: "PI", 23: "CE",
            24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA", 31: "MG", 32: "ES", 33: "RJ", 35: "SP",
            41: "PR", 42: "SC", 43: "RS", 50: "MS", 51: "MT", 52: "GO", 53: "DF"}
FUNCTIONS = ["Legislativa", "Judiciária", "Essencial à Justiça", "Administração", "Defesa Nacional",
             "Segurança Pública", "Relações Exteriores", "Assistência Social", "Previdência Social", "Saúde",
             "Trabalho", "Educação", "Cultura", "Direitos da Cidadania", "Urbanismo", "Habitação", "Saneamento",
             "Gestão Ambiental", "Ciência e Tecnologia", "Agricultura", "Organização Agrária",
             "Indústria", "Comércio e Serviços", "Comunicações", "Energia", "Transporte", "Desporto e Lazer",
             "Encargos Especiais"]
REVENUE_LINES = {"ICMS": "ICMS", "IPVA": "IPVA", "ITCD": "ITCD (heranças e doações)", "IRRF": "Imposto de renda retido na fonte",
                 "Cota-Parte do FPE": "Fundo de Participação dos Estados (União)",
                 "Transferências do FUNDEB": "Fundeb", "Outras Transferências Correntes": "Outras transferências",
                 "Transferências da LC nº 61/1989": "IPI exportação (União)",
                 "Contribuições": "Contribuições (previdência dos servidores)", "Receita Patrimonial": "Receita patrimonial",
                 "Receita de Serviços": "Receita de serviços", "Outras Receitas Correntes": "Outras receitas correntes",
                 "Outros Impostos, Taxas e Contribuições de Melhoria": "Outros impostos e taxas",
                 # Only the DF reports these (Brasília has no prefeitura, so the GDF charges the city taxes and receives the
                 # city fund); without them the DF lost about R$ 6 bi a year. The two small lines close every state to the cent.
                 "ISS": "ISS", "IPTU": "IPTU", "ITBI": "ITBI", "Cota-Parte do FPM": "Fundo de Participação dos Municípios (União)",
                 "Cota-Parte do ITR": "Cota-parte do ITR (União)", "Receita Agropecuária": "Receita agropecuária",
                 "Receita Industrial": "Receita industrial",
                 # New tax line in the 2026 template. Minas Gerais filed its 2026 1st-bimester income-tax line under this name
                 # (R$ 8,29 bi in 12 months, the IRRF of the next report); kept as filed, the monthly series reads the last report.
                 "IBS": "IBS"}
SPEND_COL = "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)"
REV_COL = "TOTAL (ÚLTIMOS 12 MESES)"


def fetch(ente, anexo):
    url = API.format(y=YEAR, ente=ente, anexo=anexo.replace(" ", "%20"))
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return url, json.load(r)["items"]
        except Exception:
            time.sleep(2 + attempt * 3)
    raise RuntimeError(f"failed {url}")


if "--control" in sys.argv:  # planted defect: drop one DF line; the revenue check must fail and nothing is written
    REVENUE_LINES.pop("ISS")
out, problems = {}, []
for code, uf in UF_CODES.items():
    url3, a3 = fetch(code, "RREO-Anexo 03")
    url2, a2 = fetch(code, "RREO-Anexo 02")
    rev = {i["conta"]: i["valor"] for i in a3 if i["coluna"] == REV_COL}
    revenue = sorted(({"label": label, "value": rev[k]} for k, label in REVENUE_LINES.items() if rev.get(k)),
                     key=lambda x: -x["value"])
    rows = [i for i in a2 if i["coluna"] == SPEND_COL and i["rotulo"] == "Total das Despesas Exceto Intra-Orçamentárias"]
    total = next((r["valor"] for r in rows if r["conta"].startswith("DESPESAS (EXCETO")), None)
    functions, current = [], None
    for r in rows[1:]:
        if r["conta"] in FUNCTIONS:
            current = {"label": r["conta"], "value": r["valor"], "sub": []}
            functions.append(current)
        elif current is not None and r["valor"]:
            label = r["conta"].split(" - ", 1)[1] if r["conta"].startswith("FU") and " - " in r["conta"] else r["conta"]
            current["sub"].append({"label": label, "value": r["valor"]})
    for f in functions:
        f["sub"].sort(key=lambda x: -x["value"])
    functions.sort(key=lambda x: -x["value"])
    fsum = sum(f["value"] for f in functions)
    if total is None or abs(fsum - total) > 1:
        problems.append(f"{uf}: functions {fsum:.2f} vs total {total}")
    rsum = sum(x["value"] for x in revenue)
    if abs((rev.get("RECEITAS CORRENTES (I)") or 0) - rsum) > 1:
        problems.append(f"{uf}: revenue lines {rsum:.2f} vs RECEITAS CORRENTES (I) {rev.get('RECEITAS CORRENTES (I)')}")
    out[uf] = {
        "year": YEAR,
        "revenue_current_total": rev.get("RECEITAS CORRENTES (I)"),
        "revenue_top": revenue,
        "to_municipalities": rev.get("Transferências Constitucionais e Legais"),
        "fundeb_deduction": rev.get("Dedução de Receita para Formação do FUNDEB"),
        "spending_total": total,
        "spending_by_function": functions,
        "sources": [{"field": "revenue", "url": url3}, {"field": "spending", "url": url2}],
        "collected_at": date.today().isoformat(),
    }
    print(uf, "ok", round((total or 0) / 1e9, 1), "bi")

if problems:  # nothing is written while a check fails
    raise SystemExit("problems: " + "; ".join(problems))
payload = json.dumps(out, ensure_ascii=False)
OUT_DATA.write_text(payload, encoding="utf-8")
OUT_PREVIEW.write_text(payload, encoding="utf-8")
print("problems: none")
