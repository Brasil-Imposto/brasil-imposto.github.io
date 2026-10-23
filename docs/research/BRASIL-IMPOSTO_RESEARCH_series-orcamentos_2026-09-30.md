# Séries de orçamento da União, dos estados e das prefeituras de SC, 2019 a 2026: método

> **Nota de 2026-10-14:** `fetch_sc_municipal_series.py` e `build_sc_municipal_series.py` viraram `fetch_municipal_series.py --uf` e `build_municipal_series.py --uf` (D71).

**Data da coleta:** 2026-09-30
**Arquivos gerados:** `data/series/union.json`, `data/series/state-budgets.json`, `data/series/sc-municipal-budgets.json`
**Scripts (em `pipelines/series/`):** `siconfi_client.py`, `siconfi_parse.py`, `fetch_state_series.py`, `build_state_series.py`, `fetch_sc_municipal_series.py`, `build_sc_municipal_series.py`, `build_union_series.py`, `checks_series.py`. O cache bruto fica em `pipelines/series/cache/`, fora do git. A mesma pasta tem scripts de outra frente de trabalho (transferências federais, INSS, população), que este relatório não cobre.
**Para que serve:** o site mostrar, para o Brasil, cada estado e cada município de SC, de onde veio o dinheiro, para onde foi, se sobrou ou faltou e quanto o governo deve, escolhendo um mês, um ano ou um mandato (2019 a 2022, 2023 a 2026).

Regra seguida do começo ao fim: nenhum valor é estimado. Cada número vem de uma linha de um relatório oficial, e o arquivo diz qual. Quando o relatório não traz o número, ou traz um número que contradiz o próprio relatório, o campo fica nulo e o motivo fica escrito ao lado.

## 1. Resumo

| Fonte | O que cobre | Último período publicado (coleta de 30/09/2026) |
|---|---|---|
| Tesouro Nacional, Resultado do Tesouro Nacional (RTN), série histórica | União (Governo Central), mês a mês, jan/2019 a ago/2026 | agosto de 2026 (boletim publicado em 29/09/2026) |
| Banco Central, SGS 13761 e 13762 | Dívida bruta do governo geral, em R$ e em % do PIB, dez/2018 a ago/2026 | agosto de 2026 |
| SICONFI, RREO dos 27 governos estaduais | todos os bimestres de 2019-B1 a 2025-B6, sem nenhum faltando, e 2026 até o último entregue | 2026-B4 (julho e agosto) em 13 estados; 2026-B3 nos outros 14 (o prazo do B4 é hoje, 30 dias depois do fim do bimestre, LRF art. 52) |
| SICONFI, RGF Anexo 02 dos 27 estados | dívida no fim de 2018 e no fim de cada quadrimestre até 2026 | 2026-Q2 (fim de agosto) em 13 estados; 2026-Q1 nos outros 14 |
| SICONFI, RREO e RGF das 295 prefeituras de SC | 6º bimestre de 2021 a 2025 e o último bimestre entregue em 2026 | anos fechados: 294 ou 295 de 295 por ano; 2026: 293 prefeituras (237 no B4, 51 no B3, 5 no B2) |

Todas as checagens passaram (seção 6). Achado paralelo: o arquivo antigo `data/state-budgets-2024.json` tem 54 linhas de total vazadas para dentro das subfunções de "Encargos Especiais" (seção 7.1). Ele não foi alterado aqui.

## 2. Sobrou ou faltou? O que cada número quer dizer

Em todos os arquivos, **positivo quer dizer que sobrou** (superávit) e **negativo quer dizer que faltou** (déficit). Os valores estão em reais correntes, sem correção pela inflação.

**Anexo 01 do RREO, o Balanço Orçamentário (campo `budget_result`).** É a conta do caixa do ano. De um lado, tudo o que entrou: impostos, repasses e também o dinheiro que o governo pegou emprestado. Do outro, tudo o que o governo já gastou. Se entrou mais do que saiu, o anexo mostra SUPERÁVIT; se saiu mais, DÉFICIT. Dois cuidados: como empréstimo conta como entrada, "sobrar" aqui não quer dizer que as contas estão saudáveis; e um déficit pode ser pago com dinheiro guardado de anos anteriores. Nos bimestres 1 a 5 o gasto comparado é o **liquidado** (serviço entregue, conta reconhecida); no 6º bimestre é o **empenhado** (tudo o que o governo se comprometeu a pagar no ano). O campo `budget_result_basis` diz qual.

**Anexo 06 do RREO, resultado primário (campo `primary_result`).** É a conta do dia a dia, sem a dívida: impostos e repasses de um lado; salários, saúde, escolas, obras do outro. Não entram os juros nem os empréstimos. Se sobrou, o governo tem dinheiro para pagar juros e diminuir o que deve. Se faltou, precisou de empréstimo ou de dinheiro guardado. "Acima da linha" quer dizer calculado pelas receitas e despesas; é o número principal do anexo e o que o arquivo usa.

