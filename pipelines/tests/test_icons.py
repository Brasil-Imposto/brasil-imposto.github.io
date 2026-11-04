"""Every icon that build-standalone-data.py puts in bi-data.js is a plain Lucide drawing (spec seguranca-doacoes, section 8):
the icons become HTML on the page, so an icon with a handler, a link or a script would run."""
import importlib.util
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "docs" / "superpowers" / "tools"
spec = importlib.util.spec_from_file_location("icon_check", TOOLS / "icon_check.py")
icon_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(icon_check)


class IconTest(unittest.TestCase):
    def test_every_committed_icon_is_clean(self):
        for f in sorted((TOOLS.parent / "previews" / "assets" / "icons").glob("*.svg")):
            with self.subTest(icon=f.name):
                self.assertEqual(icon_check.problems(f.read_text(encoding="utf-8")), [])

    def test_planted_icons_are_refused(self):
        good = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 3h18"/></svg>'
        self.assertEqual(icon_check.problems(good), [])   # the control: a clean icon passes
        for bad in ('<svg onload="x()"><path d="M0 0"/></svg>', '<svg><script>x()</script></svg>', '<svg><a href="javascript:x()"><path d="M0 0"/></a></svg>',
                    '<svg><foreignObject><img src="x"></foreignObject></svg>', '<svg><path d="M0 0" style="x"/></svg>', '<svg></svg><img src="x">'):
            with self.subTest(bad=bad):
                self.assertNotEqual(icon_check.problems(bad), [])
