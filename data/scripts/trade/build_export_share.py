"""Share of national production that is exported, for the goods the owner named -> data/trade/export-share-of-production.json.

Each item pairs a production figure and an export figure in the same unit and the same period, both from official sources:
- Conab supply and demand balances (soy grain, soy meal, soy oil, corn, cotton lint; beef, pork and chicken in carcass weight),
  where Conab already puts production and exports side by side; Conab sugarcane survey for sugar.
- IBGE: Produção Agrícola Municipal (PAM, SIDRA 5457), Produção da Extração Vegetal e da Silvicultura (PEVS, SIDRA 289), Pesquisa
  Trimestral do Abate (SIDRA 1092, 1093, 1094), Pesquisa Industrial Anual - Produto (SIDRA 10476).
- ANP: national oil production and oil exports (open data, m3). ANM: Anuário Mineral Brasileiro 2025 (base year 2024) and Sumário
  Mineral 2025, read from the PDFs (pdftotext) to confirm the pinned numbers.
- Comex Stat API (MDIC/Secex) for every export figure not taken from a balance, and to check the balances' export figures.
Where production is not officially measured in a unit comparable to exports, share is null and the reason is written.
Checks (nothing is written unless they pass): Conab's export figure equals Comex Stat for the same months within 0,5% (soy grain,
meal and oil, cotton, corn); ANP's 2025 oil export receipts equal Comex Stat NCM 27090010 to the dollar; the IBGE slaughter
quarters are complete; the ANM numbers pinned below are found in the ANM PDFs (skipped with a warning if pdftotext is missing);
every share is between 0 and 1. --control reads soy exports one year early; the Conab check must fail.
Run: python3 data/scripts/trade/build_export_share.py [--control]
"""
import csv, io, json, os, shutil, subprocess, sys, tempfile
from collections import defaultdict
from trade_common import ROOT, comexstat, fetch_bytes, months, no_dash, read_ods, read_xlsx, write_json

OUT = ROOT / "data" / "trade" / "export-share-of-production.json"
CONTROL = "--control" in sys.argv
CONAB_QOD = "https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/analises-do-mercado-agropecuario-e-extrativista/analises-de-mercado/quadro-de-oferta-e-demanda"
CONAB_GRAINS = CONAB_QOD + "/graos/quadro-de-oferta-e-demanda-de-graos-2026/quadro-de-oferta-e-demanda-graos-setembro-2026.xlsx"  # an .ods file
CONAB_MEATS = CONAB_QOD + "/carnes/oferta-e-demanda-de-carnes-2026-1/quadro_suprimentos_abr_2026.xlsx"
CONAB_CANE = ("https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cana-de-acucar/arquivos-boletins/"
              "4o-levantamento-safra-2025-26/site_previsao_de_safra-cana-de-acucar-abr-2026.xlsx")
ANP_PROD = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/ppgn-el/producao-petroleo-m3.csv"
ANP_TRADE = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/ie/petroleo/importacoes-exportacoes-petroleo-2000-2025.csv"
ANM_AMB = "https://www.gov.br/anm/pt-br/assuntos/economia-mineral/publicacoes/anuario-mineral/anuario-mineral-brasileiro/amb_metalicos__rev_2.pdf"
ANM_SUM = "https://www.gov.br/anm/pt-br/assuntos/economia-mineral/publicacoes/sumario-mineral/sumario-mineral-brasileiro-2025/sumario-2025.pdf"
SIDRA = "https://apisidra.ibge.gov.br/values"
# Pinned from the ANM PDFs (confirmed below when pdftotext exists): iron ore "produção beneficiada" 2024, table 3.1 of the AMB 2025;
# rare earths reserves (contained) from the Sumário Mineral 2025, which gives no production number for 2024 ("foi pequena").
ANM_IRON_2024_T = 448_624_077
ANM_IRON_ROW = "Ferro                   523.008.465 282.506.831 t   54,02     %    Fe     448.624.077 t"
ANM_RE_TEXT = ("produção beneficiada de concentrado de terras raras foi pequena", "Brasil (11,4 Mt")
fails, warnings = [], []


