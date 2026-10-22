"""Parsers for the SICONFI annexes used by the series builders. Input: the compact rows of a cached response,
[rotulo, coluna, cod_conta, conta, valor]. Every parser returns only values the annex reports, never a derived
estimate; where a figure is missing the caller records a null with the reason.
"""
import re

FUNCTIONS = ["Legislativa", "Judiciária", "Essencial à Justiça", "Administração", "Defesa Nacional",
             "Segurança Pública", "Relações Exteriores", "Assistência Social", "Previdência Social", "Saúde",
             "Trabalho", "Educação", "Cultura", "Direitos da Cidadania", "Urbanismo", "Habitação", "Saneamento",
             "Gestão Ambiental", "Ciência e Tecnologia", "Agricultura", "Organização Agrária",
             "Indústria", "Comércio e Serviços", "Comunicações", "Energia", "Transporte", "Desporto e Lazer",
             "Encargos Especiais"]


def _first(rows, match, col_prefix):
    for rot, col, cod, conta, val in rows:
        if match(cod, conta) and col.startswith(col_prefix):
            return val
    return None


def parse_a01(rows, period):
    """Balanço Orçamentário: totals excluding intra-budget operations, and the annex's own surplus/deficit line.
    The line compares total revenue with the spending executed so far: liquidated in bimesters 1 to 5, committed in
    the 6th (what the filed deficits match in the data). The filed value is kept only when it agrees, to R$ 1, with the
    annex's own totals on that basis; otherwise budget_result is None and _budget_status says why."""
    rev = lambda cod, conta: cod == "ReceitasExcetoIntraOrcamentarias" or conta.startswith("RECEITAS (EXCETO INTRA")
    exp = lambda cod, conta: cod == "DespesasExcetoIntraOrcamentarias" or conta.startswith("DESPESAS (EXCETO INTRA")
    sup = lambda cod, conta: cod == "Superavit" or conta.startswith("SUPERÁVIT (")
    dfc = lambda cod, conta: cod == "Deficit" or conta.startswith("DÉFICIT (")
    # Totals before the surplus/deficit line. Up to 2019 the rows coded TotalReceitas/TotalDespesas are "TOTAL (VII)"
    # and "TOTAL (XIV)", which already include the deficit and the surplus; the comparable rows are the subtotals
    # "com refinanciamento". From 2020 they are "TOTAL DAS RECEITAS (V)" and "TOTAL DAS DESPESAS (XII)".
    tot_rev = lambda cod, conta: cod == "SubtotalReceitasComRefinanciamento" or conta.startswith("TOTAL DAS RECEITAS")
    tot_exp = lambda cod, conta: cod == "SubtotalDespesasComRefinanciamento" or conta.startswith("TOTAL DAS DESPESAS")
    out = {
        "revenue_total": _first(rows, rev, "Até o Bimestre"),
        "revenue_in_bimester": _first(rows, rev, "No Bimestre"),
        "spending_committed": _first(rows, exp, "DESPESAS EMPENHADAS ATÉ O BIMESTRE"),
        "spending_liquidated": _first(rows, exp, "DESPESAS LIQUIDADAS ATÉ O BIMESTRE"),
        "spending_paid": _first(rows, exp, "DESPESAS PAGAS ATÉ O BIMESTRE"),
        "spending_committed_in_bimester": _first(rows, exp, "DESPESAS EMPENHADAS NO BIMESTRE"),
        "spending_liquidated_in_bimester": _first(rows, exp, "DESPESAS LIQUIDADAS NO BIMESTRE"),
    }
    refi = lambda cod, conta: cod == "AmortizacaoRefinanciamentoDaDivida" or conta.startswith("AMORTIZAÇÃO DA DÍVIDA / REFINANCIAMENTO")
    out["debt_refinancing_liquidated"] = _first(rows, refi, "DESPESAS LIQUIDADAS ATÉ O BIMESTRE")
    basis = "EMPENHADAS" if period == 6 else "LIQUIDADAS"
    deficit = _first(rows, dfc, "Até o Bimestre")
    surplus = _first(rows, sup, f"DESPESAS {basis} ATÉ O BIMESTRE")
    filed = -deficit if deficit else surplus
    total_rev = _first(rows, tot_rev, "Até o Bimestre")
    total_exp = _first(rows, tot_exp, f"DESPESAS {basis} ATÉ O BIMESTRE")
    expected = None if None in (total_rev, total_exp) else round(total_rev - total_exp, 2)
    if filed is None:
        status = "missing"
    elif expected is not None and abs(filed - expected) <= 1:
        status = "ok"
    else:
        status = "inconsistent"
    out["budget_result"] = filed if status == "ok" else None
    out["budget_result_basis"] = "despesas empenhadas" if basis == "EMPENHADAS" else "despesas liquidadas"
    out["_budget_status"], out["_budget_filed"], out["_budget_expected"] = status, filed, expected
    out["_total_revenue_incl_intra"], out["_total_spending_basis_incl_intra"] = total_rev, total_exp
    return out


