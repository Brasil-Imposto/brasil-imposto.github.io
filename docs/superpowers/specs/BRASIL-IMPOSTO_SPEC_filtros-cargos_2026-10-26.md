# Brasil-Imposto: os filtros da lista de cargos numa aba com gaveta

Status: **aprovada pelo autor em 2026-10-26 (D191); feita e na produção no mesmo dia (#128, #142).** O desenho é a opção B da rodada 2 (D187); esta spec diz como ele entra
na página publicada.

### Summary (English)

The cargos list of Os 3 Poderes gets the design the author picked in round 2 (D187): the bar keeps the search and a Filtros tab
with the number of active filters; the tab opens a drawer (from the right on a computer, from the bottom on a phone) with
Casa, Estado, Partido and the order, closed by "Ver N pessoas"; active filters show as removable tags under the bar. Every
filter and every order stays, the new one being what goes to the person (D177); the list opens by name A to Z; people with
partial data stay in place by their published number with the "parcial" chip (D184). The drawer follows the overlay rule of
the interface-fixes spec. No number changes. Proven by a probe with real clicks at five widths and planted controls.

## 1. O que o autor decidiu

| Decisão | O quê |
|---|---|
| D177 | Todos os filtros e todas as ordens; a lista abre por Nome (A a Z) |
| D183 | Os filtros numa aba, com uma rodada de prévia antes |
| D184 | Quem tem dado parcial fica no lugar do número publicado, com a etiqueta "parcial" que o cartão já mostra |
| D187 | A opção B da rodada 2: a aba Filtros abre uma gaveta |

Rodada aprovada: `docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_cargos-filtros-r2_2026-10-26.html` (gerador
`private/filtros/build_cargos_filtros_r2.py`). O código da opção B nessa rodada é o ponto de partida, não o código final:
lá a gaveta mexe nos controles antigos escondidos; aqui ela muda o estado da página direto.

## 2. Onde muda

Só a lista de cargos de Os 3 Poderes, no arquivo publicado `docs/superpowers/previews/os-3-poderes.html`:

- **A barra (`.tools`):** a busca e a aba **Filtros**, com o número de filtros ligados (Casa diferente de Todos, Estado,
  Partido). Embaixo, uma etiqueta por filtro ligado, com um x que o tira.
- **A gaveta:** do lado direito no computador (até 400 px de largura) e de baixo para cima no celular (até 620 px). Dentro, na
  ordem: Casa (os botões de hoje, com a contagem), Estado, Partido e Ordenar por (Nome, Total por mês, Para a pessoa, Cota
  usada, e um botão com o sentido). No pé, "Limpar filtros" e o botão "Ver N pessoas", com o número da lista na hora.
- **As ordens, oito:** Nome (A a Z e Z a A); Maior e Menor total por mês; Mais e Menos para a pessoa por mês; Maior e Menor uso
  da cota em 2026. "Para a pessoa" é o valor que a ficha já mostra com esse nome (`M.own`): o total sem a cota e o gabinete.
- **A linha da contagem** diz a ordem: "722 pessoas · ordenadas por Nome (A a Z)".
- **Quem tem dado parcial:** nada muda no cartão; a ordem usa o número publicado, como hoje.
- **O código:** a gaveta muda o estado da página (`F.house`, `F.uf`, `F.party`, `F.sort`) e chama `drawList()`; os
  controles antigos saem, sem cópia escondida. O mapa de ordens de `drawList()` ganha as quatro que faltam.

## 3. A gaveta é uma camada, com a regra da spec de defeitos de interface

Cobre a janela inteira, o cabeçalho incluído (z-index 1100); o botão de fechar fica visível e clicável em toda largura; Esc, o
fundo, o x e "Ver N pessoas" fecham; a página atrás não rola; ao abrir, o foco vai para o botão de fechar e, ao fechar, volta
para a aba Filtros.

## 4. Fora desta spec

- Números e dados: nenhum muda.
- Guardar os filtros no endereço da página (para mandar um link já filtrado): pergunta para depois.
- O site em Astro (fase B4, #6) leva o mesmo desenho quando chegar.
- As outras páginas.

## 5. Como conferir

- **Uma sonda com cliques de verdade**, `docs/superpowers/tools/cargos-filters-check.cjs`, nas cinco larguras da sonda de
  camadas: abre a aba; cada uma das oito ordens dá a lista na ordem certa; Estado e Partido filtram e mostram a etiqueta e o
  número na aba; o x da etiqueta tira o filtro; Esc, o fundo e "Ver N pessoas" fecham; o foco vai e volta; sem rolagem para
  o lado; nenhum texto cortado nos controles. Com `--control`, cada falha plantada tem de ser pega: a gaveta sempre aberta (o
  defeito que a rodada 2 achou), a gaveta sob o cabeçalho, uma ordem invertida, o número da aba errado.
- **`overlay-check.cjs`** ganha a gaveta como mais uma camada.
- **O resto da página não muda:** o texto visível fora da barra e da linha da contagem é igual antes e depois, com a lista
  aberta por Nome (A a Z).
- Capturas a 1440 e 390 px, olhadas antes da entrega.

## 6. Produção

Sem chave em `data/features.json`: a mudança troca um controle que já existe, não acrescenta uma funcionalidade. Vai ao
`staging` por pull request e à produção pela promoção por tarefa (D166), com o aviso de produção e o "pode" do autor.

## 7. Quem faz o quê

- **Sessão local (2026-10-26):** o código, a sonda e o pull request para o `staging`, depois do sim do autor a esta spec.
- **Autor:** o sim a esta spec e o "pode" da promoção.
