"""Joins the yearly two-step runs (build_two_step_balance.py) into one monthly series the site reads (D45).

Usage: python3 data/scripts/ug/build_two_step_series.py
Input: every data/ug/two-step-balance-YYYY-MM-MM.json whose check passed (a failed run is never written).
Output: data/series/federal-spending-two-step-by-uf.json, months 2019-01 to the last month with revenue by state; a month
not computed yet is null, so the site never sums a partial period. Unemployment insurance and wage bonus by state from
the MTE are annual (mte_annual): the site adds them only for a whole year inside the chosen period.
Union block (D115), monthly in "union": the official totals of both sides (Receita national revenue; RTN line 2 plus
line 4) and the official lines and Tesouro-base sums from which the site draws what the Union paid with no state.
Check, in whole cents: summed over each yearly run's months, the series gives back that run's own Union block (official
totals and every part). --control moves one cent in one month after assembly and must fail; --control=input moves one cent
in the last run's own monthly INSS line before assembly and must fail too.
"""
import glob, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
runs = [json.load(open(f)) for f in sorted(glob.glob(P("data/ug/two-step-balance-*.json")))]
assert all(r["check"]["passed"] and not r["check"]["control_run"] for r in runs)
CONTROL = next(((a.split("=", 1)[1] if "=" in a else "output") for a in sys.argv[1:] if a.startswith("--control")), None)
if CONTROL == "input":
    _u = runs[-1]["union_by_month"][runs[-1]["months"][-1]]; _u["inss_rtn"] = round(_u["inss_rtn"] + 0.01, 2)
fm = json.load(open(P("data/series/federal-by-uf-monthly.json")))
last = max(m for r in runs for m in r["months"])
months = [m for m in fm["months"] if "2019-01" <= m <= last]
UFS = sorted(runs[0]["states"])
KINDS = list(runs[0]["monthly"]["SP"]["executive_by_kind"])
BRANCHES = list(runs[0]["monthly"]["SP"]["other_branches_by_branch"])
null = lambda: [None] * len(months)
uf = {u: {"executive": null(), "central_benefits_localized": null(), "other_branches": null(), "fcdf": null(),
          "executive_by_kind": {k: null() for k in KINDS}, "other_branches_by_branch": {k: null() for k in BRANCHES}} for u in UFS}
no_state = {k: null() for k in ("executive", "central_benefits", "other_branches")}
UNION_KEYS = ["official_revenue", "official_returned_rtn", "inss_rtn", "bpc_rtn", "tesouro_base_executive_not_in_portal",
              "financial_investments_group_5", "private_international_abroad", "public_transfers_tesouro",
              "unemployment_and_wage_bonus_portal_mte_year"]
union = {k: null() for k in UNION_KEYS}
mte, years, broken = {}, {}, {}
seen = set()
for r in runs:
    for i, m in enumerate(r["months"]):
        assert m not in seen, f"{m} is in two runs"; seen.add(m)
        j = months.index(m)
        for u in UFS:
            x = r["monthly"][u]
            for k in ("executive", "central_benefits_localized", "other_branches", "fcdf"):
                uf[u][k][j] = x[k][i]
            for k in KINDS: uf[u]["executive_by_kind"][k][j] = x["executive_by_kind"][k][i]
            for k in BRANCHES: uf[u]["other_branches_by_branch"][k][j] = x["other_branches_by_branch"][k][i]
        for k in no_state: no_state[k][j] = r["no_state_by_month"][m][k]
        for k in UNION_KEYS: union[k][j] = r["union_by_month"][m][k]
    for m, v in r["check"]["broken_portal_months_left_out"].items():
        broken[m] = {**v, "reason": "Portal file with a total far from the Tesouro base in the same scope; left out on both sides of the balance"}
    y = r["months"][0][:4]
    if r.get("unemployment_insurance_and_wage_bonus_mte_annual"):
        a = r["unemployment_insurance_and_wage_bonus_mte_annual"]
        mte[y] = {"uf": {u: {"unemployment_insurance": a[f"{u}|unemployment_insurance"], "wage_bonus": a[f"{u}|wage_bonus"]} for u in UFS},
                  "no_state": sum(v for k, v in a.items() if k.split("|")[0] not in UFS)}
    years[y] = {"months": [r["months"][0], r["months"][-1]], "check_passed": True, "union_block": r["union_block"],
                "unemployment_and_wage_bonus_rule": r["check"]["unemployment_and_wage_bonus_rule"],
                "tesouro_minus_portal_executive": r["check"]["tesouro_minus_portal_executive"],
                "portal_files": {m: v["file"] for m, v in r["sources"]["portal_expense_execution"].items()},
                "tesouro_base": r["sources"]["tesouro_base"]}
