# Livro de fluxos do dinheiro público: a estrutura que garante a conta

English summary: a single ledger of money flows between nodes (the União, state governments, municipalities, the people and
companies of each state, debt creditors, the outside world), each flow recorded once, in integer cents, with its source and
how its state was assigned. Every number on screen becomes a query on this ledger, and the build fails on any duplicate,
missing row or mismatch with the official totals. Built as a small warehouse (DuckDB) fed by idempotent loads, ready to
refresh as soon as each source publishes.

Situação: **aprovada pelo autor em 2026-10-08 (D121)**, com as quatro recomendações da seção 11. Base: D107, D114 a D121.

**Emenda de 2026-10-09 (D127):** nenhuma estimativa na tela. Dinheiro que é de algum estado, sem a fonte dizer qual, vai para o nó `soc:unknown`, mostrado como "sem informação de estado", nunca somado à União. `soc:br`, "União (país inteiro)", fica só para o que a fonte oficial classifica como nacional (D114, D115). O item 3 da seção 11 foi revogado.

## 1. Objetivo

O autor quer que cada brasileiro que entrar no site veja a verdade sobre o dinheiro do imposto (D107). Ele pediu uma estrutura de dados que
garanta a conta, sem receita nem despesa contada duas vezes (D119), e aprovou o
entendimento em 2026-10-08 (D120). As pesquisas e as fontes servem para validar a lógica; quando um número muda num lugar, ele
muda em todos os lugares onde aparece, porque todos saem da mesma linha.

## 2. Por que o jeito de hoje falha

Cada tela soma o dinheiro no seu próprio script, com a sua própria regra:

| Tela | Script de hoje | O que deu errado |
|---|---|---|
| Mapa dos estados | `build_two_step_balance.py` | o DF mudou de posição três vezes: o gasto nacional pago pela sede contou no DF, depois o salário de quem trabalha lá saiu e o imposto retido desse salário ficou (D118) |
| Modal do estado | `build_state_series.py` | o Fundeb e a parte das prefeituras contavam como receita e como gasto do estado (D116) |
| A conta da União | `union.json` | certo ao milhão, mas sem ligação com o mapa: os 27 estados somavam R$ 222,6 bi a favor enquanto a União tinha déficit |
| Para onde vai o dinheiro | `build_spending_slices.py` | uma busca por pedaço de palavra pôs R$ 10 bi de custeio de tribunais em "Servidores ativos" |

Quatro scripts, quatro regras. Um conserto num lugar não chega aos outros. O livro troca isso por uma base só.

## 3. Os princípios (aprovados pelo autor em 2026-10-08)

1. **Um livro de fluxos.** Cada movimento real de dinheiro é uma linha: de quem, para quem, em que mês, de que tipo, quanto, e a fonte oficial. Cada movimento é registrado uma vez. Nenhuma tela refaz a conta por conta própria.
2. **Quem manda e quem recebe dinheiro:** a União, cada governo estadual, os municípios de cada estado, as pessoas e empresas de cada estado, os credores da dívida e o exterior.
3. **Todo número da tela é uma soma sobre o livro:** o mapa, o modal do estado, a conta da União, o bolo do gasto.
4. **Um salário são duas linhas:** a União paga o salário bruto ao servidor e o servidor devolve o imposto retido. Conta o líquido que ficou. O DF não ganha crédito por imposto pago com salário do governo. A mesma regra vale para todos os estados.
5. **Dinheiro entre governos é repasse, não gasto:** da União para o estado, do estado para os municípios, o Fundeb. Só o gasto final de quem usa o dinheiro conta como gasto. É o que impede o gasto dobrado, e é como as estatísticas oficiais de finanças públicas consolidam as contas de governo.
6. **O que a fonte não consegue pôr num estado vai para "União (país inteiro)",** nunca é forçado num estado, dos dois lados.
7. **Empréstimo e dívida são linhas à parte:** o empréstimo que sai, o pagamento que volta, os juros que vão aos credores. A exportação nunca passa por um governo, o que mostra por que ela não cobre o déficit.
8. **Conferências embutidas; se uma falha, a construção para** (seção 6).

