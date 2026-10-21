# Ponte Hercílio Luz: quanto foi pago, contrato por contrato

Coleta: 05/10/2026. Serve à decisão D91, D92 e D93 (primeiro número do cartão do caso: "Total gasto", lido por contrato e não por empresa). Dados: `data/hercilio-luz-paid-by-contract.json`. Script: `data/scripts/ponte/build_paid_by_contract.py` (checagem ao centavo; `--control` tem de falhar).

## Resposta

- **Total pago nos 13 contratos da restauração: R$ 473.654.492,00** (valores nominais, sem correção).
- Desse total, **R$ 444.532.975,60** vêm do extrato SICOP de cada contrato no Portal da Transparência de SC (pagamentos de 2011 a 2020).
- Os outros **R$ 29.121.516,40** são o pago antes de 2011 no contrato PJ-00264/2008 (Consórcio Florianópolis Monumento): o TCE-SC registra R$ 38.921.239,05 pagos no contrato até maio de 2012 (http://consulta.tce.sc.gov.br/relatoriosdecisao/relatoriotecnico/3728501.PDF, item 2.6), e o Portal mostra R$ 9.799.722,65 pagos de janeiro de 2011 a maio de 2012; a diferença é o pago antes de 2011. É conta entre dois números oficiais, não estimativa, mas nenhum documento imprime esse valor.
- **Falta** o pago de 2006 a 2010 no contrato de supervisão PJ-00170/2006 (Prosul e Concremat): nenhum número oficial de valor pago foi encontrado (ver "Não confirmado").
- Para comparar: o valor atual dos 13 contratos no registro soma R$ 484.645.236,82 (valor de contrato, não pago).

## Pago por contrato

Fonte de cada linha: extrato SICOP do contrato na API do Portal da Transparência do Poder Executivo de SC (`contratoResumoFinanceiro` e `contratoPagamento`). O número do título (NUTITULO) de cada contrato vem do registro de contratos SIGEF/SICOP da CGE-SC (https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/ff7c3cac-3e38-4801-9fd8-e4ccb69ca31d/download/contratos.csv).

| Contrato | Empresa | Pago (linhas positivas) | Estornado | Pago líquido | Primeiro e último pagamento | Fonte |
|---|---|---|---|---|---|---|
| PJ-00170/2006 | CONCREMAT ENG. E TECNOLOGIA S.A. | R$ 2.149.968,61 | R$ 5.358,25 | **R$ 2.144.610,36** | 11/01/2011 a 29/04/2016 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=53682 |
| PJ-00170/2006/PROSUL | PROSUL - Proj., Superv. e Planejamento Ltda | R$ 3.385.087,62 | R$ 13.779,78 | **R$ 3.371.307,84** | 11/01/2011 a 26/03/2014 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=53663 |
| PJ-00264/2008 | Consórcio Florianópolis Monumento | R$ 33.905.128,44 | R$ 17.772,75 | **R$ 33.887.355,69** | 07/01/2011 a 04/11/2014 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=70204 |
| PJ-00204/2014 | RMG ENGENHARIA S/C LTDA. | R$ 1.951.820,02 | R$ 0,00 | **R$ 1.951.820,02** | 08/04/2015 a 19/05/2015 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=88906 |
| PJ-00012/2015 | EMPA SA SERVIÇOS DE ENGENHARIA | R$ 12.624.974,17 | R$ 0,00 | **R$ 12.624.974,17** | 13/05/2015 a 26/11/2015 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=89257 |
| PJ-00143/2015 | EMPA SA SERVIÇOS DE ENGENHARIA | R$ 11.400.601,42 | R$ 0,00 | **R$ 11.400.601,42** | 17/11/2015 a 05/05/2016 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=90666 |
| PJ-00001/2016/FARES | Fares & Associados Engenharia Ltda. | R$ 137.482,95 | R$ 0,00 | **R$ 137.482,95** | 07/07/2016 a 13/07/2016 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=91908 |
| PJ-00056/2016 | TEIXEIRA DUARTE - Engenharia e Construções S.A. | R$ 372.292.879,82 | R$ 8.738.183,49 | **R$ 363.554.696,33** | 30/05/2016 a 29/06/2020 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=91858 |
| PJ-00093/2016 | RMG ENGENHARIA S/C LTDA. | R$ 10.514.984,53 | R$ 37.903,70 | **R$ 10.477.080,83** | 08/07/2016 a 27/09/2019 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=92132 |
| PJ-00009/2019 | TEIXEIRA DUARTE - Engenharia e Construções S.A. | R$ 3.156.151,79 | R$ 0,00 | **R$ 3.156.151,79** | 18/03/2019 a 04/07/2019 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=97701 |
| CT-00006/2019 | RMG ENGENHARIA S/C LTDA. | R$ 1.712.033,96 | R$ 0,00 | **R$ 1.712.033,96** | 05/09/2019 a 01/07/2020 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=98298 |
| PJ-00060/2019 | GEOARQUEOLOGIA Pesquisa Científica Ltda - ME | R$ 80.260,31 | R$ 400,07 | **R$ 79.860,24** | 08/11/2019 a 23/11/2020 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=98300 |
| CT-00026/2019 | SDF Engenharia EIRELI | R$ 35.000,00 | R$ 0,00 | **R$ 35.000,00** | 11/03/2020 a 13/03/2020 | https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=98679 |
| | **Soma do Portal (calculada)** | | | **R$ 444.532.975,60** | 07/01/2011 a 23/11/2020 | |
| PJ-00264/2008 | Pago antes de 2011 (TCE-SC menos Portal até maio de 2012) | | | **R$ 29.121.516,40** | antes de 2011 | http://consulta.tce.sc.gov.br/relatoriosdecisao/relatoriotecnico/3728501.PDF |
| | **Total pago (calculado)** | | | **R$ 473.654.492,00** | | |

Como ler: "pago líquido" é a soma de todas as linhas de pagamento do extrato (despesa paga, retenções de ISS, IRRF, INSS e caução, menos os estornos). Em cada contrato e em cada ano essa soma é igual ao "vlpago" do resumo financeiro do próprio extrato, ao centavo. As datas são as da primeira e da última linha positiva.

## Antes de 2011 (o Portal começa em 2011)

O extrato SICOP do Portal só tem linhas de pagamento de 2011 em diante. Três linhas do registro são anteriores: PJ-00170/2006 (Concremat e Prosul) e PJ-00264/2008.

- **PJ-00264/2008.** TCE-SC, Relatório DLC 462/2012, item 2.6 (http://consulta.tce.sc.gov.br/relatoriosdecisao/relatoriotecnico/3728501.PDF): "Conforme extrato do Sistema Integrado de Controle de Obras Públicas - SICOP da Administração Estadual, atualizado em julho de 2012, o último pagamento ocorreu em maio do corrente ano, referente aos meses de janeiro a março de 2012, acumulando R$ 38.921.239,05". Conferências: (1) o valor do TCE-SC é igual, ao centavo, ao acumulado da medição 040 do SICOP (período até 31/03/2012); (2) R$ 38.921.239,05 + R$ 24.087.633,04 pagos no Portal depois de maio de 2012 = R$ 63.008.872,09, igual ao centavo à medição final acumulada no SICOP e ao valor atual do contrato no registro; (3) o extrato não tem pagamento entre 29/05/2012 e 17/08/2012, o que bate com "último pagamento em maio" num extrato atualizado em julho de 2012.
- **PJ-00170/2006 (supervisão, Consórcio Prosul-Concremat).** Nenhum valor pago de 2006 a 2010 encontrado. O mesmo relatório do TCE-SC (item 2.7 e item 2.10.4) traz valor inicial (R$ 9.811.282,66), aditivos e o custo mensal da supervisão (R$ 117.616,86, base abril de 2012), não o acumulado pago. O SICOP mede R$ 3.691.338,90 (Concremat) e R$ 5.536.403,29 (Prosul) acumulados até dezembro de 2010 (https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=53682 e ...=53663); medido não é pago, então esses valores ficam fora do total.

## Checagens

- Duas contas independentes: (1) inteiros em centavos a partir do "vlpago" anual de cada contrato; (2) Decimal sobre as linhas de pagamento. Portal: R$ 444.532.975,60 nas duas. Com o pré-2011: R$ 473.654.492,00 nas duas. Iguais ao centavo, contrato por contrato e ano por ano.
- Controle plantado: somar R$ 0,01 a uma linha do PJ-00056/2016 (`--control`) faz a checagem falhar ("PJ-00056/2016 2016: summary 61363201.36 vs lines 61363201.37") e nada é gravado.
- Contra a consulta por credor já guardada em `data/hercilio-luz.json`: Teixeira Duarte 2016 a 2019, EMPA 2015 e 2016, Consórcio Florianópolis Monumento 2011 a 2014, RMG 2015 a 2019, Fares 2016, Geoarqueologia 2020 e SDF 2020 são iguais ao centavo à soma dos contratos da ponte da mesma empresa no ano. Onde diferem, a empresa tem outros contratos com o Estado no ano (Teixeira Duarte 2020, RMG 2020 e 2021, Prosul, Concremat 2016), salvo os dois casos em "Não confirmado".
- Achado: como o "vlbruto" do credor (Teixeira Duarte, 2019: R$ 89.019.342,39) é igual à soma das linhas do contrato que já inclui os estornos negativos, o "vlbruto" da consulta por credor já desconta os estornos. Isso responde à ressalva "não se sabe se vlbruto já desconta vlestorno" de `data/hercilio-luz.json` (arquivo não editado).

## Não confirmado

- **Pago de 2006 a 2010 no PJ-00170/2006** (Prosul e Concremat): sem número oficial. Fora do total.
- **O pago antes de 2011 no PJ-00264/2008** (R$ 29.121.516,40) é uma diferença calculada; nenhum documento o imprime. Está no total porque as três conferências acima fecham ao centavo.
- **PJ-00060/2019 (Geoarqueologia), 2019:** a consulta por credor mostra R$ 16.402,68 pagos à empresa, que só tem este contrato no registro; o extrato do contrato mostra R$ 400,07 nesse ano. A diferença de R$ 16.002,61 não está ligada ao contrato no extrato e fica fora do total (https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/pgtocredor?anomesinifiltro=201901&anomesfimfiltro=201912&credorfiltro%5B%5D=583240&tipopagamentocredorfiltro=1&page=1&indicador=0).
- **PJ-00170/2006 (Concremat), 2011:** o extrato do contrato soma R$ 1.104.600,17 e a consulta por credor (CNPJ 33.146.648/0003-91) mostra R$ 993.730,38 para a empresa inteira no ano. A diferença de R$ 110.869,79 não foi explicada. O total usa o extrato do contrato.
- **Linhas "PP Resolvida por outra PP" (R$ 10.860.043,48 em 2016 e R$ 425.465,83 em 2018) e "Paga e Estornada por NE" (R$ 5.767.258,12 e o estorno de R$ 2.079.124,47 em 2019), todas no PJ-00056/2016:** entram porque o "vlpago" oficial do contrato e o "vlbruto" do credor as incluem. Sem elas, o pago ficaria muito abaixo do medido; com elas, o pago líquido (R$ 363.554.696,33) fica R$ 71.464,66 abaixo da medição final acumulada (R$ 363.626.160,99). O significado exato dessas situações no SIGEF não foi confirmado em documento.
- **DL-00001/2618-2019 (RMG, R$ 1.451.313,01 pagos em novembro de 2019)**: objeto "Para pagamento realizado na supervisão da PHL e que não estava no escopo do Contrato PJ 093/2016" (https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]=98648). Está fora dos 13 contratos (registro relacionado em `data/hercilio-luz.json`) e fora do total; com ele, o total seria R$ 475.105.805,01.
- Contratos da ponte anteriores a 2006 e posteriores a 2019 (por exemplo iluminação e manutenção) e gastos de outros órgãos ficam fora do escopo.

