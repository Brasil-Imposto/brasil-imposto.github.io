"""Builds the data of the "Os 3 Poderes" design preview: the federal powers as a tree, from the President, the heads of
Congress and the head of the STF down to each budget organ and unit, with what each spends.

Money: the Tesouro base "Despesas e Transferências Totais da União" (data/ug/cache/dtt_monthly_YYYY.json.gz), direct
application only (modality 90), so transfers to states and municipalities never count as an organ's spending. Personnel is
group 1, split by the RTN category the base gives each row (active, retired and pensioners, court orders: D72 never mixes
them); running costs are group 3 and investment group 4. Two rows of the Fazenda are not its own people: the Fundo
Constitucional do DF (unit 73901) and the court orders paid for personnel (unit 71103) become their own nodes.
People: data/federal/servants-by-branch.json (each count with its own date and source) and the Congress quotas from
data/federal/federal-section.json. Anything the project has not collected is listed per node in "to_collect", never filled.

Usage: uv run python docs/superpowers/tools/build-tres-poderes-data.py [YEAR] [LAST_MONTH]
Writes docs/superpowers/previews/assets/tres-poderes-data.js
"""
import collections, gzip, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
YEAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
LAST = int(sys.argv[2]) if len(sys.argv) > 2 else 8
OUT = ROOT / "docs" / "superpowers" / "previews" / "assets" / "tres-poderes-data.js"
MES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

dt = json.load(gzip.open(ROOT / "data" / "ug" / "cache" / f"dtt_monthly_{YEAR}.json.gz", "rt"))
months = sorted({r[0] for r in dt["agg"]})
if not (LAST in months):
    raise SystemExit(f"{YEAR}-{LAST:02d} is not in the Tesouro base (months {months})")
ORG_NAME, UO_NAME = dt["names"]["orgao"], dt["names"]["uo"]

LEGISLATIVE = {"1000": "Câmara dos Deputados", "2000": "Senado Federal", "3000": "Tribunal de Contas da União"}
JUDICIARY = {"10000": "Supremo Tribunal Federal", "11000": "Superior Tribunal de Justiça", "12000": "Justiça Federal",
             "13000": "Justiça Militar", "14000": "Justiça Eleitoral", "15000": "Justiça do Trabalho",
             "16000": "Justiça do Distrito Federal e dos Territórios", "17000": "Conselho Nacional de Justiça"}
ESSENTIAL = {"34000": "Ministério Público da União", "29000": "Defensoria Pública da União"}
# The base keeps some organs under older names; these are the names of the organs in 2026.
EXECUTIVE_NAMES = {
    "20000": "Presidência da República", "22000": "Ministério da Agricultura e Pecuária", "24000": "Ministério da Ciência, Tecnologia e Inovação",
    "25000": "Ministério da Fazenda", "26000": "Ministério da Educação", "28000": "Ministério do Desenvolvimento, Indústria, Comércio e Serviços",
    "30000": "Ministério da Justiça e Segurança Pública", "32000": "Ministério de Minas e Energia", "33000": "Ministério da Previdência Social",
    "35000": "Ministério das Relações Exteriores", "36000": "Ministério da Saúde", "37000": "Controladoria-Geral da União",
    "39000": "Ministério dos Transportes", "40000": "Ministério do Trabalho e Emprego", "41000": "Ministério das Comunicações",
    "42000": "Ministério da Cultura", "44000": "Ministério do Meio Ambiente e Mudança do Clima", "46000": "Ministério da Gestão e da Inovação em Serviços Públicos",
    "47000": "Ministério do Planejamento e Orçamento", "49000": "Ministério do Desenvolvimento Agrário e Agricultura Familiar", "51000": "Ministério do Esporte",
    "52000": "Ministério da Defesa", "53000": "Ministério da Integração e do Desenvolvimento Regional", "54000": "Ministério do Turismo",
    "55000": "Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome", "56000": "Ministério das Cidades",
    "58000": "Ministério da Pesca e Aquicultura", "63000": "Advocacia-Geral da União", "68000": "Ministério de Portos e Aeroportos",
    "81000": "Ministério dos Direitos Humanos e da Cidadania", "84000": "Ministério dos Povos Indígenas"}
