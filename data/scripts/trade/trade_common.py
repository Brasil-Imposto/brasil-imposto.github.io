"""Shared helpers for the trade datasets (data/scripts/trade/).

comexstat(body): one POST to the official Comex Stat API (MDIC/Secex, https://api-comexstat.mdic.gov.br/docs). The API answers
429 to rapid calls ("tente novamente em 10 segundos"), so a call waits and retries. If the environment variable BI_TRADE_CACHE
names a folder, responses are kept there (gzip JSON, a few hundred KB each) so a rerun does not query again; without it nothing
is written to disk.
sgs(series, start, end): a Banco Central SGS series (https://api.bcb.gov.br/dados/serie/bcdata.sgs.<n>/dados).
ptax_daily(start, end): the daily closing PTAX from the Banco Central PTAX service (olinda.bcb.gov.br), used to prove that SGS
3698 is the monthly average of the PTAX sale rate.
"""
import gzip, hashlib, json, os, subprocess, time
from decimal import Decimal
from pathlib import Path

API = "https://api-comexstat.mdic.gov.br"
ROOT = Path(__file__).resolve().parents[3]
DASHES = (chr(0x2013), chr(0x2014))
_last = [0.0]


def fetch_bytes(url, data=None, timeout=300):
    """curl, as the other data scripts do: some government hosts send an incomplete certificate chain that Python's ssl rejects
    and curl (system trust store) accepts, with verification on."""
    cmd = ["curl", "-sS", "-g", "-L", "-m", str(timeout), "-A", "brasil-imposto-data/1.0"]
    if data is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data-binary", "@-"]
    r = subprocess.run(cmd + [url], input=data, capture_output=True)
    if r.returncode:
        raise RuntimeError(f"curl failed ({r.returncode}) for {url}: {r.stderr[:200]!r}")
    return r.stdout


def _get(url, data=None, timeout=300):
    raw = fetch_bytes(url, data, timeout)
    try:
        return json.loads(raw)
    except ValueError:
        return {"error": {"code": 0, "message": raw[:200].decode("utf-8", "replace")}}


def _cached(key, fetch):
    folder = os.environ.get("BI_TRADE_CACHE")
    if not folder:
        return fetch()
    p = Path(folder) / (hashlib.sha1(key.encode()).hexdigest() + ".json.gz")
    if p.exists():
        return json.load(gzip.open(p, "rt", encoding="utf-8"))
    v = fetch()
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(p, "wt", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False)
    return v


def comexstat(body, path="/general"):
    key = path + json.dumps(body, sort_keys=True)

    def fetch():
        for _ in range(12):
            wait = 1.5 - (time.time() - _last[0])
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()
            d = _get(f"{API}{path}?language=pt", json.dumps(body).encode())
            if (d.get("error") or {}).get("code") == 429:
                time.sleep(11)
                continue
            if not d.get("success"):
                raise RuntimeError(f"Comex Stat error for {body}: {str(d)[:300]}")
            return d["data"]["list"]
        raise RuntimeError("Comex Stat kept answering 429")
    return _cached(key, fetch)


def comexstat_get(path):
    def fetch():
        for _ in range(12):
            wait = 1.5 - (time.time() - _last[0])
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()
            d = _get(f"{API}{path}")
            if (d.get("error") or {}).get("code") == 429:
                time.sleep(11)
                continue
            return d["data"]
        raise RuntimeError("Comex Stat kept answering 429")
    return _cached("GET" + path, fetch)


def latest_month():
    d = comexstat_get("/general/dates/updated")
    return int(d["year"]), int(d["monthNumber"]), d["updated"]


def months(y0, m0, y1, m1):
    out, y, m = [], y0, m0
    while (y, m) <= (y1, m1):
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def sgs(series, start, end):
    """start/end as dd/mm/yyyy; returns {YYYY-MM: Decimal} for monthly series, {YYYY-MM-DD: Decimal} for daily ones."""
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series}/dados?formato=json&dataInicial={start}&dataFinal={end}"
    rows = _cached(url, lambda: _get(url))
    out = {}
    for r in rows:
        d, m, y = r["data"].split("/")
        out[f"{y}-{m}-{d}"] = Decimal(r["valor"])
    return out


def ptax_daily(start_mmddyyyy, end_mmddyyyy):
    url = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,"
           f"dataFinalCotacao=@dataFinalCotacao)?@dataInicial='{start_mmddyyyy}'&@dataFinalCotacao='{end_mmddyyyy}'&$format=json")
    return _cached(url, lambda: _get(url))["value"]


