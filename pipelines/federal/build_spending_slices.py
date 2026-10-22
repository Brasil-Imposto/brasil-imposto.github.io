"""Where the União's money goes, by month, 2019 onward -> data/series/union-spending-slices.json (the home "cake").

Reads the Tesouro base "Despesas e Transferências Totais da União" already cached by pipelines/ug/agg_dtt_monthly.py
(data/ug/cache/dtt_monthly_YYYY.json.gz: payments by month, órgão, unidade, grupo, modalidade, ação, Categoria RTN).
Every row goes to exactly one slice, in this order: Câmara and Senado (órgãos 1000 and 2000, everything they pay except
financial rows);
party funds (ações 0413 fundo partidário and 0EB8 fundo eleitoral); then by the RTN category into the main slices
(transfers, INSS, health, education, social assistance, unemployment insurance, active servants, retired servants,
court orders), by a closed table of category names (MAIN_CATEGORY); an unknown category stops the build. Owner, 2026-10-06 (D99): nothing unrelated shares a slice. The rest is split so that every slice is one
thing: each specific RTN program category (servant benefits, Pronaf, Lei Kandir, Fundo Constitucional do DF...) is its
own slice, its "créditos extraordinários" variant joins it; the generic area categories (Transporte, Defesa, Ciência e
Tecnologia, Administração, Segurança Pública) and the RTN's own catch-all ("Demais") are split by the ministry that paid.
Financial rows (debt amortization and other "N/A") are left out; interest comes from the Banco Central series in
union.json, as in the account above the cake. Category labels change across years (Roman numerals until 2023, "nan" in
2024), so they are normalized before matching.
Each slice also carries its payments by budget action (and by ministry for program slices), month by month, so the
site can open the detail of any slice for any period. Action titles are the official ones from SIOP
(data/federal/action-titles.json, by pipelines/federal/fetch_action_titles.py).
Checks (nothing is written unless they pass): each month the slices add up to the base's own total, to the cent
(Decimal); each slice's actions add up to the slice, to the cent; each year the base matches the Tesouro account (RTN,
union.json) within 0,5%. --control drops one category from the classification; the first check must fail.
Run: python3 pipelines/federal/build_spending_slices.py [--control]
"""
import gzip, json, re, sys, unicodedata
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "data" / "ug" / "cache"
OUT = ROOT / "data" / "series" / "union-spending-slices.json"
CONTROL = "--control" in sys.argv

