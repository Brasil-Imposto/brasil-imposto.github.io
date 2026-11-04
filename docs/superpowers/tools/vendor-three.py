"""three.js 0.170.0 served by the site itself (spec seguranca-doacoes, section 8; D219): the seven modules Início imports, taken
from the npm package and checked against the hashes the import map pinned, before their one change: an add-on's import of
'three' becomes the relative path of the copy beside it, so the page needs no import map (an inline import map is inline code,
which the CSP refuses). pipelines/tests/test_vendor_three.py undoes that change and checks the hashes again.

Run once per three.js version: python3 docs/superpowers/tools/vendor-three.py
"""
import base64
import hashlib
import io
import json
import tarfile
import urllib.request
from pathlib import Path

VERSION = "0.170.0"
OUT = Path(__file__).resolve().parents[1] / "previews" / "assets" / "vendor" / "three"
CORE = "../../../build/three.module.js"
PINNED = {   # sha384, the values of Início's import map until 2026-11-03
    "build/three.module.js": "GY5FqjttLCFRt/McQbyaVdCk2O1IQtOeX8Py6NfD89BIAsIyJFRl4UgSXrk2vXAk",
    "examples/jsm/lines/Line2.js": "svIqR2W/RlXb3d4T+bDn3JO+LXLbacA7GpMAUDJxTOFyZmVogvDRaOS7KZBRxcxc",
    "examples/jsm/lines/LineGeometry.js": "nfFqbe33KO97I7jZXjW73quBqqskqqj64WZycLNDzn0GGGI3aoWLZzuy8i0jeYmU",
    "examples/jsm/lines/LineMaterial.js": "bLpiIpNrFJ+EMb4Upzkap/Bc9Ul2wLoUMEfFm0PmZfyywMUYUsc5X98AuAYwwjq1",
    "examples/jsm/lines/LineSegments2.js": "nm+9Od/cYIb15jGaA1U2Geoo18K/i9fF2fZ4KbI2rZydtfYxqwtWRlbvdVfiECU5",
    "examples/jsm/lines/LineSegmentsGeometry.js": "2bbjHgEUXo9c3VW3OaZV638VYLXKhlNhNStU2D1Jm77zamWSQVYZak2p/Z0bZrmh",
    "examples/jsm/renderers/CSS2DRenderer.js": "9CXQqRjuKfYvfHem9p/LPU6b7PaeeiDuC/gp1qRz3bEV9txWG5wi9XhrkE/0/Dn9",
}


def fetch(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def b64(digest):
    return base64.b64encode(digest).decode()


def main():
    meta = json.loads(fetch(f"https://registry.npmjs.org/three/{VERSION}"))
    tgz = fetch(meta["dist"]["tarball"])
    algo, want = meta["dist"]["integrity"].split("-", 1)
    if not (algo == "sha512" and b64(hashlib.sha512(tgz).digest()) == want):
        raise SystemExit("vendor-three: the package does not match the registry's integrity")
    with tarfile.open(fileobj=io.BytesIO(tgz)) as tar:
        for rel, pin in PINNED.items():
            raw = tar.extractfile(f"package/{rel}").read()
            got = b64(hashlib.sha384(raw).digest())
            if got != pin:
                raise SystemExit(f"vendor-three: {rel} has sha384 {got}, not the pinned {pin}")
            text = raw.decode("utf-8")
            text = text.replace("from 'three'", f"from '{CORE}'")   # Line2.js and the core import no 'three'
            dest = OUT / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
        (OUT / "LICENSE").write_bytes(tar.extractfile("package/LICENSE").read())
    print(f"three.js {VERSION}: {len(PINNED)} modules and LICENSE in {OUT}")


if __name__ == "__main__":
    main()
