"""The guarantees of spec section 6. Each check returns a Result; build.py publishes only when every one is ok and
every planted error (planted.py) is caught by at least one of them."""
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal

import measures
import rtn_map
import sources

EPS = Decimal("0.001")      # reais; the RTN's own parts close within R$ 0.00005 (measured 2026-10-08)
RREO_CHECKPOINTS = len(list(sources.rreo_bimesters()))


@dataclass
class Result:
    name: str
    failures: int = 0
    sample: list = field(default_factory=list)
    detail: dict = field(default_factory=dict)

    @property
    def ok(self):
        return self.failures == 0

    def fail(self, item):
        self.failures += 1
        if len(self.sample) < 8:
            self.sample.append(item)


def _rows(con, sql, params=()):
    return con.execute(sql, list(params)).fetchall()


def rreo_verdict(until, dtt_cents, rreo_cents, whole_reais):
    """'ok', 'known_gap' or 'fail' for one RREO checkpoint (D122): to the cent where the RREO prints cents, one printed
    unit (R$ 1) where it prints whole reais, and a recorded gap only when it is exactly the one recorded."""
    gap = dtt_cents - rreo_cents
    if until in sources.RREO_KNOWN_GAPS:
        return "known_gap" if gap == sources.RREO_KNOWN_GAPS[until] else "fail"
    return "ok" if abs(gap) <= (sources.RREO_WHOLE_REAIS_UNIT_CENTS if whole_reais else 0) else "fail"


def g1_unique_ids(con, flow):
    r = Result("G1 nenhum flow_id repetido")
    for fid, n in _rows(con, f"SELECT flow_id, count(*) FROM {flow} GROUP BY flow_id HAVING count(*) > 1"):
        r.fail({"flow_id": fid, "copies": int(n)})
    return r


def g2_complete_rows(con, flow):
    r = Result("G2 toda linha tem origem, destino diferente, tipo, fonte e método de localização")
    sql = f"""SELECT f.flow_id, f.source_key, f.period FROM {flow} f
        LEFT JOIN node a ON a.node_id = f.from_node
        LEFT JOIN node b ON b.node_id = f.to_node
        LEFT JOIN flow_type t ON t.flow_type_id = f.flow_type
        LEFT JOIN current_release s ON s.source_id = f.source_id
        LEFT JOIN allocation_rule ar ON ar.rule_id = f.rule_id
        WHERE f.flow_id IS NULL OR f.period IS NULL OR f.amount_cents IS NULL OR f.source_key IS NULL
           OR a.node_id IS NULL OR b.node_id IS NULL OR f.from_node = f.to_node
           OR t.flow_type_id IS NULL OR s.source_id IS NULL OR ar.rule_id IS NULL
           OR f.basis IS NULL OR f.basis NOT IN ('cash', 'accrual')
           OR f.location_method IS DISTINCT FROM ar.method
           OR (NOT t.allows_negative AND f.amount_cents < 0)
           OR f.amount_cents = 0 OR day(f.period) <> 1"""
    for fid, key, p in _rows(con, sql):
        r.fail({"flow_id": fid, "source_key": key, "period": str(p)})
    return r


