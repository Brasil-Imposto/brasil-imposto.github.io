"""The workflows run pinned code with the least permission (trust spec, D1).

Every `uses:` of .github/workflows/ and deploy/staging/deploy.yml names an action by a 40-character commit with its version in a
comment, so a moved tag cannot change what runs. No workflow grants a write permission at its top: a write appears only in the
job that needs it, and the only ones allowed are Pages' (pages and id-token), in a job named deploy.
Controls: a copy with an action at @v4, and a copy with pages: write at the top, must fail.
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FILES = sorted((REPO / ".github" / "workflows").glob("*.yml")) + [REPO / "deploy" / "staging" / "deploy.yml"]
USES = re.compile(r"^\s*(?:-\s+)?uses:\s*(\S+)(.*)$")
PINNED = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
JOB_WRITES = {"pages", "id-token"}


def problems(name, text):
    out, lines = [], text.splitlines()
    for n, line in enumerate(lines, 1):
        m = USES.match(line)
        if m and not (PINNED.match(m.group(1)) and re.search(r"#\s*v\d", m.group(2))):
            out.append(f"{name}:{n}: {m.group(1)} is not pinned by commit with its version in a comment")
    job, block = None, None
    for n, line in enumerate(lines, 1):
        indent = len(line) - len(line.lstrip())
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if indent == 0:
            block = "top" if line.startswith("permissions:") else None
            if line.startswith("permissions:") and "write" in line:
                out.append(f"{name}:{n}: write permission at the top")
            continue
        if indent == 2 and re.match(r"^  [\w-]+:\s*$", line) and block != "top":
            job, block = line.strip()[:-1], None
            continue
        if indent == 4 and line.strip().startswith("permissions:"):
            block = "job"
            continue
        if indent == 4 and block == "job":
            block = None
        m = re.match(r"^\s+([\w-]+):\s*write\b", line)
        if m and block == "top":
            out.append(f"{name}:{n}: {m.group(1)}: write at the top")
        elif m and block == "job" and not (m.group(1) in JOB_WRITES and job == "deploy"):
            out.append(f"{name}:{n}: {m.group(1)}: write in job {job}")
    return out


class WorkflowsTest(unittest.TestCase):
    def test_every_action_is_pinned_and_every_write_is_scoped(self):
        self.assertGreaterEqual(len(FILES), 5)
        found = [p for f in FILES for p in problems(f.name, f.read_text(encoding="utf-8"))]
        self.assertEqual(found, [])

    def test_control_an_action_by_tag_fails(self):
        text = (REPO / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        bad = re.sub(r"actions/checkout@[0-9a-f]{40} # v[\d.]+", "actions/checkout@v4", text)
        self.assertNotEqual(bad, text)
        self.assertTrue(any("actions/checkout@v4" in p for p in problems("pages.yml", bad)))

    def test_control_pages_write_at_the_top_fails(self):
        text = (REPO / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        bad = text.replace("permissions:\n  contents: read\n", "permissions:\n  contents: read\n  pages: write\n", 1)
        self.assertNotEqual(bad, text)
        self.assertTrue(any("pages: write at the top" in p for p in problems("pages.yml", bad)))


if __name__ == "__main__":
    unittest.main()
