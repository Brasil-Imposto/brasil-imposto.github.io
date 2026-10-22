"""Matching of municipality names in the Receita Federal and Portal da Transparência files to IBGE codes.

The files carry names without accents and, for a few municipalities, a different spelling; ALIAS holds those differences
per state, found by the unmatched-name lists of the builders (an unmatched name means money without a municipality).
"""
import unicodedata

ALIAS = {
    "SC": {"BALNEARIO DE PICARRAS": "BALNEARIO PICARRAS", "PRESIDENTE CASTELO BRANCO": "PRESIDENTE CASTELLO BRANCO"},
    "RS": {"SANTANA DO LIVRAMENTO": "SANT ANA DO LIVRAMENTO"},  # IBGE: Sant'Ana do Livramento
}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    for a, b in (("'", " "), ("-", " "), (".", " ")): s = s.replace(a, b)
    return " ".join(s.split())


def matcher(uf, names):
    """names: {ibge_code: IBGE name}. Returns code_of(name) -> ibge_code or None."""
    by_norm = {norm(n): c for c, n in names.items()}
    alias = ALIAS.get(uf, {})

    def code_of(name):
        n = norm(name); n = alias.get(n, n); return by_norm.get(n)
    return code_of
