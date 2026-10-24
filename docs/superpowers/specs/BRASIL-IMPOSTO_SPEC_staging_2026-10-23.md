# Spec: o ambiente de staging e as chaves de funcionalidade

**Summary (English).** A second public site, staging, at `https://brasil-imposto.github.io/staging/`, built from a `staging` branch of
this repository and hosted by a new repository, `Brasil-Imposto/staging`, that holds only a deploy workflow. Staging is where every pull
request lands first, including ideas not yet approved; production keeps only what the maintainer approves. One codebase, one build
script with two profiles, and one switch file (`data/features.json`): staging builds every feature on, production only the approved
ones, and a feature switched off is absent from the page. Promotion is a pull request from `staging` to `main`, followed by a back-merge.
Production stays byte for byte what is live today when this lands.

Estado: **aprovada pelo mantenedor em 2026-10-23.** Feita: #52 (2026-10-23) e a seção 6 no mesmo dia; staging público por escolha do mantenedor (D165); falta o token do deploy automático. Base: as escolhas do mantenedor na mesma data (staging num segundo repositório para
simular produção; staging como ambiente de ideias, onde cada contribuição entra primeiro; uma funcionalidade chega à produção por chave,
não por cópia de código entre ramos).

## 1. Os dois sites

| | Produção | Staging |
|---|---|---|
| Endereço | `https://brasil-imposto.github.io` | `https://brasil-imposto.github.io/staging/` |
| Montado a partir de | `main` | o ramo `staging` deste repositório |
| Publicado por | o GitHub Pages deste repositório (`pages.yml`) | o GitHub Pages do repositório `Brasil-Imposto/staging` |
| Chaves | só as aprovadas | todas ligadas |
| Marcas | nenhuma | uma faixa no topo de cada página e `<meta name="robots" content="noindex">` |

Texto da faixa: "Ambiente de testes: inclui ideias ainda não aprovadas. O site oficial é brasil-imposto.github.io." com o endereço como
link. O `robots.txt` da produção (na raiz do site) passa a ter `User-agent: *` e `Disallow: /staging/`.

As três páginas usam só caminhos relativos para os seus arquivos (conferido em 2026-10-23: nenhum caminho começa na raiz), então
funcionam sob `/staging/`. Os links absolutos que existem apontam para o GitHub e para a imagem de prévia social da produção, e podem
ficar assim.

## 2. As chaves: `data/features.json`

```json
{
  "features": [
    {
      "key": "apoie",
      "issue": 46,
      "description": "O botão Apoie e o modal de apoio",
      "staging": true,
      "production": false
    }
  ]
}
```

- Um esquema em `schemas/` valida o arquivo (chaves em inglês, `key` único, `issue` inteiro, `staging` e `production` booleanos).
- **Desligada é ausente:** uma funcionalidade desligada no perfil não entra na página montada (nem marcação, nem estilo, nem script
  dela); nunca é escondida por CSS.
