"""The sheets of Os 3 Poderes (D235): in the label and value lists (.others) the label takes the free width and wraps, and the value
never shrinks and takes at most 60% of the row (before, the label could not wrap and ran out of its box, and the value was squeezed
until its letters stacked); and the sources line lists the sources of the spending a sheet shows, so no sheet outside the
parliamentarians (who have their own line) ends in "Fontes: .". Controls: the old rules and the old sources line are each caught.
The layout itself is measured in the browser by docs/superpowers/tools/overflow-check.cjs."""
import json
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAGE = REPO / "docs" / "superpowers" / "previews" / "os-3-poderes.html"
JS = REPO / "docs" / "superpowers" / "previews" / "assets" / "tres-poderes-page.js"
DATA = REPO / "docs" / "superpowers" / "previews" / "assets" / "tres-poderes-r3-data.js"
OLD_RULES = ".others li span { flex:none; } .others li b { text-align:right; min-width:0; overflow-wrap:anywhere; }"
OLD_SRCS = "const srcs = [...new Set(x.items.map((it) => it.source).filter(Boolean))];"


def rule(css, selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return re.sub(r"\s+", "", m.group(1)) if m else None


def list_problems(html):
    """What is wrong with the .others rules in the page (an empty list is the approved layout)."""
    span, b = rule(html, ".others li span"), rule(html, ".others li b")
    out = []
    if span is None or "flex:none" in span or "min-width:0" not in span or "overflow-wrap:anywhere" not in span:
        out.append("the label cannot take the free width and wrap")
    if b is None or "flex:00auto" not in b or "max-width:60%" not in b:
        out.append("the value can shrink, or has no 60% cap")
    return out


def sources(srcs_line):
    """Each sheet outside the parliamentarians and the sources its line lists, by running the page's own srcs line on the data."""
    script = ("global.window = {}; require(process.argv[1]);"
              "const out = {}; for (const x of window.TP3.people) { if (x.house === 'camara' || x.house === 'senado') continue;"
              f" {srcs_line} out[x.id] = srcs; }} console.log(JSON.stringify(out));")
    run = subprocess.run(["node", "-e", script, str(DATA)], capture_output=True, text=True, check=True)
    return json.loads(run.stdout)


def current_sources():
    """The sources each sheet lists with the page's srcs line as committed."""
    with open(JS, encoding="utf-8") as f:   # read with open(): the file starts with "//", which test_layout reads as a path
        return sources(srcs_line(f.read()))


def srcs_line(js):
    found = re.findall(r"^\s*(const srcs = .*;)\s*$", js, re.M)
    if len(found) != 1:
        raise AssertionError(f"one srcs line expected, found {len(found)}")
    return found[0]


class ListsTest(unittest.TestCase):
    def test_the_list_rules_are_the_approved_ones(self):
        self.assertEqual(list_problems(PAGE.read_text(encoding="utf-8")), [])

    def test_control_the_old_rules_are_caught(self):
        html = PAGE.read_text(encoding="utf-8")
        old = re.sub(r"\.others li span \{[^}]*\}\s*\.others li b \{[^}]*\}", OLD_RULES, html, count=1)
        self.assertNotEqual(old, html, "the plant landed")
        self.assertEqual(len(list_problems(old)), 2)


class SourcesLineTest(unittest.TestCase):
    def test_every_sheet_lists_the_sources_of_what_it_shows(self):
        got = current_sources()
        self.assertGreater(len(got), 100)
        self.assertEqual([k for k, v in got.items() if not v], [], "a sheet whose sources line would read 'Fontes: .'")
        viagens = "https://portaldatransparencia.gov.br/download-de-dados/viagens/2026"
        self.assertIn(viagens, got["exec:rosangela-lula-da-silva"])
        self.assertIn(viagens, got["exec:luiz-inacio-lula-da-silva"])
        self.assertTrue(any("/download-de-dados/cpgf/" in u for u in got["exec:luiz-inacio-lula-da-silva"]))

    def test_control_the_old_line_leaves_the_spouse_without_sources(self):
        self.assertEqual(sources(OLD_SRCS)["exec:rosangela-lula-da-silva"], [])


if __name__ == "__main__":
    unittest.main()