def g3_release_totals(con, flow):
    r = Result("G3 cada divulgação fecha com o total que ela mesma publica")
    ds = sources.RTN["dataset"]
    printed = {(k, p): e for k, p, e in _rows(con, "SELECT line_key, period, value_reais FROM cur_line WHERE dataset = ? "
                                                  "AND kind IN ('leaf', 'total', 'adjustment')", [ds])}
    worst = Decimal(0)
    for total in sorted(rtn_map.PARTITIONS):
        parts = [c for c in rtn_map.ALL_CODES if rtn_map.parent(c) == total]
        for p in sources.months():
            d = abs(sum(printed[(c, p)] for c in parts) - printed[(total, p)])
            worst = max(worst, d)
            if d > EPS:
                r.fail({"rtn_line": total, "period": str(p), "parts_minus_total_reais": str(d)})
    r.detail["rtn_parts_vs_totals_worst_reais"] = str(worst)
    led, worst_c = measures.RtnLedger(con, flow), 0
    for code in ("1", "2", "4"):
        for p in sources.months():
            v, n = led.line(code, p)
            d = abs(v - led.pub[(code, p)][0])
            worst_c = max(worst_c, d)
            if d > (n + 1) // 2:
                r.fail({"rtn_line": code, "period": str(p), "ledger_cents": v, "printed_cents": led.pub[(code, p)][0]})
    r.detail["rtn_lines_1_2_4_worst_cents"] = worst_c
    paid = defaultdict(int)
    for p, c in _rows(con, f"""SELECT f.period, sum(f.amount_cents) FROM {flow} f JOIN current_release s USING (source_id)
            WHERE s.dataset LIKE 'tesouro.dtt.%' AND f.source_key LIKE '%|paid' GROUP BY 1"""):
        paid[p] += int(c)
    for p, c in _rows(con, """SELECT period, sum(amount_cents) FROM cur_internal WHERE dataset LIKE 'tesouro.dtt.%'
            AND source_key LIKE '%|paid' AND to_part <> 'intra' GROUP BY 1"""):
        paid[p] += int(c)
    rreo = _rows(con, "SELECT period, value_cents FROM cur_line WHERE kind = 'control' AND line_key = 'rreo:interest_paid_ytd'")
    whole = defaultdict(lambda: True)        # a year prints whole reais when every checkpoint of it ends in ,00
    for until, c in rreo:
        whole[until.year] = whole[until.year] and int(c) % 100 == 0
    known, worst_r = {}, 0
    for until, c in rreo:
        ytd = sum(v for p, v in paid.items() if p.year == until.year and p <= until)
        verdict = rreo_verdict(until, ytd, int(c), whole[until.year])
        if verdict == "fail":
            r.fail({"rreo_until": str(until), "dtt_cents": ytd, "rreo_cents": int(c), "gap_cents": ytd - int(c)})
        elif verdict == "known_gap":
            known[str(until)] = ytd - int(c)
        else:
            worst_r = max(worst_r, abs(ytd - int(c)))
    r.detail["rreo_checkpoints"] = len(rreo)
    r.detail["rreo_whole_reais_years"] = sorted(y for y, w in whole.items() if w)
    r.detail["rreo_worst_gap_cents_outside_known"] = worst_r
    r.detail["rreo_known_gaps_cents"] = known
    if len(rreo) != RREO_CHECKPOINTS:
        r.fail({"rreo_checkpoints": len(rreo), "expected": RREO_CHECKPOINTS})
    return r


def g4_lines_conserved(con, flow):
    r = Result("G4 as partes de cada linha oficial somam a linha, ao centavo (estados, União e sem informação de estado dão o total)")
    sql = f"""WITH f AS (SELECT source_id, source_key, period, sum(amount_cents) AS s FROM {flow} GROUP BY ALL),
        i AS (SELECT source_id, source_key, period, sum(amount_cents) AS s FROM cur_internal GROUP BY ALL),
        l AS (SELECT source_id, line_key, period, value_cents * flow_sign AS v FROM cur_line WHERE kind IN ('leaf', 'derived'))
        SELECT l.source_id, l.line_key, l.period, l.v, f.s, i.s FROM l
        LEFT JOIN f ON f.source_id = l.source_id AND f.source_key = l.line_key AND f.period = l.period
        LEFT JOIN i ON i.source_id = l.source_id AND i.source_key = l.line_key AND i.period = l.period
        WHERE coalesce(f.s, 0) + coalesce(i.s, 0) <> coalesce(l.v, 0)"""
    for sid, key, p, v, fs, ins in _rows(con, sql):
        r.fail({"source_id": sid, "line": key, "period": str(p), "printed_cents": v, "flow_cents": fs, "internal_cents": ins})
    orphan = f"""SELECT f.source_id, f.source_key, f.period FROM {flow} f
        LEFT JOIN cur_line l ON l.source_id = f.source_id AND l.line_key = f.source_key AND l.period = f.period
             AND l.kind IN ('leaf', 'derived')
        WHERE l.line_key IS NULL"""
    for sid, key, p in _rows(con, orphan):
        r.fail({"flow_without_official_line": key, "source_id": sid, "period": str(p)})
    r.detail["lines_checked"] = _rows(con, "SELECT count(*) FROM cur_line WHERE kind IN ('leaf', 'derived')")[0][0]
    return r


