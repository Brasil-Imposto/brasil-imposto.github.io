"""pipelines/build.py (the 2024 balance by state) stops when an input is missing, naming the file and the script that writes it,
and never touches data/uf-balance-2024.json then (cleanup plan, task 7, P1-12). Before this, a missing transfers or direct
spending file wrote the published file with those blocks as null."""
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILD = REPO / "pipelines" / "build.py"
OUT = REPO / "data" / "uf-balance-2024.json"
INPUTS = ["arrecadacao-estado.csv", "ibge_pop.json", "transf_agg_2024.json", "tt/lc176est.csv", "tt/lc176mun.csv",
          "direct_2024.json", "sources.json"]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


class RootBuildTest(unittest.TestCase):
    def run_without(self, missing):
        with tempfile.TemporaryDirectory() as d:
            for name in INPUTS:
                if name != missing:
                    (Path(d) / name).parent.mkdir(parents=True, exist_ok=True)
                    (Path(d) / name).write_text("")
            before = sha(OUT)
            r = subprocess.run([sys.executable, "-B", str(BUILD)], cwd=d, capture_output=True, text=True)
            self.assertEqual(sha(OUT), before, "the published file changed")
            return r

    def test_a_missing_input_stops_the_build_and_names_it(self):
        for missing, writer in (("transf_agg_2024.json", "agg_transfers.py"), ("direct_2024.json", "build_direct.py")):
            with self.subTest(missing=missing):
                r = self.run_without(missing)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(missing, r.stderr)
                self.assertIn(writer, r.stderr)


if __name__ == "__main__":
    unittest.main()
