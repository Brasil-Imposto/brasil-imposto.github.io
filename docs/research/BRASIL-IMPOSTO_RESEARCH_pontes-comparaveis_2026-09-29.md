# Pontes comparáveis à Ponte Hercílio Luz: custo por m² de tabuleiro, em R$ de dezembro de 2024

- **Data da coleta:** 2026-09-29.
- **Pergunta:** para o botão "Comparar com um projeto parecido", quanto custou, por metro quadrado de tabuleiro, restaurar a Ponte Hercílio Luz, e quanto custaram obras parecidas no mundo, tudo convertido para reais de dezembro de 2024 por dois métodos (câmbio de mercado e paridade de poder de compra).
- **Dados:** `data/bridge-comparables.json` (chaves em inglês, todos os fatores e fontes dentro do arquivo).
- **Scripts:** `data/scripts/bridges/download.sh` e `data/scripts/bridges/build.py` (reproduzem o JSON; ver seção 6).
- **Regra desta pesquisa:** nenhum número sem fórmula e fonte. Onde a fonte é de engenharia ou de imprensa, isso está escrito ao lado do número.

---

## 0. Resposta curta

| Obra | Tipo | Área de tabuleiro (m²) | Custo em R$ dez/2024, câmbio | Custo em R$ dez/2024, PPP | **R$/m², câmbio** | **R$/m², PPP** |
|---|---|---|---|---|---|---|
| **Ponte Hercílio Luz** (Florianópolis, 2006 a 2019) | Restauração de ponte pênsil de barras de olhal | 11.658 | 825,2 mi | 825,2 mi | **70.784** | **70.784** |
| Ponte Hercílio Luz, limite inferior (ver 3.3) | idem | 11.658 | 646,6 mi | 646,6 mi | 55.462 | 55.462 |
| Széchenyi Lánchíd (Budapeste, 2021 a 2023) | Restauração de ponte pênsil de correntes de barras de olhal | 4.100 | 458,8 mi | 462,6 mi | **111.880** | **112.815** |
| Lions' Gate Bridge (Vancouver, 2000 a 2001) | Troca de toda a estrutura suspensa de ponte pênsil | 13.721 | 406,7 mi | 176,3 mi | **29.640** | **12.846** |
| Ponte Pênsil Alves de Lima (Chavantes, SP, 2023) | Restauração leve de ponte pênsil histórica | 656 | 6,3 mi | 6,3 mi | **9.587** | **9.587** |
| Cầu Thuận Phước (Da Nang, 2003 a 2009) | Ponte pênsil **nova**, vão de 405 m | 33.408 | 374,2 mi | 780,7 mi | **11.200** | **23.368** |

**Leitura honesta, em um parágrafo.** A restauração da Hercílio Luz custou, por m² de tabuleiro, **menos** do que a da Ponte das Correntes de Budapeste, a comparação mais parecida em tipo e em época: cerca de 37% menos pelos dois métodos (R$ 70,8 mil contra R$ 111,9 mil e R$ 112,8 mil por m²); se a área de Budapeste for medida pela largura total de 14,5 m em vez da largura útil, a diferença cai para cerca de 15% (R$ 83,3 mil e R$ 84,0 mil por m²), ainda com Budapeste mais cara. A Hercílio Luz custou **mais** por m² do que as outras três: 2,4 vezes (câmbio) a 5,5 vezes (PPP) a troca do tabuleiro da Lions' Gate, 7,4 vezes a restauração leve da Alves de Lima e de 3 a 6 vezes a ponte pênsil nova de Da Nang. Mas os escopos não são iguais: na Hercílio Luz foram trocadas as próprias barras de olhal que sustentam o vão, as selas, as rótulas e os pendurais, todas as fundações foram reforçadas e foi preciso erguer 3.400 t de estrutura provisória para segurar o vão central; nada disso aconteceu em Vancouver nem em Chavantes, e em Budapeste as correntes foram tratadas, não substituídas. A ponte nova do Vietnã tem 65% da área em viadutos de acesso de concreto e foi feita em outro país e outra década; ela serve como ordem de grandeza, não como prova de que "sairia mais barato fazer outra". A tabela, portanto, **não** permite dizer que a Hercílio Luz custou caro ou barato; permite dizer que ela ficou abaixo da restauração europeia mais parecida e acima de obras de escopo menor.

---

## 1. Os comparáveis escolhidos

Critério: (a) restaurações de pontes pênseis históricas, de preferência de correntes ou barras de olhal; (b) uma ponte pênsil nova com vão central de 250 a 450 m, para a referência "restaurar ou construir". Cada candidato só entrou se havia custo publicado e dimensões suficientes para calcular a área de tabuleiro.

