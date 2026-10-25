"""Every path and script CONTRIBUTING.md cites exists (Phase 2 spec, P1): if a script is renamed, the guide must change with it.
A path with folders must exist as written; a script cited by its name alone must exist in docs/superpowers/tools/.
Control: a renamed path and a renamed script must be reported."""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXT = r"(?:json|lock|cjs|mjs|yml|py|js|md)"
PATH = re.compile(r"(?<![\w/.-])((?:docs|pipelines|site|data|schemas|\.github)/[\w./-]+\." + EXT + r")(?![\w])")
SCRIPT = re.compile(r"`([\w-]+\.(?:py|cjs))`")
TOOLS = REPO / "docs" / "superpowers" / "tools"


def cited(text):
    return set(PATH.findall(text)), set(SCRIPT.findall(text))


def missing(text):
    paths, scripts = cited(text)
    return sorted({p for p in paths if not (REPO / p).exists()} | {s for s in scripts if not (TOOLS / s).exists()})


class ContributingPathsTest(unittest.TestCase):
    def test_every_cited_path_and_script_exists(self):
        text = (REPO / "CONTRIBUTING.md").read_text(encoding="utf-8")
        paths, scripts = cited(text)
        self.assertGreaterEqual(len(paths) + len(scripts), 10)
        self.assertEqual(missing(text), [])

    def test_control_a_renamed_path_or_script_is_reported(self):
        self.assertEqual(missing("rode docs/superpowers/tools/check-all-renamed.py e `build-casos.py`"),
                         ["build-casos.py", "docs/superpowers/tools/check-all-renamed.py"])


if __name__ == "__main__":
    unittest.main()
