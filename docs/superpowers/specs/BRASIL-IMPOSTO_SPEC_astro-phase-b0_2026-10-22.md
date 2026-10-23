# Brasil-Imposto: site em Astro, fase B0 (esqueleto, pipelines, esquemas e CI)

Status: **aprovada (D151, 2026-10-22) com as 7 respostas recomendadas; em execução.** Feitos: #23 (`pipelines/`), #25 (uv),
#26 (nomes em inglês), #32 e #33 (o inventário das chaves), #34 (esquemas e exportação) e #35 (o esqueleto em Astro), com o job
`ci`. Falta: a sonda de paridade das prévias dentro do `ci` e as chaves de `data/` em inglês. Issue: #2.

### Summary (English)

Phase B0 lays the ground for the Astro site without changing anything a visitor sees: the GitHub Pages workflow keeps
publishing today's pages until phase B5. It adds an Astro 7 skeleton in `site/` (strict TypeScript, pinned versions), moves the
Python scripts of `pipelines/` to `pipelines/` with every reference rewritten, adds JSON Schemas in `schemas/` and an export
step that writes the per-entity JSON files the site will read, with English keys and official labels as values, and adds a CI
workflow that blocks a pull request on any red check. Done when: the Astro build is green, the new JSON files pass their
schemas, every pipeline output is equal in value to today's, and today's pages show the same visible text in every probe
combination. Seven questions for the maintainer close the section.

## 1. O que a fase entrega

1. **`site/` com o esqueleto Astro.** Astro 7.4.2 (a versão no npm em 2026-10-22, que pede Node 22.23.4 ou mais novo), saída
   estática, `tsconfig` estendendo o `strictest` do Astro, TypeScript na versão que o `astro check` aceita (conferida na
   documentação do Astro ao montar o esqueleto; o npm já tem a 7.0.2), `package-lock.json` e `.nvmrc` com a versão do Node.
   Uma página só, que lê um JSON de entidade e mostra o nome e um número, para provar a cadeia inteira (dado, esquema, tipo,
   página). **Essa página não vai ao ar:** o Pages continua publicando as prévias de hoje até a fase B5.
2. **`pipelines/`:** os scripts de `pipelines/` passam para `pipelines/` com `git mv`, e toda referência é reescrita no
   mesmo pull request (scripts, `README.md`, `CONTRIBUTING.md`, `.claude/CLAUDE.md`, docs, formulários de issue). Os
   construtores de `docs/superpowers/tools/` **ficam onde estão** até a fase B5, porque o `pages.yml` os chama e saem junto com
   as prévias; assim esta fase não mexe no workflow de publicação.
3. **Python com `uv`:** Python 3.12, `pyproject.toml` e `uv.lock` no lugar de `requirements.txt`, com as mesmas versões fixadas
   de hoje (duckdb 1.5.6, openpyxl 3.1.5, xlrd 2.0.1) mais o validador de esquema.
4. **`schemas/`:** um JSON Schema (draft 2020-12) por tipo de arquivo de entidade (Brasil, estado, município, caso, pessoa),
   cada número com o objeto de fonte (órgão, base, link, data de coleta). Os tipos do TypeScript são gerados desses esquemas,
   nunca escritos à mão, para os dois lados não divergirem.
5. **O passo de exportação** (`pipelines/export/`): lê os dados publicados de hoje em `data/` e grava um JSON por entidade, com
   chaves em inglês e os rótulos oficiais como valores, como a fonte escreve. Cada arquivo é validado contra o seu esquema antes
   de ser gravado; um arquivo que falha não é gravado.
