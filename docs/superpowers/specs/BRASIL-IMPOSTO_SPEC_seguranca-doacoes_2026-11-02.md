# Spec: segurança da doação em cripto, prevenir e detectar

Status: **aprovada (D217), auditada (D218), fechada com as respostas da auditoria (D219) e com a rodada `seguranca-r1` respondida (D220, 2026-11-03).** Entrou em `docs/superpowers/specs/` no pull request da fase 1 (2026-11-03), que fecha a mais séria das fraquezas que descreve (o texto dos dados rodando como código), para que o código possa citá-la; até ali ficou em `private/security/` (padrão aprendido de 2026-11-02).

Base: o relatório `private/security/BRASIL-IMPOSTO_RESEARCH_seguranca-doacoes_2026-11-01.md`, a auditoria de referências `private/security/BRASIL-IMPOSTO_RESEARCH_precedentes-seguranca_2026-11-02.md` (com as notas D1, D2 e D3), o laboratório em `private/security/lab/`, D204 a D219. Quem faz (D164): a sessão de plano e código aberta pelo prompt de 2026-11-03, dona do plano e dos ramos desta spec; a sessão que escreveu a spec parou na entrega.

**Summary in English**

- **The rule (D218):** every mechanism here has a named project or platform that uses it, read on its own page. What had none was removed (17 items) or asked (5, answered in D219). No reader found an incident where these mechanisms caught an attack: the evidence is that serious projects run them.
- **What it delivers:** the data texts that ran as code are escaped and a script policy blocks the class; the send defects are fixed; the address is checked whole; the repository, the served files, the settings and the five addresses are watched by scheduled jobs on GitHub that e-mail the contact inbox on any change (D216), with a daily all-clear.
- **What it cannot see:** anything that happens only on a donor's machine, and a stolen GitHub account used carefully (it can silence monitors on the same account). With the page-side detectors removed (D219), attempts inside visitors' browsers are not seen at all. Section 13 lists every gap.
- **Measured on 2026-11-02:** production has no crypto view and no address; the test site answers 404 (off, D214); the five addresses have no history.

## 1. O objetivo

Nas palavras do autor (D215): *"the thing i want is for us to no if even an attempt of malicious agents happen inside the platform (any attempt - i want to see the most advanced security mechanisms and best practices ... ever built) we will do that so that we know if we truly need to be worried about changing our approach cause right now I just want to ship this while being 100% sure it works fine and perfectly"*. E a regra de D218: só entra mecanismo com caso real de sucesso.

Duas metas: (1) saber de toda tentativa que toque o que o projeto consegue observar (o repositório e a organização, os arquivos servidos, a configuração, os cinco endereços na blockchain); (2) lançar a cripto com prova de que funciona.

## 2. O desenho em uma tabela

