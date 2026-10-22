# Ponte Hercílio Luz: contratos, empresas, responsáveis e achados oficiais

**Data da coleta:** 2026-09-29 (todas as consultas abaixo foram feitas nesta data, salvo indicação)
**Ponto de partida:** seção 4 de `private/gemini/BRASIL-IMPOSTO_RESEARCH_florianopolis-verificacao_2026-09-25.md` (fora do repositório, D97)
**Pergunta:** para a restauração da ponte, quais empresas foram contratadas, quem respondia pelo contrato no Estado, quem governava, quanto foi pago e o que os órgãos oficiais concluíram.
**Onde a pesquisa foi feita:** computador nos EUA (IP norte-americano). Vários servidores públicos brasileiros não respondem a esse acesso; isso está no diário (seção 7).

## Regras desta pesquisa (valem para o uso no site)

1. Só **papéis** (quem ocupava qual cargo, quem assinou, quem foi fiscal) e **achados oficiais**, com as palavras exatas do órgão.
2. Nenhuma inferência de irregularidade além do texto do órgão. Não há, neste documento, nenhuma conclusão própria sobre conduta de pessoa ou empresa.
3. Cada nome vem com fonte oficial e papel. Cada achado vem com a situação jurídica (em aberto, arquivado, condenação, absolvição, em recurso) **tal como consta no documento lido**; quando não foi possível confirmar a situação atual, isso está escrito.
4. Nenhum número sem URL oficial e data da coleta.
5. Menção a um nome num processo não significa culpa. Recomendação para o site: exibir sempre o papel e a situação do processo ao lado do nome, e nunca listar pessoas numa tela de "achados" sem a decisão correspondente.

## 0. Resumo

| Item | Resultado | Fonte principal |
|---|---|---|
| 1. Os 13 contratos | ✅ Tabela completa (número, objeto, empresa, CNPJ, datas, valores, situação). Soma igual à de 2026-09-25: R$ 465.106.951,83 original e R$ 484.645.236,82 atual. Consórcios: Florianópolis Monumento (duas composições diferentes nas fontes oficiais) e Prosul-Concremat. Um 14º registro ligado à restauração (RMG, DL-00001/2618-2019) escapou do filtro original | Registro de contratos SIGEF/SICOP (CGE-SC); Receita (via espelho); TCE-SC |
| 2. Quem assinou | ✅ Nos três contratos principais, assinou pelo Estado o dirigente do DEINFRA: Romualdo Theophanes de França Júnior (PJ-264/2008) e Wanderley Teodoro Agostini (PJ-012/2015 e PJ-056/2016) | Extratos no DOE-SC nº 18.501, nº 20.010 e nº 20.283 |
| 3. Governadores | ✅ Seis pessoas no período, com datas | Alesc, Memória Política |
| 4. Pagamentos | ⚠️ Parcial: por empresa e ano, de 2011 em diante, sem separar por contrato. Ex.: Teixeira Duarte, R$ 373.694.994,99 brutos de 2016 a 2020 (inclui um contrato de outras pontes) | Portal da Transparência de SC (API) |
| 5. Achados oficiais | ✅ TCE-SC: multas em 2015, recursos julgados em 2017, multa por seguro em 2017, prescrição e arquivamento em 2025 com dois processos novos abertos. Alesc: CPI encerrada em 2019 com "encaminhamento para apurar possíveis ilicitudes". MPSC: ação de improbidade de 2018 sem decisão localizada | DOTC-e do TCE-SC; Agência Alesc; MPSC |

---

## 1. Os 13 contratos de restauração, supervisão e projetos (2006 a 2019)

### 1.1 Fonte

Portal de Dados Abertos de SC, conjunto "Contratos", organização Controladoria-Geral do Estado (CGE-SC), origem SIGEF e SICOP (Sistema Integrado de Controle de Obras Públicas):
- Arquivo: https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/ff7c3cac-3e38-4801-9fd8-e4ccb69ca31d/download/contratos.csv (73.749.080 bytes; SHA-256 `839d2ab72acdd7a088e3563a0281250ddf5f151b6f74d7bb4bd918e025a35860`; recurso atualizado pelo portal em 2026-09-29 10:02).
- Dicionário de dados v1.1: https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/7e5a6853-70c4-4282-b866-2c37856bdefc/download/dicionario-de-dados-contratos-v1.1.xlsx
- Script que refaz o filtro: `pipelines/ponte/filter_contracts.py` (filtro "PONTE" e "HERCILIO", sem acento, em objeto, resumo ou bem público). Resultado: os mesmos 26 registros da coleta de 2026-09-25; os 13 abaixo são o grupo "restauração, supervisão e projetos, 2006 a 2019" daquela pesquisa. A soma bate com a de 2026-09-25 ao centavo.

### 1.2 Tabela

| # | Contrato | Objeto (texto do registro, resumido só no fim) | Contratada (nome no registro) | CNPJ | Assinatura | Valor original | Valor atual | Situação | Unidade gestora (código) | Processo SGPe |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | PJ-00170/2006 | Execução de serviços de gerenciamento, coordenação, supervisão, controle de qualidade e apoio a fiscalização das obras de reabilitação da Ponte Hercílio Luz em Florianópolis | CONCREMAT ENG. E TECNOLOGIA S.A. | 33.146.648/0003-91 | 2006-08-25 | R$ 3.924.487,59 | R$ 6.106.108,74 | Rescindido | Departamento Estadual de Infraestrutura (530025) | vazio |
| 2 | PJ-00170/2006/PROSUL | Execução de serviços de gerenciamento, coordenação, supervisão, controle de qualidade e apoio a fiscalização das obras de reabilitação da Ponte Hercílio Luz em Florianópolis | PROSUL - Proj., Superv. e Planejamento Ltda | 80.996.861/0001-00 | 2006-08-25 | R$ 5.886.795,07 | R$ 9.160.234,18 | Rescindido | Departamento Estadual de Infraestrutura (530025) | vazio |
| 3 | PJ-00264/2008 | Execução dos Serviços de Restauração e Reabilitação da Ponte Hercílio Luz. | Consórcio Florianópolis Monumento | 10.769.406/0001-97 | 2008-11-27 | R$ 154.879.651,29 | R$ 63.008.872,09 | Rescindido | Departamento Estadual de Infraestrutura (530025) | vazio |
| 4 | PJ-00204/2014 | Elaboração de Projetos Complementares para a Execução da Restauração e Reabilitação da Ponte Hercílio Luz. | RMG ENGENHARIA S/C LTDA. | 38.738.381/0001-83 | 2014-11-14 | R$ 1.951.820,02 | R$ 1.951.820,02 | Concluído | Departamento Estadual de Infraestrutura (530025) | 20370/2014 |
| 5 | PJ-00012/2015 | Execução dos Serviços de Conclusão das Estruturas de Sustentação Inferior da Ponte Hercílio Luz. | EMPA SA SERVIÇOS DE ENGENHARIA | 17.159.856/0001-07 | 2015-02-25 | R$ 10.357.290,64 | R$ 12.941.168,93 | Concluído | Departamento Estadual de Infraestrutura (530025) | 20369/2014 |
| 6 | PJ-00143/2015 | Execução dos Serviços de Montagem da Complementação da Treliça Espacial de Sustentação Provisória da Ponte Hercílio Luz. | EMPA SA SERVIÇOS DE ENGENHARIA | 17.159.856/0001-07 | 2015-10-02 | R$ 11.400.601,42 | R$ 11.400.601,42 | Concluído | Departamento Estadual de Infraestrutura (530025) | 19225/2015 |
| 7 | PJ-00001/2016/FARES | Assessoramentoao DEINFRA na Atualização do Orçamento Referencial das Obras de Restauração e Recuperação da Ponte Hercílio Luz em Florianópolis | Fares & Associados Engenharia Ltda. | 52.573.623/0001-57 | 2016-01-04 | R$ 137.482,95 | R$ 137.482,95 | Concluído | Departamento Estadual de Infraestrutura (530025) | 25291/2015 |
| 8 | PJ-00056/2016 | Serviços de execução das obras de restauração e reabilitação da Ponte Hercílio Luz. | TEIXEIRA DUARTE - Engenharia e Construções S.A. | 24.447.770/0001-45 | 2016-03-10 | R$ 262.925.435,21 | R$ 363.824.397,74 | Concluído | Departamento Estadual de Infraestrutura (530001) | 23131/2015 |
| 9 | PJ-00093/2016 | Assessoramento ao DEINFRA no Monitoramento e Supervisão Técnica das Obras de Restauração e Recuperação da Ponte Hercílio Luz em Florianópolis | RMG ENGENHARIA S/C LTDA. | 38.738.381/0001-83 | 2016-05-18 | R$ 8.582.938,87 | R$ 11.110.051,81 | Concluído | Departamento Estadual de Infraestrutura (530025) | 10782/2015 |
| 10 | PJ-00009/2019 | Execução dos Serviços Emergenciais de Substituição/Reforço das Estruturas de Sustentação Provisória (ESP) Inferior da Ponte Hercílio Luz. | TEIXEIRA DUARTE - Engenharia e Construções S.A. | 24.447.770/0001-45 | 2019-02-20 | R$ 3.156.151,79 | R$ 3.156.151,79 | Concluído | Departamento Estadual de Infraestrutura (530025) | 26336/2018 |
| 11 | CT-00006/2019 | Assessoramento ao DEINFRA no Monitoramento e Supervisão Técnica das Obras de Restauração e Recuperação da Ponte Hercílio Luz em Florianópolis | RMG ENGENHARIA S/C LTDA. | 38.738.381/0001-83 | 2019-07-04 | R$ 1.773.434,13 | R$ 1.717.146,84 | Concluído | Departamento Estadual de Infraestrutura (530001) | 1051/2019 |
| 12 | PJ-00060/2019 | Serviços de Monitoramento Arqueológico e Educacional nas Obras de Restauração e Reabilitação da Ponte Hercílio Luz. | GEOARQUEOLOGIA Pesquisa Científica Ltda - ME | 01.956.161/0001-16 | 2019-07-08 | R$ 95.862,85 | R$ 96.200,31 | Andamento | Secretaria de Estado da Infraestrutura e Mobilidade (530001) | 12859/2018 |
| 13 | CT-00026/2019 | Execução dos projetos executivos das instalações elétricas, subestação, de iluminação pública viária, iluminação decorativa e de proteção contra descargas atmosféricas da Ponte Hercílio Luz. | SDF Engenharia EIRELI | 24.055.348/0001-44 | 2019-09-25 | R$ 35.000,00 | R$ 35.000,00 | Concluído | Secretaria de Estado da Infraestrutura e Mobilidade (530001) | 8415/2019 |
| | **Soma (calculada)** | | | | | **R$ 465.106.951,83** | **R$ 484.645.236,82** | | | |

