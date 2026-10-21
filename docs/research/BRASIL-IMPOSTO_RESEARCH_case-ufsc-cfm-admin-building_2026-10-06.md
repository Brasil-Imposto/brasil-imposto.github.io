# Caso: prédio abandonado na UFSC (campus Trindade, Florianópolis)

> **English summary.** Research for a new case: a federal building at UFSC (Trindade campus) that was started and never finished.
> Every fact below is read on an official primary source (UFSC, TCU, CGU, Portal da Transparência, DOU, Obrasgov), with the quote.
> Status: in progress (written incrementally; sections fill as facts are confirmed).

Pesquisa feita em 2026-10-06. Regras: só fonte oficial primária, com citação; página que não abriu fica como "não confirmado".
Matérias de imprensa servem só de pista para achar o documento oficial.

## 1. Identificação do prédio (candidatos)

Busca inicial no Obrasgov.br (API pública `api.obrasgov.gestao.gov.br/obrasgov/api/projeto-investimento?uf=SC&situacao=...`,
lida em 2026-10-06): nenhum projeto da UFSC com situação "Paralisada"; cinco com situação "Inacabada", três deles no campus
Trindade (Campus Reitor João David Ferreira Lima):

| idUnico | Nome no Obrasgov | Situação desde | Valor previsto (federal) |
|---|---|---|---|
| 59825.42-35 | Construção do Bloco Administrativo e Instalação de Elevador no Bloco 29 da QMC do CFM | 2015-06-01 | R$ 7.077.758,10 |
| 59844.42-03 | Retomada do Bloco Administrativo do CFM | 2023-05-23 | R$ 6.751.904,72 |
| 51935.42-18 | Etapa II do Prédio da Engenharia de Superfície da EMC do CTC | 2022-02-17 | R$ 3.270.950,30 |
| 59792.42-49 | Etapa II do CTS-03 (campus Araranguá, fora de Florianópolis) | 2023-10-19 | R$ 3.944.442,25 |
| 19950.42-63 | CPAAV (campus Curitibanos, fora de Florianópolis) | 2025-03-13 | R$ 8.699.296,23 |

Descrição do Bloco Administrativo do CFM no Obrasgov (as duas fichas): "construção de edifício de 05 (cinco) pavimentos com
subsolo técnico, cobertura e área técnica, totalizando área aproximada de 3.441,88 m2", com auditório, biblioteca, lanchonete,
secretarias de graduação e pós-graduação, salas de tutoria e salas administrativas. Endereço: "Campus Reitor Prof. João David
Ferreira Lima - Florianópolis/SC".


## 2. Fatos confirmados

### 2.1 Bloco Administrativo do CFM: primeira paralisação e licitação da retomada (2019)

