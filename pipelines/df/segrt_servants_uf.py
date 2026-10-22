"""Servidores civis ativos do Poder Executivo federal (SIAPE) por UF do município da unidade de exercício (SEGRT/MGI).
Entrada: data/df/segrt_serv_por_mun_exerc_202608.csv
(https://repositorio.dados.gov.br/segrt/Serv_por_municipio/2026/Serv_por_mun_exerc_202608.csv).
Saída: data/df/segrt_servants_uf_202608.json e tabela por mil habitantes (população IBGE 2026)."""
import csv, json, sys
BASE = sys.argv[1] if len(sys.argv) > 1 else "."
f = f"{BASE}/data/df/segrt_serv_por_mun_exerc_202608.csv"
rows = list(csv.reader(open(f, encoding="utf-8-sig"), delimiter=";"))
agg, nomun = {}, 0
for r in rows[1:]:
    if not r: continue
    uf, n = r[0].strip(), int(r[2].replace(".", ""))
    agg[uf] = agg.get(uf, 0) + n
pop = json.load(open(f"{BASE}/data/series/population.json"))["uf"]
out = {"source": "https://repositorio.dados.gov.br/segrt/Serv_por_municipio/2026/Serv_por_mun_exerc_202608.csv",
       "month": "2026-08", "population_year": "2026", "by_uf": agg}
json.dump(out, open(f"{BASE}/data/df/segrt_servants_uf_202608.json", "w"), ensure_ascii=False, indent=1)
tot = sum(agg.values()); print("total", tot, "linhas", len(rows) - 1, "UFs/códigos", sorted(agg))
rk = sorted(((v / pop[u]["population"]["2026"] * 1000, u, v) for u, v in agg.items() if u in pop), reverse=True)
for i, (d, u, v) in enumerate(rk, 1):
    print(f"{i:2d} {u} {v:7d} servidores  {d:5.1f} por mil hab  ({v/tot*100:4.1f}% do total)")
print("sem UF válida:", {u: v for u, v in agg.items() if u not in pop})
