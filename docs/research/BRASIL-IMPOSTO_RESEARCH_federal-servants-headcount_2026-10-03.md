# Quantas pessoas a União paga em cada Poder: ativos, aposentados e pensionistas

**Pergunta (D72):** quantos servidores **ativos**, **aposentados** e **pensionistas** a União paga em cada Poder (Executivo civil, militares, Judiciário, Legislativo, MPU, DPU), para mostrar duas barras separadas e o custo por pessoa ao lado da folha que já existe em `private/archive/data/federal/federal-section-2026-01-07.json`.

**Coletado em:** 2026-10-03. **Saída:** `data/federal/servants-by-branch.json`.

## Resumo

| Poder (chave no JSON) | Ativos | Aposentados (inativos) | Pensionistas (beneficiários) | Data | Fonte |
|---|---:|---:|---:|---|---|
| Executivo civil, com DPU, BCB e ABIN (`executive_civil`) | 663.308 | 421.369 | 281.712 | jul/2025 | RPPS, PLDO 2027 |
| Militares das Forças Armadas (`executive_military`) | 350.858 | 168.564 | 224.321 (139.842 instituidores) | mai/2025 | Defesa, PLDO 2027 |
| Judiciário da União (`judiciary`) | 105.545 | 34.919 | 10.145 | jul/2025 | RPPS, PLDO 2027 |
| Legislativo: Câmara, Senado e TCU (`legislative`) | 6.960 | 8.752 | 3.729 | jul/2025 | RPPS, PLDO 2027 |
| MPU (`mpu`) | 16.889 | 2.797 | 1.055 | jul/2025 | RPPS, PLDO 2027 |
| DPU, já contada no Executivo acima (`dpu`) | 1.085 (680 defensores e 405 servidores) | 48 | 29 (30 instituidores) | jul/2026 | DPU, Anexo I |

- Os quatro grupos civis somam exatamente o total impresso pela avaliação: 792.702 ativos, 467.837 aposentados e 296.641 pensionistas. A conferência foi testada com um controle quebrado (uma unidade a menos no MPU), que falha como deve.
- **Aposentados e pensionistas civis da União são do RPPS, não do INSS** (Constituição, art. 40); militares têm um terceiro sistema (SPSMFA).
- **O sistema de Justiça não é o mais caro por servidor** pela mesma fonte: o Legislativo paga em média R$ 18.541 ao ativo e R$ 39.390 ao aposentado, contra R$ 14.978 e R$ 22.057 no Judiciário (seção "O sistema de Justiça é o mais caro por servidor?").
- Sem confirmação: TCU separado, aposentados do Judiciário por ramo, MPU por ramo.

## Registro das fontes

### Fonte 1. Avaliação atuarial do RPPS da União, PLDO 2027 (base cadastral de julho de 2025)

- **Documento:** PLDO 2027, Anexo IV.11, "Avaliação Atuarial do Regime Próprio de Previdência Social dos Servidores, Aposentados e Pensionistas dos Poderes Executivo, Legislativo e Judiciário", data focal 31/12/2025, elaborada pela CGAAI/DRPPS/SRPC do Ministério da Previdência Social (PDF de 2026-04-15, 108 páginas).
- **Link:** https://www.gov.br/planejamento/pt-br/assuntos/orcamento/orcamentos-anuais/2027/pldo/anexo-iv-11-avaliacao-atuarial-rpps.pdf (o arquivo em si: o mesmo endereço com `/@@download/file` no fim; sem isso o gov.br devolve a página HTML).
- **Data de referência:** "os dados da base cadastral dos servidores, aposentados e pensionistas, usados no cálculo atuarial, devem referir-se ao mês de julho de 2025" (p. 15).
- **Frase da p. 15:** "no total, foram considerados 1.557.180 segurados, sendo 792.702 (50,9%) servidores ativos, 467.837 (30,0%) aposentados e 296.641 (19,0%) pensionistas."
- As tabelas 3 a 6 (p. 16 e 17) são imagens; lidas por extração das imagens do PDF.

