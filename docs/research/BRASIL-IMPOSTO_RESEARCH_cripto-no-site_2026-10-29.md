# A doação em cripto feita dentro do site: carteiras de cada rede, o que um site estático consegue e o peso na página

Pesquisa pedida pelo autor em 2026-10-29 (D205: *"the brasil imposto website should not just show the address... it should be able to do the transaction - user selects which token, which chain and the amount he wants to send and sends... everything done inside the website"*). Pergunta: num site estático no GitHub Pages, sem servidor e sem chave secreta (tudo que está na página é público), como quem doa escolhe a moeda, a rede e o valor e envia sem sair do site, confirmando na tela da própria carteira.

**Como foi feito:** passada nos registros primeiro (nenhuma pesquisa anterior sobre conectar carteira pela página; a pesquisa de custódia de 2026-10-29 trata só de onde ficam as chaves do projeto). Depois, dois agentes de pesquisa leram as páginas dos próprios padrões, carteiras, emissores e provedores em 2026-10-29: EVM e Tron (147 mil tokens) e Solana, Bitcoin e XRP Ledger (157 mil tokens). A sessão conferiu de novo o seletor da função `transfer(address,uint256)` (`a9059cbb`) com o keccak-256 do `support_data.py`. As notas completas dos agentes, com todas as URLs, ficam em `private/apoie/` (fora do repositório público). Página que não abriu fica como "não confirmado".

## 1. Resumo

| Rede e moedas | No computador (extensão) | No celular | Servidor, nó ou chave? | Biblioteca? |
|---|---|---|---|---|
| Ethereum (ETH; USDT e USDC ERC-20) | A página fala direto com a carteira (EIP-6963 e EIP-1193): pede a conta, confere a rede e manda `eth_sendTransaction` | Link que abre o app da carteira já preenchido (MetaMask documenta; Trust Wallet tem link próprio) ou o navegador interno da carteira | Não: a carteira usa o próprio nó | Não |
| BNB Smart Chain (BNB; USDT e USDC BEP-20) | Igual, mais trocar para a rede 56 (e adicioná-la, se a carteira não tiver) | Igual | Não | Não |
| Tron (USDT TRC-20) | TronLink injeta `window.tron` e o próprio `tronWeb`; a página monta a transferência e a carteira assina | Navegador interno do TronLink (existe; a injeção não foi confirmada); link da Trust Wallet (não confirmado para Tron) | Não, se tudo passar pelo `tronWeb` da carteira | Não |
| Solana (SOL; USDT e USDC SPL) | Pela extensão, a página precisa montar a transação com um bloco recente, de um nó: o nó público oficial recusa pedidos de páginas | Link ou QR do Solana Pay: a carteira monta a transação | Link: não. Extensão: sim, um nó | Link: não. Extensão: cerca de 107 KB |
| Bitcoin (BTC) | UniSat (`window.unisat.sendBitcoin`, sem biblioteca); Xverse pede uma biblioteca sem versão para navegador | Link ou QR `bitcoin:` (BIP-321) | Não | Link: não |
| XRP Ledger (XRP) | GemWallet (5 KB) ou Crossmark (10 KB) | Link ou QR de pedido de pagamento do Xaman, sem chave | Link: não | Link: não |

**O que decide:** em quase todas as redes dá para enviar sem servidor, sem chave e sem biblioteca, falando direto com a carteira do navegador ou abrindo o app da carteira com tudo preenchido. As exceções são a Solana pela extensão (precisa de um nó) e o WalletConnect (precisa de uma conta e de um identificador do provedor, com teto no plano grátis). O endereço de destino vem sempre do arquivo de dados conferido; o valor e a rede, de quem doa; a confirmação final é sempre na tela da carteira.

## 2. EVM: Ethereum e BNB Smart Chain

