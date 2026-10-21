"""Export prices: Brazil's export unit value next to the World Bank reference price, 2015 to 2025 -> data/trade/export-prices.json.

Brazil: Comex Stat API (MDIC/Secex), US$ FOB divided by net weight, per year, for the 10 largest SH4 products of 2025 plus three the
owner asked about or that have a direct reference (soybean meal, cotton, banana). Crude oil is priced per barrel from the
statistical quantity (m3) of the NCM codes in 2709, 1 barrel = 0,158987294928 m3.
Reference: World Bank Commodity Price Data (Pink Sheet), annual nominal prices (CMO-Historical-Data-Annual.xlsx), with the
series definitions from its own "Description" sheet. A reference price is a specific grade at a specific place (often with
freight to the buyer); it is not the price any one exporter gets, so each pair carries the World Bank's own definition and a
note on what differs. Products with no World Bank series (petroleum products other than crude, chemical wood pulp) have null.
Checks (nothing is written unless they pass): the 2025 US$ and kg of each product equal those in data/trade/exports-by-product.json
(built month by month, a different query path), to the dollar and the kg; each World Bank annual price used equals the mean of
its 12 monthly prices (CMO-Historical-Data-Monthly.xlsx) within the annual file's rounding (the monthly mean is the value used);
every year has crude oil months whose declared kg per m3 is between 800 and 1000 (months outside are listed and left out of the
barrel price). --control adds US$ 1 to one product in 2025; the first check must fail.
Run (after build_exports_by_product.py): python3 data/scripts/trade/build_export_prices.py [--control]
"""
import json, sys
from trade_common import ROOT, comexstat, fetch_bytes, no_dash, read_xlsx, write_json

OUT = ROOT / "data" / "trade" / "export-prices.json"
CONTROL = "--control" in sys.argv
WB_PAGE = "https://www.worldbank.org/en/research/commodity-markets"
WB_BASE = "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/"
YEARS = list(range(2015, 2026))
BBL_M3 = 0.158987294928
EXTRA = ["2304", "5201", "0803"]
# SH4 -> (unit of the Brazilian price, World Bank columns, note on comparability)
REF = {
    "2709": ("US$/barril", ["Crude oil, Brent"], "Brent é o petróleo de referência do Mar do Norte, preço à vista; o petróleo exportado pelo Brasil tem outra qualidade (densidade e enxofre) e costuma ser negociado com desconto ou prêmio sobre o Brent."),
    "1201": ("US$/t", ["Soybeans"], "Até 2020 e de 2021 a 2024 a série do Banco Mundial é a soja dos EUA posta em Roterdã (c.i.f., inclui frete até a Europa); de 2025 em diante é a soja dos EUA embarcada no Golfo (f.o.b.)."),
    "2601": ("US$/t", ["Iron ore, cfr spot"], "A referência é o minério com 62% de ferro entregue na China (c.f.r., inclui o frete marítimo) por tonelada seca; o valor do Brasil é f.o.b. no porto brasileiro, por tonelada de peso líquido declarado (com umidade), e mistura teores diferentes."),
    "0901": ("US$/kg", ["Coffee, Arabica", "Coffee, Robusta"], "Preços indicativos da Organização Internacional do Café, café verde descarregado nos mercados de Nova York e Europa (ex-dock, inclui o transporte); a posição 0901 do Brasil é quase toda café verde, arábica e conilon."),
    "0202": ("US$/kg", ["Beef"], "A referência é carne da Nova Zelândia (90% de carne magra) importada pelos EUA, c.i.f.; desde 2024 a série mudou de origem. A posição 0202 é carne bovina congelada, com cortes e qualidades diferentes."),
    "1701": ("US$/kg", ["Sugar, world"], "Preço diário do Acordo Internacional do Açúcar para açúcar bruto embarcado nos portos do Caribe (f.o.b.); a posição 1701 do Brasil inclui o açúcar bruto e o refinado."),
    "2710": ("US$/t", [], "O Banco Mundial não publica preço de referência para óleos de petróleo que não sejam brutos (óleo combustível, diesel e outros)."),
    "4703": ("US$/t", [], "O Banco Mundial não publica mais preço anual de celulose; a série antiga era de celulose de fibra longa da Suécia, e o Brasil exporta sobretudo fibra curta de eucalipto."),
    "0207": ("US$/kg", ["Chicken"], "Desde setembro de 2021 a série \"Chicken\" do Banco Mundial é o preço de atacado do frango congelado no estado de São Paulo, isto é, um preço do próprio Brasil e não um preço mundial; antes era o preço de atacado nos EUA."),
    "1005": ("US$/t", ["Maize"], "Milho amarelo nº 2 dos EUA embarcado nos portos do Golfo (f.o.b.), a referência mais próxima do milho exportado."),
    "2304": ("US$/t", ["Soybean meal"], "De 1999 a 2020 a referência era o próprio farelo do Brasil posto em Roterdã (c.i.f.); de 2021 a 2024 também farelo do Brasil em Roterdã; de 2025 em diante, farelo dos EUA f.o.b. Roterdã."),
    "5201": ("US$/kg", ["Cotton, A Index"], "Índice A da Cotton Outlook, algodão médio entregue no Extremo Oriente (c.f.r., inclui frete)."),
    "0803": ("US$/kg", ["Banana, US", "Banana, Europe"], "Bananas da América Central e do Sul, grandes marcas, preço de importação nos EUA e no sul da Europa (inclui frete e, na Europa, tarifas)."),
}
SCALE = {"US$/t": 1000.0, "US$/kg": 1.0}
WB_UNIT_TO_BR = {"($/mt)": "US$/t", "($/kg)": "US$/kg", "($/bbl)": "US$/barril", "($/dmtu)": "US$/t"}

