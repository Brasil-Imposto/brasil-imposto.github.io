"""Build data/series/federal-payroll-by-uf.json: personnel spending of the Uniao (grupo de despesa 1) located in each UF,
monthly from 2019-01, plus the FCDF block and a national check against the Tesouro RTN.

Usage: build_federal_payroll_by_uf.py <workdir>   (needs openpyxl)
Inputs (produced by the two aggregators, see their docstrings):
  <workdir>/cache/desp_YYYYMM.json  agg_payroll_monthly.py     Portal da Transparencia, Execucao da Despesa (Poder Executivo)
  <workdir>/cache/dtt_YYYY.json     agg_union_expense_base.py  Tesouro, Despesas e Transferencias Totais (all Powers)
  pipelines/series/cache/union/serie_historica_ago26.xlsx  RTN serie historica (downloaded by build_union_series.py)
Rules (the research note explains each one):
  value      = paid in the month + restos a pagar paid in the month
  scope      = grupo 1 with modalidade 90 (direct application). Modalidade 91 (employer contributions paid inside the
               federal budget) is reported in the national check and never located; other modalidades go to not_located.
  FCDF       = unidade orcamentaria 73901 is taken out of every total and reported apart (it is already counted in the
               map as fcdf_df_constitutional_fund).
  Executive  = located by the UF of the budget localizer (column UF of the Portal file). Rows without a UF there are
               not_located: the Armed Forces pay from central paying units and the localizer is "Nacional".
  Other Powers (Tesouro base, no localizer): located by the UF of the unidade orcamentaria when the unit works in a
               single UF (Camara, Senado, TCU, tribunais superiores, CNJ, TJDFT, MPDFT and ESMPU in DF; each TRE; each
               TRF at its seat; each TRT whose region is one UF). Units spread over several UFs are not_located.
"""
import collections, glob, json, os, re, sys
from datetime import date
import openpyxl

W = sys.argv[1]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "data", "series", "federal-payroll-by-uf.json")
RTN_FILE = os.path.join(ROOT, "pipelines", "series", "cache", "union", "serie_historica_ago26.xlsx")
RTN_URL = "https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326"
RTN_PAGE = "https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/8"
PORTAL_PAGE = "https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao"
DTT_PAGE = "https://www.tesourotransparente.gov.br/ckan/dataset/despesas-e-transferencias-totais"
COLLECTED = "2026-10-01"

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
       "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
MONTHS = [f"{y}-{m:02d}" for y in range(2019, 2027) for m in range(1, 13) if f"{y}-{m:02d}" <= "2026-08"]
MI = {m: i for i, m in enumerate(MONTHS)}

FCDF_UO = "73901"
MILITARY_ACTIONS = {"2867", "214H", "0179", "218J", "218K", "00QD"}
POWER_OF_ORGAO = {"1000": "legislative", "2000": "legislative", "3000": "legislative", "29000": "dpu", "34000": "mpu"}
POWER_OF_ORGAO.update({str(c): "judiciary" for c in range(10000, 18000, 1000)})
DF_UNITS = {"1101", "2101", "3101", "10101", "11101", "14101", "15101", "16101", "17101", "34103", "34105"}
TRF_SEAT = {1: "DF", 2: "RJ", 3: "SP", 4: "RS", 5: "PE", 6: "MG"}
TRT_SINGLE_UF = {1: "RJ", 2: "SP", 3: "MG", 4: "RS", 5: "BA", 6: "PE", 7: "CE", 9: "PR", 12: "SC", 13: "PB", 15: "SP",
                 16: "MA", 17: "ES", 18: "GO", 19: "AL", 20: "SE", 21: "RN", 22: "PI", 23: "MT", 24: "MS"}
TRT_TWO_UFS = {8: "PA e AP", 10: "DF e TO", 11: "AM e RR", 14: "RO e AC"}
TRE_UF = {"ACRE": "AC", "ALAGOAS": "AL", "AMAZONAS": "AM", "AMAPA": "AP", "BAHIA": "BA", "CEARA": "CE", "DIST. FEDERAL": "DF",
          "DISTRITO FEDERAL": "DF", "ESPIRITO SANTO": "ES", "GOIAS": "GO", "MARANHAO": "MA", "MINAS GERAIS": "MG",
          "MATO G. DO SUL": "MS", "MATO GROSSO DO SUL": "MS", "MATO GROSSO": "MT", "PARA": "PA", "PARAIBA": "PB",
          "PERNAMBUCO": "PE", "PIAUI": "PI", "PARANA": "PR", "RIO DE JANEIRO": "RJ", "RIO G.DO NORTE": "RN",
          "RIO GRANDE DO NORTE": "RN", "RONDONIA": "RO", "RORAIMA": "RR", "RIO G. DO SUL": "RS", "RIO GRANDE DO SUL": "RS",
          "SANTA CATARINA": "SC", "SERGIPE": "SE", "SAO PAULO": "SP", "TOCANTINS": "TO"}

