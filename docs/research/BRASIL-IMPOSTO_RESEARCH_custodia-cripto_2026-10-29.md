# Onde guardar a cripto do Brasil-Imposto: carteira de celular, carteira física ou multiassinatura (2026-10-29)

Pesquisa pedida pelo autor em 2026-10-28 ("do another deep research ... so that we can at least be more sure of the choice"), sobre a carteira que guarda as doações em cripto (D156: Bitcoin; um endereço 0x para Ethereum e BNB Smart Chain; Solana; Tron só para USDT; XRP Ledger). Hoje uma pessoa só guarda as chaves (a pessoa mantenedora), os endereços ficam públicos no site e o plano é gratuito, salvo custo aprovado pelo autor.

**Como foi feito:** cada fato foi lido na página do próprio fabricante ou provedor, ou na Receita Federal, em 2026-10-29; uma página que não abriu fica como "não confirmado". Dois agentes de pesquisa: carteiras de celular gratuitas (194 mil tokens) e carteiras físicas, multiassinatura e o custo de importar (210 mil tokens). A sessão conferiu de novo, nas páginas originais, o suporte do Trezor Suite a Tron e XRP e a regra de importação da Receita.

## 1. Resumo

| Caminho | As 5 redes | Custo | Nome da pessoa no cadastro | Ponto fraco |
|---|---|---|---|---|
| Trust Wallet (app de celular) | Sim, confirmado nas páginas e no registro de redes da própria Trust Wallet | Grátis | Não (sem conta, sem e-mail) | As chaves ficam num celular conectado; app de código fechado (só a biblioteca central é aberta) |
| Exodus ou Coinomi (app de celular) | Não confirmadas todas nas páginas próprias (Exodus); Coinomi lista as 5 | Grátis | Não | Nenhuma auditoria independente nomeada; código fechado |
| Trezor Safe 3 (carteira física) | Sim, no Trezor Suite (Tron, Solana e XRP confirmados nas páginas do Trezor); USDT na Tron e USDT/USDC na Solana não confirmados no app | US$ 59, ou R$ 349 na loja do Trezor; com imposto de importação, até cerca de R$ 569 | Não na carteira; sim na compra (nome e endereço de entrega) | Espera pela entrega; os dados de compradores vazaram em 2026 por fornecedores do Trezor |
| Ledger Nano S Plus (carteira física) | Sim, no app da Ledger | US$ 69; quatro revendas no Brasil na lista da Ledger (preço não lido) | Não na carteira; sim na compra | Vazamento de dados de clientes em 2020 e ataque à biblioteca Connect Kit em dezembro de 2023 |
| Multiassinatura (várias pessoas assinam) | Cinco mecanismos diferentes, um por rede | Taxas de rede | Não | Com uma pessoa só, não tira o ponto único de decisão; no Ethereum e na BNB Smart Chain o mesmo endereço 0x não é garantido |

**O que decide:** carteira de celular agora sai de graça e fica pronta hoje; carteira física guarda as chaves fora da internet. **Trocar depois muda todos os endereços públicos**, porque a carteira física precisa gerar as próprias palavras (usar nela as palavras criadas no celular desfaz a proteção). Os endereços antigos continuam recebendo enquanto a carteira do celular existir.

## 2. Carteiras de celular gratuitas

- **Trust Wallet:** a única em que as 5 redes foram lidas nos dados do próprio provedor (o registro de redes da biblioteca Wallet Core lista Bitcoin, Ethereum, BNB Smart Chain, Solana, Tron e XRP; a BNB Smart Chain usa o mesmo caminho de derivação do Ethereum, então o endereço 0x é o mesmo). Sem conta; 12 palavras; as palavras seguem o padrão do mercado e podem ser restauradas em outra carteira, se a Trust Wallet sumir. Biblioteca central aberta (Apache-2.0), app fechado. A página de segurança cita auditorias (CertiK, Cure53, Halborn, Kudelski, Quantstamp), sem relatórios datados. A extensão de navegador foi atacada em dezembro de 2025 (versão 2.68, cerca de US$ 7 milhões, com reembolso prometido) e em abril de 2023; o app de celular não foi afetado nas duas vezes.
- **Exodus:** sem conta, 12 palavras, explica a reserva de 1 XRP; nenhuma auditoria independente nomeada; BNB Smart Chain e Tron só por resumo de busca (as páginas bloquearam a leitura).
- **Coinomi:** lista as 5 redes, anônima, explica a reserva do XRP; sem cópia na nuvem; nenhuma auditoria encontrada; código fechado.
- **Evitar:** Atomic Wallet (perda estimada acima de US$ 100 milhões em junho de 2023, causa não divulgada, sem reembolso encontrado, segundo reportagens); Zengo (pede conta de e-mail e não tem frase de recuperação); Bitget Wallet (promove entrada por rede social). SafePal, Guarda e OKX Wallet ficaram com redes ou regras não confirmadas.

