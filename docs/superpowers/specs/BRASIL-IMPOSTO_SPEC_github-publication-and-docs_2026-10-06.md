# Brasil-Imposto: publicação no GitHub e documentação

Status: **Rascunho para aprovação, revisão 2** (D3). As respostas do autor de 2026-10-06 estão aplicadas (D97, D98). Nada de repositório, `git init` ou commit antes da aprovação. Criar o repositório e fazer o push são ações públicas e só acontecem com a ordem explícita do autor (D54).

### Summary (English)

This spec prepares the first public release of Brasil-Imposto on GitHub: what goes in now (the latest home preview, its shared modules and builders, the published data JSON and the data pipelines), what stays out (everything derived from the Gemini conversation, 2026 candidacies, people only cited in investigations, the author's verbatim quotes and older previews), and what is never versioned (generated bundles, caches and every raw download). It defines the documentation set (README in Portuguese with an English summary, CONTRIBUTING, CODE_OF_CONDUCT based on Contributor Covenant 2.1 in Portuguese, GOVERNANCE with the four neutrality rules of D51 and a four-phase path from a single owner to an elected council, SECURITY, AGPL-3.0 for code and CC BY 4.0 for data and texts, data sources with release dates, one guide per pipeline with its cent check and failing control, issue and PR templates for new states and new cases) and the GitHub Pages deployment of the preview (D56). The author answered seven of the nine decisions on 2026-10-06; three points remain open (section 2).

## 1. O que o registro já decidiu

| Registro | O que já está decidido |
|---|---|
| D2 (2026-09-25) | Repositório público no GitHub, com as práticas atuais de código aberto. No início só o autor aprova Pull Requests; novos mantenedores entram conforme o projeto crescer. |
| D51 e GD48 (2026-10-02) | Só dados, sem chamado ao voto; regras de nomes e um botão "pedir correção" em cada página; sem advogado por enquanto. As quatro regras de neutralidade no `GOVERNANCE.md` desde o primeiro dia: mantenedores declaram filiação partidária e cargo público; nunca dois mantenedores do mesmo partido; filiado não aprova sozinho PR sobre o próprio partido; o projeto recusa dinheiro de partido, candidato e ocupante de cargo eletivo e publica toda fonte acima de 5% da receita do ano. |
| D54 (GD30, GD31, GD32, GD43, GD44, GD47) | Organização `brasil-imposto`. AGPL-3.0 no código, CC BY 4.0 nos dados e textos. Código, nomes de arquivo, chaves de JSON e commits em inglês; documentação em português com resumo em inglês. O pacote de colaboração inteiro da pesquisa, sem política de IA; código de conduta 2.1 em português. Fora do repositório: a conversa do Gemini, as candidaturas de 2026 e quem só foi citado em investigação. Nada de commit nem push até o autor mandar. |
| D55 (GD45) | Site em Astro 7, TypeScript estrito, three.js e mapa SVG gerado no build, um JSON por entidade, scripts Python com atualização mensal por PR. Tem spec própria, fora desta. |
| D56 (GD46) | GitHub Pages em `brasil-imposto.github.io`. As notas dos usuários, no futuro, num Worker com banco D1 numa conta Cloudflare própria do projeto, com o passo a passo documentado para futuros desenvolvedores. Saída anotada no grill se a banda apertar: Cloudflare Pages. |
| D97 e D98 (2026-10-06) | As respostas a esta spec: decisões publicadas sem citações; só a prévia mais recente; tudo o que deriva da conversa com o Gemini fora; fotos versionadas; CI de proveniência sem o bruto; nomes de arquivo e todo o código em inglês, inclusive os documentos; brutos fora do git; bandeiras oficiais; nenhuma referência a outro projeto; candidaturas de 2026 fora dos dados. |
| Pesquisa de colaboração, seção 7 (adotada por GD47) | Tudo por PR, inclusive o autor; um assunto por PR; título com a área (`data:`, `map:`, `docs:`); pseudônimo estável aceito; revisão no vocabulário do Bitcoin Core (Concept, Approach, `ACK <commit>` dizendo como revisou); DCO no lugar de CLA; `main` protegida com PR obrigatório e 0 aprovações enquanto houver um mantenedor (1 aprovação de outra pessoa quando entrar o segundo); checks verdes aceitos só do GitHub Actions; commits do mantenedor assinados; `SECURITY.md` com relato privado; formulários "Pedir correção", "Acrescentar fonte", "Proposta de método" e "Defeito"; modelo de PR com checklist de fonte; `CODEOWNERS`; rótulos; CI de proveniência e OpenSSF Scorecard; `docs/decisions/`; Discussions com quatro categorias (Perguntas, Ideias, Propostas de método, Anúncios); quadro público de cobertura; sem chat e sem pedir dinheiro no lançamento. |

### Conferido em 2026-10-06

| Fato | Fonte |
|---|---|
| O nome `brasil-imposto` está livre: não existe usuário nem organização com ele. | API do GitHub, resposta 404 |
| O endereço sem subpasta exige um repositório chamado `brasil-imposto.github.io`. Com outro nome, o site fica em `brasil-imposto.github.io/<repositório>/`. | Documentação do GitHub, "What is GitHub Pages" |
| Site publicado até 1 GB; banda de 100 GB por mês (limite flexível); cada publicação expira em 10 minutos. | Documentação do GitHub, "GitHub Pages limits" |
| Aviso em arquivo acima de 50 MiB, bloqueio acima de 100 MiB, repositório idealmente abaixo de 1 GB. | Documentação do GitHub, "About large files on GitHub" |
| O código de conduta 2.1 existe em português do Brasil no repositório oficial, sem travessões, com um campo de contato a preencher. | `EthicalSource/contributor_covenant`, `content/version/2/1/code_of_conduct.pt-br.md` |
| O GitHub não tem API para criar organização, exigir 2FA na organização nem criar categorias de Discussions. O resto (repositório, regras da `main`, rótulos, Pages, Discussions ligado, relato privado de falha, quadro de cobertura) sai pelo `gh`. | Descrição oficial da API REST e introspecção da API GraphQL |
| O dono da organização tem acesso administrativo completo, e o GitHub recomenda pelo menos dois donos. Papéis por repositório: Read, Triage, Write, Maintain e Admin. As regras da `main` valem para administradores que não estejam na lista de exceção, e qualquer pessoa com leitura vê as regras ativas. O registro de auditoria cobre 180 dias e só os donos o leem. | Documentação do GitHub: "Roles in an organization", "Repository roles for an organization", "About rulesets", "Reviewing the audit log for your organization" |

## 2. Decisões: respondidas e em aberto

| # | Decisão | Estado |
|---|---|---|
| 1 | Organização e nome do repositório | **Em aberto.** O autor perguntou como os grandes projetos começam com controle total e descentralizam depois; a resposta e a proposta estão logo abaixo. Nome recomendado: `brasil-imposto/brasil-imposto.github.io`, para o site abrir sem subpasta. |
| 2 | Citações do autor nos registros | Decidido (D97): as decisões vão a público sem as citações literais; os originais ficam em `private/`. |
| 3 | Prévias no repositório | Decidido (D97): só a mais recente. |
| 4 | Material derivado da conversa do Gemini | Decidido (D97): fora, inclusive a auditoria e a verificação de Florianópolis. |
| 5 | Candidaturas de 2026 depois do 2º turno (25 de outubro) | **Em aberto.** São os registros do TSE de candidatura em 2026 de quatro pessoas que aparecem em dois casos (CEI Comasa e ETE Insular). Já saíram dos dados (D98). Recomendação: ficam fora de vez. |
| 6 | Fotos (57 MB) | Decidido (D97): versionadas no repositório. |
| 7 | Proveniência sem o bruto no repositório | Decidido (D97): o CI confere o esquema, os totais oficiais e o tamanho dos arquivos; cada pipeline grava um manifesto dos brutos com SHA-256. |
| 8 | Email público | Decidido (D97), pela recomendação: "noreply" do GitHub nos commits; endereço gratuito do projeto para conduta e segurança, criado pelo autor. |
| 9 | Nomes de arquivo | Decidido (D97): todos em inglês, inclusive os dos documentos, e todo o código em inglês. |
| 10 | Foto da Fazenda sob CC BY-ND 3.0 (item à parte 3) | **Em aberto.** Não existe substituta com licença livre que dê para usar (seção 13). |

### Organização: controle total agora, descentralização depois

Os grandes projetos chegaram ao mesmo desenho por caminhos parecidos (pesquisa de colaboração, seção 1): o Python teve um dono só até 2018 e passou a um conselho eleito de cinco pessoas; no Bitcoin Core, quem faz o merge julga o consenso e não o próprio gosto; o Kubernetes sobe as pessoas por uma escada (membro, revisor, aprovador) com critérios numéricos e escopo por pasta; o Rust tem um conselho com limite por afiliação. Proposta para o `GOVERNANCE.md`, escrita desde o primeiro dia (os números são sugestões, a confirmar):

| Fase | Quando | Quem decide | No GitHub |
|---|---|---|---|
| 0. Fundação | Hoje | O autor | O autor é o único dono da organização. Tudo entra por PR, inclusive o que ele faz, e a regra da `main` não tem exceção, nem para o dono. |
| 1. Revisores | 3 contribuidores recorrentes (por exemplo, 5 PRs aceitos em 3 meses) | O autor, com revisão de outras pessoas | Time de revisores com papel Triage e depois Write; `CODEOWNERS` por área (um estado, uma base de dados). |
| 2. Segundo mantenedor | Um revisor com histórico (por exemplo, 10 PRs revisados) | Dois mantenedores; todo PR precisa da aprovação de outra pessoa | Segundo dono da organização, como o GitHub recomenda; a regra pede 1 aprovação de quem não fez o último envio. |
| 3. Conselho | 5 ou mais mantenedores | Conselho eleito, no modelo do Python, com o limite de partido de GD48 | O papel de dono fica só com membros do conselho; o autor passa a ser uma cadeira. |

Limite honesto: no GitHub, qualquer dono pode mudar qualquer regra. A descentralização é um compromisso escrito, visível nas regras ativas e no registro de auditoria. A garantia final é a licença: a AGPL e a CC BY deixam qualquer pessoa copiar o código e os dados e seguir com o projeto se os mantenedores falharem.

## 3. O que vai ao repositório agora

Regra: **versionado** é tudo o que foi escrito à mão e tudo o que precisa de um download do governo para ser refeito (os JSON de `data/`, as malhas `geo-*.json`). **Não versionado** é tudo o que se refaz só com arquivos versionados (os pacotes da prévia) e todo arquivo bruto baixado de uma fonte.

| Caminho | O que é |
|---|---|
| `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`, `SECURITY.md` | Os documentos de entrada (seção 8) |
| `LICENSE`, `LICENSE-DATA` | AGPL-3.0 e CC BY 4.0 (seção 7) |
| `CLAUDE.md` | Regras do projeto para quem contribui com agentes, sem citações e sem as regras da máquina do autor |
| `.github/` | Formulários, modelo de PR, `CODEOWNERS` e workflows (seção 9) |
| `data/` | Os JSON publicados |
| `data/scripts/` | Os pipelines de coleta e montagem |
| `docs/data-sources.md`, `docs/pipelines/`, `docs/decisions/`, `docs/future-work.md`, `docs/credits-and-licenses.md` | Fontes, guias dos pipelines, decisões sem citações, trabalho futuro (D57), créditos |
| `docs/research/` | As pesquisas, menos o que fica fora (seção 4) |
| `docs/superpowers/previews/`, `docs/superpowers/tools/` | A prévia mais recente com os módulos (`assets/`) e os construtores |
| `private/` | Só na máquina do autor, ignorada pelo git |

O repositório se chama `brasil-imposto.github.io` pela recomendação da decisão 1.

Também antes do primeiro commit (D97, decisão 9): todo nome de arquivo e de pasta passa para o inglês, inclusive os das pesquisas e do grill (por exemplo, `..._colaboracao-open-source_...` vira `..._open-source-collaboration_...`), e as chaves de JSON em português também (`arrecadacao`, `nome`, `populacao_2024` e `saldo_d41` em `data/ug/ug-balance-2024*.json`; `receita_national_total` nos `two-step-balance-*`; `valor_aditado_brl` na obra da SC-401), junto com os scripts, módulos e textos que os citam. Rótulos oficiais usados como valor (nomes de tributos, funções de governo, linhas de anexo) não são nomes de código e ficam como a fonte os escreve. Depois da troca, a prévia é refeita e conferida.

## 4. O que fica fora (D54, D97)

Tudo o que sai vai para `private/`, dentro da pasta do projeto (D1) e fora do git.

| O quê | Onde está hoje | Como sai |
|---|---|---|
| Tudo o que deriva da conversa do Gemini | A conversa, a auditoria e a verificação de Florianópolis, em `docs/research/` | Arquivos inteiros para `private/`; os valores oficiais de Florianópolis continuam em `data/florianopolis.json` |
| Candidaturas de 2026 | Feito em 2026-10-06 (D98): saíram de dois casos, de dois scripts e de duas pesquisas | Guardadas em `private/election-2026-flags.json`, para a revisão jurídica |
| Quem só foi citado em investigação | A conferir, arquivo por arquivo: pesquisas da ponte (responsáveis), escândalos, INSS, pré-sal e DF; `data/hercilio-luz.json`, `data/cases/inss-deductions.json`, `data/home/scandals-status.json`, `data/scripts/ponte/build_json.py` | Fica só quem tem papel num documento oficial, com o ato e o link (D48). O resto vai para `private/` com a indicação de onde estava |
| As citações do autor (D97) | `README.md` (tabela D), grill, `CLAUDE.md`, `docs/ai/learned-patterns.md`, `previews/src/*-notes.html` | Versões públicas sem citações; os originais em `private/` |
| As prévias anteriores (D97) | `docs/superpowers/previews/` | Para `private/previews/` |

## 5. O que nunca é versionado, e como refazer

| Caminho | Tamanho | O que é | Como refazer |
|---|---|---|---|
| `docs/superpowers/previews/assets/bi-data.js` | 85 MB | Pacote de dados da prévia | `build-standalone-data.py` |
| `bi-geo*.js`, `bi-post-grill.js`, `cases.json` (mesma pasta) | 2 MB | Pacotes da prévia | `build-cases.py`, `build-post-grill-data.py`, `build-standalone-data.py` |
| `data/scripts/series/cache/` | 210 MB | Downloads do SICONFI, do Portal e do Tesouro | Os scripts `fetch_*` e `download_*.sh` do pipeline, que retomam de onde pararam |
| `data/ug/cache/` | 94 MB | Base de despesas do Tesouro | Pipeline da regra em duas etapas |
| `data/df/cache/` | 16 MB | Portal da Transparência do DF | Pipeline do DF por Região Administrativa |
| `data/scripts/siconfi/cache/` | (já ignorado hoje) | Relatórios do SICONFI | Pipeline dos orçamentos de 2024 |
| `data/federal/raw/` | 38 MB | ZIPs e CSVs da Câmara, do Senado e das emendas (D98) | Pipeline da seção federal |
| `data/ug/*.csv`, `data/ug/*.pdf` | 29 MB | Cadastro de unidades gestoras do SIAFI e dois PDFs (D98) | Pipeline da regra em duas etapas |
| `data/df/*.csv`, `data/df/*.xlsx` | 5 MB | Arquivos baixados para a pesquisa do DF (D98) | Pipeline do DF |

### O novo `.gitignore`

```
# caches e brutos de download: refeitos pelos pipelines (docs/pipelines/)
**/cache/
data/federal/raw/
data/ug/*.csv
data/ug/*.pdf
data/df/*.csv
data/df/*.xlsx
# pacotes gerados da prévia: refeitos por docs/superpowers/tools/
docs/superpowers/previews/assets/bi-data.js
docs/superpowers/previews/assets/bi-geo*.js
private/archive/docs/superpowers/previews/assets/bi-post-grill.js
docs/superpowers/previews/assets/cases.json
# material que não é publicado (D54, D97)
private/
# ambiente
__pycache__/
*.pyc
.venv/
node_modules/
.DS_Store
```

### Como quem chega refaz tudo

```
# a prévia: só Python 3, sem pacotes (conferido: os três usam a biblioteca padrão)
python3 docs/superpowers/tools/build-cases.py
python3 docs/superpowers/tools/build-standalone-data.py
python3 private/archive/docs/superpowers/tools/build-post-grill-data.py
# depois, abrir a prévia mais recente pelo caminho do arquivo no navegador
```

Os dados: cada pipeline tem o seu guia em `docs/pipelines/` (seção 8), com as entradas, os comandos, a checagem ao centavo e o `--control` que tem de falhar.

## 6. Fotos: créditos e licenças

Decidido (D97): as fotos são versionadas. Hoje são 5.323 fotos JPG de políticos (57 MB, em `governors/`, `rs-mayors/`, `sc-mayors/`, `state-deputies/` e `union/`), cada uma com arquivo, fonte, autor e licença em `data/politicians/photos.json`, e 18 fotos de obras com `credits.json` em cada pasta de caso. Licenças: 5.322 fotos do TSE sob CC BY (licença dos conjuntos de candidatos no portal de dados abertos do TSE); 1 foto de gov.br sob CC BY-ND 3.0 (decisão 10); nas obras, 10 sob CC BY-SA e 8 sob CC BY ou atribuição.

Créditos: os registros por foto continuam sendo a fonte. `docs/credits-and-licenses.md` resume por fonte e licença, e diz que cada foto mantém a própria licença: o CC BY 4.0 do projeto não vale para fotos de terceiros (as CC BY-SA continuam CC BY-SA). Quem cobrir outro estado manda as fotos no mesmo PR, com o registro de crédito de cada uma.

## 7. Licenças

| O quê | Licença |
|---|---|
| Código: scripts Python, construtores, JS, CSS e HTML da prévia, workflows | AGPL-3.0, em `LICENSE` |
| Dados publicados (`data/**/*.json`) e textos (documentação e pesquisas) | CC BY 4.0, em `LICENSE-DATA`, com a forma de citar: "Fonte: <órgão>; dados tratados pelo Brasil-Imposto" |
| Dado oficial de origem | Regras de cada órgão, listadas em `docs/data-sources.md`; o projeto não reivindica direito sobre o dado público |
| Fotos | A licença de cada arquivo, no registro de créditos |
| Bandeiras (27 estados e 30 países) | Domínio público, arquivos oficiais do Wikimedia Commons, com fonte e SHA-1 em `credits.json` de cada pasta (D98) |
| Copiadas no repositório: d3 7.9.0, topojson-client 3.1.0, Clipper 6.4.2 | ISC, ISC e Boost 1.0 (conferido no npm e no cabeçalho do Clipper) |
| Carregadas de fora, sem cópia: three.js 0.170.0, fonte Manrope | MIT (jsDelivr) e SIL OFL (Google Fonts) |
| Malhas | Natural Earth em domínio público (conferido no site); IBGE pelos termos do IBGE, a registrar com link no plano |

## 8. Documentação

Documentos em português, nomes de arquivo em inglês, prosa sem travessões (conferida por script, com uma linha de controle que tem de ser pega).

| Arquivo | Conteúdo |
|---|---|
| `README.md` | O que é, em três linhas; link do site; estado (prévia, ainda não o site final de D55); como abrir a prévia na própria máquina; de onde vêm os números; como ajudar; neutralidade; licenças; no fim, a seção "In English" para desenvolvedores de fora (GD44). |
| `CONTRIBUTING.md` | Tudo por PR, inclusive o autor; um assunto por PR; título com a área; DCO com `git commit -s`; identidade: conta do GitHub com email válido, pseudônimo estável aceito; o ônus da prova é de quem acrescenta o número (regra da Wikipedia); vocabulário de revisão (Concept, Approach, `ACK <commit>` dizendo como revisou); checklist de dados; tarefas por dificuldade; sem política de IA (GD47). |
| `CODE_OF_CONDUCT.md` | O texto oficial 2.1 em português do Brasil, com o contato da decisão 8, mais um anexo do projeto (pesquisa, seção 7): discussão partidária e ataque a pessoa mostrada no site saem do repositório. |
| `GOVERNANCE.md` | Quem decide hoje (o autor, D2) e como (o motivo por escrito no PR); as quatro fases da seção 2, com os números que o autor confirmar; as quatro regras de neutralidade de D51 e GD48, com as palavras da decisão; mudança de método anunciada em Discussions com 7 a 10 dias de comentário antes do merge; um quadro de áreas com situação ("mantido", "sem dono"), estado por estado. |
| `SECURITY.md` | Como relatar falha sem expor: o relato privado do GitHub e o contato da decisão 8. |
| `LICENSE`, `LICENSE-DATA` | Textos integrais da AGPL-3.0 e da CC BY 4.0. |
| `docs/data-sources.md` | Para cada fonte: órgão, base, link, frequência, última divulgação, termos de uso e armadilhas conhecidas (a tabela de fontes dos padrões aprendidos). As datas vêm de `data/release-dates.json` por script, para nunca divergirem do dado. |
| `docs/pipelines/` | Um guia por pipeline: balanço por estado de 2024 (o `data/scripts/README.md` de hoje), séries federais e dos estados, municípios de um estado (`--uf`), regra em duas etapas, seção federal, DF por Região Administrativa, políticos e fotos, obras e casos, total pago da ponte, bolo da União, malhas e a própria prévia. Cada guia: entradas com link, comandos na ordem, saídas, checagem ao centavo, o `--control` que tem de falhar, tempo e disco esperados, e o ritmo dos servidores do governo (Portal: um arquivo a cada 90 segundos, script que retoma). Mais uma página de regras de coleta: um arquivo por vez, apagar o bruto, ler só o necessário. |
| `docs/decisions/` | `README.md` com a tabela D1 em diante, sem citações (D97), e as perguntas em aberto; daqui em diante, uma decisão por arquivo (`0099-<assunto>.md`), com o link do PR. |
| `docs/future-work.md` | As notas dos usuários (GD41) com o passo a passo do Worker e do D1 (D56); os pedidos pela Lei de Acesso (GD42); os outros estados (D52); o asfalto pelos contratos; a folha federal de 2019 a 2023 (Q32); o INSS por município (Q25). |
| `docs/credits-and-licenses.md` | Fotos, bandeiras, bibliotecas, fontes e malhas, cada um com a licença (seções 6 e 7). |
| `CLAUDE.md` | Regras do projeto para quem contribui com agentes. |

## 9. Formulários, modelo de PR e configurações do GitHub

| Arquivo | O que faz |
|---|---|
| `.github/ISSUE_TEMPLATE/data-correction.yml` | "Pedir correção": página ou número, período, o que está errado, link da fonte oficial com o valor certo (obrigatório) e a data em que a fonte foi aberta; rótulo `data-correction`. O botão de cada página abre este formulário já preenchido pela URL. |
| `add-source.yml` | "Acrescentar fonte": órgão e base, link oficial, licença ou termo de uso, frequência, ano de referência, unidade, e qual número do site a base sustenta. |
| `new-state.yml` | "Cobrir os municípios de um estado": a UF e o caminho já feito em SC e no RS (`fetch_municipal_series.py --uf`, `build_municipal_series.py --uf`, `build_municipal_federal.py --uf`, `build_mayors.py --uf`, `build-geo-state.cjs`), cada passo com a checagem ao centavo e o controle que falha; prefeitos desde 2020 (D80); fotos com crédito; rótulos `new-state` e `uf:xx`. |
| `new-case.yml` | "Propor um caso (obra)": obra e local; documentos oficiais com link (contrato, aditivos, pagamentos); empresas com CNPJ; quem assinou pelo governo e quem governava, só com papel em documento oficial (D48); achados de órgãos de controle com a situação jurídica; fotos com licença livre; projeto comparável com a fonte do custo. Texto do formulário: "diferença sem explicação", nunca "desvio" sem decisão oficial. Rótulos `new-case` e `needs-source`. |
| `method-proposal.yml`, `bug-report.yml`, `config.yml` | "Proposta de método" (abre a janela de comentário), "Defeito na página ou no código", e issue em branco desligada, com link para Discussions. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Checklist em que item não marcado exige justificativa: fonte oficial com link, ano de referência e data de coleta; o script refaz o JSON; checagem ao centavo e controle que falha, com a saída colada; total igual ao total oficial; nenhum texto toma partido; foto com licença e crédito; identificadores em inglês e interface em português; DCO. |
| `.github/CODEOWNERS` | O autor como dono de tudo, na fase 0. |
| Workflows | `pages.yml` (publicação, seção 10); `checks.yml` (esquema de proveniência, totais oficiais, tamanho de arquivo, DCO e varredura de segredos que só mostra nomes); `scorecard.yml`. Nunca `pull_request_target` com o código do PR. O DCO é conferido por um workflow do próprio repositório, sem instalar aplicativo de terceiros (a pesquisa citava o app DCO; o workflow faz a mesma checagem sem dar permissão a terceiros). |
| Rótulos | Os padrões do GitHub mais `data-correction`, `new-source`, `method-change`, `needs-source`, `new-state`, `new-case`, `uf:ac` a `uf:to` e `difficulty:low`, `difficulty:medium`, `difficulty:high`. |
| Quadro de cobertura | GitHub Projects público, um cartão por estado: municípios, prefeitos e casos, com quem está cuidando. |

## 10. Publicação no GitHub Pages (D56)

- O workflow `pages.yml` roda a cada merge na `main` e sob comando manual: instala Python, roda os três construtores da prévia, copia a prévia mais recente como `index.html` junto com `assets/`, envia o pacote e publica. Sem segredos; permissões só de Pages.
- Qual prévia é a home fica numa única linha do workflow, trocada a cada rodada nova.
- Tamanho do site publicado: cerca de 150 MB, abaixo do limite de 1 GB.
- Depois da primeira publicação: abrir o endereço na largura da janela do autor e em 420 px, e medir se o Pages entrega o pacote comprimido.

| Banda (limite flexível de 100 GB por mês) | Primeira visita | Visitas por mês |
|---|---|---|
| Pacote sem compressão | 85 MB | cerca de 1.100 |
| Pacote com gzip (medido aqui: 17,5 MB) | 17,5 MB | cerca de 5.700 |

A compressão do Pages não está confirmada; só a primeira publicação mostra. Se a banda apertar: o pacote dividido por estado (D55) ou o Cloudflare Pages (nota de GD46).

## 11. Antes do primeiro commit

1. **Varredura de segredos**, por script Python sobre o que seria versionado (já com o `.gitignore`): chaves de nuvem, tokens do GitHub, chaves privadas, arquivos `.env`, atribuições do tipo `api_key`, `secret`, `password` ou `token` com valor, URLs com usuário e senha. Mostra só arquivo, linha e nome da regra, nunca o valor. Controle: uma chave falsa plantada numa cópia de teste tem de ser pega.
2. **Dados pessoais e nomes**: o email, o telefone e os caminhos da máquina do autor; nenhum projeto além do Brasil-Imposto citado (D98); nenhuma candidatura de 2026; nenhum arquivo da seção 4. Cada busca provada antes com um caso plantado.
3. **Travessões**: zero na prosa dos documentos novos, com linha de controle.
4. **Tamanho**: nenhum arquivo acima de 50 MiB; total do repositório.
5. **Reconstrução limpa**: copiar só o que seria versionado para uma pasta temporária, rodar os três construtores, abrir a prévia pelo caminho do arquivo na largura da janela do autor e em 420 px, e comparar com a prévia de hoje.
6. **`git init` e um commit local**, com assinatura do DCO. Nada de push.

## 12. Ordem de execução depois da aprovação

1. Plano escrito (`/writing-plans`), para leitura do autor.
2. Limpeza no lugar: seção 4 para `private/`, nomes e chaves em inglês, prévia refeita e conferida.
3. Documentos da seção 8 e arquivos da seção 9.
4. `.gitignore` e as checagens da seção 11.
5. Commit local.
6. **Só com a ordem do autor:** o autor cria a organização `brasil-imposto` no navegador (o único passo sem API); o agente cria o repositório, faz o push e configura pelo `gh` as regras da `main`, os rótulos, o Pages, o Discussions, o relato privado de falha e o quadro de cobertura; o autor liga o 2FA obrigatório e cria as quatro categorias de Discussions (dois cliques sem API); o agente abre o site e confere nas duas larguras.

## 13. Itens à parte, achados no caminho

| # | Item | Estado |
|---|---|---|
| 1 | Brutos fora dos caches listados | Decidido (D98): fora do git, na seção 5. |
| 2 | Bandeiras sem registro de fonte e licença | Feito em 2026-10-06 (D98): as 27 dos estados já eram idênticas às do Wikimedia Commons; as 30 dos países foram trocadas pelas oficiais (a de Honduras estava desatualizada), todas em domínio público, com `credits.json`; o mapa usa a proporção real de cada bandeira. |
| 2b | RR, AC e PA não abriam | Feito em 2026-10-06 (D98): o painel quebrava no vice-governador vago (o vice tinha assumido o governo). Agora aparece "Cargo vago", com a data e o motivo oficial. Os 27 estados abrem em 2026, e os seis estados com vaga em 2022 (AL, CE, MA, PA, PI e TO) abrem em 2022. |
| 3 | Foto da Fazenda sob CC BY-ND 3.0, reduzida para 200 px | Em aberto (decisão 10). A cópia do Wikimedia Commons marcada como domínio público usa uma marca do governo dos Estados Unidos, que não vale para foto do governo brasileiro; as fotos CC BY-SA disponíveis são de grupo e não dizem quem é quem. |
| 4 | Referências a outros projetos | Feito em 2026-10-06 (D98): removidas de todos os arquivos. |
| 5 | Candidaturas de 2026 no dado | Feito em 2026-10-06 (D98). Achado no caminho: a nota da ETE Insular mostrava essas candidaturas na tela, contra D36; corrigida. |

## 14. Fora desta spec

- O site em Astro (D55), com spec própria.
- A atualização mensal dos dados por Action (D55), que vem com o site; até lá os pipelines rodam na máquina do mantenedor.
- O servidor das notas (D56): só documentado em `docs/future-work.md`.
- Pedido de doação e domínio próprio.

## 15. Riscos

- **Banda do Pages**, com o pacote de 85 MB (seção 10).
- **Histórico que cresce**: os JSON grandes (o maior tem 38,5 MB) são reescritos a cada atualização; D55 divide por entidade.
- **Governo troca arquivos**: um pipeline refeito pode dar outro número; o manifesto dos brutos (decisão 7) mostra quando isso aconteceu.
- **"Pedir correção" exige conta no GitHub**: dito na própria página do formulário.
- **Exposição política**: o 2º turno é em 25 de outubro e o projeto não tem data de lançamento (D53); as regras de D51 e o `GOVERNANCE.md` valem desde o primeiro commit.
