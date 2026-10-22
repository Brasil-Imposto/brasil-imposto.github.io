"""The Judiciary's records on "Os 3 Poderes", as the approved spec reads them (BRASIL-IMPOSTO_SPEC_judiciario-dados_2026-10-22,
D154). Used by build-tres-poderes-r3-data.py (the whole page's data) and by build-tres-poderes-r3-judiciary.py (only the
Judiciary's part, from files in git).

What the repository's data already allows, for every court (the STF first, the others next, Q79):
  - money in decimal, rounded to the cent half up (Q73): each monthly figure is the 2026 total over the months published;
  - each item says its state: "paid", or "zero_payroll" when the published payroll column is zero for 2026 (Q74; never
    "não recebe", which needs an act or a page that says so);
  - the TSE's items form their own block, with their own months (Q76);
  - "court_since" (admission to the court) and "office" (the post inside the court, with its own date and source) replace
    "since", which mixed the two;
  - the total says it is an average, over which months, and that it adds two averages when the TSE pays too (Q72, Q76).
"""
import re
from decimal import ROUND_HALF_UP, Decimal

NOT_OWN = {"per_diem", "tse_per_diem"}  # per diems pay expenses of the office, not the person
OFFICE_OF = {"presidente-stf": "Presidente do STF"}  # positions-2026.json: the post, as the page's tree names it


def average(year_total, months):
    """The monthly average in reais, computed in decimal and rounded half up (15.455,40 / 8 = 1.931,93)."""
    return float((Decimal(str(year_total)) / months).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def months_count(note):
    """The months the court published, as the collector wrote them in the item's note."""
    m = re.search(r"média = total / (\d+) meses", note or "")
    if not m:
        raise ValueError(f"note without the month count: {note!r}")
    return int(m.group(1))


MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def months_label(label):
    """The collector's list of months, shorter and in the same words: "jan, mar, abr, mai, jun, jul, ago 2026" reads
    "jan e mar a ago 2026"; a run of three or more months becomes "x a y"."""
    m = re.fullmatch(r"((?:[a-z]{3}(?:, | a )?)+) (\d{4})", label or "")
    if not m or " a " in m.group(1):
        return label
    ms = sorted(MONTHS.index(x) for x in m.group(1).split(", "))
    runs, start = [], ms[0]
    for a, b in zip(ms, ms[1:] + [None]):
        if b != a + 1:
            runs += [f"{MONTHS[start]} a {MONTHS[a]}"] if a - start >= 2 else [MONTHS[i] for i in range(start, a + 1)]
            start = b
    return (", ".join(runs[:-1]) + " e " + runs[-1] if len(runs) > 1 else runs[0]) + " " + m.group(2)


def offices(positions):
    """Holders of a post inside a court, by name: the post's label, since when, and the official source of the date."""
    out = {}
    for pos in positions:
        for h in pos.get("people", []) if pos["id"] in OFFICE_OF else []:
            if h.get("since") and h.get("source"):
                out[h["name"]] = {"label": OFFICE_OF[pos["id"]], "since": h["since"], "source": h["source"]}
    return out


def record(x, office_by_name=None, apply=True):
    """One judge's record for the page. apply=False gives the record as it was before D154, byte for byte (the proof)."""
    items = [dict(it, own=it["key"] not in NOT_OWN) for it in x["items"]]
    rec = {"id": x["id"], "house": "judiciario", "court": x.get("court"), "ministry": x.get("ministry"), "position": x["position"],
           "name": x["name"], "role": x.get("role"), "tse_role": x.get("tse_role"), "party": x.get("party"), "uf": None,
           "since": x.get("since"), "photo": x.get("photo"), "photo_credit": x.get("photo_credit"), "page": x.get("page"),
           "data_as_of": x.get("data_as_of"), "note": x.get("note"), "items": items}
    if not apply or not items:
        return rec
    court, tse = [], []
    for it in items:
        n = months_count(it["note"])
        it["monthly"] = average(it["year_total"], n)
        it["months_count"] = n
        it["state"] = "paid" if it["year_total"] else "zero_payroll"
        if it["key"].startswith("tse_"):
            it["block"] = "tse"
            it["months"] = months_label(it["months"])
            tse.append(it)
        else:
            court.append(it)
    if any(it["state"] == "zero_payroll" for it in tse):
        raise ValueError(f"{x['name']}: a TSE item with no value; the collector keeps only the TSE items paid")
    sal = next((it for it in court if it["key"] == "salary"), court[0])
    for it in court:
        it["months"] = months_label(it["months"])
    rec.pop("since")
    rec["court_since"] = x.get("since")
    rec["office"] = (office_by_name or {}).get(x["name"])
    rec["total_label"] = "Média por mês"
    c = x["court"]
    own = f"{sal['months']}, {sal['months_count']} meses"
    if tse:
        t = tse[0]
        if not (all(i["months"] == t["months"] for i in tse)):
            raise SystemExit(x["name"])
        rec["total_note"] = f"soma da média do {c} ({own}) com a do TSE ({t['months']}, {t['months_count']} meses)"
        rec["tse_months"] = f"{t['months']}, {t['months_count']} meses"
    else:
        who = "o STF publicou" if c == "STF" else f"o {c} enviou ao painel do CNJ"
        rec["total_note"] = f"{sal['months']}, os {sal['months_count']} meses que {who}"
    return rec
