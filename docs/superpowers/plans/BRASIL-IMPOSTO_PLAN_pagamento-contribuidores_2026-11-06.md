# Brasil-Imposto: plano do pagamento público de quem contribui (spec do Apoie, seção 11)

> **Para quem implementa com agentes:** subagent-driven-development (um implementador por tarefa, revisão entre tarefas). Passos em
> caixas (`- [ ]`). Cada tarefa é um pull request no `staging`, com `git commit -s`, a etiqueta do `guard` (D223) quando toca um caminho
> de `.github/guard-paths.txt`, e o merge pela sessão com `gh pr merge --admin` só depois do portão que lê cada verificação.

**Meta:** a regra de D230 a D234 no ar no staging: a regra escrita, os textos novos da janela do Apoie, o livro-caixa público (dados,
conta ao centavo e página própria) e o script que calcula a divisão do mês a partir do GitHub.

**Arquitetura:** o livro-caixa é um JSON por mês em `data/support-ledger/`, validado por `schemas/support-ledger.schema.json` e por uma
conferência ao centavo em `pipelines/support/ledger.py`. A divisão é uma função pura em `pipelines/support/split_month.py` (issues do mês
e o valor a dividir entram, as partes saem), com uma busca separada no GitHub (GraphQL pelo `gh`). A página `livro-caixa.html` é montada
de `data/support-ledger/` por `build-ledger-page.py`, atrás da chave `livro-caixa` de `data/features.json` (ligada no staging, desligada
na produção até o lote, como toda funcionalidade nova).

**Ferramentas:** Python 3.12 (uv), `jsonschema` (Draft 2020-12, já no `uv.lock`), `unittest`, `gh` para a busca, os construtores de
`docs/superpowers/tools/`, `apoie-check.cjs` e `visible-text` para a tela.

**In English:** five pull requests into staging: the rule in GOVERNANCE and CONTRIBUTING, the new panel texts, the ledger data with its
to-the-cent check, the monthly split script, and the ledger page behind a staging-only switch. Tests first in each.

---

## Arquivos

| Arquivo | Papel |
|---|---|
| `GOVERNANCE.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.claude/CLAUDE.md` | a regra escrita (tarefa 1) |
| `docs/superpowers/tools/apoie.py`, `pipelines/tests/test_support.py` | os textos da janela (tarefa 2) |
| `schemas/support-ledger.schema.json`, `data/support-ledger/2026-11.json`, `pipelines/support/ledger.py`, `pipelines/tests/test_support_ledger.py` | o livro-caixa (tarefa 3) |
| `pipelines/support/split_month.py`, `pipelines/tests/test_split_month.py`, `pipelines/tests/fixtures/split/*.json` | a divisão (tarefa 4) |
| `data/features.json`, `docs/superpowers/tools/site_chrome.py`, `docs/superpowers/tools/build-ledger-page.py`, `docs/superpowers/tools/build-site.py`, `docs/superpowers/tools/check-all.py`, `.github/workflows/ci.yml`, `.github/workflows/pages.yml`, `deploy/staging/deploy.yml` (e a cópia do `Brasil-Imposto/staging`), `docs/superpowers/previews/livro-caixa.html`, `pipelines/tests/test_build_site.py` | a página (tarefa 5) |

---

### Tarefa 1: a regra escrita

**Arquivos:** `GOVERNANCE.md` (seção "Quem pode doar"), `CONTRIBUTING.md` (seção nova), `.github/PULL_REQUEST_TEMPLATE.md`,
`.claude/CLAUDE.md` (passo 2 do fluxo). Caminho do `guard`: `.github/*`.

- [ ] **Passo 1: `GOVERNANCE.md`, troca o texto inteiro de "Quem pode doar" por:**

```markdown
## Quem pode doar

O Brasil-Imposto é de código aberto e sem fins lucrativos: toda funcionalidade é e continua disponível para todas as pessoas, de
graça. Ainda não é uma associação registrada: as doações chegam às carteiras do mantenedor, e cada entrada e saída é publicada no
livro-caixa do apoio. Vale a regra 4 acima.

Como o dinheiro é dividido (spec do Apoie, seção 11):

1. Primeiro, a infraestrutura do mês, pelo recibo de cada gasto, só do que o projeto paga como projeto.
2. O resto vai para quem fechou no mês uma issue com peso (o rótulo `difficulty:low`, `difficulty:medium` ou `difficulty:high`, peso
   1, 2 ou 3, posto antes do trabalho), inclusive a pessoa mantenedora, na proporção do peso, por um script público.
3. O peso se discute na issue antes de começar; depois do merge não muda. Uma pessoa mantenedora pode tirar o peso de uma issue
   fechada por spam ou mau uso, com o motivo escrito na issue.
4. Não há pagamento do trabalho anterior à regra. Valor não reclamado volta à divisão depois de 6 meses.
5. Nenhum dado de pagamento vai em issue ou pull request: o pedido é feito em particular, só quando houver valor a pagar.
6. Quem contribui sabe que talvez nunca receba: o pagamento só existe quando há doação.
```

- [ ] **Passo 2: `CONTRIBUTING.md`, seção nova depois de "Revisão":**