### 1.1 Széchenyi Lánchíd, Budapeste (Hungria), restauração 2021 a 2023

- **O que é:** ponte pênsil de correntes de barras de olhal, aberta em 1849 e reconstruída de 1947 a 1949 depois de destruída na guerra. Três vãos, pilares de pedra.
- **O que foi feito:** segundo a BKK (empresa de transporte da prefeitura), demolição do tabuleiro de concreto armado e construção de novo tabuleiro de aço ortotrópico; passeios de concreto demolidos e refeitos em aço; reparo e proteção anticorrosiva da estrutura metálica que ficou; proteção anticorrosiva das correntes acima do tabuleiro, nos canais e nas câmaras de ancoragem subterrâneas; restauro de pedras, rosetas e leões; guarda-corpos refeitos; iluminação nova; remanejamento de redes; impermeabilização das câmaras de ancoragem. **As correntes foram tratadas, não trocadas.** Fonte: https://bkk.hu/blog/rozsdas-volt-ragyogo-lett-a-lanchid-felujitas-kulisszatitkai.10600/
- **Datas:** contrato assinado em 2021-02-02, obra iniciada em 2021-03-17 (https://bkk.hu/fejlesztesek/kiemelt-fejlesztesek/archivum/a-lanchid-felujitasa/dokumentumok-kozbeszerzes-kozerdeku-adatok/); ponte devolvida aos usuários em 2023-08-04 (Budapest Közút: https://www.budapestkozut.hu/mernok-igazgatosag/szechenyi-lanchid/).
- **Dimensões:** comprimento 380,02 m; largura total 14,5 m; pista entre meios-fios 6,45 m; passeios de 2,17 m (https://bkk.hu/fejlesztesek/kiemelt-fejlesztesek/archivum/fovarosi-fejlesztesek/kozteruleti-fejlesztesek/-a-szechenyi-lanchid-rekonstrukcioja.5786/). **Vão central: não encontrado nas páginas oficiais lidas; ficou nulo no JSON.**
- **Área de tabuleiro:** largura útil = 6,45 + 2 × 2,17 = 10,79 m; área = 380,02 × 10,79 = **4.100,42 m²**. Alternativa com largura total: 380,02 × 14,5 = 5.510,29 m².
- **Custo oficial:** Acordo de Execução (Megvalósítási megállapodás), 3ª alteração, assinado em 18/01/2021, depois do resultado da licitação: "teljes költségigénye tervezetten bruttó 26.751.161.000,- Ft", ou seja, **custo total previsto de HUF 26.751.161.000, bruto (com IVA de 27%)**, "que inclui todos os custos necessários". Tabela do anexo (valores em milhões de forints): obra HUF 20.593,332 mi líquidos; total líquido HUF 21.063,907 mi; IVA HUF 5.687,254 mi. Cronograma anual bruto: 2019: 22,530; 2020: 0,370; 2021: 7.852,568; 2022: 9.280,355; 2023: 9.556,108; 2024: 39,230. Fonte (PDF escaneado, lido página a página): https://bkk.hu/downloads/5957/
- **Ressalva:** é o **orçamento aprovado**, não o custo final auditado. Usei o valor bruto porque contratos públicos brasileiros também embutem tributos no preço.

### 1.2 Lions' Gate Bridge, Vancouver (Canadá), troca da estrutura suspensa 2000 a 2001

- **O que é:** ponte pênsil de cabos de 1938, vão central de 472 m.
- **O que foi feito:** substituição de **toda a estrutura suspensa** (tabuleiro, passeios, treliças de rigidez e pendurais) por um tabuleiro ortotrópico 35% mais largo, em fechamentos noturnos, com a ponte aberta de dia; reforço sísmico. Torres, cabos principais e ancoragens foram mantidos.
- **Datas:** contrato em abril de 1999; troca de setembro de 2000 a setembro de 2001; pavimentação final no verão de 2002.
- **Dimensões:** ponte pênsil de 847 m (Figura 1 do artigo); nova seção de 16,2 m (três faixas de 3,6 m e dois passeios de 2,7 m, Figura 3). Área = 847 × 16,2 = **13.721,4 m²**.
- **Custo:** "The successful Contractor ... was selected in April 1999 to execute the $86.5 million contract. The cost of the suspension bridge portion of the project was approximately **$66 million**." Os CAD 86,5 milhões incluem a via elevada no Stanley Park e acessos; usei só os **CAD 66 milhões** da ponte pênsil. É custo de construção: não inclui projeto nem supervisão.
- **Tipo de fonte:** **fonte de engenharia**, não documento do governo: artigo técnico de D. Matson (Buckland & Taylor, engenheiro do proprietário durante a obra), conferência da Transportation Association of Canada: https://www.tac-atc.ca/wp-content/uploads/Matson.pdf

### 1.3 Ponte Pênsil Alves de Lima, Chavantes (SP), restauração entregue em 2023

- **O que é:** ponte pênsil de 1920 sobre o Rio Paranapanema, tombada pelo Condephaat; 164 m de extensão, 4 m de largura, vão de 80 m.
- **O que foi feito:** "reparos com substituição de componentes de madeira no guarda-corpo e no tabuleiro"; 95 m³ de madeira e 21 t de aço. **Escopo leve.**
- **Custo oficial:** **R$ 5,9 milhões**, entregue em 20/10/2023. Fonte: DER-SP, nota de 23/10/2023 (página do DER carrega por script; lida na cópia do Internet Archive): http://web.archive.org/web/20260413175100/http://www.der.sp.gov.br/WebSite/Comunicacao/SalaImprensa.aspx?idNoticia=1659
- **Área:** 164 × 4 = **656 m²**.
- **Ressalva:** a nota não diz quando a obra começou; usei 2023, ano da entrega. Entrou na tabela por ser a única restauração de ponte pênsil brasileira com custo oficial e dimensões completas encontrada nesta coleta. A Ponte Pênsil de São Vicente (DER-SP, R$ 5,2 milhões, 2022 a 2023) ficou de fora porque a nota oficial não traz a largura.

### 1.4 Cầu Thuận Phước, Da Nang (Vietnã), ponte pênsil nova, 2003 a 2009 (referência "construir")

- **O que é:** ponte pênsil nova. Trecho pênsil de 655 m (125 + 405 + 125 m), viga caixão de aço e dois cabos principais de 360 mm; viadutos de acesso de concreto protendido de 600 m de cada lado; comprimento total 1.856 m; 18 m de largura, 4 faixas, 2 passeios e 2 faixas para bicicleta; inaugurada em 19/07/2009. Fonte oficial (portal da cidade de Da Nang, 03/11/2014): https://danang.gov.vn/vi/web/dng/w/cau-thuan-phuoc-dai-lua-noi-doi-bo-song-han-i
- **Área:** 1.856 × 18 = **33.408 m²**. Só o trecho pênsil: 655 × 18 = 11.790 m².
- **Custo:** "tổng vốn đầu tư gần 1.000 tỷ đồng" (investimento total de **quase 1 trilhão de dong**). **FONTE SECUNDÁRIA (imprensa), valor aproximado:** jornal Sài Gòn Giải Phóng, 19/07/2009: https://www.sggp.org.vn/thanh-pho-da-nang-khanh-thanh-cau-thuan-phuoc-khoi-cong-xay-dung-cau-rong-post183851.html . O jornal Tuổi Trẻ (09/06/2008) registra o início em 17/01/2003 com orçamento de pouco mais de 587 bilhões de dong, ajustado quatro vezes: https://tuoitre.vn/cau-thuan-phuoc-bon-lan-nang-von-262119.htm . Nenhum documento oficial com o custo final foi encontrado.
- **Por que esta e não outra:** foi a única ponte pênsil nova com vão entre 250 e 450 m, concluída nas últimas décadas, com dimensões oficiais e custo publicado que esta coleta encontrou. As pontes pênseis norueguesas recentes que apareceram nas buscas (Hardangerbrua, Hålogalandsbrua, Dalsfjordbrua) têm vão acima de 450 m, e a Sandsfjordbrua (Noruega, 2015, 290 m) não é pênsil; as da Índia (Dobra-Chanti) e da Noruega de 1997 (Lysefjordbrua) só tinham custo em fontes sem origem clara.

### 1.5 Candidatos verificados e descartados

| Candidato | Por que ficou de fora |
|---|---|
| Clifton Suspension Bridge (Reino Unido) | Não verificado nesta coleta (limite de buscas); nenhuma obra de restauração com custo publicado apareceu nas buscas feitas. Candidato a verificar. |
| Hammersmith Bridge (Reino Unido) | Não verificado nesta coleta (limite de buscas). Até onde se sabe, a restauração completa não foi executada, então não haveria custo realizado; candidato a verificar. |
| Menai Suspension Bridge (País de Gales) | Obras ainda em andamento; a imprensa técnica (New Civil Engineer, 27/01/2026: https://www.newcivilengineer.com/latest/work-on-menai-suspension-bridge-to-continue-to-2027-due-to-critical-crossbeam-issue-27-01-2026/ ) fala em conclusão em 2027. Sem custo final; não verificado em fonte oficial. |
| Brooklyn Bridge (EUA) | O NYC DOT publica valores por contrato (por exemplo, Contrato 6, 2010 a 2017, US$ 650 milhões, para acessos e pintura de toda a ponte: https://www.nyc.gov/html/dot/html/infrastructure/brooklyn-bridge.shtml ), mas a reconstrução é um programa de contratos de 1980 a 2023 sem total nem distribuição anual publicados; somar pedaços não daria um número comparável. |
| Angus L. Macdonald Bridge, "Big Lift" (Halifax, Canadá, 2015 a 2019) | Escopo muito parecido com o de Vancouver, mas o custo final não aparece nos relatórios anuais da Halifax Harbour Bridges (https://halifaxharbourbridges.ca/managing-the-bridges/publications/ ); a nota oficial de 2014 falava em construção "na faixa de CAD 150 milhões" (estimativa), e a largura do tabuleiro publicada é inconsistente (11,5 m e 34,8 pés). |
| Pont de Tancarville (França, troca de cabos 1996 a 1999) | Só troca da suspensão, sem troca de tabuleiro (página oficial da CCI: https://www.pontsnormandietancarville.fr/lhistoire/pont-de-tancarville/les-evenements-majeurs/ , que descreve a obra sem valor); o custo de 240 milhões de francos só apareceu em fonte secundária. |

---

## 2. Método de normalização para R$ de dezembro de 2024

### 2.1 Fórmulas

Para um valor gasto em moeda local (LCU) no ano *a*:

- **(i) Câmbio de mercado:** `R$ dez/2024 = valor_LCU × (R$ por US$ no ano a ÷ LCU por US$ no ano a) × (IPCA dez/2024 ÷ média do IPCA no ano a)`
- **(ii) PPP:** `R$ dez/2024 = valor_LCU × (fator PPP do Brasil no ano a ÷ fator PPP do país no ano a) × (IPCA dez/2024 ÷ média do IPCA no ano a)`

Uso a média anual do IPCA porque o câmbio e o fator PPP também são médias do ano. Para valores já em reais, os dois métodos se reduzem à correção pelo IPCA.

### 2.2 Fontes dos fatores

- **IPCA:** IBGE, SIDRA, tabela 1737, variável 2266, número-índice (dez/1993 = 100): https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all?formato=json . Dezembro de 2024 = **7.100,50**.
- **Câmbio:** Banco Mundial, WDI, indicador PA.NUS.FCRF, "Official exchange rate (LCU per US$, period average)": https://api.worldbank.org/v2/country/BRA;HUN;CAN;VNM/indicator/PA.NUS.FCRF?format=json&per_page=1000&date=1995:2025 (última atualização da base: 2026-07-13).
- **PPP:** Banco Mundial, WDI/ICP, indicador PA.NUS.PPP, "PPP conversion factor, GDP (LCU per international $)": https://api.worldbank.org/v2/country/BRA;HUN;CAN;VNM/indicator/PA.NUS.PPP?format=json&per_page=1000&date=1995:2025 (última atualização: 2026-07-13).

### 2.3 Fatores usados

| Ano | Média do IPCA | Fator IPCA até dez/2024 | R$/US$ | LCU/US$ | PPP Brasil (R$/$ int.) | PPP do país (LCU/$ int.) |
|---|---|---|---|---|---|---|
| 2001 (Canadá) | 1.748,0133 | 4,062040 | 2,349632 | CAD 1,548840 | 0,802171 | CAD 1,220053 |
| 2006 (Vietnã) | 2.581,0342 | 2,751029 | 2,175327 | VND 15.994,25 | 1,098564 | VND 3.871,272 |
| 2019 (Hungria) | 5.213,6133 | 1,361915 | 3,944471 | HUF 290,66 | 2,216445 | HUF 138,797 |
| 2020 (Hungria) | 5.381,0625 | 1,319535 | 5,155179 | HUF 307,997 | 2,264911 | HUF 141,838 |
| 2021 (Hungria) | 5.827,7800 | 1,218388 | 5,394401 | HUF 303,141 | 2,379274 | HUF 148,351 |
| 2022 (Hungria) | 6.368,6042 | 1,114922 | 5,163970 | HUF 372,596 | 2,411656 | HUF 155,230 |
| 2023 (Hungria, Brasil) | 6.661,1500 | 1,065957 | 4,994380 | HUF 353,088 | 2,445593 | HUF 169,087 |
| 2024 (Hungria) | 6.952,0733 | 1,021350 | 5,388935 | HUF 365,691 | 2,483710 | HUF 175,578 |

(valores completos, com todas as casas, no bloco `method` do JSON)

### 2.4 Ano de gasto usado em cada obra, e por quê

| Obra | Ano(s) usado(s) | Por quê |
|---|---|---|
| Széchenyi Lánchíd | Cada ano de 2019 a 2024, com a parcela do cronograma oficial | O acordo oficial traz o gasto previsto ano a ano; cada parcela vai pelos fatores do seu ano. |
| Lions' Gate | 2001 | A troca ocorreu de set/2000 a set/2001 (ponto médio em 2001); não há cronograma anual publicado. |
| Alves de Lima | 2023 | Ano da entrega; início não publicado. Suposição sinalizada. |
| Thuận Phước | 2006 | Ponto médio entre o início (jan/2003) e a inauguração (jul/2009); não há cronograma anual publicado. |
| Hercílio Luz | Mês de assinatura de cada contrato | O CSV oficial traz a data de cada contrato; uso o índice mensal do IPCA do mês da assinatura. |

### 2.5 Dois exemplos de conta, para conferência

- **Budapeste, parcela de 2022:** 9.280.355.000 × (5,163970 ÷ 372,595833) × (7.100,50 ÷ 6.368,6042) = **R$ 143.401.933** (câmbio); 9.280.355.000 × (2,411656 ÷ 155,230128) × 1,114922 = **R$ 160.749.092** (PPP). Somadas as seis parcelas: R$ 458.755.603 (câmbio) e R$ 462.589.174 (PPP).
- **Vancouver:** 66.000.000 × (2,349632 ÷ 1,548840) × 4,062040 = **R$ 406.706.747** (câmbio); 66.000.000 × (0,802171 ÷ 1,220053) × 4,062040 = **R$ 176.269.102** (PPP).

### 2.6 Limites do método

- O fator PPP do Banco Mundial mede o nível de preços do **PIB inteiro**, não o da construção civil; o ICP tem PPPs de construção, mas não na base aberta usada aqui. Em países de mão de obra barata (Vietnã), o PPP do PIB tende a encarecer a obra convertida.
- Os dois métodos divergem muito em 2001 e 2006 (Vancouver: R$ 406,7 mi contra R$ 176,3 mi) porque o real estava muito desvalorizado em relação à sua paridade naqueles anos e depois o IPCA acumulado é aplicado sobre essa base. Nenhum dos dois é "o certo"; por isso os dois aparecem.
- O Banco Mundial revisa séries; os valores usados estão gravados no JSON com a data de atualização.

---

## 3. Ponte Hercílio Luz pelo mesmo método

### 3.1 Os 13 contratos, por data de assinatura

Fonte: Portal de Dados Abertos de SC, conjunto "Contratos" (SIGEF): https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/ff7c3cac-3e38-4801-9fd8-e4ccb69ca31d/download/contratos.csv . Filtro: "PONTE" e "HERCILIO" (sem acento) no objeto, resumo ou bem público; 26 contratos; destes, os 13 de restauração, supervisão e projetos classificados na verificação de 2026-09-25. O script confere que os 13 somam R$ 465.106.951,83 (original) e R$ 484.645.236,82 (atual).

| Assinatura | Contrato | Contratada | Situação | Valor original (R$) | Valor atual (R$) | Fator IPCA até dez/2024 | Valor atual em R$ dez/2024 | Limite inferior em R$ dez/2024 |
|---|---|---|---|---|---|---|---|---|
| 2006-08-25 | PJ-00170/2006 | Concremat | Rescindido | 3.924.487,59 | 6.106.108,74 | 2,751524 | 16.801.104 | 10.798.321 |
| 2006-08-25 | PJ-00170/2006/PROSUL | Prosul | Rescindido | 5.886.795,07 | 9.160.234,18 | 2,751524 | 25.204.603 | 16.197.657 |
| 2008-11-27 | PJ-00264/2008 | Consórcio Florianópolis Monumento | Rescindido | 154.879.651,29 | 63.008.872,09 | 2,461366 | 155.087.908 | 155.087.908 |
| 2014-11-14 | PJ-00204/2014 | RMG Engenharia | Concluído | 1.951.820,02 | 1.951.820,02 | 1,762593 | 3.440.264 | 3.440.264 |
| 2015-02-25 | PJ-00012/2015 | EMPA | Concluído | 10.357.290,64 | 12.941.168,93 | 1,706711 | 22.086.841 | 17.676.907 |
| 2015-10-02 | PJ-00143/2015 | EMPA | Concluído | 11.400.601,42 | 11.400.601,42 | 1,611571 | 18.372.875 | 18.372.875 |
| 2016-01-04 | PJ-00001/2016/FARES | Fares & Associados | Concluído | 137.482,95 | 137.482,95 | 1,560471 | 214.538 | 214.538 |
| 2016-03-10 | PJ-00056/2016 | Teixeira Duarte | Concluído | 262.925.435,21 | 363.824.397,74 | 1,539931 | 560.264.575 | 404.887.106 |
| 2016-05-18 | PJ-00093/2016 | RMG Engenharia | Concluído | 8.582.938,87 | 11.110.051,81 | 1,518749 | 16.873.378 | 13.035.328 |
| 2019-02-20 | PJ-00009/2019 | Teixeira Duarte | Concluído | 3.156.151,79 | 3.156.151,79 | 1,381708 | 4.360.880 | 4.360.880 |
| 2019-07-04 | CT-00006/2019 | RMG Engenharia | Concluído | 1.773.434,13 | 1.717.146,84 | 1,359161 | 2.333.878 | 2.333.878 |
| 2019-07-08 | PJ-00060/2019 | Geoarqueologia | Andamento | 95.862,85 | 96.200,31 | 1,359161 | 130.752 | 130.293 |
| 2019-09-25 | CT-00026/2019 | SDF Engenharia | Concluído | 35.000,00 | 35.000,00 | 1,358209 | 47.537 | 47.537 |
| **Total** | **13** | | | **465.106.951,83** | **484.645.236,82** | | **825.219.135** | **646.583.494** |

Fator IPCA = índice de dez/2024 (7.100,50) ÷ índice do mês da assinatura. Por ano de assinatura (valor atual corrigido): 2006, R$ 42,0 mi; 2008, R$ 155,1 mi; 2014, R$ 3,4 mi; 2015, R$ 40,5 mi; 2016, R$ 577,4 mi; 2019, R$ 6,9 mi.

### 3.2 Área de tabuleiro

- Comprimento: **821 m** (Governo de SC, página oficial da reabertura: http://web.archive.org/web/20240807222022/https://www.sc.gov.br/vivaaponte/caracteristicas-da-ponte-hercilio-luz/ ; partes: viaduto continental 222,504 m, viaduto insular 259,080 m, vão central 339,471 m, somando 821,055 m, segundo o GRANTE/UFSC: https://grante.ufsc.br/graduacao_informacoes/historico/recuperacao-da-ponte-hercilio-luz/ ).
- Largura: **pista de 9,2 m e dois passeios de 2,5 m**, total útil **14,2 m**. Fonte: ficha da obra da contratada (Teixeira Duarte), que é **fonte de engenharia**, não do governo: https://www.teixeiraduarteconstrucao.com.br/projetos/reabilitacao-e-restauro-da-ponte-hercilio-luz/ . Nenhuma fonte oficial com a largura foi encontrada; a largura total fora a fora (incluindo as treliças) também não.
- Área = 821 × 14,2 = **11.658,2 m²**.

### 3.3 Custo por m²

- **Central (valor atual corrigido):** R$ 825.219.135 ÷ 11.658,2 = **R$ 70.784 por m²** (igual nos dois métodos, porque os valores já estão em reais).
- **Limite inferior:** para cada contrato, o menor entre valor original e valor atual, corrigido desde a assinatura: R$ 646.583.494 ÷ 11.658,2 = **R$ 55.462 por m²**. Motivo: o valor atual inclui aditivos de reajuste, que já são correção monetária; corrigi-lo de novo desde a assinatura conta parte da inflação duas vezes. Como o CSV não separa aditivo de reajuste de aditivo de acréscimo de serviço, o número real fica entre R$ 55,5 mil e R$ 70,8 mil por m².

### 3.4 O que NÃO está nesse número

- **Primeira etapa (viadutos de acesso), 2006:** a linha do tempo oficial do Governo de SC diz "contratada por aproximadamente R$ 21 milhões", início em 17/02/2006 (http://web.archive.org/web/20240807221921/https://www.sc.gov.br/vivaaponte/linha-do-tempo/ ). Esse contrato **não aparece no CSV do SIGEF**, que praticamente começa em 2006. Corrigido de fev/2006 a dez/2024 (fator 2,772745), dá cerca de **R$ 58,2 milhões**. Com ele, o custo por m² sobe para cerca de **R$ 75,8 mil** (central) e **R$ 60,5 mil** (limite inferior). Não somei na tabela principal porque o valor é aproximado.
- **1982 a 2005:** nada desse período está no registro de contratos.
- **Depois da reabertura:** iluminação cênica, manutenção contínua e entorno (8 contratos) ficam fora, como na verificação de 2026-09-25.
- **Valor pago:** são valores de contrato, não pagamentos; os dados abertos de pagamento de SC não cobrem o período da obra.

### 3.5 Escopo da restauração (para comparar com os outros)

Segundo a ficha da contratada e o artigo técnico da UFMG apresentado no Construmetal 2016 (https://www.abcem.org.br/construmetal/downloads/apresentacao/42_DESAFIOS-DA-REABILITACAO-DE-ESTRUTURAS-METALICAS-ANTIGAS-PONTE-HERCILIO-LUZ.pdf ): substituição das barras de olhal (723 t), das selas no topo das torres, das rótulas de apoio e dos pendurais; reforço de todas as fundações; estrutura provisória de sustentação sob o vão central (3.400 t) com transferência de carga por macacos; substituição de cerca de 2.000 t de estrutura metálica; novo tabuleiro de aço ortotrópico com passeios (2.000 t), no lugar do antigo de longarinas e madeira; substituição de rebites; pintura anticorrosiva de 70.000 m²; 8.000 m³ de concreto armado. Mais supervisão, projetos complementares e revisão de orçamento (contratos do quadro 3.1).

---

## 4. Tabela comparativa e leitura

### 4.1 Tabela

| Obra | País, anos | Escopo em uma linha | Vão central (m) | Área (m²) | R$/m² dez/2024, câmbio | R$/m² dez/2024, PPP | Tipo de fonte do custo |
|---|---|---|---|---|---|---|---|
| **Ponte Hercílio Luz** | Brasil, 2006 a 2019 | Troca das barras de olhal, selas, rótulas, pendurais e tabuleiro; fundações; estrutura provisória | 339,5 | 11.658 | **70.784** (limite inferior 55.462) | **70.784** (55.462) | Oficial (contratos SIGEF) |
| Széchenyi Lánchíd | Hungria, 2021 a 2023 | Tabuleiro e passeios novos; correntes tratadas, não trocadas; restauro de pedra | não encontrado | 4.100 | **111.880** (83.254 pela largura total) | **112.815** (83.950 pela largura total) | Oficial (orçamento aprovado, não custo final) |
| Lions' Gate Bridge | Canadá, 2000 a 2001 | Troca de toda a estrutura suspensa; cabos e torres mantidos; só construção | 472 | 13.721 | **29.640** | **12.846** | Engenharia (engenheiro do proprietário) |
| Ponte Pênsil Alves de Lima | Brasil, 2023 | Troca de madeira do tabuleiro e do guarda-corpo | 80 | 656 | **9.587** | **9.587** | Oficial (DER-SP) |
| Cầu Thuận Phước (nova) | Vietnã, 2003 a 2009 | Ponte pênsil nova com 1,2 km de viadutos de concreto | 405 | 33.408 | **11.200** (31.735 só o trecho pênsil) | **23.368** (66.214 só o trecho pênsil) | Imprensa (aproximado) |

### 4.2 O que a tabela mostra

1. **Contra a obra mais parecida, a Hercílio Luz fica abaixo.** A Ponte das Correntes de Budapeste é do mesmo tipo (correntes de barras de olhal), é da mesma época de obra e o custo vem de documento oficial. Por m² de largura útil, Budapeste custou R$ 111,9 mil (câmbio) e R$ 112,8 mil (PPP), contra R$ 70,8 mil da Hercílio Luz. Pela largura total de Budapeste, R$ 83,3 mil e R$ 84,0 mil. Nos quatro cenários, Budapeste custou mais por m², mesmo sem ter trocado as correntes.
2. **Contra obras de escopo menor, a Hercílio Luz fica acima.** A troca do tabuleiro da Lions' Gate custou entre R$ 12,8 mil e R$ 29,6 mil por m²; a restauração leve da Alves de Lima, R$ 9,6 mil.
3. **Contra a ponte pênsil nova do Vietnã, a Hercílio Luz fica acima em quase todos os cenários.** A ponte inteira de Da Nang custou R$ 11,2 mil (câmbio) a R$ 23,4 mil (PPP) por m². Mesmo atribuindo todo o custo só ao trecho pênsil, dá R$ 31,7 mil a R$ 66,2 mil por m²; só nesse último caso (PPP, só trecho pênsil) o número passa o limite inferior da Hercílio Luz (R$ 55,5 mil), e continua abaixo do central (R$ 70,8 mil).

### 4.3 O que a tabela NÃO mostra

1. **Escopos diferentes.** Custo por m² de tabuleiro é uma régua simples e injusta: ele divide pelo tabuleiro um trabalho que, na Hercílio Luz, foi em grande parte embaixo (fundações, estrutura provisória de 3.400 t) e em cima (barras de olhal, selas, pendurais). Uma obra que só troca o tabuleiro (Vancouver) ou só a madeira (Chavantes) sempre sairá mais barata por essa régua.
2. **Custo de 13 anos, incluindo o contrato rescindido.** O número da Hercílio Luz inclui o contrato de 2008 rescindido (R$ 155,1 mi corrigidos) e duas supervisões de 2006 também rescindidas. Ele mede o que o Estado contratou até reabrir a ponte, não o custo de uma obra feita de uma vez.
3. **Valor de contrato, não valor pago.** O mesmo vale para Budapeste (orçamento aprovado) e Vancouver (valor aproximado de construção).
4. **País e época.** Mão de obra, aço, normas e câmbio de 2001, 2006 e 2021 não são os mesmos; a conversão pelo PIB (PPP) não mede preço de obra. A distância entre os dois métodos (Vancouver: R$ 12,8 mil contra R$ 29,6 mil) mostra quanto a resposta depende dessa escolha.
5. **Restaurar ou construir.** A comparação com uma ponte nova no Vietnã é só ordem de grandeza. Não existe, nesta coleta, ponte pênsil nova do mesmo porte, no Brasil, no mesmo período, com custo oficial. Além disso, a Hercílio Luz é tombada nas esferas municipal, estadual e federal (GRANTE/UFSC), então demolir e construir outra não era uma alternativa equivalente. O artigo técnico sobre a obra afirma que reabilitar custa, "para a maioria dos casos", entre 10% e 30% de uma obra nova semelhante; os dados reunidos aqui não permitem testar essa regra para a Hercílio Luz.
6. **Áreas com definições próximas, não idênticas.** Usei largura útil (pista mais passeios) em todas as obras onde a fonte a separa; na Hercílio Luz a largura total fora a fora não foi encontrada, e ela seria maior que 14,2 m (as treliças ficam entre a pista e os passeios), o que baixaria o custo por m².

---

## 5. Pendências

- Largura total da Hercílio Luz em fonte oficial (SIE/SC ou projeto de referência do DEINFRA).
- Custo final (não orçado) da Ponte das Correntes: a BKK publica as notas fiscais e medições do contrato principal numa pasta do Google Drive linkada em https://bkk.hu/fejlesztesek/kiemelt-fejlesztesek/archivum/a-lanchid-felujitasa/dokumentumok-kozbeszerzes-kozerdeku-adatok/ ; não foi somada nesta coleta.
- Valor exato e contratada da primeira etapa de 2006 (viadutos de acesso) da Hercílio Luz.
- Custo oficial final da ponte de Da Nang (hoje só em imprensa).
- Custo final do "Big Lift" de Halifax, que seria o comparável de escopo mais próximo da troca de tabuleiro.

---

## 6. Como reproduzir

```bash
SCRIPTS=~/Documents/Brasil-Imposto/data/scripts/bridges
mkdir -p /tmp/bridges && cd /tmp/bridges
bash $SCRIPTS/download.sh      # IPCA (SIDRA), câmbio e PPP (Banco Mundial), contratos de SC (~73 MB)
python3 $SCRIPTS/build.py      # grava data/bridge-comparables.json e imprime as tabelas
```

O `build.py` para com erro se o filtro não devolver 26 contratos ou se os 13 de restauração não somarem exatamente R$ 465.106.951,83 (original) e R$ 484.645.236,82 (atual). Os dados de custo e dimensão das obras estrangeiras estão escritos no próprio script, cada um com a URL da fonte.

---

## 7. Diário de transparência

- **BKK (Budapeste):** o acordo com o orçamento (https://bkk.hu/downloads/5957/) e o contrato de obra (https://bkk.hu/downloads/6038/) são PDFs escaneados, sem texto; as páginas do acordo foram lidas como imagem. O valor líquido "HUF 18,8 bilhões" do contrato com a A-Híd, citado por buscadores, não foi confirmado em documento oficial e não foi usado.
- **DER-SP:** as notas do DER carregam por script e vêm vazias por download direto; lidas nas cópias do Internet Archive de 13/04/2026.
- **Governo de SC (vivaaponte):** o site respondeu erro 500; lido nas cópias do Internet Archive de 07/08/2024.
- **Portal de Da Nang:** o domínio www.danang.gov.vn recusou a conexão segura; a mesma página foi lida em danang.gov.vn e cttdt.danangportal.gov.vn.
- **Halifax Harbour Bridges:** relatórios anuais 2017-18 e 2018-19 e demonstrações financeiras 2018 e 2019 lidos; nenhum traz o custo final do Big Lift.
- **Wikipedia:** usada só para localizar fontes; nenhum número da tabela vem dela.
- **Pesquisas na web usadas:** 19 (limite combinado: cerca de 25). O resto foi leitura direta das fontes (curl e leitura de PDF).
- **Checagem de travessões:** o texto, o JSON e os scripts foram conferidos por contagem de caracteres (zero travessões), com uma linha de controle que contém os dois caracteres para provar que a checagem funciona.