## 3. Carteiras físicas

- **Trezor Safe 3:** US$ 59 (R$ 349 na lista em reais da loja do Trezor; não diz se inclui impostos). Elemento seguro EAL6+, código aberto. Tron, Solana e XRP aparecem nas páginas de cada moeda do Trezor como compatíveis com o Safe 3 no Trezor Suite (conferido pela sessão). Não confirmado: USDT na Tron e USDT/USDC na Solana dentro do Trezor Suite, e se a loja envia para o Brasil. Sem revenda no Brasil na lista do Trezor. Em 2026, o Trezor informou dois vazamentos de dados de compradores por fornecedores (envio e newsletter), sem acesso a chaves.
- **Ledger Nano S Plus:** US$ 69; as 5 redes no app da Ledger (a Tron pede 0,1 TRX para ativar, segundo artigo de suporte não aberto). Quatro revendas no Brasil na lista da própria Ledger (Cash Fort Brasil, Karimex / E-Spot, KriptoBR e Mercado Livre pela E-Spot), o que evita a importação. Vazamento de dados de clientes em 2020 e ataque à biblioteca Connect Kit em dezembro de 2023 (páginas da Ledger).
- **Tangem** (cartões, US$ 59,90 por dois): lista as 5 redes; USDT na Tron não confirmado; cópia de cartão para cartão, sem palavras.
- Comprar uma carteira física deixa nome e endereço com a loja: os vazamentos acima transformam o comprador em alvo de mensagens falsas. Nunca digitar as palavras em site, e-mail ou mensagem.

## 4. Custo de importar uma carteira física (Receita Federal)

Página "Quanto vou pagar de impostos?" da Receita Federal (lida e conferida em 2026-10-29): compra acima de US$ 50 em site **certificado** no Remessa Conforme paga 60% de imposto de importação menos um desconto de US$ 30; em site **não certificado**, 60% sem desconto; o ICMS do estado (17% a 20%) entra por dentro e incide também sobre o imposto de importação. Para o Trezor Safe 3 (US$ 59), supondo US$ 1 = R$ 5,00, frete zero e ICMS de 17% (suposições, não fontes): cerca de **R$ 388** em loja certificada e **R$ 569** em loja não certificada. Se a loja do Trezor é certificada não foi confirmado; o total na finalização da compra é o número que vale.

## 5. Multiassinatura

Cada rede tem o seu mecanismo: contratos Safe (Ethereum e BNB Smart Chain), carteira com várias chaves (Bitcoin), Squads (Solana), permissões da conta (Tron) e lista de assinantes (XRP Ledger). Na Tron e no XRP Ledger o endereço público continua o mesmo. No Ethereum e na BNB Smart Chain, um Safe é um contrato em cada rede, e o mesmo endereço 0x nas duas não é garantido (dinheiro enviado para o endereço numa rede onde o Safe não existe pode se perder). Com uma pessoa só, a multiassinatura acrescenta chaves e risco de perda sem tirar o ponto único de decisão. **Faz sentido quando houver uma segunda pessoa mantenedora.**

## 6. Recomendação

**Trust Wallet, só o app de celular, numa carteira nova só do projeto, agora**, com uma regra: quando o saldo em cripto passar de um valor que o autor define, a cripto vai para uma carteira física (compra aprovada pelo autor nessa hora), com endereços novos no site e os antigos ainda monitorados.

- **Por quê:** é a única opção gratuita com as 5 redes confirmadas nas páginas do próprio provedor, sem conta e sem nome no cadastro, e fica pronta hoje; as doações do começo tendem a ser pequenas, e o risco de um celular só pesa quando há saldo.
- **Quando a carteira física desde já é melhor:** se os endereços nunca mudarem importa mais do que o custo (cerca de R$ 349 a R$ 569 no Trezor Safe 3, ou o preço de uma revenda brasileira da Ledger) e a espera pela entrega.
- **Fora:** Atomic Wallet, Zengo, carteira de corretora (prende o projeto ao nome do autor) e multiassinatura por enquanto.

## 7. O que não foi confirmado

Trust Wallet: relatórios de auditoria datados, empresa responsável e país. Exodus: a lista completa de redes no celular. Trezor: USDT na Tron e USDT/USDC na Solana no Trezor Suite, envio ao Brasil, certificação no Remessa Conforme, número de palavras. Ledger: preço nas revendas brasileiras, número de palavras, o artigo da ativação da Tron. Multiassinatura: a regra oficial do Safe sobre o mesmo endereço em redes diferentes. Os detalhes de incidentes da Atomic, Guarda, Coinomi, OKX e SafePal vêm de resumos de reportagens, não de páginas abertas.
