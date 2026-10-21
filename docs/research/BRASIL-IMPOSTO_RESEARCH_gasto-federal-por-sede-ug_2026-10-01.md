# Gasto federal pela sede da unidade gestora que paga (2024)

**Data da coleta:** 2026-10-01. **Scripts:** `data/scripts/ug/`. **Dados baixados e agregados:** `data/ug/`.
**Pergunta:** se o gasto da União passar a contar na UF da unidade gestora (UG) que paga, a mesma regra que a Receita usa para o imposto (sede de quem recolhe), qual fica o saldo das 27 UFs em 2024, e onde fica o DF?
**Regra seguida:** só fonte oficial, com link; o que é conta feita aqui está marcado como cálculo; o que não deu para abrir está em "Não consegui confirmar". Nada aqui é decisão: é o resultado da regra em teste, com as distorções que ela cria.

## 0. Resposta curta

- **Fonte do local:** cadastro de unidades gestoras do SIAFI publicado pelo Tesouro Nacional (coluna UF, "onde a Unidade Gestora está localizada"). Toda UG que pagou em 2024 está no cadastro; só um código inválido (-3) do próprio arquivo do Portal, R$ 0,41 bi, fica sem UF.
- **DF:** com o gasto federal contado na UF da UG que paga, o DF passa de **+R$ 2.918** por pessoa por mês (o que mais envia) para **−R$ 6.836** (o que mais recebe, quase seis vezes o segundo, AP com −R$ 1.151). O DF fica com 63,9% de todo o gasto federal que a regra localiza.
- **As outras UFs** quase não mudam (de −R$ 11 a −R$ 188 por pessoa por mês), exceto o RJ (de R$ 1.343 para R$ 971), onde a Marinha e a Aeronáutica pagam os militares.
- **Sem UF depois da regra:** R$ 61,99 bi de R$ 669,59 bi (9,3%): sentenças judiciais pagas pelos tribunais (41,28) e unidades nacionais dos outros Poderes (19,82), cuja UG pagadora não está em arquivo aberto.
- **Checagem:** soma das UFs mais sem UF bate ao centavo com o recorte de cada base, e a ponte até o total publicado do Tesouro deixa um resíduo de R$ 0,47 bi (0,08%); tirar R$ 1 bi de SP faz a checagem falhar.
- **Distorções:** a regra põe na sede da unidade que paga a folha militar (Brasília e Rio), os aposentados de órgãos extintos, o seguro-desemprego e o abono do país inteiro (R$ 80,64 bi numa UG de Brasília), as compras centralizadas da Saúde, obras do DNIT e até gasto no exterior. Mesmo tirando benefícios, subvenções, encargos e a folha militar, o DF continua o que mais recebe (−R$ 1.968).

## 1. Onde fica cada UG: a fonte

