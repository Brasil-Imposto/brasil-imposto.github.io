"""The Python environment is the one pyproject.toml and uv.lock describe: Python 3.12 and every dependency at its pinned
version. Run through uv (`uv run --locked python -m unittest discover -s pipelines/tests`), it proves the lock is in use."""
import importlib.metadata
import re
import sys
import tomllib
import unittest
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


class EnvironmentTest(unittest.TestCase):
    def test_python_is_3_12(self):
        self.assertEqual(sys.version_info[:2], (3, 12))

    def test_every_dependency_at_its_pinned_version(self):
        pins = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["dependencies"]
        self.assertGreaterEqual(len(pins), 4)
        for pin in pins:
            name, version = re.fullmatch(r"([A-Za-z0-9_.-]+)==([0-9][^\s;]*)", pin).groups()
            with self.subTest(name=name):
                self.assertEqual(importlib.metadata.version(name), version)


if __name__ == "__main__":
    unittest.main()
