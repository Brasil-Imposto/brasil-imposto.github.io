# Fase 1, complemento: arquitetura dos dados, proveniência, método das contas, DF e integração das páginas (2026-10-24)

Issue #66. Completa a auditoria de confiança de 2026-10-23 (#55, `BRASIL-IMPOSTO_RESEARCH_auditoria-confianca_2026-10-23.md`),
que já entregou:
- os problemas por gravidade;
- os testes executados;
- as questões abertas;
- o plano.

Este documento cobre os itens que faltavam do pedido da Fase 1: 1, 2, 4 e 5, e a seção 5 do pedido (o método das contas).

Toda afirmação sobre o comportamento vem do código lido nesta sessão, com o arquivo e a função citados.
- **Comprovado:** está no código ou no arquivo de dados.
- **Calculado:** saiu de um script incluído aqui.
- **Não comprovado:** o dado ou o código não sustenta; fica como lacuna.

Nada na tela nem nos dados publicados mudou neste trabalho.

## 1. Arquitetura atual dos dados

O caminho é o mesmo para todas as páginas, com cinco camadas:

| Camada | Onde | O que faz |
|---|---|---|
| Fonte oficial | Receita Federal, CGU (Portal da Transparência), Tesouro (RTN, SICONFI, Tesouro Transparente), MDS, Previdência (BEPS, AEPS), IBGE, Banco Central, Câmara, Senado, tribunais | Publica os arquivos |
| Coleta e tratamento | `pipelines/` (Python 3.12, `uv.lock`) | Baixa, lê e agrega. Os brutos não ficam no repositório (`.gitignore`); só o resultado tratado |
| Dados tratados | `data/` (90 arquivos JSON; a família de séries em `data/series/`) | Cada arquivo diz as suas fontes (84 de 90) e a data de coleta (62 de 90) |
| Pacote da página | `docs/superpowers/tools/build-standalone-data.py` grava `assets/bi-data.js` (e `bi-federal.js`); outros construtores gravam os pacotes de Os 3 Poderes e de Como o dinheiro anda | Junta os arquivos de `data/` que a página usa. A tabela `SERIES_WRITERS` diz o script que faz cada série |
| Cálculo na tela | `assets/serieslayer.js` (`BIL`), `assets/periods.js` (`BIT`), `assets/map-notes-model.js` (`BIMN`), `assets/federal-section.js`, o script de cada página | O saldo de cada estado e de cada período é calculado no navegador, a partir das séries mensais |

As famílias de dados e as páginas que as usam:

| Família | Arquivos | Script | Página |
|---|---|---|---|
| Saldo federal por UF, mensal | `data/series/federal-by-uf-monthly.json`, `federal-spending-two-step-by-uf.json`, `federal-revenue-uf-estimated.json`, `population.json`, `data/df/gdp-share.json` | `pipelines/series/build_federal_by_uf_monthly.py`, `pipelines/ug/build_two_step_series.py`, `pipelines/series/estimate_uf_revenue.py`, `pipelines/series/build_population.py`, `pipelines/df/fetch_gdp_share.py` | Início (mapa, modal do estado) |
| Contas da União | `data/series/union.json`, `union-spending-slices.json`, `public-sector-primary.json` | `pipelines/series/build_union_series.py`, `pipelines/federal/build_spending_slices.py`, `pipelines/series/fetch_public_sector_primary.py` | Início (A conta da União, Para onde vai), Como o dinheiro anda (O governo federal) |
| Orçamentos estaduais e municipais | `data/series/state-budgets.json`, `sc-*`, `rs-*` | `pipelines/series/build_state_series.py`, `build_municipal_*.py` | Início (modal do estado e dos municípios de SC e RS) |
| Pessoal federal | `data/series/federal-payroll-by-uf.json`, `data/federal/federal-section.json`, `data/federal/servants-by-branch.json` | `pipelines/series/build_federal_payroll_by_uf.py`, `pipelines/federal/build_federal_section.py`, registro transcrito à mão (sem script) | Início (nota do FCDF), Como o dinheiro anda (O governo federal) |
| Os 3 Poderes | `data/federal/{judiciary,senate,executive,presidency,officeholders,positions}-2026.json`, `data/politicians/*` | `docs/superpowers/tools/collect-*.py`, `build-tres-poderes-*.py` | Os 3 Poderes |
| Fluxo do dinheiro (2025) | `assets/dinheiro-r1-data.js` | `docs/superpowers/tools/build-dinheiro-r1-data.py` (RTN 2025 e RREO dos 27 estados, mais as regras da Constituição) | Como o dinheiro anda |
| Comércio exterior, casos, Rede | `data/trade/`, `data/cases/`, `data/ledger/` | `pipelines/trade/`, `build-cases.py`, `pipelines/ledger/` | Início (staging), casos, Rede do dinheiro |

