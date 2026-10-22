"""Builds the data of "Os 3 Poderes", design round 3: the tree of positions (from build-tres-poderes-r2-data.py) plus every
federal parliamentarian in office, with salary and each allowance: whether he or she uses it and how much in 2026.

Inputs (data/federal/raw-pay/, collected on 2026-10-21):
  deputies-in-office.json, deputies-pay-2026.jsonl   Câmara open data and each deputy's own page (fetch-deputies-pay.py)
  senators-in-office.json                             Senado open data, senators in office
  sen-moradia.json                                    Senado open data, housing allowance and official flat, senator by senator
  data/federal/raw/senado-ceaps-2026.csv              Senado, the 2026 quota spending, line by line
  data/federal/positions-2026.json                    the tree of positions and the official values of each item
  data/federal/raw-pay/camara-ceap/housing-complement-2026.json   collect-camara-ceap-2026.py: the housing-allowance
                                                      complement each deputy is paid out of the cota, month by month
  data/federal/senate-2026.json                       collect-senate-2026.py: each senator's office staff cost, the CEAPS
                                                      table in force (Ato do Presidente 8/2025) and what has no official list
  data/federal/executive-2026.json, judiciary-2026.json   collect-executive-2026.py, collect-judiciary-2026.py: President, Vice,
                                                      ministers and the higher courts' ministers, each pay component they publish
  data/federal/presidency-2026.json                   collect-presidency-2026.py: public spending tied to the President's post
                                                      (staff trips, the corporate card of the units that serve him) and to his
                                                      spouse, who holds no office; never personal income
Party of a deputy: the deputy's own history in data/politicians/federal-deputies.json when it has one (the Câmara list cuts
long acronyms), otherwise the Câmara list. Nothing is estimated: what no source says is "unknown".

Usage: .venv/bin/python docs/superpowers/tools/build-tres-poderes-r3-data.py
Writes data/federal/officeholders-2026.json and docs/superpowers/previews/assets/tres-poderes-r3-data.js
"""
import csv, json, re, unicodedata
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "federal" / "raw-pay"
OUT = ROOT / "data" / "federal" / "officeholders-2026.json"
JS = ROOT / "docs" / "superpowers" / "previews" / "assets" / "tres-poderes-r3-data.js"
brl = lambda s: float(s.replace(".", "").replace(",", "."))
plain = lambda s: unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper().strip()
POS = json.loads((ROOT / "data" / "federal" / "positions-2026.json").read_text())
sys.path.insert(0, str(ROOT / "pipelines" / "politicians"))
import judiciary_view  # noqa: E402  (the Judiciary's records, shared with build-tres-poderes-r3-judiciary.py)
OFFICES = judiciary_view.offices(POS["positions"])
SALARY = POS["salary_2026"]
item_value = {p["id"]: {it["key"]: it for it in p.get("items", [])} for p in POS["positions"]}
# Monthly averages use the months both houses have settled: January to July. The Câmara publishes the office budget only up
# to July, and the quota's later months are still arriving (house-wide on 21/10/2026: August at about two thirds of July in
# the Câmara, three quarters in the Senado file of 02/10/2026; September far lower). Later months show, marked as arriving.
AVG_MONTHS = {"camara": 7, "senado": 7}
money = lambda s: brl(re.search(r"R\$ ([\d.]+(?:,\d{2})?)", s).group(1)) if s and "R$" in s else None


def flat_use(s):
    """The Câmara writes "Faz uso desde D" for a current use and "Fez uso de D1 a D2" for each past one, both on one line."""
    if s is None:
        return {"uses": None}
    now = re.search(r"Faz uso desde (\d{2}/\d{2}/\d{4})", s)
    ended_2026 = [b for a, b in re.findall(r"Fez uso de (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})", s) if b.endswith("/2026")]
    return {"uses": bool(now or ended_2026), "now": bool(now), "since": now.group(1) if now else None, "until": ended_2026[-1] if ended_2026 else None}