| Superfície | Mecanismo | Quem usa (auditoria) | Frequência |
|---|---|---|---|
| A. Repositório e organização | Rulesets também no `Brasil-Imposto/staging` | Homebrew (as regras da organização cobrem os repositórios dos sites) | Fixo |
| | Ações só fixadas por commit, por política | Kubernetes, Semgrep, Safe | Fixo |
| | A verificação `guard`: falha no pull request que toca arquivo sensível até a etiqueta posta depois do último push | glsec; o Prow do Kubernetes tira a etiqueta a cada push | Em cada pull request |
| | CODEOWNERS e toda publicação na produção esperando a aprovação do autor no ambiente (D221, D222); uma segunda pessoa quando houver (D214) | Homebrew, uv, ruff (ambiente com revisores obrigatórios) | No lote |
| | Alarme quando a configuração de segurança muda | OpenSSF Allstar (sigstore, google), safe-settings | A cada 15 minutos |
| B. Construção e publicação | O hash de cada arquivo publicado, gravado a cada publicação | Safe publica o checksum de cada versão; Uniswap e Aave, o hash IPFS | A cada publicação |
| C. Site no ar | Todo arquivo servido conferido pelo hash contra a cópia boa (a cada 5 minutos o que mudou, as quatro páginas com os endereços inteiras, tudo uma vez por dia, D222), e os cinco endereços contra uma cópia própria do monitor | Recomendação escrita da Security Alliance (D219: fica sem usuário nomeado) | A cada 5 minutos |
| D. Navegador de quem visita | Textos dos dados escapados e regra contra inserir HTML sem limpar | Firefox (`no-unsanitized`) | No código e no `ci` |
| | CSP numa meta, só com origens, sem código inline | Uniswap (D219) | Em cada página |
| | Fontes servidas pelo próprio site | Signal, ethereum.org | Em cada página |
| | O ícone da carteira só se for `data:image` | MetaMask, RainbowKit | Em cada carteira |
| | O endereço inteiro em grupos de 4 | Trezor; MetaMask manda olhar o meio do endereço | Na confirmação |
| | Enviada, depois confirmada na rede, com destino e valor conferidos | MetaMask, Binance, Solana Pay, BTCPay | Depois de cada envio |
| E. Blockchain | Alarme em qualquer transação que saia dos cinco endereços | Lido (vigia aberto do tesouro), Etherscan | A cada 15 minutos |
| G. Alarmes e resposta | Pausar uma moeda ou rede à mão, pelo estado e um deploy | Kraken, Coinbase, Binance pausam uma rede | À mão (D219) |
| | Tirar o site do ar primeiro, por uma folha de resposta escrita | Security Alliance; Safe depois do Bybit | À mão |
| | Sinal de vida diário cuja falta é o alarme | Prometheus ("Watchdog") | Diário |
| | `security.txt` e o registro de endereços | ethereum.org, GitHub; EFF e Tor listam os endereços | Fixo |

O monitor mora em `Brasil-Imposto/monitor`, público (D217), com os agendamentos criados pela conta do autor: o GitHub manda o e-mail de um agendamento para quem o criou. Os logs só trazem tipos e hashes, nunca nomes, valores ou endereços de webhook.

## 3. Onde os alarmes chegam (D216, com D219)

- **Toda conferência roda nos servidores do GitHub** e falha quando acha algo; a falha vira o e-mail do próprio GitHub, com o link da execução. Passos do autor: avisos do Actions por e-mail só para falhas; o endereço da caixa do formulário verificado na conta e escolhido como destino dos avisos da organização.
- **Os avisos do navegador de D216 não têm mais o que mandar:** os detectores da página saíram na auditoria (D219). A chave pública do Web3Forms segue só no formulário de contato.
- **Sinal de vida:** um comentário diário, às 9h de Brasília, numa issue fixada do monitor ("Sinal de vida"), com as contagens do dia; o e-mail dele chega pelos avisos de quem acompanha o repositório. **Se não chegar até as 10h, vale como alarme.** É o padrão "Watchdog" do Prometheus: um sinal que sempre dispara, e a falta dele avisa.
- **O monitor vigiado:** um agendamento a cada hora no repositório principal confere que a conferência mais frequente do monitor rodou há menos de três dos seus intervalos (hoje a `chain`, de 15 em 15 minutos: 45 minutos) e falha se não rodou. O monitor grava seu estado num commit diário, porque o GitHub desliga agendamentos de repositório público sem atividade em 60 dias; se mesmo assim desligar, o sinal de vida para.

## 4. Pausar e tirar do ar (D219)

- **Pausar uma moeda ou rede:** o campo `status` por rede, que já existe em `data/support.json` (é como o XRP está em "Em breve"), ganha o valor `"paused"`, num pull request com o `guard` e um deploy. O botão da rede fica apagado com "Pausada" e não mostra endereço; se todas as redes de uma moeda pararem, o botão da moeda também; se todas pararem, o cartão "Cripto" fica apagado com "Pausada". É como a Kraken e a Coinbase pausam uma rede. Quando a segunda pessoa estiver no ambiente de produção (D214), o deploy espera a aprovação dela.
- **Tirar o site do ar:** "Unpublish site" nas configurações do Pages (segundos, o site inteiro), o primeiro passo da folha de resposta da Security Alliance. É a parada de emergência.
- A pausa automática e o `pause.json` saíram (D219): nenhuma fonte trata do disparo automático.

## 5. A. Repositório e organização

