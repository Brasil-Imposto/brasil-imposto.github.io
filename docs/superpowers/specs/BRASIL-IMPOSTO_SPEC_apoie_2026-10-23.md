# Spec: o botão Apoie e a janela de apoio

English summary: the "Apoie" button and its modal on the three published pages, built switched off. Every value still missing
(the addresses, the Sponsors page, the cap, the return threshold, the project e-mail) lives in `data/support.json`; the button
renders only when the apoie switch of `data/features.json` is on for the build (spec staging), and the build refuses it in
production without the contact form's access key, and a live channel with any value missing or any address in the wrong format. The texts are the ones the maintainer approved, word for word. Open points come
back as questions at the end.

Status: **aprovada pelo mantenedor em 2026-10-23** (desenho e todos os textos, na mensagem que pediu esta construção), com base em
D123, D124, D152, D155 e D156 (D155 e D156 estão no registro local de decisões, ainda não publicado). Construída desligada. **A seção 9 (rodada 3) foi aprovada pelo mantenedor em 2026-10-28 (D203).**

## 1. Portões dos canais de pagamento

O agente não decide nenhum destes. Desde 2026-10-23 (seção 8), eles valem para cada canal de pagamento ir de `"soon"` para
`"live"`; o botão e o formulário de contato vão ao ar antes, com a chave `apoie` de `data/features.json` ligada na produção e a
chave do formulário, pela mão do mantenedor.

1. **D123:** o pedido só vai ao ar depois do 2º turno da eleição (2026-10-25).
2. **D125 a D127:** toda tela lê o livro de fluxos, toda garantia passa, nenhuma estimativa na tela. O ponto em aberto é a
   estimativa do DF (D146), pergunta Q41.
3. **Todo valor do canal preenchido.** O teste `pipelines/tests/test_support.py` e a construção das páginas (`site_chrome.parts`)
   recusam um canal `"live"` com qualquer valor vazio ou endereço fora do formato da rede, e a chave `apoie` ligada na produção
   sem a chave do formulário.

## 2. O arquivo de dados: `data/support.json`

Chaves em inglês. Hoje tudo vazio. Se uma montagem leva o botão é a chave `apoie` de `data/features.json` (spec de staging,
seção 2), que substituiu o campo `enabled` deste arquivo.

| Chave | Hoje | O que é |
|---|---|---|
| `maintainer_cap_brl` | `null` | o teto do valor fixo da manutenção, por mês, em reais |
| `contact_form` | `{"provider": "web3forms", "access_key": null}` | a chave pública do Web3Forms para a caixa do projeto; nenhum e-mail na página (D124, seção 8) |
| `sponsors` | `status: "soon"`, `sponsors_url: null`, `fiscal_host: {"name": "Open Source Collective", "url": null}` | o canal do GitHub Sponsors; `sponsors_url` será `https://github.com/sponsors/Brasil-Imposto` |
| `crypto` | `status: "soon"`, `unidentified_return_above_brl: null`, 5 grupos com `address: null` | o canal de cripto: o valor acima do qual doação de carteira sem identificação é devolvida, e um endereço por grupo, com as redes, o explorador de cada rede e as moedas |

Os grupos de endereço, as redes e as moedas:

| Grupo (formato) | Rede | Moedas | Explorador |
|---|---|---|---|
| Bitcoin (`bc1`, `1` ou `3`) | Bitcoin | BTC | mempool.space, `https://mempool.space/address/{address}` |
| EVM, um endereço `0x` (`0x` e 40 hexadecimais) | Ethereum | ETH; USDT e USDC (ERC-20) | Etherscan, `https://etherscan.io/address/{address}` |
| | BNB Smart Chain | BNB, USDT e USDC (BEP-20) | BscScan, `https://bscscan.com/address/{address}` |
| Solana (base58, 32 a 44) | Solana | SOL; USDT e USDC (SPL) | Solscan, `https://solscan.io/account/{address}` |
| Tron (`T` e 33 em base58) | Tron | USDT (TRC-20) | Tronscan, `https://tronscan.org/address/{address}/transactions` |
| XRP Ledger (`r` e base58) | XRP Ledger | XRP | XRPScan, `https://xrpscan.com/account/{address}` |