## 4. O modelo

### 4.1 Nós: quem tem o dinheiro

| Nó | O que é | Exemplo |
|---|---|---|
| `gov:uniao` | Governo Central do RTN: Tesouro, INSS e Banco Central | paga salários federais, recebe o imposto de renda |
| `gov:uf:SC` | governo do estado (o DF é estado e município ao mesmo tempo) | recebe o FPE, paga professores estaduais |
| `gov:mun:SC` | as prefeituras do estado, juntas; em SC, RS e DF também uma a uma (`gov:mun:4205407`) | recebem o FPM e a parte do ICMS |
| `soc:uf:SC` | pessoas e empresas que moram ou trabalham no estado | pagam impostos, recebem salários e benefícios |
| `soc:br` | **União (país inteiro)**: o que a fonte oficial classifica como nacional (localizador "Nacional" do orçamento) | vacinas compradas pela sede para o país todo |
| `soc:unknown` | **sem informação de estado** (D127): dinheiro de pessoas e empresas de algum estado, que a fonte não diz qual | a folha federal que nenhum arquivo aberto põe num estado |
| `fin:credores` | quem tem títulos da dívida, por tipo (bancos, fundos, previdência, estrangeiros) | recebe os juros |
| `ext:mundo` | o exterior | paga pelas exportações |

### 4.2 O fluxo: a linha do livro

O grão é: uma linha da fonte oficial, num mês, de um nó para outro, de um tipo.

```
flow(
  flow_id         TEXT PRIMARY KEY,    -- hash of (source_id, source_key, period, from_node, to_node, flow_type)
  period          DATE,                -- first day of the month
  from_node       TEXT REFERENCES node,
  to_node         TEXT REFERENCES node,
  flow_type       TEXT REFERENCES flow_type,
  amount_cents    BIGINT,              -- integer cents, never floating point
  basis           TEXT,                -- 'cash' or 'accrual'
  source_id       TEXT REFERENCES source_release,
  source_key      TEXT,                -- the source's own row key (budget action, tax line, program)
  location_method TEXT,                -- 'direct', 'official_split', 'estimate', 'unallocated'
  rule_id         TEXT REFERENCES allocation_rule,
  pair_id         TEXT                 -- links a gross salary to the tax withheld from it
)
```

O valor é guardado em centavos inteiros: soma de inteiros não erra por arredondamento, e todo total fecha ao centavo.

### 4.3 Tipos de fluxo

| Tipo | Natureza | De para | Fonte principal |
|---|---|---|---|
| imposto e contribuição | primário | `soc:uf` para `gov:uniao` | Receita Federal, arrecadação por estado |
| imposto retido de salário público | circular | `soc:uf` para `gov:uniao`, par do salário | Receita (CPSS e retenções identificáveis) |
| salário bruto de servidor | primário | `gov:uniao` para `soc:uf` | folha federal por estado de exercício |
| benefício (INSS, BPC, Bolsa Família, seguro) | primário | `gov:uniao` para `soc:uf` | BEPS, MDS, Ministério do Trabalho |
| compra, obra, serviço | primário | `gov:uniao` para `soc:uf` ou `soc:br` | Tesouro, gasto por ação e localizador |
| repasse constitucional e voluntário | entre governos | `gov:uniao` para `gov:uf` ou `gov:mun` | Tesouro e Portal da Transparência |
| parte das prefeituras e Fundeb | entre governos | `gov:uf` para `gov:mun` | SICONFI, RREO |
| imposto estadual e municipal | primário | `soc:uf` para `gov:uf` ou `gov:mun` | SICONFI, RREO |
| juros da dívida | financeiro | `gov:uniao` para `fin:credores` | Banco Central (competência) e Tesouro (caixa) |
| empréstimo e devolução | financeiro | `gov:uniao` para `soc:uf` e de volta | Tesouro e as exposições de motivos |
| dividendos e royalties | primário | empresa para `gov:uniao`; royalties repartidos | RTN, ANP, ANM |
| exportação e importação | fora do governo | `ext:mundo` para `soc:uf` e de volta | Comex Stat |

