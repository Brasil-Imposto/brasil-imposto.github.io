# Doação rápida: como um brasileiro pode apoiar o Brasil-Imposto em segundos (2026-10-28)

Pesquisa pedida pelo autor em 2026-10-28: existe um jeito de um brasileiro doar mais rápido do que com cripto ou GitHub Sponsors, como nas lives e no YouTube, onde a pessoa digita um valor e doa em segundos? Os limites são os do projeto: nenhum Pix no nome ou no CPF do autor (D123: o projeto tem de parecer uma organização, não uma pessoa; Pix com o nome do projeto só com CNPJ), tudo público num livro-caixa, o site apartidário, e só plano gratuito sem a aprovação do autor.

**Como foi feito:** cada fato foi lido na página do próprio provedor ou do Banco Central, em 2026-10-28 (páginas montadas por script foram abertas num navegador sem tela). Uma página que não abriu fica como "não confirmado", nunca preenchida pela memória. Dois agentes de pesquisa (Pix e provedores; plataformas), 365 mil tokens no total; as taxas da LivePix e da Vakinha foram relidas pela sessão.

## 1. Resumo

| Caminho | Nome que o doador vê no Pix | Quem abre a conta | Taxa (quem cobra) | Valor digitado pelo doador | Livro público |
|---|---|---|---|---|---|
| Chave Pix num banco, QR sem valor | O dono da chave (com CPF, o nome do autor) | CPF ou CNPJ | Não conferido nesta pesquisa | Sim | Não; o projeto publica o seu |
| Provedor que faz um QR por valor (InfinitePay, Asaas, Efí, Mercado Pago) | O dono da conta: com CPF, o nome do autor | CPF ou CNPJ | De R$ 0 (InfinitePay) a R$ 1,99 por Pix (Asaas) | Sim, com um pequeno servidor | Sim, pela API, se o projeto publicar |
| Woovi | A empresa dona do CNPJ | Só CNPJ | 0,80% por Pix (mín. R$ 0,50, máx. R$ 5,00) ou R$ 0,85 por Pix (Woovi) | Sim | Sim, pela API |
| LivePix (ferramenta de lives) | Não confirmado; o Pix cai na conta da plataforma ("sem revelar seus dados") | Pessoa física | 5% por doação por Pix, 7% no cartão (LivePix LTDA) | Não confirmado | Não; só o painel do criador |
| AlertPix (ferramenta de lives) | Não confirmado; a plataforma intermedeia | CPF ou CNPJ | 2% por doação e R$ 0,20 por saque (Tips Group LTDA) | Não confirmado | Não confirmado |
| Vakinha (vaquinha online) | Não confirmado; o Pix cai no saldo da vaquinha, na plataforma | CPF ou CNPJ | 6,4% + R$ 0,50 por doação; saque de R$ 5,00 a R$ 17,99 (Vakinha Ltda) | Sim | Em parte: a página mostra o total e os apoiadores |
| Benfeitoria | Não confirmado | CPF ou CNPJ | Sem comissão da plataforma; a taxa da integradora de pagamento não foi confirmada | Não confirmado | Não confirmado |
| Open Collective (Open Source Collective) | Cartão em dólar; nome na fatura não confirmado | O projeto, com o Open Source Collective como anfitrião | 10% de cada entrada, mais a taxa do processador (Open Source Collective) | Não confirmado | Sim, o melhor do grupo: cada entrada e cada despesa |
| GitHub Sponsors | O perfil patrocinado no GitHub | Pessoa ou organização numa região aceita (o Brasil é aceito) | 0% de conta pessoal; até 6% de conta de organização (GitHub) | Por faixas, uma vez ou todo mês | Não; com o Open Source Collective, entra no livro dele |
| YouTube Super Chat | YouTube | Canal monetizado | O criador fica com 70% (YouTube) | Só no chat de uma live | Não |

**A conclusão que vale para todos:** o que torna a doação das lives rápida é o Pix com um valor que a pessoa escolhe; isso o Pix já faz de graça. O que decide o caminho é **o nome que aparece na tela do banco de quem doa**, e esse nome é sempre o de quem tem a chave Pix (seção 2).