O padrão de endereço de cada explorador foi conferido nas páginas que os buscadores indexam de cada um (2026-10-23); esta sessão
não alcança os exploradores diretamente (ver as perguntas).

## 3. O botão (em `site_chrome.py`, só com a chave `apoie` ligada na montagem)

- Uma pílula verde (#12803F), texto branco "Apoie", com um baú dourado (preenchimento #F9BE2A, contorno escuro #8A6A00 e um
  cadeado pequeno). Sem coração.
- No computador, depois dos links das páginas; no celular, ao lado do "Menu".
- Até 380 px, o Menu mostra só o ícone (o nome "Menu" fica para leitores de tela), para o cabeçalho caber em 320 px.

## 4. A janela (um painel, aberto pelo botão)

Acima do cabeçalho, como as fichas corrigidas em #43 (camada 1100, a página travada por trás). O botão de fechar fica fixo enquanto
o painel rola. Escape e um clique fora fecham; o foco volta para o botão. Nenhum número do livro-caixa por enquanto (nada entrou
ainda).

### 4.1 Vista principal, nesta ordem, com os textos exatamente assim

1. O logo, e então "Apoie o Brasil-Imposto".
2. "O Brasil-Imposto mostra, com dados oficiais e a fonte de cada número, para onde vai o imposto pago no Brasil. É apartidário e
   de código aberto. O seu apoio paga duas coisas, e nada além delas: o trabalho de quem desenvolve o projeto e a infraestrutura
   que mantém os dados corretos e no ar."
3. "Para onde vai o dinheiro": uma barra fina em duas cores (verde, azul) como legenda, e duas colunas:
   - "1. Desenvolvedores": "Quem entrega trabalho aceito no repositório. Cada tarefa paga é uma issue com o valor em reais
     publicado antes de o trabalho começar, e o pagamento sai quando o pull request entra no site. A pessoa mantenedora recebe um
     valor fixo por mês para revisar, publicar e manter o projeto, com teto de {maintainer_cap_brl}."
   - "2. Infraestrutura": "O custo real de cada mês, com a nota de cada gasto: hoje, as ferramentas de inteligência artificial
     usadas para coletar e conferir os dados; depois, servidor e banco de dados, quando o site precisar. O site é hospedado de
     graça no GitHub Pages."
4. Um quadro "Como cada mês é dividido": "1. Primeiro, a infraestrutura do mês, pelo custo real. 2. Com o restante, as tarefas
   pagas que entraram no mês, pelo valor que estava publicado na issue. 3. Depois, o valor fixo da manutenção, até o teto. 4. O que
   ficar fica guardado para os meses seguintes, e o saldo aparece no livro-caixa." e, abaixo: "Não pagamos por número de commits,
   de linhas ou de pull requests: pesquisar e conferir uma fonte oficial pode levar dias e virar poucas linhas. O valor de cada
   tarefa é decidido antes, à vista de todos."
5. "Como apoiar": dois cartões lado a lado (um sobre o outro no celular), cada um abrindo a sua vista dentro da janela:
   - GitHub Sponsors (a marca do GitHub): "Em dólar, uma vez pela sua conta do GitHub." Botão "Apoiar pelo GitHub
     Sponsors".
   - Cripto (uma moeda): "Sete moedas: BTC, ETH, SOL, USDT, USDC, XRP e BNB. Cada endereço é público, com o link do explorador."
     Botão "Apoiar com cripto".