**Anexo 06 do RREO, resultado nominal (campo `nominal_result`).** É o primário depois de pagar os juros da dívida (e de receber os juros do dinheiro aplicado). Diz se, no fim, a dívida tende a crescer (faltou) ou a diminuir (sobrou). O anexo também traz o cálculo "abaixo da linha", que olha direto quanto a dívida líquida mudou; os dois cálculos dão números diferentes e ambos estão no campo `results_reported`.

**RGF Anexo 02, a dívida (campo `debt`).** `dc` (Dívida Consolidada) é tudo o que o governo deve a prazo longo: empréstimos, parcelamentos, precatórios vencidos. `dcl` (Dívida Consolidada Líquida) é essa dívida menos o dinheiro em caixa e o que outros devem ao governo. DCL negativa quer dizer que o governo tem mais dinheiro guardado do que dívida. `dcl_pct_rcl` compara a dívida com a receita de um ano (Receita Corrente Líquida); o limite do Senado é 200% para estados e 120% para municípios (Resolução do Senado nº 40/2001).

**União (arquivo `union.json`).** `primary_result` é o resultado primário do Governo Central apurado pelo Tesouro (acima da linha): a receita que sobra depois de repassar a parte de estados e municípios (`revenue_net`) menos a despesa primária (`primary_spending`). `nominal_result` é o resultado nominal apurado pelo Banco Central (abaixo da linha): o primário mais os juros (`nominal_interest`). `gross_debt_brl` e `gross_debt_pct_gdp` são a dívida bruta do governo geral (União, estados e municípios, sem o Banco Central e as estatais).

## 3. Método

### 3.1 SICONFI (estados e prefeituras)

- API pública do Tesouro: `https://apidatalake.tesouro.gov.br/ords/siconfi/tt/` (`rreo`, `rgf`, `entes`). Sem login e sem chave.
- A API não aceita consulta sem `id_ente` (testado: devolve zero linhas), então é uma chamada por governo, por período e por anexo. No máximo 6 chamadas ao mesmo tempo, com espera crescente em caso de erro, e paginação da API seguida quando existe.
- **Os dois tipos de relatório sempre são tentados:** "RREO" e depois "RREO Simplificado"; "RGF" e depois "RGF Simplificado", por quadrimestre e por semestre. O Anexo 01 decide o tipo do período; os outros anexos seguem o mesmo tipo e, se faltarem, o outro tipo é tentado.
- Cada resposta bruta fica guardada, sem perda, num arquivo por governo (`cache/siconfi/E-42.jsonl.gz`, `M-4205407.jsonl.gz`), então uma nova execução retoma de onde parou. Respostas vazias de anos fechados também ficam guardadas; as de 2026 não, porque o relatório ainda pode chegar.
- Estados: todos os 6 bimestres de cada ano, de 2019 a 2026. Prefeituras: o 6º bimestre (ano fechado) de 2021 a 2025 e, em 2026, o último bimestre entregue por cada uma.

### 3.2 O que sai de cada anexo

| Anexo | Linhas e colunas usadas | Campos |
|---|---|---|
| RREO 01, Balanço Orçamentário | "RECEITAS (EXCETO INTRA-ORÇAMENTÁRIAS)", colunas "Até o Bimestre" e "No Bimestre"; "DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS)", colunas empenhadas, liquidadas e pagas até o bimestre e no bimestre; linhas "SUPERÁVIT" e "DÉFICIT"; "AMORTIZAÇÃO DA DÍVIDA / REFINANCIAMENTO" | `revenue_total`, `revenue_in_bimester`, `spending_committed`, `spending_liquidated`, `spending_paid`, `spending_*_in_bimester`, `budget_result`, `debt_refinancing_liquidated` |
| RREO 02, Despesa por Função | bloco "Total das Despesas Exceto Intra-Orçamentárias", coluna "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)"; funções e subfunções | `spending_by_function` (mesmo formato de `data/state-budgets-2024.json`), `spending_by_function_total` |
| RREO 03, Receita Corrente Líquida | todas as linhas; coluna "TOTAL (ÚLTIMOS 12 MESES)" e as 12 colunas mensais `<MR-11>` a `<MR>` | estados: `revenue_lines` (as mesmas 13 linhas e nomes do arquivo de 2024, mais a Lei Kandir quando existe), `revenue_current_total`, `rcl`, `to_municipalities`, `fundeb_deduction`; prefeituras: todas as linhas com grupo (imposto, transferência, outra); `revenue_monthly` nos dois |
| RREO 06, Resultados | todas as linhas "RESULTADO PRIMÁRIO" e "RESULTADO NOMINAL", acima e abaixo da linha | `primary_result`, `nominal_result`, o nome exato da linha usada em `*_method`, todas em `results_reported` |
| RGF 02, Dívida Consolidada Líquida | "DÍVIDA CONSOLIDADA - DC (I)", "DÍVIDA CONSOLIDADA LÍQUIDA (DCL)", "% da DCL sobre a RCL AJUSTADA", colunas "Até o nº Quadrimestre" ou "Semestre" e "SALDO DO EXERCÍCIO ANTERIOR" | `debt` |

Detalhes que mudam o número:

