# Exportações do Brasil por produto: o que o país vende, para quem, quanto do que produz e a que preço

> **English summary.** Official datasets on what Brazil sells abroad (every SH4 product, 2025 and 2026 to date, US$ FOB, kg,
> R$ at BCB PTAX), by state, imports and trade balance, the share of national output that is exported for the goods the owner
> named, and export unit values against World Bank reference prices. Sources: Comex Stat API (MDIC/Secex), IBGE SIDRA, Conab, ANP, ANM, BCB SGS, World Bank Pink Sheet.

Data da pesquisa: 2026-10-06. Pedido do autor (palavras dele): *"bring a new section and column showing brazil's most lucrative
selling goods (not just most lucrative but every good we sell not only for the inside market but mostly to the outside cause in
truth Brazil is still a colony and sells almost everything abroad for the price of nothing) -- get all this information together
accurately and clearly"*. Citou carne, banana, café, terras raras e produtos da Amazônia.

Regra deste trabalho: só fonte oficial primária; o número é lido na fonte; o que não abriu fica "não confirmado".

## Andamento (registro incremental)

### 1. Comex Stat: como a API funciona (lido na documentação oficial)

- Documentação: https://api-comexstat.mdic.gov.br/docs (descrição OpenAPI em https://api-comexstat.mdic.gov.br/docs/doc.yaml).
- Consulta: `POST https://api-comexstat.mdic.gov.br/general?language=pt` com corpo JSON
  `{"flow":"export"|"import","monthDetail":bool,"period":{"from":"AAAA-MM","to":"AAAA-MM"},"filters":[...],"details":[...],"metrics":["metricFOB","metricKG",...]}`.
  Detalhamentos aceitos: country, economicBlock, state (UF do produto), via, urf, ncm, subHeading (SH6), heading (SH4), chapter (SH2),
  section, CGCE, CUCI e ISIC. Métricas: metricFOB (US$ FOB), metricKG (quilograma líquido), metricStatistic (só com ncm), e para
  importação metricFreight, metricInsurance, metricCIF.
- Última atualização (`GET /general/dates/updated`, lida em 2026-10-06): `{"updated":"2026-10-06","year":"2026","monthNumber":"09"}`.
  Portanto 2026 vai de janeiro a setembro.
- Limite de uso: a API responde 429 ("Você excedeu o limite de solicitações. Por favor, tente novamente em 10 segundos") a chamadas
  seguidas; os scripts esperam 11 s e repetem.
- Totais oficiais de conferência (arquivo pequeno do próprio MDIC, 2 KB):
  https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_TOTAIS_CONFERENCIA.csv e `IMP_TOTAIS_CONFERENCIA.csv`.
  Exportação 2025: US$ 348.278.462.500 FOB, 859.827.661.441 kg; 2026 (jan a set): US$ 284.654.368.793 FOB.
  A API devolve o mesmo total de 2025 ao dólar (consulta sem detalhamento).
- **Armadilha achada:** a soma por posição SH4 (`details:["heading"]`) dá US$ 348.278.456.345 em 2025, US$ 6.155 a menos que o
  total. A diferença são dois NCM que a tabela de correspondência da API não liga a nenhuma posição: 81126100 (desperdícios e
  resíduos de cádmio, US$ 4.822) e 85492100 (desperdícios elétricos e eletrônicos com cádmio, mercúrio, chumbo ou PCB, US$ 1.333).
  Por isso os scripts consultam por NCM (8 dígitos) e montam a SH4 pelos 4 primeiros dígitos, que é a definição da posição; a
  soma por NCM fecha com o total ao dólar.
- Tabelas auxiliares oficiais (pequenas, não são a base bruta): `NCM.csv` (3,4 MB, traz o código de fator agregado de cada NCM) e
  `NCM_FAT_AGREG.csv` em https://balanca.mdic.gov.br/balanca/bd/tabelas/. Fator agregado: 01 básicos; 02 semimanufaturados;
  03 manufaturados; 04 transações especiais; 05 consumo de bordo; 06 reexportação.