6. "Antes de apoiar", uma lista:
   - "Quem recebe: o GitHub Sponsors paga ao Open Source Collective, organização sem fins lucrativos que guarda o dinheiro do
     projeto e publica cada entrada e cada despesa; as carteiras de cripto são do projeto e ficam com a pessoa mantenedora."
   - "O que o apoio compra: trabalho e infraestrutura. Não compra conteúdo: ninguém que apoia muda o que o site mostra, e as regras
     de neutralidade valem para todos."
   - "De quem não aceitamos: partido, candidato e ocupante de cargo eletivo. Toda fonte acima de 5% da receita do ano é publicada
     com o nome."
   - "Tudo o que entra e tudo o que sai é publicado, mês a mês, no livro-caixa do projeto."
   - "Em reais: doação em cripto ou em dólar entra no livro-caixa em reais, pela cotação do dia em que chegou."
   - "Imposto de renda: a doação não é dedutível; o projeto não é uma entidade beneficente."
7. A vista de contato (D124) abre pela linha em destaque logo depois dos cartões (seção 8). Sem `contact_form.access_key`, ela
   não existe.

### 4.2 Vista "Apoiar pelo GitHub Sponsors" (com "Voltar")

Três passos: "Abra a página do Brasil-Imposto no GitHub Sponsors." / "Escolha um valor, uma vez ou todo mês." / "Pague com a forma
de pagamento da sua conta do GitHub." Os fatos: "Em dólar. O GitHub não cobra taxa de quem apoia por uma conta pessoal; o apoio
feito por uma organização tem taxa de até 6%. O dinheiro vai para o Open Source Collective, que fica com 10% para guardar e prestar
contas do dinheiro do projeto." E o botão "Abrir o GitHub Sponsors", para `sponsors_url`.

### 4.3 Vista "Apoiar com cripto" (com "Voltar")

- Sete botões de moeda: BTC, ETH, SOL, USDT, USDC, XRP, BNB. Escolher uma mostra só as redes dela; cada linha com o nome da rede,
  o endereço, "Copiar" e o link do explorador. USDT mostra quatro redes e USDC três, com "Escolha uma das redes acima ao enviar.".
- O aviso: "Confira a rede antes de enviar. Uma moeda enviada por uma rede que não está na lista se perde, e o projeto não consegue
  devolver."
- A regra: "Doação acima de {unidentified_return_above_brl} vinda de carteira sem identificação é devolvida para a carteira de
  origem."
- Um painel de moeda escondido fica escondido de verdade: uma regra `display` na classe do painel venceria o atributo `hidden`,
  então a folha de estilo da janela esconde todo `[hidden]` dentro dela com `!important`.

### 4.4 Vista de contato (D124)

Nome, e-mail e mensagem; "O que você gostaria de ver no Brasil-Imposto? Conte para a gente. Lemos todas as mensagens e usamos as
ideias para planejar as próximas atualizações."; "Seu nome e e-mail servem só para responder você." Com um campo escondido contra
robôs (honeypot), como D124 pede. O envio é pelo Web3Forms (seção 8).

## 5. Como foi construído

- `data/support.json`: os valores (seção 2).
- `docs/superpowers/tools/support_data.py`: lê o arquivo (ou o de `BI_SUPPORT_JSON`, para um teste local nunca enviado ao git),
  confere a estrutura sempre, a chave do formulário quando `apoie` está ligada na produção e os valores de cada canal `"live"`,
  e formata reais.
- `docs/superpowers/tools/apoie.py`: o botão, a janela, o estilo e o código, com os textos aprovados.
- `docs/superpowers/tools/site_chrome.py`: `parts()` acrescenta o botão, a janela, o estilo e o código só com a chave `apoie`
  ligada no perfil da montagem. A
  janela fica fora de `<header>`, porque o `backdrop-filter` da barra prenderia um filho fixo dentro dela. O código entra no próprio
  `<script id="bi-chrome-js">`, o único que o carregamento do mapa de Início roda na hora (`map_loader.py`), então o botão funciona
  enquanto os dados do mapa carregam.
- `pipelines/tests/test_support.py`: o arquivo enviado desligado e vazio; as sete moedas e as redes de cada uma; os exploradores;
  com a chave ligada, cada valor vazio falha e cada endereço errado plantado falha; desligado, o cabeçalho é o de antes; ligado, o
  botão, os textos e nenhum e-mail na página.
