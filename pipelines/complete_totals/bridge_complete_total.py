"""Ponte Hercilio Luz: complete paid total of the 13 restoration contracts (2006 to 2020), with the payments before 2011
and the 2014 payments of the supervision contract PJ-170/2006 read from the ALESC CPI final report.

Inputs (read only): data/hercilio-luz-paid-by-contract.json (Portal SICOP net paid per contract, 2011-2020) and the
output of hercilio_luz_supervision_cpi.py (run here). Pass 1: Decimal sum contract by contract, using the CPI table total for
the three contracts that started before 2011. Pass 2: integer cents, starting from the Portal grand total and swapping
the Portal amounts of those three contracts for the CPI totals. Both passes must agree to the cent.
--control adds R$ 0,01 to one contract in pass 1; the check must then fail (exit 1).
"""
import json
import pathlib
import subprocess
import sys
from decimal import Decimal

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CPI_NAMES = {"PJ-00170/2006": "Concremat", "PJ-00170/2006/PROSUL": "Prosul", "PJ-00264/2008": "Florianopolis Monumento"}


def main():
    control = "--control" in sys.argv
    portal = json.loads((ROOT / "data" / "hercilio-luz-paid-by-contract.json").read_text(encoding="utf-8"))
    run = subprocess.run([sys.executable, str(HERE / "hercilio_luz_supervision_cpi.py")], capture_output=True, text=True)
    if run.returncode != 0:
        print("CPI check failed:", run.stdout[-500:], run.stderr[-500:])
        sys.exit(1)
    cpi = json.loads(run.stdout)
    rows = []
    for c in portal["contracts"]:
        if c["number"] in CPI_NAMES:
            rows.append((c["number"], Decimal(cpi[CPI_NAMES[c["number"]]]["cpi_total_brl"]), "CPI ALESC, Apendice A"))
        else:
            rows.append((c["number"], Decimal(str(c["net_paid_brl"])), "Portal SC, extrato SICOP"))
    if control:
        rows[0] = (rows[0][0], rows[0][1] + Decimal("0.01"), rows[0][2])
    pass_1 = sum((value for _, value, _ in rows), Decimal(0))
    cents = round(Decimal(str(portal["total_net_paid_portal_brl"])) * 100)
    for c in portal["contracts"]:
        if c["number"] in CPI_NAMES:
            cents += round(Decimal(cpi[CPI_NAMES[c["number"]]]["cpi_total_brl"]) * 100) - round(Decimal(str(c["net_paid_brl"])) * 100)
    pass_2 = Decimal(cents) / 100
    result = {
        "contracts": [{"number": n, "paid_brl": str(v), "source": s} for n, v, s in rows],
        "total_paid_brl_pass_1": str(pass_1),
        "total_paid_brl_pass_2": str(pass_2),
        "previous_total_brl": str(Decimal(str(portal["total_net_paid_brl"]))),
        "added_vs_previous_brl": str(pass_1 - Decimal(str(portal["total_net_paid_brl"]))),
        "pj170_paid_2006_2010_brl": cpi["pj170_paid_2006_2010_brl"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=1))
    if pass_1 != pass_2:
        print(f"CHECK FAILED: pass 1 {pass_1} != pass 2 {pass_2}")
        sys.exit(1)


if __name__ == "__main__":
    main()
