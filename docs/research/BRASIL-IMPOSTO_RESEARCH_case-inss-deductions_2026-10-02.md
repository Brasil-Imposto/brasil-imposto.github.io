# Caso: descontos associativos não autorizados em benefícios do INSS

Pesquisa de 2026-10-02 para a página de caso (D48, GD40, GD23, GD25). Só fontes oficiais; a imprensa serviu apenas de pista.
Dados estruturados: `data/cases/inss-deductions.json`.

Nota de acesso: em 2026-10-02 as notícias do gov.br (CGU, INSS, AGU, PF, Previdência) respondem com "Conteúdo Restrito"; as páginas
que não são notícia abrem normalmente. A lista de notícias do Ministério da Previdência de julho de 2026 traz o título
"Ministério da Previdência Social adequa canais de comunicação para o período de defeso eleitoral", o que sugere que as notícias
foram recolhidas durante o período eleitoral (hipótese, não confirmada).
As notícias do gov.br citadas aqui foram lidas na cópia do Internet Archive (`web.archive.org/web/<data>/...`) indicada em cada
fonte (campo `archive_url` no JSON); o link de referência é o original do gov.br. DOU, Planalto, STF, TCU, Senado, eaud da CGU e
Portal da Transparência foram lidos no original.

## 1. O que aconteceu

Entidades associativas e sindicais tinham Acordos de Cooperação Técnica (ACTs) com o INSS que permitiam descontar mensalidades
direto na folha de aposentados e pensionistas. Segundo a CGU, esses acordos "permitiam que as entidades realizassem descontos
de mensalidades associativas diretamente na folha de pagamento de aposentados e pensionistas do INSS, sem a autorização dos
beneficiários". Numa auditoria publicada em 23/04/2025, a CGU entrevistou 1.273 beneficiários nas 27 UFs: "1.242 beneficiários
entrevistados (97,6%) informaram não ter autorizado o desconto, e 1.221 (95,9%) afirmaram não participar de associação". Os
descontos tinham saído "de R$ 536,3 milhões em 2021 a R$ 1,3 bilhão em 2023, podendo alcançar R$ 2,6 bilhões em 2024". Em
23/04/2025 a CGU e a Polícia Federal deflagraram a Operação Sem Desconto, "com o objetivo de combater um esquema nacional de
descontos associativos não autorizados em aposentadorias e pensões" (palavras da CGU), com 211 mandados de busca, sequestro de
bens de "mais de R$ 1 bilhão" e o afastamento de "seis servidores públicos". Depois, a União e o INSS fecharam com o MPF, a DPU e
a OAB um acordo homologado pelo STF (ADPF 1.236, 02/07/2025) para devolver aos beneficiários, pela via administrativa e com
correção, os descontos "realizados entre março de 2020 e março de 2025", pagos com crédito extraordinário do orçamento federal.

Fontes: CGU, notícias de 23/04/2025 (duas) e Relatório de Auditoria nº 1675291; STF, ADPF 1.236 (decisão de 02/07/2025).

## 2. Dinheiro, separando público e privado

Regra GD40: o dinheiro descontado era **privado** (saiu do benefício de cada aposentado e foi repassado às entidades). O dinheiro
que a União usa para devolver é **público** (crédito extraordinário no orçamento do INSS). O que a AGU bloqueia ou cobra das
entidades é dinheiro que pode **voltar** ao poder público depois.

### 2.1 Quanto foi descontado dos beneficiários (dinheiro privado)

| Período | Valor | Órgão e documento | Frase que sustenta |
|---|---|---|---|
| 2016 | R$ 413,2 mi | CGU, Relatório de Auditoria nº 1675291 (publicado em 23/04/2025), Gráfico 1, p. 12 | rótulo do gráfico "Total dos Descontos" (em R$ milhões) |
| 2017 | R$ 460,4 mi | idem | idem |
| 2018 | R$ 617,4 mi | idem | idem |
| 2019 | R$ 604,6 mi | idem | idem |
| 2020 | R$ 510,9 mi | idem | idem |
| 2021 | R$ 536,3 mi | idem | "saindo de R$ 536,3 milhões em 2021 para R$ 1,3 bilhão em 2023" |
| 2022 | R$ 706,2 mi | idem | rótulo do gráfico |
| 2023 | R$ 1.299,8 mi | idem | "R$ 1,3 bilhão em 2023" |
| 2024 (estimativa) | R$ 2.637,2 mi | idem | "com a possibilidade de alcançar R$ 2,6 bilhões até o final de 2024, se os descontos realizados em maio de 2024 permanecerem estáveis" |
| 2019 a 2024 | R$ 6,3 bi (estimado) | CGU e PF, notícias de 23/04/2025 | "as entidades cobraram de aposentados e pensionistas o valor estimado de R$ 6,3 bilhões, no período entre 2019 e 2024" |

Conferências e ressalvas:
- A soma dos rótulos do Gráfico 1 de 2019 a 2024 dá R$ 6.295,0 milhões, o que bate com os "R$ 6,3 bilhões" da CGU e da PF.
  Os valores foram lidos no gráfico renderizado da página 12 do PDF (conferido a olho) e no texto extraído.
- **R$ 6,3 bi é o total dos descontos associativos, não o total comprovado como não autorizado.** O que a CGU mediu sobre
  autorização foi a amostra: "1.242 beneficiários entrevistados (97,6%) informaram não ter autorizado o desconto".
- A própria CGU diz que os valores estão **subestimados**: nota 3 do relatório, "Os valores e quantidades calculados a partir da
  Maciça estão subestimados em aproximadamente 20% devido à base compartilhada pelo INSS não contemplar as rubricas em sua
  integralidade".
