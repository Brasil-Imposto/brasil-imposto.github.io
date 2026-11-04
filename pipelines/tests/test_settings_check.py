"""settings-check.py (spec seguranca-doacoes, section 5): the comparison of the settings read through the API with the expected ones."""
import importlib.util
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "docs" / "superpowers" / "tools"
_spec = importlib.util.spec_from_file_location("settings_check", TOOLS / "settings-check.py")
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)
REPO = "Brasil-Imposto/brasil-imposto.github.io"


def good():
    w = sc.EXPECTED[REPO]
    return {"branches": {b: {"rules": set(v["rules"]), "checks": set(v["checks"])} for b, v in w["branches"].items()}, "actions": dict(w["actions"])}


class SettingsCheckTest(unittest.TestCase):
    def test_the_expected_settings_pass(self):
        self.assertEqual(sc.problems(REPO, good(), sc.EXPECTED[REPO]), [])

    def test_each_missing_setting_is_reported(self):
        g = good(); g["branches"]["staging"]["checks"].discard("guard"); g["branches"]["main"]["rules"].discard("deletion")
        g["actions"]["sha_pinning_required"] = False; del g["branches"]["main"]
        found = sc.problems(REPO, g, sc.EXPECTED[REPO])
        self.assertIn(f"{REPO} staging: check guard not required", found)
        self.assertIn(f"{REPO} main: no deletion rule", found)
        self.assertIn(f"{REPO} actions: sha_pinning_required is False, not True", found)

    def test_control_a_repository_with_no_ruleset_fails_everything(self):
        found = sc.problems("Brasil-Imposto/staging", {"branches": {}, "actions": {"allowed_actions": "all", "sha_pinning_required": False}}, sc.EXPECTED["Brasil-Imposto/staging"])
        self.assertEqual(len(found), 4 + 1 + 2)


if __name__ == "__main__":
    unittest.main()
