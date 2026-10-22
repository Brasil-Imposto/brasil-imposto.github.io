"""Numbers for the federal section below the map (D44, GD24), for one run of months of one year.

Usage: .venv/bin/python pipelines/federal/build_federal_section.py 2026 1 7 [--control | --control=input-branch]
Inputs (already in the project):
  data/series/union.json                     Union accounts (Tesouro RTN, BCB)
  data/ug/cache/dtt_monthly_YYYY.json.gz     Tesouro base "Despesas e Transferências Totais da União" (agg_dtt_monthly.py)
  data/df/segrt_servants_uf_202608.json    Executive civil servants in exercise by state (Ministério da Gestão, SIAPE)
  data/federal/raw/camara-ceap-YYYY.csv.zip  Câmara, Cota para o Exercício da Atividade Parlamentar (CEAP)
  data/federal/raw/senado-ceaps-YYYY.csv     Senado, Cota para o Exercício da Atividade Parlamentar dos Senadores (CEAPS)
  data/federal/raw/EmendasParlamentares.zip  Portal da Transparência, emendas parlamentares (all years)
  pipelines/series/cache/union/serie_historica_ago26.xlsx  Tesouro RTN, Tabela 1.1 (line 4.2, personnel, R$ million)
Output: data/federal/federal-section.json, one file, the run's months inside (English keys; money in reais)
Check against an official total published apart from the rows: each month's payroll (Tesouro base, group 1, direct
application) must be 0.970 to 1.000 times RTN line 4.2 "Pessoal e Encargos Sociais" (measured 0.977 to 0.996 over the 92
months of 2019 to 2026-08; the RTN line covers a little more than group 1, modality 90). Assembly checks, in whole cents:
payroll by branch and by kind, CEAP by month and amendments by type and by author add up to the same rows summed directly;
they prove nothing is lost while grouping, not that the rows are complete. The CEAP and the amendments have no total
published apart from the files in the project (the Câmara, the Senado and the Portal publish their own totals online; that
comparison waits for the source registry). --control removes R$ 0,01 from each block after grouping; --control=input-branch
drops the Judiciary's payroll rows of the last month from the input. Both must fail.
"""
import collections, csv, gzip, io, json, os, sys, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
args = [a for a in sys.argv[1:] if not a.startswith("--")]
YEAR, M0, M1 = int(args[0]), int(args[1]), int(args[2])
CONTROL = next(((a.split("=", 1)[1] if "=" in a else "output") for a in sys.argv[1:] if a.startswith("--control")), None)
assert CONTROL in (None, "output", "input-branch"), CONTROL
MONTHS = [f"{YEAR}-{m:02d}" for m in range(M0, M1 + 1)]
c = lambda v: int(round(v * 100))
R = lambda cents: round(cents / 100, 2)
br = lambda s: float(s.replace(".", "").replace(",", ".")) if s.strip() else 0.0

# ---------- Union accounts
u = json.load(open(P("data/series/union.json")))
ix = [u["months"].index(m) for m in MONTHS]
FLOW = ["revenue", "transfers_to_subnationals", "revenue_net", "primary_spending", "primary_result", "primary_result_below_line", "nominal_interest", "nominal_result"]
union = {k: round(sum(u[k][i] for i in ix), 2) for k in FLOW}
union["gross_debt_brl"] = u["gross_debt_brl"][ix[-1]]; union["gross_debt_pct_gdp"] = u["gross_debt_pct_gdp"][ix[-1]]
union["gross_debt_at"] = MONTHS[-1]
union["gross_debt_at_start"] = u["gross_debt_brl"][u["months"].index(f"{YEAR - 1}-12")]
union["latest_month_published"] = u["latest"]["primary_result"]
union["sources"] = u["sources"]

# ---------- federal payroll by branch (Tesouro base, group 1, direct application), and Congress cost
MILITARY_ACTIONS = {"2867", "214H", "0179", "218J", "218K", "00QD"}
BRANCH = {"1000": "legislative", "2000": "legislative", "3000": "legislative", "29000": "dpu", "34000": "mpu"}
BRANCH.update({str(k): "judiciary" for k in range(10000, 18000, 1000)})
dt = json.load(gzip.open(P("data/ug/cache", f"dtt_monthly_{YEAR}.json.gz"), "rt"))
if CONTROL == "input-branch":  # the Judiciary's payroll of the last month goes missing from the input, as a filter bug would
    dt["agg"] = [r for r in dt["agg"] if not (r[0] == M1 and r[3] == "1" and BRANCH.get(r[1]) == "judiciary")]
