# Spec: a prévia social do site

**Summary (English).** When someone shares a link to the site, the preview shows one image: the logo, the name Brasil·Imposto below it
and a short description below the name, in a centred column on white, 1200 x 630 px. The description is "Para onde vai o imposto, com
dados oficiais e a fonte de cada número." in two lines, so the whole column fits inside the square centre that some chat apps crop. The
three pages get the Open Graph and Twitter card tags in their shared head block. Tests with a planted control; the PR goes to `main`,
which is production, and merges only after the maintainer's go on a PROD WARNING.

Estado: **aprovada pelo autor em 2026-10-22** (a opção 2 das opções de prévia social). Decisão de origem: D153.
Visual: `docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_social-preview-options_2026-10-22.html`, opção 2.

## O que muda

1. **Arquivo novo** `docs/superpowers/previews/assets/brand/og-image.png`: 1200 x 630 px, fundo branco; a marca (250 px), o nome
   Brasil·Imposto (Manrope 800, 74 px, o ponto verde `#12803F`) e a descrição em duas linhas (Manrope 500, 30 px, `#5B6773`, 560 px de
   largura). A coluna inteira cabe no quadrado de 630 px do centro.
2. **Etiquetas no `<head>`** das três páginas, no bloco compartilhado de `site_chrome.py` (entre os marcadores `site-chrome:css`):
   `og:site_name` (Brasil-Imposto), `og:type` (website), `og:locale` (pt_BR), `og:description` (a descrição), `og:image` com o endereço
   completo (`https://brasil-imposto.github.io/assets/brand/og-image.png`), `og:image:width` (1200), `og:image:height` (630),
   `og:image:alt` e `twitter:card` (`summary_large_image`).
3. O título de cada página continua o seu `<title>`, que os aplicativos usam quando não há `og:title`.
4. As três páginas refeitas pelos construtores de sempre.

## Como conferir

- Os testes de `pipelines/tests/test_site_chrome.py`: cada página leva as etiquetas com os valores acima, a imagem existe e mede
  1200 x 630; o controle planta uma página sem `og:image` e o teste precisa falhar.
- As três páginas em 1440 e 420 px com `site-check.cjs`; depois do deploy, as etiquetas e a imagem conferidas no ar.

## Fora desta mudança

`og:title` e `og:url` por página, `<meta name="description">`, e a imagem da organização no GitHub.
