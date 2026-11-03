"""No page carries code the CSP would have to allow inline (spec seguranca-doacoes, section 8; D219, Uniswap's form)."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREVIEWS = ROOT / "docs" / "superpowers" / "previews"
PAGES = ("BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html", "como-ler-o-mapa.html", "como-o-dinheiro-anda.html", "os-3-poderes.html")
DATA_TYPES = {"application/json"}


class _Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inline, self.handlers, self.js_urls, self.srcs, self._cur = [], [], [], [], None

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.handlers += [f"{tag} {k}" for k, _ in attrs if k.startswith("on")]
        self.js_urls += [v for k, v in attrs if k in ("href", "src", "action") and v and v.strip().lower().startswith("javascript:")]
        if tag == "script":
            if d.get("src") or d.get("data-src"):
                self.srcs.append(d.get("src") or d.get("data-src"))
            self._cur = (d.get("type") or "text/javascript", [])

    def handle_data(self, data):
        if self._cur:
            self._cur[1].append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._cur:
            kind, body = self._cur
            if "".join(body).strip() and kind not in DATA_TYPES:
                self.inline.append(kind)
            self._cur = None


def scan(html):
    s = _Scripts()
    s.feed(html)
    return s


import importlib.util
_spec = importlib.util.spec_from_file_location("csp", ROOT / "docs" / "superpowers" / "tools" / "csp.py")
csp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(csp)


class NoInlineCodeTest(unittest.TestCase):
    def test_pages_have_no_inline_code(self):
        for name in PAGES:
            with self.subTest(page=name):
                s = scan((PREVIEWS / name).read_text(encoding="utf-8"))
                self.assertEqual(s.inline, [], "inline scripts (importmap included)")
                self.assertEqual(s.handlers, [], "on* attributes")
                self.assertEqual(s.js_urls, [], "javascript: links")

    def test_our_scripts_write_no_handler_attributes(self):
        handler = re.compile(r"\son[a-z]+\s*=\s*[\"']")
        for f in sorted((PREVIEWS / "assets").glob("*.js")):
            with self.subTest(file=f.name):
                self.assertIsNone(handler.search(f.read_text(encoding="utf-8")))

    def test_the_scan_sees_inline_code(self):   # the control: the same scan on a page with each planted defect
        s = scan('<script>x()</script><script type="importmap">{}</script><img src="a" onerror="x()"><a href="javascript:x()">a</a>'
                 '<script type="application/json">{}</script>')
        self.assertEqual((s.inline, s.handlers, len(s.js_urls)), (["text/javascript", "importmap"], ["img onerror"], 1))


class PolicyTest(unittest.TestCase):
    def test_script_src_is_origins_only(self):
        script = dict(csp.DIRECTIVES)["script-src"]
        for banned in ("'unsafe-inline'", "'unsafe-eval'", "'strict-dynamic'", "data:", "blob:", "*", "https:"):
            self.assertNotIn(banned, script)
        self.assertEqual(dict(csp.DIRECTIVES)["object-src"], ("'none'",))
        self.assertEqual(dict(csp.DIRECTIVES)["base-uri"], ("'none'",))

    def test_every_page_has_the_meta_first(self):
        for name in PAGES:
            with self.subTest(page=name):
                html = (PREVIEWS / name).read_text(encoding="utf-8")
                self.assertEqual(html.count('http-equiv="Content-Security-Policy"'), 1)
                at = html.index(csp.META)
                self.assertLess(at, html.index("<script"))
                self.assertLess(at, html.index("<link"))

    def test_every_script_is_allowed(self):
        allowed = set(dict(csp.DIRECTIVES)["script-src"])
        for name in PAGES:
            for src in scan((PREVIEWS / name).read_text(encoding="utf-8")).srcs:
                with self.subTest(page=name, src=src):
                    self.assertTrue(src.startswith("assets/") or src in allowed, src)
