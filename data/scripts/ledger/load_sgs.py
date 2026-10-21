"""Load the Banco Central's NFSP series for the Governo Central (SGS 4606, 4639 and 4573): the independent check of
RTN lines 9, 8 and 10 (interest by accrual, D121). Stored as published lines only; they are not flows.

Usage: .venv/bin/python data/scripts/ledger/load_sgs.py"""
import calendar
import html
import json
import re
import time
from datetime import date

import db
import registry
import sources
from money import from_millions, to_cents

SOAP = ('<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
        'xmlns:pub="http://publico.ws.wssgs.bcb.gov.br"><soapenv:Body><pub:getUltimoValorXML><in0>{code}</in0>'
        '</pub:getUltimoValorXML></soapenv:Body></soapenv:Envelope>')


def official_name(code):
    with registry.fetch(sources.SGS_SOAP, data=SOAP.format(code=code).encode("utf-8"), timeout=60,
                        headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": '""'}) as fx:
        names = re.findall(r"<NOME>(.*?)</NOME>", html.unescape(fx.path.read_text(encoding="utf-8", errors="replace")))
    if len(names) != 1:
        raise SystemExit(f"SGS {code}: the service did not return one name")
    return names[0].strip()


def fetch_series(url):
    """The SGS API answers an empty body now and then: up to three tries, 10 s apart."""
    for attempt in range(1, 4):
        with registry.fetch(url, timeout=120) as fx:
            raw = fx.path.read_bytes()
        try:
            items = json.loads(raw)
            if isinstance(items, list) and items:
                return fx, items
        except json.JSONDecodeError:
            pass
        time.sleep(10 * attempt)
    raise SystemExit(f"SGS: no valid answer from {url}")


def run(con):
    out = []
    last_day = calendar.monthrange(sources.LAST.year, sources.LAST.month)[1]
    for code, (key, rtn_line, name) in sources.SGS.items():
        if official_name(code) != name:
            raise SystemExit(f"SGS {code} changed its name; expected {name!r}")
        url = sources.SGS_URL.format(code=code, first=sources.FIRST.strftime("%d/%m/%Y"),
                                     last=f"{last_day:02d}/{sources.LAST:%m/%Y}")
        fx, items = fetch_series(url)
        con.begin()
        try:
            source_id, new = registry.register(
                con, f"bcb.sgs.{code}", fx, title=f"SGS {code}: {name}", publisher="Banco Central do Brasil",
                page_url="https://www3.bcb.gov.br/sgspub/", published_on=None,
                published_note="o Banco Central não publica a data de divulgação na API", loader="load_sgs.py")
            if new:
                rows = []
                for it in items:
                    d, m, y = it["data"].split("/")
                    e = from_millions(it["valor"])
                    rows.append((source_id, key, date(int(y), int(m), 1), "series", name, e, to_cents(e), 1))
                if sorted(r[2] for r in rows) != sources.months():
                    raise SystemExit(f"SGS {code}: months do not cover {sources.FIRST} to {sources.LAST}")
                db.insert(con, published=rows)
            con.commit()
        except BaseException:
            con.rollback()
            raise
        out.append({"dataset": f"bcb.sgs.{code}", "source_id": source_id, "new": new, "sha256": fx.sha256,
                    "bytes": fx.bytes})
        print("sgs", out[-1])
    return out


if __name__ == "__main__":
    run(db.connect())
