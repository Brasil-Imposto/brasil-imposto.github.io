# Livro de fluxos, fase 1: plano de implementação

English summary: implementation plan for phase 1 of the approved money-flow ledger spec (D121). It builds a DuckDB
warehouse with the spec's five tables plus five support tables, a source registry that hashes every file with SHA-256
while it streams and never keeps it, four loaders (Tesouro RTN Tabela 1.2; Banco Central SGS 4606, 4639 and 4573;
the Tesouro's expense base for interest paid in cash; the União's RREO as its control), the seven guarantees of spec
section 6 and the four planted errors that must fail. The gov:uniao node covers January 2019 to August 2026 and is
reconciled to every RTN line and to the Banco Central, with interest by accrual and by cash side by side. Every number
in this plan was measured on 2026-10-08 before writing it.

Status: **plano da fase 1, executado em 2026-10-08 e emendado em 2026-10-09 (D127)**

**Emenda de 2026-10-09 (D127):** o que a fonte não diz o estado vai para `soc:unknown`, "sem informação de estado", e nunca fica somado à União; `soc:br`, "União (país inteiro)", fica só para o que a fonte oficial classifica como nacional. A regra `national_total_v1` virou `no_state_in_source_v1`. Nenhuma estimativa vai à tela.

### Para quem executa
Executar as tarefas na ordem, marcando as caixas. Sem git (D54): onde um plano comum mandaria fazer commit, aqui o
passo é rodar os testes e seguir. Execução nesta mesma sessão, sem subagentes, com atualizações curtas ao autor.
Todo comando roda na pasta `~/Documents/Brasil-Imposto`.

### Objetivo
O esqueleto do livro de fluxos e o nó `gov:uniao` de jan/2019 a ago/2026, batendo com o RTN linha por linha e com o
Banco Central, com os juros pelos dois critérios lado a lado (D121), e a construção parando se qualquer garantia falhar.

### Arquitetura
Um arquivo DuckDB (`data/ledger/ledger.duckdb`). Cada carregador busca a fonte uma vez, calcula o SHA-256 enquanto o
arquivo chega, registra a divulgação, guarda os números que a fonte imprime e os fluxos que saem deles, e apaga o
arquivo. A construção junta os fluxos das divulgações atuais, roda as sete garantias, planta os quatro erros numa
cópia e só então publica a tabela `flow`. Se algo falhar, a tabela `flow` fica como estava.

### Ferramentas
Python 3.11 (`/usr/local/bin/python3`, que já tem o openpyxl), DuckDB (a instalar, gratuito), unittest do próprio
Python. Nenhum serviço pago.

## 1. O que medi antes de escrever o plano

| O que | Resultado | O que isso decide |
|---|---|---|
| RTN, Tabela 1.2 (arquivo de ago/2026, já no disco) | 159 linhas com código, 8 linhas de memorando, 92 meses de jan/2019 a ago/2026, em R$ milhões com frações de centavo | cada linha é guardada com o valor exato e também em centavos inteiros |
| As partes do RTN somam os totais? | sim: a maior diferença, em conta exata, é R$ 0,00005 (linhas 1, 2, 4, 4.4.1, 4.4.2 e as identidades 3, 5, 8 e 10) | a conferência dos totais é exata nos números do próprio Tesouro |
| Partes arredondadas ao centavo contra o total arredondado | diferença de até 2 centavos em alguns meses (linha 2 em 1 mês, linha 4 em 4, 4.4.1 em 41, 4.4.2 em 50) | cada linha bate ao centavo com o seu próprio valor; um total bate com a soma das partes, e a diferença para o total impresso só pode ser arredondamento (no máximo meio centavo por parte), o que a conta exata acima prova. É a regra já usada no projeto (padrões aprendidos, 2026-10-02) |
| Linhas "dos quais" (d/q) | 6: 1.4.8.1, 4.1.1.1, 4.1.2.1, 4.2.1, 4.3.01.2.1, 4.3.05.1 | cada uma vira duas linhas do livro, a parte e o resto, para nada contar duas vezes |
| Linha 4.3.08, compensação ao RGPS pela desoneração da folha | R$ 30,0 bi em 40 dos 92 meses; igual, mês a mês e ao centavo, à compensação que o memorando põe dentro da arrecadação do RGPS (1.3) | é a União pagando a si mesma (Tesouro para o INSS): vai para uma tabela de movimentos internos e nunca vira fluxo; o RTN continua batendo linha por linha |
| Banco Central, SGS 4606, 4639 e 4573 ("Governo Federal e Banco Central", R$ milhões com duas casas) | batem com as linhas 9, 8 e 10 do RTN com o sinal trocado; maior diferença R$ 5.933 em 92 meses | tolerância de uma unidade publicada (R$ 10 mil), a regra de 2026-10-03 |
| Juros pagos em dinheiro: base do Tesouro "Despesas e Transferências Totais da União", grupo de despesa 2 | R$ 352,03 bi em 2024; o RREO da União (SICONFI) traz R$ 352.023.046.079,93 "pagas até o bimestre"; a diferença de R$ 4,64 mi são restos a pagar pagos, que o RREO não põe nessa coluna | o fluxo é o total pago no mês; a conferência com o RREO usa só as despesas do ano pagas, ao centavo |
| Ação 0669 dentro do grupo 2 | "Cobertura do resultado negativo apurado no Banco Central", R$ 4,16 bi em 2024 | é o Tesouro pagando o Banco Central, dentro da União: movimento interno, fora dos juros pagos aos credores |
| Tamanho dos arquivos da base do Tesouro | 23 a 38 MB por ano, 8 anos (cerca de 270 MB no total, um por vez) | baixar, somar e apagar um por vez; nenhum passa de 200 MB; o disco tem 8,7 GB livres |
| Bibliotecas | DuckDB não está instalado; pytest também não | instalar só o DuckDB; testes com o unittest do Python |
| RREO da União, 46 pontos, contra a base do Tesouro (visto na Tarefa 11) | 2024 a 2026: iguais ao centavo nos 18 pontos. 2019 a 2023: o RREO imprime reais inteiros (os 30 valores terminam em ,00) e as diferenças ficam dentro de R$ 0,50, menos dois pontos de 2023: R$ 0,96 (outubro) e R$ 3,79 (dezembro) a menos na base do Tesouro, causa não achada | decisão 9 (D122) |
| Certificados do Python 3.11 (python.org) | não tem pacote de certificados: toda chamada HTTPS do Python falha (`CERTIFICATE_VERIFY_FAILED`), visto na Tarefa 5 | os downloads passam pelo `curl`, que usa os certificados do Mac, como os scripts de hoje; o SHA-256 é calculado enquanto os bytes saem do curl |

## 2. Decisões desta fase, dentro da spec

| # | Decisão | Por quê |
|---|---|---|
| 1 | Cinco tabelas além das cinco da spec: `published_line` (cada número que a fonte imprime, como imprime), `internal_flow` (dinheiro que a União paga a si mesma), `flow_stage` (o que cada divulgação diz, antes das garantias), `release_supersede` (que divulgação substituiu qual) e `build_run` (cada construção) | sem `published_line`, as garantias 3 e 5 teriam de reler o arquivo bruto, que não é guardado; as outras deixam toda tabela só com inserção, nunca alteração |
| 2 | Um nó novo, `gov:sub:br`: governos estaduais e municipais ainda não separados por estado | o RTN dá FPM, FPE, Fundeb e os outros repasses só no total do país; sem esse nó o repasse iria para `soc:br` e contaria como gasto, o que a garantia 7 proíbe. As fases 2 e 3 repartem por estado; o mapa nunca mostra esse nó |
| 3 | Na fase 1 todo fluxo do RTN fica marcado "sem informação de estado" (`soc:unknown`, D127), nunca somado à União, menos o Fundo Constitucional do DF, que a lei manda ao governo do DF (método "direto") | é o que a fonte permite; a localização é trabalho das fases 2 e 3 |
| 4 | Juros por competência: o valor do Banco Central que o RTN reproduz na linha 9 (com mais casas que o SGS), conferido com o SGS 4606. Juros por caixa: a base do Tesouro, grupo 2, conferida com o RREO. Lado a lado, nunca na mesma soma | D121; a garantia 7 também confere que nenhuma fonte mistura os dois critérios |
| 5 | Linhas do RTN que misturam gasto final com repasse a estados e municípios ficam como "gasto que a fonte não separa": Saúde, Educação e demais do Executivo (4.4), créditos extraordinários, convênios, doações, ANA, multas da ANEEL, PNAFE, Funcafé, Fundo Setorial Audiovisual, Emgea, FDA/FDNE, reserva de contingência | a fase 3 separa pela modalidade de aplicação da base do Tesouro; nenhuma delas entra no mapa antes disso |
| 6 | O par salário e contribuição, na fase 1: a folha sem sentenças judiciais (4.2, resto) e a contribuição do servidor (1.4.3), mês a mês, os dois em "sem informação de estado" | a garantia 6 já roda sobre 92 pares reais; o erro plantado "par em estados diferentes" mexe num deles |
| 7 | Suposição registrada: a compensação 4.3.08 está dentro da arrecadação urbana (1.3.1), porque a desoneração da folha (Lei 12.546/2011) troca a contribuição das empresas sobre a folha por uma sobre a receita, e a contribuição rural tem regra própria | se estiver errada, muda só a divisão entre urbano e rural; nenhum total muda e nada no site usa essa divisão |
| 8 | Arredondamento ao centavo: metade para o par | é o que os scripts de hoje usam; o valor exato fica guardado ao lado |
| 9 | Garantia 3 para os juros pagos (decisão do autor, D122): ao centavo onde o RREO imprime centavos (2024 em diante); uma unidade impressa (R$ 1) onde imprime reais inteiros (2019 a 2023); os dois pontos de 2023 ficam como diferença conhecida, anotada com o valor exato, e a construção para se mudarem um centavo | a mesma regra de uma unidade publicada usada no SGS; a diferença de 2023 continua à vista |

## 3. Arquivos

| Arquivo | O que faz |
|---|---|
| `data/scripts/ledger/money.py` | valor exato e centavos inteiros |
| `data/scripts/ledger/schema.sql` | as tabelas e as três visões das divulgações atuais |
| `data/scripts/ledger/reference.py` | nós, tipos de fluxo e regras de localização |
| `data/scripts/ledger/db.py` | abre o armazém, cria o esquema, grava linhas, impressão digital da tabela `flow` |
| `data/scripts/ledger/registry.py` | busca com SHA-256 em fluxo, limites de disco e de tamanho, registro e substituição de divulgações |
| `data/scripts/ledger/sources.py` | endereço e identidade de cada fonte da fase 1 |
| `data/scripts/ledger/rtn_map.py` | o papel de cada linha do RTN (seção 4) |
| `data/scripts/ledger/load_rtn.py` | carregador do RTN |
| `data/scripts/ledger/load_sgs.py` | carregador do Banco Central |
| `data/scripts/ledger/load_dtt_interest.py` | carregador dos juros pagos em dinheiro |
| `data/scripts/ledger/load_rreo_union.py` | carregador do RREO da União (conferência dos juros pagos) |
| `data/scripts/ledger/measures.py` | a conta da União refeita a partir do livro |
| `data/scripts/ledger/guarantees.py` | as garantias 1 a 7 |
| `data/scripts/ledger/planted.py` | os quatro erros que têm de falhar (garantia 8) |
| `data/scripts/ledger/build.py` | a construção: carregar, conferir, plantar, publicar, relatar |
| `data/scripts/ledger/requirements.txt` | versões do DuckDB e do openpyxl |
| `data/scripts/ledger/tests/` | testes unitários e a lista de códigos do RTN de ago/2026 |
| `data/ledger/ledger.duckdb` | o armazém (gerado, fora do git) |
| `data/ledger/build-report.json` | o relatório de cada construção (gerado) |

## 4. Mapa das linhas do RTN (Tabela 1.2)

Cada código impresso tem um papel só; um código novo numa divulgação futura para a carga até ser posto aqui.
"Sem informação de estado" é `soc:unknown` (D127); "estados e municípios (a separar)" é `gov:sub:br`.

