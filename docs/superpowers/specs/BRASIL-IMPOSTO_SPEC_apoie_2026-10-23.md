# Spec: o botão Apoie e a janela de apoio

English summary: the "Apoie" button and its modal on the three published pages, built switched off. Every value still missing
(the addresses, the Sponsors page, the cap, the return threshold, the project e-mail) lives in `data/support.json`; the button
renders only when the apoie switch of `data/features.json` is on for the build (spec staging), and the build refuses it in
production without the contact form's access key, and a live channel with any value missing or any address in the wrong format. The texts are the ones the maintainer approved, word for word. Open points come
back as questions at the end.

Status: **aprovada pelo mantenedor em 2026-10-23** (desenho e todos os textos, na mensagem que pediu esta construção), com base em
D123, D124, D152, D155 e D156 (D155 e D156 estão no registro local de decisões, ainda não publicado). Construída desligada. **A seção 9 (rodada 3) foi aprovada pelo mantenedor em 2026-10-28 (D203).** **A seção 10 (a cripto pronta para a produção) foi aprovada em 2026-10-29 (D205).**

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

Chaves em inglês. Se uma montagem leva o botão é a chave `apoie` de `data/features.json` (spec de staging,
seção 2), que substituiu o campo `enabled` deste arquivo.

| Chave | Hoje | O que é |
|---|---|---|
| `contact_form` | `{"provider": "web3forms", "access_key": null}` | a chave pública do Web3Forms para a caixa do projeto; nenhum e-mail na página (D124, seção 8) |
| `sponsors` | `status: "soon"`, `sponsors_url: null`, `fiscal_host: {"name": "Open Source Collective", "url": null}` | o canal do GitHub Sponsors; `sponsors_url` será `https://github.com/sponsors/Brasil-Imposto` |
| `crypto` | `status: "live"`, 5 grupos com endereço, `status` em cada rede (o XRP Ledger em `"soon"`) | o canal de cripto: um endereço por grupo, com as redes, o explorador de cada rede e as moedas |

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
3. "Para onde vai o dinheiro do apoio": os textos da seção 9.3.
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

O Open Source Collective recusou o projeto como fiscal host em 2026-11-01 (D214). O GitHub Sponsors aceita uma organização no Brasil recebendo direto numa conta bancária; quem recebe está em aberto, e os textos abaixo que citam o Open Source Collective mudam antes de o canal abrir.

Três passos: "Abra a página do Brasil-Imposto no GitHub Sponsors." / "Escolha um valor, uma vez ou todo mês." / "Pague com a forma
de pagamento da sua conta do GitHub." Os fatos: "Em dólar. O GitHub não cobra taxa de quem apoia por uma conta pessoal; o apoio
feito por uma organização tem taxa de até 6%. O dinheiro vai para o Open Source Collective, que fica com 10% para guardar e prestar
contas do dinheiro do projeto." E o botão "Abrir o GitHub Sponsors", para `sponsors_url`.

### 4.3 Vista "Apoiar com cripto" (com "Voltar")

- Sete botões de moeda (BTC, ETH, SOL, USDT, USDC, XRP, BNB), cada um com o ícone do token à esquerda do nome (D206). Uma moeda sem rede
  aberta fica na fila, apagada, com "Em breve", e não abre nada (o XRP hoje, D206).
- Escolher uma moeda mostra só a seção "Escolha a Rede", com os botões das redes dela, nenhum pré-escolhido (USDT quatro, USDC três). O
  endereço, "Copiar" e o link do explorador aparecem só depois de tocar numa rede (D211); o desenho completo com o envio está na spec
  `docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_cripto-no-site_2026-10-29.md`. O site hoje ainda mostra todas as redes ao mesmo tempo.
- O aviso: "Confira a rede antes de enviar. Uma moeda enviada por uma rede que não está na lista se perde, e o projeto não consegue
  devolver."
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
  `"live"` pede todos os valores do canal preenchidos (o teste de endereços e valores vale para `"live"`).
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
  abaixo disso (opção A, D200). D220 muda isso na fase 2 da spec de segurança: o cartão do GitHub Sponsors sai e o da Cripto vem antes do
  Pix, enquanto o Pix não está disponível, em duas colunas (uma no celular). O do Pix: a marca "R$" num quadrado verde, o título "Pix" e "Em reais, qualquer valor, com Pix ou
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

