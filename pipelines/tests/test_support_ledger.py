"""The support ledger (spec apoie 11.3): every month valid against its schema, the balance closing to the cent, the owed amounts never
negative, and each month's pool what the rule gives. Controls: one real more in an entry, a payout above what was owed, a split
whose shares plus the kept cents differ from the pool, a split whose pool is not the rule's, and a month out of order after a month
that does not close (both found)."""
import unittest

from pipelines.support import ledger


class LedgerTest(unittest.TestCase):
    def test_every_month_is_valid_and_closes(self):
        months = ledger.load_all()
        self.assertGreaterEqual(len(months), 1)
        self.assertEqual(ledger.problems(months), [])

    def test_control_one_real_more_in_an_entry(self):
        m = [{"month": "2026-12", "opening_cents": 0, "entries": [{"date": "2026-12-03", "channel": "pix", "amount_cents": 10100}],
              "infra": [], "split": None, "payouts": [], "returned": [], "closing_cents": 10000}]
        self.assertTrue(any("does not close" in p for p in ledger.problems(m)))

    def test_control_a_payout_above_what_was_owed(self):
        dec = {"month": "2026-12", "opening_cents": 0, "entries": [{"date": "2026-12-03", "channel": "pix", "amount_cents": 10000}],
               "infra": [], "split": {"pool_cents": 10000, "kept_cents": 0, "shares": [
                   {"login": "a", "issues": [{"number": 1, "weight": 1}], "points": 1, "amount_cents": 10000}]},
               "payouts": [], "returned": [], "closing_cents": 10000}
        # January closes to the cent (10,000 + 1 - 10,001 = 0), so only the owed check can fire
        jan = {"month": "2027-01", "opening_cents": 10000, "entries": [{"date": "2027-01-02", "channel": "pix", "amount_cents": 1}],
               "infra": [], "split": None,
               "payouts": [{"login": "a", "split_month": "2026-12", "amount_cents": 10001, "date": "2027-01-05", "channel": "pix"}],
               "returned": [], "closing_cents": 0}
        found = ledger.problems([dec, jan])
        self.assertEqual(len(found), 1, found)
        self.assertIn("more than owed", found[0])

    def test_control_a_split_that_does_not_add_up(self):
        m = [{"month": "2026-12", "opening_cents": 0, "entries": [{"date": "2026-12-03", "channel": "pix", "amount_cents": 10000}],
              "infra": [], "split": {"pool_cents": 10000, "kept_cents": 1, "shares": [
                  {"login": "a", "issues": [{"number": 1, "weight": 1}], "points": 1, "amount_cents": 10000}]},
              "payouts": [], "returned": [], "closing_cents": 10000}]
        self.assertTrue(any("shares plus kept" in p for p in ledger.problems(m)))

    def test_control_a_split_whose_pool_is_not_the_rule(self):
        # December closes with 10,000 and owes nothing from before, so the rule gives a pool of 10,000, not 9,000
        m = [{"month": "2026-12", "opening_cents": 0, "entries": [{"date": "2026-12-03", "channel": "pix", "amount_cents": 10000}],
              "infra": [], "split": {"pool_cents": 9000, "kept_cents": 0, "shares": [
                  {"login": "a", "issues": [{"number": 1, "weight": 1}], "points": 1, "amount_cents": 9000}]},
              "payouts": [], "returned": [], "closing_cents": 10000}]
        found = ledger.problems(m)
        self.assertEqual(len(found), 1, found)
        self.assertIn("the rule gives 10000", found[0])

    def test_control_a_month_out_of_order_and_a_later_error_still_found(self):
        nov = {"month": "2026-11", "opening_cents": 0, "entries": [], "infra": [], "split": None, "payouts": [], "returned": [],
               "closing_cents": 1}   # does not close
        jan = {"month": "2027-01", "opening_cents": 1, "entries": [], "infra": [], "split": None, "payouts": [], "returned": [],
               "closing_cents": 2}   # skips December and does not close either
        found = ledger.problems([nov, jan])
        self.assertEqual(sum("does not close" in p for p in found), 2, found)
        self.assertTrue(any("not the month after it" in p for p in found), found)

    def test_the_pool_follows_the_rule(self):
        dec = {"month": "2026-12", "opening_cents": 0, "entries": [{"date": "2026-12-03", "channel": "pix", "amount_cents": 50000}],
               "infra": [{"date": "2026-12-10", "service": "servidor", "amount_cents": 2000, "receipt_url": "https://example.org/r"}],
               "split": None, "payouts": [], "returned": [], "closing_cents": 48000}
        self.assertEqual(ledger.pool_cents([dec], "2026-12"), 48000)


if __name__ == "__main__":
    unittest.main()