CATEGORIES = {
    "executive_civil_active": "Poder Executivo, pessoal civil ativo (vencimentos, vantagens, contratos temporários e encargos pagos diretamente)",
    "executive_civil_retired": "Poder Executivo, aposentadorias de servidores civis (elemento de despesa 01)",
    "executive_civil_pensioners": "Poder Executivo, pensões civis (elemento de despesa 03)",
    "executive_civil_court_orders_and_prior_years": "Poder Executivo, sentenças judiciais e despesas de exercícios anteriores de pessoal (elementos 91 e 92)",
    "military_active": "Militares ativos pagos pela União (Forças Armadas e ex-territórios)",
    "military_retired": "Militares da reserva e reformados",
    "military_pensioners": "Pensões militares",
    "legislative": "Câmara dos Deputados, Senado Federal e Tribunal de Contas da União (ativos, aposentados e pensionistas)",
    "judiciary": "Poder Judiciário da União (ativos, aposentados e pensionistas)",
    "mpu": "Ministério Público da União (ativos, aposentados e pensionistas)",
    "dpu": "Defensoria Pública da União (ativos, aposentados e pensionistas)",
}
REASONS = {
    "military_central_payroll": "Militares das Forças Armadas: a folha é paga por unidades centrais (Centro de Pagamento do Exército, Pagadoria de Pessoal da Marinha, Subdiretoria de Pagamento de Pessoal da Aeronáutica) com localizador Nacional, e o microdado de militares do Portal traz UF_EXERCICIO = -1 em todos os registros.",
    "executive_civil_without_uf": "Poder Executivo, pessoal civil cujo localizador orçamentário é Nacional, regional ou exterior (folhas centralizadas de ministérios, autarquias nacionais, inativos de órgãos extintos e ex-territórios, servidores no exterior). O SIAFI não diz em que UF a pessoa trabalha ou mora.",
    "national_scope_unit": "Unidades dos outros Poderes com quadro em todo o país: Justiça Federal de primeiro grau, Justiça Militar, Ministério Público Federal, do Trabalho e Militar, Defensoria Pública da União.",
    "trt_covering_two_ufs": "Tribunais Regionais do Trabalho cuja região cobre duas UFs: 8ª (PA e AP), 10ª (DF e TO), 11ª (AM e RR) e 14ª (RO e AC). A base do Tesouro não separa a despesa entre as duas.",
    "court_orders_other_branches": "Sentenças judiciais e precatórios de pessoal pagos pelos tribunais e demais órgãos dos outros Poderes (categoria 2.2.5 do RTN): o local de quem recebe não é o da unidade que paga.",
    "other_modalities": "Grupo 1 pago por transferência (modalidades 30 a 50) e não por aplicação direta.",
}


def trt_region(name):
    m = re.search(r"TRABALHO DA (\d+)A\. REGIAO", name)
    return int(m.group(1)) if m else None


def locate_other_power(uo, name):
    """UF of a unit of the Legislativo, Judiciario, MPU or DPU, or a not_located reason."""
    if uo in DF_UNITS: return "DF", None
    if "REGIONAL ELEITORAL" in name:
        key = re.sub(r"^TRIBUNAL REGIONAL ELEITORAL D[OAE]S? ", "", name).strip()
        return TRE_UF[key], None
    m = re.search(r"REGIONAL FEDERAL DA (\d)A\. REGIAO", name)
    if m: return TRF_SEAT[int(m.group(1))], None
    r = trt_region(name)
    if r is not None:
        return (TRT_SINGLE_UF[r], None) if r in TRT_SINGLE_UF else (None, "trt_covering_two_ufs")
    return None, "national_scope_unit"


RTN_LABEL = {"2.2.1": "2.2.1 - Ativo Civil", "2.2.2": "2.2.2 - Ativo Militar", "2.2.3": "2.2.3 - Aposentadorias e pensões civis",
             "2.2.4": "2.2.4 - Reformas e pensões militares", "2.2.5": "2.2.5 - Sentenças e Precatórios"}


