# Spec: a doação em cripto feita dentro do site

Status: **rascunho para a aprovação do mantenedor** (D205). Nenhum código antes da aprovação e das rodadas de prévia (D3, D185). Pesquisa: `docs/research/BRASIL-IMPOSTO_RESEARCH_cripto-no-site_2026-10-29.md`. Quem faz (D164): a sessão local de 2026-10-29, que tem o #162 (esta spec) e o #163 (o código da seção 10 do Apoie, onde a vista de copiar o endereço já está pronta e testada).

## 1. O objetivo

Nas palavras do autor (D205): *"the brasil imposto website should not just show the address... it should be able to do the transaction - user selects which token, which chain and the amount he wants to send and sends... everything done inside the website"*. Quem doa escolhe a moeda, a rede e o valor, e envia sem sair do site; a confirmação final é sempre na tela da própria carteira. O autor vai testar mandando um valor pequeno em cada moeda e cada rede, de preferência por este fluxo (o que também cria a conta do XRP).

## 2. O que fica como está

- **A vista de copiar o endereço continua** (pedido do autor): quem envia de uma corretora não conecta carteira nenhuma. As sete moedas, as redes de cada uma, o endereço, "Copiar", o link do explorador e o aviso da rede ficam exatamente como na seção 4.3 da spec do Apoie, com as proteções da seção 10.
- O site continua estático no GitHub Pages: sem servidor, sem banco de dados, sem chave secreta. Nada de quem doa é guardado ou enviado a lugar nenhum: nem o endereço da carteira, nem o valor.
- O XRP fica "Em breve" até o primeiro 1 XRP do mantenedor (D205; pergunta 8 para o caminho desse envio).

## 3. O mapa do fluxo

### 3.1 Por onde se entra

| # | Entrada | Onde cai |
|---|---|---|
| E1 | Botão "Apoie" no cabeçalho, cartão "Cripto", "Apoiar com cripto" | A vista da cripto, com as moedas (como hoje) |
| E2 | Um link do site com a moeda, a rede e o valor (`#apoie-cripto?moeda=USDT&rede=tron&valor=10`), usado pelo QR do computador e pelo botão que abre o site no app da carteira | A vista da cripto, já com a moeda, a rede e o valor escolhidos. O link nunca traz o endereço: ele vem sempre do arquivo de dados |
| E3 | O site aberto dentro do navegador de um app de carteira (a carteira injeta o seu objeto na página) | Como E1 ou E2; no passo 4, "Carteira deste navegador" aparece primeiro |
| E4 | Computador com extensão de carteira | Passo 4 com "Carteira deste navegador" (a extensão encontrada, pelo nome e ícone dela) |
| E5 | Computador sem extensão | Passo 4 com o QR para o celular e "Copiar o endereço" |
| E6 | Celular com o app da carteira instalado | Passo 4 com "Abrir no app da carteira" |
| E7 | Quem envia de uma corretora | Passo 2: a linha da rede com o endereço e "Copiar", como hoje |

### 3.2 Os passos

1. **Moeda:** os sete botões de hoje (BTC, ETH, SOL, USDT, USDC, XRP, BNB). Uma moeda cujas redes estão todas "Em breve" não abre envio (o XRP hoje).
2. **Rede:** as linhas de hoje (nome da rede, endereço, "Copiar", explorador). Cada linha ganha "Enviar pelo site" (pergunta 1).
3. **Valor:** um campo na unidade da moeda ("10 USDT", "0,005 BTC"), com vírgula ou ponto. Sem valor em reais (pergunta 7).
4. **Como enviar**, só os caminhos que funcionam para aquela rede naquele aparelho:
   - "Carteira deste navegador": as extensões encontradas para a rede (pelo nome e ícone que cada uma anuncia);
   - "Abrir no app da carteira" (no celular): um botão por app documentado para a rede, que abre o app com o destino e o valor preenchidos;
   - "QR para o celular" (no computador): o link de pagamento da rede num QR, para a câmera do celular;
   - "Copiar o endereço": a linha do passo 2, para corretora ou outra carteira.
