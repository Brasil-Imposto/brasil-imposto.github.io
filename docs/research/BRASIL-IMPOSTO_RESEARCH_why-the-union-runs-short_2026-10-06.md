# Por que a conta da União fecha no negativo (pesquisa, 2026-10-06)

**English summary.** Why the Central Government shows a nominal deficit of about R$ 811,5 bi in Jan to Aug 2026 although it collects R$ 2 trillion in taxes: most of the gap is interest on the public debt, not primary spending.
Covers interest (size, indexers, who holds the debt), how exports are treated by the tax system and what the Union does collect from exporting sectors, subsidies (Orçamento de Subsídios da União, DGT 2026, CMAP), the tax burden split by level of government, and headline export facts.
Every number below was read on an official primary source (URL and quote given); what could not be opened is marked "não confirmado".

**Status:** concluída em 06/10/2026. Dados: `data/economy/union-shortfall-explained.json`. Escopo: Governo Central (Tesouro Nacional, Previdência Social e Banco Central), como o painel "A conta da União".

## Pergunta do autor
"i dont think its right that we pay so much money in taxes and we still end up more than 800 bi in negatives, not even counting how much brazil sells to the outside ... all kinds of subsidios and we are still this much on the negative? how?"

## 0. O painel, como ponto de partida
Números do painel (dados do projeto, `data/series/union.json`, RTN Tabela 1.1, série histórica de agosto de 2026, publicada em 29/09/2026), não auditados aqui:

| Linha | 2025 (ano) | 2026 (jan a ago) |
|---|---|---|
| Receita total | R$ 2.902,3 bi | R$ 2.081,6 bi |
| Transferências a estados e municípios | R$ 569,7 bi | R$ 411,9 bi |
| Despesa primária | R$ 2.394,2 bi | R$ 1.764,6 bi |
| Resultado primário | -R$ 61,7 bi | -R$ 94,9 bi |
| Juros nominais (Banco Central) | -R$ 891,9 bi | -R$ 714,4 bi |
| Resultado nominal | -R$ 950,6 bi | -R$ 811,5 bi |

Leitura direta: em 2026 (jan a ago) os juros são **88%** do resultado nominal negativo (714,4 de 811,5); o resultado primário responde pelo resto.

## 1. Juros: o tamanho, o porquê e quem recebe

### 1.1 Resultado nominal = primário + juros (Banco Central, nota de 30/09/2026)
Fonte: Banco Central, Estatísticas fiscais, nota para a imprensa de 30/09/2026, planilha `202609_Tabelas_de_estatisticas_fiscais.xlsx`, Tabela 2 ("Necessidades de financiamento do setor público, fluxos acumulados no ano", R$ milhões, sinal (+) déficit).
URL: https://www.bcb.gov.br/content/estatisticas/hist_estatisticasfiscais/202609_Tabelas_de_estatisticas_fiscais.xlsx

| Governo Central | 2025 (ano) | % PIB | 2026 (jan a ago) | % PIB |
|---|---|---|---|---|
| Resultado nominal (déficit) | R$ 950.566,99 mi | 7,46 | R$ 811.489,30 mi | 9,03 |
| Juros nominais | R$ 891.879,89 mi | 7,00 | R$ 714.402,56 mi | 7,95 |
| dos quais Governo Federal (inclui INSS) | R$ 867.671,16 mi | 6,81 | R$ 671.006,44 mi | 7,46 |
| dos quais Banco Central | R$ 24.208,73 mi | 0,19 | R$ 43.396,12 mi | 0,48 |
| Resultado primário (déficit) | R$ 58.687,10 mi | 0,46 | R$ 97.086,74 mi | 1,08 |
| dos quais Governo Federal sem INSS | superávit de R$ 259.340,77 mi | 2,04 | superávit de R$ 180.616,96 mi | 2,01 |
| dos quais INSS (Previdência, RGPS) | déficit de R$ 317.158,25 mi | 2,49 | déficit de R$ 277.020,08 mi | 3,08 |

Confere com o painel: juros de R$ 714,4 bi e nominal de R$ 811,5 bi em 2026; R$ 891,9 bi e R$ 950,6 bi em 2025. A diferença de R$ 2,2 bi do painel é a do primário "acima da linha" (Tesouro, R$ 94,9 bi) contra "abaixo da linha" (Banco Central, R$ 97,1 bi).

Fatos que o painel não mostra:
- **O Tesouro, sem a Previdência, tem superávit primário**: R$ 180,6 bi em jan a ago de 2026 e R$ 259,3 bi em 2025. O primário negativo do Governo Central vem do INSS (déficit de R$ 277,0 bi em 2026 e R$ 317,2 bi em 2025). Linhas 39 a 41 da Tabela 2.
- **Os juros do Banco Central incluem o resultado das operações de swap cambial.** Citação da nota (p. 1): "Contribuiu para esse aumento, o resultado das operações de swap cambial no período (ganho de R$19,9 bilhões em agosto de 2025 e perda de R$9,3 bilhões em agosto de 2026)."
- Setor público consolidado (União, estados, municípios e estatais), 12 meses até agosto de 2026: "os juros nominais alcançaram R$1.182,2 bilhões (8,86% do PIB), comparativamente a R$946,5 bilhões (7,61% do PIB) nos doze meses até agosto de 2025" (nota, p. 1).
- PIB acumulado usado pelo BCB (dado preliminar): R$ 12.738.565,61 mi em 2025; R$ 8.989.174,76 mi em jan a ago de 2026 (Tabela 2, linha 50).

**Juros reais contra correção pela inflação: não publicado.** As 27 tabelas da nota de 30/09/2026 não separam a parte dos juros que só repõe a inflação da parte que é juro real (o antigo "resultado operacional"); a busca no catálogo de dados abertos do BCB por "juros reais" e "operacional" não achou série fiscal com essa divisão. O que o BCB publica é a divisão por indexador (abaixo). Não estimamos a divisão (seria uma suposição).

### 1.2 Juros por indexador (setor público consolidado, BCB Tabela 16)
Fonte: mesma planilha, Tabela 16 "NFSP, Juros nominais por indexador", R$ milhões. É o setor público consolidado (o BCB não publica esta divisão só para o Governo Central).