def ptax_monthly(month_list):
    """SGS 3698 (dólar, venda, média mensal) for the given YYYY-MM months, each proved equal (4 decimals) to the mean of the daily
    closing PTAX sale rate from the PTAX service. Returns ({YYYY-MM: Decimal}, list of failures)."""
    y0, m0 = month_list[0].split("-"); y1, m1 = month_list[-1].split("-")
    s = sgs(3698, f"01/{m0}/{y0}", f"28/{m1}/{y1}")
    rates, fails = {}, []
    for ym in month_list:
        k = f"{ym}-01"
        if k not in s:
            fails.append(f"SGS 3698 has no value for {ym}")
            continue
        rates[ym] = s[k]
    daily = ptax_daily(f"{m0}-01-{y0}", _month_end(y1, m1))
    # The PTAX service can return the same day twice (2025-04-23 comes back twice); one quote per day.
    day = {}
    for r in daily:
        day.setdefault(r["dataHoraCotacao"][:10], Decimal(str(r["cotacaoVenda"])))
    by = {}
    for d, v in day.items():
        by.setdefault(d[:7], []).append(v)
    for ym, v in rates.items():
        if ym not in by:
            fails.append(f"no daily PTAX for {ym}")
            continue
        mean = (sum(by[ym]) / len(by[ym])).quantize(Decimal("0.0001"))
        if abs(mean - v) > Decimal("0.0001"):
            fails.append(f"{ym}: SGS 3698 {v} != mean of daily PTAX {mean}")
    return rates, fails


def _month_end(y, m):
    import calendar
    return f"{m}-{calendar.monthrange(int(y), int(m))[1]}-{y}"


def no_dash(s):
    if s is None:
        return s
    for d in DASHES:
        s = s.replace(d, "-")
    return s


def dash_count(text):
    return sum(text.count(d) for d in DASHES)


def write_json(path, obj):
    txt = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    if dash_count(txt):
        raise SystemExit(f"refusing to write {path}: {dash_count(txt)} dash characters in the output")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(txt, encoding="utf-8")
    return len(txt.encode())


def read_xlsx(raw, sheet):
    """Rows of one sheet of an .xlsx file (bytes), as lists of cell values (str or float); no third-party package needed."""
    import io, re, zipfile
    import xml.etree.ElementTree as ET
    m = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    r_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    z = zipfile.ZipFile(io.BytesIO(raw))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(m + "si"):
            shared.append("".join(t.text or "" for t in si.iter(m + "t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rid = next(s.get(r_ns + "id") for s in wb.iter(m + "sheet") if s.get("name") == sheet)
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = next(r.get("Target") for r in rels if r.get("Id") == rid).lstrip("/")
    target = target if target.startswith("xl/") else "xl/" + target
    rows = []
    for row in ET.fromstring(z.read(target)).iter(m + "row"):
        cells = {}
        for c in row.iter(m + "c"):
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            idx = 0
            for ch in col:
                idx = idx * 26 + ord(ch) - 64
            v = c.find(m + "v")
            if c.get("t") == "s" and v is not None:
                val = shared[int(v.text)]
            elif c.get("t") == "inlineStr":
                val = "".join(t.text or "" for t in c.iter(m + "t"))
            elif v is not None:
                try:
                    val = float(v.text)
                except ValueError:
                    val = v.text
            else:
                val = None
            cells[idx - 1] = val
        rows.append([cells.get(i) for i in range(max(cells) + 1)] if cells else [])
    return rows


def read_ods(raw):
    """{sheet name: rows} of an OpenDocument spreadsheet (bytes); repeated cells and rows are expanded (rows capped at 2000)."""
    import io, zipfile
    import xml.etree.ElementTree as ET
    T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
    O = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
    X = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
    root = ET.fromstring(zipfile.ZipFile(io.BytesIO(raw)).read("content.xml"))
    out = {}
    for tb in root.iter(T + "table"):
        rows = []
        for row in tb.iter(T + "table-row"):
            cells = []
            for c in row:
                if c.tag not in (T + "table-cell", T + "covered-table-cell"):
                    continue
                n = min(int(c.get(T + "number-columns-repeated", "1")), 200)
                v = c.get(O + "value")
                if v is not None:
                    try:
                        v = float(v)
                    except ValueError:
                        pass
                else:
                    txt = " ".join("".join(p.itertext()) for p in c.iter(X + "p"))
                    v = txt if txt else None
                cells += [v] * n
            while cells and cells[-1] is None:
                cells.pop()
            for _ in range(min(int(row.get(T + "number-rows-repeated", "1")), 5)):
                rows.append(cells)
            if len(rows) > 2000:
                break
        out[tb.get(T + "name")] = rows
    return out