| Linha | Descrição no RTN | Vira no livro |
|---|---|---|
| `1` | RECEITA TOTAL 1/ | total: soma exata das linhas logo abaixo (conferida) |
| `1.1` | Receita Administrada pela RFB | total: soma exata das linhas logo abaixo (conferida) |
| `1.1.01` | Imposto sobre a Importação | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.02` | IPI | total: soma exata das linhas logo abaixo (conferida) |
| `1.1.02.1` | IPI - Fumo | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.02.2` | IPI - Bebidas | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.02.3` | IPI - Automóveis | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.02.4` | IPI - Vinculado à importação | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.02.5` | IPI - Outros | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.03` | Imposto sobre a Renda | total: soma exata das linhas logo abaixo (conferida) |
| `1.1.03.1` | I.R. - Pessoa Física | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.03.2` | I.R. - Pessoa Jurídica | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.03.3` | I.R. - Retido na fonte | total: soma exata das linhas logo abaixo (conferida) |
| `1.1.03.3.1` | IRRF - Rendimentos do Trabalho | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.03.3.2` | IRRF - Rendimentos do Capital | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.03.3.3` | IRRF - Rendimentos de Residentes no Exterior | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.03.3.4` | IRRF - Outros Rendimentos | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.04` | IOF | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.05` | Cofins | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.06` | PIS/Pasep | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.07` | CSLL | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.08` | CPMF | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.09` | CIDE - Combustíveis | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.1.10` | Outras Receitas Administradas pela RFB | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.2` | Incentivos Fiscais | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.3` | Arrecadação Líquida para o RGPS | total: soma exata das linhas logo abaixo (conferida) |
| `1.3.1` | Arrecadação Líquida para o RGPS - Urbana | dividida: `1.3.1~ordinary` (arrecadação comum) + a compensação do Tesouro (interno, linha 4.3.08) |
| `1.3.1~ordinary` | Arrecadação Líquida para o RGPS - Urbana, exceto a parte acima | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.3.2` | Arrecadação Líquida para o RGPS - Rural | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.4` | Receitas Não Administradas pela RFB | total: soma exata das linhas logo abaixo (conferida) |
| `1.4.1` | Concessões e Permissões | fluxo: outras receitas, sem informação de estado → União |
| `1.4.2` | Dividendos e Participações | total: soma exata das linhas logo abaixo (conferida) |
| `1.4.2.1` | Banco do Brasil | fluxo: dividendo e royalty, sem informação de estado → União |
| `1.4.2.2` | BNB | fluxo: dividendo e royalty, sem informação de estado → União |
| `1.4.2.3` | BNDES | fluxo: dividendo e royalty, sem informação de estado → União |
| `1.4.2.4` | Caixa Econômica Federal | fluxo: dividendo e royalty, sem informação de estado → União |
| `1.4.2.5` | Empresa Brasileira de Correios e Telégrafos (Correios) | fluxo: dividendo e royalty, sem informação de estado → União |
| `1.4.2.6` | Eletrobrás | fluxo: dividendo e royalty, sem informação de estado → União |
| `1.4.2.7` | IRB | fluxo: dividendo e royalty, sem informação de estado → União |
| `1.4.2.8` | Petrobras | fluxo: dividendo e royalty, sem informação de estado → União |
| `1.4.2.9` | Demais Dividendos e Participações | fluxo: dividendo e royalty, sem informação de estado → União |
| `1.4.3` | Contr. Plano de Seguridade Social do Servidor | fluxo: retido de salário público, sem informação de estado → União |
| `1.4.4` | Receitas de Exploração de Recursos Naturais | fluxo: dividendo e royalty, sem informação de estado → União |
| `1.4.5` | Receitas Próprias (fontes 50, 81 e 82) | fluxo: outras receitas, sem informação de estado → União |
| `1.4.6` | Contribuição do Salário Educação | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.4.7` | Complemento para o FGTS (LC nº 110/01) | fluxo: imposto e contribuição, sem informação de estado → União |
| `1.4.8` | Demais Receitas Não Administradas pela RFB | dividida: `1.4.8.1` (dos quais) + `1.4.8~rest` (o resto) |
| `1.4.8~rest` | Demais Receitas Não Administradas pela RFB, exceto a parte acima | fluxo: outras receitas, sem informação de estado → União |
| `1.4.8.1` | d/q Receitas de Operações com Ativos | fluxo: outras receitas, sem informação de estado → União |
| `2` | TRANSF. POR REPARTIÇÃO DE RECEITA 2/ | total: soma exata das linhas logo abaixo (conferida) |
| `2.1` | FPM / FPE / IPI-EE | fluxo: repasse a governos, União → estados e municípios (a separar) |
| `2.2` | Fundos Constitucionais | total: soma exata das linhas logo abaixo (conferida) |
| `2.2.1` | Repasse Total | fluxo: transferência a pessoas, empresas e fundos, União → sem informação de estado |
| `2.2.2` | Superávit dos Fundos | fluxo: transferência a pessoas, empresas e fundos, União → sem informação de estado |
| `2.3` | Transferência de Contribuição do Salário Educação | fluxo: repasse a governos, União → estados e municípios (a separar) |
| `2.4` | Transferências de Exploração de Recursos Naturais | fluxo: repasse a governos, União → estados e municípios (a separar) |
| `2.5` | Transferência da CIDE - Combustíveis | fluxo: repasse a governos, União → estados e municípios (a separar) |
| `2.6` | Demais Transferências por Repartição de Receita | fluxo: repasse a governos, União → estados e municípios (a separar) |
| `3` | RECEITA LÍQUIDA (1-2) | resultado: refeito a partir do livro e conferido |
| `4` | DESPESA TOTAL 2/ | total: soma exata das linhas logo abaixo (conferida) |
| `4.1` | Benefícios Previdenciários | total: soma exata das linhas logo abaixo (conferida) |
| `4.1.1` | Benefícios Previdenciários - Urbano 3/ | dividida: `4.1.1.1` (dos quais) + `4.1.1~rest` (o resto) |
| `4.1.1~rest` | Benefícios Previdenciários - Urbano 3/, exceto a parte acima | fluxo: benefício, União → sem informação de estado |
| `4.1.1.1` | Sent. Judiciais e Precatórios de Benefícios Previdenciários - Urbano | fluxo: benefício, União → sem informação de estado |
| `4.1.2` | Benefícios Previdenciários - Rural 3/ | dividida: `4.1.2.1` (dos quais) + `4.1.2~rest` (o resto) |
| `4.1.2~rest` | Benefícios Previdenciários - Rural 3/, exceto a parte acima | fluxo: benefício, União → sem informação de estado |
| `4.1.2.1` | Sent. Judiciais e Precatórios de Benefícios Previdenciários - Rural | fluxo: benefício, União → sem informação de estado |
| `4.2` | Pessoal e Encargos Sociais | dividida: `4.2.1` (dos quais) + `4.2~rest` (o resto) |
| `4.2~rest` | Pessoal e Encargos Sociais, exceto a parte acima | fluxo: folha (bruto), União → sem informação de estado |
| `4.2.1` | Sent. Judiciais e Precatórios de Pessoal e Encargos | fluxo: folha (bruto), União → sem informação de estado |
| `4.3` | Outras Despesas Obrigatórias | total: soma exata das linhas logo abaixo (conferida) |
| `4.3.01` | Abono e Seguro Desemprego | total: soma exata das linhas logo abaixo (conferida) |
| `4.3.01.1` | Abono | fluxo: benefício, União → sem informação de estado |
| `4.3.01.2` | Seguro Desemprego | dividida: `4.3.01.2.1` (dos quais) + `4.3.01.2~rest` (o resto) |
| `4.3.01.2~rest` | Seguro Desemprego, exceto a parte acima | fluxo: benefício, União → sem informação de estado |
| `4.3.01.2.1` | d/q Seguro Defeso | fluxo: benefício, União → sem informação de estado |
| `4.3.02` | Anistiados | fluxo: benefício, União → sem informação de estado |
| `4.3.03` | Apoio Fin. EE/MM | fluxo: repasse a governos, União → estados e municípios (a separar) |
| `4.3.04` | Benefícios de Legislação Especial e Indenizações | fluxo: benefício, União → sem informação de estado |
| `4.3.05` | Benefícios de Prestação Continuada da LOAS/RMV | dividida: `4.3.05.1` (dos quais) + `4.3.05~rest` (o resto) |
| `4.3.05~rest` | Benefícios de Prestação Continuada da LOAS/RMV, exceto a parte acima | fluxo: benefício, União → sem informação de estado |
| `4.3.05.1` | Sentenças Judiciais e Precatórios de BPC/LOAS | fluxo: benefício, União → sem informação de estado |
| `4.3.06` | Complemento para o FGTS (LC nº 110/01) | fluxo: transferência a pessoas, empresas e fundos, União → sem informação de estado |
| `4.3.07` | Créditos Extraordinários 16/ | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.08` | Compensação ao RGPS pelas Desonerações da Folha | interno: Tesouro → INSS; o mesmo dinheiro está dentro da 1.3.1; nunca é fluxo |
| `4.3.09` | Fabricação de Cédulas e Moedas | fluxo: compra e serviço, União → sem informação de estado |
| `4.3.10` | FUNDEB (Complem. União) | fluxo: repasse a governos, União → estados e municípios (a separar) |
| `4.3.11` | Fundo Constitucional DF (Custeio e Capital) | fluxo: repasse a governos, União → governo do DF (direto, Lei 10.633/2002) |
| `4.3.12` | Legislativo/Judiciário/MPU/DPU (Custeio e Capital) | fluxo: compra e serviço, União → sem informação de estado |
| `4.3.13` | Lei Kandir (LC nº 87/96 e 102/00) e LC nº 176 de 2020 | fluxo: repasse a governos, União → estados e municípios (a separar) |
| `4.3.14` | Sentenças Judiciais e Precatórios (Custeio e Capital) | fluxo: sentença judicial, União → sem informação de estado |
| `4.3.15` | Subsídios, Subvenções e Proagro | total: soma exata das linhas logo abaixo (conferida) |
| `4.3.15.1` | Operações Oficiais de Crédito e Reordenamento de Passivos | total: soma exata das linhas logo abaixo (conferida) |
| `4.3.15.1.1` | Equalização de custeio agropecuário | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.2` | Equalização de invest. rural e agroindustrial 4/ | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.3` | Política de preços agrícolas | total: soma exata das linhas logo abaixo (conferida) |
| `4.3.15.1.3.1` | Equalização Empréstimo do Governo Federal | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.3.2` | Equalização Aquisições do Governo Federal | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.3.3` | Garantia à Sustentação de Preços | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.4` | Pronaf | total: soma exata das linhas logo abaixo (conferida) |
| `4.3.15.1.4.1` | Equalização Empréstimo do Governo Federal | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.4.2` | Concessão de Financiamento 5/ | fluxo: empréstimo e devolução, União → sem informação de estado |
| `4.3.15.1.4.3` | Aquisição | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.5` | Proex | total: soma exata das linhas logo abaixo (conferida) |
| `4.3.15.1.5.1` | Equalização Empréstimo do Governo Federal | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.5.2` | Concessão de Financiamento 5/ | fluxo: empréstimo e devolução, União → sem informação de estado |
| `4.3.15.1.6` | Programa especial de saneamento de ativos (PESA) 6/ | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.7` | Álcool | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.8` | Cacau | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.9` | Programa de subsídio à habitação de interesse social (PSH) | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.10` | Securitização da dívida agrícola (LEI 9.138/1995) | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.11` | Fundo da terra/ INCRA 5/ | fluxo: empréstimo e devolução, União → sem informação de estado |
| `4.3.15.1.12` | Funcafé | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.15.1.13` | Revitaliza | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.14` | Programa de Sustentação ao Investimento - PSI | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.15` | Operações de Microcredito Produtivo Orientado (EQMPO) | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.16` | Operações de crédito destinadas a Pessoas com deficiência (EQPCD) 7/ | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.17` | Fundo nacional de desenvolvimento (FND) 5/ | fluxo: empréstimo e devolução, União → sem informação de estado |
| `4.3.15.1.18` | Fundo Setorial Audiovisual (FSA) | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.15.1.19` | Capitalização à Emgea | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.15.1.20` | Subv. Parcial à Remuneração por Cessão de Energia Elétrica de Itaipu | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.21` | Subvenções Econômicas | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.22` | Equalização dos Fundos FDA/FDNE/FDCO | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.23` | Sudene | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.1.24` | Receitas de Recuperação de Subvenções 8/ | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.2` | Proagro | fluxo: subsídio, União → sem informação de estado |
| `4.3.15.3` | PNAFE | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.15.4` | Demais Subsídios e Subvenções | fluxo: subsídio, União → sem informação de estado |
| `4.3.16` | Transferências ANA | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.17` | Transferências Multas ANEEL | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.18` | Impacto Primário do FIES | fluxo: empréstimo e devolução, União → sem informação de estado |
| `4.3.19` | Financiamento de Campanha Eleitoral | fluxo: transferência a pessoas, empresas e fundos, União → sem informação de estado |
| `4.3.20` | Demais Despesas Obrigatórias | total: soma exata das linhas logo abaixo (conferida) |
| `4.3.20.1` | Auxílio CDE | fluxo: transferência a pessoas, empresas e fundos, União → sem informação de estado |
| `4.3.20.2` | Convênios | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.20.3` | Doações | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.20.4` | FDA/FDNE | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.20.5` | Reserva de Contingência | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.3.20.6` | Ressarc. Est/Mun. Comb. Fósseis | fluxo: repasse a governos, União → estados e municípios (a separar) |
| `4.4` | Despesas do Poder Executivo Sujeitas à Programação Financeira | total: soma exata das linhas logo abaixo (conferida) |
| `4.4.1` | Obrigatórias com Controle de Fluxo | total: soma exata das linhas logo abaixo (conferida) |
| `4.4.1.1` | Benefícios a servidores públicos | fluxo: folha (bruto), União → sem informação de estado |
| `4.4.1.2` | Bolsa Família e Auxílio Brasil | fluxo: benefício, União → sem informação de estado |
| `4.4.1.3` | Saúde | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.1.4` | Educação | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.1.5` | Demais | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.2` | Despesas Discricionárias | total: soma exata das linhas logo abaixo (conferida) |
| `4.4.2.1` | Saúde | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.2.2` | Educação | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.2.3` | Defesa | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.2.4` | Transporte | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.2.5` | Administração | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.2.6` | Ciência e Tecnologia | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.2.7` | Segurança Pública | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.2.8` | Assistência Social | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `4.4.2.9` | Demais | fluxo: gasto que a fonte não separa, União → sem informação de estado |
| `5` | RESULTADO PRIMÁRIO GOVERNO CENTRAL - ACIMA DA LINHA (3 - 4) | resultado: refeito a partir do livro e conferido |
| `6` | AJUSTES METODOLÓGICOS | ajuste, não é dinheiro: guardado e usado na linha 8 |
| `6.1` | Ajuste Metodológico Itaipu 9/ | ajuste, não é dinheiro: guardado e usado na linha 8 |
| `6.2` | Ajuste Metodológico Caixa - Competência 10/ | ajuste, não é dinheiro: guardado e usado na linha 8 |
| `6.3` | Ajuste Metodológico Recursos Não Sacados do PIS/PASEP (EC nº 126/2022) 11/ | ajuste, não é dinheiro: guardado e usado na linha 8 |
| `6.4` | Ajuste Metodológico Compensações LC nº 194/2022 (pré-Acordo União e Estados/Distrito Federal) 12/ | ajuste, não é dinheiro: guardado e usado na linha 8 |
| `7` | DISCREPÂNCIA ESTATÍSTICA | ajuste, não é dinheiro: guardado e usado na linha 8 |
| `8` | RESULTADO PRIMÁRIO DO GOVERNO CENTRAL - ABAIXO DA LINHA (5 + 6 + 7) | resultado: refeito a partir do livro e conferido |
| `9` | JUROS NOMINAIS 13/ | fluxo: juros por competência, União → credores (o RTN imprime negativo; o fluxo é positivo) |
| `10` | RESULTADO NOMINAL DO GOVERNO CENTRAL (8 + 9) 14/ | resultado: refeito a partir do livro e conferido |

## Tarefa 0: preparação

- [ ] **Passo 1: conferir o disco.** Rodar `df -h ~ | tail -1`. Esperado: 5 GB livres ou mais (8,7 GB em 2026-10-08). Abaixo de 5 GB, parar e avisar.
- [ ] **Passo 2: instalar o DuckDB** no Python que já tem o openpyxl, e anotar as versões.

```bash
/usr/local/bin/python3 -m pip install --user duckdb
mkdir -p data/scripts/ledger/tests/fixtures data/ledger
/usr/local/bin/python3 -c "import duckdb, openpyxl; print(f'duckdb=={duckdb.__version__}'); print(f'openpyxl=={openpyxl.__version__}')" > data/scripts/ledger/requirements.txt
cat data/scripts/ledger/requirements.txt
```

Esperado: duas linhas, `duckdb==<versão>` e `openpyxl==3.1.5`.

- [ ] **Passo 3: tirar o armazém gerado do futuro repositório.** Acrescentar ao `.gitignore`:

```
data/ledger/ledger.duckdb
data/ledger/ledger.duckdb.wal
data/scripts/ledger/__pycache__/
data/scripts/ledger/tests/__pycache__/
```

## Tarefa 1: dinheiro em centavos

**Arquivos:** criar `data/scripts/ledger/money.py` e `data/scripts/ledger/tests/test_money.py`.

- [ ] **Passo 1: escrever o teste.**

`data/scripts/ledger/tests/test_money.py`

```python
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from money import exact, from_millions, to_cents  # noqa: E402


class MoneyTest(unittest.TestCase):
    def test_millions_use_the_number_the_file_holds(self):
        self.assertEqual(from_millions(241960.60662784002), Decimal("241960606627.84002000"))
        self.assertEqual(from_millions("102880.81"), Decimal("102880810000.00000000"))

    def test_cents_round_half_to_even(self):
        self.assertEqual(to_cents(Decimal("0.005")), 0)
        self.assertEqual(to_cents(Decimal("0.015")), 2)
        self.assertEqual(to_cents(Decimal("-0.015")), -2)

    def test_negative_lines_keep_their_sign(self):
        self.assertEqual(to_cents(from_millions(-562.410764057834)), -56241076406)

    def test_exact_reais_from_a_float_cell(self):
        self.assertEqual(to_cents(exact(1024768.4)), 102476840)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Passo 2: rodar e ver falhar.** `/usr/local/bin/python3 -m unittest discover -s data/scripts/ledger/tests -p 'test_money.py' -v`. Esperado: `ModuleNotFoundError: No module named 'money'`.
- [ ] **Passo 3: escrever o código.**

`data/scripts/ledger/money.py`

```python
"""Money helpers: exact decimal values and integer cents, never floating point (spec 4.2)."""
from decimal import ROUND_HALF_EVEN, Decimal

EXACT = Decimal("1e-8")  # reais; finer than anything the sources publish


def _decimal(value):
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(repr(value))  # the shortest repr is the number the file holds
    return Decimal(str(value))


def exact(value):
    """A source number in reais (int, float, str or Decimal) as an exact Decimal."""
    return _decimal(value).quantize(EXACT, ROUND_HALF_EVEN)


def from_millions(value):
    """R$ milhões, as the RTN and the SGS publish, to exact reais."""
    return (_decimal(value) * 1_000_000).quantize(EXACT, ROUND_HALF_EVEN)


def to_cents(reais):
    """Exact reais to integer cents, rounding half to even."""
    return int((reais * 100).quantize(Decimal(1), ROUND_HALF_EVEN))
