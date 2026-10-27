# Brasil-Imposto: padrões aprendidos

Registro do que as sessões de 2026-09-25 a 2026-10-01 (rounds 1 a 11 das prévias) e de 2026-10-01 a 02 (grill de alinhamento) ensinaram. As decisões do autor ficam em
`docs/decisions/README.md` (tabela D, perguntas Q); aqui ficam os padrões de trabalho, as armadilhas dos dados e as receitas que funcionaram.

## Learned patterns

### Fontes oficiais: frequência e armadilhas
| Dado | Fonte | Frequência | Armadilha |
|---|---|---|---|
| Arrecadação federal por estado | Receita Federal | mensal | De fev/2025 a jan/2026 a Receita lançou no DF de 14,8% a 25,2% da arrecadação do país (antes, no máximo 10,8%), em quase todos os tributos ao mesmo tempo. Meses com 2% a 4% sem estado em 2024-09 e 2026. Ver D37 e D40. |
| Arrecadação federal por município | Receita Federal | **anual** (2005 a 2025) | Não há versão mensal aberta encontrada; por isso o saldo da cidade não fecha num mês do ano corrente. O arquivo de 2025 tem a mesma quebra do DF (Brasília com R$ 603 bi). |
| Repasses da União | Portal da Transparência (CGU) | mensal | O servidor de downloads tem um WAF da AWS que bloqueia rajadas (HTTP 405 com página de desafio no lugar do ZIP). Ritmo que funcionou: um arquivo a cada 90 s, com espera crescente; o script retoma de onde parou (`pipelines/series/agg_transfers_monthly.py`). |
| Bolsa Família, BPC | MDS (MI Social) | mensal | O programa mudou de nome (Auxílio Brasil de nov/2021 a fev/2023). |
| INSS | Previdência (BEPS) | mensal por estado | Por município existe microdado aberto do INSS (jul/2021 em diante), sem login; ainda não carregado. Nunca escrever "não há dado aberto" sem procurar. |
| Orçamentos de estados e prefeituras | Tesouro, SICONFI | a cada 2 meses (RREO) e 4 meses (RGF) | Buscar o RREO **e** o RREO Simplificado: só o primeiro faz 2.329 municípios parecerem "sem relatório". Os relatórios são acumulados no ano: o bimestre isolado é a diferença entre dois. |
| Contas do governo federal | Tesouro (RTN) e BCB (dívida) | mensal | Um mês de atraso. |
| Folha federal por estado | Portal da Transparência (execução da despesa) | mensal | Militares não têm estado em nenhum arquivo aberto (todos os registros com UF -1). O arquivo de servidores tem 40% das linhas sem UF e põe no DF quem trabalha fora. Aposentados e pensionistas não têm coluna de UF. R$ 208 bi da folha de 2024 ficam sem estado. |
| Gasto federal direto por UF | Portal (execução da despesa) mais o cadastro de UGs do SIAFI (Tesouro Transparente, `siafi-relatorio-unidades-gestoras`) | mensal | Pelo localizador, 90% do gasto direto do Executivo fica sem UF; pela UG que paga, quase tudo ganha UF, mas seguro-desemprego, abono, folha militar, compras centralizadas da Saúde e obras do DNIT caem na sede (DF, RJ). Regra adotada: as duas etapas (D45). O arquivo de jun/2025 vem com quase o dobro do normal. |
| Seguro-desemprego e abono por UF | MTE, Relatório de Gestão do FAT (anual) | anual | A única série por UF achada são os rótulos de dois gráficos do PDF. No seguro-desemprego, a soma das barras por UF não bate com a pizza por região do mesmo gráfico; o total bate e o texto confirma as barras. |
| Vínculos públicos por UF, três esferas | Ipea, Atlas do Estado Brasileiro (a partir da RAIS) | anual, com atraso | O ano mais recente por UF é 2021. Federais civis do Executivo mais recentes: arquivo do SIAPE do Ministério da Gestão. |
| Arrecadação federal por natureza jurídica | Receita Federal | mensal | Não tem UF. Mostra que 98,7% da contribuição dos servidores federais (CPSSS) é paga por órgãos federais: imposto que a União paga a si mesma e que o arquivo por UF registra no DF. |

### Estimativa só com teste
- Uma estimativa só entra no site com um teste do método em anos em que o dado verdadeiro existe, e o erro vai para a tela.
- Fica num arquivo separado do dado publicado (ex.: `data/series/federal-revenue-uf-estimated.json`). O publicado nunca é alterado.
- Quando o teste mostra erro grande para a pergunta em jogo, não se estima. Ex.: a folha federal por participação errou 4,8% na mediana e 10,6% no DF, justo o estado em discussão (D41).
- Uma "foto de antes" para comparar pode ser um estado intermediário de outra coleta. O invariante certo é o arquivo publicado: 2024 da série mensal tem de bater ao centavo com `data/uf-balance-2024.json`, e a checagem tem de pegar um erro de controle de R$ 500.

- Checagem ao centavo, sessão de 2026-10-02: o arquivo da Receita por estado tem colunas com três casas decimais, e 4
  estado-mês de 2026 caem em meio centavo exato (AC, MA e RR em fev, RO em jun). O critério certo é "a série é o valor
  exato do arquivo arredondado ao centavo" (diferença de até meio centavo contra uma passada em `Decimal`), não igualdade.
- A passada independente também erra: a primeira somou as colunas erradas (`r[13] + r[14]` em vez de pago mais restos a
  pagar) e o controle acusou R$ 29,7 bi a mais do que o centavo esperado. Quando o controle falha por mais do que o erro
  plantado, o defeito está na checagem.
- O script só grava o JSON depois de a checagem passar; antes, uma rodada que falhava deixava o arquivo no disco.
- A base do Tesouro somada sem mês (`pipelines/ug/agg_dtt_full.py`) não serve para um período parcial; `pipelines/ug/agg_dtt_monthly.py` guarda o mês.
  O FCDF (unidade 73901) fica sob o órgão 25000 (Fazenda) nessa base, não sob o 73000.

- **A checagem ao centavo não pega um erro de recorte.** Em 2019 o fundo do INSS tinha outro código de unidade (25917;
  40904 em 2023; 33904 em 2024), a exclusão por código não pegou nada, os benefícios entraram de novo como gasto do
  Executivo no DF e o DF saiu a -R$ 21.687 por pessoa por mês, com todas as checagens ao centavo verdes. A defesa:
  excluir pelo nome do fundo e pela ação, e comparar o que o recorte deixa de fora com a série que conta aquilo pelo
  destino (INSS, Bolsa Família, BPC, FCDF numa faixa de 0,85 a 1,3), provada com o erro plantado de volta.