**Prevenir**
- `Brasil-Imposto/staging`: ruleset igual ao da `main` (só por pull request, `dco`, sem force push, sem apagar), criado por API.
- Ações: a política do GitHub que exige ação fixada por commit inteiro, nos dois repositórios e no monitor; a lista de ações permitidas só com as que usamos.
- `guard`: verificação obrigatória que falha quando o pull request toca `data/support.json` (bloco `crypto`), `assets/bi-cripto*.js`, os vendors da cripto, `.github/`, `deploy/`, o gerador da CSP, o teste dos endereços fixados ou o próprio `guard`. Passa só com a etiqueta `seguranca-revisada` posta pelo autor, no GitHub, depois do último push (D222; as sessões nunca a põem); um push novo tira a etiqueta (como o glsec e o Prow fazem). Roda pelo código da `main`, nunca pelo do pull request.
- CODEOWNERS com esses caminhos. No lote: toda publicação na produção espera a aprovação do autor como revisor obrigatório do ambiente de produção (D221, D222), porque o GitHub não deixa quem abriu um pull request aprová-lo e as sessões os abrem com a conta dele; uma segunda pessoa entra também quando houver (D214).

**Detectar** (monitor, a cada 15 minutos; cada mudança alarma uma vez e vira a nova base, então o histórico fica no monitor)
- O que o Allstar cobre: proteção de ramo e rulesets, administradores, colaboradores e workflows. A mesma conferência lê também apps instalados e suas permissões, webhooks, chaves de deploy, ambientes e suas regras, configuração do Pages e a política do Actions: é o mesmo mecanismo em mais endpoints (o Allstar não os cobre).
- Lê com um GitHub App da organização, só leitura (D217), o único que lista os tokens finos com acesso à organização ("Only GitHub Apps can use this endpoint").

**O que não se vê:** logins e sessões da conta (o log de auditoria de uma organização gratuita só se lê na tela, por 180 dias); tokens clássicos e o login do `gh` desta máquina; o que um app autorizado faz dentro das permissões que já tem. Uma chave SSH nova na conta: o próprio GitHub manda e-mail ao dono.

## 6. B. Construção e publicação

- O `pages.yml` grava `build-manifest.json` no site, com o commit, a hora e o sha256 de cada arquivo publicado, e o hash do conjunto vai na nota da versão (o padrão do checksum por versão da Safe). Esse arquivo é a cópia boa que a seção 7 compara.
- Publicação só da `main` (já é assim).

## 7. C. O site no ar (D219)

- **A cada 5 minutos** (horário quebrado, `2-59/5`, porque o GitHub atrasa as horas cheias), na forma de D222: cada arquivo servido é pedido com a pergunta "mudou?" e só desce e é conferido pelo sha256, contra o manifesto do commit que está no ar (lido na API de publicações, nunca só no manifesto), quando mudou; as quatro páginas com os endereços descem inteiras; uma vez por dia, tudo desce e é conferido. O bloco `#bi-cripto-data` é lido e os cinco endereços e sete contratos comparados com `pins.json`, a cópia própria do monitor, que mora em outro repositório e só muda por pull request lá. A CSP tem de estar lá. Baixar tudo a cada 5 minutos daria cerca de 756 GB por mês, acima do limite flexível de 100 GB do Pages (medido em 2026-11-03).
- Por que todo arquivo: no ataque ao Bybit o arquivo trocado ficou dois dias no servidor e o código só disparava para uma carteira; olhar só os endereços mostrados não teria visto.
- Até o lote, a produção não tem cripto: a conferência roda no `ci` contra a montagem local e passa a olhar a produção no dia do lote.

**O que não se vê:** o intervalo entre duas rodadas (agendamentos atrasam e podem ser descartados em horas de pico); quem recebeu um arquivo trocado.

## 8. D. O navegador de quem visita