def sidra(path):
    return json.loads(fetch_bytes(f"{SIDRA}/{path}"))[1:]


def exp(filt, values, ym0, ym1, flow="export"):
    """US$ FOB and kg of a Comex Stat filter between two months, inclusive. The API reads a period as a grid, the years from..to
    times the months from..to: 2024-02 to 2025-03 returns only February and March of each year, and 2025-02 to 2026-01 returns
    nothing. So a period that crosses a year is asked one calendar year at a time."""
    usd = kg = 0
    for y in range(int(ym0[:4]), int(ym1[:4]) + 1):
        a = ym0 if y == int(ym0[:4]) else f"{y}-01"
        b = ym1 if y == int(ym1[:4]) else f"{y}-12"
        r = comexstat({"flow": flow, "monthDetail": True, "period": {"from": a, "to": b}, "filters": [{"filter": filt, "values": values}],
                       "details": [], "metrics": ["metricFOB", "metricKG"]})
        want = set(months(y, int(a[5:]), y, int(b[5:])))
        got = {f"{x['year']}-{x['monthNumber']}" for x in r}
        if got - want:
            fails.append(f"Comex Stat {values} {a} to {b}: months outside the period {sorted(got - want)}")
        usd += sum(int(x["metricFOB"]) for x in r); kg += sum(int(x["metricKG"]) for x in r)
    return usd, kg


def kt(kg):
    return round(kg / 1e6, 3)


def near(a, b, tol=0.005):
    return abs(a / b - 1) <= tol


# Conab grains (ODS despite the .xlsx name)
grains = read_ods(fetch_bytes(CONAB_GRAINS))
soy_rows = grains["Suprimento_-_Soja"]
hdr = next(r for r in soy_rows if len(r) > 2 and r[1] == "2020/21")
col = hdr.index("2024/25")
block, soy = None, {}
for r in soy_rows:
    if r and isinstance(r[0], str):
        if r[0].startswith("1. Soja"): block = "grain"
        elif r[0].startswith("2. Farelo"): block = "meal"
        elif r[0].startswith("3. Óleo"): block = "oil"
        elif block and len(r) > col and ("Produção" in r[0] or "Exportação" in r[0]):
            soy[(block, "production" if "Produção" in r[0] else "exports")] = r[col]
sup = grains["Suprimento"]
bal, prod_name = {}, None
for r in sup:
    if r and r[0]:
        prod_name = str(r[0]).strip()
    if len(r) > 9 and r[1] == "2024/25" and prod_name in ("ALGODÃO", "MILHO"):
        bal[prod_name] = {"production": r[4], "exports": r[8]}
conab_note = next((r[0] for r in soy_rows if r and isinstance(r[0], str) and r[0].startswith("Nota")), "")

# Conab meats
meats = read_xlsx(fetch_bytes(CONAB_MEATS), "quadro_Suprimentos")
meat, section, years = {}, None, None
for r in meats:
    if not r or r[0] is None:
        continue
    s = str(r[0])
    if s.startswith(("1-", "2 -", "3 -", "4 -")):
        section = {"1": "chicken", "2": "beef", "3": "pork", "4": "total"}[s[0]]
    elif s == "ANO":
        years = [str(int(x)) if isinstance(x, float) else str(x) for x in r]
    elif section in ("chicken", "beef", "pork") and s.startswith(("PRODUÇÃO", "EXPORTAÇÃO")) and years and "2025" in years:
        meat[(section, "production" if s.startswith("PRODUÇÃO") else "exports")] = (r[years.index("2025")], s)
meat_tail = " ".join(str(r[0]) for r in meats if r and isinstance(r[0], str) and ("Fonte" in r[0] or "Nota" in r[0] or "ELAB" in r[0]))

