// What "Os 3 Poderes" shows for the STF after D154 (spec BRASIL-IMPOSTO_SPEC_judiciario-dados_2026-10-22), read on the screen:
//   - each minister's full sheet: the "Média por mês" equals the average summed by hand in the audit, its note names the months,
//     the lines shown add up to it, and no line says "não recebe" (a payroll zero reads "sem valor na folha publicada");
//   - the TSE's lines sit under "Pago pelo TSE" for the four ministers the TSE pays;
//   - Fachin's sheet says "No STF desde 16/06/2015" and "Presidente do STF desde 29/09/2025"; the tree's card of the post, in
//     "Quem ocupa em 2026", says "desde 29/09/2025";
//   - each minister's card in the list: the same total and no "não recebe";
//   - no sheet is wider than its box (the long TSE text wraps);
//   - every judge of STJ, TST, STM and TSE too: the lines shown add up to the "Média por mês", and nothing reads "não recebe".
// Usage: node tres-poderes-judiciary-check.cjs <page.html | https://url> [--control]
// --control plants three errors before the page reads its data (R$ 0,01 off Dino's holiday line; Gilmar's housing zero turned
// back into a plain "not used"; Fachin's presidency dated from his admission; the old CSS that kept a long value on one line): the
// run must then report exactly those: Dino's total, Gilmar's "não recebe", Fachin on his sheet and the tree's card, and the four
// sheets with the long TSE text wider than their box; and one STM judge's payroll zero turned back into "not used".
// Env: PW_CORE (path to playwright-core), CHROME_HEADLESS (chrome-headless-shell binary), VT_WIDTH (default 1440).
const path = require('path');

const EXPECTED = { 'stf:edson-fachin': 62805.72, 'stf:alexandre-moraes': 53224.53, 'stf:gilmar-mendes': 73023.68, 'stf:carmen-lucia': 62805.72,
  'stf:dias-toffoli': 72641.75, 'stf:luiz-fux': 62805.72, 'stf:nunes-marques': 64775.71, 'stf:andre-mendonca': 63745.91,
  'stf:cristiano-zanin': 51196.01, 'stf:flavio-dino': 53514.32 };
const TSE = ['stf:gilmar-mendes', 'stf:dias-toffoli', 'stf:nunes-marques', 'stf:andre-mendonca'];
const brl = (t) => +t.replace(/[^\d,−-]/g, '').replace(/\./g, '').replace(',', '.').replace('−', '-');

