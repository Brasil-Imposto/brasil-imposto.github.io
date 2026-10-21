"""How each line of the RTN Tabela 1.2 becomes ledger rows (spec 4.3 and 4.4, phase 1).

Every code printed in the table has exactly one role here:
  LEAVES      a money flow, with its type, its two nodes and the rule that placed it
  TOTALS      the sum of the lines right under it (the table's own parts add up exactly; checked, never a flow)
  OF_WHICH    a line followed by a 'd/q' (of which) line: stored as that child plus '<code>~rest'
  RGPS_URBAN  1.3.1, which holds the Tesouro's compensation to the RGPS: '1.3.1~ordinary' plus the internal money
  INTERNAL    money the União pays itself (printed on both sides of the table): internal_flow, never a flow
  RESULTS, ADJUSTMENTS, INTEREST  the bottom of the table (lines 3 and 5 to 10)
A code that is not here stops the load: a new line has to be placed first."""

U, SOC, SUB, CRED, DF = "gov:uniao", "soc:unknown", "gov:sub:br", "fin:credores", "gov:uf:DF"   # D127
NAT = "no_state_in_source_v1"


def _in(flow_type):        # people and companies pay the União
    return (flow_type, SOC, U, NAT)


def _out(flow_type):       # the União pays people and companies
    return (flow_type, U, SOC, NAT)


_GOV = ("transfer_union_to_subnational", U, SUB, NAT)   # the União pays state and municipal governments

LEAVES = {
    # 1. Receita total
    "1.1.01": _in("tax"), "1.1.02.1": _in("tax"), "1.1.02.2": _in("tax"), "1.1.02.3": _in("tax"),
    "1.1.02.4": _in("tax"), "1.1.02.5": _in("tax"), "1.1.03.1": _in("tax"), "1.1.03.2": _in("tax"),
    "1.1.03.3.1": _in("tax"), "1.1.03.3.2": _in("tax"), "1.1.03.3.3": _in("tax"), "1.1.03.3.4": _in("tax"),
    "1.1.04": _in("tax"), "1.1.05": _in("tax"), "1.1.06": _in("tax"), "1.1.07": _in("tax"), "1.1.08": _in("tax"),
    "1.1.09": _in("tax"), "1.1.10": _in("tax"), "1.2": _in("tax"), "1.3.2": _in("tax"),
    "1.4.1": _in("other_revenue"),
    "1.4.2.1": _in("dividend_royalty"), "1.4.2.2": _in("dividend_royalty"), "1.4.2.3": _in("dividend_royalty"),
    "1.4.2.4": _in("dividend_royalty"), "1.4.2.5": _in("dividend_royalty"), "1.4.2.6": _in("dividend_royalty"),
    "1.4.2.7": _in("dividend_royalty"), "1.4.2.8": _in("dividend_royalty"), "1.4.2.9": _in("dividend_royalty"),
    "1.4.3": _in("public_payroll_withholding"), "1.4.4": _in("dividend_royalty"), "1.4.5": _in("other_revenue"),
    "1.4.6": _in("tax"), "1.4.7": _in("tax"), "1.4.8.1": _in("other_revenue"),
    # 2. Transferências por repartição de receita
    "2.1": _GOV, "2.2.1": _out("transfer_to_society"), "2.2.2": _out("transfer_to_society"), "2.3": _GOV,
    "2.4": _GOV, "2.5": _GOV, "2.6": _GOV,
    # 4. Despesa total
    "4.1.1.1": _out("social_benefit"), "4.1.2.1": _out("social_benefit"), "4.2.1": _out("public_payroll_gross"),
    "4.3.01.1": _out("social_benefit"), "4.3.01.2.1": _out("social_benefit"), "4.3.02": _out("social_benefit"),
    "4.3.03": _GOV, "4.3.04": _out("social_benefit"), "4.3.05.1": _out("social_benefit"),
    "4.3.06": _out("transfer_to_society"), "4.3.07": _out("mixed_spending"), "4.3.09": _out("purchase"),
    "4.3.10": _GOV, "4.3.11": ("transfer_union_to_subnational", U, DF, "fcdf_df_v1"), "4.3.12": _out("purchase"),
    "4.3.13": _GOV, "4.3.14": _out("court_order"),
    "4.3.15.1.1": _out("subsidy"), "4.3.15.1.2": _out("subsidy"), "4.3.15.1.3.1": _out("subsidy"),
    "4.3.15.1.3.2": _out("subsidy"), "4.3.15.1.3.3": _out("subsidy"), "4.3.15.1.4.1": _out("subsidy"),
    "4.3.15.1.4.2": _out("lending"), "4.3.15.1.4.3": _out("subsidy"), "4.3.15.1.5.1": _out("subsidy"),
    "4.3.15.1.5.2": _out("lending"), "4.3.15.1.6": _out("subsidy"), "4.3.15.1.7": _out("subsidy"),
    "4.3.15.1.8": _out("subsidy"), "4.3.15.1.9": _out("subsidy"), "4.3.15.1.10": _out("subsidy"),
    "4.3.15.1.11": _out("lending"), "4.3.15.1.12": _out("mixed_spending"), "4.3.15.1.13": _out("subsidy"),
    "4.3.15.1.14": _out("subsidy"), "4.3.15.1.15": _out("subsidy"), "4.3.15.1.16": _out("subsidy"),
    "4.3.15.1.17": _out("lending"), "4.3.15.1.18": _out("mixed_spending"), "4.3.15.1.19": _out("mixed_spending"),
    "4.3.15.1.20": _out("subsidy"), "4.3.15.1.21": _out("subsidy"), "4.3.15.1.22": _out("subsidy"),
    "4.3.15.1.23": _out("subsidy"), "4.3.15.1.24": _out("subsidy"),
    "4.3.15.2": _out("subsidy"), "4.3.15.3": _out("mixed_spending"), "4.3.15.4": _out("subsidy"),
    "4.3.16": _out("mixed_spending"), "4.3.17": _out("mixed_spending"), "4.3.18": _out("lending"),
    "4.3.19": _out("transfer_to_society"),
    "4.3.20.1": _out("transfer_to_society"), "4.3.20.2": _out("mixed_spending"), "4.3.20.3": _out("mixed_spending"),
    "4.3.20.4": _out("mixed_spending"), "4.3.20.5": _out("mixed_spending"), "4.3.20.6": _GOV,
    "4.4.1.1": _out("public_payroll_gross"), "4.4.1.2": _out("social_benefit"), "4.4.1.3": _out("mixed_spending"),
    "4.4.1.4": _out("mixed_spending"), "4.4.1.5": _out("mixed_spending"),
    "4.4.2.1": _out("mixed_spending"), "4.4.2.2": _out("mixed_spending"), "4.4.2.3": _out("mixed_spending"),
    "4.4.2.4": _out("mixed_spending"), "4.4.2.5": _out("mixed_spending"), "4.4.2.6": _out("mixed_spending"),
    "4.4.2.7": _out("mixed_spending"), "4.4.2.8": _out("mixed_spending"), "4.4.2.9": _out("mixed_spending"),
}

