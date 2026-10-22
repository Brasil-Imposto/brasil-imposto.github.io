"""Arrecadação federal por UF (Receita), 2024: composição do DF por coluna do arquivo, participação no país e por pessoa.
Entrada: data/df/arrecadacao-estado.csv (https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv).
Saída: data/df/rfb_breakdown_2024.json e tabela na tela."""
import csv, json, re, sys
BASE = sys.argv[1] if len(sys.argv) > 1 else "."
YEAR = sys.argv[2] if len(sys.argv) > 2 else "2024"
rows = list(csv.reader(open(f"{BASE}/data/df/arrecadacao-estado.csv", encoding="latin1"), delimiter=";"))
h = rows[0]


def f(x):
    x = x.strip()
    if not x: return 0.0
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", x): x = x.replace(".", "")
    return float(x.replace(",", "."))


agg = {}
for r in rows[1:]:
    if r[0] != YEAR: continue
    d = agg.setdefault(r[2], {c: 0.0 for c in h[3:]})
    for c, x in zip(h[3:], r[3:]): d[c] += f(x)
pop = json.load(open(f"{BASE}/data/series/population.json"))["uf"]
P = {uf: pop[uf]["population"][YEAR] for uf in agg}
cols = [c for c in h[3:] if sum(agg[u][c] for u in agg) != 0]
nat = {c: sum(agg[u][c] for u in agg) for c in cols}
out = {"year": YEAR, "source": "https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv", "unit": "BRL",
       "population_source": "data/series/population.json (IBGE)", "uf": {u: {"population": P[u], "by_column": agg[u], "total": sum(agg[u].values())} for u in agg},
       "national": nat}
json.dump(out, open(f"{BASE}/data/df/rfb_breakdown_{YEAR}.json", "w"), ensure_ascii=False, indent=1)
popBR = sum(P.values())
print(f"DF pop share {P['DF']/popBR*100:.2f}%  total DF {sum(agg['DF'].values())/1e9:.2f} bi")
print(f"{'coluna':70s} {'DF R$ bi':>9s} {'BR R$ bi':>9s} {'DF %BR':>7s} {'DF R$/hab':>10s} {'BR exDF R$/hab':>14s}")
for c in cols:
    df = agg["DF"][c]; br = nat[c]
    exdf = (br - df) / (popBR - P["DF"])
    print(f"{c[:70]:70s} {df/1e9:9.2f} {br/1e9:9.2f} {df/br*100 if br else 0:7.1f} {df/P['DF']:10.0f} {exdf:14.0f}")
