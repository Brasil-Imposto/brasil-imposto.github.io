# Spec: o logo no site e os ícones da aba

**Summary (English).** Put the decided logo (D153) into the published site: the shared header and footer show the mark instead of the
flag image, and the three pages get a tab icon (favicon.ico with drawings made for 16 and 32 px) and an Apple touch icon. One source
(`site_chrome.py`), the pages rebuilt by their builders, tests with a planted control, screenshots at 1440 and 420. The PR goes to `main`,
which is production: it merges only after the maintainer's go on a PROD WARNING.

Estado: **aprovada e no ar desde 2026-10-22 (PR #37).** Data: 2026-10-22. Decisão de origem: D153 (logo decidido em 2026-10-22: o Resplendor
em ouro sol, as estrelas de prata viradas para fora, o globo com o céu da bandeira e o brilho leve; o ponto verde entre Brasil e Imposto).
Visual de referência: `docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_logo-final_2026-10-22.html`, seção "No site".

## O que muda

1. **Arquivos novos** em `docs/superpowers/previews/assets/brand/` (o workflow `pages.yml` já publica a pasta `assets/` inteira):
   `brasil-imposto-logo.svg` (a marca para fundo claro, 22 KB), `favicon.ico` (os desenhos de 16 e 32 px num arquivo só, 2 KB) e
   `apple-touch-icon.png` (180 px, fundo branco, 19 KB). Os originais e o gerador ficam fora do repositório público
   (`private/logo/`), como os das rodadas.
2. **Cabeçalho e rodapé** (`docs/superpowers/tools/site_chrome.py`): em `header()` e `footer()`, a imagem da bandeira
   (`assets/flags/br.svg`, `alt="Bandeira do Brasil"`) vira a marca (`assets/brand/brasil-imposto-logo.svg`, `alt=""`, porque o nome vem
   escrito logo ao lado). No CSS, `.bi-brand img` passa de 26 x 19 px com borda arredondada e contorno para 30 x 30 px, sem borda e sem
   contorno. O nome e o ponto verde (`#12803F`) ficam como estão.
3. **Ícones da aba**: o bloco compartilhado do `<head>` (o que fica entre os marcadores `site-chrome:css`) ganha
   `<link rel="icon" href="assets/brand/favicon.ico" sizes="16x16 32x32">` e
   `<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">`. Nenhum marcador novo.
4. **As três páginas refeitas** pelos construtores de sempre: `build-site-chrome.py` (Os 3 Poderes, Como o dinheiro anda) e
   `build-platform-preview.py` (Início).

## Como conferir

- `pipelines/tests/test_site_chrome.py` continua passando (cada página igual ao módulo).
- Um teste novo: cada uma das três páginas aponta para a marca e para os dois ícones, e os três arquivos existem; o controle planta uma
  página com o caminho errado e o teste precisa falhar.
- Capturas das três páginas em 1440 e 420 px, olhadas; o ícone visto na aba do Chrome.

## Fora desta mudança

A imagem de prévia social (`og:image`), um web manifest, o site novo em Astro (vai usar os mesmos arquivos quando chegar lá), o README e
a imagem da organização no GitHub (o autor sobe o PNG; a API do GitHub não troca o avatar de uma organização).

## Entrega

Um ramo `feat/logo-on-site` a partir da `main`, commits com `-s` (DCO), um PR. A `main` publica o site no ar: antes do merge, um aviso
🚨 PROD WARNING com o que entra, o que pode quebrar e as conferências, e o merge só com o "pode" do autor.