def g5_union_matches_rtn_and_bcb(con, flow):
    r = Result("G5 o nó gov:uniao bate com o RTN e com o Banco Central, linha por linha")
    led, worst, checked = measures.RtnLedger(con, flow), defaultdict(int), 0
    for (code, p), (cents, _sign, kind) in sorted(led.pub.items(), key=lambda x: (x[0][1], x[0][0])):
        if kind == "adjustment" or cents is None or (kind == "memo" and code not in rtn_map.MEMO_CHECKS):
            continue
        if kind == "memo":
            parts = [led.line(c, p) for c in rtn_map.MEMO_CHECKS[code]]
            v, n = sum(x[0] for x in parts), sum(x[1] for x in parts)
        else:
            v, n = led.line(code, p)
        tolerance = 0 if kind in ("leaf", "derived") else (n + 1) // 2
        d = abs(v - cents)
        worst[kind] = max(worst[kind], d)
        checked += 1
        if d > tolerance:
            r.fail({"rtn_line": code, "period": str(p), "ledger_cents": v, "printed_cents": cents, "tolerance": tolerance})
    r.detail["rtn_lines_checked"] = checked
    r.detail["rtn_worst_cents_by_kind"] = dict(worst)
    if sorted(p for (k, p) in led.pub if k == "1") != sources.months():
        r.fail({"coverage": "RTN"})
    series = {(k, p): int(c) for k, p, c in _rows(con, "SELECT line_key, period, value_cents FROM cur_line WHERE kind = 'series'")}
    for code, (key, rtn_line, _name) in sources.SGS.items():
        months = sorted(p for (k, p) in series if k == key)
        if months != sources.months():
            r.fail({"coverage": key})
            continue
        w = 0
        for p in months:
            v, _ = led.line(rtn_line, p)
            d = abs(v + series[(key, p)])            # the SGS prints a need for financing: the RTN sign flipped
            w = max(w, d)
            if d > sources.SGS_UNIT_CENTS:
                r.fail({"sgs": code, "period": str(p), "ledger_cents": v, "sgs_cents": series[(key, p)]})
        r.detail[f"bcb_sgs_{code}_worst_cents"] = w
    return r


def g6_pairs_same_state(con, flow):
    r = Result("G6 todo par salário e imposto retido mora no mesmo estado")
    sql = f"""WITH p AS (
          SELECT f.pair_id, f.flow_type, coalesce(CASE WHEN a.is_government THEN b.uf ELSE a.uf END, 'BR') AS uf
          FROM {flow} f JOIN node a ON a.node_id = f.from_node JOIN node b ON b.node_id = f.to_node
          WHERE f.pair_id IS NOT NULL)
        SELECT pair_id, count(DISTINCT uf),
               count(*) FILTER (WHERE flow_type = 'public_payroll_gross'),
               count(*) FILTER (WHERE flow_type = 'public_payroll_withholding')
        FROM p GROUP BY pair_id
        HAVING count(DISTINCT uf) <> 1
            OR count(*) FILTER (WHERE flow_type = 'public_payroll_gross') = 0
            OR count(*) FILTER (WHERE flow_type = 'public_payroll_withholding') = 0"""
    for pid, n_uf, n_g, n_w in _rows(con, sql):
        r.fail({"pair_id": pid, "states": int(n_uf), "gross": int(n_g), "withheld": int(n_w)})
    for fid, key in _rows(con, f"SELECT flow_id, source_key FROM {flow} WHERE flow_type = 'public_payroll_withholding' "
                               f"AND pair_id IS NULL"):
        r.fail({"withholding_without_pair": key, "flow_id": fid})
    r.detail["pairs"] = _rows(con, f"SELECT count(DISTINCT pair_id) FROM {flow} WHERE pair_id IS NOT NULL")[0][0]
    return r


def g7_no_transfer_in_spending(con, flow):
    r = Result("G7 fluxo entre governos nunca entra numa medida de gasto")
    both = f"""SELECT f.flow_id, f.source_key, t.nature FROM {flow} f
        JOIN node a ON a.node_id = f.from_node JOIN node b ON b.node_id = f.to_node
        JOIN flow_type t ON t.flow_type_id = f.flow_type
        WHERE (a.is_government AND b.is_government) <> (t.nature = 'intergovernmental')"""
    for fid, key, nature in _rows(con, both):
        r.fail({"flow_id": fid, "source_key": key, "nature": nature,
                "why": "entre dois governos tem de ser repasse, e repasse só existe entre governos"})
    spend = f"""SELECT s.flow_id, s.source_key FROM ({measures.SPENDING_SQL.format(flow=flow)}) s
        JOIN flow_type t ON t.flow_type_id = s.flow_type JOIN node b ON b.node_id = s.to_node
        WHERE t.nature = 'intergovernmental' OR b.is_government"""
    for fid, key in _rows(con, spend):
        r.fail({"flow_id": fid, "source_key": key, "why": "repasse dentro da medida de gasto"})
    mixed = f"""SELECT s.dataset FROM {flow} f JOIN current_release s USING (source_id)
        WHERE f.flow_type = 'interest' GROUP BY 1 HAVING count(DISTINCT f.basis) > 1"""
    for (ds,) in _rows(con, mixed):
        r.fail({"dataset": ds, "why": "juros por competência e por caixa vindos da mesma fonte"})
    return r


ALL = (g1_unique_ids, g2_complete_rows, g3_release_totals, g4_lines_conserved, g5_union_matches_rtn_and_bcb,
       g6_pairs_same_state, g7_no_transfer_in_spending)


def run_all(con, flow):
    return [g(con, flow) for g in ALL]
