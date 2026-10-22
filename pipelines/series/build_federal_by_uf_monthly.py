"""Assemble data/series/federal-by-uf-monthly.json from the raw inputs in <workdir>.

Usage: build_federal_by_uf_monthly.py <workdir> [last Portal month published, YYYY-MM]   (needs openpyxl and the pdftotext binary)
If the last Portal month is given and some months up to it were not aggregated (e.g. the CGU server blocked the download),
those months are null and listed in flags.transfers_missing_months.
Inputs (see download_inputs.sh and the other scripts in this folder):
  arrecadacao-estado.csv, serie-1994-2025.xlsx, rfbpdf/analise-mensal-<last>.pdf   Receita Federal
  cache/transf_YYYYMM.json (agg_transfers_monthly.py), tt/lc176est.csv, tt/lc176mun.csv   Portal da Transparencia, Tesouro
  misocial/misocial_YYYY.csv (download_misocial.sh)   MDS MI Social
  beps_rgps_uf.json (beps_rgps_by_uf.py), aeps_inss_uf.json (aeps_inss_by_uf.py)   Previdencia
"""
import collections, csv, glob, json, os, re, subprocess, sys
from datetime import date
from pathlib import Path
import openpyxl
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from classify_transfers import classify, CATS, UFS, STATE, MUNI
from taxmap import TAXMAP
from parse_tt import parse as tt_parse

W = Path(sys.argv[1]); OUT = HERE.parents[1] / "data" / "series" / "federal-by-uf-monthly.json"
TODAY = date.today().isoformat()
MES = {'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12}
FIRST = "2019-01"

def mrange(a, b):
    y, m = map(int, a.split("-"))
    while f"{y}-{m:02d}" <= b:
        yield f"{y}-{m:02d}"; m += 1
        if m == 13: y, m = y + 1, 1

def num_rfb(x):
    x = x.strip()
    if not x: return 0.0
    if re.fullmatch(r'-?\d{1,3}(\.\d{3})+(,\d+)?', x): x = x.replace('.', '')
    return float(x.replace(',', '.'))

# ---------- 1. federal revenue by UF (Receita, arrecadacao-estado.csv) ----------
rows = list(csv.reader(open(W / "arrecadacao-estado.csv", encoding="latin1"), delimiter=";"))
H = rows[0]
col2key = {c: k for k, cs in TAXMAP.items() for c in cs}
unmapped = [c for c in H[3:] if c not in col2key]
if not (not unmapped):
    raise SystemExit(unmapped)
rev = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(float)))  # month -> uf -> key -> value
for r in rows[1:]:
    if r[0] < FIRST[:4]: continue
    ym = f"{r[0]}-{MES[r[1]]:02d}"
    for c, x in zip(H[3:], r[3:]):
        rev[ym][r[2]][col2key[c]] += num_rfb(x)
REV_LAST = max(rev)

# national monthly totals (R$ milhões): serie historica XLSX by year, and Tabela III of the latest monthly analysis PDF for the current year
nat = {}
wb = openpyxl.load_workbook(W / "serie-1994-2025.xlsx", read_only=True, data_only=True)
for y in range(2019, 2026):
    for row in wb[str(y)].iter_rows(values_only=True):
        if row[0] and str(row[0]).strip().startswith("TOTAL GERAL"):
            for m in range(12): nat[f"{y}-{m + 1:02d}"] = row[1 + m] * 1e6
            break
PDF = W / "rfbpdf" / "analise-mensal-2026.pdf"   # the latest monthly analysis; its Tabela III has every month of the year so far
PDF_URL = "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/arrecadacao-federal/2026/analise-mensal-ago-2026.pdf"
txt = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], capture_output=True, text=True).stdout
i0 = txt.index("TABELA III\n") if "TABELA III\n" in txt else re.search(r"TABELA III\s*\n", txt).start()
block = txt[i0: txt.index("TABELA III-A")]
MON = {'JAN': 1, 'FEV': 2, 'MAR': 3, 'ABR': 4, 'MAIO': 5, 'MAI': 5, 'JUN': 6, 'JUL': 7, 'AGO': 8, 'SET': 9, 'OUT': 10, 'NOV': 11, 'DEZ': 12}
pending = []
for line in block.splitlines():
    t = line.split()
    if t and t[0] in MON and len(t) >= 10:
        pending.append((MON[t[0]], float(t[-1].replace('.', '').replace(',', '.'))))
    elif len(t) == 1 and re.fullmatch(r"20\d\d", t[0]):
        y = int(t[0])
        for m, v in pending:
            if y >= 2026: nat[f"{y}-{m:02d}"] = v * 1e6
        pending = []

