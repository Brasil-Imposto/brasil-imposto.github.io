# ETE Insular (Florianópolis): contratos, empresas, responsáveis, achados e comparação

**Data da coleta:** 2026-09-30 (todas as consultas nesta data, salvo indicação)
**Dados:** `data/works/ete-insular.json` (gerado por `pipelines/works/build_ete_insular.py`)
**Fotos:** `docs/superpowers/previews/assets/cases/ete-insular/` com `credits.json`
**Pergunta:** para a ampliação da Estação de Tratamento de Esgoto (ETE) Insular, quais contratos existem, com quem, quanto já foi gasto, quem assinou, quem governava, o que os órgãos de controle disseram e se o custo é razoável perto de obras parecidas.
**Onde a pesquisa foi feita:** computador nos EUA (IP norte-americano), como nas pesquisas anteriores.

## Regras desta pesquisa

As mesmas da pesquisa da Ponte Hercílio Luz: só papéis e atos oficiais, com as palavras do órgão; nenhuma inferência de irregularidade; cada número com URL oficial e data da coleta; a imprensa serviu só para achar documentos. Nenhum documento oficial lido usa "superfaturamento", "sobrepreço" ou "desvio" para esta obra.

## 0. Resumo

| Item | Resultado | Fonte principal |
|---|---|---|
| Escolha | ✅ Obra de saneamento em debate em 2025 e 2026 (retomada, 82,87% da estrutura civil em jan/2026, operação prometida para 2026, contrato prorrogado até abr/2027, novo contrato do emissário assinado em 15/09/2026) | Casan (notícias e portal) |
| Contratos | ✅ Três: o primeiro (Trix-Infracon, R$ 94,7 milhões, 2018, rescindido), o atual (Itajuí/Construtami, R$ 144,9 milhões em 2020, hoje R$ 261,9 milhões com 19 registros de alteração) e o do emissário (CFO, R$ 31,2 milhões, set/2026) | Portal da Transparência da Casan |
| Pagamentos | ⚠️ Só acumulado: R$ 177,4 milhões "consumidos" (SAP, base de 05/09/2026) e R$ 159,1 milhões de valor principal faturado (30/08/2026). Nada por ano | Portal da Casan |
| Empresas | ✅ Consórcio, líder e consorciada com CNPJ e quadro societário; Trix e Infracon sem CNPJ nos documentos da Casan | Receita (via espelho) |
| Quem assinou | ✅ Diretores da Casan nos aditivos (assinatura digital nos PDFs) e nas Resoluções; o extrato do contrato de 2020 no DOE não foi localizado | PDFs da Casan |
| Governadores | ✅ Quatro pessoas nas datas relevantes, com partido na época | Alesc, Memória Política |
| Achados | ✅ Rescisão e multa do primeiro contrato (Casan, com acordo judicial homologado); auditoria antiga do TCE-SC sobre a estação existente. Nenhum achado do TCE-SC, MPSC, TCU, CGU ou MPF sobre o contrato atual foi localizado | Casan, TCE-SC |
| Comparação | ✅ R$ 430 mil por L/s de capacidade (R$ dez/2024). Praticamente igual à nova ETE Potecas da própria Casan; 7,0 vezes a ampliação da ETE Belém (Curitiba, 4 vezes maior); bem abaixo da ampliação de Fredericksburg (EUA): 8,8 vezes mais cara pelo câmbio, 4,0 pela PPP | seção 6 |

## 1. Por que esta obra (candidatos considerados)

A tarefa pedia duas obras de saúde, saneamento, educação ou obras urbanas municipais em Florianópolis, Joinville, Blumenau, Itajaí, Chapecó ou Criciúma, em debate em 2025 e 2026 e com registros oficiais suficientes para todos os campos. Foram checados, não presumidos:

| Candidato | O que se achou | Decisão |
|---|---|---|
| Hospitais estaduais nessas cidades | No registro de contratos do Estado (CSV do SIGEF, 106.071 linhas), as obras de saúde nessas cidades são pequenas: reforma da ala de cardiologia do Hospital Regional Hans Dieter Schmidt, em Joinville (R$ 10,2 milhões, 2024), subestação do Hospital Regional de São José (R$ 16,5 milhões, 2025) | Descartado: escala pequena e sem debate público relevante |
| Novo complexo do Hospital São José e da Maternidade Darcy Vargas (Joinville) | Protocolo de intenção para compra de área (R$ 23 milhões) e PPP a estruturar; sem contrato de obra | Descartado: não há contrato |
| Policlínica Regional de Blumenau (Novo PAC, R$ 30 milhões) | O próprio prefeito disse, em set/2025, não saber se a obra seguirá; sem contrato | Descartado |
| Barragem de Botuverá (cheias do Itajaí-Mirim) | Contrato CT-00055/2026 de R$ 152,9 milhões assinado em 14/09/2026, situação "A iniciar" | Descartado: sem pagamentos nem execução; Botuverá não está na lista de cidades |
| ETE Sul da Ilha (Florianópolis) | Licitação anunciada em 2025, contrato não localizado | Descartado |
| **ETE Insular (Casan, Florianópolis)** | Três contratos com aditivos e PDFs no portal da Casan, tabela de obras com valor faturado, rescisão com acordo judicial, auditoria antiga do TCE-SC, notícias oficiais de 2025 e 2026 | **Escolhida** (saneamento) |
| **CEIs de Joinville (15 creches, R$ 226 milhões)** | Contratos, empenhos e pagamentos na API aberta da Prefeitura, extratos no Diário Oficial, TAC do MPSC e recomendação de jul/2026 | **Escolhida** (educação), ver `BRASIL-IMPOSTO_RESEARCH_obras-sc-cei-comasa-joinville_2026-09-30.md` |

Obras de estrada, ponte, túnel, porto e mobilidade ficaram de fora de propósito (outra pesquisa cuida delas).

## 2. A obra

- **O que é:** ampliação e modernização da ETE Insular, a estação que trata o esgoto do Centro de Florianópolis e bairros vizinhos, mais redes das Bacias D e F. A Casan chama a obra de "a maior obra de saneamento de Santa Catarina" (notícia de 02/07/2020).
- **Quanto muda:** de 296 para 612 litros por segundo; de 150 mil para 225 mil moradores atendidos; tratamento terciário, "capaz de remover além de matéria orgânica os elementos nitrogênio e fósforo" (Casan, 24/01/2020).
- **Escopo do contrato, além da estação:** "Ligações domiciliares - 3.753 un.; Rede coletora - 12.209 m; Estações Elevatórias de Esgoto - 6 un.; Emissários - 9.512 m" (Casan, 02/07/2020).
- **Quem faz:** Companhia Catarinense de Águas e Saneamento (Casan), sociedade de economia mista do Estado (CNPJ 82.508.433/0001-17). A Casan não usa o SIGEF: seus contratos e gastos não aparecem no registro de contratos nem no Portal da Transparência do Poder Executivo.
- **Dinheiro:** financiamento da JICA. Os termos aditivos dizem: "Os recursos financeiros [...] são provenientes da Agência de Cooperação Internacional do Japão - JICA".
- **Função SICONFI:** Saneamento (17). Como é gasto de empresa estatal, não entra nos balanços do Estado no SICONFI.
- **Município:** Florianópolis, código IBGE 4205407.
- **Situação:** em execução. "82,87% da estrutura civil concluída" em 2025; "Já para 2026, a CASAN vai trabalhar para a conclusão das estruturas em andamento com o objetivo de iniciar a operação" (Casan, 20/01/2026). Na tabela "Obras de expansão" (dados até 30/08/2026): "Andamento", início nov/20, término abr/27.

Linha do tempo (datas de documentos oficiais):

| Data | Fato | Fonte |
|---|---|---|
| 2018-09-10 | Início de vigência do EOC 1151/2018, Consórcio Trix-Infracon (Concorrência Internacional 7/2017) | Portal da Casan |
| 2019-08-19 | Resolução 213/2019: rescisão unilateral e suspensão do consórcio | Portal da Casan (texto no registro) |
| 2019-10-07 | Resolução 264/2019: suspensão com efeito suspensivo; rescisão mantida | idem |
| 2020-01-23 | Três consórcios entregam propostas na nova licitação | Casan, 24/01/2020 |
| 2020-07-02 | Menor proposta: R$ 145.509.368,55, enviada à JICA | Casan, 02/07/2020 |
| 2020-11-06 | Assinatura do EOC 1246/2020 com o Consórcio Itajuí/Construtami, R$ 144.899.952,36, 1.620 dias | Termos aditivos ("celebrado em 06/11/2020") |
| 2020-12-10 e 2020-12-17 | Acordo judicial com o Consórcio Trix-Infracon e sentença de homologação | Resolução Casan 135/2021 |
| 2025-04-14 | Fim do prazo original (calculado: 06/11/2020 + 1.620 dias); prorrogado para 14/04/2026 | TA 06/2025 |
| 2026-04-14 | Nova prorrogação, até 14/04/2027 | TA 08/2026 |
| 2026-09-15 | Contrato EOC 1534/2026 (emissário de esgoto bruto de 560 mm e adutora de água de 710 mm), Construtora CFO, R$ 31.190.417,28 | PDF do contrato |