# Conab sugarcane: sugar production by season
cane = read_xlsx(fetch_bytes(CONAB_CANE), "Produção de açúcar")
sugar_row = next(r for r in cane if r and r[0] == "BRASIL")
sugar = {"2024/25": sugar_row[1], "2025/26": sugar_row[3]}

# IBGE
pam = {(r["D4N"]): int(r["V"]) for r in sidra("t/5457/n1/all/v/214/p/2025/c782/40124,40122,40139,40136,40151,40099,45982")}
pevs = {(r["D4N"]): int(r["V"]) for r in sidra("t/289/n1/all/v/144/p/2025/c193/3403,3405,3435")}
abate = {}
for name, path in (("beef", "t/1092/n1/all/v/285/p/202501-202504/c12716/115236/c18/992/c12529/118225"),
                   ("pork", "t/1093/n1/all/v/285/p/202501-202504/c12716/115236/c12529/118225"),
                   ("chicken", "t/1094/n1/all/v/285/p/202501-202504/c12716/115236/c12529/118225")):
    rows = sidra(path)
    if len(rows) != 4:
        fails.append(f"IBGE slaughter {name}: {len(rows)} quarters of 2025")
    abate[name] = sum(int(r["V"]) for r in rows)
pia = {r["D4N"]: r["V"] for r in sidra("t/10476/n1/all/v/214/p/2024/c1264/52992")}

# ANP
def anp_rows(url):
    return list(csv.reader(io.StringIO(fetch_bytes(url).decode("utf-8-sig")), delimiter=";"))[1:]
num = lambda s: float(s.replace(",", ".")) if s else 0.0
anp_prod = sum(num(r[-1]) for r in anp_rows(ANP_PROD) if r[0] == "2025")
anp_trade = [r for r in anp_rows(ANP_TRADE) if r[0] == "2025" and r[3].startswith("EXPORT")]
anp_exp_m3, anp_exp_usd = sum(num(r[4]) for r in anp_trade), sum(num(r[5]) for r in anp_trade)
if len(anp_trade) != 12:
    fails.append(f"ANP 2025 oil exports: {len(anp_trade)} months")

# ANM PDFs: confirm the pinned numbers
if shutil.which("pdftotext"):
    with tempfile.TemporaryDirectory() as tmp:
        for url, needles in ((ANM_AMB, [ANM_IRON_ROW]), (ANM_SUM, list(ANM_RE_TEXT))):
            p = os.path.join(tmp, "f.pdf")
            open(p, "wb").write(fetch_bytes(url))
            txt = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout
            for n in needles:
                if n not in txt:
                    fails.append(f"ANM PDF {url.rsplit('/', 1)[1]}: '{n[:60]}' not found")
            os.remove(p)
else:
    warnings.append("pdftotext not found: the ANM numbers were not re-read from the PDFs")

# Comex Stat
y25 = ("2025-01", "2025-12")
soy_y = ("2024-01", "2024-12") if CONTROL else y25
c = {
    "soy_grain": exp("heading", ["1201"], *soy_y), "soy_meal": exp("heading", ["2304"], *y25), "soy_oil": exp("heading", ["1507"], *y25),
    "corn_conab": exp("heading", ["1005"], "2025-02", "2026-01"), "corn_2025": exp("heading", ["1005"], *y25),
    "cotton": exp("heading", ["5201"], *y25), "coffee": exp("heading", ["0901"], *y25),
    "sugar_2526": exp("heading", ["1701"], "2025-04", "2026-03"), "sugar_2425": exp("heading", ["1701"], "2024-04", "2025-03"),
    "beef": exp("heading", ["0201", "0202"], *y25), "pork": exp("heading", ["0203"], *y25),
    "chicken": exp("subHeading", ["020711", "020712", "020713", "020714"], *y25),
    "banana": exp("heading", ["0803"], *y25), "orange_fresh": exp("subHeading", ["080510"], *y25),
    "orange_juice": exp("subHeading", ["200911", "200912", "200919"], *y25),
    "iron_2024": exp("heading", ["2601"], "2024-01", "2024-12"), "pulp_2024": exp("heading", ["4703"], "2024-01", "2024-12"),
    "crude_ncm": exp("ncm", ["27090010"], *y25),
    "rare_earths": exp("ncm", ["25309030", "28053010", "28053090", "28461010", "28461090", "28469010", "28469020", "28469090"], *y25),
    "acai": exp("ncm", ["20079921"], *y25),
    "brazil_nut_shell": exp("ncm", ["08012100"], *y25), "brazil_nut_shelled": exp("ncm", ["08012200"], *y25),
    "brazil_nut_imports": exp("ncm", ["08012100", "08012200"], *y25, flow="import"),
    "tropical_wood": exp("subHeading", ["440721", "440722", "440725", "440726", "440727", "440728", "440729", "440922", "441231"], *y25),
}

