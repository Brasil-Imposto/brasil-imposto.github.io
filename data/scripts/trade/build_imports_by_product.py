"""Brazil's imports by product (SH4) and the trade balance, 2025 and 2026 to the latest month -> data/trade/imports-by-product.json.

Source: Comex Stat API (MDIC/Secex), flow import, queried by NCM for each period and grouped into SH4 by the first 4 NCM digits
(the API's own SH4 grouping can leave out NCM codes missing from its correspondence table). Compact on purpose: each product has
code, official pt-BR description, SH2 chapter, US$ FOB and net kg; the trade balance is exports minus imports, both FOB, by month.
Checks (nothing is written unless they pass): the NCM rows add up to the import total the API returns with no detail, to the
dollar and to the kg; each period matches the official MDIC conference file (IMP_TOTAIS_CONFERENCIA.csv); the monthly totals add
up to the period total, for exports and imports. --control drops the largest NCM row; the first check must fail.
Run: python3 data/scripts/trade/build_imports_by_product.py [--control]
"""
import csv, io, sys
from collections import defaultdict
from trade_common import ROOT, comexstat, fetch_bytes, latest_month, months, no_dash, write_json

OUT = ROOT / "data" / "trade" / "imports-by-product.json"
CONTROL = "--control" in sys.argv
TOTALS = {"import": "https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_TOTAIS_CONFERENCIA.csv",
          "export": "https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_TOTAIS_CONFERENCIA.csv"}

ly, lm, updated = latest_month()
PERIODS = {"2025": months(2025, 1, 2025, 12), str(ly): months(ly, 1, ly, lm)} if ly > 2025 else {"2025": months(2025, 1, 2025, lm)}
official = {f: {r["CO_ANO"]: r for r in csv.DictReader(io.StringIO(fetch_bytes(u).decode("latin-1")), delimiter=";")} for f, u in TOTALS.items()}
fails = []

def body(flow, ms, details, monthly=False):
    return {"flow": flow, "monthDetail": monthly, "period": {"from": ms[0], "to": ms[-1]}, "filters": [], "details": details,
            "metrics": ["metricFOB", "metricKG"]}

sh4, totals, balance, names4, names2 = {}, {}, {}, {}, {}
for p, ms in PERIODS.items():
    rows = comexstat(body("import", ms, ["ncm"]))
    if CONTROL and p == "2025":
        rows = sorted(rows, key=lambda r: -int(r["metricFOB"]))[1:]
    agg = defaultdict(lambda: [0, 0])
    for r in rows:
        agg[r["coNcm"][:4]][0] += int(r["metricFOB"]); agg[r["coNcm"][:4]][1] += int(r["metricKG"])
    tot = comexstat(body("import", ms, []))[0]
    tu, tk = int(tot["metricFOB"]), int(tot["metricKG"])
    su, sk = sum(v[0] for v in agg.values()), sum(v[1] for v in agg.values())
    if (su, sk) != (tu, tk):
        fails.append(f"{p}: import NCM rows US$ {su:,} / {sk:,} kg != API total US$ {tu:,} / {tk:,} kg")
    e = comexstat(body("export", ms, []))[0]
    for flow, (u, k) in (("import", (tu, tk)), ("export", (int(e["metricFOB"]), int(e["metricKG"])))):
        o = official[flow].get(p)
        if o is None or (int(o["VL_FOB"]), int(o["KG_LIQUIDO"])) != (u, k):
            fails.append(f"{p} {flow}: API US$ {u:,} / {k:,} kg != official conference file {o and (o['VL_FOB'], o['KG_LIQUIDO'])}")
        totals.setdefault(p, {})[flow] = (u, k)
    mon = {}
    for flow in ("export", "import"):
        for r in comexstat(body(flow, ms, [], True)):
            mon.setdefault(f"{r['year']}-{r['monthNumber']}", {})[flow] = int(r["metricFOB"])
        if sum(mon[m].get(flow, 0) for m in mon) != totals[p][flow][0]:
            fails.append(f"{p} {flow}: months do not add up to the period total")
    balance[p] = [{"month": m, "exports_usd_fob": mon[m]["export"], "imports_usd_fob": mon[m]["import"],
                   "balance_usd_fob": mon[m]["export"] - mon[m]["import"]} for m in ms]
    sh4[p] = agg
    for r in comexstat(body("import", ms, ["heading"])):
        names4[r["headingCode"]] = r["heading"]
    for r in comexstat(body("import", ms, ["chapter"])):
        names2[r["chapterCode"]] = r["chapter"]

if fails:
    print("CHECK FAILED:\n- " + "\n- ".join(fails[:12])); sys.exit(1)
if CONTROL:
    print("control run passed the checks: the identity check is not working"); sys.exit(2)

codes = sorted({c for p in PERIODS for c in sh4[p]}, key=lambda c: -sh4["2025"].get(c, [0])[0])
out = {
    "title": "Importações do Brasil por produto (posição SH4) e saldo comercial",
    "source": {"name": "Comex Stat, MDIC/Secex", "api": "https://api-comexstat.mdic.gov.br/general (POST, flow import, details ncm)",
               "docs": "https://api-comexstat.mdic.gov.br/docs", "updated": updated, "conference_totals": TOTALS},
    "unit": {"usd_fob": "US$ FOB", "kg": "quilograma líquido"},
    "periods": {p: {"from": ms[0], "to": ms[-1], "exports_usd_fob": totals[p]["export"][0], "imports_usd_fob": totals[p]["import"][0],
                    "balance_usd_fob": totals[p]["export"][0] - totals[p]["import"][0], "imports_kg": totals[p]["import"][1],
                    "exports_kg": totals[p]["export"][1], "products": len(sh4[p])} for p, ms in PERIODS.items()},
    "balance_monthly": balance,
    "columns": ["sh4", "name", "sh2"] + [f"{p}_{m}" for p in PERIODS for m in ("usd_fob", "kg")],
    "chapters": {c: no_dash(n) for c, n in sorted(names2.items())},
    "products": [[c, no_dash(names4.get(c)), c[:2]] + [v for p in PERIODS for v in (sh4[p].get(c, [None, None]))] for c in codes],
    "check": {"identity": "os NCM importados somam o total da API ao dólar e ao kg", "official": "exportação e importação de cada período batem com os arquivos oficiais de conferência do MDIC",
              "monthly": "os meses somam o período", "control": "--control tira o maior NCM; a checagem tem de falhar"},
}
size = write_json(OUT, out)
print(f"wrote {OUT.relative_to(ROOT)}: {len(codes)} SH4, {size // 1024} KB; " + "; ".join(
    f"{p}: exports US$ {totals[p]['export'][0]:,}, imports US$ {totals[p]['import'][0]:,}, balance US$ {totals[p]['export'][0] - totals[p]['import'][0]:,}" for p in PERIODS)
    + f"; SH4 without description: {[c for c in codes if c not in names4]}")