| Indexador | 2025 | 2026 (jan a ago) |
|---|---|---|
| Selic (LFT, operações compromissadas do BCB, dívida bancária) | R$ 781.344,56 mi (77,5%) | R$ 583.946,25 mi (75,4%) |
| IPCA (NTN-B) | R$ 209.688,77 mi | R$ 167.799,51 mi |
| Prefixado (LTN, NTN-F) | R$ 184.396,54 mi | R$ 140.886,55 mi |
| Câmbio (interna e externa, líquida de reservas) | -R$ 18.480,32 mi | -R$ 13.684,94 mi |
| TJLP/TLP (créditos com BNDES, fundos, FAT: o governo recebe) | -R$ 50.788,68 mi | -R$ 46.543,02 mi |
| Outros (inclui "resultado caixa das operações de swap cambial") | -R$ 105.895,91 mi | -R$ 65.259,43 mi |
| **Total** | **R$ 1.007.553,10 mi** | **R$ 774.550,30 mi** |

A parte em IPCA (NTN-B) soma correção pela inflação e cupom real; o BCB não separa as duas.

### 1.3 Por que os juros são tão grandes: tamanho da dívida e taxa
Fonte: mesma planilha, Tabelas 17, 21 e 24; nota, seção 2.
- **Dívida Bruta do Governo Geral (DBGG, conceito BCB)**: R$ 10.017.919,14 mi (78,64% do PIB) em dezembro de 2025; **R$ 11.054.954,37 mi (82,86% do PIB) em agosto de 2026** (Tabela 17, linha 11). Nota: "A DBGG ... atingiu 82,9% do PIB (R$11,1 trilhões) em agosto de 2026 ... No ano, o aumento de 4,2 p.p. do PIB resultou da incorporação de juros nominais (6,5 p.p.), das emissões líquidas de dívida (1,5 p.p.), do crescimento do PIB nominal (-3,6 p.p.) e do efeito da valorização cambial (-0,2 p.p.)."
- Dívida Líquida do Setor Público: R$ 9.240.949,79 mi (69,26% do PIB) em agosto de 2026 (Tabela 17, linha 13).
- **DBGG por indexador, agosto de 2026** (Tabela 21): Selic 57,99%; índices de preços 19,55% (IPCA 18,76%); prefixado 17,09%; câmbio 4,60%; TJLP/TLP 0,45%; TR 0,32%. Em dezembro de 2025: Selic 52,77%, IPCA 21,50%, prefixado 19,02%, câmbio 4,99%.
- **Taxa de juros implícita na DBGG, 12 meses até agosto de 2026: 13,05% ao ano** (Governo Federal: 13,16%) (Tabela 24, linhas 9 e 10).
- **Selic** (BCB SGS 4189, "Taxa de juros - Selic acumulada no mês anualizada base 252"): 14,90% ao ano de julho de 2025 a fevereiro de 2026; 13,94% em agosto de 2026. Média simples das taxas mensais anualizadas: 14,32% em 2025 e 14,50% em jan a ago de 2026 (cálculo nosso sobre a série). URL: https://api.bcb.gov.br/dados/serie/bcdata.sgs.4189/dados?formato=json&dataInicial=01/01/2025&dataFinal=30/09/2026
- **Inflação (IPCA, IBGE, SIDRA tabela 1737)**: 4,26% em 12 meses até dezembro de 2025; 4,22% em 12 meses até agosto de 2026. URL: https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2265/p/202512,202608
- Leitura (cálculo nosso, não número oficial): com a Selic de agosto de 2026 (13,94%) e o IPCA de 12 meses (4,22%), a taxa básica fica cerca de 9,3% acima da inflação.

### 1.4 A Dívida Pública Federal (DPF): estoque, composição, custo e quem tem os títulos
Fonte: Tesouro Nacional, Relatório Mensal da Dívida Pública Federal de agosto de 2026 (PDF criado em 28/09/2026) e seu anexo em planilha.
- Texto: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/55919_1762808/Texto_RMD_Ago_26.pdf
- Anexo: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/55919_1762808/anexos/29322_995516/Anexo%20RMD_Agosto_26.zip (arquivo `Anexo RMD_Agosto_26.xlsx`)

**Estoque.** Citação (seção 2.1): "O estoque da DPF apresentou aumento, em termos nominais, de 0,04%, passando de R$ 9.288,78 bilhões, em julho, para R$ 9.292,73 bilhões, em agosto." Tabela 2.1: DPF R$ 8.635,09 bi em dez/2025; R$ 9.292,73 bi em ago/2026 (dívida interna em títulos, DPMFi, R$ 8.944,48 bi; dívida externa, DPFe, R$ 348,26 bi). No mês, a DPMFi teve "apropriação positiva de juros, no valor de R$ 79,66 bilhões".

**Composição por indexador** (Anexo 2.4, R$ bi e % do estoque):

| Indexador | dez/2025 | ago/2026 |
|---|---|---|
| Taxa flutuante (Selic, LFT) | R$ 4.166,72 bi (48,25%) | R$ 4.901,03 bi (52,74%) |
| Índice de preços (IPCA, NTN-B) | R$ 2.239,48 bi (25,93%) | R$ 2.157,35 bi (23,22%) |
| Prefixado (LTN, NTN-F) | R$ 1.904,00 bi (22,05%) | R$ 1.887,23 bi (20,31%) |
| Câmbio | R$ 324,89 bi (3,76%) | R$ 347,13 bi (3,74%) |
| **Total DPF** | **R$ 8.635,09 bi** | **R$ 9.292,73 bi** |

O Plano Anual de Financiamento de 2026 (revisado) previa taxa flutuante entre 49% e 53% do estoque (texto do RMD, quadro "Indicadores PAF 2026").

**Custo médio.** Citação (seção 4.1): "O custo médio acumulado nos últimos doze meses da DPF apresentou aumento, passando de 12,45% a.a., em julho, para 12,59% a.a., em agosto. Já o custo médio acumulado em doze meses da DPMFi diminuiu, de 13,14% a.a., em julho, para 13,06% a.a., em agosto." Anexo 4.2, agosto de 2026: LFT 14,82% a.a.; LTN 12,72%; NTN-F 11,58%; NTN-B 10,38%.

