# Livro de fluxos, fase 1: o que foi construído e conferido

English summary: phase 1 of the money-flow ledger is built and published in the local warehouse (DuckDB,
`data/ledger/ledger.duckdb`). The gov:uniao node holds every line of the Tesouro's RTN Tabela 1.2 from January 2019 to
August 2026 as 8,281 flows, plus 500 monthly interest payments in cash from the Tesouro's expense base. All seven
guarantees of spec section 6 pass, and the four planted errors are caught. Every RTN line matches its own published
value to the cent. Totals and results match within rounding: at most 3 and 4 cents, because the Tesouro publishes
fractions of a cent. The Banco Central series match within one published unit (largest gap R$ 5,933). Interest paid
matches the União's RREO to the cent from 2024 on, and within R$ 1 where the RREO prints whole reais (2019 to 2023). Two
2023 checkpoints are known gaps of R$ 0.96 and R$ 3.79 (D122). Reloading every source changed nothing. Nothing on the
site changed in this phase. Updated on 2026-10-09 (D127): money whose state the source does not give is tagged
"sem informação de estado" (no state information) and is never counted as kept by the União; the warehouse was rebuilt
from scratch under that rule.

Status: **fase 1 construída, conferida e publicada no armazém; o site não mudou**

**Atualizado em 2026-10-09 (D127):** o que a fonte não diz o estado leva a marca "sem informação de estado" e nunca fica somado à União. O armazém foi reconstruído do zero com essa regra; os números abaixo são os da reconstrução.

### O que esta fase entrega
O esqueleto do livro (spec, seções 4 a 7) e o nó `gov:uniao` de jan/2019 a ago/2026, batendo com o RTN linha por linha e
com o Banco Central, com os juros pelos dois critérios lado a lado (D121, D122). Plano: `docs/superpowers/plans/BRASIL-IMPOSTO_PLAN_money-flow-ledger-phase-1_2026-10-08.md`.
Código: `data/scripts/ledger/` (29 testes passam). Relatório da máquina: `data/ledger/build-report.json`.

## 1. As garantias

| Garantia | Resultado | O que foi medido |
|---|---|---|
| G1 nenhum `flow_id` repetido | passa | 8.781 fluxos, 8.781 identificadores |
| G2 toda linha completa | passa | origem, destino diferente, tipo, fonte, método de localização igual ao da regra, sinal permitido pelo tipo |
| G3 cada divulgação fecha com o que publica | passa | as partes do RTN somam os totais com diferença máxima de R$ 0,00005 em conta exata; juros pagos contra o RREO em 46 pontos: ao centavo de 2024 a 2026, dentro de R$ 1 de 2019 a 2023 (o RREO imprime reais inteiros; maior diferença R$ 0,50), mais as duas diferenças conhecidas de 2023 |
| G4 as partes de cada linha oficial somam a linha | passa | 12.674 linhas oficiais conferidas ao centavo |
| G5 o nó `gov:uniao` bate com o RTN e com o Banco Central | passa | 14.996 linhas-mês do RTN: cada linha ao centavo; totais até 3 centavos e resultados até 4 centavos, todos explicados por arredondamento; Banco Central: maior diferença R$ 5.106 (juros, SGS 4606), R$ 5.933 (primário, 4639) e R$ 4.984 (nominal, 4573), dentro de uma unidade publicada (R$ 10 mil) |
| G6 todo par salário e retenção no mesmo estado | passa | 92 pares (folha sem sentenças judiciais e contribuição do servidor, um por mês) |
| G7 repasse nunca entra numa medida de gasto | passa | nenhum fluxo entre governos fora do tipo repasse; a medida de gasto não tem repasse; nenhuma fonte mistura juros por competência e por caixa |

## 2. Os erros que têm de falhar

| Erro plantado | Onde | Pego por |
|---|---|---|
| linha duplicada | Cofins (1.1.05), ago/2026, R$ 37,38 bi | G1, G3, G4, G5 |
| linha apagada | FPM, FPE e IPI-EE (2.1), ago/2026, R$ 38,82 bi | G3, G4, G5 |
| sinal trocado | Fundeb, complemento da União (4.3.10), ago/2026, R$ 5,54 bi | G3, G4, G5 |
| par em estados diferentes | contribuição do servidor (1.4.3), ago/2026, levada ao DF | G6 |

Controle da construção (`build.py --control`): trocar o sinal do IRRF do trabalho (1.1.03.3.1) antes das garantias fez a
construção parar (G3, G4 e G5 acusaram), e a tabela publicada ficou idêntica antes e depois (mesma impressão digital).

## 3. A conta da União pelo livro (R$ bilhões)

Cada número abaixo é uma consulta sobre o livro (`measures.py`), não uma cópia do RTN. Entre parênteses, a linha do RTN.
Os juros aparecem como valor pago (no RTN a linha 9 é negativa). Os juros que correram (Banco Central, competência) e os
juros pagos em dinheiro (Tesouro, caixa) medem coisas diferentes e nunca entram na mesma soma.

