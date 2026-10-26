"""The two builds of the site (spec BRASIL-IMPOSTO_SPEC_staging_2026-10-23, sections 3 and 7): production is the committed pages
byte for byte plus robots.txt, carries no feature switched off in production, and staging writes nothing into the repository.
Every rule has a planted failure."""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "docs" / "superpowers" / "tools"
PREVIEWS = TOOLS.parent / "previews"
_spec = importlib.util.spec_from_file_location("build_site", TOOLS / "build-site.py")
build_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_site)
site_chrome = build_site.site_chrome
ACCESS_KEY = "00000000-1111-4222-8333-444444444444"   # a dummy Web3Forms access key, for these tests only
# what each switch leaves in a page when it is built in: its class names, its style and its script
MARKS = {"apoie": ("bi-apoie", "bi-ap-", "bi-apoie-css"),
         "trade": ("data-trade", "o-que-o-brasil-vende", "home-trade", "BIHT", "O que o Brasil vende ao exterior, produto por produto"),
         "rede": ('id="rede"', "data-graph", "ledger-graph", "3d-force-graph", "bi-ledger-interest", "platform.css", "Rede do dinheiro", "#rede")}
# what a switch's content leaves in a script or style of assets/ (home-feed.js keeps the hook window.BIHT and names its file in a
# comment, so in assets/ only the section itself counts, with its own files)
ASSET_MARKS = {"apoie": ("bi-apoie-css",), "trade": ("data-trade", "o-que-o-brasil-vende", "O que o Brasil vende ao exterior, produto por produto"),
               "rede": ("data-graph-stage", "BILGV")}


def status():
    """The state of every committed file: git status, and the hash of the diff, so a write into a file already changed counts."""
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, check=True).stdout
    return git("status", "--porcelain", "--untracked-files=no").decode() + hashlib.sha256(git("diff", "--binary")).hexdigest()


def run(profile, out, env=None):
    subprocess.run(["python3", str(TOOLS / "build-site.py"), "--profile", profile, "--out", str(out)], check=True, cwd=REPO,
                   env={**os.environ, **(env or {})}, stdout=subprocess.DEVNULL)


def leaks(site, data):
    """The marks of each feature switched off in production that are in a built page or in a file of its assets/ (its own
    files are left out of the build, so a mark in any other file is a leak too)."""
    out = []
    files = sorted(Path(site).glob("*.html")) + sorted(p for p in (Path(site) / "assets").glob("*") if p.suffix in (".js", ".css"))
    for f in data["features"]:
        if f["production"]:
            continue
        for page in files:
            text = page.read_text(encoding="utf-8")
            marks = MARKS[f["key"]] if page.suffix == ".html" else ASSET_MARKS[f["key"]]
            out += [f"{page.name}: {f['key']} ({m})" for m in marks if m in text]
            out += [f"{page.name}: {f['key']} (file)" for fn in build_site.FEATURES.get(f["key"], {}).get("files", ()) if page.name == fn]
    return out


def built(profile, features_json, key):
    """One committed page as build-site.py makes it for the profile, under another features file (with_features, then the
    staging chrome for staging)."""
    old = os.environ.get("BI_FEATURES_JSON")
    os.environ["BI_FEATURES_JSON"] = str(features_json)
    try:
        page = build_site.with_features((PREVIEWS / site_chrome.ALL_PAGES[key][0]).read_text(encoding="utf-8"), key, profile)
        return page if profile == "production" else build_site.staging_page(page, key)
    finally:
        os.environ.pop("BI_FEATURES_JSON") if old is None else os.environ.__setitem__("BI_FEATURES_JSON", old)


class BuildSiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.before = status()
        cls.prod, cls.stage = Path(cls.tmp.name) / "production", Path(cls.tmp.name) / "staging"
        run("production", cls.prod)
        run("staging", cls.stage)
        cls.after = status()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_production_is_the_committed_pages_plus_robots(self):
        for key, (name, _) in site_chrome.ALL_PAGES.items():
            with self.subTest(page=key):
                built = self.prod / ("index.html" if key == "inicio" else name)
                self.assertEqual(built.read_bytes(), (PREVIEWS / name).read_bytes())
        self.assertEqual((self.prod / "robots.txt").read_text(encoding="utf-8"), "User-agent: *\nDisallow: /staging/\n")
        self.assertEqual((self.prod / site_chrome.HOME).read_text(encoding="utf-8"), build_site.FORWARD)
        self.assertEqual(sorted(p.name for p in self.prod.iterdir()), sorted(
            [".nojekyll", "assets", "index.html", "robots.txt", site_chrome.HOME] + [n for k, (n, _) in site_chrome.ALL_PAGES.items() if k != "inicio"]))

    def test_nothing_switched_off_leaks_into_production(self):
        data = json.loads((REPO / "data" / "features.json").read_text(encoding="utf-8"))
        self.assertEqual(leaks(self.prod, data), [])

    def test_control_apoie_on_in_production_is_found(self):
        tmp = Path(self.tmp.name)
        support = json.loads((REPO / "data" / "support.json").read_text(encoding="utf-8"))
        support["contact_form"]["access_key"] = ACCESS_KEY
        switched = {"features": [{"key": "apoie", "issue": 46, "description": "O botão Apoie", "staging": True, "production": True},
                                 {"key": "rede", "issue": 130, "description": "A prévia da Rede do dinheiro", "staging": True, "production": False}]}
        (tmp / "support.json").write_text(json.dumps(support), encoding="utf-8")
        (tmp / "features.json").write_text(json.dumps(switched), encoding="utf-8")
        site = tmp / "control"
        site.mkdir()
        for key, (name, _) in site_chrome.ALL_PAGES.items():   # the committed pages with apoie built in, as production would make them
            env = {"BI_SUPPORT_JSON": str(tmp / "support.json"), "BI_FEATURES_JSON": str(tmp / "features.json")}
            old = {k: os.environ.get(k) for k in env}
            os.environ.update(env)
            try:
                page = site_chrome.inject((PREVIEWS / name).read_text(encoding="utf-8"), key, "production")
            finally:
                for k, v in old.items():
                    os.environ.pop(k) if v is None else os.environ.__setitem__(k, v)
            (site / name).write_text(page, encoding="utf-8")
        off = json.loads((REPO / "data" / "features.json").read_text(encoding="utf-8"))   # the leak check sees apoie as switched off
        for f in off["features"]:
            if f["key"] == "apoie":
                f["production"] = False
        found = leaks(site, off)
        self.assertEqual(len(found), len(site_chrome.ALL_PAGES) * len(MARKS["apoie"]), found)

    def test_trade_is_off_in_production_and_on_in_staging(self):
        data = json.loads((REPO / "data" / "features.json").read_text(encoding="utf-8"))
        trade = next(f for f in data["features"] if f["key"] == "trade")
        self.assertEqual((trade["staging"], trade["production"]), (True, False))
        for fn in build_site.FEATURES["trade"]["files"]:
            self.assertFalse((self.prod / "assets" / fn).exists(), fn)
            self.assertTrue((self.stage / "assets" / fn).exists(), fn)
        page = (self.stage / "index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('<link rel="stylesheet" href="assets/home-trade.css">'), 1)
        self.assertEqual(page.count('<script type="text/x-bi-deferred" data-src="assets/home-trade.js"></script>'), 1)
        self.assertLess(page.index('data-src="assets/home-feed.js"'), page.index('data-src="assets/home-trade.js"'),
                        "home-trade.js reads home-feed.js's helpers, so it runs after it")

    def test_control_trade_on_in_production_is_found(self):
        tmp = Path(self.tmp.name)
        data = json.loads((REPO / "data" / "features.json").read_text(encoding="utf-8"))
        for f in data["features"]:
            if f["key"] == "trade":
                f["production"] = True
        (tmp / "trade-on.json").write_text(json.dumps(data), encoding="utf-8")
        site = tmp / "trade-control"
        shutil.copytree(self.stage / "assets", site / "assets")   # the assets a build with trade on carries
        (site / "index.html").write_text(built("production", tmp / "trade-on.json", "inicio"), encoding="utf-8")
        for f in data["features"]:   # the leak check sees trade as switched off
            if f["key"] == "trade":
                f["production"] = False
        found = leaks(site, data)
        self.assertIn("index.html: trade (home-trade)", found)
        self.assertIn("home-trade.js: trade (file)", found)
        self.assertIn("home-trade.css: trade (file)", found)

    def test_rede_is_off_in_production_and_on_in_staging(self):
        data = json.loads((REPO / "data" / "features.json").read_text(encoding="utf-8"))
        rede = next(f for f in data["features"] if f["key"] == "rede")
        self.assertEqual((rede["staging"], rede["production"]), (True, False))
        for fn in build_site.FEATURES["rede"]["files"]:
            self.assertFalse((self.prod / "assets" / fn).exists(), fn)
            self.assertTrue((self.stage / "assets" / fn).exists(), fn)
        page = (self.stage / "index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('id="rede"'), 1)
        self.assertEqual(page.count('<link rel="stylesheet" href="assets/platform.css">'), 1)
        self.assertEqual(page.count('<script type="text/x-bi-deferred" data-src="assets/ledger-graph-view.js"></script>'), 1)
        self.assertLess(page.index('id="para-onde-vai"'), page.index('id="rede"'))
        for key, (name, _) in site_chrome.ALL_PAGES.items():
            with self.subTest(page=key):
                stage = (self.stage / ("index.html" if key == "inicio" else name)).read_text(encoding="utf-8")
                self.assertEqual(stage.count(">Rede do dinheiro (prévia)</a>"), 1)

    def test_control_rede_on_in_production_is_found(self):
        tmp = Path(self.tmp.name)
        data = json.loads((REPO / "data" / "features.json").read_text(encoding="utf-8"))
        for f in data["features"]:
            if f["key"] == "rede":
                f["production"] = True
        (tmp / "rede-on.json").write_text(json.dumps(data), encoding="utf-8")
        site = tmp / "rede-control"
        shutil.copytree(self.stage / "assets", site / "assets")   # the assets a build with rede on carries
        (site / "index.html").write_text(built("production", tmp / "rede-on.json", "inicio"), encoding="utf-8")
        for f in data["features"]:   # the leak check sees rede as switched off
            if f["key"] == "rede":
                f["production"] = False
        found = leaks(site, data)
        self.assertIn('index.html: rede (id="rede")', found)
        self.assertIn("index.html: rede (ledger-graph)", found)
        self.assertIn("platform.css: rede (file)", found)
        self.assertIn("ledger-graph-view.js: rede (file)", found)

    def test_staging_marks_every_page_and_builds_apoie(self):
        for key, (name, _) in site_chrome.ALL_PAGES.items():
            with self.subTest(page=key):
                page = (self.stage / ("index.html" if key == "inicio" else name)).read_text(encoding="utf-8")
                self.assertEqual(page.count('<meta name="robots" content="noindex">'), 1)
                self.assertEqual(page.count('class="bi-staging"'), 1)
                self.assertLess(page.index('class="bi-staging"'), page.index('class="bi-header"'), "the strip comes first")
                self.assertIn("s.style.top = Math.max(0, h.getBoundingClientRect().bottom)", page, "the phone menu follows the header")
                text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page))
                self.assertIn("Ambiente de testes: inclui ideias ainda não aprovadas. O site oficial é brasil-imposto.github.io", text)
                self.assertEqual(page.count('class="bi-apoie-btn"'), 1, "apoie is on in staging")
                self.assertNotIn("a definir", text)
        self.assertFalse((self.stage / "robots.txt").exists())

    def test_staging_writes_nothing_into_the_repository(self):
        self.assertEqual(self.after, self.before)

    def test_control_a_build_that_writes_a_committed_file_is_seen(self):
        target = REPO / "data" / "support.json"
        original = target.read_bytes()
        try:
            target.write_bytes(original + b"\n")
            self.assertNotEqual(status(), self.before)
        finally:
            target.write_bytes(original)
        self.assertEqual(status(), self.before)


if __name__ == "__main__":
    unittest.main()
