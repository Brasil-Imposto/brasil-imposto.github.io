"""Builds the support ledger page "Livro-caixa do apoio" (spec apoie, section 11.3; round apoie-r4, option B, D234): the state
today (what came in, what went out, the balance) and, newest month first, each month's entries, infrastructure, split, payouts and
returned pay, read from data/support-ledger/ (pipelines/support/ledger.py). The site build serves it only where the livro-caixa
switch is on (site_chrome.SWITCHED_PAGES); the header and footer are the common ones. Nothing made up: a month shows only the parts
it has. No donor is named, except a source above 5% of the year's income (GOVERNANCE.md, neutrality rule 4). Every text from the
data is escaped. Python's own packages only, as every builder (the ci and the deploys run them without the locked environment).
Run: python3 docs/superpowers/tools/build-ledger-page.py
"""
import html
import sys
from pathlib import Path

import site_chrome

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from pipelines.support import ledger  # noqa: E402

PREVIEWS = REPO / "docs" / "superpowers" / "previews"
OUT = PREVIEWS / site_chrome.LEDGER_PAGE
BLOB = f"{site_chrome.REPO_URL}/blob/main"
MONTHS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro",
          "dezembro"]
e = html.escape

# the lead of round apoie-r4, word for word; the two links sit on words it already has
LEAD = ("Cada doação, cada gasto de infraestrutura e cada pagamento a quem contribui, mês a mês. A divisão de cada mês é calculada "
        f'por um <a href="{BLOB}/pipelines/support/split_month.py">script público</a>, que qualquer pessoa pode rodar e chegar aos '
        "mesmos centavos. Nenhum nome de quem doou aparece, salvo o que a "
        f'<a href="{BLOB}/GOVERNANCE.md#regras-de-neutralidade">regra das fontes</a> pede: toda fonte acima de 5% da receita do ano é '
        "publicada com o nome.")

# the ledger style of round apoie-r4 (private/apoie/build_apoie_r4.py, CSS), .r4-led-* renamed .led-*; the month box is solid,
# since the dashed one marked the round's made-up example
CSS = """
  .led-page { max-width: 860px; margin: 0 auto; padding: 28px 20px 48px; }
  .led-page h1 { font-size: 30px; margin: 0 0 12px; letter-spacing: -.01em; }
  .led-lead { margin: 0 0 12px; color: #36424D; line-height: 1.55; }
  .led-today { background: #EAF5EE; border-radius: 12px; padding: 12px 14px; color: #0E5A2C; margin: 0 0 16px; line-height: 1.5; }
  .led-month { border: 1px solid #E3E8ED; border-radius: 14px; padding: 14px; margin: 0 0 16px; }
  .led-month h2 { margin: 4px 0 8px; font-size: 17px; }
  .led-month h3 { margin: 14px 0 6px; font-size: 13.5px; color: #4A5560; text-transform: uppercase; letter-spacing: .04em; }
  .led-month table { width: 100%; border-collapse: collapse; font-size: 14px; }
  .led-month th, .led-month td { text-align: left; padding: 6px 6px; border-bottom: 1px solid #E3E8ED; vertical-align: top; }
  .led-month th { font-size: 12.5px; color: #5A6672; font-weight: 700; }
  .led-num { text-align: right !important; white-space: nowrap; font-variant-numeric: tabular-nums; }
  .led-nw { white-space: nowrap; }
  .led-tot td { font-weight: 800; border-bottom: 0; }
  .led-p { margin: 0; font-size: 14px; }
  .led-sum { margin: 14px 0 0; font-weight: 700; font-size: 14px; }
  @media (max-width: 520px) { .led-month table { font-size: 12.5px; } .led-month th, .led-month td { padding: 5px 3px; } .led-page h1 { font-size: 24px; } }
"""