# ---------- check: each run's Union block comes back from the monthly series, to the cent
c = lambda v: int(round(v * 100))
if CONTROL == "output":
    j = months.index(runs[-1]["months"][-1]); union["inss_rtn"][j] = round(union["inss_rtn"][j] + 0.01, 2)
F = json.load(open(P("data/series/federal-by-uf-monthly.json")))
fi = {m: i for i, m in enumerate(F["months"])}
bad = {}
for r in runs:
    y, ms = r["months"][0][:4], r["months"]
    J = [months.index(m) for m in ms]
    S = lambda a: sum(c(a[j]) for j in J)
    states = lambda k: sum(c(F["uf"][u][k][fi[m]]) for u in UFS for m in ms)
    states_tr = sum(c(F["uf"][u]["transfers"]["total"][fi[m]]) for u in UFS for m in ms)
    ub, p = r["union_block"], r["union_block"]["returned"]["parts"]
    central = S(no_state["central_benefits"]) + (round(mte[y]["no_state"] * 100) if y in mte else 0)
    got = {"sent_official_total": S(union["official_revenue"]) - c(ub["sent"]["official_total"]),
           "returned_official_total": S(union["official_returned_rtn"]) - c(ub["returned"]["official_total"]),
           "national_programs": S(no_state["executive"]) - c(p["national_programs_executive_no_state_in_localizer"]),
           "central_benefits": central - c(p["benefits_paid_by_a_central_unit_without_state"]),
           "other_branches": S(no_state["other_branches"]) - c(p["other_branches_without_state"]),
           "tesouro_not_in_portal": S(union["tesouro_base_executive_not_in_portal"]) - c(p["tesouro_base_executive_not_in_portal_court_ordered_and_residue"]),
           "inss": S(union["inss_rtn"]) - states("inss") - c(p["inss_benefits_not_in_the_bulletin_by_state"]),
           "bpc": S(union["bpc_rtn"]) - states("bpc") - c(p["bpc_not_in_the_series_by_state"]),
           "group_5": S(union["financial_investments_group_5"]) - c(p["financial_investments_group_5"]),
           "private_abroad": S(union["private_international_abroad"]) - c(p["payments_to_private_entities_international_bodies_and_abroad"]),
           "transfers": S(union["public_transfers_tesouro"]) - states_tr - c(p["transfers_to_state_and_city_governments_not_placed_in_a_state"])}
    # the central-benefits part also holds the emergency aid paid through the Bolsa Família action (2020, 2021): it is in
    # the run's no_state_by_month central_benefits already, so the sum above covers it
    bad.update({f"{y}:{k}": v for k, v in got.items() if v != 0})
print("union block check, cents off by run and part:", bad or "none")
if bad:
    raise SystemExit("CHECK FAILED")
out = {"title": "Federal spending in each state under the two-step rule (GD16, D45, D114), monthly",
       "rule": runs[0]["rule"], "months": months, "uf": uf, "mte_annual": mte, "no_state": no_state, "union": union, "years": years,
       "broken_months": broken, "missing_months": [m for m in months if m not in seen and m not in broken], "collected_at": "2026-10-02",
       "built_from": [os.path.relpath(f, ROOT) for f in sorted(glob.glob(P("data/ug/two-step-balance-*.json")))]}
if not CONTROL:
    json.dump(out, open(P("data/series/federal-spending-two-step-by-uf.json"), "w"), ensure_ascii=False)
print("months", months[0], months[-1], "computed", len(seen), "missing", len(out["missing_months"]), "broken", list(broken), "mte years", list(mte))
