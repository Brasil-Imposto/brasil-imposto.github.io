# Governança do Brasil-Imposto

Este documento diz quem decide no projeto hoje, como decide e como a decisão passa a ser dividida quando o projeto crescer.

## Quem decide hoje

O projeto está na **fase 0**: um mantenedor, @VitorPChaves, dono da organização `Brasil-Imposto` e de todo o repositório
(`.github/CODEOWNERS`).

- **Tudo entra por pull request**, inclusive o que o mantenedor faz. A regra da `main` não tem exceção, nem para o dono: pull
  request obrigatório, o check do DCO verde, histórico linear, sem force push.
- **Toda decisão tem o motivo por escrito no pull request** que a aplica. As decisões que mudam o produto ficam registradas em
  `docs/decisions/README.md`.
- Enquanto houver um só mantenedor, o pull request não exige aprovação de outra pessoa; a partir da fase 2, exige.

## As quatro fases

Os números abaixo são sugestões. Mudar um deles é uma proposta de método (ver abaixo).

| Fase | Quando começa | Quem decide | No GitHub |
|---|---|---|---|
| 0. Fundação | Hoje | O mantenedor | Um dono da organização; tudo por pull request, sem exceção |
| 1. Revisores | 3 pessoas contribuindo com frequência (por exemplo, 5 pull requests aceitos em 3 meses) | O mantenedor, com a revisão de outras pessoas | Time de revisores com o papel Triage e depois Write; `CODEOWNERS` por área (um estado, uma base de dados) |
| 2. Segundo mantenedor | Um revisor com histórico (por exemplo, 10 pull requests revisados) | Dois mantenedores; todo pull request precisa da aprovação de outra pessoa | Segundo dono da organização, como o GitHub recomenda; a regra da `main` pede 1 aprovação de quem não fez o último envio |
| 3. Conselho | 5 ou mais mantenedores | Um conselho eleito, com o limite de partido das regras de neutralidade | O papel de dono fica só com membros do conselho; o fundador passa a ser uma cadeira |

**Limite honesto:** no GitHub, qualquer dono pode mudar qualquer regra. A divisão do poder é um compromisso escrito, visível
nas regras ativas da `main` (que qualquer pessoa pode ler) e no registro de auditoria da organização. A garantia final é a
licença: a AGPL-3.0 e a CC BY 4.0 deixam qualquer pessoa copiar o código e os dados e continuar o projeto.

## Regras de neutralidade

O projeto é apartidário: mostra dados oficiais, com fonte, sem chamado ao voto, e trata qualquer governo e qualquer partido do
mesmo jeito. Valem desde o primeiro dia:

1. **Mantenedores declaram filiação partidária e cargo público**, neste arquivo, ao entrar e sempre que mudarem.
2. **Nunca dois mantenedores do mesmo partido.**
3. **Quem é filiado a um partido não aprova sozinho pull request sobre o próprio partido.**
4. **O projeto recusa dinheiro de partido, de candidato e de ocupante de cargo eletivo, e publica toda fonte de dinheiro acima
   de 5% da receita do ano.**

Declarações dos mantenedores:

| Mantenedor | Filiação partidária | Cargo público |
|---|---|---|
| @VitorPChaves | Nenhuma | Nenhum |

## Quem pode doar

Hoje o projeto não recebe doação. Quando receber, valem a regra 4 acima e estas: tudo o que entra e tudo o que sai fica
publicado mês a mês; uma doação em cripto acima de um valor, vinda de carteira sem identificação, é devolvida (o valor é
definido e publicado antes da primeira doação). O pedido de apoio só vai ao site quando o projeto cumprir o padrão de qualidade
dos dados que o justifica.

## Mudança de método

Mudar como um número é calculado, de onde ele vem ou como aparece (uma regra de localização, uma estimativa, uma fonte nova
que substitui outra) é uma **proposta de método**:

1. Abra uma issue pelo formulário "Proposta de método", com o que muda, o motivo, o efeito nos números e as fontes.
2. A proposta é anunciada em Discussions e fica **de 7 a 10 dias** aberta para comentário antes do merge.
3. O pull request que a aplica traz a checagem ao centavo, o controle que falha e o motivo da decisão por escrito.

Correção de um erro, sem mudança de método, não precisa da janela de comentário.

## Áreas

| Área | Situação | Quem cuida |
|---|---|---|
| Saldo de cada estado com a União (27 estados) | Mantido | @VitorPChaves |
| As contas do Brasil e o governo federal | Mantido | @VitorPChaves |
| Municípios de SC | Mantido | @VitorPChaves |
| Municípios do RS | Mantido | @VitorPChaves |
| DF por Região Administrativa | Mantido | @VitorPChaves |
| Municípios dos outros 24 estados | Sem dono | Veja a issue "Municípios de outros estados" |
| Os 3 Poderes | Mantido | @VitorPChaves |
| Como o dinheiro anda | Mantido | @VitorPChaves |
| Casos (obras) | Mantido | @VitorPChaves |
| Site e páginas | Mantido | @VitorPChaves |

## In English

Phase 0 today: one maintainer, everything through pull requests with no exception for the owner, and the reason for each
decision written in its pull request. Four phases, with suggested thresholds, lead to reviewers, a second maintainer and an
elected council. Neutrality rules: maintainers declare party membership and public office; never two maintainers from the same
party; a party member never approves alone a pull request about their own party; no money from parties, candidates or elected
officeholders, and every source above 5% of the year's income is published. Method changes get 7 to 10 days of comment in
Discussions before merging.