# ---------- 2. transfers (Portal monthly caches + Tesouro LC 176) ----------
caches = sorted(glob.glob(str(W / "cache" / "transf_*.json")))
TR_MONTHS = [Path(c).stem.split("_")[1] for c in caches]
TR_LAST = max(f"{TR_MONTHS[-1][:4]}-{TR_MONTHS[-1][4:]}", sys.argv[2] if len(sys.argv) > 2 else "")
TR_AVAILABLE = {f"{m[:4]}-{m[4:]}" for m in TR_MONTHS}
TR_MISSING = [m for m in mrange(FIRST, TR_LAST) if m not in TR_AVAILABLE]
TR_LAST_COLLECTED = max(TR_AVAILABLE)
tr = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(float)))  # month -> uf -> cat
trs = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(float)))  # month -> uf -> sphere
nouf = collections.defaultdict(lambda: collections.defaultdict(float))  # month -> action -> value (public recipients without UF)
excluded = collections.defaultdict(lambda: collections.defaultdict(float))
action_names, partial_info = {}, {}
for c in caches:
    d = json.load(open(c)); ym = f"{d['month'][:4]}-{d['month'][4:]}"
    action_names.update(d["action_names"])
    partial_info[ym] = {"rows": d["rows"], "ano_mes_values": d["ano_mes_values"]}
    for uf, tipo, fav, func, acao, modal, mun, v in d["keys"]:
        sphere, cat = classify(uf, fav, func, acao, modal, mun)
        if sphere:
            tr[ym][uf][cat] += v; trs[ym][uf][sphere] += v
        else:
            excluded[ym][cat.split(":")[0]] += v
            if cat.startswith("public_without_uf") or cat == "lc176_replaced_by_tesouro":
                nouf[ym][acao] += v
de, _, _ = tt_parse(str(W / "tt" / "lc176est.csv")); dm, _, _ = tt_parse(str(W / "tt" / "lc176mun.csv"))
TT_LAST = max(f"{y}-{m:02d}" for d in (de, dm) for s in d.values() for (y, m), v in s.items() if v)
lc176_check = {}   # Tesouro (per UF, summed) against the Portal action 00SE (no UF), month by month
for ym in mrange("2020-01", TR_LAST):
    y, m = map(int, ym.split("-"))
    tt = sum(s.get((y, m), 0.0) for d in (de, dm) for s in d.values())
    pt = nouf[ym].get("00SE", 0.0) if ym in TR_AVAILABLE else None
    if tt or pt: lc176_check[ym] = {"tesouro": round(tt, 2), "portal_00SE": None if pt is None else round(pt, 2)}
for ym in mrange(FIRST, TR_LAST):
    y, m = map(int, ym.split("-"))
    for uf in UFS:
        e, mu = de.get(uf, {}).get((y, m), 0.0), dm.get(uf, {}).get((y, m), 0.0)
        tr[ym][uf]['lc176_kandir_compensation'] += e + mu
        trs[ym][uf][STATE] += e; trs[ym][uf][MUNI] += mu

# ---------- 3. Bolsa Familia / Auxilio Brasil and BPC (MDS MI Social) ----------
bf = collections.defaultdict(lambda: collections.defaultdict(float)); bpc = collections.defaultdict(lambda: collections.defaultdict(float))
bf_seen, bpc_seen, prog = collections.Counter(), collections.Counter(), {}
for f in sorted(glob.glob(str(W / "misocial" / "misocial_*.csv"))):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        ym = f"{r['anomes_s'][:4]}-{r['anomes_s'][4:]}"
        if ym < FIRST: continue
        a, b1, b2 = r['valor_repassado_bolsa_familia_f'], r['pab_valor_pago_d'], r['pab_extraordinario_valor_pago_d']
        if a not in ('', None):
            bf[ym][r['sigla_uf']] += float(a); bf_seen[ym] += 1; prog[ym] = "Bolsa Família"
        if b1 not in ('', None) or b2 not in ('', None):
            bf[ym][r['sigla_uf']] += float(b1 or 0) + float(b2 or 0); bf_seen[ym] += 1; prog[ym] = "Auxílio Brasil"
        if r['bpc_val_f'] not in ('', None):
            bpc[ym][r['sigla_uf']] += float(r['bpc_val_f']); bpc_seen[ym] += 1