## 3. Contratos

Fonte: Portal da Transparência da Casan. O portal é um aplicativo Angular; os dados vêm de endpoints JSON sem login, achados lendo o código da página e usados pelo script `pipelines/works/casan_fetch.py`: `/data/contrato?ano=&objeto=` (vista PNTP, com aditivos e PDFs), `/data/contratos?empresafiltro[]=` (vista SAP, com valor consumido e saldo) e a tabela "Obras de expansão" (CSV).

| Contrato | Licitação | Contratada | CNPJ | Início | Valor original | Valor atual | Situação |
|---|---|---|---|---|---|---|---|
| EOC 1151/2018 | CI 7/2017 | Consórcio Trix-Infracon (Trix Engenharia Civil Ltda e Infracon Engenharia e Comércio Ltda) | não consta | 2018-09-10 | R$ 94.663.085,48 | R$ 94.663.085,48 | Rescindido |
| EOC 1246/2020 | CN 1/2019 | Consórcio Itajuí/Construtami ETE Insular | 39.673.759/0001-70 | 2020-11-06 | R$ 144.899.952,36 | R$ 261.908.002,30 (calculado) | Vigente, até 2027-04-14 |
| EOC 1534/2026 | PL 115/2026 | Construtora CFO Ltda | 19.862.375/0001-99 | 2026-09-15 | R$ 31.190.417,28 | R$ 31.190.417,28 | Vigente, até 2028-06-19 |

Notas:
- **Valor atual do EOC 1246/2020** = original + todos os aditivos - supressões do registro PNTP, calculado nesta pesquisa. Decomposição: reajustes R$ 64.139.512,18; reequilíbrio econômico-financeiro de 14,84% (TA 01/2021) R$ 21.502.843,20 e sua atualização (2023) R$ 168.254,68; acréscimos quantitativos e qualitativos R$ 31.487.302,66; supressões R$ 289.862,78. Sem os reajustes, o "valor principal" é R$ 197.768.490,12, e a tabela oficial "Obras de expansão" da Casan traz exatamente esse número (conferido ao centavo pelo script).
- **Crescimento:** +80,75% sobre o original com reajustes; +36,49% sem eles (cálculo).
- **Divergência entre as duas vistas da Casan:** o SAP (base de 05/09/2026) mostra R$ 251.067.149,78, porque ainda não traz o TA 07/2025 (R$ 4.719.562,01) e o reajuste 6/2026 (R$ 6.121.290,51). A soma dos dois fecha a diferença.
- **Contrato de 2018:** o SAP o divide em duas linhas, uma por empresa (EOC001151/2018-A, R$ 47.331.542,73, Trix; -B, R$ 47.331.542,75, Infracon), ambas com valor consumido zero.
- **EOC 1534/2026:** mistura esgoto (emissário do SES Insular) e água (adutora do Sul da Ilha). Fica fora das somas e da comparação. "O valor relativo à mão de obra é R$ 6.737.130,13 [...] O valor relativo aos materiais e equipamentos é R$ 24.453.287,15"; recursos "provenientes do Orçamento de 2026, 2027 e 2028 da CASAN".
- **Contrato vizinho, só como contexto:** EOC 1119/2017 (Consórcio Fast-CFO, R$ 17.039.000,00), sistema complementar da Beira-Mar Norte. Não é a ampliação da ETE.

Registros de alteração do EOC 1246/2020 (texto do objeto resumido; a lista completa, com links dos PDFs, está no JSON):

