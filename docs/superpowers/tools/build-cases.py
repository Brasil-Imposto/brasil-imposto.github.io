"""Builds previews/assets/cases.json (the case modals) from the research data files.

Numbers are computed from data/*.json; the only prose written here is short neutral summaries of
official findings, each paired with the official status and link. Rules for this file:
roles and official findings only, no name next to a finding unless the official text names them,
never "desvio" or "superfaturamento" unless an official body used the word.
Run: python3 docs/superpowers/tools/build-cases.py
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data"
TARGET = ROOT / "docs" / "superpowers" / "previews" / "assets" / "cases.json"


def brl(v):
    if abs(v) >= 1e9:
        return f"R$ {v / 1e9:,.1f} bi".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs(v) >= 1e6:
        return f"R$ {v / 1e6:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {v:,.0f}".replace(",", ".")


COUNTRY_PT = {"Brazil": "Brasil", "Hungary": "Hungria", "Canada": "Canadá", "Vietnam": "Vietnã"}


def cnpj(v):
    d = "".join(ch for ch in (v or "") if ch.isdigit())
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}" if len(d) == 14 else v


def num(v):
    return f"{v:,.0f}".replace(",", ".")


def brl_exact(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def governor_on(date, governors):
    """Governor in office on an ISO date; dates whose start is unconfirmed fall back to the listed term."""
    for g in governors:
        start, end = g["start"][:10], g["end"][:10]
        if len(start) == 10 and len(end) == 10 and start <= date <= end:
            return g["name"]
    return None


MEDIA = ROOT / "docs" / "superpowers" / "previews" / "assets" / "cases" / "hercilio-luz"
# Party at the time of each act, from the governor's Alesc biography (mandate table and text).
GOV_EXTRA = {
    "Luiz Henrique da Silveira": {"party": "PMDB", "party_name": "Partido do Movimento Democrático Brasileiro", "party_now": "hoje MDB",
                                  "photo": "gov-luiz-henrique.jpg", "wiki": "https://pt.wikipedia.org/wiki/Luiz_Henrique_da_Silveira"},
    "Raimundo Colombo": {"party": "PSD", "party_name": "Partido Social Democrático", "party_now": "mandato 2015 a 2018; no de 2011 a 2014 era do DEM",
                         "photo": "gov-raimundo-colombo.jpg", "wiki": "https://pt.wikipedia.org/wiki/Raimundo_Colombo"},
    "Carlos Moisés da Silva": {"party": "PSL", "party_name": "Partido Social Liberal", "party_now": "em 2022 o PSL se juntou ao DEM e formou o União Brasil",
                               "photo": "gov-carlos-moises.jpg", "wiki": "https://pt.wikipedia.org/wiki/Carlos_Mois%C3%A9s_da_Silva"},
}
# Official websites linked only where the name matches without ambiguity (none of the home pages shows a CNPJ).
COMPANY_SITE = {"24447770000145": "https://www.teixeiraduarteconstrucao.com.br", "33146648000391": "https://www.concremat.com.br",
                "17159856000107": "https://www.empa.com.br"}
# Plain-language scope of each compared work, from data/bridge-comparables.json.
SCOPE_SHORT = {
    "Ponte Hercílio Luz": "troca das barras de olhal, reforço das fundações e estrutura provisória",
    "Széchenyi Lánchíd": "tabuleiro novo e reparo das correntes, sem trocar as barras",
    "Lions' Gate Bridge": "troca do tabuleiro e da estrutura suspensa",
    "Cầu Thuận Phước": "ponte nova, com viadutos de concreto",
    "Ponte Pênsil Alves de Lima": "reparo de madeira do tabuleiro e do guarda-corpo",
}


def bridge_case():
    hl = json.loads((DATA / "hercilio-luz.json").read_text(encoding="utf-8"))
    cmp = json.loads((DATA / "bridge-comparables.json").read_text(encoding="utf-8"))
    me = cmp["hercilio_luz"]
    restoration = [c for c in hl["contracts"] if c["group"] == "restoration_2006_2019"]
    total = sum(c["value_current_brl"] for c in restoration)
    if not (abs(total - hl["contracts_totals_computed"]["value_current_brl"]) < 0.01):
        raise SystemExit("contract total drifted")

    by_company = defaultdict(lambda: {"value": 0.0, "contracts": [], "status": set(), "cnpj": None})
    for c in restoration:
        k = c["contractor_name_in_record"].strip()
        by_company[k]["value"] += c["value_current_brl"]
        by_company[k]["contracts"].append(c["number"])
        by_company[k]["status"].add(c["status_in_record"])
        by_company[k]["cnpj"] = c.get("contractor_cnpj")
    companies = sorted(by_company.items(), key=lambda kv: -kv[1]["value"])

    main = max(restoration, key=lambda c: c["value_current_brl"])
    td = next(x for x in hl["payments"]["companies"] if x["cnpj"] == main["contractor_cnpj"])
    paid_years = [y for y in td["by_year"] if 2016 <= y["year"] <= 2020]
    paid = sum(y["all_units"].get("vlbruto", 0) for y in paid_years)

    governors = hl["governors"]
    key_dates = [(c["number"], c["signed_on"]) for c in sorted(restoration, key=lambda c: -c["value_current_brl"])[:3]]
    officials = []
    for o in hl["officials"]:
        if o.get("signed"):
            officials.append({"name": o["name"], "role": "Presidente do DEINFRA, assinou pelo Estado", "period": ", ".join(o["signed"])})
    signed_under = defaultdict(list)
    for number, signed in sorted(key_dates, key=lambda x: x[1]):
        g = governor_on(signed, governors)
        if g:
            signed_under[g].append((number, signed[:4]))
    for g, contracts in signed_under.items():
        officials.append({"name": g, "role": "Governador na data da assinatura do " + " e do ".join(n for n, _ in contracts),
                          "period": " e ".join(sorted({y for _, y in contracts}))})
    reopened = governor_on("2019-12-30", governors)
    if reopened:
        officials.append({"name": reopened, "role": "Governador na reabertura da ponte", "period": "2019"})

    # Short neutral summaries of each official finding; the official status and link travel with it.
    summaries = {
        "ELC 07/00582703": "Mandou suspender a licitação de forma cautelar (2007) e, em 2008, considerou o edital de acordo com a lei.",
        "RLA 12/00285490": "Aplicou multas a responsáveis do DEINFRA por permitir que o contrato PJ-264/2008 tivesse acréscimo de 50,29% e supressão de 44,78% do valor por aditivos, acima do limite da Lei 8.666/93.",
        "REC 16/00030243": "Julgou os recursos contra essas multas: duas decisões mantidas na íntegra, três com multas canceladas no todo ou em parte.",
        "REP 14/00346689": "Multa de R$ 1.136,52 ao então presidente do DEINFRA por não fiscalizar a apresentação do seguro de riscos de engenharia pelo Consórcio Florianópolis Monumento.",
        "CPI da Ponte Hercílio Luz": "O relatório final trocou a palavra 'indiciamento' por encaminhamento ao MPTC, ao MP e ao TCE 'para apurar possíveis ilicitudes'. Não é acusação nem condenação.",
        "@REP 15/00524643": "Reconheceu a prescrição (o prazo para punir e cobrar ressarcimento venceu) para 11 contratos, sem julgar o mérito, e mandou abrir processos novos sobre o PJ-056/2016 e o CT-006/2019.",
        "Ação civil pública": "Ação de improbidade administrativa pedindo o ressarcimento de R$ 233.675.518,92 aos cofres públicos.",
        "Inquérito civil": "Instaurou inquérito civil para apurar o andamento das obras de recuperação.",
    }
    findings = []
    for f in sorted(hl["findings"], key=lambda f: f["date"][:10]):
        text = next((v for k, v in summaries.items() if f["process"].startswith(k)), None)
        if not (text):
            raise SystemExit(f"no summary for {f['process']}")
        findings.append({"body": f"{f['body'].split(' (')[0]} ({f['date'][:4]})", "text": text, "status": f["status"].split(";")[0], "url": f["url"]})

    items = [{"label": me["name"].replace(" (restauração)", ""), "detail": "restauração, 13 contratos, 2006 a 2019",
              "value": me["cost_per_m2_brl_2024_fx"], "self": True}]
    for p in cmp["comparables"]:
        items.append({"label": p["name"].split(" (")[0], "detail": COUNTRY_PT.get(p["country"], p["country"]) + ", " + p["years"].split(" (")[0],
                      "value": p["cost_per_m2_brl_2024_fx"]})
    items.sort(key=lambda i: -i["value"])
    for i in items:
        i["display"] = f"R$ {num(i['value'])} por m²"
    closest = next(p for p in cmp["comparables"] if "Lánchíd" in p["name"])
    diff = closest["cost_per_m2_brl_2024_fx"] - me["cost_per_m2_brl_2024_fx"]
    gap_positive = diff < 0
    gap_text = (f"A obra mais parecida, em Budapeste (mesma técnica de correntes de barras de olhal), custou "
                f"R$ {num(abs(diff))} a mais por m² do que a Hercílio Luz. As obras que custaram menos fizeram "
                "menos: nenhuma trocou as barras de olhal nem reforçou fundações, e a do Vietnã é uma ponte nova com viadutos de concreto."
                if not gap_positive else
                f"A Hercílio Luz custou R$ {num(abs(diff))} a mais por m² do que a obra mais parecida.")

    credits = json.loads((MEDIA / "credits.json").read_text(encoding="utf-8"))
    media_path = "assets/cases/hercilio-luz/"
    def credit(f):
        c = credits[f]
        return {"credit": f"{c['author']}, {c['license']}", "link": c["commons"]}
    media = [
        {"src": media_path + "bridge-1940.jpg", "caption": "1940: a ponte em uso, 14 anos depois de inaugurada", **credit("bridge-1940.jpg")},
        {"src": media_path + "bridge-restoration.jpg", "caption": "2018: a restauração, com a estrutura provisória", **credit("bridge-restoration.jpg")},
        {"src": media_path + "bridge-today.jpg", "caption": "2025: reaberta desde 30/12/2019", **credit("bridge-today.jpg")},
    ]
    gov_source = {g["name"]: g["source"] for g in governors}
    people = []
    for o in hl["officials"]:
        if o.get("signed"):
            people.append({"name": o["name"], "role": "Presidente do DEINFRA", "detail": "assinou pelo Estado: " + ", ".join(o["signed"]),
                           "photo": None, "party": None,
                           "links": [{"label": "Assinatura no Diário Oficial", "url": s["url"]} for s in o["source"][:1]]})
    for g, contracts in signed_under.items():
        x = GOV_EXTRA[g]
        people.append({"name": g, "role": "Governador", "detail": "no dia da assinatura do " + " e do ".join(n for n, _ in contracts),
                       "photo": media_path + x["photo"], "photo_credit": credit(x["photo"])["credit"], "photo_link": credit(x["photo"])["link"],
                       "party": x["party"], "party_name": x["party_name"], "party_note": x["party_now"],
                       "links": [{"label": "Biografia na Alesc", "url": gov_source[g]}, {"label": "Wikipédia", "url": x["wiki"]}]})
    if reopened:
        x = GOV_EXTRA[reopened]
        people.append({"name": reopened, "role": "Governador", "detail": "na reabertura da ponte, em 30/12/2019",
                       "photo": media_path + x["photo"], "photo_credit": credit(x["photo"])["credit"], "photo_link": credit(x["photo"])["link"],
                       "party": x["party"], "party_name": x["party_name"], "party_note": x["party_now"],
                       "links": [{"label": "Biografia na Alesc", "url": gov_source[reopened]}, {"label": "Wikipédia", "url": x["wiki"]}]})
    registry = {c["cnpj"]: c for c in hl["companies"]}
    company_cards = []
    for name, v in companies:
        digits = "".join(ch for ch in (v["cnpj"] or "") if ch.isdigit())
        reg = registry.get(digits, {})
        links = []
        if COMPANY_SITE.get(digits):
            links.append({"label": "Site oficial", "url": COMPANY_SITE[digits]})
        links.append({"label": "Portal da Transparência", "url": f"https://portaldatransparencia.gov.br/pessoa-juridica/{digits}"})
        links.append({"label": "Contratos (dados de SC)", "url": restoration[0]["source"]["url"]})
        company_cards.append({"name": name, "cnpj": cnpj(v["cnpj"]), "trade_name": reg.get("trade_name"), "city": reg.get("city"),
                              "contracts": v["contracts"], "value": v["value"], "status": ", ".join(sorted(v["status"])), "links": links})
    bridges = [me, *cmp["comparables"]]
    details = []
    for p in bridges:
        key = p["name"].split(" (")[0].split(",")[0]
        details.append({"label": key, "country": COUNTRY_PT.get(p["country"], p["country"]), "years": p["years"].split(" (")[0].replace("-", " a "),
                        "length_m": p["length_m"], "width_m": p["deck_width_m"], "area_m2": p["deck_area_m2"],
                        "total_brl_2024": p["cost_brl_2024_fx"], "per_m2": p["cost_per_m2_brl_2024_fx"], "scope": SCOPE_SHORT.get(key, ""),
                        "self": p is me, "source": p["sources"][0]["url"]})
    details.sort(key=lambda d: -d["per_m2"])

    return {
        "id": "ponte-hercilio-luz", "uf": "SC", "municipality": "4205407", "function": "Transporte", "kind": "obra",
        "media": media, "people": people, "company_cards": company_cards, "compare_details": details,
        "card": {"image": media_path + "bridge-today.jpg", "stats": [["Valor dos contratos", brl(total)], ["Contratos", f"{len(restoration)}"],
                 ["Período", "2006 a 2019"], ["Custo por m²", f"R$ {num(me['cost_per_m2_brl_2024_fx'])}"]]},
        "title": "Ponte Hercílio Luz", "short": "Ponte Hercílio Luz",
        "teaser": f"Restauração: {len(restoration)} contratos de 2006 a 2019, {brl(json.loads((DATA / 'hercilio-luz-paid-by-contract.json').read_text(encoding='utf-8'))['total_paid_2006_2020_brl'])} pagos.",
        "subtitle": "Ponte pênsil de 1926, interditada em 1982 e reaberta em 30/12/2019. Obra do Governo do Estado (DEINFRA).",
        "facts": [
            {"label": "Contratos de restauração", "value": f"{len(restoration)}, de 2006 a 2019", "note": "registro de contratos do Estado (SIGEF)"},
            {"label": "Valor atual dos contratos", "value": brl(total), "note": "valor de contrato, nominal, com aditivos"},
            {"label": "Maior contrato", "value": brl(main["value_current_brl"]), "note": f"{main['contractor_name_in_record'].split(' - ')[0]}, {main['number']}"},
            {"label": "Pago à mesma empresa", "value": brl(paid), "note": "2016 a 2020, bruto; inclui um contrato de outras pontes"},
            {"label": "Custo por m² (2024)", "value": f"R$ {num(me['cost_per_m2_brl_2024_fx'])}", "note": "contratos corrigidos pelo IPCA"},
        ],
        "companies": [{"name": name, "cnpj": cnpj(v["cnpj"]), "contract": ", ".join(v["contracts"]),
                       "value": v["value"], "status": ", ".join(sorted(v["status"]))} for name, v in companies[:7]],
        "officials": officials,
        "findings": findings,
        "compare": {
            "title": "Custo por m² de tabuleiro, em reais de 2024",
            "subtitle": "Valores convertidos pelo câmbio do ano do gasto e corrigidos pelo IPCA até dezembro de 2024. O método por paridade de poder de compra dá a mesma ordem.",
            "items": items,
            "gap": {"positive": gap_positive, "text": gap_text},
            "reading": ("Os valores da Hercílio Luz são de contrato, não de pagamento. A etapa de 2006 (cerca de R$ 21 mi nominais) não está "
                        f"nos dados abertos; o número real fica entre R$ {num(me['lower_bound_cost_per_m2_brl_2024'])}"
                        f" e R$ {num(me['cost_per_m2_brl_2024_fx'])} por m², mais essa etapa. "
                        "O custo de Budapeste é o orçamento aprovado. O que esta comparação não mede: as décadas com a ponte fechada."),
            "sources": [{"label": p["name"].split(" (")[0].split(",")[0], "url": p["sources"][0]["url"]} for p in [me, *cmp["comparables"]]],
        },
        "sources": [
            {"label": "Contratos: dados abertos de SC (SIGEF)", "url": restoration[0]["source"]["url"]},
            *[{"label": f"Assinatura: {s['doc']}", "url": s["url"]} for o in hl["officials"] if o.get("signed") for s in o["source"][:2]],
            {"label": "Governadores: Alesc", "url": governors[0]["source"]["url"] if isinstance(governors[0]["source"], dict) else governors[0]["source"]},
            {"label": "Pagamentos: Portal da Transparência de SC", "url": paid_years[0]["query_url_all_units"]},
        ],
    }


# ---------- Works researched in round 10 (data/works/*.json) ----------
# One converter for every work record. The records carry official words (summary_quote) and neutral readings written
# by the research; this file only reshapes them. Candidacies in the 2026 election are not in the data (D54).
import unicodedata

PREVIEWS = ROOT / "docs" / "superpowers" / "previews"


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return "-".join("".join(ch if ch.isalnum() else " " for ch in s).split())


def all_credits():
    """Every photo credit under assets/cases, so a governor's portrait is reused across cases."""
    out = {}
    for f in (PREVIEWS / "assets" / "cases").glob("*/credits.json"):
        for name, c in json.loads(f.read_text(encoding="utf-8")).items():
            out[f"assets/cases/{f.parent.name}/{name}"] = c
    return out


