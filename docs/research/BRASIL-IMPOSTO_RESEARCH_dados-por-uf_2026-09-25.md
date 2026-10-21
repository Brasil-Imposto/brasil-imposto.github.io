# Dados por UF: arrecadação federal, transferências e gasto direto da União

**Data da coleta:** 2026-09-25
**Ano de referência usado:** 2024 (ver seção 1)
**Arquivo de dados:** `data/uf-balance-2024.json` (27 objetos, valores em reais nominais, com fonte por campo)
**Regra seguida:** nenhum número estimado. Tudo o que está aqui foi somado a partir de arquivos oficiais; onde não houve fonte, o campo é `null` e o motivo está escrito.

---

## 0. Resumo em uma tela

| Pergunta | Resposta curta |
|---|---|
| Qual ano usar | **2024.** O ano de 2025 está completo no arquivo da Receita, mas a distribuição por UF de 2025 tem uma quebra: o DF salta de 6,9% para 20,4% da arrecadação federal, enquanto SP, RJ e os demais caem (seção 1.3). |
| Arrecadação federal por UF | 27 de 27 UFs, por tributo. A soma das UFs bate com o total nacional da Receita com diferença de R$ 1,37 bi (0,05%) em 2024. |
| Transferências por UF | 27 de 27 UFs, estado mais municípios, em 18 categorias. FPE, FPM, IPI-Exportação, ITR e LC 176 conferem com o Tesouro Nacional até o centavo. |
| Gasto direto por UF | INSS (27/27), Bolsa Família (27/27), FCDF (só DF). **Folha federal por UF: `null`** (sem fonte aberta viável). 90% do gasto direto primário da União está registrado como "Nacional" no SIAFI. |
| População | 27 de 27 UFs, IBGE, estimativas 2024, 2025 e 2026. |

---

## 1. Arrecadação federal por UF

### 1.1 Fonte

- **Receita Federal, "Arrecadação por Estado"**, arquivo único com todos os anos, mensal, por tributo, a preços correntes: https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv
- Página do conjunto: https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/arrecadacao-por-estado/arrecadacao-por-estado
- Total nacional para a conciliação: **série histórica da Receita, 1994 a 2025** (XLSX, uma aba por ano, R$ milhões): https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/serie-historica/arrecadacao-das-receitas-federais-1994-a-2025.xlsx
- Cobertura do arquivo por UF: janeiro de 2000 a julho de 2026. **2024 e 2025 estão completos** (12 meses × 27 UFs). 2026 vai até julho.

No JSON, `federal_revenue.by_tax` traz: Imposto de Importação, Imposto de Exportação, IPI (5 colunas somadas), IRPF, IRPJ (financeiras e demais), IRRF (trabalho, capital, remessas ao exterior, outros), IOF, ITR, COFINS, PIS/PASEP, CSLL, CIDE-Combustíveis, PSS dos servidores, outras receitas administradas, receita previdenciária (RGPS) e receitas administradas por outros órgãos. `total` é a soma de tudo e corresponde ao "TOTAL GERAL" da Receita; `rfb_administered` exclui as receitas administradas por outros órgãos.

### 1.2 Conciliação: soma das UFs contra o total nacional

| Tributo | Soma das UFs 2024 (R$ mi) | Nacional 2024 (R$ mi) | Diferença 2024 (R$ mi) | Soma das UFs 2025 (R$ mi) | Nacional 2025 (R$ mi) | Diferença 2025 (R$ mi) |
|---|---:|---:|---:|---:|---:|---:|
| Imposto de Importação | 73.436,6 | 77.876,8 | -4.440,1 | 90.814,2 | 90.814,2 | 0,0 |
| Imposto de Exportação | 3.084,0 | 9,5 | 3.074,4 | 1,9 | 1,9 | 0,0 |
| IPI | 80.526,4 | 80.526,4 | 0,0 | 86.688,1 | 86.688,1 | 0,0 |
| IRPF | 70.539,4 | 70.539,4 | 0,0 | 77.247,3 | 77.247,3 | 0,0 |
| IRPJ | 320.259,3 | 320.259,3 | 0,0 | 337.187,7 | 337.187,7 | 0,0 |
| IRRF | 444.994,6 | 444.994,6 | 0,0 | 501.132,2 | 501.132,2 | 0,0 |
| IOF | 67.410,5 | 67.410,5 | 0,0 | 85.413,5 | 85.413,5 | 0,0 |
| ITR | 3.523,2 | 3.523,2 | 0,0 | 4.149,1 | 4.149,1 | 0,0 |
| COFINS | 417.234,1 | 417.234,1 | 0,0 | 451.749,1 | 451.749,1 | 0,0 |
| PIS/PASEP | 113.361,9 | 113.361,9 | 0,0 | 122.169,2 | 122.169,2 | 0,0 |
| CSLL | 170.733,9 | 170.733,9 | 0,0 | 184.662,6 | 184.662,6 | 0,0 |
| CIDE-Combustíveis | 2.914,5 | 2.914,5 | 0,0 | 3.232,5 | 3.232,5 | 0,0 |
| PSS (servidores) | 41.873,3 | 41.873,3 | 0,0 | 43.083,2 | 43.083,2 | 0,0 |
| Outras receitas administradas | 41.607,1 | 41.607,1 | 0,0 | 50.392,7 | 47.885,3 | 2.507,5 |
| Receita previdenciária (RGPS) | 671.357,5 | 671.357,8 | -0,3 | 694.874,3 | 727.846,5 | -32.972,2 |
| Administradas por outros órgãos | 128.480,0 | 128.479,6 | 0,4 | 123.006,0 | 123.612,4 | -606,4 |
| **TOTAL GERAL** | 2.651.336,3 | 2.652.701,8 | -1.365,6 | 2.855.803,7 | 2.886.874,8 | -31.071,1 |