(async () => {
  const pagePath = process.argv[2], control = process.argv.includes('--control');
  const origin = /^https?:\/\//.test(pagePath) ? new URL(pagePath).origin : null;
  const url = origin ? pagePath.split('#')[0] : 'file://' + path.resolve(pagePath);
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox'] });
  const bad = {}, errors = [];
  let checkedAll = 0;
  const fail = (id, why) => { (bad[id] = bad[id] || []).push(why); };
  try {
    const ctx = await browser.newContext({ viewport: { width: +(process.env.VT_WIDTH || 1440), height: 900 } });
    await ctx.route('**/*', (r) => { const u = r.request().url(); return u.startsWith('file:') || (origin && u.startsWith(origin)) ? r.continue() : r.abort(); });
    if (control) {
      await ctx.addInitScript(() => {
        let v;
        Object.defineProperty(window, 'TP3', { configurable: true, get: () => v, set: (d) => {
          d.people.find((p) => p.id === 'stf:flavio-dino').items.find((i) => i.key === 'vacation').monthly -= 0.01;
          delete d.people.find((p) => p.id === 'stf:gilmar-mendes').items.find((i) => i.key === 'housing').state;
          d.people.find((p) => p.id === 'stf:edson-fachin').office.since = '2015-06-16';
          delete d.people.find((p) => p.court === 'STM').items.find((i) => i.state === 'zero_payroll').state;
          document.addEventListener('DOMContentLoaded', () => document.head.insertAdjacentHTML('beforeend', '<style>.others li b{white-space:nowrap}</style>'));
          v = d;
        } });
      });
    }
    const open = async (hash) => {
      const page = await ctx.newPage();
      page.on('pageerror', (e) => errors.push(e.message));
      await page.goto(url + hash);
      await page.waitForSelector('body[data-ready="1"]', { timeout: 120000 });
      return page;
    };
    for (const id of Object.keys(EXPECTED)) {
      const page = await open('#p=' + encodeURIComponent(id));
      await page.waitForSelector('[data-back]:not([hidden]) [data-sheet] .big', { timeout: 20000 });
      const s = await page.$eval('[data-sheet]', (sh) => ({
        text: sh.innerText,
        lines: [...sh.querySelectorAll('.p-cols .box:first-child .r.person .vl')].map((e) => e.innerText),
        big: sh.querySelector('.big span').innerText, total: sh.querySelector('.big b').innerText,
        note: (sh.querySelector('.big + .tnote') || {}).innerText || '', blk: (sh.querySelector('.blk') || {}).innerText || '',
        wide: [...sh.querySelectorAll('.box')].some((b) => b.scrollWidth > b.clientWidth + 1) || sh.scrollWidth > sh.clientWidth + 1 }));
      const total = brl(s.total), sum = s.lines.filter((t) => /por mês/.test(t)).reduce((a, t) => a + brl(t.split('\n')[0]), 0);
      if (Math.abs(total - EXPECTED[id]) > 0.001) fail(id, `sheet total ${total} != ${EXPECTED[id]}`);
      if (Math.abs(sum - total) > 0.001) fail(id, `sheet lines add up to ${sum.toFixed(2)}, total ${total}`);
      if (!/^média por mês$/i.test(s.big.trim()) || !/meses/.test(s.note)) fail(id, `total label "${s.big}" / note "${s.note}"`);
      if (/não recebe/.test(s.text)) fail(id, 'sheet says "não recebe"');
      if (TSE.includes(id) !== /^PAGO PELO TSE/i.test(s.blk)) fail(id, `TSE block "${s.blk}"`);
      if (id === 'stf:edson-fachin' && !(/No STF desde\s+16\/06\/2015/.test(s.text) && /Presidente do STF desde\s+29\/09\/2025/.test(s.text))) fail(id, 'dates');
      if (/No cargo desde/.test(s.text)) fail(id, '"No cargo desde" still shown');
      if (s.wide) fail(id, 'sheet wider than its box');
      await page.close();
    }
    const page = await open('');
    // every judge of every court: the lines shown add up to the average, which says so, and nothing reads "não recebe"
    const all = await page.evaluate(() => window.TP3.people.filter((p) => p.house === 'judiciario' && p.items.length).map((p) => p.id));
    for (const id of all) {
      checkedAll++;
      await page.evaluate((h) => { location.hash = h; }, '#p=' + encodeURIComponent(id));
      await page.waitForFunction((n) => { const h = document.querySelector('[data-sheet] h2'); return h && h.innerText === n; },
        await page.evaluate((i) => window.TP3.people.find((p) => p.id === i).name, id), { timeout: 10000 });
      const s = await page.$eval('[data-sheet]', (sh) => ({ text: sh.innerText, big: sh.querySelector('.big span').innerText, total: sh.querySelector('.big b').innerText,
        lines: [...sh.querySelectorAll('.p-cols .box:first-child .r.person .vl')].map((e) => e.innerText),
        wide: [...sh.querySelectorAll('.box')].some((b) => b.scrollWidth > b.clientWidth + 1) }));
      const sum = s.lines.filter((t) => /por mês/.test(t)).reduce((a, t) => a + brl(t.split('\n')[0]), 0);
      if (Math.abs(sum - brl(s.total)) > 0.005) fail(id, `lines add up to ${sum.toFixed(2)}, average ${s.total}`);
      if (!/^média por mês$/i.test(s.big.trim())) fail(id, `total label "${s.big}"`);
      if (/não recebe/.test(s.text)) fail(id, 'sheet says "não recebe"');
      if (s.wide && !EXPECTED[id]) fail(id, 'sheet wider than its box');
    }
    await page.evaluate(() => { history.replaceState(null, '', location.pathname); });
    await page.reload(); await page.waitForSelector('body[data-ready="1"]');
    await page.click('button[data-mode="pessoa"]');  // the tree's card shows who holds the post in this mode
    const node = await page.$eval('[data-node="presidente-stf"]', (n) => n.innerText);
    if (!/desde 29\/09\/2025/.test(node) || /16\/06\/2015/.test(node)) fail('stf:edson-fachin', 'tree card date');
    await page.click('button[data-house="judiciario"]');
    for (const id of Object.keys(EXPECTED)) {
      await page.fill('[data-q]', '');
      await page.fill('[data-q]', id === 'stf:carmen-lucia' ? 'Cármen' : id.split(':')[1].split('-').pop());
      const c = await page.waitForSelector(`[data-card="${id}"]`, { timeout: 10000 }).then((el) => el.innerText()).catch(() => null);
      if (c == null) { fail(id, 'card not found'); continue; }
      const t = brl(c.split(/TOTAL POR MÊS|MÉDIA POR MÊS/i)[1] || '');
      if (Math.abs(t - EXPECTED[id]) > 0.001) fail(id, `card total ${t} != ${EXPECTED[id]}`);
      if (/não recebe/.test(c)) fail(id, 'card says "não recebe"');
    }
  } finally {
    await browser.close();
  }
  const ids = Object.keys(bad).sort();
  for (const id of ids) console.log(`FAIL ${id}: ${bad[id].join('; ')}`);
  console.log(`checked ${Object.keys(EXPECTED).length} STF ministers in detail and ${checkedAll} judges of every court: ${ids.length} with problems, page errors=${errors.length}${control ? ' (control run)' : ''}`);
  if (control) {
    const want = { 'stf:andre-mendonca': /^sheet wider/, 'stf:dias-toffoli': /^sheet wider/, 'stf:edson-fachin': /dates; tree card/, 'stf:flavio-dino': /sheet total/,
      'stf:gilmar-mendes': /não recebe.*sheet wider|sheet wider.*não recebe/, 'stf:nunes-marques': /^sheet wider/ };
    const stm = ids.filter((i) => i.startsWith('stm:') && /não recebe/.test(bad[i].join()));
    if (stm.length === 1) want[stm[0]] = /^sheet says "não recebe"$/;
    // the old CSS also widens the other courts' sheets with a long TSE text: those may only report that
    for (const i of ids) if (!want[i] && !i.startsWith('stf:')) want[i] = /^sheet wider than its box$/;
    const ok = stm.length === 1 && ids.join(',') === Object.keys(want).sort().join(',') && ids.every((id) => want[id].test(bad[id].join('; ')));
    console.log(ok ? 'control: every planted error caught' : 'BROKEN CONTROL: the planted errors were not all caught');
    process.exit(ok ? 0 : 1);
  }
  process.exit(ids.length || errors.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