def norm_rtn(cat):
    """The base spells the RTN category as '2.2.1 - Ativo Civil' (2024 on) or 'II.2.1 - Pessoal e Encargos Sociais - Ativo
    civil' (2022 and 2023), and the empty category as 'nan' or 'N/A'. Return one spelling for all years."""
    code = str(cat).split(" ")[0]
    if code.startswith("II."): code = "2." + code[3:]  # roman II is RTN block 2
    if code in RTN_LABEL: return RTN_LABEL[code]
    return "no RTN category" if str(cat) in ("nan", "N/A", "", "None") else str(cat)


def series():
    return [None] * len(MONTHS)


def addm(arr, i, v):
    arr[i] = (arr[i] or 0.0) + v


# ---------- load caches
portal = {}
for f in sorted(glob.glob(os.path.join(W, "cache", "desp_*.json"))):
    d = json.load(open(f)); ym = d["month"]; portal[f"{ym[:4]}-{ym[4:]}"] = d
dtt = {}
for f in sorted(glob.glob(os.path.join(W, "cache", "dtt_*.json"))):
    d = json.load(open(f)); dtt[d["year"]] = d
dtt_months = [m for m in MONTHS if m[:4] in dtt and int(m[5:]) in {r[0] for r in dtt[m[:4]]["gnd1"]}]
portal_months = [m for m in MONTHS if m in portal]
complete = [m for m in MONTHS if m in portal and m in dtt_months]
EXEC_CATS = [c for c in CATEGORIES if c.startswith(("executive", "military"))]
OTHER_CATS = ["legislative", "judiciary", "mpu", "dpu"]
EXEC_REASONS = ["military_central_payroll", "executive_civil_without_uf"]
OTHER_REASONS = ["national_scope_unit", "trt_covering_two_ufs", "court_orders_other_branches"]

uf_total = {u: series() for u in UFS}
uf_exec = {u: series() for u in UFS}
uf_other = {u: series() for u in UFS}
uf_cat = {u: {c: series() for c in CATEGORIES} for u in UFS}
nl_reason = {r: series() for r in REASONS}
nl_exec_by_orgao = collections.defaultdict(lambda: collections.defaultdict(float))  # year -> orgao -> value
fcdf_personnel = series()
check = collections.defaultdict(lambda: collections.defaultdict(float))  # month -> metric -> value
names_orgao = {}
units_seen = {}

for m in portal_months:  # Executive, Portal da Transparencia
    i = MI[m]
    fcdf_personnel[i] = 0.0
    for r in EXEC_REASONS + ["other_modalities"]: nl_reason[r][i] = nl_reason[r][i] or 0.0
    for u in UFS:
        uf_exec[u][i] = 0.0
        for c in EXEC_CATS: uf_cat[u][c][i] = 0.0
    d = portal[m]; names_orgao.update(d["names"]["orgao"])
    for uf, osup, osub, ug, uo, acao, mod, elem, paid, rp, liq in d["gnd1"]:
        v = paid + rp
        if mod == "91": check[m]["intra_budget_modality_91"] += v; continue
        if uo == FCDF_UO:
            fcdf_personnel[i] += v; continue
        if mod != "90":
            nl_reason["other_modalities"][i] += v; continue
        check[m]["portal_executive_gnd1_direct_excl_fcdf"] += v
        if acao in MILITARY_ACTIONS:
            cat = "military_retired" if elem == "01" else "military_pensioners" if elem == "03" else "military_active"
        else:
            cat = ("executive_civil_retired" if elem == "01" else "executive_civil_pensioners" if elem == "03" else
                   "executive_civil_court_orders_and_prior_years" if elem in ("91", "92") else "executive_civil_active")
        if uf in uf_exec:
            uf_exec[uf][i] += v; uf_cat[uf][cat][i] += v
        else:
            nl_reason["military_central_payroll" if cat.startswith("military") else "executive_civil_without_uf"][i] += v
            nl_exec_by_orgao[m[:4]][names_orgao.get(osup, osup)] += v

