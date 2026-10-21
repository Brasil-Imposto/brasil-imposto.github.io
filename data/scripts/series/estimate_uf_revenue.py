"""Estimates the split of federal revenue by state (UF) for the months where the Receita Federal booked in the
Distrito Federal a large part of what was paid in other states (status 'uf_attribution_broken' in
data/series/federal-by-uf-monthly.json; February 2025 to January 2026).

Method (owner decision D37, 2026-10-01): for each broken month and each tax line, every UF gets its share of that
line in the same calendar month of the latest sound year, applied to the national total of the line; the month is
then scaled so the sum of the UFs equals the national total published by the Receita. The published numbers are
not changed; the estimate is a separate file. The method is backtested on sound years (2024 from 2023 and 2023
from 2022) and the error is stored with the estimate, so the site can show it.

Run: python3 data/scripts/series/estimate_uf_revenue.py
Output: data/series/federal-revenue-uf-estimated.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "data" / "series" / "federal-by-uf-monthly.json"
MUNI = sorted((ROOT / "data" / "series").glob("*-municipal-federal.json"))  # sc-, rs-: states with municipal series
OUT = ROOT / "data" / "series" / "federal-revenue-uf-estimated.json"

F = json.loads(SRC.read_text(encoding="utf-8"))
MONTHS = F["months"]
IX = {m: i for i, m in enumerate(MONTHS)}
UFS = list(F["uf"])
STATUS = F["national"]["federal_revenue_month_status"]
NATIONAL = F["national"]["federal_revenue_total_receita"]
LINES = list(F["uf"]["SC"]["federal_revenue"]["by_tax"])


def val(uf, line, month):
    arr = F["uf"][uf]["federal_revenue"]["by_tax"].get(line)
    i = IX.get(month)
    return (arr[i] or 0.0) if arr is not None and i is not None else 0.0


def broken(month):
    return "broken" in str(STATUS[IX[month]])


def reference(month):
    """Same calendar month of the latest earlier year that is not broken."""
    y, m = int(month[:4]), month[5:7]
    for yy in range(y - 1, int(MONTHS[0][:4]) - 1, -1):
        r = f"{yy}-{m}"
        if r in IX and not broken(r):
            return r
    raise ValueError(f"no reference for {month}")


def estimate(month, ref, scale_to_national=True):
    """Per UF and per tax line, the estimated revenue of `month` using the shares of `ref`."""
    out = {u: {k: 0.0 for k in LINES} for u in UFS}
    for k in LINES:
        n = sum(val(u, k, month) for u in UFS)
        r = sum(val(u, k, ref) for u in UFS)
        for u in UFS:
            out[u][k] = n * val(u, k, ref) / r if r > 0 else val(u, k, month)
    attributed = sum(sum(x.values()) for x in out.values())
    factor = 1.0
    nat = NATIONAL[IX[month]]
    if scale_to_national and nat and attributed > 0:
        factor = nat / attributed
        for u in UFS:
            for k in LINES:
                out[u][k] *= factor
    return out, factor


def backtest(year, ref_year):
    """Annual error per UF when a sound year is rebuilt from the previous year's shares (no national scaling)."""
    est = {u: 0.0 for u in UFS}
    act = {u: 0.0 for u in UFS}
    for mm in range(1, 13):
        m, r = f"{year}-{mm:02d}", f"{ref_year}-{mm:02d}"
        e, _ = estimate(m, r, scale_to_national=False)
        for u in UFS:
            est[u] += sum(e[u].values())
            act[u] += sum(val(u, k, m) for k in LINES)
    err = {u: round(100 * (est[u] - act[u]) / act[u], 2) for u in UFS}
    absolute = sorted(abs(x) for x in err.values())
    return {"year": year, "reference_year": ref_year, "median_abs_error_pct": absolute[len(absolute) // 2],
            "max_abs_error_pct": absolute[-1], "error_pct_by_uf": err}


months = [m for m in MONTHS if STATUS[IX[m]] is not None and broken(m)]
uf = {u: {"total": [], "by_tax": {k: [] for k in LINES}} for u in UFS}
refs, factors = {}, {}
for m in months:
    ref = reference(m)
    e, factor = estimate(m, ref)
    refs[m], factors[m] = ref, round(factor, 6)
    for u in UFS:
        for k in LINES:
            uf[u]["by_tax"][k].append(round(e[u][k], 2))
        uf[u]["total"].append(round(sum(e[u].values()), 2))

# Municipalities of each state with a municipal series, 2025 (annual file, same break): each municipality keeps its
# reported share of the state, scaled to the state's estimated 2025 total.
municipal_2025 = {}
for path in MUNI:
    scm = json.loads(path.read_text(encoding="utf-8")); u = scm["uf"]
    reported = sum((m["federal_revenue_annual"].get("2025") or 0) for m in scm["municipalities"].values())
    est = sum((F["uf"][u]["federal_revenue"]["total"][IX[f"2025-{mm:02d}"]] or 0) for mm in range(1, 13) if f"2025-{mm:02d}" not in refs)
    est += sum(uf[u]["total"][months.index(m)] for m in months if m.startswith("2025"))
    municipal_2025[f"{u.lower()}_municipal_2025"] = {
        "reported_sum": round(reported, 2), "state_estimate": round(est, 2), "scale": round(est / reported, 6) if reported else None,
        "method": f"Cada município mantém a sua participação publicada dentro {'do' if u == 'RS' else 'de'} {u} em 2025, aplicada ao total estimado do estado."}

out = {
    "description": "Estimativa da arrecadação federal por estado nos meses em que a Receita Federal lançou no DF parte da arrecadação de outros estados. Não substitui o dado publicado, que continua em federal-by-uf-monthly.json.",
    "method": ("Para cada mês com a quebra e cada tributo, cada estado recebe a sua participação naquele tributo no mesmo mês "
               "do último ano sem quebra, aplicada ao total do país desse tributo; depois o mês é ajustado para somar o total "
               "nacional publicado pela Receita."),
    "months": months,
    "reference_month": refs,
    "scale_to_national_total": factors,
    "backtest": [backtest(2024, 2023), backtest(2023, 2022)],
    "uf": uf,
    **municipal_2025,
    "sources": [{"label": "Receita Federal, arrecadação por estado (dado publicado)", "file": "data/series/federal-by-uf-monthly.json"}],
}
OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print("months", months[0], "to", months[-1], len(months))
for b in out["backtest"]:
    print("backtest", b["year"], "from", b["reference_year"], "median", b["median_abs_error_pct"], "max", b["max_abs_error_pct"])
df = sum(uf["DF"]["total"][i] for i, m in enumerate(months) if m.startswith("2025"))
dfr = sum((F["uf"]["DF"]["federal_revenue"]["total"][IX[m]] or 0) for m in months if m.startswith("2025"))
print(f"DF feb-dec 2025: reported {dfr / 1e9:.1f} bi, estimated {df / 1e9:.1f} bi")
for k, v in municipal_2025.items():
    print(k, "scale", v["scale"])
