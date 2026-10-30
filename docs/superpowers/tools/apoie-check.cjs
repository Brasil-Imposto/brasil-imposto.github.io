// The Apoie button and its modal (spec apoie), measured as a visitor meets them, on a build with data/support.json turned on.
// Web3Forms is intercepted: no message is ever sent for real. For each page and width:
//   header   the header fits the window: nothing in it passes the right edge, the button and Menu do not overlap
//   top      with the modal open, the close button's centre is inside the window and is the topmost element there
//   bottom   the same after the panel is scrolled to its end (the close button stays pinned)
//   hscroll  no horizontal scroll: on the page (measured before the modal opens, since it locks the page) and inside the panel,
//            in every view and with every coin
//   columns  the three cards of "Como apoiar" (Pix, GitHub Sponsors, Cripto) sit in three equal columns above 820 px and one under
//            the other at 820 px and below (the computed tracks and the cards' own positions)
//   soon     each card on "soon" shows "Em breve", holds no link, button or address, and a click on it opens nothing
//   pix      Pix on "soon": its card shows "Em breve" and holds no button, link or address (the soon check, for the Pix card
//            alone). Pix live (a test build, BI_SUPPORT_JSON pointing at a file outside the repository, read here for the
//            expected address): its card has the button "Apoiar com Pix", the view opens alone, the link to the campaign equals
//            pix.campaign_url, opens in a new tab with noopener, Escape closes from that view and the focus is back on Apoie
//   views    each button of the main view opens its focused view, the only view displayed (computed display), and Voltar
//            comes back
//   coins    (only when crypto is live) each coin shows only its own panel, with its networks on "live" in the data file (all
//            open: BTC 1, ETH 1, SOL 1, USDT 4, USDC 3, XRP 1, BNB 1); a coin with none (XRP until its account exists, spec
//            section 10) keeps its button in the row, disabled, with "Em breve", and has no panel
//   addresses (only when crypto is live; spec apoie, section 10.2, item 3) for every coin and network, in the order of the data
//            file: the network's name, the address shown, the address "Copiar" puts on the clipboard (read back from the real
//            clipboard after a real click) and the explorer link equal data/support.json (or BI_SUPPORT_JSON)
//   sri      (section 10.2, item 4; once per page, at the first width) every script the page asks of another site is served
//            changed, with a line that marks it as run; none may run, since each has its hash; a page that asks for none says so
//   empty    the contact form sent empty shows the three field messages and makes no request
//   fast     a send sooner than the minimum time after the view opens makes no request
//   honey    a send with the honeypot (botcheck) checked makes no request
//   send     a normal send reads "Enviando..." with the button disabled, makes one POST to the Web3Forms URL with the access key
//            and the fields, and shows the success line
//   error    a send that Web3Forms answers with an error shows the error line and keeps the fields
//   escape   Escape closes the modal
//   focus    after closing, the focus is back on the Apoie button
//   outside  a click outside the panel closes it
// Usage: node apoie-check.cjs <base url of a served test build> [--control] [--widths=1440,420,320]
// For a build with the Pix live, give the same data file that built it: BI_SUPPORT_JSON=/path/support.json
// --control plants a failure for every check (hidden parts displayed, the close button not pinned, the modal under the header, a
// header wider than the window, a button in each "soon" card, the field messages hidden, a clock that skips the minimum time,
// a honeypot the page cannot read, Web3Forms' answers swapped, Escape swallowed, focus() disabled, the backdrop not
// clickable, two columns of cards at every width, the Pix link sent to another address, the first ETH address and its explorer
// link changed on the page, the hashes taken out of the page so the changed outside scripts run); every check must then fail,
// or the probe is blind.
// Env: PW_CORE (path to playwright-core), CHROME_HEADLESS (chrome-headless-shell binary).
const fs = require('fs');
const path = require('path');
const SUPPORT = JSON.parse(fs.readFileSync(process.env.BI_SUPPORT_JSON || path.join(__dirname, '..', '..', '..', 'data', 'support.json'), 'utf8'));
// every row the crypto view must show for a coin, in the order of the data file (support_data.networks_of)
const expected = (coin) => SUPPORT.crypto.groups.flatMap((g) => g.networks.filter((n) => n.status === 'live').flatMap((n) => n.coins.filter((c) => c.coin === coin)
  .map((c) => ({ name: n.name + (c.standard ? ` (${c.standard})` : ''), address: g.address, href: n.explorer_url.replace('{address}', g.address), explorer: n.explorer }))));
