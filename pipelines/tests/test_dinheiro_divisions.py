"""The divisions of "Como o dinheiro anda" add up (trust spec, B4), over the page's own data file, dinheiro-r1-data.js.

- Each tax's split of R$ 100 adds up to 100%.
- The União lines that the Tesouro's RTN defines as sums close: 3 = 1 minus 2, 5 = 3 minus 4, 2 = 2.1 to 2.6, 4 = 4.1 to 4.4;
  and the 27 states' spending by function adds up to its total. Every value is published rounded to R$ 0,1 bi, so each can be
  off by up to R$ 0,05 bi: an identity of n values holds within n times R$ 0,05 bi (the declared rounding).
- Every source has a URL.
Controls: one part of a split with 1 percentage point more, and one União line R$ 1 bi off, must fail.
"""
import copy
import json
import unittest
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "docs" / "superpowers" / "previews" / "assets" / "dinheiro-r1-data.js"
HALF_STEP = Decimal("0.05")


def load():
    text = DATA.read_text(encoding="utf-8")
    return json.loads(text[text.index("{"):text.rindex("}") + 1], parse_float=Decimal)


def problems(d):
    out = []
    for t in d["taxes"]:
        total = sum((Decimal(str(p[1])) for p in t["split"]), Decimal(0))
        if abs(total - 100) > Decimal("0.0001"):
            out.append(f"tax {t['id']}: the split adds up to {total}%")
    u = {k: Decimal(str(v["bi"])) for k, v in d["union"].items()}
    identities = [("3 = 1 - 2", u["3"], u["1"] - u["2"], 3), ("5 = 3 - 4", u["5"], u["3"] - u["4"], 3),
                  ("2 = 2.1 to 2.6", u["2"], sum((u[f"2.{i}"] for i in range(1, 7)), Decimal(0)), 7),
                  ("4 = 4.1 to 4.4", u["4"], sum((u[f"4.{i}"] for i in range(1, 5)), Decimal(0)), 5)]
    spend = [Decimal(str(x[1])) for x in d["states_spending"]]
    identities.append(("the 27 states' spending", Decimal(str(d["states_spending_total"])), sum(spend, Decimal(0)), len(spend) + 1))
    for name, total, parts, n in identities:
        if abs(total - parts) > HALF_STEP * n:
            out.append(f"{name}: {total} against {parts}, beyond the rounding of {n} values")
    out += [f"source without a URL: {s['name']}" for s in d["sources"] if not s.get("url")]
    return out


class DinheiroDivisionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load()

    def test_every_division_adds_up(self):
        self.assertEqual(len(self.data["taxes"]), 8)
        self.assertEqual(len(self.data["states_spending"]), 27)
        self.assertEqual(problems(self.data), [])

    def test_control_one_percentage_point_more_fails(self):
        d = copy.deepcopy(self.data)
        d["taxes"][0]["split"][0][1] += 1
        self.assertTrue(any(p.startswith(f"tax {d['taxes'][0]['id']}") for p in problems(d)))

    def test_control_a_union_line_one_billion_off_fails(self):
        d = copy.deepcopy(self.data)
        d["union"]["4.2"]["bi"] += 1
        self.assertTrue(any(p.startswith("4 = 4.1 to 4.4") for p in problems(d)))


if __name__ == "__main__":
    unittest.main()
