"""Seguro-desemprego (unemployment insurance) and abono salarial (wage bonus) of 2024 by the recipient's UF, read from
the Relatório de Gestão do FAT, exercício 2024.

Source: Ministério do Trabalho e Emprego, Relatório de Gestão do FAT, exercício 2024 (CODEFAT), page
"Relatório de Gestão do FAT" of the Portal do FAT:
  https://portalfat.trabalho.gov.br/transparencia-e-prestacao-de-contas/relatorios-de-gestao/relatorio-de-gestao-do-fat/
  PDF: https://portalfat.trabalho.gov.br/wp-content/uploads/2025/04/Relatorio-de-Gestao-do-FAT-2024.pdf
  Gráfico 13 (p. 42): "Distribuição de pagamentos do seguro-desemprego por UF e por Região do Brasil", R$ millions.
  Gráfico 14 (p. 43): "Distribuição de beneficiários por UF e Distribuição de pagamentos do abono salarial por Região
  do Brasil", R$ millions (the axis is in R$ millions, and paragraph 140 confirms it: SP with 24.3% of the payments).
  Source of both charts, as stated in the report itself: CGSAP/DGB/SPT/MTE.

Usage: python3 pipelines/ug/extract_fat_uf_hybrid.py
Reads the text of the chart labels (pdftotext), checks the sum by region against the pie totals of the same chart
and writes data/ug/mte-seguro-abono-uf-2024_hybrid.json (values in reais).
"""
import json, os, re, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
PDF = P("data/ug/rg_fat_2024_hybrid.pdf")
URL = "https://portalfat.trabalho.gov.br/wp-content/uploads/2025/04/Relatorio-de-Gestao-do-FAT-2024.pdf"
if not os.path.exists(PDF):
    subprocess.run(["curl", "-sS", "-L", "-m", "300", "-A", "Mozilla/5.0", "-o", PDF, URL], check=True)

NAME_UF = {"ACRE": "AC", "ALAGOAS": "AL", "AMAZONAS": "AM", "AMAPA": "AP", "BAHIA": "BA", "CEARA": "CE",
           "DISTRITO FEDERAL": "DF", "ESPIRITO SANTO": "ES", "GOIAS": "GO", "MARANHAO": "MA", "MINAS GERAIS": "MG",
           "MATO GROSSO DO SUL": "MS", "MATO GROSSO": "MT", "PARA": "PA", "PARAIBA": "PB", "PERNAMBUCO": "PE", "PIAUI": "PI",
           "PARANA": "PR", "RIO DE JANEIRO": "RJ", "RIO GRANDE DO NORTE": "RN", "RONDONIA": "RO", "RORAIMA": "RR",
           "RIO GRANDE DO SUL": "RS", "SANTA CATARINA": "SC", "SERGIPE": "SE", "SAO PAULO": "SP", "TOCANTINS": "TO"}
UFS = sorted(NAME_UF.values())
REGION = {"Norte": ["AC", "AM", "AP", "PA", "RO", "RR", "TO"], "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
          "Sudeste": ["ES", "MG", "RJ", "SP"], "Sul": ["PR", "RS", "SC"], "Centro-Oeste": ["DF", "GO", "MS", "MT"]}
# totals by region written on the pie of the same charts (R$ millions), only to check the reading of the labels
PIE = {"seguro_desemprego": {"Norte": 5132.3, "Nordeste": 11337.3, "Sudeste": 22351.1, "Sul": 8868.8, "Centro-Oeste": 4258.7, "unclassified": 6.1},
       "abono_salarial": {"Norte": 1667.5, "Nordeste": 6269.2, "Sudeste": 13001.9, "Sul": 4622.8, "Centro-Oeste": 2225.8, "unclassified": 348.4}}
num = lambda s: float(s.replace(".", "").replace(",", "."))
text = lambda page: subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-layout", PDF, "-"],
                                   capture_output=True, text=True, check=True).stdout

out = {"source": "Ministério do Trabalho e Emprego, Relatório de Gestão do FAT, exercício 2024 (Fonte: CGSAP/DGB/SPT/MTE)",
       "page_url": "https://portalfat.trabalho.gov.br/transparencia-e-prestacao-de-contas/relatorios-de-gestao/relatorio-de-gestao-do-fat/",
       "pdf_url": URL, "unit": "R$ (os rótulos do gráfico estão em R$ milhões com duas casas)", "series": {}}

# Gráfico 13, p. 42: state names written in full
sd, nc = {}, None
for line in text(42).splitlines():
    m = re.match(r"^\s*(N[ãa]o Classificado|[A-Z][A-Z ]+?)\s{2,}([\d.]+,\d{2})\b", line)
    if not m: continue
    k, v = m.group(1).strip(), num(m.group(2))
    if k.lower().startswith("n"): nc = v
    elif k in NAME_UF: sd[NAME_UF[k]] = v
if not (sorted(sd) == UFS and nc is not None):
    raise SystemExit((sorted(sd), nc))

