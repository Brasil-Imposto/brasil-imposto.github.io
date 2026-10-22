# Criciúma (SC): verificação da afirmação sobre manutenção da frota

**Data da coleta:** 2026-09-29 (todas as consultas abaixo foram feitas nesta data, salvo indicação)
**Afirmação a verificar (recebida de terceiro, sem fonte):** "a Prefeitura de Criciúma (SC) orçou recentemente R$ 500.000,00 para a manutenção dos carros da prefeitura, que são 6 carros".
**Regra:** nenhum número inventado ou estimado. Cada valor tem URL oficial e data da coleta. Contas feitas nesta pesquisa sobre valores oficiais estão marcadas "calc.". Valor estimado e ata de registro de preços são **teto**, não gasto.
**Onde a pesquisa foi feita:** computador nos EUA (IP norte-americano). Ver o diário (seção 4).
**Arquivos gerados:** `private/archive/data/criciuma-fleet.json` (dados) e `pipelines/criciuma/` (scripts de coleta).

---

## 0. Veredito

**Não confirmado como foi dito.** Nenhum registro oficial encontrado liga R$ 500.000,00 a uma frota de 6 carros.

| Parte da afirmação | O que os registros mostram | Situação |
|---|---|---|
| "R$ 500.000,00" | O valor existe, exatamente, como **valor estimado (teto)** de dois registros de preços da Prefeitura, ambos de **2024**: Pregão Eletrônico 193/PMC/2024 (elétrica e ar-condicionado) e 163/PMC/2024 (retífica de motores). | Existe, mas em 2024 |
| "para a manutenção dos carros da prefeitura" | Cada um desses dois pregões cobre **uma só especialidade** (elétrica e ar-condicionado; retífica de motores) da frota inteira: carros leves, caminhões e ônibus. | Parcial |
| "que são 6 carros" | Os itens desses pregões somam **164** e **162** unidades (calc., soma das quantidades por modelo de veículo). Nenhum registro de manutenção encontrado cobre 6 veículos. | Não encontrado |
| "recentemente" | O registro de manutenção de frota mais recente com valor próximo é o Pregão Eletrônico **093/PMC/2026** (agosto e setembro de 2026): teto de **R$ 448.560,00** para 12 meses, para a frota da **Polícia Civil** em Criciúma, declarada no termo de referência como **54 veículos**. Não são carros da Prefeitura, embora a compra seja feita pelo Município, que emite o empenho (termo de referência). | Valor diferente, frota diferente |
| Gasto efetivo | Nenhum desses valores é gasto. Os valores pagos estão no portal de transparência da Prefeitura (Betha), que não pôde ser consultado por script (seção 4). | Não verificado |

**Leitura neutra:** um cidadão que vê "R$ 500 mil para manutenção de veículos" em um edital de Criciúma provavelmente está vendo um teto de registro de preços que cobre mais de 160 veículos e uma única especialidade, ou o teto de R$ 448,6 mil para 54 viaturas da Polícia Civil. O site não deve exibir a frase "R$ 500 mil para 6 carros": ela não tem base em registro oficial encontrado.

---

## 1. Os registros oficiais de Criciúma

### 1.1 Órgãos consultados

Fonte: busca pública do PNCP (a mesma que alimenta o site pncp.gov.br), filtrada pelo município de Criciúma (identificador interno do PNCP `municipios=4386`), mais a API de consulta do PNCP. Os CNPJs abaixo são os que aparecem nos próprios registros.

| Órgão | CNPJ | Registros de manutenção de veículos no PNCP |
|---|---|---|
| Município de Criciúma (Prefeitura) | 82.916.818/0001-13 | Sim: 31 editais desde 2022 (lista em `private/archive/data/criciuma-fleet.json`, que traz também os 2 do CriciúmaPrev) e o contrato 130/PMC/2025 |
| Fundo Municipal de Saúde | 08.435.209/0001-90 | Contrato 107/FMS/2025 (gerenciamento de frota) |
| Fundo Municipal de Assistência Social | 11.786.437/0001-19 | Contrato 022/FMAS/2025 (gerenciamento de frota) |
| Fundação Municipal de Esportes | 86.951.555/0001-34 | Contrato 010/FME/2025 (gerenciamento de frota) |
| Fundação Cultural de Criciúma | 00.074.312/0001-40 | Contrato 020/FCC/2025 (gerenciamento de frota) |
| Câmara Municipal de Criciúma | 83.728.949/0001-30 | **Nenhum** registro de manutenção de veículos. Há credenciamento de combustível (seção 1.5) |
| CriciúmaPrev (instituto de previdência) | 05.140.677/0001-49 | Revisão de 70.000 km do seu único veículo (Inexigibilidade 3/2026, estimado R$ 5.772,39) |

