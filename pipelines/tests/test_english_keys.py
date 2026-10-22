"""JSON keys in English (cleanup plan, task 6, B14): every key of the tracked data files is English, a proper name (a body,
a programme, a slug) or a field named as its source names it. The keys that still wait are listed here with the reason, so
the list can only shrink: a key that is renamed must leave WAITING too."""
import json
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Portuguese words that do not occur in the English keys of the project
PT = set("""nome numero valor data dias inicio reinicio observacao justificativa percentual aditado aditados aditivos termos
ultimo ato pessoal encargos custeio beneficios investimento inversoes funcao orgao localizador natureza estadual estaduais
executivo judiciario legislativo soma rotulos diferenca conferencia regioes pizza classificado nao credor posse moradia verbas
aux cadastro situacao vinculo exercicio ponte ano mes municipio prefeito governador deputado distrital senador cargo partido
eleito eleicao mandato titular suplente folha salario apostilamentos paralisacoes despesas correntes outras militares
aposentados ativos pensionistas sentencas exercicios anteriores sem""".split())

# proper names and source fields, kept as written (each with where it comes from)
ALLOWED = {
    "data", "data_as_of", "data_issues", "why_no_data",     # English "data"
    "vice", "vice_mayor", "ordinary_vice_mayors_elected", "supplementary_vice_mayors_elected",  # English "vice"
    "receita", "receita_2024", "release_receita_2024", "receita_national_total", "federal_revenue_total_receita",
    "union_block_sent_states_plus_union_minus_receita_total",   # the Receita Federal, a body
    "consortium_members_receita",
    "salario_educacao_quotas",                                  # the Salário-Educação, a federal contribution
    "vlbruto", "vlestorno",                                     # fields of the SC transparency portal API
    "tse_cargo",                                                # a field of the TSE candidacy file
    "ponte-hercilio-luz",                                       # a case slug
}
SLUG = re.compile(r"^(program:|[a-z]+(-[a-z]+){2,}-[a-z]{2}$)")    # programme slugs and person ids

# keys that wait, with the reason; they leave this list when they are renamed
WAITING = {
    # read by the Três Poderes page that the open interface pull request changes
    "data/federal/officeholders-2026.json": {"posse", "sen_moradia", "sen_moradia_api", "sen_verbas"},
    "data/federal/positions-2026.json": {"aux", "posse", "sen_moradia", "sen_moradia_api", "sen_verbas"},
    # in the home bundle, whose size the pages of the open interface pull request carry
    "data/series/federal-payroll-by-uf.json": None,
    "data/politicians/state-deputies.json": {"deputado_distrital", "deputado_estadual"},
    "data/politicians/federal-deputies.json": {"persons_with_suplente_term", "suplente_terms_by_legislature"},
    "data/politicians/senators.json": {"persons_titular_only", "persons_with_suplente_exercise", "titular"},
}


def portuguese_keys(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            words = re.split(r"[_\-\s]+", k.lower())
            if (not re.fullmatch(r"[A-Z0-9_.:/ -]+", k) and " " not in k and len(k) < 60 and k not in ALLOWED
                    and not SLUG.match(k) and PT.intersection(words)):
                out.add(k)
            portuguese_keys(v, out)
    elif isinstance(obj, list):
        for x in obj:
            portuguese_keys(x, out)
    return out


def scan():
    files = subprocess.run(["git", "-C", str(REPO), "ls-files", "data/*.json"], capture_output=True, text=True,
                           check=True).stdout.split()
    found = {}
    for f in files:
        keys = portuguese_keys(json.loads((REPO / f).read_text(encoding="utf-8")), set())
        if keys:
            found[f] = keys
    return found


class EnglishKeysTest(unittest.TestCase):
    def test_only_the_waiting_keys_are_portuguese(self):
        found = scan()
        for f, keys in found.items():
            self.assertIn(f, WAITING, f"{f}: Portuguese keys {sorted(keys)}")
            if WAITING[f] is not None:
                self.assertEqual(keys, WAITING[f], f"{f}: the waiting list is out of date")
        self.assertEqual(set(WAITING) - set(found), set(), "a file left WAITING's reason behind: drop it from the list")

    def test_control_a_planted_key_is_caught(self):
        self.assertEqual(portuguese_keys({"ok": {"nome_controle": 1}}, set()), {"nome_controle"})


if __name__ == "__main__":
    unittest.main()
