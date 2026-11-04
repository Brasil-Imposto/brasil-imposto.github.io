"""guard (spec seguranca-doacoes, section 5, attack R1): the paths that need the label seguranca-revisada, the owners of those paths,
and a workflow that never checks out or runs code from the pull request. Attack R3 (a new push after the label) is the workflow's
own step, proven on GitHub with a test pull request."""
import importlib.util
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("guard", REPO / ".github" / "scripts" / "guard.py")
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)


def workflow():
    return (REPO / ".github" / "workflows" / "guard.yml").read_text(encoding="utf-8")


class GuardPathsTest(unittest.TestCase):
    def test_r1_an_address_and_its_pinned_test_changed_together_need_the_label(self):
        self.assertEqual(guard.sensitive(["data/support.json", "pipelines/tests/test_support.py", "README.md"]),
                         ["data/support.json", "pipelines/tests/test_support.py"])

    def test_control_an_ordinary_change_needs_nothing(self):
        self.assertEqual(guard.sensitive(["README.md", "docs/research/x.md", "data/series/federal-revenue.json", "docs/superpowers/previews/os-3-poderes.html"]), [])

    def test_every_path_of_the_spec_is_listed(self):
        for name in ("data/support.json", "docs/superpowers/previews/assets/bi-cripto.js", "docs/superpowers/previews/assets/bi-cripto-core.js",
                     "docs/superpowers/previews/assets/vendor/crossmark-sdk.js", "docs/superpowers/previews/assets/vendor/three/build/three.module.js",
                     ".github/workflows/pages.yml", ".github/scripts/guard.py", ".github/guard-paths.txt", "deploy/staging/deploy.yml",
                     "docs/superpowers/tools/csp.py", "pipelines/tests/test_support.py", "SECURITY.md"):
            with self.subTest(name=name):
                self.assertEqual(guard.sensitive([name]), [name])

    def test_codeowners_names_every_guard_path(self):
        owners = (REPO / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
        for p in guard.patterns():
            want = "/" + (p[:-1] if p.endswith("/*") else p)
            with self.subTest(pattern=p):
                self.assertRegex(owners, rf"(?m)^{re.escape(want)} @Brasil-Imposto/maintainers$")


class GuardWorkflowTest(unittest.TestCase):
    def test_it_runs_from_the_base_and_reads_the_pull_request_only_through_the_api(self):
        t = workflow()
        self.assertIn("pull_request_target:", t)
        self.assertIn("types: [opened, reopened, synchronize, labeled, unlabeled]", t)
        self.assertRegex(t, r"(?m)^permissions: \{\}$")
        self.assertNotIn("ref:", t, "the checkout is the base branch's default")
        self.assertNotIn("github.event.pull_request.head", t)
        self.assertIn("sparse-checkout: |\n            .github/scripts/guard.py\n            .github/guard-paths.txt\n", t)
        self.assertIn('gh api -X DELETE "repos/$REPO/issues/$PR/labels/$LABEL"', t, "R3: a new push takes the label off")
        self.assertIn("LABEL: seguranca-revisada", t)

    def test_control_a_checkout_of_the_pull_request_is_seen(self):
        planted = workflow().replace("persist-credentials: false", "persist-credentials: false\n          ref: ${{ github.event.pull_request.head.sha }}", 1)
        self.assertNotEqual(planted, workflow())
        self.assertTrue("ref:" in planted and "github.event.pull_request.head" in planted)


if __name__ == "__main__":
    unittest.main()
