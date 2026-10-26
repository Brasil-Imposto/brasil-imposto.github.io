"""The feature switches (spec BRASIL-IMPOSTO_SPEC_staging_2026-10-23, section 2): data/features.json follows its schema, each key
appears once, and the one switch today is apoie, on in staging. Every rule has a planted failure."""
import copy
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "docs" / "superpowers" / "tools"))
import features  # noqa: E402

SCHEMA = json.loads((REPO / "schemas" / "features.schema.json").read_text(encoding="utf-8"))


def committed():
    return json.loads(features.PATH.read_text(encoding="utf-8"))


def schema_errors(data):
    return [e.message for e in Draft202012Validator(SCHEMA).iter_errors(data)]


class FeaturesFileTest(unittest.TestCase):
    def test_the_file_follows_its_schema(self):
        Draft202012Validator.check_schema(SCHEMA)
        self.assertEqual(schema_errors(committed()), [])
        self.assertEqual(features.problems(committed()), [])

    def test_apoie_is_on_in_staging(self):
        d = committed()
        self.assertEqual([f["key"] for f in d["features"]], ["apoie", "trade", "rede"])
        self.assertIs(features.on("apoie", "staging", d), True)
        self.assertIsInstance(features.on("apoie", "production", d), bool)

    def test_trade_is_on_in_staging_only(self):
        # O que o Brasil vende on Início, only in staging (D159, spec home-trim); its issue is the one the switch was opened for
        d = committed()
        self.assertIs(features.on("trade", "staging", d), True)
        self.assertIs(features.on("trade", "production", d), False)
        self.assertEqual(next(f["issue"] for f in d["features"] if f["key"] == "trade"), 57)

    def test_control_a_bad_file_fails_the_schema_and_the_module(self):
        cases = {"a key in Portuguese capitals": lambda d: d["features"][0].update(key="Apoie"),
                 "issue as text": lambda d: d["features"][0].update(issue="46"),
                 "staging as text": lambda d: d["features"][0].update(staging="yes"),
                 "a field outside the schema": lambda d: d["features"][0].update(enabled=True)}
        for name, change in cases.items():
            with self.subTest(case=name):
                d = copy.deepcopy(committed()); change(d)
                self.assertTrue(schema_errors(d), name)
                if name != "a field outside the schema":
                    self.assertTrue(features.problems(d), name)

    def test_control_a_key_twice_fails(self):
        d = copy.deepcopy(committed()); d["features"].append(copy.deepcopy(d["features"][0]))
        self.assertEqual(schema_errors(d), [], "JSON Schema cannot see it, so the module must")
        self.assertTrue(any("appears twice" in p for p in features.problems(d)))

    def test_control_an_unknown_key_or_profile_stops_the_build(self):
        with self.assertRaises(SystemExit):
            features.on("no-such-feature", "production", committed())
        with self.assertRaises(SystemExit):
            features.on("apoie", "preview", committed())


if __name__ == "__main__":
    unittest.main()
