"""The Apoie button's data (spec BRASIL-IMPOSTO_SPEC_apoie_2026-10-23, sections 1 to 8, and spec staging, section 2): data/support.json
stays empty until the maintainer fills it in, and the apoie switch of data/features.json says which build carries the button. Production
may turn it on with both payment channels on "soon" and without the contact form's access key (D162: the form stays out until the key is filled); a channel goes "live" only with every one of its values filled and every address in its network's format. The
built pages never show "a definir" and never carry an e-mail address. Every rule has a planted failure."""
import copy
import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "docs" / "superpowers" / "tools"
sys.path.insert(0, str(TOOLS))
import apoie  # noqa: E402
import site_chrome  # noqa: E402
import support_data  # noqa: E402

_spec = importlib.util.spec_from_file_location("email_scan", TOOLS / "email-scan.py")
email_scan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(email_scan)

ACCESS_KEY = "00000000-1111-4222-8333-444444444444"   # a dummy Web3Forms access key, for these tests only
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


def on_soon():
    """The data production goes live with: both channels on "soon" and the form's access key."""
    d = copy.deepcopy(committed())
    d["contact_form"]["access_key"] = ACCESS_KEY
    return d


def on_live():
    d = on_soon()
    d["maintainer_cap_brl"] = 3000
    d["sponsors"].update(status="live", sponsors_url="https://github.com/sponsors/Brasil-Imposto")
    d["sponsors"]["fiscal_host"]["url"] = "https://opencollective.com/example"
    d["crypto"].update(status="live", unidentified_return_above_brl=500)
    for g in d["crypto"]["groups"]:
        g["address"] = DUMMY[g["format"]]
    return d


def switches(production, staging=True):
    return {"features": [{"key": "apoie", "issue": 46, "description": "O botão Apoie", "staging": staging, "production": production}]}


def build(data, on=True, profile="production"):
    """The parts of the three pages for a test build: data as data/support.json, the apoie switch on (or off) in the profile."""
    files, old = {}, {}
    for env, content in (("BI_SUPPORT_JSON", data), ("BI_FEATURES_JSON", switches(on, on))):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(content, f)
        files[env], old[env] = f.name, os.environ.get(env)
        os.environ[env] = f.name
    try:
        return {k: site_chrome.parts(k, profile) for k in site_chrome.PAGES}
    finally:
        for env, name in files.items():
            os.unlink(name)
            if old[env] is None:
                os.environ.pop(env)
            else:
                os.environ[env] = old[env]


def text(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).replace(" ,", ",").replace(" .", ".")


class CommittedFileTest(unittest.TestCase):
    def test_off_and_empty_until_the_maintainer_fills_it(self):
        d = committed()
        self.assertNotIn("enabled", d, "the apoie switch of data/features.json replaced it")
        self.assertEqual(d["contact_form"], {"provider": "web3forms", "access_key": None})
        self.assertNotIn("contact_email", d)
        self.assertIsNone(d["maintainer_cap_brl"])
        self.assertEqual(d["sponsors"], {"status": "soon", "sponsors_url": None,
                                         "fiscal_host": {"name": "Open Source Collective", "url": None}})
        self.assertEqual(d["crypto"]["status"], "soon")
        self.assertIsNone(d["crypto"]["unidentified_return_above_brl"])
        self.assertEqual([g["address"] for g in d["crypto"]["groups"]], [None] * 5)
        self.assertEqual(support_data.problems(d), [], "the button needs no access key in either profile (D162)")

    def test_the_seven_coins_and_their_networks(self):
        d = committed()
        count = {c: len(support_data.networks_of(d, c)) for c in support_data.COINS}
        self.assertEqual(count, {"BTC": 1, "ETH": 1, "SOL": 1, "USDT": 4, "USDC": 3, "XRP": 1, "BNB": 1})
        names = {c: [n["name"] + (f" ({s})" if s else "") for _, n, s in support_data.networks_of(d, c)] for c in ("USDT", "USDC", "BNB")}
        self.assertEqual(names["USDT"], ["Ethereum (ERC-20)", "BNB Smart Chain (BEP-20)", "Solana (SPL)", "Tron (TRC-20)"])
        self.assertEqual(names["USDC"], ["Ethereum (ERC-20)", "BNB Smart Chain (BEP-20)", "Solana (SPL)"])
        self.assertEqual(names["BNB"], ["BNB Smart Chain (BEP-20)"])

    def test_one_address_per_group_and_its_explorers(self):
        urls = {n["id"]: n["explorer_url"] for g in committed()["crypto"]["groups"] for n in g["networks"]}
        self.assertEqual(urls, {"bitcoin": "https://mempool.space/address/{address}", "ethereum": "https://etherscan.io/address/{address}",
                                "bsc": "https://bscscan.com/address/{address}", "solana": "https://solscan.io/account/{address}",
                                "tron": "https://tronscan.org/address/{address}/transactions",
                                "xrp-ledger": "https://xrpscan.com/account/{address}"})

    def test_no_email_address_in_the_data_file(self):
        self.assertEqual(email_scan.find(support_data.PATH.read_text(encoding="utf-8")), [])


