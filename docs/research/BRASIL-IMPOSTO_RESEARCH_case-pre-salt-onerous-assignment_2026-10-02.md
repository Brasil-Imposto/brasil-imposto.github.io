# Caso: cessão onerosa do pré-sal (2010 a 2022)

Pesquisa para a página de caso (D48). Só fonte oficial; cada número traz órgão, data de referência, link e a frase do documento.
Dados estruturados: `data/cases/pre-salt-onerous-assignment.json`. Coleta: 2026-10-02.

**Correção monetária.** IPCA, número-índice da tabela 1737 do IBGE/SIDRA (variável 2266), dezembro de 2024 = 7.100,50.
Fator = 7.100,50 dividido pelo índice do mês de referência: set/2010 = 3.126,29 (fator 2,27122); out/2013 = 3.760,30 (1,88828);
dez/2019 = 5.320,25 (1,33462); dez/2021 = 6.120,04 (1,16020); mai/2022 = 6.412,88 (1,10722). Fonte:
https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/201009,201310,201912,202112,202205,202412

**Câmbio.** PTAX de venda do BCB (API Olinda, `CotacaoDolarDia`): 03/09/2010 = 1,7281; 01/11/2019 = 3,9786; 27/12/2019 = 4,0545;
17/12/2021 = 5,6959; 21/10/2013 = 2,1738.

**Aviso de coleta.** Em outubro de 2026 (período eleitoral) as notícias de gov.br e da Agência Petrobras aparecem como "Conteúdo
Restrito" ou "Inativação de conteúdos no período eleitoral". Essas páginas foram lidas na cópia do Internet Archive
(`web.archive.org/web/<ano>id_/<url>`), que reproduz a página oficial; o link guardado é o oficial, com a cópia indicada.

## 1. O que aconteceu

Em 30 de junho de 2010, a Lei 12.276 autorizou a União a "ceder onerosamente à Petróleo Brasileiro S.A. - PETROBRAS, dispensada a
licitação, o exercício das atividades de pesquisa e lavra de petróleo [...] em áreas não concedidas localizadas no pré-sal", até
"5.000.000.000 (cinco bilhões) de barris equivalentes de petróleo", e autorizou a União a "subscrever ações do capital social da
Petrobras e a integralizá-las com títulos da dívida pública mobiliária federal". O contrato foi assinado em 3 de setembro de 2010 por
R$ 74,8 bilhões (extrato no DOU de 21/09/2010) ("US$ 42,5 bilhões - R$ 74,8 bilhões ao câmbio da época", nas palavras da ANP). A lei mandou rever o valor
depois da fase de exploração; a revisão foi assinada em 1º de novembro de 2019 e "prevê o ressarcimento à companhia de US$ 9,058
bilhões" (Petrobras), pagos pela União em dezembro de 2019 (R$ 34,41 bilhões, Ministério da Economia). Os volumes acima dos 5
bilhões de barris foram leiloados em partilha de produção: em 6 de novembro de 2019, nas palavras da ANP, "Foram arrematados dois blocos - Búzios e
Itapu, com arrecadação total de R$ 69.960.000.000,00 de bônus de assinatura" e Atapu e Sépia ficaram sem oferta; em 17 de dezembro
de 2021, "Foram arrematados dois blocos - Sépia e Atapu, com arrecadação total de R$ 11.140.000.000,00 de bônus de assinatura" (ANP). A Lei 13.885/2019
mandou repartir o bônus, "descontada a despesa decorrente da revisão do contrato de cessão onerosa", com estados, Distrito Federal
e municípios.