- 2024 é estimativa (maio de 2024 repetido até dezembro). A CGU também fala em "6 milhões de aposentados e pensionistas" que
  "podem ter sido lesados" (notícia de 23/04/2025) e num "estoque" de "7,7 milhões de beneficiários" com desconto (relatório, p. 34).
- O acordo de devolução cobre os descontos "realizados entre março de 2020 e março de 2025" (STF, ADPF 1.236, decisão de
  02/07/2025), não todo o período 2016 a 2024.

### 2.2 Quanto já foi devolvido aos beneficiários, e por quem

| Data de referência | Valor | Beneficiários | Quem pagou | Fonte e frase |
|---|---|---|---|---|
| 20/12/2025 | R$ 2,74 bi | "mais de 4 milhões" | INSS (União) | AGU, notícia de 20/12/2025: "o INSS já ressarciu R$ 2,74 bilhões a mais de 4 milhões de beneficiários que contestaram os descontos" |
| 01/04/2026 | R$ 3.011.377.439,58 | 4.431.470 aderiram ao acordo | Governo Federal, via acordo coordenado pelo INSS | INSS, notícia de 01/04/2026: "O Governo Federal já devolveu R$ 3.011.377439, 58 a aposentados e pensionistas" e "4.431.470 beneficiários aderiram ao acordo" |
| 30/09/2026 | R$ 3.654.802.192,32 | não informado | INSS, ação orçamentária 00XK | Portal da Transparência (CGU), execução da despesa de jul/2025 a set/2026; ver 2.3 |

- Quem paga é a União, pelo INSS, com dinheiro do orçamento (crédito extraordinário). As entidades não pagam diretamente nessa
  via; a União depois cobra delas por ação de regresso (AGU, item 2.4). O acordo prevê que a entidade tem 15 dias úteis para
  responder à contestação; se não responde ou apresenta documento irregular, o beneficiário pode aderir (INSS, 01/04/2026).
- O valor de 01/04/2026 está escrito no original como "R$ 3.011.377439, 58" (separadores trocados); lido como
  R$ 3.011.377.439,58.
- Um número mais recente ("R$ 3,26 bilhões a 4,8 milhões") circula só na imprensa, não confirmado em fonte oficial. As notícias do
  gov.br de julho a outubro de 2026 não estavam acessíveis (ver a nota de acesso).

### 2.3 Quanto saiu do dinheiro público

| Ato | Data | Valor | Frase do documento |
|---|---|---|---|
| Medida Provisória nº 1.306 (Lula, Simone Tebet) | 16/07/2025 (DOU 17/07/2025) | R$ 3.312.824.545,00 | "Fica aberto crédito extraordinário, em favor do Ministério da Previdência Social, no valor de R$ 3.312.824.545,00" (ação 00XK, "Ressarcimento aos Beneficiários do Regime Geral de Previdência Social por Descontos Indevidos") |
| Medida Provisória nº 1.378 (Lula, Bruno Moretti) | 20/07/2026 (DOU 21/07/2026) | R$ 547.000.000,00 | "Fica aberto crédito extraordinário [...] no valor de R$ 547.000.000,00"; fonte: superávit financeiro de 2025 do INSS (EXM nº 1.689/2026) |
| **Total aberto** | | **R$ 3.859.824.545,00** | soma dos dois atos |

- A MP 1.306 "perdeu sua vigência em novembro de 2025 sem ter sido convertida em lei" (EXM nº 1.689/2026; Congresso: "SEM
  EFICÁCIA"). O empenho de 2025 já tinha sido feito e foi pago (abaixo).
- A MP 1.378 decorre "da ampliação, pelo Supremo Tribunal Federal (STF), em abril de 2026, do alcance do acordo homologado" (EXM).
- O STF determinou que essa despesa fique fora do limite de gastos e da meta fiscal: "a dotação orçamentária destinada ao
  cumprimento das obrigações objeto do Acordo Interinstitucional homologado seja excluída dos limites referidos no art. 3º da Lei
  Complementar nº 200/23 [...] bem como para fins de verificação do cumprimento da meta" (despacho de 09/07/2025; referendado pelo
  Plenário na sessão virtual de 06 a 13/03/2026).

**Execução (quanto foi de fato pago), ação 00XK, Portal da Transparência (CGU), arquivos mensais de execução da despesa:**

| Mês | Empenhado | Pago no mês (inclui restos a pagar pagos) | Acumulado |
|---|---|---|---|
| jul/2025 | R$ 3.312.824.545,00 | R$ 908,40 mi | R$ 908,40 mi |
| ago/2025 | | R$ 393,05 mi | R$ 1.301,45 mi |
| set/2025 | | R$ 411,74 mi | R$ 1.713,20 mi |
| out/2025 | | R$ 712,28 mi | R$ 2.425,48 mi |
| nov/2025 | | R$ 272,02 mi | R$ 2.697,51 mi |
| dez/2025 | | R$ 137,11 mi | R$ 2.834,61 mi |
| jan/2026 | | R$ 83,09 mi | R$ 2.917,70 mi |
| fev/2026 | | R$ 45,06 mi | R$ 2.962,76 mi |
| mar/2026 | | R$ 39,78 mi | R$ 3.002,54 mi |
| abr/2026 | | R$ 59,31 mi | R$ 3.061,85 mi |
| mai/2026 | | R$ 57,38 mi | R$ 3.119,23 mi |
| jun/2026 | | R$ 91,68 mi | R$ 3.210,91 mi |
| jul/2026 | | R$ 11,58 mi | R$ 3.222,50 mi |
| ago/2026 | R$ 547.000.000,00 | R$ 318,31 mi | R$ 3.540,81 mi |
| set/2026 | | R$ 114,00 mi | **R$ 3.654,80 mi** |

