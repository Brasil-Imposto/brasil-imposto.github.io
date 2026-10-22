# Totais completos: seis lacunas fechadas com número oficial

> **Atualização de 2026-10-14:** o total pago da ponte Hercílio Luz passou a R$ 507.319.980,20 (2006 a 2020) com a 1ª etapa, PJ 015/2006, lida na CPI (auditoria A1, aplicada em `data/complete-totals-2026-10-06.json`). Os R$ 483.404.916,67 abaixo são o valor desta coleta.

Coleta: 06/10/2026. Serve à decisão D100 (nada de "a conferir" na tela) e a D91, D93 e D95 (primeiro número de cada caso é o total gasto completo, com fonte). Dados: `data/complete-totals-2026-10-06.json`. Scripts: `pipelines/complete_totals/`.

Regra: só fonte oficial e primária, com a frase do órgão (nas citações, o travessão dos títulos originais foi trocado por hífen). Toda soma confere ao centavo com o total oficial, e cada script tem um `--control` que planta um erro e tem de falhar.

## Resumo

| # | Lacuna | Valor final | O que mede | Fonte |
|---|---|---|---|---|
| 1 | Ponte Hercílio Luz, supervisão PJ-00170/2006, 2006 a 2010 | R$ 8.982.441,11 | pago (bruto) de 20/12/2006 a 31/12/2010 | CPI da Ponte, Alesc, Apêndice A |
| 1 | Ponte Hercílio Luz, 13 contratos | R$ 483.404.916,67 | total pago, nominal, 2006 a 2020 | CPI da Alesc e Portal de SC |
| 2 | Linha 17-Ouro | R$ 5.543.066 mil | investimento realizado pelo Metrô, 2010 a ago/2026 | relatórios do Metrô |
| 3 | ETE Insular | R$ 229 milhões | investimento total realizado até 31/12/2025 | Relatório da Administração 2025 da Casan |
| 4 | SC-401 terceira faixa | R$ 41.694.715,23 | pago bruto (empresa mais impostos retidos) até 30/09/2026 | extrato SICOP, Portal de SC |
| 5 | Banco Master | R$ 15 bilhões | ativos do BRB vindos do Master (valor de referência); perda ainda não quantificada | Fato Relevante do BRB, 20/04/2026 |
| 6 | Datas de divulgação | Receita 2024: 28/01/2025; BEPS 2024: 31/03/2025 | data original da publicação (Receita); data do arquivo oficial (BEPS) | gov.br, cópias do Internet Archive e o arquivo do BEPS |

## 1. Ponte Hercílio Luz: supervisão PJ-00170/2006 paga de 2006 a 2010

**Resposta: R$ 8.982.441,11 pagos de 2006 a 2010** no contrato de supervisão (Prosul R$ 5.389.722,50; Concremat R$ 3.592.718,61), lidos pagamento a pagamento no relatório final da CPI da Ponte Hercílio Luz da Alesc (documentos de 19/12/2019 no e-Legis). Com isso, **o total pago nos 13 contratos da restauração passa a R$ 483.404.916,67** (valores nominais, 2006 a 2020), R$ 9.750.424,67 a mais que os R$ 473.654.492,00 de 05/10/2026: R$ 8.982.441,11 do período 2006 a 2010 e R$ 767.983,56 de pagamentos de julho e setembro de 2014 do mesmo contrato que o extrato do contrato no Portal de SC não traz.

