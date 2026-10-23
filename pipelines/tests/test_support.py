"""The Apoie button's data (spec BRASIL-IMPOSTO_SPEC_apoie_2026-10-23): data/support.json stays off and empty until the
maintainer fills it in, and with `enabled` true every value must be filled and every address must have its network's format.
A planted bad address of each network must fail."""
import copy
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "docs" / "superpowers" / "tools"))
import apoie  # noqa: E402
import site_chrome  # noqa: E402
import support_data  # noqa: E402

# well-formed dummy addresses, for these tests only (never in data/support.json)
DUMMY = {"bitcoin": "bc1qtesttesttesttesttesttesttesttesttest", "evm": "0x" + "7e57" * 10,
         "solana": "TestTestTestTestTestTestTestTestTest", "tron": "TTestTestTestTestTestTestTestTestT",
         "xrp": "rTestTestTestTestTestTestTest"}
BAD = {"bitcoin": ["bc1qtestbtest", "2Test" + "T" * 30, "bc1qTESTtesttesttesttesttesttesttesttest"],
       "evm": ["0x" + "7e57" * 9 + "7e5", "0x" + "7e57" * 9 + "7e5g", "7e57" * 10 + "00"],
       "solana": ["Test0TestTestTestTestTestTestTestTest", "TestTest"],
       "tron": ["TTestTestTestTestTestTestTestTest", "XTestTestTestTestTestTestTestTestT", "TTestTestTestTestTestTestTestTestl"],
       "xrp": ["xTestTestTestTestTestTestTest", "rTest", "rTestTestTestTestTestTestTes0"]}


def committed():
    return json.loads(support_data.PATH.read_text(encoding="utf-8"))


def filled():
    d = copy.deepcopy(committed())
    d.update(enabled=True, sponsors_url="https://github.com/sponsors/Brasil-Imposto", maintainer_cap_brl=3000,
             unidentified_return_above_brl=500, contact_email="contato@example.org")
    d["fiscal_host"]["url"] = "https://opencollective.com/example"
    for g in d["crypto"]:
        g["address"] = DUMMY[g["format"]]
    return d


class CommittedFileTest(unittest.TestCase):
    def test_off_and_empty_until_the_maintainer_fills_it(self):
        d = committed()
        self.assertIs(d["enabled"], False)
        for key in ("sponsors_url", "maintainer_cap_brl", "unidentified_return_above_brl", "contact_email"):
            self.assertIsNone(d[key], key)
        self.assertEqual(d["fiscal_host"], {"name": "Open Source Collective", "url": None})
        self.assertEqual([g["address"] for g in d["crypto"]], [None] * 5)
        self.assertEqual(support_data.problems(d), [])

    def test_the_seven_coins_and_their_networks(self):
        d = committed()
        count = {c: len(support_data.networks_of(d, c)) for c in support_data.COINS}
        self.assertEqual(count, {"BTC": 1, "ETH": 1, "SOL": 1, "USDT": 4, "USDC": 3, "XRP": 1, "BNB": 1})
        names = {c: [n["name"] + (f" ({s})" if s else "") for _, n, s in support_data.networks_of(d, c)] for c in ("USDT", "USDC", "BNB")}
        self.assertEqual(names["USDT"], ["Ethereum (ERC-20)", "BNB Smart Chain (BEP-20)", "Solana (SPL)", "Tron (TRC-20)"])
        self.assertEqual(names["USDC"], ["Ethereum (ERC-20)", "BNB Smart Chain (BEP-20)", "Solana (SPL)"])
        self.assertEqual(names["BNB"], ["BNB Smart Chain (BEP-20)"])

    def test_one_address_per_group_and_its_explorers(self):
        urls = {n["id"]: n["explorer_url"] for g in committed()["crypto"] for n in g["networks"]}
        self.assertEqual(urls, {"bitcoin": "https://mempool.space/address/{address}", "ethereum": "https://etherscan.io/address/{address}",
                                "bsc": "https://bscscan.com/address/{address}", "solana": "https://solscan.io/account/{address}",
                                "tron": "https://tronscan.org/address/{address}/transactions",
                                "xrp-ledger": "https://xrpscan.com/account/{address}"})