# Units whose name in the base lost its accents; the rest keep the base name until the data round.
UNIT_NAMES = {"52121": "Comando do Exército", "52131": "Comando da Marinha", "52111": "Comando da Aeronáutica", "52101": "Ministério da Defesa (administração)",
              "20101": "Presidência da República (gabinete e secretarias)", "60101": "Gabinete da Vice-Presidência da República",
              "20118": "Agência Brasileira de Inteligência (ABIN)", "25103": "Secretaria Especial da Receita Federal do Brasil",
              "15101": "Tribunal Superior do Trabalho", "14101": "Tribunal Superior Eleitoral", "34101": "Ministério Público Federal",
              "34104": "Ministério Público do Trabalho", "34103": "Ministério Público do Distrito Federal e dos Territórios", "34102": "Ministério Público Militar"}
SPLIT_UNITS = {"73901": "Fundo Constitucional do Distrito Federal", "71103": "Sentenças judiciais e precatórios pagos pela Fazenda"}
SMALL = {"da", "de", "do", "das", "dos", "e", "a", "o", "em", "para"}


def title(s):
    words = s.replace(".", ". ").replace(",", ", ").split()
    return " ".join(w.lower() if (w.lower() in SMALL and i) else w.capitalize() for i, w in enumerate(words))


def kind_of(cat):
    if cat.startswith(("2.2.1", "2.2.2")): return "personnel_active"
    if cat.startswith(("2.2.3", "2.2.4")): return "personnel_retired"
    if cat.startswith("2.2.5"): return "personnel_court_orders"
    return "personnel_other"


COST_KEYS = ["personnel_active", "personnel_retired", "personnel_court_orders", "personnel_other", "operating", "investment"]
cost = collections.defaultdict(lambda: collections.defaultdict(lambda: dict.fromkeys(COST_KEYS, 0)))  # org -> uo -> cost
for mon, org, uo, g, mo, ac, cat, v in dt["agg"]:
    if mo != "90" or mon > LAST or g not in ("1", "3", "4"): continue
    k = kind_of(cat) if g == "1" else "operating" if g == "3" else "investment"
    cost[org][uo][k] += v


def total(c):
    c = {k: round(v, 2) for k, v in c.items()}
    c["personnel"] = round(c["personnel_active"] + c["personnel_retired"] + c["personnel_court_orders"] + c["personnel_other"], 2)
    c["all"] = round(c["personnel"] + c["operating"] + c["investment"], 2)
    return c


def add(a, b):
    return {k: a.get(k, 0) + b.get(k, 0) for k in COST_KEYS}


def unit_nodes(org, skip=()):
    out = []
    for uo, c in cost[org].items():
        if uo in skip: continue
        out.append({"id": f"uo:{uo}", "name": UNIT_NAMES.get(uo) or title(UO_NAME.get(uo, uo)), "kind": "unit", "cost": total(c)})
    return sorted(out, key=lambda n: -n["cost"]["all"])


def organ(org, name, **extra):
    c = {k: 0 for k in COST_KEYS}
    for uo, x in cost[org].items():
        if uo not in SPLIT_UNITS: c = add(c, x)
    n = {"id": f"org:{org}", "name": name, "kind": "organ", "cost": total(c), "children": unit_nodes(org, SPLIT_UNITS)}
    n.update(extra)
    return n


def group(nid, name, children, **extra):
    c = {k: 0 for k in COST_KEYS}
    for ch in children: c = add(c, {k: ch["cost"][k] for k in COST_KEYS})
    n = {"id": nid, "name": name, "kind": extra.pop("kind", "group"), "cost": total(c), "children": sorted(children, key=lambda x: -x["cost"]["all"])}
    n.update(extra)
    return n