```

- [ ] **Passo 4: rodar e ver passar.** Mesmo comando. Esperado: `Ran 4 tests ... OK`.

## Tarefa 2: esquema, nós, tipos e regras

**Arquivos:** criar `schema.sql`, `reference.py`, `db.py` e `tests/test_schema.py` em `data/scripts/ledger/`.

- [ ] **Passo 1: escrever o teste.** Ele prova que iniciar duas vezes não duplica nada, que a tabela `flow` recusa origem igual ao destino e nó desconhecido, e que uma linha de referência alterada no lugar para a construção.

`data/scripts/ledger/tests/test_schema.py`

```python
import sys
import unittest
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db  # noqa: E402
import reference  # noqa: E402

RELEASE = ("INSERT INTO source_release VALUES ('t@1', 't', 't', 'p', 'u', NULL, NULL, NULL, ?, 1, "
           "TIMESTAMP '2026-10-08 00:00:00', 'test')")
FLOW = "INSERT INTO flow VALUES ('x', DATE '2026-08-01', ?, ?, 'tax', 1, 'cash', 't@1', 'k', 'unallocated', 'no_state_in_source_v1', NULL)"


class SchemaTest(unittest.TestCase):
    def setUp(self):
        self.con = db.connect(":memory:")
        self.con.execute(RELEASE, ["0" * 64])

    def test_init_twice_keeps_one_copy_of_the_reference(self):
        db.init(self.con)
        self.assertEqual(self.con.execute("SELECT count(*) FROM node").fetchone()[0], 86)
        self.assertEqual(len(reference.NODES), 86)

    def test_flow_accepts_a_good_row(self):
        self.con.execute(FLOW, ["soc:unknown", "gov:uniao"])
        self.assertEqual(self.con.execute("SELECT count(*) FROM flow").fetchone()[0], 1)

    def test_flow_rejects_same_origin_and_destination(self):
        with self.assertRaises(duckdb.ConstraintException):
            self.con.execute(FLOW, ["gov:uniao", "gov:uniao"])

    def test_flow_rejects_an_unknown_node(self):
        with self.assertRaises(duckdb.ConstraintException):
            self.con.execute(FLOW, ["soc:uf:XX", "gov:uniao"])

    def test_a_reference_row_changed_in_place_stops_the_build(self):
        self.con.execute("DELETE FROM allocation_rule WHERE rule_id = 'fcdf_df_v1'")
        self.con.execute("INSERT INTO allocation_rule VALUES ('fcdf_df_v1', 1, 'direct', 'outro texto', 'x')")
        with self.assertRaises(SystemExit):
            reference.seed(self.con)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Passo 2: rodar e ver falhar.** `/usr/local/bin/python3 -m unittest discover -s data/scripts/ledger/tests -p 'test_schema.py' -v`. Esperado: `No module named 'db'`.
- [ ] **Passo 3: escrever o esquema.**

`data/scripts/ledger/schema.sql`

```sql
-- Money-flow ledger, phase 1 (spec: docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_money-flow-ledger_2026-10-08.md).
-- Reference, release and line tables are insert-only: a row never changes in place. A changed meaning gets a new id,
-- and a new release of a source is a new row that supersedes the old one (release_supersede).

CREATE TABLE IF NOT EXISTS node (
  node_id       TEXT PRIMARY KEY,
  kind          TEXT NOT NULL CHECK (kind IN ('gov_union', 'gov_state', 'gov_municipal', 'gov_subnational_unassigned',
                                              'society_state', 'society_national', 'society_unknown', 'creditors', 'world')),
  uf            TEXT CHECK (uf IS NULL OR length(uf) = 2),
  is_government BOOLEAN NOT NULL,
  label_pt      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flow_type (
  flow_type_id    TEXT PRIMARY KEY,
  nature          TEXT NOT NULL CHECK (nature IN ('primary', 'intergovernmental', 'circular', 'financial', 'external')),
  allows_negative BOOLEAN NOT NULL,
  label_pt        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS allocation_rule (
  rule_id        TEXT PRIMARY KEY,
  version        INTEGER NOT NULL,
  method         TEXT NOT NULL CHECK (method IN ('direct', 'official_split', 'estimate', 'unallocated')),
  description_pt TEXT NOT NULL,
  evidence       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_release (
  source_id      TEXT PRIMARY KEY,            -- <dataset>@<first 12 hex characters of the sha256>
  dataset        TEXT NOT NULL,
  title          TEXT NOT NULL,
  publisher      TEXT NOT NULL,
  url            TEXT NOT NULL,
  page_url       TEXT,
  published_on   DATE,
  published_note TEXT,                        -- what published_on is, or why it is empty
  sha256         TEXT NOT NULL CHECK (length(sha256) = 64),
  bytes          BIGINT NOT NULL,
  fetched_at     TIMESTAMP NOT NULL,
  loader         TEXT NOT NULL,
  UNIQUE (dataset, sha256)
);

CREATE TABLE IF NOT EXISTS release_supersede (
  old_source_id TEXT PRIMARY KEY REFERENCES source_release (source_id),
  new_source_id TEXT NOT NULL REFERENCES source_release (source_id),
  superseded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS published_line (     -- every number a release prints, as printed
  source_id   TEXT NOT NULL REFERENCES source_release (source_id),
  line_key    TEXT NOT NULL,
  period      DATE NOT NULL,
  kind        TEXT NOT NULL CHECK (kind IN ('leaf', 'derived', 'total', 'result', 'adjustment', 'memo', 'series', 'control')),
  label       TEXT NOT NULL,
  value_reais DECIMAL(38, 8),                 -- exact; NULL when the source prints text such as "Não Disp"
  value_cents BIGINT,
  flow_sign   SMALLINT NOT NULL CHECK (flow_sign IN (1, -1)),  -- flows under this line carry value * flow_sign
  PRIMARY KEY (source_id, line_key, period)
);

CREATE TABLE IF NOT EXISTS internal_flow (      -- money the União pays itself: kept for the reconciliation, never a flow
  source_id    TEXT NOT NULL REFERENCES source_release (source_id),
  source_key   TEXT NOT NULL,
  also_in_key  TEXT,                          -- the other RTN line where the same money is printed
  period       DATE NOT NULL,
  from_part    TEXT NOT NULL,
  to_part      TEXT NOT NULL,
  amount_cents BIGINT NOT NULL,
  PRIMARY KEY (source_id, source_key, period)
);

CREATE TABLE IF NOT EXISTS flow_stage (         -- what each release says, before the guarantees; no constraints on purpose
  flow_id TEXT, period DATE, from_node TEXT, to_node TEXT, flow_type TEXT, amount_cents BIGINT, basis TEXT,
  source_id TEXT, source_key TEXT, location_method TEXT, rule_id TEXT, pair_id TEXT
);

CREATE TABLE IF NOT EXISTS build_run (
  run_id      TEXT PRIMARY KEY,
  started_at  TIMESTAMP NOT NULL,
  finished_at TIMESTAMP NOT NULL,
  status      TEXT NOT NULL CHECK (status IN ('published', 'stopped')),
  flow_rows   BIGINT NOT NULL,
  report_json TEXT NOT NULL
);

CREATE OR REPLACE VIEW current_release AS
  SELECT r.* FROM source_release r
  WHERE NOT EXISTS (SELECT 1 FROM release_supersede s WHERE s.old_source_id = r.source_id);

CREATE OR REPLACE VIEW cur_line AS
  SELECT l.*, r.dataset FROM published_line l JOIN current_release r USING (source_id);

CREATE OR REPLACE VIEW cur_internal AS
  SELECT i.*, r.dataset FROM internal_flow i JOIN current_release r USING (source_id);
```

- [ ] **Passo 4: escrever a referência.** 86 nós: a União, `gov:sub:br`, `soc:br`, `soc:unknown` (D127), os credores, o exterior, 27 governos estaduais, 26 conjuntos de prefeituras (o DF é estado e município ao mesmo tempo) e 27 sociedades estaduais.

`data/scripts/ledger/reference.py`

```python
"""Reference rows of the ledger: nodes, flow types and allocation rules (spec 4.1, 4.3 and 4.4).

Rows never change in place. A changed meaning gets a new id (allocation rules carry a version), so a flow always points
to the rule that placed it. While phase 1 is in development, deleting data/ledger/ledger.duckdb rebuilds everything."""

UFS = tuple("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())

NODES = [
    ("gov:uniao", "gov_union", None, True, "União (Governo Central: Tesouro, INSS e Banco Central)"),
    ("gov:sub:br", "gov_subnational_unassigned", None, True,
     "Governos estaduais e municipais, sem informação de estado (ainda não separados)"),
    ("soc:br", "society_national", None, False, "União (país inteiro): o que a fonte oficial classifica como nacional"),
    ("soc:unknown", "society_unknown", None, False,
     "Sem informação de estado: pessoas e empresas de algum estado, que a fonte não diz qual (D127)"),
    ("fin:credores", "creditors", None, False, "Credores da dívida pública"),
    ("ext:mundo", "world", None, False, "Exterior"),
]
for _uf in UFS:
    NODES.append((f"gov:uf:{_uf}", "gov_state", _uf, True,
                  "Governo do Distrito Federal" if _uf == "DF" else f"Governo do estado ({_uf})"))
    if _uf != "DF":  # the DF is state and municipality at once (spec 4.1)
        NODES.append((f"gov:mun:{_uf}", "gov_municipal", _uf, True, f"Prefeituras do estado ({_uf})"))
    NODES.append((f"soc:uf:{_uf}", "society_state", _uf, False, f"Pessoas e empresas do estado ({_uf})"))

FLOW_TYPES = [  # (id, nature, allows_negative, label)
    ("tax", "primary", True, "Imposto e contribuição"),
    ("public_payroll_withholding", "circular", True, "Imposto e contribuição retidos de salário público"),
    ("public_payroll_gross", "primary", True, "Salário bruto de servidor (ativos, aposentados e pensionistas)"),
    ("social_benefit", "primary", True, "Benefício (INSS, BPC, Bolsa Família, seguro-desemprego, abono)"),
    ("purchase", "primary", False, "Compra, obra e serviço"),
    ("court_order", "primary", True, "Sentença judicial e precatório"),
    ("subsidy", "primary", True, "Subsídio e subvenção"),
    ("transfer_to_society", "primary", True, "Transferência a pessoas, empresas, fundos e entidades"),
    ("mixed_spending", "primary", True, "Gasto que a fonte não separa (compra, repasse a estados e municípios e outros)"),
    ("transfer_union_to_subnational", "intergovernmental", True, "Repasse da União a estados e municípios"),
    ("transfer_state_to_municipal", "intergovernmental", True, "Repasse do estado aos municípios (parte das prefeituras e Fundeb)"),
    ("subnational_tax", "primary", True, "Imposto estadual e municipal"),
    ("dividend_royalty", "primary", True, "Dividendo e royalty"),
    ("other_revenue", "primary", True, "Outras receitas (concessões, receitas próprias e demais)"),
    ("interest", "financial", True, "Juros da dívida"),
    ("lending", "financial", True, "Empréstimo e devolução"),
    ("trade", "external", False, "Exportação e importação"),
]

RULES = [  # (id, version, method, description, evidence)
    ("no_state_in_source_v1", 1, "unallocated",
     "A fonte publica só o total do país. O fluxo fica marcado 'sem informação de estado' (pessoas e empresas, ou governos "
     "estaduais e municipais) até uma fonte oficial dizer o estado, nas fases 2 e 3. Nunca conta como dinheiro que ficou "
     "na União (D127).",
     "RTN Tabela 1.2 e base Despesas e Transferências Totais da União: nenhuma das duas tem estado"),
    ("fcdf_df_v1", 1, "direct", "O Fundo Constitucional do Distrito Federal vai ao governo do DF.",
     "Lei 10.633/2002, art. 1º"),
    ("no_state_endpoint_v1", 1, "direct", "Nenhuma das pontas tem estado: a União paga juros aos credores da dívida.",
     "spec, seção 4.1 (nó fin:credores)"),
]

METHOD = {r[0]: r[2] for r in RULES}


def seed(con):
    con.executemany("INSERT INTO node VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING", NODES)
    con.executemany("INSERT INTO flow_type VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING", FLOW_TYPES)
    con.executemany("INSERT INTO allocation_rule VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING", RULES)
    for table, key, rows in (("node", "node_id", NODES), ("flow_type", "flow_type_id", FLOW_TYPES),
                             ("allocation_rule", "rule_id", RULES)):
        if con.execute(f"SELECT * FROM {table} ORDER BY {key}").fetchall() != sorted(rows):
            raise SystemExit(f"{table}: the warehouse differs from reference.py; a changed row needs a new id")
```

- [ ] **Passo 5: escrever a abertura do armazém.**

`data/scripts/ledger/db.py`

```python
"""Open the ledger warehouse (one DuckDB file) with the schema and the reference rows in place. Idempotent."""
from pathlib import Path

import duckdb

import reference

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "ledger" / "ledger.duckdb"
SCHEMA = Path(__file__).with_name("schema.sql")

FLOW_DDL = """CREATE TABLE IF NOT EXISTS flow (
  flow_id         TEXT PRIMARY KEY,             -- sha256 of dataset, source_key, period, from_node, to_node, flow_type
  period          DATE NOT NULL,
  from_node       TEXT NOT NULL REFERENCES node (node_id),
  to_node         TEXT NOT NULL REFERENCES node (node_id),
  flow_type       TEXT NOT NULL REFERENCES flow_type (flow_type_id),
  amount_cents    BIGINT NOT NULL,
  basis           TEXT NOT NULL CHECK (basis IN ('cash', 'accrual')),
  source_id       TEXT NOT NULL REFERENCES source_release (source_id),
  source_key      TEXT NOT NULL,
  location_method TEXT NOT NULL CHECK (location_method IN ('direct', 'official_split', 'estimate', 'unallocated')),
  rule_id         TEXT NOT NULL REFERENCES allocation_rule (rule_id),
  pair_id         TEXT,
  CHECK (from_node <> to_node),
  CHECK (day(period) = 1)
)"""


def connect(path=DB_PATH):
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    init(con)
    return con


def init(con):
    con.execute(SCHEMA.read_text(encoding="utf-8"))
    con.execute(FLOW_DDL)
    reference.seed(con)


def insert(con, published=(), flows=(), internal=()):
    if published:
        con.executemany("INSERT INTO published_line VALUES (?, ?, ?, ?, ?, ?, ?, ?)", list(published))
    if flows:
        con.executemany("INSERT INTO flow_stage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", list(flows))
    if internal:
        con.executemany("INSERT INTO internal_flow VALUES (?, ?, ?, ?, ?, ?, ?)", list(internal))


def fingerprint(con, table="flow"):
    """Row count, total and an order-free hash of the ids: equal fingerprints mean an unchanged table."""
    n, total, h = con.execute(f"SELECT count(*), coalesce(sum(amount_cents), 0), coalesce(bit_xor(hash(flow_id)), 0) "
                              f"FROM {table}").fetchone()
    return {"rows": int(n), "sum_cents": int(total), "id_hash": int(h)}
```

- [ ] **Passo 6: rodar e ver passar.** Esperado: `Ran 5 tests ... OK`.

## Tarefa 3: cadastro de fontes com SHA-256

**Arquivos:** criar `registry.py` e `tests/test_registry.py`.

- [ ] **Passo 1: escrever o teste.** Usa um arquivo local por `file://`: o hash bate, o arquivo some no fim, um arquivo acima do limite para, pouco disco para antes de baixar, o mesmo arquivo duas vezes é uma divulgação só, e um arquivo diferente substitui o anterior.

`data/scripts/ledger/tests/test_registry.py`

