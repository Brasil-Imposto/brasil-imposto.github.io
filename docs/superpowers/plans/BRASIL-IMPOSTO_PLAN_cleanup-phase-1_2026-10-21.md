# Auditoria de limpeza, fase 1: plano de implementação

English summary: implementation plan for phase 1 of the cleanup audit (D137), approved by the author on 2026-10-21 (D139, Q42).
Phase 1 changes nothing a visitor sees. It sets up one Python environment, moves dead and orphan files to `private/archive/`,
takes the author's quotes out of code comments, removes the superseded 2024 balance and the dead page branches, makes every
check able to fail (each with a control that does fail), stops the ledger control from ever publishing, and renames the
Portuguese JSON keys. Two instruments prove "no visible change": the visible text of the page in 100 states and periods,
identical before and after, and the page's generated files rebuilt from source.

Situação: **plano escrito em 2026-10-21; execução nesta sessão, tarefa por tarefa, cada uma anunciada ao autor.**

### Para quem executa
Executar na ordem, marcando as caixas. Sem git (D54): no lugar do commit, cada tarefa termina com as provas e com uma linha no
registro (seção "Registro da execução" no fim). Execução pelo mesmo agente, sem subagentes. O código de cada passo é escrito
contra o arquivo lido na hora; cada achado está descrito, com arquivo e linha, nos anexos da auditoria
(`docs/research/audit/BRASIL-IMPOSTO_AUDIT_cleanup-*_2026-10-14.md`). Todo comando roda em `~/Documents/Brasil-Imposto`.
Cópia do projeto de antes da fase 1: `private/snapshots/brasil-imposto-before-cleanup-phase-1_2026-10-21.tar.gz`.

### Objetivo
O caminho até a página fica limpo e reproduzível sem mudar nada na tela: um ambiente, nada morto ao lado do que vive,
checagens que podem falhar, chaves em inglês.

### Fora desta fase (com o motivo)
- Mudanças na tela: fase 3 (decisões já registradas) e fase 4 (decisões de D139).
- Mudança de pastas, nomes de arquivo em português (R-11), um construtor só, manifesto dos brutos, `sources.toml` com as
  versões das fontes (P1-16), um pacote de utilidades comuns (P2-17) e o caminho do mapa (P2-18): fase 2, porque mexem na
  estrutura. P1-16 estava na fase 1 (achado B8); vai para a fase 2 junto com o manifesto dos brutos (B4), que lê o mesmo
  registro de fontes.
- Notas ao autor e a marca "Só na prévia" na página (F-12, primeira parte): saem quando houver a versão pública e a de
  revisão, com o construtor único da fase 2. Nesta fase saem só as citações dos comentários.
- Ficam onde estão, como trabalho pendente: `data/works/alcantara.json` (item 6 da V1), `data/scripts/works/build_ufsc_cfm_admin.py`
  (item 7 da V1), `data/cases/inss-deductions.json` e `data/cases/pre-salt-onerous-assignment.json` (casos futuros: o autor
  quer a lista de escândalos crescendo, D139).
- Os scripts de pesquisa avulsa de `data/df/` (P1-19) e os relatórios de 2024 da raiz (P1-22): reproduzem pesquisas publicadas,
  então vão para `docs/research/` na fase 2, com os caminhos de leitura e escrita corrigidos, e não para o arquivo privado.
- O CSS dos desenhos reprovados em `proposals.css` (parte de F-8): sai na fase 2, com a separação dos estilos, provado por estilo
  computado; o texto visível não enxerga CSS.

### Instrumentos de prova (feitos antes de qualquer mudança)
1. **Texto visível:** `docs/superpowers/tools/visible-text-probe.cjs` grava o texto da página em 19 períodos do hero e na janela
   dos 27 estados em ano 2026, mandato 2019-2022 e mês 2025-06 (100 textos). Base:
   `private/cleanup-proof/visible-text-before-phase-1_2026-10-21.json`. Provado em 2026-10-21: duas rodadas iguais (100 de 100)
   e um erro plantado ("Voltou para o estadO" numa cópia de `proposals.js`) pego em 54 textos.
   ```bash
   export PW_CORE=<pasta>/node_modules/playwright-core CHROME_HEADLESS=<chrome-headless-shell>
   node docs/superpowers/tools/visible-text-probe.cjs docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html <saida.json>
   node docs/superpowers/tools/visible-text-probe.cjs --compare private/cleanup-proof/visible-text-before-phase-1_2026-10-21.json <saida.json>
   ```
   Esperado: `100 texts compared, 0 differ`, `0 errors`.