**Quem tem os títulos (DPMFi, agosto de 2026)** (Anexo 2.7, "Detentores dos Títulos Públicos Federais, DPMFi", R$ bi):

| Detentor | dez/2025 | ago/2026 | % em ago/2026 | Quem é (nota do Tesouro) |
|---|---|---|---|---|
| Instituições financeiras | 2.732,36 | 2.792,10 | 31,22% | "carteira própria de bancos comerciais, bancos de investimento, corretoras, distribuidoras e cooperativas de crédito. Também inclui os bancos estatais e o BNDES" |
| Previdência | 1.891,19 | 2.024,37 | 22,63% | "carteira própria de previdência aberta e fechada e RPPS" |
| Fundos de investimento | 1.727,68 | 2.014,62 | 22,52% | "fundos de investimento regidos pela CVM", sem as aplicações dos demais grupos |
| Não residentes | 859,64 | 886,30 | 9,91% | pessoa física ou jurídica "domiciliado ou com sede no exterior" |
| Outros | 357,88 | 425,65 | 4,76% | "contas de cliente pessoa-física residentes, sociedade de capitalização, entre outros" |
| Seguradoras | 288,70 | 298,62 | 3,34% | "seguradoras e resseguradoras" |
| Tesouro Direto (pessoas físicas) | 213,24 | 271,99 | 3,04% | programa de venda a pessoas físicas |
| Governo | 238,34 | 230,83 | 2,58% | "fundos e recursos administrados pela União tais como FAT, FGTS, fundos extramercado, fundo soberano, fundos garantidores" |
| **Total DPMFi** | **8.309,03** | **8.944,48** | 100% | |

Leitura: quem recebe os juros da dívida interna são, nessa ordem, bancos (inclusive os estatais e o BNDES), fundos de pensão e previdência (inclusive os regimes próprios de servidores), fundos de investimento (onde está a poupança aplicada de pessoas e empresas) e, com cerca de 10%, investidores de fora. O Tesouro não publica quem são as pessoas por trás de cada grupo. Destaque do texto: "os Não-residentes possuem 70,35% de sua carteira em títulos prefixados, enquanto a carteira do grupo Previdência é composta de 51,53% de títulos vinculados a índices de preços."

Observação: a DPMFi não inclui as operações compromissadas do Banco Central (R$ 1.372,1 bi em agosto de 2026, BCB Tabela 17), que também pagam a Selic e entram na dívida bruta.

## 2. Exportações e as contas do governo

### 2.1 O que a União recebe dos setores exportadores (Tesouro, RTN; Receita Federal)
Fonte A: Tesouro Nacional, Resultado do Tesouro Nacional, série histórica de agosto de 2026 (`serie_historica_ago26.xlsx`, publicada em 29/09/2026), Tabela 1.2 "Resultado Primário do Governo Central, Mensal, Valores Correntes", R$ milhões, soma dos meses (cálculo nosso). URL: https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326 (página: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/8)

| Linha da Tabela 1.2 | 2025 | 2026 (jan a ago) |
|---|---|---|
| 1.4.4 Receitas de Exploração de Recursos Naturais (royalties, participação especial, CFEM e outras) | R$ 139.345,8 mi | R$ 112.087,1 mi |
| 2.4 Transferências de Exploração de Recursos Naturais (a estados e municípios) | R$ 70.207,8 mi | R$ 56.279,3 mi |
| Fica com a União (diferença, cálculo nosso) | R$ 69.138,0 mi | R$ 55.807,8 mi |
| 1.4.2 Dividendos e Participações (todas as estatais) | R$ 49.796,6 mi | R$ 19.255,9 mi |
| 1.4.2.8 dos quais Petrobras | R$ 13.825,7 mi | R$ 7.407,3 mi |
| 1.4.2.3 dos quais BNDES | R$ 22.326,0 mi | R$ 7.607,1 mi |
| 4.3.13 Lei Kandir (LC 87/96 e 102/00) e LC 176/2020 (despesa: compensação aos estados) | R$ 3.984,7 mi | R$ 2.656,2 mi |
| Receita total do Governo Central, para comparação | R$ 2.902.274,6 mi | R$ 2.081.627,9 mi |

Leitura: a exploração de recursos naturais rendeu 4,8% da receita total em 2025 e 5,4% em 2026 (cálculo nosso); cerca de metade foi repassada a estados e municípios.

Fonte B: Receita Federal, "Arrecadação por Estado" (dados abertos, mensal, por tributo, R$ correntes), coluna "IMPOSTO SOBRE EXPORTAÇÃO", soma das 27 UFs (cálculo nosso; o arquivo tinha até julho de 2026 na coleta de 06/10/2026). URL: https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv

| Imposto de Exportação | Valor |
|---|---|
| 2023 | R$ 4.422,9 mi (maio a setembro: o imposto temporário sobre petróleo bruto de 2023) |
| 2024 | R$ 3.084,0 mi (R$ 3.074,6 mi só em setembro) |
| **2025** | **R$ 1,9 milhão** (praticamente zero) |
| 2026, jan a jul | R$ 8.002,5 mi (RJ R$ 7.426,8 mi; SP R$ 430,6 mi; ES R$ 135,4 mi) |
| 2026, agosto | R$ 1,9 bi (Tesouro, RTN de agosto, texto: "alterações legislativas no Imposto de Exportação sobre óleo bruto (Resolução Gecex nº 938/2026), item responsável pelo recolhimento de R$ 1,9 bilhão no mês de agosto de 2026", já registrado em `BRASIL-IMPOSTO_RESEARCH_recent-revenue_2026-10-04.md`) |

O imposto de 2026 vem da Medida Provisória nº 1.340, de 12/03/2026 (Planalto, lida em 06/10/2026: "Vigência encerrada"), art. 10: "Fica estabelecida a alíquota de 12% (doze por cento) do imposto sobre a exportação de óleos brutos de petróleo ou de minerais betuminosos, classificados no código 2709 da Nomenclatura Comum do Mercosul NCM, incidente sobre o valor total das exportações." O mesmo ato criou subvenção ao óleo diesel (art. 1º, R$ 0,32 por litro) e alíquota de 50% na exportação de diesel (art. 12). URL: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/mpv/mpv1340.htm . Depois, Resolução Gecex nº 938/2026 (12%, 60 dias) e nº 957/2026 (prorrogação), registradas no documento citado acima.