PAGE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Livro-caixa do apoio · Brasil-Imposto</title>
<link rel="stylesheet" href="assets/fonts/manrope.css">
<style>
  :root { --ink: #14202B; --muted: #5B6773; --line: #E3E7EC; --paper: #FFFFFF; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink); font-family: 'Manrope', system-ui, sans-serif; -webkit-font-smoothing: antialiased; }
  a { color: var(--muted); }
@@CSS@@</style>
<!-- site-chrome:css -->
<!-- /site-chrome:css -->
</head>
<body>
<!-- site-chrome:header -->
<!-- /site-chrome:header -->
<main><div class="led-page">
<h1>Livro-caixa do apoio</h1>
@@BODY@@
</div></main>
<!-- site-chrome:js -->
<!-- /site-chrome:js -->
<!-- site-chrome:footer -->
<!-- /site-chrome:footer -->
</body>
</html>
"""


def money(cents):
    """R$ 1.234,56 from whole cents, with no float on the way."""
    reais, rest = divmod(cents, 100)
    return f"R$ {reais:,}".replace(",", ".") + f",{rest:02d}"


def amount(cents):
    """An amount inside a sentence, never broken between "R$" and the number."""
    return f'<span class="led-nw">{money(cents)}</span>'


def day(iso):
    return f"{iso[8:10]}/{iso[5:7]}"


def month_name(month):
    y, m = month.split("-")
    return f"{MONTHS[int(m) - 1].capitalize()} de {y}"


def total(items):
    return sum(i["amount_cents"] for i in items)


def link(url, text):
    return f'<a href="{e(url)}">{e(text)}</a>'


def table(head, rows, foot=None):
    """head: the column titles, a title starting with '#' is a number column; rows and foot: cells already escaped."""
    nums = [h.startswith("#") for h in head]
    th = "".join(f'<th class="led-num">{e(h[1:])}</th>' if n else f"<th>{e(h)}</th>" for h, n in zip(head, nums))
    body = "".join("<tr>" + "".join(f'<td class="led-num">{c}</td>' if n else f"<td>{c}</td>" for c, n in zip(r, nums)) + "</tr>"
                   for r in rows)
    return f"<table><tr>{th}</tr>{body}{foot or ''}</table>"


def today(months):
    """The state today; with nothing received, spent or paid, the exact text of round apoie-r4."""
    got, infra = sum(total(m["entries"]) for m in months), sum(total(m["infra"]) for m in months)
    paid = sum(total(m["payouts"]) for m in months)
    parts = ["nenhuma doação recebida" if not got else f"{amount(got)} em doações recebidas",
             "nenhum gasto de infraestrutura (o site é hospedado de graça no GitHub Pages)" if not infra
             else f"{amount(infra)} em gastos de infraestrutura",
             "nenhum pagamento" if not paid else f"{amount(paid)} em pagamentos a quem contribuiu"]
    balance = months[-1]["closing_cents"] if months else 0
    return f'<div class="led-today"><b>Até agora:</b> {parts[0]}, {parts[1]} e {parts[2]}. Saldo: {amount(balance)}.</div>'


def channel_of(entry):
    if entry["channel"] == "pix":
        name = "Pix"
    else:
        coin = " ".join(x for x in (entry.get("coin_amount"), entry.get("coin")) if x)
        name = f"Cripto ({coin})" if coin else "Cripto"
    return e(name + (f", {entry['source_name']}" if entry.get("source_name") else ""))


def proof_of(entry):
    if entry.get("tx_url"):
        return link(entry["tx_url"], "transação")
    return link(entry["statement_url"], "extrato") if entry.get("statement_url") else ""


def month_block(m):
    sums = (m["opening_cents"], total(m["entries"]), total(m["infra"]), total(m["payouts"]))
    if sums[0] + sums[1] - sums[2] - sums[3] != m["closing_cents"]:   # the page never prints a sum that does not close
        raise SystemExit(f"build-ledger-page: {m['month']} does not close to the cent (pipelines/support/ledger.py)")
    out = [f'<section class="led-month" id="mes-{e(m["month"])}"><h2>{e(month_name(m["month"]))}</h2>']
    if m["entries"]:
        rows = [[e(day(x["date"])), channel_of(x), money(x["amount_cents"]), proof_of(x)] for x in m["entries"]]
        foot = f'<tr class="led-tot"><td colspan="2">Total</td><td class="led-num">{money(sums[1])}</td><td></td></tr>'
        out.append("<h3>Entradas</h3>" + table(["Dia", "Canal", "#Valor", "Prova"], rows, foot))
    if m["infra"]:
        rows = [[e(day(x["date"])), e(x["service"]), money(x["amount_cents"]), link(x["receipt_url"], "recibo")] for x in m["infra"]]
        foot = f'<tr class="led-tot"><td colspan="2">Total</td><td class="led-num">{money(sums[2])}</td><td></td></tr>'
        out.append("<h3>Infraestrutura</h3>" + table(["Dia", "Serviço", "#Valor", "Recibo"], rows, foot))
    if m["split"]:
        s = m["split"]
        if s["shares"]:
            rows = [[e("@" + x["login"]), e(", ".join(f"#{i['number']} (peso {i['weight']})" for i in x["issues"])), str(x["points"]),
                     money(x["amount_cents"])] for x in s["shares"]]
            foot = (f'<tr class="led-tot"><td colspan="3">Centavos que ficam para o mês seguinte</td>'
                    f'<td class="led-num">{money(s["kept_cents"])}</td></tr>')
            out.append("<h3>Divisão de quem contribuiu</h3>" + table(["Quem", "Issues fechadas", "#Pontos", "#Parte"], rows, foot))
        else:
            out.append(f'<h3>Divisão de quem contribuiu</h3><p class="led-p">Nenhuma issue com peso fechada no mês: '
                       f"{amount(s['kept_cents'])} ficam para o mês seguinte.</p>")
    if m["payouts"]:
        rows = [[e("@" + x["login"]), money(x["amount_cents"]),
                 "Pix" if x["channel"] == "pix" else "Cripto" + (f" ({link(x['tx_url'], 'transação')})" if x.get("tx_url") else ""),
                 e(day(x["date"]))] for x in m["payouts"]]
        out.append("<h3>Pagamentos</h3>" + table(["Quem", "#Valor", "Canal", "Dia"], rows))
    if m["returned"]:
        rows = [[e("@" + x["login"]), e(month_name(x["split_month"])), money(x["amount_cents"]), e(day(x["date"]))] for x in m["returned"]]
        out.append("<h3>Não reclamado, de volta à divisão</h3>" + table(["Quem", "Divisão de", "#Valor", "Dia"], rows))
    out.append(f'<p class="led-sum">A conta fecha: saldo anterior {amount(sums[0])} + entradas {amount(sums[1])} - infraestrutura '
               f"{amount(sums[2])} - pagamentos {amount(sums[3])} = saldo {amount(m['closing_cents'])}.</p></section>")
    return "".join(out)


def build(months=None):
    months = ledger.load_all() if months is None else months
    body = (f'<p class="led-lead">{LEAD}</p>\n{today(months)}\n'
            + "\n".join(month_block(m) for m in sorted(months, key=lambda m: m["month"], reverse=True)))
    page = site_chrome.inject(PAGE.replace("@@CSS@@", CSS).replace("@@BODY@@", body), "livro")
    if not (chr(0x2014) not in page and chr(0x2013) not in page):
        raise SystemExit("dash found")
    return page


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(OUT.name, round(OUT.stat().st_size / 1024), "KB")