BF_MONTHS = sorted(m for m in bf if sum(bf[m].values()) > 0)
BPC_MONTHS = sorted(m for m in bpc if sum(bpc[m].values()) > 0)   # months not yet published come back as zeros in every municipality
BF_LAST, BPC_LAST = BF_MONTHS[-1], BPC_MONTHS[-1]

# ---------- 4. INSS: BEPS table 19 (RGPS emitted, monthly) and AEPS B.15 (annual, includes BPC) ----------
beps = json.load(open(W / "beps_rgps_uf.json"))
by_month = collections.defaultdict(list)
for url, v in beps.items(): by_month[v["reference_month"]].append((url, v))
inss, inss18, beps_files, beps_dupes = {}, {}, {}, {}
for ym, lst in by_month.items():
    lst.sort(key=lambda t: t[0].rsplit("/", 1)[-1])          # the later upload (-1, -2, _a suffix) sorts last
    url, v = lst[-1]
    inss[ym] = {uf: v["uf"][uf]["value"] for uf in UFS}
    if v.get("uf_18"): inss18[ym] = {uf: v["uf_18"][uf]["value"] for uf in UFS}
    beps_files[ym] = url
    vals = {round(x["uf"]["BR"]["value"], 2) for _, x in lst}
    if len(vals) > 1: beps_dupes[ym] = {u.rsplit("/", 1)[-1]: round(x["uf"]["BR"]["value"], 2) for u, x in lst}
INSS_LAST = max(inss)
aeps = json.load(open(W / "aeps_inss_uf.json"))

# ---------- assemble ----------
LAST = max(REV_LAST, TR_LAST, BF_LAST, BPC_LAST, INSS_LAST)
MONTHS = list(mrange(FIRST, LAST))
def r2(x): return None if x is None else round(x, 2)

DF_THRESHOLD, GAP_THRESHOLD = 12.0, 0.5
rev_status, nat_arr, sum_arr, gap_arr, df_share = [], [], [], [], []
for ym in MONTHS:
    if ym > REV_LAST:
        rev_status.append("not_published"); nat_arr.append(r2(nat.get(ym))); sum_arr.append(None); gap_arr.append(None); df_share.append(None); continue
    s = sum(sum(rev[ym][u].values()) for u in UFS); n = nat.get(ym)
    dfp = 100 * sum(rev[ym]['DF'].values()) / s
    st = []
    if dfp > DF_THRESHOLD: st.append("uf_attribution_broken")
    if n and abs(s - n) / n * 100 > GAP_THRESHOLD: st.append("unattributed_gap")
    rev_status.append("+".join(st) or "ok"); nat_arr.append(r2(n)); sum_arr.append(r2(s)); gap_arr.append(r2(n - s) if n else None); df_share.append(round(dfp, 2))

