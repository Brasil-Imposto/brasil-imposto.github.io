"""Builds the data of "Os 3 Poderes", design round 2: a tree of positions (cargos), each with its salary and every
allowance at its official value, and the people who hold them in 2026 with what each one actually uses.

Every value comes from an official page or file kept in data/federal/raw-pay/ (fetched on 2026-10-21, SHA-256 recorded):
  camara-mandato.html   Câmara, Portal da Posse, "Exercício do mandato": salary, housing allowance, office budget, Ceap by state
  dep-<id>.html         Câmara, each deputy's page for 2026: salary, official flat, housing allowance, Ceap and office budget used
  mesa-camara-m.json    Câmara open data, Mesa Diretora (who presides)
  mesa-senado.json      Senado open data, Mesa do Senado
  sen-moradia.json      Senado open data, housing allowance and official flat, senator by senator
  ceaps.txt             Senado, table of the senators' quota by state (text of the official PDF)
  dl172.html, l14520.htm  Decreto Legislativo 172/2022 and Lei 14.520/2023 (salaries)
  data/federal/raw/senado-ceaps-2026.csv  Senado, quota spending of 2026, line by line
Counts and averages of servants, military and judges come from data/federal/servants-by-branch.json.
A value the project has not collected is "a coletar", never filled in.

Usage: uv run python docs/superpowers/tools/build-tres-poderes-r2-data.py
Writes data/federal/positions-2026.json and docs/superpowers/previews/assets/tres-poderes-r2-data.js
"""
import csv, hashlib, html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "federal" / "raw-pay"
OUT = ROOT / "data" / "federal" / "positions-2026.json"
JS = ROOT / "docs" / "superpowers" / "previews" / "assets" / "tres-poderes-r2-data.js"
FETCHED = "2026-10-21"
MON = {"JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4, "MAI": 5, "JUN": 6, "JUL": 7, "AGO": 8, "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12}
STATE = {"Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES",
         "Goiás": "GO", "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG", "Pará": "PA", "Paraíba": "PB",
         "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI", "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS",
         "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE", "Tocantins": "TO"}
brl = lambda s: float(s.replace(".", "").replace(",", "."))
import unicodedata
plain = lambda s: unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper().strip()


def page_text(name, enc="utf-8"):
    t = (RAW / name).read_bytes().decode(enc, "ignore")
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def need(text, pattern, label):
    m = re.search(pattern, text)
    if not m:
        raise SystemExit(f"{label}: pattern not found, the page changed")
    return m


sources = {p.name: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "fetched_on": FETCHED} for p in sorted(RAW.iterdir())}
URL = {"camara_mandate": "https://especial.camara.leg.br/posse2027/exercicios-do-mandato/",
       "dl172": "https://www2.camara.leg.br/legin/fed/decleg/2022/decretolegislativo-172-21-dezembro-2022-793529-publicacaooriginal-166604-pl.html",
       "l14520": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/L14520.htm",
       "cf93": "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm",
       "sen_housing": "https://www12.senado.leg.br/transparencia/sen/coapat/auxilio-moradia-e-imoveis-funcionais",
       "sen_housing_api": "https://adm.senado.gov.br/adm-dadosabertos/api/v1/senadores/auxilio-moradia-imoveis-funcionais?formato=json",
       "sen_ceaps": "https://www12.senado.leg.br/transparencia/leg/pdf/CotaExercicioAtivParlamSenadores.pdf",
       "sen_allowances": "https://www12.senado.leg.br/perguntas-frequentes/canais-de-atendimento/senadores/os-senadores-recebem-mais-alguma-verba-alem-do-subsidio"}

# ---------- salaries (read from the law texts, not typed)
dl = page_text("dl172.html", "latin-1").encode("latin-1", "ignore").decode("utf-8", "ignore")
SALARY = brl(need(dl, r"IV - R\$ ([\d.]+,\d{2}) \(quarenta e seis mil trezentos e sessenta e seis reais e dezenove centavos\), a partir de 1º de fevereiro de 2025", "DL 172").group(1))
stf = page_text("l14520.htm", "latin-1")
STF_SALARY = brl(need(stf, r"III - R\$ ([\d.]+,\d{2}) \(quarenta e seis mil trezentos e sessenta e seis reais e dezenove centavos\), a partir", "Lei 14.520").group(1))
SUPERIOR = round(STF_SALARY * 0.95, 2)  # CF art. 93, V: 95% of the STF minister's salary