# Cross-checks: Conab export figures against Comex Stat for the same months
for name, conab_kt, kg in (("soy grain", soy[("grain", "exports")], c["soy_grain"][1]), ("soy meal", soy[("meal", "exports")], c["soy_meal"][1]),
                           ("soy oil", soy[("oil", "exports")], c["soy_oil"][1]), ("cotton", bal["ALGODÃO"]["exports"], c["cotton"][1]),
                           ("corn", bal["MILHO"]["exports"], c["corn_conab"][1])):
    if not near(conab_kt, kg / 1e6):
        fails.append(f"Conab {name} exports {conab_kt:,.1f} kt != Comex Stat {kg / 1e6:,.1f} kt for the same months")
if round(anp_exp_usd) != c["crude_ncm"][0]:
    fails.append(f"ANP 2025 oil export receipts US$ {anp_exp_usd:,.0f} != Comex Stat NCM 27090010 US$ {c['crude_ncm'][0]:,}")


def item(key, name, share, production, exports, note, extra=None):
    if share is not None and not 0 <= share <= 1:
        fails.append(f"{key}: share {share} outside 0 to 1")
    e = {"key": key, "name": name, "share_exported": None if share is None else round(share, 4), "production": production, "exports": exports, "note": no_dash(note)}
    if extra:
        e.update(extra)
    return e