- **Arquivo do governo quebrado:** o arquivo do Portal de jun/2025 foi gerado de novo pela CGU em 01/10/2026 com todos os
  valores zerados (uma versão anterior tinha a folha em dobro). Conferir cada mês do Portal contra a base do Tesouro no
  mesmo recorte **sem as sentenças judiciais** (só o Tesouro as traz: R$ 61,6 bi de precatórios em dez/2023, R$ 25,9 bi
  em mar/2026 com a ação nova 00WU, por isso identificadas pela categoria do RTN, não pelo código). Sem elas a razão fica
  entre 1,00 e 1,01 mês a mês; fora de 0,9 a 1,1 o mês fica de fora dos dois lados, com aviso na tela.

### Data de divulgação (GD33): onde ler
- Portal da Transparência: `Last-Modified` do arquivo no servidor de dados abertos da CGU (os meses de 2026 foram gerados
  de novo em 17/09/2026). Receita: a data "Publicado em" da Análise da Arrecadação do mês no gov.br (o CSV por estado não
  tem data e o gov.br não manda `Last-Modified`). Tesouro: `last_modified` do recurso no CKAN. IBGE: campo `modificacao`
  de `/api/v3/agregados/6579/periodos`. Previdência: data da página `/view` do boletim. MDS (MI Social) e a API do Banco
  Central não publicam data.
- "Sem data publicada" (a fonte não tem) e "data a conferir" (ainda não lemos) são coisas diferentes na tela; a prévia
  quase mostrou a data do BEPS de 2026 para os números de 2024.
- Em 2026-10-02 o Portal entregou os arquivos de execução da despesa de jan a jul/2026 no ritmo de 90 s, sem bloqueio:
  a coleta que travou em Q32 (folha federal de nov/2025 em diante) pode ser tentada de novo.

### Regra de localização: a mesma dos dois lados
- O lado "envia" segue a lei: IR retido, PIS e COFINS são recolhidos na matriz de quem paga (Lei 9.779/1999, art. 15; RIR/2018,
  arts. 202 e 932), o que infla SP e o DF. Um lado "voltou" que só conta o que tem UF no localizador fica assimétrico e pintou o
  DF de verde.
- Quando o autor diz que um número "não faz sentido", pesquisar os fatos **e** testar a definição da métrica. No DF, os fatos
  confirmaram a leitura dele (1º em vínculos públicos e em gasto por pessoa) e o defeito era a regra, não o dado.
- Mostrar a sensibilidade entre variantes antes de decidir: o DF ficou em último em todas (de -R$ 1.968 a -R$ 6.836 por pessoa
  por mês em 2024), então a conclusão se sustenta e só o tamanho depende da regra.
- Toda regra vale igual para os 27 estados; nenhuma regra só para o DF.

### Rodadas depois do grill (D59)
- Uma rodada nova parte da simulação aprovada e muda só o que a regra pede. A rodada 1 foi montada do zero e perdeu o
  modal do estado, os casos, as fotos, o seletor de anos e as bandeiras dos vizinhos; o autor reprovou na hora.
- Os vizinhos ficaram pretos porque a página não carregava `bi-data.js` (as bandeiras vão embutidas nele): pelo caminho do
  arquivo, o Chrome bloqueia o desenho de imagens soltas no WebGL. A sonda servida por http escondeu isso. **Conferir a
  prévia pelo `file://`, do jeito que o autor abre**, com uma foto (não só `data-ready`).
- Cartão sobre o mapa: conferir em 1024, 1280, 1366, 1440, 1680 e 1920 px. A legenda cresceu com notas e datas e cobriu a
  costa da BA e do ES em 1280 px; as notas longas saíram de cima do mapa (desde D159 ficam na página "Como ler o mapa") e, entre 761 e 1062 px de janela (1180 px de CSS, com o zoom de 90% de D96), os cartões
  saem de cima do mapa.
- Uma classe genérica num componente novo colide com a página: a dica da busca de emendas usou `.hint` e herdou o
  `position: absolute` da dica do hero, aparecendo em cima do mapa.

### Banco Central e posts de redes sociais (2026-10-03)
- Em 2026-10-03 o `api.bcb.gov.br` servia um certificado de outro host. O serviço SOAP do SGS em
  `www3.bcb.gov.br/wssgs/services/FachadaWSSGS` (certificado válido) entrega as mesmas séries (`getValoresSeriesXML`).
- O SGS publica em R$ milhões com duas casas (R$ 10 mil). A cópia do Tesouro tem mais casas: a conferência entre as duas
  é dentro de uma unidade publicada, não ao centavo.
- Números de posts políticos costumam estar certos e mal rotulados: os R$ 126 bi de superávit de 2022 são do setor
  público inteiro (o governo federal teve R$ 46 a 55 bi); os R$ 10,8 tri são a dívida bruta (estoque), não déficit.
  Mostrar no site o número com o escopo escrito, nunca escolher o escopo que favorece um lado.
- `inOffice` contava como no cargo quem saía no primeiro dia do período (a data de fim é o dia da posse do sucessor):
  o mandato 2023 a 2026 mostrava dois presidentes. Fim é exclusivo.

### Dado que não existe (2026-10-03)
- Quando o dado pedido não existe (saldo com a União por Região Administrativa do DF), perguntar ao autor; nunca colorir
  com outra medida que ele não pediu (a população foi reprovada na hora, D68).
- Edição por fatia de texto (`t[:a] + novo + t[b:]`) com marcador de fim distante apagou dez funções de `statehero.js`
  (do painel do DF até o fim do mapa municipal) e o mapa sumiu de todos os estados. A cópia de segurança já tinha sido
  apagada na limpeza; foi preciso reconstruir pelo que foi lido na sessão. Regras: substituição exata com
  `assert t.count(old) == 1`, nunca fatia entre marcadores distantes; apagar a cópia de segurança só depois de testar a
  página; depois de mexer num módulo compartilhado, testar os modais que o usam (SC e DF).

### Linhas de um anexo somam o total do anexo (2026-10-03)
- O mapa de linhas do RREO Anexo 3 tinha só as linhas dos estados. O DF informa no mesmo anexo os impostos de prefeitura de
  Brasília (ISS, IPTU, ITBI) e o FPM, cerca de R$ 6 bi por ano, e eles sumiram da coluna "Pagou" por semanas; a legenda ainda
  dizia que estavam dentro de "Taxas estaduais" (R$ 606 mi, que são outra coisa). O total não acusou porque a linha
  "Demais receitas" era calculada como o resto e engolia a diferença calada.
