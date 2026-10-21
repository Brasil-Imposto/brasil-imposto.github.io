# Situação dos cinco "Maiores escândalos": resolvido ou não resolvido

Pesquisa de 05/10/2026 para a etiqueta de cada cartão da seção "Maiores escândalos" (D65), com os mesmos casos de
`data/home/scandals.json`. Saída de dados: `data/home/scandals-status.json`.

## Regra aplicada (a mesma para os cinco)

Definição usada: o escândalo está resolvido quando foi esclarecido e os responsáveis responderam por ele.

Regra operacional: **"Resolvido"** só quando um registro oficial mostra os responsáveis punidos por decisão definitiva:
condenação criminal com trânsito em julgado, ou punição administrativa ou de tribunal de contas da qual não cabe mais recurso
(por exemplo, condenação do TCU ou de um TCE em Tomada de Contas Especial). Nos demais casos, **"Não resolvido"**. O dinheiro
público recuperado ou devolvido é registrado à parte, só com valor publicado por órgão oficial; sem valor oficial, fica `null`.

Notas de método:
- Notícia de imprensa serviu só para achar o documento oficial; nenhum fato abaixo tem a imprensa como fonte.
- Página que não abriu fica como "não confirmado".
- "Bloqueado", "sequestrado" ou "constituído" (crédito tributário lançado) não é "recuperado": é dinheiro indisponível ou cobrado
  por decisão provisória ou lançamento. Só entra em `money_recovered_brl` valor que um órgão oficial diz ter voltado aos cofres
  públicos (ou devolvido à vítima pelo responsável).
- Denúncia recebida, condenação sem trânsito em julgado, prisão preventiva, indiciamento e afastamento cautelar não são decisão
  definitiva e não mudam a etiqueta; aparecem no texto como fase do processo.

## 1. Emendas de relator (RP 9), o "orçamento secreto"

**Etiqueta: Não resolvido.** Dinheiro público recuperado: **não confirmado** (`null`).

### O que está decidido

- STF, Plenário, 19/12/2022 (ADPF 854, julgada com as ADPFs 850, 851 e 1.014): declarou incompatíveis com a Constituição as
  práticas do "orçamento secreto". A decisão trata do mecanismo orçamentário; não é decisão de responsabilidade de pessoas.
  Fonte: https://legis.senado.leg.br/norma/36822451/publicacao/37033963 (ementa: "elevadas quantias (mais de R$ 53 bilhões
  entre 2020 e 2022) vinculadas a finalidades genéricas, vagas e ambíguas").

### O que está pendente

- A ADPF 854 segue em fase de execução sob a relatoria do ministro Flávio Dino. O andamento no portal do STF tem petições até
  05/10/2026 ("05/10/2026 | Petição | ADVOGADO-GERAL DA UNIÃO - Petição: 125282").
  Fonte: https://portal.stf.jus.br/processos/detalhe.asp?incidente=6199750
- Identificação de quem indicou as emendas: na decisão de 09/09/2026, o relator registra que "o Poder Executivo reportou o
  registro de 8.340 empenhos com apoiamento identificado, os quais somavam R$ 8.471.048.174,10, importando 18,18% do valor total
  dos empenhos de Emendas de Relator (RP9) do período, que foi de R$ 46.593.741.196,42". O Legislativo informou outra base
  ("9.580 empenhos apoiados até 24/05/2026 (78,8% do total das emendas), totalizando R$ 10.143.789.470 (87,3% do valor total)",
  calculada só sobre restos a pagar), e o relator anotou "divergência significativa entre os dados apresentados pelos Poderes
  Legislativo e Executivo, circunstância que comprometia a adequada compreensão do grau de rastreabilidade das 'emendas de
  relator' (RP 9) relativas aos exercícios de 2020 a 2022".
  Fonte: STF, decisão monocrática de 09/09/2026, https://portal.stf.jus.br/processos/downloadPeca.asp?id=15390221646&ext=.pdf
