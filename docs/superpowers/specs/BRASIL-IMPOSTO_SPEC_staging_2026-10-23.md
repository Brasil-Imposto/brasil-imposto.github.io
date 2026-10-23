# Spec: o ambiente de staging e as chaves de funcionalidade

**Summary (English).** A second public site, staging, at `https://brasil-imposto.github.io/staging/`, built from a `staging` branch of
this repository and hosted by a new repository, `Brasil-Imposto/staging`, that holds only a deploy workflow. Staging is where every pull
request lands first, including ideas not yet approved; production keeps only what the maintainer approves. One codebase, one build
script with two profiles, and one switch file (`data/features.json`): staging builds every feature on, production only the approved
ones, and a feature switched off is absent from the page. Promotion is a pull request from `staging` to `main`, followed by a back-merge.
Production stays byte for byte what is live today when this lands.

Estado: **aprovada pelo mantenedor em 2026-10-23.** Base: as escolhas do mantenedor na mesma data (staging num segundo repositório para
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
- **Estado inicial:** a única chave é `apoie` (ligada no staging, desligada na produção). O campo `enabled` de `data/support.json`
  (PR #46) sai: a chave passa a ser a única fonte. No staging, o modal aparece com os valores que existem e "a definir" no lugar dos
  que faltam. A produção só pode ligar `apoie` com todos os valores de `data/support.json` preenchidos, e um teste garante isso.
- **Aprovar para a produção** é um pull request de uma linha no `staging` que muda `production` para `true`, seguido da promoção.
- Esconder partes da produção (a próxima tarefa do mantenedor) será uma chave a mais por parte, neste mesmo arquivo.

## 3. Um script de montagem, dois perfis

`docs/superpowers/tools/build-site.py --profile {production,staging} --out <pasta>` faz o que o passo "Assemble the site" de
`pages.yml` faz hoje (os quatro construtores, as três páginas, `assets/`, `index.html`, `.nojekyll`), mais:

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
- **A chave da produção pede os dados:** com `apoie` ligada na produção e um valor de `data/support.json` vazio, o teste falha.
- **O staging não suja o repositório:** depois de `build-site.py --profile staging`, `git status` não mostra mudança em arquivo
  versionado; o controle é uma montagem que escreve num arquivo versionado de propósito.
- **O staging funciona:** depois do primeiro deploy, `site-check.cjs` nas três páginas de `/staging/` em 1440 e 420 px, com
  `--control`; a faixa e o `noindex` em cada página; o botão Apoie presente no staging e ausente na produção.

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
