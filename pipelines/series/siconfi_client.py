"""SICONFI (Tesouro Nacional) client shared by the series builders.

One gzip JSONL cache file per entity (pipelines/series/cache/siconfi/<esfera>-<id>.jsonl.gz). Each API response is
appended as one gzip member, so an interrupted run loses at most the record being written and a rerun resumes.
Rows are stored losslessly but compactly: the fields that are constant within a response (exercicio, periodo,
instituicao, ...) go once in "meta"; each item keeps [rotulo, coluna, cod_conta, conta, valor].
Empty answers are cached too (status "empty"), except for the current year, where a report can still arrive.
"""
import gzip
import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
CACHE_DIR = Path(__file__).resolve().parent / "cache" / "siconfi"
CURRENT_YEAR = 2026
ROW_FIELDS = ("rotulo", "coluna", "cod_conta", "conta", "valor")


def _http_json(url, tries=10):
    last = None
    for n in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as exc:  # 429 = the API's rate limit: wait longer than for other errors
            last = exc
            retry = exc.headers.get("Retry-After") if exc.headers else None
            wait = int(retry) if retry and retry.isdigit() else (min(600, 30 * 2 ** n) if exc.code == 429 else min(60, 2 * 2 ** n))
            time.sleep(wait)
        except Exception as exc:  # network errors: back off and retry
            last = exc
            time.sleep(min(60, 2 * (2 ** n)))
    raise RuntimeError(f"failed after {tries} tries: {url}: {last}")


def fetch_all(url):
    """Follows ORDS pagination (limit 5000) and returns the full item list."""
    items, offset = [], 0
    while True:
        page = _http_json(url + (f"&offset={offset}" if offset else ""))
        items.extend(page["items"])
        if not page.get("hasMore"):
            return items
        offset += len(page["items"])


def rreo_url(year, period, tipo, esfera, ente, anexo):
    q = {"an_exercicio": year, "nr_periodo": period, "co_tipo_demonstrativo": tipo, "co_esfera": esfera,
         "id_ente": ente, "no_anexo": anexo}
    return API + "/rreo?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)


def rgf_url(year, periodicity, period, tipo, esfera, ente, anexo="RGF-Anexo 02", poder="E"):
    q = {"an_exercicio": year, "in_periodicidade": periodicity, "nr_periodo": period, "co_tipo_demonstrativo": tipo,
         "no_anexo": anexo, "co_esfera": esfera, "co_poder": poder, "id_ente": ente}
    return API + "/rgf?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)


def compact(items):
    if not items:
        return {}, []
    meta = {k: v for k, v in items[0].items() if k not in ROW_FIELDS}
    for it in items:
        for k, v in meta.items():
            if it.get(k) != v:
                raise ValueError(f"field {k} not constant within a response")
    return meta, [[it.get(f) for f in ROW_FIELDS] for it in items]


class EntityCache:
    """Cache of one entity. Not thread-safe by design: one worker owns one entity at a time."""

    def __init__(self, esfera, ente):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.path = CACHE_DIR / f"{esfera}-{ente}.jsonl.gz"
        self.records = {}
        if self.path.exists():
            good, broken = [], False
            try:
                with gzip.open(self.path, "rt", encoding="utf-8") as fh:
                    for line in fh:
                        good.append(json.loads(line))
            except (EOFError, OSError, json.JSONDecodeError):
                broken = True
            for rec in good:
                self.records[rec["key"]] = rec
            if broken:  # rewrite without the truncated tail so later appends stay readable
                with gzip.open(self.path, "wt", encoding="utf-8") as fh:
                    for rec in self.records.values():
                        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def get(self, key, url):
        rec = self.records.get(key)
        if rec is not None:
            return rec
        items = fetch_all(url)
        meta, rows = compact(items)
        rec = {"key": key, "url": url, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "status": "ok" if rows else "empty", "meta": meta, "rows": rows}
        year = int(key.split("|")[1])
        if rows or year < CURRENT_YEAR:
            with gzip.open(self.path, "at", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            self.records[key] = rec
        return rec

    def rreo(self, year, period, tipo, esfera, ente, anexo):
        key = f"rreo|{year}|{period}|{tipo}|{anexo}"
        return self.get(key, rreo_url(year, period, tipo, esfera, ente, anexo))

    def rgf(self, year, periodicity, period, tipo, esfera, ente, anexo="RGF-Anexo 02"):
        key = f"rgf|{year}|{periodicity}{period}|{tipo}|{anexo}"
        return self.get(key, rgf_url(year, periodicity, period, tipo, esfera, ente, anexo))


def entes():
    return _http_json(API + "/entes")["items"]


class Progress:
    def __init__(self, total, every=25, label=""):
        self.total, self.every, self.label, self.n = total, every, label, 0
        self.lock = threading.Lock()
        self.t0 = time.time()

    def tick(self):
        with self.lock:
            self.n += 1
            if self.n % self.every == 0 or self.n == self.total:
                print(f"{self.label} {self.n}/{self.total} ({time.time() - self.t0:.0f}s)", flush=True)