| Grupo (como o documento chama) | Servidores ativos | Aposentados | Pensionistas | Remuneração média do ativo (R$) | Provento médio do aposentado (R$) | Provento médio do pensionista (R$) |
|---|---:|---:|---:|---:|---:|---:|
| Poder Executivo (Tabela 3) | 663.308 | 421.369 | 281.712 | 13.369,72 | 12.013,58 | 7.050,41 |
| Poder Legislativo (Tabela 4) | 6.960 | 8.752 | 3.729 | 18.541,40 | 39.389,57 | 25.356,55 |
| Poder Judiciário (Tabela 5) | 105.545 | 34.919 | 10.145 | 14.977,90 | 22.056,80 | 16.016,67 |
| Ministério Público da União (Tabela 6, "Poder MP") | 16.889 | 2.797 | 1.055 | 16.663,22 | 23.664,18 | 17.383,86 |
| **Total (Tabela 2)** | **792.702** | **467.837** | **296.641** | | | |

Conferência: as quatro linhas somam exatamente o total da Tabela 2 nas três colunas, e em cada tabela feminino mais masculino dá o total geral.

O que cada grupo contém, nas palavras do documento:
- Executivo: "os órgãos incluídos no Sistema Integrado de Administração de Pessoal (SIAPE) [...] além de instituições com informações extra-SIAPE, como a Defensoria Pública da União, a Agência Brasileira de Inteligência e o Banco Central do Brasil." **A DPU está dentro do Executivo nesta fonte.** Inclui também os militares dos ex-territórios (nota 17 do demonstrativo: "Estão incluídos nesta avaliação atuarial os benefícios concedidos e a conceder para os militares dos Ex-Territórios").
- Legislativo: "o Senado Federal, a Câmara dos Deputados e o Tribunal de Contas da União."
- Judiciário: "o Supremo Tribunal Federal, o Superior Tribunal de Justiça, o Superior Tribunal Militar, o Tribunal de Justiça do Distrito Federal e Territórios, os Tribunais Regionais Federais, as Seções Judiciárias da Justiça Federal, os Tribunais Regionais do Trabalho, os Tribunais Regionais Eleitorais, o Conselho da Justiça Federal, o Conselho Nacional de Justiça e o Conselho Superior da Justiça do Trabalho."
- MPU: "o Ministério Público do Distrito Federal e Territórios, o Ministério Público Federal, o Ministério Público Militar, o Ministério Público do Trabalho e o Conselho Nacional do Ministério Público."
- Fora dos quatro grupos: as polícias Civil e Militar e o Corpo de Bombeiros do DF (pagos pela União pelo FCDF) aparecem só em valores atuariais (Anexo XV), sem quantidade de pessoas.
- **Militares das Forças Armadas não estão aqui** (não são do RPPS; ver seção sobre militares).

Quem é contado: o RPPS cobre os titulares de cargo efetivo (art. 40 da Constituição); os membros (magistrados, membros do MP e de tribunal de contas) entram, pois o documento lista "magistrado, membro do Ministério Público ou de Tribunal de Contas" entre as situações funcionais da base. Ocupantes só de cargo em comissão, temporários e empregados públicos são do RGPS e não entram nesta contagem.

Pensionistas: o documento não usa a palavra "instituidor" nas tabelas; cada pensionista tem sexo e idade próprios (Executivo: 253.002 mulheres e 28.710 homens, idade média 72 anos), o que indica que a contagem é de **beneficiários** (quem recebe), não de instituidores. Isso é leitura da tabela, não frase do documento.

### Fonte 2. A mesma avaliação, edição anterior: PLDO 2026 (base cadastral de julho de 2024)

