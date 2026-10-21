"""State governments, every bimester from 2019 to the latest published -> data/series/state-budgets.json

Reads the cache filled by fetch_state_series.py (run that first; it resumes). No network access here.
Per bimester (cumulative from January, as the RREO reports it):
  Anexo 01  receitas realizadas and despesas empenhadas, liquidadas e pagas (excluding intra-budget operations) and
            the annex's own surplus/deficit line (receitas realizadas menos despesas empenhadas);
  Anexo 02  spending by function, liquidated, cumulative (same format and rules as data/state-budgets-2024.json);
  Anexo 03  revenue lines, 12-month totals (same lines and labels as the 2024 file) plus monthly values per line;
  Anexo 06  resultado primario and nominal, the figure the annex reports, with the name of the line used.
RGF Anexo 02: Divida Consolidada and DCL at the end of each quadrimester.
Run: python3 data/scripts/series/build_state_series.py
"""
import json
from datetime import date
from pathlib import Path

from fetch_state_series import FIRST_YEAR, UF_CODES
from siconfi_client import API, CURRENT_YEAR, EntityCache
from siconfi_parse import parse_a01, parse_a02, parse_a03, parse_a06, parse_rgf02

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "series" / "state-budgets.json"
RREO_TYPES = ["RREO", "RREO Simplificado"]
REVENUE_LINES = {"ICMS": "ICMS", "IPVA": "IPVA", "ITCD": "ITCD (heranças e doações)", "IRRF": "Imposto de renda retido na fonte",
                 "Cota-Parte do FPE": "Fundo de Participação dos Estados (União)",
                 "Transferências do FUNDEB": "Fundeb", "Outras Transferências Correntes": "Outras transferências",
                 "Transferências da LC nº 61/1989": "IPI exportação (União)",
                 "Transferências da LC nº 87/1996": "Lei Kandir, compensação do ICMS (União)",
                 "Contribuições": "Contribuições (previdência dos servidores)", "Receita Patrimonial": "Receita patrimonial",
                 "Receita de Serviços": "Receita de serviços", "Outras Receitas Correntes": "Outras receitas correntes",
                 "Outros Impostos, Taxas e Contribuições de Melhoria": "Outros impostos e taxas",
                 # Only the DF reports these (Brasília has no prefeitura, so the GDF charges the city taxes and receives the
                 # city fund); without them the DF lost about R$ 6 bi a year. The two small lines close every state to the cent.
                 "ISS": "ISS", "IPTU": "IPTU", "ITBI": "ITBI", "Cota-Parte do FPM": "Fundo de Participação dos Municípios (União)",
                 "Cota-Parte do ITR": "Cota-parte do ITR (União)", "Receita Agropecuária": "Receita agropecuária",
                 "Receita Industrial": "Receita industrial",
                 # New tax line in the 2026 template. Minas Gerais filed its 2026 1st-bimester income-tax line under this name
                 # (R$ 8,29 bi in 12 months, the IRRF of the next report); kept as filed, the monthly series reads the last report.
                 "IBS": "IBS"}
BUDGET_RESULT_METHOD = ("Anexo 01, linha SUPERÁVIT ou DÉFICIT como enviada: total das receitas realizadas menos o total das despesas "
                        "executadas (liquidadas nos bimestres 1 a 5, empenhadas no 6º), com as intraorçamentárias. Só é usada quando "
                        "bate, até R$ 1, com os totais do próprio anexo (a base está em budget_result_basis)")


def budget_null(a01, period):
    """Reason for a null budget_result, with the annex's own numbers."""
    basis = "empenhadas" if period == 6 else "liquidadas"
    if a01["_budget_status"] == "missing":
        return f"o Anexo 01 enviado não preenche a linha SUPERÁVIT nem a linha DÉFICIT na coluna das despesas {basis}"
    return (f"a linha SUPERÁVIT/DÉFICIT enviada ({a01['_budget_filed']}) não bate com o próprio anexo: total das receitas "
            f"{a01['_total_revenue_incl_intra']} menos total das despesas {basis} {a01['_total_spending_basis_incl_intra']} = "
            f"{a01['_budget_expected']}; o valor enviado não é usado")


