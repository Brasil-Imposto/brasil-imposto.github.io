# Recentes: maiores decisões fiscais federais publicadas no DOU (2026-07-01 a 2026-10-02)

Pesquisa para o componente "Recentes" da home (D64). Coletado em 2026-10-02. Saída de dados: `data/home/recent.json`
(8 itens, em ordem de valor). Toda frase de valor abaixo foi lida na página primária (DOU em in.gov.br, Planalto ou
Exposição de Motivos em PDF do Planalto); o que não foi aberto está marcado "não confirmado".

## Critério

- **Universo:** atos federais (lei, lei complementar, medida provisória) publicados no Diário Oficial da União de
  01/07/2026 a 02/10/2026. Varredura completa da lista de MPs de 2026 (API da Câmara, MPs 1.374 a 1.394) e da lista de
  leis e leis complementares de 2026 (API de legislação do Senado, Leis 15.453 a 15.526 e LCs 233 a 237).
- **Entra:** ato que fixa no próprio texto, ou na exposição de motivos oficial, um valor em reais de gasto, empréstimo
  com recursos da União, renúncia ou perda de receita, renegociação de dívidas, garantia, crédito extraordinário ou
  receita. Qualquer lado político; não há filtro de autor.
- **Ordem:** maior valor oficial primeiro; empate desfeito pela data mais recente.
- **Leis de conversão:** entram quando o valor está no texto publicado no período, com a origem do valor dita no campo
  `status` (Lei 15.503 herda o teto da MP 1.359, de maio; Lei 15.473 herda o da MP 1.345, de março). Se o componente
  quiser só "valor novo no período", basta retirar esses dois itens: a lista continua válida.
- **Sem dupla contagem:** crédito extraordinário que só financia um teto já listado não entra de novo (MP 1.387, R$ 7 bi,
  é parte do teto da MP 1.379).
- **Natureza do valor:** quase todos são tetos autorizados (`cap`) ou estimativas oficiais (`estimated_cost`); nenhum é
  valor pago. A interface deve dizer "até" ou "estimativa".

## Os 8 itens (ordem de valor)

| # | Ato | DOU | Valor oficial | Tipo | Natureza |
|---|---|---|---|---|---|
| 1 | Lei 15.503 (motoristas de aplicativo e taxistas) | 14/09 extra A | até R$ 30 bi | empréstimo (spending) | teto |
| 2 | MP 1.393 (Desenrola Brasil 3.0) | 25/09 extra A | até R$ 15 bi | renegociação | teto |
| 3 | Lei 15.473 (Plano Brasil Soberano, crédito à exportação) | 22/07 extra | até R$ 15 bi | empréstimo (spending) | teto |
| 4 | MP 1.379 (ampliação do crédito à exportação) | 22/07 extra B | até R$ 13,5 bi | empréstimo (spending) | teto |
| 5 | MP 1.377 (Finep rural, Desenrola Adimplentes, Fies) | 16/07 extra C | R$ 13,285 bi | crédito extraordinário | teto |
| 6 | MP 1.394 (proibição das bets) | 25/09 | R$ 12,021 bi (2026 a 2028) | perda de receita | estimativa |
| 7 | MP 1.389 (subvenção a diesel e gasolina) | 09/09 | R$ 6,605 bi | crédito extraordinário | teto |
| 8 | LC 235 (créditos fiscais a fertilizantes) | 28/08 | até R$ 5 bi (2027 a 2031) | renúncia | teto |

### 1. Lei nº 15.503, de 14/09/2026 (conversão da MP 1.366)
- DOU: https://www.in.gov.br/web/dou/-/lei-n-15.503-de-14-de-setembro-de-2026-731640068
- Assinaram: Luiz Inácio Lula da Silva, Frederico de Siqueira Filho, Dario Carnevalli Durigan, Paulo Henrique Rodrigues
  Pereira, Márcio Fernando Elias Rosa, Luiz Marinho, George André Palermo Santoro, Guilherme Castro Boulos.
