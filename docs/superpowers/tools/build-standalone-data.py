"""Packs the preview data into classic scripts so the previews open straight from the file path.

Chrome blocks fetch() and local ES-module imports on file:// pages, but classic <script src> works. Flags used as
WebGL textures are inlined as data URIs, because an image loaded from file:// would taint the canvas.
Run: .venv/bin/python docs/superpowers/tools/build-standalone-data.py
Every input the page reads is required: a missing file stops the build with the name of the script that writes it.
"""
import base64
import json
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "previews" / "assets"
load = lambda name: json.loads((ASSETS / name).read_text(encoding="utf-8"))


def need(path, writer):
    if not path.exists():
        raise SystemExit(f"missing input {path}: written by {writer}")
    return path


read = lambda path, writer: json.loads(need(path, writer).read_text(encoding="utf-8"))

geo = load("map-geo.json")
icons = {p.stem: p.read_text(encoding="utf-8") for p in sorted((ASSETS / "icons").glob("*.svg"))}
flag_data = {}
for c in geo["countries"]:
    if c.get("flag") and c["flag"] not in flag_data:
        svg = (ASSETS / "flags" / f"{c['flag']}.svg").read_bytes()
        flag_data[c["flag"]] = "data:image/svg+xml;base64," + base64.b64encode(svg).decode()

# The 27 states with name and population (2024, the base the map divides by when a period has no population of its own).
STATES = [{"uf": s["uf"], "name": s["name"], "population": s["population"]}
          for s in json.loads((ASSETS.parents[3] / "data" / "uf-balance-2024.json").read_text(encoding="utf-8"))]
data = {"states": STATES, "budgets": load("state-budgets.json"), "cases": load("cases.json"),
        "icons": icons, "flagData": flag_data, "regions": {s["uf"]: s["region"] for s in geo["brazil"]}}
# Taxes paid in each state, all three spheres: federal by tax (Receita Federal), state lines come with the budgets,
# municipal is the sum over every municipality (SICONFI); municipal stays null until that collection has run.
DATA = ASSETS.parents[3] / "data"
data["federal"] = {s["uf"]: {"by_tax": s["federal_revenue"]["by_tax"], "total": s["federal_revenue"]["total"],
                             "rfb": s["federal_revenue"]["rfb_administered"]}
                   for s in json.loads((DATA / "uf-balance-2024.json").read_text(encoding="utf-8"))}
data["municipal"] = read(DATA / "municipal-taxes-2024.json", "pipelines/siconfi/build_municipal_taxes.py")["by_uf"]
# Santa Catarina, one level down: the municipal balance and the municipal map (round 9).
data["sc"] = read(DATA / "sc-municipal-balance-2024.json", "pipelines/municipios/build_municipal_balance.py")
# Time series (round 10), each with the script that writes it.
SERIES = DATA / "series"
SERIES_WRITERS = {
    "union": "pipelines/series/build_union_series.py", "union-spending-slices": "pipelines/federal/build_spending_slices.py",
    "population": "pipelines/series/build_population.py", "federal-by-uf-monthly": "pipelines/series/build_federal_by_uf_monthly.py",
    "state-budgets": "pipelines/series/build_state_series.py", "sc-municipal-federal": "pipelines/series/build_municipal_federal.py",
    "sc-municipal-budgets": "pipelines/series/build_municipal_series.py", "rs-municipal-federal": "pipelines/series/build_municipal_federal.py",
    "rs-municipal-budgets": "pipelines/series/build_municipal_series.py", "federal-revenue-uf-estimated": "pipelines/series/estimate_uf_revenue.py",
    "federal-payroll-by-uf": "pipelines/series/build_federal_payroll_by_uf.py", "federal-spending-two-step-by-uf": "pipelines/ug/build_two_step_series.py",
    "public-sector-primary": "pipelines/series/fetch_public_sector_primary.py"}