| Ato | Data | Valor | O que diz |
|---|---|---|---|
| Reajuste 1/2021 | 2021-06-08 | R$ 13.573.213,24 | jan/20 a jan/21, índice 0,093673 |
| TA 01/2021 | 2021-10-25 | R$ 21.502.843,20 | "reequilíbrio econômico financeiro no percentual de 14,84% [...] em face ao evento imprevisível ou, no mínimo, previsível de consequências incalculáveis" |
| Reajuste 2/2022 | 2022-04-28 | R$ 19.023.487,57 | jan/20 a jan/22 |
| TA 02/2023 | 2023-01-09 | R$ 9.357.632,00 | "Acréscimo quantitativo e qualitativo de 6,46% ao valor original" |
| Reajuste 3/2023 | 2023-03-24 | R$ 10.619.068,06 | jan/20 a jan/23 |
| TA 03/2023 | 2023-10-25 | + R$ 5.320.331,68, - R$ 163.879,12 | acréscimo de 3,67% e supressão de 0,11% |
| Reequilíbrio 0/2023 | 2023-12-01 | R$ 168.254,68 | atualização do TA 03/2023 |
| Reajuste 4/2024 | 2024-04-23 | R$ 4.430.637,92 | jan/20 a jan/24 |
| TA 04/2024 | 2024-09-12 | + R$ 2.864.534,77, - R$ 125.983,66 | acréscimo de 1,98% e supressão de 0,09% |
| TA 05/2024 | 2024-10-23 | R$ 9.225.242,20 | "Acréscimo quantitativo de 6,37% ao valor original" |
| Reajuste 5/2025 | 2025-03-06 | R$ 10.371.814,88 | jan/20 a jan/25 |
| TA 06/2025 | 2025-04-14 | prazo | até 14/04/2026 |
| TA 07/2025 | 2025-08-22 | R$ 4.719.562,01 | acréscimo de 3,26% |
| Reajuste 6/2026 | 2026-03-17 | R$ 6.121.290,51 | jan/20 a jan/26 |
| TA 08/2026 | 2026-04-14 | prazo | até 14/04/2027 |

Mais quatro registros de troca de gestor ou fiscal (2024, 2025 e 2026), sem valor.

## 4. Pagamentos

**Por ano: não disponível (null no JSON).** Motivo: a Casan é estatal e não paga pelo SIGEF, então os pagamentos não aparecem no Portal da Transparência do Executivo (a API usada na pesquisa da ponte não os traz). O portal da Casan publica, por contrato, só o acumulado e o saldo; a página "Despesa da Empresa" remete às demonstrações financeiras, que não abrem por contrato.

| Medida | Valor | Data-base | Fonte |
|---|---|---|---|
| Valor consumido do EOC 1246/2020 (SAP) | R$ 177.381.260,29 | 2026-09-05 | `/data/contratos?empresafiltro[]=2000009269` |
| Saldo do EOC 1246/2020 (SAP) | R$ 73.685.889,49 | 2026-09-05 | idem |
| Valor principal faturado (sem reajustes) | R$ 159.075.646,78 de R$ 197.768.490,12 (80,4%, cálculo) | 2026-08-30 | tabela "Obras de expansão" |
| Valor consumido do EOC 1151/2018 | R$ 0,00 | 2026-09-05 | SAP, fornecedores 2000004715 e 2000005225 |

"Valor consumido" é o nome do campo no SAP; o portal não o define como pagamento. Pedido para completar: a Casan, pela Lei de Acesso à Informação, os pagamentos por ano do contrato EOC 1246/2020.

## 5. Empresas

Fonte: base aberta do CNPJ da Receita Federal. O servidor oficial e o espelho minhareceita.org (que respondeu 503 nesta data) foram substituídos pelo espelho público publica.cnpj.ws para quatro CNPJs; o da CFO saiu do minhareceita.org. É fonte derivada, não o servidor oficial.

| CNPJ | Razão social | Natureza | Cidade | Situação | Sócios ou consorciadas (Receita) | Site oficial |
|---|---|---|---|---|---|---|
| 39.673.759/0001-70 | CONSORCIO ITAJUI/CONSTRUTAMI ETE INSULAR | Consórcio de Sociedades | Curitiba/PR | Ativa (2020-11-04) | Itajuí Engenharia de Obras Ltda e Construtami Engenharia e Comércio Ltda (consorciadas); Lorenzo Varassin (administrador) | não tem |
| 78.739.158/0001-75 | ITAJUI ENGENHARIA DE OBRAS LTDA (líder) | Sociedade Empresária Limitada | Curitiba/PR | Ativa | Paulo Cesar Varassin (sócio-administrador), Lorenzo Varassin (administrador) e três holdings sócias desde 2023 | itajui.com.br (mesmo domínio do e-mail do consórcio na Autorização Contratual) |
| 58.793.852/0001-63 | CONSTRUTAMI ENGENHARIA E COMERCIO LTDA | Sociedade Empresária Limitada | São Paulo/SP | Ativa | F M Rodrigues & Cia Ltda; Marcelo Souza de Camargo Rodrigues (sócio-administrador) | construtami.com.br (logotipo, e-mail e cidade conferem) |
| 19.862.375/0001-99 | CONSTRUTORA CFO LTDA | Sociedade Empresária Limitada | Florianópolis/SC | Ativa | Marcio Frank Silva de Oliveira (sócio-administrador), José Alessandro da Silva Oliveira | cfo.eng.br (mesmo endereço e e-mail do contrato) |
| não consta | TRIX ENGENHARIA CIVIL LTDA | | | | | não verificado |
| não consta | INFRACON ENGENHARIA E COMÉRCIO LTDA | | | | | não verificado (há mais de uma "Infracon" no PNCP; sem o CNPJ, não se escolhe) |