# Each portrait under assets/cases with the exact names (as the case data writes them) of the one person it shows. A photo goes
# only to an exact name, never to a name that merely starts the same way.
PORTRAITS = {
    "Adriano Bornschein Silva (Adriano Silva)": "prefeito-adriano-silva",
    "Carlos Moisés da Silva": "gov-carlos-moises",
    "Daniela Reinehr": "gov-daniela-reinehr",
    "Jorginho Mello": "gov-jorginho-mello",
}


def portrait(name, credits):
    """The portrait of exactly this person (PORTRAITS), wherever it sits under assets/cases."""
    stem = PORTRAITS.get(name)
    hits = [(path, c) for path, c in credits.items() if stem and path.rsplit("/", 1)[1].rsplit(".", 1)[0] == stem]
    return hits[0] if hits else (None, None)


EN_MONTH = {m: i + 1 for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}


def pt_dates(s):
    """'Sep 5, 2026, 2:00:12 AM' (a raw system timestamp copied from a portal) -> '05/09/2026'."""
    import re
    s = re.sub(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{1,2}), (\d{4})(?:, \d{1,2}:\d{2}:\d{2} [AP]M)?",
               lambda m: f"{int(m.group(2)):02d}/{EN_MONTH[m.group(1)]:02d}/{m.group(3)}", str(s))
    return re.sub(r"\b(\d{4})-(\d{2})-(\d{2})\b", r"\3/\2/\1", s)  # ISO dates read as dd/mm/aaaa


