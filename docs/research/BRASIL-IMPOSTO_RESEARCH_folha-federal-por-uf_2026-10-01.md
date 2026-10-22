# Folha de pessoal da União por UF

**Data da coleta:** 2026-10-01. **Arquivo:** `data/series/federal-payroll-by-uf.json`. **Scripts:** `pipelines/series/agg_payroll_monthly.py`, `agg_union_expense_base.py`, `build_federal_payroll_by_uf.py`.

**Pergunta:** quanto a União paga em pessoal (ativos, aposentados e pensionistas; civis e militares; Executivo, Legislativo, Judiciário, MPU e DPU) a pessoas em cada UF, para preencher `direct_spending.federal_payroll`, hoje `null` em `data/uf-balance-2024.json`.

## 1. Resposta curta

- Nenhuma fonte aberta diz onde trabalha ou mora cada pessoa paga pela União. O que existe é a UF que o próprio sistema de execução (SIAFI) atribui à despesa, e a sede de cada unidade dos outros Poderes. Com essas duas regras, **38,8% da folha de 2024 (sem o FCDF) tem UF: R$ 132,16 bi de R$ 340,34 bi**. Os outros **R$ 208,20 bi ficam em `not_located`**, com o motivo.
- **DF em 2024: R$ 39,04 bi localizados** (Executivo R$ 19,92 bi, Legislativo R$ 11,10 bi, Judiciário R$ 7,09 bi, MPU R$ 0,93 bi), fora o FCDF. É um piso: militares, folhas centralizadas de ministérios e aposentados pagos por unidades sem UF não entram em nenhuma UF.
- **Militares: nenhum real tem UF.** As Forças Armadas pagam por três unidades centrais com localizador Nacional, e o microdado de militares do Portal traz UF_EXERCICIO = -1 em todos os 345.468 registros (2024-01).
- **FCDF não é contado duas vezes:** o pessoal pago pelo FCDF (R$ 18,54 bi em 2024, polícias, bombeiros, saúde e educação do DF) está dentro da folha da União no SIAFI e no RTN; aqui ele sai de tudo e fica em `fcdf_personnel_excluded`.
- Cobertura: Executivo de 2024-01 a 2025-10 (só 2024 completo); Legislativo, Judiciário, MPU, DPU e FCDF de 2022-01 a 2026-08. 2019 a 2021 e o resto de 2025 e 2026 ficaram `null`: o servidor do Portal passou a bloquear os downloads. Os scripts retomam de onde pararam.

## 2. Fontes

| Fonte | O que dá | Formato | Uso |
|---|---|---|---|
| Portal da Transparência, Execução da Despesa: https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/AAAAMM | Pagamentos do Poder Executivo por mês, com órgão, unidade gestora, unidade orçamentária, ação, grupo, modalidade, elemento e a UF do localizador | ZIP mensal (5 a 11 MB) | Executivo por UF |
| Tesouro Nacional, Despesas e Transferências Totais da União (critério valor pago): https://www.tesourotransparente.gov.br/ckan/dataset/despesas-e-transferencias-totais | Todos os Poderes, por mês, órgão, unidade orçamentária, grupo, modalidade, ação e categoria do RTN. Sem UF | XLSX anual (23 a 38 MB) | Outros Poderes por UF, FCDF, checagem nacional |
| Tesouro Nacional, RTN, série histórica, tabela 1.5: https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326 (publicada em 2026-09-29, já em `pipelines/series/cache/union/`) | Pessoal e Encargos Sociais por mês e por tipo (ativo civil, ativo militar, aposentadorias e pensões civis, reformas e pensões militares, sentenças) | XLSX | Total nacional |
| Portal da Transparência, servidores e militares: https://portaldatransparencia.gov.br/download-de-dados/servidores | Microdado por pessoa e por mês (cadastro e remuneração) | ZIP mensal (SIAPE cerca de 79 MB) | Testado; ver seção 7 |

## 3. Método

**Valor.** Pago no mês mais restos a pagar pagos no mês (é o critério "valor pago" da tabela 1.5 do RTN), grupo de despesa 1 (Pessoal e Encargos Sociais). O valor é bruto: inclui o imposto de renda retido e a contribuição do servidor (PSS), que o lado "arrecadação" do mapa já conta na UF onde a Receita registra (no DF, IRRF do trabalho de R$ 48,31 bi e PSS de R$ 18,44 bi em 2024).

