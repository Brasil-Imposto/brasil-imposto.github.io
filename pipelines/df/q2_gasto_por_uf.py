"""Pergunta 2: gasto direto da União por UF do localizador (Portal da Transparência, Execução da Despesa).
Entrada: data/df/cache/despuf_YYYYMM.json (gerados por agg_desp_uf.py).
Uso: q2_gasto_por_uf.py <base> <ano>
Definição (a mesma de BRASIL-IMPOSTO_RESEARCH_dados-por-uf_2026-09-25.md, seção 3.3): valor pago + restos a pagar pagos,
modalidades 90 e 91 (aplicação direta), grupos 1 (pessoal), 3 (outras despesas correntes), 4 (investimentos) e
5 (inversões financeiras). Juros (2) e amortização (6) ficam fora. Saída: data/df/q2_gasto_por_uf_<ano>.json."""
import collections, glob, json, sys
BASE, YEAR = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(f"{BASE}/data/df/cache/despuf_{YEAR}??.json"))
months = [json.load(open(f))["month"] for f in files]
pop = json.load(open(f"{BASE}/data/series/population.json"))["uf"]
G = {"1": "pessoal", "3": "custeio_e_beneficios", "4": "investimento", "5": "inversoes"}
byuf = collections.defaultdict(lambda: collections.defaultdict(float))
df_org = collections.defaultdict(float); df_fun = collections.defaultdict(float)
noloc = collections.defaultdict(float); noloc_fun = collections.defaultdict(float)
names = {"orgao": {}, "funcao": {}, "localizador": {}}
total = 0.0; total_all_mod = collections.defaultdict(float)
for f in files:
    d = json.load(open(f))
    for k in names: names[k].update(d["names"][k])
    for uf, loc, g, mo, org, fun, p, rp, liq in d["agg"]:
        v = p + rp
        if g not in G: continue
        total_all_mod[mo[:1] if mo not in ("90", "91") else mo] += v
        if mo not in ("90", "91"): continue
        total += v
        if uf and uf != "-1":
            byuf[uf][G[g]] += v
            if uf == "DF":
                df_org[org] += v; df_fun[fun] += v
                if org == "73000": byuf["DF"]["orgao_73000"] += v
        else:
            noloc[loc] += v; noloc_fun[fun] += v
loc_tot = sum(sum(v for k, v in x.items() if k in G.values()) for x in byuf.values())
print(f"{YEAR}: meses {months[0]} a {months[-1]} ({len(months)}). Gasto direto primário: R$ {total/1e9:.2f} bi; com UF {loc_tot/1e9:.2f} bi ({loc_tot/total*100:.1f}%); sem UF {(total-loc_tot)/1e9:.2f} bi ({(total-loc_tot)/total*100:.1f}%)")
print("sem UF por código de localizador (exemplo de nome):", [(k, names["localizador"].get(k, "")[-25:], round(v / 1e9, 2)) for k, v in sorted(noloc.items(), key=lambda t: -t[1])[:8]])
print("sem UF por função:", [(names["funcao"].get(k, k), round(v / 1e9, 2)) for k, v in sorted(noloc_fun.items(), key=lambda t: -t[1])[:10]])
py = YEAR if pop["DF"]["population"].get(YEAR) else "2024"
rows = []
for uf, x in byuf.items():
    if uf not in pop: print("UF desconhecida", uf, dict(x)); continue
    t = sum(v for k, v in x.items() if k in G.values()); P = pop[uf]["population"][py]
    rows.append((t / P, uf, t, x["pessoal"], x["custeio_e_beneficios"], x["investimento"], x["inversoes"], P))
rows.sort(reverse=True)
print(f"por UF (população IBGE {py}), R$ bi e R$ por pessoa:")
for i, (pc, uf, t, pe, cu, inv, ifi, P) in enumerate(rows, 1):
    print(f"{i:2d} {uf} total {t/1e9:7.2f} ({pc:7.0f}/hab)  pessoal {pe/1e9:6.2f} ({pe/P:6.0f})  custeio {cu/1e9:6.2f} ({cu/P:6.0f})  invest {inv/1e9:5.2f} ({inv/P:5.0f})  inversões {ifi/1e9:5.2f}")
dfx = byuf["DF"]; fc = dfx.get("orgao_73000", 0.0)
dft = sum(v for k, v in dfx.items() if k in G.values()); P = pop["DF"]["population"][py]
rest = [r for r in rows if r[1] != "DF"]; rt = sum(r[2] for r in rest); rp_ = sum(r[7] for r in rest)
print(f"DF: total {dft/1e9:.2f} bi ({dft/P:.0f}/hab); dos quais órgão 73000 (FCDF e outras transferências registradas como aplicação direta) {fc/1e9:.2f} bi; sem ele {(dft-fc)/1e9:.2f} bi ({(dft-fc)/P:.0f}/hab). Resto do país: {rt/rp_:.0f}/hab")
print("DF por órgão superior:", [(names["orgao"].get(k, k)[:45], round(v / 1e9, 2)) for k, v in sorted(df_org.items(), key=lambda t: -t[1])[:12]])
print("DF por função:", [(names["funcao"].get(k, k), round(v / 1e9, 2)) for k, v in sorted(df_fun.items(), key=lambda t: -t[1])[:10]])
json.dump({"year": YEAR, "months": months, "definition": __doc__.split("Definição")[1].strip(), "total_direct_primary": total,
           "located": loc_tot, "not_located": total - loc_tot, "not_located_by_localizador": noloc,
           "not_located_by_funcao": {names["funcao"].get(k, k): v for k, v in noloc_fun.items()},
           "by_uf": {r[1]: {"total": r[2], "pessoal": r[3], "custeio_e_beneficios": r[4], "investimento": r[5], "inversoes": r[6],
                             "population": r[7], "per_capita": r[0]} for r in rows},
           "df_orgao_73000": fc, "df_by_orgao": {names["orgao"].get(k, k): v for k, v in df_org.items()},
           "df_by_funcao": {names["funcao"].get(k, k): v for k, v in df_fun.items()}},
          open(f"{BASE}/data/df/q2_gasto_por_uf_{YEAR}.json", "w"), ensure_ascii=False, indent=1)