# ---------- Câmara rules
mandate_page = page_text("camara-mandato.html")
HOUSING_DEP = brl(need(mandate_page, r"O valor do auxílio-moradia é de R\$ ([\d.]+,\d{2})", "Câmara housing").group(1))
HOUSING_DEP_MAX = brl(need(mandate_page, r"o valor total do benefício poderá alcançar R\$ ([\d.]+,\d{2})", "Câmara housing max").group(1))
OFFICE_DEP = brl(need(mandate_page, r"O valor da verba de gabinete é de R\$ ([\d.]+,\d{2})", "Câmara office budget").group(1))
STAFF_PAY = [brl(x) for x in need(mandate_page, r"é R\$ ([\d.]+,\d{2}); e o maior, R\$ ([\d.]+,\d{2})", "secretaries pay").groups()]
ceap_block = mandate_page[mandate_page.index("Valor da cota (R$)"):]
CEAP_DEP = {uf: brl(v) for uf, v in re.findall(r"\b([A-Z]{2}) ([\d.]+,\d{2})", ceap_block[:600])}
if not (len(CEAP_DEP) == 27):
    raise SystemExit(CEAP_DEP)

# ---------- Senado rules
HOUSING_SEN = brl(need(page_text("senado-moradia.html"), r"é de R\$ ([\d.]+,\d{2})", "Senado housing").group(1))
CEAPS = {}
for line in (RAW / "ceaps.txt").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\s*\d+\s+(.+?)\s+R\$ ([\d.]+,\d{2})", line)
    if m: CEAPS[STATE[m.group(1).strip()]] = brl(m.group(2))
if not (len(CEAPS) == 27):
    raise SystemExit(CEAPS)

# ---------- people: the Mesa of each house
mesa_c = json.loads((RAW / "mesa-camara-m.json").read_text())["dados"]
DEP = json.loads((ROOT / "data" / "politicians" / "federal-deputies.json").read_text())
SEN = json.loads((ROOT / "data" / "politicians" / "senators.json").read_text())
person_of = lambda data, pid: next(p for ps in data["by_uf"].values() for p in ps if p["id"] == pid)


def deputy(member):
    pid = member["id"]; t = page_text(f"dep-{pid}.html")
    upd = need(t, r"Informações de recursos atualizadas em (\d{2}/\d{2}/\d{4})", "updated").group(1)
    sal = brl(need(t, r"Salário mensal bruto \? R\$ ([\d.]+,\d{2})", "salary").group(1))
    flat = need(t, r"Imóvel funcional \? (.+?) Auxílio-moradia", "flat").group(1).strip()
    housing = need(t, r"Auxílio-moradia \? (.+?) Viagens em missão oficial", "housing").group(1).strip()
    passport = need(t, r"Passaporte diplomático \? (\S+)", "passport").group(1)

    def block(label, nxt):
        seg = t[t.index(label + " ? Percentual gasto"):]
        seg = seg[:seg.index(nxt)] if nxt in seg else seg[:2000]
        total, pct = need(seg, r"Total \(R\$\) Percentual Gasto ([\d.]+,\d{2}) ([\d.]+)%", label).groups()
        months = {MON[m]: brl(v) for m, v in re.findall(r"\b(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ) ([\d.]+,\d{2})", seg)}
        return {"used_year": brl(total), "used_pct": float(pct), "months": months}
    ceap = block("Cota parlamentar", "Verba de gabinete ?")
    office = block("Verba de gabinete", "Salário mensal bruto")
    p = person_of(DEP, f"camara:{pid}")
    uf = member["siglaUf"]
    # the Mesa endpoint cuts long acronyms ("REPUBLIC"); the party comes from the deputy's own history
    party = next((h["party"] for h in reversed(p.get("party_history") or []) if h.get("end") is None), member["siglaPartido"])
    return {"id": f"camara:{pid}", "name": p["name"], "party": party, "uf": uf, "role": member["titulo"], "photo": p["photo"]["url"],
            "photo_credit": p["photo"]["author"], "updated": upd, "source": f"https://www.camara.leg.br/deputados/{pid}?ano=2026",
            "items": {"salary": {"status": "yes", "value": sal},
                      "housing": {"status": "yes" if housing.startswith("Recebe") else "no", "text": housing},
                      "flat": {"status": "yes" if flat.startswith("Faz uso") else "no", "text": flat},
                      "ceap": {"status": "yes" if ceap["used_year"] > 0 else "no", "used_year": ceap["used_year"], "used_pct": ceap["used_pct"],
                               "months": len(ceap["months"]), "limit_month": CEAP_DEP[uf]},
                      "office": {"status": "yes" if office["used_year"] > 0 else "no", "used_year": office["used_year"], "used_pct": office["used_pct"], "months": len(office["months"])},
                      "passport": {"status": "yes" if passport.startswith("Possui") else "no", "text": passport}}}