def rec(cache, year, period, tipo, anexo):
    r = cache.records.get(f"rreo|{year}|{period}|{tipo}|{anexo}")
    return r if r and r["status"] == "ok" else None


def any_type(cache, year, period, anexo, first):
    for tipo in [first] + [t for t in RREO_TYPES if t != first]:
        r = rec(cache, year, period, tipo, anexo)
        if r:
            return r, tipo
    return None, None


LINE_GAPS = []  # filled by build_period; main() refuses to write while it is not empty


def build_period(cache, year, period):
    a01, tipo = any_type(cache, year, period, "RREO-Anexo 01", "RREO")
    if a01 is None:
        return None
    out = {"report": tipo, "months_covered": [f"{year}-01", f"{year}-{2 * period:02d}"]}
    nulls = {}
    parsed = parse_a01(a01["rows"], period)
    out.update({k: v for k, v in parsed.items() if not k.startswith("_")})
    out["budget_result_method"] = BUDGET_RESULT_METHOD
    for k in ("revenue_total", "spending_committed", "spending_liquidated", "spending_paid"):
        if out[k] is None:
            nulls[k] = "linha não encontrada no Anexo 01 deste período"
    if out["budget_result"] is None:
        nulls["budget_result"] = budget_null(parsed, period)

    a06, _ = any_type(cache, year, period, "RREO-Anexo 06", tipo)
    if a06:
        out.update(parse_a06(a06["rows"]))
        for k in ("primary_result", "nominal_result"):
            if out[k] is None:
                nulls[k] = "o Anexo 06 deste período não traz linha de resultado " + ("primário" if k.startswith("p") else "nominal")
    else:
        out.update({"primary_result": None, "primary_result_method": None, "nominal_result": None,
                    "nominal_result_method": None, "results_reported": {}})
        nulls["primary_result"] = nulls["nominal_result"] = "Anexo 06 não encontrado no SICONFI (RREO e RREO Simplificado)"

    a02, _ = any_type(cache, year, period, "RREO-Anexo 02", tipo)
    if a02:
        functions, total = parse_a02(a02["rows"])
        out["spending_by_function"], out["spending_by_function_total"] = functions, total
    else:
        out["spending_by_function"], out["spending_by_function_total"] = [], None
        nulls["spending_by_function"] = "Anexo 02 não encontrado no SICONFI (RREO e RREO Simplificado)"

    a03, _ = any_type(cache, year, period, "RREO-Anexo 03", tipo)
    if a03:
        lines, window = parse_a03(a03["rows"], year, period)
        by_key = {ln["key"]: ln for ln in lines}
        rev = [{"key": k, "label": label, "value": by_key[k]["total_12m"]} for k, label in REVENUE_LINES.items()
               if k in by_key and by_key[k]["total_12m"]]
        out["revenue_lines"] = sorted(rev, key=lambda x: -x["value"])
        out["revenue_lines_window"] = list(window)
        get = lambda prefix: next((ln["total_12m"] for ln in lines if ln["key"].startswith(prefix)), None)
        out["revenue_current_total"] = get("RECEITAS CORRENTES (I)")
        out["rcl"] = get("RECEITA CORRENTE LÍQUIDA (III)")
        out["to_municipalities"] = get("Transferências Constitucionais e Legais")
        out["fundeb_deduction"] = get("Dedução de Receita para Formação do FUNDEB")
        gap = (out["revenue_current_total"] or 0) - sum(x["value"] for x in rev)
        if abs(gap) > 1:
            LINE_GAPS.append(f"{year}-B{period}: as linhas somam R$ {gap:,.2f} a menos que RECEITAS CORRENTES (I)")
    else:
        out["revenue_lines"], out["revenue_lines_window"] = [], None
        nulls["revenue_lines"] = "Anexo 03 não encontrado no SICONFI (RREO e RREO Simplificado)"
    out["nulls"] = nulls
    return out