- **Escapar** os três campos que rodaram como código (Os 3 Poderes, "Média por mês"; Como o dinheiro anda, "Tribunais Superiores"; as strings dos ícones da janela do estado) e todo campo que o laboratório alcançar. O laboratório de dados envenenados vira teste permanente: todo texto de todo arquivo de dados, em todas as páginas.
- **A regra do Firefox** (`no-unsanitized/method` e `no-unsanitized/property` em erro) no `ci`, contra todo `innerHTML`, `outerHTML` e `insertAdjacentHTML` novo que não passe pela função de escape.
- **CSP como a da Uniswap (D219):** uma meta gerada pela construção, com `script-src` só de origens (o próprio site e os CDNs com hash que já usamos), sem `unsafe-inline` nem `unsafe-eval`, `object-src 'none'`, `base-uri 'none'`, `connect-src` só com o próprio site, o Web3Forms do formulário e os nós públicos da conferência de cada doação. Os scripts inline das páginas saem para arquivos. Sem `unsafe-inline` em script, um manipulador injetado não roda. O estilo da Uniswap é lido no plano antes de fixar o `style-src`.
- **Fontes no próprio site:** Manrope e JetBrains Mono (OFL 1.1); sai o Google Fonts.
- **O ícone da carteira** só entra se começar por `data:image` (a regra da biblioteca da MetaMask e do RainbowKit); senão o botão fica sem ícone.
- **O endereço inteiro em grupos de 4** no resumo e na espera da carteira, no lugar de "confira os 4 últimos" (golpes acertam de 14 a 20 caracteres; Trezor mostra em grupos de 4; MetaMask manda olhar o meio).
- **Depois de enviar:** a página procura a transação num nó público da rede e mostra "Enviada pela sua carteira", depois "Confirmada na rede", conferindo destino e valor (Solana Pay: achar a transação "doesn't guarantee that a valid transfer with the expected amount and recipient happened"); se o destino for outro, avisa quem doou. Sem resposta do nó, fica o link. A Solana fica fora (o envio dela é no app). D217.

**O que não se vê (D219):** tentativas dentro do navegador de quem visita (os detectores da página saíram); um programa malicioso que muda a tela da carteira; uma extensão de carteira maliciosa; quem envia a partir do histórico da carteira.

## 9. E. A blockchain

- A cada 15 minutos, pelos nós públicos e grátis já usados na revisão (`ethereum-rpc.publicnode.com`, `bsc-rpc.publicnode.com`, `api.trongrid.io`, `mempool.space`, `xrplcluster.com`, `api.mainnet-beta.solana.com`), sem chave: **qualquer transação que saia de um dos cinco endereços** (gasto de BTC, nonce que muda no ETH e na BSC, saída na Tron, sequência da conta no XRP Ledger, assinatura da chave na Solana). Uma aprovação de token é uma transação que sai do endereço, então este alarme a vê. O gasto de teste de cada endereço que o autor vai fazer dispara o alarme, como deve.
- **Nó que não responde** três vezes seguidas vira alarme de "não deu para conferir", nunca um verde.
- O envenenamento por transferência de valor zero fica com os exploradores e as carteiras (o Etherscan esconde e marca; a MetaMask avisa).

**O que não se vê:** a semente roubada antes do primeiro uso (o primeiro sinal é a saída).

## 10. G. Folha de resposta, `security.txt` e registro de endereços

- **Folha de resposta, uma página, do modelo da Security Alliance:** tirar do ar ("Unpublish site"), avisar, apurar, pausar a moeda ou rede, trocar os endereços (carteira nova, pull request com o `guard`, a cópia do monitor), e antes de voltar: causa achada, falha corrigida, publicação nova de fonte conferida, credenciais trocadas. Ler o log de auditoria na tela.
- **`security.txt`** (RFC 9116) com `Contact` em link (o relato privado de vulnerabilidade do GitHub, como o do próprio GitHub), `Expires` e `Canonical`; sem endereço de e-mail.
- **Registro de endereços (D219):** os cinco endereços, a data e o commit em que cada um entrou, numa lista simples no `SECURITY.md`, com o histórico do git, como o EFF e o Tor listam endereços.

## 11. Os defeitos do envio

Correções do código que já existe; cada uma vira um teste que falha antes.

