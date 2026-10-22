"""Brazil's exports by product (SH4), every product, 2025 and 2026 to the latest month -> data/trade/exports-by-product.json.

Source: Comex Stat API (MDIC/Secex), https://api-comexstat.mdic.gov.br/docs. Queried month by month at NCM level (8 digits) and
grouped into SH4 positions by the first 4 digits, which is the definition of the position. The API's own SH4 grouping
(details "heading") leaves out two NCM codes that its correspondence table does not link to any position (81126100 and
85492100, US$ 6.155 in 2025), so grouping by NCM is the only way the products add up to the total.
Each product: SH4 code and official pt-BR description, SH2 chapter and description, US$ FOB, net kg, share of the period total,
the value in R$ (each month's US$ times that month's PTAX average, BCB SGS 3698, dólar venda, média do período) and, for the
50 largest of each period, the 3 largest destination countries.
Checks (nothing is written unless they pass): each month the NCM rows add up to the month total the API returns with no
detail, to the dollar and to the kg; each period adds up to the official MDIC conference file (EXP_TOTAIS_CONFERENCIA.csv); each
top-50 product's destinations add up to the product, to the dollar; SGS 3698 equals the mean of the daily closing PTAX (BCB PTAX
service) for every month, to 4 decimals. --control drops the largest NCM row of one month; the first check must fail.
Run: python3 pipelines/trade/build_exports_by_product.py [--control]
(Optional: BI_TRADE_CACHE=<temp folder> keeps API answers between runs.)
"""
import csv, io, sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from trade_common import ROOT, comexstat, fetch_bytes, latest_month, months, no_dash, ptax_monthly, write_json

OUT = ROOT / "data" / "trade" / "exports-by-product.json"
CONTROL = "--control" in sys.argv
TOTALS_URL = "https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_TOTAIS_CONFERENCIA.csv"
TOP = 50
CENT = Decimal("0.01")

ly, lm, updated = latest_month()
PERIODS = {"2025": months(2025, 1, 2025, 12), str(ly): months(ly, 1, ly, lm)} if ly > 2025 else {"2025": months(2025, 1, 2025, lm)}
all_months = [m for ms in PERIODS.values() for m in ms]
fails = []

rates, fx_fails = ptax_monthly(all_months)
fails += fx_fails

official = {row["CO_ANO"]: row for row in csv.DictReader(io.StringIO(fetch_bytes(TOTALS_URL).decode("latin-1")), delimiter=";")}

sh4 = {p: defaultdict(lambda: [0, 0, Decimal(0)]) for p in PERIODS}   # period -> sh4 -> [usd, kg, brl]
ptot = {}
names4, names2 = {}, {}
for p, ms in PERIODS.items():
    y0, m0 = ms[0].split("-"); y1, m1 = ms[-1].split("-")
    month_total = {f"{r['year']}-{r['monthNumber']}": (int(r["metricFOB"]), int(r["metricKG"]))
                   for r in comexstat({"flow": "export", "monthDetail": True, "period": {"from": ms[0], "to": ms[-1]}, "filters": [],
                                       "details": [], "metrics": ["metricFOB", "metricKG"]})}
    pu = pk = 0
    pb = Decimal(0)
    for i, ym in enumerate(ms):
        rows = comexstat({"flow": "export", "monthDetail": False, "period": {"from": ym, "to": ym}, "filters": [], "details": ["ncm"],
                          "metrics": ["metricFOB", "metricKG"]})
        if CONTROL and p == "2025" and i == 0:
            rows = sorted(rows, key=lambda r: -int(r["metricFOB"]))[1:]
        mu = mk = 0
        for r in rows:
            u, k = int(r["metricFOB"]), int(r["metricKG"])
            e = sh4[p][r["coNcm"][:4]]
            e[0] += u; e[1] += k; e[2] += Decimal(u) * rates.get(ym, Decimal(0))
            mu += u; mk += k
        if (mu, mk) != month_total.get(ym):
            fails.append(f"{ym}: NCM rows US$ {mu:,} / {mk:,} kg != API month total {month_total.get(ym)}")
        pu += mu; pk += mk; pb += Decimal(mu) * rates.get(ym, Decimal(0))
    o = official.get(p)
    if o is None or (int(o["VL_FOB"]), int(o["KG_LIQUIDO"])) != (pu, pk):
        fails.append(f"{p}: products US$ {pu:,} / {pk:,} kg != official conference file {o and (o['VL_FOB'], o['KG_LIQUIDO'])}")
    ptot[p] = (pu, pk, pb)
    for r in comexstat({"flow": "export", "monthDetail": False, "period": {"from": ms[0], "to": ms[-1]}, "filters": [], "details": ["heading"],
                        "metrics": ["metricFOB"]}):
        names4[r["headingCode"]] = r["heading"]
    for r in comexstat({"flow": "export", "monthDetail": False, "period": {"from": ms[0], "to": ms[-1]}, "filters": [], "details": ["chapter"],
                        "metrics": ["metricFOB"]}):
        names2[r["chapterCode"]] = r["chapter"]