- **Documento:** PLDO 2026, Anexo IV.11, avaliação atuarial do RPPS da União, data focal 31/12/2024 (PDF de 2025-04-24, 112 páginas).
- **Link:** https://www.gov.br/planejamento/pt-br/assuntos/orcamento/orcamentos-anuais/2026/pldo/11-iv-11-avaliacao-atuarial-rpps.pdf (arquivo: o mesmo endereço com `/@@download/file`).
- **Data de referência:** "devem referir-se ao mês de julho de 2024" (p. 16).
- **Frase:** "No total, foram considerados 1.599.655 segurados, sendo 798.284 servidores ativos (49,9%), 492.239 aposentados (30,8%) e 309.132 pensionistas (19,3%)."
- Tabelas 6 a 9 (p. 17 e 18), imagens lidas da mesma forma; os quatro grupos somam exatamente o total.

| Grupo | Ativos | Aposentados | Pensionistas | Remuneração média do ativo (R$) | Provento médio do aposentado (R$) | Provento médio do pensionista (R$) |
|---|---:|---:|---:|---:|---:|---:|
| Poder Executivo (Tabela 6) | 669.182 | 446.775 | 294.419 | 11.686,09 | 11.089,99 | 7.879,33 |
| Poder Legislativo (Tabela 7) | 6.776 | 8.747 | 3.643 | 17.519,68 | 35.542,34 | 27.800,32 |
| Poder Judiciário (Tabela 8) | 105.294 | 33.949 | 10.055 | 14.382,26 | 22.092,09 | 20.538,06 |
| MPU (Tabela 9) | 17.032 | 2.768 | 1.015 | 16.183,90 | 22.842,63 | 20.184,48 |
| **Total** | **798.284** | **492.239** | **309.132** | | | |

Atenção: de julho de 2024 para julho de 2025 o Executivo perde 25.406 aposentados (446.775 para 421.369) e 12.707 pensionistas. O relatório não explica a queda nas páginas lidas; pode ser mudança de base (por exemplo, um órgão extra-SIAPE que entrou ou saiu), não só óbitos. Não comparar os dois anos como tendência sem essa explicação.

### Fonte 3. Militares das Forças Armadas: avaliação atuarial do PLDO 2027 (dados de maio de 2025)

- **Documento:** PLDO 2027, Anexo IV.12, "Avaliação Atuarial do Sistema de Pensões Militares das Forças Armadas", Volume 1, elaborado pelo Centro de Análises de Sistemas Navais, "de responsabilidade do Ministério da Defesa (MD)", datado de 23 de março de 2026.
- **Link:** https://www.gov.br/planejamento/pt-br/assuntos/orcamento/orcamentos-anuais/2027/pldo/anexo-iv-12-avaliacao-atuarial-pensoes-militares-2013-volume-1.pdf (arquivo: o mesmo endereço com `/@@download/file`).
- **Data de referência:** "Os dados correntes utilizados foram de maio de 2025, extrapolados para a posição de 31 de dezembro de 2025" (seção 3, p. 5). As quantidades da seção 3.1.1 são da base de maio de 2025; o documento não diz se as próprias quantidades foram extrapoladas.
- **Seção 3.1.1, "Quantidades" (p. 6), texto extraído do PDF:**

| Grupo | Oficiais | Praças | Total |
|---|---:|---:|---:|
| a) Militares ativos | 34.076 de carreira + 16.589 temporários | 102.922 de carreira + 181.334 temporários + 8.063 praças especiais de carreira + 7.874 praças especiais temporárias | **350.858** |
| b) Militares inativos (reserva remunerada e reformados) | 53.030 | 115.534 | **168.564** |
| c) Pensionistas tronco (instituidores) | 81.544 | 58.298 | **139.842** |
| d) Pensionistas beneficiários (quem recebe) | 96.147 (de oficiais) | 128.174 (de praças) | **224.321** |