- **Tesouro Nacional, "Unidades Gestoras cadastradas no SIAFI"** (Tesouro Transparente, conjunto `siafi-relatorio-unidades-gestoras`): https://www.tesourotransparente.gov.br/ckan/dataset/siafi-relatorio-unidades-gestoras , arquivo CSV https://www.tesourotransparente.gov.br/ckan/dataset/54a699f4-55e3-41cc-a900-27c123545472/resource/7b83145e-6dc5-4ad2-9730-77132188eb2f/download/siafirelatoriounidadesgestoras.csv (versão de 2025-06-01, 14,9 MB, salvo em `data/ug/siafi_unidades_gestoras_2025-06.csv`).
- Metadados do Tesouro (`private/archive/data/ug/metadados_ug.pdf`, mesmo conjunto): a coluna UF "corresponde a Unidade Federativa onde a Unidade Gestora está localizada"; a lista é a da transação CONUG do SIAFI, com UGs ativas e inativas; série mensal desde nov/2015.
- Conteúdo: 49.363 UGs, cada uma com código, título, UF, órgão, função (executora, credora, controle), situação (ativa ou não), CEP e endereço. 67 UGs têm UF "EX" (exterior). 184 linhas têm aspas quebradas no endereço; os 10 primeiros campos (até o CEP) leem certo, e o script usa só eles.
- Por que esta fonte e não a tabela UASG do compras.gov.br (que a pesquisa da folha testou): o cadastro do Tesouro é o do próprio SIAFI, o sistema que registra o pagamento, e tem toda UG que paga, inclusive as que não fazem compras. As candidatas restantes não foram necessárias: a API de órgãos SIAFI do Portal da Transparência pede chave de acesso.
- Limite: o cadastro é uma foto de junho de 2025, e a UF é a da sede atual da UG. Para medir o efeito, a versão anterior publicada no mesmo conjunto (2020-01, https://www.tesourotransparente.gov.br/ckan/dataset/54a699f4-55e3-41cc-a900-27c123545472/resource/49a9331b-43f3-4a70-a85f-b473c34c208f/download/siafirelatoriounidadesgestoras.csv , salva em `private/archive/data/ug/siafi_unidades_gestoras_2020-01.csv`) foi comparada: do gasto do Executivo no recorte (R$ 548,54 bi), R$ 523,33 bi foram pagos por UGs com a mesma UF em 2020 e 2025, R$ 1,10 bi por UGs que mudaram de UF (a maior, UG 275068, R$ 0,98 bi, do RJ em 2020 para o DF em 2025) e R$ 24,10 bi por UGs criadas depois de 2020. A UF de 2024 não está publicada; a mudança entre as duas fotos é pequena.

## 2. Método

### 2.1 Arquivos de despesa

| Fonte | O que dá | Uso aqui |
|---|---|---|
| Portal da Transparência (CGU), Execução da Despesa, 12 arquivos mensais de 2024: https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/202401 (até 202412) | Pagamentos do **Poder Executivo**, linha a linha, com o código da UG, a unidade orçamentária, a ação, o grupo, a modalidade, o elemento e a UF do localizador | Executivo pela UF da UG |
| Tesouro Nacional, "Despesas e Transferências Totais da União", 2024 (critério valor pago): https://www.tesourotransparente.gov.br/ckan/dataset/despesas-e-transferencias-totais , arquivo `limite-gastos-lc200dez24.xlsx` | Todos os Poderes, por órgão, unidade orçamentária, grupo, modalidade e ação. **Não tem UG nem UF** | Legislativo, Judiciário, MPU e DPU pela sede da unidade; total do Executivo no mesmo recorte para a checagem |
| Cadastro de UGs do SIAFI (seção 1) | UF de cada UG | Local |

Os agregados guardados (`data/ug/cache/`) já foram feitos de novo nesta coleta, porque os de `data/df/cache/` não guardavam o código da UG e os de `data/scripts/series/cache/payroll/` só guardavam o grupo 1 (pessoal). Os ZIPs foram baixados um a cada 90 s e apagados depois de somados. Scripts: `data/scripts/ug/agg_desp_ug.py` (Portal), `data/scripts/ug/agg_dtt_full.py` (Tesouro), `private/archive/data/scripts/ug/build_ug_balance.py` (contas). Saída: `private/archive/data/ug/ug-balance-2024.json`.

### 2.2 Recorte (o que entra no "voltou" pela regra)

Valor pago no ano mais restos a pagar pagos (o critério "valor pago" do RTN e da pesquisa da folha).

| Entra | Fica fora, e por quê |
|---|---|
| Grupo 1 (pessoal: ativos, aposentados, pensionistas, civis e militares), grupo 3 (outras despesas correntes: custeio, benefícios, subsídios) e grupo 4 (investimentos), **modalidade 90** (aplicação direta) | Grupos 2 e 6 (juros e amortização da dívida): financeiros, não são gasto num estado |
| | Grupo 5 (inversões financeiras: financiamentos do FAT ao BNDES, fundos constitucionais FNE, FNO e FCO, FIES, cotas do FAR): é empréstimo ou compra de ativo, não gasto; mostrado à parte (seção 3) |
| | Modalidade 91 (a União pagando a ela mesma dentro do orçamento, como a contribuição patronal): não chega a ninguém, e a pesquisa da folha também a deixou fora |
| | Modalidades 30 a 80 (transferências a estados, municípios, consórcios, entidades privadas e exterior): as transferências a governos já estão no saldo pelo destino (Portal, repasses) |
| | Unidade 33904, Fundo do Regime Geral de Previdência Social (INSS): já no saldo pelo destino (BEPS) |
| | Ação 8442 da unidade 55101 (Bolsa Família): já no saldo pelo destino (MDS) |
| | Ações 00IN e 00H5 da unidade 55901, FNAS (BPC; a 00H5 também paga a Renda Mensal Vitalícia por idade): já no saldo pelo destino (MDS) |
| | Unidade 73901 (FCDF): já no saldo do DF inteiro (D41) |

A folha localizada de D41 (`federal-payroll-by-uf.json`) **sai** do "voltou" e é substituída pelo gasto pela UG, que já contém a folha do Executivo e a dos outros Poderes. Nada é contado duas vezes: o recorte acima é o único lugar onde pessoal, custeio e investimento entram.

### 2.3 Regras de local

| Parte | Regra |
|---|---|
| Poder Executivo | UF da UG que paga, pelo cadastro do SIAFI. UG com UF "EX", fora do cadastro ou inválida (código -3 no próprio arquivo do Portal) fica sem UF |
| Legislativo, Judiciário, MPU, DPU | A base do Tesouro não tem UG; o órgão pagador é a unidade orçamentária. Unidade com sede numa UF: na UF da sede (Câmara, Senado, TCU, STF, STJ, TSE, TST, CSJT, CNJ, TJDFT, MPDFT e ESMPU no DF; cada TRE na sua UF; cada TRF na UF da sede; **cada TRT na UF da sede, inclusive os de duas UFs**: 8ª em Belém, 10ª em Brasília, 11ª em Manaus, 14ª em Porto Velho). Unidade única com UGs em todo o país (Justiça Federal de primeiro grau, Justiça Militar da União, MPF, MPT, MPM, DPU): sem UF, porque a UG que paga não está na base; a conta "tudo na sede, em Brasília" está na seção 6 |

Para mostrar as distorções, o gasto do Executivo no recorte é separado em subcategorias (campo `executivo_pela_ug`): pessoal civil ativo e outros; aposentadorias e pensões civis (elementos 01 e 03); pessoal militar (as mesmas ações da pesquisa da folha: 2867, 214H, 0179, 218J, 218K, 00QD); encargos especiais (função 28: sentenças, Proagro, garantias, subsídios lançados nessa função); subvenções econômicas fora da função 28 (elemento 45, como as do Plano Safra e do Pronaf); benefícios a pessoas que não são servidores (elementos 06, 10, 18, 20, 48 e 59, e as ações 00H4 seguro-desemprego e 0581 abono salarial); custeio; investimento.

## 3. O que cada bloco soma em 2024 (R$ bi, cálculo)

| Bloco | R$ bi |
|---|---:|
| **Executivo no recorte (Portal)** | **548,54** |
| dos quais pessoal (grupo 1) / custeio e benefícios (grupo 3) / investimento (grupo 4) | 278,68 / 236,98 / 32,88 |
| **Outros Poderes no recorte (Tesouro)** | **79,29** |
| Fora: juros e amortização da dívida (grupos 2 e 6) | 2.010,70 |
| Fora: inversões financeiras (grupo 5) | 135,39 |
| Fora: transferências e outras modalidades (30 a 80) | 763,79 |
| Fora: modalidade 91 (intraorçamentária) | 21,96 |
| Fora, já no saldo pelo destino: INSS (FRGPS) / Bolsa Família / BPC / FCDF (parte de aplicação direta) | 913,56 / 168,20 / 105,75 / 22,65 |
| Fora: outros Poderes fora do recorte (modalidade 91 e transferências) | 8,46 |

Conferência do download: o gasto direto primário do Executivo (grupos 1, 3, 4 e 5, modalidades 90 e 91) soma R$ 1.916,04 bi, e a parte com UF no localizador R$ 192,16 bi, iguais aos da pesquisa do DF de hoje (seção 2.2 dela). Os arquivos baixados de novo são os mesmos.

## 4. Resultado: o saldo de 2024 com a regra

**Fórmula (cálculo).** Saldo = arrecadação federal registrada na UF − ("voltou"), com:
- D41 (atual): "voltou" = transferências + Bolsa Família + INSS + BPC + FCDF (só DF) + folha localizada (`federal-payroll-by-uf.json`).
- Regra pela UG: "voltou" = transferências + Bolsa Família + INSS + BPC + FCDF (só DF) + gasto federal pela UG (Executivo no recorte pela UF da UG + outros Poderes pela sede).

O saldo D41 reproduz o do projeto: DF R$ 104,44 bi, R$ 2.918 por pessoa por mês (população IBGE 2024 de `population.json`). A coluna "mesmo recorte pelo localizador" usa o mesmo pessoal, custeio e investimento, mas o Executivo pela UF do localizador (a regra de hoje): ela separa o efeito de ampliar o recorte do efeito de trocar a regra.

Ordem: da UF que mais envia para a que mais recebe com a regra; entre parênteses, a posição em D41.

| # (antes) | UF | Saldo D41 (R$/pessoa/mês) | Saldo pela UG (R$/pessoa/mês) | Diferença | Mesmo recorte pelo localizador (R$/pessoa/mês) | Gasto federal pela UG (R$ bi) | Folha localizada D41 (R$ bi) | Saldo D41 (R$ bi) | Saldo pela UG (R$ bi) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 (3) | SP | 1.270 | 1.259 | -11 | 1.266 | 15,15 | 9,21 | 700,48 | 694,54 |
| 2 (2) | RJ | 1.343 | 971 | -372 | 1.320 | 91,67 | 14,76 | 277,56 | 200,65 |
| 3 (4) | SC | 781 | 762 | -19 | 768 | 5,38 | 3,56 | 75,53 | 73,72 |
| 4 (5) | ES | 282 | 263 | -19 | 267 | 2,94 | 2,03 | 13,87 | 12,96 |
| 5 (6) | PR | 198 | 184 | -14 | 189 | 6,39 | 4,43 | 28,08 | 26,13 |
| 6 (7) | RS | 21 | -14 | -35 | -54 | 16,00 | 11,28 | 2,79 | -1,93 |
| 7 (8) | MG | -32 | -51 | -19 | -45 | 16,63 | 11,71 | -8,06 | -12,98 |
| 8 (9) | MT | -34 | -56 | -21 | -46 | 2,69 | 1,71 | -1,58 | -2,56 |
| 9 (10) | GO | -74 | -88 | -14 | -83 | 4,03 | 2,80 | -6,49 | -7,73 |
| 10 (12) | MS | -155 | -191 | -36 | -182 | 2,85 | 1,58 | -5,40 | -6,67 |
| 11 (11) | AM | -152 | -194 | -42 | -172 | 3,31 | 1,17 | -7,81 | -9,95 |
| 12 (14) | PE | -394 | -422 | -28 | -405 | 7,62 | 4,40 | -45,08 | -48,30 |
| 13 (15) | CE | -453 | -476 | -24 | -461 | 5,56 | 2,96 | -50,14 | -52,75 |
| 14 (13) | RO | -384 | -489 | -105 | -421 | 2,73 | 0,53 | -8,05 | -10,25 |
| 15 (16) | PA | -469 | -494 | -26 | -486 | 5,08 | 2,43 | -48,74 | -51,40 |
| 16 (17) | BA | -488 | -503 | -15 | -500 | 7,00 | 4,38 | -86,99 | -89,61 |
| 17 (18) | RN | -635 | -668 | -33 | -657 | 4,21 | 2,84 | -26,27 | -27,64 |
| 18 (19) | SE | -668 | -690 | -23 | -685 | 1,85 | 1,23 | -18,36 | -18,98 |
| 19 (20) | PB | -678 | -701 | -23 | -696 | 4,73 | 3,59 | -33,72 | -34,86 |
| 20 (22) | MA | -690 | -704 | -14 | -699 | 2,98 | 1,78 | -58,05 | -59,25 |
| 21 (21) | AL | -685 | -704 | -19 | -699 | 2,34 | 1,59 | -26,47 | -27,22 |
| 22 (23) | TO | -727 | -747 | -20 | -744 | 0,99 | 0,61 | -13,76 | -14,13 |
| 23 (24) | PI | -796 | -820 | -25 | -810 | 2,43 | 1,42 | -32,23 | -33,23 |
| 24 (27) | AC | -1.037 | -1.069 | -33 | -1.055 | 0,80 | 0,46 | -10,95 | -11,30 |
| 25 (25) | RR | -941 | -1.130 | -188 | -962 | 1,99 | 0,37 | -8,10 | -9,72 |
| 26 (26) | AP | -967 | -1.151 | -184 | -992 | 2,07 | 0,30 | -9,32 | -11,09 |
| 27 (1) | **DF** | **2.918** | **-6.836** | **-9.754** | 2.625 | **388,18** | 39,04 | 104,44 | **-244,69** |

(Positivo = a UF envia mais do que recebe, verde no mapa; negativo = recebe mais, vermelho.)

### 4.1 Onde fica o DF

- **O DF passa de 1º (o que mais envia, R$ 2.918 por pessoa por mês) a 27º, o que mais recebe: R$ 6.836 por pessoa por mês**, quase seis vezes o segundo que mais recebe (AP, R$ 1.151). Em reais, de +R$ 104,44 bi para −R$ 244,69 bi.
- A mudança vem toda da regra, não do recorte maior: com o mesmo pessoal, custeio e investimento pela UF do localizador, o DF continuaria o mais verde (R$ 2.625).
- O "voltou" do DF passa de R$ 79,65 bi para R$ 428,79 bi: transferências 3,78; Bolsa Família 1,51; INSS 10,48; BPC 1,24; FCDF 23,61; **gasto federal pela UG 388,18** (Executivo 360,96; Legislativo 13,86; Judiciário 12,23; MPU 1,12).
- Executivo pago por UGs do DF, por subcategoria (R$ bi): benefícios a pessoas 101,07; custeio 55,59; aposentadorias e pensões civis 54,75; pessoal civil ativo 52,56; pessoal militar 46,81; investimento 23,80; subvenções econômicas 15,30; encargos especiais 11,08.
- O DF fica com **63,9% de todo o gasto federal que a regra localiza** (R$ 388,18 de 607,60 bi), com 1,40% da população: R$ 130.138 por morador por ano, contra R$ 1.047 no resto do país.
- O RJ é o outro grande afetado: de R$ 1.343 para R$ 971 por pessoa por mês, porque a Marinha e a Aeronáutica pagam os militares por UGs no Rio (seção 6). Nas outras UFs a diferença fica entre −R$ 11 e −R$ 188 por pessoa por mês e a ordem quase não muda.

### 4.2 Sensibilidade (contas, não decisões)

Tirando do "voltou" (e deixando sem UF) as partes que a regra mais distorce, seção 6:

| UF | Regra | Sem benefícios a pessoas, encargos especiais e subvenções | E também sem a folha militar |
|---|---:|---:|---:|
| DF | -6.836 | -3.276 | -1.968 |
| RJ | 971 | 979 | 1.191 |
| SP | 1.259 | 1.259 | 1.259 |
| SC | 762 | 764 | 764 |
| RS | -14 | -12 | -12 |

O DF continua o 27º (o que mais recebe) nas três colunas. Pondo as unidades nacionais dos outros Poderes na sede, em Brasília (seção 6, item 9), o DF iria a −R$ 7.390.

## 5. Quanto fica sem UF depois da regra, e a checagem

### 5.1 Sem UF

| | R$ bi | % do recorte nacional |
|---|---:|---:|
| Recorte nacional publicado (Tesouro: Executivo 590,30 + outros Poderes 79,29) | 669,59 | 100% |
| Com UF pela regra (27 UFs) | 607,60 | 90,7% |
| **Sem UF** | **61,99** | **9,3%** |
| dos quais sentenças judiciais (precatórios e RPV) do Executivo, pagas pelos tribunais e ausentes do arquivo do Portal (grupo 1: 2,87; grupo 3: 38,41) | 41,28 | 6,2% |
| dos quais unidades nacionais dos outros Poderes (Justiça Federal de primeiro grau 8,74 só de pessoal, MPF, MPT, MPM, DPU, Justiça Militar) | 19,82 | 3,0% |
| dos quais UG inválida (código -3) no próprio arquivo do Portal | 0,41 | 0,1% |
| dos quais diferença residual Portal contra Tesouro | 0,47 | 0,1% |

Para comparar: pela UF do localizador, 90,0% do gasto direto primário do Executivo fica sem UF; pela UF da UG, só R$ 0,47 bi de R$ 1.916,04 bi (UG inválida). Na folha, D41 deixa R$ 208,20 bi sem UF; pela UG, a folha do Executivo inteira tem UF (os R$ 92,13 bi de militares incluídos, seção 6).

Achado lateral: os R$ 2,92 bi que a pesquisa da folha registrou como "Executivo um pouco menor no Portal do que na base do Tesouro" são, quase todos (R$ 2,87 bi), sentenças judiciais de pessoal que o arquivo do Portal não traz.

### 5.2 Checagem (cálculo, `build_ug_balance.py` e `bridge_portal_tesouro.py`)

| Conta | R$ |
|---|---:|
| Executivo: soma das 27 UFs pela UG | 548.126.359.410,68 |
| mais UG inválida (sem UF) | 411.200.710,16 |
| = recorte do Executivo no Portal | 548.537.560.120,84 |
| **Diferença** | **0,00** |
| Outros Poderes: soma das 27 UFs pela sede | 59.476.447.404,40 |
| mais unidades nacionais (sem UF) | 19.818.322.239,20 |
| = recorte dos outros Poderes no Tesouro | 79.294.769.643,60 |
| **Diferença** | **0,00** |

Ponte até o total publicado do Executivo no mesmo recorte (base do Tesouro, a mesma por trás do RTN; a pesquisa da folha mostrou que as categorias de pessoal dela batem com a tabela 1.5 do RTN):

| Grupo | Sentenças judiciais? | Tesouro (R$ bi) | Portal (R$ bi) | Tesouro menos Portal |
|---|---|---:|---:|---:|
| 1 | não | 278,69 | 278,64 | 0,05 |
| 1 | sim | 2,91 | 0,04 | 2,87 |
| 3 | não | 237,39 | 236,98 | 0,41 |
| 3 | sim | 38,41 | 0,00 | 38,41 |
| 4 | não | 32,89 | 32,88 | 0,01 |
| **Total** | | **590,30** | **548,54** | **41,76** |

Fecha assim: 669,59 (publicado) = 607,60 (27 UFs) + 41,28 (sentenças) + 19,82 (unidades nacionais) + 0,41 (UG inválida) + 0,47 (resíduo, 0,08% do recorte).

**Erro de controle:** `python3 private/archive/data/scripts/ug/build_ug_balance.py --control` tira R$ 1 bi do custeio de SP depois da montagem. Resultado: soma das 27 UFs do Executivo 547.126.359.410,68, **diferença 1.000.000.000,00, "passou": false, "CHECAGEM FALHOU", código de saída 1**; o arquivo salvo não é tocado (`control_run: false` no JSON). A checagem pega o erro.

## 6. Distorções da regra (com o tamanho, quando o dado permite)

A regra é simétrica com a Receita (sede de quem paga dos dois lados), mas a sede de quem paga não é onde o dinheiro chega. As distorções abaixo são do próprio dado de 2024; nenhuma foi corrigida no resultado da seção 4.

| # | Distorção | Tamanho em 2024 (R$ bi, cálculo) | Para onde a regra leva |
|---:|---|---:|---|
| 1 | **Folha militar paga por centros de pagamento.** Centro de Pagamento do Exército (UG 160063, Brasília) 45,81; Pagadoria de Pessoal da Marinha (773200, Rio) 23,99; Subdiretoria de Pagamento de Pessoal da Aeronáutica (120052, Rio) 19,66. O microdado de militares do Portal traz UF_EXERCICIO = -1 em todos os registros, então não há dado aberto de onde os militares estão | 92,13 no total (o mesmo total da pesquisa da folha): DF 46,81; RJ 43,95; RO 0,73, AP 0,35 e RR 0,21 (sobretudo inativos e pensões militares pagos por UGs nesses estados, incluídos os dos ex-territórios) | DF e RJ |
| 2 | **Aposentadorias e pensões civis pagas por unidades centrais.** A maior é a Diretoria de Centralização de Serviços de Inativos, Pensionistas e Órgãos Extintos (170597, Brasília), 20,10, que paga inativos de órgãos extintos e ex-territórios; depois Ministério da Saúde (250006) 9,13, RPPU (512016) 5,77, Fazenda (200334 e 200230) 4,71 | DF 54,75 dos 80,41 do país (68,1%); pelo localizador, o DF tinha 13,18 | DF |
| 3 | **Folhas de ativos centralizadas.** Folha de pagamento da Fazenda (200281) 6,80; EBSERH, sede (155007), 6,12, que paga pessoal de hospitais universitários de vários estados; Ministério da Saúde 4,03; Embrapa, sede, 2,93 | DF 52,56 dos 106,15 do país (49,5%); pelo localizador, 6,74 | DF |
| 4 | **Benefícios pagos a pessoas no país inteiro por uma UG em Brasília** (não estão no saldo pelo destino). Seguro-desemprego 52,35 e abono salarial 28,29 (UG 380916, FAT); Auxílio Gás 3,43; provisão de profissionais da atenção primária 3,43; bolsas da CAPES 3,28; apoio às famílias desalojadas pelas enchentes (ação 00WD, quase todo no RS) 2,28; educação e trabalho na saúde 1,38 | DF 101,07 dos 103,66 do país (97,5%) | DF |
| 5 | **Subvenções e encargos especiais.** Subvenções do Pronaf, do investimento rural e do alongamento de dívidas rurais pela UG 170700 (Brasília); Farmácia Popular 3,55; Proagro 5,44 | DF 26,38 dos 27,70 do país (subvenções 15,30 de 15,61; encargos 11,08 de 12,09) | DF |
| 6 | **Compras centralizadas distribuídas aos estados.** Departamento de Logística em Saúde (250005): medicamentos 10,82, vacinas e insumos 5,10, doenças hematológicas 1,54; livros didáticos do FNDE 2,02 | DF 55,59 de custeio, de 105,63 do país (52,6%); pelo localizador, 2,14 | DF |
| 7 | **Obras e compras de investimento pagas pela sede.** DNIT sede (393003) 13,54, em rodovias de vários estados (ação 163Q, 8,02); caças Gripen 1,48 e cargueiro KC-390 0,69 | DF 23,80 de 32,88 do país (72,4%); pelo localizador, 0,16 | DF |
| 8 | **Gasto no exterior pago por UG cadastrada no DF.** O cadastro põe em "DF" a Comissão Aeronáutica Brasileira na Europa (120091; 3,56 no recorte) e o Escritório Financeiro em Nova Iorque (240017; 2,62). Nenhuma UG com UF "EX" pagou no recorte | Localizador "exterior": 5,51, dos quais 4,55 vão ao DF e 0,96 ao RJ | DF |
| 9 | **Unidades nacionais dos outros Poderes** (Justiça Federal de primeiro grau, MPF, MPT, MPM, DPU, Justiça Militar). O cadastro do SIAFI mostra UGs ativas desses órgãos em todo o país (órgão 12000, Justiça Federal com os TRFs, e órgão 34000, MPU, com UGs nas 27 UFs; DPU em 17; Justiça Militar em 12), mas a base do Tesouro não diz qual UG pagou | 19,82 sem UF; na sede (Brasília), o DF iria de −R$ 6.836 para −R$ 7.390 por pessoa por mês | sem UF ou DF |
| 10 | **Sentenças judiciais do Executivo** (precatórios e RPV), pagas pelos tribunais e ausentes do arquivo do Portal | 41,28 sem UF; pela regra iriam à UF do tribunal que paga, que não está em nenhum arquivo aberto por UG | sem UF |
| 11 | **Gasto localizado em outra UF e pago por UG do DF.** A regra também tira de uma UF o que o localizador já punha nela | 11,00 no país, dos quais RS 6,62 (enchentes: famílias desalojadas 2,28, subvenção do Pronampe 0,81, seguro-desemprego 0,37) | DF |
| 12 | **Folha bruta.** O valor pago inclui o IR retido e a contribuição do servidor, que o lado "envia" já conta no DF pela sede. Com a regra, os dois lados ficam pela sede; antes, só o "envia" ficava | IRRF do trabalho no DF 48,31 e CPSSS 18,44 (pesquisa do DF, seção 3) | simetria, não distorção nova |
| 13 | **Foto do cadastro.** UF da sede em junho de 2025, aplicada a 2024 | Entre as fotos de 2020 e 2025, só R$ 1,10 bi do recorte está em UGs que mudaram de UF (seção 1) | pequeno |

Leitura de conjunto (cálculo): das UGs que a regra põe no DF, R$ 327,69 bi vêm de despesa que o SIAFI lança com localizador sem UF (Nacional, regional ou exterior), R$ 22,27 bi já tinham localizador DF e R$ 11,00 bi tinham localizador de outra UF. A regra não descobre onde o gasto "Nacional" acontece: ela o põe onde fica a unidade que paga, que é Brasília para quase todas as folhas e programas nacionais e o Rio para a Marinha e a Aeronáutica.

## 7. As maiores UGs do recorte (2024, R$ bi)

| UG | Nome no SIAFI | UF no cadastro | Total no recorte | Maior parte |
|---|---|---|---:|---|
| 380916 | Coordenação-Geral de Recursos do FAT | DF | 80,64 | benefícios a pessoas 80,64 |
| 160063 | Centro de Pagamento do Exército | DF | 48,46 | pessoal militar 45,81 |
| 773200 | Pagadoria de Pessoal da Marinha | RJ | 26,37 | pessoal militar 23,99 |
| 120052 | Subdiretoria de Pagamento de Pessoal (Aeronáutica) | RJ | 22,23 | pessoal militar 19,66 |
| 170597 | Dir. Centralização de Inativos, Pensionistas e Órgãos Extintos | DF | 20,54 | aposentadorias e pensões 20,10 |
| 250005 | Departamento de Logística em Saúde | DF | 20,34 | custeio 19,86 |
| 250006 | Coordenação-Geral de Gestão de Pessoas (Saúde) | DF | 17,13 | aposentadorias e pensões 9,13 |
| 170700 | Coord.-Geral de Controle e Execução de Operações Fiscais | DF | 15,93 | subvenções 10,11 |
| 393003 | DNIT, sede | DF | 15,04 | investimento 13,54 |
| 200334 | Coordenação-Geral de Administração (Fazenda) | DF | 7,56 | pessoal ativo 3,93 |
| 155007 | EBSERH, sede | DF | 7,21 | pessoal ativo 6,12 |
| 200281 | Folha de Pagamento, Fazenda | DF | 7,16 | pessoal ativo 6,80 |
| 512016 | Execução orçamentária do RPPU | DF | 5,87 | aposentadorias e pensões 5,77 |
| 510001 | Coord.-Geral de Orçamento, Finanças e Contabilidade | DF | 5,05 | pessoal ativo 2,65 |
| 200230 | Serviço de Orçamento e Finanças de Pessoal (Fazenda) | DF | 4,93 | pessoal ativo 2,60 |
| 257001 | Diretoria Executiva do Fundo Nacional de Saúde | DF | 4,84 | subvenções 3,55 |
| 254420 | Fundação Oswaldo Cruz | RJ | 4,64 | custeio 3,08 |
| 550007 | Secretaria Nacional de Renda de Cidadania | DF | 4,22 | benefícios a pessoas 3,43 |
| 154003 | CAPES | DF | 4,06 | benefícios a pessoas 3,77 |
| 173057 | Banco Central do Brasil | DF | 3,77 | aposentadorias e pensões 1,90 |

A lista das 60 maiores, com todas as subcategorias, está em `private/archive/data/ug/ug-balance-2024.json` (`top_ugs`).

## 8. Não consegui confirmar

| Item | Tentativa | Situação |
|---|---|---|
| UG que paga as unidades nacionais dos outros Poderes e as sentenças judiciais do Executivo | A base do Tesouro não tem UG; o Portal só tem o Executivo | Sem dado aberto por UG; caminho: Tesouro Gerencial (fechado) ou pedido pela Lei de Acesso à Informação ao Tesouro (pagamentos de 2024 por UG dos órgãos 10000 a 34000 e da unidade 71103) |
| UF de cada UG em 2024 (o cadastro aberto é a foto de junho de 2025) | Só as versões de 2025-06 e 2020-01 estão no CKAN | A de 2020 serviu só para medir mudanças (seção 1); nenhuma UG do recorte ficou sem UF por falta no cadastro (só o código inválido -3) |
| API de órgãos SIAFI do Portal da Transparência | Pede chave de acesso | Não usada; o cadastro do Tesouro bastou |
| Onde estão os militares e os aposentados pagos pelas unidades centrais | Microdado de militares com UF -1; aposentados sem coluna de UF (pesquisa da folha, seção 8) | Continua sem dado aberto; a regra os põe na UF do centro de pagamento |

## 9. Como reproduzir

Na pasta do projeto:

```bash
# cadastro de UGs do SIAFI (Tesouro Transparente)
curl -sS -A Mozilla/5.0 -o data/ug/siafi_unidades_gestoras_2025-06.csv 'https://www.tesourotransparente.gov.br/ckan/dataset/54a699f4-55e3-41cc-a900-27c123545472/resource/7b83145e-6dc5-4ad2-9730-77132188eb2f/download/siafirelatoriounidadesgestoras.csv'
# execução da despesa do Portal, com a UG: um mês a cada 90 s (WAF); retoma de onde parou e apaga cada ZIP
python3 data/scripts/ug/agg_desp_ug.py data/ug 202401,202402,202403,202404,202405,202406,202407,202408,202409,202410,202411,202412 90
# base do Tesouro de 2024 (precisa de openpyxl, instalado no `.venv`)
.venv/bin/python data/scripts/ug/agg_dtt_full.py data/ug 2024
# contas, checagem e erro de controle
python3 private/archive/data/scripts/ug/build_ug_balance.py            # grava private/archive/data/ug/ug-balance-2024.json
python3 private/archive/data/scripts/ug/build_ug_balance.py --control  # tem de falhar
python3 private/archive/data/scripts/ug/bridge_portal_tesouro.py       # ponte Portal contra Tesouro
python3 private/archive/data/scripts/ug/report_ug_tables.py            # tabelas deste relatório
```


## Regra em duas etapas (2024)

Regra aprovada pelo autor (GD16 no grill): vale a UF onde o gasto foi aplicado quando o localizador do arquivo de execução tem
UF; senão, a UF da unidade gestora que pagou. Seguro-desemprego e abono salarial contam pela UF de quem recebeu. Juros e
amortização da dívida ficam fora; repasses e benefícios seguem contados pelo destino, como em D41.

O agente que fez este cálculo parou antes de escrever esta seção. O agente principal escreveu a seção a partir de
`private/archive/data/ug/ug-balance-2024_hybrid.json`, depois de rodar de novo `private/archive/data/scripts/ug/build_ug_balance_hybrid.py` (o JSON se reproduz
igual, menos a data da coleta) e o controle `--control` (tira R$ 1 bi de SP; o script para com "CHECAGEM FALHOU").

### Seguro-desemprego e abono por UF
- Fonte: Ministério do Trabalho e Emprego, Relatório de Gestão do FAT, exercício 2024,
  <https://portalfat.trabalho.gov.br/wp-content/uploads/2025/04/Relatorio-de-Gestao-do-FAT-2024.pdf>: seguro-desemprego no
  Gráfico 13 (p. 42), abono salarial no Gráfico 14 (p. 43). Os valores saem dos rótulos dos gráficos, em R$ milhões com duas
  casas (`data/ug/mte-seguro-abono-uf-2024_hybrid.json`).
- Ressalva: no seguro-desemprego, a soma das barras por UF não bate com a pizza por região do mesmo gráfico (Norte -350,0,
  Nordeste +584,7, Sul -381,6, Centro-Oeste +82,7, Sudeste +64,2, R$ milhões), embora o total bata; o texto do relatório
  confirma as barras. Usam-se as barras, a única série por UF publicada. No abono, barras e pizza batem.
- O relatório soma o que foi pago aos trabalhadores no ano, não a execução orçamentária do Portal. A diferença fica sem UF:
  R$ 0,40 bi no seguro-desemprego e R$ 0,50 bi no abono (inclui R$ 0,35 bi "não classificado" pelo próprio MTE).

### Saldo, R$ por pessoa por mês (positivo = envia mais do que recebe)

| UF | Atual (D41) | UG pura | Duas etapas |
|---|---:|---:|---:|
| SP | 1.270 | 1.259 | 1.223 |
| RJ | 1.343 | 971 | 944 |
| SC | 781 | 762 | 721 |
| ES | 282 | 263 | 228 |
| PR | 198 | 184 | 150 |
| MG | -32 | -51 | -85 |
| MT | -34 | -56 | -89 |
| RS | 21 | -14 | -98 |
| GO | -74 | -88 | -122 |
| AM | -152 | -194 | -220 |
| MS | -155 | -191 | -232 |
| PE | -394 | -422 | -447 |
| CE | -453 | -476 | -500 |
| RO | -384 | -489 | -521 |
| PA | -469 | -494 | -530 |
| BA | -488 | -503 | -532 |
| RN | -635 | -668 | -698 |
| SE | -668 | -690 | -721 |
| PB | -678 | -701 | -729 |
| AL | -685 | -704 | -732 |
| MA | -690 | -704 | -747 |
| TO | -727 | -747 | -777 |
| PI | -796 | -820 | -846 |
| AC | -1.037 | -1.069 | -1.094 |
| RR | -941 | -1.130 | -1.153 |
| AP | -967 | -1.151 | -1.185 |
| **DF** | 2.918 | -6.836 | **-4.318** |

- **DF: -R$ 4.318 por pessoa por mês** (-R$ 154,57 bi no ano), o 27º, cerca de 3,6 vezes o 26º (AP, -R$ 1.185). Pela UG pura
  era -R$ 6.836; pelo critério atual, +R$ 2.918.
- As outras UFs mudam pouco em relação à UG pura; o RS cai para -R$ 98 porque a ajuda das enchentes volta para o RS.

### O que fica sem UF
- Executivo: R$ 0,40 bi de UGs fora do cadastro, R$ 0,40 bi de seguro-desemprego e R$ 0,50 bi de abono.
- Outros Poderes: R$ 19,82 bi das unidades de atuação nacional (Justiça Federal de primeiro grau, MPF, MPT, MPM, DPU, Justiça
  Militar).
- Sentenças judiciais e resíduo entre o Tesouro e o Portal: R$ 41,76 bi.

### Checagem
- A soma das 27 UFs mais o que ficou sem UF bate ao centavo com o recorte do Executivo do cálculo anterior
  (R$ 548,54 bi) e com o total publicado pelo Tesouro (R$ 669,59 bi); diferença R$ 0,00.
- Nada saiu do saldo por falta de dado por UF.

### Distorções que sobram (maiores UGs que ainda contam pela sede, porque o localizador não tem UF)
| UG | UF do cadastro | 2024 (R$ bi) | O que é |
|---|---|---:|---|
| Centro de Pagamento do Exército | DF | 48,46 | 45,81 de folha militar de quem serve no país inteiro |
| Pagadoria de Pessoal da Marinha | RJ | 26,37 | 23,99 de folha militar |
| Subdiretoria de Pagamento de Pessoal (Aeronáutica) | RJ | 22,23 | 19,66 de folha militar |
| Departamento de Logística em Saúde | DF | 20,34 | Compras centralizadas do Ministério da Saúde para o país |
| Inativos e pensionistas de órgãos extintos | DF | 17,76 | Aposentadorias e pensões pagas de forma centralizada |
| Operações fiscais do Ministério da Fazenda | DF | 15,07 | 9,59 de subvenções econômicas e 5,35 de encargos |
| DNIT | DF | 12,05 | 10,56 de investimento em rodovias sem UF no localizador |

Nenhum arquivo aberto diz onde moram os militares nem onde chegam as compras centralizadas; a tela precisa dizer que, no DF e
no RJ, parte do que "voltou" é gasto pago ali para o país inteiro.
