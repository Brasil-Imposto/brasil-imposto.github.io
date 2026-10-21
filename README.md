# Brasil-Imposto

Mapa cívico, apartidário e de código aberto que mostra, com dados oficiais, como o imposto pago no Brasil é arrecadado e
redistribuído entre a União, os estados e os municípios, quem ocupa cada cargo dos três Poderes e quanto recebe, e para onde vai
o dinheiro. Cada número tem a fonte oficial ao lado.

**Estado:** primeira versão pública (v1), ainda em prévia. As páginas são arquivos HTML estáticos montados a partir dos dados
deste repositório.

## As páginas

| Página | O que mostra |
|---|---|
| Início (`docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html`) | O mapa do Brasil com o saldo de cada estado com a União (o que foi para a União menos o que voltou), por mês, ano ou mandato desde 2019; as contas do Brasil; a janela de cada estado, com os municípios de SC e RS e as Regiões Administrativas do DF |
| Os 3 Poderes (`..._tres-poderes-round-3_2026-10-21.html`) | A árvore dos cargos da União e a ficha de cada pessoa: os 513 deputados, os 81 senadores, o presidente, o vice, os ministros de Estado e os ministros dos tribunais superiores, com salário, cada auxílio e o que cada um usou em 2026; para cada parlamentar, cada projeto que apresentou e o que aconteceu com ele |
| Como o dinheiro anda (`..._como-o-dinheiro-anda-round-1_2026-10-21.html`) | Quem cobra cada imposto, as partes que a Constituição manda passar de um governo para o outro, quem gasta o quê e o que vira dívida, com os números de 2025 |

## Como abrir na sua máquina

Só é preciso Python 3, sem pacotes extras:

```
python3 docs/superpowers/tools/build-cases.py
python3 docs/superpowers/tools/build-standalone-data.py
python3 docs/superpowers/tools/build-simulation.py
python3 docs/superpowers/tools/build-platform-preview.py
```

Depois, abra os arquivos das páginas acima no navegador pelo caminho do arquivo. Os pacotes `assets/bi-data.js` e
`assets/bi-geo*.js` não ficam no repositório: são refeitos por esses comandos a partir de `data/`.

## De onde vêm os números

Receita Federal (arrecadação por estado), Tesouro Nacional (Resultado do Tesouro Nacional e SICONFI), Portal da Transparência
(gastos, repasses, folha, cartões e viagens), INSS, MDS, IBGE (população e PIB), Câmara dos Deputados, Senado Federal, CNJ e os
tribunais superiores, TSE, Planalto (leis e Constituição) e os portais dos estados e municípios cobertos. Os scripts que buscam e
montam cada base estão em `data/scripts/` e `docs/superpowers/tools/`; as pesquisas que explicam cada escolha estão em
`docs/research/`, e as decisões do projeto em `docs/decisions/README.md`.

Regras de método que aparecem na tela:

- **Sem informação de estado:** o dinheiro que a fonte oficial não põe em nenhum estado fica num bloco próprio, nunca espalhado
  pelos estados.
- **DF, estimativa:** a Receita registra no DF o imposto que órgãos e empresas com sede em Brasília retêm ou pagam pelo país
  inteiro (Lei 9.779/1999, art. 15). No mapa, em cada imposto o DF conta no máximo a sua parte no PIB do Brasil (IBGE); o que
  passa disso vai para o bloco da União. A outra estimativa do saldo são os meses de fevereiro de 2025 a janeiro de 2026, em que
  a Receita lançou no DF a arrecadação de outros estados; nos dois casos a tela diz que é estimativa.
- **Repasse não é gasto:** dinheiro que só passa de um governo para outro não conta como gasto de quem só repassou.

## Neutralidade

Só dados oficiais, com fonte; nenhum chamado ao voto; o mesmo tratamento para qualquer governo e qualquer partido; pessoas
aparecem só com o papel que têm num documento oficial. Cada página tem "Pedir correção".

## Como ajudar

Abra uma issue para corrigir um número (com o link da fonte oficial com o valor certo) ou para propor uma fonte, um estado ou um
caso. Mudanças entram por pull request. Veja `CONTRIBUTING.md`.

## Licenças

Código: AGPL-3.0 (`LICENSE`). Dados publicados em `data/` e textos: CC BY 4.0 (`LICENSE-DATA`), citando "Fonte: <órgão>; dados
tratados pelo Brasil-Imposto". O dado público de origem segue as regras de cada órgão. Fotos e bandeiras: a licença e o crédito de
cada arquivo estão junto deles.

## In English

Brasil-Imposto is a civic, nonpartisan, open-source map of Brazilian public money built only from official data: how federal,
state and municipal taxes are collected and shared, what each federal officeholder is paid and uses, and where the money goes.
The pages are static HTML built from `data/` with Python 3 and no extra packages (commands above). Code is AGPL-3.0; data and
texts are CC BY 4.0. Issues and pull requests are welcome, in Portuguese or English; every number needs its official source.
