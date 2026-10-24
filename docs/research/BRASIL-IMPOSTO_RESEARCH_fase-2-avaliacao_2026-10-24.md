# Fase 2: avaliação do projeto como open source (2026-10-24)

Issue #64. Pedido do mantenedor de 2026-10-24: elevar o Brasil·Imposto a um padrão profissional de engenharia, manutenção,
segurança, colaboração e confiabilidade, sem contradizer a Fase 1. A Fase 1 é a auditoria de confiança e a spec
`docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_confianca_2026-10-23.md`, que este documento chama de "spec de confiança".

Este relatório só mede e recomenda. As mudanças propostas estão na spec
`docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_fase-2-profissionalizacao_2026-10-24.md`. Pela regra do projeto, nenhuma mudança de
código ou de workflow começa antes da aprovação da spec.

Legenda usada abaixo:
- **medido:** conferido nesta sessão, com o comando ou a leitura citados.
- **lido:** tirado de um documento do repositório, sem rodar nada.
- **recomendado:** proposta ainda não implementada.

## 1. Estado inicial (ramo `staging` em `7a239b1`, 2026-10-24)

### 1.1 O que já existe e funciona

| Área | Estado | Como foi conferido |
|---|---|---|
| Fluxo de mudança | Todo pull request vai para o `staging`; a promoção para a `main` é um pull request "release" | lido (`CONTRIBUTING.md`, #60) |
| Regras dos ramos | `main` e `staging`: pull request obrigatório, sem force-push, sem apagar, checks `ci` e `dco` obrigatórios; `main` com histórico linear; ninguém dispensa as regras | medido (API de rulesets) |
| Aprovação humana | 0 aprovação exigida nas duas regras | medido; é o item G2 da spec de confiança |
| Testes no pull request | Job `ci`: 80 testes de `pipelines/tests`, 30 do livro-caixa, os arquivos de entidade conferidos pelos esquemas, o site Astro (tipos, `check`, testes, build), e as páginas versionadas iguais ao que os construtores fazem | lido (`ci.yml`) e medido (rodadas do #59) |
| Assinatura | Job `dco` em todo pull request | lido |
| Análise de código | CodeQL na configuração padrão (actions, JavaScript e TypeScript, Python), semanal e em todo pull request | medido (API) |
| Relato de falha | Relato privado do GitHub ligado; `SECURITY.md` explica o caminho | medido (API) e lido |
| Ações de terceiros | `ci.yml` fixa as ações por commit; `pages.yml` usa etiquetas (`@v4`, `@v5`, `@v3`) | lido; é o item D1 da spec de confiança |
| Permissões | `ci.yml` e `dco.yml` com `contents: read`; `staging-dispatch.yml` com `{}`; `pages.yml` dá `pages: write` e `id-token: write` aos dois jobs, inclusive ao de montagem | lido; também é o item D1 |
| Atualização de dependências | Não há `dependabot.yml` | medido; é o item D2 |
| Interruptores | `data/features.json` com esquema; uma função ligada só no staging fica fora da produção, conferido com controle | lido (#52, #59) |
| Proveniência dos dados | 84 de 90 arquivos JSON de `data/` têm uma chave de fonte ou URL; 62 têm uma chave de data de coleta | medido (varredura das chaves) |
| Esquemas | `schemas/` com 7 esquemas (caso, país, estado, município, pessoa, comum, interruptores), usados pela exportação de entidades e pelo `ci` | lido |
| Governança | `GOVERNANCE.md` com quatro fases e um só mantenedor hoje; regras de neutralidade; mudança de método com janela de comentário; `CODEOWNERS` com um dono para tudo | lido |
| Formulários | Sete formulários de issue, entre eles "Pedir correção" e "Proposta de método"; modelo de pull request com fontes, capturas e lista de conferência | lido |

### 1.2 O que falta ou está frágil

| Achado | Efeito | Já previsto na Fase 1? |
|---|---|---|
| `CONTRIBUTING.md` tem 18 linhas e manda para a página da organização; não diz como preparar o ambiente, rodar os testes nem diagnosticar uma falha | Quem chega precisa ler o README inteiro e adivinhar o resto | Em parte (F1) |
| As variáveis das sondas (`PW_CORE`, `CHROME_HEADLESS`, `CDN_MIRROR`) e o uso das sondas de navegador estão só nos comentários dos scripts | Ninguém de fora roda as conferências de tela | Sim (F1) |
| Não há um catálogo dos indicadores: a definição de "Enviou", "Voltou", "Por habitante", "Proporção", "Estimativa do DF" e das médias dos 3 Poderes vive no código das páginas e nas notas do mapa | Uma regra mudada num lugar pode divergir de outro; quem lê não tem uma página de definições | Não |
| `pages.yml` monta e publica sem rodar nenhum teste; a proteção é só o `ci` obrigatório no pull request | Um dado bruto mudado direto na `main` por um pull request com `ci` verde publica; um construtor que falha impede a publicação (falha segura nesse caso), mas um dado incompleto e bem formado passa | Não |
| As correções de dados não têm um registro público (o que estava errado, o que mudou, quando, a fonte) | Jornalistas e pesquisadores não sabem se um número que citaram mudou | Não |
| O registro de decisões para no D154; as aprovações de 2026-10-23 (staging, Início mais curta, spec de confiança) não estão nele | A história pública das decisões está atrás do que aconteceu | Sim (G1) |
| Não há tarefas para iniciantes: as 13 issues abertas são grandes ou de dados | Ninguém de fora tem por onde começar | Não |
| Nenhum linter ou formatador | Estilo mantido à mão; é aceitável hoje, com um só autor | Não |

### 1.3 O caminho de quem nunca contribuiu (medido num clone limpo)

| Pergunta do pedido | Resposta | Evidência |
|---|---|---|
| Entender o propósito e a arquitetura rápido? | Propósito sim (README, seções "O que é" e "As páginas"); arquitetura em parte: a tabela de pastas existe, falta um desenho de como dados viram páginas | lido |
| Preparar o ambiente com instruções reproduzíveis? | Sim para as páginas: os quatro construtores e o passo do Node rodaram sem erro em cerca de 20 s num clone limpo; Python 3.12 e Node 24 estão fixados (`.python-version`, `.nvmrc`), e as bibliotecas em `uv.lock` | medido |
| Executar testes e validações? | Os testes sim (`uv run python -m unittest discover -s pipelines/tests`, cerca de 40 s); as sondas de navegador não, sem documentação | medido |
| Gerar o site e os dados? | O site sim (`build-site.py --profile production\|staging`); os dados brutos só pelos guias de cada pipeline (`pipelines/README.md` cobre o balanço de 2024; #12 pede os outros) | medido e lido |
| Achar onde um número é coletado e transformado? | Difícil: não há um índice "arquivo de dados, script que o faz, fonte, página que o mostra" | lido |
| Fazer uma mudança pequena sem entender tudo? | Sim em texto e estilo das páginas (cada página tem seu construtor e as conferências pegam a deriva); difícil em dados | medido no #59 |
| Submeter e entender a revisão? | O modelo de pull request é claro; quem revisa e quantas aprovações vale só está na página da organização | lido |

## 2. O que as referências fazem e o que serve aqui

O critério é a prática, não o tamanho da comunidade. Cada linha diz se serve ao Brasil·Imposto, com um mantenedor e poucos
recursos.

| Projeto | Prática | Serve aqui? |
|---|---|---|
| OpenFisca | Parâmetros de regras públicas em arquivos de dados, cada valor com data de vigência e referência à norma; testes de regra escritos como casos de entrada e saída esperada | **Sim, é a mais próxima.** Um catálogo de indicadores com definição, fonte, natureza (individual, agregado, estimado) e casos de teste por indicador (spec, P3 e P4) |
| OpenFisca | Documentação das regras gerada a partir dos próprios parâmetros | Sim: a página de definições sai do catálogo, então não diverge do código (P4) |
| OpenStreetMap | Toda edição é um conjunto de mudanças com comentário e fonte; atribuição obrigatória pela licença dos dados | Já existe em parte: o modelo de pull request pede a fonte. Falta o registro público de correções (P5) |
| OpenStreetMap | Um grupo próprio cuida das disputas sobre dados | Ainda não: há um mantenedor. `GOVERNANCE.md` já prevê a evolução; documentar como uma disputa corre hoje (P6) |
| Bitcoin Core | Revisão por mais de uma pessoa antes do merge; mudanças pequenas e focadas; notas de versão a cada lançamento; builds reproduzíveis | Builds reproduzíveis já existem (o `ci` confere as páginas byte a byte). Notas de versão a cada promoção (G3 da spec de confiança). A segunda revisão depende de um segundo mantenedor (G2) |
| Home Assistant | Donos por área no `CODEOWNERS`; um guia de desenvolvimento separado do guia do usuário; uma escala de qualidade por integração | Donos por área quando houver pessoas (G4). Guia de desenvolvimento sim (P1). A escala de qualidade vira, aqui, o nível de conferência de cada base de dados (no catálogo, P3) |
| VS Code | Guia de contribuição com o ambiente, os comandos e o diagnóstico; issues marcadas para iniciantes; plano de iteração público | Guia sim (P1); tarefas iniciais sim (P7); o plano de iteração é o roteiro da seção 6 numa issue fixada |

Fica de fora: contêiner de desenvolvimento, que o ambiente atual (Python e Node com versões fixadas) não pede; bots de triagem,
que um projeto deste tamanho não precisa; e qualquer selo sem uma verificação por trás.

## 3. Integração entre as páginas

Medido no código atual:

- **Compartilhado e bom:**
  - o cabeçalho, o rodapé e o carregador saem de um só módulo (`site_chrome.py`, `map_loader.py`);
  - as notas do mapa saem de um só modelo (`map-notes-model.js`), que a Início e a página Como ler o mapa usam (#59);
  - os interruptores de `data/features.json`;
  - os esquemas de entidade do site Astro.
- **Duplicado ou implícito:**
  - a definição de cada indicador (o que entra em "Voltou", o teto do DF, como se arredonda uma média) está no código de cada
    página e nos textos das notas;
  - não há identificador estável de indicador: as chaves dos dados (`perPersonMonth`, `balance`) e os nomes da tela são as únicas
    referências;
  - a natureza do valor (oficial, agregado por nós, estimado) aparece na tela do DF ("estimativa"), mas não é um campo comum dos
    dados.

Recomendação (spec, P3 e P4): um catálogo de indicadores. Ele é um contrato, não um modelo único: cada base de dados continua com
o seu formato, e o catálogo diz, para cada indicador:
- o identificador estável;
- o nome na tela;
- a definição em português;
- a unidade;
- a natureza (individual, agregado, estimado);
- as fontes;
- o arquivo e a chave de onde sai;
- as páginas que o mostram;
- a decisão que o fixou (D1 em diante).

Um teste confere que toda chave citada existe nos dados e toda fonte citada existe em `release-dates.json`. Nenhum número muda.

## 4. Automação, segurança e cadeia de fornecimento

| Tema | Estado | Recomendação | Onde |
|---|---|---|---|
| Testes em pull request | Feitos | Manter | |
| Esquemas | Feitos para entidades e interruptores | Estender ao catálogo | P3 |
| Integridade dos dados | Parcial (DF, totais e Judiciário em testes; A1 e B1 da Fase 1 ampliam) | Seguir a ordem da spec de confiança | A1, B1 |
| Proveniência | 84 de 90 arquivos com fonte, 62 com data | C2 da Fase 1 e #10 | C2 |
| Links de fonte | Sem checagem | Checagem semanal que abre uma issue, nunca bloqueia | C3 |
| Publicação com falha segura | A publicação não roda testes | Rodar os testes de dados e a conferência das páginas no job de montagem do `pages.yml` antes do upload | P2 (pede o sim do mantenedor: mexe em workflow) |
| Ações e permissões do `pages.yml` | Etiquetas e permissão ampla | Fixar por commit e dar `pages` e `id-token` só ao job de deploy | D1 |
| Dependências | Sem atualização automática | Dependabot para Actions, pip (uv) e npm, semanal, agrupado | D2 |
| OpenSSF Scorecard | Não roda | Rodar com resultado só na aba de segurança, sem selo até a nota refletir as correções acima | D3 (#11) |
| Linter e formatador | Nenhum | Não agora. Avaliar o Ruff só nos pipelines quando houver um segundo colaborador frequente | decisão do mantenedor (Q-F2-3) |
| Segredos | Um segredo (`STAGING_DISPATCH_TOKEN`), usado só pelo workflow de staging, com permissão vazia no workflow; o varredor de e-mail do projeto roda nos testes | Documentar no `SECURITY.md` quem trata cada alerta (CodeQL, Dependabot, varredura de segredos) e em quanto tempo | P8 |

## 5. Governança e documentação

`GOVERNANCE.md` descreve a estrutura real (um mantenedor, fases com gatilhos) e não promete comunidade que não existe: isso está
certo e fica.

Faltam quatro coisas:
- quem aprova e integra hoje, dito no repositório e não só na página da organização (P1);
- como corre uma disputa sobre um dado ou uma interpretação (P6);
- onde fica o registro das correções (P5);
- por onde um iniciante começa (P7).

Para cidadãos, jornalistas e pesquisadores:
- a página Como ler o mapa já explica as notas e as datas;
- falta uma página "Definições" por indicador, gerada do catálogo (P4), e o registro de correções (P5);
- o README já tem resumo em inglês;
- o guia de desenvolvimento (P1) ganha um resumo em inglês, para atrair colaboradores de fora.

## 6. Roteiro de três meses (recomendado)

| Mês | Entregas | Depende de |
|---|---|---|
| 1 | Aprovação desta spec; P1 (guia de desenvolvimento); D1 com P2 (`pages.yml` seguro e com falha segura); D2; G1 em dia; P7 (as tarefas iniciais publicadas) | o sim do mantenedor |
| 1 e 2 | A ordem da spec de confiança: A1, A4, B1, B4, C3, F1 | as decisões Q-A2, Q-A3 e Q-C1 já pedidas |
| 2 | P3 (catálogo de indicadores, com teste); P4 (página Definições); P5 (registro de correções); P8 (tratamento de alertas no `SECURITY.md`) | as decisões Q-F2-1 e Q-F2-2 |
| 3 | D3 (Scorecard); C2 e #10 (proveniência no `ci`); P6 (disputas); revisão das fases do `GOVERNANCE.md` com quem tiver chegado | as entregas anteriores |

## 7. Limitações desta avaliação

- Não medi tempos de revisão nem contribuições externas: não há colaboradores externos ainda.
- A rede da sessão bloqueia os sites das fontes oficiais, então a checagem de links ficou de fora.
- A configuração de alertas de dependência do repositório não pôde ser lida pela API daqui (acesso negado pelo proxy).
- As práticas das referências estão descritas pelo que elas publicam sobre o próprio processo, não por uma medição.

## In English

Phase 2 assessment of Brasil·Imposto as an open-source project.

What already works:
- branch rulesets with required `ci` and `dco`;
- 80 Python tests plus the site and data checks on every pull request;
- CodeQL;
- private vulnerability reporting;
- byte-for-byte reproducible pages;
- feature switches.

Gaps:
- a thin `CONTRIBUTING.md` and no developer guide;
- no shared indicator catalogue, so definitions live in page code;
- publishing runs no tests;
- no public log of data corrections;
- no starter tasks;
- `pages.yml` pinning and permissions, and no dependency updates (both already planned in Phase 1).

Recommendations are in the Phase 2 spec. Nothing is implemented before the maintainer approves it.
