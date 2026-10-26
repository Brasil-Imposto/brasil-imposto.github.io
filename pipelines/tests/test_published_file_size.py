"""Published files stay under a size limit (issue #121, part of #10): nothing under data/ or under the preview assets may grow past
LIMIT_BYTES, so the site does not get heavy without anyone noticing.

The largest published file today is data/series/rs-municipal-budgets.json, at about 37 MB; the limit leaves room to grow and sits at
the 50 MB mark where GitHub starts to warn on a push. A file that really has to be bigger raises the limit here, in the same pull
request, with the reason.
Run: uv run --locked python -m unittest discover -s pipelines/tests"""
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
# the folders whose tracked files are published (bi-data.js is generated and stays out of git, so it is not listed)
PUBLISHED = ("data", "docs/superpowers/previews/assets")
LIMIT_BYTES = 50 * 1024 * 1024


def published_files():
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z", "--", *PUBLISHED], capture_output=True, check=True).stdout
    return [REPO / rel for rel in out.decode().split("\0") if rel and (REPO / rel).is_file()]


def oversize(files, limit=LIMIT_BYTES):
    """The files that pass the limit, as (path, size), biggest first."""
    return sorted(((f, f.stat().st_size) for f in files if f.stat().st_size > limit), key=lambda item: -item[1])


class PublishedFileSizeTest(unittest.TestCase):
    def test_the_published_files_are_found(self):
        # a moved folder would make the size test below pass on an empty list
        files = published_files()
        for folder in PUBLISHED:
            self.assertTrue(any((REPO / folder) in f.parents for f in files), f"no tracked file under {folder}/")

    def test_no_published_file_passes_the_limit(self):
        big = oversize(published_files())
        self.assertEqual(big, [], "published files over %d MB: %s" % (
            LIMIT_BYTES // (1024 * 1024), ", ".join(f"{f.relative_to(REPO)} ({size / (1024 * 1024):.1f} MB)" for f, size in big)))

    def test_control_a_planted_oversize_file_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            planted = Path(tmp) / "planted.json"
            with planted.open("wb") as f:
                f.truncate(LIMIT_BYTES + 1)  # one byte over, without writing 50 MB to disk
            fine = Path(tmp) / "fine.json"
            fine.write_text("{}", encoding="utf-8")
            self.assertEqual(oversize([planted, fine]), [(planted, LIMIT_BYTES + 1)])


if __name__ == "__main__":
    unittest.main()
