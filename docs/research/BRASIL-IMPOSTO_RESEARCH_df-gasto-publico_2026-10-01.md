# DF: servidores, gasto público e por que o mapa mostra o DF "enviando"

**Data da coleta:** 2026-10-01. **Scripts:** `pipelines/df/`. **Dados baixados e agregados:** `data/df/`.
**Regra seguida:** só fonte oficial, com link e ano. O que é conta feita aqui sobre dado oficial está marcado como cálculo; o que é estimativa fica numa seção separada. O que não deu para abrir está na lista "não consegui confirmar".

## 0. Contexto: de onde vem o "R$ 2.918 por pessoa por mês"

O número da Q30 é reproduzível com os arquivos do projeto (2024, R$ bi, população IBGE 2024 de 2.982.818):

| Parte | Valor 2024 | Arquivo |
|---|---:|---|
| Arrecadação federal registrada no DF (Receita) | 184,10 | `data/series/federal-by-uf-monthly.json` |
| menos transferências da União ao DF | 3,78 | idem |
| menos Bolsa Família | 1,51 | idem |
| menos INSS (BEPS, sem BPC) | 10,48 | idem |
| menos BPC | 1,24 | idem |
| menos Fundo Constitucional do DF (FCDF) | 23,61 | `data/series/federal-payroll-by-uf.json` (bloco `fcdf`) |
| menos folha federal localizada no DF (sem FCDF) | 39,04 | idem (`uf.DF.annual`) |
| **Saldo** | **104,45** | |

104,45 bi / 2.982.818 pessoas / 12 meses = **R$ 2.918 por pessoa por mês**. O saldo é positivo porque o lado "envia" (184,10) é maior que tudo o que o mapa consegue pôr no lado "voltou" (79,65). As seções 1 a 4 olham cada lado.

## 1. Servidores públicos por estado, nas três esferas

### 1.1 Fonte

