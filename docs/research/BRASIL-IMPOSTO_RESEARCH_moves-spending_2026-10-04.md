# Maiores gastos do período: movimentos federais do lado do gasto, 2019 a 2026

Pesquisa para a coluna "Maiores gastos do período" da home (D88, D89). Coletado em 2026-10-04. Saída de dados:
`data/home/moves-spending.json` (mesmas chaves dos itens de `data/home/recent.json`, mais `year` e, quando cabe,
`moved_on`). Julho a outubro de 2026 já estão em `recent.json` e não foram refeitos. Documento escrito aos poucos, um
ano por vez, do mais novo para o mais antigo.

## Regra

- **Entra (1), ato:** lei, lei complementar ou medida provisória federal que fixa no próprio texto, ou na exposição de
  motivos oficial, um valor em reais de gasto, empréstimo com recursos da União, crédito extraordinário, renegociação de
  dívidas, garantia, ou renúncia e perda de receita (`revenue_waiver`). Data: a do Diário Oficial da União.
- **Entra (2), pagamento:** gasto fixado antes e pago num mês que o Resultado do Tesouro Nacional (RTN) daquele mês
  destaca como atípico ou extraordinário (precatórios concentrados, integralização de fundo, capitalização de estatal,
  fundo eleitoral, transferência única). Data: o mês do pagamento, em `moved_on`.
- **Sem dupla contagem:** quando um crédito extraordinário financia o programa criado por outro ato, entra só o de maior
  valor oficial (em empate, o ato que criou o programa) e o outro aparece na situação do item; lei de conversão que repete o valor de uma medida provisória fica com a medida provisória, no ano em que o valor
  foi fixado pela primeira vez; ato com teto e pagamento depois: fica o movimento único e identificável. O campo
  `status` diz o que ficou de fora.
- **Vários tetos no mesmo ato:** o valor do item é o teto principal; os demais aparecem no resumo (mesma prática de
  `recent.json`, por exemplo a LC 235).
- **Não entram:** a lei orçamentária anual e as leis de crédito suplementar ou especial (projetos PLN), que
  redistribuem o orçamento já aprovado; limites que só restringem uma despesa existente.
- **Ordem:** os 10 maiores de cada ano civil pelo valor oficial; mesmo critério para qualquer governo, sem filtro de
  partido ou de autor.
- **Natureza do valor:** `cap` (teto autorizado), `estimated_cost` (estimativa oficial) ou `paid` (pago, lido no RTN).

## Fontes e acesso (2026-10-04)

- Desta máquina, `in.gov.br`, `planalto.gov.br` e `camara.leg.br` não responderam (tempo esgotado em todas as
  tentativas, inclusive sem proxy). Por isso os textos foram lidos em duas cópias oficiais ou fiéis: o sistema de
  Legislação Federal do Senado Federal (`legis.senado.leg.br/norma/<id>`, "Ver texto no Sigen", com assinaturas e
  anexos) e, para exposições de motivos, cópias do Internet Archive das páginas do Planalto (link do snapshot citado).
- Lista de atos por ano: API de legislação do Senado (`dadosabertos/legislacao/lista?tipo=MPV|LEI|LCP&ano=`); situação
  de cada medida provisória: API de processos do Senado (`dadosabertos/processo`).
- Pagamentos: boletim mensal do RTN (PDF do Tesouro Transparente), lido com pdftotext e apagado em seguida.
- `act.url` aponta para a página da norma no Senado; `amount_source.url` aponta para a página exata lida.
- Exposições de motivos: as das medidas provisórias (`_ato.../exm/`) e as dos projetos de lei e de lei complementar do
  Executivo (`projetos/.../pl/exm/` e `.../plp/exm/`), todas lidas em cópias do Internet Archive do Planalto. Uma lei que
  nasceu de projeto do Executivo entra com a estimativa da exposição de motivos do projeto, e o item avisa que a estimativa
  é do texto enviado, não do aprovado.
- Vários anos numa estimativa: soma dos anos que a exposição de motivos traz (mesma prática de `recent.json`, MP 1.394).
- Cargos de quem assinou: só quando um documento oficial lido mostra o cargo (cabeçalho da exposição de motivos com a sigla
  do ministério e o nome do signatário, ou assinatura digital com o cargo) em data até seis meses do ato e sem troca no
  cargo registrada no intervalo; nos demais casos o cargo fica `null`. O Presidente da República é confirmado pelo próprio
  ato.


## 2026 (jan a jun)

| # | Movimento | Data | Valor oficial | Tipo | Natureza |
|---|---|---|---|---|---|
| 1 | Pagamento concentrado de sentenças judiciais e precatórios em março de 2026 | 2026-03 | R$ 71,375 bi | gasto | pago |
| 2 | Financiamento de carros novos para motoristas de aplicativo e taxistas (Medida Provisória nº 1.359) | 2026-05-19 | R$ 30 bi | gasto | teto |
| 3 | Crédito extraordinário para financiar caminhões e ônibus e reforçar fundos garantidores (Medida Provisória nº 1.354) | 2026-04-30 | R$ 17 bi | crédito extraordinário | teto |
| 4 | Plano Brasil Soberano: linhas de crédito a exportadores (Medida Provisória nº 1.345) | 2026-03-25 | R$ 15 bi | gasto | teto |
| 5 | Subvenção ao óleo diesel rodoviário de R$ 0,32 por litro (Medida Provisória nº 1.340) | 2026-03-12 | R$ 10 bi | gasto | teto |
| 6 | Crédito extraordinário para empréstimos a companhias aéreas (Medida Provisória nº 1.368) | 2026-06-19 | R$ 8 bi | crédito extraordinário | teto |
| 7 | Integralização de R$ 5,5 bilhões ao FIPEM em março de 2026 | 2026-03 | R$ 5,5 bi | gasto | pago |
| 8 | Novo Desenrola Brasil: garantia da União para renegociar dívidas de pessoas físicas (Medida Provisória nº 1.355) | 2026-05-04 | R$ 5 bi | renegociação de dívidas | teto |
| 9 | Reconhecimento de Saberes e Competências dos técnico-administrativos em educação (Lei nº 15.367) | 2026-03-31 | R$ 4,167 bi | gasto | estimativa |
| 10 | Regime Emergencial de Abastecimento de Combustíveis: subvenção ao diesel importado (Medida Provisória nº 1.349) | 2026-04-07 | R$ 4 bi | gasto | teto |

### 2026.1 Pagamento concentrado de sentenças judiciais e precatórios em março de 2026
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 32, N. 3 (março de 2026), 2026-04-30: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/3
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de março de 2026, Tabela 3.1 (R$ milhões, preços correntes, coluna março de 2026), soma das cinco linhas de sentenças judiciais e precatórios (benefícios previdenciários urbano e rural, pessoal, BPC e custeio e capital). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/54551_1765837/boletim_mar26.pdf
- Trecho: "Benefícios Previdenciários, Urbano: Sentenças Judiciais e Precatórios 20.481,0; Rural: Sentenças Judiciais e Precatórios 5.585,9; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 9.057,4; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 975,5; 4.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 35.275,0. Nota 13 do mês: crescimento explicado pelo cronograma de pagamentos de sentenças judiciais e precatórios, que em 2026 concentrou- se em março, enquanto em 2025 a torre de pagamentos ocorreu em julho."
- Situação: Pago em março de 2026. O valor inclui as requisições de pequeno valor pagas no mês. Em 2025 a concentração dos pagamentos ocorreu em julho.

