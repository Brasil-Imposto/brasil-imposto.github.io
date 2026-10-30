"""The Apoie button's data (spec BRASIL-IMPOSTO_SPEC_apoie_2026-10-23, sections 1 to 10, and spec staging, section 2): data/support.json
stays empty until the maintainer fills it in, and the apoie switch of data/features.json says which build carries the button. Production
may turn it on with the three payment channels (Pix, GitHub Sponsors, crypto) on "soon" and without the contact form's access key (D162: the form stays out until the key is filled); a channel goes "live" only with every one of its values filled and every address in its network's format. The
built pages never show "a definir" and never carry an e-mail address. Each crypto address passes its network's checksum and equals
the address pinned here (section 10.2). Every rule has a planted failure."""
import hashlib
import copy
import html as htmllib
import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest
from html.parser import HTMLParser
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
_spec = importlib.util.spec_from_file_location("build_site", TOOLS / "build-site.py")
build_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_site)

ACCESS_KEY = "00000000-1111-4222-8333-444444444444"   # a dummy Web3Forms access key, for these tests only
PIX_URL = "https://www.vakinha.com.br/vaquinha/teste-da-sonda"   # a dummy campaign, for these tests only
PIX_NAME = "Nome de Teste"
# valid addresses taken from each standard's own text, for these tests only (never in data/support.json): BIP-350's first
# segwit vector, EIP-55's first mixed-case vector, the 32 zero bytes of Solana's system program, the base58 form on TRON's
# Account page and the address of xrpl.org's Addresses page example
DUMMY = {"bitcoin": "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", "evm": "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",
         "solana": "1" * 32, "tron": "TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL", "xrp": "rDTXLQ7ZKZVKz33zJbHjgVShjsBnqMBhmN"}
# The five project addresses, as the maintainer sent them on 2026-10-29. data/support.json must hold exactly these: an address
# changes only together with this line, in the same pull request (section 10.2, item 2).
PINNED = {"bitcoin": "bc1qevkvnl6rvpfyyyjzk08lckz9xn3936qhp86zna", "evm": "0xb947cC8445841cf40AFCA723804d06855bea7bc7",
          "solana": "FUYqFTFwvF8fgm1NmbRXAEERtRLDry1DCQfNgbZyFv8f", "tron": "TLoXMf8yCEtRJcbR3tqidYd76f1hi4r6cU",
          "xrp": "rwJXvMdap5E7C49ZkfAjpeAMLd15UmEch2"}
# the alphabet of each base58 network: Bitcoin's (also Solana's and Tron's) and the XRP Ledger's, copied from xrpl.org
ALPHABET = {"bitcoin": "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz",
            "xrp": "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz"}
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
    """The three channels (Pix, GitHub Sponsors, crypto) on "soon", with the form's access key."""
    d = copy.deepcopy(committed())
    d["contact_form"]["access_key"] = ACCESS_KEY
    d["crypto"]["status"] = "soon"
    return d


def on_soon_crypto_live():
    """The data production goes live with: the access key, the Pix and GitHub Sponsors on "soon", crypto open with XRP on "soon"."""
    d = copy.deepcopy(committed())
    d["contact_form"]["access_key"] = ACCESS_KEY
    return d


def on_live():
    d = on_soon()
    d["pix"].update(status="live", campaign_url=PIX_URL, bank_screen_name=PIX_NAME)
    d["sponsors"].update(status="live", sponsors_url="https://github.com/sponsors/Brasil-Imposto")
    d["sponsors"]["fiscal_host"]["url"] = "https://opencollective.com/example"
    d["crypto"]["status"] = "live"
    for g in d["crypto"]["groups"]:
        g["address"] = DUMMY[g["format"]]
        for n in g["networks"]:
            n["status"] = "live"
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
        self.assertEqual(d["crypto"]["status"], "live", "section 10.1; XRP stays on soon by its network (NetworkStatusTest)")
        self.assertNotIn("unidentified_return_above_brl", d["crypto"], "section 10.1: any amount from any wallet stays")
        # the five project addresses came from the maintainer; each passes its network's format and checksum
        for g in d["crypto"]["groups"]:
            self.assertIsNone(support_data.address_problem(g["format"], g["address"]), g["id"])
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


