"""Load the RTN Tabela 1.2 (Governo Central, monthly, R$ milhões) into the ledger: every printed line as a
published_line, the money lines as flows (rtn_map.py), the União's payments to itself as internal_flow.

Usage: uv run python pipelines/ledger/load_rtn.py
The file is read once from the Tesouro, hashed while it streams and deleted at the end (registry.fetch)."""
import hashlib
import re
from datetime import date

import openpyxl

import db
import reference
import registry
import rtn_map
import sources
from money import from_millions, to_cents

CODE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s")


def flow_id(dataset, key, period, from_node, to_node, flow_type):
    raw = "|".join([dataset, key, period.isoformat(), from_node, to_node, flow_type])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def read_table(path):
    """{code: (label, {period: number})} and {memo key: (label, {period: number or text})} for FIRST..LAST."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb[sources.RTN["sheet"]].iter_rows(values_only=True))
    wb.close()
    title, unit = str(rows[1][0]), str(rows[2][0])
    if not (title.startswith("Tabela 1.2.") and "R$ Milhões" in unit and "Correntes" in unit):
        raise SystemExit(f"RTN Tabela 1.2 layout changed: {title!r} / {unit!r}")
    cols = {}
    for j, d in enumerate(rows[4]):
        if hasattr(d, "year") and sources.FIRST <= date(d.year, d.month, 1) <= sources.LAST:
            cols[date(d.year, d.month, 1)] = j
    if sorted(cols) != sources.months():
        raise SystemExit(f"RTN months do not cover {sources.FIRST} to {sources.LAST}")
    lines, memo, section = {}, {}, "lines"
    for r in rows[5:]:
        label = str(r[0]).strip() if r[0] is not None else ""
        if not label:
            continue
        if label == "Memorando":
            section = "memo"
            continue
        if label.startswith("Obs."):
            break
        values = {p: r[j] for p, j in cols.items()}
        if section == "memo":
            memo["memo:" + label] = (label, values)
            continue
        m = CODE.match(label)
        if not m or m.group(1) in lines:
            raise SystemExit(f"RTN line without a code, or a code twice: {label!r}")
        bad = [p for p, v in values.items() if not isinstance(v, (int, float))]
        if bad:
            raise SystemExit(f"RTN {m.group(1)}: not a number in {bad[0]}")
        lines[m.group(1)] = (label, values)
    return lines, memo


def build_rows(lines, memo, source_id, dataset):
    if set(lines) != rtn_map.ALL_CODES:
        raise SystemExit(f"RTN codes changed: new {sorted(set(lines) - rtn_map.ALL_CODES)}, "
                         f"gone {sorted(rtn_map.ALL_CODES - set(lines))}; place them in rtn_map.py first")
    published, flows, internal, ex = [], [], [], {}
    for code, (label, values) in lines.items():
        sign = -1 if code in rtn_map.INTEREST else 1
        for p, v in values.items():
            e = ex[(code, p)] = from_millions(v)
            published.append((source_id, code, p, rtn_map.kind_of(code), label, e, to_cents(e), sign))
    for key, (label, values) in memo.items():
        for p, v in values.items():
            e = from_millions(v) if isinstance(v, (int, float)) else None
            if e is not None:
                ex[(key, p)] = e
            published.append((source_id, key, p, "memo", label, e, None if e is None else to_cents(e), 1))
    labels = {**{c: lb for c, (lb, _) in lines.items()}, **{k: lb for k, (lb, _) in memo.items()}}
    for key, (whole, part) in rtn_map.DERIVED.items():
        label = f"{labels[whole]}, exceto: {labels[part]}"
        for p in sources.months():
            e = ex[(key, p)] = ex[(whole, p)] - ex[(part, p)]
            published.append((source_id, key, p, "derived", label, e, to_cents(e), 1))
    for key, (flow_type, frm, to, rule) in {**rtn_map.LEAVES, **rtn_map.REST, **rtn_map.INTEREST}.items():
        basis, sign = ("accrual", -1) if key in rtn_map.INTEREST else ("cash", 1)
        for p in sources.months():
            cents = sign * to_cents(ex[(key, p)])
            if cents:
                pair = f"payroll:{p:%Y-%m}" if key in rtn_map.PAIR else None
                flows.append((flow_id(dataset, key, p, frm, to, flow_type), p, frm, to, flow_type, cents, basis,
                              source_id, key, reference.METHOD[rule], rule, pair))
    for key, (from_part, to_part, also_in) in rtn_map.INTERNAL.items():
        for p in sources.months():
            cents = to_cents(ex[(key, p)])
            if cents:
                internal.append((source_id, key, also_in, p, from_part, to_part, cents))
    return published, flows, internal


def run(con):
    s = sources.RTN
    with registry.fetch(s["url"], suffix=".xlsx") as fx:
        con.begin()
        try:
            source_id, new = registry.register(con, s["dataset"], fx, title=s["title"], publisher=s["publisher"],
                                               page_url=s["page_url"], published_on=s["published_on"],
                                               published_note=s["published_note"], loader="load_rtn.py")
            if new:
                db.insert(con, *build_rows(*read_table(fx.path), source_id, s["dataset"]))
            con.commit()
        except BaseException:
            con.rollback()
            raise
    out = {"dataset": s["dataset"], "source_id": source_id, "new": new, "sha256": fx.sha256, "bytes": fx.bytes}
    print("rtn", out)
    return out


if __name__ == "__main__":
    run(db.connect())
