"""ETE Insular (Casan): reads the two official cumulative figures the Casan publishes and checks them to the cent.

1. SAP contract balance (Portal da Transparencia da Casan, "Acompanhamento dos Saldos Contratuais"):
   check valorContrato - valorConsumido == valorAtual (the "Saldo" the extract page shows).
2. "Obras de expansao" table (CSV): check that the "SES Insular - Ampliacao ETE e Bacias D/F" principal equals
   the principal of contract EOC 1246/2020 (original + amendments, no readjustments) plus contract EOC 1534/2026.

Usage: python3 casan_insular_check.py [--control]
--control plants R$ 0,01 in the consumed value; the check must then fail (exit 1).
Nothing is written to disk.
"""
import json
import sys
import urllib.request
from decimal import Decimal

BASE = "https://transparencia.casan.com.br"
SAP = BASE + "/data/contratos?empresafiltro%5B%5D=2000009269&dtinivigenciainifiltro=2000-01-01&dtinivigenciafimfiltro=2026-12-31&page=1"
SAP_DATE = BASE + "/data/contratos/dataAtualizacao"
OBRAS = BASE + "/data/download/4981/2"
EOC_1246_PRINCIPAL = Decimal("197768490.12")   # original + amendments, data/works/ete-insular.json (value_principal_brl)
EOC_1534_VALUE = Decimal("31190417.28")        # contract signed 15/09/2026, data/works/ete-insular.json


def get(url):
    with urllib.request.urlopen(url, timeout=90) as resp:
        return resp.read()


def money(text):
    text = text.replace("R$", "").strip()
    return Decimal("0") if text in ("-", "") else Decimal(text.replace(".", "").replace(",", "."))


def main():
    control = "--control" in sys.argv
    failures = []
    rows = json.loads(get(SAP))["lista"]["data"]
    row = next(r for r in rows if r["numeroContrato"] == "EOC001246/2020")
    contract = Decimal(str(row["valorContrato"]))
    consumed = Decimal(str(row["valorConsumido"])) + (Decimal("0.01") if control else 0)
    balance = Decimal(str(row["valorAtual"]))
    if contract - consumed != balance:
        failures.append(f"SAP: contract {contract} - consumed {consumed} != balance {balance}")
    csv = get(OBRAS).decode("latin-1")
    line = next(l for l in csv.splitlines() if "SES Insular" in l)
    cells = line.split(";")
    principal, billed = money(cells[6]), money(cells[7])
    if principal != EOC_1246_PRINCIPAL + EOC_1534_VALUE:
        failures.append(f"Obras: principal {principal} != {EOC_1246_PRINCIPAL} + {EOC_1534_VALUE}")
    as_of = [l for l in csv.splitlines() if l.startswith("Dados atualizados")]
    if failures:
        print("CHECK FAILED:", "; ".join(failures))
        sys.exit(1)
    print(json.dumps({
        "sap_loaded_at": json.loads(get(SAP_DATE))["dataAtualizacao"],
        "sap_contract_brl": str(contract),
        "sap_consumed_brl": str(consumed),
        "sap_balance_brl": str(balance),
        "obras_row": cells[1],
        "obras_start_end": [cells[4], cells[5]],
        "obras_principal_brl": str(principal),
        "obras_principal_billed_brl": str(billed),
        "obras_as_of": as_of[0].split(";")[0] if as_of else None,
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
