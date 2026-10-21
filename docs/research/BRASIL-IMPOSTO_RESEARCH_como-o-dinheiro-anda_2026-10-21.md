# Como o dinheiro do imposto anda no Brasil: arrecadação, repartição e gasto

English summary: how Brazilian tax money actually moves, read from the Constitution (Planalto, 2026-10-21) and sized with the
official 2025 figures already in the project (Tesouro RTN in the ledger, the 27 state RREOs). Three governments each levy their
own taxes; the Constitution then moves fixed shares between them (FPE, FPM, IPI-exportação, CIDE, ITR, IOF-ouro, the
municipalities' 25% of ICMS and 50% of IPVA); Fundeb pools 20% of a basket of state and municipal revenue and returns it by
enrollment, topped up by the União; each government spends what it keeps; the União also pays interest. The platform can mirror
this exactly: every movement is one flow between the same nodes, each sharing rule is one row with its article and percentage,
and every screen is a sum over the flows. That is the ledger already approved in D121; this document gives it the real rulebook.

Status: **pesquisa de 2026-10-21, pedida pelo autor antes da fase 2 da limpeza.** Regras lidas na Constituição Federal no
Planalto em 2026-10-21 (redação atual, com a EC 132/2023); tamanhos de 2025 do RTN do Tesouro (já no livro de fluxos, que bate
com o RTN linha por linha) e dos RREOs dos 27 estados (já em `data/series/state-budgets.json`).

### O pedido
O autor pediu a lógica exata de como o governo arrecada o dinheiro do imposto e como o redistribui, para usar a mesma lógica
na plataforma e deixá-la mais simples e fácil de manter (2026-10-21).

### A resposta em uma frase
O dinheiro faz sempre o mesmo caminho: **as pessoas e empresas pagam tributos a três governos; a Constituição manda cada governo
passar partes fixas aos outros; cada governo gasta o que ficou com ele; o que falta vira dívida, e a dívida cobra juros.**
Se a plataforma guardar o dinheiro exatamente nesse caminho, cada tela vira uma soma sobre os mesmos movimentos.

@@include BRASIL-IMPOSTO_RESEARCH_como-o-dinheiro-anda_2026-10-21.svg

## 1. Quem cobra o quê

Cada governo só cobra os tributos que a Constituição lhe dá. O DF cobra os do estado e os do município ao mesmo tempo.

| Governo | Tributos | Artigo |
|---|---|---|
| União | imposto de renda (IR), produtos industrializados (IPI), operações financeiras (IOF), importação (II), exportação (IE), propriedade rural (ITR); a partir de 2027, o imposto seletivo | CF art. 153 |
| União, para a seguridade | contribuições sobre a folha (previdência, INSS), sobre o faturamento (Cofins, PIS) e sobre o lucro (CSLL); a partir de 2027, a CBS no lugar do PIS e da Cofins | CF art. 195; ADCT art. 126 |
| Estados e DF | circulação de mercadorias e serviços (ICMS), veículos (IPVA), heranças e doações (ITCMD) | CF art. 155 |
| Municípios e DF | imóveis urbanos (IPTU), compra de imóveis (ITBI), serviços (ISS) | CF art. 156 |

Quem paga é sempre uma pessoa ou empresa que mora ou trabalha em algum estado (D120). O dado oficial nem sempre diz qual: a
Receita registra o imposto onde fica a sede de quem recolhe, por isso o DF, São Paulo e o Rio aparecem com imposto de empresas e
órgãos que têm sede ali.

## 2. Quem passa dinheiro para quem (as regras fixas)

O imposto de renda e o IPI são da União, mas metade não fica com ela. As regras abaixo são percentuais fixos sobre a arrecadação;
nenhuma depende de escolha do governo do momento.

| De | Para | Regra | Artigo |
|---|---|---|---|
| União | estados e DF | **FPE: 21,5%** do IR e do IPI (e, a partir de 2027, do imposto seletivo), repartido entre os estados pelos critérios da lei complementar (LC 62/1989) | CF art. 159, I, a |
| União | municípios | **FPM: 25,5%** do IR e do IPI: 22,5% por mês, mais 1% no primeiro decêndio de dezembro, 1% em julho e 1% em setembro | CF art. 159, I, b, d, e, f |
| União | bancos regionais (FNO, FNE, FCO) | **3%** do IR e do IPI, emprestados a empresas do Norte, Nordeste e Centro-Oeste; metade do Nordeste para o semiárido | CF art. 159, I, c |
| União | estados e DF | **IPI-exportação: 10%** do IPI, pela exportação de produtos industrializados de cada estado; nenhum estado passa de 20% | CF art. 159, II e § 2º |
| União | estados e DF | **CIDE-combustíveis: 29%** | CF art. 159, III |
| União | municípios | **ITR: 50%** do imposto dos imóveis rurais do município; 100% se o município cobra o imposto | CF art. 158, II |
| União | estado e município de origem | **IOF-ouro:** 30% ao estado e 70% ao município de onde o ouro saiu | CF art. 153, § 5º |
| (fica no ente) | estados, DF e municípios | o **IR retido na fonte dos salários que eles mesmos pagam** é deles: nunca passa pela União | CF arts. 157, I, e 158, I |
| estados | seus municípios | **25% do ICMS** (no mínimo 65% pelo valor adicionado em cada município e até 35% por lei estadual, com pelo menos 10 pontos por resultados de aprendizagem) e **50% do IPVA** | CF art. 158, III, IV e § 1º |
| estados | seus municípios | **25%** do que o estado recebe de IPI-exportação e de CIDE | CF art. 159, §§ 3º e 4º |
| União | estados e municípios | participação nos **royalties** de petróleo, gás, energia e minérios explorados no seu território, na forma da lei | CF art. 20, § 1º |

Na conta do Tesouro, essas repartições saem da receita antes de a União gastar: é a linha 2 do RTN ("transferências por
repartição de receita"), e a "receita líquida" da União é a receita total menos elas.

### O fundo comum da educação (Fundeb)

Em cada estado existe um fundo contábil. Entram nele **20%** do ICMS, do IPVA, do ITCMD, do FPE, do FPM, do IPI-exportação, do
ITR e das cotas que os estados passam aos municípios, do governo do estado e de cada prefeitura (CF art. 212-A, II). O fundo
devolve o dinheiro às redes pelo **número de alunos matriculados** (art. 212-A, III). A União **completa** o fundo com no mínimo
**23%** do total em 2026 (art. 212-A, V), depois de subir aos poucos desde 2021: 12%, 15%, 17%, 19%, 21% e 23% (ADCT art. 60).

Por isso o estado aparece duas vezes no RREO: uma linha que **sai** ("dedução para formação do Fundeb") e uma que **entra**
("transferências do Fundeb"). As duas são o mesmo fundo; só a diferença é dinheiro que mudou de dono.

### Os mínimos de gasto

O governo também não escolhe quanto gastar em educação e saúde: a União aplica pelo menos **18%** e estados, DF e municípios pelo
menos **25%** da receita de impostos, inclusive a que veio de repartição, em ensino (CF art. 212). Em saúde, a União aplica pelo
menos **15%** da receita corrente líquida, e estados e municípios os percentuais da lei complementar sobre os seus impostos e
repartições (CF art. 198, § 2º).

## 3. Os repasses que não são regra fixa

Além das regras, a União passa dinheiro a estados e municípios por decisão de lei ou de orçamento. Na conta do Tesouro eles
contam como **despesa** da União, não como repartição, mas o dinheiro faz o mesmo caminho: sai de um governo e é gasto por outro.

- **Complemento da União ao Fundeb** (RTN 4.3.10).
- **Fundo Constitucional do DF:** a União mantém a polícia civil, a polícia penal, a polícia militar e os bombeiros do DF e dá
  assistência financeira a outros serviços públicos dele, por meio de um fundo próprio (CF art. 21, XIV; RTN 4.3.11 e parte
  da folha em 4.2).
- **SUS, fundo a fundo,** e os outros repasses obrigatórios por lei.
- **Voluntários:** convênios e emendas parlamentares, inclusive as transferências especiais.
- **Compensações:** Lei Kandir e LC 176/2020 (RTN 4.3.13).

## 4. Quem gasta

Cada governo gasta o que ficou com ele depois das repartições. O gasto final é sempre um pagamento a uma pessoa ou empresa:
salário, aposentadoria, benefício, compra, obra, serviço. Duas exceções saem do país dos governos: os **juros da dívida**, pagos a
quem tem títulos (bancos, fundos, previdências, estrangeiros), e o **empréstimo**, que sai e volta.

A União paga direto às pessoas o que nenhum estado paga: a previdência do INSS, o BPC, o Bolsa Família, o seguro-desemprego e o
abono, a folha federal. Por isso o dinheiro federal "volta" a cada estado por dois caminhos: pelos governos (repartições e
repasses) e pelas pessoas (benefícios, salários e compras da União ali).

## 5. Os tamanhos de 2025

### União (RTN do Tesouro, 12 meses de 2025)

| Linha | O que é | R$ bi |
|---|---|---|
| 1 | Receita total | 2.902,3 |
| 1.1 | administrada pela Receita (IR, IPI, IOF, Cofins, PIS, CSLL e outras) | 1.859,8 |
| 1.3 | contribuição líquida para o INSS | 709,7 |
| 1.4 | não administrada pela Receita (royalties, dividendos, concessões e outras) | 332,7 |
| 2 | Repartida com estados e municípios por regra | 569,7 |
| 2.1 | FPM, FPE e IPI-exportação | 454,7 |
| 2.4 | exploração de recursos naturais (royalties) | 70,2 |
| 2.3 | salário-educação | 21,4 |
| 2.2 | fundos constitucionais (FNO, FNE, FCO) | 18,7 |
| 2.5 e 2.6 | CIDE e demais | 4,8 |
| 3 | Receita líquida, o que ficou com a União | 2.332,6 |
| 4 | Despesa total | 2.394,2 |
| 4.1 | aposentadorias e pensões do INSS | 1.026,9 |
| 4.2 | pessoal | 402,6 |
| 4.3 | outras obrigatórias (BPC 127,2; seguro-desemprego e abono 87,8; complemento do Fundeb 59,7; precatórios 42,8; outras) | 390,6 |
| 4.4 | sujeitas à programação financeira do Executivo (Bolsa Família 158,1; saúde 228,6; o custeio e o investimento dos ministérios) | 574,3 |
| 5 | Resultado primário (3 menos 4) | -61,7 |
| 9 | Juros nominais | -891,9 |
| 10 | Resultado nominal | -950,6 |

### Estados (RREO dos 27 estados, 12 meses de 2025)

| Linha | R$ bi |
|---|---|
| ICMS | 862,9 |
| IPVA | 94,0 |
| ITCMD | 20,2 |
| FPE recebido (bruto, antes do Fundeb) | 205,0 |
| Passado às prefeituras (26 estados; o DF não tem municípios) | 261,5 |
| Deduzido para o Fundeb | 187,3 |
| Recebido do Fundeb | 118,8 |

Os números dos estados vêm de cada RREO como o estado publicou. As prefeituras de SC, RS e do DF estão no projeto; as dos outros
estados ainda não.

## 6. A mesma lógica na plataforma

O caminho acima tem só seis tipos de movimento. Se cada movimento real vira uma linha, com de quem, para quem, mês, valor, regra
e fonte, a plataforma passa a ter uma base só, e cada tela é uma soma sobre ela.

| Movimento real | De para | Regra que o define | Onde está o dado |
|---|---|---|---|
| 1. tributo pago | pessoas e empresas de um estado para o governo que cobra | arts. 153, 155, 156, 195 | Receita por estado; RREO de estados e municípios |
| 2. repartição por regra | governo para governo | uma linha por regra, com artigo e percentual (seção 2) | RTN linha 2; Tesouro, transferências constitucionais; RREO |
| 3. fundo comum | estado e prefeituras para o Fundeb e de volta, por matrícula; complemento da União | art. 212-A; ADCT art. 60 | RREO (dedução e transferência do Fundeb); RTN 4.3.10 |
| 4. repasse por decisão | União para estado ou município | lei ou orçamento (seção 3) | Portal da Transparência; RTN 4.3 |
| 5. gasto final | governo para pessoas e empresas de um estado (salário, benefício, compra) | o orçamento de cada governo | Tesouro, Portal, INSS, MDS; RREO |
| 6. dívida | União para os credores (juros); empréstimos que saem e voltam | a lei de cada operação | Banco Central e Tesouro |

Fora dos governos: a exportação vai do exterior para as empresas e nunca passa por um caixa público.

**É exatamente o livro de fluxos já aprovado (D119 a D122):** os nós de lá (`gov:uniao`, `gov:uf`, `gov:mun`, `soc:uf`,
`fin:credores`, `ext:mundo`, mais `soc:unknown` para "sem informação de estado") são os donos do dinheiro deste caminho, e os
tipos de fluxo de lá são estes seis movimentos. O que esta pesquisa acrescenta é o livro de regras: cada repartição da seção 2
entra como uma linha da tabela de regras do livro, com o artigo e o percentual.

### O que fica mais simples

- **Uma conta, uma versão.** O saldo de um estado é: o que as pessoas e empresas dele pagaram à União, menos o que voltou da
  União a ele (movimentos 2, 3, 4 e 5). Hoje esse número existe em seis arquivos com seis valores para o DF; no livro ele é uma
  consulta só.
- **As regras viram conferência.** Com a arrecadação e o percentual na mesma base, o repasse esperado se calcula: o FPE tem de ser
  21,5% do IR e do IPI arrecadados no período (a lei complementar define os decêndios e as deduções), o FPM 22,5% (mais o 1% dos
  meses certos), a parte das prefeituras 25% do ICMS. Uma fonte que erre aparece na hora, porque a regra da Constituição e o valor publicado deixam de bater.
- **Repasse nunca vira gasto duas vezes.** O dinheiro entre governos tem tipo próprio (movimentos 2 a 4), então o estado não
  conta como seu o que só passou por ele (D116) e a União não conta como gasto o que só repartiu.
- **Uma tela nova é uma consulta, não um script.** O mapa, a janela do estado, a conta da União e "para onde vai o dinheiro"
  leem as mesmas linhas; um conserto num lugar chega a todos.
- **Atualizar é carregar a divulgação nova.** A fonte publica, o livro carrega, as conferências passam, as telas mudam juntas.

### O que não fica mais simples (e por quê)

- **Dinheiro que a fonte não põe em um estado** continua em "sem informação de estado" (D127): a folha federal sem estado nos
  arquivos abertos, o imposto que a Receita registra na sede, a contribuição do INSS de dezembro de 2025 que falta no arquivo por
  estado (D139). A regra não inventa o que o dado não diz.
- **Calendários diferentes:** a União publica por mês, os estados por bimestre e as prefeituras com atraso. O livro guarda o mês
  de cada linha e a tela diz até quando cada parte vai.
- **Caixa e competência:** juros e alguns repasses existem nos dois regimes; o livro guarda os dois (D121, item 2).
- **A reforma tributária muda as regras até 2033:** em 2026 a CBS (0,9%) e o IBS (0,1%) são só teste, compensados no PIS e na
  Cofins (ADCT art. 125); de 2027 em diante saem o PIS e a Cofins e entram a CBS e o imposto seletivo (ADCT art. 126); o ICMS e o
  ISS caem aos poucos de 2029 a 2032 e acabam em 2033 (ADCT arts. 128 e 129). No livro, cada mudança é uma regra nova com data
  de início, e os meses antigos continuam com a regra antiga.

## 7. O que isso muda na ordem do trabalho

Hoje o livro tem só a fase 1 (o nó da União, conferido com o RTN). O mapa, a janela do estado e a seção federal ainda saem dos
scripts antigos, que a auditoria de 2026-10-14 mostrou estarem cheios de versões paralelas.

**Recomendação:** organizar a fase 2 da limpeza (as pastas novas) em torno deste caminho, e não em torno dos scripts de hoje.
Os pipelines ficam um por movimento (tributo, repartição, fundo comum, repasse, gasto, dívida), todos alimentando o livro; as
fases 2 a 4 do livro (arrecadação por estado; o que a União paga a cada estado; governos estaduais e municipais) passam a ser o
centro do trabalho; e os scripts que só servem a uma tela saem na fase 5 do livro, em vez de serem arrumados agora e apagados
depois. É uma escolha do autor: a fase 2 da limpeza, como aprovada (Q43), arruma as pastas de hoje sem mudar a lógica.

## 8. Fontes

- Constituição Federal, redação atual, lida no Planalto em 2026-10-21: arts. 20, § 1º; 21, XIV; 153 (e § 5º); 155; 156; 157;
  158; 159; 195; 198, § 2º; 212; 212-A; ADCT arts. 60 e 125 a 129.
  https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm
- Tesouro Nacional, Resultado do Tesouro Nacional (RTN), série histórica, Tabela 1.1, divulgação de agosto de 2026, carregada no
  livro de fluxos (garantia G5: bate com o RTN linha por linha).
  https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/8
- RREO Anexo 3 (receita corrente líquida) dos 27 estados, SICONFI, em `data/series/state-budgets.json`.
- Não conferido nesta pesquisa: os percentuais da LC 141/2012 para a saúde de estados e municípios e os coeficientes do FPE
  (LC 62/1989).