- A rodada das regras do dinheiro (D170): por onde sai o pagamento de quem contribui
  (Q34) e a cotação que converte cada doação em reais (Q36).
- A regra dos pesos escrita no `GOVERNANCE.md`, as etiquetas de peso no repositório e o peso dos pull requests já aceitos desde
  2026-09-25, para a aprovação do mantenedor (D201, D202): tarefa própria.
- A ida à produção: no próximo lote (D192).

## 10. A cripto pronta para a produção (D204)

Status: **aprovada pelo mantenedor em 2026-10-29 (D205) e construída no #163 em 2026-10-29 (10.4), com o XRP "Em breve" por rede pela opção A da rodada de prévia (D206).** O XRP fica "Em breve" até o mantenedor mandar o primeiro 1 XRP (D205): `data/support.json` passa a ter um estado por rede, e o botão do XRP em "Em breve" passa por uma rodada de prévia (D185). O teste de verdade na rede (10.2, item 5) é feito pelo mantenedor em todas as moedas e redes, de preferência pela doação dentro do site, que é um pedido novo com sessão e spec próprias (D205). Quem faz (D164): a sessão local de 2026-10-28, nos ramos desta spec (#162) e do
código (#163). Os cinco endereços do projeto já estão em `data/support.json` no #163, conferidos pela soma de verificação de cada rede e na
API pública de cada rede, com a cripto ainda em `"soon"`.

### 10.1 O que muda

- **Sai a regra de devolução** (D204): `crypto.unidentified_return_above_brl` deixa `data/support.json` e `support_data.py`, e a frase
  "Doação acima de ... vinda de carteira sem identificação é devolvida para a carteira de origem." sai da vista da cripto. Qualquer valor de
  qualquer carteira fica.
- **A cripto abre no próximo lote de produção** (D204, D192): `crypto.status` passa a `"live"`. Abrem a vista "Apoiar com cripto" (seção
  4.3), o cartão com "Sete moedas: BTC, ETH, SOL, USDT, USDC, XRP e BNB. Cada endereço é público, com o link do explorador." e a parte da
  cripto em "Quem recebe" (seção 9.3). O Pix continua "Em breve" até o portão dele; o cartão do GitHub Sponsors sai (D220).
- **XRP** (D204): sem compra de reserva. O XRP Ledger só cria a conta quando ela recebe 1 XRP ou mais; antes disso, um envio menor é recusado
  pela rede e o dinheiro fica com quem tentou doar (só a taxa da rede é gasta). A primeira doação de 1 XRP ou mais cria a conta; 1 XRP dela
  fica preso como reserva da rede. Até lá, o XRPScan mostra o endereço como não encontrado.

### 10.2 Testes e proteções antes da produção

Cada teste é escrito antes da mudança e visto falhando (TDD), e cada um tem o seu controle plantado.

1. **Soma de verificação de cada endereço, no `ci`:** `support_data.py` confere, além do formato, a soma de verificação de cada rede:
   bech32 ou bech32m no Bitcoin, EIP-55 no endereço 0x (as letras maiúsculas e minúsculas são a soma), base58check com o byte de versão
   certo na Tron (0x41) e no XRP (0x00, com o alfabeto do XRP), e 32 bytes na Solana. Sem dependência nova: o keccak-256 do EIP-55 em
   Python puro, conferido contra um vetor de teste conhecido. Controle: um caractere trocado em cada endereço tem de falhar.
2. **Os endereços fixados no teste:** um teste guarda os cinco endereços esperados; qualquer mudança em `data/support.json` quebra o `ci`
   até o teste mudar junto, no mesmo pull request. Um endereço nunca muda em silêncio.
3. **A página mostra e copia o que está no arquivo:** `apoie-check.cjs` lê, em cada moeda e rede, o endereço exibido e o que o botão
   "Copiar" põe na área de transferência, e compara com `data/support.json`; confere também o link de cada explorador. Controle: um endereço
   trocado na página tem de falhar.
4. **Nenhum script de fora sem verificação na página com os endereços:** "Como o dinheiro anda" carrega duas bibliotecas de CDN sem hash de
   integridade (d3 no cdnjs, d3-sankey no jsdelivr). Um arquivo adulterado na CDN poderia trocar o endereço que quem doa vê. Elas ganham os
   atributos `integrity` (hash SRI) e `crossorigin`, e um teste recusa script externo sem `integrity` em toda página com o botão Apoie.
   Controle: tirar um hash tem de falhar.
5. **Um teste de verdade na rede** (D205): o mantenedor manda um valor pequeno em cada moeda e cada rede, de preferência pela doação dentro
   do site, e a sessão confere a chegada no explorador e na API de cada rede; o mantenedor confere no celular. O que entra fica no projeto
   e vai ao livro-caixa como doação do mantenedor.
6. **Provas:** as da seção 9.6, mais a vista da cripto aberta em 1440, 420 e 320 px, cada moeda com as suas redes, "Copiar" e os links,
   com `apoie-check.cjs --control`.

### 10.3 Fora desta seção

O livro-caixa que se preenche sozinho com as entradas das carteiras (depois); a carteira física acima de um saldo a definir; código QR dos
endereços.

### 10.4 Como foi construído (2026-10-29, #163)

- **Soma de verificação:** `support_data.address_problem`, sem dependência; vetores do BIP-350, do EIP-55, do Bitcoin Core, da página de contas da Tron e da página de endereços do xrpl.org. O keccak-256 em Python puro bate com o resumo conhecido da entrada vazia e, com o preenchimento do SHA-3, com o `hashlib.sha3_256`. Controle: 5.811 trocas de um caractere nos quatro endereços com soma (Bitcoin, 0x, Tron e XRP), todas recusadas. **A Solana não tem soma de verificação:** uma troca de um caractere continua com 32 bytes (e até um caractere a menos pode continuar com 32); lá quem pega a troca é o endereço fixado no teste (item 2). Um endereço preenchido é conferido em qualquer estado, não só com a cripto aberta.
- **Scripts de fora:** além das duas bibliotecas de "Como o dinheiro anda", a Início carrega sete módulos do three.js pelo mapa de importação (os cinco que o código importa e os dois que o Line2 importa), e a Início do staging carrega o 3d-force-graph (a prévia da Rede, D172). Os três ganharam hash: os atributos nas duas tags, a lista `integrity` no mapa de importação (posta pelo `build-platform-preview.py`; Chrome 127, Firefox 138 e Safari 18 conferem, um navegador mais antigo ignora a lista) e o `data-integrity` que o carregador do mapa repõe. Cada hash foi conferido com o hash que o próprio CDN publica.
- **`apoie-check.cjs`** ganhou duas conferências: `addresses` (nome da rede, endereço mostrado, endereço copiado lido da área de transferência de verdade e link do explorador, em cada moeda e rede) e `sri` (cada script de fora servido como publicado tem de ser aceito, e servido alterado não pode rodar). Nas versões de produção e de staging, todas passam; no controle, todas falham.
- **O estado por rede (D205, D206):** cada rede tem `status`; a cripto está em `"live"` e o XRP Ledger em `"soon"`. Uma moeda sem rede aberta fica na fila, apagada (contorno tracejado), desligada, com "Em breve", sem painel, e a página não leva o endereço dela (opção A da rodada `apoie-xrp-r1`). O texto do cartão "Cripto" fica como aprovado em 10.1 (D208). Cada botão de moeda tem o ícone do token à esquerda do nome (D206, rodada `cripto-envio-r1` aprovada em D208): o conjunto aberto cryptocurrency-icons 0.18.1 (CC0), em `assets/cripto/`, carregado só quando aparece (o do SOL depois virou a marca da Solana, fora do CC0, D213); o XRP apagado leva o ícone em cinza.
- **Dois defeitos achados pelas conferências novas:** o "copiar" dos cartões de casos (`assets/cases.js`) e o "Copiar link" de Os 3 Poderes pegavam todo clique em `[data-copy]` da página, então o "Copiar" da janela copiava só os dígitos do endereço na Início e o link da página em Os 3 Poderes. Os dois passaram a pegar só os próprios botões, e um teste recusa um "copiar" que pega a página inteira.

## 11. Rodada 4 (2026-11-06): a regra pública do pagamento de quem contribui (D230, D231)

Status: **aprovada pelo mantenedor em 2026-11-06 (D233), com a pergunta 11.7 respondida (D232).** Muda a regra da seção 9 (D201 e D202), o texto da coluna
"2. Desenvolvedores" e do quadro "Como cada mês é dividido" (9.3), e a seção "Quem pode doar" do `GOVERNANCE.md`. Nenhum código
antes da aprovação desta seção, e nenhuma tela antes da rodada de prévia dos textos (D185).

**In English:** contributors are paid by a public rule. Each issue gets its weight (1, 2 or 3) from its difficulty label before
anyone works on it; each month the infrastructure is paid first, then the rest is split by the weights of the issues closed that
month, the maintainer included by the same rule; a public script computes the split from GitHub and a public monthly ledger records
every donation, cost and payout. No back pay; unclaimed pay returns to the pool after 6 months; payment details are asked privately,
only when there is money to pay; contributors know they may never be paid. The project says it is open source and non-profit, with
one honest line: it is not yet a registered association, and donations reach the maintainer's wallets.

### 11.1 Por que muda

- Em 2026-11-06, 160 dos 161 pull requests unidos eram do mantenedor (as sessões com IA) e 1 de uma pessoa de fora. Pela regra de
  D201 e D202 (peso no pull request no merge e, nas primeiras divisões, todo o trabalho desde 25/09/2026), quase toda a parte dos
  desenvolvedores das primeiras doações iria para quem escolhe os pesos, e a regra não estava escrita no `GOVERNANCE.md` nem no
  `CONTRIBUTING.md`; o `GOVERNANCE.md` ainda dizia "Hoje o projeto não recebe doação" e mantinha a devolução de cripto que D204 tirou.
- Pesquisa de 2026-11-06 (privada, em `private/research/`): nenhum projeto achado paga a pessoa mantenedora pela mesma divisão de pull
  requests nem paga o passado. Os mais próximos: a **Drips Wave** (a pessoa mantenedora põe a complexidade da issue antes do trabalho,
  100, 150 ou 200 pontos; um fundo dividido pela parte de cada pessoa no ciclo; quem organiza pode descontar pontos por mau uso) e o
  **Actual Budget** (um fundo mensal dividido por pontos que um script público calcula; cada pagamento publicado com o nome no GitHub).
  Os projetos cívicos brasileiros lidos (Querido Diário, Base dos Dados, Serenata, Brasil.IO) não pagam por contribuição.

### 11.2 A regra

1. **O que conta:** uma issue com rótulo de dificuldade, posto antes de alguém começar (`difficulty:low` peso 1, `difficulty:medium`
   peso 2, `difficulty:high` peso 3), fechada no mês por um pull request unido. O peso é da issue: dividir o trabalho em vários pull
   requests não muda nada, e pull request sem issue com peso não entra na divisão (como na Drips Wave).
2. **De quem é:** da pessoa atribuída à issue quando ela fecha, uma pessoa por issue. Quem quer uma issue pede nela, e uma pessoa
   mantenedora atribui.
3. **O peso se discute antes:** quem discorda diz na issue antes de começar; depois do merge o peso não muda. O script confere que o
   rótulo veio antes da atribuição (pela linha do tempo da issue); se veio depois, a issue não conta. Uma pessoa mantenedora pode tirar
   o peso de uma issue fechada por spam ou mau uso, com o motivo escrito na issue (como na Drips Wave).
4. **A pessoa mantenedora entra pela mesma regra** (D231): o trabalho dela só conta numa issue com peso aberta antes, como o de
   qualquer pessoa, sem valor fixo e sem teto. Quando houver uma segunda pessoa mantenedora, ela confirma o peso das issues da primeira
   (o Actual Budget paga quem mantém por pontos públicos).
5. **O mês:** do dia 1 ao último dia, na hora de Brasília. Fechado o mês: primeiro a infraestrutura do mês, pelo recibo de cada gasto;
   o resto vai para quem tem issues com peso fechadas no mês, na proporção da soma dos pesos de cada pessoa. As partes são em centavos,
   arredondadas para baixo, e os centavos que sobram ficam para o mês seguinte. Num mês sem issue com peso fechada, o resto fica para o
   mês seguinte (D202).
6. **Sem pagamento do passado** (D230): a regra vale a partir do primeiro mês com ela publicada no site da produção.
7. **O cálculo é público:** um script do repositório lê do GitHub as issues fechadas no mês (rótulo, pessoa atribuída, datas da linha
   do tempo) e o livro-caixa do mês (entradas e infraestrutura) e escreve a divisão; qualquer pessoa roda e chega aos mesmos centavos
   (como o script de pontos do Actual Budget).
8. **O pagamento** (D231): quem recebe escolhe cripto ou Pix. Nenhum dado de pagamento aparece em issue ou pull request: o pedido é
   feito em particular, só quando houver valor a pagar. Antes do primeiro pagamento a outra pessoa, a resposta do contador sobre os
   impostos (Q39) é um portão.
9. **Não reclamado:** fica guardado 6 meses e depois volta para a divisão do mês seguinte, com a linha no livro-caixa (D231; o Actual
   Budget zera o não reclamado duas vezes por ano).
10. **Quem contribui sabe que talvez nunca receba:** o pagamento só existe quando há doação (D231).

### 11.3 O livro-caixa público

- Um arquivo por mês em `data/support-ledger/AAAA-MM.json` (fora de `data/ledger/`, que é o livro de fluxos do dinheiro público),
  validado por um JSON Schema, com: cada entrada (data, canal, valor e, na cripto, o link da transação; nenhum nome de quem doou);
  cada gasto de infraestrutura (serviço, valor, data e o recibo); a divisão do mês como o script escreve (o @ do GitHub, as issues, a
  soma dos pesos, o valor); cada pagamento feito (o @ do GitHub, o valor, a data, o canal e, na cripto, o link da transação; no Pix,
  só "Pix" e a data); o saldo; e quantos meses o saldo paga a infraestrutura no ritmo dos últimos três meses (como a Base dos Dados).
- A conta fecha ao centavo: saldo do mês anterior + entradas - infraestrutura - pagamentos = saldo do mês, e o saldo bate com o que as
  carteiras e a conta mostram no último dia (regra das contas, D94).
- Onde o site mostra o livro-caixa (uma vista da janela do Apoie ou uma página) é a rodada de prévia (D185).

### 11.4 Os textos (exatamente assim; a rodada de prévia mostra cada um no lugar)

- **Abertura (troca o texto de 9.3):** "O Brasil-Imposto mostra, com dados oficiais e a fonte de cada número, para onde vai o imposto
  pago no Brasil. É apartidário, de código aberto e sem fins lucrativos: toda funcionalidade é e continua disponível para todas as
  pessoas, de graça. O seu apoio paga duas coisas, e nada além delas: a infraestrutura que mantém os dados corretos e no ar e o
  trabalho de quem desenvolve o projeto."
- **Linha nova, logo depois** (D231): "O Brasil-Imposto ainda não é uma associação registrada: as doações chegam às carteiras do
  mantenedor, e cada entrada e saída é publicada." Quando o Pix abrir, "às carteiras" passa a "às carteiras e à conta".
- **Coluna "2. Desenvolvedores" (troca):** "Quem fecha uma issue com peso, inclusive a pessoa mantenedora. O que sobra de cada mês,
  depois da infraestrutura, é dividido pelo peso das issues fechadas no mês (1, 2 ou 3, posto na issue antes do trabalho). Quem
  contribui sabe que talvez nunca receba: o pagamento só existe quando há doação, e cada um é publicado no livro-caixa."
- **Quadro "Como cada mês é dividido" (troca os quatro itens):** "Primeiro, a infraestrutura do mês, pelo recibo de cada gasto." /
  "O resto vai para quem fechou issues com peso no mês, inclusive a pessoa mantenedora, na proporção do peso (1, 2 ou 3), por um script
  público que qualquer pessoa pode rodar." / "Num mês sem issue com peso fechada, o resto fica para o mês seguinte; valor não
  reclamado volta à divisão depois de 6 meses." / "Tudo fica no livro-caixa público: cada doação, cada gasto e cada pagamento."
- **Sai** o item "Nas primeiras divisões, contam todas as contribuições aceitas desde o início do projeto..." (D230).
- **Coluna "1. Infraestrutura" (troca, D232):** "O custo real de cada mês, pelo recibo de cada gasto, só do que o projeto paga como
  projeto: servidor, banco de dados, domínio e a ferramenta de IA que coleta e confere os dados, quando paga em nome do projeto. Hoje o
  site é hospedado de graça no GitHub Pages e o projeto não paga nenhum serviço. A assinatura de IA de cada pessoa que contribui não
  entra aqui: ela é paga pela divisão. É a primeira coisa paga com o apoio."

### 11.5 `GOVERNANCE.md` e `CONTRIBUTING.md`

- **`GOVERNANCE.md`, "Quem pode doar" (troca o texto inteiro):** valem a regra 4 e o livro-caixa; sem fins lucrativos, com a linha da
  associação; a regra de 11.2 em seis linhas, com o link para esta seção; sai "Hoje o projeto não recebe doação" e sai a devolução de
  cripto de carteira sem identificação (D204).
- **`CONTRIBUTING.md`, seção nova "Issues com peso":** como pedir uma issue, o peso antes do trabalho, quem atribui, o aviso de que
  talvez nunca haja pagamento, e que nenhum dado de pagamento vai em issue ou pull request.
- **O modelo de pull request** ganha a linha "Closes #N da issue com peso, se houver".

### 11.6 Provas

- **O script da divisão**, testes primeiro, com casos gravados: dois meses com pesos 1, 2 e 3 entre duas pessoas e a pessoa
  mantenedora, a soma das partes mais os centavos guardados igual ao que sobra da infraestrutura, ao centavo; controles que têm de
  falhar: uma issue sem rótulo contada, um rótulo posto depois da atribuição contado, uma issue fechada sem pull request unido contada,
  um centavo a mais numa parte.
- **O livro-caixa:** o JSON Schema e a conta ao centavo de 11.3, com um controle (um real a mais numa entrada).
- **Os textos:** `apoie-check.cjs` confere cada texto de 11.4 na janela, e o texto que sai some; `visible-text` nas quatro páginas.
- Capturas em 1440 e 420 px da janela, olhadas antes de entregar.

### 11.7 Pergunta ao mantenedor (rodada 2), respondida (D232)

1. **O que conta como infraestrutura.** O texto aprovado da coluna "1. Infraestrutura" (9.3, D201) diz: "hoje, as ferramentas de
   inteligência artificial usadas para coletar e conferir os dados". Cada pessoa que contribui paga a própria assinatura de IA (D201).
   - **a) (escolhida, D232)** Só o que o projeto paga como projeto, cada um com recibo: servidor, banco de dados, domínio e a ferramenta de IA que coleta e
     confere os dados, quando ela for paga em nome do projeto. A assinatura pessoal de quem contribui (a do mantenedor também) não
     entra: ela já é paga pela divisão. Nota 75, recomendada: com pessoas que o mantenedor não conhece, nenhum recibo pessoal entra
     antes da divisão, e o livro-caixa não mostra o preço da ferramenta de cada pessoa (D201).
   - b) Também a assinatura de IA do mantenedor; a das outras pessoas não. Nota 40: uma regra só para uma pessoa.
   - c) A assinatura de IA de toda pessoa que fechou issue com peso no mês, pelo recibo. Nota 50: o livro-caixa passa a mostrar o preço
     da ferramenta de cada pessoa, o que D201 pediu para não mostrar, e uma assinatura de quem fechou uma issue pequena come a parte de
     todas as outras.

### 11.8 Quem faz (D164)

A sessão local de 2026-11-06, depois da aprovação: a rodada de prévia dos textos, o plano, e os pull requests no `staging`.
