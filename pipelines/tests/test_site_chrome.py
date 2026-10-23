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
                p, want = page(key), site_chrome.parts(key)  # with the Apoie parts when data/support.json turns them on
                self.assertEqual(site_chrome.extract(p, "header"), want["header"])
                self.assertEqual(site_chrome.extract(p, "css"), want["css"])
                self.assertEqual(site_chrome.extract(p, "js"), want["js"])
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


class SiteBrandTest(unittest.TestCase):
    """The logo (D153) in the header and footer, and the tab icons in the head, on every page (spec logo-no-site)."""
    LOGO, ICO, TOUCH = "assets/brand/brasil-imposto-logo.svg", "assets/brand/favicon.ico", "assets/brand/apple-touch-icon.png"

    def problems(self, p):
        out = []
        for name in ("header", "footer"):
            block = site_chrome.extract(p, name)
            if f'src="{self.LOGO}"' not in block:
                out.append(f"{name}: no logo")
            if "assets/flags/br.svg" in block:
                out.append(f"{name}: the flag is still there")
        head = site_chrome.extract(p, "css")
        for rel, href in (("icon", self.ICO), ("apple-touch-icon", self.TOUCH)):
            if f'rel="{rel}" href="{href}"' not in head:
                out.append(f"head: no {rel}")
        return out

    def test_every_page_carries_the_logo_and_the_icons(self):
        for key in site_chrome.PAGES:
            with self.subTest(page=key):
                self.assertEqual(self.problems(page(key)), [])

    def test_the_files_exist(self):
        for rel in (self.LOGO, self.ICO, self.TOUCH):
            with self.subTest(file=rel):
                self.assertTrue((PREVIEWS / rel).is_file(), rel)

    def test_control_a_wrong_path_fails(self):
        broken = page("inicio").replace(f'src="{self.LOGO}"', 'src="assets/brand/missing.svg"', 1)
        self.assertNotEqual(broken, page("inicio"), "the plant did not land")
        self.assertIn("header: no logo", self.problems(broken))


class SiteSocialPreviewTest(unittest.TestCase):
    """The social preview (D153, spec social-preview): the Open Graph and Twitter tags in every page's head, and the 1200 x 630 image."""
    IMAGE = "assets/brand/og-image.png"
    TAGS = {
        'property="og:site_name"': "Brasil-Imposto",
        'property="og:type"': "website",
        'property="og:locale"': "pt_BR",
        'property="og:description"': "Para onde vai o imposto, com dados oficiais e a fonte de cada número.",
        'property="og:image"': "https://brasil-imposto.github.io/" + IMAGE,
        'property="og:image:width"': "1200",
        'property="og:image:height"': "630",
        'name="twitter:card"': "summary_large_image",
    }

    def problems(self, p):
        head = site_chrome.extract(p, "css")
        out = [f"head: {attr} is not {value}" for attr, value in self.TAGS.items() if f'<meta {attr} content="{value}">' not in head]
        if 'property="og:image:alt" content="' not in head:
            out.append("head: no og:image:alt")
        return out

    def test_every_page_carries_the_tags(self):
        for key in site_chrome.PAGES:
            with self.subTest(page=key):
                self.assertEqual(self.problems(page(key)), [])

    def test_the_image_is_1200_by_630(self):
        data = (PREVIEWS / self.IMAGE).read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual((int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")), (1200, 630))

    def test_control_a_page_without_the_image_fails(self):
        tag = f'<meta property="og:image" content="https://brasil-imposto.github.io/{self.IMAGE}">'
        broken = page("inicio").replace(tag, "", 1)
        self.assertNotEqual(broken, page("inicio"), "the plant did not land")
        self.assertTrue(any("og:image" in x for x in self.problems(broken)))


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