CONAB_G = f"Conab, Quadro de oferta e demanda de grãos (estimativa de setembro de 2026), {CONAB_GRAINS}"
CONAB_M = f"Conab, Quadro de suprimento de carnes (abril de 2026), {CONAB_MEATS}"
COMEX = "Comex Stat, MDIC/Secex (API https://api-comexstat.mdic.gov.br/general)"
PAM = "IBGE, Produção Agrícola Municipal 2025, SIDRA tabela 5457 (quantidade produzida)"
PEVS = "IBGE, Produção da Extração Vegetal e da Silvicultura 2025, SIDRA tabela 289"
ABATE = "IBGE, Pesquisa Trimestral do Abate de Animais, 2025 (soma dos 4 trimestres, peso total das carcaças, estabelecimentos sob inspeção federal, estadual ou municipal), SIDRA tabelas 1092, 1093 e 1094"
items = [
    item("soy_grain", "Soja em grão", soy[("grain", "exports")] / soy[("grain", "production")],
         {"value": soy[("grain", "production")], "unit": "mil t", "period": "safra 2024/25", "source": CONAB_G},
         {"value": soy[("grain", "exports")], "unit": "mil t", "period": "janeiro a dezembro de 2025", "source": CONAB_G, "comex_stat_kt": kt(c["soy_grain"][1]), "usd_fob": c["soy_grain"][0]},
         "Balanço da Conab: o estoque de passagem da soja é em 31 de dezembro, então a safra 2024/25 corresponde às exportações de 2025. O restante da soja vai para esmagamento (farelo e óleo), sementes e estoques.",
         {"alternative": {"production_ibge_pam_2025_t": pam["Soja (em grão)"], "share": round(c["soy_grain"][1] / 1000 / pam["Soja (em grão)"], 4), "source": PAM}}),
    item("soy_meal", "Farelo de soja", soy[("meal", "exports")] / soy[("meal", "production")],
         {"value": soy[("meal", "production")], "unit": "mil t", "period": "2025 (safra 2024/25)", "source": CONAB_G},
         {"value": soy[("meal", "exports")], "unit": "mil t", "period": "2025", "source": CONAB_G, "comex_stat_kt": kt(c["soy_meal"][1]), "usd_fob": c["soy_meal"][0]},
         "Farelo produzido no Brasil pelo esmagamento da soja; o restante vai para ração animal no mercado interno."),
    item("soy_oil", "Óleo de soja", soy[("oil", "exports")] / soy[("oil", "production")],
         {"value": soy[("oil", "production")], "unit": "mil t", "period": "2025 (safra 2024/25)", "source": CONAB_G},
         {"value": soy[("oil", "exports")], "unit": "mil t", "period": "2025", "source": CONAB_G, "comex_stat_kt": kt(c["soy_oil"][1]), "usd_fob": c["soy_oil"][0]},
         "A maior parte do óleo de soja fica no país (alimentação e biodiesel)."),
    item("corn", "Milho", bal["MILHO"]["exports"] / bal["MILHO"]["production"],
         {"value": bal["MILHO"]["production"], "unit": "mil t", "period": "safra 2024/25", "source": CONAB_G},
         {"value": bal["MILHO"]["exports"], "unit": "mil t", "period": "fevereiro de 2025 a janeiro de 2026 (estoque de passagem em 31 de janeiro)", "source": CONAB_G,
          "comex_stat_kt": kt(c["corn_conab"][1]), "usd_fob": c["corn_conab"][0]},
         "Pelo balanço da Conab, cerca de dois terços do milho ficam no país (ração, etanol de milho, indústria).",
         {"alternative": {"production_ibge_pam_2025_t": pam["Milho (em grão)"], "exports_2025_t": round(c["corn_2025"][1] / 1000),
                          "share": round(c["corn_2025"][1] / 1000 / pam["Milho (em grão)"], 4), "source": PAM}}),
    item("cotton", "Algodão em pluma", bal["ALGODÃO"]["exports"] / bal["ALGODÃO"]["production"],
         {"value": bal["ALGODÃO"]["production"], "unit": "mil t de pluma", "period": "safra 2024/25", "source": CONAB_G},
         {"value": bal["ALGODÃO"]["exports"], "unit": "mil t", "period": "2025 (estoque de passagem em 31 de dezembro)", "source": CONAB_G,
          "comex_stat_kt": kt(c["cotton"][1]), "usd_fob": c["cotton"][0]},
         "O IBGE mede o algodão em caroço (com semente), que não é comparável com a pluma exportada; por isso a produção é a da Conab."),
    item("coffee", "Café (grão)", c["coffee"][1] / 1000 / pam["Café (em grão) Total"],
         {"value": pam["Café (em grão) Total"], "unit": "t", "period": "2025", "source": PAM},
         {"value": round(c["coffee"][1] / 1000), "unit": "t", "period": "2025", "source": COMEX + ", posição 0901 (café verde, torrado e descafeinado)", "usd_fob": c["coffee"][0]},
         "A colheita vai de maio a setembro e a exportação de uma safra se estende pelo ano seguinte, então a razão do ano civil é aproximada. O café solúvel (2101) não está incluído."),
    item("sugar", "Açúcar", c["sugar_2526"][1] / 1000 / (sugar["2025/26"] * 1000),
         {"value": sugar["2025/26"], "unit": "mil t", "period": "safra 2025/26 (abril de 2025 a março de 2026)",
          "source": f"Conab, Acompanhamento da safra brasileira de cana-de-açúcar, 4º levantamento 2025/26 (abril de 2026), {CONAB_CANE}"},
         {"value": round(c["sugar_2526"][1] / 1e6, 3), "unit": "mil t", "period": "abril de 2025 a março de 2026", "source": COMEX + ", posição 1701", "usd_fob": c["sugar_2526"][0]},
         "Mesmo período da safra. A cana que não vira açúcar vira etanol, que quase todo fica no país.",
         {"previous_season": {"season": "2024/25", "production_kt": sugar["2024/25"], "exports_kt": round(c["sugar_2425"][1] / 1e6, 3),
                              "share": round(c["sugar_2425"][1] / 1e6 / sugar["2024/25"], 4)}}),
    item("beef", "Carne bovina", meat[("beef", "exports")][0] / meat[("beef", "production")][0],
         {"value": meat[("beef", "production")][0], "unit": "mil t equivalente carcaça", "period": "2025", "source": CONAB_M},
         {"value": meat[("beef", "exports")][0], "unit": "mil t equivalente carcaça", "period": "2025", "source": CONAB_M + " (Secex convertida em equivalente carcaça pela Conab)",
          "comex_stat_kt_product_weight_0201_0202": kt(c["beef"][1]), "usd_fob_0201_0202": c["beef"][0]},
         "Equivalente carcaça: a carne desossada exportada é convertida para o peso de carcaça de que veio, para comparar com a produção. "
         "A produção da Conab (11.933,85 mil t) é maior que o peso de carcaças da pesquisa de abate do IBGE, que só cobre o abate sob inspeção; a planilha da Conab não detalha a diferença.",
         {"alternative": {"production_ibge_abate_2025_t": round(abate["beef"] / 1000), "share_with_conab_exports": round(meat[("beef", "exports")][0] * 1e6 / abate["beef"], 4), "source": ABATE}}),
    item("pork", "Carne suína", meat[("pork", "exports")][0] / meat[("pork", "production")][0],
         {"value": meat[("pork", "production")][0], "unit": "mil t equivalente carcaça", "period": "2025", "source": CONAB_M},
         {"value": meat[("pork", "exports")][0], "unit": "mil t equivalente carcaça", "period": "2025", "source": CONAB_M,
          "comex_stat_kt_product_weight_0203": kt(c["pork"][1]), "usd_fob_0203": c["pork"][0]},
         "Produção de carne suína da Conab tirada do abate do IBGE.",
         {"alternative": {"production_ibge_abate_2025_t": round(abate["pork"] / 1000), "source": ABATE}}),
    item("chicken", "Carne de frango", meat[("chicken", "exports")][0] / meat[("chicken", "production")][0],
         {"value": meat[("chicken", "production")][0], "unit": "mil t", "period": "2025", "source": CONAB_M + "; a planilha atribui a produção de frango à Associação Brasileira dos Produtores de Pintos de Corte (APINCO)"},
         {"value": meat[("chicken", "exports")][0], "unit": "mil t", "period": "2025", "source": CONAB_M + " (Secex)",
          "comex_stat_kt_0207_chicken": kt(c["chicken"][1]), "usd_fob_0207_chicken": c["chicken"][0]},
         "A produção de frango da planilha da Conab vem de uma associação do setor, não de pesquisa oficial; com o peso de carcaças do IBGE (abate sob inspeção) a proporção fica no campo alternative.",
         {"alternative": {"production_ibge_abate_2025_t": round(abate["chicken"] / 1000), "exports_comex_0207_chicken_t": round(c["chicken"][1] / 1000),
                          "share": round(c["chicken"][1] / abate["chicken"], 4), "source": ABATE + "; " + COMEX + ", subposições 0207.11 a 0207.14 (peso do produto)"}}),
    item("banana", "Banana", c["banana"][1] / 1000 / pam["Banana (cacho)"],
         {"value": pam["Banana (cacho)"], "unit": "t", "period": "2025", "source": PAM},
         {"value": round(c["banana"][1] / 1000), "unit": "t", "period": "2025", "source": COMEX + ", posição 0803", "usd_fob": c["banana"][0]},
         "O IBGE mede a banana em cacho; a exportação é em peso líquido. Quase toda a banana fica no mercado interno."),
    item("orange_juice", "Suco de laranja", None,
         {"value": pam["Laranja"], "unit": "t de laranja (fruta)", "period": "2025", "source": PAM},
         {"value": round(c["orange_juice"][1] / 1000), "unit": "t de suco", "period": "2025", "source": COMEX + ", subposições 2009.11, 2009.12 e 2009.19", "usd_fob": c["orange_juice"][0]},
         "Não calculado: nenhuma fonte oficial mede a produção de suco de laranja em toneladas, e a conversão de fruta em suco não é publicada por órgão oficial. "
         "A PIA-Produto do IBGE mede só suco concentrado, em mil litros.",
         {"orange_fresh_exports_t": round(c["orange_fresh"][1] / 1000), "orange_fresh_share": round(c["orange_fresh"][1] / 1000 / pam["Laranja"], 6)}),
    item("iron_ore", "Minério de ferro", c["iron_2024"][1] / 1000 / ANM_IRON_2024_T,
         {"value": ANM_IRON_2024_T, "unit": "t (produção beneficiada)", "period": "2024", "source": f"ANM, Anuário Mineral Brasileiro 2025, ano-base 2024, tabela 3.1, {ANM_AMB}"},
         {"value": round(c["iron_2024"][1] / 1000), "unit": "t", "period": "2024", "source": COMEX + ", posição 2601 (minério, concentrados e pelotas)", "usd_fob": c["iron_2024"][0]},
         "Último ano com produção publicada pela ANM é 2024. Parte do minério vira pelotas no país, e as pelotas exportadas estão na posição 2601."),
    item("crude_oil", "Petróleo bruto", anp_exp_m3 / anp_prod,
         {"value": round(anp_prod), "unit": "m³", "period": "2025", "source": f"ANP, dados abertos, produção nacional de petróleo (óleo e condensado), {ANP_PROD}"},
         {"value": round(anp_exp_m3), "unit": "m³", "period": "2025", "source": f"ANP, dados abertos, exportação de petróleo (fonte Secex), {ANP_TRADE}", "usd_fob": round(anp_exp_usd)},
         "A outra metade é refinada no país; o Brasil também importa petróleo e derivados (veja imports-by-product.json)."),
    item("cellulose", "Celulose (pastas químicas de madeira)", None,
         {"value": int(pia.get("1710.2035 Pastas químicas de madeira, à soda ou ao sulfato, exceto pastas para dissolução", 0) or 0), "unit": "t", "period": "2024",
          "source": "IBGE, Pesquisa Industrial Anual - Produto 2024, SIDRA tabela 10476, produto 1710.2035"},
         {"value": round(c["pulp_2024"][1] / 1000), "unit": "t", "period": "2024", "source": COMEX + ", posição 4703", "usd_fob": c["pulp_2024"][0]},
         "Não calculado: a exportação de 2024 é maior que a produção que a PIA-Produto registra para o mesmo produto, então a pesquisa não cobre toda a produção de celulose; não há outra fonte oficial de produção."),
    item("rare_earths", "Terras raras", None,
         {"value": None, "unit": None, "period": "2024",
          "source": f"ANM, Sumário Mineral 2025, ano-base 2024, {ANM_SUM}: \"a produção beneficiada de concentrado de terras raras foi pequena\" (início da operação em Minaçu, GO); nenhum número publicado. Reservas: 11,4 Mt de óxidos contidos, a segunda maior do mundo segundo a mesma publicação."},
         {"value": round(c["rare_earths"][1] / 1000, 1), "unit": "t", "period": "2025", "source": COMEX + ", NCM 2530.90.30, 2805.30 e 2846", "usd_fob": c["rare_earths"][0]},
         "Não calculado: a produção não tem número oficial publicado. A exportação de 2025 é pequena (veja o valor em US$).",
         {"reserves_mt": 11.4}),
    item("acai", "Açaí", None,
         {"value": pam["Açaí"] + pevs["1.1 - Açaí (fruto)"], "unit": "t de fruto", "period": "2025",
          "source": f"{PAM} (açaí cultivado, {pam['Açaí']} t) + {PEVS} (açaí extrativo, {pevs['1.1 - Açaí (fruto)']} t)"},
         {"value": round(c["acai"][1] / 1000, 1), "unit": "t de purê", "period": "2025", "source": COMEX + ", NCM 2007.99.21 (purês de açaí)", "usd_fob": c["acai"][0]},
         "Não calculado: a produção é de fruto e a exportação é de purê; não há conversão oficial. Parte do açaí exportado pode sair em outros códigos (polpas e misturas) que não separam o açaí."),
    item("brazil_nut", "Castanha-do-pará", (c["brazil_nut_shell"][1] + c["brazil_nut_shelled"][1] - c["brazil_nut_imports"][1]) / 1000 / pevs["1.6 - Castanha-do-pará"],
         {"value": pevs["1.6 - Castanha-do-pará"], "unit": "t", "period": "2025", "source": PEVS},
         {"value": round((c["brazil_nut_shell"][1] + c["brazil_nut_shelled"][1]) / 1000), "unit": "t", "period": "2025",
          "source": COMEX + ", NCM 0801.21.00 (com casca) e 0801.22.00 (sem casca)", "usd_fob": c["brazil_nut_shell"][0] + c["brazil_nut_shelled"][0],
          "with_shell_t": round(c["brazil_nut_shell"][1] / 1000), "shelled_t": round(c["brazil_nut_shelled"][1] / 1000), "imports_t": round(c["brazil_nut_imports"][1] / 1000)},
         "Limite inferior: (exportação com casca + sem casca - importação) / produção. A castanha sem casca pesa menos que a castanha com casca de que veio, então a parte exportada da produção é maior que este número.",
         {"share_is_lower_bound": True}),
    item("tropical_wood", "Madeira nativa (tropical)", None,
         {"value": pevs["7.3 - Madeira em tora"], "unit": "m³ de madeira em tora (extrativa)", "period": "2025", "source": PEVS},
         {"value": round(c["tropical_wood"][1] / 1000), "unit": "t", "period": "2025",
          "source": COMEX + ", madeira tropical serrada (4407.21 a 4407.29), perfilada (4409.22) e compensada (4412.31)", "usd_fob": c["tropical_wood"][0]},
         "Não calculado: a produção é de madeira em tora, em m³, e a exportação é de madeira serrada e beneficiada, em kg; não há conversão oficial. A exportação de madeira nativa em tora é praticamente nula."),
]
if fails:
    print("CHECK FAILED:\n- " + "\n- ".join(fails)); sys.exit(1)