Buscas feitas (todas com `municipios=4386`, tipos edital, contrato e ata): "veículos", "manutenção", "frota", "oficina", "gerenciamento de manutenção", e a lista completa de 1.149 contratos do município sem termo de busca.

### 1.2 O registro recente: Pregão Eletrônico 093/PMC/2026 (frota da Polícia Civil)

| Campo | Valor, como consta no registro |
|---|---|
| Órgão | Município de Criciúma. Órgão gerenciador da ata: "Secretaria Geral do município de Criciúma/SC" (edital, item 3.1). O termo de referência é assinado pela Delegacia Regional de Polícia Civil de Criciúma |
| Número | Pregão Eletrônico nº 093/PMC/2026; Processo Administrativo nº 709145 (no PNCP: processo "7091452026", controle `82916818000113-1-000179/2026`) |
| Objeto (texto exato) | "Registro de preços de peças e serviços, para manutenção preventiva e corretiva (mecânica, elétrica, eletrônica, suspensão, freios, ar condicionado) da frota de veículos leves, médios, SUV’s e camionetes, pertencentes a Polícia Civil do município de Criciúma/SC." |
| Modalidade | Pregão eletrônico, **registro de preços** (SRP = sim); critério "maior desconto (%) sobre tabela" (Tabela CILIA); hora técnica de referência R$ 180,00 |
| Valor estimado (teto) | **R$ 448.560,00** "para o período de 12 meses" (termo de referência, item 6) |
| Divisão por lote | Lote 1, leves e motocicletas: R$ 196.380,00 · Lote 2, médios e sedãs: R$ 87.660,00 · Lote 3, SUVs: R$ 52.320,00 · Lote 4, camionetes, vans e carga: R$ 112.200,00 |
| Como o teto foi calculado (segundo o próprio documento) | "até 12% do seu valor venal de mercado (Tabela FIPE de referência)" por veículo por ano; soma dos valores FIPE da frota: R$ 3.737.966,66 |
| Número de veículos | O termo de referência diz **"uma frota de 54 veículos"** (item 2) e "TOTAL DA FROTA 54". Atenção: as quantidades por lote listadas no mesmo documento são 38, 11, 4 e 9, que somam **62** (calc.). O documento não explica a diferença |
| Datas | Publicado no PNCP em 2026-08-20; sessão remarcada para 18/09/2026 às 09h (aviso de retificação de 01/09/2026) |
| Valor contratado | **Nenhum.** Em 2026-09-29 os 4 itens aparecem "Em andamento" no PNCP, sem resultado publicado; as edições do Diário Oficial de Criciúma de 18/09 a 28/09/2026 não trazem homologação |
| Fornecedor | Nenhum ainda |
| Valores pagos | Não se aplica (sem ata assinada) |
| R$ por veículo por ano (calc.) | R$ 448.560,00 ÷ 54 = **R$ 8.306,67** (com 62 veículos: R$ 7.234,84) |

Fontes (coletadas em 2026-09-29):
- Registro no PNCP: https://pncp.gov.br/app/editais/82916818000113/2026/179 · API: https://pncp.gov.br/api/consulta/v1/orgaos/82916818000113/compras/2026/179
- Itens e valores por lote: https://pncp.gov.br/api/pncp/v1/orgaos/82916818000113/compras/2026/179/itens
- Termo de referência (PDF): https://pncp.gov.br/pncp-api/v1/orgaos/82916818000113/compras/2026/179/arquivos/2
- Edital (PDF): https://pncp.gov.br/pncp-api/v1/orgaos/82916818000113/compras/2026/179/arquivos/4
- Aviso de retificação e remarcação (PDF): https://pncp.gov.br/pncp-api/v1/orgaos/82916818000113/compras/2026/179/arquivos/5
- Diário Oficial Eletrônico de Criciúma nº 4046, 20/08/2026 (aviso de licitação): https://apoio.criciuma.sc.gov.br/files/2026-08-20-1787257880-20-08-2026.pdf
- Diário Oficial Eletrônico de Criciúma nº 4056, 03/09/2026 (retificação e remarcação): https://apoio.criciuma.sc.gov.br/files/2026-09-03-1788467783-03-09-2026.pdf