class RulesTest(unittest.TestCase):
    def test_on_with_both_channels_soon_passes(self):
        self.assertEqual(support_data.problems(on_soon()), [])

    def test_on_without_the_access_key_passes(self):
        d = on_soon(); d["contact_form"]["access_key"] = None
        self.assertEqual(support_data.problems(d), [])

    def test_control_an_email_address_as_the_access_key_fails(self):
        d = on_soon(); d["contact_form"]["access_key"] = "someone" + chr(64) + "example.org"
        self.assertTrue(any(p.startswith("contact_form.access_key") for p in support_data.problems(d)))

    def test_a_status_outside_soon_and_live_fails(self):
        d = on_soon(); d["sponsors"]["status"] = "open"
        self.assertTrue(any(p.startswith("sponsors.status") for p in support_data.problems(d)))

    def test_live_with_every_value_passes(self):
        self.assertEqual(support_data.problems(on_live()), [])

    def test_live_with_a_value_missing_fails(self):
        cases = {"sponsors_url": lambda d: d["sponsors"].update(sponsors_url=None),
                 "fiscal_host": lambda d: d["sponsors"]["fiscal_host"].update(url=None),
                 "maintainer_cap_brl": lambda d: d.update(maintainer_cap_brl=None),
                 "threshold": lambda d: d["crypto"].update(unidentified_return_above_brl=None)}
        for i in range(5):
            cases[f"address {i}"] = (lambda i: lambda d: d["crypto"]["groups"][i].update(address=None))(i)
        for name, change in cases.items():
            with self.subTest(missing=name):
                d = on_live(); change(d)
                self.assertTrue(support_data.problems(d), name)

    def test_control_a_planted_bad_address_fails(self):
        for fmt, bad in BAD.items():
            for a in bad:
                with self.subTest(fmt=fmt, address=a):
                    d = on_live()
                    next(g for g in d["crypto"]["groups"] if g["format"] == fmt)["address"] = a
                    self.assertTrue(any("is not a" in p for p in support_data.problems(d)), a)

    def test_the_money_format(self):
        self.assertEqual(support_data.brl(3000), "R$ 3.000,00")
        self.assertEqual(support_data.brl(1234567.5), "R$ 1.234.567,50")