- Regra: toda lista de linhas tirada de um anexo soma o total do próprio anexo ao real, em todos os entes e períodos, e o
  script não grava quando não soma (controle: tirar uma linha tem que falhar). Uma linha "Demais" calculada como resto nunca
  serve de checagem. A mesma checagem pegou Minas, que preencheu o IRRF do 1º bimestre de 2026 com o nome "IBS".

### Comparar só na mesma régua (2026-10-03)
- "O Judiciário é o mais caro por servidor": na única régua igual para todos os Poderes civis (remuneração média do quadro
  efetivo, avaliação atuarial do RPPS, julho de 2025) a maior média é a do Legislativo. A conta do CNJ (R$ 68,7 mil a
  R$ 101,6 mil por magistrado por mês) soma indenizações, encargos e o que se paga a aposentados, e não existe igual para os
  outros Poderes. As duas aparecem lado a lado, cada uma com o que mede, e nunca numa lista ordenada única.
- Dividir a folha do Tesouro pela contagem do RPPS infla o Legislativo: os comissionados sem vínculo (cerca de 15 mil na
  Câmara e no Senado) recebem dessa folha e não entram na contagem.

### "Por pessoa, por mês" em período aberto (2026-10-03)
- Cada fonte cobre meses diferentes dentro do mesmo período: em 2026, a arrecadação federal ia até julho e os relatórios dos
  estados (bimestrais) até junho, mas a página dividia tudo pelos 8 meses do período. Todos os estados apareciam até 25% abaixo
  em 2026 (DF: pagou R$ 5.460 em vez de R$ 6.360 por pessoa e por mês). Ninguém viu porque o número parecia plausível.
- Regra: a média mensal divide pelos meses que a fonte cobre (`sum()` já devolve `n`; usar), e o cartão diz quais meses são
  ("2026 (janeiro a junho), último relatório do governo"). Conferir com um número feito à mão: ISS do DF de janeiro a junho
  dividido por 6 deu R$ 113,62, e a tela mostrava R$ 85 (dividido por 8).

### DF por Região Administrativa (2026-10-03)
- Brasília é o único município do DF (CF art. 32); o GDF cobra ISS, IPTU e ITBI e recebe o FPM, e informa tudo no mesmo RREO
  dos impostos de estado. As 37 regiões não têm prefeitura, câmara nem imposto próprio.
- Portal da Transparência do DF: API aberta em `/api/...`, que exige o cabeçalho `x-client-id` com qualquer UUID. Tem orçamento por
  Unidade Gestora (cada Administração Regional é uma), gasto por subtítulo (o lugar vem no fim do nome), o painel "Despesas
  Regionais" (pago por Administração) e a folha (função "ADMINISTRADOR REGIONAL"). DODF, Infobras e os sites das Administrações não
  responderam; a "Consulta Dinâmica" dá "Erro SQL".
- Só 3,5% a 8,7% do gasto do GDF cita uma região, e parte disso é sede de órgão (Plano Piloto: folha do TCDF, do DER e do
  Hemocentro). Nenhuma das duas medidas por região serve para colorir o mapa sem enganar; isso tem de ir ao autor antes (ver
  `.claude/CLAUDE.md`, "O que perguntar em vez de decidir"), não depois.

### Custo por pessoa no setor público federal (2026-10-03)
- Quantidades e médias por Poder: avaliações atuariais do PLDO (Anexo IV.11, regime próprio dos civis; Anexo IV.12, militares),
  baixar com `/@@download/file` no fim do endereço do gov.br. A DPU vem dentro do Executivo nessa fonte.
- Custo por magistrado com tudo somado: CNJ, Justiça em Números (PDF de 27 MB; `pdftotext` e apagar o PDF). As frases
  "média mensal de R$ X mil por magistrado(a)" estão no texto, por ramo; incluem o que se paga a aposentados.

### Disco (2026-10-02)
- O disco encheu (ENOSPC) com cinco agentes de coleta em paralelo; a ferramenta de comandos parou de funcionar e nem o
  diagnóstico rodava. Regra das coletas grandes: um arquivo por vez, apagar o bruto, ler por HTTP Range, temporário apagado no
  fim, parar com menos de 5 GB livres, no máximo dois agentes de coleta.
- Um agente parado pode deixar processo órfão (um `http.server` ficou servindo a pasta temporária): conferir `pgrep` e
  o diretório do processo antes de matar.
- Pasta temporária de sessão antiga guardava 2,9 GB de brutos já processados (obras, ponte, séries): apagar o bruto assim
  que o JSON do projeto existe.

### Prévias que abrem pelo arquivo
- As prévias abrem por `file://`: nada de `fetch` nem import de módulo local. Os dados vão como scripts clássicos (`window.BI` em `assets/bi-data.js`), gerados por `docs/superpowers/tools/build-standalone-data.py`. A simulação da home sai de `tools/build-simulation.py`.
- Ordem depois de qualquer mudança em `data/`: `build-cases.py` (se mexeu em obras), `build-standalone-data.py`, `build-simulation.py`.
- Os módulos compartilhados em `docs/superpowers/previews/assets/` (`proposals.js`, `statehero.js`, `serieslayer.js`, `contas.js`, `periods.js`, `politicians.js`, `cases.js`) servem a página de propostas e a simulação, para nunca divergirem.

### Conferir antes de entregar
- **Link longo perde o fim ao ser copiado do terminal** (2026-10-06, duas vezes): o endereço da spec tinha 142 caracteres e o
  Chrome do autor recebeu só até `.htm`, sem o `l`, e deu ERR_FILE_NOT_FOUND. Na entrega, abrir a página no Chrome dele
  (`open -a "Google Chrome" <arquivo>`) e dar também o link curto da pasta (`file://<pasta do projeto>/docs/superpowers/previews/`).
- Servir `docs/superpowers` com `python3 -m http.server 8765 --bind 127.0.0.1` e fotografar com `docs/superpowers/tools/shot.sh` (o `chrome-headless-shell` do Playwright, já com os ajustes abaixo).
- O WebGL do mapa 3D só funciona no headless com `--enable-unsafe-swiftshader --use-angle=swiftshader`.
- Usar um `--user-data-dir` novo a cada foto: o perfil reaproveitado serviu `bi-data.js` e `contas.js` velhos duas vezes e quase gerou diagnóstico falso.
- `tools/action-probe.html` abre o estado (`open=SC`), escolhe município (`mun=<IBGE>`), período (`period=year:2024`), modal do Brasil (`brasil=1`) e rola até um seletor (`scrollto=`). A página do round 10 aceita `?case=<id>&cmp=1`.
- Sempre em duas larguras: 1440 e 420.