- Pago em 2025: R$ 2.834.611.941,12. Pago em 2026 até setembro: R$ 820.190.251,20. Total: **R$ 3.654.802.192,32**.
- Conferências (invariante externo): até março de 2026 o Portal soma R$ 3.002,5 mi; o INSS informou R$ 3.011,4 mi devolvidos em
  01/04/2026. Até novembro de 2025 o Portal soma R$ 2.697,5 mi e até dezembro R$ 2.834,6 mi; a AGU informou R$ 2,74 bi em
  20/12/2025. Os restos a pagar pagos em 2026 (R$ 478,3 mi) igualam o empenho de 2025 menos o pago em 2025, ou seja, o crédito da
  MP 1.306 foi usado por inteiro. Nenhuma outra ação orçamentária do arquivo de agosto de 2026 traz "descontos indevidos" no nome.
- O arquivo de setembro de 2026 foi baixado em 02/10/2026 e pode ser revisto pelo Portal.

### 2.4 Bloqueado ou cobrado das entidades (dinheiro que pode voltar)

| Data | Valor | O que é | Fonte e frase |
|---|---|---|---|
| 23/04/2025 | mais de R$ 1 bi | ordens judiciais de sequestro de bens na deflagração | CGU e PF, 23/04/2025: "ordens de sequestro de bens no valor de mais de R$ 1 bilhão" |
| 08/05/2025 | R$ 2,56 bi pedidos | 1ª ação cautelar da AGU (12 entidades e dirigentes) | AGU, 08/05/2025: "bloqueio de bens móveis e imóveis na ordem de R$ 2,56 bilhões contra 12 entidades associativas" |
| 12/06/2025 | R$ 2,8 bi | bloqueio deferido pela Justiça Federal nas 15 ações desse lote | AGU, 12/06/2025: "obteve o bloqueio de R$ 2,8 bilhões em bens e ativos financeiros de associações, empresas e pessoas físicas" |
| 17/06/2025 | cerca de R$ 12 mi | sequestro de cinco imóveis (3ª Vara Federal de Sergipe) | PF, 17/06/2025: "o sequestro de cinco imóveis vinculados aos investigados, avaliados em aproximadamente R$ 12 milhões" |
| 20/12/2025 | R$ 6,6 bi pedidos; R$ 4,4 bi deferidos; **R$ 514 mi efetivamente bloqueados** | saldo de 37 ações cautelares | AGU, 20/12/2025: "a AGU requereu o bloqueio de R$ 6,6 bilhões [...] Decisões liminares já determinaram bloqueio de R$ 4,4 bilhões. Desse total, R$ 514 milhões já foram efetivamente bloqueados, por meio do Sistema de Busca de Ativos do Poder Judiciário (Sisbajud), além da constrição de 17 imóveis e 76 veículos" |
| 20/12/2025 | R$ 135 mi cobrados | ações regressivas (4º lote, 8 entidades) para reaver o que o INSS já pagou | AGU, 20/12/2025: "Somam-se a isso outros R$ 135 milhões cobrados por meio das ações regressivas do quarto lote" |

- "Bloqueado" não é "recuperado": é dinheiro indisponível por decisão provisória. Nenhuma fonte oficial encontrada informa valor já
  **devolvido aos cofres públicos** pelas entidades até 02/10/2026 (ver "O que não foi confirmado").
- Os valores de bloqueio se sobrepõem (o lote de R$ 2,8 bi está dentro dos R$ 4,4 bi); não somar as linhas.

## 3. "Retorno" em três linhas (D48, GD25)

1. **Custo (dinheiro público):** R$ 3.859.824.545,00 abertos em créditos extraordinários (MP 1.306/2025 e MP 1.378/2026); pagos
   pela ação 00XK de julho de 2025 a setembro de 2026: **R$ 3.654.802.192,32** (Portal da Transparência). Fora do limite de gastos
   e da meta fiscal por decisão do STF.
2. **Dinheiro que entra e sai depois:** sai o ressarcimento acima; pode voltar o que a AGU cobra das entidades: **R$ 514 milhões
   efetivamente bloqueados** (de R$ 4,4 bi em bloqueios deferidos por liminar) e **R$ 135 milhões** cobrados em ações regressivas
   (AGU, 20/12/2025). Nenhuma devolução efetiva aos cofres públicos foi encontrada em fonte oficial até 02/10/2026.
3. **Uso medido:** **4.431.470** beneficiários aderiram ao acordo e receberam **R$ 3.011.377.439,58** até 01/04/2026 (INSS). A CGU
   estimava "6 milhões" de possíveis lesados (23/04/2025). Sugestão para a tela: "4,4 milhões de pessoas receberam a devolução",
   com a data.

## 4. Pessoas (GD23)

Critério aplicado: entra quem tem papel num documento oficial (decidiu, assinou pelo governo, fiscalizou ou foi alvo de decisão
oficial: exoneração, afastamento, demissão, denúncia recebida, condenação), sempre com o ato. Ficam fora, sem nome: investigados
que só aparecem em inquérito, pessoas físicas com bens bloqueados por liminar (cautelar, não é decisão de responsabilidade),
os mais de 200 nomes do parecer da CPMI (o parecer foi **rejeitado**, então não é ato da comissão), os indiciados pela PF
(indiciamento não é denúncia recebida; e o número só foi achado na imprensa) e dois gestores citados no Acórdão 2.252/2026 do
TCU só para "citação e/ou audiência" (sem decisão de mérito). Até 02/10/2026 **nenhuma denúncia recebida nem condenação** ligada
ao caso foi encontrada em fonte oficial.