for m in dtt_months:  # other Powers, Tesouro base
    i = MI[m]; y, mm = m[:4], int(m[5:]); dd = dtt[y]
    for r in OTHER_REASONS + ["other_modalities"]: nl_reason[r][i] = nl_reason[r][i] or 0.0
    for u in UFS:
        uf_other[u][i] = 0.0
        for c in OTHER_CATS: uf_cat[u][c][i] = 0.0
    for mo_, orgao, uo, mod, acao, cat_rtn, v in dd["gnd1"]:
        if mo_ != mm: continue
        cat_rtn = norm_rtn(cat_rtn)
        if cat_rtn.startswith("2.2"): check[m]["tesouro_rtn_personnel"] += v
        if orgao not in POWER_OF_ORGAO:
            if mod == "90" and uo != FCDF_UO: check[m]["tesouro_executive_gnd1_direct_excl_fcdf"] += v
            continue
        if mod == "91": check[m]["intra_budget_modality_91"] += v; continue
        if mod != "90":
            nl_reason["other_modalities"][i] += v; continue
        check[m]["other_powers_gnd1_direct"] += v
        if cat_rtn.startswith("2.2.5"):
            nl_reason["court_orders_other_branches"][i] += v; continue
        name = dd["names"]["uo"][uo]
        uf, reason = locate_other_power(uo, name)
        units_seen[uo] = (name, uf, reason)
        if uf:
            uf_other[uf][i] += v; uf_cat[uf][POWER_OF_ORGAO[orgao]][i] += v
        else:
            nl_reason[reason][i] += v

nl_total = series()
for m in complete:
    i = MI[m]
    for u in UFS: uf_total[u][i] = uf_exec[u][i] + uf_other[u][i]
    nl_total[i] = sum(nl_reason[r][i] for r in REASONS)

# ---------- RTN table 1.5 (published) for the national check
wb = openpyxl.load_workbook(RTN_FILE, read_only=True)
rows = list(wb["1.5"].iter_rows(values_only=True))
hdr = [r for r in rows if r[0] and str(r[0]).startswith("Discrimina")][0]
want = {"2.2  Pessoal e Encargos Sociais": "personnel_and_charges_sociais", "2.2.1 Ativo Civil": "active_civil", "2.2.2 Ativo Militar": "active_military",
        "2.2.3 Aposentadorias e pensões civis": "civil_retirement_and_pensions", "2.2.4 Reformas e pensões militares": "military_retirement_and_pensions",
        "2.2.5 Sentenças e Precatórios": "court_orders", "2.3.11  Fundo Constitucional DF": "fcdf_custeio_e_capital"}
rtn = collections.defaultdict(dict)
for r in rows:
    lab = str(r[0]).strip() if r[0] else ""
    for k, key in want.items():
        if lab == k.strip():
            for dt, v in zip(hdr[1:], r[1:]):
                if hasattr(dt, "year") and f"{dt.year}-{dt.month:02d}" in MI and isinstance(v, (int, float)):
                    rtn[key][f"{dt.year}-{dt.month:02d}"] = v * 1e6
if not (set(rtn) == set(want.values())):
    raise SystemExit(set(want.values()) - set(rtn))

# ---------- FCDF block (Tesouro base: all groups; Portal used as cross-check)
fcdf_tot, fcdf_by_group, fcdf_personnel_by_rtn = series(), {g: series() for g in ("1", "3", "4", "5")}, {}
fcdf_actions = collections.defaultdict(lambda: collections.defaultdict(float))
fcdf_portal = series()
for y, dd in dtt.items():
    for mo_, grp, mod, acao, cat_rtn, v in dd["fcdf"]:
        m = f"{y}-{mo_:02d}"
        if m not in MI: continue
        i = MI[m]
        addm(fcdf_tot, i, v)
        addm(fcdf_by_group.setdefault(grp, series()), i, v)
        if grp == "1":
            c = norm_rtn(cat_rtn)
            addm(fcdf_personnel_by_rtn.setdefault(c, series()), i, v)
        fcdf_actions[(grp, acao)][y] += v
        fcdf_actions[(grp, acao)]["name"] = 0.0
fcdf_action_names = {}
for dd in dtt.values(): fcdf_action_names.update(dd["names"]["acao"])
for m, d in portal.items():
    if m in MI: fcdf_portal[MI[m]] = round(sum(r[4] + r[5] for r in d["fcdf"]), 2)


def r2(x): return None if x is None else round(x, 2)


YEARS = sorted({m[:4] for m in MONTHS})


def with_ytd(arr):
    """Full year when the 12 months exist (2026: January to August); otherwise null, with the partial sum apart."""
    out, partial = {}, {}
    for y in YEARS:
        ms = [m for m in MONTHS if m.startswith(y)]
        have = [m for m in ms if arr[MI[m]] is not None]
        key = "2026_jan_ago" if y == "2026" else y
        out[key] = round(sum(arr[MI[m]] for m in ms), 2) if have and len(have) == len(ms) else None
        if have and len(have) < len(ms):
            partial[y] = {"from": have[0], "to": have[-1], "months": len(have), "value": round(sum(arr[MI[m]] for m in have), 2)}
    if partial: out["partial_years"] = partial
    return out


