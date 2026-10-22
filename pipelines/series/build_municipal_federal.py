"""Assemble data/series/{uf}-municipal-federal.json: the municipalities of one state (default Santa Catarina), 2019 onward.

Usage: build_municipal_federal.py <workdir> [last Portal month published, YYYY-MM] [--uf RS] [--transfers DIR]
                                  [--out PATH] [--collected-at YYYY-MM-DD] [--control]
  (needs openpyxl; run build_population.py --uf <UF> and agg_transfers_monthly.py --ufs <UF> first)
  federal_revenue_annual: Receita Federal, arrecadação por município (sheet TOTAL = DARF + GPS), one XLSX per year, <workdir>/rfbmun/rfb-mun-YYYY.xlsx
  transfers_monthly:      Portal da Transparência (<transfers>/transf_YYYYMM.json, default <workdir>/cache, "by_uf" rows of the UF),
                          recipient rule classify_transfers.municipal_government
  bolsa_familia_monthly:  MDS MI Social (Bolsa Família or Auxílio Brasil, same fields as the UF series), <workdir>/misocial
  bpc_monthly:            MDS MI Social, bpc_val_f (BPC paid in the municipality)
  population:             data/series/population.json, block {uf}_municipalities
Municipality names in the Receita and Portal files are matched to IBGE codes by municipality_names.py (normalised name,
plus the spelling differences of each state, found by the unmatched-name lists).
Checks (the JSON is written only when all pass):
  revenue    every row of each year's TOTAL sheet adds up to the sheet's own TOTAL row (within R$ 0,01: that row is an
             Excel sum of floats); each municipality's value, and the state's sum, equal an independent Decimal pass over
             the state's rows of the same sheet (within half a cent: the series is the file's value rounded to the cent);
             the TOTAL sheet equals DARF + GPS for each municipality of the state (diagnostic, listed)
  transfers  each municipality-month, and each unmatched name, equals the independent Decimal pass that
             agg_transfers_monthly.py made over the same Portal file (within half a cent)
--control plants R$ 0,01 in one revenue value, in one transfer month and in one GPS value, and leaves one sheet row unread:
every check must fail (the diagnostic must list the planted difference) and nothing is written.
"""
import collections, csv, glob, json, sys
from datetime import date
from decimal import Decimal
from pathlib import Path
import openpyxl
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from classify_transfers import municipal_government
from municipality_names import matcher


def take(argv, name, default=None):
    if name in argv:
        i = argv.index(name); value = argv[i + 1]; del argv[i:i + 2]; return value
    return default


ARGS = sys.argv[1:]
CONTROL = "--control" in ARGS
if CONTROL: ARGS.remove("--control")
UF = take(ARGS, "--uf", "SC").upper()
TRANSFERS = take(ARGS, "--transfers")
OUT_ARG = take(ARGS, "--out")
COLLECTED = take(ARGS, "--collected-at") or date.today().isoformat()
W = Path(ARGS[0]); ROOT = HERE.parents[1]
TRANSFERS = Path(TRANSFERS) if TRANSFERS else W / "cache"
OUT = Path(OUT_ARG) if OUT_ARG else ROOT / "data" / "series" / f"{UF.lower()}-municipal-federal.json"
POP = json.load(open(ROOT / "data" / "series" / "population.json"))
FIRST = "2019-01"; YEARS = list(range(2019, 2026))

names = {c: m["name"].rsplit(" - ", 1)[0] for c, m in POP[f"{UF.lower()}_municipalities"].items()}   # SIDRA names end in " - UF"
code_of = matcher(UF, names)
def mrange(a, b):
    y, m = map(int, a.split("-"))
    while f"{y}-{m:02d}" <= b:
        yield f"{y}-{m:02d}"; m += 1
        if m == 13: y, m = y + 1, 1

# federal revenue per municipality, annual
rev, rev_unmatched, rev_totals = collections.defaultdict(dict), {}, {}
RFB = "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/copy_of_arrecadacao-das-receitas-administradas-pela-rfb-por-municipio/arrecadacao-das-receitas-administradas-pela-rfb/arrecadacao-da-receita-administrada-pela-rfb-por-municipio-{}.xlsx"
for y in YEARS:
    wb = openpyxl.load_workbook(W / "rfbmun" / f"rfb-mun-{y}.xlsx", read_only=True)
    ws = wb[[s for s in wb.sheetnames if s.upper() == "TOTAL"][0]]
    um = []
    for row in ws.iter_rows(min_row=7, values_only=True):
        if not row or row[1] != UF or not isinstance(row[2], (int, float)): continue
        c = code_of(row[0])
        if c: rev[c][str(y)] = rev[c].get(str(y), 0.0) + float(row[2])
        else: um.append(row[0])
    rev_unmatched[str(y)] = um
    rev_totals[str(y)] = round(sum(v.get(str(y), 0.0) for v in rev.values()), 2)