MAIN = {  # key -> label shown on the site
    "transfers": "Transferências por repartição de receita (estados, municípios e fundos regionais FNE, FNO e FCO)",
    "inss": "Previdência (INSS): benefícios do regime geral, inclusive decisões judiciais",
    "health": "Saúde (SUS)",
    "education": "Educação",
    "social": "Assistência social: Bolsa Família, BPC e outros",
    "unemployment": "Seguro-desemprego e abono salarial",
    "active": "Servidores ativos (civis e militares)",
    "retirees": "Aposentados e pensionistas do serviço público (civis e militares)",
    "courts": "Decisões judiciais (precatórios), fora as de aposentadorias do INSS e do BPC",
    "congress": "Câmara dos Deputados e Senado Federal",
    "parties": "Partidos políticos: fundo partidário e fundo eleitoral",
}
CONGRESS = {"1000", "2000"}
PARTIES = {"0413", "0EB8"}
AREA = ("Transporte", "Defesa", "Ciência e Tecnologia", "Administração", "Segurança Pública")
# Ministry spending outside the main slices goes to the ministry that paid; health and education ministries' own
# leftovers join the health and education slices so the same area never shows twice.
MINISTRY_TO_MAIN = {"36000": "health", "26000": "education"}
FORMER = {"25000": "de 2019 a 2022, Ministério da Economia", "39000": "de 2019 a 2022, Ministério da Infraestrutura"}
MINISTRY_SAME = {"38000": "40000"}  # the same ministry under an older code
MINISTRY = {
    "25000": "Ministério da Fazenda",
    "52000": "Ministério da Defesa",
    "39000": "Ministério dos Transportes",
    "53000": "Ministério da Integração e do Desenvolvimento Regional",
    "32000": "Ministério de Minas e Energia",
    "56000": "Ministério das Cidades",
    "24000": "Ministério da Ciência, Tecnologia e Inovação",
    "30000": "Ministério da Justiça e Segurança Pública",
    "22000": "Ministério da Agricultura e Pecuária",
    "35000": "Ministério das Relações Exteriores",
    "33000": "Ministério da Previdência Social",
    "47000": "Ministério do Planejamento e Orçamento",
    "40000": "Ministério do Trabalho e Emprego",
    "55000": "Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome",
    "44000": "Ministério do Meio Ambiente e Mudança do Clima",
    "20000": "Presidência da República",
    "46000": "Ministério da Gestão e da Inovação em Serviços Públicos",
    "49000": "Ministério do Desenvolvimento Agrário e Agricultura Familiar",
    "54000": "Ministério do Turismo",
    "41000": "Ministério das Comunicações",
    "42000": "Ministério da Cultura",
    "51000": "Ministério do Esporte",
    "68000": "Ministério de Portos e Aeroportos",
    "63000": "Advocacia-Geral da União",
    "28000": "Ministério do Desenvolvimento, Indústria, Comércio e Serviços",
    "81000": "Ministério dos Direitos Humanos e da Cidadania",
    "84000": "Ministério dos Povos Indígenas",
    "25201": "Banco Central do Brasil",
    "58000": "Ministério da Pesca e Aquicultura",
    "69000": "Ministério do Empreendedorismo, da Microempresa e da Empresa de Pequeno Porte",
    "37000": "Controladoria-Geral da União",
    "65000": "Ministério das Mulheres",
    "67000": "Ministério da Igualdade Racial",
    "57000": "Ministério das Mulheres, da Igualdade Racial, da Juventude e dos Direitos Humanos",
}
# Every paying body in the base, by its proper name (the base writes them in capitals, abbreviated and without accents).
BODY = {**MINISTRY, "1000": "Câmara dos Deputados", "2000": "Senado Federal", "3000": "Tribunal de Contas da União", "10000": "Supremo Tribunal Federal",
        "11000": "Superior Tribunal de Justiça", "12000": "Justiça Federal", "13000": "Justiça Militar", "14000": "Justiça Eleitoral",
        "15000": "Justiça do Trabalho", "16000": "Justiça do Distrito Federal e dos Territórios", "17000": "Conselho Nacional de Justiça",
        "26000": "Ministério da Educação", "29000": "Defensoria Pública da União", "34000": "Ministério Público da União", "36000": "Ministério da Saúde",
        "38000": "Ministério do Trabalho e Emprego", "59000": "Conselho Nacional do Ministério Público",
        "N/A": "Órgão não informado na base do Tesouro", None: "Órgão não informado na base do Tesouro", "None": "Órgão não informado na base do Tesouro"}
