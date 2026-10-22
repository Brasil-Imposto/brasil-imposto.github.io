"""Proves the move of data/scripts/ to pipelines/ (phase B0): every path a pipeline script builds from its own location
points, after the move, where it pointed before, with data/scripts/ mapped to pipelines/.

For each Python file, every expression that evaluates to a path (built from __file__, os, pathlib and the names the file
assigns from them) is evaluated twice in a fake repository root: the old file at its old place, from a base commit, and the
new file at its new place. The two lists must match one to one after mapping the old values. String literals naming the
old folder count too. Nothing is executed beyond those expressions and nothing touches the disk.

Run: python3 docs/superpowers/tools/prove-pipelines-move.py <base-commit>   (exit 1 on any mismatch)
"""
import ast
import os
import pathlib
import subprocess
import sys
from pathlib import Path

OLD, NEW, FAKE = "data/scripts/", "pipelines/", "/fake-repo"
REPO = Path(__file__).resolve().parents[3]


def evaluate(source, rel_path):
    """Path-like values of every expression in the file, in source order, as repository-relative strings."""
    tree = ast.parse(source)
    env = {"__file__": f"{FAKE}/{rel_path}", "os": os, "Path": Path, "pathlib": pathlib, "__builtins__": {"str": str}}
    for node in sorted((n for n in ast.walk(tree) if isinstance(n, ast.Assign)), key=lambda n: n.lineno):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                env[node.targets[0].id] = eval(compile(ast.Expression(node.value), rel_path, "eval"), env)
            except Exception:
                pass
    known = {k for k in env if k not in ("os", "Path", "pathlib", "__builtins__")}
    parent = {c: n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
    found = {}
    for node in sorted((n for n in ast.walk(tree) if isinstance(n, ast.expr)), key=lambda n: (n.lineno, n.col_offset)):
        names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and ("data/scripts" in node.value or "pipelines/" in node.value):
            found[node] = (node.lineno, "literal", node.value.replace("data/scripts", "<S>").replace("pipelines", "<S>"))
            continue
        if not names & known or isinstance(node, ast.Name):
            continue
        try:
            v = eval(compile(ast.Expression(node), rel_path, "eval"), env)
        except Exception:
            continue
        s = str(v) if isinstance(v, (str, Path)) else None
        if s and s.startswith(FAKE):
            found[node] = (node.lineno, "path", os.path.relpath(os.path.normpath(s), FAKE))

    def inside_another(node):  # a path built inside a larger path expression is judged by the larger one
        p = parent.get(node)
        while p is not None and isinstance(p, ast.expr):
            if p in found and found[p][1] == "path":
                return True
            p = parent.get(p)
        return False
    return [v for n, v in sorted(found.items(), key=lambda kv: (kv[0].lineno, kv[0].col_offset)) if not inside_another(n)]


def main(base):
    old_files = subprocess.run(["git", "ls-tree", "-r", "--name-only", base, OLD], capture_output=True, text=True, cwd=REPO, check=True).stdout.split()
    bad, checked, compared = [], 0, 0
    for old_rel in old_files:
        if not old_rel.endswith(".py"):
            continue
        new_rel = NEW + old_rel[len(OLD):]
        if not (REPO / new_rel).exists():
            bad.append(f"{old_rel}: no file at {new_rel}")
            continue
        old_src = subprocess.run(["git", "show", f"{base}:{old_rel}"], capture_output=True, text=True, cwd=REPO, check=True).stdout
        old_v = evaluate(old_src, old_rel)
        new_v = evaluate((REPO / new_rel).read_text(encoding="utf-8"), new_rel)
        mapped = [(kind, NEW + v[len(OLD):] if kind == "path" and v.startswith(OLD) else NEW.rstrip("/") if kind == "path" and v == OLD.rstrip("/") else v) for _, kind, v in old_v]
        got = [(kind, v) for _, kind, v in new_v]
        checked += 1
        compared += len(mapped)
        if mapped != got:
            for i, (a, b) in enumerate(zip(mapped + [None] * len(got), got + [None] * len(mapped))):
                if a != b:
                    line = new_v[i][0] if i < len(new_v) else old_v[i][0]
                    bad.append(f"{new_rel}:{line}: expected {a}, got {b}")
                    break
    print(f"{checked} files, {compared} path expressions compared, {len(bad)} mismatches")
    for b in bad[:20]:
        print("  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