Fontes: Lei 12.276/2010 (https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12276.htm); ANP, apresentação "Assinatura
do Termo Aditivo ao Contrato de Cessão Onerosa", 01/11/2019
(https://www.gov.br/anp/pt-br/centrais-de-conteudo/apresentacoes-palestras/2019/arquivos/2019/2019-11-01_decio-oddone_assinatura-cessao-onerosa.pdf);
Petrobras, "Assinamos Aditivo ao Contrato de Cessão Onerosa", 01/11/2019
(https://petrobras.com.br/fatos-e-dados/assinamos-aditivo-ao-contrato-de-cessao-onerosa.htm, lido na cópia de 14/11/2019 do
Internet Archive); ANP, resultados da 1ª e da 2ª rodada
(https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/1a-lveco/resultados,
https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/2-lveco/resultados); Lei 13.885/2019
(https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/L13885.htm).

## 2. Dinheiro

### 2.1 O que a União entregou ou pagou

| Item | Valor corrente | Data de referência | Em R$ de dez/2024 (IPCA) | Órgão e frase |
|---|---|---|---|---|
| Direito de produzir até 5 bilhões de barris, cedido à Petrobras (pago pela Petrobras à União em títulos públicos) | R$ 74.807.616.407,00 (ANP: "US$ 42,5 bilhões - R$ 74,8 bilhões ao câmbio da época"; "pagou US$ 8,51 por barril") | 03/09/2010 (DOU de 21/09/2010: "VALOR: R$ 74.807.616.407,00 [...] DATA DA CELEBRAÇÃO: 3 de setembro de 2010") | R$ 169,90 bi (fator 2,27122) | ANP, apresentação de 01/11/2019; TCU, notícia de 27/02/2024: "pelo valor de R$ 74,807 bilhões" |
| Ressarcimento da União à Petrobras pela revisão do contrato | US$ 9,058 bi; "cerca de R$ 34,1 bilhões" atualizados pela Selic até 30/09/2019; pago: R$ 34,41 bi | aditivo 01/11/2019; pagamento dez/2019 | R$ 45,92 bi (pagamento; fator 1,33462) | Petrobras: "O aditivo prevê o ressarcimento à companhia de US$ 9,058 bilhões"; Ministério da Economia, 27/12/2019: "R$ 34,41 bilhões foram utilizados para quitar um passivo da União com a Petrobras, encerrando a revisão da cessão onerosa" |

Observações.
- O extrato do contrato (DOU de 21/09/2010, Seção 3, p. 80) diz: "FORMA DE PAGAMENTO: Títulos da dívida pública mobiliária
  federal, na modalidade de Letras Financeira do Tesouro Nacional com vencimentos em 7 de setembro de 2014, 7 de março de 2015, 7
  de setembro de 2015 e 7 de setembro de 2016". O valor por extenso no mesmo extrato traz erro ("oitocentos e setenta milhões");
  vale o número.
- A Lei 12.276 (art. 1º, § 3º) diz que o pagamento da Petrobras "deverá ser efetivado prioritariamente em títulos da dívida pública
  mobiliária federal"; o art. 9º autorizou a União a comprar ações da Petrobras com os mesmos títulos. O sumário executivo do TCU
  resume: "Letras Financeira do Tesouro (LFT) R$67,8 bilhões" na capitalização de "R$120 bilhões (ações)" e a cessão por
  "R$ 74bi (LFT + R$)", com a ressalva "*todos são valores aproximados"
  (https://portal.tcu.gov.br/data/files/B9/E3/4E/F6/9FA0671053455957F18818A8/Sumario_executivo_cessao_onerosa_solucoes_criadas_outorga_atipica.pdf).
- O mesmo sumário do TCU escreve "saldo de US$ 9,048 bilhões"; a Petrobras escreve US$ 9,058 bilhões. A diferença (US$ 10 milhões)
  fica registrada; o valor em reais efetivamente pago (R$ 34,41 bi) vem do Ministério da Economia.
- Em reais, o valor de 2010 convertido pela PTAX de 03/09/2010 (1,7281) daria US$ 43,3 bi, não US$ 42,5 bi: o contrato usou
  câmbio próprio, que não foi localizado em documento oficial. A página deve usar o valor em reais.

### 2.2 O que entrou: bônus de assinatura (valor fixo do edital; vence quem oferece mais "excedente em óleo" à União)

Fonte principal: planilha da ANP "Resultados das Rodadas de Licitações de Partilha de Produção dos Volumes Excedentes da Cessão
Onerosa" (https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/resultados/arquivos/resultados-licitacoes-volumes-excedentes-ce.xlsx),
conferida com os extratos dos contratos no DOU.

| Rodada | Área | Bônus (R$) | Em R$ de dez/2024 | Excedente em óleo à União (mínimo / vencedor) | Consórcio vencedor (operadora *) | Contrato |
|---|---|---|---|---|---|---|
| 1ª, 06/11/2019 | Búzios | 68.194.000.000,00 | 91,01 bi (dez/2019) | 23,24% / 23,24% (sem ágio) | Petrobras 90%*, CNODC 5%, CNOOC 5% | nº 1/2020, assinado em 30/03/2020 |
| 1ª, 06/11/2019 | Itapu | 1.766.000.000,00 | 2,36 bi | 18,15% / 18,15% (sem ágio) | Petrobras 100%* | nº 2/2020, 30/03/2020 |
| 1ª, 06/11/2019 | Sépia | 22.859.000.000,00 (oferta) | não arrecadado | mínimo 27,88% | sem ofertas | |
| 1ª, 06/11/2019 | Atapu | 13.742.000.000,00 (oferta) | não arrecadado | mínimo 26,23% | sem ofertas | |
| 2ª, 17/12/2021 | Sépia | 7.138.000.000,00 | 8,28 bi (dez/2021) | 15,02% / 37,43% (ágio 149,2%) | Petrobras 30%*, TotalEnergies 28%, Petronas 21%, QP 21% | nº 02/2022, 27/04/2022 |
| 2ª, 17/12/2021 | Atapu | 4.002.000.000,00 | 4,64 bi (dez/2021) | 5,89% / 31,68% (ágio 437,9%) | Petrobras 52,5%*, Shell 25%, TotalEnergies 22,5% | nº 01/2022, 27/04/2022 |
| **Total arrecadado** | | **81.100.000.000,00** | **106,29 bi** | | | |

- 1ª rodada: R$ 69,96 bi arrecadados de R$ 106,561 bi ofertados (65,7%); 14 empresas habilitadas, 3 ofertantes (ANP, planilha).
  Mínimos de Sépia e Atapu em 2019: apresentação da ANP de 01/11/2019 ("Alíquota Mínima de Partilha: 27,88%" e "26,23%"); a
  planilha deixa essas células em branco.
- 2ª rodada: 11 empresas habilitadas, 5 ofertantes e 5 vencedoras (ANP, planilha).
- Recebimento de 2019: "O governo federal recebeu nesta sexta-feira (27/12) os R$ 35,54 bilhões restantes [...] O pagamento total
  atinge o valor de R$ 69,96 bilhões, levando em conta a antecipação de R$ 34,42 bilhões feita pela Petrobras em 10 de dezembro"
  (Ministério da Economia, 27/12/2019,
  https://www.gov.br/economia/pt-br/assuntos/noticias/2019/12/governo-conclui-recebimento-de-r-69-96-bilhoes-do-leilao-dos-excedentes-da-cessao-onerosa,
  cópia do Internet Archive de 17/01/2022). O texto oficial diz "Bacia de Campos"; a ANP situa as quatro áreas na Bacia de Santos.
- Recebimento da 2ª rodada: a data do pagamento não foi achada em texto oficial. O RTN do Tesouro (tabela 1.2, linha "1.4.1
  Concessões e Permissões") registra R$ 11.356,0 mi em fevereiro de 2022, contra R$ 692,3 mi em janeiro; é indício, não prova.

### 2.3 Para quem foi: União, estados, DF e municípios (Lei 13.885/2019 e LC 176/2020)

Regra (Lei 13.885, art. 1º): dos valores arrecadados, "descontada a despesa decorrente da revisão do contrato de cessão onerosa",
"15% (quinze por cento) aos Estados e ao Distrito Federal" (2/3 pela coluna A e 1/3 pela coluna B do Anexo), "3% (três por cento)
aos Estados confrontantes" e "15% (quinze por cento) aos Municípios", pelos coeficientes do FPM. A LC 176/2020 acrescentou o § 4º:
para Atapu e Sépia, "a União entregará, adicionalmente [...] R$ 4.000.000.000,00 (quatro bilhões de reais)".

| Evento | Base | Estados e DF (15%) | Estados confrontantes (3%) | Municípios (15%) | Total a estados, DF e municípios | Ficou com a União |
|---|---|---|---|---|---|---|
| Bônus de 2019 (Búzios e Itapu) | R$ 69,96 bi menos R$ 34,41 bi = R$ 35,55 bi | R$ 5,33 bi (cálculo) | R$ 1,07 bi (cálculo) | R$ 5,33 bi (cálculo) | **R$ 11,73 bi** (oficial; dez/2024: R$ 15,66 bi) | **R$ 23,82 bi** (oficial; dez/2024: R$ 31,79 bi) |
| Bônus de 2021 (Sépia e Atapu) | R$ 11,14 bi (sem desconto) | 33% de R$ 11,14 bi = R$ 3,68 bi, mais R$ 4,0 bi da LC 176 | (incluído) | (incluído) | **R$ 7.676.200.000,00** (oficial; dez/2024: R$ 8,50 bi) | R$ 3,46 bi (cálculo: 11,14 menos 7,68) |

- 2019: "a transferência de R$ 11,73 bilhões para as contas de Estados, Municípios e do Distrito Federal, conforme estabelecido pela
  Lei nº 13.885, de 17 de outubro de 2019 e R$ 23,82 bilhões para reforçar as contas do Governo Federal" (Ministério da Economia,
  27/12/2019). Transferência feita em 31/12/2019 (Ministério da Economia, 31/12/2019,
  https://www.gov.br/economia/pt-br/assuntos/noticias/2019/12/governo-realiza-transferencia-de-r-11-73-bilhoes-da-cessao-onerosa-para-estados-e-municipios).
  O RTN (tabela 1.5, linha "1.6.6 Outras", nota 2: "transferência a Estados, Distrito Federal e Municípios de parte dos valores
  arrecadados com os leilões dos volumes excedentes da cessão onerosa") registra R$ 11.730,1 mi em dezembro de 2019.
- 2022: "O total que será distribuído aos estados, DF e municípios é de R$ 7.676.200.000,00. Os pagamentos ocorrerão nos dias 20/05
  e 24/05" (gov.br, 20/05/2022,
  https://www.gov.br/pt-br/noticias/financas-impostos-e-gestao-publica/2022/05/governo-federal-vai-repassar-r-7-7-bilhoes-para-estados-e-municipios,
  cópia do Internet Archive de 11/11/2022; a ANP repete o número em 20/05/2022). O RTN registra R$ 7.664,1 mi em maio de 2022 na
  mesma linha (diferença de R$ 12,1 mi não explicada nas fontes lidas).
- A conta 33% x R$ 11,14 bi + R$ 4,0 bi = R$ 7,6762 bi dá exatamente o valor oficial; por isso a divisão
  15/3/15 de 2019 e a de 2022 são cálculos sobre a regra da lei, e só os totais são números oficiais publicados.
- RTN: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional (série histórica mensal, arquivo
  `seriehistoricajul26.xlsx`, atualizado em 27/08/2026).

### 2.4 O que entra depois

- **Royalties sobre a produção da cessão onerosa.** Lei 12.276, art. 5º: "Serão devidos royalties sobre o produto da lavra de que
  trata esta Lei nos termos do art. 47 da Lei nº 9.478"; a parcela de 5% segue a Lei 7.990/1989 e a que excede 5% segue o art. 49,
  II, da Lei 9.478. A ANP (01/11/2019) resume o efeito da mudança de regime nas áreas coparticipadas: "royalties em parte da
  produção elevam-se de 10% para 15%" e "haverá partilha de óleo lucro com a União". O valor em reais dos royalties e da
  participação especial pagos por esses campos não foi apurado nesta pesquisa (seção 8).
- **Óleo lucro da União nos contratos de partilha do excedente** (PPSA, Boletim Mensal nº 76, julho de 2026, publicado em
  23/09/2026, https://www.presalpetroleo.gov.br/wp-content/uploads/2026/09/JULHO_Boletim_mensal-PPSA.pdf, tabelas da página 5,
  acumulado desde 2017, em milhões de barris):

| Contrato de partilha (CPP) | Produção total acumulada (consórcio e União) | Parcela da União acumulada | Parcela da União / produção |
|---|---|---|---|
| Búzios | 890,72 | 12,52 | 1,4% |
| Sépia | 145,60 | 11,20 | 7,7% |
| Itapu | 85,38 | 6,23 | 7,3% |
| Atapu | 113,96 | 2,59 | 2,3% |
| **Quatro áreas do excedente** | **1.235,66** | **32,54** | **2,6%** |
| Mero (Libra, para comparação) | 595,00 | 114,54 | 19,3% |

  Frases do boletim: "A parcela acumulada da União, desde 2017, é de 158,40 milhões de barris de petróleo" e "Mero é responsável
  por 72,31% da parcela recebida pela União". A última coluna é cálculo desta pesquisa. A receita em reais da venda desse óleo
  pela PPSA não foi localizada por contrato (seção 8).
- **Por que a parcela da União é baixa no começo.** O Acórdão 1.260/2023-TCU-Plenário trata do "cálculo da compensação devida à
  Petróleo Brasileiro S.A. - Petrobras" e da "consequente definição do valor a ser reconhecido como custo em óleo": a compensação
  paga à Petrobras pelos novos sócios entra como custo em óleo e é recuperada antes do óleo lucro. Isso é regra do contrato, não
  conclusão desta pesquisa sobre o futuro da parcela.

## 3. Retorno em três linhas (D48)

1. **Custo.** A União entregou o direito de produzir até 5 bilhões de barris em 2010 por R$ 74,81 bi (R$ 169,90 bi de dez/2024),
   recebidos em títulos e caixa da Petrobras e em boa parte usados na capitalização da própria empresa; em 2019 devolveu R$ 34,41
   bi (R$ 45,92 bi de dez/2024) à Petrobras na revisão do contrato.
2. **Dinheiro que entra e sai depois.** Bônus de R$ 69,96 bi (2019) e R$ 11,14 bi (2021); R$ 11,73 bi (2019) e R$ 7,68 bi (2022)
   foram a estados, DF e municípios; ficaram com a União R$ 23,82 bi (2019, oficial) e R$ 3,46 bi (2022, cálculo). Depois: royalties
   (Lei 12.276, art. 5º) e o óleo lucro da União nos contratos do excedente, que somava 32,54 milhões de barris até julho de 2026
   (PPSA).
3. **Uso medido.** ANP, produção em mar por poço, arquivo atualizado em 03/09/2026, último mês julho de 2026
   (https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/fase-de-desenvolvimento-e-producao): os quatro campos com
   excedente produziram, até julho de 2026, **587,2 milhões de barris de petróleo e condensado sob a cessão onerosa** (BÚZIOS,
   ITAPU, ATAPU, SÉPIA) e **1.183,2 milhões de barris sob os contratos do excedente** (campos com sufixo `_ECO`); somados, 1.770,4
   milhões de barris (2.191,9 milhões de barris de óleo equivalente). Em julho de 2026 a média foi de 438,3 mil barris por dia na
   cessão onerosa e 1.046,1 mil barris por dia no excedente. Os outros campos da cessão onerosa achados na base (SUL DE TUPI, SUL DE
   BERBIGÃO, NORTE DE BERBIGÃO) somam mais 111,2 milhões de barris.

Notas de método da produção (cálculo desta pesquisa sobre o dado da ANP):
- Soma das colunas "Produção de Óleo (m³)" e "Produção de Condensado (m³)" de todos os poços de cada campo e mês, de 2010 a julho
  de 2026, convertida a barris por 6,28981; barril de óleo equivalente soma o gás (associado e não associado, em mil m³) na razão
  de 1.000 m³ de gás para 1 m³ de óleo.
- Os mesmos poços aparecem em `BÚZIOS` e em `BÚZIOS_ECO` (71 poços em julho de 2026): a ANP reparte a produção da jazida entre a
  cessão onerosa e o contrato de partilha. Os campos `_ECO` aparecem na base a partir de 2022.
- Conferência com a PPSA: Itapu (85,38) e Sépia (145,60) batem exatamente; Atapu dá 111,01 na ANP contra 113,96 na PPSA; Búzios dá
  841,24 na ANP contra 890,72 na PPSA (a PPSA conta meses de 2021 que a ANP registra no campo sem sufixo). Julho de 2026 em Búzios
  `_ECO`: 822,1 mil barris por dia na ANP e "822,10 mil bpd" na PPSA.
- Cessão onerosa medida contra o teto da lei: todos os campos da cessão achados somam 861,7 milhões de barris de óleo equivalente,
  cerca de 17% de 5 bilhões. É aproximado: "SUL DE LULA" só aparece em 2019, sem produção, e "SUL DE TUPI" só a partir de 2022.

## 4. Pessoas com papel em documento oficial (GD23)

Critério: só quem sancionou, assinou ou relatou. Quem aparece só citado em notícia ou acórdão, sem decisão, fica fora. Os nomes
estão grafados como no documento; quando o documento traz erro de grafia, o nome correto vem com a nota.

**Pelo poder público e pelas estatais**

| Nome | Cargo na época | Ato (número, data) | Link |
|---|---|---|---|
| Luiz Inácio Lula da Silva | Presidente da República | sancionou a Lei 12.276, 30/06/2010 | https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12276.htm |
| Guido Mantega | Ministro de Estado da Fazenda | assinou a Lei 12.276 (30/06/2010) e o contrato de cessão onerosa pela União (03/09/2010) | Planalto; DOU 21/09/2010, Seção 3, p. 80 (https://pesquisa.in.gov.br/imprensa/jsp/visualiza/index.jsp?jornal=3&pagina=80&data=21/09/2010) |
| Márcio Pereira Zimmermann | Ministro de Estado de Minas e Energia | assinou a Lei 12.276 (30/06/2010; o Planalto grafa "Zimmernam") e o contrato (03/09/2010) | Planalto; DOU 21/09/2010 |
| Adriana Queiroz de Carvalho | Procuradora-Geral da Fazenda Nacional | assinou o contrato pela União, 03/09/2010 | DOU 21/09/2010 |
| José Sergio Gabrielli de Azevedo | Presidente da Petrobras | assinou o contrato pela Petrobras, 03/09/2010 | DOU 21/09/2010 |
| Almir Guilherme Barbassa | Diretor da Petrobras | assinou o contrato, 03/09/2010 (o DOU grafa "BARBOSSA") | DOU 21/09/2010 |
| Guilherme de Oliveira Estrella | Diretor da Petrobras | assinou o contrato, 03/09/2010 | DOU 21/09/2010 |
| Haroldo Borges Rodrigues Lima | Diretor-Geral da ANP | assinou o contrato pela ANP, 03/09/2010 | DOU 21/09/2010 |
| Jair Messias Bolsonaro | Presidente da República | sancionou a Lei 13.885, 17/10/2019 | https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/L13885.htm |
| Paulo Guedes | Ministro de Estado da Economia | assinou a Lei 13.885, 17/10/2019 (o Planalto grafa "Paulo Gudes") | Planalto |
| Bento Costa Lima Leite de Albuquerque Júnior | Ministro de Estado de Minas e Energia | assinou a Lei 13.885 (17/10/2019), os contratos de partilha nº 1/2020 e 2/2020 (30/03/2020) e nº 01/2022 e 02/2022 (27/04/2022) | Planalto; ANP, extratos no DOU de 01/04/2020 e 02/05/2022 |
| Felipe Kury | Diretor-Geral Substituto da ANP | assinou o aviso de homologação e adjudicação da 1ª rodada, DOU de 18/11/2019 | https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/1a-lveco/arquivos/assinatura-de-contratos/homologacao-adjudicacao-lveco.pdf |
| José Gutman | Diretor-Geral da ANP | assinou os contratos nº 1/2020 e 2/2020, 30/03/2020 | https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/1a-lveco/arquivos/assinatura-de-contratos/extrato-contratos-lveco-dou-01042020.pdf |
| José Eduardo Vinhaes Gerk | Presidente da PPSA | assinou os contratos de 30/03/2020 e de 27/04/2022 | extratos no DOU de 01/04/2020 e 02/05/2022 |
| Roberto da Cunha Castello Branco | Presidente da Petrobras | assinou os contratos nº 1/2020 e 2/2020, 30/03/2020 | extrato no DOU de 01/04/2020 |
| Rodolfo Henrique de Saboia | Diretor-Geral da ANP | assinou o resultado de julgamento da 2ª rodada (DOU 23/12/2021; o DOU grafa "HENIRQUE") e os contratos de 27/04/2022 | https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/2-lveco/arq/resultado_julgamento_anp_lveco2_dou_23122021.pdf |
| José Mauro Ferreira Coelho | Presidente da Petrobras | assinou os contratos nº 01/2022 e 02/2022, 27/04/2022 | https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/2-lveco/arq/assinatura-de-contratos/extratos_dou_02-05-22_atapu-e-sepia.zip |

**Pelas empresas contratadas** (assinaram os contratos de partilha; D48 inclui todos com papel em documento oficial, revendo D36)

| Nome | Cargo na época | Ato | Link |
|---|---|---|---|
| Guangfeng Wan | Diretor-Geral da CNODC Brasil Petróleo e Gás Ltda. | contrato nº 1/2020 (Búzios), 30/03/2020 | extrato no DOU de 01/04/2020 |
| Jianbo Sheng | Presidente da CNOOC Petroleum Brasil Ltda. | contrato nº 1/2020 (Búzios), 30/03/2020 | extrato no DOU de 01/04/2020 |
| André Lopes de Araujo | Diretor Presidente da Shell Brasil Petróleo Ltda. | contrato nº 01/2022 (Atapu), 27/04/2022 | extrato no DOU de 02/05/2022 |
| David John Mendelson | Vice-Presidente Sênior Américas, Exploração e Produção, TotalEnergies EP Brasil Ltda. | contratos nº 01/2022 e 02/2022, 27/04/2022 | extrato no DOU de 02/05/2022 |
| Mark Fitzgerald | Vice-Presidente de Ativos Internacionais da Petronas Petróleo Brasil Ltda. | contrato nº 02/2022 (Sépia), 27/04/2022 | extrato no DOU de 02/05/2022 |
| Ali Abdulla S M Al-Mana | Procurador da QP Brasil Ltda. | contrato nº 02/2022 (Sépia), 27/04/2022 | extrato no DOU de 02/05/2022 |

**Relatores no TCU** (ver seção 6): José Jorge; José Mucio Monteiro; Raimundo Carreiro; Bruno Dantas; Walton Alencar Rodrigues;
Augusto Nardes; Antonio Anastasia.

**Caso para decisão do autor (não publicar sem decidir).** José Cesário Cecchi, Diretor-Geral Substituto da ANP, foi ouvido em
audiência pelo TCU no processo da revisão; o Acórdão 2.309/2021-Plenário decidiu "acolher, em parte, as razões de justificativa
apresentadas por José Cesário Cecchi, deixando de aplicar a penalidade [...] em face da baixa reprovabilidade da conduta do
responsável". Há decisão sobre a conduta, sem sanção. Pela regra de D48 ele tem papel em documento oficial; pela cautela de D51,
recomenda-se mostrar só se a página trouxer a frase inteira do acórdão.

Ficam fora, por aparecerem só citados: o deputado autor da representação julgada prejudicada no Acórdão 2.319/2019; o secretário
especial de Fazenda citado na nota de 27/12/2019; o ministro citado na nota de 20/05/2022; o presidente da Petrobras citado no
texto de 01/11/2019 sobre o aditivo (os signatários do aditivo não foram localizados, seção 8).

Total na tela, se o autor aprovar: 17 pelo poder público e estatais, 6 pelas empresas, 7 relatores do TCU (30 pessoas), mais 1 caso
para decisão.

## 5. Quem governava em cada data do caso

Mesmo critério para todos: cargo comprovado por ato assinado na data ou por decreto; partido pela fonte do projeto
(`data/politicians/union.json`, TSE e Agência Brasil) quando houver; sem fonte, fica "não confirmado".

| Data | Evento | Presidente da República (partido na data) | Ministro de Minas e Energia | Ministro da Fazenda / Economia |
|---|---|---|---|---|
| 30/06/2010 | Lei 12.276 | Luiz Inácio Lula da Silva (PT; mandato 01/01/2007 a 01/01/2011; registro do TSE de 2006 não aberto nesta pesquisa) | Márcio Pereira Zimmermann (assinou a lei; partido não confirmado) | Guido Mantega, Fazenda (assinou a lei; partido não confirmado) |
| 03/09/2010 | Contrato de cessão onerosa | Lula | Zimmermann (assinou) | Mantega (assinou) |
| 17/10/2019 | Lei 13.885 | Jair Messias Bolsonaro (PSL; desfiliação em 19/11/2019) | Bento Albuquerque (assinou; sem partido conhecido) | Paulo Guedes, Economia (assinou; "nenhuma filiação encontrada nas fontes oficiais consultadas", `union.json`) |
| 01/11/2019 | Aditivo da revisão | Bolsonaro (PSL) | Bento Albuquerque (no cargo; ver 17/10/2019) | Guedes |
| 06/11/2019 | 1ª rodada | Bolsonaro (PSL) | Bento Albuquerque | Guedes |
| 10 a 31/12/2019 | Bônus recebido, Petrobras paga, repasse | Bolsonaro (sem partido, de 19/11/2019 a 30/11/2021) | Bento Albuquerque | Guedes |
| 30/03/2020 | Contratos de Búzios e Itapu | Bolsonaro (sem partido) | Bento Albuquerque (assinou) | Guedes |
| 17/12/2021 | 2ª rodada | Bolsonaro (PL, desde 30/11/2021) | Bento Albuquerque | Guedes |
| 27/04/2022 | Contratos de Sépia e Atapu | Bolsonaro (PL) | Bento Albuquerque (assinou) | Guedes |
| 20 e 24/05/2022 | Repasse de R$ 7,68 bi | Bolsonaro (PL) | Adolfo Sachsida (citado como ministro na nota oficial de 20/05/2022; data de posse não confirmada) | Guedes |

Mandatos e filiação de Bolsonaro e Guedes: `data/politicians/union.json` (TSE 2018 e 2022; Agência Brasil para a desfiliação de
19/11/2019 e a filiação ao PL em 30/11/2021; decreto de nomeação de Guedes no DOU de 01/01/2019). Os períodos completos de
Zimmermann, Mantega e Bento Albuquerque no cargo não foram confirmados em decreto nesta pesquisa; a tabela só afirma que estavam no
cargo nas datas em que assinaram.

## 6. Linha do tempo dos órgãos de controle (TCU)

Fonte: base de jurisprudência do TCU (https://pesquisa.apps.tcu.gov.br), campo "acórdão" de cada decisão. Todos do Plenário.

| Acórdão | Sessão | Relator | Processo | O que decidiu (palavras do acórdão) |
|---|---|---|---|---|
| 3.087/2014 | 12/11/2014 | José Jorge | TC 024.607/2014-2 | Determinou ao MME que, quanto aos "volumes excedentes nas reservas destinadas à cessão onerosa, somente dê prosseguimento à contratação direta da Petrobras após o aprimoramento dos estudos técnicos". |
| 1.433/2015 | 10/06/2015 | José Mucio Monteiro | TC 011.325/2015-1 | "autorizar a realização de acompanhamento na revisão do contrato de cessão onerosa". |
| 353/2016 | 24/02/2016 | José Mucio Monteiro | TC 011.325/2015-1 | Determinou que MME, Petrobras e ANP "reduzam a termo todas as reuniões técnicas"; recomendou ao CNPE "contornar as deficiências do contrato de cessão onerosa quanto às premissas estipuladas para sua revisão"; alertou para riscos como "perdas de royalties, adiamento de receitas". |
| 449/2016 | 02/03/2016 | Raimundo Carreiro | TC 024.607/2014-2 | Deu "provimento parcial" ao pedido de reexame do MME e reescreveu a condição para a contratação direta da Petrobras. |
| 2.931/2018 | 12/12/2018 | José Mucio Monteiro | TC 011.325/2015-1 | Avisou o CNPE e o MME de que era "necessário o envio complementar dos estudos técnicos e econômicos", incluindo "o valor resultante da revisão, discriminado por bloco". |
| 2.319/2019 | 02/10/2019 | Bruno Dantas | TC 008.284/2019-9 | Representação sobre o pagamento à Petrobras: "julgar prejudicada a representação em razão da perda do seu objeto". |
| 2.430/2019 | 09/10/2019 | Raimundo Carreiro | TC 001.281/2019-4 | Edital da 1ª rodada: ANP e MME "atenderam com ressalvas"; entre as ressalvas, "Inconsistências técnicas de fundamentação de premissas que balizaram a modelagem do leilão e o cálculo da compensação a ser paga à Petrobras". |
| 2.548/2019 | 23/10/2019 | Raimundo Carreiro | TC 011.325/2015-1 | Revisão: os procedimentos "atendem, com ressalvas, aos aspectos de economicidade, eficiência e eficácia [...], não havendo óbices à assinatura do Termo Aditivo"; ressalvas incluem "Excessiva demora para realização do processo de revisão do contrato". |
| 2.309/2021 | 29/09/2021 | Raimundo Carreiro | TC 011.325/2015-1 | Acolheu em parte as razões de justificativa de um responsável da ANP, sem multa; arquivou o processo da revisão. |
| 2.480/2021 | 13/10/2021 | Walton Alencar Rodrigues | TC 045.221/2020-0 | Edital da 2ª rodada: ANP e MME "atenderam aos aspectos de tempestividade, completude e suficiência técnica"; recomendou "considerar os efeitos na arrecadação estatal total, em valor presente líquido, de antecipações de receitas governamentais, via bônus de assinatura". |
| 1.260/2023 | 21/06/2023 | Augusto Nardes | TC 042.484/2021-9 | Compartilhamento de Búzios e Itapu e compensação à Petrobras: "não há indícios de que [...] a definição do valor a ser pago a título de compensação [...] não tenha sido feito de forma coerente". |
| 258/2024 | 21/02/2024 | Antonio Anastasia | TC 001.281/2019-4 | 1ª rodada: a ANP "observou, sob os aspectos procedimental e formal, os ditames do edital". |
| 513/2024 | 27/03/2024 | Walton Alencar Rodrigues | TC 045.221/2020-0 | 2ª rodada: a ANP "atendeu aos requisitos previstos nos artigos 3º e 8º da IN-TCU 81/2018". |

Notas: os números de processo vêm do campo `PROC` da base (ex.: 128120194 = TC 001.281/2019-4). A notícia do TCU de 27/02/2024 sobre
o Acórdão 258/2024 escreve "Sessão: 21/2/2023"; a base registra 21/02/2024. Não foi achado acórdão do TCU de 2010 sobre o valor
inicial do contrato.

## 7. Comparação honesta (D48)

**Comparação proposta:** os quatro contratos do excedente contra Libra (1ª rodada de partilha, 21/10/2013), o leilão mais parecido:
pré-sal da Bacia de Santos, regime de partilha, bônus fixo no edital e disputa pelo percentual de óleo lucro da União. Libra virou o
campo de Mero (ANP, sumário executivo do AIP de Mero: "O poço 2-ANP-2A-RJS, descobridor da acumulação de Libra"; produção "por
meio de um Sistema de Produção Antecipada (SPA) com o FPSO Pioneiro de Libra",
https://www.gov.br/anp/pt-br/assuntos/exploracao-e-producao-de-oleo-e-gas/desenvolvimento-e-producao/pd/rd-0758-mero-e-anc-sumario-executivo-aip.pdf).

**Método.** Para cada área, duas medidas lado a lado, com dado oficial e o mesmo corte (julho de 2026):
- (a) bônus de assinatura em R$ de dez/2024 dividido pelos barris já produzidos no contrato de partilha (PPSA, acumulado);
- (b) parcela da União na produção já ocorrida (PPSA, parcela acumulada sobre produção acumulada).
A medida (a) favorece quem cobrou bônus alto; a (b) favorece quem disputou óleo lucro. Nenhuma das duas decide sozinha: a (b) ainda
muda muito, porque o custo em óleo (incluída a compensação à Petrobras, Acórdão 1.260/2023) é recuperado primeiro.

| Área | Data do leilão | Bônus (R$ de dez/2024) | Empresas ofertantes / vencedoras na rodada (ANP) | Óleo lucro mínimo / vencedor | Produção acumulada (MMbbl) | (a) Bônus por barril produzido | (b) Parcela da União |
|---|---|---|---|---|---|---|---|
| Libra (Mero) | 21/10/2013 | 28,32 bi (R$ 15 bi; fator 1,88828) | 5 / 5 (bloco único) | 41,65% / 41,65% | 595,00 | R$ 47,60 | 19,3% |
| Búzios | 06/11/2019 | 91,01 bi | 3 / 3 (rodada) | 23,24% / 23,24% | 890,72 | R$ 102,18 | 1,4% |
| Itapu | 06/11/2019 | 2,36 bi | Petrobras sozinha | 18,15% / 18,15% | 85,38 | R$ 27,61 | 7,3% |
| Sépia | 06/11/2019 | (R$ 22,86 bi pedido) | "Sem ofertas" | 27,88% / sem oferta | | | |
| Atapu | 06/11/2019 | (R$ 13,74 bi pedido) | "Sem ofertas" | 26,23% / sem oferta | | | |
| Sépia | 17/12/2021 | 8,28 bi | 5 / 5 (rodada); ANP: "conseguimos obter competição" | 15,02% / 37,43% | 145,60 | R$ 56,88 | 7,7% |
| Atapu | 17/12/2021 | 4,64 bi | idem | 5,89% / 31,68% | 113,96 | R$ 40,74 | 2,3% |

Fontes: ANP, `resultados-partilha-producao.xlsx` (Libra: bônus de R$ 15.000 milhões, excedente mínimo e ofertado de 41,65%, 5
empresas ofertantes) e `resultados-licitacoes-volumes-excedentes-ce.xlsx`; PPSA, Boletim nº 76; IPCA conforme o topo.

**O que a comparação mostra, sem conclusão de mérito.** Búzios rendeu o maior bônus por barril já produzido e a menor parcela de
óleo da União até agora; Libra, o contrário. Sépia e Atapu foram oferecidas duas vezes: com bônus de R$ 36,6 bi não houve oferta
(2019); com bônus de R$ 11,14 bi houve disputa e o óleo lucro subiu acima do mínimo (2021). O próprio TCU, no Acórdão 2.480/2021,
recomendou pesar "antecipações de receitas governamentais, via bônus de assinatura" contra "alíquota mínima de partilha". A
comparação só fecha quando a parcela da União for medida ao longo da vida dos campos; a página pode atualizar a coluna (b) todo mês
com o boletim da PPSA.

**Comparação não usada, e por quê.** Bônus por barril de reserva estimada: a ANP diz que "Os volumes estimados para cada área são
sigilosos" e só publica a faixa total do excedente ("de 6 a 15 bilhões de barris", apresentação de 01/11/2019); o volume oficial
de Libra não foi aberto nesta pesquisa. Com faixas tão largas, a conta pode dar qualquer resultado.

## 8. O que não foi confirmado

- **Signatários e texto do Termo Aditivo de 01/11/2019** (revisão): o extrato no DOU não foi achado (busca do DOU voltou vazia). Só
  há o texto da Petrobras e a apresentação da ANP.
- **Valor da revisão em dólares:** Petrobras escreve US$ 9,058 bi; o sumário executivo do TCU escreve US$ 9,048 bi. Não foi lido o
  aditivo nem a resolução do CNPE que aprovou a revisão.
- **Câmbio do contrato de 2010:** a ANP fala em US$ 42,5 bi, que não bate com a PTAX do dia (daria US$ 43,3 bi); o câmbio
  contratual não foi localizado.
- **Uso dos R$ 74,8 bi em 2010** (parte em LFT na capitalização, parte ao primário): o número de R$ 67,8 bi em LFT está no sumário do
  TCU ("valores aproximados") e num estudo da Consultoria Legislativa da Câmara (2011,
  https://bd-rest.camara.leg.br/server/api/core/bitstreams/0aafb9a1-7e79-4169-aa5a-3f6cc6367293/content), que cita a STN; a
  divisão de R$ 42,9 bi e R$ 21,9 bi vem só desse estudo e não foi conferida no Tesouro.
- **Data do pagamento do bônus da 2ª rodada:** só o indício do RTN (fevereiro de 2022).
- **Diferença de R$ 12,1 mi** entre o repasse anunciado em 2022 (R$ 7.676,2 mi) e o RTN de maio de 2022 (R$ 7.664,1 mi).
- **Divisão do repasse por ente** (15% estados, 3% confrontantes, 15% municípios): a tabela dá cálculo pela lei; o valor por UF e
  município está no link "Acesse aqui os repasses para cada estado e município" da nota de 20/05/2022, que não foi aberto.
- **Royalties e participação especial pagos pelos campos da cessão onerosa e do excedente, em reais**, e **receita da venda do óleo
  da União pela PPSA por contrato**.
- **Compensação paga pelos novos sócios à Petrobras em Sépia e Atapu** (Portaria MME nº 519/2021): não lida.
- **Mandatos completos** de Zimmermann, Mantega e Bento Albuquerque, e partido de Lula em 2010 pelo TSE (2006); a data de posse de
  Adolfo Sachsida.
- **Volume oficial estimado de Libra.**
- **Produção de Sul de Tupi (Sul de Lula) de 2019 a 2021**, possivelmente registrada em outro campo unitizado.

## 9. Fontes

Leis e atos
- Lei 12.276/2010: https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12276.htm
- Lei 13.885/2019 (com o § 4º da LC 176/2020): https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/L13885.htm
- DOU 21/09/2010, Seção 3, p. 80 (extrato do contrato de cessão onerosa): https://pesquisa.in.gov.br/imprensa/jsp/visualiza/index.jsp?jornal=3&pagina=80&data=21/09/2010
- Portaria MME nº 265/2019 (acordo de coparticipação): https://www.gov.br/mme/pt-br/acesso-a-informacao/legislacao/portarias/2019/portaria-n-265-2019.pdf

ANP
- 1ª rodada: https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/1a-lveco (resultados, assinatura de contratos)
- 2ª rodada: https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/2-lveco (resultados, assinatura dos contratos)
- Planilha de resultados do excedente: https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/resultados/arquivos/resultados-licitacoes-volumes-excedentes-ce.xlsx
- Planilha de resultados da partilha (Libra): https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/resultados/arquivos/resultados-partilha-producao.xlsx
- Extratos dos contratos, DOU 01/04/2020: https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/1a-lveco/arquivos/assinatura-de-contratos/extrato-contratos-lveco-dou-01042020.pdf
- Homologação, DOU 18/11/2019: https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/1a-lveco/arquivos/assinatura-de-contratos/homologacao-adjudicacao-lveco.pdf
- Resultado de julgamento, DOU 23/12/2021: https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/2-lveco/arq/resultado_julgamento_anp_lveco2_dou_23122021.pdf
- Extratos, DOU 02/05/2022: https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/2-lveco/arq/assinatura-de-contratos/extratos_dou_02-05-22_atapu-e-sepia.zip
- Mapa do resultado da 2ª rodada: https://www.gov.br/anp/pt-br/rodadas-anp/rodadas-concluidas/lveco/2-lveco/arq/resultados/co_resultado_v2.pdf
- Apresentação de 01/11/2019: https://www.gov.br/anp/pt-br/centrais-de-conteudo/apresentacoes-palestras/2019/arquivos/2019/2019-11-01_decio-oddone_assinatura-cessao-onerosa.pdf
- Notícia da 2ª rodada, 17/12/2021 (cópia do Internet Archive de 29/04/2024): https://www.gov.br/anp/pt-br/canais_atendimento/imprensa/noticias-comunicados/segunda-rodada-da-cessao-onerosa-tem-as-duas-areas-arrematadas
- Produção em mar por poço (dados abertos): https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/fase-de-desenvolvimento-e-producao
- Sumário executivo do AIP de Mero: https://www.gov.br/anp/pt-br/assuntos/exploracao-e-producao-de-oleo-e-gas/desenvolvimento-e-producao/pd/rd-0758-mero-e-anc-sumario-executivo-aip.pdf

PPSA
- Boletim Mensal nº 76 (julho de 2026): https://www.presalpetroleo.gov.br/wp-content/uploads/2026/09/JULHO_Boletim_mensal-PPSA.pdf

Tesouro e governo federal
- RTN, série histórica mensal: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Ministério da Economia, 27/12/2019 e 31/12/2019 (cópias do Internet Archive de 17/01/2022): links na seção 2
- gov.br, 20/05/2022 (cópia de 11/11/2022): https://www.gov.br/pt-br/noticias/financas-impostos-e-gestao-publica/2022/05/governo-federal-vai-repassar-r-7-7-bilhoes-para-estados-e-municipios
- Casa Civil, 02/05/2022 (cópia de 02/05/2022): https://www.gov.br/casacivil/pt-br/assuntos/noticias/2022/maio/governo-federal-assina-contratos-de-exploracao-e-producao-de-petroleo-e-gas-natural-dos-campos-de-sepia-e-atapu-sp (o texto dá "R$ 7,7 bilhões" de bônus para Sépia; a ANP dá R$ 7,138 bi, que é o número usado)

Petrobras
- "Assinamos Aditivo ao Contrato de Cessão Onerosa", 01/11/2019 (cópia do Internet Archive de 14/11/2019): https://petrobras.com.br/fatos-e-dados/assinamos-aditivo-ao-contrato-de-cessao-onerosa.htm

TCU
- Base de acórdãos: https://pesquisa.apps.tcu.gov.br (Acórdãos 3.087/2014, 1.433/2015, 353/2016, 449/2016, 2.931/2018, 2.319/2019, 2.430/2019, 2.548/2019, 2.309/2021, 2.480/2021, 1.260/2023, 258/2024, 513/2024)
- Sumário executivo "Cessão Onerosa: as soluções criadas para uma outorga atípica" (2020): https://portal.tcu.gov.br/data/files/B9/E3/4E/F6/9FA0671053455957F18818A8/Sumario_executivo_cessao_onerosa_solucoes_criadas_outorga_atipica.pdf
- Notícias de 26/02/2016, 21/01/2019 e 27/02/2024: https://portal.tcu.gov.br/imprensa/noticias/

IBGE e BCB
- IPCA, SIDRA 1737: https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/201009,201310,201912,202112,202205,202412
- PTAX: https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/
