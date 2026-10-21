"""Data of the page "Como o dinheiro anda", design round 1: how the tax money moves (D140), for 2025.

Inputs:
  data/ledger/ledger.duckdb        the Tesouro's RTN, every line by month (the ledger matches the RTN line by line, G5)
  data/series/state-budgets.json   the 27 state RREOs (Anexo 3 revenue by month; Anexo 2 spending by function, 6th bimester)
Rules: the sharing percentages of the Constitution, read on Planalto on 2026-10-21 (CF arts. 153, 155 to 159, 212-A; ADCT
art. 60), each with its article. The "follow R$ 100" splits are computed here from those percentages, never typed.
States' spending leaves out the "Transferências" subfunction of "Encargos Especiais": in some states it holds the share passed
to the municipalities, which the page already shows as its own flow.

Usage: .venv/bin/python -B docs/superpowers/tools/build-dinheiro-r1-data.py
Writes docs/superpowers/previews/assets/dinheiro-r1-data.js
"""
import json
from collections import defaultdict
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "superpowers" / "previews" / "assets" / "dinheiro-r1-data.js"
YEAR = 2025
CF = "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"
RTN = "https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/8"

# ---------- the União, from the ledger
LINES = ["1", "1.1", "1.3", "1.4", "2", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "3", "4", "4.1", "4.2", "4.3", "4.4", "5", "9", "10",
         "4.3.01", "4.3.05", "4.3.10", "4.3.14", "4.4.1.2", "4.4.1.3", "4.4.2.1", "4.4.1.4", "4.4.2.2"]
c = duckdb.connect(str(ROOT / "data" / "ledger" / "ledger.duckdb"), read_only=True)
rows = c.execute(f"""select line_key, any_value(label), sum(value_cents), count(*) from cur_line where dataset = 'tesouro.rtn.serie_historica'
                    and period between '{YEAR}-01-01' and '{YEAR}-12-01' and line_key in ({','.join("'" + k + "'" for k in LINES)}) group by 1""").fetchall()
union = {k: {"label": lab.strip(), "bi": round(cents / 1e11, 1)} for k, lab, cents, n in rows}
assert all(n == 12 for *_, n in rows) and len(union) == len(LINES), "a line is missing months"

# ---------- the 27 states, from their RREOs
sb = json.loads((ROOT / "data" / "series" / "state-budgets.json").read_text())
REV = {"icms": "ICMS", "ipva": "IPVA", "itcmd": "ITCD", "fpe": "Cota-Parte do FPE", "ipi_exp": "Transferências da LC nº 61/1989",
       "to_municipalities": "Transferências Constitucionais e Legais", "fundeb_out": "Dedução de Receita para Formação do FUNDEB", "fundeb_in": "Transferências do FUNDEB"}
states = {k: 0.0 for k in REV}
fn, transfers_in_spending = defaultdict(float), 0.0
for uf, x in sb["uf"].items():
    rm = x["revenue_monthly"]; idx = [i for i, m in enumerate(rm["months"]) if m.startswith(f"{YEAR}-")]
    assert len(idx) == 12, uf
    for k, line in REV.items():
        v = rm["lines"].get(line)
        if v is None:
            assert uf == "DF" and k == "to_municipalities", (uf, k)  # the DF has no municipalities
            continue
        states[k] += sum(v[i] or 0 for i in idx)
    for it in x["periods"][f"{YEAR}-B6"]["spending_by_function"]:
        if it["label"] == "Encargos Especiais":
            t = sum(s["value"] for s in it.get("sub", []) if s["label"] == "Transferências")
            transfers_in_spending += t; fn[it["label"]] += it["value"] - t
        else:
            fn[it["label"]] += it["value"]
states = {k: round(v / 1e9, 1) for k, v in states.items()}
spending = sorted(((k, round(v / 1e9, 1)) for k, v in fn.items()), key=lambda kv: -kv[1])

# ---------- the rules, and what R$ 100 of each tax becomes under them (CF, Planalto, 2026-10-21)
# Fundeb (CF art. 212-A, II; Lei 14.113/2020 art. 3, read on Planalto 2026-10-21): 20% of the FPE (art. 159, I, a), of the FPM's
# 22,5% only (art. 159, I, b; the 1% parcels of July, September and December, alíneas d to f, stay out), of the IPI-exportação
# (art. 159, II), of ICMS, IPVA and ITCMD with the municipalities' shares, and of the municipalities' ITR. CIDE, ISS, IPTU and
# ITBI stay out.
FPE, FPM, FPM_MONTHLY, REGIONAL, IPI_EXP, CIDE_STATES, FUNDEB = 21.5, 25.5, 22.5, 3.0, 10.0, 29.0, 20.0
MUNI_ICMS, MUNI_IPVA, MUNI_OF_STATE_SHARE = 25.0, 50.0, 25.0