- Valor, art. 6º: "Observada a disponibilidade orçamentária e financeira, fica a União autorizada a destinar o valor de
  até R$ 30.000.000.000,00 (trinta bilhões de reais) para disponibilizar linhas de financiamento reembolsável a
  profissionais de transporte remunerado privado individual de passageiros, taxistas e cooperativas de taxistas". Gestor:
  Ministério da Fazenda; agente financeiro: BNDES (§ 2º). Sem veto no artigo (texto do Planalto sem marca de veto).
- Origem: o mesmo teto estava no art. 2º da MP nº 1.359, de 19/05/2026 (assinada por Lula, Rogério Ceron de Oliveira e
  Márcio Elias Rosa), que esta lei revogou. A MP 1.366 não tinha valor.
- Regulamentação no DOU de 15/09: Resolução CMN nº 5.341 e Portaria Interministerial MDIC/MF nº 199 (só títulos lidos).

### 2. Desenrola Brasil 3.0 (MP nº 1.393, de 25/09/2026)
- DOU: https://www.in.gov.br/web/dou/-/medida-provisoria-n-1.393-de-25-de-setembro-de-2026-734808387
- Assinaram: Luiz Inácio Lula da Silva, Dario Carnevalli Durigan, Wellington César Lima e Silva (assinaturas conferidas
  no DOU).
- Valor, novo art. 31-E da Lei 14.690/2023: "As despesas decorrentes da aquisição, pela União, de carteiras de créditos
  inadimplidos ou de eventual integralização de cotas em fundo correrão à conta de dotações orçamentárias consignadas ao
  Ministério da Fazenda, observado o limite máximo de R$ 15.000.000.000,00 (quinze bilhões de reais)." A EXM nº 2116/2026,
  assinada pelo ministro da Fazenda, repete o teto (item 8). O texto fixa deságio mínimo de 90% sobre o valor de face e
  duração até 30/06/2028.
- Situação: em vigor; aguarda o Congresso (comissão mista em constituição em 01/10, segundo a API da Câmara).

### 3. Lei nº 15.473, de 22/07/2026 (conversão da MP 1.345, de 24/03/2026)
- DOU: https://www.in.gov.br/web/dou/-/lei-n-15.473-de-22-de-julho-de-2026-720797394
- Assinaram: Luiz Inácio Lula da Silva, André Carlos Alves de Paula Filho, Dario Carnevalli Durigan, Márcio Fernando Elias
  Rosa, Rivetla Edipo Araujo Cruz.
- Valor, art. 3º, § 1º: "As linhas de financiamento de que trata o caput deste artigo serão concedidas com a utilização de
  até R$ 15.000.000.000,00 (quinze bilhões de reais)", com superávit do Fundo de Garantia à Exportação e outras fontes.
- Origem: o teto de R$ 15 bi já estava na MP 1.345, de março.

### 4. MP nº 1.379, de 22/07/2026
- DOU: https://www.in.gov.br/web/dou/-/medida-provisoria-n-1.379-de-22-de-julho-de-2026-720797644
- Assinaram: Luiz Inácio Lula da Silva, Dario Carnevalli Durigan, Márcio Fernando Elias Rosa.
- Valor, novo § 1º-A do art. 3º da Lei 15.473: "O limite de que trata o § 1º poderá ser ampliado em até R$
  13.500.000.000,00 (treze bilhões e quinhentos milhões de reais) [...] em adição ao montante previsto no § 1º".
- Relacionado: MP 1.387 (DOU 25/08, R$ 7 bi, Lula e Bruno Moretti) abriu crédito para essas linhas; EXM nº 1903/2026
  confirma que o crédito se destina "à ampliação das linhas de financiamento autorizadas pelo art. 3º, § 1º-A".
- Situação: prazo no Congresso prorrogado até 18/11/2026 (API da Câmara).