# RTN program categories with a plainer label; the rest keep the Tesouro's own words.
PROGRAM = {
    "Apoio Fin. Municípios / Estados": "Apoio financeiro a estados e municípios (além dos repasses obrigatórios)",
    "Benefícios a servidores públicos": "Benefícios a servidores públicos",
    "Benefícios a serv públicos": "Benefícios a servidores públicos",
    "Pronaf": "Pronaf (crédito à agricultura familiar)",
    "Compensação ao RGPS pelas Desonerações da Folha": "Desoneração da folha: o Tesouro cobre a contribuição que as empresas deixaram de pagar ao INSS",
    "Proagro": "Proagro (seguro da produção rural)",
    "Lei Kandir (LC nº 87/96 e 102/00) e LC nº 176 de 2020": "Compensação aos estados pela Lei Kandir",
    "Fundo Constitucional DF": "Fundo Constitucional do Distrito Federal",
    "Equalização de invest. rural e agroindustrial": "Equalização de juros do crédito rural (investimento)",
    "Transferências Multas ANEEL": "Repasse de multas da ANEEL",
    "Equalização de custeio agropecuário": "Equalização de juros do crédito rural (custeio)",
    "Fabricação de Cédulas e Moedas": "Fabricação de cédulas e moedas",
    "Programa de Sustentação ao Investimento - PSI": "Programa de Sustentação do Investimento (PSI)",
    "Fundo Setorial Audiovisual (FSA)": "Fundo Setorial do Audiovisual (FSA)",
    "Benefícios de Legislação Especial e Indenizações": "Benefícios de legislação especial e indenizações",
    "Complemento do FGTS": "Complemento do FGTS (LC 110/2001)",
    "Complemento do FGTS (LC nº 110/01)": "Complemento do FGTS (LC 110/2001)",
    "Fundo da terra/ INCRA": "Fundo de Terras e da Reforma Agrária (INCRA)",
    "Proex": "Proex (apoio às exportações)",
    "Anistiados": "Indenizações a anistiados políticos",
    "Transferências ANA": "Repasses da Agência Nacional de Águas (ANA)",
    "Equalização Aquisições do Governo Federal": "Equalização de preços nas aquisições do governo federal",
    "Garantia à Sustentação de Preços": "Garantia de sustentação de preços",
    "Sudene": "Sudene",
    "Sudene (Microcrédito Produtivo Orientado)": "Sudene",
    "Equalização dos Fundos FDA/FDNE/FDCO": "Equalização dos fundos de desenvolvimento regional (FDA, FDNE, FDCO)",
    "Equalização Empréstimo do Governo Federal": "Equalização de empréstimos do governo federal",
    "Operações de crédito destinadas a Pessoas com deficiência (EQPCD)": "Crédito para pessoas com deficiência (equalização)",
    "Receitas de Recuperação de Subvenções": "Recuperação de subvenções (devolução)",
}

# Audit of 2026-10-06: the main slices take only these RTN categories, by exact name (as normalized by clean(), any
# letter case). A keyword test put "Legislativo" (Judiciary, MPU, DPU and TCU running costs) and the PESA ("saneamento
# de ativos") under "Ativo". A category outside this table and outside the known program and area categories below
# stops the build, so a new name never becomes a slice, or lands in a main slice, without a decision.
MAIN_CATEGORY = {
    "Benefícios Previdenciários - Urbano": "inss", "Benefícios Previdenciários - Rural": "inss",
    "Benefícios Previdenciários - Urbano e Rural": "inss", "Benefícios Previdenciários - Sentenças e precatórios": "inss",
    "Saúde": "health", "Saúde (Créditos Extraordinários)": "health",
    "Educação": "education", "Educação (Créditos Extraordinários)": "education", "FUNDEB (Complem. União)": "education",
    "FIES": "education", "Impacto Primário do FIES": "education",
    "Assistência Social": "social", "Assistência Social (Créditos Extraordinários)": "social",
    "Benefícios de Prestação Continuada da LOAS/RMV - Benefícios": "social",
    "Benefícios de Prestação Continuada da LOAS/RMV - Sentenças e Precatórios": "social",
    "Bolsa Família e Auxílio Brasil": "social", "Bolsa Família e Aux Brasil (Créd Extraord)": "social",
    "Abono e Seguro Desemprego - Benefícios": "unemployment", "Abono e Seguro Desemprego - Sentenças e Precatórios": "unemployment",
    "Aposentadorias e pensões civis": "retirees", "Reformas e pensões militares": "retirees",
    "Ativo Civil": "active", "Ativo Militar": "active",
    "Sentenças Judiciais e Precatórios - OCC": "courts", "Sentenças e Precatórios": "courts",
}
MAIN_CATEGORY = {k.lower(): v for k, v in MAIN_CATEGORY.items()}
KNOWN_PROGRAM = {k.lower() for k in PROGRAM} | {k.lower() for k in (
    "Cacau", "Funcafé", "PNAFE", "Revitaliza", "Álcool", "Legislativo, Judiciário, MPU e DPU",
    "Programa especial de saneamento de ativos (PESA)", "Financiamento de Campanha Eleitoral")}