- **Estado inicial:** a única chave é `apoie`, ligada no staging; na produção, o valor que o campo `enabled` de `data/support.json`
  tinha na `main` quando esta mudança entrou (ligado desde o PR #54, D162). Esse campo sai: a chave passa a ser a única fonte. O D158 (2026-10-23) põe o
  Apoie na produção: GitHub Sponsors e cripto mostram "Em breve", sem link e sem endereço, até cada canal estar pronto, e o formulário
  de contato funciona pelo Web3Forms quando a chave de acesso existir (PR #49; o D162 liga o botão antes dela, PR #54).
- **A regra dos dados é a do PR #49**, igual nos dois perfis: um canal em `live` precisa de todos os seus valores; um canal em `soon`
  mostra "Em breve", sem link e sem endereço; nenhum valor que falta aparece como "a definir". A produção liga `apoie` sem a chave
  de acesso do formulário (D162): sem ela, a vista de contato fica fora da página; uma chave preenchida e malformada, ou um e-mail no
  lugar dela, barra a montagem, e um teste garante isso. O staging desenha o formulário mesmo sem a chave: um envio mostra a
  linha de erro e não faz pedido.
- **Aprovar para a produção** é um pull request de uma linha no `staging` que muda `production` para `true`, seguido da promoção.
- Esconder partes da produção (a próxima tarefa do mantenedor) será uma chave a mais por parte, neste mesmo arquivo.

## 3. Um script de montagem, dois perfis

`docs/superpowers/tools/build-site.py --profile {production,staging} --out <pasta>` faz o que o passo "Assemble the site" de
`pages.yml` faz hoje (os quatro construtores, as três páginas, `assets/`, `index.html`, a página que encaminha o endereço antigo do
Início para a raiz (D160), `.nojekyll`), mais:

- lê `data/features.json` e monta cada funcionalidade só se a chave do perfil estiver ligada;
- no perfil `staging`: a faixa e o `noindex` em cada página;
- no perfil `production`: o `robots.txt`.

`pages.yml` passa a chamar `build-site.py --profile production --out _site`. As páginas versionadas no repositório continuam sendo as
da produção (a checagem do `ci` que compara as páginas versionadas com os construtores segue valendo). **A montagem do staging nunca
escreve em arquivo versionado:** tudo vai para a pasta de saída, e `git status` fica limpo depois dela.

## 4. O repositório `Brasil-Imposto/staging`

Público (o GitHub Pages do plano gratuito só publica repositório público), com um `README.md` que diz o que ele é e um workflow
`.github/workflows/deploy.yml`:

- dispara por `repository_dispatch` (tipo `staging-updated`) e por `workflow_dispatch` (o botão manual, para quando o disparo falhar);
- faz checkout de `Brasil-Imposto/brasil-imposto.github.io` no ramo `staging`, prepara o Python 3.12, roda
  `build-site.py --profile staging --out _site`, e publica com `actions/upload-pages-artifact` e `actions/deploy-pages`;
- ações fixadas por commit, como em `ci.yml`; token do workflow só com o que o deploy do Pages pede.

Nada montado é versionado nesse repositório. O arquivo do workflow fica também neste repositório, em `deploy/staging/deploy.yml`, como
fonte, para ser revisado por pull request.

No repositório principal, `.github/workflows/staging-dispatch.yml`: em todo push no ramo `staging`, chama
`POST /repos/Brasil-Imposto/staging/dispatches` com `event_type: staging-updated`, usando o segredo `STAGING_DISPATCH_TOKEN`. Sem o
segredo, o workflow termina avisando, sem falhar o push.

**O token** é um token fino (fine-grained) da conta do mantenedor, com dono a organização Brasil-Imposto, acesso só ao repositório
`Brasil-Imposto/staging` e só a permissão que o endpoint de dispatch pedir (conferir na documentação do GitHub ao criar), com validade
de no máximo um ano. O GitHub não deixa criar esse token pela API: o mantenedor cria, e a sessão local o guarda como segredo sem
mostrá-lo.

## 5. O fluxo

1. Todo ramo de tarefa sai do `staging`, e o pull request vai para o `staging` (squash; `ci` e `dco` obrigatórios).
2. Cada merge no `staging` dispara o deploy do staging.
3. **Promoção:** um pull request de `staging` para `main` (squash), com o título `release: <data>` e a lista dos pull requests que ele
   leva; o aviso de produção e o "pode" do mantenedor antes do merge.
4. **Logo depois de cada promoção:** um pull request de `main` para `staging` com merge commit (o back-merge), para os dois ramos não se
   afastarem. O GitHub Actions da organização não abre pull request (configuração da organização), então quem promove abre este também.
5. **Correção urgente:** um ramo `hotfix/*` sai da `main`, o pull request vai para a `main`, e depois o mesmo back-merge para o `staging`.

## 6. Configurações do repositório (pela sessão local, nesta ordem)

1. A regra da `main` (ruleset 25616038) hoje vale para "o ramo padrão" (`~DEFAULT_BRANCH`): passa a valer para `refs/heads/main` pelo
   nome, antes de qualquer outra mudança, senão a `main` perde a proteção quando o ramo padrão mudar.
2. Criar o ramo `staging` a partir da `main`.
3. Uma regra nova para o `staging`: só por pull request, `ci` e `dco` obrigatórios, sem push forçado e sem apagar; squash e merge commit
   permitidos (a regra do GitHub vale para todos os pull requests do ramo; pelo fluxo, o merge commit é usado só no back-merge).
4. O ramo padrão do repositório passa a ser `staging`, para os pull requests de quem contribui caírem nele.
5. `ci.yml` também roda em push no `staging`.
6. Criar o repositório `Brasil-Imposto/staging`, ligar o GitHub Pages por GitHub Actions, guardar o segredo do token.
7. Atualizar o texto que diz "pull request para a `main`": README, `CONTRIBUTING.md`, o modelo de pull request e a página da
   organização (`Brasil-Imposto/.github`, `profile/README.md`).

## 7. Como conferir

- **A produção não muda:** a montagem `production` gera as três páginas iguais, byte a byte, às publicadas antes desta mudança (a
  única diferença nova é o `robots.txt`); a sonda de texto visível dá 100 de 100.
- **Nada vaza:** um teste monta a produção e procura as marcas de cada funcionalidade desligada (por exemplo, a classe do botão Apoie);
  o controle liga `apoie` na produção num teste e a busca precisa falhar.
- **A chave da produção pede os dados:** com uma chave de acesso malformada (ou um e-mail no lugar dela), ou com um canal em `live` e
  um valor dele vazio, o teste falha; sem a chave, a produção mostra o botão e o modal sem o formulário (D162); um canal em `soon` mostra "Em breve" sem link e sem endereço (os testes e os controles
  do PR #49 continuam valendo).
- **O staging não suja o repositório:** depois de `build-site.py --profile staging`, `git status` não mostra mudança em arquivo
  versionado; o controle é uma montagem que escreve num arquivo versionado de propósito.
- **O staging funciona:** depois do primeiro deploy, `site-check.cjs` nas três páginas de `/staging/` em 1440 e 420 px, com
  `--control`; a faixa e o `noindex` em cada página; o botão Apoie presente no staging, e na produção só quando a chave `apoie` da
  produção estiver ligada.

## 8. Quem faz o quê

- **Sessão na nuvem, um pull request para a `main`:** as seções 2, 3, o arquivo `deploy/staging/deploy.yml` da seção 4, o
  `staging-dispatch.yml`, o item 5 da seção 6, os testes da seção 7 e os textos do item 7 que estão neste repositório. Começa depois que
  os pull requests #45 e #46 entrarem, porque os três mexem em `docs/superpowers/tools/site_chrome.py`. É o último pull request de
  tarefa que vai direto para a `main`: a sessão local faz a seção 6 logo depois do merge dele.
- **Sessão local:** os itens 1 a 4 e 6 da seção 6, a página da organização, e a conferência do primeiro deploy.
- **Mantenedor:** criar o token (seção 4) e dar o "pode" de cada promoção.

## 9. Fora desta spec

Quais partes esconder da produção (a próxima tarefa), o site em Astro (quando chegar, usa os mesmos perfis e a mesma chave), um domínio
próprio e um endereço de prévia por pull request.