data["series"] = {name.replace("-", "_"): read(SERIES / f"{name}.json", writer) for name, writer in SERIES_WRITERS.items()}
# D71: RS has no 2024 balance file; its map list (code, name, latest population) comes from its own series. The map reads
# every number through the period layer, as SC's does.
latest = lambda pop: next((pop[y] for y in sorted(pop, reverse=True) if pop[y] is not None), None)
data["rs"] = {"uf": "RS", "municipalities": [{"code": c, "name": m["name"], "population": latest(m["population"])}
                                            for c, m in sorted(data["series"]["rs_municipal_federal"]["municipalities"].items())]}
# Post-grill rounds: the date each source last published (GD33) and the federal section below the map (D44).
data["releases"] = json.loads((DATA / "release-dates.json").read_text(encoding="utf-8"))["sources"]
data["federal_section"] = read(DATA / "federal" / "federal-section.json", "pipelines/federal/build_federal_section.py")
# D72: headcount and average pay per branch (RPPS and military actuarial bases) and the CNJ all-in cost per magistrate.
data["federal_servants"] = read(DATA / "federal" / "servants-by-branch.json", "a hand-transcribed record (no script; its sources are inside it)")
# D71: the GDF money per Região Administrativa (administration budgets, spending that names a region, administrators, works).
data["df_money"] = read(DATA / "df" / "region-money.json", "pipelines/df/build_region_money.py")
# The DF estimate on the map (D146): the DF's share of Brazil's GDP caps each tax the Receita registers in the DF.
data["df_gdp_share"] = read(DATA / "df" / "gdp-share.json", "pipelines/df/fetch_gdp_share.py")
# Home side panels (D64, D65): recent big decisions and the largest cases of the period, when the research is in.
home = DATA / "home"
data["home"] = {k: read(home / f"{k}.json", "a research record curated by hand (no script)") for k in ("recent", "scandals")}
# D91: "Resolvido" or "Não resolvido" on each scandal, with the reason and the money recovered (scandals-status.json).
S = read(home / "scandals-status.json", "a research record curated by hand (no script)")
for it in data["home"]["scandals"]["items"]:
    if it["id"] in S["items"]:
        it["resolution"] = {**S["items"][it["id"]], "checked_on": S["checked_on"]}
# D88, D89: one list of money moves for the two period columns (largest spending, largest income) and the months each
# side has been collected for, so a period not collected yet says so instead of looking empty. recent.json covers
# jul to out/2026 on both sides; moves-spending.json and moves-revenue.json (research of 2026-10-04) add the earlier years.
MON = {m: i + 1 for i, m in enumerate(["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"])}
def covered_months(year, text):
    t = (text or "").lower()
    if t.startswith("ano completo"):
        return [f"{year}-{m:02d}" for m in range(1, 13)]
    a, _, b = t.partition(" a ")
    if a[:3] in MON and b[:3] in MON:
        return [f"{year}-{m:02d}" for m in range(MON[a[:3]], MON[b[:3]] + 1)]
    raise SystemExit(f"coverage of {year} not understood: {text!r}")
items = list(data["home"]["recent"]["items"])
cov = {"out": [f"2026-{m:02d}" for m in range(7, 11)], "in": [f"2026-{m:02d}" for m in range(7, 11)]}
for name, side in (("moves-spending", "out"), ("moves-revenue", "in")):
    j = read(home / f"{name}.json", "a research record curated by hand (no script)"); seen = {x["id"] for x in items}
    items += [x for x in j["items"] if x["id"] not in seen]
    for y, text in j.get("coverage", {}).items():
        cov[side] = sorted(set(cov[side]) | set(covered_months(int(y), text)))
# D90 ("a conta fecha?"): data/home/moves-adjustments.json merges what is one measure into one card (the child shows
# inside the parent's details), marks what would count twice or never existed as out of the sum, and adds the cards
# listed in D90 (Banco Central transfers, MP 1.374). Lapsed spending MPs stay in the sum, tagged.
A = read(home / "moves-adjustments.json", "a research record curated by hand (no script)")
seen = {x["id"] for x in items}
items += [x for x in A["items"] if x["id"] not in seen]
by_id = {x["id"]: x for x in items}
for child, parent in A["merge"].items():
    c = by_id[child]
    by_id[parent].setdefault("merged", []).append({k: c.get(k) for k in ("title", "amount_brl", "amount_kind", "moved_on", "act", "amount_source")})