S = json.loads((ROOT / "data" / "federal" / "servants-by-branch.json").read_text(encoding="utf-8"))
F = json.loads((ROOT / "data" / "federal" / "federal-section.json").read_text(encoding="utf-8"))
B, H, CT, CNJ = S["branches"], S["details"]["legislative_by_house"], S["details"]["judiciary_active_by_court"], S["judiciary_cost_per_person_cnj"]
src = lambda d: {"body": d["source"]["body"], "document": d["source"]["document"], "url": d["source"]["url"]} if isinstance(d.get("source"), dict) else None
people = lambda b, as_of=None: {"active": b.get("active"), "retired": b.get("retired"), "pensioners": b.get("pensioners"), "as_of": as_of or b.get("as_of"), "source": src(b)}
cnj = lambda k: {"per_magistrate_month": CNJ["courts"][k]["per_magistrate"], "per_servant_month": CNJ["courts"][k]["per_servant"], "as_of": CNJ["as_of"], "what": CNJ["what"]}
court = lambda k: {"magistrates": CT["courts"][k]["magistrates"], "servants": CT["courts"][k]["servants"], "as_of": CT["as_of"]}
PERSON_PAY = ["subsídio (o salário do cargo)", "auxílios (moradia, saúde, alimentação e outros que o órgão pague)", "gratificações e indenizações",
              "encargos que o órgão paga sobre a folha"]

# ---------- Legislative
house_extra = {
    "1000": {"seats": 513, "seats_what": "deputados federais", "staff": {"career": H["chamber"]["active_career_staff"], "parliamentary_secretaries": H["chamber"]["parliamentary_secretaries"],
             "special_commissioned": H["chamber"]["special_nature_commissioned"], "as_of": H["chamber"]["as_of"]}, "source": src(H["chamber"]),
             "quota": {"what": "Cota para o Exercício da Atividade Parlamentar (CEAP)", "amount": F["parliamentary_quota"]["chamber"]["total"]},
             "head": "Presidente da Câmara", "to_collect": ["o que cada deputado recebe: " + "; ".join(PERSON_PAY), "verba de gabinete por deputado"]},
    "2000": {"seats": 81, "seats_what": "senadores, três por estado (CF art. 46)", "staff": {"career": H["senate"]["active_career_staff"], "commissioned_without_tie": H["senate"]["commissioned_without_tie"],
             "as_of": H["senate"]["as_of"]}, "source": src(H["senate"]),
             "quota": {"what": "Cota para o Exercício da Atividade Parlamentar dos Senadores (CEAPS)", "amount": F["parliamentary_quota"]["senate"]["total"]},
             "head": "Presidente do Senado e do Congresso Nacional", "to_collect": ["o que cada senador recebe: " + "; ".join(PERSON_PAY)]},
    "3000": {"to_collect": ["quantos servidores e ministros o TCU tem e o que cada um recebe"]}}
legislative = group("power:legislativo", "Poder Legislativo", [organ(o, n, **house_extra[o]) for o, n in LEGISLATIVE.items()], kind="power",
                    head="Presidente do Congresso Nacional (o presidente do Senado)", people=people(B["legislative"]))

# ---------- Judiciary
court_extra = {"10000": {"court": court("stf"), "cnj_cost": cnj("superior_courts"), "seats": 11, "seats_what": "ministros", "head": "Presidente do STF"},
               "11000": {"court": court("stj"), "cnj_cost": cnj("superior_courts"), "seats": 33, "seats_what": "ministros"},
               "12000": {"court": court("federal_justice"), "cnj_cost": cnj("federal_justice")},
               "13000": {"court": court("military_justice")},
               "14000": {"court": court("electoral_justice_regional"), "cnj_cost": cnj("electoral_justice")},
               "15000": {"court": court("labor_justice_regional"), "cnj_cost": cnj("labor_justice")},
               "16000": {"court": court("tjdft")}, "17000": {}}
for o, x in court_extra.items():
    x.setdefault("to_collect", ["o que cada magistrado e cada servidor recebe: " + "; ".join(PERSON_PAY)])
judiciary = group("power:judiciario", "Poder Judiciário", [organ(o, n, **court_extra[o]) for o, n in JUDICIARY.items()], kind="power",
                  head="Presidente do Supremo Tribunal Federal", people=people(B["judiciary"]))

