"""Build the money-flow ledger, phase 1: load every source, check the guarantees, prove the planted errors fail, and
only then publish the flows. When any step fails, nothing is published and `flow` keeps the last good build.

Usage: uv run python pipelines/ledger/build.py [--skip-load] [--control]
  --skip-load  use the releases already in the warehouse (no download)
  --control    flip the sign of one real flow before the checks. A control run never publishes: it exits 0 when the
               guarantees stopped it and 1 when they missed the flip
Writes data/ledger/build-report.json and one row in build_run."""
import json
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime

import duckdb

import db
import guarantees
import load_dtt_interest
import load_rreo_union
import load_rtn
import load_sgs
import measures
import planted
import sources

REPORT = db.ROOT / "data" / "ledger" / "build-report.json"
UNION_JSON = db.ROOT / "data" / "series" / "union.json"


def by_year(monthly):
    out = defaultdict(lambda: defaultdict(int))
    for p, row in monthly.items():
        label = str(p.year) if p.year < sources.LAST.year else f"{p.year} (jan a {sources.LAST:%m})"
        for k, v in row.items():
            out[label][k] += v
    return {y: dict(v) for y, v in out.items()}


def union_json_gap(monthly):
    """Largest gap, in cents, between the ledger and today's data/series/union.json (report only, not a guarantee)."""
    u = json.loads(UNION_JSON.read_text(encoding="utf-8"))
    pos = {m: i for i, m in enumerate(u["months"])}
    gap = {}
    for name, _code in measures.LINES:
        values = [(row[name], u[name][pos[f"{p:%Y-%m}"]]) for p, row in monthly.items() if f"{p:%Y-%m}" in pos]
        gap[name] = max(abs(a - round(b * 100)) for a, b in values if b is not None)
    return gap


def unassigned(con, table):
    nodes = "('soc:unknown', 'soc:br', 'gov:sub:br')"
    rows = con.execute(f"""SELECT year(period) AS y, CASE WHEN from_node IN {nodes} THEN from_node
        ELSE to_node END AS node, sum(amount_cents) FROM {table}
        WHERE from_node IN {nodes} OR to_node IN {nodes} GROUP BY ALL ORDER BY ALL""").fetchall()
    out = defaultdict(dict)
    for y, node, s in rows:
        out[node][str(y)] = int(s)
    return dict(out)


def main(argv):
    t0, started = time.time(), datetime.now().replace(microsecond=0)
    con = db.connect()
    before = db.fingerprint(con)
    loads = {}
    if "--skip-load" not in argv:
        loads = {"rtn": load_rtn.run(con), "sgs": load_sgs.run(con), "dtt": load_dtt_interest.run(con),
                 "rreo": load_rreo_union.run(con)}
    con.execute("CREATE OR REPLACE TEMP TABLE cand_flow AS SELECT f.* FROM flow_stage f JOIN current_release r USING (source_id)")
    control = None
    if "--control" in argv:
        control = planted.plant(con, "flipped_sign", "cand_flow", "control_flow", line=planted.CONTROL_LINE)
        con.execute("CREATE OR REPLACE TEMP TABLE cand_flow AS SELECT * FROM control_flow")
    results = guarantees.run_all(con, "cand_flow")
    plants = planted.run(con, guarantees.run_all)
    ok = all(r.ok for r in results) and all(p["caught_by"] for p in plants.values())
    publish = ok and control is None
    if publish:
        con.begin()
        try:
            con.execute("DROP TABLE flow")
            con.execute(db.FLOW_DDL)
            con.execute("INSERT INTO flow SELECT * FROM cand_flow ORDER BY period, flow_id")
            con.commit()
        except (duckdb.Error, SystemExit):
            con.rollback()
            ok = publish = False
    table = "flow" if publish else "cand_flow"
    monthly = measures.union_account(con, table)
    report = {
        "status": "published" if publish else "stopped",
        "control_outcome": None if control is None else ("caught" if not ok else "missed"),
        "started_at": started.isoformat(), "seconds": round(time.time() - t0, 1), "duckdb": duckdb.__version__,
        "period": [str(sources.FIRST), str(sources.LAST)],
        "loads": loads, "control": control,
        "releases": [dict(zip(("dataset", "source_id", "sha256", "bytes", "published_on", "published_note"), r)) for r in
                     con.execute("SELECT dataset, source_id, sha256, bytes, published_on, published_note "
                                 "FROM current_release ORDER BY dataset").fetchall()],
        "guarantees": [{"id": r.id, "label": r.label, "ok": r.ok, "failures": r.failures, "sample": r.sample, "detail": r.detail}
                       for r in results],
        "planted_errors": plants,
        "flows_by_type": dict(con.execute(f"SELECT flow_type, count(*) FROM {table} GROUP BY 1 ORDER BY 1").fetchall()),
        "flow_before": before, "flow_after": db.fingerprint(con),
        "union_account_by_year_cents": by_year(monthly),
        "unassigned_by_year_cents": unassigned(con, table),
        "gap_to_union_json_cents": union_json_gap(monthly),
    }
    con.execute("INSERT INTO build_run VALUES (?, ?, ?, ?, ?, ?)",
                [uuid.uuid4().hex, started, datetime.now().replace(microsecond=0), report["status"],
                 report["flow_after"]["rows"], json.dumps(report, default=str)])
    con.execute("CHECKPOINT")
    con.close()
    report["db_bytes"] = db.DB_PATH.stat().st_size
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    for r in results:
        print(("ok    " if r.ok else "FAIL  ") + r.label, "" if r.ok else r.sample[:2])
    for kind, p in plants.items():
        print(("caught" if p["caught_by"] else "MISSED"), kind, p["target"], "by", [n.split(" ")[0] for n in p["caught_by"]])
    print(report["status"], "| flows", report["flow_after"]["rows"], "| db", report["db_bytes"], "bytes |",
          report["seconds"], "s | report", REPORT.relative_to(db.ROOT))
    return 0 if (publish if control is None else not ok) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