- Na mesma decisão, auditorias do DENASUS sobre contas de emendas parlamentares (de vários tipos, não só RP 9) apontam
  "R$ 8.421.955,61 em recursos com aplicação irregular ou não comprovada" em 25 auditorias, com "proposição de devolução e/ou
  recomposição de valores ao erário ou ao fundo de saúde". É proposta de devolução, não valor devolvido, e não é específica de
  RP 9.

### Fato relacionado, fora da etiqueta

- STF, Primeira Turma, 17/03/2026, Ação Penal 2.670: condenou por corrupção passiva os deputados federais Josimar Cunha
  Rodrigues e Gildenemir de Lima Sousa, o ex-deputado João Bosco da Costa e mais quatro réus, por cobrança de propina para
  destinar emendas parlamentares ao município de São José de Ribamar (MA) em 2020. Certidão de julgamento no andamento: "a
  Primeira Turma, por unanimidade, julgou parcialmente procedente a pretensão punitiva contida na denúncia da Ação Penal n.
  2.670"; danos morais coletivos fixados em "RS 1.667.750,00".
  Fontes: https://noticias.stf.jus.br/postsnoticias/stf-condena-sete-reus-por-desvio-de-emendas-parlamentares-destinadas-a-municipio-do-maranhao/
  e https://portal.stf.jus.br/processos/detalhe.asp?incidente=7228118
- **Não é decisão definitiva:** o andamento registra "25/05/2026 | Opostos embargos de declaração" e, até 10/09/2026, nenhum
  julgamento dos embargos nem certidão de trânsito em julgado.
- **Não confirmado que sejam emendas RP 9:** o texto lido descreve "emendas parlamentares de saúde" sem dizer o tipo. Por isso o
  caso não entra na etiqueta do cartão RP 9. Se um documento oficial mostrar que eram emendas de relator, o caso passa a ser
  "condenação não definitiva ligada a RP 9", e a etiqueta continua "Não resolvido" até o trânsito em julgado.

### Não confirmado

- Valor de dinheiro de emendas RP 9 já devolvido aos cofres públicos: nenhum órgão oficial publicou esse número nas fontes lidas.
  A AGU tem um grupo de trabalho de responsabilização e recuperação criado por ordem da ADPF 854, mas os relatórios dele não foram
  lidos nesta pesquisa (os pedidos do relator citados pela imprensa tratam de "emendas Pix", não de RP 9).
- Acórdão do TCU com condenação em Tomada de Contas Especial ligada a emendas RP 9: nenhum encontrado.

## 2. Pagamentos indevidos no Auxílio Emergencial

**Etiqueta: Não resolvido.** Dinheiro recuperado com fonte oficial: **R$ 1.073.930.000** (posição de outubro de 2021, soma
literal de duas frases do TCU; mínimo sem sobreposição possível: R$ 1,03 bilhão).

### O que está decidido

- TCU, Acórdão 3.142/2021-Plenário (TC 016.827/2020-1, sessão de 15/12/2021): concluiu o acompanhamento com determinações e
  recomendações e arquivou o processo. É um acompanhamento de política pública; o acórdão não aponta nem pune responsáveis pelos
  pagamentos indevidos estimados (R$ 45,7 bilhões, estimativa estatística de erro de focalização).
  Fonte: https://portal.tcu.gov.br/data/files/05/E0/04/FC/B9D038102DFE0FF7F18818A8/062_acordao_tcu_3142_2021.pdf
  - Parágrafo 193: "Não se verificou o controle do Ministério da Cidadania no pós-pagamento do Auxílio Emergencial, tampouco
    ações de recuperação de valores recebidos indevidamente por beneficiários."
  - Parágrafo 195: "Imperou, portanto, a voluntariedade do beneficiário em devolver o recurso que considerou recebido
    indevidamente, sem qualquer ação coercitiva da gestão do Auxílio Emergencial."

### Dinheiro recuperado