fails = []
annual_raw = fetch_bytes(WB_BASE + "CMO-Historical-Data-Annual.xlsx")
monthly_raw = fetch_bytes(WB_BASE + "CMO-Historical-Data-Monthly.xlsx")
A = read_xlsx(annual_raw, "Annual Prices (Nominal)")
M = read_xlsx(monthly_raw, "Monthly Prices")
D = read_xlsx(annual_raw, "Description")
a_hdr = next(r for r in A if len(r) > 2 and r[1] == "Crude oil, average")
a_unit = A[A.index(a_hdr) + 1]
m_hdr = next(r for r in M if len(r) > 2 and r[1] == "Crude oil, average")
updated = {"annual": next(r[0] for r in A if r and isinstance(r[0], str) and r[0].startswith("Updated")),
           "monthly": next(r[0] for r in M if r and isinstance(r[0], str) and r[0].startswith("Updated"))}

def wb(col):
    # The two files mark some series with asterisks ("Beef **" in the monthly file, "Beef" in the annual one).
    norm = lambda h: [str(x).replace("*", "").strip() if x else x for x in h]
    i, j = norm(a_hdr).index(col), norm(m_hdr).index(col)
    out = {}
    for r in A:
        if r and isinstance(r[0], float) and int(r[0]) in YEARS and i < len(r) and isinstance(r[i], float):
            out[int(r[0])] = r[i]
    # The annual file rounds to 2 significant decimals (sugar 2015: 0,30 against a monthly mean of 0,295), so the value used is the
    # mean of the 12 published monthly prices, checked against the annual file within its rounding.
    mean = {}
    for y, v in out.items():
        ms = [r[j] for r in M if r and isinstance(r[0], str) and r[0].startswith(f"{y}M") and j < len(r) and isinstance(r[j], float)]
        if len(ms) != 12 or abs(sum(ms) / 12 - v) > max(0.01 * v, 0.0051):
            fails.append(f"World Bank {col} {y}: annual {v} vs monthly mean {sum(ms) / max(len(ms), 1):.3f} ({len(ms)} months)")
        mean[y] = round(sum(ms) / max(len(ms), 1), 4)
    return mean, out, a_unit[i]

