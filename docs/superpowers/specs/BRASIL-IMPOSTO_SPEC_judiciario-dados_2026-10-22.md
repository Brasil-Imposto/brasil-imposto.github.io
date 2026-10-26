# Brasil-Imposto: dados do Poder Judiciário em "Os 3 Poderes", correção e melhoria

Status: **aprovada em 2026-10-22 com todas as recomendações (D154, Q72 a Q79).** Primeiro entra o que os dados do repositório
já permitem; a coleta nova espera os hosts dos tribunais (pergunta 7). Base: a auditoria `docs/research/BRASIL-IMPOSTO_RESEARCH_judiciario-remuneracao-auditoria_2026-10-22.md`.

### Summary (English)

The audit found the STF numbers on screen correct to the cent against what the collector read, and misleading in four ways:
one-off payments are spread over the published months without saying so on the total, a zero in a payroll column is shown as
"não recebe", Fachin's STF admission date reads as his presidency, and the Senate side counts an office team that the STF side
does not measure. This spec keeps the arithmetic, keeps the monthly average (the rule the Senate and Câmara sheets already use),
and changes what is collected and how it is labelled: (1) every item keeps its month-by-month values, so one-off payments say
when they were paid; (2) money is rounded with a written rule (decimal, half up); (3) the TSE's payments become their own block
with their own months; (4) "para a pessoa" and "mandato e equipe" follow the Senate's rule, with the office staff of each
minister by lotação and what the presidency adds; (5) both dates (in the court since, president since) appear; (6) each
requested allowance gets its own row as received with value, not received with the act, or not published with the URLs tried;
(7) the collector fails loudly instead of writing a silent zero. Tests come first, each with a planted failure. Collecting needs
the court hosts, which this cloud environment cannot reach (403 on CONNECT): the collection runs where they open.

## 1. Escopo

- **Vale para:** os ministros do STF primeiro; depois, com as mesmas regras, STJ, TST, STM e os juristas do TSE.
- **Não muda:** as contas da página (somas e médias que já fecham), o desenho da ficha, as fichas do Legislativo e do Executivo
  (fora a pergunta 6 da seção 9, que só pergunta).
- **Ordem:** testes primeiro (seção 7), depois coletor, construtor e página, um pull request por parte (seção 8).

## 2. O que "por mês" quer dizer

### 2.1 As três opções

| | Como calcula | Exemplo, Gilmar, férias (R$ 92.429,97 em 2026) | A favor | Contra |
|---|---|---|---|---|
| **(a) Meses em que foi pago** | total do item dividido pelos meses em que o item teve valor | se pago em 2 meses, R$ 46.214,99 "por mês" | mostra o tamanho real de cada pagamento | não é mensal: soma pagamentos de tamanhos diferentes e um total "por mês" com ele não fecha com nada |
| **(b) Média dos meses publicados, com o rótulo** (o método de hoje) | total do item dividido pelos meses que o tribunal publicou (8 no STF) | R$ 11.553,75 por mês | é o que o Senado e a Câmara já fazem na cota e na equipe (Q65); a soma das linhas fecha com o total de 2026 dividido por 8 | espalha o que se paga uma ou duas vezes por ano, se o rótulo não disser |
| **(c) Direito anual dividido por 12** | o que a lei dá no ano, sobre 12 | depende da lei, não do que foi pago | lisa, comparável entre cargos | é estimativa de direito, não dado pago: o que foi pago a mais ou a menos some, e exige ler leis que hoje não abriram; contraria "nada de afirmação que o dado não sustenta" |

### 2.2 Recomendação: (b), com o mês a mês à vista

- O total da ficha continua a **média dos meses publicados**, e passa a dizer isso no próprio total: "Média por mês, jan a ago
  2026" no lugar de "Total por mês" (o rótulo de grupo de D143 continua: soma ou média).
- Cada linha separa o que é de todo mês do que é do ano:
  - **Todo mês** (o item teve valor em todos os meses publicados): a média, como hoje.
  - **Pagamento do ano** (o item teve valor em parte dos meses): a média, e embaixo "pago em <meses>: R$ <valor de cada mês>",
    por exemplo "pago em jul: R$ 23.183,09". O leitor vê que os 2.897,89 da gratificação natalina são meio 13º pago num mês, e
    que os 11.553,75 de férias de Gilmar são R$ 92.429,97 pagos em <meses>.