complete_years = [y for y in YEARS if y != "2026" and all(m in complete for m in MONTHS if m.startswith(y))]


out_uf = {}
for u in UFS:
    out_uf[u] = {"total_located": [r2(x) for x in uf_total[u]],
                 "by_category": {c: [r2(x) for x in uf_cat[u][c]] for c in CATEGORIES},
                 "annual": {"total_located": with_ytd(uf_total[u]), "by_category": {c: with_ytd(uf_cat[u][c]) for c in CATEGORIES}}}

# ---------- national check, per year over the months that have both sources
nat = {}
for y in YEARS:
    ms = [m for m in complete if m.startswith(y)]
    if not ms: continue
    s = lambda key: round(sum(check[m][key] for m in ms), 2)
    located = round(sum(uf_total[u][MI[m]] for u in UFS for m in ms), 2)
    notloc = round(sum(nl_total[MI[m]] for m in ms), 2)
    other_mod = round(sum(nl_reason["other_modalities"][MI[m]] for m in ms), 2)
    fcdfp = round(sum(fcdf_personnel[MI[m]] for m in ms), 2)
    direct = round(s("portal_executive_gnd1_direct_excl_fcdf") + s("other_powers_gnd1_direct"), 2)
    rtn_tot = round(sum(rtn["personnel_and_charges_sociais"].get(m, 0.0) for m in ms), 2)
    nat[y] = {
        "months": [ms[0], ms[-1]], "n_months": len(ms),
        "rtn_table_1_5_personnel_and_social_charges": rtn_tot,
        "rtn_table_1_5_breakdown": {k: round(sum(rtn[k].get(m, 0.0) for m in ms), 2) for k in
                                    ("active_civil", "active_military", "civil_retirement_and_pensions", "military_retirement_and_pensions", "court_orders")},
        "tesouro_base_rtn_personnel": s("tesouro_rtn_personnel"),
        "siafi_gnd1_direct_payments_excl_fcdf": direct,
        "fcdf_personnel_excluded_already_counted": fcdfp,
        "sum_of_ufs_located": located,
        "not_located": notloc,
        "not_located_of_which_other_modalities": other_mod,
        "intra_budget_modality_91_excluded": s("intra_budget_modality_91"),
        "coverage_pct_of_payroll_excl_fcdf": round(100 * located / (located + notloc), 2) if located + notloc else None,
        "coverage_pct_of_rtn_excl_fcdf": round(100 * located / (rtn_tot - fcdfp), 2) if rtn_tot else None,
        "identity_check_located_plus_not_located_minus_direct_minus_other_modalities": round(located + notloc - direct - other_mod, 2),
        "executive_portal_vs_tesouro_base_gap": round(s("portal_executive_gnd1_direct_excl_fcdf") - s("tesouro_executive_gnd1_direct_excl_fcdf"), 2),
        "executive_portal_vs_tesouro_base_gap_pct": round(100 * (s("portal_executive_gnd1_direct_excl_fcdf") / s("tesouro_executive_gnd1_direct_excl_fcdf") - 1), 3),
    }

# Month-by-month agreement of the two sources on the Executive (both are SIAFI payments; they should match within ~1%).
DIVERGENCE_PCT = 3.0
monthly_check = {"portal_executive_direct_excl_fcdf": series(), "tesouro_executive_direct_excl_fcdf": series(), "status": [None] * len(MONTHS)}
for m in complete:
    i = MI[m]; pe, te = check[m]["portal_executive_gnd1_direct_excl_fcdf"], check[m]["tesouro_executive_gnd1_direct_excl_fcdf"]
    monthly_check["portal_executive_direct_excl_fcdf"][i] = round(pe, 2); monthly_check["tesouro_executive_direct_excl_fcdf"][i] = round(te, 2)
    monthly_check["status"][i] = "ok" if abs(100 * (pe / te - 1)) <= DIVERGENCE_PCT else "portal_vs_tesouro_divergent"

nl_annual_orgao = {y: {k: round(v, 2) for k, v in sorted(d.items(), key=lambda kv: -kv[1]) if v >= 1e8}
                   for y, d in sorted(nl_exec_by_orgao.items())}