2. **Arquivos gerados:** os quatro construtores da página (`build-cases.py`, `build-standalone-data.py`, `build-simulation.py`,
   `build-platform-preview.py`) refazem em 2026-10-21 os dez arquivos da página byte a byte (cópias no rascunho da sessão).
   Depois de cada tarefa: rodar os quatro e comparar; o que mudar tem de ser só o que a tarefa diz.
3. **Testes do livro:** `.venv/bin/python -B -m unittest discover -s data/scripts/ledger/tests` (29 testes, OK em 2026-10-21).

---

### Tarefa 0: um ambiente Python (B5: P1-6, P2-11)
**Arquivos:** criar `requirements.txt`; apagar `data/scripts/ledger/requirements.txt`; mudar `.gitignore`, `CLAUDE.md` (Comandos),
`data/scripts/series/estimate_uf_revenue.py:108`, as docstrings que citam `/usr/local/bin/python3`.
- [ ] `requirements.txt` na raiz com `duckdb==1.5.6`, `openpyxl==3.1.5`, `xlrd==2.0.1` (os três únicos pacotes de fora que os 147
  scripts importam, contados com `ast`) e a nota "Python 3.12 ou mais novo".
- [ ] `.venv/` e `__pycache__/` no `.gitignore` (P2-20).
- [ ] `estimate_uf_revenue.py:108`: aspas simples dentro da f-string, para o arquivo abrir também no 3.11.
- [ ] Comandos do `CLAUDE.md` e docstrings: `.venv/bin/python` no lugar de `/usr/local/bin/python3` e de `python3`; uma linha de
  instalação (`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`) e as ferramentas do sistema (poppler
  `pdftotext`, `sips` do macOS nas fotos, um Chrome sem tela para as sondas).
- [ ] Prova: os 147 scripts abrem com `ast.parse` no 3.11 e no 3.14; os 29 testes passam no `.venv`.

### Tarefa 1: mortos e órfãos para `private/archive/` (B2, B9, B10, P1-8, P1-10, P1-19, P1-22, P2-1, P2-7, E1)
**Regra:** cada arquivo vai para `private/archive/<caminho de hoje>`, com `mv`, só depois de uma busca por leitor no código vivo
(`.py`, `.cjs`, `.js`, `.sh`, `.html` fora de `private/`) que dá zero; a busca é provada antes com um nome que tem leitor.
- [ ] Páginas: as 24 rodadas antigas de `docs/superpowers/previews/` (todas as `*_DESIGN_*.html` menos a fonte
  `hero-mapa-3d-round-2`, a simulação da home e a página da plataforma), os 11 parciais `src/post-grill-round-*`, os 8 arquivos de
  rodada em `assets/` (`bi-ledger-graph.js`, `bi-ledger-graph-r2.js`, `bi-ledger-graph-r4.js`, `ledger-graph.js`,
  `ledger-graph-r2.js`, `ledger-graph.css`, `modal-options.js`, `bi-post-grill.js`).
- [ ] Construtores de rodada: `build-post-grill-round.py`, `build-post-grill-data.py`, `build-ledger-graph-data.py`,
  `build-ledger-graph-concepts-data.py`, `build-ledger-graph-network-data.py`, `ledger-graph-map-balances.cjs`,
  `ledger-graph-state-branches.cjs`; as duas linhas deles nos Comandos saem.
- [ ] Dados sem leitor (N-12, P1-8): os 10 logs; `siafi_unidades_gestoras_2020-01.csv`, `ckan_search_ug.json`,
  `ckan_ug_package.json`, `metadados_ug.pdf`, `arrecadacao-cnae.csv`, `atlas_079.csv`; `data/home/fefc-2026.json` (contradiz o
  RTN, N-11); `data/federal/raw/camara-ceap-2026.csv.zip` e `senado-ceaps-2026.csv` se a busca der zero;
  `federal-section-2026-01-07.json` (o único leitor é `build-post-grill-data.py`, que vai junto); `ug-balance-2024.json` e
  `_hybrid.json` com os seus construtores (`build_ug_balance.py`, `build_ug_balance_hybrid.py`, `report_ug_tables.py`,
  `bridge_portal_tesouro.py`, P1-11); `data/criciuma-fleet.json` com `fleet_case()` de `build-cases.py` (P2-19).
