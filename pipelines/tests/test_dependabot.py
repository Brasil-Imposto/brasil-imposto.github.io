"""The Dependabot configuration is valid (trust spec, D2): .github/dependabot.yml validates against the published Dependabot
schema (a copy in fixtures/, from https://json.schemastore.org/dependabot-2.0.json, read on 2026-10-25), covers the three
ecosystems of the repository and sends every pull request to staging.
The file is read by a small reader for the plain YAML it uses (mappings, lists, quoted scalars), since the locked environment has
no YAML package. Control: an ecosystem with a wrong name must fail the schema.
"""
import json
import re
import unittest
from pathlib import Path

import jsonschema

REPO = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((Path(__file__).parent / "fixtures" / "dependabot-2.0.schema.json").read_text(encoding="utf-8"))


def read_yaml(text):
    """The YAML subset of dependabot.yml: block mappings, block lists, scalars (quoted or not, integers)."""
    lines = [(len(l) - len(l.lstrip()), l.strip()) for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]

    def scalar(s):
        s = s.strip()
        if s[:1] in "\"'":
            return s[1:-1]
        return int(s) if re.fullmatch(r"-?\d+", s) else s

    def block(i, indent):
        if lines[i][1].startswith("- "):
            out = []
            while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
                rest = lines[i][1][2:]
                if ":" in rest and not rest[:1] in "\"'":
                    lines[i] = (indent + 2, rest)
                    item, i = block(i, indent + 2)
                else:
                    item, i = scalar(rest), i + 1
                out.append(item)
            return out, i
        out = {}
        while i < len(lines) and lines[i][0] == indent and not lines[i][1].startswith("- "):
            key, _, value = lines[i][1].partition(":")
            if value.strip():
                out[key.strip()], i = scalar(value), i + 1
            else:
                out[key.strip()], i = block(i + 1, lines[i + 1][0])
        return out, i

    return block(0, lines[0][0])[0]


class DependabotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = read_yaml((REPO / ".github" / "dependabot.yml").read_text(encoding="utf-8"))

    def test_valid_against_the_published_schema(self):
        jsonschema.validate(self.config, SCHEMA)

    def test_the_three_ecosystems_weekly_into_staging(self):
        ups = self.config["updates"]
        self.assertEqual(sorted((u["package-ecosystem"], u["directory"]) for u in ups),
                         [("github-actions", "/"), ("npm", "/site"), ("uv", "/")])
        for u in ups:
            self.assertEqual((u["target-branch"], u["schedule"]["interval"]), ("staging", "weekly"))
            self.assertTrue(u["groups"], u["package-ecosystem"])
        self.assertTrue((REPO / "uv.lock").exists() and (REPO / "site" / "package-lock.json").exists())

    def test_control_a_wrong_ecosystem_fails_the_schema(self):
        bad = json.loads(json.dumps(self.config))
        bad["updates"][0]["package-ecosystem"] = "github-action"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad, SCHEMA)


if __name__ == "__main__":
    unittest.main()