| Ano | Receita (1) | Repasses a estados e municípios (2) | Receita líquida (3) | Despesa primária (4) | Resultado primário (5) | Primário pelo Banco Central (8) | Juros que correram, Banco Central (9) | Resultado nominal (10) | Juros pagos em dinheiro, Tesouro |
|---|---|---|---|---|---|---|---|---|---|
| 2019 | 1.635,61 | 288,33 | 1.347,28 | 1.442,34 | -95,06 | -88,90 | 310,12 | -399,01 | 282,09 |
| 2020 | 1.468,10 | 263,80 | 1.204,30 | 1.947,55 | -743,25 | -745,27 | 266,66 | -1.011,92 | 344,67 |
| 2021 | 1.932,65 | 353,55 | 1.579,10 | 1.614,17 | -35,07 | -35,87 | 407,28 | -443,15 | 256,36 |
| 2022 | 2.313,31 | 457,20 | 1.856,10 | 1.809,69 | 46,41 | 54,95 | 503,23 | -448,29 | 247,34 |
| 2023 | 2.353,43 | 452,01 | 1.901,42 | 2.129,92 | -228,50 | -264,53 | 614,55 | -879,08 | 240,66 |
| 2024 | 2.679,44 | 517,65 | 2.161,79 | 2.204,71 | -42,92 | -45,36 | 855,21 | -900,57 | 347,87 |
| 2025 | 2.902,27 | 569,72 | 2.332,56 | 2.394,25 | -61,69 | -58,69 | 891,88 | -950,57 | 350,69 |
| 2026 (jan a 08) | 2.081,63 | 411,89 | 1.669,74 | 1.764,60 | -94,87 | -97,09 | 714,40 | -811,49 | 415,81 |

Valores arredondados a R$ 10 milhões. Em seis contas a soma feita à mão difere em R$ 0,01 bi por causa desse
arredondamento: linha 10 de 2019, 2020 e 2022, linha 3 de 2022 e 2025, e linha 5 de 2026. Os valores exatos, ao
centavo, estão em `data/ledger/build-report.json`, e é com eles que as garantias conferem. Os números batem com a conta
da União de hoje (`data/series/union.json`) com diferença máxima de 4 centavos, e com a pesquisa "Por que a União fecha
no negativo": juros de R$ 714,4 bi e nominal de R$ 811,5 bi em 2026; R$ 891,9 bi e R$ 950,6 bi em 2025.

## 4. O que está "sem informação de estado" (fase 1)

O RTN não diz o estado de nada. Na fase 1, então, todo o dinheiro que entra na União ou sai dela para pessoas e empresas leva a marca "sem informação de estado" (D127): saiu da União, ou entrou nela, mas a fonte não diz de qual estado. Nada fica somado à União. Em bilhões:

| Ano | Pagos à União por pessoas e empresas, sem informação de estado | Pagos pela União a pessoas e empresas, sem informação de estado | Repasses a estados e municípios, sem informação de estado | Direto ao governo do DF (FCDF, custeio e capital) | Dos quais gasto que a fonte não separa |
|---|---|---|---|---|---|
| 2019 | 1.625,41 | 1.424,43 | 294,32 | 1,73 | 265,45 |
| 2020 | 1.458,69 | 1.848,36 | 351,61 | 1,97 | 641,77 |
| 2021 | 1.925,38 | 1.583,68 | 374,62 | 2,15 | 348,38 |
| 2022 | 2.310,21 | 1.763,40 | 497,99 | 2,41 | 318,04 |
| 2023 | 2.353,43 | 2.068,46 | 509,19 | 4,28 | 335,11 |
| 2024 | 2.679,44 | 2.159,57 | 557,97 | 4,82 | 382,74 |
| 2025 | 2.902,27 | 2.338,71 | 620,35 | 4,91 | 403,92 |
| 2026 (jan a 08) | 2.081,63 | 1.727,20 | 445,29 | 4,00 | 296,45 |

De 2019 a 2022 o que pessoas e empresas pagaram fica abaixo da receita do RTN pela compensação do Tesouro ao INSS pela
desoneração da folha (linha 4.3.08): é a União pagando a si mesma e fica na tabela de movimentos internos, nunca como
fluxo. A fase 2 reparte a arrecadação por estado; a fase 3, os repasses, benefícios, folha e compras.

## 5. As fontes

Cada divulgação foi lida uma vez, com o SHA-256 calculado enquanto o arquivo chegava, e apagada em seguida. Nenhum
arquivo bruto ficou no disco.

