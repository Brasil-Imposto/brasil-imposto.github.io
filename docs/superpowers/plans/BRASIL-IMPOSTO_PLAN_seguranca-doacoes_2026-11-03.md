# Plano: segurança da doação em cripto, fases 1 a 5

> **Para quem executa:** siga as tarefas na ordem e marque os passos (`- [ ]`). **Cada ataque é um teste visto falhando antes da defesa, com controle plantado** (seção 14 da spec): o teste falha no código de hoje, a defesa entra, o teste passa, e o controle (o mesmo teste contra um defeito plantado) tem de falhar pelo motivo plantado. Texto de tela em português do Brasil; identificadores, chaves JSON e commits em inglês, todo commit com `--signoff`. Sem travessão em nada escrito. Nenhum endereço de e-mail. Código num ramo cita só decisões já públicas nesse ramo (`test_decision_refs`). Nenhum segredo impresso; uma frase de recuperação nunca entra numa sessão.

**Objetivo:** fechar as fraquezas da doação em cripto e montar a vigilância da spec, fase por fase, cada fase um pull request para o `staging` com o deploy à mão conferido na página no ar.

**Arquitetura:** o site segue estático no GitHub Pages. Fase 1: nenhum texto de dado vira HTML, uma CSP numa meta (a forma da Uniswap) bloqueia a classe, todo script sai para arquivo, fontes e three.js servidos pelo próprio site. Fase 2: as telas de D220. Fase 3: regras do repositório e o `guard`. Fase 4: o monitor em `Brasil-Imposto/monitor`, agendamentos do GitHub que falham quando acham algo (o e-mail de falha é o alarme, D216). Fase 5: folha de resposta, `security.txt`, registro de endereços.

**Tecnologia:** Python 3 (`unittest`, construtores do site), JavaScript sem empacotador, `node --test`, `playwright-core` 1.58.2 nas sondas (já fixado em `docs/superpowers/tools/package.json`), ESLint com `eslint-plugin-no-unsanitized`, GitHub Actions.

**Spec:** `BRASIL-IMPOSTO_SPEC_seguranca-doacoes_2026-11-02.md` (aprovada D217, auditada D218, fechada D219 e D220). Seção 14 é a lista de ataques; as linhas R1, R2, R3, B1, L1, P1, P2, P7, P9, C1, C5, C6, A1 e S1 aparecem abaixo com o mesmo nome. **Desenho das telas da fase 2:** a rodada `seguranca-r1` (D220), `docs/superpowers/previews/BRASIL-IMPOSTO_DESIGN_seguranca-r1_2026-11-02.html`, gerador `private/security/build_seguranca_r1.py`.

**Onde mora:** este plano e a spec ficam em `private/security/` até o pull request da fase 1, que os leva para `docs/superpowers/plans/` e `docs/superpowers/specs/` (o código passa a citar a spec).

**Deploy do staging:** um push no `staging` não publica nada (`STAGING_DISPATCH_TOKEN` não existe; o `staging-dispatch.yml` sai verde sem publicar). O site de testes fica fora do ar (D214) e só liga para testar:

```bash
gh api -X POST repos/Brasil-Imposto/staging/pages -f build_type=workflow   # liga
gh workflow run deploy.yml -R Brasil-Imposto/staging                       # publica o staging
gh api -X DELETE repos/Brasil-Imposto/staging/pages                        # desliga (a página dá 404 depois de cerca de 7 minutos)
```

A prova é a página no ar (`curl` com `?n=<hora>` e uma abertura nova no Chrome sem tela), nunca o run verde.

**Merge:** só a sessão que abriu o pull request faz commit nele ou o une (D164). Antes de unir, um script lê a conclusão de cada verificação e recusa se alguma não for `success` (`cancelled` e `timed_out` são vermelhos).

---

## O que mudou ao rodar a fase 1 (2026-11-03)

- **Mais pontos do que o laboratório:** a carga em todo texto de exibição (254.144 textos em 15.045 campos) achou, além dos três de 2026-11-01, o nome do produto e a unidade em `home-trade.js` e o nome do município no mapa (`statemap.js`). Antes: 7 de 8 páginas com injeção; depois: 0 de 8, com 2.662 textos envenenados aparecendo como texto.
- **A CSP é por montagem:** a primeira versão listava o script da prévia da rede (`3d-force-graph`, só no staging) em toda página da produção, e o teste de vazamento de chaves (`test_build_site.py`) acusou. `csp.meta(profile)` lista o script de uma chave só onde ela está ligada.
- **O script do menu é por montagem:** `assets/bi-chrome.js` versionado é o da produção; o `build-site.py` escreve o do staging na pasta de saída, como a faixa do staging (`assets/staging-strip.js`), que também era inline.
- **O `bi-data.js` sem `blob:` (1.7):** medido com os cabeçalhos do Pages, desce uma vez numa janela normal (cache em disco) e duas numa janela anônima (o cache em memória não guarda 19 MB). Vai ao autor como fato.
- **O verificador de scripts de fora tinha um buraco:** não via `import 'url';`. O controle novo pegou; o regex agora pega.
- **Dependabot:** não vigia `docs/superpowers/tools/` (só `/` e `/site`); a 1.11.2 estava errada. Acrescentar é mudança à parte, levada ao autor.
- **Sondas antigas:** `overlay-check.cjs` e `ui-sweep.cjs` precisam do Chromium inteiro em `CHROME_HEADLESS` (o mapa 3D não fica pronto no Chrome sem cabeça sem as opções do SwiftShader); assim, 90 de 90 e 0 achados.

## O que mudou ao rodar as fases 2 a 5 (2026-11-03 e 04, D221 e D222)