- Mesmo acórdão, parágrafo 197 (dados do Ministério da Cidadania e da Receita Federal): "a estratégia de envio de SMS utilizada
  pelo Ministério para recuperação de valores conseguiu reaver R$ 73,93 milhões, em apuração datada de 30/9/2021, sendo R$ 31,93
  milhões via GRU e R$ 42 milhões via Darf. Foram também recuperados R$ 1 bilhão no pagamento de Darfs no ajuste da Declaração de
  Imposto de Renda/2021, além de terem sido gerados Darfs ainda não pagos da ordem de R$ 1,9 bilhão, conforme dados recebidos da
  Receita Federal em 7/10/2021."
- Valor gravado no JSON: R$ 73,93 milhões mais R$ 1 bilhão = R$ 1.073.930.000. O texto diz "também", mas não diz se os R$ 42
  milhões via Darf estão dentro do R$ 1 bilhão; sem essa parcela, o mínimo é R$ 1.031.930.000. Os R$ 1,9 bilhão em Darfs "ainda
  não pagos" não entram.
- Fora da conta, por não ser pagamento indevido recuperado: "devolução de valores da Caixa diretamente ao Ministério da Cidadania
  por falta de movimentação de recursos nas contas", que "até março de 2021 alcançou o montante de R$ 3.786.386.021,00"
  (parágrafo 49). É dinheiro que não chegou a ser sacado.

### O que está pendente

- Cobrança administrativa do MDS, aberta em 2025: "Ao todo, 177,4 mil famílias têm valores a ressarcir e já foram notificadas. O
  valor a ser restituído para a União totaliza R$ 478,8 milhões." (MDS, 07/10/2025, cópia do Internet Archive de 07/10/2025)
  https://www.gov.br/mds/pt-br/noticias-e-conteudos/desenvolvimento-social/noticias-desenvolvimento-social/auxilio-emergencial-pago-indevidamente-177-mil-familias-devem-devolver-r-478-milhoes
- Prazo reaberto: "quem foi notificado tem até o dia 11 de janeiro para ressarcir a União" (MDS, 24/11/2025, cópia do Internet
  Archive de 24/11/2025); depois disso, a nota fala em inscrição na Dívida Ativa da União.
  https://www.gov.br/mds/pt-br/noticias-e-conteudos/desenvolvimento-social/noticias-desenvolvimento-social/mds-reabre-prazo-para-regularizacao-de-debitos-do-auxilio-emergencial

### Não confirmado

- Quanto a cobrança de 2025 já arrecadou: nenhuma nota oficial com o valor pago foi encontrada.
- Total oficial devolvido depois de outubro de 2021. A imprensa cita uma nota do Ministério da Cidadania de dezembro de 2021 com
  "R$ 6,9 bilhões em devoluções", mas, pelo que a própria imprensa descreve, o número soma valores não movimentados nas contas; a
  página oficial não abriu (gov.br respondeu 404 e o Internet Archive limitou as consultas). Não usado.
- Condenações criminais definitivas de fraudadores do benefício: houve operações da PF e ações do MPF contra fraudes individuais,
  mas nenhuma lista oficial consolidada de condenações com trânsito em julgado foi encontrada. Mesmo que existam, elas tratam de
  fraudes caso a caso, não da estimativa de R$ 45,7 bilhões, que não aponta responsáveis.

## 3. Sonegação e lavagem no setor de combustíveis (Operação Carbono Oculto)

**Etiqueta: Não resolvido.** Dinheiro público recuperado: **não confirmado** (`null`).

### O que está decidido

- Nada com caráter definitivo. A fase mais adiantada encontrada em fonte oficial é a denúncia do Ministério Público:
  "O Grupo de Atuação Especial de Combate ao Crime Organizado (GAECO) ofereceu denúncia, em 18 de agosto, contra 16 homens
  envolvidos em um esquema de adulteração de combustíveis, falsidades documentais, fraudes contra o consumo, crimes fiscais e
  conexão com outras organizações criminosas independentes." e "os denunciados integraram, promoveram e financiaram,
  pessoalmente, organização criminosa para desviar metanol, adulterar combustível e praticar lavagem de dinheiro."
  Fonte: MPSP, notícia de 26/08/2026 (lida pelo serviço Firecrawl, porque o site do MPSP responde 403 a acesso automático e o
  Internet Archive não tinha cópia),
  https://www.mpsp.mp.br/w/gaeco-denuncia-16-alvos-da-operacao-carbono-oculto-por-adulteracao-de-combustivel-e-lavagem-de-dinheiro
