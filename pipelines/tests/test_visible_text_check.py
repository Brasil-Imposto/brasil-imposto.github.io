"""The ci's visible-text check (spec paridade-enderecos-formatador, part A; D194): which pull requests skip the comparison, and
how a difference is reported. Controls: a change under data/ or in a builder must not skip; one changed word must be reported
with its line on both sides. The comparison itself runs in the visible-text workflow, where a planted word fails it.
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("visible_text_check", Path(__file__).resolve().parents[2] / "docs/superpowers/tools/visible-text-check.py")
vt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vt)


class VisibleTextCheckTest(unittest.TestCase):
    def test_a_docs_only_pull_request_skips(self):
        self.assertEqual(vt.touches_pages(["README.md", "docs/decisions/README.md", ".github/workflows/dco.yml", "CHANGELOG.md"]), [])

    def test_control_data_and_builders_do_not_skip(self):
        changed = ["data/series/state-budgets.json", "docs/superpowers/tools/site_chrome.py", "docs/superpowers/previews/os-3-poderes.html",
                   "pipelines/siconfi/build_state_budgets.py", "schemas/state.schema.json"]
        self.assertEqual(vt.touches_pages(changed), changed)

    def test_equal_texts_have_no_difference(self):
        self.assertEqual(vt.differences({"inicio:hero": "a\nb"}, {"inicio:hero": "a\nb"}), [])

    def test_control_one_changed_word_is_reported_with_its_line(self):
        self.assertEqual(vt.differences({"inicio:hero": "a\nComo ajudar\nc"}, {"inicio:hero": "a\nComo ajudarr\nc"}),
                         [("inicio:hero", 2, "Como ajudar", "Como ajudarr")])

    def test_control_a_page_missing_on_one_side_is_reported(self):
        self.assertEqual(vt.differences({"notas:page": "x"}, {}), [("notas:page", 1, "x", "<nada>")])


def fake_tree(root, switch_in_production, with_switches=True):
    """A tree with only what pages_of reads: a site_chrome.py with the page tables, and data/features.json."""
    tools = root / "docs/superpowers/tools"
    tools.mkdir(parents=True)
    chrome = 'ALL_PAGES = {"inicio": ("home.html", "Início"), "livro": ("livro-caixa.html", "Livro-caixa do apoio")}\n'
    (tools / "site_chrome.py").write_text(chrome + ('SWITCHED_PAGES = {"livro": "livro-caixa"}\n' if with_switches else ""), encoding="utf-8")
    (root / "data").mkdir()
    (root / "data/features.json").write_text(json.dumps({"features": [{"key": "livro-caixa", "production": switch_in_production}]}),
                                             encoding="utf-8")
    return root


class PagesOfTest(unittest.TestCase):
    def test_a_page_whose_switch_is_off_in_production_is_not_captured(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(vt.pages_of(fake_tree(Path(tmp) / "off", False)), {"inicio": "index.html"})
            # controls: the switch on, and a tree from before the switches, capture the page
            self.assertEqual(vt.pages_of(fake_tree(Path(tmp) / "on", True)), {"inicio": "index.html", "livro": "livro-caixa.html"})
            self.assertIn("livro", vt.pages_of(fake_tree(Path(tmp) / "old", False, with_switches=False)))

    def test_this_tree_leaves_the_ledger_page_out_of_production(self):
        self.assertNotIn("livro", vt.pages_of(Path(__file__).resolve().parents[2]))



if __name__ == "__main__":
    unittest.main()