### 4.1 Decidiram ou assinaram pelo governo

| Nome | Cargo na época | Ato (número, data) | Situação jurídica (data) |
|---|---|---|---|
| Luiz Inácio Lula da Silva | Presidente da República | MP 1.306, de 16/07/2025, e MP 1.378, de 20/07/2026 (créditos de ressarcimento); autor da ADPF 1.236 | nenhuma decisão contra ligada ao caso (02/10/2026) |
| Simone Nassar Tebet | Ministra do Planejamento e Orçamento | coassina a MP 1.306/2025 | idem |
| Bruno Moretti | Ministro do Planejamento e Orçamento | coassina a MP 1.378/2026 | idem |
| Miriam Belchior | Ministra substituta da Casa Civil | Portaria nº 489, de 23/04/2025 (exonera o presidente do INSS); Portarias nº 530/2025 e 362 e 363/2026 | idem |
| Jorge Rodrigo Araújo Messias | Advogado-Geral da União | assina o Acordo Interinstitucional pela União (STF, ADPF 1.236, decisão de 02/07/2025); ações cautelares e regressivas | idem |
| Wolney Queiroz Maciel | Ministro da Previdência Social | assina o Acordo Interinstitucional pela União (02/07/2025) | contas de 2023 do MPS sobrestadas pelo TCU até o julgamento do TC 007.871/2025-2 (Acórdão 2.252/2026, 25/08/2026); sem julgamento de mérito |
| Gilberto Waller Júnior | Presidente do INSS (30/04/2025 a 13/04/2026) | assina o Acordo pelo INSS; Portarias PRES/INSS de afastamento cautelar (nº 736/2025 e seguintes) | nenhuma decisão contra ligada ao caso |
| Adriana Maia Venturini | Procuradora-Geral Federal | assina o Acordo pelo INSS | idem |
| Débora Aparecida Andrade Floriano | Presidente substituta do INSS | Despacho Decisório PRES/INSS nº 65, de 28/04/2025 (suspende ACTs, repasses e descontos) | idem |
| Ana Cristina Viana Silveira | Presidente do INSS (desde 13/04/2026) | Portarias PRES/INSS de prorrogação dos afastamentos (nº 952/2026 a 1.838/2026) | idem |

### 4.2 Fiscalizaram ou julgaram

| Nome | Cargo | Ato | Fonte |
|---|---|---|---|
| Vinícius Marques de Carvalho | Ministro da CGU | apresentou a Operação Sem Desconto e o relatório da CGU (23/04/2025) | CGU, notícia de 23/04/2025 |
| Andrei Rodrigues | Diretor-Geral da PF | participou da apresentação da operação (23/04/2025) | idem |
| Aroldo Cedraz | Ministro do TCU, relator do TC 032.069/2023-5 | Acórdãos 1.115/2024, 1.019/2025 e 2.538/2025-Plenário | TCU |
| Odair Cunha | Ministro do TCU, relator do TC 007.871/2025-2 | inspeção "voltada à responsabilização dos envolvidos" (citada no Acórdão 2.252/2026) | DOU, Ata 32/2026 do TCU |
| Dias Toffoli | Ministro do STF, relator da ADPF 1.236 | homologação do acordo (02/07/2025) e despacho de 09/07/2025 | STF |
| André Mendonça | Ministro do STF | relator dos procedimentos que autorizaram mandados da operação | CGU, notícia de 18/12/2025 |
| Paulo Gustavo Gonet Branco | Procurador-Geral da República | assina o Acordo pelo MPF | STF, decisão de 02/07/2025 |
| Nicolao Dino | Procurador Federal dos Direitos do Cidadão | idem | idem |
| Anselmo Henrique Cordeiro Lopes, Elisandra de Oliveira Olímpio, Fabiano de Moraes | Procuradores da República | idem | idem |
| Leonardo Cardoso de Magalhães | Defensor Público-Geral Federal | assina o Acordo pela DPU | idem |
| José Alberto Ribeiro Simonetti Cabral | Presidente do Conselho Federal da OAB | assina o Acordo pelo CFOAB (não é governo) | idem |
| Carlos Viana | Senador (Podemos-MG), presidente da CPMI | eleito presidente em 20/08/2025; encerrou os trabalhos em 28/03/2026 | Agência Senado |
| Alfredo Gaspar | Deputado federal (União-AL), relator da CPMI | parecer rejeitado por 19 a 12 em 28/03/2026 | Agência Senado; partido na Câmara: UNIÃO até 29/04/2026, depois PL |

### 4.3 Alvo de decisão oficial (exoneração ou afastamento)

| Nome | Cargo na época | Ato | Situação jurídica (data) |
|---|---|---|---|
| Alessandro Antonio Stefanutto | Presidente do INSS | exonerado pela Portaria Casa Civil nº 489, de 23/04/2025 (dia da operação; o ato não traz motivo) | sem denúncia recebida nem condenação em fonte oficial (02/10/2026) |
| Carlos Roberto Lupi | Ministro da Previdência Social | exonerado **a pedido**, Decreto de 02/05/2025 | contas de 2023 do MPS sobrestadas pelo TCU (Acórdão 2.252/2026); sem julgamento de mérito |
| 12 servidores do INSS (nomes no JSON) | Técnicos e analistas do Seguro Social | afastamento cautelar por Portarias PRES/INSS que citam a Operação Sem Desconto e o PAD "instaurado e avocado pela CGU" que "não findou" | afastamento cautelar sem prejuízo da remuneração, renovado a cada 60 dias; **não é punição** |

