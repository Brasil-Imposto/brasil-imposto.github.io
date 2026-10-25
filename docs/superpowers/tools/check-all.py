"""Prepare and check everything the ci checks, in the same order, with the time of each step (trust spec, item F1).

Usage: uv run --locked python docs/superpowers/tools/check-all.py
Needs Python 3.12 with uv and Node 24 (.nvmrc); git for the check of the committed pages. Stops at the first step that fails and
exits 1, so a red step here is the step that would be red in the ci. Last, it builds the site in both profiles (production and
staging, #52) into a temporary folder and removes it.
"""
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PY = ["uv", "run", "--locked", "python"]
TOOLS = "docs/superpowers/tools"
BUILDERS = ["build-cases.py", "build-standalone-data.py", "build-simulation.py", "build-platform-preview.py",
            "build-site-chrome.py", "build-notes-page.py"]


def steps(tmp):
    yield "uv: the lock file matches pyproject.toml", ["uv", "lock", "--check"], ROOT
    yield "uv: the locked Python environment", ["uv", "sync", "--locked"], ROOT
    yield "tests of pipelines/", PY + ["-m", "unittest", "discover", "-s", "pipelines/tests"], ROOT
    yield "entity files, each checked against its schema", PY + ["pipelines/export/build_entities.py"], ROOT
    yield "site: npm ci", ["npm", "ci", "--no-audit", "--no-fund"], ROOT / "site"
    for s in ("types", "check", "test", "build"):
        yield f"site: npm run {s}", ["npm", "run", s], ROOT / "site"
    yield "tests of the ledger", PY + ["-m", "unittest", "discover", "-s", "pipelines/ledger/tests"], ROOT
    for b in BUILDERS:
        yield f"builder {b}", PY + [f"{TOOLS}/{b}"], ROOT
    yield "the committed pages are what their builders make", ["git", "diff", "--exit-code", "--stat", "--",
                                                               "docs/superpowers/previews/"], ROOT
    yield "map loader", PY + ["-m", "unittest", "pipelines/tests/test_map_loader.py"], ROOT
    for profile in ("production", "staging"):
        yield f"site, {profile} profile", PY + [f"{TOOLS}/build-site.py", "--profile", profile, "--out", str(tmp / profile)], ROOT


def main():
    for tool in ("uv", "node", "npm", "git"):
        if not shutil.which(tool):
            sys.exit(f"{tool} is not installed: see CONTRIBUTING.md, section Para desenvolver")
    node = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
    want = (ROOT / ".nvmrc").read_text().strip()
    if not node.lstrip("v").startswith(want + "."):
        print(f"note: Node {node}; the ci uses Node {want} (.nvmrc)")
    tmp = Path(tempfile.mkdtemp(prefix="bi-check-"))
    t0 = time.monotonic()
    try:
        for n, (name, cmd, cwd) in enumerate(steps(tmp), 1):
            t = time.monotonic()
            r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            took = time.monotonic() - t
            if r.returncode:
                print(r.stdout[-4000:])
                print(f"FAIL {n:2d}. {name} ({took:.0f} s): {' '.join(cmd)}")
                return 1
            print(f"ok   {n:2d}. {name} ({took:.0f} s)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"all steps passed in {time.monotonic() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
