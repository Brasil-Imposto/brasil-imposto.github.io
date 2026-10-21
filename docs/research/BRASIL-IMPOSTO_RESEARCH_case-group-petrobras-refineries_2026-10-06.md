# Refinarias da Petrobras: Abreu e Lima (RNEST), Comperj e Pasadena

> **Situação em 2026-10-14:** pesquisa pausada na rodada 11 (fica para depois da v1). Os arquivos de dados citados abaixo em `data/works/` ainda não existem.

**English summary.** Official-source research on three Petrobras refinery cases (RNEST in Ipojuca/PE, Comperj in Itaboraí/RJ,
Pasadena in Texas/USA): what each was, who decided and when, official budget vs final cost, impairments, TCU findings, money
recovered, and today's status. Every figure is read at the primary document (TCU, Petrobras filings, CVM, CPI, courts); press only as leads.

**Data da coleta:** 2026-10-06 (todas as consultas nesta data, salvo indicação)
**Pergunta:** para cada refinaria, o que era, onde, quem decidiu e quando, quanto custaria pelo orçamento oficial, quanto custou,
quanto a Petrobras baixou como perda (impairment), o que o TCU e os outros órgãos oficiais registraram, quanto foi recuperado e
qual é a situação hoje.
**Ponto de partida (D108):** RNEST, Comperj, Pasadena e o cartel de empreiteiras da Lava Jato; cada número desta página vem de documento oficial.
**Dados:** `data/works/rnest-abreu-e-lima.json`, `data/works/comperj.json`, `data/works/pasadena.json`.

## Regras desta pesquisa

1. Só documentos oficiais (TCU, CGU, AGU, Petrobras, CVM, CPI, tribunais, MPF, DOU, ANP), com as palavras do órgão. Imprensa só como pista.
2. Toda alegação com a situação oficial: indício, denúncia, condenação, condenação anulada (data e tribunal), acordo de leniência, arquivamento.
3. Pessoas só quando nomeadas numa decisão oficial, com a situação. O mesmo tratamento para todo partido e todo governo.
4. Nenhum número sem URL oficial, moeda e ano de referência. Somas marcadas como "calculado" são desta pesquisa.
5. Fonte que não abriu: "não confirmado".
6. Travessões dos originais trocados por vírgula ou parênteses (regra de estilo do projeto).

## 0. Resumo

(preenchido no fim)

## 3. Pasadena (Texas, Estados Unidos)

**Arquivo de dados:** `data/works/pasadena.json`.

### 3.1 O que foi

- A compra, pela Petrobras America Inc. (PAI, subsidiária da Petrobras), da refinaria Pasadena Refining System Inc. (PRSI) e da
  comercializadora PRSI Trading Company (PRST), do grupo belga Astra Transcor. A primeira metade foi comprada em 2006; a segunda,
  depois de arbitragem e processos nos Estados Unidos, em 2012. Capacidade: "110,000 bpd", na cidade de Pasadena, Texas
  (Petrobras, comunicado de 30/01/2019, abaixo).
- Não é obra: é uma compra de empresa. Não há dinheiro do Orçamento da União; o dinheiro é da Petrobras, empresa de economia
  mista controlada pela União.

### 3.2 O preço da vendedora um ano antes (pista do autor)