def describe(col):
    key = {"Crude oil, Brent": "Crude oil, UK Brent", "Soybeans": "Soybeans, from", "Iron ore, cfr spot": "Iron ore (any origin)",
           "Coffee, Arabica": "Coffee, Arabica (ICO)", "Coffee, Robusta": "Coffee, Robusta (ICO)", "Beef": "Beef (New Zealand)",
           "Sugar, world": "Sugar (World)", "Chicken": "Chicken (Brazil)", "Maize": "Maize (U.S.)", "Soybean meal": "Soybean meal, from",
           "Cotton, A Index": "Cotton (Cotton Outlook", "Banana, US": "major brands, US import price", "Banana, Europe": "free on truck (f.o.t.) Southern Europe"}[col]
    for r in D:
        for c in r:
            if isinstance(c, str) and key in c:
                return " ".join(c.split())
    return None

prod = json.loads((ROOT / "data" / "trade" / "exports-by-product.json").read_text(encoding="utf-8"))
p25 = {x["sh4"]: x["2025"] for x in prod["products"] if "2025" in x}
top10 = [c for c, _ in sorted(p25.items(), key=lambda x: x[1]["rank"])[:10]]
codes = top10 + [c for c in EXTRA if c not in top10]
rows = comexstat({"flow": "export", "monthDetail": False, "period": {"from": f"{YEARS[0]}-01", "to": f"{YEARS[-1]}-12"},
                  "filters": [{"filter": "heading", "values": codes}], "details": ["heading"], "metrics": ["metricFOB", "metricKG"]})
br = {(r["headingCode"], int(r["year"])): (int(r["metricFOB"]), int(r["metricKG"]), r["heading"]) for r in rows}
# Crude oil per barrel: NCM 27090010 (óleos brutos de petróleo, 99,99% of 2709), month by month. The statistical quantity (m3) is
# the least checked of the three metrics (Secex, Nota Metodológica Quantidade Estatística); a month whose declared kg per m3 falls
# outside 800 to 1000 is a declaration error (February 2017: 99 kg per m3) and is left out of the barrel price, value and volume.
oil, oil_dropped = {}, []
for r in comexstat({"flow": "export", "monthDetail": True, "period": {"from": f"{YEARS[0]}-01", "to": f"{YEARS[-1]}-12"},
                    "filters": [{"filter": "ncm", "values": ["27090010"]}], "details": ["ncm"], "metrics": ["metricFOB", "metricKG", "metricStatistic"]}):
    y, u, k, m3 = int(r["year"]), int(r["metricFOB"]), int(r["metricKG"]), int(r["metricStatistic"])
    if not m3 or not 800 <= k / m3 <= 1000:
        oil_dropped.append({"month": f"{y}-{r['monthNumber']}", "usd_fob": u, "kg": k, "m3_declared": m3, "kg_per_m3": round(k / m3) if m3 else None})
        continue
    a = oil.setdefault(y, [0, 0, 0]); a[0] += u; a[1] += k; a[2] += m3
for y in YEARS:
    if y not in oil or not 800 <= oil[y][1] / oil[y][2] <= 1000:
        fails.append(f"crude oil {y}: no clean months")
    elif oil[y][0] < 0.99 * br[("2709", y)][0] and not any(d["month"].startswith(str(y)) for d in oil_dropped):
        fails.append(f"crude oil {y}: NCM 27090010 is less than 99% of 2709")
for c in codes:
    u, k, _ = br[(c, 2025)]
    if CONTROL and c == codes[0]:
        u += 1
    if (u, k) != (p25[c]["usd_fob"], p25[c]["kg"]):
        fails.append(f"{c} 2025: US$ {u:,} / {k:,} kg here != exports-by-product.json US$ {p25[c]['usd_fob']:,} / {p25[c]['kg']:,} kg")