pay = collections.defaultdict(int); indep_pay = 0; pay_month = collections.defaultdict(int)
# D72: who works today and who is retired or a pensioner are never mixed. The Tesouro base classifies every payroll
# payment with its RTN category: 2.2.1 Ativo Civil and 2.2.2 Ativo Militar (active), 2.2.3 Aposentadorias e pensões civis
# and 2.2.4 Reformas e pensões militares (retired and pensioners, the servants' own regime, not the INSS), 2.2.5
# Sentenças e Precatórios (court-ordered payments).
KIND = lambda cat: "active" if cat.startswith(("2.2.1", "2.2.2")) else "retired_and_pensioners" if cat.startswith(("2.2.3", "2.2.4")) else "court_orders" if cat.startswith("2.2.5") else "other"
pay_kind = collections.defaultdict(lambda: collections.defaultdict(int))
house = collections.defaultdict(lambda: collections.defaultdict(int))
for mon, org, uo, g, mo, ac, cat, v in dt["agg"]:
    if not (M0 <= mon <= M1): continue
    if g == "1" and mo == "90":
        indep_pay += c(v); pay_month[mon] += c(v)
        if uo == "73901": key = "fcdf_df_security_health_education"  # FCDF sits under the Fazenda (25000) in this base
        elif org in BRANCH: key = BRANCH[org]
        elif ac in MILITARY_ACTIONS: key = "executive_military"
        else: key = "executive_civil"
        pay[key] += c(v)
        pay_kind[KIND(cat)][key] += c(v)
    if org in ("1000", "2000") and g in ("1", "3", "4") and mo == "90":  # 91 is the Union paying its own pension fund
        house[{"1000": "chamber", "2000": "senate"}[org]][{"1": "personnel", "3": "operating", "4": "investment"}[g]] += c(v)
if CONTROL == "output": pay["executive_civil"] -= 1
payroll = {k: R(v) for k, v in sorted(pay.items(), key=lambda t: -t[1])}
seats = {"chamber": 513, "senate": 81}
congress = {h: {"total": R(sum(p.values())), "by_group": {k: R(v) for k, v in p.items()}, "members": seats[h],
                "per_member_month": round(sum(p.values()) / 100 / seats[h] / len(MONTHS), 2)} for h, p in house.items()}

# ---------- executive civil servants in exercise (count)
sv = json.load(open(P("data/df/segrt_servants_uf_202608.json")))
servants = {"month": sv["month"], "total": sum(sv["by_uf"].values()), "df": sv["by_uf"]["DF"], "source": sv["source"]}

# ---------- parliamentary quotas
ceap = collections.defaultdict(int); ceap_total_file = 0; members_with_spending = set()
with zipfile.ZipFile(P("data/federal/raw", f"camara-ceap-{YEAR}.csv.zip")) as z:
    rows = csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8-sig"), delimiter=";")
    for r in rows:
        m = int(r["numMes"]); v = c(float(r["vlrLiquido"] or 0))
        if M0 <= m <= M1:
            ceap_total_file += v
            ceap[("chamber", m)] += v
            if r["nuDeputadoId"]: members_with_spending.add(("chamber", r["nuDeputadoId"]))
with open(P("data/federal/raw", f"senado-ceaps-{YEAR}.csv"), encoding="latin-1") as f:
    f.readline()
    for r in csv.DictReader(f, delimiter=";"):
        m = int(r["MES"]); v = c(br(r["VALOR_REEMBOLSADO"]))
        if M0 <= m <= M1:
            ceap_total_file += v
            ceap[("senate", m)] += v
            members_with_spending.add(("senate", r["SENADOR"]))
if CONTROL == "output": ceap[("senate", M1)] -= 1
quota = {h: {"total": R(sum(v for (hh, m), v in ceap.items() if hh == h)),
             "by_month": {f"{YEAR}-{m:02d}": R(ceap[(h, m)]) for m in range(M0, M1 + 1)},
             "members_with_spending": len({x for x in members_with_spending if x[0] == h})} for h in ("chamber", "senate")}

# ---------- parliamentary amendments by author (year to date, as the file has it)
amend = collections.defaultdict(lambda: collections.defaultdict(int)); amend_type = collections.defaultdict(int)
amend_file_total = 0; amend_cols = None
with zipfile.ZipFile(P("data/federal/raw", "EmendasParlamentares.zip")) as z:
    name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    rows = csv.DictReader(io.TextIOWrapper(z.open(name), encoding="latin-1"), delimiter=";")
    amend_cols = rows.fieldnames
    for r in rows:
        if r["Ano da Emenda"] != str(YEAR): continue
        paid = c(br(r["Valor Pago"])); comm = c(br(r["Valor Empenhado"]))
        amend_file_total += paid
        a = amend[(r["Nome do Autor da Emenda"].strip(), r["Tipo de Emenda"].strip())]
        a["paid"] += paid; a["committed"] += comm; a["count"] += 1
        amend_type[r["Tipo de Emenda"].strip()] += paid
