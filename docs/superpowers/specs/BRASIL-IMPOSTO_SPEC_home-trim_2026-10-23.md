# Spec: uma Início mais curta, com O que o Brasil vende só no staging

**Summary (English).** The first production trim under the staging switches (D157). On Início, "O que o Brasil vende" becomes the
`trade` switch: on in staging, off (absent) in production. Three sections move on both sites: "Para onde vai o dinheiro da União"
goes up to sit between "Maiores escândalos" and "Por que falta dinheiro"; "Como ler o mapa" and "Última divulgação de cada fonte"
leave Início for a new page, linked from the footer, that shows the notes for the period and measure the reader had on the map
without downloading the map's 91 MB of data; "O governo federal" leaves Início for the end of "Como o dinheiro anda". One pull
request into `staging` by the cloud session, after the staging pull request lands.

Estado: **aprovada pelo mantenedor em 2026-10-23** (D159), com as três recomendações: a página das notas abre no período e na
medida do leitor; o nome é "Como ler o mapa"; O governo federal fica no fim de Como o dinheiro anda. Base: a spec do staging,
`docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_staging_2026-10-23.md` (D157), seção 2 ("esconder partes da produção será uma chave a
mais por parte"). Feita no #59, no ar desde o #60 (2026-10-24).

## 1. O que muda

| Seção da Início | Produção | Staging |
|---|---|---|
| O que o Brasil vende | sai (chave `trade` desligada) | fica |
| Para onde vai o dinheiro da União | sobe: entre Maiores escândalos e Por que falta dinheiro | igual |
| Como ler o mapa e Última divulgação de cada fonte | vão para a página nova "Como ler o mapa", com link no rodapé | igual |
| O governo federal | vai para o fim da página Como o dinheiro anda | igual |

A Início fica nesta ordem, nos dois sites:

1. o mapa;
2. Maiores escândalos, com os maiores gastos e receitas do período (`#recentes-e-escandalos`);
3. Para onde vai o dinheiro da União (`#para-onde-vai`);
4. Por que falta dinheiro (`#por-que-falta-dinheiro`);
5. O que o Brasil vende (`#o-que-o-brasil-vende`), só no staging;
6. A rede do dinheiro do imposto, prévia (`#rede`);
7. o rodapé.

Leituras registradas com a decisão (D159):

- Só O que o Brasil vende se esconde. As mudanças de lugar valem nos dois sites, e o staging continua sendo a produção mais o que
  está escondido.
- O governo federal vai para Como o dinheiro anda, não para Os 3 Poderes (o mantenedor trocou o destino na mesma mensagem).
- A coluna "Vendeu ao exterior" do modal do estado (D109) fica nos dois sites; só a seção da Início sai.
- Esta decisão muda a ordem de D110 (Por que falta dinheiro logo abaixo de Maiores escândalos) e o lugar de D44 e D74 (a seção
  federal abaixo do mapa). D59 ("nada sai sem pedido do autor") é cumprido: as saídas são pedido do mantenedor.

## 2. Onde as seções nascem

As quatro seções e os dois links das notas estão escritos em
`docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_hero-mapa-3d-round-2_2026-09-29.html` (a fonte), que `build-simulation.py` transforma
na simulação da home e `build-platform-preview.py` na Início publicada. As mudanças entram na fonte e nos construtores, nunca à mão
numa página gerada; o `ci` continua conferindo que os construtores refazem as páginas versionadas.

## 3. A chave `trade`

Uma entrada a mais em `data/features.json`:

```json
{
  "key": "trade",
  "issue": 0,
  "description": "A seção O que o Brasil vende na Início",
  "staging": true,
  "production": false
}
```

O `issue` é o número do issue desta tarefa (a sessão na nuvem abre o issue pela API REST do GitHub e põe o número no lugar do 0).

- **Desligada é ausente** (spec do staging, seção 2): na produção, a Início não tem a seção (nenhum `data-trade`, nenhum
  `#o-que-o-brasil-vende`), nem o código que a monta (a parte de `docs/superpowers/previews/assets/home-feed.js` desde D109, que
  começa no comentário "D109, D111: O que o Brasil vende"), nem o estilo dela (as regras da seção em
  `docs/superpowers/previews/assets/home-feed.css`), nem o link "O que o Brasil vende ao exterior, produto por produto ↓" do bloco 4
  de Por que falta dinheiro. O jeito (um arquivo à parte carregado só com a chave ligada, ou a montagem cortando entre marcadores)
  fica com quem implementa, desde que o teste "nada vaza" da seção 7 passe.
- **Fica nos dois sites:** os dados `BI.trade` em `bi-data.js`, que o modal do estado também lê (`proposals.js`), e a coluna
  "Vendeu ao exterior" do modal.

## 4. Para onde vai o dinheiro da União sobe

Hoje `home-feed.js` põe Por que falta dinheiro e O que o Brasil vende logo depois de `#recentes-e-escandalos`
(`strip.after(why, trade)`), antes de `#para-onde-vai`. Passa a pô-los logo depois de `#para-onde-vai`. Nada mais muda no bloco
Para onde vai o dinheiro da União: ele continua seguindo o seletor de período do mapa.

## 5. A página Como ler o mapa

- **Arquivo:** `docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_como-ler-o-mapa_2026-10-23.html`, publicada nos dois sites ao lado
  das outras três páginas, com o cabeçalho e o rodapé comuns de `site_chrome.py`. Ela não entra na lista de páginas do cabeçalho
  (nenhum item marcado nela). O rodapé de todas as páginas ganha o link "Como ler o mapa".
- **Conteúdo:** os dois blocos que saem da Início, com os mesmos títulos, o mesmo texto e a mesma ordem: "Como ler o mapa" (as
  notas) e "Última divulgação de cada fonte" (a tabela).
- **Período e medida:** as notas mudam com o período e com a medida do mapa (a nota da escala do DF depende da medida). A página
  abre no período e na medida em que o leitor estava: os links "Notas ↓" do cartão de dados e "datas de cada fonte ↓" da linha de
  datas passam a levar à página nova com `?period=<id>&metric=<perCapita|total|ratio>` (`metric` já é o parâmetro da Início). Sem
  parâmetro, como no link do rodapé, a página abre no período e na medida em que a Início abre. A página tem o mesmo seletor de
  período do mapa (mês, ano e 4 anos) e a mesma troca de medida, e troca as notas sem recarregar.
- **Dados:** a página não baixa `bi-data.js` (91 MB). O código que monta as notas sai do script da Início para um módulo único; um
  construtor roda esse módulo para cada período e cada medida e grava um arquivo pequeno (`assets/map-notes.js`, alvo abaixo de
  1 MB), que a página lê. A tabela de datas vem de `BI.releases`. Precedente de rodar o código do mapa fora do navegador:
  `docs/superpowers/tools/ledger-graph-periods-check.cjs`, que já roda o mapa em 100 períodos.
- **Na Início:** a seção `#como-ler-o-mapa` sai, e os dois links passam a apontar para a página nova com o período e a medida do
  momento. O cartão de dados e os avisos dele ficam como estão.

## 6. O governo federal vai para Como o dinheiro anda

- **Lugar:** a seção `#governo-federal` sai da Início e entra no fim de
  `docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_como-o-dinheiro-anda-round-1_2026-10-21.html`, depois das três formas ("Siga R$ 100",
  "O caminho em seis passos" e "O grande fluxo de 2025") e antes do rodapé, nos dois sites. Ela aparece qualquer que seja a forma
  escolhida.
- **Inteira:** As contas da União, Pessoal pago pela União, o custo dos eleitos e as emendas, na forma A, cartões (D74). Sai só o
  sobretítulo "Abaixo do mapa", que deixaria de ser verdade. O título "O governo federal" e o subtítulo ficam como estão.
- **Dados:** a página não baixa `bi-data.js`. `build-standalone-data.py` grava um arquivo pequeno só com `federal_section`,
  `federal_servants` e `releases` (cerca de 300 KB, por exemplo `assets/bi-federal.js`), e a página carrega esse arquivo,
  `federal-section.js` e `federal-section.css`.
- **Na Início:** saem a seção, a chamada `window.BIFED.render` e o `federal-section.js`. O `federal-section.css` fica na Início
  enquanto o modal do estado usar a classe `fed` (`proposals.js` usa, conferido em 2026-10-23). As chaves `federal_section` e
  `federal_servants` saem de `bi-data.js` se a busca no repositório inteiro não achar outro leitor (em 2026-10-23, entre os scripts da
  página, só `federal-section.js` as lia).

## 7. Como conferir

Cada checagem com o seu controle, que tem de falhar:

- **A Início da produção:** fora das quatro mudanças, o texto visível é igual ao do ramo `staging` antes delas
  (`visible-text-probe.cjs`, com a lista das diferenças esperadas), e as seções seguem a ordem da seção 1.
- **Nada vaza:** a montagem de produção não tem `data-trade`, `o-que-o-brasil-vende`, o código nem o estilo da seção, nem o link do
  bloco 4. Controle: `trade` ligada na produção num teste, e a busca tem de falhar.
- **O staging:** a Início tem O que o Brasil vende logo abaixo de Por que falta dinheiro, e o link do bloco 4 leva a ela.
- **Como ler o mapa:** para cada período e cada medida do mapa, as notas e a tabela da página nova são iguais, texto por texto, às
  que a Início de antes da mudança mostra para o mesmo período e a mesma medida. A verdade vem da Início de antes, nunca do
  construtor novo. Controle: uma nota alterada de propósito é pega. A lista de pedidos da página não tem `bi-data.js`. Os links
  "Notas ↓" e "datas de cada fonte ↓" abrem a página no período e na medida que a Início mostrava.
- **Como o dinheiro anda:** o texto visível de O governo federal é igual ao da Início de antes, menos "Abaixo do mapa"; a página não
  pede `bi-data.js`; as três formas continuam com o mesmo texto.
- **O modal do estado** continua com a coluna "Vendeu ao exterior" nos dois sites.
- **As quatro páginas:** `site-check.cjs` em 1440 e 420 px, com `--control`; o link "Como ler o mapa" no rodapé de cada uma.
- **O `ci`:** os construtores refazem as páginas versionadas, e os testes passam.

## 8. Quem faz o quê

- **Sessão na nuvem, um pull request para o `staging`:** tudo acima. É o primeiro pull request de tarefa pela regra de D157: começa
  quando o pull request do staging tiver entrado e a sessão local tiver criado o ramo `staging` (spec do staging, seção 6, itens 1 a
  4). Ramo saindo do `staging`, commits com `-s`, sem merge.
- **Sessão local:** conferir o staging no ar depois do merge.
- **Mantenedor:** o "pode" do merge no `staging` e, depois, o da promoção à produção.

## 9. Fora desta spec

O subtítulo de O governo federal diz "janeiro a julho" enquanto os números vão até agosto (auditoria N-11): fica como está. O desenho
da página Como o dinheiro anda (Q69 a Q71) e outras partes a esconder da produção ficam para tarefas próprias.
