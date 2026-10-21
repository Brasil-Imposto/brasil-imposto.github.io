"""Municipalities of one state (default Santa Catarina), 2021 to 2025 (6th bimester, the closed year) and the latest
bimester of 2026 -> data/series/{uf}-municipal-budgets.json (sc-municipal-budgets.json, rs-municipal-budgets.json)

Reads the cache filled by fetch_municipal_series.py --uf <UF> (run that first). Same fields and rules as the state
series, with every line of Anexo 03 (own taxes and transfers) instead of the 13 state lines. Coverage (how many
municipalities filed each report, and of which type) is part of the output.

Checks, to the cent, in every municipality and period; the JSON is written only when all pass:
  Anexo 03  the tax, transfer and other lines add up to RECEITAS CORRENTES (I), in the 12-month total and in every month
            of the report; the tax lines add up to "Impostos, Taxas e Contribuições de Melhoria", the transfer lines to
            "Transferências Correntes" and the detail lines to "Receita Patrimonial";
  Anexo 02  the functions add up to the annex total, and the subfunctions to their function.
--control plants two defects (the ISS line left out of the list, the largest function dropped): the checks must fail
and nothing is written.
Run: python3 data/scripts/series/build_municipal_series.py [--uf RS] [--out PATH] [--collected-at YYYY-MM-DD] [--control]
"""
import json
import sys
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path

from build_state_series import BUDGET_RESULT_METHOD, any_type, budget_null, debt
from fetch_municipal_series import YEARS, municipalities, uf_arg
from siconfi_client import API, CURRENT_YEAR, EntityCache
from siconfi_parse import parse_a01, parse_a02, parse_a03, parse_a06

ROOT = Path(__file__).resolve().parents[3]
LINES = {  # Anexo 03 line -> (group, plain label)
    "IPTU": ("tax", "IPTU"), "ISS": ("tax", "ISS"), "ITBI": ("tax", "ITBI"),
    "IRRF": ("tax", "Imposto de renda retido na fonte"),
    "Outros Impostos, Taxas e Contribuições de Melhoria": ("tax", "Outros impostos e taxas"),
    "Cota-Parte do FPM": ("transfer", "Fundo de Participação dos Municípios (União)"),
    "Cota-Parte do ICMS": ("transfer", "Cota-parte do ICMS (estado)"),
    "Cota-Parte do IPVA": ("transfer", "Cota-parte do IPVA (estado)"),
    "Cota-Parte do ITR": ("transfer", "Cota-parte do ITR (União)"),
    "Transferências da LC nº 61/1989": ("transfer", "IPI exportação (repasse do estado)"),
    "Transferências da LC nº 87/1996": ("transfer", "Lei Kandir, compensação do ICMS"),
    "Transferências do FUNDEB": ("transfer", "Fundeb"),
    "Outras Transferências Correntes": ("transfer", "Outras transferências correntes (inclui SUS, que o Anexo 03 não separa)"),
    "Contribuições": ("other", "Contribuições"),
    "Receita Patrimonial": ("other", "Receita patrimonial"),
    "Receita Agropecuária": ("other", "Receita agropecuária"),
    "Receita Industrial": ("other", "Receita industrial"),
    "Receita de Serviços": ("other", "Receita de serviços"),
    "Outras Receitas Correntes": ("other", "Outras receitas correntes"),
}
SUS_NULL = ("O Anexo 03 não tem linha própria para o SUS: os repasses do SUS estão dentro de 'Outras Transferências "
            "Correntes'. O valor separado está no RREO Anexo 12 (Saúde), que esta série não coleta.")


def group_of(key):
    if key in LINES:
        return LINES[key][0]
    if key.startswith(("RECEITAS CORRENTES", "RECEITA CORRENTE LÍQUIDA")):
        return "total"
    if key in ("Impostos, Taxas e Contribuições de Melhoria", "Transferências Correntes"):
        return "subtotal"
    if key in ("Rendimentos de Aplicação Financeira", "Outras Receitas Patrimoniais"):
        return "detail"
    return "deduction"