**2024:** a soma das 27 UFs fica **R$ 1.365,6 milhões abaixo** do total nacional (0,05%). Toda a diferença está em **setembro de 2024**: no arquivo por UF, o Imposto de Importação daquele mês soma R$ 2.742,4 mi contra R$ 7.182,6 mi na série nacional, e o Imposto de Exportação soma R$ 3.074,6 mi contra R$ 0,2 mi. Parte do Imposto de Importação de setembro foi lançada na coluna do Imposto de Exportação (em SP, RS, SC, MG, PR, RJ e ES, entre outras), e R$ 1,37 bi não aparecem em UF nenhuma. Todos os outros tributos batem até o milhão.

**2025:** a soma das UFs fica **R$ 31.071,1 milhões abaixo** do total nacional (1,08%). Quase tudo é receita previdenciária: R$ 32.972,2 mi do RGPS não estão atribuídos a UF nenhuma. Em "outras receitas administradas" a soma das UFs passa do nacional em R$ 2.507,5 mi. O arquivo não explica nenhuma das duas diferenças.

### 1.3 Por que 2025 não serve para o mapa (por enquanto)

A conciliação do total de 2025 é quase boa, mas a **distribuição entre UFs quebrou**. A participação do DF na arrecadação federal foi de 7,7% (2019), 8,0% (2020), 7,3% (2021), 7,1% (2022), 7,2% (2023), 6,9% (2024) e, de repente, **20,4% em 2025**.

| UF | 2024 (R$ bi) | 2025 (R$ bi) | Variação (R$ bi) | Participação 2024 | Participação 2025 |
|---|---:|---:|---:|---:|---:|
| SP | 1.036,61 | 964,73 | -71,88 | 39,1% | 33,8% |
| RJ | 459,20 | 401,66 | -57,54 | 17,3% | 14,1% |
| DF | 184,10 | 583,46 | 399,37 | 6,9% | 20,4% |
| MG | 177,39 | 166,53 | -10,87 | 6,7% | 5,8% |
| SC | 140,22 | 135,27 | -4,95 | 5,3% | 4,7% |
| PR | 123,15 | 108,00 | -15,15 | 4,6% | 3,8% |
| RS | 120,22 | 108,32 | -11,90 | 4,5% | 3,8% |
| BA | 56,08 | 51,39 | -4,68 | 2,1% | 1,8% |
| ES | 49,18 | 49,70 | 0,52 | 1,9% | 1,7% |
| PE | 42,08 | 39,16 | -2,92 | 1,6% | 1,4% |
| GO | 41,84 | 38,60 | -3,24 | 1,6% | 1,4% |
| CE | 38,49 | 35,39 | -3,10 | 1,5% | 1,2% |
| AM | 26,26 | 22,03 | -4,23 | 1,0% | 0,8% |
| MT | 25,79 | 23,67 | -2,12 | 1,0% | 0,8% |
| PA | 23,05 | 22,45 | -0,61 | 0,9% | 0,8% |
| MS | 17,15 | 15,46 | -1,69 | 0,6% | 0,5% |
| MA | 15,56 | 16,39 | 0,83 | 0,6% | 0,6% |
| PB | 13,63 | 13,38 | -0,25 | 0,5% | 0,5% |
| RN | 11,40 | 11,08 | -0,32 | 0,4% | 0,4% |
| AL | 10,97 | 11,09 | 0,12 | 0,4% | 0,4% |
| PI | 8,90 | 8,93 | 0,02 | 0,3% | 0,3% |
| RO | 8,70 | 9,08 | 0,38 | 0,3% | 0,3% |
| SE | 8,25 | 7,48 | -0,77 | 0,3% | 0,3% |
| TO | 5,79 | 5,41 | -0,38 | 0,2% | 0,2% |
| AP | 2,74 | 2,72 | -0,02 | 0,1% | 0,1% |
| AC | 2,40 | 2,28 | -0,12 | 0,1% | 0,1% |
| RR | 2,19 | 2,14 | -0,05 | 0,1% | 0,1% |
| **Soma** | 2.651,34 | 2.855,80 | 204,47 | 100% | 100% |

Mês a mês, a arrecadação federal atribuída ao DF foi de R$ 13 bi a 19 bi em cada mês de 2024; de **fevereiro de 2025 a janeiro de 2026** ficou entre R$ 30 bi e 64 bi por mês; e voltou a R$ 14,5 bi em fevereiro de 2026. Os tributos que mais saltaram no DF entre 2024 e 2025: receita previdenciária (R$ 31,8 bi para 178,5 bi), IRRF do trabalho (48,3 para 112,8), COFINS demais (8,1 para 74,7), IRPJ demais (9,0 para 58,1), CSLL demais (4,1 para 30,2) e PIS demais (7,2 para 25,9). No mesmo período, a receita previdenciária de SP caiu de R$ 249,1 bi para 188,0 bi.

Isso é um problema de atribuição de UF no conjunto de dados, não um fato econômico. **Hipótese não confirmada pela Receita:** o período coincide com a entrada do MIT/DCTFWeb (declaração de tributos que substituiu a DCTF a partir dos fatos geradores de janeiro de 2025, com a primeira entrega em fevereiro), e os pagamentos por DARF gerados nesse sistema podem estar sendo atribuídos à UF errada. Não encontrei nota sobre isso na página do conjunto.

Por isso o JSON e as tabelas de saldo usam **2024**. Quando a Receita corrigir 2025, basta refazer a soma: o script de agregação já está pronto.

### 1.4 Números que a Receita publicou para 2025 (nacionais)

Da mesma série histórica (aba 2025): **TOTAL GERAL R$ 2.886.874,8 milhões**; administradas pela RFB R$ 2.763.262,4 milhões; administradas por outros órgãos R$ 123.612,4 milhões. A notícia oficial sobre esse resultado (gov.br/receitafederal, janeiro de 2026) responde "Conteúdo Restrito, é necessário autenticar" para acesso automatizado; por isso o número acima vem da planilha, não da notícia.