Leitura: fora dos impostos temporários sobre petróleo (2023 e 2026), o Imposto de Exportação quase não arrecada; em 2025, R$ 1,9 milhão.

### 2.2 Por que a exportação quase não paga imposto: a regra está na Constituição e nas leis
Todos os textos abaixo foram lidos no Planalto em 06/10/2026 (texto compilado, trechos revogados excluídos).

| Tributo | Regra | Texto (citação) | URL |
|---|---|---|---|
| Contribuições sociais e Cide | CF art. 149, § 2º, I (EC 33/2001) | "não incidirão sobre as receitas decorrentes de exportação" | https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm |
| IPI | CF art. 153, § 3º, III | "não incidirá sobre produtos industrializados destinados ao exterior" | idem |
| ICMS (estadual) | CF art. 155, § 2º, X, a (EC 42/2003) | "não incidirá: a) sobre operações que destinem mercadorias para o exterior, nem sobre serviços prestados a destinatários no exterior, assegurada a manutenção e o aproveitamento do montante do imposto cobrado nas operações e prestações anteriores" | idem |
| IBS (reforma tributária) | CF art. 156-A, § 1º, III (EC 132/2023) | "não incidirá sobre as exportações, assegurados ao exportador a manutenção e o aproveitamento dos créditos" | idem |
| Imposto de Exportação | CF art. 153, II, e § 1º | a União pode cobrar; "É facultado ao Poder Executivo ... alterar as alíquotas" | idem |
| ICMS, lei complementar | LC 87/1996 (Lei Kandir), art. 3º, II | "O imposto não incide sobre: ... II - operações e prestações que destinem ao exterior mercadorias, inclusive produtos primários e produtos industrializados semi-elaborados, ou serviços" | https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp87.htm |
| PIS/Pasep | Lei 10.637/2002, art. 5º, I | "A contribuição para o PIS/Pasep não incidirá sobre as receitas decorrentes das operações de: I - exportação de mercadorias para o exterior" | https://www.planalto.gov.br/ccivil_03/leis/2002/l10637.htm |
| Cofins | Lei 10.833/2003, art. 6º, I | "A COFINS não incidirá sobre as receitas decorrentes das operações de: I - exportação de mercadorias para o exterior" | https://www.planalto.gov.br/ccivil_03/leis/2003/l10.833.htm |
| Drawback | Lei 11.945/2009, art. 12 | insumo "para emprego ou consumo na industrialização de produto a ser exportado poderá ser realizada com suspensão do Imposto de Importação, do Imposto sobre Produtos Industrializados - IPI, da Contribuição para o PIS/Pasep e da Cofins" | https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2009/lei/l11945.htm |
| Reintegra | Lei 13.043/2014, arts. 21 e 22 | "tem por objetivo devolver parcial ou integralmente o resíduo tributário remanescente na cadeia de produção de bens exportados"; crédito de 0,1% a 3% da receita de exportação (§ 1º com "Redação dada pela Lei Complementar nº 216, de 2025") | https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l13043.htm |

**Motivo oficial ("não exportar tributos").** O texto legal que diz o objetivo com todas as letras é o do Reintegra (art. 21, acima): "devolver ... o resíduo tributário remanescente na cadeia de produção de bens exportados". A frase "não exportar tributos" aparece em pareceres e estudos; não achamos documento do governo federal aberto ao robô com essa frase exata (as cópias do Senado achadas na busca devolveram página HTML em vez do PDF). Não confirmado como citação literal de fonte federal.

**Custo das imunidades de exportação: o DGT não mede.** O Demonstrativo dos Gastos Tributários (Receita Federal) mede só desvios do "Sistema Tributário de Referência"; as imunidades constitucionais da exportação (IPI, PIS/Cofins, ICMS) não aparecem entre os itens do DGT 2026 (busca por "export", "drawback" e "reintegra" nos 26 quadros). O único item ligado à exportação é **"Exportação da Produção Rural": R$ 23.987,8 mi em 2026**, descrito como "Não incidência da contribuição social sobre receitas de exportações do setor rural (agroindústria e produtor rural pessoa jurídica)" (DGT PLOA 2026, Quadros VII e XXV; 64,6% no Sudeste, cálculo nosso sobre o Quadro VII regional). O ICMS é estadual e fica fora do DGT.

**A União ainda paga aos estados pela Lei Kandir**: R$ 3.984,7 mi em 2025 e R$ 2.656,2 mi em jan a ago de 2026 (RTN Tabela 1.2, linha 4.3.13 "Lei Kandir (LC nº 87/96 e 102/00) e LC nº 176 de 2020").

### 2.3 Como a lei divide royalties, participação especial e CFEM
- **Participação especial do petróleo (ANP).** Citação do "Relatório Trimestral de Participação Especial, 4º trimestre de 2025" (ANP): "Nos termos do art. 50 da Lei nº 9.478/97, a PE é distribuída na seguinte proporção: i) 50% à União; ii) 40% aos estados; iii) 10% aos municípios"; no pré-sal sob concessão, a parte da União vai "integralmente ao Fundo Social" (art. 49 da Lei 12.351/10). No 4º trimestre de 2025 a PE arrecadada foi R$ 6.992.855.948,12 e a distribuída R$ 6.249.344.298,68, dos quais "TOTAL UNIÃO" R$ 3.124.672.149,34 (Fundo Social R$ 2.906.244.289,52) e o estado do Rio de Janeiro 34,63%. URL: https://www.gov.br/anp/pt-br/assuntos/royalties-e-outras-participacoes/arq-royalties/pe/rel/2026/RelatrioTrimestraldeParticipaoEspecial4T2025_v01.pdf
- **CFEM (mineração).** Lei 8.001/1990, art. 2º, § 2º (redação da Lei 13.540/2017), lida no Planalto: 7% para a agência reguladora (ANM), 1% para o FNDCT, 1,8% para o Cetem, 0,2% para o Ibama (soma de 10% para órgãos federais); "15% (quinze por cento) para o Distrito Federal e os Estados onde ocorrer a produção"; "60% (sessenta por cento) para o Distrito Federal e os Municípios onde ocorrer a produção"; 15% para municípios afetados. URL: https://www.planalto.gov.br/ccivil_03/leis/l8001.htm . A arrecadação anual da CFEM em 2025 não foi confirmada (os arquivos de dados abertos da ANM não abriram para o robô).
- **Total, com a mesma régua do painel**: ver 2.1 (RTN): R$ 139,3 bi arrecadados com exploração de recursos naturais em 2025, R$ 70,2 bi repassados a estados e municípios.

