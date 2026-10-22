-- Money-flow ledger, phase 1 (spec: docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_money-flow-ledger_2026-10-08.md).
-- Reference, release and line tables are insert-only: a row never changes in place. A changed meaning gets a new id,
-- and a new release of a source is a new row that supersedes the old one (release_supersede).

CREATE TABLE IF NOT EXISTS node (
  node_id       TEXT PRIMARY KEY,
  kind          TEXT NOT NULL CHECK (kind IN ('gov_union', 'gov_state', 'gov_municipal', 'gov_subnational_unassigned',
                                              'society_state', 'society_national', 'society_unknown', 'creditors', 'world')),
  uf            TEXT CHECK (uf IS NULL OR length(uf) = 2),
  is_government BOOLEAN NOT NULL,
  label_pt      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flow_type (
  flow_type_id    TEXT PRIMARY KEY,
  nature          TEXT NOT NULL CHECK (nature IN ('primary', 'intergovernmental', 'circular', 'financial', 'external')),
  allows_negative BOOLEAN NOT NULL,
  label_pt        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS allocation_rule (
  rule_id        TEXT PRIMARY KEY,
  version        INTEGER NOT NULL,
  method         TEXT NOT NULL CHECK (method IN ('direct', 'official_split', 'estimate', 'unallocated')),
  description_pt TEXT NOT NULL,
  evidence       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_release (
  source_id      TEXT PRIMARY KEY,            -- <dataset>@<first 12 hex characters of the sha256>
  dataset        TEXT NOT NULL,
  title          TEXT NOT NULL,
  publisher      TEXT NOT NULL,
  url            TEXT NOT NULL,
  page_url       TEXT,
  published_on   DATE,
  published_note TEXT,                        -- what published_on is, or why it is empty
  sha256         TEXT NOT NULL CHECK (length(sha256) = 64),
  bytes          BIGINT NOT NULL,
  fetched_at     TIMESTAMP NOT NULL,
  loader         TEXT NOT NULL,
  UNIQUE (dataset, sha256)
);

CREATE TABLE IF NOT EXISTS release_supersede (
  old_source_id TEXT PRIMARY KEY REFERENCES source_release (source_id),
  new_source_id TEXT NOT NULL REFERENCES source_release (source_id),
  superseded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS published_line (     -- every number a release prints, as printed
  source_id   TEXT NOT NULL REFERENCES source_release (source_id),
  line_key    TEXT NOT NULL,
  period      DATE NOT NULL,
  kind        TEXT NOT NULL CHECK (kind IN ('leaf', 'derived', 'total', 'result', 'adjustment', 'memo', 'series', 'control')),
  label       TEXT NOT NULL,
  value_reais DECIMAL(38, 8),                 -- exact; NULL when the source prints text such as "Não Disp"
  value_cents BIGINT,
  flow_sign   SMALLINT NOT NULL CHECK (flow_sign IN (1, -1)),  -- flows under this line carry value * flow_sign
  PRIMARY KEY (source_id, line_key, period)
);

CREATE TABLE IF NOT EXISTS internal_flow (      -- money the União pays itself: kept for the reconciliation, never a flow
  source_id    TEXT NOT NULL REFERENCES source_release (source_id),
  source_key   TEXT NOT NULL,
  also_in_key  TEXT,                          -- the other RTN line where the same money is printed
  period       DATE NOT NULL,
  from_part    TEXT NOT NULL,
  to_part      TEXT NOT NULL,
  amount_cents BIGINT NOT NULL,
  PRIMARY KEY (source_id, source_key, period)
);

CREATE TABLE IF NOT EXISTS flow_stage (         -- what each release says, before the guarantees; no constraints on purpose
  flow_id TEXT, period DATE, from_node TEXT, to_node TEXT, flow_type TEXT, amount_cents BIGINT, basis TEXT,
  source_id TEXT, source_key TEXT, location_method TEXT, rule_id TEXT, pair_id TEXT
);

CREATE TABLE IF NOT EXISTS build_run (
  run_id      TEXT PRIMARY KEY,
  started_at  TIMESTAMP NOT NULL,
  finished_at TIMESTAMP NOT NULL,
  status      TEXT NOT NULL CHECK (status IN ('published', 'stopped')),
  flow_rows   BIGINT NOT NULL,
  report_json TEXT NOT NULL
);

CREATE OR REPLACE VIEW current_release AS
  SELECT r.* FROM source_release r
  WHERE NOT EXISTS (SELECT 1 FROM release_supersede s WHERE s.old_source_id = r.source_id);

CREATE OR REPLACE VIEW cur_line AS
  SELECT l.*, r.dataset FROM published_line l JOIN current_release r USING (source_id);

CREATE OR REPLACE VIEW cur_internal AS
  SELECT i.*, r.dataset FROM internal_flow i JOIN current_release r USING (source_id);
