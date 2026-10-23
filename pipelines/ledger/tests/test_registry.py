import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db  # noqa: E402
import registry  # noqa: E402


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.src = self.dir / "a.bin"
        self.src.write_bytes(b"x" * 3000)
        self.url = self.src.as_uri()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_hashes_while_streaming_and_deletes_the_file_after(self):
        with registry.fetch(self.url) as fx:
            kept = fx.path
            self.assertTrue(kept.exists())
            self.assertEqual(fx.sha256, hashlib.sha256(b"x" * 3000).hexdigest())
            self.assertEqual(fx.bytes, 3000)
        self.assertFalse(kept.parent.exists())

    def test_a_file_above_the_limit_stops(self):
        with self.assertRaises(registry.TooBig):
            with registry.fetch(self.url, max_bytes=1000):
                pass

    def test_low_disk_stops_before_downloading(self):
        with self.assertRaises(registry.LowDisk):
            with registry.fetch(self.url, min_free=1 << 62):
                pass

    def test_same_file_twice_is_one_release_and_a_new_file_supersedes_it(self):
        con = db.connect(":memory:")
        kw = dict(title="t", publisher="p", loader="test")
        with registry.fetch(self.url) as fx:
            a, new_a = registry.register(con, "t.ds", fx, **kw)
        with registry.fetch(self.url) as fx:
            b, new_b = registry.register(con, "t.ds", fx, **kw)
        self.assertEqual((a, new_a, new_b), (b, True, False))
        self.src.write_bytes(b"y" * 10)
        with registry.fetch(self.url) as fx:
            c, new_c = registry.register(con, "t.ds", fx, **kw)
        self.assertTrue(new_c)
        self.assertEqual(registry.current(con, "t.ds"), [c])

    def test_a_source_that_goes_back_to_an_older_file_makes_that_release_current_again(self):
        # the publisher replaces file A with B, then puts A back: A is the current release again (A, B, A)
        con = db.connect(":memory:")
        kw = dict(title="t", publisher="p", loader="test")
        with registry.fetch(self.url) as fx:
            a, _ = registry.register(con, "t.ds", fx, **kw)
        self.src.write_bytes(b"y" * 10)
        with registry.fetch(self.url) as fx:
            b, _ = registry.register(con, "t.ds", fx, **kw)
        self.assertEqual(registry.current(con, "t.ds"), [b])
        self.src.write_bytes(b"x" * 3000)
        with registry.fetch(self.url) as fx:
            again, is_new = registry.register(con, "t.ds", fx, **kw)
        self.assertEqual((again, is_new), (a, False))  # no new release: the old one, already loaded, comes back
        self.assertEqual(registry.current(con, "t.ds"), [a])
        self.assertEqual(con.execute("SELECT new_source_id FROM release_supersede WHERE old_source_id = ?", [b]).fetchone()[0], a)


if __name__ == "__main__":
    unittest.main()
