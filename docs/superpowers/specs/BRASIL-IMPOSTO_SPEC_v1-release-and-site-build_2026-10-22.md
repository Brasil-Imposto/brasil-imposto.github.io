# Brasil-Imposto: publicação da v1 e construção do site

Status: **aprovada (D149, 2026-10-22).** Os itens marcados "Feito" foram executados na sessão local, que tinha os arquivos de entrada da máquina do autor. Parte A: esta sessão, até o site no ar. Parte B: o site em Astro, construído numa sessão na nuvem, fase por fase, cada uma com a aprovação do autor.

### Summary (English)

Part A publishes v1 on GitHub under the `brasil-imposto` organization: the fixes that must land before the push (no "a coletar" on the Os 3 Poderes page, no author notes on the public home, the official Durigan photo, English commit messages, a true README), the community files that make the repository ready for contributors (SECURITY, CODE_OF_CONDUCT 2.1 in Portuguese, GOVERNANCE, CODEOWNERS, PR template, issue forms, a DCO check), a public agent guide in `.claude/CLAUDE.md`, the GitHub configuration (org, repository, Pages, security, ruleset, labels, Discussions, coverage board, release `v1.0.0`) and the open work filed as issues. Part B specifies the Astro site decided in D55, to be built in a cloud session: port the approved preview pages with parity (same visible text in every period and state, screenshots at 1440 and 420 px), a typed per-entity JSON contract with English keys and JSON Schema, Python pipelines unchanged in method, CI that blocks a red check, and a phase-by-phase workflow where the owner approves each phase before code. It also lists the skills the cloud session needs and how to load them, since a cloud session does not read the author's machine.

## 1. Base: o que já está decidido

| Registro | O que vale aqui |
|---|---|
| D2, D51, GD48 | Tudo por PR; o autor aprova no início; as quatro regras de neutralidade no `GOVERNANCE.md` |
| D54 | Organização `brasil-imposto`; AGPL-3.0 no código, CC BY 4.0 nos dados e textos; código e commits em inglês, documentação em português com resumo em inglês |
| D55, D56 | Stack: Astro 7, TypeScript estrito, three.js com mapa SVG gerado no build, um JSON por entidade, Python nos dados; hospedagem no GitHub Pages |
| D97, D98, D147, D148 | O que vai a público, o que fica fora, as 12 respostas da rodada de publicação (D148 muda D147: os documentos de comunidade, os formulários e o check do DCO entram na v1) |
| D123, D125 | O bloco de apoio e doação só vai ao ar quando o projeto passar no padrão de D125 |
| D143 | Nada fica "a coletar" na v1: cada item é ✓, ✗ ou "não publicado" |
| Pesquisas | `docs/research/BRASIL-IMPOSTO_RESEARCH_stack_2026-10-01.md` (stack, pesos, riscos) e `..._colaboracao-open-source_2026-10-01.md` (pacote de colaboração) |
| Spec anterior | `BRASIL-IMPOSTO_SPEC_github-publication-and-docs_2026-10-06.md` (seções 8 e 9: conteúdo dos documentos e formulários) |

**Organização, não conta pessoal.** Um repositório de conta pessoal tem só dois níveis, o dono e colaboradores, e a posse não se divide; a própria documentação do GitHub manda passar para uma organização quando se precisa de acesso mais fino ("Permission levels for a personal account repository"). A organização tem vários donos, os papéis Read, Triage, Write, Maintain e Admin, times, 2FA obrigatório para todos e o endereço `https://brasil-imposto.github.io` (site de organização num repositório `<org>.github.io`, "What is GitHub Pages"). É o que permite as fases de `GOVERNANCE.md`, em que o autor passa a ser uma cadeira.

## 2. Parte A: a publicação da v1 (esta sessão)

### A1. Correções antes do push