# the six titular seats of the Mesa, whose pages were fetched (the API also lists the alternates)
seen_ids = set()
mesa_c = [m for m in mesa_c if (RAW / f"dep-{m['id']}.html").exists() and not (m["id"] in seen_ids or seen_ids.add(m["id"]))]
deputies = [deputy(m) for m in mesa_c]
if not (len(deputies) == 6):
    raise SystemExit(len(deputies))

def senado_mesa():
    out = []
    def walk(o):
        if isinstance(o, dict):
            if "NomeParlamentar" in o and "Cargo" in o: out.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(json.loads((RAW / "mesa-senado.json").read_text())["MesaSenado"])
    seen, res = set(), []
    for o in out:
        if o["Http"] not in seen: seen.add(o["Http"]); res.append(o)
    return res


housing_list = {plain(x["nomeParlamentar"]): x for x in json.loads((RAW / "sen-moradia.json").read_text())["data"] if x.get("nomeParlamentar")}
ceaps_used, ceaps_months = {}, set()
with open(ROOT / "data" / "federal" / "raw" / "senado-ceaps-2026.csv", encoding="latin-1") as f:
    f.readline()
    for r in csv.DictReader(f, delimiter=";"):
        ceaps_used[plain(r["SENADOR"])] = ceaps_used.get(plain(r["SENADOR"]), 0) + brl(r["VALOR_REEMBOLSADO"])
        ceaps_months.add(int(r["MES"]))
norm = lambda s: plain(re.sub(r"^SENADORA? ", "", s.upper()))


def senator(o):
    code = o["Http"]; p = person_of(SEN, f"senado:{code}")
    name = norm(o["NomeParlamentar"]); party, uf = re.match(r"\((.+)-([A-Z]{2})\)", o["Bancada"]).groups()
    h = housing_list.get(name)
    used = ceaps_used.get(name)
    return {"id": f"senado:{code}", "name": p["name"], "party": party, "uf": uf, "role": (o["Cargo"][0] if isinstance(o["Cargo"], list) else o["Cargo"]).capitalize(),
            "photo": p["photo"]["url"], "photo_credit": p["photo"]["author"], "source": URL["sen_housing_api"],
            "items": {"salary": {"status": "yes", "value": SALARY},
                      "housing": {"status": ("yes" if h["auxilioMoradia"] == "S" else "no") if h else "unknown"},
                      "flat": {"status": ("yes" if h["imovelFuncional"] == "S" else "no") if h else "unknown"},
                      "ceaps": {"status": "yes" if used else ("no" if used == 0 else "unknown"), "used_year": round(used or 0, 2), "months": max(ceaps_months),
                                "limit_month": CEAPS[uf]},
                      "office": {"status": "unknown"}}}


senators = [senator(o) for o in senado_mesa()]
U = json.loads((ROOT / "data" / "politicians" / "union.json").read_text())
cur = {o["office"]: o for o in U["offices"] if o.get("end") is None}
union_person = lambda pid: U["people"][pid]
photo_of = lambda p: (p.get("photo") or {}).get("url") if isinstance(p.get("photo"), dict) else None
local_photo = lambda pid: f"assets/photos/union/{pid}.jpg" if (ROOT / "docs" / "superpowers" / "previews" / "assets" / "photos" / "union" / f"{pid}.jpg").exists() else None


