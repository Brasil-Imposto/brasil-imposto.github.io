"""The errors that must fail (spec 6, guarantee 8): each is planted in a copy of the candidate flows, every guarantee runs
on the copy, and the build stops if any planted error passes all of them. The four RTN plants touch one flow only; the two
cross-source plants are errors that only the checks against an outside source can see (G3 against the RREO, G5 against
the Banco Central): one of them also moves the printed line, so it runs inside a transaction that is rolled back."""
import sources

TARGETS = {  # planted error -> the RTN line it touches, in the latest month
    "duplicate_row": "1.1.05",   # Cofins
    "deleted_row": "2.1",        # FPM, FPE and IPI-EE
    "flipped_sign": "4.3.10",    # Fundeb, the União's complement
    "split_pair": "1.4.3",       # the servants' contribution, moved to another state than its salary
}
CONTROL_LINE = "1.1.03.3.1"     # build.py --control flips this one (IRRF on wages), apart from the planted targets
CROSS_SOURCE = ("dtt_paid_shift", "rtn_line_and_flow_shift")
SHIFT_CENTS = 2_000_000          # R$ 20 mil: twice the R$ 10 mil the Banco Central series can resolve
DTT_SHIFT_CENTS = 1_000             # R$ 10: ten times the R$ 1 the RREO allows in its whole-reais years


def plant_cross(con, kind, src, dst):
    con.execute(f"CREATE OR REPLACE TEMP TABLE {dst} AS SELECT * FROM {src}")
    if kind == "dtt_paid_shift":  # interest paid in cash, mid-year: the Tesouro base line and its flow move R$ 10 together,
        # beyond the R$ 1 the RREO allows in years it prints in whole reais, so only the RREO comparison (G3) can see it
        rows = con.execute(f"""SELECT f.flow_id, f.period, f.amount_cents, f.source_id, f.source_key FROM {dst} f JOIN current_release r USING (source_id)
            WHERE r.dataset LIKE 'tesouro.dtt.%' AND f.source_key LIKE '%|paid' ORDER BY f.period, f.flow_id""").fetchall()
        fid, period, amount, sid, key = rows[len(rows) // 2]
        con.execute(f"UPDATE {dst} SET amount_cents = amount_cents + ? WHERE flow_id = ?", [DTT_SHIFT_CENTS, fid])
        con.execute("UPDATE published_line SET value_cents = value_cents + ? * flow_sign WHERE source_id = ? AND line_key = ? AND period = ?",
                    [DTT_SHIFT_CENTS, sid, key, period])
        return {"line": key, "period": str(period), "amount_cents": int(amount), "moved_cents": DTT_SHIFT_CENTS}
    # rtn_line_and_flow_shift: a loader that misreads one cell writes the same wrong value in the line and in its flow
    rows = con.execute(f"""SELECT f.flow_id, f.period, f.amount_cents, f.source_id FROM {dst} f JOIN current_release r USING (source_id)
        WHERE r.dataset = ? AND f.source_key = '9' ORDER BY f.period""", [sources.RTN["dataset"]]).fetchall()
    fid, period, amount, sid = rows[len(rows) // 2]
    con.execute(f"UPDATE {dst} SET amount_cents = amount_cents + ? WHERE flow_id = ?", [SHIFT_CENTS, fid])
    con.execute("UPDATE published_line SET value_cents = value_cents + ? * flow_sign WHERE source_id = ? AND line_key = '9' AND period = ?",
                [SHIFT_CENTS, sid, period])
    return {"line": "9", "period": str(period), "amount_cents": int(amount), "moved_cents": SHIFT_CENTS}


def plant(con, kind, src, dst, line=None):
    line = line or TARGETS[kind]
    con.execute(f"CREATE OR REPLACE TEMP TABLE {dst} AS SELECT * FROM {src}")
    row = con.execute(f"""SELECT f.flow_id, f.period, f.amount_cents FROM {dst} f JOIN current_release r USING (source_id)
        WHERE r.dataset = ? AND f.source_key = ? ORDER BY f.period DESC LIMIT 1""",
                      [sources.RTN["dataset"], line]).fetchone()
    if row is None:
        raise SystemExit(f"planted error {kind}: line {line} has no flow")
    fid = row[0]
    if kind == "duplicate_row":
        con.execute(f"INSERT INTO {dst} SELECT * FROM {dst} WHERE flow_id = ?", [fid])
    elif kind == "deleted_row":
        con.execute(f"DELETE FROM {dst} WHERE flow_id = ?", [fid])
    elif kind == "flipped_sign":
        con.execute(f"UPDATE {dst} SET amount_cents = -amount_cents WHERE flow_id = ?", [fid])
    elif kind == "split_pair":
        con.execute(f"UPDATE {dst} SET from_node = 'soc:uf:DF' WHERE flow_id = ?", [fid])
    return {"line": line, "period": str(row[1]), "amount_cents": int(row[2])}


def run(con, check, src="cand_flow"):
    out = {}
    for kind in TARGETS:
        target = plant(con, kind, src, "planted")
        out[kind] = {"target": target, "caught_by": [r.id for r in check(con, "planted") if not r.ok]}
    con.execute("DROP TABLE IF EXISTS planted")
    for kind in CROSS_SOURCE:
        con.begin()
        try:
            target = plant_cross(con, kind, src, "planted")
            out[kind] = {"target": target, "caught_by": [r.id for r in check(con, "planted") if not r.ok]}
        finally:
            con.rollback()
    return out