def monthly(by_month, last, first=None):
    """Average over the complete months the person was in office: from the first month with any record to `last`."""
    months = [int(m) for m in by_month if int(m) <= last]
    if not months:
        return None, 0
    start = first or min(months)
    n = last - start + 1
    if n <= 0:
        return None, 0
    return round(sum(v for m, v in by_month.items() if start <= int(m) <= last) / n, 2), n


def match(name, pool, uf=None):
    """The record for a name in a pool keyed by plain names: exact, else the one name that starts with the other."""
    k = plain(name)
    if k in pool:
        return pool[k]
    hits = [v for p, v in pool.items() if (p.startswith(k + " ") or k.startswith(p + " ")) and (uf is None or v.get("_uf") in (None, uf))]
    return hits[0] if len(hits) == 1 else None

# ---------- deputies
hist = {p["id"]: p for ps in json.loads((ROOT / "data" / "politicians" / "federal-deputies.json").read_text())["by_uf"].values() for p in ps}
current_party = lambda pid: next((h["party"] for h in reversed(hist[pid].get("party_history") or []) if h.get("end") is None), None) if pid in hist else None
in_office = json.loads((RAW / "deputies-in-office.json").read_text())
complement = json.loads((RAW / "camara-ceap" / "housing-complement-2026.json").read_text())["by_deputy"]
rows = [json.loads(l) for l in (RAW / "deputies-pay-2026.jsonl").read_text().splitlines()]
assert len({r["id"] for r in rows}) == len(rows) == in_office["count"], (len(rows), in_office["count"])
deputies = []
for r in rows:
    yes = lambda s, word: None if s is None else s.startswith(word)
    housing, passport = yes(r["housing"], "Recebe"), yes(r["passport"], "Possui")
    pid = f"camara:{r['id']}"
    firsts = [int(m) for part in ("ceap", "office") if r[part] for m in r[part]["by_month"]]
    first = min(firsts) if firsts else None
    c_avg, n = monthly(r["ceap"]["by_month"], AVG_MONTHS["camara"], first) if r["ceap"] else (None, 0)
    o_avg, _ = monthly(r["office"]["by_month"], AVG_MONTHS["camara"], first) if r["office"] else (None, 0)
    hc = complement.get(str(r["id"]))
    hc_avg, _ = monthly(hc, AVG_MONTHS["camara"], first) if hc else (None, 0)
    deputies.append({
        "id": pid, "house": "camara", "name": r["name"], "party": current_party(pid) or r["party"], "uf": r["uf"],
        "photo": r["photo"], "page": f"https://www.camara.leg.br/deputados/{r['id']}?ano=2026", "updated": r["updated"],
        "salary": r["salary_gross"],
        "housing": {"uses": housing, "received": money(r["housing"])}, "flat": flat_use(r["flat"]),
        "housing_complement": {"by_month": hc, "year_total": round(sum(hc.values()), 2), "avg": hc_avg} if hc else None,
        "passport": {"uses": passport}, "missions": int(r["missions"]) if r["missions"] else None, "avg_months": n,
        "ceap": r["ceap"] and {"used": r["ceap"]["used_year"], "pct": r["ceap"]["used_pct"], "by_month": r["ceap"]["by_month"],
                                "avg": c_avg, "limit_month": POS["rules"]["ceap_by_uf"][r["uf"]]},
        "office": r["office"] and {"used": r["office"]["used_year"], "pct": r["office"]["used_pct"], "by_month": r["office"]["by_month"], "avg": o_avg}})