Notas de leitura da tabela (todas do dicionário de dados ou do próprio registro):
- **Valor atual** é o valor do contrato com aditivos e supressões registrados no sistema. Não é valor pago (ver seção 4). Valores nominais, sem correção.
- **Situação** é o campo `SITUACAO` do sistema, copiado como está.
- O contrato PJ-00170/2006 aparece em **duas linhas**, uma por empresa (Concremat e Prosul), com a mesma data e o mesmo objeto. O Relatório DLC 462/2012 do TCE-SC (item 2.7; ver seção 5.2) diz que o contrato foi firmado com o "Consórcio Prosul-Concremat" e que o valor inicial foi de R$ 9.811.282,66; a soma das duas linhas (R$ 3.924.487,59 + R$ 5.886.795,07, calculada) dá exatamente esse valor.
- No PJ-00056/2016 (Teixeira Duarte), no CT-00006/2019 e no PJ-00060/2019 o código da unidade gestora é 530001; nos demais é 530025. O nome da unidade vem como "Departamento Estadual de Infraestrutura" em todos, menos no PJ-00060/2019 e no CT-00026/2019 ("Secretaria de Estado da Infraestrutura e Mobilidade"). O campo "unidade fiscalizadora" é 530025 (DEINFRA) nos 13. O registro não explica a diferença de código.
- Campos `NMREPUG` (representante da unidade gestora, isto é, quem assina pelo Estado) e `NMREPCREDOR` (representante da contratada) estão **vazios nos 13 contratos**. Por isso o signatário teve de ser procurado em outra fonte (seção 2).

### 1.3 Empresas e composição dos consórcios

