"""Load the União's RREO Anexo 1 from SICONFI: 'Juros e Encargos da Dívida', despesas pagas até o bimestre.
It is the independent total the cash interest of the DTT base must match, to the cent (guarantee 3).

Usage: uv run python pipelines/ledger/load_rreo_union.py"""
import json
import time
from datetime import date

import db
import registry
import sources
from money import exact, to_cents


def run(con):
    out = []
    for year, bim in sources.rreo_bimesters():
        dataset = f"tesouro.siconfi.rreo.uniao.anexo01.{year}.b{bim}"
        with registry.fetch(sources.RREO_URL.format(year=year, bim=bim), timeout=120) as fx:
            data = json.loads(fx.path.read_bytes())
            if data.get("hasMore"):
                raise SystemExit(f"RREO {year} b{bim}: the answer is paginated")
            hits = [i for i in data["items"]
                    if i["cod_conta"] == sources.RREO_ACCOUNT and i["coluna"].startswith(sources.RREO_PAID_COLUMN)]
            if len(hits) != 1:
                raise SystemExit(f"RREO {year} b{bim}: {len(hits)} lines for {sources.RREO_ACCOUNT}")
            e = exact(hits[0]["valor"])
            con.begin()
            try:
                source_id, new = registry.register(
                    con, dataset, fx, title=f"RREO da União, {year}, {bim}º bimestre, Anexo 1",
                    publisher="Secretaria do Tesouro Nacional (SICONFI)", page_url=sources.RREO_PAGE,
                    published_on=None, published_note="o SICONFI não informa a data de divulgação na API",
                    loader="load_rreo_union.py")
                if new:
                    db.insert(con, published=[(source_id, "rreo:interest_paid_ytd", date(year, 2 * bim, 1), "control",
                                               f"{hits[0]['conta']}, {hits[0]['coluna']}", e, to_cents(e), 1)])
                con.commit()
            except BaseException:
                con.rollback()
                raise
        out.append({"dataset": dataset, "source_id": source_id, "new": new, "sha256": fx.sha256, "bytes": fx.bytes})
        time.sleep(1)
    print("rreo", len(out), "bimesters,", sum(o["new"] for o in out), "new", flush=True)
    return out


if __name__ == "__main__":
    run(db.connect())