# ---------- senators
SEN = json.loads((ROOT / "data" / "federal" / "senate-2026.json").read_text())
sen_extra = {x["id"]: x for x in SEN["people"]}
CEAPS = SEN["ceaps_rules"]["monthly_by_uf"]
for pos in POS["positions"]:
    if pos["id"] not in ("senador", "presidente-senado"):
        continue
    for it in pos["items"]:
        if it["key"] == "ceaps":
            it.update(value=max(CEAPS.values()), value_min=min(CEAPS.values()), law="Ato do Presidente do Senado 8/2025", source=SEN["ceaps_rules"]["act_url"],
                      note="muda por estado; o que sobra num mês passa para os seguintes, dentro do ano")
        if it["key"] == "office":
            it.pop("todo", None)
            it.update(value=None, note="o Senado não publica um valor em reais; a ficha de cada senador soma os salários da equipe")
    pos["items"].insert(next(i for i, it in enumerate(pos["items"]) if it["key"] == "office"),
                        {"key": "flights", "label": "Passagens aéreas: 4 idas e voltas ao DF por mês", "value": None, "note": "fora da cota; Ato da Comissão Diretora 2/2023"})
sen = json.loads((RAW / "senators-in-office.json").read_text())["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]
housing_list = {plain(x["nomeParlamentar"]): dict(x, _uf=x.get("estadoEleito")) for x in json.loads((RAW / "sen-moradia.json").read_text())["data"] if x.get("nomeParlamentar")}
ceaps, ceaps_by_month = {}, {}
with open(ROOT / "data" / "federal" / "raw" / "senado-ceaps-2026.csv", encoding="latin-1") as f:
    ceaps_updated = re.search(r"(\d{2}/\d{2}/\d{4})", f.readline()).group(1)
    for r in csv.DictReader(f, delimiter=";"):
        k, m, v = plain(r["SENADOR"]), int(r["MES"]), brl(r["VALOR_REEMBOLSADO"])
        ceaps[k] = ceaps.get(k, 0) + v
        ceaps_by_month.setdefault(k, {}); ceaps_by_month[k][m] = ceaps_by_month[k].get(m, 0) + v
last_month = max(m for d in ceaps_by_month.values() for m in d)
senators, unmatched = [], []
for s in sen:
    i = s["IdentificacaoParlamentar"]
    h = match(i["NomeParlamentar"], housing_list, i["UfParlamentar"])
    k = match(i["NomeParlamentar"], {n: {"_key": n} for n in ceaps})
    k = k and k["_key"]
    if h is None: unmatched.append(("housing", i["NomeParlamentar"]))
    if k is None: unmatched.append(("quota", i["NomeParlamentar"]))
    c_avg, n = monthly(ceaps_by_month[k], AVG_MONTHS["senado"]) if k else (None, 0)
    x = sen_extra[f"senado:{i['CodigoParlamentar']}"]; o = x["office"]
    office = ({"used": o["year_total"], "avg": o["monthly"], "pct": None, "by_month": o["by_month"], "months_label": o["months"], "staff": o["staff_count"], "kind": "staff"}
              if o["monthly"] is not None else {"used": None, "avg": None, "none_reason": "nenhum mês inteiro de exercício nas folhas publicadas de 2026", "staff": o["staff_count"], "kind": "staff"})
    limit = CEAPS[i["UfParlamentar"]]
    senators.append({
        "id": f"senado:{i['CodigoParlamentar']}", "house": "senado", "name": i["NomeParlamentar"], "party": i["SiglaPartidoParlamentar"], "uf": i["UfParlamentar"],
        "photo": i["UrlFotoParlamentar"].replace("http://", "https://"), "page": (i.get("UrlPaginaParlamentar") or f"https://www25.senado.leg.br/web/senadores/senador/-/perfil/{i['CodigoParlamentar']}").replace("http://", "https://"),
        "updated": ceaps_updated, "salary": SALARY, "salary_is_position": True,
        "housing": {"uses": None if h is None else h["auxilioMoradia"] == "S"}, "flat": {"uses": None if h is None else h["imovelFuncional"] == "S"},
        "passport": {"uses": None, "unpublished": True}, "missions": None, "avg_months": n, "exercise_since": x["exercise_since"],
        # the year's limit is 12 times the state's monthly value: unspent balance moves to later months of the same year
        "ceap": {"used": round(ceaps[k], 2), "pct": round(ceaps[k] / (12 * limit) * 100, 2), "pct_basis": "year_x12", "by_month": {m: round(v, 2) for m, v in sorted(ceaps_by_month[k].items())},
                 "avg": c_avg, "limit_month": limit} if k else {"used": 0.0, "pct": 0.0, "by_month": {}, "avg": None, "limit_month": limit, "none_registered": True},
        "office": office})

# ---------- Executive and Judiciary: each published pay component as an item; "own" says whether it goes to the person
# (per diems pay expenses of the office, not the person). INFO items are shown but never summed: net pay is the gross
# minus taxes, the corporate card is spending of the presidency's units (ABIN and EBC among them), the property fee is a
# discount whose absence proves nothing, and "mandate" only says who the minister is on leave from.
NOT_OWN = {"per_diem", "tse_per_diem"}
INFO = {"net_pay", "cpgf", "functional_property_fee", "mandate"}
EXEC_RAW = ROOT / "data" / "federal" / "raw-pay" / "executive"
# A senator on leave who is a minister is paid by the Senado (CF art. 56, § 3): the Senado payroll row, saved as evidence.
wd = json.loads((EXEC_RAW / "senado-payroll-wellington-dias-2026-08.json").read_text())
photos = {x["name"]: x for x in json.loads((EXEC_RAW / "minister-photos.json").read_text())["photos"]} if (EXEC_RAW / "minister-photos.json").exists() else {}


def normalize(x):
    """Every monthly figure means the same thing: the 2026 total divided by the months the person held the post in the
    months published (the salary's months). A one-off such as the 13th salary is spread over those months, never
    shown as if it were paid every month."""
    sal = next((it for it in x["items"] if it["key"] == "salary"), None)
    n_post = len(sal["by_month"]) if sal and sal.get("by_month") else None
    for it in x["items"]:
        it["info"] = it["key"] in INFO
        bm = it.get("by_month")
        if bm:
            assert abs(sum(bm.values()) - (it.get("year_total") or 0)) < 0.05, (x["name"], it["key"])
        n = n_post or (len(bm) if bm else None)
        if it.get("year_total") is not None and n:
            it["monthly"] = round(it["year_total"] / n, 2)
            it["months"] = sal["months"] if n_post and sal.get("months") else it.get("months")
    if x["name"] == "José Wellington Barroso de Araujo Dias" and sal and sal["uses"] is None:
        sal.update(uses=True, monthly=float(wd["row"]["remuneracao_basica"].replace(".", "").replace(",", ".")), year_total=None, months="ago 2026",
                   note="pago pelo Senado: senador licenciado que optou pela remuneração do mandato (CF art. 56, § 3º); folha do Senado de agosto de 2026",
                   source=wd["source"])
    if not x.get("photo") and x["name"] in photos and photos[x["name"]]["photo"]:
        x["photo"], x["photo_credit"] = photos[x["name"]]["photo"], photos[x["name"]]["credit"]
    return x


# ---------- spending tied to the President's post and to the spouse: SUMMED items add up to the total shown; the others are
# listed with the reason they are not added (a weaker link stated in the trip's purpose, or confidential purpose)
PRES = json.loads((ROOT / "data" / "federal" / "presidency-2026.json").read_text()) if (ROOT / "data" / "federal" / "presidency-2026.json").exists() else None
SUMMED = {"trips_entourage", "cpgf_president_units", "trips_support"}
PART_OF = {k: "cpgf_president_units" for k in ("cpgf_secretaria_de_administracao_pr", "cpgf_secretaria_de_administracao_peculiaridades", "cpgf_gabinete_de_seguranca_institucional_pr")}


def costs(items):
    # the collector's notes name its own field for the units kept apart; readers see the words, not the key
    return [dict(it, summed=it["key"] in SUMMED, part_of=PART_OF.get(it["key"]), note=(it.get("note") or "").replace("ficam em other_units", "ficam numa lista à parte"))
            for it in items]


others, other_positions = [], {}
for house, name in (("executivo", "executive-2026.json"), ("judiciario", "judiciary-2026.json")):
    f = ROOT / "data" / "federal" / name
    if not f.exists():
        continue
    src = json.loads(f.read_text())
    for pos in src.get("positions", []):
        other_positions[pos["id"]] = pos
    for x in src["people"]:
        if house == "judiciario":
            others.append(judiciary_view.record(x, OFFICES))
            continue
        if house == "executivo":
            x = normalize(x)
        if PRES and x.get("position") == "presidente":
            # the corporate card of the units tied to him comes from presidency-2026.json, which leaves ABIN, EBC and the
            # Imprensa Nacional fund out; the executive file's card total included them
            x["items"] = [it for it in x["items"] if it["key"] != "cpgf"]
        items = [dict(it, own=it["key"] not in NOT_OWN) for it in x["items"]]
        others.append({"id": x["id"], "house": house, "court": x.get("court"), "ministry": x.get("ministry"), "position": x["position"],
                       "name": x["name"], "role": x.get("role"), "tse_role": x.get("tse_role"), "party": x.get("party"), "uf": None,
                       "since": x.get("since"), "photo": x.get("photo"), "photo_credit": x.get("photo_credit"), "page": x.get("page"),
                       "data_as_of": x.get("data_as_of"), "note": x.get("note"), "items": items})
        if PRES and x.get("position") == "presidente":
            others[-1].update(office_costs=costs(PRES["president"]["items"]), trips=PRES["president"]["trips"], other_units=PRES["president"]["other_units"],
                              costs_months=PRES["months_published"], unpublished=[n for n in PRES["not_found"] if "apoiam a cônjuge" not in n["what"].lower()])
if PRES:
    s = PRES["spouse"]
    others.append({"id": "exec:rosangela-lula-da-silva", "house": "executivo", "court": None, "ministry": None, "position": "conjuge",
                   "name": s["name"], "known_as": s["known_as"], "role": "Cônjuge do Presidente da República, sem cargo público", "tse_role": None, "party": None, "uf": None,
                   "since": None, "photo": s["photo"], "photo_credit": s["photo_credit"], "page": None, "data_as_of": None, "note": None,
                   "items": [{"key": "salary", "label": "Salário", "uses": False, "monthly": None, "year_total": None, "info": False, "own": True,
                              "note": "não ocupa cargo público e não recebe salário da União", "source": None}],
                   "office_costs": costs(s["items"]), "trips": s["trips"], "structure": s["structure"], "costs_months": PRES["months_published"],
                   "unpublished": [n for n in PRES["not_found"] if "cônjuge" in n["what"].lower()]})

people = sorted(deputies + senators + others, key=lambda p: plain(p["name"]))

# ---------- the "Cargos" view of the Executive and the courts: each position's official values and rules, as collected
FROM = {"presidente": "presidente", "vice": "vice", "ministros": "ministros", "presidente-stf": "ministros-stf", "ministros-stf": "ministros-stf",
        "tribunais": "ministros-stj"}
for pos in POS["positions"]:
    src = other_positions.get(FROM.get(pos["id"]))
    if src:
        pos["items"] = [{"key": it["key"], "label": it["label"], "value": it.get("value_monthly"), "cap": "teto" in it["label"].lower(),
                         "note": (it.get("rule") or it.get("note") or "").split(". ")[0], "source": it.get("source")} for it in src["items"]]

# ---------- the tree's head counts come from who was collected, with the seats each court has by law
by_court = defaultdict(list)
for x in others:
    by_court[x["court"] or x["position"]].append(x)
if by_court:
    SEATS = {"STF": 11, "STJ": 33, "TST": 27, "STM": 15}  # CF arts. 101, 104, 111-A and 123
    vac = json.loads((ROOT / "data" / "federal" / "judiciary-2026.json").read_text()).get("vacancies", []) if (ROOT / "data" / "federal" / "judiciary-2026.json").exists() else []
    for pos in POS["positions"]:
        if pos["id"] == "ministros-stf" and by_court.get("STF"):
            pos["count"] = SEATS["STF"]
            v = next((v for v in vac if v.get("court") == "STF"), None)
            pos["count_note"] = f"{len(by_court['STF'])} em exercício" + (f", 1 cadeira vaga" + (f" desde {'/'.join(reversed(v['since'].split('-')))}" if v and v.get("since") else "") if len(by_court["STF"]) < SEATS["STF"] else "")
        if pos["id"] == "tribunais":
            got = {c: len(by_court.get(c, [])) for c in ("STJ", "TST", "STM")}
            pos["count"] = sum(SEATS[c] for c in got)
            pos["count_note"] = "; ".join(f"{c} {n} de {SEATS[c]}" for c, n in got.items()) + (f"; TSE: {len(by_court.get('TSE', []))} juristas" if by_court.get("TSE") else "")
        if pos["id"] == "ministros" and by_court.get("ministros"):
            pos["count"] = len(by_court["ministros"])

# ---------- bills: counts per role and outcome, read from the per-person files of build-tres-poderes-bills.py
# (a bill that became law counts as "law", not as "approved"; the sheet loads the full list itself)
SHARDS = ROOT / "docs" / "superpowers" / "previews" / "assets" / "tres-poderes-bills"
bills_missing = []
for p in people:
    if p["house"] not in ("camara", "senado"):
        continue
    f = SHARDS / f"{p['id'].replace(':', '-')}.js"
    if not f.exists():
        bills_missing.append(p["id"]); continue
    bills = json.loads(f.read_text(encoding="utf-8").split("] = ", 1)[1].rstrip().rstrip(";"))
    p["bills"] = {role: {"counts": dict(Counter("law" if b["law"] else b["o"] for b in bills if b["r"] == r))} for role, r in (("main", "m"), ("co", "c"))}
# ---------- the tree's sample holders (written in round 2, before the directory existed): the page reads each one from the
# directory when it has a record, so their own statuses are dropped instead of contradicting it (Alcolumbre's office cost,
# for example, is in the directory and was "unknown" in the sample)
ids = {p["id"] for p in people}
HAS_RECORD = {"presidente": lambda x: x["position"] == "presidente", "vice": lambda x: x["position"] == "vice",
              "presidente-stf": lambda x: x.get("court") == "STF" and x.get("role") == "Presidente",
              "ministros": lambda x: x["position"] == "ministros"}
for pos in POS["positions"]:
    for h in pos.get("people", []):
        if h.get("id") in ids or (pos["id"] in HAS_RECORD and any(HAS_RECORD[pos["id"]](x) for x in others)):
            h.pop("items", None)
left = [(pos["id"], h.get("name")) for pos in POS["positions"] for h in pos.get("people", [])
        for v in (h.get("items") or {}).values() if isinstance(v, dict) and v.get("status") == "unknown"]
assert not left, f"tree holders still marked unknown: {left}"

out = {"built_on": "2026-10-21", "salary": SALARY, "positions": POS["positions"], "urls": POS["urls"],
       "rules": {"housing_camara": item_value["deputado"]["housing"]["value"], "housing_senado": item_value["senador"]["housing"]["value"],
                 "office_camara": item_value["deputado"]["office"]["value"], "ceap_by_uf": POS["rules"]["ceap_by_uf"], "ceaps_by_uf": CEAPS,
                 "ceaps_act": SEN["ceaps_rules"]["act_url"]},
       "other_positions": other_positions,
       "senado_ceaps_months": last_month, "avg_months": AVG_MONTHS, "people": people,
       "coverage": {"deputies": len(deputies), "senators": len(senators), "others": len(others), "senators_unmatched": unmatched, "bills_missing": len(bills_missing)}}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
JS.write_text("window.TP3 = " + json.dumps(out, ensure_ascii=False) + ";\n", encoding="utf-8")
print(OUT.name, "|", len(deputies), "deputies |", len(senators), "senators | senators without housing or quota match:", unmatched, "| without bills file:", len(bills_missing))
