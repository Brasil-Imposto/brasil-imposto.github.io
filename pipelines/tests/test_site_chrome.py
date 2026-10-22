"""The header shared by the three published pages (D152): every page carries exactly the module's header, CSS and script, the
three headers are equal apart from the current-page mark, and "Rede (prévia)" is not in any header.
The pages read are the committed ones; the Pages workflow rebuilds Início from the same module."""
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "docs" / "superpowers" / "tools"))
import site_chrome  # noqa: E402

PREVIEWS = REPO / "docs" / "superpowers" / "previews"


def page(key):
    return (PREVIEWS / site_chrome.PAGES[key][0]).read_text(encoding="utf-8")


class SiteHeaderTest(unittest.TestCase):
    def test_each_page_carries_the_module_header(self):
        for key in site_chrome.PAGES:
            with self.subTest(page=key):
                p = page(key)
                self.assertEqual(site_chrome.extract(p, "header"), site_chrome.header(key))
                self.assertEqual(site_chrome.extract(p, "css"), site_chrome.CSS)
                self.assertEqual(site_chrome.extract(p, "js"), site_chrome.SCRIPT)
                self.assertEqual(p.count('class="bi-header"'), 1, "one header per page")

    def test_headers_equal_apart_from_the_current_page_mark(self):
        blocks = {k: site_chrome.extract(page(k), "header") for k in site_chrome.PAGES}
        for k, b in blocks.items():
            self.assertEqual(b.count('aria-current="page"'), 2, f"{k}: the current link marked in the bar and in the sheet")
        plain = {re.sub(r' aria-current="page"', "", b) for b in blocks.values()}
        self.assertEqual(len(plain), 1, "the headers differ beyond the current-page mark")

    def test_no_rede_previa_in_the_header(self):
        for key in site_chrome.PAGES:
            text = re.sub(r"<[^>]+>", " ", site_chrome.extract(page(key), "header"))
            self.assertNotRegex(text, r"Rede\s*\(prévia\)")
            self.assertNotIn("Apoie", text)



class SiteFooterTest(unittest.TestCase):
    def test_each_page_carries_the_same_footer(self):
        blocks = set()
        for key in site_chrome.PAGES:
            with self.subTest(page=key):
                p = page(key)
                self.assertEqual(site_chrome.extract(p, "footer"), site_chrome.footer())
                self.assertEqual(p.count('class="bi-footer"'), 1)
                blocks.add(site_chrome.extract(p, "footer"))
        self.assertEqual(len(blocks), 1, "the footers differ")

    def test_footer_links(self):
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", site_chrome.footer()))
        self.assertEqual(len(re.findall(r"Rede do dinheiro \(prévia\)", text)), 1)
        for label in ("Código aberto no GitHub", "Decisões do projeto", "Como ajudar", "Licenças"):
            self.assertEqual(text.count(label), 1, label)
        self.assertIn("Dados oficiais, com fonte em cada número. Código AGPL-3.0, dados CC BY 4.0.", text)


if __name__ == "__main__":
    unittest.main()
