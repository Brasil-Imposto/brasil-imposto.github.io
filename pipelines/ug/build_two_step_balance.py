"""State balance with the Union under the two-step rule (GD16, D45, D114, D115), for any run of months of one year.

Rule, the same for the 27 states:
  1. when the expense-execution file says where the money was applied (UF of the budget localizer), that UF counts;
  2. otherwise the money belongs to the Union, not to the state of the paying unit (D114). National programs paid by headquarters units, in Brasília or
     anywhere (Army, Navy and Air Force payrolls, medicines and vaccines, DNIT, Capes, Auxílio Gás), have no state in the
     localizer. One official per-state split replaces the Union here: the payroll divisions of the former federal territories
     (SIAFI units 201061 Amapá, 201062 Rondônia, 201063 Roraima) pay only the servants of that territory, so they count in it.
     Until 2026-10-06 step 2 was the UF of the paying unit, which put 74% of what "returned" to the DF on national programs;
  3. unemployment insurance (action 00H4) and wage bonus (action 0581) count by the UF of the person who receives them,
     only where an official series by UF exists: the MTE FAT management report, annual, read into
     data/ug/mte-seguro-abono-uf-YYYY_hybrid.json (today only 2024). It is used only for a run over the whole year, as an
     annual block (it has no months). Without it (GD16), the part with a UF in the localizer
     counts there, month by month, and the rest stays without a state.
Other branches (Legislative, Judiciary, MPU, DPU) have no localizer in the Tesouro base: they count by the seat of the unit,
with the same unit rules as the first unit-based balance (D41). Transfers, Bolsa Família, INSS and BPC keep counting by
destination, as in D41; the FCDF counts in the DF, read from the Tesouro base (all rows of unit 73901) so that 2019 to 2021
have it too. Debt interest and amortization stay out.

Usage: .venv/bin/python pipelines/ug/build_two_step_balance.py 2026 1 7 [--control | --control=input-row | --control=input-revenue]
Inputs (all already in the project; nothing is downloaded):
  data/ug/cache/despug_YYYYMM.json.gz        Portal da Transparência, expense execution, Executive (agg_spending_ug.py)
  data/ug/cache/dtt_monthly_YYYY.json.gz     Tesouro base "Despesas e Transferências Totais da União" (agg_dtt_monthly.py)
  data/ug/siafi_unidades_gestoras_2025-06.csv  SIAFI register of paying units, UF column
  data/series/federal-by-uf-monthly.json, federal-revenue-uf-estimated.json, population.json
  data/ug/mte-seguro-abono-uf-YYYY_hybrid.json  (optional: unemployment insurance and wage bonus by state, MTE)
  data/series/federal-payroll-by-uf.json      (only to cross-check the FCDF where both exist)
Output: data/ug/two-step-balance-YYYY-MM-MM.json (English keys; money in reais with cents)
Union block (D115): what entered the Union with no state (Receita national total minus the 27 states) and what the Union
paid with no state (RTN line 2 plus line 4, from data/ug/rtn-lines-monthly.json, minus the 27 states), with its parts.
Checks. Conservation, in whole cents: every allocated block (27 states + without state) equals the same block summed
straight from the raw rows. That pass uses the same scope function as the allocation, so it proves nothing is lost or
added on the way, not that the scope is right; the scope bands and the Portal/Tesouro band below check the scope.
Assembly: 27 states + Union = the official total on both sides holds by construction (the Union is the total minus the
states). The real Union check: every named part of what the Union paid is zero or more (a negative part means something
is counted twice) and the unnamed rest is at most 3% of the Union amount (worst real case 2.7%, 2019).
Controls, each must fail: --control takes R$ 0,01 from SP after assembly; --control=input-row reads the largest Portal row of
the middle month twice; --control=input-revenue doubles SC's revenue in the series for the first published month.
"""
import collections, csv, gzip, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
args = [a for a in sys.argv[1:] if not a.startswith("--")]
YEAR, M0, M1 = int(args[0]), int(args[1]), int(args[2])
CONTROL = next(((a.split("=", 1)[1] if "=" in a else "output") for a in sys.argv[1:] if a.startswith("--control")), None)
assert CONTROL in (None, "output", "input-row", "input-revenue"), CONTROL
MONTHS = [f"{YEAR}-{m:02d}" for m in range(M0, M1 + 1)]
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
       "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
FCDF_UO = "73901"
# Counted by destination from their own series, so they stay out of the federal spending: the RGPS fund (INSS) by name,
# because its unit code changed with the ministries (25917 in 2019, 40904 in 2023, 33904 in 2024); Bolsa Família (8442)
# and Auxílio Brasil (21DP, 2021-11 to 2023-02), which the MDS series carries; BPC (00IN, 00H5).
INSS_FUND = lambda name: "REGIME GERAL" in name
BOLSA_FAMILIA_ACTIONS = {"8442", "21DP"}
BPC_ACTIONS = {"00IN", "00H5"}
MILITARY_ACTIONS = {"2867", "214H", "0179", "218J", "218K", "00QD"}
PERSON_BENEFIT_ELEMENTS = {"06", "10", "18", "20", "48", "59"}
SD_ABONO = {"00H4": "unemployment_insurance", "0581": "wage_bonus"}
# Benefits paid to people across the country by one central unit, with no UF in most rows: the same case as unemployment
# insurance and wage bonus (GD16), so the same treatment: the UF of the localizer when present, otherwise without a state.
# Emergency aid 2020-2021 (00S4, 00SF, 00SI) and the job-retention benefit BEm (21C2) would otherwise land in the DF.
def central_program(ac, name):
    if ac in SD_ABONO: return SD_ABONO[ac]
    if "AUXILIO EMERGENCIAL" in name and "OPERACIONALIZACAO" not in name and "ACOLHIMENTO" not in name: return "emergency_aid"
    if "MANUTENCAO DO EMPREGO E DA RENDA" in name: return "job_retention_benefit"
    return None