- **Resultado do Anexo 01.** A linha SUPERÁVIT ou DÉFICIT só é usada quando bate, até R$ 1, com o próprio anexo: total das receitas menos o total das despesas executadas (liquidadas nos bimestres 1 a 5, empenhadas no 6º). Essa regra foi tirada dos próprios relatórios: depois da correção descrita no diário, 970 de 1.039 relatórios estaduais dos bimestres 1 a 5 batem com as liquidadas e 177 de 189 do 6º bimestre batem com as empenhadas. Quando a linha falta ou não bate, o campo fica nulo e o motivo, com os números do anexo, fica em `nulls.budget_result`. O número nunca é calculado por este script.
- **Resultado do Anexo 06.** O modelo do anexo mudou em 2023: até 2022 há uma linha de primário e uma de nominal, cobrindo o orçamento todo; desde 2023 o primário vem com e sem o regime de previdência dos servidores (RPPS), e o nominal acima da linha só sem RPPS. O arquivo usa o primário acima da linha **com RPPS**, que é o comparável com os anos anteriores. O nominal usa a única linha acima da linha que existe, o que cria uma quebra de série em 2023 (seção 7).
- **Receita por mês.** Cada Anexo 03 traz os 12 meses que terminam no bimestre. Cada mês vem do último relatório do próprio ano (o do 6º bimestre nos anos fechados; o último entregue em 2026). `month_report` diz de qual relatório veio cada mês. Os nomes das linhas são os do relatório, com espaços repetidos removidos e "( - )" escrito "(-)", porque a mesma linha aparece escrita dos dois jeitos em anos diferentes.
- **Intraorçamentárias.** Receitas e despesas saem sem as operações entre órgãos do mesmo governo (por exemplo, a contribuição do estado ao seu próprio fundo de previdência), que contariam o mesmo dinheiro duas vezes. A linha SUPERÁVIT ou DÉFICIT do Anexo 01 inclui essas operações dos dois lados, como foi enviada.
- **Dívida no início de um mandato.** A dívida é um saldo, não um fluxo. Para o mandato 2019 a 2022, o ponto de partida é dezembro de 2018: nos estados vem da coluna "SALDO DO EXERCÍCIO ANTERIOR" do RGF de 2019 (chave `2018-Q3`); na União, das mesmas séries do SGS (`baseline`). Nas prefeituras, a primeira chave é o fim de 2020.

### 3.3 União

- Tabela 1.1 da série histórica do RTN, arquivo `serie_historica_ago26.xlsx`, publicado em 29/09/2026 na página do boletim de agosto (`https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/8`, arquivo em `https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326`). O catálogo de dados do Tesouro ainda apontava para a versão de julho no dia da coleta, por isso a versão de agosto foi baixada da página do boletim.
- Linhas usadas: 1 (receita total), 2 (transferências a estados e municípios), 3 (receita líquida), 4 (despesa total), 5 (resultado primário acima da linha), 8 (primário abaixo da linha, do Banco Central), 9 (juros nominais) e 10 (resultado nominal do Governo Central). Valores em R$ milhões convertidos para R$.
- Dívida: SGS 13761, "Dívida bruta do governo geral - Saldos em R$ milhões - Metodologia utilizada a partir de 2008", e SGS 13762, "Dívida bruta do governo geral (% PIB) - Metodologia utilizada a partir de 2008". Os números e nomes das séries foram conferidos no serviço de metadados do próprio SGS.

### 3.4 Como o site monta um mês, um ano ou um mandato

- **Fluxos** (receita, despesa, resultados): somar os meses (União) ou usar o 6º bimestre de cada ano (estados e prefeituras) e somar os anos. O campo `aggregation` do `union.json` diz o que se soma e o que se lê no fim do período.
- **Saldos** (dívida): ler o valor no fim do período e comparar com o fim do período anterior.
- **Um mês nos estados e prefeituras:** a receita existe mês a mês (`revenue_monthly`); o gasto não existe por mês no RREO, só por bimestre (`spending_committed_in_bimester`, `spending_liquidated_in_bimester`). O arquivo não inventa um gasto mensal.
- **Mandato 2023 a 2026:** ainda incompleto; o último período de cada fonte está no campo `latest`.

## 4. União: os números

| Ano | Receita total (R$ bi) | Despesa primária (R$ bi) | Resultado primário (R$ bi) | Juros (R$ bi) | Resultado nominal (R$ bi) | Dívida bruta no fim do ano | % do PIB |
|---|---|---|---|---|---|---|---|
| 2019 | 1.635,6 | 1.442,3 | -95,1 | -310,1 | -399,0 | 5,50 tri | 74,44% |
| 2020 | 1.468,1 | 1.947,6 | -743,3 | -266,7 | -1.011,9 | 6,62 tri | 86,94% |
| 2021 | 1.932,6 | 1.614,2 | -35,1 | -407,3 | -443,2 | 6,97 tri | 77,31% |
| 2022 | 2.313,3 | 1.809,7 | 46,4 | -503,2 | -448,3 | 7,22 tri | 71,68% |
| 2023 | 2.353,4 | 2.129,9 | -228,5 | -614,5 | -879,1 | 8,08 tri | 73,83% |
| 2024 | 2.679,4 | 2.204,7 | -42,9 | -855,2 | -900,6 | 8,98 tri | 76,27% |
| 2025 | 2.902,3 | 2.394,2 | -61,7 | -891,9 | -950,6 | 10,02 tri | 78,64% |
| 2026 (jan a ago) | 2.081,6 | 1.764,6 | -94,9 | -714,4 | -811,5 | 11,05 tri | 82,86% |

