# Maiores receitas do período: entradas de dinheiro na União, 2019 a 2026

Pesquisa para a coluna "Maiores receitas do período" da home (D88, D89). Coletado em 2026-10-04. Saída de dados:
`data/home/moves-revenue.json` (mesmas chaves dos itens de `data/home/recent.json`, mais `year` e, quando conhecido,
`moved_on`; `kind` = `revenue`). Cobre janeiro de 2019 a junho de 2026; julho a outubro de 2026 já estão em
`data/home/recent.json` (ver `BRASIL-IMPOSTO_RESEARCH_recent-revenue_2026-10-04.md`). Documento escrito aos poucos, ano a
ano, do mais recente para o mais antigo. Toda frase de valor abaixo foi lida na fonte primária; o que não foi aberto está
em "Não confirmado" e o seu número não foi usado.

## Regra

- **Entra (1), entrada de dinheiro:** recebimento da União, identificável um a um, que o Tesouro Nacional destaca no
  Resultado do Tesouro Nacional (RTN) do mês: a tabela por empresa de dividendos e participações (um item por empresa e
  mês; juros sobre o capital próprio contam como dividendos, como faz o Tesouro) ou o texto das notas que explica uma
  receita atípica (bônus de assinatura de leilões de petróleo, outorgas de concessão, privatizações, devolução de recursos
  à União, tributo extraordinário ligado a um ato com data). `amount_kind` = `paid`; `moved_on` = dia do recebimento
  quando o arquivo diário de receitas do Portal da Transparência traz uma linha (ou soma de linhas) igual ao valor do
  Tesouro; senão, o mês.
- **Entra (2), ato com receita esperada:** lei, lei complementar, medida provisória ou decreto que fixa no texto ou na
  exposição de motivos oficial uma receita nova esperada em reais. `amount_kind` = `expected_revenue`; a data é a do ato.
  Quando a exposição de motivos dá um total para o período, vale o total; quando dá valores por ano, vale o do primeiro
  ano em que todas as medidas do ato estão em vigor (para um ato de agosto com efeito a partir de janeiro seguinte, o ano
  seguinte; para uma alíquota temporária que acaba no próprio ano, o ano do ato); quando a exposição não tem linha de
  total para esse ano, as linhas são somadas aqui e a soma é dita no item. Os outros anos ficam no resumo. Lei de conversão não repete a medida provisória: o item é a
  MP, e a lei aparece na situação.
- **Não entra:** arrecadação mensal ordinária de tributos; recolhimentos atípicos de IRPJ e CSLL sem ato ou evento que os
  identifique (o RTN os cita sem dizer de quem nem por quê); receitas financeiras (títulos da dívida, retorno de
  empréstimos, remuneração das disponibilidades, reversão de saldos de fundos de crédito); royalties e participação
  especial do petróleo (receita recorrente); renúncia de receita (fica na coluna de gastos, D89).
- **Quantos:** os 10 maiores de cada ano civil pelo valor oficial, o mesmo critério para todos os anos e governos, sem
  filtro de partido ou de autor.
- **Valores:** o RTN publica em R$ milhões com uma casa; o JSON guarda esse valor em reais (R$ 1.817,3 milhões viram
  1817300000). O valor exato do Portal, quando existe, fica na situação.

## Fontes e método

- Tesouro Nacional, Resultado do Tesouro Nacional, boletim mensal em PDF, página de cada mês em
  `https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/<ano>/<mês>`; lidas as
  notas do resultado do mês (receitas) e a tabela por empresa (linhas 1.4.2.x). Para achar os candidatos, a série
  histórica mensal do RTN (Tabela 1.2, `seriehistoricajul26.xlsx`, CKAN do Tesouro Transparente) foi varrida de janeiro
  de 2019 a junho de 2026; cada valor usado foi conferido no boletim do mês.
- Portal da Transparência, arquivo anual de receitas (`https://portaldatransparencia.gov.br/download-de-dados/receitas/<ano>`):
  data e valor ao centavo de cada lançamento, sem o nome de quem pagou.
- Atos: lista de medidas provisórias 2019 a 2026 (API de dados abertos do Senado, `materia/pesquisa/lista?sigla=MPV`);
  a exposição de motivos de cada MP que não abre crédito extraordinário foi baixada do Planalto e lida nos trechos de
  arrecadação. Leis, leis complementares e decretos tributários: API de legislação do Senado (`legislacao/lista`),
  filtrados pela ementa.
- Datas dos proventos da Petrobras: página "Proventos Declarados" da empresa,
  `https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/`.

## 2026 (janeiro a junho)

| # | Movimento | Data | Valor oficial | Natureza | Fonte do valor |
|---|---|---|---|---|---|
| 1 | Imposto de exportação de 12% sobre petróleo bruto criado pela MP nº 1.340/2026 | 12/03/2026 (ato) | R$ 15,6 bi | expected_revenue | Exposição de Motivos EMI nº 484/2026 |
| 2 | Imposto de exportação sobre petróleo bruto recolhido em junho de 2026 | junho de 2026 | R$ 3,8 bi | paid | RTN de junho de 2026 |
| 3 | Dividendos e participações pagos pela Petrobras à União em março de 2026 | 20/03/2026 | R$ 1.817,3 mi | paid | RTN de março de 2026 |
| 4 | Dividendos e participações pagos pela Petrobras à União em fevereiro de 2026 | 20/02/2026 | R$ 1.797,4 mi | paid | RTN de fevereiro de 2026 |
| 5 | Dividendos e participações pagos pela Petrobras à União em junho de 2026 | 22/06/2026 | R$ 1.247,4 mi | paid | RTN de junho de 2026 |
| 6 | Dividendos e participações pagos pela Petrobras à União em maio de 2026 | 20/05/2026 | R$ 1.232,9 mi | paid | RTN de maio de 2026 |
| 7 | Imposto de exportação sobre petróleo bruto recolhido em maio de 2026 | maio de 2026 | R$ 1,0 bi | paid | RTN de maio de 2026 |
| 8 | Dividendos e participações pagos pelo Banco do Brasil à União em março de 2026 | março de 2026 | R$ 835,7 mi | paid | RTN de março de 2026 |
| 9 | Dividendos e participações pagos pela Caixa Econômica Federal à União em maio de 2026 | maio de 2026 | R$ 582,0 mi | paid | RTN de maio de 2026 |
| 10 | Dividendos e participações pagos pelo Banco do Brasil à União em junho de 2026 | 11/06/2026 | R$ 404,8 mi | paid | RTN de junho de 2026 |

### Itens e trechos lidos

1. **Imposto de exportação de 12% sobre petróleo bruto criado pela MP nº 1.340/2026**: R$ 15,6 bi (expected_revenue).
   - Fonte: Exposição de Motivos EMI nº 484/2026, de 11/03/2026, assinada pelos Ministros da Fazenda e de Minas e Energia, item 5, https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/exm/exm-mp-1340-26.pdf (publicado em 2026-03-11).
   - Trecho lido: "As estimativas de arrecadação do imposto de exportação para o período de quatro meses produz arrecadação da ordem R$ 15,6 bilhões no cenário de referência central com Brent a US$ 90/barril, variando entre R$ 13,9 bilhões (Brent a US$ 80,0/barril) e R$ 17,4 bilhões (Brent a US$ 100,0/barril) dependendo do cenário."
   - Situação: Medida provisória publicada em edição extra do Diário Oficial da União de 12/03/2026; o Planalto marca a vigência como encerrada. A partir de 10/07/2026 a alíquota de 12% passou a ser fixada pela Resolução Gecex nº 938/2026. O Tesouro Nacional registrou R$ 1,0 bilhão desse imposto em maio e R$ 3,8 bilhões em junho de 2026.
2. **Imposto de exportação sobre petróleo bruto recolhido em junho de 2026**: R$ 3,8 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2026, Nota 6 do resultado mês contra mês, https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/55186_1771509/boletim_jun26.pdf (publicado em 2026-07-30).
   - Trecho lido: "resultado refletiu, principalmente, as alterações legislativas no Imposto de Exportação sobre óleo bruto (MP nº 1.340/2026), item responsável pelo recolhimento de R$ 3,8 bilhões no mês de junho de 2026."
   - Situação: Recolhido em junho de 2026. No Portal da Transparência (receitas de 2026), o Imposto sobre a Exportação somou R$ 3.773,0 milhões no mês, em três lançamentos: 10/06 R$ 1.376.780.141,17; 20/06 R$ 1.293.164.047,79; 30/06 R$ 1.103.079.804,26.
3. **Dividendos e participações pagos pela Petrobras à União em março de 2026**: R$ 1.817,3 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de março de 2026, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/54551_1765837/boletim_mar26.pdf (publicado em 2026-04-29).
   - Trecho lido: "1.4.2.8 Petrobras 2.548,9 1.817,3 (Março 2025, Março 2026, em R$ milhões)"
   - Situação: Recebido pela União em 20/03/2026 (Portal da Transparência, receitas de 2026: dividendos de R$ 1.108.755.744,07 e juros sobre o capital próprio de R$ 708.555.253,64 nessa data); atribuído à Petrobras pelo Tesouro Nacional. A Petrobras informa pagamento em 20/03/2026 da 2ª parcela dos proventos do 3º trimestre de 2025 (https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/).
4. **Dividendos e participações pagos pela Petrobras à União em fevereiro de 2026**: R$ 1.797,4 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de fevereiro de 2026, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/54224_1685003/boletim_fev26.pdf (publicado em 2026-03-30).
   - Trecho lido: "1.4.2.8 Petrobras 2.526,5 1.797,4 (Fevereiro 2025, Fevereiro 2026, em R$ milhões)"
   - Situação: Recebido pela União em 20/02/2026 (Portal da Transparência, receitas de 2026: juros sobre o capital próprio de R$ 1.797.388.502,09 nessa data); atribuído à Petrobras pelo Tesouro Nacional. A Petrobras informa pagamento em 20/02/2026 da 1ª parcela de juros sobre o capital próprio do 3º trimestre de 2025 (https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/).
5. **Dividendos e participações pagos pela Petrobras à União em junho de 2026**: R$ 1.247,4 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2026, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/55186_1771509/boletim_jun26.pdf (publicado em 2026-07-30).
   - Trecho lido: "1.4.2.8 Petrobras 1.407,5 1.247,4 (Junho 2025, Junho 2026, em R$ milhões)"
   - Situação: Recebido pela União em 22/06/2026 (Portal da Transparência, receitas de 2026: juros sobre o capital próprio de R$ 1.247.441.479,56 nessa data); atribuído à Petrobras pelo Tesouro Nacional. A Petrobras informa pagamento em 22/06/2026 da 2ª parcela de juros sobre o capital próprio do 4º trimestre de 2025 (https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/).
6. **Dividendos e participações pagos pela Petrobras à União em maio de 2026**: R$ 1.232,9 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2026, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/54963_1792828/boletim_mai26.pdf (publicado em 2026-06-29).
   - Trecho lido: "1.4.2.8 Petrobras 1.390,8 1.232,9 (Maio 2025, Maio 2026, em R$ milhões)"
   - Situação: Recebido pela União em 20/05/2026 (Portal da Transparência, receitas de 2026: juros sobre o capital próprio de R$ 1.232.876.273,24 nessa data); atribuído à Petrobras pelo Tesouro Nacional. A Petrobras informa pagamento em 20/05/2026 da 1ª parcela de juros sobre o capital próprio do 4º trimestre de 2025 (https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/).
7. **Imposto de exportação sobre petróleo bruto recolhido em maio de 2026**: R$ 1,0 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2026, Nota 6 do resultado mês contra mês, https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/54963_1792828/boletim_mai26.pdf (publicado em 2026-06-29).
   - Trecho lido: "Adicionalmente, registrou-se arrecadação de R$ 1,0 bilhão referente ao Imposto de Exportação incidente sobre óleo bruto, em razão da MP nº 1.340/2026."
   - Situação: Recolhido em maio de 2026, primeiro mês com arrecadação relevante do imposto. No Portal da Transparência (receitas de 2026), o Imposto sobre a Exportação somou R$ 1.048,5 milhões no mês: 20/05 R$ 238.894.329,26 e 31/05 R$ 809.580.671,41.
