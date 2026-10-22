# Auditoria de consistência e de arquivos do repositório

English summary: an audit of the whole repository on 2026-10-22, from a fresh `main` (`8d27196`), in three parts: (1) facts that
appear in more than one tracked place, each brought to the newest ruling, with tasks 6 and 7 of the cleanup plan
(`docs/superpowers/plans/BRASIL-IMPOSTO_PLAN_cleanup-phase-1_2026-10-21.md`); (2) a verdict for every tracked file (SAFE to
delete, KEEP, or ASK), with the evidence; deletions wait for the maintainer's yes, group by group; (3) the repository kept free
of anything outside this project. Written section by section as the work goes; the state of each part is in its heading.

Status: **partes 1, 2 e 3 feitas; a lista de apagar espera o sim do mantenedor.** Base: `main` em `8d27196`, 6.496 arquivos no git (1.148 de texto), 56 commits no GitHub. O pull request #43 (correções de interface) e o #44 (README e regras na página da
organização) entraram na `main` durante a auditoria; o ramo foi refeito sobre `131c8fc`, e os itens que esperavam o #43 foram
feitos depois disso.

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

**Os arquivos que o #43 e o #44 trouxeram** (vistos depois que entraram): KEEP. As três sondas novas (`overlay-check.cjs`,
`sheet-width-check.cjs`, `ui-sweep.cjs`) são a prova da spec de interface, a spec é registro, e as cinco imagens de
`docs/images/readme/` são lidas pelo `README.md`.

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

## Parte 1. Inconsistências (feita)

**Como foi feito.** Um inventário dos fatos que aparecem em mais de um lugar do git (comandos, caminhos, situação de specs e
planos, números de construtores, o que está publicado), com o espaço sem quebra (U+00A0) trocado por espaço antes de cada busca.
Vale a decisão mais nova do registro (`docs/decisions/README.md`) ou o que o código faz hoje; o texto antigo foi atualizado no
lugar, sem marca de "substituído". Não é inconsistência, e ficou como está: as linhas do registro de decisões que contam o que
valia na época, `prove-pipelines-move.py` e `test_layout.py` (citam o caminho antigo de propósito), os registros de pesquisa e
de execução que descrevem o que rodou naquele dia.