Links do Portal da Transparência federal estão no JSON (`portaldatransparencia.gov.br/pessoa-juridica/<CNPJ>`).

## 6. Quem assinou e quem governava

### 6.1 Assinaturas (papel, não conduta)

Os PDFs dos aditivos trazem a página "Assinaturas do documento" do sistema SGPe da Casan. O CPF aparece mascarado no original e não é reproduzido.

| Pessoa | Papel (fonte) | O que assinou |
|---|---|---|
| Roberta Maas dos Anjos | Diretora-Presidente (Resoluções 213/2019, 264/2019 e 135/2021) | Resoluções sobre o contrato de 2018; TA 01/2021 e TA 02/2023 |
| Fábio Cesar F. Krieger | Diretor de Operação e Expansão (mesmas Resoluções; notícia de 02/07/2020) | Resoluções sobre o contrato de 2018 |
| Pedro Joel Horstmann | Diretor de Operação e Expansão desde 19/07/2021; Diretor-Presidente desde 15/04/2026 (Fato Relevante de 13/04/2026) | TA 01/2021 a TA 06/2025, TA 08/2026 e o contrato EOC 1534/2026 |
| Edson Moritz Martins da Silva | Diretor-Presidente de ago/2023 a 14/04/2026 (Fato Relevante; notícia da Casan de 15/04/2026) | TA 03/2023 a TA 07/2025 |
| Rosane Vettori | Diretora Administrativa (página de RI da Casan) | TA 07/2025 e TA 08/2026 |
| Carlos Ivan Sturzbecher | Diretor Financeiro e de RI (página de RI) | Contrato EOC 1534/2026 |
| Paulo Cesar Varassin | pela contratada (certificado digital no TA 01/2021) | TA 01/2021 |
| Lorenzo Varassin | pela contratada (certificado digital nos TAs de 2023) | TA 02/2023 e TA 03/2023 |

O campo "gestor" do registro traz Evandro André Martins (EOC 1246/2020 e EOC 1534/2026); o campo "fiscal", Antonio Alexandre Martins e Rafael Casaril (com trocas registradas). Ao contrário do SIGEF, aqui a Casan separa gestor e fiscal, e os nomes são de servidores.

**Não localizado:** o extrato do contrato de 06/11/2020 no Diário Oficial do Estado (a lista de edições do DOE exige login e não há busca textual; ver diário). Por isso, quem assinou o contrato original pela Casan e pelo consórcio fica sem fonte primária.

### 6.2 Governadores nas datas relevantes

O governador não assina contratos da Casan. Partido na época, segundo as biografias da Alesc (Memória Política):

| Quem | Período | Partido na época | Datas da obra no período | Fonte |
|---|---|---|---|---|
| Eduardo Pinho Moreira | 2018-04-06 a 2018-12-31 | MDB ("Eduardo Pinho filiou-se ao Movimento Democrático Brasileiro (MDB) e assumiu efetivamente como Governador em 6 de abril de 2018") | início do contrato de 2018 | biografia 1158 |
| Carlos Moisés da Silva | 2019-01-01 a 2023-01-01, afastado de 26/10 a 27/11/2020 e de 30/03 a 07/05/2021 | PSL ("No ano de 2018, filiou-se ao Partido Social Liberal (PSL)"); Republicanos a partir de março de 2022 | rescisão (2019), TA 01/2021 | biografia 1308 |
| Daniela Reinehr | governadora interina de 26/10/2020 a 27/11/2020 | sem partido ("Atualmente sem Partido, Daniela participa da organização do partido Aliança pelo Brasil") | assinatura do contrato atual (06/11/2020) | biografia 1386 |
| Jorginho Mello | desde 2023 | PL ("Governador(a) 01/02/2023 - 31/01/2027 Partido Liberal") | aditivos de 2023 a 2026 e o contrato de set/2026 | biografia 514 |