- Erro de execução e console são coisas diferentes: o probe (`tools/action-probe.html`) pega o erro que estoura na ação
  ("PROBE ERROR ..."), e o console do Chrome sem cabeça (`--enable-logging=stderr`) pega `console.error` e erros soltos. Ler os
  dois. O console foi provado com uma página quebrada de propósito (2 erros achados) antes de confiar no zero.

### Agentes de pesquisa
- Dar a cada agente um prefixo de arquivo próprio. Dois agentes escreveram `pipelines/works/download.sh` e um apagou o do outro; recuperado do registro do agente.
- Um agente que morre no limite de uso pode deixar o próprio download rodando até o fim. Depois, conferir o log do job e rodar o passo de montagem que o agente não alcançou (assim foram recuperados os repasses de 2025 e 2026).
- Agentes com "verifique na fonte" passam do prazo (a folha levou 5h30 contra 90 min pedidos). Escopo pela decisão, não pelo tema.
- Fotos de pessoas: URLs remotas do Wikimedia Commons, da Câmara e do Senado, com autor e licença; os termos de uso da Câmara e do Senado permitem reproduzir citando a fonte.
- Três de seis agentes travaram em 2026-10-01 ("no progress for 600s"), sempre depois de escrever boa parte do trabalho. O que
  funcionou: conferir o disco antes de relançar; rodar de novo o script do agente e o controle que deve falhar; escrever a seção
  que faltou, ou lançar um agente novo só para "terminar as seções que faltam" lendo o relatório parcial (cerca de 40 min contra
  um recomeço inteiro).
- Registrar as decisões no grill **antes** de lançar um agente que lê o registro: um agente lançado antes leu até GD37 e
  relatou que GD38 a GD43 "não existiam".
- Pedir no prompt chaves de JSON e nomes de arquivo em inglês: os agentes de 2026-10-01 gravaram chaves em português
  (`data/ug/*.json`), que precisam ser renomeadas (D54).

### Texto na tela
- Nada de afirmação sem fonte, nem para explicar um número. Ex.: "boa parte da folha sem estado deve ser paga no DF" saiu do texto porque nenhum arquivo diz isso.
- Neutralidade: só cargos, datas e partido na época, o mesmo tratamento para todos. Candidaturas de 2026 ficam nos dados para a revisão jurídica e nunca na tela.
- Foto que mostra só a região da obra diz isso na legenda.
- Pistas do autor conferidas em 2026-10-04 e 05: fundo eleitoral de 2026 (5 bi certo; "dobrou" errado, igual a 2024; votação
  simbólica, sem voto por partido), monotrilho de SP (Linha 17-Ouro aberta em 31/03/2026, não 2024; nenhum documento oficial diz
  "superfaturamento"), ponte Hercílio Luz (R$ 507,3 mi pagos de 2006 a 2020, contrato por contrato com a supervisão e a 1ª etapa pela CPI; nenhum documento perto dos R$ 800 mi lembrados). Em
  todos, a resposta mostrou o fato oficial lado a lado com a lembrança, e o autor aceitou.
