# Brasil-Imposto: qual stack para a v1

Pesquisa de 2026-10-01. Decisão que serve: qual stack usar para implementar a v1 (autor: *"encontre a melhor stack possível
para este projeto - não tenho certeza de qual pode ser a melhor stack para implementarmos tudo isso"*).

Status: concluída em 2026-10-02 (seções 1, 6 e 7 escritas por um segundo agente, depois que o primeiro travou).

## 0. Ponto de partida (lido no projeto em 2026-10-01)

- Prévias: HTML estático e JavaScript puro, cerca de 6.600 linhas somando páginas, módulos e ferramentas de build. O motor 3D
  (`assets/hero3d.js`, 389 linhas) usa three.js com `Line2` e `CSS2DRenderer`; o mapa do estado (`statemap.js`, 206 linhas) é
  script clássico porque `file://` não aceita import de módulo local.
- Dados no navegador: um único `assets/bi-data.js` de 41,8 MB. Medido nesta pesquisa: 38,3 MB são as séries mensais, das quais
  22,4 MB são os orçamentos das 295 prefeituras de SC e 13,3 MB os orçamentos dos 27 estados; 1,76 MB é a lista de políticos;
  0,7 MB são bandeiras embutidas.
- Pipeline: 84 scripts Python (cerca de 10 mil linhas), só biblioteca padrão mais `openpyxl`, sem chave de API. A pasta `data/`
  tem 190 MB, dos quais cerca de 110 MB são cache de downloads brutos (`pipelines/series/cache`, `data/ug/cache`,
  `data/df/cache`) e 35 MB as séries geradas.
- Requisitos da v1 (grill GD1 a GD25 e o pedido): hospedagem grátis, repositório público, AGPL-3.0, celular primeiro com link de
  WhatsApp, URL própria com Open Graph por estado, município, obra e político, mapa 3D com drill-down, período mês, ano e 4 anos
  sobre séries de 2019 a 2026, 295 municípios na v1 e 5.570 depois, cerca de 594 parlamentares com busca, cerca de 24 casos,
  emendas, shows, Lei Rouanet, atualização mensal automatizada e reproduzível.

## 5. Hospedagem grátis (limites conferidos na documentação oficial em 2026-10-01)

### O que cada uma permite

| Limite | GitHub Pages | Cloudflare Pages (plano Free) | Cloudflare Workers com Static Assets (Free) | Netlify (Free) | Vercel (Hobby) |
|---|---|---|---|---|---|
| Banda | **100 GB por mês, limite "soft"**; acima disso o GitHub pode parar de servir ou mandar e-mail pedindo CDN [1] | **Ilimitada** para arquivos estáticos ("requests to static assets are free and unlimited") [3] | Ilimitada para arquivos estáticos [5] | 300 créditos por mês com limite rígido; banda custa 20 créditos por GB e requisições 2 créditos por 10 mil [8], então no máximo cerca de 15 GB por mês | 100 GB de "Fast Data Transfer" [9] |
| Tamanho do site | 1 GB publicado [1] | Sem limite de total citado; limite por número de arquivos | Sem limite de total citado | Não conferido | Não conferido |
| Número de arquivos | Sem limite citado | **20.000 arquivos** (100.000 nos planos pagos) [2] | 20.000 por versão (100.000 no pago) [4] | Não conferido | Não conferido |
| Tamanho de um arquivo | 100 MiB (limite do Git) [6] | 25 MiB [2] | 25 MiB [4] | Não conferido | Não conferido |
| Builds | 10 por hora, mas o limite não vale com build próprio no GitHub Actions; publicação expira em 10 min [1] | 500 por mês, 1 por vez, 20 min cada [2] | Build fica com quem publica (Actions) | Consome créditos | Não conferido |
| Prévia por Pull Request | Não tem (só com ferramenta extra) | Sim, mas **não para Pull Request vindo de fork** [10] | Não conferido | Não conferido | Não conferido |
| Uso permitido | Proibido para comércio ou SaaS; site cívico é permitido [1] | Sem restrição citada | Sem restrição citada | Sem restrição citada | **Só uso pessoal e não comercial** [9] |
| Custo | Grátis em repositório público | Grátis | Grátis (o Worker em si: 100 mil requisições por dia, só se houver código rodando) [4] | Grátis com teto rígido | Grátis com restrição de uso |

Fontes, abertas em 2026-10-01:
[1] https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
[2] https://developers.cloudflare.com/pages/platform/limits/ (atualizada em 5 set. 2026)
[3] https://developers.cloudflare.com/pages/functions/pricing/
[4] https://developers.cloudflare.com/workers/platform/limits/ (atualizada em 5 set. 2026)
[5] https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/ (atualizada em 23 abr. 2026)
[6] https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
[7] https://github.com/actions/upload-pages-artifact (README: artefato até 10 GB, recomendado abaixo de 1 GB, sem links simbólicos)
[8] https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/ e https://www.netlify.com/pricing/
[9] https://vercel.com/docs/plans/hobby e https://vercel.com/docs/limits/fair-use-guidelines (atualizada em 14 set. 2026)
[10] https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/

### Quantos arquivos o site vai ter (estimativa minha, para testar contra os limites)

| Item | v1 (SC) | Brasil inteiro |
|---|---|---|
| Páginas HTML (home, 27 estados, municípios, cerca de 594 parlamentares, cerca de 24 casos, seção federal) | cerca de 950 | cerca de 6.230 |
| Imagem de prévia (Open Graph) por página | cerca de 950 | cerca de 6.230 |
| Dados por entidade (um JSON por estado, município, político e caso) | cerca de 940 | cerca de 6.220 |
| Busca, fotos, bandeiras, ícones, JS e CSS | algumas centenas (mais 1 por página indexada se usar Pagefind) | idem |
| **Total** | **cerca de 3.000 a 4.000** | **cerca de 19.000 a 25.000** |

Leitura: a v1 cabe com folga em todos. Com os 5.570 municípios, o limite de 20.000 arquivos do Cloudflare passa a apertar. Há saída
sem pagar: uma imagem de prévia por estado para os municípios (ou gerada sob demanda), os dados dos municípios agrupados por
estado e por tema em vez de um arquivo por município, e a busca num índice único em vez de um fragmento por página. No GitHub
Pages o limite que aperta é outro, o de 1 GB e o de 100 GB de banda por mês.

### Banda num pico de WhatsApp

A conta que decide: se a primeira visita ao celular pesar cerca de 1 MB (meta da seção 1), 100 GB de banda dão cerca de 100 mil
visitas por mês. Um link cívico compartilhado em grupos de WhatsApp na semana de uma eleição pode passar disso em um ou dois dias.
No GitHub Pages o limite é "soft" (o próprio GitHub sugere pôr uma CDN na frente); no Cloudflare a banda de arquivos estáticos é
ilimitada no plano grátis. Netlify (cerca de 15 GB) e Vercel (uso não comercial, 100 GB) ficam atrás.

### Cloudflare Pages ou Workers com Static Assets

Os dois servem arquivos estáticos de graça e sem limite de banda, com o mesmo teto de 20.000 arquivos. A Cloudflare publica um
guia de migração de Pages para Workers (https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/,
atualizado em 22 set. 2026) e é para Workers que vão os recursos novos; Pages continua documentado e com limites atualizados em
set. 2026. Para um site só estático, publicado a partir do GitHub Actions, a diferença prática é pequena. Recomendo publicar com
`wrangler` a partir do Actions (o build fica no GitHub, igual para todos os forks) e escolher Workers Static Assets se o projeto
começar agora, porque é o caminho para onde a Cloudflare está levando a plataforma. Não consegui confirmar numa página oficial a
frase "recomendamos Workers para projetos novos"; é uma leitura minha do guia de migração.

Detalhes que contam para um projeto aberto:
- A prévia automática por Pull Request do Cloudflare Pages **não funciona para Pull Requests de forks** [10], que é como quase todo
  contribuidor chega. Prévia de fork exige outro mecanismo (por exemplo, o contribuidor roda `npm run build` e abre a pasta).
- Um projeto Pages criado por "Direct Upload" nunca pode ser trocado para a integração com Git depois
  (https://developers.cloudflare.com/pages/get-started/direct-upload/).
- O build precisa de uma chave de API da Cloudflare guardada como segredo do repositório (GitHub Actions secrets). Forks não
  recebem esse segredo, o que é o comportamento certo.
- Domínio próprio: grátis só os subdomínios `*.pages.dev`, `*.workers.dev` ou `*.github.io`. Um domínio `.com.br` é pago
  (registro.br); **custo a sinalizar** se o autor quiser domínio próprio (preço não conferido nesta pesquisa).

## 2. Mapa 3D

### Fatos medidos e conferidos (2026-10-01)

- As prévias projetam as malhas do IBGE e do Natural Earth **no build**, com `d3.geoEqualEarth()` (`docs/superpowers/tools/build-geo.cjs`,
  linha 48). O motor 3D recebe coordenadas planas já projetadas. Isso decide a comparação: qualquer motor que aceite coordenadas
  cartesianas mantém a projeção Equal Earth (D11); um motor que exige longitude e latitude não.
- MapLibre GL JS só implementa duas projeções, `mercator` e `vertical-perspective` (globo)
  (https://maplibre.org/maplibre-style-spec/types/, seção ProjectionDefinition). Tem a camada `fill-extrusion` (polígono 3D)
  (https://maplibre.org/maplibre-style-spec/layers/) e camadas customizadas que desenham direto no contexto WebGL do mapa
  (https://maplibre.org/maplibre-gl-js/docs/API/interfaces/CustomLayerInterface/).
- deck.gl tem `OrthographicView` "para casos não geoespaciais" e o sistema de coordenadas `cartesian`, padrão nas vistas não
  geoespaciais (https://deck.gl/docs/api-reference/core/orthographic-view, https://deck.gl/docs/developer-guide/coordinate-systems);
  `PolygonLayer` extruda polígonos (https://deck.gl/docs/api-reference/layers/polygon-layer). Aceita as coordenadas já projetadas.
- Versões e licenças no npm (registry.npmjs.org, 2026-10-01): three 0.186.1 (MIT; as prévias usam r170, de out. 2024),
  maplibre-gl 6.11.2 (BSD-3-Clause), deck.gl 9.4.0 (MIT), d3-geo 3.1.1 (ISC), topojson-client 3.1.0 (ISC). Todas compatíveis com
  AGPL-3.0.

Peso medido nesta pesquisa (arquivos baixados do jsDelivr, comprimidos com `gzip -9`; o servidor real usa gzip ou brotli, que
fica um pouco menor):

| Biblioteca | Sem compressão | gzip | Observação |
|---|---|---|---|
| three r186 (`three.core.min.js` + `three.module.min.js`) | 809 KB | **194 KB** | O pacote inteiro; com o empacotador cortando o que não é usado, fica menor |
| MapLibre 6.11.2 (`maplibre-gl.mjs` + `-shared.mjs` + `-worker.mjs`) | 1.125 KB | **303 KB** | Mais o CSS (83 KB) |
| deck.gl 9.4.0 (`dist.min.js`, tudo junto) | 2.073 KB | **575 KB** | Importando só `@deck.gl/core` e `@deck.gl/layers` fica menor; não medi |
| Código das prévias (10 módulos JS) | cerca de 270 KB | **46 KB** | |
| Malhas: `bi-geo.js` (Brasil e vizinhos) | 676 KB | 203 KB | Em GeoJSON plano; em TopoJSON a fronteira comum entre dois estados é guardada uma vez só, "frequentemente com redução de 80% ou mais" (https://github.com/topojson/topojson, README) |
| Malhas: `bi-geo-sc.js` (municípios de SC) | 373 KB | 135 KB | idem |

### Comparação

| Opção | Prós | Contras | Custo de migrar |
|---|---|---|---|
| **three.js (atual)** | Já pronto: maquete, bandeiras como textura dos vizinhos, siglas em CSS2D, DF com área de captura, mapa do estado com alfinetes. Controle total do visual (D5, D10, D11, D14). Equal Earth de graça, porque a geometria chega projetada. O menor dos três motores. Maior comunidade e documentação de WebGL na web | Tudo é código próprio: escolha (picking), câmera, rótulos, desempenho com muitos polígonos. Celular fraco precisa de cuidado (juntar geometrias, limitar resolução de pixel) | **Zero no motor**. Trabalho de passar o script clássico para módulo ES e trocar o CDN pelo pacote npm |
| MapLibre GL JS | Mapa de verdade: zoom até a rua, tiles, rótulos com colisão, acessibilidade de mapa | **Não faz Equal Earth** (só Mercator e globo), o que quebra D11. Feito para mapa base com tiles, que o projeto não usa. A maquete com bandeira nos vizinhos e o relevo do Brasil precisariam de camada customizada, isto é, de three.js dentro do MapLibre. O mais pesado depois do deck.gl | Reescrever o mapa inteiro e ainda manter three.js para o visual |
| deck.gl | Polígonos extrudados com escolha pronta, bom desempenho com milhares de polígonos (os 5.570 municípios), aceita coordenadas cartesianas | Bandeira como fundo do território e siglas centralizadas viram trabalho extra (texto em `TextLayer`, textura não é o padrão do `PolygonLayer`). O mais pesado. Linguagem própria de camadas para os contribuidores aprenderem | Reescrever o mapa inteiro |
| Outra: SVG 2D com d3-geo | Leve, acessível, fácil de contribuir, mesma projeção Equal Earth. Pode ser gerado no build, já dentro do HTML | Não é o "3D moderno de alta qualidade" de D5 e D10 | Útil como complemento, não como substituto (ver abaixo) |

### Recomendação para o mapa

**Manter three.js**, atualizado de r170 para a versão atual pelo npm, com duas camadas a mais:
1. **Um mapa em SVG gerado no build** (mesma projeção, mesmas cores) dentro do HTML de cada página. Ele aparece na hora, antes do
   JavaScript, funciona sem WebGL e em celular fraco, e serve de base para a imagem de prévia do WhatsApp de cada estado. O 3D
   carrega por cima quando o aparelho aguenta (`prefers-reduced-motion`, falta de WebGL ou bateria fraca ficam no SVG).
2. **Malhas em TopoJSON quantizado e divididas**: o Brasil e os vizinhos na home; os municípios de um estado só quando o estado
   abre. Assim o celular nunca baixa os 5.570 municípios de uma vez.

Não consegui medir o desempenho do three.js num celular real nesta pesquisa; a meta de peso fica na seção 1.

## 3. Dados no navegador e busca

### Quanto pesa cada pedaço, medido nos dados reais de `bi-data.js` (JSON compacto, `gzip -9`)

| Pedaço | Hoje | Se for um arquivo por entidade |
|---|---|---|
| Tudo junto (`bi-data.js`) | 41,8 MB, 8,3 MB com gzip | (não existe mais) |
| Nível da home (saldo, cartões federais, regiões, contas da União, população) | dentro do arquivo único | **32 KB** |
| Série federal mensal das 27 UFs, todos os detalhes | dentro do arquivo único | 583 KB inteira; **22,5 KB por UF** (mediana). Para pintar o mapa basta o saldo de cada UF por mês, uma fração disso |
| Orçamento de um estado (SICONFI, 2019 a 2026) | dentro do arquivo único | **82 KB por estado** (mediana; o maior, 94 KB) |
| Orçamento de uma prefeitura de SC | dentro do arquivo único | **16 KB por município** (mediana; o maior, 24 KB) |
| Políticos de um estado | dentro do arquivo único | **3,4 KB por UF** (mediana; o maior, 8,2 KB) |

Leitura: abrir a home custaria cerca de 32 KB de dados mais o arquivo de cores do mapa; abrir um estado, cerca de 110 KB; abrir um
município, cerca de 16 KB. Cada arquivo já traz todos os meses de 2019 a 2026, então trocar o período (mês, ano, 4 anos) não baixa
nada novo. Dividir também por período só multiplicaria arquivos (e o limite de 20.000 do Cloudflare) sem ganho real.

### Comparação

| Opção | Prós | Contras | Custo |
|---|---|---|---|
| **JSON por entidade, com todos os meses dentro** | O celular baixa só o que abre (números acima). Funciona em qualquer hospedagem estática, com cache do navegador e da CDN. É o formato que o pipeline Python já gera e que as prévias já leem. Fácil de inspecionar e de citar ("baixe o JSON de SC") | Muitos arquivos com os 5.570 municípios (ver seção 5); repetição de nomes de campo (resolve com arrays compactos se precisar) | Grátis |
| Parquet com DuckDB-WASM | SQL no navegador, consulta livre | O motor pesa demais para celular: medido nesta pesquisa, `duckdb-eh.wasm` 1.33.1 tem 35,9 MB, **8,1 MB com gzip**, mais um worker de cerca de 770 KB. Isso é o tamanho do `bi-data.js` inteiro de hoje | Grátis, mas inviável no 4G |
| Parquet com hyparquet | Leitor de Parquet em JavaScript puro, sem dependências, lê só o pedaço necessário por requisições HTTP de intervalo (README em https://github.com/hyparam/hyparquet) | Mais uma peça para os contribuidores, sem ganho real para os volumes acima (um estado inteiro cabe em 110 KB de JSON) | Grátis |
| SQLite no navegador (sql.js e similares) | Uma base só | Mesmo problema de peso do DuckDB; não medi | Grátis |

**Recomendação:** JSON por entidade, gerado no build, com todos os meses dentro. Parquet (ou CSV) fica como **formato de dado
aberto para download**, para pesquisadores e jornalistas, e não para a tela do celular.

### Busca

| Opção | Prós | Contras |
|---|---|---|
| **Índice próprio em um JSON** (nome, cargo, partido na época, UF, URL) carregado quando a pessoa toca na busca | Para nomes de 594 parlamentares, 5.570 municípios e cerca de 24 casos, o índice inteiro tem poucas dezenas de KB comprimido (estimativa; não medi). Um arquivo só, busca sem acento e por prefixo, nada de fragmentos | Não busca dentro do texto das páginas |
| Pagefind 1.5.2 | "Busca totalmente estática, feita para sites grandes, usando o mínimo de banda" e para "dezenas de milhares de páginas" (https://pagefind.app/); suporta português com radicalização (stemming) e interface traduzida, a partir de `<html lang="pt-br">` (https://pagefind.app/docs/multilingual/); funciona com qualquer gerador de site; MIT | Gera um fragmento por página indexada, o que pesa contra o limite de 20.000 arquivos do Cloudflare com os 5.570 municípios |

**Recomendação:** índice próprio de entidades na v1 (é busca de nome, não de texto). Pagefind quando houver texto longo para
buscar (os casos, as fichas com histórico), indexando só essas páginas.

## 4. Pipeline e atualização mensal

### Limites do GitHub Actions num repositório público (conferidos em 2026-10-01)

| Ponto | Regra | Fonte |
|---|---|---|
| Custo | "GitHub Actions usage is free [...] for public repositories that use standard GitHub-hosted runners." Runners maiores são sempre cobrados | https://docs.github.com/en/billing/concepts/product-billing/github-actions |
| Duração de um job | 6 horas por job; 35 dias por execução do workflow | https://docs.github.com/en/actions/reference/limits |
| Jobs ao mesmo tempo | 20 no plano Free (5 de macOS) | idem |
| Agendamento (`schedule`) | Cron POSIX em UTC (aceita fuso horário IANA); intervalo mínimo de 5 minutos; **pode atrasar em horários de pico, sobretudo no início de cada hora, e jobs podem ser descartados** se a carga for alta; só roda no branch padrão | https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows |
| Desligamento automático | **Em repositório público, o agendamento é desligado depois de 60 dias sem atividade no repositório**; em forks, vem desligado | idem e https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows |
| Pull Request aberto pelo próprio workflow | Com o `GITHUB_TOKEN`, eventos não disparam novos workflows, exceto `pull_request` aberto ou atualizado, que cria execuções **à espera de aprovação** de alguém com acesso de escrita | https://docs.github.com/en/actions/concepts/security/github_token |
| Cache | 10 GB por repositório; entradas sem acesso há mais de 7 dias são apagadas | https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching |
| Artefatos | O plano Free lista 500 MB de armazenamento de artefatos; a página diz que essas cotas são de repositório privado e que repositório público usa runner padrão de graça. Não consegui confirmar se o teto de 500 MB vale para artefatos de repositório público | página de cobrança acima |

### Onde guardar os dados

| Opção | Prós | Contras | Custo |
|---|---|---|---|
| **Dados processados (`data/*.json`) no repositório** | Cada atualização mensal vira um diff legível: dá para ver no Pull Request exatamente quais números mudaram e por quê. O site constrói direto do repositório, sem buscar nada fora | O repositório cresce a cada mês; o GitHub recomenda ficar abaixo de 1 GB (ideal) e de 5 GB (fortemente), avisa a partir de 50 MiB por arquivo e bloqueia acima de 100 MiB (https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). Hoje as séries geradas somam 35 MB; o maior arquivo é `sc-municipal-budgets.json` com 20 MB, que precisa ser dividido antes de crescer com os 5.570 municípios | Grátis |
| **Downloads brutos em GitHub Releases** (um release por coleta, com `SHA256SUMS`) | "Cada arquivo de um release precisa ter menos de 2 GiB; não há limite para o tamanho total do release nem para a banda"; até 1.000 arquivos por release (https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases). Guarda a cópia exata que gerou cada número, mesmo se o órgão revisar ou tirar o arquivo do ar | Precisa de um passo no workflow para subir e baixar | Grátis |
| Downloads brutos no repositório | Simples | Os caches de hoje somam cerca de 110 MB e crescem todo mês; incham o histórico para sempre | Grátis, mas contra a recomendação do GitHub |
| Git LFS | Arquivo grande versionado | A banda é cobrada do dono do repositório a cada download, inclusive de quem clona e dos runners; acima da cota grátis vira custo (https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-storage-and-bandwidth-usage). Não consegui confirmar o tamanho atual da cota grátis | **Possível custo** |
| Cloudflare R2 | 10 GB por mês grátis, sem custo de saída (https://developers.cloudflare.com/r2/pricing/, atualizada em 1º out. 2026) | Mais uma conta e um segredo; operações acima da cota são cobradas. Não conferi se ativar o R2 exige cartão | Grátis dentro da cota; **custo acima dela** |

### Fluxo recomendado

1. **`update-data.yml`**, agendado uma vez por mês num minuto quebrado (por exemplo dia 6, 09:17 UTC, longe do início da hora) e
   também com `workflow_dispatch` (rodar à mão):
   - restaura os brutos do último release; baixa só o que é novo, respeitando o ritmo do Portal da Transparência (um arquivo a
     cada 90 s, retomando de onde parou, como `agg_transfers_monthly.py` já faz). Um mês novo é pouca coisa; cabe com folga nas 6 h;
   - roda os scripts Python e as checagens que já existem (`checks.py`, `checks_series.py`: soma ao centavo contra o publicado e o
     controle de erro que tem de falhar);
   - sobe os brutos novos num release `dados-AAAA-MM` com `SHA256SUMS`;
   - abre um Pull Request com os JSON novos e um resumo no corpo (meses novos, números que mudaram, checagens). O autor aprova,
     como já está decidido (D2). Com o `GITHUB_TOKEN`, as checagens do PR ficam à espera de um clique em "Approve workflows to run",
     o que combina com a revisão manual.
2. **`deploy.yml`**, a cada merge no branch padrão: instala, constrói o site e publica na Cloudflare com `wrangler` (segredo
   `CLOUDFLARE_API_TOKEN`).
3. **Reprodutibilidade:** Python com versão fixa e dependências travadas (com `uv`, o `uv.lock` trava as versões e `uv run --locked`
   recusa rodar se o lock estiver desatualizado, https://docs.astral.sh/uv/concepts/projects/sync/), `package-lock.json` no lado do
   site, cada JSON com `collected_at` e link da fonte (como já é hoje), e um comando só (`make data` ou `uv run pipeline`) que refaz
   tudo a partir dos brutos de um release.
4. **Reconstrução completa** (2019 a 2026) não roda no agendamento: parte dos releases de brutos, nunca de downloads novos.

### Riscos do pipeline

- **Portal da Transparência a partir do GitHub.** O WAF já bloqueia rajadas de um IP residencial. Os runners do GitHub saem de
  datacenter; **não consegui confirmar** se o WAF da AWS ou outros portais do governo bloqueiam esses IPs. Teste necessário antes de
  confiar no agendamento; plano B: rodar o mesmo comando na máquina do autor e abrir o PR à mão.
- **Agendamento desligado em silêncio.** Se ninguém fizer merge por 60 dias, o agendamento para. O merge mensal do PR de dados é
  atividade e evita isso; um alerta (issue aberta pelo próprio workflow quando falha) ajuda.
- **Mudança de formato nas fontes.** A Receita já mudou a distribuição por UF em 2025; o workflow deve falhar alto (checagem
  vermelha) em vez de publicar número estranho.

## 1. Framework do site (documentação oficial aberta em 2026-10-02)

### O que o framework tem de resolver

- **Uma página HTML por entidade, gerada no build**, com as tags Open Graph no `<head>`: cerca de 950 páginas na v1 e cerca de
  6.230 com o Brasil inteiro (estimativa da seção 5). O protocolo Open Graph define essas tags como `<meta>` no `<head>` da
  página [F1]. Com o HTML pronto no build, a prévia do link aparece sem depender de o robô do WhatsApp rodar JavaScript (o que
  não consegui confirmar, seção 7).
- **Pouco JavaScript no celular**: só o mapa 3D e as modais, carregados depois do mapa SVG (seção 2), e nenhum runtime de
  framework que a página não use.
- **Receber as prévias quase como estão.** Medido em `docs/superpowers/previews/assets/` em 2026-10-02: cerca de 2.350 linhas de
  lógica em 11 arquivos; 3 já são módulos ES (`hero3d.js`, `modals.js`, `modal-options.js`) e 8 são scripts clássicos que
  conversam por variáveis globais (`window.BI`, `window.BIT`, `window.BIL` e outras). A página da home
  (`BRASIL-IMPOSTO_DESIGN_home-simulacao_2026-09-29.html`) tem mais cerca de 700 linhas de JavaScript dentro do próprio HTML. As
  modais montam HTML com template strings (41 linhas com tag HTML em `proposals.js`, 11 em `politicians.js`) e inserem com
  `innerHTML`.
- **TypeScript estrito** (padrão da casa) e pouca coisa nova para quem chega.

### Comparação

| Critério | JavaScript puro estático (atual) | Astro 7.3.5 | SvelteKit 3.0.0 (`adapter-static`) | Next.js 16.3.8 (export estático) | Vite 8.3.2 com React 19.3 |
|---|---|---|---|---|---|
| Milhares de páginas estáticas com Open Graph | Não há gerador: seria preciso escrever um (rotas, layout comum, `<head>` e imagem de prévia por página). É reinventar um gerador de site estático | Rota dinâmica com `getStaticPaths()`, que no modo estático (o padrão) gera uma página por entrada no build [F2]. Endpoints próprios "são chamados no build para produzir arquivos estáticos", inclusive imagens [F3]: servem para a imagem de prévia e para o JSON de cada entidade. Coleções de conteúdo validam o JSON do pipeline com esquema Zod, leem um JSON com várias entradas (`file()`) e são "adequadas para dezenas de milhares de entradas" [F4] | `adapter-static` pré-renderiza o site inteiro como arquivos estáticos [F5]. Rota com parâmetro só é gerada se o rastreador do build chegar até ela ou se for listada em `entries` [F6] | `generateStaticParams()` obrigatório; `dynamicParams: true`, rewrites, redirects, headers, ISR e a otimização de imagem padrão não funcionam no export [F7]. Imagem de prévia por rota com `opengraph-image` e `ImageResponse`, "gerada no build" por padrão [F8] | Vite puro gera uma página só (SPA). Pré-renderizar exige outra peça: o guia de SSR do Vite é "uma API de baixo nível para autores de bibliotecas e frameworks" [F9]; o caminho pronto é o React Router em modo framework com `prerender` e `ssr: false`, com as rotas dinâmicas listadas no código [F10] |
| Peso no celular (runtime do framework, sem contar three.js) | Zero | **Zero por padrão**: o Astro renderiza os componentes "para HTML e CSS, tirando todo o JavaScript do cliente automaticamente" [F11]; os `<script>` da página são TypeScript, empacotados, e podem importar pacotes npm [F12] | Zero só com `csr = false`, e aí "nenhum JavaScript vai para o cliente" e os `<script>` dos componentes são removidos [F6]. Página com mapa precisa hidratar inteira (runtime do Svelte e do SvelteKit; não medi) | React e React DOM: **cerca de 78 KB com gzip** em toda página (medido: `react` 3,5 KB e `react-dom-client` 75,1 KB, versão 19.3.0, minificados com esbuild, `gzip -9`), mais o runtime do Next (não medi). Cada rota gera também um "payload estático para a navegação" além do HTML [F7] | Os mesmos cerca de 78 KB do React, mais o React Router (não medi) |
| Curva para contribuidores | HTML e JS que qualquer um lê, mas o gerador próprio é código que só este projeto tem | Componente `.astro` é HTML com um bloco de código no topo; a documentação diz "se você sabe HTML, já sabe o bastante para escrever seu primeiro componente Astro" [F13] | Componente Svelte parece HTML, com a sintaxe própria do Svelte 5 e as convenções de arquivo do SvelteKit (`+page`, opções de página) | React com componentes de servidor e de cliente (`'use client'`), mais as restrições do export | React, mais a escolha e a configuração do roteador e da pré-renderização |
| Reaproveitar as prévias | Total, como estão | Alto: os módulos viram `<script>` processados (com `import` de npm, como `three`); as funções que montam HTML em template string, depois de trocar as globais por parâmetros, rodam no build e entram com `set:html`, "parecido com `el.innerHTML`" [F14], e as mesmas funções redesenham no navegador quando o período muda | Médio: three.js no `onMount`; as template strings viram componentes Svelte ou `{@html}` | Baixo: as template strings viram JSX (ou `dangerouslySetInnerHTML`), three.js vai para `useEffect` | Baixo, como no Next |
| Maturidade e documentação | Sem framework: nada a quebrar e nada pronto | MIT. 7,38 milhões de downloads por semana no npm (24 a 30 set. 2026). Versão 7.0.0 em 22 jun. 2026. A empresa foi comprada pela Cloudflare em 16 jan. 2026; o anúncio diz que o Astro "continua código aberto e com licença MIT" e "com vários destinos de publicação, não só a Cloudflare" [F15]. Guias oficiais de publicação no GitHub Pages, com Action própria [F16], e na Cloudflare [F17] | MIT. 3,45 milhões por semana (`@sveltejs/kit`). **A versão 3.0.0 saiu em 1º out. 2026**, um dia antes desta pesquisa: guias, exemplos e integrações ainda vão alcançar | MIT. 73 milhões por semana. Versão 16 desde 22 out. 2025. O mais usado dos frameworks completos; o export estático é um modo secundário, com a lista de restrições acima | Vite: MIT, 221 milhões por semana, versão 8 desde 12 mar. 2026. React Router: MIT, 67,5 milhões por semana, versão 8 desde 17 jun. 2026. Peças maduras, mas o conjunto quem monta é o projeto |

Versões, licenças, datas de lançamento e downloads semanais: registry.npmjs.org e api.npmjs.org, consultados em 2026-10-02.

### Leitura

- **O Astro é o único que junta os três pontos que mais pesam aqui**: página estática com Open Graph em escala (rotas, endpoints e
  coleções feitos para isso), zero JavaScript de framework no celular, e as prévias reaproveitadas quase como estão, porque um
  `<script>` do Astro é o mesmo JavaScript das prévias, agora com `import`, TypeScript e empacotamento. O mapa 3D continua three.js
  (seção 2) e nenhum React ou Svelte é necessário. Se um dia uma parte ficar muito interativa (comparações, filtros), o Astro aceita
  componentes de React, Preact, Svelte, Vue e SolidJS, até misturados na mesma página [F11], sem trocar de framework.
- **O JavaScript puro de hoje** é o mais leve e o mais fácil de ler, mas não tem gerador de páginas. Chegar a milhares de URLs com
  prévia exige escrever rotas, layout, `<head>` e imagem de prévia: um gerador próprio, que cada contribuidor teria de aprender.
- **O SvelteKit** gera o mesmo site estático, com runtime pequeno, mas é tudo ou nada por página: ou a página hidrata inteira ou não
  leva script nenhum, e o mapa está na maioria das páginas. E a versão 3 acabou de sair.
- **Next.js e Vite com React** levam o React para toda página (cerca de 78 KB com gzip antes de qualquer código do projeto) e
  obrigam a reescrever as modais em JSX. Ganham em maturidade e no número de pessoas que conhecem React; o Next traz a imagem de
  prévia pronta (`ImageResponse`).

### Meta de peso no celular (a meta citada nas seções 2 e 5)

Primeira visita vinda de um link no WhatsApp, valores com gzip. É meta, não medição, salvo onde indicado.

| Parte | Meta | De onde vem |
|---|---|---|
| HTML, CSS e mapa SVG (o que aparece antes de qualquer JavaScript) | até 150 KB | O HTML da home de hoje tem 17,9 KB e `proposals.css` 9,1 KB (medido); o mapa SVG ainda não existe |
| Dados da página | 32 KB na home, cerca de 110 KB num estado, 16 KB num município | Seção 3, medido |
| Motor 3D (three.js e código das prévias), só depois do SVG e só se o aparelho aguentar | cerca de 240 KB | Seção 2, medido (194 KB mais 46 KB) |
| Malhas do 3D | até 100 KB | Hoje 203 KB em GeoJSON; em TopoJSON quantizado, não medi |
| Fonte e imagens | o resto, até cerca de 400 KB | A fonte Manrope em 5 pesos não foi medida; a imagem de fundo do modo sem mapa (`hero-backdrop.png`, 432 KB) sai, porque o SVG faz esse papel |
| **Total** | **cerca de 1 MB com o 3D; cerca de 300 KB só com o SVG** | |

Fontes da seção 1, abertas em 2026-10-02 (as páginas do Astro, do SvelteKit, do Vite e do React Router não mostram data de
atualização):
[F1] https://ogp.me/ (seção "Basic Metadata")
[F2] https://docs.astro.build/en/guides/routing/ (seção "Static (SSG) Mode")
[F3] https://docs.astro.build/en/guides/endpoints/
[F4] https://docs.astro.build/en/guides/content-collections/
[F5] https://svelte.dev/docs/kit/adapter-static
[F6] https://svelte.dev/docs/kit/page-options (seções `prerender`, `entries` e `csr`)
[F7] https://nextjs.org/docs/app/guides/static-exports (versão 16.3.8, atualizada em 25 ago. 2026)
[F8] https://nextjs.org/docs/app/api-reference/file-conventions/metadata/opengraph-image (atualizada em 9 jul. 2026)
[F9] https://vite.dev/guide/ssr.html
[F10] https://reactrouter.com/how-to/pre-rendering
[F11] https://docs.astro.build/en/concepts/islands/
[F12] https://docs.astro.build/en/guides/client-side-scripts/
[F13] https://docs.astro.build/en/basics/astro-components/
[F14] https://docs.astro.build/en/reference/directives-reference/
[F15] https://astro.build/blog/joining-cloudflare/ (16 jan. 2026)
[F16] https://docs.astro.build/en/guides/deploy/github/
[F17] https://docs.astro.build/en/guides/deploy/cloudflare/

## 6. Stack recomendada

### As peças

| Peça | Escolha | Por quê | Base |
|---|---|---|---|
| Framework | **Astro 7**, versão fixada no `package-lock.json`, saída estática (o padrão), `tsconfig` estendendo o modelo `strictest` que o próprio Astro traz (a documentação recomenda `strict` ou `strictest` para quem escreve TypeScript, https://docs.astro.build/en/guides/typescript/) | Gera uma página com Open Graph por estado, município, obra e político; zero JavaScript de framework no celular; recebe as prévias quase como estão | Seção 1 |
| Interatividade | **TypeScript puro** nos `<script>` do Astro, sem React nem Svelte. As funções que hoje montam HTML em template string viram módulos tipados usados nos dois lados: no build (`set:html`, a página chega pronta) e no navegador (o seletor de período redesenha sem baixar nada, porque cada JSON traz todos os meses) | É o que as prévias já fazem; nada de runtime a mais | Seções 1 e 3 |
| Mapa | **three.js** do npm, de r170 para a versão atual (0.186.1), com um **mapa SVG gerado no build** (d3-geo, mesma projeção Equal Earth) que aparece antes do JavaScript e fica sozinho em aparelho fraco ou sem WebGL; malhas em **TopoJSON quantizado**, com os municípios de um estado só quando ele abre | Mantém o visual aprovado e a projeção (D11) sem reescrever o motor | Seção 2 |
| Imagem de prévia | Um endpoint estático do Astro por entidade que transforma o SVG do mapa em PNG no build com `@resvg/resvg-js` 2.6.2 ("renderizador de SVG", MPL-2.0). É ferramenta de build e não vai para o site; mesmo se fosse, a MPL 2.0 lista a AGPL 3.0 como "Secondary License" (seção 1.12, https://www.mozilla.org/en-US/MPL/2.0/) e o FAQ da Mozilla aceita combinar os dois numa "Larger Work" (pergunta 14, https://www.mozilla.org/en-US/MPL/2.0/FAQ/) | O mesmo desenho do mapa vira a prévia do WhatsApp, sem serviço externo | Seções 1 e 2 |
| Dados no navegador | **JSON por entidade, com todos os meses de 2019 a 2026 dentro**: cerca de 32 KB na home, 110 KB num estado, 16 KB num município. Parquet ou CSV só como dado aberto para download | O celular baixa só o que abre; trocar o período não baixa nada | Seção 3 |
| Busca | **Índice próprio em um JSON** (nome, cargo, partido na época, UF, URL), gerado por um endpoint do Astro e carregado quando a pessoa toca na busca. Pagefind depois, só para texto longo | Busca de nome, um arquivo só, sem fragmentos que pesem no limite de arquivos | Seção 3 |
| Pipeline | Os scripts Python de hoje, com versão fixa e `uv.lock`; `update-data.yml` mensal que baixa só o novo, roda as checagens e abre um Pull Request para o autor aprovar (D2); downloads brutos guardados em GitHub Releases com `SHA256SUMS`; JSON processados no repositório | Cada mês vira um diff legível; reproduzível a partir dos brutos | Seção 4 |
| Hospedagem | **Cloudflare Workers com Static Assets**, publicado com `wrangler` pelo GitHub Actions (`deploy.yml` a cada merge). O guia do Astro diz que "a Cloudflare recomenda Cloudflare Workers para projetos novos" (https://docs.astro.build/en/guides/deploy/cloudflare/) | Banda ilimitada para arquivo estático no plano grátis, o que importa num pico de WhatsApp | Seção 5 |

**Conflito com uma decisão do grill, para o autor resolver:** GD30 aponta o GitHub Pages ("a ideia deve ser mais ou menos essa"). A
seção 5 mostra por que esta pesquisa prefere a Cloudflare (no Pages, 100 GB de banda por mês com limite "soft" e 1 GB de site). Como
o Astro gera arquivos estáticos e tem Action oficial para o GitHub Pages, a escolha se troca só no passo de publicação: dá para começar
no GitHub Pages, como em GD30, e mudar quando a banda apertar.

### Custo de migrar das prévias

Tamanhos relativos, estimativa minha (não medi horas). O que **não muda**: os 84 scripts Python e as checagens, os dados, o CSS e o
visual aprovado, o motor three.js e as fotos dos casos.

| Passo | O que é | Tamanho |
|---|---|---|
| 1 | Esqueleto Astro com `strictest`, layout comum com `<head>` e tags Open Graph | Pequeno |
| 2 | `build-standalone-data.py` para de juntar tudo em `bi-data.js` (41,8 MB) e grava um JSON por estado, município, político e caso, mais o índice de busca. O corte já foi medido na seção 3 | Médio |
| 3 | Portar a lógica: os 3 módulos ES quase sem mudança; os 8 scripts clássicos trocam `window.BI*` por `import` e ganham tipos (cerca de 1.500 linhas); as cerca de 700 linhas de JavaScript dentro do HTML da home viram módulos. É o maior pedaço. O TypeScript estrito vai apontar `null` e campos faltando que hoje passam calados: é trabalho, e é também uma revisão que o dado precisa | Grande |
| 4 | Páginas com `getStaticPaths()` lendo os JSON: home, estado, município, caso, político, seção federal | Médio |
| 5 | Mapa SVG e imagem de prévia no build (d3-geo já é usado em `docs/superpowers/tools/build-geo.cjs`) | Médio |
| 6 | `update-data.yml` e `deploy.yml` (seção 4) | Pequeno |

As prévias continuam abrindo pelo caminho do arquivo enquanto a migração anda; o site novo passa a ser aberto com `npm run dev` (a
regra de não rodar servidor vale só para esta pesquisa).

### Riscos

1. **Framework e hospedagem na mesma empresa.** A Cloudflare comprou a empresa do Astro em jan. 2026. O anúncio promete MIT e vários
   destinos de publicação, e a saída é HTML e arquivos comuns: o GitHub Pages serve o mesmo build sem mudar uma linha do site.
2. **Ritmo de versões.** Astro 5.0.0 saiu em 3 dez. 2024, 6.0.0 em 10 mar. 2026 e 7.0.0 em 22 jun. 2026 (registry.npmjs.org): duas
   versões maiores em pouco mais de três meses. Versão fixada e atualização feita de propósito, nunca automática.
3. **Tempo de build com milhares de páginas e imagens.** Não medi. Gerar cerca de 950 PNG de prévia a cada merge pode pesar; saída:
   gerar de novo só a imagem cujo dado mudou (cache do Actions) e, com os 5.570 municípios, uma imagem por estado para os municípios
   (seção 5).
4. **Limite de 20.000 arquivos da Cloudflare** com o Brasil inteiro (seção 5). O export do Next gera um payload de navegação por rota além
   do HTML [F7]; no Astro espero uma página por rota mais os arquivos de JS e CSS compartilhados, mas não contei num build real.
5. **Duas linguagens.** Node para o site, Python para os dados. Como o site constrói a partir dos JSON que estão no repositório, quem
   mexe só no site precisa só de Node; quem mexe só nos dados, só de Python.
6. **three.js em celular fraco** não foi medido (seção 2). O mapa SVG cobre quem não aguenta o 3D.
7. **Prévia no WhatsApp** (tamanho e formato de imagem aceitos) não confirmada numa página oficial (seção 7): testar com um link real
   antes de divulgar.

### A alternativa mais forte: SvelteKit estático

Gera o mesmo site estático (`adapter-static` pré-renderiza tudo), o runtime é pequeno e o componente Svelte também parece HTML. Passa
à frente do Astro se o site virar uma aplicação com muito estado na tela em várias páginas (comparações lado a lado, filtros
combinados), porque aí um framework de componentes em toda parte paga o que custa. Hoje perde por dois motivos: é tudo ou nada por
página (a página com mapa hidrata inteira, e com `csr = false` nenhum script sobra), e a versão 3.0.0 saiu um dia antes desta
pesquisa. Next.js fica atrás dela aqui: é o mais maduro e traz imagem de prévia pronta, mas leva cerca de 78 KB de React para toda
página e obriga a reescrever as modais em JSX. O JavaScript puro de hoje, sem framework, obrigaria a escrever um gerador de páginas
próprio.

### Custo pago

**Zero na stack recomendada.** Astro, three.js, d3-geo, topojson-client e resvg-js são de código aberto e grátis; o Actions é grátis em
repositório público com runner padrão; a Cloudflare serve arquivo estático sem custo e sem limite de banda (o limite de 100 mil
requisições por dia vale só para código de Worker, que esta stack não tem). Custos possíveis, todos evitáveis e já sinalizados nas
seções 4 e 5:
- **Domínio `.com.br`** no registro.br, se o autor quiser domínio próprio (preço não conferido).
- **Plano pago da Cloudflare** só se o site passar de 20.000 arquivos; evitável agrupando arquivos (seção 5).
- **Git LFS** e **Cloudflare R2 acima da cota**: fora da stack recomendada (brutos vão para GitHub Releases).
- **Runners maiores do GitHub** são sempre cobrados: usar só o runner padrão.

## 7. Não consegui confirmar

Desta parte da pesquisa (seções 1 e 6):
- **Como o WhatsApp lê a prévia do link**: se o robô roda JavaScript e qual tamanho e formato de imagem aceita. A documentação da
  Meta para quem publica páginas (developers.facebook.com, seção "sharing/webmasters", hoje em "documentation/sharing/webmasters")
  respondeu HTTP 400 ao curl, e a cópia do Wayback veio vazia. A stack não depende de JavaScript para a prévia (as tags vão no HTML
  do build), mas o tamanho da imagem precisa de teste com um link real.
- **Peso do runtime** do Svelte e do SvelteKit, do roteador do Next e do React Router: não medi. O React foi medido minificando os
  arquivos de produção com esbuild; o empacotador de cada framework pode dar um número um pouco diferente.
- **Next.js em export estático**: quantos arquivos extras o payload de navegação gera por rota, e se `opengraph-image` funciona em
  rota dinâmica com `output: 'export'`. Não testei.
- **Astro com milhares de páginas**: tempo de build para cerca de 950 e cerca de 6.230 páginas com uma imagem de prévia cada, e a
  contagem exata de arquivos de um build real. O menu da documentação lista "incremental builds" entre os recursos experimentais;
  não avaliei.
- **`@resvg/resvg-js` no GitHub Actions**: é um módulo nativo (napi-rs); não conferi se há binário pronto para o runner Linux padrão.
- **SvelteKit 3.0.0**: saiu em 1º out. 2026; não li as notas da versão nem sei se as páginas de svelte.dev/docs/kit já descrevem a
  versão 3 (elas não mostram versão nem data).
- **Datas das páginas**: as do Astro, do SvelteKit, do Vite e do React Router não mostram data de atualização; valem pela data em que
  foram abertas (2026-10-02).
- **"A Cloudflare recomenda Workers para projetos novos"** (ponto aberto na seção 5): a frase aparece no guia de publicação do Astro na
  Cloudflare, mas continuo sem achá-la numa página da própria Cloudflare.
- **Meta de peso**: o tamanho do mapa SVG e o da fonte Manrope em 5 pesos não foram medidos; a tabela da seção 1 é meta, não medição.

Herdados das seções 2 a 5 e ainda abertos: desempenho do three.js num celular real; cota grátis atual do Git LFS; se ativar o R2
exige cartão; se o teto de 500 MB de artefatos do Actions vale para repositório público; se o WAF do Portal da Transparência e de
outros portais bloqueia os IPs dos runners do GitHub; preço do domínio `.com.br`; as células "Não conferido" de Netlify e Vercel na
tabela da seção 5.