| Mandato | Primário somado (R$ bi) | Nominal somado (R$ bi) | Dívida bruta no início (% do PIB) | Dívida bruta no fim (% do PIB) |
|---|---|---|---|---|
| 2019 a 2022 | -827,0 | -2.302,4 | 75,27% | 71,68% |
| 2023 a 2026 (até ago/2026) | -428,0 | -3.541,7 | 71,68% | 82,86% |

Início do primeiro mandato: dezembro de 2018. Início do segundo: dezembro de 2022.

## 5. Cobertura

### 5.1 Estados

Todos os 27 governos entregaram todos os bimestres de 2019-B1 a 2025-B6 (42 por estado), sem nenhum período faltando. A tabela mostra também o ano de 2025, só como exemplo do conteúdo.

| UF | Bimestres | Último RREO | Último RGF | `budget_result` nulo | Receita 2025 (R$ bi) | Despesa empenhada 2025 (R$ bi) | Anexo 01, 2025 (R$ bi) | Primário 2025 (R$ bi) | Nominal 2025 (R$ bi) | DCL fim de 2025 (R$ bi) | DCL / RCL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RO | 46 | 2026-B4 | 2026-Q2 | 0 (0 em B6) | 16,7 | 16,5 | 0,06 | -0,04 | -0,16 | -0,8 | -5,02% |
| AC | 46 | 2026-B4 | 2026-Q2 | 1 (0 em B6) | 12,7 | 12,6 | -0,02 | 0,37 | 0,21 | 1,5 | 13,23% |
| AM | 46 | 2026-B4 | 2026-Q2 | 0 (0 em B6) | 35,9 | 35,5 | 0,38 | 1,06 | -0,07 | 7,5 | 26,41% |
| RR | 45 | 2026-B3 | 2026-Q1 | 18 (4 em B6) | 10,0 | 8,8 | 1,17 | 0,40 | 0,00 | 0,8 | 9,51% |
| PA | 46 | 2026-B4 | 2026-Q2 | 2 (1 em B6) | 50,4 | 48,9 | 0,89 | -1,22 | -1,13 | 4,0 | 9,01% |
| AP | 46 | 2026-B4 | 2026-Q2 | 8 (0 em B6) | 12,0 | 11,2 | 0,79 | 0,31 | 0,44 | -0,8 | -7,96% |
| TO | 45 | 2026-B3 | 2026-Q1 | 2 (0 em B6) | 17,3 | 17,3 | -0,01 | -0,15 | -0,14 | 2,5 | 16,19% |
| MA | 46 | 2026-B4 | 2026-Q2 | 5 (2 em B6) | 34,4 | 33,5 | 0,05 | 0,78 | -0,46 | 1,7 | 5,35% |
| PI | 46 | 2026-B4 | 2026-Q2 | 0 (0 em B6) | 22,9 | 23,5 | -0,44 | -1,25 | -2,07 | 13,4 | 71,35% |
| CE | 45 | 2026-B3 | 2026-Q1 | 6 (1 em B6) | 46,0 | 44,8 | 1,05 | -0,83 | -1,43 | 12,0 | 30,25% |
| RN | 46 | 2026-B4 | 2026-Q2 | 4 (0 em B6) | 21,1 | 21,2 | -0,23 | 0,71 | 0,68 | 9,5 | 48,55% |
| PB | 45 | 2026-B3 | 2026-Q1 | 5 (1 em B6) | 23,1 | 23,1 | nulo | -1,44 | -0,82 | 0,7 | 3,20% |
| PE | 45 | 2026-B3 | 2026-Q1 | 0 (0 em B6) | 52,5 | 52,4 | 0,02 | -0,90 | -1,82 | 15,0 | 31,75% |
| AL | 46 | 2026-B4 | 2026-Q2 | 0 (0 em B6) | 21,0 | 22,1 | -1,14 | 0,89 | -0,48 | 13,5 | 71,45% |
| SE | 45 | 2026-B3 | 2026-Q1 | 2 (1 em B6) | 18,0 | 17,7 | 0,35 | 0,30 | 0,48 | 1,2 | 7,04% |
| BA | 45 | 2026-B3 | 2026-Q1 | 3 (0 em B6) | 78,1 | 77,6 | 0,48 | -0,88 | -1,86 | 24,6 | 35,67% |
| MG | 45 | 2026-B3 | 2026-Q1 | 3 (0 em B6) | 118,7 | 117,5 | 1,11 | 4,73 | -10,58 | 187,1 | 167,46% |
| ES | 45 | 2026-B3 | 2026-Q1 | 2 (0 em B6) | 31,5 | 30,5 | 0,89 | 0,01 | 0,36 | -14,7 | -52,50% |
| RJ | 45 | 2026-B3 | 2026-Q1 | 4 (0 em B6) | 108,7 | 105,9 | 1,30 | 1,22 | -20,56 | 218,4 | 217,25% |
| SP | 45 | 2026-B3 | 2026-Q1 | 7 (1 em B6) | 358,9 | 371,2 | -12,22 | 8,46 | -23,92 | 330,5 | 124,23% |
| PR | 45 | 2026-B3 | 2026-Q1 | 0 (0 em B6) | 75,3 | 75,8 | -0,87 | -5,60 | -3,12 | -3,5 | -4,92% |
| SC | 46 | 2026-B4 | 2026-Q2 | 0 (0 em B6) | 54,0 | 54,0 | -0,03 | 0,01 | -0,21 | 11,9 | 23,33% |
| RS | 45 | 2026-B3 | 2026-Q1 | 3 (1 em B6) | 72,3 | 69,6 | 2,67 | -1,59 | -3,16 | 113,4 | 174,03% |
| MS | 46 | 2026-B4 | 2026-Q2 | 0 (0 em B6) | 24,5 | 24,5 | -0,04 | -0,21 | -1,01 | 5,5 | 24,96% |
| MT | 46 | 2026-B4 | 2026-Q2 | 4 (0 em B6) | 39,6 | 39,4 | 0,09 | 0,27 | 0,54 | -5,5 | -14,91% |
| GO | 46 | 2026-B4 | 2026-Q2 | 1 (0 em B6) | 47,8 | 53,0 | -5,30 | -4,56 | -4,49 | 15,2 | 33,47% |
| DF | 45 | 2026-B3 | 2026-Q1 | 1 (0 em B6) | 39,1 | 40,4 | -1,29 | -0,93 | -0,81 | 6,2 | 15,91% |

