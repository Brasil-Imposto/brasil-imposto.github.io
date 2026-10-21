# DF por Região Administrativa: dinheiro público e quem decide, por RA

**Coleta:** 2026-10-03. **Regra seguida:** só fonte oficial do GDF, página ou API primária aberta para cada número; o que não abriu está marcado "não confirmado". Nada estimado.
**Arquivos:** script `data/scripts/df/build_region_money.py`; dados `data/df/region-money.json`.
**Pedido:** cobrir o DF como SC (cada divisão do mapa com dado de dinheiro e um painel ao clicar), usando só dinheiro público e quem decide.

## 0. Resumo

- **Existe por RA, 2019 a 2026:** orçamento de cada Administração Regional (aprovado, autorizado, empenhado, liquidado; pago para 31 das 35), e o gasto do GDF localizado por RA, somado a partir do subtítulo de cada ação (liquidado). Tudo vem do Portal da Transparência do DF por API aberta, atualizado em 2026-10-02.
- **O gasto localizado cobre pouco:** só 3,5% a 8,7% do liquidado do GDF cita uma RA; o resto é "DISTRITO FEDERAL". E parte do que é localizado é a sede de órgãos (Plano Piloto lidera por causa da folha do TCDF, do DER e do Hemocentro).
- **Administrador:** nome em 30 RAs pela folha de agosto de 2026 (Vicente Pires tem duas pessoas na função; 6 RAs sem ninguém); data do ato, edição do DODF e foto não confirmados (DODF e sites das Administrações não responderam).
- **Obras:** a lista com empresa (Infobras) não respondeu; o orçamento dá as maiores obras por RA com valor e órgão executor, sem empresa.
- **Maiores valores:** PAC de vias de Vicente Pires, R$ 416,8 mi liquidados de 2019 a 2026; túnel de Taguatinga, R$ 347,0 mi; urbanização do Sol Nascente, R$ 283,2 mi.

## 1. Onde o GDF publica isso (todas as rotas abriram em 2026-10-03)

O Portal da Transparência do DF (`https://www.transparencia.df.gov.br`, mantido pela Controladoria-Geral do DF com dados do SIGGo, o sistema contábil do GDF) é um app Angular. As rotas estão em `scripts/app.min.js` (constante `api` = `/api`). Toda chamada exige o cabeçalho `x-client-id` com um UUID qualquer (o próprio app gera um com `crypto.randomUUID()`); sem ele a API responde 400 "Header x-client-id obrigatório".

| Rota | O que traz | Usada para |
|---|---|---|
| `/api/despesa/detalhamento?anoExercicio=AAAA&page=N` | por Unidade Gestora (UG): aprovado na LOA (`valorLei`), alteração, movimentação, bloqueado, autorizado (`valorDespesaAutorizada`), empenhado, liquidado; e um `totalizador` do ano | orçamento de cada Administração Regional; total da checagem |
| `/api/despesa/detalhamento/AAAA/<UG>` | o mesmo, por programa de trabalho e **subtítulo** (`nomeSubtitulo`, que traz o lugar no fim) | gasto localizado por RA; obras |
| `/api/v2/despesas-ras?exercicio=AAAA` | painel "Despesas Regionais" do portal: empenhado, liquidado e **pago** por Administração Regional | valor pago de cada Administração |
| `/api/servidor?nomeFuncao=ADMINISTRADOR%20REGIONAL&exercicio=AAAA&mesReferencia=M` | folha do GDF: quem ocupa a função de administrador regional | administrador de cada RA |
| `/api/dataAtualizacao/<chave>` | data da última carga (milissegundos) | `published_on` |

Página humana equivalente: `https://www.transparencia.df.gov.br/#/despesas/detalhamento` (Detalhamento da Despesa) e o mapa "Despesas Regionais" na home do portal.

Datas de atualização informadas pelo próprio portal (`/api/dataAtualizacao/...`): detalhamento 2026-10-02 (11:45 UTC), painel de despesas 2026-10-02, servidores 2026-10-02. O ano de 2026 é parcial, até essa data.

## 2. Orçamento e gasto de cada Administração Regional (item 1): existe, 2019 a 2026