## 3. Subsídios

### 3.1 Gastos tributários previstos para 2026 (Receita Federal, DGT PLOA 2026)
Fonte: Receita Federal, Centro de Estudos Tributários e Aduaneiros, "Demonstrativo dos Gastos Tributários PLOA 2026", setembro de 2025, versão 1.01, e planilha de quadros.
URLs: https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/renuncia/gastos-tributarios-ploa/dgt-previsao-ploa-2026-base-conceitual.pdf e https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/renuncia/gastos-tributarios-ploa/dgt-previsao-ploa-2026-quadros.xlsx

- Total, citação (p. 9 e 10): "O gasto tributário para o ano de 2026 foi estimado em R$ 612,84 bilhões (crescimento de 12,56% em relação do DGT PLOA referente ao ano anterior), representando 4,43% do Produto Interno Bruto e 20,20% das receitas administradas pela RFB."
- Definição (p. 4): "gastos indiretos do governo realizados por intermédio do sistema tributário, visando a atender objetivos econômicos e sociais e constituem-se em uma exceção ao Sistema Tributário de Referência". Método: "perda de arrecadação"; os valores "têm natureza de estimativas, projeções ou previsões".
- Regiões (p. 10): "as regiões Sudeste e Sul obtiveram as maiores participações nos benefícios, com 49,00% e 16,13% respectivamente"; Norte e Nordeste têm a maior renúncia em relação à própria arrecadação (81,83% e 34,75%).
- Funções (p. 10): "Comércio e Serviço (22,54%), Saúde (17,41%), Agricultura (14,95%), Trabalho (11,94%), Indústria (8,31%) e Assistência Social (6,21%)".

Maiores itens (Quadro X, "Principais gastos tributários, projeções PLOA 2026", R$):

| Item | 2026 (previsão) | % do total |
|---|---|---|
| Simples Nacional | R$ 134.293,7 mi | 21,91% |
| Agricultura e Agroindústria | R$ 79.250,7 mi | 12,93% |
| Rendimentos isentos e não tributáveis (IRPF) | R$ 63.174,2 mi | 10,31% |
| Entidades sem fins lucrativos (imunes e isentas) | R$ 55.923,7 mi | 9,13% |
| Deduções do rendimento tributável (IRPF: saúde, educação, dependentes etc.) | R$ 41.685,4 mi | 6,80% |
| Poupança e títulos de crédito (imobiliário e agronegócio) | R$ 36.875,9 mi | 6,0% |
| Zona Franca de Manaus e Áreas de Livre Comércio | R$ 35.987,6 mi | 5,9% |
| Desenvolvimento regional | R$ 27.082,0 mi | 4,4% |
| Benefícios do trabalhador | R$ 24.313,2 mi | 4,0% |
| Medicamentos, produtos farmacêuticos e equipamentos médicos | R$ 22.368,3 mi | 3,6% |
| MEI | R$ 11.278,8 mi | 1,8% |
| **Total** | **R$ 612.842,9 mi** | 100% |

Dentro de "Agricultura e Agroindústria", a desoneração da cesta básica soma R$ 40.193,4 mi (PIS R$ 7.169,6 mi, Quadro XIX; Cofins R$ 33.023,8 mi, Quadro XXI).

### 3.2 Orçamento de Subsídios da União (última edição encontrada: dados de 2024)
Fonte: Ministério do Planejamento e Orçamento, Secretaria de Monitoramento e Avaliação de Políticas Públicas e Assuntos Econômicos (SMA/MPO), "Orçamento de Subsídios da União 2024" (9ª edição), "Última alteração: 19 de agosto de 2025", 19 páginas.
URL: https://www.gov.br/planejamento/pt-br/assuntos/avaliacao-de-politicas-publicas/arquivos/orcamento-de-subsidios-da-uniao/orcamento-de-subsidios-da-uniao-9a-edicao.pdf
Uma edição com os dados de 2025 não foi encontrada em 06/10/2026 (pasta oficial e busca); não confirmado se já saiu.

- Total, citação (p. 5): "Em 2024, esse valor total atingiu R$ 678 bilhões ou o equivalente a 5,78% do PIB, valor inferior aos 6,10% observados em 2023."
- Por modalidade (Tabela 1, R$ bilhões correntes): tributários R$ 564 bi (2023: 541); financeiros R$ 65 bi (2023: 44); creditícios R$ 50 bi (2023: 83); total R$ 678 bi (2023: 668). Sumário: "Os benefícios tributários seguem predominantes. Em conjunto, essa categoria responde por 83,1% de todo o orçamento de subsídios da União."
- Definições (p. 7): "Subsídios (ou benefícios) tributários são exceções ao sistema tributário de referência. Subsídios (ou benefícios) creditícios se materializam por recursos da União alocados a [fundos ou programas] ... que pressupõem taxa de retorno diferenciada."

Principais itens em 2024 (Apêndice B, Tabelas 3 e 4, R$ bilhões):

