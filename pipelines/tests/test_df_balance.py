"""The DF balance checked to the cent on every period of the selector (trust spec, item A1).

Two computations are compared:
  - the page's: df_page.cjs runs the published map's own code (periods.js, serieslayer.js) over the built data bundle;
  - an independent one: Decimal over data/ only, with the rules as the decisions write them (the trust audit's df_recompute.py,
    Appendix B): sent with the estimate of the broken months, the DF cap of D146, received by the two-step rule, the period cut
    at the last month every component has, the broken two-step months out of both sides.
Every DF figure the map shows must match to the cent, and on every complete period the 27 states (DF capped) plus the União
block must equal the official total, with the excess moved to the União and nothing else.

Two controls must fail: R$ 1 more in the DF's Cofins in a month the estimate does not replace, and the cap switched off in the
independent computation.

The bundle is built here (build-cases.py, build-standalone-data.py) because the ci runs these tests before the step that builds
the pages; the test never skips.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "docs" / "superpowers" / "tools"
ASSETS = REPO / "docs" / "superpowers" / "previews" / "assets"
CENT = Decimal("0.01")


def cent(x):
    return None if x is None else Decimal(x).quantize(CENT, ROUND_HALF_EVEN)


def load(path):
    return json.loads((REPO / path).read_text(encoding="utf-8"), parse_float=Decimal)


def recompute(page, plant=None, cap=True):
    """The independent computation; returns the comparison with the page (see the module docstring)."""
    F = load("data/series/federal-by-uf-monthly.json")
    E = load("data/series/federal-revenue-uf-estimated.json")
    TS = load("data/series/federal-spending-two-step-by-uf.json")
    G = load("data/df/gdp-share.json")
    POP = load("data/series/population.json")
    latest = page["latest"]
    UFS = sorted(F["uf"])
    assert len(UFS) == 27 and "DF" in UFS
    share = Decimal(G["gdp_df_thousand_reais"]) / Decimal(G["gdp_brasil_thousand_reais"])
    FM, EM, TM = F["months"], E["months"], TS["months"]
    fi, ei, ti = ({m: i for i, m in enumerate(x)} for x in (FM, EM, TM))
    broken = set(TS.get("broken_months") or {})

    if plant:  # R$ 1 more in one DF tax, in its first registered month that the estimate does not replace
        arr = F["uf"]["DF"]["federal_revenue"]["by_tax"][plant]
        j = next(i for i, m in enumerate(FM) if arr[i] is not None and m not in ei)
        arr[j] += 1
        F["uf"]["DF"]["federal_revenue"]["total"][j] += 1

    def rev(uf, m, tax=None):
        if m in ei:
            src = E["uf"][uf]["total"] if tax is None else E["uf"][uf]["by_tax"].get(tax)
            return None if src is None else src[ei[m]]
        src = F["uf"][uf]["federal_revenue"]["total"] if tax is None else F["uf"][uf]["federal_revenue"]["by_tax"][tax]
        return src[fi[m]]

    def last_month(months, get):
        for m in reversed(months):
            if get(m) is not None:
                return m
        return None

    def period_months(key):
        mode, v = key.split(":")
        if mode == "month":
            return [v]
        y0, y1 = (int(v), int(v)) if mode == "year" else map(int, v.split("-"))
        return [f"{y}-{m:02d}" for y in range(y0, y1 + 1) for m in range(1, 13) if f"{y}-{m:02d}" <= latest]

    def end_of(uf):
        u, t = F["uf"][uf], TS["uf"][uf]
        return min([last_month(FM, lambda m: rev(uf, m)),
                    last_month(FM, lambda m: u["transfers"]["total"][fi[m]]),
                    last_month(FM, lambda m: u["inss"][fi[m]]),
                    last_month(FM, lambda m: u["bolsa_familia"][fi[m]]),
                    last_month(TM, lambda m: t["executive"][ti[m]])])

    def total(values):
        vals = [v for v in values if v is not None]
        return (sum(vals, Decimal(0)) if vals else None), len(vals)

    def state(uf, months_all):
        end = end_of(uf)
        months = [m for m in months_all if m <= end and m not in broken]
        u, t = F["uf"][uf], TS["uf"][uf]
        out = {"months": months}
        sent_reg, n = total(rev(uf, m) for m in months)
        out["sent_registered"], out["sent_complete"] = sent_reg, n == len(months)
        out["by_tax"] = {k: total(rev(uf, m, k) for m in months)[0] for k in u["federal_revenue"]["by_tax"]}
        for k, arr in (("transfers", u["transfers"]["total"]), ("bolsa", u["bolsa_familia"]), ("inss", u["inss"]), ("bpc", u["bpc"])):
            out[k], out[k + "_n"] = total(arr[fi[m]] if m in fi else None for m in months)
        parts, full = {}, True
        for k in ("executive", "other_branches", "fcdf"):
            parts[k], n = total(t[k][ti[m]] if m in ti else None for m in months)
            full = full and n == len(months) and len(months) > 0
        central = Decimal(0)
        for y in sorted({m[:4] for m in months}):
            ms = [m for m in months if m.startswith(y)]
            mte = TS["mte_annual"].get(y)
            if mte and len(ms) == 12:
                central += mte["uf"][uf]["unemployment_insurance"] + mte["uf"][uf]["wage_bonus"]
            c, _ = total(t["central_benefits_localized"][ti[m]] if m in ti else None for m in ms)
            central += c or 0
        out["two_step_complete"] = full
        out["fcdf"] = parts["fcdf"] if full else None
        out["fed_spending"] = parts["executive"] + parts["other_branches"] + central if full else None
        out["received"] = (out["transfers"] + (out["bolsa"] or 0) + (out["inss"] or 0) + (out["bpc"] or 0) + parts["fcdf"]
                           + out["fed_spending"]) if (out["transfers"] is not None and full) else None
        return out

    def df_excess(months):
        """D146, per tax: the DF keeps at most its GDP share of that tax in the 27 states; cap=False is the control."""
        if not cap:
            return Decimal(0)
        excess = Decimal(0)
        for k in F["uf"]["DF"]["federal_revenue"]["by_tax"]:
            df = total(rev("DF", m, k) for m in months)[0] or Decimal(0)
            br = sum((total(rev(uf, m, k) for m in months)[0] or Decimal(0) for uf in UFS), Decimal(0))
            excess += df - min(df, share * br)
        return excess

    def pop_of(uf, years):
        by = {int(y): v for y, v in POP["uf"][uf]["population"].items() if v is not None}
        want = years[-1]
        return by[sorted(by, key=lambda y: (abs(y - want), -y))[0]]

    rep = {"periods": 0, "df_ok": 0, "fields_compared": 0, "gaps": [], "union_checks": 0, "union_gaps": []}
    for key, P in page["periods"].items():
        rep["periods"] += 1
        months_all = period_months(key)
        assert months_all == P["r_months"], (key, "the period's months differ from the page's selector")
        S = {uf: state(uf, months_all) for uf in UFS}
        d = S["DF"]
        ok = (len(d["months"]) > 0 and d["sent_complete"] and d["transfers_n"] == len(d["months"]) and d["two_step_complete"]
              and not [m for m in d["months"] if m in fi and "broken" in str(F["national"]["federal_revenue_month_status"][fi[m]]) and m not in ei])
        excess = df_excess(d["months"]) if d["sent_registered"] is not None else None
        sent = d["sent_registered"] - excess if excess is not None else None
        balance = sent - d["received"] if ok else None
        pop = pop_of("DF", sorted({int(m[:4]) for m in months_all}))
        mine = {"sent": sent, "sentRegistered": d["sent_registered"], "excess": excess, "received": d["received"],
                "transfers": d["transfers"], "bolsa": d["bolsa"], "inss": d["inss"], "bpc": d["bpc"], "fcdf": d["fcdf"],
                "fedSpending": d["fed_spending"], "balance": balance, "months": len(d["months"]), "ok": ok,
                "perPersonMonth": balance / pop / len(d["months"]) if ok else None}
        theirs = dict(P["df"])
        theirs["excess"] = (P["df"].get("dfEstimate") or {}).get("excess")
        rep["df_ok"] += bool(ok)
        for f, v in mine.items():
            t = theirs.get(f)
            rep["fields_compared"] += 1
            if f in ("ok", "months"):
                if v != t:
                    rep["gaps"].append([key, f, str(v), str(t)])
                continue
            if f == "perPersonMonth":
                q = Decimal("0.0001")
                a, b = (None if v is None else v.quantize(q)), (None if t is None else Decimal(repr(t)).quantize(q))
            else:
                a, b = cent(v), cent(Decimal(repr(t)) if t is not None else None)
            if a != b:
                rep["gaps"].append([key, f, str(a), str(b)])
        for k, v in (P["df"].get("byTax") or {}).items():
            rep["fields_compared"] += 1
            if cent(d["by_tax"][k]) != cent(Decimal(repr(v)) if v is not None else None):
                rep["gaps"].append([key, f"byTax.{k}", str(cent(d["by_tax"][k])), str(v)])
        # the União block after the move: 27 states (DF capped) + União = official total; the excess moved, nothing else
        if ok and all(S[u]["months"] == d["months"] and S[u]["sent_registered"] is not None for u in UFS):
            ms = d["months"]
            official = total(TS["union"]["official_revenue"][ti[m]] for m in ms)[0]
            states_reg = sum((S[u]["sent_registered"] for u in UFS), Decimal(0))
            states_capped = states_reg - excess
            union_before, union_after = official - states_reg, official - states_capped
            rep["union_checks"] += 1
            if cent(states_capped + union_after) != cent(official) or cent(union_after - union_before) != cent(excess) or union_after < 0:
                rep["union_gaps"].append([key, str(cent(official)), str(cent(states_capped)), str(cent(union_after)), str(cent(excess))])
    return rep


class DFBalanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        node = shutil.which("node")
        if not node:
            raise RuntimeError("node is needed to run the page's own code (the ci runner has it)")
        for b in ("build-cases.py", "build-standalone-data.py"):   # the bundle the page reads, built from data/
            subprocess.run([sys.executable, str(TOOLS / b)], check=True, cwd=REPO, stdout=subprocess.DEVNULL)
        cls.tmp = tempfile.TemporaryDirectory()
        out = Path(cls.tmp.name) / "page-df.json"
        subprocess.run([node, str(Path(__file__).with_name("df_page.cjs")), str(ASSETS), str(out)], check=True, cwd=REPO)
        cls.page = json.loads(out.read_text(encoding="utf-8"))
        cls.report = recompute(cls.page)
        r = cls.report
        print(f"\n[A1] {r['periods']} periods, {r['fields_compared']} DF figures compared to the cent, {r['df_ok']} periods with a "
              f"complete balance, {r['union_checks']} União checks; differences: {len(r['gaps'])} DF, {len(r['union_gaps'])} União",
              file=sys.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_period_of_the_selector_is_checked(self):
        self.assertGreaterEqual(self.report["periods"], 100)
        self.assertGreater(self.report["df_ok"], 90)
        self.assertGreater(self.report["union_checks"], 90)

    def test_every_df_figure_matches_to_the_cent(self):
        self.assertEqual(self.report["gaps"][:10], [])

    def test_the_union_block_adds_up_after_the_cap(self):
        self.assertEqual(self.report["union_gaps"][:10], [])

    def test_control_one_real_more_in_the_df_cofins_fails(self):
        r = recompute(self.page, plant="cofins")
        self.assertTrue(r["gaps"], "a real more in the DF's Cofins must show as a difference")
        self.assertTrue(any(f in ("sentRegistered", "byTax.cofins") for _, f, _, _ in r["gaps"]), r["gaps"][:5])

    def test_control_the_cap_switched_off_fails(self):
        r = recompute(self.page, cap=False)
        self.assertTrue(r["gaps"], "the independent computation without the cap must disagree with the page")
        self.assertTrue(any(f in ("sent", "excess", "balance") for _, f, _, _ in r["gaps"]), r["gaps"][:5])


if __name__ == "__main__":
    unittest.main()