- Notícia oficial da UFSC, 11/12/2019, "Economia gerada por licitação viabiliza retomada de obra na UFSC"
  (https://noticias.ufsc.br/2019/12/economia-gerada-por-licitacao-viabiliza-retomada-de-obra-na-ufsc/):
  "O certame licitatório RDC nº 007/2019 foi homologado pelo Departamento de Licitações (DPL) da UFSC, no dia 27 de novembro de
  2019, e teve como foco a retomada da obra de uma edificação do Centro de Ciências Físicas e Matemáticas (CFM) com área de
  3.441,88m²." ... "A obra para o CFM estava paralisada desde junho de 2015 e era orçada em R$ 8.284.545,67." ... "fora auferido
  um desconto de 18,50% em relação ao valor estimado para esta contratação, produzindo uma economicidade de R$ 1.532.640,95".
  Conta desta pesquisa: 8.284.545,67 menos 1.532.640,95 = 6.751.904,72, igual ao valor previsto da ficha 59844.42-03 do Obrasgov.
- Ata nº 16 do Conselho da Unidade do CFM, 21/11/2019 (https://sitecfm.paginas.ufsc.br/files/2020/09/ATA_16_2019.pdf), relato do
  Secretário de Obras, Manutenção e Ambiente (SEOMA), Paulo Roberto Pinto da Luz: "no próximo dia 26 de novembro, será aberta a
  licitação para a conclusão do prédio administrativo do CFM, com a previsão inicial para finalização no segundo semestre de
  2021" e o Secretário de Planejamento e Orçamento "irá pleitear junto ao MEC recursos financeiros para a obra, mas que não estão
  garantidos".

### 2.2 Segunda paralisação (2023) e situação depois

- Ata nº 7 do Conselho da Unidade do CFM, 10/08/2023 (https://sitecfm.paginas.ufsc.br/files/2018/06/ATA_07_2023.pdf):
  "o conselheiro Nilton Cezar Pereira perguntou sobre o andamento das obras do prédio administrativo do CFM. O Conselheiro
  Éverton Fabian Jasinski questionou sobre a retomada da obra em outubro, conforme fora noticiado. O presidente, contudo,
  repassou informação recente da Reitoria no sentido de que o recurso destinado à continuidade da obra será devolvido novamente
  ao Ministério da Educação, não havendo previsão, portanto, para retomada das obras."
- Ata nº 5 do Conselho da Unidade do CFM, 08/08/2024 (https://sitecfm.paginas.ufsc.br/files/2018/06/ATA_05_2024.pdf): o Presidente
  informou que a Universidade obteve três projetos do PAC; pediu-se à Administração Central "os documentos que embasaram o
  deferimento dos projetos da Universidade, pois, sem tirar o mérito dos pedidos aprovados, deve-se entender o motivo pelo qual
  o prédio administrativo do CFM não foi contemplado".
- Obrasgov.br, ficha 59844.42-03 ("Retomada do Bloco Administrativo do CFM"): situação "Inacabada" desde 2023-05-23; início
  previsto 2020-01-09, fim previsto 2021-07-01; data de cadastro 2025-05-20.
- Obrasgov.br, ficha 59825.42-35 (contrato original): situação "Inacabada" desde 2015-06-01; início previsto 2013-07-29, fim
  previsto 2014-11-20.


### 2.3 Obrasgov.br: execução física e motivo das paralisações (API pública, lida em 2026-10-06)

Endpoint `https://api.obrasgov.gestao.gov.br/obrasgov/api/execucao-fisica?idUnico=<id>` (os dados são preenchidos pela UFSC):

- Ficha 59825.42-35 (contrato original): `"percentual":43`, `"situacao":"Inacabada"`, `"dataSituacao":"2015-06-01"`.
  Motivos: "Rescisão contratual" e "Inadimplência da empresa executora"; indicativo: "Rescisão unilateral – Uma das partes pede
  o fim como penalidade/descumprimento". Justificativa: "A motivação e as justificativas para a rescisão unilateral estão
  presentes no MEMORANDO 012/2014/RJ (anexo) e no TERMO DE RESCISÃO UNILATERAL (anexo)." Tratativa: "Está em fase de revisão dos
  projetos para orçamentação e abertura de nova licitação prevista para o segundo semestre de 2025."
- Ficha 59844.42-03 (retomada): `"percentual":19`, `"situacao":"Inacabada"`, `"dataSituacao":"2023-05-23"`. Motivo: "Rescisão
  contratual"; indicativo "Outros". Justificativa: "A motivação e as justificativas para a rescisão amigável estão presentes no
  OFÍCIO 098/2022/DFO-SEOMA (anexo) e no TERMO DE RESCISÃO AMIGÁVEL (anexo)." Mesma tratativa (nova licitação prevista para o
  segundo semestre de 2025).
- Os anexos (memorando, ofício, termos de rescisão) não têm link público na API; não foram lidos.
- Geometria (endpoint `geometria`): polígono em torno de -27,5995 de latitude e -48,5230 de longitude, datum SIRGAS 2000, área
  executora "Departamento de Gestão de Imóveis - DGI/UFSC".
- Leitura: o percentual de 19% da retomada é o que a ficha da retomada registra; a API não diz se é sobre o prédio inteiro ou só
  sobre o contrato da retomada.

### 2.4 Contrato da retomada (Contratos.gov.br, API pública)

Fonte: `https://contratos.comprasnet.gov.br/api/contrato/inativo/ug/153163` (UG 153163, UFSC) e
`https://contratos.comprasnet.gov.br/api/contrato/69937/historico`, lidos em 2026-10-06.

- Contrato nº 00317/2019, processo 23080.075108/2019-27, RDC nº 00007/2019, categoria "Obras".
- Contratada: MENDONCA E GONCALVES CONSTRUCOES E INCORPORACOES LTDA, CNPJ 13.798.155/0001-67.
- Objeto: "FORNECIMENTO DE MATERIAL E MAO DE OBRA(EMPREITADA GLOBAL), DESTINADOS À RETOMADA DA OBRA CFM - ADMINISTRATIVO DO
  CENTRO DE CIÊNCIASFÍSICAS E MATEMÁTICAS, SITUADO NO CAMPUS REITOR JOÃO DAVID FERREIRA LIMA DA UNIVERSIDADE FEDERAL DE SANTA
  CATARINA (AREA = 3.441,88M²)."
- Assinatura 2019-12-11; publicação 2019-12-17; valor inicial e global R$ 6.751.904,72; situação "Inativo", justificativa
  "Rescindido"; vigência até 2023-05-23.
- Termo Aditivo 00001/2021 (assinado 2021-11-29): "PRORROGAR O PRAZO DE VIGÊNCIA DO CONTRATO POR MAIS 360 (TREZENTOS E SESSENTA)
  DIAS CORRIDOS, COM INÍCIO EM 30 DE NOVEMBRO DE 2021 E TÉRMINO EM 24 DE NOVEMBRO DE 2022"; valor global mantido.
- Termo Aditivo 00002/2022 (assinado 2022-11-24): "PRORROGAR O PRAZO DE VIGÊNCIA DO CONTRATO POR MAIS 180 (CENTO E OITENTA) DIAS
  CORRIDOS, COM INÍCIO EM 25 DE NOVEMBRO DE 2022 E TÉRMINO EM 23 DE MAIO DE 2023."; valor global mantido.
- Garantia: seguro garantia de R$ 337.595,24 (endpoint `garantias`).
- Fiscais do contrato (endpoint `responsaveis`): servidores da SEOMA designados pelas Portarias 0449/2019, 0054/2020 e
  0192/2020/SEOMA. São fiscais, não assinantes; ficam fora da página (mesma regra dos outros casos).

### 2.5 Situação mais recente em texto oficial (fev/2026)

- Notícia oficial da UFSC, 10/02/2026 13:16, "Administração Central da UFSC alinha prioridades para início do ano letivo com CFM,
  CFH e CCS" (https://noticias.ufsc.br/2026/02/administracao-central-da-ufsc-alinha-prioridades-para-inicio-do-ano-letivo-com-cfm-cfh-e-ccs/),
  sobre a reunião do Gabinete da Reitoria no CFM em 06/02/2026: "Destacou-se que o centro ainda ocupa áreas antigas, inclusive em
  setores previstos para demolição, e que há um prédio inacabado, paralisado há mais de dez anos, o que agrava riscos e custos e
  dificulta o funcionamento cotidiano."
- A notícia não nomeia o prédio; a única obra do CFM com situação "Inacabada" no Obrasgov é o Bloco Administrativo (fichas
  59825.42-35 e 59844.42-03), e "paralisado há mais de dez anos" bate com a primeira paralisação, em junho de 2015.
- Contexto (notícia oficial de 2023-08, "Plano de Demolição dos Modulados altera acesso e circulação em área do campus",
  https://noticias.ufsc.br/2023/08/plano-de-demolicao-dos-modulados-altera-acesso-e-circulacao-em-area-do-campus/): "Na região,
  estão situados prédios como o EFI, CCB Morfologia, CFM Oceanografia, CCE, entre outros." (os blocos modulados que o CFM ainda
  ocupa estão em plano de demolição).

### 2.6 Primeiro contrato (2013): Concorrência 011/2012, Contrato 117/2013

- Portal da Transparência, dados abertos de Compras, arquivo de julho de 2013
  (https://portaldatransparencia.gov.br/download-de-dados/compras/201307, `201307_Compras.csv`), linha da UG 153163:
  "Número do Contrato" 1172013; objeto "Fornecimento de material e maõ de obra (EMPREITADA GLOBAL), destinados a construção de
  Laboratórios de Ensino e Pesquisa e Salas de Apoio Administrativo e instalação de um Elevador no Bloco '29' do Depto. de
  Química do CFM/UFSC (área = 3.441,88m²)."; modalidade Concorrência; licitação nº 000112012 (Concorrência 11/2012);
  situação "Rescindido - Publicado"; assinatura 18/07/2013; publicação no DOU 23/07/2013; vigência 18/07/2013 a 24/03/2015;
  contratado CNPJ 03611631000135, "JULIO CESAR DE LIMA E SILVA LTDA"; valor inicial R$ 7.077.758,10; valor final
  R$ 7.077.758,10.
- Página oficial do DFO/UFSC "Bloco Administrativo e Instalação de Elevador no Bloco 29 do CFM"
  (https://dfo.ufsc.br/bloco-administrativo-e-instalacao-de-elevador-no-bloco-29-do-cfm/, publicada em 22/07/2013, última
  alteração em 26/12/2019): "Valor Contratado: R$ 7.077.758,10"; "Empresa Contratada: LIMA E SILVA ENGENHARIA E CONSTRUTORA
  LTDA – EPP"; "Data de Início da Obra: 29/07/2013"; "Data de Previsão do Término da Obra: 20/11/2014"; "Data da Vistoria:
  15/12/2014"; "Percentual Executado: 43,26%"; "Data de Conclusão do Contrato: CONTRATO RESCINDIDO EM 01/06/2015".
- Nome: o DFO escreve "Lima e Silva Engenharia e Construtora Ltda – EPP"; o cadastro do contrato e a Receita trazem a razão
  social "JULIO CESAR DE LIMA E SILVA LTDA", nome fantasia "L&S ENGENHARIA". É a mesma empresa pelo CNPJ do contrato.
- Receita Federal (base aberta do CNPJ, lida pelo espelho https://publica.cnpj.ws/cnpj/03611631000135, base de 12/09/2026):
  Curitiba/PR; início de atividade 25/01/2000; empresa de pequeno porte; atividade principal "Construção de edifícios";
  situação cadastral "Inapta" desde 14/05/2026; sócio-administrador Julio Cesar de Lima e Silva desde 25/01/2000.
- Ordem de serviço: notícia do DFO de 22/07/2013
  (https://dfo.ufsc.br/assinada-mais-uma-ordem-de-servico-para-obra-no-campus-reitor-joao-david-ferreira-lima-8/): "O Diretor do
  Departamento de Fiscalização de Obras, Eng. Rodrigo Bossle Fagundes, assinou na data de hoje, a ordem de serviço de uma obra
  com início previsto para julho de 2013, mais precisamente no dia 29".
- Notícia da UFSC de 26/09/2013, "CCE, CFM e CTC passam por obras e reparos no segundo semestre" (reproduzida no relatório
  oficial "Relatório imprensa 2013" da gestão, https://blogdagestao.ufsc.br/files/2014/05/Relat%C2%A2rio_imprensa_2013_FINAL-WEB.pdf,
  p. 69): "No final do mês de julho começaram as obras no CFM, que compreendem a construção do prédio administrativo e a
  instalação de um elevador no Bloco 29 do Departamento de Química. O projeto prevê área construída de 3.441,88 metros
  quadrados, com previsão para conclusão em novembro de 2014. A empresa contratada é a Lima e Silva Engenharia e Construtora
  Ltda – EPP." e "As novas instalações irão abrigar a direção do CFM, as coordenações dos cursos de graduação em Química,
  Física, Matemática e Meteorologia e algumas coordenações de pós-graduação, setores atualmente alocados nos blocos modulados do
  centro, construídos na década de 1960." e, na coluna seguinte do mesmo trecho do CFM: "Biblioteca setorial, anfiteatro para
  150 pessoas, espaço para a empresa júnior e salas de aula estão previstos no projeto desenvolvido pelo Departamento de
  Projetos de Arquitetura e Engenharia (DPAE) da Universidade. Os recursos são do Programa de Apoio a Planos de Reestruturação e
  Expansão das Universidades Federais (Reuni), do Governo Federal." (o PDF tem duas colunas; a biblioteca, o anfiteatro e a
  empresa júnior são do projeto do CFM, o que liga a frase do Reuni ao prédio do CFM). A notícia original no noticias.ufsc.br
  não foi achada (endereço provável devolve 404); a fonte lida é o relatório oficial da gestão que a reproduz.

### 2.7 CGU: obra paralisada e valor executado do primeiro contrato

- CGU, Relatório de Avaliação dos Resultados da Gestão nº 201702650, UFSC, publicado em 05/12/2019
  (https://eaud.cgu.gov.br/relatorios/download/855692; ficha em https://eaud.cgu.gov.br/relatorios/), trabalho de campo de
  02 a 19/10/2018, período avaliado 2013 a 2018.
  - Resposta 1.3: "A obra do prédio administrativo do Centro de Ciências Físicas e Matemáticas (CFM) está paralisada desde a
    rescisão unilateral do contrato, em 1º de junho de 2015." e "O impacto social se dá, principalmente, pela falta de estrutura
    adequada para os estudantes, servidores e professores do CFM."
  - Constatação 1.1.1.6 (título: "Existência de relevante obra paralisada (Joinville/SC), onde já foram aportados R$
    10.894.912,80, em município no qual a UFSC paga R$ 4.944.000,00 anuais em aluguel de edificação ocupada."), no fato:
    "também estão paralisadas as obras do Centro de Ciências Físicas e Matemáticas (CFM), cuja rescisão unilateral do contrato
    foi assinada em 1º de junho de 2015. O valor contratado da obra foi de R$ 7.077.758,10 e foram executados R$ 3.061.830,69,
    antes da paralisação. A UFSC informou que, como o contrato foi rescindido, necessita da contratação de uma próxima etapa
    para conclusão da edificação."
  - Conclusão da constatação: "ocorreu afronta ao artigo 45 da Lei de Responsabilidade Fiscal, pois foram inseridas novas obras,
    em lei orçamentária, sem a garantia de recursos para a conclusão dos projetos existentes." Causa: "Fragilidade no
    planejamento das obras a serem executadas pela Universidade".
  - Recomendação 1: "Priorizar a finalização de edificações inacabadas nos campi da UFSC [...] antes da realização de novos
    projetos."
  - Leitura: a constatação é sobre a UFSC em geral (o título fala de Joinville); o CFM aparece como outro caso de obra
    paralisada. A CGU não aponta irregularidade no contrato do CFM.

### 2.8 Retomada (2019 a 2023): quem assinou, motivo da rescisão e valor pago

- Contrato 317/UFSC/2019 (PDF digitalizado em https://contratos.comprasnet.gov.br/storage/contrato/69937_00317_2019/e4aaac246dcaf2596a19097e975241b4.pdf,
  lido por OCR nas páginas 1 e 34): assinado pela UFSC por "Eng. Paulo Roberto Pinto da Luz, Secretário de Obras, Manutenção e
  Ambiente"; pela contratada, pelo sócio Gabriel Mendonça Gonçalves (reconhecimento de firma em Brasília, 11/12/2019).
- Página oficial do DFO/UFSC "Retomada do Bloco Administrativo do CFM" (https://dfo.ufsc.br/retomada-do-bloco-administrativo-do-cfm/,
  publicada em 26/12/2019, última alteração em 24/05/2023): "Valor Contratado: R$ 6.751.904,72"; "Fonte de Recursos: Orçamento
  UFSC"; "Data de Início da Obra: 09/01/2020"; "Data de Previsão do Término da Obra: 01/07/2021"; "Data da Vistoria: 23/05/2023
  (Última medição realizada: 23/05/2023)"; "Percentual Executado: 19,79% (Valor total pago = R$ 1.336.183,59)"; "Descrição dos
  Serviços: Execução de alvenarias. Execução de valas de média tensão. Execução de passeios. Escavação da cisterna. Execução da
  rampa e escada de acesso ao antigo bloco do CFM."; "Data de Conclusão do Contrato: CONTRATO RESCINDIDO EM 23/05/2023".
- Termo de Rescisão Amigável (https://contratos.comprasnet.gov.br/storage/contrato/69937_00317_2019/b5qwZ0xGBRfwXEJ6EVHTtA1DdyCOk4EUIVRLiaRh.pdf),
  23/05/2023, assinado pela UFSC por "Eng. Hélio Rodak de Quadros Junior, Prefeito Universitário" e pela contratada por Igor
  Mendonça Gonçalves: "Rescisão Total e Amigável do Contrato nº 317/UFSC/2019 [...] com fundamento no art. 79, inciso II, da Lei
  n. 8.666/93, por razões de conveniência da Administração"; "A motivação para a rescisão do presente contrato está presente no
  Ofício nº 098/2022/DFO-SEOMA" (o ofício não está publicado); pagamentos na rescisão: R$ 49.952,64 de "serviços extras" (de um
  termo aditivo "autorizado, instruído, executado, porém não celebrado em razão das circunstâncias enfrentadas à época") e
  R$ 28.928,59 de "Medição complementar". Os CPFs que o documento traz não foram copiados para este projeto.
- Extrato de rescisão no DOU, 24/05/2023 (texto no Contratos.gov.br, endpoint `publicacoes`): "rescisão total e amigável do
  contrato nº 317/ufsc/2019 [...] por razões de conveniência da administração".
- Retificação do Termo Aditivo 1/2021 no DOU (09/12/2021): a empresa passou a "Mendonça & Gonçalves Construções e Incorporações
  Eireli" e o representante Gabriel Mendonça Gonçalves foi "substituído por Igor Mendonça Gonçalves".
- Receita Federal (https://publica.cnpj.ws/cnpj/13798155000167, base de 12/09/2026): razão social "MENDONCA E GONCALVES
  CONSTRUCOES E INCORPORACOES LTDA", nome fantasia "MG INCORPORADORA", Brasília/DF, situação "Ativa", início 03/06/2011, empresa
  de pequeno porte, "Construção de edifícios", sócio-administrador Igor Mendonça Gonçalves desde 03/06/2011.

### 2.9 Terceira tentativa: Concorrência Eletrônica 90002/2026 (homologada em ago/2026)

- PNCP, compra 83899526000182-1-000078/2026 (https://pncp.gov.br/app/editais/83899526000182/2026/78; API
  https://pncp.gov.br/api/consulta/v1/orgaos/83899526000182/compras/2026/78), lida em 2026-10-06: Concorrência Eletrônica nº
  90002/2026, processo 23080.061723/2025-02, publicada em 12/06/2026, propostas até 26/06/2026, critério "Maior desconto".
  Objeto: "Contratação de empresa para fornecimento de material e mão de obra (empreitada global) destinados à execução da
  retomada da obra da edificação CFM administrativo e construção do bloco de salas de aula anexo, localizado no Campus
  Universitário da Trindade da Universidade Federal de Santa Catarina (UFSC), com área de 5.101,16 m²".
  "valorTotalEstimado": 27.458.789,03; "valorTotalHomologado": 20.594.091,77.
- Resultado (API `itens/1/resultados`): fornecedor EMBRACOL OBRAS LTDA, CNPJ 05.901.551/0001-40, valor homologado
  R$ 20.594.091,77 (o registro traz 20594091,7725), "dataResultado" 2026-08-10, item "Homologado".
- Contrato: nenhum contrato da UFSC com a Embracol nem com este objeto apareceu na lista de contratos ativos da UG 153163 no
  Contratos.gov.br (lida em 2026-10-06, com contratos assinados até 05/10/2026) nem na busca de contratos do PNCP. Isso quer
  dizer "não localizado", não "não existe".
- Leitura: o objeto de 2026 junta a conclusão do prédio do CFM com um bloco novo de salas (5.101,16 m² no total, contra
  3.441,88 m² do prédio); o valor de 2026 não é comparável ao dos contratos de 2013 e 2019 sem separar as duas partes, e o
  edital não foi aberto para isso.

- Edital da Concorrência 90002/2026 (PDF de 984 páginas no PNCP, arquivo 1 da compra), "RESUMO GERAL DO ORÇAMENTO REFERENCIAL",
  data base FEV/26: "TOTAL GERAL: [...] 27.458.789,03"; "ÁREA TOTAL DA CONSTRUÇÃO (M2): 5.101,16"; "PREÇO (R$/M2): 5.382,85".
  O resumo não separa a conclusão do prédio do CFM do bloco novo de salas. Item 2.5.1.1 da planilha: "LIMPEZA DE TODA A OBRA PARA
  INÍCIO DOS TRABALHOS INCLUINDO REMOÇÃO DE MATERIAIS ABANDONADOS, RESTOS DE FORMAS, ARAMES DE AMARRAÇÃO DE FORMAS",
  51,00 m3, "ESPESSURA MÉDIA DE ENTULHO ESTIMADA EM 0,010M EM TODA A ÁREA DO EDIFÍCIO". Termo de referência assinado
  digitalmente por servidores do Departamento de Projetos de Arquitetura e Engenharia (DPAE), datado de 11/06/2026.
- Receita (https://publica.cnpj.ws/cnpj/05901551000140, base de 12/09/2026): o CNPJ 05.901.551/0001-40 aparece com a razão
  social "ORACON OBRAS LTDA", Joinville/SC, ativa, início 05/08/2003. O PNCP traz "EMBRACOL OBRAS LTDA" para o mesmo CNPJ. A
  diferença de nome não foi explicada nesta pesquisa (pode ser troca de razão social; não verificado).

### 2.10 Comparação honesta: três prédios contratados pela UFSC em 2013 no mesmo campus

Fonte única para o valor: "Valor Inicial Compra" dos dados abertos de Compras do Portal da Transparência (arquivo do mês da
assinatura); área e situação: páginas oficiais do DFO/UFSC.

| Obra | Contrato (assinatura) | Valor inicial | Área | Situação (DFO) |
|---|---|---|---|---|
| Bloco Administrativo do CFM | 117/2013 (18/07/2013), Julio Cesar de Lima e Silva Ltda | R$ 7.077.758,10 | 3.441,88 m² | rescindido em 01/06/2015 com 43,26% executado |
| Salas de Aula e Laboratórios de Ensino do CCE | 505/2012 (07/02/2013), Salver Construtora e Incorporadora Ltda | R$ 11.206.685,93 (valor final R$ 11.588.548,89) | 4.611,69 m² | "Obra concluída", 25/01/2017 |
| Blocos E, F e Anexo E do CFH | 156/2013 (30/09/2013), Construtora Progredior Ltda | R$ 17.264.244,72 (valor final igual) | 6.003,25 m² | "Obra concluída", 06/12/2017 |

- Fontes: https://portaldatransparencia.gov.br/download-de-dados/compras/201302 (CCE), /201307 (CFM), /201310 (CFH);
  https://dfo.ufsc.br/7226-2/ (CCE), https://dfo.ufsc.br/blocos-ef-e-anexo-e-do-cfh/ (CFH),
  https://dfo.ufsc.br/bloco-administrativo-e-instalacao-de-elevador-no-bloco-29-do-cfm/ (CFM).
- Divergência registrada: as páginas do DFO trazem "Valor Contratado" de R$ 13.095.521,80 (CCE) e R$ 18.668.699,57 (CFH),
  diferentes do valor inicial do Portal; a do CFM bate com o Portal (R$ 7.077.758,10). Para comparar igual com igual, o caso usa
  o valor inicial do Portal nos três.
- IPCA (IBGE, SIDRA tabela 1737, variável 2266, https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/201302,201307,201309,202412):
  fev/2013 3655,24; jul/2013 3717,03; set/2013 3738,99; dez/2024 7100,50. Correção do mês da assinatura até dez/2024.
- O que a comparação não mede: o contrato do CFM inclui um elevador no Bloco 29 da Química; o do CFH teve recursos da
  Petrobras e do orçamento da UFSC (DFO); nenhum dos valores é de pagamento.

## 3. O que não foi possível confirmar

(em andamento)

## 4. Registro de fontes consultadas