# Audit of 2026-10-06 (state balances, item 11): one payment of December 2019 to Petrobras for the revision of the
# cessão onerosa contract (action 00RY, unit 32101, function 28, no UF in the localizer) is money paid to a company, not
# spending on the people of the state of the paying unit (the DF). Only this payment stays without a state; the other
# function-28 lines without a localizer are listed for a decision in the audit fixes log.
NO_STATE_PAYMENTS = {("2019-12", "00RY"): "no_state:payment_to_company_cessao_onerosa"}
# D114: rows with no UF in the localizer are the Union's; the ex-territory payroll divisions are the one official split by state.
EX_TERRITORY_DIVISIONS = {"201061": "AP", "201062": "RO", "201063": "RR"}
UNION_NO_STATE = "no_state:union_no_state_in_localizer"
POWER_OF_ORGAO = {"1000": "legislative", "2000": "legislative", "3000": "legislative", "29000": "dpu", "34000": "mpu"}
POWER_OF_ORGAO.update({str(c): "judiciary" for c in range(10000, 18000, 1000)})
DF_UNITS = {"1101", "2101", "3101", "10101", "11101", "14101", "15101", "16101", "17101", "34103", "34105", "1901", "15126", "16103"}
TRF_SEAT = {1: "DF", 2: "RJ", 3: "SP", 4: "RS", 5: "PE", 6: "MG"}
TRT_SEAT = {1: "RJ", 2: "SP", 3: "MG", 4: "RS", 5: "BA", 6: "PE", 7: "CE", 8: "PA", 9: "PR", 10: "DF", 11: "AM", 12: "SC",
            13: "PB", 14: "RO", 15: "SP", 16: "MA", 17: "ES", 18: "GO", 19: "AL", 20: "SE", 21: "RN", 22: "PI", 23: "MT", 24: "MS"}
TRE_UF = {"ACRE": "AC", "ALAGOAS": "AL", "AMAZONAS": "AM", "AMAPA": "AP", "BAHIA": "BA", "CEARA": "CE", "DIST. FEDERAL": "DF",
          "ESPIRITO SANTO": "ES", "GOIAS": "GO", "MARANHAO": "MA", "MINAS GERAIS": "MG", "MATO G. DO SUL": "MS",
          "MATO GROSSO": "MT", "PARA": "PA", "PARAIBA": "PB", "PERNAMBUCO": "PE", "PIAUI": "PI", "PARANA": "PR",
          "RIO DE JANEIRO": "RJ", "RIO G.DO NORTE": "RN", "RONDONIA": "RO", "RORAIMA": "RR", "RIO G. DO SUL": "RS",
          "SANTA CATARINA": "SC", "SERGIPE": "SE", "SAO PAULO": "SP", "TOCANTINS": "TO"}
NATIONAL_UNITS = {"12101", "13101", "34101", "34102", "34104", "29101"}  # nationwide units: paying UG unknown in this base
SUBS = ["civil_active_and_other", "civil_retirees_and_pensions", "military", "operating_costs", "investment",
        "benefits_to_people", "special_charges", "economic_subsidies"]
c = lambda v: int(round(v * 100))  # reais -> whole cents (inputs already carry two decimals)
R = lambda cents: round(cents / 100, 2)

reg = {}
with open(P("data/ug/siafi_unidades_gestoras_2025-06.csv"), encoding="utf-8") as f:
    for x in csv.reader(f):
        x = [s.strip() for s in x]
        if len(x) >= 10 and x[0] != "UG":
            reg[x[0]] = x[3]

def ug_uf(ug):
    u = reg.get(ug)
    if u is None: return "no_state:ug_not_in_register"
    if u == "EX": return "no_state:ug_abroad"
    return u if u in UFS else "no_state:ug_without_valid_uf"

def sub_of(g, fn, ac, el):
    if g == "1":
        return "military" if ac in MILITARY_ACTIONS else "civil_retirees_and_pensions" if el in ("01", "03") else "civil_active_and_other"
    if fn == "28": return "special_charges"
    if el == "45": return "economic_subsidies"
    if g == "3" and el in PERSON_BENEFIT_ELEMENTS: return "benefits_to_people"
    return "operating_costs" if g == "3" else "investment"

UO_NAMES, AC_NAMES = {}, {}
in_scope = lambda g, mo, uo, ac: (g in ("1", "3", "4") and mo == "90" and uo != FCDF_UO and not INSS_FUND(UO_NAMES.get(uo, ""))
                                  and ac not in BOLSA_FAMILIA_ACTIONS | BPC_ACTIONS)

MTE_FILE = P("data/ug", f"mte-seguro-abono-uf-{YEAR}_hybrid.json")
MTE = json.load(open(MTE_FILE)) if os.path.exists(MTE_FILE) and (M0, M1) == (1, 12) else None  # dropped below if a month is broken
MTE_KEY = {"unemployment_insurance": "seguro_desemprego", "wage_bonus": "abono_salarial"}
sda_portal = collections.defaultdict(int)                      # program -> cents in the Portal (scope), whatever the step
sda_mte_month = collections.defaultdict(int)                   # month -> cents of the two programs the MTE year replaces