**Escopo.** Só a modalidade 90 (aplicação direta). A modalidade 91 é a contribuição patronal que a União paga a ela mesma dentro do orçamento (R$ 27,30 bi em 2024): não chega a nenhuma pessoa e fica fora, informada na checagem. Grupo 1 pago por transferência (modalidades 30 a 50) vai para `not_located`.

**Regras de localização** (nada é distribuído por população, número de servidores ou proporção):

| Parte | Regra |
|---|---|
| Poder Executivo | UF do localizador orçamentário, como o SIAFI registra (coluna UF do Portal). Sem UF ali (localizador Nacional, regional ou exterior), vai para `not_located`. |
| Legislativo, Judiciário, MPU, DPU | UF da sede da unidade orçamentária, só quando a unidade trabalha numa única UF: Câmara, Senado, TCU, STF, STJ, TSE, TST, CNJ, TJDFT, MPDFT e ESMPU no DF; cada TRE na sua UF; cada TRF na UF da sede (1ª DF, 2ª RJ, 3ª SP, 4ª RS, 5ª PE, 6ª MG); cada TRT cuja região é uma UF. |
| Não localizados dos outros Poderes | Justiça Federal de primeiro grau, Justiça Militar, MPF, MPT, MPM e DPU (quadro em todo o país); TRTs da 8ª (PA e AP), 10ª (DF e TO), 11ª (AM e RR) e 14ª (RO e AC), porque a base não separa as duas UFs. |
| FCDF | Unidade orçamentária 73901 fora de tudo (seção 6). |

**Categorias** (campo `by_category`): no Executivo, pelo elemento de despesa (01 aposentadorias, 03 pensões, 91 e 92 sentenças e despesas de exercícios anteriores, o resto ativos) e pela ação (2867, 214H, 0179 e as dos ex-territórios = militares); nos outros Poderes, uma categoria por Poder.

**Por que não a UF da unidade que paga.** A tabela de unidades (UASG) do compras.gov.br dá a UF de cada unidade gestora, mas a folha militar é paga pelo Centro de Pagamento do Exército (R$ 15,0 bi de janeiro a abril de 2024), pela Pagadoria de Pessoal da Marinha (R$ 8,0 bi) e pela Subdiretoria de Pagamento de Pessoal da Aeronáutica (R$ 6,2 bi); usar a sede delas poria todos os militares do país no DF e no RJ. A tabela foi testada e descartada.

## 4. Cobertura

| Parte | Meses com dado | Falta |
|---|---|---|
| Executivo e `total_located` | 2024-01 a 2025-10 | 2019-01 a 2023-12, 2025-11 a 2026-08 |
| Legislativo, Judiciário, MPU, DPU e FCDF | 2022-01 a 2026-08 | 2019-01 a 2021-12 |
| RTN nacional | 2019-01 a 2026-08 | nada |

Ano completo com tudo: só 2024. 2025 aparece em `partial_years` (janeiro a outubro). O motivo das faltas está na seção 9.

## 5. Checagens

**Nacional, 2024 (R$ bi)** (campo `national_check.annual`):

| Item | Valor |
|---|---:|
| RTN tabela 1.5, Pessoal e Encargos Sociais | 366,22 |
| dos quais ativo civil / ativo militar | 162,24 / 35,66 |
| dos quais aposentadorias e pensões civis / reformas e pensões militares | 101,00 / 63,62 |
| dos quais sentenças e precatórios | 3,70 |
| Base do Tesouro, soma das categorias 2.2 do RTN | 366,22 (igual ao RTN publicado) |
| Pagamentos diretos de pessoal (modalidade 90), sem FCDF | 340,34 |
| Pessoal do FCDF (separado) | 18,54 |
| Soma das 27 UFs (`sum_of_ufs_located`) | 132,16 |
| Não localizado | 208,20 |
| Cobertura (localizado sobre a folha sem FCDF) | 38,83% |
| Cobertura sobre o RTN sem o FCDF | 38,01% |