### 5. MP nº 1.377, de 16/07/2026
- DOU: https://www.in.gov.br/web/dou/-/medida-provisoria-n-1.377-de-16-de-julho-de-2026-719582266
- Assinaram: Luiz Inácio Lula da Silva, Guilherme Santos Mello (a EXM nº 1661/2026 o identifica como "Ministro de Estado do
  Planejamento e Orçamento substituto").
- Valor: "no valor de R$ 13.285.000.000,00". Composição pela EXM: R$ 9 bi Finep/FNDCT a produtores rurais (MP 1.374),
  R$ 3 bi Desenrola Adimplentes e R$ 1 bi Fies Empreendedor (MP 1.373), R$ 270 mi cana do Nordeste, R$ 15 mi Corte IDH.
- Situação: prazo prorrogado até 12/11/2026. A Agência Câmara noticia aprovação na Comissão Mista de Orçamento (só o
  título foi visto; não confirmado).

### 6. MP nº 1.394, de 25/09/2026 (proibição das apostas de quota fixa)
- DOU: https://www.in.gov.br/web/dou/-/medida-provisoria-n-1.394-de-25-de-setembro-de-2026-734808521
- Assinaram: Luiz Inácio Lula da Silva, Dario Carnevalli Durigan, Wellington César Lima e Silva.
- Valor, EXM da MP (Planalto, item 12): "implica redução de receitas tributárias na ordem R$ 1.541 bilhões para o ano de
  2026, R$ 5.150 bilhões para o ano de 2027 e R$ 5.330 bilhões para o ano de 2028", mais R$ 268,8 milhões de taxa de
  fiscalização no triênio. ⚠️ A EXM usa ponto como separador decimal ("R$ 1.541 bilhões"); lido como R$ 1,541 bi, coerente
  com a ordem de grandeza dos outros anos. Soma usada: R$ 12,021 bi (só tributos).
- Classificado como `revenue_waiver` por falta de tipo melhor: não é benefício fiscal, é receita que deixa de existir. O
  resumo do item diz isso. Se o componente ganhar um tipo `revenue_loss`, este item deve migrar.
- Única peça do lado da receita com valor oficial no período.

### 7. MP nº 1.389, de 08/09/2026 (DOU 09/09)
- DOU: https://www.in.gov.br/web/dou/-/medida-provisoria-n-1.389-de-8-de-setembro-de-2026-730725609
- Assinaram: Luiz Inácio Lula da Silva, Bruno Moretti (Ministro de Estado do Planejamento e Orçamento, conforme assinatura
  da EXM nº 1903/2026 e do Decreto de 26/06/2026 da Ordem do Mérito da Defesa).
- Valor: R$ 6.605.000.000,00; EXM nº 1999/2026: R$ 5,607 bi subvenção ao diesel (MP 1.363) e R$ 998 mi à gasolina (MP 1.358).
- Série no período, mesmo fim: MP 1.380 (R$ 3,33 bi), 1.381 (R$ 3,473 bi), 1.388 (R$ 3,152 bi) e 1.389 = R$ 16,56 bi.

### 8. Lei Complementar nº 235, de 27/08/2026 (DOU 28/08)
- DOU: https://www.in.gov.br/web/dou/-/lei-complementar-n-235-de-27-de-agosto-de-2026-728568253
- Assinaram: Luiz Inácio Lula da Silva, André Carlos Alves de Paula Filho, Dario Carnevalli Durigan, Bruno Moretti,
  Thairyne Jéssica Martins de Oliveira (Ministra de Estado de Portos e Aeroportos substituta, Portaria de Pessoal nº 177,
  DOU 31/08/2026).
- Valor, art. 7º, § 1º: créditos fiscais limitados a R$ 1 bi por ano de 2027 a 2031 (total R$ 5 bi); § 11 permite ampliar
  cada limite anual em até R$ 1 bi. Na mesma lei: subvenção ao etanol hidratado limitada a R$ 1,2 bi, compensação de
  créditos de etanol limitada a R$ 750 mi em 2026, isenção de AFRMM limitada a R$ 1 bi.

### Ficaram de fora (abaixo do corte ou sem número total)
- Lei 15.506 (16/09, minerais críticos): créditos fiscais de R$ 1 bi por ano de 2030 a 2034 (R$ 5 bi) e cota da União
  no FGAM até R$ 2 bi. Empata com a LC 235 em R$ 5 bi; ficou fora porque vários cargos de quem assinou não foram
  confirmados (Cleber Oliveira Soares, José Múcio Monteiro Filho, Fernanda Machiaveli Morão de Oliveira, Antônio Waldez
  Góes da Silva). DOU: https://www.in.gov.br/web/dou/-/lei-n-15.506-de-16-de-setembro-de-2026-732159558
- MP 1.387 (R$ 7 bi): parte do teto da MP 1.379, ver item 4.
- MP 1.385 (13/08, R$ 3,5 bi: FGI R$ 2 bi, FGO R$ 750 mi, FGHab R$ 750 mi; Lula e Moretti). MP 1.382 autoriza esses aportes.
- MP 1.391 (11/09): subvenção ao diesel "estimada em R$ 492,08 milhões por mês" (EXM nº 2037/2026), sem total.
- MP 1.376 (15/07): renegociação de dívidas rurais; equalização estimada em R$ 48,29 mi em 2026, sem total.
- Lei 15.525 (CSLL de resseguradoras), Lei 15.504 (Redata) e LC 237: sem valor no texto.
- MP 1.373 (Desenrola Adimplentes): DOU de 29/06/2026, fora da janela.

## Receitas grandes no período
- Nenhum ato de receita grande com valor oficial foi publicado na janela. Leilões: a sessão de ofertas do 4º Ciclo da
  Oferta Permanente de Partilha e do 6º Ciclo da Oferta Permanente de Concessão (ANP) está marcada para **07/10/2026**,
  depois do corte (Comunicados da CEL, DOU 15/09 e 25/09). Concessões, dividendos extraordinários e leilões da PPSA: nada
  com valor no DOU encontrado pela busca. Não foi feita varredura exaustiva de portarias e resoluções de agências; é
  possível haver ato menor não encontrado.
- O único item do lado da receita é a perda estimada com a proibição das bets (item 6).

## Os "até R$ 200 bi" do Desenrola
**Não há fonte oficial para R$ 200 bi.** Foi lido: texto da MP 1.393 no DOU, EXM nº 2116/2026, Agência Câmara de
Notícias e Agência Senado. O que as fontes oficiais dizem:
- MP 1.393 e EXM: teto de **R$ 15 bi** de despesa da União; deságio mínimo de 90% sobre o valor de face.
- Agência Câmara, 28/09/2026 (https://www.camara.leg.br/noticias/1306974-medida-provisoria-cria-programa-desenrola-3-0-para-renegociar-r-150-bilhoes-em-dividas):
  "O governo estima que até R$ 150 bilhões em dívidas possam ser renegociados pelas regras do programa" e "a estimativa
  é desembolsar R$ 15 bilhões para adquirir os R$ 150 bilhões em dívidas".
- Agência Senado (https://www12.senado.leg.br/noticias/materias/2026/09/28/desenrola-brasil-3-0-ja-esta-em-vigor-veja-como-funciona):
  "até R$ 150 bilhões em dívidas poderão ser elegíveis, com estimativa de R$ 75 bilhões efetivamente renegociados e alcance
  de até 15 milhões de pessoas".
- R$ 150 bi é valor de face das dívidas, não custo público; o custo máximo é R$ 15 bi. Imprensa privada atribui ao ministro
  do Planejamento um estoque de R$ 300 bi em dívidas vencidas; não confirmado em fonte oficial.
- Fazenda, Tesouro, Consultorias de Orçamento e TCU: nenhuma nota técnica sobre a MP 1.393 foi encontrada (as notícias do
  gov.br estão restritas no período eleitoral; a nota de adequação orçamentária do Congresso ainda pode sair).

## Quem assinou: fontes dos cargos
Nomes copiados das assinaturas de cada ato no DOU. Cargos: EXMs assinadas digitalmente (Moretti, Mello, Durigan),
Decretos de 26/06/2026 da Ordem do Mérito da Defesa (DOU 29/06: Wellington, Durigan, Márcio Elias Rosa, Santoro,
Moretti), Portaria Interministerial nº 216/2026 (DOU 22/07: Paulo Henrique Rodrigues Pereira, Luiz Marinho, Boulos),
atos do Ministério das Comunicações (DOU 02/10: Frederico de Siqueira Filho), busca do DOU (André de Paula, Agricultura e
Pecuária, 10/04/2026; Rivetla Edipo Araujo Cruz, Pesca e Aquicultura, 03/06/2026). Fotos: não baixadas, a ligar pelo
agente principal.
