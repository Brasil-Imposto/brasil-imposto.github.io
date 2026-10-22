"""The repository layout after phase B0: the Python pipelines live in pipelines/ and nothing points at the old data/scripts/.

- No tracked text file names the old folder, except docs/decisions/README.md, which is generated from the maintainer's
  private record and is updated there.
- In every pipeline file, each ROOT or REPO built from __file__ is the repository root, every path built from __file__ stays
  inside the repository, and every folder put on sys.path exists.
Run: python3 -m unittest discover -s pipelines/tests
"""
import ast
import os
import pathlib
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OLD = re.compile(r"""data/scripts|(['"])data\1\s*[/,]\s*(['"])scripts\2""")
GENERATED = {"docs/decisions/README.md"}


def tracked_text_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True).stdout.decode()
    for rel in filter(None, out.split("\0")):
        p = REPO / rel
        if p.is_file() and p.stat().st_size < 20_000_000:
            try:
                yield rel, p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue


def path_values(path, as_file=None):
    """(lineno, name or None, value) for every path a file builds from __file__, os and pathlib, outermost expressions only."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    env = {"__file__": str(as_file or path), "os": os, "Path": Path, "pathlib": pathlib, "__builtins__": {"str": str}}
    names = {}
    for node in sorted((n for n in ast.walk(tree) if isinstance(n, ast.Assign)), key=lambda n: n.lineno):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                env[node.targets[0].id] = eval(compile(ast.Expression(node.value), str(path), "eval"), env)
                names[node.value] = node.targets[0].id
            except Exception:
                pass
    known = {k for k in env if k not in ("os", "Path", "pathlib", "__builtins__")}
    parent = {c: n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
    found = {}
    for node in (n for n in ast.walk(tree) if isinstance(n, ast.expr) and not isinstance(n, ast.Name)):
        if not {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} & known:
            continue
        try:
            v = eval(compile(ast.Expression(node), str(path), "eval"), env)
        except Exception:
            continue
        if isinstance(v, (str, Path)) and os.path.isabs(str(v)):
            found[node] = os.path.normpath(str(v))

    def inside_another(node):
        p = parent.get(node)
        while isinstance(p, ast.expr):
            if p in found:
                return True
            p = parent.get(p)
        return False
    return tree, [(n.lineno, names.get(n), v, n) for n, v in found.items() if not inside_another(n)]


def file_paths(path):
    """The values of path_values that depend on the file's own location: evaluated again as if the file lived elsewhere,
    they change. Working folders and other fixed paths do not."""
    tree, here = path_values(path)
    _, there = path_values(path, Path("/elsewhere") / path.relative_to(REPO))
    moved = {(line, v) for line, _, v, _ in there}
    return tree, [item for item in here if (item[0], item[2]) not in moved]


class LayoutTest(unittest.TestCase):
    def test_no_reference_to_the_old_folder(self):
        hits = [f"{rel}:{i}" for rel, text in tracked_text_files() if rel not in GENERATED
                for i, line in enumerate(text.splitlines(), 1) if OLD.search(line)]
        self.assertEqual(hits, [], "files still name data/scripts")

    def test_paths_built_from_file_point_inside_the_repository(self):
        files = sorted((REPO / "pipelines").rglob("*.py"))
        self.assertGreater(len(files), 100)
        problems = []
        for f in files:
            rel = f.relative_to(REPO)
            tree, values = file_paths(f)
            for line, name, value, _ in values:
                if not (value + os.sep).startswith(str(REPO) + os.sep):
                    problems.append(f"{rel}:{line} leaves the repository: {value}")
                if name in ("ROOT", "REPO") and value != str(REPO):
                    problems.append(f"{rel}:{line} {name} is {value}, not the repository root")
            for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
                if ast.unparse(call.func) == "sys.path.insert" and len(call.args) == 2:
                    for line, _, value, node in values:
                        if any(node is a or node in ast.walk(a) for a in call.args[1:]) and not os.path.isdir(value):
                            problems.append(f"{rel}:{line} puts a missing folder on sys.path: {value}")
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