# transfers to the municipal government, monthly
caches = sorted(glob.glob(str(TRANSFERS / "transf_*.json")))
avail = {f"{Path(c).stem[7:11]}-{Path(c).stem[11:13]}" for c in caches}
TR_LAST = max(max(avail), ARGS[1] if len(ARGS) > 1 else "")
tr = collections.defaultdict(lambda: collections.defaultdict(float)); tr_unmatched = collections.defaultdict(float); tr_other = collections.defaultdict(float)
tr_decimal = {}  # month -> {municipality name -> Decimal}, the independent pass stored by agg_transfers_monthly.py
for c in caches:
    d = json.load(open(c)); ym = f"{d['month'][:4]}-{d['month'][4:]}"
    tr_decimal[ym] = {k: Decimal(v) for k, v in d["municipal_decimal"][UF].items()}
    for mun, fav, modal, v in d["by_uf"][UF]:
        if not municipal_government(fav, modal): tr_other[ym] += v; continue
        code = code_of(mun)
        if code: tr[code][ym] += v
        else: tr_unmatched[f"{ym}|{mun}"] += v

# Bolsa Família / Auxílio Brasil and BPC per municipality (MI Social, 6-digit IBGE code)
six = {c[:6]: c for c in names}
bf = collections.defaultdict(lambda: collections.defaultdict(float)); bpc = collections.defaultdict(lambda: collections.defaultdict(float))
bf_month_tot, bpc_month_tot = collections.defaultdict(float), collections.defaultdict(float)
for f in sorted(glob.glob(str(W / "misocial" / "misocial_*.csv"))):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if r["sigla_uf"] != UF: continue
        ym = f"{r['anomes_s'][:4]}-{r['anomes_s'][4:]}"; c = six[r["codigo_ibge"]]
        v = sum(float(r[k]) for k in ("valor_repassado_bolsa_familia_f", "pab_valor_pago_d", "pab_extraordinario_valor_pago_d") if r[k] not in ("", None))
        bf[c][ym] += v; bf_month_tot[ym] += v
        if r["bpc_val_f"] not in ("", None): bpc[c][ym] += float(r["bpc_val_f"]); bpc_month_tot[ym] += float(r["bpc_val_f"])
BF_LAST = max(m for m, v in bf_month_tot.items() if v > 0); BPC_LAST = max(m for m, v in bpc_month_tot.items() if v > 0)
LAST = max(TR_LAST, BF_LAST, BPC_LAST); MONTHS = list(mrange(FIRST, LAST))
def r2(x): return None if x is None else round(x, 2)

mun = {}
for c in sorted(names):
    mun[c] = {"name": names[c], "population": POP[f"{UF.lower()}_municipalities"][c]["population"],
              "federal_revenue_annual": {str(y): r2(rev[c].get(str(y))) for y in YEARS},
              "transfers_monthly": [r2(tr[c].get(ym, 0.0)) if ym in avail else None for ym in MONTHS],
              "bolsa_familia_monthly": [r2(bf[c].get(ym, 0.0)) if ym <= BF_LAST else None for ym in MONTHS],
              "bpc_monthly": [r2(bpc[c].get(ym, 0.0)) if ym <= BPC_LAST else None for ym in MONTHS]}
checks = {"municipalities": len(mun), "revenue_unmatched_names": rev_unmatched, "revenue_sum_by_year": rev_totals,
          "revenue_missing": {str(y): [c for c in mun if mun[c]["federal_revenue_annual"][str(y)] is None] for y in YEARS},
          "transfers_unmatched": {k: round(v, 2) for k, v in tr_unmatched.items()},
          f"transfers_to_other_{UF.lower()}_recipients_excluded_by_year": {y: round(sum(v for m, v in tr_other.items() if m.startswith(y)), 2) for y in sorted({m[:4] for m in tr_other})},
          "transfers_missing_months": [m for m in mrange(FIRST, TR_LAST) if m not in avail] or None}
if checks["transfers_missing_months"]:
    checks["transfers_missing_reason"] = "publicado pelo Portal, mas não agregado nesta coleta (verificação anti-robô do servidor da CGU); rodar agg_transfers_monthly.py de novo"