### 5.2 Prefeituras de Santa Catarina (295)

"Entregou" quer dizer que a prefeitura tem o Anexo 01 do RREO no período, por qualquer um dos dois tipos. As colunas de anexo contam quantas têm cada anexo; a de RGF conta quantas têm o Anexo 02 do RGF no ano. Em 2026, a última coluna mostra em que bimestre está cada prefeitura.

| Ano | Entregaram | RREO | RREO Simplificado | Anexo 01 | Anexo 02 | Anexo 03 | Anexo 06 | RGF | Período |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 294 de 295 | 249 | 45 | 294 | 294 | 294 | 294 | 294 | 2021-B6: 294 |
| 2022 | 295 de 295 | 254 | 41 | 295 | 295 | 295 | 295 | 295 | 2022-B6: 295 |
| 2023 | 295 de 295 | 255 | 40 | 295 | 295 | 295 | 295 | 295 | 2023-B6: 295 |
| 2024 | 295 de 295 | 254 | 41 | 295 | 295 | 295 | 295 | 295 | 2024-B6: 295 |
| 2025 | 294 de 295 | 255 | 39 | 294 | 294 | 294 | 294 | 294 | 2025-B6: 294 |
| 2026 | 293 de 295 | 256 | 37 | 293 | 293 | 270 | 270 | 293 | 2026-B2: 5, 2026-B3: 51, 2026-B4: 237 |

Prefeituras sem relatório no período (os dois tipos tentados):

- 2021: Brunópolis
- 2022: nenhuma
- 2023: nenhuma
- 2024: nenhuma
- 2025: Vargem
- 2026: Armazém, Vargem

Quantas prefeituras fecharam o ano com sobra ou falta (uma linha por prefeitura; em 2026 o ano ainda não fechou e o Anexo 01 compara com o gasto liquidado, que costuma atrasar em relação à receita, então a maioria aparece com sobra no meio do ano):

| Ano | Primário positivo | Primário negativo | Anexo 01 positivo | Anexo 01 negativo | Anexo 01 nulo |
|---|---|---|---|---|---|
| 2021 | 255 | 39 | 238 | 35 | 21 |
| 2022 | 220 | 75 | 186 | 86 | 23 |
| 2023 | 122 | 173 | 162 | 116 | 17 |
| 2024 | 169 | 126 | 199 | 89 | 7 |
| 2025 | 251 | 43 | 248 | 44 | 2 |
| 2026 (parcial, até o último bimestre de cada uma) | 274 | 19 | 290 | 3 | 0 |

## 6. Checagens

Cada checagem roda primeiro contra um controle quebrado de propósito (um valor alterado, uma função removida, o analisador antigo) e precisa falhar nele; só depois roda nos dados reais. Script: `pipelines/series/checks_series.py`. Saída da última execução:

