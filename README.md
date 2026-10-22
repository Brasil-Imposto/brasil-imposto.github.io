# Brasil-Imposto

Mapa cívico, apartidário e de código aberto que mostra, com dados oficiais, como o imposto pago no Brasil é arrecadado e
redistribuído entre a União, os estados e os municípios, quem ocupa cada cargo dos três Poderes e quanto recebe, e para onde vai
o dinheiro. Cada número tem a fonte oficial ao lado.

**Site:** <https://brasil-imposto.github.io>

**Estado:** primeira versão pública (v1). As páginas são arquivos HTML estáticos montados a partir dos dados deste repositório;
o site definitivo, em Astro, está em construção (veja "Estado do projeto").

## As páginas

| Página | O que mostra |
|---|---|
| [Início](https://brasil-imposto.github.io/) (`docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html`) | O mapa do Brasil com o saldo de cada estado com a União (o que foi para a União menos o que voltou), por mês, ano ou mandato desde 2019; as contas do Brasil; a janela de cada estado, com os municípios de SC e RS e as Regiões Administrativas do DF |
| [Os 3 Poderes](https://brasil-imposto.github.io/BRASIL-IMPOSTO_DESIGN_tres-poderes-round-3_2026-10-21.html) (`..._tres-poderes-round-3_2026-10-21.html`) | A árvore dos cargos da União e a ficha de cada pessoa: os 513 deputados, os 81 senadores, o presidente, o vice, os ministros de Estado e os ministros dos tribunais superiores, com salário, cada auxílio e o que cada um usou em 2026; para cada parlamentar, cada projeto que apresentou e o que aconteceu com ele |
| [Como o dinheiro anda](https://brasil-imposto.github.io/BRASIL-IMPOSTO_DESIGN_como-o-dinheiro-anda-round-1_2026-10-21.html) (`..._como-o-dinheiro-anda-round-1_2026-10-21.html`) | Quem cobra cada imposto, as partes que a Constituição manda passar de um governo para o outro, quem gasta o quê e o que vira dívida, com os números de 2025 |

## Como abrir na sua máquina

Só é preciso Python 3, sem pacotes extras:

```
python3 docs/superpowers/tools/build-cases.py
python3 docs/superpowers/tools/build-standalone-data.py
python3 docs/superpowers/tools/build-simulation.py
python3 docs/superpowers/tools/build-platform-preview.py
```

Os pipelines de `pipelines/` e os testes usam Python 3.12 com as versões fixadas em `uv.lock`: instale o
[uv](https://docs.astral.sh/uv/) e rode `uv sync --locked`, depois `uv run python -m unittest discover -s pipelines/tests`.

Depois, abra os arquivos das páginas acima no navegador pelo caminho do arquivo. Os pacotes `assets/bi-data.js` e
`assets/bi-geo*.js` não ficam no repositório: são refeitos por esses comandos a partir de `data/`. O último comando monta a
página como ela vai ao site; com `--author-notes`, monta também as notas de trabalho da prévia num arquivo à parte, que não vai
ao git nem ao site.

## O site em Astro (em construção)

A pasta `site/` tem o esqueleto do site definitivo (fase B0): Astro 7, TypeScript estrito e uma página de prova que lê os
arquivos de cada entidade. Esses arquivos (`site/src/generated/entities/`) são gerados a partir de `data/` e conferidos com os
esquemas de `schemas/`, nunca versionados. Com Node 24 e o uv:

```
cd site && npm ci && npm run entities && npm run types && npm run check && npm test && npm run build
```

O site no ar continua sendo o das páginas acima até a fase B5.

## De onde vêm os números

Receita Federal (arrecadação por estado), Tesouro Nacional (Resultado do Tesouro Nacional e SICONFI), Portal da Transparência
(gastos, repasses, folha, cartões e viagens), INSS, MDS, IBGE (população e PIB), Câmara dos Deputados, Senado Federal, CNJ e os
tribunais superiores, TSE, Planalto (leis e Constituição) e os portais dos estados e municípios cobertos. Os scripts que buscam e
montam cada base estão em `pipelines/` e `docs/superpowers/tools/`; as pesquisas que explicam cada escolha estão em
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
aparecem só com o papel que têm num documento oficial. As regras completas, e quem decide no projeto, estão em
[`GOVERNANCE.md`](GOVERNANCE.md).

"Pedir correção" existe hoje em Os 3 Poderes, na ficha de cada pessoa: o botão abre o formulário de correção já preenchido com
o link da ficha. Nas outras páginas o botão ainda não existe ([issue #9](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/9));
até lá, use o formulário [Pedir correção](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/new?template=data-correction.yml)
direto.

## Estado do projeto

**Pronto (v1):**

- As três páginas acima, publicadas em <https://brasil-imposto.github.io> a cada mudança na `main`.
- O saldo dos 27 estados com a União por mês, ano e mandato desde 2019; as contas do Brasil; os municípios de SC e do RS e as
  Regiões Administrativas do DF.
- Os 3 Poderes: 722 fichas, com nenhum item "a coletar".
- O pacote de colaboração: formulários de issue, modelo de pull request, `CONTRIBUTING.md`, `GOVERNANCE.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md` e o check do DCO.

**O que vem:**

- O site em Astro, fase por fase, cada fase aprovada antes do código: [B0](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/2),
  [B1](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/3), [B2](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/4),
  [B3](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/5), [B4](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/6) e
  [B5](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/7) (Parte B de
  [`docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_v1-release-and-site-build_2026-10-22.md`](docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_v1-release-and-site-build_2026-10-22.md)).
- Nomes de arquivo e chaves de JSON em inglês ([#8](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/8)).
- "Pedir correção" em todas as páginas ([#9](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/9)).
- CI de proveniência ([#10](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/10)) e OpenSSF Scorecard
  ([#11](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/11)).
- Guias dos pipelines e documentos de fontes e créditos ([#12](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/12)).
- O salário de 3 ministros licenciados da Câmara ([#13](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/13)).
- Os municípios de outros estados ([#14](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/14)).

Todas as issues abertas: <https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues>.

## Como ajudar

Abra uma [issue](https://github.com/Brasil-Imposto/brasil-imposto.github.io/issues/new/choose) por um dos formulários: pedir
correção de um número (com o link da fonte oficial com o valor certo), acrescentar uma fonte, cobrir os municípios de um estado,
propor um caso, propor uma mudança de método ou relatar um defeito. Perguntas e ideias ficam em
[Discussions](https://github.com/Brasil-Imposto/brasil-imposto.github.io/discussions). Mudanças entram por pull request: veja
[`CONTRIBUTING.md`](CONTRIBUTING.md) e o [código de conduta](CODE_OF_CONDUCT.md). Falhas de segurança se relatam em privado
([`SECURITY.md`](SECURITY.md)).

## Licenças

Código: AGPL-3.0 (`LICENSE`). Dados publicados em `data/` e textos: CC BY 4.0 (`LICENSE-DATA`), citando "Fonte: <órgão>; dados
tratados pelo Brasil-Imposto". O dado público de origem segue as regras de cada órgão. Fotos e bandeiras: a licença e o crédito de
cada arquivo estão junto deles.

## In English

Brasil-Imposto is a civic, nonpartisan, open-source map of Brazilian public money built only from official data: how federal,
state and municipal taxes are collected and shared, what each federal officeholder is paid and uses, and where the money goes.
The site is <https://brasil-imposto.github.io>. The pages are static HTML built from `data/` with Python 3 and no extra
packages (commands above); an Astro site is being built phase by phase (issues #2 to #7). "Pedir correção" (request a
correction) exists today on the Os 3 Poderes sheets; the other pages get it in issue #9. Code is AGPL-3.0; data and texts are
CC BY 4.0. Issues and pull requests are welcome, in Portuguese or English; every number needs its official source. See
`GOVERNANCE.md`, `CODE_OF_CONDUCT.md` and `SECURITY.md`.
