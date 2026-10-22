"""Checks for the series files. Every check first runs against a deliberately broken control and must FAIL there,
then runs on the real data. Prints a report; exits 1 if a real check fails or a control passes.
Run: python3 pipelines/series/checks_series.py
"""
import copy
import json
import sys
from pathlib import Path

from fetch_state_series import UF_CODES
from siconfi_client import EntityCache
from siconfi_parse import parse_a01, parse_a02, parse_a03, parse_rgf02

ROOT = Path(__file__).resolve().parents[2]
MUNI_FILES = sorted((ROOT / "data/series").glob("*-municipal-budgets.json"))  # sc-, rs-: one per state with municipal series
TOL = 1.0  # R$
failures = []


def fn_sum_errors(periods):
    """Sum of functions vs the declared Anexo 02 total, and sum of subfunctions vs each function."""
    errs = []
    for key, p in periods.items():
        if p.get("spending_by_function_total") is None:
            continue
        s = sum(f["value"] for f in p["spending_by_function"])
        if abs(s - p["spending_by_function_total"]) > TOL:
            errs.append((key, "functions", round(s - p["spending_by_function_total"], 2)))
        for f in p["spending_by_function"]:
            ss = sum(x["value"] for x in f["sub"])
            if f["sub"] and abs(ss - f["value"]) > TOL:
                errs.append((key, f["label"], round(ss - f["value"], 2)))
    return errs


def diagnose(name, control_errors, real_errors):
    """For facts of the filed data: the control must fail (the probe works); real differences are listed, not failed."""
    ok = bool(control_errors)
    print(f"[{'DIAG' if ok else 'FAIL'}] {name}: control fails with {len(control_errors)} error(s) (expected > 0); "
          f"real data has {len(real_errors)} difference(s) as filed")
    for e in real_errors[:10]:
        print("      ", e)
    if not ok:
        failures.append(name)


def expect(name, control_errors, real_errors):
    ok_control = bool(control_errors)
    ok_real = not real_errors
    print(f"[{'OK' if ok_control and ok_real else 'FAIL'}] {name}: control fails with {len(control_errors)} error(s) "
          f"(expected > 0); real data has {len(real_errors)} error(s) (expected 0)")
    for e in real_errors[:10]:
        print("      ", e)
    if not (ok_control and ok_real):
        failures.append(name)


