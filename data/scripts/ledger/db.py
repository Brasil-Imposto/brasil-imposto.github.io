"""Open the ledger warehouse (one DuckDB file) with the schema and the reference rows in place. Idempotent."""
from pathlib import Path

import duckdb

import reference

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "data" / "ledger" / "ledger.duckdb"
SCHEMA = Path(__file__).with_name("schema.sql")

FLOW_DDL = """CREATE TABLE IF NOT EXISTS flow (
  flow_id         TEXT PRIMARY KEY,             -- sha256 of dataset, source_key, period, from_node, to_node, flow_type
  period          DATE NOT NULL,
  from_node       TEXT NOT NULL REFERENCES node (node_id),
  to_node         TEXT NOT NULL REFERENCES node (node_id),
  flow_type       TEXT NOT NULL REFERENCES flow_type (flow_type_id),
  amount_cents    BIGINT NOT NULL,
  basis           TEXT NOT NULL CHECK (basis IN ('cash', 'accrual')),
  source_id       TEXT NOT NULL REFERENCES source_release (source_id),
  source_key      TEXT NOT NULL,
  location_method TEXT NOT NULL CHECK (location_method IN ('direct', 'official_split', 'estimate', 'unallocated')),
  rule_id         TEXT NOT NULL REFERENCES allocation_rule (rule_id),
  pair_id         TEXT,
  CHECK (from_node <> to_node),
  CHECK (day(period) = 1)
)"""


def connect(path=DB_PATH):
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    init(con)
    return con


def init(con):
    con.execute(SCHEMA.read_text(encoding="utf-8"))
    con.execute(FLOW_DDL)
    reference.seed(con)


def insert(con, published=(), flows=(), internal=()):
    if published:
        con.executemany("INSERT INTO published_line VALUES (?, ?, ?, ?, ?, ?, ?, ?)", list(published))
    if flows:
        con.executemany("INSERT INTO flow_stage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", list(flows))
    if internal:
        con.executemany("INSERT INTO internal_flow VALUES (?, ?, ?, ?, ?, ?, ?)", list(internal))


def fingerprint(con, table="flow"):
    """Row count, total and an order-free hash of the ids: equal fingerprints mean an unchanged table."""
    n, total, h = con.execute(f"SELECT count(*), coalesce(sum(amount_cents), 0), coalesce(bit_xor(hash(flow_id)), 0) "
                              f"FROM {table}").fetchone()
    return {"rows": int(n), "sum_cents": int(total), "id_hash": int(h)}
