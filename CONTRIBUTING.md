# Como contribuir

Obrigado por ajudar. As regras para contribuir com o Brasil-Imposto estão na página da organização:
**<https://github.com/Brasil-Imposto>**. Lá estão o caminho de uma contribuição, como virar colaborador, como preparar um pull
request, o que todo pull request leva (título, descrição, issue, capturas de tela, fontes e conferências) e como funcionam a
revisão e o merge.

Para começar agora:

- **Antes de tudo:** veja se a tarefa já tem dono, uma issue, um pull request ou um ramo abertos sobre ela. Se tiver, comente lá
  em vez de começar outra.
- **Um número errado:** o formulário [Pedir correção](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/new?template=data-correction.yml),
  com o link da fonte oficial com o valor certo.
- **Qualquer outra ideia:** um dos [formulários de issue](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/new/choose)
  ou [Discussions](https://github.com/Brasil-Imposto/brasil-imposto.github.io/discussions).
- **Um pull request:** sempre para o ramo `staging`, nunca para a `main`. A mudança é conferida no site de testes,
  <https://brasil-imposto.github.io/staging/>, e só depois vai à produção. O formulário do pull request já traz as seções que ele
  precisa ter.

O Brasil-Imposto só mostra dado oficial: toda contribuição traz a fonte.

## Para desenvolver

### O que instalar

- **Python 3.12 com o [uv](https://docs.astral.sh/uv/)** (o `ci` usa o uv 0.11.32). O uv instala o Python certo e as versões
  fixadas em `uv.lock`.
- **Node 24** (`.nvmrc`), para o site em Astro de `site/` e para as sondas.
- **git**.
- Só para as sondas (opcional): o `playwright-core` e um Chromium sem tela (veja "As sondas", abaixo).

### Preparar e conferir

Num clone novo, um comando faz tudo o que o `ci` faz, na mesma ordem, e diz o tempo de cada passo:

```bash
uv sync --locked
uv run --locked python docs/superpowers/tools/check-all.py
```

São 20 passos: o `uv.lock`, os testes de `pipelines/tests`, os arquivos de entidade conferidos com os esquemas de `schemas/`, o
site em Astro (`npm ci`, tipos, `astro check` e `tsc`, Vitest, build), os testes do livro de fluxos, os seis construtores das
páginas, a conferência de que as páginas versionadas são o que os construtores fazem, o carregador do mapa e o site montado nos
dois perfis, produção e staging. Num clone limpo, levou cerca de um minuto e meio (os testes de `pipelines/tests` são a maior
parte). O comando para no primeiro passo vermelho e sai com 1: é o passo que ficaria vermelho no `ci`.

Um passo de cada vez:

```bash
uv run --locked python -m unittest discover -s pipelines/tests        # testes (inclui o saldo do DF e dos 27 estados)
uv run --locked python docs/superpowers/tools/build-site.py --profile production --out _site   # o site como a produção
uv run --locked python docs/superpowers/tools/build-site.py --profile staging --out _site      # o site como o staging
```

### Como um dado vira página

1. `pipelines/` baixa as fontes oficiais, confere e grava `data/` (um script por base; cada um com a checagem ao centavo e um
   `--control` que tem de falhar).
2. Os construtores de `docs/superpowers/tools/` (`build-cases.py`, `build-standalone-data.py`, `build-simulation.py`,
   `build-platform-preview.py`, `build-site-chrome.py`, `build-notes-page.py`) leem `data/` e escrevem as páginas versionadas de
   `docs/superpowers/previews/` e os pacotes de `docs/superpowers/previews/assets/` (o `bi-data.js` é gerado e fica fora do git).
3. `docs/superpowers/tools/build-site.py` monta o site publicado, no perfil de produção ou de staging (as chaves de
   `data/features.json`).

Mudou um dado ou um construtor: rode os construtores na ordem acima e faça commit das páginas junto. O `ci` refaz e compara.

### As sondas

As sondas abrem as páginas num Chromium sem tela, como um visitante:

| Sonda | O que confere |
|---|---|
| `docs/superpowers/tools/site-check.cjs` | cada página responde sem erro, sem rolagem lateral, em 1440 e 420 px |
| `docs/superpowers/tools/visible-text-probe.cjs` | o texto visível da Início em 100 combinações de período e estado, para provar que uma mudança não mexeu na tela |
| `docs/superpowers/tools/apoie-check.cjs` | o botão Apoie e o formulário de contato (o envio é interceptado: nenhuma mensagem sai) |

Cada uma tem `--control`, que planta uma falha e tem de falhar. Variáveis: `PW_CORE` (a pasta do `playwright-core`),
`CHROME_HEADLESS` (o binário do Chromium sem tela), `CDN_MIRROR` (pacotes do npm servidos no lugar do cdn.jsdelivr.net, quando a
rede bloqueia), `VT_WIDTH` e `VT_STATES` (largura e estados da sonda de texto), `SC_WIDTHS` (larguras do `site-check.cjs`).
Para obter os dois primeiros:

```bash
npm install --prefix ~/.cache/brasil-imposto-probes playwright-core
node ~/.cache/brasil-imposto-probes/node_modules/playwright-core/cli.js install chromium-headless-shell
export PW_CORE=~/.cache/brasil-imposto-probes/node_modules/playwright-core
export CHROME_HEADLESS=<o caminho do chrome-headless-shell que o comando acima baixou>
```

### Erros comuns

- **"the committed pages are what their builders make" vermelho:** uma página versionada ficou diferente do que o construtor faz.
  Rode os seis construtores na ordem e faça commit das páginas.
- **`dco` vermelho:** todo commit precisa de `Signed-off-by` com o e-mail do autor do commit. Use `git commit -s`; para corrigir o
  último, `git commit --amend -s --no-edit`.
- **`uv lock --check` vermelho:** `pyproject.toml` mudou sem o `uv.lock`. Rode `uv lock` e faça commit dos dois.
- **O `data-size` da Início muda sozinho:** `build-platform-preview.py` rodou sem o `bi-data.js`. Rode `build-standalone-data.py`
  antes dele.
- **Um teste do saldo pede o `node`:** os testes do saldo rodam o próprio código do mapa no Node.

### Revisão

O pull request vai para o `staging`, com `ci` e `dco` verdes (a regra do ramo exige os dois). Quem revisa hoje é o mantenedor
(`.github/CODEOWNERS`); o merge é por squash. A produção recebe uma tarefa aprovada por vez (D166).
A verificação `visible-text` compara o texto das quatro páginas com o da base em todo pull request que mexe no que as monta;
um pull request que muda o texto da tela só entra com o rótulo `muda-a-tela`, que o mantenedor põe quando a mudança é querida (D194).
No fim de um dia com produção sai a versão do dia (D190): `docs/superpowers/tools/release-notes.py --next-version` dá o número
(`v1.N.0`), `--date AAAA-MM-DD` dá as notas, uma linha por pull request que entrou na `main` naquele dia, e `--changelog` refaz o
`CHANGELOG.md`, que vai ao `staging` por pull request e à produção com a próxima tarefa.

### In English

To develop: install Python 3.12 with uv and Node 24, then run `uv sync --locked` and
`uv run --locked python docs/superpowers/tools/check-all.py`, which runs every check of the ci in the same order (about a minute
and a half on a clean clone) and stops at the first failure. Data flows from `pipelines/` to `data/`, the builders in
`docs/superpowers/tools/` write the committed pages, and `build-site.py` assembles the site in its production or staging profile.
Pull requests go to `staging` with `ci` and `dco` green (`git commit -s`).