class NetworkStatusTest(unittest.TestCase):
    """Spec section 10: a status per network. XRP stays "Em breve" until the maintainer's first 1 XRP: its button stays in the row,
    dimmed, with the tag, opens nothing, and the page carries no XRP address."""
    XRP_SOON = ('<button type="button" class="bi-ap-coinbtn bi-ap-coinsoon" disabled><img src="assets/cripto/xrp.svg" alt="" width="20" '
                'height="20" loading="lazy">XRP <span class="bi-ap-tag">Em breve</span></button>')

    def test_the_committed_crypto_is_live_with_xrp_on_soon(self):
        d = committed()
        self.assertEqual(d["crypto"]["status"], "live", "section 10.1: crypto opens in the next production batch")
        status = {n["id"]: n["status"] for g in d["crypto"]["groups"] for n in g["networks"]}
        self.assertEqual(status, {"bitcoin": "live", "ethereum": "live", "bsc": "live", "solana": "live", "tron": "live",
                                  "xrp-ledger": "soon"})

    def test_xrp_on_soon_is_dimmed_and_has_no_address(self):
        for key, p in build(on_soon_crypto_live()).items():
            with self.subTest(page=key):
                h = p["header"]
                self.assertEqual(h.count(self.XRP_SOON), 1)
                self.assertNotIn('data-coin="XRP"', h)
                self.assertNotIn(PINNED["xrp"], h)
                for coin in ("BTC", "ETH", "SOL", "USDT", "USDC", "BNB"):
                    self.assertIn(f'data-coin-btn="{coin}"', h)
                    self.assertIn(f'data-coin="{coin}"', h)
                self.assertIn(".bi-ap-coinbtn.bi-ap-coinsoon {", p["css"])

    def test_control_xrp_live_shows_its_button_panel_and_address(self):
        d = on_soon_crypto_live()
        next(n for g in d["crypto"]["groups"] for n in g["networks"] if n["id"] == "xrp-ledger")["status"] = "live"
        h = build(d)["inicio"]["header"]
        self.assertNotIn(self.XRP_SOON, h)
        self.assertIn('data-coin-btn="XRP"', h)
        self.assertIn('data-coin="XRP"', h)
        self.assertIn(PINNED["xrp"], h)

    def test_a_network_status_outside_soon_and_live_fails(self):
        d = committed()
        d["crypto"]["groups"][0]["networks"][0]["status"] = "open"
        self.assertTrue(any("bitcoin/bitcoin.status" in p for p in support_data.problems(d)))
        d = committed()
        del d["crypto"]["groups"][1]["networks"][1]["status"]
        self.assertTrue(any("evm/bsc.status" in p for p in support_data.problems(d)))


ICONS = REPO / "docs" / "superpowers" / "previews" / "assets" / "cripto"


def svg_problems(text):
    """What an icon file must never hold: a script, an event handler, a javascript: address or anything fetched from outside (an empty
    list: clean)."""
    return re.findall(r"<script|\son\w+\s*=|javascript:|(?:xlink:)?href\s*=\s*[\"'](?:https?:)?//|url\(\s*[\"']?(?:https?:)?//", text, re.I)


