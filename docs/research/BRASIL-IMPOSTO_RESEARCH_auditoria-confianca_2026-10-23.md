# Auditoria de confiança do Brasil-Imposto (2026-10-23)

**English summary.** A read-only trust audit of the repository at `main` `2409704` (after #54), done on 2026-10-23 at the
maintainer's request, with the DF balance checked first. **The DF figures are right:** an independent recomputation from
`data/`, in exact decimals and without the page's code, gives the same value as the published page, to the cent, for all 3,060
DF figures in all 102 periods of the selector (every month from 2019-01 to 2026-08, every year, both mandates). In every one of
the 100 periods with full data, the 27 states (DF capped) plus the União block equal the official total after the move, and a
planted real in one DF tax makes the check fail. **What is wrong is around the DF figure, not in it:** since the DF cap (D146),
the published "Rede do dinheiro" preview refuses to draw in every period, showing "impostos que não somam o que o estado pagou:
DF", and the DF panel shows two different federal amounts on the same screen (R$ 2.609 and R$ 5.521 per person per month in
2026) without saying why. Other findings: no automated test covers the DF cap, the federal balance, the União block or the two
other pages' sums; the "Voltou" side of the balance cannot be traced from the page to its sources; three committed page data
files cannot be rebuilt from a clean clone; the publishing workflow pins actions by tag and gives write permissions to its build
job; the public decision log stops at D154 while the code cites D155 to D162; small source gaps (cents in 61 months; R$ 38 mil
to R$ 310 mil in four months) are listed as "diferença sem explicação". Every source host is blocked from this environment, so
whether the 4,005 source links still answer could not be verified here. The fixes, ordered by trust gained per effort, DF
first, are in `docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_confianca_2026-10-23.md`.

**Estado:** fase 1 da missão de 2026-10-23 (só leitura). Nada foi mudado no código, nos dados ou nas páginas; este relatório e a
spec são os únicos arquivos do pull request. A fase 2 começa só depois de a spec ser aprovada.