- **Identidade:** localizado + não localizado = pagamentos diretos sem FCDF + outras modalidades, com diferença de R$ 0,00 em 2024 e em 2025.
- **Ponte com o RTN:** 366,22 = 340,34 + 18,54 (FCDF) + 4,41 (parte da modalidade 91 que o RTN classifica como pessoal) + 2,92 (Executivo um pouco menor no Portal do que na base do Tesouro), com diferença de R$ 0,02 bi.
- **Portal contra Tesouro, mês a mês** (campo `national_check.monthly.status`): em 18 dos 22 meses o pessoal do Executivo no Portal fica entre 0,4% e 1,5% abaixo da base do Tesouro. Quatro meses passam de 3% e estão marcados `portal_vs_tesouro_divergent`: 2024-09 (3,3% abaixo), 2025-06 (98,7% acima), 2025-07 (15,3% abaixo) e 2025-08 (4,5% abaixo). **O arquivo de 2025-06 do Portal traz R$ 47,67 bi contra R$ 23,99 bi do Tesouro**; julho e agosto ficam abaixo, e no trimestre sobram R$ 16,7 bi no Portal. O excesso está espalhado por quase todas as linhas (militares, aposentadorias, ativos civis). A causa não foi identificada; por isso 2025 (janeiro a outubro) mostra o Portal 6,2% acima do Tesouro.
- **2025, janeiro a outubro:** RTN 321,73; diretos sem FCDF 318,14; FCDF 16,84; localizado 122,92 (38,64%); não localizado 195,23.
- **FCDF de 2024 contra o mapa:** base do Tesouro R$ 23.606.092.115,56; `uf-balance-2024.json` (Portal) R$ 23.606.312.156,44. Diferença de R$ 220.040,88 (0,001%).
- **FCDF, custeio e capital contra o RTN:** grupos 3 e 4 da base somam R$ 2,41 bi (2022), R$ 4,28 bi (2023) e R$ 4,82 bi (2024), iguais à linha 2.3.11 do RTN.
- **Reprodução:** o JSON gerado a partir dos caches copiados para `pipelines/series/cache/payroll/` é idêntico byte a byte ao gerado na pasta de trabalho.

## 6. 2024: folha localizada em DF, RJ, SC e SP (R$ bi, sem FCDF)

| Categoria | DF | RJ | SC | SP |
|---|---:|---:|---:|---:|
| Executivo, civis ativos | 6,43 | 7,10 | 1,67 | 2,54 |
| Executivo, aposentadorias civis | 8,50 | 3,60 | 0,74 | 0,63 |
| Executivo, pensões civis | 4,68 | 0,86 | 0,11 | 0,08 |
| Executivo, sentenças e exercícios anteriores | 0,30 | 0,20 | 0,03 | 0,02 |
| Militares | 0,00 | 0,00 | 0,00 | 0,00 |
| Legislativo | 11,10 | 0,00 | 0,00 | 0,00 |
| Judiciário | 7,09 | 3,00 | 1,01 | 5,94 |
| MPU | 0,93 | 0,00 | 0,00 | 0,00 |
| **Total localizado** | **39,04** | **14,76** | **3,56** | **9,21** |

O DF fica com 29,5% de tudo o que foi localizado no país. Para comparação com o balanço de 2024 (`uf-balance-2024.json`), sem decidir nada sobre o saldo:

| UF | Arrecadação federal | Transferências | INSS, Bolsa Família e FCDF | Folha localizada (este arquivo) |
|---|---:|---:|---:|---:|
| DF | 184,10 | 3,78 | 37,24 | 39,04 |
| RJ | 459,20 | 70,80 | 95,19 | 14,76 |
| SC | 140,22 | 18,76 | 42,18 | 3,56 |
| SP | 1.036,61 | 70,59 | 254,74 | 9,21 |

**O que ficou sem UF em 2024 (R$ bi):** militares das Forças Armadas 92,13; Executivo civil sem UF no SIAFI 98,44; unidades de atuação nacional dos outros Poderes 15,50; TRTs de duas UFs 2,11; outras modalidades 0,01. Dentro do Executivo sem UF, por órgão (militares incluídos): Defesa 96,00; Gestão e Inovação (inativos de órgãos extintos e ex-territórios) 22,64; Justiça e Segurança Pública 11,74; Previdência Social 10,75; Fazenda 7,15; Educação 6,91; Agricultura 6,07; AGU 3,45; Banco Central 3,21; Planejamento 2,75 (campo `not_located.executivo_sem_uf_by_orgao_superior_annual`).

## 7. FCDF e dupla contagem

Bloco `fcdf` do JSON: o que a União pagou pela unidade 73901, por mês, de 2022-01 a 2026-08, por grupo e por ação (R$ bi):

