"""The workflows run pinned code with the least permission (trust spec, D1).

Every `uses:` of .github/workflows/ and deploy/staging/deploy.yml names an action by a 40-character commit with its version in a
comment, so a moved tag cannot change what runs. No workflow grants a write permission at its top: a write appears only in the
job that needs it, and the only ones allowed are Pages' (pages and id-token), in a job named deploy, the Scorecard's
(security-events and id-token), in a job named scorecard, CodeQL's (security-events), in a job named analyze, and the guard's
(pull-requests), in a job named guard.
Every workflow that deploys to Pages builds its artifact itself (D228): a tar of _site that keeps the names starting with a dot
(the site needs .well-known/security.txt and .nojekyll), uploaded as github-pages, and no upload-pages-artifact (v3.0.1 calls
upload-artifact@v4 by tag, which the SHA rule refuses; v4 and later leave the dot files out by default; v5.0.0 stalled the deploy).
Controls: a copy with an action at @v4, a copy with pages: write at the top, a copy with a write the job is not allowed, a copy whose
tar leaves the dot files out, a copy whose artifact has another name, and a copy back on upload-pages-artifact, must fail.
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FILES = sorted((REPO / ".github" / "workflows").glob("*.yml")) + [REPO / "deploy" / "staging" / "deploy.yml"]
USES = re.compile(r"^\s*(?:-\s+)?uses:\s*(\S+)(.*)$")
PINNED = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
JOB_WRITES = {"deploy": {"pages", "id-token"}, "scorecard": {"security-events", "id-token"}, "analyze": {"security-events"},
              "guard": {"pull-requests"}}   # guard takes its label off after a new push (spec seguranca-doacoes, section 5)


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
        elif m and block == "job" and m.group(1) not in JOB_WRITES.get(job, set()):
            out.append(f"{name}:{n}: {m.group(1)}: write in job {job}")
    return out


def pages_artifact_problems(name, text):
    """A workflow with deploy-pages must archive _site with its dot files and upload the tar as github-pages."""
    out = []
    if "actions/upload-pages-artifact@" in text:
        out.append(f"{name}: uses upload-pages-artifact")
    tar = re.search(r"tar \\\n((?:\s+.*\\\n)+\s+\.\n)", text)
    if not tar or "--directory _site" not in tar.group(1):
        out.append(f"{name}: no tar of _site")
    elif re.search(r"--exclude=['\"]?\.\[", tar.group(1)):
        out.append(f"{name}: the tar leaves out the names that start with a dot")
    m = re.search(r"uses: actions/upload-artifact@[0-9a-f]{40} # v[\d.]+\n((?:[ ]{8,}\S.*\n)+)", text)   # the step's own lines only
    step = m.group(1) if m else ""
    if "name: github-pages" not in step or "path: ${{ runner.temp }}/artifact.tar" not in step:
        out.append(f"{name}: no upload of the tar as github-pages")
    return out


class WorkflowsTest(unittest.TestCase):
    def test_every_action_is_pinned_and_every_write_is_scoped(self):
        self.assertGreaterEqual(len(FILES), 5)
        found = [p for f in FILES for p in problems(f.name, f.read_text(encoding="utf-8"))]
        self.assertEqual(found, [])

    def test_every_pages_deploy_builds_its_artifact_with_the_dot_files(self):
        deploys = [f for f in FILES if "actions/deploy-pages@" in f.read_text(encoding="utf-8")]
        self.assertEqual(sorted(f.name for f in deploys), ["deploy.yml", "pages.yml"])
        found = [p for f in deploys for p in pages_artifact_problems(f.name, f.read_text(encoding="utf-8"))]
        self.assertEqual(found, [])

    def test_control_a_pages_artifact_that_breaks_fails(self):
        plants = [("            --exclude=.github \\\n", "            --exclude=.github \\\n            --exclude=.[^/]* \\\n", "dot"),
                  ("          name: github-pages\n", "          name: site\n", "github-pages"),
                  ("      - name: Archive the site for Pages\n", "      - uses: actions/upload-pages-artifact@fc324d3547104276b827a68afc52ff2a11cc49c9 # v5.0.0\n      - name: Archive the site for Pages\n", "upload-pages-artifact")]
        for f in (REPO / ".github" / "workflows" / "pages.yml", REPO / "deploy" / "staging" / "deploy.yml"):
            text = f.read_text(encoding="utf-8")
            for old, new, word in plants:
                bad = text.replace(old, new, 1)
                self.assertNotEqual(bad, text, (f.name, word))
                found = pages_artifact_problems(f.name, bad)
                self.assertEqual(len(found), 1, (f.name, word, found))
                self.assertIn(word, found[0])

    def test_control_an_action_by_tag_fails(self):
        text = (REPO / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        bad = re.sub(r"actions/checkout@[0-9a-f]{40} # v[\d.]+", "actions/checkout@v4", text)
        self.assertNotEqual(bad, text)
        self.assertTrue(any("actions/checkout@v4" in p for p in problems("pages.yml", bad)))

    def test_control_a_write_the_job_is_not_allowed_fails(self):
        text = (REPO / ".github" / "workflows" / "scorecard.yml").read_text(encoding="utf-8")
        bad = text.replace("      security-events: write\n", "      security-events: write\n      contents: write\n", 1)
        self.assertNotEqual(bad, text)
        self.assertTrue(any("contents: write in job scorecard" in p for p in problems("scorecard.yml", bad)))

    def test_control_pages_write_at_the_top_fails(self):
        text = (REPO / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        bad = text.replace("permissions:\n  contents: read\n", "permissions:\n  contents: read\n  pages: write\n", 1)
        self.assertNotEqual(bad, text)
        self.assertTrue(any("pages: write at the top" in p for p in problems("pages.yml", bad)))


if __name__ == "__main__":
    unittest.main()