```python
import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db  # noqa: E402
import registry  # noqa: E402


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.src = self.dir / "a.bin"
        self.src.write_bytes(b"x" * 3000)
        self.url = self.src.as_uri()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_hashes_while_streaming_and_deletes_the_file_after(self):
        with registry.fetch(self.url) as fx:
            kept = fx.path
            self.assertTrue(kept.exists())
            self.assertEqual(fx.sha256, hashlib.sha256(b"x" * 3000).hexdigest())
            self.assertEqual(fx.bytes, 3000)
        self.assertFalse(kept.parent.exists())

    def test_a_file_above_the_limit_stops(self):
        with self.assertRaises(registry.TooBig):
            with registry.fetch(self.url, max_bytes=1000):
                pass

    def test_low_disk_stops_before_downloading(self):
        with self.assertRaises(registry.LowDisk):
            with registry.fetch(self.url, min_free=1 << 62):
                pass

    def test_same_file_twice_is_one_release_and_a_new_file_supersedes_it(self):
        con = db.connect(":memory:")
        kw = dict(title="t", publisher="p", loader="test")
        with registry.fetch(self.url) as fx:
            a, new_a = registry.register(con, "t.ds", fx, **kw)
        with registry.fetch(self.url) as fx:
            b, new_b = registry.register(con, "t.ds", fx, **kw)
        self.assertEqual((a, new_a, new_b), (b, True, False))
        self.src.write_bytes(b"y" * 10)
        with registry.fetch(self.url) as fx:
            c, new_c = registry.register(con, "t.ds", fx, **kw)
        self.assertTrue(new_c)
        self.assertEqual(registry.current(con, "t.ds"), [c])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Passo 2: rodar e ver falhar.** `-p 'test_registry.py'`. Esperado: `No module named 'registry'`.
- [ ] **Passo 3: escrever o cadastro.**

`data/scripts/ledger/registry.py`

```python
"""Source registry (spec 4.5): fetch a source once, hash it while it streams, record the release.

Raw files are never kept: fetch() writes into a temporary folder that is deleted when the with-block ends.
Disk rules (CLAUDE.md): nothing above 200 MB, and stop when the free space falls below 5 GB.
Downloads go through curl, which uses the Mac's certificates (the python.org Python here has no certificate bundle);
the bytes are hashed as they come out of curl."""
import contextlib
import hashlib
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

MAX_BYTES = 200 * 1024 * 1024
MIN_FREE = 5 * 1024 ** 3
CHUNK = 1 << 20
UA = "Mozilla/5.0 (Brasil-Imposto ledger)"


class TooBig(Exception):
    pass


class LowDisk(Exception):
    pass


class DownloadError(Exception):
    pass


@dataclass
class Fetched:
    url: str
    sha256: str
    bytes: int
    path: Path          # temporary; gone after the with-block
    fetched_at: datetime