class PagesTest(unittest.TestCase):
    def test_off_no_button_and_the_chrome_as_before(self):
        for key, p in build(committed(), on=False).items():
            with self.subTest(page=key):
                self.assertEqual(p["header"], site_chrome.header(key))
                self.assertEqual(p["css"], site_chrome.HEAD)
                self.assertEqual(p["js"], site_chrome.SCRIPT)
                self.assertNotIn("bi-apoie", p["header"] + p["css"] + p["js"])

    def test_on_soon_the_cards_wait_and_the_form_works(self):
        for key, p in build(on_soon()).items():
            with self.subTest(page=key):
                h = p["header"]
                self.assertEqual(h.count('class="bi-apoie-btn"'), 1)
                self.assertLess(h.index("</header>"), h.index('id="bi-apoie"'), "the modal sits outside the header")
                cards = re.findall(r'<div class="bi-ap-card bi-ap-soon">(.*?)</div>', h)
                self.assertEqual(len(cards), 2)
                for c in cards:
                    self.assertIn('<span class="bi-ap-tag">Em breve</span>', c)
                    for mark in ("<a ", "<button", "<code", "data-go"):
                        self.assertNotIn(mark, c, "a card on soon has nothing to click and no address")
                for view in ("sponsors", "crypto"):
                    self.assertNotIn(f'data-view="{view}"', h)
                    self.assertNotIn(f'data-go="{view}"', h)
                t = text(h)
                for s in [apoie.SPONSORS_CARD, apoie.CRYPTO_CARD_SOON, apoie.OTHER_WAY, apoie.CONTACT_ASK, apoie.CONTACT_LGPD,
                          apoie.SENT, apoie.FAILED, apoie.LEAD, apoie.DEVELOPERS, "Fale com a gente", "Nome", "E-mail", "Mensagem"]:
                    self.assertIn(re.sub(r"\s+", " ", s), t, s[:50])
                for gone in ("Quem recebe", "a definir", "teto de", "Cada endereço é público", "Doação acima de"):
                    self.assertNotIn(gone, t, gone)
                kept = re.findall(r'<ul class="bi-ap-list">(.*?)</ul>', h)[0]
                self.assertEqual(kept.count("<li>"), 5)
                self.assertIn('data-endpoint="https://api.web3forms.com/submit"', h)
                self.assertIn(f'data-key="{ACCESS_KEY}"', h)
                self.assertIn('<input type="checkbox" name="botcheck"', h)

    def test_no_email_address_in_any_built_part(self):
        for data in (on_soon(), on_live()):
            for key, p in build(data).items():
                with self.subTest(page=key, live=data["crypto"]["status"]):
                    self.assertEqual(email_scan.find(p["header"] + p["css"] + p["js"]), [])

    def test_control_the_email_scan_catches_a_planted_address(self):
        p = build(on_soon())["inicio"]
        self.assertEqual(email_scan.find(p["header"] + email_scan.PLANTED), [email_scan.PLANTED])

    def test_on_live_the_channels_open(self):
        for key, p in build(on_live()).items():
            with self.subTest(page=key):
                h = p["header"]
                t = text(h)
                self.assertNotIn("Em breve", t)
                for view in ("sponsors", "crypto", "contact"):
                    self.assertIn(f'data-view="{view}"', h)
                for s in ["Quem recebe", apoie.CRYPTO_CARD, apoie.DEVELOPERS_CAP.replace("{cap}", "R$ 3.000,00"),
                          apoie.RETURN_RULE.replace("{limit}", "R$ 500,00")]:
                    self.assertIn(re.sub(r"\s+", " ", s), t, s[:50])
                for g in on_live()["crypto"]["groups"]:
                    self.assertIn(g["address"], h)

    def test_staging_draws_the_form_without_the_key(self):
        for key, p in build(committed(), profile="staging").items():
            with self.subTest(page=key):
                h = p["header"]
                self.assertIn('data-view="contact"', h)
                self.assertIn('data-key=""', h)
                self.assertEqual(len(re.findall(r'<div class="bi-ap-card bi-ap-soon">', h)), 2)
                self.assertNotIn("a definir", text(h))
                self.assertIn("if (!form.dataset.key) { fail.hidden = false; return; }", p["js"])

    def test_production_keeps_the_script_it_publishes(self):
        """The staging line for a keyless form goes only into the staging script: production's script is apoie.SCRIPT itself."""
        for key, p in build(committed()).items():
            with self.subTest(page=key):
                self.assertNotIn("if (!form.dataset.key)", p["js"])
                self.assertIn(apoie.SCRIPT, p["js"])
        self.assertEqual(apoie.STAGING_SCRIPT.replace(
            "      if (!form.dataset.key) { fail.hidden = false; return; }   // staging without the access key: nothing is sent\n", ""),
            apoie.SCRIPT, "the staging script differs from production's by that one line only")

    def test_on_without_the_access_key_shows_everything_but_the_form(self):
        d = on_soon(); d["contact_form"]["access_key"] = None
        for key, p in build(d).items():
            with self.subTest(page=key):
                h = p["header"]
                self.assertEqual(h.count('class="bi-apoie-btn"'), 1)
                self.assertEqual(len(re.findall(r'<div class="bi-ap-card bi-ap-soon">', h)), 2)
                for gone in ('data-go="contact"', 'data-view="contact"', "api.web3forms.com", 'name="botcheck"'):
                    self.assertNotIn(gone, h, gone)
                self.assertNotIn(re.sub(r"\s+", " ", apoie.OTHER_WAY), text(h))
                self.assertIn(re.sub(r"\s+", " ", apoie.LEAD), text(h))


    def test_control_a_bad_access_key_refuses_to_build(self):
        d = on_soon(); d["contact_form"]["access_key"] = "not-a-key"
        with self.assertRaises(SystemExit):
            build(d)


if __name__ == "__main__":
    unittest.main()