- [ ] (movido para a fase 2, ver "Fora desta fase") Pesquisa avulsa em `data/df/` (P1-19): os seis scripts (`q2_gasto_por_uf.py`, `q4_local.py`, `rfb_df_breakdown.py`,
  `rfb_natureza.py`, `atlas_vinculos_uf.py`, `agg_desp_uf.py`) e as suas saídas; os relatórios de 2024 da raiz (`recon.py`,
  `tables.py`, `checks.py`, `agg_desp.py`, P1-22) se a busca der zero; `series/agg_uorg_uf.py` e a sua saída (P1-10).
- [ ] Gemini (E1, D97 item 4): os três documentos de `docs/research/` que derivam da conversa vão para `private/`.
- [ ] Ponteiros: todo caminho de arquivo movido citado em `README.md`, `CLAUDE.md`, `docs/**/*.md` é reescrito para o caminho novo;
  prova: busca dos caminhos antigos dá zero.
- [ ] Provas: texto visível igual; os construtores refazem os arquivos da página byte a byte; 29 testes.

### Tarefa 2: citações do autor fora do código (P2-22, F-12 parte 2)
- [ ] Busca em `.js`, `.py`, `.cjs`, `.html` vivos por atribuição datada ao autor ("owner", "autor", data) e por frase citada
  entre aspas com 25 caracteres ou mais; as citações de fonte oficial ficam (são o objetivo).
- [ ] Cada comentário vira o comportamento e a decisão: `(D101)` no lugar da citação; "por quê esta regra: D100" no lugar da história.
- [ ] Provas: a busca dá zero (controle: uma citação plantada numa cópia é achada); texto visível igual; na página gerada, só
  linhas de comentário mudam (diff conferido).

### Tarefa 3: o saldo de 2024 antigo fora do pacote e os ramos mortos da página (M8: N-5, P1-11; W9: F-9)
- [ ] `BI.balance` (de `assets/uf-balance.json`, regra "saldo (b)") sai do pacote; nome, região e população vêm de um arquivo
  pequeno de estados (`uf`, `name`) e da população que a página já lê; `build-balance.py` e `assets/uf-balance.json` vão para o arquivo.
- [ ] Saem o ramo "só 2024" (`statehero.js:23`, `rowsAt()`), a busca de JSON quando `window.BI` falta, o `?nomap=1` com
  `hero-backdrop.png`, e entra uma mensagem visível "dados não carregaram" quando `window.BI` falta.
- [ ] Provas: texto visível igual, 0 erros; controle: com `bi-data.js` bloqueado a página mostra a mensagem (antes: tela vazia).

### Tarefa 4: os nove desenhos reprovados fora de `proposals.js` (W9: F-8)
- [ ] Saem `p1`, `hundred`, `p2`, `p3`, `r6a` a `r7c` e o CSS deles em `proposals.css`; `r8` vira `renderStateModal`; somem os
  interruptores `v7`, `mobile`, `cards`, `'maquete'`, com a variante escolhida fixa.
- [ ] Provas: texto visível igual, também a 420 px nos cinco estados da auditoria; busca por `render.p1`..`r7c` dá zero.

### Tarefa 5: checagens que podem falhar, cada uma com o seu controle (B3, B6, B7, B8 parte, M6, M9, M12, C3, C4)
Cada checagem nova ou refeita só conta depois de falhar num controle plantado pelo motivo plantado.
- [ ] **Rede em 100 períodos** (`ledger-graph-periods-check.cjs`, P2-21): conta cada `console.error` do código do mapa e falha.
  Hoje falha com 94 estado-meses (linha de receita negativa escondida); fica assim até a fase 4 aplicar Q48 (D139).
- [ ] **Regra em duas etapas** (`build_two_step_balance.py`, P1-1, N-4, P1-3, P1-4): a identidade "27 estados + União" passa a se
  chamar checagem de montagem; entra a checagem real: toda parte da União maior ou igual a zero e o resíduo sem nome dentro de
  uma tolerância medida no pior caso real; um controle no lado da entrada (uma linha do Portal duplicada) tem de parar;
  as faixas de escopo apertadas ao pior caso medido mais uma margem; docstring diz que a checagem ao centavo é só conservação.
  Se a parte negativa de 2024 (R$ 3,25 bi) fizer a checagem falhar, a causa é investigada e anunciada antes de seguir.
- [ ] **Receita por estado contra o total nacional** (N-14): diferença mês a mês no construtor, com tolerância tirada da pior
  diferença real e os meses negativos marcados.
