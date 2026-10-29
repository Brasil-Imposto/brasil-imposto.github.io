"""The Apoie button's data (spec BRASIL-IMPOSTO_SPEC_apoie_2026-10-23, sections 1 to 9, and spec staging, section 2): data/support.json
stays empty until the maintainer fills it in, and the apoie switch of data/features.json says which build carries the button. Production
may turn it on with the three payment channels (Pix, GitHub Sponsors, crypto) on "soon" and without the contact form's access key (D162: the form stays out until the key is filled); a channel goes "live" only with every one of its values filled and every address in its network's format. The
built pages never show "a definir" and never carry an e-mail address. Every rule has a planted failure."""
import copy
import html as htmllib
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
PIX_URL = "https://www.vakinha.com.br/vaquinha/teste-da-sonda"   # a dummy campaign, for these tests only
PIX_NAME = "Nome de Teste"
# well-formed dummy addresses, for these tests only (never in data/support.json)
DUMMY = {"bitcoin": "bc1qtesttesttesttesttesttesttesttesttest", "evm": "0x" + "7e57" * 10,
         "solana": "TestTestTestTestTestTestTestTestTest", "tron": "TTestTestTestTestTestTestTestTestT",
         "xrp": "rTestTestTestTestTestTestTest"}
BAD = {"bitcoin": ["bc1qtestbtest", "2Test" + "T" * 30, "bc1qTESTtesttesttesttesttesttesttesttest"],
       "evm": ["0x" + "7e57" * 9 + "7e5", "0x" + "7e57" * 9 + "7e5g", "7e57" * 10 + "00"],
       "solana": ["Test0TestTestTestTestTestTestTestTest", "TestTest"],
       "tron": ["TTestTestTestTestTestTestTestTest", "XTestTestTestTestTestTestTestTestT", "TTestTestTestTestTestTestTestTestl"],
       "xrp": ["xTestTestTestTestTestTestTest", "rTest", "rTestTestTestTestTestTestTes0"]}


def in_order(t, marks):
    """True when every mark appears in t after the one before it."""
    at = -1
    for m in marks:
        i = t.find(m, at + 1)
        if i < 0:
            return False
        at = i
    return True


# What the modal said before section 9; a build must show none of it. "Para onde vai o dinheiro" is the old title, and
# the new one begins with it, so it is matched as a whole phrase.
OLD_TEXTS = ["Não pagamos por número de commits, de linhas ou de pull requests",
             "A pessoa mantenedora recebe um valor fixo por mês para revisar, publicar e manter o projeto, com teto de R$ 3.000,00.",
             "Cada tarefa paga é uma issue com o valor em reais publicado antes de o trabalho começar",
             "Com o restante, as tarefas pagas que entraram no mês",
             "Depois, o valor fixo da manutenção, até o teto.",
             "1. Desenvolvedores", "2. Infraestrutura",
             "Não compra conteúdo: ninguém que apoia muda o que o site mostra"]


def removed_texts(t):
    """The texts of the modal before section 9 found in t (an empty list is clean)."""
    found = [o for o in OLD_TEXTS if o in t]
    if re.search(r"Para onde vai o dinheiro(?! do apoio)", t):
        found.append("Para onde vai o dinheiro")
    return found


def committed():
    return json.loads(support_data.PATH.read_text(encoding="utf-8"))


def on_soon():
    """The data production goes live with: both channels on "soon" and the form's access key."""
    d = copy.deepcopy(committed())
    d["contact_form"]["access_key"] = ACCESS_KEY
    return d


def on_live():
    d = on_soon()
    d["pix"].update(status="live", campaign_url=PIX_URL, bank_screen_name=PIX_NAME)
    d["sponsors"].update(status="live", sponsors_url="https://github.com/sponsors/Brasil-Imposto")
    d["sponsors"]["fiscal_host"]["url"] = "https://opencollective.com/example"
    d["crypto"].update(status="live", unidentified_return_above_brl=500)
    for g in d["crypto"]["groups"]:
        g["address"] = DUMMY[g["format"]]
    return d


def switches(production, staging=True):
    return {"features": [{"key": "apoie", "issue": 46, "description": "O botão Apoie", "staging": staging, "production": production},
                         {"key": "rede", "issue": 130, "description": "A prévia da Rede do dinheiro", "staging": True, "production": False}]}


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
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", html))).replace(" ,", ",").replace(" .", ".").replace(" ;", ";")


