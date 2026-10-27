# Inventário das APIs abertas do governo: primeira passada (2026-10-27)

Primeira passada da tarefa #158 (D182): cada API foi aberta e lida na sua própria especificação ou numa chamada real, sem pesquisa na web (D178). Serve a quem chega ao projeto e à decisão sobre a mudança para a API (D171) e sobre o middleware.

**O que esta passada entrega:** quais APIs existem, onde ficam suas especificações, o que cada uma cobre, se pede chave e quais grupos de dados oferece. **O que ela ainda não entrega:** a ligação de cada base do site à sua API, a frequência de atualização de cada fonte, os limites de pedidos e as fontes estaduais e municipais (seção 4).

## 1. Resumo

| API | Esfera | Chave | Especificação lida | Tamanho |
|---|---|---|---|---|
| Portal da Transparência | União (com dados por município) | Sim, grátis, por e-mail | Sim, OpenAPI 3 | 109 caminhos |
| SICONFI (Tesouro) | Estados e municípios | Não pediu nas chamadas feitas | Sim, OpenAPI 3 | 12 caminhos |
| Tesouro Transparente | União, repasses a estados e municípios | Não verificado | Só o catálogo | 91 conjuntos, 9 são APIs |
| Câmara dos Deputados | Legislativo federal | Não pediu na chamada feita | Sim, OpenAPI | 78 caminhos |
| Senado Federal | Legislativo federal | Não verificado | Sim, OpenAPI | 157 caminhos |
| PNCP (compras) | Compras públicas | Não verificado | Sim, OpenAPI | 12 caminhos |
| Compras.gov.br | Compras federais | Não verificado | Sim, OpenAPI | 77 caminhos |
| IBGE SIDRA | Indicadores | Não pediu na chamada feita | Só uma chamada real | n/a |
| Banco Central SGS | Séries econômicas | Não pediu na chamada feita | Só uma chamada real | n/a |
| Ipeadata | Séries econômicas | Não pediu na chamada feita | Só uma chamada real | n/a |
| TSE | Eleições | n/a (catálogo de arquivos) | Só o catálogo | 190 conjuntos |
| INSS | Previdência | n/a (catálogo de arquivos) | Só o catálogo | 35 conjuntos |

## 2. Uma por uma

### 2.1 Portal da Transparência do Governo Federal (CGU)

- **Onde:** `https://api.portaldatransparencia.gov.br/api-de-dados/...`; especificação em `https://api.portaldatransparencia.gov.br/v3/api-docs`.
- **Acesso:** cabeçalho `chave-api-dados`; a especificação manda pedir a chave grátis por e-mail em `portaldatransparencia.gov.br/api-de-dados/cadastrar-email`. Contato na especificação: `listaapitransparencia@cgu.gov.br`. Licença citada: Decreto nº 8.777/2016.
- **Grupos de dados (109 caminhos):**
  - Servidores: lista, por órgão, funções e cargos, remuneração mês a mês (D176).
  - Despesas: documentos, por órgão, por funcional programática, itens de empenho, favorecidos, plano orçamentário, tipo de transferência.
  - Contratos, convênios, licitações, emendas, viagens, cartões, notas fiscais, imóveis, renúncias fiscais.
  - Benefícios sociais **por município**: Bolsa Família e Novo Bolsa Família, Auxílio Brasil, Auxílio Emergencial, BPC, PETI, Safra, Seguro Defeso.
  - Sanções e integridade: CEIS, CNEP, CEPIM, CEAF, acordos de leniência.
- **Limites de pedidos:** não estão na especificação. Não confirmado.

### 2.2 SICONFI (Tesouro Nacional): estados e municípios

- **Onde:** `https://apidatalake.tesouro.gov.br/ords/siconfi/tt/...`; especificação em `.../ords/siconfi/open-api-catalog/tt/`. Atenção: o campo `servers` da especificação aponta para um host interno do Tesouro; usar o endereço público acima.
- **Caminhos:** `entes` (a lista de estados e municípios), `rreo`, `rgf`, `dca`, `extrato_entregas`, `extrato_relatorios`, `anexos-relatorios`, `msc_orcamentaria`, `msc_patrimonial`, `msc_controle`, `tce_orcamentaria`.
- **Parâmetros comuns:** `id_ente` (código IBGE do ente), `an_exercicio`, `nr_periodo`, `no_anexo`, `co_esfera`.
- **Verificado:** uma chamada a `rreo` para `id_ente=42` respondeu 200 com JSON.
- **Cobertura:** é a fonte nacional das contas de **estados e municípios** (relatório resumido da execução orçamentária, relatório de gestão fiscal, declaração de contas anuais, matriz de saldos contábeis).

### 2.3 Tesouro Transparente (catálogo CKAN)

