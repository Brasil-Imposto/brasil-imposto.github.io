"""The support ledger page (spec apoie 11.3; round apoie-r4, option B, D234), built by build-ledger-page.py from
data/support-ledger/: with nothing received, the exact text of the round; a month shows only the parts it has, newest first, money
in R$ 1.234,56 from whole cents, every text from the data escaped. Controls: a month that does not close stops the build, and a
poisoned text reaches the page only escaped."""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "docs" / "superpowers" / "tools"
sys.path.insert(0, str(TOOLS))
_spec = importlib.util.spec_from_file_location("build_ledger_page", TOOLS / "build-ledger-page.py")
page = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(page)

EMPTY = {"month": "2026-11", "opening_cents": 0, "entries": [], "infra": [], "split": None, "payouts": [], "returned": [], "closing_cents": 0}
DEC = {"month": "2026-12", "opening_cents": 0,
       "entries": [{"date": "2026-12-03", "channel": "crypto", "amount_cents": 30000, "coin": "USDT", "coin_amount": "57.3",
                    "tx_url": "https://tronscan.org/#/transaction/abc"},
                   {"date": "2026-12-15", "channel": "pix", "amount_cents": 20000, "statement_url": "https://example.org/extrato"}],
       "infra": [{"date": "2026-12-10", "service": "domínio", "amount_cents": 4000, "receipt_url": "https://example.org/recibo"}],
       "split": {"pool_cents": 46000, "kept_cents": 1, "shares": [
           {"login": "pessoa-a", "issues": [{"number": 12, "weight": 3}, {"number": 15, "weight": 2}], "points": 5, "amount_cents": 38333},
           {"login": "pessoa-b", "issues": [{"number": 18, "weight": 1}], "points": 1, "amount_cents": 7666}]},
       "payouts": [], "returned": [], "closing_cents": 46000}


def text(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


class LedgerPageTest(unittest.TestCase):
    def test_nothing_received_says_the_text_of_the_round(self):
        t = text(page.build([EMPTY]))
        self.assertIn("Até agora: nenhuma doação recebida, nenhum gasto de infraestrutura (o site é hospedado de graça no GitHub Pages) "
                      "e nenhum pagamento. Saldo: R$ 0,00.", t)
        self.assertIn("Novembro de 2026", t)
        self.assertIn("A conta fecha: saldo anterior R$ 0,00 + entradas R$ 0,00 - infraestrutura R$ 0,00 - pagamentos R$ 0,00 = "
                      "saldo R$ 0,00.", t)
        for part in ("Entradas", "Infraestrutura", "Divisão de quem contribuiu", "Pagamentos"):
            self.assertNotIn(f"<h3>{part}</h3>", page.build([EMPTY]), "an empty month shows none of its parts")

    def test_the_committed_page_is_the_builders(self):
        self.assertEqual((page.OUT).read_text(encoding="utf-8"), page.build())

    def test_a_month_with_money_shows_its_parts_newest_first_and_closes(self):
        h = page.build([EMPTY, DEC])
        t = text(h)
        self.assertLess(t.index("Dezembro de 2026"), t.index("Novembro de 2026"))
        self.assertIn("R$ 500,00 em doações recebidas, R$ 40,00 em gastos de infraestrutura e nenhum pagamento. Saldo: R$ 460,00.", t)
        self.assertIn("Cripto (57.3 USDT)", t)
        self.assertIn('<a href="https://tronscan.org/#/transaction/abc">transação</a>', h)
        self.assertIn("@pessoa-a #12 (peso 3), #15 (peso 2) 5 R$ 383,33", t)
        self.assertIn("Centavos que ficam para o mês seguinte R$ 0,01", t)
        self.assertIn("A conta fecha: saldo anterior R$ 0,00 + entradas R$ 500,00 - infraestrutura R$ 40,00 - pagamentos R$ 0,00 = "
                      "saldo R$ 460,00.", t)
        self.assertEqual(page.money(123456789), "R$ 1.234.567,89")
        self.assertEqual(page.money(5), "R$ 0,05")

    def test_control_a_month_that_does_not_close_stops_the_build(self):
        bad = dict(DEC, closing_cents=46100)   # one real more than the sum
        with self.assertRaises(SystemExit):
            page.build([EMPTY, bad])

    def test_control_a_poisoned_text_is_escaped(self):
        poisoned = dict(DEC, infra=[dict(DEC["infra"][0], service='<img src=x onerror="alert(1)">')])
        h = page.build([EMPTY, poisoned])
        self.assertNotIn('<img src=x', h)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", h)


if __name__ == "__main__":
    unittest.main()