## 2. A regra do Pix que decide tudo

Banco Central, Manual de Padrões para Iniciação do Pix, versão 2.10.0 (lido em 2026-10-28 no PDF do Banco Central):

- **Valor digitado pelo doador:** no QR estático, o valor é opcional. Sem ele, "o valor da transação não é fornecido. Portanto, ele deverá ser solicitado ao pagador" (seção 2.6.3). Um QR fixo, sem valor, já dá o "digite o valor e doe" das lives, sem custo e sem servidor.
- **O nome que o doador vê:** "O nome a apresentar ao pagador será necessariamente o nome retornado na consulta ao DICT. O MerchantName será ignorado pelo pagador." (nota 26). Para o QR dinâmico, o mesmo: "o nome do usuário recebedor conforme registrado no DICT" (notas 46, 66, 67 e 69).
- **Consequência:** um provedor de pagamento não consegue mostrar o próprio nome nem o nome do projeto no lugar do titular da conta. Uma conta no CPF do autor, em qualquer banco ou provedor, mostra o nome do autor. Uma conta com CNPJ mostra a razão social, e o nome fantasia se estiver no cadastro do CNPJ (Manual Operacional do DICT, seção 2.3; um MEI não pode mostrar nome fantasia).
- **A exceção que interessa:** quando o Pix vai para a conta de uma plataforma (uma vaquinha, uma ferramenta de lives), que depois repassa ao criador, o doador vê o nome de quem tem a chave: a plataforma ou o banco dela. As plataformas não dizem na página qual nome aparece (seção 6).

## 3. Como o seuimposto.com recebia dinheiro

O site "Apuração 2026" (seuimposto.com) mostrava a apuração das eleições ao vivo. O HTML que um robô recebe é só um aviso ("Não deu para abrir a apuração neste navegador"); o servidor entrega a página de verdade só a um pedido com os cabeçalhos de navegação de um navegador. Lidos a página e o seu único script, em 2026-10-28:

- **Não era um botão de doação: era um Super Chat.** Um chat ao vivo ao lado do mapa da apuração, com mensagens pagas por Pix. Valores fixos: R$ 5, 10, 20, 50, 100 e 500. Quanto maior o valor, mais tempo a mensagem fica fixada no topo (0, 1, 2, 5, 10 e 30 minutos) e mais longa ela pode ser (de 60 a 200 caracteres).
- **O fluxo:** escolher o valor, escrever a mensagem, "Pagar R$ X com Pix"; a moderação lê a mensagem antes da cobrança; aparece um QR do Pix feito para aquele valor, com "Copiar código Pix", válido por 15 minutos ("O Pix expirou. Gerar outro"); a mensagem entra quando o banco confirma.
- **Também vendia um espaço de anúncio** (marca e frase, revisados antes do Pix; quem paga primeiro leva, e o outro recebe o dinheiro de volta) e tinha anúncios do Google AdSense.
- **Regra em todo item pago:** "Mensagem paga não pode falar de candidato, partido ou eleição."
- **Não visto:** o nome do recebedor e o provedor de pagamento. Eles ficam dentro do código Pix que o servidor deles gera a cada cobrança; ler um exigiria criar uma cobrança no sistema deles, o que esta pesquisa não fez. O `robots.txt` do site pede que ferramentas de IA não usem o conteúdo; a página e o script foram lidos uma vez, para esta pergunta, sem varredura.

**Por que juntou muitas doações pequenas:** uma multidão ao vivo, num momento de atenção; valores fixos num toque; um QR por valor; e quem pagava ganhava algo visível (a mensagem no topo do chat).

**Como o mesmo funcionaria aqui:** o QR por valor pede uma conta num provedor de pagamento com API (a conta define o nome que o doador vê, seção 2) e um servidor pequeno que cria a cobrança e recebe o aviso de pagamento (um Worker da Cloudflare cabe no plano gratuito). O aviso de pagamento pode alimentar o livro-caixa público sozinho. Sem CNPJ do projeto, a conta seria no CPF do autor, e D123 recusa. A parte do Super Chat (dar algo visível a quem apoia) é tela nova e passaria por rodada de prévia (D185); num site apartidário, mensagens pagas pedem moderação a cada uma.