def parse_a02(rows, col_prefix="DESPESAS LIQUIDADAS ATÉ O BIMESTRE", leak_totals=False):
    """Despesa por Função/Subfunção, excluding intra-budget spending. Returns (functions, declared total).
    leak_totals=True reproduces the 2024 script, which let the rows after the last function (intra-budget and
    grand total) fall into the subfunctions of "Encargos Especiais"; kept only as the broken control of the checks."""
    rows = [r for r in rows if r[1].startswith(col_prefix) and r[0].startswith("Total das Despesas Exceto Intra")]
    total = next((r[4] for r in rows if r[3].startswith("DESPESAS (EXCETO")), None)
    functions, current = [], None
    for rot, col, cod, conta, val in rows:
        if conta.startswith("DESPESAS (EXCETO"):
            continue
        if not leak_totals and (conta.startswith("DESPESAS (INTRA") or conta.startswith("TOTAL (")):
            current = None
            continue
        if conta in FUNCTIONS:
            current = {"label": conta, "value": val, "sub": []}
            functions.append(current)
        elif current is not None and val:
            label = conta.split(" - ", 1)[1] if conta.startswith("FU") and " - " in conta else conta
            current["sub"].append({"label": label, "value": val})
    for f in functions:
        f["sub"].sort(key=lambda x: -x["value"])
    functions.sort(key=lambda x: -x["value"])
    return functions, total


def month_of(year, period, offset):
    """<MR-offset> in the report of bimester `period` of `year` -> 'YYYY-MM'."""
    idx = year * 12 + (2 * period - 1) - offset
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def line_key(conta):
    """The line name as filed, with whitespace collapsed and '( - )' written '(-)': the same line is spelled both
    ways in different years."""
    return re.sub(r"\s+", " ", conta).strip().replace("( - )", "(-)")


def parse_a03(rows, year, period):
    """Receita Corrente Líquida: every line with its 12-month total and its 12 monthly values.
    Returns (lines, window) where lines is an ordered list of {key, cod, total_12m, months: {YYYY-MM: v}}."""
    lines, by_key, seen_cod = [], {}, {}
    for rot, col, cod, conta, val in rows:
        key = line_key(conta)
        if key in seen_cod and seen_cod[key] != cod:
            key = f"{key} [{cod}]"
        seen_cod.setdefault(key, cod)
        line = by_key.get(key)
        if line is None:
            line = by_key[key] = {"key": key, "cod": cod, "total_12m": None, "months": {}}
            lines.append(line)
        m = re.fullmatch(r"<MR(?:-(\d+))?>", col)
        if m:
            line["months"][month_of(year, period, int(m.group(1) or 0))] = val
        elif col.startswith("TOTAL (ÚLTIMOS 12 MESES)"):
            line["total_12m"] = val
    window = (month_of(year, period, 11), month_of(year, period, 0))
    return lines, window


RESULT_RE = re.compile(r"^RESULTADO (PRIMÁRIO|NOMINAL)( AJUSTADO)?( \((COM|SEM) RPPS\))?( AJUSTADO)?\s*-\s*(Acima|Abaixo) da Linha", re.I)


def parse_a06(rows):
    """Resultado Primário e Nominal. Returns every result line reported (label -> value) and the headline choice:
    primary = 'acima da linha' (with RPPS when the annex splits it, as the pre-2023 layout covered the whole budget);
    nominal = 'acima da linha' when reported, else 'abaixo da linha'. Positive = surplus."""
    reported = {}
    pref = ("VALOR INCORRIDO", "VALOR", "Até o Bimestre")
    for rot, col, cod, conta, val in rows:
        m = RESULT_RE.match(conta.strip())
        if not m or val is None:
            continue
        label = re.sub(r"\s*\([IVXLC]+\)\s*=.*$", "", conta.strip())
        label = re.sub(r"\s*\([IVXLC]+\)\s*$", "", label)
        rank = next((i for i, p in enumerate(pref) if col.startswith(p)), len(pref))
        if label not in reported or rank < reported[label][1]:
            reported[label] = (val, rank)
    reported = {k: v[0] for k, v in reported.items()}

    def pick(kind, side, rpps_order):
        for rpps in rpps_order:
            for label, val in reported.items():
                m = RESULT_RE.match(label)
                if m.group(1).upper() != kind or m.group(6).lower() != side or (m.group(2) or m.group(5)):
                    continue
                if (m.group(4) or "").upper() == rpps:
                    return label, val
        return None, None

    out = {"results_reported": reported}
    for kind, key in (("PRIMÁRIO", "primary_result"), ("NOMINAL", "nominal_result")):
        label, val = pick(kind, "acima", ["COM", "", "SEM"])
        if label is None:
            label, val = pick(kind, "abaixo", ["COM", "", "SEM"])
        out[key] = val
        out[key + "_method"] = label
    return out


def parse_rgf02(rows, year):
    """Dívida Consolidada (DC) and Dívida Consolidada Líquida (DCL) at the end of each period reported as a column."""
    wanted = {"dc": ("DividaConsolidada", "DÍVIDA CONSOLIDADA - DC"),
              "dcl": ("DividaConsolidadaLiquida", "DÍVIDA CONSOLIDADA LÍQUIDA"),
              "dcl_pct_rcl": ("PercentualDaDCLSobreARCL", "% da DCL sobre a RCL")}
    out = {}
    for rot, col, cod, conta, val in rows:
        m = re.match(r"Até o (\d)º (Quadrimestre|Semestre)", col)
        if m:
            period = f"{year}-{'Q' if m.group(2) == 'Quadrimestre' else 'S'}{m.group(1)}"
        elif col.startswith("SALDO DO EXERCÍCIO ANTERIOR"):
            period = f"{year - 1}-prior"
        else:
            continue
        for field, (c, prefix) in wanted.items():
            if cod == c or conta.startswith(prefix):
                out.setdefault(period, {}).setdefault(field, val)
    return out