- A mesma nota diz que a operação foi "deflagrada no dia 18 de agosto de 2025"; a Receita Federal dá 28/08/2025, na nota da
  operação e na nota de um ano depois ("completa um ano neste dia 28 de agosto"). A data usada no projeto continua 28/08/2025.

### O que está pendente

- Recebimento da denúncia pela Justiça, vara e número do processo: não encontrados em fonte oficial.
- Fases seguintes da investigação, ainda sem decisão de mérito:
  - Receita Federal, 28/05/2026, Operação Fluxo Oculto: "Trata-se da 2ª fase da Operação Carbono Oculto"; "Juntas, as seis
    fintechs movimentaram mais de R$ 26 bilhões entre 2022 e 2025"; num esquema com nafta, "os prejuízos aos cofres públicos
    atingem a marca de R$ 200 milhões em tributos supostamente sonegados em dois anos". (Página restrita no gov.br; lida na cópia
    do Internet Archive.)
    https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/maio/operacao-fluxo-oculto-receita-federal-gaeco-sp-e-orgaos-parceiros-ampliam-investigacoes-sobre-organizacao-criminosa-atuante-no-setor-de-combustiveis
  - Receita Federal, 28/08/2026, Operação Bomba Oculta: "um total de1.283 CNPJs e 228 Inscrições Estaduais serão tornados
    inaptos" (sic, sem espaço no original); a operação "dá prosseguimento ao desmantelamento do esquema [...] que veio à tona com a
    Operação Carbono Oculto, que completa um ano neste dia 28 de agosto". É medida cadastral, não punição definitiva.
    https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2026/agosto/operacao-bomba-oculta-fecha-o-cerco-a-postos-de-combustiveis-clandestinos

### Dinheiro

- Lançado, não recuperado: "A Receita Federal já constituiu créditos tributários federais de um total de mais de R$ 8,67
  bilhões em pessoas e empresas integrantes do esquema." (Receita Federal, 28/08/2025). Crédito constituído é cobrança, ainda
  sujeita a defesa administrativa e judicial.
- Bloqueio pedido pela PGFN em 28/08/2025: "mais de R$ 1 bilhão em bens" (já registrado em `scandals.json`). Bloqueio não é
  recuperação.
- Valor efetivamente pago, parcelado ou recuperado: nenhum órgão oficial publicou nas fontes lidas.

### Não confirmado

- Uma segunda denúncia do MPSP (lavagem por meio de usinas de açúcar, setembro de 2026) aparece só na imprensa; a nota oficial não
  foi encontrada.
- Resultado da cobrança de 61 empresas do setor apontadas como possíveis devedoras contumazes (Receita e PGFN, 2026): aparece na
  imprensa, sem página oficial aberta, e não é específica da Carbono Oculto.

## 4. Descontos associativos não autorizados em benefícios do INSS

**Etiqueta: Não resolvido.** Dinheiro público recuperado das entidades ou dos responsáveis: **não confirmado** (`null`).

Base: a pesquisa do caso de 02/10/2026 (`docs/research/BRASIL-IMPOSTO_RESEARCH_case-inss-deductions_2026-10-02.md`), conferida de
novo hoje nos pontos abaixo.

### O que está decidido

- A devolução aos aposentados. STF, ADPF 1.236: acordo homologado em 02/07/2025 e referendado pelo Plenário (sessão virtual de 06
  a 13/03/2026). O andamento registra: "Certifico que, até a data de 17 de abril de 2026, não foi interposto recurso contra o
  acórdão publicado em 10 de abril de 2026." Última movimentação vista hoje: 19/05/2026 (ofício de uma vara de Anápolis/GO).
  Fonte: https://portal.stf.jus.br/processos/detalhe.asp?incidente=7287062