def clip(s, n=360):
    s = " ".join(pt_dates(s).split())
    return s if len(s) <= n else s[: s.rfind(" ", 0, n)] + " [...]"


def fmt_date(s):
    s = str(s)
    return f"{s[8:10]}/{s[5:7]}/{s[:4]}" if len(s) >= 10 and s[4] == "-" and s[7] == "-" else s


def contract_url(c):
    for k in ("source", "register_record"):
        v = c.get(k)
        if isinstance(v, dict) and v.get("url"):
            return v["url"]
        if isinstance(v, str) and v.startswith("http"):
            return v
    return None


def work_case(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    w, slug = d["work"], d["slug"]
    credits = all_credits()
    own = {k: v for k, v in credits.items() if k.startswith(f"assets/cases/{slug}/")}
    is_person = lambda k: k.rsplit("/", 1)[1].split("-", 1)[0] in ("gov", "prefeito", "prefeita", "vice", "pessoa")
    credit = lambda c: {"credit": f"{c['author']}, {c['license']}", "link": c["commons"]}
    media = [{"src": k, "caption": c.get("caption") or (clip(c.get("description") or w["short_name"], 120) + (f" Foto de {str(c['date'])[:4]}." if str(c.get("date", ""))[:4] >= "1900" else "")
                                                        + (f" {PHOTO_NOTE[slug]}" if slug in PHOTO_NOTE else "")), **credit(c)}
             for k, c in own.items() if not is_person(k)]
    card = d["card"]
    photo = card.get("photo")
    photo = photo.replace("docs/superpowers/previews/", "") if photo else (media[0]["src"] if media else None)

    people = []
    # Same rule as the bridge: public agents who signed for the government side, and the head of government at the time.
    # People who signed for the contractor and contract managers stay in the research record, not on the page.
    for p in d.get("people", []):
        if not p.get("name") or p.get("side") == "contratada" or not p.get("signed"):
            continue
        if any(x in p["role"].lower() for x in ("contratada", "gestor", "fiscal", "empresa", "consórcio", "consorcio")):
            continue
        signed = p.get("signed") or []
        acts = "; ".join(f"{s['act']} ({fmt_date(s['date'])})" for s in signed[:3]) + (f"; e mais {len(signed) - 3}" if len(signed) > 3 else "")
        src, c = portrait(p["name"], credits)
        links = [{"label": s["act"].split(" (")[0].split(",")[0][:30], "url": s["url"]} for s in signed[:2] if s.get("url")]
        if str(p.get("role_source", "")).startswith("http"):
            links.append({"label": "Cargo", "url": p["role_source"]})
        people.append({"name": p["name"], "role": p["role"], "detail": f"assinou: {acts}" if acts else p.get("detail", ""),
                       "photo": src, "photo_credit": c and credit(c)["credit"], "photo_link": c and credit(c)["link"],
                       "party": p.get("party_at_time"), "party_name": "", "party_note": p.get("party_note", ""), "links": links})
    for g in (d.get("governors") or []) + (d.get("head_of_government") or []):
        src, c = portrait(g["name"], credits)
        url = next((x for x in str(g.get("source", "")).split() if x.startswith("http")), None)
        label = "Candidaturas no TSE" if url and "tse.jus.br" in url else "Biografia oficial"
        people.append({"name": g["name"], "role": g.get("office", "Governador"), "detail": "no período de: " + pt_dates("; ".join(g.get("relevant_dates", []))),
                       "photo": src, "photo_credit": c and credit(c)["credit"], "photo_link": c and credit(c)["link"],
                       "party": g.get("party_at_time"), "party_name": "", "party_note": g.get("party_note", ""),
                       "links": [{"label": label, "url": url}] if url else []})

    contracts = d.get("contracts", [])
    # A contract whose number is not published (sp-monotrilho-linha-17) is named by company and date, never merged with another.
    for c in contracts:
        if not c.get("number"):
            c["number"] = f"contrato com {c['company']} de {fmt_date(c['signed_on'])}" if c.get("signed_on") else f"contrato com {c['company']}"
    def value_of(number):
        head = number.split(" (")[0]
        return sum(c.get("value_current_brl") or 0 for c in contracts if c["number"].split(" (")[0] == head)
    company_cards = []
    here = {c["number"].split(" (")[0] for c in contracts}
    for co in d.get("companies", []):
        all_nums = [str(x) for x in co.get("contracts", [])]
        nums = [n for n in all_nums if n.split(" (")[0] in here or "consorciada" in n or "líder" in n]
        elsewhere = [n for n in all_nums if n not in nums]
        holder = all("consorciada" not in x and "líder" not in x for x in nums)
        if not holder:
            continue  # consortium members are listed inside the consortium's card
        members = [pt["name"] for pt in co.get("partners", []) if "Consorciada" in pt.get("qualification", "")]
        ctr = next((c for c in contracts if c["number"].split(" (")[0] in [n.split(" (")[0] for n in nums]), {})
        links = []
        if co.get("official_website"):
            links.append({"label": "Site oficial", "url": co["official_website"]})
        if co.get("cnpj"):
            links.append({"label": "Portal da Transparência", "url": f"https://portaldatransparencia.gov.br/pessoa-juridica/{co['cnpj']}"})
        if isinstance(co.get("source"), dict) and co["source"].get("url"):
            links.append({"label": "Cadastro (CNPJ)", "url": co["source"]["url"]})
        company_cards.append({"name": co["legal_name"], "cnpj": cnpj(co["cnpj"]) if co.get("cnpj") else None,
                              "trade_name": co.get("trade_name"), "city": co.get("city"),
                              "note": "; ".join(x for x in (("consórcio de " + " e ".join(members)) if members else "",
                                                             ("também tem o contrato " + ", ".join(elsewhere)) if elsewhere else "") if x) or None,
                              "contracts": [n.split(" (")[0] for n in nums], "value": sum(value_of(n) for n in nums),
                              "status": (ctr.get("status") or co.get("registration_status", "")).split(" (")[0].split(";")[0], "links": links})
    for c in contracts:  # a contract whose company has no registry card (for example a consortium without CNPJ)
        if not any(c["number"].split(" (")[0] in cc["contracts"] for cc in company_cards):
            company_cards.append({"name": c["company"], "cnpj": cnpj(c["company_cnpj"]) if c.get("company_cnpj") else None,
                                  "cnpj_note": "CNPJ não publicado no registro da contratante", "contracts": [c["number"].split(" (")[0]],
                                  "value": c.get("value_current_brl") or c.get("value_original_brl") or 0, "status": c.get("status", ""), "links": [{"label": "Registro do contrato", "url": contract_url(c)}] if contract_url(c) else []})
    company_cards.sort(key=lambda c: -c["value"])

    findings = []
    for f in d.get("findings", []):
        findings.append({"body": f"{f['body']} ({str(f['date'])[:4]})", "text": f"{f['process']}: “{clip(f['summary_quote'])}”",
                         "status": f["status"] + (f". Sobre esta obra: {f['about_this_contract']}" if f.get("about_this_contract") else ""), "url": f.get("url")})
    sections = [{"title": "Contratos", "items": [{"head": f"{c['number'].split(' (')[0]} · {c['company']}",
                  "text": f"{clip(c.get('object_plain') or c['object'], 220)} Valor original {brl(c['value_original_brl']) if c.get('value_original_brl') is not None else 'não publicado'}; atual {brl(c['value_current_brl']) if c.get('value_current_brl') is not None else 'não publicado'}. Situação: {c['status']}.",
                  "url": contract_url(c)} for c in contracts]}]
    if w.get("status_detail"):
        sections.append({"title": "Andamento", "items": [{"head": fmt_date(s["date"]) if s.get("date") else w.get("status", "Situação"), "text": s["text"], "url": s.get("url")} for s in w["status_detail"]]})

    cmp = d.get("comparison") or {}
    compare = None
    if cmp.get("items"):
        key = cmp.get("value_key") or next(k for k in cmp["items"][0] if k.startswith("cost_per_") and k.endswith("_brl_2024"))
        unit = cmp.get("unit_short") or UNIT_SHORT.get(key, cmp["unit"])
        when = lambda i: clip(i["years"], 50) if i.get("years") else (f"contrato de {i['contract_month'][4:]}/{i['contract_month'][:4]}" if i.get("contract_month") else "")
        items = [{"label": card["title"] if i.get("is_subject") else clip(i["name"], 60), "detail": f"{i['place']} · {when(i)}", "value": i[key], "self": bool(i.get("is_subject")),
                  "display": f"R$ {num(i[key])} por {unit}"} for i in cmp["items"] if i.get(key)]
        items.sort(key=lambda i: -i["value"])
        compare = {"title": cmp.get("title") or f"Custo por {unit}, em reais de 2024", "subtitle": cmp.get("subtitle") or f"Unidade: {cmp['unit']}. {cmp['method'].get('brl_rule', '')}",
                   "items": items, "gap": {"positive": bool(cmp.get("gap_flag") or GAP_FLAG.get(slug)), "text": cmp["reading"]},
                   "reading": "O que cada obra incluiu: " + " ".join(f"{card['title'] if i.get('is_subject') else clip(i['name'], 70)} ({i['place']}): {i.get('scope_note') or i.get('project')}." for i in cmp["items"] if i.get("scope_note") or i.get("project")),
                   "sources": [{"label": clip(i["name"], 40), "url": (i["sources"][0]["url"] if isinstance(i["sources"][0], dict) else i["sources"][0])} for i in cmp["items"] if i.get("sources")]}

    facts = [{"label": s["label"], "value": s["display"], "note": s.get("note") and clip(s["note"])} for s in card["stats"]]
    agency = w["agency"]["name"] if isinstance(w.get("agency"), dict) else str(w.get("agency", ""))
    short_agency = agency.split(",")[0] if "," in agency else agency[agency.rfind("(") + 1:-1] if agency.endswith(")") else agency
    facts.append({"label": "Quem contrata", "value": short_agency, "note": " · ".join(x for x in (agency if short_agency != agency else "", w.get("financing")) if x)})
    muni = w["municipalities"][0]
    sources = [{"label": clip(u, 60), "url": u} for u in w.get("sources", [])[:4]]
    return {
        "id": slug, "uf": d.get("uf", "SC"), "municipality": str(muni["ibge_code"]), "municipalities": [str(m["ibge_code"]) for m in w["municipalities"]],
        "function": w.get("siconfi_function"), "kind": "obra",
        "media": media, "people": people, "company_cards": company_cards, "sections": sections,
        "card": {"image": photo, "stats": [[s["label"], s["display"]] for s in card["stats"]]},
        "title": card["title"], "short": card["title"], "teaser": card["subtitle"] + f". {muni['name']}.",
        "subtitle": w["description_plain"], "facts": facts, "findings": findings, "compare": compare, "sources": sources,
        "status": w.get("status"),
        "people_note": " ".join(x for x in (d.get("head_of_government_note") or d.get("governors_note"),
                                            "Partido na época, segundo o registro de candidaturas do TSE." if d.get("head_of_government") else
                                            "Partido na época do ato, segundo a biografia oficial na Assembleia Legislativa de SC.",
                                            "Fotos do Wikimedia Commons, com autor e licença no link de cada foto.") if x),
    }


def mi(v):
    return f"R$ {v / 1e6:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")


