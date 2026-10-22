<!--
Título: em inglês, no formato type(area): what changes. Exemplo: fix(site): map legend on phones.
Um assunto por pull request. As regras completas: https://github.com/Brasil-Imposto
-->

## O que muda e por quê

<!-- O problema, a mudança e o motivo, em frases curtas. -->

## Issue relacionada

<!-- Closes #... (ou o link da discussão) -->

## Capturas de tela

<!-- Toda mudança que aparece na tela: antes e depois, no computador (1440 px) e no celular (420 px). Sem mudança visível, escreva "sem mudança na tela". -->

| | Antes | Depois |
|---|---|---|
| 1440 px | | |
| 420 px | | |

## Fontes

<!-- Todo número novo ou mudado: órgão, link, período de referência e data em que a fonte foi lida. Sem número novo, escreva "nenhum número novo". -->

## Como foi conferido

<!-- Os comandos rodados e a saída de cada um: os testes, a checagem ao centavo e o erro plantado que a checagem pegou. -->

## Lista de conferência

<!-- Todo item não marcado precisa de uma linha explicando por quê. -->

- [ ] Cada número novo tem fonte oficial com link, ano de referência e data de coleta
- [ ] O script em `pipelines/` ou `docs/superpowers/tools/` refaz o arquivo sozinho, a partir da fonte
- [ ] A checagem ao centavo passa, e o controle com um erro plantado falha (as duas saídas estão acima)
- [ ] O total bate com o total oficial da fonte
- [ ] Nenhum texto toma partido; pessoas aparecem só com o papel que têm num documento oficial
- [ ] Toda foto nova tem licença livre e crédito
- [ ] Identificadores, nomes de arquivo, chaves de JSON e commits em inglês; o texto da tela em português
- [ ] As páginas mudadas foram abertas em 1440 e 420 px de largura, e as capturas estão acima
- [ ] Todos os commits assinados (`git commit -s`, DCO)
