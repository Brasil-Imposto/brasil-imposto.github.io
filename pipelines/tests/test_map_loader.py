"""The map loader of Início (D152, L1) in the committed page: one card, the data file loaded only through the loader, every
later script held back for it, and the size written into the page equal to assets/bi-data.js when that file is built."""
import re
import unittest
from pathlib import Path

PREVIEWS = Path(__file__).resolve().parents[2] / "docs" / "superpowers" / "previews"
HOME = PREVIEWS / "BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html"


class MapLoaderTest(unittest.TestCase):
    def setUp(self):
        self.page = HOME.read_text(encoding="utf-8")

    def test_one_card_and_one_loader(self):
        self.assertEqual(self.page.count('id="bi-loader"'), 1)
        self.assertEqual(self.page.count('<script id="bi-loader-js">'), 1)
        self.assertIn("Carregando os dados oficiais do mapa", self.page)
        self.assertIn("Tentar de novo", self.page)

    def test_data_only_through_the_loader(self):
        self.assertNotIn('<script src="assets/bi-data.js"></script>', self.page)
        held = re.findall(r'<script type="text/x-bi-deferred"', self.page)
        self.assertGreaterEqual(len(held), 15)
        after = self.page.split('<script id="bi-loader-js">', 1)[1]
        live = [m for m in re.findall(r'<script\b[^>]*>', after) if 'x-bi-deferred' not in m and 'bi-chrome-js' not in m]
        self.assertEqual(live, [], "a script after the loader would run before the data")

    def test_size_matches_the_built_file(self):
        m = re.search(r'id="bi-loader"[^>]* data-size="(\d+)"', self.page)
        data = PREVIEWS / "assets" / "bi-data.js"
        if not data.exists():
            self.skipTest("assets/bi-data.js is not built here")
        self.assertIsNotNone(m, "no size in the page")
        self.assertEqual(int(m.group(1)), data.stat().st_size)


if __name__ == "__main__":
    unittest.main()