- **Atlas do Estado Brasileiro (Ipea)**, série 91, "Total, proporção e evolução de vínculos públicos no Brasil, nas regiões e nos estados, por nível federativo e nível de escolaridade": https://www.ipea.gov.br/atlasestado/consulta/91 , arquivo https://www.ipea.gov.br/atlasestado/arquivos/downloads/9113-091arquivounico.xlsx (aba `Uf`). O título diz 1985 a 2023, mas a aba por UF vai **até 2021**: é o ano mais recente por UF no Atlas. A série 79 (densidade por UF) vai até 2019.
- Base do Atlas (página de metodologia, https://www.ipea.gov.br/atlasestado/quem/12/metodologia): RAIS, vínculos formais ativos, contados por CPF; "público" = CNPJ de natureza jurídica pública (administração direta, autarquias, fundações; empresas públicas e de economia mista ficam fora). **Inclui militares, policiais e bombeiros** a partir de 2011 (a RAIS passou a reportá-los). O vínculo fica na UF do estabelecimento que declara a RAIS, não necessariamente onde a pessoa trabalha.
- No DF não há municípios: o "estadual" do DF é o GDF, que também faz o papel de prefeitura. A União organiza e mantém o Judiciário e o Ministério Público do DF (CF, art. 21, XIII) e as polícias Civil, Penal e Militar e o Corpo de Bombeiros do DF, com o FCDF (art. 21, XIV): https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm . A contagem pequena de "judiciário estadual" no DF no Atlas (2.034 vínculos em 2021) indica que o TJDFT entra como federal; a metodologia do Atlas não diz isso com essas palavras. Não foi verificado em que esfera o Atlas conta as polícias e os bombeiros do DF, pagos pela União com o FCDF.
- População: estimativas do IBGE do mesmo ano (`data/series/population.json`; as de 2019 e 2021 ainda partem do Censo 2010).
- Script: `pipelines/df/atlas_vinculos_uf.py`; dado agregado: `data/df/atlas_vinculos_uf.json`.

### 1.2 Vínculos públicos por mil habitantes, 2021 (cálculo sobre o Atlas)

| # | UF | Total por mil hab | Federal | Estadual (no DF, GDF) | Municipal | Vínculos | dos quais federais |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | **DF** | **100,1** | **55,2** | 44,8 | 0,0 | 309.663 | 170.955 |
| 2 | RR | 94,1 | 10,9 | 45,2 | 38,0 | 61.395 | 7.101 |
| 3 | TO | 92,5 | 3,2 | 49,1 | 40,2 | 148.740 | 5.206 |
| 4 | AC | 74,7 | 3,9 | 41,8 | 29,1 | 67.778 | 3.526 |
| 5 | MS | 73,5 | 5,0 | 22,0 | 46,5 | 208.754 | 14.281 |
| 6 | MT | 72,9 | 2,7 | 34,1 | 36,1 | 259.989 | 9.670 |
| ... | | | | | | | |
| 21 | RJ | 47,2 | 9,3 | 10,3 | 27,6 | 824.177 | 162.156 |
| 26 | SP | 39,6 | 1,6 | 14,8 | 23,2 | 1.846.836 | 74.881 |
| 27 | SE | 37,5 | 3,1 | 7,3 | 27,1 | 87.720 | 7.211 |
| | **Brasil** | **50,8** | **4,0** | | | 10.829.630 | 857.923 |

A tabela completa (27 UFs, e 2019) sai do script. Em 2019 o quadro é o mesmo: DF 111,7 por mil (federal 66,9), RR 98,6, TO 85,6, Brasil 51,8.

Leitura:

- **O DF é o primeiro em vínculos públicos por habitante: 100,1 por mil em 2021, o dobro da média do país (50,8).** O que põe o DF em primeiro é a esfera federal: 55,2 vínculos federais por mil habitantes, contra 4,0 no país e 10,9 no segundo colocado (RR). O DF tem 19,9% de todos os vínculos federais do país (RJ, 18,9%).
- Dentro dos federais do DF em 2021: Executivo 102.463, Judiciário (inclui TJDFT) 40.230, Legislativo (Câmara, Senado, TCU) 28.262.
- **O governo local do DF não é o que mais emprega.** O GDF, que faz o papel de estado e de prefeitura, tem 44,8 vínculos por mil habitantes; somando estado e prefeituras, o DF fica em 20º de 27 em 2021 (TO 89,3, RR 83,2, AC 70,8). A diferença do DF é toda federal.

### 1.3 Servidores federais civis do Executivo, agosto de 2026 (o dado mais recente)

- Fonte: Ministério da Gestão e da Inovação (SEGRT), repositório aberto, "Servidores por município de exercício", agosto de 2026: https://repositorio.dados.gov.br/segrt/Serv_por_municipio/2026/Serv_por_mun_exerc_202608.csv (servidores civis ativos do SIAPE, pelo município da unidade de exercício; sem militares, sem Legislativo e Judiciário). Script: `pipelines/df/segrt_servidores_uf.py`.

| # | UF | Servidores ativos | Por mil hab (IBGE 2026) | % do total |
|---:|---|---:|---:|---:|
| 1 | **DF** | **59.994** | **19,9** | 12,7% |
| 2 | AP | 11.874 | 14,7 | 2,5% |
| 3 | RR | 8.919 | 11,7 | 1,9% |
| 4 | RO | 8.572 | 4,9 | 1,8% |
| 5 | RJ | 63.685 | 3,7 | 13,5% |
| ... | | | | |
| 27 | SP | 31.768 | 0,7 | 6,7% |
| | **Brasil** | 471.127 | 2,2 (1,95 sem o DF) | |

AP, RR e RO aparecem logo atrás por causa do pessoal dos ex-territórios, pago pela União. O Painel Estatístico de Pessoal (PEP) não foi usado: é um painel interativo sem arquivo; o repositório da SEGRT é o arquivo aberto do mesmo ministério.

**Resposta à pergunta 1:** sim. Com dado oficial, o DF é a UF com mais vínculos públicos por habitante (Atlas/RAIS, 2021) e com mais servidores federais civis por habitante (SIAPE, agosto de 2026), e a distância vem da esfera federal, não do GDF.

## 2. Gasto federal localizado no DF

### 2.1 Fonte e definição

- Portal da Transparência (CGU), Execução da Despesa, 12 arquivos mensais de 2024: https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/202401 (até 202412), baixados de novo em 2026-10-01, um a cada 90 s. Script: `pipelines/df/agg_desp_uf.py` (soma por UF, localizador, grupo, modalidade, órgão superior e função; apaga cada ZIP) e `pipelines/df/q2_gasto_por_uf.py`; saída `data/df/q2_gasto_por_uf_2024.json`.
- Definição, a mesma do relatório de 2024 (`BRASIL-IMPOSTO_RESEARCH_dados-por-uf_2026-09-25.md`, seção 3.3): valor pago + restos a pagar pagos, aplicação direta (modalidades 90 e 91), grupos pessoal (1), outras despesas correntes (3, custeio e benefícios), investimentos (4) e inversões (5); juros e amortização fora. A UF é a do **localizador orçamentário** que o SIAFI registra, não a de quem recebe.
- O arquivo do Portal é do **Poder Executivo** (`BRASIL-IMPOSTO_RESEARCH_folha-federal-por-uf_2026-10-01.md`, seção 2). Legislativo, Judiciário e MPU estão na seção 4.2 (folha) e não aqui.
- Conferência: o total (R$ 1.916,04 bi) e a parte com UF (R$ 192,16 bi) são iguais, até o centavo de bilhão, aos do relatório de 2024. 2025 também foi baixado (seção 2.4).

### 2.2 Quanto fica sem UF (2024)

| | R$ bi | % do gasto direto primário |
|---|---:|---:|
| Gasto direto primário do Executivo | 1.916,04 | 100% |
| Com UF no localizador | 192,16 | 10,0% |
| Sem UF | 1.723,88 | 90,0% |
| dos quais localizador "Nacional" (código 0001) | 1.675,52 | 87,4% |
| dos quais demais localizadores sem UF (regionais, como "Na Região Nordeste", e outros) | 42,27 | 2,2% |
| dos quais exterior (0002) | 6,10 | 0,3% |

Sem UF, por função: Previdência social R$ 990,65 bi, Assistência social 279,10, Trabalho 110,78, Defesa nacional 92,23, Encargos especiais 52,71, Saúde 44,26, Administração 28,35, Educação 26,29, Agricultura 24,46, Transporte 15,67. O mapa já põe por UF, por outras fontes, a maior parte da previdência (INSS, AEPS e BEPS), o BPC e o Bolsa Família; tirando Previdência e Assistência, ainda ficam **R$ 454,14 bi (23,7% do gasto direto) sem UF**, aí incluídos a folha militar, o seguro-desemprego e o abono (Trabalho) e as compras centralizadas da Saúde.

### 2.3 Gasto direto do Executivo com UF, por pessoa (2024)

| # | UF | Total (R$ bi) | R$ por pessoa | Pessoal (R$ por pessoa) | Custeio e benefícios | Investimento |
|---:|---|---:|---:|---:|---:|---:|
| 1 | **DF** | **46,50** | **15.590** | 13.407 | 2.076 | 107 |
| 2 | RS | 55,10 | 4.906 | 894 | 770 | 94 |
| 3 | RJ | 17,74 | 1.030 | 771 | 230 | 19 |
| 4 | RN | 3,54 | 1.026 | 794 | 182 | 49 |
| 5 | PB | 4,18 | 1.008 | 816 | 127 | 66 |
| ... | | | | | | |
| 17 | SC | 3,99 | 495 | 358 | 82 | 55 |
| 27 | SP | 4,82 | 105 | 83 | 20 | 3 |
| | 26 UFs sem o DF | | 695 (526 sem as inversões do RS) | 371 | 124 | 30 |

- O RS aparece em 2º por R$ 35,36 bi de inversões financeiras de 2024 (o ano das enchentes); sem elas, o resto do país fica em R$ 526 por pessoa.
- **No DF, R$ 23,61 bi dos R$ 46,50 bi são o FCDF** (unidade orçamentária 73901, registrada com localizador DF; `fcdf.annual.total["2024"]` em `data/series/federal-payroll-by-uf.json`). Sem o FCDF, o gasto direto do Executivo localizado no DF é R$ 22,90 bi, **R$ 7.676 por pessoa, cerca de 11 vezes o resto do país** (695); com o FCDF, R$ 15.590, cerca de 22 vezes.
- No DF, por função: Encargos especiais R$ 20,83 bi, Previdência social 15,36 (aposentadorias e pensões de servidores com localizador DF), Saúde 5,66, Educação 2,91. Por órgão superior: Fazenda 22,89, Saúde 14,71, Educação 3,90, Gestão e Inovação 2,85.
- O DF fica com 24,2% de todo o gasto direto do Executivo que tem UF, com 1,40% da população.

### 2.4 2025 (o ano completo mais recente), com um aviso

Mesmos scripts, 12 arquivos de 2025 (`data/df/q2_gasto_por_uf_2025.json`; população IBGE 2025). **O arquivo de junho de 2025 do Portal está fora do padrão:** soma R$ 385,0 bi de gasto direto primário (os outros meses ficam entre R$ 145,5 bi e 212,6 bi) e R$ 54,4 bi de pessoal (outros meses: R$ 24,4 bi a 40,5 bi). É a mesma anomalia já registrada na pesquisa da folha (o Portal traz R$ 47,67 bi de pessoal do Executivo em 2025-06, contra R$ 23,99 bi na base do Tesouro). Por isso há duas colunas:

| 2025 | Ano inteiro (com junho) | 11 meses (sem junho) |
|---|---:|---:|
| Gasto direto primário do Executivo (R$ bi) | 2.286,66 | 1.901,69 |
| Com UF (R$ bi e %) | 178,25 (7,8%) | 152,40 (8,0%) |
| DF, gasto direto localizado (R$ bi) | 51,21 | 43,64 |
| DF, R$ por pessoa | 17.087 | 14.561 |
| FCDF no período (R$ bi, base do Tesouro) | 24,92 | 22,89 |
| DF sem o FCDF, R$ por pessoa | 8.771 | 6.922 |
| 26 UFs sem o DF, R$ por pessoa | 604 | 517 |
| Parte do DF no gasto com UF | 28,7% | 28,6% |

Tirando Previdência e Assistência, ficam sem UF R$ 644,42 bi em 2025 (28,2%), com "Encargos especiais" sem UF saltando de R$ 52,71 bi (2024) para R$ 140,63 bi (2025); a causa não foi investigada. O quadro do DF não muda: maior gasto federal localizado por pessoa, de 11 a 14,5 vezes o resto do país sem o FCDF, e menos de 10% do gasto direto com UF.

**Resposta à pergunta 2:** sim, o DF é, de longe, a UF com o maior gasto federal direto localizado por pessoa (R$ 15.590 em 2024 com o FCDF; R$ 7.676 sem ele; R$ 695 no resto do país; em 2025, sem o mês anômalo, R$ 14.561, R$ 6.922 e R$ 517). Mas 90% do gasto direto do Executivo não tem UF no próprio sistema da União, e nenhum arquivo aberto diz quanto desse "Nacional" é gasto no DF.

## 3. O lado "envia" do DF: imposto que o governo paga a si mesmo e sedes em Brasília

### 3.1 Fontes

- Receita Federal, **arrecadação por estado**, mensal, por tributo: https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv (baixado de novo em 2026-10-01). Script: `pipelines/df/rfb_df_breakdown.py`; saída `data/df/rfb_breakdown_2024.json`.
- Receita Federal, **arrecadação por natureza jurídica do contribuinte**, mensal, nacional (sem UF): https://www.gov.br/receitafederal/dados/arrecadacao-natureza.csv (listada em "Dados abertos > Receitadata > Arrecadação", https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/arrecadacao-1). Script: `pipelines/df/rfb_natureza.py`; saída `data/df/rfb_natureza_2024.json`. O total desse arquivo em 2024 (R$ 2.608,84 bi) é um pouco menor que o do arquivo por UF (R$ 2.651,34 bi); os dois têm recortes diferentes e não foram conciliados.
- Lei nº 9.779/1999, art. 15: https://www.planalto.gov.br/ccivil_03/leis/l9779.htm
- Regulamento do Imposto de Renda, Decreto nº 9.580/2018, arts. 202, 932 e 933: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/decreto/d9580.htm

### 3.2 A regra: onde a Receita registra o imposto retido

- **Lei 9.779/1999, art. 15:** "Serão efetuados, de forma centralizada, pelo estabelecimento matriz da pessoa jurídica: I, o recolhimento do imposto de renda retido na fonte sobre quaisquer rendimentos; [...] III, a apuração e o pagamento das contribuições para o [...] PIS/PASEP e [...] COFINS".
- **RIR/2018, art. 932:** "Será efetuado, de forma centralizada, pelo estabelecimento matriz da pessoa jurídica, o recolhimento do imposto sobre a renda retido na fonte sobre quaisquer rendimentos". **Art. 202, II:** o domicílio fiscal da pessoa jurídica, "em relação às obrigações em que incorra como fonte pagadora", é "o lugar do estabelecimento matriz da pessoa jurídica que pagar".
- **RIR/2018, art. 933 (CF, art. 157, I e 158, I):** pertence aos estados, ao DF e aos municípios o imposto de renda retido sobre os salários que eles pagam aos seus servidores.

Consequência direta da regra: o IR retido no salário de um empregado que trabalha no Pará, pago por uma empresa ou órgão cuja matriz está em Brasília, é recolhido pela matriz e fica no domicílio fiscal da matriz. **Não encontrei a nota metodológica da Receita que diga, com essas palavras, que a arrecadação por estado segue esse domicílio** (ver "não consegui confirmar"); a página do conjunto não traz nota nem dicionário.

### 3.3 O que o próprio arquivo da Receita mostra (2024)

Composição da arrecadação registrada no DF, colunas selecionadas (R$ bi; "por pessoa" com a população IBGE 2024; "resto do país" = Brasil sem o DF):

| Coluna do arquivo da Receita | DF | Brasil | DF no Brasil | DF, R$ por pessoa | Resto do país, R$ por pessoa |
|---|---:|---:|---:|---:|---:|
| IRRF, rendimentos do trabalho | 48,31 | 208,84 | 23,1% | 16.196 | 766 |
| CPSSS, contribuição do servidor público federal ao seu regime | 18,44 | 41,87 | 44,0% | 6.181 | 112 |
| Receita previdenciária (RGPS) | 31,83 | 671,36 | 4,7% | 10.672 | 3.051 |
| Outras receitas administradas | 12,28 | 41,61 | 29,5% | 4.118 | 140 |
| IRRF, rendimentos do capital | 9,22 | 143,65 | 6,4% | 3.092 | 641 |
| IOF | 8,92 | 67,41 | 13,2% | 2.992 | 279 |
| COFINS, financeiras | 6,91 | 29,65 | 23,3% | 2.318 | 108 |
| PIS/PASEP, financeiras | 1,15 | 4,88 | 23,6% | 386 | 18 |
| IRPJ, entidades financeiras | 3,68 | 34,19 | 10,8% | 1.233 | 146 |
| CSLL, financeiras | 3,13 | 24,99 | 12,5% | 1.049 | 104 |
| PIS/PASEP, demais | 7,19 | 108,48 | 6,6% | 2.411 | 483 |
| IRRF, outros rendimentos | 3,56 | 20,70 | 17,2% | 1.195 | 82 |
| IRPJ, demais empresas | 9,02 | 286,07 | 3,2% | 3.023 | 1.322 |
| COFINS, demais | 8,14 | 387,58 | 2,1% | 2.729 | 1.810 |
| **Total** | **184,10** | **2.651,34** | **6,9%** | **61.719** | **11.771** |

O DF tem 1,40% da população. O IPI (0,0% a 0,5% em cada coluna) e o imposto de importação (0,1%) ficam abaixo dessa proporção e a COFINS das empresas não financeiras fica perto dela (2,1%); o que está muito acima são o imposto retido na folha, a contribuição do servidor federal, as linhas do setor financeiro e o PIS/PASEP "demais" (6,6%; o arquivo só tem as colunas "financeiras" e "demais", então o PASEP pago por entes públicos, item 5 da seção 3.4, fica por exclusão em "demais").

### 3.4 Imposto que o governo paga a si mesmo

O arquivo por natureza jurídica (nacional) diz **quem pagou** cada tributo em 2024:

| Quem pagou (natureza jurídica, 2024, Brasil) | IRRF (todos os tipos) | CPSSS | Previdência (RGPS) | Total |
|---|---:|---:|---:|---:|
| Órgãos, autarquias, fundações e fundos federais de direito público (códigos 101, 104, 107, 110, 113, 116, 131) | 43,25 | 41,32 | 5,36 | 103,92 |
| Fundo público da administração indireta federal (128) | 7,61 | 0,00 | 0,20 | 7,81 |
| Estados, DF, municípios e seus órgãos, autarquias, fundações e fundos (códigos 102, 103, 105, 106, 108, 111, 112, 114, 115, 117, 118, 123, 124, 126, 127, 129, 130, 132, 133; consórcios públicos fora) | 0,33 | 0,00 | 74,88 | 94,95 |
| Empresas públicas (201, federais, estaduais e municipais juntas) | 16,67 | 0,37 | 17,47 | 63,41 |
| Sociedades de economia mista (203, idem) | 21,35 | 0,15 | 22,82 | 236,80 |
| Todos os contribuintes | 444,62 | 41,87 | 651,27 | 2.608,84 |

O que isso confirma, com dado oficial:

1. **O IR retido e a contribuição previdenciária dos servidores federais entram na arrecadação da Receita.** Em 2024, os órgãos federais de direito público recolheram R$ 43,25 bi de IRRF e R$ 41,32 bi de CPSSS (98,7% de toda a CPSSS do país). É dinheiro que a União desconta do salário que ela mesma paga e registra como arrecadação.
2. **A CPSSS registrada no DF (R$ 18,44 bi, 44,0% do país) é, por construção, desse tipo:** quase toda a CPSSS do país é paga por órgãos federais.
3. **O IRRF dos servidores estaduais e municipais não está na arrecadação da Receita:** estados, DF, municípios e seus órgãos aparecem com R$ 0,33 bi de IRRF em 2024 (contra R$ 74,88 bi de contribuição ao RGPS). Isso responde à **Q21** com fonte oficial: não há dupla contagem com a receita de IR dos estados.
4. **Quanto do IRRF do trabalho registrado no DF (R$ 48,31 bi) vem da folha federal: não há número oficial aberto.** O arquivo por UF não tem natureza jurídica e o arquivo por natureza jurídica não tem UF. O que dá para dizer: (a) a CPSSS do DF (R$ 18,44 bi) é federal; (b) o IRRF de todos os órgãos federais do país somou R$ 43,25 bi, menos do que o IRRF do trabalho registrado só no DF; logo, o IRRF do DF também inclui imposto retido por empresas (estatais e privadas) com matriz em Brasília.
5. **A União também paga PASEP:** os órgãos do Executivo federal (código 101) recolheram R$ 4,95 bi de PIS/PASEP em 2024 (o PASEP das pessoas jurídicas de direito público incide sobre as receitas, Lei 9.715/1998, art. 2º, III: "pelas pessoas jurídicas de direito público interno, com base no valor mensal das receitas", https://www.planalto.gov.br/ccivil_03/leis/l9715.htm). A UF desse recolhimento não está em nenhum arquivo aberto; no DF, a coluna "PIS/PASEP, demais" soma R$ 7,19 bi (6,6% do país).
6. **A contribuição patronal da União ao regime dos servidores (R$ 27,30 bi em 2024, modalidade 91 no SIAFI, ver `BRASIL-IMPOSTO_RESEARCH_folha-federal-por-uf_2026-10-01.md`) é intraorçamentária;** a CPSSS da Receita (R$ 41,87 bi) não bate com ela e não foi conciliada aqui.

### 3.5 Sedes de estatais em Brasília

| Empresa | Sede | Fonte |
|---|---|---|
| Correios (ECT) | "sede e foro na cidade de Brasília, Distrito Federal" | Decreto-Lei nº 509/1969, art. 1º, § 1º (incluído pela MP 532/2011): https://www.planalto.gov.br/ccivil_03/decreto-lei/del0509.htm |
| EBSERH (hospitais universitários federais em todo o país) | "sede e foro em Brasília, Distrito Federal" | Lei nº 12.550/2011, art. 1º, § 1º: https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12550.htm |
| Caixa Econômica Federal | "sede e foro em Brasília, Distrito Federal" no estatuto aprovado pelo Decreto nº 7.973/2013, art. 2º (decreto revogado em 2021; o estatuto atual não foi aberto) | https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/decreto/d7973.htm |
| Banco do Brasil | não confirmado (o estatuto no site do banco devolveu HTTP 403) | ver "não consegui confirmar" |

Com a regra do art. 15 da Lei 9.779/1999, o IR retido dos empregados dessas empresas em todo o país, e o PIS e a COFINS delas, são recolhidos pela matriz. O efeito aparece no arquivo: as linhas "financeiras" do DF (IRPJ, CSLL, COFINS, PIS) somam R$ 14,87 bi (cálculo: 3,68 + 3,13 + 6,91 + 1,15), de 10,8% a 23,6% do país em cada linha, e o IOF e o IRRF do capital, também muito acima do peso da população (13,2% e 6,4% do país), somam mais R$ 18,14 bi no DF. **O arquivo não diz quanto disso é de cada empresa**; os números por empresa estariam nas demonstrações financeiras de cada uma, que não foram abertas.

**Resposta à pergunta 3:** sim, o lado "envia" do DF contém imposto que a União paga a si mesma (a CPSSS de R$ 18,44 bi, com certeza; uma parte não quantificável dos R$ 48,31 bi de IRRF do trabalho) e imposto recolhido em Brasília por estatais e bancos com matriz no DF sobre atividade no país inteiro. A regra que faz isso é a centralização na matriz (Lei 9.779/1999, art. 15; RIR/2018, arts. 202 e 932). Nenhuma fonte aberta separa esses valores por UF.

## 4. Com os dados locais: orçamento do DF e folha federal por pessoa (2024)

Script: `pipelines/df/q4_local.py`; saída `data/df/q4_local_2024.json`. Nada foi baixado para esta seção.

### 4.1 Despesa própria do governo estadual por pessoa

Fonte: `data/series/state-budgets.json` (SICONFI, RREO Anexo 01, despesa liquidada exceto intraorçamentária, 2024, 6º bimestre); FCDF de `data/uf-balance-2024.json` (R$ 23,61 bi, Portal da Transparência, UO 73901); população IBGE 2024.

Um ajuste é necessário para comparar: alguns estados lançam a cota-parte dos municípios (ICMS, IPVA) como despesa, na subfunção "Transferências" de Encargos Especiais (SP: R$ 71,29 bi; AM: R$ 4,76 bi), e outros como dedução da receita (SC, RJ, MG: zero nessa subfunção). A coluna "sem Transferências" tira essa subfunção.

| # | UF | Despesa liquidada (R$ bi) | R$ por pessoa | Subfunção Transferências (R$ bi) | R$ por pessoa, sem Transferências |
|---:|---|---:|---:|---:|---:|
| 1 | AC | 10,84 | 12.305 | 0,62 | 11.597 |
| 2 | **DF (só GDF)** | **35,30** | **11.836** | 0,00 | **11.836** |
| 3 | AP | 9,30 | 11.583 | 0,00 | 11.580 |
| 4 | RR | 7,80 | 10.887 | 0,14 | 10.694 |
| 5 | TO | 15,61 | 9.896 | 0,07 | 9.850 |
| 6 | MT | 33,18 | 8.648 | 0,52 | 8.512 |
| 10 | SP | 335,69 | 7.302 | 71,29 | 5.751 |
| 14 | SC | 45,74 | 5.676 | 0,00 | 5.676 |
| 15 | RJ | 97,60 | 5.668 | 0,00 | 5.668 |
| 27 | MA | 27,62 | 3.940 | 0,00 | 3.940 |
| | Média dos 26 estados (sem DF) | | 5.880 | | 5.505 |

**DF com o FCDF:** GDF R$ 35,30 bi + FCDF R$ 23,61 bi = **R$ 58,91 bi, R$ 19.750 por pessoa** (cálculo: 58,91 bi / 2.982.818). Isso é 3,6 vezes a média dos 26 estados sem Transferências (R$ 5.505) e 1,7 vez o segundo colocado (AC, R$ 11.597).

**A comparação justa precisa de estado + prefeituras**, porque o GDF faz as duas coisas. Os únicos municípios com orçamento no projeto são os de SC (`data/series/sc-municipal-budgets.json`, 295 de 295 com 2024): SC estado R$ 45,74 bi + prefeituras R$ 50,43 bi = R$ 96,17 bi, **R$ 11.934 por pessoa**. SC lança a cota-parte dos municípios como dedução da receita (subfunção Transferências zero), então essa soma não conta a cota-parte duas vezes; transferências voluntárias do estado às prefeituras, se houver, ficam nas duas. Com essa régua: o GDF sozinho (R$ 11.836) gasta por pessoa o mesmo que SC estado + prefeituras; GDF + FCDF (R$ 19.750) gasta 1,65 vez mais.

### 4.2 Folha federal localizada por pessoa

Fonte: `data/series/federal-payroll-by-uf.json`, `uf.<UF>.annual.total_located["2024"]` (sem o FCDF; método e lacunas em `BRASIL-IMPOSTO_RESEARCH_folha-federal-por-uf_2026-10-01.md`).

| # | UF | Folha localizada 2024 (R$ bi) | R$ por pessoa por ano | R$ por pessoa por mês |
|---:|---|---:|---:|---:|
| 1 | **DF** | **39,04** | **13.089** | **1.091** |
| 2 | RS | 11,28 | 1.004 | 84 |
| 3 | PB | 3,59 | 867 | 72 |
| 4 | RJ | 14,76 | 857 | 71 |
| 5 | RN | 2,84 | 823 | 69 |
| ... | | | | |
| 15 | SC | 3,56 | 442 | 37 |
| 27 | SP | 9,21 | 200 | 17 |
| | Soma das 27 UFs | 132,16 | 622 | 52 |
| | 26 UFs sem o DF | 93,12 | 444 | 37 |

O DF recebe por pessoa 29,5 vezes a folha federal localizada do resto do país (13.089 / 444). Lembrete: é um piso. R$ 208,20 bi da folha de 2024 (militares, folhas centralizadas de ministérios, inativos pagos por unidades sem UF) não têm UF em nenhum arquivo aberto.

**Resposta à pergunta 4:** com os dados locais, o DF tem o maior gasto público por pessoa entre as UFs quando se soma o FCDF ao GDF (R$ 19.750 em 2024) e, de longe, a maior folha federal localizada por pessoa (R$ 13.089). Sem o FCDF, o GDF fica em 2º lugar (1º se a cota-parte de municípios for tirada da despesa de AC).

## 5. Por que o DF aparece "enviando" mais do que recebe

Os dois lados, com o que os dados oficiais mostram:

**Lado "envia" (R$ 184,10 bi em 2024) está inflado por registro, não por renda de quem mora no DF:**

- A lei manda recolher o IR retido, o PIS e a COFINS na **matriz** de quem paga (Lei 9.779/1999, art. 15; RIR/2018, arts. 202 e 932). Órgãos federais, Correios, EBSERH, Caixa e outras entidades com matriz em Brasília recolhem no DF o imposto de quem trabalha no país inteiro.
- Parte desse "envio" é a União pagando a si mesma: toda a CPSSS (R$ 18,44 bi no DF, 44% do país) e uma parte não separável dos R$ 48,31 bi de IRRF do trabalho (23,1% do país, com 1,40% da população).
- As linhas do setor financeiro (IRPJ, CSLL, COFINS e PIS das financeiras, R$ 14,87 bi) estão entre 10,8% e 23,6% do país no DF, e o IOF e o IRRF do capital (R$ 18,14 bi) em 13,2% e 6,4%; a Caixa tem sede em Brasília (seção 3.5).
- O próprio arquivo da Receita mostra que o IPI e o imposto de importação ficam no DF abaixo do peso da população, e a COFINS das empresas não financeiras perto dele (2,1% contra 1,40%): o excesso do DF não está nos tributos sobre produção e consumo.

**Lado "voltou" (R$ 79,65 bi em 2024) está incompleto, e incompleto justamente onde o DF mais recebe:**

- Do gasto direto primário do Executivo, 90,0% (2024) e 92,2% (2025) não têm UF no SIAFI (seção 2).
- Da folha federal de 2024, R$ 208,20 bi (61%) não têm UF em nenhum arquivo aberto: todos os militares (R$ 92,13 bi), R$ 98,44 bi do Executivo civil com localizador Nacional (Defesa, Gestão, Justiça, Previdência, Fazenda...) e os órgãos de atuação nacional dos outros Poderes. O DF já fica com 29,5% da folha que tem UF.

**Os fatos que respondem ao autor:**

- O DF é, sim, a UF com mais servidores públicos por habitante: 100,1 vínculos públicos por mil habitantes (o dobro da média, 50,8; Atlas/RAIS 2021) e 19,9 servidores federais civis do Executivo por mil habitantes (contra 1,95 no resto do país; SIAPE, agosto de 2026). A diferença vem toda da esfera federal; o GDF, que acumula estado e prefeitura, fica em 20º em vínculos por habitante.
- O DF tem o maior gasto público por pessoa quando se soma o que a União paga dentro do DF: GDF + FCDF = R$ 19.750 por pessoa em 2024, contra R$ 5.505 na média dos estados e R$ 11.934 em SC somando estado e prefeituras; folha federal localizada de R$ 13.089 por pessoa, contra R$ 444 no resto do país.
- Mesmo assim o mapa o mostra "enviando" porque o lado "envia" registra no DF imposto de fora do DF (e da própria União), e o lado "voltou" não consegue registrar no DF a parte da despesa federal que o sistema da União lança como "Nacional".

## 6. Contas de sensibilidade (não são decisões nem dado novo)

Contas aritméticas sobre os números oficiais acima, para mostrar o tamanho de cada efeito. Nenhuma delas é recomendada aqui.

| Conta | Saldo do DF (R$ bi) | R$ por pessoa por mês | Natureza da conta |
|---|---:|---:|---|
| Saldo atual (D41) | 104,45 | 2.918 | publicado no projeto |
| Tirando a CPSSS (paga por órgãos federais, seção 3.4) | 86,01 | 2.403 | tira uma linha cujo pagador é conhecido; não é estimativa |
| Tirando também o IRRF do trabalho que excede o que o DF teria com o valor por pessoa do resto do país (R$ 766; excesso de R$ 46,03 bi) | 39,98 | 1.117 | **estimativa** com suposição forte e irreal (o DF tem renda por pessoa maior que a média), só para dar a ordem de grandeza do efeito sede no IRRF |

Ponto de equilíbrio pelo lado da folha: para o saldo de R$ 104,45 bi chegar a zero só com a folha sem UF, o DF teria de ficar com 50,2% dos R$ 208,20 bi não localizados (41,3% se a CPSSS sair do lado "envia"). Nenhum arquivo aberto diz quanto dessa folha é paga a quem está no DF; isso continua sendo a opção (c) da Q30.

## 7. Não consegui confirmar

| Item | Tentativa | Situação |
|---|---|---|
| Nota metodológica ou dicionário de dados da Receita para a arrecadação por estado (que diga em que UF cada pagamento é registrado) | Página do conjunto na Receita (sem nota); dados.gov.br (HTTP 401 para acesso automatizado); legado.dados.gov.br (o domínio não resolve mais); Internet Archive (fora do ar no dia da coleta) | A regra legal (centralização na matriz) está confirmada na lei e no RIR; a nota da Receita, não |
| Quanto do IRRF do trabalho registrado no DF vem da folha federal | Arquivo por UF não tem natureza jurídica; arquivo por natureza jurídica não tem UF | Sem número oficial aberto. Caminho: pedido pela Lei de Acesso à Informação à Receita (IRRF por UF e natureza jurídica do responsável) |
| Sede do Banco do Brasil no estatuto atual | `bb.com.br/docs/pub/siteEsp/ri/pt/dce/dwn/EstatutoSocial.pdf` devolveu HTTP 403 | Não confirmado na fonte primária |
| Estatuto atual da Caixa | `caixa.gov.br` entrou em ciclo de redirecionamento | Confirmado só no estatuto de 2013 (Decreto 7.973/2013, revogado em 2021) |
| Quanto cada estatal (BB, Caixa, Correios, EBSERH) recolheu no DF | Demonstrações financeiras não abertas | Pendente |
| Conteúdo de "Outras receitas administradas" no DF (R$ 12,28 bi, 29,5% do país) | O arquivo não detalha a linha | Pendente |
| Atlas do Estado depois de 2021 por UF | A série 91 diz 1985 a 2023 no título, mas a aba por UF termina em 2021; a série 67 (até 2025) é só nacional | O ano mais recente por UF é 2021 |
| Painel Estatístico de Pessoal (PEP) | Painel interativo, sem arquivo | Substituído pelo arquivo aberto da SEGRT (mesmo ministério) |
| Causa do arquivo de junho de 2025 do Portal (gasto direto e pessoal com o dobro do normal) e do salto de "Encargos especiais" sem UF em 2025 | Não investigada; já anotada na pesquisa da folha | Pendente; caminho: Fala.BR à CGU |
| Conciliação da CPSSS da Receita (R$ 41,87 bi) com a contribuição patronal intraorçamentária do SIAFI (R$ 27,30 bi) | Não feita | Pendente |

## 8. Como reproduzir

Na pasta do projeto (`openpyxl` só para o Atlas):

```bash
# arquivos oficiais (pequenos) em data/df/
curl -sSL -A Mozilla/5.0 -o data/df/arrecadacao-estado.csv   https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv
curl -sSL -A Mozilla/5.0 -o data/df/arrecadacao-natureza.csv https://www.gov.br/receitafederal/dados/arrecadacao-natureza.csv
curl -sSL -A Mozilla/5.0 -o data/df/atlas_091.xlsx https://www.ipea.gov.br/atlasestado/arquivos/downloads/9113-091arquivounico.xlsx
curl -sSL -A Mozilla/5.0 -o data/df/segrt_serv_por_mun_exerc_202608.csv https://repositorio.dados.gov.br/segrt/Serv_por_municipio/2026/Serv_por_mun_exerc_202608.csv
python3 pipelines/df/rfb_df_breakdown.py . 2024     # seção 3.3
python3 pipelines/df/rfb_natureza.py . 2024         # seção 3.4
python3 pipelines/df/atlas_vinculos_uf.py .         # seção 1.2 (openpyxl)
python3 pipelines/df/segrt_servidores_uf.py .       # seção 1.3
python3 pipelines/df/q4_local.py .                  # seção 4
# execução da despesa do Portal: um mês a cada 90 s (WAF); retoma de onde parou e apaga cada ZIP
python3 pipelines/df/agg_desp_uf.py data/df 202401,202402,...,202512 90
python3 pipelines/df/q2_gasto_por_uf.py . 2024      # seção 2
python3 pipelines/df/q2_gasto_por_uf.py . 2025      # seção 2.4
```