Conferência: cada linha soma o total impresso. Dos 350.858 ativos, 205.797 (58,7%) são temporários (oficiais temporários, praças temporárias e praças especiais temporárias), quase todos com remuneração baixa (praça temporária: R$ 2.486,77 em média).

Remunerações médias da seção 3.1.2: oficial de carreira R$ 21.456,96; praça de carreira R$ 8.854,28; praça temporária R$ 2.486,77; inativo oficial R$ 25.719,58; inativo praça R$ 10.296,38; beneficiário de oficial R$ 13.512,51; beneficiário de praça R$ 5.636,32.

Regime: os militares não são do RPPS nem do INSS. O documento diz que os proventos e as pensões "têm natureza compensatória e fazem parte do SPSMFA" (Sistema de Proteção Social dos Militares das Forças Armadas, Lei 13.954/2019) e que "Os proventos de militares inativos são financiados integralmente pelo Tesouro Nacional, sendo uma despesa Fiscal da União, sem contribuição do militar, sem contribuição patronal" (seção 4.1.1, art. 53-A da Lei 6.880/1980).

### Fonte 4. Militares, edição anterior: PLDO 2026 (dados de maio de 2024)

- **Documento:** PLDO 2026, Anexo IV.12, avaliação atuarial do sistema de pensões militares das Forças Armadas, Volume 1 (Rio de Janeiro, 11 de março de 2025).
- **Link:** https://www.gov.br/planejamento/pt-br/assuntos/orcamento/orcamentos-anuais/2026/pldo/12-anexo-iv-12-avaliacao-atuarial-do-sistema-de-pensoes-militares-das-forcas-armadas-volume-1.pdf (arquivo: com `/@@download/file`).
- **Data de referência:** "Os dados correntes utilizados foram de maio de 2024, extrapolados para a posição de 31 de dezembro de 2024."
- **Seção 3.1.1:** ativos 354.230 (35.632 oficiais de carreira, 15.598 oficiais temporários, 104.682 praças de carreira, 182.276 praças temporárias, 9.664 praças especiais de carreira, 6.378 praças especiais temporárias); "Militares veteranos" (inativos) 169.491 (52.496 oficiais, 116.995 praças); pensionistas tronco 138.370; pensionistas beneficiários 221.374. Todas as linhas somam o total impresso.

### Fonte 5. Judiciário da União por ramo, só ativos: CNJ, Justiça em Números 2025 (ano-base 2024, posição de dezembro de 2024)

- **Documento:** Conselho Nacional de Justiça, "Justiça em Números 2025" (PDF de 2025-10-09, 652 páginas). Fonte do pessoal: o sistema MPM, enviado mensalmente pelos tribunais.
- **Link:** https://www.cnj.jus.br/wp-content/uploads/2025/10/justica-em-numeros-2025.pdf
- **Definição (seção 2.1.2):** "servidores(as), incluindo o quadro efetivo, os(as) requisitados(as) e os(as) cedidos(as) de outros órgãos pertencentes ou não à estrutura do Poder Judiciário, além dos comissionados sem vínculo efetivo, excluindo-se os(as) servidores(as) do quadro efetivo que estão requisitados(as) ou cedidos(as) para outros órgãos". Terceirizados e estagiários ficam à parte ("força de trabalho auxiliar").
- **O Justiça em Números não traz quantidade de aposentados nem de pensionistas** (só a despesa com inativos). Por ramo, aposentados e pensionistas ficam sem número nesta pesquisa.

