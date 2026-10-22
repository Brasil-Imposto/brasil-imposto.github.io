# Auditoria de consistência e de arquivos do repositório

English summary: an audit of the whole repository on 2026-10-22, from a fresh `main` (`8d27196`), in three parts: (1) facts that
appear in more than one tracked place, each brought to the newest ruling, with tasks 6 and 7 of the cleanup plan
(`docs/superpowers/plans/BRASIL-IMPOSTO_PLAN_cleanup-phase-1_2026-10-21.md`); (2) a verdict for every tracked file (SAFE to
delete, KEEP, or ASK), with the evidence; deletions wait for the maintainer's yes, group by group; (3) the repository kept free
of anything outside this project. Written section by section as the work goes; the state of each part is in its heading.

Status: **em andamento.** Base: `main` em `8d27196`, 6.496 arquivos no git (1.148 de texto), 56 commits no GitHub. Arquivos que o
pull request #43 (correções de interface, aberto) muda ficam fora desta auditoria até ele ser resolvido: `.claude/CLAUDE.md`,
`docs/superpowers/tools/site_chrome.py`, as cinco páginas de `docs/superpowers/previews/*.html`, `assets/home-feed.css`,
`assets/home-feed.js`, `assets/modals.js` e os quatro arquivos novos dele.

## Parte 3. Só Brasil-Imposto (feita)

- A lista de nomes de fora do mantenedor e os caminhos da máquina de uma pessoa: **0 ocorrências** em 1.148 arquivos de texto do git e
  em 0 das mensagens dos 56 commits do GitHub (busca sem diferenciar maiúsculas, 2026-10-22).
- Controle: um clone com uma linha plantada (um caminho de máquina) no `README.md` dá 1 arquivo e 1 ocorrência; a busca enxerga.
- "Vitor" (servidores públicos, uma cidade) e o usuário do GitHub em `.github/CODEOWNERS` e `GOVERNANCE.md` ficam como estão, por
  decisão do mantenedor.
- A mesma busca roda nas mudanças de cada pull request desta auditoria antes de abri-lo.

## Parte 2. Arquivos (veredito feito; nada apagado, a lista espera o sim do mantenedor)

**Como foi feito.**
- **Mapa de leitores.** Para cada arquivo fora das categorias que nunca saem, a busca do nome no texto de todos os arquivos do
  git, separando código (`.py`, `.js`, `.cjs`, `.html`, `.yml`, `.sh`, `.json`, `.css`, `.toml`, `.ts`, `.astro`) de documentos.
  Um módulo Python conta também pelo nome importado. São 379 candidatos, e 127 sem nenhum leitor em código pelo nome.
- **Leitura por padrão, conferida à mão.** Esses 127 foram conferidos um por um, porque um construtor pode ler por padrão e não
  pelo nome. Exemplos:
  - `build-standalone-data.py:25` lê `assets/icons/*.svg` por `glob`;
  - `:29` lê `assets/flags/{flag}.svg` pela lista de países;
  - `:288` lê `geo-{uf}.json`;
  - `build-cases.py:254` lê `assets/cases/*/credits.json`;
  - `build_governors.py:22` lê a pasta `governors_curated/`;
  - os testes entram pelo `unittest discover` do CI.
- **O que as páginas carregam.** Lido nas três páginas publicadas e em tudo o que elas carregam (`src`, `href`, `data-src`,
  `import`, `fetch`). As fotos das obras foram conferidas contra o `assets/cases.json` gerado.

**Nunca saem** (regra do pedido): as três páginas e o que carregam, o que qualquer construtor, pipeline, teste, workflow ou o site
em Astro lê, `data/`, `schemas/`, o registro de decisões, os documentos da raiz e de `.github/`, `.claude/CLAUDE.md`, as pesquisas e
as specs.

### KEEP, por grupo

