# Brasil-Imposto: guia para quem contribui com agentes

Este arquivo vale para qualquer pessoa que trabalhe no repositório com um agente de código. Ele resume as regras do projeto;
as decisões completas estão em `docs/decisions/README.md` e os padrões aprendidos em `docs/ai/learned-patterns.md`.

## O projeto

Mapa cívico e apartidário que mostra, com dados oficiais, quanto cada estado envia à União e quanto recebe de volta, quem ocupa
cada cargo dos três Poderes e quanto recebe, e para onde vai o dinheiro do imposto. Cada número tem a fonte oficial ao lado.
Site: <https://brasil-imposto.github.io>.

## Stack e estrutura

- **Hoje:** páginas HTML estáticas em `docs/superpowers/previews/`, montadas por Python 3 a partir de `data/` pelos construtores
  de `docs/superpowers/tools/` (comandos no `README.md`). O workflow `.github/workflows/pages.yml` refaz e publica a cada push na
  `main`. O staging (`https://brasil-imposto.github.io/staging/`, público, com uma faixa de testes e `noindex`, D165) é
  publicado pelo repositório `Brasil-Imposto/staging` a partir do ramo `staging`. Os pacotes `assets/bi-data.js` e `assets/bi-geo*.js` não ficam no git: os construtores os refazem.
- **Em construção:** o site em Astro 7 com TypeScript estrito, three.js e um mapa SVG gerado no build, um JSON por entidade com
  JSON Schema, Python nos pipelines (Parte B de
  `docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_v1-release-and-site-build_2026-10-22.md`, uma issue por fase).
- `data/`: os dados publicados e os scripts que buscam e montam cada base (`pipelines/`).
- `docs/`: documentação em português, pesquisas (`docs/research/`), specs e planos (`docs/superpowers/`).

## Regras do projeto

- **Interface em português do Brasil; identificadores, nomes de arquivo, chaves de JSON e mensagens de commit em inglês.**
  Documentação em português, com resumo em inglês.
- **Texto neutro.** O site mostra dados e mecanismos, nunca chama ao voto. Saldo de um estado: "envia mais do que recebe" e
  "recebe mais do que envia". Nada de linguagem carregada.
- **Nenhum número sem fonte oficial**, com link, ano de referência e data da coleta. Sem fonte, não aparece.
- **Toda soma fecha à mão** com os valores como aparecem na tela, e os totais batem com o total oficial ao centavo.
- **Todo período funciona:** mês, ano e mandato, de 2019 ao último mês publicado. Um mês sem dado mostra o motivo.
- **DF por estimativa marcada:** a tela diz "estimativa" onde o DF é estimado, com o método ao lado.
- **Quem governava tem o mesmo tratamento para todos:** qualquer governo e qualquer partido aparecem do mesmo jeito.
- **Pessoas aparecem só com o papel que têm num documento oficial**, com o ato e o link.
- **Nada de afirmação que o dado não sustenta.** Quando os números não fecham, escreva "diferença sem explicação", nunca
  "desvio" sem decisão oficial.
- **Um item que o projeto não tem é "não publicado"**, nunca "a coletar".
- Prosa sem travessões.

## Fluxo de trabalho

1. Uma spec aprovada pela pessoa mantenedora antes de qualquer código (`docs/superpowers/specs/`).
2. Antes de começar, confira se a tarefa já tem dono: a seção "Quem faz o quê" da spec e as issues, pull requests e ramos abertos dela (`gh issue list --search`, `gh pr list --search`, `git ls-remote origin`). Se tiver, não comece outra: comente na issue. Um pull request aberto recebe commits só de quem o abriu, salvo pedido da pessoa mantenedora.
3. O plano, com uma tarefa por vez.
4. Testes primeiro.
5. Revisão, um assunto por pull request, commits assinados (`git commit -s`, DCO).
6. O pull request vai para o `staging` (o ramo padrão), nunca para a `main`. A `main` só recebe a promoção que a pessoa
   mantenedora aprova (`release: <data>`, squash) e, logo depois, o back-merge `main` para `staging` com merge commit; só nesses
   dois o `dco` aceita os commits que o GitHub fez ao mergear (#61). Uma funcionalidade nova entra com a sua chave em
   `data/features.json`, desligada na produção.

## Como conferir

- **Olhe a tela.** Capturas em 1440 e 420 px de largura, olhadas antes de entregar; nunca diga que algo foi conferido na tela sem
  ter olhado.
- **Toda checagem é provada com um controle que tem de falhar:** um erro plantado (um real a mais, um ponto sem ligação, uma nota
  plantada) que a checagem precisa pegar. Uma checagem que nunca falhou não foi testada.
- **O código de saída é o do comando real**, nunca o do último comando de uma cadeia com `|` ou `;`.
- Ferramentas prontas em `docs/superpowers/tools/`: `visible-text-probe.cjs` (texto visível da home em 19 períodos e dos 27
  estados, com `--audit` e o controle `--plant`), `site-check.cjs` (pedidos, erros, `body[data-ready="1"]`, rolagem horizontal
  e capturas, com `--control`), `tres-poderes-unknown-probe.cjs` (com `--control`), `tres-poderes-judiciary-check.cjs`
  (o STF na tela depois de D154, com `--control`), `overlay-check.cjs` (modais, fichas e saltos acima e abaixo do cabeçalho),
  `ui-sweep.cjs` (rolagem horizontal, controle coberto, texto cortado) e `sheet-width-check.cjs`, os três com `--control`, e
  `apoie-check.cjs` (o botão Apoie e a janela, numa construção de teste com `BI_SUPPORT_JSON`, com `--control`).
- A checagem ao centavo pega erro de valor, não erro de recorte: compare o que o recorte deixa de fora com a série que conta
  aquilo pelo destino (veja `docs/ai/learned-patterns.md`).

## Onde estão as decisões

- `docs/decisions/README.md`: as decisões (D1 em diante) e as perguntas em aberto (Q).
- `docs/ai/learned-patterns.md`: as armadilhas das fontes oficiais e as receitas que funcionaram.
- `GOVERNANCE.md`: quem decide, as regras de neutralidade e a mudança de método.

## O que perguntar em vez de decidir

Pergunte à pessoa mantenedora, numa issue ou no pull request, antes de:

- mudar uma decisão registrada em `docs/decisions/README.md`, ou o texto que o site mostra;
- mudar um método de cálculo (isso é uma proposta de método, com janela de comentário);
- usar uma fonte que não é oficial, ou estimar um número;
- acrescentar um serviço de terceiros, um custo ou uma dependência nova;
- mexer em workflows, permissões ou configurações do repositório.

## In English

Agent guide: Portuguese UI, English identifiers and commits; neutral text; no number without an official source; every sum
closes by hand; every period works; every check is proven against a planted failure; look at screenshots at 1440 and 420 px.
Specs are approved by the maintainer before code. Before starting a task, check it has no owner yet (the spec's owner
section, open issues, pull requests and branches). Pull requests go to `staging`; `main` only receives the maintainer's
promotion, followed by the back-merge. Ask before changing a recorded decision, a method, sources, dependencies or
repository settings.