products = []
for c in codes:
    unit, cols, note = REF[c] if c in REF else ("US$/t", [], "Sem série de referência associada.")
    series = []
    for y in YEARS:
        if (c, y) not in br:
            series.append({"year": y, "usd_fob": None, "kg": None, "unit_value": None}); continue
        u, k, _ = br[(c, y)]
        if c == "2709":
            uv = oil[y][0] / (oil[y][2] / BBL_M3)
        else:
            uv = u / k * SCALE[unit]
        series.append({"year": y, "usd_fob": u, "kg": k, "unit_value": round(uv, 4)})
    refs = []
    for col in cols:
        vals, published, wunit = wb(col)
        if WB_UNIT_TO_BR.get(wunit) != unit:
            fails.append(f"{c}: World Bank unit {wunit} does not match {unit}")
        ratio = {y: round(s["unit_value"] / vals[y], 4) for y, s in zip(YEARS, series) if s["unit_value"] is not None and vals.get(y)}
        refs.append({"series": col, "unit": wunit, "definition": no_dash(describe(col)), "values": {str(y): vals.get(y) for y in YEARS}, "annual_file": {str(y): published.get(y) for y in YEARS},
                     "brazil_over_reference": {str(y): v for y, v in ratio.items()}})
    products.append({"sh4": c, "name": no_dash(br[(c, 2025)][2]), "rank_2025": p25[c]["rank"], "in_top10": c in top10, "unit": unit,
                     "brazil": series, "references": refs, "comparability": note})
    if c == "2709":
        products[-1]["barrel_basis"] = {"ncm": "27090010", "months_left_out": oil_dropped,
                                        "rule": "preço por barril = US$ FOB / (m3 declarados / 0,158987294928), só com os meses em que o peso declarado dá entre 800 e 1000 kg por m3"}

if fails:
    print("CHECK FAILED:\n- " + "\n- ".join(fails[:12])); sys.exit(1)
if CONTROL:
    print("control run passed the checks: the identity check is not working"); sys.exit(2)
out = {
    "title": "Preço de exportação do Brasil e preço de referência internacional, 2015 a 2025",
    "source": {"brazil": "Comex Stat, MDIC/Secex (API https://api-comexstat.mdic.gov.br/general, valor US$ FOB e quilograma líquido por ano; petróleo bruto pela quantidade estatística em m3)",
               "reference": f"Banco Mundial, Commodity Price Data (Pink Sheet), preços anuais nominais, {WB_BASE}CMO-Historical-Data-Annual.xlsx ({updated['annual']}); página {WB_PAGE}",
               "reference_monthly": f"{WB_BASE}CMO-Historical-Data-Monthly.xlsx ({updated['monthly']}), usado só na conferência"},
    "method": ("Valor unitário = valor US$ FOB dividido pelo peso líquido do ano (ou, no petróleo bruto, pelos barris: m3 declarados divididos por 0,158987294928). "
               "brazil_over_reference é o valor unitário do Brasil dividido pelo preço de referência do mesmo ano: 1 é igual, abaixo de 1 é mais barato. "
               "FOB não inclui frete; várias referências incluem frete até o comprador, então parte da diferença é frete e qualidade, não desconto."),
    "products": products,
    "check": {"identity": "o US$ e o kg de 2025 de cada produto batem com exports-by-product.json (consulta mês a mês, caminho diferente)",
              "reference": "o preço de referência é a média dos 12 preços mensais do Banco Mundial; confere com o arquivo anual dentro do arredondamento dele (1% ou 0,005)",
              "oil_density": "petróleo bruto: meses com kg por m3 declarado fora de 800 a 1000 ficam fora do preço por barril (listados em barrel_basis)", "control": "--control soma US$ 1 a um produto; a checagem tem de falhar"},
}
size = write_json(OUT, out)
print(f"wrote {OUT.relative_to(ROOT)}: {len(products)} products, {size // 1024} KB")
for p in products:
    last = p["brazil"][-1]["unit_value"]
    print(p["sh4"], p["name"][:40], p["unit"], round(last, 2) if last else None,
          "; ".join(f"{r['series']} {r['values']['2025']} ratio {r['brazil_over_reference'].get('2025')}" for r in p["references"]))
