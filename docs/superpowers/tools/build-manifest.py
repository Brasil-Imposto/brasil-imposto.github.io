"""The manifest of one publication (spec seguranca-doacoes, section 6; Safe publishes a SHA-256 checksum file with each release): the
commit, the time and the sha256 of every published file, written into the site as build-manifest.json, and the hash of the whole set
on the last line. The served-files check of the monitor compares what is served with it (section 7, attack B1).

Run: python3 docs/superpowers/tools/build-manifest.py write <site> <commit>
     python3 docs/superpowers/tools/build-manifest.py verify <site>      (lists every file that differs; exit 1 if any)
"""
import datetime
import hashlib
import json
import sys
from pathlib import Path

NAME = "build-manifest.json"


def files(site):
    site = Path(site)
    return {p.relative_to(site).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(site.rglob("*")) if p.is_file() and p.relative_to(site).as_posix() != NAME}


def set_hash(listing):
    return hashlib.sha256(json.dumps(listing, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def write(site, commit):
    listing = files(site)
    built_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    Path(site, NAME).write_text(json.dumps({"commit": commit, "built_at": built_at, "files": listing}, indent=1, sort_keys=True) + "\n",
                                encoding="utf-8")
    return set_hash(listing)


def verify(site, manifest=None):
    want = (manifest or json.loads(Path(site, NAME).read_text(encoding="utf-8")))["files"]
    now = files(site)
    return sorted(set(want) ^ set(now) | {k for k in now if k in want and now[k] != want[k]})


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "write":
        print(f"{len(files(sys.argv[2]))} files; the set's sha256: {write(sys.argv[2], sys.argv[3])}")
    elif len(sys.argv) == 3 and sys.argv[1] == "verify":
        diff = verify(sys.argv[2])
        print("\n".join(diff) or "every file matches the manifest")
        sys.exit(1 if diff else 0)
    else:
        raise SystemExit(__doc__)