---

## 2. Transferências federais por UF (governo estadual mais todos os municípios)

### 2.1 Fontes

- **CGU, Portal da Transparência, Transferências**, 12 arquivos mensais de 2024: https://portaldatransparencia.gov.br/download-de-dados/transferencias/202401 (e assim até 202412). Sem chave, sem login. Coluna somada: `VALOR TRANSFERIDO`. Total bruto do arquivo em 2024: R$ 761,14 bi em 1.931.230 linhas.
- **Tesouro Nacional, Transferências Obrigatórias da União** (CKAN do Tesouro Transparente): https://www.tesourotransparente.gov.br/ckan/dataset/transferencias-obrigatorias-da-uniao . Usado para (a) conferir FPE, FPM, IPI-Exportação e ITR e (b) obter a LC 176 por UF, que o Portal registra sem UF.

### 2.2 O que entrou e o que ficou de fora

- **Entrou:** tudo o que foi pago à administração pública estadual ou municipal (tipos de favorecido "Administração Pública Estadual ou do Distrito Federal", "Administração Pública Municipal" e "Administração Pública", este último excluindo a modalidade 80, que é transferência ao exterior). Isso inclui os fundos estaduais e municipais de saúde, educação e assistência. Também entraram R$ 0,99 bi pagos via "Agentes Intermediários" ao RS em 2024 (ações 00VP, compensação ao estado, e 00WF, apoio aos municípios gaúchos), que o Portal registra com UF.
- **Ficou de fora do total do Portal (R$ 25,01 bi, dos quais R$ 3,99 bi da LC 176 foram repostos por UF via Tesouro, ver abaixo):** transferências a entidades sem fins lucrativos (R$ 17,8 bi no total, com destaque para SP R$ 5,29 bi e DF R$ 4,26 bi), a organismos internacionais (R$ 1,99 bi) e a empresas privadas, e R$ 1,25 bi de contribuições a organismos internacionais sem UF. Não são repasses ao estado nem aos municípios.
- **LC 176/2020 (compensação da Lei Kandir), R$ 3,99 bi:** no Portal aparece como "Agentes Intermediários" e **sem UF**. Os valores por UF vieram do Tesouro (arquivos LC176_EST e LC176_MUN), e a soma bate com o Portal até o centavo (R$ 3.985.563.374,52).
- **Convênios e transferências voluntárias:** o arquivo do Portal junta "Legais, Voluntárias e Específicas" num único tipo. Os pagamentos desse tipo a estados e municípios estão dentro das categorias por função (SUS, educação, assistência) ou em `other_legal_and_voluntary`. Não foi usado o conjunto separado de convênios.

### 2.3 Um detalhe que muda o total: FPE e FPM chegam líquidos do Fundeb

O FPE, o FPM, o IPI-Exportação e o ITR aparecem no SIAFI (e portanto no Portal e no Tesouro) **já deduzidos** dos 20% retidos para o Fundeb. O próprio CSV do Tesouro diz: "Obs: os valores já estão deduzidos da retenção para o FUNDEF/FUNDEB". A parcela retida aparece em outra ação orçamentária, **0C33, "Transferência ao Fundeb"** (R$ 78,98 bi em 2024), e volta para a mesma UF (o Fundeb de cada estado é repartido entre o governo estadual e os municípios daquele estado). Por isso o JSON soma a ação 0C33 como `fundeb_retention_on_federal_transfers`: sem ela, o FPE, o FPM, o IPI-Exportação e o ITR ficariam subcontados nos 20% retidos. A complementação da União ao Fundeb (ação 00SB, R$ 46,73 bi) é outra coisa, dinheiro novo da União, e está em `fundeb_federal_complement`.

Conferência com o Tesouro (2024, soma das 27 UFs):

| Transferência | Portal da Transparência | Tesouro Nacional | Diferença |
|---|---:|---:|---:|
| FPE (líquido do Fundeb) | R$ 149.831.128.137,61 | R$ 149.831.128.137,61 | 0,00 |
| FPM (líquido do Fundeb) | R$ 177.034.137.398,90 | R$ 177.034.137.398,90 | 0,00 |
| IPI-Exportação | R$ 6.765.493.564,94 | R$ 6.765.493.564,94 | 0,00 |
| ITR (cota municipal) | R$ 2.517.599.071,45 | R$ 2.517.599.071,45 | 0,00 |
| LC 176 | R$ 3.985.563.374,52 (sem UF) | R$ 3.985.563.374,52 | 0,00 |

### 2.4 Totais nacionais por categoria (2024, 27 UFs)

| Categoria (chave no JSON) | R$ bi |
|---|---:|
| FPE líquido (`fpe_net_of_fundeb`) | 149,83 |
| FPM líquido (`fpm_net_of_fundeb`) | 177,03 |
| IPI-Exportação líquido | 6,77 |
| ITR, cota municipal líquida | 2,52 |
| Fundeb: retenção de 20% das transferências federais (ação 0C33) | 78,98 |
| Fundeb: complementação da União (ação 00SB) | 46,73 |
| Royalties de petróleo e gás (ação 0A53) | 58,67 |
| CFEM, royalties minerais (ação 0547) | 6,73 |
| Compensação por recursos hídricos e Itaipu (0546 e 0223) | 3,19 |
| CIDE-Combustíveis, cota-parte | 0,98 |
| IOF-Ouro | 0,01 |
| LC 176 (Lei Kandir), via Tesouro | 3,99 |
| Salário-educação, quotas estadual e municipal (ação 0369) | 19,57 |
| SUS fundo a fundo e demais repasses da função saúde | 148,00 |
| FNDE e demais repasses da função educação | 10,66 |
| SUAS, função assistência social | 4,58 |
| Transferências especiais, "emendas Pix" (ação 0EC2) | 7,68 |
| Demais legais e voluntárias | 14,20 |
| **Total** | **740,12** |