Ressalvas: a tabela de mandatos da biografia de Daniela Reinehr rotula os períodos de forma inconsistente (PSL e "Partido Liberal"); o texto corrido foi preferido. A tabela da Alesc registra o início de Jorginho Mello em 01/02/2023; a posse constitucional foi em 01/01/2023.

## 7. Achados de órgãos oficiais

| # | Órgão e processo | O que é | Citação | Situação |
|---|---|---|---|---|
| 7.1 | Casan, Resolução 213/2019 (19/08/2019) | Ato da contratante | "Aplicar as Empresas TRIX Engenharia Civil Ltda e INFRACON Engenharia e Comércio Ltda., componentes do Consórcio TRIX-INFRACON INSULAR, a penalidade de 'Suspensão Temporária por 2 (dois) anos' [...] e rescisão unilateral do Contrato EOC n.º 1.151/2018 [...] tendo em vista o descumprimento das obrigações contratuais." | Rescisão mantida; suspensão depois suspensa |
| 7.2 | Casan, Resolução 264/2019 (07/10/2019) | Ato da contratante, após recurso e mandado de segurança | "Atribuir efeito suspensivo à penalidade [...] Manter a decisão de rescisão unilateral" | Decidido |
| 7.3 | Justiça de SC, 4ª Vara Cível da Capital, Autos 5006866-60.2019.8.24.0023 (e MS 5006892-58.2019.8.24.0023), registrado na Resolução Casan 135/2021 | Acordo judicial homologado | "Aplicar às Empresas integrantes do Consórcio TRIX-INFRACON INSULAR, a penalidade de 'Advertência e multa no valor de R$ 198.466,16' [...] conforme acordo judicial celebrado entre o referido consórcio e a CASAN" | Acordo de 10/12/2020, homologado em 17/12/2020, segundo a Casan. Autos não consultados |
| 7.4 | Casan, notícia de 02/07/2020 | Versão da contratante sobre o atraso | "o consórcio vencedor do processo licitatório anterior se recusou a executar a obra nos moldes previstos no Termo de Referência, forçando a rescisão do contrato e atraso do empreendimento" | Afirmação de uma parte; a disputa terminou em acordo |
| 7.5 | TCE-SC, AOR 04/05801564 e PMO 07/00627901, Decisão 3567/2010 (16/08/2010) | Auditoria operacional da estação antiga | "reiterar a implantação das recomendações 6.2.4 e 6.2.6 da Decisão n. 1457/2008, que não foram cumpridas" | Monitoramento de 2010; desfecho não localizado. Não trata da ampliação |
| 7.6 | TCE-SC, @REP 20/00098007, Relatório DLC 408/2022 | Relatório técnico sobre contrato vizinho (EOC 1119/2017) | "A Casan informa a ampliação da ETE Insular, no valor de R$ 144,8 milhões de investimento. [...] se demonstra que a ETE Insular está apresentando eficiência no tratamento dos efluentes." | Sugestão da área técnica; decisão do Pleno não localizada |

**Sobre o contrato atual (EOC 1246/2020):** nenhuma decisão do TCE-SC, MPSC, TCU, CGU ou MPF foi localizada. O reequilíbrio de 14,84% e os acréscimos (que somam 21,73% do valor original, cálculo) são atos da própria Casan, com parecer jurídico citado nos termos; nenhum órgão de controle se manifestou sobre eles nas fontes lidas. Limites: o Diário Oficial do TCE-SC não foi lido dia a dia (como na pesquisa da ponte) e o TJSC não foi consultado.

Nomes nos achados: os textos oficiais citados em 7.1 a 7.3 nomeiam só empresas; por isso nenhuma pessoa aparece ligada a eles aqui.

## 8. Comparação

**Unidade:** reais de dezembro de 2024 por litro por segundo (L/s) de capacidade de tratamento ao fim da obra. Método igual ao de `pipelines/bridges/build.py`: valores em reais corrigidos pelo IPCA do mês-base de preço até dez/2024; valores em dólar convertidos pelo câmbio médio do ano (Banco Mundial, PA.NUS.FCRF) e, à parte, pela PPP (PA.NUS.PPP), mais o IPCA. Código em `pipelines/works/convert.py`.