out_uf = {}
for uf in UFS:
    o = {}
    fr_total, fr_rfb, fr_bt = [], [], {k: [] for k in TAXMAP}
    for ym in MONTHS:
        if ym > REV_LAST:
            fr_total.append(None); fr_rfb.append(None)
            for k in TAXMAP: fr_bt[k].append(None)
            continue
        d = rev[ym][uf]
        fr_total.append(r2(sum(d.values()))); fr_rfb.append(r2(sum(d.values()) - d['administered_by_other_agencies']))
        for k in TAXMAP: fr_bt[k].append(r2(d[k]))
    o["federal_revenue"] = {"total": fr_total, "rfb_administered": fr_rfb, "by_tax": fr_bt}
    t_tot, t_st, t_mu, t_cat = [], [], [], {c: [] for c in CATS}
    for ym in MONTHS:
        if ym not in TR_AVAILABLE:
            t_tot.append(None); t_st.append(None); t_mu.append(None)
            for c in CATS: t_cat[c].append(None)
            continue
        t_tot.append(r2(sum(tr[ym][uf].values()))); t_st.append(r2(trs[ym][uf][STATE])); t_mu.append(r2(trs[ym][uf][MUNI]))
        for c in CATS: t_cat[c].append(r2(tr[ym][uf][c]))
    o["transfers"] = {"total": t_tot, "to_state_government": t_st, "to_municipalities": t_mu, "by_category": t_cat}
    o["bolsa_familia"] = [r2(bf[ym][uf]) if ym in BF_MONTHS else None for ym in MONTHS]
    o["inss"] = [r2(inss[ym][uf]) if ym in inss else None for ym in MONTHS]
    o["inss_gross_benefit_value"] = [r2(inss18[ym][uf]) if ym in inss18 else None for ym in MONTHS]
    o["bpc"] = [r2(bpc[ym][uf]) if ym in BPC_MONTHS else None for ym in MONTHS]
    o["inss_annual_aeps"] = {str(y): (r2(v[uf]) if v else None) for y, v in sorted(aeps["annual"].items())}
    out_uf[uf] = o

