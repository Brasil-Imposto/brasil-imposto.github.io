"""DF by Região Administrativa (D66): population and income of each RA from the PDAD-A 2024 (IPEDF), official reports.

Usage: python3 pipelines/df/build_regions.py [--control]
Source: IPEDF, Pesquisa Distrital por Amostra de Domicílios Ampliada 2024, one report per RA (pdad.ipe.df.gov.br): the urban
population stated in the text and Tabela 49 (households by income band) as published. The average income is not computed
from the public microdata: on 2026-10-02 it did not reproduce the report's DF figures (R$ 4.277 against R$ 5.268,60).
Each PDF is downloaded to a temporary folder, read with pdftotext and deleted at once (nothing is kept on disk).
The two RAs created in July 2026 (Leis 7.917 and 7.918) did not exist in the survey: the PDAD counts them inside the RAs
they came from, so they get no numbers of their own.
Check: the RA populations add up to the DF population of the same survey (urban and rural); --control drops one RA and
must fail. Nothing is written when the check fails.
Output: data/df/regions.json (English keys).
"""
import json, os, re, subprocess, sys, tempfile, unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
CONTROL = "--control" in sys.argv
BASE = "https://pdad.ipe.df.gov.br"
TMP = tempfile.mkdtemp(prefix="bi-pdad-")
norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
num = lambda s: float(s.replace(".", "").replace(",", "."))

def fetch_text(path):
    pdf = os.path.join(TMP, "r.pdf")
    subprocess.run(["curl", "-sS", "-L", "-m", "300", "-A", "Mozilla/5.0", "-o", pdf, BASE + path], check=True)
    head = subprocess.run(["curl", "-sS", "-I", "-m", "60", "-A", "Mozilla/5.0", BASE + path], capture_output=True, text=True).stdout
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    os.remove(pdf)
    lm = re.search(r"(?im)^last-modified:\s*(.+)$", head)
    return " ".join(txt.split()), (lm.group(1).strip() if lm else None)

POP = re.compile(r"população (?:urbana e rural |urbana |rural )?d[aoe]s? .{1,80}? era de ([\d.]+) pes-? ?soas", re.I)  # line breaks hyphenate "pes- soas"
INC = re.compile(r"renda domiciliar\d* estimada foi de R\$ ([\d.,]+) ?, que resulta em um valor médio por pessoa de R\$ ([\d.,]+)", re.I)
BANDS = ["Até 1", "Mais de 1 até 2", "Mais de 2 até 5", "Mais de 5 até 10", "Mais de 10 até 20", "Mais de 20"]
def income_bands(text):
    """Tabela 49 (Rendimento bruto domiciliar por faixas de salário mínimo): the % column as published; None where
    IPEDF suppressed the estimate (***) for an insufficient sample."""
    i = text.find("Rendimento bruto domiciliar por faixas de salário mínimo")
    seg = text[i:i + 900] if i >= 0 else ""
    out = {}
    for b in BANDS:
        m = re.search(re.escape(b) + r" (\(\*\*\*\)|[\d.]+) (\(\*\*\*\)|[\d,]+)", seg)
        out[b] = None if not m or "*" in m.group(2) else float(m.group(2).replace(",", "."))
    return out if i >= 0 else None

reports = json.loads(subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0", BASE + "/api/upts_reports/"], capture_output=True, text=True).stdout or "null") or None
if not reports:  # the list the site itself reads; kept here so the script does not depend on a guessed endpoint
    reports = json.load(open(P("data/df/pdad-2024-reports.json")))
groups = {g["name"]: g["ras"] for g in reports["presentations"]}
geo = json.load(open(P("docs/superpowers/previews/assets/geo-df.json")))
by_name = {norm(m["name"]): m for m in geo["municipalities"]}
ALIAS = {"solnascenteepordosol": "solnascentepordosol"}

df_text, df_lm = fetch_text(groups["Informações Gerais"][0]["report"])
df_pop = num(POP.search(df_text).group(1))
df_inc = INC.search(df_text)
rural_text, _ = fetch_text(groups["Informações Gerais"][1]["report"])
rural_pop = num(POP.search(rural_text).group(1))
regions, unmatched = {}, []
for ra in groups["Regiões Administrativas"]:
    label = re.sub(r"^[IVXL]+ - ", "", ra["name"]).strip()
    key = ALIAS.get(norm(label), norm(label))
    m = by_name.get(key) or next((v for k, v in by_name.items() if key in k or k in key), None)
    if not m: unmatched.append(label); continue
    text, lm = fetch_text(ra["report"])
    pm = POP.search(text); im = INC.search(text)
    regions[m["code"]] = {"name": m["name"], "number": m["number"], "pdad_report": BASE + ra["report"], "file_last_modified": lm,
                          "population": {"value": int(num(pm.group(1))) if pm else None, "year": 2024, "source": "IPEDF, PDAD-A 2024"},
                          "household_income_bands_pct": {"value": income_bands(text), "year": 2024, "unit": "% dos domicílios por faixa de salário mínimo (R$ 1.412,00, jul/2024)",
                                                         "source": "IPEDF, PDAD-A 2024, Tabela 49 do relatório da RA"}}
for m in geo["municipalities"]:
    if m["code"] not in regions:
        regions[m["code"]] = {"name": m["name"], "number": m["number"], "population": {"value": None}, "household_income_bands_pct": {"value": None},
                              "why_no_data": "RA criada em julho de 2026; a PDAD-A 2024 conta este território dentro da RA de onde ele saiu."}
if CONTROL:
    regions.pop(next(c for c, r in regions.items() if r["population"]["value"]))
pop_sum = sum(r["population"]["value"] or 0 for r in regions.values()) + rural_pop
diff = pop_sum - df_pop
check = {"ra_urban_population_plus_rural": pop_sum, "rural_population": rural_pop, "df_population_pdad": df_pop, "difference": diff, "difference_pct": round(diff / df_pop * 100, 3),
         "ras_without_population": [r["name"] for r in regions.values() if r["population"]["value"] is None],
         "unmatched_report_names": unmatched, "passed": abs(diff) / df_pop < 0.005 and not unmatched, "control_run": CONTROL}
print(json.dumps(check, ensure_ascii=False, indent=1))
os.rmdir(TMP)
if not check["passed"]:
    raise SystemExit("CHECK FAILED")
if not CONTROL:
    json.dump({"collected_on": "2026-10-02", "law": "37 RAs: Leis distritais nº 7.917 e 7.918, de 03/07/2026, criaram Ponte Alta (RA XXXVII) e 26 de Setembro (RA XXXVI)",
               "survey": {"name": "PDAD-A 2024 (Pesquisa Distrital por Amostra de Domicílios Ampliada)", "body": "IPEDF Codeplan", "url": BASE,
                          "df_population": df_pop, "df_rural_population": rural_pop, "df_household_income": num(df_inc.group(1)) if df_inc else None,
                          "df_income_per_person": num(df_inc.group(2)) if df_inc else None, "df_report_last_modified": df_lm},
               "regions": regions, "check": check,
               "union_balance_by_region": {"available": False, "reason": "A arrecadação federal, os repasses, o Bolsa Família e o BPC por município existem para o DF só como um todo (Brasília); nenhuma fonte federal aberta os divide por Região Administrativa."}},
              open(P("data/df/regions.json"), "w"), ensure_ascii=False, indent=1)