def split_top(s, sep="; "):
    """Split on sep only outside parentheses."""
    out, depth, cur, i = [], 0, "", 0
    while i < len(s):
        ch = s[i]
        depth += ch == "("; depth -= ch == ")"
        if depth == 0 and s.startswith(sep, i):
            out.append(cur); cur = ""; i += len(sep); continue
        cur += ch; i += 1
    return out + [cur]


def contractor(s):
    """'Consórcio A (2014); B (2020)' -> ('Consórcio B', history); 'Consórcio X (Ivaí líder; ...)' -> ('Consórcio X', detail)."""
    segs = split_top(s)
    last = segs[-1]
    name, detail = (last[: last.rfind(" (")], last[last.rfind(" (") + 2: -1]) if last.endswith(")") and " (" in last else (last, None)
    if segs[0].startswith("Consórcio") and not name.startswith("Consórcio"):
        name = "Consórcio " + name
    note = ("histórico do contratado: " + s) if len(segs) > 1 else detail
    return name, note


def party_text(v):
    if isinstance(v, dict):
        return ", depois ".join(f"{p} ({str(d)[:4]})" for d, p in sorted(v.items()))
    return v


def road_case(path):
    """Road records (BR-470, SC-401): contracts carry the company names, comparison is per km."""
    d = json.loads(path.read_text(encoding="utf-8"))
    w, slug, cmpd = d["work"], d["slug"], d["comparison"]
    credits = all_credits()
    strip = lambda s: s.replace("docs/superpowers/previews/", "")
    # The road photos show the surroundings; the Contorno's shows the work itself (Túnel 2), so it carries no such note.
    note = "" if slug in SHOWS_WORK else " Mostra o entorno; não há foto de uso livre da obra."
    media = [{"src": strip(m["file"]), "caption": f"{m['caption']}.{note}", "credit": f"{m['author']}, {m['license']}", "link": m["page"]} for m in d.get("media", [])]
    title = cmpd["this_work"]["name"].split(" (")[0].replace(" - ", " a ")

    people = []
    for p in d.get("people", []):
        head = p.get("head_of_government")
        # D48: everyone with a role in an official document appears; a manager fined by the TCU has one, even in an inspection role.
        fined = "multa" in (p.get("note") or "").lower()
        if not (head or p.get("signed") or p.get("on_dates")) or (any(x in p["role"].lower() for x in ("fiscal", "gerente de fiscaliza")) and not fined):
            continue
        src, c = portrait(p["name"], credits)
        signed = [pt_dates(s) for s in (p.get("signed") or [])]
        detail = ("assinou: " + "; ".join(signed[:3]) + (f"; e mais {len(signed) - 3}" if len(signed) > 3 else "")) if signed \
            else "no período de: " + pt_dates("; ".join(p.get("on_dates", [])))
        links = []
        for s in (p.get("source") or [])[:2]:
            url = s["url"] if isinstance(s, dict) else s
            label = "Candidaturas no TSE" if "tse.jus.br" in url else "Biografia oficial" if "alesc" in url else "Documento"
            links.append({"label": label, "url": url})
        people.append({"name": p["name"], "role": p["role"], "detail": detail, "photo": src,
                       "photo_credit": c and f"{c['author']}, {c['license']}", "photo_link": c and c["commons"],
                       "party": party_text(p.get("party_at_time")), "party_name": p.get("party_name", "") or "", "party_note": p.get("note", "") or "", "links": links})

    registry = {c["cnpj"]: c for c in d.get("companies", [])}
    def holder(number):
        """The current holder of a contract: the registry entry that names it and is not a past leader or a member."""
        for c in d.get("companies", []):
            for x in c["contracts"]:
                if x.startswith(number) and not any(k in x for k in ("líder em", "líder de ", "consorciada")):
                    return c
        return None
    cards = {}
    for ct in d["contracts"]:
        name, cnote = contractor(ct["company"])
        value = ct.get("value_global_current_brl") or ct.get("value_current_brl") or ct.get("value_current_initial_prices_brl") or 0
        reg = holder(ct["number"])
        card = cards.setdefault(name, {"name": name, "cnpj": cnpj(reg["cnpj"]) if reg else None, "trade_name": reg and reg.get("trade_name"),
                                       "city": reg and reg.get("city"), "contracts": [], "value": 0.0, "status": ct.get("status_in_record", ""), "links": [],
                                       "note": None, "cnpj_note": "CNPJ do consórcio não publicado no registro"})
        card["contracts"].append(ct["number"]); card["value"] += value
        if cnote:
            card["note"] = cnote
        if reg and not card["links"]:
            for u in reg.get("transparency_links", [])[:2]:
                card["links"].append({"label": "Portal da Transparência" if "portaldatransparencia" in u else "Transparência de SC", "url": u})
            if reg.get("official_website"):
                card["links"].insert(0, {"label": "Site oficial", "url": reg["official_website"]})
        if not card["links"] and ct.get("sources"):
            card["links"].append({"label": "Registro do contrato", "url": ct["sources"][0]["url"]})
    company_cards = sorted(cards.values(), key=lambda c: -c["value"])
    for c in company_cards:
        c["contracts"] = sorted(set(c["contracts"]))
    # A concession has no contract value paid by the government: the concessionaire's card shows what it declares it
    # invested, and a private contract of the concessionaire with no published value says so instead of showing R$ 0.
    company_lead = None
    head = d.get("card", {}).get("head")
    if head and slug in SHOWS_WORK:
        company_lead = "investimento declarado pela concessionária; contratos dela com construtoras não têm valor publicado"
        for c in company_cards:
            if c["cnpj"]:
                c["value"] = head["investment_total"]["value_brl"]
            elif not c["value"]:
                c["value"] = None; c["value_note"] = "valor não publicado (contrato privado da concessionária)"
                c["cnpj_note"] = "CNPJ não citado no comunicado da concessionária"
        company_cards.sort(key=lambda c: -(c["value"] or 0))
    # A controller holds no contract of its own: it is named on the card of the company it controls.
    for reg in d.get("companies", []):
        if "controladora" in (reg.get("role") or "") and reg.get("cnpj"):
            for c in company_cards:
                if c["cnpj"]:
                    c["note"] = " ".join(x for x in (c["note"], f"Controlada pela {reg['legal_name'].title().replace(' S.A.', ' S.A.')} (CNPJ {cnpj(reg['cnpj'])}).") if x)
                    break

    findings = [{"body": f"{f['body']} ({str(f.get('date', ''))[:4]})".replace(" ()", ""),
                 "text": f"{f.get('decision') or f['process']}: “{clip(f['summary_quote'])}”",
                 "status": f["status"], "url": f.get("url")} for f in d.get("findings", [])]
    sections = [{"title": "Contratos", "items": [{"head": f"{ct['number']}{' · lote ' + ct['lot'] if ct.get('lot') else ''} · {contractor(ct['company'])[0]}",
                  "text": f"{clip(ct['object'], 200)} " + "; ".join(x for x in (
                      f"Valor original {brl(ct['value_original_brl'])}" if ct.get("value_original_brl") is not None else "Valor original não publicado no registro",
                      f"atual {brl(ct.get('value_global_current_brl') or ct.get('value_current_brl'))}" if (ct.get("value_global_current_brl") or ct.get("value_current_brl")) else "") if x)
                      + f". Situação: {ct.get('status_in_record', '')}.",
                  "url": ct["sources"][0]["url"] if ct.get("sources") else None} for ct in d["contracts"]]}]
    if d.get("people_gaps"):
        sections.append({"title": "O que ainda não se sabe", "items": [{"head": "Lacuna", "text": g} for g in d["people_gaps"]]})

    allw = [dict(cmpd["this_work"], self=True), *cmpd["comparables"]]
    items = sorted([{"label": x["name"].split(" (")[0] if not x.get("self") else title, "detail": x.get("category", ""), "value": x["cost_per_km_brl_2024"],
                     "self": bool(x.get("self")), "display": f"{mi(x['cost_per_km_brl_2024'])} por km"} for x in allw], key=lambda i: -i["value"])
    compare = {"title": "Custo por km, em reais de 2024", "subtitle": f"Unidade: {cmpd['unit']}.", "items": items,
               "gap": {"positive": bool(GAP_FLAG.get(slug)), "text": cmpd["result"]},
               "reading": " ".join(cmpd.get("caveats", [])),
               "sources": [{"label": x["name"].split(" (")[0][:40], "url": x["sources"][0]["url"]} for x in allw if x.get("sources")]}

    agency = w["agency"]["name"]
    munis = w["municipalities_ibge"]
    facts = [{"label": k, "value": v, "note": None} for k, v in d["card"]["stats"]]
    facts.append({"label": "Quem contrata", "value": agency.split(",")[0].split(" (")[0], "note": agency})
    facts.append({"label": "Extensão", "value": f"{str(w['length_km']).replace('.', ',')} km", "note": ", ".join(m["name"] for m in munis)})
    return {
        "id": slug, "uf": "SC", "municipality": munis[0]["code"], "municipalities": [m["code"] for m in munis], "function": w.get("siconfi_function"), "kind": "obra",
        "media": media, "people": people, "company_cards": company_cards, "company_lead": company_lead, "sections": sections,
        "card": {"image": strip(d["card"]["image"]), "stats": d["card"]["stats"]},
        "title": title, "short": title, "teaser": f"{w['status'].split('. ')[0]}. {', '.join(m['name'] for m in munis)}.",
        "subtitle": w["description"], "facts": facts, "findings": findings, "compare": compare,
        "sources": [{"label": s["doc"][:60], "url": s["url"]} for ct in d["contracts"][:1] for s in ct.get("sources", [])[:2]],
        "status": w["status"],
        "people_note": " ".join(x for x in (d.get("people_note"), "Partido na época, segundo a biografia oficial na Alesc ou o registro de candidaturas do TSE.",
                                            "Fotos do Wikimedia Commons, com autor e licença no link de cada foto.") if x),
    }