class CoinIconTest(unittest.TestCase):
    """Spec section 10, round cripto-envio-r1: each coin button carries the token's icon, left of the name, the dimmed XRP
    included. The icons are the CC0 set cryptocurrency-icons 0.18.1, served from the site itself and loaded only when shown."""

    def test_every_coin_button_carries_its_icon(self):
        for key, p in build(on_soon_crypto_live()).items():
            with self.subTest(page=key):
                h = p["header"]
                for coin in support_data.COINS:
                    img = f'<img src="assets/cripto/{coin.lower()}.svg" alt="" width="20" height="20" loading="lazy">'
                    if coin == "XRP":
                        self.assertIn(f'<button type="button" class="bi-ap-coinbtn bi-ap-coinsoon" disabled>{img}XRP <span class="bi-ap-tag">', h)
                    else:
                        self.assertIn(f'data-coin-btn="{coin}" aria-pressed="false">{img}{coin}</button>', h)
                self.assertIn(".bi-ap-coinbtn img {", p["css"])

    def test_the_icon_files_are_clean_svgs(self):
        names = sorted(f.name for f in ICONS.glob("*.svg"))
        self.assertEqual(names, sorted(f"{c.lower()}.svg" for c in support_data.COINS))
        for f in ICONS.glob("*.svg"):
            with self.subTest(icon=f.name):
                text = f.read_text(encoding="utf-8")
                self.assertTrue(text.lstrip().startswith("<svg"))
                self.assertLess(len(text.encode()), 2048)
                self.assertEqual(svg_problems(text), [])
        self.assertIn("CC0", (ICONS / "LICENSE.txt").read_text(encoding="utf-8"))

    def test_control_a_planted_script_or_outside_reference_is_caught(self):
        clean = (ICONS / "btc.svg").read_text(encoding="utf-8")
        for plant in ('<script>alert(1)</script>', '<g onload="x()"/>', '<image href="https://exemplo.org/x.png"/>',
                      '<a xlink:href="javascript:x()"/>', '<rect style="fill:url(https://exemplo.org/p)"/>'):
            with self.subTest(plant=plant):
                self.assertNotEqual(svg_problems(clean.replace("</svg>", plant + "</svg>")), [])


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
                 "bank_screen_name": lambda d: d["pix"].update(bank_screen_name=None)}
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


