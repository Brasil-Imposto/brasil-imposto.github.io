"""Stream the Portal da Transparencia monthly transfer ZIPs, aggregate them, delete each raw file.

Usage: agg_transfers_monthly.py <workdir> <first YYYYMM> <last YYYYMM> [seconds between downloads, default 45]
                                [--ufs SC,RS] [--raw-dir <dir>]
For every month it writes <workdir>/cache/transf_YYYYMM.json with:
  keys:      [UF, TIPO TRANSFERENCIA, TIPO FAVORECIDO, CODIGO FUNCAO, ACAO, CODIGO MODALIDADE, has_municipio] -> sum of VALOR TRANSFERIDO
  by_uf:     {UF: [[NOME MUNICIPIO, TIPO FAVORECIDO, CODIGO MODALIDADE, sum], ...]}, every row of each UF in --ufs (default SC)
  municipal_decimal: {UF: {NOME MUNICIPIO: "sum"}}: an independent second pass over the same file, in Decimal, of the rows
             paid to the municipal government (favorecido "Administração Pública Municipal", or "Administração Pública"
             with modality 40 or 41); build_municipal_federal.py checks its monthly series against it to the cent
  action_names: ACAO -> NOME ACAO
The raw ZIP (in --raw-dir, default <workdir>/raw) is deleted as soon as the month is aggregated, so the disk never holds
more than one month. Months already aggregated with every requested UF are skipped (resumable).
"""
import collections, csv, io, json, os, subprocess, sys, time, zipfile
from decimal import Decimal


def take(argv, name, default):
    if name in argv:
        i = argv.index(name)
        value = argv[i + 1]
        del argv[i:i + 2]
        return value
    return default


argv = sys.argv[1:]
UFS = take(argv, "--ufs", "SC").split(",")
W = argv[0]; first, last = argv[1], argv[2]
RAW = take(argv, "--raw-dir", None) or os.path.join(W, "raw")
PACE = int(argv[3]) if len(argv) > 3 else 45  # seconds between downloads
URL = "https://portaldatransparencia.gov.br/download-de-dados/transferencias/{}"
os.makedirs(os.path.join(W, "cache"), exist_ok=True); os.makedirs(RAW, exist_ok=True)


def months(a, b):
    y, m = int(a[:4]), int(a[4:])
    while f"{y}{m:02d}" <= b:
        yield f"{y}{m:02d}"
        m += 1
        if m == 13: y, m = y + 1, 1


def num(x):
    return float(x.replace(".", "").replace(",", ".")) if x else 0.0


def decimal_pass(zp, ufs):
    """Second, independent read of the file: Decimal sums of the municipal-government rows, by UF and municipality name."""
    out = {uf: collections.defaultdict(Decimal) for uf in ufs}
    with zipfile.ZipFile(zp) as z:
        rows = csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding="latin1"), delimiter=";")
        for row in rows:
            uf = row["UF"]
            if uf not in out:
                continue
            fav, modal = row["TIPO FAVORECIDO"], row["CÓDIGO MODALIDADE APLICAÇÃO DESPESA"]
            if fav == "Administração Pública Municipal" or (fav == "Administração Pública" and modal in ("40", "41")):
                raw = row["VALOR TRANSFERIDO"]
                out[uf][row["NOME MUNICÍPIO"]] += Decimal(raw.replace(".", "").replace(",", ".")) if raw else Decimal(0)
    return {uf: {k: str(v) for k, v in d.items()} for uf, d in out.items()}


def cached_ok(path):
    if not os.path.exists(path):
        return False
    try:
        d = json.load(open(path))
    except ValueError:
        return False
    return all(uf in d.get("by_uf", {}) and uf in d.get("municipal_decimal", {}) for uf in UFS)


for ym in months(first, last):
    out = os.path.join(W, "cache", f"transf_{ym}.json")
    if cached_ok(out): continue
    zp = os.path.join(RAW, f"transf_{ym}.zip")
    # The CGU download host sits behind an AWS WAF that answers bursts with an HTML "Human Verification" page:
    # pace the downloads and back off when that page comes back.
    for attempt in range(7):
        rc = subprocess.run(["curl", "-sS", "-L", "-m", "600", "-A", "Mozilla/5.0", "-o", zp, URL.format(ym)]).returncode
        if rc == 0 and zipfile.is_zipfile(zp): break
        wait = min(120 * 2 ** attempt, 1800)
        print(time.strftime("%H:%M:%S"), ym, "not a zip (WAF challenge or error), waiting", wait, "s", flush=True)
        time.sleep(wait)
    else:
        print(time.strftime("%H:%M:%S"), ym, "DOWNLOAD FAILED", flush=True); continue
    size = os.path.getsize(zp)
    z = zipfile.ZipFile(zp); name = z.namelist()[0]
    r = csv.reader(io.TextIOWrapper(z.open(name), encoding="latin1"), delimiter=";")
    ix = {c: i for i, c in enumerate(next(r))}
    iu, it, ifv, ifn, ia, ina, imo, imn, iv, iym = (ix[c] for c in ("UF", "TIPO TRANSFERÊNCIA", "TIPO FAVORECIDO", "CÓDIGO FUNÇÃO", "AÇÃO", "NOME AÇÃO",
                                                                   "CÓDIGO MODALIDADE APLICAÇÃO DESPESA", "NOME MUNICÍPIO", "VALOR TRANSFERIDO", "ANO / MÊS"))
    keys, names, yms = collections.defaultdict(float), {}, collections.Counter()
    by_uf = {uf: collections.defaultdict(float) for uf in UFS}
    n = 0
    for row in r:
        n += 1
        v = num(row[iv]); yms[row[iym]] += 1
        keys[(row[iu], row[it], row[ifv], row[ifn], row[ia], row[imo], "MUN" if row[imn] else "NOMUN")] += v
        names.setdefault(row[ia], row[ina])
        if row[iu] in by_uf:
            by_uf[row[iu]][(row[imn], row[ifv], row[imo])] += v
    z.close()
    dec = decimal_pass(zp, UFS)
    os.remove(zp)
    json.dump({"month": ym, "rows": n, "zip_bytes": size, "file": name, "ano_mes_values": dict(yms),
               "keys": [list(k) + [round(v, 2)] for k, v in keys.items()],
               "by_uf": {uf: [list(k) + [round(v, 2)] for k, v in d.items()] for uf, d in by_uf.items()},
               "municipal_decimal": dec, "action_names": names},
              open(out + ".tmp", "w"), ensure_ascii=False)
    os.replace(out + ".tmp", out)
    print(time.strftime("%H:%M:%S"), ym, "rows", n, "zip", size, "total_bi", round(sum(keys.values()) / 1e9, 3), flush=True)
    time.sleep(PACE)
print("DONE", flush=True)