- **Achar as carteiras** (EIP-6963, eips.ethereum.org): a página escuta `eip6963:announceProvider` e depois dispara `eip6963:requestProvider`; cada carteira responde com nome, ícone e o objeto EIP-1193. Sem resposta, cai para `window.ethereum` (carteiras antigas e navegadores internos). O EIP avisa que o identificador `rdns` é declarado pela própria carteira e pode ser imitado.
- **Conta e rede** (EIP-1193, EIP-3326, EIP-3085): `eth_requestAccounts`; `wallet_switchEthereumChain` com `0x1` (Ethereum) ou `0x38` (BNB Smart Chain, lido ao vivo na rede); se a carteira responder 4902 (rede não adicionada, documentado pela MetaMask), `wallet_addEthereumChain` com nome, moeda e um endereço de nó que a carteira guarda (a página nunca chama esse nó). Erros: 4001 recusado por quem doa; -32002 pedido já aberto.
- **Enviar:** moeda nativa com `eth_sendTransaction` e `value` em wei (exemplo da própria MetaMask; a página usa BigInt, nunca número de ponto flutuante); token com `eth_sendTransaction` para o contrato do token e os dados `a9059cbb` + destino em 32 bytes + valor em 32 bytes. A MetaMask estima o gás.
- **Casas decimais por token e por rede** (lidas nos contratos): USDT e USDC têm 6 no Ethereum e 18 na BNB Smart Chain. A página guarda as casas de cada token em cada rede: 1 USDT enviado como 10^6 na BNB Smart Chain seria um trilionésimo de dólar.
- **Celular sem servidor:** link da MetaMask que abre a página no navegador interno (`https://link.metamask.io/dapp/{site}`) e link de envio preenchido (`https://link.metamask.io/send/{destino}@{rede}?value=...`; para token, `.../{contrato}@{rede}/transfer?address={destino}&uint256=...`), que "mostra a tela de confirmação" e troca a rede sozinho. A Trust Wallet tem `https://link.trustwallet.com/open_url?coin_id=60&url=...` (navegador interno) e `https://link.trustwallet.com/send?asset=...&address=...&amount=...` (a unidade de `amount` não está escrita na página). O EIP-681 diz que o valor no link é "só uma sugestão" que a pessoa pode mudar.
- **WalletConnect (Reown):** um só painel para centenas de carteiras, também no celular. Exige criar um projeto e um identificador no painel da Reown; o identificador é público por desenho, protegido por uma lista de domínios. Plano grátis "Starter": 2,5 milhões de chamadas por mês, e passou disso, **corta** (as conexões falham até o mês seguinte). Pago: Pro, US$ 89 por mês (ou US$ 890 por ano); Growth, US$ 350 por mês. Vendedor: Reown, cobrança pela Stripe; a empresa que emite a cobrança não foi confirmada. Peso: a entrada do AppKit tem 15,9 KB comprimidos, mas carrega muitos outros arquivos ao rodar (o peso real não foi medido).

## 3. Tron

- TronLink "injeta um objeto window.tron em toda página" (docs.tronlink.org), com `request` e o `tronWeb` da conta depois da autorização. Descoberta pelo TIP-6963 (o irmão Tron do EIP-6963). Conta: `eth_requestAccounts`. Recusa: a promessa rejeita com o texto `'Confirmation declined by user'`, não com um erro.
- Envio: montar a chamada `transfer(address,uint256)` no contrato do USDT, assinar com `trx.sign` (abre a janela do TronLink) e enviar com `sendRawTransaction`. Nenhuma página do TronLink mostra a sequência de TRC-20 de ponta a ponta (não confirmado); a regra da própria Tron: "não ponha chaves privadas no código da página; peça a assinatura pelo TronLink".
- Quem doa precisa de TRX na carteira para pagar a energia da transferência (quantidade não confirmada).
- Chave do TronGrid só se a página chamar o TronGrid por conta própria (grátis, para cotas; os limites não são publicados). Pelo `tronWeb` da carteira, a página não chama nenhum nó.
- Celular: o navegador interno do TronLink existe (página da Tron); o formato de link e a injeção não foram confirmados. Nenhum link de pagamento Tron documentado, além do link da Trust Wallet com o ativo `c195_tTR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t` (não confirmado se funciona para Tron).

## 4. Solana

- **Solana Pay, pedido de transferência:** `solana:{destino}?amount=...&spl-token={mint}&label=&message=`. "Não interativo": a carteira monta a transação com os dados do link, então a página não precisa de servidor nem de nó. O valor vai em unidades da moeda (SOL, não lamports). Token só para a conta associada (ATA) do destino; se a carteira cria essa conta quando ela ainda não existe não está no texto lido (não confirmado). **Risco de manutenção:** a especificação saiu do repositório oficial em 2026-03-26 e o site docs.solanapay.com não respondeu; a última cópia lida é a do commit `546f194`.
- **Pela extensão (Phantom):** `window.phantom.solana`, `connect`, `signAndSendTransaction`. A página precisa montar a transação com um bloco recente, pedido a um nó. O nó público oficial (`api.mainnet.solana.com`) "não é feito para aplicações em produção" e pode bloquear sites (página da Solana, cópia do Web Archive de 2026-10-18); num teste com curl, ele respondeu 403 a todo pedido com o cabeçalho Origin, que toda página manda (não testado num navegador de verdade). Um nó grátis de terceiros (PublicNode) respondeu, sem termos de uso confirmados. Um nó com chave expõe a chave na página.
- Mints dos emissores: USDT `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` (página da Tether) e USDC `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` (página da Circle), os dois com 6 casas (lidas na rede).
- Carteiras que documentam pagar um link `solana:`: a especificação cita a Phantom; a Solflare lista "Solana Pay" entre as funções; Backpack e Trust Wallet não confirmadas.

## 5. Bitcoin

- **BIP-321** (substituiu o BIP-21): `bitcoin:{endereço}?amount={BTC em decimal}&label=&message=`; aceita endereços `bc1`. "A carteira não pode agir sem a autorização de quem paga." Quais carteiras respeitam o valor do link não foi confirmado carteira por carteira.
- **Extensões:** Xverse, `sendTransfer` com o valor em satoshis; quem doa revisa destino, valor e escolhe a taxa na carteira (página da Xverse); a biblioteca `sats-connect` não tem versão para navegador (pede um empacotador). UniSat: `window.unisat.sendBitcoin(destino, satoshis)`, sem biblioteca. Leather: `sendTransfer`, detalhes não confirmados (os exemplos não abriram). Nenhuma pede chave ou servidor.

