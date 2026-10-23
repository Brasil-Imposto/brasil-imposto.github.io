"""Case pages give a portrait only to the person it shows, by exact name (cleanup plan, task 7, P2-8). The old match by first
and last name gave a governor's photo to anyone whose name started the same way. build-cases.py builds the page data when run,
so the test takes only its portrait table and functions, read from the source."""
import ast
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "docs" / "superpowers" / "tools" / "build-cases.py"
CREDITS = {f"assets/cases/{c}/{f}.jpg": {"credit": "x", "link": "y"} for c, f in (
    ("hercilio-luz", "gov-carlos-moises"), ("ete-insular", "gov-daniela-reinehr"), ("ete-insular", "gov-jorginho-mello"),
    ("cei-comasa-joinville", "prefeito-adriano-silva"))}


def load():
    tree = ast.parse(SRC.read_text(encoding="utf-8"))
    keep = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name in ("slugify", "portrait"))
            or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "PORTRAITS" for t in n.targets))]
    ns = {"unicodedata": __import__("unicodedata")}
    exec(compile(ast.Module(body=keep, type_ignores=[]), str(SRC), "exec"), ns)
    return ns["portrait"]


class CasePortraitTest(unittest.TestCase):
    def test_portrait_by_exact_name_only(self):
        portrait = load()
        self.assertEqual(portrait("Carlos Moisés da Silva", CREDITS)[0], "assets/cases/hercilio-luz/gov-carlos-moises.jpg")
        self.assertEqual(portrait("Adriano Bornschein Silva (Adriano Silva)", CREDITS)[0],
                         "assets/cases/cei-comasa-joinville/prefeito-adriano-silva.jpg")
        # control: another person whose first names are the same must get no photo
        self.assertEqual(portrait("Carlos Moisés Pereira", CREDITS), (None, None))
        self.assertEqual(portrait("Jorginho Santos", CREDITS), (None, None))


if __name__ == "__main__":
    unittest.main()