Os 12 afastamentos (portaria inicial, última prorrogação encontrada):
Geovani Batista Spiecker, Reinaldo Carlos Barroso de Almeida, Vanderlei Barbosa dos Santos e Jucimar Fonseca da Silva (nº 736, de
25/07/2025; nº 1.769, de 15/09/2026); André Paulo Félix Fidelis (nº 1.383, de 26/09/2025; nº 1.769/2026); Alan do Nascimento Santos
e Sandra Helena Lima do Nascimento (nº 544, de 17/03/2026; nº 1.768, de 14/09/2026); Francisco Assis Santos Mano Barreto (nº 544/2026;
nenhuma prorrogação encontrada depois); Marcos de Brito Campos Junior e Rogerio Soares de Souza (nº 261, de 30/01/2026; nº 1.553, de
04/08/2026); Everaldo Felício de Macedo Junior (nº 1.037, de 27/05/2026; nº 1.837, de 24/09/2026); Juliana Maria Dias Peixoto
(nº 1.498, de 28/07/2026; nº 1.838, de 24/09/2026).

**Ponto para o autor (D51, risco jurídico):** o critério GD23 inclui "afastamento", mas aqui é afastamento **cautelar** de
servidores de carreira, sem decisão de mérito. Recomendação do agente: na tela, mostrar o número (12) e o ato; os nomes só no dado,
até haver decisão de mérito do PAD. A decisão é do autor.

## 5. Quem governava em cada período do caso

Período do caso: o relatório da CGU cobre descontos de 2016 a maio de 2024, a PF e a CGU falam de 2019 a 2024, e o acordo de
devolução cobre março de 2020 a março de 2025. A tabela começa em 2019 (início da série de R$ 6,3 bi) e vai até hoje. Datas de
início e fim são as do ato no Diário Oficial (data do ato; publicação entre parênteses quando diferente). Partido: o registrado na
fonte oficial indicada; quando não há fonte oficial, está escrito.

### Presidente da República

| Nome | Início | Fim | Partido na época | Fonte |
|---|---|---|---|---|
| Jair Messias Bolsonaro | 01/01/2019 | 01/01/2023 | PSL na eleição de 2018 (TSE); sem partido de 19/11/2019 a 30/11/2021; PL a partir de 30/11/2021 | `data/politicians/union.json` (TSE, consulta_cand 2018 e 2022; datas de filiação pela Agência Brasil) |
| Luiz Inácio Lula da Silva | 01/01/2023 | no cargo | PT (eleição de 2022, TSE) | `data/politicians/union.json` |

### Ministro responsável pela Previdência

| Nome | Cargo | Início | Fim | Partido na época | Fonte |
|---|---|---|---|---|---|
| Paulo Guedes | Ministro da Economia (a Previdência era uma secretaria especial desse ministério) | 01/01/2019 | 27/07/2021 (para a Previdência) | sem registro na fonte | `union.json`; MP 1.058/2021 criou o Ministério do Trabalho e Previdência |
| Rogério Simonetti Marinho | Secretário Especial de Previdência e Trabalho (não ministro) | Decreto de 04/01/2019 | fev/2020 | não verificado em fonte oficial | DOU, Decreto de 04/01/2019 |
| Bruno Bianco Leal | Secretário Especial de Previdência e Trabalho (não ministro) | Decreto de 13/02/2020 (DOU 14/02/2020) | jul/2021 | não verificado | DOU, Decreto de 13/02/2020 |
| Onyx Dornelles Lorenzoni | Ministro do Trabalho e Previdência | Decreto de 27/07/2021 (DOU 28/07/2021) | 30/03/2022 (exonerado a pedido; saiu de 11/11/2021 a 19/11/2021 e foi renomeado) | DEM até 23/02/2022, depois UNIÃO (registro da Câmara dos Deputados) | DOU, Decretos de 27/07/2021, 11/11/2021, 19/11/2021 e 30/03/2022; Câmara, API de dados abertos |
| José Carlos Oliveira | Ministro do Trabalho e Previdência | Decreto de 30/03/2022 (DOU 31/03/2022) | Decreto de 31/12/2022 (DOU 01/01/2023) | não verificado em fonte oficial | DOU |
| Carlos Roberto Lupi | Ministro da Previdência Social | Decreto de 01/01/2023 | Decreto de 02/05/2025 (exonerado a pedido) | PDT só na imprensa, não confirmado em fonte oficial nesta pesquisa | DOU, Decretos de 01/01/2023 e 02/05/2025 |
| Wolney Queiroz Maciel | Ministro da Previdência Social | Decreto de 02/05/2025 | no cargo (assina portarias até 30/09/2026) | PDT como deputado federal de 2019 a 2023 (Câmara); em 2025, não verificado | DOU, Decreto de 02/05/2025; Portaria MPS nº 1.424/2026 |

### Presidente do INSS

