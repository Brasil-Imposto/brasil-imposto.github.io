# Séries federais por mês: arrecadação, transferências, Bolsa Família e INSS por UF, e municípios de SC (2019 a 2026)

**Data da coleta:** 2026-09-30
**Arquivos de dados:** `data/series/federal-by-uf-monthly.json`, `data/series/sc-municipal-federal.json`, `data/series/population.json`
**Scripts:** `pipelines/series/` (ordem de execução na seção 8)
**Regra seguida:** nenhum número estimado. Tudo foi somado a partir de arquivos oficiais; onde não há fonte, o valor é `null` e o motivo está no próprio JSON (`flags`, `coverage`, `null_reasons`). Valores em reais correntes, sem correção pela inflação.

---

## 0. Resumo em uma tela

| Série (chave no JSON) | Recorte | Primeiro | Último publicado | Fonte |
|---|---|---|---|---|
| Arrecadação federal, total e por tributo (`federal_revenue`) | UF, mensal | 2019-01 | 2026-07 | Receita Federal |
| Transferências, total, governo estadual, municípios e 18 categorias (`transfers`) | UF, mensal | 2019-01 | 2026-09 (mês incompleto) | Portal da Transparência + Tesouro (LC 176) |
| Bolsa Família ou Auxílio Brasil (`bolsa_familia`) | UF, mensal | 2019-01 | 2026-09 | MDS, MI Social |
| INSS, benefícios do RGPS emitidos (`inss`, `inss_gross_benefit_value`) | UF, mensal | 2019-01 | 2026-08 | BEPS (Previdência) |
| BPC (`bpc`) | UF, mensal | 2019-01 | 2026-08 | MDS, MI Social |
| INSS com BPC (`inss_annual_aeps`) | UF, anual | 2019 | 2024 | AEPS (Previdência) |
| Transferências à prefeitura (`transfers_monthly`) | 295 municípios de SC, mensal | 2019-01 | 2026-09 | Portal da Transparência |
| Bolsa Família ou Auxílio Brasil, BPC (`bolsa_familia_monthly`, `bpc_monthly`) | 295 municípios de SC, mensal | 2019-01 | 2026-09 e 2026-08 | MDS, MI Social |
| Arrecadação federal no município (`federal_revenue_annual`) | 295 municípios de SC, anual | 2019 | 2025 | Receita Federal |
| População | 27 UFs e 295 municípios de SC, anual | 2019 | 2026 (2023 `null`) | IBGE |

| Pergunta | Resposta curta |
|---|---|
| 2024 bate com o balanço já publicado? | **Sim, exatamente.** Arrecadação e transferências de 2024 somadas mês a mês reproduzem `data/uf-balance-2024.json` com diferença de 0,0000% em todas as 27 UFs (cada tributo e cada categoria até R$ 0,1 mi). Os 295 municípios de SC reproduzem `data/sc-municipal-balance-2024.json` com diferença máxima de R$ 0,00 em transferências, Bolsa Família, arrecadação e população. |
| Arrecadação: soma das UFs contra o total nacional | Igual até o centavo de 2019 a 2023. 2024: -0,05% (setembro). 2025: -1,08%. 2026 (jan a jul): -1,67%. |
| 2025 serve para o mapa? | **Não, de fevereiro de 2025 a janeiro de 2026** (12 meses): o DF fica com 14,8% a 25,2% da arrecadação do país (máximo de 2019 a 2024: 10,8%). A partir de fevereiro de 2026 a distribuição volta ao normal, mas 2% a 4% por mês ficam sem UF. Veredito na seção 4. |
| INSS por UF | Mensal, de 2019-01 a 2026-08 (BEPS). Anual 2019 a 2024 (AEPS). |
| INSS ou BPC por município | **BPC: existe e está no arquivo de SC** (MDS, mensal, 2019-01 a 2026-08). **RGPS: existe em microdado aberto do próprio INSS** (sem login, 2021-07 a 2026-07, 0,55 a 1 GB por mês); foi validado para SC em agosto de 2024, mas a série não foi montada (seção 5). |
| brasiltransparente.digital | Projeto comunitário de código aberto (AGPL-3.0) sobre o gasto pago da União em 2025, sem recorte por UF ou município. Não preenche as nossas lacunas geográficas (seção 6). |

---

## 1. Método

### 1.1 Arrecadação federal por UF, mensal

- Fonte: Receita Federal, "Arrecadação por Estado", https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv (mesmo arquivo do relatório de 2024, baixado de novo em 2026-09-30; vai até **julho de 2026**).
- Leitura com as regras de `pipelines/parse_rfb.py` (formatos numéricos misturados) e as chaves de `pipelines/taxmap.py`. `total`, `rfb_administered` e `by_tax` (16 grupos) por UF e mês.
- Total nacional para conferência: série histórica da Receita (XLSX, 1994 a 2025, linha TOTAL GERAL) e, para 2026, a Tabela III da "Análise da Arrecadação das Receitas Federais" de agosto de 2026 (PDF, https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/arrecadacao-federal/2026/analise-mensal-ago-2026.pdf), que traz todos os meses de janeiro de 2021 a agosto de 2026.
- Cada mês recebe um status em `national.federal_revenue_month_status`: `ok`; `uf_attribution_broken` (DF acima de 12% da soma das UFs; de 2019 a 2024 o máximo mensal foi 10,8%, em maio de 2020, quando o adiamento de tributos na pandemia encolheu o total do país); `unattributed_gap` (soma das UFs difere do total nacional em mais de 0,5%); `not_published`.

### 1.2 Transferências federais por UF, mensal