- [ ] **Série central** `federal-by-uf-monthly.json` (P1-13): checagem ao centavo contra o arquivo da Receita e os totais do Portal,
  com `--control`, em `checks_series.py`; mês parcial e mês sem dado gravados como nulo, não como número (a página não lê esses
  meses hoje; o texto visível prova).
- [ ] **Seção federal** (`build_federal_section.py`, P1-14): as cinco conferências passam a comparar com totais que a fonte
  publica por conta própria (linha de pessoal do RTN; totais anuais da CEAP; totais de emendas do Portal); o que sobrar é
  chamado de checagem de montagem.
- [ ] **Bundle** (`build-standalone-data.py`, P2-4, P2-5, P1-15): toda entrada que a página lê é obrigatória (erro com o nome do
  construtor que a escreve), com uma lista explícita das seções em espera; a checagem tautológica do "por que falta" sai; a
  seção federal é escolhida por nome fixo, não pela ordem dos nomes.
- [ ] **Livro de fluxos** (`ledger/build.py`, P2-2; `planted.py`, P2-13): com `--control` nunca publica; dois erros plantados novos
  que só as garantias de fonte externa pegam (um fluxo DTT `|paid` no meio do ano; a linha 9 do RTN deslocada na linha e no fluxo);
  a spec diz quais garantias são estruturais.
- [ ] **BR-470** (P2-9): falha com mês faltando; restos a pagar pagos conferidos contra o total do Tesouro; soma em centavos;
  SHA-256 de cada ZIP na saída. **Citações das obras** (P2-16): a comparação guarda dígitos e separadores; ETE e CEI passam
  pelo mesmo conferidor. Controles: "R$ 113.652" contra "R$ 1.136,52" tem de falhar; um mês removido tem de falhar.
- [ ] Provas: cada controle falha pelo motivo plantado; o que roda de verdade passa (ou a falha real é anunciada); texto visível igual.

### Tarefa 6: chaves de JSON e textos de código em inglês (B14: N-13, P1-21, P2-12)
- [ ] Chaves em português trocadas no escritor e no leitor ao mesmo tempo: `federal-payroll-by-uf.json` (e `serieslayer.js`,
  `fcdf.by_group.pessoal_e_encargos`), `mte-seguro-abono-uf-2024_hybrid.json`, `sc-401-terceira-faixa.json`, `ibge-estados.json`,
  `br-470-duplicacao.json`, as chaves de checagem de `two-step-balance-*.json`, a saída de `br470_payments.py`, `state-deputies.json`,
  os valores de `governors_curated/*.json`; as garantias do livro ganham um id em inglês (`g1_unique_ids`) com a frase como rótulo.
- [ ] Docstrings e comentários em português traduzidos nos scripts listados em P1-21 e P2-12.
- [ ] Provas: a busca de chaves em português (com o controle `nome_controle` plantado) dá só nomes próprios e campos de fonte;
  texto visível igual; arquivos regenerados iguais aos antigos com o mapa de chaves aplicado.

### Tarefa 7: o mesmo fato com valores diferentes, e armadilhas pequenas (C5: N-11; B15 parte)
- [ ] SC-401: o total calculado ganha o rótulo "líquido"; Linha 17: a nota "não localizado" sai e entra o campo `provenance` de
  registro feito à mão (P2-19).
- [ ] Fotos de signatário só por nome exato, com uma tabela de apelidos (P2-8); o registro de fontes volta à versão antiga quando
  o órgão volta atrás, com teste A, B, A (P2-14); `build.py` da raiz falha com entrada faltando e grava num temporário (P1-12);
  `municipal-taxes-2024.json` marca `complete: false` onde há município sem dado (P1-24); `build-balance.py` sai com a Tarefa 3;
  os `assert` que guardam dados viram `raise SystemExit` (P2-20); `shot.sh` abre a página da plataforma (P2-20).
- [ ] Caminhos e regras da máquina do autor fora dos arquivos que vão a público (E2): `docs/ai/learned-patterns.md`, o acompanhamento.
- [ ] Provas: texto visível igual; testes; cada armadilha com o seu controle.

### Tarefa 8: fecho da fase
- [ ] Texto visível igual ao da base (100 de 100), 0 erros; arquivos gerados: só as mudanças das tarefas; 29 testes ou mais.
- [ ] Registro: uma decisão no README, o acompanhamento da rodada 11, o `CLAUDE.md` ("Próxima sessão"), o estado de trabalho.
- [ ] Nada aberto no fim: nenhum Chrome sem tela, nenhum servidor.

---

### Registro da execução
(uma linha por tarefa, com as provas)