| Defeito | Correção |
|---|---|
| XRP: um resultado `tec` aparece como "Doação enviada" | Ler o resultado e mostrar a recusa da rede, a menos que seja `tesSUCCESS` |
| Trocar de rede com a conexão pendente prende a carteira à rede nova | A conexão pertence à rede em que começou; trocar de rede a cancela |
| `showConfirm` fora do `try`: um erro antes da confirmação trava o botão | Dentro do `try` |
| Tron: o resultado de `triggerSmartContract` não é conferido e o erro diz "saldo insuficiente" | Conferir `result` e explicar a falha de verdade |
| UniSat e Crossmark: a rede da carteira não é conferida | `getNetwork` ou `getChain` na UniSat e a rede da Crossmark antes de enviar |
| "Confira os 4 últimos" | O endereço inteiro em grupos de 4 (seção 8) |

Ficam como estão (D219): o valor "1.000" lido como 1 (a regra do Bitcoin Core: o separador é sempre decimal e dois separadores são recusados; o botão mostra o valor) e o primeiro envio de SOL abaixo do mínimo, que a rede recusa sem perda.

## 12. As telas que mudam (rodada `seguranca-r1`, D185, respondida em D220)

Desenhadas no modal real (`docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_seguranca-r1_2026-11-02.html`, gerador `private/security/build_seguranca_r1.py`) e decididas:

1. **O endereço inteiro em grupos de 4, num bloco próprio, em letra maior** (opção b), com "Compare o endereço inteiro com o da carteira, grupo por grupo. Se a carteira encurtar o endereço, abra o endereço inteiro nela." no lugar de "Confira se o endereço termina em ...", também no link do celular.
2. **Pausada como desenhada:** o botão da rede, o da moeda ou o cartão "Cripto" apagado com "Pausada", sem endereço.
3. **Dois passos depois de enviar** (opção c): "Enviada pela sua carteira", depois "Confirmada na rede", com os estados conferindo, ainda não apareceu, não deu para conferir; e, em vermelho, "A transação não foi para o Brasil-Imposto" com o endereço de destino inteiro, em grupos de 4.
4. **Em "Como apoiar", o cartão do GitHub Sponsors sai e o da Cripto vem antes do Pix** (desenho do autor sobre a prévia, D220), em duas colunas no computador e uma no celular.

## 13. O que não dá para ver nem fechar

- Programa malicioso ou extensão maliciosa na máquina de quem doa, e quem doa sem conferir o endereço na tela da carteira.
- Tentativas dentro do navegador de quem visita: nenhum detector de página passou na auditoria (D219).
- Uma conta do GitHub do autor roubada e usada com cuidado: ela pode silenciar o monitor, que mora na mesma conta (D216). Sobram o sinal de vida que para e o alarme da primeira mudança. Um vigia fora do GitHub pediria uma conta fora dele.
- O login do `gh` nesta máquina tem `repo` e `workflow`: um programa malicioso aqui age como o autor. A foto da configuração vê o efeito, não o ato.
- O app do Claude no GitHub tem administração, conteúdo e workflows em todos os repositórios; a foto vigia, não restringe. Restringir é decisão à parte.
- Um ataque ao próprio GitHub ou ao Pages: o monitor só encurta o tempo.
- O registro de endereços fora do GitHub: não há canal (a campanha da Vakinha, quando abrir, pode ser um).
- Uma transação enviada não volta.
- O que só uma carteira de verdade mostra, até as fases 6 e 7.

## 14. A prova e a ordem

**Cada ataque é um teste visto falhando antes da defesa, com controle plantado.**