def split(parts):
    """parts: [(destination, pct of the tax, pct of the tax that pays 20% into the state's education fund)]."""
    out, fund = [], 0.0
    for dest, pct, base in parts:
        f = round(base * FUNDEB / 100, 4); fund += f
        out.append([dest, round(pct - f, 4)])
    if fund:
        out.append(["fundeb", round(fund, 4)])
    assert abs(sum(p for _, p in out) - 100) < 0.001, parts
    return out


TAXES = [
    {"id": "ir", "label": "Imposto de renda", "collector": "uniao", "art": "CF arts. 153, III, e 159, I",
     "note": "O imposto de renda retido no salário de quem trabalha para o estado ou a prefeitura fica com eles (CF arts. 157, I, e 158, I).",
     "split": split([["uniao", 100 - FPE - FPM - REGIONAL, 0], ["estados", FPE, FPE], ["prefeituras", FPM, FPM_MONTHLY], ["regional", REGIONAL, 0]])},
    {"id": "ipi", "label": "IPI", "collector": "uniao", "art": "CF arts. 153, IV, e 159, I e II",
     "note": "O IPI-exportação (10%) vai aos estados pela exportação de cada um; cada estado passa 25% dele às prefeituras.",
     "split": split([["uniao", 100 - FPE - FPM - REGIONAL - IPI_EXP, 0], ["estados", FPE + IPI_EXP * 0.75, FPE + IPI_EXP * 0.75],
                      ["prefeituras", FPM + IPI_EXP * 0.25, FPM_MONTHLY + IPI_EXP * 0.25], ["regional", REGIONAL, 0]])},
    {"id": "inss", "label": "INSS, Cofins, PIS e CSLL", "collector": "uniao", "art": "CF art. 195",
     "note": "Contribuições da seguridade social: pagam a previdência, a saúde e a assistência, e não são repartidas.", "split": split([["uniao", 100, 0]])},
    {"id": "icms", "label": "ICMS", "collector": "estados", "art": "CF arts. 155, II, e 158, IV",
     "note": "Das prefeituras, pelo menos 65% vão pelo valor adicionado em cada município e até 35% por lei estadual.",
     "split": split([["estados", 100 - MUNI_ICMS, 100 - MUNI_ICMS], ["prefeituras", MUNI_ICMS, MUNI_ICMS]])},
    {"id": "ipva", "label": "IPVA", "collector": "estados", "art": "CF arts. 155, III, e 158, III",
     "note": "Metade fica com a prefeitura do município onde o veículo está registrado.",
     "split": split([["estados", 100 - MUNI_IPVA, 100 - MUNI_IPVA], ["prefeituras", MUNI_IPVA, MUNI_IPVA]])},
    {"id": "itcmd", "label": "ITCMD (heranças e doações)", "collector": "estados", "art": "CF art. 155, I", "note": "",
     "split": split([["estados", 100, 100]])},
    {"id": "iss", "label": "ISS, IPTU e ITBI", "collector": "prefeituras", "art": "CF art. 156",
     "note": "Impostos da prefeitura, que não entram no fundo da educação.", "split": split([["prefeituras", 100, 0]])},
    {"id": "cide", "label": "CIDE-combustíveis", "collector": "uniao", "art": "CF art. 159, III, e § 4º",
     "note": "Cada estado passa 25% da sua parte às prefeituras.",
     "split": split([["uniao", 100 - CIDE_STATES, 0], ["estados", CIDE_STATES * (100 - MUNI_OF_STATE_SHARE) / 100, 0], ["prefeituras", CIDE_STATES * MUNI_OF_STATE_SHARE / 100, 0]])},
]
RULES = [
    {"from": "União", "to": "estados e DF", "what": "FPE", "pct": "21,5% do IR e do IPI", "art": "CF art. 159, I, a"},
    {"from": "União", "to": "prefeituras", "what": "FPM", "pct": "25,5% do IR e do IPI (22,5% por mês e 1% em julho, setembro e dezembro)", "art": "CF art. 159, I, b, d, e, f"},
    {"from": "União", "to": "bancos do Norte, Nordeste e Centro-Oeste", "what": "fundos regionais (FNO, FNE, FCO)", "pct": "3% do IR e do IPI", "art": "CF art. 159, I, c"},
    {"from": "União", "to": "estados e DF", "what": "IPI-exportação", "pct": "10% do IPI, pela exportação de cada estado", "art": "CF art. 159, II"},
    {"from": "União", "to": "estados e DF", "what": "CIDE-combustíveis", "pct": "29%", "art": "CF art. 159, III"},
    {"from": "União", "to": "prefeituras", "what": "ITR", "pct": "50% (100% se a prefeitura cobra)", "art": "CF art. 158, II"},
    {"from": "estados", "to": "prefeituras", "what": "ICMS", "pct": "25%", "art": "CF art. 158, IV"},
    {"from": "estados", "to": "prefeituras", "what": "IPVA", "pct": "50%", "art": "CF art. 158, III"},
    {"from": "estados e prefeituras", "to": "fundo da educação do estado (Fundeb)", "what": "Fundeb", "pct": "20% de ICMS, IPVA e ITCMD (com as partes das prefeituras), do FPE, dos 22,5% mensais do FPM, do IPI-exportação e do ITR das prefeituras; volta pelo número de alunos; a União completa com no mínimo 23% em 2026", "art": "CF art. 212-A; Lei 14.113/2020, art. 3; ADCT art. 60"},
]
# the page prints the route of each rule and the states' spending functions as phrases a reader understands
ROUTE = {"União": "da União", "estados": "dos estados", "estados e prefeituras": "dos estados e das prefeituras", "estados e DF": "aos estados e ao DF",
         "prefeituras": "às prefeituras", "bancos do Norte, Nordeste e Centro-Oeste": "aos bancos do Norte, Nordeste e Centro-Oeste",
         "fundo da educação do estado (Fundeb)": "ao fundo da educação do estado (Fundeb)"}
