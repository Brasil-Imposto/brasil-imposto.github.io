# Maiores Escândalos (D65): casos de 2019 a 2026 ordenados por dinheiro público

Pesquisa de 2026-10-02 para o componente "Maiores Escândalos" do lado esquerdo da home (D65). Só fontes oficiais; a imprensa
serviu apenas de pista. Dados estruturados: `data/home/scandals.json`.

Nota de acesso: em 2026-10-02 as notícias do gov.br (PF, Receita, Previdência) respondem "Conteúdo Restrito" e foram lidas na
cópia do Internet Archive; o portal do TCU respondeu 503 a pedidos automáticos (a notícia de 2020 foi lida no Internet Archive, os
PDFs do TCU abriram no original); o portal do STF respondeu 403 (o acórdão da ADPF 854 foi lido no registro de legislação do
Senado); os documentos do `legis.senado.leg.br/sdleg-getter` pedem verificação de navegador e não abriram.

## Critério

Ordem pelo **valor de dinheiro público envolvido segundo achado ou ato oficial** (STF, TCU, CGU, PF, MPF, AGU, Receita Federal,
CPI ou CPMI com relatório aprovado, ou o ato oficial que gastou o dinheiro), o mesmo critério para qualquer governo e partido.
Dinheiro privado fica separado e não entra na ordem. Valor que não foi confirmado numa página oficial aberta vira `null` e o caso
vai para o fim. Pessoas: só quem tem papel num documento oficial, com o ato (mesma regra GD23 do caso INSS); quem só foi citado,
investigado ou alvo de medida cautelar fica de fora, sem nome.

**Atenção para o autor:** "dinheiro público envolvido" não é a mesma coisa nos cinco casos, e o cartão precisa dizer o que o
número é. No RP 9 é o dinheiro alocado por um mecanismo julgado inconstitucional (não um prejuízo apurado); no Auxílio Emergencial
é uma estimativa estatística do TCU de pagamentos indevidos; na Carbono Oculto é tributo lançado pela Receita; no INSS é o que a
União abriu para devolver descontos privados. A ordem segue o critério escrito, mas comparar os valores lado a lado exige essa
ressalva em cada cartão.

## Casos

| # | Caso | Período | Dinheiro público (achado oficial) | Órgão e documento | Privado (separado) |
|---|---|---|---|---|---|
| 1 | Emendas de relator (RP 9), o "orçamento secreto" | 2020 a 2022 | mais de R$ 53 bi | STF, ADPF 854, Plenário, 19/12/2022 | não se aplica |
| 2 | Pagamentos indevidos no Auxílio Emergencial | 2020 a 2021 | R$ 45.775.508.721,66 (estimativa) | TCU, Balanço da Fiscalização (set/2022) e Acórdão 3.142/2021-Plenário | não se aplica |
| 3 | Sonegação e lavagem no setor de combustíveis (Operação Carbono Oculto) | 2020 a 2025 | mais de R$ 8,67 bi em créditos tributários | Receita Federal, 28/08/2025 | não se aplica |
| 4 | Descontos associativos não autorizados no INSS | 2019 a 2025 | R$ 3.859.824.545,00 abertos (R$ 3.654.802.192,32 pagos até set/2026) | MPs 1.306/2025 e 1.378/2026; Portal da Transparência | R$ 6,3 bi descontados (CGU e PF, 2019 a 2024) |
| 5 | Banco Master e as operações com o BRB | 2024 a 2025 | **não confirmado** | (ver abaixo) | não confirmado |

### 1. Emendas de relator (RP 9), o "orçamento secreto" (2020 a 2022)

- **O que o órgão disse:** o STF julgou procedentes as ADPFs 850, 851, 854 e 1.014 para "declarar incompatíveis com a ordem
  constitucional brasileira as práticas orçamentárias viabilizadoras do chamado 'esquema do orçamento secreto', consistentes no
  uso indevido das emendas do Relator-Geral do orçamento". A ementa diz que "o destino final dos recursos alocados sob a rubrica
  RP 9 (emendas do relator) acha-se recoberto por um manto de névoas".