| Nome | Início | Fim | Fonte (DOU) |
|---|---|---|---|
| Renato Rodrigues Vieira | Portaria Casa Civil nº 516, de 15/01/2019 (DOU 16/01/2019) | exonerado a pedido, Portaria nº 31, de 28/01/2020 | Casa Civil, Portarias de 15/01/2019 e 28/01/2020 |
| Leonardo José Rolim Guimarães | Portaria nº 33, de 28/01/2020 (DOU 29/01/2020) | 04/11/2021 (designado Secretário de Previdência, Portaria nº 1.262) | Casa Civil, Portarias de 28/01/2020 e 04/11/2021 |
| José Carlos Oliveira | Portaria nº 1.263, de 04/11/2021 (DOU 05/11/2021) | 30/03/2022 (nomeado ministro) | Casa Civil; Decretos de 30/03/2022 |
| Guilherme Gastaldello Pinheiro Serrano | Portaria nº 347, de 06/04/2022 (DOU 07/04/2022) | exonerado, Portaria nº 135, de 01/01/2023 (DOU 02/01/2023) | Casa Civil |
| Glauco André Fonseca Wamburg (interino) | Portaria nº 1.465, de 01/02/2023 (DOU 02/02/2023) | Portaria nº 2.632, de 04/07/2023 | Casa Civil |
| Alessandro Antonio Stefanutto | Portaria nº 2.633, de 04/07/2023 (DOU 05/07/2023) | exonerado, Portaria nº 489, de 23/04/2025 | Casa Civil |
| Débora Aparecida Andrade Floriano (substituta) | assina como "Presidente Substituta" em 28/04/2025 | | Despacho Decisório PRES/INSS nº 65/2025 |
| Gilberto Waller Júnior | Portaria nº 530, de 30/04/2025 | exonerado, Portaria nº 362, de 13/04/2026 | Casa Civil |
| Ana Cristina Viana Silveira | Portaria nº 363, de 13/04/2026 | no cargo (assina em 24/09/2026) | Casa Civil; Portaria PRES/INSS nº 1.837/2026 |

Lacunas sem titular nomeado nos atos encontrados: 02/01/2023 a 01/02/2023 e 23/04/2025 a 29/04/2025 (substitutos não levantados).
Presidentes do INSS e o ministro José Carlos Oliveira são servidores de carreira ou técnicos; nenhuma filiação partidária foi
procurada para eles. Para o site, a regra D39 (mesmo tratamento para todos) pede que o partido apareça só para quem a fonte
oficial registra.

## 6. Linha do tempo dos órgãos de controle

| Data | Órgão | Ato | Link |
|---|---|---|---|
| 05/06/2024 | TCU | Acórdão 1.115/2024-Plenário (TC 032.069/2023-5, relator Aroldo Cedraz, a pedido do Congresso): medida cautelar; novos descontos só com "assinatura eletrônica avançada e biometria", "bloqueio automático para todos os novos descontos" e determinação de "buscar o ressarcimento de valores descontados indevidamente" | portal.tcu.gov.br, notícia de 05/06/2024 |
| 23/04/2025 | CGU | Publica o Relatório de Auditoria nº 1675291 (entrevistas com 1.273 beneficiários) | eaud.cgu.gov.br/relatorio/1675762 |
| 23/04/2025 | PF e CGU | Operação Sem Desconto: 211 mandados de busca, 6 prisões temporárias, sequestro de bens de mais de R$ 1 bi, 6 servidores afastados | gov.br/pf e gov.br/cgu, notícias de 23/04/2025 |
| 23/04/2025 | Presidência (Casa Civil) | Exonera o presidente do INSS (Portaria nº 489) | DOU |
| 28/04/2025 | INSS | Despacho Decisório PRES/INSS nº 65: suspende os ACTs de mensalidade associativa, os repasses e os descontos | DOU |
| 02/05/2025 | Presidência | Exonera a pedido o ministro da Previdência e nomeia o sucessor (Decretos de 02/05/2025) | DOU |
| 07/05/2025 | TCU | Acórdão 1.019/2025-Plenário: nega os recursos do INSS e de três associações; mantém a decisão de 2024 | portal.tcu.gov.br, notícia de 07/05/2025 |
| 08/05/2025 | AGU | Primeira ação cautelar: pede bloqueio de R$ 2,56 bi de 12 entidades e dirigentes (Lei Anticorrupção) | gov.br/agu, notícia de 08/05/2025 |
| 12/05/2025 | INSS | Instrução Normativa PRES/INSS nº 186 (fluxo de consulta, contestação e restituição) | DOU |
| 12/06/2025 | Justiça Federal (7ª Vara do DF), pedido da AGU | Bloqueio de R$ 2,8 bi nas 15 ações do primeiro lote | gov.br/agu, notícia de 12/06/2025 |
| 17/06/2025 | STF | ADPF 1.236 (relator Dias Toffoli), autor o Presidente da República: liminar em parte; convoca conciliação | portal.stf.jus.br, incidente 7287062 |
| 17/06/2025 | PF | Prisões preventivas e sequestro de imóveis (3ª Vara Federal de Sergipe) | gov.br/pf, notícia de 17/06/2025 |
| 02/07/2025 (lançada no andamento em 03/07) | STF | Homologa o Acordo Interinstitucional (União, INSS, MPF, DPU, CFOAB): devolução administrativa dos descontos de mar/2020 a mar/2025; suspende a prescrição | STF, decisão de 02/07/2025 |
| 09/07/2025 | STF | Despacho: a despesa do acordo fica fora dos limites da LC 200/2023 e da meta fiscal | STF |
| 16/07/2025 | Presidência | MP 1.306/2025: crédito extraordinário de R$ 3.312.824.545,00 (ação 00XK) | planalto.gov.br |
| 25/07/2025 | INSS | Portaria PRES/INSS nº 736: primeiro afastamento cautelar de servidores ligado à operação | DOU |
| 20/08/2025 | Congresso | Instalada a CPMI do INSS (presidente Carlos Viana, relator Alfredo Gaspar) | Agência Senado, 20/08/2025 |
| 12/09/2025 | PF | Operação Cambota (desdobramento): 2 prisões preventivas autorizadas pelo STF | gov.br/pf |
| 09/10/2025 | PF e CGU | Nova fase: 66 mandados de busca expedidos pelo STF | gov.br/pf |
| 29/10/2025 | TCU | Acórdão 2.538/2025-Plenário: o tema está em apuração nos TCs 016.470/2024-9, 007.869/2025-8 e 007.871/2025-2 | DOU, Ata 43/2025 do TCU |
| nov/2025 | Congresso | MP 1.306/2025 perde a eficácia sem ser convertida em lei | congressonacional.leg.br (MPV 1306/2025, "SEM EFICÁCIA") |
| 13/11/2025 | PF e CGU | Nova fase: 63 buscas, 10 prisões preventivas em 15 UFs e no DF | gov.br/pf |
| 18/12/2025 | CGU e PF | Nova fase: 52 buscas, 16 prisões, mandados do STF "sob a relatoria do Ministro André Mendonça" | gov.br/cgu |
| 20/12/2025 | AGU | 37 ações cautelares, R$ 4,4 bi em bloqueios deferidos, R$ 514 mi efetivamente bloqueados; ações regressivas de R$ 135 mi | gov.br/agu |
| 13/03/2026 (registro 16/03) | STF | Plenário referenda a cautelar e homologa o acordo com interpretação conforme: pagamento administrativo com presunção de boa-fé do segurado | STF, aba Decisões da ADPF 1.236 |
| 28/03/2026 | Congresso | CPMI termina sem relatório final: parecer do relator rejeitado por 19 a 12 | Agência Senado, 28/03/2026 |
| 20/07/2026 | Presidência | MP 1.378/2026: crédito extraordinário de R$ 547.000.000,00 (ação 00XK) | planalto.gov.br |
| 25/08/2026 | TCU | Acórdão 2.252/2026-Plenário: sobrestá as contas de 2023 do Ministério da Previdência de quatro gestores até o julgamento do TC 007.871/2025-2 (relator Odair Cunha), cuja inspeção "apontou necessidade de citação e/ou audiência" | DOU, Ata 32/2026 do TCU |