def union_holder(office, items):
    o = cur[office]; p = union_person(o["person_id"])
    return {"id": o["person_id"], "name": p["name"], "party": o.get("party_at_start"), "since": o["start"], "photo": local_photo(o["person_id"]) or photo_of(p),
            "photo_credit": "Wikimedia Commons" if photo_of(p) and not local_photo(o["person_id"]) else None, "items": items}


S = json.loads((ROOT / "data" / "federal" / "servants-by-branch.json").read_text())
B, CNJ, CT, H = S["branches"], S["judiciary_cost_per_person_cnj"]["courts"], S["details"]["judiciary_active_by_court"]["courts"], S["details"]["legislative_by_house"]
sal_item = lambda v, law, url: {"key": "salary", "label": "Salário (subsídio)", "value": v, "law": law, "url": url}

positions = [
    {"id": "root", "parent": None, "title": "Os 3 Poderes da União", "kind": "root", "row": 0,
     "note": "Cada cargo abaixo mostra o salário e cada auxílio com o valor oficial. No botão, quem ocupa o cargo em 2026 e o que usa."},
    # ---- heads
    {"id": "presidente", "parent": "root", "title": "Presidente da República", "power": "Executivo", "count": 1, "row": 1, "col": [1, 2],
     "items": [sal_item(SALARY, "Decreto Legislativo 172/2022", URL["dl172"]),
               {"key": "residence", "label": "Residência oficial (Palácio da Alvorada)", "value": None, "note": "sem valor publicado"},
               {"key": "other", "label": "Transporte, segurança e cartão da Presidência", "value": None, "todo": True}],
     "people": [union_holder("Presidente da República", {"salary": {"status": "yes", "value": SALARY}, "residence": {"status": "yes"}, "other": {"status": "unknown"}})]},
    {"id": "presidente-senado", "parent": "root", "title": "Presidente do Senado e do Congresso Nacional", "power": "Legislativo", "count": 1, "row": 1, "col": [3, 4],
     "is_member_of": "senador", "people": [s for s in senators if s["role"].upper() == "PRESIDENTE"]},
    {"id": "presidente-stf", "parent": "root", "title": "Presidente do Supremo Tribunal Federal", "power": "Judiciário", "count": 1, "row": 1, "col": [5, 6],
     "items": [sal_item(STF_SALARY, "Lei 14.520/2023", URL["l14520"]), {"key": "allowances", "label": "Auxílios pagos pelo STF", "value": None, "todo": True}],
     "people": [{"id": "edson-fachin", "name": "Edson Fachin", "since": "2025-09-29", "photo": None, "source": "https://noticias.stf.jus.br/postsnoticias/ministro-edson-fachin-assume-hoje-29-a-presidencia-do-stf/",
                 "items": {"salary": {"status": "yes", "value": STF_SALARY}, "allowances": {"status": "unknown"}}}]},
    # ---- second row
    {"id": "vice", "parent": "presidente", "title": "Vice-Presidente da República", "power": "Executivo", "count": 1, "row": 2, "col": [1, 1],
     "items": [sal_item(SALARY, "Decreto Legislativo 172/2022", URL["dl172"]), {"key": "residence", "label": "Residência oficial (Palácio do Jaburu)", "value": None, "note": "sem valor publicado"}],
     "people": [union_holder("Vice-Presidente da República", {"salary": {"status": "yes", "value": SALARY}, "residence": {"status": "unknown"}})]},
    {"id": "ministros", "parent": "presidente", "title": "Ministros de Estado", "power": "Executivo", "count": None, "row": 2, "col": [2, 2],
     "items": [sal_item(SALARY, "Decreto Legislativo 172/2022", URL["dl172"]), {"key": "housing", "label": "Imóvel funcional ou auxílio-moradia", "value": None, "todo": True},
               {"key": "boards", "label": "Jetons de conselhos de estatais", "value": None, "todo": True}],
     "people": [union_holder("Ministro de Estado da Fazenda", {"salary": {"status": "yes", "value": SALARY}, "housing": {"status": "unknown"}, "boards": {"status": "unknown"}}) | {"role": "Ministro da Fazenda"}]},
    {"id": "senador", "parent": "presidente-senado", "title": "Senadores", "power": "Legislativo", "count": 81, "count_note": "três por estado (CF art. 46)", "row": 2, "col": [3, 3],
     "items": [sal_item(SALARY, "Decreto Legislativo 172/2022", URL["dl172"]),
               {"key": "housing", "label": "Auxílio-moradia", "value": HOUSING_SEN, "note": "só para quem não usa imóvel funcional", "url": URL["sen_housing"]},
               {"key": "flat", "label": "Imóvel funcional (apartamento do Senado)", "value": None, "note": "no lugar do auxílio; sem valor publicado"},
               {"key": "ceaps", "label": "Cota parlamentar (Ceaps)", "value": max(CEAPS.values()), "value_min": min(CEAPS.values()),
                "note": "R$ 15 mil mais cinco passagens à capital do estado; muda por estado", "url": URL["sen_ceaps"]},
               {"key": "office", "label": "Gabinete (servidores comissionados)", "value": None, "todo": True},
               {"key": "start_end", "label": "Ajuda de custo no início e no fim do mandato", "value": SALARY, "note": "um salário em cada ponta; não é mensal", "monthly": False, "url": URL["dl172"]}],
     "people": [s for s in senators if s["role"].upper() != "PRESIDENTE"]},
    {"id": "presidente-camara", "parent": "presidente-senado", "title": "Presidente da Câmara dos Deputados", "power": "Legislativo", "count": 1, "row": 2, "col": [4, 4],
     "is_member_of": "deputado", "people": [d for d in deputies if d["role"] == "Presidente"]},
    {"id": "ministros-stf", "parent": "presidente-stf", "title": "Ministros do STF", "power": "Judiciário", "count": CT["stf"]["magistrates"], "count_note": "com o presidente", "row": 2, "col": [5, 5],
     "items": [sal_item(STF_SALARY, "Lei 14.520/2023", URL["l14520"]), {"key": "allowances", "label": "Auxílios pagos pelo STF", "value": None, "todo": True}],
     "cost_per_person": {"value": CNJ["superior_courts"]["per_magistrate"], "what": "custo médio por mês de cada ministro de tribunal superior, com tudo o que o tribunal paga (CNJ, 2024)"}, "people": []},
    {"id": "tribunais", "parent": "presidente-stf", "title": "Ministros dos tribunais superiores (STJ, TST, TSE, STM)", "power": "Judiciário",
     "count": CT["stj"]["magistrates"] + CT["tst"]["magistrates"], "count_note": "STJ e TST; TSE e STM a coletar", "row": 2, "col": [6, 6],
     "items": [{"key": "salary", "label": "Salário (subsídio)", "value": SUPERIOR, "law": "95% do salário do STF (CF art. 93, V)", "url": URL["cf93"]},
               {"key": "allowances", "label": "Auxílios pagos por cada tribunal", "value": None, "todo": True}],
     "cost_per_person": {"value": CNJ["superior_courts"]["per_magistrate"], "what": "custo médio por mês de cada ministro de tribunal superior (CNJ, 2024)"}, "people": []},
    # ---- third row: careers (groups, one average each)
    {"id": "servidores-civis", "parent": "ministros", "title": "Servidores civis do Executivo", "power": "Executivo", "count": B["executive_civil"]["active"], "row": 3, "col": [1, 1], "group": True,
     "averages": [["na ativa", B["executive_civil"]["average_monthly_brl"]["active"]], ["aposentados", B["executive_civil"]["average_monthly_brl"]["retired"]], ["pensionistas", B["executive_civil"]["average_monthly_brl"]["pensioners"]]],
     "as_of": B["executive_civil"]["as_of"]},
    {"id": "militares", "parent": "ministros", "title": "Militares das Forças Armadas", "power": "Executivo", "count": B["executive_military"]["active"], "row": 3, "col": [2, 2], "group": True,
     "averages": [["oficial de carreira", B["executive_military"]["average_monthly_brl"]["active_career_officer"]], ["praça de carreira", B["executive_military"]["average_monthly_brl"]["active_career_enlisted"]],
                  ["praça temporária", B["executive_military"]["average_monthly_brl"]["active_temporary_enlisted"]]], "as_of": B["executive_military"]["as_of"]},
    {"id": "deputado", "parent": "presidente-camara", "title": "Deputados federais", "power": "Legislativo", "count": 513, "row": 3, "col": [3, 3],
     "items": [sal_item(SALARY, "Decreto Legislativo 172/2022", URL["dl172"]),
               {"key": "housing", "label": "Auxílio-moradia", "value": HOUSING_DEP, "value_max": HOUSING_DEP_MAX, "note": f"até R$ {HOUSING_DEP_MAX:,.2f} com o complemento pela cota; só sem imóvel funcional".replace(",", "X").replace(".", ",").replace("X", "."), "url": URL["camara_mandate"]},
               {"key": "flat", "label": "Imóvel funcional (apartamento da Câmara)", "value": None, "note": "no lugar do auxílio; sem valor publicado"},
               {"key": "ceap", "label": "Cota parlamentar (Ceap)", "value": max(CEAP_DEP.values()), "value_min": min(CEAP_DEP.values()), "note": "reembolso de passagens, escritório, combustível e divulgação; muda por estado", "url": URL["camara_mandate"]},
               {"key": "office", "label": "Verba de gabinete", "value": OFFICE_DEP, "note": f"salários de até 25 secretários parlamentares", "url": URL["camara_mandate"]},
               {"key": "passport", "label": "Passaporte diplomático", "value": None, "note": "sem valor"},
               {"key": "start_end", "label": "Ajuda de custo no início e no fim do mandato", "value": SALARY, "note": "um salário em cada ponta; não é mensal", "monthly": False, "url": URL["dl172"]}],
     "people": [d for d in deputies if d["role"] != "Presidente"]},
    {"id": "servidores-camara", "parent": "presidente-camara", "title": "Quem trabalha na Câmara", "power": "Legislativo", "count": H["chamber"]["active_career_staff"] + H["chamber"]["parliamentary_secretaries"], "row": 3, "col": [4, 4], "group": True,
     "averages": [["servidor de carreira (média do Legislativo)", B["legislative"]["average_monthly_brl"]["active"]], ["secretário parlamentar, menor salário", STAFF_PAY[0]], ["secretário parlamentar, maior salário", STAFF_PAY[1]]],
     "count_detail": f"{H['chamber']['active_career_staff']:,} de carreira e {H['chamber']['parliamentary_secretaries']:,} secretários parlamentares (dez/2025)".replace(",", "."), "as_of": H["chamber"]["as_of"]},
    {"id": "juizes", "parent": "tribunais", "title": "Juízes federais e do trabalho", "power": "Judiciário", "count": CT["federal_justice"]["magistrates"] + CT["labor_justice_regional"]["magistrates"], "row": 3, "col": [5, 5], "group": True,
     "averages": [["custo por juiz federal (CNJ)", CNJ["federal_justice"]["per_magistrate"]], ["custo por juiz do trabalho (CNJ)", CNJ["labor_justice"]["per_magistrate"]]],
     "averages_note": "Custo médio mensal por magistrado em 2024, com tudo o que o tribunal paga; não é o salário.", "as_of": "2024"},
    {"id": "servidores-judiciario", "parent": "tribunais", "title": "Servidores do Judiciário", "power": "Judiciário", "count": B["judiciary"]["active"], "row": 3, "col": [6, 6], "group": True,
     "averages": [["na ativa", B["judiciary"]["average_monthly_brl"]["active"]], ["aposentados", B["judiciary"]["average_monthly_brl"]["retired"]]], "as_of": B["judiciary"]["as_of"]},
]
by = {p["id"]: p for p in positions}
for p in positions:  # the heads of the houses have the items of their members
    if p.get("is_member_of"):
        p["items"] = by[p["is_member_of"]]["items"]

out = {"built_on": FETCHED, "salary_2026": SALARY, "rules": {"ceap_by_uf": CEAP_DEP, "ceaps_by_uf": CEAPS}, "positions": positions, "sources": sources, "urls": URL,
       "periods": {"camara": "2026, até a atualização da Câmara", "senado_ceaps": f"janeiro a {['', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'][max(ceaps_months)]} de 2026"}}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
JS.write_text("window.TP2 = " + json.dumps(out, ensure_ascii=False) + ";\n", encoding="utf-8")
print(OUT.name, "|", len(positions), "positions |", len(deputies), "deputies |", len(senators), "senators | salary", SALARY, "| STF", STF_SALARY, "| superior", SUPERIOR)
for d in deputies[:2] + senators[:2]:
    print(" ", d["name"], d["role"], {k: v.get("status") for k, v in d["items"].items()})