- **Valor:** "elevadas quantias (mais de R$ 53 bilhões entre 2020 e 2022) vinculadas a finalidades genéricas, vagas e ambíguas"
  (STF, ementa da ADPF 854, Plenário, 19/12/2022). No JSON: 53.000.000.000 (piso; o texto diz "mais de"). Não é prejuízo apurado.
- **Situação:** julgado em 19/12/2022 (vencidos em parte cinco ministros, nomeados na decisão). O STF ordenou publicar, em 90 dias,
  os dados das despesas RP 9 de 2020 a 2022 "assim como a identificação dos respectivos solicitadores e beneficiários". A ADPF 854
  segue em execução sob a relatoria de Flávio Dino, com decisões "ad referendum do Plenário" (Nota Informativa do Senado, posição em
  26/02/2025). Decisões de 2025 e 2026 não foram levantadas.
- **Pessoas com ato:** Rosa Weber (relatora e presidente, voto condutor); Flávio Dino (relator da execução). Os relatores-gerais do
  orçamento de 2020 a 2022 não entraram porque nenhum ato com o nome deles foi aberto nesta pesquisa.
- **Fontes:** Senado, registro da decisão: https://legis.senado.leg.br/norma/36822451/publicacao/37033963 ; Nota Informativa:
  https://www12.senado.leg.br/noticias/arquivos/2025/02/28/nota-informativa-decisoes-stf-versao-final.pdf

### 2. Pagamentos indevidos no Auxílio Emergencial (2020 e 2021)

- **O que o órgão disse:** "O Auxílio Emergencial foi tempestivo e alcançou trabalhadores sem renda formal, porém, os altos índices
  de pagamentos indevidos resultaram em desperdício de recursos públicos" (TCU, Balanço da Fiscalização, set/2022).
- **Valor:** "A soma desses dois erros de focalização gerou um custo estimado de pagamentos indevidos de aproximadamente R$ 45,7
  bilhões, já considerando os pagamentos interrompidos por ações de controle." Tabela do Balanço: elegíveis a mais, 7.449.427
  pessoas, R$ 21.533.874.753,52; mães chefes de família a mais, 6.483.993, R$ 24.241.633.968,14; total **R$ 45.775.508.721,66**,
  "14% de R$ 330 bilhões pagos". O Acórdão 3.142/2021-Plenário (item 81) repete: "o montante em pagamentos indevidos de Auxílio
  Emergencial poderia chegar a R$ 45,7 bilhões", e explica que a estimativa "refere-se a cotejamento entre o público-alvo estimado,
  com base na [PNAD Contínua], e os pagamentos efetuados". É estimativa, não fraude comprovada caso a caso.
- **Outros números do TCU:** 4,9 milhões de benefícios cancelados por TCU, CGU, TCEs e CGEs até julho de 2021, e "R$ 12,3 bilhões
  em pagamentos indevidos que teriam sido pagos" sem essa detecção (prevenidos).
- **Situação:** acompanhamento concluído e arquivado pelo Acórdão 3.142/2021-Plenário (TC 016.827/2020-1, sessão de 15/12/2021,
  relator Bruno Dantas). Devolução à União: não levantada.
- **Atos:** Acórdão 2.282/2020-Plenário (26/08/2020), que determinou "verificação mensal de elegibilidade [...] cessando os
  pagamentos quando detectado descumprimento dos requisitos legais"; Acórdão 3.142/2021-Plenário (15/12/2021).
- **Pessoas com ato:** Bruno Dantas (relator).
- **Fontes:** https://portal.tcu.gov.br/data/files/4B/12/02/82/6CD33810B4FE0FF7E18818A8/00_cartilha_auxilio-emergencial_TCU_2022.pdf ;
  https://portal.tcu.gov.br/data/files/05/E0/04/FC/B9D038102DFE0FF7F18818A8/062_acordao_tcu_3142_2021.pdf ;
  https://portal.tcu.gov.br/imprensa/noticias/tcu-determina-interrupcao-de-pagamentos-indevidos-do-auxilio-emergencial (lida em
  web.archive.org/web/20251119145056)
- Ligação com D67 (o Auxílio Emergencial vira projeto): o mesmo processo traz o total pago, R$ 330,35 bi até julho de 2021.

