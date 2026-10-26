"""The dco check (D188): every commit needs its author's sign-off, except the commits GitHub verified as the dependabot[bot]
account. The test runs the very script embedded in .github/workflows/dco.yml against sample commits, so it checks what the
workflow runs. Controls: a commit without a sign-off by a person, a dependabot[bot] commit GitHub did not verify, and a commit
by another account that only claims Dependabot's name must all fail.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = (REPO / ".github" / "workflows" / "dco.yml").read_text(encoding="utf-8")


def embedded_script():
    m = re.search(r"python3 - <<'PY'\n(.*?)\n\s*PY\n", WORKFLOW, re.S)
    assert m, "the dco workflow no longer embeds its script"
    return textwrap.dedent(m.group(1))


def commit(login, email, message, verified=False, name="Pessoa"):
    return {"sha": "a" * 40, "author": {"login": login} if login else None,
            "commit": {"author": {"name": name, "email": email}, "committer": {"email": email},
                       "message": message, "verification": {"verified": verified}}}


SIGNED = commit("pessoa", "pessoa@example.org", "fix: x\n\nSigned-off-by: Pessoa <pessoa@example.org>\n")
UNSIGNED = commit("pessoa", "pessoa@example.org", "fix: x\n")
BOT = commit("dependabot[bot]", "49699333+dependabot[bot]@users.noreply.github.com", "build(deps): bump x\n", verified=True,
             name="dependabot[bot]")


def run(commits):
    with tempfile.TemporaryDirectory() as d:
        Path(d, "commits.json").write_text(json.dumps([commits]), encoding="utf-8")
        env = dict(os.environ, REPO="Brasil-Imposto/brasil-imposto.github.io", HEAD_REF="dependabot/x", BASE_REF="staging",
                   HEAD_REPO="Brasil-Imposto/brasil-imposto.github.io")
        return subprocess.run([sys.executable, "-c", embedded_script()], cwd=d, env=env, capture_output=True, text=True).returncode


class DcoTest(unittest.TestCase):
    def test_signed_commits_pass(self):
        self.assertEqual(run([SIGNED]), 0)

    def test_a_verified_dependabot_commit_passes(self):
        self.assertEqual(run([BOT, SIGNED]), 0)

    def test_control_a_commit_without_sign_off_fails(self):
        self.assertEqual(run([SIGNED, UNSIGNED]), 1)

    def test_control_an_unverified_dependabot_commit_fails(self):
        self.assertEqual(run([dict(BOT, commit=dict(BOT["commit"], verification={"verified": False}))]), 1)

    def test_control_another_account_with_dependabots_name_fails(self):
        self.assertEqual(run([dict(BOT, author={"login": "someone"})]), 1)


if __name__ == "__main__":
    unittest.main()