if CONTROL:
    print("control run passed the checks: the identity check is not working"); sys.exit(2)
out = {
    "title": "Quanto da produção nacional vai para fora",
    "rule": ("Produção e exportação na mesma unidade e no mesmo período, de fontes oficiais. Onde a Conab publica o balanço (produção e exportação lado a lado), ele é a fonte; "
             "a exportação do balanço é conferida com o Comex Stat nos mesmos meses. Onde a produção não é medida numa unidade comparável, share_exported é null e a nota diz por quê."),
    "conab_note": no_dash(conab_note), "conab_meats_sources": no_dash(meat_tail),
    "items": items,
    "warnings": warnings,
    "check": {"conab_vs_comex": "exportação da Conab = Comex Stat nos mesmos meses, dentro de 0,5% (soja, farelo, óleo, algodão, milho)",
              "anp_vs_comex": "receita de exportação de petróleo da ANP em 2025 = Comex Stat NCM 27090010 ao dólar",
              "anm": "os números da ANM fixados no script aparecem nos PDFs da ANM", "range": "toda proporção entre 0 e 1",
              "control": "--control lê a exportação de soja de 2024; a checagem da Conab tem de falhar"},
}
size = write_json(OUT, out)
print(f"wrote {OUT.relative_to(ROOT)}: {len(items)} items, {size // 1024} KB; warnings: {warnings}")
for i in items:
    print(f"{i['key']:14} {i['share_exported']}", i.get("alternative", {}).get("share", ""))
