"""Execução da despesa do Portal da Transparência (Poder Executivo), somada com o código da unidade gestora (UG).

Uso: agg_spending_ug.py <workdir> <YYYYMM>[,<YYYYMM>...] [segundos entre downloads, padrão 90]
Para cada mês grava <workdir>/cache/despug_YYYYMM.json.gz com a soma de valor pago, restos a pagar pagos e valor
liquidado por [UF do localizador, código do localizador, grupo, modalidade, órgão superior, órgão subordinado, UG,
unidade orçamentária, função, subfunção, ação, elemento]. Guarda o cabeçalho do CSV e os nomes dos códigos.
O ZIP bruto é apagado assim que o mês é somado; meses prontos são pulados (retoma de onde parou).
O servidor da CGU tem um WAF da AWS que bloqueia rajadas: um download a cada 90 s, com espera crescente.
"""
import collections, csv, gzip, io, json, os, subprocess, sys, time, zipfile

W = sys.argv[1]
MONTHS = sys.argv[2].split(",")
PACE = int(sys.argv[3]) if len(sys.argv) > 3 else 90
URL = "https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/{}"
os.makedirs(os.path.join(W, "cache"), exist_ok=True); os.makedirs(os.path.join(W, "raw"), exist_ok=True)


def num(x):
    return float(x.replace(".", "").replace(",", ".")) if x else 0.0


for i, ym in enumerate(MONTHS):
    out = os.path.join(W, "cache", f"despug_{ym}.json.gz")
    if os.path.exists(out):
        continue
    zp = os.path.join(W, "raw", f"desp_{ym}.zip")
    t0 = time.time()
    for attempt in range(6):
        if os.path.exists(zp) and zipfile.is_zipfile(zp):
            break  # ZIP já baixado numa rodada anterior
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
    header = next(r)
    ix = {c: k for k, c in enumerate(header)}
    keycols = ["UF", "Código Localizador", "Código Grupo de Despesa", "Código Modalidade da Despesa",
               "Código Órgão Superior", "Código Órgão Subordinado", "Código Unidade Gestora",
               "Código Unidade Orçamentária", "Código Função", "Código Subfução", "Código Ação",
               "Código Elemento de Despesa"]
    namecols = {"localizador": ("Código Localizador", "Nome Localizador"), "orgao": ("Código Órgão Superior", "Nome Órgão Superior"),
                "orgao_sub": ("Código Órgão Subordinado", "Nome Órgão Subordinado"), "ug": ("Código Unidade Gestora", "Nome Unidade Gestora"),
                "uo": ("Código Unidade Orçamentária", "Nome Unidade Orçamentária"), "funcao": ("Código Função", "Nome Função"),
                "acao": ("Código Ação", "Nome Ação"), "elemento": ("Código Elemento de Despesa", "Nome Elemento de Despesa"),
                "modalidade": ("Código Modalidade da Despesa", "Modalidade da Despesa"), "grupo": ("Código Grupo de Despesa", "Nome Grupo de Despesa")}
    ki = [ix[c] for c in keycols]
    ni = {k: (ix[a], ix[b]) for k, (a, b) in namecols.items() if a in ix and b in ix}
    ip, irp, il = ix["Valor Pago (R$)"], ix["Valor Restos a Pagar Pagos (R$)"], ix["Valor Liquidado (R$)"]
    agg = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    names = {k: {} for k in ni}
    n = 0
    for row in r:
        n += 1
        for k, (a, b) in ni.items():
            names[k][row[a]] = row[b][:90]
        v = agg[tuple(row[j].strip() for j in ki)]
        v[0] += num(row[ip]); v[1] += num(row[irp]); v[2] += num(row[il])
    z.close(); os.remove(zp)
    with gzip.open(out + ".tmp", "wt", encoding="utf-8") as f:
        json.dump({"month": ym, "url": URL.format(ym), "file": name, "zip_bytes": size, "rows": n, "header": header,
                   "columns": ["uf", "localizador", "grupo", "modalidade", "orgao_superior", "orgao_subordinado", "ug", "uo",
                               "funcao", "subfuncao", "acao", "elemento", "valor_pago", "restos_a_pagar_pagos", "valor_liquidado"],
                   "agg": [list(k) + [round(x[0], 2), round(x[1], 2), round(x[2], 2)] for k, x in agg.items()],
                   "names": names}, f, ensure_ascii=False)
    os.replace(out + ".tmp", out)
    print(ym, "ok", n, "linhas", size, "bytes", round(time.time() - t0), "s", flush=True)
    if i < len(MONTHS) - 1:
        time.sleep(PACE)
print("fim", flush=True)
