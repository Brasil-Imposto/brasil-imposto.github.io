"""Arrecadação federal por natureza jurídica do contribuinte (Receita), nacional, por ano.
Entrada: data/df/arrecadacao-natureza.csv (https://www.gov.br/receitafederal/dados/arrecadacao-natureza.csv).
Saída: data/df/rfb_natureza_<ano>.json e tabela na tela (R$ bi)."""
import csv, json, re, sys
BASE = sys.argv[1] if len(sys.argv) > 1 else "."
YEAR = sys.argv[2] if len(sys.argv) > 2 else "2024"
rows = list(csv.reader(open(f"{BASE}/data/df/arrecadacao-natureza.csv", encoding="latin1"), delimiter=";"))
h = rows[0]
cols = [c for c in h[4:] if c]


def f(x):
    x = x.strip()
    if not x: return 0.0
    return float(x.replace(".", "").replace(",", "."))


agg, names, months = {}, {}, set()
for r in rows[1:]:
    if not r or r[0] != YEAR: continue
    months.add(r[1])
    d = agg.setdefault(r[2], {c: 0.0 for c in cols}); names[r[2]] = r[3]
    for c, x in zip(h[4:], r[4:]):
        if c: d[c] += f(x)
json.dump({"year": YEAR, "months": sorted(months), "source": "https://www.gov.br/receitafederal/dados/arrecadacao-natureza.csv",
           "unit": "BRL", "by_natureza": {k: {"name": names[k], **v, "total": sum(v.values())} for k, v in agg.items()}},
          open(f"{BASE}/data/df/rfb_natureza_{YEAR}.json", "w"), ensure_ascii=False, indent=1)
tot = {c: sum(v[c] for v in agg.values()) for c in cols}
print("meses", len(months), "total geral R$ bi %.2f" % (sum(tot.values()) / 1e9))
print("TOTAL", {c: round(tot[c] / 1e9, 2) for c in cols})
for k in sorted(agg, key=lambda k: -sum(agg[k].values()))[:40]:
    v = agg[k]
    print(f"{k} {names[k][:62]:62s} tot {sum(v.values())/1e9:8.2f} IRRF {v['IRRF']/1e9:7.2f} CPSSS {v['CPSSS']/1e9:6.2f} Prev {v['Contribuição Previdenciária']/1e9:7.2f} Pis {v['Pis/Pasep']/1e9:6.2f} Outras {v['Outras Receitas Administradas']/1e9:6.2f}")