```markdown
### Issues com peso

Uma issue com `difficulty:low`, `difficulty:medium` ou `difficulty:high` tem peso 1, 2 ou 3 na divisão das doações do mês (regra no
`GOVERNANCE.md`, "Quem pode doar"). Para pegar uma, peça na própria issue; uma pessoa mantenedora atribui. Se o peso parecer errado,
diga na issue antes de começar: depois do merge ele não muda. O pull request diz `Closes #N`. Nunca escreva dado de pagamento em
issue ou pull request. O projeto é sem fins lucrativos e talvez nunca haja pagamento: ele só existe quando há doação, e cada um fica
no livro-caixa público.
```

- [ ] **Passo 3: `.github/PULL_REQUEST_TEMPLATE.md`, linha nova no topo da lista de conferência:**

```markdown
- [ ] Se este pull request resolve uma issue com peso, ele diz `Closes #N` dela.
```

- [ ] **Passo 4: `.claude/CLAUDE.md`, no fim do passo 2 do fluxo, a frase:**

```markdown
   Trabalho que deve contar na divisão das doações precisa de uma issue com rótulo de dificuldade posto antes de começar, também o da
   pessoa mantenedora e o das sessões com agentes (D231).
```

- [ ] **Passo 5:** conferir: `python3 -c "t=open('GOVERNANCE.md').read();assert 'não recebe doação' not in t and 'é devolvida' not in t"`;
  a contagem de travessões dos quatro arquivos dá 0 com um controle; `uv run --locked python -m unittest discover -s pipelines/tests`.
- [ ] **Passo 6:** commit `docs(governance): the public rule that pays contributors (spec apoie 11, D230 to D234)`, pull request,
  etiqueta do `guard` listando `.github/PULL_REQUEST_TEMPLATE.md`.

---

### Tarefa 2: os textos da janela do Apoie

**Arquivos:** `docs/superpowers/tools/apoie.py`, `pipelines/tests/test_support.py`. Caminho do `guard`: `apoie.py`.

- [ ] **Passo 1: o teste primeiro.** Em `pipelines/tests/test_support.py`, no teste dos textos da vista principal (o que hoje percorre
  `apoie.LEAD, apoie.MONEY_TITLE, apoie.INFRA, apoie.DEVELOPERS, ... *apoie.MONTH`), acrescentar `apoie.ASSOC` à lista e um teste novo:

```python
    def test_the_texts_of_section_11_4(self):
        self.assertIn("sem fins lucrativos: toda funcionalidade é e continua disponível para todas as pessoas, de graça.", apoie.LEAD)
        self.assertEqual(apoie.ASSOC, "O Brasil-Imposto ainda não é uma associação registrada: as doações chegam às carteiras do "
                                      "mantenedor, e cada entrada e saída é publicada.")
        self.assertIn("só do que o projeto paga como projeto", apoie.INFRA)
        self.assertIn("Hoje o site é hospedado de graça no GitHub Pages e o projeto não paga nenhum serviço.", apoie.INFRA)
        self.assertIn("posto na issue antes do trabalho", apoie.DEVELOPERS)
        self.assertIn("Quem contribui sabe que talvez nunca receba", apoie.DEVELOPERS)
        self.assertEqual(len(apoie.MONTH), 4)
        self.assertFalse(any("25/09/2026" in m or "primeiras divisões" in m for m in apoie.MONTH))
        h = self.header("staging")
        self.assertIn(apoie.ASSOC, text(h))
        self.assertLess(text(h).index(apoie.LEAD[:40]), text(h).index(apoie.ASSOC))
```

  (`self.header` e `text` são os auxiliares que a classe dos textos já usa; se o nome for outro, usar o da classe.)

- [ ] **Passo 2:** rodar `uv run --locked python -m unittest pipelines.tests.test_support -k section_11_4`; esperado: falha (`ASSOC` não
  existe).
- [ ] **Passo 3: `apoie.py`.** Trocar as constantes pelos textos exatos da spec (11.4, D232):

```python
LEAD = ("O Brasil-Imposto mostra, com dados oficiais e a fonte de cada número, para onde vai o imposto pago no Brasil. É "
        "apartidário, de código aberto e sem fins lucrativos: toda funcionalidade é e continua disponível para todas as pessoas, "
        "de graça. O seu apoio paga duas coisas, e nada além delas: a infraestrutura que mantém os dados corretos e no ar e o "
        "trabalho de quem desenvolve o projeto.")
ASSOC = ("O Brasil-Imposto ainda não é uma associação registrada: as doações chegam às carteiras do mantenedor, e cada entrada e "
         "saída é publicada.")
INFRA = ("O custo real de cada mês, pelo recibo de cada gasto, só do que o projeto paga como projeto: servidor, banco de dados, "
         "domínio e a ferramenta de IA que coleta e confere os dados, quando paga em nome do projeto. Hoje o site é hospedado de "
         "graça no GitHub Pages e o projeto não paga nenhum serviço. A assinatura de IA de cada pessoa que contribui não entra "
         "aqui: ela é paga pela divisão. É a primeira coisa paga com o apoio.")
DEVELOPERS = ("Quem fecha uma issue com peso, inclusive a pessoa mantenedora. O que sobra de cada mês, depois da infraestrutura, é "
              "dividido pelo peso das issues fechadas no mês (1, 2 ou 3, posto na issue antes do trabalho). Quem contribui sabe que "
              "talvez nunca receba: o pagamento só existe quando há doação, e cada um é publicado no livro-caixa.")
MONTH = ["Primeiro, a infraestrutura do mês, pelo recibo de cada gasto.",
         "O resto vai para quem fechou issues com peso no mês, inclusive a pessoa mantenedora, na proporção do peso (1, 2 ou 3), por "
         "um script público que qualquer pessoa pode rodar.",
         "Num mês sem issue com peso fechada, o resto fica para o mês seguinte; valor não reclamado volta à divisão depois de 6 meses.",
         "Tudo fica no livro-caixa público: cada doação, cada gasto e cada pagamento."]
