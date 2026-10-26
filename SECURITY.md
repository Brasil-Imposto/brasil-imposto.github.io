# Segurança

## Como relatar uma falha

Não abra issue, pull request nem discussão pública sobre uma falha de segurança.

Use o relato privado de falha do GitHub: na aba **Security** deste repositório, **Report a vulnerability**, ou direto em
<https://github.com/Brasil-Imposto/brasil-imposto.github.io/security/advisories/new>. O relato fica visível só para as pessoas
mantenedoras, e a conversa sobre a correção acontece ali mesmo.

Ajuda incluir: o que acontece, onde (página, arquivo ou workflow), os passos para reproduzir e o que a falha permite fazer.

Por enquanto o projeto não tem email. Quando tiver, ele entra aqui como mais um canal.

## O que está no escopo

- O site publicado em <https://brasil-imposto.github.io> e o código deste repositório.
- Os workflows do GitHub Actions do repositório.
- Segredo, dado pessoal ou caminho de máquina publicado por engano no repositório ou no site.

Um número errado no site não é falha de segurança: use o formulário "Pedir correção" das issues, com o link da fonte oficial.

## Prazos dos alertas

Quem trata os alertas é o mantenedor (fase 0 do `GOVERNANCE.md`), nestes prazos:

- **CodeQL, alerta alto ou crítico:** bloqueia o merge no `staging`, por onde toda mudança entra, e é corrigido no mesmo pull
  request.
- **Dependabot, alerta de segurança:** tratado em até 7 dias.
- **Os outros alertas:** revistos uma vez por mês.
- **Segredo vazado** (a varredura de segredos do GitHub): o segredo é trocado antes de qualquer outra coisa.

## Versões

Só a versão em `main`, que é a publicada no site, recebe correção.

## In English

Report security issues privately through GitHub's private vulnerability reporting (Security tab, "Report a vulnerability").
Do not open public issues for them. There is no project email yet. Only `main`, the published site, is supported.
Deadlines: a high or critical CodeQL alert blocks the merge into `staging` and is fixed in the same pull request; a Dependabot
security alert within 7 days; other alerts reviewed monthly; a leaked secret is rotated before anything else.