if CONTROL == "output": amend_type[next(iter(amend_type))] -= 1
authors = sorted(({"author": k[0], "type": k[1], "paid": R(v["paid"]), "committed": R(v["committed"]), "amendments": v["count"]}
                  for k, v in amend.items()), key=lambda t: -t["paid"])
indiv = collections.defaultdict(lambda: collections.defaultdict(int))  # one row per parliamentarian, both individual types
for (name, kind), v in amend.items():
    if kind.startswith("Emenda Individual"):
        for k in ("paid", "committed", "count"): indiv[name][k] += v[k]
individual_authors = sorted(({"author": n, "paid": R(v["paid"]), "committed": R(v["committed"]), "amendments": v["count"]}
                             for n, v in indiv.items()), key=lambda t: -t["paid"])

diff = {"payroll_branches_minus_independent_pass": sum(pay.values()) - indep_pay,
        "payroll_by_kind_minus_independent_pass": sum(sum(x.values()) for x in pay_kind.values()) - indep_pay,
        "quota_months_minus_file_total": sum(ceap.values()) - ceap_total_file,
        "amendments_by_type_minus_file_total": sum(amend_type.values()) - amend_file_total,
        "amendments_by_author_minus_file_total": sum(c(a["paid"]) for a in authors) - amend_file_total}
import openpyxl
_rows = list(openpyxl.load_workbook(P("pipelines/series/cache/union/serie_historica_ago26.xlsx"), read_only=True, data_only=True)["1.1"].iter_rows(values_only=True))
_head = next(r for r in _rows if r and r[0] == "Discriminação")
_line = next(r for r in _rows if r and isinstance(r[0], str) and r[0].strip().startswith("4.2") and "Pessoal" in r[0])
rtn_personnel = {d.month: v * 1e6 for d, v in zip(_head[1:], _line[1:]) if hasattr(d, "year") and d.year == YEAR and v is not None}
PAYROLL_RTN_BAND = (0.970, 1.000)
payroll_over_rtn = {f"{YEAR}-{m:02d}": round(pay_month[m] / 100 / rtn_personnel[m], 4) for m in range(M0, M1 + 1)}
payroll_off_band = {m: r for m, r in payroll_over_rtn.items() if not (PAYROLL_RTN_BAND[0] <= r <= PAYROLL_RTN_BAND[1])}
check = {"unit": "centavos", "assembly_differences": diff, "payroll_over_rtn_line_4_2_by_month": payroll_over_rtn,
         "payroll_rtn_band": list(PAYROLL_RTN_BAND), "payroll_off_band": payroll_off_band,
         "passed": all(v == 0 for v in diff.values()) and not payroll_off_band, "control_run": bool(CONTROL)}
out = {"title": f"Federal section numbers, {MONTHS[0]} to {MONTHS[-1]}", "months": MONTHS, "collected_at": "2026-10-02",
       "union_accounts": union, "federal_payroll_by_branch": payroll, "federal_payroll_total": R(sum(pay.values())),
       "federal_payroll_by_kind": {k: {b: R(v) for b, v in sorted(x.items(), key=lambda t: -t[1]) if v} for k, x in pay_kind.items()},
       "federal_payroll_kind_totals": {k: R(sum(x.values())) for k, x in pay_kind.items()},
       "executive_civil_servants": servants, "congress_cost": congress, "parliamentary_quota": quota,
       "amendments": {"year": YEAR, "paid_total": R(amend_file_total), "paid_by_type": {k: R(v) for k, v in sorted(amend_type.items(), key=lambda t: -t[1])},
                      "authors": authors, "individual_authors": individual_authors, "individual_authors_count": len(individual_authors),
                      "file_generated": "2026-10-01", "note": "Amendments are summed by year of the amendment, as the Portal file publishes them; paid = Valor Pago (no month column in this file)."},
       "check": check,
       "sources": {"tesouro_base": {"url": dt["url"], "last_modified": dt.get("resource_last_modified")},
                   "union": "data/series/union.json", "servants": sv["source"],
                   "chamber_quota": f"https://www.camara.leg.br/cotas/Ano-{YEAR}.csv.zip",
                   "senate_quota": f"https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_{YEAR}.csv",
                   "amendments": "https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO",
                   "amendments_columns": amend_cols}}
print(json.dumps({"check": check, "payroll": payroll, "congress": {h: (v["total"], v["per_member_month"]) for h, v in congress.items()},
                  "quota": {h: v["total"] for h, v in quota.items()}, "amend_types": out["amendments"]["paid_by_type"],
                  "top_authors": authors[:6], "union": {k: union[k] for k in ("primary_result", "nominal_result", "gross_debt_brl")}}, ensure_ascii=False, indent=1))
if not check["passed"]:
    raise SystemExit("CHECK FAILED")  # nothing is written when the check fails
if not CONTROL:
    json.dump(out, open(P("data/federal", "federal-section.json"), "w"), ensure_ascii=False, indent=1)