const NETWORKS = Object.fromEntries(['BTC', 'ETH', 'SOL', 'USDT', 'USDC', 'XRP', 'BNB'].map((c) => [c, expected(c).length]));
// the line added to every outside script: plain script syntax, valid in a classic script and in a module alike
const mark = (u) => `\n;(window.__biTampered = window.__biTampered || []).push(${JSON.stringify(u)});\n`;
// the control's page: every hash taken out (integrity, data-integrity and the import map's list), plus one outside script with no
// hash, so the plant lands on a page that loads nothing from outside too
const unhash = (html) => html.replace(/ integrity="[^"]*"/g, '').replace(/ data-integrity="[^"]*"/g, '').replace(/"integrity": \{/g, '"integrity-off": {')
  .replace('</body>', '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script></body>');
// the control's other page: one character of every hash changed, so the real files no longer match
const rehash = (html) => html.replace(/(sha(?:256|384|512)-)(.)/g, (m, alg, c) => alg + (c === 'A' ? 'B' : 'A'));
const PAGES = ['BRASIL-IMPOSTO_DESIGN_platform-preview_2026-10-09.html', 'os-3-poderes.html',
  'como-o-dinheiro-anda.html'];
const AT = String.fromCharCode(64);
const PERSON = { name: 'Pessoa de Teste', email: 'teste' + AT + 'exemplo.org', message: 'Mensagem de teste da sonda.' };
const PLANT = `
  .bi-apoie .bi-ap-coin.bi-ap-coin, .bi-apoie .bi-ap-view.bi-ap-view { display: block !important; }
  .bi-ap-top { position: static !important; }
  .bi-apoie { z-index: 500 !important; }
  .bi-end { min-width: 150vw !important; }
  .bi-ap-coins, .bi-ap-cards { min-width: 150vw !important; }
  .bi-ap-cards.bi-ap-cards { grid-template-columns: 1fr 1fr !important; }
  .bi-ap-backdrop { pointer-events: none !important; }
  .bi-apoie .bi-ap-err.bi-ap-err { display: none !important; }`;

(async () => {
  const args = process.argv.slice(2), base = args.find((a) => !a.startsWith('--')).replace(/\/?$/, '/');
  const control = args.includes('--control');
  const widths = ((args.find((a) => a.startsWith('--widths=')) || '--widths=1440,420,320').split('=')[1]).split(',').map(Number);
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox'] });
  const rows = [];
  const report = (w, page, check, ok, detail) => rows.push({ w, page, check, ok, detail });
  const shown = (p, sel) => p.$$eval(sel, (es) => es.filter((e) => getComputedStyle(e).display !== 'none').map((e) => e.dataset.view || e.dataset.coin || e.className));
  const visible = (p, sel) => p.$$eval(sel, (es) => es.filter((e) => getComputedStyle(e).display !== 'none' && e.getClientRects().length).length);
  const hit = (p) => p.$eval('.bi-ap-x', (btn) => { const r = btn.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
    const inside = x >= 0 && y >= 0 && x <= innerWidth && y <= innerHeight, top = inside ? document.elementFromPoint(x, y) : null;
    return { ok: inside && !!top && (top === btn || btn.contains(top)), at: `${x.toFixed(0)},${y.toFixed(0)}`, on: top ? String(top.className || top.tagName).slice(0, 30) : 'off screen' }; });
  // clicks inside the page go through the DOM: whether a real click would reach a control is what `top` and `bottom` measure
  const tap = (p, sel) => p.$eval(sel, (e) => e.click());
  const isOpen = (p) => p.$eval('#bi-apoie', (e) => getComputedStyle(e).display !== 'none');
  for (const w of widths) {
    for (const page of PAGES) {
      const key = page.split('_')[2];
      if (w === widths[0]) {
        // sri, two passes: every outside script served as published must be accepted (a wrong hash would break the page), and
        // served changed must be refused (none of the changed scripts runs). The control serves the page with every hash taken
        // out (the changed scripts run) and, in the first pass, with one character of each hash changed (the real files are refused).
        const pass = async (changed) => {
          const sctx = await browser.newContext({ viewport: { width: w, height: 900 } });
          const asked = [], refused = [];
          await sctx.route('**/*', async (r) => {
            const u = r.request().url();
            if (u.startsWith(base)) {
              if (control && r.request().resourceType() === 'document') { const res = await r.fetch(); return r.fulfill({ response: res, body: (changed ? unhash : rehash)(await res.text()) }); }
              return r.continue();
            }
            if (r.request().resourceType() === 'script' && /^https:\/\//.test(u)) {
              asked.push(u);
              if (!changed) return r.continue();
              const res = await r.fetch();
              return r.fulfill({ response: res, body: (await res.text()) + mark(u) });
            }
            return r.abort();
          });
          const sp = await sctx.newPage();
          sp.on('console', (m) => { if (/integrity|digest/i.test(m.text())) refused.push(m.text().slice(0, 120)); });
          await sp.goto(base + page);
          await sp.waitForSelector('.bi-apoie-btn', { timeout: 120000 });
          // Início holds its scripts back until the map's data has run (map_loader): wait until it has run every one or stopped
          // on a refused file, then until no new outside script is asked for in 3 s
          await sp.waitForFunction(() => !document.querySelector('script[type="text/x-bi-deferred"]') || document.querySelector('.bi-loader[data-state="error"]'), null, { timeout: 120000 });
          let before = -1;
          for (let i = 0; i < 40 && before !== asked.length; i++) { before = asked.length; await sp.waitForTimeout(3000); }
          const ran = await sp.evaluate(() => window.__biTampered || []);
          await sctx.close();
          return { asked: [...new Set(asked)], refused, ran };
        };
        const real = await pass(false), bad = await pass(true);
        const ok = real.refused.length === 0 && bad.ran.length === 0 && (real.asked.length > 0) === (bad.asked.length > 0);
        report(w, key, 'sri', ok, bad.asked.length || real.asked.length
          ? `as published: ${real.asked.length} outside scripts, ${real.refused.length} refused${real.refused.length ? ' (' + real.refused[0] + ')' : ''}; `
            + `changed: ${bad.asked.length} asked for, ${bad.ran.length} ran${bad.ran.length ? ': ' + bad.ran.join(', ') : ''}`
          : 'no outside script on this page');
      }
      const ctx = await browser.newContext({ viewport: { width: w, height: w <= 420 ? 800 : 900 }, permissions: ['clipboard-read', 'clipboard-write'] });
      const posts = [];
      let answer = 'ok';
      await ctx.route('**/*', async (r) => {
        const u = r.request().url();
        if (u.startsWith('https://api.web3forms.com/')) {
          posts.push({ url: u, method: r.request().method(), body: r.request().postData() });
          const good = (answer === 'ok') !== control;  // the control swaps Web3Forms' answers
          await new Promise((res) => setTimeout(res, 400));
          return r.fulfill(good ? { status: 200, contentType: 'application/json', body: '{"success":true,"message":"Email sent successfully!"}' }
            : { status: 500, contentType: 'application/json', body: '{"success":false,"message":"Something went wrong"}' });
        }
        return u.startsWith(base) ? r.continue() : r.abort();
      });
      if (control) {
        await ctx.addInitScript((css) => {
          HTMLElement.prototype.focus = function () {};
          addEventListener('keydown', (e) => { if (e.key === 'Escape') e.stopImmediatePropagation(); }, true);
          const real = Date.now.bind(Date); let n = 0; Date.now = () => real() + 10000 * (n++);  // every reading 10 s later
          const desc = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'checked');  // a honeypot the page cannot read
          Object.defineProperty(HTMLInputElement.prototype, 'checked', { get() { return this.name === 'botcheck' ? false : desc.get.call(this); },
            set(v) { desc.set.call(this, v); }, configurable: true });
          document.addEventListener('DOMContentLoaded', () => {
            const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);
            document.querySelectorAll('.bi-ap-soon').forEach((c) => c.insertAdjacentHTML('beforeend', '<button type="button" data-go="main">x</button>'));
            document.querySelectorAll('[data-view="pix"] a').forEach((a) => { a.href = 'https://exemplo.org/'; });   // the Pix link goes elsewhere
            const net = document.querySelector('.bi-ap-coin[data-coin="ETH"] .bi-ap-net');   // the first ETH address, swapped
            if (net) { const c = net.querySelector('code'); c.textContent = c.textContent.slice(0, -1) + 'x';
              net.querySelector('[data-copy]').dataset.copy = c.textContent; net.querySelector('a').href = 'https://exemplo.org/'; }
          });
        }, PLANT);
      }
      const p = await ctx.newPage();
      await p.goto(base + page);
      await p.waitForSelector('.bi-apoie-btn', { timeout: 120000 });
      await p.waitForTimeout(300);
      const h = await p.evaluate(() => {
        const hd = document.querySelector('.bi-header'), btn = document.querySelector('.bi-apoie-btn').getBoundingClientRect();
        const menu = document.querySelector('.bi-menu-btn').getBoundingClientRect(), menuShown = menu.width > 0;
        const past = [...hd.querySelectorAll('*')].filter((e) => e.getClientRects().length && e.getBoundingClientRect().right > innerWidth + 0.5).length;
        const overlap = menuShown && btn.right > menu.left + 0.5;
        return { ok: past === 0 && !overlap && btn.width > 0, detail: `${past} parts past the right edge, button and Menu ${overlap ? 'overlap' : 'apart'}` };
      });
      report(w, key, 'header', h.ok, h.detail);
      // the page is measured before the modal opens: an open modal locks the page with overflow hidden, which hides its width
      const pageWide = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      await tap(p, '.bi-apoie-btn');
      await p.waitForTimeout(250);
      const t = await hit(p);
      report(w, key, 'top', t.ok, `close button centre ${t.at}, on top there: ${t.ok ? 'the button' : t.on}`);
      await p.$eval('.bi-ap-panel', (e) => { e.scrollTop = e.scrollHeight; });
      await p.waitForTimeout(150);
      const bt = await hit(p);
      report(w, key, 'bottom', bt.ok, `after scrolling to the end: centre ${bt.at}, on top there: ${bt.ok ? 'the button' : bt.on}`);
      const cols = await p.$eval('.bi-ap-cards', (el) => { const kids = [...el.children], r = kids.map((k) => k.getBoundingClientRect());
        return { n: kids.length, tracks: getComputedStyle(el).gridTemplateColumns.split(' ').length, rows: new Set(r.map((x) => Math.round(x.top))).size,
          even: Math.max(...r.map((x) => x.width)) - Math.min(...r.map((x) => x.width)) <= 1,
          titles: kids.map((k) => k.querySelector('h4').firstChild.textContent.trim()) }; });
      const wantCols = w > 820 ? 3 : 1;
      report(w, key, 'columns', cols.n === 3 && cols.tracks === wantCols && cols.rows === (wantCols === 3 ? 1 : 3) && cols.even && cols.titles.join() === 'Pix,GitHub Sponsors,Cripto',
        `${cols.n} cards (${cols.titles.join(', ')}) in ${cols.tracks} column(s) over ${cols.rows} row(s), ${cols.even ? 'equal' : 'unequal'} widths; wanted ${wantCols}`);
      const hs = { doc: pageWide, panel: await p.$eval('.bi-ap-panel', (e) => e.scrollWidth - e.clientWidth) };
      await p.$eval('.bi-ap-panel', (e) => { e.scrollTop = 0; });
      // the cards on "soon"
      const soon = await p.$$eval('.bi-ap-soon', (cs) => cs.map((c) => ({ tag: [...c.querySelectorAll('.bi-ap-tag')].some((t) => t.textContent.trim() === 'Em breve' && t.getClientRects().length),
        clickable: c.querySelectorAll('a, button, code, [data-go]').length })));
      if (soon.length) {
        for (const i of soon.keys()) {
          await p.$$eval('.bi-ap-soon', (cs, i) => cs[i].click(), i); await p.waitForTimeout(60);
        }
        const after = await shown(p, '.bi-ap-view');
        const bad = soon.filter((c) => !c.tag || c.clickable).length + (after.length === 1 && after[0] === 'main' ? 0 : 1);
        report(w, key, 'soon', bad === 0, `${soon.length} cards on soon; ${bad ? `${bad} problems (a missing tag, something to click, or a view opened: ${JSON.stringify(after)})` : 'each with Em breve and nothing to click'}`);
      }
      const pixCard = await p.$$eval('.bi-ap-card', (cs) => { const c = cs.find((x) => x.querySelector('h4').firstChild.textContent.trim() === 'Pix');
        return c ? { soon: c.classList.contains('bi-ap-soon'), tag: [...c.querySelectorAll('.bi-ap-tag')].some((x) => x.textContent.trim() === 'Em breve'),
          clickable: c.querySelectorAll('a, button, code, [data-go]').length, button: (c.querySelector('button') || {}).textContent } : null; });
      const pixLive = await p.$('.bi-ap-view[data-view="pix"]') !== null;
      if (pixCard && !pixLive) {
        report(w, key, 'pix', pixCard.soon && pixCard.tag && pixCard.clickable === 0, `Pix on soon: tag ${pixCard.tag ? 'Em breve' : 'absent'}, ${pixCard.clickable} things to click`);
      }
      // the views the main view opens
      const gos = await p.$$eval('.bi-ap-view[data-view="main"] [data-go]', (bs) => [...new Set(bs.map((b) => b.dataset.go))]);
      const v = [];
      for (const go of gos) {
        await p.$eval('.bi-ap-panel', (e) => { e.scrollTop = 0; });
        await p.$eval(`.bi-ap-view[data-view="main"] [data-go="${go}"]`, (e) => e.click()); await p.waitForTimeout(120);
        const s = await shown(p, '.bi-ap-view');
        if (!(s.length === 1 && s[0] === go)) v.push(`${go}: displayed ${JSON.stringify(s)}`);
        if (go === 'crypto') {
          const bad = [];
          for (const [coin, n] of Object.entries(NETWORKS)) {
            if (n === 0) {   // on soon: dimmed, disabled, with the tag, and no panel
              const s = await p.evaluate((coin) => { const b = [...document.querySelectorAll('.bi-ap-coinsoon')].find((x) => x.firstChild.textContent.trim() === coin);
                return { found: !!b, disabled: !!b && b.disabled, tag: !!b && !!b.querySelector('.bi-ap-tag') && b.querySelector('.bi-ap-tag').textContent.trim() === 'Em breve',
                  panel: !!document.querySelector(`.bi-ap-coin[data-coin="${coin}"]`), dashed: !!b && getComputedStyle(b).borderTopStyle === 'dashed' }; }, coin);
              if (!(s.found && s.disabled && s.tag && !s.panel && s.dashed)) bad.push(`${coin} on soon: ${JSON.stringify(s)}`);
              continue;
            }
            await tap(p, `[data-coin-btn="${coin}"]`); await p.waitForTimeout(60);
            const c = await shown(p, '.bi-ap-coin');
            const nets = await p.$$eval(`.bi-ap-coin[data-coin="${coin}"] .bi-ap-net`, (es) => es.filter((e) => e.getClientRects().length).length);
            if (!(c.length === 1 && c[0] === coin && nets === n)) bad.push(`${coin}: panels ${JSON.stringify(c)}, ${nets} networks`);
            hs.panel = Math.max(hs.panel, await p.$eval('.bi-ap-panel', (e) => e.scrollWidth - e.clientWidth));
          }
          report(w, key, 'coins', bad.length === 0, bad.length ? bad.join('; ') : 'each coin alone, with its networks');
          const wrong = [];
          let rowsSeen = 0;
          for (const coin of Object.keys(NETWORKS).filter((c) => NETWORKS[c] > 0)) {
            await tap(p, `[data-coin-btn="${coin}"]`); await p.waitForTimeout(60);
            const sel = `.bi-ap-coin[data-coin="${coin}"] .bi-ap-net`;
            const rows = await p.$$eval(sel, (es) => es.map((e) => ({ name: e.querySelector('.bi-ap-net-name').textContent.trim(),
              shown: e.querySelector('code').textContent.trim(), href: e.querySelector('a').getAttribute('href'), explorer: e.querySelector('a').textContent.trim() })));
            const want = expected(coin);
            if (rows.length !== want.length) wrong.push(`${coin}: ${rows.length} rows, the file has ${want.length}`);
            for (const [i, r] of rows.entries()) {
              const e = want[i] || {};
              await p.evaluate(() => navigator.clipboard.writeText(''));
              await p.locator(`${sel} [data-copy]`).nth(i).click(); await p.waitForTimeout(80);
              const copied = await p.evaluate(() => navigator.clipboard.readText()).catch((x) => `(clipboard not readable: ${x.message})`);
              rowsSeen += 1;
              for (const [what, got, ok] of [['name', r.name, e.name], ['shown', r.shown, e.address], ['copied', copied, e.address],
                ['explorer link', r.href, e.href], ['explorer name', r.explorer, e.explorer]]) {
                if (got !== ok) wrong.push(`${coin} ${r.name}: ${what} ${JSON.stringify(got)}, the file has ${JSON.stringify(ok)}`);
              }
            }
          }
          report(w, key, 'addresses', rowsSeen > 0 && wrong.length === 0, wrong.length ? wrong.join('; ')
            : `${rowsSeen} rows: the name, the address shown and copied, and the explorer link equal the data file`);
        }
        hs.panel = Math.max(hs.panel, await p.$eval('.bi-ap-panel', (e) => e.scrollWidth - e.clientWidth));
        const back = await p.$('.bi-ap-back');
        if (back && await back.isVisible()) { await back.evaluate((e) => e.click()); await p.waitForTimeout(80); }
        const m = await shown(p, '.bi-ap-view');
        if (!(m.length === 1 && m[0] === 'main')) v.push(`Voltar from ${go}: displayed ${JSON.stringify(m)}`);
      }
      if (pixLive) {
        const want = SUPPORT && SUPPORT.pix && SUPPORT.pix.campaign_url;
        await p.waitForTimeout(100);
        if (await isOpen(p) === false) { await tap(p, '.bi-apoie-btn'); await p.waitForTimeout(150); }
        const label = await p.$eval('.bi-ap-view[data-view="main"] [data-go="pix"]', (b) => b.textContent.trim());
        await p.$eval('.bi-ap-view[data-view="main"] [data-go="pix"]', (e) => e.click()); await p.waitForTimeout(120);
        const only = await shown(p, '.bi-ap-view');
        const a = await p.$eval('.bi-ap-view[data-view="pix"] a.bi-ap-cta', (x) => ({ href: x.getAttribute('href'), target: x.target, rel: x.rel, text: x.textContent.trim() }));
        const facts = await p.$eval('.bi-ap-view[data-view="pix"] .bi-ap-facts', (x) => x.textContent);
        hs.panel = Math.max(hs.panel, await p.$eval('.bi-ap-panel', (e) => e.scrollWidth - e.clientWidth));
        await p.keyboard.press('Escape'); await p.waitForTimeout(150);
        const closed = !(await isOpen(p));
        const back = await p.evaluate(() => document.activeElement && document.activeElement.classList.contains('bi-apoie-btn'));
        const good = !!want && label === 'Apoiar com Pix' && only.length === 1 && only[0] === 'pix' && a.href === want && a.target === '_blank'
          && /noopener/.test(a.rel) && a.text === 'Abrir a vaquinha' && SUPPORT.pix.bank_screen_name && facts.includes(SUPPORT.pix.bank_screen_name) && closed && back;
        report(w, key, 'pix', good, `Pix live: button "${label}", view ${JSON.stringify(only)}, link ${a.href === want ? 'equals campaign_url' : 'is ' + a.href}, ${a.target} ${a.rel}, Escape ${closed ? 'closed it' : 'did not close it'}, focus ${back ? 'on Apoie' : 'elsewhere'}${want ? '' : ' (no BI_SUPPORT_JSON to compare)'}`);
        await tap(p, '.bi-apoie-btn'); await p.waitForTimeout(150);
      }
      report(w, key, 'views', gos.length > 0 && v.length === 0, v.length ? v.join('; ') : `${gos.join(', ')}: each alone, and back`);
      // the contact form
      const enter = async () => {
        if (await p.$eval('.bi-ap-back', (b) => !b.hidden)) await tap(p, '.bi-ap-back');
        await tap(p, '.bi-ap-view[data-view="main"] [data-go="contact"]'); await p.waitForTimeout(100);
      };
      const fill = (honey) => p.evaluate(([v, honey]) => { const f = document.querySelector('.bi-ap-form').elements;
        f.name.value = v.name; f.email.value = v.email; f.message.value = v.message; f.botcheck.checked = honey; }, [PERSON, honey]);
      const submit = () => tap(p, '.bi-ap-form [type="submit"]');
      const { endpoint, key: accessKey } = await p.$eval('.bi-ap-form', (f) => ({ endpoint: f.dataset.endpoint, key: f.dataset.key }));
      await enter();
      await p.evaluate(() => { const f = document.querySelector('.bi-ap-form').elements; f.name.value = ''; f.email.value = ''; f.message.value = ''; });
      posts.length = 0; await submit(); await p.waitForTimeout(150);
      const errs = await visible(p, '.bi-ap-err');
      report(w, key, 'empty', errs === 3 && posts.length === 0, `${errs} field messages shown, ${posts.length} requests`);
      await enter(); await fill(false); posts.length = 0; await submit(); await p.waitForTimeout(500);
      report(w, key, 'fast', posts.length === 0, `a send right after the view opened: ${posts.length} requests`);
      await enter(); await fill(true); await p.waitForTimeout(3100); posts.length = 0; await submit(); await p.waitForTimeout(500);
      report(w, key, 'honey', posts.length === 0, `a send with the honeypot checked: ${posts.length} requests`);
      await enter(); await fill(false); await p.waitForTimeout(3100); posts.length = 0; answer = 'ok'; await submit(); await p.waitForTimeout(150);
      const during = await p.$eval('.bi-ap-form [type="submit"]', (b) => ({ text: b.textContent, disabled: b.disabled }));
      await p.waitForTimeout(700);
      const body = posts[0] ? JSON.parse(posts[0].body || '{}') : {};
      const fields = body.access_key === accessKey && body.name === PERSON.name && body.email === PERSON.email && body.message === PERSON.message
        && body.subject === 'Brasil-Imposto: mensagem pelo site' && body.from_name === 'Site Brasil-Imposto' && body.botcheck === false;
      const okLine = await visible(p, '.bi-ap-sent');
      report(w, key, 'send', posts.length === 1 && posts[0].method === 'POST' && posts[0].url === endpoint && fields && during.text === 'Enviando...' && during.disabled && okLine === 1,
        `${posts.length} POST to ${posts[0] ? posts[0].url : 'nowhere'}, fields ${fields ? 'as sent' : 'wrong'}, while sending "${during.text}" ${during.disabled ? 'disabled' : 'enabled'}, success line ${okLine ? 'shown' : 'absent'}`);
      await enter(); await fill(false); await p.waitForTimeout(3100); posts.length = 0; answer = 'fail'; await submit(); await p.waitForTimeout(900);
      const errLine = await visible(p, '.bi-ap-fail');
      const kept = await p.evaluate((v) => { const f = document.querySelector('.bi-ap-form').elements; return f.name.value === v.name && f.message.value === v.message; }, PERSON);
      report(w, key, 'error', posts.length === 1 && errLine === 1 && kept, `${posts.length} POST, error line ${errLine ? 'shown' : 'absent'}, fields ${kept ? 'kept' : 'lost'}`);
      hs.panel = Math.max(hs.panel, await p.$eval('.bi-ap-panel', (e) => e.scrollWidth - e.clientWidth));
      report(w, key, 'hscroll', hs.doc <= 0 && hs.panel <= 0, `page ${hs.doc}px, panel ${hs.panel}px past the width`);
      await p.keyboard.press('Escape'); await p.waitForTimeout(150);
      report(w, key, 'escape', !(await isOpen(p)), 'Escape');
      if (!(await isOpen(p))) { await tap(p, '.bi-apoie-btn'); await p.waitForTimeout(150); }
      await tap(p, '.bi-ap-x'); await p.waitForTimeout(150);
      const focus = await p.evaluate(() => document.activeElement && document.activeElement.classList.contains('bi-apoie-btn'));
      report(w, key, 'focus', !(await isOpen(p)) && focus, `focus on ${await p.evaluate(() => String(document.activeElement.className || document.activeElement.tagName).slice(0, 30))}`);
      await tap(p, '.bi-apoie-btn'); await p.waitForTimeout(150);
      await p.mouse.click(3, (await p.evaluate(() => innerHeight)) - 3); await p.waitForTimeout(150);
      report(w, key, 'outside', !(await isOpen(p)), 'a click at the window corner, outside the panel');
      await ctx.close();
    }
  }
  await browser.close();
  for (const r of rows) console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.w}px ${r.page} | ${r.check}: ${r.detail}`);
  const bad = rows.filter((r) => !r.ok).length;
  console.log(`${rows.length} checks, ${bad} failed${control ? ' (control run)' : ''}`);
  if (control) {
    const blind = [...new Set(rows.filter((r) => r.ok).map((r) => r.check))];
    console.log(blind.length ? `BROKEN CONTROL: checks that passed with every failure planted: ${blind.join(', ')}` : 'control: every check failed, as it must');
    process.exit(blind.length ? 1 : 0);
  }
  process.exit(bad ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