| Lugar | Antes | Agora | Fonte |
|---|---|---|---|
| 28 linhas de docstring em `pipelines/` e `docs/superpowers/tools/`, `pipelines/README.md` (linha 29), o plano de limpeza (linha 53) | `.venv/bin/python ...` | `uv run python ...` | D151 e #25 (Python com uv); `README.md` |
| 7 pesquisas em `docs/research/`, a docstring de `pipelines/bridges/build.py`, os dois planos | a pasta do projeto na máquina do autor | `$(git rev-parse --show-toplevel)/...`, ou "na raiz do repositório" | D147 (o projeto no git) |
| `docs/superpowers/tools/shot.sh` | o navegador numa pasta de cache de um Mac; a página padrão `home-simulacao` | `CHROME_HEADLESS`, como as sondas; a página padrão é a da plataforma | plano, tarefa 7 (P2-20); D149 (a home publicada) |
| Spec da fase B0 do Astro, linha de situação | "proposta, aguardando a aprovação" | aprovada (D151) e em execução; feitos #23, #25, #26, #32 e #33, #34, #35; falta a sonda de paridade no `ci` e as chaves de `data/` | D151; histórico de pull requests |
| Spec de cabeçalho, rodapé e carregamento | "o carregamento falta" | carregamento feito (#31) | D152; #31 |
| Plano de limpeza, situação e "Para quem executa" | "execução nesta sessão"; "Sem git (D54)" | tarefas 0 a 5 feitas; 6 a 8 nesta auditoria, por pull request; anexos fora do git | D147; esta auditoria |
| Registro de decisões, Fase, "Estado em 2026-10-22" e "Se a sessão cair" | "brainstorming com prévias (D3)"; próximo passo já feito | v1 publicada (D149); feitos desde então: logo e prévia social (#37, #42), cabeçalho, rodapé e carregamento (#27, #28, #31), Judiciário (#40, #41); próximo: Q78, o resto da B0, tarefas 6 a 8 e a fase 2 do livro | D149, D152, D153, D154 |
| `CONTRIBUTING.md` | "os quatro construtores"; "deputados estaduais ainda não estão no projeto" | a versão do #44, mais nova, levou essas regras para a página da organização; o arquivo fica como a `main` o deixou | #44 |
| `docs/ai/learned-patterns.md` | ponteiro para um arquivo de decisões fora do git; regras da máquina do autor | `docs/decisions/README.md`; regras gerais, sem caminho de máquina | D147; plano, tarefa 7 (E2) |
| Comentários e docstrings de 46 scripts (193 trechos) | em português | em inglês; nomes oficiais e campos de fonte como estão | regra do projeto (`.claude/CLAUDE.md`); plano, tarefa 6 |
| Chaves de 19 arquivos de `data/` e dos seus escritores e leitores (lista no plano, registro da tarefa 6) | em português (`pessoal`, `by_natureza`, `numero`, `posse`, `pessoal_e_encargos`, `deputado_estadual`...) | em inglês, cada arquivo igual ao antigo com o mapa aplicado | regra do projeto; plano, tarefa 6 |
| Códigos de `governors_curated/*.json`, `governors.json` e `union.json` | `eleito`, `interino`, `vago`, `governador`, `oficial`... | `elected`, `acting`, `vacant`, `governor`, `official`...; a tela mostra os mesmos rótulos | plano, tarefa 6 |
| Garantias do livro de fluxos | identificadas pela frase em português | id em inglês (`g1_unique_ids`...) com a frase como rótulo | plano, tarefa 6 |
| `pipelines/ledger/registry.py` | uma fonte que volta a um arquivo antigo não volta a valer | a divulgação antiga volta a ser a atual (teste A, B, A) | plano, tarefa 7 (P2-14) |
| `pipelines/build.py` | entrada faltando virava `None`; gravava direto no arquivo publicado | para e diz o script que escreve a entrada; grava num temporário | plano, tarefa 7 (P1-12) |
| `data/municipal-taxes-2024.json` | nada dizia que faltam municípios | `complete: false` em 11 estados | plano, tarefa 7 (P1-24) |
| `build-cases.py`, fotos de signatário | por parte do nome | só por nome exato, com tabela de apelidos | plano, tarefa 7 (P2-8) |
| 124 `assert` em 42 arquivos | somem com `python -O` | `raise SystemExit` | plano, tarefa 7 (P2-20) |

**Provas.** 41 testes de `pipelines/tests` e 30 do livro passam; os cinco construtores que o `ci` confere refazem as páginas, e
só mudam o que as chaves pedem: o tamanho do pacote no carregamento da home, os dois leitores de Os 3 Poderes e o de
`serieslayer.js`; o pacote `bi-data.js` difere do da `main` só na série da folha federal, igual a ela com o mapa aplicado; a
exportação das entidades valida contra os esquemas. Cada teste novo
falhou no código antigo; o teste de chaves pega o controle `nome_controle` e o arquivo antigo do SC-401. Texto visível e
verificação do site: na descrição do pull request.

## Para o mantenedor

- **O registro de decisões é gerado.** `docs/decisions/README.md` sai de `private/decisions-original.md` (fora do git) por
  `publish-decisions.py`; as três linhas mudadas aqui (Fase, Estado em 2026-10-22, Se a sessão cair) precisam ir para o
  original, ou a próxima publicação as desfaz.
- **SC-401 "líquido" e Linha 17 `provenance`** (tarefa 7): dependem do texto do anexo P2-19, fora do git. O total calculado
  (`total_paid_ct_00014_2025_brl_computed`, R$ 40.728.766,00) é o pago líquido; a tela usa o pago com os retidos
  (R$ 41.694.715,23, `complete-totals`). Falta a frase do anexo para o rótulo.
- **Escritores que não rodaram aqui:** os das chaves trocadas baixam as entradas de sites que a rede desta sessão não alcança;
  a troca foi provada pelos dados (mapa aplicado) e pelo código. Uma rodada completa de cada um confirma.
- **`pages.yml`** usa `actions/setup-python@v5` pela etiqueta, enquanto o `ci.yml` fixa por commit. Mexer em workflow é decisão
  sua.
- **Perguntas sem decisão mais nova:** Q56 a Q58 e Q69 a Q71 continuam abertas; nada no git as responde.

## Não conferido

- `shot.sh` não rodou: pede `zsh`, que esta máquina não tem; a mudança é só o navegador e a página padrão.
- Os escritores citados acima (entradas fora de alcance).
- O site publicado: esta sessão não alcança `brasil-imposto.github.io`; as páginas foram conferidas servidas localmente.