- Fonte: CGU, Portal da Transparência, Transferências, 93 arquivos mensais de 201901 a 202609 (https://portaldatransparencia.gov.br/download-de-dados/transferencias/AAAAMM), sem chave. Cada ZIP foi baixado, somado em streaming e apagado na hora (nunca mais de um mês em disco). A soma de cada mês fica num cache pequeno, com as chaves UF, tipo de transferência, tipo de favorecido, função, ação, modalidade e se há município, o que permite refazer a classificação sem baixar de novo.
- **Classificação: a mesma de `pipelines/build.py`**, escrita linha a linha em `pipelines/series/classify_transfers.py`. Duas extensões, necessárias para 2019 a 2021 e documentadas no código:
  1. **Ação 0E36** ("Complementação da União ao Fundeb", o Fundeb que valeu até 2020) entra em `fundeb_federal_complement`, a mesma categoria da ação 00SB (Fundeb da EC 108/2020). Sem isso, R$ 15,60 bi de 2019 e R$ 12,53 bi de 2020 cairiam em `education_fnde_and_other`.
  2. **"Agentes Intermediários":** o `build.py` admitiu as duas ações de 2024 que têm UF (00VP ao governo do RS, 00WF aos municípios do RS). A regra foi escrita como "linhas com UF e modalidade estadual (3x) ou municipal (4x)". Em 2024 ela seleciona exatamente 00VP e 00WF; em 2019 acrescenta a parte da cessão onerosa do pré-sal registrada com UF.
- **Estado ou municípios:** o tipo de favorecido decide ("Administração Pública Estadual ou do DF" = governo estadual; "Administração Pública Municipal" = municípios). No tipo genérico "Administração Pública", a modalidade 3x é governo estadual; nas demais, a linha com nome de município vai para municípios (inclui consórcios públicos, modalidades 70 e 71, R$ 0,18 bi no período coletado). A LC 176 entra pelo Tesouro: LC176_EST no governo estadual, LC176_MUN nos municípios. O DF conta como governo estadual.
- **LC 176 por UF:** Tesouro Nacional, arquivos LC176_EST e LC176_MUN, mês a mês, como no `build.py`. O Tesouro vai até agosto de 2026; em setembro de 2026 a categoria fica em zero por falta de dado (`flags.lc176_tesouro_last_month`).
- **O que fica sem UF.** O Portal registra três transferências grandes a governos **sem UF**: a cessão onerosa do pré-sal (ação 00RX, dezembro de 2019), o auxílio da LC 173/2020 (ação 00S7, quatro parcelas de R$ 15,0 bi, de junho a setembro de 2020) e a LC 176 (00SE, de dezembro de 2020 em diante; o Tesouro publica esta por UF e o total do Tesouro é igual ao do Portal em todos os meses). O Tesouro Transparente publica a LC 176 por UF, mas não publica as outras duas (conferido no conjunto "Transferências Obrigatórias da União", no arquivo consolidado e no conjunto por município). **Elas não foram distribuídas entre as UFs**: ficam em `national.transfers_public_recipients_without_uf`, mês a mês e por ação. A própria LC 173 (https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp173.htm) só permite reconstruir parte da divisão: o Anexo I fixa o valor de cada estado nos R$ 30 bi aos estados e ao DF (art. 5º, II, a); os R$ 20 bi aos municípios seguem a mesma proporção, sem o DF (art. 5º, § 4º); e os R$ 10 bi de saúde e assistência dependem da taxa de incidência da Covid-19 divulgada pelo Ministério da Saúde e da população (art. 5º, § 1º), sem valor por UF no texto. É valor fixado em lei, não pagamento registrado; usá-lo é uma decisão a tomar (seção 9).
- O arquivo de **setembro de 2026** foi gerado pelo Portal em 2026-09-29, durante o próprio mês: é um mês incompleto (`flags.transfers_partial_month`).

### 1.3 Bolsa Família, mensal

- Fonte: MDS, Matriz de Informação Social (API Solr, sem chave), um CSV por ano com os 5.571 municípios.
- O programa mudou duas vezes no período e os campos mudaram junto:

| Meses | Programa | Campo(s) |
|---|---|---|
| 2019-01 a 2021-10 | Bolsa Família | `valor_repassado_bolsa_familia_f` |
| 2021-11 a 2022-06 | Auxílio Brasil | `pab_valor_pago_d` + `pab_extraordinario_valor_pago_d` (benefício extraordinário, de 2021-12) |
| 2022-07 a 2023-02 | Auxílio Brasil | só `pab_valor_pago_d` (o valor já inclui os complementos) |
| 2023-03 a 2026-09 | Bolsa Família | `valor_repassado_bolsa_familia_f` |

- A série `bolsa_familia` junta os dois programas, porque o Auxílio Brasil substituiu o Bolsa Família nesse intervalo; o nome do programa de cada mês está em `national.bolsa_familia_program`. Conferência de coerência: em junho de 2022, em Florianópolis, (R$ 2.446.214 + R$ 2.524.273) / 12.254 famílias = R$ 405,6 por família, o piso de R$ 400 da época; em setembro de 2022, R$ 9.357.128 / 15.484 = R$ 604, o piso de R$ 600.
- **O Auxílio Emergencial não está na série.** De abril a dezembro de 2020 e de abril a outubro de 2021 a maior parte das famílias do Bolsa Família recebeu o Auxílio Emergencial no lugar do benefício, e por isso a série cai para R$ 0,1 bi a R$ 1,3 bi por mês nesses meses (contra R$ 2,5 bi antes).
- A API devolve registros para meses futuros (até 2026-12) com os campos vazios ou zerados; um mês só conta como publicado quando a soma é maior que zero. O BPC de setembro de 2026 veio zerado em todos os municípios e ficou `null`.

### 1.4 INSS e BPC por UF

- **`inss`, mensal:** Boletim Estatístico da Previdência Social (BEPS), um XLS por mês (https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/Dados-estatisticos-previdencia-social-e-inss/boletins-da-previdencia-social), tabela 19, "Benefícios do RGPS emitidos, por clientela, segundo as Unidades da Federação", coluna Valor Total. 92 meses, de 2019-01 a 2026-08, sem falhas. Inclui o 13º nos meses em que é pago e **não inclui o BPC**. É o mesmo conceito da AEPS: em 2024 a soma das UFs dá R$ 785,6 bi, contra R$ 786,9 bi da AEPS (R$ 876,9 bi com BPC menos R$ 90,0 bi de BPC).
- **`inss_gross_benefit_value`, mensal:** tabela 18 do mesmo boletim. Segundo a nota da própria tabela, é "o valor do benefício não incluindo outros créditos de natureza eventual e os descontos": fica acima da tabela 19 nos meses comuns (sem o desconto dos consignados) e abaixo dela nos meses do 13º (que é crédito eventual).
- **`bpc`, mensal:** BPC pago em cada município (MI Social, `bpc_val_f`), somado por UF, 2019-01 a 2026-08.
- **`inss_annual_aeps`, anual 2019 a 2024:** AEPS, tabela B.15, valor de benefícios emitidos no ano, **com o BPC**. É o conceito de `data/uf-balance-2024.json`. Cada ano vem da sua própria edição; as edições seguintes repetem os mesmos valores (nenhuma revisão encontrada).
- Não somar `inss_annual_aeps` com `bpc` (o BPC já está dentro).
- Quando um mês do BEPS tem mais de um arquivo publicado, os números foram comparados. Só dois meses diferem: 2021-05 (R$ 51,2 bi no primeiro arquivo, R$ 71,1 bi no reenvio, que traz a primeira parcela do 13º antecipado; junho de 2021 tem R$ 70,5 bi) e 2023-11 (diferença de R$ 0,1 mi). Vale o arquivo enviado depois; os dois valores estão em `flags.beps_duplicate_uploads`.

### 1.5 Municípios de Santa Catarina

- **Arrecadação federal, anual 2019 a 2025:** Receita, "Arrecadação da Receita administrada pela RFB por município", um XLSX por ano, aba TOTAL (DARF + GPS). Não inclui as receitas administradas por outros órgãos (por isso a soma nacional desse arquivo fica cerca de 5% abaixo do arquivo por UF). Os 295 municípios casam com o código do IBGE em todos os anos, com a mesma normalização e os dois apelidos do script de 2024.
- **Transferências, mensal:** mesma regra de destinatário de `data/sc-municipal-balance-2024.json` (favorecido "Administração Pública Municipal", ou "Administração Pública" com modalidade 40 ou 41). Linhas de SC com favorecido municipal mas sem nome de município somam R$ 1,07 mi no período coletado e ficaram fora (listadas em `checks.transfers_unmatched`).
- **Bolsa Família e BPC, mensal:** MI Social, município a município.
- **População:** `data/series/population.json`.

### 1.6 População

- Estimativas do IBGE (SIDRA 6579, variável 9324) para 2019, 2020, 2021, 2024, 2025 e 2026; **Censo 2022** (SIDRA 4709, variável 93: 203.080.756 pessoas no Brasil, 7.610.361 em SC) para 2022; **2023 é `null`**: o IBGE não publicou estimativa para 2023 (a tabela 6579 pula de 2021 para 2024).
- **Quebra de nível entre 2021 e 2022.** As estimativas de 2019 a 2021 partem do Censo 2010 e ficaram acima do que o Censo 2022 encontrou: o Brasil passa de 213,3 milhões (estimativa 2021) para 203,1 milhões (Censo 2022). Um valor per capita de 2021 e outro de 2022 não medem a mesma coisa.
- Checagem: a soma das 27 UFs é igual ao total do Brasil em todos os anos, e a soma dos 295 municípios é igual ao total de SC.

---

## 2. Cobertura

| Série | Meses `null` e motivo |
|---|---|
| `federal_revenue` | 2026-08, 2026-09: ainda não estão no arquivo da Receita (último mês publicado: 2026-07). Os meses com a atribuição por UF quebrada **não** são `null`: têm o valor bruto da Receita e o status em `national.federal_revenue_month_status`. |
| `transfers` | faltam meses de 2019-01 a 2026-09; meses publicados mas não agregados nesta coleta (bloqueio anti-robô do servidor da CGU): 2022-06, 2022-07, 2022-08, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-02, 2023-03, 2023-04, 2023-05, 2023-06, 2023-07, 2023-08, 2023-09, 2023-10, 2023-11, 2023-12, 2025-01, 2025-02, 2025-03, 2025-04, 2025-05, 2025-06, 2025-07, 2025-08, 2025-09, 2025-10, 2025-11, 2025-12, 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09. 2026-09 está incompleto. |
| `bolsa_familia` | nenhum de 2019-01 a 2026-09. |
| `inss`, `inss_gross_benefit_value`, `bpc` | 2026-09: ainda não publicados. |
| `inss_annual_aeps` | 2025 e 2026: a AEPS 2025 ainda não foi publicada. |
| SC `federal_revenue_annual` | 2026: ano em curso (o arquivo municipal é anual). |
| População | 2023 em todas as unidades (o IBGE não publicou estimativa). |

---

## 3. Checagens

### Arrecadação: soma das UFs x total nacional (R$ bi)

| Ano | Meses | Soma das 27 UFs | Total nacional (Receita) | Diferença | Diferença % |
|---|---:|---:|---:|---:|---:|
| 2019 | 12 | 1.537,08 | 1.537,08 | 0,00 | 0,000 |
| 2020 | 12 | 1.479,39 | 1.479,39 | 0,00 | 0,000 |
| 2021 | 12 | 1.878,82 | 1.878,82 | 0,00 | 0,000 |
| 2022 | 12 | 2.218,48 | 2.218,48 | 0,00 | 0,000 |
| 2023 | 12 | 2.318,12 | 2.318,12 | 0,00 | 0,000 |
| 2024 | 12 | 2.651,34 | 2.652,70 | -1,37 | -0,051 |
| 2025 | 12 | 2.855,80 | 2.886,87 | -31,07 | -1,076 |
| 2026 | 7 | 1.845,28 | 1.876,52 | -31,24 | -1,665 |

### Status mensal da arrecadação por UF (meses fora de 'ok')

| Mês | Status | Participação do DF | Soma das UFs (R$ bi) | Total nacional (R$ bi) | Sem UF (R$ bi) |
|---|---|---:|---:|---:|---:|
| 2024-09 | unattributed_gap | 7,0% | 201,8 | 203,2 | 1,4 |
| 2024-12 | ok | 7,3% | 261,3 | 261,3 | 0,0 |
| 2025-01 | ok | 6,2% | 301,2 | 301,2 | 0,0 |
| 2025-02 | uf_attribution_broken | 14,8% | 202,5 | 202,5 | 0,0 |
| 2025-03 | uf_attribution_broken | 22,1% | 209,7 | 209,7 | 0,0 |
| 2025-04 | uf_attribution_broken | 24,5% | 247,7 | 247,7 | 0,0 |
| 2025-05 | uf_attribution_broken | 21,3% | 230,2 | 230,2 | 0,0 |
| 2025-06 | uf_attribution_broken | 22,6% | 234,6 | 234,6 | 0,0 |
| 2025-07 | uf_attribution_broken | 25,2% | 254,2 | 254,2 | 0,0 |
| 2025-08 | uf_attribution_broken | 24,3% | 208,8 | 208,8 | 0,0 |
| 2025-09 | uf_attribution_broken | 22,9% | 216,7 | 216,7 | 0,0 |
| 2025-10 | uf_attribution_broken | 24,2% | 261,9 | 261,9 | 0,0 |
| 2025-11 | uf_attribution_broken | 24,0% | 226,8 | 226,8 | 0,0 |
| 2025-12 | uf_attribution_broken+unattributed_gap | 16,6% | 261,7 | 292,7 | 31,1 |
| 2026-01 | uf_attribution_broken | 17,3% | 325,8 | 325,8 | 0,0 |
| 2026-02 | ok | 6,5% | 222,1 | 222,1 | 0,0 |
| 2026-03 | unattributed_gap | 6,6% | 224,6 | 229,2 | 4,6 |
| 2026-04 | ok | 5,7% | 278,8 | 278,8 | 0,0 |
| 2026-05 | unattributed_gap | 6,2% | 257,1 | 266,8 | 9,7 |
| 2026-06 | unattributed_gap | 6,5% | 258,8 | 264,4 | 5,7 |
| 2026-07 | unattributed_gap | 5,9% | 278,1 | 289,3 | 11,2 |
| 2026-08 | not_published | n/d | n/d | 235,6 | n/d |
| 2026-09 | not_published | n/d | n/d | n/d | n/d |

### 2024: série mensal x data/uf-balance-2024.json

Maior diferença por UF: arrecadação 0,0000%, transferências 0,0000%.

### Totais anuais das 27 UFs (R$ bi)

| Ano | Arrecadação | Transferências | ao governo estadual | aos municípios | Bolsa Família / Auxílio Brasil | INSS (RGPS, BEPS t19) | INSS bruto (BEPS t18) | BPC (MI Social) | INSS AEPS (com BPC) | Transferências sem UF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 1.537,08 | 383,04 | 156,57 | 226,47 | 31,16 | 530,09 | 542,27 | 55,53 | 587,28 | 10,65 |
| 2020 | 1.479,39 | 414,53 | 162,69 | 251,84 | 9,67 | 567,19 | 577,61 | 58,42 | 627,20 | 63,31 |
| 2021 | 1.878,82 | 493,56 | 202,39 | 291,17 | 25,92 | 578,90 | 615,23 | 61,91 | 662,15 | 4,86 |
| 2022 | 2.218,48 | 251,77 (5 meses) | 112,27 (5 meses) | 139,49 (5 meses) | 114,62 | 665,19 | 690,68 | 70,94 | 734,35 | 1,34 (5 meses) |
| 2023 | 2.318,12 | n/d | n/d | n/d | 169,62 | 724,71 | 755,13 | 85,11 | 802,20 | n/d |
| 2024 | 2.651,34 | 740,12 | 284,10 | 456,02 | 170,40 | 785,58 | 820,24 | 102,27 | 876,90 | 3,99 |
| 2025 | 2.855,80 | n/d | n/d | n/d | 159,54 | 846,84 | 880,99 | 116,62 | n/d | n/d |
| 2026 | 1.845,28 (7 meses) | n/d | n/d | n/d | 116,83 (9 meses) | 635,97 (8 meses) | 630,29 (8 meses) | 82,90 (8 meses) | n/d | n/d |

### Transferências a governos registradas sem UF, por ação (R$ bi)

| Ação | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 00RX TRANSFERENCIA A ESTADOS, DISTRITO FEDERAL E MUNICIPIOS DE PARTE D | 10,66 | 0,00 | 0,00 | 0,00 | n/d | 0,00 | n/d | n/d |
| 00S7 AUXILIO FINANCEIRO AOS ESTADOS, AO DISTRITO FEDERAL E AOS MUNICIP | 0,00 | 60,15 | 0,00 | 0,00 | n/d | 0,00 | n/d | n/d |
| 00SE TRANSFERENCIA TEMPORARIA A ESTADOS, DISTRITO FEDERAL E MUNICIPIOS | 0,00 | 3,12 | 4,86 | 1,33 | n/d | 3,99 | n/d | n/d |

### SC: soma dos 295 municípios por ano (R$ bi)

| Ano | Arrecadação federal registrada nos municípios | Transferências às prefeituras | Bolsa Família / Auxílio Brasil | BPC |
|---|---:|---:|---:|---:|
| 2019 | 63,87 | 7,52 | 0,24 | 0,94 |
| 2020 | 69,41 | 8,62 | 0,09 | 0,98 |
| 2021 | 96,43 | 9,37 | 0,26 | 1,04 |
| 2022 | 106,09 | 4,28 (5 meses) | 1,18 | 1,18 |
| 2023 | 111,89 | n/d | 1,87 | 1,43 |
| 2024 | 139,83 | 13,49 | 1,89 | 1,75 |
| 2025 | 135,13 | n/d | 1,72 | 2,00 |
| 2026 | n/d | n/d | 1,28 (9 meses) | 1,39 (8 meses) |

### LC 176: Tesouro por UF contra o Portal sem UF

Soma do Tesouro (LC176_EST + LC176_MUN, 27 UFs) igual à ação 00SE do Portal em 29 de 30 meses, de 2020-12 a 2024-12; meses com diferença: 2022-02. O Tesouro publicou a LC 176 por UF até 2026-08; nos meses de transferências depois disso a categoria lc176_kandir_compensation fica em zero por falta de dado, não por falta de pagamento.

### INSS

- BEPS tabela 19 somada em 2024 (27 UFs): R$ 785,58 bi. AEPS 2024 sem o BPC: R$ 786,94 bi (R$ 876,90 bi menos R$ 89,96 bi). Diferença de 0,2%.
- SC 2024: BEPS (RGPS) R$ 38,73 bi mais BPC do MI Social R$ 1,75 bi, contra AEPS com BPC R$ 40,29 bi.
- Microdado do INSS contra o BEPS, SC, agosto de 2024: 0,05% (seção 5).
- Bolsa Família 2024 (27 UFs): R$ 170,40 bi, o mesmo valor de `data/uf-balance-2024.json`.

### SC

Os 295 municípios em 2024: transferências à prefeitura, Bolsa Família, arrecadação federal e população iguais a `data/sc-municipal-balance-2024.json` em todos os municípios (maior diferença: R$ 0,00). Nomes: os 295 municípios casam com o IBGE em todos os anos da Receita (2019 a 2025) e em todos os meses do Portal; as linhas de favorecido municipal de SC sem nome de município somam R$ 1,07 mi no período e ficaram fora.

---

## 4. Veredito sobre 2025: a quebra da arrecadação por UF

**O que foi olhado de novo (2026-09-30):** o arquivo por UF baixado outra vez (agora com 2026 até julho), o total nacional mês a mês (série histórica até 2025 e Tabela III do relatório de agosto de 2026), a página do conjunto na Receita, o arquivo da Receita **por município** de 2025 e uma busca por nota oficial.

**Evidência, mês a mês** (tabela completa na seção 3):

1. **De 2025-02 a 2026-01 (12 meses) a distribuição entre UFs quebra.** O DF fica com 14,8% (fev/2025) a 25,2% (jul/2025) da soma das UFs; de 2019 a 2024 o máximo mensal foi 10,8%. O total do país nesses meses bate com o nacional até o centavo (menos dezembro): o dinheiro não sumiu, foi atribuído ao DF. A receita previdenciária atribuída ao DF sai de cerca de R$ 2,5 bi por mês (2024) para R$ 9,9 bi em fevereiro de 2025 e R$ 16,7 bi a R$ 18,6 bi por mês de março a novembro de 2025 e em janeiro de 2026; em dezembro de 2025 e de fevereiro de 2026 em diante volta a cerca de R$ 2,8 bi. No ano de 2025, SP perde R$ 71,9 bi e RJ R$ 57,5 bi em relação a 2024 (tabela da seção 1.3 do relatório de 2024).
2. **2025-12:** além do DF alto (16,6%), R$ 31,1 bi não estão em UF nenhuma: faltam R$ 33,0 bi de receita previdenciária (R$ 60,5 bi nas UFs contra R$ 93,5 bi no total nacional) e R$ 0,6 bi de receitas de outros órgãos, e as demais linhas somam R$ 2,5 bi a mais que o nacional. É o mesmo buraco que o relatório de 2024 via no ano de 2025 inteiro: ele está todo em dezembro.
3. **De 2026-02 em diante a distribuição volta ao padrão** (DF entre 5,7% e 6,6%, como antes de 2025; SP entre 39,5% e 42,7%, contra 37,2% a 40,6% em 2024), **mas 2026-03, 05, 06 e 07 têm de R$ 4,6 bi a R$ 11,2 bi por mês sem UF** (2,0% a 3,9% do total): R$ 5,3 bi a R$ 5,9 bi de receita previdenciária por mês, mais parte das receitas administradas por outros órgãos.
4. **O arquivo por município de 2025 tem a mesma quebra:** Brasília aparece com R$ 603,3 bi, contra R$ 180,1 bi em 2024. As duas publicações vêm da mesma base, então uma não serve para corrigir a outra.
5. **Nenhuma nota da Receita.** A página do conjunto por UF ainda descreve só os anos de 2000 a 2021; o conjunto "Resultado da arrecadação" no dados.gov.br responde 401; uma busca na web não achou explicação oficial. A hipótese do relatório de 2024 (a troca da DCTF pela DCTFWeb com o MIT, que vale para fatos geradores de janeiro de 2025 com primeira entrega em fevereiro) continua **sem confirmação**; o fato de a quebra começar exatamente em fevereiro de 2025 é compatível com ela.

**Veredito.**

- **Meses afetados:** 2025-02 a 2026-01 com a distribuição por UF quebrada (`uf_attribution_broken`); 2025-12, 2026-03, 2026-05, 2026-06 e 2026-07 com parte da arrecadação sem UF (`unattributed_gap`); e, como já se sabia, 2024-09 (R$ 1,37 bi sem UF, Imposto de Importação lançado como Exportação).
- **O que o site deve fazer: cair para o dado confiável, não mostrar com aviso.** Nos meses `uf_attribution_broken`, a arrecadação por UF não pode pintar o mapa nem entrar no saldo: um aviso não conserta a leitura de que o DF "enviou" R$ 583 bi em 2025. Na prática:
  - mês isolado dentro do intervalo quebrado: mostrar o total nacional do mês e o aviso "a Receita atribuiu parte da arrecadação deste mês ao DF; a divisão por estado não é confiável", sem mapa colorido pela arrecadação;
  - ano 2025 e mandato 2023 a 2026: a arrecadação por UF fica indisponível no mapa (as transferências, o Bolsa Família e o INSS continuam disponíveis); o seletor pode oferecer 2023 a 2024 como o trecho confiável do mandato;
  - meses `unattributed_gap` (2% a 4% sem UF): podem ser mostrados, com a nota "R$ X bi deste mês não têm estado atribuído pela Receita".
- **Nada foi corrigido no arquivo.** Os valores brutos da Receita estão em `uf.*.federal_revenue`, e o status de cada mês está em `national.federal_revenue_month_status`. Quando a Receita republicar 2025, basta baixar o CSV de novo e rodar o script: o status é recalculado.
- Pedir explicação à Receita pelo Fala.BR continua recomendado (Q11).

---

## 5. INSS e BPC por município: o que existe (busca de 30 minutos)

Resultado: **o dado existe sem login, em duas fontes, e uma delas já está nos arquivos.** Não é preciso chave de API do dados.gov.br (a Q25 pode ser fechada).

| # | Fonte | O que tem | Cobertura | Acesso | Situação |
|---|---|---|---|---|---|
| 1 | MDS, MI Social, campo `bpc_val_f` (e `bpc_ben_i`, `bpc_idoso_val_f`, `bpc_pcd_val_f`, `rmv_val_f`) | **BPC pago por município e mês** (idoso e pessoa com deficiência; também a Renda Mensal Vitalícia) | 2019-01 a 2026-08, 5.571 municípios | API aberta, a mesma do Bolsa Família | **Usado:** `bpc_monthly` em `sc-municipal-federal.json` e `bpc` por UF |
| 2 | INSS, Dados Abertos (CKAN próprio, https://dadosabertos.inss.gov.br/), conjunto "Benefícios emitidos" (https://dadosabertos.inss.gov.br/dataset/beneficios-emitidos-plano-de-dados-abertos-jun-2023-a-jun-2025 e, até 2023, https://dadosabertos.inss.gov.br/dataset/inss-beneficios-emitidos) | **Microdado de cada benefício emitido**: espécie, despacho, sexo, clientela, UF, meio de pagamento, banco, município de pagamento, **município de residência** e **valor líquido**. Inclui RGPS e BPC | 2021-07 a 2026-07, com duas falhas: 2022-02 (o link "fevereiro 2022" aponta para o arquivo de março) e 2024-04 (não listado; o endereço previsível no S3 responde 403). Nada antes de 2021-07 | CSV em ZIP no S3 da AWS (armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com), sem login; licença Creative Commons Atribuição | **Validado, não montado:** cada mês tem de 0,55 GB (agosto de 2024) a 1,0 GB (julho de 2026) compactado |
| 3 | INSS, "Dados agregados da folha de pagamento" (mesmo CKAN) | Quantidade e valor dos benefícios emitidos por **despacho** | mensal | XLSX pequeno | Não serve: não tem município nem UF |
| 4 | AEPS 2024 (ZIP de 549 arquivos) | 16 seções; nenhuma com município | anual | aberto | Não serve |
| 5 | AEPS Infologo (www3.dataprev.gov.br/infologo) | base histórica que tinha recortes municipais | | o servidor não respondeu (sem conexão) | Fora do ar |
| 6 | dados.gov.br | espelho dos conjuntos acima | | API responde 401 sem login | Desnecessário: o CKAN do INSS está aberto |
| 7 | Portal da Transparência, download "BPC" por beneficiário | BPC por pessoa e município | | mesmo servidor com bloqueio automático (seção 7) | **Não testado** nesta sessão, para não disparar o bloqueio durante a coleta das transferências |

**Validação do microdado (fonte 2), agosto de 2024.** O arquivo foi lido em streaming (`curl | tar -xOf - | python`, nada gravado em disco), com `pipelines/series/inss_issued_by_municipality.py`: 40.425.357 benefícios, R$ 67,71 bi líquidos no país, 27 UFs, zero linhas inválidas. Filtrando a coluna UF = Santa Catarina: 1.757.954 benefícios, R$ 3.099,4 mi, dos quais R$ 130,9 mi nas espécies de amparo (BPC da pessoa com deficiência R$ 83,7 mi, BPC do idoso R$ 46,6 mi, amparos previdenciários R$ 0,5 mi). Sem elas sobram R$ 2.968,6 mi, contra **R$ 2.967,1 mi na tabela 19 do BEPS** para SC no mesmo mês: diferença de 0,05%. O valor do microdado é, portanto, o mesmo conceito da série `inss`.

Três cuidados para quem for montar a série municipal com a fonte 2:

1. **A coluna UF é a da agência que mantém o benefício, não a da residência.** Os benefícios mantidos em SC têm 2.680 municípios de residência diferentes. Para SC por município é preciso filtrar pelo `Mun Resid` com "-Sc-", não pela coluna UF.
2. **O município vem com código de 5 dígitos do INSS e nome cortado em 20 caracteres** (por exemplo "20053-Sc-Florianópol"), não com o código do IBGE. É preciso uma tabela de correspondência (por nome dentro da UF).
3. **Volume:** um ano de SC exige ler 12 arquivos, cerca de 7 GB em streaming (dá para fazer sem guardar nada em disco, mas leva tempo); a série inteira desde 2021-07 passa de 50 GB lidos. **Para 2019 e 2020 não há microdado publicado.**

Recomendação: montar só o ano de referência do mapa (por exemplo 2024, 11 meses disponíveis porque falta abril) ou só os anos que o site mostrar, e registrar abril de 2024 como `null`.

---

## 6. brasiltransparente.digital

**Quem mantém.** Projeto comunitário, sem fins lucrativos, que se apresenta como "plataforma independente de tecnologia cívica". Código na organização do GitHub `brasil-transparente` (criada em 2025-04-16; 4 repositórios: `brasil-transparente-processor`, `-api` e `-frontend`). O principal autor é o usuário `gabriel-missel` (145 e 96 commits nos dois repositórios principais; o perfil público diz Gabriel Missel, engenheiro de software sênior, Porto Alegre), com mais 7 contribuidores com 1 a 6 commits. Mantido por doações via Pix. Contato por e-mail e Discord.

**O que tem.** Somente a **despesa paga da União** (regime de caixa), **exercício 2025**, em duas visões: (a) "Resumo", com 10 grupos reclassificados pelo projeto (aposentadorias e pensões, juros, saúde, educação, transferência de renda, precatórios, defesa, seguro-desemprego e abono, Judiciário, outros), total de R$ 2,93 tri; (b) "Gastos detalhados", navegação Poder > Ministério > Órgão > Unidade Gestora > Elemento de despesa. Regras próprias de método: **retira os repasses a estados e municípios**, retira o refinanciamento da dívida, considera só valores pagos, e move precatórios e RPVs do Judiciário para o Executivo.

**O que não tem.** Nenhum recorte por UF ou por município (a API aceita `unidadeFederativaId`, mas só o id 1, União, tem dados; outros ids devolvem lista vazia ou erro 500). Não tem favorecido, CNPJ ou contrato. Não tem ação orçamentária nem programa (o nível mais fino é o elemento de despesa), então não separa emendas parlamentares. Não tem série histórica (só 2025) nem arrecadação.

**Fontes declaradas.** Portal da Transparência (execução da despesa), Câmara, Senado, STF, CNJ, TCU, MPF, MPT, MPM, MPDFT, ESMPU e DPU, com links na página "Origem".

**Atualidade.** O site mostra 2025; o repositório `processor` recebeu commit em 2026-09-28. O dump do banco fica num Google Drive citado no README.

**Licença.** Código sob AGPL-3.0. Nenhuma licença declarada para os dados (que são públicos na origem).

**API.** https://api.brasiltransparente.digital, sem chave, documentação OpenAPI em https://api.brasiltransparente.digital/v3/api-docs (8 rotas GET; título "Brasil Transparente REST API", versão "1.0.0-2024" embora os dados sejam de 2025).

**Preenche as nossas lacunas?**

| Lacuna do projeto | Resposta |
|---|---|
| INSS por município | Não. Só total nacional do Fundo do RGPS por elemento. |
| Detalhe do gasto federal | Em parte: dá o gasto nacional de 2025 por órgão, unidade gestora e elemento, útil para explicar o gasto "Nacional" sem UF (Q10), mas não o reparte por UF. |
| Contratos e empresas | Não. |
| Emendas parlamentares | Não (sem ação orçamentária, e os repasses a estados e municípios são retirados por método). |

**Três números cruzados (2025, ano inteiro).**

| Número (2025) | Este projeto | Brasil Transparente | Diferença | Por quê |
|---|---:|---:|---:|---|
| Bolsa Família | R$ 159,5 bi (MI Social, 27 UFs); R$ 162,9 bi somando o Auxílio Gás (R$ 3,3 bi, MI Social) | R$ 161,6 bi (Secretaria Nacional de Renda de Cidadania, elemento "Auxílios Financeiros a Pessoa Física"; o grupo "Programas de Transferência de Renda" soma R$ 162,1 bi) | -1,2% só com o Bolsa Família; 0,8% com o Auxílio Gás | o Brasil Transparente para no elemento de despesa, sem a ação, e não separa os programas da mesma secretaria |
| BPC | R$ 116,6 bi (MI Social) | R$ 122,1 bi (INSS, elemento "Benefício Mensal ao Deficiente e ao Idoso") | -4,5% | pago no SIAFI no ano (inclui restos a pagar) contra valor da folha mensal por município |
| Benefícios do RGPS | R$ 846,8 bi (BEPS t19, líquido dos consignados, com 13º); R$ 881,0 bi (BEPS t18, bruto, sem 13º) | R$ 980,4 bi (Fundo do RGPS, 6 elementos de aposentadorias, pensões e outros benefícios, urbanos e rurais) | -13,6% e -10,1% | o SIAFI registra o pagamento bruto com o 13º; o BEPS desconta os consignados (t19) ou deixa o 13º de fora (t18) |

Leitura neutra: os dois primeiros ficam próximos e as diferenças têm causa conhecida (o elemento do Brasil Transparente junta o que a mesma secretaria paga a pessoas físicas; o BPC do MDS é por município de pagamento e o do Brasil Transparente é o pago no SIAFI no ano, que inclui restos a pagar). O terceiro difere por conceito: o BEPS e a AEPS medem o benefício **emitido líquido** dos consignados, e o Brasil Transparente mede a **despesa paga** bruta do SIAFI; o relatório de 2024 já registrava a mesma distância (seção 3.4 daquele relatório). Nenhum dos três indica erro de um lado ou de outro.

---

## 7. Diário de transparência

Mesmo critério do relatório de 2024: registrar o que aconteceu, com o mesmo peso para o fácil e para o difícil. "Passos" conta as ações até ter o número utilizável.

| # | Conjunto | URL | Formato | Chave ou login | Passos | O que aconteceu |
|---|---|---|---|---|---|---|
| 1 | Receita: arrecadação por estado | https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv | CSV único, latin1, `;` | Não | 3 | Baixado de novo; agora vai até julho de 2026. Os formatos numéricos misturados continuam (vírgula de milhar em 2001 e 2002, ponto de milhar em 2023 e 2024). **A página do conjunto ainda lista só os anos de 2000 a 2021** e não tem nenhuma nota sobre 2025. |
| 2 | Receita: série histórica nacional | https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/serie-historica/arrecadacao-das-receitas-federais-1994-a-2025.xlsx | XLSX, uma aba por ano, colunas mensais | Não | 2 | Limpo. Termina em 2025. |
| 3 | Receita: análise mensal da arrecadação | https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/arrecadacao-federal/2026/ | PDF mensal | Não | 4 | Única fonte automatizável do total nacional de 2026. A Tabela III traz todos os meses desde janeiro de 2021, mas só em PDF: foi preciso extrair o texto com `pdftotext` e ler a coluna Total Geral. O conjunto "Resultado da arrecadação" no dados.gov.br respondeu **401** e a página "Análise gerencial" respondeu "Conteúdo Restrito". |
| 4 | Receita: arrecadação por município | https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/copy_of_arrecadacao-das-receitas-administradas-pela-rfb-por-municipio | XLSX por ano (0,5 a 1,9 MB) | Não | 3 | Padrão de endereço estável de 2018 a 2025. A aba se chama "Total" em 2019 e 2020 e "TOTAL" depois; o título da aba muda de "TOTAL" para "RECOLHIMENTOS EM DARF E GPS". Nomes sem acento, casados com o IBGE com dois apelidos. **O arquivo de 2025 tem a mesma quebra do DF** do arquivo por UF. |
| 5 | Portal da Transparência: transferências | https://portaldatransparencia.gov.br/download-de-dados/transferencias/AAAAMM | ZIP mensal (1,4 a 7,3 MB) com CSV de até 160 MB | Não, mas com **bloqueio automático** | 8 | 93 meses. Depois de 18 downloads seguidos, o servidor de arquivos (dadosabertos-download.cgu.gov.br) passou a responder com uma página "Human Verification" (AWS WAF) no lugar do ZIP, com código HTTP 405. O bloqueio saiu sozinho depois de alguns minutos; com 45 s entre downloads e espera crescente quando a página aparece, a coleta terminou, com mais bloqueios pelo caminho. O arquivo do mês corrente (202609) é gerado durante o mês. Três transferências grandes a governos vêm sem UF (cessão onerosa, LC 173 e LC 176). |
| 6 | Tesouro Transparente: transferências obrigatórias | https://www.tesourotransparente.gov.br/ckan/dataset/transferencias-obrigatorias-da-uniao | CSVs largos e XLSX consolidado | Não | 4 | LC 176 por UF e por mês bate com o Portal em 2024 (SC: R$ 86,21 mi). **Não há LC 173 nem cessão onerosa** em nenhum dos três conjuntos de transferências do Tesouro (por UF, consolidado e por município); a busca no CKAN por "LC 173", "coronavirus" e "cessao onerosa" voltou vazia. |
| 7 | MDS: MI Social | https://aplicacoes.mds.gov.br/sagi/servicos/misocial | API Solr, CSV | Não | 5 | Rápida (5 MB por ano, os 5.571 municípios). Obstáculos: os campos mudam com o programa (Bolsa Família, Auxílio Brasil em dois formatos) e não há dicionário na chamada; foi preciso abrir registros de meses diferentes para achar os campos. A API devolve meses futuros (até 2026-12) com valores vazios ou zero. Um campo de 2026 (`pbf_vlr_repassado_d`) traz o próprio mês (202608) no lugar de um valor. |
| 8 | Previdência: BEPS | https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/Dados-estatisticos-previdencia-social-e-inss/boletins-da-previdencia-social | XLS mensal (2,7 MB, 29 abas) | Não | 6 | Todos os 92 meses existem, mas espalhados: a pasta de 2023 se chama "2023-1", a de 2024 "2024-1" (a "2024" dá 404), dois meses de 2024 estão na pasta de 2025, o mês mais recente está na página principal, e os nomes de arquivo variam ("Bepsa_janeiro2019a_finala_Excel.xls", "beps19.05b.xls", "beps082022_final_dez22.xls"). 20 meses têm mais de um arquivo; em 2 deles os números diferem, sem aviso de qual vale. |
| 9 | Previdência: AEPS 2019 a 2024 | https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/Dados-estatisticos-previdencia-social-e-inss/anuarios-da-previdencia-social/anuarios-da-previdencia-social | ZIP por ano (4,7 a 11,9 MB, 480 a 550 arquivos) | Não | 5 | Cada ano tem um nome de ZIP diferente (`aeps-2019-xlsx-3.zip`, `aeps_2020_xlsx-2.zip`, `aeps_2021-xls.zip`...) e a tabela muda de nome (`19SB_15.xlsx` e depois `20SB15.xlsx`). O download de 2024 foi cortado no meio uma vez e precisou ser retomado. Valores iguais entre edições. |
| 10 | INSS: dados abertos (CKAN próprio) | https://dadosabertos.inss.gov.br/ | ZIP com CSV por mês, 0,55 a 1 GB | Não | 4 | **API CKAN aberta**, diferente do dados.gov.br. O microdado tem município de residência e valor líquido. Obstáculos: tamanho, código de município próprio do INSS, nome cortado em 20 caracteres, coluna UF da agência (não da residência), um link apontando para o mês errado e um mês faltando. |
| 11 | AEPS Infologo | http://www3.dataprev.gov.br/infologo/ | | | 1 | Sem resposta do servidor. |
| 12 | IBGE: população | https://servicodados.ibge.gov.br/api/v3/agregados/6579 e /4709 | API JSON | Não | 3 | Fácil. 2023 não existe; entre 2021 e 2022 muda a base (estimativa do Censo 2010 para o Censo 2022). Os nomes de município vêm com " - SC" no fim. |
| 13 | brasiltransparente.digital | https://api.brasiltransparente.digital/v3/api-docs | API JSON | Não | 4 | Documentação OpenAPI clara, respostas rápidas. Só União, só 2025. |

**Balanço neutro do diário.** Tudo o que entrou nos números está aberto e sem cadastro, e as somas que puderam ser cruzadas bateram: 2024 reproduzido exatamente, UFs contra nacional até o centavo de 2019 a 2023, o microdado do INSS contra o BEPS com 0,05%. As dificuldades foram de forma, não de acesso: arquivos oficiais em pastas com nomes irregulares, versões repetidas sem indicação de qual vale, campos que mudam de nome, total nacional de 2026 só em PDF, um bloqueio automático no servidor da CGU que trata download em sequência como robô, e transferências de dezenas de bilhões registradas sem estado. A quebra de 2025 na Receita continua sem nenhuma explicação pública.

---

## 8. Como reproduzir

Todos os scripts estão em `pipelines/series/` e usam a mesma pasta de trabalho, fora do repositório. Dependências: Python 3 com `openpyxl` e `xlrd`, `curl`, `tar` (para o microdado do INSS) e `pdftotext` (poppler). Nenhuma chave de API, nenhum login.

```bash
SERIES=~/Documents/Brasil-Imposto/pipelines/series
W=/caminho/para/pasta-de-trabalho
bash $SERIES/download_inputs.sh $W                        # Receita, Tesouro (cerca de 10 MB)
bash $SERIES/download_misocial.sh $W                      # MDS MI Social, 8 CSVs de cerca de 5 MB
python3 $SERIES/agg_transfers_monthly.py $W 201901 202609 45   # Portal: um ZIP por vez, somado e apagado; 45 s entre downloads
python3 $SERIES/beps_rgps_by_uf.py $W                     # BEPS, cerca de 115 XLS de 2,7 MB, lidos e apagados
python3 $SERIES/aeps_inss_by_uf.py $W                     # AEPS 2019 a 2024, lidos e apagados
python3 $SERIES/build_population.py $W                    # -> data/series/population.json
python3 $SERIES/build_federal_by_uf_monthly.py $W         # -> data/series/federal-by-uf-monthly.json
python3 $SERIES/build_sc_municipal_federal.py $W          # -> data/series/sc-municipal-federal.json
python3 $SERIES/report_tables.py                          # tabelas deste relatório
```

Opcional, microdado do INSS de um mês (0,55 a 1 GB lido em streaming, nada gravado):

```bash
curl -s "https://armazenamento-dadosabertos.s3.sa-east-1.amazonaws.com/PDA_2023_2025/Grupos_de_dados/Benef%C3%ADcios+emitidos/D.SDA.PDA.003.EMI.202408.CSV.ZIP" \
  | tar -xOf - | python3 $SERIES/inss_issued_by_municipality.py saida.json "Santa Catarina"
```

Módulo auxiliar: `classify_transfers.py` (regras de destinatário, esfera e categoria das transferências, compartilhadas pelos dois construtores). Os scripts reaproveitam `pipelines/taxmap.py` e `pipelines/parse_tt.py`. O pico de disco da coleta foi de cerca de 100 MB (o maior arquivo guardado ao mesmo tempo é um ZIP mensal de até 7 MB; os caches mensais somam cerca de 60 MB).

---

## 9. Decisões para o autor

| # | Decisão | Opções | Recomendação |
|---|---|---|---|
| 1 | Arrecadação por UF de 2025-02 a 2026-01 | (a) esconder no mapa e mostrar só o total nacional; (b) mostrar com aviso | (a), seção 4 |
| 2 | LC 173/2020 (R$ 60,1 bi em 2020) e cessão onerosa (R$ 10,7 bi sem UF em 2019) | (a) deixar fora das UFs, como está; (b) distribuir pelo Anexo I da própria lei (cobre R$ 50 bi dos R$ 60 bi; os R$ 10 bi de saúde não têm valor por UF na lei; e é valor fixado, não pagamento registrado) | (a) por enquanto, com o valor nacional visível; (b) só com uma fonte de pagamento por UF |
| 3 | INSS no mapa | `inss` (BEPS t19, mesmo conceito da AEPS de 2024) ou `inss_gross_benefit_value` (t18, sem desconto e sem 13º) | `inss`, para manter o conceito do balanço de 2024; explicar que é líquido dos consignados |
| 4 | INSS por município (fecha a Q25 sem chave de API) | montar com o microdado do INSS para os anos que o site mostrar | começar por 2024 em SC (11 meses; abril não existe) |
| 5 | Auxílio Emergencial (2020 e 2021) | fora, como está; ou coletar à parte | fora, com o aviso já escrito em `flags` |