```
== 1. data/state-budgets-2024.json reproduced by the 2024-B6 period
[OK] reproduction of the 27 states (functions, subfunctions, revenue lines, totals): control fails with 2 error(s) (expected > 0); real data has 0 error(s) (expected 0)
      note: the 2024 file carries 54 leaked total rows inside 'Encargos Especiais' subfunctions (2 per state); the comparison ignores exactly those, and the new series does not have them
== 2. sum of functions == Anexo 02 total, and sum of subfunctions == function (every state, every bimester)
[OK] function sums, states: control fails with 2 error(s) (expected > 0); real data has 0 error(s) (expected 0)
      control detail: [('2024-B6 (old parser, leak)', 'Encargos Especiais', 50108845132.98), ('2024-B6 (one function dropped)', 'functions', -10148987189.69)]
      states checked per year: {'2019': 27, '2020': 27, '2021': 27, '2022': 27, '2023': 27, '2024': 27, '2025': 27, '2026': 27}
[OK] function sums, SC municipalities (1789 municipality-periods): control fails with 2 error(s) (expected > 0); real data has 0 error(s) (expected 0)
== 3. Anexo 01 budget_result: every value kept equals total revenue - total executed spending of the same annex
[OK] budget_result identity, states (1228 reports): control fails with 1 error(s) (expected > 0); real data has 0 error(s) (expected 0)
      line as filed, by bimester: {('B1-B5', 'inconsistent'): 21, ('B1-B5', 'missing'): 48, ('B1-B5', 'ok'): 970, ('B6', 'inconsistent'): 2, ('B6', 'missing'): 10, ('B6', 'ok'): 177} (ok = kept; missing and inconsistent = null with the reason in the period's nulls)
[OK] budget_result identity, SC municipalities (1789 municipality-periods): control fails with 1 error(s) (expected > 0); real data has 0 error(s) (expected 0)
      line as filed: {'ok': 1719, 'inconsistent': 27, 'missing': 43}
== 4. Anexo 03: the 12 monthly columns add up to the 12-month total (states, every report)
[OK] monthly columns vs 12-month total (36241 line-reports): control fails with 1 error(s) (expected > 0); real data has 0 error(s) (expected 0)
== 5. monthly revisions: the same month in a later report of the next year (diagnostic, not a failure)
      2848 of 153538 (line, month) values differ between the year's own last report and a report of the next year; examples: [('RO', 'RECEITAS CORRENTES (I)', '2021-03', 904426447.05, '2022-B1', 905514094.83), ('RO', 'Transferências Correntes', '2021-03', 379865955.89, '2022-B1', 380953603.67), ('RO', 'Transferências do FUNDEB', '2021-03', 80362140.3, '2022-B1', 81449788.08), ('RO', 'RECEITA CORRENTE LÍQUIDA (III) = (I - II)', '2021-03', 668345415.32, '2022-B1', 669433063.1), ('RO', 'RECEITA CORRENTE LÍQUIDA AJUSTADA PARA CÁLCULO DOS LIMITES DE ENDIVIDAMENTO (V) = (III - IV)', '2021-03', 668345415.32, '2022-B1', 669433063.1)]
== 6. RGF: 'saldo do exercício anterior' of year Y == DC/DCL at the end of Y-1 (diagnostic)
      19 differences in 189 year pairs; examples: [('RR', 2019, 'dcl', 1627286620.94, 1481202178.18), ('PI', 2021, 'dcl', 5369389881.72, 5545089559.36), ('AL', 2019, 'dcl', 6404121918.62, 6477034731.52), ('AL', 2021, 'dcl', 4758264282.23, 4892885209.4), ('AL', 2022, 'dc', 10359518124.82, 11647507757.57), ('AL', 2022, 'dcl', 7245315323.33, 8940683840.54)]
== 7. Anexo 02 total - Anexo 01 liquidated spending == debt refinancing line of Anexo 01 (every state-period)
[DIAG] Anexo 01 vs Anexo 02 spending totals explained by refinancing: control fails with 1 error(s) (expected > 0); real data has 6 difference(s) as filed
       ('AP 2021-B5', -8350846.19, 0)
       ('CE 2022-B3', 28000.0, 0)
       ('AL 2019-B4', 20.0, 0)
       ('MG 2025-B3', -82655.18, 0)
       ('RJ 2019-B3', 4363614, 4363612)
       ('RJ 2019-B4', 5803147, 5803150)
      200 state-periods have debt refinancing, which Anexo 01 keeps outside 'DESPESAS (EXCETO INTRA)' and Anexo 02 includes
== 8. Union: revenue - transfers == net revenue; net revenue - spending == primary result; primary (below the line) + interest == nominal
[OK] Union identities (92 months): control fails with 1 error(s) (expected > 0); real data has 0 error(s) (expected 0)
== 9. Union: the monthly RTN values add up to the RTN's own annual table (Tabela 2.1), 2019 to 2025
[OK] Union monthly sums vs RTN annual table: control fails with 1 error(s) (expected > 0); real data has 0 error(s) (expected 0)
RESULT: all checks passed
```

Leitura:

1. **O arquivo de 2024 é reproduzido pelo período 2024-B6** nos 27 estados: funções, subfunções, as 13 linhas de receita, o total de despesas, a receita corrente, o repasse aos municípios e a dedução do Fundeb, valor por valor. A única diferença são as 54 linhas vazadas do arquivo antigo (seção 7.1).
2. **Soma das funções igual ao total do Anexo 02**, e soma das subfunções igual a cada função, em todos os 1.228 períodos estaduais e nos 1.789 períodos municipais. A segunda soma é nova: ela pega o vazamento do analisador antigo, que a primeira soma não pegava.
3. **Resultado do Anexo 01:** todo valor mantido bate com os totais do próprio anexo, relido de forma independente pelo nome da linha.
4. **Receita mensal:** as 12 colunas mensais somam o total de 12 meses em todas as 36.241 linhas de relatório estaduais.
5. **Anexo 01 contra Anexo 02:** dos 204 períodos em que o gasto liquidado dos dois anexos difere, 198 diferem exatamente pela linha de refinanciamento da dívida; sobram 6 diferenças enviadas assim pelos estados (listadas na saída).
6. **União:** receita total menos transferências igual à receita líquida, receita líquida menos despesa igual ao primário, primário abaixo da linha mais juros igual ao nominal, nos 92 meses; e a soma dos meses igual à tabela anual do próprio RTN (Tabela 2.1), de 2019 a 2025.