```

  e, no `modal()`, logo depois do parágrafo de `LEAD`, o parágrafo `f'<p class="bi-ap-assoc">{escape(ASSOC)}</p>'`, com o CSS
  `.bi-ap-assoc { margin: 10px 0 0; font-size: 13.5px; color: #4A5560; }` em `apoie.CSS` (o desenho aprovado da rodada `apoie-r4`).

- [ ] **Passo 4:** rodar o teste: passa. Rodar `uv run --locked python -m unittest discover -s pipelines/tests` e os construtores (a
  janela entra nas páginas commitadas: `build-platform-preview.py`, `build-site-chrome.py`, `build-notes-page.py`), conferindo que
  `git diff --stat docs/superpowers/previews/` só mostra as páginas com a janela.
- [ ] **Passo 5:** controle: trocar `ASSOC` por um texto com um caractere a mais faz o teste falhar; desfazer.
- [ ] **Passo 6:** commit `feat(apoie): the panel texts of the public pay rule (spec apoie 11.4, D230 to D232)`, pull request, etiqueta do
  `guard` listando `docs/superpowers/tools/apoie.py`.

---

### Tarefa 3: o livro-caixa (dados e conta ao centavo)

**Arquivos:** criar `schemas/support-ledger.schema.json`, `data/support-ledger/2026-11.json`, `pipelines/support/__init__.py` (vazio),
`pipelines/support/ledger.py`, `pipelines/tests/test_support_ledger.py`.

- [ ] **Passo 1: o esquema** `schemas/support-ledger.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "support-ledger.schema.json",
  "title": "Um mês do livro-caixa do apoio (spec do Apoie, seção 11.3)",
  "type": "object",
  "additionalProperties": false,
  "required": ["month", "opening_cents", "entries", "infra", "split", "payouts", "returned", "closing_cents"],
  "properties": {
    "month": {"type": "string", "pattern": "^20[0-9]{2}-(0[1-9]|1[0-2])$"},
    "opening_cents": {"type": "integer", "minimum": 0},
    "entries": {"type": "array", "items": {"type": "object", "additionalProperties": false,
      "required": ["date", "channel", "amount_cents"],
      "properties": {
        "date": {"type": "string", "format": "date"},
        "channel": {"enum": ["crypto", "pix"]},
        "amount_cents": {"type": "integer", "minimum": 1},
        "coin": {"type": "string"}, "coin_amount": {"type": "string"},
        "tx_url": {"type": "string", "pattern": "^https://"},
        "statement_url": {"type": "string", "pattern": "^https://"},
        "source_name": {"type": "string", "description": "só para fonte acima de 5% da receita do ano (regra 4)"}}}},
    "infra": {"type": "array", "items": {"type": "object", "additionalProperties": false,
      "required": ["date", "service", "amount_cents", "receipt_url"],
      "properties": {"date": {"type": "string", "format": "date"}, "service": {"type": "string"},
                     "amount_cents": {"type": "integer", "minimum": 1}, "receipt_url": {"type": "string", "pattern": "^https://"}}}},
    "split": {"oneOf": [{"type": "null"}, {"type": "object", "additionalProperties": false,
      "required": ["pool_cents", "shares", "kept_cents"],
      "properties": {"pool_cents": {"type": "integer", "minimum": 0}, "kept_cents": {"type": "integer", "minimum": 0},
        "shares": {"type": "array", "items": {"type": "object", "additionalProperties": false,
          "required": ["login", "issues", "points", "amount_cents"],
          "properties": {"login": {"type": "string"}, "points": {"type": "integer", "minimum": 1},
            "amount_cents": {"type": "integer", "minimum": 0},
            "issues": {"type": "array", "items": {"type": "object", "additionalProperties": false, "required": ["number", "weight"],
              "properties": {"number": {"type": "integer"}, "weight": {"enum": [1, 2, 3]}}}}}}}}}]},
    "payouts": {"type": "array", "items": {"type": "object", "additionalProperties": false,
      "required": ["login", "split_month", "amount_cents", "date", "channel"],
      "properties": {"login": {"type": "string"}, "split_month": {"type": "string", "pattern": "^20[0-9]{2}-(0[1-9]|1[0-2])$"},
        "amount_cents": {"type": "integer", "minimum": 1}, "date": {"type": "string", "format": "date"},
        "channel": {"enum": ["crypto", "pix"]}, "tx_url": {"type": "string", "pattern": "^https://"}}}},
    "returned": {"type": "array", "items": {"type": "object", "additionalProperties": false,
      "required": ["login", "split_month", "amount_cents", "date"],
      "properties": {"login": {"type": "string"}, "split_month": {"type": "string"}, "amount_cents": {"type": "integer", "minimum": 1},
        "date": {"type": "string", "format": "date"}}}},
    "closing_cents": {"type": "integer", "minimum": 0}
  }
}
```

- [ ] **Passo 2: o primeiro mês** `data/support-ledger/2026-11.json` (o mês da regra; nada recebido):

```json
{"month": "2026-11", "opening_cents": 0, "entries": [], "infra": [], "split": null, "payouts": [], "returned": [], "closing_cents": 0}
```

- [ ] **Passo 3: o teste primeiro** `pipelines/tests/test_support_ledger.py`:

```python
"""The support ledger (spec apoie 11.3): every month valid against its schema, the balance closing to the cent, the owed amounts never
negative, and each month's pool what the rule gives. Controls: one real more in an entry, a payout above what was owed, a split
whose shares plus the kept cents differ from the pool."""
import unittest

from pipelines.support import ledger


class LedgerTest(unittest.TestCase):
    def test_every_month_is_valid_and_closes(self):
        months = ledger.load_all()
        self.assertGreaterEqual(len(months), 1)
        self.assertEqual(ledger.problems(months), [])

    def test_control_one_real_more_in_an_entry(self):
        m = [{"month": "2026-12", "opening_cents": 0, "entries": [{"date": "2026-12-03", "channel": "pix", "amount_cents": 10100}],
              "infra": [], "split": None, "payouts": [], "returned": [], "closing_cents": 10000}]
        self.assertTrue(any("does not close" in p for p in ledger.problems(m)))

    def test_control_a_payout_above_what_was_owed(self):
        dec = {"month": "2026-12", "opening_cents": 0, "entries": [{"date": "2026-12-03", "channel": "pix", "amount_cents": 10000}],
               "infra": [], "split": {"pool_cents": 10000, "kept_cents": 0, "shares": [
                   {"login": "a", "issues": [{"number": 1, "weight": 1}], "points": 1, "amount_cents": 10000}]},
               "payouts": [], "returned": [], "closing_cents": 10000}
        # January closes to the cent (10,000 + 1 - 10,001 = 0), so only the owed check can fire
        jan = {"month": "2027-01", "opening_cents": 10000, "entries": [{"date": "2027-01-02", "channel": "pix", "amount_cents": 1}],
               "infra": [], "split": None,
               "payouts": [{"login": "a", "split_month": "2026-12", "amount_cents": 10001, "date": "2027-01-05", "channel": "pix"}],
               "returned": [], "closing_cents": 0}
        found = ledger.problems([dec, jan])
        self.assertEqual(len(found), 1, found)
        self.assertIn("more than owed", found[0])

    def test_control_a_split_that_does_not_add_up(self):
        m = [{"month": "2026-12", "opening_cents": 0, "entries": [{"date": "2026-12-03", "channel": "pix", "amount_cents": 10000}],
              "infra": [], "split": {"pool_cents": 10000, "kept_cents": 1, "shares": [
                  {"login": "a", "issues": [{"number": 1, "weight": 1}], "points": 1, "amount_cents": 10000}]},
              "payouts": [], "returned": [], "closing_cents": 10000}]
        self.assertTrue(any("shares plus kept" in p for p in ledger.problems(m)))

    def test_the_pool_follows_the_rule(self):
        dec = {"month": "2026-12", "opening_cents": 0, "entries": [{"date": "2026-12-03", "channel": "pix", "amount_cents": 50000}],
               "infra": [{"date": "2026-12-10", "service": "servidor", "amount_cents": 2000, "receipt_url": "https://example.org/r"}],
               "split": None, "payouts": [], "returned": [], "closing_cents": 48000}
        self.assertEqual(ledger.pool_cents([dec], "2026-12"), 48000)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Passo 4:** rodar; esperado: falha de importação (`pipelines.support.ledger` não existe).
- [ ] **Passo 5: `pipelines/support/ledger.py`:**

```python
"""The support ledger (spec apoie 11.3): one JSON per month in data/support-ledger/, valid against schemas/support-ledger.schema.json.
The balance closes to the cent (opening + entries - infrastructure - payouts = closing), each month opens with the previous closing,
nothing is paid or returned beyond what a split left owed, and a split's shares plus its kept cents equal its pool. The pool of a
month is its closing balance minus what earlier splits still owe after that month's payouts and returns (spec 11.2, items 5 and 9)."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

REPO = Path(__file__).resolve().parents[2]
DIR = REPO / "data" / "support-ledger"
SCHEMA = json.loads((REPO / "schemas" / "support-ledger.schema.json").read_text(encoding="utf-8"))


def load_all():
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(DIR.glob("*.json"))]


def _sum(items):
    return sum(i["amount_cents"] for i in items)


def owed(months, until):
    """What each (login, split month) is still owed after every payout and return up to and including the month `until`."""
    left = {}
    for m in months:
        if m["month"] > until:
            break
        for p in m["payouts"] + m["returned"]:
            left[(p["login"], p["split_month"])] = left.get((p["login"], p["split_month"]), 0) - p["amount_cents"]
        if m["split"] and m["month"] < until:
            for s in m["split"]["shares"]:
                left[(s["login"], m["month"])] = left.get((s["login"], m["month"]), 0) + s["amount_cents"]
    return left


def pool_cents(months, month):
    m = next(x for x in months if x["month"] == month)
    return m["closing_cents"] - sum(v for v in owed(months, month).values() if v > 0)


def problems(months):
    out, validator, prev = [], Draft202012Validator(SCHEMA, format_checker=FormatChecker()), None
    for m in months:
        out += [f"{m.get('month')}: {e.message}" for e in validator.iter_errors(m)]
        if out:
            continue
        if m["opening_cents"] + _sum(m["entries"]) - _sum(m["infra"]) - _sum(m["payouts"]) != m["closing_cents"]:
            out.append(f"{m['month']}: the balance does not close to the cent")
        if prev and m["opening_cents"] != prev["closing_cents"]:
            out.append(f"{m['month']}: opens with {m['opening_cents']}, the previous month closed with {prev['closing_cents']}")
        if m["split"] and _sum(m["split"]["shares"]) + m["split"]["kept_cents"] != m["split"]["pool_cents"]:
            out.append(f"{m['month']}: shares plus kept cents differ from the pool")
        prev = m
    if not out and months:
        left = {}
        for m in months:
            for p in m["payouts"] + m["returned"]:
                k = (p["login"], p["split_month"])
                left[k] = left.get(k, 0) - p["amount_cents"]
                if left[k] < 0:
                    out.append(f"{m['month']}: {p['login']} paid or returned more than owed for {p['split_month']}")
            if m["split"]:
                for s in m["split"]["shares"]:
                    left[(s["login"], m["month"])] = left.get((s["login"], m["month"]), 0) + s["amount_cents"]
    return out
```

  Nota para o implementador: na conferência de "mais do que o devido", a divisão de um mês só cria dívida depois de os pagamentos do
  mesmo mês serem lidos, porque os pagamentos de uma divisão saem no mês seguinte; o controle do passo 3 pega um pagamento de 10.001
  centavos contra 10.000 devidos.

- [ ] **Passo 6:** rodar `uv run --locked python -m unittest pipelines.tests.test_support_ledger -v`; esperado: 5 testes passam. O
  controle do pagamento acima do devido tem um mês de janeiro que fecha ao centavo, para que só a conferência da dívida possa falhar.
- [ ] **Passo 7:** `uv run --locked python -m unittest discover -s pipelines/tests` (o `test_layout` acha `pipelines/support/`); commit
  `feat(support): the public support ledger, its schema and the to-the-cent check (spec apoie 11.3, D230)`; pull request.

---

### Tarefa 4: a divisão do mês

**Arquivos:** criar `pipelines/support/split_month.py`, `pipelines/tests/test_split_month.py`,
`pipelines/tests/fixtures/split/issues-2026-12.json`.

- [ ] **Passo 1: o caso gravado** `pipelines/tests/fixtures/split/issues-2026-12.json`, na forma que `normalize()` devolve (horas em UTC;
  dezembro na hora de Brasília vai de 2026-12-01T03:00:00Z a 2027-01-01T03:00:00Z):

```json
[
 {"number": 12, "closedAt": "2026-12-05T15:00:00Z", "stateReason": "COMPLETED", "closerMerged": true,
  "labels": ["difficulty:high", "area:data"], "assignees": ["pessoa-a"],
  "labeled": [{"label": "difficulty:high", "at": "2026-12-01T10:00:00Z"}], "assigned": [{"login": "pessoa-a", "at": "2026-12-01T11:00:00Z"}]},
 {"number": 15, "closedAt": "2026-12-20T15:00:00Z", "stateReason": "COMPLETED", "closerMerged": true,
  "labels": ["difficulty:medium"], "assignees": ["pessoa-a"],
  "labeled": [{"label": "difficulty:medium", "at": "2026-12-02T10:00:00Z"}], "assigned": [{"login": "pessoa-a", "at": "2026-12-03T10:00:00Z"}]},
 {"number": 18, "closedAt": "2026-12-31T23:30:00Z", "stateReason": "COMPLETED", "closerMerged": true,
  "labels": ["difficulty:low"], "assignees": ["pessoa-b"],
  "labeled": [{"label": "difficulty:low", "at": "2026-12-04T10:00:00Z"}], "assigned": [{"login": "pessoa-b", "at": "2026-12-04T12:00:00Z"}]},
 {"number": 20, "closedAt": "2026-12-10T15:00:00Z", "stateReason": "COMPLETED", "closerMerged": true,
  "labels": ["area:docs"], "assignees": ["pessoa-b"], "labeled": [], "assigned": [{"login": "pessoa-b", "at": "2026-12-05T10:00:00Z"}]},
 {"number": 21, "closedAt": "2026-12-11T15:00:00Z", "stateReason": "COMPLETED", "closerMerged": true,
  "labels": ["difficulty:high"], "assignees": ["pessoa-b"],
  "labeled": [{"label": "difficulty:high", "at": "2026-12-09T10:00:00Z"}], "assigned": [{"login": "pessoa-b", "at": "2026-12-06T10:00:00Z"}]},
 {"number": 22, "closedAt": "2026-12-12T15:00:00Z", "stateReason": "COMPLETED", "closerMerged": false,
  "labels": ["difficulty:low"], "assignees": ["pessoa-b"],
  "labeled": [{"label": "difficulty:low", "at": "2026-12-01T10:00:00Z"}], "assigned": [{"login": "pessoa-b", "at": "2026-12-02T10:00:00Z"}]},
 {"number": 23, "closedAt": "2027-01-01T04:00:00Z", "stateReason": "COMPLETED", "closerMerged": true,
  "labels": ["difficulty:low"], "assignees": ["pessoa-b"],
  "labeled": [{"label": "difficulty:low", "at": "2026-12-01T10:00:00Z"}], "assigned": [{"login": "pessoa-b", "at": "2026-12-02T10:00:00Z"}]}
]
```

  Esperado em dezembro com 50.000 centavos: contam #12 (3), #15 (2) e #18 (1, fechada às 20h30 do dia 31 em Brasília); ficam de fora
  #20 (sem rótulo), #21 (rótulo depois da atribuição), #22 (fechada sem pull request unido) e #23 (janeiro em Brasília). Pontos: pessoa-a
  5, pessoa-b 1. Partes: 41.666 e 8.333; centavos guardados: 1.

- [ ] **Passo 2: o teste primeiro** `pipelines/tests/test_split_month.py`:

```python
"""The monthly split (spec apoie 11.2): only issues closed in the month (Brasília time) by a merged pull request, with one difficulty
label put before the assignment and one assignee, count; shares in whole cents, rounded down, the rest kept. Controls: an unlabeled
issue, a label put after the assignment and an issue closed without a merged pull request, each counted, must change the result; one
cent more in a share must fail the sum."""
import copy
import json
import unittest
from pathlib import Path

from pipelines.support import split_month as sm

CASE = json.loads((Path(__file__).parent / "fixtures" / "split" / "issues-2026-12.json").read_text(encoding="utf-8"))


class SplitTest(unittest.TestCase):
    def test_december(self):
        r = sm.compute(CASE, "2026-12", 50000)
        self.assertEqual([(s["login"], s["points"], s["amount_cents"]) for s in r["shares"]], [("pessoa-a", 5, 41666), ("pessoa-b", 1, 8333)])
        self.assertEqual(r["kept_cents"], 1)
        self.assertEqual(sum(s["amount_cents"] for s in r["shares"]) + r["kept_cents"], r["pool_cents"])
        self.assertEqual(sorted(x["number"] for x in r["skipped"]), [20, 21, 22])   # #23 is January's, not skipped here

    def test_nothing_to_split(self):
        r = sm.compute(CASE, "2026-12", 0)
        self.assertEqual(sum(s["amount_cents"] for s in r["shares"]), 0)
        r = sm.compute([], "2026-12", 50000)
        self.assertEqual((r["shares"], r["kept_cents"]), ([], 50000))

    def test_controls_each_rule_bites(self):
        base = sm.compute(CASE, "2026-12", 50000)["shares"]
        for number, change in ((20, {"labels": ["difficulty:low"], "labeled": [{"label": "difficulty:low", "at": "2026-12-01T00:00:00Z"}]}),
                               (21, {"labeled": [{"label": "difficulty:high", "at": "2026-12-05T10:00:00Z"}]}),
                               (22, {"closerMerged": True})):
            case = copy.deepcopy(CASE)
            next(i for i in case if i["number"] == number).update(change)
            self.assertNotEqual(sm.compute(case, "2026-12", 50000)["shares"], base, number)

    def test_control_one_cent_more_fails_the_sum(self):
        r = sm.compute(CASE, "2026-12", 50000)
        r["shares"][0]["amount_cents"] += 1
        self.assertNotEqual(sum(s["amount_cents"] for s in r["shares"]) + r["kept_cents"], r["pool_cents"])

    def test_normalize_reads_the_graphql_shape(self):
        node = {"number": 7, "closedAt": "2026-12-05T15:00:00Z", "stateReason": "COMPLETED",
                "labels": {"nodes": [{"name": "difficulty:low"}]}, "assignees": {"nodes": [{"login": "pessoa-a"}]},
                "timelineItems": {"nodes": [
                    {"__typename": "LabeledEvent", "createdAt": "2026-12-01T10:00:00Z", "label": {"name": "difficulty:low"}},
                    {"__typename": "AssignedEvent", "createdAt": "2026-12-01T11:00:00Z", "assignee": {"login": "pessoa-a"}},
                    {"__typename": "ClosedEvent", "createdAt": "2026-12-05T15:00:00Z", "closer": {"__typename": "PullRequest", "merged": True}}]}}
        i = sm.normalize(node)
        self.assertEqual((i["labels"], i["assignees"], i["closerMerged"]), (["difficulty:low"], ["pessoa-a"], True))
        self.assertEqual(sm.compute([i], "2026-12", 300)["shares"][0]["amount_cents"], 300)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Passo 3:** rodar; esperado: falha de importação.
- [ ] **Passo 4: `pipelines/support/split_month.py`:**

```python
"""The monthly split of the support (spec apoie 11.2): who closed weighted issues in a month and their share of what is left after
the infrastructure. Pure: compute(issues, month, pool_cents) takes issues in normalize()'s shape. fetch() reads closed issues from
GitHub through `gh api graphql` (any GitHub login works; the repository is public), so anyone can run it and reach the same cents.

Usage: python3 -m pipelines.support.split_month 2026-12 50000      (the pool in cents, from pipelines.support.ledger.pool_cents)
"""
import json
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

REPO = ("Brasil-Imposto", "brasil-imposto.github.io")
WEIGHTS = {"difficulty:low": 1, "difficulty:medium": 2, "difficulty:high": 3}
TZ = ZoneInfo("America/Sao_Paulo")
QUERY = """query($owner:String!,$name:String!,$cursor:String){repository(owner:$owner,name:$name){issues(first:50,after:$cursor,
states:CLOSED,orderBy:{field:UPDATED_AT,direction:DESC}){pageInfo{hasNextPage endCursor} nodes{number closedAt updatedAt stateReason
labels(first:20){nodes{name}} assignees(first:5){nodes{login}} timelineItems(first:100,itemTypes:[LABELED_EVENT,ASSIGNED_EVENT,
CLOSED_EVENT]){nodes{__typename ... on LabeledEvent{createdAt label{name}} ... on AssignedEvent{createdAt assignee{... on User{login}}}
... on ClosedEvent{createdAt closer{__typename ... on PullRequest{merged}}}}}}}}}"""


def when(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def bounds(month):
    y, m = map(int, month.split("-"))
    return datetime(y, m, 1, tzinfo=TZ), datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=TZ)


def normalize(node):
    items = node["timelineItems"]["nodes"]
    closes = [i for i in items if i["__typename"] == "ClosedEvent"]
    closer = closes[-1]["closer"] if closes else None
    return {"number": node["number"], "closedAt": node["closedAt"], "stateReason": node["stateReason"],
            "closerMerged": bool(closer and closer.get("__typename") == "PullRequest" and closer.get("merged")),
            "labels": [n["name"] for n in node["labels"]["nodes"]],
            "assignees": [n["login"] for n in node["assignees"]["nodes"]],
            "labeled": [{"label": i["label"]["name"], "at": i["createdAt"]} for i in items if i["__typename"] == "LabeledEvent"],
            "assigned": [{"login": (i.get("assignee") or {}).get("login"), "at": i["createdAt"]} for i in items
                         if i["__typename"] == "AssignedEvent"]}


def weight(issue, start, end):
    """The issue's weight and its person, or the reason it does not count."""
    if not (start <= when(issue["closedAt"]) < end):
        return None, "closed outside the month"
    if issue["stateReason"] != "COMPLETED" or not issue["closerMerged"]:
        return None, "not closed by a merged pull request"
    marks = [label for label in issue["labels"] if label in WEIGHTS]
    if len(marks) != 1 or len(issue["assignees"]) != 1:
        return None, "needs one difficulty label and one assignee"
    who = issue["assignees"][0]
    put = [when(x["at"]) for x in issue["labeled"] if x["label"] == marks[0]]
    took = [when(x["at"]) for x in issue["assigned"] if x["login"] == who]
    if not put or not took or max(put) > max(took):
        return None, "the label came after the assignment"
    return WEIGHTS[marks[0]], who


def compute(issues, month, pool_cents):
    start, end = bounds(month)
    per, skipped = {}, []
    for issue in sorted(issues, key=lambda i: i["number"]):
        w, who = weight(issue, start, end)
        if w is None:
            if who != "closed outside the month":
                skipped.append({"number": issue["number"], "reason": who})
            continue
        per.setdefault(who, []).append({"number": issue["number"], "weight": w})
    total = sum(x["weight"] for v in per.values() for x in v)
    shares = [{"login": login, "issues": items, "points": sum(x["weight"] for x in items),
               "amount_cents": pool_cents * sum(x["weight"] for x in items) // total if total else 0}
              for login, items in sorted(per.items(), key=lambda kv: (-sum(x["weight"] for x in kv[1]), kv[0]))]
    return {"month": month, "pool_cents": pool_cents, "shares": shares,
            "kept_cents": pool_cents - sum(s["amount_cents"] for s in shares), "skipped": skipped}


def fetch(month):
    start, _ = bounds(month)
    out, cursor = [], None
    while True:
        args = ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"owner={REPO[0]}", "-F", f"name={REPO[1]}"]
        if cursor:
            args += ["-F", f"cursor={cursor}"]
        page = json.loads(subprocess.run(args, check=True, capture_output=True, text=True).stdout)["data"]["repository"]["issues"]
        out += [normalize(n) for n in page["nodes"]]
        if not page["pageInfo"]["hasNextPage"] or when(page["nodes"][-1]["updatedAt"]) < start:
            return out
        cursor = page["pageInfo"]["endCursor"]


if __name__ == "__main__":
    month, pool = sys.argv[1], int(sys.argv[2])
    print(json.dumps(compute(fetch(month), month, pool), ensure_ascii=False, indent=1))
```

- [ ] **Passo 5:** rodar `uv run --locked python -m unittest pipelines.tests.test_split_month -v`; esperado: 5 testes passam.
- [ ] **Passo 6:** rodar de verdade, só leitura: `uv run --locked python -m pipelines.support.split_month 2026-11 0`; esperado: um JSON
  com `shares` vazias ou com as issues com peso fechadas em novembro, e `skipped` listando as fechadas sem a regra. Conferir uma issue
  da lista à mão na linha do tempo do GitHub.
- [ ] **Passo 7:** `uv run --locked python -m unittest discover -s pipelines/tests`; commit
  `feat(support): the monthly split script (spec apoie 11.2, D230 and D231)`; pull request.

---

### Tarefa 5: a página do livro-caixa, atrás da chave `livro-caixa`

**Arquivos:** `data/features.json`, `docs/superpowers/tools/site_chrome.py`, criar `docs/superpowers/tools/build-ledger-page.py` e
`docs/superpowers/previews/livro-caixa.html` (gerada), `docs/superpowers/tools/build-site.py`, `docs/superpowers/tools/check-all.py`,
`.github/workflows/ci.yml`, `.github/workflows/pages.yml`, `deploy/staging/deploy.yml` e o `deploy.yml` do `Brasil-Imposto/staging`
(o mesmo arquivo, depois deste merge), `pipelines/tests/test_build_site.py`, `apoie.py` (o link da linha do livro-caixa). Caminhos do
`guard`: `.github/*`, `deploy/*`, `apoie.py`.

- [ ] **Passo 1: a chave** em `data/features.json`, depois de `rede`:

```json
  {
   "key": "livro-caixa",
   "issue": 0,
   "description": "A página Livro-caixa do apoio, o link no rodapé e o link na linha do livro-caixa da janela do Apoie (spec do Apoie, seção 11.3, D234)",
   "staging": true,
   "production": false
  }
```

  O implementador abre a issue da tarefa antes do código e põe o número dela em `issue` (o esquema `schemas/features.schema.json` pede
  um inteiro; conferir se aceita 0 ou se pede o número real).

- [ ] **Passo 2: o teste primeiro**, em `pipelines/tests/test_build_site.py`:

```python
    def test_the_ledger_page_only_where_its_switch_is_on(self):
        for profile, present in (("staging", True), ("production", False)):
            with tempfile.TemporaryDirectory() as tmp:
                build_site.build(profile, tmp)
                site = Path(tmp)
                self.assertEqual((site / "livro-caixa.html").exists(), present, profile)
                foot = (site / "como-ler-o-mapa.html").read_text(encoding="utf-8")
                self.assertEqual('href="livro-caixa.html"' in foot, present, profile)
```

  e, no teste que lista os arquivos do site (linha que monta `[".nojekyll", ".well-known", "assets", "index.html", ...]`), tirar
  `livro-caixa.html` da lista da produção.

- [ ] **Passo 3:** rodar; esperado: falha (a página não existe).
- [ ] **Passo 4: `site_chrome.py`.** Acrescentar a página fora do cabeçalho e o link do rodapé com a chave:

```python
LEDGER_PAGE = "livro-caixa.html"
OTHER_PAGES = {"notas": (NOTES_PAGE, "Como ler o mapa"), "livro": (LEDGER_PAGE, "Livro-caixa do apoio")}
SWITCHED_PAGES = {"livro": "livro-caixa"}   # pages built only where their switch is on (build-site.py)
```

  Em `footer(rede=True, ledger=False)`, depois de `(NOTES_PAGE, "Como ler o mapa", "")`, o par
  `(LEDGER_PAGE, "Livro-caixa do apoio", "")` só quando `ledger`; em `parts()`, `ledger = features.on("livro-caixa", profile)` passado
  aos dois `footer(...)`.

- [ ] **Passo 5: `build-site.py`.** No laço das páginas, pular a página cuja chave está desligada:

```python
    for key, (name, _label) in site_chrome.ALL_PAGES.items():
        if key in site_chrome.SWITCHED_PAGES and not features.on(site_chrome.SWITCHED_PAGES[key], profile):
            continue
```

  e `"build-ledger-page.py"` no fim de `BUILDERS`.

- [ ] **Passo 6: `build-ledger-page.py`**, no molde de `build-notes-page.py` (mesmo `<head>`, marcadores do `site_chrome`, CSS do desenho
  aprovado `private/apoie/build_apoie_r4.py`, constante `CSS`, as regras `.r4-led-*`, renomeadas `.led-*`): lê
  `pipelines.support.ledger.load_all()`, escreve `docs/superpowers/previews/livro-caixa.html` com:
  - o título "Livro-caixa do apoio" e o texto de abertura da rodada `apoie-r4` (com o link para o script
    `pipelines/support/split_month.py` e para o `GOVERNANCE.md` no GitHub);
  - "Até agora": a soma de todas as entradas, da infraestrutura e dos pagamentos, e o saldo do último mês; sem nada recebido, o texto
    exato "nenhuma doação recebida, nenhum gasto de infraestrutura (o site é hospedado de graça no GitHub Pages) e nenhum pagamento.
    Saldo: R$ 0,00.";
  - um bloco por mês, do mais novo para o mais velho, com as tabelas Entradas, Infraestrutura, Divisão de quem contribuiu e Pagamentos
    e a linha "A conta fecha: ...", só com as partes que o mês tem; nenhum exemplo fictício na página real.
  - valores em `R$ 1.234,56` (a função `money` da rodada); o JSON nunca entra cru na página (cada texto por `html.escape`).

  Depois `python3 docs/superpowers/tools/site_chrome.py`-style: a página passa por `site_chrome.inject(page, "livro")` como as outras
  (ver `build-notes-page.py`, fim do arquivo).

- [ ] **Passo 7: as listas dos construtores.** A linha `python docs/superpowers/tools/build-ledger-page.py` depois de
  `build-notes-page.py` em `.github/workflows/ci.yml`, `.github/workflows/pages.yml` e `deploy/staging/deploy.yml`, e
  `"build-ledger-page.py"` no fim de `BUILDERS` de `check-all.py`. O `deploy.yml` do `Brasil-Imposto/staging` recebe a mesma linha num
  pull request de lá, unido depois deste.

- [ ] **Passo 8: o link da janela.** Em `apoie.py`, a linha "Tudo o que entra e tudo o que sai é publicado, mês a mês, no livro-caixa do
  projeto." ganha o link `<a href="livro-caixa.html">livro-caixa do projeto</a>` só quando a chave `livro-caixa` estiver ligada no
  perfil (o `modal()` recebe o perfil como já recebe `staging`); teste em `test_support.py`: o link no staging, nenhum link na produção.

- [ ] **Passo 9:** rodar `uv run --locked python docs/superpowers/tools/check-all.py`; esperado: tudo verde, e `git status` mostra a
  página nova commitável e nenhuma outra prévia mudada além das com a janela.
- [ ] **Passo 10: a tela.** Montar o staging numa pasta temporária, servir, olhar `livro-caixa.html` e a janela em 1440 e 420 px;
  `apoie-check.cjs --staging` com uma conferência nova: o link da linha do livro-caixa leva à página, e a página mostra "Saldo: R$ 0,00";
  `visible-text` nas quatro páginas.
- [ ] **Passo 11:** commit `feat(site): the support ledger page behind the livro-caixa switch (spec apoie 11.3, D234)`; pull request com a
  etiqueta do `guard` listando os caminhos; depois do merge, o pull request do `deploy.yml` no `Brasil-Imposto/staging`, o deploy do
  staging (ligar, publicar, conferir no ar `livro-caixa.html` e a janela, desligar, D214).

---

## Conferência do plano contra a spec

| Spec | Tarefa |
|---|---|
| 11.2 itens 1 a 3 e 5 a 7 (o peso, de quem é, antes, o mês, sem passado, o script público) | 4 (código) e 1 (regra escrita) |
| 11.2 item 4 (a pessoa mantenedora pela mesma regra; a segunda confirma) | 1 (regra; a confirmação vale quando houver a segunda pessoa) |
| 11.2 itens 8 a 10 (o pagamento em particular, o não reclamado, talvez nunca) | 1 (regra) e 3 (`payouts`, `returned`, a dívida nunca negativa) |
| 11.3 (o livro-caixa, a conta ao centavo, os nomes pela regra 4, a página própria) | 3 e 5 |
| 11.4 (os textos) | 2 e 5 (o link) |
| 11.5 (`GOVERNANCE.md`, `CONTRIBUTING.md`, o modelo de pull request) | 1 |
| 11.6 (as provas) | 2 a 5, cada uma com controle |
| 11.2 item 8, o portão do contador (Q39) antes do primeiro pagamento a outra pessoa | fora do código: um portão do mantenedor (D231), conferido antes de registrar o primeiro `payouts` de outra pessoa |
