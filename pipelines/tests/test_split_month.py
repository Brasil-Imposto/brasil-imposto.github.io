"""The monthly split (spec apoie 11.2): only issues closed in the month (Brasília time) by a merged pull request, with one difficulty
label put before the assignment and one assignee, count; shares in whole cents, rounded down, the rest kept. Controls: an unlabeled
issue, a label put after the assignment and an issue closed without a merged pull request, each counted, must change the result; one
cent more in a share must fail the sum."""
import copy
import json
import unittest
from pathlib import Path

from pipelines.support import ledger, split_month as sm

CASE = json.loads((Path(__file__).parent / "fixtures" / "split" / "issues-2026-12.json").read_text(encoding="utf-8"))
# the second month of spec 11.6: weights 1, 2 and 3 between two people and the maintainer; with December's #23, closed on
# January 1st in Brasília
JANUARY = CASE + json.loads((Path(__file__).parent / "fixtures" / "split" / "issues-2027-01.json").read_text(encoding="utf-8"))


class SplitTest(unittest.TestCase):
    def test_december(self):
        r = sm.compute(CASE, "2026-12", 50000)
        self.assertEqual([(s["login"], s["points"], s["amount_cents"]) for s in r["shares"]], [("pessoa-a", 5, 41666), ("pessoa-b", 1, 8333)])
        self.assertEqual(r["kept_cents"], 1)
        self.assertEqual(sum(s["amount_cents"] for s in r["shares"]) + r["kept_cents"], r["pool_cents"])
        self.assertEqual(sorted(x["number"] for x in r["skipped"]), [20, 21, 22])   # #23 is January's, not skipped here

    def test_january_two_people_and_the_maintainer(self):
        r = sm.compute(JANUARY, "2027-01", 10000)   # 7 points: 10,000 x 3 // 7 = 4,285; 10,000 x 2 // 7 = 2,857 twice; 1 kept
        self.assertEqual({s["login"]: [i["number"] for i in s["issues"]] for s in r["shares"]},
                         {"mantenedor": [30], "pessoa-a": [31], "pessoa-b": [23, 32]})   # December's issues are outside January
        self.assertEqual([(s["login"], s["points"], s["amount_cents"]) for s in r["shares"]],
                         [("mantenedor", 3, 4285), ("pessoa-a", 2, 2857), ("pessoa-b", 2, 2857)])
        self.assertEqual(r["kept_cents"], 1)
        self.assertEqual(r["skipped"], [])

    def test_the_shares_close_on_what_the_infrastructure_left(self):
        # spec 11.6: the shares plus the kept cents equal what is left after the infrastructure, to the cent, with the pool from
        # the ledger (50,000 in, 2,000 of infrastructure)
        dec = {"month": "2026-12", "opening_cents": 0, "entries": [{"date": "2026-12-03", "channel": "pix", "amount_cents": 50000}],
               "infra": [{"date": "2026-12-10", "service": "servidor", "amount_cents": 2000, "receipt_url": "https://example.org/r"}],
               "split": None, "payouts": [], "returned": [], "closing_cents": 48000}
        r = sm.compute(CASE, "2026-12", ledger.pool_cents([dec], "2026-12"))
        self.assertEqual(sum(s["amount_cents"] for s in r["shares"]) + r["kept_cents"], 50000 - 2000)
        self.assertEqual([s["amount_cents"] for s in r["shares"]], [40000, 8000])
        dec["split"] = {k: r[k] for k in ("pool_cents", "shares", "kept_cents")}
        self.assertEqual(ledger.problems([dec]), [], "the split as the script writes it is a valid ledger split")

    def test_nothing_to_split(self):
        r = sm.compute(CASE, "2026-12", 0)
        self.assertEqual(sum(s["amount_cents"] for s in r["shares"]), 0)
        r = sm.compute([], "2026-12", 50000)
        self.assertEqual((r["shares"], r["kept_cents"]), ([], 50000))

    def test_controls_each_rule_bites(self):
        base = sm.compute(CASE, "2026-12", 50000)["shares"]
        for number, change in ((20, {"labels": ["difficulty:low"], "labeled": [{"label": "difficulty:low", "at": "2026-12-01T00:00:00Z"}]}),
                               (21, {"labeled": [{"label": "difficulty:high", "at": "2026-12-05T10:00:00Z"}]}),
                               (22, {"closerMerged": True})):
            case = copy.deepcopy(CASE)
            next(i for i in case if i["number"] == number).update(change)
            self.assertNotEqual(sm.compute(case, "2026-12", 50000)["shares"], base, number)

    def test_control_one_cent_more_fails_the_sum(self):
        r = sm.compute(CASE, "2026-12", 50000)
        r["shares"][0]["amount_cents"] += 1
        self.assertNotEqual(sum(s["amount_cents"] for s in r["shares"]) + r["kept_cents"], r["pool_cents"])

    def test_normalize_reads_the_graphql_shape(self):
        node = {"number": 7, "closedAt": "2026-12-05T15:00:00Z", "stateReason": "COMPLETED",
                "labels": {"nodes": [{"name": "difficulty:low"}]}, "assignees": {"nodes": [{"login": "pessoa-a"}]},
                "timelineItems": {"nodes": [
                    {"__typename": "LabeledEvent", "createdAt": "2026-12-01T10:00:00Z", "label": {"name": "difficulty:low"}},
                    {"__typename": "AssignedEvent", "createdAt": "2026-12-01T11:00:00Z", "assignee": {"login": "pessoa-a"}},
                    {"__typename": "ClosedEvent", "createdAt": "2026-12-05T15:00:00Z", "closer": {"__typename": "PullRequest", "merged": True}}]}}
        i = sm.normalize(node)
        self.assertEqual((i["labels"], i["assignees"], i["closerMerged"]), (["difficulty:low"], ["pessoa-a"], True))
        self.assertEqual(sm.compute([i], "2026-12", 300)["shares"][0]["amount_cents"], 300)


if __name__ == "__main__":
    unittest.main()
