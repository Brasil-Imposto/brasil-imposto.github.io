"""No money counted twice between "Voltou" and the federal spending (item 6 of #66; report of the phase 1 complement, section 5).

A state's "Voltou" adds the transfers, Bolsa Família, INSS, BPC and FCDF by destination, plus the federal spending located there
(the two-step rule). The same money would count twice if the spending kept those flows. The data shows they were taken out:
  - every yearly file of the two-step rule and the series file state the rule: the five flows by destination;
  - every yearly file records what its scope took out of the spending for each of the four programs found in the Portal, as a
    ratio over the series "Voltou" uses, and the ratio sits inside the builder's band (a program left in the spending, or taken
    out twice, falls outside it); its own checks passed with zero differences, the flows of the states equal to the series;
  - in the series file, a state's spending is only the eight spending kinds, which add up to it in every month, so no flow
    counted by destination hides in it.
The sum of "Voltou" itself, each flow once, is checked to the cent by test_df_balance.py (A1 and B1).

Controls: an INSS ratio at half of the series, a ninth kind named for a flow, and kinds that miss the spending by R$ 1 must fail.
"""
import ast
import copy
import json
import unittest
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SERIES = REPO / "data" / "series" / "federal-spending-two-step-by-uf.json"
BUILDER = REPO / "pipelines" / "ug" / "build_two_step_balance.py"
RULE = "Transfers, Bolsa Família, INSS, BPC and FCDF by destination"
KINDS = {"civil_active_and_other", "civil_retirees_and_pensions", "military", "operating_costs", "investment", "benefits_to_people",
         "special_charges", "economic_subsidies"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_float=Decimal)


def builder_bands():
    """The BANDS of build_two_step_balance.py, read from its source (the test never copies them)."""
    for node in ast.parse(BUILDER.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "BANDS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("BANDS not found in build_two_step_balance.py")


def year_problems(name, d, bands):
    c, out = d["check"], []
    if RULE not in d["rule"]:
        out.append(f"{name}: the rule does not count the five flows by destination")
    if not c.get("passed") or any(v != 0 for v in c["differences"].values()):
        out.append(f"{name}: its own checks did not pass with zero differences")
    ratios = c.get("scope_exclusions_over_series") or {}
    for k, (_, lo, hi) in bands.items():
        r = ratios.get(k)
        if r is None or not (lo <= r <= hi):
            out.append(f"{name}: {k} taken out of the spending at {r} of the series, outside {lo} to {hi}")
    if c.get("scope_out_of_band"):
        out.append(f"{name}: scope_out_of_band {c['scope_out_of_band']}")
    return out


def series_problems(T):
    out = [] if RULE in T["rule"] else ["the series file: the rule does not count the five flows by destination"]
    for uf, u in T["uf"].items():
        extra = set(u["executive_by_kind"]) - KINDS
        if extra:
            out.append(f"{uf}: spending kinds {sorted(extra)}")
        for i, m in enumerate(T["months"]):
            if u["executive"][i] is None:
                continue
            s = sum((v[i] or 0 for v in u["executive_by_kind"].values()), Decimal(0))
            if abs(s - u["executive"][i]) > Decimal("0.005"):
                out.append(f"{uf} {m}: the kinds add up to {s}, the spending is {u['executive'][i]}")
    return out


class DoubleCountingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bands = builder_bands()
        cls.years = {p.name: load(p) for p in sorted((REPO / "data" / "ug").glob("two-step-balance-*.json"))}
        cls.series = load(SERIES)

    def test_every_year_of_the_series_has_its_file(self):
        self.assertEqual(sorted(n[17:21] for n in self.years), sorted(self.series["years"]) if self.series.get("years") else
                         sorted({m[:4] for m in self.series["months"]}))

    def test_the_four_programs_were_taken_out_of_the_spending_every_year(self):
        self.assertEqual(sorted(self.bands), ["bolsa_familia", "bpc", "fcdf", "inss"])
        problems = [p for n, d in self.years.items() for p in year_problems(n, d, self.bands)]
        self.assertEqual(problems, [])

    def test_the_spending_holds_only_its_eight_kinds(self):
        self.assertEqual(series_problems(self.series), [])

    def test_control_inss_left_in_the_spending_fails(self):
        name, d = next(iter(self.years.items()))
        d = copy.deepcopy(d)
        d["check"]["scope_exclusions_over_series"]["inss"] = 0.5
        self.assertTrue(any("inss" in p for p in year_problems(name, d, self.bands)))

    def test_control_a_flow_hidden_in_the_spending_fails(self):
        T = copy.deepcopy(self.series)
        T["uf"]["SP"]["executive_by_kind"]["transfers"] = [Decimal(0)] * len(T["months"])
        self.assertTrue(any(p.startswith("SP: spending kinds") for p in series_problems(T)))

    def test_control_kinds_that_miss_the_spending_fail(self):
        T = copy.deepcopy(self.series)
        i = next(i for i, v in enumerate(T["uf"]["SP"]["executive"]) if v is not None)
        T["uf"]["SP"]["executive"][i] += 1
        self.assertTrue(any(p.startswith(f"SP {T['months'][i]}") for p in series_problems(T)))


if __name__ == "__main__":
    unittest.main()