dest = {}
for p, ms in PERIODS.items():
    top = sorted(sh4[p], key=lambda c: -sh4[p][c][0])[:TOP]
    rows = comexstat({"flow": "export", "monthDetail": False, "period": {"from": ms[0], "to": ms[-1]}, "filters": [{"filter": "heading", "values": top}],
                      "details": ["heading", "country"], "metrics": ["metricFOB", "metricKG"]})
    by = defaultdict(list)
    for r in rows:
        by[r["headingCode"]].append((r["country"], int(r["metricFOB"]), int(r["metricKG"])))
    for c in top:
        s = sum(u for _, u, _ in by[c])
        if s != sh4[p][c][0]:
            fails.append(f"{p} {c}: destinations US$ {s:,} != product US$ {sh4[p][c][0]:,}")
        dest[(p, c)] = sorted(by[c], key=lambda x: -x[1])[:3]

missing = sorted(c for p in PERIODS for c in sh4[p] if c not in names4)
if fails:
    print("CHECK FAILED:\n- " + "\n- ".join(fails[:12]) + ("\n- ..." if len(fails) > 12 else "")); sys.exit(1)
if CONTROL:
    print("control run passed the checks: the identity check is not working"); sys.exit(2)

def brl(x):
    return float(x.quantize(CENT, ROUND_HALF_UP))

codes = sorted({c for p in PERIODS for c in sh4[p]}, key=lambda c: -sh4["2025"][c][0] if c in sh4["2025"] else 0)
products = []
for c in codes:
    e = {"sh4": c, "name": no_dash(names4.get(c)), "sh2": c[:2], "chapter": no_dash(names2.get(c[:2]))}
    for p in PERIODS:
        if c not in sh4[p]:
            continue
        u, k, b = sh4[p][c]
        v = {"usd_fob": u, "kg": k, "share": round(u / ptot[p][0], 6), "brl": brl(b), "rank": 0}
        if (p, c) in dest:
            v["top_destinations"] = [{"country": n, "usd_fob": du, "kg": dk, "share_of_product": round(du / u, 4)} for n, du, dk in dest[(p, c)]]
        e[p] = v
    products.append(e)
for p in PERIODS:
    for i, c in enumerate(sorted(sh4[p], key=lambda c: -sh4[p][c][0]), 1):
        next(x for x in products if x["sh4"] == c)[p]["rank"] = i

out = {
    "title": "Exportações do Brasil por produto (posição SH4)",
    "source": {"name": "Comex Stat, Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (Secex)",
               "api": "https://api-comexstat.mdic.gov.br/general (POST, flow export, details ncm, métricas metricFOB e metricKG)",
               "docs": "https://api-comexstat.mdic.gov.br/docs", "updated": updated,
               "conference_totals": TOTALS_URL,
               "fx": "Banco Central do Brasil, SGS 3698 (taxa de câmbio, dólar americano, venda, média mensal da PTAX), https://api.bcb.gov.br/dados/serie/bcdata.sgs.3698/dados"},
    "unit": {"usd_fob": "US$ FOB (valor no porto de embarque, sem frete e seguro)", "kg": "quilograma líquido", "brl": "R$ correntes, cada mês convertido pela PTAX média do mês",
             "share": "fração do total exportado no período (0 a 1)"},
    "periods": {p: {"from": ms[0], "to": ms[-1], "months": len(ms), "total_usd_fob": ptot[p][0], "total_kg": ptot[p][1], "total_brl": brl(ptot[p][2]),
                    "products": len(sh4[p])} for p, ms in PERIODS.items()},
    "fx_monthly": {m: float(v) for m, v in rates.items()},
    "method": ("Consulta mês a mês por NCM (8 dígitos) e soma pela posição SH4 (4 primeiros dígitos). A posição SH4 da própria API deixa de fora "
               "dois NCM sem correspondência na tabela dela (81126100 e 85492100); por isso a soma é feita a partir do NCM. "
               "Destinos: os 3 maiores países de cada um dos 50 maiores produtos do período."),
    "products": products,
    "check": {"identity": "em cada mês os NCM somam o total da API ao dólar e ao kg", "official": "cada período bate com o arquivo oficial de conferência do MDIC",
              "destinations": "os países de cada um dos 50 maiores produtos somam o produto ao dólar",
              "fx": "a SGS 3698 é a média da PTAX diária de venda (serviço PTAX do BCB) em todos os meses, a 4 casas",
              "control": "--control tira o maior NCM de um mês; a checagem tem de falhar"},
}
size = write_json(OUT, out)
print(f"wrote {OUT.relative_to(ROOT)}: {len(products)} SH4 products, " + ", ".join(f"{p}: US$ {ptot[p][0]:,} FOB, R$ {brl(ptot[p][2]):,.2f}" for p in PERIODS)
      + f", {size // 1024} KB; SH4 codes without an API description: {missing}")