**Fonte.** Alesc, Comissão Parlamentar de Inquérito da Ponte Hercílio Luz (RQC/0016.6/2019, Ato da Presidência nº 030-DL de 2019), relatório do relator, volume com as páginas 901 a 1819 (https://portalelegis.alesc.sc.gov.br/proposicoes/legado/RQC-0016.6-2019/anexo/10766/visualizar, documento de 19/12/2019 na lista de documentos do e-Legis; o voto vencedor, https://portalelegis.alesc.sc.gov.br/proposicoes/legado/RQC-0016.6-2019/anexo/10772/visualizar, adota o parecer do relator e só altera as páginas 1718 e 1719). Lido em 06/10/2026.
- "APÊNDICE A - ATUALIZAÇÃO DOS VALORES CONTRATUAIS" (p. 1736 do relatório): uma tabela por contrato, com as colunas "MEDIÇÃO", "DATA DE INÍCIO", "DATA DE TÉRMINO", "VALOR MEDIDO", "DATA DA LIQUIDAÇÃO", "VALOR DA LIQUIDAÇÃO", "DATA DO PAGAMENTO", "VALOR DO PAGAMENTO", "PGTOS NO MÊS" e "VALOR ATUALIZADO".
- "Contrato PJ 170/2006 - Prosul" (p. 1754 a 1763): primeira linha "1 29/08/06 31/08/06 3.328,92 08/12/06 3.328,92 20/12/06 3.328,92"; última "TOTAL 9.160.234,16".
- "Contrato PJ 170/2006 - Concremat" (p. 1763 a 1773): primeiro pagamento em 12/03/2007; "TOTAL 6.106.108,71".
- No quadro geral (p. 1344), a mesma CPI lista "PJ 170/06 25/08/06 Prosul [...] R$ 9.160.234 2014" e "Concremat R$ 6.106.108", e explica: "Para fins de atualização dos valores, avaliou-se que o valor contratual não representaria uma base confiável, uma vez que pode não ter sido executado na sua totalidade".

**Pago por ano (data do pagamento na tabela da CPI)**

| Ano | Prosul | Concremat | Soma | Portal de SC, extrato dos dois contratos |
|---|---|---|---|---|
| 2006 | R$ 42.182,51 | R$ 0,00 | R$ 42.182,51 | não cobre |
| 2007 | R$ 1.154.809,02 | R$ 797.574,43 | R$ 1.952.383,45 | não cobre |
| 2008 | R$ 850.954,35 | R$ 567.056,05 | R$ 1.418.010,40 | não cobre |
| 2009 | R$ 1.036.997,36 | R$ 626.726,35 | R$ 1.663.723,71 | não cobre |
| 2010 | R$ 2.304.779,26 | R$ 1.601.361,78 | R$ 3.906.141,04 | não cobre |
| **2006 a 2010** | **R$ 5.389.722,50** | **R$ 3.592.718,61** | **R$ 8.982.441,11** | |
| 2011 | R$ 1.490.609,90 | R$ 993.730,38 | R$ 2.484.340,28 | R$ 2.484.340,28 |
| 2012 | R$ 671.111,24 | R$ 447.450,94 | R$ 1.118.562,18 | R$ 1.118.562,18 |
| 2013 | R$ 833.377,53 | R$ 555.277,39 | R$ 1.388.654,92 | R$ 1.388.654,92 |
| 2014 | R$ 775.412,99 | R$ 479.649,53 | R$ 1.255.062,52 | R$ 487.078,96 |
| 2016 | R$ 0,00 | R$ 37.281,86 | R$ 37.281,86 | R$ 37.281,86 |
| **Total** | **R$ 9.160.234,16** | **R$ 6.106.108,71** | **R$ 15.266.342,87** | |

**Por que confiar na tabela da CPI (conferências feitas):**
- A soma das linhas de pagamento é igual ao "TOTAL" impresso em cada tabela, ao centavo, e a soma da coluna "PGTOS NO MÊS" também (prova de que nenhuma linha ficou de fora da leitura).
- De 2011 a 2013, a CPI e o Portal de SC dão o mesmo valor ao centavo, somando as duas linhas do contrato. Separadas, só 2011 difere: R$ 110.869,79 que o extrato SICOP põe na linha da Concremat (nutitulo 53682) a CPI põe na da Prosul (medição 55, paga em 30/03/2011); o próprio extrato registra essa liquidação para o credor 951 (Prosul), e a consulta por credor da Concremat (CNPJ 33.146.648/0003-91) em 2011 dá R$ 993.730,38, igual à CPI. Isso também explica a diferença de R$ 110.869,79 que ficou "não explicada" em 05/10/2026.
- 2014: a CPI tem pagamentos em 25/07/2014 e 25/09/2014 (medições 91 a 95) que o extrato do contrato no Portal não traz. Para a Concremat, a consulta por credor do Portal (https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/pgtocredor?anomesinifiltro=201401&anomesfimfiltro=201412&credorfiltro%5B%5D=20913&tipopagamentocredorfiltro=1&totais=1&page=1&indicador=0) mostra "vlbruto" de R$ 479.649,53 em 2014, igual à CPI ao centavo. Para a Prosul (R$ 288.334,03 a mais em 2014), a consulta por credor mistura muitos contratos e não separa este; o número vem só da CPI.
- O total pago bate com o valor atual do contrato no registro SICOP (R$ 9.160.234,18 e R$ 6.106.108,74; diferenças de R$ 0,02 e R$ 0,03) e fica R$ 2.490,48 e R$ 2.490,50 abaixo da medição final acumulada.
- A mesma leitura aplicada à tabela "Contrato PJ 264/2008 - Consórcio Florianópolis Monumento" (p. 1773) dá **R$ 29.121.516,40 pagos antes de 2011**, exatamente o valor que em 05/10/2026 só existia como diferença entre o TCE-SC e o Portal. Agora há documento oficial que o imprime linha a linha. Total da tabela: R$ 63.008.872,09, igual ao Portal mais o pré-2011. Em 2011 e 2012 há R$ 7.515,14 de ISS retido que o Portal registra pago em 15/12/2011 e a CPI conta no pagamento de 2012; a soma dos dois anos é igual.
- As tabelas da CPI para PJ 204/2014, PJ 012/2015, PJ 143/2015 e PJ 093/2016 têm o mesmo total do Portal ao centavo. Os demais contratos (Fares, Teixeira Duarte, RMG de 2019, Geoarqueologia e SDF) não foram comparados; a tabela da Teixeira Duarte na CPI vai só até 2019.

**Total pago nos 13 contratos (nominal):**

| Parte | Valor | Fonte |
|---|---|---|
| 10 contratos sem pagamento antes de 2011 | R$ 405.129.701,71 | Portal de SC, extrato SICOP (05/10/2026) |
| PJ-00170/2006 (Prosul e Concremat) | R$ 15.266.342,87 | CPI da Alesc, Apêndice A |
| PJ-00264/2008 | R$ 63.008.872,09 | CPI da Alesc, Apêndice A (igual ao TCE-SC mais o Portal) |
| **Total** | **R$ 483.404.916,67** | soma conferida em duas passadas |

**Sobre os "R$ 19,4 milhões" do TCE-SC.** A notícia do TCE-SC de 19/10/2015 sobre o processo RLA-12/00285490 (https://www.tcesc.tc.br/tcesc-inicia-julgamento-do-processo-que-trata-de-contratos-para-restauracao-e-supervisao-das-0) diz que "ao consórcio responsável pela supervisão da obra haviam sido pagos R$ 19,4 milhões". Esse número não bate com os pagamentos (R$ 15,27 milhões no total, pela CPI e pelo Portal); bate com o valor do contrato com os aditivos de 2010 e 2012 (R$ 9.811.282,66 + R$ 5.158.436,86 + R$ 4.466.623,62 = R$ 19.436.343,14, extrato SICOP). Fica fora da conta.

Checagens: `pipelines/complete_totals/hercilio_luz_supervision_cpi.py` (lê as tabelas da CPI, confere total e coluna do mês ao centavo, compara com o Portal; `--control` soma R$ 0,01 a um pagamento e falha: "Prosul: payments 9160234.17 != TOTAL 9160234.16") e `pipelines/complete_totals/bridge_complete_total.py` (total dos 13 contratos em duas passadas, Decimal e centavos inteiros; `--control` falha: "pass 1 483404916.68 != pass 2 483404916.67").

## 2. Linha 17-Ouro: total pago ou investido até hoje

**Resposta: R$ 5.543.066 mil (R$ 5,54 bi) de investimento realizado na Linha 17-Ouro de 2010 a agosto de 2026**, somando ano a ano o que o próprio Metrô publica como investimento realizado (caixa) na linha, em valores nominais. Até dezembro de 2025: R$ 4.840.350 mil; de janeiro a agosto de 2026: R$ 702.716 mil. O número do governo, "investimento de R$ 5,97 bilhões" (Agência SP), fica R$ 0,43 bi acima; nenhum documento lido explica a diferença (o orçamento revisado de 2026 para a linha é R$ 996.573 mil, dos quais R$ 702.716 mil realizados até agosto).

**O que o número mede.** Desembolso do Metrô na implantação da linha (ação orçamentária 2282 "LINHA 17-OURO", no grupo "EMPREENDIMENTOS EM EXPANSÃO"); o Relatório de Administração 2016, ao apresentar o orçamento de investimentos de 2017, diz que "os recursos para os citados investimentos são provenientes do Tesouro do Estado e de financiamentos". Os relatórios chamam de "Investimentos realizados (caixa)" (2014 a 2021) e "Investimentos realizados (caixa e aportes)" (2021 a 2025); de 2010 a 2013, "Quadro Comparativo dos Recursos Financeiros", linha "1. Investimentos".

| Ano | Linha 17 (R$ mil) | Fonte principal | Segunda fonte do Metrô para o mesmo ano |
|---|---|---|---|
| 2010 | 200 | Relatório da Administração 2011, quadro 2011/2010 | |
| 2011 | 46.700 | idem | |
| 2012 | 221.100 | Relatório de Administração 2013, quadro 2013/2012 | |
| 2013 | 326.300 | Relatório de Administração 2013 | Relatório de Administração 2014 (326,3) |
| 2014 | 491.990 | Relatório Integrado 2021, p. 44 | Relatório de Administração 2015 (492,0) |
| 2015 | 272.060 | idem | Relatórios de Administração 2015 e 2016 (272,1) |
| 2016 | 137.560 | idem | Relatório de Administração 2016 (137,5) |
| 2017 | 196.790 | idem | Acompanhamento Financeiro 2017 (196.785) |
| 2018 | 243.300 | idem | Acompanhamento Financeiro dez/2018 (243.297) |
| 2019 | 168.200 | idem | Acompanhamento Financeiro dez/2019 (168.192) |
| 2020 | 164.900 | idem | Acompanhamento Financeiro dez/2020 (164.878; diferença de R$ 22 mil) |
| 2021 | 286.000 | Relatório Integrado 2025, p. 11 | Acompanhamento Financeiro dez/2021 (286.008) |
| 2022 | 206.020 | idem | Relatório Integrado 2023, p. 20 (206,02) |
| 2023 | 208.680 | idem | Acompanhamento Financeiro dez/2023 (208.683) |
| 2024 | 722.250 | idem | Acompanhamento Financeiro dez/2024 (722.248) |
| 2025 | 1.148.300 | idem | Acompanhamento Financeiro dez/2025 (1.148.301) |
| 2026 (jan a ago) | 702.716 | Acompanhamento Financeiro ago/2026, "REALIZADO ACUMULADO" | |
| **Total** | **5.543.066** | | |

**Frases e endereços (lidos em 06/10/2026):**
- Relatório Integrado 2025, "Investimentos realizados (caixa e aportes) - Expansão da Rede (milhões)", linha "Linha 17 286,00 206,02 208,68 722,25 1.148,30" (2021 a 2025): https://transparencia.metrosp.com.br/sites/default/files/Relat%C3%B3rio%20Integrado%202025.pdf
- Relatório Integrado 2021, "Investimentos Realizados (Caixa) - Expansão da Rede (R$ milhões)", 2014 a 2021 (gráfico de barras com os valores por linha e o total de cada ano): https://transparencia.metrosp.com.br/sites/default/files/RELAT%C3%93RIO%20INTEGRADO%202021_0.pdf
- Acompanhamento Financeiro de Ações, Programas e Projetos Previstos, agosto de 2026: "2282 LINHA 17-OURO - ( JABAQUARA - SÃO PAULO - MORUMBI) 996.573 74.786 702.716 71%" (orçamento revisado, realizado no mês, realizado acumulado, em R$ mil): https://transparencia.metrosp.com.br/sites/default/files/Investimentos%20para%202026%20fechamento%20%20agosto.pdf
- Relatório de Administração 2013: "Quadro comparativo dos recursos financeiros - 2013/2012", "- Linha 17 - Ouro - São Judas - Congonhas - Jabaquara - Morumbi 326,3 221,1": https://transparencia.metrosp.com.br/node/1689/download ; o de 2014 repete 326,3 para 2013 (https://transparencia.metrosp.com.br/node/1688/download).
- Relatório da Administração 2011 ("Balanço 2011 - CMSP - Dados finais publicados no jornal"), "Quadro Comparativo dos Recursos Financeiros - 2011/2010", "Linha 17 Ouro - São Judas - Congonhas - Jabaquara - Morumbi 46,7 0,2" (cópia do Internet Archive de 01/11/2012; o arquivo é digitalizado e a coluna da expansão soma 650,5 e 1.067,2, como impresso): https://web.archive.org/web/20121101150948/http://www.metro.sp.gov.br/metro/institucional/pdf/rel-administracao.pdf
- Relatórios de Administração 2015 e 2016 ("Quadro Comparativo dos Recursos Financeiros"): https://transparencia.metrosp.com.br/node/210/download e https://transparencia.metrosp.com.br/node/694/download

**Conferências.** `pipelines/complete_totals/metro_line17_total.py`: para cada ano, as linhas transcritas da mesma tabela ou gráfico somam o total impresso (dentro de uma unidade impressa), o que pega valor lido na linha errada; onde há segunda fonte do Metrô, as duas batem (diferenças acima de uma unidade só em 2020, R$ 22 mil); a soma da Linha 17 sai igual em duas passadas; `--control` soma R$ 11 mil ao valor de 2018 e falha ("2018: lines 1710711 vs printed total 1710700").

**Ressalvas.**
- 2022: o Acompanhamento de dezembro de 2022 (emitido em 09/01/2023) mostra R$ 173.416 mil realizados na Linha 17; os Relatórios Integrados de 2023 e de 2025 mostram R$ 206,02 mi. Todas as linhas de 2022 diferem entre esses documentos, e nenhum deles diz por quê; foi usado o valor publicado depois, duas vezes.
- 2013: o Relatório Integrado de 2017 (publicado no portal com o nome "relatório integrado 2020.pdf") traz um gráfico de 2013 a 2017 cuja coluna de 2013 soma R$ 2.787 mi de expansão, contra R$ 2.569,2 mi nos Relatórios de Administração de 2013 e 2014; os valores por linha desse gráfico não foram usados.
- O quadro mais antigo lido é o de 2011/2010; em 2010 o gasto na linha foi R$ 0,2 mi. Anos anteriores não foram lidos.
- O total é nominal e soma conceitos muito próximos com nomes diferentes ao longo dos anos ("recursos financeiros, investimentos", "investimentos realizados (caixa)", "(caixa e aportes)"); nos anos em que dois deles existem, batem.

## 3. ETE Insular: o que é "valor consumido" e quanto foi pago

**Resposta curta.** A Casan não define "consumido" como pago, e não publica pagamentos por contrato. O número oficial de gasto da própria Casan para a obra é o **"investimento total realizado" de R$ 229 milhões até 31/12/2025** ("Ampliação do Sistema de Esgotamento Sanitário Insular", dos quais R$ 27 milhões em 2025), no Relatório da Administração de 2025, Tabela 9, "Principais investimentos no ano (em termos de recursos aplicados)". É o candidato a primeiro número do cartão ("Investimento total, realizado até dez/2025, Casan"). Não há número oficial de pago em 2026.

**Fonte do número principal.** Casan, Relatório da Administração 2025 (https://ri.casan.com.br/bfd_download/relatorio-da-administracao-dfp-2025/, p. 25 do PDF; a mesma tabela está na DFP 2025, https://ri.casan.com.br/bfd_download/dfp-2025/), lido em 06/10/2026:
> "Os principais investimentos realizados ao longo de 2025 (em termos de montantes aplicados), para a implantação, melhoria e ampliação dos sistemas de abastecimento de água e esgotamento sanitário foram executados nos municípios apresentados na Tabela 9."
> Linha: "Florianópolis | Esgoto | Ampliação do Sistema de Esgotamento Sanitário Insular | 27 | 229" (colunas "Investimento em 2025 (R$ milhões)" e "Investimento total realizado (R$ milhões)").

O que esse número inclui, pelas Notas Explicativas da DFP 2025 (página 85 de 153, logo antes do item "3.7. Imobilizado e Intangível"): "O Ativo de Contrato é reconhecido inicialmente pelo valor justo e inclui custos de empréstimos capitalizados durante o período em que o ativo se encontra em fase de construção." Ou seja, é o custo da obra registrado pela Casan, que pode incluir juros do financiamento da JICA no período de construção, e não só o que foi pago à construtora. A Casan publica o valor em milhões, sem centavos.

**O que é "valor consumido".**
- No portal da Casan, o campo aparece na tela "Acompanhamento dos Saldos Contratuais" e no extrato do contrato, com três linhas: "Original (R$)", "Consumido (R$)" e "Saldo (R$)", e o saldo é calculado na própria página como `valorContrato - valorConsumido` (código da página `app/views/extrato-contrato.html`); no código do portal, a fonte é "SAP" e o gestor dos dados é a "Gerência de Licitações (GLI)". Nenhuma página, glossário, FAQ ou script do portal define a palavra; a página "Despesa da Empresa" diz que "as informações acerca das despesas da Companhia encontram-se na Demonstração do Resultado e nas Notas Explicativas" e o "Orçamento da Despesa" é classificado como "confidenciais e estratégicas".
- Leitura de hoje (SAP carregado em 06/10/2026 14h40, https://transparencia.casan.com.br/data/contratos?empresafiltro%5B%5D=2000009269&dtinivigenciainifiltro=2000-01-01&dtinivigenciafimfiltro=2026-12-31&page=1): contrato EOC001246/2020, valor R$ 261.908.002,30, **consumido R$ 203.441.074,09**, saldo R$ 58.466.928,21 (a conta fecha ao centavo).
- O consumido não acompanha o faturamento: de 05/09/2026 (R$ 177.381.260,29) a 06/10/2026 subiu R$ 26.059.813,80, enquanto o "Valor Principal Faturado do investimento" da tabela "Obras de expansão" subiu R$ 1.359.127,94 (de R$ 159.075.646,78 até 30/08/2026 para R$ 160.434.774,72 até 30/09/2026). Por isso ele não serve como "pago" na tela.

**Tabela "Obras de expansão" de hoje** (https://transparencia.casan.com.br/data/download/4981/2, "Dados atualizados: Contratos celebrados e Valores consolidados até 30/09/2026"): linha "SES Insular - Ampliação ETE e Bacias D/F", situação "Andamento", "set/26" a "mar/28", valor principal R$ 228.958.907,40, faturado R$ 160.434.774,72. O principal mudou: agora é o principal do EOC 1246/2020 (R$ 197.768.490,12) mais o contrato EOC 1534/2026 da Construtora CFO (R$ 31.190.417,28), igual ao centavo. As datas "set/26" e "mar/28" passaram a ser as do contrato novo. O "faturado" é sem reajustes.

**Como usar no cartão (proposta).** Primeiro número: "Investimento total R$ 229 mi (realizado até dez/2025, Relatório da Administração da Casan)". Detalhes: "faturado, sem reajustes: R$ 160,4 mi até set/2026 (tabela de obras da Casan)"; "consumido no SAP: R$ 203,4 mi (06/10/2026; a Casan não diz que é pago)". O valor de R$ 229 mi é da obra de ampliação do SES Insular inteira, nome que a própria Casan usa para a mesma obra da tabela de obras ("SES Insular - Ampliação ETE e Bacias D/F"), e já supera o consumido do contrato principal, então inclui custos além desse contrato (como os juros capitalizados).

Checagem: `pipelines/complete_totals/casan_insular_check.py` confere o saldo do SAP (contrato menos consumido) e a soma dos dois contratos contra o principal da tabela de obras, ao centavo; `--control` soma R$ 0,01 ao consumido e falha.

## 4. SC-401 terceira faixa: o que mede "Pago até set/2026"

**Resposta: é o valor pago bruto do contrato da obra (CT-00014/2025, Britagem Vogelsanger), isto é, o que o Estado pagou à empresa mais os impostos que reteve dela e repassou (INSS, IRRF e ISS).** Os R$ 40,7 mi eram a carga do Portal de 30/09/2026; na carga lida hoje o pago subiu para **R$ 41.694.715,23**, igual ao centavo ao valor medido acumulado nas 18 medições até 31/08/2026. Pode ser o primeiro número do cartão, com o rótulo "pago até set/2026".

Fonte: extrato SICOP do contrato, Portal da Transparência do Poder Executivo de SC, https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=104411 (lido em 06/10/2026; último pagamento em 30/09/2026).

| Ano | Pago (vlpago do resumo) | Líquido à empresa | Impostos retidos (INSS, IRRF, ISS, menos estornos) |
|---|---|---|---|
| 2025 | R$ 26.786.756,45 | R$ 25.538.781,37 | R$ 1.247.975,08 |
| 2026 (até 30/09) | R$ 14.907.958,78 | R$ 14.061.622,12 | R$ 846.336,66 |
| **Total** | **R$ 41.694.715,23** | **R$ 39.600.403,49** | **R$ 2.094.311,74** |

- Medição: "MEDIÇÃO 018", período até 31/08/2026, "vlacumuladototal" R$ 41.694.715,23 (R$ 40.224.998,39 a preços iniciais mais R$ 1.469.716,84 de reajuste). Pago igual a medido: não há valor medido esperando pagamento.
- Definições do próprio Portal de SC (glossário, https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/glossario, lido em 06/10/2026): "Valor Pago": "Após a conferência do recebimento de bens, materiais e serviços (liquidação), a despesa foi devidamente paga." "Retenção": "É o valor retido pelo Estado do montante a ser pago ao credor. Esse valor é repassado para a pessoa de direito." "Valor a pagar": "Corresponde à diferença entre o valor total medido e o valor pago pela execução dos serviços realizados pela contratada."
- Por que é bruto: em cada ano, o "vlpago" do resumo é a soma de todas as linhas de pagamento, e essas linhas são de dois tipos: "Despesa Empenhada" (o que vai para a conta da empresa) e "Retenção INSS", "Retenção IRRF Receita", "Retenção ISS" (o que o Estado retém e paga ao INSS, à Receita e à prefeitura), com os estornos negativos. As duas partes somam o pago ao centavo.
- Por que o número mudou: na carga de 30/09/2026, 2026 tinha R$ 14.907.958,78 liquidados e R$ 13.942.009,55 pagos; a diferença (R$ 965.949,23) foi paga em 30/09/2026 e já aparece hoje.
- Outros contratos ligados à obra, fora deste número: projeto CT-00018/2021 (Norden Engenharia), R$ 441.107,18 pagos de 2022 a 2025 (extrato ...nutitulofiltro[]=101659); supervisão CT-00315/2022 (Iguatemi), R$ 1.832.974,12 pagos em 2025 e 2026 (extrato ...nutitulofiltro[]=103057), mas o objeto da supervisão cobre a restauração da SC-401 e da SC-404 em três trechos, então somá-la misturaria outras obras (regra de D95). Obra mais projeto: R$ 42.135.822,41.
- Checagem: `pipelines/complete_totals/sicop_paid.py 104411` confere, ano a ano, linhas igual a resumo ao centavo, e líquido mais retenções igual ao pago; `--control` soma R$ 0,01 a uma linha e falha ("2025: summary 26786756.45 vs lines 26786756.46").

## 5. Banco Master: dinheiro público envolvido

**Resposta: nenhum órgão publicou ainda o prejuízo de dinheiro público. O maior valor oficial de dinheiro público envolvido é o do BRB (banco controlado pelo Distrito Federal): ativos "oriundos de operações recebidas pelo BRB do Banco Master" com "valor de referência de R$ 15 bilhões"** (Fato Relevante do BRB, 20/04/2026). É exposição de um banco público, não perda apurada. Proposta para o campo `public_money_brl`: 15.000.000.000, com o rótulo "ativos do BRB vindos do Master (valor de referência)"; os outros valores oficiais abaixo ficam nos detalhes, sem somar (medem coisas diferentes e em parte o mesmo dinheiro).

**Fontes oficiais lidas (documentos do BRB no sistema da CVM, lidos em 06/10/2026):**

| Data | Documento | O que diz (palavras do documento) | O que mede |
|---|---|---|---|
| 24/11/2025 | Comunicado ao Mercado (https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&descTipo=IPE&CodigoInstituicao=1&numProtocolo=1449007&numSequencia=973719&numVersao=1) | "uma vez identificadas as carteiras recebidas em desconformidade com o contrato celebrado, atuou de forma diligente para promover a substituição dos referidos ativos. Durante esse processo, no qual foram substituídos aproximadamente R$ 10 bilhões em ativos" | carteiras compradas do Master trocadas por outros ativos do Master |
| 10/03/2026 | Fato Relevante com a Lei distrital nº 7.845/2026 (https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&descTipo=IPE&CodigoInstituicao=1&numProtocolo=1488603&numSequencia=1013309&numVersao=1) | Art. 2º, III: "operações de crédito com o Fundo Garantidor de Crédito - FGC ou instituições financeiras, até o limite de R$ 6.600.000.000,00" para "recomposição, reforço ou ampliação do patrimônio líquido e do capital social" do BRB | dinheiro público autorizado (teto), não gasto |
| 09/03/2026 | Aviso aos Acionistas, aumento de capital (https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&descTipo=IPE&CodigoInstituicao=1&numProtocolo=1487722&numSequencia=1012428&numVersao=1) | "O montante total da emissão poderá alcançar até R$ 8.860.750.000,00", mínimo "R$ 529.000.000,00", "preço de emissão de R$ 5,29" | aumento de capital proposto (o DF é o controlador); quanto o DF subscreveu não foi publicado nos documentos lidos |
| 20/04/2026 | Fato Relevante, MoU com a Quadra (https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&descTipo=IPE&CodigoInstituicao=1&numProtocolo=1506735&numSequencia=1031441&numVersao=1) | "transferência de ativos detidos pela Companhia, oriundos de operações recebidas pelo BRB do Banco Master" e "A Operação possui valor de referência de R$ 15 bilhões" | ativos do BRB vindos do Master |
| 28/05/2026 | Fato Relevante, acordo homologado pelo STF na ACO 3.755/DF (https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&descTipo=IPE&CodigoInstituicao=1&numProtocolo=1528228&numSequencia=1052934&numVersao=1) | "contratação, pelo DF, de operação de crédito junto ao Fundo Garantidor de Créditos (“FGC”), de até 16% (dezesseis por cento) da Receita Corrente Líquida, para o fim exclusivo de aporte de capital pelo acionista controlador no BRB" | empréstimo do DF para pôr capital no BRB (teto em % da RCL) |
| 17/07/2026 | Fato Relevante (https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&descTipo=IPE&CodigoInstituicao=1&numProtocolo=1546080&numSequencia=1070786&numVersao=1) | o BRB "decidiu não dar continuidade à operação no âmbito do Memorando de Entendimentos" | a venda dos ativos de R$ 15 bi não aconteceu; os ativos seguem no BRB |
| 24/08/2026 | Ata da AGE (https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&descTipo=IPE&CodigoInstituicao=1&numProtocolo=1564187&numSequencia=1088893&numVersao=1) | "a quantificação definitiva dos prejuízos depende da conclusão dos trabalhos em curso e da divulgação das demonstrações financeiras correspondentes" | prejuízo ainda não quantificado pelo próprio BRB |
| 31/03/2026 | Fato Relevante (https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext&descTipo=IPE&CodigoInstituicao=1&numProtocolo=1499239&numSequencia=1023945&numVersao=1) | "a publicação das demonstrações financeiras referentes ao 3º (terceiro) e ao 4º (quarto) trimestres de 2025 será postergada" | por isso não há balanço com a perda |

**Separado, dinheiro privado:** o FGC pagou "R$37,7 bilhões" de "R$40,4 bilhões em valor de cobertura" (Banco Central, Relatório de Estabilidade Financeira de maio de 2026, já em `scandals-status`). O FGC é mantido pelas instituições financeiras.

**Regimes próprios de previdência (RPPS):** o valor de R$ 1,867 bi em letras financeiras do Master aplicado por 18 regimes de estados e municípios é atribuído pela imprensa ao Ministério da Previdência Social (19/11/2025). A página do Ministério sobre o caso (https://www.gov.br/previdencia/pt-br/noticias/2026/maio/201cos-problemas-no-banco-master-foram-detectados-pela-previdencia-social-em-2024201d-afirma-wolney-queiroz) responde hoje "Conteúdo Restrito. É necessário autenticar para visualizar essa página", e o Internet Archive não tem cópia; a nota do Rioprevidência (https://www.rj.gov.br/rioprevidencia/node/803) responde "Acesso negado", também na cópia do Internet Archive. Não confirmado na fonte primária; fica fora.

**Conferência:** `pipelines/complete_totals/master_public_money.py` confere ao centavo que o aumento de capital fecha (ações vezes preço igual ao montante; capital antes mais aumento igual ao capital depois, nos dois limites); `--control` muda o preço em R$ 0,01 e falha.

## 6. Datas de divulgação: Receita 2024 e BEPS 2024

**Achado que vale para as duas:** em 03/07/2026 o gov.br republicou em bloco os arquivos antigos. Hoje, toda Análise da Arrecadação de dez/2023 a jan/2026 mostra "Publicado em 03/07/2026 15h38" ou "15h39" e "Atualizado em 08/07/2026" (conferido em dez/2023, mar/2024, nov/2024, dez/2024, jun/2025 e jan/2026), e todo boletim do BEPS de 2024 a jan/2026, e até o anuário AEPS 2024, mostra "Publicado em 03/07/2026 19h23". Essa data é da republicação, não da divulgação do dado; usá-la diria que o dado de 2024 saiu em 2026. A data original foi lida em cópias antigas do próprio gov.br no Internet Archive (Receita) e, onde não há cópia, no próprio arquivo oficial (BEPS).

**receita_2024: 28/01/2025.**
- Listagem da pasta 2024 no gov.br, cópia do Internet Archive de 30/01/2025 (https://web.archive.org/web/20250130132517/https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/arrecadacao-federal/2024), coluna "Data de modificação": "Análise Arrecadação Dez 2024 Arquivo 28/01/2025 11h00"; "Análise Mensal - Dez 2024 - Anexo Arquivo 28/01/2025 10h49"; "Desempenho da Arrecadação JAN-1995 A DEZ-2024. Arquivo 28/01/2025 10h58".
- Página da análise de dezembro, cópia de 03/04/2025 (https://web.archive.org/web/20250403200304/https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/arrecadacao-federal/2024/apresentacao-arrecadacao-dez-2024.pdf/view): "Atualizado em 28/01/2025 11h00". A página da série "Desempenho da Arrecadação JAN-1995 A DEZ-2024" já estava no ar na cópia de 29/01/2025 01h36 (UTC), com "Atualizado em 28/01/2025 10h58".
- Hoje (https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/arrecadacao-federal/2024/analise-mensal-dez-2024.pdf/view, lido em 06/10/2026): "Publicado em 03/07/2026 15h39", "Atualizado em 08/07/2026 14h21" (a republicação em bloco). O PDF da análise mensal foi trocado em 08/12/2025 (cópia de 08/01/2026: "Atualizado em 08/12/2025 13h27"); o anexo com as tabelas ficou com 28/01/2025 10h49 até a republicação.

**beps_2024: 31/03/2025 (data em que o arquivo do boletim de dezembro de 2024 foi salvo; a página não guarda mais a data de publicação).**
- A página do boletim de dez/2024 (https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/Dados-estatisticos-previdencia-social-e-inss/boletins-da-previdencia-social/2024-1/beps122024_final.xls/view, lida em 06/10/2026) diz "Publicado em 03/07/2026 19h23" e "Atualizado em 07/07/2026 13h02", igual a todos os boletins de 2024 a jan/2026. O servidor não manda `Last-Modified`. O Internet Archive não tem cópia do arquivo nem da página de dez/2024 (busca por prefixo nos dois endereços, o antigo `/arquivos/` e o novo `/2024-1/`); a cópia de 13/03/2025 da página "BEPS anteriores" ainda ia só até out/2024.
- O arquivo oficial (beps122024_final.xls, baixado do endereço acima e apagado depois) traz nas propriedades: salvo pela última vez em 31/03/2025 20h46 UTC (17h46 em Brasília). Lido com `pipelines/complete_totals/ole_saved_date.py`.
- Calibração do método: nos boletins de mai/2026 e jun/2026 republicados em 31/08/2026, a página diz "Publicado em 31/08/2026 17h09" e o arquivo foi salvo às 19h51 e 19h52 UTC do mesmo dia (16h51 e 16h52 em Brasília), 17 minutos antes. O boletim de out/2024 foi salvo em 18/02/2025, coerente com a página de 13/03/2025 que já o listava.
- Recomendação para a tela: "dezembro de 2024 publicado em 31/03/2025 (data do arquivo oficial)". A data exata da publicação não está mais na página; a data do arquivo é a mais próxima que a fonte oficial guarda.

## Não consegui confirmar

1. **Ponte, PJ-00170/2006, Prosul, julho e setembro de 2014 (R$ 288.334,03).** Só a tabela da CPI traz esses pagamentos. Tentado: extrato SICOP do contrato (para em 26/03/2014) e consulta por credor do Portal de SC (credor 951, Deinfra, jul/2014 e set/2014: R$ 2.748.197,03 e R$ 1.701.345,55, porque a Prosul tem outros contratos no mesmo mês). Para a Concremat, o mesmo tipo de lacuna foi confirmado pela consulta por credor (R$ 479.649,53 em 2014). Os dois valores entram no total porque a tabela da CPI fecha com o seu TOTAL e com o valor do contrato.
2. **Ponte, notícia do TCE-SC de 2015 ("R$ 19,4 milhões" pagos à supervisão).** Não confere com os pagamentos; bate com valor de contrato mais aditivos. O relatório técnico DLC 084/2014, citado no acórdão, não foi achado numa busca na web; o sistema de consulta de processos do TCE-SC não foi consultado pelo número do processo.
3. **Linha 17-Ouro, 2010 a 2012.** Uma fonte por ano: Relatório da Administração 2011 (cópia do Internet Archive de um arquivo digitalizado, conferida pela soma da coluna) e Relatório de Administração 2013. O Relatório de 2012 não foi achado: o Portal da Transparência do Metrô começa em 2013 e as cópias de 2013 do endereço antigo no Internet Archive redirecionam para o arquivo de 2011.
4. **Linha 17-Ouro, R$ 5,97 bi do governo.** Não há documento que detalhe o número. A série do Metrô dá R$ 5,54 bi até agosto de 2026.
5. **Linha 17-Ouro, 2013 e 2022.** Há números diferentes entre documentos do próprio Metrô (2013: Relatórios de Administração 326,3 contra um gráfico do Relatório Integrado de 2017 em que a coluna inteira é outra; 2022: Acompanhamento de dezembro, 173,4, contra os Relatórios Integrados de 2023 e 2025, 206,02). Usados os valores explicados na seção 2.
6. **ETE Insular, pago em 2026 e definição de "consumido".** A Casan não publica pagamentos por contrato nem define "consumido". Tentado: telas e scripts do portal da Casan (extrato do contrato, saldos contratuais, FAQ, mapa do site), página "Despesa da Empresa", Relatório da Administração e DFP de 2025, e as notícias da Casan. O caminho que resta é um pedido à Casan pela Lei de Acesso à Informação.
7. **Banco Master, regimes próprios de previdência (R$ 1,867 bi).** A página do Ministério está restrita e sem cópia no Internet Archive (ver seção 5).
8. **Banco Master, prejuízo e aporte do DF.** O BRB diz que o prejuízo depende das demonstrações de 2025, ainda não publicadas até a assembleia de 24/08/2026; quanto do aumento de capital o DF subscreveu não está nos documentos lidos (o Fato Relevante de 27/05/2026 trata só do procedimento de homologação parcial).
9. **BEPS 2024, data exata de publicação.** A página não guarda mais a data original e o Internet Archive não tem cópia; usada a data do arquivo oficial, com a calibração descrita na seção 6.
