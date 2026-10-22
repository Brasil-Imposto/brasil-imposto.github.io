import sys
import unittest
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db  # noqa: E402
import reference  # noqa: E402

RELEASE = ("INSERT INTO source_release VALUES ('t@1', 't', 't', 'p', 'u', NULL, NULL, NULL, ?, 1, "
           "TIMESTAMP '2026-10-08 00:00:00', 'test')")
FLOW = "INSERT INTO flow VALUES ('x', DATE '2026-08-01', ?, ?, 'tax', 1, 'cash', 't@1', 'k', 'unallocated', 'no_state_in_source_v1', NULL)"


class SchemaTest(unittest.TestCase):
    def setUp(self):
        self.con = db.connect(":memory:")
        self.con.execute(RELEASE, ["0" * 64])

    def test_init_twice_keeps_one_copy_of_the_reference(self):
        db.init(self.con)
        self.assertEqual(self.con.execute("SELECT count(*) FROM node").fetchone()[0], 86)
        self.assertEqual(len(reference.NODES), 86)

    def test_flow_accepts_a_good_row(self):
        self.con.execute(FLOW, ["soc:unknown", "gov:uniao"])
        self.assertEqual(self.con.execute("SELECT count(*) FROM flow").fetchone()[0], 1)

    def test_flow_rejects_same_origin_and_destination(self):
        with self.assertRaises(duckdb.ConstraintException):
            self.con.execute(FLOW, ["gov:uniao", "gov:uniao"])

    def test_flow_rejects_an_unknown_node(self):
        with self.assertRaises(duckdb.ConstraintException):
            self.con.execute(FLOW, ["soc:uf:XX", "gov:uniao"])

    def test_a_reference_row_changed_in_place_stops_the_build(self):
        self.con.execute("DELETE FROM allocation_rule WHERE rule_id = 'fcdf_df_v1'")
        self.con.execute("INSERT INTO allocation_rule VALUES ('fcdf_df_v1', 1, 'direct', 'outro texto', 'x')")
        with self.assertRaises(SystemExit):
            reference.seed(self.con)


if __name__ == "__main__":
    unittest.main()