class CommittedFileTest(unittest.TestCase):
    def test_form_key_and_addresses_filled_and_the_channels_waiting(self):
        d = committed()
        self.assertNotIn("enabled", d, "the apoie switch of data/features.json replaced it")
        self.assertEqual(d["contact_form"]["provider"], "web3forms")
        self.assertRegex(d["contact_form"]["access_key"], support_data.ACCESS_KEY, "D168: the maintainer's Web3Forms key")
        self.assertNotIn("contact_email", d)
        self.assertNotIn("maintainer_cap_brl", d, "the maintainer has no fixed amount and no cap (spec section 9)")
        self.assertEqual(list(d)[1:5], ["pix", "contact_form", "sponsors", "crypto"], "the Pix channel comes first")
        self.assertEqual(d["pix"], {"status": "soon", "provider": "Vakinha", "campaign_url": None, "bank_screen_name": None})
        self.assertEqual(d["sponsors"], {"status": "soon", "sponsors_url": None,
                                         "fiscal_host": {"name": "Open Source Collective", "url": None}})
        self.assertEqual(d["crypto"]["status"], "soon")
        self.assertIsNone(d["crypto"]["unidentified_return_above_brl"])
        # the five project addresses came from the maintainer on 2026-10-28; each must fit its network's format
        for g in d["crypto"]["groups"]:
            self.assertRegex(g["address"] or "", support_data.FORMATS[g["format"]], g["id"])
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
                 "campaign_url": lambda d: d["pix"].update(campaign_url=None),
                 "bank_screen_name": lambda d: d["pix"].update(bank_screen_name=None),
                 "threshold": lambda d: d["crypto"].update(unidentified_return_above_brl=None)}
        for i in range(5):
            cases[f"address {i}"] = (lambda i: lambda d: d["crypto"]["groups"][i].update(address=None))(i)
        for name, change in cases.items():
            with self.subTest(missing=name):
                d = on_live(); change(d)
                self.assertTrue(support_data.problems(d), name)

    def test_the_pix_needs_a_https_vakinha_address_and_the_bank_name(self):
        planted = {"http://": "http://www.vakinha.com.br/vaquinha/teste", "another domain": "https://www.exemplo.org/vaquinha/teste",
                   "lookalike host": "https://vakinha.com.br.exemplo.org/vaquinha/teste",
                   "vakinha only in the path": "https://exemplo.org/vakinha.com.br/teste", "no campaign path": "https://www.vakinha.com.br/",
                   "not an address": "vakinha.com.br/vaquinha/teste"}
        for name, url in planted.items():
            with self.subTest(campaign_url=name):
                d = on_live(); d["pix"]["campaign_url"] = url
                self.assertTrue(any(p.startswith("pix.campaign_url") for p in support_data.problems(d)), url)
        for url in ("https://vakinha.com.br/vaquinha/teste", PIX_URL):
            with self.subTest(accepted=url):
                d = on_live(); d["pix"]["campaign_url"] = url
                self.assertEqual(support_data.problems(d), [])
        for name in ("", "   ", None):
            with self.subTest(bank_screen_name=name):
                d = on_live(); d["pix"]["bank_screen_name"] = name
                self.assertTrue(any(p.startswith("pix.bank_screen_name") for p in support_data.problems(d)))

    def test_the_pix_on_soon_needs_no_value_and_a_wrong_status_or_provider_fails(self):
        d = on_soon(); d["pix"]["status"] = "open"
        self.assertTrue(any(p.startswith("pix.status") for p in support_data.problems(d)))
        d = on_soon(); d["pix"]["provider"] = "Outra"
        self.assertTrue(any(p.startswith("pix.provider") for p in support_data.problems(d)))
        d = on_soon(); d["pix"]["campaign_url"] = "http://www.vakinha.com.br/x"   # not checked until the Pix is live
        self.assertEqual(support_data.problems(d), [])

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
                self.assertEqual(p["header"], site_chrome.header(key, rede=False))   # switches() keeps rede off in production
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
                self.assertEqual(len(cards), 3)
                for c in cards:
                    self.assertIn('<span class="bi-ap-tag">Em breve</span>', c)
                    for mark in ("<a ", "<button", "<code", "data-go"):
                        self.assertNotIn(mark, c, "a card on soon has nothing to click and no address")
                for view in ("pix", "sponsors", "crypto"):
                    self.assertNotIn(f'data-view="{view}"', h)
                    self.assertNotIn(f'data-go="{view}"', h)
                t = text(h)
                for s in [apoie.PIX_CARD, apoie.SPONSORS_CARD, apoie.CRYPTO_CARD_SOON, apoie.OTHER_WAY, apoie.CONTACT_ASK, apoie.CONTACT_LGPD,
                          apoie.SENT, apoie.FAILED, apoie.LEAD, apoie.DEVELOPERS, "Fale com a gente", "Nome", "E-mail", "Mensagem"]:
                    self.assertIn(re.sub(r"\s+", " ", s), t, s[:50])
                for gone in ("Quem recebe", "a definir", "teto de", "Cada endereço é público", "Doação acima de", "Apoiar com Pix",
                             "Abrir a vaquinha"):
                    self.assertNotIn(gone, t, gone)
                kept = re.findall(r'<ul class="bi-ap-list">(.*?)</ul>', h)[0]
                self.assertEqual(kept.count("<li>"), 5)
                self.assertIn('data-endpoint="https://api.web3forms.com/submit"', h)
                self.assertIn(f'data-key="{ACCESS_KEY}"', h)
                self.assertIn('<input type="checkbox" name="botcheck"', h)

    # --- spec section 9 (round 3): the Pix, the new texts and their order --------------------------------------------------------
    def main_view(self, data, profile="production"):
        return build(data, profile=profile)["inicio"]["header"]

    def test_the_cards_are_pix_sponsors_crypto_in_three_columns_that_fall_to_one(self):
        h = self.main_view(on_soon())
        cards = re.search(r'<div class="bi-ap-cards">(.*?)</div><div class="bi-ap-other">', h, re.S).group(1)
        self.assertEqual(re.findall(r"<h4>(.*?) <span", cards), ["Pix", "GitHub Sponsors", "Cripto"])
        self.assertIn('<span class="bi-ap-nw">Brasil-Imposto</span>', cards, "Brasil-Imposto never breaks at its hyphen")
        self.assertRegex(apoie.CSS, r"\.bi-ap-cards \{[^}]*grid-template-columns: repeat\(3, minmax\(0, 1fr\)\)")
        narrow = re.search(r"@media \(max-width: 820px\) \{(.*?)\n\}", apoie.CSS, re.S).group(1)
        self.assertRegex(narrow, r"\.bi-ap-cards \{ grid-template-columns: 1fr; \}")
        self.assertIn(".bi-ap-bar i { flex: 1; border-radius: 99px; background: #1F5FAF; }\n.bi-ap-bar i + i { background: #12803F; }", apoie.CSS,
                      "the bar is blue, then green, in the order of the columns")

    def test_the_main_view_texts_of_section_9_3(self):
        t = text(self.main_view(on_soon()))
        for s in [apoie.LEAD, apoie.MONEY_TITLE, apoie.INFRA, apoie.DEVELOPERS, apoie.PIX_CARD, *apoie.MONTH,
                  "Quem entrega trabalho aceito no repositório, inclusive a pessoa mantenedora.",
                  'O que o apoio compra: trabalho e infraestrutura. Junto com a doação, você pode pedir pelo "Fale com a gente" uma '
                  'funcionalidade que ainda não existe; os pedidos entram no planejamento das próximas atualizações. Nenhum apoio muda '
                  'um número: todo número vem da fonte oficial, e as regras de neutralidade valem para todos.']:
            self.assertIn(re.sub(r"\s+", " ", s), t, s[:60])

    def test_the_order_of_the_main_view(self):
        marks = ["1. Infraestrutura", "2. Desenvolvedores", "Como apoiar", "Pix", "GitHub Sponsors", "Cripto", apoie.OTHER_WAY,
                 "Como cada mês é dividido", "Antes de apoiar"]
        h = self.main_view(on_soon())
        self.assertTrue(in_order(text(h), marks))
        self.assertLess(text(h).index("Para onde vai o dinheiro do apoio"), text(h).index("1. Infraestrutura"))

    def test_control_the_order_check_catches_the_box_before_the_contact_line_and_a_column_swap(self):
        h = self.main_view(on_soon())
        box = re.search(r'<div class="bi-ap-box">.*?</ol></div>', h, re.S).group(0)
        moved = h.replace(box, "").replace('<div class="bi-ap-other">', box + '<div class="bi-ap-other">')
        marks = ["Como apoiar", apoie.OTHER_WAY, "Como cada mês é dividido", "Antes de apoiar"]
        self.assertNotEqual(moved, h, "the plant landed")
        self.assertFalse(in_order(text(moved), marks))
        self.assertFalse(in_order(text(h), ["2. Desenvolvedores", "1. Infraestrutura"]))

    def test_the_texts_that_left_are_gone_and_the_check_catches_each_when_planted(self):
        for profile in ("production", "staging"):
            for data in (on_soon(), on_live()):
                with self.subTest(profile=profile, pix=data["pix"]["status"]):
                    self.assertEqual(removed_texts(text(self.main_view(data, profile))), [])
        h = self.main_view(on_soon())
        for old in [*OLD_TEXTS, "Para onde vai o dinheiro"]:
            with self.subTest(planted=old[:40]):
                planted = h.replace('<h3>Antes de apoiar</h3>', f'<p>{old}</p><h3>Antes de apoiar</h3>')
                self.assertNotEqual(planted, h, "the plant landed")
                self.assertTrue(removed_texts(text(planted)), old)

    def test_the_pix_card_on_live_has_the_button_and_the_view_opens_to_the_campaign(self):
        h = self.main_view(on_live())
        card = re.search(r'<div class="bi-ap-card"><svg class="bi-ap-mark".*?<h4>Pix</h4>.*?</div>', h, re.S).group(0)
        self.assertIn('<button type="button" class="bi-ap-cta" data-go="pix">Apoiar com Pix</button>', card)
        self.assertNotIn("Em breve", card)
        view = re.search(r'<section class="bi-ap-view" data-view="pix" hidden>.*?</section>', h, re.S).group(0)
        self.assertIn(f'href="{PIX_URL}" target="_blank" rel="noopener">Abrir a vaquinha</a>', view)
        t = text(view)
        for s in ["Apoiar com Pix", *apoie.PIX_STEPS, apoie.PIX_FACTS.replace("{bank}", PIX_NAME)]:
            self.assertIn(s, t, s[:50])
        self.assertIn("6,4% mais R$ 0,50", t)
        self.assertNotIn('data-view="pix"', self.main_view(on_soon()))

    def test_who_receives_joins_one_part_per_open_channel_in_the_order_pix_sponsors_crypto(self):
        parts = [apoie.RECEIVES["pix"], apoie.RECEIVES["sponsors"].replace("{host}", "Open Source Collective"), apoie.RECEIVES["crypto"]]
        t = text(self.main_view(on_live()))
        self.assertIn("Quem recebe: " + "; ".join(parts) + ".", t)
        self.assertIn("o Pix e o cartão vão para a Vakinha, que repassa o valor à pessoa mantenedora; cada repasse é publicado no "
                      "livro-caixa do projeto; o GitHub Sponsors paga ao", t)
        for open_channels, expected in ((("pix",), parts[:1]), (("crypto",), parts[2:]), (("pix", "crypto"), [parts[0], parts[2]])):
            with self.subTest(open=open_channels):
                d = on_live()
                for channel in ("pix", "sponsors", "crypto"):
                    if channel not in open_channels:
                        d[channel]["status"] = "soon"
                self.assertIn("Quem recebe: " + "; ".join(expected) + ".", text(self.main_view(d)))
        link = '<a href="https://opencollective.com/example" target="_blank" rel="noopener">Open Source Collective</a>'
        self.assertIn(link, self.main_view(on_live()), "the host is linked when its address is filled in")

    def test_no_maintainer_cap_anywhere(self):
        self.assertFalse(hasattr(apoie, "DEVELOPERS_CAP"))
        self.assertFalse(hasattr(apoie, "NOT_PAID_BY"))
        d = on_live(); d["maintainer_cap_brl"] = 3000   # a leftover key is ignored, never drawn
        self.assertNotIn("3.000", text(self.main_view(d)))
        self.assertNotIn("maintainer_cap", (TOOLS / "support_data.py").read_text(encoding="utf-8"))

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
                for view in ("pix", "sponsors", "crypto", "contact"):
                    self.assertIn(f'data-view="{view}"', h)
                self.assertNotIn("teto de", t)
                for s in ["Quem recebe", apoie.CRYPTO_CARD, "Apoiar com Pix", apoie.RETURN_RULE.replace("{limit}", "R$ 500,00")]:
                    self.assertIn(re.sub(r"\s+", " ", s), t, s[:50])
                for g in on_live()["crypto"]["groups"]:
                    self.assertIn(g["address"], h)

    def test_staging_draws_the_form_without_the_key(self):
        d = committed(); d["contact_form"]["access_key"] = None
        for key, p in build(d, profile="staging").items():
            with self.subTest(page=key):
                h = p["header"]
                self.assertIn('data-view="contact"', h)
                self.assertIn('data-key=""', h)
                self.assertEqual(len(re.findall(r'<div class="bi-ap-card bi-ap-soon">', h)), 3)
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
                self.assertEqual(len(re.findall(r'<div class="bi-ap-card bi-ap-soon">', h)), 3)
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
