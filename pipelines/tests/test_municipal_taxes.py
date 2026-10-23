"""data/municipal-taxes-2024.json says, state by state, whether every municipality reported (cleanup plan, task 7, P1-24): a
state total with municipalities missing is marked complete: false, so no screen reads it as the whole state."""
import copy
import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data" / "municipal-taxes-2024.json"


def problems(d):
    out = []
    for uf, v in d["by_uf"].items():
        if v.get("complete") is not (v["reported"] == v["municipalities"]):
            out.append(uf)
        if v["reported"] + v["not_reported"] + v["errors"] != v["municipalities"]:
            out.append(uf + " counts")
    return out


class MunicipalTaxesTest(unittest.TestCase):
    def test_every_state_says_whether_it_is_complete(self):
        d = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertEqual(problems(d), [])
        self.assertEqual(sorted(uf for uf, v in d["by_uf"].items() if not v["complete"]),
                         ["AL", "AP", "BA", "DF", "MA", "MT", "PA", "PI", "PR", "RN", "TO"])
        planted = copy.deepcopy(d)  # control: a state with a municipality missing marked complete
        planted["by_uf"]["AL"]["complete"] = True
        self.assertEqual(problems(planted), ["AL"])


if __name__ == "__main__":
    unittest.main()
