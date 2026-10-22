# Contorno Viário da Grande Florianópolis (BR-101/SC): obra, prazos, custo, quem paga, achados oficiais e comparação

**Data da coleta:** 2026-10-06 (todas as consultas nesta data, salvo indicação)
**Pergunta:** o que é o Contorno, o que o contrato de concessão de 2008 pedia e quando, quando cada trecho abriu e por que atrasou, quanto custou segundo os documentos oficiais, quem paga (pedágio ou imposto), o que os órgãos de controle disseram, e quanto custa por km em comparação com obras parecidas.
**Pistas do autor (D100):** "superfaturado" (palavra dele) e a afirmação de que a obra teve muitos atrasos e levou muitos anos a mais do que devia (tradução da mensagem dele). Tratadas como pistas e conferidas nos documentos (seção 9).
**Dados:** `data/works/florianopolis-bypass.json`. **Script:** `pipelines/works/build_florianopolis_bypass.py`.

## Regras desta pesquisa

1. Só papéis e achados oficiais, com as palavras do órgão. Nenhuma inferência de irregularidade.
2. Nenhum número sem URL oficial, ano de referência e data da coleta. Somas marcadas como "calculado" são desta pesquisa.
3. Travessões dos originais trocados por vírgula ou hífen (regra de estilo do projeto).
4. Nenhuma informação de candidatura de 2026 (D54).

## 0. Resumo

| Item | Resultado | Fonte principal |
|---|---|---|
| Investimento total (primeiro número do cartão) | ✅ **R$ 3,9 bilhões**, investimento declarado pela concessionária (nominal, 2014 a 2024); dinheiro da concessionária recuperado pelo pedágio, **sem dinheiro do Orçamento da União** (SIOP, 2008 a 2026, com controle) | DFP 2024 da Autopista Litoral Sul (CVM), ANTT, BNDES |
| Contrato inicial | ✅ R$ 175.951.204,31 (preços de jul/2007) pelos 47,33 km na proposta vencedora; R$ 466,9 mi em reais de dez/2024 | proposta (ANTT), TCU |
| Prazo | ✅ contrato: fim do 4º ano (fev/2012); aberto em 09/08/2024: **12 anos e 6 meses de atraso** (16,5 anos de concessão contra 4 previstos) | PER, TCU, DFP 2024 |
| Pedágio | ✅ a revisão que incluiu o trecho Sul A levou o pedágio do carro de R$ 2,70 para R$ 3,90 nas cinco praças (12/12/2020); R$ 0,42193 da TBP vêm do Contorno | Deliberação ANTT 500/2020; Voto DDB 120/2020 |
| Achados | ✅ TCU multou três servidores da ANTT pelo adiamento de 2009 (2019, mantido em 2020); a unidade técnica do TCU apontou "sobrepreço" de R$ 203,1 mi, depois R$ 136,6 mi, no Sul A (2020); a ANTT cortou R$ 16,3 mi e o TCU encerrou como "não cumprida" (2024); obra concluída com desapropriações pendentes (2025) | TCU |
| Pistas do autor | "superfaturado": nenhum documento usa o termo; há "sobrepreço" apontado pela unidade técnica, com R$ 120,3 mi sem corte. Atrasos: confirmados | seção 9 |
| Pessoas | ✅ 9 agentes da ANTT com ato e link; presidentes Lula (PT), Dilma (PT) e Bolsonaro (partido em dez/2020 não confirmado) | contrato, TCU, ANTT, TSE |
| Empresas | ✅ Autopista Litoral Sul (09.313.969/0001-97), Arteris (02.919.555/0001-67); ⚠️ uma construtora nomeada (contrato rescindido), sem CNPJ; as demais não aparecem em documento oficial | CNPJ.ws, CVM, DFP |
| Comparação | ✅ R$ 35,3 mi/km pelo valor regulatório (igual ao projeto do Contorno de Goiânia, R$ 35,0 mi/km); R$ 78,0 mi/km pelo investimento declarado (nominal) | ANTT, TCU, IBGE |
| Foto | ✅ uma foto livre da obra (Túnel 2), recortada sem as autoridades | Wikimedia Commons |

## 1. A obra

