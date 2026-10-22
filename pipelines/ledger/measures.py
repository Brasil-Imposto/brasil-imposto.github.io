"""Measures: every number on screen is a sum over the ledger (spec section 5). Phase 1 has the União account: the RTN
lines rebuilt from the flows, plus the interest paid in cash. Interest by accrual and by cash are never added up."""
from collections import defaultdict

import rtn_map
import sources

SPENDING_SQL = """SELECT f.* FROM {flow} f JOIN flow_type t ON t.flow_type_id = f.flow_type
JOIN node a ON a.node_id = f.from_node JOIN node b ON b.node_id = f.to_node
WHERE a.is_government AND NOT b.is_government AND t.nature = 'primary'"""

LINES = (("revenue", "1"), ("transfers_to_subnationals", "2"), ("revenue_net", "3"), ("primary_spending", "4"),
         ("primary_result", "5"), ("primary_result_below_line", "8"), ("nominal_interest", "9"), ("nominal_result", "10"))


class RtnLedger:
    """The RTN Tabela 1.2 rebuilt from the ledger. line(code, period) -> (cents, number of rounded terms)."""

    def __init__(self, con, flow):
        ds = sources.RTN["dataset"]
        self.by_period = defaultdict(list)
        for key, p, s, n in con.execute(f"""SELECT f.source_key, f.period, sum(f.amount_cents), count(*)
                FROM {flow} f JOIN current_release r USING (source_id) WHERE r.dataset = ? GROUP BY ALL""", [ds]).fetchall():
            self.by_period[p].append((key, None, int(s), int(n)))
        for key, also, p, c in con.execute("SELECT source_key, also_in_key, period, amount_cents FROM cur_internal "
                                           "WHERE dataset = ?", [ds]).fetchall():
            self.by_period[p].append((key, also, int(c), 1))
        self.pub = {(k, p): (c, sign, kind) for k, p, c, sign, kind in con.execute(
            "SELECT line_key, period, value_cents, flow_sign, kind FROM cur_line WHERE dataset = ?", [ds]).fetchall()}

    def line(self, code, p):
        if code in rtn_map.RESULTS:
            total = n = 0
            for part, sign in rtn_map.RESULTS[code]:
                if part in rtn_map.ADJUSTMENTS:
                    total, n = total + sign * self.pub[(part, p)][0], n + 1
                else:
                    v, k = self.line(part, p)
                    total, n = total + sign * v, n + k
            return total, n
        total = n = 0
        for key, also, cents, k in self.by_period.get(p, ()):
            if rtn_map.under(key, code) or (also is not None and rtn_map.under(also, code)):
                total, n = total + cents, n + k
        return (-total if code in rtn_map.INTEREST else total), n


def union_account(con, flow):
    """{period: {line name: cents}} with the RTN's signs, plus interest_paid_cash (DTT, positive = paid)."""
    led = RtnLedger(con, flow)
    cash = dict(con.execute(f"""SELECT f.period, sum(f.amount_cents) FROM {flow} f JOIN current_release r USING (source_id)
        WHERE f.flow_type = 'interest' AND f.basis = 'cash' GROUP BY 1""").fetchall())
    out = {}
    for p in sources.months():
        out[p] = {name: led.line(code, p)[0] for name, code in LINES}
        out[p]["interest_paid_cash"] = int(cash.get(p, 0))
    return out