ROAD = {"sc-401-terceira-faixa", "br-470-duplicacao", "florianopolis-bypass"}
SHOWS_WORK = {"florianopolis-bypass"}


# Short unit for each comparison key the research records use.
UNIT_SHORT = {"cost_per_l_s_final_brl_2024": "L/s de capacidade", "cost_per_place_brl_2024": "vaga"}
# "PARA ONDE FOI O DINHEIRO?" only where the research numbers show a cost gap the official record does not explain.
# CEI Comasa: 1,4x the m² of a same-state FNDE creche and 2,7x the state SINAPI m² against 1,4 to 2,0
# for the others; the reading itself says the record does not explain the difference. Pending legal review (Q13).
GAP_FLAG = {"cei-comasa-joinville": True}
# The research found no free-licensed photo of these works; the page says so under the landscape it shows instead.
PHOTO_NOTE = {"ete-insular": "Mostra a região; não há foto de uso livre da estação.",
              "cei-comasa-joinville": "Mostra a região; não há foto de uso livre da creche."}
WORK_ORDER = ["ete-insular", "cei-comasa-joinville", "sc-401-terceira-faixa", "br-470-duplicacao", "sp-monotrilho-linha-17", "florianopolis-bypass"]  # extended as each research record lands


# The Criciúma fleet case is not published (D28); its research stays in docs/research/.
cases = [c for c in (bridge_case(), *((road_case if s in ROAD else work_case)(DATA / 'works' / f'{s}.json') for s in WORK_ORDER if (DATA / 'works' / f'{s}.json').exists())) if c]