| Grupo | Quantos | Quem precisa |
|---|---:|---|
| Ícones `assets/icons/*.svg` | 41 | `build-standalone-data.py:25` (glob), embutidos em `bi-data.js` |
| Bandeiras `assets/flags/*.svg` | 30 + créditos | `build-standalone-data.py:29` (29 países do comércio) e `flags/br.svg` direto na página |
| Fotos e créditos das obras publicadas | 19 fotos + 8 créditos | `build-cases.py` grava o caminho em `cases.json`, que a página abre |
| Geometrias e malhas (`map-geo.json`, `geo-*.json`, `countries-50m.json`, `ibge-*`) | 7 | `build-geo*.cjs`, `build-standalone-data.py`, `pipelines/df/build_regions.py` |
| `assets/hero3d.js`, `assets/modals.js` | 2 | `build-simulation.py` empacota os dois na página |
| `brand/og-image.png` | 1 | as `meta og:image` das três páginas (`site_chrome.py`) |
| Construtores e coletores de `docs/superpowers/tools/` (27 menos o da rodada 1, grupo A) e `tools/vendor/` (3, lidos por `build-geo.cjs`) | 26 + 3 | cada um grava um arquivo que a página carrega ou que outro construtor lê (por exemplo, `build-tres-poderes-r2-data.py` grava `data/federal/positions-2026.json`, lido por `build-tres-poderes-r3-data.py:36`) |
| Sondas e checagens (`*-check.cjs`, `*-probe.cjs`, `action-probe.html`, `shot.sh`) | 9 | `CLAUDE.md`, o CI, `shot.sh` abre `action-probe.html`; a tarefa 7 do plano cita `shot.sh` |
| `rename-json-keys.py`, `english-keys-map.json` | 2 | a tarefa 6 do plano (as chaves em inglês) |
| `publish-decisions.py` | 1 | escreve `docs/decisions/README.md` a partir do original local (tarefa 8 do plano) |
| `prove-pipelines-move.py`, `pipelines/tests/test_layout.py` | 2 | a prova da mudança para `pipelines/` (#23); nomeiam o caminho antigo de propósito |
| Scripts de `pipelines/` (`.py`, `.sh`, fora os testes), mais `governors_curated/*.json` (22), `ledger/schema.sql` e os dois `README.md` | 130 + 25 | gravam um arquivo de `data/` ou refazem os números de uma pesquisa de `docs/research/` que os cita (por exemplo, `pipelines/df/*.py` em `RESEARCH_df-gasto-publico`, `pipelines/trade/*.py` em `RESEARCH_exports-by-product`) |
| Testes (`pipelines/tests/`, `pipelines/ledger/tests/`) | 11 | o CI (`unittest discover`) |
| Configuração e o site em Astro (`.gitignore`, `.python-version`, `pyproject.toml`, `uv.lock`, os 9 arquivos de `site/`) | 13 | git, uv, npm, Astro |
| `docs/ai/learned-patterns.md` | 1 | `CLAUDE.md` aponta para ele |
| O plano da limpeza, fase 1 | 1 | aberto: tarefas 6 a 8 |

### SAFE (a lista de apagar, por grupo; espera o sim)

**Grupo A. Os 3 Poderes, rodada 1.**
- `docs/superpowers/tools/build-tres-poderes-data.py` e `docs/superpowers/previews/assets/tres-poderes-data.js`.
- Prova:
  - nenhuma página carrega `tres-poderes-data.js` (busca em todos os arquivos do git: só o próprio construtor o nomeia);
  - o construtor publicado, `build-tres-poderes-r3-data.py`, não importa nem lê nada da rodada 1 (as entradas dele estão listadas
    na docstring, linhas 4 a 21, e nenhuma é da rodada 1);
  - o que a rodada 1 decidiu está em D142 e D143 (a rodada 3 publicada).

**Grupo B. Os 3 Poderes, a cópia de dados da rodada 2.**
- `docs/superpowers/previews/assets/tres-poderes-r2-data.js`.
- Prova:
  - nenhuma página o carrega;
  - o conteúdo é igual, objeto por objeto, a `data/federal/positions-2026.json` (comparação feita em 2026-10-22: `True`).
- O construtor da rodada 2 **fica**, porque grava `positions-2026.json`. No mesmo commit, ele deixa de gravar a cópia `.js`
  (linhas 17, 25 e 262).

### ASK (o mantenedor decide)

1. **Planos executados por inteiro.** `docs/superpowers/plans/BRASIL-IMPOSTO_PLAN_money-flow-ledger-phase-1_2026-10-08.md`: o
   status diz "executado em 2026-10-08 e emendado em 2026-10-09 (D127)", mas as 48 caixas seguem desmarcadas. É um registro;
   apagar ou guardar?
2. **Fotos de casos ainda não publicados.** `assets/cases/alcantara/` (2 fotos e os créditos) e
   `assets/cases/ufsc-cfm-admin-building/` (1 foto e os créditos). Nenhuma está no `cases.json` publicado. O plano da limpeza deixa
   os dois casos como trabalho pendente (itens 6 e 7 da V1, D139).
3. **Ferramentas de conferência manual que nada chama:** `band-wrapper.html`, `hover-probe.html`, `flag-grid.html` e
   `render-doc.py`. Estão na lista de ferramentas do `README.md` e não são lidas por nenhum código. São das rodadas de desenho;
   ficam ou saem?
4. **Os coletores do Diário Oficial da ponte Hercílio Luz:** `pipelines/hercilio_luz/apesc_doe.py`, `doe_walk.py` e
   `dotc_scan.sh`. Nenhum código os chama e nenhum documento os cita pelo nome. Baixam as edições do DOE-SC e do DOTC-e cujos
   trechos a pesquisa `RESEARCH_ponte-hercilio-luz-responsaveis_2026-09-29.md` cita (linhas 102 a 115). São o método da coleta e
   não gravam nada no git. Recomendo guardar, porque mostram como a evidência foi obtida.

Os outros scripts de `pipelines/` sem leitor nem documento gravam arquivos que estão no git: `pipelines/ug/extract_fat_uf_hybrid.py`,
`pipelines/ug/extract_rtn_lines.py` e `pipelines/works/media_fetch.py`. Por isso ficam (KEEP).

## Parte 1. Inconsistências (em andamento)

## Não conferido