5. **Conferir:** moeda, rede, valor e o endereço completo, com os 4 últimos caracteres em destaque, e a frase "Na carteira, confira se o endereço termina em {4 últimos}." Para token, o aviso da taxa: "Você vai precisar de um pouco de {ETH, BNB, TRX ou SOL} na carteira para a taxa da rede."
6. **Na carteira:** conectar (a conta), trocar para a rede certa se precisar, e o pedido de envio; quem doa confirma na tela da carteira.
7. **Resultado:** "Doação enviada. Obrigado!" com o link da transação no explorador da rede (do arquivo de dados) e "Pode levar alguns minutos para aparecer."

### 3.3 Cada ramo e cada erro

| Caso | O que a tela mostra | Onde termina |
|---|---|---|
| Nenhuma carteira da rede neste navegador | "Nenhuma carteira de {rede} neste navegador." e só os outros caminhos | QR, app ou copiar |
| Várias carteiras encontradas | A lista, pelo nome e ícone de cada uma | Quem doa escolhe uma |
| Valor vazio, zero, negativo ou com letras | "Informe um valor maior que zero." e o botão desligado | Passo 3 |
| Mais casas decimais do que a moeda tem (8 no BTC, 6 no USDT da Tron, 18 no ETH...) | "{moeda} aceita até {n} casas depois da vírgula." | Passo 3 |
| XRP abaixo de 1 enquanto a conta do projeto não existe | "O primeiro envio para esta conta precisa ser de 1 XRP ou mais (a reserva da rede)." | Passo 3 |
| Quem doa recusa a conexão na carteira | "Conexão recusada na carteira. Nada foi enviado." | Passo 4 |
| Um pedido já está aberto na carteira | "Abra a carteira: há um pedido esperando a sua resposta." | Passo 6 |
| A carteira está bloqueada | "Desbloqueie a carteira e tente de novo." | Passo 6 |
| A carteira está em outra rede e a troca é recusada | "A carteira continua na rede {rede da carteira}. Troque para {rede} para enviar." O site nunca envia em outra rede: confere a rede logo antes do envio | Passo 6 |
| A rede não está na carteira (BNB Smart Chain) | O pedido para adicionar a rede; recusado, a mesma frase do caso acima | Passo 6 |
| A conta ou a rede mudam com o pedido aberto | O site confere de novo antes de enviar e refaz o passo 6 | Passo 6 |
| Quem doa recusa o envio na carteira | "Envio cancelado na carteira. Nada foi enviado." | Passo 5 |
| Saldo insuficiente (valor ou taxa) | A carteira avisa; se ela devolver o erro: "A carteira recusou o envio: saldo insuficiente para o valor e a taxa." | Passo 3 |
| A carteira aceita e devolve o identificador | O resultado do passo 7 | Fim |
| A transação falha depois, na rede | O site só tem o identificador; o explorador mostra a falha | Fim |
| Clique duplo em "Enviar" | O botão fica desligado enquanto o pedido está aberto | Passo 6 |
| No celular, o app da carteira não está instalado | O link da MetaMask e o do Xaman caem numa página da própria carteira; os links `solana:`, `bitcoin:` e `xrpl:` não abrem nada: depois de alguns segundos sem sair da página, "Nenhum app abriu? Use o QR em outro aparelho ou copie o endereço." | QR ou copiar |
| A carteira abre sem o valor preenchido | "Se a carteira não trouxer o valor, digite {valor} {moeda}." (o padrão de cada rede diz que o valor do link é só uma sugestão) | Na carteira |
| Token na Solana para uma conta de token que ainda não existe | A carteira pode cobrar uma pequena taxa para criar a conta (não confirmado); o teste do autor confere | Na carteira |
| Quem doa sai da página no meio (troca de app, recarrega, a bateria acaba) | Nada é reenviado sozinho; ao voltar, a vista abre do começo; o histórico fica na carteira | Passo 1 |
| A carteira mostra um endereço diferente do resumo | O resumo pede para conferir os 4 últimos caracteres e cancelar se não baterem | Cancelado |
| Moeda "Em breve" (o XRP hoje) | O botão da moeda como decidido na rodada do XRP | Sem envio |

### 3.4 Onde o fluxo termina

Enviado (com o link da transação), cancelado (nada sai da carteira), ou um caminho alternativo (QR, app ou copiar o endereço). Nenhuma saída deixa quem doa sem o endereço: a linha com "Copiar" está sempre na tela.

## 4. Como o site fala com cada carteira (versão 1, com as recomendações das perguntas)