- Cada Administração Regional é uma UG própria, códigos 190103 (Plano Piloto) a 190137 (Arapoanga). O mapeamento UG para RA foi feito pelo nome que o próprio portal dá à UG, e conferido: 190103 a 190133 seguem a numeração das RAs I a XXXI; 190134 é Arniqueira (RA XXXIII), 190135 Sol Nascente/Pôr do Sol (RA XXXII), 190136 Água Quente (RA XXXV), 190137 Arapoanga (RA XXXIV).
- Por ano e RA o JSON traz: `initial` (aprovado na LOA), `authorized` (autorizado, depois de créditos e bloqueios), `committed`, `liquidated` (Detalhamento por UG) e `paid` (painel Despesas Regionais).
- Cobertura: 31 Administrações em 2019 e 2020; 33 em 2021 a 2023 (entram Sol Nascente e Arniqueira); 34 em 2024 (Arapoanga); 35 em 2025 e 2026 (Água Quente).
- **`paid` só existe para 31 Administrações.** O painel `/v2/despesas-ras` não traz Sol Nascente/Pôr do Sol, Arniqueira, Arapoanga nem Água Quente em nenhum ano; para elas `paid` é `null` e vale o liquidado.
- **26 de Setembro (RA XXXVI) e Ponte Alta (RA XXXVII)**, criadas pelas Leis 7.918 e 7.917 de 03/07/2026, ainda não têm UG no orçamento de 2026; `administration_budget` fica vazio.
- Ordem de grandeza: as 35 Administrações somaram R$ 345,4 mi autorizados e R$ 319,7 mi liquidados em 2025, menos de 1% do liquidado do GDF (R$ 42,37 bi). A maior é Taguatinga (R$ 21,2 mi autorizados em 2025); a menor com UG é Água Quente (R$ 1,8 mi). Em 2025, 72,1% do liquidado das 35 Administrações foi folha (ação 8502, Administração de Pessoal); em 30 delas a folha passa de 60%.
- Diferença conhecida entre as duas rotas: o empenhado é idêntico nas duas, mas o liquidado do painel Despesas Regionais é um pouco diferente do liquidado do Detalhamento (ex.: SCIA 2025, R$ 5.192.739,10 contra R$ 5.135.991,23). O JSON guarda cada um com o nome da rota de onde veio; não misturar.

## 3. Gasto do GDF localizado por RA (item 2): existe, mas cobre só 4% a 9% do gasto

**Dá para somar.** A rota `/api/despesa/detalhamento/AAAA/<UG>` devolve, para cada UG, o valor por subtítulo, e o GDF escreve o lugar no fim do subtítulo, depois do último hífen (ex.: "CONSTRUÇÃO DE TÚNEL-RODOVIÁRIO NA AVENIDA CENTRAL- TAGUATINGA"). O script baixa todas as UGs de cada ano (123 a 136 por ano, cerca de 3.300 a 4.300 subtítulos por ano) e classifica cada linha:

1. o último trecho cita exatamente uma RA: conta para essa RA;
2. o último trecho é "DISTRITO FEDERAL" ou "DF": `df_wide` (o GDF não regionalizou);
3. o último trecho não cita lugar: vale o texto inteiro, se ele citar exatamente uma RA;
4. linhas da própria Administração Regional sem lugar no texto contam para a RA dela;
5. o resto vai para `not_located` (ex.: "REGIÃO OESTE", "DF ENTORNO", emendas sem lugar) ou `multiple_regions`.

O valor é o **liquidado**: o pago não é publicado por subtítulo.

**Checagem:** em todos os anos, RAs + `df_wide` + `not_located` + `multiple_regions` = total liquidado do portal (`totalizador`), ao centavo (2025: R$ 42.370.260.061,43). **Controle:** a mesma checagem com a maior linha removida falha em todos os anos (o script para se o controle não falhar).

**O limite real:** o GDF marca quase tudo como "DISTRITO FEDERAL".

