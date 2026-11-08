"""The support ledger (spec apoie 11.3): one JSON per month in data/support-ledger/, valid against schemas/support-ledger.schema.json.
The balance closes to the cent (opening + entries - infrastructure - payouts = closing), each month opens with the previous closing,
nothing is paid or returned beyond what a split left owed, and a split's shares plus its kept cents equal its pool. The pool of a
month is its closing balance minus what earlier splits still owe after that month's payouts and returns (spec 11.2, items 5 and 9)."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

REPO = Path(__file__).resolve().parents[2]
DIR = REPO / "data" / "support-ledger"
SCHEMA = json.loads((REPO / "schemas" / "support-ledger.schema.json").read_text(encoding="utf-8"))


def load_all():
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(DIR.glob("*.json"))]


def _next(month):
    y, m = map(int, month.split("-"))
    return f"{y + (m == 12)}-{m % 12 + 1:02d}"


def _sum(items):
    return sum(i["amount_cents"] for i in items)


def owed(months, until):
    """What each (login, split month) is still owed after every payout and return up to and including the month `until`."""
    left = {}
    for m in months:
        if m["month"] > until:
            break
        for p in m["payouts"] + m["returned"]:
            left[(p["login"], p["split_month"])] = left.get((p["login"], p["split_month"]), 0) - p["amount_cents"]
        if m["split"] and m["month"] < until:
            for s in m["split"]["shares"]:
                left[(s["login"], m["month"])] = left.get((s["login"], m["month"]), 0) + s["amount_cents"]
    return left


def pool_cents(months, month):
    m = next(x for x in months if x["month"] == month)
    return m["closing_cents"] - sum(v for v in owed(months, month).values() if v > 0)


def problems(months):
    out, validator, prev = [], Draft202012Validator(SCHEMA, format_checker=FormatChecker()), None
    for m in months:
        errors = [f"{m.get('month')}: {e.message}" for e in validator.iter_errors(m)]
        if errors:   # this month's arithmetic is not read, the next months' still is
            out += errors
            continue
        if prev and m["month"] != _next(prev["month"]):
            out.append(f"{m['month']}: comes after {prev['month']}, not the month after it")
        if m["opening_cents"] + _sum(m["entries"]) - _sum(m["infra"]) - _sum(m["payouts"]) != m["closing_cents"]:
            out.append(f"{m['month']}: the balance does not close to the cent")
        if prev and m["opening_cents"] != prev["closing_cents"]:
            out.append(f"{m['month']}: opens with {m['opening_cents']}, the previous month closed with {prev['closing_cents']}")
        if m["split"] and _sum(m["split"]["shares"]) + m["split"]["kept_cents"] != m["split"]["pool_cents"]:
            out.append(f"{m['month']}: shares plus kept cents differ from the pool")
        if m["split"] and m["split"]["pool_cents"] != pool_cents(months, m["month"]):
            out.append(f"{m['month']}: the split's pool is {m['split']['pool_cents']}, the rule gives {pool_cents(months, m['month'])}")
        prev = m
    if not out and months:
        left = {}
        for m in months:
            for p in m["payouts"] + m["returned"]:
                k = (p["login"], p["split_month"])
                left[k] = left.get(k, 0) - p["amount_cents"]
                if left[k] < 0:
                    out.append(f"{m['month']}: {p['login']} paid or returned more than owed for {p['split_month']}")
            if m["split"]:
                for s in m["split"]["shares"]:
                    left[(s["login"], m["month"])] = left.get((s["login"], m["month"]), 0) + s["amount_cents"]
    return out
