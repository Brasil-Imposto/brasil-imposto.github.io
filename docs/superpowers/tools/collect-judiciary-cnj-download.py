"""Download each court's 2026 Anexo VIII spreadsheets from the CNJ panel (Portaria CNJ 63/2017).

The panel is a QlikView page, so the export is driven in a headless browser: filter Tribunal and Ano,
open each tab and press "Enviar para Excel". Output: data/federal/raw-pay/judiciary/cnj/<court>-<year>-all-<tab>.xlsx,
the files read by collect-judiciary-2026.py.

Needs node, playwright-core (path in the PW_CORE environment variable) and a Chromium headless shell (path in CHROME_HEADLESS).
Run: uv run python -B docs/superpowers/tools/collect-judiciary-cnj-download.py [stj tst stm tse] [--year 2026]
About 1.5 minutes per court.
"""
import argparse, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/federal/raw-pay/judiciary/cnj"
PLAYWRIGHT = Path(os.environ["PW_CORE"])  # like the other tools: the path to a playwright-core install
SHELL = Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-mac-arm64/chrome-headless-shell"
TABS = "Contracheque,Direitos Pessoais,Indeniza,Direitos Eventuais,Controle de Arquivos"

JS = r"""
const { chromium } = require(process.env.PW_CORE);
const [court, year, month, outDir, tabsArg] = process.argv.slice(2);
const tabs = tabsArg.split(',');
const URL = 'https://paineis.cnj.jus.br/QvAJAXZfc/opendoc.htm?document=qvw_l%2FPainelCNJ.qvw&host=QVS%40neodimio03&anonymous=true&sheet=shPORT63Relatorios';
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await chromium.launch({ executablePath: process.env.SHELL_PATH, args: ['--no-sandbox'] });
  const ctx = await b.newContext({ acceptDownloads: true, viewport: { width: 1600, height: 1000 } });
  const page = await ctx.newPage();
  await page.goto(URL, { timeout: 90000 });
  await page.waitForSelector("xpath=//*[@title='Tribunal']", { timeout: 90000 });
  await sleep(4000);
  async function pick(title, value) {
    await page.click(`xpath=//*[@title='${title}']//*[@title='Pesquisar']`);
    await page.waitForSelector('xpath=/html/body/div[2]/input', { state: 'visible', timeout: 20000 });
    await page.fill('xpath=/html/body/div[2]/input', value);
    await page.press('xpath=/html/body/div[2]/input', 'Enter');
    await sleep(5000);
  }
  await pick('Tribunal', court);
  await pick('Ano', year);
  if (month !== 'all') await pick('Mês Referencia', month);
  for (const tab of tabs) {
    await page.locator('td', { hasText: tab }).first().click({ timeout: 20000 });
    await sleep(6000);
    const dlP = page.waitForEvent('download', { timeout: 60000 }).catch(() => null);
    const popP = ctx.waitForEvent('page', { timeout: 60000 }).catch(() => null);
    await page.locator("xpath=//*[@title='Enviar para Excel']").filter({ visible: true }).first().click();
    const first = await Promise.race([dlP, popP]);
    const target = `${outDir}/${court}-${year}-${month}-${tab}.xlsx`;
    let saved = null;
    if (first && first.saveAs) { await first.saveAs(target); saved = target; }
    else if (first) { const d = await dlP; if (d) { await d.saveAs(target); saved = target; } }
    console.log('TAB', tab, 'SAVED', saved);
    if (!saved) process.exitCode = 2;
  }
  await b.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("courts", nargs="*", default=["stj", "tst", "stm", "tse"])
    ap.add_argument("--year", default="2026")
    a = ap.parse_args()
    for need in (PLAYWRIGHT, SHELL):
        if not need.exists():
            sys.exit(f"missing: {need}")
    if not shutil.which("node"):
        sys.exit("missing: node")
    OUT.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PW_CORE=str(PLAYWRIGHT), SHELL_PATH=str(SHELL))
    failed = []
    with tempfile.TemporaryDirectory() as tmp:
        js = Path(tmp) / "cnj-export.js"
        js.write_text(JS)
        for court in a.courts:
            r = subprocess.run(["node", str(js), court, a.year, "all", str(OUT), TABS], env=env, capture_output=True, text=True, timeout=600)
            print(court, r.returncode, r.stdout.strip().replace("\n", " | "), r.stderr.strip()[-300:])
            if r.returncode != 0:
                failed.append(court)
    if failed:
        sys.exit(f"export failed for: {', '.join(failed)}")


if __name__ == "__main__":
    main()
