"""Paid amount of one SC state contract, read from its SICOP extract (Portal da Transparencia de SC).

Checks, to the cent, for every year: sum of payment lines == "vlpago" of the financial summary.
Splits the paid amount into net transfer to the contractor and taxes withheld (retencoes),
and compares the cumulative paid amount with the last cumulative measurement (medicao).

Usage: python3 sicop_paid.py <nutitulo> [--control]
--control adds R$ 0,01 to one payment line; the check must then fail (exit 1).
The raw extract lives only in a temporary folder that is deleted at the end.
"""
import json
import shutil
import sys
import tempfile
import urllib.request
from collections import defaultdict
from decimal import Decimal

API = "https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]={}"


def fetch(nutitulo, folder):
    path = f"{folder}/extract.json"
    with urllib.request.urlopen(API.format(nutitulo), timeout=90) as resp, open(path, "wb") as out:
        out.write(resp.read())
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def summarize(extract, control=False):
    lines = extract["contratoPagamento"]
    if control:
        lines = [dict(line) for line in lines]
        lines[0]["valor"] = str(Decimal(lines[0]["valor"]) + Decimal("0.01"))
    by_year = defaultdict(Decimal)
    by_kind = defaultdict(Decimal)
    for line in lines:
        value = Decimal(line["valor"])
        by_year[line["ano"]] += value
        kind = line["detipopreparacaopagamento"]
        by_kind["net_to_contractor" if kind == "Despesa Empenhada" else "withheld_taxes"] += value
    failures = []
    summary = {row["ano"]: Decimal(row["vlpago"]) for row in extract["contratoResumoFinanceiro"]}
    for year in sorted(set(summary) | set(by_year)):
        if summary.get(year, Decimal(0)) != by_year.get(year, Decimal(0)):
            failures.append(f"{year}: summary {summary.get(year)} vs lines {by_year.get(year)}")
    paid = sum(summary.values(), Decimal(0))
    if paid != by_kind["net_to_contractor"] + by_kind["withheld_taxes"]:
        failures.append("net + withheld != paid")
    measurements = extract.get("contratoMedicoes") or []
    last = max(measurements, key=lambda m: int(m["numero"])) if measurements else None
    dates = [line["dtreferencia"][:10] for line in lines if Decimal(line["valor"]) > 0]
    return failures, {
        "contract": extract["contrato"].get("nucontrato") or (extract["contratoResumoFinanceiro"] or [{}])[0].get("nucontrato"),
        "paid_brl": str(paid),
        "paid_by_year_brl": {y: str(v) for y, v in sorted(summary.items())},
        "net_to_contractor_brl": str(by_kind["net_to_contractor"]),
        "withheld_taxes_brl": str(by_kind["withheld_taxes"]),
        "liquidated_brl": str(sum((Decimal(r["vlliquidado"]) for r in extract["contratoResumoFinanceiro"]), Decimal(0))),
        "last_measurement": None if last is None else {
            "number": last["numero"],
            "period_end": last["periodomedicaotermino"][:10],
            "accumulated_total_brl": last["vlacumuladototal"],
        },
        "first_payment": min(dates) if dates else None,
        "last_payment": max(dates) if dates else None,
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    control = "--control" in sys.argv
    folder = tempfile.mkdtemp(prefix="sicop_")
    try:
        extract = fetch(args[0], folder)
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    failures, result = summarize(extract, control)
    if failures:
        print("CHECK FAILED:", "; ".join(failures))
        sys.exit(1)
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