| # | O quê | Feito quando |
|---|---|---|
| A1.1 | **Os 3 Poderes sem "a coletar" (D143).** A legenda passa de "? a coletar" para "? não publicado", e o rótulo do sinal também; os 6 textos de reserva no código deixam de dizer "a coletar"; os 2 senadores sem mês inteiro de folha mostram "i" com a explicação; o construtor tira dos 21 ocupantes de exemplo da árvore os estados antigos da rodada 2 (16 "unknown"), que a página não mostra mas o JSON público carregava contra o registro de cada pessoa. **Feito em 2026-10-22.** | A sonda `tres-poderes-unknown-probe.cjs` (entra no repositório) conta 0 "a coletar" na árvore e nas 722 fichas; o controle, que apaga o dado de um senador, aparece como um sinal a mais |
| A1.2 | **A home pública sem notas do autor.** O bloco "Apoie" fica fora do site publicado (D125; hoje diz "Só na prévia" e "os botões não levam a lugar nenhum"), e o texto visível perde os códigos internos (D123, D125, Q33 e outros, 14 códigos hoje). A prévia local continua com tudo | A sonda de texto visível da home (a home em 19 períodos e a janela dos 27 estados em ano, mandato e mês): 0 códigos D, Q ou GD e 0 "Só na prévia" no site publicado; a sonda também roda com uma nota plantada, que tem de ser pega. **Feito em 2026-10-22** (PRs #1 e #20, conferido no ar) |
| A1.3 | **Foto de Dario Durigan:** o arquivo oficial sem alteração, com crédito (D148, item 11). **Feito em 2026-10-22** (1000 x 1500 px, da cópia do Internet Archive da página oficial) | `photos.json` com o tamanho real e a nota; o arquivo igual, byte a byte, ao baixado da fonte |
| A1.4 | **Feito em 2026-10-22 (PR #17).** **README verdadeiro.** Hoje diz "Cada página tem Pedir correção", e só Os 3 Poderes tem. Passa a dizer onde há e que o botão nas outras páginas é uma issue aberta. Ganha a seção "Estado do projeto": o que está pronto, o que vem (o site em Astro, Parte B), com link para as issues e o quadro | Leitura do texto contra as páginas |
| A1.5 | **Mensagens dos 4 commits em inglês** (D54), sem o escopo interno `learn`; as linhas do DCO ficam. **Feito em 2026-10-22** | `git log` com as 4 mensagens novas e `Signed-off-by` em todas |

### A2. Arquivos novos no repositório

**Feito em 2026-10-22** (PRs #15 e #16; a declaração do mantenedor no PR #19, D150; perfil de comunidade em 100%).

| Arquivo | Conteúdo |
|---|---|
| `SECURITY.md` | Como relatar falha sem expor: o relato privado de falha do GitHub. Sem email por enquanto (D148): o email do projeto entra quando existir |
| `CODE_OF_CONDUCT.md` | Texto oficial do Contributor Covenant 2.1 em português do Brasil (repositório `EthicalSource/contributor_covenant`, com a atribuição que o próprio texto traz); o contato de conduta é a denúncia de conteúdo aos mantenedores, do próprio GitHub, até existir o email do projeto; mais o anexo do projeto: discussão partidária e ataque a pessoa mostrada no site saem do repositório |
| `GOVERNANCE.md` | Quem decide hoje e como (o motivo por escrito no PR); as quatro fases da spec de 2026-10-06 (seção 2) com os números sugeridos, revisáveis por proposta de método; as quatro regras de neutralidade de D51 e GD48; a regra de quem pode doar; mudança de método com 7 a 10 dias de comentário em Discussions; um quadro de áreas com situação |
| `.github/CODEOWNERS` | O autor dono de tudo (fase 0) |
| `.github/PULL_REQUEST_TEMPLATE.md` | O checklist da spec de 2026-10-06 (seção 9): fonte oficial, script que refaz o JSON, checagem ao centavo com controle, total oficial, neutralidade, foto com licença, identificadores em inglês, DCO |
| `.github/ISSUE_TEMPLATE/` | `data-correction.yml`, `add-source.yml`, `new-state.yml`, `new-case.yml`, `method-proposal.yml`, `bug-report.yml` e `config.yml` (issue em branco desligada, link para Discussions), com os campos da seção 9 da spec de 2026-10-06 |
| `.github/workflows/dco.yml` | Confere o `Signed-off-by` de cada commit do PR, sem aplicativo de terceiros e sem `pull_request_target`. **Feito em 2026-10-22**, testado com dois controles (assinatura de outra pessoa e commit sem assinatura) |
| `.claude/CLAUDE.md` | O guia público para quem contribui com agentes (seção B7). Fica em `.claude/` porque o `CLAUDE.md` da raiz é o caderno local do autor, fora do git |
| `docs/superpowers/tools/tres-poderes-unknown-probe.cjs` | A sonda de A1.1 |
| Esta spec | Em `docs/superpowers/specs/`, para a outra sessão e para quem chegar |

### A3. Checagens antes do push

Cada uma provada antes com um caso plantado que tem de ser pego: segredos (mostra só arquivo, linha e regra); dados pessoais e caminhos da máquina; nenhuma citação do autor; nenhum outro projeto citado (D98); travessões na prosa nova; nenhum arquivo acima de 50 MiB; reconstrução limpa só com os arquivos versionados refazendo as saídas byte a byte; referências de arquivo com maiúsculas e minúsculas exatas (o Linux do Actions diferencia); as sondas de A1.1 e A1.2.

### A4. Configuração no GitHub

**Feito em 2026-10-22**, menos o que depende do autor: exigir 2FA e as permissões da organização.

Pelo `gh`, depois da organização criada pelo autor:

1. **Organização:** nome de exibição "Brasil-Imposto", descrição "Quanto cada estado envia e recebe da União, com dados oficiais e código aberto.", sem email público (D148); permissão base Read; membros não criam repositórios; Actions só da organização e do GitHub; `GITHUB_TOKEN` só leitura por padrão; Actions não cria nem aprova PR. 2FA obrigatório: clique do autor (sem API).
2. **Repositório** `brasil-imposto/brasil-imposto.github.io`, público: só squash merge; branch apagada depois do merge; sign-off obrigatório nos commits feitos pela web; Wiki desligado (edição de wiki não passa por revisão; a documentação vive no repositório); Issues, Discussions e Projects ligados; denúncia de conteúdo aos mantenedores ligada; os tópicos de D148; link do site.
3. **Pages** com fonte "GitHub Actions", ligado **antes** do push, para o primeiro deploy não falhar.
4. **Segurança:** relato privado de falha, proteção contra push de segredos, alertas e atualizações do Dependabot, CodeQL na configuração padrão. Se algum pedir plano pago, para e avisa.
5. **Push** da `main`; acompanhar o workflow do Pages até o fim.
6. **Ruleset da `main`**, depois do push (não tem exceção, nem para o dono): PR obrigatório, 0 aprovações enquanto houver um mantenedor, check do DCO obrigatório e aceito só do GitHub Actions, histórico linear, sem force push e sem apagar.
7. **Rótulos** (seção 9 da spec de 2026-10-06, mais `area:site`, `area:data`, `area:docs`), **issues** de A5, **quadro público "Cobertura"** (um cartão por estado), **release `v1.0.0`** com notas em português e resumo em inglês.
8. **Conferência no ar** em 1440 e 420 px; medir se o `bi-data.js` chega comprimido.
9. Tirar o escopo `admin:org` do token desta máquina.

Cliques do autor no fim: as quatro categorias de Discussions (Perguntas, Ideias, Propostas de método, Anúncios); avatar e imagem de prévia social, escolhidos numa página de opções.

### A5. Issues abertas no dia 1

**Feito em 2026-10-22:** rótulos, issues, o quadro público "Cobertura" (27 cartões) e a release `v1.0.0`.

| Issue | Rótulos |
|---|---|
| Site em Astro, uma issue por fase da Parte B (B6), com link para esta spec | `area:site`, `difficulty:high` |
| Nomes de arquivo e chaves de JSON em inglês (D97, item 9), feito na fase B0 | `area:data` |
| Botão "Pedir correção" em todas as páginas, abrindo o formulário já preenchido | `area:site`, `difficulty:medium` |
| CI de proveniência: esquema, totais oficiais, tamanho de arquivo, manifesto dos brutos com SHA-256 | `area:data`, `difficulty:high` |
| OpenSSF Scorecard | `difficulty:low` |
| Guias dos pipelines (`docs/pipelines/`), `docs/data-sources.md`, `docs/future-work.md`, `docs/credits-and-licenses.md` | `area:docs` |
| Salário de 3 ministros licenciados da Câmara (pagos pela Câmara, fora do SIAPE), como já feito para o senador licenciado | `area:data` |
| Municípios de outros estados, no caminho de SC e RS | `new-state`, `uf:xx` |

## 3. Parte B: o site em Astro (sessão na nuvem)

### B1. Objetivo e critério de aceite

Levar as páginas publicadas para o Astro **sem mudar o que o autor aprovou**. As prévias publicadas são o desenho aprovado e o critério de aceite de cada fase é a paridade: o mesmo texto visível que a prévia, medido pela sonda de texto visível nas combinações dela (a home em 19 períodos, a janela dos 27 estados em ano, mandato e mês), e capturas de tela em 1440 e 420 px olhadas lado a lado. Nada sai do que existe (D59). Diferença intencional só com o sim do autor, listada na fase.

### B2. Stack, com versões fixadas

| Peça | Escolha |
|---|---|
| Site | Astro 7 (7.4.2 no npm em 2026-10-22), saída estática; `tsconfig` estendendo o `strictest` do Astro; a versão do TypeScript que o `astro check` aceita, conferida na documentação do Astro ao montar o esqueleto (o npm já tem a 7.0.2, o compilador novo) |
| Interatividade | TypeScript puro nos scripts do Astro, sem React nem Next; um componente React ou Svelte só onde uma seção virar aplicação, com o sim do autor |
| Mapa | three.js 0.186.1 do npm, mais o mapa SVG gerado no build (d3-geo, Equal Earth, D11) para aparelho sem WebGL; malhas em TopoJSON quantizado |
| Prévia social | Uma imagem por entidade gerada no build a partir do SVG do mapa (`@resvg/resvg-js`) |
| Dados | Python 3.12 com `uv` e `uv.lock`; os métodos e as checagens ao centavo não mudam |
| Testes | Vitest nas funções puras (somas, períodos, o teto do DF), Playwright no navegador (paridade, interação com eventos reais de mouse e toque, acessibilidade com axe), os testes Python existentes |
| Node | A versão que o Astro 7 exige, em `.nvmrc` |

### B3. Contrato de dados

- Um JSON por entidade (Brasil, estado, município, caso, pessoa), com todos os meses de 2019 a 2026 dentro, no lugar do pacote único `bi-data.js` de 85 MB. Pesos medidos na pesquisa de stack (seção 3): cerca de 32 KB na home, 110 KB num estado, 16 KB num município.
- Gerados no build a partir de `data/`, sem versionar (D151): o repositório não guarda uma segunda cópia dos dados.
- Chaves em inglês (D97, item 9); rótulos oficiais usados como valor ficam como a fonte escreve.
- Um JSON Schema por tipo de arquivo em `schemas/`, conferido pelo Python ao gravar e pelo CI a cada PR; os tipos do TypeScript são gerados dos mesmos schemas, para os dois lados nunca divergirem.
- Cada número carrega a fonte (órgão, base, link, data de coleta) no próprio arquivo.

### B4. Estrutura do repositório (alvo)

```
site/        o site em Astro (TypeScript)
pipelines/   os scripts Python de hoje (pipelines e os construtores de docs/superpowers/tools)
data/        os dados publicados (a fonte única) e o manifesto dos brutos; os JSON por entidade são gerados no build (D151)
schemas/     JSON Schema de cada tipo de arquivo
docs/        documentação em português
.github/     workflows, formulários, CODEOWNERS
```

Cada mudança de caminho com `git mv` e todas as referências reescritas no mesmo PR. As prévias saem do repositório na fase B5, depois da paridade (o histórico do git guarda todas).

### B5. Qualidade que bloqueia o merge

- CI em todo PR: `astro check` e `tsc` sem erro, Vitest, testes Python, esquema dos JSON, build, DCO. Check vermelho não entra.
- Sonda de paridade com controle: uma mudança plantada no texto tem de ser pega antes de valer o verde.
- Acessibilidade: WCAG 2.2 AA como meta; modais por teclado; axe sem violação séria.
- Peso no celular: a meta da pesquisa de stack (seção 1, "Meta de peso no celular"), medida no build.
- Todo número na tela com a fonte ao lado; toda soma fecha à mão com os valores como aparecem (D94).

### B6. Fases

Cada fase: brainstorming, a seção da fase escrita, **aprovação do autor**, plano, issues, implementação com testes primeiro, revisão. Nenhum código de uma fase antes do sim do autor para ela.

| Fase | Entrega | Pronto quando |
|---|---|---|
| B0 | Esqueleto Astro, `pipelines/` e `schemas/`, chaves em inglês, CI | Build verde; os JSON novos passam no esquema; as saídas dos pipelines iguais em valor às de hoje |
| B1 | Home: mapa 3D e SVG, períodos, contas do Brasil, janela do estado | Paridade da home e das janelas dos 27 estados pela sonda de texto visível |
| B2 | Páginas de estado, município (SC, RS) e DF por Região Administrativa, com prévia social | Paridade das janelas; uma página e uma imagem por entidade |
| B3 | Casos (obras) e pessoas | Paridade das cartas e fichas |
| B4 | Os 3 Poderes e Como o dinheiro anda | Paridade das duas páginas, sonda de A1.1 verde |
| B5 | O Pages publica o site Astro; as prévias saem | Site no ar conferido em 1440 e 420; links antigos com redirecionamento |

### B7. O guia público para agentes (`.claude/CLAUDE.md`)

Seções: o projeto em três linhas; a stack e a estrutura; as regras do projeto (interface em português do Brasil, identificadores em inglês; texto neutro, "envia mais do que recebe" e "recebe mais do que envia", D45; nenhum número sem fonte oficial; toda soma fecha à mão; todo período funciona; DF por estimativa marcada, D146; quem governava com o mesmo tratamento para todos; nada de afirmação que o dado não sustenta); o fluxo (spec aprovada pelo autor antes de código, plano, testes primeiro, revisão); como conferir (capturas em 1440 e 420 olhadas antes de entregar, toda checagem provada com um controle que tem de falhar, código de saída do comando real, nunca do último da cadeia); onde estão as decisões (`docs/decisions/README.md`) e os padrões aprendidos (`docs/ai/learned-patterns.md`); o que perguntar ao autor em vez de decidir. Sem citações do autor, sem caminhos da máquina, sem outros projetos.

### B8. A sessão na nuvem: skills e ambiente

Uma sessão na nuvem roda numa cópia do repositório e **não lê nada da máquina do autor**: nem as skills de `~/.claude/skills/`, nem o `CLAUDE.md` global, nem plugins. Lê o `CLAUDE.md`, o `.claude/CLAUDE.md` e o `.claude/rules/` do repositório, e as skills ativadas na conta do claude.ai (documentação do Claude Code: "Settings in cloud sessions", "What carries over from your setup", "Skills in Cowork and cloud sessions").

**Skills que o autor sobe na conta do claude.ai** (ficam privadas e valem em toda sessão na nuvem, inclusive nas de projeto):

| Skill | Para quê |
|---|---|
| `brainstorming`, `grill-me` com `grilling` | A seção de cada fase, antes do código |
| `writing-plans`, `to-tickets` | O plano e as issues de cada fase |
| `subagent-driven-development`, `tdd` | Implementar com testes primeiro, uma tarefa por vez |
| `codebase-design`, `domain-modeling` | Módulos profundos, o vocabulário do domínio |
| `frontend-design`, `web-design-guidelines`, `seo-audit` | A interface, a revisão de interface e as páginas com prévia social |

Já vêm na nuvem: `/code-review`, `/security-review`, `/simplify`. Fica fora `web-perf`, que precisa do Chrome DevTools MCP, ausente na nuvem. O autor sobe cada skill pela página de skills do claude.ai.

**Ambiente:** o padrão ("Trusted") alcança os registros de pacotes, o que basta para o site. Os pipelines baixam de sites do governo e rodam na máquina do mantenedor até a atualização mensal pelo Actions (D55); se a sessão na nuvem precisar rodar um, o ambiente ganha a lista desses domínios. O Playwright e o navegador dele entram pelo script de preparação do ambiente.

**A sessão é só do Brasil-Imposto:** um repositório, este (D98).

### B9. Começo da sessão na nuvem (texto para colar)

```
Brasil-Imposto, repositório brasil-imposto/brasil-imposto.github.io. Leia .claude/CLAUDE.md e a Parte B de
docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_v1-release-and-site-build_2026-10-22.md. Comece pela fase B0 com a skill
brainstorming: escreva a seção da fase e me peça aprovação. Nenhum código antes do meu sim. Fale comigo em inglês;
a interface fica em português do Brasil.
```

## 4. Ordem e quem faz o quê

| Passo | Quem | O quê |
|---|---|---|
| 1 | Autor | Aprova esta spec |
| 2 | Autor, em paralelo | Organização no plano Free (contato de cobrança privado, trocável), 2FA obrigatório, `admin:org` no `gh`, "org ok" |
| 3 | Agente | A1, A2 e A3; página de opções do avatar e da prévia social |
| 4 | Agente, com "org ok" | A4 e A5 |
| 5 | Autor | Categorias de Discussions; avatar e prévia social; sobe as skills na conta do claude.ai |
| 6 | Autor | Abre a sessão na nuvem com o texto de B9 |

**Portões que falham sem aviso**, com a saída: o plano Team em vez do Free na criação (escolher "Create a free organization"); o 2FA obrigatório recusado se a conta do autor não tiver 2FA; chamadas da organização com 404 sem o escopo `admin:org`; o push por HTTPS que cai no meio (aumentar `http.postBuffer`, tentar de novo, depois mandar um commit por vez); o bloqueio de segredo da conta (ver só caminho e regra); o deploy do Pages que falha se o Pages não estiver ligado antes; o ruleset criado antes do push bloquearia o próprio push.

## 5. Fora desta spec

O conteúdo novo de cada página (perguntas abertas Q50, Q53, Q56, Q57, Q69 a Q71, entre outras), a fase 2 do livro de fluxos, o servidor das notas (D56), domínio próprio, o email do projeto, o botão "Apoie" com doação por carteira cripto (D123; D125 diz quando o bloco vai ao ar). Cada um tem a sua spec, com o autor.

## 6. Riscos

- **Banda do Pages** com o pacote de 85 MB até a fase B2, que o divide.
- **Paridade cara de medir** com milhares de combinações: a sonda cobre as mesmas combinações de hoje, e as capturas são olhadas, nunca supostas.
- **Ritmo de versões do Astro** (duas versões maiores em 2026): versão fixada, atualização de propósito.
- **Dono único** até a fase 2 de `GOVERNANCE.md`: a garantia final é a licença, que deixa qualquer pessoa copiar e continuar.
