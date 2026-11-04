"""guard (spec seguranca-doacoes, section 5; the form of glsec's "Sensitive paths" check): reads file names on stdin, one per line,
and prints the ones that match .github/guard-paths.txt, sorted. The workflow runs this file from the base branch
(pull_request_target), never from the pull request.
"""
import fnmatch
import sys
from pathlib import Path

PATHS = Path(__file__).resolve().parents[1] / "guard-paths.txt"


def patterns(text=None):
    text = PATHS.read_text(encoding="utf-8") if text is None else text
    return [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def sensitive(names, pats=None):
    pats = patterns() if pats is None else pats
    return sorted({n for n in names if any(fnmatch.fnmatchcase(n, p) for p in pats)})


if __name__ == "__main__":
    print("\n".join(sensitive(line.strip() for line in sys.stdin if line.strip())))