**Ciclo anterior da mesma frota:** Pregão Eletrônico 101/PMC/2024 (PNCP `82916818000113-1-000124/2024`), "Registro de Preços de peças e serviços, para manutenção preventiva e corretiva dos veículos que compõem a frota de viaturas da Polícia Civil de Criciúma/SC". Valor estimado R$ 408.784,32; valor homologado R$ 301.566,53; 26 itens, um por modelo de veículo, somando **54** unidades (calc.), incluindo 4 motocicletas; ata válida por "1 (um) ano". O Diário Oficial de Criciúma nº 4034, de 04/08/2026 (https://apoio.criciuma.sc.gov.br/files/2026-08-04-1785874397-04-08-2026.pdf), designa fiscal para a "Ata de Registro de Preços nº 195/2024 ... empresa De Luca Peças Automotivas Ltda, CNPJ 04.013.657/0001-44" com esse objeto. Fontes: https://pncp.gov.br/api/consulta/v1/orgaos/82916818000113/compras/2024/124 · https://pncp.gov.br/api/pncp/v1/orgaos/82916818000113/compras/2024/124/itens · edital: https://pncp.gov.br/pncp-api/v1/orgaos/82916818000113/compras/2024/124/arquivos/1

### 1.3 Onde aparece "R$ 500.000,00": dois registros de preços de 2024

A Prefeitura não compra a manutenção da frota em um único contrato: publica registros de preços separados por especialidade (elétrica e ar-condicionado, mecânica de leves, retífica de motores, bicos injetores, caminhões e ônibus, filtros e lubrificantes, pneus, funilaria). Nesses editais cada item é **um modelo de veículo**, com a quantidade de unidades daquele modelo; por isso a soma das quantidades dá o número de veículos cobertos. Dois deles têm valor estimado de exatamente R$ 500.000,00.

| Campo | PE 193/PMC/2024 | PE 163/PMC/2024 |
|---|---|---|
| Controle PNCP | `82916818000113-1-000230/2024` | `82916818000113-1-000193/2024` |
| Processo administrativo | 704359/2024 | 703842/2024 |
| Objeto (texto exato) | "Registro de preços de peças e serviços, para manutenção elétrica e ar condicionado, da frota de veículos leves, caminhões e ônibus, pertencentes ao município de Criciúma/SC." | "Registro de Preços de peças e serviços, para retífica de motores, da frota de veículos leves, caminhões e ônibus, pertencentes ao município de Criciúma/SC." |
| Modalidade | Pregão eletrônico, registro de preços, "maior desconto (%) sobre tabela" | Pregão eletrônico, registro de preços |
| Valor estimado (teto) | R$ 500.000,00 ("VALOR TOTAL DA CONTRATAÇÃO" na capa do edital) | R$ 500.000,00 |
| Valor homologado | R$ 412.743,91 (relatório de vencedores e API do PNCP) | API do PNCP: R$ 208.672,84, mas só 49 dos 83 itens têm resultado lançado; o relatório de vencedores anexado ao mesmo registro soma R$ 379.385,81 para os 83 itens. A diferença não é explicada nos documentos |
| Fornecedores e valores homologados | Auto Elétrica Smania Ltda (01.472.839/0001-95) R$ 198.811,01 · Centro Automotivo Fica Frio Ltda (22.124.216/0001-00) R$ 188.810,95 · Mecânica Sangaletti Ltda (07.160.911/0001-25) R$ 14.451,22 · 10 Ponto Auto Center Ltda (36.338.745/0001-02) R$ 10.670,73 | Borges Comércio Varejista de Peças e Retífica (29.120.465/0001-68) R$ 189.447,53 · Martinelli Comercial de Peças Sul Catarinense (07.533.147/0001-96) R$ 116.033,96 · De Luca Peças Automotivas Ltda (04.013.657/0001-44) R$ 73.904,33 |
| Vigência | Ata de 12 meses (edital, item 5.1) | Ata nº 4/2025, assinada em 16/01/2025, válida até 16/01/2026 |
| Veículos cobertos (calc.) | **164** unidades em 85 itens (inclui 2 reboques) | **162** unidades em 83 itens |
| R$ por veículo por ano (calc., só esta especialidade) | R$ 3.048,78 | R$ 3.086,42 |
| Valores pagos | Não obtidos (seção 4, linha 4) | Não obtidos |

Fontes (2026-09-29):
- PE 193/PMC/2024: https://pncp.gov.br/app/editais/82916818000113/2024/230 · itens: https://pncp.gov.br/api/pncp/v1/orgaos/82916818000113/compras/2024/230/itens · edital: https://pncp.gov.br/pncp-api/v1/orgaos/82916818000113/compras/2024/230/arquivos/1 · vencedores: https://pncp.gov.br/pncp-api/v1/orgaos/82916818000113/compras/2024/230/arquivos/2
- PE 163/PMC/2024: https://pncp.gov.br/app/editais/82916818000113/2024/193 · itens: https://pncp.gov.br/api/pncp/v1/orgaos/82916818000113/compras/2024/193/itens · vencedores: https://pncp.gov.br/pncp-api/v1/orgaos/82916818000113/compras/2024/193/arquivos/3 · ata: https://pncp.gov.br/api/pncp/v1/orgaos/82916818000113/compras/2024/193/atas

**Os outros registros de preços da mesma família** (valores estimados, API do PNCP): mecânica de veículos leves, PE 194/PMC/2024, R$ 400.000,00 para 94 unidades (homologado R$ 156.528,92); elétrica e ar-condicionado, PE 130/PMC/2025 (sucessor do 193/2024), R$ 650.000,00 para 166 unidades (homologado R$ 560.503,62); bicos injetores, PE 131/PMC/2025, R$ 700.000,00; caminhões e ônibus, PE 18/PMC/2024, R$ 900.000,00; equipamentos pesados, PE 49/PMC/2024, R$ 3.706.068,83. A lista completa, com links, está em `private/archive/data/criciuma-fleet.json` (chave `all_criciuma_fleet_tenders_pncp`).

### 1.4 Os contratos de gerenciamento de frota (Prefeitura e quatro órgãos)

Desde novembro de 2025 a Prefeitura e quatro órgãos municipais têm contratos derivados da ata de registro de preços do **CINCATARINA** (Consórcio Interfederativo Santa Catarina, CNPJ 12.075.748/0001-32), Pregão Eletrônico 0093/2023, processo 0062/2023-e. Objeto da ata: "REGISTRO DE PREÇOS para futura e eventual contratação, com fornecimento parcelado, de serviços de Gerenciamento da Manutenção Preditiva, Preventiva e Corretiva de Veículos Automotores e Equipamentos, incluindo Pneus, Óleos Lubrificantes e Lavação, em uma ampla rede credenciada de oficinas, autopeças ou concessionárias, no Modelo de Autogestão (...)". Valor estimado da ata para todos os entes consorciados: R$ 205.859.426,00; homologado R$ 205.838.840,06.

Fornecedor dos cinco contratos: **MAXIFROTA SERVIÇOS DE MANUTENÇÃO DE FROTA LTDA**, CNPJ 27.284.516/0001-61. Taxa de administração: "0,01% (zero virgula zero um por cento negativo)". O contrato diz que "O valor contratado é meramente estimativo, de forma que os pagamentos dependerão dos serviços e fornecimentos, efetivamente, prestados" (cláusula 3.4) e que a soma das manutenções de um veículo em 12 meses não deve ultrapassar 40% da tabela FIPE.

| Contrato | Órgão | Assinatura | Vigência | Valor estimado | Nº de veículos no contrato |
|---|---|---|---|---|---|
| 130/PMC/2025 (processo 168/2025) | Prefeitura | 17/11/2025 | 24/11/2025 a 24/11/2026 | R$ 5.200.000,00 | não informado |
| 107/FMS/2025 (processo 37/2025) | Fundo Municipal de Saúde | 17/11/2025 | 25/11/2025 a 25/11/2026 | R$ 700.000,00 | não informado |
| 010/FME/2025 (processo 8/2025) | Fundação Municipal de Esportes | 25/11/2025 | 25/11/2025 a 25/11/2026 | R$ 250.000,00 | não informado |
| 022/FMAS/2025 (processo 25/2025) | Fundo Municipal de Assistência Social | 17/11/2025 | 25/11/2025 a 25/11/2026 | R$ 200.000,00 | não informado |
| 020/FCC/2025 (processo 30/2025) | Fundação Cultural | 17/11/2025 | 25/11/2025 a 25/11/2026 | R$ 50.000,00 | não informado |

Nenhum dos cinco contratos (PDF de 15 a 16 páginas cada) lista os veículos atendidos, e nenhum tem valor de R$ 500.000,00. Sem o número de veículos, não é possível calcular R$ por veículo para esses contratos.

Fontes (2026-09-29):
- Ata CINCATARINA: https://pncp.gov.br/api/consulta/v1/orgaos/12075748000132/compras/2023/93
- Contrato 130/PMC/2025: https://pncp.gov.br/app/contratos/82916818000113/2025/75 · PDF: https://pncp.gov.br/pncp-api/v1/orgaos/82916818000113/contratos/2025/75/arquivos/1
- 107/FMS/2025: https://pncp.gov.br/api/pncp/v1/orgaos/08435209000190/contratos/2025/163
- 010/FME/2025: https://pncp.gov.br/api/pncp/v1/orgaos/86951555000134/contratos/2025/1
- 022/FMAS/2025: https://pncp.gov.br/api/pncp/v1/orgaos/11786437000119/contratos/2025/21
- 020/FCC/2025: https://pncp.gov.br/api/pncp/v1/orgaos/00074312000140/contratos/2025/1
- Diário Oficial de Criciúma nº 3999, 16/06/2026 (designação de fiscal dos contratos 130/PMC, 107/FMS, 020/FCC e 022/FMAS): https://apoio.criciuma.sc.gov.br/files/2026-06-16-1781642080-16-06-2026.pdf

### 1.5 Câmara Municipal de Criciúma

Nenhum registro de manutenção de veículos da Câmara foi encontrado no PNCP (lidos os objetos de 39 editais, 34 contratos e 14 atas com o CNPJ da Câmara; os 34 contratos são todos os que a Câmara tem no PNCP, conferidos na lista completa de 1.149 contratos do município). O único registro ligado à frota é o credenciamento de combustível (Inexigibilidade 13/2026; contrato `83728949000130-2-000015/2026`, R$ 87.490,00 por 12 meses: 11.000 litros de gasolina aditivada e 2.000 litros de gasolina comum). O Documento de Formalização da Demanda fala em "frota de veículos oficiais da Câmara Municipal" sem dizer quantos veículos são. O site da Câmara (camaracriciuma.sc.gov.br) redireciona para uma página de captcha e não foi consultado. Fontes: https://pncp.gov.br/api/pncp/v1/orgaos/83728949000130/contratos/2026/15 · DFD: https://pncp.gov.br/pncp-api/v1/orgaos/83728949000130/compras/2026/13/arquivos/2

### 1.6 O que não foi encontrado

- Nenhum registro de manutenção de veículos com R$ 500.000,00 **e** 6 veículos, em nenhum órgão de Criciúma.
- Nenhuma ocorrência de "500.000,00" junto de manutenção de veículos nas 120 edições do Diário Oficial Eletrônico de Criciúma de 09/04/2026 a 28/09/2026.
- Nenhum registro de manutenção de veículos da Câmara Municipal no PNCP.
- Valores efetivamente pagos (empenhado, liquidado, pago): não obtidos para nenhum dos registros (seção 4).

---

## 2. Comparação com outros municípios de SC

### 2.1 Critério

- Municípios de SC com população próxima à de Criciúma (214.493 habitantes no Censo 2022): São José, Itajaí, Chapecó, Palhoça, Jaraguá do Sul, Lages, Blumenau, Balneário Camboriú e Brusque. População: IBGE, Censo 2022, tabela 4709 (https://apisidra.ibge.gov.br/values/t/4709/n6/4204608,4208203,4204202,4211900,4216602,4208906,4209300,4202404,4202008,4202909/v/93/p/2022).
- Registros do PNCP de 2024 a 2026 com objeto de manutenção de frota (busca "manutenção veículos" e "manutenção frota" por município), abertos um a um. Entram só os que **dizem o número de veículos** em documento publicado no PNCP e têm período definido.
- Conta: valor estimado (teto) ÷ número de veículos ÷ período em anos. É **teto por veículo**, não gasto por veículo. Nenhuma tabela privada de preços foi usada.

### 2.2 Tabela

| Município (hab. 2022) | Órgão e registro | Valor estimado | Homologado | Período | Veículos (como consta) | R$ por veículo por ano (calc.) |
|---|---|---|---|---|---|---|
| São José (270.299) | Câmara Municipal, PE 06/2026 (`83708248000139-1-000032/2026`) | R$ 36.600,00 | R$ 10.900,00 | 12 meses | **6**: "A Frota do órgão é composta atualmente por 6 veículos de passeio" | **R$ 6.100,00** |
| São José (270.299) | Câmara Municipal, PE 011/2024 (`83708248000139-1-000037/2024`) | R$ 27.315,00 | R$ 22.815,00 | 12 meses | 3 listados (um quarto veículo, na garantia, ficou de fora) | R$ 9.105,00 |
| São José (270.299) | Prefeitura, frota da Delegacia Regional de Polícia Civil, PE 25/2024 (`82892274000105-1-000037/2024`) | R$ 283.500,00 | R$ 236.358,00 | 1 ano | 49 linhas no Anexo I (37 leves e 12 médios); a placa MKM9301 aparece duas vezes, então 48 placas distintas | R$ 5.785,71 (com 48: R$ 5.906,25) |
| Chapecó (254.785) | Prefeitura, PE 084/2026 (`83021808000182-1-000108/2026`) | R$ 6.696.300,00 | R$ 5.868.498,50 | 12 meses | "aproximadamente 700 veículos, incluindo máquinas e equipamentos" | R$ 9.566,14 (contagem aproximada, inclui máquinas) |
| Brusque (141.385) | SAMAE (autarquia de água), PE 083/2024 (`82985003000196-1-000153/2024`) | R$ 727.020,35 | R$ 672.691,55 | 12 meses | 51 no Anexo V: 20 motos, 6 carros, 15 caminhonetes, 9 caminhões, 1 retroescavadeira | R$ 14.255,30 |
| Blumenau (361.261) | SAMAE (autarquia de água), PE 2234/2024 (`83779462000186-1-000024/2024`) | R$ 1.983.450,00 (só os lotes de veículos; o registro inteiro, R$ 2.628.450,00, inclui 2 retroescavadeiras) | R$ 2.479.973,01 (registro inteiro) | 12 meses | 31: "15 Veículos Leves, 07 Veículos Médios, 09 Veículos Pesados" | R$ 63.982,26 (só os 15 leves: R$ 35.083,33) |

**Resumo (calc.):** 6 registros de 4 municípios. Faixa de **R$ 5.785,71 a R$ 63.982,26** por veículo por ano; **mediana R$ 9.335,57**. Sem Chapecó (contagem aproximada), a mediana é R$ 9.105,00.

**Criciúma, para comparação (mesma conta):** Polícia Civil 2026, R$ 8.306,67 (54 veículos) ou R$ 7.234,84 (62); Polícia Civil 2024, R$ 7.570,08 (54); os dois registros de R$ 500.000,00 de 2024 dão R$ 3.048,78 e R$ 3.086,42 por veículo, mas cada um cobre uma só especialidade.

**O caso mais parecido com a afirmação:** a Câmara de São José tem exatamente 6 carros de passeio e fixou teto de R$ 36.600,00 para 12 meses de manutenção completa (mão de obra e peças).

Fontes dos registros (2026-09-29):
- São José, Câmara 2026: https://pncp.gov.br/app/editais/83708248000139/2026/32 · edital (ZIP com PDF): https://pncp.gov.br/pncp-api/v1/orgaos/83708248000139/compras/2026/32/arquivos/1
- São José, Câmara 2024: https://pncp.gov.br/app/editais/83708248000139/2024/37 · edital (ZIP com PDF): https://pncp.gov.br/pncp-api/v1/orgaos/83708248000139/compras/2024/37/arquivos/1
- São José, Polícia Civil 2024: https://pncp.gov.br/app/editais/82892274000105/2024/37 · termo de referência: https://pncp.gov.br/pncp-api/v1/orgaos/82892274000105/compras/2024/37/arquivos/2
- Chapecó 2026: https://pncp.gov.br/app/editais/83021808000182/2026/108 · ETP: https://pncp.gov.br/pncp-api/v1/orgaos/83021808000182/compras/2026/108/arquivos/2 · termo de referência: https://pncp.gov.br/pncp-api/v1/orgaos/83021808000182/compras/2026/108/arquivos/3
- Brusque, SAMAE 2024: https://pncp.gov.br/app/editais/82985003000196/2024/153 · edital com Anexo V: https://pncp.gov.br/pncp-api/v1/orgaos/82985003000196/compras/2024/153/arquivos/2
- Blumenau, SAMAE 2024: https://pncp.gov.br/app/editais/83779462000186/2024/24 · termo de referência: https://pncp.gov.br/pncp-api/v1/orgaos/83779462000186/compras/2024/24/arquivos/5

### 2.3 Limites desta comparação

- A faixa é larga porque as frotas são diferentes: uma câmara com carros de passeio não se compara a uma autarquia de saneamento com caminhões pesados (em Blumenau, o lote de pesados sozinho tem teto de R$ 1.009.200,00 para 9 veículos). O TCU diz que a estimativa deve considerar tipo e idade da frota e distância percorrida (seção 3).
- Todos os valores são tetos. Em registro de preços, nem o homologado é gasto: o gasto é o que for empenhado e pago.
- Registros abertos e deixados de fora (motivo): São José PE 48/2024, secretaria de segurança (os valores por órgão no termo de referência não batem com a lista de veículos: há R$ 240.000,00 de leves para um órgão sem nenhum veículo leve listado); São José PE 27/2024, bombeiros (sem preço de mão de obra nem valor total publicado); Câmara de Palhoça, 3 veículos, R$ 16.441,97 (compra direta única, sem período); Itajaí (PE 067/2024, PE 085/2024, PE 220/2025, Dispensa 068/2024), Balneário Camboriú (PE 006/2025) e Blumenau Prefeitura (PE 34/2024), sem número de veículos nos documentos publicados; Jaraguá do Sul compra manutenção por veículo e por peça em dezenas de compras diretas, sem contrato anual de frota; Lages e Palhoça (Prefeitura), nenhum registro de manutenção de frota encontrado com os termos usados.
- Contratos de gerenciamento de frota (modelo CINCATARINA, como o de Criciúma) não dizem o número de veículos e ficaram fora.

---

## 3. Referências oficiais sobre custo de manutenção de frota pública

Nenhuma referência oficial encontrada traz um valor em R$ por veículo por ano. O que existe:

| Fonte | O que diz | URL (2026-09-29) |
|---|---|---|
| TCU, Acórdão 1077/2019-Plenário, relatora Ana Arraes, sessão de 15/05/2019 (jurisprudência selecionada, tema "Orçamento estimativo") | "Nas licitações para contratação de serviços de gerenciamento de manutenção de veículos, devem ser considerados nos cálculos da estimativa de custos, entre outros elementos intrínsecos às características do objeto, o tipo e a idade da frota, bem como a previsão de distância a ser percorrida pelos veículos, com vistas à alocação de recursos suficientes e necessários para prestação dos serviços durante todo o período contratual (art. 8º, caput, da Lei 8.666/1993)." | https://pesquisa.apps.tcu.gov.br/documento/jurisprudencia-selecionada/*/KEY:JURISPRUDENCIA-SELECIONADA-73112 |
| IN SLTI/MP nº 3, de 15/05/2008 (administração pública federal; vigência atual não verificada nesta pesquisa) | "Veículo recuperável: veículo cuja recuperação seja possível com orçamento máximo de cinqüenta por cento de seu valor de mercado." Art. 24: os órgãos apuram o custo operacional de cada veículo em um "Mapa de Controle do Desempenho e Manutenção do Veículo Oficial" | http://comprasnet.gov.br/legislacao/in/IN03_08.htm |
| Parâmetros nos próprios documentos de Criciúma | Termo de referência do PE 093/PMC/2026: teto anual por viatura de "até 12% do seu valor venal de mercado (Tabela FIPE de referência)". Contratos CINCATARINA: a soma das manutenções de um veículo em 12 meses não deve ultrapassar "40% da tabela FIPE" | seções 1.2 e 1.4 |

Não foram encontrados estudos de custo de frota da CGU ou do Estado de SC com valor por veículo nesta pesquisa (limite de buscas respeitado; ver seção 5).

---

## 4. Diário de transparência

Todas as consultas em 2026-09-29, a partir de IP dos EUA.

| # | Fonte | URL | Formato | Login ou captcha | Passos | Obstáculos |
|---|---|---|---|---|---|---|
| 1 | PNCP, busca pública | https://pncp.gov.br/api/search/?q=...&tipos_documento=edital\|contrato\|ata&municipios=4386 | JSON | Não | Descobrir o `municipio_id` interno do PNCP (Criciúma = 4386) a partir de uma busca por nome; depois filtrar por município e tipo de documento | Conexão **reiniciada pelo servidor** ("Connection reset by peer") em pedidos sem User-Agent de navegador e com `tam_pagina=100`; funcionou com User-Agent de navegador e páginas de 50. A busca não traz valor estimado dos editais, só o valor global dos contratos. A busca por texto é ampla (em Jaraguá do Sul, "manutenção frota" devolveu 2.494 documentos) |
| 2 | PNCP, API de consulta | https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq} | JSON | Não | Um pedido por compra | **HTTP 429 (Too Many Requests)** depois de uma sequência curta de pedidos (cerca de uma dúzia em poucos segundos); exigiu pausa de 20 s ou mais entre tentativas. Não existe filtro por município com valor, então cada compra precisa de um pedido |
| 3 | PNCP, API do portal (itens, arquivos, contratos, resultados) | https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens · /arquivos · /contratos/{ano}/{seq} | JSON e PDF | Não | Itens trazem quantidade e valor por item; arquivos trazem edital e termo de referência em PDF (com camada de texto, lida com `pdftotext`) | Resultado por item volta vazio (HTTP 204) quando a licitação ainda não foi homologada. O número de veículos quase nunca está nos campos estruturados: está no PDF, ou na soma das quantidades quando o edital lista um item por modelo de veículo |
| 4 | Portal da Transparência de Criciúma | https://transparencia.criciuma.sc.gov.br/ | HTML que abre o portal Betha em iframe (https://transparencia.betha.cloud/#/n4W91vnHptoBkiHKAxioOA==/...) | O código da página carrega um login anônimo (OAuth Betha) e o reCAPTCHA do Google | A página inicial lista as consultas (despesas por credor, empenhos pagos, contratos, atas, bens patrimoniais) como links para o Betha | A API do Betha (`api.transparencia.betha.cloud/transparencia/api/...`) responde **401 "Sem token de autenticação"** a pedidos sem o token; os resultados chegam por WebSocket. **Valores pagos não foram obtidos.** Consulta manual em navegador é o próximo passo (seção 5) |
| 5 | Diário Oficial Eletrônico de Criciúma | https://www.criciuma.sc.gov.br/does.php · edições em https://apoio.criciuma.sc.gov.br/files/AAAA-MM-DD-*.pdf | PDF com texto | Não | Listagem paginada (12 edições por página, 216 páginas); baixadas as 120 edições de 09/04/2026 a 28/09/2026 (601 MB) e lidas com `pdftotext` | Sem busca por texto no site; é preciso baixar edição por edição. Nenhuma ocorrência de "500.000,00" junto de manutenção de veículos nessas 120 edições |
| 6 | DOM-SC (Diário Oficial dos Municípios de SC) | https://diariomunicipal.sc.gov.br/?r=site/portal&codigoEntidade=79 | HTML | Não | Busca por entidade "Prefeitura municipal de Criciúma" | A entidade existe na lista, mas **sem nenhuma publicação**: Criciúma publica no seu próprio Diário Oficial (linha 5). A busca por texto do DOM-SC traz resultados de todos os municípios (útil só para extratos do CINCATARINA) |
| 7 | TCE-SC, e-Sfinge e Farol | https://www.tcesc.tc.br/esfinge · https://servicos.tcesc.tc.br/farol_externo/ | Painéis Qlik Sense (paineistransparencia.tce.sc.gov.br) | Não | O e-Sfinge é o sistema de envio dos municípios ao TCE; o acesso público é pelos painéis do Farol (licitações, despesas municipais, painel de preços) | Os painéis carregam dados por WebSocket do Qlik, **sem API aberta nem arquivo para baixar** encontrado. Não consultados por script. O link antigo do "Portal do Cidadão" (servicos.tce.sc.gov.br/sic/home.php) devolve 404 |
| 8 | Site da Câmara de Criciúma | https://www.camaracriciuma.sc.gov.br/ | HTML | **Captcha** (redireciona para /captcha) | Nenhum | Não consultado |
| 9 | IBGE, SIDRA (população, Censo 2022) | https://apisidra.ibge.gov.br/values/t/4709/n6/4204608,.../v/93/p/2022 | JSON | Não | Um pedido | Nenhum |
| 10 | TCU, jurisprudência selecionada | https://pesquisa.apps.tcu.gov.br/rest/publico/base/jurisprudencia-selecionada/documentosResumidos | JSON | Não | Busca por termo | O parâmetro de ordenação precisa ser um campo válido (`DTRELEVANCIA desc`), senão HTTP 422 |

**Nota sobre acesso do exterior:** diferente da pesquisa de Florianópolis, nenhum portal de Criciúma ou de SC bloqueou o IP dos EUA nesta coleta. Os obstáculos foram técnicos (token, WebSocket, captcha, limite de pedidos), não geográficos.

## 5. Próximos passos sugeridos (não feitos)

1. **Valores pagos:** abrir no navegador o Portal da Transparência de Criciúma (Betha), consultas "Empenhos pagos por ordem cronológica" e "Despesas por credor", e buscar os CNPJs dos fornecedores das seções 1.2 a 1.4 (De Luca Peças Automotivas, Auto Elétrica Smania, Centro Automotivo Fica Frio, Borges, Martinelli, Maxifrota). Isso diz quanto de fato foi pago.
2. **Resultado do PE 093/PMC/2026:** conferir no PNCP a homologação da sessão de 18/09/2026 (ainda sem resultado em 29/09/2026).
3. **Número de veículos da Prefeitura:** a consulta "Relação de bens patrimoniais" do mesmo portal Betha e o link "Rastreamento de veículos da frota municipal" (https://rastreamento.inviocar.com/sharing/c883d5fe8057f022b7e44d7f195ae1e0) podem dar a frota total, que falta para calcular R$ por veículo do contrato de R$ 5,2 milhões.
4. **Origem da afirmação:** perguntar ao autor da afirmação qual documento ele viu (número de edital, data, órgão). Com isso, a verificação fica direta.
5. **Pedido pela LAI (Fala.BR ou e-SIC municipal):** pedir à Prefeitura o número de veículos coberto pelo contrato 130/PMC/2025 e os valores pagos por contrato em 2025 e 2026.

## 6. Arquivos e scripts

| Arquivo | Conteúdo |
|---|---|
| `private/archive/data/criciuma-fleet.json` | Registros de Criciúma, contratos de gerenciamento, lista de 33 editais de manutenção de veículos de órgãos de Criciúma no PNCP, comparação com outros municípios, referências oficiais. Chaves em inglês, valores numéricos em BRL, fonte e data em cada registro |
| `private/archive/pipelines/criciuma/pncp_search.py` | Busca pública do PNCP por termo, tipo e município, com User-Agent de navegador e paginação |
| `private/archive/pipelines/criciuma/pncp_get.py` | Baixa um endereço da API do PNCP (JSON ou arquivo) com novas tentativas |
| `private/archive/pipelines/criciuma/criciuma_fleet_editais.py` | Lista os editais de manutenção de veículos de órgãos de Criciúma e busca valor estimado e homologado |
| `private/archive/pipelines/criciuma/doe_fetch.py` | Baixa edições do Diário Oficial Eletrônico de Criciúma e extrai o texto |
| `private/archive/pipelines/criciuma/bench_fetch.py` | Baixa cabeçalho, itens e lista de arquivos de compras do PNCP (comparação) |
| `private/archive/pipelines/criciuma/bench_docs.py` | Baixa editais e termos de referência do PNCP e extrai o texto |
| `private/archive/pipelines/criciuma/build_json.py` | Monta `private/archive/data/criciuma-fleet.json` com os valores copiados das fontes e calcula as razões |