## 4. Um por um

### 4.1 Chave Pix e QR sem valor, numa conta de banco
- **Nome que o doador vê:** o titular da conta. Com CPF, o nome do autor: D123 recusa.
- **Custo:** não conferido nesta pesquisa, porque o caminho já é recusado por D123.
- **Velocidade:** a mais rápida de todas: abrir o app do banco, ler o QR, digitar o valor, confirmar.

### 4.2 Provedores que fazem um QR por valor
O nome que o doador vê é o titular da conta em todos (seção 2). Para usar com o nome do projeto, todos pedem o CNPJ do projeto.

- **InfinitePay** (CloudWalk Instituição de Pagamento e Serviços Ltda): conta para CPF, MEI e CNPJ, "Abra em 5 minutos", com análise facial; Pix "100% gratuito para CNPJ, MEI e pessoa física"; sem mensalidade. Os termos não têm cláusula sobre doação ou política; a aprovação pode ser revogada "sem a necessidade de justificativa". API para o livro: não confirmado.
- **Asaas:** conta para pessoa física e jurídica; R$ 1,99 por Pix recebido (R$ 0,99 nos 3 primeiros meses); manutenção da conta grátis; API pública com avisos de pagamento (webhooks), boa para um livro automático. Termos: nenhuma cláusula sobre doação ou política, só a 19.2(e), "atividades comerciais não aceitas pelo Asaas por falta de interesse comercial".
- **Efí** (Efí S.A.): conta pessoa física e empresa; Pix pela API 1,19% por Pix; no aplicativo, 30 Pix grátis por mês, mas a gratuidade "não é válida para recebimentos por uma chave Pix cadastrada na API ou webhook"; sem mensalidade. Termos e prazo de abertura: não confirmados.
- **Mercado Pago:** a página se contradiz (0,49% no topo, 0% no corpo, com 0,49% para CNPJ que fatura a partir de R$ 15.000 por mês); no QR fixo o cliente pode "inserir o valor e pagar". Termos: a página não abriu, não confirmado.
- **Woovi:** só conta PJ (CNPJ); 0,80% por Pix confirmado (mínimo R$ 0,50, máximo R$ 5,00) ou R$ 0,85 por Pix; sem mensalidade nem adesão; API e webhooks.
- **Stripe no Brasil:** Pix "somente por convite", 1,19% por Pix.
- **PagBank:** Pix "0% nos primeiros 30 dias" na tabela de vendas; depois disso, não confirmado.

### 4.3 Ferramentas de doação de lives
- **LivePix** (LivePix LTDA): conta de pessoa física, com verificação de documentos quando pedida. O dinheiro vai para uma carteira na plataforma e sai por Pix para uma conta "de mesma titularidade". "Receba incentivos por Pix sem revelar seus dados." Taxas: 5% por doação por Pix, 7% no cartão e 7% internacional (taxa mínima R$ 0,01); 3 saques grátis por mês, depois R$ 0,50 por saque (os termos dizem R$ 1,00: as duas páginas se contradizem). Tem "Vaquinhas" com link para divulgar fora das lives. Termos: o serviço é de "gorjetas" para "criadores de conteúdo"; nenhuma cláusula sobre política, só a proibição de fins ilícitos. Um site cívico não é criador de conteúdo de live: encaixe incerto.
- **AlertPix** (Tips Group LTDA): CPF ou CNPJ, saque para conta da mesma titularidade; "sem a exposição de seus dados pessoais"; 2% por doação e R$ 0,20 por saque; saque em até 48 horas. Serviço novo (termos de abril de 2026).
- **YouTube Super Chat e Super Thanks:** existem no Brasil, mas exigem um canal monetizado e só funcionam dentro do chat de uma live ou estreia; o YouTube diz, na página em inglês, "Fan funding features are not crowdfunding or donation tools". Não serve a um site sem canal.

