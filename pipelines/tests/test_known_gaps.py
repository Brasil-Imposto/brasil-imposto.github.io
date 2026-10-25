"""The unexplained differences, listed and locked (trust spec, item A4).

The monthly checks of the trust audit (section 1.4 and DF-4), over data/ only:
  - states_vs_sum_of_ufs: the 27 state totals of a month against the states' sum the file keeps;
  - sum_of_ufs_plus_unattributed_vs_national: that sum plus the part without a state against the Receita's national total;
  - negative_unattributed: a month whose part without a state is below zero (the states add up to more than the country);
  - tax_sum_registered and tax_sum_estimate: a state's taxes against its total, in the Receita's file and in the estimate.
Every difference found must be in data/series/known-gaps.json with its value, and every item of that file must still happen:
a new difference fails, and so does an item that no longer happens, so the list can only shrink.

Controls: R$ 1 planted in one state's total in one month must show as a new difference in the monthly checks, and an item
listed that never happened must show as no longer happening.
"""
import json
import sys
import unittest
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KNOWN = REPO / "data" / "series" / "known-gaps.json"
CENT = Decimal("0.01")
CHECKS = ("states_vs_sum_of_ufs", "sum_of_ufs_plus_unattributed_vs_national", "negative_unattributed",
          "tax_sum_registered", "tax_sum_estimate")


def cent(x):
    return Decimal(x).quantize(CENT, ROUND_HALF_EVEN)


def load(path):
    return json.loads((REPO / path).read_text(encoding="utf-8"), parse_float=Decimal)


def current(plant=None):
    """Every difference of the monthly checks, as {check: {"<month>" or "<month> <UF>": "<difference in reais>"}}.
    plant=(uf, month) adds R$ 1 to that state's total in that month first (the control)."""
    F = load("data/series/federal-by-uf-monthly.json")
    E = load("data/series/federal-revenue-uf-estimated.json")
    ufs, N, fm = sorted(F["uf"]), F["national"], F["months"]
    fi, ei = {m: i for i, m in enumerate(fm)}, {m: i for i, m in enumerate(E["months"])}
    if plant:
        uf, m = plant
        F["uf"][uf]["federal_revenue"]["total"][fi[m]] += 1
    out = {c: {} for c in CHECKS}
    out["_months"] = 0
    for m in fm:
        i = fi[m]
        tot, sou, na = (N[k][i] for k in ("federal_revenue_total_receita", "federal_revenue_sum_of_ufs",
                                          "federal_revenue_not_attributed_to_any_uf"))
        if tot is None or sou is None:
            continue
        out["_months"] += 1
        s27 = sum((F["uf"][u]["federal_revenue"]["total"][i] or 0 for u in ufs), Decimal(0))
        if cent(s27) != cent(sou):
            out["states_vs_sum_of_ufs"][m] = str(cent(s27) - cent(sou))
        if na is not None and cent(sou + na) != cent(tot):
            out["sum_of_ufs_plus_unattributed_vs_national"][m] = str(cent(sou + na) - cent(tot))
        if na is not None and cent(na) < 0:
            out["negative_unattributed"][m] = str(cent(na))
        for u in ufs:
            R = F["uf"][u]["federal_revenue"]
            if R["total"][i] is None:
                continue
            s = sum((R["by_tax"][k][i] or 0 for k in R["by_tax"]), Decimal(0))
            if cent(s) != cent(R["total"][i]):
                out["tax_sum_registered"][f"{m} {u}"] = str(cent(s) - cent(R["total"][i]))
    for m in E["months"]:
        j = ei[m]
        for u in ufs:
            R = E["uf"][u]
            if R["total"][j] is None:
                continue
            s = sum((R["by_tax"][k][j] or 0 for k in R["by_tax"]), Decimal(0))
            if cent(s) != cent(R["total"][j]):
                out["tax_sum_estimate"][f"{m} {u}"] = str(cent(s) - cent(R["total"][j]))
    return out


def compare(found, known):
    """(new, stale): differences found and not listed (or listed with another value), and listed items no longer found."""
    new, stale = [], []
    for c in CHECKS:
        listed = known["checks"][c]["gaps"]
        new += [(c, k, v, listed.get(k)) for k, v in found[c].items() if listed.get(k) != v]
        stale += [(c, k, v) for k, v in listed.items() if k not in found[c]]
    return new, stale


class KnownGapsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.known = json.loads(KNOWN.read_text(encoding="utf-8"))
        cls.found = current()
        cls.new, cls.stale = compare(cls.found, cls.known)
        n = sum(len(cls.known["checks"][c]["gaps"]) for c in CHECKS)
        print(f"\n[A4] {cls.found['_months']} months checked, {n} known differences, {len(cls.new)} new, {len(cls.stale)} no "
              f"longer happening", file=sys.stderr)

    def test_every_check_is_listed(self):
        self.assertEqual(sorted(self.known["checks"]), sorted(CHECKS))
        self.assertGreater(self.found["_months"], 80)

    def test_no_new_difference(self):
        self.assertEqual(self.new[:10], [], "a difference that is not in data/series/known-gaps.json (check, key, found, listed)")

    def test_no_listed_difference_is_gone(self):
        self.assertEqual(self.stale[:10], [], "remove these items from data/series/known-gaps.json: they no longer happen")

    def test_every_item_says_where_it_comes_from(self):
        for c in CHECKS:
            self.assertTrue(self.known["checks"][c]["origin"].strip(), c)
            self.assertTrue(self.known["checks"][c]["explanation"].strip(), c)

    def test_control_one_real_planted_in_a_state_fails(self):
        new, _ = compare(current(plant=("SP", "2023-05")), self.known)
        self.assertIn(("states_vs_sum_of_ufs", "2023-05"), [(c, k) for c, k, _, _ in new], new[:5])

    def test_control_a_listed_item_that_never_happened_fails(self):
        known = json.loads(json.dumps(self.known))
        known["checks"]["states_vs_sum_of_ufs"]["gaps"]["1999-01"] = "0.01"
        _, stale = compare(self.found, known)
        self.assertIn(("states_vs_sum_of_ufs", "1999-01", "0.01"), stale)


if __name__ == "__main__":
    unittest.main()