## 7. Comparação honesta (D48)

**Proposta: os descontos associativos de cada ano em relação ao total pago em benefícios do RGPS no mesmo ano.**

| Ano | Descontos associativos (CGU) | Benefícios previdenciários do RGPS (RTN, Tabela 1.1, linha 4.1) | Participação |
|---|---|---|---|
| 2019 | R$ 604,6 mi | R$ 626.510,4 mi | 0,097% |
| 2020 | R$ 510,9 mi | R$ 663.904,4 mi | 0,077% |
| 2021 | R$ 536,3 mi | R$ 709.582,5 mi | 0,076% |
| 2022 | R$ 706,2 mi | R$ 796.976,6 mi | 0,089% |
| 2023 | R$ 1.299,8 mi | R$ 898.872,9 mi | 0,145% |
| 2024 (estimativa da CGU) | R$ 2.637,2 mi | R$ 938.544,5 mi | 0,281% |
| 2019 a 2024 | R$ 6.295,0 mi | R$ 4.634.391,3 mi | 0,136% |

Fontes: CGU, Relatório nº 1675291, Gráfico 1; Tesouro Nacional, RTN, série histórica de agosto de 2026 (arquivo
`serie_historica_ago26.xlsx`, https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326), Tabela 1.1, linha "4.1 Benefícios
Previdenciários", soma dos meses, R$ correntes.

Por que essa comparação:
- É a mesma base de dinheiro (o benefício pago pelo RGPS, do qual saía o desconto), no mesmo período, de duas fontes oficiais.
- Mostra as duas coisas ao mesmo tempo, sem escolher tese: no total o desconto é uma fração pequena do que o RGPS paga (cerca de
  0,14%), mas a fração quase triplicou de 2019 para 2024 (de 0,097% para 0,281%), enquanto os benefícios cresceram 1,5 vez. O
  crescimento é o que a CGU e o TCU apontam como sinal de alerta.
- Ressalvas que vão junto na tela: a CGU diz que os descontos estão subestimados em cerca de 20% (com isso, 0,16% no período); 2024 é
  estimativa; os benefícios do RTN incluem 13º e sentenças judiciais; e a fração média esconde que o desconto atingia uma parte
  dos beneficiários ("6 milhões" segundo a CGU, de "40,1 milhões de benefícios pagos em maio de 2024", nota 3 do relatório).
- Alternativa equivalente, se o site preferir a base do INSS: BEPS, tabela 18 (valor bruto dos benefícios emitidos), já carregada
  em `data/series/federal-by-uf-monthly.json` (`inss_gross_benefit_value`); dá 0,157% no período 2019 a 2024.

Não é "projeto parecido" no sentido das obras: não existe outro caso oficial de descontos em folha com dado comparável. A
comparação acima é a que o dado sustenta.

## O que não foi confirmado

- **Balanço oficial do ressarcimento depois de 01/04/2026.** As notícias do gov.br de julho a outubro de 2026 estavam restritas e o
  Internet Archive não tinha cópia. "R$ 3,26 bilhões a 4,8 milhões": só na imprensa, não confirmado em fonte oficial. O valor pago
  pela ação 00XK (Portal da Transparência) cobre o dinheiro até setembro de 2026, mas não o número de pessoas.