| Obra | Capacidade final | Custo informado | Base | R$ de dez/2024 | R$ por L/s final | R$ por L/s acrescentado |
|---|---|---|---|---|---|---|
| **ETE Insular + Bacias D e F** (Florianópolis) | 612 L/s (de 296) | R$ 197.768.490,12 (valor principal) | jan/2020, IPCA x1,331822 | R$ 263,39 milhões | **R$ 430.380** | R$ 833.520 |
| Nova ETE Potecas, 1ª etapa (São José/SC, Casan) | 600 L/s | R$ 240.841.428,47 (três contratos, sem reajustes) | mai/2022, dez/2023, jul/2024 | R$ 262,97 milhões | R$ 438.290 | não se aplica (estação nova) |
| ETE Belém, ampliação (Curitiba, Sanepar) | 2.520 L/s (de 1.500) | "cerca de R$ 140 milhões" | abr/2022 | R$ 155,74 milhões | R$ 61.802 | R$ 152.686 |
| Fredericksburg WWTP Upgrade (Virgínia, EUA) | 262,9 L/s (6,0 MGD, de 4,5) | US$ 180 milhões | 2024 | R$ 990,72 milhões (câmbio); R$ 456,61 milhões (PPP) | R$ 3.768.421 (câmbio); R$ 1.736.830 (PPP) | R$ 15,08 milhões (câmbio) |

Leitura:
- **Contra a Potecas (mesma empresa, mesmo tipo de licitação, época próxima):** a Insular custa praticamente o mesmo por L/s (a Potecas sai 2% mais cara), mesmo com 12 km de redes, 6 elevatórias e 3.753 ligações dentro do contrato da Insular. Por habitante de projeto, a Insular sai mais cara (R$ 1.171 contra R$ 801), porque atende menos gente por L/s.
- **Contra a ETE Belém:** a Insular custa 7,0 vezes o L/s. A Belém é quatro vezes maior (escala barateia o L/s), a notícia oficial não cita tratamento terciário nem redes, e o valor foi corrigido só desde abr/2022, embora parte tenha sido gasta antes: o custo da Belém está subestimado aqui.
- **Contra Fredericksburg:** a obra de SC custou menos. A americana, com remoção avançada de nitrogênio e fósforo, sai 8,8 vezes mais cara por L/s pelo câmbio e 4,0 vezes pela PPP. O número americano é orçamento, não custo final.
- **Limite comum:** o custo da Insular inclui redes; como a Casan não publica o valor separado da estação, o custo por L/s da Insular é um limite superior do custo só da estação.

Fontes de cada fator estão no JSON (`comparison.items[].sources` e `comparison.method`). Candidatos descartados: obras de rede da Casan (Ingleses, Saco Grande), sem capacidade de estação na mesma fonte; ETE Alambari (Sanepar, Cambará), página oficial com erro 403 do exterior; ETE Mampituba (Torres/RS), porque a Corsan é privada desde 2023.

## 9. Fotos

| Arquivo | O que mostra | Autor | Licença | Página |
|---|---|---|---|---|
| `baia-sul.jpg` | Baía Sul de Florianópolis (paisagem; não mostra a estação) | Danny Botelho | CC BY-SA 2.0 | https://commons.wikimedia.org/wiki/File:Ba%C3%ADa_Sul_de_Florian%C3%B3polis.jpg |
| `gov-daniela-reinehr.jpg` | Daniela Reinehr, 06/11/2020 (governadora interina na assinatura do contrato) | Marcos Corrêa/PR | CC BY 2.0 | https://commons.wikimedia.org/wiki/File:Daniela_Reinehr_em_novembro_de_2020.jpg |
| `gov-jorginho-mello.jpg` | Jorginho Mello (retrato como senador, 2017) | Agência Senado | Attribution | https://commons.wikimedia.org/wiki/File:Senador_Jorginho_Mello_(cropped).jpg |

Não há foto livre da ETE Insular no Wikimedia Commons (buscas por "ETE Insular", "estação de tratamento de esgoto Florianópolis" e "Casan Florianópolis" sem resultado). As fotos das notícias são "Acervo CASAN", sem licença livre declarada. O retrato de Carlos Moisés já existe em `cases/hercilio-luz/`.

## 10. Card

| Número | Valor | Nota |
|---|---|---|
| Contrato atual | R$ 261,9 milhões | original R$ 144,9 milhões |
| Capacidade | 296 → 612 L/s | Casan |
| Já consumido | R$ 177,4 milhões | SAP da Casan, base de 05/09/2026 |
| Atraso | +2 anos | fim previsto em abr/2025, prorrogado para abr/2027 |

## 11. Lacunas