# ---------- checks against independent passes, on the values that would be written ----------
HALF_CENT, CENT = Decimal("0.005"), Decimal("0.01")
dec = lambda x: Decimal(str(x))
if CONTROL:  # planted defects: R$ 0,01 in one revenue value and in one transfer month
    first = next(iter(mun))
    mun[first]["federal_revenue_annual"]["2024"] = round(mun[first]["federal_revenue_annual"]["2024"] + 0.01, 2)
    i = MONTHS.index(max(avail)); mun[first]["transfers_monthly"][i] = round(mun[first]["transfers_monthly"][i] + 0.01, 2)
failed, report = [], []

rev_errs, rev_diag, sheet_errs = [], [], []
for y in YEARS:
    wb = openpyxl.load_workbook(W / "rfbmun" / f"rfb-mun-{y}.xlsx", read_only=True, data_only=True)
    sheets = {s.upper(): wb[s] for s in wb.sheetnames}
    per_sheet = {}
    for sname in ("TOTAL", "DARF", "GPS"):
        rows = [r for r in sheets[sname].iter_rows(values_only=True) if r and len(r) > 2 and r[0] is not None]
        # the sheet's own total: label TOTAL (or Total), UF "-" (2023: empty), a number (the 2019 subtitle row is also "TOTAL")
        total_row = [r for r in rows if str(r[0]).strip().upper() == "TOTAL" and r[1] in ("-", None) and isinstance(r[2], (int, float))]
        body = [r for r in rows if isinstance(r[2], (int, float)) and r not in total_row]
        if CONTROL and y == 2024 and sname == "TOTAL":  # planted: one row of the sheet left unread
            body = body[1:]
        if CONTROL and y == 2024 and sname == "GPS":  # planted: R$ 0,01 in the GPS value of the state's first row
            k = next(i for i, r in enumerate(body) if r[1] == UF); body[k] = (body[k][0], body[k][1], body[k][2] + 0.01)
        if sname == "TOTAL":
            s = sum(dec(r[2]) for r in body)
            if len(total_row) != 1:
                sheet_errs.append((y, "linha TOTAL da aba TOTAL não encontrada"))
            elif abs(s - dec(total_row[0][2])) >= CENT:
                sheet_errs.append((y, "linhas - TOTAL da aba", str(s - dec(total_row[0][2]))))
        acc = collections.defaultdict(Decimal)
        for r in body:
            if r[1] == UF: acc[r[0]] += dec(r[2])
        per_sheet[sname] = acc
    by_code, unmatched = collections.defaultdict(Decimal), Decimal(0)
    for name, v in per_sheet["TOTAL"].items():
        c = code_of(name)
        if c: by_code[c] += v
        else: unmatched += v
    for c, m in mun.items():
        got = m["federal_revenue_annual"][str(y)]
        if (got is None) != (c not in by_code) or (got is not None and abs(dec(got) - by_code[c]) > HALF_CENT):
            rev_errs.append((y, c, m["name"], got, str(by_code.get(c))))
    written = sum(dec(m["federal_revenue_annual"][str(y)] or 0) for m in mun.values())
    expected = sum(per_sheet["TOTAL"].values())
    if unmatched or abs(written - expected) > HALF_CENT * len(mun):
        rev_errs.append((y, "soma do estado", str(written), str(expected), "sem município: " + str(unmatched)))
    for name, v in per_sheet["TOTAL"].items():
        parts = per_sheet["DARF"].get(name, Decimal(0)) + per_sheet["GPS"].get(name, Decimal(0))
        if v.quantize(CENT) != parts.quantize(CENT):  # each side rounded to the cent: the sheets carry float noise
            rev_diag.append((y, name, str(v), str(parts)))
    report.append(f"{y}: {len(per_sheet['TOTAL'])} linhas de {UF}, soma R$ {expected:,.2f}")
print(f"[{'OK' if not sheet_errs else 'FAIL'}] revenue: every row of each TOTAL sheet adds up to the sheet's own TOTAL row ({len(YEARS)} years)", sheet_errs[:5])
print(f"[{'OK' if not rev_errs else 'FAIL'}] revenue: {UF} municipality values and state sum vs an independent Decimal pass over the sheet: {len(rev_errs)} error(s)", rev_errs[:5])
print(f"[DIAG] revenue: TOTAL sheet vs DARF + GPS per municipality of {UF}, each rounded to the cent: {len(rev_diag)} difference(s)", rev_diag[:5])
for line in report: print("      ", line)
failed += ["revenue sheet total"] if sheet_errs else []
failed += ["revenue vs Decimal pass"] if rev_errs else []

