import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from money import exact, from_millions, to_cents  # noqa: E402


class MoneyTest(unittest.TestCase):
    def test_millions_use_the_number_the_file_holds(self):
        self.assertEqual(from_millions(241960.60662784002), Decimal("241960606627.84002000"))
        self.assertEqual(from_millions("102880.81"), Decimal("102880810000.00000000"))

    def test_cents_round_half_to_even(self):
        self.assertEqual(to_cents(Decimal("0.005")), 0)
        self.assertEqual(to_cents(Decimal("0.015")), 2)
        self.assertEqual(to_cents(Decimal("-0.015")), -2)

    def test_negative_lines_keep_their_sign(self):
        self.assertEqual(to_cents(from_millions(-562.410764057834)), -56241076406)

    def test_exact_reais_from_a_float_cell(self):
        self.assertEqual(to_cents(exact(1024768.4)), 102476840)


if __name__ == "__main__":
    unittest.main()