- **Fase 2 (#174):** cada caso visto falhando no `staging` antes (12 de 48 em `cripto-check.cjs`, 8 de 17 nos testes do núcleo, os da pausa). O caso "erro antes da confirmação" precisou clicar de novo para falhar no código velho. A frase desenhada "Já avisamos o Brasil-Imposto" ficou de fora: depois de D219 a página não manda aviso. A regra dos métodos de carteira de `test_support.py` passou a ler só o que entra no `request` de uma carteira, para a leitura dos nós públicos não contar como chamada de carteira. A rodada antiga não renderiza mais; a comparação foi contra o código e o CSS dela.
- **Fase 3 (#175 e `Brasil-Imposto/staging#4`):** o `guard` copia a forma do glsec (o rótulo sai a cada push; a verificação lê a etiqueta na hora), em vez das datas de etiqueta e push do esboço da 3.4.2. O CODEOWNERS já dava tudo ao time (`*`): as linhas dos caminhos do `guard` entraram para quando houver donos por área. A configuração mudou pela API depois do merge, e `settings-check.py` ficou verde; R1 e R3 provados nos #177 e #178.
- **Fase 5 (#176) entrou antes da fase 3:** não dependia dela, e o `guard` passou a valer a partir do merge do #175.
- **Fase 4 em parte:** `Brasil-Imposto/monitor` com `chain` (C1 e C5) e `heartbeat`; o estado no ramo `state`. O A1 vigia a `chain` com 45 minutos até a conferência de 5 minutos existir. A conferência dos arquivos servidos segue D222; a foto da configuração espera o GitHub App do autor.
- **D222 e D223:** a sessão põe a etiqueta `seguranca-revisada` depois de listar no pull request os caminhos sensíveis (D223 mudou D222, item 1); a produção espera a aprovação dele no ambiente, no lote.

## Escolhas do plano e quem as usa (D218)

O que a spec deixou para o plano decidir, cada escolha com quem a usa, lido na fonte:

| Escolha | Quem usa (lido em 2026-11-03) |
|---|---|
| `style-src 'self' 'unsafe-inline'`, `img-src * blob: data:`, `form-action 'none'` | Uniswap, `apps/web/public/csp.json` no repositório `Uniswap/interface` (styleSrc, imgSrc, formAction) |
| Fonte de script com caminho exato (o arquivo do CDN, não o domínio todo) | Uniswap, mesmo arquivo: `fontSrc` traz `https://fonts.gstatic.com/s/inter/v18/*` |
| three.js servido pelo próprio site, sem mapa de importação | Uniswap, mesmo arquivo: `scriptSrc` é `'self'`, `'wasm-unsafe-eval'` e um host de captcha; todo o código do app sai do próprio site. Um mapa de importação inline é código inline: a CSP só de origens o bloqueia, e não existe mapa de importação em arquivo. Security Alliance, "Third-Party Script Security": "self-hosting removes it" |
| Escapar e proibir HTML sem escape, com uma lista que só encolhe para o que já existe | Firefox (`no-unsanitized` em erro); a lista é o recurso "bulk suppressions" do próprio ESLint (ler a página da documentação do ESLint no passo 1.4.1 antes de usar) |
| `object-src 'none'`, `base-uri 'none'` | Texto da spec aprovada (seção 8) |

Tudo o mais que aparecer no código sem quem o use vira pergunta ao autor dizendo que não há precedente (D218).

---

## Arquivos

| Arquivo | O que faz | Fase |
|---|---|---|
| `docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_seguranca-doacoes_2026-11-02.md`, `docs/superpowers/plans/BRASIL-IMPOSTO_PLAN_seguranca-doacoes_2026-11-03.md` | A spec e este plano, saídos de `private/security/` | 1 |
| `docs/superpowers/tools/poison-data.py` | Novo. Cópia envenenada de um site montado (todo texto de dado ganha a carga) | 1 |
| `docs/superpowers/tools/poison-check.cjs` | Novo. P1: abre cada página envenenada, clica, conta cada `img[src="x"]` que entra | 1 |
| `docs/superpowers/tools/static-server.cjs` | Novo. Servidor local das sondas (fila grande; tira a CSP com `--no-csp` para o controle de P2) | 1 |
| `docs/superpowers/tools/csp.py` | Novo. A política, uma fonte só | 1 |
| `docs/superpowers/tools/csp-check.cjs` | Novo. P2 e zero violações de CSP em cada página e na vista da cripto | 1 |
| `docs/superpowers/tools/fonts-check.cjs` | Novo. P9: nenhum pedido ao Google Fonts | 1 |
| `docs/superpowers/tools/vendor-three.py`, `vendor-fonts.py` | Novos. Baixam, conferem o hash e gravam os arquivos de fora | 1 |
| `docs/superpowers/tools/eslint.config.mjs`, `eslint-suppressions.json` | Novos. A regra do Firefox e a lista do que já existe | 1 |
| `docs/superpowers/previews/assets/vendor/three/` | Novo. Os 7 módulos do three.js 0.170.0 e a licença | 1 |
| `docs/superpowers/previews/assets/fonts/` | Novo. Manrope e JetBrains Mono (OFL 1.1), `manrope.css` e `jetbrains-mono.css` | 1 |
| `docs/superpowers/previews/assets/bi-chrome.js`, `bi-loader.js`, `home-map.js`, `map-notes-page.js`, `dinheiro-page.js`, `federal-cards.js`, `tres-poderes-page.js`, `forward.js` | Novos. Os scripts que hoje são inline | 1 |
| `docs/superpowers/tools/site_chrome.py`, `map_loader.py`, `build-site.py`, `build-simulation.py`, `build-platform-preview.py`, `build-notes-page.py`, `apoie.py` | Escrevem `<script src>` no lugar do inline, a meta da CSP, a folha de fontes | 1 |
| `docs/superpowers/previews/assets/federal-section.js`, `proposals.js`, `modals.js`, `bi-cripto.js`, `build-standalone-data.py` | Escape, ícones conferidos, `onerror` por ouvinte, ícone da carteira só `data:image` | 1 |
| `pipelines/tests/test_csp.py`, `test_vendor_three.py`, `test_icons.py` | Novos | 1 |
| `.github/workflows/ci.yml` | Novo job `security`: ESLint, P1, P2, P9 | 1 |
| `docs/superpowers/previews/assets/bi-cripto.js`, `bi-cripto-core.js`, `apoie.py`, `support_data.py`, `data/support.json` | Defeitos do envio, endereço em grupos de 4, `"paused"`, conferência na rede, cartões | 2 |
| `.github/workflows/guard.yml`, `.github/scripts/guard.py`, `.github/guard-paths.txt`, `.github/CODEOWNERS` | O `guard` e os donos dos caminhos sensíveis | 3 |
| `docs/superpowers/tools/build-manifest.py`, `.github/workflows/pages.yml` | O manifesto de cada publicação | 3 |
| `docs/superpowers/tools/settings-check.py` | Novo. Confere rulesets e política de ações dos dois repositórios | 3 |
| `Brasil-Imposto/monitor` (repositório novo) | `pins.json`, `checks/*.py`, `tests/`, workflows | 4 |
| `.github/workflows/monitor-watch.yml` | A1: o monitor rodou há menos de três intervalos da conferência mais frequente | 4 |
| `docs/security/BRASIL-IMPOSTO_RUNBOOK_resposta-incidente_2026-11-03.md`, `SECURITY.md`, `docs/superpowers/previews/.well-known/security.txt` | Folha de resposta, registro de endereços, `security.txt` | 5 |

---

## Tarefa 0: dono, ramo e linha de base

- [ ] **0.1** Conferir que ninguém mais tem a tarefa (D164): `gh pr list --state open`, `git ls-remote --heads origin | grep -iE 'segur|secur'`, `ListAgents` e as transcrições das sessões irmãs. Achou dono: parar e avisar o autor. (Feito em 2026-11-03: nenhum.)
- [ ] **0.2** Ramo da fase a partir do `staging`, numa worktree dentro do projeto:

```bash
cd ~/Documents/Brasil-Imposto && git fetch origin -q
git worktree add .worktrees/seguranca-fase-1 -b fix/seguranca-fase-1 origin/staging
```

- [ ] **0.3** Linha de base, antes de qualquer mudança, guardada em `private/security/baseline/` (fora do git): a suíte inteira (`python3 docs/superpowers/tools/check-all.py`, código de saída guardado), as duas montagens (`build-site.py --profile production` e `--profile staging`), e as sondas que já existem contra a montagem de staging: `apoie-check.cjs`, `cripto-check.cjs`, `site-check.cjs`, `visible-text-probe.cjs --audit`. Fotos das quatro páginas e da vista da cripto a 1440 e 420 px (a comparação pixel a pixel da fase 1 parte delas).

---

## Fase 1: nada de dado vira código, CSP da Uniswap, fontes e scripts no próprio site

Nenhum texto de tela muda nesta fase (a verificação `visible-text` tem de dar zero diferença).

### Tarefa 1.1: a spec e o plano entram no repositório

- [ ] **1.1.1** Copiar `private/security/BRASIL-IMPOSTO_SPEC_seguranca-doacoes_2026-11-02.md` para `docs/superpowers/specs/` e este plano para `docs/superpowers/plans/`. Na spec, a linha de status ganha: "Entrou no repositório no pull request da fase 1, que fecha o texto rodando como código." Os relatórios `BRASIL-IMPOSTO_RESEARCH_*` seguem em `private/` (listam fraquezas que só fecham nas fases 3 e 4).
- [ ] **1.1.2** `python3 -m unittest pipelines/tests/test_decision_refs.py -v` (sem `-I`: o teste importa `pipelines`): toda decisão citada já está no registro público (D204 a D220 estão desde o #171).

### Tarefa 1.2: P1, o laboratório de dados envenenados vira teste (vermelho primeiro)

**Arquivos:** criar `docs/superpowers/tools/poison-data.py`, `docs/superpowers/tools/static-server.cjs`, `docs/superpowers/tools/poison-check.cjs`.

- [ ] **1.2.1** O envenenador. Todo texto de exibição de todo arquivo de dados (os `assets/*.js` que são uma atribuição de JSON, os `assets/*.json` e o bloco `#bi-cripto-data` de cada página) ganha a carga que quebra texto e atributo. Identificador (uma palavra ASCII sem espaço, código, número, data, cor, caminho de arquivo) fica como está, senão a página não acha o que procura e o teste fica verde sem ver nada.

```python
"""Writes a poisoned copy of a built site (spec seguranca-doacoes, section 14, attack P1): every display text of every data
file ends with PAYLOAD, so a text that reaches a page as HTML instead of text inserts an <img src="x">. poison-check.cjs
serves the copy.

Run: python3 docs/superpowers/tools/poison-data.py <built site> <out>
"""
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

PAYLOAD = '"\'><img src="x" onerror="window.__xss=1">'
PER_FIELD = 150   # texts poisoned per field: every field covered and the page still loads (2026-11-01: 110 MB crashed the browser)
ASSIGN = re.compile(r'^\s*((?:window\.)?[A-Za-z_$][\w$.]*\s*=\s*)(.*?);?\s*$', re.S)
DISPLAY_WORD = re.compile(r'[A-Z][a-z]{2,}')


def is_display(s):
    """A text a person reads: has a space, a letter outside ASCII, is markup or a link, or is one capitalized word."""
    return (" " in s or any(ord(ch) > 127 and ch.isalpha() for ch in s) or s.startswith("<") or s.startswith("http")
            or bool(DISPLAY_WORD.fullmatch(s)))


def poison(value, path, seen):
    if isinstance(value, dict):
        return {k: poison(v, f"{path}.{k}" if not k.isdigit() else f"{path}.#", seen) for k, v in value.items()}
    if isinstance(value, list):
        return [poison(v, f"{path}[]", seen) for v in value]
    if isinstance(value, str) and is_display(value) and seen[path] < PER_FIELD:
        seen[path] += 1
        return value + PAYLOAD
    return value


def main(src, out):
    src, out = Path(src), Path(out)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out)
    seen = Counter()
    for f in sorted((out / "assets").glob("*.js")) + sorted((out / "assets").glob("*.json")):
        text = f.read_text(encoding="utf-8")
        m = ASSIGN.match(text) if f.suffix == ".js" else None
        body, head = (m.group(2), m.group(1)) if m else (text, None)
        try:
            data = json.loads(body)
        except ValueError:
            continue   # code, not data
        data = poison(data, f.name, seen)
        dumped = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        f.write_text((head + dumped + ";\n") if head else dumped, encoding="utf-8")
    block = re.compile(r'(<script type="application/json" id="bi-cripto-data">)(.*?)(</script>)', re.S)
    for page in sorted(out.glob("*.html")):
        t = page.read_text(encoding="utf-8")
        m = block.search(t)
        if not m:
            continue
        data = poison(json.loads(m.group(2)), "bi-cripto-data", seen)
        dumped = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        page.write_text(t[:m.start(2)] + dumped + t[m.end(2):], encoding="utf-8")
    fields, texts = len(seen), sum(seen.values())
    print(f"poisoned {texts} texts in {fields} fields")
    if texts < 5000:
        raise SystemExit("poison-data: fewer than 5,000 texts poisoned; the poisoner is broken, not the site")


if __name__ == "__main__":
    main(*sys.argv[1:3])
```

Atenção: o bloco `#bi-cripto-data` envenenado não pode trocar os endereços (são uma palavra ASCII sem espaço, então `is_display` os deixa); a sonda confere isso.

- [ ] **1.2.2** O servidor das sondas (o `http.server` do Python derruba conexão numa rajada, padrão aprendido de 2026-11-01):

```js
// A static server for the probes: no queue limit, and --no-csp strips the CSP meta so P2's control can run the same page without it.
const http = require('http'), fs = require('fs'), path = require('path');
const [root, port = '8791', flag] = process.argv.slice(2);
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.txt': 'text/plain', '.geojson': 'application/json' };
http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (p.endsWith('/')) p += 'index.html';
  const f = path.join(root, path.normalize(p));
  if (!f.startsWith(path.resolve(root))) { res.writeHead(403); return res.end(); }
  fs.readFile(f, (e, b) => {
    if (e) { res.writeHead(404); return res.end(); }
    if (flag === '--no-csp' && f.endsWith('.html')) b = Buffer.from(String(b).replace(/<meta http-equiv="Content-Security-Policy"[^>]*>/, ''));
    res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' });
    res.end(b);
  });
}).listen(+port, '127.0.0.1', () => console.log(`serving ${root} on ${port}${flag ? ' ' + flag : ''}`));
```

- [ ] **1.2.3** A sonda P1, a partir de `private/security/lab/poison.cjs` (mesmas páginas, mesmos cliques), com três mudanças: lança o próprio servidor, falha com código de saída, e tem `--control`. O controle planta um buraco de verdade: na cópia servida, a função `esc` do script de Os 3 Poderes vira identidade; a sonda tem de acusar.

```js
// P1 (spec seguranca-doacoes, section 14): poisoned data in every text, and nothing it carries may become an element on any page.
// Run: node docs/superpowers/tools/poison-check.cjs <poisoned site> [--control]
const { chromium } = require('playwright-core');
const { spawn } = require('child_process'), fs = require('fs'), path = require('path');
const [site, mode] = process.argv.slice(2), PORT = 8792, base = `http://127.0.0.1:${PORT}/`;
const PAGES = [['os-3-poderes.html', 300], ['como-o-dinheiro-anda.html', 120], ['como-ler-o-mapa.html', 60], ['index.html', 150],
  ['index.html?open=SC', 150], ['index.html?open=DF', 150], ['index.html?modal=brasil', 80], ['index.html#apoie-cripto?moeda=USDT&rede=tron&valor=10', 20]];
const MUST_SHOW = ['os-3-poderes.html', 'como-o-dinheiro-anda.html', 'index.html?open=SC'];   // the poison has to reach these screens as text
if (mode === '--control') {   // the planted hole: Os 3 Poderes stops escaping
  const f = path.join(site, 'assets', 'tres-poderes-page.js'), t = fs.readFileSync(f, 'utf8');
  const esc = /const esc = \(s\) => [^\n]*;/;
  if (!esc.test(t)) throw new Error('control: esc() not found in tres-poderes-page.js');
  fs.writeFileSync(f, t.replace(esc, "const esc = (s) => String(s == null ? '' : s);"));
}
(async () => {
  const server = spawn(process.execPath, [path.join(__dirname, 'static-server.cjs'), site, String(PORT)], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 400));
  let injected = 0, failedShow = 0, total = 0;
  try {
    for (const [u, nClicks] of PAGES) {
      const b = await chromium.launch({ args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--js-flags=--max-old-space-size=4096'] });
      try {
        const c = await b.newContext({ viewport: { width: 1280, height: 860 } });
        await c.route('**/*', (r) => (r.request().url().startsWith(base) || /cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net/.test(r.request().url()) ? r.continue() : r.abort()));
        const p = await c.newPage();
        await p.addInitScript(() => { window.__sinks = 0; new MutationObserver((ms) => { for (const m of ms) for (const n of m.addedNodes) if (n.nodeType === 1 && (n.matches?.('img[src="x"]') || n.querySelector?.('img[src="x"]'))) window.__sinks++; }).observe(document, { childList: true, subtree: true }); });
        await p.goto(base + u, { waitUntil: 'domcontentloaded', timeout: 120000 });
        await p.waitForFunction(() => !document.querySelector('script[type="text/x-bi-deferred"]') || document.querySelector('.bi-loader[data-state="error"]'), null, { timeout: 90000 }).catch(() => {});
        await p.waitForTimeout(2500);
        await p.evaluate(async (max) => { let n = 0; const all = [...document.querySelectorAll('button, [role="button"], summary, a[href^="#"], [data-id], [data-uf], [data-case], tr[data-id], li[data-id]')].filter((e) => e.getClientRects().length && !e.closest('header') && !e.closest('.bi-header')).slice(0, max);
          for (const e of all) { try { e.click(); n++; } catch (_) {} if (n % 10 === 0) await new Promise((r) => setTimeout(r, 30)); } }, nClicks);
        await p.waitForTimeout(1500);
        const r = await p.evaluate(() => ({ xss: !!window.__xss, added: window.__sinks, now: document.querySelectorAll('img[src="x"]').length, shown: (document.body.innerText.match(/<img src="x"/g) || []).length }));
        const bad = r.xss || r.added || r.now;
        injected += bad ? 1 : 0; total += r.shown;
        if (MUST_SHOW.includes(u) && !r.shown) failedShow++;
        console.log(`${bad ? 'INJECTED' : 'clean   '} ${u.padEnd(52)} ${JSON.stringify(r)}`);
      } finally { await b.close().catch(() => {}); }
    }
  } finally { server.kill(); }
  console.log(`${injected} of ${PAGES.length} pages injected; ${total} poisoned texts shown as text`);
  if (failedShow) { console.log('BROKEN PROBE: the poison did not reach a screen it must reach'); process.exit(2); }
  if (mode === '--control') { console.log(injected ? 'control caught' : 'BROKEN CONTROL: the planted hole was not seen'); process.exit(injected ? 0 : 1); }
  process.exit(injected ? 1 : 0);
})();
```

O controle depende de `assets/tres-poderes-page.js`, que nasce na tarefa 1.5; até lá, `--control` planta em `os-3-poderes.html` com a mesma expressão (trocar o caminho na linha `const f`, e voltar depois da 1.5).

- [ ] **1.2.4** Rodar contra o código de hoje e ver vermelho:

```bash
T=docs/superpowers/tools; S=$TMPDIR/bi-stg; P=$TMPDIR/bi-poison
python3 $T/build-site.py --profile staging --out $S && python3 $T/poison-data.py $S $P
(cd $T && node poison-check.cjs $P) > $TMPDIR/p1.log 2>&1; echo "exit: $?"; tail -12 $TMPDIR/p1.log
```

Esperado: `exit: 1`, com INJECTED em Os 3 Poderes, Como o dinheiro anda e `index.html?open=SC` e `?open=DF` (o laboratório de 2026-11-01). Depois rodar `build-platform-preview.py` e `build-notes-page.py` sem variável e conferir `git status` limpo (armadilha do `build-site.py`).

### Tarefa 1.3: escapar cada texto que a sonda pega

**Arquivos:** `docs/superpowers/previews/assets/federal-section.js`, o script de Os 3 Poderes (inline em `os-3-poderes.html` até a 1.5; a fonte é o construtor que o escreve, achar com `grep -rln "const D = window.TP3" docs/superpowers/tools docs/superpowers/previews`), `docs/superpowers/tools/build-standalone-data.py`, `pipelines/tests/test_icons.py`.

- [ ] **1.3.1** Achar cada ponto: rodar `private/security/lab/where.cjs` contra a cópia envenenada (ele imprime o `outerHTML` do pai de cada `img[src="x"]`). Os três de 2026-11-01: o rótulo de Os 3 Poderes ("Média por mês"), `bars()` em `federal-section.js` (o rótulo `l` e a nota `s` entram crus) e `icon()` em `proposals.js` (o SVG do ícone vem do dado).
- [ ] **1.3.2** `federal-section.js`, `bars()`: `${esc(l)}` e `<small>${esc(s)}</small>`. Os 3 Poderes: o rótulo que a sonda mostrar passa por `esc()` (a função já existe no mesmo script).
- [ ] **1.3.3** Ícones: os 41 SVG de `assets/icons/` (Lucide) entram no `bi-data.js` como texto e viram HTML. Escapar quebraria os ícones; a defesa é conferir cada SVG contra o vocabulário do Lucide na construção, e a construção para com qualquer outra coisa. Teste primeiro (`pipelines/tests/test_icons.py`):

```python
"""Every icon that build-standalone-data.py puts in bi-data.js is a plain Lucide drawing (spec seguranca-doacoes, section 8):
the icons become HTML on the page, so an icon with a handler, a link or a script would run."""
import importlib.util
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "docs" / "superpowers" / "tools"
spec = importlib.util.spec_from_file_location("icon_check", TOOLS / "icon_check.py")
icon_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(icon_check)


class IconTest(unittest.TestCase):
    def test_every_committed_icon_is_clean(self):
        for f in sorted((TOOLS.parent / "previews" / "assets" / "icons").glob("*.svg")):
            with self.subTest(icon=f.name):
                self.assertEqual(icon_check.problems(f.read_text(encoding="utf-8")), [])

    def test_planted_icons_are_refused(self):
        good = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 3h18"/></svg>'
        self.assertEqual(icon_check.problems(good), [])   # the control: a clean icon passes
        for bad in ('<svg onload="x()"><path d="M0 0"/></svg>', '<svg><script>x()</script></svg>', '<svg><a href="javascript:x()"><path d="M0 0"/></a></svg>',
                    '<svg><foreignObject><img src="x"></foreignObject></svg>', '<svg><path d="M0 0" style="x"/></svg>', '<svg></svg><img src="x">'):
            with self.subTest(bad=bad):
                self.assertNotEqual(icon_check.problems(bad), [])
```

`docs/superpowers/tools/icon_check.py` (com `html.parser`, nunca regex de tag, que o CodeQL marca como alto):

```python
"""The Lucide vocabulary: the only elements and attributes an icon may have (spec seguranca-doacoes, section 8)."""
from html.parser import HTMLParser

ELEMENTS = {"svg", "path", "circle", "rect", "line", "polyline", "polygon", "ellipse", "g"}
ATTRIBUTES = {"xmlns", "width", "height", "viewbox", "fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin", "class",
              "d", "cx", "cy", "r", "rx", "ry", "x", "y", "x1", "y1", "x2", "y2", "points"}


class _Walk(HTMLParser):
    def __init__(self):
        super().__init__()
        self.problems, self.depth, self.roots = [], 0, 0

    def handle_starttag(self, tag, attrs):
        if self.depth == 0:
            self.roots += 1
        if tag not in ELEMENTS:
            self.problems.append(f"element {tag}")
        self.problems += [f"attribute {k}" for k, _ in attrs if k not in ATTRIBUTES]
        self.depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.depth -= 1

    def handle_endtag(self, tag):
        self.depth -= 1

    def handle_data(self, data):
        if data.strip():
            self.problems.append("text")


def problems(svg):
    w = _Walk()
    w.feed(svg.split("-->", 1)[-1] if svg.lstrip().startswith("<!--") else svg)
    if w.roots != 1:
        w.problems.append(f"{w.roots} root elements")
    return w.problems
```

`build-standalone-data.py`, na linha que monta `icons`: para com `SystemExit(f"build-standalone-data: icon {stem}: {problems}")` se `icon_check.problems()` não for vazio. Rodar o teste antes do módulo existir (vermelho por importação), depois verde.

- [ ] **1.3.4** Rodar a sonda P1 de novo: `exit: 0`, `0 of 8 pages injected`, e os textos envenenados aparecendo como texto nas telas de `MUST_SHOW`. Controle (`--control`): `control caught`, exit 0. Se aparecer um ponto novo, voltar ao 1.3.1 com ele.

### Tarefa 1.4: a regra do Firefox no `ci`

**Arquivos:** `docs/superpowers/tools/package.json`, `package-lock.json` (`git add -f`: o `.gitignore_global` desta máquina ignora o lock), `eslint.config.mjs`, `eslint-suppressions.json`.

- [ ] **1.4.1** Ler na fonte, antes de instalar: a página "Bulk Suppressions" da documentação do ESLint (o arquivo, `--suppress-all`, o que acontece quando um item da lista some) e o README do `eslint-plugin-no-unsanitized` (a opção `escape`). Conferir com `npm view eslint version deprecated license`, `npm view eslint-plugin-no-unsanitized version deprecated license`; versões exatas no `package.json`.
- [ ] **1.4.2** A configuração. Os arquivos do site são scripts clássicos, menos `home-map.js` (módulo); os de fora (`assets/vendor/`) ficam de fora.

```js
// The Firefox rule against unescaped HTML (spec seguranca-doacoes, section 8): no-unsanitized/method and /property as errors,
// with esc() as the escape. What existed on 2026-11-03 sits in eslint-suppressions.json, a list that only shrinks.
import nounsanitized from 'eslint-plugin-no-unsanitized';

const rules = {
  'no-unsanitized/method': ['error', { escape: { methods: ['esc'] } }],
  'no-unsanitized/property': ['error', { escape: { methods: ['esc'] } }],
};
export default [
  { ignores: ['docs/superpowers/previews/assets/vendor/**'] },
  { files: ['docs/superpowers/previews/assets/*.js'], plugins: { 'no-unsanitized': nounsanitized }, rules,
    languageOptions: { ecmaVersion: 'latest', sourceType: 'script' } },
  { files: ['docs/superpowers/previews/assets/home-map.js'], languageOptions: { sourceType: 'module' } },
];
```

Rodar da raiz do repositório: `docs/superpowers/tools/node_modules/.bin/eslint --config docs/superpowers/tools/eslint.config.mjs --suppressions-location docs/superpowers/tools/eslint-suppressions.json 'docs/superpowers/previews/assets/*.js'`. Se a versão do ESLint resolver os caminhos pelo diretório da configuração, ajustar `files` ao que a documentação lida mandar.

- [ ] **1.4.3** Vermelho primeiro: sem a lista, a regra acusa o que existe (contar e guardar o número). Gerar a lista com `--suppress-all`. Controle: acrescentar num arquivo `el.innerHTML = \`<b>${x}</b>\`` e ver o ESLint falhar; tirar.
- [ ] **1.4.4** Rodar depois da tarefa 1.5 de novo, porque os scripts que saem do HTML passam a ser vistos; a lista é refeita uma vez só, no fim da fase, e a contagem vai no pull request.

### Tarefa 1.5: todo script sai para arquivo, nenhum `onerror` no HTML

**Arquivos:** `pipelines/tests/test_csp.py` (novo, só a parte "sem código inline" agora), os construtores e os arquivos novos de `assets/` listados acima.

- [ ] **1.5.1** Teste primeiro. Lê as quatro páginas publicadas e as páginas de reencaminhamento do `build-site.py`:

```python
"""No page carries code the CSP would have to allow inline (spec seguranca-doacoes, section 8; D219, Uniswap's form)."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREVIEWS = ROOT / "docs" / "superpowers" / "previews"
PAGES = ("BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html", "como-ler-o-mapa.html", "como-o-dinheiro-anda.html", "os-3-poderes.html")
DATA_TYPES = {"application/json"}


class _Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inline, self.handlers, self.js_urls, self.srcs, self._cur = [], [], [], [], None

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.handlers += [f"{tag} {k}" for k, _ in attrs if k.startswith("on")]
        self.js_urls += [v for k, v in attrs if k in ("href", "src", "action") and v and v.strip().lower().startswith("javascript:")]
        if tag == "script":
            if d.get("src") or d.get("data-src"):
                self.srcs.append(d.get("src") or d.get("data-src"))
            self._cur = (d.get("type") or "text/javascript", [])

    def handle_data(self, data):
        if self._cur:
            self._cur[1].append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._cur:
            kind, body = self._cur
            if "".join(body).strip() and kind not in DATA_TYPES:
                self.inline.append(kind)
            self._cur = None


def scan(html):
    s = _Scripts()
    s.feed(html)
    return s


class NoInlineCodeTest(unittest.TestCase):
    def test_pages_have_no_inline_code(self):
        for name in PAGES:
            with self.subTest(page=name):
                s = scan((PREVIEWS / name).read_text(encoding="utf-8"))
                self.assertEqual(s.inline, [], "inline scripts (importmap included)")
                self.assertEqual(s.handlers, [], "on* attributes")
                self.assertEqual(s.js_urls, [], "javascript: links")

    def test_our_scripts_write_no_handler_attributes(self):
        handler = re.compile(r"\son[a-z]+\s*=\s*[\"']")
        for f in sorted((PREVIEWS / "assets").glob("*.js")):
            with self.subTest(file=f.name):
                self.assertIsNone(handler.search(f.read_text(encoding="utf-8")))

    def test_the_scan_sees_inline_code(self):   # the control: the same scan on a page with each planted defect
        s = scan('<script>x()</script><script type="importmap">{}</script><img src="a" onerror="x()"><a href="javascript:x()">a</a>'
                 '<script type="application/json">{}</script>')
        self.assertEqual((s.inline, s.handlers, len(s.js_urls)), (["text/javascript", "importmap"], ["img onerror"], 1))
```

Rodar: falha com a lista do que existe hoje (importmap, `bi-loader-js`, o módulo da Início, `bi-chrome-js`, os scripts de Como ler o mapa, Como o dinheiro anda e Os 3 Poderes; `onerror` em `modals.js:168`, na página da Início e em `ph()` de Os 3 Poderes).

- [ ] **1.5.2** Cada script vai para o seu arquivo, escrito pelo mesmo construtor que hoje o põe inline, e a página ganha `<script src="assets/<nome>.js"></script>` no mesmo lugar (a ordem de execução não muda):

| Hoje inline | Arquivo | Quem escreve |
|---|---|---|
| `bi-chrome-js` (menu, rodapé), em todas | `assets/bi-chrome.js` | `site_chrome.py` (`SCRIPT`) |
| `bi-loader-js` (Início) | `assets/bi-loader.js` | `map_loader.py` (`SCRIPT`) |
| o módulo da Início (`data-module`, 46.777 caracteres) | `assets/home-map.js` (módulo) | `build-simulation.py` |
| as notas de Como ler o mapa | `assets/map-notes-page.js` | `build-notes-page.py` |
| o script grande de Como o dinheiro anda e o de 173 caracteres | `assets/dinheiro-page.js`, `assets/federal-cards.js` | o construtor da página (achar com `grep -rln "window.BIM, U = D.union"`) |
| o script de Os 3 Poderes | `assets/tres-poderes-page.js` | o construtor da página |
| o reencaminhamento (`FORWARD` em `build-site.py`) | `assets/forward.js` | `build-site.py` |
| o que `docs/superpowers/previews/src/platform-script.html` tiver de inline (só o staging, chave `rede`) | um arquivo em `assets/` por bloco | `build-site.py` |

O teste do `ci` "as páginas versionadas são o que os construtores fazem" passa a cobrir os arquivos novos: o passo do `ci.yml` termina em `git diff --exit-code -- docs/superpowers/previews/`, que já inclui `assets/`.

- [ ] **1.5.3** `map_loader.hold()`: um `<script type="module" src="...">` vira `<script type="text/x-bi-deferred" data-src="..." data-module>`; o carregador já cria `type = 'module'` com `src`. Um script inline mandado para `hold()` passa a parar a construção (`SystemExit`), para que ninguém volte a pôr código inline.
- [ ] **1.5.4** `onerror` sai do HTML. Um ouvinte só, em fase de captura, em `bi-chrome.js` (que roda em todas as páginas):

```js
// Images that fail to load (spec seguranca-doacoes, section 8: no handler attributes, the CSP blocks them). data-fallback="hide"
// hides the image, data-fallback="remove" removes it; the error event does not bubble, so the listener captures it.
document.addEventListener('error', (e) => {
  const img = e.target;
  if (!(img instanceof HTMLImageElement) || !img.dataset.fallback) return;
  if (img.dataset.fallback === 'remove') img.remove(); else img.style.display = 'none';
}, true);
```

`modals.js:168` e a Início: `onerror="this.style.display='none'"` vira `data-fallback="hide"`; `ph()` de Os 3 Poderes: `onerror="this.remove()"` vira `data-fallback="remove"`.

- [ ] **1.5.5** Rodar `test_csp.py`: a parte "sem código inline" verde, menos o mapa de importação (tarefa 1.6). Rodar a suíte inteira e as sondas da linha de base: iguais.

### Tarefa 1.6: three.js no próprio site, o mapa de importação sai

**Arquivos:** `docs/superpowers/tools/vendor-three.py`, `pipelines/tests/test_vendor_three.py`, `docs/superpowers/previews/assets/vendor/three/`, a fonte do módulo da Início (`BRASIL-IMPOSTO_DESIGN_hero-mapa-3d-round-2_2026-09-29.html`, onde nasce o mapa de importação) e `build-platform-preview.py` (`THREE_INTEGRITY` sai).

- [ ] **1.6.1** Teste primeiro: cada um dos 7 arquivos guardados, com a única troca desfeita, tem o sha384 de hoje (os valores do mapa de importação em `build-platform-preview.py`, copiados para o teste):

```python
"""three.js 0.170.0 served by the site itself (spec seguranca-doacoes, section 8): each file is the npm file byte for byte except
its import of 'three', which points to the copy beside it. Undoing that one change gives the hash the import map pinned."""
import base64
import hashlib
import unittest
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[2] / "docs" / "superpowers" / "previews" / "assets" / "vendor" / "three"
CORE = "../../../build/three.module.js"
PINNED = {   # sha384 from the import map of 2026-11-03 (build-platform-preview.py, THREE_INTEGRITY)
    "build/three.module.js": "GY5FqjttLCFRt/McQbyaVdCk2O1IQtOeX8Py6NfD89BIAsIyJFRl4UgSXrk2vXAk",
    "examples/jsm/lines/Line2.js": "svIqR2W/RlXb3d4T+bDn3JO+LXLbacA7GpMAUDJxTOFyZmVogvDRaOS7KZBRxcxc",
    "examples/jsm/lines/LineGeometry.js": "nfFqbe33KO97I7jZXjW73quBqqskqqj64WZycLNDzn0GGGI3aoWLZzuy8i0jeYmU",
    "examples/jsm/lines/LineMaterial.js": "bLpiIpNrFJ+EMb4Upzkap/Bc9Ul2wLoUMEfFm0PmZfyywMUYUsc5X98AuAYwwjq1",
    "examples/jsm/lines/LineSegments2.js": "nm+9Od/cYIb15jGaA1U2Geoo18K/i9fF2fZ4KbI2rZydtfYxqwtWRlbvdVfiECU5",
    "examples/jsm/lines/LineSegmentsGeometry.js": "2bbjHgEUXo9c3VW3OaZV638VYLXKhlNhNStU2D1Jm77zamWSQVYZak2p/Z0bZrmh",
    "examples/jsm/renderers/CSS2DRenderer.js": "9CXQqRjuKfYvfHem9p/LPU6b7PaeeiDuC/gp1qRz3bEV9txWG5wi9XhrkE/0/Dn9",
}


def upstream_hash(text):
    return base64.b64encode(hashlib.sha384(text.replace(f"from '{CORE}'", "from 'three'").encode("utf-8")).digest()).decode()


class VendorThreeTest(unittest.TestCase):
    def test_each_file_is_the_pinned_upstream_file(self):
        for rel, want in PINNED.items():
            with self.subTest(file=rel):
                self.assertEqual(upstream_hash((VENDOR / rel).read_text(encoding="utf-8")), want)

    def test_nothing_imports_a_bare_three(self):
        for f in VENDOR.rglob("*.js"):
            self.assertNotIn("from 'three'", f.read_text(encoding="utf-8"), f.name)

    def test_a_changed_byte_is_seen(self):   # the control
        t = (VENDOR / "examples/jsm/lines/Line2.js").read_text(encoding="utf-8")
        self.assertNotEqual(upstream_hash(t.replace("Line2", "Line3", 1)), PINNED["examples/jsm/lines/Line2.js"])
```

Vermelho: a pasta não existe.

- [ ] **1.6.2** `vendor-three.py`: baixa `https://registry.npmjs.org/three/-/three-0.170.0.tgz`, confere o `dist.integrity` (sha512) do pacote lido em `https://registry.npmjs.org/three/0.170.0`, extrai os 7 arquivos, confere cada sha384 contra `PINNED` **antes** de trocar `from 'three'` por `from '../../../build/three.module.js'` (os 6 complementos; o núcleo não importa `three`), grava em `assets/vendor/three/` com o `LICENSE` do pacote (MIT). Para se qualquer hash diferir.
- [ ] **1.6.3** O módulo da Início importa pelo caminho relativo ao próprio arquivo (`assets/home-map.js`): `'./vendor/three/build/three.module.js'` e `'./vendor/three/examples/jsm/lines/Line2.js'` e os outros; o mapa de importação sai da fonte (página `hero-mapa-3d-round-2`) e de `build-platform-preview.py`. Reconstruir com `build-simulation.py` e `build-platform-preview.py`.
- [ ] **1.6.4** `test_vendor_three.py` verde; `test_csp.py` inteiro verde; `test_published_file_size.py` verde (o núcleo tem perto de 1,3 MB). A Início desenha o mapa (foto a 1440 e 420 contra a linha de base).

### Tarefa 1.7: o `bi-data.js` sem `blob:`

O carregador baixa `bi-data.js` com a porcentagem real e roda o texto por um endereço `blob:`; a CSP só de origens recusa `blob:` em `script-src`.

- [ ] **1.7.1** Medir antes de mudar: com a CSP sem `blob:`, a Início trava no carregador (`.bi-loader[data-state="error"]`), e esse é o teste vermelho (vem de graça do `csp-check.cjs` da tarefa 1.8, que conta violações e espera o mapa).
- [ ] **1.7.2** Trocar o `blob:` por um `<script src="assets/bi-data.js">` depois do download, que o navegador serve do cache (o Pages manda `max-age=600`). Medir com o Playwright, pelo CDP (`Network.responseReceived`, `fromDiskCache` ou `fromMemoryCache`), no servidor local com o mesmo `cache-control` e no staging no ar: o arquivo desce uma vez só. **Se descer duas vezes**, parar: `blob:` em `script-src` ou o download em dobro vai ao autor como pergunta, com o tamanho medido e dizendo que não há precedente lido para `blob:` em `script-src`.

### Tarefa 1.8: a CSP da Uniswap (P2)

**Arquivos:** `docs/superpowers/tools/csp.py`, `site_chrome.py` (a meta logo depois de `<meta charset>`), `build-site.py` (`FORWARD`), `pipelines/tests/test_csp.py` (a parte da política), `docs/superpowers/tools/csp-check.cjs`.

- [ ] **1.8.1** Teste primeiro, em `test_csp.py`:

```python
import importlib.util
spec = importlib.util.spec_from_file_location("csp", ROOT / "docs" / "superpowers" / "tools" / "csp.py")
csp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(csp)


class PolicyTest(unittest.TestCase):
    def test_script_src_is_origins_only(self):
        script = dict(csp.DIRECTIVES)["script-src"]
        for banned in ("'unsafe-inline'", "'unsafe-eval'", "'strict-dynamic'", "data:", "blob:", "*", "https:"):
            self.assertNotIn(banned, script)
        self.assertEqual(dict(csp.DIRECTIVES)["object-src"], ("'none'",))
        self.assertEqual(dict(csp.DIRECTIVES)["base-uri"], ("'none'",))

    def test_every_page_has_the_meta_first(self):
        for name in PAGES:
            with self.subTest(page=name):
                html = (PREVIEWS / name).read_text(encoding="utf-8")
                self.assertEqual(html.count('http-equiv="Content-Security-Policy"'), 1)
                at = html.index(csp.META)
                self.assertLess(at, html.index("<script"))
                self.assertLess(at, html.index("<link"))

    def test_every_script_is_allowed(self):
        allowed = set(dict(csp.DIRECTIVES)["script-src"])
        for name in PAGES:
            for src in scan((PREVIEWS / name).read_text(encoding="utf-8")).srcs:
                with self.subTest(page=name, src=src):
                    self.assertTrue(src.startswith("assets/") or src in allowed, src)
```

A mesma conferência roda na montagem de staging (as páginas com a chave `rede` e as de reencaminhamento): `test_build_site.py` já monta as duas; acrescentar lá a chamada a `scan` e à meta.

- [ ] **1.8.2** A política:

```python
"""The site's Content Security Policy, one meta for every page (spec seguranca-doacoes, section 8). D219: Uniswap's form, a list
of origins in a page tag and no inline code; style-src, img-src and form-action as Uniswap's apps/web/public/csp.json has them
(read 2026-11-03). Each CDN script is listed by its exact file, the way Uniswap scopes fonts.gstatic.com to one path."""
SCRIPT_FILES = (
    "https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js",                         # Como o dinheiro anda
    "https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js",               # Como o dinheiro anda
    "https://cdn.jsdelivr.net/npm/3d-force-graph@1.80.0/dist/3d-force-graph.min.js",     # Início on staging (rede)
)
CONNECT = ("https://api.web3forms.com",)   # the contact form; phase 2 adds the public nodes of the donation check
DIRECTIVES = (
    ("default-src", ("'self'",)),
    ("script-src", ("'self'",) + SCRIPT_FILES),
    ("style-src", ("'self'", "'unsafe-inline'")),
    ("font-src", ("'self'",)),
    ("img-src", ("*", "blob:", "data:")),
    ("connect-src", ("'self'",) + CONNECT),
    ("object-src", ("'none'",)),
    ("base-uri", ("'none'",)),
    ("form-action", ("'none'",)),
)
POLICY = "; ".join(f"{name} {' '.join(values)}" for name, values in DIRECTIVES)
META = f'<meta http-equiv="Content-Security-Policy" content="{POLICY}">'
```

`site_chrome.inject()` põe `csp.META` logo depois de `<meta charset="utf-8">`, entre marcadores próprios (`<!-- site-chrome:csp -->`), como faz com o resto; `FORWARD` em `build-site.py` também.

- [ ] **1.8.3** A sonda P2 e zero violações:

```js
// P2 (spec seguranca-doacoes, section 14) and no CSP violation anywhere: each page loads, is clicked through and opens the crypto
// view with zero securitypolicyviolation events; then a handler injected into the page must not run. --control serves the same
// pages without the meta and the handler must run.
// Run: node docs/superpowers/tools/csp-check.cjs <built site> [--control]
const { chromium } = require('playwright-core');
const { spawn } = require('child_process'), path = require('path');
const [site, mode] = process.argv.slice(2), PORT = 8793, base = `http://127.0.0.1:${PORT}/`;
const PAGES = ['index.html', 'index.html?open=SC', 'como-ler-o-mapa.html', 'como-o-dinheiro-anda.html', 'os-3-poderes.html', 'index.html#apoie-cripto?moeda=USDT&rede=tron&valor=10'];
(async () => {
  const server = spawn(process.execPath, [path.join(__dirname, 'static-server.cjs'), site, String(PORT)].concat(mode === '--control' ? ['--no-csp'] : []), { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 400));
  let bad = 0, ran = 0;
  try {
    const b = await chromium.launch({ args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
    for (const u of PAGES) {
      const p = await (await b.newContext({ viewport: { width: 1280, height: 860 } })).newPage();
      await p.addInitScript(() => { window.__violations = []; document.addEventListener('securitypolicyviolation', (e) => window.__violations.push(`${e.violatedDirective} ${e.blockedURI}`)); });
      await p.goto(base + u, { waitUntil: 'load', timeout: 120000 });
      await p.waitForFunction(() => !document.querySelector('script[type="text/x-bi-deferred"]') || document.querySelector('.bi-loader[data-state]'), null, { timeout: 90000 }).catch(() => {});
      await p.waitForTimeout(2000);
      const before = await p.evaluate(() => ({ v: window.__violations.slice(), loader: document.querySelector('.bi-loader')?.dataset.state || 'none' }));
      await p.evaluate(() => { const d = document.createElement('div'); d.innerHTML = '<img src="x" onerror="window.__p2=1">'; document.body.append(d); });
      await p.waitForTimeout(800);
      const p2 = await p.evaluate(() => window.__p2 === 1);
      ran += p2 ? 1 : 0;
      const pageBad = mode !== '--control' && (before.v.length > 0 || before.loader === 'error');
      bad += pageBad ? 1 : 0;
      console.log(`${pageBad ? 'FAIL' : 'ok  '} ${u.padEnd(60)} violations ${before.v.length}${before.v.length ? ' (' + before.v[0] + ')' : ''}, loader ${before.loader}, injected handler ${p2 ? 'RAN' : 'blocked'}`);
      await p.context().close();
    }
    await b.close();
  } finally { server.kill(); }
  if (mode === '--control') { const ok = ran === PAGES.length; console.log(ok ? 'control: without the CSP the handler runs on every page' : `BROKEN CONTROL: the handler ran on ${ran} of ${PAGES.length}`); process.exit(ok ? 0 : 1); }
  process.exit(bad || ran ? 1 : 0);
})();
```

Vermelho primeiro: antes da meta, `injected handler RAN` em toda página e exit 1. Depois: zero violações, carregador em `done`, `blocked` em todas, exit 0; `--control`: o manipulador roda em todas.

- [ ] **1.8.4** Rodar as sondas de funcionamento contra a montagem com CSP: `apoie-check.cjs` (177 de 177 nas duas), `cripto-check.cjs` (30 de 30 com carteiras de mentira), `site-check.cjs`, `overlay-check.cjs`, `cargos-filters-check.cjs`, `ledger-graph-periods-check.cjs`. Qualquer queda é a CSP quebrando o site: achar a origem que falta e decidir pelo arquivo exato, nunca pelo domínio todo.

### Tarefa 1.9: fontes no próprio site (P9)

**Arquivos:** `docs/superpowers/tools/vendor-fonts.py`, `docs/superpowers/previews/assets/fonts/`, `docs/superpowers/tools/fonts-check.cjs`, os construtores que escrevem o `<link>` do Google Fonts (`apoie.py`, `build-notes-page.py` e as páginas-fonte; `render-doc.py` não é do site e fica), `bi-cripto.js` (a JetBrains Mono que vem quando a vista da cripto abre).

- [ ] **1.9.1** A sonda primeiro, vermelha hoje:

```js
// P9 (spec seguranca-doacoes, section 14): no page asks fonts.googleapis.com or fonts.gstatic.com, the crypto view included.
// --control plants the Google Fonts link in the served Início, and the probe must see it.
// Run: node docs/superpowers/tools/fonts-check.cjs <built site> [--control]
const { chromium } = require('playwright-core');
const { spawn } = require('child_process'), fs = require('fs'), os = require('os'), path = require('path');
let [site, mode] = process.argv.slice(2);
const PORT = 8794, base = `http://127.0.0.1:${PORT}/`, GOOGLE = /fonts\.(googleapis|gstatic)\.com/;
const PAGES = ['index.html', 'como-ler-o-mapa.html', 'como-o-dinheiro-anda.html', 'os-3-poderes.html', 'index.html#apoie-cripto?moeda=USDT&rede=tron&valor=10'];
if (mode === '--control') {
  const copy = fs.mkdtempSync(path.join(os.tmpdir(), 'fonts-control-'));
  fs.cpSync(site, copy, { recursive: true });
  const f = path.join(copy, 'index.html');
  fs.writeFileSync(f, fs.readFileSync(f, 'utf8').replace('</head>', '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope"></head>'));
  site = copy;
}
(async () => {
  const server = spawn(process.execPath, [path.join(__dirname, 'static-server.cjs'), site, String(PORT)], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 400));
  let asked = 0;
  try {
    const b = await chromium.launch({ args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
    for (const u of PAGES) {
      const c = await b.newContext({ viewport: { width: 1280, height: 860 } }), seen = [];
      c.on('request', (r) => { if (GOOGLE.test(r.url())) seen.push(r.url()); });
      await c.route(GOOGLE, (r) => r.abort());   // seen, never fetched
      const p = await c.newPage();
      await p.goto(base + u, { waitUntil: 'load', timeout: 120000 });
      await p.waitForTimeout(3000);
      asked += seen.length;
      console.log(`${seen.length ? 'ASKED' : 'ok   '} ${u.padEnd(60)} ${seen.length} Google Fonts requests`);
      await c.close();
    }
    await b.close();
  } finally { server.kill(); }
  if (mode === '--control') { console.log(asked ? 'control caught' : 'BROKEN CONTROL: the planted link was not seen'); process.exit(asked ? 0 : 1); }
  process.exit(asked ? 1 : 0);
})();
```

- [ ] **1.9.2** `vendor-fonts.py`: lê a URL `css2` que as páginas usam hoje, pede o CSS com o `User-Agent` de um Chrome atual (o Google entrega woff2 com `unicode-range` por subconjunto), baixa cada woff2 para `assets/fonts/`, escreve `assets/fonts/manrope.css` e `assets/fonts/jetbrains-mono.css` com os mesmos blocos `@font-face` apontando para os arquivos locais, e copia o texto da OFL 1.1 de cada família do repositório da própria fonte (Manrope e JetBrains Mono) para `assets/fonts/OFL-manrope.txt` e `OFL-jetbrains-mono.txt`. Os arquivos são os mesmos que o Google serve ao Chrome, então o desenho das letras não muda.
- [ ] **1.9.3** O `<link>` do Google Fonts (e o `preconnect`) vira `<link rel="stylesheet" href="assets/fonts/manrope.css">` em todo construtor; o modal carrega `assets/fonts/jetbrains-mono.css` quando a vista abre (ou a folha já vem na página, se o peso medido da JetBrains Mono for pequeno: decidir pela medida, sem mudar o que aparece).
- [ ] **1.9.4** `fonts-check.cjs`: zero pedidos, exit 0; `--control`: `control caught`. Comparação pixel a pixel contra as fotos da linha de base (quatro páginas e a vista da cripto, 1440 e 420): iguais, com controle (uma foto com 1 px trocado tem de dar diferença).

### Tarefa 1.10: o ícone da carteira só se for `data:image` (P7)

**Arquivos:** `docs/superpowers/previews/assets/bi-cripto.js:71`, `docs/superpowers/tools/cripto-check.cjs`.

- [ ] **1.10.1** Teste primeiro em `cripto-check.cjs`: três carteiras EIP-6963 de mentira anunciam `icon` = `javascript:window.__p7=1`, `https://example.invalid/track.png` e `<img src=x onerror=window.__p7=1>`; o botão de cada uma não pode ter `img`, e `window.__p7` fica indefinido. Controle: uma quarta anuncia `data:image/png;base64,` de um PNG de 1 px válido, e o botão dela tem o `img`. Rodar: vermelho (hoje o `img` entra com qualquer `src`).
- [ ] **1.10.2** A regra do RainbowKit, palavra por palavra:

```js
// MetaMask's EIP-6963 library and RainbowKit accept a wallet's icon only as a data:image URI (spec seguranca-doacoes, section 8)
const iconOk = (icon) => typeof icon === 'string' && icon.replace(/\n/g, '').startsWith('data:image');
// ...
if (iconOk(w.info.icon)) { const i = el('img'); i.src = w.info.icon; i.alt = ''; b.prepend(i); }
```

- [ ] **1.10.3** `cripto-check.cjs` inteiro verde (31 de 31 com o caso novo) na montagem de staging.

### Tarefa 1.11: o job `security` no `ci`

**Arquivo:** `.github/workflows/ci.yml`.

- [ ] **1.11.1** Um job novo, `security`, ao lado do `ci` (roda em paralelo), com ações fixadas por commit como as outras e `permissions: contents: read`:

```yaml
  security:
    name: security
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7.1.0
        with:
          python-version: "3.12"
      - uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0
        with:
          node-version-file: .nvmrc
          cache: npm
          cache-dependency-path: docs/superpowers/tools/package-lock.json
      - name: The pinned browser and the lint rule
        working-directory: docs/superpowers/tools
        run: |
          npm ci --no-audit --no-fund
          npx playwright-core install --only-shell chromium
      - name: "No unescaped HTML (the Firefox rule, spec seguranca-doacoes section 8)"
        run: docs/superpowers/tools/node_modules/.bin/eslint --config docs/superpowers/tools/eslint.config.mjs --suppressions-location docs/superpowers/tools/eslint-suppressions.json 'docs/superpowers/previews/assets/*.js'
      - name: "Attacks P1, P2 and P9 against the staging build, each with its control"
        run: |
          python docs/superpowers/tools/build-site.py --profile staging --out "$RUNNER_TEMP/site"
          python docs/superpowers/tools/poison-data.py "$RUNNER_TEMP/site" "$RUNNER_TEMP/poison"
          cd docs/superpowers/tools
          node poison-check.cjs "$RUNNER_TEMP/poison"
          node csp-check.cjs "$RUNNER_TEMP/site"
          node csp-check.cjs "$RUNNER_TEMP/site" --control
          node fonts-check.cjs "$RUNNER_TEMP/site"
          node fonts-check.cjs "$RUNNER_TEMP/site" --control
          python ../tools/poison-data.py "$RUNNER_TEMP/site" "$RUNNER_TEMP/poison-control"
          node poison-check.cjs "$RUNNER_TEMP/poison-control" --control
```

Cada linha roda com `set -e` (o padrão do `bash` do Actions), então um controle quebrado derruba o job. O `security` vira verificação obrigatória dos dois rulesets na fase 3.

- [ ] **1.11.2** `test_workflows.py` confere o job novo (ações fixadas por commit). O Dependabot não vê o `package-lock.json` das ferramentas: pergunta ao autor, mudança à parte.

### Tarefa 1.12: prova da fase, pull request, deploy e conferência no ar

- [ ] **1.12.1** Suíte inteira (`check-all.py`, código de saída guardado num arquivo, nunca por `| tail`), `tsc` do `site/` se tocado, todas as sondas e os controles. `visible-text-check.py` depois do commit: zero diferença de texto.
- [ ] **1.12.2** A spec e o plano em `docs/superpowers/`; o `CHANGELOG.md` e o que o projeto pedir para um pull request (ver `CONTRIBUTING.md`). Commit com `--signoff`, mensagem citando a spec (`fix(security): ... (spec seguranca-doacoes, phase 1)`), antes conferir `git log origin/fix/seguranca-fase-1..HEAD` e `gh pr list --head fix/seguranca-fase-1`.
- [ ] **1.12.3** Pull request para o `staging` com `gh pr create --body-file -` (heredoc entre aspas), corpo conferido depois de postado. Esperar todas as verificações; o script de merge recusa qualquer uma que não seja `success`. Squash; `gh pr view N --json state` diz `MERGED`.
- [ ] **1.12.4** Ligar o site de testes, rodar o deploy, conferir no ar: as quatro páginas com a meta da CSP (`curl` com `?n=<hora>`), `csp-check.cjs` e `fonts-check.cjs` apontados para a URL do staging (aceitam URL no lugar da pasta: acrescentar na 1.8.3 e 1.9.1 que um argumento começando por `https://` pula o servidor local), a Início desenhando o mapa. Desligar o site de testes. Remover a worktree.

---

## Fase 2: as telas de D220

Ramo `feat/seguranca-fase-2` saído do `staging` depois do merge da fase 1. Texto de tela muda (a verificação `visible-text` com a etiqueta de mudança pretendida). Cada tela é medida contra o desenho da rodada `seguranca-r1`, caixa por caixa, como `private/apoie/cripto-envio-design-check.cjs` mediu o envio: um medidor novo `private/security/seguranca-design-check.cjs` com controle plantado.

### Tarefa 2.1: os defeitos do envio, um teste cada

**Arquivos:** `docs/superpowers/previews/assets/bi-cripto.js`, `docs/superpowers/tools/cripto-check.cjs`.

Para cada linha, primeiro o caso na sonda com a carteira de mentira, visto falhando; depois a correção; depois o caso verde e o controle (a carteira se comportando bem passa).

- [ ] **2.1.1** XRP: a Crossmark de mentira devolve `meta.TransactionResult: "tecUNFUNDED_PAYMENT"`. Hoje: "Doação enviada". Correção: só `tesSUCCESS` é envio; qualquer outro resultado mostra a recusa da rede com o código. Controle: `tesSUCCESS` mostra o passo "Enviada pela sua carteira".
- [ ] **2.1.2** Trocar de rede com a conexão pendente: a MetaMask de mentira segura `eth_requestAccounts` por 2 s, a sonda toca em outra rede nesse tempo. Hoje: a carteira fica presa à rede nova. Correção: cada conexão guarda a rede em que começou (`const startedOn = root.dataset.net`) e, quando volta, só segue se `root.dataset.net === startedOn`; trocar de rede cancela. Controle: sem troca, a conexão segue.
- [ ] **2.1.3** `showConfirm` fora do `try` (linha 214): uma carteira que lança erro antes da confirmação trava o botão em "ocupado". Correção: `showConfirm` dentro do `try`, `state.busy = false` no `finally`. Controle: sem erro, a confirmação aparece.
- [ ] **2.1.4** Tron: a TronLink de mentira devolve `{ result: { result: false, message: <hex de "REVERT"> } }` em `triggerSmartContract`. Hoje: o erro diz "saldo insuficiente". Correção: conferir `result.result === true` antes de assinar; senão, a mensagem da rede decodificada. Controle: `result: true` segue para assinar.
- [ ] **2.1.5** UniSat e Crossmark na rede errada: a UniSat de mentira responde `getChain()` com `{ enum: 'BITCOIN_TESTNET4' }`, a Crossmark com a rede de testes. Hoje: segue. Correção: antes de enviar, a rede tem de ser a principal; senão, "A carteira está na rede de testes" e nada é pedido. Controle: rede principal segue.

### Tarefa 2.2: o endereço inteiro em grupos de 4 (seção 12, item 1)

**Arquivos:** `docs/superpowers/previews/assets/bi-cripto-core.js`, `pipelines/tests/cripto_core.test.cjs`, `bi-cripto.js`.

- [ ] **2.2.1** Teste no Node primeiro:

```js
test('groups of 4, the whole address, nothing dropped', () => {
  assert.deepEqual(C.groupsOf4('TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE'), ['TQn9', 'Y2kh', 'EsLJ', 'W1Ch', 'VWFM', 'SMeR', 'Dow5', 'KcbL', 'SE']);
  assert.equal(C.groupsOf4('0xAbC').join(''), '0xAbC');
  const a = 'bc1qevkvnl6rvpexample0000000000000000000';
  assert.equal(C.groupsOf4(a).join(''), a);   // the control: joining the groups gives the address back
});
```

- [ ] **2.2.2** `groupsOf4 = (a) => a.match(/.{1,4}/g) || []` no núcleo. Na confirmação e na espera da carteira, o endereço vira um bloco próprio, em letra maior, cada grupo um `span` (texto por `textContent`, nunca HTML), como no quadro 1b da rodada; a frase "Confira se o endereço termina em ..." vira "Compare o endereço inteiro com o da carteira, grupo por grupo. Se a carteira encurtar o endereço, abra o endereço inteiro nela.", também na nota do link do celular (linha 81 de hoje).
- [ ] **2.2.3** `cripto-check.cjs`: a sonda lê os grupos da tela, junta e compara com o endereço fixado em `test_support.py`, nas cinco redes; controle: um grupo plantado a menos tem de falhar. Medida contra o quadro 1b.

### Tarefa 2.3: S1, pausar uma moeda ou rede

**Arquivos:** `docs/superpowers/tools/support_data.py`, `apoie.py`, `bi-cripto.js`, `pipelines/tests/test_support.py`, `cripto-check.cjs`.

- [ ] **2.3.1** Teste primeiro (`test_support.py`): um `support.json` de teste com a rede Tron do USDT em `"paused"` monta o modal com o botão da Tron apagado, texto "Pausada", `disabled`, e nenhum endereço da Tron na página; todas as redes de uma moeda em `"paused"` apagam a moeda; todas as redes de todas as moedas apagam o cartão "Cripto" com "Pausada". Controle: `"live"` abre e mostra o endereço. Vermelho: `STATUSES` não aceita `"paused"`.
- [ ] **2.3.2** `STATUSES = ("soon", "live", "paused")`; `apoie.py` desenha como o quadro 2 da rodada; `send_data()` não leva endereço de rede pausada (a página nunca tem o endereço, nem escondido).
- [ ] **2.3.3** `cripto-check.cjs` com o caso pausado (o link de entrada para uma rede pausada não abre o envio) e medida contra o quadro 2.

### Tarefa 2.4: C6, a conferência de cada doação na rede

**Arquivos:** `bi-cripto-core.js` (as leituras das respostas, puras, testadas no Node com respostas gravadas), `bi-cripto.js` (a consulta e os dois passos), `csp.py` (os nós em `connect-src`), `pipelines/tests/cripto_core.test.cjs`.

- [ ] **2.4.1** Medir antes (spec, seção 17): cada nó grátis responde a um pedido do navegador de outra origem? Uma página local faz `fetch` a `ethereum-rpc.publicnode.com`, `bsc-rpc.publicnode.com`, `api.trongrid.io`, `mempool.space` e `xrplcluster.com` e lê `access-control-allow-origin`. O nó que recusar fica com "só o link" (spec, seção 8), e isso vai no pull request.
- [ ] **2.4.2** Testes primeiro, com respostas reais gravadas de transações públicas (uma por rede, guardadas em `pipelines/tests/fixtures/chain/`): `C.checkTransfer(family, response, expected)` devolve `confirmed` quando destino e valor batem, `wrong` com o destino de verdade quando o destino é outro (C6), `pending` quando a transação ainda não aparece, `unknown` quando a resposta não serve. EVM: o recibo (`eth_getTransactionReceipt`), `status` 1, e para token o log `Transfer` (tópico `0xddf252ad...`) do contrato certo com o `to` e o valor; nativo, `eth_getTransactionByHash` com `to` e `value`. Tron: `gettransactioninfobyid` e o log do contrato. Bitcoin: `mempool.space/api/tx/<id>`, a saída para o endereço com o valor. XRP: `tx` com `TransactionResult` `tesSUCCESS`, `Destination` e `delivered_amount`. Controle de cada rede: a mesma resposta com o destino trocado dá `wrong`.
- [ ] **2.4.3** `bi-cripto.js`: depois do envio, "Enviada pela sua carteira"; a página consulta o nó a cada 5 s por até 3 minutos, depois a cada 30 s por até 20 minutos; `confirmed` mostra "Confirmada na rede"; `wrong` mostra, em vermelho, "A transação não foi para o Brasil-Imposto" com o destino inteiro em grupos de 4 (seção 12, item 3); `unknown` ou sem resposta, "não deu para conferir" e o link. A Solana fica fora (D217). `csp.py`: os nós medidos em `connect-src`, cada um pela origem exata.
- [ ] **2.4.4** `cripto-check.cjs` com nós de mentira (rota do Playwright): os quatro estados, cada um medido contra os quadros da tela 3 da rodada.

### Tarefa 2.5: os cartões de "Como apoiar" (seção 12, item 4)

- [ ] **2.5.1** Teste primeiro em `test_support.py`: a ordem dos cartões é Cripto, Pix; nenhum cartão do GitHub Sponsors; duas colunas a partir da largura do desenho, uma no celular. Vermelho hoje. Controle: a ordem antiga falha.
- [ ] **2.5.2** `apoie.py` (e `data/support.json`, se a ordem vier de lá): o cartão do GitHub Sponsors sai do modal (os dados dele ficam no arquivo para quando Q38 se resolver), a Cripto vem antes do Pix. `apoie-check.cjs` segue a vista nova.

### Tarefa 2.6: prova, pull request, deploy

- [ ] **2.6.1** As mesmas provas da 1.12, mais o medidor contra a rodada (`seguranca-design-check.cjs`, todas as caixas dos quadros 1b, 2, 3c e 4 a até 1 px, com controle), `visible-text-check.py --label` com só as frases da seção 12 mudando.
- [ ] **2.6.2** Pull request, merge, site de testes ligado, deploy, conferência no ar (as telas a 1440 e 420, as sondas contra a URL), site de testes desligado.

---

## Fase 3: repositório e organização

Ramo `ci/seguranca-fase-3` para o que é arquivo; o que é configuração vai pela API, com a conferência antes e depois.

### Tarefa 3.1: a conferência da configuração (base de R2, na máquina)

**Arquivo:** `docs/superpowers/tools/settings-check.py` (lê pela API com o `gh` desta máquina; o monitor da fase 4 usa a mesma lista de conferências pelo GitHub App).

- [ ] **3.1.1** O esperado, escrito antes: os dois repositórios (`Brasil-Imposto/brasil-imposto.github.io` e `Brasil-Imposto/staging`) com ruleset ativo no ramo padrão (só por pull request, `dco` obrigatório, sem force push, sem apagar), política de ações `allowed_actions: selected` com `sha_pinning_required: true`, e as verificações obrigatórias `ci`, `security`, `dco`, `guard` no `staging` e na `main` do site. Rodar: vermelho (o `Brasil-Imposto/staging` tem 0 rulesets; a política de ações não exige SHA; `security` e `guard` ainda não existem). Controle: o esperado com uma regra plantada que nenhum repositório tem tem de falhar.

### Tarefa 3.2: rulesets do `Brasil-Imposto/staging` e política de ações

- [ ] **3.2.1** Ler o ruleset da `main` do site (`gh api repos/Brasil-Imposto/brasil-imposto.github.io/rulesets/<id>`) e criar o mesmo no `Brasil-Imposto/staging` (`gh api -X POST repos/Brasil-Imposto/staging/rulesets --input <arquivo>`), com o `dco` daquele repositório (conferir se ele tem o workflow; se não tiver, copiar o `dco.yml` por pull request lá antes do ruleset, que senão recusaria o próprio pull request).
- [ ] **3.2.2** Política de ações: `gh api -X PUT repos/<repo>/actions/permissions -F enabled=true -f allowed_actions=selected -F sha_pinning_required=true` e a lista `selected-actions` só com as ações que os workflows usam (lidas dos arquivos, `uses:`). Ler antes, na documentação da API do GitHub, o nome exato do campo de SHA obrigatório; conferir lendo de volta.
- [ ] **3.2.3** `settings-check.py`: verde nas partes feitas.

### Tarefa 3.3: CODEOWNERS e a lista dos caminhos sensíveis

- [ ] **3.3.1** `.github/guard-paths.txt`, uma fonte só, lida pelo `guard` e pelo teste do CODEOWNERS: `data/support.json`, `docs/superpowers/previews/assets/bi-cripto*.js`, `docs/superpowers/previews/assets/vendor/**`, `.github/**`, `deploy/**`, `docs/superpowers/tools/csp.py`, `docs/superpowers/tools/support_data.py`, `pipelines/tests/test_support.py`, `SECURITY.md`.
- [ ] **3.3.2** Teste primeiro (`test_workflows.py`): cada linha de `guard-paths.txt` tem dono em `.github/CODEOWNERS` (`@Brasil-Imposto/maintainers`). Vermelho; acrescentar; verde. A segunda pessoa no ambiente de produção, com "prevent self-review", fica para o lote (D214).

### Tarefa 3.4: R1 e R3, o `guard`

**Arquivos:** `.github/scripts/guard.py`, `pipelines/tests/test_guard.py`, `.github/workflows/guard.yml`.

- [ ] **3.4.1** Ler antes o `sensitive-paths.yml` do glsec (`gh api repos/glsec/glsec/contents/.github/workflows/sensitive-paths.yml`) e a página da GitHub Security Lab sobre `pull_request_target` ("Preventing pwn requests"): o `guard` roda pelo código da base e **nunca** faz checkout do código do pull request; só lê pela API a lista de arquivos e a linha do tempo. O `ci.yml` diz "never pull_request_target"; o `guard` é a exceção escrita, e `test_workflows.py` passa a aceitar `pull_request_target` só no `guard.yml`, sem nenhum `ref:` de cabeça do pull request no checkout.
- [ ] **3.4.2** A decisão, pura, testada primeiro:

```python
"""guard (spec seguranca-doacoes, section 5): a pull request that touches a sensitive path fails until the label
seguranca-revisada is put after its last push; a new push takes the label off (as glsec and Kubernetes Prow do)."""
import fnmatch

LABEL = "seguranca-revisada"


def sensitive(files, patterns):
    return sorted(f for f in files if any(fnmatch.fnmatch(f, p) for p in patterns))


def decide(files, patterns, label_events, last_push_at):
    """label_events: [(created_at, 'labeled' | 'unlabeled')] for LABEL, oldest first; ISO times compare as text."""
    hits = sensitive(files, patterns)
    if not hits:
        return True, "no sensitive path"
    state, at = None, None
    for when, kind in label_events:
        state, at = kind, when
    if state == "labeled" and at > last_push_at:
        return True, f"{len(hits)} sensitive paths, labeled after the last push"
    return False, f"{len(hits)} sensitive paths ({', '.join(hits[:5])}); needs the label {LABEL} after the last push"
```

`test_guard.py`: R1 (um pull request que muda `data/support.json` e `pipelines/tests/test_support.py` juntos, sem etiqueta: falha); R3 (etiqueta às 10:00, push às 10:05: falha); os controles (pull request só com `README.md`: passa; etiqueta às 10:06 depois do push das 10:05: passa); e `unlabeled` depois de `labeled`: falha.
- [ ] **3.4.3** `guard.yml`: `on: pull_request_target: types: [opened, synchronize, reopened, labeled, unlabeled]`; `permissions: pull-requests: write, contents: read`; checkout da base (o padrão do `pull_request_target`, sem `ref:`), `persist-credentials: false`; um passo lê `gh api repos/$REPO/pulls/$N/files --paginate`, a linha do tempo (`issues/$N/timeline`, eventos `labeled`/`unlabeled` dessa etiqueta) e a hora do último push (o `committed_at` do evento `committed` mais novo, ou `head_ref_force_pushed`), chama `decide()` e sai com 1 quando falha; em `synchronize`, antes, tira a etiqueta (`gh api -X DELETE repos/$REPO/issues/$N/labels/seguranca-revisada`, ignorando 404). Criar a etiqueta no repositório (`gh label create seguranca-revisada`).
- [ ] **3.4.4** Prova no ar, com pull requests de teste (fechados depois, com comentário dizendo que eram o teste R1 e R3 da spec): R1 vermelho, controle verde, R3 vermelho depois do push, verde com a etiqueta nova. Depois do merge do `guard`, acrescentar `guard` e `security` às verificações obrigatórias dos rulesets do `staging` e da `main` (`settings-check.py` verde inteiro).

### Tarefa 3.5: o manifesto de cada publicação (base de B1)

**Arquivos:** `docs/superpowers/tools/build-manifest.py`, `pipelines/tests/test_build_manifest.py`, `.github/workflows/pages.yml`, `deploy/staging/deploy.yml`.

- [ ] **3.5.1** Teste primeiro: `build-manifest.py write <site> <commit>` grava `<site>/build-manifest.json` com `commit`, `built_at` e `files` (`caminho: sha256` de todo arquivo, menos o próprio manifesto); `verify(site, manifest)` devolve a lista do que difere. Casos: o site recém-montado: lista vazia; um byte trocado num arquivo (B1): o arquivo na lista; um arquivo a mais e um a menos: os dois na lista. O hash do conjunto (`sha256` do manifesto ordenado) sai na última linha, para a nota da versão.
- [ ] **3.5.2** `pages.yml` e o `deploy.yml` do staging chamam `build-manifest.py write _site "$GITHUB_SHA"` depois da montagem e antes do upload; o hash do conjunto vai para o resumo do run (`$GITHUB_STEP_SUMMARY`) e, no dia de produção, para a nota da versão (`release-notes.py`).
- [ ] **3.5.3** Pull request (o `guard` acusa, porque toca `.github/`: etiqueta depois do último push), merge, deploy do staging com o site de testes ligado, `curl` do `build-manifest.json` no ar e `verify` contra o site baixado; desligar.

---

## Fase 4: o monitor

Repositório novo `Brasil-Imposto/monitor`, público (D217), criado pela conta do autor (o `gh` desta máquina é dela; o GitHub manda o e-mail de um agendamento para quem o criou). Logs só com tipos e hashes, nunca nomes, valores ou endereços de webhook.

### Tarefa 4.0: medir o peso da conferência de 5 minutos, antes de qualquer código

- [x] **4.0.1** Medido em 2026-11-03: uma passada inteira baixa 87 MB (6.112 arquivos, com gzip), cerca de 756 GB por mês a cada 5 minutos, contra o limite flexível de 100 GB do Pages. Decidido em D222: a cada 5 minutos, cada arquivo é pedido com a pergunta "mudou?" (`If-None-Match`) e só desce e é conferido quando mudou; as quatro páginas com os endereços descem inteiras; tudo desce e é conferido uma vez por dia. Nada disso custa dinheiro.

### Tarefa 4.1: o repositório, `pins.json` e a base

- [ ] **4.1.1** `gh api -X POST orgs/Brasil-Imposto/repos -f name=monitor -f visibility=public -f description=...`; ruleset na `main` (só por pull request, sem force push, sem apagar; o `dco`), política de ações com SHA obrigatório; `pins.json` com os cinco endereços e os sete contratos copiados de `data/support.json` (o teste do monitor confere que batem com o arquivo do site no `staging`, e um endereço plantado diferente tem de falhar). Pull request lá para cada arquivo.
- [ ] **4.1.2** Linha do monitor e do GitHub App no registro de serviços (`blaclab-docs/knowledge/operations/`, bloco do Brasil-Imposto) no mesmo turno em que forem criados.

### Tarefa 4.2: R2, a foto da configuração (a cada 15 minutos)

**Arquivos no monitor:** `checks/settings.py`, `checks/endpoints.py`, `tests/test_settings.py`, `.github/workflows/settings.yml`.

- [ ] **4.2.1** Testes primeiro, com respostas gravadas: a foto normalizada (rulesets, administradores, colaboradores, workflows, apps instalados e permissões, webhooks só pelo tipo e eventos, chaves de deploy pelo título e hash, ambientes e regras, Pages, política de ações, tokens finos com acesso à organização) comparada à base guardada em `state/settings.json`. Cada tipo de mudança da seção 14 (ruleset apagado, colaborador novo, app novo, chave de deploy, webhook, ambiente sem revisor, Pages) dá um alarme com o tipo e o hash, nunca o valor; respostas iguais dão zero alarmes (o controle). Uma mudança alarma uma vez e vira a base nova.
- [ ] **4.2.2** `settings.yml`: `schedule: cron: '7-59/15 * * * *'`, o token do GitHub App só leitura (`actions/create-github-app-token`, fixado por SHA conferido contra a tag; segredos `APP_ID` e `APP_PRIVATE_KEY` que o autor cola na tela do GitHub, passos na resposta final), a conferência; mudança: commit da base nova e `exit 1` (o e-mail de falha é o alarme). Os passos do autor para criar o App vêm na resposta final, na ordem da tela.

### Tarefa 4.3: B1 e L1, a conferência dos arquivos servidos (a cada 5 minutos, na forma de D222)

**Arquivos no monitor:** `checks/served.py`, `tests/test_served.py`, `.github/workflows/served.yml`.

- [x] **4.3.1** Testes primeiro, contra um site local montado com `build-manifest.json`: B1 (um byte trocado num arquivo servido: alarme com o caminho e os dois hashes); L1 (um endereço trocado no bloco `#bi-cripto-data` de uma página: alarme dizendo a rede, sem o endereço); a CSP ausente de uma página: alarme; os controles (o site certo: zero alarmes). O commit no ar vem da API de publicações do Pages, nunca só do manifesto (um manifesto trocado junto com o arquivo não engana).
- [x] **4.3.2** `served.yml`: `cron: '2-59/5 * * * *'`. Até o lote, a produção não tem cripto nem manifesto: o workflow roda contra a montagem local do `staging` (spec, seção 7) e passa a olhar a produção no dia do lote (uma linha de configuração, `TARGET`).
- **Feito em 2026-11-04 (`Brasil-Imposto/monitor#2`, `5952110`):** `checks/served.py` lê a publicação no registro do GitHub (a implantação do Pages mais nova com sucesso, a execução por trás dela, que tem de ser o workflow de publicação do site no seu ramo e para o commit da implantação, e a única linha do hash do conjunto no log da montagem) e confere o manifesto servido contra ela e cada arquivo contra o manifesto: um manifesto trocado junto com o arquivo não engana. A cada rodada, "mudou?" (`If-None-Match`) para cada arquivo; as quatro páginas com os endereços (listadas em `pins.json`) descem inteiras; tudo desce na primeira rodada de cada dia UTC e em toda publicação nova (a ETag do Pages é a hora da publicação e o tamanho, medido no ar). L1: endereços e contratos do bloco contra `pins.json`; rede pausada não alarma, rede desconhecida alarma. CSP em toda página, sem código inline. 27 testes (23 vermelhos num esboço sem conferência, antes dela); na montagem de verdade (6.152 arquivos, servidor local que responde 304 como o Pages): passada inteira sem alarme, a seguinte pediu os 6.152 e baixou 5; os controles `b1`, `manifest`, `l1` e `csp` pegos, e com a defesa desligada os de `b1` e `l1` falham. Um 304 do Pages tem cerca de 370 bytes de cabeçalho (medido no ar): a cada 5 minutos, a conferência gastaria cerca de 25 GB por mês do limite flexível de 100 GB (estimativa a partir do medido: 6.148 respostas 304 e 5 descidas por rodada, mais a passada diária de 87 MB). O `served.yml` roda só à mão até o lote (a rodada no `staging` provou a leitura do registro do GitHub com o token do próprio monitor); o agendamento entra no lote, na forma que o autor escolher para o agendador. Até lá, o job `security` do `ci` roda a mesma conferência, fixada no commit do monitor, na montagem do `staging`. O monitor ganhou `tests.yml` (não havia workflow que rodasse os testes dele).

### Tarefa 4.4: C1 e C5, os cinco endereços na blockchain (a cada 15 minutos)

**Arquivos no monitor:** `checks/chain.py`, `tests/test_chain.py`, `tests/fixtures/`, `.github/workflows/chain.yml`.

- [ ] **4.4.1** Testes primeiro, com respostas gravadas dos nós da seção 9 da spec: C1 (uma saída plantada em cada rede: gasto de BTC em `mempool.space`, nonce que sobe no ETH e na BSC, transação de saída na Tron, `Sequence` que sobe no XRP Ledger, assinatura da chave na Solana: alarme com a rede e o hash da transação); C5 (o nó fora do ar três rodadas seguidas: alarme "não deu para conferir", nunca verde; duas rodadas: ainda sem alarme); os controles (respostas sem saída: zero alarmes; nó respondendo: verde). O estado (contagem por endereço, falhas seguidas por nó) em `state/chain.json`.
- [ ] **4.4.2** `chain.yml`: `cron: '11-59/15 * * * *'`, sem chave nenhuma.

### Tarefa 4.5: sinal de vida, monitor vigiado e a base diária

- [ ] **4.5.1** `heartbeat.yml`: `cron: '0 12 * * *'` (9h em Brasília), um comentário na issue fixada "Sinal de vida" com as contagens do dia (rodadas, alarmes, por tipo), que chega por e-mail a quem acompanha o repositório. Teste do texto com as contagens gravadas.
- [ ] **4.5.2** O commit diário do estado (o GitHub desliga agendamentos de repositório público sem atividade em 60 dias), no mesmo `heartbeat.yml`.
- [x] **4.5.3** A1, no repositório principal, `.github/workflows/monitor-watch.yml`: `cron: '23 * * * *'`, lê pela API pública a última execução da conferência mais frequente do monitor e falha se ela tiver mais de três intervalos (hoje a `chain`, de 15 em 15 minutos: 45 minutos). Teste `pipelines/tests/test_monitor_watch.py`: 46 minutos falha, 4 passa (controle), nenhuma falha. No #179, à espera da etiqueta do autor.

### Tarefa 4.6: prova e os passos do autor

- [ ] **4.6.1** Cada workflow disparado à mão uma vez com um alarme plantado (uma base de teste diferente), visto falhando no GitHub, e uma vez limpo, visto passando; depois a base de verdade.
- [ ] **4.6.2** Resposta final ao autor, na ordem e nas palavras de cada tela: criar o GitHub App da organização só leitura e instalar; gerar a chave e colar nos segredos do monitor (a chave nunca passa por esta sessão); avisos do Actions por e-mail só para falhas; o endereço da caixa do formulário verificado e escolhido para os avisos da organização; acompanhar o repositório do monitor.

---

## Fase 5: folha de resposta, `security.txt`, registro de endereços

Ramo `docs/seguranca-fase-5`.

- [ ] **5.1** `docs/security/BRASIL-IMPOSTO_RUNBOOK_resposta-incidente_2026-11-03.md`, uma página, no modelo da Security Alliance (seção 10 da spec): tirar do ar ("Unpublish site"), avisar, apurar (o log de auditoria na tela), pausar a moeda ou rede (`"paused"` e um deploy), trocar os endereços (carteira nova, pull request com o `guard`, `pins.json` do monitor), e antes de voltar: causa achada, falha corrigida, publicação nova de fonte conferida, credenciais trocadas. Cada passo com o comando exato.
- [ ] **5.2** `security.txt` (RFC 9116), teste primeiro (`test_security_txt.py`): `Contact` é o link do relato privado de vulnerabilidade do repositório, `Expires` dentro de um ano e no futuro, `Canonical` igual ao endereço servido, nenhum endereço de e-mail (o teste procura `@`; controle: uma linha plantada com `@` falha). Servido em `/.well-known/security.txt`; se o Pages não servir `/.well-known/` (spec, seção 17, conferir com `curl` no staging ligado), na raiz.
- [ ] **5.3** Registro de endereços no `SECURITY.md`, teste primeiro (`test_security_register.py`): a tabela tem os cinco endereços iguais aos de `data/support.json`, cada um com a data e o commit em que entrou (lidos do `git log` de `data/support.json`); controle: um endereço plantado diferente falha.
- [ ] **5.4** Pull request (o `guard` acusa o `SECURITY.md`), merge, deploy do staging com o site ligado, `curl` do `security.txt`, desligar.

---

## Depois deste plano (fora do código das fases 1 a 5)

- **Fase 6:** carteiras de verdade em redes de teste contra uma montagem local (MetaMask em Sepolia e na BSC testnet, TronLink na Nile, UniSat em testnet4 ou signet, Crossmark na testnet do XRP Ledger), chaves geradas por script direto no Keychain e importadas sem aparecer (D217); a CSP provada com as carteiras de verdade; o captcha do faucet fica com o autor.
- **Fase 7:** o teste de verdade do autor com o site de testes ligado só para isso; o gasto de teste de cada endereço (dispara o alarme C1, como deve); depois o lote da produção, com o aviso de produção (D192), as regras novas do repositório e a aprovação do autor em cada publicação (D221, D222), e a segunda pessoa quando houver (D214).

## Conferência do plano contra a spec

| Spec | Onde |
|---|---|
| Seção 5 (repositório) | Tarefas 3.1 a 3.4 |
| Seção 6 (manifesto) | Tarefa 3.5 |
| Seção 7 (arquivos servidos) | Tarefas 4.0 e 4.3 |
| Seção 8 (navegador) | Tarefas 1.2 a 1.10; 2.2; 2.4 |
| Seção 9 (blockchain) | Tarefa 4.4 |
| Seção 3 (alarmes, sinal de vida, monitor vigiado) | Tarefas 4.2 a 4.5 |
| Seção 4 (pausar) | Tarefa 2.3 |
| Seção 10 (folha, `security.txt`, registro) | Fase 5 |
| Seção 11 (defeitos do envio) | Tarefa 2.1, 2.2 |
| Seção 12 (telas) | Tarefas 2.2 a 2.5 |
| Seção 14 (R1, R2, R3, B1, L1, P1, P2, P7, P9, C1, C5, C6, A1, S1) | R1 e R3: 3.4; R2: 4.2; B1 e L1: 3.5 e 4.3; P1: 1.2 e 1.3; P2: 1.8; P7: 1.10; P9: 1.9; C1 e C5: 4.4; C6: 2.4; A1: 4.5; S1: 2.3 |
| Seção 17 (não confirmado) | Confirmados: `/.well-known/` servido (5.2, no ar em 2026-11-04); os nós respondem a outra origem (2.4.1); o `style-src` da Uniswap (lido em 2026-11-03). Abertos: rulesets de organização no plano grátis; carteiras com a CSP (fase 6); atividade de agendamento (4.5.2) |
