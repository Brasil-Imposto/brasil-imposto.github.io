"""The manifest of each publication (spec seguranca-doacoes, section 6; Safe publishes a SHA-256 checksum with each release): every
published file with its sha256, the commit and the time, and the hash of the whole set; verify() lists what differs (attack B1)."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "docs" / "superpowers" / "tools"
_spec = importlib.util.spec_from_file_location("build_manifest", TOOLS / "build-manifest.py")
manifest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(manifest)


class ManifestTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.site = Path(self.tmp.name)
        (self.site / "assets").mkdir()
        (self.site / "index.html").write_text("<p>Brasil-Imposto</p>", encoding="utf-8")
        (self.site / "assets" / "bi-cripto.js").write_text("// the send", encoding="utf-8")
        self.set_hash = manifest.write(self.site, "a" * 40)

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_fresh_build_matches_its_manifest(self):
        m = json.loads((self.site / manifest.NAME).read_text(encoding="utf-8"))
        self.assertEqual(sorted(m["files"]), ["assets/bi-cripto.js", "index.html"], "every file but the manifest itself")
        self.assertEqual(m["commit"], "a" * 40)
        self.assertEqual(manifest.verify(self.site), [])
        self.assertRegex(self.set_hash, r"^[0-9a-f]{64}$")

    def test_b1_a_changed_byte_is_listed(self):
        (self.site / "assets" / "bi-cripto.js").write_text("// the sena", encoding="utf-8")
        self.assertEqual(manifest.verify(self.site), ["assets/bi-cripto.js"])

    def test_a_file_added_or_removed_is_listed(self):
        (self.site / "extra.js").write_text("x", encoding="utf-8")
        (self.site / "index.html").unlink()
        self.assertEqual(manifest.verify(self.site), ["extra.js", "index.html"])

    def test_control_the_set_hash_follows_the_files(self):
        before = self.set_hash
        (self.site / "index.html").write_text("<p>outro</p>", encoding="utf-8")
        self.assertNotEqual(manifest.write(self.site, "a" * 40), before)


if __name__ == "__main__":
    unittest.main()