- **Valor já devolvido aos cofres públicos pelas entidades.** Só há bloqueios (R$ 514 mi efetivos) e cobranças (R$ 135 mi).
- **Quanto as entidades devolveram diretamente** aos beneficiários pelo fluxo da IN PRES/INSS nº 186/2025.
- **Indiciamentos da PF em 2026** (a imprensa fala em 48 pessoas): só na imprensa; e indiciamento não entra em GD23.
- **Denúncia recebida ou condenação** ligada ao caso: nenhuma encontrada em fonte oficial até 02/10/2026.
- **Partidos** de Carlos Lupi (PDT) e de Wolney Queiroz em 2025 em fonte oficial; partido de Rogério Marinho em 2019. Para Lupi, o
  caminho é o TSE (órgão partidário) ou uma candidatura registrada.
- **Quem assinou cada ACT** de mensalidade associativa pelo INSS ao longo dos anos (as cópias estão em
  https://www.gov.br/inss/pt-br/acesso-a-informacao/acordos-de-cooperacao-tecnica-acts-de-mensalidades-associativas; não levantado
  por tempo). Entra em GD23 ("quem assinou pelo governo") e pode ser o próximo passo.
- **Resultado dos PARs** (CGU e INSS) contra entidades e do PAD avocado pela CGU.
- **Data exata** em que a MP 1.306/2025 perdeu a eficácia (a EXM diz "novembro de 2025"; o Congresso marca "SEM EFICÁCIA").
- **Substitutos na presidência do INSS** nos intervalos 02/01 a 01/02/2023 e 24 a 29/04/2025.
- **Data do acórdão do Plenário do STF** de 2026: a aba de decisões registra a sessão virtual de 06 a 13/03/2026 (lançada em
  16/03/2026); a EXM fala em "abril de 2026" (provável data de publicação).

## Fontes

Notícias do gov.br lidas na cópia do Internet Archive (data da cópia entre parênteses).

- CGU, Relatório de Auditoria nº 1675291 (publicado em 23/04/2025): https://eaud.cgu.gov.br/relatorio/1675762 (PDF:
  https://eaud.cgu.gov.br/relatorios/download/1675762)
- CGU, "Operação combate descontos não autorizados...", 23/04/2025:
  https://www.gov.br/cgu/pt-br/assuntos/noticias/2025/04/fraude-no-inss-aposentados-e-pensionistas-tiveram-quase-r-6-3-bi-em-descontos-sem-autorizacao (cópia de 30/04/2025)
- CGU, "CGU e PF combatem descontos não autorizados...", 23/04/2025:
  https://www.gov.br/cgu/pt-br/assuntos/noticias/2025/04/cgu-e-pf-combatem-descontos-nao-autorizados-em-beneficios-do-inss (cópia de 23/04/2025)
- PF, 23/04/2025: https://www.gov.br/pf/pt-br/assuntos/noticias/2025/04/pf-e-cgu-investigam-descontos-irregulares-em-beneficios-do-inss
- PF, 17/06/2025, 12/09/2025, 09/10/2025, 13/11/2025; CGU, 18/12/2025 (fases da operação): links no JSON (`control_timeline`)
- INSS, 01/04/2026: https://www.gov.br/inss/pt-br/assuntos/governo-federal-ja-devolveu-mais-de-r-3-bilhoes-a-beneficiarios-vitimas-de-descontos-indevidos (cópia de 13/05/2026)
- AGU, 08/05/2025, 12/06/2025 e 20/12/2025: https://www.gov.br/agu/pt-br/comunicacao/noticias/agu-ajuiza-dois-novos-lotes-de-acoes-contra-associacoes-envolvidas-em-fraudes-do-inss e demais no JSON
- Planalto, MP nº 1.306/2025: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/mpv/mpv1306.htm
- Planalto, MP nº 1.378/2026: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/mpv/mpv1378.htm e EXM nº 1.689/2026:
  https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/exm/exm-mp-1378-26.pdf
- Senado, Nota Técnica da MPV 1.378/2026: https://www12.senado.leg.br/orcamento/documentos/estudos/tipos-de-estudos/notas-tecnicas-de-adequacao-orcamentaria-e-financeira/nota_tecnica_mpv_1378_2026.pdf
- Congresso, MPV 1.306/2025: https://www.congressonacional.leg.br/materias/medidas-provisorias/-/mpv/169657
- STF, ADPF 1.236: https://portal.stf.jus.br/processos/detalhe.asp?incidente=7287062; decisão de 02/07/2025:
  https://portal.stf.jus.br/processos/downloadPeca.asp?id=15378368128&ext=.pdf; despacho de 09/07/2025:
  https://portal.stf.jus.br/processos/downloadPeca.asp?id=15378455298&ext=.pdf
- Portal da Transparência, execução da despesa, arquivos mensais 202507 a 202609:
  https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/AAAAMM
- TCU: https://portal.tcu.gov.br/imprensa/noticias/auditoria-constata-irregularidades-em-descontos-na-folha-de-pagamento-de-aposentados ;
  https://portal.tcu.gov.br/imprensa/noticias/tcu-nega-recursos-do-inss-em-processo-sobre-descontos-na-folha-de-aposentados ;
  DOU, Ata 43/2025 (Acórdão 2.538/2025) e Ata 32/2026 (Acórdão 2.252/2026)
- Agência Senado, CPMI: https://www12.senado.leg.br/noticias/materias/2025/08/20/cpmi-do-inss-carlos-viana-e-o-presidente-e-alfredo-gaspar-o-relator
  e https://www12.senado.leg.br/noticias/materias/2026/03/28/cpmi-do-inss-termina-sem-relatorio-final
- Tesouro Nacional, RTN, série histórica de agosto de 2026: https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326
- Diário Oficial da União (nomeações, exonerações, Despacho Decisório nº 65/2025, IN nº 186/2025, Portarias PRES/INSS de
  afastamento): links de cada ato no JSON (`governments`, `people`, `control_timeline`)