def monthly(cache, periods_ok):
    """Each month comes from the last report of its own year (6th bimester for closed years)."""
    months, month_report, lines, labels = [], [], {}, {}
    for year in range(FIRST_YEAR, CURRENT_YEAR + 1):
        last = max((p for (y, p) in periods_ok if y == year), default=None)
        if last is None:
            continue
        a03, _ = any_type(cache, year, last, "RREO-Anexo 03", "RREO")
        if a03 is None:
            continue
        parsed, _ = parse_a03(a03["rows"], year, last)
        own = [f"{year}-{m:02d}" for m in range(1, 2 * last + 1)]
        base = len(months)
        months.extend(own)
        month_report.extend([f"{year}-B{last}"] * len(own))
        for ln in parsed:
            series = lines.setdefault(ln["key"], [None] * base)
            series.extend(ln["months"].get(mk) for mk in own)
            labels.setdefault(ln["key"], REVENUE_LINES.get(ln["key"], ln["key"]))
        for key, series in lines.items():  # a line absent from this year's report stays null for its months
            series.extend([None] * (len(months) - len(series)))
    return {"months": months, "month_report": month_report, "lines": lines, "labels": labels,
            "null_reason": "linha ausente do Anexo 03 daquele ano (o modelo do relatório mudou)"}


def debt(cache, code, first_year=FIRST_YEAR):
    """Balances at the end of each period, from the last RGF filed in each year. The first year's report also gives
    the balance at the end of the year before (column 'SALDO DO EXERCÍCIO ANTERIOR'), the starting point of a mandate."""
    out = {}
    for year in range(first_year, CURRENT_YEAR + 1):
        for key in sorted((k for k in cache.records if k.startswith(f"rgf|{year}|")),
                          key=lambda k: (k.split("|")[2][0] != "Q", -int(k.split("|")[2][1:]))):
            r = cache.records[key]
            if r["status"] != "ok":
                continue
            periodicity = key.split("|")[2][0]
            for period, vals in parse_rgf02(r["rows"], year).items():
                label = f"{key.split('|')[3]} {year} {key.split('|')[2]}"
                if not period.endswith("prior"):
                    out[period] = {**vals, "report": label}
                elif year == first_year:
                    end = f"{year - 1}-{'Q3' if periodicity == 'Q' else 'S2'}"
                    out[end] = {**vals, "report": label + ", coluna SALDO DO EXERCÍCIO ANTERIOR"}
            break
    return dict(sorted(out.items()))