- Foto de obra no Wikimedia Commons: abrir e olhar antes de usar. A primeira candidata do monotrilho ("Monotrilho, Linha
  17-Ouro") mostrava um túnel de avenida, sem monotrilho; a escolhida mostra a Estação Morumbi em obras (2020).
- Afirmação do autor é pista, não fato: a venda dos gasodutos atribuída ao Tarcísio (a Petrobras vendeu a NTS em 2017 e a TAG em
  2019; ele era ministro da Infraestrutura), o "nunca apresentou um projeto" do Tiririca, os "pelo menos R$ 100 bi" dos
  escândalos e os shows "no Norte e Nordeste" (o caso mais repercutido foi em MG). Conferir na fonte antes de qualquer frase.
- Quando o pedido vem com linguagem carregada ("sugam", "gera valor", uma página só sobre um político, a Rouanet como "comprar
  artistas"), manter a intenção e propor a forma neutra apoiada na própria regra do autor (GD10, só dados): legenda formal,
  ficha igual para todos com busca, Rouanet entre os demais incentivos. Ele aceitou todas as vezes.

### Grill e rodadas de decisão
- Estado do grill num arquivo do projeto: árvore de pontos (G), registro de decisões (GD) com as palavras do autor, e uma tabela
  que liga cada pergunta da rodada ao seu ponto. Nos títulos da rodada, numerar de 1 em diante; os códigos G só no arquivo.
- Começar pela raiz (o objetivo, montado com as frases do próprio autor), nunca pela logística de lançamento.
- O autor responde melhor a uma tabela curta (# | decisão | recomendação) do que a texto longo; repetir em formato curto o que
  ele pular. Uma pergunta escondida na primeira linha de uma tabela logo depois de uma lista passou despercebida.
- Ao acrescentar linhas a uma tabela markdown por script, inserir depois da última linha e conferir que nenhuma linha em branco
  separa as linhas; inserir antes do título seguinte quebrou a tabela de decisões em sete pedaços.
- Na conversa com o autor (terminal), nada de `<br>` dentro de tabela: o terminal mostra a tag crua
  (2026-10-04). Opções de uma célula vão separadas por ponto e vírgula, ou a tabela vira lista.

### Mudar como um estado aparece: são quatro lugares (2026-10-17, D138)
O veredito de um estado ("Enviou", "Recebeu", "o que mais envia") e a cor dele saem de quatro fontes, e cada uma precisa
mudar junto: a página-fonte da home (`BRASIL-IMPOSTO_DESIGN_hero-mapa-3d-round-2_2026-09-29.html`: valor da métrica, escala,
tooltip, linha da legenda, notas e o líder), `assets/statehero.js` (janela do DF e mapa das Regiões Administrativas),
`assets/proposals.js` (caixa "O estado e a União" da janela de qualquer estado) e `assets/ledger-graph-view.js` (a rede).
Depois, reconstruir com `build-simulation.py` e `build-platform-preview.py`, e conferir no navegador as três métricas, os
três períodos, alguns anos, o passar do mouse e o clique, procurando o veredito antigo em todo texto visível. A primeira
passada do DF em revisão esqueceu `proposals.js`, achado só porque a janela foi aberta com clique de verdade.
O Chrome guarda os scripts da prévia: depois de mudar um `assets/*.js`, recarregar com Cmd+Shift+R.

### DF, vizinhos e entradas de dinheiro (2026-10-04)
- O mapa de um estado mostra o mesmo número do mapa do Brasil quando o dado não desce mais: o DF usa a linha `BIL.federalAt('DF')` e
  a escala de 26 estados da home (`statemap` aceita `scale` de fora), em vez de inventar uma medida por região (D68, D78).
- Nome de vizinho no mapa 3D: no celular (420 px) o quadro é limitado pela largura e as margens laterais somem; só a margem de cima
  aparece em todas as larguras. Goiás fica acima da divisa norte; Minas, que só encosta no canto sudeste, aparece em 1440 e some em
  420. O construtor confere que cada nome cai dentro do próprio estado, com controle plantado.
- Entradas de dinheiro na União (dividendos, imposto novo): a fonte é o Resultado do Tesouro Nacional do mês (tabela por empresa e
  texto sobre receitas atípicas) mais o arquivo diário de receitas do Portal da Transparência para a data. Datas no cartão: o dia
  do pagamento (`moved_on`), não a data do documento que o registra.

### RS no formato de SC (2026-10-04)
- Generalizar em vez de copiar: os scripts de SC ganharam `--uf`, e a prova de que nada mudou foi refazer SC com eles. Onde o bruto
  de SC já tinha sido apagado, o mesmo arquivo nacional baixado para o RS foi agregado para os dois estados numa passada só, e SC
  saiu igual valor por valor ao publicado, menos set/2026, que o Portal ainda estava preenchendo quando SC foi coletado.
- O agente de coleta parou por travamento (600 s), mas os dois downloads que ele lançou seguiram sozinhos e terminaram; o log de
  progresso do agente (feito, rodando, próximo) bastou para continuar sem relançar nada.
- O WAF do Portal alternou: de 90 s por arquivo a esperas de 1 a 2 horas por arquivo (das 3h às 9h), e depois voltou a 90 s.
  Script que retoma de onde parou é obrigatório.
- Uma checagem nova (o nome de cada vizinho cai dentro do próprio país) achou um defeito antigo no mapa de SC (Argentina do lado
  brasileiro). Defeito achado assim vai para o autor como item à parte; a exceção fica escrita no próprio script.
- Na Grande Porto Alegre, quatro dos dez maiores municípios ficam colados: os nomes no mapa do RS pulam o município cujo nome
  cobriria outro (só no RS; SC ficou como estava).
- Afirmação do autor conferida na fonte (fundo eleitoral, 2026-10-04): "5 bi" certo; "dobrou" errado para 2026 (igual a 2024; o
  que dobrou foi 2020 para 2022; em 2026 o Congresso multiplicou por 4,9 a proposta do Executivo); "esquerda e direita votaram a
  favor" sem registro: votação simbólica, só os votos contrários ficam anotados. As APIs de votação da Câmara e do Senado não
  registram sessões conjuntas do Congresso; resultado vazio delas não prova nada. tse.jus.br bloqueia acesso automático (403):
  ler pelo Internet Archive.
- "A conta fecha?" (D90): perder a validade não quer dizer a mesma coisa dos dois lados. Receita prevista de MP que caducou
  nunca existiu (fora da soma); MP de gasto que caducou pode ter sido gasta enquanto valia (Auxílio Emergencial, MPs 937 e
  988): tirar da soma seria falso negativo. Teto e previsão não são caixa: a conta que fecha usa só valores pagos.
- Planalto, in.gov.br e camara.leg.br recusaram conexão desta máquina em 2026-10-04 e 05; o servidor de documentos do Senado
  responde com desafio de robô. Funcionou: cópia do Planalto no Internet Archive (`web.archive.org/web/2026/<url>`, com
  `curl -L`) e a API de dados abertos do Senado para ementa e lista de documentos.
- No celular as listas da home ficam numa faixa fora do hero: qualquer atualização tem de procurar no documento inteiro, não
  dentro do hero (a faixa ficou parada no ano errado até a correção).
- Zoom do navegador x CSS `zoom` (Chrome 149, medido em 2026-10-05): `html { zoom: .9 }` imita o zoom de 90% para posições,
  elementos fixos e coordenadas do mouse (getBoundingClientRect e clientX ficam na mesma escala), mas encolhe `vh` e `vw` em
  10%: toda unidade de tela precisa ser dividida pelo fator. Mapas WebGL com rótulos CSS2D medem o tamanho em px da página
  (`offsetWidth`), não da tela, e convertem a posição do mouse pelo fator `k = rect.width / offsetWidth` antes de posicionar o
  balão. Conferir comparando a página nova em 100% com uma cópia sem o zoom renderizada na janela dividida por 0,9.
- "Soma" de uma lista de destaques não é a conta (2026-10-05): somar só os cartões (maiores movimentos isolados) mostrou
  R$ 34 bi de receitas da União, sem os impostos comuns; o autor pegou comparando com SC (R$ 97,5 bi só de um estado). Uma
  soma com o nome "Receitas" tem de ser o total oficial (RTN), e toda conta exibida tem de fechar com os valores como aparecem
  na tela: com "tri" de duas casas, cada linha arredonda até R$ 5 bi e a conta feita à mão não fecha. Conferir somando os
  valores exibidos, em todos os períodos.
- Base do Tesouro "Despesas e Transferências Totais da União": a coluna CATEGORIA_RTN muda de forma entre os anos (números
  romanos "I." e "II." até 2023, "nan" no lugar de "N/A" em 2024). Sem normalizar, 2019 a 2024 pareciam 13% a 96% acima do
  RTN; normalizado, todos os anos batem em até 0,2%. Câmara e Senado saem por órgão (1000, 2000); fundos partidário e eleitoral
  por ação (0413, 0EB8).
- CSS `zoom` não muda as media queries: elas leem a janela real. Para "100% igual a 90%", todo limite de layout tem de ser
  dividido pelo fator também (layout lateral a partir de 1181 px de CSS = 1063 px de janela). O erro de 2026-10-05 deixou
  janelas de 1063 a 1180 px no layout empilhado; conferir na largura da janela do autor, não só em larguras redondas.
- O pacote da prévia passou de 43 MB para 85 MB (orçamentos do RS, 37,6 MB) e abre em cerca de 1 s pelo arquivo; no site (D55) cada
  estado vai num JSON próprio.

### Rede do dinheiro e testes de interação (2026-10-09, D133 a D136)

- **A rede usa as funções do mapa no navegador, para qualquer período** (`assets/ledger-graph-model.js`): o número de cada estado
  é o do mapa no mesmo período. `docs/superpowers/tools/ledger-graph-periods-check.cjs` roda os 100 períodos (92 meses, 8 anos,
  2 mandatos) e planta dois controles (R$ 1 na Cofins de SC; um ponto sem ligação) em ano, mandato e mês.
- **A tolerância tem de ser menor que o controle.** Com tolerância de R$ 1, o controle de R$ 1 passou no mandato 2023 a 2026,
  porque a diferença real ali era de R$ 0,08. Medir antes a maior diferença real em todos os períodos e pôr a tolerância entre
  ela e o controle (hoje R$ 0,50).
- **3d-force-graph 1.80, o que a biblioteca faz sozinha:** deixa arrastar os pontos (`enableNodeDrag` vem ligado); o
  ForceGraph3D fixa `clickAfterDrag(false)` e conta qualquer movimento de 1 px do mouse apertado como arrasto, então o clique
  some; o raio dela acerta pontos apagados quase invisíveis (a opacidade sai do alfa da cor) e testa todas as ligações a cada
  movimento; trocar `linkColor` refaz toda a atualização das ligações, partículas incluídas. Solução que ficou
  (`assets/ledger-graph-view.js`): `enablePointerInteraction(false)`; a página lê o clique (até 6 px e 700 ms) e escolhe o
  ponto pela linha de visão do cursor (`screen2GraphCoords`) contra a esfera de cada ponto (raio `cbrt(val) * nodeRelSize`),
  o aceso mais perto primeiro; folga de 6 px só quando nada é atingido (a folga competindo em profundidade deu 12 de 20
  cidades certas); o destaque espera o ponteiro parar 0,2 s (recolorir a cada cidade cruzada travava a página).
- **Interação se confere com eventos reais de mouse, não com captura de tela** (o autor achou três defeitos seguidos: arrastar,
  clicar, selecionar no cacho). Uma janela de automação do Chrome que fica escondida dá captura branca e a cena não
  anda. No Chrome sem tela, o desenho por software é lento: depois de um voo de
  câmera de 1,4 s, esperar 3 s antes de apontar para um ponto.
- **A sonda não pode usar o mesmo cálculo que testa.** A de seleção calcula a linha de visão por conta própria e, em cada erro,
  imprime o que a geometria atinge; foi isso que mostrou o defeito da folga em uma rodada. Controle: a mesma sonda 25 px fora do
  centro tem de errar quase tudo.
- **Pergunta sobre estimativa diz o número e os meses exatos.** "2025 tem meses estimados" foi lido como "2025 é tudo
  estimativa" e o autor achou que a pesquisa tinha sido perdida. Dizer: só "o que cada estado pagou", de fev a dez/2025; o total
  do país e tudo o que voltou são oficiais.

### Os 3 Poderes, DF e publicação (2026-10-21, D143 a D147)

- **Soma de um grupo tem rótulo de soma.** O cartão dos 513 deputados mostrava a média por deputado com o rótulo "total médio
  por pessoa", lido como o total do grupo. Mostrar "Os N juntos" com a soma e, embaixo, "Média por <cargo>", cada número com o
  seu rótulo.
- **Linha informativa fica fora do total.** O líquido do salário e a fatura do cartão repetem dinheiro que já está em outras
  linhas; somados, contam duas vezes. Ficam ao lado como informação (marca "i"), fora da soma.
- **Pagamento único não é mensal.** O 13º e outros pagamentos de uma vez são espalhados pelos meses do período antes de entrar
  no "por mês".
- **Cartão da Presidência pelas unidades certas.** A busca por órgão traz ABIN e EBC; o gasto ligado ao presidente usa só as três
  unidades da Presidência de `data/federal/presidency-2026.json`.
- **A janela da coleta não é um fato da pessoa.** "Câmara, desde 1987" era o início da varredura; a ficha mostra o primeiro e o
  último ano dos projetos da própria pessoa. Todo "desde <ano>" na tela é conferido contra a idade e o mandato de quem aparece.
- **Situação de um projeto da Câmara.** A referência é o campo "Situação" da página do projeto. Na API,
  `statusProposicao.descricaoSituacao` de `/proposicoes/{id}` quase sempre traz o último passo de tramitação ("Aguardando
  Encaminhamento"), não a situação. Na auditoria das três fichas de divulgação, nas 50 divergências entre a ficha e a API, a página
  confirmou a ficha em 41; em 8 era o mesmo apensamento com outras palavras ou um passo atrás ("Tramitando em Conjunto" ou
  "Aguardando Apensação" na ficha, "Apensado ao PL x" na página) e 1 página não tinha o campo.
- **Fundeb só sobre os 22,5% do FPM.** A Lei 14.113/2020, art. 3, tira o Fundeb da alínea b (os 22,5% mensais); as parcelas
  extras de 1% ficam fora. Aplicar sobre o FPM inteiro aumenta o Fundeb.
- **Complemento de moradia da Câmara tem linha própria**, como dinheiro pago à pessoa, separado do que reembolsa gasto.
- **Folha federal por estado é parcial.** Militares, aposentados e pensionistas não têm estado nos arquivos do Portal da
  Transparência; `data/federal/payroll-by-uf-2024.json` tem só janeiro.
- **A estimativa do DF (D146) se prova pela soma.** Em cada imposto, o DF conta no máximo a sua parte no PIB; ano a ano, o
  estimado mais o que foi para a União dá o registrado, e nenhum outro estado muda.
- **A planta do controle de vazamento é maior que a folga.** 40 letras cabiam no cartão e o controle passava; com 90 letras e uma
  checagem de que a planta vazou, o controle vale. Texto vazio tem retângulo em (0,0) e é pulado.
- **Tirar citações sem quebrar títulos.** `publish-decisions.py` tira só as citações em itálico, `(?<!\*)\*"[^\n]*?"\*(?!\*)`;
  a forma larga cortava títulos em negrito como `**"..."**`. O script para se sobrar alguma citação.
- **Primeiro commit público.** O email nos commits é o noreply do GitHub (D97 item 8), configurado no repositório local antes
  do commit e conferido com `git log -1 --format=%ae`; o email pessoal ficaria em todo commit público.

### Publicação no GitHub e sessão na nuvem (2026-10-22, D148 a D153)

- **Endereço:** um site de organização mora num repositório `<org>.github.io` e abre em `https://<org>.github.io` (documentação do GitHub, "What is
  GitHub Pages"). O Pages respondeu o endereço da raiz mesmo com o nome da organização em maiúsculas (`Brasil-Imposto`).
- **Ordem que funcionou:** criar o repositório, ligar o Pages com a fonte "GitHub Actions", ligar a segurança, fazer o push e só então o ruleset da
  `main` (sem exceção, nem para o dono: criado antes, recusaria o próprio push). Depois disso, toda mudança, mesmo de documento, entra por PR com o check
  `dco` verde (squash, que o GitHub assina; desde D157, no `staging`, e o back-merge de cada promoção usa merge commit).
- **Peso medido no ar:** `bi-data.js` tem 87 MB e chega com cerca de 20 MB pela rede (gzip do Pages); o mapa espera esse arquivo inteiro, por isso o
  cartão de carregamento com o progresso real (D152). A divisão por entidade vem com o site em Astro (fases B0 a B2).
- **Conferir o site publicado:** `visible-text-probe.cjs <URL> <saída> --audit` (com `--plant` como controle, que tem de pegar a nota plantada) e
  `tres-poderes-unknown-probe.cjs <URL> [--control]` aceitam a URL publicada; o perfil de comunidade sai em `GET repos/<org>/<repo>/community/profile`.
- **Contar o que a página mostra, não o que o dado diz:** os 16 "unknown" da árvore de Os 3 Poderes eram dado morto (a página lê o registro de cada
  pessoa); a sonda que abre a página e as 722 fichas achou os sinais que apareciam de verdade, e o controle provou que ela enxerga.
- **Sessão do Claude Code na nuvem:** lê o `CLAUDE.md` e o `.claude/` do repositório e as skills ativadas na conta do claude.ai, nada da máquina de quem
  mantém. O GitHub passa por um proxy que recusa GraphQL (`gh pr`, `gh issue`, Projects), tags, releases e apagar branch: usar REST (`gh api`). O app do
  Claude no GitHub tem de estar instalado na organização, senão todo push volta 403. A rede padrão do ambiente não alcança o site publicado (lista de
  domínios do ambiente). Ruleset, Pages, segurança, release, quadro e categorias de Discussions ficam com a sessão local.
- **Documentação do GitHub como fonte primária barata:** `https://docs.github.com/api/article/body?pathname=/en/<caminho>` devolve a página em markdown.
- **Categorias de Discussions** não têm API: foram editadas no navegador.
- **Logo (D153):** nada da marca de um governo, nenhuma bandeira alterada (Lei 5.700/1971, art. 31, II); verde, amarelo, azul e branco livres
  (arts. 28 e 29). As 27 estrelas das rodadas estão nas posições oficiais, lidas em `docs/superpowers/previews/assets/flags/br.svg`; o gerador das rodadas
  fica fora do git.

### Staging, promoção e produção (2026-10-23 e 24, D157 a D165)

- **Conferir a produção antes de uma promoção:** montar `build-site.py --profile production --out _site` em duas cópias
  `git archive` (a `main` e a cabeça do pull request), comparar com `diff -rq` e plantar um byte como controle. A diferença
  esperada é dita antes de comparar: no #52, só o `robots.txt`; no #60, as quatro mudanças de D159 e nada do comércio (os 59
  seletores do CSS caíram a 0).
- **Promoção e back-merge (D166):** uma tarefa aprovada por pull request para a `main` (ramo saído da `main` com o cherry-pick
  do squash da tarefa no `staging`, squash, com o aviso de produção), nunca o `staging` inteiro; uma tarefa que mexe nas linhas de
  outra ainda fora da `main` espera o merge dela e sai da `main` nova (#80 depois do #76). Logo depois da última, `main` para
  `staging` com merge commit (merge commits ligados no repositório; a regra da `main` segue só squash). O
  squash que o GitHub faz usa o e-mail da conta como autor e a assinatura com o noreply, por isso o `dco` aceita esses commits,
  que só o back-merge leva; o commit de cada tarefa na `main` é feito à mão, com o noreply e `-s` (#61).
- **Depois de um deploy do Pages:** o Pages manda `cache-control: max-age=600`, e quem abriu o site pouco antes vê a versão
  antiga por até 10 minutos (2026-10-24: o autor achou que a promoção não tinha ido ao ar). Conferir com `curl` e `?n=<hora>`
  e uma abertura nova no Chrome sem tela, e dizer junto com "está no ar": Cmd+Shift+R.
- **Tirar o staging do ar e religar:** `gh api -X DELETE repos/Brasil-Imposto/staging/pages` (404 em segundos, a produção não
  muda); religar com `gh api -X POST repos/Brasil-Imposto/staging/pages -f build_type=workflow` e rodar o deploy. O staging é
  público por escolha do autor (D165): restringir a quem contribui, só no GitHub, pede o GitHub Enterprise Cloud (pago).
- **Ações fixadas por commit:** conferir cada SHA contra a tag oficial (`repos/actions/<ação>/git/ref/tags/<versão>`,
  desembrulhando a tag anotada), nunca só pelo comentário de versão.
- **CodeQL vermelho num pull request:** os achados saem em `repos/<repo>/check-runs/<id>/annotations`; a lista
  `code-scanning/alerts?ref=refs/pull/<n>/merge` voltou vazia.

### Promoção por tarefa, testes de confiança e fechamento (2026-10-24 e 25, D166 a D171)

- **O workflow que publica a produção vai sozinho e primeiro:** merge, esperar o deploy dele passar, e só então o resto do lote
  (#105, o `pages.yml` fixado por commit: build e deploy verdes antes dos outros dez). Se ele falhasse, nada mais dependeria dele.
- **A ordem do lote sai de uma simulação:** cada cherry-pick sozinho sobre a `main` e todos em sequência, com a árvore final igual à
  do `staging`. Uma tarefa que edita as linhas de outra (a dupla contagem, #88, nas linhas do B1) ou importa o código dela (o B1
  importa a conferência do A4; o teste de G1 precisa de D166 a D171 no registro) só ganha o pull request de produção depois do merge
  da outra, saindo da `main` nova; aplicar limpo não basta, porque o `ci` dele falharia sem a outra.
- **Antes do aviso de produção, dizer quais arquivos publicados mudam e conferir:** o site montado da `main` e do `staging` diferiu
  em 8 arquivos, as 4 páginas (o formulário no cabeçalho, #99) e os 4 pacotes com as chaves trocadas (#101), e em nada mais.
- **Todo lote de merges no `staging` termina com o deploy à mão do staging** enquanto não existe o `STAGING_DISPATCH_TOKEN`, e a
  conferência no ar (o formulário com a chave, a faixa, o `noindex`). Em 2026-10-25 o deploy ficou para depois de 11 merges, até o
  autor perguntar o que faltava.
- **A4, uma lista que só encolhe:** `data/series/known-gaps.json` guarda cada diferença sem explicação (367 em 2026-10-25, quase
  todas de um centavo) e `test_known_gaps.py` falha com uma diferença nova e com um item que já não acontece. Quando a Receita
  trouxer 2026 ao centavo (Q-A4), os itens de 2026 saem da lista no mesmo pull request.
- **B1, o centavo do ponto flutuante:** a página soma o bloco da União em ponto flutuante (27 valores na casa dos trilhões), e o
  resultado pode cair a um centavo da soma exata; o centavo é admitido só ali, e o controle de R$ 1 em São Paulo prova que o bloco
  ainda pega. `federalAt` devolve `fcdf` nulo fora do DF: a conta independente segue a mesma regra.
- **Um teste que varre o repositório (`git ls-files`) não vê o próprio arquivo antes do `git add`:** o teste de G1 passou aqui e
  falhou no `ci`, porque achou no próprio código o número que o seu controle planta. Rodar depois do `git add`, e o teste pula o
  próprio arquivo.
- **`cmd | tail -1 && git commit --amend && git push` sobe um teste vermelho:** o código da cadeia é o do `tail` (#98). Gravar a saída
  num arquivo, guardar `$?` e só então seguir.
- **Dependabot:** os commits dele não levam `Signed-off-by`, então o `dco` os recusa (Q98, rascunho #96). O Dependabot também não lê
  `deploy/staging/deploy.yml`, que roda no repositório `Brasil-Imposto/staging`; o `test_workflows.py` confere que ele segue fixado.
- **Citação que não fecha no registro:** `\(\*"[^)]*?"\*[,;]` acha uma citação seguida de texto antes do `"*)`. A D166 tinha uma, e o
  padrão do `publish-decisions.py` apagou a D167 inteira do registro público até a citação ser corrigida; duas citações seguidas no
  mesmo parêntese, `(*"a"*; *"b"*)`, são inofensivas (D69, D77, D130, D134, D157, D159 conferidas palavra por palavra).
- **Organização no GitHub** (D173: a exigência de 2FA fica desligada)**:** exigir 2FA não tem API e tira da organização quem não tem 2FA (`orgs/<org>/members?filter=2fa_disabled`
  lista antes); `members_can_create_repositories` tem (`PATCH orgs/<org>`).
- **A chave do Web3Forms é ligada a uma caixa de entrada e serve a mais de um site** (D168): copiada da página publicada do outro
  site por script, sem aparecer na saída de nenhum comando.
- **Prévia de perguntas:** `render-doc.py` sem nenhuma seção `##` dá `class="lead"` a todo parágrafo; as linhas "Recommended" saem
  como `<p><b>`, que o passo depois troca por `p.rec`. A prévia fica em `docs/superpowers/previews/` (fora do git), a fonte em
  `private/questions/`.

### Rodadas 1 e 2 respondidas, produção em lote e a primeira contribuição de fora (2026-10-26, D172 a D194)

- **O registro público sai do privado pelo gerador:** `docs/superpowers/tools/publish-decisions.py` escreve `docs/decisions/README.md`
  a partir de `private/decisions-original.md` (sem as citações). Editar os dois à mão funcionou, mas o gerador é o caminho; numa
  worktree, copiar o arquivo privado para `private/` dela antes de rodar (o `private/` não vai ao git). Uma linha acrescentada acima
  da tabela de decisões desloca os índices calculados antes: D183 a D186 entraram antes de D182 assim; conferir a ordem de D1 em
  diante depois de cada inserção.
- **Promoção por tarefa e o `dco`:** o commit de squash do `staging` sai com o e-mail principal da conta como autor, e o `dco` de um
  pull request de tarefa para a `main` quer o autor igual à assinatura. No cherry-pick, `commit --amend --author` com o endereço
  noreply do mantenedor (o #132 falhou antes disso). **Exceção:** o commit de quem contribui de fora mantém o autor dele (o do #124
  já vem com o autor igual à assinatura).
- **Pull request de fork:** os workflows de quem contribui pela primeira vez esperam aprovação (`gh api -X POST
  repos/<repo>/actions/runs/<id>/approve`; os presos: `actions/runs?status=action_required`). A configuração automática do CodeQL
  não analisou o fork e a regra `code_scanning` do `staging` barrou o merge: daí o `codeql.yml` (D193). Para refazer as verificações
  de um fork, fechar e reabrir uma vez só, e só depois que o merge commit do pull request (`refs/pull/<n>/merge`) já tiver a mudança
  de workflow da base; repetir vira ruído público na página de quem contribuiu (o autor perguntou por quê).
- **A regra do CodeQL só barra o alerta que o pull request traz:** os 24 alertas altos já abertos não barram nada. Um regex de tags
  HTML vira `py/bad-tag-filter` (alto) mesmo lendo um arquivo nosso: ler o arquivo linha a linha (`build-site.py`, `script_tags`).
- **Provas do `pages.yml` sem tocar a produção:** o ambiente `github-pages` só publica da `main`, então um disparo num ramo monta e
  sobe o artefato e tem o deploy recusado. O grupo de concorrência `pages` cancela a execução anterior: dois disparos seguidos, a
  segunda cancela a primeira (rodar um de cada vez). `gh release create --target` quer o nome do ramo ou o SHA inteiro.
- **Copiar um arquivo de um ramo para outro repositório:** `git fetch` antes de `git show origin/<ramo>:<arquivo>`; o PR #2 do
  `Brasil-Imposto/staging` levou a fonte antiga por causa de uma referência local parada.
- **Chave de funcionalidade para tirar algo que já está na produção (`rede`, #131):** a chave só acrescenta; a página versionada é a
  produção byte a byte. Então o construtor deixa a parte fora da página publicada, `build-site.py` a acrescenta no staging pelas
  âncoras, e o cabeçalho e o rodapé (`site_chrome.py`) seguem a chave. Duas chaves na mesma âncora: a ordem do dicionário decide a
  ordem das folhas de estilo; conferir o staging byte a byte contra o de antes.
- **Interface:** uma regra `display` de classe vence o atributo `hidden` (a gaveta ficava sempre aberta): `[hidden] { display: none }`
  explícito. O cabeçalho do site está no z-index 1000; camadas por cima, 1100.
- **Rodada de prévia da Início:** cada página carrega cerca de 91 MB de dados; seis iframes dela travam o navegador. Capturas mais
  um link para abrir cada opção ao vivo. Um `#id` no `src` de um iframe rola a página de fora também: rolar só dentro do iframe.
- **Controle que não pousou:** a gaveta plantada ficou sob o próprio fundo, e os cliques caíram no fundo; a ordem da cota passou com
  24 pessoas sem cota (valores iguais). Um controle tem de falhar pelo motivo plantado.
- **A verificação `visible-text` (#154) compara commits:** para rodar `visible-text-check.py` na máquina, fazer o commit antes; com
  mudança só na árvore de trabalho ela pega o caminho curto. Um controle plantado num construtor regera as páginas versionadas:
  rodar os construtores de novo depois de tirar o plantio.
- **O `.gitignore_global` desta máquina ignora `package-lock.json`:** o lock de `docs/superpowers/tools/` precisa de `git add -f`, como
  o de `site/`.