### 4.4 Vaquinhas e financiamento coletivo
- **Vakinha** (Vakinha Ltda): CPF (maior de 18) ou CNPJ; Pix e cartão. O Pix cai no saldo da vaquinha, na plataforma, com uma chave Pix própria de cada vaquinha; o saque vai para uma conta no nome de quem criou. Taxas: 6,4% + R$ 0,50 por doação, descontadas no saque; saque de R$ 5,00 (até 3 dias úteis), R$ 9,99 (1 dia útil) ou R$ 17,99 (no mesmo dia); criar a vaquinha é grátis. O valor fica disponível no 5º dia depois da doação. A página da vaquinha mostra a meta, o total e os apoiadores. Termos: nenhuma cláusula sobre política; a 9.2(k) deixa o Vakinha encerrar campanhas "a critério do Vakinha" por publicidade negativa.
- **Benfeitoria:** CPF ou CNPJ; sem comissão da plataforma (a integradora de pagamento cobra a sua taxa, valor não confirmado); recusa expressamente "campanhas político-partidárias" e avalia cada projeto. Um projeto apartidário pode passar pela avaliação, mas é decisão deles.
- **APOIA.se:** recorrente 13%; pontual de 6% a 15% (artigo de 2024) ou "até 6%" (página atual): as páginas se contradizem. Conta, Pix e regras: não confirmados.
- **Catarse e Kickante:** taxas, conta e regras não confirmadas (as páginas não abriram com esse conteúdo). A Kickante aceita Pix, cartão e boleto e diz não fazer curadoria.

### 4.5 Open Collective e GitHub Sponsors para quem doa do Brasil
- **Open Collective, com o Open Source Collective:** o doador paga com cartão, PayPal, transferência ou cripto; sem Pix; tudo em dólar. O Open Source Collective fica com 10% de cada entrada, mais a taxa do processador de pagamento. Em troca, o melhor livro público do grupo: cada entrada e cada despesa aparecem na página do coletivo. Critérios de aceite: licença de código aberto e repositório de organização, os dois atendidos pelo Brasil-Imposto. O pedido do projeto está em revisão desde 2026-10-23 (lido na API pública do Open Collective em 2026-10-28: ainda não aprovado).
- **GitHub Sponsors:** pede uma conta no GitHub; uma vez ou todo mês; 0% de taxa para quem apoia por conta pessoal, até 6% por conta de organização. Pix não aparece nas páginas lidas. Com o Open Source Collective como anfitrião fiscal (D156), o dinheiro entra no livro público dele.
- **Um anfitrião fiscal brasileiro no Open Collective, com Pix?** A API pública do Open Collective lista 5 anfitriões no Brasil (2026-10-28); só um tem coletivos ativos: PopSolutions Software e Comunicação, em reais, taxa de 0%, 7 coletivos, saldo de R$ 112,86, e aceita só cartão (`CREDIT_CARD` e `PAYMENT_INTENT`). Não há Pix por esse caminho.
- **IOF no cartão em dólar:** 3,5% por compra no texto em vigor do Decreto 6.306/2007, art. 15-B, VII, com a página do Planalto marcando a disputa do Decreto Legislativo 176/2025 e da ADC 96. A página da Receita não abriu: não informar uma alíquota ao doador sem confirmar.

## 5. Velocidade para quem doa

| Caminho | Passos de quem doa |
|---|---|
| Qualquer Pix (chave, QR sem valor, QR por valor) | Abrir o app do banco, ler o QR ou colar o código, digitar ou conferir o valor, confirmar |
| Vakinha, LivePix | Abrir o link, escolher o valor, pagar o Pix na tela |
| Open Collective, GitHub Sponsors | Formulário de cartão em dólar (ou entrar no GitHub), mais o IOF |
| Cripto | Ter uma carteira com saldo, copiar o endereço, escolher a rede certa, enviar |

## 6. O que não foi confirmado

- **O nome na tela do banco de quem doa** pela Vakinha, LivePix e AlertPix. Nenhuma das três diz na página. A conferência definitiva custa um minuto e nenhum real: abrir o Pix de uma vaquinha qualquer no app do banco, ler o nome mostrado antes de confirmar e cancelar.
- **Mercado Pago:** cláusula sobre atividades proibidas e tipo de conta. **PagBank:** a taxa depois de 30 dias. **Efí:** termos e se a API aceita conta de pessoa física. **Asaas:** link de valor livre. **InfinitePay:** API para o livro. **LivePix:** valor mínimo, prazo de abertura e o valor do saque (R$ 0,50 ou R$ 1,00). **APOIA.se, Catarse, Kickante:** taxas e regras. **Benfeitoria:** a taxa da integradora. **Open Source Collective:** o nome na fatura do cartão e o pagamento a uma conta no Brasil. **GitHub Sponsors:** as formas de pagamento para um doador no Brasil. **IOF:** a página da Receita.