8. **Dividendos e participações pagos pelo Banco do Brasil à União em março de 2026**: R$ 835,7 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de março de 2026, Tabela 3.1, linha 1.4.2.1 Banco do Brasil (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/54551_1765837/boletim_mar26.pdf (publicado em 2026-04-29).
   - Trecho lido: "1.4.2.1 Banco do Brasil 1.835,1 835,7 (Março 2025, Março 2026, em R$ milhões)"
   - Situação: Recebido pela União em março de 2026; no Portal da Transparência (receitas de 2026), duas entradas de juros sobre o capital próprio somam o valor do Tesouro: 05/03 R$ 634.666.644,17 e 11/03 R$ 200.985.801,56. Atribuído ao Banco do Brasil pelo Tesouro Nacional; o Portal não nomeia o pagador.
9. **Dividendos e participações pagos pela Caixa Econômica Federal à União em maio de 2026**: R$ 582,0 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2026, Tabela 3.1, linha 1.4.2.4 Caixa (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/54963_1792828/boletim_mai26.pdf (publicado em 2026-06-29).
   - Trecho lido: "1.4.2.4 Caixa 0,0 582,0 (Maio 2025, Maio 2026, em R$ milhões)"
   - Situação: Recebido pela União em maio de 2026; atribuído à Caixa Econômica Federal pelo Tesouro Nacional. O Portal da Transparência não nomeia o pagador e nenhuma linha diária de maio bate sozinha com o valor; a maior entrada de juros sobre o capital próprio do mês sem outro pagador identificado é de R$ 554.011.249,23, em 14/05/2026.
10. **Dividendos e participações pagos pelo Banco do Brasil à União em junho de 2026**: R$ 404,8 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2026, Tabela 3.1, linha 1.4.2.1 Banco do Brasil (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/55186_1771509/boletim_jun26.pdf (publicado em 2026-07-30).
   - Trecho lido: "1.4.2.1 Banco do Brasil 1.217,0 404,8 (Junho 2025, Junho 2026, em R$ milhões)"
   - Situação: Recebido pela União em 11/06/2026 (Portal da Transparência, receitas de 2026: juros sobre o capital próprio de R$ 404.774.157,49 nessa data); atribuído ao Banco do Brasil pelo Tesouro Nacional.

### Também conferido em 2026 (janeiro a junho)

- **Logo abaixo do corte (RTN, Tabela 3.1):** Banco do Nordeste, março, R$ 383,4 mi (Portal: R$ 383.415.457,66 em
  30/03/2026); BNDES, maio, R$ 202,2 mi (Portal: dividendos de R$ 87.955.089,05 e juros sobre o capital próprio de
  R$ 114.204.532,20 em 08/05/2026); Eletrobras, maio, R$ 86,2 mi (Portal: R$ 86.203.632,14 em 06/05/2026). As linhas
  "Demais dividendos" (R$ 696,3 mi em abril, R$ 733,4 mi em junho) somam várias empresas e não identificam o pagador.
- **Notas do RTN, janeiro a junho:** nenhuma concessão, leilão, privatização ou devolução à União destacada. Concessões e
  Permissões ficaram entre R$ 202,1 mi (junho) e R$ 909,6 mi (maio) por mês, sem item nomeado. Bônus de assinatura de
  partilha no Portal: R$ 51,8 mi em 26/03/2026.
- **Recolhimentos atípicos de IRPJ e CSLL** (RTN de maio: "recolhimentos atípicos na estimativa mensal"; RTN de junho:
  "recolhimentos atípicos da estimativa mensal (R$ 4,0 bilhões entre IRPJ e CSLL)"): o Tesouro não diz de quem nem por
  quê; fora da regra.
- **Atos:** as exposições de motivos das MPs 1.334 a 1.373 (janeiro a junho, exceto créditos extraordinários) foram
  lidas. Só a MP 1.340 fixa receita nova em reais. A MP 1.355 (Novo Desenrola) estima "arrecadação entre R$ 1,7 bilhão e
  R$ 1,8 bilhão anuais" na renegociação de contratos do Fies: é recuperação de crédito (receita financeira), fora da
  regra. Leis e leis complementares de janeiro a junho de 2026 com tema tributário (LC 227, LC 228, LC 229, Lei 15.329,
  Lei 15.394): nenhuma fixa receita nova em reais; a LC 228 reduz alíquotas (renúncia).

## 2025

| # | Movimento | Data | Valor oficial | Natureza | Fonte do valor |
|---|---|---|---|---|---|
| 1 | Imposto mínimo sobre altas rendas e tributação de dividendos remetidos ao exterior (Lei nº 15.270/2025) | 26/11/2025 (ato) | R$ 34.120,0 mi | expected_revenue | Exposição de Motivos EM nº 00019/2025 MF |
| 2 | Tributação de aplicações financeiras, apostas, CSLL e juros sobre capital próprio (MP nº 1.303/2025) | 11/06/2025 (ato) | R$ 20.870,0 mi | expected_revenue | Exposição de Motivos EMI nº 00041/2025 MF MGI |
| 3 | Leilões dos direitos da União em acordos de individualização da produção de petróleo (AIP) | dezembro de 2025 | R$ 8,8 bi | paid | RTN de dezembro de 2025 |
| 4 | Dividendos e participações pagos pelo BNDES à União em agosto de 2025 | 12/08/2025 | R$ 6.783,7 mi | paid | RTN de agosto de 2025 |
| 5 | Dividendos e participações pagos pelo BNDES à União em maio de 2025 | 16/05/2025 | R$ 6.560,7 mi | paid | RTN de maio de 2025 |
| 6 | Dividendos e participações pagos pelo BNDES à União em dezembro de 2025 | 29/12/2025 | R$ 6.180,0 mi | paid | RTN de dezembro de 2025 |
| 7 | Resgate de recursos da União nos fundos garantidores FGO e FGI | maio de 2025 | R$ 5,0 bi | paid | RTN de maio de 2025 |
| 8 | Dividendos e participações pagos pelo BNDES à União em outubro de 2025 | 31/10/2025 | R$ 2.801,6 mi | paid | RTN de outubro de 2025 |
| 9 | Dividendos e participações pagos pela Caixa Econômica Federal à União em abril de 2025 | 04/04/2025 | R$ 2.771,0 mi | paid | RTN de abril de 2025 |
| 10 | Dividendos e participações pagos pela Petrobras à União em março de 2025 | 20/03/2025 | R$ 2.548,9 mi | paid | RTN de março de 2025 |

### Itens e trechos lidos

1. **Imposto mínimo sobre altas rendas e tributação de dividendos remetidos ao exterior (Lei nº 15.270/2025)**: R$ 34.120,0 mi (expected_revenue).
   - Fonte: Exposição de Motivos EM nº 00019/2025 MF, de 15/03/2025, do Projeto de Lei nº 1.087/2025 (convertido na Lei nº 15.270/2025), item 26, tabela em bilhões de reais, linha Total, coluna 2026, https://www.planalto.gov.br/ccivil_03/Projetos/Ato_2023_2026/2025/PL/Exm/Exm-0019-25-MF.doc (publicado em 2025-03-15).
   - Trecho lido: "A Secretaria Especial da Receita Federal do Brasil estima que estas medidas resultem na arrecadação dos seguintes valores, em bilhões de reais: Imposto mínimo da Pessoa Física 25,22 (2026) 29,49 (2027) 29,83 (2028); Dividendos para o Exterior 8,9 (2026) 9,69 (2027) 9,81 (2028); Total 34,12 (2026) 39,18 (2027) 39,64 (2028)"
   - Situação: Lei em vigor, publicada no Diário Oficial da União de 27/11/2025, com efeitos a partir de 2026. Os valores são os da exposição de motivos do projeto enviado pelo Executivo (PL nº 1.087/2025); o texto foi alterado no Congresso e a estimativa não foi refeita no ato. A mesma exposição estima a renúncia da redução do imposto de renda em R$ 25,84 bilhões em 2026 (lado da saída).
2. **Tributação de aplicações financeiras, apostas, CSLL e juros sobre capital próprio (MP nº 1.303/2025)**: R$ 20.870,0 mi (expected_revenue).
   - Fonte: Exposição de Motivos EMI nº 00041/2025 MF MGI, de 10/06/2025, item 44, tabela dos ganhos estimados; valor = soma, feita nesta pesquisa, das cinco linhas da coluna 2026, o primeiro ano completo de vigência (a exposição não traz total), https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/exm/exm-1303-25.pdf (publicado em 2025-06-10).
   - Trecho lido: "os art. 61 a art. 64 da Medida Provisória introduzem outras alterações na legislação tributária que acarretam aumento de receita tributária. A tabela abaixo apresenta os ganhos estimados em razão desses dispositivos: [coluna 2026] Revogação Isenção TVM R$ 2.600 milhões; Apostas de Quota Fixa R$ 1.700 milhões; Alíquota da CSLL R$ 1.580 milhões; Juros sobre Capital Próprio R$ 4.990 milhões; Compensação de Tributos Administrados pela RFB R$ 10.000 milhões"
   - Situação: Perdeu a validade sem ser votada: o Ato Declaratório nº 67/2025 do Presidente da Mesa do Congresso Nacional (Diário Oficial da União de 15/10/2025) informa que a MP 'teve seu prazo de vigência encerrado no dia 8 de outubro de 2025'. A receita prevista para 2026 não se realizou por esta MP.
3. **Leilões dos direitos da União em acordos de individualização da produção de petróleo (AIP)**: R$ 8,8 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2025, Nota 7 do resultado mês contra mês (Exploração de Recursos Naturais), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/53718_1740106/boletim_dez25.pdf (publicado em 2026-01-29).
   - Trecho lido: "o crescimento observado é decorrente, primordialmente, da realização de leilões sobre direitos futuros de Acordos de Individualização da Produção (AIPs) em dezembro de 2025 (+R$ 8,8 bilhões), evento que não teve contrapartida em dezembro de 2024."
   - Situação: Recebido em dezembro de 2025. No Portal da Transparência (receitas de 2025), a natureza 'ALIEN.DIR.OBRIG.DECORRENTES DE AIP' registra R$ 1.558.368.862,00 em 17/12/2025 e R$ 7.234.932.100,00 em 18/12/2025, total de R$ 8.793.300.962,00.
4. **Dividendos e participações pagos pelo BNDES à União em agosto de 2025**: R$ 6.783,7 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de agosto de 2025, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/52973_1663793/Boletim_ago25.pdf (publicado em 2025-09-29).
   - Trecho lido: "1.4.2.3 BNDES 0,0 6.783,7 (Agosto 2024, Agosto 2025, em R$ milhões)"
   - Situação: Recebido pela União em 12/08/2025 (Portal da Transparência, receitas de 2025: juros sobre o capital próprio de R$ 6.783.656.005,09 nessa data); atribuído ao BNDES pelo Tesouro Nacional (Nota 5 do RTN de agosto de 2025: 'pagamentos de dividendos do BNDES (R$ 6,8 bilhões)').
5. **Dividendos e participações pagos pelo BNDES à União em maio de 2025**: R$ 6.560,7 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2025, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/52393_1645927/Boletim_mai25.pdf (publicado em 2025-06-26).
   - Trecho lido: "1.4.2.3 BNDES 10.083,2 6.560,7 (Maio 2024, Maio 2025, em R$ milhões)"
   - Situação: Recebido pela União em 16/05/2025 (Portal da Transparência, receitas de 2025: dividendos de R$ 5.742.562.860,75 e juros sobre o capital próprio de R$ 818.174.726,80 nessa data, soma de R$ 6.560.737.587,55); atribuído ao BNDES pelo Tesouro Nacional.
6. **Dividendos e participações pagos pelo BNDES à União em dezembro de 2025**: R$ 6.180,0 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2025, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/53718_1740106/boletim_dez25.pdf (publicado em 2026-01-29).
   - Trecho lido: "1.4.2.3 BNDES 13.623,4 6.180,0 (Dezembro 2024, Dezembro 2025, em R$ milhões)"
   - Situação: Recebido pela União em 29/12/2025 (Portal da Transparência, receitas de 2025: dividendos de R$ 3.613.195.243,94 e juros sobre o capital próprio de R$ 2.566.804.756,06 nessa data, soma de R$ 6.180.000.000,00); atribuído ao BNDES pelo Tesouro Nacional. Um lançamento de dividendos de R$ 3.474.869.756,57 em 26/12/2025 foi estornado no mesmo dia.
7. **Resgate de recursos da União nos fundos garantidores FGO e FGI**: R$ 5,0 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2025, Nota 4 do resultado mês contra mês (Demais Receitas Não Administradas), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/52393_1645927/Boletim_mai25.pdf (publicado em 2025-06-26).
   - Trecho lido: "explicado, principalmente, pelos resgates de recursos do Fundo de Garantia de Operações - FGO e do Fundo Garantidor para Investimentos - FGI em maio de 2025, cujo montantante foi da ordem de R$ 5,0 bilhões, sem contrapartida em maio de 2024."
   - Situação: Recebido em maio de 2025. O RTN de maio de 2026 (Nota 10) descreve o resgate como 'devolução de recursos aportados pela União para viabilizar medidas de apoio durante a calamidade pública ocorrida no Rio Grande do Sul'. No Portal da Transparência (receitas de 2025), a natureza 'ALIENACAO DE BENS INTANGIVEIS' registra R$ 111.594.418,29 em 22/05/2025 e R$ 4.928.631.916,36 em 28/05/2025; o Portal não nomeia os fundos.
8. **Dividendos e participações pagos pelo BNDES à União em outubro de 2025**: R$ 2.801,6 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de outubro de 2025, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/53290_2433011/boletim_out25.pdf (publicado em 2025-11-26).
   - Trecho lido: "1.4.2.3 BNDES 0,0 2.801,6 (Outubro 2024, Outubro 2025, em R$ milhões)"
   - Situação: Recebido pela União em 31/10/2025 (Portal da Transparência, receitas de 2025: juros sobre o capital próprio de R$ 2.801.605.448,78 nessa data); atribuído ao BNDES pelo Tesouro Nacional.
9. **Dividendos e participações pagos pela Caixa Econômica Federal à União em abril de 2025**: R$ 2.771,0 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de abril de 2025, Tabela 3.1, linha 1.4.2.4 Caixa (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/52218_1693606/Boletim_abr25.pdf (publicado em 2025-05-29).
   - Trecho lido: "1.4.2.4 Caixa 0,0 2.771,0 (Abril 2024, Abril 2025, em R$ milhões)"
   - Situação: Recebido pela União em 04/04/2025 (Portal da Transparência, receitas de 2025: juros sobre o capital próprio de R$ 2.685.003.573,21, mais R$ 85.953.435,07 de multas e juros, nessa data); atribuído à Caixa pelo Tesouro Nacional.
10. **Dividendos e participações pagos pela Petrobras à União em março de 2025**: R$ 2.548,9 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de março de 2025, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/51990_2454681/Boletim_mar25.pdf (publicado em 2025-04-29).
   - Trecho lido: "1.4.2.8 Petrobras 2.575,9 2.548,9 (Março 2024, Março 2025, em R$ milhões)"
   - Situação: Pago pela Petrobras em 20/03/2025, 2ª parcela dos proventos do 3º trimestre de 2024 (https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/); atribuído à Petrobras pelo Tesouro Nacional. No Portal da Transparência, as entradas de 20/03/2025 (dividendos de R$ 2.909.345.833,52 e juros sobre o capital próprio de R$ 1.046.678.250,43) reúnem os pagamentos da Petrobras e do Banco do Brasil e não separam as duas empresas.

### Também conferido em 2025

- **Logo abaixo do corte (RTN, tabela por empresa):** Petrobras, fevereiro, R$ 2.526,5 mi (Portal: R$ 3.284.461.863,92
  em 20/02/2025, com estorno parcial de R$ 757.946.390,10 em 27/02/2025); Banco do Brasil, março, R$ 1.835,1 mi;
  Petrobras, agosto, R$ 1.700,4 mi (Portal: R$ 1.700.354.816,72 em 20/08/2025); Caixa, dezembro, R$ 1.409,7 mi (Portal:
  R$ 1.409.682.908,08 em 05/12/2025); Petrobras, junho, R$ 1.407,5 mi; Petrobras, maio, R$ 1.390,8 mi; Eletrobras,
  dezembro, R$ 1.262,0 mi (Portal: R$ 1.262.001.132,93 em 19/12/2025); Eletrobras, agosto, R$ 1.173,9 mi (Portal:
  R$ 1.173.911.972,12 em 28/08/2025).
- **Notas do RTN de 2025 que não viram item:** recolhimento atípico de IRPJ de R$ 3,0 bilhões em julho "especialmente
  relacionado a empresas do setor financeiro" (sem ato nem pagador identificado); arrecadação atípica de R$ 331,0 milhões
  em loterias de apostas de quota fixa em junho (abaixo do corte); indenizações por desastres de acordos judiciais e multas
  de acordos de leniência em setembro (o RTN não dá o valor de cada uma; no Portal, R$ 562.633.472,22 de indenização em
  18/09/2025 e R$ 475.713.553,93 de multas de leniência em 26/09/2025, abaixo do corte); devolução de depósitos judiciais
  de R$ 6,2 bilhões em novembro (é saída, não entrada); arrecadação do IOF maior por causa do Decreto nº 12.499/2025
  (arrecadação ordinária de um tributo, ver abaixo).
- **Decretos do IOF (Decreto nº 12.466, de 22/05/2025, e Decreto nº 12.499, de 11/06/2025):** aumentaram alíquotas do IOF.
  As páginas do Planalto não trazem exposição de motivos e o texto dos decretos não fixa valor de receita; a estimativa
  citada em notas do Ministério da Fazenda não é exposição de motivos. Fora da regra (2).
- **Lei Complementar nº 224/2025 (26/12/2025)** (corte de benefícios fiscais) **e Lei nº 15.265/2025 (21/11/2025)**
  (Rearp e tributação de empréstimo de títulos): as páginas do Planalto não ligam exposição de motivos e o texto não fixa
  receita em reais; nenhum valor foi lido em fonte primária. Ficam fora até achar a exposição de motivos de origem.
- **Outras MPs de 2025:** exposições de motivos lidas de todas as MPs de 2025 que não abrem crédito extraordinário; só a
  MP 1.303 fixa receita nova em reais. A MP 1.301 estima redução de receita (lado da saída).
- **Concessões e Permissões:** sem item destacado nas notas de 2025. No Portal, os bônus de assinatura da ANP de outubro de
  2025 somam várias linhas de R$ 93,1 mi a R$ 407,6 mi (leilão com vários vencedores; abaixo do corte).
- **Acordo de Equalização de Gastos e Volumes da jazida de Jubarte:** RTN de dezembro de 2025, Nota 8 do acumulado no
  ano: "acordo de Equalização de Gastos e Volumes (EGV) da Jazida de Jubarte (R$ 1,5 bilhão em outubro)". Entrada única
  identificada, mas abaixo do corte de 2025 (o 10º item tem R$ 2.548,9 mi).

## 2024

| # | Movimento | Data | Valor oficial | Natureza | Fonte do valor |
|---|---|---|---|---|---|
| 1 | Limite à compensação de créditos de PIS/Pasep e Cofins (MP nº 1.227/2024) | 04/06/2024 (ato) | R$ 17,5 bi | expected_revenue | Exposição de Motivos EM nº 00060/2024 MF |
| 2 | Dividendos e participações pagos pelo BNDES à União em dezembro de 2024 | dezembro de 2024 | R$ 13.623,4 mi | paid | RTN de dezembro de 2024 |
| 3 | Dividendos e participações pagos pelo BNDES à União em maio de 2024 | maio de 2024 | R$ 10.083,2 mi | paid | RTN de maio de 2024 |
| 4 | Dividendos e participações pagos pela Petrobras à União em dezembro de 2024 | dezembro de 2024 | R$ 7.774,0 mi | paid | RTN de dezembro de 2024 |
| 5 | Depósitos judiciais transferidos pela Caixa à Conta Única do Tesouro (art. 41 da Lei nº 14.973/2024) | outubro de 2024 | R$ 6,2 bi | paid | RTN de outubro de 2024 |
| 6 | Dividendos e participações pagos pelo BNDES à União em novembro de 2024 | 29/11/2024 | R$ 5.793,5 mi | paid | RTN de novembro de 2024 |
| 7 | Dividendos e participações pagos pela Petrobras à União em junho de 2024 | 20/06/2024 | R$ 5.496,0 mi | paid | RTN de junho de 2024 |
| 8 | Dividendos e participações pagos pela Petrobras à União em maio de 2024 | 20/05/2024 | R$ 5.448,8 mi | paid | RTN de maio de 2024 |
| 9 | Outorgas das usinas hidrelétricas da Copel (desestatização da Copel) | 21/11/2024 | R$ 4,1 bi | paid | RTN de novembro de 2024 |
| 10 | Imposto sobre rendimentos acumulados em fundos de investimento (art. 28 da Lei nº 14.754/2023) | janeiro de 2024 | R$ 4,1 bi | paid | RTN de janeiro de 2024 |

### Itens e trechos lidos

1. **Limite à compensação de créditos de PIS/Pasep e Cofins (MP nº 1.227/2024)**: R$ 17,5 bi (expected_revenue).
   - Fonte: Exposição de Motivos EM nº 00060/2024 MF, de 29/05/2024, assinada por Fernando Haddad, seção VI (Impacto Orçamentário-Financeiro), https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/exm/exm-1227-24.pdf (publicado em 2024-05-29).
   - Trecho lido: "Registra-se que a limitação da compensação tributária, a partir de 1º de junho de 2024, permitirá que R$ 17,5 bilhões (dezessete bilhões e quinhentos milhões de reais) em débitos relativos a tributos administrados pela Secretaria Especial da Receita Federal do Brasil deixem de ser compensados com créditos do regime de incidência não cumulativa da Contribuição para o PIS/Pasep e da Cofins no exercício de 2024."
   - Situação: Sem efeito na parte de receita: o Presidente do Congresso Nacional rejeitou sumariamente os incisos III e IV do art. 1º e os arts. 5º e 6º (limite à compensação e revogação do ressarcimento de créditos presumidos), com encerramento da vigência desde a edição (Ato Declaratório nº 36/2024, Diário Oficial da União de 12/06/2024); o restante da MP perdeu a vigência em 01/10/2024 (Ato Declaratório nº 95/2024).
2. **Dividendos e participações pagos pelo BNDES à União em dezembro de 2024**: R$ 13.623,4 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2024, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/51291_1726861/boletim_dez24.pdf (publicado em 2025-01-30).
   - Trecho lido: "1.4.2.3 BNDES 0,0 13.623,4 (Dezembro 2023, Dezembro 2024, em R$ milhões)"
   - Situação: Recebido pela União em dezembro de 2024; atribuído ao BNDES pelo Tesouro Nacional (Nota 2 do RTN de dezembro de 2024: 'maiores recebimentos de dividendos e juros sobre o capital próprio do BNDES (+R$ 13,6 bilhões)'). No Portal da Transparência, a maior entrada do mês é de 27/12/2024 (dividendos de R$ 10.033.151.061,89 e juros sobre o capital próprio de R$ 4.095.926.675,82), soma que inclui outro pagador; o Portal não nomeia quem pagou.
3. **Dividendos e participações pagos pelo BNDES à União em maio de 2024**: R$ 10.083,2 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2024, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/49889_1570617/boletim_mai24.pdf (publicado em 2024-06-26).
   - Trecho lido: "1.4.2.3 BNDES 10.425,1 10.083,2 (Maio 2023, Maio 2024, em R$ milhões)"
   - Situação: Recebido pela União em maio de 2024; atribuído ao BNDES pelo Tesouro Nacional. No Portal da Transparência, as entradas de 08/05/2024 (dividendos de R$ 5.426.371.012,00 e juros sobre o capital próprio de R$ 4.929.073.284,28) comportam o pagamento, mas somam mais que ele e não nomeiam o pagador.
4. **Dividendos e participações pagos pela Petrobras à União em dezembro de 2024**: R$ 7.774,0 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2024, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/51291_1726861/boletim_dez24.pdf (publicado em 2025-01-30).
   - Trecho lido: "1.4.2.8 Petrobras 4.253,6 7.774,0 (Dezembro 2023, Dezembro 2024, em R$ milhões)"
   - Situação: Recebido pela União em dezembro de 2024, em duas datas: 20/12/2024 (R$ 1.969.732.228,31, 2ª parcela dos dividendos do 2º trimestre de 2024) e 23/12/2024 (R$ 5.804.249.135,84, dividendos extraordinários em parcela única), segundo o Portal da Transparência (soma igual ao valor do Tesouro) e as datas de pagamento da Petrobras (https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/).
5. **Depósitos judiciais transferidos pela Caixa à Conta Única do Tesouro (art. 41 da Lei nº 14.973/2024)**: R$ 6,2 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de outubro de 2024, Nota 9 do resultado mês contra mês (Demais Receitas Não Administradas), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/50869_1601111/boletim_out24.pdf (publicado em 2024-12-03).
   - Trecho lido: "justificado, especialmente, pelo recebimento de depósitos judiciais transferidos pela CAIXA em outubro de 2024 (cerca de R$ 6,2 bilhões)."
   - Situação: Recebido em outubro de 2024. O art. 41 da Lei nº 14.973/2024 mandou transferir para a Conta Única, em até 30 dias, os depósitos judiciais e extrajudiciais que ainda não estavam nela; o RTN de outubro de 2025 (Nota 7) liga a entrada de outubro de 2024 a esse artigo. No Portal da Transparência, a maior entrada não tributária de outubro de 2024 é de R$ 6.307.623.766,21 em 20/10/2024 (natureza 'OUTRAS REC.N.ARREC.N.PROJ.RFB-PRIM.'); o Portal não diz a origem.
6. **Dividendos e participações pagos pelo BNDES à União em novembro de 2024**: R$ 5.793,5 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de novembro de 2024, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/51179_1615868/boletim_nov24.pdf (publicado em 2025-01-15).
   - Trecho lido: "1.4.2.3 BNDES 0,0 5.793,5 (Novembro 2023, Novembro 2024, em R$ milhões)"
   - Situação: Recebido pela União em 29/11/2024 (Portal da Transparência, receitas de 2024: juros sobre o capital próprio de R$ 5.793.534.103,81 nessa data); atribuído ao BNDES pelo Tesouro Nacional.
7. **Dividendos e participações pagos pela Petrobras à União em junho de 2024**: R$ 5.496,0 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2024, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/50117_1586943/boletim_jun24.pdf (publicado em 2024-07-26).
   - Trecho lido: "1.4.2.8 Petrobras 3.467,2 5.496,0 (Junho 2023, Junho 2024, em R$ milhões)"
   - Situação: Pago pela Petrobras em 20/06/2024: 2ª parcela dos dividendos extraordinários e dos dividendos do 4º trimestre de 2023 (https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/); atribuído à Petrobras pelo Tesouro Nacional. No Portal da Transparência, as entradas de 20/06/2024 somam mais que o valor do Tesouro e incluem outro pagador.
8. **Dividendos e participações pagos pela Petrobras à União em maio de 2024**: R$ 5.448,8 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2024, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/49889_1570617/boletim_mai24.pdf (publicado em 2024-06-26).
   - Trecho lido: "1.4.2.8 Petrobras 5.388,9 5.448,8 (Maio 2023, Maio 2024, em R$ milhões)"
   - Situação: Recebido pela União em 20/05/2024 (Portal da Transparência, receitas de 2024: dividendos de R$ 5.448.760.613,85 nessa data); 1ª parcela dos dividendos extraordinários e dos dividendos do 4º trimestre de 2023 (https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/).
9. **Outorgas das usinas hidrelétricas da Copel (desestatização da Copel)**: R$ 4,1 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de novembro de 2024, Nota 5 do resultado mês contra mês (Concessões e Permissões), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/51179_1615868/boletim_nov24.pdf (publicado em 2025-01-15).
   - Trecho lido: "majoritariamente explicado pela arrecadação de 4,1 bilhões em novembro de 2024, referente às outorgas das Usinas Hidrelétricas Governador Bento Munhoz da Rocha Netto, Governador Ney Aminthas de Barros Braga e Governador José Richa, decorrentes do processo de desestatização da COPEL, ocorrido em 2023."
   - Situação: Recebido pela União em 21/11/2024 (Portal da Transparência, receitas de 2024: R$ 4.073.915.184,17 na natureza 'CONC.SERV.GER.TRANSM.DISTR.ENER.ELET', unidade ANEEL, nessa data).
10. **Imposto sobre rendimentos acumulados em fundos de investimento (art. 28 da Lei nº 14.754/2023)**: R$ 4,1 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de janeiro de 2024, Nota 1 do resultado mês contra mês (Imposto sobre a Renda), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/49021_1589260/boletim_jan24.pdf (publicado em 2024-02-28).
   - Trecho lido: "Rendimentos do Capital (+R$ 2,3 bilhões), incluindo os recolhimentos de R$ 4,1 bilhões decorrentes da tributação dos fundos de investimento assinalados no art.28, inciso I, da Lei nº 14.754/2023"
   - Situação: Recolhido em janeiro de 2024. O art. 28 da Lei nº 14.754/2023 deu ao cotista a opção de pagar o imposto de renda sobre os rendimentos acumulados até 30/11/2023 à alíquota de 8%. O Portal da Transparência não separa esse recolhimento das demais linhas de IRRF sobre rendimentos de capital.

### Também conferido em 2024

- **Logo abaixo do corte:** antecipação paga pela Vale de R$ 4,0 bilhões a título de "Ajuste Regulatório Preliminar" dos
  termos aditivos das ferrovias Carajás e Vitória a Minas (RTN de dezembro de 2024, Nota 1; Portal: R$ 2.800.000.000,00
  e R$ 1.200.000.000,00 em 30/12/2024); MP nº 1.262/2024 (adicional da CSLL das regras globais contra a erosão da base
  tributária, convertida na Lei nº 15.079/2024), cuja exposição de motivos estima "R$ 3,44 bilhões ... em 2026, R$ 7,28
  bilhões ... em 2027, e R$ 7,69 bilhões ... em 2028"; Caixa, março, R$ 2.792,6 mi (Portal: R$ 2.724.583.613,50 mais
  R$ 68.046.359,48 de multas e juros em 26/03/2024); Petrobras, março, R$ 2.575,9 mi (Portal: R$ 2.575.850.686,50 em
  20/03/2024); Petrobras, fevereiro, R$ 2.553,3 mi; Banco do Brasil, junho, R$ 1.897,4 mi; Banco do Brasil, dezembro,
  R$ 1.890,6 mi; outorgas das autorizações de apostas de quota fixa, R$ 1,8 bilhão em dezembro (várias empresas);
  Programa Desenrola Agências, R$ 1,7 bilhão em dezembro (RTN de dezembro, Nota 4).
- **Atualização de bens e direitos no exterior (Lei nº 14.754/2023):** o RTN de maio de 2024 diz que o IRPF cresceu
  "R$ 7,1 bilhões, resultado da atualização de bens e direitos no exterior". É uma variação contra maio de 2023, não o
  valor recolhido; o Tesouro não publica o total recolhido. Não entrou.
- **Recolhimentos atípicos de Cofins** "da ordem de R$ 2,0 bilhões em junho de 2024" (RTN de junho): sem ato nem pagador.
- **Atos de 2024:** exposições de motivos de todas as MPs de 2024 que não abrem crédito extraordinário foram lidas; só a
  MP 1.227 e a MP 1.262 fixam receita nova em reais. A Lei nº 14.973/2024 (desoneração da folha com medidas de
  compensação) veio do PL nº 1.847/2024, do senador Efraim Filho (API do Senado), sem exposição de motivos do Executivo; o valor de cada medida não está no
  texto da lei. Ela entra aqui só pelo recebimento dos depósitos judiciais, que o Tesouro mediu.

## 2023

| # | Movimento | Data | Valor oficial | Natureza | Fonte do valor |
|---|---|---|---|---|---|
| 1 | Novo tratamento tributário das subvenções do ICMS (MP nº 1.185/2023) | 30/08/2023 (ato) | R$ 35,3 bi | expected_revenue | Exposição de Motivos da MP nº 1.185/2023 |
| 2 | Recursos não sacados do PIS/Pasep incorporados pela União | 04/09/2023 | R$ 26,0 bi | paid | RTN de setembro de 2023 |
| 3 | Tributação periódica dos fundos de investimento fechados (MP nº 1.184/2023) | 28/08/2023 (ato) | R$ 13.280,0 mi | expected_revenue | Exposição de Motivos EM nº 00104/2023 MF |
| 4 | Dividendos e participações pagos pelo BNDES à União em maio de 2023 | 26/05/2023 | R$ 10.425,1 mi | paid | RTN de maio de 2023 |
| 5 | Tributação de aplicações financeiras, empresas e trusts no exterior (Lei nº 14.754/2023) | 12/12/2023 (ato) | R$ 7.050,0 mi | expected_revenue | Exposição de Motivos EM nº 00105/2023 MF |
| 6 | Imposto de exportação sobre petróleo bruto (MP nº 1.163/2023) | 28/02/2023 (ato) | R$ 6.650,0 mi | expected_revenue | Exposição de Motivos EM nº 00026/2023 MF |
| 7 | Dividendos e participações pagos pela Petrobras à União em janeiro de 2023 | 19/01/2023 | R$ 6.307,9 mi | paid | RTN de janeiro de 2023 |
| 8 | Revogação do benefício fiscal do setor de eventos, o Perse (MP nº 1.202/2023) | 28/12/2023 (ato) | R$ 6.010,0 mi | expected_revenue | Exposição de Motivos EM nº 00175/2023 MF |
| 9 | Dividendos e participações pagos pela Petrobras à União em maio de 2023 | 19/05/2023 | R$ 5.388,9 mi | paid | RTN de maio de 2023 |
| 10 | Dividendos e participações pagos pela Petrobras à União em dezembro de 2023 | dezembro de 2023 | R$ 4.253,6 mi | paid | RTN de dezembro de 2023 |

### Itens e trechos lidos

1. **Novo tratamento tributário das subvenções do ICMS (MP nº 1.185/2023)**: R$ 35,3 bi (expected_revenue).
   - Fonte: Exposição de Motivos da MP nº 1.185/2023, de 29/08/2023, item 21, https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/exm/exm-1185-23.pdf (publicado em 2023-08-29).
   - Trecho lido: "cabe informar que a medida tem potencial de arrecadação da ordem de R$ 35,3 bilhões (trinta e cinco bilhões e trezentos milhões de reais) em 2024, R$ 32,4 bilhões (trinta e dois bilhões e quatrocentos milhões de reais) em 2025, R$ 34,1 bilhões (trinta e quatro bilhões e cem milhões de reais) em 2026 e R$ 36,1 bilhões (trinta e seis bilhões e cem milhões de reais) em 2027."
   - Situação: Convertida na Lei nº 14.789, de 29/12/2023 (Planalto). Os valores são os da exposição de motivos da MP; a lei de conversão não refez a estimativa.
2. **Recursos não sacados do PIS/Pasep incorporados pela União**: R$ 26,0 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de setembro de 2023, Nota 6 do resultado mês contra mês (Demais Receitas), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/48173_1514993/boletim_set23.pdf (publicado em 2023-10-27).
   - Trecho lido: "explicado pela entrada de recursos não sacados do PIS/PASEP (conforme previsto na Emenda Constitucional nº 126/2022), no montante de R$ 26,0 bilhões, em setembro de 2023, sem contrapartida em setembro de 2022."
   - Situação: Recebido pela União em 04/09/2023 (Portal da Transparência, receitas de 2023: R$ 25.987.585.222,01 na natureza 'REC.PIS/PASEP NAO RECL.SUP.20 ANOS' nessa data). A entrada foi prevista na Emenda Constitucional nº 126/2022.
3. **Tributação periódica dos fundos de investimento fechados (MP nº 1.184/2023)**: R$ 13.280,0 mi (expected_revenue).
   - Fonte: Exposição de Motivos EM nº 00104/2023 MF, de 24/08/2023, item 40, https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/exm/exm-1184-23.pdf (publicado em 2023-08-24).
   - Trecho lido: "a medida proporcionará impacto orçamentário-financeiro positivo estimado da ordem de R$ 3,21 bilhões para o ano de 2023, de R$ 13,28 bilhões para o ano de 2024, de R$ 3,51 bilhões para o ano de 2025 e de aproximadamente R$ 3,86 bilhões para o ano de 2026."
   - Situação: A MP perdeu a vigência em 04/02/2024 (Ato Declaratório nº 6/2024 do Presidente da Mesa do Congresso Nacional). A tributação dos fundos fechados foi aprovada na Lei nº 14.754/2023, que também tem item próprio nesta lista; em janeiro de 2024 o Tesouro registrou R$ 4,1 bilhões da opção de pagamento antecipado prevista no art. 28 dessa lei.
4. **Dividendos e participações pagos pelo BNDES à União em maio de 2023**: R$ 10.425,1 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2023, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/47344_1471837/boletim_mai23.pdf (publicado em 2023-06-29).
   - Trecho lido: "1.4.2.3 BNDES 0,0 10.425,1 (Maio 2022, Maio 2023, em R$ milhões)"
   - Situação: Recebido pela União em 26/05/2023 (Portal da Transparência, receitas de 2023: dividendos de R$ 7.058.261.957,24 e juros sobre o capital próprio de R$ 3.366.799.207,29 nessa data, soma igual ao valor do Tesouro); atribuído ao BNDES pelo Tesouro Nacional (RTN de maio de 2023, Nota 4: 'dividendos e juros sobre o capital próprio do BNDES, no valor de R$ 10,4 bilhões').
5. **Tributação de aplicações financeiras, empresas e trusts no exterior (Lei nº 14.754/2023)**: R$ 7.050,0 mi (expected_revenue).
   - Fonte: Exposição de Motivos EM nº 00105/2023 MF, de 24/08/2023, do Projeto de Lei nº 4.173/2023 (convertido na Lei nº 14.754/2023), item 42, https://www.planalto.gov.br/ccivil_03/Projetos/Ato_2023_2026/2023/PL/Exm/105-2023-MF.htm (publicado em 2023-08-24).
   - Trecho lido: "a medida proporcionará impacto orçamentário-financeiro positivo potencial para a União, cuja estimativa é da ordem de R$ 7,05 bilhões para o ano de 2024, próximo à R$ 6,75 bilhões para o ano de 2025 e de R$ 7,13 bilhões para o ano de 2026."
   - Situação: Lei em vigor, publicada no Diário Oficial da União de 13/12/2023. O valor é o da exposição de motivos do projeto enviado pelo Executivo (aplicações e entidades no exterior); a lei também incorporou a tributação dos fundos fechados da MP nº 1.184/2023, que tem item próprio.
6. **Imposto de exportação sobre petróleo bruto (MP nº 1.163/2023)**: R$ 6.650,0 mi (expected_revenue).
   - Fonte: Exposição de Motivos EM nº 00026/2023 MF, de 28/02/2023, item 8, https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/exm/exm-1163-23.pdf (publicado em 2023-02-28).
   - Trecho lido: "Ademais, a medida ora proposta eleva a alíquota do imposto de exportação incidente sobre as exportações de óleos brutos de petróleo ou de minerais betuminosos, classificado no código 2709 da Nomenclatura Comum do Mercosul (...), cujo impacto financeiro positivo, nos termos da Nota Cetad/Coest nº 025, de 28 de fevereiro de 2023, é da ordem de R$ 6,65 bilhões (seis bilhões, seiscentos e cinquenta milhões de reais)."
   - Situação: A MP perdeu a vigência em 28/06/2023 (Ato Declaratório nº 47/2023 do Presidente da Mesa do Congresso Nacional). O RTN de setembro de 2023 registra o 'fim da vigência da Medida Provisória nº 1.163/2023, que havia estabelecido até 30 de junho de 2023 a cobrança do imposto de exportação'. A mesma MP manteve reduzidos tributos sobre combustíveis, com renúncia estimada em R$ 6,61 bilhões (lado da saída).
7. **Dividendos e participações pagos pela Petrobras à União em janeiro de 2023**: R$ 6.307,9 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de janeiro de 2023, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/46286_1495495/boletim_jan23.pdf (publicado em 2023-02-27).
   - Trecho lido: "1.4.2.8 Petrobras 0,0 6.307,9 (Janeiro 2022, Janeiro 2023, em R$ milhões)"
   - Situação: Recebido pela União em 19/01/2023 (Portal da Transparência, receitas de 2023: dividendos de R$ 6.030.147.651,34 e juros sobre o capital próprio de R$ 277.759.881,48 nessa data, soma igual ao valor do Tesouro); atribuído à Petrobras pelo Tesouro Nacional (RTN de janeiro de 2023, Nota 5).
8. **Revogação do benefício fiscal do setor de eventos, o Perse (MP nº 1.202/2023)**: R$ 6.010,0 mi (expected_revenue).
   - Fonte: Exposição de Motivos EM nº 00175/2023 MF, de 27/12/2023, item 52.1, https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/exm/exm-1202-23.pdf (publicado em 2023-12-27).
   - Trecho lido: "impacto positivo da ordem de R$ 6,01 bilhões (seis bilhões e 10 milhões de reais) em 2024 em relação à revogação do art. 4º da Lei nº 14.148, de 2021, que reduz a 0% (zero por cento) as alíquotas do IRPJ, da CSLL, da Contribuição para o PIS/Pasep e da Cofins, incidentes sobre o resultado auferido pelas pessoas jurídicas pertencentes ao setor de eventos (PERSE)"
   - Situação: Convertida na Lei nº 14.873/2024 (Planalto), que tratou do limite à compensação de créditos judiciais. O Perse voltou a ter alíquotas reduzidas pela Lei nº 14.859/2024, que revogou dispositivo da MP. A mesma exposição estima impacto negativo de R$ 5,62 bilhões em 2024 com a desoneração parcial da folha (lado da saída).
9. **Dividendos e participações pagos pela Petrobras à União em maio de 2023**: R$ 5.388,9 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2023, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/47344_1471837/boletim_mai23.pdf (publicado em 2023-06-29).
   - Trecho lido: "1.4.2.8 Petrobras 11.110,1 5.388,9 (Maio 2022, Maio 2023, em R$ milhões)"
   - Situação: Pago pela Petrobras em 19/05/2023, 1ª parcela dos dividendos do 4º trimestre de 2022 (https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/); atribuído à Petrobras pelo Tesouro Nacional. No Portal da Transparência, a entrada de dividendos de 19/05/2023 é de R$ 5.460.068.801,03, um pouco acima do valor do Tesouro.
10. **Dividendos e participações pagos pela Petrobras à União em dezembro de 2023**: R$ 4.253,6 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2023, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/48787_1551088/boletim_dez23.pdf (publicado em 2024-01-29).
   - Trecho lido: "1.4.2.8 Petrobras 6.230,2 4.253,6 (Dezembro 2022, Dezembro 2023, em R$ milhões)"
   - Situação: Recebido pela União em dezembro de 2023; a Petrobras informa pagamentos em 15/12/2023 (2ª parcela dos dividendos do 2º trimestre de 2023) e em 27/12/2023 (4ª parcela dos dividendos do 4º trimestre de 2022) (https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/). No Portal da Transparência, as entradas de dividendos dessas datas (R$ 2.149.469.032,48 e R$ 2.125.231.524,68) somam um pouco mais que o valor do Tesouro.

### Também conferido em 2023

- **Logo abaixo do corte:** MP nº 1.171/2023 (30/04/2023; tributação de aplicações e entidades no exterior e tabela do
  IRPF; perdeu a vigência em 27/08/2023, Ato Declaratório nº 62/2023), cuja exposição de motivos diz que "as medidas
  estabelecidas no Título I têm potencial de arrecadação da ordem de R$ 3,25 bilhões para o ano de 2023, próximo a
  R$ 3,59 bilhões para o ano de 2024 e de R$ 6,75 bilhões para o ano de 2025"; Petrobras, setembro, R$ 3.541,4 mi
  (Portal: R$ 3.541.436.618,67 em 20/09/2023); Petrobras, agosto, R$ 3.540,4 mi (Portal: R$ 1.039.520.429,73 mais
  R$ 2.500.912.448,47 em 18/08/2023); Petrobras, junho, R$ 3.467,2 mi (Portal: R$ 3.467.152.065,31 em 16/06/2023);
  Caixa, julho, R$ 1,8 bilhão (RTN de julho de 2023, Nota 6); MP nº 1.175/2023, com aumento de PIS/Pasep e Cofins sobre
  diesel e biodiesel "estimado em R$ 1,6 bilhão ... para o ano de 2023".
- **Imposto de exportação de petróleo cobrado de março a junho de 2023 (MP 1.163):** o RTN cita o imposto em maio, junho
  e julho, sem dar o valor; no Portal da Transparência o Imposto sobre a Exportação somou R$ 1.020,0 mi em maio,
  R$ 1.455,4 mi em junho e R$ 1.071,7 mi em julho de 2023 (todos os produtos). Cada mês fica abaixo do corte; o ato
  entrou como receita esperada.
- **Voto de qualidade no Carf (MP nº 1.160/2023 e Lei nº 14.689/2023):** as exposições de motivos dizem que "cerca de
  R$ 59 bilhões ... por ano, deixarão de ser exigidos" com a regra antiga. É valor de créditos em disputa, não receita
  esperada; não entrou.
- **Apostas de quota fixa (MP nº 1.182/2023 e Lei nº 14.790/2023):** as exposições de motivos não trazem estimativa de
  arrecadação em reais (só o custo de cargos, R$ 3,5 milhões em 2023). Não entrou.
- **Programa de redução de litigiosidade ("Litígio Zero"):** o RTN de setembro de 2023 cita reclassificação de "cerca
  de R$ 4,8 bilhões" entre rubricas, "sem qualquer efeito sobre o resultado primário"; não é entrada nova.
- **Atos de 2023 lidos:** exposições de motivos de todas as MPs de 2023 que não abrem crédito extraordinário, mais as dos
  projetos de lei do Executivo que viraram as Leis nº 14.754, 14.689 e 14.790.

## 2022

| # | Movimento | Data | Valor oficial | Natureza | Fonte do valor |
|---|---|---|---|---|---|
| 1 | Bônus de outorga dos novos contratos de geração da Eletrobras (desestatização) | 20/06/2022 | R$ 26,6 bi | paid | RTN de junho de 2022 |
| 2 | Dividendos e participações pagos pelo BNDES à União em junho de 2022 | 30/06/2022 | R$ 18.878,6 mi | paid | RTN de junho de 2022 |
| 3 | Dividendos e participações pagos pela Petrobras à União em setembro de 2022 | 20/09/2022 | R$ 12.590,4 mi | paid | RTN de setembro de 2022 |
| 4 | Dividendos e participações pagos pela Petrobras à União em agosto de 2022 | 31/08/2022 | R$ 12.550,4 mi | paid | RTN de agosto de 2022 |
| 5 | Bônus de assinatura da segunda rodada da cessão onerosa (campos de Sépia e Atapu) | fevereiro de 2022 | R$ 11,2 bi | paid | RTN de fevereiro de 2022 |
| 6 | Dividendos e participações pagos pela Petrobras à União em maio de 2022 | maio de 2022 | R$ 11.110,1 mi | paid | RTN de maio de 2022 |
| 7 | Dividendos e participações pagos pela Petrobras à União em junho de 2022 | 20/06/2022 | R$ 6.948,8 mi | paid | RTN de junho de 2022 |
| 8 | Dividendos e participações pagos pela Petrobras à União em julho de 2022 | 20/07/2022 | R$ 6.943,8 mi | paid | RTN de julho de 2022 |
| 9 | Dividendos e participações pagos pela Petrobras à União em dezembro de 2022 | 20/12/2022 | R$ 6.230,2 mi | paid | RTN de dezembro de 2022 |
| 10 | Dividendos e participações pagos pela Caixa Econômica Federal à União em fevereiro de 2022 | fevereiro de 2022 | R$ 3.591,4 mi | paid | RTN de fevereiro de 2022 |

### Itens e trechos lidos

1. **Bônus de outorga dos novos contratos de geração da Eletrobras (desestatização)**: R$ 26,6 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2022, Nota 5 do resultado mês contra mês (Concessões e Permissões), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/44179_1398982/boletim_jun22.pdf (publicado em 2022-07-28).
   - Trecho lido: "desempenho explicado pelo recebimento de R$ R$ 26,6 bilhões, repassados à União em junho de 2022, referentes ao bônus de outorga dos novos contratos de concessão de geração de energia elétrica advindos da desestatização da Centrais Elétricas Brasileiras S/A (Eletrobras)."
   - Situação: Recebido pela União em 20/06/2022 (Portal da Transparência, receitas de 2022: R$ 26.635.960.067,14 na natureza 'CONC.SERV.GER.TRANSM.DISTR.ENER.ELET', unidade ANEEL, nessa data).
2. **Dividendos e participações pagos pelo BNDES à União em junho de 2022**: R$ 18.878,6 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2022, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/44179_1398982/boletim_jun22.pdf (publicado em 2022-07-28).
   - Trecho lido: "1.4.2.3 BNDES 0,0 18.878,6 (Junho 2021, Junho 2022, em R$ milhões)"
   - Situação: Recebido pela União em 30/06/2022: no Portal da Transparência (receitas de 2022), as entradas dessa data (dividendos de R$ 15.499.767.875,29 e juros sobre o capital próprio de R$ 3.737.422.191,43) somam o valor do BNDES mais os R$ 358,6 milhões do Banco do Brasil da mesma tabela do Tesouro; atribuído ao BNDES pelo Tesouro Nacional (RTN de junho de 2022, Nota 6).
3. **Dividendos e participações pagos pela Petrobras à União em setembro de 2022**: R$ 12.590,4 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de setembro de 2022, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/45087_1498358/boletim_set22.pdf (publicado em 2022-10-27).
   - Trecho lido: "1.4.2.8 Petrobras 0,0 12.590,4 (Setembro 2021, Setembro 2022, em R$ milhões)"
   - Situação: Recebido pela União em 20/09/2022 (Portal da Transparência, receitas de 2022: dividendos de R$ 12.590.428.490,29 nessa data, igual ao valor do Tesouro).
4. **Dividendos e participações pagos pela Petrobras à União em agosto de 2022**: R$ 12.550,4 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de agosto de 2022, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/44839_1419442/boletim_ago22.pdf (publicado em 2022-09-29).
   - Trecho lido: "1.4.2.8 Petrobras 6.020,6 12.550,4 (Agosto 2021, Agosto 2022, em R$ milhões)"
   - Situação: Recebido pela União em 31/08/2022: no Portal da Transparência (receitas de 2022), as entradas dessa data (dividendos de R$ 11.245.887.783,82 e juros sobre o capital próprio de R$ 2.433.430.591,00) somam o valor da Petrobras mais os R$ 1.128,9 milhões do Banco do Brasil da mesma tabela do Tesouro.
5. **Bônus de assinatura da segunda rodada da cessão onerosa (campos de Sépia e Atapu)**: R$ 11,2 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de fevereiro de 2022, Nota 5 do resultado mês contra mês (Concessões e Permissões), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/43146_1460239/RTN_Boletim_2022_02.pdf (publicado em 2022-03-30).
   - Trecho lido: "desempenho explicado pelo recebimento de recursos de bônus de assinatura relativos a segunda rodada da cessão onerosa (Campos de Sépia e Atapu (...) no montante de R$ 11,2 bilhões)."
   - Situação: Recebido em fevereiro de 2022 (Concessões e Permissões somou R$ 11.356,0 milhões no mês, Tabela do RTN). No Portal da Transparência, os bônus de assinatura de partilha de fevereiro de 2022 aparecem em lançamentos de 02, 16, 17 e 18/02/2022, divididos entre naturezas da União e de estados e municípios de um modo que não permite somar a parte da União; o valor do item é o do Tesouro.
6. **Dividendos e participações pagos pela Petrobras à União em maio de 2022**: R$ 11.110,1 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2022, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/43920_2193378/boletim_mai22.pdf (publicado em 2022-06-29).
   - Trecho lido: "1.4.2.8 Petrobras 0,0 11.110,1 (Maio 2021, Maio 2022, em R$ milhões)"
   - Situação: Recebido pela União em maio de 2022; atribuído à Petrobras pelo Tesouro Nacional (RTN de maio de 2022, Nota 5: 'recebimento de R$ 11,1 bilhões (Petrobrás) em maio de 2022'). No Portal da Transparência, a entrada de dividendos de 16/05/2022 é de R$ 11.360.833.147,05, acima do valor do Tesouro, e não nomeia o pagador.
7. **Dividendos e participações pagos pela Petrobras à União em junho de 2022**: R$ 6.948,8 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2022, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/44179_1398982/boletim_jun22.pdf (publicado em 2022-07-28).
   - Trecho lido: "1.4.2.8 Petrobras 0,0 6.948,8 (Junho 2021, Junho 2022, em R$ milhões)"
   - Situação: Recebido pela União em 20/06/2022 (Portal da Transparência, receitas de 2022: dividendos de R$ 5.339.776.434,71 e juros sobre o capital próprio de R$ 1.609.089.415,02 nessa data, soma igual ao valor do Tesouro).
8. **Dividendos e participações pagos pela Petrobras à União em julho de 2022**: R$ 6.943,8 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de julho de 2022, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/44555_2176239/boletim_jul22.pdf (publicado em 2022-08-30).
   - Trecho lido: "1.4.2.8 Petrobras 0,0 6.943,8 (Julho 2021, Julho 2022, em R$ milhões)"
   - Situação: Recebido pela União em 20/07/2022 (Portal da Transparência, receitas de 2022: dividendos de R$ 6.943.840.946,78 nessa data, igual ao valor do Tesouro).
9. **Dividendos e participações pagos pela Petrobras à União em dezembro de 2022**: R$ 6.230,2 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2022, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/46073_1449893/boletim_dez22.pdf (publicado em 2023-01-27).
   - Trecho lido: "1.4.2.8 Petrobras 12.158,2 6.230,2 (Dezembro 2021, Dezembro 2022, em R$ milhões)"
   - Situação: Recebido pela União em 20/12/2022 (Portal da Transparência, receitas de 2022: dividendos de R$ 4.290.373.892,02 e juros sobre o capital próprio de R$ 1.939.909.155,29 nessa data, soma igual ao valor do Tesouro).
10. **Dividendos e participações pagos pela Caixa Econômica Federal à União em fevereiro de 2022**: R$ 3.591,4 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de fevereiro de 2022, Tabela 3.1, linha 1.4.2.4 Caixa (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/43146_1460239/RTN_Boletim_2022_02.pdf (publicado em 2022-03-30).
   - Trecho lido: "1.4.2.4 Caixa 0,0 3.591,4 (Fevereiro 2021, Fevereiro 2022, em R$ milhões)"
   - Situação: Recebido pela União em fevereiro de 2022; atribuído à Caixa pelo Tesouro Nacional (RTN de fevereiro de 2022, Nota 6: 'recebimento de R$ 3,6 bilhões de dividendos da Caixa Econômica Federal'). No Portal da Transparência, a maior entrada do mês é de juros sobre o capital próprio de R$ 3.528.318.855,72 em 24/02/2022; o Portal não nomeia o pagador.

### Também conferido em 2022

- **Logo abaixo do corte:** outorga ligada à desestatização da CEEE-GT, R$ 2,0 bilhões (RTN de dezembro de 2023, Nota 5,
  sobre 2022; Portal: R$ 2.051.016.278,51 em 08/12/2022); Banco do Brasil, novembro, R$ 1.152,9 mi, e agosto, R$ 1.128,9
  mi.
- **Atos de 2022:** exposições de motivos de todas as MPs de 2022 que não abrem crédito extraordinário foram lidas. A MP
  nº 1.115/2022 (CSLL de bancos a 21% até 31/12/2022) estima "aumento de arrecadação estimado em R$ 244.110.000,00 ...
  para o ano de 2022", abaixo do corte. A MP nº 1.128/2022 (perdas no recebimento de créditos de instituições
  financeiras) prevê aumento de R$ 17,9 bilhões em 2025 e R$ 11,6 bilhões em 2026 seguido de redução de R$ 23,1 bilhões
  em 2027 e R$ 6,3 bilhões em 2028: é efeito de calendário, não receita nova; não entrou. Em 2022 os atos tributários
  foram, na maior parte, reduções (renúncia, lado da saída).
- **Recolhimentos atípicos de IRPJ e CSLL** "da ordem de R$ 6,0 bilhões em junho de 2022" e "de R$ 4,0 bilhões em julho
  de 2022", "especialmente por empresas ligadas ao setor de commodities" (RTN de junho e de julho): sem ato nem pagador
  identificado; fora da regra.
- **Boletim de março de 2022:** a página do Tesouro Transparente responde "não encontrado" (404) em
  `/2022/3` e `/2022/3-2`. A série histórica do RTN não mostra item grande em março de 2022 (Concessões R$ 202 mi;
  dividendos só do Banco do Brasil, R$ 1.483 mi na série histórica, abaixo do corte).

## 2021

| # | Movimento | Data | Valor oficial | Natureza | Fonte do valor |
|---|---|---|---|---|---|
| 1 | Dividendos e participações pagos pela Petrobras à União em dezembro de 2021 | 15/12/2021 | R$ 12.158,2 mi | paid | RTN de dezembro de 2021 |
| 2 | Dividendos e participações pagos pelo BNDES à União em novembro de 2021 | 17/11/2021 | R$ 8.616,2 mi | paid | RTN de novembro de 2021 |
| 3 | Devolução à União de recursos do Pronampe | junho de 2021 | R$ 6,3 bi | paid | RTN de junho de 2021 |
| 4 | Dividendos e participações pagos pela Petrobras à União em agosto de 2021 | agosto de 2021 | R$ 6.020,6 mi | paid | RTN de agosto de 2021 |
| 5 | Dividendos e participações pagos pelo BNDES à União em maio de 2021 | 10/05/2021 | R$ 4.949,2 mi | paid | RTN de maio de 2021 |
| 6 | Aumento da CSLL dos bancos, limite à isenção de IPI e mudanças no REIQ (MP nº 1.034/2021) | 01/03/2021 (ato) | R$ 3.689,2 mi | expected_revenue | Exposição de Motivos EM nº 00041/2021 ME |
| 7 | Dividendos e participações pagos pela Petrobras à União em abril de 2021 | 29/04/2021 | R$ 2.965,0 mi | paid | RTN de abril de 2021 |
| 8 | Dividendos e participações pagos pela Caixa Econômica Federal à União em maio de 2021 | 14/05/2021 | R$ 2.816,2 mi | paid | RTN de maio de 2021 |
| 9 | Outorga do Bloco Sul da 6ª rodada de concessões de aeroportos | 27/10/2021 | R$ 2.190,0 mi | paid | RTN de outubro de 2021 |
| 10 | Dividendos e participações pagos pela Eletrobras à União em fevereiro de 2021 | 19/02/2021 | R$ 958,5 mi | paid | RTN de fevereiro de 2021 |

### Itens e trechos lidos

1. **Dividendos e participações pagos pela Petrobras à União em dezembro de 2021**: R$ 12.158,2 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2021, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/42576_1431436/RTN_Boletim_2021_12.pdf (publicado em 2022-01-28).
   - Trecho lido: "1.4.2.8 Petrobras 897,3 12.158,2 (Dezembro 2020, Dezembro 2021, em R$ milhões)"
   - Situação: Recebido pela União em 15/12/2021 (Portal da Transparência, receitas de 2021: dividendos de R$ 8.210.676.485,61 e juros sobre o capital próprio de R$ 3.947.547.015,56 nessa data, soma igual ao valor do Tesouro); atribuído à Petrobras pelo Tesouro Nacional (RTN de dezembro de 2021, Nota 5).
2. **Dividendos e participações pagos pelo BNDES à União em novembro de 2021**: R$ 8.616,2 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de novembro de 2021, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/42331_1387131/RTN_Boletim_2021_11.pdf (publicado em 2021-12-29).
   - Trecho lido: "1.4.2.3 BNDES 0,0 8.616,2 (Novembro 2020, Novembro 2021, em R$ milhões)"
   - Situação: Recebido pela União em 17/11/2021 (Portal da Transparência, receitas de 2021: dividendos de R$ 4.718.282.694,07 e juros sobre o capital próprio de R$ 3.897.882.930,58 nessa data, soma igual ao valor do Tesouro); atribuído ao BNDES pelo Tesouro Nacional (RTN de novembro de 2021, Nota 7: 'pagamento de R$ 8.616,2 milhões pelo BNDES').
3. **Devolução à União de recursos do Pronampe**: R$ 6,3 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2021, Nota 9 do resultado mês contra mês (Demais Receitas Não Administradas pela RFB), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/40424_1257203/boletim_jun21_.pdf (publicado em 2021-07-29).
   - Trecho lido: "influenciada pela devolução de R$ 6,3 bilhões relativa ao Pronampe (Programa Nacional de Apoio às Microempresas e Empresas de Pequeno Porte"
   - Situação: Recebido em junho de 2021, segundo o Tesouro Nacional. O RTN de junho de 2022 (Nota 8) cita a mesma devolução como 'R$ 6,9 bilhões de recursos do Programa Nacional de Apoio às Microempresas e Empresas de Pequeno Porte (PRONAMPE)', em valores atualizados. O Portal da Transparência não traz linha identificada como Pronampe.
4. **Dividendos e participações pagos pela Petrobras à União em agosto de 2021**: R$ 6.020,6 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de agosto de 2021, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/41583_1378048/Boletim_ago21.pdf (publicado em 2021-09-28).
   - Trecho lido: "1.4.2.8 Petrobras 0,0 6.020,6 (Agosto 2020, Agosto 2021, em R$ milhões)"
   - Situação: Recebido pela União em agosto de 2021; atribuído à Petrobras pelo Tesouro Nacional. O Portal da Transparência não mostra entrada de dividendos ou juros sobre o capital próprio desse valor no mês (as duas naturezas somam R$ 1.185,1 milhões em agosto de 2021); o dia não foi confirmado.
5. **Dividendos e participações pagos pelo BNDES à União em maio de 2021**: R$ 4.949,2 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2021, Tabela 3.1, linha 1.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/39791_1308277/RTN_Boletim_2021_05.pdf (publicado em 2021-06-29).
   - Trecho lido: "1.4.2.3 BNDES 0,0 4.949,2 (Maio 2020, Maio 2021, em R$ milhões)"
   - Situação: Recebido pela União em 10/05/2021 (Portal da Transparência, receitas de 2021: juros sobre o capital próprio de R$ 3.210.973.571,01 e dividendos de R$ 1.738.225.291,46 nessa data, soma igual ao valor do Tesouro); atribuído ao BNDES pelo Tesouro Nacional (RTN de maio de 2021, Nota 7).
6. **Aumento da CSLL dos bancos, limite à isenção de IPI e mudanças no REIQ (MP nº 1.034/2021)**: R$ 3.689,2 mi (expected_revenue).
   - Fonte: Exposição de Motivos EM nº 00041/2021 ME, de 26/02/2021, item 8; valor = soma, feita nesta pesquisa, das três estimativas para 2021, único ano em que as três medidas valem juntas (a exposição não traz total), https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/exm/exm-mp-1034-21.pdf (publicado em 2021-02-26).
   - Trecho lido: "proporcionarão aumento de arrecadação nos seguintes montantes: (...) a) R$ 2.271,55 milhões (dois bilhões e duzentos e setenta e um milhões e quinhentos e cinquenta mil reais) para o ano de 2021, no caso da majoração da alíquota de CSLL; (...) b) R$ 750,00 milhões (setecentos e cinquenta milhões de reais) para o ano de 2021, no caso de isenção de IPI para automóvel adquirido por pessoa acometida por deficiência física; (...) c) R$ 667,62 milhões (seiscentos e sessenta e sete milhões e seiscentos e vinte mil reais) para o ano de 2021, R$ 1.432,73 milhões (um bilhão e quatrocentos e trinta e dois milhões e setecentos e trinta mil reais) para 2022 e R$ 1.529,73 milhões (um bilhão e quinhentos e vinte e nove milhões e setecentos e trinta mil reais) para 2023, no caso do REIQ."
   - Situação: Convertida na Lei nº 14.183, de 14/07/2021 (Planalto). A exposição de motivos apresenta as três medidas como compensação de renúncias de receita de um decreto editado na mesma ocasião (lado da saída).
7. **Dividendos e participações pagos pela Petrobras à União em abril de 2021**: R$ 2.965,0 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de abril de 2021, Tabela 3.1, linha 1.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/39278_1230382/RTN_Boletim_2021_04.pdf (publicado em 2021-05-27).
   - Trecho lido: "1.4.2.8 Petrobras 0,0 2.965,0 (Abril 2020, Abril 2021, em R$ milhões)"
   - Situação: Recebido pela União em 29/04/2021 (Portal da Transparência, receitas de 2021: dividendos de R$ 2.965.046.960,53 nessa data, igual ao valor do Tesouro); atribuído à Petrobras pelo Tesouro Nacional (RTN de abril de 2021, Nota 8).
8. **Dividendos e participações pagos pela Caixa Econômica Federal à União em maio de 2021**: R$ 2.816,2 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2021, Tabela 3.1, linha 1.4.2.4 Caixa (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/39791_1308277/RTN_Boletim_2021_05.pdf (publicado em 2021-06-29).
   - Trecho lido: "1.4.2.4 Caixa 1.008,0 2.816,2 (Maio 2020, Maio 2021, em R$ milhões)"
   - Situação: Recebido pela União em 14/05/2021 (Portal da Transparência, receitas de 2021: juros sobre o capital próprio de R$ 2.816.147.598,81 nessa data, igual ao valor do Tesouro); atribuído à Caixa pelo Tesouro Nacional.
9. **Outorga do Bloco Sul da 6ª rodada de concessões de aeroportos**: R$ 2.190,0 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de outubro de 2021, Nota 6 do resultado mês contra mês (Concessões e Permissões), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/42128_1307599/RTN_Boletim_2021_10.pdf (publicado em 2021-11-29).
   - Trecho lido: "em outubro de 2021 houve pagamento de outorga da 6ª Rodada de Concessões Aeroportuárias, relativos aos Blocos Central e Sul, no valor de R$ 778,3 milhões e R$ 2,19 bilhões, respectivamente."
   - Situação: Recebido em 27/10/2021 (Portal da Transparência, receitas de 2021: R$ 2.196.688.936,48 na natureza 'DELEG.P/EXPLOR.INFRAEST.AEROPORTUARIA', Fundo Nacional de Aviação Civil, nessa data). O Bloco Central pagou R$ 778,3 milhões no mesmo mês.
10. **Dividendos e participações pagos pela Eletrobras à União em fevereiro de 2021**: R$ 958,5 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de fevereiro de 2021, Tabela 3.1, linha 1.4.2.6 Eletrobrás (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/38234_1200446/RTN_Boletim_2021_02.pdf (publicado em 2021-03-30).
   - Trecho lido: "1.4.2.6 Eletrobrás 0,0 958,5 (Fevereiro 2020, Fevereiro 2021, em R$ milhões)"
   - Situação: Recebido pela União em 19/02/2021 (Portal da Transparência, receitas de 2021: dividendos de R$ 958.507.907,49 nessa data, igual ao valor do Tesouro). A desestatização da Eletrobras só ocorreu em 2022 (RTN de junho de 2022, Nota 5).

### Também conferido em 2021

- **Logo abaixo do corte:** Banco do Brasil, março, R$ 833,2 mi; outorga do Bloco Central da 6ª rodada de aeroportos,
  R$ 778,3 mi (mesma nota do item do Bloco Sul); Eletrobras, agosto, R$ 642,1 mi (Portal: R$ 642.053.021,28 em
  31/08/2021).
- **Concessões de dezembro de 2021:** o RTN de dezembro (Nota 4) explica a alta de Concessões e Permissões pelas
  "concessão de 5G e novas concessões de transportes terrestres", sem valor de cada uma. No Portal, há R$ 405.000.000,00
  e R$ 450.000.000,00 de delegação de serviços de telecomunicações em 22/12/2021 e R$ 1.018.442.187,56 de delegação de
  transporte rodoviário em 28/12/2021, sem nome do contrato. Sem valor do Tesouro por evento; não entraram.
- **Restituições de despesas de exercícios anteriores** de R$ 2,3 bilhões (janeiro) e R$ 2,5 bilhões (março) citadas pelo
  RTN: devoluções sem origem identificada; não entraram.
- **Decreto nº 10.797/2021 (IOF, 16/09/2021):** aumentou o IOF até o fim de 2021; o Planalto não traz exposição de
  motivos e o texto não fixa valor de receita. Não entrou.
- **Outras MPs de 2021:** a MP nº 1.072/2021 (taxa de fiscalização da CVM) estima "arrecadação de R$ 568 milhões" por ano
  a partir de 2022, abaixo do corte.

## 2020

| # | Movimento | Data | Valor oficial | Natureza | Fonte do valor |
|---|---|---|---|---|---|
| 1 | Devolução à União de recursos do Programa Emergencial de Suporte a Empregos (PESE) | julho de 2020 | R$ 13,1 bi | paid | RTN de julho de 2020 |
| 2 | Pagamento antecipado de outorgas da Malha Paulista e da Ferrovia Norte-Sul | 15/09/2020 | R$ 5,1 bi | paid | RTN de setembro de 2021 |
| 3 | Dividendos e participações pagos pela Eletrobras à União em setembro de 2020 | 09/09/2020 | R$ 1.085,6 mi | paid | Secretaria do Tesouro Nacional |
| 4 | Dividendos e participações pagos pela Caixa Econômica Federal à União em maio de 2020 | maio de 2020 | R$ 1.008,0 mi | paid | RTN de maio de 2020 |
| 5 | Dividendos e participações pagos pela Petrobras à União em dezembro de 2020 | 15/12/2020 | R$ 897,3 mi | paid | RTN de dezembro de 2020 |
| 6 | Dividendos e participações pagos pelo Banco do Brasil à União em março de 2020 | março de 2020 | R$ 888,7 mi | paid | RTN de março de 2020 |
| 7 | Dividendos e participações pagos pela Petrobras à União em fevereiro de 2020 | 07/02/2020 | R$ 751,6 mi | paid | RTN de fevereiro de 2020 |
| 8 | Dividendos e participações pagos pelo Banco do Brasil à União em agosto de 2020 | 31/08/2020 | R$ 633,5 mi | paid | RTN de agosto de 2020 |
| 9 | Dividendos e participações pagos pelo Banco do Brasil à União em novembro de 2020 | 27/11/2020 | R$ 279,1 mi | paid | RTN de novembro de 2020 |
| 10 | Dividendos e participações pagos pelo Banco do Brasil à União em dezembro de 2020 | 30/12/2020 | R$ 167,6 mi | paid | RTN de dezembro de 2020 |

### Itens e trechos lidos

1. **Devolução à União de recursos do Programa Emergencial de Suporte a Empregos (PESE)**: R$ 13,1 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de julho de 2020, Nota 12 do resultado mês contra mês (Subsídios, Subvenções e Proagro), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/34082_1080992/relatorio_jul20.pdf (publicado em 2020-08-28).
   - Trecho lido: "redução explicada, principalmente, pela devolução à União de R$ 13,1 bilhões que haviam sido destinados ao Programa Emergencial de Suporte a Empregos - PESE, instituído pela MP 944/2020, para enfrentamento das consequências econômicas e sociais decorrentes do estado de emergência causado pela pandemia do Coronavírus (Covid-19)."
   - Situação: Recebido em julho de 2020. O Tesouro registrou a devolução como redução da despesa com subsídios do mês, e não como receita; por isso ela não aparece no arquivo de receitas do Portal da Transparência. O RTN de julho de 2021 (Nota 14) cita o mesmo evento como 'devolução à União de R$ 14,3 bilhões (em valores reais)'.
2. **Pagamento antecipado de outorgas da Malha Paulista e da Ferrovia Norte-Sul**: R$ 5,1 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de setembro de 2021, Nota 6 do resultado mês contra mês (Concessões e Permissões), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/41791_1370391/boletim_set21.pdf (publicado em 2021-10-28).
   - Trecho lido: "em setembro de 2020 houve pagamento antecipado de R$ 5,1 bilhões em outorgas referentes aos contratos de concessão da Malha Paulista e da Ferrovia Norte-Sul."
   - Situação: Recebido em 15/09/2020 (Portal da Transparência, receitas de 2020: R$ 5.101.422.676,46 na natureza 'DELEG.P/PREST.SERV.TRANSP.FERROVIARIO', unidade ANTT, nessa data). O valor vem do RTN de setembro de 2021, que compara com setembro de 2020; o RTN de setembro de 2020 (Nota 6) descreve o mesmo pagamento, mas o data como 'setembro de 2019', o que não bate com o Portal nem com a tabela do próprio boletim (Concessões e Permissões: R$ 2.573,9 milhões em setembro de 2019 e R$ 5.321,1 milhões em setembro de 2020).
3. **Dividendos e participações pagos pela Eletrobras à União em setembro de 2020**: R$ 1.085,6 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional, série histórica mensal (arquivo seriehistoricajul26.xlsx), Tabela 1.2, R$ milhões, valores correntes, https://www.tesourotransparente.gov.br/ckan/dataset/ab56485b-9c40-4efb-8563-9ce3e1973c4b/resource/527ccdb1-3059-42f3-bf23-b5e3ab4c6dc6/download/seriehistoricajul26.xlsx (publicado em 2026-08-27).
   - Trecho lido: "Tabela 1.2, linha 1.4.2.6 Eletrobrás, coluna 2020-09: 1.085,6"
   - Situação: Recebido pela União em 09/09/2020 (Portal da Transparência, receitas de 2020: dividendos de R$ 1.085.577.390,95 nessa data, igual ao valor da série). No boletim de setembro de 2020, o valor está na linha 'Demais' (R$ 1.094,2 milhões); a série histórica atual do Tesouro o atribui à Eletrobras.
4. **Dividendos e participações pagos pela Caixa Econômica Federal à União em maio de 2020**: R$ 1.008,0 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2020, Tabela 3.1, linha I.4.2.4 Caixa (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/33440_1806414/relatorio_mai20.pdf (publicado em 2020-06-29).
   - Trecho lido: "I.4.2.4 Caixa 0,0 1.008,0 (Maio 2019, Maio 2020, em R$ milhões)"
   - Situação: Recebido pela União em maio de 2020; atribuído à Caixa pelo Tesouro Nacional. No Portal da Transparência, as entradas de 18/05/2020 (dividendos de R$ 709.959.236,01 e juros sobre o capital próprio de R$ 283.803.843,89) somam R$ 993,8 milhões; o restante não foi localizado nas linhas acima de R$ 50 milhões.
5. **Dividendos e participações pagos pela Petrobras à União em dezembro de 2020**: R$ 897,3 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2020, Tabela 3.1, linha I.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/37105_1940142/RTN_Boletim_2020_12.pdf (publicado em 2021-01-28).
   - Trecho lido: "I.4.2.8 Petrobras 0,0 897,3 (Dezembro 2019, Dezembro 2020, em R$ milhões)"
   - Situação: Recebido pela União em 15/12/2020 (Portal da Transparência, receitas de 2020: dividendos de R$ 897.328.940,48 nessa data, igual ao valor do Tesouro).
6. **Dividendos e participações pagos pelo Banco do Brasil à União em março de 2020**: R$ 888,7 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de março de 2020, Tabela 3.1, linha I.4.2.1 Banco do Brasil (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/32496_1118956/relatorio_mar20.pdf (publicado em 2020-04-29).
   - Trecho lido: "I.4.2.1 Banco do Brasil 1.087,2 888,7 (Março 2019, Março 2020, em R$ milhões)"
   - Situação: Recebido pela União em março de 2020, em duas entradas de juros sobre o capital próprio no Portal da Transparência que somam o valor do Tesouro: 05/03/2020 R$ 628.790.600,77 e 31/03/2020 R$ 259.922.739,34.
7. **Dividendos e participações pagos pela Petrobras à União em fevereiro de 2020**: R$ 751,6 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de fevereiro de 2020, Tabela 3.1, linha I.4.2.8 Petrobras (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/32077_1027817/relatorio_fev20.pdf (publicado em 2020-03-30).
   - Trecho lido: "I.4.2.8 Petrobras 0,0 751,6 (Fevereiro 2019, Fevereiro 2020, em R$ milhões)"
   - Situação: Recebido pela União em 07/02/2020 (Portal da Transparência, receitas de 2020: juros sobre o capital próprio de R$ 751.554.097,70 nessa data, igual ao valor do Tesouro).
8. **Dividendos e participações pagos pelo Banco do Brasil à União em agosto de 2020**: R$ 633,5 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de agosto de 2020, Tabela 3.1, linha I.4.2.1 Banco do Brasil (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/34388_1067659/RTN_Boletim_2020_08.pdf (publicado em 2020-09-29).
   - Trecho lido: "I.4.2.1 Banco do Brasil 648,5 633,5 (Agosto 2019, Agosto 2020, em R$ milhões)"
   - Situação: Recebido pela União em 31/08/2020 (Portal da Transparência, receitas de 2020: juros sobre o capital próprio de R$ 633.524.125,80 nessa data, igual ao valor do Tesouro).
9. **Dividendos e participações pagos pelo Banco do Brasil à União em novembro de 2020**: R$ 279,1 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de novembro de 2020, Tabela 3.1, linha I.4.2.1 Banco do Brasil (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/36289_1149131/RTN_Boletim_2020_11.pdf (publicado em 2020-12-29).
   - Trecho lido: "I.4.2.1 Banco do Brasil 530,6 279,1 (Novembro 2019, Novembro 2020, em R$ milhões)"
   - Situação: Recebido pela União em 27/11/2020 (Portal da Transparência, receitas de 2020: juros sobre o capital próprio de R$ 279.054.001,43 nessa data, igual ao valor do Tesouro).
10. **Dividendos e participações pagos pelo Banco do Brasil à União em dezembro de 2020**: R$ 167,6 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2020, Tabela 3.1, linha I.4.2.1 Banco do Brasil (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/37105_1940142/RTN_Boletim_2020_12.pdf (publicado em 2021-01-28).
   - Trecho lido: "I.4.2.1 Banco do Brasil 252,4 167,6 (Dezembro 2019, Dezembro 2020, em R$ milhões)"
   - Situação: Recebido pela União em 30/12/2020 (Portal da Transparência, receitas de 2020: juros sobre o capital próprio de R$ 167.605.036,45 nessa data, igual ao valor do Tesouro).

### Também conferido em 2020

- **Ano de poucas entradas grandes:** em abril de 2020 uma resolução do CMN limitou o pagamento de dividendos dos bancos
  por causa da Covid-19 (RTN de setembro, outubro e novembro de 2020, notas de Dividendos e Participações). Por isso os
  itens 9 e 10 são pequenos.
- **Logo abaixo do corte:** Banco do Brasil, setembro, R$ 147,4 mi (Portal: R$ 147.372.439,01 em 30/09/2020); Banco do
  Nordeste, abril, R$ 130,3 mi (série histórica).
- **Restituição de depósitos de sentenças judiciais não sacados (agosto de 2020):** o RTN de agosto (Nota 7) explica a
  alta de Demais Receitas por ela, sem dar o valor; no Portal, a natureza "RESTIT.DEP.DE SENTENÇAS JUD.Ñ SACADOS" soma
  R$ 1.094,9 milhões no mês, em vários lançamentos. Sem valor do Tesouro e sem entrada única; não entrou.
- **Recolhimentos atípicos** de IRPJ (R$ 2,5 bilhões em setembro) e de CSLL ("da ordem de 1,5 bilhão" em dezembro,
  "efetuados por algumas empresas de diversos setores econômicos"): sem pagador nem ato; fora da regra.
- **Atos de 2020:** exposições de motivos de todas as MPs de 2020 que não abrem crédito extraordinário foram lidas;
  nenhuma fixa receita nova relevante em reais (as de 2020 reduzem tributos ou tratam de despesas da pandemia). A alta da
  CSLL dos bancos para 20% veio do art. 32 da Emenda Constitucional nº 103/2019 (Planalto), que não é lei, MP nem
  decreto, e cuja exposição não foi lida.

## 2019

| # | Movimento | Data | Valor oficial | Natureza | Fonte do valor |
|---|---|---|---|---|---|
| 1 | Bônus do leilão dos volumes excedentes da cessão onerosa (pré-sal) | dezembro de 2019 | R$ 70,0 bi | paid | RTN de dezembro de 2019 |
| 2 | Bônus de assinatura da 16ª rodada de concessões de petróleo e gás | dezembro de 2019 | R$ 8,9 bi | paid | RTN de dezembro de 2019 |
| 3 | Transação tributária para encerrar litígios e cobranças da União (MP nº 899/2019) | 16/10/2019 (ato) | R$ 6.384,0 mi | expected_revenue | Exposição de Motivos Interministerial EMI nº 00268/2019 ME AGU |
| 4 | Bônus de assinatura da 6ª rodada de partilha do pré-sal | dezembro de 2019 | R$ 5,0 bi | paid | RTN de dezembro de 2019 |
| 5 | Dividendos e participações pagos pelo BNDES à União em novembro de 2019 | 18/11/2019 | R$ 4.591,0 mi | paid | RTN de novembro de 2019 |
| 6 | Dividendos e participações pagos pela Caixa Econômica Federal à União em setembro de 2019 | 30/09/2019 | R$ 3,0 bi | paid | RTN de setembro de 2019 |
| 7 | Recursos do acordo entre a Petrobras e autoridades norte-americanas incorporados pela União | 18/09/2019 | R$ 2.669,1 mi | paid | RTN de setembro de 2019 |
| 8 | Contribuição previdenciária sobre o seguro-desemprego (MP nº 905/2019, Programa Verde e Amarelo) | 11/11/2019 (ato) | R$ 1.920,0 mi | expected_revenue | Exposição de Motivos EM nº 352/2019 ME |
| 9 | Dividendos e participações pagos pelo BNDES à União em setembro de 2019 | 19/09/2019 | R$ 1.819,6 mi | paid | RTN de setembro de 2019 |
| 10 | Dividendos e participações pagos pela Caixa Econômica Federal à União em março de 2019 | março de 2019 | R$ 1.766,8 mi | paid | RTN de março de 2019 |

### Itens e trechos lidos

1. **Bônus do leilão dos volumes excedentes da cessão onerosa (pré-sal)**: R$ 70,0 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2019, Nota 6 do resultado mês contra mês (Concessões e Permissões), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/31547_1016534/relatorio_dez19.pdf (publicado em 2020-01-29).
   - Trecho lido: "acréscimo decorrente principalmente do recebimento de recursos relativos ao leilão da cessão onerosa ocorrido em nov/19, com impacto financeiro na Conta Única da União em dez/19, no montante de R$ 70,0 bilhões."
   - Situação: Recebido em dezembro de 2019. No Portal da Transparência, os bônus de assinatura de partilha de dezembro de 2019 somam R$ 63.250,7 milhões na natureza da União e R$ 11.730,1 milhões na de estados e municípios (inclui também a 6ª rodada de partilha), em lançamentos de 10, 26, 27 e 30/12/2019. No mesmo mês, a União pagou R$ 34,4 bilhões à Petrobras pela revisão do contrato da cessão onerosa (Nota 13) e o RTN registra no ano a transferência de R$ 11,7 bilhões a estados e municípios (Nota 15 do acumulado no ano).
2. **Bônus de assinatura da 16ª rodada de concessões de petróleo e gás**: R$ 8,9 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2019, Nota 6 do resultado mês contra mês (Concessões e Permissões), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/31547_1016534/relatorio_dez19.pdf (publicado em 2020-01-29).
   - Trecho lido: "Ainda, houve ingressos de R$ 8,9 bilhões associados à 16ª rodada de concessões de campos de petróleo e de R$ 5,0 bilhões relativos à 6ª rodada de partilha do petróleo do pré-sal."
   - Situação: Recebido em dezembro de 2019 (Portal da Transparência, receitas de 2019: a natureza 'BONUS ASSINAT.DE CONTRATO DE CONCESSAO' soma R$ 8.922,1 milhões no mês, com as maiores entradas em 19, 20, 23 e 27/12/2019).
3. **Transação tributária para encerrar litígios e cobranças da União (MP nº 899/2019)**: R$ 6.384,0 mi (expected_revenue).
   - Fonte: Exposição de Motivos Interministerial EMI nº 00268/2019 ME AGU, de 06/09/2019, item 10, https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/exm/exm-mp-899-19.pdf (publicado em 2019-09-06).
   - Trecho lido: "Estimativas conservadoras apontam como resultado da medida a arrecadação de R$ 1,425 bilhão em 2019, R$ 6,384 bilhões em 2020 e R$ 5,914 bilhões em 2021, sem prejuízo da economia de recursos decorrentes da solução dos litígios encerrados pela transação."
   - Situação: Convertida na Lei nº 13.988, de 14/04/2020 (Planalto). O valor é o de 2020, primeiro ano inteiro de vigência; a exposição não foi refeita na lei de conversão.
4. **Bônus de assinatura da 6ª rodada de partilha do pré-sal**: R$ 5,0 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2019, Nota 6 do resultado mês contra mês (Concessões e Permissões), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/31547_1016534/relatorio_dez19.pdf (publicado em 2020-01-29).
   - Trecho lido: "Ainda, houve ingressos de R$ 8,9 bilhões associados à 16ª rodada de concessões de campos de petróleo e de R$ 5,0 bilhões relativos à 6ª rodada de partilha do petróleo do pré-sal."
   - Situação: Recebido em dezembro de 2019. No Portal da Transparência, o bônus aparece junto com o do leilão da cessão onerosa nas naturezas de bônus de partilha (ver o item do leilão da cessão onerosa).
5. **Dividendos e participações pagos pelo BNDES à União em novembro de 2019**: R$ 4.591,0 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de novembro de 2019, Tabela 3.1, linha I.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/31401_1105010/relatorio_nov19.pdf (publicado em 2019-12-27).
   - Trecho lido: "I.4.2.3 BNDES 0,0 4.591,0 (Novembro 2018, Novembro 2019, em R$ milhões)"
   - Situação: Recebido pela União em 18/11/2019 (Portal da Transparência, receitas de 2019: dividendos de R$ 4.591.021.788,02 nessa data, igual ao valor do Tesouro); atribuído ao BNDES pelo Tesouro Nacional (RTN de novembro de 2019, Nota 9).
6. **Dividendos e participações pagos pela Caixa Econômica Federal à União em setembro de 2019**: R$ 3,0 bi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de setembro de 2019, Tabela 3.1, linha I.4.2.4 Caixa (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/31079_992768/relatorio_set19.pdf (publicado em 2019-10-30).
   - Trecho lido: "I.4.2.4 Caixa 0,0 3.000,0 (Setembro 2018, Setembro 2019, em R$ milhões)"
   - Situação: Recebido pela União em 30/09/2019: no Portal da Transparência (receitas de 2019), a entrada de juros sobre o capital próprio dessa data (R$ 3.338.599.760,80) soma o valor da Caixa mais os R$ 338,6 milhões do Banco do Brasil da mesma tabela do Tesouro.
7. **Recursos do acordo entre a Petrobras e autoridades norte-americanas incorporados pela União**: R$ 2.669,1 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de setembro de 2019, Nota 7 do resultado mês contra mês (Demais Receitas), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/31079_992768/relatorio_set19.pdf (publicado em 2019-10-30).
   - Trecho lido: "incorporação de recursos resultante de acordo celebrado entre a empresa Petróleo Brasileiro S/A - Petrobras e autoridades norte-americanas no montante de R$ 2.669,1 milhões."
   - Situação: Recebido em 18/09/2019 (Portal da Transparência, receitas de 2019: R$ 2.669.114.238,21 na natureza 'MULT.LEG.ANTICORRUP.ACORDOS LENIÊNCIA' nessa data).
8. **Contribuição previdenciária sobre o seguro-desemprego (MP nº 905/2019, Programa Verde e Amarelo)**: R$ 1.920,0 mi (expected_revenue).
   - Fonte: Exposição de Motivos EM nº 352/2019 ME, item 11, https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/exm/exm-mp%20905-19.pdf (publicado em 2019-11-11).
   - Trecho lido: "A desoneração proposta será compensada por meio de aumento de receita obtido com contribuição previdenciária sobre os valores pagos aos beneficiários do seguro-desemprego, que poderão considerar o período de recebimento de seguro desemprego para fins de concessão de benefícios previdenciários. Prevê-se uma arrecadação de R$ 1,92 bilhão em 2020; R$ 2,39 bilhões em 2021 e 2,48 bilhões em 2022."
   - Situação: Revogada pela Medida Provisória nº 955/2020 (Planalto). A contribuição compensaria a desoneração da folha do contrato Verde e Amarelo (lado da saída).
9. **Dividendos e participações pagos pelo BNDES à União em setembro de 2019**: R$ 1.819,6 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de setembro de 2019, Tabela 3.1, linha I.4.2.3 BNDES (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/31079_992768/relatorio_set19.pdf (publicado em 2019-10-30).
   - Trecho lido: "I.4.2.3 BNDES 0,0 1.819,6 (Setembro 2018, Setembro 2019, em R$ milhões)"
   - Situação: Recebido pela União em 19/09/2019 (Portal da Transparência, receitas de 2019: juros sobre o capital próprio de R$ 1.819.643.483,05 nessa data, igual ao valor do Tesouro).
10. **Dividendos e participações pagos pela Caixa Econômica Federal à União em março de 2019**: R$ 1.766,8 mi (paid).
   - Fonte: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de março de 2019, Tabela 3.1, linha I.4.2.4 Caixa (R$ milhões, preços correntes), https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/29719_950722/nimmar2019.pdf (publicado em 2019-04-29).
   - Trecho lido: "I.4.2.4 Caixa 0,0 1.766,8 (Março 2018, Março 2019, em R$ milhões)"
   - Situação: Recebido pela União em março de 2019; atribuído à Caixa pelo Tesouro Nacional (RTN de março de 2019, Nota 6: 'R$ 1,8 bilhão da Caixa'). No Portal da Transparência, a maior entrada de juros sobre o capital próprio do mês é de R$ 1.740.942.071,12 em 28/03/2019; o Portal não nomeia o pagador.

### Também conferido em 2019

- **Logo abaixo do corte:** BNDES, maio, R$ 1.628,3 mi; unificação da área do Parque das Baleias, na Bacia de Campos,
  "arrecadação atípica em abril de 2019 de R$ 1,5 bilhão" (RTN de dezembro de 2019, Nota 11 do acumulado no ano); BNDES,
  outubro, R$ 1.459,7 mi (Portal: R$ 1.459.657.793,50 em 16/10/2019); outorga da usina hidrelétrica Porto Primavera,
  ligada à privatização da Cesp, R$ 1,4 bilhão em maio (RTN de maio, Nota 8); concessões aeroportuárias, R$ 1,4 bilhão
  em julho (RTN de julho, Nota 6); Banco do Brasil, março, R$ 1.087,2 mi; parcela da concessão do aeroporto do Galeão,
  R$ 1,0 bilhão em junho (RTN de junho, Nota 7).
- **Recolhimento atípico de IRPJ de R$ 5,2 bilhões em agosto** "relativos a reorganizações societárias de algumas
  empresas" (RTN de agosto, Nota 1): sem pagador nem ato; fora da regra.
- **Portal sem valor do Tesouro:** outorga aeroportuária de R$ 1.917.141.383,73 em 05/09/2019 (Fundo Nacional de Aviação
  Civil), que o RTN de setembro não destaca; abaixo do corte de qualquer forma.
- **Boletins de janeiro e fevereiro de 2019:** o texto extraído não traz notas legíveis; a série histórica não mostra
  item grande nesses meses (Concessões R$ 498 mi e R$ 143 mi; nenhum dividendo).
- **Atos de 2019:** exposições de motivos de todas as MPs de 2019 que não abrem crédito extraordinário foram lidas; só a
  MP 899 e a MP 905 fixam receita nova relevante em reais.

## Não confirmado

- **Câmara dos Deputados:** a API de dados abertos (`dadosabertos.camara.leg.br`) não respondeu durante a coleta
  (tempo esgotado). As listas de MPs, leis e decretos vieram da API do Senado e os textos e exposições de motivos, do
  Planalto. Exposições de motivos de projetos de lei do Executivo que não estão ligadas na página do Planalto não foram
  lidas; os casos conhecidos estão nas notas de cada ano (LC nº 224/2025, Lei nº 15.265/2025).
- **2024, valor recolhido com a atualização de bens no exterior (Lei nº 14.754/2023):** o Tesouro só publica a variação
  do IRPF; o total não foi confirmado.
- **2023, imposto de exportação de petróleo de março a junho de 2023 (MP nº 1.163/2023):** o RTN não dá o valor por mês;
  só o total do Imposto sobre a Exportação no Portal (todos os produtos).
- **2021, dia do pagamento da Petrobras de agosto de 2021 (R$ 6.020,6 mi):** não há linha correspondente no arquivo de
  receitas do Portal; ficou só o mês.
- **2020, origem exata da devolução do PESE:** o Tesouro a registra como redução de despesa; não há linha no arquivo de
  receitas do Portal; ficou só o mês e o valor do Tesouro.
- **2025, "alienação de bens intangíveis" de R$ 1.275.000.000,00 (26/11/2025) e R$ 3.710.220.000,00 (05/12/2025)**
  (Portal da Transparência, setorial do Ministério da Fazenda): as notas do RTN de novembro e dezembro de 2025 não as
  explicam e o Portal não diz o que foi vendido. Valor e natureza não confirmados; não usados.
- **2025, cargo de Manoel Carlos de Almeida Neto** na assinatura da Lei nº 15.270/2025: o Planalto mostra só o nome. O
  cargo não foi conferido em fonte primária (um resumo de busca, que não é fonte, o descreve como secretário-executivo
  do Ministério da Justiça que respondeu pelo ministério). O item diz isso no campo `office`.
- **2025, divisão Petrobras e Banco do Brasil em março:** as entradas do Portal de 20/03/2025 somam os dois pagadores; o
  valor de cada empresa vem só da tabela do Tesouro.

## Fora da regra, mas grandes: receitas financeiras

Entradas identificáveis e muito grandes que a regra deixa de fora porque o Tesouro as trata como receita financeira
(não entram no resultado primário do RTN). Ficam aqui para o autor decidir se a coluna deve mostrá-las.

- **Transferência do resultado do Banco Central ao Tesouro** (Portal da Transparência, natureza "RESULTADO DO
  BACEN-DEMAIS OPERACOES"): 14/03/2019 R$ 25.973.338.020,89; 12/09/2019 R$ 21.413.301.786,56; 06/03/2020
  R$ 22.288.681.258,25; **28/08/2020 R$ 350.022.251.304,30**; 25/02/2022 R$ 72.801.160.234,90; 14/03/2025
  R$ 28.746.262.897,98. É receita financeira, não primária.
- **Reversão de saldos e restituições de fundos de crédito:** Fundo de Garantia à Exportação e Ministério da Fazenda,
  R$ 13.494,3 milhões em abril e maio de 2026 (ver o item à parte abaixo).
- **Alienação de títulos mobiliários** (Portal): R$ 3.196.059.064,91 em 23/07/2019 e R$ 7.497.283.096,09 em
  16/04/2021, sem identificação do que foi vendido.
- **Emissão de títulos da dívida, remuneração das disponibilidades do Tesouro e retorno de empréstimos:** operações
  financeiras recorrentes, não listadas.

## Erro de dado achado no caminho (item à parte)

- Em `BRASIL-IMPOSTO_RESEARCH_recent-revenue_2026-10-04.md` (seção "Entradas grandes ainda sem identificação oficial"),
  a "reversão de saldos não aplicados de apoio financeiro reembolsável, 01/07/2026: R$ 13.494,3 milhões" não entrou em
  01/07/2026. No arquivo de receitas de 2026 do Portal da Transparência, o dinheiro entrou como "RESTIT.DESP.FINANCEIRAS
  EX.ANTERIORES-PRINC." em 15/04/2026 (R$ 5.156.774.534,00, setorial do Ministério da Fazenda) e 15/05/2026
  (R$ 8.337.521.912,70, Fundo de Garantia à Exportação-BNDES); em 01/07/2026 as duas linhas foram estornadas (soma de
  menos R$ 13.494,3 milhões na mesma natureza) e relançadas na natureza "REVERSAO SALD.Ñ.APLIC.REL.APOIO FIN.REEM-PRI".
  É reclassificação, não entrada nova. O item não está no JSON (é receita financeira) e nada foi alterado no arquivo
  antigo; fica o aviso.
