# Brasil-Imposto: cabeçalho único, rodapé e carregamento do mapa

Status: **aprovada (D152, 2026-10-22).** Escolhas do mantenedor: cabeçalho A (barra fixa), carregamento L1 (progresso real) e o rodapé como desenhado. Vale para as três páginas publicadas: Início, Os 3 Poderes e Como o dinheiro anda.

### Summary (English)

One header and one footer for the three published pages, from a single source, and a real-progress loader while the map's data downloads. The header is a fixed white bar with the links Início, Os 3 Poderes, Como o dinheiro anda and Código aberto, the current page underlined, and a Menu button on phones. "Rede (prévia)" leaves the header and lives in the new footer. The loader shows the true download percentage, computed from the bytes received against the file size written into the page at build time.

## 1. Cabeçalho (opção A)

- **Uma fonte só** para as três páginas: o mesmo trecho de HTML e CSS entra nas três no build, nunca copiado à mão em três lugares. O resultado visível é idêntico nas três, menos a marca da página atual.
- **Barra:** 62 px de altura; fundo `rgba(255,255,255,.94)` com `backdrop-filter: blur(8px)`; linha de 1 px `#E3E7EC` embaixo; `position: sticky; top: 0`, acima do mapa; margem lateral de 22 px (14 px no celular).
- **Marca:** a bandeira (26 x 19 px, cantos de 4 px) e "Brasil·Imposto" em Manrope 800, 15 px, com o ponto em verde `#12803F`; leva ao Início.
- **Links:** Início, Os 3 Poderes, Como o dinheiro anda e Código aberto (o repositório no GitHub). Manrope 700, 13 px, cor `#5B6773`, 18 px entre eles. Página atual: cor `#14202B` e sublinhado `box-shadow: 0 2px 0 #14202B` com 3 px de espaço.
- **Sem "Rede (prévia)"** no cabeçalho. **Sem botão Apoie agora:** ele entra depois, com spec própria (D123, D125), na ponta direita.
- **No Início:** o cabeçalho solto de hoje sai; o mapa começa logo abaixo da barra. O cartão "Entenda a ECONOMIA do Brasil" e o painel do período ficam onde estão em relação ao mapa; nada mais do Início muda.
- **Celular (até 820 px):** a marca e um botão "Menu" (pílula branca com linha `#E3E7EC`, Manrope 700 13 px e o ícone de três traços). Ele abre, logo abaixo da barra, uma folha branca (`rgba(255,255,255,.98)`) com os quatro links (Manrope 700, 17 px, 11 px acima e abaixo, linha entre eles, a página atual em verde) e a nota "Rede do dinheiro (prévia), decisões e licenças ficam no rodapé."; aberto, o botão diz "Fechar". Fecha com Esc e com toque fora; `aria-expanded` e foco corretos.

## 2. Rodapé

- O mesmo nas três páginas, no fim da página: fundo branco, linha `#E3E7EC` em cima, 22 px por 24 px de margem interna, na largura do conteúdo.
- À esquerda, a marca e a linha "Dados oficiais, com fonte em cada número. Código AGPL-3.0, dados CC BY 4.0." (12,5 px, `#5B6773`).
- Os links (Manrope 700, 13,5 px, `#5B6773`, 18 px entre eles; empilham no celular): **Rede do dinheiro (prévia)** (o cartão da rede que já está no fim do Início), **Código aberto no GitHub** (o repositório), **Decisões do projeto** (`docs/decisions/README.md`), **Como ajudar** (`CONTRIBUTING.md`) e **Licenças** (a seção Licenças do README).
- O cartão da rede continua onde está no Início; só o link do cabeçalho sai.

## 3. Carregamento do mapa (L1, progresso real)

- Enquanto os dados do mapa chegam, um cartão no centro da área do mapa: branco, linha `#E3E7EC`, cantos de 14 px, 16 por 18 px de margem interna, sombra `0 10px 30px rgba(20,32,43,.08)`, largura `min(300px, 86%)`.
- Texto "Carregando os dados oficiais do mapa" (Manrope 800, 14 px); barra de 8 px com fundo `#EDF1F4` e preenchimento verde `#12803F`, cantos redondos; embaixo, "27 estados, desde 2019" (12,5 px, `#5B6773`) à esquerda e a porcentagem (800, `#14202B`, algarismos de largura fixa) à direita.
- **Progresso verdadeiro:** o arquivo de dados é baixado com `fetch` e lido por partes; a porcentagem é a dos bytes recebidos sobre o tamanho do arquivo sem compressão, escrito na página no build (o navegador entrega os bytes já descomprimidos, e o `Content-Length` do Pages é o tamanho comprimido). Depois o conteúdo roda como o script de hoje. A porcentagem nunca volta e nunca mostra 100% antes de o mapa estar pronto; o cartão some quando a página marca `body[data-ready="1"]`.
- **Falha:** se o download falhar, o cartão diz "Não foi possível carregar os dados." com um botão "Tentar de novo". **Tamanho desconhecido** (por exemplo, numa prévia local com outro arquivo): barra sem porcentagem, nunca um número inventado.
- Nada sai do lugar quando o cartão some.

## 4. Como conferir

- A auditoria de texto visível do Início (`--audit` e o controle `--plant`) e a sonda de Os 3 Poderes continuam passando.
- "Rede (prévia)" aparece 0 vezes no cabeçalho e 1 vez no rodapé de cada página; o trecho do cabeçalho é igual nas três páginas publicadas, menos a marca da página atual (teste com controle: uma diferença plantada num dos três tem de ser pega).
- Carregamento: com a rede limitada no navegador de teste, a porcentagem só sobe e chega a 100% só com o mapa pronto; o controle é um tamanho errado escrito na página, que o teste tem de pegar.
- Capturas em 1440 e 420 px das três páginas: o cabeçalho, o rodapé, o menu aberto no celular e o cartão de carregamento no meio do caminho, olhadas antes de entregar; depois do merge, o site no ar nas duas larguras.

## 5. Fora desta spec

O botão Apoie, as fases do site em Astro (esta mudança fica nas páginas publicadas de hoje e nos construtores delas) e qualquer mudança de número ou de texto além do cabeçalho, do rodapé e do cartão de carregamento.
