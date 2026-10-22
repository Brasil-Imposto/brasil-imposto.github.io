"""Vínculos públicos por UF e nível federativo (Atlas do Estado Brasileiro, Ipea, série 91, a partir da RAIS).
Entrada: data/df/atlas_091.xlsx (https://www.ipea.gov.br/atlasestado/arquivos/downloads/9113-091arquivounico.xlsx).
Saída: data/df/atlas_public_jobs_by_uf.json e tabela por mil habitantes (população do IBGE em data/series/population.json)."""
import json, sys, openpyxl
BASE = sys.argv[1] if len(sys.argv) > 1 else "."
wb = openpyxl.load_workbook(f"{BASE}/data/df/atlas_091.xlsx", read_only=True)
ws = wb["Uf"]
rows = list(ws.iter_rows(values_only=True)); h = rows[0]
years = sorted({r[0] for r in rows[1:] if r[0]})
out = {}
for r in rows[1:]:
    if not r[0]: continue
    d = dict(zip(h, r)); y = str(d["ano"]); uf = d["uf"]
    rec = {lvl: sum((d.get(f"total_nivel_{n}_{lvl}") or 0) for n in range(1, 6)) for lvl in ("federal", "estadual", "municipal")}
    for pod in ("executivo", "legislativo", "judiciario"):
        for lvl in ("federal", "estadual", "municipal"):
            rec[f"{pod}_{lvl}"] = sum((d.get(f"vinculos_{pod}_{lvl}_nivel_{n}") or 0) for n in range(1, 6))
    out.setdefault(y, {})[uf] = rec
json.dump({"source": "https://www.ipea.gov.br/atlasestado/consulta/91", "file": "9113-091arquivounico.xlsx, aba Uf",
           "years": years, "data": out}, open(f"{BASE}/data/df/atlas_public_jobs_by_uf.json", "w"), ensure_ascii=False, indent=1)
print("anos", years[0], "a", years[-1])
pop = json.load(open(f"{BASE}/data/series/population.json"))["uf"]
for y in [str(years[-1]), "2019"]:
    py = y if pop["DF"]["population"].get(y) else None
    if not py: print(y, "sem população do IBGE no arquivo local"); continue
    rows2 = []
    for uf, rec in out[y].items():
        if uf not in pop:
            print(y, "linha sem UF válida:", uf, rec["federal"], rec["estadual"], rec["municipal"]); continue
        p = pop[uf]["population"][py]; tot = rec["federal"] + rec["estadual"] + rec["municipal"]
        rows2.append((tot / p * 1000, uf, rec["federal"] / p * 1000, rec["estadual"] / p * 1000, rec["municipal"] / p * 1000, tot, rec["federal"]))
    rows2.sort(reverse=True)
    print(f"--- {y}: vínculos públicos por mil habitantes (população IBGE {py})")
    for i, (t, uf, f, e, m, tot, fed) in enumerate(rows2, 1):
        print(f"{i:2d} {uf} total {t:6.1f}  federal {f:5.1f}  estadual {e:5.1f}  municipal {m:5.1f}   vínculos {tot:9d}  federais {fed:7d}")
