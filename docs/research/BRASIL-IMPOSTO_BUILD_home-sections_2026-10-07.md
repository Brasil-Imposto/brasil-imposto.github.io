# Seções novas da home e coluna "Vendeu ao exterior" (registro da construção, 2026-10-07)

**English summary.** Built the two home sections asked in D109 to D111 ("Por que falta dinheiro" and "O que o Brasil vende"), the 4th column "Vendeu ao exterior" in the state modal, and the D116 fix of the "Sobrou ou faltou" block.
Data comes only from `data/economy/` and `data/trade/`, packed by `build-standalone-data.py` with checks against the source files and two controls that must fail.
Checked by screenshots at 1100, 1063 and 420 px, by a page probe (sums by hand, order, toggles) and by opening the 27 state modals with no console error.

## O que foi construído

| Pedido | Onde | Como |
|---|---|---|
| "Por que falta dinheiro" (D110) | `assets/home-feed.js` (`whySection`), `assets/home-feed.css` (`.hw-*`) | seção criada pelo próprio script logo abaixo de "Maiores escândalos" (`#por-que-falta-dinheiro`), sem mexer na página do mapa. Seis blocos: os juros são a maior parte do que faltou (barra: R$ 714,4 bi de R$ 811,5 bi); por que os juros são altos e quem recebe (dívida, Selic, inflação, detentores dos títulos por R$ 100); a Previdência antes dos juros; a exportação quase não paga imposto e o que a União recebe desses setores; subsídios (imposto que deixa de entrar, maiores itens); o tamanho de cada parte (tributos de 2025 por quem arrecada). Cada bloco: título, uma frase, números, período e fontes com link. Nenhuma vez a palavra "cartão" na seção. |
| "O que o Brasil vende" (D109, D111) | `assets/home-feed.js` (`tradeSection`), `assets/home-feed.css` (`.ht-*`) | logo abaixo da anterior (`#o-que-o-brasil-vende`). Seletor próprio "2025 (ano inteiro)" e "2026 (janeiro a setembro)", com a frase de que não segue o seletor do mapa. Linha de contexto: vendeu, comprou, sobrou, peso no PIB (2025) e produtos básicos 22,8% em 2000 e 58,2% em 2025. Todos os produtos do maior para o menor (1.194 em 2025, 1.196 em 2026), 20 na tela e o botão "Mostrar todos os N produtos". Por produto: nome oficial, US$, R$ pela PTAX, parte do total; nos 50 maiores, os 3 países; barra "vai para fora / fica no Brasil" onde há produção oficial (17 linhas, com fonte e ano); preço do Brasil contra a referência do Banco Mundial em 2025 (13 produtos), com a ressalva de frete ou de tipo de cada referência. |
| Coluna "Vendeu ao exterior" (D109) | `assets/proposals.js` (`exportsCol`, `tri8`, `r8`), `assets/proposals.css` | 4ª coluna no computador e 4ª aba no celular, na cor de tinta do projeto (#14202B). Total do estado em US$ e R$, os 5 maiores produtos e "Demais produtos" (do maior para o menor, D73), o período e a regra do Comex Stat (estado que produziu, não sede da empresa). Segue o período do modal: 2026 mostra janeiro a setembro; outros anos mostram 2025, com o aviso de que antes de 2025 não há o dado por estado. Com quatro colunas lado a lado (modal a partir de 1000 px, toda janela de 1063 px ou mais) o valor vai para baixo do nome; entre 761 e 999 px as colunas ficam em duas linhas de duas. |
| "Sobrou ou faltou" coerente com "Gastou" (D116) | `assets/proposals.js` (`contasNet`) | o mesmo valor que saiu de "Gastou" (Encargos Especiais, subfunção Transferências) sai de "Entrou" e de "Saiu", com rótulos novos e uma nota no bloco; o resultado oficial não muda. Num mês, o relatório bimestral recebe o dobro da média mensal. SP, 2026 (janeiro a agosto): entrou R$ 200,3 bi, saiu R$ 181,8 bi (igual a "Gastou"), sobrou R$ 18,5 bi, como antes. |

## Dados

`docs/superpowers/tools/build-standalone-data.py` agora empacota `BI.shortfall` (49 fatos usados, com valor, unidade, período, órgão e link) e `BI.trade` (produtos, estados, parte da produção, preços e contexto, 363 KB). Checagens que param o build: cada fato igual ao arquivo de origem; detentores da dívida somam o total; União + estados + municípios somam a carga tributária; benefícios menos arrecadação do INSS de 2025 igual ao déficit; juros e resultado de janeiro a agosto de 2026 iguais aos de `data/series/union.json` (os de "A conta da União"); produtos somam o total oficial em US$ e em R$ nos dois períodos; os estados (com "Não Declarada") somam o Brasil; exportação menos importação igual ao saldo; preços de 2025 iguais ao arquivo de produtos. Controles: `--control=shortfall` e `--control=trade` mudam um valor e o build para antes de gravar (saída 1 nos dois).

## Conferências

- Builds, cada um com o código de saída lido: `build-standalone-data.py` 0; `build-post-grill-data.py` 0; `build-simulation.py` 0. `build-post-grill-round.py` não foi rodado (pedido).
- Capturas (Chrome sem janela, pela simulação da home): as duas seções em 1100 e em 420 px; modais de SC e do DF em 1100 px (quatro colunas) e em 420 px (aba "Vendeu"); SC em 1063 px (quatro colunas) e em 1062 px (duas linhas de duas). Sem texto cortado nem rolagem lateral.
- Sonda da página (1100 e 420 px): ordem das seções (escândalos, por que falta dinheiro, o que o Brasil vende, bolo); 6 blocos; "cartão" na seção 1: 0; travessões na tela: 0 (controle com um de cada: 2); toda conta fecha à mão (811,5; 96,4; 55,8; 4.127,2); detentores somam R$ 100,00; subsídios somam R$ 612,8 bi; 20, 1.194 e 1.196 produtos, em ordem decrescente (controle: a lista invertida falha); rolagem lateral: nenhuma.
- Os 27 modais (sonda com `--dump-dom`, perfil novo a cada vez): `modalOpen=true` nos 27, zero `Uncaught`, `TypeError` ou `ReferenceError` (controle: uma página com erro proposital é pega). Numa segunda sonda, nos períodos 2026, 2024, março de 2026 e mandato 2023 a 2026: coluna nova nos 27 e o resultado oficial de "Sobrou ou faltou" igual ao de antes em todos.
- Travessões nos arquivos mudados: 0 antes e 0 depois (contagem com controle).

## Para o autor

1. **"Cartão" nos nomes oficiais:** 27 posições exportadas têm "cartão" ou "cartões" no nome oficial (papel e cartão). Ficaram como a fonte escreve, porque é o nome do produto; a seção "Por que falta dinheiro" não usa a palavra.
2. **"Demais" no topo:** pela regra D73 (inclui as linhas "Demais"), "Demais benefícios" (R$ 202,5 bi) abre a lista de subsídios e "Demais produtos" abre a coluna de SC.
3. **Arredondamento que fecha (maior resto):** "Agricultura e agroindústria" aparece com R$ 79,2 bi (exato R$ 79,25 bi) para os sete itens somarem R$ 612,8 bi à mão.
4. **Links montados:** a API do Comex Stat só aceita POST, então o link é a página da documentação dela; as linhas do IBGE sem link apontam para a página da tabela no SIDRA.
5. **Ainda não feito:** a versão renderizada deste registro (render-doc) e a montagem da rodada ficam com a sessão principal.
