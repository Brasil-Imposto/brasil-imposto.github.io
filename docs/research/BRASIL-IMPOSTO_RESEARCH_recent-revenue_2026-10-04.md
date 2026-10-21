# Recentes: maiores entradas de dinheiro na União (2026-07-01 a 2026-10-03)

Pesquisa para o lado da receita do componente "Recentes" da home. Coletado em 2026-10-04. Saída de dados:
`data/home/recent-revenue-candidates.json` (mesmas chaves dos itens de `data/home/recent.json`, `kind` = `revenue`). Em 2026-10-04 os quatro itens foram conferidos no RTN de agosto e juntados a `data/home/recent.json`, com a data do pagamento em `moved_on`; o arquivo de candidatos foi apagado.
Complementa `BRASIL-IMPOSTO_RESEARCH_recent-big-decisions_2026-10-02.md`, cuja varredura de leis e MPs não achou ato
de receita com valor oficial. Toda frase de valor abaixo foi lida na página primária; o que não foi aberto está marcado
"não confirmado". Documento escrito aos poucos, item a item.

## Critério

- **Entra:** uma entrada de dinheiro na União, identificável uma a uma, com valor oficial em reais lido em fonte
  primária (Tesouro Nacional, Diário Oficial da União, Planalto, ANP, PPSA, comunicado ou documento CVM da estatal),
  ocorrida de 01/07/2026 a 03/10/2026.
- **Não entra:** arrecadação mensal ordinária de tributos; qualquer coisa depois de 03/10/2026 (a sessão pública de
  ofertas da ANP de 07/10/2026 fica fora).
- **Natureza do valor:** `paid` para dinheiro recebido, `expected_revenue` para previsão oficial.
- **Ordem:** maior valor oficial primeiro; mesmo critério para qualquer governo.

## Resumo

| # | Entrada | Data | Valor oficial | Natureza | Fonte do valor |
|---|---|---|---|---|---|
| 1 | Dividendos e participações do BNDES à União | 25/08/2026 | R$ 7.405,0 mi | paid | RTN de agosto (Tesouro) |
| 2 | Imposto de exportação de 12% sobre petróleo bruto (Resolução Gecex 938) | agosto de 2026 | R$ 1,9 bi | paid | RTN de agosto (Tesouro) |
| 3 | Juros sobre o capital próprio da Petrobras à União (1ª parcela) | 20/08/2026 | R$ 1.311,0 mi | paid | RTN de agosto (Tesouro) |
| 4 | Dividendos e participações do Banco do Nordeste à União | 26/08/2026 | R$ 165,1 mi | paid | RTN de agosto (Tesouro) |

Nenhum ato de receita com previsão oficial de arrecadação (`expected_revenue`) foi achado na janela.

## Itens confirmados

### 1. Dividendos e participações pagos pelo BNDES à União, agosto de 2026: R$ 7.405,0 milhões (paid)
- Fonte: Secretaria do Tesouro Nacional, Boletim Resultado do Tesouro Nacional, Vol. 32, N. 8, agosto de 2026,
  publicado em 29/09/2026. Página: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/8
  PDF: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/55921_1803160/boletim_ago26.pdf
- Linha lida na Tabela 3.1 (R$ milhões, preços correntes; colunas agosto de 2025 e agosto de 2026):
  "1.4.2.3 BNDES 6.783,7 7.405,0".
- No mesmo mês, a rubrica 1.4.2 Dividendos e Participações somou R$ 8.881,1 milhões (BNDES R$ 7.405,0 mi,
  Petrobras R$ 1.311,0 mi, BNB R$ 165,1 mi).

### 2. Imposto de exportação de 12% sobre petróleo bruto (Resolução Gecex nº 938/2026): R$ 1,9 bilhão em agosto (paid)
- Ato: Resolução Gecex nº 938, de 09/07/2026, Diário Oficial da União de 10/07/2026,
  https://www.in.gov.br/web/dou/-/resolucao-gecex-n-938-de-9-de-julho-de-2026-718114520 . Texto lido: "Fica estabelecida
  a alíquota de 12% do imposto sobre a exportação de óleos brutos de petróleo ou de minerais betuminosos, classificados
  na posição 2709 da Nomenclatura Comum do Mercosul - NCM." Vigência de 60 dias a partir de 10/07/2026. Assinatura:
  "MÁRCIO FERNANDO ELIAS ROSA, Presidente do Comitê".
