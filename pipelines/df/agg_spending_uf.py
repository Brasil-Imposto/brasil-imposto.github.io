"""Direct spending of the União by the state of the location code (Portal da Transparência, Execução da Despesa).

Usage: agg_spending_uf.py <workdir> <YYYYMM>[,<YYYYMM>...] [seconds between downloads, default 90]
For each month it writes <workdir>/cache/despuf_YYYYMM.json with the sum of amount paid, restos a pagar paid and liquidated by
[state, location code (only when the state is empty), expense group, modality, top-level body, function].
The raw ZIP is deleted as soon as the month is summed. Months already summed are skipped (it resumes where it stopped).
The CGU server has an AWS WAF that blocks bursts: one download every 90 s, with a growing wait.
"""
import collections, csv, io, json, os, subprocess, sys, time, zipfile

W = sys.argv[1]
MONTHS = sys.argv[2].split(",")
PACE = int(sys.argv[3]) if len(sys.argv) > 3 else 90
URL = "https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/{}"
os.makedirs(os.path.join(W, "cache"), exist_ok=True); os.makedirs(os.path.join(W, "raw"), exist_ok=True)


def num(x):
    return float(x.replace(".", "").replace(",", ".")) if x else 0.0


for ym in MONTHS:
    out = os.path.join(W, "cache", f"despuf_{ym}.json")
    if os.path.exists(out):
        continue
    zp = os.path.join(W, "raw", f"desp_{ym}.zip")
    t0 = time.time()
    for attempt in range(6):
        rc = subprocess.run(["curl", "-sS", "-L", "-m", "900", "-A", "Mozilla/5.0", "-o", zp, URL.format(ym)]).returncode
        if rc == 0 and zipfile.is_zipfile(zp):
            break
        wait = min(120 * 2 ** attempt, 1800)
        print(ym, "não é ZIP (desafio do WAF ou erro), esperando", wait, "s", flush=True)
        time.sleep(wait)
    else:
        print(ym, "DOWNLOAD FALHOU", flush=True)
        continue
    size = os.path.getsize(zp)
    z = zipfile.ZipFile(zp); name = z.namelist()[0]
    r = csv.reader(io.TextIOWrapper(z.open(name), encoding="latin1"), delimiter=";")
    ix = {c: i for i, c in enumerate(next(r))}
    iuf, iloc, iln = ix["UF"], ix["Código Localizador"], ix["Nome Localizador"]
    ios, ion = ix["Código Órgão Superior"], ix["Nome Órgão Superior"]
    ign, imo, ifu, ifn = ix["Código Grupo de Despesa"], ix["Código Modalidade da Despesa"], ix["Código Função"], ix["Nome Função"]
    ip, irp, il = ix["Valor Pago (R$)"], ix["Valor Restos a Pagar Pagos (R$)"], ix["Valor Liquidado (R$)"]
    agg = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    names = {"orgao": {}, "funcao": {}, "localizador": {}}
    n = 0
    for row in r:
        n += 1
        uf = row[iuf].strip()
        loc = "" if uf and uf != "-1" else row[iloc]
        if loc:
            names["localizador"][loc] = row[iln][:80]
        names["orgao"][row[ios]] = row[ion][:80]
        names["funcao"][row[ifu]] = row[ifn][:60]
        a = agg[(uf, loc, row[ign], row[imo], row[ios], row[ifu])]
        a[0] += num(row[ip]); a[1] += num(row[irp]); a[2] += num(row[il])
    z.close(); os.remove(zp)
    json.dump({"month": ym, "url": URL.format(ym), "file": name, "zip_bytes": size, "rows": n,
               "columns": ["uf", "localizador_sem_uf", "grupo", "modalidade", "orgao_superior", "funcao",
                           "valor_pago", "restos_a_pagar_pagos", "valor_liquidado"],
               "agg": [list(k) + [round(v[0], 2), round(v[1], 2), round(v[2], 2)] for k, v in agg.items()],
               "names": names}, open(out, "w"), ensure_ascii=False)
    print(ym, "ok", n, "linhas", size, "bytes", round(time.time() - t0), "s", flush=True)
    time.sleep(PACE)
print("fim", flush=True)