| Lacuna | Onde provavelmente está | Como obter |
|---|---|---|
| Pagamentos por ano | Contas a pagar da Casan (SAP) | Pedido pela Lei de Acesso à Informação à Casan |
| Valor da estação separado das redes | Planilha da Autorização Contratual do EOC 1246/2020 | Pedido à Casan (a planilha não está entre os PDFs publicados) |
| Extrato do contrato de 06/11/2020 e signatários | DOE-SC de nov/2020 | Leitura edição por edição (repositório do DOE) ou pedido à Casan |
| CNPJs da Trix e da Infracon | Contrato EOC 1151/2018 | Pedido à Casan |
| Andamento dos autos 5006866-60.2019.8.24.0023 | TJSC (eproc) | Consulta de um IP brasileiro |
| Manifestação do TCE-SC sobre o reequilíbrio de 14,84% e os aditivos | DOTC-e | Leitura do Diário do TCE-SC de 2021 a 2026 |

## 12. Diário de transparência

| # | O que se buscou | Onde | Formato | Login | Passos | Resultado e obstáculos |
|---|---|---|---|---|---|---|
| 1 | Obras estaduais de saúde, educação e barragens nas seis cidades | dados.sc.gov.br, CSV de contratos (73,8 MB) | CSV | não | 1 download | ✅ triagem; a Casan não está nesse registro |
| 2 | Contratos da Casan | transparencia.casan.com.br | aplicativo Angular sobre JSON | não | cerca de 90 consultas | ✅ com esforço: os endpoints não são documentados e foram achados lendo o código da página; o filtro por objeto exige primeiro buscar um id; a exportação em CSV respondeu 302 sem conteúdo |
| 3 | Aditivos e contrato em PDF | `/data/contrato/arquivo/<id>` | PDF assinado digitalmente | não | 21 downloads | ✅ texto legível; o contrato original de 2020 não está entre os arquivos |
| 4 | Valor faturado | tabela "Obras de expansão" | CSV em Latin-1 | não | 2 | ✅ |
| 5 | Pagamentos por ano | portal da Casan, "Despesa da Empresa" | link para demonstrações financeiras | não | 3 | ❌ não existe por contrato |
| 6 | Licitação no PNCP | pncp.gov.br | JSON | não | 3 buscas | ⚠️ a Casan publica editais no PNCP desde 2026; os contratos de 2018 e 2020 são anteriores |
| 7 | Cadastro das empresas | Receita (oficial), minhareceita.org, publica.cnpj.ws | JSON | não | 12 | ⚠️ servidor oficial inacessível do exterior; minhareceita.org com erro 503 nesta data; publica.cnpj.ws funcionou (com limite de consultas; o script espera entre elas) |
| 8 | Diretores e datas | RI da Casan (página e Fato Relevante) | HTML e PDF | não | 3 | ✅ |
| 9 | Governadores e partidos | memoriapolitica.alesc.sc.gov.br | HTML | não | 5 | ✅; uma biografia com rótulos de partido inconsistentes |
| 10 | Candidaturas 2026 | TSE, API DivulgaCand | JSON | não | 2 | ❌ 403 do exterior; o arquivo aberto do CDN do TSE funcionou ✅ |
| 11 | Achados do TCE-SC | tcesc.tc.br e consulta.tce.sc.gov.br | PDF | não | 6 | ✅ dois documentos, achados por busca na web; sem busca por processo pública |
| 12 | Extrato no DOE-SC | portal.doe.sea.sc.gov.br | PDF | ⚠️ lista de edições exige login | 0 | ❌ não tentado edição por edição nesta coleta |
| 13 | Comparáveis | Casan (Potecas), AEN Paraná, prefeitura de Fredericksburg, Sanepar | HTML | não | 6 | ⚠️ AEN Paraná respondeu 404 (lida a cópia do Internet Archive); Sanepar respondeu 403 |
| 14 | Fotos | Wikimedia Commons (API) | JPG | não | 8 | ⚠️ nenhuma foto livre da estação; limite de requisições (429) contornado com espera |
| 15 | Buscas na web | buscador | | não | 8 das 12 buscas da pesquisa (incluindo a triagem dos candidatos) | só para achar endereços; nenhum número deste relatório vem de notícia de imprensa |

**Em resumo:** a Casan publica mais do que o Estado publicou para a ponte (aditivos em PDF, com assinaturas e valores, e o valor faturado), mas tudo atrás de um aplicativo sem documentação, e sem pagamentos por ano. Para saber quanto foi pago em cada ano, e quanto custou só a estação, é preciso pedir à Casan.