| Órgão ou ramo da União | Magistrados | Servidores | dos quais do quadro efetivo | Onde no documento |
|---|---:|---:|---:|---|
| STF | 11 ministros (mais 39 juízes auxiliares cedidos de outros tribunais) | 1.177 | 999 | seção 2.2.2: "o STF contava com uma equipe de 1.227 pessoas, sendo 11 Ministros(as), 1.177 servidores(as) e 39 juízes(as) instrutores(as) ou auxiliares" |
| STJ | 33 | 2.871 | 2.571 | infográfico do STJ, p. 81 |
| TST | 27 | 2.386 | 2.094 | infográfico do TST, p. 82 |
| TSE | 14 | 890 | 786 | infográfico do TSE, p. 83 |
| Justiça Militar da União (STM e auditorias) | 54 | 1.139 | 774 | infográfico da JMU, p. 84 |
| Justiça Federal (TRFs e seções judiciárias) | 2.014 | 27.656 | 25.197 | "a Justiça Federal possuía um total de 27.656 servidores(as), dentre os quais 25.197 eram do quadro efetivo (91,1%)" |
| Justiça do Trabalho (TRTs) | 3.662 | 39.305 | 37.442 | "a Justiça do Trabalho possuía um total de 39.305 servidores(as), dentre os quais 37.442 eram do quadro efetivo (95,3%)" |
| Justiça Eleitoral (TREs) | 2.841 (ver nota) | 23.093 | 14.374 | "dentre os quais 14.374 eram do quadro efetivo (62,2%), 7.710 requisitados(as) ou cedidos(as) de outros órgãos (33,4%)" |
| TJDFT | 379 | 10.232 | não informado | Tabela 1, Justiça Estadual por porte |

Notas:
- O texto do STF diz "Dos(as) 1.777 servidores(as), a maioria, 999 (84,9%) eram efetivos"; 999 é 84,9% de 1.177, então "1.777" é erro de digitação do próprio relatório. Vale 1.177.
- Os magistrados da Justiça Eleitoral são, na maior parte, juízes estaduais e federais designados por mandato; não são cargos próprios da Justiça Eleitoral. E 7.710 servidores da Eleitoral são requisitados de outros órgãos (muitos de prefeituras e estados). Somar os 2.841 e os 23.093 como "pessoal pago pela União" contaria gente que não é da folha dela.
- O STF, os conselhos (CNJ, CJF, CSJT) e o TJDFT ficam fora dos segmentos "Federal" e "Trabalho" no relatório; os conselhos não aparecem com quantidade própria nas páginas lidas.
- Comparação de escala (não é conferência ao número): o RPPS conta 105.545 ativos no Judiciário em julho de 2025, com magistrados, só quadro efetivo, incluindo os cedidos para fora; o Justiça em Números soma 108.749 servidores (efetivos, requisitados de fora e comissionados sem vínculo) em dezembro de 2024, sem os magistrados. São conceitos diferentes e meses diferentes; não somar nem subtrair um do outro.

### Fonte 6. Câmara dos Deputados: "Anexo I - Quantitativo Físico de Pessoal", posição de dezembro de 2025

Todos os órgãos dos Poderes, o MPU e a DPU publicam as mesmas tabelas padronizadas ("TABELA 1 - PODERES EXECUTIVO, LEGISLATIVO E JUDICIÁRIO - DPU - MPU - EMPRESAS ESTATAIS DEPENDENTES DA UNIÃO"), com colunas de ativos (ocupados estáveis e não estáveis, vagos), inativos (aposentado, **instituidor de pensão**) e **beneficiário de pensão**. É o formato que separa instituidor (o servidor que morreu e deixou a pensão) de beneficiário (quem recebe).