OF_WHICH = {"1.4.8": "1.4.8.1", "4.1.1": "4.1.1.1", "4.1.2": "4.1.2.1", "4.2": "4.2.1",
            "4.3.01.2": "4.3.01.2.1", "4.3.05": "4.3.05.1"}

RGPS_URBAN = "1.3.1"
RGPS_ORDINARY = "1.3.1~ordinary"
COMPENSATION_MEMO = "memo:Compensação ao RGPS pelas Desonerações da Folha"

DERIVED = {  # derived key -> (printed line, the part taken out of it)
    **{f"{parent}~rest": (parent, child) for parent, child in OF_WHICH.items()},
    RGPS_ORDINARY: (RGPS_URBAN, COMPENSATION_MEMO),
}

REST = {
    "1.4.8~rest": _in("other_revenue"), "4.1.1~rest": _out("social_benefit"), "4.1.2~rest": _out("social_benefit"),
    "4.2~rest": _out("public_payroll_gross"), "4.3.01.2~rest": _out("social_benefit"),
    "4.3.05~rest": _out("social_benefit"), RGPS_ORDINARY: _in("tax"),
}

INTERNAL = {"4.3.08": ("tesouro", "rgps", RGPS_URBAN)}   # compensation for the payroll tax relief, also inside 1.3.1

TOTALS = {"1", "1.1", "1.1.02", "1.1.03", "1.1.03.3", "1.3", "1.4", "1.4.2", "2", "2.2", "4", "4.1", "4.3", "4.3.01",
          "4.3.15", "4.3.15.1", "4.3.15.1.3", "4.3.15.1.4", "4.3.15.1.5", "4.3.20", "4.4", "4.4.1", "4.4.2"}
PARTITIONS = TOTALS | {"6"}                              # their printed parts add up exactly (closure check)

RESULTS = {"3": (("1", 1), ("2", -1)), "5": (("3", 1), ("4", -1)), "8": (("5", 1), ("6", 1), ("7", 1)),
           "10": (("8", 1), ("9", 1))}
ADJUSTMENTS = {"6", "6.1", "6.2", "6.3", "6.4", "7"}     # methodological adjustments and statistical discrepancy: not money
INTEREST = {"9": ("interest", U, CRED, "no_state_endpoint_v1")}   # Banco Central, accrual; printed negative

PAIR = {"4.2~rest", "1.4.3"}   # gross payroll without court orders, and the servants' contribution withheld from it

MEMO_CHECKS = {  # memo line -> the ledger lines that must add up to it
    "memo:Arrecadação Líquida para o RGPS": ("1.3",),
    "memo:Arrecadação Ordinária": (RGPS_ORDINARY, "1.3.2"),
    COMPENSATION_MEMO: ("4.3.08",),
}

ALL_CODES = (set(LEAVES) | TOTALS | set(OF_WHICH) | {RGPS_URBAN} | set(INTERNAL) | set(RESULTS) | ADJUSTMENTS
             | set(INTEREST))


def kind_of(code):
    if code in LEAVES or code in INTERNAL or code in INTEREST:
        return "leaf"
    if code in TOTALS or code in OF_WHICH or code == RGPS_URBAN:
        return "total"
    if code in RESULTS:
        return "result"
    if code in ADJUSTMENTS:
        return "adjustment"
    raise KeyError(code)


def parent(code):
    return code.rsplit(".", 1)[0] if "." in code else None


def under(key, line):
    """True when ledger key `key` is part of printed line `line` (the line itself, a sub-code, or a derived part)."""
    return key == line or key.startswith(line + ".") or key.startswith(line + "~")