| Ano | Total | Pessoal (grupo 1) | Custeio (grupo 3) | Investimento (grupo 4) |
|---|---:|---:|---:|---:|
| 2022 | 16,41 | 14,00 | 2,36 | 0,06 |
| 2023 | 21,98 | 17,70 | 4,17 | 0,11 |
| 2024 | 23,61 | 18,78 | 4,66 | 0,16 |
| 2025 | 24,92 | 20,01 | 4,77 | 0,14 |
| 2026 (jan. a ago.) | 18,99 | 14,98 | 3,89 | 0,12 |

2019 a 2021: `null` (arquivos anuais do Tesouro não baixados; seção 9).

**Onde o FCDF já está.** O grupo 1 do FCDF paga as polícias Civil e Militar e o Corpo de Bombeiros do DF (ativos, inativos e pensionistas, ações 00NR, 00NS, 00QN e 00Q2) e o pessoal da saúde e da educação do DF (ações 009T e 0312). Em 2024 ele está:

- **no SIAFI**, como despesa de pessoal da União com localizador DF (R$ 18,54 bi na modalidade 90 e R$ 0,24 bi na 91);
- **no RTN**, dentro da linha 2.2 (ativo civil 10,01; ativo militar 3,70; reformas e pensões militares 3,46; aposentadorias e pensões civis 1,38). A linha 2.3.11 do RTN, "Fundo Constitucional DF", traz só custeio e capital.

Neste arquivo o grupo 1 do FCDF fica fora de `total_located` e de `not_located` e aparece só em `fcdf_personnel_excluded`, porque o mapa já soma o FCDF inteiro em `fcdf_df_constitutional_fund`. **Quem usar o RTN como total nacional precisa tirar o pessoal do FCDF**: a checagem faz isso.

Não está confirmado se o microdado de servidores do Portal (SIAPE) traz esse pessoal. Na leitura do cadastro de 2024-01, "Governo do Distrito Federal" apareceu só como destino de 70 servidores federais cedidos ao SUS, mas a leitura listava apenas órgãos selecionados, e a busca completa pelos órgãos da PCDF, PMDF e CBMDF não foi feita. Isso não afeta este arquivo, que não usa o SIAPE nos valores; afetaria um futuro bloco `located_by_exercise`.

**INSS:** os benefícios do RGPS não são folha de pessoal e não aparecem no grupo 1; nada aqui se sobrepõe a `inss_benefits`.

## 8. Localizar pelo local de exercício da pessoa (bloco `located_by_exercise`)

O pedido era um segundo bloco, separado e nunca somado a `total_located`, com a folha de um mês de referência por ano alocada pelo microdado por pessoa. **Ele não foi construído nesta coleta e está `null` no JSON.** O que os arquivos lidos mostram:

| Arquivo (mês lido) | Tem UF? | Achado |
|---|---|---|
| Servidores_SIAPE (2024-01) | Sim, UF_EXERCICIO | 734.571 linhas de cadastro, 598.999 pessoas. UF_EXERCICIO = -1 em 39,7% das linhas. O DF aparece como UF de exercício de pessoal de instituições de outras UFs: Instituto Federal de Alagoas, 1.288 linhas no DF e 19 em AL; Universidade Federal da Integração Latino-Americana (Foz do Iguaçu), 801 no DF e 12 no PR; ex-Território do Amapá, 5.191 no DF e 68 no AP. 20.735 linhas no DF do Ministério da Saúde são RESIDENCIA E PMM (bolsas de residência e Mais Médicos, que não são pessoal). |
| Militares (2024-01) | Coluna existe, vazia | UF_EXERCICIO = -1 nos 345.468 registros (Exército 204.845, Marinha 72.906, Aeronáutica 67.717). |
| Aposentados_SIAPE, Aposentados_BACEN, Pensionistas_SIAPE, Pensionistas_BACEN, Pensionistas_DEFESA (2024-12) | Não | Nenhuma coluna de UF no cadastro (os SIAPE e DEFESA lidos pelos primeiros 64 KB do ZIP). |

Consequência: pelo microdado só os servidores civis ativos do Executivo poderiam ser alocados, e o campo de UF põe no DF pessoal que trabalha em outras UFs, o que aumentaria o DF. **Militares (ativos, inativos e pensionistas) e aposentados e pensionistas civis não têm UF em nenhuma fonte aberta encontrada.** O cabeçalho de Reserva_Reforma_Militares não chegou a ser lido.