unknown_category = set()
# Notes shown in the detail of a slice (audit of 2026-10-06).
NOTE = {
    "courts": "Pelo Resultado do Tesouro Nacional de agosto de 2026, as sentenças judiciais e precatórios de todas as áreas "
              "somaram R$ 93,3 bi de janeiro a agosto de 2026: custeio e capital R$ 38,2 bi, pessoal R$ 11,1 bi, benefícios do "
              "INSS R$ 39,6 bi e BPC R$ 4,4 bi. Os do INSS estão na fatia da Previdência e os do BPC na da Assistência social.",
    PROGRAM["Compensação ao RGPS pelas Desonerações da Folha"]:
              "O dinheiro passa pelo INSS: sai do Tesouro para o fundo do regime geral (RGPS), que paga os benefícios da fatia "
              "da Previdência. Quem pagou menos contribuição sobre a folha foram as empresas da desoneração.",
}
# Rows without a budget action (the cache writes an empty cell as the text "None"): named by their RTN category.
NO_ACTION = {"Impacto Primário do FIES": "Impacto primário do FIES, sem ação orçamentária",
             "Superávit dos Fundos Constitucionais": "Devolução do superávit dos fundos constitucionais"}
def no_action(a):
    return a is None or str(a).strip() in ("", "None", "nan", "N/A")

def clean(c):
    c = re.sub(r"^[IVX0-9.]+\s*-?\s*", "", str(c)).strip()
    for s in ("(Discricionárias)", "(Obrigatórias com Controle de Fluxo)"):
        c = c.replace(s, "")
    for s in ("Discricionárias - ", "Obrigatórias com Controle de Fluxo - ", "Pessoal e Encargos Sociais - "):
        c = c.replace(s, "")
    return re.sub(r"\s+", " ", c).strip(" -")

def kind(c):
    c = str(c).strip()
    if c in ("N/A", "nan", "None", ""):
        return "fin"
    return "tr" if re.match(r"^(I|1)\.", c) and not c.startswith("II") else "prim"

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def slice_of(orgao, acao, cat):
    if orgao in CONGRESS:
        return "congress"
    if acao in PARTIES:
        return "parties"
    k = kind(cat)
    if k == "fin":
        return None
    if k == "tr":
        return "transfers"
    c = clean(cat)
    if CONTROL and c.startswith("Saúde"):
        return "DROPPED"
    if c.lower() in MAIN_CATEGORY:
        return MAIN_CATEGORY[c.lower()]
    base = re.sub(r"\s*\((Créditos Extraordinários|Créd Extraord)\)", "", c).strip()
    if base.startswith("Demais") or base in AREA:
        org = MINISTRY_SAME.get(orgao, orgao)
        if org in MINISTRY_TO_MAIN:
            return MINISTRY_TO_MAIN[org]
        return f"ministry:{org}"
    if base.lower() not in KNOWN_PROGRAM:
        unknown_category.add(c)
    return f"program:{slug(PROGRAM.get(base, base))}"