- `docs/superpowers/tools/apoie-check.cjs`: a sonda da janela no navegador (seção 6), com `--control`.

## 6. Provas

- **Desligado:** os construtores refazem as três páginas byte a byte iguais às da `main`; a sonda de texto visível dá 100 de 100;
  nenhum botão no cabeçalho.
- **Ligado, numa construção de teste** (endereços falsos mas bem formados, nunca enviados ao git): `site-check.cjs` em 1440, 420 e
  320 px, com `--control`; `apoie-check.cjs`, que abre a janela, cada vista e cada moeda, e confere: o cabeçalho cabe; o botão de
  fechar clicável no alto e depois de rolar até o fim; só o painel da moeda escolhida exibido (o `display` calculado, não o
  atributo), com as suas redes; sem rolagem lateral; Escape, clique fora e foco de volta. O controle planta uma falha para cada
  checagem, e todas têm de falhar.

## 7. Perguntas ao mantenedor

1. **O envio do formulário (Q40).** Respondida pelo mantenedor em 2026-10-23: Web3Forms, com a chave pública em
   `contact_form.access_key` (seção 8).
2. **Textos que esta mensagem não trouxe e a construção precisou:** os rótulos do formulário ("Nome", "E-mail", "Mensagem") e o
   botão "Enviar"; o nome de cada explorador como texto do link (mempool.space, Etherscan, BscScan, Solscan, Tronscan, XRPScan);
   "Fechar" como nome do botão de fechar para leitores de tela (o mesmo do Menu aberto). Ficam assim ou têm outro texto?
3. **"Copiar" depois de copiar:** o botão fica verde por 1,8 segundo, sem texto novo. Basta, ou entra um texto ("Copiado")?
4. **Os exploradores:** o padrão de cada um veio das páginas indexadas do próprio explorador; esta sessão não alcança os sites.
   Vale abrir um endereço real em cada um antes de ligar o botão. No Tronscan o padrão indexado termina em `/transactions`.
5. **A sonda de texto publicado:** `visible-text-probe.cjs --audit` conta "Apoie" e "Fale com a gente" como controles que o site
   publicado nunca mostra. Ao ligar o botão, essa regra muda junto; fica para a decisão de ligar.
6. **O registro de decisões:** D155 e D156 estão no registro local. Q33 a Q39 (D123) parecem respondidas por esta mensagem (o
   teto vira `maintainer_cap_brl`; o pagamento de outros desenvolvedores por tarefa paga em issue; a sobra guardada para os meses
   seguintes; cotação do dia em reais e as sete moedas; o valor de devolução vira `unidentified_return_above_brl`; o Open Source
   Collective como quem recebe). Fecha essas perguntas no registro?

## 8. Produção: o botão e o formulário no ar, os canais em breve (mantenedor, 2026-10-23)

Decisão do mantenedor: o botão Apoie e o formulário "Fale com a gente" vão ao ar agora, para quem quiser apoiar de outro jeito falar
com a pessoa mantenedora já; o GitHub Sponsors e a cripto ficam fechados até os portões deles passarem (D123, D125 a D127 e os
valores de `data/support.json`).

- **Cada canal tem um estado** (`sponsors.status` e `crypto.status`): `"soon"` mostra o cartão com a etiqueta "Em breve";
  `"live"` pede todos os valores do canal preenchidos (o teste de endereços e valores vale para `"live"`; com qualquer canal
  `"live"`, o teto `maintainer_cap_brl` também é exigido).
- **A chave `apoie` pode ser ligada na produção com os dois canais em `"soon"`**, com ou sem `contact_form.access_key` (D162): sem
  ela, a vista de contato fica fora da página; preenchida, é um UUID (um endereço de e-mail ali é recusado). A chave do formulário fica `null` até a sessão local escrevê-la; a
  produção liga `apoie` em `data/features.json`.