- Pago pela União aos beneficiários pela ação 00XK ("Ressarcimento aos Beneficiários do Regime Geral de Previdência Social por
  Descontos Indevidos"): R$ 3.654.802.192,32 de julho de 2025 a setembro de 2026 (Portal da Transparência, soma feita na pesquisa
  de 02/10/2026). É dinheiro público que **sai** para cobrir descontos privados; não é dinheiro recuperado.
- Afastamentos e exonerações (presidente do INSS exonerado em 23/04/2025; ministro exonerado a pedido em 02/05/2025; 12 servidores
  afastados de forma cautelar) não são punição definitiva: o próprio ato de afastamento é cautelar e o PAD "não findou".

### O que está pendente

- Investigação criminal no STF (relator ministro André Mendonça), ainda com diligências: "A Polícia Federal cumpriu, nesta
  terça-feira (21/7), no Distrito Federal, mandado de busca e apreensão no âmbito da Operação Sem Desconto"; "A ordem judicial foi
  expedida pelo Supremo Tribunal Federal e tem a finalidade de descapitalizar investigado apontado como um dos principais atores do
  esquema criminoso." (PF, 21/07/2026)
  https://www.gov.br/pf/pt-br/assuntos/noticias/2026/07/pf-cumpre-mandado-de-busca-e-apreensao-no-ambito-da-operacao-sem-desconto
- Denúncia: nenhuma denúncia oferecida ou recebida encontrada em fonte oficial até 05/10/2026. A imprensa fala em relatório da PF
  com 48 indiciados entregue ao STF em julho de 2026, para a PGR decidir; não há nota oficial aberta com isso, e indiciamento não
  muda a etiqueta.
- AGU contra as entidades: "Desse total, R$ 514 milhões já foram efetivamente bloqueados, por meio do Sistema de Busca de Ativos do
  Poder Judiciário (Sisbajud), além da constrição de 17 imóveis e 76 veículos." e "outros R$ 135 milhões cobrados por meio das
  ações regressivas" (AGU, 20/12/2025). Bloqueio e cobrança não são dinheiro devolvido; nenhum balanço oficial posterior foi
  encontrado hoje.
  https://www.gov.br/agu/pt-br/comunicacao/noticias/agu-ajuiza-dois-novos-lotes-de-acoes-contra-associacoes-envolvidas-em-fraudes-do-inss
- TCU: Acórdão 2.252/2026-Plenário (25/08/2026) sobrestá contas de 2023 do Ministério da Previdência até o julgamento do TC
  007.871/2025-2, cuja inspeção "apontou necessidade de citação e/ou audiência". Sem julgamento de mérito. (Texto lido na pesquisa
  de 02/10/2026; in.gov.br não respondeu a esta máquina hoje, curl com erro 92.)
- CPMI do INSS: encerrada em 28/03/2026 sem relatório final (parecer rejeitado por 19 a 12).

### Não confirmado

- Valor devolvido aos cofres públicos pelas entidades ou por pessoas investigadas.
- Resultado dos processos administrativos de responsabilização (PAR) contra entidades e do PAD avocado pela CGU.
- Relatório da PF com indiciamentos (só na imprensa).

## 5. Banco Master e as operações com o BRB

**Etiqueta: Não resolvido.** Dinheiro público recuperado: **não confirmado** (`null`).

### O que está decidido

- Banco Central: "O Banco Central decretou a liquidação extrajudicial do Banco Master S.A., do Banco Master de Investimento S.A.,
  do Banco Letsbank S.A., e da Master S.A. Corretora de Câmbio, Títulos e Valores Mobiliários, bem como Regime de Administração
  Especial Temporária (RAET) no Banco Master Múltiplo S.A., instituições integrantes do Conglomerado Master." (63ª Ata do Comef,
  19/11/2025). A liquidação encerra a atividade do banco; não é decisão de responsabilidade de pessoas.
  https://www.bcb.gov.br/content/publicacoes/atascomef/202511/Ata_63_Comef_pt.pdf
- O ato de liquidação em si (Ato do Presidente do Banco Central) não foi aberto; a ata do Comef é a fonte oficial lida.

### O que está pendente