- **Onde:** `https://www.tesourotransparente.gov.br/ckan/api/3/action/package_list`: 91 conjuntos.
- **Nove são APIs:** `api-dca-entes`, `api-de-transferencias-constitucionais`, `api-extrato-entes`, `api-msc-controle-entes`, `api-msc-orcamentaria-entes`, `api-msc-patrimonial-entes`, `api-rgf-entes`, `api-rreo-entes`, `api-tabela-entes`.
- **Transferências constitucionais:** a descrição do conjunto diz que dá os repasses constitucionais da União a estados e municípios, por ente. O recurso de API aponta para uma página do Tesouro (`sisweb.tesouro.gov.br`) que **não li**; conferir antes de contar com ela.

### 2.4 Câmara dos Deputados

- **Onde:** `https://dadosabertos.camara.leg.br/api/v2/...`; especificação em `https://dadosabertos.camara.leg.br/api/v2/api-docs` (78 caminhos).
- **Grupos:** deputados (11), proposições (7), votações (4), eventos (6), órgãos (5), partidos (4), legislaturas (4), frentes (3), blocos (3), grupos (4), referências (27).
- **Verificado:** `GET /api/v2/deputados?itens=1` respondeu com JSON, sem chave.

### 2.5 Senado Federal

- **Onde:** `https://legis.senado.leg.br/dadosabertos/...`; especificação em `https://legis.senado.leg.br/dadosabertos/v3/api-docs` (157 caminhos).
- **Grupos maiores:** senador (por código: 14 caminhos, mais a lista), plenário (resultado, lista, agenda, encontro, votação), comissão, matéria, composição, votação de comissão, processo, taquigrafia.
- **Chave e limites:** não verifiquei.

### 2.6 PNCP e Compras.gov.br (compras públicas)

- **PNCP:** `https://pncp.gov.br/api/consulta/v3/api-docs` (12 caminhos): atas, contratações (publicação, atualização, proposta), contratos, plano de contratações anual (`pca`), instrumentos de cobrança. A especificação não diz quais esferas cobre; conferir se os municípios estão dentro antes de contar com ele.
- **Compras.gov.br:** `https://dadosabertos.compras.gov.br/v3/api-docs` (77 caminhos): módulos de UASG, órgão, serviço, material, contratos. Federal.

### 2.7 Indicadores econômicos

- **IBGE SIDRA:** `https://apisidra.ibge.gov.br/values/t/<tabela>/...`; uma chamada à tabela 1737 respondeu 200 com JSON.
- **Banco Central, SGS:** `https://api.bcb.gov.br/dados/serie/bcdata.sgs.<série>/dados?formato=json`; a série 433 respondeu `{"data":"01/09/2026","valor":"0.82"}`.
- **Ipeadata:** `http://www.ipeadata.gov.br/api/odata4/Metadados` respondeu 200 (OData).

### 2.8 TSE e INSS (CKAN)

- **TSE:** `https://dadosabertos.tse.jus.br/api/3/action/package_list`: 190 conjuntos (por exemplo `candidatos-<ano>` desde 1933). É um catálogo de arquivos para baixar, não uma API de consulta.
- **INSS:** `https://dadosabertos.inss.gov.br/api/3/action/package_list`: 35 conjuntos (benefícios concedidos, emitidos, indeferidos, entre outros), também arquivos.

## 3. Não consegui confirmar nesta passada

| O que | Por quê |
|---|---|
| IBGE Localidades e Agregados (`servicodados.ibge.gov.br`) | Três tentativas deram tempo esgotado desta conexão (o SIDRA do mesmo instituto respondeu); repetir de uma conexão no Brasil ou pelo Chrome do mantenedor |
| Transferegov (`api.transferegov.gestao.gov.br`) | Respondeu 403 daqui |
| Catálogo `dados.gov.br` | Respondeu 401: pede um token de acesso |
| TCU | O endereço que tentei deu 404; não procurei outro |
| Banco Central Olinda | A raiz deu 404; o SGS acima funciona |
| Limites de pedidos de cada API | Não estão nas especificações; ler a página de cada órgão |
| Frequência de atualização de cada fonte | Fica nos metadados de cada conjunto; não lida |
| Chave do Senado, de PNCP e de Compras.gov.br | Não li o esquema de segurança |

## 4. O que falta para fechar a tarefa #158

1. Ligar cada base do site à sua API (as chaves de fonte de `data/`), com o que a API entrega a mais e a menos do que o site usa hoje.
2. A frequência de atualização e os limites de cada uma, lidos nas páginas oficiais.
3. As fontes **estaduais e municipais**: não há uma API nacional única; os estados têm portais e tribunais de contas próprios (não inventariados). O SICONFI, o PNCP e os benefícios do Portal por município são o que cobre todos os municípios hoje.
4. As lacunas da seção 3, de uma conexão no Brasil.

Restrição que já vale: um arquivo de dados acima de 50 MB falha o teste do #124, então a coleta por município precisa dividir os arquivos.