**Base:** `main` em `2409704` (#54), 2026-10-23. O que já existe e não foi refeito: a fase 1 da auditoria de limpeza (D161,
`docs/superpowers/plans/BRASIL-IMPOSTO_PLAN_cleanup-phase-1_2026-10-21.md`), a auditoria de consistência (#45), `ci.yml`,
`dco.yml`, o CodeQL, a regra da `main`, `GOVERNANCE.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, os formulários de issue, o modelo
de pull request, os esquemas de `schemas/`, `uv.lock` e as issues #8 a #14. Onde um achado pertence a uma dessas issues, a
tabela diz qual.

**Como ler os riscos:** **alto** quando um cidadão pode ver na tela um número que não fecha ou não consegue confiar no que vê;
**médio** quando o número está certo mas não se prova sozinho (sem teste, sem fonte alcançável, sem reprodução); **baixo**
quando é higiene, sem efeito no que a tela mostra.

---

## 1. O DF primeiro

### 1.1 Como foi conferido

Duas contas feitas separadamente e comparadas ao centavo:

- **A da página:** o código publicado (`periods.js` e `serieslayer.js`) rodado em Node sobre o próprio pacote de dados
  (`assets/bi-data.js`, montado pelos construtores do repositório), em todos os 102 períodos que o seletor oferece: os 92 meses de
  2019-01 a 2026-08 (o último mês do seletor, `series.union.latest.nominal_result`), os 8 anos e os 2 mandatos. Script
  `page-df.cjs` (Apêndice A).
- **A independente:** um script em Python (`df_recompute.py`, Apêndice B) que lê só `data/` (nunca o pacote nem o JavaScript),
  aplica as regras como as decisões as escrevem (D37, D45, GD16, D114, D146) e soma em `Decimal` com os dígitos do próprio JSON.
  Ele refaz:
  - o que o DF enviou, mês a mês, com a estimativa de `federal-revenue-uf-estimated.json` nos 12 meses que ela cobre (de 2025-02
    a 2026-01);
  - o teto do D146 imposto por imposto: o DF fica com no máximo a sua parte do PIB do Brasil (`data/df/gdp-share.json`,
    365.669.108 / 10.943.345.439 mil reais = 3,341474597857662%) daquele imposto nos 27 estados;
  - o excesso que sai do DF e vai para o bloco da União;
  - o que voltou: repasses, Bolsa Família, INSS, BPC, FCDF e o gasto federal no DF pela regra em duas etapas (executivo, outros
    Poderes e benefícios centrais localizados, mais o seguro-desemprego e o abono anuais do MTE para um ano inteiro dentro do
    período), contado só quando todo mês do período tem o dado;
  - o fim do período em cada estado (o último mês que todo componente tem) e a saída dos meses marcados quebrados (2025-06).

### 1.2 Resultado

| Conferência | Resultado |
|---|---|
| As figuras do DF que o mapa mostra (enviado, enviado registrado, excesso, voltou, repasses, Bolsa Família, INSS, BPC, FCDF, gasto em duas etapas, saldo, saldo por pessoa por mês, meses, completo) e cada imposto do DF, nos 102 períodos | **3.060 figuras comparadas, 0 diferenças ao centavo** (o saldo por pessoa, a quatro casas) |
| Períodos com o saldo do DF completo | 100 de 102 (os dois sem saldo são os mesmos nos dois cálculos) |
| Depois da mudança, os 27 estados (DF com o teto) mais o bloco da União igualam o total oficial | **100 de 100 períodos**; a diferença do bloco da União antes e depois é igual ao excesso; o bloco nunca fica negativo |
| O total oficial nos dois arquivos que o trazem (`federal-by-uf-monthly.json` e `federal-spending-two-step-by-uf.json`) | iguais em todos os períodos |
| **Controle:** R$ 1 a mais na Cofins do DF em 2019-01 | a conferência falha (15 diferenças, saída 1), e a conferência mensal da seção 1.4 pega o real plantado |

**A igualdade "27 estados mais a União igual ao total oficial" vale por construção:** a página define o bloco da União como o
total oficial menos os 27 estados (`unionAt` no Início; `ledger-graph-model.js:102`), e por isso um real plantado no DF não a
quebra. A conferência que pode falhar é a da seção 1.4: mês a mês, os 27 estados como a Receita os registra contra a soma do
próprio arquivo e o total nacional.

O teto em 2024, imposto por imposto (a parte do DF em cada imposto, antes do teto):

| Imposto | DF registrado | Teto (3,34% do Brasil) | Excesso que vai para a União | Parte do DF |
|---|---|---|---|---|
| IRRF | R$ 63,19 bi | R$ 14,87 bi | R$ 48,32 bi | 14,2% |
| Contribuição dos servidores (PSS) | R$ 18,44 bi | R$ 1,40 bi | R$ 17,04 bi | 44,0% |
| Outras receitas da Receita | R$ 12,28 bi | R$ 1,39 bi | R$ 10,89 bi | 29,5% |
| Contribuição ao INSS | R$ 31,83 bi | R$ 22,43 bi | R$ 9,40 bi | 4,7% |
| IOF | R$ 8,92 bi | R$ 2,25 bi | R$ 6,67 bi | 13,2% |
| PIS/Pasep | R$ 8,34 bi | R$ 3,79 bi | R$ 4,55 bi | 7,4% |
| IRPJ | R$ 12,69 bi | R$ 10,70 bi | R$ 1,99 bi | 4,0% |
| CSLL | R$ 7,22 bi | R$ 5,71 bi | R$ 1,52 bi | 4,2% |
| Cofins | R$ 15,05 bi | R$ 13,94 bi | R$ 1,11 bi | 3,6% |
| Os outros 7 impostos | abaixo do teto | | R$ 0 | |
| **Total** | **R$ 184,10 bi** | | **R$ 101,50 bi** | o DF fica com R$ 82,60 bi |

### 1.3 Achados do DF

**DF-1 (alto). A prévia "A rede do dinheiro do imposto" não desenha em nenhum período, por causa do DF.**
- Evidência: `node docs/superpowers/tools/ledger-graph-periods-check.cjs "$PWD"` sai com `CHECK FAILED`. Em **100 de 100
  períodos** com dado completo, a conferência `taxes` diz "impostos que não somam o que o estado pagou: DF".
- Na página montada (Início, "Abrir a prévia da rede", 2026), o visitante lê: "Uma conferência falhou neste período; o grafo não
  é desenhado com números que não fecham." e logo abaixo "impostos que não somam o que o estado pagou: DF".
- Causa: `ledger-graph-model.js:54-56` soma os impostos do DF sem o teto (`federalAt().byTax`, R$ 11,36 bi em 2019-01) e
  compara com o enviado com o teto (`sent`, R$ 4,24 bi); a tolerância é R$ 0,50.
- A conferência está certa em recusar: o defeito é o modelo do grafo não ter acompanhado o D146.
- O verificador existe mas não roda no `ci` (seção 3), por isso nada avisou.
- Relação: a spec do Início mais curto (#48) e o D160 ("produção não tem prévia") já tratam de onde a prévia fica.

**DF-2 (alto). O painel do DF mostra dois valores diferentes para o imposto federal, sem dizer por quê.**
- Evidência: texto visível do modal do DF, ano 2026, montado da `main`:
  - "Com a União · 2026 (janeiro a julho) · Foi para a União R$ 2.609 /mês por pessoa": o valor com o teto, R$ 54,98 bi em 7
    meses.
  - Na mesma tela, "PAGOU · Impostos pagos por quem vive aqui · União R$ 5.521/mês", com os cartões "Imposto de renda União
    R$ 2.290/mês", "INSS União R$ 924/mês", "Previdência dos servidores federais União R$ 533/mês" e outros: os valores sem o
    teto, que somam os R$ 116,66 bi registrados.
- Causa: `proposals.js:282` (`paidView`) lê `fed.byTax`, que `serieslayer.js:197` devolve sem o teto, enquanto `sent` já tem o
  teto.
- O mesmo `byTax` alimenta a frase do Início sobre a contribuição dos servidores registrada no DF
  (`BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html:1327`). Lá o valor registrado é o pretendido: a frase fala do que a
  Receita registra.
- O cidadão vê R$ 2.609 e R$ 5.521 lado a lado e não tem como saber qual vale. A nota do teto só aparece no cartão do mapa
  ("Estimativa: em cada imposto o DF conta no máximo...").

**DF-3 (médio). Nenhum teste automático cobre o teto do DF nem o saldo do DF.**
- Evidência: `grep -rln "dfCapped\|df_gdp_share\|gdp-share" pipelines docs/superpowers/tools site` acha só
  `pipelines/df/fetch_gdp_share.py` e `docs/superpowers/tools/build-standalone-data.py`. Nenhum teste.
- A conta desta auditoria é a primeira a refazer o DF por fora.

**DF-4 (baixo). Nos meses estimados, os impostos do DF somam de R$ 0,01 a R$ 0,03 a mais ou a menos que o total do DF.**
- Diferença sem explicação, em 9 períodos, todos dentro de 2025-02 a 2026-01:

| Período | Soma dos impostos | Total |
|---|---|---|
| abr/2025 | R$ 16.102.755.986,01 | R$ 16.102.755.986,00 |
| jul/2025 | R$ 15.880.266.030,14 | R$ 15.880.266.030,16 |
| set/2025 | R$ 15.343.046.434,82 | R$ 15.343.046.434,85 |
| out/2025 | R$ 17.899.482.012,49 | R$ 17.899.482.012,48 |
| nov/2025 | R$ 16.466.483.909,87 | R$ 16.466.483.909,86 |
| dez/2025 | R$ 24.418.912.694,92 | R$ 24.418.912.694,91 |
| jan/2026 | R$ 22.470.513.593,71 | R$ 22.470.513.593,70 |
| 2025 | R$ 185.930.029.160,62 | R$ 185.930.029.160,63 |
| 2026 | R$ 116.664.435.152,55 | R$ 116.664.435.152,54 |

**DF-5 (baixo). Uma parte do PIB, a de 2023, vale para todos os períodos de 2019 a 2026.**
- `data/df/gdp-share.json` tem um ano só (`"year": 2023`). A tela diz "IBGE 2023".
- Não é um erro de conta: é como o D146 está escrito. Fica registrado para o mantenedor decidir se cada ano usa o PIB do seu
  ano (o IBGE publica com dois anos de atraso).

### 1.4 Os totais oficiais, mês a mês (fora da igualdade por construção)

**DF-6 (médio). O total nacional de 2026 vem em milhões, e em quatro meses os estados somam mais do que o país.**
- Diferenças sem explicação:
  - Os totais de 2026 vêm da Tabela III da Análise da Arrecadação em PDF, em R$ milhões
    (`build_federal_by_uf_monthly.py:235`): R$ 325.751.000.000,00 em jan/2026, R$ 222.117.000.000,00 em fev/2026, e assim até
    ago/2026.
  - Com eles, a parte "sem estado" fica negativa:

| Mês | Os 27 estados menos o total nacional |
|---|---|
| jan/2026 | R$ 250.550,94 |
| fev/2026 | R$ 309.569,57 |
| mar/2024 | R$ 38.134,77 |
| jun/2024 | R$ 102.360,98 |

  - Em mar/2024 e jun/2024 o total vem da série anual em planilha, não do PDF.
  - Em outros 55 meses, a parte "sem estado" fica entre −R$ 0,05 e −R$ 7,03.
- Esses valores entram no bloco da União, que é o total oficial menos os 27 estados. Não mudam o DF.

**DF-7 (baixo). A soma dos 27 estados no arquivo difere da soma que o próprio arquivo guarda.**
- Em 59 meses a diferença é de até R$ 0,03.
- Em 2 meses (out/2024 e mar/2025), a soma dos estados mais o "sem estado" difere do total nacional em R$ 0,01.
- Diferença sem explicação.

---

## 2. Rastreabilidade

### 2.1 Do número à fonte, por família

| Família na tela | Arquivo em `data/` | Script que escreve | Fonte oficial | Período | Lido em | O cidadão chega à fonte pela página? |
|---|---|---|---|---|---|---|
| Início, mapa e modal: "Foi para a União" por estado e por imposto | `series/federal-by-uf-monthly.json` | `pipelines/series/build_federal_by_uf_monthly.py` | Receita, `arrecadacao-estado.csv`, a série 1994 a 2025 e a Análise mensal de ago/2026 | 2019-01 a 2026-07 | 2026-09-30 | Sim: o modal liga "Arrecadação federal por estado: Receita Federal" |
| A estimativa dos meses de 2025-02 a 2026-01 | `series/federal-revenue-uf-estimated.json` | `pipelines/series/estimate_uf_revenue.py` | derivada do arquivo acima (o método e o teste retroativo estão no arquivo) | 2025-02 a 2026-01 | sem data | Só a palavra "estimada" e o número de meses; o método não tem link |
| O teto do DF | `df/gdp-share.json` | `pipelines/df/fetch_gdp_share.py` | IBGE SIDRA, tabela 5938 | PIB de 2023 | 2026-10-21 | Não: a tela diz "IBGE 2023", sem link |
| "Voltou": repasses | `series/federal-by-uf-monthly.json` | o mesmo | Portal da Transparência, transferências | mensal | 2026-09-30 | Sim (modal) |
| "Voltou": INSS, BPC, Bolsa Família | `series/federal-by-uf-monthly.json` | o mesmo | Previdência (BEPS), MDS | mensal | 2026-09-30 | Não: só o nome e a data de divulgação, sem link |
| "Voltou": FCDF e gasto federal pela regra em duas etapas | `series/federal-spending-two-step-by-uf.json` | `pipelines/ug/build_two_step_series.py`, a partir de `data/ug/two-step-balance-*.json` | Portal, despesas por execução (uma URL por mês em `data/ug/`), Tesouro | 2019-01 a 2026-07 | 2026-10-02 | Não: o arquivo que a página lê não tem fontes, só `built_from`; as URLs ficam em `data/ug/`, fora do pacote |
| Bloco da União | `series/federal-spending-two-step-by-uf.json` (`union`) | o mesmo | Tesouro, RTN | mensal | 2026-10-02 | Sim: o Início liga o RTN |
| Contas do estado (RREO, RGF) | `series/state-budgets.json` | `pipelines/series/build_state_series.py` | SICONFI | bimestral | 2026-10-07 | Sim: o modal liga o RREO e o RGF |
| Rede do dinheiro: juros | `assets/bi-ledger-interest.js` (versionado) | `build-ledger-interest-asset.py`, a partir de `data/ledger/ledger.duckdb` (fora do git) | Tesouro, Banco Central | | | Não se refaz a partir de um clone (seção 2.3) |
| Os 3 Poderes: salários, auxílios, fichas | `assets/tres-poderes-r3-data.js` (versionado) | `build-tres-poderes-r3-data.py`, a partir de `data/federal/raw-pay/` (fora do git) | Câmara, Senado, Planalto, STF e os tribunais | 2026 | por ficha | Sim, por pessoa: 594 links de ficha; 14 links na página |
| Como o dinheiro anda: divisões | `assets/dinheiro-r1-data.js` (versionado) | `build-dinheiro-r1-data.py`, a partir de `data/ledger/ledger.duckdb` | Constituição, RTN de 2025, RREO dos 27 estados | 2025 | só a Constituição tem data (2026-10-21) | Em parte: o arquivo tem 3 fontes, a página liga só a Constituição |

### 2.2 Achados

**T-1 (médio). Metade do saldo, o lado "Voltou", não leva à fonte pela página.**
- O modal do DF (e o de cada estado) liga a Receita, os repasses do Portal e o SICONFI. Não liga:
  - o BEPS do INSS;
  - o MDS (Bolsa Família e BPC);
  - os arquivos de despesas do Portal que fazem a regra em duas etapas;
  - o FCDF do Tesouro;
  - o IBGE do teto.
- O arquivo que a página lê (`federal-spending-two-step-by-uf.json`) não tem nenhuma URL (0 na varredura): as fontes ficam em
  `data/ug/two-step-balance-*.json`, com uma URL do Portal por mês, número de linhas e tamanho.
- Conferido na página montada: 57 links externos no modal do DF, nenhum para esses cinco.
- Relação: #12 (guias e documentos de fontes).

**T-2 (médio). A estimativa de 12 meses não tem data de leitura nem link para o seu método.**
- `federal-revenue-uf-estimated.json` tem 0 URLs e nenhum campo de data.
- A fonte declarada é o próprio arquivo da Receita (`"file": "data/series/federal-by-uf-monthly.json"`).
- O teste retroativo está no arquivo (2024 contra 2023: erro mediano de 2,5%, máximo de 16,61%, no AP), mas não na tela.

**T-3 (médio). Como o dinheiro anda: duas das três fontes não são clicáveis.**
- O arquivo traz o RTN de 2025 e o RREO dos 27 estados com URL.
- A página montada tem 7 links externos: 6 para o GitHub e 1 para a Constituição.
- O RTN e o SICONFI não têm data de leitura.

**T-4 (médio). 23 arquivos de `data/` sem data de leitura, 7 deles sem URL nenhuma.**
- A varredura de 89 arquivos JSON de `data/` (sem `raw/` e `cache/`) procurou campos de data (`collected`, `read_on`,
  `checked`, `fetched`, `as_of`).
- Sem URL e sem data:
  - `df/federal_spending_by_uf_2024.json`
  - `df/federal_spending_by_uf_2025.json`
  - `df/pdad-2024-reports.json`
  - `df/q4_local_2024.json`
  - `federal/bills-2026-summary.json`
  - `ledger/build-report.json`
  - `series/federal-revenue-uf-estimated.json`
- Com URL mas sem data:
  - `series/union-spending-slices.json`
  - os sete arquivos de `trade/`
  - `ug/rtn-lines-monthly.json`
  - `ug/mte-seguro-abono-uf-2024_hybrid.json`
  - `home/moves-adjustments.json`
  - e outros.
- Relação: #10 (CI de proveniência, que pede o esquema e o manifesto).

**T-5 (baixo). 13.670 das 17.493 ocorrências de URL não têm data de leitura em nenhum objeto acima delas.**
- São 4.005 URLs distintas nas três páginas: 3.204 no Início, 1.403 em Os 3 Poderes e 3 em Como o dinheiro anda.
- A maior parte são fichas e fotos de políticos:
  - 8.774 em `politicians_view.uf` e 3.188 em `politicians_view.mayors`;
  - 595 fotos e 594 fichas em Os 3 Poderes.
- Também ficam sem data 79 links de pessoas e 33 fontes nos casos, e 34 em comércio exterior.

**T-6 (médio). Três arquivos de dados das páginas, versionados, não se refazem a partir de um clone.**
- `build-tres-poderes-r3-data.py` para em `FileNotFoundError: .../data/federal/raw-pay/deputies-in-office.json`.
- `build-dinheiro-r1-data.py` e `build-ledger-interest-asset.py` param em `Cannot open database ".../data/ledger/ledger.duckdb"`.
  O livro (`pipelines/ledger/build.py`) baixa as fontes, o que esta sessão não alcança.
- O `ci` não confere esses três arquivos contra os seus construtores. Confere só as três páginas e os quatro construtores do
  Início.
- Relação: #10 (manifesto dos brutos).

### 2.3 Os links ainda respondem?

Não verificado aqui: todo host de fonte respondeu 403 ao CONNECT do proxy desta sessão (seção "Não verificado"). A proposta é um
workflow semanal no GitHub Actions, cujos runners alcançam os sites do governo (spec, item C3).

---

## 3. Testes

O que o `ci` roda hoje e o que cada parte protege:

| Teste | Protege |
|---|---|
| `test_layout.py`, `test_environment.py`, `test_no_data_asserts.py` | a estrutura do repositório, o ambiente travado, as guardas sob `python -O` |
| `test_english_keys.py` | as chaves em inglês |
| `test_entities.py` + `build_entities.py` | os arquivos por entidade da fase B0: esquema e paridade de cada número com `data/` |
| `test_site_chrome.py`, `test_map_loader.py` | o cabeçalho, o rodapé e o carregador iguais nas três páginas; links do Início; o tamanho do pacote |
| `test_support.py` | os dados do Apoie |
| `test_judiciary_view.py` | Os 3 Poderes, só o Judiciário: médias em `Decimal` com arredondamento meio para cima, somas fechadas à mão, datas, estados (D154) |
| `test_case_portraits.py`, `test_municipal_taxes.py`, `test_root_build.py` | retratos dos casos, o `complete: false` dos impostos municipais, o construtor de 2024 |
| `pipelines/ledger/tests/` (30) | as garantias do livro, o dinheiro em centavos, o registro de fontes, o mapa do RTN, o esquema |
| o passo "as páginas versionadas são as dos construtores" | que as três páginas saem dos construtores |
| `site/src/lib/series.test.ts` (Vitest) | a biblioteca de séries do site em Astro |

**TST-1 (alto). Os caminhos do dinheiro não têm teste.** Sem teste no `ci`:
- o saldo federal de cada estado (`federalAt`);
- a regra em duas etapas na página;
- o teto do DF;
- o bloco da União;
- as conferências da Rede do dinheiro (o verificador existe e hoje falha, DF-1);
- as somas e médias do Legislativo e do Executivo em Os 3 Poderes;
- as divisões de Como o dinheiro anda.

O pipeline das duas etapas tem uma conferência própria ("27 estados mais a União igual ao total, ao centavo",
`build_two_step_balance.py`). Ela roda quando os dados são refeitos, não a cada pull request.

**TST-2 (médio). As sondas de navegador só rodam à mão.** São estas, cada uma com o seu `--control`:
- `site-check`
- `visible-text-probe`
- `overlay-check`
- `ui-sweep`
- `apoie-check`
- `home-link-check`
- `ledger-graph-periods-check`
- `tres-poderes-judiciary-check`

**TST-3 (baixo). Duas regras de arredondamento em Os 3 Poderes.**
- O Judiciário usa `Decimal` com meio para cima (testado).
- O Legislativo e o Executivo usam `round()` de Python sobre `float` (`build-tres-poderes-r3-data.py:67`), que arredonda meio
  para o par e sofre do binário.

Conferido nesta auditoria, sem teste: as divisões de Como o dinheiro anda fecham.
- Cada imposto reparte 100,0%.
- O gasto dos 27 estados soma R$ 1.318,3 bi contra o total de R$ 1.318,4 bi.
- A receita e a despesa da União diferem das suas partes em R$ 0,1 bi e R$ 0,2 bi. É o arredondamento a uma casa, e os valores
  vêm em bilhões com uma casa.

---

## 4. CI e cadeia de suprimentos

| Workflow | Quando roda | Permissões | Ações |
|---|---|---|---|
| `ci.yml` | todo pull request; push na `main` | `contents: read` | fixadas por commit |
| `dco.yml` | todo pull request | `contents: read` | nenhuma ação externa |
| `pages.yml` | push na `main`; manual | `contents: read`, `pages: write`, `id-token: write` no workflow inteiro | **fixadas por tag**: `checkout@v4`, `setup-python@v5`, `upload-pages-artifact@v3`, `deploy-pages@v4` |
| CodeQL (configuração padrão do GitHub) | pull requests e semanal | | `actions`, `javascript-typescript`, `python` |

- **CI-1 (médio). O workflow que publica o site fixa as ações por tag.**
  - Uma tag pode ser movida; um commit não.
  - `ci.yml` já segue a regra.
  - O #52 fixa por commit o `deploy.yml` do staging, mas mantém as tags do `pages.yml`.
- **CI-2 (médio). `pages: write` e `id-token: write` valem também para o job `build`.** Bastariam no job `deploy`.
- **CI-3 (médio). Não há atualização de dependências.**
  - Os alertas e as correções de segurança do Dependabot estão ligados.
  - Não há `.github/dependabot.yml` nem Renovate para as ações, o `uv.lock` e o `package-lock.json`.
- **CI-4 (baixo). Sem OpenSSF Scorecard** (#11).
- **CI-5 (médio). Nenhuma checagem de que os links de fonte respondem** (seção 2.3; #10, #12).
- **CI-6 (médio). O `ci` não roda as conferências de dinheiro nem as sondas** (TST-1, TST-2).

---

## 5. Segurança (lido pela API, só leitura)

**Verificado:**
- O repositório é público.
- Varredura de segredos: ligada.
- Proteção de push: ligada.
- Alertas e correções de segurança do Dependabot: ligados.
- Relato privado de vulnerabilidade: ligado.
- `web_commit_signoff_required`: ligado.
- Merge só por squash, ramo apagado depois do merge.
- A regra 25616038 da `main`:
  - ativa, sem quem a contorne;
  - sem apagar, sem push forçado, histórico linear, só por pull request, só squash;
  - `ci` e `dco` obrigatórios (não estritos);
  - **0 aprovações exigidas e nenhuma revisão de dono de código**;
  - alvo `~DEFAULT_BRANCH`.
- CodeQL configurado.

- **SEC-1 (médio). Nenhuma aprovação é exigida para um pull request entrar na `main`.** Com novos colaboradores (a fase 1 do
  `GOVERNANCE.md`), um pull request de outra pessoa entraria só com o `ci` e o `dco` verdes. O alvo `~DEFAULT_BRANCH` já está na
  spec de staging (seção 6, item 1).
- **SEC-2 (baixo). A varredura de segredos sem padrões genéricos e sem checagem de validade.** As duas estão desligadas:
  `secret_scanning_non_provider_patterns` e `secret_scanning_validity_checks`.

---

## 6. Experiência de quem contribui (de um clone limpo, nesta sessão)

| Passo | Tempo | Resultado |
|---|---|---|
| `git clone` | 21 s | 89 MB de `.git`, 216 MB no disco |
| `uv sync --locked` (sem cache) | 11 s | ok |
| `uv run --locked python -m unittest discover -s pipelines/tests` | 19 s | ok (1 pulado) |
| `... -s pipelines/ledger/tests` | 6 s | ok |
| os cinco construtores das páginas | 5 s | ok; `git status` limpo |
| `build_entities.py` | 1 s | ok |
| `cd site && npm ci` | 13 s | ok, com aviso `EBADENGINE` |
| `npm run types`, `npm test` | 1 s | ok |
| `npm run check`, `npm run build` | | **param**: "Please upgrade Node.js to a supported version: ">=22.23.4"" (esta sessão tem Node 22.22.0; o repositório pede 24 em `.nvmrc`) |

São uns 12 comandos em três blocos do README, e pouco mais de um minuto de trabalho depois do clone.

- **DX-1 (médio). Não há um comando único de preparo e conferência.**
  - O bloco de montagem do README não traz `build-site-chrome.py`, que o `ci` roda.
  - Nenhum documento de quem contribui explica as variáveis das sondas (`PW_CORE`, `CHROME_HEADLESS`, `CDN_MIRROR`).
  - Com o #52, `build-site.py` vira o comando único de montagem.
- **DX-2 (baixo). Não há dicionário de dados.**
  - Os esquemas de `schemas/` cobrem só os arquivos por entidade (6 esquemas).
  - As séries de `data/series/`, que fazem o mapa, não têm esquema. Relação: #10.
- **DX-3 (baixo). O Node mínimo só aparece no erro.** `npm ci` passa com Node antigo, e `check` e `build` param com uma
  mensagem curta.
- **DX-4 (médio). Três arquivos de página não se refazem** (T-6).

---

## 7. Governança (só as lacunas)

- **GOV-1 (médio). O registro público de decisões para em D154.**
  - O código, as specs e os pull requests já citam D155 a D162: D157 o staging, D158 o Apoie, D160 os links do Início, D161 o
    fecho da limpeza, D162 o Apoie ligado.
  - `grep` de cada um em `docs/decisions/README.md`: 0.
  - O registro público sai de `publish-decisions.py` a partir de `private/decisions-original.md`, fora do git, então só a sessão
    local o atualiza.
- **GOV-2 (baixo). `CODEOWNERS` tem um dono para tudo** (`* @VitorPChaves`, fase 0 do `GOVERNANCE.md`). Não há donos por área.
- **GOV-3 (baixo). Sem documento de triagem.**
  - As etiquetas existem: `area:*`, `difficulty:*`, `uf:*`, `needs-source`, `method-change`, `good first issue`.
  - Não há etiqueta de entrada (`needs-triage`) nem regra de quem faz a triagem e em quanto tempo.
- **GOV-4 (baixo). Uma versão só, v1.0.0 (2026-10-22), sem `CHANGELOG`.** Do #45 ao #54, mudanças que o visitante vê foram ao ar
  sem nota de versão.

---

## Verificado

- Os valores do DF na página, ao centavo, nos 102 períodos (seção 1.2), com o controle.
- A igualdade dos 27 estados mais a União com o total oficial, nos 100 períodos completos, e a igualdade do total oficial entre os
  dois arquivos.
- As diferenças mensais da seção 1.4, com o controle de R$ 1.
- A conferência da Rede do dinheiro, falhando nos 100 períodos, e a mensagem na página montada.
- Os dois valores do DF no mesmo modal (texto visível).
- As URLs das três páginas (4.005), os links que cada página mostra (navegador), as datas de leitura dos 89 arquivos.
- A reconstrução das páginas de um clone limpo e os tempos.
- As configurações de segurança da seção 5.

## Não verificado

| O quê | Por quê | O que foi tentado |
|---|---|---|
| Se as 4.005 URLs de fonte ainda respondem | A política de rede desta sessão nega os hosts, com 403 ao CONNECT: `www.gov.br`, `www.camara.leg.br`, `dadosabertos.camara.leg.br`, `portaldatransparencia.gov.br`, `www.tesourotransparente.gov.br`, `apisidra.ibge.gov.br`, `legis.senado.leg.br`, `www.planalto.gov.br`, `web.archive.org`, `commons.wikimedia.org` | `curl` com agente de navegador e o estado do proxy. A proposta é rodar a checagem no GitHub Actions (spec, C3) |
| O valor de cada número contra o arquivo oficial de origem (o centavo do CSV da Receita, do Portal, do Tesouro) | Os mesmos hosts | A conta foi refeita a partir de `data/`, que é o que o repositório traz |
| A reconstrução de `tres-poderes-r3-data.js`, `dinheiro-r1-data.js` e `bi-ledger-interest.js` | Precisam de `data/federal/raw-pay/` e de `data/ledger/ledger.duckdb`, fora do git, e o livro baixa as fontes | Os três construtores rodados (erros na seção 2.2, T-6) |
| `npm run check` e `npm run build` do site em Astro | Node 22.22.0 nesta sessão; o repositório pede 24 | O `ci` roda os dois com Node 24 e está verde |
| As configurações da organização (dois fatores, regras da organização), as permissões padrão do token do Actions e os alertas abertos (Dependabot, CodeQL, segredos) | A API desta sessão responde 403 a esses caminhos ("sessions are bound to their configured repositories", "Resource not accessible by integration") | `gh api` só de leitura |
| O site no ar | `brasil-imposto.github.io` está fora do alcance desta sessão (403) | A página foi montada da `main` com os construtores e servida localmente |

---

## Apêndice A. `page-df.cjs` (a conta da página)

```js
// Runs the published page's own code (periods.js, serieslayer.js) over its own data bundle (assets/bi-data.js) and prints,
// for every period the selector offers, every DF figure the map shows.
// Usage: node page-df.cjs <assets folder> <out.json>
const fs = require('fs'), vm = require('vm'), path = require('path');
const [dir, out] = process.argv.slice(2);
const ctx = { window: {}, console };
ctx.window.window = ctx.window;
vm.createContext(ctx);
for (const f of ['bi-data.js', 'periods.js', 'serieslayer.js']) vm.runInContext(fs.readFileSync(path.join(dir, f), 'utf8'), ctx, { filename: f });
const W = ctx.window, BIT = W.BIT, BIL = W.BIL, U = W.BI.series.union;
const latest = U.latest.nominal_result;
const periods = [];
for (const m of W.BI.series.federal_by_uf_monthly.months) if (m <= latest) periods.push({ mode: 'month', month: m });
for (let y = 2019; y <= +latest.slice(0, 4); y++) periods.push({ mode: 'year', year: y });
for (const k of ['2019-2022', '2023-2026']) periods.push({ mode: 'mandate', mandate: k });
const UFS = Object.keys(W.BI.series.federal_by_uf_monthly.uf);
const res = { latest, periods: {} };
for (const p of periods) {
  const r = BIT.resolve(p, latest);
  const key = p.mode === 'month' ? `month:${p.month}` : p.mode === 'year' ? `year:${p.year}` : `mandate:${p.mandate}`;
  const df = BIL.federalAt('DF', r);
  const all = Object.fromEntries(UFS.map((u) => { const f = BIL.federalAt(u, r); return [u, { sent: f.sent, sentRegistered: f.sentRegistered, received: f.received, ok: f.ok, months: f.months }]; }));
  res.periods[key] = { r_months: r.months, df: { ...df, fedSpendingParts: undefined }, all };
}
fs.writeFileSync(out, JSON.stringify(res));
```

Comandos: os quatro construtores do README; `node page-df.cjs docs/superpowers/previews/assets page-df.json`;
`python3 -I df_recompute.py <repositório> page-df.json` (0 diferenças nos valores do DF; sai com 1 por causa de DF-4 e da seção
1.4); `python3 -I df_recompute.py <repositório> page-df.json --plant cofins` (o controle).

## Apêndice B. `df_recompute.py` (a conta independente)

O controle (`--plant TAX`) soma R$ 1 a um imposto do DF no primeiro mês registrado fora da estimativa.

```python
"""Independent recomputation of every DF figure of the map (trust audit, 2026-10-23).

Reads only data/ (never the page's bundle or its JavaScript) and applies the rules as the decisions write them:
  - sent: the federal revenue the Receita registers in the DF, month by month, with the estimate of
    data/series/federal-revenue-uf-estimated.json in the months it covers (the Receita's broken UF split);
  - the DF cap (D146): in each tax the DF counts at most its share of Brazil's GDP (data/df/gdp-share.json) of that tax in the
    27 states; the excess leaves the DF and lands in the União block (official total minus the 27 states);
  - received: transfers, Bolsa Família, INSS, BPC, the FCDF and the federal spending in the DF by the two-step rule
    (data/series/federal-spending-two-step-by-uf.json: executive + other branches + central benefits localized, plus the
    MTE's yearly unemployment insurance and wage bonus for a whole year inside the period); counted only when every month of
    the period has it;
  - the period ends at the last month every component has (per state), and the months the two-step file marks broken leave
    both sides.
Every sum is a Decimal of the JSON's own digits. Compares with the page's figures (page-df.json, written by page-df.cjs) to the
cent and checks that, in every period, the 27 states plus the União block still equal the official total after the move.

Usage: python3 df_recompute.py <repo> <page-df.json> [--plant TAX]   (--plant adds R$ 1 to one DF tax in one month: the check
must then fail)
"""
import json
import sys
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

repo, page_path = Path(sys.argv[1]), Path(sys.argv[2])
plant = sys.argv[sys.argv.index("--plant") + 1] if "--plant" in sys.argv else None
load = lambda p: json.loads((repo / p).read_text(encoding="utf-8"), parse_float=Decimal)
F = load("data/series/federal-by-uf-monthly.json")
E = load("data/series/federal-revenue-uf-estimated.json")
TS = load("data/series/federal-spending-two-step-by-uf.json")
G = load("data/df/gdp-share.json")
POP = load("data/series/population.json")
page = json.loads(page_path.read_text(encoding="utf-8"))
latest = page["latest"]
UFS = sorted(F["uf"])
assert len(UFS) == 27 and "DF" in UFS
CENT = Decimal("0.01")
cent = lambda x: None if x is None else Decimal(x).quantize(CENT, ROUND_HALF_EVEN)
share = Decimal(G["gdp_df_thousand_reais"]) / Decimal(G["gdp_brasil_thousand_reais"])

FM, EM, TM = F["months"], E["months"], TS["months"]
fi, ei, ti = ({m: i for i, m in enumerate(x)} for x in (FM, EM, TM))
broken = set(TS.get("broken_months") or {})

if plant:  # one real added to one DF tax in its first registered month that the estimate does not replace
    arr = F["uf"]["DF"]["federal_revenue"]["by_tax"][plant]
    j = next(i for i, m in enumerate(FM) if arr[i] is not None and m not in ei)
    arr[j] += 1
    F["uf"]["DF"]["federal_revenue"]["total"][j] += 1


def rev(uf, m, tax=None):
    """Revenue of a state in a month: the estimate where it covers the month, the Receita's file elsewhere."""
    if m in ei:
        src = E["uf"][uf]["total"] if tax is None else E["uf"][uf]["by_tax"].get(tax)
        return None if src is None else src[ei[m]]
    src = F["uf"][uf]["federal_revenue"]["total"] if tax is None else F["uf"][uf]["federal_revenue"]["by_tax"][tax]
    return src[fi[m]]


def last_month(months, get):
    for m in reversed(months):
        if get(m) is not None:
            return m
    return None


def period_months(key):
    mode, v = key.split(":")
    if mode == "month":
        return [v]
    y0, y1 = (int(v), int(v)) if mode == "year" else map(int, v.split("-"))
    return [f"{y}-{m:02d}" for y in range(y0, y1 + 1) for m in range(1, 13) if f"{y}-{m:02d}" <= latest]


def end_of(uf):
    u, t = F["uf"][uf], TS["uf"][uf]
    ends = [last_month(FM, lambda m: rev(uf, m)),
            last_month(FM, lambda m: u["transfers"]["total"][fi[m]]),
            last_month(FM, lambda m: u["inss"][fi[m]]),
            last_month(FM, lambda m: u["bolsa_familia"][fi[m]]),
            last_month(TM, lambda m: t["executive"][ti[m]])]
    return min(ends)


def total(values):
    vals = [v for v in values if v is not None]
    return (sum(vals, Decimal(0)) if vals else None), len(vals)


def state(uf, months_all):
    end = end_of(uf)
    months = [m for m in months_all if m <= end and m not in broken]
    u, t = F["uf"][uf], TS["uf"][uf]
    out = {"months": months}
    sent_reg, n = total(rev(uf, m) for m in months)
    out["sent_registered"], out["sent_complete"] = sent_reg, n == len(months)
    out["by_tax"] = {k: total(rev(uf, m, k) for m in months)[0] for k in u["federal_revenue"]["by_tax"]}
    for k, arr in (("transfers", u["transfers"]["total"]), ("bolsa", u["bolsa_familia"]), ("inss", u["inss"]), ("bpc", u["bpc"])):
        out[k], out[k + "_n"] = total(arr[fi[m]] if m in fi else None for m in months)
    parts = {}
    full = True
    for k in ("executive", "other_branches", "fcdf"):
        parts[k], n = total(t[k][ti[m]] if m in ti else None for m in months)
        full = full and n == len(months) and len(months) > 0
    central = Decimal(0)
    for y in sorted({m[:4] for m in months}):
        ms = [m for m in months if m.startswith(y)]
        mte = TS["mte_annual"].get(y)
        if mte and len(ms) == 12:
            central += mte["uf"][uf]["unemployment_insurance"] + mte["uf"][uf]["wage_bonus"]
        c, _ = total(t["central_benefits_localized"][ti[m]] if m in ti else None for m in ms)
        central += c or 0
    out["two_step_complete"] = full
    out["fcdf"] = parts["fcdf"] if full else None
    out["fed_spending"] = parts["executive"] + parts["other_branches"] + central if full else None
    out["received"] = (out["transfers"] + (out["bolsa"] or 0) + (out["inss"] or 0) + (out["bpc"] or 0) + parts["fcdf"]
                       + out["fed_spending"]) if (out["transfers"] is not None and full) else None
    return out


def df_cap(months):
    """D146, per tax: the DF keeps at most its GDP share of that tax in the 27 states."""
    registered = capped = Decimal(0)
    rows = {}
    for k in F["uf"]["DF"]["federal_revenue"]["by_tax"]:
        df = total(rev("DF", m, k) for m in months)[0] or Decimal(0)
        br = sum((total(rev(uf, m, k) for m in months)[0] or Decimal(0) for uf in UFS), Decimal(0))
        keep = min(df, share * br)
        rows[k] = {"df": df, "brazil": br, "cap": share * br, "kept": keep, "excess": df - keep}
        registered += df
        capped += keep
    return registered - capped, rows


def pop_of(uf, years):
    by = {int(y): v for y, v in POP["uf"][uf]["population"].items() if v is not None}
    want = years[-1]
    y = sorted(by, key=lambda y: (abs(y - want), -y))[0]
    return by[y]


report = {"periods": 0, "df_ok": 0, "fields_compared": 0, "gaps": [], "union_checks": 0, "union_gaps": [], "tax_sum_gaps": [],
          "cap_rows": {}, "share": str(share), "plant": plant}
for key, P in page["periods"].items():
    report["periods"] += 1
    months_all = period_months(key)
    assert months_all == P["r_months"], (key, "period months differ from the page's selector")
    S = {uf: state(uf, months_all) for uf in UFS}
    d = S["DF"]
    ok = (len(d["months"]) > 0 and d["sent_complete"] and d["transfers_n"] == len(d["months"]) and d["two_step_complete"]
          and not [m for m in d["months"] if m in fi and "broken" in str(F["national"]["federal_revenue_month_status"][fi[m]]) and m not in ei])
    excess, rows = df_cap(d["months"]) if d["sent_registered"] is not None else (None, {})
    sent = d["sent_registered"] - excess if excess is not None else None
    balance = sent - d["received"] if ok else None
    years = sorted({int(m[:4]) for m in months_all})
    pop = pop_of("DF", years)
    mine = {"sent": sent, "sentRegistered": d["sent_registered"], "excess": excess, "received": d["received"],
            "transfers": d["transfers"], "bolsa": d["bolsa"], "inss": d["inss"], "bpc": d["bpc"], "fcdf": d["fcdf"],
            "fedSpending": d["fed_spending"], "balance": balance, "months": len(d["months"]), "ok": ok,
            "perPersonMonth": balance / pop / len(d["months"]) if ok else None}
    theirs = dict(P["df"])
    theirs["excess"] = (P["df"].get("dfEstimate") or {}).get("excess")
    report["df_ok"] += bool(ok)
    for f, v in mine.items():
        t = theirs.get(f)
        report["fields_compared"] += 1
        if f in ("ok", "months"):
            if v != t:
                report["gaps"].append([key, f, str(v), str(t)])
            continue
        if f == "perPersonMonth":
            a, b = (None if v is None else v.quantize(Decimal("0.0001"))), (None if t is None else Decimal(repr(t)).quantize(Decimal("0.0001")))
        else:
            a, b = cent(v), cent(Decimal(repr(t)) if t is not None else None)
        if a != b:
            report["gaps"].append([key, f, str(a), str(b)])
    for k, v in (P["df"].get("byTax") or {}).items():
        report["fields_compared"] += 1
        if cent(d["by_tax"][k]) != cent(Decimal(repr(v)) if v is not None else None):
            report["gaps"].append([key, f"byTax.{k}", str(cent(d["by_tax"][k])), str(v)])
    # the taxes of the DF add up to what the Receita registers there (the page shows the total, the cards each tax)
    if d["sent_registered"] is not None:
        st = sum((v or 0 for v in d["by_tax"].values()), Decimal(0))
        if cent(st) != cent(d["sent_registered"]):
            report["tax_sum_gaps"].append([key, str(cent(st)), str(cent(d["sent_registered"]))])
    # the União block after the move: 27 states (DF capped) + União = official total; the excess moved, nothing else
    if ok and all(S[u]["months"] == d["months"] and S[u]["sent_registered"] is not None for u in UFS):
        ms = d["months"]
        official = total(TS["union"]["official_revenue"][ti[m]] for m in ms)[0]
        states_reg = sum((S[u]["sent_registered"] for u in UFS), Decimal(0))
        states_capped = states_reg - excess
        union_before, union_after = official - states_reg, official - states_capped
        report["union_checks"] += 1
        if cent(states_capped + union_after) != cent(official) or cent(union_after - union_before) != cent(excess) or union_after < 0:
            report["union_gaps"].append([key, str(cent(official)), str(cent(states_capped)), str(cent(union_after)), str(cent(excess))])
        # the official total of the Receita file vs the two-step file's official revenue (two copies of the same number)
        rf = total(F["national"]["federal_revenue_total_receita"][fi[m]] for m in ms)[0]
        if cent(rf) != cent(official):
            report["union_gaps"].append([key, "official differs between files", str(cent(rf)), str(cent(official))])
    if key in ("year:2024", "year:2025", "mandate:2023-2026", "month:2026-08"):
        report["cap_rows"][key] = {k: {x: str(cent(y)) for x, y in v.items()} for k, v in rows.items()}
# Month by month, outside the União identity (which holds by construction): the 27 states as the Receita registers them add up
# to the file's own sum of the states, and that sum plus what no state received equals the Receita's national total. In the
# estimated months the 27 states are the estimate, which says it is scaled to the national total.
N = F["national"]
report["monthly_official"] = {"months": 0, "gaps": []}
for m in FM:
    tot, sou, na = N["federal_revenue_total_receita"][fi[m]], N["federal_revenue_sum_of_ufs"][fi[m]], N["federal_revenue_not_attributed_to_any_uf"][fi[m]]
    if tot is None:
        continue
    report["monthly_official"]["months"] += 1
    s27 = sum((F["uf"][u]["federal_revenue"]["total"][fi[m]] or 0 for u in UFS), Decimal(0))
    if cent(s27) != cent(sou):
        report["monthly_official"]["gaps"].append([m, "27 states (file) vs sum_of_ufs", str(cent(s27)), str(cent(sou))])
    if na is not None and cent(sou + na) != cent(tot):
        report["monthly_official"]["gaps"].append([m, "sum_of_ufs + not attributed vs national", str(cent(sou + na)), str(cent(tot))])
    if m in ei:
        se = sum((E["uf"][u]["total"][ei[m]] or 0 for u in UFS), Decimal(0))
        report["monthly_official"].setdefault("estimate", []).append([m, str(cent(se)), str(cent(sou)), str(cent(tot))])
print(json.dumps({k: (v if k != "cap_rows" else "...") for k, v in report.items()}, ensure_ascii=False, indent=1)[:6000])
(Path(page_path).parent / ("recompute-plant.json" if plant else "recompute.json")).write_text(json.dumps(report, ensure_ascii=False, indent=1))
sys.exit(1 if report["gaps"] or report["union_gaps"] or report["tax_sum_gaps"] or report["monthly_official"]["gaps"] else 0)
```