- **Valores que faltam:** a produção nunca mostra "a definir". A frase que depende de um valor `null` sai (o teto da manutenção, o
  valor de devolução da cripto). O staging segue a mesma regra, e desenha o formulário mesmo sem a chave: um envio mostra a linha
  de erro e não faz pedido (spec de staging, seção 2).
- **"Como apoiar":** os dois cartões lado a lado (um sobre o outro no celular), cada um com "Em breve" ao lado do título e sem nada
  para clicar enquanto o canal estiver em `"soon"`: sem botão, sem vista, sem endereço. Sob GitHub Sponsors: "Em dólar, uma vez ou
  todo mês, pela sua conta do GitHub." Sob Cripto: "Sete moedas: BTC, ETH, SOL, USDT, USDC, XRP e BNB."
- **Logo depois dos cartões**, uma linha em destaque com o botão que abre a vista de contato: "Quer apoiar de outro jeito, ou falar
  com a gente? Escreva por aqui." Botão: "Fale com a gente". O link "Fale com a gente" do fim da vista principal sai, porque a
  linha faz o mesmo.
- **"Antes de apoiar"** fica só com o que vale sem canal aberto: "O que o apoio compra", "De quem não aceitamos", "Tudo o que entra
  e tudo o que sai é publicado, mês a mês, no livro-caixa do projeto.", "Em reais" e "Imposto de renda". "Quem recebe" volta quando
  um canal abrir.
- **O formulário (D124):** Nome, E-mail e Mensagem, com os textos de 4.4. Enviado por JavaScript (fetch), em JSON, para
  `https://api.web3forms.com/submit`, com `access_key`, `name`, `email`, `message`, `subject` "Brasil-Imposto: mensagem pelo
  site", `from_name` "Site Brasil-Imposto" e `botcheck`. O honeypot é a caixa `botcheck`, escondida por CSS: marcada, nada sai.
  Envio a menos de 3 segundos da abertura da vista é descartado. Sucesso é a resposta 200 com `success: true`.
- **Estados:** enquanto envia, o botão diz "Enviando..." e fica desativado; no sucesso o formulário dá lugar a "Mensagem enviada.
  Respondemos pelo e-mail que você informou."; em qualquer erro, "Não foi possível enviar agora. Tente de novo em alguns minutos.",
  com os campos mantidos. Campos obrigatórios e e-mail válido conferidos antes do envio, com a mensagem sob o campo.
- **Nenhum endereço de e-mail** na página, no repositório, num commit ou num pull request: `docs/superpowers/tools/email-scan.py`
  procura o padrão, com um endereço plantado como controle.
- **Provas:** a montagem da produção com a chave `apoie` ligada e uma chave falsa do formulário (só no teste) e `apoie-check.cjs`
  em 1440, 420 e 320 px,
  com `--control` (seção 6); desligado, as três páginas iguais às da `main`.


## 9. Rodada 3 (2026-10-28): o Pix pela Vakinha e a divisão pelas contribuições (D198 a D202)

Status: **aprovada pelo mantenedor em 2026-10-28 (D203).** A prévia da rodada, com todas as respostas aplicadas, é
`docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_apoie-r3_2026-10-28.html` (gerador local `private/apoie/build_apoie_r3.py`, sobre
uma cópia da página publicada em 2026-10-28). Pesquisa que levou ao Pix pela Vakinha:
`docs/research/BRASIL-IMPOSTO_RESEARCH_doacao-rapida_2026-10-28.md`. Nada desta seção vai para o código antes da aprovação (D185).

**Quem faz (D164):** a sessão local de 2026-10-28. Conferido em 2026-10-28: nenhuma issue, pull request ou ramo aberto de outra sessão
trata do Apoie.

### 9.1 `data/support.json`

- **Sai `maintainer_cap_brl`** (D202: a pessoa mantenedora não tem valor fixo nem teto). `support_data.problems` deixa de exigi-lo, e
  a frase do teto (`DEVELOPERS_CAP`) sai de `apoie.py`.
- **Entra o canal `pix`**, o primeiro dos três:

| Chave | Hoje | O que é |
|---|---|---|
| `pix.status` | `"soon"` | `"soon"` mostra o cartão com "Em breve" e nada para clicar; `"live"` abre a vista do Pix |
| `pix.provider` | `"Vakinha"` | o nome da plataforma, escrito nos textos |
| `pix.campaign_url` | `null` | o endereço da vaquinha do Brasil-Imposto; com `"live"`, precisa ser `https://` no domínio `vakinha.com.br` |
| `pix.bank_screen_name` | `null` | o nome que o app do banco mostra antes de confirmar o Pix, conferido pelo mantenedor sem pagar (D199, item 3) |

O teste recusa `pix` em `"live"` com qualquer desses valores vazio, ou com o endereço fora do formato.

### 9.2 Portões do Pix

O cartão do Pix fica "Em breve" até: a conta na Vakinha existir (o mantenedor ainda não se cadastrou), a vaquinha estar criada
(`campaign_url`), o nome da tela do banco estar conferido (`bank_screen_name`) e o portão da seção 1 passar. Abrir um canal antes de
D125 a D127 é a mesma pergunta ainda aberta para a cripto (D158), e vale igual para o Pix.

### 9.3 Vista principal: os textos novos, exatamente assim

Na ordem em que aparecem:

- **Abertura:** "O Brasil-Imposto mostra, com dados oficiais e a fonte de cada número, para onde vai o imposto pago no Brasil. É
  apartidário e de código aberto. O seu apoio paga duas coisas, e nada além delas: a infraestrutura que mantém os dados corretos e no
  ar e o trabalho de quem desenvolve o projeto." (a infraestrutura primeiro, D201)
- **Título:** "Para onde vai o dinheiro do apoio" (D200). A barra fina fica azul e depois verde, na ordem das colunas.
- **Coluna "1. Infraestrutura"** (primeira, D201): "O custo real de cada mês, que muda de um mês para outro, com a nota de cada gasto:
  hoje, as ferramentas de inteligência artificial usadas para coletar e conferir os dados; depois, servidor e banco de dados, quando o
  site precisar. O site é hospedado de graça no GitHub Pages. É a primeira coisa paga com o apoio."
- **Coluna "2. Desenvolvedores":** "Quem entrega trabalho aceito no repositório, inclusive a pessoa mantenedora. O que sobra de cada
  mês, depois da infraestrutura, é dividido entre quem contribuiu pelo peso de cada contribuição aceita (1, 2 ou 3, escrito no pull
  request antes do merge), e cada pagamento é publicado no livro-caixa."
- **"Como apoiar":** três cartões do mesmo tamanho, Pix, GitHub Sponsors e Cripto, em três colunas acima de 820 px e um sobre o outro
  abaixo disso (opção A, D200). O do Pix: a marca "R$" num quadrado verde, o título "Pix" e "Em reais, qualquer valor, com Pix ou
  cartão, pela vaquinha do Brasil-Imposto."; em `"soon"`, a etiqueta "Em breve" ao lado do título e nenhum botão; em `"live"`, o
  botão "Apoiar com Pix". "Brasil-Imposto" nunca quebra no hífen.
- **A linha do "Fale com a gente"**, logo depois dos cartões, como hoje.
- **O quadro "Como cada mês é dividido"**, depois dessa linha (D200), com quatro itens (D202): "Primeiro, a infraestrutura do mês, pelo
  custo real, que muda de um mês para outro." / "O resto vai para quem contribuiu, inclusive a pessoa mantenedora, dividido pelo peso
  de cada contribuição aceita no mês (1, 2 ou 3)." / "Nas primeiras divisões, contam todas as contribuições aceitas desde o início do
  projeto, em 25/09/2026, de todas as pessoas, até esse saldo ser pago; depois, só as do mês." / "Num mês sem contribuição aceita, o
  resto fica guardado para os meses seguintes, e o saldo aparece no livro-caixa."