- TCU, Acórdão 1927/2014-Plenário (voto, item 17): "Em janeiro de 2005, o grupo belga Astra Transcor (vinculado à holding
  NPM/CNP) adquiriu 100% das ações da refinaria americana PRSI por US$ 42,5 milhões, junto à Crown Central Petroleum Corporation
  (Crown)". **Confirmado**, com a ressalva de que o valor é o que o TCU registra a partir dos documentos da Petrobras.
  [Acórdão 1927/2014](https://pesquisa.apps.tcu.gov.br/doc/acordao-completo/1927/2014/Plen%C3%A1rio), sessão de 23/07/2014.

### 3.3 Quanto a Petrobras pagou (tabela do TCU)

TCU, Acórdão 1927/2014-Plenário, voto, item 35, "Preço Pago por 100% das Ações da Refinaria e da Trading":

| Parcela | US$ |
|---|---|
| Preço contratual inicial pelos 50% da refinaria, com adiantamentos de maio de 2006 | 189.000.000,00 |
| Alocação especial pelos 50% da PRSI Trading Company | 170.285.714,30 |
| Ajustes de preço da refinaria (cláusula 5.04 do SPA) | 66.411.500,00 |
| Compra dos 50% restantes da PRSI | 342.416.009,04 |
| Encerramento das demais disputas | 478.083.990,96 |
| **Preço total por 100% da refinaria e da trading** | **1.245.697.714,30** |

Conferência (calculado): a soma das cinco linhas como o TCU as publica dá US$ 1.246.197.214,30, US$ 499.500,00 a mais do que o total da mesma tabela (US$ 1.245.697.714,30). O acórdão não explica a diferença; o site usa o total escrito pelo TCU e registra a diferença.

O mesmo acórdão registra o acordo extrajudicial de 2012 (TOTAL "MM US$ 820,5", referenciado a 30/4/2012), aprovado pelo
Conselho de Administração em 13/6/2012 (Ata CA 1.368).

### 3.4 Quem decidiu e quando (documentos citados pelo TCU)

| Data | Ato | Fonte |
|---|---|---|
| 02/02/2006 | Diretoria Executiva aprova a assinatura dos contratos (Ata DE 4.567), por proposta do Diretor da Área Internacional (DIP INTER-DN 20/2006) | TCU, Acórdão 1927/2014, item 9.3.1 |
| 03/02/2006 | Conselho de Administração, reunião n. 1.268, autoriza a compra de 50% | TCU, Acórdão 1927/2014, voto |
| 13/06/2012 | Conselho de Administração aprova o acordo extrajudicial com a Astra (Ata CA 1.368) | TCU, Acórdão 1927/2014, relatório |
| 30/01/2019 | PAI assina a venda de toda a refinaria à Chevron U.S.A. | Petrobras, 6-K de 31/01/2019 |
| 01/05/2019 | Venda concluída | Petrobras, 6-K de 02/05/2019 |

O voto do Acórdão 1927/2014 registra que a apresentação feita ao Conselho de Administração em 3/2/2006 "deixou de mencionar a
cláusula que garantia rentabilidade de 6,9% para o processamento do óleo de Marlim e também as condições para o exercício do Put
Option que viriam a constar dos contratos".

**Quem governava** (presidente da República; Pasadena fica fora do Brasil, sem governador):
- fev/2006: Luiz Inácio Lula da Silva, eleito em 2002 pelo PT (TSE, `consulta_cand_2002_BR.csv`: "LUIZ INACIO LULA DA SILVA", "PT", "ELEITO").
- jun/2012: Dilma Rousseff, eleita em 2010 pelo PT (TSE, `consulta_cand_2010_BR.csv`: "DILMA VANA ROUSSEFF", "PT", "ELEITO").
- jan a mai/2019: Jair Bolsonaro, eleito em 2018 pelo PSL (TSE 2018, já registrado em `data/politicians/union.json`).

### 3.5 Achados oficiais (TCU)

| Decisão | Data | O que decidiu | Situação |
|---|---|---|---|
| Acórdão 1927/2014-Plenário (TC 005.406/2013-7) | 23/07/2014 | Converteu a representação em tomada de contas especial e mandou citar os responsáveis por quatro parcelas de prejuízo: US$ 580.428.571,30 (compra de 50% "desconsiderando o laudo" da Muse & Stancil de US$ 186 milhões), US$ 39.700.000,00, US$ 79.890.000,00 (carta de intenções) e US$ 92.300.000,00 (adiamento do cumprimento da sentença arbitral); bloqueou bens por um ano | indício (citação); soma calculada das quatro parcelas: US$ 792.318.571,30 |
| Acórdão 440/2017 e 835/2021 (TC 005.259/2015-0) | 15/03/2017 e 14/04/2021 | Parcela de US$ 39,7 milhões "descaracterizada"; processo arquivado sem julgamento do mérito | arquivamento |
| Acórdão 1881/2017 (TC 005.261/2015-5) | 30/08/2017 | Parcela de US$ 92,3 milhões (sentença arbitral): contas julgadas regulares, "quitação plena". Parcela de US$ 79,89 milhões (carta de intenções): contas irregulares, débito solidário de José Sérgio Gabrielli de Azevedo e Nestor Cuñat Cerveró, multa de R$ 10 milhões a cada um e inabilitação por 8 anos | para Cerveró, anulado pelo Acórdão 899/2019 e refeito pelo Acórdão 1099/2019 (mesma condenação); recursos negados no Acórdão 2329/2020 |
| Acórdão 834/2021 (TC 025.551/2014-0) | 14/04/2021 | Prejuízo pela compra acima do valor: contas irregulares e débito solidário de **US$ 453.296.325,17** (R$ 1.109.216.107,69 na conversão de 17/10/2014; "Valor atualizado até 14/12/2018: R$ 1.594.916.340,37") contra Aurélio Oliveira Telles, Cezar de Souza Tavares, Luís Carlos Moreira da Silva, Rafael Mauro Comino (comissão de negociadores), Nestor Cuñat Cerveró, Paulo Roberto Costa e José Sérgio Gabrielli de Azevedo; multa de R$ 110 milhões a Luís Carlos Moreira da Silva, Nestor Cuñat Cerveró e José Sérgio Gabrielli de Azevedo; multa de R$ 67.854,00 a Almir Guilherme Barbassa, Guilherme de Oliveira Estrella, Ildo Luis Sauer e Renato de Souza Duque; contas dos ex-membros do Conselho de Administração Antônio Palocci Filho, Claudio Luis da Silva Haddad, Fabio Colletti Barbosa, Gleuber Vieira e Dilma Vana Rousseff julgadas "regulares com ressalva" | condenação pelo TCU (decisão administrativa); embargos rejeitados no Acórdão 2636/2022 (30/11/2022), que afirma a "não ocorrência da prescrição" |
| Acórdão 836/2021 (TC 035.952/2016-4) | 14/04/2021 | Empresa Astra Oil Company LLC revel, contas irregulares, débito solidário com os responsáveis do Acórdão 834/2021 e multa de R$ 330 milhões | condenação pelo TCU |

Quanto desse débito foi efetivamente pago: **não confirmado** (nenhum documento oficial aberto com valor recolhido).

### 3.6 A venda (2019)

- Petrobras, 6-K de 31/01/2019 ([SEC](https://www.sec.gov/Archives/edgar/data/1119639/000119312519022789/d682665d6k.htm)):
  "The transaction value comprises US$ 562 million, of which US$ 350 million corresponds to equity and US$ 212 million corresponds
  to working capital as of October 2018."
- Petrobras, 6-K de 02/05/2019 ([SEC](https://www.sec.gov/Archives/edgar/data/1119639/000119312519133831/d739871d6k.htm)):
  "The transaction closed today with the payment by Chevron to PAI of US$ 467 million (about R$ 1.8 billion), of which US$ 350
  million corresponds to equity and US$ 117 million corresponds to working capital, which will be adjusted later to reflect the
  closing date position."

### 3.7 Situação para a etiqueta

**"Concluído"** não se aplica bem a uma compra; a etiqueta proposta é **"Concluído"** com o sentido de caso encerrado no
negócio: a refinaria foi vendida e a venda foi concluída em 01/05/2019 (Petrobras, 6-K acima). O processo no TCU teve decisão de
mérito (2021) e embargos julgados (2022).

### 3.8 Para uma criança entender

1. Em 2005 uma empresa comprou uma refinaria nos Estados Unidos por 42,5 milhões de dólares (TCU, Acórdão 1927/2014).
2. Entre 2006 e 2012 a Petrobras pagou 1,25 bilhão de dólares pela mesma refinaria inteira (TCU, Acórdão 1927/2014).
3. O TCU decidiu em 2021 que sete pessoas e a empresa vendedora têm de devolver 453 milhões de dólares à Petrobras, e em 2019 a
   Petrobras vendeu a refinaria por 467 milhões de dólares (TCU, Acórdãos 834 e 836/2021; Petrobras, 2019).