### 2.5 Transferências por UF, por grupo (2024, R$ bi)

| UF | FPE líq. | FPM líq. | Fundeb: retenção 20% das transf. federais | Fundeb: complementação da União | Royalties e compensações financeiras | SUS fundo a fundo | Salário-educação + FNDE | Demais (IPI-Exp, ITR, CIDE, IOF-Ouro, LC 176, SUAS, emendas Pix, outras) | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RO | 4,20 | 1,57 | 1,41 | 0,03 | 0,24 | 1,40 | 0,26 | 0,69 | 9,81 |
| AC | 5,44 | 0,96 | 1,57 | 0,10 | 0,06 | 0,91 | 0,18 | 0,59 | 9,82 |
| AM | 5,20 | 3,11 | 2,00 | 2,85 | 0,62 | 3,52 | 0,84 | 0,90 | 19,04 |
| RR | 4,31 | 0,90 | 1,28 | 0,02 | 0,06 | 0,76 | 0,12 | 0,70 | 8,14 |
| PA | 9,26 | 5,98 | 3,76 | 7,16 | 2,83 | 5,97 | 1,55 | 1,75 | 38,26 |
| AP | 5,25 | 0,77 | 1,48 | 0,03 | 0,10 | 1,00 | 0,11 | 0,58 | 9,32 |
| TO | 5,74 | 2,46 | 2,00 | 0,09 | 0,18 | 1,72 | 0,28 | 0,74 | 13,21 |
| MA | 10,56 | 7,42 | 4,31 | 8,40 | 0,65 | 6,31 | 1,34 | 1,38 | 40,37 |
| PI | 6,40 | 4,70 | 2,65 | 2,45 | 0,16 | 3,55 | 0,67 | 1,08 | 21,65 |
| CE | 10,62 | 8,81 | 4,62 | 6,56 | 0,36 | 7,60 | 1,57 | 1,46 | 41,61 |
| RN | 5,98 | 4,39 | 2,47 | 0,43 | 0,72 | 3,40 | 0,46 | 0,86 | 18,70 |
| PB | 7,03 | 5,81 | 3,05 | 1,35 | 0,26 | 3,87 | 0,64 | 0,95 | 22,96 |
| PE | 10,31 | 8,69 | 4,52 | 2,56 | 0,39 | 7,58 | 1,29 | 1,25 | 36,59 |
| AL | 6,50 | 3,95 | 2,50 | 1,96 | 0,57 | 3,56 | 0,55 | 0,68 | 20,29 |
| SE | 5,98 | 2,72 | 2,10 | 0,19 | 0,40 | 1,94 | 0,32 | 0,50 | 14,16 |
| BA | 13,79 | 16,23 | 7,13 | 8,79 | 1,43 | 11,17 | 2,29 | 2,49 | 63,32 |
| MG | 7,09 | 23,04 | 7,14 | 0,56 | 4,00 | 15,36 | 2,68 | 3,79 | 63,65 |
| ES | 2,39 | 3,12 | 1,34 | 0,29 | 2,79 | 2,88 | 0,53 | 0,76 | 14,09 |
| RJ | 2,64 | 5,34 | 2,18 | 1,33 | 44,14 | 11,13 | 1,79 | 2,25 | 70,80 |
| SP | 1,57 | 23,56 | 6,05 | 0,61 | 4,72 | 23,19 | 6,17 | 4,71 | 70,59 |
| PR | 4,17 | 12,03 | 3,94 | 0,21 | 1,81 | 7,79 | 1,71 | 2,37 | 34,02 |
| SC | 1,88 | 6,88 | 2,10 | 0,10 | 0,50 | 4,85 | 1,09 | 1,36 | 18,76 |
| RS | 3,02 | 11,84 | 3,55 | 0,13 | 0,56 | 7,93 | 1,45 | 4,04 | 32,51 |
| MS | 1,94 | 2,57 | 1,19 | 0,04 | 0,22 | 2,07 | 0,43 | 1,30 | 9,75 |
| MT | 3,25 | 3,16 | 1,65 | 0,08 | 0,27 | 2,45 | 0,58 | 1,80 | 13,25 |
| GO | 4,29 | 6,61 | 2,66 | 0,32 | 0,55 | 4,81 | 0,90 | 1,55 | 21,67 |
| DF | 1,02 | 0,39 | 0,34 | 0,07 | 0,02 | 1,30 | 0,43 | 0,20 | 3,78 |

---

## 3. Gasto direto da União por UF

### 3.1 O que foi possível regionalizar

| Item (chave no JSON) | Fonte | Total 27 UFs 2024 | Observação |
|---|---|---:|---|
| Benefícios do INSS (`inss_benefits`) | AEPS 2024, tabela B.15, "valor de benefícios emitidos, acumulado no ano": https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/arquivos/aeps_2024.zip | R$ 876,90 bi | Inclui aposentadorias, pensões, auxílios e o BPC/LOAS. Valores em R$ mil na origem. Inclui o 13º (abril e maio de 2024 somam cerca de R$ 100 bi cada na tabela mensal B.17). |
| dos quais BPC/LOAS (`inss_bpc_loas_included`) | AEPS 2024, tabela 13.3 | R$ 89,96 bi | Já está dentro do valor do INSS. Informativo, não somar. |
| Bolsa Família (`bolsa_familia`) | MDS, Matriz de Informação Social, campo `valor_repassado_bolsa_familia_f`, 12 meses × 5.571 municípios: https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&fq=anomes_s:2024*&fl=codigo_ibge,sigla_uf,municipio,anomes_s,valor_repassado_bolsa_familia_f,pbf_qtd_familias_benef_i&rows=200000&wt=csv | R$ 170,40 bi | Conferência: a ação 8442 do SIAFI (Bolsa Família) pagou R$ 168,20 bi em 2024 (pago mais restos a pagar pagos). |
| Fundo Constitucional do DF (`fcdf_df_constitutional_fund`) | Portal da Transparência, Execução da Despesa 2024, unidade orçamentária 73901 | R$ 23,61 bi (só DF) | A União paga as polícias Civil e Militar, os Bombeiros e parte da saúde e da educação do DF. No SIAFI é despesa direta (modalidade 90), não transferência; na prática financia serviços do governo do DF. |
| Folha federal (`federal_payroll`) | nenhuma | `null` | Ver 3.3. |