## 7. Ressalvas

1. **Achado no arquivo de 2024.** O script `pipelines/siconfi/build_state_budgets.py` deixa as duas linhas que vêm depois da última função ("DESPESAS (INTRA-ORÇAMENTÁRIAS) (II)" e "TOTAL (III) = (I + II)") caírem dentro das subfunções de "Encargos Especiais". São 54 linhas, 2 por estado; em SC, a maior "subfunção" de Encargos Especiais aparece como "TOTAL (III)", R$ 47,9 bi. Os totais das funções estão certos, por isso a checagem antiga passava. O arquivo não foi alterado nesta tarefa; a série nova não tem o erro.
2. **Dados declarados.** O SICONFI publica o que cada governo envia. Há relatórios com linhas vazias ou que contradizem o próprio anexo: a linha de SUPERÁVIT ou DÉFICIT do Anexo 01 ficou nula em 69 relatórios estaduais dos bimestres 1 a 5, em 12 do 6º bimestre e em 70 dos 1.789 períodos municipais (43 sem a linha, 27 com valor que não bate). O motivo está em `nulls` de cada período.
3. **Quebra de série no resultado nominal em 2023.** Até 2022, o nominal acima da linha inclui a previdência dos servidores; desde 2023, o anexo só traz o nominal acima da linha sem ela. O primário não tem essa quebra (usa sempre o "com RPPS"). O site não deve comparar o nominal de 2022 com o de 2023 sem avisar.
4. **Acima e abaixo da linha dão números diferentes** (em SC, 2022: nominal acima da linha, R$ -0,95 bi; abaixo da linha, R$ +0,24 bi). O arquivo usa o acima da linha e guarda os outros em `results_reported`.
5. **Refinanciamento.** O total de despesa do Anexo 01 (`spending_*`) não inclui o refinanciamento da dívida; o total do Anexo 02 inclui. Em 200 dos 1.228 períodos estaduais os dois diferem por isso.
6. **Revisões.** Um relatório mais novo pode trazer outro valor para um mês antigo: 2.848 de 153.538 pares (linha, mês) diferem entre o relatório do próprio ano e o do ano seguinte. A regra é usar o do próprio ano. No RGF, o saldo do ano anterior foi reapresentado em 19 de 189 casos; o arquivo usa o fim de ano do RGF do próprio ano. A série do RTN também é revisada: os números podem diferir dos anunciados na época.
7. **Valores nominais.** Nada está corrigido pela inflação. Comparar 2019 com 2026 sem corrigir exagera o crescimento.
8. **Escopos diferentes na União.** Os resultados são do Governo Central (Tesouro, Previdência e Banco Central); a dívida bruta é do governo geral (inclui estados e municípios).
9. **Receita dos estados é bruta.** `revenue_lines` traz o ICMS e o IPVA inteiros; a parte que vai para as prefeituras está em `to_municipalities`, como no arquivo de 2024.
10. **SUS nas prefeituras.** O Anexo 03 não tem linha própria para o SUS: os repasses estão dentro de "Outras Transferências Correntes", porque as demais linhas de transferência têm fonte com nome (FPM, ICMS, IPVA, ITR, LC nº 61/1989 e Fundeb) e o SUS não é nenhuma delas. O valor separado está no Anexo 12 (Saúde), que esta série não coleta; cada período municipal traz esse aviso em `nulls.sus_transfers`.
11. **2026 é parcial** e muda nas próximas semanas: o prazo do 4º bimestre é hoje e o do 5º é 30/11/2026. Nas prefeituras, o último bimestre de 2026 varia de uma para outra (campo `period` da cobertura).
12. **Tamanho dos arquivos.** `state-budgets.json` tem cerca de 12 MB e `sc-municipal-budgets.json` cerca de 21 MB, porque trazem as subfunções de cada período e a receita mês a mês de cada linha. O site deve carregar um estado ou um município por vez.

## 8. Diário de transparência