union = json.loads((ROOT / "data" / "series" / "union.json").read_text(encoding="utf-8"))
months, vals, labels = [], defaultdict(dict), {}
acts = defaultdict(lambda: defaultdict(dict))      # slice -> ação -> month -> value
orgs = defaultdict(lambda: defaultdict(dict))      # program slice -> ministry -> month -> value
act_name, org_name, unnamed_body = {}, {}, set()
fails, base_total = [], {}
for y in range(2019, 2100):
    f = CACHE / f"dtt_monthly_{y}.json.gz"
    if not f.exists():
        break
    d = json.load(gzip.open(f)); N = d["names"]
    acc = defaultdict(lambda: defaultdict(Decimal)); tot = defaultdict(Decimal)
    a_acc = defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal)))
    o_acc = defaultdict(lambda: defaultdict(lambda: defaultdict(Decimal)))
    for mo, orgao, uo, grupo, mod, acao, cat, v in d["agg"]:
        # Financial rows ("N/A") are out for everyone, Câmara and Senado included: their only such row is action 09HB, the
        # União's intra-budget contribution to its own servants' pension regime (audit of 2026-10-06).
        if kind(cat) == "fin":
            continue
        v = Decimal(str(v)); tot[mo] += v
        s = slice_of(orgao, acao, cat)
        if s == "DROPPED":
            continue
        acc[mo][s] += v
        if no_action(acao):
            base = re.sub(r"\s*\((Créditos Extraordinários|Créd Extraord)\)", "", clean(cat)).strip()
            acao = "no-action:" + NO_ACTION.get(base, f"{PROGRAM.get(base, base)}, sem ação orçamentária")
        a_acc[mo][s][acao] += v
        act_name[acao] = N["acao"].get(acao, acao)
        if s.startswith("program:"):
            o = MINISTRY_SAME.get(orgao, orgao); o_acc[mo][s][o] += v
            org_name[o] = BODY.get(o) or N["orgao"].get(orgao, orgao) or "Órgão não informado na base do Tesouro"
            if o not in BODY: unnamed_body.add(o)
        if s.startswith("ministry:"):
            labels[s] = MINISTRY.get(s.split(":")[1]) or N["orgao"].get(orgao, orgao).title()
        elif s.startswith("program:"):
            base = re.sub(r"\s*\((Créditos Extraordinários|Créd Extraord)\)", "", clean(cat)).strip()
            labels[s] = PROGRAM.get(base, base)
    for mo in sorted(acc):
        ym = f"{y}-{mo:02d}"; months.append(ym)
        if sum(acc[mo].values()) != tot[mo]:
            fails.append(f"{ym}: slices {sum(acc[mo].values())} != base total {tot[mo]}")
        for s, v in acc[mo].items():
            vals[s][ym] = float(round(v, 2))
            if sum(a_acc[mo][s].values()) != v:
                fails.append(f"{ym} {s}: actions {sum(a_acc[mo][s].values())} != slice {v}")
            for a, av in a_acc[mo][s].items():
                if av:
                    acts[s][a][ym] = float(round(av, 2))
            for o, ov in o_acc[mo][s].items():
                if ov:
                    orgs[s][o][ym] = float(round(ov, 2))
        base_total[ym] = float(tot[mo])
    # The base against the Tesouro account (RTN), year by year: transfers plus primary spending.
    ix = {m: i for i, m in enumerate(union["months"])}
    ys = [m for m in months if m.startswith(str(y))]
    rtn = sum(union["primary_spending"][ix[m]] + union["transfers_to_subnationals"][ix[m]] for m in ys)
    base = sum(base_total[m] for m in ys)
    if abs(base / rtn - 1) > 0.005:
        fails.append(f"{y}: base {base / 1e9:.1f} bi vs RTN {rtn / 1e9:.1f} bi")

if unknown_category:
    fails.insert(0, "RTN categories not in the classification table (add each to MAIN_CATEGORY or KNOWN_PROGRAM): " + "; ".join(sorted(unknown_category)))
if fails:
    print("CHECK FAILED:\n- " + "\n- ".join(fails[:12]) + ("\n- ..." if len(fails) > 12 else "")); sys.exit(1)
if CONTROL:
    print("control run passed the checks: the identity check is not working"); sys.exit(2)

mi = {m: i for i, m in enumerate(months)}
# Official action titles (SIOP, by year): the title of the latest year in which the action was paid in that slice.
TITLES = json.loads((ROOT / "data" / "federal" / "action-titles.json").read_text(encoding="utf-8"))["titles"]
PORTAL = {}
for f in sorted(CACHE.glob("despug_*.json.gz")):  # Portal da Transparência monthly files: full action names, in capitals
    PORTAL.update(json.load(gzip.open(f))["names"].get("acao") or {})