- Investigação criminal no STF: as decisões de 14/01/2026 foram do ministro Dias Toffoli; a 9ª fase (18/06/2026) foi autorizada
  pelo ministro André Mendonça. Última fase encontrada em fonte oficial:
  - PF, 09/07/2026: "A Polícia Federal deflagrou, nesta quinta-feira (9/7), a 10ª fase da Operação Compliance Zero para apurar
    indícios de atuação coordenada em redes sociais voltada, em tese, a comprometer a credibilidade da atuação do Banco Central do
    Brasil." https://www.gov.br/pf/pt-br/assuntos/noticias/2026/07/policia-federal-deflagra-10a-fase-da-operacao-compliance-zero
  - STF, 18/06/2026 (9ª fase): "O ministro André Mendonça [...] autorizou a Polícia Federal (PF) a deflagrar a 9ª fase da
    Operação Compliance Zero, com o cumprimento de mandados de busca e apreensão e a aplicação de medidas cautelares contra
    investigados por suposto envolvimento em crimes financeiros, de lavagem de dinheiro, corrupção ativa e passiva e de
    organização criminosa relacionados ao Banco Master."
    https://noticias.stf.jus.br/postsnoticias/stf-autoriza-9a-fase-da-operacao-compliance-zero-em-sp-ba-e-df/
  - Denúncia: nenhuma denúncia oferecida ou recebida encontrada em fonte oficial até 05/10/2026. A imprensa fala em conclusão do
    inquérito principal e preparação de indiciamentos em agosto de 2026; sem nota oficial aberta.
- TCDF, 23/09/2026: "o Tribunal de Contas do Distrito Federal (TCDF) decidiu, em caráter cautelar, determinar a indisponibilidade
  de bens de ex-integrantes da alta administração do BRB"; "A medida tem por objetivo resguardar eventual ressarcimento aos cofres
  públicos"; "Além do bloqueio cautelar de bens por prazo de um ano, o Tribunal determinou a conversão do processo em Tomada de
  Contas Especial (TCE), instrumento destinado à apuração de responsabilidades e de possíveis danos ao patrimônio público." Os
  ex-dirigentes "terão um prazo de 30 dias para se manifestar". É cautelar, sem julgamento das contas.
  https://www2.tc.df.gov.br/tcdf-determina-bloqueio-de-bens-de-ex-dirigentes-do-brb/

### Dinheiro

- Nenhum valor de dinheiro público recuperado foi publicado por órgão oficial nas fontes lidas. O TCDF fala em "eventual
  ressarcimento".
