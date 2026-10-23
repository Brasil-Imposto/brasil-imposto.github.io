"""Finds e-mail addresses in built pages or in a diff (spec apoie, section 8: no address in the page, the repository, a commit or a
pull request). Prints each one found with its file and exits 1 when any is found.

Usage: python3 docs/superpowers/tools/email-scan.py <file or folder> [...] [--plant]
       git diff main | python3 docs/superpowers/tools/email-scan.py -
--plant adds one address to the text it reads (built here from its parts, so no address is written in this file); the scan
must then find it, or it is blind.
"""
import re
import sys
from pathlib import Path

PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
PLANTED = "planted.address" + chr(64) + "example" + ".org"
TEXT = {".html", ".js", ".cjs", ".css", ".json", ".py", ".md", ".txt", ".yml", ".svg", ".diff", ".patch"}


def find(text):
    return PATTERN.findall(text)


def texts(args):
    for a in args:
        if a == "-":
            yield "stdin", sys.stdin.read()
            continue
        p = Path(a)
        files = sorted(x for x in p.rglob("*") if x.is_file() and x.suffix in TEXT) if p.is_dir() else [p]
        for f in files:
            yield str(f), f.read_text(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--plant"]
    if not args:
        sys.exit(__doc__)
    hits = []
    for name, text in texts(args):
        if "--plant" in sys.argv:
            text += "\n" + PLANTED
        hits += [(name, h) for h in find(text)]
    for name, h in hits:
        print(f"{name}: {h}")
    print(f"{len(hits)} e-mail addresses found")
    sys.exit(1 if hits else 0)
