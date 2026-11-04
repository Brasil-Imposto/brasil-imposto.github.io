"""Writes a poisoned copy of a built site (spec seguranca-doacoes, section 14, attack P1): every display text of every data
file ends with PAYLOAD, so a text that reaches a page as HTML instead of text inserts an <img src="x">. poison-check.cjs
serves the copy.

Run: python3 docs/superpowers/tools/poison-data.py <built site> <out>
"""
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

PAYLOAD = '"\'><img src="x" onerror="window.__xss=1">'
PER_FIELD = 150   # texts poisoned per field: every field covered and the page still loads (2026-11-01: 110 MB crashed the browser)
ASSIGN = re.compile(r'^\s*((?:window\.)?[A-Za-z_$][\w$.]*\s*=\s*)(.*?);?\s*$', re.S)
DISPLAY_WORD = re.compile(r'[A-Z][a-z]{2,}')


def is_display(s):
    """A text a person reads: has a space, a letter outside ASCII, is markup or a link, or is one capitalized word."""
    return (" " in s or any(ord(ch) > 127 and ch.isalpha() for ch in s) or s.startswith("<") or s.startswith("http")
            or bool(DISPLAY_WORD.fullmatch(s)))


def poison(value, path, seen):
    if path == "bi-data.js.icons":
        return value   # the icons are markup on purpose; icon_check.py refuses any icon outside Lucide's vocabulary at build
    if isinstance(value, dict):
        return {k: poison(v, f"{path}.{k}" if not k.isdigit() else f"{path}.#", seen) for k, v in value.items()}
    if isinstance(value, list):
        return [poison(v, f"{path}[]", seen) for v in value]
    if isinstance(value, str) and is_display(value) and seen[path] < PER_FIELD:
        seen[path] += 1
        return value + PAYLOAD
    return value


def main(src, out):
    src, out = Path(src), Path(out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out)
    seen = Counter()
    for f in sorted((out / "assets").glob("*.js")) + sorted((out / "assets").glob("*.json")):
        text = f.read_text(encoding="utf-8")
        m = ASSIGN.match(text) if f.suffix == ".js" else None
        body, head = (m.group(2), m.group(1)) if m else (text, None)
        try:
            data = json.loads(body)
        except ValueError:
            continue   # code, not data
        data = poison(data, f.name, seen)
        dumped = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        f.write_text((head + dumped + ";\n") if head else dumped, encoding="utf-8")
    block = re.compile(r'(<script type="application/json" id="bi-cripto-data">)(.*?)(</script>)', re.S)
    for page in sorted(out.glob("*.html")):
        t = page.read_text(encoding="utf-8")
        m = block.search(t)
        if not m:
            continue
        data = poison(json.loads(m.group(2)), "bi-cripto-data", seen)
        dumped = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        page.write_text(t[:m.start(2)] + dumped + t[m.end(2):], encoding="utf-8")
    fields, texts = len(seen), sum(seen.values())
    print(f"poisoned {texts} texts in {fields} fields")
    if texts < 5000:
        raise SystemExit("poison-data: fewer than 5,000 texts poisoned; the poisoner is broken, not the site")


if __name__ == "__main__":
    main(*sys.argv[1:3])
