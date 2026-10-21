"""Municipal taxes paid in each state, 2024: the sum over every municipality (SICONFI RREO Anexo 03, 6th bimester).

SICONFI has no bulk endpoint for municipalities, so this makes one call per municipality (5,570), keeps only the
12-month totals of the tax lines, and caches each result in a JSONL file so an interrupted run resumes.
Coverage is part of the output: a state's total is only as complete as the number of municipalities that reported.
Small municipalities file the "RREO Simplificado" instead of the RREO, so both report types are tried (the first run
asked only for "RREO" and wrongly counted 2,329 municipalities as not reporting; kept as a record of the trap).
Run: python3 data/scripts/siconfi/build_municipal_taxes.py
"""
import json
import time
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data" / "scripts" / "siconfi" / "cache" / "municipal-rreo03-2024.jsonl"
OUT = ROOT / "data" / "municipal-taxes-2024.json"
API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
URL = API + "/rreo?an_exercicio=2024&nr_periodo=6&co_tipo_demonstrativo={tipo}&co_esfera=M&no_anexo=RREO-Anexo%2003&id_ente={id}"
TYPES = ["RREO", "RREO Simplificado"]
LINES = {"IPTU": "iptu", "ISS": "iss", "ITBI": "itbi", "IRRF": "irrf", "Outros Impostos, Taxas e Contribuições de Melhoria": "other_taxes_fees"}
COL = "TOTAL (ÚLTIMOS 12 MESES)"


def get(url, tries=5):
    for n in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 + 3 * n)
    return None


entes = [e for e in get(API + "/entes")["items"] if e["esfera"] == "M"]
done = {}
CACHE.parent.mkdir(parents=True, exist_ok=True)
if CACHE.exists():
    for line in CACHE.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        # Records from before both report types were tried are fetched again.
        if rec["status"] == "not_reported" and "types_tried" not in rec:
            continue
        done[rec["id"]] = rec
todo = [e for e in entes if e["cod_ibge"] not in done]
print(f"{len(entes)} municipalities, {len(done)} cached, {len(todo)} to fetch", flush=True)


def fetch(e):
    for tipo in TYPES:
        d = get(URL.format(id=e["cod_ibge"], tipo=tipo.replace(" ", "%20")))
        if d is None:
            return {"id": e["cod_ibge"], "uf": e["uf"], "status": "error"}
        vals = {LINES[i["conta"]]: i["valor"] for i in d["items"] if i["coluna"] == COL and i["conta"] in LINES}
        if vals:
            return {"id": e["cod_ibge"], "uf": e["uf"], "status": "ok", "report": tipo, **vals}
    return {"id": e["cod_ibge"], "uf": e["uf"], "status": "not_reported", "types_tried": TYPES}


with open(CACHE, "a", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=6) as pool:
    futures = [pool.submit(fetch, e) for e in todo]
    for n, f in enumerate(as_completed(futures), 1):
        rec = f.result()
        if rec["status"] != "error":
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            done[rec["id"]] = rec
        if n % 250 == 0:
            print(f"{n}/{len(todo)}", flush=True)

by_uf = defaultdict(lambda: {"municipalities": 0, "reported": 0, "not_reported": 0, "errors": 0, **{k: 0.0 for k in LINES.values()}})
last = {}
for line in CACHE.read_text(encoding="utf-8").splitlines():
    rec = json.loads(line)
    last[rec["id"]] = rec
done = last
for e in entes:
    u = by_uf[e["uf"]]
    u["municipalities"] += 1
    rec = done.get(e["cod_ibge"])
    if rec is None:
        u["errors"] += 1
    elif rec["status"] == "ok":
        u["reported"] += 1
        for k in LINES.values():
            u[k] += rec.get(k) or 0.0
    else:
        u["not_reported"] += 1
for u in by_uf.values():
    u["total"] = round(sum(u[k] for k in LINES.values()), 2)
    for k in LINES.values():
        u[k] = round(u[k], 2)

OUT.write_text(json.dumps({
    "year": 2024,
    "source": "SICONFI, RREO Anexo 03 (Receita Corrente Líquida) de cada município, 6º bimestre, coluna 'TOTAL (ÚLTIMOS 12 MESES)'",
    "url_pattern": URL,
    "report_types": TYPES,
    "collected_at": date.today().isoformat(),
    "note": "IRRF é o imposto de renda retido na folha dos servidores municipais, que fica com a prefeitura (CF art. 158, I).",
    "by_uf": dict(sorted(by_uf.items())),
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("coverage:", {k: f"{v['reported']}/{v['municipalities']}" for k, v in sorted(by_uf.items())})
