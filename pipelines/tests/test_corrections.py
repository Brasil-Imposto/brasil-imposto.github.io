"""The public corrections log (Phase 2 spec, P5; D172, question 7): data/corrections.json follows its schema, every entry cites
the pull request that made the correction and an official source, and the entries are newest first. The README and the "Pedir
correção" form point at the log. Controls: an entry without its pull request, one without a source link and two entries out
of order must each fail.
"""
import json
import unittest
from pathlib import Path

import jsonschema

REPO = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((REPO / "schemas" / "corrections.schema.json").read_text(encoding="utf-8"))
LOG = json.loads((REPO / "data" / "corrections.json").read_text(encoding="utf-8"))
# a made-up entry for the tests only; the real log starts empty until the maintainer names its first correction
ENTRY = {"date": "2026-10-05", "page": "Página de teste", "what": "Um número de teste", "before": "R$ 1,00", "after": "R$ 2,00",
         "reason": "Entrada inventada para o teste.", "source": {"label": "Fonte de teste", "url": "https://example.org/"},
         "pull_request": 1}


def problems(log):
    out = [e.message for e in jsonschema.Draft202012Validator(SCHEMA).iter_errors(log)]
    dates = [c.get("date", "") for c in log.get("corrections", [])]
    if dates != sorted(dates, reverse=True):
        out.append("entries are not newest first")
    return out


class CorrectionsTest(unittest.TestCase):
    def test_the_log_follows_its_schema(self):
        self.assertEqual(problems(LOG), [])

    def test_a_full_entry_passes(self):
        self.assertEqual(problems({"corrections": [ENTRY]}), [])

    def test_control_an_entry_without_its_pull_request_fails(self):
        self.assertTrue(problems({"corrections": [{k: v for k, v in ENTRY.items() if k != "pull_request"}]}))

    def test_control_an_entry_without_a_source_link_fails(self):
        self.assertTrue(problems({"corrections": [dict(ENTRY, source={"label": "Tesouro Nacional", "url": "tesouro"})]}))

    def test_control_entries_out_of_order_fail(self):
        self.assertIn("entries are not newest first", problems({"corrections": [dict(ENTRY, date="2026-10-01"), ENTRY]}))

    def test_the_readme_and_the_form_point_at_the_log(self):
        self.assertIn("data/corrections.json", (REPO / "README.md").read_text(encoding="utf-8"))
        self.assertIn("data/corrections.json", (REPO / ".github" / "ISSUE_TEMPLATE" / "data-correction.yml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