- **Sai** o parágrafo "Não pagamos por número de commits, de linhas ou de pull requests..." (D200).
- **"O que o apoio compra":** "trabalho e infraestrutura. Junto com a doação, você pode pedir pelo "Fale com a gente" uma
  funcionalidade que ainda não existe; os pedidos entram no planejamento das próximas atualizações. Nenhum apoio muda um número: todo
  número vem da fonte oficial, e as regras de neutralidade valem para todos." (D201)
- **"Quem recebe"** continua só com algum canal aberto, e passa a juntar uma parte por canal aberto, nesta ordem, separadas por ponto e
  vírgula: Pix, "o Pix e o cartão vão para a Vakinha, que repassa o valor à pessoa mantenedora; cada repasse é publicado no
  livro-caixa do projeto" (D199); GitHub Sponsors, "o GitHub Sponsors paga ao {host}, organização sem fins lucrativos que guarda o
  dinheiro do projeto e publica cada entrada e cada despesa"; cripto, "as carteiras de cripto são do projeto e ficam com a pessoa
  mantenedora".
- **As outras linhas de "Antes de apoiar"** ficam como estão.

### 9.4 Vista "Apoiar com Pix" (com "Voltar"), só com `pix.status` em `"live"`

Três passos: "Abra a vaquinha do Brasil-Imposto na Vakinha." / "Digite o valor que quiser." / "Pague com Pix, pelo app do seu banco, ou
com cartão." Os fatos: "A Vakinha recebe a doação e repassa o valor ao projeto. Na tela do seu banco, o Pix aparece para
{bank_screen_name}. A Vakinha fica com 6,4% mais R$ 0,50 de cada doação, e cada repasse entra no livro-caixa do projeto, com o extrato da
Vakinha." E o botão "Abrir a vaquinha", para `campaign_url`, numa aba nova. A taxa é a da página da Vakinha lida em 2026-10-28; se ela
mudar, o texto muda junto.

### 9.5 Como construir

- `support_data.py`: o canal `pix` na estrutura e nos valores de `"live"`; sem `maintainer_cap_brl`.
- `apoie.py`: os textos e a ordem de 9.3, o cartão e a vista do Pix, o quadro depois do contato, sem o parágrafo e sem a frase do teto,
  "Quem recebe" por canal.
- `pipelines/tests/test_support.py`: a estrutura do `pix`; `"live"` sem `campaign_url` ou sem `bank_screen_name` falha; controles
  plantados: um endereço `http://` e um de outro domínio, cada um tem de falhar; a ordem da vista principal (infraestrutura,
  desenvolvedores, cartões, contato, quadro, "Antes de apoiar"); os textos que saíram não aparecem, com a construção de antes como
  controle, onde eles aparecem.
- `docs/superpowers/tools/apoie-check.cjs`: o cartão do Pix em "Em breve" sem botão; três colunas em 1440 px e uma em 420 e 320 px;
  numa construção de teste com o Pix em `"live"`, a vista abre, o link é o de `campaign_url`, Escape e o foco de volta, com `--control`.
- A comparação do texto visível no `ci` (#154) vai mostrar a diferença dos textos do modal: esperada, e anotada no pull request.

### 9.6 Provas

- A construção da produção, com o Pix em `"soon"`: capturas em 1440, 420 e 320 px, olhadas; `apoie-check.cjs` com `--control`.
- Uma construção de teste com o Pix em `"live"` (endereço e nome falsos mas bem formados, nunca enviados ao git): a vista do Pix nas três
  larguras.

### 9.7 Fora desta seção

- A rodada das regras do dinheiro (D170): o portão dos canais, `unidentified_return_above_brl`, por onde sai o pagamento de quem contribui
  (Q34) e a cotação que converte cada doação em reais (Q36).
- A regra dos pesos escrita no `GOVERNANCE.md`, as etiquetas de peso no repositório e o peso dos pull requests já aceitos desde
  2026-09-25, para a aprovação do mantenedor (D201, D202): tarefa própria.
- A ida à produção: no próximo lote (D192).