- Isso exige guardar o mês a mês de cada item (seção 6.1). Os números de hoje não mudam com (b), só ganham os meses.

### 2.3 Fontes com janelas diferentes
As linhas do TSE (jeton, gratificação eleitoral, diárias) viram um **bloco próprio "Pago pelo TSE"**, com os meses no título
("média de jan, mar a ago 2026; fevereiro não publicado pelo TSE"). O total da ficha soma as duas médias e diz "soma da média
do STF (8 meses) com a do TSE (7 meses)". A ficha do Senado já mostra janelas diferentes, cada uma com o rótulo; aqui o rótulo
vai também para o total.

### 2.4 Arredondamento
Todo valor em reais é calculado em decimal (`decimal.Decimal`, nunca ponto flutuante) e arredondado ao centavo **meio para
cima** (`ROUND_HALF_UP`), a regra que o leitor refaz à mão. O total é a soma das linhas como aparecem na tela. Efeito medido na
auditoria: R$ 0,01 a mais na linha de férias de 8 ministros do STF e 14 linhas do STJ; Gilmar e Toffoli não mudam (seção 8 da
auditoria).

## 3. Para a pessoa e mandato e equipe, pela regra do Senado

A regra do Senado (Q61, Q67): **para a pessoa** é o que a pessoa recebe; **mandato e equipe** é o que paga a equipe e as despesas
do cargo. No Judiciário:

| Vai para | Itens |
|---|---|
| **Para a pessoa** | subsídio, vantagens pessoais, abono de permanência, férias, gratificação natalina, exercícios anteriores, cada auxílio pago em dinheiro (alimentação, transporte, saúde, pré-escolar, moradia), ajuda de custo, jeton e gratificação eleitoral do TSE, e as colunas equivalentes do Anexo VIII nos outros tribunais |
| **Mandato e equipe** | diárias (do tribunal e do TSE), passagens, **equipe do gabinete** (seção 3.1) e, para o presidente, **o que a presidência acrescenta** (seção 3.2) |
| **Mostrado, fora da soma** | o que não tem valor em reais publicado por pessoa: carro oficial, segurança, imóvel funcional, como o "imóvel funcional: usa, sem valor em reais publicado" da ficha do Senado |

### 3.1 Equipe do gabinete
- **A mesma medida do Senado:** a soma dos salários brutos de todos os servidores lotados no gabinete do ministro, média dos
  meses publicados, com o número de pessoas e o mês a mês ("salários brutos de N pessoas do gabinete, média de jan a ago 2026").
- **Fonte:** a folha do STF com a lotação de cada servidor. Se a folha publicada não trouxer a lotação, a linha diz "não
  publicado" com as URLs tentadas; nunca uma estimativa por cargo.
- Nos outros tribunais, a mesma regra, cada um com a sua fonte; o que não for publicado por gabinete fica "não publicado".

### 3.2 O que a presidência acrescenta
- Na folha de 2026 do presidente, nada a mais (o total de Fachin é igual ao de Cármen Lúcia e ao de Fux); a ficha diz isso numa
  nota: "a folha publicada não traz pagamento pela presidência".
- A estrutura da presidência (o gabinete da presidência e as unidades ligadas a ela) entra em "mandato e equipe" do presidente,
  pela mesma medida da 3.1, se a fonte publicar a lotação; senão, "não publicado".
- O mesmo para a vice-presidência, se a fonte separar.

## 4. Datas

- **"No STF desde"** (a data de admissão do eGesp, que é a posse no tribunal) para os 10, no lugar de "No cargo desde".
- **"Presidente do STF desde 29/09/2025"** para Fachin, com a fonte (STF Notícias, já no repositório em `positions-2026.json`),
  relida na recoleta. **"Vice-Presidente do STF desde"** para Moraes, de página oficial do STF; sem ela, a linha não aparece e a
  falta vai para o "não publicado" da ficha.
