"""The per-entity JSON files of phase B0 (D151): exported from data/ at build time, never committed.
- every file passes its schema (schemas/), the export writes the expected number of entities;
- value parity: every number in an entity file equals the number in data/ it comes from;
- the checks catch what they must (a changed value, a number without a source, a key that is not in the schema, a
  missing file): each is planted on a copy and must be reported.
Run: uv run --locked python -m unittest discover -s pipelines/tests"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "pipelines" / "export"))
import build_entities  # noqa: E402


def data(rel):
    return json.loads((REPO / "data" / rel).read_text(encoding="utf-8"))


def parity(entities):
    """Every exported number against its value in data/; returns the differences."""
    bad = []
    monthly = data("series/federal-by-uf-monthly.json")
    pop = data("series/population.json")
    for e in entities:
        if e["type"] == "state":
            src = monthly["uf"][e["id"]]
            expected = {"federal_revenue": src["federal_revenue"]["total"], "transfers": src["transfers"]["total"],
                        "bolsa_familia": src["bolsa_familia"], "bpc": src["bpc"], "inss": src["inss"]}
            for k, values in expected.items():
                s = e["series"][k]
                if s["values"] != values or s["months"] != monthly["months"]:
                    bad.append(f"{e['id']}.{k}")
            p = pop["uf"][e["id"]]["population"]
            if e["population"]["values"] != [p[str(y)] for y in e["population"]["years"]]:
                bad.append(f"{e['id']}.population")
        elif e["type"] == "municipality":
            p = pop[f"{e['uf'].lower()}_municipalities"][e["id"]]["population"]
            if e["population"]["values"] != [p[str(y)] for y in e["population"]["years"]]:
                bad.append(f"{e['id']}.population")
        elif e["type"] == "country":
            s = e["series"]["federal_revenue"]
            if s["values"] != monthly["national"]["federal_revenue_total_receita"] or s["months"] != monthly["months"]:
                bad.append("BR.federal_revenue")
    return bad


class EntitiesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        cls.written = build_entities.build(cls.out)
        cls.entities = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(cls.out.rglob("*.json"))]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_counts(self):
        by = {}
        for e in self.entities:
            by[e["type"]] = by.get(e["type"], 0) + 1
        pop = data("series/population.json")
        self.assertEqual(by.get("country"), 1)
        self.assertEqual(by.get("state"), 27)
        self.assertEqual(by.get("municipality"), len(pop["sc_municipalities"]) + len(pop["rs_municipalities"]))
        self.assertEqual(by.get("case"), len(list((REPO / "data" / "cases").glob("*.json"))))
        self.assertGreater(by.get("person", 0), 600)
        self.assertEqual(len(self.entities), self.written)

    def test_every_file_passes_its_schema(self):
        problems = [p for e in self.entities for p in build_entities.validate(e)]
        self.assertEqual(problems, [])

    def test_value_parity(self):
        self.assertEqual(parity(self.entities), [])

    def test_every_series_has_a_source_and_matching_lengths(self):
        for e in self.entities:
            for name, s in list(e.get("series", {}).items()) + ([("population", e["population"])] if "population" in e else []):
                self.assertIn("url", s["source"], f"{e['id']}.{name}")
                axis = s.get("months", s.get("years"))
                self.assertEqual(len(axis), len(s["values"]), f"{e['id']}.{name}")

    # the checks above must catch what they are for
    def test_control_changed_value_is_caught(self):
        planted = copy.deepcopy(self.entities)
        st = next(e for e in planted if e["type"] == "state")
        st["series"]["transfers"]["values"][5] += 0.01
        self.assertEqual(parity(planted), [f"{st['id']}.transfers"])

    def test_control_number_without_source_is_caught(self):
        st = copy.deepcopy(next(e for e in self.entities if e["type"] == "state"))
        del st["series"]["inss"]["source"]
        self.assertTrue(build_entities.validate(st))

    def test_control_unknown_key_is_caught(self):
        st = copy.deepcopy(next(e for e in self.entities if e["type"] == "state"))
        st["valor"] = 1
        self.assertTrue(build_entities.validate(st))

    def test_control_missing_file_is_caught(self):
        fewer = [e for e in self.entities if not (e["type"] == "state" and e["id"] == "SC")]
        self.assertNotEqual(sum(e["type"] == "state" for e in fewer), 27)


if __name__ == "__main__":
    unittest.main()
