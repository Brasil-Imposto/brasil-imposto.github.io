"""Federal balance of each municipality of one state (default Santa Catarina), 2024: the same rule as the state map,
one level down -> data/{uf}-municipal-balance-2024.json

balance = federal revenue collected in the municipality (Receita Federal, arrecadação por município, DARF + GPS)
          minus (federal transfers to the municipal government, Portal da Transparência, + Bolsa Família paid there, MDS).
INSS benefits and the federal payroll have no open per-municipality source without a dados.gov.br login, so they
are NOT in this balance (they are in the state balance); the preview says so on screen.
Inputs: the small downloads of ./download.sh <workdir> <UF> (names, population, Receita file, Bolsa Família) and the 12
monthly Portal caches of 2024 written by pipelines/series/agg_transfers_monthly.py --ufs <UF> (one raw file at a time);
run from any folder:
    python3 pipelines/municipios/build_municipal_balance.py <workdir> [--uf RS] [--transfers DIR] [--out PATH]
                                                               [--collected-at YYYY-MM-DD]
  --transfers: folder with transf_2024MM.json (default <workdir>/cache)
Needs openpyxl (a local venv is enough).
"""
import collections, csv, glob, json, sys
from datetime import date
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipelines" / "series"))
from classify_transfers import municipal_government
from municipality_names import matcher


def take(argv, name, default=None):
    if name in argv:
        i = argv.index(name); value = argv[i + 1]; del argv[i:i + 2]; return value
    return default


ARGS = sys.argv[1:]
UF = take(ARGS, "--uf", "SC").upper()
TRANSFERS = take(ARGS, "--transfers")
OUT_ARG = take(ARGS, "--out")
COLLECTED = take(ARGS, "--collected-at") or date.today().isoformat()
W = Path(ARGS[0])
TRANSFERS = Path(TRANSFERS) if TRANSFERS else W / "cache"
OUT = Path(OUT_ARG) if OUT_ARG else ROOT / "data" / f"{UF.lower()}-municipal-balance-2024.json"
CACHE = ROOT / "pipelines" / "siconfi" / "cache" / "municipal-rreo03-2024.jsonl"
IBGE_UF = {"SC": "42", "RS": "43"}[UF]
uf = UF.lower()

names = {str(m["id"]): m["nome"] for m in json.load(open(W / f"mun-{uf}.json"))}
code_of = matcher(UF, names)

# population 2024 (IBGE estimates, SIDRA 6579)
pop = {}
for res in json.load(open(W / f"pop-{uf}.json"))[0]["resultados"]:
    for s in res["series"]:
        pop[s["localidade"]["id"]] = int(s["serie"]["2024"])

# federal revenue by municipality (sheet TOTAL = DARF + GPS)
rev, rev_unmatched = {}, []
ws = openpyxl.load_workbook(W / "rfb-mun-2024.xlsx", read_only=True)["TOTAL"]
for row in ws.iter_rows(min_row=7, values_only=True):
    if not row or row[1] != UF or row[2] is None:
        continue
    c = code_of(row[0])
    if c: rev[c] = rev.get(c, 0.0) + float(row[2])
    else: rev_unmatched.append(row[0])

# federal transfers to the municipal government (same recipient rule as the state build, restricted to municipalities)
tr, tr_unmatched, tr_other = collections.defaultdict(float), collections.defaultdict(float), 0.0
caches = sorted(glob.glob(str(TRANSFERS / "transf_2024??.json")))
if len(caches) != 12:
    raise SystemExit(f"{len(caches)} of the 12 monthly Portal caches of 2024 in {TRANSFERS}; run agg_transfers_monthly.py first")
for f in caches:
    for mun, fav, modal, v in json.load(open(f))["by_uf"][UF]:
        if not municipal_government(fav, modal):
            tr_other += v; continue
        c = code_of(mun)
        if c: tr[c] += v
        else: tr_unmatched[mun] += v

# Bolsa Família paid in each municipality (MDS MI Social, 6-digit IBGE code)
bf = collections.defaultdict(float)
six = {c[:6]: c for c in names}
for row in csv.DictReader(open(W / f"bf-{uf}.csv", encoding="utf-8")):
    if row["valor_repassado_bolsa_familia_f"]:
        bf[six[row["codigo_ibge"]]] += float(row["valor_repassado_bolsa_familia_f"])

# municipal taxes (SICONFI, from the all-municipality collection)
mt = {}
for line in open(CACHE, encoding="utf-8"):
    rec = json.loads(line)
    if rec["uf"] == UF and rec["status"] == "ok":
        mt[str(rec["id"])] = {k: rec.get(k) or 0.0 for k in ("iss", "iptu", "itbi", "irrf", "other_taxes_fees")}

rows = []
for c, n in sorted(names.items()):
    sent, t, b = rev.get(c), tr.get(c, 0.0), bf.get(c, 0.0)
    received = t + b
    rows.append({"code": c, "name": n, "population": pop.get(c), "federal_revenue": round(sent, 2) if sent is not None else None,
                 "federal_transfers": round(t, 2), "bolsa_familia": round(b, 2), "received": round(received, 2),
                 "balance": round(sent - received, 2) if sent is not None else None,
                 "balance_per_capita": round((sent - received) / pop[c], 2) if sent is not None and pop.get(c) else None,
                 "returned_per_real": round(received / sent, 4) if sent else None,
                 "municipal_taxes": mt.get(c)})
checks = {
    "municipalities": len(rows), "with_revenue": sum(r["federal_revenue"] is not None for r in rows),
    "with_transfers": sum(r["federal_transfers"] > 0 for r in rows), "with_bolsa_familia": sum(r["bolsa_familia"] > 0 for r in rows),
    "with_population": sum(r["population"] is not None for r in rows), "with_municipal_taxes": sum(r["municipal_taxes"] is not None for r in rows),
    "revenue_unmatched_names": rev_unmatched, "transfers_unmatched": {k: round(v, 2) for k, v in tr_unmatched.items()},
    "sum_federal_revenue": round(sum(r["federal_revenue"] or 0 for r in rows), 2), "sum_transfers": round(sum(tr.values()), 2),
    "transfers_to_state_government_and_others_excluded": round(tr_other, 2), "sum_bolsa_familia": round(sum(bf.values()), 2),
}
OUT.write_text(json.dumps({
    "year": 2024, "uf": UF,
    "definition": "saldo com a União do município: arrecadação federal registrada no município menos (transferências federais à prefeitura + Bolsa Família)",
    "not_included": "benefícios do INSS e folha federal (sem dado aberto por município sem login no dados.gov.br); transferências ao governo estadual",
    "sources": {
        "federal_revenue": "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/copy_of_arrecadacao-das-receitas-administradas-pela-rfb-por-municipio/arrecadacao-das-receitas-administradas-pela-rfb/arrecadacao-da-receita-administrada-pela-rfb-por-municipio-2024.xlsx",
        "federal_transfers": "https://portaldatransparencia.gov.br/download-de-dados/transferencias/2024MM",
        "bolsa_familia": f"https://aplicacoes.mds.gov.br/sagi/servicos/misocial (fq=sigla_uf:{UF}, anomes_s:2024*)",
        "population": f"https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024/variaveis/9324?localidades=N6[N3[{IBGE_UF}]]",
        "municipal_taxes": "SICONFI, RREO Anexo 03 de cada município (data/municipal-taxes-2024.json)",
    },
    "collected_at": COLLECTED, "checks": checks, "municipalities": rows,
}, ensure_ascii=False), encoding="utf-8")
print(json.dumps(checks, ensure_ascii=False, indent=1)[:1500])