| # | Ataque simulado | O que tem de acontecer | Controle |
|---|---|---|---|
| R1 | Pull request muda um endereço e o teste fixado juntos | `guard` falha; depois do merge, o monitor acusa | Pull request sem arquivo sensível passa |
| R2 | Mudança de configuração de cada tipo (ruleset apagado, colaborador, app, chave de deploy, webhook, ambiente sem revisor, Pages) | A foto acusa cada uma | Respostas iguais: zero alarmes |
| R3 | Push novo depois da etiqueta | `guard` volta a falhar | Etiqueta depois do último push: passa |
| B1 | Arquivo servido com um byte trocado | A conferência de 5 minutos acusa | O arquivo certo passa |
| L1 | Endereço trocado no bloco de dados servido | A conferência de 5 minutos acusa | Os endereços certos: zero alarmes |
| P1 | Dados envenenados em todo texto (7.896 textos em 265 campos) | Nada roda em nenhuma página | Um buraco plantado dispara |
| P2 | Manipulador inline injetado | A CSP bloqueia | A mesma página sem CSP roda |
| P7 | Ícone de carteira com `javascript:` ou HTML | Botão sem ícone | Um PNG válido aparece |
| P9 | Rede da página | Nenhum pedido ao Google Fonts | Uma página com o Google Fonts plantado: a sonda acusa |
| C1 | Saída plantada nas respostas de um nó | Alarme | Respostas sem saída: zero alarmes |
| C5 | Nó fora do ar três vezes | Alarme de "não deu para conferir" | Nó respondendo: verde |
| C6 | A transação foi para outro endereço | Aviso a quem doou | A transação certa: "Confirmada na rede" |
| A1 | Monitor parado há mais de três intervalos (45 minutos para a `chain`) | O agendamento do repositório principal falha | Monitor com rodada recente: passa |
| S1 | Uma moeda ou rede com `status` `"paused"` | Botão apagado com "Pausada", sem endereço | `"live"`: abre |

Mais um teste por defeito da seção 11, e a CSP provada com as carteiras de verdade na fase 6.

**A ordem, cada fase um pull request para o `staging` com o deploy à mão conferido no ar:**
1. Escape, regra do Firefox, CSP da Uniswap (scripts inline para arquivos), fontes no site, ícone, o laboratório como teste permanente (nenhum texto de tela muda). Esta spec entra no repositório aqui.
2. As telas de D220 (seção 12): os defeitos do envio, o endereço inteiro, a pausa por rede, a conferência na rede e os cartões de "Como apoiar".
3. Repositório e organização: rulesets do `staging`, política de ações, CODEOWNERS, `guard`, manifesto no `pages.yml`.
4. O monitor: foto da configuração, conferência de 5 minutos, blockchain, sinal de vida, monitor vigiado. Passos do autor na resposta final, em ordem de tela: o GitHub App, os avisos de e-mail, acompanhar o repositório; a linha do App e do monitor no registro de serviços.
5. Folha de resposta, `security.txt`, registro de endereços.
6. Carteiras de verdade em redes de teste, contra uma montagem local: MetaMask (Sepolia e BSC testnet), TronLink (Nile), UniSat (testnet4 ou signet), Crossmark (testnet do XRP Ledger), com as chaves geradas por script direto no Keychain e importadas sem aparecer (D217); um captcha de faucet fica com o autor.
7. O teste de verdade do autor com o site de testes ligado só para isso; o gasto de teste de cada endereço; depois o lote da produção com o aviso de produção (D192), as regras novas e a aprovação do autor em cada publicação (D221, D222), e a segunda pessoa quando houver (D214).

## 15. Custo

Nada pago, e nada que peça cartão. Repositório público roda o Actions de graça ("This usage remains free", documentação do GitHub, lida em 2026-11-04), e o Pages não cobra: passar do limite flexível de 100 GB por mês faz o GitHub poder parar de servir o site, por isso a forma de D222 para a conferência de 5 minutos; o GitHub App e os nós públicos não custam. Um repositório privado teria só US$ 12 por mês de franquia, cerca de 2.000 minutos de Linux, e a conferência de 5 minutos sozinha passa disso.

## 16. Fora desta spec

A carteira nova no celular (D214, TODO); um staging na Cloudflare, onde hospedar a API (em aberto); quem recebe o GitHub Sponsors (o cartão saiu do modal em D220); Trusted Types; os 17 mecanismos que a auditoria tirou (lista e motivo em `private/security/BRASIL-IMPOSTO_RESEARCH_precedentes-seguranca_2026-11-02.md`).

## 17. Não confirmado

Se os rulesets de organização valem no plano grátis (os do repositório valem); como MetaMask, TronLink, UniSat e Crossmark se comportam com a CSP (fase 6); o que conta como atividade para o GitHub não desligar um agendamento além de um commit. Confirmados nas fases 1 a 5: o Pages serve `/.well-known/`; os cinco nós grátis respondem a uma página na origem do site; o `style-src` da Uniswap é `'self' 'unsafe-inline'`.