items = [x for x in items if x["id"] not in A["merge"]]
for k, v in A["not_in_total"].items():
    by_id[k]["in_total"] = False; by_id[k]["not_in_total_reason"] = v["reason"]
    by_id[k]["tags"] = sorted(set(by_id[k].get("tags", [])) | set(v["tags"]))
for x in items:
    if x["kind"] != "revenue" and (x.get("act") or {}).get("type") == "Medida Provisória" and str(x.get("status", "")).startswith(("Perdeu a eficácia", "Rejeitada", "Revogada")):
        x["tags"] = sorted(set(x.get("tags", [])) | {A["lapsed_spending_tag"]})
data["home"]["moves"] = {"items": items, "coverage": cov, "as_of": max(cov["out"] + cov["in"])}
# D110 (2026-10-07): "Por que falta dinheiro" on the home, from data/economy/union-shortfall-explained.json. D109 and D111:
# "O que o Brasil vende" on the home and "Vendeu ao exterior" in the state modal, from data/trade/. Only the fields shown are
# packed, and every packed total is checked against its source file; --control=shortfall or --control=trade breaks one value
# and must stop the build before anything is written.
import sys
CONTROL = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--control=")), "")
def check(ok, what):
    if not ok:
        raise SystemExit(f"check failed: {what}")
SHORTFALL_FACTS = [
    "central_nominal_deficit_2026ytd", "central_interest_2026ytd", "interest_share_of_nominal_deficit_2026ytd",
    "central_primary_deficit_below_line_2026ytd", "treasury_without_inss_primary_surplus_2026ytd", "inss_primary_deficit_2026ytd",
    "inss_primary_deficit_2025", "rgps_benefits_2025", "rgps_net_revenue_2025",
    "gross_debt_dbgg_aug2026", "gross_debt_dbgg_pct_gdp_aug2026", "gross_debt_selic_share_aug2026", "gross_debt_implicit_rate_12m_aug2026",
    "selic_annualized_aug2026", "ipca_12m_aug2026", "dpmfi_total_aug2026",
    "dpmfi_holder_financial_institutions_aug2026", "dpmfi_holder_pension_aug2026", "dpmfi_holder_investment_funds_aug2026",
    "dpmfi_holder_non_residents_aug2026", "dpmfi_holder_others_aug2026", "dpmfi_holder_insurers_aug2026",
    "dpmfi_holder_tesouro_direto_aug2026", "dpmfi_holder_government_aug2026",
    "export_tax_2025", "export_tax_2026_jan_jul", "natural_resources_revenue_2026ytd", "natural_resources_transfers_2026ytd",
    "dividends_petrobras_2026ytd", "export_rural_tax_expenditure_2026",
    "tax_expenditure_total_2026", "tax_expenditure_simples_2026", "tax_expenditure_agro_2026", "tax_expenditure_irpf_exempt_income_2026",
    "tax_expenditure_nonprofits_2026", "tax_expenditure_irpf_deductions_2026", "tax_expenditure_zfm_2026", "tax_expenditure_basic_basket_2026",
    "subsidies_total_2024", "subsidies_tax_2024", "cash_subsidies_rtn_2026ytd",
    "tax_burden_total_2025", "tax_burden_pct_gdp_2025", "tax_burden_central_2025", "tax_burden_states_2025", "tax_burden_municipalities_2025",
    "central_share_of_tax_burden_2025", "revenue_sharing_transfers_2025", "central_interest_2025",
]
SF = read(DATA / "economy" / "union-shortfall-explained.json", "a research record curated by hand (no script)")
by = {f["id"]: f for f in SF["facts"]}
facts = {}
for k in SHORTFALL_FACTS:
    f = by[k]; s = f["source"]
    facts[k] = {"v": f["value"], "unit": f["unit"], "period": f["period"], "body": s.get("body"), "doc": s.get("document"), "url": s.get("url"),
                **({"note": f["note"]} if f.get("note") else {})}
if CONTROL == "shortfall":
    facts["dpmfi_holder_pension_aug2026"]["v"] += 1
