"""The Judiciary's records on "Os 3 Poderes" (spec BRASIL-IMPOSTO_SPEC_judiciario-dados_2026-10-22, D154). Each check is a
function that returns the problems it finds; each test runs it on the committed data (no problems) and on a copy with one
planted error (the problem must be found)."""
import copy
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "pipelines" / "politicians"))
import judiciary_view  # noqa: E402

FED = REPO / "data" / "federal"
ASSET = REPO / "docs" / "superpowers" / "previews" / "assets" / "tres-poderes-r3-data.js"
PRESIDENCY_SOURCE = "https://noticias.stf.jus.br/postsnoticias/ministro-edson-fachin-assume-hoje-29-a-presidencia-do-stf/"
# Média por mês of each STF minister after D154, summed by hand from the eGesp totals of January to August 2026 (audit, section 8)
EXPECTED = {"stf:edson-fachin": 62805.72, "stf:alexandre-moraes": 53224.53, "stf:gilmar-mendes": 73023.68, "stf:carmen-lucia": 62805.72,
            "stf:dias-toffoli": 72641.75, "stf:luiz-fux": 62805.72, "stf:nunes-marques": 64775.71, "stf:andre-mendonca": 63745.91,
            "stf:cristiano-zanin": 51196.01, "stf:flavio-dino": 53514.32}


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def page_people():
    a = ASSET.read_text(encoding="utf-8")
    return json.loads(a[a.index("=") + 1:].strip().rstrip(";"))["people"]


def fresh_records(src=None):
    src = src or load(FED / "judiciary-2026.json")
    offices = judiciary_view.offices(load(FED / "positions-2026.json")["positions"])
    return {x["id"]: judiciary_view.record(x, offices) for x in src["people"]}


def stale(page, fresh):
    """Records on the page that differ from what the module builds from the data file."""
    return [p["id"] for p in page if p["house"] == "judiciario" and p != fresh.get(p["id"])]


def sums(page):
    """STF totals: each monthly figure is its total over the months, rounded half up, and the lines add up to the expected total."""
    bad = []
    for p in page:
        if p.get("court") != "STF":
            continue
        for it in p["items"]:
            if it["monthly"] != judiciary_view.average(it["year_total"], judiciary_view.months_count(it["note"])):
                bad.append(f"{p['id']} {it['key']}")
        if abs(round(sum(it["monthly"] for it in p["items"]), 2) - EXPECTED[p["id"]]) > 0.001:
            bad.append(f"{p['id']} total")
    return bad


def states(page):
    """STF items carry a state; a zero is "zero_payroll", never shown as not received; TSE items are their own block."""
    bad = []
    for p in page:
        if p.get("court") != "STF":
            continue
        for it in p["items"]:
            want = "paid" if it["year_total"] else "zero_payroll"
            if it.get("state") != want or (it["key"].startswith("tse_") != (it.get("block") == "tse")):
                bad.append(f"{p['id']} {it['key']}")
        if not p.get("total_label") or not p.get("total_note") or (any(i.get("block") == "tse" for i in p["items"]) and "TSE" not in p["total_note"]):
            bad.append(f"{p['id']} total label")
    return bad


def dates(page):
    """Every STF record says when the person joined the court; the president also says since when he presides, with the source."""
    bad = [p["id"] for p in page if p.get("court") == "STF" and ("since" in p or not p.get("court_since"))]
    fachin = next(p for p in page if p["id"] == "stf:edson-fachin")
    if fachin.get("court_since") != "2015-06-16" or (fachin.get("office") or {}) != {"label": "Presidente do STF", "since": "2025-09-29", "source": PRESIDENCY_SOURCE}:
        bad.append("stf:edson-fachin office")
    return bad


class JudiciaryViewTest(unittest.TestCase):
    def test_average_is_decimal_half_up(self):
        self.assertEqual(judiciary_view.average(15455.40, 8), 1931.93)
        self.assertEqual(judiciary_view.average(92429.97, 8), 11553.75)
        # control: the float rounding the collector used gives the other cent, so this test tells the two apart
        self.assertEqual(round(15455.40 / 8, 2), 1931.92)

    def test_months_label_keeps_the_same_months(self):
        cases = {"jan, mar, abr, mai, jun, jul, ago 2026": "jan e mar a ago 2026", "jan a ago 2026": "jan a ago 2026",
                 "jan, fev, abr 2026": "jan, fev e abr 2026", "mar 2026": "mar 2026"}
        for long, short in cases.items():
            self.assertEqual(judiciary_view.months_label(long), short)
        # control: the shortened label must name the same months, so a dropped month is caught
        self.assertNotEqual(judiciary_view.months_label("jan, mar, abr, mai, jun, jul, ago 2026"), "mar a ago 2026")

    def test_months_count_needs_the_note(self):
        self.assertEqual(judiciary_view.months_count("Soma dos meses publicados; média = total / 8 meses publicados pelo tribunal."), 8)
        with self.assertRaises(ValueError):  # control
            judiciary_view.months_count("Soma dos meses publicados.")

    def test_page_data_is_current(self):
        page, fresh = page_people(), fresh_records()
        self.assertEqual(stale(page, fresh), [])
        src = load(FED / "judiciary-2026.json")  # control: R$ 0,01 more in the source must make the page stale
        next(it for it in src["people"][0]["items"] if it["key"] == "salary")["year_total"] += 0.01
        self.assertEqual(stale(page, fresh_records(src)), [src["people"][0]["id"]])

    def test_stf_sums_close_by_hand(self):
        page = page_people()
        self.assertEqual(sums(page), [])
        planted = copy.deepcopy(page)  # control
        next(it for p in planted if p["id"] == "stf:flavio-dino" for it in p["items"] if it["key"] == "vacation")["monthly"] -= 0.01
        self.assertEqual(sums(planted), ["stf:flavio-dino vacation", "stf:flavio-dino total"])

    def test_states(self):
        page = page_people()
        self.assertEqual(states(page), [])
        planted = copy.deepcopy(page)  # control
        next(it for p in planted if p["id"] == "stf:gilmar-mendes" for it in p["items"] if it["key"] == "housing")["state"] = "paid"
        self.assertEqual(states(planted), ["stf:gilmar-mendes housing"])

    def test_dates(self):
        page = page_people()
        self.assertEqual(dates(page), [])
        planted = copy.deepcopy(page)  # control
        next(p for p in planted if p["id"] == "stf:edson-fachin")["office"] = None
        self.assertEqual(dates(planted), ["stf:edson-fachin office"])

    def test_other_courts_unchanged_until_their_turn(self):
        page = page_people()
        self.assertTrue(all("state" not in it for p in page if p["house"] == "judiciario" and p["court"] != "STF" for it in p["items"]))


if __name__ == "__main__":
    unittest.main()
