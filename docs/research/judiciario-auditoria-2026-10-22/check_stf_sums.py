"""Audit check, 2026-10-22: every STF number on the "Os 3 Poderes" page, recomputed to the cent from the repository.

Reads data/federal/judiciary-2026.json (what the collector wrote) and the page's data asset
(docs/superpowers/previews/assets/tres-poderes-r3-data.js), and checks:
  1. each item's monthly figure is its 2026 total divided by the months the note says, rounded as the collector rounds
     (Python round on a float); the cases where that differs from rounding half up are listed as a finding;
  2. the page asset carries the same items and figures as the data file;
  3. each person's "Total por mês" is the sum of the item figures, and equals the value read on screen (local build, 2026-10-22);
  4. the salary line is 8 times the subsídio of Lei 14.520/2023 as the data file records it;
  5. the group: the sum of the 10, the average, and the part the page puts under "mandato e equipe".
--plant adds R$ 0,01 to one item's 2026 total in memory; the check must then fail (exit 1).
--plant-screen adds R$ 0,01 to one value read on screen; the check must then fail too.
Run: python3 docs/research/judiciario-auditoria-2026-10-22/check_stf_sums.py [--plant | --plant-screen]
Read-only: writes nothing.
"""
import json, re, sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
data = json.loads((ROOT / "data/federal/judiciary-2026.json").read_text())
asset = (ROOT / "docs/superpowers/previews/assets/tres-poderes-r3-data.js").read_text()
page = json.loads(asset[asset.index("=") + 1:].strip().rstrip(";"))
plant = "--plant" in sys.argv
if plant:
    fachin = next(p for p in data["people"] if p["id"] == "stf:edson-fachin")
    next(it for it in fachin["items"] if it["key"] == "vacation")["year_total"] += 0.01

# read on screen, local build of main 615f7f3, 2026-10-22 (sheet of each person, "TOTAL POR MÊS")
SCREEN = {"stf:edson-fachin": 62805.71, "stf:flavio-dino": 53514.31, "stf:alexandre-moraes": 53224.52, "stf:gilmar-mendes": 73023.68}
if "--plant-screen" in sys.argv:
    SCREEN["stf:gilmar-mendes"] += 0.01
NOT_OWN = {"per_diem", "tse_per_diem"}  # build-tres-poderes-r3-data.py

bad, half = [], []
def eq(a, b, what):
    if abs(a - b) > 0.005:
        bad.append(f"{what}: {a:.2f} != {b:.2f}")

subsidio = next(it["value_monthly"] for pos in data["positions"] if pos["id"] == "ministros-stf" for it in pos["items"] if it["key"] == "salary")
stf = [p for p in data["people"] if p["court"] == "STF"]
pstf = {p["id"]: p for p in page["people"] if p.get("court") == "STF"}
assert len(stf) == 10 and len(pstf) == 10, (len(stf), len(pstf))
g_total = g_own = 0.0
for p in stf:
    total = own = 0.0
    for it in p["items"]:
        n = int(re.search(r"média = total / (\d+) meses", it["note"]).group(1))
        eq(it["monthly"], round(it["year_total"] / n, 2), f"{p['name']} {it['key']} monthly = year_total / {n}")
        half_up = float((Decimal(str(it["year_total"])) / n).quantize(Decimal("0.01"), ROUND_HALF_UP))
        if abs(half_up - it["monthly"]) > 0.005:
            half.append(f"{p['name']} {it['key']}: {it['year_total']:.2f} / {n} = {Decimal(str(it['year_total'])) / n}, shown {it['monthly']:.2f}, half-up {half_up:.2f}")
        pit = next(x for x in pstf[p["id"]]["items"] if x["key"] == it["key"])
        eq(pit["monthly"], it["monthly"], f"{p['name']} {it['key']} page monthly")
        eq(pit["year_total"], it["year_total"], f"{p['name']} {it['key']} page year_total")
        total += it["monthly"]
        own += 0 if it["key"] in NOT_OWN else it["monthly"]
        if it["key"] == "salary":
            eq(it["year_total"], round(8 * subsidio, 2), f"{p['name']} salary = 8 x subsídio")
    if p["id"] in SCREEN:
        eq(total, SCREEN[p["id"]], f"{p['name']} total on screen")
    print(f"{p['name']:<20} total {total:>10.2f}  para a pessoa {own:>10.2f}  mandato e equipe {total - own:>8.2f}")
    g_total += total; g_own += own
eq(g_total, 620538.99, "group sum"); eq(g_own, 616027.39, "group para a pessoa"); eq(g_total - g_own, 4511.60, "group mandato e equipe")
eq(round(g_total / 10, 2), 62053.90, "group average")
print(f"GROUP sum {g_total:.2f}, average {g_total / 10:.2f}, para a pessoa {g_own:.2f}, mandato e equipe {g_total - g_own:.2f}")
print(f"half-cent cases rounded down by the collector (float round), a finding, not a failure: {len(half)}" + "".join("\n  " + h for h in half))
print("FAIL" if bad else "PASS", f"({len(bad)} differences)" + ("".join("\n  " + b for b in bad)))
sys.exit(1 if bad else 0)