| Ano | Liquidado GDF | Localizado em alguma RA | % | `df_wide` | `not_located` |
|---|---|---|---|---|---|
| 2019 | R$ 23,55 bi | R$ 2,06 bi | 8,7% | R$ 21,43 bi | R$ 0,07 bi |
| 2020 | R$ 24,23 bi | R$ 1,85 bi | 7,6% | R$ 22,24 bi | R$ 0,14 bi |
| 2021 | R$ 27,74 bi | R$ 1,15 bi | 4,2% | R$ 26,35 bi | R$ 0,24 bi |
| 2022 | R$ 32,52 bi | R$ 1,18 bi | 3,6% | R$ 30,95 bi | R$ 0,38 bi |
| 2023 | R$ 32,10 bi | R$ 1,32 bi | 4,1% | R$ 30,40 bi | R$ 0,38 bi |
| 2024 | R$ 38,62 bi | R$ 1,50 bi | 3,9% | R$ 36,42 bi | R$ 0,70 bi |
| 2025 | R$ 42,37 bi | R$ 2,00 bi | 4,7% | R$ 39,63 bi | R$ 0,73 bi |
| 2026 (até 02/10) | R$ 31,59 bi | R$ 1,11 bi | 3,5% | R$ 29,97 bi | R$ 0,52 bi |

Saúde e educação, a maior parte do gasto, vêm com "DISTRITO FEDERAL" mesmo quando o nome cita um hospital ou escola de uma RA (ex.: "HOSPITAL REGIONAL DO RECANTO DAS EMAS- DISTRITO FEDERAL" fica em `df_wide`, porque o script segue o localizador do GDF).

**Cuidados para a tela (o número não pode ser lido como "gasto para a RA"):**
- O localizador às vezes marca a **sede do órgão**, não o público atendido. Plano Piloto tem o maior valor localizado todo ano (R$ 1,10 bi em 2025), e os três maiores itens são folha de pessoal de órgãos sediados lá: TCDF R$ 345,3 mi, DER R$ 198,7 mi, Fundação Hemocentro R$ 87,3 mi. Águas Claras: a sede do Metrô (R$ 37,4 mi de benefícios e R$ 24,6 mi de manutenção).
- SCIA/Estrutural aparece com R$ 281,2 mi em 2025, dos quais R$ 276,0 mi são "FORNECIMENTO EMERGENCIAL DE ALIMENTOS" da Secretaria de Desenvolvimento Social, localizado no "SETOR COMPL. DE IND. E ABASTECIMENTO". O dado oficial diz SCIA; se é a distribuição para o DF a partir de lá, o subtítulo não diz.
- A Codhab localiza "CONSTRUÇÃO DE UNIDADES HABITACIONAIS ... SOL NASCENTE- CEILÂNDIA" em Ceilândia (último trecho), embora o texto cite Sol Nascente. O script segue o localizador.
- Valores antes da criação de uma RA (ex.: Ponte Alta, R$ 0,5 mi em 2025 de uma pavimentação "DO MONJOLO A PONTE ALTA") são o lugar citado no texto, não uma RA que existia.
- Por isso o JSON traz, por RA, `localized_of_which_administration` (quanto é da própria Administração) e `top_localized_items_2025` (os três maiores itens com UG, ação e subtítulo), para o painel mostrar do que é feito o número.

## 4. Administrador regional (item 3): nome existe; data e ato do DODF não confirmados; foto não

- **Nome:** a folha do GDF no Portal da Transparência (`/api/servidor`, função "ADMINISTRADOR REGIONAL", símbolo CNP04, referência **agosto de 2026**, o último mês publicado; setembro ainda vem vazio) traz 32 registros em 31 Administrações. O JSON grava o nome e a `payroll_admission_date` (data de admissão na folha).
- **A data de admissão na folha não é o ato de nomeação.** Para quem vem da carreira, ela pode ser a da admissão original (ex.: Candangolândia, 05/01/2009). Por isso `since` e `act` ficam `null`.
- Sem administrador na folha de agosto de 2026: **Lago Norte, Riacho Fundo II, Sudoeste/Octogonal e Arniqueira** (nas três primeiras a folha mostra só a chefia de gabinete); e as duas RAs novas, 26 de Setembro e Ponte Alta. Não confirmado se o cargo está vago ou ocupado por alguém lotado em outro órgão.
- **Vicente Pires** tem duas pessoas com a função em agosto de 2026 (admissões em 07/04/2025 e 27/08/2026, provável troca no mês); o JSON guarda as duas em `payroll_holders` e deixa `name` nulo.
- **DODF (`dodf.df.gov.br`) e os sites das Administrações (`*.df.gov.br`, ex.: `planopiloto.df.gov.br`, `segov.df.gov.br`)** não responderam daqui (tempo esgotado em todas as tentativas; a Agência Brasília respondeu 403). Sem eles não há número da edição do DODF, data do ato nem foto com termos de uso: `act`, `since` e `photo` = `null`. O SINJ-DF abriu, mas ele indexa normas, não atos de pessoal. Próximo passo: abrir o DODF pelo Chrome do autor (no Brasil ou com navegador real), buscar "nomear ... Administrador Regional" por RA.