### 4.4 Onde cada fluxo mora

Cada linha diz como o estado foi escolhido, e a tela mostra isso:

- **direto:** a fonte dá o estado de quem paga ou recebe;
- **divisão oficial:** uma distribuição oficial por estado (por exemplo, o boletim do INSS por estado) reparte o valor;
- **estimativa:** uma divisão aproximada; desde D127 nunca vai à tela (o valor aparece em "sem informação de estado");
- **sem estado:** vai para `soc:unknown`, "sem informação de estado" (D127), nunca para a União; só o que a fonte classifica como nacional vai para `soc:br`, "União (país inteiro)".

**Regra dos pares:** o imposto retido de um salário público mora no mesmo estado que o salário. Assim o circular se anula
estado por estado, e o DF não fica nem com o salário de quem trabalha fora nem com o imposto de quem não mora lá. As regras de
localização ficam numa tabela própria (`allocation_rule`), com a evidência e a versão de cada uma.

### 4.5 Fontes e versões

Cada carga de fonte vira uma linha em `source_release`: conjunto de dados, data de divulgação, endereço, SHA-256 do arquivo
lido (D98) e data da coleta. Uma divulgação nova substitui a anterior pela chave natural do fluxo: carregar duas vezes a mesma
divulgação não muda nada. O arquivo bruto não é guardado: é lido em fluxo, somado e descartado (regra de disco).

## 5. Cada número da tela é uma consulta

| Tela | Consulta sobre o livro |
|---|---|
| Mapa: saldo do estado | o que vai de `soc:uf:X`, `gov:uf:X` e `gov:mun:X` para `gov:uniao`, menos o que vem de `gov:uniao` para esses três nós, no período |
| Blocos "União (país inteiro)" e "sem informação de estado" do mapa | os mesmos fluxos com `soc:br` e com `soc:unknown`, cada um no seu bloco (D127); os 27 estados mais os dois blocos dão o total oficial dos dois lados |
| Modal do estado | entradas e saídas de `gov:uf:X`; "Recebeu" sem os repasses que saem; "Gastou" só o que vai para fora do governo |
| A conta da União | o nó `gov:uniao`, conferido com cada linha do RTN e com o Banco Central |
| Para onde vai o dinheiro | as saídas de `gov:uniao` por área e programa |
| O que o Brasil vende | os fluxos de `ext:mundo`, fora do governo |

Os casos de obra e os escândalos continuam no seu próprio domínio e se ligam ao livro pelo número do contrato.

## 6. As garantias

A construção para se qualquer uma falhar:

1. Nenhum `flow_id` repetido.
2. Toda linha tem origem, destino diferente da origem, tipo, fonte e método de localização.
3. Cada divulgação de fonte soma exatamente o total que ela mesma publica, ao centavo.
4. Por tipo de fluxo e mês, os 27 estados, `soc:br` e `soc:unknown` dão o total nacional, ao centavo.
5. O nó `gov:uniao` bate com o RTN e com o Banco Central, linha por linha.
6. Todo par salário e imposto retido mora no mesmo estado.
7. Fluxo entre governos nunca entra numa medida de gasto.
8. **Testes que têm de falhar:** uma linha duplicada de propósito, uma linha apagada, um sinal trocado, um par em estados diferentes. Se algum desses passar, a conferência está quebrada e a construção para.

## 7. Arquitetura

Extrair, normalizar, localizar, conferir, publicar:

- **Extrair:** um carregador por fonte, que lê em fluxo e não guarda o bruto.
- **Normalizar:** a linha da fonte vira fluxo, com tipo e nós.
- **Localizar:** aplica as regras de `allocation_rule`.
- **Conferir:** as garantias da seção 6.
- **Publicar:** JSON por entidade para o site estático (D55, D56).

O armazém é um arquivo DuckDB: gratuito, local, feito para consultas de análise, SQL comum. Estimativa de tamanho e de tempo
na fase 1, antes de seguir.

## 8. Pronto para tempo real

As fontes publicam por mês, e algumas por dia. "Tempo real" aqui quer dizer: assim que a fonte publica, o site mostra.

- Um calendário de divulgação por fonte.
- Cargas incrementais e idempotentes pela chave natural.
- Uma tarefa agendada gratuita (GitHub Actions em repositório público) que busca, confere e publica.
- A data de cada número na tela.

## 9. Fases

| Fase | O que entrega | Como se confere |
|---|---|---|
| 0 | esta spec aprovada | o "aprovado" do autor |
| 1 | o esqueleto do livro e o nó `gov:uniao`, de jan/2019 a ago/2026 | bate com o RTN e com o Banco Central linha por linha |
| 2 | a arrecadação por estado e as regras de localização | 27 estados, `soc:br` e `soc:unknown` dão o total da Receita |
| 3 | o que a União paga a cada estado: repasses, benefícios, folha com divisão oficial, compras | soma e pares conferidos; a decomposição do DF mostrada ao autor antes de qualquer cor (D118) |
| 4 | governos estaduais e municipais (SICONFI) | cada estado bate com o seu RREO |
| 5 | todas as telas lidas do livro; os scripts antigos saem | as telas mostram os mesmos totais da conta da União |
| 6 | o calendário e a tarefa agendada | uma divulgação nova entra sem mudar nada mais |

Até a fase 5, a prévia fica com os números de hoje, marcada "em revisão", e o DF por estimativa marcada (D146; antes cinza, D120 e D138).

## 10. Limites conhecidos das fontes

- **Folha federal por estado em dinheiro:** o SIAPE publica só a contagem de servidores; o microdado de remuneração do Portal estava bloqueado na última coleta. Na fase 3, a ordem de busca é o microdado do Portal, o Atlas do Estado Brasileiro do IPEA e a RAIS; o que nenhuma fonte oficial põe num estado (militares, aposentados e pensionistas) fica em "sem informação de estado" (D127).
- **Imposto centralizado nas sedes de empresas:** a Receita não publica por empresa, então o imposto de um banco com sede em Brasília conta no DF. Fica onde a Receita registra, com a marca de sede e sem tamanho estimado (D127), a menos que surja uma divisão oficial.
- **Juros:** o Banco Central mede por competência (o que correu) e o Tesouro por caixa (o que foi pago). O livro guarda os dois e cada tela diz qual mostra.
- **Arrecadação por estado de fev/2025 a jan/2026:** os meses da quebra da Receita voltam ao autor na fase 2, com opções (D127): o dado oficial existe, mas põe no DF a arrecadação de outros estados.

## 11. Decisões do autor (D121: "go with your recommendation on all")

| # | Decisão | Decidido |
|---|---|---|
| 1 | Motor do armazém: DuckDB, SQLite ou arquivos Parquet soltos | DuckDB |
| 2 | Juros na conta da União: só o que correu (Banco Central, como hoje); só o que foi pago em dinheiro; ou os dois lado a lado | os dois lado a lado |
| 3 | Folha federal sem divisão oficial em dinheiro: estimativa pela contagem oficial de servidores, marcada; ou deixar em "União (país inteiro)" | estimativa marcada; **revogado em 2026-10-09 (D127): sem estimativa, a folha sem estado fica em "sem informação de estado"** |
| 4 | Começar a fase 1 numa sessão nova, com esta spec como ponto de partida | sim |
