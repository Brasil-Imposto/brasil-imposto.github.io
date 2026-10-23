"""Public decision log (D97): the decisions and questions without the author's literal quotes.

The original, with the author's words, is private/decisions-original.md (local, never versioned); sessions append to it.
This script writes docs/decisions/README.md from it, removing every quotation of the author: the "(*"..."*)" parentheticals
and the inline *"..."* quotes. Run it after every change to the original.

Usage: uv run python -B docs/superpowers/tools/publish-decisions.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC, OUT = ROOT / "private" / "decisions-original.md", ROOT / "docs" / "decisions" / "README.md"
t = SRC.read_text(encoding="utf-8")
n_paren = len(re.findall(r'\(\*"', t))
t = re.sub(r'\s*\(\*"[\s\S]*?"\*\)', "", t)                 # (*"..."*)
# the italic quote *"..."* only: a bold title that quotes a label, **"..."**, is not the author's quote
ITALIC = r'(?<!\*)\*"[^\n]*?"\*(?!\*)'
n_inline = len(re.findall(ITALIC, t))
t = re.sub(r"\s?" + ITALIC, "", t)
t = re.sub(r"\(\s*[;,]?\s*\)", "", t)                        # empty parentheses left behind
t = re.sub(r"\(\s*[;,]\s*", "(", t)
t = re.sub(r" +([.,;:])", r"\1", t)
t = re.sub(r":\s*,", ":", t)                                # "abono:, ficam" where a quote was
t = re.sub(r"nas palavras do autor:\*\*\s*[;,]?", "segundo o autor:**", t)
t = re.sub(r"\*\*\s*;", "**", t)
if not (not re.search(r'(?<!\*)\*"|"\*(?!\*)', t)):
    raise SystemExit("a quotation survived")
head = ("# Decisões e perguntas do Brasil-Imposto\n\n> Registro público das decisões (D1 em diante) e das perguntas em aberto. As citações literais do autor "
        "ficam fora desta versão (D97).\n\n")
body = t.split("\n", 1)[1] if t.startswith("# ") else t
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(head + body, encoding="utf-8")
print("removed", n_paren, "parenthetical and", n_inline, "inline quotations ->", OUT.relative_to(ROOT))
