import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import reference  # noqa: E402
import rtn_map  # noqa: E402

FIXTURE = Path(__file__).with_name("fixtures") / "rtn-t12-codes-ago26.json"


class RtnMapTest(unittest.TestCase):
    def test_every_printed_code_has_exactly_one_role(self):
        codes = set(json.loads(FIXTURE.read_text(encoding="utf-8"))["codes"])
        self.assertEqual(rtn_map.ALL_CODES, codes)
        roles = [set(rtn_map.LEAVES), rtn_map.TOTALS, set(rtn_map.OF_WHICH), {rtn_map.RGPS_URBAN},
                 set(rtn_map.INTERNAL), set(rtn_map.RESULTS), rtn_map.ADJUSTMENTS, set(rtn_map.INTEREST)]
        self.assertEqual(sum(len(r) for r in roles), len(codes))

    def test_mappings_use_known_types_nodes_and_rules(self):
        types = {t[0] for t in reference.FLOW_TYPES}
        nodes = {n[0] for n in reference.NODES}
        for key, (flow_type, a, b, rule) in {**rtn_map.LEAVES, **rtn_map.REST, **rtn_map.INTEREST}.items():
            self.assertIn(flow_type, types, key)
            self.assertTrue(a in nodes and b in nodes and a != b, key)
            self.assertIn(rule, reference.METHOD, key)

    def test_between_governments_means_transfer_and_nothing_else(self):
        gov = {n[0] for n in reference.NODES if n[3]}
        nature = {t[0]: t[1] for t in reference.FLOW_TYPES}
        for key, (flow_type, a, b, _rule) in {**rtn_map.LEAVES, **rtn_map.REST}.items():
            self.assertEqual(a in gov and b in gov, nature[flow_type] == "intergovernmental", key)

    def test_money_without_a_state_is_marked_never_kept_in_the_uniao(self):  # D127
        for key, (_t, a, b, rule) in {**rtn_map.LEAVES, **rtn_map.REST}.items():
            if reference.METHOD[rule] == "unallocated":
                self.assertIn(b if a == "gov:uniao" else a, ("soc:unknown", "gov:sub:br"), key)

    def test_under(self):
        self.assertTrue(rtn_map.under("1.1.03.3.1", "1.1.03"))
        self.assertTrue(rtn_map.under("4.2~rest", "4.2"))
        self.assertFalse(rtn_map.under("10", "1"))
        self.assertFalse(rtn_map.under("4.3.15.1.10", "4.3.15.1.1"))


if __name__ == "__main__":
    unittest.main()
