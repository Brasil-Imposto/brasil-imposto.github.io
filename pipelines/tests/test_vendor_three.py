"""three.js 0.170.0 served by the site itself (spec seguranca-doacoes, section 8): each file is the npm file byte for byte except
its import of 'three', which points to the copy beside it. Undoing that one change gives the hash the import map pinned."""
import base64
import hashlib
import unittest
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[2] / "docs" / "superpowers" / "previews" / "assets" / "vendor" / "three"
CORE = "../../../build/three.module.js"
PINNED = {   # sha384 from the import map of 2026-11-03 (build-platform-preview.py, THREE_INTEGRITY)
    "build/three.module.js": "GY5FqjttLCFRt/McQbyaVdCk2O1IQtOeX8Py6NfD89BIAsIyJFRl4UgSXrk2vXAk",
    "examples/jsm/lines/Line2.js": "svIqR2W/RlXb3d4T+bDn3JO+LXLbacA7GpMAUDJxTOFyZmVogvDRaOS7KZBRxcxc",
    "examples/jsm/lines/LineGeometry.js": "nfFqbe33KO97I7jZXjW73quBqqskqqj64WZycLNDzn0GGGI3aoWLZzuy8i0jeYmU",
    "examples/jsm/lines/LineMaterial.js": "bLpiIpNrFJ+EMb4Upzkap/Bc9Ul2wLoUMEfFm0PmZfyywMUYUsc5X98AuAYwwjq1",
    "examples/jsm/lines/LineSegments2.js": "nm+9Od/cYIb15jGaA1U2Geoo18K/i9fF2fZ4KbI2rZydtfYxqwtWRlbvdVfiECU5",
    "examples/jsm/lines/LineSegmentsGeometry.js": "2bbjHgEUXo9c3VW3OaZV638VYLXKhlNhNStU2D1Jm77zamWSQVYZak2p/Z0bZrmh",
    "examples/jsm/renderers/CSS2DRenderer.js": "9CXQqRjuKfYvfHem9p/LPU6b7PaeeiDuC/gp1qRz3bEV9txWG5wi9XhrkE/0/Dn9",
}


def upstream_hash(text):
    return base64.b64encode(hashlib.sha384(text.replace(f"from '{CORE}'", "from 'three'").encode("utf-8")).digest()).decode()


class VendorThreeTest(unittest.TestCase):
    def test_each_file_is_the_pinned_upstream_file(self):
        for rel, want in PINNED.items():
            with self.subTest(file=rel):
                self.assertEqual(upstream_hash((VENDOR / rel).read_text(encoding="utf-8")), want)

    def test_nothing_imports_a_bare_three(self):
        for f in VENDOR.rglob("*.js"):
            self.assertNotIn("from 'three'", f.read_text(encoding="utf-8"), f.name)

    def test_a_changed_byte_is_seen(self):   # the control
        t = (VENDOR / "examples/jsm/lines/Line2.js").read_text(encoding="utf-8")
        self.assertNotEqual(upstream_hash(t.replace("Line2", "Line3", 1)), PINNED["examples/jsm/lines/Line2.js"])