`total_available` no JSON = INSS + Bolsa Família + FCDF. Não inclui folha.

### 3.2 Gasto direto por UF (2024, R$ bi)

| UF | INSS (benefícios emitidos, R$ bi) | dos quais BPC/LOAS (R$ bi) | Bolsa Família (R$ bi) | FCDF (R$ bi) | Folha federal |
|---|---:|---:|---:|---:|---|
| RO | 5,25 | 0,82 | 1,07 | 0,00 | null |
| AC | 1,97 | 0,46 | 1,15 | 0,00 | null |
| AM | 7,78 | 2,04 | 5,76 | 0,00 | null |
| RR | 1,01 | 0,34 | 0,70 | 0,00 | null |
| PA | 18,87 | 4,20 | 11,50 | 0,00 | null |
| AP | 1,29 | 0,51 | 1,05 | 0,00 | null |
| TO | 4,31 | 0,76 | 1,33 | 0,00 | null |
| MA | 20,59 | 2,96 | 10,42 | 0,00 | null |
| PI | 13,00 | 1,49 | 4,90 | 0,00 | null |
| CE | 31,41 | 5,59 | 11,88 | 0,00 | null |
| RN | 11,85 | 1,65 | 4,04 | 0,00 | null |
| PB | 15,04 | 2,30 | 5,46 | 0,00 | null |
| PE | 32,57 | 5,84 | 12,87 | 0,00 | null |
| AL | 10,83 | 1,89 | 4,46 | 0,00 | null |
| SE | 7,97 | 1,20 | 3,08 | 0,00 | null |
| BA | 54,48 | 8,51 | 19,88 | 0,00 | null |
| MG | 96,49 | 8,78 | 12,78 | 0,00 | null |
| ES | 16,54 | 1,55 | 2,49 | 0,00 | null |
| RJ | 81,76 | 7,44 | 13,43 | 0,00 | null |
| SP | 234,25 | 14,87 | 20,49 | 0,00 | null |
| PR | 51,26 | 4,02 | 4,94 | 0,00 | null |
| SC | 40,29 | 1,55 | 1,89 | 0,00 | null |
| RS | 67,76 | 3,76 | 5,32 | 0,00 | null |
| MS | 9,28 | 1,61 | 1,72 | 0,00 | null |
| MT | 10,07 | 1,62 | 2,16 | 0,00 | null |
| GO | 18,84 | 2,56 | 4,13 | 0,00 | null |
| DF | 12,12 | 1,63 | 1,51 | 23,61 | null |

### 3.3 O que não dá para dividir por UF

Na Execução da Despesa do Portal da Transparência (12 arquivos mensais de 2024, https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/202401 e seguintes), a coluna `UF` só é preenchida quando o localizador orçamentário é um estado ou município. Somando pagamentos diretos primários (modalidades 90 e 91; grupos pessoal, outras correntes, investimentos e inversões; pago mais restos a pagar pagos):

- Total: **R$ 1.916,04 bi**.
- Com UF: **R$ 192,16 bi (10,0%)**.
- Sem UF: **R$ 1.723,88 bi (90,0%)**, dos quais R$ 1.675,5 bi com localizador "NACIONAL" e o resto em localizadores regionais (Nordeste, Norte, Centro-Oeste) ou "Exterior".

Os maiores itens registrados como "Nacional" em 2024:

| Ação | Pago 2024 (R$ bi) | Com UF no SIAFI (R$ bi) | Fonte alternativa por UF |
|---|---:|---:|---|
| 00SJ Benefícios previdenciários (RGPS) | 903,65 | 0,00 | AEPS (usada) |
| 8442 Bolsa Família | 168,20 | 0,00 | MDS MI Social (usada) |
| 00IN e 00H5 BPC | 105,74 | 0,00 | AEPS (usada, dentro do INSS) |
| 20TP Ativos civis da União | 105,77 | 54,81 | nenhuma encontrada |
| 0181 Aposentadorias e pensões civis da União | 78,38 | 34,03 | nenhuma encontrada |
| 00H4 Seguro-desemprego | 52,35 | 0,37 | não pesquisada |
| 214H, 2867 e 0179 Militares (inativos, ativos, pensões) | 91,97 | 0,00 | nenhuma encontrada |
| 0581 Abono salarial | 28,29 | 0,00 | não pesquisada |

