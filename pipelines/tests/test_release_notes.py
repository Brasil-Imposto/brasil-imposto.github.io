"""Release notes (D190, trust spec G3): a day's notes cite every pull request merged into main that day, in Brasília time,
and nothing else. Controls: a pull request merged into staging, one merged into main the day before (in Brasília, though the
same day in UTC) and one closed without merging are planted in the list and must stay out; dropping a pull request of the
day must make the check fail.
"""
import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("release_notes", Path(__file__).resolve().parents[2] / "docs/superpowers/tools/release-notes.py")
rn = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rn)


def pr(n, merged, base="main", title=None):
    return {"number": n, "title": title or f"task {n}", "merged_at": merged, "base": {"ref": base}}


DAY = [pr(105, "2026-10-25T18:16:00Z"), pr(100, "2026-10-25T18:17:00Z"), pr(109, "2026-10-25T18:22:00Z")]
PLANTED = [pr(118, "2026-10-25T18:30:00Z", base="staging"),  # into staging: not production
           pr(97, "2026-10-25T02:30:00Z"),                      # 23:30 of 2026-10-24 in Brasília
           pr(98, None)]                                        # closed without merging


def cited(text):
    return {int(n) for n in __import__("re").findall(r"\(#(\d+)\)", text)}


class ReleaseNotesTest(unittest.TestCase):
    def test_the_day_cites_every_pull_request_merged_into_main(self):
        self.assertEqual(cited(rn.notes("2026-10-25", DAY + PLANTED)), {105, 100, 109})

    def test_control_the_planted_pull_requests_stay_out(self):
        text = rn.notes("2026-10-25", DAY + PLANTED)
        for n in (118, 97, 98):
            self.assertNotIn(f"(#{n})", text)
        self.assertEqual(cited(rn.notes("2026-10-24", DAY + PLANTED)), {97})

    def test_control_a_missing_pull_request_is_caught(self):
        self.assertNotEqual(cited(rn.notes("2026-10-25", DAY[:-1] + PLANTED)), {105, 100, 109})

    def test_changelog_one_section_per_day_newest_first(self):
        text = rn.changelog(DAY + PLANTED)
        self.assertEqual(__import__("re").findall(r"^## (\S+)$", text, __import__("re").M), ["2026-10-25", "2026-10-24"])

    def test_next_version_one_minor_per_day(self):
        self.assertEqual(rn.next_version(["v1.0.0"]), "v1.1.0")
        self.assertEqual(rn.next_version(["v1.0.0", "v1.1.0", "v1.2.0", "something"]), "v1.3.0")


if __name__ == "__main__":
    unittest.main()