| Modalidade | Item | 2024 | % do total |
|---|---|---|---|
| Tributário | Simples Nacional | 118,2 | 17,4% |
| Tributário | Agricultura e Agroindústria | 77,2 | 11,4% |
| Tributário | Rendimentos isentos e não tributáveis (IRPF) | 57,7 | 8,5% |
| Tributário | Entidades sem fins lucrativos (imunes e isentas) | 43,8 | 6,5% |
| Tributário | Deduções do rendimento tributável (IRPF) | 38,3 | 5,6% |
| Tributário | Zona Franca de Manaus e Áreas de Livre Comércio | 27,6 | 4,1% |
| Tributário | Desenvolvimento Regional | 23,6 | 3,5% |
| Tributário | PERSE (setor de eventos) | 17,7 | 2,6% |
| Tributário | Desoneração da folha de salários | 15,8 | 2,3% |
| Tributário | Desoneração da folha dos municípios | 10,6 | 1,6% |
| Financeiro | FCVS (Fundo de Compensação das Variações Salariais) | 33,0 | 4,9% |
| Financeiro | Minha Casa Minha Vida | 12,9 | 1,9% |
| Financeiro | Tarifa social de energia (subclasse baixa renda) | 6,4 | 0,9% |
| Financeiro | Pronaf (equalização) | 5,0 | 0,7% |
| Financeiro | Operações de investimento rural e agroindustrial (equalização) | 2,8 | 0,4% |
| Creditício | Fundos Constitucionais (FNE, FNO, FCO) | 23,7 | 3,5% |
| Creditício | FIES | 20,7 | 3,0% |
| Creditício | FAT | 7,7 | 1,1% |
| Creditício | Fundo da Marinha Mercante | -10,9 | -1,6% |

Sumário (p. 4): "Dentro dos benefícios tributários, merece destaque o crescimento dos subsídios associados ao Imposto sobre a Renda das Pessoas Físicas", e "a extinção do benefício tributário dos combustíveis (R$ 31,2 bilhões em 2023)".

**O que entra no caixa de cada ano** (Tesouro, RTN Tabela 1.2, linha 4.3.15 "Subsídios, Subvenções e Proagro", despesa primária): R$ 25.488,9 mi em 2025 e R$ 14.257,8 mi em jan a ago de 2026; dos quais equalização do Pronaf R$ 8.883,0 mi (2025) e R$ 5.790,0 mi (2026), equalização de investimento rural e agroindustrial R$ 5.762,3 mi e R$ 4.278,5 mi, equalização de custeio agropecuário R$ 2.166,1 mi e R$ 1.100,1 mi, Proex R$ 477,8 mi e R$ 443,1 mi. Os subsídios tributários não aparecem como despesa: são receita que deixa de entrar.

**Como os subsídios entram no déficit.** Os R$ 612,8 bi do DGT 2026 e os R$ 564 bi tributários do OSU 2024 não são gasto registrado no painel: são estimativas de receita que não foi arrecadada, calculadas contra um "sistema tributário de referência". Somar esse valor ao déficit seria uma suposição (supõe que, sem o benefício, a atividade e a arrecadação seriam as mesmas); a própria Receita diz que os valores "têm natureza de estimativas".

### 3.3 Avaliações oficiais que acharam problema no subsídio
1. **Desoneração de PIS/Cofins da cesta básica (CMAP, avaliação de 2021; boletim de maio de 2023).** Fonte: Ministério do Planejamento e Orçamento, "Avaliação de Políticas Públicas #1, mai 2023, Desoneração da cesta básica e direito à alimentação". URL: https://www.gov.br/planejamento/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/cmap/politicas/2021/subsidios/boletim_desoneracao-cesta-basica-e-direto-a-alimentacao.pdf/@@display-file/file (página: https://www.gov.br/planejamento/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/cmap/politicas/area/assistencia-e-previdencia-social/subsidios/desoneracao-cesta-basica). Citações: "RECURSOS ENVOLVIDOS R$ 34,7 BI"; "Política reduz preços médios da cesta em 5%"; "a maior parte dos gastos tributários associados à desoneração da Cesta Básica acabam direcionados aos grupos de maior renda. Isso é explicado principalmente pelo fato de o gasto geral das famílias mais ricas, em valores absolutos, ser obviamente maior"; "dos 23 alimentos desonerados, 18 estavam alinhados a boas práticas nutricionais, mas cinco incluíam ultraprocessados".
2. **Desoneração da folha de pagamentos (Ministério da Fazenda, Secretaria de Política Econômica, abril de 2024).** Não é avaliação do CMAP; é estudo do Ministério da Fazenda escrito no debate da prorrogação da política (Lei 14.784/2023 e MP 1.202/2023). Lido na cópia do Internet Archive (o gov.br pediu login): https://web.archive.org/web/2025id_/https://www.gov.br/fazenda/pt-br/central-de-conteudo/publicacoes/conjuntura-economica/estudos-economicos/2024/desoneracao_final_3.pdf . Citações: "a afirmação de que as atividades beneficiadas pela política de desoneração da folha de pagamentos são aquelas que mais geram postos de trabalho não encontra respaldo nos dados"; as 141 classes CNAE desoneradas "perderam participação na geração de postos formais de emprego ... passando de 21% do total de vínculos formais em 2015 para 18% em 2021". O próprio estudo ressalva: "Este resultado não permite uma conclusão contundente de impacto da política, uma vez que este estudo não isola, a partir de métodos estatísticos, o efeito da desoneração". Valor no OSU 2024: R$ 15,8 bi.

### 3.4 Lei que cortou benefícios: Lei Complementar nº 224, de 26/12/2025
Fonte: Planalto, texto compilado lido em 06/10/2026. URL: https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp224.htm
- Ementa: "Dispõe sobre a redução e os critérios de concessão de incentivos e benefícios de natureza tributária, financeira ou creditícia concedidos exclusivamente no âmbito da União".
- Art. 4º: "Os incentivos e benefícios federais de natureza tributária são reduzidos na forma deste artigo", para PIS/Cofins, IRPJ e CSLL, Imposto de Importação, IPI e contribuição previdenciária do empregador (§ 1º), nos itens do DGT anexo à LOA de 2026 e no lucro presumido, Reiq, créditos presumidos e alíquotas zero da Lei 10.925/2004 (§ 2º).
- Como: § 4º, I: isenção e alíquota zero passam a "alíquota correspondente a 10% (dez por cento) da alíquota do sistema padrão de tributação"; créditos presumidos limitados "a 90% (noventa por cento) do valor original"; lucro presumido: "acréscimo de 10% (dez por cento) nos percentuais de presunção", só sobre a receita acima de R$ 5 milhões por ano (§ 5º).
- Fora do corte (§ 8º): "imunidades constitucionais"; Zona Franca de Manaus e áreas de livre comércio; a cesta básica nacional da LC 214/2025; entidades sem fins lucrativos; o benefício do art. 146, III, d, da Constituição (o Simples Nacional); Minha Casa, Minha Vida; Prouni; CPRB (desoneração da folha), entre outros.
- Teto (art. 5º): "Caso o valor total dos incentivos e benefícios tributários ultrapasse montante equivalente a 2% (dois por cento) do Produto Interno Bruto (PIB), fica vedada a concessão, ampliação ou prorrogação de incentivos e benefícios tributários", salvo com compensação (§ 2º).
- Estimativa oficial de arrecadação da LC 224: não encontrada no RTN de agosto de 2026 (busca por "224" no boletim). Não confirmado.
- Leitura: os cinco maiores itens do DGT 2026 (Simples, agro, rendimentos isentos do IRPF, entidades sem fins lucrativos e deduções do IRPF) estão, no todo ou em parte, fora do corte, ou não são dos tributos do § 1º (IRPF). Isto é leitura do texto da lei, não cálculo oficial.