Achado de arquitetura (A-1, médio):
- o cálculo do saldo vive no navegador (`serieslayer.js`);
- os testes em Python conferem os dados, e a página é conferida por sondas de navegador fora do `ci`;
- o item A1 da spec de confiança põe o saldo do DF no `ci`, e B1 os 27 estados.

## 2. Proveniência dos indicadores principais

O apêndice `docs/research/fase-1-complemento-2026-10-24/provenance.json` tem um registro por indicador, com os campos do pedido.
O resumo:

| Indicador (tela) | Chave | Fórmula (código) | Fontes | Coleta | Lacunas |
|---|---|---|---|---|---|
| Enviou (por estado) | `BIL.federalAt().sent` | Arrecadação da Receita por UF, somada no período; nos meses da quebra de 2025, a estimativa (`federal-revenue-uf-estimated`); no DF, o teto pelo PIB (D146) | Receita, Arrecadação por Estado (CSV mensal) | 2026-09-30 | A data de coleta é do arquivo inteiro, não de cada mês |
| Voltou (por estado) | `.received` | Transferências (Portal) + Bolsa Família + INSS + BPC + FCDF + gasto federal pela regra em duas etapas | CGU (Portal, Transferências e Execução da Despesa), MDS, BEPS, Tesouro Transparente | 2026-09-30 e 2026-10-02 | `federal-spending-two-step-by-uf.json` não tem campo de fonte, só `built_from` (os arquivos de `data/ug/`) |
| Saldo | `.balance` | Enviou menos Voltou, só quando os dois lados estão completos no período (`ok`) | as duas acima | | |
| Por habitante, por mês | `.perPersonMonth` | Saldo / população / meses do período | IBGE (estimativas; 2022 do Censo; 2023 sem valor) | | A população de 2023 é nula no arquivo; o código usa a regra de `popOf` |
| Proporção | `VALUE.ratio` em `map-notes-model.js` | log(Enviou / Voltou), para a cor | as acima | | |
| Estimativa do DF | `.dfEstimate.excess` | Por tributo, o DF conta no máximo 3,34% do total dos 27 estados (a parte do DF no PIB de 2023); o excesso vai para a União | IBGE, PIB dos Municípios (SIDRA 5938, lido em 2026-10-21) | 2026-10-21 | Um ano de PIB (2023) para todos os períodos (pergunta DF-5) |
| Bloco da União | `BIMN.unionAt` | Total oficial menos os 27 estados, nos dois lados | Receita (total nacional), Tesouro (RTN) | 2026-09-30 | Recomputado na auditoria de 2026-10-23 |
| A conta da União | `union.json` | RTN tabela 1.1 e Banco Central (juros nominais) | Tesouro (RTN), Banco Central | 2026-09-30 | |
| Pessoal pago pela União | `federal-section.json` | Pago mais restos a pagar pagos, grupo 1, modalidade 90 (o critério do RTN 1.5) | Portal da Transparência; base do Tesouro | 2026-10-02 | Valor bruto (com IR e PSS retidos) |
| Remuneração média por tribunal | `data/federal/judiciary-2026.json` | Médias das folhas de janeiro a agosto de 2026, pelas regras do D154 | Portais de transparência dos tribunais | 2026-10-21 | Ver a auditoria do Judiciário (#38, #40, #41) |
| Fluxo de 2025 | `dinheiro-r1-data.js` | RTN 2025 e RREO dos 27 estados | Tesouro (RTN, SICONFI), Constituição | 2026-10-21 | O pacote é gerado, mas os arquivos de entrada estão fora de `data/` (C5 da spec de confiança) |

Achado P-1 (médio): 6 dos 90 arquivos de `data/` não têm chave de fonte. Um deles é `data/features.json`, que é de configuração
e não precisa.

Achado P-2 (médio):
- `federal-spending-two-step-by-uf.json`, que compõe a maior parte do "Voltou", não diz a fonte no próprio arquivo, só os arquivos
  de que foi feito;
- a fonte está nesses arquivos (`data/ug/`) e no código, não no arquivo publicado;
- é o item C2 da spec de confiança.

## 3. Método das contas públicas, como o código faz hoje

| Termo | Definição no código | Onde |
|---|---|---|
| Arrecadação atribuída à UF ("Enviou") | O que a Receita Federal registra na UF, que é onde fica o estabelecimento que recolhe. Não é onde mora quem paga. Valores correntes, sem correção pela inflação. Só tributos administrados pela Receita | `federal-by-uf-monthly.json`, `sources[0]`; `serieslayer.js` |
| Transferência recebida | Toda transferência da União ao estado, às prefeituras e a entidades na UF, pela coluna "valor transferido" do Portal. Inclui FPE, FPM, Fundeb e repasses voluntários | `federal-by-uf-monthly.json`, `uf.*.transfers`; `pipelines/series/classify_transfers.py` |
| Gasto federal territorial | Gasto direto da União pela UF do localizador do orçamento. Sem localizador, fica com a União (D114), salvo a folha dos ex-territórios (AP, RO, RR). Os outros Poderes vão pela sede da unidade. Seguro-desemprego e abono vão pela UF do localizador ou do MTE (anual). Juros e amortização ficam fora | `federal-spending-two-step-by-uf.json`, `rule`; `serieslayer.js`, `twoStepAt` |
| Benefícios a pessoas | INSS (BEPS, UF do pagamento), Bolsa Família e BPC (MDS, soma dos municípios) | `federal-by-uf-monthly.json` |
| FCDF | Contado como "Voltou" do DF | `twoStepAt`, `fcdf` |
| Saldo | Enviou menos Voltou, no mesmo conjunto de meses. Um mês com o arquivo do Portal quebrado (2025-06) sai dos dois lados. O saldo só aparece com os dois lados completos | `federalAt` |
| Níveis de governo | Só a União. O que o estado e as prefeituras arrecadam e gastam fica no modal, em separado (RREO), e não entra no saldo | `stateAt` |
| Per capita | Saldo / população da UF no período / número de meses | `federalAt`, `perPersonMonth` |
| Juros e dívida | Fora do saldo por UF (regra acima). Aparecem só na conta da União (RTN e Banco Central) | `union.json` |
| Previdência | O INSS que a UF recebe entra no "Voltou"; as contribuições previdenciárias entram no "Enviou" pela Receita | as duas fontes acima |

Dupla contagem: onde ela poderia acontecer e o que o código faz.

| Risco | O que o código faz | Situação |
|---|---|---|
| A mesma transferência no "Voltou" do estado e no gasto federal | As transferências entram pelo arquivo de transferências; a regra em duas etapas tira as transferências e os benefícios do gasto (eles vão "por destino") | Comprovado na regra do arquivo (`rule`: transferências e benefícios "por destino", fora do gasto); um teste que confira a separação mês a mês ainda não existe (seção 5.2, item 3) |
| Fundeb contado na transferência e no gasto do estado | O saldo é só federal; o Fundeb do estado só aparece no modal do RREO | Comprovado; não entra no saldo |
| Folha federal no "Voltou" e o IR e o PSS dessa mesma folha no "Enviou" | A folha é bruta (`value_definition`). O IR e o PSS retidos são recolhidos pelo órgão que paga e a Receita os registra onde esse órgão está, em geral no DF | Não é dupla contagem: são dois fluxos reais. Mas parte do "Enviou" do DF é imposto de servidores que moram em todo o país; o teto do DF reduz isso, sem separar |
| O gasto dos outros Poderes pela sede | Câmara, Senado, STF e tribunais superiores contam no "Voltou" do DF, mesmo pagando pessoas de outros estados (deputados, senadores) | Comprovado na regra; não é dupla contagem, é uma escolha de atribuição que favorece o DF |

## 4. Distrito Federal: método atual, alternativas e efeito

### 4.1 O que o código faz hoje

Comprovado em `serieslayer.js`, `dfCapped` e `federalAt`:

1. **Enviou:** a arrecadação que a Receita registra no DF. Em cada tributo, o DF conta no máximo 3,34% do total dos 27 estados
   (a parte do DF no PIB de 2023, IBGE). O excesso sai do DF e vai para o bloco da União (D146). Em 2025-02 a 2026-01 a Receita
   lançou no DF parte do que foi pago em outros estados (a quebra); nesses meses vale a estimativa por estado, ajustada ao total
   nacional.
2. **Voltou:** soma de:
   - as transferências da União ao DF;
   - Bolsa Família, INSS e BPC no DF;
   - o FCDF;
   - o gasto federal localizado no DF, inclusive os Poderes com sede em Brasília.
3. **Observado e estimado:**
   - observados: o "Voltou" inteiro e o "Enviou" registrado;
   - estimados: o teto do DF em todos os meses e a divisão por estado nos meses da quebra.
4. **Períodos:**
   - o saldo usa só os meses em que todos os lados estão publicados;
   - 2025-06 sai dos dois lados.

### 4.2 Alternativas calculadas

Script: `docs/research/fase-1-complemento-2026-10-24/df_alternatives.cjs`, sobre os dados do mapa e as funções do próprio mapa.
Saída: `df_alternatives.json`. Controle: com o teto em 100%, o saldo com teto é igual ao saldo sem teto em todos os períodos. Com
o teto em 5%, que corta, o controle falha como deve.

Valores em R$ bilhões correntes; saldo = Enviou menos Voltou (negativo: recebe mais do que envia).

| Período | Voltou | Enviou registrado | (a) Sem teto | (b) Teto pelo PIB de 2023, hoje | (c) Teto pela população |
|---|---|---|---|---|---|
| 2019 | 66,6 | 118,9 | 52,4 | -26,2 | -46,6 |
| 2020 | 68,4 | 118,4 | 50,1 | -24,3 | -49,0 |
| 2021 | 68,3 | 137,5 | 69,2 | -13,2 | -44,0 |
| 2022 | 73,8 | 158,6 | 84,8 | -8,5 | -46,3 |
| 2023 | 83,2 | 166,7 | 83,5 | -14,2 | -53,6 |
| 2024 | 91,3 | 184,1 | 92,8 | -8,7 | -56,2 |
| 2025 | 84,7 | 185,9 | 101,2 | -3,1 | -49,7 |
| 2026 (jan. a ago.) | 58,9 | 116,7 | 57,8 | -3,9 | -35,3 |
| Mandato 2019 a 2022 | 277,0 | 533,5 | 256,5 | -66,6 | -187,2 |
| Mandato 2023 a 2026 (até ago.) | 318,1 | 653,4 | 335,3 | -29,2 | -192,6 |

Notas:
- O teto pela população usa a parte do DF na população do ano (1,39% a 1,45%). O teto pelo PIB usa 3,34%.
- "Enviou registrado" de 2025 e de janeiro de 2026 já usa a estimativa por estado nos meses da quebra (`withEstimate`), como a tela.
- O excesso que sai do DF entra no bloco da União; o saldo do país não muda.

Leitura:
- **O sinal do saldo do DF depende do método.** Sem teto, o DF envia mais do que recebe em todos os anos. Com o teto pelo PIB, que
  é o que a tela mostra hoje, ele recebe mais do que envia. Com o teto pela população, recebe muito mais. Nenhum dos três é "o
  certo" com os dados abertos de hoje: nenhum arquivo aberto separa o imposto retido em Brasília pela UF de quem paga.
- O teto pelo PIB é o mais defensável dos três: usa uma base econômica, não demográfica, e é o que o D146 decidiu. A população ignora a diferença de renda: a parte do DF no PIB
  (3,34%) é mais que o dobro da parte na população (1,39% a 1,45%), pelos dois arquivos do IBGE usados aqui.
- O saldo do DF com teto pelo PIB foi de -26,2 em 2019 a -3,1 em 2025. A queda acompanha o "Enviou" registrado, que subiu de
  118,9 a 185,9, mais rápido que o "Voltou". A tela não explica essa tendência.

### 4.3 Alternativas que os dados de hoje não permitem calcular

| Alternativa | O que falta | Pergunta |
|---|---|---|
| (d) PIB de cada ano em vez do de 2023 | A série do PIB dos municípios para 2019 a 2022 e as edições futuras: a tabela 5938 do SIDRA tem, o pipeline lê só o último ano | DF-5, já aberta |
| (e) Tirar do "Enviou" do DF o IR e o PSS retidos da folha federal paga a quem mora em outra UF | O valor retido por UF de residência; o Portal só dá a folha bruta | Nova (Q-C-1) |
| (f) Contar o gasto dos outros Poderes pela UF de quem recebe, não pela sede | A UF de cada deputado e senador está em `data/politicians/`, mas o gasto da Câmara e do Senado não vem separado por parlamentar em nenhum arquivo do projeto; os tribunais não têm UF de origem | Nova (Q-C-2) |

### 4.4 Recomendação

Recomendações, sem mudar a tela agora:
- manter (b);
- mostrar no painel do DF os três valores, (a), (b) e (c), como faixa, com a frase de que o sinal depende do método (é a pergunta
  Q-A3 da spec de confiança, que este quadro informa);
- implementar (d) quando o pipeline ler os outros anos do PIB.

## 5. Integração entre as páginas

### 5.1 O que liga as páginas hoje, e o que é comprovável

| Ligação | Comprovável? | Como |
|---|---|---|
| O "Voltou" do mapa contém a folha federal | Sim | A regra em duas etapas põe a folha do Executivo (pelo localizador) e a dos outros Poderes (pela sede) no gasto federal por UF |
| "Pessoal pago pela União" (Como o dinheiro anda) e a despesa com pessoal da conta da União (RTN 4.2) | Sim, com escopo diferente | O primeiro é grupo 1, modalidade 90, pago mais restos a pagar (critério do RTN 1.5); o RTN 4.2 é a linha da conta. Os dois não somam: o primeiro é parte do segundo, com recortes diferentes. A reconciliação está em `federal-section.json` (`check`) |
| A remuneração individual dos 3 Poderes e a despesa com pessoal | Em parte | Cada salário de um ministro do STF, de um deputado ou de um senador está dentro do grupo 1 do órgão, que está dentro do "Pessoal pago pela União" e do "Voltou" do DF. Não somar: a remuneração individual já está contada no agregado |
| A remuneração individual e o "Enviou" | Em parte | O IR e o PSS retidos desses salários estão no "Enviou" da UF onde o órgão recolhe (em geral o DF) |
| Os 3 Poderes e o mapa por estado | Não hoje | Os deputados e senadores são de um estado, mas o gasto da Câmara e do Senado conta no DF. Ligar exigiria a alternativa (f) |
| A conta da União e o bloco da União no mapa | Sim | O bloco do mapa é o total oficial menos os 27 estados; a conta da União é o RTN. Medem coisas diferentes (atribuição territorial e resultado do governo central) e não devem ser apresentadas como iguais |

### 5.2 Proposta de arquitetura

A proposta liga as páginas sem dependência artificial e sem forçar um modelo único:

1. **Catálogo de indicadores** (`data/indicators.json`, item P3 da spec da Fase 2). Para cada indicador:
   - identificador estável;
   - definição;
   - unidade;
   - natureza (individual, agregado, estimado);
   - fontes;
   - arquivo e chave;
   - páginas que o mostram.

   O catálogo usa os registros de `provenance.json` como ponto de partida.
2. **Relações explícitas no catálogo**, com três tipos:
   - `part_of`: a remuneração de um cargo é parte da despesa de pessoal do órgão, que é parte do gasto federal no DF;
   - `same_flow_as`: o IR retido da folha e o "Enviou" do DF;
   - `differs_in_scope_from`: "Pessoal pago pela União" e o RTN 4.2.

   Uma página pode mostrar "faz parte de", mas um teste impede somar indicadores ligados por `part_of`.
3. **Testes de integração** (item 6 do pedido; A1, A4 e B1 da spec de confiança):
   - o mesmo número em duas páginas vem da mesma chave;
   - um indicador `part_of` nunca supera o seu todo no mesmo período e escopo;
   - o saldo do DF e dos 27 estados é recomputado no `ci`.
4. **Navegação:** de cada indicador para a sua definição (a página Definições, P4) e para as fontes, com o período e a medida,
   como a página Como ler o mapa já faz.

## 6. O que foi implementado nesta sessão

- Este relatório e o apêndice de proveniência (`provenance.json`).
- O script das alternativas do DF, com a saída e o controle. É evidência de pesquisa, não entra no site nem no `ci`.
- Nenhuma mudança nos dados publicados, na tela, nos testes do `ci` ou nos workflows.

Os testes do item 6 (A1, A4, B1, dupla contagem e consistência entre páginas) são os próximos pull requests, um por item, pela
spec de confiança aprovada.

## 7. Questões abertas novas

- **Q-C-1:** separar do "Enviou" do DF o IR e o PSS retidos da folha de quem mora em outra UF. Não há dado aberto por UF de
  residência. Manter como limitação escrita?
- **Q-C-2:** o gasto da Câmara e do Senado por UF do parlamentar, em vez da sede (alternativa (f)): vale uma spec própria?
- **Q-C-3:** mostrar no painel do DF a faixa dos três métodos (seção 4.4), junto com Q-A3?

## 8. Plano para os próximos passos

1. Os testes A1, A4 e B1 da spec de confiança, um pull request cada.
2. O catálogo de indicadores (P3 da spec da Fase 2), a partir de `provenance.json`.
3. As respostas a Q-C-1 a Q-C-3 e às perguntas já abertas (Q-A2, Q-A3, Q-A4, Q-C1, Q-B3, DF-5).
4. O pipeline do PIB com todos os anos (alternativa (d)).

## In English

Phase 1 complement, covering what the 2026-10-23 trust audit left open:
- the data architecture;
- provenance for each main indicator, with a JSON appendix;
- the public-accounts methodology as the code implements it, including where double counting could happen and why it does not;
- the DF methodology with three computed alternatives;
- how the pages relate and a proposed architecture linking them.

Key finding: the sign of the DF balance depends on the method. With no cap the DF sends more than it receives in every year; with
the GDP cap the site uses today (D146) it receives more than it sends; with a population cap it receives far more. No open dataset
separates tax withheld in Brasília by the payer's state, so the limitation is stated rather than hidden. Nothing on screen
changed.