## 6. XRP Ledger

- **Reserva:** 1 XRP de reserva base na rede principal (xrpl.org, Reserves). Um pagamento menor para uma conta que ainda não existe falha com `tecNO_DST_INSUF_XRP`, e quem envia perde só a taxa da rede. A conta do projeto ainda não existe: a primeira doação precisa ser de 1 XRP ou mais.
- **Xaman sem chave e sem servidor:** link de pedido de pagamento `https://xaman.app/detect/request:{endereço}?amount={XRP}&network=XRPL`, que abre o Xaman já preenchido; sem o app, cai numa página com o pedido e os links para instalar. Também `xrpl://{endereço}?amount=...` (qualquer carteira XRPL pode atender; sem página de reserva). O SDK do Xaman na página pede uma chave pública e cadastro no painel do Xaman; a chave secreta nunca pode ir para a página.
- **Extensões:** GemWallet, `sendPayment` com o valor em drops (1 XRP = 1.000.000); Crossmark, `signAndSubmitAndWait`. Nenhuma pede chave.
- **Tag de destino:** só é exigida se a conta ligar a opção RequireDest; a conta do projeto não precisa.

## 7. USDT e USDC na BNB Smart Chain não são da Tether nem da Circle

- A página da Tether lista, na BNB Smart Chain, só o token de ouro (XAU₮); nenhum USD₮. As páginas da Circle não listam a BNB Smart Chain nem a Tron (zero ocorrências de BNB, BSC, Binance e Tron).
- Os dois contratos que as carteiras mostram na BNB Smart Chain (`0x55d398326f99059fF775485246999027B3197955` e `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d`) respondem com o mesmo dono na rede, e o registro de ativos da Trust Wallet descreve o USDC como "BNB pegged USD Coin ... emitido pela Binance" (fonte secundária). Nenhuma página da Binance abriu. Conclusão lida: na BNB Smart Chain, os dois são versões lastreadas por terceiro, não emissão da Tether ou da Circle, com 18 casas.
- Contratos dos emissores: USDT Ethereum `0xdAC17F958D2ee523a2206206994597C13D831ec7` e Tron `TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t` (Tether); USDC Ethereum `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` (Circle); todos com 6 casas.

## 8. O peso na página (issue #150)

Medido em 2026-10-29 nas versões exatas do jsDelivr (bytes comprimidos com gzip -9):

| Biblioteca | Comprimido | Precisa? |
|---|---|---|
| Nenhuma (EVM, Tron, links e QR) | 0 | Caminho recomendado |
| Gerador de QR (`qrcode-generator` 2.0.4) | 11,7 KB | Só para o QR no computador |
| GemWallet API 3.8.0 | 5,2 KB | Só se a extensão do XRP entrar |
| Crossmark SDK 0.4.0 | 10,5 KB | Idem |
| `@solana/web3.js` 1.98.4 | 106,8 KB | Só se a Solana pela extensão entrar |
| `xrpl` 5.3.0 | 138,3 KB | Não precisa |
| `ethers` 6.17.0 | 160,7 KB | Não precisa |
| `tronweb` 6.5.1 | 232,1 KB | Não precisa (a carteira já injeta) |

## 9. O que as telas de confirmação mostram

A Xverse mostra destinos, valores e a taxa, que quem doa escolhe. A MetaMask diz que o link "mostra a tela de confirmação". O TronLink abre uma janela com Recusar e Assinar. Os campos exatos das telas de MetaMask, Trust Wallet, TronLink, Phantom, Xaman, GemWallet e Crossmark não estão escritos nas páginas lidas: o teste do autor em cada moeda e rede (D205) é o que confere.

## 10. O que não foi confirmado

- Se os navegadores internos de MetaMask, Trust Wallet e TronLink injetam o objeto da carteira (provável; nenhuma página diz).
- Se links `ethereum:` sem o domínio da MetaMask abrem alguma carteira; a unidade do valor no link da Trust Wallet e se ele funciona para USDT na Tron.
- Quem emite USDT e USDC na BNB Smart Chain, numa página da Binance.
- Uma página do TronLink com a transferência TRC-20 de ponta a ponta; quanto TRX quem doa precisa.
- Se Phantom, Solflare, Backpack e Trust Wallet pagam um link `solana:` com token, no computador e no celular; se a carteira cria a conta de token do destino; o teste do nó público da Solana num navegador.
- Quais carteiras respeitam o valor num link `bitcoin:`; a taxa da UniSat sem `feeRate`; os detalhes da Leather.
- Quais carteiras XRPL, além do Xaman, atendem `xrpl://`.
- O peso real do AppKit da Reown; a empresa que cobra pela Reown.