## 9. Lacunas e motivos

| Lacuna | Motivo | Como fechar |
|---|---|---|
| Executivo de 2019 a 2023 e de 2025-11 a 2026-08 | O servidor de arquivos da CGU (dadosabertos-download.cgu.gov.br) passou a segurar conexões por 16 minutos sem enviar nada e a devolver a página de verificação do AWS WAF; o computador da coleta ficou sem memória livre | Rodar `agg_payroll_monthly.py` de novo; ele pula os meses prontos |
| Outros Poderes e FCDF de 2019 a 2021 | Cada XLSX anual do Tesouro levava cerca de 16 minutos para baixar no fim da coleta | Rodar `agg_union_expense_base.py` com 2019, 2020 e 2021 |
| Militares por UF | Nenhuma fonte aberta tem a UF (seções 3 e 8) | Pedido pela Lei de Acesso à Informação ao Ministério da Defesa (totais por UF, sem dado pessoal) |
| Executivo civil com localizador Nacional (R$ 98,44 bi em 2024) | O SIAFI não registra onde a pessoa trabalha | Microdado SIAPE com regra de correção do DF a definir, ou pedido de dado agregado por UF ao Ministério da Gestão e da Inovação |
| Aposentados e pensionistas pelo endereço | O endereço não é público | Só por pedido de dado agregado por UF |
| Bloco `located_by_exercise` | Seção 8 | Baixar um mês de referência por ano quando o servidor da CGU voltar a responder |
| 2025-06 no Portal | R$ 23,7 bi a mais que o Tesouro, causa não identificada | Perguntar à CGU (Fala.BR) ou usar a base do Tesouro para o total do Executivo |

## 10. Diário das fontes

| # | Fonte | Acesso | Tentativas | Resultado |
|---|---|---|---|---|
| 1 | Portal, Execução da Despesa | sem chave, ZIP mensal de 5 a 11 MB | 23 meses baixados | ✅ até 2025-10. Depois, conexões presas por 16 minutos e página do AWS WAF; cada mês levava de 30 a 75 s com a pausa |
| 2 | Tesouro, Despesas e Transferências Totais | sem chave, URL de cada ano pela API CKAN | 6 anos | ✅ 2022 a 2026. A aba de dados se chama "base" em 2024 e "2025" em 2025; o nome da coluna muda de caixa (Categoria_RTN, CATEGORIA_RTN); a categoria do RTN vem como "II.2.1 - Pessoal e Encargos Sociais - Ativo civil" em 2022 e 2023 e "2.2.1 - Ativo Civil" depois, e a vazia como "nan" ou "N/A". O script normaliza tudo |
| 3 | RTN, série histórica | já no cache do projeto | 1 | ✅ tabela 1.5 tem a folha por tipo; a tabela 1.1 não separa |
| 4 | Portal, servidores e militares | sem chave, ZIP mensal (SIAPE 79 MB; militares 285 MB descompactados) | 4 arquivos inteiros (SIAPE e militares de 2024-01, aposentados e pensionistas do BACEN de 2024-12) e 3 cabeçalhos pelos primeiros 64 KB | ⚠️ seção 8 |
| 5 | compras.gov.br, tabela UASG | API aberta, 92 páginas de 500 | 1 | ✅ funciona e dá a UF de cada unidade, mas a unidade que paga não é onde a pessoa está (seção 3); descartada |

## 11. Como reproduzir

Os caches agregados (14 MB, fora do git) ficam em `pipelines/series/cache/payroll/cache/`. Na pasta do projeto:

1. `python3 pipelines/series/agg_payroll_monthly.py pipelines/series/cache/payroll 201901-202608 20`: baixa e agrega os meses que faltam do Portal, apagando cada ZIP.
2. `python3 pipelines/series/agg_union_expense_base.py pipelines/series/cache/payroll 2019,2020,2021,2022,2023,2024,2025,2026`: o mesmo para a base do Tesouro (precisa de openpyxl).
3. `python3 pipelines/series/build_federal_payroll_by_uf.py pipelines/series/cache/payroll`: gera `data/series/federal-payroll-by-uf.json` (precisa de openpyxl e do RTN em `pipelines/series/cache/union/`).

Com os caches atuais, o passo 3 gera o mesmo arquivo byte a byte.