v = lambda k: facts[k]["v"]
holders = [k for k in SHORTFALL_FACTS if k.startswith("dpmfi_holder_")]
check(abs(sum(v(k) for k in holders) - v("dpmfi_total_aug2026")) < 0.5, "shortfall: the debt holders add up to the DPMFi total")
check(abs(v("tax_burden_central_2025") + v("tax_burden_states_2025") + v("tax_burden_municipalities_2025") - v("tax_burden_total_2025")) < 1,
      "shortfall: Union, states and municipalities add up to the tax burden")
check(abs(v("rgps_benefits_2025") - v("rgps_net_revenue_2025") - v("inss_primary_deficit_2025")) < 1, "shortfall: INSS 2025 benefits minus revenue equal its deficit")
check(v("tax_expenditure_total_2026") > sum(v(k) for k in SHORTFALL_FACTS if k.startswith("tax_expenditure_") and k not in ("tax_expenditure_total_2026", "tax_expenditure_basic_basket_2026")),
      "shortfall: the largest tax expenditures fit inside the total")
# The section says its numbers are the ones of "A conta da União" for January to August 2026: same interest, same result.
U = data["series"].get("union")
if U:
    ix = [i for i, m in enumerate(U["months"]) if "2026-01" <= m <= "2026-08"]
    check(len(ix) == 8 and all(U["nominal_interest"][i] is not None for i in ix), "shortfall: the União account has January to August 2026")
    check(abs(-sum(U["nominal_interest"][i] for i in ix) / 1e6 - v("central_interest_2026ytd")) < 0.05, "shortfall: interest equals the União account (jan to aug 2026)")
    check(abs(-sum(U["nominal_result"][i] for i in ix) / 1e6 - v("central_nominal_deficit_2026ytd")) < 0.05, "shortfall: the result equals the União account (jan to aug 2026)")
data["shortfall"] = {"collected_on": SF["collected_on"], "facts": facts}
TRADE = DATA / "trade"
need(TRADE / "exports-by-product.json", "the scripts in pipelines/trade/")
rd = lambda n: json.loads((TRADE / f"{n}.json").read_text(encoding="utf-8"))
EP, EU, PR, SH, CX, IM = (rd(n) for n in ("exports-by-product", "exports-by-uf", "export-prices", "export-share-of-production", "trade-context", "imports-by-product"))
YEARS = ("2025", "2026")
# Each product: [US$ FOB, R$, share of all exports, rank] per period; the 50 largest of a period also carry their 3 main
# destinations as [country, share of the product].
products = []
for p in EP["products"]:
    row = {"sh4": p["sh4"], "name": p["name"], "sh2": p["sh2"]}
    for y in YEARS:
        q = p.get(y)
        if q:
            row[y] = [q["usd_fob"], q["brl"], q["share"], q["rank"]] + ([[[d["country"], d["share_of_product"]] for d in q["top_destinations"]]] if q.get("top_destinations") else [])
    products.append(row)
if CONTROL == "trade":
    products[0]["2025"][0] += 1
periods = {}
for y in YEARS:
    per, rows = EP["periods"][y], [r[y] for r in products if y in r]
    check(sum(r[0] for r in rows) == per["total_usd_fob"], f"trade {y}: the products add up to the US$ total")
    check(abs(sum(r[1] for r in rows) - per["total_brl"]) < 1, f"trade {y}: the products add up to the R$ total")
    check(len(rows) == per["products"], f"trade {y}: number of products")
    check(sum(1 for r in rows if len(r) > 4) == 50 and all(sum(d[1] for d in r[4]) <= 1.0001 for r in rows if len(r) > 4), f"trade {y}: destinations of the 50 largest")
    b = IM["periods"][y]
    check(b["exports_usd_fob"] == per["total_usd_fob"] and b["exports_usd_fob"] - b["imports_usd_fob"] == b["balance_usd_fob"], f"trade {y}: exports minus imports equal the balance")
    periods[y] = {"from": per["from"], "to": per["to"], "usd": per["total_usd_fob"], "brl": per["total_brl"], "products": per["products"],
                  "imports_usd": b["imports_usd_fob"], "balance_usd": b["balance_usd_fob"]}