### 3. Sonegação e lavagem no setor de combustíveis, Operação Carbono Oculto (2020 a 2025)

- **O que o órgão disse:** operação contra "organização responsável por sonegação e lavagem de dinheiro no setor de combustíveis"
  (Receita Federal, 28/08/2025), com buscas em "cerca de 350 alvos" em oito estados. Cerca de 1.000 postos "movimentaram R$ 52
  bilhões entre 2020 e 2024"; uma fintech "atuava como 'banco paralelo' da organização criminosa, tendo movimentado mais de R$ 46
  bilhões de 2020 a 2024"; 40 fundos com patrimônio de R$ 30 bi.
- **Valor (público):** "A Receita Federal já constituiu créditos tributários federais de um total de mais de R$ 8,67 bilhões em
  pessoas e empresas integrantes do esquema." Os R$ 52 bi e R$ 46 bi são movimentação, não dinheiro público; não entram na ordem.
- **Situação:** operação deflagrada; a PGFN ingressou com "ações judiciais cíveis de bloqueio de mais de R$ 1 bilhão em bens".
  Denúncias e decisões posteriores não foram levantadas.
- **Pessoas:** nenhuma; a notícia oficial não nomeia ninguém.
- **Fonte:** https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2025/agosto/operacao-carbono-oculto-rrb-e-orgaos-parceiros-combatem-organizacao-responsavel-por-sonegacao-e-lavagem-de-dinheiro-no-setor-de-combustiveis
  (lida em web.archive.org/web/20250828223729)
- Ressalva: a Receita não está na lista de exemplos do pedido, mas o lançamento de crédito tributário é ato oficial de um órgão
  federal. Se o autor quiser só órgãos de controle e justiça, este caso sai.

### 4. Descontos associativos não autorizados no INSS (2019 a 2025)

Reaproveitado de `docs/research/BRASIL-IMPOSTO_RESEARCH_case-inss-deductions_2026-10-02.md` e `data/cases/inss-deductions.json`,
sem nova coleta.
- **Valor público:** R$ 3.859.824.545,00 em créditos extraordinários (MP 1.306/2025, R$ 3.312.824.545,00; MP 1.378/2026,
  R$ 547.000.000,00); pagos pela ação 00XK até setembro de 2026: R$ 3.654.802.192,32. A ordem usa o valor aberto pelos atos.
- **Valor privado:** "valor estimado de R$ 6,3 bilhões, no período entre 2019 e 2024" descontado de aposentados (CGU e PF).
- Mesmo usando o privado (R$ 6,3 bi), o caso continuaria em 4º lugar.

### 5. Banco Master e as operações com o BRB (2024 e 2025)

- **O que os órgãos disseram:** a PF deflagrou a Operação Compliance Zero em 18/11/2025 "com o objetivo de combater a emissão de
  títulos de crédito falsos por instituições financeiras", após "requisição do Ministério Público Federal, para investigar a
  possível fabricação de carteiras de crédito insubsistentes por uma instituição financeira. Tais títulos teriam sido vendidos a
  outro banco e, após fiscalização do Banco Central, substituídos por outros ativos sem avaliação técnica adequada". Na 2ª fase
  (14/01/2026), com mandados do STF, "medidas de sequestro e bloqueio de bens e valores que superam R$ 5,7 bilhões". O TCDF
  determinou em 23/09/2026 "a indisponibilidade de bens de ex-integrantes da alta administração do BRB", por um ano, "para
  resguardar eventual ressarcimento aos cofres públicos", e converteu o processo 00600-00003617/2025-75-e em Tomada de Contas Especial.
- **Valor público: não confirmado.** Pistas da imprensa sem página oficial aberta: R$ 12,2 bi em carteiras compradas pelo BRB
  (atribuído à PF e ao Banco Central) e R$ 1,867 bi aplicados por 18 regimes próprios de previdência em letras financeiras do Master,
  sem cobertura do FGC (atribuído ao Ministério da Previdência). O bloqueio de R$ 2,7 bi do TCDF também só aparece na imprensa (a
  notícia do TCDF não traz valor). Os R$ 5,7 bi da PF são bloqueio, não dinheiro público perdido.