## 4. A ordem de grandeza: quanto de "imposto que pagamos" vai para a União
Fonte: Tesouro Nacional, "Estimativa da Carga Tributária Bruta do Governo Geral" de 2025 (dados preliminares), Tabela 1. Notícia do Tesouro de 10/04/2026: https://www.gov.br/tesouronacional/pt-br/noticias/carga-tributaria-bruta-do-governo-geral-atinge-32-40-do-pib-em-2025 . O boletim foi lido na cópia anexada à Prestação de Contas do Presidente da República 2025 (CGU), porque a página do Tesouro Transparente carrega o arquivo por script: https://www.gov.br/cgu/pt-br/assuntos/auditoria-e-fiscalizacao/avaliacao-da-gestao-dos-administradores/prestacao-de-contas-do-presidente-da-republica/2025/AnexoEstimativadaCargaTributriaBoletim_CTB_20251.pdf

Citação: "Em 2025, a estimativa da carga tributária bruta (CTB) do governo geral (governos central, estaduais e municipais) foi de 32,40% do PIB, o que representa um aumento de 0,18 p.p. do PIB em relação a 2024." O boletim lembra: "a Secretaria da Receita Federal do Brasil (RFB) é a área responsável pela publicação do dado oficial da carga tributária no Brasil" (o número da Receita para 2025 não foi buscado aqui).

| Esfera (quem arrecada) | 2025, R$ milhões | % do PIB | Parte do total (cálculo nosso) |
|---|---|---|---|
| Governo Central | 2.750.941 | 21,60% | 66,7% |
| Governos estaduais | 1.067.626 | 8,38% | 25,9% |
| Governos municipais | 308.665 | 2,42% | 7,5% |
| **Governo geral** | **4.127.232** | **32,40%** | 100% |

Por tipo (Tabela 2, governo geral, 2025): impostos sobre bens e serviços R$ 1.755.056 mi (13,78% do PIB); sobre renda, lucros e ganhos de capital R$ 1.166.558 mi (9,16%); contribuições ao RGPS R$ 687.416 mi (5,40%); sobre a propriedade R$ 220.047 mi (1,73%); sobre o comércio exterior R$ 90.222 mi (0,71%, inclui o Imposto de Importação).

Comparações de ordem de grandeza (cálculo nosso; conceitos diferentes, por isso não somar nem subtrair uns dos outros):
- Do que o Governo Central arrecada, parte vai para estados e municípios: R$ 569,7 bi em 2025 (RTN, "Transferências por repartição de receita", que inclui FPE, FPM, royalties e salário-educação).
- Os juros do Governo Central em 2025 (R$ 891,9 bi, BCB) equivalem a 32,4% dos tributos arrecadados pelo Governo Central no ano (R$ 2.750,9 bi, Tesouro) e a 21,6% de todos os tributos do país (R$ 4.127,2 bi).
- Os benefícios previdenciários (RGPS) custaram R$ 1.026.872,5 mi em 2025 (RTN Tabela 1.2, linha 4.1), contra R$ 709.714,3 mi de arrecadação líquida para o RGPS (linha 1.3).

## 5. Exportações: os números principais (o conjunto completo está em outro trabalho)
O levantamento completo por produto, estado e destino está em `docs/research/BRASIL-IMPOSTO_RESEARCH_exports-by-product_2026-10-06.md`; aqui só os números de cabeçalho, conferidos de novo na fonte em 06/10/2026.

- **Valor exportado** (MDIC/Secex, arquivo oficial de conferência `EXP_TOTAIS_CONFERENCIA.csv`, https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_TOTAIS_CONFERENCIA.csv): 2025, US$ 348.278.462.500 FOB; 2026 (jan a set), US$ 284.654.368.793; 2024, US$ 337.046.161.710.
- **O que se exporta, pela classificação oficial atual (ISIC, Comex Stat, `details:["ISICSection"]`)**: 2025, indústria de transformação US$ 188,41 bi (54,1%), indústria extrativa US$ 80,32 bi (23,1%), agropecuária US$ 77,61 bi (22,3%), outros US$ 1,93 bi (0,6%). 2026 (jan a set): 51,6%, 25,0%, 22,8% e 0,6%. Observação: na ISIC, carne, açúcar, farelo de soja e celulose contam como indústria de transformação. A Secex descontinuou a série por "fator agregado" (básicos, semimanufaturados, manufaturados) ao adotar a ISIC (registrado no documento de exportações acima, com a citação da Nota Metodológica). API: https://api-comexstat.mdic.gov.br/general
- **Peso no PIB** (IBGE, Contas Nacionais Trimestrais, SIDRA tabela 1846, valores correntes, soma dos 4 trimestres de 2025, cálculo nosso): PIB R$ 12.738.566 mi; exportação de bens e serviços R$ 2.270.104 mi (17,8% do PIB); importação de bens e serviços R$ 2.225.524 mi (17,5% do PIB); diferença R$ 44.580 mi (0,35% do PIB). Valor adicionado da agropecuária R$ 775.297 mi (7,1% do valor adicionado) e das indústrias extrativas R$ 403.599 mi (3,7%). URL: https://apisidra.ibge.gov.br/values/t/1846/n1/all/v/all/p/202501,202502,202503,202504/c11255/all
- **Termos de troca**: a série usada no país é calculada pela Funcex (entidade privada) e reproduzida no Ipeadata; não há série de órgão do governo lida aqui. Não confirmado em fonte oficial do governo.

