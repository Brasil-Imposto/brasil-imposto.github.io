"""Runs the tests of the crypto send's pure core (bi-cripto-core.js) in node, as pipelines/tests/test_df_balance.py does for a page's own
code, and proves they can fail: a copy of the core with the decimals rule broken must not pass."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parents[1] / "docs" / "superpowers" / "previews" / "assets" / "bi-cripto-core.js"


def run(core=None):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is needed to run the crypto core's tests (the ci runner has it)")
    env = dict(os.environ, **({"BI_CORE": str(core)} if core else {}))
    return subprocess.run([node, "--test", str(HERE / "cripto_core.test.cjs")], env=env, capture_output=True, text=True).returncode


class CryptoCoreTest(unittest.TestCase):
    def test_the_core_passes(self):
        self.assertEqual(run(), 0)

    def test_control_a_broken_decimals_rule_fails(self):
        text = CORE.read_text(encoding="utf-8")
        broken = text.replace("frac.length > decimals", "frac.length > decimals + 9")
        self.assertNotEqual(broken, text, "the plant landed")
        with tempfile.TemporaryDirectory() as d:
            copy = Path(d) / "bi-cripto-core.js"
            copy.write_text(broken, encoding="utf-8")
            self.assertNotEqual(run(copy), 0)


if __name__ == "__main__":
    unittest.main()