def title(a, series):
    # SIOP writes some titles with an en dash; the site prints a plain hyphen (no dashes in the site's text).
    return (_title(a, series) or str(a)).replace(chr(0x2013), "-").replace(chr(0x2014), "-")
def _title(a, series):
    if str(a).startswith("no-action:"):
        return str(a)[len("no-action:"):]
    if no_action(a):
        return "Sem ação orçamentária informada na base do Tesouro"
    for y in sorted({m[:4] for m in series}, reverse=True):
        if a in TITLES.get(y, {}):
            return TITLES[y][a]
    for y in sorted(TITLES, reverse=True):
        if a in TITLES[y]:
            return TITLES[y][a]
    untitled.add(a)
    return PORTAL.get(a) or act_name.get(a) or a
untitled = set()
sparse = lambda series: [[mi[m], v] for m, v in sorted(series.items(), key=lambda x: mi[x[0]])]
order = sorted(vals, key=lambda s: -sum(vals[s].values()))
def entry(s):
    group = "main" if s in MAIN else s.split(":")[0]
    e = {"label": MAIN.get(s) or labels[s], "group": group, "values": [vals[s].get(m, 0.0) for m in months],
         "actions": sorted(([a if not (no_action(a) or str(a).startswith("no-action:")) else "", title(a, ser), sparse(ser)] for a, ser in acts[s].items()), key=lambda x: -sum(v for _, v in x[2]))}
    if e["label"] in NOTE or s in NOTE:
        e["note"] = NOTE.get(s) or NOTE[e["label"]]
    if group == "ministry":
        e["note"] = "Custeio, investimentos e programas do ministério. Salários, aposentadorias e benefícios de servidores estão nas fatias próprias."
        if s.split(":")[1] in FORMER:
            e["former"] = FORMER[s.split(":")[1]]
    if group == "program":
        e["ministries"] = sorted(([o, org_name.get(o, o), sparse(ser)] for o, ser in orgs[s].items()), key=lambda x: -sum(v for _, v in x[2]))
    return e
out = {
    "title": "Para onde vai o dinheiro da União, por mês",
    "source": {"name": "Tesouro Nacional, Despesas e Transferências Totais da União (pagamentos totais)",
               "url": "https://www.tesourotransparente.gov.br/ckan/dataset/despesas-e-transferencias-totais",
               "interest": "Banco Central, juros nominais do Governo Central (data/series/union.json)"},
    "rule": ("Cada pagamento entra em uma fatia só: primeiro Câmara e Senado (tudo o que os dois pagam: funcionamento, salários e aposentadorias), "
             "depois os fundos partidário e eleitoral, depois pela categoria do Resultado do Tesouro Nacional. Cada programa que o Tesouro nomeia tem fatia própria; "
             "o gasto que o Tesouro só classifica por área (transporte, defesa, ciência, administração, segurança e demais) fica com o ministério que pagou. "
             "Os pagamentos financeiros (amortização da dívida e outros) ficam fora; os juros vêm do Banco Central, como na conta da União. "
             "Salários de médicos e professores federais estão em Servidores ativos, como no Tesouro."),
    "months": months,
    "slices": {s: entry(s) for s in order},
    "base_total": [base_total[m] for m in months],
    "check": {"identity": "as fatias somam o total da base ao centavo em todos os meses", "actions": "as ações de cada fatia somam a fatia ao centavo",
              "rtn": "cada ano bate com o RTN em até 0,5%", "control": "--control tira uma categoria; a checagem tem de falhar"},
}
OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"wrote {OUT.relative_to(ROOT)}: {len(months)} months, {months[0]} to {months[-1]}, {len(order)} slices "
      f"({sum(1 for s in order if s in MAIN)} main, {sum(1 for s in order if s.startswith('program:'))} programs, {sum(1 for s in order if s.startswith('ministry:'))} ministries), "
      f"{OUT.stat().st_size // 1024} KB; actions without an official SIOP title (Tesouro name kept): {len(untitled)}; paying bodies without a proper name: {sorted(unnamed_body)}")