def _download(url, out, data, headers, max_bytes, timeout):
    cmd = ["curl", "-sS", "-L", "--fail", "--max-time", str(timeout), "--max-filesize", str(max_bytes), "-A", UA]
    for name, value in (headers or {}).items():
        cmd += ["-H", f"{name}: {value}"]
    if data is not None:
        cmd += ["--data-binary", "@-"]
    digest, n = hashlib.sha256(), 0
    stdin = subprocess.PIPE if data is not None else subprocess.DEVNULL
    with subprocess.Popen(cmd + [url], stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc, \
            open(out, "wb") as f:
        if data is not None:
            proc.stdin.write(data)
            proc.stdin.close()
        while chunk := proc.stdout.read(CHUNK):
            n += len(chunk)
            if n > max_bytes:
                proc.kill()
                raise TooBig(f"{url} passed {max_bytes} bytes while downloading")
            digest.update(chunk)
            f.write(chunk)
        err = proc.stderr.read().decode("utf-8", "replace").strip()
        code = proc.wait()
    if code == 63:
        raise TooBig(f"{url} announces more than {max_bytes} bytes")
    if code != 0:
        raise DownloadError(f"curl exit {code} for {url}: {err}")
    return digest.hexdigest(), n


@contextlib.contextmanager
def fetch(url, *, data=None, headers=None, suffix="", max_bytes=MAX_BYTES, min_free=MIN_FREE, timeout=600, attempts=3):
    free = shutil.disk_usage(Path.home()).free
    if free < min_free:
        raise LowDisk(f"free disk {free / 1024 ** 3:.1f} GB is below {min_free / 1024 ** 3:.0f} GB")
    tmp = Path(tempfile.mkdtemp(prefix="bi-ledger-"))
    try:
        out = tmp / f"source{suffix}"   # openpyxl reads a workbook only when the name ends in .xlsx
        for attempt in range(1, attempts + 1):
            try:
                sha, n = _download(url, out, data, headers, max_bytes, timeout)
                break
            except (DownloadError, OSError):
                if attempt == attempts:
                    raise
                time.sleep(10 * attempt)
        yield Fetched(url, sha, n, out, datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def current(con, dataset):
    rows = con.execute("SELECT source_id FROM current_release WHERE dataset = ? ORDER BY source_id", [dataset]).fetchall()
    return [r[0] for r in rows]


def register(con, dataset, fx, *, title, publisher, loader, url=None, page_url=None, published_on=None,
             published_note=None):
    """(source_id, is_new). The same file twice is one release; a different file supersedes the current one."""
    row = con.execute("SELECT source_id FROM source_release WHERE dataset = ? AND sha256 = ?", [dataset, fx.sha256]).fetchone()
    if row:
        return row[0], False
    source_id = f"{dataset}@{fx.sha256[:12]}"
    previous = current(con, dataset)
    con.execute("INSERT INTO source_release VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [source_id, dataset, title, publisher, url or fx.url, page_url, published_on, published_note,
                 fx.sha256, fx.bytes, fx.fetched_at, loader])
    for old in previous:
        con.execute("INSERT INTO release_supersede VALUES (?, ?, ?)", [old, source_id, fx.fetched_at])
    return source_id, True
```

- [ ] **Passo 4: rodar e ver passar.** Esperado: `Ran 4 tests ... OK`.

## Tarefa 4: as fontes e o mapa do RTN

**Arquivos:** criar `sources.py`, `rtn_map.py`, `tests/test_rtn_map.py` e `tests/fixtures/rtn-t12-codes-ago26.json`.

- [ ] **Passo 1: gravar a lista de códigos do RTN de ago/2026** (só os códigos e os rótulos do memorando, tirados do arquivo que já está no disco; nenhum valor).

```bash
/usr/local/bin/python3 - <<'PY'
import json, re, openpyxl
wb = openpyxl.load_workbook("data/scripts/series/cache/union/serie_historica_ago26.xlsx", read_only=True, data_only=True)
rows = list(wb["1.2"].iter_rows(values_only=True))
codes, memo, section = [], [], "lines"
for r in rows[5:]:
    label = str(r[0]).strip() if r[0] is not None else ""
    if not label:
        continue
    if label == "Memorando":
        section = "memo"
        continue
    if label.startswith("Obs."):
        break
    if section == "lines":
        codes.append(re.match(r"^(\d+(?:\.\d+)*)\.?\s", label).group(1))
    else:
        memo.append(label)
json.dump({"source": "RTN serie_historica_ago26.xlsx, Tabela 1.2", "codes": codes, "memo": memo},
          open("data/scripts/ledger/tests/fixtures/rtn-t12-codes-ago26.json", "w"), ensure_ascii=False, indent=0)
print(len(codes), "codes,", len(memo), "memo lines")
PY
```

Esperado: `159 codes, 8 memo lines`.

- [ ] **Passo 2: escrever o teste.** Todo código impresso tem exatamente um papel; todo tipo, nó e regra existe; entre dois governos é sempre repasse e repasse é sempre entre governos.

`data/scripts/ledger/tests/test_rtn_map.py`

```python
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import reference  # noqa: E402
import rtn_map  # noqa: E402

FIXTURE = Path(__file__).with_name("fixtures") / "rtn-t12-codes-ago26.json"


class RtnMapTest(unittest.TestCase):
    def test_every_printed_code_has_exactly_one_role(self):
        codes = set(json.loads(FIXTURE.read_text(encoding="utf-8"))["codes"])
        self.assertEqual(rtn_map.ALL_CODES, codes)
        roles = [set(rtn_map.LEAVES), rtn_map.TOTALS, set(rtn_map.OF_WHICH), {rtn_map.RGPS_URBAN},
                 set(rtn_map.INTERNAL), set(rtn_map.RESULTS), rtn_map.ADJUSTMENTS, set(rtn_map.INTEREST)]
        self.assertEqual(sum(len(r) for r in roles), len(codes))

    def test_mappings_use_known_types_nodes_and_rules(self):
        types = {t[0] for t in reference.FLOW_TYPES}
        nodes = {n[0] for n in reference.NODES}
        for key, (flow_type, a, b, rule) in {**rtn_map.LEAVES, **rtn_map.REST, **rtn_map.INTEREST}.items():
            self.assertIn(flow_type, types, key)
            self.assertTrue(a in nodes and b in nodes and a != b, key)
            self.assertIn(rule, reference.METHOD, key)

    def test_between_governments_means_transfer_and_nothing_else(self):
        gov = {n[0] for n in reference.NODES if n[3]}
        nature = {t[0]: t[1] for t in reference.FLOW_TYPES}
        for key, (flow_type, a, b, _rule) in {**rtn_map.LEAVES, **rtn_map.REST}.items():
            self.assertEqual(a in gov and b in gov, nature[flow_type] == "intergovernmental", key)

    def test_money_without_a_state_is_marked_never_kept_in_the_uniao(self):  # D127
        for key, (_t, a, b, rule) in {**rtn_map.LEAVES, **rtn_map.REST}.items():
            if reference.METHOD[rule] == "unallocated":
                self.assertIn(b if a == "gov:uniao" else a, ("soc:unknown", "gov:sub:br"), key)

    def test_under(self):
        self.assertTrue(rtn_map.under("1.1.03.3.1", "1.1.03"))
        self.assertTrue(rtn_map.under("4.2~rest", "4.2"))
        self.assertFalse(rtn_map.under("10", "1"))
        self.assertFalse(rtn_map.under("4.3.15.1.10", "4.3.15.1.1"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Passo 3: rodar e ver falhar.** `-p 'test_rtn_map.py'`. Esperado: `No module named 'rtn_map'`.
- [ ] **Passo 4: escrever as fontes.**

`data/scripts/ledger/sources.py`

```python
"""The phase-1 sources: where each one lives and what it measures (spec section 9, D121)."""
from datetime import date

FIRST = date(2019, 1, 1)
LAST = date(2026, 8, 1)


def months(first=FIRST, last=LAST):
    out, y, m = [], first.year, first.month
    while (y, m) <= (last.year, last.month):
        out.append(date(y, m, 1))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


RTN = {
    "dataset": "tesouro.rtn.serie_historica",
    "title": "Resultado do Tesouro Nacional (RTN), série histórica, Tabela 1.2 (Governo Central, mensal, R$ milhões correntes)",
    "publisher": "Secretaria do Tesouro Nacional",
    "url": "https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326",
    "page_url": "https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/8",
    "published_on": date(2026, 9, 29),
    "published_note": "data da publicação do RTN de agosto de 2026 na página do Tesouro",
    "sheet": "1.2",
}

SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial={first}&dataFinal={last}"
SGS_SOAP = "https://www3.bcb.gov.br/wssgs/services/FachadaWSSGS"
SGS = {  # code -> (line_key, the RTN line it mirrors with the sign flipped, official name)
    4606: ("sgs:4606", "9", "NFSP sem desvalorização cambial - Fluxo mensal corrente - Juros nominais - Total - "
                            "Governo Federal e Banco Central"),
    4639: ("sgs:4639", "8", "NFSP sem desvalorização cambial - Fluxo mensal corrente - Resultado primário - Total - "
                            "Governo Federal e Banco Central"),
    4573: ("sgs:4573", "10", "NFSP sem desvalorização cambial - Fluxo mensal corrente - Resultado nominal - Total - "
                             "Governo Federal e Banco Central"),
}
SGS_UNIT_CENTS = 1_000_000  # the SGS prints R$ milhões with two decimals: one printed unit is R$ 10 mil

DTT_CKAN = "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id=despesas-e-transferencias-totais"
DTT_PAGE = "https://www.tesourotransparente.gov.br/ckan/dataset/despesas-e-transferencias-totais"
DTT_YEARS = tuple(range(FIRST.year, LAST.year + 1))
DTT_INTEREST_GROUP = "2"                 # grupo de natureza de despesa 2: Juros e Encargos da Dívida
DTT_INTERNAL_ACTIONS = {"0669": "bcb"}   # Cobertura do resultado negativo apurado no Banco Central: Tesouro to Banco Central
DTT_INTRA_MODALITY = "91"                # aplicação direta intra-orçamentária: inside the União

RREO_URL = ("https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio={year}&nr_periodo={bim}"
            "&co_tipo_demonstrativo=RREO&no_anexo=RREO-Anexo%2001&co_esfera=U&id_ente=1")
RREO_PAGE = "https://siconfi.tesouro.gov.br/siconfi/pages/public/consulta_finbra_rreo/finbra_rreo_list.jsf"
RREO_ACCOUNT = "JurosEEncargosDaDivida"
RREO_PAID_COLUMN = "DESPESAS PAGAS ATÉ O BIMESTRE"
RREO_WHOLE_REAIS_UNIT_CENTS = 100   # 2019 to 2023 the RREO prints whole reais: one printed unit is R$ 1 (D122)
RREO_KNOWN_GAPS = {                 # checkpoint -> DTT minus RREO in cents, beyond the RREO's rounding; cause not found (D122)
    date(2023, 10, 1): -96,
    date(2023, 12, 1): -379,
}


def rreo_bimesters():
    for y in range(FIRST.year, LAST.year + 1):
        for b in range(1, (6 if y < LAST.year else LAST.month // 2) + 1):
            yield y, b
```

- [ ] **Passo 5: escrever o mapa** (é a seção 4 deste plano em código).

`data/scripts/ledger/rtn_map.py`

```python
"""How each line of the RTN Tabela 1.2 becomes ledger rows (spec 4.3 and 4.4, phase 1).

Every code printed in the table has exactly one role here:
  LEAVES      a money flow, with its type, its two nodes and the rule that placed it
  TOTALS      the sum of the lines right under it (the table's own parts add up exactly; checked, never a flow)
  OF_WHICH    a line followed by a 'd/q' (of which) line: stored as that child plus '<code>~rest'
  RGPS_URBAN  1.3.1, which holds the Tesouro's compensation to the RGPS: '1.3.1~ordinary' plus the internal money
  INTERNAL    money the União pays itself (printed on both sides of the table): internal_flow, never a flow
  RESULTS, ADJUSTMENTS, INTEREST  the bottom of the table (lines 3 and 5 to 10)
A code that is not here stops the load: a new line has to be placed first."""

U, SOC, SUB, CRED, DF = "gov:uniao", "soc:unknown", "gov:sub:br", "fin:credores", "gov:uf:DF"   # D127
NAT = "no_state_in_source_v1"


def _in(flow_type):        # people and companies pay the União
    return (flow_type, SOC, U, NAT)


def _out(flow_type):       # the União pays people and companies
    return (flow_type, U, SOC, NAT)


_GOV = ("transfer_union_to_subnational", U, SUB, NAT)   # the União pays state and municipal governments

LEAVES = {
    # 1. Receita total
    "1.1.01": _in("tax"), "1.1.02.1": _in("tax"), "1.1.02.2": _in("tax"), "1.1.02.3": _in("tax"),
    "1.1.02.4": _in("tax"), "1.1.02.5": _in("tax"), "1.1.03.1": _in("tax"), "1.1.03.2": _in("tax"),
    "1.1.03.3.1": _in("tax"), "1.1.03.3.2": _in("tax"), "1.1.03.3.3": _in("tax"), "1.1.03.3.4": _in("tax"),
    "1.1.04": _in("tax"), "1.1.05": _in("tax"), "1.1.06": _in("tax"), "1.1.07": _in("tax"), "1.1.08": _in("tax"),
    "1.1.09": _in("tax"), "1.1.10": _in("tax"), "1.2": _in("tax"), "1.3.2": _in("tax"),
    "1.4.1": _in("other_revenue"),
    "1.4.2.1": _in("dividend_royalty"), "1.4.2.2": _in("dividend_royalty"), "1.4.2.3": _in("dividend_royalty"),
    "1.4.2.4": _in("dividend_royalty"), "1.4.2.5": _in("dividend_royalty"), "1.4.2.6": _in("dividend_royalty"),
    "1.4.2.7": _in("dividend_royalty"), "1.4.2.8": _in("dividend_royalty"), "1.4.2.9": _in("dividend_royalty"),
    "1.4.3": _in("public_payroll_withholding"), "1.4.4": _in("dividend_royalty"), "1.4.5": _in("other_revenue"),
    "1.4.6": _in("tax"), "1.4.7": _in("tax"), "1.4.8.1": _in("other_revenue"),
    # 2. Transferências por repartição de receita
    "2.1": _GOV, "2.2.1": _out("transfer_to_society"), "2.2.2": _out("transfer_to_society"), "2.3": _GOV,
    "2.4": _GOV, "2.5": _GOV, "2.6": _GOV,
    # 4. Despesa total
    "4.1.1.1": _out("social_benefit"), "4.1.2.1": _out("social_benefit"), "4.2.1": _out("public_payroll_gross"),
    "4.3.01.1": _out("social_benefit"), "4.3.01.2.1": _out("social_benefit"), "4.3.02": _out("social_benefit"),
    "4.3.03": _GOV, "4.3.04": _out("social_benefit"), "4.3.05.1": _out("social_benefit"),
    "4.3.06": _out("transfer_to_society"), "4.3.07": _out("mixed_spending"), "4.3.09": _out("purchase"),
    "4.3.10": _GOV, "4.3.11": ("transfer_union_to_subnational", U, DF, "fcdf_df_v1"), "4.3.12": _out("purchase"),
    "4.3.13": _GOV, "4.3.14": _out("court_order"),
    "4.3.15.1.1": _out("subsidy"), "4.3.15.1.2": _out("subsidy"), "4.3.15.1.3.1": _out("subsidy"),
    "4.3.15.1.3.2": _out("subsidy"), "4.3.15.1.3.3": _out("subsidy"), "4.3.15.1.4.1": _out("subsidy"),
    "4.3.15.1.4.2": _out("lending"), "4.3.15.1.4.3": _out("subsidy"), "4.3.15.1.5.1": _out("subsidy"),
    "4.3.15.1.5.2": _out("lending"), "4.3.15.1.6": _out("subsidy"), "4.3.15.1.7": _out("subsidy"),
    "4.3.15.1.8": _out("subsidy"), "4.3.15.1.9": _out("subsidy"), "4.3.15.1.10": _out("subsidy"),
    "4.3.15.1.11": _out("lending"), "4.3.15.1.12": _out("mixed_spending"), "4.3.15.1.13": _out("subsidy"),
    "4.3.15.1.14": _out("subsidy"), "4.3.15.1.15": _out("subsidy"), "4.3.15.1.16": _out("subsidy"),
    "4.3.15.1.17": _out("lending"), "4.3.15.1.18": _out("mixed_spending"), "4.3.15.1.19": _out("mixed_spending"),
    "4.3.15.1.20": _out("subsidy"), "4.3.15.1.21": _out("subsidy"), "4.3.15.1.22": _out("subsidy"),
    "4.3.15.1.23": _out("subsidy"), "4.3.15.1.24": _out("subsidy"),
    "4.3.15.2": _out("subsidy"), "4.3.15.3": _out("mixed_spending"), "4.3.15.4": _out("subsidy"),
    "4.3.16": _out("mixed_spending"), "4.3.17": _out("mixed_spending"), "4.3.18": _out("lending"),
    "4.3.19": _out("transfer_to_society"),
    "4.3.20.1": _out("transfer_to_society"), "4.3.20.2": _out("mixed_spending"), "4.3.20.3": _out("mixed_spending"),
    "4.3.20.4": _out("mixed_spending"), "4.3.20.5": _out("mixed_spending"), "4.3.20.6": _GOV,
    "4.4.1.1": _out("public_payroll_gross"), "4.4.1.2": _out("social_benefit"), "4.4.1.3": _out("mixed_spending"),
    "4.4.1.4": _out("mixed_spending"), "4.4.1.5": _out("mixed_spending"),
    "4.4.2.1": _out("mixed_spending"), "4.4.2.2": _out("mixed_spending"), "4.4.2.3": _out("mixed_spending"),
    "4.4.2.4": _out("mixed_spending"), "4.4.2.5": _out("mixed_spending"), "4.4.2.6": _out("mixed_spending"),
    "4.4.2.7": _out("mixed_spending"), "4.4.2.8": _out("mixed_spending"), "4.4.2.9": _out("mixed_spending"),
}

OF_WHICH = {"1.4.8": "1.4.8.1", "4.1.1": "4.1.1.1", "4.1.2": "4.1.2.1", "4.2": "4.2.1",
            "4.3.01.2": "4.3.01.2.1", "4.3.05": "4.3.05.1"}

RGPS_URBAN = "1.3.1"
RGPS_ORDINARY = "1.3.1~ordinary"
COMPENSATION_MEMO = "memo:Compensação ao RGPS pelas Desonerações da Folha"

DERIVED = {  # derived key -> (printed line, the part taken out of it)
    **{f"{parent}~rest": (parent, child) for parent, child in OF_WHICH.items()},
    RGPS_ORDINARY: (RGPS_URBAN, COMPENSATION_MEMO),
}

REST = {
    "1.4.8~rest": _in("other_revenue"), "4.1.1~rest": _out("social_benefit"), "4.1.2~rest": _out("social_benefit"),
    "4.2~rest": _out("public_payroll_gross"), "4.3.01.2~rest": _out("social_benefit"),
    "4.3.05~rest": _out("social_benefit"), RGPS_ORDINARY: _in("tax"),
}

INTERNAL = {"4.3.08": ("tesouro", "rgps", RGPS_URBAN)}   # compensation for the payroll tax relief, also inside 1.3.1

TOTALS = {"1", "1.1", "1.1.02", "1.1.03", "1.1.03.3", "1.3", "1.4", "1.4.2", "2", "2.2", "4", "4.1", "4.3", "4.3.01",
          "4.3.15", "4.3.15.1", "4.3.15.1.3", "4.3.15.1.4", "4.3.15.1.5", "4.3.20", "4.4", "4.4.1", "4.4.2"}
PARTITIONS = TOTALS | {"6"}                              # their printed parts add up exactly (closure check)

RESULTS = {"3": (("1", 1), ("2", -1)), "5": (("3", 1), ("4", -1)), "8": (("5", 1), ("6", 1), ("7", 1)),
           "10": (("8", 1), ("9", 1))}
ADJUSTMENTS = {"6", "6.1", "6.2", "6.3", "6.4", "7"}     # methodological adjustments and statistical discrepancy: not money
INTEREST = {"9": ("interest", U, CRED, "no_state_endpoint_v1")}   # Banco Central, accrual; printed negative

PAIR = {"4.2~rest", "1.4.3"}   # gross payroll without court orders, and the servants' contribution withheld from it

MEMO_CHECKS = {  # memo line -> the ledger lines that must add up to it
    "memo:Arrecadação Líquida para o RGPS": ("1.3",),
    "memo:Arrecadação Ordinária": (RGPS_ORDINARY, "1.3.2"),
    COMPENSATION_MEMO: ("4.3.08",),
}

ALL_CODES = (set(LEAVES) | TOTALS | set(OF_WHICH) | {RGPS_URBAN} | set(INTERNAL) | set(RESULTS) | ADJUSTMENTS
             | set(INTEREST))


def kind_of(code):
    if code in LEAVES or code in INTERNAL or code in INTEREST:
        return "leaf"
    if code in TOTALS or code in OF_WHICH or code == RGPS_URBAN:
        return "total"
    if code in RESULTS:
        return "result"
    if code in ADJUSTMENTS:
        return "adjustment"
    raise KeyError(code)


def parent(code):
    return code.rsplit(".", 1)[0] if "." in code else None


def under(key, line):
    """True when ledger key `key` is part of printed line `line` (the line itself, a sub-code, or a derived part)."""
    return key == line or key.startswith(line + ".") or key.startswith(line + "~")
```

- [ ] **Passo 6: rodar e ver passar.** Esperado: `Ran 5 tests ... OK`.

## Tarefa 5: carregador do RTN

**Arquivo:** criar `load_rtn.py`.

- [ ] **Passo 1: escrever o carregador.**

`data/scripts/ledger/load_rtn.py`

```python
"""Load the RTN Tabela 1.2 (Governo Central, monthly, R$ milhões) into the ledger: every printed line as a
published_line, the money lines as flows (rtn_map.py), the União's payments to itself as internal_flow.

Usage: /usr/local/bin/python3 data/scripts/ledger/load_rtn.py
The file is read once from the Tesouro, hashed while it streams and deleted at the end (registry.fetch)."""
import hashlib
import re
from datetime import date

import openpyxl

import db
import reference
import registry
import rtn_map
import sources
from money import from_millions, to_cents

CODE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s")


def flow_id(dataset, key, period, from_node, to_node, flow_type):
    raw = "|".join([dataset, key, period.isoformat(), from_node, to_node, flow_type])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def read_table(path):
    """{code: (label, {period: number})} and {memo key: (label, {period: number or text})} for FIRST..LAST."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb[sources.RTN["sheet"]].iter_rows(values_only=True))
    wb.close()
    title, unit = str(rows[1][0]), str(rows[2][0])
    if not (title.startswith("Tabela 1.2.") and "R$ Milhões" in unit and "Correntes" in unit):
        raise SystemExit(f"RTN Tabela 1.2 layout changed: {title!r} / {unit!r}")
    cols = {}
    for j, d in enumerate(rows[4]):
        if hasattr(d, "year") and sources.FIRST <= date(d.year, d.month, 1) <= sources.LAST:
            cols[date(d.year, d.month, 1)] = j
    if sorted(cols) != sources.months():
        raise SystemExit(f"RTN months do not cover {sources.FIRST} to {sources.LAST}")
    lines, memo, section = {}, {}, "lines"
    for r in rows[5:]:
        label = str(r[0]).strip() if r[0] is not None else ""
        if not label:
            continue
        if label == "Memorando":
            section = "memo"
            continue
        if label.startswith("Obs."):
            break
        values = {p: r[j] for p, j in cols.items()}
        if section == "memo":
            memo["memo:" + label] = (label, values)
            continue
        m = CODE.match(label)
        if not m or m.group(1) in lines:
            raise SystemExit(f"RTN line without a code, or a code twice: {label!r}")
        bad = [p for p, v in values.items() if not isinstance(v, (int, float))]
        if bad:
            raise SystemExit(f"RTN {m.group(1)}: not a number in {bad[0]}")
        lines[m.group(1)] = (label, values)
    return lines, memo


def build_rows(lines, memo, source_id, dataset):
    if set(lines) != rtn_map.ALL_CODES:
        raise SystemExit(f"RTN codes changed: new {sorted(set(lines) - rtn_map.ALL_CODES)}, "
                         f"gone {sorted(rtn_map.ALL_CODES - set(lines))}; place them in rtn_map.py first")
    published, flows, internal, ex = [], [], [], {}
    for code, (label, values) in lines.items():
        sign = -1 if code in rtn_map.INTEREST else 1
        for p, v in values.items():
            e = ex[(code, p)] = from_millions(v)
            published.append((source_id, code, p, rtn_map.kind_of(code), label, e, to_cents(e), sign))
    for key, (label, values) in memo.items():
        for p, v in values.items():
            e = from_millions(v) if isinstance(v, (int, float)) else None
            if e is not None:
                ex[(key, p)] = e
            published.append((source_id, key, p, "memo", label, e, None if e is None else to_cents(e), 1))
    labels = {**{c: lb for c, (lb, _) in lines.items()}, **{k: lb for k, (lb, _) in memo.items()}}
    for key, (whole, part) in rtn_map.DERIVED.items():
        label = f"{labels[whole]}, exceto: {labels[part]}"
        for p in sources.months():
            e = ex[(key, p)] = ex[(whole, p)] - ex[(part, p)]
            published.append((source_id, key, p, "derived", label, e, to_cents(e), 1))
    for key, (flow_type, frm, to, rule) in {**rtn_map.LEAVES, **rtn_map.REST, **rtn_map.INTEREST}.items():
        basis, sign = ("accrual", -1) if key in rtn_map.INTEREST else ("cash", 1)
        for p in sources.months():
            cents = sign * to_cents(ex[(key, p)])
            if cents:
                pair = f"payroll:{p:%Y-%m}" if key in rtn_map.PAIR else None
                flows.append((flow_id(dataset, key, p, frm, to, flow_type), p, frm, to, flow_type, cents, basis,
                              source_id, key, reference.METHOD[rule], rule, pair))
    for key, (from_part, to_part, also_in) in rtn_map.INTERNAL.items():
        for p in sources.months():
            cents = to_cents(ex[(key, p)])
            if cents:
                internal.append((source_id, key, also_in, p, from_part, to_part, cents))
    return published, flows, internal


def run(con):
    s = sources.RTN
    with registry.fetch(s["url"], suffix=".xlsx") as fx:
        con.begin()
        try:
            source_id, new = registry.register(con, s["dataset"], fx, title=s["title"], publisher=s["publisher"],
                                               page_url=s["page_url"], published_on=s["published_on"],
                                               published_note=s["published_note"], loader="load_rtn.py")
            if new:
                db.insert(con, *build_rows(*read_table(fx.path), source_id, s["dataset"]))
            con.commit()
        except BaseException:
            con.rollback()
            raise
    out = {"dataset": s["dataset"], "source_id": source_id, "new": new, "sha256": fx.sha256, "bytes": fx.bytes}
    print("rtn", out)
    return out


if __name__ == "__main__":
    run(db.connect())
```

- [ ] **Passo 2: rodar.** `/usr/local/bin/python3 data/scripts/ledger/load_rtn.py`. Esperado: uma linha `rtn {... 'new': True ...}` com o SHA-256 e cerca de 4,3 MB.
- [ ] **Passo 3: conferir o que entrou.**

```bash
/usr/local/bin/python3 - <<'PY'
import sys; sys.path.insert(0, "data/scripts/ledger")
import db
con = db.connect()
for t in ("published_line", "flow_stage", "internal_flow", "source_release"):
    print(t, con.execute(f"SELECT count(*) FROM {t}").fetchone()[0])
print("pairs", con.execute("SELECT count(DISTINCT pair_id) FROM flow_stage").fetchone()[0])
PY
```

Esperado: `published_line 16008` (159 linhas, 8 de memorando e 7 derivadas, vezes 92 meses), `flow_stage 8281`, `internal_flow 40`, `source_release 1`, `pairs 92`.

- [ ] **Passo 4: rodar de novo.** Esperado: `'new': False` e as mesmas contagens (carregar duas vezes a mesma divulgação não muda nada).

## Tarefa 6: carregador do Banco Central

**Arquivo:** criar `load_sgs.py`.

- [ ] **Passo 1: escrever o carregador.** Antes de ler os valores, confere o nome oficial de cada série no serviço do SGS.

`data/scripts/ledger/load_sgs.py`

```python
"""Load the Banco Central's NFSP series for the Governo Central (SGS 4606, 4639 and 4573): the independent check of
RTN lines 9, 8 and 10 (interest by accrual, D121). Stored as published lines only; they are not flows.

Usage: /usr/local/bin/python3 data/scripts/ledger/load_sgs.py"""
import calendar
import html
import json
import re
import time
from datetime import date

import db
import registry
import sources
from money import from_millions, to_cents

SOAP = ('<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
        'xmlns:pub="http://publico.ws.wssgs.bcb.gov.br"><soapenv:Body><pub:getUltimoValorXML><in0>{code}</in0>'
        '</pub:getUltimoValorXML></soapenv:Body></soapenv:Envelope>')


def official_name(code):
    with registry.fetch(sources.SGS_SOAP, data=SOAP.format(code=code).encode("utf-8"), timeout=60,
                        headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": '""'}) as fx:
        names = re.findall(r"<NOME>(.*?)</NOME>", html.unescape(fx.path.read_text(encoding="utf-8", errors="replace")))
    if len(names) != 1:
        raise SystemExit(f"SGS {code}: the service did not return one name")
    return names[0].strip()


def fetch_series(url):
    """The SGS API answers an empty body now and then: up to three tries, 10 s apart."""
    for attempt in range(1, 4):
        with registry.fetch(url, timeout=120) as fx:
            raw = fx.path.read_bytes()
        try:
            items = json.loads(raw)
            if isinstance(items, list) and items:
                return fx, items
        except json.JSONDecodeError:
            pass
        time.sleep(10 * attempt)
    raise SystemExit(f"SGS: no valid answer from {url}")


def run(con):
    out = []
    last_day = calendar.monthrange(sources.LAST.year, sources.LAST.month)[1]
    for code, (key, rtn_line, name) in sources.SGS.items():
        if official_name(code) != name:
            raise SystemExit(f"SGS {code} changed its name; expected {name!r}")
        url = sources.SGS_URL.format(code=code, first=sources.FIRST.strftime("%d/%m/%Y"),
                                     last=f"{last_day:02d}/{sources.LAST:%m/%Y}")
        fx, items = fetch_series(url)
        con.begin()
        try:
            source_id, new = registry.register(
                con, f"bcb.sgs.{code}", fx, title=f"SGS {code}: {name}", publisher="Banco Central do Brasil",
                page_url="https://www3.bcb.gov.br/sgspub/", published_on=None,
                published_note="o Banco Central não publica a data de divulgação na API", loader="load_sgs.py")
            if new:
                rows = []
                for it in items:
                    d, m, y = it["data"].split("/")
                    e = from_millions(it["valor"])
                    rows.append((source_id, key, date(int(y), int(m), 1), "series", name, e, to_cents(e), 1))
                if sorted(r[2] for r in rows) != sources.months():
                    raise SystemExit(f"SGS {code}: months do not cover {sources.FIRST} to {sources.LAST}")
                db.insert(con, published=rows)
            con.commit()
        except BaseException:
            con.rollback()
            raise
        out.append({"dataset": f"bcb.sgs.{code}", "source_id": source_id, "new": new, "sha256": fx.sha256,
                    "bytes": fx.bytes})
        print("sgs", out[-1])
    return out


if __name__ == "__main__":
    run(db.connect())
```

- [ ] **Passo 2: rodar.** `/usr/local/bin/python3 data/scripts/ledger/load_sgs.py`. Esperado: três linhas `sgs {...}`, e 276 linhas novas em `published_line` (3 séries vezes 92 meses).

## Tarefa 7: carregador dos juros pagos em dinheiro

**Arquivo:** criar `load_dtt_interest.py`.

- [ ] **Passo 1: escrever o carregador.**

`data/scripts/ledger/load_dtt_interest.py`

```python
"""Load the interest the União paid in cash (D121): Tesouro, base "Despesas e Transferências Totais da União",
grupo de natureza de despesa 2 (Juros e Encargos da Dívida), by month, one year file at a time.

Usage: /usr/local/bin/python3 data/scripts/ledger/load_dtt_interest.py [YEAR ...]
Each file (23 to 38 MB) is read once, hashed while it streams, summed and deleted before the next one starts.
The money the Tesouro passes to the Banco Central (action 0669) and intra-budget payments stay inside the União:
internal_flow, never a flow to the creditors."""
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

import openpyxl

import db
import registry
import sources
from load_rtn import flow_id
from money import exact, to_cents

NEED = ("ID_ANO", "ID_MES", "ORGAO_CODIGO", "UNIDADE_ORCAMENTARIA_CODIGO", "ID_GRUPO_DESPESA_NADE", "CO_MOAP_NADE",
        "ACAO", "NO_ACAO", "DESPESAS_PAGAS", "RESTOS_A_PAGAR_PAGOS", "PAGAMENTOS_TOTAIS")
PARTS = {"paid": ("DESPESAS_PAGAS", "despesas do ano pagas"), "rap": ("RESTOS_A_PAGAR_PAGOS", "restos a pagar pagos")}
EPS = Decimal("0.001")


def resources():
    with registry.fetch(sources.DTT_CKAN, timeout=60) as fx:
        items = json.loads(fx.path.read_bytes())["result"]["resources"]
    return {int(x["name"][-4:]): x for x in items if x["name"].startswith("Despesas e Transferências da União - ")}


def read_interest(path, year):
    """{(key, period): {"paid": Decimal, "rap": Decimal}} and {key: action name}, group 2 only."""
    wb = openpyxl.load_workbook(path, read_only=True)
    sheet = next(n for n in wb.sheetnames if next(wb[n].iter_rows(max_row=1, values_only=True))[0] == "ID_ANO")
    rows = wb[sheet].iter_rows(values_only=True)
    header = [str(c).strip().upper() for c in next(rows)]
    missing = [c for c in NEED if c not in header]
    if missing:
        raise SystemExit(f"DTT {year}: columns missing {missing}")
    ix = {c: header.index(c) for c in NEED}
    agg, names = defaultdict(lambda: {"paid": Decimal(0), "rap": Decimal(0)}), {}
    for r in rows:
        if r[ix["ID_MES"]] is None or str(r[ix["ID_GRUPO_DESPESA_NADE"]]).strip() != sources.DTT_INTEREST_GROUP:
            continue
        if int(r[ix["ID_ANO"]]) != year:
            raise SystemExit(f"DTT {year}: a row of year {r[ix['ID_ANO']]}")
        p = date(year, int(r[ix["ID_MES"]]), 1)
        action = str(r[ix["ACAO"]]).strip().zfill(4)
        key = ".".join([str(r[ix["ORGAO_CODIGO"]]).strip(), str(r[ix["UNIDADE_ORCAMENTARIA_CODIGO"]]).strip(), action,
                        str(r[ix["CO_MOAP_NADE"]]).strip()])
        paid, rap, total = (exact(r[ix[c]] or 0) for c in ("DESPESAS_PAGAS", "RESTOS_A_PAGAR_PAGOS", "PAGAMENTOS_TOTAIS"))
        if abs(paid + rap - total) > EPS:
            raise SystemExit(f"DTT {year} {key} {p}: despesas pagas + restos a pagar pagos != pagamentos totais")
        agg[(key, p)]["paid"] += paid
        agg[(key, p)]["rap"] += rap
        names[key] = str(r[ix["NO_ACAO"]]).strip()
    wb.close()
    return agg, names


def build_rows(agg, names, source_id, dataset):
    published, flows, internal = [], [], []
    for (key, p), parts in sorted(agg.items()):
        if p > sources.LAST:
            continue
        action, modality = key.split(".")[2], key.split(".")[3]
        for part, (column, label) in PARTS.items():
            line_key, e = f"{key}|{part}", parts[part]
            cents = to_cents(e)
            published.append((source_id, line_key, p, "leaf", f"{names[key]} ({label})", e, cents, 1))
            if not cents:
                continue
            if action in sources.DTT_INTERNAL_ACTIONS:
                internal.append((source_id, line_key, None, p, "tesouro", sources.DTT_INTERNAL_ACTIONS[action], cents))
            elif modality == sources.DTT_INTRA_MODALITY:
                internal.append((source_id, line_key, None, p, "tesouro", "intra", cents))
            else:
                flows.append((flow_id(dataset, line_key, p, "gov:uniao", "fin:credores", "interest"), p, "gov:uniao",
                              "fin:credores", "interest", cents, "cash", source_id, line_key, "direct",
                              "no_state_endpoint_v1", None))
    return published, flows, internal


def run(con, years=sources.DTT_YEARS):
    res, out = resources(), []
    for year in years:
        r, dataset = res[year], f"tesouro.dtt.{year}"
        with registry.fetch(r["url"], suffix=".xlsx", timeout=1500) as fx:
            con.begin()
            try:
                source_id, new = registry.register(
                    con, dataset, fx, title=r["name"], publisher="Secretaria do Tesouro Nacional",
                    page_url=sources.DTT_PAGE, published_on=datetime.fromisoformat(r["last_modified"]).date(),
                    published_note="data de atualização do arquivo no portal (CKAN last_modified)",
                    loader="load_dtt_interest.py")
                if new:
                    db.insert(con, *build_rows(*read_interest(fx.path, year), source_id, dataset))
                con.commit()
            except BaseException:
                con.rollback()
                raise
        out.append({"dataset": dataset, "source_id": source_id, "new": new, "sha256": fx.sha256, "bytes": fx.bytes})
        print("dtt", out[-1], flush=True)
    return out


if __name__ == "__main__":
    years = tuple(int(a) for a in sys.argv[1:]) or sources.DTT_YEARS
    run(db.connect(), years)
```

- [ ] **Passo 2: rodar um ano por vez**, conferindo o disco antes de cada um (`df -h ~ | tail -1`):

```bash
for y in 2019 2020 2021 2022 2023 2024 2025 2026; do
  df -h ~ | tail -1
  /usr/local/bin/python3 data/scripts/ledger/load_dtt_interest.py $y || break
done
ls /var/folders/*/*/T/ 2>/dev/null | grep -c bi-ledger
```

Esperado: oito linhas `dtt {...}` com arquivos de 23 a 38 MB e, no fim, `0` (nenhuma pasta temporária sobrou).

## Tarefa 8: carregador do RREO da União

**Arquivo:** criar `load_rreo_union.py`.

- [ ] **Passo 1: escrever o carregador.**

`data/scripts/ledger/load_rreo_union.py`

```python
"""Load the União's RREO Anexo 1 from SICONFI: 'Juros e Encargos da Dívida', despesas pagas até o bimestre.
It is the independent total the cash interest of the DTT base must match, to the cent (guarantee 3).

Usage: /usr/local/bin/python3 data/scripts/ledger/load_rreo_union.py"""
import json
import time
from datetime import date

import db
import registry
import sources
from money import exact, to_cents


def run(con):
    out = []
    for year, bim in sources.rreo_bimesters():
        dataset = f"tesouro.siconfi.rreo.uniao.anexo01.{year}.b{bim}"
        with registry.fetch(sources.RREO_URL.format(year=year, bim=bim), timeout=120) as fx:
            data = json.loads(fx.path.read_bytes())
            if data.get("hasMore"):
                raise SystemExit(f"RREO {year} b{bim}: the answer is paginated")
            hits = [i for i in data["items"]
                    if i["cod_conta"] == sources.RREO_ACCOUNT and i["coluna"].startswith(sources.RREO_PAID_COLUMN)]
            if len(hits) != 1:
                raise SystemExit(f"RREO {year} b{bim}: {len(hits)} lines for {sources.RREO_ACCOUNT}")
            e = exact(hits[0]["valor"])
            con.begin()
            try:
                source_id, new = registry.register(
                    con, dataset, fx, title=f"RREO da União, {year}, {bim}º bimestre, Anexo 1",
                    publisher="Secretaria do Tesouro Nacional (SICONFI)", page_url=sources.RREO_PAGE,
                    published_on=None, published_note="o SICONFI não informa a data de divulgação na API",
                    loader="load_rreo_union.py")
                if new:
                    db.insert(con, published=[(source_id, "rreo:interest_paid_ytd", date(year, 2 * bim, 1), "control",
                                               f"{hits[0]['conta']}, {hits[0]['coluna']}", e, to_cents(e), 1)])
                con.commit()
            except BaseException:
                con.rollback()
                raise
        out.append({"dataset": dataset, "source_id": source_id, "new": new, "sha256": fx.sha256, "bytes": fx.bytes})
        time.sleep(1)
    print("rreo", len(out), "bimesters,", sum(o["new"] for o in out), "new", flush=True)
    return out


if __name__ == "__main__":
    run(db.connect())
```

- [ ] **Passo 2: rodar.** `/usr/local/bin/python3 data/scripts/ledger/load_rreo_union.py`. Esperado: `rreo 46 bimesters, 46 new` (seis por ano de 2019 a 2025 e quatro em 2026).

## Tarefa 9: medidas e garantias

**Arquivos:** criar `measures.py`, `guarantees.py` e `tests/test_guarantees.py`.

- [ ] **Passo 1: escrever o teste.** Um livro mínimo de duas linhas passa em tudo; cada garantia pega o erro feito para ela; e a regra do RREO (D122) aceita só o que a decisão aceita.

`data/scripts/ledger/tests/test_guarantees.py`

```python
import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import db  # noqa: E402
import guarantees as g  # noqa: E402

P = date(2026, 8, 1)
FLOWS = [
    ("f1", P, "soc:unknown", "gov:uniao", "public_payroll_withholding", 100, "cash", "t@1", "A", "unallocated",
     "no_state_in_source_v1", "payroll:2026-08"),
    ("f2", P, "gov:uniao", "soc:unknown", "public_payroll_gross", 200, "cash", "t@1", "B", "unallocated",
     "no_state_in_source_v1", "payroll:2026-08"),
]
CHECKS = (g.g1_unique_ids, g.g2_complete_rows, g.g4_lines_conserved, g.g6_pairs_same_state, g.g7_no_transfer_in_spending)


def fixture():
    con = db.connect(":memory:")
    con.execute("INSERT INTO source_release VALUES ('t@1', 't.ds', 't', 'p', 'u', NULL, NULL, NULL, ?, 1, "
                "TIMESTAMP '2026-10-08 00:00:00', 'test')", ["0" * 64])
    db.insert(con, published=[("t@1", "A", P, "leaf", "a", Decimal("1.00"), 100, 1),
                              ("t@1", "B", P, "leaf", "b", Decimal("2.00"), 200, 1)], flows=FLOWS)
    con.execute("CREATE TEMP TABLE cand AS SELECT * FROM flow_stage")
    return con


class GuaranteesTest(unittest.TestCase):
    def setUp(self):
        self.con = fixture()

    def failed(self, check):
        return not check(self.con, "cand").ok

    def test_clean_rows_pass_every_check(self):
        for check in CHECKS:
            self.assertFalse(self.failed(check), check.__name__)

    def test_g1_catches_a_duplicate(self):
        self.con.execute("INSERT INTO cand SELECT * FROM cand WHERE flow_id = 'f1'")
        self.assertTrue(self.failed(g.g1_unique_ids))

    def test_g2_catches_same_origin_and_destination(self):
        self.con.execute("UPDATE cand SET to_node = 'soc:unknown' WHERE flow_id = 'f1'")
        self.assertTrue(self.failed(g.g2_complete_rows))

    def test_g2_catches_a_negative_purchase(self):
        self.con.execute("UPDATE cand SET flow_type = 'purchase', amount_cents = -200 WHERE flow_id = 'f2'")
        self.assertTrue(self.failed(g.g2_complete_rows))

    def test_g4_catches_a_deleted_row(self):
        self.con.execute("DELETE FROM cand WHERE flow_id = 'f2'")
        self.assertTrue(self.failed(g.g4_lines_conserved))

    def test_g4_catches_a_flipped_sign(self):
        self.con.execute("UPDATE cand SET amount_cents = -amount_cents WHERE flow_id = 'f1'")
        self.assertTrue(self.failed(g.g4_lines_conserved))

    def test_g6_catches_a_pair_split_across_states(self):
        self.con.execute("UPDATE cand SET from_node = 'soc:uf:DF' WHERE flow_id = 'f1'")
        self.assertTrue(self.failed(g.g6_pairs_same_state))

    def test_g7_catches_a_payment_to_a_government_typed_as_spending(self):
        self.con.execute("UPDATE cand SET to_node = 'gov:sub:br' WHERE flow_id = 'f2'")
        self.assertTrue(self.failed(g.g7_no_transfer_in_spending))


class RreoVerdictTest(unittest.TestCase):  # decision D122
    def test_years_printed_in_cents_must_match_to_the_cent(self):
        self.assertEqual(g.rreo_verdict(date(2025, 12, 1), 100, 100, False), "ok")
        self.assertEqual(g.rreo_verdict(date(2025, 12, 1), 101, 100, False), "fail")

    def test_years_printed_in_whole_reais_allow_one_printed_unit(self):
        self.assertEqual(g.rreo_verdict(date(2021, 6, 1), 950, 1000, True), "ok")
        self.assertEqual(g.rreo_verdict(date(2021, 6, 1), 899, 1000, True), "fail")

    def test_known_gaps_must_stay_exactly_as_recorded(self):
        self.assertEqual(g.rreo_verdict(date(2023, 12, 1), 1000 - 379, 1000, True), "known_gap")
        self.assertEqual(g.rreo_verdict(date(2023, 12, 1), 1000 - 380, 1000, True), "fail")
        self.assertEqual(g.rreo_verdict(date(2023, 10, 1), 1000, 1000, True), "fail")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Passo 2: rodar e ver falhar.** `-p 'test_guarantees.py'`. Esperado: `No module named 'guarantees'`.
- [ ] **Passo 3: escrever as medidas.** A conta da União sai daqui: cada linha do RTN refeita a partir dos fluxos.

`data/scripts/ledger/measures.py`

```python
"""Measures: every number on screen is a sum over the ledger (spec section 5). Phase 1 has the União account: the RTN
lines rebuilt from the flows, plus the interest paid in cash. Interest by accrual and by cash are never added up."""
from collections import defaultdict

import rtn_map
import sources

SPENDING_SQL = """SELECT f.* FROM {flow} f JOIN flow_type t ON t.flow_type_id = f.flow_type
JOIN node a ON a.node_id = f.from_node JOIN node b ON b.node_id = f.to_node
WHERE a.is_government AND NOT b.is_government AND t.nature = 'primary'"""

LINES = (("revenue", "1"), ("transfers_to_subnationals", "2"), ("revenue_net", "3"), ("primary_spending", "4"),
         ("primary_result", "5"), ("primary_result_below_line", "8"), ("nominal_interest", "9"), ("nominal_result", "10"))


class RtnLedger:
    """The RTN Tabela 1.2 rebuilt from the ledger. line(code, period) -> (cents, number of rounded terms)."""

    def __init__(self, con, flow):
        ds = sources.RTN["dataset"]
        self.by_period = defaultdict(list)
        for key, p, s, n in con.execute(f"""SELECT f.source_key, f.period, sum(f.amount_cents), count(*)
                FROM {flow} f JOIN current_release r USING (source_id) WHERE r.dataset = ? GROUP BY ALL""", [ds]).fetchall():
            self.by_period[p].append((key, None, int(s), int(n)))
        for key, also, p, c in con.execute("SELECT source_key, also_in_key, period, amount_cents FROM cur_internal "
                                           "WHERE dataset = ?", [ds]).fetchall():
            self.by_period[p].append((key, also, int(c), 1))
        self.pub = {(k, p): (c, sign, kind) for k, p, c, sign, kind in con.execute(
            "SELECT line_key, period, value_cents, flow_sign, kind FROM cur_line WHERE dataset = ?", [ds]).fetchall()}

    def line(self, code, p):
        if code in rtn_map.RESULTS:
            total = n = 0
            for part, sign in rtn_map.RESULTS[code]:
                if part in rtn_map.ADJUSTMENTS:
                    total, n = total + sign * self.pub[(part, p)][0], n + 1
                else:
                    v, k = self.line(part, p)
                    total, n = total + sign * v, n + k
            return total, n
        total = n = 0
        for key, also, cents, k in self.by_period.get(p, ()):
            if rtn_map.under(key, code) or (also is not None and rtn_map.under(also, code)):
                total, n = total + cents, n + k
        return (-total if code in rtn_map.INTEREST else total), n


def union_account(con, flow):
    """{period: {line name: cents}} with the RTN's signs, plus interest_paid_cash (DTT, positive = paid)."""
    led = RtnLedger(con, flow)
    cash = dict(con.execute(f"""SELECT f.period, sum(f.amount_cents) FROM {flow} f JOIN current_release r USING (source_id)
        WHERE f.flow_type = 'interest' AND f.basis = 'cash' GROUP BY 1""").fetchall())
    out = {}
    for p in sources.months():
        out[p] = {name: led.line(code, p)[0] for name, code in LINES}
        out[p]["interest_paid_cash"] = int(cash.get(p, 0))
    return out
```

- [ ] **Passo 4: escrever as garantias.**

`data/scripts/ledger/guarantees.py`

```python
"""The guarantees of spec section 6. Each check returns a Result; build.py publishes only when every one is ok and
every planted error (planted.py) is caught by at least one of them."""
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal

import measures
import rtn_map
import sources

EPS = Decimal("0.001")      # reais; the RTN's own parts close within R$ 0.00005 (measured 2026-10-08)
RREO_CHECKPOINTS = len(list(sources.rreo_bimesters()))


@dataclass
class Result:
    name: str
    failures: int = 0
    sample: list = field(default_factory=list)
    detail: dict = field(default_factory=dict)

    @property
    def ok(self):
        return self.failures == 0

    def fail(self, item):
        self.failures += 1
        if len(self.sample) < 8:
            self.sample.append(item)


def _rows(con, sql, params=()):
    return con.execute(sql, list(params)).fetchall()


def rreo_verdict(until, dtt_cents, rreo_cents, whole_reais):
    """'ok', 'known_gap' or 'fail' for one RREO checkpoint (D122): to the cent where the RREO prints cents, one printed
    unit (R$ 1) where it prints whole reais, and a recorded gap only when it is exactly the one recorded."""
    gap = dtt_cents - rreo_cents
    if until in sources.RREO_KNOWN_GAPS:
        return "known_gap" if gap == sources.RREO_KNOWN_GAPS[until] else "fail"
    return "ok" if abs(gap) <= (sources.RREO_WHOLE_REAIS_UNIT_CENTS if whole_reais else 0) else "fail"


def g1_unique_ids(con, flow):
    r = Result("G1 nenhum flow_id repetido")
    for fid, n in _rows(con, f"SELECT flow_id, count(*) FROM {flow} GROUP BY flow_id HAVING count(*) > 1"):
        r.fail({"flow_id": fid, "copies": int(n)})
    return r


def g2_complete_rows(con, flow):
    r = Result("G2 toda linha tem origem, destino diferente, tipo, fonte e método de localização")
    sql = f"""SELECT f.flow_id, f.source_key, f.period FROM {flow} f
        LEFT JOIN node a ON a.node_id = f.from_node
        LEFT JOIN node b ON b.node_id = f.to_node
        LEFT JOIN flow_type t ON t.flow_type_id = f.flow_type
        LEFT JOIN current_release s ON s.source_id = f.source_id
        LEFT JOIN allocation_rule ar ON ar.rule_id = f.rule_id
        WHERE f.flow_id IS NULL OR f.period IS NULL OR f.amount_cents IS NULL OR f.source_key IS NULL
           OR a.node_id IS NULL OR b.node_id IS NULL OR f.from_node = f.to_node
           OR t.flow_type_id IS NULL OR s.source_id IS NULL OR ar.rule_id IS NULL
           OR f.basis IS NULL OR f.basis NOT IN ('cash', 'accrual')
           OR f.location_method IS DISTINCT FROM ar.method
           OR (NOT t.allows_negative AND f.amount_cents < 0)
           OR f.amount_cents = 0 OR day(f.period) <> 1"""
    for fid, key, p in _rows(con, sql):
        r.fail({"flow_id": fid, "source_key": key, "period": str(p)})
    return r


def g3_release_totals(con, flow):
    r = Result("G3 cada divulgação fecha com o total que ela mesma publica")
    ds = sources.RTN["dataset"]
    printed = {(k, p): e for k, p, e in _rows(con, "SELECT line_key, period, value_reais FROM cur_line WHERE dataset = ? "
                                                  "AND kind IN ('leaf', 'total', 'adjustment')", [ds])}
    worst = Decimal(0)
    for total in sorted(rtn_map.PARTITIONS):
        parts = [c for c in rtn_map.ALL_CODES if rtn_map.parent(c) == total]
        for p in sources.months():
            d = abs(sum(printed[(c, p)] for c in parts) - printed[(total, p)])
            worst = max(worst, d)
            if d > EPS:
                r.fail({"rtn_line": total, "period": str(p), "parts_minus_total_reais": str(d)})
    r.detail["rtn_parts_vs_totals_worst_reais"] = str(worst)
    led, worst_c = measures.RtnLedger(con, flow), 0
    for code in ("1", "2", "4"):
        for p in sources.months():
            v, n = led.line(code, p)
            d = abs(v - led.pub[(code, p)][0])
            worst_c = max(worst_c, d)
            if d > (n + 1) // 2:
                r.fail({"rtn_line": code, "period": str(p), "ledger_cents": v, "printed_cents": led.pub[(code, p)][0]})
    r.detail["rtn_lines_1_2_4_worst_cents"] = worst_c
    paid = defaultdict(int)
    for p, c in _rows(con, f"""SELECT f.period, sum(f.amount_cents) FROM {flow} f JOIN current_release s USING (source_id)
            WHERE s.dataset LIKE 'tesouro.dtt.%' AND f.source_key LIKE '%|paid' GROUP BY 1"""):
        paid[p] += int(c)
    for p, c in _rows(con, """SELECT period, sum(amount_cents) FROM cur_internal WHERE dataset LIKE 'tesouro.dtt.%'
            AND source_key LIKE '%|paid' AND to_part <> 'intra' GROUP BY 1"""):
        paid[p] += int(c)
    rreo = _rows(con, "SELECT period, value_cents FROM cur_line WHERE kind = 'control' AND line_key = 'rreo:interest_paid_ytd'")
    whole = defaultdict(lambda: True)        # a year prints whole reais when every checkpoint of it ends in ,00
    for until, c in rreo:
        whole[until.year] = whole[until.year] and int(c) % 100 == 0
    known, worst_r = {}, 0
    for until, c in rreo:
        ytd = sum(v for p, v in paid.items() if p.year == until.year and p <= until)
        verdict = rreo_verdict(until, ytd, int(c), whole[until.year])
        if verdict == "fail":
            r.fail({"rreo_until": str(until), "dtt_cents": ytd, "rreo_cents": int(c), "gap_cents": ytd - int(c)})
        elif verdict == "known_gap":
            known[str(until)] = ytd - int(c)
        else:
            worst_r = max(worst_r, abs(ytd - int(c)))
    r.detail["rreo_checkpoints"] = len(rreo)
    r.detail["rreo_whole_reais_years"] = sorted(y for y, w in whole.items() if w)
    r.detail["rreo_worst_gap_cents_outside_known"] = worst_r
    r.detail["rreo_known_gaps_cents"] = known
    if len(rreo) != RREO_CHECKPOINTS:
        r.fail({"rreo_checkpoints": len(rreo), "expected": RREO_CHECKPOINTS})
    return r


def g4_lines_conserved(con, flow):
    r = Result("G4 as partes de cada linha oficial somam a linha, ao centavo (estados, União e sem informação de estado dão o total)")
    sql = f"""WITH f AS (SELECT source_id, source_key, period, sum(amount_cents) AS s FROM {flow} GROUP BY ALL),
        i AS (SELECT source_id, source_key, period, sum(amount_cents) AS s FROM cur_internal GROUP BY ALL),
        l AS (SELECT source_id, line_key, period, value_cents * flow_sign AS v FROM cur_line WHERE kind IN ('leaf', 'derived'))
        SELECT l.source_id, l.line_key, l.period, l.v, f.s, i.s FROM l
        LEFT JOIN f ON f.source_id = l.source_id AND f.source_key = l.line_key AND f.period = l.period
        LEFT JOIN i ON i.source_id = l.source_id AND i.source_key = l.line_key AND i.period = l.period
        WHERE coalesce(f.s, 0) + coalesce(i.s, 0) <> coalesce(l.v, 0)"""
    for sid, key, p, v, fs, ins in _rows(con, sql):
        r.fail({"source_id": sid, "line": key, "period": str(p), "printed_cents": v, "flow_cents": fs, "internal_cents": ins})
    orphan = f"""SELECT f.source_id, f.source_key, f.period FROM {flow} f
        LEFT JOIN cur_line l ON l.source_id = f.source_id AND l.line_key = f.source_key AND l.period = f.period
             AND l.kind IN ('leaf', 'derived')
        WHERE l.line_key IS NULL"""
    for sid, key, p in _rows(con, orphan):
        r.fail({"flow_without_official_line": key, "source_id": sid, "period": str(p)})
    r.detail["lines_checked"] = _rows(con, "SELECT count(*) FROM cur_line WHERE kind IN ('leaf', 'derived')")[0][0]
    return r


def g5_union_matches_rtn_and_bcb(con, flow):
    r = Result("G5 o nó gov:uniao bate com o RTN e com o Banco Central, linha por linha")
    led, worst, checked = measures.RtnLedger(con, flow), defaultdict(int), 0
    for (code, p), (cents, _sign, kind) in sorted(led.pub.items(), key=lambda x: (x[0][1], x[0][0])):
        if kind == "adjustment" or cents is None or (kind == "memo" and code not in rtn_map.MEMO_CHECKS):
            continue
        if kind == "memo":
            parts = [led.line(c, p) for c in rtn_map.MEMO_CHECKS[code]]
            v, n = sum(x[0] for x in parts), sum(x[1] for x in parts)
        else:
            v, n = led.line(code, p)
        tolerance = 0 if kind in ("leaf", "derived") else (n + 1) // 2
        d = abs(v - cents)
        worst[kind] = max(worst[kind], d)
        checked += 1
        if d > tolerance:
            r.fail({"rtn_line": code, "period": str(p), "ledger_cents": v, "printed_cents": cents, "tolerance": tolerance})
    r.detail["rtn_lines_checked"] = checked
    r.detail["rtn_worst_cents_by_kind"] = dict(worst)
    if sorted(p for (k, p) in led.pub if k == "1") != sources.months():
        r.fail({"coverage": "RTN"})
    series = {(k, p): int(c) for k, p, c in _rows(con, "SELECT line_key, period, value_cents FROM cur_line WHERE kind = 'series'")}
    for code, (key, rtn_line, _name) in sources.SGS.items():
        months = sorted(p for (k, p) in series if k == key)
        if months != sources.months():
            r.fail({"coverage": key})
            continue
        w = 0
        for p in months:
            v, _ = led.line(rtn_line, p)
            d = abs(v + series[(key, p)])            # the SGS prints a need for financing: the RTN sign flipped
            w = max(w, d)
            if d > sources.SGS_UNIT_CENTS:
                r.fail({"sgs": code, "period": str(p), "ledger_cents": v, "sgs_cents": series[(key, p)]})
        r.detail[f"bcb_sgs_{code}_worst_cents"] = w
    return r


def g6_pairs_same_state(con, flow):
    r = Result("G6 todo par salário e imposto retido mora no mesmo estado")
    sql = f"""WITH p AS (
          SELECT f.pair_id, f.flow_type, coalesce(CASE WHEN a.is_government THEN b.uf ELSE a.uf END, 'BR') AS uf
          FROM {flow} f JOIN node a ON a.node_id = f.from_node JOIN node b ON b.node_id = f.to_node
          WHERE f.pair_id IS NOT NULL)
        SELECT pair_id, count(DISTINCT uf),
               count(*) FILTER (WHERE flow_type = 'public_payroll_gross'),
               count(*) FILTER (WHERE flow_type = 'public_payroll_withholding')
        FROM p GROUP BY pair_id
        HAVING count(DISTINCT uf) <> 1
            OR count(*) FILTER (WHERE flow_type = 'public_payroll_gross') = 0
            OR count(*) FILTER (WHERE flow_type = 'public_payroll_withholding') = 0"""
    for pid, n_uf, n_g, n_w in _rows(con, sql):
        r.fail({"pair_id": pid, "states": int(n_uf), "gross": int(n_g), "withheld": int(n_w)})
    for fid, key in _rows(con, f"SELECT flow_id, source_key FROM {flow} WHERE flow_type = 'public_payroll_withholding' "
                               f"AND pair_id IS NULL"):
        r.fail({"withholding_without_pair": key, "flow_id": fid})
    r.detail["pairs"] = _rows(con, f"SELECT count(DISTINCT pair_id) FROM {flow} WHERE pair_id IS NOT NULL")[0][0]
    return r


def g7_no_transfer_in_spending(con, flow):
    r = Result("G7 fluxo entre governos nunca entra numa medida de gasto")
    both = f"""SELECT f.flow_id, f.source_key, t.nature FROM {flow} f
        JOIN node a ON a.node_id = f.from_node JOIN node b ON b.node_id = f.to_node
        JOIN flow_type t ON t.flow_type_id = f.flow_type
        WHERE (a.is_government AND b.is_government) <> (t.nature = 'intergovernmental')"""
    for fid, key, nature in _rows(con, both):
        r.fail({"flow_id": fid, "source_key": key, "nature": nature,
                "why": "entre dois governos tem de ser repasse, e repasse só existe entre governos"})
    spend = f"""SELECT s.flow_id, s.source_key FROM ({measures.SPENDING_SQL.format(flow=flow)}) s
        JOIN flow_type t ON t.flow_type_id = s.flow_type JOIN node b ON b.node_id = s.to_node
        WHERE t.nature = 'intergovernmental' OR b.is_government"""
    for fid, key in _rows(con, spend):
        r.fail({"flow_id": fid, "source_key": key, "why": "repasse dentro da medida de gasto"})
    mixed = f"""SELECT s.dataset FROM {flow} f JOIN current_release s USING (source_id)
        WHERE f.flow_type = 'interest' GROUP BY 1 HAVING count(DISTINCT f.basis) > 1"""
    for (ds,) in _rows(con, mixed):
        r.fail({"dataset": ds, "why": "juros por competência e por caixa vindos da mesma fonte"})
    return r


ALL = (g1_unique_ids, g2_complete_rows, g3_release_totals, g4_lines_conserved, g5_union_matches_rtn_and_bcb,
       g6_pairs_same_state, g7_no_transfer_in_spending)


def run_all(con, flow):
    return [g(con, flow) for g in ALL]
```

- [ ] **Passo 5: rodar todos os testes.** `/usr/local/bin/python3 -m unittest discover -s data/scripts/ledger/tests -v`. Esperado: `Ran 29 tests ... OK`.

## Tarefa 10: os erros que têm de falhar

**Arquivo:** criar `planted.py`.

- [ ] **Passo 1: escrever os erros plantados.** Cada um mexe numa linha real do mês mais recente, numa cópia; a tabela de verdade não é tocada.

`data/scripts/ledger/planted.py`

```python
"""The four errors that must fail (spec 6, guarantee 8): each is planted in a copy of the candidate flows, every
guarantee runs on the copy, and the build stops if any planted error passes all of them."""
import sources

TARGETS = {  # planted error -> the RTN line it touches, in the latest month
    "duplicate_row": "1.1.05",   # Cofins
    "deleted_row": "2.1",        # FPM, FPE and IPI-EE
    "flipped_sign": "4.3.10",    # Fundeb, the União's complement
    "split_pair": "1.4.3",       # the servants' contribution, moved to another state than its salary
}
CONTROL_LINE = "1.1.03.3.1"     # build.py --control flips this one (IRRF on wages), apart from the planted targets


def plant(con, kind, src, dst, line=None):
    line = line or TARGETS[kind]
    con.execute(f"CREATE OR REPLACE TEMP TABLE {dst} AS SELECT * FROM {src}")
    row = con.execute(f"""SELECT f.flow_id, f.period, f.amount_cents FROM {dst} f JOIN current_release r USING (source_id)
        WHERE r.dataset = ? AND f.source_key = ? ORDER BY f.period DESC LIMIT 1""",
                      [sources.RTN["dataset"], line]).fetchone()
    if row is None:
        raise SystemExit(f"planted error {kind}: line {line} has no flow")
    fid = row[0]
    if kind == "duplicate_row":
        con.execute(f"INSERT INTO {dst} SELECT * FROM {dst} WHERE flow_id = ?", [fid])
    elif kind == "deleted_row":
        con.execute(f"DELETE FROM {dst} WHERE flow_id = ?", [fid])
    elif kind == "flipped_sign":
        con.execute(f"UPDATE {dst} SET amount_cents = -amount_cents WHERE flow_id = ?", [fid])
    elif kind == "split_pair":
        con.execute(f"UPDATE {dst} SET from_node = 'soc:uf:DF' WHERE flow_id = ?", [fid])
    return {"line": line, "period": str(row[1]), "amount_cents": int(row[2])}


def run(con, check, src="cand_flow"):
    out = {}
    for kind in TARGETS:
        target = plant(con, kind, src, "planted")
        out[kind] = {"target": target, "caught_by": [r.name for r in check(con, "planted") if not r.ok]}
    con.execute("DROP TABLE IF EXISTS planted")
    return out
```

## Tarefa 11: a construção

**Arquivo:** criar `build.py`.

- [ ] **Passo 1: escrever a construção.**

`data/scripts/ledger/build.py`

```python
"""Build the money-flow ledger, phase 1: load every source, check the guarantees, prove the planted errors fail, and
only then publish the flows. When any step fails, nothing is published and `flow` keeps the last good build.

Usage: /usr/local/bin/python3 data/scripts/ledger/build.py [--skip-load] [--control]
  --skip-load  use the releases already in the warehouse (no download)
  --control    flip the sign of one real flow before the checks: the build must stop and leave `flow` as it was
Writes data/ledger/build-report.json and one row in build_run."""
import json
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime

import duckdb

import db
import guarantees
import load_dtt_interest
import load_rreo_union
import load_rtn
import load_sgs
import measures
import planted
import sources

REPORT = db.ROOT / "data" / "ledger" / "build-report.json"
UNION_JSON = db.ROOT / "data" / "series" / "union.json"


def by_year(monthly):
    out = defaultdict(lambda: defaultdict(int))
    for p, row in monthly.items():
        label = str(p.year) if p.year < sources.LAST.year else f"{p.year} (jan a {sources.LAST:%m})"
        for k, v in row.items():
            out[label][k] += v
    return {y: dict(v) for y, v in out.items()}


def union_json_gap(monthly):
    """Largest gap, in cents, between the ledger and today's data/series/union.json (report only, not a guarantee)."""
    u = json.loads(UNION_JSON.read_text(encoding="utf-8"))
    pos = {m: i for i, m in enumerate(u["months"])}
    gap = {}
    for name, _code in measures.LINES:
        values = [(row[name], u[name][pos[f"{p:%Y-%m}"]]) for p, row in monthly.items() if f"{p:%Y-%m}" in pos]
        gap[name] = max(abs(a - round(b * 100)) for a, b in values if b is not None)
    return gap


def unassigned(con, table):
    nodes = "('soc:unknown', 'soc:br', 'gov:sub:br')"
    rows = con.execute(f"""SELECT year(period) AS y, CASE WHEN from_node IN {nodes} THEN from_node
        ELSE to_node END AS node, sum(amount_cents) FROM {table}
        WHERE from_node IN {nodes} OR to_node IN {nodes} GROUP BY ALL ORDER BY ALL""").fetchall()
    out = defaultdict(dict)
    for y, node, s in rows:
        out[node][str(y)] = int(s)
    return dict(out)


def main(argv):
    t0, started = time.time(), datetime.now().replace(microsecond=0)
    con = db.connect()
    before = db.fingerprint(con)
    loads = {}
    if "--skip-load" not in argv:
        loads = {"rtn": load_rtn.run(con), "sgs": load_sgs.run(con), "dtt": load_dtt_interest.run(con),
                 "rreo": load_rreo_union.run(con)}
    con.execute("CREATE OR REPLACE TEMP TABLE cand_flow AS SELECT f.* FROM flow_stage f JOIN current_release r USING (source_id)")
    control = None
    if "--control" in argv:
        control = planted.plant(con, "flipped_sign", "cand_flow", "control_flow", line=planted.CONTROL_LINE)
        con.execute("CREATE OR REPLACE TEMP TABLE cand_flow AS SELECT * FROM control_flow")
    results = guarantees.run_all(con, "cand_flow")
    plants = planted.run(con, guarantees.run_all)
    ok = all(r.ok for r in results) and all(p["caught_by"] for p in plants.values())
    if ok:
        con.begin()
        try:
            con.execute("DROP TABLE flow")
            con.execute(db.FLOW_DDL)
            con.execute("INSERT INTO flow SELECT * FROM cand_flow ORDER BY period, flow_id")
            con.commit()
        except (duckdb.Error, SystemExit):
            con.rollback()
            ok = False
    table = "flow" if ok else "cand_flow"
    monthly = measures.union_account(con, table)
    report = {
        "status": "published" if ok else "stopped",
        "started_at": started.isoformat(), "seconds": round(time.time() - t0, 1), "duckdb": duckdb.__version__,
        "period": [str(sources.FIRST), str(sources.LAST)],
        "loads": loads, "control": control,
        "releases": [dict(zip(("dataset", "source_id", "sha256", "bytes", "published_on", "published_note"), r)) for r in
                     con.execute("SELECT dataset, source_id, sha256, bytes, published_on, published_note "
                                 "FROM current_release ORDER BY dataset").fetchall()],
        "guarantees": [{"name": r.name, "ok": r.ok, "failures": r.failures, "sample": r.sample, "detail": r.detail}
                       for r in results],
        "planted_errors": plants,
        "flows_by_type": dict(con.execute(f"SELECT flow_type, count(*) FROM {table} GROUP BY 1 ORDER BY 1").fetchall()),
        "flow_before": before, "flow_after": db.fingerprint(con),
        "union_account_by_year_cents": by_year(monthly),
        "unassigned_by_year_cents": unassigned(con, table),
        "gap_to_union_json_cents": union_json_gap(monthly),
    }
    con.execute("INSERT INTO build_run VALUES (?, ?, ?, ?, ?, ?)",
                [uuid.uuid4().hex, started, datetime.now().replace(microsecond=0), report["status"],
                 report["flow_after"]["rows"], json.dumps(report, default=str)])
    con.execute("CHECKPOINT")
    con.close()
    report["db_bytes"] = db.DB_PATH.stat().st_size
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    for r in results:
        print(("ok    " if r.ok else "FAIL  ") + r.name, "" if r.ok else r.sample[:2])
    for kind, p in plants.items():
        print(("caught" if p["caught_by"] else "MISSED"), kind, p["target"], "by", [n.split(" ")[0] for n in p["caught_by"]])
    print(report["status"], "| flows", report["flow_after"]["rows"], "| db", report["db_bytes"], "bytes |",
          report["seconds"], "s | report", REPORT.relative_to(db.ROOT))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Passo 2: construir com o que já foi carregado.** `/usr/local/bin/python3 data/scripts/ledger/build.py --skip-load`. Esperado: sete linhas `ok`, quatro linhas `caught`, e `published | flows <8.281 mais os juros pagos> | db <tamanho> bytes`. Os erros plantados têm de ser pegos assim: linha duplicada por G1, G3, G4 e G5; linha apagada por G3, G4 e G5; sinal trocado por G3, G4 e G5; par separado por G6.
- [ ] **Passo 3: provar que a construção para.** `/usr/local/bin/python3 data/scripts/ledger/build.py --skip-load --control; echo "exit $?"`. Esperado: linhas `FAIL`, os quatro erros plantados ainda pegos, `stopped` e `exit 1`; no relatório, `flow_before` igual a `flow_after` (a tabela publicada não mudou). O controle troca o sinal de uma linha fora dos alvos plantados (1.1.03.3.1, IRRF do trabalho).
- [ ] **Passo 4: a construção completa, buscando tudo de novo.** `/usr/local/bin/python3 data/scripts/ledger/build.py; echo "exit $?"`. Esperado: toda carga com `'new': False` (as mesmas divulgações), `published`, `exit 0`, e a impressão digital da tabela `flow` igual à do passo 2.
- [ ] **Passo 5: tempo e tamanho** (spec, seção 7). Anotar do relatório os segundos da construção completa e os bytes do armazém.

## Tarefa 12: relatório ao autor e registros

- [ ] **Passo 1: escrever o relatório** em `docs/research/BRASIL-IMPOSTO_BUILD_ledger-phase-1_2026-10-08.md` (português, com resumo em inglês), a partir de `data/ledger/build-report.json`: divulgações com SHA-256, garantias, erros plantados, a conta da União por ano pelo livro (receita, repasses, despesa, primário, juros pelos dois critérios, nominal), o que ficou em `soc:br` e em `gov:sub:br`, a distância para o `union.json` de hoje, tempo e tamanho, e os limites desta fase.
- [ ] **Passo 2: renderizar e conferir.** `python3 docs/superpowers/tools/render-doc.py docs/research/BRASIL-IMPOSTO_BUILD_ledger-phase-1_2026-10-08.md docs/superpowers/previews/BRASIL-IMPOSTO_BUILD_ledger-phase-1_2026-10-08.html --kind relatório`; olhar a página antes de entregar.
- [ ] **Passo 3: travessões.** Conferir que nenhum texto novo tem travessão, com uma linha de controle que precisa acusar.
- [ ] **Passo 4: registros.** Comandos do livro na seção "Comandos" do `CLAUDE.md`; estado no acompanhamento da rodada 11; nenhum processo deixado rodando.

## Autoconferência contra a spec

| Spec | Onde está no plano |
|---|---|
| 4.1 nós | Tarefa 2 (`reference.py`), mais `gov:sub:br` (decisão 2) e `soc:unknown` (D127) |
| 4.2 fluxo em centavos inteiros, `flow_id` pelo hash | Tarefas 1, 2 e 5 (`flow_id` = SHA-256 de conjunto, chave, mês, origem, destino e tipo; o conjunto no lugar da divulgação, para que uma divulgação nova substitua a anterior pela chave natural) |
| 4.3 tipos de fluxo | Tarefa 2 (os 12 tipos da spec e 5 da fase 1) e seção 4 |
| 4.4 método de localização e regras com evidência e versão | Tarefa 2 (`allocation_rule`) e garantia 2 |
| 4.5 fontes, SHA-256, idempotência, nada bruto guardado | Tarefa 3 e Tarefa 11, passo 4 |
| 5 cada número é uma consulta | Tarefa 9 (`measures.py`: a conta da União) |
| 6.1 a 6.7 | Tarefa 9 (`guarantees.py`, G1 a G7) |
| 6.8 erros que têm de falhar | Tarefa 10 e Tarefa 11, passos 2 e 3 |
| 7 DuckDB, tempo e tamanho | Tarefas 0 e 11, passo 5 |
| 9 fase 1: gov:uniao de jan/2019 a ago/2026, RTN linha por linha e Banco Central | Tarefas 5, 6 e 9 (G5) |
| D121 juros pelos dois critérios | Tarefas 5, 7 e 8 (decisão 4) |

Fora desta fase, como a spec manda: arrecadação por estado (fase 2), o que a União paga a cada estado (fase 3), estados e municípios (fase 4), as telas lidas do livro (fase 5), o calendário e a tarefa agendada (fase 6).