- Os outros tribunais seguem a mesma regra: posse no tribunal e, para quem tem cargo de direção, a data do cargo, cada uma com
  a fonte. A data do TSE continua no texto do biênio, como hoje.
- No modelo de dados: `court_since` e `office_since` (com `office_source`), no lugar de `since`.

## 5. As linhas novas da ficha

Cada linha tem um destes quatro estados, e só estes chegam à tela:

| Estado | Na tela | Exige |
|---|---|---|
| **recebe** | o valor por mês, ✓, a nota com o ano e os meses | valor publicado em fonte oficial |
| **não recebe** | "não recebe", ✗ | ato ou página oficial que diga que o ministro não recebe, com o link |
| **zero na folha** | "R$ 0,00 na folha publicada", sem ✓ nem ✗ | a coluna da folha publicada veio 0,00 em todos os meses (lida como "0,00", nunca vazia) |
| **não publicado** | o selo "não publicado" e o motivo | as URLs tentadas, gravadas no `not_found` |

O estado interno "não conferido" (fonte que não abriu) **nunca chega à tela**: o build falha enquanto houver um (seção 7).

Linhas, na ordem da ficha (STF; nos outros tribunais, as colunas do Anexo VIII já cobrem parte):

| Chave | Rótulo | Vai para |
|---|---|---|
| `food_allowance` | Auxílio-alimentação | para a pessoa |
| `transport_allowance` | Auxílio-transporte | para a pessoa |
| `health_allowance` | Auxílio-saúde | para a pessoa |
| `preschool_allowance` | Auxílio pré-escolar | para a pessoa |
| `housing` | Auxílio-moradia (já existe) | para a pessoa |
| `relocation` | Ajuda de custo | para a pessoa |
| `per_diem` | Diárias | mandato e equipe |
| `flights` | Passagens | mandato e equipe |
| `office_staff` | Equipe do gabinete | mandato e equipe |
| `presidency_staff` | Estrutura da presidência (só o presidente) | mandato e equipe |
| `official_car` | Carro oficial | fora da soma |
| `security` | Segurança | fora da soma |
| `official_residence` | Imóvel funcional | fora da soma |

- **"Auxílio-paletó":** é a ajuda de custo do Congresso no início e no fim do mandato (Decreto Legislativo 172/2022, como a ficha
  do Senado já mostra). A linha `relocation` responde por ela no STF: o valor, se houver; "não recebe" com o ato, se houver um que
  diga; senão "não publicado".
- As colunas de hoje do eGesp continuam, com o estado "zero na folha" no lugar de "não recebe" quando vierem 0,00.
- Uma célula vazia não é zero: a linha fica "não publicado", com a página da folha como URL tentada.
- Enquanto houver linha "não publicado", o total leva a marca "parcial" que a página já usa.

## 6. Mudanças no pipeline

### 6.1 Coletor (`collect-judiciary-2026.py`)
1. **Mês a mês em tudo:** cada item grava `by_month` (`{"01": "46366.19", ...}`) e, ao lado, o texto da célula como veio
   (`raw_by_month`), para o STF e para o painel do CNJ. O construtor passa a conferir, como já faz no Executivo, que a soma dos
   meses é o total do ano.
2. **Leitura estrita:** `num()` aceita só número vazio, "0", "0,00" e valores no formato brasileiro; qualquer outro texto para o
   coletor com o nome do arquivo, a linha e a coluna. Vazio e zero ficam diferentes no dado (`null` contra `0`).
3. **Títulos conferidos:** cada coluna esperada (as 11 do eGesp, as de cada aba do Anexo VIII) tem de ser achada em cada arquivo;
   faltando uma, o coletor para e diz qual.
4. **Total da própria fonte:** onde a fonte publica um total por pessoa e mês ("Total de Rendimentos" no Anexo VIII; a coluna
   equivalente do eGesp, se houver), a soma dos componentes lidos tem de bater com ele ao centavo; a diferença para o coletor e é
   registrada no `not_found`, nunca absorvida.
5. **Equipe do gabinete:** a folha do STF lida inteira, não só "MINISTRO"; cada servidor somado ao gabinete da sua lotação; o
   mesmo para a presidência. Se a lotação não vier na fonte, "não publicado" com as URLs.