- Fora da conta, por ser dinheiro privado: o FGC pagou "R$37,7 bilhões" de "R$40,4 bilhões em valor de cobertura" entre 19/01 e
  27/02/2026 (Banco Central, Relatório de Estabilidade Financeira, maio de 2026,
  https://www.bcb.gov.br/content/publicacoes/ref/202605/RELESTAB202605-refPub.pdf). O FGC é mantido pelas instituições
  financeiras.
- Fora da conta, por falta de fonte oficial: a substituição de carteiras do Master por outros ativos no BRB (a imprensa fala em
  mais de R$ 10 bilhões "liquidados ou substituídos"). Ativo substituído não é dinheiro recuperado, e o valor desses ativos é
  justamente o que está em apuração.
- Bloqueios determinados pelo STF e pelo TCDF são indisponibilidade cautelar, não recuperação.

### Não confirmado

- Ato do Presidente do Banco Central que decretou a liquidação (número e texto).
- Inquérito do Banco Central sobre a responsabilidade dos administradores do conglomerado liquidado e qualquer processo
  administrativo sancionador ligado ao caso.
- Valor de dinheiro público envolvido (continua não confirmado, como em `scandals.json`).

## Resumo

| Escândalo | Etiqueta | Decidido | Pendente | Dinheiro recuperado (fonte oficial) |
|---|---|---|---|---|
| Orçamento secreto (RP 9) | Não resolvido | STF declarou a prática inconstitucional (19/12/2022) | ADPF 854 em execução; autor da indicação identificado em 18,18% do valor de RP 9 (09/09/2026); nenhuma condenação definitiva ligada a RP 9 | não confirmado |
| Auxílio Emergencial | Não resolvido | TCU concluiu e arquivou o acompanhamento (15/12/2021), sem apontar responsáveis | cobrança do MDS a 177,4 mil famílias (R$ 478,8 milhões), prazo até 11/01/2026 | R$ 1.073.930.000 (TCU, posição de outubro de 2021) |
| Carbono Oculto | Não resolvido | nada definitivo | denúncia do MPSP contra 16 (18/08/2026), recebimento não confirmado; créditos de R$ 8,67 bi lançados | não confirmado |
| INSS | Não resolvido | devolução aos aposentados homologada pelo STF (acórdão sem recurso); R$ 3,65 bi pagos pela União | investigação no STF; ações da AGU com R$ 514 mi bloqueados; TCU sem mérito; nenhuma denúncia | não confirmado (valor pago aos aposentados é saída, não recuperação) |
| Banco Master e BRB | Não resolvido | liquidação extrajudicial pelo Banco Central (18/11/2025) | investigação no STF (10ª fase em 09/07/2026); TCE no TCDF com bloqueio cautelar (23/09/2026) | não confirmado |

## Pontos para o autor

1. **Os cinco ficam "Não resolvido" pela regra.** Nenhum dos cinco tem pessoa punida por decisão definitiva em fonte oficial. A
   etiqueta não distingue "nem denúncia ainda" (Master, INSS) de "denúncia oferecida" (Carbono Oculto); se o autor quiser essa
   diferença na tela, ela já está no campo `why`.
2. **Condenação parcial.** A regra diz "os responsáveis punidos". Se um dia só parte dos envolvidos for condenada em definitivo
   (por exemplo, um réu de uma ação e não os demais), a pesquisa recomenda manter "Não resolvido" e citar a condenação no `why`,
   para tratar todos os casos do mesmo jeito. A decisão é do autor.
3. **AP 2.670 no STF** (condenação não definitiva de deputados por propina em emendas de 2020): não entrou no cartão RP 9 porque
   o documento lido não diz que eram emendas de relator. Se o autor quiser, o próximo passo é abrir o acórdão e conferir o tipo das
   emendas.
4. **Auxílio Emergencial:** o único valor recuperado com fonte oficial é de outubro de 2021. Um número mais novo depende de pedido
   ao MDS pela Lei de Acesso à Informação (quanto a cobrança de 2025 arrecadou).

## Fontes principais

- STF, ADPF 854, decisão de 09/09/2026: https://portal.stf.jus.br/processos/downloadPeca.asp?id=15390221646&ext=.pdf
- STF, ADPF 854, andamento: https://portal.stf.jus.br/processos/detalhe.asp?incidente=6199750
- STF, AP 2.670, andamento: https://portal.stf.jus.br/processos/detalhe.asp?incidente=7228118
- TCU, Acórdão 3.142/2021-Plenário: https://portal.tcu.gov.br/data/files/05/E0/04/FC/B9D038102DFE0FF7F18818A8/062_acordao_tcu_3142_2021.pdf
- MDS, 07/10/2025 e 24/11/2025 (cópias do Internet Archive): links na seção 2
- MPSP, 26/08/2026: https://www.mpsp.mp.br/w/gaeco-denuncia-16-alvos-da-operacao-carbono-oculto-por-adulteracao-de-combustivel-e-lavagem-de-dinheiro
- Receita Federal, 28/08/2025, 28/05/2026 e 28/08/2026: links na seção 3
- STF, ADPF 1.236, andamento: https://portal.stf.jus.br/processos/detalhe.asp?incidente=7287062
- PF, 21/07/2026 (Sem Desconto) e 09/07/2026 (Compliance Zero): links nas seções 4 e 5
- Banco Central, 63ª Ata do Comef: https://www.bcb.gov.br/content/publicacoes/atascomef/202511/Ata_63_Comef_pt.pdf
- TCDF, 23/09/2026: https://www2.tc.df.gov.br/tcdf-determina-bloqueio-de-bens-de-ex-dirigentes-do-brb/