class AddressChecksumTest(unittest.TestCase):
    """Section 10.2, item 1: each address passes its network's checksum, not only its shape. The vectors come from each standard's
    own text; the keccak-256 of EIP-55 is pure Python, checked against the known empty-input digest and, with SHA-3's padding,
    against the standard library's sha3_256."""

    def test_keccak_256_matches_the_known_vector_and_sha3_of_the_standard_library(self):
        self.assertEqual(support_data.keccak_256(b"").hex(), "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470")
        for n in (0, 1, 55, 135, 136, 137, 271, 272, 500):   # around the 136-byte block of keccak-256
            data = bytes(range(256)) * 2
            with self.subTest(length=n):
                self.assertEqual(support_data.sponge(data[:n], 0x06), hashlib.sha3_256(data[:n]).digest())

    def test_eip55_vectors(self):
        # the eight addresses of EIP-55's test cases (two whose checksum is all capitals, two all lowercase, four mixed)
        for a in ("0x52908400098527886E0F7030069857D2E4169EE7", "0x8617E340B3D01FA5F11F306F4090FD50E238070D",
                  "0xde709f2102306220921060314715629080e2fb77", "0x27b1fdb04752bbc536007a920d24acb045561c26",
                  "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed", "0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359",
                  "0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB", "0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb"):
            with self.subTest(valid=a):
                self.assertIsNone(support_data.address_problem("evm", a))
        for a in ("0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed", "0x5AAEB6053F3E94C9B9A09F33669435E7EF1BEAED",
                  "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAeD"):
            with self.subTest(invalid=a):
                self.assertIsNotNone(support_data.address_problem("evm", a))

    def test_bech32_and_bech32m_vectors_of_bip_350(self):
        for a in ("BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4",
                  "bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7kt5nd6y", "BC1SW50QGDZ25J",
                  "bc1zw508d6qejxtdg4y5r3zarvaryvaxxpcs", "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0"):
            with self.subTest(valid=a):
                self.assertIsNone(support_data.address_problem("bitcoin", a.lower()))
        for a in ("bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqh2y7hd",      # bech32 instead of bech32m
                  "BC1S0XLXVLHEMJA6C4DQV22UAPCTQUPFHLXM9H8Z3K2E72Q4K9HCZ7VQ54WELL",       # bech32 instead of bech32m
                  "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kemeawh",                          # bech32m instead of bech32
                  "BC130XLXVLHEMJA6C4DQV22UAPCTQUPFHLXM9H8Z3K2E72Q4K9HCZ7VQ7ZWS8R",       # witness version 17
                  "bc1pw5dgrnzv",                                                        # a 1-byte program
                  "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7v8n0nx0muaewav253zgeav",  # 41 bytes
                  "BC1QR508D6QEJXTDG4Y5R3ZARVARYV98GJ9P",                                 # 16 bytes at version 0
                  "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7v07qwwzcrf",      # zero padding over 4 bits
                  "bc1gmk9yu",                                                           # no data
                  "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7"):     # a valid testnet address
            with self.subTest(invalid=a):
                self.assertIsNotNone(support_data.address_problem("bitcoin", a.lower()))

    def test_legacy_bitcoin_addresses_of_bitcoin_core(self):
        # main-chain addresses of Bitcoin Core's src/test/data/key_io_valid.json, with the hash its script holds
        for a, h in (("1FsSia9rv4NeEwvJ2GvXrX7LyxYspbN2mo", "a31c06bd463e3923bc1aadbde48b16976c080717"),
                     ("36j4NfKv6Akva9amjWrLG6MuSQym1GuEmm", "373b819a068f32b7a6b38b6b38729647cfde01c2")):
            with self.subTest(valid=a):
                self.assertIsNone(support_data.address_problem("bitcoin", a))
                self.assertEqual(support_data.base58check(a, ALPHABET["bitcoin"])[1:].hex(), h)

    def test_tron_and_xrp_decode_to_the_bytes_their_documentation_gives(self):
        for a, h in (("TDp4x8kCJ6aHz8wnqZgkaVQAm2ajH1og3L", "412a260a110bc7b03f19c40a0bd04ff2c5dcb57594"),
                     ("TNPeeaaFB7K9cmo4uQpcU32zGK8G1NYqeL", "418840e6c55b9ada326d211d818c34a994aeced808")):
            with self.subTest(tron=a):
                self.assertIsNone(support_data.address_problem("tron", a))
                self.assertEqual(support_data.base58check(a, ALPHABET["bitcoin"]).hex(), h)
        for a, h in (("rrrrrrrrrrrrrrrrrrrrrhoLvTp", "00" * 21), ("rrrrrrrrrrrrrrrrrrrrBZbvji", "00" * 20 + "01")):
            with self.subTest(xrp=a):
                self.assertIsNone(support_data.address_problem("xrp", a))
                self.assertEqual(support_data.base58check(a, ALPHABET["xrp"]).hex(), h)
        for a in ("rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", "rDTXLQ7ZKZVKz33zJbHjgVShjsBnqMBhmN"):
            with self.subTest(xrp=a):
                self.assertIsNone(support_data.address_problem("xrp", a))
        self.assertIsNotNone(support_data.address_problem("tron", "TDp4x8kCJ6aHz8wnqZgkaVQAm2ajH1og3M"))
        self.assertIsNotNone(support_data.address_problem("xrp", "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTi"))

    def test_solana_is_32_bytes(self):
        self.assertIsNone(support_data.address_problem("solana", "1" * 32))
        self.assertEqual(support_data.b58decode(PINNED["solana"], ALPHABET["bitcoin"]).__len__(), 32)
        # Solana addresses run from 32 to 44 characters, so one character less can still be 32 bytes: two less is 31 here
        self.assertEqual(len(support_data.b58decode(PINNED["solana"][:-1], ALPHABET["bitcoin"])), 32)
        self.assertIsNotNone(support_data.address_problem("solana", PINNED["solana"][:-2]), "31 bytes")
        self.assertIsNotNone(support_data.address_problem("solana", PINNED["solana"] + "z"), "33 bytes")
        self.assertIsNotNone(support_data.address_problem("solana", "1" * 33), "33 zero bytes")

    def test_control_every_one_character_change_of_a_project_address_fails(self):
        """Every substitution inside the address's own alphabet (so the shape still passes) and, on the 0x address, every flip of a
        letter's case. Solana has no checksum: a substitution keeps its 32 bytes, and the pin (PinnedAddressesTest) is what
        catches it there."""
        hexdigits = "0123456789abcdefABCDEF"
        for fmt, a in PINNED.items():
            if fmt == "solana":
                continue
            alphabet = {"bitcoin": "qpzry9x8gf2tvdw0s3jn54khce6mua7l", "evm": hexdigits, "tron": ALPHABET["bitcoin"],
                        "xrp": ALPHABET["xrp"]}[fmt]
            start = {"bitcoin": 3, "evm": 2, "tron": 1, "xrp": 1}[fmt]
            passed, tried = [], 0
            for i in range(start, len(a)):
                for ch in alphabet:
                    if ch == a[i]:
                        continue
                    b = a[:i] + ch + a[i + 1:]
                    if not support_data.FORMATS[fmt].match(b):
                        continue
                    tried += 1
                    if support_data.address_problem(fmt, b) is None:
                        passed.append(b)
            with self.subTest(fmt=fmt, tried=tried):
                self.assertGreater(tried, 100)
                self.assertEqual(passed, [], f"{len(passed)} of {tried} changes passed")

    def test_a_bad_address_fails_in_any_status(self):
        for status in ("soon", "live"):
            for g in range(5):
                with self.subTest(status=status, group=g):
                    d = on_live() if status == "live" else committed()
                    a = d["crypto"]["groups"][g]["address"]
                    # Solana has no checksum: its plant is one the 32-byte rule can see (two characters less, 31 bytes)
                    planted = a[:-2] if d["crypto"]["groups"][g]["format"] == "solana" else a[:-1] + ("2" if a[-1] != "2" else "3")
                    d["crypto"]["groups"][g]["address"] = planted
                    self.assertTrue(any("is not a valid" in p for p in support_data.problems(d)), planted)