- **Página:** https://www2.camara.leg.br/transparencia/recursos-humanos/servidores/quantitativos/2025
- **Servidores de cargo efetivo** (arquivo `copy_of_cargo-efetivo-aposentados-instituidores-de-pensao-e-pensionistas-31-12-2019`, apesar do nome traz "POSIÇÃO: DEZEMBRO DE 2025"; Departamento de Administração de Pessoal), linha TOTAL: ocupados 2.626 (2.349 estáveis e 277 não estáveis), vagos 743, **aposentados 3.291**, **instituidores de pensão 1.020**, **beneficiários de pensão 1.230**. Notas: 5 aposentados e 4 instituidores que eram de cargo em comissão ficam fora da tabela.
- **Deputados** (arquivo `copy_of_deputados-ativos-aposentados-pensionistas-31-12-2016`, "ANEXO I - QUANTITATIVO FÍSICO DE PESSOAL / TABELA 2 - MEMBROS", posição dezembro de 2025): 513 ativos, **376 aposentados, 436 instituidores e 468 beneficiários de pensão** (ex-deputados e seus pensionistas).
- **Secretários parlamentares** (Anexo III, posição dezembro de 2025, arquivo `TabelaSp31.08.2025.pdf`): **10.082 ocupantes**, dos quais 9.845 sem vínculo com o serviço público (192 e 45 nas duas colunas "com vínculo").
- **Cargos de natureza especial (CNE)** (Anexo III, dezembro de 2025): 1.738 ocupados, dos quais 1.685 sem vínculo; 65 vagos.
- **Contratados temporários** (Anexo V, dezembro de 2025): nenhum.

Consequência para o custo por pessoa: na Câmara a folha paga muito mais gente do que os 2.626 efetivos. Secretários parlamentares e CNE são de livre nomeação, contribuem para o INSS (não para o RPPS) e **não aparecem** nos 6.960 ativos do Legislativo da avaliação do RPPS. Dividir a folha da Câmara só pelos efetivos superestima o custo por pessoa.

### Fonte 7. Senado Federal: Anexo I, posição de dezembro de 2025 (sistema ERGON, Secretaria de Gestão de Pessoas)

- **Página:** https://www12.senado.leg.br/transparencia/rh/segp/arquivos
- **Servidores de cargo efetivo** (`01-quantitativo-fisico-de-pessoal_anexo_i_tabela-1_31122025_gerado12012026.pdf` e o CSV equivalente), linha TOTAL: estáveis 1.440, não estáveis 885, **ocupados 2.325**, vagos 984, **aposentados 3.653**, **instituidores de pensão 1.388**, **beneficiários de pensão 1.710**. A soma das linhas do CSV bate com a linha TOTAL do PDF nas nove colunas.
- **Senadores** (`02-quantitativo-de-parlamentares_anexo_i_tabela-2_301122025_gerado12012026.pdf`): 87 ocupados (nota: "Dos Senadores ativos, 6 encontram-se licenciados e/ou afastados"; 81 cadeiras mais 6 sugere que os suplentes em exercício entram na conta junto com os titulares licenciados, o que é leitura nossa, não frase do documento), **63 aposentados** (4 com aposentadoria suspensa por estarem em mandato), **59 instituidores** e **69 beneficiários de pensão**.
- **Cargos em comissão e funções de confiança** (Anexo III, posição de agosto de 2025; o de dezembro de 2025 não foi encontrado na pasta): 5.494 ocupados, dos quais **3.942 sem vínculo** com o serviço público; inclui 681 secretários parlamentares e 811 assessores parlamentares. Em abril de 2026: 5.350 ocupados, 4.012 sem vínculo.

### Fonte 8. DPU: Anexo I e Anexo III, posição de julho/agosto de 2026

