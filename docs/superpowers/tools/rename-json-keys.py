"""Renames identifier keys of data/ files to English (phase B0, D151, issue #8), from english-keys-map.json, and proves it.

The rename is textual, so each file keeps its layout: only the `"old":` tokens of the mapped keys change. The proof, for
every file in the map, compares with a base commit:
- the new text equals the old text with exactly the mapped key tokens replaced, and
- the new file loads to the old data with the mapped keys renamed (same values, same order, nothing else).
A key the map names that the file does not have, or a new name that already exists beside it, is an error.

Run: python3 docs/superpowers/tools/rename-json-keys.py apply
     python3 docs/superpowers/tools/rename-json-keys.py check <base-commit>   (exit 1 on any difference)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAP = json.loads((Path(__file__).with_name("english-keys-map.json")).read_text(encoding="utf-8"))
MAP.pop("_about")


def split(spec):
    key, _, parent = spec.partition("@")
    return key, parent or None


def rename_obj(o, renames, parent=None, used=None):
    """The data with the mapped keys renamed; `used` collects the specs that matched."""
    if isinstance(o, list):
        return [rename_obj(v, renames, parent, used) for v in o]
    if not isinstance(o, dict):
        return o
    out = {}
    for k, v in o.items():
        new = k
        for spec, target in renames.items():
            key, scope = split(spec)
            if k == key and (scope is None or scope == parent):
                new = target
                used.add(spec)
        if new in out or (new != k and new in o):
            raise ValueError(f"renaming {k} to {new} collides with an existing key")
        out[new] = rename_obj(v, renames, k, used)
    return out


def rename_text(text, data, renames):
    """Replace the "key": tokens in the file's own text, scoped renames only where the structure says so."""
    tokens = list(re.finditer(r'"((?:[^"\\]|\\.)*)"\s*:', text))
    # walk the parsed structure in document order to know each key's parent
    order = []

    def walk(o, parent):
        if isinstance(o, list):
            for v in o:
                walk(v, parent)
        elif isinstance(o, dict):
            for k, v in o.items():
                order.append((k, parent))
                walk(v, k)
    walk(data, None)
    if len(order) != len(tokens) or any(json.loads(f'"{t.group(1)}"') != k for t, (k, _) in zip(tokens, order)):
        raise ValueError("could not line the key tokens up with the parsed keys")
    out, last = [], 0
    for t, (k, parent) in zip(tokens, order):
        for spec, target in renames.items():
            key, scope = split(spec)
            if k == key and (scope is None or scope == parent):
                out.append(text[last:t.start(1)] + target)
                last = t.end(1)
    return "".join(out) + text[last:]


def apply():
    for rel, renames in MAP.items():
        p = REPO / rel
        text = p.read_text(encoding="utf-8")
        data = json.loads(text)
        used = set()
        rename_obj(data, renames, used=used)
        missing = set(renames) - used
        if missing:
            raise SystemExit(f"{rel}: the map names keys the file does not have: {sorted(missing)}")
        p.write_text(rename_text(text, data, renames), encoding="utf-8")
        print(f"{rel}: {len(renames)} keys renamed")


def check(base):
    bad = 0
    for rel, renames in MAP.items():
        old_rel = rel
        old = subprocess.run(["git", "show", f"{base}:{old_rel}"], cwd=REPO, capture_output=True, text=True)
        if old.returncode:
            print(f"{rel}: not in {base}"); bad += 1; continue
        new_text = (REPO / rel).read_text(encoding="utf-8")
        old_data, used = json.loads(old.stdout), set()
        expected_data = rename_obj(old_data, renames, used=used)
        new_data = json.loads(new_text)
        same_values = json.dumps(new_data, ensure_ascii=False) == json.dumps(expected_data, ensure_ascii=False)
        same_text = new_text == rename_text(old.stdout, old_data, renames)
        missing = set(renames) - used
        ok = same_values and same_text and not missing
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'} {rel}: {len(renames)} keys; values equal: {same_values}; only key tokens changed: {same_text}"
              + (f"; missing: {sorted(missing)}" if missing else ""))
    print(f"{len(MAP)} files, {bad} with a difference")
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["apply"]:
        apply()
    else:
        sys.exit(check(sys.argv[2]))
