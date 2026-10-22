"""Ponte Hercilio Luz, contracts that started before 2011 (the SC Portal extracts start in 2011): supervision PJ-170/2006
(Prosul and Concremat lines) and restoration PJ-264/2008 (Consorcio Florianopolis Monumento). Payments by date, read from
the ALESC CPI final report (Relatorio Final da CPI da Ponte Hercilio Luz, Apendice A, payment tables per contract).

Checks:
 1. per contract, the sum of parsed payment lines == the TOTAL line printed in the table, to the cent;
 2. per contract, the sum of the "PGTOS NO MES" column == the same total (proves every payment row was parsed);
 3. per contract and year, payments dated 2011 onwards are compared with the "vlpago" of the contract's SICOP extract
    (Portal da Transparencia de SC): for the two PJ-170/2006 lines together, and for PJ-264/2008, the 2011-2013 sum must
    match the Portal to the cent; per-year differences (year-end timing of withheld taxes, 2014 payments missing from the
    contract extract) are reported, not failed: see the report.
--control adds R$ 0,01 to one parsed payment; check 1 must then fail (exit 1).

Usage: python3 hercilio_luz_supervision_cpi.py [--control]
The PDF (9 MB) and its text live only in a temporary folder deleted at the end.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from collections import defaultdict
from decimal import Decimal

PDF_URL = "https://portalelegis.alesc.sc.gov.br/proposicoes/legado/RQC-0016.6-2019/anexo/10766/visualizar"
SICOP = "https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]={}"
DASH = chr(0x2013)  # the PDF titles use an en dash
SECTIONS = [("Prosul", f"Contrato PJ 170/2006 {DASH} Prosul", f"Contrato PJ 170/2006 {DASH} Concremat", "53663"),
            ("Concremat", f"Contrato PJ 170/2006 {DASH} Concremat", "Contrato PJ 264/2008", "53682"),
            ("Florianopolis Monumento", f"Contrato PJ 264/2008 {DASH} Consórcio Florianópolis Monumento", "Contrato PJ 204/2014", "70204")]
STRICT_YEARS = (2011, 2012, 2013)
DATE = re.compile(r"^\d{2}/\d{2}/\d{2}(\d{2})?$")
NUM = re.compile(r"^\d{1,3}(\.\d{3})*,\d{2}$|^\d+,\d{2}$|^0$")


def money(token):
    return Decimal(token.replace(".", "").replace(",", ".")) if token != "0" else Decimal(0)


def year_of(date):
    y = date.split("/")[2]
    return int(y) if len(y) == 4 else 2000 + int(y)


def parse(text, start, end):
    begin = text.index(start)
    block = text[begin:text.index(end, begin + len(start))]
    payments, month_column, total = [], Decimal(0), None
    for line in block.splitlines():
        tokens = line.split()
        if tokens[:1] == ["TOTAL"]:
            total = money(tokens[1])
            continue
        if not tokens or not tokens[0].isdigit() or len(tokens) < 4 or not DATE.match(tokens[1]):
            continue
        dates = [i for i, t in enumerate(tokens) if DATE.match(t)]
        if len(dates) >= 4 and dates[3] + 1 < len(tokens) and NUM.match(tokens[dates[3] + 1]):
            pay_index = dates[3] + 1
            payments.append({"measurement": int(tokens[0]), "paid_on": tokens[dates[3]], "value": money(tokens[pay_index])})
            extras = tokens[pay_index + 1:]
        else:
            dash = max((i for i, t in enumerate(tokens) if t == "-"), default=None)
            extras = tokens[dash + 1:] if dash is not None else []
        extras = [t for t in extras if NUM.match(t)]
        if len(extras) == 2:
            month_column += money(extras[0])
    return payments, month_column, total


def main():
    control = "--control" in sys.argv
    folder = tempfile.mkdtemp(prefix="cpi_")
    try:
        pdf = f"{folder}/cpi.pdf"
        req = urllib.request.Request(PDF_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=600) as resp, open(pdf, "wb") as out:
            out.write(resp.read())
        subprocess.run(["pdftotext", "-layout", pdf, f"{folder}/cpi.txt"], check=True)
        text = open(f"{folder}/cpi.txt", encoding="utf-8", errors="replace").read()
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    failures, result = [], {}
    portal_by_year_both, cpi_by_year_both = defaultdict(Decimal), defaultdict(Decimal)
    for name, start, end, nutitulo in SECTIONS:
        group = "PJ-170/2006" if name in ("Prosul", "Concremat") else name
        payments, month_column, total = parse(text, start, end)
        if control and name == "Prosul":
            payments[0]["value"] += Decimal("0.01")
        paid = sum((p["value"] for p in payments), Decimal(0))
        if paid != total:
            failures.append(f"{name}: payments {paid} != TOTAL {total}")
        if month_column != total:
            failures.append(f"{name}: PGTOS NO MES {month_column} != TOTAL {total}")
        by_year = defaultdict(Decimal)
        for p in payments:
            by_year[year_of(p["paid_on"])] += p["value"]
        with urllib.request.urlopen(SICOP.format(nutitulo), timeout=90) as resp:
            extract = json.loads(resp.read())
        portal = {int(r["ano"]): Decimal(r["vlpago"]) for r in extract["contratoResumoFinanceiro"]}
        for y, v in portal.items():
            portal_by_year_both[(group, y)] += v
        for y, v in by_year.items():
            cpi_by_year_both[(group, y)] += v
        before_2011 = sum((v for y, v in by_year.items() if y <= 2010), Decimal(0))
        result[name] = {
            "nutitulo": nutitulo,
            "cpi_total_brl": str(total),
            "payment_lines": len(payments),
            "paid_by_year_brl": {str(y): str(v) for y, v in sorted(by_year.items())},
            "paid_2006_2010_brl": str(before_2011),
            "first_payment": min(payments, key=lambda p: (year_of(p["paid_on"]), p["paid_on"][3:5], p["paid_on"][:2]))["paid_on"],
            "portal_by_year_brl": {str(y): str(v) for y, v in sorted(portal.items())},
            "diff_cpi_minus_portal_2011_on": {str(y): str(by_year.get(y, Decimal(0)) - portal.get(y, Decimal(0)))
                                              for y in sorted(set(portal) | {y for y in by_year if y >= 2011})},
        }
    for key in sorted(set(portal_by_year_both) | {k for k in cpi_by_year_both if k[1] >= 2011}):
        cpi, portal = cpi_by_year_both.get(key, Decimal(0)), portal_by_year_both.get(key, Decimal(0))
        if cpi != portal:
            result.setdefault("per_year_differences", []).append(f"{key[0]} {key[1]}: CPI {cpi} vs Portal {portal}")
    for group in sorted({k[0] for k in cpi_by_year_both}):
        cpi = sum((v for k, v in cpi_by_year_both.items() if k[0] == group and k[1] in STRICT_YEARS), Decimal(0))
        portal = sum((v for k, v in portal_by_year_both.items() if k[0] == group and k[1] in STRICT_YEARS), Decimal(0))
        if cpi != portal:
            failures.append(f"{group} 2011-2013: CPI {cpi} vs Portal {portal}")
    pj170 = {k: v for k, v in cpi_by_year_both.items() if k[0] == "PJ-170/2006"}
    result["pj170_paid_2006_2010_brl"] = str(sum((v for k, v in pj170.items() if k[1] <= 2010), Decimal(0)))
    result["pj170_cpi_total_brl"] = str(sum(pj170.values(), Decimal(0)))
    print(json.dumps(result, ensure_ascii=False, indent=1))
    if failures:
        print("CHECK FAILED:", "; ".join(failures))
        sys.exit(1)


if __name__ == "__main__":
    main()