| Fonte | SHA-256 (12 primeiros) | Tamanho | Data da divulgação |
|---|---|---|---|
| Tesouro, RTN série histórica de ago/2026, Tabela 1.2 | `0b4c8bbd6d5e` | 4,3 MB | 29/09/2026 |
| Banco Central, SGS 4606 (juros nominais, Governo Federal e Banco Central) | `c29495deaefa` | 3,8 kB | a API não publica data |
| Banco Central, SGS 4639 (resultado primário) | `c8551539964e` | 3,8 kB | a API não publica data |
| Banco Central, SGS 4573 (resultado nominal) | `25541d9fcaa7` | 3,8 kB | a API não publica data |
| Tesouro, Despesas e Transferências Totais da União, 2019 | `c6fd6e938193` | 37,1 MB | 23/02/2024 (atualização no portal) |
| idem, 2020 | `1df8009cfb59` | 37,5 MB | 29/04/2025 |
| idem, 2021 | `0b0f7bcac494` | 37,8 MB | 29/04/2025 |
| idem, 2022 | `d1a85f5b1d87` | 36,7 MB | 29/04/2025 |
| idem, 2023 | `68f0be69a00d` | 31,8 MB | 29/04/2025 |
| idem, 2024 | `79147001fa45` | 29,6 MB | 30/12/2025 |
| idem, 2025 | `886f4e3266e9` | 34,5 MB | 25/02/2026 |
| idem, 2026 (até agosto) | `986cafb6901e` | 23,1 MB | 29/09/2026 |
| Tesouro, SICONFI, RREO da União, Anexo 1, 46 bimestres de 2019 a ago/2026 | um por bimestre | 0,17 a 0,30 MB cada | o SICONFI não informa a data na API |

O arquivo do RTN baixado tem o mesmo SHA-256 da cópia que já estava no disco desde 30/09/2026: o Tesouro não o mudou.

## 6. Tempo e tamanho (spec, seção 7)

| Medida | Valor |
|---|---|
| Construção do zero, baixando e lendo todas as fontes | 12 min 30 s (reconstrução de 2026-10-09, com D127) |
| Construção completa sem fonte nova (baixa tudo, nada muda) | 6 min 43 s, quase tudo download (12 s de processador) |
| Construção com as fontes já no armazém | 3 s, com as sete garantias e os quatro erros plantados |
| Armazém | 8,9 MB logo depois da reconstrução do zero; 15,2 MB depois de cinco construções na primeira rodada (o arquivo cresce um pouco a cada construção; a fase 6, com a carga mensal, decide se ele é recriado de tempos em tempos) |
| Carga dos 8 arquivos de juros pagos | cerca de 1 min por ano, um arquivo por vez; o disco ficou em 8,5 GB livres |
| Carregar tudo de novo | 58 divulgações, nenhuma nova, tabela publicada idêntica |

## 7. Limites desta fase e itens anunciados

- **Diferença conhecida de 2023 (D122):** a base do Tesouro tem R$ 0,96 (até outubro) e R$ 3,79 (até dezembro) a menos de
  juros pagos que o RREO de 2023. A causa não foi achada. As duas ficam anotadas com o valor exato, e a construção para se
  mudarem um centavo.
- **A folha do FCDF não vai ao DF nesta fase:** o RTN põe a folha paga pelo Fundo Constitucional do DF dentro de "Pessoal
  e Encargos" (4.2), sem informação de estado; só o custeio e o capital (4.3.11) vão direto ao governo do DF. É a fase 3 que
  separa, com a decomposição dos dois lados mostrada antes de qualquer cor (D118).
- **Gasto que a fonte não separa:** de R$ 265 bi (2019) a R$ 642 bi (2020) por ano estão em linhas do RTN que misturam
  compra com repasse a estados e municípios (Saúde, Educação e demais do Executivo, créditos extraordinários e outras). A
  fase 3 separa pela modalidade de aplicação da base do Tesouro.
- **Juros pagos e juros que correram medem coisas diferentes:** o Banco Central apura os juros líquidos que correram
  sobre a dívida no mês; o orçamento registra o que pagou como "juros e encargos da dívida". Por que a diferença é desse
  tamanho fica para a tela que mostrar os dois, com fonte; esta fase só guarda os dois sem misturar.
- **Suposição registrada:** a compensação do Tesouro ao INSS (4.3.08) está dentro da arrecadação urbana (1.3.1). Se
  estiver errada, só muda a divisão entre urbano e rural, que nada usa.
- **Encontrados no caminho e já resolvidos:** o Python 3.11 deste Mac não tem pacote de certificados, então os downloads
  passam pelo `curl`, como nos scripts de hoje; a API do Banco Central devolveu uma vez uma resposta vazia, e o carregador
  agora tenta de novo até três vezes; `at` é palavra reservada no DuckDB (a coluna virou `superseded_at`); o openpyxl só
  abre arquivo com nome terminado em `.xlsx`.

## 8. Como rodar

```bash
.venv/bin/python -m unittest discover -s data/scripts/ledger/tests   # 29 testes
.venv/bin/python data/scripts/ledger/build.py                        # busca tudo, confere, publica (cerca de 7 min)
.venv/bin/python data/scripts/ledger/build.py --skip-load            # só confere e publica o que já está no armazém
.venv/bin/python data/scripts/ledger/build.py --skip-load --control  # tem de parar com exit 1
```

## 9. Próximo passo

Depois da fase 2: o documento público do que falta e do que vem com apoio (D128), com cada lacuna, o tamanho medido no livro, a fonte oficial que a fecharia e o custo, inclusive os pedidos pela Lei de Acesso que ficam para quando houver apoio.


Fase 2 da spec: a arrecadação por estado e as regras de localização, com os 27 estados, "União (país inteiro)" e "sem informação de estado" dando o total da
Receita. Começa quando o autor mandar, com `/writing-plans` para a fase 2.