**Por que exportar não fecha a conta da União (leitura dos dados acima).**
1. A receita de exportação é das empresas que vendem (privadas e estatais), não do governo. O governo recebe por tributos sobre o lucro (IRPJ e CSLL), pelos royalties e pela participação especial, pela CFEM e pelos dividendos das estatais (seção 2.1).
2. A Constituição manda não cobrar IPI, ICMS, PIS/Cofins e o futuro IBS sobre a exportação (seção 2.2). O Imposto de Exportação é opcional e arrecadou R$ 1,9 milhão em 2025.
3. O Brasil importa quase o mesmo tanto que exporta: em 2025, exportação de 17,8% do PIB e importação de 17,5% (IBGE).

## 6. O que os dados dizem sobre a pergunta do autor
- **Por que a União fecha no negativo, com tanto imposto pago?** Os R$ 811,5 bi de jan a ago de 2026 são, em 88%, juros da dívida (R$ 714,4 bi). Antes dos juros, o déficit é de R$ 94,9 bi; e, dentro dele, o Tesouro sem a Previdência tem superávit de R$ 180,6 bi, enquanto o INSS tem déficit de R$ 277,0 bi (BCB, Tabela 2). As receitas líquidas cobrem 94,6% da despesa primária (R$ 1.669,7 bi de R$ 1.764,6 bi, RTN, cálculo nosso); os juros ficam sem cobertura e viram dívida nova.
- **E o que o Brasil vende para fora?** O dinheiro das exportações é das empresas que exportam, não do governo, e a Constituição proíbe cobrar IPI, ICMS, PIS/Cofins (e o futuro IBS) sobre a exportação. O Imposto de Exportação rendeu R$ 1,9 milhão em 2025. O que a União recebe dos setores que mais exportam vem de royalties, participação especial e CFEM (R$ 139,3 bi em 2025, cerca de metade repassada a estados e municípios), de dividendos (Petrobras R$ 13,8 bi em 2025) e dos tributos sobre o lucro. **Neste ponto a premissa não se sustenta**: a venda para fora não é receita do governo, e a regra de não tributar a exportação está na Constituição.
- **E os subsídios?** Os subsídios existem e são grandes (R$ 678 bi em 2024 pelo OSU; R$ 612,8 bi de benefícios tributários previstos para 2026), mas a maior parte não é dinheiro pago: é imposto que deixa de ser cobrado, medido contra uma regra de referência. O maior item é o Simples Nacional (R$ 134,3 bi), não o agronegócio exportador (R$ 79,3 bi para "agricultura e agroindústria", dos quais R$ 40,2 bi são a cesta básica). O único benefício ligado diretamente à exportação no DGT é a não incidência da contribuição previdenciária sobre a exportação rural (R$ 24,0 bi). Uma avaliação oficial (CMAP) achou que a maior parte do benefício da cesta básica vai para quem tem mais renda; a LC 224/2025 cortou 10% de parte dos benefícios e criou um teto de 2% do PIB, mas deixou de fora o Simples, a Zona Franca e a cesta básica.
- **"Quanto dos impostos vai para a União."** Dos R$ 4,13 tri de tributos de 2025, o Governo Central arrecadou R$ 2,75 tri (66,7%); estados, R$ 1,07 tri; municípios, R$ 0,31 tri. Do que arrecada, a União repassou R$ 569,7 bi a estados e municípios em 2025.

## 7. Como mostrar no site (proposta, 6 cartões neutros)
Cada cartão aponta para os fatos de `data/economy/union-shortfall-explained.json` (campo `cards[].fact_ids`).

| # | Título | Fato em uma linha | Valor | `cards[].id` |
|---|---|---|---|---|
| 1 | O que forma o déficit | Dos R$ 811,5 bi de déficit da União de janeiro a agosto de 2026, R$ 714,4 bi são juros da dívida. | 88% são juros | `card_interest_share` |
| 2 | Antes dos juros: Tesouro e Previdência | De janeiro a agosto de 2026, o Tesouro sem a Previdência teve superávit primário de R$ 180,6 bi e a Previdência (INSS) teve déficit de R$ 277,0 bi. | +R$ 180,6 bi e -R$ 277,0 bi | `card_primary_split` |
| 3 | Por que os juros são altos | A dívida bruta é de R$ 11,05 tri (82,9% do PIB), 58% dela atrelada à Selic, que estava em 13,94% ao ano em agosto de 2026, com inflação de 4,22% em 12 meses. | R$ 11,05 tri; Selic 13,94% | `card_debt_and_rate` |
| 4 | Quem tem os títulos da dívida | Em agosto de 2026: instituições financeiras 31,2%, previdência 22,6%, fundos de investimento 22,5%, não residentes 9,9%, demais 13,7%. | R$ 8,94 tri em títulos | `card_debt_holders` |
| 5 | Exportação e impostos | A Constituição proíbe cobrar IPI, ICMS e PIS/Cofins sobre a exportação. O Imposto de Exportação arrecadou R$ 1,9 milhão em 2025; royalties e participações renderam R$ 139,3 bi, metade repassada a estados e municípios. | R$ 1,9 mi e R$ 139,3 bi | `card_exports_taxes` |
| 6 | Subsídios: receita que deixa de entrar | A Receita prevê R$ 612,8 bi em benefícios tributários em 2026 (4,43% do PIB). O maior é o Simples Nacional, R$ 134,3 bi. São estimativas, não despesa paga. | R$ 612,8 bi | `card_tax_expenditures` |

Regras de texto respeitadas: só fatos com fonte, sem adjetivo de juízo (D45, D51); "superávit" e "déficit" com sinal explícito.

## 8. Não confirmado
- Divisão dos juros entre correção pela inflação e juro real (o BCB não publica nas tabelas atuais).
- Orçamento de Subsídios da União com dados de 2025 (não encontrado em 06/10/2026).
- Arrecadação anual da CFEM (dados abertos da ANM não abriram).
- Citação literal "não exportar tributos" em documento do governo federal.
- Estimativa oficial de arrecadação da LC 224/2025.
- Termos de troca em série de órgão do governo (a série usual é da Funcex, privada).
- Carga tributária de 2025 pela Receita Federal (órgão do número oficial); usado o boletim do Tesouro.