# Every case card opens like the monotrilho's, "Investimento total" then "Contrato inicial". The
# parenthesis says what each number measures (paid, current contract, the government's figure), never a sum the data
# cannot support. Values are read from the research records, not typed here; the other two lines stay as they were.
def head_stats(cid):
    W = lambda s: json.loads((DATA / "works" / f"{s}.json").read_text(encoding="utf-8"))
    # D100: the first number is the complete total actually spent, with its source. The totals that
    # closed the last gaps are in data/complete-totals-2026-10-06.json (pipelines/complete_totals/, cent checks and controls).
    T = json.loads((DATA / "complete-totals-2026-10-06.json").read_text(encoding="utf-8"))["gaps"]
    if cid == "ponte-hercilio-luz":
        # Audit 2026-10-06 (cases, Ponte): the paid total now includes the 2006 first stage (PJ 015/2006), and the initial
        # value is the first contracts only (2006 to 2008); a contract that replaced a rescinded one is not added again (D95).
        pc = json.loads((DATA / "hercilio-luz-paid-by-contract.json").read_text(encoding="utf-8"))
        return (("Investimento total (pago, 2006 a 2020)", brl(pc["total_paid_2006_2020_brl"]), pc["total_paid_2006_2020_includes"]),
                ("Contrato inicial (2006 a 2008)", brl(pc["initial_contracts_2006_2008"]["value_original_brl"]), pc["initial_contracts_2006_2008"]["rule"]),
                ("Valor dos contratos", "Contratos"))
    if cid == "ete-insular":
        c = next(x for x in W(cid)["contracts"] if x["number"].startswith("EOC 1246/2020"))
        return (("Investimento total (realizado até dez/2025)", brl(T["ete_insular"]["value_brl"]),
                 "custo da ampliação do sistema Insular registrado pela Casan (Relatório da Administração 2025); pode incluir juros do financiamento"),
                (f"Contrato inicial ({c['signed_on'][:4]})", brl(c["value_original_brl"]), c["company"]), ("Já consumido", "Capacidade"))
    if cid == "cei-comasa-joinville":
        d = W(cid); c = d["contracts"][0]
        return (("Investimento total (pago)", brl(d["payments"]["total_gross_brl"]), "liquidado bruto, Portal da Transparência de Joinville"),
                (f"Contrato inicial ({c['signed_on'][:4]})", brl(c["value_original_brl"]), c["company"]), ("Pago", "Vagas"))
    if cid == "sc-401-terceira-faixa":
        c = next(x for x in W(cid)["contracts"] if x["number"] == "CT-00014/2025")
        return (("Investimento total (pago até set/2026)", brl(T["sc401_paid"]["value_brl"]),
                 "pago à construtora, com os impostos retidos (INSS, IRRF e ISS), Portal da Transparência de SC; obra em execução"),
                (f"Contrato inicial ({c['signed_on'][:4]})", brl(c["value_original_brl"]), c["company"]), ("Pago até set/2026", "Aditivo de valor"))
    if cid == "br-470-duplicacao":
        d = W(cid)
        return (("Investimento total (pago, União e SC)", brl(d["payments"]["total_public_paid_brl_computed"]), "pago de 2014 a set/2026"),
                ("Contrato inicial (4 lotes)", brl(d["contracts_totals_computed"]["value_original_brl"]), "soma dos contratos de obra assinados"), ("Contratos de obra (preço inicial)", "Pago (União e Estado)"))
    if cid == "florianopolis-bypass":
        h = W(cid)["card"]["head"]
        a, b = h["investment_total"], h["initial_contract"]
        return ((a["label"], a["display"], a["note"]), (b["label"], b["display"], b["note"]), (a["label"], b["label"]))
    if cid == "sp-monotrilho-linha-17":
        st = W(cid)["card"]["stats"]
        v = T["metro_line17_invested"]["value_brl"]
        return (("Investimento total (realizado pelo Metrô)", "R$ " + f"{v / 1e9:.2f}".replace(".", ",") + " bi",
                 "investimento na Linha 17, 2010 a ago/2026, regime de caixa, relatórios do Metrô; o Governo de SP divulga R$ 5,97 bi, sem detalhar"),
                ("Contrato inicial (2011)", st[1]["display"], st[1].get("note")), (st[0]["label"], st[1]["label"]))
    return None