## 7. Recomendação

O autor decidiu em 2026-10-28 que o Brasil-Imposto não abre CNPJ por enquanto (D198), e D123 continua: nenhum Pix no nome ou no CPF do autor. Sem CNPJ, todo Pix rápido termina numa conta no nome do autor; a única escolha é se quem doa vê esse nome. Por isso o caminho mais rápido que cabe nas regras é **uma plataforma que recebe o Pix na conta dela e repassa depois**.

**Recomendada: Vakinha, como um terceiro cartão "Pix" na janela do Apoie**, com link para uma vaquinha chamada Brasil-Imposto.

- **Por que a Vakinha:** Pix e cartão; os termos são de campanha para uma causa (as ferramentas de live são escritas para gorjetas de criadores de conteúdo, e um site não é um canal de live); a página mostra a meta, o total e os apoiadores, que qualquer pessoa compara com o livro-caixa do projeto.
- **Custo para o projeto**, cobrado pela Vakinha Ltda e descontado no saque: 6,4% + R$ 0,50 por doação, e R$ 5,00 por saque (até 3 dias úteis). Pesa nas doações pequenas:

| Doação | Vakinha (6,4% + R$ 0,50) | LivePix (5%) |
|---|---|---|
| R$ 5 | R$ 0,82 (16,4%) | R$ 0,25 |
| R$ 10 | R$ 1,14 (11,4%) | R$ 0,50 |
| R$ 50 | R$ 3,70 (7,4%) | R$ 2,50 |
| R$ 100 | R$ 6,90 (6,9%) | R$ 5,00 |

- **A alternativa mais barata:** LivePix (5% por doação, 3 saques grátis por mês, saque a qualquer hora), com o risco de os termos não servirem a um projeto que não é criador de conteúdo de live. A AlertPix (2%) é a mais barata, mas é um serviço novo.
- **O que o autor aceita com isso:** o saque vai para uma conta no nome do autor. A plataforma conhece o autor (nome, CPF, conta); quem doa não vê. Sem essa aceitação, não existe Pix rápido sem CNPJ, e as doações ficam em cripto e GitHub Sponsors.
- **Transparência:** cada saque entra no livro-caixa do projeto no mês em que sai, com o extrato da plataforma; o total público da vaquinha confere com o livro. A janela do Apoie diz quem recebe o Pix e para onde ele vai, num texto novo que passa pela aprovação do autor e por uma rodada de prévia (D185).
- **Antes de abrir a conta:** a conferência de um minuto do nome que aparece na tela do banco (seção 6).
- **Mais tarde, se o projeto crescer:** o CNPJ próprio (uma associação) dá o Pix com o nome "Brasil-Imposto" e um livro-caixa que se preenche sozinho (seção 3).
- **Fora:** o Pix na chave do autor (D123); o YouTube (pede canal monetizado); a Benfeitoria (avalia cada projeto e veta campanha político-partidária); o Open Collective para Pix (o único anfitrião brasileiro ativo aceita só cartão).

## 8. Perguntas ao autor

1. **Aceitar o saque numa conta no seu nome, por trás da plataforma, com cada saque publicado no livro-caixa?** Sem isso, não há Pix rápido sem CNPJ.
   Recomendado: sim, pela plataforma; quem doa vê o nome da plataforma, nunca o seu.
2. **Qual plataforma:** Vakinha, LivePix ou AlertPix?
   Recomendado: Vakinha, pelos termos de causa e pelo total público, apesar da taxa maior.
3. **A conferência do nome na tela do banco (um minuto seu, sem pagar nada):** abrir o Pix de uma vaquinha qualquer no app do seu banco, ler o nome mostrado antes de confirmar, e cancelar.
   Recomendado: fazer antes de abrir a conta na plataforma.