# Gráfico 14, p. 43: state abbreviations; "UF IGNORADA" comes with its label 348 on a line of its own
ab, ign, t43 = {}, None, text(43).splitlines()
for i, line in enumerate(t43):
    m = re.match(r"^\s*([A-Z]{2})\s+([\d.]+,\d{2})\b", line)
    if m and m.group(1) in UFS: ab[m.group(1)] = num(m.group(2))
    if "UF IGNORADA" in line:
        for nxt in t43[i:i + 4]:
            n = re.search(r"\b(\d{3})\b\s*$", nxt.strip())
            if n: ign = float(n.group(1)); break
if not (sorted(ab) == UFS and ign is not None):
    raise SystemExit((sorted(ab), ign))

for key, vals, unk, figure in (("seguro_desemprego", sd, nc, "Gráfico 13, p. 42"), ("abono_salarial", ab, ign, "Gráfico 14, p. 43")):
    regions = {r: round(sum(vals[u] for u in us), 2) for r, us in REGION.items()}
    diff = {r: round(regions[r] - PIE[key][r], 2) for r in REGION}
    total = sum(vals.values()) + unk
    if key == "abono_salarial":
        if not (all(abs(d) <= 0.2 for d in diff.values())):
            raise SystemExit((key, diff))  # the pie rounds to one decimal place
        if not (abs(total - 28133.7) < 5):
            raise SystemExit(total)  # Quadro 12: R$ 28,133.7 million committed (empenhados)
        if not (all(abs(vals[u] / total * 100 - s) < 0.05 for u, s in {"SP": 24.3, "MG": 11.5, "RJ": 8.3, "PR": 6.2, "BA": 5.7}.items())):
            raise SystemExit("check failed: all((abs(vals[u] / total * 100 - s) < 0.05 for u, s in {'SP': 24.3, 'MG': 11.5, 'RJ': 8.3, 'PR': 6.2, 'BA': 5.7}.items()))")  # paragraph 140
    else:
        # for seguro-desemprego the pie by region does NOT match the sum of the UF bars (up to R$ 585 million apart per region),
        # although the totals match; the bars match the report's own text (paragraphs 133 to 135), which is checked here
        if not (abs(total - 52000) < 50):
            raise SystemExit(total)  # paragraph 133: R$ 52.0 billion
        if not (all(abs(vals[u] / total * 100 - s) < 0.05 for u, s in {"SP": 25.0, "MG": 10.2, "RJ": 6.1, "RS": 6.1}.items())):
            raise SystemExit("check failed: all((abs(vals[u] / total * 100 - s) < 0.05 for u, s in {'SP': 25.0, 'MG': 10.2, 'RJ': 6.1, 'RS': 6.1}.items()))")  # paragraph 134
        if not (abs(regions["Sudeste"] / total * 100 - 43.1) < 0.05):
            raise SystemExit("check failed: abs(regions['Sudeste'] / total * 100 - 43.1) < 0.05")  # paragraph 135: Sudeste R$ 22.4 billion, 43.1%
    out["series"][key] = {"figure": figure, "uf_millions": vals, "unclassified_millions": unk,
                          "uf": {u: round(vals[u] * 1e6, 2) for u in UFS}, "unclassified": round(unk * 1e6, 2),
                          "sum_27_ufs": round(sum(vals.values()) * 1e6, 2),
                          "regions_vs_pie_check_millions": {"sum_of_labels": regions, "pie": PIE[key], "difference": diff}}
out["notes"] = ["Seguro-desemprego: a soma das barras por UF não bate com a pizza por região do mesmo gráfico (Norte -350,0, Nordeste +584,7, Sul -381,6, Centro-Oeste +82,7, Sudeste +64,2, R$ milhões), embora o total bata; o texto do relatório confirma as barras (SP 25,0%, MG 10,2%, RJ 6,1%, RS 6,1%, Sudeste 43,1%) e diz Nordeste R$ 11,4 bi (21,8%), que é o valor da pizza. Usam-se as barras por UF, a única série por UF publicada.",
                "Seguro-desemprego: o rótulo da barra 'Não Classificado' diz 4,82 e a pizza do mesmo gráfico diz 6,1 (R$ milhões); usa-se o da barra, e a diferença fica no resíduo sem UF.",
                "Seguro-desemprego: todas as modalidades (formal, pescador artesanal, doméstico, bolsa qualificação, trabalhador resgatado); as duas parcelas adicionais do RS (MP 1.218/2024) estão no formal (Quadro 11).",
                "Os dois gráficos somam valores pagos aos trabalhadores no exercício, não a execução orçamentária do Portal; a diferença entre as duas fica sem UF no cálculo."]
json.dump(out, open(P("data/ug/mte-seguro-abono-uf-2024_hybrid.json"), "w"), ensure_ascii=False, indent=1)
for k, s in out["series"].items():
    print(k, "27 UFs R$ bi", round(s["sum_27_ufs"] / 1e9, 4), "não classificado R$ bi", round(s["unclassified"] / 1e9, 4),
          "DF R$ bi", round(s["uf"]["DF"] / 1e9, 4), "regiões contra pizza", s["regions_vs_pie_check_millions"]["difference"])