def build_period(cache, year, period):
    a01, tipo = any_type(cache, year, period, "RREO-Anexo 01", "RREO")
    if a01 is None:
        return None
    out = {"report": tipo, "months_covered": [f"{year}-01", f"{year}-{2 * period:02d}"]}
    parsed = parse_a01(a01["rows"], period)
    out.update({k: v for k, v in parsed.items() if not k.startswith("_")})
    out["budget_result_method"] = BUDGET_RESULT_METHOD
    nulls = {k: "linha não encontrada no Anexo 01" for k in
             ("revenue_total", "spending_committed", "spending_liquidated", "spending_paid") if out[k] is None}
    if out["budget_result"] is None:
        nulls["budget_result"] = budget_null(parsed, period)
    a06, _ = any_type(cache, year, period, "RREO-Anexo 06", tipo)
    if a06:
        out.update(parse_a06(a06["rows"]))
        for k in ("primary_result", "nominal_result"):
            if out[k] is None:
                nulls[k] = "o Anexo 06 enviado não traz esta linha de resultado"
    else:
        out.update({"primary_result": None, "primary_result_method": None, "nominal_result": None,
                    "nominal_result_method": None, "results_reported": {}})
        nulls["primary_result"] = nulls["nominal_result"] = "Anexo 06 não encontrado no SICONFI (RREO e RREO Simplificado)"
    a02, _ = any_type(cache, year, period, "RREO-Anexo 02", tipo)
    if a02:
        out["spending_by_function"], out["spending_by_function_total"] = parse_a02(a02["rows"])
    else:
        out["spending_by_function"], out["spending_by_function_total"] = [], None
        nulls["spending_by_function"] = "Anexo 02 não encontrado no SICONFI (RREO e RREO Simplificado)"
    a03, _ = any_type(cache, year, period, "RREO-Anexo 03", tipo)
    monthly = None
    if a03:
        lines, window = parse_a03(a03["rows"], year, period)
        out["revenue_lines"] = [{"key": ln["key"], "label": LINES.get(ln["key"], (None, ln["key"]))[1],
                                 "group": group_of(ln["key"]), "value": ln["total_12m"]} for ln in lines]
        out["revenue_lines_window"] = list(window)
        monthly = {ln["key"]: ln["months"] for ln in lines}
    else:
        out["revenue_lines"], out["revenue_lines_window"] = [], None
        nulls["revenue_lines"] = "Anexo 03 não encontrado no SICONFI (RREO e RREO Simplificado)"
    nulls["sus_transfers"] = SUS_NULL
    out["nulls"] = nulls
    return out, monthly


CENT = Decimal("0.005")


def dec(v):
    return Decimal(str(v)) if v is not None else Decimal(0)


def line_sum_errors(label, p, monthly):
    """Every list of lines taken from an annex against the annex's own total, to the cent."""
    errs = []
    lines = p["revenue_lines"]
    if lines:
        by_key = {ln["key"]: ln for ln in lines}
        total = next((ln for ln in lines if ln["key"].startswith("RECEITAS CORRENTES")), None)
        if total is None or total["value"] is None:
            errs.append((label, "Anexo 03", "linha RECEITAS CORRENTES (I) ausente"))
        else:
            s = sum(dec(ln["value"]) for ln in lines if ln["group"] in ("tax", "transfer", "other"))
            if abs(s - dec(total["value"])) > CENT:
                errs.append((label, "Anexo 03, 12 meses", "linhas - RECEITAS CORRENTES (I)", str(s - dec(total["value"]))))
        for sub, group in (("Impostos, Taxas e Contribuições de Melhoria", "tax"), ("Transferências Correntes", "transfer"),
                           ("Receita Patrimonial", "detail")):
            parts = [ln for ln in lines if ln["group"] == group]
            if sub in by_key and by_key[sub]["value"] is not None and parts:
                s = sum(dec(ln["value"]) for ln in parts)
                if abs(s - dec(by_key[sub]["value"])) > CENT:
                    errs.append((label, "Anexo 03, 12 meses", f"linhas - {sub}", str(s - dec(by_key[sub]["value"]))))
        if total is not None and monthly:
            for month, t in monthly.get(total["key"], {}).items():
                if t is None:
                    continue
                s = sum(dec(series.get(month)) for k, series in monthly.items() if group_of(k) in ("tax", "transfer", "other"))
                if abs(s - dec(t)) > CENT:
                    errs.append((label, f"Anexo 03, {month}", "linhas - RECEITAS CORRENTES (I)", str(s - dec(t))))
    if p.get("spending_by_function_total") is not None:
        s = sum(dec(f["value"]) for f in p["spending_by_function"])
        if abs(s - dec(p["spending_by_function_total"])) > CENT:
            errs.append((label, "Anexo 02", "funções - total do anexo", str(s - dec(p["spending_by_function_total"]))))
        for f in p["spending_by_function"]:
            if f["sub"]:
                s = sum(dec(x["value"]) for x in f["sub"])
                if abs(s - dec(f["value"])) > CENT:
                    errs.append((label, "Anexo 02", f"subfunções - {f['label']}", str(s - dec(f["value"]))))
    return errs