1. Leitura do `README.md` e dos dois scripts do SICONFI. Armadilha herdada: prefeituras pequenas entregam o "RREO Simplificado"; os dois tipos são sempre tentados, também no RGF (que tem o "RGF Simplificado" semestral).
2. Teste da API sem `id_ente` para baixar todos os estados de uma vez: zero linhas. Uma chamada por governo, período e anexo.
3. O disco do computador tinha 4,2 GB livres. O cache passou a guardar cada resposta comprimida e sem os campos repetidos (sem perder informação): 43 MB para os 27 estados.
4. Comparando o analisador com o arquivo de 2024, apareceram as 54 linhas vazadas (ressalva 1). A série nova para de ler subfunções na linha das intraorçamentárias; a checagem de soma das subfunções foi criada para pegar esse tipo de erro.
5. O Anexo 06 muda de modelo: até 2022, uma linha de primário e uma de nominal; desde 2023, com e sem RPPS (conferido em todos os 1.228 períodos estaduais pelo nome da linha usada); a coluna onde o resultado aparece também muda (em 2019, "VALOR INCORRIDO"; em 2022 e 2024, conferidos, "VALOR"), e o analisador aceita as duas. O analisador procura as linhas pelo nome ("RESULTADO PRIMÁRIO ... Acima da Linha") e guarda o nome exato da linha usada.
6. O catálogo de dados do Tesouro ainda oferecia a série do RTN até julho; a página do boletim de agosto, publicada em 29/09/2026, tinha a série até agosto. Foi usada a de agosto.
7. Os números das séries do SGS foram conferidos no serviço de metadados do Banco Central: 13761 é a dívida bruta em R$ milhões e 13762, em % do PIB.
8. A primeira rodada das checagens falhou no resultado do Anexo 01: 657 relatórios sem a linha na coluna das empenhadas e 79 com valor diferente dos totais. Duas causas. Primeira: a base muda com o bimestre (liquidadas nos bimestres 1 a 5, empenhadas no 6º), o que os próprios dados mostram. Segunda, um erro deste script: no modelo de 2019, as linhas chamadas "TOTAL" já incluem o superávit ou o déficit, e a comparação certa é com os subtotais "com refinanciamento". Corrigido; restaram 69 + 12 relatórios nulos, cada um com o motivo.
9. A diferença entre o gasto liquidado do Anexo 01 e o total do Anexo 02 (204 períodos estaduais) foi explicada, ao centavo, pela linha de refinanciamento da dívida em 198 deles; os 6 restantes são diferenças enviadas pelos estados, de R$ 2 a R$ 8,35 mi (dois deles no RJ, em 2019, com R$ 2 e R$ 3 de diferença na própria linha de refinanciamento).
10. A mesma linha do Anexo 03 aparece escrita de dois jeitos em anos diferentes ("( - )" e "(-)"); os nomes foram normalizados para a série mensal não se partir.
11. Uma busca na web para citar o Manual de Demonstrativos Fiscais sobre a base do resultado do Anexo 01. A página do manual não mostrou o texto; a regra fica apoiada nos dados (item 8) e a citação ficou como pendência.
12. Para o mandato 2019 a 2022 ter ponto de partida, a dívida de dezembro de 2018 foi incluída (SGS e coluna do RGF de 2019).
13. As prefeituras de SC foram coletadas depois dos estados, também com no máximo 6 chamadas ao mesmo tempo (cerca de 18 minutos, 36 MB de cache).
14. 23 prefeituras que usam o RREO Simplificado mandaram o 4º bimestre de 2026 só com os Anexos 01 e 02. A LRF, art. 63, II, "c" (texto conferido no site do Planalto), deixa os municípios com menos de 50 mil habitantes divulgarem por semestre os demonstrativos do art. 53, que incluem a receita corrente líquida e os resultados. O 3º bimestre dessas prefeituras tem os dois anexos e entrou como um período separado (`2026-B3`), com o aviso no período `2026-B4`.
15. Quatro casos sem nenhum RREO na API foram consultados de novo, nos seis bimestres e nos dois tipos: Brunópolis (2021), Vargem (2025 e 2026) e Armazém (2026). A API não devolve relatório; isso mostra que o dado não está publicado na API na data da coleta, não prova que a prefeitura deixou de entregar.
16. Conferência cruzada com um arquivo que já existia: a soma de IPTU, ISS, ITBI, IR retido e outros impostos das 295 prefeituras em 2024 é igual, ao centavo, à linha de SC de `data/municipal-taxes-2024.json`.

## 9. Como reproduzir

```bash
cd "$(git rev-parse --show-toplevel)/pipelines/series"
python3 fetch_state_series.py          # cerca de 13 min na primeira vez; retoma do cache
python3 build_state_series.py
python3 fetch_sc_municipal_series.py   # cerca de 20 min na primeira vez; retoma do cache
python3 build_sc_municipal_series.py
python3 build_union_series.py          # precisa de openpyxl
python3 checks_series.py               # a checagem 9 precisa de openpyxl
```

O cache fica em `pipelines/series/cache/`, com um `.gitignore` próprio (o `.gitignore` da raiz não foi alterado). Uma nova coleta pode dar números um pouco diferentes se os governos reenviarem relatórios.

## 10. Pendências

1. Acrescentar estes arquivos à tabela "Arquivos" do `README.md` (não alterado nesta tarefa).
2. Regerar ou corrigir `data/state-budgets-2024.json` (ressalva 1); o período 2024-B6 da série nova já tem os valores certos.
3. Conferir no Manual de Demonstrativos Fiscais o texto da regra da base do resultado do Anexo 01.
4. Se o site precisar do SUS por prefeitura, coletar o RREO Anexo 12.
5. Rodar de novo depois de 30/09/2026 para pegar o 4º bimestre dos 14 estados que ainda não aparecem e das prefeituras atrasadas.
6. Decidir se o site mostra valores corrigidos pela inflação e como avisa a quebra do resultado nominal em 2023.
