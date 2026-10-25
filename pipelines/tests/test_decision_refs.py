"""Every decision number cited in the specs, the data, the pipelines, the page code and the site exists in the public record
docs/decisions/README.md (trust spec, G1), so a reader who follows "D146" from a page or a file always finds it.
D999 is the project's planted control code (the trust spec and visible-text-probe.cjs use it on purpose) and is left out, and
this file, which names the code its control plants, is not read.
Control: a D998 planted in a copy of a spec must be reported."""
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCOPE = ["docs/superpowers/specs", "data", "pipelines", "docs/superpowers/tools", "docs/superpowers/previews/assets", "site/src"]
SUFFIXES = (".md", ".py", ".js", ".cjs", ".mjs", ".json", ".ts", ".astro")
CITE = re.compile(r"(?<![\w-])(D\d{1,3})(?![\w-])")
PLANTED = {"D999"}


def recorded():
    return set(re.findall(r"(?m)^\| *(D\d+) \|", (REPO / "docs" / "decisions" / "README.md").read_text(encoding="utf-8")))


def missing(texts, known):
    out = {}
    for name, text in texts:
        for d in set(CITE.findall(text)) - known - PLANTED:
            out.setdefault(d, []).append(name)
    return out


class DecisionRefsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        files = subprocess.run(["git", "ls-files", *SCOPE], cwd=REPO, capture_output=True, text=True, check=True).stdout.split()
        cls.texts = [(f, (REPO / f).read_text(encoding="utf-8")) for f in files
                     if f.endswith(SUFFIXES) and f != "pipelines/tests/test_decision_refs.py"]
        cls.known = recorded()

    def test_every_cited_decision_is_in_the_public_record(self):
        self.assertGreater(len(self.known), 160)
        self.assertGreater(len(self.texts), 100)
        self.assertEqual(missing(self.texts, self.known), {})

    def test_control_a_planted_decision_is_reported(self):
        spec = next((n, t) for n, t in self.texts if n.startswith("docs/superpowers/specs/"))
        self.assertEqual(missing([(spec[0], spec[1] + " (D998)")], self.known), {"D998": [spec[0]]})


if __name__ == "__main__":
    unittest.main()