**Folha federal por UF (`null`):** a despesa de pessoal da União (grupo 1) somou R$ 317,83 bi em 2024, e só 37,0% (R$ 117,75 bi) tem UF no SIAFI, em regra por causa do localizador orçamentário e não do local de trabalho do servidor (R$ 40,0 bi desse valor são do DF, dos quais R$ 18,8 bi são do FCDF). O Painel Estatístico de Pessoal é um painel interativo (http://painel.pep.planejamento.gov.br/) sem arquivo aberto de despesa por UF; o repositório aberto da SEGRT (https://repositorio.dados.gov.br/segrt/) traz, por município, só a contagem de servidores e só a partir de novembro de 2025; o download de servidores do Portal da Transparência é por pessoa e por mês (cerca de 79 MB compactados por mês só para o SIAPE, sem militares), o que passa de 1 GB para um ano e não foi feito. Nenhum valor foi estimado a partir de um mês.

### 3.4 INSS: benefício emitido não é o mesmo que despesa paga

A AEPS mede o **valor dos benefícios emitidos** (R$ 876,90 bi em 2024, com BPC). O SIAFI registra, no mesmo ano, **R$ 903,65 bi pagos na ação do RGPS mais R$ 105,74 bi no BPC**, total de R$ 1.009,39 bi. As notas da AEPS dizem que "a partir da Lei 10.820 são considerados os descontos referentes aos valores em empréstimos consignados" (a tabela B.30 registra R$ 91,29 bi de consignados em 2024) e que a espécie 16 (auxílio da União) está excluída; a tabela 7.2 registra ainda R$ 23,43 bi de "créditos emitidos na concessão". As definições são diferentes e a AEPS não traz uma ponte com o SIAFI; este relatório não soma esses itens para "fechar" a conta. O valor por UF usado é o da AEPS, que é a única fonte oficial encontrada com o INSS por UF, e ele fica abaixo do total pago registrado no SIAFI.

---

## 4. População por UF

- **IBGE, Estimativas de População**, tabela 6579, variável 9324, via API sem chave: https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024|2025|2026/variaveis/9324?localidades=N3[all]|N1[all]
- A estimativa mais recente é a de **2026** (Brasil: 214.211.951). O JSON guarda `population` = estimativa de **2024** (é a que casa com o ano dos fluxos e é a usada no per capita) e `population_latest` = estimativa de 2026.
- Brasil 2024: 212.583.750. Soma das 27 UFs: 212.583.750.

---

## 5. Saldo por UF, 2024 (duas versões candidatas)

- **(a) arrecadação menos transferências**
- **(b) arrecadação menos (transferências + gasto direto disponível)**, onde gasto direto disponível = INSS + Bolsa Família + FCDF. **Sem a folha federal.**
- Valor positivo: a União arrecadou na UF mais do que devolveu por esses canais. Per capita com a população estimada de 2024.

| UF | População 2024 | Arrecadação federal (R$ bi) | Transferências (R$ bi) | Gasto direto disponível (R$ bi) | Saldo (a) R$ bi | Saldo (a) R$/hab | Saldo (b) R$ bi | Saldo (b) R$/hab |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RO | 1.746.227 | 8,70 | 9,81 | 6,33 | -1,11 | -634 | -7,44 | -4.258 |
| AC | 880.631 | 2,40 | 9,82 | 3,12 | -7,42 | -8.431 | -10,55 | -11.978 |
| AM | 4.281.209 | 26,26 | 19,04 | 13,55 | 7,22 | 1.688 | -6,32 | -1.477 |
| RR | 716.793 | 2,19 | 8,14 | 1,71 | -5,96 | -8.310 | -7,67 | -10.697 |
| PA | 8.664.306 | 23,05 | 38,26 | 30,36 | -15,21 | -1.755 | -45,57 | -5.259 |
| AP | 802.837 | 2,74 | 9,32 | 2,34 | -6,58 | -8.199 | -8,92 | -11.116 |
| TO | 1.577.342 | 5,79 | 13,21 | 5,64 | -7,42 | -4.702 | -13,06 | -8.281 |
| MA | 7.010.960 | 15,56 | 40,37 | 31,01 | -24,81 | -3.538 | -55,81 | -7.961 |
| PI | 3.375.646 | 8,90 | 21,65 | 17,89 | -12,75 | -3.777 | -30,65 | -9.078 |
| CE | 9.233.656 | 38,49 | 41,61 | 43,29 | -3,12 | -338 | -46,41 | -5.026 |
| RN | 3.446.071 | 11,40 | 18,70 | 15,89 | -7,30 | -2.120 | -23,20 | -6.732 |
| PB | 4.145.040 | 13,63 | 22,96 | 20,50 | -9,34 | -2.253 | -29,84 | -7.199 |
| PE | 9.539.029 | 42,08 | 36,59 | 45,44 | 5,49 | 575 | -39,95 | -4.189 |
| AL | 3.220.104 | 10,97 | 20,29 | 15,29 | -9,31 | -2.893 | -24,60 | -7.640 |
| SE | 2.291.077 | 8,25 | 14,16 | 11,05 | -5,91 | -2.579 | -16,95 | -7.400 |
| BA | 14.850.513 | 56,08 | 63,32 | 74,36 | -7,24 | -488 | -81,60 | -5.495 |
| MG | 21.322.691 | 177,39 | 63,65 | 109,26 | 113,74 | 5.334 | 4,48 | 210 |
| ES | 4.102.129 | 49,18 | 14,09 | 19,03 | 35,09 | 8.554 | 16,06 | 3.916 |
| RJ | 17.219.679 | 459,20 | 70,80 | 95,19 | 388,40 | 22.556 | 293,21 | 17.028 |
| SP | 45.973.194 | 1.036,61 | 70,59 | 254,74 | 966,03 | 21.013 | 711,29 | 15.472 |
| PR | 11.824.665 | 123,15 | 34,02 | 56,20 | 89,14 | 7.538 | 32,93 | 2.785 |
| SC | 8.058.441 | 140,22 | 18,76 | 42,18 | 121,46 | 15.072 | 79,27 | 9.837 |
| RS | 11.229.915 | 120,22 | 32,51 | 73,08 | 87,71 | 7.810 | 14,63 | 1.303 |
| MS | 2.901.895 | 17,15 | 9,75 | 11,00 | 7,40 | 2.549 | -3,61 | -1.243 |
| MT | 3.836.399 | 25,79 | 13,25 | 12,23 | 12,54 | 3.268 | 0,31 | 80 |
| GO | 7.350.483 | 41,84 | 21,67 | 22,97 | 20,16 | 2.743 | -2,81 | -383 |
| DF | 2.982.818 | 184,10 | 3,78 | 37,24 | 180,32 | 60.452 | 143,08 | 47.969 |
| **Soma 27 UFs** | 212.583.750 | 2.651,34 | 740,12 | 1.070,91 | 1.911,22 | 8.990 | 840,31 | 3.953 |

Leitura obrigatória antes de colorir o mapa com esta tabela:

1. A soma dos saldos (b) das 27 UFs é **positiva em R$ 840,31 bi**. Isso não é "dinheiro que a União guarda": é o espaço ocupado pelo gasto que não tem UF (folha civil e militar, compras de saúde, seguro-desemprego, abono, juros da dívida e o resto do "Nacional" da seção 3.3). A versão (b) é incompleta por construção.
2. A falta da folha federal pesa mais onde há mais servidores federais, sobretudo **DF** e **RJ**: nesses dois o saldo (b) está mais alto do que seria com a folha.
3. O saldo do DF, do RJ e de SP é inflado pelo efeito sede (seção 6).

---

## 6. Ressalvas, quantificadas onde os dados permitem

### 6.1 Arrecadação registrada no domicílio do contribuinte (efeito sede)

Tributos federais são registrados na UF do estabelecimento que paga (em geral a matriz), não onde a venda, a renda ou o emprego acontecem. Comparação de participações:

| UF | Participação na arrecadação federal 2024 | Participação no PIB 2023 (IBGE) | Participação na população 2024 |
|---|---:|---:|---:|
| SP | 39,1% | 31,5% | 21,6% |
| RJ | 17,3% | 10,7% | 8,1% |
| DF | 6,9% | 3,3% | 1,4% |
| MG | 6,7% | 8,9% | 10,0% |
| RS | 4,5% | 5,9% | 5,3% |
| PR | 4,6% | 6,1% | 5,6% |
| SC | 5,3% | 4,7% | 3,8% |
| BA | 2,1% | 3,9% | 7,0% |

- **SP**: 39,1% da arrecadação federal contra 31,5% do PIB e 21,6% da população. SP concentra 49,9% do IRRF do país (R$ 222,25 bi de R$ 444,99 bi) e 66,7% do IOF (R$ 44,97 bi de R$ 67,41 bi).
- **RJ**: 17,3% da arrecadação contra 10,7% do PIB. R$ 106,85 bi da arrecadação do RJ (83,2% do total nacional desta linha) estão em "administradas por outros órgãos", linha que o arquivo não detalha. **Hipótese a confirmar:** royalties e participações especiais do petróleo, pagos por empresas com sede no RJ.
- **DF**: 6,9% da arrecadação contra 3,3% do PIB e 1,4% da população. O DF concentra o IRRF retido na folha federal e o PSS dos servidores: IRRF do trabalho de R$ 48,31 bi (23,1% do país) e PSS de R$ 18,44 bi (44,0% do país) em 2024. Também é sede de bancos públicos federais.
- O arquivo da Receita não permite separar quanto de cada tributo "pertence" economicamente a outra UF. Nenhum ajuste foi feito.

### 6.2 Outras ressalvas

- **2025 por UF quebrado** (seção 1.3): DF com R$ 583,46 bi, 20,4% do país.
- **Setembro de 2024**: Imposto de Importação lançado como Imposto de Exportação em várias UFs, e R$ 1,37 bi sem UF (seção 1.2).
- **Royalties** estão dos dois lados: parte da receita "de outros órgãos" (lado da arrecadação, concentrada no RJ) e R$ 58,67 bi repassados a estados e municípios produtores (lado das transferências).
- **Fundeb**: dentro de cada estado, o Fundeb redistribui entre governo estadual e municípios; como o JSON soma estado mais municípios, essa redistribuição interna não altera o total da UF.
- **FCDF**: tratado como gasto direto (é como o SIAFI registra). Se o mapa preferir tratá-lo como transferência ao DF, o saldo (a) do DF cai em R$ 23,61 bi; o (b) não muda.
- **Transferências a entidades privadas** (R$ 17,8 bi a entidades sem fins lucrativos, com UF) ficaram fora dos dois saldos.
- **Nominal:** todos os valores são correntes do ano, sem correção pela inflação.

---

## 7. Diário de transparência

Critério: registrar o que aconteceu, com o mesmo peso para o que foi fácil e para o que foi difícil. "Passos" conta as ações até ter o número utilizável (achar, baixar, entender, somar, conferir).

| # | Conjunto | URL | Formato | Chave ou login | Passos | O que aconteceu |
|---|---|---|---|---|---|---|
| 1 | Receita: arrecadação por estado | https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv | CSV único (2,4 MB), latin1, separador `;` | Não | 5 | Achado com 1 busca; download direto. **Formatos numéricos misturados no mesmo arquivo**: inteiros; decimais com vírgula; milhar com vírgula em 2001 e 2002 (5.625 valores); milhar com ponto em 2023 (81 valores) e em maio de 2024 (TO, 2 valores). Sem dicionário de dados na página. Colunas antigas vazias (CPMF, IPMF, FUNDAF). Quebra de atribuição em 2025 (DF). Erro em setembro de 2024. A linha "administradas por outros órgãos" não é detalhada. |
| 2 | Receita: série histórica nacional | https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/serie-historica/arrecadacao-das-receitas-federais-1994-a-2025.xlsx | XLSX, uma aba por ano, R$ milhões | Não | 3 | Limpo e fácil. Foi a única forma automatizada de obter o total de 2025: a **notícia oficial** do resultado e a página "Análise gerencial da arrecadação" respondem "Conteúdo Restrito, é necessário autenticar" a acesso automatizado (curl e WebFetch). |
| 3 | Portal da Transparência: transferências | https://portaldatransparencia.gov.br/download-de-dados/transferencias/AAAAMM | ZIP mensal (2,2 a 5,5 MB) com CSV de 78 MB ou mais, latin1 | Não | 7 | Download simples, 12 arquivos, cerca de 45 MB compactados. 36 colunas, 1,93 milhão de linhas em 2024. Obstáculos: FPE e FPM vêm líquidos do Fundeb e a retenção está numa ação separada (0C33), sem aviso no arquivo; a LC 176 vem **sem UF** ("Agentes Intermediários"); o tipo de favorecido "Administração Pública" é genérico e só a modalidade de aplicação diz se é estado, município ou exterior; o total de transferências a empresas privadas no DF é **negativo** (R$ -1,21 bi), provavelmente estornos. |
| 4 | Tesouro Transparente: transferências obrigatórias | https://www.tesourotransparente.gov.br/ckan/dataset/transferencias-obrigatorias-da-uniao | CSV largo (UF nas linhas, meses nas colunas "janeiro/24"), latin1, com cabeçalho institucional e notas no rodapé | Não (a API CKAN funciona sem chave) | 4 | Números batem com o Portal até o centavo. Formato pensado para leitura humana, não para máquina: 7 linhas de cabeçalho antes da tabela, números com ponto de milhar, traço para zero, nota metodológica misturada às linhas de dados. |
| 5 | dados.gov.br (Bolsa Família MI Social) | https://dados.gov.br/dataset/bolsa-familia-misocial | nenhum (bloqueado) | **Sim, na prática**: a página e a API responderam HTTP 401 ao acesso automatizado | 2, sem sucesso | O portal nacional de dados abertos não entregou nada sem autenticação. Contornado indo direto à fonte do MDS (item 6). |
| 6 | MDS: Matriz de Informação Social (Bolsa Família) | https://aplicacoes.mds.gov.br/sagi/servicos/misocial (API Solr) | CSV ou JSON via API | Não | 4 | Funciona bem e é rápida (2,8 MB para um ano inteiro). Obstáculo: o nome do campo não está documentado na chamada; foi preciso baixar um registro com 397 campos para achar `valor_repassado_bolsa_familia_f`. Um município (Boa Esperança do Norte, MT, instalado depois) aparece com valores vazios em 2024. |
| 7 | Previdência: AEPS 2024 | https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/arquivos/aeps_2024.zip | ZIP de 10 MB com cerca de 550 entradas (pastas, XLSX e PDF) | Não | 5 | Dados bons, mas é preciso abrir o ZIP e procurar a tabela certa entre centenas de planilhas; valores em R$ mil; tabelas "continua/conclusão" divididas em abas. O conceito "benefício emitido" não fecha com a despesa paga do SIAFI e a AEPS não traz a ponte. AEPS 2025 ainda não publicado. |
| 8 | Portal da Transparência: execução da despesa | https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/AAAAMM | ZIP mensal (4,9 a 11,1 MB) com CSV de até 84 MB, latin1 | Não | 6 | Download simples (85 MB compactados no ano). A coluna UF só existe onde o localizador orçamentário é local: 90% do gasto direto primário não tem UF. Serviu para quantificar o "Nacional", achar o FCDF (UO 73901) e conferir o Bolsa Família. |
| 9 | Folha federal por UF | http://painel.pep.planejamento.gov.br/ ; https://repositorio.dados.gov.br/segrt/ ; Portal da Transparência (servidores) | painel interativo; CSV de contagem; ZIP por pessoa e mês | Não | 5, sem resultado utilizável | Não há arquivo aberto com a despesa anual de pessoal por UF. O painel exporta por consulta manual; o repositório tem só contagem de servidores por município e só desde novembro de 2025; o microdado do Portal exigiria mais de 1 GB para um ano. Resultado: `null`. |
| 10 | IBGE: estimativas de população | https://servicodados.ibge.gov.br/api/v3/agregados/6579/... | API JSON | Não | 2 | O mais fácil de todos. Estimativas de 2024, 2025 e 2026 em uma chamada. Também foi usado o PIB por UF de 2023 (tabela 5938), só como comparação na seção 6. |

**Balanço neutro do diário.** Tudo o que entrou nos números estava aberto, sem chave e sem cadastro, e quase tudo em CSV ou XLSX, não em PDF. As somas oficiais que puderam ser cruzadas bateram (transferências Portal contra Tesouro até o centavo; arrecadação por UF contra nacional em 2024 com 0,05% de diferença). Por outro lado, "fácil de achar" não se sustentou em cinco pontos: (1) o dado por UF de 2025 da Receita tem uma quebra de atribuição sem nenhum aviso; (2) arquivos oficiais trazem formatos numéricos inconsistentes e colunas sem dicionário; (3) o portal nacional dados.gov.br e duas páginas da Receita recusaram acesso automatizado; (4) regras que mudam o resultado em dezenas de bilhões (FPE e FPM líquidos do Fundeb, LC 176 sem UF) só aparecem para quem cruza duas fontes; (5) 90% do gasto direto da União não tem UF no próprio sistema de execução, e a folha federal por UF não existe em arquivo aberto.

---

## 8. Como reproduzir

Todos os scripts de download e agregação estão em [`data/scripts/`](../../data/scripts/), com um `README.md` que lista a ordem de execução e as entradas e saídas de cada passo. Resumo: `download.sh` baixa as fontes oficiais (cerca de 150 MB compactados, que ficam fora do repositório); `agg_transf.py`, `agg_desp.py` e `agg_fcdf.py` somam os arquivos do Portal da Transparência; `build_direct.py` monta INSS, BPC, Bolsa Família e FCDF por UF; `build.py` gera `data/uf-balance-2024.json`; `recon.py` e `tables.py` produzem as tabelas deste relatório; `checks.py` refaz as conferências citadas (formatos numéricos, quebra do DF em 2025, setembro de 2024, Portal contra Tesouro, parcela do gasto direto sem UF). Nenhuma chave de API ou login é necessário; `openpyxl` é a única dependência Python.
