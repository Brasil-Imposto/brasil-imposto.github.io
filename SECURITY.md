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

## Versões

Só a versão em `main`, que é a publicada no site, recebe correção.

## In English

Report security issues privately through GitHub's private vulnerability reporting (Security tab, "Report a vulnerability").
Do not open public issues for them. There is no project email yet. Only `main`, the published site, is supported.