6. **Outros relatórios do STF:** diárias, passagens, benefícios, veículos e imóveis, cada um com a URL, o período e a data de
   leitura; cada auxílio pedido resolvido em um dos quatro estados da seção 5.
7. **Datas:** `court_since` (admissão) e `office_since` com a fonte (seção 4).
8. **Detalhe completo:** o texto das colunas "outra" sem corte no dado; a página decide quanto mostrar.
9. **Meses que faltam:** cada tribunal com mês faltando entre janeiro e o último publicado vai para o `not_found` (hoje falta o
   STM).
10. **Arredondamento:** decimal, meio para cima (seção 2.4).
11. **Setembro de 2026 em diante:** o coletor tenta cada mês até o atual e registra o código de resposta de cada tentativa.

### 6.2 Construtor (`build-tres-poderes-r3-data.py`)
- `NOT_OWN` passa a `{"per_diem", "tse_per_diem", "flights", "office_staff", "presidency_staff"}`; uma lista nova `NO_VALUE` com
  `{"official_car", "security", "official_residence"}`, mostradas fora da soma.
- O bloco do TSE separado (seção 2.3), com os meses dele.
- O estado de cada linha (recebe, não recebe, zero na folha, não publicado) vem pronto do dado, não deduzido na página.

### 6.3 Página (`os-3-poderes.html`)
- "Média por mês, jan a ago 2026" no total; "pago em <meses>" sob cada pagamento do ano; o bloco "Pago pelo TSE".
- O estado "zero na folha" ("R$ 0,00 na folha publicada", sem marca); "não recebe" só com o link do ato.
- "No STF desde" e "Presidente do STF desde", cada uma com a fonte.
- As linhas novas da seção 5, a divisão "para a pessoa / mandato e equipe" e a marca "parcial".
- O texto da fonte no pé da ficha diz também: "Pagamentos do ano aparecem na média e com o mês em que foram pagos."

### 6.4 Esquema e exportação
`schemas/` ganha os campos novos (`by_month`, `raw_by_month`, `state`, `court_since`, `office_since`, `office_source`) e a
exportação de entidades passa a validá-los; os tipos do site são gerados de novo (fase B0).

## 7. Testes, cada um com um controle que tem de falhar

| Teste | Confere | Controle plantado |
|---|---|---|
| Soma dos meses | `by_month` soma o total do ano, item por item | um mês com R$ 0,01 a mais |
| Total da fonte | componentes somam o "Total de Rendimentos" da fonte, pessoa por pessoa e mês por mês | um componente com R$ 0,01 a mais |
| Leitura estrita | um texto ilegível numa célula para o coletor | uma célula "R$ 1.784,4x" num arquivo de teste |
| Títulos | falta de uma coluna esperada para o coletor | um arquivo de teste com "Auxílio-saúde (R$)" no lugar de "Auxílio Saúde (R$)" |
| Arredondamento | 15.455,40 / 8 dá 1.931,93; nenhum `float` no caminho do dinheiro | um valor arredondado em ponto flutuante (1.931,92) |
| Soma à mão | o total da ficha é a soma das linhas como aparecem na tela, para cada ministro (a checagem da auditoria, `check_stf_sums.py`, vira teste) | R$ 0,01 num item e R$ 0,01 num total lido na tela |
| Para a pessoa e mandato | as chaves de mandato e equipe e as fora da soma estão onde a seção 3 diz | `per_diem` marcado como da pessoa |
| Estados | nenhum "não recebe" sem link de ato; nenhum "zero na folha" de célula vazia; nenhum "não conferido" no dado publicado (o build falha) | um "não recebe" sem link; um "não conferido" deixado no arquivo |
| Datas | Fachin mostra as duas datas, cada uma com fonte; nenhuma ficha diz "No cargo desde" | a data da presidência apagada |
| Meses que faltam | todo mês faltando de cada tribunal está no `not_found` | um mês tirado do arquivo do STM de teste |
| Tela | sonda de texto visível: "não recebe" e "não publicado" só onde o dado manda; capturas das fichas de Fachin, Dino, Moraes e Gilmar em 1440 e 420 px, olhadas | a sonda de hoje com `--control` |
| Neutralidade | o texto novo não tem "supersalário", "penduricalho" nem travessões | uma palavra plantada |