- **Tarefa 0 (2026-10-21):** `.venv` com Python 3.14.6, `requirements.txt` na raiz (duckdb 1.5.6, openpyxl 3.1.5, xlrd 2.0.1),
  `.gitignore` com `.venv/` e `__pycache__/`, Comandos e docstrings com `.venv/bin/python`. Duas f-strings que só o 3.12 lia:
  `estimate_uf_revenue.py:108` (saída refeita igual byte a byte) e `build_br470.py:365` (achada pela checagem no 3.11, fora da
  auditoria; sem a pasta de downloads, provada pela igualdade das duas formas em três entradas). Os 147 scripts abrem no 3.11 e
  no 3.14; 29 testes OK.
- **Tarefa 1 (2026-10-21):** 82 arquivos para `private/archive/` (eram 84; ver a correção na tarefa 5) (24 rodadas, 11 parciais, 8 arquivos de rodada, 7 construtores,
  10 logs, 6 brutos sem leitor, `fefc-2026.json`, a CEAP crua, `federal-section-2026-01-07.json`, `ug-balance-2024*.json` e os
  4 construtores dele, `criciuma-fleet.json` e os 7 scripts de Criciúma); `fleet_case()` saiu de `build-cases.py` (D28). Busca
  por leitor antes (controle `periods.js`: 5 leitores achados). Os três documentos do Gemini para `private/gemini/`. 71 ponteiros
  reescritos nos documentos atuais; só a nota histórica de retomada do acompanhamento guarda o nome antigo. Provas: os 10
  arquivos da página iguais byte a byte, 100 de 100 textos iguais, 0 erros, 29 testes.
- **Tarefa 2 (2026-10-21):** 23 comentários reescritos em 13 arquivos (atribuições "owner, data" viram o comportamento ou o
  código da decisão; as três citações literais saíram). A busca dá 5, todas de autoria de projeto de lei; o controle plantado
  é achado. Páginas geradas: só 6 linhas de comentário mudam em cada uma; dados iguais; 100 de 100 textos iguais.

- **Tarefa 3 (2026-10-21):** `BI.balance` virou `BI.states` (uf, nome, população; iguais aos de antes nos 27 estados); a única
  diferença no pacote é essa chave. Saíram o ramo "só 2024" de `rowsAt()` e de `statehero.js`, a busca de JSON sem `window.BI`, o
  `?nomap=1` e a primeira chamada de `apply()` antes do período; `build-balance.py`, `assets/uf-balance.json` e `hero-backdrop.png`
  para o arquivo. Entrou a mensagem "Os dados não carregaram. Recarregue a página.". Provas: 100 de 100 textos iguais, 0 erros;
  controle com `bi-data.js` bloqueado mostra a mensagem; carga normal não mostra.
- **Tarefa 4 (2026-10-21):** alcance calculado a partir do que a página chama (`view`, `muniView`, `render`, `helpers`), sem contar
  comentários nem textos entre aspas: 24 declarações mortas saíram de `proposals.js` (649 para 509 linhas), e mais três depois de
  fixar a variante (`REV_ICON`, o ajudante `cases`, `ranking()` em `statehero.js`). `r8` virou `renderStateModal`; saíram os
  interruptores `v7`, `v6`, `mobile`, `cards`, `switch` e `'maquete'`/`'ranking'`/`'plano'`. Provas: 100 de 100 textos iguais a
  1100 px; a 420 px (SC, DF, SP, RS, AM, 34 textos) igual ao arquivo original; o alcance dá 0 morto.