located_by_exercise = {
    "status": "não construído nesta coleta; os valores ficam null",
    "values": None,
    "what_it_would_be": "Folha bruta de um mês de referência por ano, alocada pelo campo UF_EXERCICIO do microdado de servidores do Portal da Transparência (https://portaldatransparencia.gov.br/download-de-dados/servidores/AAAAMM_Servidores_SIAPE), sem anualizar. Seria um bloco separado de total_located e nunca somado a ele.",
    "why_null": "O servidor de arquivos da CGU (dadosabertos-download.cgu.gov.br) passou a segurar as conexões e a devolver a página de verificação do AWS WAF em 2026-10-01 (downloads de 16 minutos sem nenhum byte), e o computador da coleta estava sem memória livre. O arquivo SIAPE tem cerca de 79 MB por mês; nenhum mês de referência foi baixado depois do teste de 2024-01, cujo arquivo foi apagado após a leitura.",
    "findings_from_the_files_that_were_read": {
        "siape_servants_2024_01": "734.571 linhas de cadastro, 598.999 pessoas. UF_EXERCICIO = -1 em 291.768 linhas (39,7%). O DF aparece como UF de exercício de pessoal de instituições de outras UFs: Instituto Federal de Alagoas 1.288 linhas no DF e 19 em AL; Universidade Federal da Integração Latino-Americana (Foz do Iguaçu, PR) 801 no DF e 12 no PR; ex-Território do Amapá 5.191 no DF e 68 no AP. 20.735 linhas do Ministério da Saúde com situação RESIDENCIA E PMM (bolsas de residência e Mais Médicos, que não são pessoal) estão no DF. Usar o campo como está aumentaria o DF.",
        "military_2024_01": "345.468 linhas de cadastro (Exército 204.845, Marinha 72.906, Aeronáutica 67.717): UF_EXERCICIO = -1 em todas. Não há UF de militar em nenhum arquivo aberto encontrado.",
        "retirees_and_pensioners_2024_12": "Os cadastros de Aposentados_SIAPE, Aposentados_BACEN, Pensionistas_SIAPE, Pensionistas_BACEN e Pensionistas_DEFESA não têm nenhuma coluna de UF (cabeçalhos lidos em 2026-10-01). Aposentados e pensionistas não podem ser localizados pelo microdado.",
    },
    "consequence": "Pelo microdado, só os servidores civis ativos do Executivo (SIAPE) poderiam ser alocados, e com o defeito do DF acima. Militares (ativos, inativos e pensionistas) e aposentados e pensionistas civis continuam sem UF em qualquer fonte aberta encontrada.",
}

fcdf_block = {
    "description": "Fundo Constitucional do Distrito Federal (unidade orçamentária 73901): o que a União pagou no mês, todos os grupos de despesa, pago mais restos a pagar pagos.",
    "uf": "DF",
    "total": [r2(x) for x in fcdf_tot],
    "by_group": {{"1": "personnel_and_charges", "3": "other_current_expenses", "4": "investments", "5": "financial_investments"}[g]: [r2(x) for x in a]
                 for g, a in fcdf_by_group.items() if any(x for x in a if x)},
    "personnel_by_rtn_category": {k: [r2(x) for x in a] for k, a in fcdf_personnel_by_rtn.items()},
    "annual": {"total": with_ytd(fcdf_tot), **{f"group_{g}": with_ytd(a) for g, a in fcdf_by_group.items() if any(x for x in a if x)}},
    "by_action_annual": {f"{g} {a} {fcdf_action_names.get(a, '')}": {y: round(v, 2) for y, v in sorted(d.items()) if y != "name"}
                         for (g, a), d in sorted(fcdf_actions.items())},
    "cross_check_portal_total": [x for x in fcdf_portal],
    "cross_check_uf_balance_2024": {"value": 23606312156.44, "file": "data/uf-balance-2024.json", "field": "direct_spending.fcdf_df_constitutional_fund"},
    "already_inside_payroll": "O grupo 1 (pessoal e encargos) do FCDF paga as polícias Civil e Militar, o Corpo de Bombeiros (ativos, inativos e pensionistas) e o pessoal da saúde e da educação do DF. Esse grupo está dentro da despesa de pessoal da União no SIAFI (unidade 73901, localizador DF) e dentro da linha 2.2 Pessoal e Encargos Sociais do RTN (2.2.1 a 2.2.4). Neste arquivo ele é separado em fcdf_personnel_excluded e NÃO entra em total_located do DF nem em not_located, porque o mapa já soma o FCDF inteiro em direct_spending.fcdf_df_constitutional_fund. Não está confirmado se o microdado de servidores do Portal (SIAPE) traz esse pessoal (a busca pelos órgãos da PCDF, PMDF e CBMDF não foi feita); este arquivo não usa o SIAPE nos valores.",
    "sources": [{"url": DTT_PAGE, "note": "Tesouro Nacional, Despesas e Transferências Totais da União (critério valor pago), arquivo anual XLSX (aba de dados 'base' ou com o nome do ano), coluna PAGAMENTOS_TOTAIS, UNIDADE_ORCAMENTARIA_CODIGO = 73901.", "collected_at": COLLECTED},
                {"url": PORTAL_PAGE, "note": "Conferência: Portal da Transparência, Execução da Despesa, mesma unidade, Valor Pago + Valor Restos a Pagar Pagos.", "collected_at": COLLECTED}],
}