# The state modal column: the state's total and its 5 largest products. "ND" (no state declared) stays out of the modal
# but is part of the check that the states add up to Brazil.
by_uf = {}
for y in YEARS:
    check(sum(s[y]["usd_fob"] for s in EU["states"]) == EP["periods"][y]["total_usd_fob"], f"trade {y}: the states (with ND) add up to Brazil")
for s in EU["states"]:
    if s["uf"] == "ND":
        continue
    by_uf[s["uf"]] = {}
    for y in YEARS:
        q = s[y]
        check(sum(t["usd_fob"] for t in q["top_products"]) <= q["usd_fob"], f"trade {y} {s['uf']}: top products fit inside the state")
        check(all(abs(t["usd_fob"] / q["usd_fob"] - t["share_of_state"]) < 1e-4 for t in q["top_products"]), f"trade {y} {s['uf']}: shares of the state")
        by_uf[s["uf"]][y] = {"usd": q["usd_fob"], "brl": q["brl"], "share": q["share_of_brazil"],
                             "top": [[t["sh4"], t["name"], t["usd_fob"], t["share_of_state"], t["share_of_brazil_product"]] for t in q["top_products"]]}
check(len(by_uf) == 27, "trade: 27 states")
# D111: how much of the national output goes abroad, attached to the product line(s) it measures.
SHARE_SH4 = {"soy_grain": ["1201"], "soy_meal": ["2304"], "soy_oil": ["1507"], "corn": ["1005"], "cotton": ["5201"], "coffee": ["0901"],
             "sugar": ["1701"], "beef": ["0201", "0202"], "pork": ["0203"], "chicken": ["0207"], "banana": ["0803"], "orange_juice": ["2009"],
             "iron_ore": ["2601"], "crude_oil": ["2709"], "cellulose": ["4703"], "brazil_nut": ["0801"]}
import re
# A source line "Body, document, URL": the name without the URL, and a link a reader can open (the Comex Stat API answers
# only POST, so its documentation page stands in; IBGE lines name their SIDRA table).
def src(s):
    m = re.search(r"https?://[^\s),;]+", s)
    url = m.group(0).rstrip(":.") if m else None
    if url and url.endswith("api-comexstat.mdic.gov.br/general"):
        url = EP["source"]["docs"]
    if not url:
        m = re.search(r"SIDRA tabela (\d+)", s)
        url = f"https://sidra.ibge.gov.br/tabela/{m.group(1)}" if m else None
    return [re.sub(r"\s*\(API https?://[^)]*\)", "", s.split(", http")[0]).strip(), url]
share, share_none = {}, []
codes = {p["sh4"] for p in products}
for it in SH["items"]:
    out = it["share_exported"]
    check(out is None or 0 < out < 1, f"share {it['key']}: between 0 and 1")
    if out is not None and not it.get("share_is_lower_bound"):
        check(abs(float(it["exports"]["value"]) / float(it["production"]["value"]) - out) < 0.002, f"share {it['key']}: exports over production")
    pr_, ex_ = it["production"], it["exports"]
    row = {"name": it["name"], "out": out, "lower": bool(it.get("share_is_lower_bound")), "note": it.get("note"),
           "prod": [pr_["value"], pr_["unit"], pr_["period"]] + src(pr_["source"]), "exp": [ex_["value"], ex_["unit"], ex_["period"]] + src(ex_["source"])}
    if it["key"] in SHARE_SH4:
        for c in SHARE_SH4[it["key"]]:
            check(c in codes, f"share {it['key']}: product {c} exists")
            share.setdefault(c, []).append(row)
    else:
        share_none.append(row)
# D109: Brazil's export price against the World Bank reference, 2025 (the last year of the comparison).
prices = {}
for p in PR["products"]:
    bz = next(x for x in p["brazil"] if x["year"] == 2025)
    q = next(x for x in EP["products"] if x["sh4"] == p["sh4"])["2025"]
    check(bz["usd_fob"] == q["usd_fob"] and bz["kg"] == q["kg"], f"prices {p['sh4']}: 2025 equals the product file")
    prices[p["sh4"]] = {"unit": p["unit"], "bz": bz["unit_value"], "comp": p["comparability"],
                        "refs": [[r["series"], r["unit"], r["values"]["2025"], r["brazil_over_reference"]["2025"]] for r in (p.get("references") or [])]}
