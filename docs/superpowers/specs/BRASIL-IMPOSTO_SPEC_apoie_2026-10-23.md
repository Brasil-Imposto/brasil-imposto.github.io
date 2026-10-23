# Spec: o botão Apoie e a janela de apoio

English summary: the "Apoie" button and its modal on the three published pages, built switched off. Every value still missing
(the addresses, the Sponsors page, the cap, the return threshold, the project e-mail) lives in `data/support.json`; the button
renders only when `enabled` is true, which the maintainer turns on after the gates below, and the build refuses `enabled` with any
value missing or any address in the wrong format. The texts are the ones the maintainer approved, word for word. Open points come
back as questions at the end.

Status: **aprovada pelo mantenedor em 2026-10-23** (desenho e todos os textos, na mensagem que pediu esta construção), com base em
D123, D124, D152, D155 e D156 (D155 e D156 estão no registro local de decisões, ainda não publicado). Construída desligada.

## 1. Portões dos canais de pagamento

O agente não decide nenhum destes. Desde 2026-10-23 (seção 8), eles valem para cada canal de pagamento ir de `"soon"` para
`"live"`; o botão e o formulário de contato vão ao ar antes, com `enabled: true` e a chave do formulário, pela mão do mantenedor.

1. **D123:** o pedido só vai ao ar depois do 2º turno da eleição (2026-10-25).
2. **D125 a D127:** toda tela lê o livro de fluxos, toda garantia passa, nenhuma estimativa na tela. O ponto em aberto é a
   estimativa do DF (D146), pergunta Q41.
3. **Todo valor do canal preenchido.** O teste `pipelines/tests/test_support.py` e a construção das páginas (`site_chrome.parts`)
   recusam um canal `"live"` com qualquer valor vazio ou endereço fora do formato da rede, e `enabled: true` sem a chave do
   formulário.

## 2. O arquivo de dados: `data/support.json`

Chaves em inglês. Hoje tudo vazio e `enabled: false`.

| Chave | Hoje | O que é |
|---|---|---|
| `enabled` | `false` | o botão aparece só com `true`, e `true` pede `contact_form.access_key` (seção 8) |
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

## 3. O botão (em `site_chrome.py`, só com `enabled: true`)

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
   - GitHub Sponsors (a marca do GitHub): "Em dólar, uma vez ou todo mês, pela sua conta do GitHub." Botão "Apoiar pelo GitHub
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
  confere a estrutura sempre e os valores quando `enabled` é `true`, e formata reais.
- `docs/superpowers/tools/apoie.py`: o botão, a janela, o estilo e o código, com os textos aprovados.
- `docs/superpowers/tools/site_chrome.py`: `parts()` acrescenta o botão, a janela, o estilo e o código só com `enabled: true`. A
  janela fica fora de `<header>`, porque o `backdrop-filter` da barra prenderia um filho fixo dentro dela. O código entra no próprio
  `<script id="bi-chrome-js">`, o único que o carregamento do mapa de Início roda na hora (`map_loader.py`), então o botão funciona
  enquanto os dados do mapa carregam.
- `pipelines/tests/test_support.py`: o arquivo enviado desligado e vazio; as sete moedas e as redes de cada uma; os exploradores;
  com `enabled: true`, cada valor vazio falha e cada endereço errado plantado falha; desligado, o cabeçalho é o de antes; ligado, o
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
- **`enabled` pode ser `true` com os dois canais em `"soon"`**, mas só com `contact_form.access_key` preenchida (um UUID; um
  endereço de e-mail ali é recusado). Neste pull request `enabled` fica `false` e a chave fica `null`: a sessão local escreve a
  chave e liga `enabled` num commit no mesmo ramo, e o merge espera o "pode" do mantenedor.
- **Valores que faltam:** a produção nunca mostra "a definir". A frase que depende de um valor `null` sai (o teto da manutenção, o
  valor de devolução da cripto). O staging pode mostrar "a definir" (spec de staging).
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
- **Provas:** a montagem da produção com `enabled` ligado e uma chave falsa (só no teste) e `apoie-check.cjs` em 1440, 420 e 320 px,
  com `--control` (seção 6); desligado, as três páginas iguais às da `main`.

