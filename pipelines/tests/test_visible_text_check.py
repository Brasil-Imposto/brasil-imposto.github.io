"""The ci's visible-text check (spec paridade-enderecos-formatador, part A; D194): which pull requests skip the comparison, and
how a difference is reported. Controls: a change under data/ or in a builder must not skip; one changed word must be reported
with its line on both sides. The comparison itself runs in the visible-text workflow, where a planted word fails it.
"""
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
