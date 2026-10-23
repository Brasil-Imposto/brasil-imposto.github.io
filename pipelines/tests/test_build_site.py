"""The two builds of the site (spec BRASIL-IMPOSTO_SPEC_staging_2026-10-23, sections 3 and 7): production is the committed pages
byte for byte plus robots.txt, carries no feature switched off in production, and staging writes nothing into the repository.
Every rule has a planted failure."""
import hashlib
import importlib.util
import json
import os
import re
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
MARKS = {"apoie": ("bi-apoie", "bi-ap-", "bi-apoie-css")}


def status():
    """The state of every committed file: git status, and the hash of the diff, so a write into a file already changed counts."""
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, check=True).stdout
    return git("status", "--porcelain", "--untracked-files=no").decode() + hashlib.sha256(git("diff", "--binary")).hexdigest()


def run(profile, out, env=None):
    subprocess.run(["python3", str(TOOLS / "build-site.py"), "--profile", profile, "--out", str(out)], check=True, cwd=REPO,
                   env={**os.environ, **(env or {})}, stdout=subprocess.DEVNULL)


def leaks(site, data):
    """The marks of each feature switched off in production that are in a built page."""
    out = []
    for f in data["features"]:
        if f["production"]:
            continue
        for page in sorted(Path(site).glob("*.html")):
            text = page.read_text(encoding="utf-8")
            out += [f"{page.name}: {f['key']} ({m})" for m in MARKS[f["key"]] if m in text]
    return out


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
        for key, (name, _) in site_chrome.PAGES.items():
            with self.subTest(page=key):
                built = self.prod / ("index.html" if key == "inicio" else name)
                self.assertEqual(built.read_bytes(), (PREVIEWS / name).read_bytes())
        self.assertEqual((self.prod / "robots.txt").read_text(encoding="utf-8"), "User-agent: *\nDisallow: /staging/\n")
        self.assertEqual((self.prod / site_chrome.HOME).read_text(encoding="utf-8"), build_site.FORWARD)
        self.assertEqual(sorted(p.name for p in self.prod.iterdir()), sorted(
            [".nojekyll", "assets", "index.html", "robots.txt", site_chrome.HOME] + [n for k, (n, _) in site_chrome.PAGES.items() if k != "inicio"]))

    def test_nothing_switched_off_leaks_into_production(self):
        data = json.loads((REPO / "data" / "features.json").read_text(encoding="utf-8"))
        self.assertEqual(leaks(self.prod, data), [])

    def test_control_apoie_on_in_production_is_found(self):
        tmp = Path(self.tmp.name)
        support = json.loads((REPO / "data" / "support.json").read_text(encoding="utf-8"))
        support["contact_form"]["access_key"] = ACCESS_KEY
        switched = {"features": [{"key": "apoie", "issue": 46, "description": "O botão Apoie", "staging": True, "production": True}]}
        (tmp / "support.json").write_text(json.dumps(support), encoding="utf-8")
        (tmp / "features.json").write_text(json.dumps(switched), encoding="utf-8")
        site = tmp / "control"
        site.mkdir()
        for key, (name, _) in site_chrome.PAGES.items():   # the committed pages with apoie built in, as production would make them
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
        self.assertEqual(len(found), 3 * len(MARKS["apoie"]), found)

    def test_staging_marks_every_page_and_builds_apoie(self):
        for key, (name, _) in site_chrome.PAGES.items():
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
