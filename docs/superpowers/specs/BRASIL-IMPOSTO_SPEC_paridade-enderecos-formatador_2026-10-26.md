# Brasil-Imposto: a conferência do texto da tela no `ci`, os endereços limpos e o formatador

Status: **rascunho, espera o sim do autor.** Três respostas da rodada 1 que pedem uma escolha de como fazer antes do código:
a pergunta 41 (#82, Q95), a 28 (Q86) e a 8 (D174).

### Summary (English)

Three answers of round 1 that need a choice of approach before any code. (A) The CI check of the visible text (#82): on every
pull request that touches what builds the pages, both sites are built and the text of the four pages compared; a difference fails
unless the maintainer adds the label "muda-a-tela"; pull requests that touch none of it pass in seconds. (B) Clean addresses:
the three page files are renamed in the repository, every reference follows, and the old names forward, so production stays the
committed files byte for byte. (C) Ruff and Prettier, blocking: hand-written code only, generated pages and data left out, one
formatting-only pull request proven to change nothing on screen and no data, then the blocking step.

## A. A conferência do texto da tela em todo pull request (#82, pergunta 41)

- **O quê:** um passo novo do `ci` monta o site da produção duas vezes, a partir do pull request e a partir da base, abre as quatro
  páginas num navegador sem tela e compara o texto visível: a Início em 19 períodos e o painel dos 27 estados em ano, mandato e mês
  (as 100 combinações da `visible-text-probe.cjs`), e o texto inteiro de Os 3 Poderes, Como o dinheiro anda e Como ler o mapa.
- **Quando falha:** qualquer diferença falha o passo e mostra as linhas que mudaram, a menos que o pull request tenha o rótulo
  **"muda-a-tela"**, que só o mantenedor põe. Pôr ou tirar o rótulo roda o passo de novo.
- **Caminho curto:** se o pull request não mexe em nada que monta as páginas (`docs/superpowers/previews/`, as ferramentas de
  montagem, `data/`, `pipelines/`), o passo passa em segundos, sem montar nada.
- **Custo:** o navegador sem tela e o `playwright-core` entram no `ci`, fixados pela versão, como dependência só de desenvolvimento.
  Medido em 2026-10-26: a sonda leva 74 segundos nas 100 combinações, num Mac M1. No `ci`, com as duas montagens do site e a
  instalação do navegador, a estimativa é de 5 a 8 minutos por pull request que mexe nas páginas (a medir no primeiro).
- **Controle:** uma palavra trocada num construtor tem de falhar o passo; o mesmo pull request com o rótulo tem de passar.

**Decisão do autor (A1):** o passo entra como verificação obrigatória da regra do `staging`?

- (a) Sim: um pull request que muda a tela sem o rótulo não entra ⭐
- (b) Não: o passo só avisa, com o X vermelho, e o merge continua possível

Recomendação: (a). É o que a resposta 41 descreve ("uma mudança na tela passa sempre por você"); os pull requests só de texto e
de dados que não mudam a tela passam pelo caminho curto ou pela comparação sem diferença.

## B. Endereços limpos (pergunta 28)

- **O quê:** Os 3 Poderes, Como o dinheiro anda e Como ler o mapa passam a `/os-3-poderes.html`, `/como-o-dinheiro-anda.html` e
  `/como-ler-o-mapa.html`. Os nomes antigos encaminham para os novos, guardando o `?` e o `#`, como o D160 fez com a Início.
- **Como:** os três arquivos são renomeados no repositório (`git mv`), dentro de `docs/superpowers/previews/`, e todas as
  referências do código, dos testes e das ferramentas mudam no mesmo pull request (28 arquivos citam os nomes hoje; os registros
  de decisão e as pesquisas guardam o nome antigo, que é história). `build-site.py` escreve uma página de encaminhamento para cada
  nome antigo, nos dois sites.
- **Por que renomear e não trocar o nome só na montagem:** a produção continua sendo os arquivos versionados byte a byte, a regra
  que `test_build_site.py` confere hoje; trocar só na montagem quebraria essa garantia.
- **Controle:** um link para um nome antigo em qualquer página montada falha o teste; cada nome antigo, aberto no site montado,
  chega à página nova com o mesmo `?` e `#`.

Sem pergunta: a resposta 28 já escolheu os endereços.

## C. Ruff e Prettier em tudo, bloqueando (pergunta 8, D174)

- **Alcance:** o código escrito à mão. Python (`pipelines/`, `docs/superpowers/tools/`) com Ruff (formatação e checagem); JavaScript,
  CSS e as fontes HTML de `docs/superpowers/previews/src/` com Prettier. **Ficam de fora** os arquivos gerados: as páginas
  montadas, os dados de `data/` e os scripts de dados que os construtores escrevem, e o Markdown (os registros e as pesquisas, que
  o Prettier reescreveria). A lista dos gerados vem dos construtores, e um teste falha quando um arquivo que um construtor escreve
  não está na lista.
- **Largura da linha:** 140 caracteres, perto do que o código já usa (metade das linhas de Python tem até 59; 1.724 passam de 140).
- **Ordem:** primeiro um pull request só de formatação, provado sem efeito: o Ruff confere que a árvore sintática do Python não
  muda; os construtores refazem as páginas versionadas iguais; o texto visível das quatro páginas é igual (a conferência de A).
  Depois, o passo no `ci` que falha quando um arquivo não está formatado. As versões do Ruff e do Prettier ficam fixadas.
- **Risco:** um pull request grande, com quase todos os arquivos de código, que conflita com qualquer ramo aberto: entra quando não
  houver pull request de código aberto.

Sem pergunta além da largura, que segue a recomendação se o autor não disser outra.

## D. Quem faz o quê

- **Sessão local:** A, B e C, um pull request por parte, depois do sim a esta spec.
- **Autor:** o sim, a escolha A1 e o "pode" da produção (em lote, D192).
