"""Banco Master: arithmetic checks on the official BRB figures used in the report (values transcribed from BRB filings
on the CVM system; nothing is downloaded).

Checks, to the cent: capital increase maximum and minimum = shares x issue price; capital after = capital before +
increase (both bounds). --control changes the issue price by R$ 0,01; the checks must then fail (exit 1).
"""
import sys
from decimal import Decimal as D

PRICE = D("5.29")                      # Aviso aos Acionistas, 09/03/2026: "preco de emissao de R$ 5,29"
SHARES_MAX, SHARES_MIN = 1_675_000_000, 100_000_000
AMOUNT_MAX, AMOUNT_MIN = D("8860750000.00"), D("529000000.00")
CAPITAL_BEFORE = D("2344020829.07")
CAPITAL_AFTER_MAX, CAPITAL_AFTER_MIN = D("11204770829.07"), D("2873020829.07")


def main():
    price = PRICE + (D("0.01") if "--control" in sys.argv else 0)
    failures = []
    if SHARES_MAX * price != AMOUNT_MAX:
        failures.append(f"max: {SHARES_MAX} x {price} = {SHARES_MAX * price} != {AMOUNT_MAX}")
    if SHARES_MIN * price != AMOUNT_MIN:
        failures.append(f"min: {SHARES_MIN} x {price} = {SHARES_MIN * price} != {AMOUNT_MIN}")
    if CAPITAL_BEFORE + SHARES_MAX * price != CAPITAL_AFTER_MAX:
        failures.append("capital after (max) does not close")
    if CAPITAL_BEFORE + SHARES_MIN * price != CAPITAL_AFTER_MIN:
        failures.append("capital after (min) does not close")
    if failures:
        print("CHECK FAILED:", "; ".join(failures))
        sys.exit(1)
    print("ok: capital increase R$", AMOUNT_MIN, "to R$", AMOUNT_MAX, "closes with price and capital")


if __name__ == "__main__":
    main()
