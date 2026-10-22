"""Print the markdown tables of docs/research/BRASIL-IMPOSTO_RESEARCH_series-federais_2026-09-30.md from the series JSONs.

Usage: report_tables.py   (reads data/series/*.json and the 2024 JSONs; no network)
"""
import json
from pathlib import Path
D = (Path(__file__).resolve().parents[2] / "data")
U = json.load(open(D / "series" / "federal-by-uf-monthly.json"))
S = json.load(open(D / "series" / "sc-municipal-federal.json"))
R24 = {x["uf"]: x for x in json.load(open(D / "uf-balance-2024.json"))}
M = U["months"]; N = U["national"]
def br(x, d=2): return f"{(0.0 if round(x, d) == 0 else x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
def idx(y): return [i for i, m in enumerate(M) if m.startswith(str(y))]
def total(key, y, sub=None):
    s = 0.0
    for o in U["uf"].values():
        arr = o[key] if sub is None else o[key][sub]
        s += sum(arr[i] for i in idx(y) if arr[i] is not None)
    return s

print("### Arrecadação: soma das UFs x total nacional (R$ bi)\n")
print("| Ano | Meses | Soma das 27 UFs | Total nacional (Receita) | Diferença | Diferença % |\n|---|---:|---:|---:|---:|---:|")
for y in range(2019, 2027):
    ii = [i for i in idx(y) if N["federal_revenue_sum_of_ufs"][i] is not None]
    s = sum(N["federal_revenue_sum_of_ufs"][i] for i in ii); t = sum(N["federal_revenue_total_receita"][i] for i in ii)
    print(f"| {y} | {len(ii)} | {br(s/1e9)} | {br(t/1e9)} | {br((s-t)/1e9)} | {br(100*(s/t-1),3)} |")

print("\n### Status mensal da arrecadação por UF (meses fora de 'ok')\n")
print("| Mês | Status | Participação do DF | Soma das UFs (R$ bi) | Total nacional (R$ bi) | Sem UF (R$ bi) |\n|---|---|---:|---:|---:|---:|")
for i, m in enumerate(M):
    st = N["federal_revenue_month_status"][i]
    if st != "ok" or ("2024-12" <= m <= "2026-07"):
        s, t, g, df = N["federal_revenue_sum_of_ufs"][i], N["federal_revenue_total_receita"][i], N["federal_revenue_not_attributed_to_any_uf"][i], N["federal_revenue_df_share_pct"][i]
        print(f"| {m} | {st} | {br(df,1)+'%' if df is not None else 'n/d'} | {br(s/1e9,1) if s else 'n/d'} | {br(t/1e9,1) if t else 'n/d'} | {br(g/1e9,1) if g is not None else 'n/d'} |")

print("\n### 2024: série mensal x data/uf-balance-2024.json\n")
wr = wt = 0
for uf, o in U["uf"].items():
    r = sum(o["federal_revenue"]["total"][i] for i in idx(2024)); t = sum(o["transfers"]["total"][i] for i in idx(2024))
    wr = max(wr, abs(r / R24[uf]["federal_revenue"]["total"] - 1) * 100); wt = max(wt, abs(t / R24[uf]["transfers"]["total"] - 1) * 100)
print(f"Maior diferença por UF: arrecadação {br(wr,4)}%, transferências {br(wt,4)}%.")

print("\n### Totais anuais das 27 UFs (R$ bi)\n")
print("| Ano | Arrecadação | Transferências | ao governo estadual | aos municípios | Bolsa Família / Auxílio Brasil | INSS (RGPS, BEPS t19) | INSS bruto (BEPS t18) | BPC (MI Social) | INSS AEPS (com BPC) | Transferências sem UF |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
def nmonths(key, y, sub=None):
    o = next(iter(U["uf"].values())); arr = o[key] if sub is None else o[key][sub]
    return sum(1 for i in idx(y) if arr[i] is not None)
def cell(key, y, sub=None):
    n = nmonths(key, y, sub)
    if n == 0: return "n/d"
    v = br(total(key, y, sub) / 1e9)
    return v if n == 12 else f"{v} ({n} meses)"
for y in range(2019, 2027):
    nm = lambda k, s=None: total(k, y, s)
    aeps = sum((o["inss_annual_aeps"].get(str(y)) or 0) for o in U["uf"].values())
    nouf = sum(v for i, v in enumerate(N["transfers_public_recipients_without_uf"]["total"]) if M[i].startswith(str(y)) and v is not None)
    lc = sum(sum(o["transfers"]["by_category"]["lc176_kandir_compensation"][i] or 0 for i in idx(y)) for o in U["uf"].values())
    g = "inss_gross_benefit_value" in next(iter(U["uf"].values()))
    tn = sum(1 for i in idx(y) if N["transfers_public_recipients_without_uf"]["total"][i] is not None)
    print(f"| {y} | {cell('federal_revenue', y, 'total')} | {cell('transfers', y, 'total')} | {cell('transfers', y, 'to_state_government')} | {cell('transfers', y, 'to_municipalities')} | {cell('bolsa_familia', y)} | {cell('inss', y)} | {cell('inss_gross_benefit_value', y) if g else 'n/d'} | {cell('bpc', y)} | {br(aeps/1e9) if aeps else 'n/d'} | {(br(nouf/1e9) + ('' if tn == 12 else f' ({tn} meses)')) if tn else 'n/d'} |")

print("\n### Transferências a governos registradas sem UF, por ação (R$ bi)\n")
print("| Ação | " + " | ".join(str(y) for y in range(2019, 2027)) + " |\n|---|" + "---:|" * 8)
for a, arr in N["transfers_public_recipients_without_uf"]["by_action"].items():
    print(f"| {a[:70]} | " + " | ".join((br(sum(arr[i] or 0 for i in idx(y)) / 1e9) if any(arr[i] is not None for i in idx(y)) else "n/d") for y in range(2019, 2027)) + " |")

print("\n### SC: soma dos 295 municípios por ano (R$ bi)\n")
SM = S["months"]
print("| Ano | Arrecadação federal registrada nos municípios | Transferências às prefeituras | Bolsa Família / Auxílio Brasil | BPC |\n|---|---:|---:|---:|---:|")
for y in range(2019, 2027):
    ii = [i for i, m in enumerate(SM) if m.startswith(str(y))]
    def s(k):
        first = next(iter(S["municipalities"].values()))
        n = sum(1 for i in ii if first[k][i] is not None)
        vals = [m[k][i] for m in S["municipalities"].values() for i in ii if m[k][i] is not None]
        return "n/d" if not n else br(sum(vals) / 1e9) + ("" if n == 12 else f" ({n} meses)")
    rv = sum((m["federal_revenue_annual"].get(str(y)) or 0) for m in S["municipalities"].values())
    print(f"| {y} | {br(rv/1e9) if rv else 'n/d'} | {s('transfers_monthly')} | {s('bolsa_familia_monthly')} | {s('bpc_monthly')} |")
