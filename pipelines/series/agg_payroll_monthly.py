"""Stream the Portal da Transparencia monthly expense-execution ZIPs (Execucao da Despesa), keep what the federal
payroll series needs, delete each raw file.

Usage: agg_payroll_monthly.py <workdir> <YYYYMM-YYYYMM>[,<YYYYMM-YYYYMM>...] [seconds between downloads, default 45]
Ranges are processed in the order given (put the most needed year first). For every month it writes
<workdir>/cache/desp_YYYYMM.json with:
  gnd1:   every row of Grupo de Despesa 1 (Pessoal e Encargos Sociais), summed by
          [UF (budget localizer), orgao superior, orgao subordinado, unidade gestora, unidade orcamentaria, acao,
           modalidade, elemento] -> [valor pago, restos a pagar pagos, valor liquidado]
  fcdf:   every row of unidade orcamentaria 73901 (Fundo Constitucional do Distrito Federal), any group, summed by
          [grupo, modalidade, acao, elemento] -> same three values
  totals: all rows summed by [grupo, modalidade] -> same three values (national check)
  names:  code -> name for orgaos, unidades gestoras, unidades orcamentarias and acoes
The raw ZIP is deleted as soon as the month is aggregated, so the disk never holds more than one month.
Already aggregated months are skipped (resumable).
"""
import collections, csv, io, json, os, subprocess, sys, time, zipfile

W = sys.argv[1]
RANGES = [r.split("-") for r in sys.argv[2].split(",")]
PACE = int(sys.argv[3]) if len(sys.argv) > 3 else 45
URL = "https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/{}"
os.makedirs(os.path.join(W, "cache"), exist_ok=True); os.makedirs(os.path.join(W, "raw"), exist_ok=True)


def months(a, b):
    y, m = int(a[:4]), int(a[4:])
    while f"{y}{m:02d}" <= b:
        yield f"{y}{m:02d}"
        m += 1
        if m == 13: y, m = y + 1, 1


def num(x):
    return float(x.replace(".", "").replace(",", ".")) if x else 0.0


def add(d, k, p, rp, liq):
    a = d[k]; a[0] += p; a[1] += rp; a[2] += liq


for a, b in RANGES:
    for ym in months(a, b):
        out = os.path.join(W, "cache", f"desp_{ym}.json")
        if os.path.exists(out): continue
        zp = os.path.join(W, "raw", f"desp_{ym}.zip")
        if not (os.path.exists(zp) and zipfile.is_zipfile(zp)):
            # The CGU download host sits behind an AWS WAF that answers bursts with an HTML "Human Verification"
            # page: pace the downloads and back off when that page comes back.
            for attempt in range(7):
                rc = subprocess.run(["curl", "-sS", "-L", "-m", "600", "-A", "Mozilla/5.0", "-o", zp, URL.format(ym)]).returncode
                if rc == 0 and zipfile.is_zipfile(zp): break
                wait = min(120 * 2 ** attempt, 1800)
                print(ym, "not a zip (WAF challenge or error), waiting", wait, "s", flush=True)
                time.sleep(wait)
            else:
                print(ym, "DOWNLOAD FAILED", flush=True); continue
            fetched = True
        else:
            fetched = False
        size = os.path.getsize(zp)
        z = zipfile.ZipFile(zp); name = z.namelist()[0]
        r = csv.reader(io.TextIOWrapper(z.open(name), encoding="latin1"), delimiter=";")
        ix = {c: i for i, c in enumerate(next(r))}
        c = lambda col: ix[col]
        iym, iuf = c("Ano e mês do lançamento"), c("UF")
        ios, ion, iob, iobn = c("Código Órgão Superior"), c("Nome Órgão Superior"), c("Código Órgão Subordinado"), c("Nome Órgão Subordinado")
        iug, iugn, iuo, iuon = c("Código Unidade Gestora"), c("Nome Unidade Gestora"), c("Código Unidade Orçamentária"), c("Nome Unidade Orçamentária")
        iac, iacn, ign, imo, iel = c("Código Ação"), c("Nome Ação"), c("Código Grupo de Despesa"), c("Código Modalidade da Despesa"), c("Código Elemento de Despesa")
        ip, irp, il = c("Valor Pago (R$)"), c("Valor Restos a Pagar Pagos (R$)"), c("Valor Liquidado (R$)")
        gnd1, fcdf, tot = (collections.defaultdict(lambda: [0.0, 0.0, 0.0]) for _ in range(3))
        names = {"orgao": {}, "ug": {}, "uo": {}, "acao": {}}
        yms = collections.Counter(); n = 0
        for row in r:
            n += 1; yms[row[iym]] += 1
            p, rp, liq = num(row[ip]), num(row[irp]), num(row[il])
            g, mo = row[ign], row[imo]
            add(tot, (g, mo), p, rp, liq)
            if row[iuo] == "73901":
                add(fcdf, (g, mo, row[iac], row[iel]), p, rp, liq)
            if g == "1":
                add(gnd1, (row[iuf], row[ios], row[iob], row[iug], row[iuo], row[iac], mo, row[iel]), p, rp, liq)
                names["orgao"].setdefault(row[ios], row[ion]); names["orgao"].setdefault(row[iob], row[iobn])
                names["ug"].setdefault(row[iug], row[iugn]); names["uo"].setdefault(row[iuo], row[iuon])
                names["acao"].setdefault(row[iac], row[iacn])
            elif row[iuo] == "73901":
                names["acao"].setdefault(row[iac], row[iacn])
        z.close(); os.remove(zp)
        r2 = lambda d: [list(k) + [round(v[0], 2), round(v[1], 2), round(v[2], 2)] for k, v in d.items()]
        json.dump({"month": ym, "rows": n, "zip_bytes": size, "file": name, "url": URL.format(ym),
                   "ano_mes_values": dict(yms), "gnd1": r2(gnd1), "fcdf": r2(fcdf), "totals": r2(tot), "names": names},
                  open(out, "w"), ensure_ascii=False)
        g1 = sum(v[0] + v[1] for v in gnd1.values())
        print(ym, "rows", n, "zip", size, "gnd1_paid_bi", round(g1 / 1e9, 3), "fcdf_paid_bi",
              round(sum(v[0] + v[1] for v in fcdf.values()) / 1e9, 3), flush=True)
        if fetched: time.sleep(PACE)
print("DONE", flush=True)