- **Tarefa 5 (2026-10-21).** Cada checagem nova falhou no seu controle pelo motivo plantado.
  - Rede em 100 períodos: conta os alertas do código do mapa e falha; hoje 94 estado-meses (o maior, MG mar/2026, R$ 3,46 bi),
    os mesmos da auditoria, até Q48 na fase 4. Controle: R$ 10 mi na receita corrente de SC 2024-01 é pego.
  - Regra em duas etapas: identidades viram checagem de montagem; entram toda parte da União maior ou igual a zero, o resto sem
    nome até 3% da União (pior caso 2,7%, 2019), a razão Portal/Tesouro de 0,995 a 1,025 por mês (medida 1,000 a 1,015) e as
    faixas de escopo apertadas ao pior caso medido. Sete anos passam e reescrevem só o bloco `check`; 2024 falha (resto de
    -R$ 3,25 bi) e não grava nada. Investigado: não é o bloco do MTE (R$ 80,64 bi contra R$ 80,71 bi no RTN) nem os meses de
    precatórios; o resto verdadeiro fica negativo de março a dezembro de 2024 (cerca de R$ 0,3 bi por mês). Achar a linha
    exige comparar linha a linha a base do Tesouro com as partes nomeadas: pesquisa de dados, levada ao autor.
    Controles novos no lado da entrada: uma linha do Portal lida duas vezes (pega pela razão Portal/Tesouro em 2019, 2023 e 2025,
    pela parte negativa em 2026; as checagens ao centavo não a veem) e a receita de SC dobrada (pega pela comparação com o
    arquivo da Receita). A série das duas etapas ganhou `--control=input`; refeita igual byte a byte.
  - Série central `federal-by-uf-monthly.json` (`checks_series.py`, seção 10): a receita dos 27 estados em 79 meses publicados
    bate com o arquivo da Receita a meio centavo (controle de R$ 0,01 pego); a diferença nacional menos estados acima de R$ 10
    é listada com o sinal (9 meses, os mesmos de N-14); os meses depois do último da Receita com números são listados (ago e
    set/2026). O construtor desta série não roda hoje (a pasta de entradas não está no projeto): os nulos de mês parcial vão
    para a fase 2, com o manifesto dos brutos.
  - Seção federal: a folha de cada mês contra a linha 4.2 do RTN, faixa 0,970 a 1,000 (medida 0,977 a 0,996 em 92 meses);
    as outras viram checagens de montagem (CEAP e emendas não têm total publicado à parte no projeto). Controle de entrada:
    a folha do Judiciário de ago/2026 apagada passa pelas checagens de montagem e é pega pela faixa (0,864). Um arquivo só,
    `data/federal/federal-section.json`, com os meses dentro; no pacote muda só `federal_section.check`.
  - Pacote: toda entrada é obrigatória e o erro dá o nome do script que a escreve (controle: sem `public-sector-primary.json`
    para e não toca no pacote); a checagem tautológica do "por que falta" saiu e `--control=shortfall` é pego pela soma dos
    detentores da dívida.
  - Livro de fluxos: `--control` nunca publica (sai 0 quando as garantias param, 1 quando não param; `control_outcome` no
    relatório). Dois erros plantados novos que só a fonte de fora vê: a linha DTT de juros pagos e o fluxo movidos R$ 10 juntos
    (pego só por G3, contra o RREO) e a linha 9 do RTN e o fluxo movidos R$ 20 mil juntos (pego só por G5, contra o Banco
    Central), cada um numa transação desfeita; `published_line` igual à cópia de antes. 8.781 fluxos, mesma impressão digital; 29 testes.
  - Obras: `require_quote` confere cada número da citação com os separadores (o verificador antigo aceitava "R$ 113.652" e
    "R$ 11.365,2" para "R$ 1.136,52"; o novo recusa os dois e aceita o ponto quebrado do PDF); `require_complete_months`
    para a BR-470 com mês sem download. Provado no `self_test` que todo construtor de obra roda ao começar. Os construtores de
    obra não rodam hoje (os documentos baixados não estão no projeto): as citações reais, ETE e CEI no verificador, restos a
    pagar contra o Tesouro, soma em centavos e o SHA-256 de cada ZIP ficam para a fase 2, com os brutos baixados de novo.
  - **Correção da tarefa 1:** a busca por leitor procurava o nome literal e não via o f-string de `build_federal_section.py`
    (`camara-ceap-{YEAR}.csv.zip`, `senado-ceaps-{YEAR}.csv`); a auditoria (N-12) tinha o mesmo ponto cego. Os dois voltaram
    para `data/federal/raw/`; uma nova busca pelo prefixo do nome de cada arquivo movido não achou outro leitor.

- **Tarefa 2, complemento (2026-10-21):** a busca só lia comentários `#` e `//`; duas citações do autor estavam na docstring de
  `build_two_step_balance.py` (D114 e GD16) e saíram. A busca nova lê também as docstrings e as citações junto de um código D, GD
  ou Q; restam quatro, todas nome oficial ou título de seção ("Despesas e Transferências Totais da União", "Por que falta
  dinheiro", "O que o Brasil vende").
- **Parada para nova sessão (2026-10-21):** tarefas 0 a 5 feitas; 6 a 8 ficam para uma sessão nova (custo do contexto). Volume
  medido para a tarefa 6: cerca de 300 linhas de comentário e docstring em português em 77 scripts, mais as chaves de N-13 e P2-12.