| Rede | Computador | Celular | QR no computador |
|---|---|---|---|
| Ethereum e BNB Smart Chain | Extensões pelo EIP-6963 (e `window.ethereum` como reserva): `eth_requestAccounts`, `wallet_switchEthereumChain` (e `wallet_addEthereumChain` para a BNB Smart Chain), `eth_sendTransaction` com o valor ou com a chamada `transfer` do token. Sem biblioteca | Link de envio da MetaMask (documentado: preenche e troca a rede); abrir o site no navegador da MetaMask ou da Trust Wallet, onde o caminho do computador roda | Link EIP-681 da rede |
| Tron (USDT) | TronLink pelo TIP-6963 e o `tronWeb` que a própria carteira injeta. Sem biblioteca | Abrir o site no navegador do TronLink (a confirmar no teste); senão, copiar o endereço | Não há link de pagamento Tron documentado: só copiar |
| Solana | Link do Solana Pay (pergunta 3) | Link `solana:` com o valor e, para token, o mint | O mesmo link num QR |
| Bitcoin | Link `bitcoin:` (pergunta 4) | Link `bitcoin:` com o valor em BTC | O mesmo link num QR |
| XRP Ledger | Link de pedido do Xaman (pergunta 5) | O mesmo link, que abre o Xaman preenchido | O mesmo link num QR |

## 5. Regras de segurança

1. **O destino vem só do arquivo de dados conferido** (`data/support.json`, com a soma de verificação e o endereço fixado no teste, seção 10 do Apoie). Nunca do link, de um campo, da carteira ou de qualquer resposta de fora. O link do site (E2) só escolhe moeda, rede e valor.
2. **Os contratos dos tokens também vêm do arquivo**, fixados no teste como os endereços, cada um conferido na página do emissor (ou marcado quando o emissor não o lista, pergunta 6).
3. **O valor vira unidades inteiras com BigInt**, pelas casas de cada token em cada rede (USDT: 6 no Ethereum e na Tron, 18 na BNB Smart Chain). Nunca número de ponto flutuante. Casas demais são recusadas, não arredondadas.
4. **Só transferências simples.** O código chama só uma lista fechada de métodos da carteira (conta, rede, troca de rede, adicionar rede, enviar). Nunca assinatura de mensagem, `approve`, `permit` ou permissão de gastar tokens; um teste recusa qualquer outro método no código.
5. **A rede e a conta são conferidas logo antes de cada envio;** o site nunca envia numa rede diferente da escolhida.
6. **O resumo mostra o endereço completo** e pede para conferir os 4 últimos caracteres na tela da carteira.
7. **Nenhum script de fora sem hash** (seção 10.2, item 4, do Apoie). Sem biblioteca sempre que der; uma biblioteca necessária fica no próprio site (`assets/`), revisada no pull request.
8. **O site nunca pede frase de recuperação nem chave privada.** A vista diz isso numa linha.
9. **Nada sai sozinho:** cada envio precisa de um clique na página e da confirmação na carteira; nada é refeito depois de recarregar.

## 6. O arquivo de dados

Chaves em inglês. Em cada rede de `crypto.groups[].networks[]`:

- `status`: `"live"` ou `"soon"` (D205: o estado por rede; uma rede em `"soon"` não mostra endereço nem envio);
- `chain_id` nas redes EVM (1 e 56);
- `tx_url`: o endereço da transação no explorador (`https://etherscan.io/tx/{tx}`, por exemplo);
- `native_decimals` e, em cada moeda que é token, `contract` (ou `mint` na Solana), `decimals` e `issuer_listed` (verdadeiro quando o emissor lista o contrato na própria página).

`support_data.py` confere tudo isso, e o teste fixa cada contrato como fixa os endereços.

## 7. O peso na página (#150)

- O código do envio fica num arquivo próprio (`assets/bi-cripto.js`), carregado só quando quem doa toca em "Enviar pelo site". Quem não abre o envio não baixa nada a mais.
- Meta: o arquivo do envio abaixo de 15 KB comprimidos, sem biblioteca. O gerador de QR (11,7 KB comprimidos, `qrcode-generator` 2.0.4) fica em `assets/` e só carrega quando o QR aparece no computador.
- Nenhuma biblioteca de rede (ethers, tronweb, `@solana/web3.js`, xrpl): as carteiras fazem esse trabalho.

## 8. Provas (cada teste escrito antes do código e visto falhando, cada um com o seu controle plantado)