- Prorrogação: Resolução Gecex nº 957, de 01/09/2026 (DOU 03/09/2026),
  https://www.in.gov.br/web/dou/-/resolucao-gecex-n-957-de-1-de-setembro-de-2026-729944383 : "Prorroga, por um prazo
  de sessenta dias, a vigência da alíquota de 12%", em vigor a partir de 08/09/2026.
- Origem: Nota Informativa SEI nº 2350/2026/MF (Secretaria de Reformas Econômicas, assinada em 25/08/2026),
  https://www.gov.br/mdic/pt-br/assuntos/camex/outros-documentos/notas/deferimentos/240a-reuniao-ordinaria-do-comite-executivo-de-gestao-gecex/nota-informativa-sei-no-2350_2026.pdf :
  "O Imposto de Exportação em análise foi instituído pela Medida Provisória nº 1.340, de 12 de março de 2026". A nota não
  traz estimativa de arrecadação.
- Valor (Tesouro, RTN de agosto, Nota 5 do mês, PDF acima): "resultado refletiu, principalmente, as alterações
  legislativas no Imposto de Exportação sobre óleo bruto (Resolução Gecex nº 938/2026), item responsável pelo
  recolhimento de R$ 1,9 bilhão no mês de agosto de 2026."
- Julho (Tesouro, RTN de julho, Nota 6 do mês,
  https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/55499_1749788/boletim_jul26.pdf ):
  "as alterações legislativas no Imposto de Exportação sobre óleo bruto (MP nº 1.340/2026), item responsável pelo
  recolhimento de R$ 3,2 bilhões no mês de julho de 2026."
- Ressalva para quem decidir: é a arrecadação de um tributo, mas de um tributo extraordinário e temporário, criado e
  mantido por atos com data; por isso entrou como candidato. Se o painel quiser o total da janela, julho mais agosto
  somam R$ 5,1 bilhões (soma de dois valores oficiais já arredondados pelo Tesouro, atribuídos a atos diferentes);
  setembro ainda não foi publicado. Se o painel tratar o caso como arrecadação ordinária, basta retirar o item.

### 3. Dividendos e participações pagos pela Petrobras à União, agosto de 2026: R$ 1.311,0 milhões (paid)
- Fonte: RTN de agosto de 2026, Tabela 3.1 (PDF do item 1). Linha lida: "1.4.2.8 Petrobras 1.700,4 1.311,0"
  (agosto de 2025, agosto de 2026, R$ milhões).
- Datas (página da Petrobras "Proventos Declarados: Pagos e a Pagar",
  https://www.investidorpetrobras.com.br/acoes-dividendos-e-dividas/dividendos-e-jcp/ ): Ano Fiscal 2026, 1T, JCP,
  "1a | PAGO | 20/08/2026 | 11/05/2026 | 01/06/2026 | R$ 0,350486" e "2a | PAGO | 21/09/2026 | 11/05/2026 | 01/06/2026 |
  R$ 0,350486" (colunas: parcela, situação, data do pagamento, data da divulgação, data base, valor bruto por ação ON).
- Valor exato e data (Portal da Transparência, receitas de 2026, ver seção "Fonte diária"): 20/08/2026, "JUROS SOBRE O
  CAPITAL PROPRIO-PRINCIPAL", R$ 1.310.983.999,23.
- Segunda parcela: o Portal da Transparência registra em 21/09/2026 outra entrada de juros sobre o capital próprio de
  R$ 1.310.983.999,23, igual ao centavo à de 20/08 e na data da 2ª parcela da Petrobras. A linha não nomeia o pagador e
  o Tesouro ainda não publicou o RTN de setembro (sai no fim de outubro); por isso ficou no `status`, e não no valor do
  item. Se o RTN de setembro confirmar, o item passa a R$ 2.621.967.998,46 (duas parcelas).
- Fora da janela: parcelas do 2T de 2026 com pagamento em 23/11/2026 e 21/12/2026.

### 4. Dividendos e participações pagos pelo Banco do Nordeste à União, agosto de 2026: R$ 165,1 milhões (paid)
- Fonte: RTN de agosto de 2026, Tabela 3.1 (PDF do item 1). Linha lida: "1.4.2.2 BNB 167,6 165,1" (agosto de 2025,
  agosto de 2026, R$ milhões).
- Valor exato e data (Portal da Transparência): 26/08/2026, "JUROS SOBRE O CAPITAL PROPRIO-PRINCIPAL", R$ 165.104.391,62.
- Entrou por ser a quarta maior entrada identificada; é pequena perto das demais e pode ser cortada pelo painel.

## Fonte diária: Portal da Transparência (receitas de 2026)
- Arquivo: https://portaldatransparencia.gov.br/download-de-dados/receitas/2026 (redireciona para
  `dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/receitas/2026_Receitas.zip`, atualizado em 02/10/2026,
  cobre lançamentos até 30/09/2026). Cada linha traz órgão, unidade gestora, natureza da receita, valor realizado e data,
  mas não o nome de quem pagou. Serviu para datar e dar o valor exato das entradas que o Tesouro nomeia no RTN.