tr_errs, n_cells = [], 0
for ym in sorted(avail):
    i = MONTHS.index(ym)
    exp_code, exp_un = collections.defaultdict(Decimal), {}
    for name, v in tr_decimal[ym].items():
        c = code_of(name)
        if c: exp_code[c] += v
        else: exp_un[f"{ym}|{name}"] = v
    for c, m in mun.items():
        n_cells += 1
        got = m["transfers_monthly"][i]
        if got is None or abs(dec(got) - exp_code.get(c, Decimal(0))) > HALF_CENT:
            tr_errs.append((ym, c, m["name"], got, str(exp_code.get(c, Decimal(0)))))
    got_un = {k: v for k, v in checks["transfers_unmatched"].items() if k.startswith(ym + "|")}
    for k in set(got_un) | set(exp_un):
        if k not in got_un or k not in exp_un or abs(dec(got_un[k]) - exp_un[k]) > HALF_CENT:
            tr_errs.append((k, "sem município", got_un.get(k), str(exp_un.get(k))))
print(f"[{'OK' if not tr_errs else 'FAIL'}] transfers: {n_cells} municipality-months vs the independent Decimal pass over the same Portal files: {len(tr_errs)} error(s)", tr_errs[:5])
failed += ["transfers vs Decimal pass"] if tr_errs else []
if failed:
    raise SystemExit(f"CHECK FAILED: {failed}; nothing written")

s25, s24 = rev_totals["2025"], rev_totals["2024"]
bi = lambda v: f"{v / 1e9:.1f}".replace(".", ",")
compared = ("é parecida com a de 2024, mas" if abs(s25 / s24 - 1) <= 0.05 else
            f"é {'maior' if s25 > s24 else 'menor'} que a de 2024 (R$ {bi(s24)} bi), e")
OUT.write_text(json.dumps({
    "uf": UF, "months": MONTHS, "years": YEARS, "currency": "BRL, valores correntes", "collected_at": COLLECTED,
    "coverage": {"federal_revenue_annual": [str(YEARS[0]), str(YEARS[-1])], "transfers_monthly": [FIRST, TR_LAST], "bolsa_familia_monthly": [FIRST, BF_LAST], "bpc_monthly": [FIRST, BPC_LAST]},
    "definitions": {
        "federal_revenue_annual": "arrecadação das receitas administradas pela Receita Federal registrada no município (aba TOTAL = DARF + GPS); não inclui receitas de outros órgãos",
        "transfers_monthly": f"transferências federais à prefeitura: favorecido 'Administração Pública Municipal', ou 'Administração Pública' com modalidade 40 ou 41 (mesma regra de data/{UF.lower()}-municipal-balance-2024.json)",
        "bolsa_familia_monthly": "Bolsa Família (2019-01 a 2021-10 e de 2023-03 em diante) ou Auxílio Brasil (2021-11 a 2023-02) pago no município; o Auxílio Emergencial não está incluído",
        "bpc_monthly": "Benefício de Prestação Continuada pago no município (MI Social, bpc_val_f); é parte dos benefícios do INSS, a única parte com dado aberto por município nesta série"},
    "flags": {"2025_federal_revenue": f"O arquivo municipal de 2025 da Receita tem a mesma quebra do arquivo por UF (Brasília com R$ 603 bi). Em {UF} a soma dos municípios de 2025 (R$ {bi(s25)} bi) {compared} a distribuição entre municípios não foi validada contra outra fonte.",
              "transfers_partial_month": f"{TR_LAST} está incompleto (arquivo gerado pelo Portal durante o mês)." if TR_LAST >= COLLECTED[:7] and TR_LAST in avail else None,
              "population": "2023 sem estimativa do IBGE (null); ver data/series/population.json."},
    "sources": [{"field": "federal_revenue_annual", "url": RFB.format("AAAA"), "files": {str(y): RFB.format(y) for y in YEARS}},
                {"field": "transfers_monthly", "url": "https://portaldatransparencia.gov.br/download-de-dados/transferencias/AAAAMM"},
                {"field": "bolsa_familia_monthly", "url": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&fq=anomes_s:AAAA*&fq=sigla_uf:{UF}&fl=codigo_ibge,anomes_s,valor_repassado_bolsa_familia_f,pab_valor_pago_d,pab_extraordinario_valor_pago_d&rows=200000&wt=csv"},
                {"field": "bpc_monthly", "url": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&fq=anomes_s:AAAA*&fq=sigla_uf:{UF}&fl=codigo_ibge,anomes_s,bpc_val_f&rows=200000&wt=csv"},
                {"field": "population", "url": "data/series/population.json (IBGE SIDRA 6579 e 4709)"}],
    "checks": checks, "municipalities": mun}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(json.dumps({k: v for k, v in checks.items() if k != "revenue_missing"}, ensure_ascii=False)[:1500])
print("revenue missing counts", {y: len(v) for y, v in checks["revenue_missing"].items()})
print("wrote", OUT, OUT.stat().st_size // 1024, "KB")