Fonte cadastral: dados abertos do CNPJ da Receita Federal. O servidor oficial (`arquivos.receitafederal.gov.br` e `dadosabertos.rfb.gov.br`) recusou a conexão a partir dos EUA; os registros foram lidos no espelho de código aberto **minhareceita.org**, que republica em JSON a base aberta da Receita (versão declarada pelo próprio serviço: "2026-09", em https://minhareceita.org/updated). **É fonte derivada, não o servidor oficial**; conferido com um segundo espelho (BrasilAPI) para razão social e situação, com resultado igual.

| CNPJ | Razão social (Receita) | Natureza jurídica | Município | Situação cadastral (data) | Contratos |
|---|---|---|---|---|---|
| 33.146.648/0003-91 | CONCREMAT ENGENHARIA E TECNOLOGIA S/A (filial) | Sociedade Anônima Fechada | São Paulo/SP | Ativa (2005-11-03) | PJ-00170/2006 |
| 80.996.861/0001-00 | PROSUL PROJETOS SUPERVISAO E PLANEJAMENTO LTDA | Sociedade Empresária Limitada | Florianópolis/SC | Ativa (2005-11-03) | PJ-00170/2006/PROSUL |
| 10.769.406/0001-97 | CONSORCIO FLORIANOPOLIS MONUMENTO | Consórcio de Sociedades | Florianópolis/SC | Ativa (2009-04-16) | PJ-00264/2008 |
| 38.738.381/0001-83 | RMG - ENGENHARIA S/C LTDA | Sociedade Simples Limitada | Belo Horizonte/MG | Ativa (2005-11-03) | PJ-00204/2014, PJ-00093/2016, CT-00006/2019 |
| 17.159.856/0001-07 | EMPA S/A SERVICOS DE ENGENHARIA (nome fantasia na Receita: "TEIXEIRA DUARTE - ENGENHARIA E CONSTRUCOES") | Sociedade Anônima Fechada | São Paulo/SP | Ativa (2005-11-03) | PJ-00012/2015, PJ-00143/2015 |
| 52.573.623/0001-57 | FARES & ASSOCIADOS ENGENHARIA LTDA | Sociedade Empresária Limitada | São Paulo/SP | Ativa (2002-11-16) | PJ-00001/2016/FARES |
| 24.447.770/0001-45 | TEIXEIRA DUARTE - ENGENHARIA E CONSTRUCOES, S.A. | Estabelecimento, no Brasil, de Sociedade Estrangeira | São Paulo/SP | Ativa (2016-03-23) | PJ-00056/2016, PJ-00009/2019 |
| 01.956.161/0001-16 | GEOARQUEOLOGIA PESQUISA CIENTIFICA LTDA | Sociedade Empresária Limitada | Florianópolis/SC | Ativa (2001-02-25) | PJ-00060/2019 |
| 24.055.348/0001-44 | SDF ENGENHARIA LTDA | Sociedade Empresária Limitada | Siderópolis/SC | Ativa (2016-01-26) | CT-00026/2019 |

**Consórcio Florianópolis Monumento (PJ-00264/2008).** Duas fontes oficiais, que registram momentos diferentes:

| Fonte | O que diz |
|---|---|
| TCE-SC, Relatório DLC 462/2012, item 2.5 (sobre a licitação de 2008) | "O primeiro, denominado Florianópolis Monumento, formado pelas empresas CSA Group Inc. e Construtora Espaço Aberto Ltda." O mesmo relatório, item 2.6, registra que o Segundo Termo Aditivo, "de 19/06/2009, [...] alterou o CNPJ do Consórcio". |
| Receita Federal, quadro de sócios do CNPJ 10.769.406/0001-97 (base 2026-09, via espelho) | Sociedades consorciadas: CASTOR CONSTRUTORA E INCORPORADORA LTDA (CNPJ 76.601.343/0001-73) e CSA GERENCIAMENTO LTDA. (CNPJ 10.680.332/0001-18), ambas com entrada em 2009-04-16. |

Não há, nas fontes lidas, documento que ligue as duas composições (por exemplo, alteração de nome ou sucessão). Por isso as duas ficam registradas lado a lado, sem conclusão. Situação cadastral atual das consorciadas na Receita: Castor Construtora e Incorporadora Ltda, ativa; CSA Gerenciamento Ltda., **inapta desde 2018-08-28, motivo "omissão de declarações"** (texto cadastral da Receita, não é achado de órgão de controle).

**Consórcio Prosul-Concremat (PJ-00170/2006).** Não tem CNPJ próprio no registro de contratos: o sistema grava uma linha por empresa. A composição (Prosul e Concremat) vem do Relatório DLC 462/2012, item 2.7.

**Consórcio de 2019 fora do grupo dos 13.** O registro 2019CT004011 / 2020CT000215 (Fundo Estadual de Defesa Civil) é do "CONSORCIO RMG - TEIXEIRA DUARTE - REAPROVEITAMENTO DE ESTRUTURAS DE SUSTENTACAO PROVISORIAS DA PONTE HERCILIO LUZ" (CNPJ 35.194.522/0001-56), para projetos de outras pontes com material das estruturas provisórias. Não é obra da ponte e não entra nos 13.

### 1.4 O campo "fiscal do contrato" não é uma lista de servidores

O registro traz o campo `NMFISCAL`, que o dicionário define como "Nome do Fiscal do Contrato". Nos 13 contratos ele traz de 2 a 10 nomes. **Cuidado para o site:** cruzando com o quadro de sócios da Receita, pelo menos cinco nomes desse campo aparecem, com grafia idêntica, como sócio ou administrador **da própria contratada** daquele contrato (a Receita mascara o CPF, então a coincidência é de nome, não de documento) (por exemplo, o administrador do Consórcio Florianópolis Monumento consta no campo do PJ-00264/2008; um sócio-administrador da RMG consta no PJ-00204/2014; o sócio-administrador da Fares, da Geoarqueologia e da SDF consta no contrato da respectiva empresa). O sistema, portanto, mistura no mesmo campo pessoas do lado do Estado e do lado da empresa, e não diz quem é quem. **Recomendação:** não publicar esse campo como "servidores responsáveis". Os nomes ficam no JSON como dado bruto do sistema (`contracts[].sicop_inspector_field_raw`), com esse aviso, e fora de `officials[]`.

## 2. Quem assinou e quem respondia pelos contratos

Pergunta: para os três contratos principais, qual órgão contratou e quem assinou pelo Estado. Fonte principal: os extratos publicados no Diário Oficial do Estado (DOE-SC). As edições de 2012 em diante estão no repositório público do DOE (`portal.doe.sea.sc.gov.br/repositorio/...`); as anteriores a 2012, no Arquivo Público do Estado (`acervo.arquivopublico.sc.gov.br`). Nas citações, o travessão do original foi trocado por hífen (regra de estilo do projeto); o resto está como impresso.

### 2.1 Os três contratos principais

| Contrato | Órgão contratante | Ato publicado | Quem assinou pelo Estado (texto do DOE) | Quem assinou pela contratada (texto do DOE) | Fonte |
|---|---|---|---|---|---|
| PJ-00264/2008 (Consórcio Florianópolis Monumento) | Departamento Estadual de Infraestrutura (DEINFRA) | "EXTRATO DE TERMO DE CONTRATO- PJ.264/2008. Origem: CC.l. Edital nº 044/07 [...] Valor: R$ 154.879.651,29 [...] Local e Data: Florianópolis, 27.11.2008." | "Sr. Romualdo Theophanes de França Júnior pelo DEINFRA" | "Sr. Paulo Ney Almeida, pelo consórcio" | DOE-SC nº 18.501, 02/12/2008, página 462. Cópia do Arquivo Público: https://acervo.arquivopublico.sc.gov.br/uploads/r/arquivo-publico-do-estado-de-santa-catarina-apesc/2/0/a/20aeb6bb94c901d551291669cdafd8ffcc4666ee096d1c9a171a01ac460b213f/f834b399-2a11-48ee-a8d5-ae5064bc61a3-14634-DOE_18501_02_12_2008_484F.pdf |
| PJ-00012/2015 (EMPA) | DEINFRA | "DISPENSA DE LICITAÇÃO Nº 002/2015. PJ. 012/2015. Objeto: Execução de serviços de conclusão das estruturas de sustentação inferior da Ponte Hercílio Luz. Vencedora: EMPA S.A SERVIÇOS DE ENGENHARIA. Valor: R$ 10.357.290,64. Prazo: 180 dias. Florianópolis, 25.02.2015." | "Wanderley Teodoro Agostini, pelo DEINFRA" | "os Srs. João Pedro Carrilho Calado e José Luís Batista Silva, pela contratada" | DOE-SC nº 20.010, 27/02/2015, página 321: https://portal.doe.sea.sc.gov.br/repositorio/2015/20150227/Jornal/1129.pdf |
| PJ-00056/2016 (Teixeira Duarte) | DEINFRA | "DISPENSA DE LICITAÇÃO Nº 001/2016. PJ. 056/2016. Objeto: Serviços de execução das obras de restauração e reabilitação da Ponte Hercílio Luz. Vencedora: TEIXEIRA DUARTE - ENGENHARIA E CONSTRUÇÕES S.A. Valor: R$ 262.925.435,21. Prazo: 30 meses. Fundamentação Legal: Artigo 24, inciso "XV" da Lei nº 8.663 [sic] Florianópolis, 10.03.2016." | "Wanderley Teodoro Agostini, pelo DEINFRA" | "o Sr. José Luís Batista Silva e João Pedro Carrilho Calado Antunes Lopes, pela contratada" | DOE-SC nº 20.283, 25/04/2016, página 21: https://portal.doe.sea.sc.gov.br/repositorio/2016/20160425/Jornal/1406.pdf |

Leitura: nos três extratos, **quem assina pelo Estado é o dirigente do DEINFRA** (autarquia vinculada à Secretaria de Estado da Infraestrutura). Nenhum dos três extratos traz assinatura do secretário de Estado da Infraestrutura nem do governador. O cargo de cada signatário na data vem de documentos oficiais da mesma época (tabela 2.3).

### 2.2 Atos oficiais ligados aos mesmos contratos

| Ato | O que diz (citação) | Quem assina | Fonte |
|---|---|---|---|
| Resolução CA nº 0049/2016 do Conselho Administrativo do DEINFRA, 09/03/2016 (processo DEINFRA 23131/2015, o mesmo número de processo do PJ-00056/2016 no registro de contratos) | "RESOLVE: APROVAR a DISPENSA DE LICITAÇÃO N.º 001/2016, com fulcro no Art. 24, XV, da Lei N.º 8.666/93, para contratação do serviço de restauração e reabilitação da Ponte Hercílio Luz, sendo detentora a Empresa TEIXEIRA DUARTE - ENGENHARIA E CONSTRUÇÕES S.A., no valor de R$ 262.925.435,21 [...] e o prazo de execução dos serviços será de 30 (trinta) meses" | "Wanderley Teodoro Agostini Presidente" (como presidente do Conselho Administrativo do DEINFRA) | DOE-SC nº 20.260, 16/03/2016, página 19: https://portal.doe.sea.sc.gov.br/repositorio/2016/20160316/Jornal/1383.pdf |
| Portaria DEINFRA nº 103, de 05/04/2016 | Designa sete servidores (com matrícula), "sob a coordenação do primeiro, [para] fiscalizar a execução dos serviços de recuperação da Ponte Hercílio Luz, conforme PJ-56/2016, e fiscalizar os serviços de supervisão". O primeiro nome é o do engenheiro Wenceslau Jeronimo Diotallevy. | "Wanderley Teodoro Agostini Presidente" | DOE-SC nº 20.278, 14/04/2016, página 11: https://portal.doe.sea.sc.gov.br/repositorio/2016/20160414/Jornal/1401.pdf |
| Contrato PJ-0170/2006 (supervisão, Consórcio Prosul-Concremat) | Assinado em 25/08/2006, segundo o TCE-SC; valor inicial R$ 9.811.282,66 | **Signatário não localizado nesta coleta** (o DOE de agosto de 2006 não foi aberto) | Relatório TCE-SC DLC 462/2012, item 2.7 |

### 2.3 Cargo de cada pessoa na data, segundo documentos oficiais

| Pessoa | Cargo registrado | Quando | Documento oficial |
|---|---|---|---|
| Romualdo Theophanes de França Júnior | "Presidente do Departamento Estadual de Infra-estrutura - DEINFRA" | Decisão TCE-SC nº 4067/2007, de 12/12/2007 (sobre o edital 044/07), transcrita no Relatório DLC 462/2012; e signatário do PJ-264/2008 em 27/11/2008 | Relatório DLC 462/2012, item 2.5; DOE-SC nº 18.501 |
| Paulo Roberto Meller | "Diretor Presidente do Deinfra" e "Responsável" no processo RLA 12/00285490 | Relatório de 02/08/2012 | Relatório DLC 462/2012, cabeçalho e item 3.2 |
| Wanderley Teodoro Agostini | Signatário "pelo DEINFRA" e "Presidente" | aparece no cargo em atos datados de 25/02/2015 a 05/04/2016 | DOE-SC nº 20.010, nº 20.260, nº 20.278 e nº 20.283 |
| Paulo Ney Almeida | Signatário "pelo consórcio"; na Receita, administrador do Consórcio Florianópolis Monumento e sócio-administrador da Castor Construtora e Incorporadora Ltda | 27/11/2008 | DOE-SC nº 18.501; quadro de sócios da Receita (base 2026-09, via espelho) |
| José Luís Batista Silva; João Pedro Carrilho Calado (Antunes Lopes) | Signatários "pela contratada" (EMPA em 2015; Teixeira Duarte em 2016) | 2015 e 2016 | DOE-SC nº 20.010 e nº 20.283 |

**Não encontrado nesta coleta:** ato de nomeação de cada presidente do DEINFRA com datas exatas de início e fim (seriam decretos publicados no DOE); por isso a tabela diz só as datas em que cada um aparece no cargo em documento oficial. Também não foi identificado, em documento oficial lido, quem era o secretário de Estado da Infraestrutura em cada data.

### 2.4 Por que o site não deve usar o campo "fiscal" do registro de contratos como lista de servidores

Reforço da seção 1.4: o campo `NMFISCAL` do PJ-00056/2016 e do PJ-00009/2019 traz "JOÃO PEDRO CARRILHO CALADO ANTUNES LOPES", o mesmo nome que assina **pela contratada** no extrato do DOE. Já a Portaria DEINFRA nº 103/2016, que é o ato oficial de designação dos fiscais do Estado para o PJ-56/2016, traz outra lista (sete servidores com matrícula). Para dizer quem fiscalizava pelo Estado, a fonte é a portaria de designação, não o campo do sistema.

## 3. Governadores no período (2006 a 2019)

Fonte: Assembleia Legislativa de SC (Alesc), "Memória Política de Santa Catarina", bloco "Mandatos" e texto de cada biografia, acessadas em 2026-09-29. Partido omitido de propósito (regra 2 do projeto: o site não cita partidos).

| Quem | Início | Fim | Condição | Fonte (Alesc) |
|---|---|---|---|---|
| Luiz Henrique da Silveira | 2003-01-01 | 2006-04-09 | titular, 1º mandato | https://memoriapolitica.alesc.sc.gov.br/biografia/638-Luiz_Henrique_da_Silveira |
| Eduardo Pinho Moreira | 2006-04-09 | 2006-07-06 | interino (vice-governador) | https://memoriapolitica.alesc.sc.gov.br/biografia/1158-Eduardo_Pinho_Moreira |
| Pedro Manoel Abreu | 2006-07-07 | 2006-07-14 | temporário (presidente do Tribunal de Justiça), segundo o texto da biografia de Eduardo Pinho Moreira | mesma página acima |
| Eduardo Pinho Moreira | 2006 (depois de 14/07) | 2006-12-31 | efetivado; texto: "tornou-se efetivo na função até 31 de dezembro de 2006" | mesma página acima |
| Luiz Henrique da Silveira | 2007-01-01 | 2010-03-25 | titular, 2º mandato; "Deixou o cargo de Governador, em 25 de março de 2010, para disputar o de Senador" | biografia 638 |
| Leonel Pavan | 2010-03-25 | 2010-12-31 | vice-governador que assumiu | https://memoriapolitica.alesc.sc.gov.br/biografia/960-Leonel_Pavan |
| Raimundo Colombo | 2011 (ver nota) | 2018-04-05 | titular, dois mandatos (2011 a 2014 e 2015 a 2018); "Renunciou ao cargo de Governador em 5 de abril de 2018" | https://memoriapolitica.alesc.sc.gov.br/biografia/480-Raimundo_Colombo |
| Eduardo Pinho Moreira | 2018-04-06 (posse como titular) | 2018-12-31 (a biografia registra "01/01/2019") | titular até o fim do mandato | biografia 1158 e Agência AL, 06/04/2018: https://agenciaal.alesc.sc.gov.br/index.php/noticia_single/eduardo-pinho-moreira-toma-posse-como-governador-titular-em-solenidade-na-a |
| Carlos Moisés da Silva | 2019-01-01 | 2023-01-01 (registro da biografia) | titular; "Tomou posse em 1º de janeiro de 2019" | https://memoriapolitica.alesc.sc.gov.br/biografia/1308-Carlos_Moises |

Notas:
- **Raimundo Colombo, data de início:** a biografia da Alesc registra só os anos ("2011 - 2014" e "2015 - 2018"). A data de 1º de janeiro de 2011 é a data de posse fixada pela Constituição Federal, art. 28 (redação vigente à época), não um registro lido nesta coleta.
- **Início de 2018:** a nota da Agência AL de 06/04/2018 chama Eduardo Pinho Moreira de "governador em exercício" antes da posse como titular, e a biografia dele cita uma reportagem de 16/02/2018 intitulada "Eduardo Pinho Moreira é empossado como governador". Ou seja, ele já exercia o cargo antes de 6 de abril; **a data de início desse exercício não foi confirmada em página oficial nesta coleta.**
- **Substituições curtas** (viagens e licenças, em que o vice, o presidente da Alesc ou o do TJSC assumem por dias) não estão listadas; a biografia de Luiz Henrique cita várias. A tabela cobre quem exercia o cargo de forma continuada.
- **Governador na data de cada contrato principal** (cruzamento calculado): PJ-00170/2006 (assinado em 2006-08-25) cai no período de Eduardo Pinho Moreira efetivado; PJ-00264/2008 (2008-11-27), no 2º mandato de Luiz Henrique da Silveira; PJ-00012/2015 (2015-02-25) e PJ-00056/2016 (2016-03-10), no 2º mandato de Raimundo Colombo; os contratos de 2019, no mandato de Carlos Moisés da Silva. É só um cruzamento de datas; não significa que o governador assinou o contrato: nos documentos lidos, quem assina pelo Estado é o dirigente do órgão (seção 2).

## 4. Pagamentos efetivamente feitos a cada empresa

### 4.1 O que existe

| Base | Cobertura | Serve para a ponte? |
|---|---|---|
| Dados abertos (dados.sc.gov.br): "Empenhos" | 2021 a 2026 (arquivos anuais) | Não cobre a obra (2006 a 2021) |
| Dados abertos: "Pagamentos" | só março de 2022 | Não |
| Dados abertos: "Fornecedores" | só 2022 | Não |
| **Portal da Transparência do Poder Executivo de SC, consulta "Fornecedores"** (fonte SIGEF, gestor Secretaria de Estado da Fazenda) | **de 2011 em diante** (2008, 2009 e 2010 voltam vazios; 2011 tem dados) | **Sim, a partir de 2011**, por credor, ano e unidade gestora |

A consulta "Fornecedores" do Portal (https://www.transparencia.sc.gov.br/fornecedores) é servida por uma API pública, sem login, que o próprio site usa: `https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/pgtocredor` (credor localizado por CNPJ em `.../api/busca/documento`). O script `pipelines/ponte/payments.py` refaz todas as consultas. Parâmetro `tipopagamentocredorfiltro=1`: é o valor que a página do Portal envia por padrão. Situação da carga no próprio Portal (`.../api/processo-carga`): base "Carga fato pagto fornecedores" atualizada em 2026-09-29, até 09/2026.

Campos, segundo o dicionário de dados "Fornecedores" v1.0 (https://dados.sc.gov.br/dataset/6b72a588-3f47-4af0-baa9-f92d8bb0928e/resource/339d73d6-4b98-4fdd-8b94-3e1ee7d70030/download/dicionario-de-dados-fornecedores-v1.0.xlsx): `vlbruto` "Valor bruto recebido pelo credor"; `vlretido` "Valor retido"; `vlestorno` "Valor estornado" ("Valor devolvido"). O Portal descreve o total como "o valor pago a fornecedores, incluindo retenções". O dicionário não diz se `vlbruto` já desconta os estornos; por isso os dois aparecem separados abaixo, sem somar um no outro.

**Controles feitos antes de confiar nos números:** um id de credor inexistente (999999999) devolve vazio; uma unidade gestora inexistente (999999) devolve vazio; a Teixeira Duarte em 2015, antes do contrato, devolve vazio; e o filtro por unidade gestora DEINFRA (530025) devolve o mesmo total que "todos os órgãos" nos anos em que a empresa só tinha contrato com o DEINFRA.

### 4.2 Resultado por empresa (consulta em 2026-09-29)

| Empresa (credor no portal) | CNPJ | Id do credor | Anos com pagamento | Valor bruto pago, todos os órgãos (soma calculada) | Valor estornado (soma calculada) | Contratos da empresa no registro de contratos |
|---|---|---|---|---|---|---|
| TEIXEIRA DUARTE - ENGENHARIA E CONSTRUCOES  S A | 24447770000145 | 466549 | 2016 a 2020 | R$ 373.694.994,99 | R$ -8.738.183,49 | PJ-00056/2016 e PJ-00009/2019 (ponte); CT-00016/2020 (reforço das pontes Colombo Salles e Pedro Ivo, R$ 6.984.175,68 atual) |
| EMPA S A SERVICOS DE ENGENHARIA | 17159856000107 | 424866 | 2015 a 2016 | R$ 24.025.575,59 | R$ 0,00 | só PJ-00012/2015 e PJ-00143/2015 (ponte) |
| CONSORCIO FLORIANOPOLIS MONUMENTO | 10769406000197 | 174769 | 2011 a 2014 | R$ 33.887.355,69 | R$ -17.772,75 | só PJ-00264/2008 (ponte) |
| RMG - ENGENHARIA S C LTDA | 38738381000183 | 423600 | 2015 a 2021 | R$ 16.221.892,76 | R$ -37.903,70 | PJ-00204/2014, PJ-00093/2016, CT-00006/2019 e DL-00001/2618-2019 (ponte); CT-00059/2019 (pontes Colombo Salles e Pedro Ivo) |
| PROSUL PROJETOS SUPERVISAO E PLANEJAMENTO LTDA | 80996861000100 | 951 | 2011 a 2026 | R$ 250.227.173,08 | R$ -704.338,17 | 114 contratos no registro, de vários órgãos; a ponte é só um deles |
| CONCREMAT ENGENHARIA E TECNOLOGIA S A | 33146648000391 | 20913 | 2011 a 2024 | R$ 6.104.816,00 | R$ -13.678,30 | PJ-00170/2006 (ponte) e PJ-00165/2014 (rodovia SC-290); outros contratos podem estar em outros CNPJ da empresa |
| FARES   ASSOCIADOS ENGENHARIA LTDA | 52573623000157 | 473472 | 2016 a 2023 | R$ 1.039.387,85 | R$ 0,00 | só PJ-00001/2016/FARES no registro; não há outro contrato deste CNPJ no registro que explique os pagamentos de 2021 a 2023 (SIE) |
| GEOARQUEOLOGIA PESQUISA CIENTIFICA LTDA | 01956161000116 | 583240 | 2019 a 2020 | R$ 95.862,85 | R$ -400,07 | só PJ-00060/2019 (ponte) |
| SDF ENGENHARIA EIRELI | 24055348000144 | 592803 | 2020 a 2020 | R$ 35.000,00 | R$ 0,00 | só CT-00026/2019 (ponte) |

Por ano, para as quatro empresas com os contratos de restauração mais relevantes (os totais da Teixeira Duarte e da RMG incluem outros contratos, ver tabela acima):

| Empresa | Ano | Bruto pago (todos os órgãos) | Bruto pago, UG DEINFRA (530025) | Bruto pago, UG SIE (530001) |
|---|---|---|---|---|
| TEIXEIRA DUARTE - ENGENHARIA E CONSTRUCOES  S A | 2016 | R$ 61.363.201,36 | R$ 61.363.201,36 | R$ 0,00 |
| TEIXEIRA DUARTE - ENGENHARIA E CONSTRUCOES  S A | 2017 | R$ 93.659.794,67 | R$ 93.659.794,67 | R$ 0,00 |
| TEIXEIRA DUARTE - ENGENHARIA E CONSTRUCOES  S A | 2018 | R$ 86.470.181,26 | R$ 86.470.181,26 | R$ 0,00 |
| TEIXEIRA DUARTE - ENGENHARIA E CONSTRUCOES  S A | 2019 | R$ 89.019.342,39 | R$ 71.870.775,94 | R$ 17.148.566,45 |
| TEIXEIRA DUARTE - ENGENHARIA E CONSTRUCOES  S A | 2020 | R$ 43.182.475,31 | R$ 0,00 | R$ 43.182.475,31 |
| EMPA S A SERVICOS DE ENGENHARIA | 2015 | R$ 18.987.728,69 | R$ 18.987.728,69 | R$ 0,00 |
| EMPA S A SERVICOS DE ENGENHARIA | 2016 | R$ 5.037.846,90 | R$ 5.037.846,90 | R$ 0,00 |
| CONSORCIO FLORIANOPOLIS MONUMENTO | 2011 | R$ 6.520.883,68 | R$ 6.520.883,68 | R$ 0,00 |
| CONSORCIO FLORIANOPOLIS MONUMENTO | 2012 | R$ 5.299.956,75 | R$ 5.299.956,75 | R$ 0,00 |
| CONSORCIO FLORIANOPOLIS MONUMENTO | 2013 | R$ 16.878.580,18 | R$ 16.878.580,18 | R$ 0,00 |
| CONSORCIO FLORIANOPOLIS MONUMENTO | 2014 | R$ 5.187.935,08 | R$ 5.187.935,08 | R$ 0,00 |
| RMG - ENGENHARIA S C LTDA | 2015 | R$ 1.951.820,02 | R$ 1.951.820,02 | R$ 0,00 |
| RMG - ENGENHARIA S C LTDA | 2016 | R$ 2.373.842,62 | R$ 2.373.842,62 | R$ 0,00 |
| RMG - ENGENHARIA S C LTDA | 2017 | R$ 4.185.844,16 | R$ 4.185.844,16 | R$ 0,00 |
| RMG - ENGENHARIA S C LTDA | 2018 | R$ 2.798.194,28 | R$ 2.798.194,28 | R$ 0,00 |
| RMG - ENGENHARIA S C LTDA | 2019 | R$ 3.542.863,87 | R$ 1.629.937,45 | R$ 1.912.926,42 |
| RMG - ENGENHARIA S C LTDA | 2020 | R$ 1.269.225,34 | R$ 0,00 | R$ 1.269.225,34 |
| RMG - ENGENHARIA S C LTDA | 2021 | R$ 100.102,47 | R$ 0,00 | R$ 100.102,47 |

### 4.3 Como ler (limites)

1. **É pagamento ao credor, não ao contrato.** A consulta não separa por contrato. Onde a empresa só tem contratos da ponte no registro (EMPA, Consórcio Florianópolis Monumento, Geoarqueologia, SDF), o valor pode ser lido como pago por esses contratos. Onde tem outros contratos (Teixeira Duarte, RMG, Prosul, Concremat, Fares), o valor inclui os outros, listados na última coluna da tabela 4.2. **Para a Prosul, o total não diz nada sobre a ponte.**
2. **Antes de 2011 não há dado de pagamento aberto.** Para o Consórcio Florianópolis Monumento (contrato de 2008), o Portal mostra só 2011 a 2014. Há um número oficial do período anterior: o TCE-SC, citando extrato do SICOP "atualizado em julho de 2012", registra que o último pagamento ao consórcio "ocorreu em maio do corrente ano, referente aos meses de janeiro a março de 2012, acumulando R$ 38.921.239,05 e medições até junho de 2012, com saldo a pagar de R$ 1.595.516,86" (Relatório DLC 462/2012, item 2.6). Os dois números não se somam: um é acumulado desde 2008 até maio de 2012, o outro é o fluxo anual de 2011 a 2014.
3. **Supervisão de 2006 (Prosul e Concremat):** sem dado separável. A Concremat do registro é a filial 0003; pagamentos a outros CNPJ da mesma empresa não entram.
4. **Valores nominais**, sem correção.
5. **DL-00001/2618-2019:** o registro de contratos traz um registro da RMG, R$ 1.451.313,01, objeto "Para pagamento realizado na supervisão da PHL e que não estava no escopo do Contrato PJ 093/2016" (bem público "INDENIZAÇÃO DE SERVIÇOS"). Ele não entrou nos 13 porque o texto diz "PHL" e não "Ponte Hercílio". O TCE-SC o cita na Decisão 928/2025 (seção 5.5). Recomendação: tratar como 14º registro ligado à restauração, com essa nota.

## 5. Achados oficiais

Resumo da situação jurídica de cada achado (detalhe e citações abaixo):

| # | Órgão e processo | O que é | Situação na última informação oficial lida |
|---|---|---|---|
| 5.1 | TCE-SC, ELC 07/00582703 | Análise do edital 044/07 | Encerrado: irregularidades apontadas em 2007 (Decisão 4067/2007); edital considerado em conformidade depois das correções (Decisão 0594/2008) |
| 5.2 | TCE-SC, RLA 12/00285490 | Auditoria dos contratos PJ-264/2008 e PJ-170/2006 | **Julgado com multas** (Acórdão 0788/2015); **recursos julgados** em 01/11/2017 (Acórdãos 0632 a 0636/2017): multas mantidas integralmente para duas pessoas, reduzidas para duas, canceladas para uma (falecida). Cobrança: não verificada |
| 5.3 | TCE-SC, REP 14/00346689 | Seguro de riscos de engenharia do PJ-264/2008 | **Julgado procedente com multa** (Acórdão 0585/2017). Recurso: não verificado |
| 5.4 | Alesc, CPI (Ato 0030-DL/2019) | Investigação parlamentar | **Encerrada**; relatório final aprovado em 18/12/2019 com **encaminhamento** "para apurar possíveis ilicitudes" (não é acusação nem condenação) |
| 5.5 | TCE-SC, REP 15/00524643 | Representação do Ministério Público de Contas sobre contratos de 1980 em diante | **Arquivado** (Decisão 928/2025): **prescrição reconhecida** para a maior parte dos contratos, sem julgamento de mérito sobre eles; improcedente quanto ao PJ 046/90; **abertura de dois processos novos** (PJ 056/2016 e CT 006/2019), cujo número e andamento não foram encontrados |
| 5.6 | MPSC, ação civil pública de improbidade (17/12/2018) | Pedido de ressarcimento de R$ 233.675.518,92 | **Ajuizada**; última informação oficial lida (18/12/2018): "sob análise do Juiz". **Resultado judicial não encontrado** |
| 5.7 | MPSC, inquérito civil (2012) | Acompanhar o andamento da obra | Instaurado em 2012; desfecho não encontrado |

**"Superfaturamento" ou "sobrepreço":** nenhum dos documentos oficiais lidos nesta coleta usa esses termos (busca com controle positivo, ver diário). Isso confirma e estende a seção 4.4 da pesquisa de 2026-09-25.

### 5.1 TCE-SC: edital da restauração (2007 e 2008)

Fonte: transcrição no Relatório DLC 462/2012, item 2.5 (http://consulta.tce.sc.gov.br/relatoriosdecisao/relatoriotecnico/3728501.PDF). O edital de Concorrência 044/07 foi analisado no processo ELC 07/00582703. Pela Decisão 4067/2007 (12/12/2007), o Pleno arguiu "ilegalidades" no edital e determinou "cautelarmente" a "sustação do procedimento licitatório", endereçada a "Romualdo Theophanes de França Júnior - Presidente do Departamento Estadual de Infra-estrutura - DEINFRA". Segundo o mesmo relatório, "Após justificativas e correções, a área técnica alterou sua proposta de Decisão", e a Decisão definitiva 0594/2008 (19/03/2008) decidiu "Conhecer do Edital de Concorrência Pública n. 044/2007 [...] considerando seus termos em consonância com as determinações do art. 40 da Lei Federal n. 8.666/93", com determinações ao DEINFRA (entre elas, retirar da fonte de recursos "aqueles oriundos da arrecadação com multas de trânsito" e incluir "ação ou subação específica para a restauração e reabilitação da Ponte Hercílio Luz" no orçamento de 2009). Sobre a licitação: dois consórcios foram habilitados; o concorrente pediu retirada, e "restando um único consórcio participante, a Unidade homologou o resultado da licitação em 18/11/2008". **Situação: encerrado.** As decisões 4067/2007 e 0594/2008 foram lidas na transcrição do Relatório DLC 462/2012, não no original.

### 5.2 TCE-SC: auditoria RLA 12/00285490 (contratos PJ-264/2008 e PJ-170/2006)

**Relatório técnico** DLC 462/2012 (02/08/2012), relatório preliminar que propôs audiência do responsável: http://consulta.tce.sc.gov.br/relatoriosdecisao/relatoriotecnico/3728501.PDF

**Acórdão 0788/2015**, sessão de 04/11/2015, publicado no Diário Oficial Eletrônico do TCE-SC (DOTC-e) nº 1845, 04/12/2015, páginas 2 e 3: https://consulta.tce.sc.gov.br/Diario/dotc-e2015-12-04.pdf . "Responsáveis: Paulo Roberto Meller, Romualdo Theophanes de França Júnior, Nelson Luiz Giorno Picanço, Wenceslau Jerônimo Diotallévy e Lyana Carrilho Cardoso". Multas aplicadas (fundamento: art. 70, II, da Lei Complementar estadual 202/2000):

| Pessoa e cargo (texto do acórdão) | Itens | Motivo (texto do acórdão, resumido só na extensão) | Valor por item |
|---|---|---|---|
| Paulo Roberto Meller, "ex-Diretor-Presidente do Departamento Estadual de Infraestrutura - DEINFRA" | 6.2.1.1 a 6.2.1.6 | "autorizar que o Contrato n. PJ-170/2006 (supervisão da obra) sofresse acréscimo de valor que ultrapassa o limite de 25% do inicial contratado"; "permitir que o Contrato n. PJ-264/2008 (restauração da ponte) sofresse acréscimo de 50,29% e supressão de 44,78% do seu valor por meio de Termos Aditivos"; "autorizar alteração contratual sem as devidas justificativas no Contrato n. PJ-170/2006"; "deixar de aplicar a multa prevista na Cláusula Sexta do Contrato n. PJ-264/2008 por atraso na execução dos serviços"; "não exigir a manutenção das condições de habilitação e qualificação técnica"; "permitir que praticamente todos os serviços executados até o momento fossem subcontratados, incluindo fundações e estrutura metálica" | R$ 5.000,00; 5.000,00; 1.200,00; 5.000,00; 3.000,00; 5.000,00 |
| Romualdo Theophanes de França Júnior, "ex-Diretor-Presidente do DEINFRA" | 6.2.2.1 a 6.2.2.6 | os mesmos itens de acréscimo (PJ-170/2006 e PJ-264/2008), alteração sem justificativa, habilitação e subcontratação, mais "deixar de promover nova licitação em função da alteração do objeto contratado na obra de restauração da Ponte Hercílio Luz" | R$ 5.000,00; 5.000,00; 5.000,00; 1.200,00; 3.000,00; 5.000,00 |
| Nelson Luiz Giorno Picanço, "Consultor Executivo do DEINFRA" | 6.2.3.1 a 6.2.3.3 | acréscimo acima de 25% no PJ-170/2006; acréscimo e supressão no PJ-264/2008; alteração sem justificativa no PJ-170/2006 | R$ 5.000,00; 5.000,00; 1.200,00 |
| Wenceslau Jerônimo Diotallévy, "Fiscal das Obras de restauração da Ponte Hercílio Luz" | 6.2.4.1 a 6.2.4.3 | acréscimo e diminuição no PJ-264/2008; habilitação; subcontratação | R$ 5.000,00; 3.000,00; 5.000,00 |
| Lyana Carrilho Cardoso, "Assistente Jurídica do DEINFRA" | 6.2.5 | "elaborar pareceres jurídicos a aditivos ao Contrato n. PJ-170/2006 sem justificativa idônea para legitimá-los e usando como base posicionamento inexistente do TCE/SC" | R$ 5.000,00 |

O acórdão também determinou ao DEINFRA que iniciasse "processo administrativo próprio [...] no sentido de aplicar as devidas sanções ao Consórcio contratado, a partir do termo de rescisão e Parecer Projur n. 0373/2014" (item 6.3.1). O resultado desse processo administrativo não foi encontrado.

**Recursos** (Recurso de Reexame), julgados na sessão de 01/11/2017, publicados no DOTC-e nº 2313, 01/12/2017, páginas 4 a 6: https://consulta.tce.sc.gov.br/Diario/dotc-e2017-12-01.pdf

| Recurso | Acórdão | Recorrente | Resultado (texto) | Multas que ficaram (soma calculada) |
|---|---|---|---|---|
| REC 16/00030243 | 0632/2017 | Wenceslau Jeronimo Diotallevy | "dar-lhe provimento parcial para: 6.1.1. cancelar a multa estabelecida no subitem 6.2.4.1" | R$ 8.000,00 |
| REC 16/00030324 | 0633/2017 | Lyana Carrilho Cardoso | "negar-lhe provimento, ratificando na íntegra a deliberação recorrida" | R$ 5.000,00 |
| REC 16/00030405 | 0634/2017 | Romualdo Theophanes de França Júnior | "negar-lhe provimento, ratificando na íntegra a deliberação recorrida" | R$ 24.200,00 |
| REC 16/00030596 | 0635/2017 | Espólio de Nelson Luiz Giorno Picanço | "dar-lhe provimento para: 6.1.1. tornar insubsistentes os itens 6.2.3.1, 6.2.3.2 e 6.2.3.3 [...] cancelando as multas aplicadas [...] que totalizam o montante de R$ 11.200,00" (o parecer do Ministério Público de Contas MPC/47.675/2017 registra o falecimento em 19/11/2015, antes da publicação do acórdão) | R$ 0,00 |
| REC 16/00030677 | 0636/2017 | Paulo Roberto Meller | "dar-lhe provimento parcial para: 6.1.1. cancelar a multa estabelecida no subitem 6.2.1.2" | R$ 19.200,00 |

**Situação: decisão administrativa do TCE-SC depois dos recursos.** Não foi verificado se as multas foram pagas, cobradas judicialmente ou contestadas na Justiça. Recomendação para o site: se exibir, exibir o acórdão final (2017) ao lado do original (2015), com o valor que ficou, e a frase "multa administrativa aplicada pelo Tribunal de Contas", que é o que o documento diz.

### 5.3 TCE-SC: seguro do contrato PJ-264/2008 (REP 14/00346689)

**Acórdão 0585/2017**, sessão de 04/10/2017, DOTC-e nº 2295, 06/11/2017, páginas 8 e 9: https://consulta.tce.sc.gov.br/Diario/dotc-e2017-11-06.pdf . "6.1. Julgar procedente a Representação formalizada pelo Procurador-geral do Ministério Público de Contas." Multa de R$ 1.136,52 a "Romualdo Theophanes de França Júnior - ex-Presidente do Departamento Estadual de Infraestrutura - DEINFRA", "em face da omissão no poder-dever de fiscalização em relação à apresentação do 'Seguro de Riscos de Engenharia' pelo Consórcio Florianópolis Monumento, junto ao Termo de Contrato n. PJ 264/2008". **Situação: julgado; recurso não verificado.** (O original publica o CPF do responsável; este documento não o reproduz.)

### 5.4 Alesc: CPI da Ponte Hercílio Luz (2019)

Constituída pelo "Ato da Presidência nº 0030-DL, de 21 de fevereiro de 2019, para investigar ilicitudes praticadas nas obras da Ponte Hercílio Luz em procedimentos licitatórios ocorridos desde a sua interdição até a atualidade" (Diário da Assembleia nº 7.566, 19/12/2019, ata da 31ª reunião: https://www.alesc.sc.gov.br/wp-content/uploads/diarios/7566dia.pdf).

**Relatório final aprovado** em 18/12/2019, por unanimidade, o do deputado Fernando Krelling, depois da rejeição dos relatórios dos deputados Bruno Souza e Ismael dos Santos. Fonte: Agência Alesc, 18/12/2019, "Aprovado relatório final da CPI da Ponte Hercílio Luz": https://agenciaal.alesc.sc.gov.br/index.php/noticia_single/aprovado-relatorio-final-da-cpi-da-ponte-hercilio-luz . Citações literais da nota:

- "O relatório aprovado suprime a palavra 'indiciamento' e a substitui por encaminhamento para apurar possíveis ilicitudes e o documento será encaminhado ao Ministério Público junto ao Tribunal de Contas (MPTC), Ministério Público (MP) e Tribunal de Contas do Estado (TCE)."
- "O parecer final da CPI da Ponte Hercílio Luz é composto por 1.842 páginas, sendo quase 400 referentes ao voto do relator. Foram suprimidas as páginas 1.718 e 1.719 e nele, em vez de pedir o indiciamento, o novo relator encaminhou os nomes de 20 pessoas para apuramento de possíveis ilicitudes, além da declaração de inidoneidade ou a suspensão à atuação em procedimentos licitatórios de seis empresas."
- "Entre os crimes que estão sugeridos pra serem apurados estão improbidade administrativa, falsidade ideológica, prevaricação, fraude à licitação, associação criminosa, lavagem de dinheiro, falso testemunho, entre outros."
- "para que sejam analisadas possíveis irregularidades de R$ 24,6 milhões aos cofres públicos por parte do Consórcio Florianópolis Movimento [sic], de R$ 12,2 milhões pela Usimec (referente a contrato de 1982) e de outros R$ 5,2 milhões pela contratação da Steimann, em 1993."

A nota traz duas listas, com estes títulos exatos. "Pessoas citadas no relatório final da CPI": Raul Ozório de Almeida; Telmo Fernando Mattar de Souza; Tolstói Maia Duarte; Sidney Lourenço Dal Sasso; Hubert Beck Júnior; Roberto Alexandre Zattar; Paulo Ney Almeida; Marcos Amin; Luiz Antônio Ramos; Justiniano Pedroso; Olívio Karasek Rocha; Eduardo Hamond Régua; Raimundo Colombo; Paulo Meller; Wenceslau Jerônimo Diotallévy; Wilfredo Brillinger; Celso Magalhães Carvalho; Romualdo Theophanes de França Junior; Dalmo Pickler Baesso; Ricardo Bridon Soares (20 nomes). "Empresas citadas no relatório": Construtora Roca; TEC - Técnica de Engenharia Catarinense; Prosul; Construtora Espaço Aberto; Consórcio Florianópolis Monumento; CSA Group Florida e CSA.

**Cuidados obrigatórios para o site:** (1) a nota não diz o que é atribuído a cada nome, nem o período; publicar a lista sem isso sugere uma culpa que o documento não afirma; (2) a própria CPI trocou "indiciamento" por "encaminhamento para apurar possíveis ilicitudes"; esse é o termo a usar; (3) a lista cobre fatos desde 1982, não só a restauração de 2006 a 2019; (4) um dos nomes é de ex-governador, e o site vai ao ar dias antes da eleição: a recomendação é **não exibir a lista de nomes da CPI** até ler o relatório integral (servidor da Alesc inacessível do exterior; ver diário) e poder mostrar, para cada nome, o trecho exato. **Situação: CPI encerrada; encaminhamentos a MPTC, MP e TCE.** O que o TCE fez com o encaminhamento aparece em parte na seção 5.5 (a Decisão 928/2025 cita folhas do "relatório da CPI").

Nota de leitura: as atas das 31ª e 32ª reuniões (Diário da Assembleia nº 7.566 e nº 7.588) trazem a leitura e a votação do relatório **rejeitado** (do relator original). Esse texto não é a conclusão da CPI e não deve ser usado como achado.

### 5.5 TCE-SC: representação do Ministério Público de Contas (@REP 15/00524643) e a prescrição

**Decisão 928/2025**, sessão virtual de 08/08/2025, DOTC-e nº 4145, 19/08/2025, páginas 2 e 3: https://consulta.tce.sc.gov.br/Diario/dotc-e2025-08-19.pdf . Assunto: "Representação do Ministério Público de Contas junto ao TCE/SC acerca de supostas irregularidades pertinentes aos contratos de obras, reformas, manutenção, supervisão e fiscalização referentes à Ponte Hercílio Luz". Unidade gestora: Secretaria de Estado da Infraestrutura e Mobilidade (SIE). O cabeçalho lista "Interessados" e um "Responsável" (termos processuais do TCE para quem é parte ou é chamado a se manifestar; não significam culpa).

O que o Pleno decidiu (citações):
- Item 1: "Reconhecer, de ofício, a prescrição das pretensões punitiva e ressarcitória deste Tribunal, com fundamento nos arts. 83-A, 83-B, 83-C e 83-F da Lei Complementar (estadual) n. 202/2000 (instituídos pela Lei Complementar - estadual - n. 819/2023)", em relação a uma lista de contratos que inclui, entre os 13 desta pesquisa: **PJ 170/2006, PJ 264/2008, PJ 204/2014, PJ 12/2015, PJ 143/2015, PJ 001/2016, PJ 93/2016, PJ 009/2019, CT 026/2019, PJ 060/2019**, além de DL-00001/2618-2019, contratos de 1980 a 2005 e os convênios UFSC/FEESC.
- Item 2: "a formação de autos apartados em processos específicos": "Processo 1 - RMG Engenharia: Contrato CT 006/2019 e Dispensa de Licitação DL 001/19 [...] também constantes das fs. 1746 a 1747 do relatório da CPI" e "Processo 2 - Teixeira Duarte e EMPA: Contrato PJ 056/2016, analisado no item 2.5.4. do Relatório DLC n. 177/2023 [...] também constantes das fs. 1726 a 1732 do relatório da CPI".
- Item 3: "Julgar improcedente a Representação quanto ao Contrato PJ 046/90".
- Itens 4 e 5: recomendações à SIE (plano de trabalho "baseado em matrizes de risco", avaliação de entregas antes do pagamento, entre outras) e sugestão de análise de "Auditoria Operacional" na SIE.
- Item 7: "Determinar o arquivamento dos autos."

**Situação: arquivado.** Para os contratos prescritos, o TCE-SC perdeu o poder de multar ou mandar ressarcir; **não houve julgamento de mérito** sobre eles nesse processo (prescrição não é absolvição nem condenação). Para PJ 056/2016 e CT 006/2019, o Tribunal mandou abrir processos próprios; **número e andamento não encontrados** (busca no DOTC-e de 29/08/2025 a 28/09/2026 por "Hercílio Luz", "PJ 056/2016", "CT 006/2019", "PHL" e pelos nomes das empresas: nenhuma decisão encontrada). O Relatório DLC 177/2023 e o Relatório DLC 495/2021 citados na decisão não foram lidos.

### 5.6 MPSC: ação civil pública por improbidade (2018)

Fonte: MPSC, notícia de 18/12/2018, "Ponte Hercílio Luz: MPSC requer devolução de R$ 233,67 milhões por obra não concluída": https://www.mpsc.mp.br/w/noticias/-ponte-hercilio-luz-mpsc-requer-devolucao-de-r-23367-milhoes-por-obra-nao-concluida . Ajuizada em 17/12/2018 pela Promotora de Justiça titular da 26ª Promotoria de Justiça da Capital. "A ação civil pública por atos de improbidade administrativa com pedido de ressarcimento de R$ 233.675.518,92 aos cofres públicos". A nota diz que é "contra 12 envolvidos - oito com atuação no Departamento Estadual de Infraestrutura (Deinfra) e quatro empresas" e lista, com o papel que ela mesma atribui: Romualdo Theophanes de França Júnior, "ex-presidente do Deinfra"; Paulo Roberto Meller, "ex-presidente do Deinfra"; Wenceslau Jerônico [sic] Diotallévy, "engenheiro e servidor do Deinfra"; Antônio Carlos Xavier, "engenheiro e servidor do Deinfra"; Nelson Luiz Giorno Picanço, "engenheiro ex-servidor do Deinfra"; Lyana Carrilho Cardoso, "Assistente Jurídica do Deinfra"; PROSUL - Projetos, Supervisão e Planejamento Ltda; Concremat Engenharia e Tecnologia S/A; Wilfredo Brillinger, "engenheiro"; Construtora Espaço Aberto, "compõe o consórcio Florianópolis Monumento"; CSA Group INC, "compõe o consórcio Florianópolis Monumento"; Paulo Ney Almeida, "arquiteto".

O que a ação sustenta está na nota como **alegação do MPSC**, não como fato julgado (por exemplo: aditivos que "ofenderam expressamente o limitador de 25% previsto pela Lei de Licitações" e o pedido de "indisponibilidade de bens"). A nota escreve "contrato nº 264/2006"; o contrato é o PJ-264/2008. **Situação na última informação oficial lida:** "A ação está agora sob análise do Juiz de Direito da Vara da Fazenda Pública da comarca da Capital" (18/12/2018). Número do processo, decisão liminar e sentença: **não encontrados** (o sistema do TJSC exige o número; ver diário). Recomendação para o site: exibir só "ação ajuizada pelo MPSC em 17/12/2018, sem decisão judicial localizada", sem a lista de réus, até achar o andamento.

### 5.7 MPSC: inquérito civil sobre o andamento da obra (2012)

MPSC, notícia de 14/03/2012: a 30ª Promotoria de Justiça da Capital "instaurou inquérito civil para apurar o andamento das obras de recuperação da Ponte Hercílio Luz", com o objetivo declarado de "estabelecer prazos, em um Termo de Ajustamento de Conduta": https://www.mpsc.mp.br/w/noticias/inquerito-civil-apura-andamento-de-reforma-da-ponte-hercilio-luz . **Desfecho não encontrado.**

## 6. Lacunas e recomendações para o site

### 6.1 O que não foi encontrado

| Lacuna | Onde provavelmente está | Como obter |
|---|---|---|
| Relatório final integral da CPI (1.842 páginas) e o que cada um dos 20 nomes tem a ver com o quê | `file.alesc.sc.gov.br/documentos/legislativo/cpi_ponte_hercilio_luz/` | De um IP brasileiro, ou pedido pela Lei de Acesso à Informação à Alesc |
| Andamento e sentença da ação do MPSC (2018) | TJSC (eproc ou e-SAJ), Vara da Fazenda Pública da Capital | Pedir o número do processo ao MPSC (Ouvidoria) ou achar no Diário da Justiça |
| Número e andamento dos dois processos novos do TCE-SC (PJ 056/2016 e CT 006/2019) | Sistema de processos do TCE-SC | Pedido à Ouvidoria do TCE-SC citando a Decisão 928/2025, item 2 |
| Pagamentos antes de 2011 (Consórcio Florianópolis Monumento de 2008 a 2010; supervisão desde 2006) | SIGEF histórico | Pedido pela Lei de Acesso à Informação à Secretaria de Estado da Fazenda |
| Pagamentos separados por contrato (Teixeira Duarte, RMG) | Documentos de pagamento do Portal (empenho e ordem bancária) | Leitura adicional da API do Portal, ou pedido à Fazenda |
| Signatário do PJ-170/2006 | DOE-SC de agosto ou setembro de 2006 (Arquivo Público) | Mesmo método da seção 2 (edição por edição) |
| Datas exatas de nomeação e exoneração dos presidentes do DEINFRA e dos secretários da Infraestrutura | Decretos no DOE-SC | Busca por nome no DOE; o acervo antigo não tem busca textual |
| Data em que Eduardo Pinho Moreira começou a exercer o governo em 2018 | DOE-SC ou Diário da Assembleia de fevereiro de 2018 | Leitura das edições de fevereiro de 2018 |
| Se as multas do TCE-SC (2015 e 2017) foram pagas ou contestadas na Justiça | TCE-SC (setor de cobrança) e Procuradoria-Geral do Estado | Pedido à Ouvidoria do TCE-SC |
| Composição do Consórcio Florianópolis Monumento em 2008 vs. 2009 (duas composições diferentes nas fontes) | Termo aditivo de 19/06/2009 ("alterou o CNPJ do Consórcio") | Pedido do aditivo ao órgão (hoje SIE) |

### 6.2 Recomendações de uso (regras legais e éticas do projeto)

1. **Pode exibir com segurança** (papel oficial e fonte primária): os 13 contratos (seção 1) com valor original, valor atual e situação; as empresas e CNPJ; o órgão contratante; quem assinou cada contrato pelo DEINFRA e pela contratada (seção 2.1); os governadores do período (seção 3), sempre com a nota de que o governador não assinou os contratos; e os pagamentos por credor, com os limites da seção 4.3.
2. **Pode exibir com contexto completo:** as decisões do TCE-SC de 2015 e 2017 (seções 5.2 e 5.3), mostrando o acórdão final depois do recurso, o valor que ficou e a frase "multa administrativa aplicada pelo Tribunal de Contas"; e a Decisão 928/2025 (seção 5.5), com a explicação de que prescrição não é julgamento de mérito.
3. **Não exibir por enquanto:** a lista de 20 nomes da CPI e a lista de réus da ação do MPSC. Os documentos oficiais lidos não ligam cada nome a um fato, e a ação não tem decisão localizada. Exibir nomes sem isso, a dias da eleição, sugere culpa que nenhum órgão declarou.
4. **Não usar** o campo "fiscal do contrato" do registro como lista de servidores (seções 1.4 e 2.4), nem a leitura do relatório rejeitado nas atas da CPI (seção 5.4).
5. **Termos:** usar só os termos dos órgãos ("irregularidades", "multa", "possíveis ilicitudes", "encaminhamento", "prescrição"). "Superfaturamento" e "sobrepreço" não aparecem em nenhum documento oficial lido.

## 7. Diário de transparência

Todas as consultas em 2026-09-29, a partir de um IP nos EUA. "Passos" conta requisições ou downloads até o dado.

| # | O que se buscou | Onde (URL base) | Formato | Login | Passos | Resultado e obstáculos |
|---|---|---|---|---|---|---|
| 1 | Registro de contratos e dicionário | https://dados.sc.gov.br/ (conjunto "Contratos", CGE-SC) | CSV de 73 MB e XLSX | não | 2 | ✅ imediato. O campo de quem assina pelo Estado (`NMREPUG`) está vazio nos 13 contratos; o campo "fiscal" mistura nomes do Estado e da empresa |
| 2 | Cadastro das empresas e sócios | https://arquivos.receitafederal.gov.br/ e https://dadosabertos.rfb.gov.br/ | ZIP | não | 3 | ❌ conexão recusada ou tempo esgotado a partir dos EUA. Usados os espelhos de código aberto minhareceita.org (base 2026-09) e BrasilAPI, que republicam a base aberta da Receita: ✅ |
| 3 | Extratos de contrato de 2015 e 2016 | https://portal.doe.sea.sc.gov.br/ | PDF (edições de até 178 MB) | ⚠️ a lista de edições exige login (HTTP 401) | 73 edições baixadas | ✅ com esforço. O repositório de PDFs é público, mas: (a) o certificado TLS do servidor está incompleto (falta a cadeia intermediária; foi preciso desligar a verificação para baixar); (b) o endereço usa um número interno, diferente do número da edição, achado por tentativa; (c) não há busca textual aberta. O extrato do contrato de R$ 262,9 milhões saiu 46 dias depois da assinatura, sem a palavra "Hercílio" no título |
| 4 | Extrato de contrato de 2008 | https://acervo.arquivopublico.sc.gov.br/ (edições do DOE até 2011) | PDF (edições de 44 a 70 MB) | não | 13 edições, com várias repetições | ✅ com esforço. Erros HTTP 502 intermitentes; sem busca textual dentro das edições; foi preciso adivinhar o endereço de cada edição (número e data) |
| 5 | Governadores | https://memoriapolitica.alesc.sc.gov.br/ | HTML | não | 6 | ✅. A galeria depende de JavaScript; as biografias abrem direto. Uma biografia tem inconsistência interna (datas de 2018) |
| 6 | Relatório final da CPI | http://file.alesc.sc.gov.br/documentos/legislativo/cpi_ponte_hercilio_luz/ | PDF | não se aplica | 3 | ❌ sem resposta do exterior (de novo, como em 2026-09-25); o Internet Archive não tem cópia (índice vazio; a API de disponibilidade respondeu 429) |
| 7 | Atas da CPI | https://www.alesc.sc.gov.br/wp-content/uploads/diarios/ | PDF | não | 101 edições | ✅ as atas das 31ª e 32ª reuniões (relatório rejeitado). A ata da 33ª reunião (a da aprovação) não foi achada nas edições até julho de 2020 |
| 8 | Notas oficiais da CPI e da posse de 2018 | https://agenciaal.alesc.sc.gov.br/ | HTML | não | 3 | ✅ |
| 9 | Relatórios e pareceres do TCE-SC | https://consulta.tce.sc.gov.br/RelatoriosDecisao/ | PDF e HTML | não | 8 | ✅ quando se tem o endereço exato (achado por busca na web). A consulta pública de processo por número não foi encontrada (endereços testados deram 404) |
| 10 | Acórdãos do TCE-SC | https://consulta.tce.sc.gov.br/Diario/dotc-eAAAA-MM-DD.pdf | PDF | não | 377 edições lidas | ✅ o Diário Oficial Eletrônico do TCE tem endereço previsível por data; foi o caminho para achar os acórdãos de 2015, 2017 e 2025 |
| 11 | Pagamentos por empresa | https://www.transparencia.sc.gov.br/ | aplicativo JavaScript sobre API | não | cerca de 460 consultas | ✅ com esforço: a API não é documentada e foi achada lendo o código da página. Cobre de 2011 em diante; não separa por contrato |
| 12 | Pagamentos em dados abertos | https://dados.sc.gov.br/ (Empenhos, Pagamentos, Fornecedores) | CSV e JSON | não | 3 | ❌ para a obra: empenhos só de 2021 em diante, pagamentos só de março de 2022, fornecedores só de 2022 |
| 13 | Ação do MPSC | https://www.mpsc.mp.br/ | HTML | não | 3 | ✅ a notícia de 2018. A íntegra da ação está embutida pelo SlideShare (serviço privado), não em servidor do MPSC; o número do processo não aparece |
| 14 | Andamento judicial | TJSC | não se aplica | não | 0 | ❌ não consultado: a consulta pública exige o número do processo, que não foi encontrado |
| 15 | Texto do art. 24, XV, da Lei 8.666/93 | https://www.planalto.gov.br/ | HTML | não | 1 | ❌ tempo esgotado a partir dos EUA; por isso o texto da lei não é citado aqui |
| 16 | Buscas na web para localizar documentos | buscador | não se aplica | não | 17 buscas | Usadas só para achar endereços; nenhum número deste documento vem de notícia. Duas notícias (Tudo Aqui SC, 20/08/2025; Upiara) só serviram de pista para achar a Decisão 928/2025 no DOTC-e |

**Em resumo:** tudo o que foi pedido existe em fonte oficial, menos o relatório integral da CPI e o andamento da ação judicial. Mas quase nada estava "à mão": o signatário de cada contrato exigiu abrir edição por edição do Diário Oficial (sem busca textual, com certificado quebrado, lista de edições atrás de login e acervo antigo com erros 502); os acórdãos do TCE-SC só apareceram lendo o Diário do Tribunal dia a dia; os pagamentos só saíram lendo o código da página do Portal da Transparência, e mesmo assim só de 2011 em diante e sem separar por contrato. De 16 frentes, 10 deram o dado (5 delas só com esforço técnico), 1 deu dado parcial (atas da CPI) e 5 falharam. De um IP brasileiro, provavelmente abririam o servidor da CPI, a Receita e o Planalto; os outros obstáculos continuariam.