vaf = {y["year"]: y for y in CX["value_added_factor"]["years"]}
for yr in (2000, 2025):
    check(sum(g["usd_fob"] for g in vaf[yr]["groups"]) == vaf[yr]["total_usd_fob"], f"context {yr}: the value-added groups add up")
check(vaf[2025]["total_usd_fob"] == EP["periods"]["2025"]["total_usd_fob"], "context 2025: the same total as the products")
gdp = next(y for y in CX["gdp_share"]["years"] if y["year"] == 2025)
basic = lambda yr: next(g["share"] for g in vaf[yr]["groups"] if g["key"] == "basic")
data["trade"] = {
    "source": {"name": EP["source"]["name"], "docs": EP["source"]["docs"], "updated": EP["source"]["updated"], "fx": EP["source"]["fx"],
               "uf_rule": EU["source"]["uf_rule"], "prices": PR["source"]["reference"], "gdp": CX["gdp_share"]["source"], "gdp_url": CX["gdp_share"]["url"],
               "vaf_note": CX["value_added_factor"]["note"], "vaf_url": CX["value_added_factor"]["urls"][0]},
    "periods": periods, "products": products, "by_uf": by_uf, "share": share, "share_none": share_none, "prices": prices,
    "context": {"gdp_year": 2025, "exports_gdp": gdp["exports_share_of_gdp"], "imports_gdp": gdp["imports_share_of_gdp"],
                "basic": {"2000": basic(2000), "2025": basic(2025)}},
}
# Who held office in each period (round 11): one JSON per office in data/politicians/.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from politicians_view import build as build_politicians
POL = DATA / "politicians"
data["politicians_view"] = build_politicians(need(POL, "the scripts in pipelines/politicians/"))
if data["politicians_view"] and data["home"].get("recent"):
    import unicodedata
    key = lambda s: "".join(c for c in unicodedata.normalize("NFD", s.lower()) if c.isalpha())
    union = json.loads((POL / "union.json").read_text(encoding="utf-8"))
    face = {}
    for pid, p in union["people"].items():
        for k in (p.get("name"), p.get("full_name")):
            if k:
                face[key(k)] = next((x["photo"] for lst in data["politicians_view"]["union"].values() for x in lst if x["name"] == p["name"] and x["photo"]), None)
    for it in (data["home"].get("moves") or data["home"]["recent"])["items"]:  # every money move card gets the signer's photo
        for s in it.get("signed_by", []):
            n = key(s["name"]); s["photo"] = face.get(n) or next((v for k, v in face.items() if v and (k in n or n in k)), None)
# D66: the DF map by Região Administrativa and its population (PDAD-A 2024).
geo_df = need(ASSETS / "geo-df.json", "docs/superpowers/tools/build-geo-df.cjs")
(ASSETS / "bi-geo-df.js").write_text("window.BI_GEO_DF = " + geo_df.read_text(encoding="utf-8") + ";\n", encoding="utf-8")
data["df_regions"] = read(DATA / "df" / "regions.json", "pipelines/df/build_regions.py")
for uf in ("sc", "rs"):
    state_geo = need(ASSETS / f"geo-{uf}.json", "docs/superpowers/tools/build-geo-state.cjs")
    (ASSETS / f"bi-geo-{uf}.js").write_text(f"window.BI_GEO_{uf.upper()} = " + state_geo.read_text(encoding="utf-8") + ";\n", encoding="utf-8")
(ASSETS / "bi-data.js").write_text("window.BI = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
(ASSETS / "bi-geo.js").write_text("window.BI_GEO = " + json.dumps(geo, ensure_ascii=False) + ";\n", encoding="utf-8")
print("bi-data.js", round((ASSETS / "bi-data.js").stat().st_size / 1024), "KB · bi-geo.js", round((ASSETS / "bi-geo.js").stat().st_size / 1024), "KB ·",
      len(icons), "icons ·", len(flag_data), "flags")