## 5. Obras por RA (item 4): lista com empresa não confirmada; o orçamento dá as maiores obras sem empresa

- A lista oficial de obras do GDF é o **Infobras** (`https://www.infobras.sinesp.df.gov.br/infobrasLai/index.xhtml`, linkado pelo Portal em "Obras e Instalações"); não respondeu daqui (tempo esgotado). O painel de "Obras Paralisadas" é um Power BI sem API aberta. A consulta "Obras e Instalações" do portal e a Consulta Dinâmica (que tem credor) usam a rota `/api/despesa/consulta-dinamica`, que respondeu **500 "Erro SQL"** a todas as combinações de parâmetros testadas. Resultado: **empresa não confirmada** (`company: null`).
- O que o JSON traz em `works`: as até 3 maiores **ações do tipo projeto** (código da ação começando por 1, 3, 5 ou 7) com nome de obra (construção, reforma, urbanização, pavimentação, implantação, drenagem, túnel, viaduto e afins) localizadas na RA, somando o liquidado de 2019 a 2026, com UG executora, ação, subtítulo e anos.
- As maiores:

| RA | Obra (subtítulo) | Executora | Liquidado 2019 a 2026 |
|---|---|---|---|
| Vicente Pires | PAC, pavimentação e qualificação de vias urbanas no setor habitacional | Secretaria de Obras | R$ 416,8 mi |
| Taguatinga | Construção de túnel rodoviário na Avenida Central | Secretaria de Obras | R$ 347,0 mi |
| Sol Nascente/Pôr do Sol | Obras de urbanização, Pró-Moradia, Condomínio Sol Nascente | Secretaria de Obras | R$ 283,2 mi |
| Ceilândia | Construção de unidades habitacionais, Codhab, Sol Nascente | Codhab | R$ 118,0 mi |
| São Sebastião | Construção de Centros de Detenção Provisória | Secretaria de Segurança Pública | R$ 38,3 mi |

## 6. Datas de publicação (item 5)

Todas as três fontes do portal informam atualização em **2026-10-02** (`/api/dataAtualizacao/detalhamento` = 1790941553673 ms; `painel-despesas` e `servidores-por-orgao` idem). O JSON grava em `sources[].updated_on` e em `regions[*].published_on`. A folha usada é a de referência 2026-08.

## 7. O que não existe ou não abriu, e por quê

| Item | Situação | Por quê |
|---|---|---|
| Pago por subtítulo (gasto localizado) | não existe na rota aberta | o Detalhamento publica até o liquidado; o pago com subtítulo só na Consulta Dinâmica, que dá "Erro SQL" |
| Pago das Administrações de Sol Nascente, Arniqueira, Arapoanga e Água Quente | não existe | o painel Despesas Regionais não traz essas UGs |
| Orçamento de 26 de Setembro e Ponte Alta | não existe | RAs criadas em 03/07/2026, sem UG no orçamento de 2026 |
| Gasto localizado da saúde e educação por RA | não existe | o GDF localiza quase tudo como "DISTRITO FEDERAL" (91% a 95% do liquidado) |
| Ato de nomeação (DODF), data, foto | não confirmado | DODF e sites das Administrações sem resposta daqui |
| Administrador de Lago Norte, Riacho Fundo II, Sudoeste/Octogonal, Arniqueira | não confirmado | sem a função na folha de agosto de 2026 |
| Empresa de cada obra | não confirmado | Infobras sem resposta; Consulta Dinâmica com "Erro SQL" |
| `dados.df.gov.br` | não usado | o portal da transparência já tem a série completa por API |

## 8. Como rodar

```bash
python3 data/scripts/df/build_region_money.py                    # baixa tudo (cerca de 1.100 chamadas, uns 15 min), pasta temporária apagada no fim
python3 data/scripts/df/build_region_money.py --rows-cache DIR    # guarda e reaproveita as linhas compactas (cerca de 6 MB para 8 anos)
```
O script para com erro se a checagem falhar ou se o controle não falhar. Sem `--rows-cache`, nenhum arquivo baixado fica no disco.
