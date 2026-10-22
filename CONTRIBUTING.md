# Como contribuir

Obrigado por ajudar. O Brasil-Imposto só mostra dado oficial, então toda contribuição precisa da fonte.

## Corrigir um número

Abra uma issue com: a página e o número, o período, o que está errado e o link da fonte oficial com o valor certo (e a data em que
você abriu a fonte). Quem acrescenta um número prova o número.

## Pull requests

- Tudo entra por pull request, inclusive o que o mantenedor faz; um assunto por pull request.
- Se mudar dados: o script que monta o arquivo em `pipelines/` ou `docs/superpowers/tools/` tem de refazê-lo, com a fonte
  oficial e a data da coleta. Totais têm de bater com o total oficial da fonte, ao centavo.
- Depois de mudar dados ou páginas, rode os quatro construtores do `README.md` e confira a página na largura do computador e do
  celular.
- Nomes de código e chaves de JSON em inglês; o texto que aparece na tela em português.
- Nenhum texto toma partido; pessoas aparecem só com o papel que têm num documento oficial.
- Assine os commits (`git commit -s`, DCO).

## Novos estados e municípios

Os municípios de SC e RS e as Regiões Administrativas do DF já estão cobertos; o caminho para outro estado é o mesmo dos scripts
`--uf` em `pipelines/series/` e `pipelines/politicians/`. Deputados estaduais ainda não estão no projeto: contribuições são
bem-vindas, no mesmo formato das fichas dos deputados federais.
