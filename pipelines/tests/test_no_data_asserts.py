"""Checks that guard data stay on under `python -O` (cleanup plan, task 7, P2-20): no `assert` statement in the pipelines and
the page builders, only `if not (...): raise SystemExit(...)`. Tests keep `assert`."""
import ast
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def asserts(paths):
    out = []
    for p in paths:
        tree = ast.parse(Path(p).read_text(encoding="utf-8"))
        out += [f"{Path(p).name}:{n.lineno}" for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    return out


def code_files():
    files = subprocess.run(["git", "-C", str(REPO), "ls-files", "pipelines/*.py", "docs/superpowers/tools/*.py"],
                           capture_output=True, text=True, check=True).stdout.split()
    return [REPO / f for f in files if "/tests/" not in f]


class NoDataAssertsTest(unittest.TestCase):
    def test_no_assert_guards_data(self):
        self.assertEqual(asserts(code_files()), [])
        with tempfile.TemporaryDirectory() as d:  # control: a planted assert is found
            p = Path(d) / "planted.py"
            p.write_text("x = 1\nassert x == 1, 'planted'\n")
            self.assertEqual(asserts([p]), ["planted.py:2"])


if __name__ == "__main__":
    unittest.main()