6. **Chaves e nomes em inglês (issue #8):** nos arquivos novos de entidade, tudo em inglês desde o início. Em `data/`, uma primeira
   varredura achou 29 chaves com cara de identificador e com palavras em português (por exemplo `valor_aditado_brl`,
   `df_by_orgao`, `executivo_civil_ativos`), em 20 arquivos, e 4 nomes de pasta ou arquivo (`municipios/`, `ponte/`,
   `inss_emitidos_municipio.py`, `ponte_supervision_cpi.py`). O primeiro passo da fase é o inventário completo, conferido à mão; cada chave muda junto com quem a lê, no mesmo pull request.
   Nomes próprios de fonte (Receita Federal, Salário-educação, Bolsa Família) continuam como a fonte escreve.
7. **CI** (`.github/workflows/ci.yml`, em todo pull request): os testes Python, a validação de esquema de cada JSON novo,
   `astro check`, `tsc --noEmit`, Vitest, o build do Astro e a sonda de paridade das prévias. Permissões só de leitura, ações
   fixadas por SHA, nunca `pull_request_target`. Um check vermelho bloqueia o merge depois que entrar no ruleset da `main`.

## 2. Testes, escritos antes do código

| Teste | O que prova | O controle que tem de falhar |
|---|---|---|
| Paridade de valor dos pipelines | Para cada saída de hoje, o arquivo novo traz os mesmos valores, campo a campo, pelo mapa de chaves antigas para novas | Um centavo a mais num valor de um estado |
| Esquemas | Todo JSON de entidade passa no seu esquema | Um número sem o objeto de fonte; uma chave em português |
| Tipos gerados | `tsc --noEmit` passa com os tipos gerados dos esquemas | Um campo renomeado no esquema e não na página |
| Prévias intactas | `visible-text-probe.cjs --compare`: o texto visível das prévias igual antes e depois da fase, nas 100 combinações (home em 19 períodos, 27 estados em 3 períodos) | Uma palavra trocada num construtor |
| Referências | Nenhum caminho antigo (`pipelines/`) sobra em código ou documento; maiúsculas e minúsculas exatas | Um caminho antigo plantado num documento |
| Build | `astro build` gera a página de prova, que lê um JSON de entidade | Um JSON de entidade apagado |

## 3. Pronto quando

- O build do Astro está verde no CI, e o CI falha em cada controle da tabela acima.
- Os JSON de entidade passam no esquema.
- Cada saída dos pipelines é igual em valor à de hoje.
- As três páginas publicadas mostram o mesmo texto visível que antes da fase, e `site-check.cjs` passa em 1440 e 420 px.
- O `pages.yml` não mudou, e o site no ar continua o mesmo.

## 4. Fora desta fase

Qualquer página portada para o Astro (fases B1 a B4), o three.js, o mapa SVG, a prévia social, a publicação do Astro no Pages
(B5), mudança de método ou de número, e a saída das prévias do repositório.

## 5. Riscos

- **Renomear chaves quebra uma prévia sem aviso:** a sonda de paridade das prévias roda em todo pull request desta fase.
- **Muitos rótulos oficiais são chaves de dicionário hoje** (cerca de 130 mil na amostra, como os nomes de órgão do SIAFI ou as
  linhas do RREO). Nos arquivos novos eles viram valores; nos arquivos de `data/` a forma só muda quando o pipeline daquele
  arquivo for tocado, para esta fase não virar uma reescrita dos dados.
- **Ritmo de versões do Astro:** versões fixadas; atualização só de propósito, num pull request próprio.

## 6. Perguntas para o mantenedor

**Respondidas em 2026-10-22 (D151): o mantenedor aceitou a recomendação das sete.** A fase B0 está aprovada.

1. **Versão do Node.** Recomendo a 24 (LTS), que cumpre o mínimo do Astro 7.4.2 (22.23.4) e fica em suporte por mais tempo.
2. **Gerenciador de pacotes.** Recomendo o npm, que já vem com o Node: uma ferramenta a menos para quem contribui.
3. **Onde ficam os JSON de entidade.** Recomendo gerá-los no build, a partir de `data/`, sem versionar: o repositório não cresce
   com uma segunda cópia dos dados, e o dado de origem continua sendo um só.
4. **Construtores das prévias.** Recomendo que fiquem em `docs/superpowers/tools/` até a fase B5, para esta fase não tocar no
   `pages.yml`.
5. **Dependências novas, todas gratuitas e de código aberto:** `jsonschema` (Python), `json-schema-to-typescript`, `vitest`,
   `@astrojs/check`, `playwright`. Recomendo aceitar as cinco.
6. **O check do CI no ruleset da `main`.** Mudar o ruleset é configuração do repositório: recomendo que o mantenedor acrescente o
   check `ci` como obrigatório depois do primeiro verde, ou autorize o agente a fazer isso.
7. **Rótulos oficiais como chave em `data/`.** Recomendo mudar a forma só nos arquivos novos de entidade nesta fase, e nos de
   `data/` quando o pipeline de cada um for tocado (pergunta da seção 5).