# ---------- Executive, Portal, month by month
exe = {m: collections.defaultdict(int) for m in MONTHS}        # month -> (dest, sub) -> cents
how = collections.defaultdict(int)                             # (dest, "localizer" | "ex_territory_division" | "union") -> cents
moved = collections.defaultdict(int)                           # (UF of the paying unit, kind) -> cents the earlier step 2 put there
sda = collections.defaultdict(int)                             # (program, dest) -> cents
indep_exec = {m: 0 for m in MONTHS}                            # independent pass: same scope, summed without allocation
excluded_checks = collections.defaultdict(int)                 # what the scope leaves out, to compare with the series
excluded_by_month = collections.defaultdict(lambda: collections.defaultdict(int))
portal_meta = {}
for m in MONTHS:
    fn_ = P("data/ug/cache", f"despug_{m.replace('-', '')}.json.gz")
    d = json.load(gzip.open(fn_, "rt"))
    if CONTROL == "input-row" and m == MONTHS[len(MONTHS) // 2]:  # one Portal row read twice, as a join or download bug would
        d["agg"].append(list(max((r for r in d["agg"] if in_scope(r[2], r[3], r[7], r[10])), key=lambda r: r[12] + r[13])))
    portal_meta[m] = {"file": d["file"], "rows": d["rows"], "zip_bytes": d["zip_bytes"], "url": d["url"]}
    UO_NAMES.update(d["names"]["uo"]); AC_NAMES.update(d["names"]["acao"])
    for row in d["agg"]:
        uf, lc, g, mo, osup, osub, ug, uo, fn, sf, ac, el, paid, rp, liq = row
        if g in ("1", "3", "4") and mo == "90":
            for k, hit in (("fcdf_in_portal", uo == FCDF_UO), ("bolsa_familia_in_portal", ac in BOLSA_FAMILIA_ACTIONS),
                           ("bpc_in_portal", ac in BPC_ACTIONS), ("inss_in_portal", INSS_FUND(UO_NAMES.get(uo, "")))):
                if hit: excluded_by_month[m][k] += c(paid + rp); break
            if uo == FCDF_UO: excluded_checks["fcdf_in_portal"] += c(paid + rp)
            elif ac in BOLSA_FAMILIA_ACTIONS: excluded_checks["bolsa_familia_in_portal"] += c(paid + rp)
            elif ac in BPC_ACTIONS: excluded_checks["bpc_in_portal"] += c(paid + rp)
            elif INSS_FUND(UO_NAMES.get(uo, "")): excluded_checks["inss_in_portal"] += c(paid + rp)
    # independent pass: scope total straight from the rows
    indep_exec[m] = sum(c(r[12] + r[13]) for r in d["agg"] if in_scope(r[2], r[3], r[7], r[10]))  # valor pago + restos a pagar pagos
    for uf, lc, g, mo, osup, osub, ug, uo, fn, sf, ac, el, paid, rp, liq in d["agg"]:
        if not in_scope(g, mo, uo, ac): continue
        v = c(paid + rp)
        prog = central_program(ac, AC_NAMES.get(ac, ""))
        if prog:
            sda_portal[prog] += v
            if MTE and prog in SD_ABONO.values():
                sda_mte_month[m] += v
                continue  # replaced below by the MTE annual series (step 3)
            dest = uf if uf in UFS else "no_state:no_official_series_by_state"
            sda[(prog, dest)] += v
            exe[m][(dest, prog)] += v
            continue
        k = sub_of(g, fn, ac, el)
        if uf in UFS: dest, h = uf, "localizer"
        elif ug in EX_TERRITORY_DIVISIONS: dest, h = EX_TERRITORY_DIVISIONS[ug], "ex_territory_division"
        elif (m, ac) in NO_STATE_PAYMENTS and fn == "28": dest, h = NO_STATE_PAYMENTS[(m, ac)], "union"
        else:
            dest, h = UNION_NO_STATE, "union"
            moved[(ug_uf(ug), k)] += v
        exe[m][(dest, k)] += v
        how[(dest, h)] += v

# ---------- other branches, Tesouro base, month by month
dt = json.load(gzip.open(P("data/ug/cache", f"dtt_monthly_{YEAR}.json.gz"), "rt"))
oth = {m: collections.defaultdict(int) for m in MONTHS}
indep_oth = {m: 0 for m in MONTHS}
dtt_exec = {m: 0 for m in MONTHS}
dtt_exec_no_court = {m: 0 for m in MONTHS}  # without court-ordered payments, which only the Tesouro base carries
# court-ordered payments by the Tesouro's own RTN category ("Sentenças Judiciais e Precatórios", "Sentenças e Precatórios"),
# not by action code: in 2026-03 R$ 25,9 bi of precatórios came under a new action (00WU)
COURT_ORDERED = lambda cat: "Sentenças" in cat or "Sentencas" in cat
dtt_months = sorted({r[0] for r in dt["agg"]})
UO_NAMES.update({k: v for k, v in dt["names"]["uo"].items() if k not in UO_NAMES and v})
for mon, org, uo, g, mo, ac, cat, v in dt["agg"]:
    m = f"{YEAR}-{mon:02d}"
    if m not in oth: continue
    if org not in POWER_OF_ORGAO:
        if in_scope(g, mo, uo, ac):
            dtt_exec[m] += c(v)
            if not COURT_ORDERED(cat): dtt_exec_no_court[m] += c(v)
        continue
    if not (g in ("1", "3", "4") and mo == "90"): continue
    indep_oth[m] += c(v)
    name = dt["names"]["uo"][uo]
    if uo in DF_UNITS: u = "DF"
    elif "REGIONAL ELEITORAL" in name: u = TRE_UF[re.sub(r"^TRIBUNAL REGIONAL ELEITORAL D[OAE]S? ", "", name).strip()]
    elif re.search(r"REGIONAL FEDERAL DA (\d)A\. REGIAO", name): u = TRF_SEAT[int(re.search(r"REGIONAL FEDERAL DA (\d)A\. REGIAO", name).group(1))]
    elif re.search(r"TRABALHO DA (\d+)A\. REGIAO", name): u = TRT_SEAT[int(re.search(r"TRABALHO DA (\d+)A\. REGIAO", name).group(1))]
    elif uo in NATIONAL_UNITS: u = "no_state:nationwide_unit"
    else: raise SystemExit(f"unit without a rule: {uo} {name}")
    oth[m][(u, POWER_OF_ORGAO[org])] += c(v)

# A Portal month whose total is far from the Tesouro base in the same scope, court-ordered payments aside (only the
# Tesouro carries them: R$ 61,6 bi of precatórios in 2023-12), is a broken file: 2025-06 was regenerated by the CGU on
# 2026-10-01 with every value zeroed (an earlier version carried twice the payroll). Elsewhere the ratio is 1.00 month
# after month. A broken month is left out on both sides of the balance and listed, never computed.
broken_months = {m: {"portal": R(indep_exec[m]), "tesouro_without_court_ordered": R(dtt_exec_no_court[m])} for m in MONTHS
                 if dtt_exec_no_court[m] and not (0.9 <= indep_exec[m] / dtt_exec_no_court[m] <= 1.1)}
MONTHS = [m for m in MONTHS if m not in broken_months]
# Measured on the runs of 2019 to 2026: outside the broken months the Portal is 1.000 to 1.015 times the Tesouro base in the
# same scope. A month outside this band that is not a broken file means a row read twice or lost on one side.
PORTAL_TESOURO_BAND = (0.995, 1.025)
ratio_off_band = {m: round(indep_exec[m] / dtt_exec_no_court[m], 4) for m in MONTHS if dtt_exec_no_court[m]
                  and not (PORTAL_TESOURO_BAND[0] <= indep_exec[m] / dtt_exec_no_court[m] <= PORTAL_TESOURO_BAND[1])}

# step 3 with the MTE series: the year's Portal total of each program goes to the states by the MTE values; what the MTE
# does not place in a state, and the gap between the Portal and the MTE, stay without a state (as in the 2024 hybrid run)
mte_annual = collections.defaultdict(int)                      # (dest, program) -> cents, annual block
assert not (MTE and broken_months), "an MTE year with a broken Portal month needs a decision"
if MTE:
    for prog, key in MTE_KEY.items():
        s = MTE["series"][key]
        placed = 0
        for u in UFS:
            mte_annual[(u, prog)] = c(s["uf"][u]); placed += c(s["uf"][u])
        mte_annual[("no_state:mte_not_in_a_state_or_portal_gap", prog)] = sda_portal[prog] - placed

# FCDF from the Tesouro base: every row of unit 73901, valor pago (PAGAMENTOS_TOTAIS)
fcdf_m = {m: 0 for m in MONTHS}
for mon, org, uo, g, mo, ac, cat, v in dt["agg"]:
    m = f"{YEAR}-{mon:02d}"
    if m in fcdf_m and uo == FCDF_UO: fcdf_m[m] += c(v)

# ---------- revenue (sent) and the destination-based flows, from the series
fm = json.load(open(P("data/series/federal-by-uf-monthly.json")))
est = json.load(open(P("data/series/federal-revenue-uf-estimated.json")))
fp = json.load(open(P("data/series/federal-payroll-by-uf.json")))
pop = json.load(open(P("data/series/population.json")))
ix = {m: fm["months"].index(m) for m in MONTHS}
ixe = {m: est["months"].index(m) for m in MONTHS if m in est["months"]}
ixp = {m: fp["months"].index(m) for m in MONTHS if m in fp["months"]}
status = {m: fm["national"]["federal_revenue_month_status"][ix[m]] for m in MONTHS}
broken = lambda m: "uf_attribution_broken" in status[m]
for m in MONTHS:
    assert status[m] != "not_published", f"{m}: revenue by state not published"
    assert not broken(m) or m in ixe, f"{m}: broken split and no estimate"
if CONTROL == "input-revenue":  # SC's revenue doubled in the series in the first published month of the run
    _m = next(m for m in MONTHS if not broken(m))
    fm["uf"]["SC"]["federal_revenue"]["total"][ix[_m]] *= 2

def revenue(u, m):
    if broken(m): return c(est["uf"][u]["total"][ixe[m]]), "estimated"
    return c(fm["uf"][u]["federal_revenue"]["total"][ix[m]]), "published"

FLOWS = ["transfers", "bolsa_familia", "inss", "bpc", "fcdf"]
def flow(u, m, k):
    if k == "fcdf": return fcdf_m[m] if u == "DF" else 0
    x = fm["uf"][u]
    v = x["transfers"]["total"][ix[m]] if k == "transfers" else x[k][ix[m]]
    assert v is not None, (u, m, k)
    return c(v)

# Independent pass over the Receita file itself (data/df/arrecadacao-estado.csv, same bytes as the URL on 2026-10-02),
# in exact decimals: some columns carry fractions of a cent, so each state-month is compared after rounding to cents.
from decimal import Decimal, ROUND_HALF_EVEN
MES = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
       "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}
def dec(x):
    x = x.strip()
    if not x: return Decimal(0)
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", x): x = x.replace(".", "")
    return Decimal(x.replace(",", "."))
receita_file = collections.defaultdict(Decimal)
with open(P("data/df/arrecadacao-estado.csv"), encoding="latin1") as f:
    rr = csv.reader(f, delimiter=";"); H = next(rr)
    for r in rr:
        m = f"{r[0]}-{MES[r[1]]:02d}"
        if m in ix and r[2] in UFS: receita_file[(r[2], m)] += sum((dec(x) for x in r[3:]), Decimal(0))
receita_file_mills = {k: int((v * 1000).quantize(Decimal(1), rounding=ROUND_HALF_EVEN)) for k, v in receita_file.items()}
# the series value must be the file's exact value rounded to the cent: within half a cent (5 mills); at an exact
# half-cent tie (AC, MA, RR in 2026-02 and RO in 2026-06) either side is a correct rounding
off_by_more_than_half_cent = lambda u, m: abs(revenue(u, m)[0] * 10 - receita_file_mills[(u, m)]) > 5

# ---------- assembly
PROGRAMS = list(SD_ABONO.values()) + ["emergency_aid", "job_retention_benefit"]
BRANCHES = ["legislative", "judiciary", "mpu", "dpu"]
def pop_of(u):  # the run's year, or the nearest year IBGE published (there is no 2023 estimate)
    by = {int(y): v for y, v in pop["uf"][u]["population"].items() if v is not None}
    return by[min(by, key=lambda y: (abs(y - YEAR), -y))]
monthly, period = {}, {}
for u in UFS:
    row = {k: [] for k in ["sent", "sent_kind"] + FLOWS + ["executive", "central_benefits_localized", "other_branches", "returned", "balance"]}
    row["executive_by_kind"] = {k: [] for k in SUBS}; row["other_branches_by_branch"] = {k: [] for k in BRANCHES}
    tot = collections.defaultdict(int)
    for m in MONTHS:
        s, kind = revenue(u, m)
        fl = {k: flow(u, m, k) for k in FLOWS}
        kinds = {k: exe[m].get((u, k), 0) for k in SUBS}
        sdl = sum(exe[m].get((u, k), 0) for k in PROGRAMS)
        brs = {k: oth[m].get((u, k), 0) for k in BRANCHES}
        ex, ot = sum(kinds.values()), sum(brs.values())
        ret = sum(fl.values()) + ex + sdl + ot
        row["sent"].append(R(s)); row["sent_kind"].append(kind)
        for k in FLOWS: row[k].append(R(fl[k])); tot[k] += fl[k]
        for k in SUBS: row["executive_by_kind"][k].append(R(kinds[k])); tot["kind:" + k] += kinds[k]
        for k in BRANCHES: row["other_branches_by_branch"][k].append(R(brs[k])); tot["branch:" + k] += brs[k]
        row["executive"].append(R(ex)); row["central_benefits_localized"].append(R(sdl)); row["other_branches"].append(R(ot))
        row["returned"].append(R(ret)); row["balance"].append(R(s - ret))
        tot["sent"] += s; tot["returned"] += ret; tot["exec"] += ex; tot["sdl"] += sdl; tot["oth"] += ot
    mte_u = {k: mte_annual.get((u, k), 0) for k in PROGRAMS}
    tot["returned"] += sum(mte_u.values())
    monthly[u] = row
    n = pop_of(u)
    bal = tot["sent"] - tot["returned"]
    period[u] = {"population": n, "sent": R(tot["sent"]),
                 "sent_estimated_months": [m for m in MONTHS if broken(m)],
                 "returned": R(tot["returned"]),
                 "returned_parts": {**{k: R(tot[k]) for k in FLOWS}, "federal_spending_executive": R(tot["exec"]),
                                    "central_benefits_localized": R(tot["sdl"]),
                                    "unemployment_and_wage_bonus_mte": R(sum(mte_u.values())),
                                    "federal_spending_other_branches": R(tot["oth"])},
                 "executive_by_kind": {k: R(tot["kind:" + k]) for k in sorted(SUBS, key=lambda k: -tot["kind:" + k])},
                 "unemployment_and_wage_bonus_mte": {k: R(v) for k, v in mte_u.items()},
                 "other_branches_by_branch": {k: R(tot["branch:" + k]) for k in sorted(BRANCHES, key=lambda k: -tot["branch:" + k])},
                 "executive_by_localizer": R(how.get((u, "localizer"), 0)),
                 "executive_by_ex_territory_division": R(how.get((u, "ex_territory_division"), 0)),
                 "executive_moved_to_union_d114": R(sum(v for (pu, k), v in moved.items() if pu == u)),
                 "balance": R(bal), "balance_per_person_month": round(bal / 100 / n / len(MONTHS), 2)}

if CONTROL == "output":  # one cent goes missing from SP after assembly, on both sides; the checks below must catch both
    receita_file_mills[("SP", MONTHS[-1])] += 10
    period["SP"]["returned_parts"]["federal_spending_executive"] = R(c(period["SP"]["returned_parts"]["federal_spending_executive"]) - 1)
    period["SP"]["sent"] = R(c(period["SP"]["sent"]) - 1)

# ---------- checks, whole cents
def no_state(blocks):
    out = collections.defaultdict(int)
    for m in MONTHS:
        for (dest, k), v in blocks[m].items():
            if dest not in UFS: out[f"{dest}|{k}"] += v
    return out
ns_exec, ns_oth = no_state(exe), no_state(oth)
for (dest, k), v in mte_annual.items():
    if dest not in UFS: ns_exec[f"{dest}|{k}"] += v
part = lambda k: sum(c(period[u]["returned_parts"][k]) for u in UFS)
sum_uf_exec = part("federal_spending_executive") + part("central_benefits_localized") + part("unemployment_and_wage_bonus_mte")
sum_uf_oth = part("federal_spending_other_branches")
national_rev = {m: c(fm["national"]["federal_revenue_total_receita"][ix[m]]) for m in MONTHS}
# Revenue: published months are checked state by state against the Receita file (above); an estimated month must add up
# to the Receita national total (the estimate is scaled to it). What the Receita did not put in any state is national
# total minus the states, in exact cents (the series stores it as a float, off by up to a cent per month: reported only).
sum_month = {m: sum(revenue(u, m)[0] for u in UFS) for m in MONTHS}
pub = [m for m in MONTHS if not broken(m)]
estm = [m for m in MONTHS if broken(m)]
unattributed = {m: national_rev[m] - sum_month[m] for m in MONTHS}
na = fm["national"]["federal_revenue_not_attributed_to_any_uf"]
sum_uf_sent = sum(c(period[u]["sent"]) for u in UFS)
sum_uf_bal = sum(c(period[u]["balance"]) for u in UFS)
sum_uf_ret = sum(c(period[u]["returned"]) for u in UFS)
sum_uf_flows = sum(part(k) for k in FLOWS)
series_flows = sum(flow(u, m, k) for u in UFS for m in MONTHS for k in FLOWS)
diff = {
    "executive_states_plus_no_state_minus_independent_pass": sum_uf_exec + sum(ns_exec.values()) - sum(indep_exec[m] for m in MONTHS),
    "other_branches_states_plus_no_state_minus_independent_pass": sum_uf_oth + sum(ns_oth.values()) - sum(indep_oth[m] for m in MONTHS),
    "sent_published_state_months_off_the_receita_file_by_more_than_half_a_cent": sum(1 for u in UFS for m in pub if off_by_more_than_half_cent(u, m)),
    # the estimate stores each state rounded to the cent: 27 roundings move a month's sum by at most 13.5 cents
    "sent_estimated_months_off_the_receita_national_total_by_more_than_27_half_cents": sum(1 for m in estm if abs(sum_month[m] - national_rev[m]) > 13),
    "sent_states_minus_months": sum_uf_sent - sum(sum_month.values()),
    "flows_states_minus_series": sum_uf_flows - series_flows,
    "returned_minus_parts": sum_uf_ret - sum_uf_flows - sum_uf_exec - sum_uf_oth,
    "balance_minus_sent_plus_returned": sum_uf_bal - sum_uf_sent + sum_uf_ret,
}
# The scope check the cent check cannot do: what the scope leaves out of the Portal (because it is counted by destination
# from its own series) must be about the size of that series. In 2019 the INSS fund had another unit code, nothing was
# left out, and the benefits were counted twice (DF at -R$ 21.687 per person per month) while every cent check passed.
# Bands: the worst ratio of the runs of 2019 to 2026 plus a margin (INSS 1.128 to 1.186, Bolsa Família 0.976 to 1.042, BPC
# 1.034 to 1.080, FCDF 0.938 to 0.989).
BANDS = {"inss": ("inss_in_portal", 1.10, 1.22), "bolsa_familia": ("bolsa_familia_in_portal", 0.95, 1.07),
         "bpc": ("bpc_in_portal", 1.01, 1.11), "fcdf": ("fcdf_in_portal", 0.91, 1.02)}
kept = set(MONTHS)
excluded_kept = collections.defaultdict(int)
for m in kept:
    for k, v in excluded_by_month[m].items(): excluded_kept[k] += v
# In the months when Bolsa Família families got emergency aid instead (series flag bolsa_familia_auxilio_emergencial),
# the residual emergency aid of 2020-09 to 2020-12 was paid through the Bolsa Família action (8442): the Portal carries
# about R$ 2,3 bi a month more than the MDS series. That excess is emergency aid: without a state, like the rest of it.
AE_SUBSTITUTION = {f"2020-{i:02d}" for i in range(4, 13)} | {f"2021-{i:02d}" for i in range(4, 11)}
bf_excess_as_emergency_aid = {m: max(0, excluded_by_month[m]["bolsa_familia_in_portal"] - sum(flow(u, m, "bolsa_familia") for u in UFS))
                              for m in MONTHS if m in AE_SUBSTITUTION}
excluded_kept["bolsa_familia_in_portal"] -= sum(bf_excess_as_emergency_aid.values())
scope_ratio = {k: round(excluded_kept[col] / max(sum(flow(u, m, k) for u in UFS for m in MONTHS), 1), 3) for k, (col, lo, hi) in BANDS.items()}
scope_out_of_band = {k: r for k, r in scope_ratio.items() if not (BANDS[k][1] <= r <= BANDS[k][2])}
# ---------- Union block (D115): 27 states + Union = the official total, on both sides, in whole cents.
# Sent: the Receita national total; the Union is what the Receita file puts in no state (month by month, independent of
# the period dict). Returned: RTN line 2 (transfers by revenue sharing) plus line 4 (primary spending), the total "As contas
# do Brasil" uses; the Union is that total minus the 27 states summed from the raw blocks (flows, Portal, Tesouro, MTE).
rtn = json.load(open(P("data/ug/rtn-lines-monthly.json")))
rix = {m: rtn["months"].index(m) for m in MONTHS}
rline = lambda k, m: c(rtn["lines"][k][rix[m]])
official_ret = {m: rline("transfers_to_subnationals", m) + rline("primary_spending", m) for m in MONTHS}
states_raw = {m: sum(flow(u, m, k) for u in UFS for k in FLOWS) + sum(v for (d, k), v in exe[m].items() if d in UFS)
              + sum(v for (d, k), v in oth[m].items() if d in UFS) for m in MONTHS}
mte_states = sum(v for (d, k), v in mte_annual.items() if d in UFS)
union_sent = sum(unattributed[m] for m in MONTHS)
union_ret = sum(official_ret.values()) - sum(states_raw.values()) - mte_states
states_parts_ret = sum_uf_flows + sum_uf_exec + sum_uf_oth
# Assembly checks: they hold by construction (the Union is the official total minus the states), so they guard the
# assembly only; what explains the Union amount is checked below with its parts.
diff["assembly_union_block_sent_states_plus_union_minus_receita_total"] = sum(c(period[u]["sent"]) for u in UFS) + union_sent - sum(national_rev.values())
diff["assembly_union_block_returned_states_plus_union_minus_rtn_total"] = states_parts_ret + union_ret - sum(official_ret.values())
sflow = lambda k: sum(flow(u, m, k) for u in UFS for m in MONTHS)
# Rows of the Tesouro base inside the RTN (any category but "nan"/"N/A") that no state flow of the site carries: financial
# investments (group 5: constitutional funds lent by the regional banks, capitalizations), payments to private entities,
# international bodies and abroad (modalities 50, 60, 67, 70, 72, 80), and transfers to state and city governments
# (modalities 20 to 46 and 71 to 76) beyond what the Portal places in a state.
PRIVATE_OR_ABROAD = {"50", "60", "67", "70", "72", "80"}
PUBLIC_TRANSFER = {"20", "22", "30", "31", "32", "35", "36", "40", "41", "42", "45", "46", "71", "73", "74", "75", "76"}
dtt_rest = collections.defaultdict(lambda: collections.defaultdict(int))
for mon, org, uo, g, mo, ac, cat, v in dt["agg"]:
    m = f"{YEAR}-{mon:02d}"
    if m not in official_ret or cat in ("nan", "N/A"): continue
    if g == "5": dtt_rest[m]["financial_investments"] += c(v)
    elif g in ("1", "3", "4") and mo in PRIVATE_OR_ABROAD: dtt_rest[m]["private_international_abroad"] += c(v)
    elif g in ("1", "3", "4") and mo in PUBLIC_TRANSFER: dtt_rest[m]["public_transfers_tesouro"] += c(v)
ns = lambda blocks, keep: sum(v for m in MONTHS for (d, k), v in blocks[m].items() if d not in UFS and keep(k))
union_parts = {
    "national_programs_executive_no_state_in_localizer": ns(exe, lambda k: k not in PROGRAMS),
    "benefits_paid_by_a_central_unit_without_state": ns(exe, lambda k: k in PROGRAMS) + sum(bf_excess_as_emergency_aid.values())
        + sum(v for (d, k), v in mte_annual.items() if d not in UFS),
    "other_branches_without_state": ns(oth, lambda k: True),
    "tesouro_base_executive_not_in_portal_court_ordered_and_residue": sum(dtt_exec[m] - indep_exec[m] for m in MONTHS),
    "inss_benefits_not_in_the_bulletin_by_state": sum(rline("social_security_benefits", m) for m in MONTHS) - sflow("inss"),
    "bpc_not_in_the_series_by_state": sum(rline("bpc", m) for m in MONTHS) - sflow("bpc"),
    "financial_investments_group_5": sum(dtt_rest[m]["financial_investments"] for m in MONTHS),
    "payments_to_private_entities_international_bodies_and_abroad": sum(dtt_rest[m]["private_international_abroad"] for m in MONTHS),
    "transfers_to_state_and_city_governments_not_placed_in_a_state": sum(dtt_rest[m]["public_transfers_tesouro"] for m in MONTHS) - sflow("transfers"),
}
union_parts["other_payments_without_state_and_differences_between_bases"] = union_ret - sum(union_parts.values())
RESIDUAL_MAX_SHARE = 0.03
union_parts_negative = {k: R(v) for k, v in union_parts.items() if v < 0}
union_residual_share = round(union_parts["other_payments_without_state_and_differences_between_bases"] / union_ret, 4) if union_ret else None
union_explained = not union_parts_negative and union_residual_share is not None and union_residual_share <= RESIDUAL_MAX_SHARE
pop_br = sum(pop_of(u) for u in UFS)
union_block = {
    "sent": {"union": R(union_sent), "states": R(sum(c(period[u]["sent"]) for u in UFS)), "official_total": R(sum(national_rev.values())),
             "official_total_source": "Receita Federal, arrecadação total (Análise da Arrecadação, Tabela III, e série 1994 a 2025)",
             "union_per_person_month": round(union_sent / 100 / pop_br / len(MONTHS), 2)},
    "returned": {"union": R(union_ret), "states": R(states_parts_ret), "official_total": R(sum(official_ret.values())),
                 "official_total_source": "Tesouro Nacional, RTN Tabela 1.1, linha 2 (transferências por repartição de receita) mais linha 4 (despesa total)",
                 "union_per_person_month": round(union_ret / 100 / pop_br / len(MONTHS), 2),
                 "parts": {k: R(v) for k, v in sorted(union_parts.items(), key=lambda t: -t[1])}},
    "population_brazil": pop_br, "months": len(MONTHS)}
moved_by_uf = collections.defaultdict(int)
for (pu, k), v in moved.items(): moved_by_uf[pu] += v
passed = (all(v == 0 for v in diff.values()) and dtt_months[-1] >= M1 and not scope_out_of_band and not ratio_off_band
          and union_explained)
fp_fcdf = {m: c(fp["fcdf"]["total"][ixp[m]]) for m in MONTHS if m in ixp and fp["fcdf"]["total"][ixp[m]] is not None}
check = {"unit": "centavos", "differences": diff, "passed": passed, "control_run": bool(CONTROL),
         "union_parts_negative": union_parts_negative, "union_residual_share": union_residual_share,
         "union_residual_max_share": RESIDUAL_MAX_SHARE, "portal_tesouro_band": list(PORTAL_TESOURO_BAND),
         "portal_tesouro_ratio_off_band": ratio_off_band,
         "unemployment_and_wage_bonus_rule": "MTE annual series by state (step 3)" if MTE else "localizer UF where present, otherwise without a state (no official series by state)",
         "independent_pass_executive": R(sum(indep_exec[m] for m in MONTHS)), "independent_pass_other_branches": R(sum(indep_oth[m] for m in MONTHS)),
         "broken_portal_months_left_out": broken_months,
         "portal_over_tesouro_without_court_ordered_by_month": {m: round(indep_exec[m] / dtt_exec_no_court[m], 3) for m in indep_exec if dtt_exec_no_court[m]},
         "executive_without_state": {k: R(v) for k, v in sorted(ns_exec.items(), key=lambda t: -t[1])},
         "executive_moved_to_union_by_paying_unit_state_d114": {k: R(v) for k, v in sorted(moved_by_uf.items(), key=lambda t: -t[1])},
         "other_branches_without_state": {k: R(v) for k, v in sorted(ns_oth.items(), key=lambda t: -t[1])},
         "revenue_without_state_by_month": {m: R(v) for m, v in unattributed.items()},
         "revenue_without_state_series_float_minus_exact_cents": {m: c(na[ix[m]]) - unattributed[m] for m in pub if na[ix[m]] is not None},
         "receita_national_total": R(sum(national_rev.values())),
         "estimated_months_states_minus_national_cents": {m: sum_month[m] - national_rev[m] for m in estm},
         "tesouro_executive_same_scope": R(sum(dtt_exec[m] for m in MONTHS)),
         "tesouro_minus_portal_executive": R(sum(dtt_exec[m] for m in MONTHS) - sum(indep_exec[m] for m in MONTHS)),
         "tesouro_minus_portal_executive_note": "The Tesouro base carries court-ordered payments (sentenças judiciais) and a residue the Portal file does not; they stay without a state.",
         "fcdf_tesouro_minus_payroll_series_cents": {m: fcdf_m[m] - v for m, v in fp_fcdf.items()},
         "scope_exclusions_found_in_portal": {k: R(v) for k, v in excluded_checks.items()},
         "scope_exclusions_over_series": scope_ratio, "scope_out_of_band": scope_out_of_band,
         "emergency_aid_paid_through_bolsa_familia_action": {m: R(v) for m, v in bf_excess_as_emergency_aid.items() if v},
         "series_same_flows_for_comparison": {k: R(sum(flow(u, m, k) for u in UFS for m in MONTHS)) for k in ("bolsa_familia", "bpc", "inss", "fcdf")}}

ranked = sorted(UFS, key=lambda u: period[u]["balance_per_person_month"])
others = [period[u]["balance_per_person_month"] for u in UFS if u != "DF"]
out = {"title": f"State balance with the Union, two-step rule (GD16), {MONTHS[0]} to {MONTHS[-1]}",
       "rule": "Federal spending: UF of the budget localizer when the file has one; otherwise the Union (D114), except the payroll divisions of the former territories (AP, RO, RR), which count in their state. Unemployment insurance and wage bonus: UF of the localizer when present, otherwise without a state (no official monthly series by state; GD16). Other branches by the seat of the unit. Transfers, Bolsa Família, INSS, BPC and FCDF by destination. Interest and amortization out.",
       "sign": "balance > 0: the state sends more than it receives; balance < 0: it receives more than it sends",
       "months": MONTHS, "revenue_month_status": status, "collected_at": "2026-10-02",
       "check": check, "states": period, "monthly": monthly,
       "unemployment_insurance_and_wage_bonus": {f"{p}|{d}": R(v) for (p, d), v in sorted(sda.items())},
       "unemployment_insurance_and_wage_bonus_without_state_by_month": {m: R(sum(v for (dest, k), v in exe[m].items() if k in SD_ABONO.values() and dest not in UFS)) for m in MONTHS},
       "unemployment_insurance_and_wage_bonus_mte_annual": {f"{d}|{k}": R(v) for (d, k), v in sorted(mte_annual.items())} if MTE else None,
       "fcdf_tesouro_by_month": {m: R(v) for m, v in fcdf_m.items()},
       "union_block": union_block,
       "union_by_month": {m: {"official_revenue": R(national_rev[m]), "official_returned_rtn": R(official_ret[m]),
                              "inss_rtn": R(rline("social_security_benefits", m)), "bpc_rtn": R(rline("bpc", m)),
                              "tesouro_base_executive_not_in_portal": R(dtt_exec[m] - indep_exec[m]),
                              "financial_investments_group_5": R(dtt_rest[m]["financial_investments"]),
                              "private_international_abroad": R(dtt_rest[m]["private_international_abroad"]),
                              "public_transfers_tesouro": R(dtt_rest[m]["public_transfers_tesouro"]),
                              "unemployment_and_wage_bonus_portal_mte_year": R(sda_mte_month[m]) if MTE else None} for m in MONTHS},
       "no_state_by_month": {m: {"executive": R(sum(v for (d, k), v in exe[m].items() if d not in UFS and k not in PROGRAMS)),
                                 "central_benefits": R(sum(v for (d, k), v in exe[m].items() if d not in UFS and k in PROGRAMS) + bf_excess_as_emergency_aid.get(m, 0)),
                                 "central_benefits_by_program": {p: R(sum(v for (d, k), v in exe[m].items() if d not in UFS and k == p) + (bf_excess_as_emergency_aid.get(m, 0) if p == "emergency_aid" else 0)) for p in PROGRAMS},
                                 "other_branches": R(sum(v for (d, k), v in oth[m].items() if d not in UFS)),
                                 "revenue": R(unattributed[m])} for m in MONTHS},
       "rank_most_received_first": ranked,
       "scale_without_df": {"min": min(others), "max": max(others),
                            "df": period["DF"]["balance_per_person_month"],
                            "df_outside": not (min(others) <= period["DF"]["balance_per_person_month"] <= max(others))},
       "sources": {"portal_expense_execution": portal_meta, "tesouro_base": {"url": dt["url"], "last_modified": dt.get("resource_last_modified"), "months_in_file": dtt_months},
                   "series": ["data/series/federal-by-uf-monthly.json", "data/series/federal-revenue-uf-estimated.json",
                              "data/series/federal-payroll-by-uf.json (fcdf)", "data/series/population.json"],
                   "paying_unit_register": "data/ug/siafi_unidades_gestoras_2025-06.csv"}}
print(json.dumps(check, ensure_ascii=False, indent=1))
print("rank:", [(u, period[u]["balance_per_person_month"]) for u in ranked])
print("union block:", json.dumps(union_block, ensure_ascii=False))
if not passed:
    raise SystemExit("CHECK FAILED")  # nothing is written when the check fails
if not CONTROL:
    json.dump(out, open(P("data/ug", f"two-step-balance-{YEAR}-{M0:02d}-{M1:02d}.json"), "w"), ensure_ascii=False, indent=1)