- **Nome nos documentos:** "Contorno de Florianópolis" (PER, TCU, ANTT), "Contorno Rodoviário de Florianópolis" (TCU), "Contorno Viário da Grande Florianópolis" (ANTT, 2024) e "Contorno Viário de Florianópolis" (concessionária).
- **O que é:** uma rodovia nova em pista dupla, a oeste da BR-101, que tira o tráfego de longa distância do trecho urbano da BR-101 entre Biguaçu e Palhoça (Grande Florianópolis). Faz parte do contrato de concessão da Autopista Litoral Sul (BR-116/376/PR e BR-101/SC, Curitiba a Palhoça), da ANTT.
- **Tamanho, como entregue:** "corredor expresso de 50 km de pistas duplas, 6 acessos por trevos, 4 túneis duplos, 7 pontes e mais 20 passagens em desnível" (nota 1 das Demonstrações Financeiras de 2024 da concessionária, DFP entregue à CVM e publicada pela ANTT; [PDF](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/relatorios/relatorios-financeiros/df-4degtri2024-litoral-sul.pdf), lido em 2026-10-06). O relatório da administração no mesmo arquivo conta por sentido: "8 túneis, 14 pontes, 20 passagens em desnível, 6 trevos, e 44 obras de arte especiais". A ANTT repete "50 quilômetros", "quatro túneis duplos e seis acessos por trevos" ([notícia de 06/08/2024](https://www.gov.br/antt/pt-br/assuntos/ultimas-noticias/maior-obra-de-infraestrutura-terrestre-da-america-latina-sera-inaugurada-em-santa-catarina-nesta-sexta-feira-9-8)).
- **Tamanho no contrato de 2008:** "Contorno de Florianópolis, em pista dupla, com 47,33 km em cada sentido (total de 94,66 km)" (PER original, item 5.1.4, p. 83; [PDF da ANTT](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/documentos-de-gestao/contrato-e-anexos/anexos-do-contrato/per-original.pdf)). O mesmo PER, no esquema linear, marca o início do contorno no km 196,1 (Antônio Carlos, SC-408) e o fim no km 220,0 da BR-101; o TCU chamou isso de "única inconsistência no PER" e tomou os 47,33 km do edital e da proposta como a extensão contratual (Acórdão 2954/2011, relatório).
- **Trecho "Sul A":** 7,91 km (km 220+396 a km 228+310) com "3 (três) túneis duplos, 1 (uma) passagem inferior, 3 (três) passagens superiores e 2 (dois) viadutos", incluído em 2020 por termo aditivo porque a ANTT apontou "a necessidade de alteração de traçado do Contorno de Florianópolis, especificamente pelo crescimento da mancha urbana de Palhoça/SC" (Termo Aditivo nº 002/2020, considerandos e Anexo I; [PDF da ANTT](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/documentos-de-gestao/contrato-e-anexos/termos-aditivos/termo-aditivo-autopista-litoral-sul-contorno-de-florianopolis.pdf)).
- **Municípios:** a ANTT e o BNDES falam em "ao menos nove cidades, entre Santo Amaro da Imperatriz e Tijucas" afetadas; o traçado passa por Biguaçu, São José e Palhoça (PER e TA 002/2020: km 196 a 228 da BR-101, de Biguaçu a Palhoça).
- **Nível e órgão:** federal. Poder concedente: União, por meio da ANTT (autarquia federal). Função (SICONFI): Transporte.

## 2. A concessão e o lugar do Contorno no contrato

- **Contrato:** Edital ANTT nº 003/2007, Lote 07, BR-116/376/PR e BR-101/SC, trecho Curitiba a Palhoça (Florianópolis). Página da concessão na ANTT ([link](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul), lida em 2026-10-06): "Data da Assinatura: 14/02/2008", "Início da Concessão: 18/02/2008", "Prazo da Concessão: 25 anos", "Início da Cobrança de Pedágio: 22/02/2009", extensão de 405,90 km, controladora Arteris S/A. (O TCU escreve "assinatura do contrato (22/02/2008)" no Acórdão 3346/2012; a data da ANTT é a da página oficial da concessão.)
- **Tamanho do contrato:** "investimentos de R$ 1.505.060.776,07 e receita de R$ 5.987.643.947,77, ao longo do período de 25 anos de concessão" (TCU, Acórdão 1366/2019, voto, item 3; valores da proposta, preços de 2007).
- **O Contorno no contrato:** obra obrigatória, item 5.1.4 do PER original, "a ser executado até o final do 4º ano" (fevereiro de 2012). O TCU: "As obras de construção do Contorno de Florianópolis são as principais obras a cargo do concessionário e as de maior valor individual (R$ 175.951.204,31, Peça 64, p. 12). Segundo o PER original da licitação (item 5.1.4., Peça 33), deveriam ser concluídas até o final do quarto ano de concessão, em fevereiro de 2012" (Acórdão 2954/2011, relatório).
- **Obras associadas no PER original:** trevos completos no Contorno (4 em pista simples e 3 em pista dupla, "até o final do 2º ano"), 4 passagens inferiores tipo galeria e 12 viadutos no Contorno ("até o final do 3º/4º ano").
- **Quem paga:** a concessionária constrói com dinheiro próprio e financiamento, e recupera o investimento pela tarifa de pedágio, nos termos do contrato. Cada obra nova entra pelo reequilíbrio: "A recomposição do equilíbrio do valor determinado na subcláusula 2.1 ocorrerá de forma integral à Tarifa Básica de Pedágio (TBP)" (TA 002/2020, cláusula 3.3). Detalhes na seção 4.

## 3. Linha do tempo: prazo do contrato e aberturas reais

| Data | Fato | Fonte |
|---|---|---|
| 1999 | Projeto do contorno feito pelo DNER, com 47,33 km do km 175 ao km 220 da BR-101, usado como referência da licitação | TCU, Acórdão 1043/2014, relatório |
| 14/02/2008 | Assinatura do contrato de concessão (início da concessão em 18/02/2008) | [ANTT, página da concessão](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul) |
| fev/2012 | **Prazo original:** fim do 4º ano da concessão ("deveriam ser concluídas até o final do quarto ano de concessão, em fevereiro de 2012") | PER original, item 5.1.4; TCU, Acórdão 2954/2011 |
| 19/02/2009 | A concessionária abre o licenciamento ambiental no Ibama, "praticamente um ano após a assinatura do contrato", com os mesmos dados do projeto de 1999 | TCU, Acórdão 1366/2019, voto, citando o Acórdão 3346/2012 |
| 05/11/2009 | Resolução ANTT 3.312 e 1ª Revisão Extraordinária adiam o Contorno em três anos (Nota Técnica 137/2009: de "2º ao 4º ano" para "5º ao 7º ano") | TCU, Acórdãos 2954/2011 e 1366/2019 |
| 31/03/2010 | Ofício 295/2010/GEINV/SUINF aprova projeto alterado, com 33,9 km (início no km 196) em vez de 47,33 km (início no km 175) | TCU, Acórdãos 1366/2019 e 1043/2014 |
| 05/12/2012 | TCU manda a ANTT não adiar de novo o prazo "prevista para fevereiro de 2015" e manter 47,33 km | TCU, Acórdão 3346/2012 |
| 28/08/2013 | Termo de Ajuste de Conduta (TAC) ANTT e concessionária, vigente a partir de 1º/9/2013: Contorno a executar "entre março de 2014 e fevereiro de 2016" | TCU, Acórdão 2957/2020, relatório; DOU de 28/12/2013 citado no Acórdão 1179/2016 |
| mai/2014 | Início das obras ("foi iniciado em maio de 2014"); primeiro trecho: Intermediário 03, km 211+543 a 215+682, São José | DFP 2021 a 2024 da concessionária; ANTT, relatório mensal de jul/2024 |
| 11/11/2015 | TCU, em embargos, troca o prazo fixo por "fixe a data de conclusão ... tendo em vista as características do novo traçado" | TCU, Acórdão 2883/2015 |
| 2020 | "Termo de Ajuste de Conduta Parcial" entre MPF, concessionária e os municípios de Biguaçu e Palhoça, com novos prazos | TCU, Acórdão 2802/2022, voto |
| 10/12/2020 | Termo Aditivo nº 002/2020 inclui o trecho Sul A (7,91 km, 3 túneis duplos) | ANTT |
| 13/12/2022 | TCU registra "novo prazo de conclusão estimado para fevereiro de 2024" depois de "atrasos e paralisações por conta de problemas com o traçado da rodovia, licenciamento ambiental e desapropriação" | TCU, Acórdão 2802/2022, voto |
| **09/08/2024** | **Inauguração e liberação ao tráfego de todo o Contorno** ("Em 09 de agosto de 2024, a Sociedade inaugurou o Contorno Viário de Florianópolis"; o relatório da administração diz "deu início a sua operação em 10/08/2024") | DFP 2024 da concessionária; [ANTT, 06/08/2024](https://www.gov.br/antt/pt-br/assuntos/ultimas-noticias/maior-obra-de-infraestrutura-terrestre-da-america-latina-sera-inaugurada-em-santa-catarina-nesta-sexta-feira-9-8); BNDES, 09/08/2024 |
| 10/09/2025 | TCU: "as obras foram concluídas, restando pendente desapropriações, que têm muitos trechos com objeção e/ou com ressalvas" | TCU, Acórdão de Relação 2062/2025 |

**Aberturas parciais:** o único trecho que os documentos lidos dão como em operação antes de agosto de 2024 é o trevo do km 215+380 ("que já se encontrava em operação", DFP 2021 e 2022). O tronco do Contorno abriu inteiro em 09/08/2024. Não achei documento oficial de abertura parcial do tronco (ver seção 12).

**Contas do atraso (calculado):** previsto para fev/2012, aberto em ago/2024: **12 anos e 6 meses depois do prazo original**. Do início da concessão (fev/2008) à abertura: 16 anos e 6 meses, contra 4 anos previstos. Do início das obras (mai/2014) à abertura: 10 anos e 3 meses. Contra o último prazo estimado registrado pelo TCU (fev/2024): 6 meses depois.

**Motivos do atraso nos documentos oficiais:**
- TCU (2011 e 2012): "os atrasos na elaboração dos estudos e projetos do Contorno de Florianópolis ocorreram por responsabilidade exclusiva da Concessionária"; a concessionária "demorou um ano para requerer abertura do processo de licenciamento ambiental" e "13 meses, após o encaminhamento do Termo de Referência Definitivo pelo IBAMA" para dar continuidade (Acórdão 3346/2012, citado no 1366/2019).
- TCU (2019): sobre a Nota Técnica 137/2009 da ANTT que adiou a obra, "os técnicos da ANTT fizeram um exame extremamente superficial que não foi embasado em estudos prévios"; a única justificativa da nota era "Segundo a concessionária, para o início desses serviços são necessários vários estudos quanto a impactos ambientais" (Acórdão 1366/2019, voto).
- Defesa dos servidores da ANTT no TCU: os atrasos "decorrem das atuações de vários atores, desde órgãos ambientais, passando pelo Poder Judiciário (no caso das desapropriações), pelo Ministério dos Transportes, pelo Dnit e até pelo extinto DNER" (Acórdão 1366/2019, voto, item 17.3).
- Justiça Federal: a 3ª Turma do TRF4, na Apelação 5014533-38.2012.4.04.7200/SC, "em 29/11/2018, confirmou a decisão de primeiro grau que havia concluído pela impossibilidade de imputação de responsabilidade à ANTT pelo atraso das obras obrigatórias", com trânsito em julgado em 08/02/2019 (citado no Acórdão 1366/2019, voto, item 18).
- ANTT (2020): mudança de traçado "pelo crescimento da mancha urbana de Palhoça/SC, sobre a área prevista inicialmente para a obra" (TA 002/2020).
- TCU (2022): "atrasos e paralisações por conta de problemas com o traçado da rodovia, licenciamento ambiental e desapropriação" (Acórdão 2802/2022).

## 4. Dinheiro: custo previsto, custos oficiais posteriores, custo final e quem paga

### 4.1 Investimento total (o primeiro número do cartão)

**R$ 3,9 bilhões**, "investimento total" do Contorno, segundo o relatório da administração nas Demonstrações Financeiras Padronizadas (DFP) de 31/12/2024 da Autopista Litoral Sul, entregues à CVM e publicadas pela ANTT ("Com um investimento total de R$ 3,9 bilhões, o Contorno foi projetado para melhorar significativamente a mobilidade"; [PDF na ANTT](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/relatorios/relatorios-financeiros/df-4degtri2024-litoral-sul.pdf), p. 22 do arquivo da CVM, lido em 2026-10-06). A ANTT repete o número ("com um investimento de R$ 3,9 bilhões", [notícia de 06/08/2024](https://www.gov.br/antt/pt-br/assuntos/ultimas-noticias/maior-obra-de-infraestrutura-terrestre-da-america-latina-sera-inaugurada-em-santa-catarina-nesta-sexta-feira-9-8)), e o BNDES também ("O contorno, que recebeu R$ 3,9 bilhões em investimentos", notícia de 09/08/2024, retirada do ar no defeso eleitoral de 2026 e lida pela [cópia do Internet Archive](https://web.archive.org/web/20260606013112/https://agenciadenoticias.bndes.gov.br/cultura/Com-apoio-do-BNDES-Contorno-Viario-de-Florianopolis-e-inaugurado/)).

- **O que mede:** dinheiro investido pela concessionária na obra, de 2014 a 2024, em valores nominais (reais de cada ano, sem correção). É dinheiro da concessionária (capital próprio e dívida), recuperado pela tarifa de pedágio; **não é dinheiro do Orçamento da União** (seção 4.4).
- **Precisão:** os três documentos oficiais trazem o número arredondado (R$ 3,9 bi). Nenhum documento lido traz o valor ao centavo nem a divisão por ano ou por trecho. As DFP de 2021 a 2025 trazem o investimento anual da concessionária inteira (todas as obras), não só o Contorno: R$ 398,8 mi (2020), R$ 893,2 mi (2021), R$ 1.133,4 mi (2022), R$ 1.206,8 mi (2023), R$ 916,3 mi (2024) e R$ 309,2 mi (2025).

### 4.2 Custo previsto no contrato (2007/2008)

- **Proposta vencedora, planilha do PER, item 5.1.2:** "Contorno de Florianópolis - Pista Dupla - L = 47,33 x 2 = 94,66 km", **R$ 175.951.204,31**, a preços de julho de 2007 ("Proposta Comercial, Cronograma Físico e Plano Econômico-Financeiro", PDF escaneado de 282 páginas, p. 211 do arquivo, p. 207 da proposta; [ANTT](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/documentos-de-gestao/processo-de-licitacao/proposta-comercial-cronograma-fisico-e-plano-economico-financeiro.pdf); lido por OCR e conferido na imagem recortada da linha). O mesmo valor está no TCU ("R$ 175.951.204,31, Peça 64, p. 12", Acórdão 2954/2011) e na planilha de execução da ANTT (R$ 175.951.204,30).
- **Obras associadas** (trevos, passagens e viadutos do Contorno): R$ 81.715.204,00; **verba de desapropriação** da concessão inteira, "a maior parte" para o Contorno: R$ 100.710.500,00. O TCU somou: "a postergação das obras relativas ao contorno de Florianópolis envolve o adiamento de um investimento não inferior a R$ 330 milhões (Contorno: R$ 175.951.204,31; Obras associadas: R$ 81.715.204,00 e Desapropriação: R$ 80.000.000,0)" (Acórdão 2954/2011, relatório). Soma conferida: R$ 337.666.408,31.
- Em reais de dez/2024 (IPCA, IBGE/SIDRA tabela 1737, jul/2007 = 2.675,79, dez/2024 = 7.100,50): o valor da proposta para o Contorno equivale a **R$ 466,9 mi** (calculado).

### 4.3 Custos oficiais posteriores

| Data | Valor | O que é | Fonte |
|---|---|---|---|
| 2016 | R$ 228 mi (proposta × 1,3) contra até R$ 600 mi | estimativas do TCU para remunerar o aumento de extensão (obra nova contra preço por km da proposta) | TCU, Acórdão 1179/2016, relatório |
| 2020 (ref. jan/2019) | cerca de R$ 500 mi | "os investimentos já contratados para a execução do Contorno de Florianópolis (extensão de 47,33 km)" | TCU, Acórdão 2957/2020 |
| 2020 (ref. jan/2019) | cerca de R$ 1,64 bi | orçamento do trecho Sul A "estimado inicialmente pela concessionária" | ANTT, Voto DDB 120/2020 |
| 2020 (ref. jan/2019) | R$ 923.846.486,36 | orçamento do Sul A aprovado pela área técnica da ANTT | TCU, Acórdãos 2112/2020 e 2957/2020 |
| 2020 (ref. jan/2019) | R$ 907.537.042,19 | orçamento ajustado pela ANTT, "redução de R$ 16.309.444,17" | TCU, Acórdão 2957/2020, declaração do Ministro Benjamin Zymler |
| 08/12/2020 (ref. jan/2019) | **R$ 907.409.977,72** | valor final do reequilíbrio do Sul A: R$ 854.113.307,34 de obra mais 6,24% de custos administrativos | ANTT, Voto DDB 120/2020 ([PDF](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/revisoes-e-reajustes/2020-1/sei_antt-4693800-voto-ddb-120_2020.pdf)) |
| 10/12/2020 (preços de jul/2007) | **R$ 491.251.185,69** | o mesmo Sul A no contrato: R$ 462.397.576,89 de obra mais R$ 28.853.608,80 de custos administrativos, em quatro anos de concessão | Termo Aditivo nº 002/2020, cláusula 2.1 e Quadro 1 |
| 2026 (preços de jul/2007) | R$ 664.672.742,58 (calculado) | itens só do Contorno na planilha de execução da ANTT (18º ano): PER original R$ 175.951.204,30; Sul A R$ 461.243.802,12; duas passagens do Sul B R$ 4.396.976,69 e R$ 11.266.671,93; trevos do Contorno R$ 11.814.087,54 | [ANTT, planilha de execução acumulada](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/documentos-de-gestao/acompanhamento-de-obras/execucao-acumulada-de-obras-de-ampliacao-de-capacidade-e-melhorias) |

Notas: (1) a planilha da ANTT dá o item do PER original como 100% executado, mas com valor executado de R$ 165.235.775,96 contra o total de R$ 175.951.204,30; a planilha não explica a diferença de R$ 10.715.428,34. (2) O Sul A na planilha (R$ 461.243.802,12) é R$ 1.153.774,77 menor que no termo aditivo (R$ 462.397.576,89); o aditivo previa que o valor "poderá ser alterado a menor" pela análise do projeto de automação e ITS (cláusula 2.1.2), mas a planilha não diz o motivo. (3) Estes valores são o que a tarifa remunera (valor regulatório), não o dinheiro gasto pela concessionária.

### 4.4 Quem paga: pedágio, não imposto

- **Contrato:** a obra é encargo da concessionária, remunerada pela tarifa. Cada inclusão de obra nova muda a Tarifa Básica de Pedágio (TBP): "A recomposição do equilíbrio do valor determinado na subcláusula 2.1 ocorrerá de forma integral à Tarifa Básica de Pedágio (TBP)" (TA 002/2020, cl. 3.3).
- **Aumento de pedágio ligado ao Contorno:** a Deliberação ANTT nº 500, de 08/12/2020 (DOU de 09/12/2020; [PDF](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/revisoes-e-reajustes/2020-1/deliberacao-500-de-08-12-2020.pdf)), aprovou a 14ª Revisão Extraordinária, "alterando a Tarifa Básica de Pedágio de R$ 1,43948 para R$ 1,93101", e levou o pedágio do carro "de R$ 2,70 (dois reais e setenta centavos) para R$ 3,90 (três reais e noventa centavos), nas praças de pedágio P1, em São José dos Pinhais/PR, P2, em Garuva/SC, P3, em Araquari/SC, P4, em Porto Belo/SC, e P5, em Palhoça/SC", a partir de 12/12/2020 (44,44% depois do arredondamento, somando revisão ordinária, revisão extraordinária e IPCA). Dos R$ 0,49153 de aumento da TBP na revisão extraordinária, R$ 0,40039 (28,20055%) são do Contorno e R$ 0,02154 (1,51716%) dos custos administrativos dele (ANTT, Voto DDB 120/2020, Figura 06, "Impacto percentual sobre a TBP - Contorno de Florianópolis"). O voto não mostra o efeito, na mesma revisão, das outras obras aprovadas na mesma deliberação (terceira faixa da BR-101 entre Palhoça e Biguaçu e ponte sobre o Rio Camboriú); a diferença de R$ 0,06960 fica sem divisão publicada.
- **Orçamento da União:** nenhuma ação orçamentária federal com "Contorno" e "Florianópolis" (nem Palhoça ou Biguaçu) de 2008 a 2026 no SIOP (dados abertos do orçamento federal, endpoint SPARQL). Controle: a mesma consulta acha os contornos de Joinville, São Francisco do Sul, Chapecó e Araranguá. Nenhum documento lido fala em dinheiro do Tesouro na obra.
- **Banco público (empréstimo, não gasto):** o BNDES diz que "Em 2011, o BNDES financiou com R$ 703 milhões a Arteris Litoral Sul S.A" (para a concessão inteira) e que, na emissão de R$ 2 bilhões em debêntures de 2021, "O Banco subscreveu 6,7% das debêntures (R$ 134 milhões)"; a dívida com o BNDES foi quitada com essa emissão (notícia do BNDES de 09/08/2024, cópia do Internet Archive). É empréstimo a ser pago pela concessionária, não despesa do governo.
- **Desapropriações:** pagas pela concessionária, com a verba de R$ 100.710.500,00 da proposta; o que passar disso vai para a tarifa (cláusulas 6.37.d e 16.24, citadas no Acórdão 2954/2011). Em 2025 o TCU registrou desapropriações ainda pendentes (Acórdão de Relação 2062/2025).

## 5. Achados oficiais

Todos do TCU, lidos na íntegra pela API pública de acórdãos (`https://pesquisa.apps.tcu.gov.br/rest/publico/base/acordao-completo/documento?termo=KEY:ACORDAO-COMPLETO-<n>`), em 2026-10-06. A busca por "Contorno de Florianópolis" achou 24 deliberações (2000 a 2025); as que decidem algo sobre a obra estão abaixo.

### 5.1 Auditoria do contrato e o adiamento de 2009 (TC 005.534/2011-9)

| Decisão | Data | O que o TCU disse ou decidiu | Situação |
|---|---|---|---|
| Acórdão 2954/2011-Plenário (relator Marcos Bemquerer) | 09/11/2011 | Oitivas sobre a "postergação, em três anos, por meio da Resolução n. 3.312, de 05/11/2009, e da 1ª Revisão Extraordinária, das datas de conclusão de obras obrigatórias, dentre elas o Contorno de Florianópolis, sem que tivessem sido apresentadas justificativas válidas" e sobre a "alteração do projeto do Contorno de Florianópolis baseada em motivação insuficiente e inválida" (extensão reduzida em 18 km) | substituído pelas decisões seguintes |
| Acórdão 3346/2012-Plenário (Bemquerer) | 05/12/2012 | Determina à ANTT "abstenha-se de postergar novamente a data de conclusão do Contorno de Florianópolis (com extensão de 47,33 km) e das obras associadas, prevista para fevereiro de 2015", aplicar multa contratual se não concluído e fixar "prazo final e definitivo" | alterado em recursos (abaixo) |
| Acórdão 427/2013-Plenário (Bemquerer), embargos | 06/03/2013 | O Contorno "deverá passar ao largo das zonas urbanas, conforme o traçado original" | |
| Acórdão 1043/2014-Plenário (Benjamin Zymler), pedidos de reexame | 23/04/2014 | Tira o item que impedia a tarifa de incluir o Contorno antes da conclusão; manda a ANTT criar método para a valorização imobiliária das desapropriações | |
| Acórdão 2883/2015-Plenário (Zymler), embargos | 11/11/2015 | Troca o prazo fixo por: "fixe a data de conclusão do Contorno de Florianópolis e das obras associadas, tendo em vista as características do novo traçado" | |
| **Acórdão 1366/2019-Plenário (Bemquerer)** | 12/06/2019 | **Multa** (art. 58, II, da Lei 8.443/1992) a quatro servidores da ANTT pela nota técnica que adiou o Contorno e por falhas de fiscalização; o voto vê "negligência e imperícia tanto na conduta dos que elaboraram a Nota Técnica 137/2009/GEINV/SUINF ... quanto na atuação do que pautou suas decisões com base em um documento nitidamente sem respaldo técnico"; manda a ANTT apresentar "plano de ação ... para se garantir a implementação urgente do Contorno Rodoviário de Florianópolis" | multas mantidas para três (abaixo) |
| Acórdão 1416/2020-Plenário (Zymler), pedido de reexame | 03/06/2020 | Exclui a multa de um dos quatro (o diretor que relatou o voto da revisão) e mantém as outras três; o próprio texto registra que "a unidade técnica reconheceu que não houve dano ao erário" | **decidido**; pagamento das multas não verificado |
| Acórdão 2802/2022-Plenário (Bemquerer), monitoramento (TC 010.683/2013-5) | 13/12/2022 | Considera cumpridas ou em cumprimento as determinações; registra "atrasos e paralisações por conta de problemas com o traçado da rodovia, licenciamento ambiental e desapropriação" e "novo prazo de conclusão estimado para fevereiro de 2024"; arquiva | **encerrado** |

Multas do Acórdão 1366/2019 mantidas pelo 1416/2020: Mário Mondolfo (Superintendente de Exploração de Infraestrutura Rodoviária), R$ 15.000,00; Deuzedir Martins (Gerente de Engenharia e Investimentos de Rodovias), R$ 12.000,00; Rubens Narciso Peduti Dal Molin (Gerente de Fiscalização e Controle Operacional de Rodovias), R$ 10.000,00. A multa de Mário Rodrigues Júnior (Diretor da ANTT), R$ 17.000,00, foi excluída. As razões de justificativa de Bernardo José Figueiredo Gonçalves de Oliveira (Diretor-Geral da ANTT, que aprovou a Resolução 3.312/2009) foram acolhidas, sem multa. Nomes reproduzidos porque o acórdão aplicou sanção (mesma regra da ficha da BR-470).

### 5.2 O preço do trecho Sul A (TC 026.406/2020-9)

| Decisão | Data | O que o TCU disse ou decidiu | Situação |
|---|---|---|---|
| Representação da unidade técnica (SeinfraRodoviaAviação), referendada pelo Acórdão 2112/2020-Plenário (relator Raimundo Carreiro) | cautelar de 05/08/2020; acórdão de 12/08/2020 | "indícios de significativo sobrepreço no orçamento das obras de implantação do Contorno Rodoviário de Florianópolis e nos respectivos procedimentos de alteração da tarifa, no valor de R$ 203.122.754,88, equivalente a 22,99% do orçamento aprovado pela ANTT, de R$ 923.846.486,36"; cautelar para a ANTT não assinar o aditivo acima dos valores de referência nem aumentar o pedágio antes da obra | cautelar revogada em 04/11/2020 |
| **Acórdão 2957/2020-Plenário (Carreiro)** | 04/11/2020 | Representação "parcialmente procedente". A unidade técnica reduziu o valor para "um sobrepreço de R$ 136.563.993,32 (ref. janeiro/2019)"; o relator não condicionou o aditivo a cortar esse valor ("não cabe interferir, neste momento, na avaliação do orçamento do novo Trecho Sul A ... realizada pela ANTT no pleno exercício de sua competência regulatória"), mas o Plenário mandou a ANTT corrigir itens do orçamento e "realize tratativas com vistas a obter o valor justo dos investimentos, com redução estimada em R$ 136 milhões" (item 9.5, proposto pelo Ministro Benjamin Zymler, que escreveu que "os indícios de superestimativa nos valores dos investimentos não foram afastados") | determinações monitoradas |
| Acórdão de Relação 1836/2023-Plenário (Antonio Anastasia) | 06/09/2023 | Apensa a representação ao monitoramento (TC 006.219/2023-3) | |
| **Acórdão de Relação 2029/2024-Plenário (Anastasia)** | 25/09/2024 | Itens de correção do orçamento cumpridos; item 9.5 **"não cumprida"**: a ANTT negociou, "obtendo, contudo, alteração de valores consideravelmente aquém da estimativa do Tribunal (R$ 16.309.444,17, data-base: janeiro/2019)"; o TCU dispensou a continuidade do monitoramento porque a agência "adotou as medidas" e "restando motivado o não atendimento"; processo encerrado | **encerrado, sem multa nem débito** |

Diferença em aberto, calculada a partir dos números do TCU: a unidade técnica estimou R$ 136.563.993,32 de sobrepreço; a ANTT cortou R$ 16.309.444,17; restam **R$ 120.254.549,15 (ref. jan/2019) que o TCU apontou e que o encerramento do processo deixou sem corte**. É uma diferença sem explicação aceita pelo TCU, mas o TCU não a julgou dano nem aplicou sanção; a ANTT sustentou que o impacto seria "cerca de R$ 0,10 (2,6% do valor da tarifa de pedágio)" (Voto DDB 120/2020).

Conta da própria fonte: R$ 203.122.754,88 é 21,99% de R$ 923.846.486,36, não 22,99% como está escrito nos acórdãos; registro a diferença sem corrigir a citação.

### 5.3 Monitoramento da obra (TC 039.653/2020-0)

- Acórdão de Relação 2062/2025-Plenário (10/09/2025), monitoramento do Acórdão 2605/2020: "as obras foram concluídas, restando pendente desapropriações, que têm muitos trechos com objeção e/ou com ressalvas, havendo, ainda, sentença arbitral para cobrança do custo de arbitragem e honorários." (O acórdão não diz quem venceu a arbitragem.)

### 5.4 Justiça

- TRF4, 3ª Turma, Apelação/Remessa Necessária 5014533-38.2012.4.04.7200/SC: em 29/11/2018 confirmou a sentença que concluiu "pela impossibilidade de imputação de responsabilidade à ANTT pelo atraso das obras obrigatórias"; trânsito em julgado em 08/02/2019 (citado no voto do Acórdão TCU 1366/2019). Outras ações civis públicas citadas no mesmo voto: 5011157-44.2012.4.04.7200, 5007718-88.2013.4.04.7200 e 5004170-55.2013.4.04.7200. Não li as sentenças (seção 12).
- "Termo de Ajuste de Conduta Parcial" de 2020 entre MPF, concessionária e municípios de Biguaçu e Palhoça (citado no Acórdão TCU 2802/2022). Não li o termo.

### 5.5 Palavras usadas

Busca, nas 29 deliberações baixadas, por termos a até 1.500 caracteres de "Florianópolis" (controle: frase inventada com os dois termos, achados). "Superfaturamento": só em texto doutrinário genérico (Acórdão 427/2013), nunca sobre esta obra. "Sobrepreço": nos acórdãos 2112/2020, 2833/2020, 2957/2020 e 3248/2020, sobre o orçamento do Sul A. "Desvio": só como desvio de tráfego. "Dano ao erário": no 2957/2020 (declaração do Ministro-Substituto André Luís de Carvalho, sobre a "estimativa de dano ao erário" da unidade técnica) e no 1416/2020 ("não houve dano ao erário", sobre o adiamento de 2009).

## 6. Pessoas

Regra D48: só agentes públicos com papel num documento oficial, cada um com o ato e o link. Quem assinou pela empresa fica só aqui (D36). Nenhuma informação de candidatura de 2026. CPFs e documentos pessoais que aparecem nos PDFs não foram copiados.

| Nome | Cargo | Ato | Fonte |
|---|---|---|---|
| José Alexandre Nogueira de Resende | Diretor-Geral da ANTT | assinou o contrato de concessão (14/02/2008) | [Contrato, ANTT](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/documentos-de-gestao/contrato-e-anexos/contrato-e-aditivos/contrato.pdf), preâmbulo |
| Noboru Ofugi | Diretor da ANTT | assinou o contrato de concessão (14/02/2008) | idem |
| Bernardo José Figueiredo Gonçalves de Oliveira | Diretor-Geral da ANTT | aprovou a Resolução 3.312, de 05/11/2009, que adiou o Contorno em três anos; o TCU acolheu suas razões, sem multa | TCU, Acórdão 1366/2019 |
| Mário Rodrigues Júnior | Diretor da ANTT | apresentou o Voto 162/2009 que propôs a revisão; multa do TCU excluída no recurso | TCU, Acórdãos 1366/2019 e 1416/2020 |
| Mário Mondolfo | Superintendente de Exploração de Infraestrutura Rodoviária da ANTT | assinou a Nota Técnica 137/2009 (adiamento); multado em R$ 15.000,00 | TCU, Acórdãos 1366/2019 e 1416/2020 |
| Deuzedir Martins | Gerente de Engenharia e Investimentos de Rodovias da ANTT | assinou a Nota Técnica 137/2009 e o Ofício 295/2010 (aprovou o projeto alterado); multado em R$ 12.000,00 | idem |
| Rubens Narciso Peduti Dal Molin | Gerente de Fiscalização e Controle Operacional de Rodovias da ANTT | fiscalização do contrato; multado em R$ 10.000,00 | idem |
| Davi Ferreira Gomes Barreto | Diretor da ANTT | relator do Voto DDB 120/2020 (14ª Revisão Extraordinária e aditivo do Sul A), 08/12/2020 | [Voto DDB 120/2020](https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul/revisoes-e-reajustes/2020-1/sei_antt-4693800-voto-ddb-120_2020.pdf) |
| Marcelo Vinaud Prado | Diretor-Geral em exercício da ANTT | assinou a Deliberação 500/2020 (08/12/2020) e o Termo Aditivo nº 002/2020 (10/12/2020) | Deliberação 500/2020; TA 002/2020 |

Pela concessionária (só no registro, D36): José Carlos Ferreira de Oliveira Filho (Diretor Presidente) e Francisco Leonardo Moura da Costa (Diretor Administrativo-Financeiro) no contrato de 2008; Antonio Cesar Ribas Sass e Giane Luza Zimmer Freitas (diretores) no TA 002/2020.

**Chefe do governo em cada ato (obra federal):**

| Pessoa | Cargo | Atos no período | Partido na época | Fonte do partido |
|---|---|---|---|---|
| Luiz Inácio Lula da Silva | Presidente da República | contrato (14/02/2008); Resolução 3.312 (05/11/2009); Ofício 295/2010 (31/03/2010); inauguração (09/08/2024) | PT | TSE, candidaturas 2006 e 2022 ([2006](https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2006.zip), [2022](https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2022.zip)), situação ELEITO em 2022 |
| Dilma Vana Rousseff | Presidenta da República | TAC (28/08/2013); início das obras (mai/2014) | PT | TSE, candidaturas 2010 e 2014, ELEITO no 2º turno |
| Jair Messias Bolsonaro | Presidente da República | Deliberação 500/2020 e TA 002/2020 (dezembro de 2020) | eleito em 2018 pelo PSL (TSE); filiação em dez/2020 não confirmada em fonte oficial aberta (seção 12) | TSE, candidaturas 2018 e 2022 (em 2022, PL) |

Governadores de SC não entram: a obra é de concessão federal, e nenhum ato do Estado aparece nos documentos de contrato e pagamento lidos. (O Governo de SC aparece no TCU só como uma das vozes a favor do traçado original, Acórdão 427/2013.)

## 7. Empresas

Cadastro: base aberta do CNPJ da Receita Federal pelo espelho público CNPJ.ws (os espelhos BrasilAPI e minhareceita.org responderam HTTP 500 e 503 em 2026-10-06) e cadastro de companhias abertas da CVM ([cad_cia_aberta.csv](https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv)).

| Empresa | CNPJ | Papel | Cadastro | Fonte do papel |
|---|---|---|---|---|
| Autopista Litoral Sul S.A. | 09.313.969/0001-97 | concessionária; dona do investimento | ativa, matriz em São José dos Pinhais/PR, início em 21/01/2008; companhia aberta na CVM (categoria B, código 21997) | contrato de 2008; TA 002/2020 |
| Arteris S.A. | 02.919.555/0001-67 | controladora da concessionária | ativa, matriz em São Paulo/SP; companhia aberta na CVM (categoria B, código 19771) | página da concessão na ANTT ("Empresas Controladoras: ARTERIS S/A"); DFP 2024 |
| Azevedo & Travassos Infraestrutura Ltda. | não publicado nos documentos lidos | construtora contratada pela concessionária "como parte do contrato da obra do Contorno Viário de Florianópolis ... realizado em 19 de junho de 2023"; "Conforme comunicado ao mercado emitido em 10 de julho de 2023 a Litoral Sul rescindiu o contrato" | CNPJ não achado | DFP 2023, 2024 e 2025 da concessionária |

- **Site oficial:** a ANTT liga a concessão a `https://www.arteris.com.br/rodovias/litoral-sul/` (link na página oficial da concessão); a DFP cita `ri.arteris.com.br`. O nome bate sem ambiguidade com Arteris.
- **As outras construtoras do Contorno não aparecem em documento oficial aberto.** A obra é contratada pela concessionária (empresa privada), sem licitação pública; os relatórios mensais da ANTT (jan/2016, jan/2022, jul/2024) e as DFP não dão os nomes; o TCU fala só em "construtoras contratadas" e prevê no orçamento do Sul A que "cada um dos três túneis duplos será executado por construtoras independentes". Não procurei em notícias de imprensa.
- Azevedo & Travassos S.A. (CNPJ 61.351.532/0001-68, companhia aberta) tem nome parecido com a construtora, mas nenhum documento lido liga as duas; por isso o CNPJ dela não foi atribuído à construtora.

## 8. Comparação honesta

Unidade: reais de dezembro de 2024 por km de rodovia nova em pista dupla. Correção pelo IPCA (IBGE/SIDRA, tabela 1737; jul/2007 = 2.675,79; mar/2015 = 4.215,26; jan/2019 = 5.116,93; ago/2024 = 6.966,50; dez/2024 = 7.100,50). Extensão do Contorno: 50 km (ANTT e concessionária; o relatório mensal da ANTT diz "aproximadamente 51 km").

| Obra | Valor | Base | Em reais de dez/2024 | Por km | O que mede |
|---|---|---|---|---|---|
| Contorno de Florianópolis, investimento declarado | R$ 3,9 bi | nominal, 2014 a 2024 | pelo menos R$ 3,9 bi | **R$ 78,0 mi/km** (nominal; corrigido seria mais) | dinheiro investido pela concessionária (DFP 2024) |
| Contorno de Florianópolis, valor regulatório | R$ 664.672.742,58 | jul/2007 | R$ 1.763.781.465,92 | **R$ 35,3 mi/km** | o que a tarifa remunera pelos itens só do Contorno (planilha da ANTT) |
| Trecho Sul A (7,914 km, 3 túneis duplos) | R$ 907.409.977,72 | jan/2019 | R$ 1.259.166.052,07 | **R$ 159,1 mi/km** | orçamento final aprovado pela ANTT (Voto DDB 120/2020) |
| Contorno de Goiânia, projeto de 44 km "Classe Especial" (BR-060/153, não construído) | R$ 913.869.440,00 | mar/2015 | R$ 1.539.390.205,76 | **R$ 35,0 mi/km** | estimativa do projeto executivo citada pelo TCU (Acórdão 1174/2018, transcrito no Acórdão 2195/2019) |
| Contorno de Goiânia, previsto no PER, 30 km "classe 1A" (não construído) | R$ 233.622.469,57 | mar/2015 | R$ 393.531.204,52 | **R$ 13,1 mi/km** | idem |
| Proposta de 2007 para o Contorno (47,33 km) | R$ 175.951.204,31 | jul/2007 | R$ 466.905.671,30 | R$ 9,9 mi/km | preço da proposta vencedora, antes das mudanças de traçado |

Leitura: pelo valor que a tarifa remunera, o Contorno custou o mesmo por km (R$ 35,3 mi) que o projeto do Contorno de Goiânia na classe mais alta (R$ 35,0 mi), e tem quatro túneis duplos e 44 obras de arte especiais. Pelo dinheiro que a concessionária declara ter investido (R$ 3,9 bi, sem correção), o custo por km é mais que o dobro (R$ 78,0 mi). Os documentos não explicam a diferença entre os dois números (o primeiro está em preços de 2007 da proposta, o segundo é o gasto contábil, que inclui juros capitalizados durante a obra, segundo as DFP). O trecho Sul A, com três túneis em 7,9 km, é o pedaço mais caro por km.

Ressalvas: (1) Goiânia é projeto, não obra feita, e em terreno diferente; (2) nenhum dos valores está ao centavo do gasto final, porque a concessionária publica só o total arredondado; (3) o TCU cita custos médios de contornos de outros estudos (R$ 5,5 mi/km da Infra S.A.; R$ 11,7 mi/km da Eco101, base jan/2023), mas esses números medem "o custo das pistas" isolado, sem túneis e obras de arte, e por isso ficaram fora da tabela.

## 9. As duas pistas do autor, lado a lado com os documentos

| Pista do autor | O que os documentos oficiais dizem |
|---|---|
| "superfaturado" | Nenhum documento oficial lido usa "superfaturamento" para esta obra. A unidade técnica do TCU apontou "indícios de significativo sobrepreço" no orçamento do trecho Sul A (R$ 203,1 mi, depois R$ 136,6 mi, ref. jan/2019). O Plenário não barrou o aditivo, mas mandou a ANTT negociar "o valor justo dos investimentos, com redução estimada em R$ 136 milhões" (Acórdão 2957/2020). A ANTT conseguiu R$ 16,3 mi; o TCU registrou a determinação como "não cumprida" e encerrou o caso sem multa nem débito (Acórdão 2029/2024). Ficaram R$ 120,3 mi (jan/2019) apontados e não cortados. Antes disso, a própria ANTT cortou 45% do orçamento inicial da concessionária para o Sul A (de cerca de R$ 1,64 bi para R$ 907 mi). |
| muitos atrasos e anos a mais do que devia (pista do autor, em tradução) | Confirmado. O contrato mandava concluir até fevereiro de 2012; o Contorno abriu em 09/08/2024, **12 anos e 6 meses depois**. Os prazos foram adiados em 2009 (para fev/2015), em 2013 (TAC: até fev/2016) e de novo depois (estimativa de fev/2024). O TCU atribuiu o primeiro atraso à concessionária e multou três servidores da ANTT pelo adiamento de 2009 sem justificativa técnica; a Justiça Federal (TRF4) concluiu que o atraso não podia ser imputado à ANTT; o TCU registrou depois "problemas com o traçado da rodovia, licenciamento ambiental e desapropriação". |

## 10. Fotos

- Busca no Wikimedia Commons (API, 2026-10-06) por "Contorno Viário Florianópolis", "Contorno de Florianópolis", "Contorno Viário da Grande Florianópolis", "Contorno rodoviário Florianópolis", "túnel contorno Palhoça" e "BR-101 Biguaçu/Palhoça/São José". Só há 29 fotos com licença livre, todas da cerimônia de inauguração (09/08/2024), da conta "Lula Oficial" no Flickr, autor Ricardo Stuckert/PR, CC BY-SA 2.0. Abri e olhei todas numa folha de miniaturas: 24 mostram autoridades em primeiro plano ou a plateia; 3 mostram o emboque do Túnel 2 com um grupo de pessoas pequeno ao fundo; 2 mostram a placa de inauguração com nomes.
- **Escolhida:** `docs/superpowers/previews/assets/cases/florianopolis-bypass/tunnel-2-palhoca-2024.jpg`, a partir de [53912407328](https://commons.wikimedia.org/wiki/File:09.08.2024_-_Cerim%C3%B4nia_de_inaugura%C3%A7%C3%A3o_do_Contorno_Vi%C3%A1rio_da_Grande_Florian%C3%B3polis_(53912407328).jpg): emboque do Túnel 2 com a placa "Túnel 2 Extensão 908 m". Recortei a parte de cima, sem as pessoas da cerimônia (regra de neutralidade: a foto mostra a obra, não autoridades), 960 x 720 px; o recorte segue sob CC BY-SA 2.0, registrado em `credits.json` (campo `modification`).
- A foto mostra a própria obra. O conversor `road_case()` acrescenta a toda legenda "Mostra o entorno; não há foto de uso livre da obra.", o que estaria errado aqui; fica para o agente principal.

## 11. Diário de transparência

Todas as consultas em 2026-10-06, de um computador fora do Brasil.

| # | O que se buscou | Onde | Formato | Login | Resultado e obstáculos |
|---|---|---|---|---|---|
| 1 | Deliberações do TCU sobre o Contorno | API pública de acórdãos do TCU | JSON | não | ✅ 24 resultados para "Contorno de Florianópolis", mais 5 por número de processo; o firewall só aceita cabeçalho de navegador |
| 2 | Contrato, PER, aditivos, revisões | páginas da concessão na ANTT (gov.br) | PDF | não | ✅ o pedido HEAD dá 403, o GET funciona; os PDFs do SEI perdem a ligadura "ti" na extração de texto ("es mado"), e a checagem de citações foi adaptada |
| 3 | Preço da proposta de 2007 | ANTT, processo de licitação | PDF escaneado de 61 MB, sem texto | não | ✅ com esforço: OCR com o Vision do macOS e conferência na imagem recortada; o arquivo foi apagado depois |
| 4 | Investimento total | DFP da concessionária (2021 a 2025) publicadas pela ANTT | PDF | não | ✅ só o total arredondado (R$ 3,9 bi); nenhum valor por ano ou por trecho |
| 5 | Execução das obras | planilha de execução acumulada da ANTT (18º ano) | XLSX | não | ✅ valores a preços de jul/2007 |
| 6 | Construtoras | relatórios mensais da ANTT (jan/2016, jan/2022, jul/2024), DFP, TCU | PDF | não | ⚠️ só uma construtora nomeada (DFP); os relatórios não trazem nomes |
| 7 | Dinheiro da União | SIOP, endpoint SPARQL | JSON | não | ✅ zero ações de 2008 a 2026; controle acha outros contornos em SC |
| 8 | Aberturas e valor | notícias da ANTT e do BNDES | HTML | não | ✅ a notícia do BNDES saiu do ar no defeso eleitoral de 2026 e foi lida pelo Internet Archive; o aviso de pauta do Ministério dos Transportes pede login ("Conteúdo Restrito") e o Planalto pediu captcha |
| 9 | CNPJ | BrasilAPI, minhareceita.org, CNPJ.ws; cadastro da CVM | JSON, CSV | não | ⚠️ BrasilAPI (500) e minhareceita (503) fora; CNPJ.ws respondeu |
| 10 | Partido dos presidentes | TSE (candidaturas 2006 a 2022); Biblioteca da Presidência; listas de filiados do TSE | ZIP, HTML | não | ⚠️ candidaturas ok; biografia "em manutenção"; listas de filiados com 404 |
| 11 | Fotos | API do Wikimedia Commons | JSON, JPG | não | ✅ 29 fotos, todas da inauguração; uma recortada |
| 12 | MPF e sentenças da Justiça | só citações no TCU | | | ❌ não li as ações nem o TAC Parcial de 2020 |

**Em resumo:** numa concessão, o dinheiro não passa pelo orçamento público, e por isso não aparece no Portal da Transparência nem no SIOP. O que existe aberto é o valor regulatório (contrato, aditivos, planilha da ANTT, a preços de 2007) e o total que a concessionária declara à CVM, arredondado. A conta ao centavo do que foi gasto não está publicada em lugar nenhum que eu tenha achado.

## 12. Não consegui confirmar

| O que falta | O que tentei | Onde provavelmente está |
|---|---|---|
| Investimento no Contorno ao centavo e por ano | DFP 2021 a 2025 (só total arredondado e investimento anual da concessão inteira); planilha da ANTT (só valores de 2007); notícias da ANTT e do BNDES (R$ 3,9 bi) | contabilidade regulatória da concessionária na ANTT; pedido pela LAI à ANTT |
| Por que o valor regulatório corrigido (R$ 1,76 bi) é menos da metade do declarado (R$ 3,9 bi) | DFP (citam juros capitalizados durante a obra, sem número) | notas da DFP por obra, se existirem; ANTT |
| Por que a planilha da ANTT dá R$ 165.235.775,96 executados de R$ 175.951.204,30 com 100% feito | planilha (sem nota) | ANTT, processo da 18ª revisão |
| Abertura parcial do tronco antes de 09/08/2024 | DFP 2021 a 2024; relatório mensal de jul/2024; TCU | relatórios mensais da ANTT de 2023 e 2024, um a um |
| Nomes e CNPJ das construtoras que fizeram a maior parte da obra | relatórios da ANTT, DFP, TCU | contratos privados da concessionária (não públicos); comunicados ao mercado na CVM |
| CNPJ da Azevedo & Travassos Infraestrutura Ltda. | CNPJ.ws não busca por nome; busca na web só achou a controladora | base completa do CNPJ (Receita), que não abre do exterior |
| Partido do Presidente da República em dez/2020 | TSE (candidaturas), Biblioteca da Presidência ("em manutenção"), listas de filiados do TSE (404) | TSE, relação de filiados; biografia oficial quando voltar |
| Texto do TAC de 2013 e do TAC Parcial de 2020 (MPF, concessionária, Biguaçu e Palhoça) | só citações no TCU | DOU de 28/12/2013; MPF em SC |
| Sentenças das ações civis públicas (5011157-44.2012, 5014533-38.2012, 5007718-88.2013, 5004170-55.2013) | só citações no TCU | consulta processual da JFSC e do TRF4 |
| Quem venceu a arbitragem sobre o Contorno e quanto custou | TCU (Acórdão de Relação 2062/2025 cita "sentença arbitral para cobrança do custo de arbitragem e honorários") | ANTT, página de arbitragens |
| Se as multas do TCU foram pagas | acórdãos | TCU, consulta processual (cobrança) |
| Porcentagem do sobrepreço | o acórdão escreve 22,99%; a conta dá 21,99% | íntegra da representação (peça 45 do TC 026.406/2020-9) |

## 13. Como reproduzir

```bash
W=$(mktemp -d); S=~/Documents/Brasil-Imposto/pipelines/works
python3 $S/build_florianopolis_bypass.py $W --fetch     # TCU, ANTT, DFP, SIOP, IBGE, CVM, CNPJ.ws, TSE, Commons (cerca de 5 MB depois de converter os PDFs em texto)
python3 $S/build_florianopolis_bypass.py $W             # 18 checagens; grava data/works/florianopolis-bypass.json
python3 $S/build_florianopolis_bypass.py $W --control   # planta R$ 500 no Quadro 1 do TA 002/2020: tem de falhar e não gravar
rm -rf $W
```

Checagens (todas no JSON, campo `checks`): as linhas e colunas do Quadro 1 do TA 002/2020 somam aos totais oficiais ao centavo (a tabela oficial arredonda o total do 14º ano em R$ 0,01 para cima, e a soma dos totais anuais dá R$ 491.251.185,70 contra R$ 491.251.185,69; tolerância de um centavo só nos totais anuais e na soma deles; todas as outras conferem exatas); custos administrativos = 6,24% da obra; R$ 854.113.307,34 × 1,0624 = R$ 907.409.977,72; R$ 923.846.486,36 menos R$ 16.309.444,17 = R$ 907.537.042,19; o corte registrado pelo TCU em 2024 é o mesmo de 2020; a proposta (TCU) e a planilha da ANTT diferem em R$ 0,01; zero ações no SIOP com controle positivo; JSON sem travessão. Toda citação do JSON é conferida no texto baixado. O controle deu "CHECAGEM FALHOU: TA 002/2020: obra, soma dos 4 anos = total do item: calculado 462398076.89 contra oficial 462397576.89", saída 1, e o JSON não mudou.
