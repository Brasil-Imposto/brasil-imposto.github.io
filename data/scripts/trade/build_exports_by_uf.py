"""Exports by state (UF of production), 2025 and 2026 to the latest month -> data/trade/exports-by-uf.json.

Source: Comex Stat API (MDIC/Secex). In "Dados Gerais" the export state is the state where the good was produced, whatever the
exporter's seat (official FAQ, question 10). Queried by state and NCM for each period and grouped into SH4 by the first 4 NCM
digits (the API's own SH4 grouping leaves out two NCM codes, see build_exports_by_product.py). Rows without a producing state
come as "Não Declarada"; the API's UF table also has "Consumo de Bordo", "Exterior", "Estados Diversos - Café", "Mercadoria
Nacionalizada" and "Reexportação", kept under their own names when they appear.
Each state: total US$ FOB and kg, share of Brazil, value in R$ (month by month at the PTAX average, BCB SGS 3698) and its 5 largest
SH4 products with their share of the state and of Brazil's exports of that product.
Checks (nothing is written unless they pass): states add up to the Brazil total the API returns with no detail, to the dollar
and to the kg; each state's NCM rows add up to the state total the API returns with the state detail only; each month the states
add up to the month total (for the R$ conversion). --control drops one state; the first check must fail.
Run: python3 data/scripts/trade/build_exports_by_uf.py [--control]
"""
import sys
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from trade_common import ROOT, comexstat, comexstat_get, latest_month, months, no_dash, ptax_monthly, write_json

OUT = ROOT / "data" / "trade" / "exports-by-uf.json"
CONTROL = "--control" in sys.argv
CENT = Decimal("0.01")

ly, lm, updated = latest_month()
PERIODS = {"2025": months(2025, 1, 2025, 12), str(ly): months(ly, 1, ly, lm)} if ly > 2025 else {"2025": months(2025, 1, 2025, lm)}
rates, fails = ptax_monthly([m for ms in PERIODS.values() for m in ms])
uf_table = {r["text"]: r["uf"] for r in comexstat_get("/tables/uf")}

def body(ms, details, monthly=False):
    return {"flow": "export", "monthDetail": monthly, "period": {"from": ms[0], "to": ms[-1]}, "filters": [], "details": details,
            "metrics": ["metricFOB", "metricKG"]}

periods, names4 = {}, {}
for p, ms in PERIODS.items():
    total = comexstat(body(ms, []))[0]
    tu, tk = int(total["metricFOB"]), int(total["metricKG"])
    st = {r["state"]: (int(r["metricFOB"]), int(r["metricKG"])) for r in comexstat(body(ms, ["state"]))}
    if CONTROL and p == "2025":
        st.pop(sorted(st, key=lambda s: -st[s][0])[5])
    su, sk = sum(v[0] for v in st.values()), sum(v[1] for v in st.values())
    if (su, sk) != (tu, tk):
        fails.append(f"{p}: states US$ {su:,} / {sk:,} kg != Brazil total US$ {tu:,} / {tk:,} kg")
    prod = defaultdict(lambda: defaultdict(int))
    for r in comexstat(body(ms, ["state", "ncm"])):
        prod[r["state"]][r["coNcm"][:4]] += int(r["metricFOB"])
    for s, (u, _) in st.items():
        if sum(prod[s].values()) != u:
            fails.append(f"{p} {s}: NCM rows US$ {sum(prod[s].values()):,} != state total US$ {u:,}")
    brl = defaultdict(Decimal)
    mt = {f"{r['year']}-{r['monthNumber']}": int(r["metricFOB"]) for r in comexstat(body(ms, [], True))}
    ms_sum = defaultdict(int)
    for r in comexstat(body(ms, ["state"], True)):
        ym = f"{r['year']}-{r['monthNumber']}"
        brl[r["state"]] += Decimal(int(r["metricFOB"])) * rates[ym]
        ms_sum[ym] += int(r["metricFOB"])
    for ym in ms:
        if ms_sum[ym] != mt.get(ym):
            fails.append(f"{ym}: states by month US$ {ms_sum[ym]:,} != month total {mt.get(ym)}")
    national = defaultdict(int)
    for s in prod:
        for c, v in prod[s].items():
            national[c] += v
    for r in comexstat(body(ms, ["heading"])):
        names4[r["headingCode"]] = r["heading"]
    periods[p] = {"ms": ms, "total": (tu, tk), "states": st, "prod": prod, "brl": brl, "national": national}

if fails:
    print("CHECK FAILED:\n- " + "\n- ".join(fails[:12]) + ("\n- ..." if len(fails) > 12 else "")); sys.exit(1)
if CONTROL:
    print("control run passed the checks: the identity check is not working"); sys.exit(2)

unknown = sorted({s for p in periods.values() for s in p["states"] if s not in uf_table})
out_states = {}
for p, d in periods.items():
    tu, tk = d["total"]
    for s, (u, k) in sorted(d["states"].items(), key=lambda x: -x[1][0]):
        code = uf_table.get(s, s)
        e = out_states.setdefault(code, {"uf": code, "name": s})
        top = sorted(d["prod"][s].items(), key=lambda x: -x[1])[:5]
        e[p] = {"usd_fob": u, "kg": k, "share_of_brazil": round(u / tu, 6), "brl": float(d["brl"][s].quantize(CENT, ROUND_HALF_UP)),
                "top_products": [{"sh4": c, "name": no_dash(names4.get(c, c)), "usd_fob": v, "share_of_state": round(v / u, 4) if u else None,
                                  "share_of_brazil_product": round(v / d["national"][c], 4)} for c, v in top]}
order = sorted(out_states, key=lambda c: -out_states[c].get("2025", {}).get("usd_fob", 0))
out = {
    "title": "Exportações por estado de produção",
    "source": {"name": "Comex Stat, MDIC/Secex", "api": "https://api-comexstat.mdic.gov.br/general (POST, flow export, details state e state+ncm)",
               "docs": "https://api-comexstat.mdic.gov.br/docs", "updated": updated,
               "uf_rule": "Nas exportações, a UF é o estado produtor da mercadoria, independentemente da sede da empresa exportadora (FAQ oficial do MDIC, pergunta 10, https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/perguntas-frequentes-faq)",
               "fx": "Banco Central do Brasil, SGS 3698 (dólar, venda, média mensal da PTAX)"},
    "periods": {p: {"from": d["ms"][0], "to": d["ms"][-1], "total_usd_fob": d["total"][0], "total_kg": d["total"][1]} for p, d in periods.items()},
    "not_declared_note": "\"Não Declarada\" reúne as exportações sem estado produtor informado na declaração; entra na soma para fechar com o total do Brasil.",
    "states": [out_states[c] for c in order],
    "check": {"identity": "os estados (mais \"Não Declarada\") somam o total do Brasil ao dólar e ao kg", "products": "os NCM de cada estado somam o total do estado ao dólar",
              "monthly": "os estados somam o total de cada mês (base da conversão em R$)", "control": "--control tira um estado; a checagem tem de falhar"},
}
size = write_json(OUT, out)
print(f"wrote {OUT.relative_to(ROOT)}: {len(order)} entries, {size // 1024} KB; names outside the API UF table: {unknown}")