doc = {
    "title": "Folha de pessoal da União localizada por UF",
    "months": MONTHS,
    "currency": "BRL, valores correntes (sem correção pela inflação)",
    "collected_at": COLLECTED,
    "value_definition": "Pago no mês mais restos a pagar pagos no mês, grupo de despesa 1 (Pessoal e Encargos Sociais), modalidade 90 (aplicação direta). É o critério 'valor pago' da tabela 1.5 do RTN. Valor bruto: inclui o imposto de renda retido e a contribuição do servidor (PSS), que a arrecadação federal do mapa já conta no DF e nas demais UFs.",
    "location_rules": {
        "executive": "UF do localizador orçamentário (coluna UF do arquivo de Execução da Despesa do Portal da Transparência). É a atribuição do próprio SIAFI, não o local de trabalho ou de moradia da pessoa.",
        "other_branches": "UF da sede da unidade orçamentária, só quando a unidade trabalha numa única UF: Câmara, Senado, TCU, STF, STJ, TSE, TST, CNJ, TJDFT, MPDFT e ESMPU no DF; cada TRE na sua UF; cada TRF na UF da sede; cada TRT cuja região é uma UF. As demais unidades vão para not_located.",
        "fcdf": "Unidade 73901 fora de tudo (ver fcdf.already_inside_payroll).",
        "never_estimated": "Nenhum valor foi distribuído por população, por número de servidores ou por qualquer proporção. O que o dado não localiza fica em not_located.",
    },
    "categories": CATEGORIES,
    "coverage": {"total_located_and_executive": [complete[0], complete[-1]] if complete else None,
                 "other_powers_and_fcdf": [dtt_months[0], dtt_months[-1]] if dtt_months else None,
                 "complete_years": complete_years,
                 "rule": "total_located e as categorias executive_* e military_* só existem nos meses com o arquivo do Portal; legislative, judiciary, mpu, dpu e o bloco fcdf existem nos meses com a base do Tesouro. Fora disso, null.",
                 "missing_reason": "Coleta de 2026-10-01 interrompida no limite de tempo: o Portal passou a bloquear downloads (AWS WAF) depois de 2025-10, e cada arquivo anual do Tesouro de 2019 a 2021 levava cerca de 16 minutos. Os scripts retomam de onde pararam (pipelines/series/agg_payroll_monthly.py e agg_union_expense_base.py)."},
    "uf": out_uf,
    "fcdf_personnel_excluded": {"uf": "DF", "monthly": [r2(x) for x in fcdf_personnel], "annual": with_ytd(fcdf_personnel),
                                "note": "Grupo 1, modalidade 90, unidade 73901 (FCDF), pelo Portal. Já contado no mapa dentro do FCDF; não somar à folha."},
    "not_located": {"total": [r2(x) for x in nl_total], "by_reason": {k: [r2(x) for x in a] for k, a in nl_reason.items()},
                    "annual": {"total": with_ytd(nl_total), "by_reason": {k: with_ytd(a) for k, a in nl_reason.items()}},
                    "reasons": REASONS,
                    "executive_without_uf_by_top_body_annual": nl_annual_orgao},
    "national_check": {"annual": nat, "monthly": monthly_check,
                       "monthly_status_rule": f"status = portal_vs_tesouro_divergent quando o pessoal do Executivo no Portal difere da base do Tesouro em mais de {DIVERGENCE_PCT}% no mês. Nesses meses os valores do Executivo por UF vêm do Portal e devem ser lidos com cuidado.",
                       "note": "sum_of_ufs_located + not_located = pagamentos diretos de pessoal da União sem o FCDF, mais a parcela de outras modalidades. A diferença para o RTN vem do FCDF (que o RTN inclui), da parcela da modalidade 91 que o RTN classifica como pessoal e da pequena diferença entre o Portal e a base do Tesouro no Executivo (executive_portal_vs_tesouro_base_gap)."},
    "fcdf": fcdf_block,
    "units_of_other_powers": {uo: {"name": n, "uf": uf, "not_located_reason": rs} for uo, (n, uf, rs) in sorted(units_seen.items())},
    "sources": [
        {"fields": ["uf.*: categorias executive_* e military_*", "not_located: military_central_payroll, executive_civil_without_uf"], "url": PORTAL_PAGE,
         "files": "https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/AAAAMM (um ZIP por mês, 2019-01 a 2026-08)",
         "note": "CGU, Portal da Transparência, Execução da Despesa. Só o Poder Executivo federal. Colunas usadas: UF, Código Órgão Superior, Código Unidade Orçamentária, Código Ação, Código Grupo de Despesa = 1, Código Modalidade da Despesa, Código Elemento de Despesa, Valor Pago (R$), Valor Restos a Pagar Pagos (R$).", "collected_at": COLLECTED},
        {"fields": ["uf.*: legislative, judiciary, mpu, dpu", "not_located: national_scope_unit, trt_covering_two_ufs, court_orders_other_branches", "fcdf", "national_check.tesouro_base_rtn_personnel"],
         "url": DTT_PAGE, "files": "um XLSX por ano, URL de cada arquivo lida na API CKAN do Tesouro Transparente",
         "note": "Tesouro Nacional, Despesas e Transferências Totais da União, critério valor pago (a base da tabela 1.5 do RTN). Todos os Poderes, por mês, órgão, unidade orçamentária, grupo, modalidade, ação e categoria do RTN. Não tem UF nem localizador.", "collected_at": COLLECTED},
        {"fields": ["national_check.*.rtn_table_1_5_*"], "url": RTN_URL, "page": RTN_PAGE,
         "note": "Tesouro Nacional, RTN, série histórica (serie_historica_ago26.xlsx, publicada em 2026-09-29), tabela 1.5, linhas 2.2 a 2.2.5 e 2.3.11, R$ milhões convertidos para R$.", "collected_at": "2026-09-30"},
    ],
    "nulls": {"rule": "null = mês sem o arquivo de origem daquele campo; nenhum valor foi estimado.",
              "months_without_portal": [m for m in MONTHS if m not in portal],
              "months_without_tesouro_base": [m for m in MONTHS if m not in dtt_months]},
    "located_by_exercise": located_by_exercise,
    "flags": {
        "df_understated": "O DF recebe só o que o SIAFI localiza no DF e as unidades dos outros Poderes com sede no DF. Ficam fora, em not_located, os militares que servem em Brasília, a parte em Brasília das folhas centralizadas de ministérios e autarquias, a parte da 10ª Região do Trabalho e os aposentados e pensionistas que moram no DF mas são pagos por unidades sem UF. Por isso o total do DF é um piso, não o valor completo.",
        "retirees_location": "Aposentados e pensionistas são localizados pela unidade que paga (Executivo: localizador; outros Poderes: sede da unidade), não pelo endereço de quem recebe, que não é público.",
        "tcu_and_parliament": "O TCU tem secretarias em todas as UFs e os gabinetes parlamentares podem ter pessoal nos estados; a base do Tesouro não separa esse pessoal, e ele foi localizado no DF pela sede.",
        "portal_2025_06": "O arquivo de 2025-06 da Execução da Despesa do Portal traz R$ 47,67 bi de pessoal do Executivo (sem FCDF), contra R$ 23,99 bi na base do Tesouro para o mesmo mês; julho e agosto ficam abaixo do Tesouro (R$ 5,83 bi e R$ 1,12 bi), e de junho a agosto o Portal soma R$ 16,7 bi a mais. O excesso está espalhado por quase todas as linhas (militares, aposentadorias, ativos civis), não numa só. Causa não identificada; ver national_check.monthly.status.",
        "siape_uf_of_work": "Ver located_by_exercise: o campo UF_EXERCICIO do SIAPE tem 39,7% de -1 e põe no DF pessoal de outras UFs; não foi usado em total_located.",
    },
}
json.dump(doc, open(OUT, "w"), ensure_ascii=False, indent=1)
print("wrote", OUT, "complete months", len(complete), "tesouro months", len(dtt_months), "complete years", complete_years)
for y, v in nat.items(): print(y, {k: (round(x / 1e9, 2) if isinstance(x, float) and abs(x) > 1e6 else x) for k, x in v.items() if not isinstance(x, dict)})