- **Página:** https://www.dpu.def.br/transparencia-rh/cargos-efetivos-vagos (planilha `Portal_da_transparencia_JULHO_2026___DIDEP.xls`, abas "ANEXO I - TAB 1", "TAB 2" e "TAB 3").
- **Defensores (Tabela 2, posição 12/07/2026):** "DEFENSOR PÚBLICO DA UNIÃO | 680 ocupados | 17 vagos | 697 | 29 aposentados | 22 instituidores de pensão | 51 | 25 beneficiários de pensão".
- **Servidores do quadro próprio (Tabela 1, PCCDPU, posição "12.8.2026"):** 405 ocupados; 19 aposentados, 8 instituidores e 4 beneficiários de pensão.
- **Linha "TOTAL GERAL" da Tabela 1:** 48 aposentados (29 + 19), 30 instituidores (22 + 8), 29 beneficiários (25 + 4); a coluna "TOTAL" de inativos traz 89, que não bate com 48 + 30 = 78. Erro da própria planilha; usamos as colunas.
- **Requisitados de outros órgãos:** 676 (447 estatutários, 57 empregados CLT, 150 anistiados e outros). A mesma aba lista 391 cargos ocupados do PGPE redistribuídos para a DPU; a planilha não deixa claro se eles estão dentro dos 405 do PCCDPU ou fora. Não somamos.
- Na avaliação do RPPS, a DPU está **dentro do Executivo** (Fonte 1). Os aposentados antigos da DPU, do tempo em que o pessoal era do Executivo, ficam no SIAPE; a DPU tem poucos aposentados próprios porque a carreira é recente.

### Câmara, Senado e TCU separados: o que falta

