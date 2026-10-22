"""UF of every SIAPE organizational unit (UORG), read from the SIAPE structure file, streamed and never saved.

Source: https://repositorio.dados.gov.br/segrt/Estrutura%20Organizacional%20-%20SIAPE/DIM_UORG.csv (Ministério da Gestão,
SIAPE, about 164 MB; one row per UORG and validity range, columns data_ref_ini, data_ref_fim, uorg_key, uorg_sg_uf).
It is the same unit register the ministry uses for "Serv_por_mun_exerc" (servants by municipality of exercise).
Usage: python3 pipelines/series/agg_uorg_uf.py 2026-07,2024-07
Output: pipelines/series/cache/payroll/servants/uorg_uf.json.gz  {month: {uorg_key: UF}} for the rows valid in each month,
plus the file's Last-Modified and byte count. Nothing raw touches the disk.
"""
import csv, gzip, io, json, os, sys, urllib.request
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
URL = "https://repositorio.dados.gov.br/segrt/Estrutura%20Organizacional%20-%20SIAPE/DIM_UORG.csv"
OUT = os.path.join(ROOT, "pipelines/series/cache/payroll/servants/uorg_uf.json.gz")
MONTHS = sys.argv[1].split(",")
ym = lambda d: d[6:10] + "-" + d[3:5]  # dd/mm/yyyy -> yyyy-mm
resp = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=1800)
meta = {"url": URL, "last_modified": resp.headers.get("Last-Modified"), "content_length": resp.headers.get("Content-Length")}
r = csv.reader(io.TextIOWrapper(resp, encoding="latin1", newline=""), delimiter=";")
H = next(r); ix = {c: i for i, c in enumerate(H)}
maps = {m: {} for m in MONTHS}; current = {}; rows = 0
for x in r:
    rows += 1
    k, uf = x[ix["uorg_key"]].strip(), x[ix["uorg_sg_uf"]].strip()
    a, b = ym(x[ix["data_ref_ini"]]), ym(x[ix["data_ref_fim"]])
    for m in MONTHS:
        if a <= m <= b and uf: maps[m][k] = uf
    if x[ix["ind_reg_vig_var"]].strip() == "S" and uf: current[k] = uf
meta["rows"] = rows
json.dump({"source": meta, "by_month": maps, "current": current}, gzip.open(OUT, "wt"), ensure_ascii=False)
print(json.dumps(meta), {m: len(v) for m, v in maps.items()}, "current", len(current))