for r in RULES:
    r["route"] = f"{ROUTE[r['from']]} {ROUTE[r['to']]}"
    r["what"] = r["what"][0].upper() + r["what"][1:]
FUNCTION_NAME = {"Encargos Especiais": "Dívida e outros encargos", "Previdência Social": "Previdência dos servidores", "Judiciária": "Justiça (Judiciário)",
                 "Essencial à Justiça": "Ministério Público e Defensoria", "Legislativa": "Assembleia Legislativa e Tribunal de Contas"}
spending = [(FUNCTION_NAME.get(k, k), v) for k, v in spending]
PHRASE = {"ir": "imposto de renda", "inss": "INSS, Cofins, PIS ou CSLL", "itcmd": "ITCMD (herança ou doação)", "iss": "ISS, IPTU ou ITBI"}
for x in TAXES:
    x["phrase"] = PHRASE.get(x["id"], x["label"])
out = {"year": YEAR, "union": union, "states": states, "states_spending": spending, "states_spending_total": round(sum(fn.values()) / 1e9, 1),
       "states_transfers_in_spending": round(transfers_in_spending / 1e9, 1), "taxes": TAXES, "rules": RULES,
       "minimums": [{"what": "Educação", "rule": "União 18%; estados, DF e prefeituras 25% da receita de impostos, com a recebida por repartição", "art": "CF art. 212"},
                    {"what": "Saúde", "rule": "União 15% da receita corrente líquida; estados e prefeituras pelos percentuais da lei complementar", "art": "CF art. 198, § 2º"}],
       "sources": [{"name": "Constituição Federal, lida no Planalto em 2026-10-21", "url": CF}, {"name": "Tesouro Nacional, Resultado do Tesouro Nacional (RTN), 2025", "url": RTN},
                   {"name": "RREO dos 27 estados, 2025 (SICONFI)", "url": "https://siconfi.tesouro.gov.br/"}]}
OUT.write_text("window.BIM = " + json.dumps(out, ensure_ascii=False) + ";\n", encoding="utf-8")
print("union lines", len(union), "| states", states, "| states spending", out["states_spending_total"], "| transfers left out", out["states_transfers_in_spending"])
print("R$ 100 of IR:", TAXES[0]["split"], "| IPI:", TAXES[1]["split"])