Os testes usam arquivos de teste pequenos, recortados dos arquivos oficiais (algumas linhas de um mês), guardados com a URL e a
data de leitura; os arquivos brutos inteiros continuam fora do git.

## 8. Ordem do trabalho e rede

1. **Testes** (seção 7), com os arquivos de teste recortados.
2. **Coletor**, um pull request: 6.1, itens 1 a 4 e 7 a 11 (o que muda a leitura do que já é coletado).
3. **Coletor, coleta nova**, um pull request: 6.1, itens 5 e 6 (equipe e outros relatórios).
4. **Construtor e esquema**, um pull request: 6.2 e 6.4.
5. **Página**, um pull request: 6.3, com as capturas.
6. **STJ, TST, STM e TSE** com as mesmas regras, um pull request.

Cada um com `git commit -s`, os testes e as sondas de hoje passando. **A coleta precisa dos hosts oficiais**, que este ambiente
na nuvem não alcança (403 no CONNECT do proxy em 2026-10-22, lista na seção 10 da auditoria): os passos 2 e 3 rodam onde eles
abrem (pergunta 7).

## 9. Perguntas ao mantenedor

Cada uma com a recomendação marcada; o que não for respondido segue a recomendação só depois da aprovação desta spec.

1. **"Por mês":** (a) meses em que foi pago; **(b) média dos meses publicados, com o rótulo no total e o mês de cada pagamento do
   ano ★**; (c) direito anual dividido por 12. Recomendo (b): é a régua que a Câmara e o Senado já usam, a soma fecha à mão, e o
   mês de cada pagamento explica Gilmar e Toffoli sem estimar nada.
2. **Arredondamento:** **meio para cima ★** ou meio para o par. Recomendo meio para cima: é o que o leitor faz à mão com uma
   calculadora (muda R$ 0,01 em 8 ministros do STF e 14 linhas do STJ).
3. **Um zero na folha:** **"R$ 0,00 na folha publicada", sem ✗ ★**, ou manter "não recebe". Recomendo o primeiro: o zero é o que
   a fonte diz; "não recebe" afirma mais do que ela.
4. **Equipe do gabinete:** **a mesma medida do Senado, todos os lotados, inclusive de carreira ★** (Q67), ou só os cargos em
   comissão. Recomendo a do Senado, para que os dois lados meçam a mesma coisa.
5. **TSE:** **bloco próprio, com os meses no título e o total dizendo que soma duas médias ★**, ou dividir o TSE pelos 8 meses do
   STF (supõe zero em fevereiro, que o TSE não publicou). Recomendo o bloco.
6. **A régua do salário no Legislativo** (fora desta spec, só a pergunta): a ficha do Senado mostra o valor do cargo e a do STF a
   média da folha, então "para a pessoa" não compara igual. **Uma spec própria para usar a folha também nas fichas do Senado e da
   Câmara ★**, ou deixar como está e dizer na ficha qual régua cada uma usa. Recomendo a spec própria, depois desta.
7. **Onde coletar:** **acrescentar os hosts da seção 10 da auditoria à lista de rede do ambiente na nuvem ★** (configuração que
   só o mantenedor pode mudar), ou rodar a coleta na máquina do mantenedor e trazer o resultado. Recomendo a lista de rede, para a
   coleta e os testes rodarem no mesmo lugar.
8. **Ordem:** **STF primeiro, os outros tribunais no fim ★**, ou os cinco juntos. Recomendo o STF primeiro: é a pergunta aberta,
   e as regras saem testadas antes de chegar aos outros.

As respostas estão em D154 e nas perguntas Q72 a Q79 de `docs/decisions/README.md`.

## 10. Fora desta spec

- As fichas do Senado e da Câmara (pergunta 6).
- Valores de 2019 a 2025 do Judiciário (a página de hoje mostra 2026).
- Explicar na tela o que cada rubrica paga (por exemplo, o que é "Vantagens Pessoais") além do que a própria fonte disser: só
  entra com a legenda ou o ato oficial.
- Qualquer adjetivo sobre os valores: a ficha mostra o número, a fonte e o método.