# ---------- Functions essential to justice (outside the three powers, CF arts. 127 to 135)
essential = group("power:funcoes", "Funções essenciais à Justiça", [organ(o, n, to_collect=["o que cada membro e cada servidor recebe: " + "; ".join(PERSON_PAY)],
                  people=people(B["mpu" if o == "34000" else "dpu"])) for o, n in ESSENTIAL.items()], kind="power", head="Procurador-Geral da República e Defensor Público-Geral Federal",
                  note="O Ministério Público e a Defensoria não fazem parte de nenhum dos três Poderes (CF, Título IV, Capítulo IV).")

# ---------- Executive: every other organ; the DF fund and the personnel court orders get their own nodes
special = {o for o in list(LEGISLATIVE) + list(JUDICIARY) + list(ESSENTIAL)}
ministries, charges = [], []
for org in cost:
    if org in special: continue
    name = EXECUTIVE_NAMES.get(org) or title(ORG_NAME.get(org, org))
    n = organ(org, name)
    if org not in EXECUTIVE_NAMES and n["cost"]["personnel"] < 1e6:
        n["kind"] = "charge"; charges.append(n)
    else:
        ministries.append(n)
for o in ministries:
    if o["id"] == "org:52000":
        o["people"] = {"active": B["executive_military"]["active"], "retired": B["executive_military"]["retired"], "pensioners": B["executive_military"]["pensioners"],
                       "as_of": B["executive_military"]["as_of"], "source": src(B["executive_military"]), "what": "militares das Forças Armadas"}
        o["ranks"] = {"active_breakdown": B["executive_military"]["active_breakdown"], "average_monthly_brl": B["executive_military"]["average_monthly_brl"]}
    o.setdefault("to_collect", ["quantos servidores o órgão tem e o que cada um recebe: " + "; ".join(PERSON_PAY)])
    if o["id"] == "org:20000":
        o["head"] = "Presidente da República"
        o["to_collect"] = ["o que o presidente e o vice recebem: subsídio e o custo da residência oficial, da segurança e das viagens"] + o["to_collect"]
split = []
for uo, name in SPLIT_UNITS.items():
    c = {k: 0 for k in COST_KEYS}
    for org in cost:
        if uo in cost[org]: c = add(c, cost[org][uo])
    split.append({"id": f"uo:{uo}", "name": name, "kind": "organ", "cost": total(c), "children": [],
                  "note": ("A União paga as polícias e os bombeiros do DF e ajuda em outros serviços públicos dele (CF art. 21, XIV)." if uo == "73901"
                           else "Dívidas que a Justiça mandou a União pagar: de salários e aposentadorias (no pessoal) e outras (no custeio). A base registra na Fazenda, mas não são gasto com os servidores dela.")})
executive = group("power:executivo", "Poder Executivo", ministries + split + ([group("group:encargos", "Encargos da União (sem quadro de pessoal)", charges)] if charges else []),
                  kind="power", head="Presidente da República", people={**people(B["executive_civil"]), "what": "servidores civis (sem os militares)"})

tree = group("root:uniao", "União: os três Poderes e as funções essenciais à Justiça", [executive, legislative, judiciary, essential], kind="root")
check = abs(tree["cost"]["all"] - sum(sum(c.values()) for org in cost.values() for c in org.values())) < 1
if not (check):
    raise SystemExit("the tree does not add up to the base")
data = {"period": f"{MES[0]} a {MES[LAST - 1]} de {YEAR}", "year": YEAR, "months": LAST,
        "source": {"body": "Tesouro Nacional", "document": "Despesas e Transferências Totais da União, aplicação direta (modalidade 90)", "url": dt["url"],
                   "file_last_modified": dt.get("resource_last_modified")},
        "tree": tree}
OUT.write_text("window.TP = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
print(OUT.name, round(OUT.stat().st_size / 1024), "KB |", data["period"], "| total R$", round(tree["cost"]["all"] / 1e9, 1), "bi | personnel R$",
      round(tree["cost"]["personnel"] / 1e9, 1), "bi |", {c["name"]: round(c["cost"]["personnel"] / 1e9, 1) for c in tree["children"]})