class EnabledRuleTest(unittest.TestCase):
    def test_filled_dummy_data_passes(self):
        self.assertEqual(support_data.problems(filled()), [])

    def test_enabled_with_a_value_missing_fails(self):
        for key in ("sponsors_url", "maintainer_cap_brl", "unidentified_return_above_brl", "contact_email"):
            with self.subTest(key=key):
                d = filled(); d[key] = None
                self.assertTrue(any(p.startswith(key) for p in support_data.problems(d)), key)
        d = filled(); d["fiscal_host"]["url"] = None
        self.assertTrue(support_data.problems(d))
        for i in range(5):
            with self.subTest(group=i):
                d = filled(); d["crypto"][i]["address"] = None
                self.assertTrue(support_data.problems(d))

    def test_control_a_planted_bad_address_fails(self):
        for fmt, bad in BAD.items():
            for a in bad:
                with self.subTest(fmt=fmt, address=a):
                    d = filled()
                    next(g for g in d["crypto"] if g["format"] == fmt)["address"] = a
                    self.assertTrue(any("is not a" in p for p in support_data.problems(d)), a)

    def test_the_money_format(self):
        self.assertEqual(support_data.brl(3000), "R$ 3.000,00")
        self.assertEqual(support_data.brl(1234567.5), "R$ 1.234.567,50")


class PagesTest(unittest.TestCase):
    def build(self, data):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
        old = os.environ.get("BI_SUPPORT_JSON")
        os.environ["BI_SUPPORT_JSON"] = f.name
        try:
            return {k: site_chrome.parts(k) for k in site_chrome.PAGES}
        finally:
            os.unlink(f.name)
            if old is None:
                os.environ.pop("BI_SUPPORT_JSON")
            else:
                os.environ["BI_SUPPORT_JSON"] = old

    def test_off_no_button_and_the_chrome_as_before(self):
        for key, p in self.build(committed()).items():
            with self.subTest(page=key):
                self.assertEqual(p["header"], site_chrome.header(key))
                self.assertEqual(p["css"], site_chrome.HEAD)
                self.assertEqual(p["js"], site_chrome.SCRIPT)
                self.assertNotIn("bi-apoie", p["header"] + p["css"] + p["js"])

    def test_on_the_button_the_texts_and_no_email(self):
        d = filled()
        for key, p in self.build(d).items():
            with self.subTest(page=key):
                h = p["header"]
                self.assertEqual(h.count('class="bi-apoie-btn"'), 1)
                self.assertLess(h.index('class="bi-links"'), h.index('class="bi-apoie-btn"'))
                self.assertLess(h.index('class="bi-apoie-btn"'), h.index('class="bi-menu-btn"'))
                self.assertLess(h.index("</header>"), h.index('id="bi-apoie"'), "the modal sits outside the header")
                text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).replace(" ,", ",")
                for t in [apoie.LEAD, apoie.INFRA, apoie.NOT_PAID_BY, apoie.SPONSORS_FACTS, apoie.WARNING, apoie.CONTACT_ASK,
                          apoie.CONTACT_LGPD, apoie.PICK_NETWORK, *apoie.MONTH, *apoie.SPONSORS_STEPS,
                          apoie.DEVELOPERS.replace("{cap}", "R$ 3.000,00"), apoie.RETURN_RULE.replace("{limit}", "R$ 500,00"),
                          "Apoie o Brasil-Imposto", "Para onde vai o dinheiro", "Como cada mês é dividido", "Como apoiar",
                          "Antes de apoiar", "Fale com a gente", "Apoiar pelo GitHub Sponsors", "Apoiar com cripto",
                          "Abrir o GitHub Sponsors", "Voltar", "Copiar"]:
                    self.assertIn(re.sub(r"\s+", " ", t), text, t[:50])
                self.assertNotIn(d["contact_email"], h + p["js"], "D124: the e-mail never on the page")
                self.assertIn(".bi-apoie [hidden] { display: none !important; }", p["css"])
                for g in d["crypto"]:
                    self.assertIn(g["address"], h)

    def test_on_with_a_value_missing_refuses_to_build(self):
        d = filled(); d["crypto"][0]["address"] = "bc1"
        with self.assertRaises(SystemExit):
            self.build(d)

    def test_without_the_email_no_contact_form(self):
        h = apoie.modal(dict(filled(), contact_email=None))
        self.assertNotIn('data-view="contact"', h)
        self.assertNotIn('data-go="contact"', h)


if __name__ == "__main__":
    unittest.main()
