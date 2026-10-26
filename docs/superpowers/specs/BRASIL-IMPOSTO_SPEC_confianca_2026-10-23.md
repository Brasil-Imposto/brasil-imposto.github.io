# Spec: confiança, as correções da auditoria de 2026-10-23

**Summary (English).** The fixes from the trust audit (`docs/research/BRASIL-IMPOSTO_RESEARCH_auditoria-confianca_2026-10-23.md`),
ordered by trust gained per effort, the DF first. One pull request per item, tests first, each test proven by a planted failure
that must make it fail; every pull request body says what was verified and what could not be. No refactor of code that works
and no new feature: where an item changes what the screen says, the text goes to the maintainer before the code. Items that
belong to the repository settings, the private decision log or the organization page are marked for the local session and the
maintainer.

Estado: **aprovada (D169, 2026-10-25).** Feitos: A1 (#72), A4 (#86), B1 (#87), B4 (#97), D1 (#95), F1 (#90) e G1 (#89, #98); D2 em rascunho (#96, espera Q98). Respondidas em 2026-10-26 (D172): Q-A2 (a Rede do dinheiro sai da produção e fica no staging), Q-A3 (o texto proposto), Q-A4 (os valores ao centavo quando a Receita os publicar), Q-C1 (sim), Q-B3 (sim, com a tabela de cada centavo antes do merge) e DF-5 (cada ano com a sua parte no PIB, com a tabela antes). G3: uma versão por dia com produção e uma linha por tarefa no `CHANGELOG.md` (D190); D2: o `dco` aceita a conta `dependabot[bot]` (D188). Dona dos itens da sessão na nuvem desde 2026-10-25: a sessão local (D167).

## 1. Regras de toda correção

- Um pull request por item, para o `staging` se o ramo já existir (spec de staging), senão para a `main`.
- Os testes vêm primeiro. Cada teste tem um controle plantado, que precisa falhar pelo motivo plantado.
- O corpo do pull request diz o que foi verificado e o que não pôde ser, com o motivo.
- Nada de refatorar código que funciona, nada de funcionalidade nova.
- Um item que muda o texto da tela ou um método de cálculo só começa depois de o mantenedor aprovar o texto ou o método
  (`GOVERNANCE.md`).
- Commits com `-s`; identificadores em inglês, texto da tela e documentação em português, sem travessões.

## 2. A ordem

Risco e esforço vêm do relatório. A ordem é a confiança ganha por esforço, com o DF primeiro.

| # | Item | Achados | Risco | Esforço | Quem | Depende de |
|---|---|---|---|---|---|---|
| A1 | O saldo do DF conferido no `ci`, período por período | DF-3 | médio | baixo | sessão local | nada |
| A2 | A Rede do dinheiro com o teto do DF | DF-1 | alto | médio | sessão local, depois do sim ao método | decisão Q-A2 |
| A3 | Um só valor federal no painel do DF | DF-2 | alto | médio | sessão local, depois do sim ao texto | decisão Q-A3 |
| A4 | As diferenças sem explicação, registradas e travadas | DF-4, DF-6, DF-7 | médio | baixo | sessão local | nada |
| D1 | `pages.yml` com as ações por commit e as permissões só no deploy | CI-1, CI-2 | médio | baixo | sessão local | o #52 |
| B1 | O saldo dos 27 estados e o bloco da União conferidos no `ci` | TST-1 | alto | baixo, sobre o A1 | sessão local | A1 |
| B2 | As conferências da Rede e as sondas no `ci` | TST-2, CI-6 | médio | médio | sessão local | A2 |
| C1 | As fontes do lado "Voltou" no painel de cada estado | T-1 | médio | médio | sessão local, depois do sim ao texto | decisão Q-C1 |
| C2 | Data de leitura e URL em todo arquivo de dados | T-2, T-4 | médio | médio | sessão local | nada (#10) |
| C3 | A checagem semanal dos links de fonte | seção 2.3, CI-5 | médio | baixo | sessão local | nada (#10, #12) |
| B3 | Os 3 Poderes: Legislativo e Executivo nas regras do D154 | TST-1, TST-3 | médio | médio | sessão local, depois do sim | decisão Q-B3 |
| B4 | Como o dinheiro anda: as divisões conferidas | TST-1 | baixo | baixo | sessão local | nada |
| C4 | Como o dinheiro anda: o RTN e o SICONFI com link e data | T-3 | médio | baixo | sessão local, depois do sim ao texto | nada |
| D2 | Atualização de dependências | CI-3 | médio | baixo | sessão local | nada |
| F1 | Um comando para preparar e conferir; as variáveis das sondas documentadas | DX-1, DX-3 | médio | baixo | sessão local | o #52 |
| G1 | O registro público de decisões até a última | GOV-1 | médio | baixo | sessão local | nada |
| G2 | Uma aprovação exigida na regra da `main` e do `staging` | SEC-1 | médio | baixo | mantenedor | a fase 1 do `GOVERNANCE.md` |
| G3 | Notas de versão a cada promoção | GOV-4 | baixo | baixo | sessão local | o staging no ar |
| C5 | Os três arquivos de página reconstruíveis | T-6, DX-4 | médio | alto | sessão local | #10 (manifesto dos brutos) |
| D3 | OpenSSF Scorecard | CI-4 | baixo | baixo | sessão local | #11 |
| F2 | Dicionário de dados a partir dos esquemas | DX-2 | baixo | médio | sessão local | #10 |
| G4 | Donos por área, triagem, varredura de segredos com os extras | GOV-2, GOV-3, SEC-2 | baixo | baixo | mantenedor | a fase 1 do `GOVERNANCE.md` |

## 3. Os itens

### A1. O saldo do DF conferido no `ci`

- **O quê:** `pipelines/tests/test_df_balance.py` roda as duas contas da auditoria e compara as duas ao centavo, em todos os
  períodos do seletor.
  - A da página: o código de `periods.js` e `serieslayer.js` em Node sobre o pacote montado, como `page-df.cjs` do relatório,
    Apêndice A.
  - A independente: `Decimal` sobre `data/`, como `df_recompute.py`, Apêndice B.
  - O `ci` já tem Node e monta o pacote no passo das páginas.
- **Teste:** 0 diferenças nas figuras do DF (enviado, registrado, excesso, voltou e cada parte, saldo, por pessoa, cada imposto)
  em todos os períodos; a igualdade da União em todos os períodos completos.
- **Controle:** a mesma conta sobre uma cópia dos dados com R$ 1 a mais na Cofins do DF num mês fora da estimativa precisa
  falhar. Uma segunda cópia, com o teto desligado na conta independente, também precisa falhar.
- **Não muda:** nenhuma página, nenhum dado.

### A2. A Rede do dinheiro com o teto do DF

- **O quê:** hoje a prévia recusa desenhar em todos os períodos (DF-1). Há duas saídas, e é o mantenedor quem escolhe
  (**Q-A2**):
  - **(a)** o grafo desenha os impostos do DF com o teto, cada um com o que o DF fica (o mínimo entre o registrado e a parte do
    PIB), e o excesso como uma parte que liga o DF à União: "registrado no DF por sedes e órgãos com sede em Brasília, contado na
    União (estimativa, D146)";
  - **(b)** a prévia sai da produção e fica só no staging, como o D160 diz das prévias e como a spec do Início mais curto (#48)
    prevê.
  - Recomendação: (b) agora, porque não muda método nem texto; (a) quando a prévia for aprovada para a produção.
- **Teste:** `ledger-graph-periods-check.cjs` passa em todos os períodos, e roda no `ci` (B2).
- **Controle:** os dois controles que já existem (R$ 1 na Cofins de SC, um ponto sem ligação) continuam falhando. Um terceiro
  desfaz o teto no grafo, e a conferência `taxes` precisa falhar no DF.

### A3. Um só valor federal no painel do DF

- **O quê:** a coluna "PAGOU" do DF soma os impostos sem o teto (R$ 5.521 por pessoa por mês em 2026), enquanto "Com a União"
  mostra o valor com o teto (R$ 2.609). O texto é do mantenedor (**Q-A3**). Proposta:
  - os cartões federais do DF mostram o que fica no DF depois do teto, imposto por imposto;
  - uma linha logo abaixo: "Mais R$ X bi registrados no DF por sedes e órgãos com sede em Brasília foram contados na União
    (estimativa: em cada imposto, o DF conta no máximo a sua parte no PIB do Brasil, IBGE 2023)".
- O dado: `federalAt` devolve também `byTaxCapped`; `byTax` fica como está para a frase da contribuição dos servidores, que fala
  do que a Receita registra.
- **Teste:** nos períodos completos, a soma dos cartões federais do DF é igual ao "Foi para a União" do mesmo painel, ao
  centavo; nos outros 26 estados, nada muda (os dois campos iguais).
- **Controle:** trocar `byTaxCapped` por `byTax` no DF precisa fazer o teste falhar. O texto visível dos outros 26 estados fica
  igual ao de antes (`visible-text-probe --compare`).

### A4. As diferenças sem explicação, registradas e travadas

- **O quê:** um arquivo `data/series/known-gaps.json` com cada diferença da seção 1.4 do relatório e do DF-4, com o valor, o
  mês e a origem (o total de 2026 em R$ milhões, a soma dos estados, a estimativa). Nenhuma explicação que o dado não sustenta;
  o campo diz "diferença sem explicação" quando é o caso.
- **Teste:** a conferência mensal do relatório (os 27 estados contra a soma do arquivo, e essa soma mais o "sem estado" contra o
  total nacional) falha com qualquer diferença que não esteja na lista, e com qualquer item da lista que já não aconteça. Assim
  a lista só encolhe.
- **Controle:** R$ 1 plantado num estado num mês precisa fazer o teste falhar.
- **Pergunta ao mantenedor (Q-A4):** trocar os totais de 2026 em milhões pelos do arquivo mensal da Receita assim que ele trouxer
  2026 ao centavo.

### D1. `pages.yml` com as ações por commit e as permissões só no deploy

- **O quê:**
  - as quatro ações do `pages.yml` fixadas por commit, com a versão em comentário, como `ci.yml`;
  - `pages: write` e `id-token: write` movidos para o job `deploy`;
  - feito depois do #52, que reescreve o passo de montagem.
- **Teste:** `pipelines/tests/test_workflows.py`, em que todo `uses:` dos workflows (e do `deploy/staging/deploy.yml`) é um
  commit de 40 caracteres e nenhum workflow dá escrita fora do job que precisa dela.
- **Controle:** uma cópia de um workflow com `@v4` e outra com `pages: write` no topo precisam falhar.

### B1. O saldo dos 27 estados e o bloco da União conferidos no `ci`

- **O quê:** o teste do A1 estendido aos 27 estados e ao bloco da União (cada parte do bloco), e a conferência mensal contra o
  total nacional.
- **Teste:** 0 diferenças ao centavo em todos os estados e períodos; o bloco da União igual ao total oficial menos os estados.
- **Controle:** R$ 1 plantado num estado qualquer precisa ser pego no estado e na conferência mensal.

### B2. As conferências da Rede e as sondas no `ci`

- **O quê:** um job `probes` no `ci`.
  - Primeiro, `ledger-graph-periods-check.cjs`, que roda em Node sem navegador.
  - Depois, `site-check.cjs` e `visible-text-probe.cjs --audit` com o Chromium do Playwright. As bibliotecas de CDN ficam num
    espelho local fixado por versão, como `CDN_MIRROR`.
- **Teste:** as saídas de hoje, que passam, com o `--control` de cada uma no mesmo job.
- **Controle:** o job inteiro falha se qualquer `--control` passar.

### C1. As fontes do lado "Voltou" no painel de cada estado

- **O quê:**
  - `build_two_step_series.py` passa a escrever `sources` no arquivo da série, a partir das fontes de `data/ug/`: URL, mês e
    data de leitura.
  - O painel de cada estado lista, junto das fontes que já tem, as do BEPS do INSS, do MDS (Bolsa Família e BPC), do Portal
    (despesas por execução), do Tesouro (FCDF) e, no DF, do IBGE (teto).
  - O texto é do mantenedor (**Q-C1**).
  - Relação: #12.
- **Teste:** cada família de número do painel tem pelo menos uma URL e uma data de leitura no pacote.
- **Controle:** apagar as fontes de uma família na cópia do pacote precisa fazer o teste falhar.

### C2. Data de leitura e URL em todo arquivo de dados

- **O quê:**
  - os 23 arquivos sem data e os 7 sem URL da seção 2.2 do relatório ganham `collected_at` e as URLs que os seus scripts já
    leem;
  - um arquivo curado à mão diz "registro feito à mão" (o campo `provenance` do #45).
  - Relação: #10.
- **Teste:** todo arquivo de `data/` que um construtor de página lê tem data de leitura e pelo menos uma URL, ou a marca de
  registro feito à mão.
- **Controle:** um arquivo plantado sem data precisa ser achado.

### C3. A checagem semanal dos links de fonte

- **O quê:** `.github/workflows/source-links.yml`, semanal e manual.
  - Pede cada URL distinta das três páginas, com `HEAD` e, se preciso, `GET` com agente de navegador.
  - Respeita um intervalo por host e publica a lista dos que não respondem como resumo do job.
  - Não falha o `ci` dos pull requests, porque um site do governo fora do ar não é erro do pull request.
  - Relação: #10, #12.
- **Teste:** o script de checagem tem teste de unidade com um servidor local.
- **Controle:** uma URL plantada que dá 404 precisa aparecer na lista.

### B3. Os 3 Poderes: Legislativo e Executivo nas regras do D154

- **O quê:**
  - as médias e somas do Legislativo e do Executivo passam a `Decimal` com meio para cima, como as do Judiciário;
  - antes, uma tabela mostra ao mantenedor cada centavo que muda na tela (**Q-B3**).
- **Teste:** os testes de `test_judiciary_view.py` estendidos à Câmara, ao Senado e ao Executivo (somas que fecham à mão,
  médias, rótulos de meses).
- **Controle:** um valor plantado numa ficha precisa fazer a soma falhar.

### B4. Como o dinheiro anda: as divisões conferidas

- **O quê:** um teste sobre `dinheiro-r1-data.js`:
  - cada imposto reparte 100%;
  - as partes de cada linha da União e o gasto dos 27 estados fecham com o total, dentro do arredondamento declarado (R$ 0,1 bi
    por parte);
  - cada fonte tem URL.
- **Controle:** uma parte plantada com 1 ponto percentual a mais precisa falhar.

### C4. Como o dinheiro anda: o RTN e o SICONFI com link e data

- **O quê:** as duas fontes que o arquivo já traz ganham link na página e data de leitura no arquivo, com o texto aprovado.
- **Teste:** cada fonte do arquivo aparece como link na página montada.
- **Controle:** uma fonte plantada sem link precisa ser achada.

### D2. Atualização de dependências

- **O quê:** `.github/dependabot.yml` para as ações do GitHub, o `uv.lock` (pip) e o `site/package-lock.json` (npm), semanal,
  agrupado por ecossistema, com os pull requests no `staging`.
- **Teste:** o arquivo valida contra o esquema publicado do Dependabot, lido no teste.
- **Controle:** um ecossistema plantado com nome errado precisa falhar.
- Não verificável antes do merge: se o GitHub abre os pull requests. O corpo do pull request diz isso.

### F1. Um comando para preparar e conferir

- **O quê:**
  - `docs/superpowers/tools/check-all.py` roda, na ordem e com o tempo de cada um, o que o `ci` roda: os testes, os construtores,
    `git diff --exit-code` nas páginas e o `build-site.py` dos dois perfis do #52.
  - O README passa a ter um bloco só, com as versões de Python e Node e as variáveis das sondas (`PW_CORE`, `CHROME_HEADLESS`,
    `CDN_MIRROR`).
- **Teste:** o comando sai com 0 num clone limpo no `ci`.
- **Controle:** uma página versionada alterada de propósito faz o comando sair com 1.

### G1 a G4, C5, D3 e F2

- **G1 (sessão local):** publicar D155 a D162 no registro público com `publish-decisions.py`.
  - Teste: um teste do `ci` acha no registro todo `D` citado em `docs/superpowers/specs/`, `data/` e no código.
  - Controle: um `D999` plantado numa spec.
- **G2 (mantenedor):** `required_approving_review_count` 1 e revisão do dono de código nas regras da `main` e do `staging`,
  quando entrar a segunda pessoa com acesso de escrita (fase 1 do `GOVERNANCE.md`).
- **G3:** a cada promoção do staging, uma versão com notas geradas da lista de pull requests que ela leva, e um `CHANGELOG.md`.
  - Desde D166 a produção recebe uma tarefa por vez: como fica a versão é a pergunta 46 da prévia de 2026-10-25 (Q100).
  - Teste: a nota cita todo pull request da promoção.
  - Controle: um pull request de fora plantado na lista.
- **G4 (mantenedor):** `CODEOWNERS` por área; uma etiqueta de entrada `needs-triage` e um parágrafo de triagem em
  `GOVERNANCE.md`; os padrões genéricos e a checagem de validade da varredura de segredos.
- **C5:** com o manifesto dos brutos do #10, os três construtores leem entradas versionadas com hash, e o `ci` confere os três
  arquivos de página contra os construtores.
  - Controle: um byte plantado num arquivo de página.
- **D3:** o Scorecard do #11.
- **F2:** um dicionário de dados gerado de `schemas/`, com esquemas novos para as séries de `data/series/` (#10).
  - Teste: todo arquivo de `data/series/` valida contra o seu esquema.
  - Controle: um campo plantado fora do esquema.

## 4. Perguntas ao mantenedor

1. **Q-A2:** a Rede do dinheiro sai da produção (recomendado agora) ou passa a desenhar o teto do DF?
2. **Q-A3:** o painel do DF mostra os impostos com o teto e uma linha com o excesso, com o texto da seção A3?
3. **Q-A4:** trocar os totais de 2026 em milhões pelos ao centavo quando a Receita os publicar?
4. **Q-C1:** a lista de fontes do lado "Voltou" no painel, com o texto proposto no pull request.
5. **Q-B3:** o Legislativo e o Executivo passam às regras de arredondamento do D154, com a tabela de cada centavo que muda?
6. **DF-5:** o teto do DF continua com a parte do PIB de 2023 em todos os períodos, ou cada ano usa o seu?

## 5. Fora desta spec

Funcionalidades novas, o site em Astro (fases B1 a B5, #3 a #7), as mudanças de pastas da fase 2 da limpeza, o que esconder da
produção (a spec do Início mais curto, #48) e as configurações do repositório que a spec de staging já prevê.