- Conferência com o RTN de agosto: as três entradas de juros sobre o capital próprio de agosto (25/08 R$ 7.404.969.362,58;
  20/08 R$ 1.310.983.999,23; 26/08 R$ 165.104.391,62) somam R$ 8.881,1 milhões, o mesmo total da rubrica 1.4.2
  Dividendos e Participações no RTN de agosto.
- Imposto sobre a Exportação no Portal da Transparência (todas as naturezas "IMPOSTO SOBRE A EXPORTACAO", todos os
  produtos, soma das linhas diárias por mês, R$ milhões): jan 0,1; fev 0,1; mar 13,0; abr 10,9; mai 1.048,6;
  jun 3.774,8; jul 3.161,4; ago 1.945,5; set 1.969,1. Julho e agosto batem com o RTN (R$ 3,2 bi e R$ 1,9 bi). Na janela
  (julho a setembro) a soma é R$ 7.076,0 milhões. O item 2 usa só o valor de agosto, que o Tesouro liga em texto à
  Resolução Gecex nº 938; se o painel preferir o total da janela, a soma acima é a opção, com a ressalva de que a linha do
  Portal cobre o imposto de exportação inteiro (antes de maio de 2026 ele rendia cerca de R$ 0,1 milhão por mês).

## Entradas grandes ainda sem identificação oficial (não entraram no JSON)
Valores exatos no Portal da Transparência, mas sem documento oficial que diga de onde vieram. Não foram usados; ficam
como pistas para conferir quando o Tesouro publicar o RTN de setembro (fim de outubro de 2026).
- **Restituição de despesas primárias de exercícios anteriores, setembro de 2026: R$ 13.517,5 milhões** no mês
  (natureza "RESTIT.DESP.PRIMARIAS EX.ANTERIORES-PRINC.", unidade "SETORIAL ORCAMENTARIA E FINANCEIRA-MF"), em quatro
  linhas: 08/09 R$ 6.399.367.868,00; 24/09 R$ 3.616.451.634,16; 25/09 R$ 2.230.404.117,75; 30/09 R$ 1.201.197.535,33.
  Nos outros meses de 2026 a mesma natureza ficou entre R$ 107,6 milhões e R$ 1.606,8 milhões. É dinheiro devolvido à
  União de gastos de anos anteriores; quem devolveu e por quê não foi achado. Se o RTN de setembro explicar, pode ser a
  maior entrada da janela.
- **Reversão de saldos não aplicados de apoio financeiro reembolsável, 01/07/2026: R$ 13.494,3 milhões** (natureza
  "REVERSAO SALD.Ñ.APLIC.REL.APOIO FIN.REEM-PRI"): R$ 8.337.521.912,70 na unidade "FUNDO DE GARANTIA A
  EXPORTACAO-BNDES" e R$ 5.156.774.534,00 na setorial do Ministério da Fazenda; mais R$ 508.996.783,15 em 17/08. É receita
  de capital (volta de recursos já autorizados para empréstimo, não receita nova); a Lei 15.473/2026 não traz cláusula
  de reversão. Não identificado.
  **Correção (2026-10-04, pesquisa de receitas de 2019 a 2026):** 01/07/2026 é só uma reclassificação no Portal; o dinheiro
  entrou em 15/04/2026 (R$ 5.156,8 milhões) e em 15/05/2026 (R$ 8.337,5 milhões). Ver
  `BRASIL-IMPOSTO_RESEARCH_moves-revenue_2026-10-04.md`.