### 2026.2 Financiamento de carros novos para motoristas de aplicativo e taxistas (Medida Provisória nº 1.359)
- Ato ou registro: Medida Provisória 1.359, 2026-05-19: https://legis.senado.leg.br/norma/43301927
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Rogério Ceron de Oliveira; Márcio Fernando Elias Rosa
- Valor: Medida Provisória nº 1.359/2026, art. 2º (Diário Oficial da União, edição extra de 19/05/2026; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/43301927/publicacao/43301142
- Trecho: "Art. 2º Observada a disponibilidade orçamentária e financeira, fica a União autorizada a destinar o valor de até R$ 30.000.000.000,00 (trinta bilhões de reais), para disponibilizar linhas de financiamento reembolsável a profissionais de transporte remunerado privado individual de passageiros, taxistas e cooperativas de taxistas"
- Situação: Revogada e incorporada pela Lei nº 15.503, de 14/09/2026, que manteve o teto de R$ 30 bilhões (item de recent.json). O crédito extraordinário que financiou o teto, Medida Provisória nº 1.362, de 25/05/2026 (R$ 30 bilhões), não entra de novo; perdeu a eficácia em 22/09/2026, segundo o Senado Federal.

### 2026.3 Crédito extraordinário para financiar caminhões e ônibus e reforçar fundos garantidores (Medida Provisória nº 1.354)
- Ato ou registro: Medida Provisória 1.354, 2026-04-30: https://legis.senado.leg.br/norma/43212250
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Bruno Moretti (Ministro de Estado do Planejamento e Orçamento)
- Valor: Medida Provisória nº 1.354/2026, art. 1º (Diário Oficial da União, edição extra de 30/04/2026; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/43212250/publicacao/43212656
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor de Encargos Financeiros da União e de Operações Oficiais de Crédito, no valor de R$ 17.000.000.000,00 (dezessete bilhões de reais), para atender às programações constantes do Anexo."
- Situação: Perdeu a eficácia em 27/08/2026, segundo o Senado Federal (a Medida Provisória nº 1.371, de 22/06/2026, alterou esta medida). Financia os tetos da Medida Provisória nº 1.353, de 30/04/2026 (até R$ 14,5 bilhões em linhas de financiamento e até R$ 2 bilhões a mais no FGI), que por isso não entra como item próprio; a Medida Provisória nº 1.353 também perdeu a eficácia em 27/08/2026. O Tesouro Nacional registrou o aporte de R$ 2 bilhões ao FGI em maio de 2026.

### 2026.4 Plano Brasil Soberano: linhas de crédito a exportadores (Medida Provisória nº 1.345)
- Ato ou registro: Medida Provisória 1.345, 2026-03-25: https://legis.senado.leg.br/norma/42930860
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Dario Carnevalli Durigan (Ministro de Estado da Fazenda); Geraldo José Rodrigues Alckmin Filho (Ministro de Estado do Desenvolvimento, Indústria, Comércio e Serviços)
- Valor: Medida Provisória nº 1.345/2026, art. 3º, § 1º, da Lei nº 12.712/2012 na redação dada pela medida (Diário Oficial da União de 25/03/2026; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/42930860/publicacao/42933964
- Trecho: "§ 1º As linhas de financiamento de que trata o caput serão concedidas com a utilização de até R$ 15.000.000.000,00 (quinze bilhões de reais)"
- Situação: Convertida na Lei nº 15.473, de 22/07/2026, que manteve o teto de R$ 15 bilhões (item de recent.json). O crédito extraordinário da Medida Provisória nº 1.352, de 28/04/2026 (R$ 5 bilhões ao Fundo de Garantia à Exportação para estas linhas), é parte deste teto e não entra de novo.

### 2026.5 Subvenção ao óleo diesel rodoviário de R$ 0,32 por litro (Medida Provisória nº 1.340)
- Ato ou registro: Medida Provisória 1.340, 2026-03-12: https://legis.senado.leg.br/norma/42896455
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda); Alexandre Silveira de Oliveira (Ministro de Estado de Minas e Energia)
- Valor: Medida Provisória nº 1.340/2026, art. 2º (Diário Oficial da União, edição extra de 12/03/2026; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/42896455/publicacao/42897024
- Trecho: "Art. 2º A subvenção econômica de que trata esta Medida Provisória ficará limitada ao valor total de R$ 10.000.000.000,00 (dez bilhões de reais)."
- Situação: Perdeu a eficácia em 09/07/2026, segundo o Senado Federal. O crédito extraordinário da Medida Provisória nº 1.344, de 19/03/2026 (R$ 10 bilhões para esta subvenção), não entra de novo. A Medida Provisória nº 1.349 acrescentou R$ 0,80 por litro até 31/05/2026 (item próprio pela subvenção à importação).

### 2026.6 Crédito extraordinário para empréstimos a companhias aéreas (Medida Provisória nº 1.368)
- Ato ou registro: Medida Provisória 1.368, 2026-06-19: https://legis.senado.leg.br/norma/43432257
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Bruno Moretti (Ministro de Estado do Planejamento e Orçamento)
- Valor: Medida Provisória nº 1.368/2026, art. 1º (Diário Oficial da União de 19/06/2026; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/43432257/publicacao/43429544
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério de Portos e Aeroportos, no valor de R$ 8.000.000.000,00 (oito bilhões de reais), para atender à programação constante do Anexo."
- Situação: Em tramitação no Congresso Nacional, vigência prorrogada (Ato do Presidente do Congresso Nacional nº 74/2026). Finalidade segundo a descrição da matéria no Senado Federal: empréstimo a companhias aéreas brasileiras para neutralizar o impacto no custo do querosene de aviação. O anexo do crédito não tem texto no sistema do Senado e não foi lido.

### 2026.7 Integralização de R$ 5,5 bilhões ao FIPEM em março de 2026
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 32, N. 3 (março de 2026), 2026-04-30: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/3
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de março de 2026, Nota 15 do mês (Discricionárias). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/54551_1765837/boletim_mar26.pdf
- Trecho: "explicado, principalmente, pelo crescimento nos pagamentos de ações nas funções Educação (+R$ 6,1 bilhões), que incluiu a integralização de R$ 5,5 bilhões ao Fundo de Incentivo à Permanência e Conclusão Escolar para Estudantes do Ensino Médio"
- Situação: Pago em março de 2026. Em fevereiro de 2026 a União já tinha integralizado R$ 3,5 bilhões ao mesmo fundo; até maio, as integralizações de 2026 somaram R$ 9,5 bilhões, segundo o Tesouro Nacional.

### 2026.8 Novo Desenrola Brasil: garantia da União para renegociar dívidas de pessoas físicas (Medida Provisória nº 1.355)
- Ato ou registro: Medida Provisória 1.355, 2026-05-04: https://legis.senado.leg.br/norma/43247820
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Dario Carnevalli Durigan (Ministro de Estado da Fazenda); Leonardo Osvaldo Barchini Rosa; Paulo Henrique Rodrigues Pereira; Esther Dweck; Bruno Moretti (Ministro de Estado do Planejamento e Orçamento); Wolney Queiroz Maciel; Luiz Marinho
- Valor: Medida Provisória nº 1.355/2026, art. 15 (Diário Oficial da União, edição extra de 04/05/2026; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/43247820/publicacao/43243323
- Trecho: "Art. 15. Fica a União autorizada a aumentar em até R$ 5.000.000.000,00 (cinco bilhões de reais) a sua participação no FGO, por meio da subscrição adicional de cotas para constituição de patrimônio segregado no Fundo, com direitos e obrigações próprios, exclusivamente para a cobertura das operações de crédito a que se refere o art. 6º para reestruturação de dívidas de pessoas físicas beneficiárias nos termos do disposto no art. 3º."
- Situação: Perdeu a eficácia em 31/08/2026 sem conversão em lei, segundo o Senado Federal.

### 2026.9 Reconhecimento de Saberes e Competências dos técnico-administrativos em educação (Lei nº 15.367)
- Ato ou registro: Lei 15.367, 2026-03-31: https://legis.senado.leg.br/norma/42966204
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Margareth Menezes da Purificação Costa; Camilo Sobreira de Santana; Esther Dweck (Ministra de Estado da Gestão e da Inovação em Serviços Públicos); Wolney Queiroz Maciel
- Valor: Exposição de Motivos nº 803/2025 MGI do projeto de lei, assinada por Esther Dweck em 02/12/2025 (Planalto, cópia do Internet Archive); valor de 2026. Fonte lida: https://web.archive.org/web/20260302005643/https://www.planalto.gov.br/CCIVIL_03/Projetos/Ato_2023_2026/2025/PL/Exm/Exm-803-25-MIGSP.doc
- Trecho: "(ii) para 2026, um impacto orçamentário de R$ 4.166.686.095,16; e (iii) para 2027 e 2028, um impacto orçamentário de R$ 5.609.026.382,69."
- Situação: Lei em vigor (Diário Oficial da União de 31/03/2026). O valor é o impacto estimado para 2026 no projeto enviado pelo Executivo; a mesma exposição de motivos indica R$ 5,61 bilhões "para 2027 e 2028", sem deixar claro se o valor é anual, por isso só 2026 entra. A estimativa sobre o texto aprovado não foi lida.

### 2026.10 Regime Emergencial de Abastecimento de Combustíveis: subvenção ao diesel importado (Medida Provisória nº 1.349)
- Ato ou registro: Medida Provisória 1.349, 2026-04-07: https://legis.senado.leg.br/norma/43024252
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Dario Carnevalli Durigan (Ministro de Estado da Fazenda); Alexandre Silveira de Oliveira (Ministro de Estado de Minas e Energia)
- Valor: Medida Provisória nº 1.349/2026, art. 5º (Diário Oficial da União, edição extra de 07/04/2026; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/43024252/publicacao/43027102
- Trecho: "Art. 5º A subvenção econômica à importação de óleo diesel de uso rodoviário de que trata o art. 4º ficará limitada ao valor total de R$ 4.000.000.000,00 (quatro bilhões de reais)."
- Situação: Perdeu a eficácia em 04/08/2026, segundo o Senado Federal. O crédito extraordinário da Medida Provisória nº 1.365, de 03/06/2026 (R$ 1 bilhão para o capital de giro das companhias aéreas previsto nesta medida), não entra de novo.

### Ficaram de fora em 2026 (janeiro a junho)
- **Medida Provisória nº 1.362 (25/05, R$ 30 bi, crédito extraordinário):** financia o teto da MP 1.359 (anexo:
  "Financiamento a Profissionais de Transporte Remunerado Privado Individual de Passageiros, Taxistas e Cooperativas de
  Taxistas"). Perdeu a eficácia em 22/09/2026 (Senado).
- **MP 1.353 (30/04, até R$ 14,5 bi em linhas e R$ 2 bi ao FGI):** financiada pela MP 1.354 (R$ 17 bi, listada por ter o
  maior valor; inclui R$ 500 mi ao FGCE). EXM nº 1022/2026, assinada por Bruno Moretti, "Ministro de Estado do Planejamento
  e Orçamento", cópia do Internet Archive:
  https://web.archive.org/web/20260507174220/https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/exm/exm-mp-1354-26.pdf.
- **MP 1.344 (19/03, R$ 10 bi):** anexo "Subvenção Econômica à Comercialização de Óleo Diesel de Uso Rodoviário no
  Território Nacional (Medida Provisória nº 1.340, de 2026)"; financia o teto da MP 1.340.
- **MP 1.352 (28/04, R$ 5 bi):** anexo do Fundo de Garantia à Exportação, "Financiamentos a Pessoas Físicas e Jurídicas
  de Direito Privado Exportadoras de Bens e Serviços [...] abrangidos pelo Plano Brasil Soberano"; parte do teto da MP 1.345.
- **MP 1.365 (03/06, R$ 1 bi):** anexo "Financiamento Destinado a Capital de Giro aos Prestadores de Serviços Aéreos
  Regulares"; financia o R$ 1 bi do art. 21 da MP 1.349.
- **Abaixo do 10º lugar (R$ 4 bi):** integralização de R$ 3,5 bi ao FIPEM em fevereiro de 2026 (RTN de fevereiro, Nota 14:
  "que incluiu a integralização de R$ 3,5 bilhões ao Fundo de Incentivo à Permanência e Conclusão Escolar para Estudantes do
  Ensino Médio"); MP 1.373 (29/06, Desenrola Adimplentes, até R$ 3 bi, e Fies Empreendedor, até
  R$ 1 bi); LC 228 (19/03, renúncia do REIQ limitada a R$ 2 bi mais R$ 1,1 bi em 2026); MP 1.342 (17/03, R$ 1,305 bi,
  enchentes em Minas Gerais e outros); MP 1.337 (06/03, até R$ 500 mi do Fundo Social para áreas em calamidade).
- **Lei 15.399 (04/05):** "No exercício de 2026, a despesa de que trata o § 1º deste artigo não excederá a R$
  7.909.535.000,00": limite que restringe uma despesa existente (seguro-desemprego do pescador artesanal), não entra.
- **MP 1.374 (assinada em 30/06/2026, DOU de 01/07/2026):** até R$ 10 bi do superávit do FNDCT para linha de
  financiamento rural via Finep (art. 15-A da Lei 11.540/2007). Pela data do DOU cai na janela de `recent.json`
  (julho), que não foi refeita; `recent.json` não a lista como item próprio (lista a MP 1.377, cujo crédito de
  R$ 13,285 bi inclui R$ 9 bi para essa linha). Fica para o agente principal decidir.
- Medidas sem valor total no texto: MP 1.358 (subvenção a combustíveis derivados de petróleo), MP 1.363 (R$ 1,12 por
  litro de diesel, sem teto), MP 1.338 (R$ 7.300 por família na Zona da Mata mineira, sem total).

### Conflito com `recent.json` (para o agente principal)
- `recent.json` lista a **Lei 15.503** (14/09/2026, R$ 30 bi) e a **Lei 15.473** (22/07/2026, R$ 15 bi), leis de
  conversão que repetem os tetos das **MPs 1.359 e 1.345**, listadas aqui. Na visão anual de 2026, somar as duas
  colunas conta o mesmo teto duas vezes. Pela regra deste arquivo fica a medida provisória (primeiro ato que fixou o
  valor); a escolha final entre as duas é do agente principal.
- Da mesma forma, a MP 1.377 de `recent.json` (R$ 13,285 bi) inclui R$ 3 bi para o Desenrola Adimplentes e R$ 1 bi
  para o Fies Empreendedor, tetos criados pela MP 1.373 (junho, abaixo do corte aqui).

### Não confirmado (2026)
- Finalidade da MP 1.368 tirada da descrição da matéria no Senado ("Empréstimo a companhias aéreas brasileiras para
  neutralizar o impacto no custo do querosene de aviação (QAV)"); o anexo não tem texto no sistema do Senado e o DOU não
  abriu.
- Cargos não confirmados em documento lido (ficam `null`): Rogério Ceron de Oliveira e Márcio Fernando Elias Rosa (MPs
  1.353 e 1.359; houve troca no Ministério do Desenvolvimento, Indústria, Comércio e Serviços entre março e abril de 2026),
  e os signatários da MP 1.355 e da Lei 15.367 sem exposição de motivos própria. Confirmados: Fernando Haddad, Fazenda (EM
  nº 427/2026 MF, 06/03/2026); Dario Carnevalli Durigan, Fazenda (EXM nº 581/2026 MF MDIC, 24/03/2026, e assinatura
  digital da EXM da MP 1.349, 07/04/2026); Alexandre Silveira de Oliveira, Minas e Energia (assinatura digital da EXM da MP
  1.349, 06/04/2026); Geraldo Alckmin, Desenvolvimento, Indústria, Comércio e Serviços (EXM nº 581/2026 MF MDIC); Bruno
  Moretti, Planejamento e Orçamento (EXM nº 1022/2026); Esther Dweck, Gestão e Inovação (EXM nº 803/2025, 02/12/2025).


## 2025 (ano completo)

| # | Movimento | Data | Valor oficial | Tipo | Natureza |
|---|---|---|---|---|---|
| 1 | Isenção do Imposto de Renda para quem ganha até R$ 5 mil por mês (Lei nº 15.270) | 2025-11-27 | R$ 83,24 bi | renúncia de receita | estimativa |
| 2 | Pagamento concentrado de sentenças judiciais e precatórios em julho de 2025 | 2025-07 | R$ 63,692 bi | gasto | pago |
| 3 | Plano Brasil Soberano: até R$ 30 bilhões em financiamento a exportadores (Medida Provisória nº 1.309) | 2025-08-13 | R$ 30 bi | gasto | teto |
| 4 | Regulamentação da reforma tributária: parcela do IBS descontada da CBS em 2026 a 2028 (Lei Complementar nº 214) | 2025-01-16 | R$ 17,9 bi | renúncia de receita | estimativa |
| 5 | Programa Especial de Sustentabilidade da Indústria Química (PRESIQ): créditos financeiros de 2027 a 2031 (Lei nº 15.294) | 2025-12-22 | R$ 12,5 bi | renúncia de receita | teto |
| 6 | Linha de crédito para quitar dívidas de produtores rurais (Medida Provisória nº 1.314) | 2025-09-05 | R$ 12 bi | renegociação de dívidas | teto |
| 7 | Reajuste dos soldos dos militares das Forças Armadas (Medida Provisória nº 1.293) | 2025-03-28 | R$ 8,3 bi | gasto | estimativa |
| 8 | Regime Especial de Tributação para Serviços de Datacenter (REDATA) (Medida Provisória nº 1.318) | 2025-09-18 | R$ 7,25 bi | renúncia de receita | estimativa |
| 9 | Financiamento para renovar a frota de caminhões (Medida Provisória nº 1.328) | 2025-12-16 | R$ 6 bi | gasto | teto |
| 10 | Crédito extraordinário para subvenções do Plano Safra (Medida Provisória nº 1.289) | 2025-02-24 | R$ 4,178 bi | crédito extraordinário | teto |

### 2025.1 Isenção do Imposto de Renda para quem ganha até R$ 5 mil por mês (Lei nº 15.270)
- Ato ou registro: Lei 15.270, 2025-11-27: https://legis.senado.leg.br/norma/41758136
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda); Manoel Carlos de Almeida Neto; Simone Nassar Tebet (Ministra de Estado do Planejamento e Orçamento)
- Valor: Exposição de Motivos nº 19/2025 MF do Projeto de Lei nº 1.087/2025, item 24, assinada por Fernando Haddad (Planalto, cópia do Internet Archive); soma de 2026 a 2028. Fonte lida: https://web.archive.org/web/20260118063755/https://www.planalto.gov.br/ccivil_03/Projetos/Ato_2023_2026/2025/PL/Exm/Exm-0019-25-MF.doc
- Trecho: "Estudo elaborado pela Secretaria Especial da Receita Federal do Brasil estima uma renúncia de receitas, em 2026, de R$ 25,84 bilhões (vinte e cinco bilhões e oitocentos e quarenta milhões de reais), em 2027, de R$ 27,72 bilhões (vinte e sete bilhões e setecentos e vinte milhões de reais), e em 2028, de R$ 29,68 (vinte e nove bilhões e seiscentos e oitenta milhões de reais)."
- Situação: Lei em vigor (Diário Oficial da União de 27/11/2025), efeitos a partir de 2026. A estimativa é do projeto enviado pelo Executivo; o Congresso ampliou a faixa de redução parcial de R$ 7.000 para R$ 7.350, e a estimativa da lei aprovada não foi lida. A mesma exposição de motivos estima a arrecadação das medidas de compensação (imposto mínimo sobre altas rendas e dividendos remetidos ao exterior) em R$ 34,12 bilhões em 2026, R$ 39,18 bilhões em 2027 e R$ 39,64 bilhões em 2028.

### 2025.2 Pagamento concentrado de sentenças judiciais e precatórios em julho de 2025
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 31, N. 7 (julho de 2025), 2025-08-28: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2025/7
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de julho de 2025, Tabela 3.1 (R$ milhões, preços correntes, coluna julho de 2025), soma das cinco linhas de sentenças judiciais e precatórios (benefícios previdenciários urbano e rural, pessoal, BPC e custeio e capital). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/52799_1666088/boletim_jul25.pdf
- Trecho: "Benefícios Previdenciários, Urbano: Sentenças Judiciais e Precatórios 16.479,6; Rural: Sentenças Judiciais e Precatórios 4.471,7; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 5.900,1; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 913,1; 4.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 35.927,4. Nota 12 do mês: elevação explicada, em grande parte, pelo cronograma de pagamentos de precatórios, que em 2025 foi concentrado em julho, enquanto em 2024 concentrou-se em fevereiro."
- Situação: Pago em julho de 2025. O valor inclui as requisições de pequeno valor pagas no mês. Em outubro de 2025 o Tesouro registrou mais R$ 1,4 bilhão de precatórios excedentes ao sublimite da EC nº 114/2021 que não tinham sido pagos com o lote de julho.

### 2025.3 Plano Brasil Soberano: até R$ 30 bilhões em financiamento a exportadores (Medida Provisória nº 1.309)
- Ato ou registro: Medida Provisória 1.309, 2025-08-13: https://legis.senado.leg.br/norma/41236701
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda); Geraldo José Rodrigues Alckmin Filho (Ministro de Estado do Desenvolvimento, Indústria, Comércio e Serviços)
- Valor: Medida Provisória nº 1.309/2025, art. 5º-A da Lei nº 9.818/1999 na redação dada pela medida (Diário Oficial da União, edição extra de 13/08/2025; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/41236701/publicacao/41247297
- Trecho: "Art. 5º-A. Fica autorizada a utilização do superávit financeiro do FGE, apurado em 31 de dezembro de 2024, inclusive do principal, limitada ao montante de R$ 30.000.000.000,00 (trinta bilhões de reais), como fonte de recursos para a disponibilização de linhas de financiamento a pessoas físicas e jurídicas de direito privado exportadoras de bens e serviços, bem como seus fornecedores"
- Situação: Perdeu a eficácia em 10/12/2025 sem conversão em lei, segundo o Senado Federal. O crédito extraordinário da Medida Provisória nº 1.310, de 01/09/2025 (R$ 30 bilhões ao Fundo de Garantia à Exportação para estas linhas), não entra de novo.

### 2025.4 Regulamentação da reforma tributária: parcela do IBS descontada da CBS em 2026 a 2028 (Lei Complementar nº 214)
- Ato ou registro: Lei Complementar 214, 2025-01-16: https://legis.senado.leg.br/norma/40180341
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Luiz Paulo Teixeira Ferreira; Fernando Haddad (Ministro de Estado da Fazenda); Márcio Luiz França Gomes; Esther Dweck; Geraldo José Rodrigues Alckmin Filho (Ministro de Estado do Desenvolvimento, Indústria, Comércio e Serviços); Maria Osmarina Marina da Silva Vaz de Lima; Silvio Serafim Costa Filho; Nísia Verônica Trindade Lima
- Valor: Exposição de Motivos nº 38/2024 MF do Projeto de Lei Complementar nº 68/2024, item 289, assinada por Fernando Haddad (Planalto, cópia do Internet Archive); soma de 2026 a 2028. Fonte lida: https://web.archive.org/web/20261003225658/https://www.planalto.gov.br/ccivil_03/projetos/ato_2023_2026/2024/plp/exm/exm-038-24-mf.doc
- Trecho: "O impacto do projeto no tocante à alíquota de 0,1% do IBS que será descontada da CBS, nos termos dos arts. 125 e 127 do ADCT, foi estimado em até R$ 5,63 bilhões para o ano de 2026, em R$ 5,96 bilhões para o ano de 2027 e em R$ 6,31 bilhões para o ano de 2028 em redução de receitas da União"
- Situação: Lei complementar em vigor desde 16/01/2025 (Diário Oficial da União, edição extra). A estimativa é do projeto enviado pelo Executivo; a estimativa sobre o texto aprovado não foi lida. A dedução decorre da transição prevista nos arts. 125 e 127 do Ato das Disposições Constitucionais Transitórias (Emenda Constitucional nº 132/2023).

### 2025.5 Programa Especial de Sustentabilidade da Indústria Química (PRESIQ): créditos financeiros de 2027 a 2031 (Lei nº 15.294)
- Ato ou registro: Lei 15.294, 2025-12-22: https://legis.senado.leg.br/norma/41853726
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda); Geraldo José Rodrigues Alckmin Filho (Ministro de Estado do Desenvolvimento, Indústria, Comércio e Serviços); Simone Nassar Tebet (Ministra de Estado do Planejamento e Orçamento); Jorge Rodrigo Araújo Messias
- Valor: Lei nº 15.294/2025, art. 3º, § 3º (Diário Oficial da União de 22/12/2025; texto oficial no Senado Federal); soma dos limites anuais de 2027 a 2031. Fonte lida: https://legis.senado.leg.br/norma/41853726/publicacao/41859066
- Trecho: "Os créditos financeiros de que trata este artigo serão limitados aos seguintes valores globais para cada ano-calendário: [...] 2027 - R$ 2.500.000.000,00 (dois bilhões e quinhentos milhões de reais); [...] 2031 - R$ 2.500.000.000,00 (dois bilhões e quinhentos milhões de reais)."
- Situação: Lei em vigor desde 22/12/2025. A mesma lei prevê outro grupo de créditos financeiros limitado a R$ 500 milhões por ano de 2027 a 2031.

### 2025.6 Linha de crédito para quitar dívidas de produtores rurais (Medida Provisória nº 1.314)
- Ato ou registro: Medida Provisória 1.314, 2025-09-05: https://legis.senado.leg.br/norma/41397586
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda)
- Valor: Medida Provisória nº 1.314/2025, art. 2º (Diário Oficial da União, edição extra de 05/09/2025; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/41397586/publicacao/41397703
- Trecho: "Art. 2º Fica autorizada a utilização do superávit financeiro apurado em 31 de dezembro de 2024 de fontes supervisionadas por unidades do Ministério da Fazenda, limitada ao montante de até R$ 12.000.000.000,00 (doze bilhões de reais), como fonte de recursos para a disponibilização de linha de crédito rural criada com o objetivo de permitir a liquidação ou a amortização das seguintes operações"
- Situação: Perdeu a eficácia em 12/02/2026, segundo o Senado Federal. O crédito extraordinário da Medida Provisória nº 1.316, de 16/09/2025 (R$ 12 bilhões, anexo "Financiamento Destinado à Liquidação ou à Amortização de Dívidas de Produtores Rurais Prejudicados por Eventos Adversos"), financia este teto e não entra de novo.

### 2025.7 Reajuste dos soldos dos militares das Forças Armadas (Medida Provisória nº 1.293)
- Ato ou registro: Medida Provisória 1.293, 2025-03-28: https://legis.senado.leg.br/norma/40493293
- Assinaram: Geraldo José Rodrigues Alckmin Filho (Vice-Presidente da República, no exercício do cargo de Presidente da República); José Múcio Monteiro Filho (Ministro de Estado da Defesa); Simone Nassar Tebet (Ministra de Estado do Planejamento e Orçamento)
- Valor: Exposição de Motivos Interministerial nº 25/2025 MD MPO da Medida Provisória nº 1.293/2025, item 6 (Planalto, cópia do Internet Archive); soma do primeiro e do segundo ano. Fonte lida: https://web.archive.org/web/20260710074536/https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/exm/exm-1293-25.pdf
- Trecho: "O impacto orçamentário estimado é de R$ 3 bilhões no primeiro ano e R$ 5,3 bilhões no segundo."
- Situação: Convertida na Lei nº 15.167, de 17/07/2025, segundo o Senado Federal.

### 2025.8 Regime Especial de Tributação para Serviços de Datacenter (REDATA) (Medida Provisória nº 1.318)
- Ato ou registro: Medida Provisória 1.318, 2025-09-18: https://legis.senado.leg.br/norma/41468171
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda); Geraldo José Rodrigues Alckmin Filho (Ministro de Estado do Desenvolvimento, Indústria, Comércio e Serviços); Alexandre Silveira de Oliveira (Ministro de Estado de Minas e Energia)
- Valor: Exposição de Motivos Interministerial nº 10/2025 MDIC MF MME da Medida Provisória nº 1.318/2025 (Planalto, cópia do Internet Archive); soma de 2026 a 2028. Fonte lida: https://web.archive.org/web/20260924164807/https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/exm/exm-1318-25.pdf
- Trecho: "a Secretaria Especial da Receita Federal do Brasil estimou impacto orçamentário-financeiro negativo, decorrente da medida ora analisada, nos montantes aproximados de R$ 5,20 bilhões para o ano de 2026, de R$ 1,00 bilhão para o ano de 2027 e de R$ 1,05 bilhão para o ano de 2028."
- Situação: Perdeu a eficácia em 25/02/2026, segundo o Senado Federal.

### 2025.9 Financiamento para renovar a frota de caminhões (Medida Provisória nº 1.328)
- Ato ou registro: Medida Provisória 1.328, 2025-12-16: https://legis.senado.leg.br/norma/41836886
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda); Geraldo José Rodrigues Alckmin Filho (Ministro de Estado do Desenvolvimento, Indústria, Comércio e Serviços)
- Valor: Medida Provisória nº 1.328/2025, art. 2º (Diário Oficial da União, edição extra de 16/12/2025; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/41836886/publicacao/41836963
- Trecho: "Art. 2º Fica autorizada a destinação de até R$ 6.000.000.000,00 (seis bilhões de reais), obedecida a disponibilidade orçamentária, para disponibilizar linhas de financiamento reembolsável a pessoas físicas e jurídicas de direito privado para aquisição de caminhões novos ou seminovos para renovação de frota."
- Situação: Perdeu a eficácia em 27/05/2026, segundo o Senado Federal.

### 2025.10 Crédito extraordinário para subvenções do Plano Safra (Medida Provisória nº 1.289)
- Ato ou registro: Medida Provisória 1.289, 2025-02-24: https://legis.senado.leg.br/norma/40391956
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Simone Nassar Tebet (Ministra de Estado do Planejamento e Orçamento)
- Valor: Medida Provisória nº 1.289/2025, art. 1º (Diário Oficial da União, edição extra de 24/02/2025; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/40391956/publicacao/40392123
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor de Operações Oficiais de Crédito, no valor de R$ 4.177.883.185,00 (quatro bilhões cento e setenta e sete milhões oitocentos e oitenta e três mil cento e oitenta e cinco reais)"
- Situação: Perdeu a eficácia em 23/06/2025, segundo o Senado Federal.

### Ficaram de fora em 2025
- **Créditos que só financiam um teto listado:** MP 1.310 (01/09, R$ 30 bi ao FGE, Plano Brasil Soberano, parte da MP
  1.309); MP 1.316 (16/09, R$ 12 bi, parte da MP 1.314).
- **MP 1.294 (11/04, tabela do IRPF):** a EXM nº 25/2025 MF estima "redução de receitas da ordem de: R$ 3,29 bilhões [...]
  em 2025; R$ 5,34 bilhões [...] em 2026; e R$ 5,73 bilhões [...] em 2027" e diz que 2026 e 2027 "já está considerada, de
  forma consolidada, na estimativa que acompanhou o Projeto de Lei nº 1.087 de 2025, não sendo, por conseguinte, um impacto
  adicional". Sem dupla contagem, o valor próprio é R$ 3,29 bi (2025), abaixo do 10º lugar. Revogada em 11/08/2025 (Senado).
- **Abaixo do 10º lugar (R$ 4,18 bi):** MP 1.306 (17/07, R$ 3,313 bi, ressarcimento de descontos indevidos do INSS); MP
  1.326 (01/12, reajuste das forças de segurança do DF, valores da EXM abaixo do corte); Lei 15.105 e Lei 15.106 (conversões de créditos
  de 2024); MP 1.299 (R$ 520 mi).
- **Lei Complementar 221 (18/11):** autoriza descontar até R$ 5 bi por ano de despesas com projetos estratégicos de defesa
  da meta fiscal e do limite de despesas. É exceção à regra fiscal, não autorização de gasto novo; não entra.
- **Lei 15.269 (24/11, setor elétrico):** muda para 2030 a 2034 os limites anuais dos créditos fiscais da Lei 14.990/2024
  (R$ 1,7 bi a R$ 5 bi por ano); o valor foi fixado em 2024 e não é novo.
- **Lei 15.132 (30/04):** repete os R$ 15 bi da Política Nacional Aldir Blanc fixados em 2022 (Lei 14.399/2022).
- **MPs 1.290 e 1.331 (saques do FGTS, cerca de R$ 12 bi e R$ 7,8 bi segundo as EXMs):** dinheiro dos trabalhadores, não
  da União. **MP 1.323 e Lei 15.399/2026:** limites ao seguro-defeso (R$ 7,325 bi em 2025), restrição de despesa existente.
- **MP 1.304 (setor elétrico):** a EXM cita custos de até R$ 35 bi por ano de vetos derrubados, pagos pelos consumidores de
  energia, não pela União.
- **Projeto de lei das carreiras do Executivo (EXM nº 17/2025 MGI MPO):** "possui exatamente o mesmo teor da Medida
  Provisória nº 1.286" (31/12/2024); o valor pertence a 2024.
- **Lei Complementar 212 (Propag, renegociação das dívidas dos estados):** sem valor em reais no texto; projeto do Senado,
  sem exposição de motivos do Executivo. Fica fora por falta de valor oficial.
- **Pagamentos no RTN de 2025:** compensações a estados pela LC 194/2022 por abatimento de dívidas (entre R$ 0,8 bi e
  R$ 1,0 bi por mês de janeiro a maio) e R$ 1,4 bi de precatórios em outubro, abaixo do corte.

### Não confirmado (2025)
- Estimativas da Lei 15.270 e da LC 214 são das exposições de motivos dos projetos enviados pelo Executivo; as estimativas
  sobre os textos aprovados (que mudaram) não foram lidas.
- Cargos de Manoel Carlos de Almeida Neto, Jorge Rodrigo Araújo Messias e dos demais signatários da LC 214 (exceto Fernando
  Haddad, Esther Dweck e Geraldo Alckmin) não confirmados; ficam `null`.


## 2024 (ano completo)

| # | Movimento | Data | Valor oficial | Tipo | Natureza |
|---|---|---|---|---|---|
| 1 | Reajustes e reestruturação das carreiras do Poder Executivo federal (Medida Provisória nº 1.286) | 2024-12-31 | R$ 73,912 bi | gasto | estimativa |
| 2 | Pagamento concentrado de sentenças judiciais e precatórios em fevereiro de 2024 | 2024-02 | R$ 32,077 bi | gasto | pago |
| 3 | Financiamentos com o superávit do Fundo Social para o Rio Grande do Sul e o clima: até R$ 20 bilhões (Lei nº 14.981) | 2024-09-23 | R$ 20 bi | gasto | teto |
| 4 | Programa de Desenvolvimento do Hidrogênio de Baixa Emissão de Carbono (PHBC): créditos fiscais de 2028 a 2032 (Lei nº 14.990) | 2024-09-30 | R$ 18,3 bi | renúncia de receita | teto |
| 5 | Programa Emergencial de Retomada do Setor de Eventos (Perse): limite de R$ 15 bilhões de 2024 a 2026 (Lei nº 14.859) | 2024-05-23 | R$ 15 bi | renúncia de receita | teto |
| 6 | Crédito extraordinário para a calamidade no Rio Grande do Sul (Medida Provisória nº 1.218) | 2024-05-11 | R$ 12,179 bi | crédito extraordinário | teto |
| 7 | Isenção do Imposto de Renda até dois salários mínimos (Medida Provisória nº 1.206) | 2024-02-06 | R$ 10,33 bi | renúncia de receita | estimativa |
| 8 | Crédito extraordinário para compra e estoques públicos de arroz (Medida Provisória nº 1.225) | 2024-05-24 | R$ 6,699 bi | crédito extraordinário | teto |
| 9 | Fundo para recuperar infraestruturas atingidas por eventos climáticos: aporte de até R$ 6,5 bilhões para o Rio Grande do Sul (Medida Provisória nº 1.278) | 2024-12-12 | R$ 6,5 bi | gasto | teto |
| 10 | Até R$ 6 bilhões do FGEDUC para o fundo da poupança do ensino médio (Medida Provisória nº 1.213) | 2024-04-23 | R$ 6 bi | gasto | teto |

### 2024.1 Reajustes e reestruturação das carreiras do Poder Executivo federal (Medida Provisória nº 1.286)
- Ato ou registro: Medida Provisória 1.286, 2024-12-31: https://legis.senado.leg.br/norma/40036017
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Cristina Kiomi Mori; Gustavo José de Guimarães e Souza
- Valor: Exposição de Motivos Interministerial nº 140/2024 MGI MPO da Medida Provisória nº 1.286/2024, item 15, assinada por Esther Dweck e Simone Tebet (Planalto, cópia do Internet Archive); soma de 2025 a 2027. Fonte lida: https://web.archive.org/web/20260710085015/https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/exm/exm-1286-24.pdf
- Trecho: "Tudo somado, o impacto orçamentário acumulado da proposta nos exercícios de 2025, 2026 e 2027 será, respectivamente, de R$ 17.987.199.520,68, de R$ 26.756.859.315,88, e de R$ 29.167.578.816,57."
- Situação: Perdeu a eficácia em 02/06/2025, segundo o Senado Federal. O Executivo reenviou o mesmo conteúdo como projeto de lei (Exposição de Motivos nº 17/2025 MGI MPO: "possui exatamente o mesmo teor da Medida Provisória nº 1.286"); a lei resultante não entra de novo.

### 2024.2 Pagamento concentrado de sentenças judiciais e precatórios em fevereiro de 2024
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 30, N. 2 (fevereiro de 2024), 2024-03-26: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2024/2
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de fevereiro de 2024, Tabela 3.1 (R$ milhões, preços correntes, coluna fevereiro de 2024), soma das cinco linhas de sentenças judiciais e precatórios (benefícios previdenciários urbano e rural, pessoal, BPC e custeio e capital). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/49174_1539700/boletim_fev24.pdf
- Trecho: "Benefícios Previdenciários, Urbano: Sentenças Judiciais e Precatórios 1.305,6; Rural: Sentenças Judiciais e Precatórios 351,8; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 667,7; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 205,2; 4.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 29.546,7. Nota 11 do mês: explicado pela diferença no cronograma de pagamentos dos precatórios em 2023 e 2024. Enquanto em 2023 a concentração de pagamento dos precatórios nesta rubrica ocorreu em maio (R$ 16,5 bilhões, a preços de fevereiro de 2024), em 2024 estes pagamentos foram concentrados em fevereiro (R$ 29,6 bilhões)."
- Situação: Pago em fevereiro de 2024. O valor inclui as requisições de pequeno valor pagas no mês. Os precatórios de pessoal e de benefícios previdenciários devidos em 2024 foram antecipados para dezembro de 2023, após decisão do STF nas ADIs 7.047 e 7.064, por isso esta concentração é menor que a de outros anos.

### 2024.3 Financiamentos com o superávit do Fundo Social para o Rio Grande do Sul e o clima: até R$ 20 bilhões (Lei nº 14.981)
- Ato ou registro: Lei 14.981, 2024-09-23: https://legis.senado.leg.br/norma/39686235
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Carlos Henrique Baqueta Fávaro; Luiz Paulo Teixeira Ferreira; Antônio Waldez Góes da Silva; Cristina Kiomi Mori; Maria Osmarina Marina da Silva Vaz de Lima
- Valor: Lei nº 14.981/2024, art. 47-A da Lei nº 12.351/2010 na redação dada pela lei (Diário Oficial da União de 23/09/2024; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/39686235/publicacao/39689663
- Trecho: "Art. 47-A. É autorizada a utilização do superávit financeiro do FS apurado em 31 de dezembro de 2023, inclusive do principal, limitada ao montante de R$ 20.000.000.000,00 (vinte bilhões de reais), incluídos os montantes do superávit financeiro já transferidos até a data de publicação da lei que introduziu este artigo, em decorrência da aplicação do disposto na Medida Provisória nº 1.226, de 29 de maio de 2024"
- Situação: Lei em vigor. O limite começou em R$ 15 bilhões na Medida Provisória nº 1.226, de 29/05/2024 (revogada em 23/09/2024, segundo o Senado Federal). Os créditos extraordinários que financiaram a linha não entram de novo: Medida Provisória nº 1.233, de 18/06/2024 (R$ 17,6 bilhões, dos quais R$ 15 bilhões para esta linha e R$ 2 bilhões para o Fundo de Arrendamento Residencial), e Medida Provisória nº 1.269, de 22/10/2024 (R$ 5 bilhões, saldo do limite). A mesma lei autoriza subvenção de até R$ 3 bilhões e aporte de até R$ 4,5 bilhões no FGO, descontados os valores já concedidos pela Medida Provisória nº 1.216.

### 2024.4 Programa de Desenvolvimento do Hidrogênio de Baixa Emissão de Carbono (PHBC): créditos fiscais de 2028 a 2032 (Lei nº 14.990)
- Ato ou registro: Lei 14.990, 2024-09-30: https://legis.senado.leg.br/norma/39716074
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Geraldo José Rodrigues Alckmin Filho
- Valor: Lei nº 14.990/2024, art. 4º, § 1º (Diário Oficial da União de 30/09/2024; texto oficial no Senado Federal); soma dos limites anuais de 2028 a 2032. Fonte lida: https://legis.senado.leg.br/norma/39716074/publicacao/39717103
- Trecho: "Entre 2028 e 2032, os créditos fiscais mencionados neste artigo serão limitados aos seguintes valores globais para cada ano-calendário: [...] 2028: R$ 1.700.000.000,00 (um bilhão e setecentos milhões de reais); [...] 2029: R$ 2.900.000.000,00 (dois bilhões e novecentos milhões de reais); [...] 2030: R$ 4.200.000.000,00 (quatro bilhões e duzentos milhões de reais); [...] 2031: R$ 4.500.000.000,00 (quatro bilhões e quinhentos milhões de reais); [...] 2032: R$ 5.000.000.000,00 (cinco bilhões de reais)."
- Situação: Lei em vigor. A Lei nº 15.269/2025 deslocou os mesmos limites anuais para 2030 a 2034; o total continua R$ 18,3 bilhões e não entra de novo.

### 2024.5 Programa Emergencial de Retomada do Setor de Eventos (Perse): limite de R$ 15 bilhões de 2024 a 2026 (Lei nº 14.859)
- Ato ou registro: Lei 14.859, 2024-05-23: https://legis.senado.leg.br/norma/38539018
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda)
- Valor: Lei nº 14.859/2024, art. 4º-A da Lei nº 14.148/2021 na redação dada pela lei (Diário Oficial da União de 23/05/2024; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/38539018/publicacao/38539287
- Trecho: "Art. 4º-A. O benefício fiscal estabelecido no art. 4º terá o seu custo fiscal de gasto tributário fixado, nos meses de abril de 2024 a dezembro de 2026, no valor máximo de R$ 15.000.000.000,00 (quinze bilhões de reais)"
- Situação: Lei em vigor. O texto prevê relatórios bimestrais da Receita Federal sobre o custo do benefício.

### 2024.6 Crédito extraordinário para a calamidade no Rio Grande do Sul (Medida Provisória nº 1.218)
- Ato ou registro: Medida Provisória 1.218, 2024-05-11: https://legis.senado.leg.br/norma/38486396
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Simone Nassar Tebet (Ministra de Estado do Planejamento e Orçamento)
- Valor: Medida Provisória nº 1.218/2024, art. 1º (Diário Oficial da União, edição extra de 11/05/2024; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/38486396/publicacao/38486487
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor de diversos órgãos do Poder Executivo, de Encargos Financeiros da União, e de Operações Oficiais de Crédito, no valor de R$ 12.179.438.240,00 (doze bilhões cento e setenta e nove milhões quatrocentos e trinta e oito mil duzentos e quarenta reais)"
- Situação: Convertida na Lei nº 14.962, de 05/09/2024, que repete o valor e não entra de novo. Pelo anexo, R$ 4,95 bilhões integralizam cotas do FGI e do FGO no Rio Grande do Sul e R$ 2 bilhões pagam subvenções a operações de crédito (rurais, Pronaf e Pronampe da Medida Provisória nº 1.216, de 09/05/2024). A Medida Provisória nº 1.216 (aporte de até R$ 4,5 bilhões no FGO e subvenção de até R$ 2 bilhões) é financiada por este crédito e não entra como item próprio.

### 2024.7 Isenção do Imposto de Renda até dois salários mínimos (Medida Provisória nº 1.206)
- Ato ou registro: Medida Provisória 1.206, 2024-02-06: https://legis.senado.leg.br/norma/38192230
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda)
- Valor: Exposição de Motivos nº 4/2024 MF da Medida Provisória nº 1.206/2024, item 7 (Planalto, cópia do Internet Archive); soma de 2024 a 2026. Fonte lida: https://web.archive.org/web/20260516093153/https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/exm/exm-1206-24.pdf
- Trecho: "estima-se uma redução de receitas em 2024 da ordem de R$ 3,03 bilhões (três bilhões e trinta milhões de reais), em 2025 de R$ 3,53 bilhões (três bilhões e quinhentos e trinta milhões de reais) e em 2026 de R$ 3,77 bilhões (três bilhões e setecentos e setenta milhões de reais)"
- Situação: Revogada em 01/05/2024, segundo o Senado Federal.

### 2024.8 Crédito extraordinário para compra e estoques públicos de arroz (Medida Provisória nº 1.225)
- Ato ou registro: Medida Provisória 1.225, 2024-05-24: https://legis.senado.leg.br/norma/38544035
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Simone Nassar Tebet (Ministra de Estado do Planejamento e Orçamento)
- Valor: Medida Provisória nº 1.225/2024, art. 1º (Diário Oficial da União, edição extra de 24/05/2024; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/38544035/publicacao/38544671
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor dos Ministérios da Agricultura e Pecuária e do Desenvolvimento Agrário e Agricultura Familiar, no valor de R$ 6.698.923.000,00 (seis bilhões seiscentos e noventa e oito milhões novecentos e vinte e três mil reais)"
- Situação: Perdeu a eficácia em 20/09/2024, segundo o Senado Federal.

### 2024.9 Fundo para recuperar infraestruturas atingidas por eventos climáticos: aporte de até R$ 6,5 bilhões para o Rio Grande do Sul (Medida Provisória nº 1.278)
- Ato ou registro: Medida Provisória 1.278, 2024-12-12: https://legis.senado.leg.br/norma/39923537
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda); Rui Costa dos Santos (Ministro de Estado Chefe da Casa Civil da Presidência da República)
- Valor: Medida Provisória nº 1.278/2024, art. 8º (Diário Oficial da União de 12/12/2024; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/39923537/publicacao/39923963
- Trecho: "fica a União autorizada a integralizar o valor de até R$ 6.500.000.000,00 (seis bilhões e quinhentos milhões de reais) no fundo de que trata o art. 1º."
- Situação: Perdeu a eficácia em 21/05/2025, segundo o Senado Federal. O crédito extraordinário da Medida Provisória nº 1.282, de 23/12/2024 (R$ 6,5 bilhões ao Ministério das Cidades), financia este aporte e não entra de novo.

### 2024.10 Até R$ 6 bilhões do FGEDUC para o fundo da poupança do ensino médio (Medida Provisória nº 1.213)
- Ato ou registro: Medida Provisória 1.213, 2024-04-23: https://legis.senado.leg.br/norma/38343456
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); José Wellington Barroso de Araujo Dias (Ministro de Estado do Desenvolvimento e Assistência Social, Família e Combate à Fome); Fernando Haddad (Ministro de Estado da Fazenda); Márcio Luiz França Gomes; Luiz Marinho
- Valor: Medida Provisória nº 1.213/2024, § 6º-B incluído na lei do fundo garantidor (Diário Oficial da União de 23/04/2024; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/38343456/publicacao/38343797
- Trecho: "§ 6º-B. Para cumprimento do disposto no § 6º-A, o fundo de que trata o inciso III do caput integralizará cotas no Fundo de Incentivo à Permanência no Ensino Médio - FIPEM, no montante de até R$ 6.000.000.000,00 (seis bilhões de reais), observado no Fundo de Garantia de Operações de Crédito Educativo - FGEDUC o montante de recursos financeiros disponíveis ainda não vinculados às garantias já contratadas."
- Situação: Perdeu a eficácia em 20/08/2024, segundo o Senado Federal. O fundo que recebe (FIPEM) custeia o incentivo da Lei nº 14.818/2024; a participação direta da União nele, de até R$ 20 bilhões, foi fixada pela Medida Provisória nº 1.198/2023 (item de 2023). Em dezembro de 2024, a Lei nº 15.076 mandou o FGO integralizar mais R$ 4 bilhões no mesmo fundo (abaixo do corte).

### Ficaram de fora em 2024
- **Atos do mesmo programa de um item listado (fica o de maior valor):** MP 1.216 (09/05, FGO até R$ 4,5 bi e subvenção
  até R$ 2 bi, financiada pela MP 1.218); MP 1.226 (29/05, Fundo Social até R$ 15 bi, limite elevado a R$ 20 bi pela Lei
  14.981); MP 1.233 (18/06, R$ 17,6 bi, dos quais R$ 15 bi para a linha do Fundo Social da Lei 14.981 e R$ 2 bi para o
  FAR; o restante, R$ 2,6 bi, fica abaixo do corte); MP 1.269 (22/10, R$ 5 bi, saldo do limite do Fundo Social); MP 1.282
  (23/12, R$ 6,5 bi, financia a MP 1.278).
- **Leis de conversão ou repetição de valor:** Lei 14.962 (conversão da MP 1.218); Lei 15.010 (conversão da MP 1.237);
  Lei 14.902 (Programa Mover, repete os limites de 2024 a 2028 da MP 1.205/2023, item de 2023).
- **Lei 14.818 (16/01, fundo da poupança do ensino médio, até R$ 20 bi):** repete o limite fixado pela MP 1.198, de
  27/11/2023 (item de 2023).
- **Abaixo do 10º lugar (R$ 6 bi):** MP 1.257 (16/09, R$ 5,13 bi,
  dos quais R$ 4,42 bi para antecipar precatórios do Rio Grande do Sul); Fundo Especial de Financiamento de Campanha pago
  em agosto de 2024 (RTN de agosto, linha 4.3.19: R$ 4.951,3 milhões); Lei 15.076 (26/12, R$ 4 bi do FGO para o FIPEM).
- **Lei Complementar 206 (renegociação da dívida do Rio Grande do Sul):** sem valor em reais no texto nem na exposição de
  motivos do projeto (EXM nº 49/2024 MF, lida). Fica fora por falta de valor oficial.
- **Lei 14.973 (desoneração da folha):** a EXM nº 13/2024 MF do projeto estima o custo de manter a contribuição sobre a
  receita bruta (R$ 12 bi em 2024 e 2025, R$ 13 bi em 2026 e 2027), mas descreve a proposta do governo, que era revogar
  o benefício, e não a lei aprovada. Fica fora por não haver estimativa oficial lida do texto aprovado.
- **Lei Complementar 210 (emendas parlamentares) e Lei 14.937 (Letra de Crédito do Desenvolvimento):** limites de regra
  orçamentária e de emissão, não gasto; não entram.

### Não confirmado (2024)
- Cargos de Cristina Kiomi Mori e Gustavo José de Guimarães e Souza (MP 1.286), de Geraldo Alckmin (Lei 14.990), dos
  signatários da Lei 14.981 e de Márcio França e Luiz Marinho (MP 1.213) não confirmados em documento lido; ficam `null`.
- Finalidade da MP 1.225 (arroz) tirada do anexo (formação de estoques públicos e subvenção nas aquisições) e da descrição
  da matéria no Senado.


## 2023 (ano completo)

| # | Movimento | Data | Valor oficial | Tipo | Natureza |
|---|---|---|---|---|---|
| 1 | Programa Bolsa Família recriado no lugar do Auxílio Brasil (Medida Provisória nº 1.164) | 2023-03-02 | R$ 176,5 bi | gasto | estimativa |
| 2 | Pagamento de precatórios atrasados após decisão do STF, em dezembro de 2023 | 2023-12 | R$ 95,274 bi | gasto | pago |
| 3 | Pagamento concentrado de sentenças judiciais e precatórios em maio de 2023 | 2023-05 | R$ 31,041 bi | gasto | pago |
| 4 | Compensação aos estados pelas perdas de ICMS sobre combustíveis (Lei Complementar nº 201) | 2023-10-24 | R$ 27,015 bi | gasto | teto |
| 5 | Redução a zero de PIS/Pasep e Cofins sobre combustíveis em 2023 (Medida Provisória nº 1.157) | 2023-01-02 | R$ 25 bi | renúncia de receita | estimativa |
| 6 | Poupança para estudantes do ensino médio: fundo de até R$ 20 bilhões (Medida Provisória nº 1.198) | 2023-11-28 | R$ 20 bi | gasto | teto |
| 7 | Programa Mobilidade Verde e Inovação (Mover): créditos financeiros às montadoras de 2024 a 2028 (Medida Provisória nº 1.205) | 2023-12-30 | R$ 19,3 bi | renúncia de receita | teto |
| 8 | Salário mínimo de R$ 1.320 a partir de maio de 2023 (Medida Provisória nº 1.172) | 2023-05-01 | R$ 13 bi | gasto | estimativa |
| 9 | Reajuste de 9% para servidores do Poder Executivo federal (Medida Provisória nº 1.170) | 2023-04-28 | R$ 9,62 bi | gasto | estimativa |
| 10 | Dispensa de multas em processos do CARF decididos por voto de qualidade (Medida Provisória nº 1.160) | 2023-01-12 | R$ 8,049 bi | renúncia de receita | estimativa |

### 2023.1 Programa Bolsa Família recriado no lugar do Auxílio Brasil (Medida Provisória nº 1.164)
- Ato ou registro: Medida Provisória 1.164, 2023-03-02: https://legis.senado.leg.br/norma/36861233
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); José Wellington Barroso de Araujo Dias (Ministro de Estado do Desenvolvimento e Assistência Social, Família e Combate à Fome); Fernando Haddad (Ministro de Estado da Fazenda); Simone Nassar Tebet (Ministra de Estado do Planejamento e Orçamento)
- Valor: Exposição de Motivos Interministerial nº 6/2023 MDS MPO MF da Medida Provisória nº 1.164/2023 (Planalto, cópia do Internet Archive); valor de 2023. Fonte lida: https://web.archive.org/web/20260121104736/https://planalto.gov.br/CCIVIL_03/_Ato2023-2026/2023/Exm/Exm-1164-23.pdf
- Trecho: "O novo Bolsa Família beneficiará em 2023 aproximadamente de 21 milhões de famílias, com orçamento no exercício aproximadamente R$ 175,7 bilhões. Estima-se para o ano de 2023 custos administrativos adicionais da ordem de R$ 850 milhões para apoio aos entes federados e outras ações de gestão. Com isso, o impacto orçamentário total previsto é de R$ 176,5 bilhões."
- Situação: Convertida na Lei nº 14.601, de 19/06/2023, segundo o Senado Federal. O valor é o orçamento do programa inteiro em 2023, a maior parte já prevista na lei orçamentária para o programa que ele substituiu; não é dinheiro novo somado ao orçamento.

### 2023.2 Pagamento de precatórios atrasados após decisão do STF, em dezembro de 2023
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 29, N. 12 (dezembro de 2023), 2024-01-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2023/12
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2023, Tabela 3.1 (R$ milhões, preços correntes, coluna dezembro de 2023), soma das cinco linhas de sentenças judiciais e precatórios (benefícios previdenciários urbano e rural, pessoal, BPC e custeio e capital). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/48787_1551088/boletim_dez23.pdf
- Trecho: "Benefícios Previdenciários, Urbano: Sentenças Judiciais e Precatórios 23.422,3; Rural: Sentenças Judiciais e Precatórios 6.217,6; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 13.022,1; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 808,7; 4.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 51.803,4. Nota 12 do mês: crescimento explicado pela destinação de recursos para o adimplemento da decisão judicial de mérito do STF, no âmbito das ADIs nº 7.064 e nº 7.047"
- Situação: Pago em dezembro de 2023. O valor inclui as requisições de pequeno valor pagas no mês. O dinheiro veio do crédito extraordinário da Medida Provisória nº 1.200, de 20/12/2023 (R$ 93,1 bilhões, dos quais R$ 92,4 bilhões para precatórios, segundo a EM nº 100/2023 MPO), que não entra de novo; a medida perdeu a eficácia em 28/05/2024, segundo o Senado Federal.

### 2023.3 Pagamento concentrado de sentenças judiciais e precatórios em maio de 2023
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 29, N. 5 (maio de 2023), 2023-06-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2023/5
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2023, Tabela 3.1 (R$ milhões, preços correntes, coluna maio de 2023), soma das cinco linhas de sentenças judiciais e precatórios (benefícios previdenciários urbano e rural, pessoal, BPC e custeio e capital). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/47344_1471837/boletim_mai23.pdf
- Trecho: "Benefícios Previdenciários, Urbano: Sentenças Judiciais e Precatórios 8.225,5; Rural: Sentenças Judiciais e Precatórios 2.543,5; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 3.911,4; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 355,6; 4.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 16.005,4. Nota 10 do acumulado: explicado pela diferença no cronograma de pagamentos desta rubrica em 2023 e 2022. Enquanto em 2022 a concentração ocorreu em junho (R$ 7,3 bilhões) e agosto (R$ 6,7 bilhões), em 2023 estes pagamentos foram concentrados em maio (R$ 16,0 bilhões)."
- Situação: Pago em maio de 2023, dentro do limite anual para precatórios que vigorava antes da decisão do STF. O valor inclui as requisições de pequeno valor pagas no mês.

### 2023.4 Compensação aos estados pelas perdas de ICMS sobre combustíveis (Lei Complementar nº 201)
- Ato ou registro: Lei Complementar 201, 2023-10-24: https://legis.senado.leg.br/norma/37740658
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda); Camilo Sobreira de Santana (Ministro de Estado da Educação); Nísia Verônica Trindade Lima
- Valor: Lei Complementar nº 201/2023, art. 2º (Diário Oficial da União, edição extra de 24/10/2023; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/37740658/publicacao/37742111
- Trecho: "Art. 2º Em observância ao disposto nos arts. 3º e 14 da Lei Complementar nº 194, de 23 de junho de 2022 , a União compensará a quantia nominal de R$ 27.014.900.000,00 (vinte e sete bilhões quatorze milhões e novecentos mil reais) aos Estados e ao Distrito Federal, a título de quitação total do valor devido em razão da redução da arrecadação do ICMS ocasionada pela aplicação do disposto na referida Lei Complementar"
- Situação: Lei complementar em vigor. Pagamento em parcelas, por transferência direta e abatimento de dívidas dos estados com a União, de 2023 a 2025; o Resultado do Tesouro Nacional registra essas compensações mês a mês (por exemplo, novembro e dezembro de 2023 e janeiro a maio de 2025).

### 2023.5 Redução a zero de PIS/Pasep e Cofins sobre combustíveis em 2023 (Medida Provisória nº 1.157)
- Ato ou registro: Medida Provisória 1.157, 2023-01-02: https://legis.senado.leg.br/norma/36722080
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda)
- Valor: Exposição de Motivos da Medida Provisória nº 1.157/2023 (Planalto, cópia do Internet Archive). Fonte lida: https://web.archive.org/web/20260613033336/http://planalto.gov.br/ccivil_03/_ato2023-2026/2023/exm/exm-1157-23.pdf
- Trecho: "cabe informar que a medida em tela ocasiona renúncia de receitas tributárias estimada em R$ 25 bilhões (vinte e cinco bilhões), que já foi considerada na estimativa de receita orçamentária para 2023"
- Situação: Perdeu a eficácia em 01/06/2023, segundo o Senado Federal. A Medida Provisória nº 1.163, de 28/02/2023, mudou as alíquotas da gasolina e do etanol (redução de receitas estimada em R$ 6,61 bilhões, abaixo do corte).

### 2023.6 Poupança para estudantes do ensino médio: fundo de até R$ 20 bilhões (Medida Provisória nº 1.198)
- Ato ou registro: Medida Provisória 1.198, 2023-11-28: https://legis.senado.leg.br/norma/37874486
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda); Camilo Sobreira de Santana (Ministro de Estado da Educação); Alexandre Silveira de Oliveira
- Valor: Medida Provisória nº 1.198/2023, art. 6º (Diário Oficial da União, edição extra de 28/11/2023; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/37874486/publicacao/37874692
- Trecho: "fica a União autorizada a participar, no limite global de até R$ 20.000.000.000,00 (vinte bilhões de reais), de fundo que, atendidos os requisitos estabelecidos nesta Medida Provisória, tenha por finalidade custear e gerir a poupança dos estudantes vinculados ao programa."
- Situação: Perdeu a eficácia em 06/05/2024, segundo o Senado Federal. A Lei nº 14.818, de 16/01/2024, repetiu o limite de R$ 20 bilhões e não entra de novo. Integralizações posteriores no fundo (FIPEM) vindas de outros fundos aparecem como itens próprios quando entram no corte.

### 2023.7 Programa Mobilidade Verde e Inovação (Mover): créditos financeiros às montadoras de 2024 a 2028 (Medida Provisória nº 1.205)
- Ato ou registro: Medida Provisória 1.205, 2023-12-30: https://legis.senado.leg.br/norma/38066962
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Luciana Barbosa de Oliveira Santos (Ministra de Estado da Ciência, Tecnologia e Inovação); Fernando Haddad (Ministro de Estado da Fazenda); Geraldo José Rodrigues Alckmin Filho (Ministro de Estado do Desenvolvimento, Indústria, Comércio e Serviços)
- Valor: Medida Provisória nº 1.205/2023, art. 15, § 2º (Diário Oficial da União, edição extra de 30/12/2023; texto oficial no Senado Federal); soma dos limites anuais de 2024 a 2028, pelos valores por extenso. Fonte lida: https://legis.senado.leg.br/norma/38066962/publicacao/38083612
- Trecho: "Os créditos financeiros de que trata esta Medida Provisória serão limitados aos seguintes valores globais para cada ano-calendário: [...] 2024 - R$ 3.500.000.000,00 (três bilhões e quinhentos milhões de reais); [...] 2025 - R$ 3.800.000,00 (três bilhões e oitocentos milhões de reais); [...] 2026 - R$ 3.900.000,00 (três bilhões e novecentos milhões de reais); [...] 2027 - R$ 4.000.000,00 (quatro bilhões de reais); [...] 2028 - R$ 4.100.000,00 (quatro bilhões e cem milhões de reais)."
- Situação: Perdeu a eficácia em 31/05/2024, segundo o Senado Federal; a Lei nº 14.902, de 27/06/2024, criou o mesmo programa com os mesmos limites (R$ 3,5 bi, 3,8 bi, 3,9 bi, 4,0 bi e 4,1 bi) e não entra de novo. No texto da medida lido no Senado, os algarismos de 2025 a 2028 aparecem em milhões (por exemplo, "R$ 3.800.000,00") e o valor por extenso em bilhões; a soma usa o valor por extenso, confirmado pela Lei nº 14.902.

### 2023.8 Salário mínimo de R$ 1.320 a partir de maio de 2023 (Medida Provisória nº 1.172)
- Ato ou registro: Medida Provisória 1.172, 2023-05-01: https://legis.senado.leg.br/norma/37004638
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda); Simone Nassar Tebet (Ministra de Estado do Planejamento e Orçamento); Carlos Roberto Lupi; Luiz Marinho
- Valor: Exposição de Motivos Interministerial nº 54/2023 MF MPS MPO MTE da Medida Provisória nº 1.172/2023 (Planalto, cópia do Internet Archive); soma de 2023 a 2025. Fonte lida: https://web.archive.org/web/20260511154647/http://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/exm/exm-1172-23.pdf
- Trecho: "calculou impacto total adicional de R$ 3,3 bilhões em 2023, de R$ 4,8 bilhões em 2024, e de R$ 4,9 bilhões em 2025."
- Situação: Convertida na Lei nº 14.663, de 28/08/2023, segundo o Senado Federal. O valor é o custo adicional na Previdência Social calculado pelo governo.

### 2023.9 Reajuste de 9% para servidores do Poder Executivo federal (Medida Provisória nº 1.170)
- Ato ou registro: Medida Provisória 1.170, 2023-04-28: https://legis.senado.leg.br/norma/37004516
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Esther Dweck (Ministra de Estado da Gestão e da Inovação em Serviços Públicos); Simone Nassar Tebet (Ministra de Estado do Planejamento e Orçamento)
- Valor: Exposição de Motivos da Medida Provisória nº 1.170/2023, assinada por Esther Dweck e Simone Tebet (Planalto, cópia do Internet Archive); valor de 2023. Fonte lida: https://web.archive.org/web/20260110071855/https://www.planalto.gov.br/ccivIl_03/_Ato2023-2026/2023/Exm/Exm-1170-23.pdf
- Trecho: "enquanto remete a um custo da ordem de R$ 9,62 bilhões para o exercício de 2023 e de R$ 13,82 bilhões anualizado."
- Situação: Convertida na Lei nº 14.673, de 14/09/2023, segundo o Senado Federal. O valor é o custo de 2023; anualizado, o governo estimou R$ 13,82 bilhões.

### 2023.10 Dispensa de multas em processos do CARF decididos por voto de qualidade (Medida Provisória nº 1.160)
- Ato ou registro: Medida Provisória 1.160, 2023-01-12: https://legis.senado.leg.br/norma/36770869
- Assinaram: Luiz Inácio Lula da Silva (Presidente da República); Fernando Haddad (Ministro de Estado da Fazenda)
- Valor: Exposição de Motivos nº 16/2023 MF da Medida Provisória nº 1.160/2023, item 15, assinada por Fernando Haddad (Planalto, cópia do Internet Archive). Fonte lida: https://web.archive.org/web/20260304080937/https://www.planalto.gov.br/CCIVIL_03/////_Ato2023-2026/2023/Exm/Exm-1160-23.pdf
- Trecho: "cabe informar que o art. 3º da medida em tela ocasiona renúncia de receitas tributárias estimada em R$ 8.049 milhões (oito bilhões e quarenta e nove milhões de reais) em 2023"
- Situação: Perdeu a eficácia em 01/06/2023, segundo o Senado Federal. A exposição de motivos diz que a renúncia seria compensada pela arrecadação de outra medida provisória editada no mesmo dia.

### Ficaram de fora em 2023
- **MP 1.200 (20/12, crédito extraordinário de R$ 93,1 bi, dos quais R$ 92,4 bi para precatórios):** financiou o pagamento
  de dezembro de 2023, listado pelo valor pago (R$ 95,3 bi, maior).
- **Abaixo do 10º lugar (R$ 8,05 bi):** MP 1.163 (28/02, alíquotas de gasolina, álcool, GNV e querosene de aviação; EXM:
  "redução de receitas tributárias estimada em R$ 6,61 bilhões"); Lei 14.640 (31/07, Escola em Tempo Integral, R$ 3,5 bi
  aos estados); MP 1.165 (Mais Médicos especialistas, R$ 712,5 mi em 2023 e cerca de R$ 3 bi nos dois anos seguintes);
  MP 1.175 e MP 1.178 (desconto patrocinado na compra de veículos, limites de R$ 500 mi e R$ 1 bi, ampliados depois).
- **MP 1.189 (27/09, Rio Grande do Sul):** eleva de R$ 20 bi para R$ 20,1 bi o limite de participação da União no FGI
  fixado em 2020; o valor novo é R$ 100 mi.
- **MP 1.176 e Lei 14.690 (Desenrola Brasil):** sem valor total da União no texto lido (só limites por devedor); a EXM da
  MP 1.199 cita R$ 137 bi em dívidas reduzidas a R$ 25 bi no leilão, valores privados, não gasto da União.
- **Lei Complementar 203 (15/12):** exclui até R$ 6 bi da poupança do ensino médio dos limites da LC 200; exceção à regra
  fiscal, não gasto novo.
- **Lei 14.784 (desoneração da folha até 2027):** sem valor no texto e sem exposição de motivos do Executivo (projeto do
  Congresso).
- **Medidas de aumento de receita** (MPs 1.159, 1.171, 1.184, 1.185 e 1.202): ficam para a coluna de receitas.
- **Pagamentos no RTN de 2023:** compensações da LC 194/2022 e transferências temporárias ao FPE e ao FPM (LC 201/2023),
  registradas em novembro e dezembro, já cobertas pelo item da LC 201; R$ 2,9 bi da Lei Paulo Gustavo (LC 195/2022) pagos
  em julho, abaixo do corte.

### Não confirmado (2023)
- Cargos de Alexandre Silveira de Oliveira (MP 1.198; a EXM foi assinada pelo substituto Erain Pereira da Cruz), Carlos
  Roberto Lupi e Luiz Marinho (MP 1.172; ordem das assinaturas diferente da ordem dos ministérios no cabeçalho) e Nísia
  Trindade Lima (LC 201) não confirmados; ficam `null`.
- MP 1.164: o valor é o orçamento total do programa em 2023 dito na exposição de motivos, não um gasto adicional; o item
  diz isso na situação.


## 2022 (ano completo)

| # | Movimento | Data | Valor oficial | Tipo | Natureza |
|---|---|---|---|---|---|
| 1 | Pagamento concentrado de sentenças judiciais e precatórios em agosto de 2022 | 2022-08 | R$ 27,262 bi | gasto | pago |
| 2 | Crédito extraordinário para o adicional de R$ 200 do Auxílio Brasil e o Auxílio Gás (Medida Provisória nº 1.130) | 2022-07-22 | R$ 27,095 bi | crédito extraordinário | teto |
| 3 | Política Nacional Aldir Blanc de Fomento à Cultura: R$ 3 bilhões por ano durante cinco anos (Lei nº 14.399) | 2022-07-08 | R$ 15 bi | gasto | teto |
| 4 | Crédito extraordinário para auxílio a caminhoneiros e taxistas e para estados que reduziram tributos do etanol (Medida Provisória nº 1.131) | 2022-07-28 | R$ 10,901 bi | crédito extraordinário | teto |
| 5 | Pagamento de sentenças judiciais e precatórios em junho de 2022 | 2022-06 | R$ 9,577 bi | gasto | pago |
| 6 | Repasse a estados e municípios do bônus da segunda rodada da cessão onerosa, em maio de 2022 | 2022-05 | R$ 7,7 bi | gasto | pago |
| 7 | Crédito extraordinário para benefícios da Previdência Social em 2022 (Medida Provisória nº 1.144) | 2022-12-15 | R$ 7,564 bi | crédito extraordinário | teto |
| 8 | Fundo Especial de Financiamento de Campanha das eleições de 2022, pago em agosto de 2022 | 2022-08 | R$ 4,955 bi | gasto | pago |
| 9 | Apoio ao setor cultural afetado pela pandemia (Lei Complementar nº 195, Lei Paulo Gustavo) | 2022-07-08 | R$ 3,862 bi | gasto | teto |
| 10 | Crédito extraordinário para custear a gratuidade de idosos no transporte público (Medida Provisória nº 1.134) | 2022-08-26 | R$ 2,5 bi | crédito extraordinário | teto |

### 2022.1 Pagamento concentrado de sentenças judiciais e precatórios em agosto de 2022
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 28, N. 8 (agosto de 2022), 2022-09-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2022/8
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de agosto de 2022, Tabela 3.1 (R$ milhões, preços correntes, coluna agosto de 2022), soma das cinco linhas de sentenças judiciais e precatórios (benefícios previdenciários urbano e rural, pessoal, BPC e custeio e capital). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/44839_1419442/boletim_ago22.pdf
- Trecho: "Benefícios Previdenciários, Urbano: Sentenças Judiciais e Precatórios 9.725,7; Rural: Sentenças Judiciais e Precatórios 2.530,1; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 8.125,4; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 418,9; 4.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 6.462,0. Nota 10 do mês: explicado, principalmente, pelo pagamento de Sentenças Judiciais e Precatórios no montante de R$ 12,3 bilhões em agosto de 2022 frente a R$ 1,4 bilhão em agosto de 2021 (a valores de agosto de 2022)."
- Situação: Pago em agosto de 2022. O valor inclui as requisições de pequeno valor pagas no mês. Em 2022 os pagamentos se dividiram entre junho e agosto; em 2021 ficaram concentrados em junho.

### 2022.2 Crédito extraordinário para o adicional de R$ 200 do Auxílio Brasil e o Auxílio Gás (Medida Provisória nº 1.130)
- Ato ou registro: Medida Provisória 1.130, 2022-07-22: https://legis.senado.leg.br/norma/36111103
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 1.130/2022, art. 1º (Diário Oficial da União, edição extra de 22/07/2022; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/36111103/publicacao/36111201
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Cidadania e de Encargos Financeiros da União, no valor de R$ 27.094.524.171,00 (vinte e sete bilhões noventa e quatro milhões quinhentos e vinte e quatro mil cento e setenta e um reais)"
- Situação: Convertida na Lei nº 14.469, de 16/11/2022, que repete o valor e não entra de novo. O gasto foi autorizado pela Emenda Constitucional nº 123/2022, que não é lei nem medida provisória; esta medida abriu o crédito.

### 2022.3 Política Nacional Aldir Blanc de Fomento à Cultura: R$ 3 bilhões por ano durante cinco anos (Lei nº 14.399)
- Ato ou registro: Lei 14.399, 2022-07-08: https://legis.senado.leg.br/norma/36062349
- Assinaram: Jair Messias Bolsonaro (Presidente da República)
- Valor: Lei nº 14.399/2022, art. 6º (Diário Oficial da União, edição extra de 08/07/2022; texto oficial no Senado Federal); cinco parcelas anuais de R$ 3 bilhões. Fonte lida: https://legis.senado.leg.br/norma/36062349/publicacao/36072638
- Trecho: "Art. 6º A União entregará aos Estados, ao Distrito Federal e aos Municípios, a cada ano, em parcela única, o valor correspondente a R$ 3.000.000.000,00 (três bilhões de reais), no primeiro exercício subsequente ao da entrada em vigor desta Lei e nos 4 (quatro) anos seguintes."
- Situação: Lei em vigor; originada de projeto do Congresso Nacional. A Medida Provisória nº 1.135/2022 tentou adiar os pagamentos para 2024 a 2028 e perdeu a eficácia em 05/02/2023; a Medida Provisória nº 1.274/2024 e a Lei nº 15.132/2025 mudaram regras de execução sem reduzir os R$ 15 bilhões.

### 2022.4 Crédito extraordinário para auxílio a caminhoneiros e taxistas e para estados que reduziram tributos do etanol (Medida Provisória nº 1.131)
- Ato ou registro: Medida Provisória 1.131, 2022-07-28: https://legis.senado.leg.br/norma/36159057
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 1.131/2022, art. 1º (Diário Oficial da União, edição extra de 28/07/2022; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/36159057/publicacao/36159220
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério do Trabalho e Previdência e de Transferências a Estados, Distrito Federal e Municípios, no valor de R$ 10.901.400.000,00 (dez bilhões novecentos e um milhões e quatrocentos mil reais)"
- Situação: Perdeu a eficácia em 28/11/2022, segundo o Senado Federal. Gastos previstos na Emenda Constitucional nº 123/2022.

### 2022.5 Pagamento de sentenças judiciais e precatórios em junho de 2022
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 28, N. 6 (junho de 2022), 2022-07-28: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2022/6
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2022, Tabela 3.1 (R$ milhões, preços correntes, coluna junho de 2022), soma das cinco linhas de sentenças judiciais e precatórios (benefícios previdenciários urbano e rural, pessoal, BPC e custeio e capital). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/44179_1398982/boletim_jun22.pdf
- Trecho: "Benefícios Previdenciários, Urbano: Sentenças Judiciais e Precatórios 1.707,2; Rural: Sentenças Judiciais e Precatórios 389,8; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 220,7; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 185,3; 4.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 7.073,9. Nota 14 do mês: essa redução resultou de ajuste no calendário de pagamentos de Sentenças Judiciais e Precatórios em 2022, com efeitos no comparativo entre junho de 2022, em que foram pagos R$7,1 bilhões, e junho de 2021, com pagamentos de R$ 18,3 bilhões."
- Situação: Pago em junho de 2022. O valor inclui as requisições de pequeno valor pagas no mês. A outra parte da concentração de 2022 foi paga em agosto (item próprio).

### 2022.6 Repasse a estados e municípios do bônus da segunda rodada da cessão onerosa, em maio de 2022
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 28, N. 5 (maio de 2022), 2022-06-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2022/5
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de maio de 2022, Nota 10 do mês (valor arredondado pelo Tesouro); linha 2.6 Demais transferências por repartição de receita de maio de 2022: R$ 7.698,9 milhões. Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/43920_2193378/boletim_mai22.pdf
- Trecho: "2.6 Demais 25,8 7.698,9 (maio de 2021, maio de 2022). Nota 10 do mês: variação explicada pelas transferências em maio de 2022 à estados e municípios no valor de R$ 7,7 bilhões relativos aos recursos de bônus de assinatura decorrentes da segunda rodada da cessão onerosa (Campos de Sépia e Atapu"
- Situação: Pago em maio de 2022. A linha do Tesouro em que o repasse aparece (2.6 Demais, R$ 7.698,9 milhões em maio de 2022) inclui pequenos valores de outras transferências (R$ 25,8 milhões em maio de 2021). A União recebeu R$ 11,2 bilhões de bônus de assinatura nessa rodada, segundo a mesma nota.

### 2022.7 Crédito extraordinário para benefícios da Previdência Social em 2022 (Medida Provisória nº 1.144)
- Ato ou registro: Medida Provisória 1.144, 2022-12-15: https://legis.senado.leg.br/norma/36597629
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 1.144/2022, art. 1º (Diário Oficial da União de 15/12/2022; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/36597629/publicacao/36602607
- Trecho: "Art. 1º Fica aberto crédito extraordinário em favor do Ministério do Trabalho e Previdência, no valor de R$ 7.564.496.198,00 (sete bilhões quinhentos e sessenta e quatro milhões quatrocentos e noventa e seis mil cento e noventa e oito reais)"
- Situação: Perdeu a eficácia em 24/05/2023, segundo o Senado Federal.

### 2022.8 Fundo Especial de Financiamento de Campanha das eleições de 2022, pago em agosto de 2022
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 28, N. 8 (agosto de 2022), 2022-09-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2022/8
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de agosto de 2022, linha 4.3.19 Financiamento de Campanha Eleitoral (R$ milhões) e Nota 15 do mês. Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/44839_1419442/boletim_ago22.pdf
- Trecho: "Nota 15 - Financiamento de Campanha Eleitoral (+R$ 4.955,3 milhões): explicado pelo pagamento desta rubrica em agosto de 2022, sem contrapartida no mesmo mês do ano anterior."
- Situação: Pago em agosto de 2022. O valor foi fixado na lei orçamentária de 2022, que não entra como ato.

### 2022.9 Apoio ao setor cultural afetado pela pandemia (Lei Complementar nº 195, Lei Paulo Gustavo)
- Ato ou registro: Lei Complementar 195, 2022-07-08: https://legis.senado.leg.br/norma/36061880
- Assinaram: Jair Messias Bolsonaro (Presidente da República)
- Valor: Lei Complementar nº 195/2022, art. 3º (Diário Oficial da União, edição extra de 08/07/2022; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/36061880/publicacao/36063789
- Trecho: "Art. 3º A União entregará aos Estados, ao Distrito Federal e aos Municípios R$ 3.862.000.000,00 (três bilhões, oitocentos e sessenta e dois milhões de reais) para aplicação em ações emergenciais que visem a combater e mitigar os efeitos da pandemia da covid-19 sobre o setor cultural."
- Situação: Lei complementar em vigor; originada de projeto do Congresso Nacional. O Tesouro Nacional registrou o pagamento de R$ 2,9 bilhões em julho de 2023, como restos a pagar.

### 2022.10 Crédito extraordinário para custear a gratuidade de idosos no transporte público (Medida Provisória nº 1.134)
- Ato ou registro: Medida Provisória 1.134, 2022-08-26: https://legis.senado.leg.br/norma/36315739
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Sérgio Nogueira de Oliveira
- Valor: Medida Provisória nº 1.134/2022, art. 1º (Diário Oficial da União de 26/08/2022; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/36315739/publicacao/36315867
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor de Encargos Financeiros da União, no valor de R$ 2.500.000.000,00 (dois bilhões e quinhentos milhões de reais), para atender à programação constante do Anexo."
- Situação: Finalidade segundo a EM nº 295/2022 ME, assinada por Paulo Guedes: assistência financeira aos entes com transporte público coletivo para custear a gratuidade de idosos até 31/12/2022, conforme o art. 5º, IV, da Emenda Constitucional nº 123/2022.

### Ficaram de fora em 2022
- **Emenda Constitucional nº 123/2022:** autorizou os gastos do segundo semestre (adicional do Auxílio Brasil, auxílios a
  caminhoneiros e taxistas, Auxílio Gás, gratuidade de idosos, crédito do etanol), mas emenda constitucional não é lei nem
  medida provisória; os créditos que abriram o dinheiro (MPs 1.130, 1.131 e 1.134) entram como itens.
- **Leis de conversão:** Lei 14.469 (conversão da MP 1.130); Lei 14.347 (25/05, crédito de R$ 6,412 bi à Saúde) e Lei
  14.433 (R$ 1,2 bi) repetem créditos de medidas provisórias anteriores.
- **Lei Complementar 194 (teto do ICMS) e Lei Complementar 192 (combustíveis):** sem valor em reais no texto; a compensação
  aos estados foi fixada pela LC 201/2023 (item de 2023).
- **MP 1.128 (perdas de crédito das instituições financeiras):** a EXM prevê aumento de arrecadação em 2025 e 2026 (R$ 17,9
  bi e R$ 11,6 bi) e redução em 2027 e 2028 (R$ 23,1 bi e R$ 6,3 bi); é efeito de calendário, sem renúncia líquida.
- **MP 1.136 (FNDCT):** limite de R$ 5,555 bi para aplicar recursos do fundo em 2022; restrição de despesa, não gasto novo.
- **MP 1.135:** adiava os pagamentos da LC 195 e da Lei 14.399; perdeu a eficácia em 05/02/2023.
- **MP 1.105 e MP 1.107/Lei 14.438 (FGTS):** dinheiro dos trabalhadores, não da União.
- **Abaixo do 10º lugar (R$ 2,5 bi):** MP 1.111 e Lei 14.433 (R$ 1,2 bi, subvenção ao Pronaf); MP 1.143 (salário mínimo de
  R$ 1.302 em 2023; a EXM traz só o custo de cada R$ 1 de aumento, R$ 254,53 mi por ano no RGPS, sem custo total).
- **Pagamentos do RTN de 2022:** antecipação do 13º de aposentados (abril a junho) é calendário de despesa obrigatória, não
  pagamento atípico de gasto fixado antes; não entra.

### Não confirmado (2022)
- Cargo de Paulo Sérgio Nogueira de Oliveira (MP 1.134) não confirmado; fica `null`. Paulo Guedes: "Ministro de Estado da
  Economia" pelas EMs do Ministério da Economia que ele assinou em 2022 (nº 78, 250, 260, 295 e 439).


## 2021 (ano completo)

| # | Movimento | Data | Valor oficial | Tipo | Natureza |
|---|---|---|---|---|---|
| 1 | Auxílio Emergencial 2021 (Medida Provisória nº 1.039) | 2021-03-18 | R$ 43 bi | gasto | estimativa |
| 2 | Pagamento concentrado de sentenças judiciais e precatórios em junho de 2021 | 2021-06 | R$ 34,48 bi | gasto | pago |
| 3 | Crédito extraordinário para prorrogar o Auxílio Emergencial 2021 (Medida Provisória nº 1.056) | 2021-07-06 | R$ 20,272 bi | crédito extraordinário | teto |
| 4 | Crédito extraordinário para o Benefício Emergencial de Manutenção do Emprego e da Renda de 2021 (Medida Provisória nº 1.044) | 2021-04-28 | R$ 9,978 bi | crédito extraordinário | teto |
| 5 | Crédito extraordinário para o Ministério da Saúde no combate à covid-19 (Medida Provisória nº 1.062) | 2021-08-10 | R$ 9,102 bi | crédito extraordinário | teto |
| 6 | Crédito extraordinário para compra de vacinas contra a covid-19 (Medida Provisória nº 1.083) | 2021-12-24 | R$ 6,412 bi | crédito extraordinário | teto |
| 7 | Crédito extraordinário para compra de vacinas contra a covid-19 (Medida Provisória nº 1.048) | 2021-05-10 | R$ 5,5 bi | crédito extraordinário | teto |
| 8 | Crédito extraordinário para o Ministério da Saúde no combate à covid-19 (Medida Provisória nº 1.041) | 2021-03-31 | R$ 5,324 bi | crédito extraordinário | teto |
| 9 | Crédito extraordinário para o fundo garantidor do Pronampe (Medida Provisória nº 1.053) | 2021-06-04 | R$ 5 bi | crédito extraordinário | teto |
| 10 | Crédito extraordinário para o auxílio emergencial de 2020 a pessoas provedoras de família monoparental (Medida Provisória nº 1.084) | 2021-12-24 | R$ 4,153 bi | crédito extraordinário | teto |

### 2021.1 Auxílio Emergencial 2021 (Medida Provisória nº 1.039)
- Ato ou registro: Medida Provisória 1.039, 2021-03-18: https://legis.senado.leg.br/norma/33338529
- Assinaram: Jair Messias Bolsonaro (Presidente da República); João Inácio Ribeiro Roma Neto (Ministro de Estado da Cidadania); Wagner de Campos Rosário; José Levi Mello do Amaral Júnior
- Valor: Exposição de Motivos Interministerial nº 6/2021 MCID AGU CGU da Medida Provisória nº 1.039/2021 (Planalto, cópia do Internet Archive). Fonte lida: https://web.archive.org/web/20260608235150/http://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/exm/exm-mp-1039-21.pdf
- Trecho: "Assim, para atender integralmente a proposta da presente Medida Provisória, serão necessários R$ 43 bilhões (quarenta e três bilhões de reais) para o pagamento de benefícios para 45,6 milhões (quarenta e cinco milhões e seiscentas mil) de pessoas elegíveis"
- Situação: Perdeu a eficácia em 16/07/2021, segundo o Senado Federal. Financiada pelos créditos extraordinários das Medidas Provisórias nº 1.037 (R$ 42,58 bilhões) e nº 1.038 (R$ 394,56 milhões), de 18/03/2021, que não entram de novo. A prorrogação do auxílio teve crédito próprio (Medida Provisória nº 1.056, item próprio). A Emenda Constitucional nº 109/2021 limitou o custo a R$ 44 bilhões.

### 2021.2 Pagamento concentrado de sentenças judiciais e precatórios em junho de 2021
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 27, N. 6 (junho de 2021), 2021-07-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2021/6
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2021, Tabela 3.1 (R$ milhões, preços correntes, coluna junho de 2021), soma das cinco linhas de sentenças judiciais e precatórios; a concentração em junho é dita no Resultado do Tesouro Nacional de agosto de 2022, Nota 14. Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/40424_1257203/boletim_jun21_.pdf
- Trecho: "Benefícios Previdenciários, Urbano: Sentenças Judiciais e Precatórios 8.602,1; Rural: Sentenças Judiciais e Precatórios 2.229,3; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 6.940,4; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 353,9; 4.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 16.354,0. RTN de agosto de 2022, Nota 14: Enquanto em 2021, a concentração ocorreu no mês de junho (R$ 18,1 bilhões a valores de agosto de 2022"
- Situação: Pago em junho de 2021. O valor inclui as requisições de pequeno valor pagas no mês. O boletim de junho de 2021 compara o mês com junho de 2020 ("redução nos pagamentos de precatórios"); a concentração dos pagamentos de 2021 em junho é registrada pelo Tesouro no boletim de agosto de 2022.

### 2021.3 Crédito extraordinário para prorrogar o Auxílio Emergencial 2021 (Medida Provisória nº 1.056)
- Ato ou registro: Medida Provisória 1.056, 2021-07-06: https://legis.senado.leg.br/norma/34259770
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 1.056/2021, art. 1º (Diário Oficial da União de 06/07/2021; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/34259770/publicacao/34260123
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Cidadania, no valor de R$ 20.272.300.000,00 (vinte bilhões duzentos e setenta e dois milhões e trezentos mil reais)"
- Situação: Perdeu a eficácia em 15/11/2021, segundo o Senado Federal. Segundo a EM nº 166/2021 ME, o crédito custeia a prorrogação do Auxílio Emergencial 2021 além das quatro parcelas previstas na Medida Provisória nº 1.039; é dinheiro adicional ao do item da Medida Provisória nº 1.039.

### 2021.4 Crédito extraordinário para o Benefício Emergencial de Manutenção do Emprego e da Renda de 2021 (Medida Provisória nº 1.044)
- Ato ou registro: Medida Provisória 1.044, 2021-04-28: https://legis.senado.leg.br/norma/33668073
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 1.044/2021, art. 1º (Diário Oficial da União de 28/04/2021; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/33668073/publicacao/33675030
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Economia, no valor de R$ 9.977.701.233,00 (nove bilhões novecentos e setenta e sete milhões setecentos e um mil duzentos e trinta e três reais)"
- Situação: Perdeu a eficácia em 07/09/2021, segundo o Senado Federal. Financia o novo programa criado pela Medida Provisória nº 1.045, de 27/04/2021, cuja exposição de motivos estima custo de R$ 9.977.537.704,87 (menor, por isso não entra como item próprio).

### 2021.5 Crédito extraordinário para o Ministério da Saúde no combate à covid-19 (Medida Provisória nº 1.062)
- Ato ou registro: Medida Provisória 1.062, 2021-08-10: https://legis.senado.leg.br/norma/34664444
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 1.062/2021, art. 1º (Diário Oficial da União de 10/08/2021; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/34664444/publicacao/34664521
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Saúde, no valor de R$ 9.102.436.262,00 (nove bilhões cento e dois milhões quatrocentos e trinta e seis mil duzentos e sessenta e dois reais)"
- Situação: Perdeu a eficácia em 07/12/2021, segundo o Senado Federal.

### 2021.6 Crédito extraordinário para compra de vacinas contra a covid-19 (Medida Provisória nº 1.083)
- Ato ou registro: Medida Provisória 1.083, 2021-12-24: https://legis.senado.leg.br/norma/35319984
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Marcelo Pacheco dos Guaranys
- Valor: Medida Provisória nº 1.083/2021, art. 1º (Diário Oficial da União de 24/12/2021; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/35319984/publicacao/35320938
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Saúde, no valor de R$ 6.412.000.000,00 (seis bilhões quatrocentos e doze milhões de reais)"
- Situação: Convertida na Lei nº 14.347, de 25/05/2022, que repete o valor e não entra de novo.

### 2021.7 Crédito extraordinário para compra de vacinas contra a covid-19 (Medida Provisória nº 1.048)
- Ato ou registro: Medida Provisória 1.048, 2021-05-10: https://legis.senado.leg.br/norma/33824911
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 1.048/2021, art. 1º (Diário Oficial da União de 10/05/2021; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/33824911/publicacao/33825299
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Saúde, no valor de R$ 5.500.071.904,00 (cinco bilhões quinhentos milhões setenta e um mil novecentos e quatro reais)"
- Situação: Perdeu a eficácia em 19/09/2021, segundo o Senado Federal.

### 2021.8 Crédito extraordinário para o Ministério da Saúde no combate à covid-19 (Medida Provisória nº 1.041)
- Ato ou registro: Medida Provisória 1.041, 2021-03-31: https://legis.senado.leg.br/norma/33378810
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 1.041/2021, art. 1º (Diário Oficial da União de 31/03/2021; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/33378810/publicacao/33379310
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Saúde, no valor de R$ 5.324.320.142,00 (cinco bilhões trezentos e vinte e quatro milhões trezentos e vinte mil cento e quarenta e dois reais)"
- Situação: Perdeu a eficácia em 10/08/2021, segundo o Senado Federal.

### 2021.9 Crédito extraordinário para o fundo garantidor do Pronampe (Medida Provisória nº 1.053)
- Ato ou registro: Medida Provisória 1.053, 2021-06-04: https://legis.senado.leg.br/norma/34132654
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 1.053/2021, art. 1º (Diário Oficial da União de 04/06/2021; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/34132654/publicacao/34132927
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor de Encargos Financeiros da União, no valor de R$ 5.000.000.000,00 (cinco bilhões de reais)"
- Situação: Perdeu a eficácia em 14/10/2021, segundo o Senado Federal. A Lei nº 14.161, de 02/06/2021, tornou o Pronampe permanente sem fixar valor.

### 2021.10 Crédito extraordinário para o auxílio emergencial de 2020 a pessoas provedoras de família monoparental (Medida Provisória nº 1.084)
- Ato ou registro: Medida Provisória 1.084, 2021-12-24: https://legis.senado.leg.br/norma/35320056
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Marcelo Pacheco dos Guaranys
- Valor: Medida Provisória nº 1.084/2021, art. 1º (Diário Oficial da União de 24/12/2021; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/35320056/publicacao/35338729
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Cidadania, no valor de R$ 4.153.017.000,00 (quatro bilhões cento e cinquenta e três milhões e dezessete mil reais)"
- Situação: Perdeu a eficácia em 01/06/2022, segundo o Senado Federal. Segundo a EM nº 382/2021 ME, decorre da derrubada do veto nº 35/2020 e da Lei nº 14.171/2021, que mudou as regras do auxílio emergencial de 2020 para pessoas provedoras de família monoparental.

### Ficaram de fora em 2021
- **Créditos do mesmo programa de um item listado (fica o de maior valor):** MP 1.037 (R$ 42,58 bi) e MP 1.038 (R$ 394,56
  mi), que financiam o Auxílio Emergencial 2021 da MP 1.039 (R$ 43 bi); MP 1.045 (novo BEm, custo estimado de R$ 9,9775 bi
  na EXM, menor que o crédito da MP 1.044); MP 1.088 (R$ 3,5 bi) e Lei 14.172 (R$ 3,5 bi, internet para alunos e
  professores), abaixo do corte.
- **MP 1.052 e Lei 14.227 (fundo de estruturação de projetos de concessão, "no limite total de R$ 11.000.000.000,00"):** o
  mesmo limite já estava no art. 32 da Lei 12.712/2012 (texto original lido no Senado), que a medida só redirecionou; o
  valor não é novo.
- **Abaixo do 10º lugar (R$ 4,15 bi):** MP 1.032 (R$ 2,86 bi, Saúde); MP 1.043 (R$ 2,69 bi, Saúde); MP 1.076 (Benefício
  Extraordinário do Auxílio Brasil, R$ 2,67 bi em 2021 pela EXM); Lei 14.148 (Perse, indenizações limitadas a R$ 2,5 bi);
  Lei 14.182 (Eletrobras, compensação limitada a R$ 3,5 bi).
- **MP 1.061 (Auxílio Brasil):** sem valor total no texto nem na exposição de motivos lida.
- **Pagamentos do RTN de 2021:** capitalização de empresa a ser criada a partir da cisão da CBTU (R$ 2,8 bi) e do Banco da
  Amazônia (R$ 1,0 bi) em dezembro, abaixo do corte.

### Não confirmado (2021)
- Cargos de Wagner de Campos Rosário e José Levi Mello do Amaral Júnior (MP 1.039; a ordem das assinaturas da EXM difere da
  ordem dos órgãos no cabeçalho) e de Marcelo Pacheco dos Guaranys (MPs 1.083 e 1.084, que assinou as EMs sem indicar
  cargo) ficam `null`.


## 2020 (ano completo)

| # | Movimento | Data | Valor oficial | Tipo | Natureza |
|---|---|---|---|---|---|
| 1 | Crédito extraordinário de R$ 101,6 bilhões para o auxílio emergencial (Medida Provisória nº 988) | 2020-07-01 | R$ 101,6 bi | crédito extraordinário | teto |
| 2 | Crédito extraordinário de R$ 98,2 bilhões para o auxílio emergencial (Medida Provisória nº 937) | 2020-04-02 | R$ 98,2 bi | crédito extraordinário | teto |
| 3 | Auxílio emergencial residual de setembro a dezembro de 2020 (Medida Provisória nº 1.000) | 2020-09-03 | R$ 79,067 bi | gasto | estimativa |
| 4 | Crédito extraordinário de R$ 60,2 bilhões para o auxílio financeiro a estados e municípios (Medida Provisória nº 978) | 2020-06-04 | R$ 60,189 bi | crédito extraordinário | teto |
| 5 | Compensação aos estados pelas perdas da Lei Kandir, de 2020 a 2037 (Lei Complementar nº 176) | 2020-12-29 | R$ 58 bi | gasto | teto |
| 6 | Crédito extraordinário de R$ 51,6 bilhões para o Benefício Emergencial de Manutenção do Emprego e da Renda (Medida Provisória nº 935) | 2020-04-01 | R$ 51,642 bi | crédito extraordinário | teto |
| 7 | Programa Emergencial de Suporte a Empregos: R$ 34 bilhões da União para financiar folhas de pagamento (Medida Provisória nº 944) | 2020-04-03 | R$ 34 bi | gasto | teto |
| 8 | Pagamento concentrado de sentenças judiciais e precatórios em junho de 2020 | 2020-06 | R$ 33,095 bi | gasto | pago |
| 9 | Crédito extraordinário de R$ 29,1 bilhões para o auxílio emergencial e despesas da pandemia (Medida Provisória nº 970) | 2020-05-26 | R$ 29,058 bi | crédito extraordinário | teto |
| 10 | Crédito extraordinário de R$ 25,7 bilhões para o auxílio emergencial (Medida Provisória nº 956) | 2020-04-24 | R$ 25,72 bi | crédito extraordinário | teto |

### 2020.1 Crédito extraordinário de R$ 101,6 bilhões para o auxílio emergencial (Medida Provisória nº 988)
- Ato ou registro: Medida Provisória 988, 2020-07-01: https://legis.senado.leg.br/norma/32302303
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 988/2020, art. 1º (Diário Oficial da União de 01/07/2020; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/32302303/publicacao/32303414
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Cidadania, no valor de R$ 101.600.000.000,00 (cento e um bilhões e seiscentos milhões de reais)"
- Situação: Perdeu a eficácia em 04/11/2020, segundo o Senado Federal. Financia o auxílio emergencial criado pela Lei nº 13.982, de 02/04/2020 (lei do Congresso, sem valor no texto), prorrogado depois por decreto; cada crédito é uma parcela própria de dinheiro e entra como item.

### 2020.2 Crédito extraordinário de R$ 98,2 bilhões para o auxílio emergencial (Medida Provisória nº 937)
- Ato ou registro: Medida Provisória 937, 2020-04-02: https://legis.senado.leg.br/norma/32046819
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 937/2020, art. 1º (Diário Oficial da União de 02/04/2020; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/32046819/publicacao/32048011
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Cidadania, no valor de R$ 98.200.000.000,00 (noventa e oito bilhões e duzentos milhões de reais)"
- Situação: Perdeu a eficácia em 30/07/2020, segundo o Senado Federal. Financia o auxílio emergencial criado pela Lei nº 13.982, de 02/04/2020 (lei do Congresso, sem valor no texto), prorrogado depois por decreto; cada crédito é uma parcela própria de dinheiro e entra como item.

### 2020.3 Auxílio emergencial residual de setembro a dezembro de 2020 (Medida Provisória nº 1.000)
- Ato ou registro: Medida Provisória 1.000, 2020-09-03: https://legis.senado.leg.br/norma/32615700
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Onyx Lorenzoni (Ministro de Estado da Cidadania)
- Valor: Exposição de Motivos nº 30/2020 MCID da Medida Provisória nº 1.000/2020, item 16, assinada por Onyx Dornelles Lorenzoni (Planalto, cópia do Internet Archive). Fonte lida: https://web.archive.org/web/20260711014620/https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/exm/exm-mp-1000-20.pdf
- Trecho: "Assim, para atender integralmente a proposta da presente Medida Provisória, serão necessários R$ 79.067.284.289,08 para o pagamento de benefícios para 61.488.087 de pessoas elegíveis"
- Situação: Perdeu a eficácia em 10/02/2021, segundo o Senado Federal. O valor inclui R$ 11,47 bilhões de crédito ordinário do Bolsa Família usados no auxílio, segundo a mesma exposição de motivos. O crédito extraordinário da Medida Provisória nº 999, de 02/09/2020 (R$ 67,6 bilhões), financia o auxílio residual e não entra de novo.

### 2020.4 Crédito extraordinário de R$ 60,2 bilhões para o auxílio financeiro a estados e municípios (Medida Provisória nº 978)
- Ato ou registro: Medida Provisória 978, 2020-06-04: https://legis.senado.leg.br/norma/32240840
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 978/2020, art. 1º (Diário Oficial da União de 04/06/2020; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/32240840/publicacao/32240956
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor de Transferências a Estados, Distrito Federal e Municípios, no valor de R$ 60.189.488.452,00 (sessenta bilhões cento e oitenta e nove milhões quatrocentos e oitenta e oito mil quatrocentos e cinquenta e dois reais)"
- Situação: Perdeu a eficácia em 01/10/2020, segundo o Senado Federal. Financia o auxílio de R$ 60 bilhões da Lei Complementar nº 173, de 27/05/2020 (menor que o crédito, por isso não entra como item próprio); a mesma lei complementar suspendeu dívidas de estados e municípios com a União, sem valor no texto.

### 2020.5 Compensação aos estados pelas perdas da Lei Kandir, de 2020 a 2037 (Lei Complementar nº 176)
- Ato ou registro: Lei Complementar 176, 2020-12-29: https://legis.senado.leg.br/norma/33037478
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Marcelo Pacheco dos Guaranys
- Valor: Lei Complementar nº 176/2020, art. 1º (Diário Oficial da União, edição extra de 29/12/2020; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/33037478/publicacao/33039279
- Trecho: "Art. 1º A União entregará aos Estados, ao Distrito Federal e aos Municípios, no período de 2020 a 2037, o montante de R$ 58.000.000.000,00 (cinquenta e oito bilhões de reais), assim escalonado:"
- Situação: Lei complementar em vigor. A mesma lei prevê R$ 4 bilhões adicionais, pagos com a receita dos blocos de Atapu e Sépia; o Resultado do Tesouro Nacional registra esses repasses na linha "Lei Kandir (LC nº 87/96 e 102/00) e LC nº 176 de 2020".

### 2020.6 Crédito extraordinário de R$ 51,6 bilhões para o Benefício Emergencial de Manutenção do Emprego e da Renda (Medida Provisória nº 935)
- Ato ou registro: Medida Provisória 935, 2020-04-01: https://legis.senado.leg.br/norma/32040121
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 935/2020, art. 1º (Diário Oficial da União de 01/04/2020; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/32040121/publicacao/32041153
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Economia, no valor de R$ 51.641.629.500,00 (cinquenta e um bilhões seiscentos e quarenta e um milhões seiscentos e vinte e nove mil e quinhentos reais)"
- Situação: Perdeu a eficácia em 30/07/2020, segundo o Senado Federal. Financia o programa criado pela Medida Provisória nº 936, de 01/04/2020, cuja exposição de motivos estima o custo em R$ 51,2 bilhões (menor, por isso não entra como item próprio).

### 2020.7 Programa Emergencial de Suporte a Empregos: R$ 34 bilhões da União para financiar folhas de pagamento (Medida Provisória nº 944)
- Ato ou registro: Medida Provisória 944, 2020-04-03: https://legis.senado.leg.br/norma/32052949
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia); Roberto de Oliveira Campos Neto (Presidente do Banco Central do Brasil)
- Valor: Medida Provisória nº 944/2020, art. 8º (Diário Oficial da União, edição extra de 03/04/2020; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/32052949/publicacao/32056423
- Trecho: "Art. 8º Ficam transferidos, da União para o BNDES, R$ 34.000.000.000,00 (trinta e quatro bilhões de reais), destinados à execução do Pr ograma Emergencial de Suporte a Empregos."
- Situação: Convertida, com mudanças, na Lei nº 14.043, de 19/08/2020, que reduziu a transferência ao BNDES para até R$ 17 bilhões e destinou R$ 12 bilhões ao FGO do Pronampe. O crédito extraordinário da Medida Provisória nº 943, de 03/04/2020 (R$ 34 bilhões), financia a transferência e não entra de novo. Pelo Resultado do Tesouro Nacional, a União aportou R$ 14,4 bilhões no programa em agosto de 2020 (valor a preços de agosto de 2021).

### 2020.8 Pagamento concentrado de sentenças judiciais e precatórios em junho de 2020
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 26, N. 6 (junho de 2020), 2020-07-30: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2020/6
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de junho de 2020, Tabela 3.1 (R$ milhões, preços correntes, coluna junho de 2020), soma das cinco linhas de sentenças judiciais e precatórios (benefícios previdenciários urbano e rural, pessoal, BPC e custeio e capital). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/33778_1059996/relatorio_jun20.pdf
- Trecho: "Benefícios Previdenciários, Urbano: d/q Sentenças Judiciais e Precatórios 7.264,2; Rural: d/q Sentenças Judiciais e Precatórios 1.640,9; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 3.735,2; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 281,0; IV.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 20.173,6. Nota 17 do mês: aumento explicado pela alteração do cronograma de pagamentos de precatórios, historicamente efetuados em meses anteriores."
- Situação: Pago em junho de 2020. O valor inclui as requisições de pequeno valor pagas no mês. Em 2019 a concentração tinha ocorrido em março; o Tesouro atribui a mudança ao novo cronograma de pagamentos.

### 2020.9 Crédito extraordinário de R$ 29,1 bilhões para o auxílio emergencial e despesas da pandemia (Medida Provisória nº 970)
- Ato ou registro: Medida Provisória 970, 2020-05-26: https://legis.senado.leg.br/norma/32208233
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 970/2020, art. 1º (Diário Oficial da União de 26/05/2020; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/32208233/publicacao/32208857
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor dos Ministérios da Saúde e da Cidadania, no valor de R$ 29.058.260.654,00 (vinte e nove bilhões cinquenta e oito milhões duzentos e sessenta mil seiscentos e cinquenta e quatro reais)"
- Situação: Perdeu a eficácia em 22/09/2020, segundo o Senado Federal. Pelo anexo, R$ 28,72 bilhões vão para o auxílio emergencial. Financia o auxílio emergencial criado pela Lei nº 13.982, de 02/04/2020 (lei do Congresso, sem valor no texto), prorrogado depois por decreto; cada crédito é uma parcela própria de dinheiro e entra como item.

### 2020.10 Crédito extraordinário de R$ 25,7 bilhões para o auxílio emergencial (Medida Provisória nº 956)
- Ato ou registro: Medida Provisória 956, 2020-04-24: https://legis.senado.leg.br/norma/32129896
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 956/2020, art. 1º (Diário Oficial da União de 24/04/2020; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/32129896/publicacao/32131201
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Cidadania, no valor de R$ 25.720.000.000,00 (vinte e cinco bilhões setecentos e vinte milhões de reais)"
- Situação: Perdeu a eficácia em 21/09/2020, segundo o Senado Federal. Financia o auxílio emergencial criado pela Lei nº 13.982, de 02/04/2020 (lei do Congresso, sem valor no texto), prorrogado depois por decreto; cada crédito é uma parcela própria de dinheiro e entra como item.

### Ficaram de fora em 2020
- **Créditos do mesmo programa de um item listado (fica o de maior valor):** MP 999 (R$ 67,6 bi, auxílio residual da MP
  1.000); MP 943 (R$ 34 bi, PESE da MP 944); MP 936 (BEm; EXM: "custo estimado é de R$ 51,2 bilhões", menor que o crédito
  da MP 935); Lei Complementar 173 (R$ 60 bi, financiada pela MP 978); MP 938 e MP 939 (apoio ao FPE e ao FPM, R$ 16 bi
  cada, abaixo do corte); MP 975 e MP 977 (FGI do Peac, R$ 20 bi cada, abaixo do corte).
- **Abaixo do 10º lugar (R$ 25,7 bi):** MP 1.015 (R$ 20 bi, vacinas e saúde); MP 972 (R$ 15,9 bi ao FGO do Pronampe); MP 997 (R$ 12 bi); MP 1.020 (R$ 10,2 bi); MPs 969 e 1.002 (R$ 10 bi cada).
- **Leis de conversão com valor diferente:** Lei 14.043 (conversão da MP 944, até R$ 17 bi ao BNDES e R$ 12 bi ao FGO do
  Pronampe), dita na situação do item da MP 944; Lei 14.041 (conversão da MP 938).
- **Fundo Especial de Financiamento de Campanha de 2020:** pago em parcelas a partir de julho de 2020 (R$ 36,56 mi em
  julho no RTN), total abaixo do corte.
- **Lei 13.982 (auxílio emergencial):** sem valor no texto; os créditos que o financiaram entram como itens.

### Não confirmado (2020)
- Cargo de Marcelo Pacheco dos Guaranys (LC 176) não confirmado; fica `null`. Onyx Lorenzoni: "Ministro de Estado da
  Cidadania" pela EM nº 30/2020 MCID que assinou; Roberto Campos Neto: "Presidente do Banco Central do Brasil" pela EMI nº
  8/2020 BACEN ME (primeiro signatário, primeiro órgão).


## 2019 (ano completo)

| # | Movimento | Data | Valor oficial | Tipo | Natureza |
|---|---|---|---|---|---|
| 1 | Pagamento à Petrobras pela revisão do contrato da cessão onerosa, em dezembro de 2019 | 2019-12 | R$ 34,4 bi | gasto | pago |
| 2 | Reestruturação da carreira e do sistema de proteção social dos militares (Lei nº 13.954) | 2019-12-17 | R$ 21,16 bi | gasto | estimativa |
| 3 | Pagamento concentrado de sentenças judiciais e precatórios em abril de 2019 | 2019-04 | R$ 13,905 bi | gasto | pago |
| 4 | Pagamento concentrado de sentenças judiciais e precatórios em março de 2019 | 2019-03 | R$ 12,291 bi | gasto | pago |
| 5 | Repasse a estados e municípios de parte do leilão dos excedentes da cessão onerosa, em dezembro de 2019 | 2019-12 | R$ 11,7 bi | gasto | pago |
| 6 | Aumento de capital de empresas estatais não dependentes, em dezembro de 2019 | 2019-12 | R$ 9,595 bi | gasto | pago |
| 7 | Repasse adicional de R$ 4 bilhões a estados ligado aos blocos de Atapu e Sépia (Lei nº 13.885) | 2019-10-17 | R$ 4 bi | gasto | teto |
| 8 | Reembolso de combustíveis a distribuidoras de energia pela CDE, até R$ 3,5 bilhões (Medida Provisória nº 879) | 2019-04-24 | R$ 3,5 bi | gasto | teto |
| 9 | Parcela de dezembro de 2019 do Bolsa Família paga em dobro (Medida Provisória nº 898) | 2019-10-16 | R$ 2,58 bi | gasto | estimativa |
| 10 | Crédito extraordinário para o acolhimento de refugiados da Venezuela (Medida Provisória nº 880) | 2019-04-30 | R$ 223,9 mi | crédito extraordinário | teto |

### 2019.1 Pagamento à Petrobras pela revisão do contrato da cessão onerosa, em dezembro de 2019
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 25, N. 12 (dezembro de 2019), 2020-01-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2019/12
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2019, Nota 13 do mês (valor arredondado pelo Tesouro). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/31547_1016534/relatorio_dez19.pdf
- Trecho: "explicado principalmente pelo pagamento à Petrobras decorrente da revisão do contrato de cessão onerosa (R$ 34,4 bilhões em dez/19)"
- Situação: Pago em dezembro de 2019. Na tabela do teto de gastos do mesmo boletim, a linha "IV.5 Cessão Onerosa" soma R$ 46.144,43 milhões em dezembro de 2019, juntando este pagamento e o repasse do bônus a estados e municípios (item próprio).

### 2019.2 Reestruturação da carreira e do sistema de proteção social dos militares (Lei nº 13.954)
- Ato ou registro: Lei 13.954, 2019-12-17: https://legis.senado.leg.br/norma/31836233
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Fernando Azevedo e Silva; Paulo Guedes (Ministro de Estado da Economia)
- Valor: Exposição de Motivos Interministerial nº 61/2019 MD ME do Projeto de Lei nº 1.645/2019, itens 18 e 19, assinada por Fernando Azevedo e Silva e Paulo Guedes (Planalto, cópia do Internet Archive); total de despesas de 2020 a 2022 no quadro. Fonte lida: https://web.archive.org/web/20260614201323/https://www.planalto.gov.br/ccivil_03/projetos/ato_2019_2022/2019/pl/exm/exm-00061-md-me.htm
- Trecho: "A elevação estimada das despesas com pessoal, decorrentes da alteração do Sistema de Proteção Social dos Militares das Forças Armadas e da reestruturação da carreira, alcançarão os seguintes montantes: [...] ANO TOTAL DE DESPESAS TOTAL DE RECEITAS RESULTADO RECEITA X DESPESAS 2020 4,73 5,49 0,76 2021 7,06 7,87 0,81 2022 9,37 10,09 0,72 TOTAL 21,16 23,45 2,29"
- Situação: Lei em vigor (Diário Oficial da União de 17/12/2019). A estimativa é do projeto enviado pelo Executivo; a estimativa sobre o texto aprovado não foi lida. A mesma exposição de motivos estima R$ 23,45 bilhões de receitas e economias no período, com as novas contribuições dos militares.

### 2019.3 Pagamento concentrado de sentenças judiciais e precatórios em abril de 2019
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 25, N. 4 (abril de 2019), 2019-05-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2019/4
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de abril de 2019, Tabela 3.1 (R$ milhões, preços correntes, coluna abril de 2019), soma das cinco linhas de sentenças judiciais e precatórios (benefícios previdenciários urbano e rural, pessoal, BPC e custeio e capital). Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/29904_993167/Nimabr2019.pdf
- Trecho: "Benefícios Previdenciários, Urbano: d/q Sentenças Judiciais e Precatórios 738,4; Rural: d/q Sentenças Judiciais e Precatórios 196,0; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 468,3; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 86,2; IV.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 12.415,8. Nota 13 do mês: em abril ocorre, conforme calendário estabelecido pelo Conselho de Justiça Federal, concentração de maior parte dos pagamentos de Sentenças Judiciais e Precatórios (Custeio e Capital)."
- Situação: Pago em abril de 2019. O valor inclui as requisições de pequeno valor pagas no mês. Em 2019 a concentração se dividiu: precatórios de benefícios e de pessoal em março (item próprio), os de custeio e capital em abril.

### 2019.4 Pagamento concentrado de sentenças judiciais e precatórios em março de 2019
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 25, N. 3 (março de 2019), 2019-04-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2019/3
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de março de 2019, Tabela 3.1 (R$ milhões, preços correntes, coluna março de 2019), soma das cinco linhas de sentenças judiciais e precatórios; a concentração em março é dita no Resultado do Tesouro Nacional de março de 2020, Nota 7. Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/29719_950722/nimmar2019.pdf
- Trecho: "Benefícios Previdenciários, Urbano: d/q Sentenças Judiciais e Precatórios 5.629,4; Rural: d/q Sentenças Judiciais e Precatórios 1.488,2; Pessoal e Encargos Sociais: d/q Sentenças Judiciais e Precatórios 3.943,3; BPC da LOAS/RMV: d/q Sentenças Judiciais e Precatórios 233,8; IV.3.14 Sentenças Judiciais e Precatórios (Custeio e Capital) 996,2. RTN de março de 2020, Nota 7: Em março 2019, houve concentração de pagamentos de R$ 7,4 bilhões (em valores de mar/20) em sentenças judiciais e precatórios relativos à benefícios previdenciários sem contrapartida em março de 2020."
- Situação: Pago em março de 2019. O valor inclui as requisições de pequeno valor pagas no mês. O Tesouro registra no boletim de março de 2020 a concentração de março de 2019: R$ 7,4 bilhões em benefícios previdenciários e R$ 4,1 bilhões em pessoal, a preços de março de 2020.

### 2019.5 Repasse a estados e municípios de parte do leilão dos excedentes da cessão onerosa, em dezembro de 2019
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 25, N. 12 (dezembro de 2019), 2020-01-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2019/12
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2019, Nota 15 do acumulado (valor arredondado pelo Tesouro); linha II.6 Demais transferências de dezembro de 2019: R$ 11.885,9 milhões. Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/31547_1016534/relatorio_dez19.pdf
- Trecho: "aumento explicado principalmente pela transferência de parte dos valores arrecadados com os leilões dos volumes excedentes de petróleo (cessão onerosa), no montante de R$ 11,7 bilhões."
- Situação: Pago em dezembro de 2019, pelos critérios da Lei nº 13.885, de 17/10/2019. A linha do Tesouro em que o repasse aparece (II.6 Demais, R$ 11.885,9 milhões em dezembro de 2019) inclui outras transferências pequenas (R$ 130,5 milhões em dezembro de 2018).

### 2019.6 Aumento de capital de empresas estatais não dependentes, em dezembro de 2019
- Ato ou registro: Boletim Resultado do Tesouro Nacional Vol. 25, N. 12 (dezembro de 2019), 2020-01-29: https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2019/12
- Assinaram: registro de pagamento
- Valor: Secretaria do Tesouro Nacional, Resultado do Tesouro Nacional de dezembro de 2019, tabela do teto de gastos, linha IV.4 (R$ milhões, coluna dezembro de 2019); destaque no Resultado do Tesouro Nacional de dezembro de 2020, Nota 12. Fonte lida: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/31547_1016534/relatorio_dez19.pdf
- Trecho: "IV.4 Despesas com aumento de capital de empresas estatais não dependentes (Inciso IV do § 6º) 2.149,13 9.594,74 (dezembro de 2018, dezembro de 2019). RTN de dezembro de 2020, Nota 12: aumento de capital de empresas estatais não dependentes (R$ 9,6 bilhões em dez/19)"
- Situação: Pago em dezembro de 2019. O boletim não diz quais empresas receberam o aumento de capital; é uma linha que pode juntar mais de uma estatal.

### 2019.7 Repasse adicional de R$ 4 bilhões a estados ligado aos blocos de Atapu e Sépia (Lei nº 13.885)
- Ato ou registro: Lei 13.885, 2019-10-17: https://legis.senado.leg.br/norma/31591283
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia); Bento Albuquerque (Ministro de Estado de Minas e Energia)
- Valor: Lei nº 13.885/2019, art. 1º, § 4º (Diário Oficial da União, edição extra de 17/10/2019; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/31591283/publicacao/31598014
- Trecho: "§ 4º Dos valores arrecadados na forma do caput deste artigo referentes aos Blocos de Atapu e Sépia, descontada a despesa decorrente da revisão do contrato de cessão onerosa, a União entregará, adicionalmente em relação ao disposto nos incisos I, II e III do caput deste artigo, R$ 4.000.000.000,00 (quatro bilhões de reais)"
- Situação: Lei em vigor; o repasse depende da arrecadação dos leilões dos blocos de Atapu e Sépia. A Lei Complementar nº 176/2020 repetiu o mesmo valor (não entra de novo). O texto do Senado grafa um dos signatários como "Paulo Gudes".

### 2019.8 Reembolso de combustíveis a distribuidoras de energia pela CDE, até R$ 3,5 bilhões (Medida Provisória nº 879)
- Ato ou registro: Medida Provisória 879, 2019-04-24: https://legis.senado.leg.br/norma/30917379
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia); Bento Albuquerque (Ministro de Estado de Minas e Energia)
- Valor: Medida Provisória nº 879/2019, § 1º-B do art. 13 da Lei nº 10.438/2002 na redação dada pela medida (Diário Oficial da União, edição extra de 24/04/2019; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/30917379/publicacao/30917415
- Trecho: "§ 1º-B. O pagamento de que trata o inciso IX do caput é limitado a R$ 3.500.000.000,00 (três bilhões e quinhentos milhões de reais) até o exercício de 2021, sujeito à disponibilidade orçamentária e financeira."
- Situação: Rejeitada pelo Plenário da Câmara dos Deputados em 20/08/2019, segundo o Senado Federal.

### 2019.9 Parcela de dezembro de 2019 do Bolsa Família paga em dobro (Medida Provisória nº 898)
- Ato ou registro: Medida Provisória 898, 2019-10-16: https://legis.senado.leg.br/norma/31582218
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia); Osmar Terra (Ministro de Estado da Cidadania)
- Valor: Exposição de Motivos Interministerial nº 72/2019 MCID ME da Medida Provisória nº 898/2019, item 11 (Planalto, cópia do Internet Archive). Fonte lida: https://web.archive.org/web/20260119153619/http://planalto.gov.br/CCIVIL_03/_Ato2019-2022/2019/Exm/Exm-MP-898-19.pdf
- Trecho: "estima-se que deverão ser adicionados R$ 2,58 bilhões reais na ação 8442"
- Situação: Perdeu a eficácia em 26/03/2020, segundo o Senado Federal.

### 2019.10 Crédito extraordinário para o acolhimento de refugiados da Venezuela (Medida Provisória nº 880)
- Ato ou registro: Medida Provisória 880, 2019-04-30: https://legis.senado.leg.br/norma/30921791
- Assinaram: Jair Messias Bolsonaro (Presidente da República); Paulo Guedes (Ministro de Estado da Economia)
- Valor: Medida Provisória nº 880/2019, art. 1º (Diário Oficial da União de 30/04/2019; texto oficial no Senado Federal). Fonte lida: https://legis.senado.leg.br/norma/30921791/publicacao/30921806
- Trecho: "Art. 1º Fica aberto crédito extraordinário, em favor do Ministério da Defesa, no valor de R$ 223.853.000,00 (duzentos e vinte e três milhões, oitocentos e cinquenta e três mil reais)"
- Situação: Perdeu a eficácia em 29/08/2019, segundo o Senado Federal. Finalidade segundo a descrição da matéria no Senado: refugiados da Venezuela.

### Ficaram de fora em 2019
- **Lei 13.843 (crédito suplementar de R$ 248,9 bi para cumprir a regra de ouro):** lei de crédito suplementar, que
  redistribui o orçamento aprovado; não entra pela regra.
- **MP 905 (Contrato Verde e Amarelo):** a exposição de motivos diz que a Receita Federal estimou o custo da desoneração "nos
  termos da Tabela 1", mas a tabela não aparece no texto lido (é imagem); valor não confirmado.
- **MP 916 (salário mínimo de 2020):** a exposição de motivos traz o custo de cada R$ 1 de aumento (R$ 355,5 mi em 2020),
  sem custo total.
- **MP 889 (saques do FGTS e do PIS/Pasep):** dinheiro dos trabalhadores, não da União.
- **MP 904 (extinção do DPVAT) e MP 899 (transação tributária):** entradas de dinheiro na União; ficam para a coluna de
  receitas.
- **Poucos atos de gasto com valor em 2019:** os créditos extraordinários do ano foram pequenos; por isso o último lugar
  da lista é de R$ 224 mi (MP 880); a MP 911 (R$ 131,7 mi, auxílio a pescadores atingidos pelas manchas de óleo) fica em
  11º.

### Não confirmado (2019)
- Projetos de lei do Executivo de 2018: o índice do Internet Archive não devolveu exposições de motivos desses projetos;
  leis de 2019 nascidas de projetos de 2018 podem ter estimativa não lida. Das exposições de motivos de projetos de 2019,
  só 20 estavam arquivadas e foram lidas.
- Cargo de Fernando Azevedo e Silva em 17/12/2019 (a exposição de motivos que o identifica como Ministro da Defesa é de
  20/03/2019, fora da janela de seis meses); fica `null`.
- Quais empresas receberam o aumento de capital de dezembro de 2019 (o boletim não detalha).


## Não confirmado (todos os anos)

- **Acesso às fontes:** `in.gov.br`, `planalto.gov.br` e `camara.leg.br` não responderam desta máquina em 2026-10-04 e
  2026-10-05. Nenhum valor veio dessas páginas diretamente: os textos dos atos foram lidos no sistema de Legislação Federal
  do Senado e as exposições de motivos em cópias do Internet Archive do Planalto. Onde a cópia não existia, o valor não
  foi usado.
- **Exposições de motivos de projetos de lei:** só as arquivadas pelo Internet Archive foram lidas (2019: 20; 2020: 37;
  2021: 51; 2022: 49; 2023: 22; 2024: 75; 2025: 52; 2026: 2). Leis nascidas de projetos do Executivo cuja exposição de
  motivos não está arquivada podem ter estimativa oficial não lida. As estimativas usadas (Lei 15.270, LC 214, Lei 15.367,
  Lei 13.954) são dos textos enviados, não dos aprovados.
- **MP 1.368/2026:** finalidade pela descrição da matéria no Senado; o anexo não tem texto no Senado.
- **MP 905/2019:** custo da desoneração em tabela de imagem, não lida.
- **Aumento de capital de estatais de dezembro de 2019:** o boletim não diz quais empresas.
- **Cargos `null`:** listados em cada ano; regra de confirmação no início deste documento.
- **Dois valores arredondados pelo Tesouro** (pagamento à Petrobras de R$ 34,4 bi em 2019; repasses do bônus da cessão
  onerosa de R$ 11,7 bi em 2019 e R$ 7,7 bi em 2022) usam o número escrito na nota do boletim; as linhas das tabelas
  juntam outros valores e estão citadas na situação de cada item.

## Pontos para o agente principal

- **Mesmo teto contado duas vezes em 2026:** `recent.json` lista a Lei 15.503 (R$ 30 bi) e a Lei 15.473 (R$ 15 bi), que
  repetem os tetos das MPs 1.359 e 1.345 listadas aqui (janeiro a junho). Somar as duas colunas no ano de 2026 conta esses
  tetos duas vezes; escolher um lado (a regra deste arquivo fica com a medida provisória).
- **MP 1.374/2026 (DOU de 01/07/2026, até R$ 10 bi do FNDCT para crédito rural via Finep):** cai na janela de
  `recent.json`, que não a lista como item próprio (lista a MP 1.377, cujo crédito inclui R$ 9 bi para essa linha). Pela
  regra de maior valor, a MP 1.374 (R$ 10 bi) seria o item e a parte de R$ 9 bi da MP 1.377 ficaria na situação.
- **Precatórios:** o valor de cada pagamento concentrado é a soma de cinco linhas da Tabela 3.1 do boletim (benefícios
  urbanos e rurais, pessoal, BPC e custeio e capital) no mês, e inclui as requisições de pequeno valor pagas no mês. O
  Tesouro não publica um total único; as linhas estão no campo `quote`.
- **Programa social inteiro:** o Bolsa Família de 2023 (MP 1.164, R$ 176,5 bi) entra pelo orçamento do programa no ano,
  como manda a regra (valor da exposição de motivos); a maior parte já estava na lei orçamentária para o Auxílio Brasil,
  que ele substituiu, e a situação do item diz isso.
