# Spec: Fase 2, profissionalização do projeto (2026-10-24)

Issue #64. Avaliação: `docs/research/BRASIL-IMPOSTO_RESEARCH_fase-2-avaliacao_2026-10-24.md`. Esta spec completa a de confiança
(`BRASIL-IMPOSTO_SPEC_confianca_2026-10-23.md`, "spec de confiança"): não repete os itens dela, só os põe na ordem desta fase.

Situação: **aprovada (D169, 2026-10-25).** Feitos: P1 (#90); P7, as issues #91 a #94 (a tarefa 5 da seção 5 veio no #90). P6 espera o sim ao texto (Q99); P2, P3, P5 e P8 esperam Q-F2-4, Q-F2-1, Q-F2-2 e Q-F2-5 (perguntas 9, 6, 7 e 10 da prévia de perguntas de 2026-10-25).

## 1. Regras

Valem as regras da seção 1 da spec de confiança:
- um pull request por item, para o `staging`;
- testes primeiro, cada um com um controle plantado;
- nada de refatorar o que funciona;
- texto da tela e método só com o sim do mantenedor;
- commits com `-s`.

E duas regras desta fase:
- **Nenhum número publicado muda.** Um item que mudaria um número para e vira pergunta.
- **Uma ferramenta nova só entra com dono e tratamento definidos:**
  - quem lê o alerta;
  - em quanto tempo;
  - o que bloqueia e o que só avisa.

## 2. A ordem

Os itens P são desta spec; os outros códigos são da spec de confiança.

| # | Item | Problema | Risco | Esforço | Depende de |
|---|---|---|---|---|---|
| P1 | Guia de desenvolvimento no `CONTRIBUTING.md` | Quem chega não acha o ambiente, os comandos nem o diagnóstico | baixo | baixo | nada |
| F1 | Um comando para preparar e conferir (spec de confiança) | Os comandos estão espalhados | baixo | baixo | P1 |
| D1 + P2 | `pages.yml` seguro e com falha segura | Ações por etiqueta, permissão ampla, publicação sem teste | médio | baixo | Q-F2-4 |
| D2 | Atualização de dependências (spec de confiança) | Nada avisa uma versão vulnerável | baixo | baixo | nada |
| P7 | Tarefas iniciais publicadas | Nenhuma porta de entrada | baixo | baixo | o sim desta spec |
| P3 | Catálogo de indicadores, com esquema e teste | Definições espalhadas pelo código | médio | médio | Q-F2-1 |
| P4 | Página Definições, gerada do catálogo | Cidadãos não têm a definição de cada número | baixo | médio | P3, texto aprovado |
| P5 | Registro público de correções | Quem citou um número não sabe se ele mudou | baixo | baixo | Q-F2-2 |
| P8 | Tratamento dos alertas no `SECURITY.md` | Alertas sem dono documentado | baixo | baixo | D2 |
| P6 | Como corre uma disputa sobre dado ou interpretação | Não está escrito | baixo | baixo | nada |
| D3 | OpenSSF Scorecard (#11) | Medir a cadeia de fornecimento | baixo | baixo | D1, D2 |

A ordem da spec de confiança (A1, A4, B1, B4, C3 e os outros) segue em paralelo e não é alterada por esta.

## 3. Os itens

### P1. Guia de desenvolvimento no `CONTRIBUTING.md`

- **Problema:** o `CONTRIBUTING.md` tem 18 linhas e manda para a página da organização. Quem quer mudar o código não acha ali:
  - o ambiente;
  - os comandos;
  - as conferências;
  - o diagnóstico;
  - quem revisa.
- **Arquivos:** `CONTRIBUTING.md` (acrescentar; o que existe fica).
- **O que entra:**
  - a seção "Para desenvolver", com o que instalar (Python 3.12 e uv, Node 24, Chromium só para as sondas);
  - os comandos medidos num clone limpo (montar as páginas, rodar os testes, montar os dois perfis do site);
  - o mapa "um dado vira página": `pipelines/` faz `data/`, os construtores fazem as páginas e os pacotes de `assets/`, e o
    `build-site.py` monta o site;
  - as sondas e suas variáveis;
  - os erros mais comuns e o que fazer;
  - quem revisa hoje e o que o `ci` exige;
  - um resumo em inglês.
- **Aceitação:** uma pessoa (ou uma sessão sem contexto) segue só o `CONTRIBUTING.md` num clone limpo e chega aos testes verdes e ao
  site montado. O pull request traz a saída de cada comando.
- **Riscos:** o texto envelhecer. Mitigação: um teste confere que cada script citado existe (controle: um nome trocado falha).

### D1 + P2. `pages.yml` seguro e com falha segura

- **Problema:**
  - D1: as ações estão fixadas por etiqueta;
  - D1: `pages: write` e `id-token: write` valem também para o job que monta o site;
  - P2: a publicação não roda nenhum teste. Um dado incompleto mas bem formado chega à produção se o `ci` do pull request passou
    antes de outra mudança, ou por uma execução manual.
- **Arquivos:** `.github/workflows/pages.yml`; o workflow do staging em `deploy/staging/deploy.yml` recebe o mesmo.
- **O que muda:**
  - as ações passam a ser fixadas por commit, como no `ci.yml`;
  - as permissões ficam `contents: read` no nível do workflow, e `pages: write` e `id-token: write` só no job de deploy;
  - o job de montagem roda, antes do upload, os testes de dados (`pipelines/tests`) e a conferência de que as páginas montadas
    são as versionadas;
  - se algo falha, não há upload, e o site no ar continua o anterior.
- **Aceitação:**
  - uma execução com um teste plantado para falhar não publica, e o site no ar não muda;
  - uma execução normal publica igual a hoje, conferido byte a byte com a montagem anterior.
- **Riscos:** a publicação fica cerca de um minuto mais lenta. Mexe em workflow, por isso pede o sim (Q-F2-4).

### P3. Catálogo de indicadores

- **Problema:** a definição de cada número da tela vive no código da página e nas notas. Não há identificador estável nem um campo
  comum que diga se o valor é oficial, agregado pelo projeto ou estimado.
- **Arquivos:** novos `data/indicators.json`, `schemas/indicators.schema.json` e um teste em `pipelines/tests/`. Nenhum
  arquivo de dados existente muda.
- **O que entra, por indicador:**
  - identificador estável em inglês (por exemplo `state.federal.sent`, `state.federal.returned`, `state.federal.per_capita_month`,
    `state.federal.ratio`, `df.federal.estimate_cap`, `judiciary.court.average_pay`);
  - nome na tela, definição em português e unidade;
  - natureza: `individual`, `aggregate` ou `estimate`;
  - fontes, com o identificador de `data/release-dates.json`;
  - de onde sai (arquivo e chave);
  - páginas que o mostram;
  - decisões (D1 em diante) e limitações conhecidas.
- **Primeira versão:** só os indicadores do mapa e dos 3 Poderes que já estão na tela. Os outros entram aos poucos.
- **Aceitação:** o teste confere, cada coisa com um controle que falha:
  - o esquema;
  - que toda chave citada existe no arquivo citado;
  - que toda fonte existe em `release-dates.json`;
  - que toda decisão citada existe no registro de decisões;
  - que todo indicador `estimate` tem a limitação escrita.
- **Riscos:** o catálogo virar um segundo lugar para mudar. Mitigação: o teste falha quando a chave some ou muda, e P4 gera a
  página a partir dele.
- **Natureza diferente, contrato diferente:** o catálogo não força um modelo único. Ele só aponta para cada base no formato dela.

### P4. Página Definições

- **Problema:** um cidadão não acha, sem ler o código, o que é cada número.
- **Arquivos:**
  - um construtor novo em `docs/superpowers/tools/`;
  - a página nova em `docs/superpowers/previews/`;
  - o link no rodapé (`site_chrome.py`).
- **O que entra:**
  - para cada indicador do catálogo: o nome, a definição, a natureza, as fontes com link e data e as limitações;
  - links de ida e volta com a página Como ler o mapa.
- **Aceitação:**
  - a página é igual ao que o construtor faz (o `ci` confere);
  - cada definição na tela é a do catálogo, texto por texto;
  - as conferências de tela de sempre em 1440 e 420 px.
- **Riscos:** é texto novo na tela, então o texto vai ao mantenedor antes (regra do `GOVERNANCE.md`).

### P5. Registro público de correções

- **Problema:** quando um número publicado muda por correção, não há um lugar que diga:
  - o que estava;
  - o que ficou;
  - por quê;
  - quando;
  - com que fonte.
- **Arquivos (opção recomendada, Q-F2-2):** `data/corrections.json`, com esquema, e uma seção no README que aponta para ele. O
  formulário "Pedir correção" ganha a frase dizendo que a correção aceita entra no registro.
- **Aceitação:**
  - o teste do esquema;
  - um teste de que toda correção cita o pull request e a fonte, com controle;
  - a primeira entrada é uma correção real já feita, se o mantenedor indicar uma.
- **Riscos:** nenhum número muda por este item.

### P6. Disputas sobre dados ou interpretação

- **Problema:** `GOVERNANCE.md` tem a mudança de método, mas não diz como corre uma disputa sobre um dado ou uma leitura.
- **Arquivos:** `GOVERNANCE.md` (uma seção).
- **O que entra, a estrutura real de hoje:**
  - a disputa vira issue, com as fontes dos dois lados;
  - o mantenedor decide com a fonte oficial;
  - a decisão entra no registro com o número D;
  - se o dado muda, o registro de correções recebe a entrada.
- **Aceitação:** o texto descreve só o que existe e diz o que muda quando houver mais pessoas (a fase 2 do próprio
  `GOVERNANCE.md`).
- **Riscos:** é texto de governança, então só com o sim do mantenedor ao texto.

### P7. Tarefas iniciais

- **Problema:** as 13 issues abertas são grandes; ninguém de fora tem por onde começar.
- **O que entra:** as issues da seção 5, com o rótulo `difficulty:low`, que o repositório já usa (#11). Cada uma traz:
  - o problema;
  - os arquivos;
  - os critérios de aceitação;
  - como conferir.
- **Aceitação:** cada issue pode ser feita sem ler o resto do sistema, e o guia P1 basta para preparar o ambiente.

### P8. Tratamento dos alertas

- **Problema:** CodeQL já roda e o Dependabot vai rodar, mas não está escrito quem trata cada alerta nem em quanto tempo.
- **Arquivos:** `SECURITY.md` (uma seção).
- **Recomendação:**
  - CodeQL alto ou crítico bloqueia o merge e é tratado no mesmo pull request;
  - Dependabot de segurança é tratado em até 7 dias;
  - o resto dos alertas é revisto uma vez por mês pelo mantenedor;
  - a varredura de segredos, se um segredo vazar, troca o segredo antes de qualquer outra coisa.
- **Riscos:** prometer um prazo que um mantenedor sozinho não cumpre. Os prazos acima são a recomendação; o mantenedor escolhe
  (Q-F2-5).

## 4. Decisões do mantenedor

| # | Pergunta | Opções | Recomendação | Impacto |
|---|---|---|---|---|
| Q-F2-1 | Catálogo de indicadores (P3)? | (a) sim, começando pelo mapa e pelos 3 Poderes; (b) sim, tudo de uma vez; (c) não agora | (a) | (a) dá o contrato sem parar o resto; (b) atrasa o resto um mês |
| Q-F2-2 | Onde fica o registro de correções (P5)? | (a) `data/corrections.json` com esquema e seção no README; (b) um arquivo `CORRECOES.md` à mão; (c) só no registro de decisões | (a) | (a) dá para mostrar na tela depois e testar; (b) é mais simples e não testável; (c) mistura método com correção |
| Q-F2-3 | Linter e formatador | (a) não agora; (b) Ruff só nos pipelines, só avisando; (c) Ruff e Prettier em tudo, bloqueando | (a) | (b) e (c) mexem em muitos arquivos de uma vez e não pegam erro de dado |
| Q-F2-4 | Testes antes da publicação (P2) | (a) testes de dados e conferência das páginas antes do upload; (b) só a conferência das páginas; (c) como está | (a) | (a) custa cerca de um minuto por publicação e impede publicar dado que falha nos testes |
| Q-F2-5 | Prazos de alerta (P8) | (a) os da seção P8; (b) só "revisto uma vez por mês"; (c) outros | (a) | um prazo escrito é uma promessa pública |
| Q-F2-6 | Exigir uma aprovação nos rulesets (G2 da spec de confiança) | (a) quando houver um segundo mantenedor; (b) já, com o mantenedor aprovando os pull requests das sessões | (a) | (b) não acrescenta revisão real com uma só pessoa |

## 5. Tarefas iniciais (rascunhos; viram issues depois do sim)

1. **Um teste para os scripts citados no README.**
   - Problema: o README cita comandos; se um script for renomeado, o README mente.
   - Aceitação: o teste lista os scripts citados e falha se um não existe, com um controle que troca um nome.
   - Arquivos: `pipelines/tests/`.
2. **A fonte dos seis arquivos de dados sem chave de fonte.**
   - Problema: os seis arquivos de `data/` sem chave de fonte:
     - `data/df/federal_spending_by_uf_2024.json`;
     - `data/df/federal_spending_by_uf_2025.json`;
     - `data/df/pdad-2024-reports.json`;
     - `data/df/q4_local_2024.json`;
     - `data/federal/bills-2026-summary.json`;
     - `data/features.json`, que é de configuração e fica de fora.
   - Aceitação: cada arquivo ganha a fonte, pelo pipeline que o faz, e a fonte é a que o pipeline já lê, sem número mudado.
   - Depende de C2.
3. **O guia do pipeline de uma base.**
   - Problema: #12 pede guias de cada pipeline.
   - Aceitação: escolher uma base (por exemplo o comércio exterior); o guia diz a fonte, os comandos, o que sai e como conferir,
     e foi seguido num clone limpo.
4. **Texto alternativo das imagens dos casos.**
   - Problema: conferir que toda imagem em `assets/cases/` tem crédito e texto alternativo na página.
   - Aceitação: um teste com controle.
5. **O resumo em inglês do guia de desenvolvimento.**
   - Depende de P1.
   - Aceitação: o resumo cobre o ambiente, os comandos e o fluxo do pull request.

## 6. Critérios de sucesso da fase

Os do pedido do mantenedor, cada um com o item que o atende:

| Critério | Atendido por |
|---|---|
| Um colaborador novo configura o ambiente e roda as verificações seguindo a documentação | P1, F1 |
| As mudanças relevantes são validadas automaticamente | `ci` atual, A1, B1, P2 |
| Os dados compartilhados entre páginas seguem contratos explícitos | P3 |
| As regras metodológicas importantes estão documentadas e testadas | P3, P4, A1, B1 |
| A segurança e a revisão estão claras | D1, D2, P8, G2 |
| As contribuições têm um caminho compreensível | P1, P7 |
| A publicação não troca dado válido por resultado incompleto | P2 |
| As limitações estão registradas | P3, P5, seção 7 do relatório |

## 7. Quem faz o quê

- **Sessão local (D167; a nuvem ficou sem créditos em 2026-10-25), com o sim de D169:** um pull request por item, na ordem da seção 2. Antes de começar um item, conferir se
  ele já tem dono (regra 2 de `.claude/CLAUDE.md`).
- **Mantenedor:**
  - o sim a esta spec;
  - as decisões Q-F2-1 a Q-F2-6;
  - os textos de tela e de governança;
  - os merges.

## 8. Fora desta spec

- funcionalidades novas;
- o site em Astro (#3 a #7; a B0, #2, fechou em 2026-10-24);
- os itens de método da spec de confiança (A2, A3, C1, B3), que já têm as perguntas deles;
- selos de qualquer tipo.

## In English

The Phase 2 spec proposes small, reviewable changes:
- a developer guide;
- safe publishing that fails closed;
- dependency updates;
- an indicator catalogue with schema and tests, plus a definitions page generated from it;
- a public corrections log;
- alert-handling rules;
- a dispute process;
- starter issues.

No published number changes. Six maintainer decisions are listed with options and impact.