for c in cases:
    hs = head_stats(c["id"])
    if not hs:
        continue
    inv, ini, drop = hs
    c["card"]["stats"] = [[inv[0], inv[1]], [ini[0], ini[1]]] + [s for s in c["card"]["stats"] if s[0] not in drop][:2]
    c["facts"] = [{"label": inv[0], "value": inv[1], "note": inv[2]}, {"label": ini[0], "value": ini[1], "note": ini[2]}] + [f for f in c["facts"] if f["label"] not in drop]
# D102: "Em andamento", "Concluído" or "Abandonado", each from a dated official source (data/works/stages.json).
STAGES_FILE = ROOT / "data" / "works" / "stages.json"
STAGES = json.loads(STAGES_FILE.read_text(encoding="utf-8"))["cases"] if STAGES_FILE.exists() else {}
STAGE_KIND = {"Em andamento": "ongoing", "Concluído": "done", "Abandonado": "abandoned"}
for c in cases:
    s = STAGES.get(c["id"])
    if s:
        if not (s["label"] in STAGE_KIND and s.get("source_url") and s.get("as_of")):
            raise SystemExit(c["id"])
        c["stage"] = {"label": s["label"], "kind": STAGE_KIND[s["label"]], "as_of": s["as_of"], "url": s["source_url"]}
TARGET.write_text(json.dumps(cases, ensure_ascii=False), encoding="utf-8")
print(f"{len(cases)} case(s) -> {TARGET.relative_to(ROOT)}")
for c in cases:
    print(c["title"], "|", c["teaser"])
    for f in c["facts"]:
        print("  ", f["label"], "=", f["value"], "|", f.get("note"))
    for o in c.get("officials", []):
        print("  official:", o)
    print("  gap:", c["compare"] and c["compare"]["gap"])