def main():
    states = json.loads((ROOT / "data/series/state-budgets.json").read_text(encoding="utf-8"))["uf"]
    old = json.loads((ROOT / "data/state-budgets-2024.json").read_text(encoding="utf-8"))

    print("== 1. data/state-budgets-2024.json reproduced by the 2024-B6 period")
    leaked = {"TOTAL (III) = (I + II)", "DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)"}

    def compare(new_states, old_file):
        errs = []
        for uf, o in old_file.items():
            p = new_states[uf]["periods"]["2024-B6"]
            if [(f["label"], f["value"]) for f in o["spending_by_function"]] != \
               [(f["label"], f["value"]) for f in p["spending_by_function"]]:
                errs.append((uf, "functions"))
            for fo, fn in zip(o["spending_by_function"], p["spending_by_function"]):
                subs_old = [(x["label"], x["value"]) for x in fo["sub"] if x["label"] not in leaked]
                if subs_old != [(x["label"], x["value"]) for x in fn["sub"]]:
                    errs.append((uf, "sub", fo["label"]))
            if [(x["label"], x["value"]) for x in o["revenue_top"]] != [(x["label"], x["value"]) for x in p["revenue_lines"]]:
                errs.append((uf, "revenue_top"))
            for a, b in (("spending_total", "spending_by_function_total"), ("revenue_current_total", "revenue_current_total"),
                         ("to_municipalities", "to_municipalities"), ("fundeb_deduction", "fundeb_deduction")):
                if o[a] != p[b]:
                    errs.append((uf, a, o[a], p[b]))
        return errs

    broken = copy.deepcopy(states)
    broken["SC"]["periods"]["2024-B6"]["spending_by_function"][0]["value"] += 0.01
    broken["RS"]["periods"]["2024-B6"]["revenue_lines"].pop()
    expect("reproduction of the 27 states (functions, subfunctions, revenue lines, totals)", compare(broken, old), compare(states, old))
    n_leaked = sum(1 for o in old.values() for f in o["spending_by_function"] for x in f["sub"] if x["label"] in leaked)
    print(f"      note: the 2024 file carries {n_leaked} leaked total rows inside 'Encargos Especiais' subfunctions "
          f"(2 per state); the comparison ignores exactly those, and the new series does not have them")

    print("== 2. sum of functions == Anexo 02 total, and sum of subfunctions == function (every state, every bimester)")
    sc = EntityCache("E", 42)
    rows = sc.records["rreo|2024|6|RREO|RREO-Anexo 02"]["rows"]
    f_leak, t = parse_a02(rows, leak_totals=True)
    control = {"2024-B6 (old parser, leak)": {"spending_by_function": f_leak, "spending_by_function_total": t}}
    f_ok, t = parse_a02(rows)
    dropped = {"2024-B6 (one function dropped)": {"spending_by_function": f_ok[1:], "spending_by_function_total": t}}
    control_errs = fn_sum_errors(control) + fn_sum_errors(dropped)
    real_errs, per_year = [], {}
    for uf, s in states.items():
        for e in fn_sum_errors(s["periods"]):
            real_errs.append((uf,) + e)
        for key in s["periods"]:
            per_year.setdefault(key[:4], set()).add(uf)
    expect("function sums, states", control_errs, real_errs)
    print("      control detail:", control_errs[:3])
    print("      states checked per year:", {y: len(v) for y, v in sorted(per_year.items())})

    for muni_path in MUNI_FILES:
        munis = json.loads(muni_path.read_text(encoding="utf-8"))["municipalities"]
        m_errs, checked = [], 0
        for code, m in munis.items():
            checked += len(m["periods"])
            m_errs += [(code, m["name"]) + e for e in fn_sum_errors(m["periods"])]
        expect(f"function sums, {muni_path.name[:2].upper()} municipalities ({checked} municipality-periods)", control_errs, m_errs)

    print("== 3. Anexo 01 budget_result: every value kept equals total revenue - total executed spending of the same annex")

    def budget_errs(label, kept, rows, period):
        basis = "EMPENHADAS" if period == 6 else "LIQUIDADAS"
        rev = exp = None
        for rot, col, cod, conta, val in rows:  # independent re-read by line name, not the parser
            if conta.startswith(("TOTAL DAS RECEITAS", "SUBTOTAL COM REFINANCIAMENTO (V)")) and col.startswith("Até o Bimestre") and rev is None:
                rev = val
            if conta.startswith(("TOTAL DAS DESPESAS", "SUBTOTAL COM REFINANCIAMENTO (XII)")) and \
                    col.startswith(f"DESPESAS {basis} ATÉ O BIMESTRE") and exp is None:
                exp = val
        if kept is None:
            return []
        if None in (rev, exp) or abs(kept - (rev - exp)) > TOL:
            return [(label, kept, rev, exp)]
        return []

    def monthly_errs(label, lines):
        errs = []
        for ln in lines:
            if ln["total_12m"] is None or not ln["months"]:
                continue
            diff = sum(v or 0 for v in ln["months"].values()) - ln["total_12m"]
            if abs(diff) > TOL:
                errs.append((label, ln["key"], round(diff, 2)))
        return errs

    b_real, m_real, n_a01, n_lines = [], [], 0, 0
    status = {}
    sc = EntityCache("E", 42)
    sc_rows = sc.records["rreo|2024|6|RREO|RREO-Anexo 01"]["rows"]
    b_control = budget_errs("SC 2024-B6 kept with the sign flipped",
                            -states["SC"]["periods"]["2024-B6"]["budget_result"], sc_rows, 6)
    lines, _ = parse_a03(sc.records["rreo|2024|6|RREO|RREO-Anexo 03"]["rows"], 2024, 6)
    icms = next(ln for ln in lines if ln["key"] == "ICMS")
    icms["months"]["2024-03"] = 0
    m_control = monthly_errs("SC 2024-B6 with ICMS of March zeroed", [icms])
    for code, uf in UF_CODES.items():
        cache = EntityCache("E", code)
        for key, r in cache.records.items():
            if r["status"] != "ok":
                continue
            _, y, p = key.split("|")[:3]
            if key.endswith("RREO-Anexo 01"):
                n_a01 += 1
                a = parse_a01(r["rows"], int(p))
                phase = "B6" if p == "6" else "B1-B5"
                status[(phase, a["_budget_status"])] = status.get((phase, a["_budget_status"]), 0) + 1
                kept = states[uf]["periods"].get(f"{y}-B{p}", {}).get("budget_result")
                b_real += budget_errs(f"{uf} {y}-B{p}", kept, r["rows"], int(p))
            elif key.endswith("RREO-Anexo 03"):
                lines, _ = parse_a03(r["rows"], int(y), int(p))
                n_lines += len(lines)
                m_real += monthly_errs(f"{uf} {y}-B{p}", lines)
    expect(f"budget_result identity, states ({n_a01} reports)", b_control, b_real)
    print(f"      line as filed, by bimester: {dict(sorted(status.items()))} "
          f"(ok = kept; missing and inconsistent = null with the reason in the period's nulls)")
    for muni_path in MUNI_FILES:
        munis_all = json.loads(muni_path.read_text(encoding="utf-8"))["municipalities"]
        mb_real, mstatus = [], {}
        for code, m in munis_all.items():
            cache = EntityCache("M", int(code))
            for key, pr in m["periods"].items():
                y, b = key.split("-B")
                r = cache.records.get(f"rreo|{y}|{b}|{pr['report']}|RREO-Anexo 01")
                a = parse_a01(r["rows"], int(b))
                mstatus[a["_budget_status"]] = mstatus.get(a["_budget_status"], 0) + 1
                mb_real += budget_errs(f"{code} {m['name']} {key}", pr["budget_result"], r["rows"], int(b))
        expect(f"budget_result identity, {muni_path.name[:2].upper()} municipalities ({sum(mstatus.values())} municipality-periods)", b_control, mb_real)
        print(f"      line as filed: {mstatus}")
    print("== 4. Anexo 03: the 12 monthly columns add up to the 12-month total (states, every report)")
    expect(f"monthly columns vs 12-month total ({n_lines} line-reports)", m_control, m_real)

    print("== 5. monthly revisions: the same month in a later report of the next year (diagnostic, not a failure)")
    revised, compared = 0, 0
    examples = []
    for code, uf in UF_CODES.items():
        s = states[uf]["revenue_monthly"]
        chosen = {(k, m): v for k, series in s["lines"].items() for m, v in zip(s["months"], series)}
        cache = EntityCache("E", code)
        for key, r in cache.records.items():
            if r["status"] != "ok" or not key.endswith("RREO-Anexo 03"):
                continue
            _, y, p, _, _ = key.split("|")
            lines, _ = parse_a03(r["rows"], int(y), int(p))
            for ln in lines:
                for m, v in ln["months"].items():
                    if m[:4] == y or (ln["key"], m) not in chosen or chosen[(ln["key"], m)] is None or v is None:
                        continue
                    compared += 1
                    if abs(chosen[(ln["key"], m)] - v) > TOL:
                        revised += 1
                        if len(examples) < 5:
                            examples.append((uf, ln["key"], m, chosen[(ln["key"], m)], f"{y}-B{p}", v))
    print(f"      {revised} of {compared} (line, month) values differ between the year's own last report and a report "
          f"of the next year; examples: {examples}")

    print("== 6. RGF: 'saldo do exercício anterior' of year Y == DC/DCL at the end of Y-1 (diagnostic)")
    mism, comp = [], 0
    for code, uf in UF_CODES.items():
        cache = EntityCache("E", code)
        d = states[uf]["debt"]
        for key, r in cache.records.items():
            if r["status"] != "ok" or not key.startswith("rgf|"):
                continue
            y = int(key.split("|")[1])
            prior = parse_rgf02(r["rows"], y).get(f"{y - 1}-prior")
            end = d.get(f"{y - 1}-Q3")
            if end and "SALDO DO EXERCÍCIO ANTERIOR" in end.get("report", ""):
                continue  # the 2018 baseline is this same column: comparing it with itself proves nothing
            if prior and end:
                comp += 1
                for f in ("dc", "dcl"):
                    if prior.get(f) is not None and end.get(f) is not None and abs(prior[f] - end[f]) > TOL:
                        mism.append((uf, y - 1, f, end[f], prior[f]))
    print(f"      {len(mism)} differences in {comp} year pairs; examples: {mism[:6]}")

    print("== 7. Anexo 02 total - Anexo 01 liquidated spending == debt refinancing line of Anexo 01 (every state-period)")

    def refi_errs(label, pr):
        if pr.get("spending_liquidated") is None or pr.get("spending_by_function_total") is None:
            return []
        gap = pr["spending_by_function_total"] - pr["spending_liquidated"]
        refi = pr.get("debt_refinancing_liquidated") or 0
        return [(label, round(gap, 2), refi)] if abs(gap - refi) > TOL else []

    control = copy.deepcopy(states["ES"]["periods"]["2024-B6"])
    control["debt_refinancing_liquidated"] = 0
    real, gaps = [], 0
    for uf, s in states.items():
        for key, pr in s["periods"].items():
            real += refi_errs(f"{uf} {key}", pr)
            if pr.get("debt_refinancing_liquidated"):
                gaps += 1
    diagnose("Anexo 01 vs Anexo 02 spending totals explained by refinancing", refi_errs("ES 2024-B6 refinancing zeroed", control), real)
    print(f"      {gaps} state-periods have debt refinancing, which Anexo 01 keeps outside 'DESPESAS (EXCETO INTRA)' and Anexo 02 includes")

    print("== 8. Union: revenue - transfers == net revenue; net revenue - spending == primary result; "
          "primary (below the line) + interest == nominal")
    u = json.loads((ROOT / "data/series/union.json").read_text(encoding="utf-8"))

    def union_errs(d):
        errs = []
        for i, m in enumerate(d["months"]):
            vals = [d[k][i] for k in ("revenue", "transfers_to_subnationals", "revenue_net", "primary_spending",
                                      "primary_result", "primary_result_below_line", "nominal_interest", "nominal_result")]
            if None in vals:
                continue
            r, t, rn, sp, pr, pb, ni, nr = vals
            for label, diff in (("net", r - t - rn), ("primary", rn - sp - pr), ("nominal", pb + ni - nr)):
                if abs(diff) > TOL:
                    errs.append((m, label, round(diff, 2)))
        return errs
    bu = copy.deepcopy(u)
    bu["primary_spending"][0] += 1e6
    expect("Union identities (92 months)", union_errs(bu), union_errs(u))

    print("== 9. Union: the monthly RTN values add up to the RTN's own annual table (Tabela 2.1), 2019 to 2025")
    try:
        import openpyxl
    except ImportError:
        print("      skipped: openpyxl not installed")
    else:
        wb = openpyxl.load_workbook(Path(__file__).resolve().parent / "cache/union/serie_historica_ago26.xlsx", read_only=True, data_only=True)
        rows = list(wb["2.1"].iter_rows(values_only=True))
        header = next(r for r in rows if r[0] == "Discriminação")

        def annual_errs(d):
            errs = []
            for key, prefix in (("revenue", "1. RECEITA TOTAL"), ("primary_spending", "4. DESPESA TOTAL"),
                                ("primary_result", "5. RESULTADO PRIMÁRIO GOVERNO CENTRAL - ACIMA DA LINHA")):
                row = next(r for r in rows if isinstance(r[0], str) and r[0].startswith(prefix))
                annual = dict(zip(header, row))
                for y in range(2019, 2026):
                    s = sum(v for m, v in zip(d["months"], d[key]) if m.startswith(str(y)))
                    if abs(s - annual[y] * 1e6) > 1000:  # R$ 1 mil: the table is in R$ milhões with float noise
                        errs.append((key, y, round(s / 1e6, 1), round(annual[y], 1)))
            return errs
        bu = copy.deepcopy(u)
        bu["revenue"][5] += 1e9
        expect("Union monthly sums vs RTN annual table", annual_errs(bu), annual_errs(u))

    print("== 10. Central series federal-by-uf-monthly.json (every revenue, transfer and benefit value of the state map)")
    import csv
    import re
    from decimal import Decimal
    fm = json.loads((ROOT / "data/series/federal-by-uf-monthly.json").read_text(encoding="utf-8"))
    MES = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
           "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}

    def dec(x):  # the same reading as build_two_step_balance.py: "1.234.567,89" and "1234567.89" both occur
        x = x.strip()
        if not x:
            return Decimal(0)
        if re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", x):
            x = x.replace(".", "")
        return Decimal(x.replace(",", "."))
    receita = {}
    with open(ROOT / "data/df/arrecadacao-estado.csv", encoding="latin1") as f:
        rows = csv.reader(f, delimiter=";")
        next(rows)
        months = set(fm["months"])
        for r in rows:
            k = (r[2], f"{r[0]}-{MES[r[1]]:02d}")
            if k[1] not in months:
                continue
            receita[k] = receita.get(k, Decimal(0)) + sum((dec(x) for x in r[3:]), Decimal(0))
    status = fm["national"]["federal_revenue_month_status"]
    published = [i for i, s in enumerate(status) if s in ("ok", "unattributed_gap")]

    def revenue_errs(d):
        """Each state's revenue in a published month must be the Receita file's exact value rounded to the cent."""
        errs = []
        for u, x in d["uf"].items():
            for i in published:
                v = x["federal_revenue"]["total"][i]
                ref = receita[(u, d["months"][i])]
                if v is None or abs(Decimal(str(v)) - ref) > Decimal("0.005"):
                    errs.append((u, d["months"][i], v, float(ref)))
        return errs
    bad = copy.deepcopy(fm)
    bad["uf"]["SC"]["federal_revenue"]["total"][published[0]] += 0.01
    expect(f"state revenue vs the Receita file, to the half cent ({len(published)} published months x 27 states)",
           revenue_errs(bad), revenue_errs(fm))

    # National total minus the 27 states, month by month. Outside the months the series flags, the gap measured on
    # 2026-10-21 is -R$ 7,02 to +R$ 3,06 (the national series is rounded); a month beyond R$ 10 is listed, and a negative
    # one means the states add up to more than the country.
    GAP_TOL = 10.0

    def gap_errs(d):
        errs = []
        nat = d["national"]["federal_revenue_total_receita"]
        for i in published:
            g = nat[i] - sum(x["federal_revenue"]["total"][i] for x in d["uf"].values())
            if abs(g) > GAP_TOL:
                errs.append((d["months"][i], status[i], round(g, 2), "states above the national total" if g < 0 else "without a state"))
        return errs
    ok_month = next(i for i in published if abs(fm["national"]["federal_revenue_total_receita"][i]
                                                 - sum(x["federal_revenue"]["total"][i] for x in fm["uf"].values())) <= GAP_TOL)
    bad = copy.deepcopy(fm)
    bad["uf"]["SC"]["federal_revenue"]["total"][ok_month] += 1e6
    diagnose(f"national revenue minus the 27 states beyond R$ {GAP_TOL:.0f} a month", gap_errs(bad), gap_errs(fm))

    def unpublished_with_numbers(d):
        """Months after the last month the Receita published that still carry transfer numbers (partial for the map)."""
        out = []
        for i, s in enumerate(status):
            if s == "not_published":
                n = sum(1 for x in d["uf"].values() if x["transfers"]["total"][i] is not None)
                if n:
                    out.append((d["months"][i], f"transfers in {n} states", "the Portal's own file of the month may be partial"))
        return out
    bad = copy.deepcopy(fm)
    bad["national"]["federal_revenue_month_status"] = ["not_published"] * len(status)
    diagnose("months past the Receita's last published month that carry numbers", unpublished_with_numbers(bad), unpublished_with_numbers(fm))

    print("\nRESULT:", "all checks passed" if not failures else f"FAILED: {failures}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