SRI = re.compile(r"^sha(256|384|512)-[A-Za-z0-9+/]+={0,2}$")
OUTSIDE = re.compile(r"^(https?:)?//")


class _Scripts(HTMLParser):
    """Every script element of a page, as [attributes, text]: the standard library's parser, which reads tag and attribute names
    in any case, an end tag with spaces, and a script's content as raw text."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.found, self.open = [], None

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.open = [dict(attrs), ""]
            self.found.append(self.open)

    def handle_data(self, data):
        if self.open is not None:
            self.open[1] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self.open = None


def scripts(page):
    p = _Scripts()
    p.feed(page)
    p.close()
    return p.found


def outside_without_integrity(page):
    """Each script a page loads from another site without an integrity hash (an empty list: none). A script element with an outside
    src needs integrity and crossorigin="anonymous"; one the map loader holds back needs data-integrity; through an import map,
    every outside address it maps exactly, and every module the page's own code imports through it, needs an integrity entry
    (the modules those import in turn: apoie-check.cjs, the sri check, tampers with every outside file in a real browser)."""
    out, found = [], scripts(page)
    for attrs, _body in found:
        held = "data-src" in attrs
        src = attrs.get("data-src" if held else "src") or ""
        if OUTSIDE.match(src):
            sri = attrs.get("data-integrity" if held else "integrity") or ""
            if not (SRI.match(sri) and (held or attrs.get("crossorigin") == "anonymous")):
                out.append(src)
    maps = [json.loads(body) for attrs, body in found if attrs.get("type") == "importmap"]
    imports = {k: v for m in maps for k, v in m.get("imports", {}).items()}
    integrity = {k: v for m in maps for k, v in m.get("integrity", {}).items()}
    out += [u for u, h in integrity.items() if not SRI.match(h)]
    out += [u for u in imports.values() if OUTSIDE.match(u) and not u.endswith("/") and u not in integrity]
    code = "\n".join(body for attrs, body in found if attrs.get("type") == "module" or "data-module" in attrs)
    for a, b in re.findall(r"""(?:import|export)\s[^'";]*?from\s*['"]([^'"]+)['"]|import\s*\(\s*['"]([^'"]+)['"]""", code):
        spec = a or b
        prefix = max((k for k in imports if k.endswith("/") and spec.startswith(k)), key=len, default=None)
        url = imports.get(spec) or (imports[prefix] + spec[len(prefix):] if prefix else spec)
        if OUTSIDE.match(url) and url not in integrity:
            out.append(url)
    return out


def published(profile):
    """Each page with the Apoie button as the site build serves it in the profile (build-site.py, without running the builders)."""
    pages = {}
    for key, (name, _label) in site_chrome.ALL_PAGES.items():
        page = build_site.with_features((REPO / "docs" / "superpowers" / "previews" / name).read_text(encoding="utf-8"), key, profile)
        pages[key] = page if profile == "production" else build_site.staging_page(page, key)
    return pages


class OutsideScriptsTest(unittest.TestCase):
    """Section 10.2, item 4: a file changed on a CDN could swap the address a donor sees, so no page with the Apoie button runs a
    script from another site without its hash."""

    def test_every_page_with_the_button_checks_each_outside_script(self):
        for profile in ("production", "staging"):
            for key, page in published(profile).items():
                with self.subTest(profile=profile, page=key):
                    self.assertIn('class="bi-apoie-btn"', page)
                    self.assertEqual(outside_without_integrity(page), [])

    def test_the_pages_load_what_the_hashes_cover(self):
        """The outside scripts as measured on 2026-10-29: d3 and d3-sankey on Como o dinheiro anda, the seven three.js modules of
        Início (the five its code imports and the two Line2 imports), and 3d-force-graph on the staging Início (the money network
        preview, D172)."""
        prod, stag = published("production"), published("staging")
        self.assertIn('<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js" integrity="sha384-', prod["dinheiro"])
        m = json.loads(next(body for attrs, body in scripts(prod["inicio"]) if attrs.get("type") == "importmap"))
        self.assertEqual(sorted(u.rsplit("/", 1)[1] for u in m["integrity"]),
                         ["CSS2DRenderer.js", "Line2.js", "LineGeometry.js", "LineMaterial.js", "LineSegments2.js",
                          "LineSegmentsGeometry.js", "three.module.js"])
        self.assertIn('data-src="https://cdn.jsdelivr.net/npm/3d-force-graph@1.80.0/dist/3d-force-graph.min.js" data-integrity="sha384-',
                      stag["inicio"])

    def test_control_each_hash_removed_or_broken_is_caught(self):
        prod, stag = published("production"), published("staging")
        cases = {
            "d3 without integrity": (prod["dinheiro"], lambda p: re.sub(r'(d3\.min\.js") integrity="[^"]+"', r"\1", p)),
            "d3-sankey without crossorigin": (prod["dinheiro"], lambda p: re.sub(r'(d3-sankey\.min\.js" integrity="[^"]+") crossorigin="anonymous"', r"\1", p)),
            "a three.js module out of the list": (prod["inicio"], lambda p: re.sub(r'\s*"[^"]+/LineMaterial\.js": "sha384-[^"]+",?', "", p)),
            "three.module.js out of the list": (prod["inicio"], lambda p: re.sub(r'\s*"[^"]+/three\.module\.js": "sha384-[^"]+",?', "", p)),
            "a hash that is not one": (prod["inicio"], lambda p: re.sub(r'(/Line2\.js": ")sha384-[^"]+', r"\1md5-abc", p)),
            "the held 3d-force-graph without data-integrity": (stag["inicio"], lambda p: re.sub(r' data-integrity="[^"]+"', "", p)),
            "a new outside script": (prod["tres-poderes"], lambda p: p.replace("</body>", '<script src="https://cdn.example.org/x.js"></script></body>')),
            "one in capitals, with a spaced end tag": (prod["tres-poderes"],
                                                       lambda p: p.replace("</body>", '<SCRIPT SRC="https://cdn.example.org/x.js"></SCRIPT ></body>')),
        }
        for name, (page, plant) in cases.items():
            with self.subTest(plant=name):
                planted = plant(page)
                self.assertNotEqual(planted, page, "the plant landed")
                self.assertNotEqual(outside_without_integrity(planted), [], name)


PAGE_WIDE_COPY = re.compile(r"""closest\(\s*['"]\[data-copy\]['"]\s*\)""")


def page_wide_copy_listeners(page):
    """A click listener of the page, or of a script of ours it loads, that catches every [data-copy] button (an empty list: none).
    Such a listener also catches the modal's "Copiar" and writes something else after it: the digits only (the case cards'
    CNPJ copy) or the page's address (the links of Os 3 Poderes) in place of the crypto address. Section 10.2, item 3."""
    found = [f"page: {m}" for m in PAGE_WIDE_COPY.findall(page)]
    for attrs, _body in scripts(page):
        src = (attrs.get("src") or attrs.get("data-src") or "").split("?")[0]
        f = REPO / "docs" / "superpowers" / "previews" / src
        if src.startswith("assets/") and src.endswith(".js") and f.exists():
            found += [f"{src}: {m}" for m in PAGE_WIDE_COPY.findall(f.read_text(encoding="utf-8"))]
    return found


class CopyTest(unittest.TestCase):
    def test_no_page_catches_every_copy_button(self):
        for profile in ("production", "staging"):
            for key, page in published(profile).items():
                with self.subTest(profile=profile, page=key):
                    self.assertEqual(page_wide_copy_listeners(page), [])

    def test_control_a_page_wide_copy_listener_is_caught(self):
        page = published("production")["dinheiro"]
        planted = page.replace("</body>", "<script>document.addEventListener('click', (e) => { const c = e.target.closest('[data-copy]'); });"
                                          "</script></body>")
        self.assertNotEqual(planted, page, "the plant landed")
        self.assertEqual(len(page_wide_copy_listeners(planted)), 1)
        self.assertIn("assets/cases.js", published("production")["inicio"], "the scripts a page loads are read too")


def pin_diff(data):
    """The groups of data whose address differs from PINNED (an empty list: every address as pinned)."""
    return [g["id"] for g in data["crypto"]["groups"] if PINNED.get(g["format"]) != g["address"]] \
        + sorted(set(PINNED) - {g["format"] for g in data["crypto"]["groups"]})


class PinnedAddressesTest(unittest.TestCase):
    def test_the_committed_addresses_are_the_pinned_ones(self):
        self.assertEqual(pin_diff(committed()), [])
        self.assertEqual(len(committed()["crypto"]["groups"]), 5)

    def test_control_any_change_of_one_address_is_caught(self):
        for g in range(5):
            with self.subTest(group=g):
                d = committed()
                a = d["crypto"]["groups"][g]["address"]
                d["crypto"]["groups"][g]["address"] = a[:5] + ("A" if a[5] != "A" else "B") + a[6:]
                self.assertEqual(pin_diff(d), [d["crypto"]["groups"][g]["id"]])
        d = committed(); del d["crypto"]["groups"][4]
        self.assertEqual(pin_diff(d), ["xrp"], "a group that left is caught too")


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
                for s in ["Quem recebe", apoie.CRYPTO_CARD, "Apoiar com Pix"]:
                    self.assertIn(re.sub(r"\s+", " ", s), t, s[:50])
                self.assertNotIn("Doação acima de", t, "section 10.1: the return rule left the crypto view")
                self.assertNotIn("bi-ap-rule", h + p["css"])
                for g in on_live()["crypto"]["groups"]:
                    self.assertIn(g["address"], h)

    def test_staging_draws_the_form_without_the_key(self):
        d = committed(); d["contact_form"]["access_key"] = None
        for key, p in build(d, profile="staging").items():
            with self.subTest(page=key):
                h = p["header"]
                self.assertIn('data-view="contact"', h)
                self.assertIn('data-key=""', h)
                # the Pix and GitHub Sponsors on soon; crypto open (section 10.1)
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
