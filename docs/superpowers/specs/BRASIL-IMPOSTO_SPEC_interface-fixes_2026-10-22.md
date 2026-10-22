# Brasil-Imposto: defeitos de interface das três páginas publicadas

Status: **aprovada pelo mantenedor em 2026-10-22 para os tipos de defeito listados aqui**; o que ficar fora deles volta como
pergunta. Vale para Início, Os 3 Poderes e Como o dinheiro anda.

### Summary (English)

Overlays (the person sheet, the "Ver as contas do Brasil" modal, the home feed's detail sheet) sat under the site header
(z-index 1000), so their close buttons could not be clicked; the home modal could open off screen on a desktop; the jumps to
"#parlamentares" and the home's sections landed under the header. The rule: every overlay covers the whole window, header
included, its close button is visible and clickable at every width, Escape closes it, the page behind does not scroll, and focus
returns to what opened it; every in-page jump lands below the header. Proven by two probes with planted controls and a sweep
of the three pages at 1440, 1024, 768, 420 and 360 px.

## 1. A regra

1. **Camada:** modal, ficha e o fundo escuro ficam acima do cabeçalho do site (z-index 1100, contra 1000 do cabeçalho) e cobrem
   a janela inteira, cabeçalho incluído.
2. **Fechar:** o botão de fechar fica inteiro na janela e é o elemento no topo no seu centro e em quatro pontos ao redor
   (`document.elementFromPoint`), em toda largura; um clique ali fecha.
3. **Esc** fecha; **a página atrás não rola** enquanto a camada está aberta; ao fechar, **o foco volta** ao botão que abriu.
4. **Saltos dentro da página** (links para `#id` e botões como "Ver cada um ↓"): o alvo fica abaixo da borda de baixo do
   cabeçalho, por `scroll-margin-top: 80px` em todo elemento com `id`, definido uma vez, no módulo do cabeçalho.
5. **Uma fonte:** o que vale para as três páginas fica em `docs/superpowers/tools/site_chrome.py` (a margem dos saltos e a classe
   `bi-locked`, que trava a rolagem); as páginas são refeitas pelos construtores, e o CI confere que as páginas no git são o que
   eles fazem.

## 2. Onde muda

| Página | Camada | Antes | Depois |
|---|---|---|---|
| Os 3 Poderes | ficha da pessoa (`.back`) | z-index 40, o botão de fechar sob o cabeçalho; foco não voltava | z-index 1100; foco no botão de fechar ao abrir e de volta ao "Ver ficha completa" ao fechar |
| Início | "Ver as contas do Brasil" (`.modal-layer`, em `hero-mapa-3d-round-2` e `assets/modals.js`) | no computador, presa ao mapa (`position: absolute`) e podia abrir fora da tela; no celular, sob o cabeçalho; a página rolava atrás | `position: fixed` e z-index 1100 em toda largura, centrada na janela; trava a rolagem; foco como acima |
| Início | detalhe do feed (`.hf-sheet`, em `assets/home-feed.css` e `.js`) | z-index 60, sob o cabeçalho no celular; a página rolava atrás | z-index 1100; trava a rolagem; foco como acima |
| As três | saltos para `#id` | o alvo parava sob o cabeçalho | `scroll-margin-top: 80px` |

## 3. Fora desta spec

- A barra de filtros de Os 3 Poderes (`.tools`), em redesenho numa rodada própria.
- Dados e números.
- Gosto de layout e texto: voltam como pergunta no pull request.

## 4. Como conferir

- `docs/superpowers/tools/overlay-check.cjs`: as três camadas e todos os saltos, nas cinco larguras; `--control` planta cada
  falha (os z-index antigos, o painel do feed no topo da janela, `scroll-margin-top: 0`, `focus()` desligado, Esc engolido, a
  página livre para rolar) e todas as checagens têm de falhar.
- `docs/superpowers/tools/ui-sweep.cjs`: rolagem horizontal, controle coberto e texto cortado num controle, nas cinco larguras;
  `--control` planta um defeito de cada tipo, que tem de aparecer em toda página e largura.
- `docs/superpowers/tools/sheet-width-check.cjs`: o cartão "Outros" da ficha com a linha mais longa (Gilmar Mendes, "No TSE"),
  de 820 a 1280 px; `--control` volta a regra antiga.
- `site-check.cjs` nas três páginas em 1440 e 420, com `--control`; os testes de unidade; capturas olhadas em 1440 e 420.
