"""Monthly interest of the União for the platform preview's network graph (D134), read from the published ledger
(data/ledger/ledger.duckdb, phase 1): accrual (RTN, the interest that ran) and cash (DTT group 2, the interest paid),
each month in reais, with the source releases behind them (title, publisher, url, SHA-256).

Usage: .venv/bin/python docs/superpowers/tools/build-ledger-interest-asset.py
Writes docs/superpowers/previews/assets/bi-ledger-interest.js (window.BI_LEDGER_INTEREST). Stops unless every month from
the first to the last has both bases and the yearly sums equal the ledger's own sums to the cent."""
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "superpowers" / "previews" / "assets" / "bi-ledger-interest.js"


def main():
    con = duckdb.connect(str(ROOT / "data/ledger/ledger.duckdb"), read_only=True)
    rows = con.execute("""SELECT strftime(period, '%Y-%m') AS m, basis, sum(amount_cents) FROM flow
                          WHERE flow_type = 'interest' AND from_node = 'gov:uniao' AND to_node = 'fin:credores'
                          GROUP BY 1, 2 ORDER BY 1""").fetchall()
    cents = {}
    for m, basis, c in rows:
        cents.setdefault(m, {})[basis] = int(c)
    months = sorted(cents)
    y0, m0 = int(months[0][:4]), int(months[0][5:])
    expected = []
    while True:
        s = f"{y0}-{m0:02d}"; expected.append(s)
        if s == months[-1]: break
        y0, m0 = (y0 + 1, 1) if m0 == 12 else (y0, m0 + 1)
    if months != expected or any(set(cents[m]) != {"accrual", "cash"} for m in months):
        raise SystemExit("CHECK FAILED: a month is missing one of the two bases")
    for y in sorted({m[:4] for m in months}):
        for basis in ("accrual", "cash"):
            ledger = con.execute("SELECT sum(amount_cents) FROM flow WHERE flow_type = 'interest' AND basis = ? AND year(period) = ?", [basis, int(y)]).fetchone()[0]
            if sum(cents[m][basis] for m in months if m.startswith(y)) != ledger:
                raise SystemExit(f"CHECK FAILED: {basis} {y} differs from the ledger")
    sources = {}
    for basis in ("accrual", "cash"):
        sources[basis] = [dict(zip(("title", "publisher", "url", "sha256", "fetched_at"), (r[0], r[1], r[2], r[3], str(r[4])[:10]))) for r in con.execute(
            """SELECT DISTINCT s.title, s.publisher, s.url, s.sha256, s.fetched_at FROM flow f JOIN source_release s USING (source_id)
               WHERE f.flow_type = 'interest' AND f.basis = ? ORDER BY 1""", [basis]).fetchall()]
    con.close()
    data = {"months": months, "accrual": [cents[m]["accrual"] / 100 for m in months], "cash": [cents[m]["cash"] / 100 for m in months], "sources": sources}
    OUT.write_text("window.BI_LEDGER_INTEREST = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"{len(months)} months, {months[0]} to {months[-1]}; 2024 accrual R$ {sum(cents[m]['accrual'] for m in months if m.startswith('2024')) / 1e11:.2f} bi;",
          {b: len(v) for b, v in sources.items()}, "source releases; wrote", OUT.relative_to(ROOT), OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