- Câmbio: Banco Central, SGS 3698 (dólar americano, venda, média mensal),
  https://api.bcb.gov.br/dados/serie/bcdata.sgs.3698/dados?formato=json. Conferido mês a mês contra a média da PTAX diária de
  venda do serviço PTAX do BCB (https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo...): bate a 4
  casas em todos os 21 meses. **Armadilha:** o serviço PTAX devolveu o dia 2025-04-23 duas vezes; sem tirar a duplicata, abril de
  2025 dá 5,7791 em vez de 5,7837. Os scripts guardam uma cotação por dia.
- Rede: o Python recusa a cadeia de certificados de balanca.mdic.gov.br; os scripts usam curl (com verificação), como os outros
  scripts do projeto.
- UF: "No módulo de pesquisa 'Dados Gerais' do Comex Stat, o critério para as exportações por UF considera o estado produtor da
  mercadoria, independentemente da sede (município) onde está localizada a empresa exportadora. No caso das IMPORTAÇÕES, a UF do
  produto se refere ao domicílio fiscal da empresa importadora" (FAQ oficial, pergunta 10,
  https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/perguntas-frequentes-faq).
- Fator agregado: a Secex **descontinuou** a divulgação por fator agregado ao adotar a ISIC (Nota Metodológica ISIC, versão 1.1,
  fevereiro de 2020, https://balanca.mdic.gov.br/balanca/metodologia/Nota_ISIC-CUCI.pdf: "o objetivo de adotar a classificação
  ISIC e, por consequência discontinuar as séries de fator agregado"). A tabela oficial NCM.csv ainda traz o código de fator
  agregado: todos os NCM exportados em 2025 têm código (01, 02, 03 ou "NA" em 22 NCM, US$ 0,13 bi). A série de fator agregado
  depois de 2019 é, portanto, um cálculo feito aqui com a tabela oficial, não uma divulgação da Secex; a série oficial atual é a
  ISIC (Agropecuária, Indústria Extrativa, Indústria de Transformação, Outros Produtos), que a API entrega direto.

### 2. Conjunto 1: exportações por produto (feito)

Script `data/scripts/trade/build_exports_by_product.py` -> `data/trade/exports-by-product.json` (519 KB).
- 21 consultas por NCM, uma por mês (2025-01 a 2026-09), mais total mensal, nomes SH4 e SH2, e países dos 50 maiores.
- Checagens que passaram: NCM somam o total mensal da API ao dólar e ao kg em todos os meses; cada período bate com o arquivo
  oficial de conferência (2025: US$ 348.278.462.500 e 859.827.661.441 kg; 2026 jan a set: US$ 284.654.368.793); os países de
  cada um dos 50 maiores produtos somam o produto ao dólar; PTAX conferida. `--control` (tira o maior NCM de jan/2025) falhou nas
  três primeiras checagens, como devia.
- Resultado 2025: 1.194 posições SH4 exportadas; US$ 348,28 bi FOB = R$ 1.942,55 bi (R$ 1.942.546.721.202,80).
  2026 (jan a set): 1.196 posições; US$ 284,65 bi = R$ 1.463,17 bi.
- 10 maiores de 2025 (participação no total): petróleo bruto 2709 (12,79%), soja 1201 (12,50%), minério de ferro 2601 (8,32%),
  café 0901 (4,28%), carne bovina congelada 0202 (4,15%), açúcar 1701 (4,05%), óleos de petróleo exceto brutos 2710 (2,97%),
  celulose 4703 (2,63%), carnes de aves 0207 (2,53%), milho 1005 (2,46%). Juntos: 56,7%. Os 20 maiores: 70,9%.
- Destinos: a China comprou 79,3% da soja, 67,6% do minério de ferro, 61,2% da carne bovina congelada e 45,0% do petróleo bruto
  em 2025.

### 3. Conjunto 2: exportações por estado (feito)

Script `data/scripts/trade/build_exports_by_uf.py` -> `data/trade/exports-by-uf.json` (60 KB). Consultas: `details:["state"]`,
`["state","ncm"]` e `["state"]` mensal, por período.
- Checagens que passaram: os 27 estados mais "Não Declarada" somam o total do Brasil ao dólar e ao kg nos dois períodos; os NCM de
  cada estado somam o estado; os estados somam cada mês. `--control` (tira um estado) falhou, como devia.
- 2025: SP US$ 71,39 bi (20,50%), RJ 48,98 (14,06%), MG 45,83 (13,16%), MT 30,19 (8,67%), PA 24,34 (6,99%), PR 23,65 (6,79%),
  RS 21,53 (6,18%). "Não Declarada": US$ 2,31 bi em 2025 e US$ 4,64 bi em 2026 (jan a set), quase tudo petróleo.
- O petróleo bruto é 79,2% das exportações do RJ; minério de ferro é 47,8% das do PA; soja é 82,7% das do PI.

### 4. Conjunto 3: importações por produto e saldo (feito)

Script `data/scripts/trade/build_imports_by_product.py` -> `data/trade/imports-by-product.json` (215 KB, linhas compactas).
- Checagens que passaram: NCM importados somam o total da API ao dólar e ao kg; exportação e importação de cada período batem
  com os arquivos oficiais de conferência; os meses somam o período. `--control` falhou, como devia.
- 2025: importações US$ 280,21 bi FOB (280.208.433.825); saldo US$ 68,07 bi. 2026 (jan a set): importações US$ 222,26 bi; saldo
  US$ 62,40 bi.
- Maiores importações de 2025: óleos de petróleo exceto brutos 2710 (US$ 15,55 bi, combustíveis como diesel), turbinas 8411
  (10,99), partes de veículos 8708 (8,62), automóveis 8703 (7,39), medicamentos 3004 (7,35), petróleo bruto 2709 (6,61),
  produtos do sangue e vacinas 3002 (6,53), defensivos agrícolas 3808 (5,60), circuitos integrados 8542 (5,55), adubos 3102 e
  3105 (4,87 e 4,71).

### 5. Conjunto 5: preço de exportação contra preço de referência (feito)

Script `data/scripts/trade/build_export_prices.py` -> `data/trade/export-prices.json` (26 KB). Os 10 maiores produtos de 2025 mais
farelo de soja (2304), algodão (5201) e banana (0803, citada pelo autor).
- Brasil: valor unitário = US$ FOB / kg líquido por ano (Comex Stat, consulta `details:["heading"]` de 2015-01 a 2025-12).
  Petróleo bruto por barril: NCM 27090010, US$ FOB / (m³ declarados / 0,158987294928).
- Referência: Banco Mundial, Pink Sheet, arquivo anual
  https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx
  (atualizado em 2 de setembro de 2026) e mensal `CMO-Historical-Data-Monthly.xlsx` (2 de outubro de 2026), página
  https://www.worldbank.org/en/research/commodity-markets. As definições de cada série foram lidas na aba "Description" do arquivo.
- **Armadilhas achadas:**
  - O arquivo anual do Banco Mundial arredonda (açúcar 2015: 0,30 US$/kg contra média mensal de 0,295). O valor usado é a média
    dos 12 meses publicados, conferida com o anual dentro do arredondamento.
  - A quantidade estatística (m³) do petróleo de fevereiro de 2017 dá 99 kg por m³: erro de declaração. A própria Secex avisa que
    essa métrica é a menos conferida das três (Nota Metodológica DIEST "Quantidade Estatística",
    https://balanca.mdic.gov.br/balanca/metodologia/Nota_Quantidade_Estatistica.pdf). Esse mês fica fora do preço por barril.
  - Desde setembro de 2021 a série "Chicken" do Banco Mundial é o preço de atacado do frango congelado **em São Paulo**: é um preço
    do próprio Brasil, não um preço mundial. Fica no arquivo com essa nota.
  - A série de soja do Banco Mundial mudou de base (c.i.f. Roterdã até 2024; f.o.b. Golfo dos EUA desde 2025); o farelo de soja de
    referência foi, de 1999 a 2024, o próprio farelo brasileiro em Roterdã.
  - Não há referência do Banco Mundial para óleos de petróleo exceto brutos (2710) nem para celulose (4703): `null`.
- Checagens que passaram: US$ e kg de 2025 de cada produto iguais aos de `exports-by-product.json` (caminho de consulta diferente);
  preços do Banco Mundial conferidos; meses do petróleo com densidade declarada plausível. `--control` falhou, como devia.
- Razão preço do Brasil / referência, 2025 (1 = igual): petróleo 0,91 (US$ 63,06 contra Brent 69,05 por barril); soja 0,97
  (402 contra 414 US$/t); minério de ferro 0,69 (69,6 contra 100,2 US$/t, mas a referência inclui frete até a China e é por
  tonelada seca com 62% de ferro); café 0,77 do arábica e 1,35 do robusta (o Brasil exporta os dois); carne bovina congelada 0,77;
  açúcar 1,12; milho 1,03; farelo de soja 0,93; algodão 0,95; frango 1,04 (referência é preço de SP); banana 0,37 da referência
  dos EUA (a referência é preço de importação, com frete; o Brasil exporta pouca banana, quase toda por terra ao Mercosul).
- Série 2015 a 2025: soja entre 0,77 e 1,01; milho entre 0,79 e 1,08; açúcar entre 0,86 e 1,12; petróleo entre 0,78 e 0,93;
  minério entre 0,61 e 0,77 (sempre abaixo, coerente com frete e umidade fora da conta FOB).

### 6. Conjunto 6: contexto, exportações no PIB e tipo de produto (feito)

Script `data/scripts/trade/build_trade_context.py` -> `data/trade/trade-context.json` (24 KB).
- PIB e exportação de bens e serviços: IBGE, Contas Nacionais Trimestrais, SIDRA 1846, R$ milhões correntes, soma dos 4 trimestres:
  `https://apisidra.ibge.gov.br/values/t/1846/n1/all/v/585/p/200001-202504/c11255/90707,93404,93405,93406,102880,93407,93408`.
  Conferência anual: SIDRA 6784 (PIB anual, até 2023).
- Checagens: em todos os 104 trimestres, consumo das famílias + governo + investimento + estoques + exportação - importação = PIB
  (até R$ 3 milhões de arredondamento). O PIB somado dos trimestres bate com a tabela anual com diferença de R$ 1 milhão
  (arredondamento), **menos 2017, 2018 e 2019, que diferem cerca de 0,1%** (2017: 6.585.479 contra 6.592.743; 2018: 7.004.141
  contra 6.996.861; 2019: 7.389.131 contra 7.394.332). São duas tabelas do IBGE com versões diferentes desses anos; ficam
  registradas no JSON. Fator agregado e ISIC somam o total oficial ao dólar em todos os 26 anos. `--control` falhou, como devia.
- **Exportação de bens e serviços / PIB:** 2000: 10,2%; 2005: 15,2%; 2010: 10,9%; 2015: 12,9%; 2019: 14,1%; 2022: 19,6% (máximo
  da série); 2025: 17,8% (R$ 2.270 bi de R$ 12.739 bi). Importação / PIB 2025: 17,5%.
- **Fator agregado** (calculado com a tabela NCM oficial): básicos 22,8% em 2000, 32,3% em 2007, 44,9% em 2010, 53,8% em 2019,
  57,3% em 2020 e 58,2% em 2025; manufaturados 59,8% em 2000 e 28,7% em 2025; semimanufaturados entre 12,9% e 15,4%.
  Limitação: a tabela atual pode classificar algum NCM antigo de forma diferente da que a Secex usava na época. "Consumo de
  bordo" e "transações especiais" quase somem da exportação a partir de 2019. Motivo **não confirmado**: a nota de revisão de
  metodologia de abril de 2021 (https://balanca.mdic.gov.br/balanca/metodologia/NotaInformativaRevisaoMetodologia.pdf, lida)
  trata do Repetro, de Itaipu e do Recof, e não fala de consumo de bordo.
- **ISIC** (divisão oficial atual): 2025 indústria de transformação 54,1%, extrativa 23,1%, agropecuária 22,3%, outros 0,6%;
  2000: transformação 83,0%, agropecuária 8,1%, extrativa 6,7%. Atenção: a ISIC põe carne, açúcar, farelo, celulose e
  suco na indústria de transformação; o fator agregado põe carne in natura e soja em grão em básicos.

### 7. Conjunto 4: quanto da produção vai para fora (feito)

Script `data/scripts/trade/build_export_share.py` -> `data/trade/export-share-of-production.json` (19 KB).

**Armadilha grave da API do Comex Stat achada aqui:** o período é lido como uma grade, anos de..até vezes meses de..até.
`2024-02` a `2025-03` devolve só fevereiro e março de cada ano; `2025-02` a `2026-01` devolve nada. Um período que cruza o ano
tem de ser pedido um ano civil por vez. (Os outros scripts só usam períodos dentro do mesmo ano ou de janeiro a dezembro, que a
grade cobre por inteiro.)

Fontes lidas na origem:
- Conab, Quadro de oferta e demanda de grãos, estimativa de setembro de 2026 (arquivo .ods com nome .xlsx):
  https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/analises-do-mercado-agropecuario-e-extrativista/analises-de-mercado/quadro-de-oferta-e-demanda/graos/quadro-de-oferta-e-demanda-de-graos-2026/quadro-de-oferta-e-demanda-graos-setembro-2026.xlsx
  Estoque de passagem: soja e algodão em 31 de dezembro (a safra 2024/25 corresponde às exportações de 2025); milho em 31 de
  janeiro (exportações de fevereiro de 2025 a janeiro de 2026).
- Conab, Quadro de suprimento de carnes, abril de 2026 (equivalente carcaça para bovinos e suínos):
  .../quadro-de-oferta-e-demanda/carnes/oferta-e-demanda-de-carnes-2026-1/quadro_suprimentos_abr_2026.xlsx. A planilha diz que a
  produção de frango vem da APINCO (associação do setor) e a de bovinos e suínos do abate do IBGE.
- Conab, cana-de-açúcar, 4º levantamento da safra 2025/26 (abril de 2026):
  https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cana-de-acucar/arquivos-boletins/4o-levantamento-safra-2025-26/site_previsao_de_safra-cana-de-acucar-abr-2026.xlsx
- IBGE SIDRA: PAM 2025 (tabela 5457), PEVS 2025 (289), Abate 2025 (1092, 1093, 1094), PIA-Produto 2024 (10476).
- ANP, dados abertos: produção de petróleo em m³ (https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/ppgn-el/producao-petroleo-m3.csv,
  fonte Boletim Mensal de Produção) e exportação de petróleo em m³ e US$ FOB (.../arquivos/ie/petroleo/importacoes-exportacoes-petroleo-2000-2025.csv,
  fonte Secex segundo o metadado da ANP).
- ANM, Anuário Mineral Brasileiro 2025, ano-base 2024 (PDF, tabela 3.1):
  https://www.gov.br/anm/pt-br/assuntos/economia-mineral/publicacoes/anuario-mineral/anuario-mineral-brasileiro/amb_metalicos__rev_2.pdf;
  ANM, Sumário Mineral 2025, ano-base 2024: https://www.gov.br/anm/pt-br/assuntos/economia-mineral/publicacoes/sumario-mineral/sumario-mineral-brasileiro-2025/sumario-2025.pdf.
  Os números da ANM ficam fixados no script e são reconferidos no texto do PDF a cada execução (pdftotext).

Checagens que passaram: exportação da Conab igual ao Comex Stat nos mesmos meses (soja em grão 108.181,1 mil t contra 108.181,06;
farelo 23.269,2 contra 23.269,2; óleo 1.362,9 contra 1.362,9; algodão 3.026,0 contra 3.026,0; milho 41.631,5 contra 41.580,1,
diferença de 0,1%); receita de exportação de petróleo da ANP em 2025 (US$ 44.536.157.927) igual ao Comex Stat NCM 27090010 ao
dólar; os quatro trimestres de 2025 no abate; os números da ANM achados nos PDFs. `--control` (soja de 2024) falhou, como devia.

| Produto | Exportado / produzido | Produção | Exportação | Fonte e período |
|---|---|---|---|---|
| Minério de ferro | 86,7% | 448,6 Mt (beneficiada) | 388,7 Mt | ANM 2024 e Comex Stat 2024 (último ano com produção da ANM) |
| Açúcar | 77,1% | 44,18 Mt | 34,05 Mt | Conab safra 2025/26, exportação de abr/2025 a mar/2026 (2024/25: 79,6%) |
| Algodão em pluma | 74,1% | 4,08 Mt | 3,03 Mt | Conab safra 2024/25 |
| Café em grão | 65,3% | 3,48 Mt | 2,27 Mt | IBGE PAM 2025 e Comex Stat 2025 (0901; sem solúvel) |
| Soja em grão | 63,1% | 171,5 Mt | 108,2 Mt | Conab 2024/25 (com a produção do IBGE PAM 2025, 65,5%) |
| Farelo de soja | 52,6% | 44,2 Mt | 23,3 Mt | Conab 2025 |
| Petróleo bruto | 51,0% | 218,8 milhões de m³ | 111,6 milhões de m³ | ANP 2025 |
| Carne bovina | 38,0% | 11,93 Mt eq. carcaça | 4,53 Mt eq. carcaça | Conab 2025 |
| Carne de frango | 32,6% | 15,82 Mt | 5,16 Mt | Conab 2025 (produção da APINCO); com o abate do IBGE e o peso exportado das subposições 0207.11 a 0207.14: 34,2% |
| Milho | 29,5% | 141,2 Mt | 41,6 Mt | Conab 2024/25 (fev/2025 a jan/2026) |
| Carne suína | 26,3% | 5,66 Mt eq. carcaça | 1,49 Mt eq. carcaça | Conab 2025 |
| Castanha-do-pará | pelo menos 16,2% | 26.343 t | 5.023 t (3.685 com casca, 1.338 sem casca; 769 t importadas) | IBGE PEVS 2025 e Comex Stat 2025 |
| Óleo de soja | 11,6% | 11,77 Mt | 1,36 Mt | Conab 2025 |
| Banana | 1,1% | 7,29 Mt | 80 mil t | IBGE PAM 2025 e Comex Stat 2025 |
| Suco de laranja | não calculado | 16,56 Mt de laranja | 2,22 Mt de suco | não há produção oficial de suco em t |
| Celulose | não calculado | 10,39 Mt (PIA-Produto 2024) | 18,56 Mt (2024) | a PIA registra menos que o exportado; não cobre toda a produção |
| Terras raras | não calculado | sem número oficial | 680 t, US$ 12,0 milhões (2025) | ANM: produção 2024 "pequena"; reservas de 11,4 Mt, 2ª do mundo |
| Açaí | não calculado | 2,27 Mt de fruto (PAM + PEVS) | 182 t de purê (NCM 2007.99.21) | fruto e purê não são comparáveis; parte pode sair em outros códigos |
| Madeira nativa | não calculado | 10,53 milhões de m³ em tora (PEVS) | 248 mil t de madeira tropical serrada e beneficiada, US$ 333 milhões | m³ de tora e kg de serrado não são comparáveis |

Notas: na carne bovina, a produção da Conab (11.933,85 mil t) é maior que o peso de carcaças da pesquisa de abate do IBGE
(11.103,2 mil t, só abate sob inspeção); a planilha não detalha a diferença. Com o número do IBGE a proporção seria 40,8%.
A ANM informa que 70% das pelotas de minério de ferro produzidas em 2024 foram exportadas (AMB 2025, apêndice).

## O que os dados dizem sobre a premissa

A premissa do pedido tem três partes; cada uma é testada abaixo só com os números acima.

**1. "Vende quase tudo para fora".** Para a economia como um todo, não: a exportação de bens e serviços equivaleu a 17,8% do PIB
em 2025 (IBGE, Contas Nacionais), e a exportação de bens convertida pela PTAX (R$ 1.942,5 bi) a 15,2% do PIB. A importação foi
17,5% do PIB. Para alguns produtos, sim, a maior parte sai do país: minério de ferro 86,7% (2024), açúcar 77,1%, algodão 74,1%,
café 65,3%, soja em grão 63,1%, farelo de soja 52,6%, petróleo bruto 51,0%. Para outros, a maior parte fica: carne bovina 38,0%
exportada, frango 32,6%, milho 29,5%, carne suína 26,3%, óleo de soja 11,6%, banana 1,1%. Portanto a frase vale para um grupo de
produtos básicos e não vale para a economia nem para as carnes, o milho, o óleo e a banana.

**2. "Pelo preço de nada".** O valor unitário de exportação do Brasil fica perto do preço internacional de referência do Banco
Mundial nos produtos em que a comparação é direta: em 2025, soja 0,97 do preço de referência, milho 1,03, açúcar 1,12, algodão
0,95, farelo de soja 0,93, petróleo 0,91 do Brent. Fica bem abaixo no minério de ferro (0,69), mas a referência é o minério com
62% de ferro entregue na China, com frete e por tonelada seca, e o valor do Brasil é no porto brasileiro, sem frete e com
umidade; e na carne bovina congelada (0,77 da carne magra da Nova Zelândia posta nos EUA). Os dados não mostram venda por
"preço de nada"; mostram preço de mercado, com diferenças que em parte são frete, qualidade e base de entrega.

**3. O perfil da pauta.** A parte de produtos básicos no valor exportado subiu de 22,8% em 2000 para 58,2% em 2025, e a de
manufaturados caiu de 59,8% para 28,7% (fator agregado, calculado com a tabela oficial NCM). Pela ISIC, que a Secex usa hoje, a
indústria de transformação caiu de 83,0% para 54,1%, e a agropecuária subiu de 8,1% para 22,3%, a extrativa de 6,7% para 23,1%.
Os 10 maiores produtos somam 56,7% do valor exportado em 2025; pelo fator agregado, 83,0% do valor desses 10 é de produtos
básicos (petróleo bruto, soja, minério de ferro, café, carne bovina congelada, carne de frango, milho), 10,8% de semimanufaturados
(celulose e a maior parte do açúcar) e 6,3% de manufaturados (derivados de petróleo e açúcar refinado). A China comprou 79,3% da
soja, 67,6% do minério de ferro e 61,2% da carne bovina congelada. Esses números descrevem a composição da pauta; não dizem, por
si, que o país é ou não é uma colônia, e o site não deve fazer essa afirmação (D45, D51).

**Contexto que o leitor precisa ao lado:** o Brasil vendeu US$ 348,3 bi e comprou US$ 280,2 bi em 2025 (saldo de US$ 68,1 bi). Entre
as maiores compras estão óleo diesel e outros derivados de petróleo (US$ 15,6 bi), turbinas, partes e automóveis, medicamentos,
vacinas, defensivos agrícolas, circuitos integrados e adubos.

## O que não foi confirmado

- Produção oficial de **suco de laranja** em toneladas (não existe); conversão oficial de fruta em suco (não existe).
- Produção oficial de **celulose** que cubra o setor: a PIA-Produto 2024 registra 10,39 Mt, menos que os 18,56 Mt exportados.
- Produção de **terras raras** em número: a ANM só diz que foi "pequena" em 2024.
- **Açaí** e **madeira nativa**: produção e exportação em unidades que não se comparam sem conversão oficial; parte do açaí pode
  sair em códigos genéricos de polpa e mistura que não o separam.
- A diferença entre a produção de carne bovina da Conab e o abate do IBGE não está explicada na planilha da Conab.
- Produção de frango por pesquisa oficial completa: o abate do IBGE cobre só o abate sob inspeção; a Conab usa número da APINCO.
- O motivo do sumiço de "consumo de bordo" e "transações especiais" a partir de 2019 no fator agregado.
- Fator agregado depois de 2019: não é número publicado pela Secex (calculado aqui com a tabela NCM oficial).
- Diferença de cerca de 0,1% entre o PIB trimestral e o anual do IBGE em 2017 a 2019 (versões diferentes nas duas tabelas).
- Preço de referência do Banco Mundial para celulose e para derivados de petróleo (não existe na Pink Sheet atual).

## Arquivos e como rodar

Todos em `data/scripts/trade/`, cada um com checagem e `--control` que tem de falhar (todos conferidos em 2026-10-06/07):

```bash
python3 data/scripts/trade/build_exports_by_product.py [--control]   # -> data/trade/exports-by-product.json
python3 data/scripts/trade/build_exports_by_uf.py [--control]        # -> data/trade/exports-by-uf.json
python3 data/scripts/trade/build_imports_by_product.py [--control]   # -> data/trade/imports-by-product.json
python3 data/scripts/trade/build_export_prices.py [--control]        # -> data/trade/export-prices.json (depois do primeiro)
python3 data/scripts/trade/build_trade_context.py [--control]        # -> data/trade/trade-context.json
python3 data/scripts/trade/build_export_share.py [--control]         # -> data/trade/export-share-of-production.json
```

`trade_common.py` tem a chamada à API (espera e repete no 429), a PTAX conferida, leitores de .xlsx e .ods sem pacote externo e
a recusa de gravar JSON com travessão. `BI_TRADE_CACHE=<pasta temporária>` guarda as respostas entre execuções (opcional; sem ela
nada é gravado em disco). Os arquivos da Conab mudam de nome a cada mês: o script fixa o de setembro de 2026 (grãos), abril de
2026 (carnes e cana); atualizar a URL quando sair a próxima estimativa.
