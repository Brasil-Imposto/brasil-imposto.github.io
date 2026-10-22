# Poder Judiciário em "Os 3 Poderes": auditoria da remuneração, começando pelo STF

English summary: the maintainer suspected the STF pay on the "Os 3 Poderes" page was wrong (the STF president below the Senate
president, R$ 62k per minister, Dino and Moraes at R$ 53k, Gilmar at R$ 73k, "many auxílios"). Every STF number on screen was
recomputed to the cent from the repository and matches the data file and the page data (a check with two planted controls, both
caught). The numbers are the collector's arithmetic applied to what the STF eGesp payroll published for January to August 2026;
what makes them look odd is the method and what is measured, not an arithmetic error: (1) the Senate president's sheet adds his
whole office team (25 people, R$ 395.504,61 a month) and his quota, and the STF side measures no team at all, so the totals
compare different things; on "para a pessoa" the STF president is above the Senate president (R$ 62.805,71 against
R$ 46.366,19, the Senate side showing the position's value, the STF side the payroll average); (2) the STF's R$ 4.511,60 of
"mandato e equipe" is the TSE's per diems to Toffoli and Nunes Marques, not jetons; (3) "por mês" spreads one-off payments
(half a 13th salary, one third of a salary for holidays, Gilmar's R$ 92.429,97 of holiday pay) over the 8 published months;
(4) "No cargo desde 16/06/2015" is Fachin's admission to the STF, not his presidency (29/09/2025, already in the repository);
(5) the "Auxílios e benefícios", "Indenizações" and "Auxílio Moradia" columns read R$ 0,00 for all ten ministers in all eight
months, and the page turns that zero into "não recebe". One cent of rounding was found (a half cent rounded down on eight
ministers' holiday line). **No official source could be opened from this environment**: every court, CNJ, Planalto and Web
Archive host answered 403 to the proxy's CONNECT on 2026-10-22, so every check against the source is listed under "não
conferido", with the hosts and the error. The spec that follows from this audit is
`docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_judiciario-dados_2026-10-22.md`.

Status: **auditoria de 2026-10-22, feita só com o que está no repositório** (`main` em `615f7f3`): o arquivo
`data/federal/judiciary-2026.json` (coletado em 2026-10-21), o coletor `docs/superpowers/tools/collect-judiciary-2026.py`, o
construtor `docs/superpowers/tools/build-tres-poderes-r3-data.py`, os dados da página
(`docs/superpowers/previews/assets/tres-poderes-r3-data.js`) e a página em si, aberta num build local. Os arquivos brutos que o
coletor leu (`data/federal/raw-pay/`) não ficam no git, então não há série mês a mês aqui. Nenhum número deste documento veio de
notícia, estimativa ou memória.

### O pedido
Auditar os dados do Poder Judiciário na página "Os 3 Poderes", começando pelo STF, e escrever a spec para corrigir e melhorar.
A suspeita do autor é a pergunta a responder, não a resposta: onde a fonte oficial confirma um número, ele fica e a tela explica
por que é o que é; onde a fonte mostra mais, corrige.

### A resposta em uma frase
**As contas da página fecham ao centavo com o que o STF publicou; o que parece errado vem de três escolhas de método (a média
que espalha pagamentos do ano, um zero lido como "não recebe" e um "desde" que é a posse no tribunal) e de uma comparação
desigual (o Senado soma a equipe do gabinete e o STF não mede equipe nenhuma).** O que só a fonte responde (o mês a mês, a
legenda de cada coluna do eGesp, os auxílios fora da folha, a equipe de cada gabinete) ficou "não conferido" porque nenhum site
oficial abriu deste ambiente.

## 1. Como a auditoria foi feita

1. **Acesso às fontes.** Em 2026-10-22, às 17:31 e de novo às 17:33 UTC, cada host oficial respondeu ao proxy deste ambiente
   com `CONNECT tunnel failed, response 403` (curl, código 56). A regra do pedido é não contornar: nenhum espelho, nenhuma cópia de
   terceiros, nenhum serviço de busca. A lista dos hosts está na seção 10.
2. **O que dava para conferir aqui** foi conferido com uma checagem reproduzível,
   `docs/research/judiciario-auditoria-2026-10-22/check_stf_sums.py` (só lê, não escreve nada):
   - cada valor "por mês" é o total de 2026 dividido pelo número de meses que a nota do item diz, arredondado como o coletor
     arredonda;
   - os dados da página trazem os mesmos itens e valores que o arquivo do coletor;
   - o "Total por mês" de cada pessoa é a soma dos itens e é igual ao lido na tela;
   - a linha de subsídio é 8 vezes o subsídio da Lei 14.520/2023 como o arquivo o registra (R$ 46.366,19);
   - a soma dos 10, a média e a parte que a página põe em "mandato e equipe".

   Resultado: `PASS (0 differences)`, código de saída 0. **Controles:** `--plant` soma R$ 0,01 ao total de férias de Fachin e a
   checagem falha (2 diferenças, saída 1); `--plant-screen` soma R$ 0,01 ao total de Gilmar lido na tela e a checagem falha (1
   diferença, saída 1).
3. **A tela.** A página `BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html` foi servida localmente
   (`python3 -m http.server`) e as fichas de Fachin, Dino, Moraes, Gilmar e do presidente do Senado foram abertas pelo link
   próprio (`#p=stf:edson-fachin` e assim por diante), lidas e capturadas em 1440 e 420 px. Os totais lidos na tela são os da
   checagem acima.

## 2. O que a tela mostra hoje no STF, e de onde vem cada número

Todos os valores abaixo são "por mês" como a página mostra: o total de 2026 de cada coluna da folha do STF (eGesp, "Rendimentos
da folha", Situação Funcional = MINISTRO, janeiro a agosto de 2026, lida pelo coletor em 2026-10-21) dividido por 8, os meses
publicados. As linhas do TSE vêm do arquivo do TSE no painel do CNJ (Anexo VIII da Portaria CNJ 63/2017) e são divididas por 7,
os meses que o TSE publicou (janeiro e março a agosto; fevereiro não está no painel).

| Ministro | Subsídio | Vantagens pessoais | Abono de permanência | Férias | Gratificação natalina | TSE | Total por mês | Para a pessoa | Mandato e equipe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Edson Fachin (Presidente) | 46.366,19 | 4.057,04 | 7.552,67 | 1.931,92 | 2.897,89 | 0,00 | **62.805,71** | 62.805,71 | 0,00 |
| Alexandre de Moraes (Vice-Presidente) | 46.366,19 | 2.028,52 | 0,00 | 1.931,92 | 2.897,89 | 0,00 | **53.224,52** | 53.224,52 | 0,00 |
| Gilmar Mendes (Decano) | 46.366,19 | 4.057,04 | 7.552,67 | 11.553,75 | 2.897,89 | 596,14 (jeton) | **73.023,68** | 73.023,68 | 0,00 |
| Cármen Lúcia | 46.366,19 | 4.057,04 | 7.552,67 | 1.931,92 | 2.897,89 | 0,00 | **62.805,71** | 62.805,71 | 0,00 |
| Dias Toffoli | 46.366,19 | 1.738,73 | 0,00 | 11.997,04 | 2.897,89 | 6.160,10 (jeton) + 3.481,80 (diárias) | **72.641,75** | 69.159,95 | 3.481,80 |
| Luiz Fux | 46.366,19 | 4.057,04 | 7.552,67 | 1.931,92 | 2.897,89 | 0,00 | **62.805,71** | 62.805,71 | 0,00 |
| Nunes Marques | 46.366,19 | 2.897,89 | 0,00 | 1.931,92 | 2.897,89 | 8.743,37 (jeton) + 908,64 (gratificação eleitoral) + 1.029,80 (diárias) | **64.775,70** | 63.745,90 | 1.029,80 |
| André Mendonça | 46.366,19 | 2.897,89 | 0,00 | 1.931,92 | 2.897,89 | 8.743,37 (jeton) + 908,64 (gratificação eleitoral) | **63.745,90** | 63.745,90 | 0,00 |
| Cristiano Zanin | 46.366,19 | 0,00 | 0,00 | 1.931,92 | 2.897,89 | 0,00 | **51.196,00** | 51.196,00 | 0,00 |
| Flávio Dino | 46.366,19 | 2.318,31 | 0,00 | 1.931,92 | 2.897,89 | 0,00 | **53.514,31** | 53.514,31 | 0,00 |
| **Soma dos 10** | | | | | | | **620.538,99** | **616.027,39** | **4.511,60** |
| **Média por ministro** | | | | | | | **62.053,90** | | |

As colunas "Vantagens de natureza periódica/eventual", "Exercício de cargo em comissão/função comissionada", "Auxílios e
benefícios", "Indenizações", "Exercícios Anteriores e licença prêmio convertida em pecúnia" e "Auxílio Moradia" somam R$ 0,00 em
2026 para os 10 ministros, e a tela mostra cada uma como "não recebe" com um ✗.

**Conta à mão, Fachin:** 46.366,19 + 4.057,04 + 7.552,67 + 1.931,92 + 2.897,89 = 62.805,71. **Gilmar:** 46.366,19 + 4.057,04 +
7.552,67 + 11.553,75 + 2.897,89 + 596,14 = 73.023,68. **Dino:** 46.366,19 + 2.318,31 + 1.931,92 + 2.897,89 = 53.514,31.
**Moraes:** 46.366,19 + 2.028,52 + 1.931,92 + 2.897,89 = 53.224,52. As quatro batem com a tela.

Os números que o autor citou são os da tela: R$ 62 mil é a média por ministro (62.053,90), Dino R$ 53.514,31, Moraes
R$ 53.224,52, Gilmar R$ 73.023,68.

### O que cada total de 2026 é, em subsídios (derivado)
Dividindo o total de 2026 de cada coluna pelo subsídio de R$ 46.366,19 (conta feita aqui, não publicada pelo STF):

| Coluna | Total de 2026 | Em subsídios |
|---|---:|---|
| Subsídio | 370.929,52 | exatamente 8 (um por mês publicado) |
| Gratificação natalina e antecipação | 23.183,09 (os 10) | 0,5000: meio subsídio, a primeira metade do 13º |
| Férias | 15.455,40 (8 ministros) | 0,3333: um terço de um subsídio |
| Férias, Gilmar | 92.429,97 | 1,9935 |
| Férias, Toffoli | 95.976,31 | 2,0700 |
| Vantagens pessoais | de 0 a 32.456,34 | 0, 30, 35, 40, 50 ou 70% de um subsídio, exatamente |
| Abono de permanência | 60.421,36 (Fachin, Gilmar, Cármen, Fux) | 7.552,67 por mês, 16,29% do subsídio |

A conta mostra a forma dos números, não o que cada um paga: o arquivo guarda só o total do ano, e a legenda das colunas do eGesp
não pôde ser aberta (seção 10). Em particular, **não dá para dizer daqui se as férias de Gilmar e de Toffoli são férias
indenizadas, adiantamento ou outro lançamento**, nem o que é a rubrica "Vantagens Pessoais". Os arquivos de outros tribunais
detalham rubricas parecidas como adicional por tempo de serviço, VPNI e PVTAC (seção 8), mas o STF não detalha, e uma rubrica de
outro tribunal não vale como explicação para o STF.

## 3. As cinco pistas, uma a uma

### 3.1 O presidente do Senado, o do STF e os R$ 4.511,60 de "mandato e equipe"
Fichas lidas na tela, 2026-10-22:

| | Davi Alcolumbre (Senado) | Edson Fachin (STF) |
|---|---:|---:|
| Salário | 46.366,19, "valor do cargo, todo mês" | 46.366,19, média da folha de jan a ago |
| Outros componentes da folha | não entram | 16.439,52 (vantagens pessoais, abono, férias, 13º) |
| Auxílio-moradia | não recebe (usa imóvel funcional) | R$ 0,00 na folha, mostrado como "não recebe" |
| Cota (CEAPS) | 32.285,71 | não existe no STF |
| Equipe do gabinete | 395.504,61 (25 pessoas, salários brutos, jan a set) | **não medida** |
| **Total por mês** | **474.156,51** | **62.805,71** |
| Para a pessoa | 46.366,19 | 62.805,71 |
| Mandato e equipe | 427.790,32 | 0,00 |

1. **O total do Senado é maior porque mede mais coisas.** O bloco "Equipe do gabinete" soma os salários brutos de quem trabalha
   no gabinete e nos escritórios do senador (regra respondida em Q67, D145). Do lado do STF não há medida nenhuma da equipe dos
   gabinetes. A comparação dos totais compara um salário mais uma equipe com um salário sozinho.
2. **Para a pessoa, o presidente do STF fica acima do presidente do Senado** (62.805,71 contra 46.366,19). Mas os dois números
   também não são a mesma medida: o do Senado é o valor do cargo (o subsídio), o do STF é a média do que a folha pagou, com 13º,
   férias, abono de permanência e vantagens pessoais. A spec propõe a mesma régua dos dois lados (pergunta ao autor, porque mexe
   na ficha do Senado).
3. **Os R$ 4.511,60 do STF em "mandato e equipe" não são jetons.** São as diárias pagas pelo TSE a Dias Toffoli (3.481,80 por
   mês, R$ 24.372,60 em 2026) e a Nunes Marques (1.029,80 por mês, R$ 7.208,59 em 2026): o construtor marca `per_diem` e
   `tse_per_diem` como despesa do cargo, não da pessoa (`NOT_OWN` em `build-tres-poderes-r3-data.py`). Os jetons do TSE
   (Gilmar 596,14; Toffoli 6.160,10; Nunes Marques e Mendonça 8.743,37 cada) contam como "para a pessoa". Soma conferida:
   3.481,80 + 1.029,80 = 4.511,60.
4. **O que a presidência acrescenta.** Na folha publicada, nada: Fachin preside o STF desde 29/09/2025, então os oito meses de
   2026 são de presidente, e o total dele é igual, ao centavo, ao de Cármen Lúcia e ao de Luiz Fux (62.805,71); a coluna
   "Exercício de cargo em comissão/função comissionada" é R$ 0,00. O que a presidência tem fora da folha (o gabinete da
   presidência, carro, segurança, residência) não está no repositório e ficou não conferido. Nota: no TST e no STM o detalhe
   publicado traz "Representação magistrado presidente" (seção 8); no STF não aparece rubrica assim.

### 3.2 O que "por mês" quer dizer hoje
O coletor faz, para cada coluna, **total de 2026 dividido pelos meses que o tribunal publicou** (8 no STF, 7 no TSE), e a tela
escreve "média de jan a ago 2026" sob cada linha. A conta está certa; o efeito é espalhar pagamentos que acontecem uma ou duas
vezes por ano:

- **Gratificação natalina:** os R$ 23.183,09 são meio subsídio, a primeira metade do 13º. A tela mostra 2.897,89 por mês, o que
  não é o 13º espalhado pelo ano (se o 13º for um subsídio inteiro, premissa não lida em fonte hoje, seriam 46.366,19 / 12 =
  3.863,85) nem o que foi pago no mês em que foi pago (o arquivo não guarda o mês).
- **Férias:** 8 ministros têm R$ 15.455,40 no ano, um terço de um subsídio. A tela mostra 1.931,92 por mês. O pedido lembra que
  magistrados têm 60 dias de férias por ano; a regra não pôde ser lida hoje (o Planalto não abriu), então aqui ela é uma
  pergunta, não um fato: se for assim e o terço for pago a cada período, falta um terço no ano, e a média de jan a ago não diz
  isso.
- **Gilmar e Toffoli:** R$ 92.429,97 e R$ 95.976,31 de férias, divididos por 8, viram 11.553,75 e 11.997,04 "por mês". É isso que
  põe Gilmar em 73.023,68 e Toffoli em 72.641,75. Sem o mês a mês e a legenda não dá para dizer se é indenização de férias.
- **TSE:** os valores do TSE são divididos por 7 mesmo para quem aparece em 2 dos 7 meses (Gilmar), e a tela soma uma média de 8
  meses com uma média de 7. A ficha do Senado já mostra janelas diferentes (a cota de janeiro a julho, a equipe de janeiro a
  setembro), cada uma com o rótulo; no STF a janela do TSE aparece só na nota da linha.
- **Arredondamento:** 15.455,40 / 8 = 1.931,925 exatos. O coletor usa `round()` do Python num número de ponto flutuante, e
  1.931,925 vira 1.931,92 (o binário guarda 1.931,92499...). Arredondando meio centavo para cima, seria 1.931,93. Afeta a linha de
  férias de 8 ministros e o total de cada um em R$ 0,01. Nenhuma regra oficial fixa o arredondamento de uma média; a spec propõe
  uma regra escrita.

As opções de método e a recomendação estão na spec (seção 2).

### 3.3 Os auxílios zerados
- No arquivo, as colunas "Auxílios e benefícios", "Indenizações" e "Auxílio Moradia" somam R$ 0,00 em 2026 para os 10 ministros. O
  coletor lê o valor de cada célula com `num()`, que devolve 0,0 para célula vazia, para "0" e **também para um texto que não
  consegue ler** (o `except ValueError` devolve 0,0 sem aviso). Daqui não dá para separar "o STF publicou 0,00" de "a célula
  veio vazia" ou "o coletor não leu": os arquivos brutos não estão no git e o eGesp não abriu.
- A tela transforma esse zero em "não recebe" com ✗. Isso afirma mais do que o dado diz: um zero na coluna de uma folha não prova
  que a pessoa não recebe o benefício por outro caminho (um plano de saúde pago fora da folha, por exemplo).
- O auxílio-alimentação dos outros tribunais vem da Portaria Conjunta nº 3/2025. Pela nota que o coletor escreveu ao lê-la em
  2026-10-21, os signatários são CNJ, TSE, STJ e CJF, TST e CSJT, STM e TJDFT: o STF não está entre eles. Então um auxílio do STF,
  se existir, viria de ato do próprio STF, que não foi localizado (já registrado no `not_found` do arquivo).
- **Conferido em todos os relatórios de transparência do STF?** Não. Só a folha do eGesp está no repositório. Os demais relatórios
  (benefícios, diárias, passagens, veículos) não foram abertos: seção 10.

### 3.4 "No cargo desde 16/06/2015"
O coletor preenche `since` com a "Data de Admissão" da ficha individual do eGesp (`det-*.html`), que é a posse no STF. Para Fachin,
16/06/2015. A ficha mostra essa data como "No cargo desde" ao lado de "Cargo: Presidente", o que leva a ler a data como início da
presidência. A data da presidência já está no repositório: **29/09/2025**, em `data/federal/positions-2026.json` e
`officeholders-2026.json`, com a fonte STF Notícias
(`https://noticias.stf.jus.br/postsnoticias/ministro-edson-fachin-assume-hoje-29-a-presidencia-do-stf/`). As duas datas têm fonte
oficial; nenhuma das duas páginas pôde ser reaberta hoje para conferir. A data da vice-presidência de Moraes não está no
repositório.

### 3.5 Setembro de 2026
Em 2026-10-21 o eGesp devolveu HTTP 500 para o mês 9 (registrado no `not_found`). Hoje o host não abriu (403 no CONNECT do
proxy), então setembro **segue não conferido**: não dá para saber se foi publicado.

## 4. Os 10 ministros, mês a mês

**Não conferido.** O pedido era cada componente mês a mês como a fonte publica, com URL e data de leitura, e o total da própria
fonte conferido com o nosso arquivo ao centavo. O repositório não tem esse dado:

- o arquivo `judiciary-2026.json` guarda, por coluna, só o total do ano, a média e o rótulo dos meses ("jan a ago 2026"); o
  coletor do STF não grava `by_month` (o do Executivo grava, e o construtor confere que a soma dos meses bate com o total);
- as páginas mensais do eGesp lidas em 2026-10-21 (`data/federal/raw-pay/judiciary/stf/stf-2026-<m>.html`) não estão no git
  (`.gitignore`, linha 4) e não estão neste clone;
- o eGesp (`https://egesp-portal.stf.jus.br/transparencia/rendimento_folha`) não abriu hoje.

O que o arquivo permite dizer sobre o mês a mês, sem a fonte:
- **Subsídio:** 370.929,52 = 8 x 46.366,19, então os oito meses pagaram o subsídio cheio, para os 10.
- **Os demais:** só o total do ano. Os 10 aparecem nos 8 meses do STF (nenhuma nota "A pessoa aparece em N dos 8 meses"); no TSE,
  Gilmar aparece em 2 dos 7 meses, Toffoli em 5, Nunes Marques e Mendonça em 6.
- **O total da própria fonte:** o eGesp tem colunas de rendimento, não uma coluna de total que o coletor leia; a soma de
  conferência fica para a recoleta (spec, seção 5).

## 5. Cada item pedido, ministro do STF

"Não conferido" quer dizer que a resposta depende de uma página oficial que não abriu hoje; não quer dizer "não publicado" (que
exige ter tentado as URLs e não ter achado) nem "não recebe".

| Item | O que o repositório diz | Status desta auditoria |
|---|---|---|
| Auxílio-alimentação (o "auxílio refeição") | coluna "Auxílios e benefícios" do eGesp em R$ 0,00 nos 8 meses, sem detalhe; o STF não assina a Portaria Conjunta nº 3/2025 | não conferido (legenda do eGesp; ato do STF) |
| Auxílio-transporte | idem, dentro de "Auxílios e benefícios" se existir | não conferido |
| Auxílio-moradia | coluna "Auxílio Moradia" do eGesp em R$ 0,00 nos 8 meses | não conferido (a coluna existe e veio zerada; se é zero publicado ou célula vazia, só o bruto diz) |
| Auxílio-saúde | dentro de "Auxílios e benefícios", R$ 0,00 | não conferido |
| Auxílio pré-escolar | idem | não conferido |
| Ajuda de custo ("auxílio-paletó", o "auxílio terno") | no Congresso é a ajuda de custo no início e no fim do mandato (Decreto Legislativo 172/2022, como a ficha do Senado registra). Ministro do STF não tem mandato com início e fim desse tipo; nenhuma regra equivalente está no repositório | não conferido (pesquisar ato do STF; até lá, nenhuma linha) |
| Diárias | não estão na folha do eGesp; as do TSE aparecem para Toffoli e Nunes Marques | não conferido (relatório de diárias do STF) |
| Passagens | nada no repositório | não conferido |
| Carro oficial | nada no repositório | não conferido |
| Segurança | nada no repositório | não conferido |
| Imóvel funcional | nada no repositório | não conferido |

## 6. A equipe de cada gabinete

**Não conferido.** A régua do Senado (Q67) soma o salário bruto de todos os lotados no gabinete e nos escritórios do senador. Para
usar a mesma régua no STF é preciso a folha dos servidores com a lotação de cada um ("Gabinete do Ministro X", e o que a
presidência acrescenta: o gabinete da presidência e as unidades ligadas a ela). O coletor de hoje filtra a folha do eGesp por
"Situação Funcional = MINISTRO" e lê só nome e colunas de rendimento, então mesmo que a mesma página traga os servidores, o
repositório não tem o dado, e não dá para saber daqui se a página publica a lotação. A spec propõe a coleta e a regra de exibição.

## 7. Os outros tribunais: STJ, TST, STM e TSE

Fonte de todos: o arquivo de cada tribunal no painel do CNJ (Anexo VIII da Portaria CNJ 63/2017, abas Contracheque, Direitos
Pessoais, Indenizações, Direitos Eventuais), baixado pelo coletor em 2026-10-21. O painel e os portais dos tribunais não abriram
hoje, então a pergunta "o zero vem da fonte ou do coletor" só tem resposta parcial: o que o arquivo mostra, e o que no coletor
poderia produzir um zero sem aviso.

| Tribunal | Pessoas | Meses no arquivo | Colunas com R$ 0,00 para todos em 2026 |
|---|---:|---|---|
| STJ | 32 | jan, abr, mai, jun | Auxílio Pré-escolar, Auxílio Saúde, Auxílio Natalidade, Auxílio Moradia, Ajuda de Custo, Gratificação natalina, Antecipação de gratificação natalina, Substituição, Gratificação por exercício cumulativo, JETON, Direitos eventuais: outra, Remuneração do órgão de origem |
| TST | 27 | jan a set | Auxílio Saúde, Gratificação natalina, Substituição, JETON |
| STM | 15 | fev, mai, jun, jul, ago | Diárias, Auxílio Saúde, Auxílio Natalidade, Auxílio Moradia, Ajuda de Custo, Antecipação de férias, Gratificação natalina, Substituição, Gratificação por encargo Curso/Concurso, Pagamentos retroativos, JETON, Remuneração do órgão de origem |
| TSE (3 juristas) | 3 | jan, mar a ago | as que não aparecem não são gravadas: o coletor guarda só as colunas com valor para cada pessoa do TSE |

O que se lê disso:

1. **Auxílio Saúde é R$ 0,00 para todos os ministros dos três tribunais.** Pode ser a fonte (o tribunal lança o auxílio em outra
   coluna, como o STM lança "Auxílio-alimentação-ativo" em "Direitos eventuais: outra") ou o coletor: ele procura cada coluna pelo
   título exato (`h == col`) e **não confere se achou cada título**; um título escrito de outro jeito zeraria a coluna sem aviso.
   Sem o arquivo bruto, não dá para separar. A spec põe a conferência de títulos no coletor.
2. **Gratificação natalina é zero em todos**, e a antecipação aparece só no TST (2 pessoas) e no STM (10). No STJ os meses
   publicados no painel são só 4.
3. **Meses faltando:** o STJ enviou ao painel só 4 meses (registrado no `not_found`, com a aba Controle de Arquivos). **O STM
   tem só 5 meses no arquivo coletado (fev, mai, jun, jul e ago) e isso não está no `not_found`**; a ficha mostra os meses na nota de cada linha, mas a
   falta não é explicada. A spec acrescenta.
4. **A coluna "Indenizações: outra" pesa muito:** é diferente de zero para todos os ministros dos três tribunais, com média de
   R$ 24.205,73 por mês no STJ, R$ 12.053,31 no TST e R$ 37.568,83 no STM. O detalhe que o TST e o STM publicam nomeia, entre
   outras, "PVTAC - art. 3 Resolução Conjunta CNJ/CNMP 14/2026", "GECJAO", "Indenização de licença compensatória" e
   "Indenização de licença-prêmio". **O STJ não traz detalhe nessa coluna** no arquivo coletado. O coletor também **corta o detalhe em 300 caracteres**, e
   no STM ele aparece cortado no meio de uma rubrica.
5. **Valores negativos:** "Antecipação de férias" soma R$ -334.737,82 no TST em 2026 (12 pessoas), o desconto da antecipação. A
   página mostra um negativo como desconto e o subtrai do total, o que está certo se o adiantamento entrou como positivo em outra
   linha do mesmo período; se o adiantamento foi pago antes de janeiro de 2026, só o desconto entra na média de 2026, e o
   arquivo não diz quando foi. A spec trata.
6. **TST, conferência entre fontes:** o CSV do próprio TST e o Anexo VIII diferem em 31 de 206 pessoa-mês (fev 14, mar 2, mai 1,
   ago 13, set 1), já registrado no `not_found`; a causa não foi confirmada.
7. **Média por ministro, para situar:** STJ R$ 95.949,79, TST R$ 89.523,44, STM R$ 100.287,57 por mês, contra R$ 62.053,90 no STF
   (todas do arquivo, mesmo método: total do ano dividido pelos meses que cada tribunal publicou, diárias incluídas). A diferença
   está sobretudo nas colunas de indenizações e direitos pessoais que os três detalham e o STF publica zeradas ou não tem.
8. **Presidência:** o detalhe do TST e do STM traz "Representação magistrado presidente". No STF não há rubrica parecida na folha
   publicada (seção 3.1).

## 8. Cada número e texto da página que mudaria

Só o que o repositório já permite calcular, pelas recomendações da spec (nada muda antes da aprovação). O que depende da fonte
(auxílios, equipe, mês a mês) entra como linha nova "não conferido" ou "não publicado" e não tem número novo aqui.

| O quê | Antes | Depois | Por quê | Fonte |
|---|---|---|---|---|
| Férias, por mês, 8 ministros (todos menos Gilmar e Toffoli) | 1.931,92 | 1.931,93 | 15.455,40 / 8 = 1.931,925; arredondamento escrito, meio centavo para cima, que o leitor refaz à mão (spec, 2.4) | eGesp, total de jan a ago |
| Total por mês, Fachin, Cármen Lúcia, Fux | 62.805,71 | 62.805,72 | a linha de férias acima | idem |
| Total por mês, Moraes | 53.224,52 | 53.224,53 | idem | idem |
| Total por mês, Dino | 53.514,31 | 53.514,32 | idem | idem |
| Total por mês, Nunes Marques | 64.775,70 | 64.775,71 | idem | idem |
| Total por mês, Mendonça | 63.745,90 | 63.745,91 | idem | idem |
| Total por mês, Zanin | 51.196,00 | 51.196,01 | idem | idem |
| Total por mês, Gilmar e Toffoli | 73.023,68 e 72.641,75 | sem mudança | as médias deles não caem em meio centavo | idem |
| Soma dos 10; média; para a pessoa | 620.538,99; 62.053,90; 616.027,39 | 620.539,07; 62.053,91; 616.027,47 | soma das linhas acima | idem |
| STJ, linhas em meio centavo | 29 linhas arredondadas para cima ou para baixo conforme o binário | 14 delas mudam R$ 0,01 | a mesma regra escrita | painel do CNJ |
| "No cargo desde", Fachin | 16/06/2015 | "No STF desde 16/06/2015" e "Presidente do STF desde 29/09/2025" | a primeira é a posse no tribunal | eGesp (admissão); STF Notícias (presidência) |
| "No cargo desde", demais ministros | data de admissão | "No STF desde" a mesma data | o rótulo diz o que a data é | eGesp |
| "Auxílios e benefícios", "Indenizações", "Auxílio Moradia" e as outras 3 colunas zeradas | "não recebe" ✗ | "R$ 0,00 na folha publicada" | um zero na folha não prova que a pessoa não recebe; a spec só usa ✗ "não recebe" com ato ou página que o diga | eGesp |
| Linhas do TSE (jeton, gratificação eleitoral, diárias) | misturadas às do STF, média de 7 meses só na nota | um bloco "Pago pelo TSE", com os meses no título | duas janelas diferentes somadas precisam aparecer como tal | painel do CNJ |
| Linhas novas: equipe do gabinete, diárias, passagens, carro oficial, segurança, imóvel funcional, cada auxílio | não aparecem | "não conferido" até a recoleta; depois valor com fonte, "não recebe" com ato, ou "não publicado" com as URLs tentadas | os itens pedidos | seção 5 |
| Marca "parcial" no total | não aparece | aparece enquanto houver linha sem dado | regra que a página já usa para linha desconhecida | página |
| STM, meses faltando | só na nota de cada linha | também no "não publicado" da ficha | jan, mar, abr e set não estão no arquivo coletado do painel | painel do CNJ |

A tabela "antes e depois" de Fachin, Dino, Moraes e Gilmar está na descrição do pull request.

## 9. Achados no código (coletor e construtor)

1. `num()` devolve 0,0 para texto ilegível (`except ValueError`), sem aviso: um zero na tela pode ser um erro de leitura.
2. `cnj_pay()` procura cada coluna pelo título exato e não confere se achou cada uma; um título mudado zera a coluna sem aviso.
3. `stf_pay()` não grava o mês a mês; `build_items()` grava só total, média e rótulo dos meses. Sem o mês a mês não dá para mostrar
   "pago em agosto", conferir a soma dos meses (o Executivo confere) nem refazer a média de outra forma.
4. A média usa `round()` de ponto flutuante: 37 linhas em meio centavo exato (8 no STF, 29 no STJ) vão para cima ou para baixo
   conforme a representação binária.
5. `since` do STF é a data de admissão e a ficha a chama de "No cargo desde".
6. O detalhe das colunas "outra" é cortado em 300 caracteres.
7. As linhas do TSE são divididas pelos 7 meses do TSE e somadas às do STF, divididas por 8, sem rótulo no total.
8. O `not_found` não registra os meses que o STM não enviou.
9. A página transforma `uses: false` (total zero) em "não recebe" ✗.

Nenhum desses achados muda um número sem a fonte, exceto o arredondamento. Todos estão na spec.

## 10. Não conferido

Todos os hosts abaixo responderam, em 2026-10-22 às 17:31 e às 17:33 UTC, `curl: (56) CONNECT tunnel failed, response 403` (o
proxy de saída deste ambiente recusou o túnel; código HTTP 000 no curl). A regra do pedido é não contornar.

| Host | O que seria conferido |
|---|---|
| `egesp-portal.stf.jus.br` | folha de jan a set de 2026, mês a mês, de cada ministro (`/transparencia/rendimento_folha`); a legenda de cada coluna; setembro; a lotação dos servidores de cada gabinete |
| `transparencia.stf.jus.br` | relatórios de diárias, passagens, benefícios, veículos e imóveis do STF |
| `portal.stf.jus.br` | composição atual; atos de auxílios do STF |
| `noticias.stf.jus.br` | a data da presidência de Fachin (29/09/2025) e a da vice-presidência de Moraes |
| `paineis.cnj.jus.br` | Anexo VIII de STJ, TST, STM e TSE; os títulos exatos das colunas |
| `atos.cnj.jus.br` | Portaria Conjunta nº 3/2025 (auxílio-alimentação) e o ato de 2026 |
| `www.planalto.gov.br` | Lei 14.520/2023; Constituição, art. 93, V; a lei da magistratura (férias) |
| `web.archive.org` | composição do TSE (cópia de 2026-09-03) |
| `www.stj.jus.br` | ministros do STJ; tabela de antiguidade |
| `www.tst.jus.br`, `transparencia-remuneracao.tst.jus.br` | ministros e CSV de remuneração do TST |
| `www.stm.jus.br`, `dspace.stm.jus.br` | ministros e atas do STM |
| `www.tse.jus.br` | composição e pagamentos do TSE |

Também não conferido, por não estar no repositório: os arquivos brutos de 2026-10-21 (`data/federal/raw-pay/`, fora do git por
decisão do projeto). Com eles, os itens 1, 2 e 4 da seção 9 e o mês a mês da seção 4 se resolvem sem rede.

## 11. Como refazer

```
python3 docs/research/judiciario-auditoria-2026-10-22/check_stf_sums.py                 # PASS, saída 0
python3 docs/research/judiciario-auditoria-2026-10-22/check_stf_sums.py --plant         # FAIL, saída 1 (controle)
python3 docs/research/judiciario-auditoria-2026-10-22/check_stf_sums.py --plant-screen  # FAIL, saída 1 (controle)
```

Os valores "lidos na tela" que a checagem usa foram lidos num build local de `main` em `615f7f3`, abrindo
`BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html#p=stf:edson-fachin` (e Dino, Moraes, Gilmar, `senado:3830`).