- **Valor privado:** o que o FGC pagou aos depositantes não foi confirmado em fonte oficial.
- **Situação:** liquidação extrajudicial pelo Banco Central em 18/11/2025 (o ato do BC não foi aberto); inquérito no STF; TCE no TCDF.
- **Pessoas:** nenhuma no JSON. Os nomes que aparecem (ex-dirigentes do BRB, controlador do Master) estão ligados a medidas
  cautelares (prisão preventiva, indisponibilidade de bens), que a regra GD23 deixa de fora.
- **Fontes:** PF, https://www.gov.br/pf/pt-br/assuntos/noticias/2025/11/policia-federal-combate-crimes-praticados-contra-o-sistema-financeiro-nacional
  (web.archive.org/web/20251201); PF, https://www.gov.br/pf/pt-br/assuntos/noticias/2026/01/policia-federal-deflagra-segunda-fase-da-operacao-compliance-zero
  (web.archive.org/web/2026); TCDF, https://www2.tc.df.gov.br/tcdf-determina-bloqueio-de-bens-de-ex-dirigentes-do-brb/
- Sugestão para o cartão: mostrar "valor público: em apuração (TCE no TCDF)" até um documento oficial publicar o número.

## Casos considerados e por que ficaram de fora

| Caso | Por que ficou de fora |
|---|---|
| Compra da vacina Covaxin (CPI da Pandemia, relatório aprovado em 26/10/2021) | Contrato de cerca de R$ 1,6 bi que não chegou a ser pago (pista da imprensa); o relatório da CPI está no `legis.senado.leg.br`, que não abriu. Mesmo confirmado, ficaria abaixo do INSS. |
| Aplicações do GDF em CDBs do BRB (R$ 3,4 bi) | É representação de um deputado distrital no TCDF (28/08/2026), não achado. |
| Imóveis públicos do DF para capitalizar o BRB | TCDF pediu explicações (26/03/2026); sem valor de achado. |
| Emendas Pix e emendas de comissão (ADIs 7688, 7695, 7697) | Período posterior ao RP 9 e auditorias da CGU ainda em curso; sem valor total de achado aberto. |

## O que não foi confirmado

- Banco Master: todo valor de dinheiro público (R$ 12,2 bi do BRB, R$ 1,867 bi dos regimes próprios), o bloqueio de R$ 2,7 bi do
  TCDF, os nomes dos alvos do TCDF, o valor pago pelo FGC e o ato de liquidação do Banco Central.
- RP 9: valores por ano e quanto foi pago (o STF fala em "mais de R$ 53 bilhões"); decisões de execução de 2025 e 2026.
- Auxílio Emergencial: quanto foi devolvido à União depois do acompanhamento.
- Carbono Oculto: denúncias, decisões e valor efetivamente bloqueado depois de 28/08/2025.
- Covaxin: valor do contrato e trechos do relatório da CPI.

## Fontes

- STF, ADPF 854 (decisão de 19/12/2022), no registro do Senado: https://legis.senado.leg.br/norma/36822451/publicacao/37033963
- Senado, Nota Informativa sobre decisões do STF (27/02/2025): https://www12.senado.leg.br/noticias/arquivos/2025/02/28/nota-informativa-decisoes-stf-versao-final.pdf
- TCU, Balanço da Fiscalização do Auxílio Emergencial (set/2022): https://portal.tcu.gov.br/data/files/4B/12/02/82/6CD33810B4FE0FF7E18818A8/00_cartilha_auxilio-emergencial_TCU_2022.pdf
- TCU, Acórdão 3.142/2021-Plenário: https://portal.tcu.gov.br/data/files/05/E0/04/FC/B9D038102DFE0FF7F18818A8/062_acordao_tcu_3142_2021.pdf
- TCU, notícia do Acórdão 2.282/2020 (02/09/2020): https://portal.tcu.gov.br/imprensa/noticias/tcu-determina-interrupcao-de-pagamentos-indevidos-do-auxilio-emergencial
- Receita Federal, Operação Carbono Oculto (28/08/2025): ver o link no caso 3.
- PF, Operação Compliance Zero (18/11/2025 e 14/01/2026) e TCDF (23/09/2026): ver os links no caso 5.
- Caso INSS: as fontes em `data/cases/inss-deductions.json`.