def checked(label, built, errors, control):
    """Runs the line-sum checks on one period as it goes into the output (with the planted defect under --control)."""
    p, monthly = built
    if control and p["spending_by_function"]:
        p = {**p, "spending_by_function": p["spending_by_function"][1:]}
    errors.extend(line_sum_errors(label, p, monthly))
    return built


def opt(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main():
    uf = uf_arg()
    control = "--control" in sys.argv
    if control:  # planted defect 1: ISS left out of the list of tax lines (it falls into the catch-all group)
        LINES.pop("ISS")
    out_path = Path(opt("--out") or ROOT / "data" / "series" / f"{uf.lower()}-municipal-budgets.json")
    ms = municipalities(uf)
    errors, checked_periods = [], 0
    result = {}
    cov = {y: Counter() for y in list(YEARS) + [CURRENT_YEAR]}
    for e in ms:
        code = e["cod_ibge"]
        cache = EntityCache("M", code)
        periods, months, month_report, lines = {}, [], [], {}
        for year in list(YEARS) + [CURRENT_YEAR]:
            built = None
            for period in ([6] if year < CURRENT_YEAR else range(6, 0, -1)):
                built = build_period(cache, year, period)
                if built:
                    break
            c = cov[year]
            c["municipalities"] += 1
            if not built:
                c["not_filed"] += 1
                continue
            key = f"{year}-B{period}"
            p, monthly = checked(f"{code} {key}", built, errors, control)
            checked_periods += 1
            periods[key] = p
            if year == CURRENT_YEAR and not p["revenue_lines"]:
                for earlier in range(period - 1, 0, -1):
                    eb = build_period(cache, year, earlier)
                    if eb and eb[0]["revenue_lines"]:
                        ekey = f"{year}-B{earlier}"
                        periods[ekey], monthly = checked(f"{code} {ekey}", eb, errors, control)
                        checked_periods += 1
                        for field in ("revenue_lines", "primary_result", "nominal_result"):
                            p["nulls"][field] = (f"{p['report']}: os Anexos 03 e 06 podem ser semestrais para municípios com "
                                                 f"menos de 50 mil habitantes (LRF art. 63, II, c); o último enviado está em {ekey}")
                        cov[year][f"annexes_03_06_from:{ekey}"] += 1
                        period = earlier  # the monthly revenue below comes from that report
                        break
            c["filed"] += 1
            c["report:" + p["report"]] += 1
            c[f"period:{key}"] += 1
            for field, name in (("revenue_total", "anexo01"), ("spending_by_function_total", "anexo02"),
                                ("revenue_lines_window", "anexo03"), ("primary_result", "anexo06")):
                if p.get(field) is not None:
                    c[name] += 1
            if monthly:
                own = [f"{year}-{m:02d}" for m in range(1, 2 * period + 1)]
                base = len(months)
                months.extend(own)
                month_report.extend([key] * len(own))
                for k, series in monthly.items():
                    lines.setdefault(k, [None] * base).extend(series.get(mk) for mk in own)
                for k, series in lines.items():
                    series.extend([None] * (len(months) - len(series)))
        d = debt(cache, code, first_year=min(YEARS))
        for year in list(YEARS) + [CURRENT_YEAR]:
            if any(k.startswith(str(year)) for k in d):
                cov[year]["rgf_filed"] += 1
        result[str(code)] = {"name": e["ente"], "population_siconfi": e["populacao"], "periods": periods,
                             "revenue_monthly": {"months": months, "month_report": month_report, "lines": lines},
                             "debt": d}
    coverage = {str(y): dict(sorted(c.items())) for y, c in cov.items()}
    for y, c in coverage.items():
        print(y, c)
    if errors:
        kinds = Counter(e[1].split(",")[0] + (", mês" if "," in e[1] and "12 meses" not in e[1] else "") for e in errors)
        print(f"CHECK FAILED: {len(errors)} line sums do not match their annex total ({dict(kinds)}); e.g.")
        for e in errors[:8]:
            print("  ", e)
        raise SystemExit("nothing written")
    print(f"check passed: {checked_periods} municipality-periods, every list of lines adds up to its annex total to the cent "
          "(Anexo 03 in 12 months and in every month; Anexo 02 functions and subfunctions)")
    payload = {
        "municipalities": result,
        "unit": "BRL (reais correntes)",
        "sign": "resultado positivo = sobrou dinheiro (superávit); negativo = faltou (déficit)",
        "period_rule": "YYYY-B6 = ano fechado (janeiro a dezembro). Em 2026, o último bimestre que cada prefeitura entregou "
                       "(acumulado de janeiro ao fim dele). revenue_lines = 12 meses que terminam no bimestre; revenue_monthly = mês a mês.",
        "debt_rule": "YYYY-Qn = fim do quadrimestre n; YYYY-Sn = fim do semestre n (prefeituras pequenas entregam o RGF por semestre)",
        "line_groups": {"tax": "impostos da própria prefeitura", "transfer": "transferências recebidas",
                        "other": "outras receitas correntes próprias", "subtotal": "soma de linhas acima",
                        "detail": "detalhe de uma linha acima", "total": "total do anexo",
                        "deduction": "deduções e ajustes para chegar à Receita Corrente Líquida"},
        "coverage": coverage,
        "coverage_note": "filed = prefeituras com RREO (Anexo 01) no período, pelo tipo RREO ou RREO Simplificado; anexo0N = quantas "
                         f"têm aquele anexo; rgf_filed = quantas têm RGF Anexo 02 no ano; municipalities = total ({len(ms)})",
        "sources": [
            {"fields": ["revenue_total", "spending_committed", "spending_liquidated", "spending_paid", "budget_result"],
             "source": "Tesouro Nacional, SICONFI, RREO Anexo 01 (Balanço Orçamentário), exceto intraorçamentárias; budget_result: "
                       + BUDGET_RESULT_METHOD,
             "url_pattern": API + "/rreo?an_exercicio={year}&nr_periodo={bimester}&co_tipo_demonstrativo={report}&co_esfera=M&id_ente={ibge}&no_anexo=RREO-Anexo%2001"},
            {"fields": ["spending_by_function"], "source": "SICONFI, RREO Anexo 02, despesas liquidadas até o bimestre, exceto intraorçamentárias",
             "url_pattern": API + "/rreo?an_exercicio={year}&nr_periodo={bimester}&co_tipo_demonstrativo={report}&co_esfera=M&id_ente={ibge}&no_anexo=RREO-Anexo%2002"},
            {"fields": ["revenue_lines", "revenue_monthly"], "source": "SICONFI, RREO Anexo 03 (Receita Corrente Líquida), todas as linhas: "
                       "coluna 'TOTAL (ÚLTIMOS 12 MESES)' e colunas mensais <MR-11> a <MR>",
             "url_pattern": API + "/rreo?an_exercicio={year}&nr_periodo={bimester}&co_tipo_demonstrativo={report}&co_esfera=M&id_ente={ibge}&no_anexo=RREO-Anexo%2003"},
            {"fields": ["primary_result", "nominal_result", "results_reported"], "source": "SICONFI, RREO Anexo 06; a linha usada está em *_method",
             "url_pattern": API + "/rreo?an_exercicio={year}&nr_periodo={bimester}&co_tipo_demonstrativo={report}&co_esfera=M&id_ente={ibge}&no_anexo=RREO-Anexo%2006"},
            {"fields": ["debt"], "source": "SICONFI, RGF Anexo 02 (Dívida Consolidada Líquida), Poder Executivo, RGF ou RGF Simplificado",
             "url_pattern": API + "/rgf?an_exercicio={year}&in_periodicidade={Q_or_S}&nr_periodo={n}&co_tipo_demonstrativo={report}&no_anexo=RGF-Anexo%2002&co_esfera=M&co_poder=E&id_ente={ibge}"},
            {"fields": ["name", "population_siconfi"], "source": "SICONFI, cadastro de entes", "url": API + "/entes"},
        ],
        "collected_at": opt("--collected-at") or date.today().isoformat(),
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("wrote", out_path, out_path.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