all_actions = sorted({a for ym in nouf for a in nouf[ym]})
big_actions = [a for a in all_actions if sum(abs(nouf[ym][a]) for ym in nouf) > 1e8]
national = {
    "federal_revenue_total_receita": nat_arr, "federal_revenue_sum_of_ufs": sum_arr, "federal_revenue_not_attributed_to_any_uf": gap_arr,
    "federal_revenue_df_share_pct": df_share, "federal_revenue_month_status": rev_status,
    "transfers_public_recipients_without_uf": {
        "total": [r2(sum(nouf[ym].values())) if ym in TR_AVAILABLE else None for ym in MONTHS],
        "by_action": {f"{a} {action_names.get(a, '')}".strip(): [r2(nouf[ym].get(a, 0.0)) if ym in TR_AVAILABLE else None for ym in MONTHS] for a in big_actions},
        "note": "Pagamentos a governos estaduais e municipais que o Portal da Transparência registra sem UF. Não entram em nenhuma UF. A LC 176 (00SE) aparece aqui e também, por UF, dentro das UFs via Tesouro Nacional: não somar as duas."},
    "bolsa_familia_program": [prog.get(ym) if ym in BF_MONTHS else None for ym in MONTHS],
}
flags = {
    "2025_uf_attribution": ("Arrecadação federal por UF: de 2025-02 a 2026-01 a Receita atribuiu ao DF entre 14,8% e 25,2% da arrecadação do país "
                            "(de 2019 a 2024 o máximo mensal foi 10,8%, em maio de 2020), e as demais UFs ficaram subestimadas; o total nacional desses meses "
                            "está correto. Em 2025-12 há ainda R$ 31,1 bi sem UF (R$ 33,0 bi de receita previdenciária). Em 2026-03, 05, 06 e 07 a distribuição "
                            "voltou ao padrão, mas de R$ 4,6 bi a R$ 11,2 bi por mês (2% a 4%) não estão em UF nenhuma. O mesmo salto do DF aparece no arquivo "
                            "da Receita por município de 2025 (Brasília com R$ 603 bi). Sem nota da Receita. Recomendação ao site: para meses com status "
                            "uf_attribution_broken, não pintar o mapa nem calcular saldo por UF com a arrecadação; mostrar o total nacional e um aviso. "
                            "Para períodos que contêm esses meses (ano 2025, mandato 2023-2026), a arrecadação por UF fica indisponível no mapa. "
                            "Os valores brutos continuam no arquivo, sem correção."),
    "federal_revenue_month_status_rule": f"uf_attribution_broken: participação do DF acima de {DF_THRESHOLD}% da soma das UFs; unattributed_gap: soma das UFs difere do total nacional da Receita em mais de {GAP_THRESHOLD}%; not_published: mês ainda fora do arquivo da Receita.",
    "2024_09_import_tax": "Em 2024-09 parte do Imposto de Importação foi lançada como Imposto de Exportação em várias UFs e R$ 1,37 bi ficaram sem UF (status unattributed_gap).",
    "bolsa_familia_programs": "2019-01 a 2021-10 Bolsa Família (campo valor_repassado_bolsa_familia_f); 2021-11 a 2023-02 Auxílio Brasil, o programa que substituiu o Bolsa Família (pab_valor_pago_d + pab_extraordinario_valor_pago_d; de 2022-07 em diante o valor vem só em pab_valor_pago_d); 2023-03 em diante Bolsa Família (valor_repassado_bolsa_familia_f). O programa de cada mês está em national.bolsa_familia_program.",
    "bolsa_familia_auxilio_emergencial": "De 2020-04 a 2020-12 e de 2021-04 a 2021-10 a maior parte das famílias do Bolsa Família recebeu o Auxílio Emergencial no lugar do benefício; o Auxílio Emergencial NÃO está nesta série, por isso o Bolsa Família cai nesses meses.",
    "inss_definition": "inss = benefícios do RGPS emitidos no mês na UF (BEPS, tabela 19; valor em R$; inclui o 13º nos meses em que é pago; não inclui o BPC/LOAS; é o mesmo conceito da AEPS, que desconta os empréstimos consignados: em 2024 a soma das UFs dá R$ 785,6 bi, contra R$ 786,9 bi da AEPS sem o BPC). inss_gross_benefit_value = valor dos benefícios do RGPS antes dos descontos e sem créditos eventuais (BEPS, tabela 18), mais perto da despesa paga registrada no SIAFI. bpc = BPC pago no mês na UF (MDS MI Social, soma dos municípios, campo bpc_val_f). inss_annual_aeps = benefícios emitidos no ano pela AEPS, tabela B.15, que INCLUI o BPC: é o conceito usado em data/uf-balance-2024.json. Não somar inss_annual_aeps com bpc.",
    "transfers_partial_month": (f"O arquivo de transferências de {TR_LAST} foi gerado pelo Portal durante o próprio mês (coleta em {TODAY}): o mês está incompleto." if TR_LAST >= TODAY[:7] and TR_LAST in TR_AVAILABLE else None),
    "transfers_missing_months": ({"months": TR_MISSING, "reason": "arquivo publicado pelo Portal, mas não agregado nesta coleta: o servidor de downloads da CGU respondeu com uma verificação anti-robô (AWS WAF) em vez do ZIP; rodar agg_transfers_monthly.py de novo e reconstruir"} if TR_MISSING else None),
    "transfers_without_uf": "Três transferências grandes a estados e municípios estão no Portal sem UF: cessão onerosa do pré-sal (ação 00RX, 2019-12, R$ 10,7 bi sem UF; outros R$ 1,1 bi vieram com UF e estão nas UFs), auxílio da LC 173/2020 (ação 00S7, quatro parcelas de R$ 15,0 bi de 2020-06 a 2020-09) e LC 176 (00SE, de 2020-12 em diante). A LC 176 vem por UF do Tesouro, como em 2024. As outras duas não têm fonte aberta por UF no Tesouro Transparente: ficam fora das UFs, listadas em national.transfers_public_recipients_without_uf.",
    "lc176_tesouro_last_month": f"O Tesouro publicou a LC 176 por UF até {TT_LAST}; nos meses de transferências depois disso a categoria lc176_kandir_compensation fica em zero por falta de dado, não por falta de pagamento." if TT_LAST < TR_LAST else None,
    "lc176_tesouro_vs_portal": lc176_check,
    "fundeb_old_code": "Até 2020 a complementação da União ao Fundeb usava a ação 0E36; ela foi classificada em fundeb_federal_complement, a mesma categoria da ação 00SB (Fundeb da EC 108/2020).",
    "population_break_2021_2022": "Ver data/series/population.json: as estimativas de 2019 a 2021 vêm da base do Censo 2010 e a de 2022 é o Censo 2022; o total do país cai de 213,3 mi para 203,1 mi entre os dois anos. Valores per capita de anos diferentes não são comparáveis sem essa ressalva.",
    "beps_duplicate_uploads": {"rule": "quando um mês tem mais de um arquivo do BEPS com números diferentes, vale o enviado depois (sufixo -1 ou _a)", "months": beps_dupes},
}
sources = [
    {"field": "uf.*.federal_revenue", "url": "https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv", "coverage": [FIRST, REV_LAST], "note": "Receita Federal, Arrecadação por Estado, mensal, por tributo, preços correntes. Chaves de by_tax: pipelines/taxmap.py."},
    {"field": "national.federal_revenue_total_receita (2019 a 2025)", "url": "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/serie-historica/arrecadacao-das-receitas-federais-1994-a-2025.xlsx", "note": "Linha TOTAL GERAL, R$ milhões."},
    {"field": "national.federal_revenue_total_receita (2026)", "url": PDF_URL, "note": "Análise da Arrecadação das Receitas Federais, agosto de 2026, Tabela III, coluna Total Geral, R$ milhões."},
    {"field": "uf.*.transfers", "url": "https://portaldatransparencia.gov.br/download-de-dados/transferencias/AAAAMM", "coverage": [FIRST, TR_LAST], "note": "CGU, Portal da Transparência, Transferências, coluna VALOR TRANSFERIDO, arquivos de 201901 a " + TR_MONTHS[-1] + ". Regras em pipelines/series/classify_transfers.py."},
    {"field": "uf.*.transfers.by_category.lc176_kandir_compensation", "url": "https://www.tesourotransparente.gov.br/ckan/dataset/f85b6632-1c9c-4beb-9e60-72e91156c984/resource/a58f5b6d-4e1f-4571-9597-3c8cca6d8259/download/lc176est.csv", "note": "Tesouro Nacional, LC176_EST (governo estadual) e LC176_MUN (municípios): https://www.tesourotransparente.gov.br/ckan/dataset/f85b6632-1c9c-4beb-9e60-72e91156c984/resource/b05b73e1-6189-4be3-8ea6-98d864db8a3c/download/lc176mun.csv"},
    {"field": "uf.*.bolsa_familia", "url": "https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&fq=anomes_s:AAAA*&fl=codigo_ibge,sigla_uf,anomes_s,valor_repassado_bolsa_familia_f,pab_valor_pago_d,pab_extraordinario_valor_pago_d&rows=200000&wt=csv", "coverage": [FIRST, BF_LAST], "note": "MDS, Matriz de Informação Social, soma dos municípios de cada UF."},
    {"field": "uf.*.bpc", "url": "https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&fq=anomes_s:AAAA*&fl=codigo_ibge,sigla_uf,anomes_s,bpc_val_f&rows=200000&wt=csv", "coverage": [FIRST, BPC_LAST], "note": "MDS, Matriz de Informação Social, campo bpc_val_f, soma dos municípios."},
    {"field": "uf.*.inss", "url": "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/Dados-estatisticos-previdencia-social-e-inss/boletins-da-previdencia-social", "coverage": [FIRST, INSS_LAST], "note": "Boletim Estatístico da Previdência Social (BEPS), XLS mensal, tabela 19 (inss) e tabela 18 (inss_gross_benefit_value), coluna Valor Total. Arquivo usado em cada mês: files.", "files": beps_files},
    {"field": "uf.*.inss_annual_aeps", "url": "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/Dados-estatisticos-previdencia-social-e-inss/anuarios-da-previdencia-social/anuarios-da-previdencia-social", "note": "AEPS, tabela B.15, valor de benefícios emitidos no ano (R$ mil convertidos para R$), edição de cada ano.", "files": aeps["files"]},
]
coverage = {"federal_revenue": [FIRST, REV_LAST], "transfers": [FIRST, TR_LAST], "bolsa_familia": [FIRST, BF_LAST], "bpc": [FIRST, BPC_LAST],
            "inss": [FIRST, INSS_LAST], "inss_gross_benefit_value": [min(inss18), max(inss18)] if inss18 else None, "inss_annual_aeps": ["2019", "2024"]}
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump({"months": MONTHS, "currency": "BRL, valores correntes (sem correção pela inflação)", "collected_at": TODAY, "coverage": coverage,
           "uf": out_uf, "national": national, "flags": flags, "sources": sources}, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
print("written", OUT, os.path.getsize(OUT), "bytes; coverage", coverage)
