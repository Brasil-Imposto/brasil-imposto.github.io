"""Question 4, with the project's local data only (2024):
(a) each state government's own liquidated spending per person (SICONFI, RREO Annex 01, intra-budget items excluded);
    in the DF also GDF + FCDF (paid by the União); and SC state + 295 municipalities as an example of "state + municipalities";
(b) federal payroll with a known state, per person (FCDF excluded).
Output: data/df/q4_local_2024.json and tables on screen."""
import json, sys
BASE = sys.argv[1] if len(sys.argv) > 1 else "."
s = json.load(open(f"{BASE}/data/series/state-budgets.json"))
pop = json.load(open(f"{BASE}/data/series/population.json"))["uf"]
fp = json.load(open(f"{BASE}/data/series/federal-payroll-by-uf.json"))
ub = {r["uf"]: r for r in json.load(open(f"{BASE}/data/uf-balance-2024.json"))}
fcdf = ub["DF"]["direct_spending"]["fcdf_df_constitutional_fund"]
P = {u: pop[u]["population"]["2024"] for u in s["uf"]}
rows = []
for u, d in s["uf"].items():
    p = d["periods"]["2024-B6"]
    # Some states book the municipalities' share as spending (Encargos Especiais > Transferências), others as a
    # revenue deduction. To compare them, that subfunction is taken out of spending.
    tr = sum(sb["value"] for f in p["spending_by_function"] if f["label"] == "Encargos Especiais" for sb in (f.get("sub") or []) if sb["label"] == "Transferências")
    rows.append({"uf": u, "pop": P[u], "spending_liquidated": p["spending_liquidated"], "spending_committed": p["spending_committed"],
                 "transfers_subfunction": tr, "per_capita_ex_transfers": (p["spending_liquidated"] - tr) / P[u],
                 "to_municipalities": p.get("to_municipalities"), "revenue_total": p["revenue_total"],
                 "per_capita_liquidated": p["spending_liquidated"] / P[u]})
rows.sort(key=lambda r: -r["per_capita_liquidated"])
print("FCDF 2024 (uf-balance-2024.json):", round(fcdf / 1e9, 2), "bi")
print("(a) despesa liquidada do governo estadual por pessoa, 2024")
for i, r in enumerate(rows, 1):
    print(f"{i:2d} {r['uf']} R$ {r['spending_liquidated']/1e9:7.2f} bi  R$ {r['per_capita_liquidated']:7.0f}/hab | subfunção Transferências {r['transfers_subfunction']/1e9:6.2f} bi -> sem ela R$ {r['per_capita_ex_transfers']:7.0f}/hab")
rk2 = sorted(rows, key=lambda r: -r["per_capita_ex_transfers"])
print("ordem sem a subfunção Transferências:", [(r["uf"], round(r["per_capita_ex_transfers"])) for r in rk2[:8]])
print("média 26 estados sem DF, sem Transferências:", round(sum(r["spending_liquidated"] - r["transfers_subfunction"] for r in rows if r["uf"] != "DF") / sum(r["pop"] for r in rows if r["uf"] != "DF")))
df = next(r for r in rows if r["uf"] == "DF")
df_plus = (df["spending_liquidated"] + fcdf) / df["pop"]
print(f"DF GDF + FCDF: R$ {(df['spending_liquidated']+fcdf)/1e9:.2f} bi, R$ {df_plus:.0f}/hab")
br_states = sum(r["spending_liquidated"] for r in rows if r["uf"] != "DF"); br_pop = sum(r["pop"] for r in rows if r["uf"] != "DF")
print(f"26 estados (sem DF), média ponderada: R$ {br_states/br_pop:.0f}/hab")
# SC state + municipalities
m = json.load(open(f"{BASE}/data/series/sc-municipal-budgets.json"))["municipalities"]
sc_mun = 0.0; n = 0; miss = []
for code, md in m.items():
    pp = (md.get("periods") or {}).get("2024-B6")
    if pp and pp.get("spending_liquidated") is not None: sc_mun += pp["spending_liquidated"]; n += 1
    else: miss.append(code)
sc = next(r for r in rows if r["uf"] == "SC")
sc_to_mun = sc["to_municipalities"] or 0
print(f"SC: estado {sc['spending_liquidated']/1e9:.2f} bi + prefeituras {sc_mun/1e9:.2f} bi ({n} de {len(m)} com 2024-B6) = {(sc['spending_liquidated']+sc_mun)/1e9:.2f} bi, R$ {(sc['spending_liquidated']+sc_mun)/sc['pop']:.0f}/hab; sem prefeitura: {miss[:5]}")
# (b) federal payroll with a known state
fr = []
for u in s["uf"]:
    v = fp["uf"][u]["annual"]["total_located"]["2024"]
    fr.append((v / P[u], u, v))
fr.sort(reverse=True)
print("(b) folha federal localizada 2024 (sem FCDF) por pessoa")
for i, (pc, u, v) in enumerate(fr, 1):
    print(f"{i:2d} {u} R$ {v/1e9:6.2f} bi  R$ {pc:7.0f}/hab/ano  R$ {pc/12:6.0f}/hab/mês")
tot_loc = sum(v for _, _, v in fr); tot_pop = sum(P.values())
print(f"Brasil (soma localizada) R$ {tot_loc/1e9:.2f} bi, R$ {tot_loc/tot_pop:.0f}/hab; sem DF R$ {(tot_loc-fp['uf']['DF']['annual']['total_located']['2024'])/(tot_pop-P['DF']):.0f}/hab")
json.dump({"year": 2024, "fcdf_2024": fcdf, "state_spending": rows,
           "df_gdf_plus_fcdf": {"value": df["spending_liquidated"] + fcdf, "per_capita": df_plus},
           "sc_state_plus_municipalities": {"state": sc["spending_liquidated"], "municipalities": sc_mun, "n_municipalities": n,
                                             "per_capita": (sc["spending_liquidated"] + sc_mun) / sc["pop"]},
           "federal_payroll_located": [{"uf": u, "value": v, "per_capita_year": pc} for pc, u, v in fr]},
          open(f"{BASE}/data/df/q4_local_2024.json", "w"), ensure_ascii=False, indent=1)