- **TCU: não confirmado.** A página de transparência (https://portal.tcu.gov.br/transparencia-e-prestacao-de-contas/servico/tabelas-demonstrativas-do-quadro-de-pessoal) aponta para um sistema em `contas.tcu.gov.br` que devolveu "O acesso a este recurso foi bloqueado pela solução de firewall de aplicações do Tribunal de Contas da União" para o acesso automatizado, e o Wayback não tem cópia. Precisa abrir no Chrome do autor.
- Por isso o Legislativo só tem total na fonte do RPPS (6.960 ativos, 8.752 aposentados, 3.729 pensionistas, julho de 2025), e não dá para tirar o TCU por diferença: as tabelas da Câmara e do Senado são de dezembro de 2025, contam só cargo efetivo e incluem aposentados de cargos em comissão do regime antigo, enquanto o RPPS é de julho de 2025.
- **MPU por ramo (MPF, MPT, MPM, MPDFT): não pesquisado** por falta de tempo; o total está na Fonte 1.

## Aposentados e pensionistas da União são do RPPS, não do INSS

Confirmado na fonte:

1. **Constituição, art. 40, caput** (https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm): "O regime próprio de previdência social dos servidores titulares de cargos efetivos terá caráter contributivo e solidário, mediante contribuição do respectivo ente federativo, de servidores ativos, de aposentados e de pensionistas".
2. **Constituição, art. 40, § 13:** "Aplica-se ao agente público ocupante, exclusivamente, de cargo em comissão declarado em lei de livre nomeação e exoneração, de outro cargo temporário, inclusive mandato eletivo, ou de emprego público, o Regime Geral de Previdência Social." Ou seja: quem só tem cargo em comissão (secretários parlamentares, CNE sem vínculo), temporários e empregados públicos ficam no INSS; os servidores de cargo efetivo e seus pensionistas ficam no RPPS da União.
3. **A avaliação atuarial do PLDO 2027** se apresenta como a do "Regime Próprio de Previdência Social (RPPS) dos servidores civis, aposentados e pensionistas da União" (introdução, p. 5) e é feita pelo Ministério da Previdência separadamente da avaliação do RGPS (Anexo IV.10 do mesmo PLDO).
4. **Militares** não estão em nenhum dos dois: o Sistema de Proteção Social dos Militares das Forças Armadas (Fonte 3).
5. Detalhe: quem entrou depois da previdência complementar (4 de fevereiro de 2013 no Executivo e no Legislativo; 14 de outubro de 2013 no Judiciário e no MPU) continua no RPPS, mas com benefício limitado ao teto do RGPS (Fonte 1, item 2.1 c).

Consequência para o site: os números do INSS (RGPS, BEPS) e os da folha de aposentados federais (RTN 2.2.3) são de dois regimes diferentes e não se somam nem se comparam como se fossem o mesmo.

## O sistema de Justiça é o mais caro por servidor?

Pela mesma fonte e no mesmo mês (RPPS, julho de 2025, só cargo efetivo e membros), **não**: o Legislativo paga mais por pessoa, nos ativos e muito mais nos aposentados.

| Grupo | Remuneração média do ativo (R$/mês) | Provento médio do aposentado (R$/mês) | Provento médio do pensionista (R$/mês) |
|---|---:|---:|---:|
| Legislativo (Câmara, Senado, TCU) | 18.541,40 | 39.389,57 | 25.356,55 |
| MPU | 16.663,22 | 23.664,18 | 17.383,86 |
| Judiciário | 14.977,90 | 22.056,80 | 16.016,67 |
| Executivo (com DPU, BCB, ABIN) | 13.369,72 | 12.013,58 | 7.050,41 |

Ressalvas:
- São médias de todo o quadro efetivo, de magistrados e ministros a técnicos; o documento não define nas páginas lidas se a "remuneração média" inclui auxílios e verbas indenizatórias. Leia como a base previdenciária, não como o contracheque bruto.
- O Judiciário tem muito mais gente (105.545 ativos contra 6.960 do Legislativo), então gasta muito mais no total (R$ 28,1 bi contra R$ 7,4 bi de janeiro a julho de 2026 na folha do projeto), mas menos por pessoa.
- **Militares** (Fonte 3, maio de 2025): oficial de carreira R$ 21.456,96 e praça de carreira R$ 8.854,28 em média, mas 58,7% dos ativos são temporários com média de R$ 2.486,77 (praças) a R$ 12.840,88 (oficiais).

**Para o site calcular custo por pessoa direito**, ainda falta:
1. Separar a folha de cada Poder em ativos e inativos. O RTN separa ativo e inativo só no total da União (2.2.1 a 2.2.4); por Poder, a base do Tesouro tem o elemento de despesa (01 aposentadorias, 03 pensões, 11 vencimentos), que já é usado no Executivo em `BRASIL-IMPOSTO_RESEARCH_folha-federal-por-uf_2026-10-01.md`.
2. Contar no denominador dos ativos quem a folha paga e o RPPS não conta: secretários parlamentares e CNE da Câmara (cerca de 11.500 sem vínculo em dezembro de 2025), comissionados sem vínculo do Senado (3.942 em agosto de 2025) e os comissionados sem vínculo do Judiciário (26.168 em todo o Judiciário, inclusive estadual, no Justiça em Números). Sem isso, o custo por pessoa do Legislativo sai inflado.
3. Usar a mesma data no numerador e no denominador, ou dizer que não usa.

## Pendências

| # | O que | Situação |
|---|---|---|
| 1 | TCU separado (ativos, aposentados, pensionistas) | Não confirmado: firewall do TCU; abrir no Chrome do autor |
| 2 | Aposentados e pensionistas do Judiciário por ramo | Não encontrado em fonte consolidada; cada tribunal publica o Anexo I (ex.: TRF3, por seção judiciária), seria preciso juntar cerca de 90 arquivos |
| 3 | MPU por ramo | Não pesquisado |
| 4 | Por que o Executivo perdeu 25.406 aposentados de julho de 2024 para julho de 2025 no RPPS | Não explicado nas páginas lidas |
| 5 | Por que o Executivo tem 663.308 ativos no RPPS e o SIAPE de agosto de 2026 tem 471.127 servidores em exercício (`data/df/segrt_servidores_uf_202608.json`) | Não conciliado; o RPPS inclui BCB, ABIN, DPU, ex-territórios e órgãos fora do SIAPE, mas a diferença é grande demais para fechar sem a base |
| 6 | Policiais e bombeiros do DF pagos pelo FCDF | Sem quantidade de pessoas nas fontes lidas (só valores atuariais) |
| 7 | Deputados e senadores aposentados: de que plano vêm (o extinto IPC e o PSSC, Lei 9.506/1997) | Não conferido na fonte nesta pesquisa |
