import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db  # noqa: E402
import guarantees as g  # noqa: E402

P = date(2026, 8, 1)
FLOWS = [
    ("f1", P, "soc:unknown", "gov:uniao", "public_payroll_withholding", 100, "cash", "t@1", "A", "unallocated",
     "no_state_in_source_v1", "payroll:2026-08"),
    ("f2", P, "gov:uniao", "soc:unknown", "public_payroll_gross", 200, "cash", "t@1", "B", "unallocated",
     "no_state_in_source_v1", "payroll:2026-08"),
]
CHECKS = (g.g1_unique_ids, g.g2_complete_rows, g.g4_lines_conserved, g.g6_pairs_same_state, g.g7_no_transfer_in_spending)


def fixture():
    con = db.connect(":memory:")
    con.execute("INSERT INTO source_release VALUES ('t@1', 't.ds', 't', 'p', 'u', NULL, NULL, NULL, ?, 1, "
                "TIMESTAMP '2026-10-08 00:00:00', 'test')", ["0" * 64])
    db.insert(con, published=[("t@1", "A", P, "leaf", "a", Decimal("1.00"), 100, 1),
                              ("t@1", "B", P, "leaf", "b", Decimal("2.00"), 200, 1)], flows=FLOWS)
    con.execute("CREATE TEMP TABLE cand AS SELECT * FROM flow_stage")
    return con


class GuaranteesTest(unittest.TestCase):
    def setUp(self):
        self.con = fixture()

    def failed(self, check):
        return not check(self.con, "cand").ok

    def test_clean_rows_pass_every_check(self):
        for check in CHECKS:
            self.assertFalse(self.failed(check), check.__name__)

    def test_g1_catches_a_duplicate(self):
        self.con.execute("INSERT INTO cand SELECT * FROM cand WHERE flow_id = 'f1'")
        self.assertTrue(self.failed(g.g1_unique_ids))

    def test_g2_catches_same_origin_and_destination(self):
        self.con.execute("UPDATE cand SET to_node = 'soc:unknown' WHERE flow_id = 'f1'")
        self.assertTrue(self.failed(g.g2_complete_rows))

    def test_g2_catches_a_negative_purchase(self):
        self.con.execute("UPDATE cand SET flow_type = 'purchase', amount_cents = -200 WHERE flow_id = 'f2'")
        self.assertTrue(self.failed(g.g2_complete_rows))

    def test_g4_catches_a_deleted_row(self):
        self.con.execute("DELETE FROM cand WHERE flow_id = 'f2'")
        self.assertTrue(self.failed(g.g4_lines_conserved))

    def test_g4_catches_a_flipped_sign(self):
        self.con.execute("UPDATE cand SET amount_cents = -amount_cents WHERE flow_id = 'f1'")
        self.assertTrue(self.failed(g.g4_lines_conserved))

    def test_g6_catches_a_pair_split_across_states(self):
        self.con.execute("UPDATE cand SET from_node = 'soc:uf:DF' WHERE flow_id = 'f1'")
        self.assertTrue(self.failed(g.g6_pairs_same_state))

    def test_g7_catches_a_payment_to_a_government_typed_as_spending(self):
        self.con.execute("UPDATE cand SET to_node = 'gov:sub:br' WHERE flow_id = 'f2'")
        self.assertTrue(self.failed(g.g7_no_transfer_in_spending))


class RreoVerdictTest(unittest.TestCase):  # decision D122
    def test_years_printed_in_cents_must_match_to_the_cent(self):
        self.assertEqual(g.rreo_verdict(date(2025, 12, 1), 100, 100, False), "ok")
        self.assertEqual(g.rreo_verdict(date(2025, 12, 1), 101, 100, False), "fail")

    def test_years_printed_in_whole_reais_allow_one_printed_unit(self):
        self.assertEqual(g.rreo_verdict(date(2021, 6, 1), 950, 1000, True), "ok")
        self.assertEqual(g.rreo_verdict(date(2021, 6, 1), 899, 1000, True), "fail")

    def test_known_gaps_must_stay_exactly_as_recorded(self):
        self.assertEqual(g.rreo_verdict(date(2023, 12, 1), 1000 - 379, 1000, True), "known_gap")
        self.assertEqual(g.rreo_verdict(date(2023, 12, 1), 1000 - 380, 1000, True), "fail")
        self.assertEqual(g.rreo_verdict(date(2023, 10, 1), 1000, 1000, True), "fail")


if __name__ == "__main__":
    unittest.main()