def main():
    import sys
    if "--control" in sys.argv:  # planted defect: drop one DF line; the line-sum check must fail and nothing is written
        REVENUE_LINES.pop("ISS")
    result, coverage = {}, {}
    gaps = {}
    for code, uf in UF_CODES.items():
        LINE_GAPS.clear()
        cache = EntityCache("E", code)
        periods, ok = {}, []
        missing = []
        for year in range(FIRST_YEAR, CURRENT_YEAR + 1):
            for period in range(1, 7):
                p = build_period(cache, year, period)
                if p is None:
                    if year < CURRENT_YEAR:
                        missing.append(f"{year}-B{period}")
                    continue
                periods[f"{year}-B{period}"] = p
                ok.append((year, period))
        d = debt(cache, code)
        result[uf] = {"ibge": code, "periods": periods, "revenue_monthly": monthly(cache, ok), "debt": d,
                      "latest": {"rreo": max(periods, key=lambda k: (int(k[:4]), int(k[-1]))) if periods else None,
                                 "rgf": max(d, key=lambda k: (int(k[:4]), k[5], int(k[6]))) if d else None},
                      "missing_periods": missing}
        coverage[uf] = {"periods": len(periods), "missing": missing, "latest_rreo": result[uf]["latest"]["rreo"],
                        "latest_rgf": result[uf]["latest"]["rgf"]}
        print(uf, len(periods), "periods, latest", result[uf]["latest"], "missing", missing, flush=True)
        if LINE_GAPS:
            gaps[uf] = list(LINE_GAPS)
    if gaps:
        for uf, g in gaps.items():
            print("CHECK FAILED", uf, len(g), "periods, e.g.", g[0])
        raise SystemExit("revenue lines do not add up to RECEITAS CORRENTES (I); nothing written")
    print("check passed: in every state and bimester the revenue lines add up to RECEITAS CORRENTES (I) within R$ 1")
    payload = {
        "uf": result,
        "unit": "BRL (reais correntes)",
        "sign": "resultado positivo = sobrou dinheiro (superávit); negativo = faltou (déficit)",
        "period_rule": "YYYY-Bn = acumulado de janeiro ao fim do bimestre n (B6 = ano fechado). Os campos *_in_bimester são só o bimestre. "
                       "revenue_lines é o total dos 12 meses que terminam no bimestre (revenue_lines_window); para um mês, um ano ou um "
                       "mandato, some revenue_monthly.",
        "debt_rule": "YYYY-Qn = saldo no fim do quadrimestre n (Q1 abril, Q2 agosto, Q3 dezembro), do último RGF entregue no ano",
        "coverage": coverage,
        "sources": [
            {"fields": ["revenue_total", "revenue_in_bimester", "spending_committed", "spending_liquidated", "spending_paid",
                        "spending_committed_in_bimester", "spending_liquidated_in_bimester", "budget_result"],
             "source": "Tesouro Nacional, SICONFI, RREO Anexo 01 (Balanço Orçamentário). Receitas: 'RECEITAS (EXCETO INTRA-ORÇAMENTÁRIAS)', "
                       "coluna 'Até o Bimestre'. Despesas: 'DESPESAS (EXCETO INTRA-ORÇAMENTÁRIAS)', colunas empenhadas, liquidadas e pagas "
                       "até o bimestre. budget_result: " + BUDGET_RESULT_METHOD,
             "url_pattern": API + "/rreo?an_exercicio={year}&nr_periodo={bimester}&co_tipo_demonstrativo={report}&co_esfera=E&id_ente={ibge}&no_anexo=RREO-Anexo%2001"},
            {"fields": ["spending_by_function", "spending_by_function_total"],
             "source": "SICONFI, RREO Anexo 02 (Despesa por Função/Subfunção), 'Total das Despesas Exceto Intra-Orçamentárias', "
                       "coluna 'DESPESAS LIQUIDADAS ATÉ O BIMESTRE (d)'",
             "url_pattern": API + "/rreo?an_exercicio={year}&nr_periodo={bimester}&co_tipo_demonstrativo={report}&co_esfera=E&id_ente={ibge}&no_anexo=RREO-Anexo%2002"},
            {"fields": ["revenue_lines", "revenue_current_total", "rcl", "to_municipalities", "fundeb_deduction", "revenue_monthly"],
             "source": "SICONFI, RREO Anexo 03 (Receita Corrente Líquida): coluna 'TOTAL (ÚLTIMOS 12 MESES)' e colunas mensais <MR-11> a <MR>",
             "url_pattern": API + "/rreo?an_exercicio={year}&nr_periodo={bimester}&co_tipo_demonstrativo={report}&co_esfera=E&id_ente={ibge}&no_anexo=RREO-Anexo%2003"},
            {"fields": ["primary_result", "nominal_result", "results_reported"],
             "source": "SICONFI, RREO Anexo 06 (Resultados Primário e Nominal). O nome exato da linha usada está em *_method; "
                       "todas as linhas de resultado do anexo estão em results_reported",
             "url_pattern": API + "/rreo?an_exercicio={year}&nr_periodo={bimester}&co_tipo_demonstrativo={report}&co_esfera=E&id_ente={ibge}&no_anexo=RREO-Anexo%2006"},
            {"fields": ["debt"],
             "source": "SICONFI, RGF Anexo 02 (Demonstrativo da Dívida Consolidada Líquida), Poder Executivo: 'DÍVIDA CONSOLIDADA - DC (I)', "
                       "'DÍVIDA CONSOLIDADA LÍQUIDA (DCL)' e '% da DCL sobre a RCL AJUSTADA', colunas 'Até o nº Quadrimestre'",
             "url_pattern": API + "/rgf?an_exercicio={year}&in_periodicidade=Q&nr_periodo={quadrimester}&co_tipo_demonstrativo=RGF&no_anexo=RGF-Anexo%2002&co_esfera=E&co_poder=E&id_ente={ibge}"},
        ],
        "collected_at": date.today().isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("wrote", OUT, OUT.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