- **Juros sobre o capital próprio, 11/09/2026: R$ 400.517.515,36.** A linha não nomeia o pagador. Imprensa diz que o
  Banco do Brasil pagou juros sobre o capital próprio em 11/09/2026; não confirmado em fonte primária do banco nem no
  Tesouro.
- **Alienação de títulos e valores mobiliários, 24/08/2026: R$ 605.943.920,41** (natureza "ALIEN.TIT.,VAL.MOB.E
  APL.CONG.TEMP.-PRINC."). Não identificado.

## Grandes, mas recorrentes (fora do critério)
- Participação especial do petróleo (pagamento trimestral, 31/07/2026, várias linhas acima de R$ 2 bilhões) e royalties
  mensais: receita ordinária de exploração de recursos naturais. RTN de julho: "Exploração de Recursos Naturais" somou
  R$ 22.147,2 milhões no mês, explicada pelo preço do barril e pela produção.
- Remuneração paga pelo BNDES ao FAT sobre repasses para programas de desenvolvimento econômico, 14/07/2026:
  R$ 12.900.954.751,85 (pagamento semestral regular ao fundo).
- Venda do petróleo e gás da União pela PPSA (natureza "COM.PETRO,GAS NAT.E OUTROS-CONTR.PART."): entradas semanais de
  R$ 0,2 a R$ 0,9 bilhão. Os leilões spot da PPSA na janela (7º em 29/07, 8º em 26/08 e 02/09, 9º em 30/09) vendem cargas
  de cerca de 1 milhão de barris, e "os valores obtidos são divulgados 15 dias após o embarque das cargas" (notícias da
  PPSA, https://www.presalpetroleo.gov.br/noticias/ ); nenhum valor publicado.
- Remuneração das disponibilidades do Tesouro no Banco Central e emissão de títulos da dívida: operações financeiras,
  não receita.

## Verificado, sem entrada de receita grande na janela
- **RTN de julho e de agosto de 2026** (notas do mês): nenhuma receita atípica além do imposto de exportação. Os
  "recolhimentos atípicos da ordem de R$ 11,0 bilhões entre IRPJ e CSLL" citados no acumulado de julho não aparecem na
  nota do mês de julho, logo são de antes da janela. "Concessões e Permissões": R$ 237,3 milhões em julho e
  R$ 112,1 milhões em agosto. Banco do Brasil, Caixa e Eletrobras: zero em julho e agosto.
- **ANP e bônus de assinatura:** a sessão de 07/10/2026 está fora. No Portal da Transparência não há entrada de bônus
  de assinatura entre 01/07 e 30/09/2026. O 3º Ciclo da Oferta Permanente de Partilha teve as assinaturas dos contratos
  concluídas segundo notícia da PPSA de 03/07/2026, e a cerimônia de 05/08/2026 informa: "O processo prevê bônus de
  assinatura de R$ 103,7 milhões"
  (https://www.presalpetroleo.gov.br/noticias/cerimonia-marca-assinatura-dos-contratos-dos-blocos-arrematados-no-3o-opp/ ).
  Valor pequeno e sem entrada registrada na janela.
- **PPSA:** o 6º Leilão de Petróleo da União não aparece nas notícias da PPSA entre 01/07 e 03/10/2026; o leilão de
  áreas não contratadas foi em dezembro de 2025, fora da janela.
- **Decretos de 2026** (API de legislação do Senado, 86 decretos de 01/07 a 03/10/2026, filtro por termos de receita):
  nenhum aumenta receita; o Decreto nº 13.116, de 09/09/2026, reduz PIS/Pasep e Cofins (perda de receita, lado da saída).
- **Leis e MPs:** já varridos em `BRASIL-IMPOSTO_RESEARCH_recent-big-decisions_2026-10-02.md`, sem receita com valor
  oficial.
- **Concessões de aeroportos, portos, rodovias e ferrovias:** nenhum leilão com outorga paga à União encontrado na
  janela; as linhas de outorga no Portal da Transparência ficaram abaixo de R$ 75 milhões por mês.
- **Comunicação oficial no período eleitoral:** gov.br e PPSA restringem notícias de 04/07 a 25/10/2026 (aviso da PPSA de
  08/07/2026), o que limita a busca por comunicados.