1. **As contas do valor:** valor digitado para unidades inteiras, em cada token e rede, com casos de borda (casas demais, zero, vírgula e ponto). Controle: 6 casas no USDT da BNB Smart Chain tem de falhar.
2. **Os links de pagamento:** cada link (MetaMask, EIP-681, Solana Pay, BIP-321, Xaman) igual ao formato da página de cada padrão, com o destino do arquivo. Controle: um destino trocado tem de falhar.
3. **A chamada do token:** os dados `a9059cbb` + destino + valor, conferidos com o keccak-256 do `support_data.py`.
4. **Uma sonda no navegador com carteiras de mentira** (um objeto EIP-1193 anunciado pelo EIP-6963, um `window.tron` e os links interceptados), que grava cada pedido: o destino, o contrato, o valor e a rede iguais ao arquivo de dados em cada moeda e rede; a recusa, a troca de rede recusada e o clique duplo com as frases da seção 3.3. Controle: um destino trocado no caminho do envio tem de falhar.
5. **A lista fechada de métodos** (regra 4): um método fora da lista no código tem de falhar.
6. **O teste de verdade:** o autor manda um valor pequeno em cada moeda e cada rede pelo fluxo, no site de testes; a sessão confere a chegada no explorador e na API de cada rede.

## 9. Perguntas ao mantenedor (rodada 1)

1. **Onde fica o envio na vista da cripto?** a) um botão "Enviar pelo site" em cada linha de rede, que abre o valor e o "como enviar" logo abaixo, com a linha do endereço como está (recomendado); b) um fluxo em passos que substitui a vista, com "copiar o endereço" como um dos caminhos; c) uma página separada.
2. **Como o site fala com as carteiras?** a) sem biblioteca, sem servidor e sem conta: a extensão do navegador por chamadas diretas onde as carteiras documentam (EVM e Tron) e links ou QR que abrem o app da carteira preenchido (recomendado); b) o mesmo, mais o WalletConnect da Reown: um painel para centenas de carteiras, com uma conta e um identificador público da Reown; plano grátis com corte em 2,5 milhões de chamadas por mês, Pro a US$ 89 por mês; c) só links e QR.
3. **Solana:** a) só o link e o QR do Solana Pay na versão 1 (recomendado); b) também a extensão (Phantom), pelo nó grátis da PublicNode, sem termos de uso confirmados, e 107 KB de biblioteca; c) um nó com chave, que fica visível na página.
4. **Bitcoin:** a) só o link e o QR `bitcoin:` (recomendado); b) mais a extensão UniSat, sem biblioteca; c) mais a Xverse, que pede uma etapa de montagem do código.
5. **XRP:** a) só o link e o QR do Xaman, sem chave (recomendado); b) mais as extensões GemWallet (5 KB) e Crossmark (10 KB); c) o SDK do Xaman, com conta e chave pública no painel do Xaman.
6. **USDT e USDC na BNB Smart Chain** (não são da Tether nem da Circle; 18 casas): a) ficam, com uma linha de fato no envio e na vista do endereço (recomendado); b) saem do site; c) ficam sem nota.
7. **Valor em reais:** a) só na unidade da moeda na versão 1, porque a cotação é a Q36, ainda aberta (recomendado); b) mostrar o valor aproximado em reais por uma fonte pública de preço.
8. **O primeiro 1 XRP pelo site:** a) no site de testes, o XRP abre no envio com o mínimo de 1 XRP; o autor envia por lá, e a produção abre o XRP depois que a conta existir (recomendado); b) o autor envia o primeiro 1 XRP direto do app da carteira, e o XRP abre depois; c) a produção abre o XRP já, com o mínimo de 1 XRP na primeira doação (muda D205).
9. **Depois de enviar:** a) o link da transação no explorador, sem o site consultar nada (recomendado); b) o site consulta a API pública da rede até a doação chegar (mais chamadas de fora, com os limites de cada rede).

Depois das respostas: as rodadas de prévia do envio (o botão na linha, o valor, o "como enviar", o resumo, o QR, os erros e o resultado, no computador e no celular), e então o plano e o código.

## 10. Fora desta spec

A cotação em reais (Q36); o site confirmar a chegada da doação; um livro-caixa automático das carteiras; o WalletConnect, se a pergunta 2 ficar em a; uma política de conteúdo (CSP) para a página.
