"""Reference rows of the ledger: nodes, flow types and allocation rules (spec 4.1, 4.3 and 4.4).

Rows never change in place. A changed meaning gets a new id (allocation rules carry a version), so a flow always points
to the rule that placed it. While phase 1 is in development, deleting data/ledger/ledger.duckdb rebuilds everything."""

UFS = tuple("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())

NODES = [
    ("gov:uniao", "gov_union", None, True, "União (Governo Central: Tesouro, INSS e Banco Central)"),
    ("gov:sub:br", "gov_subnational_unassigned", None, True,
     "Governos estaduais e municipais, sem informação de estado (ainda não separados)"),
    ("soc:br", "society_national", None, False, "União (país inteiro): o que a fonte oficial classifica como nacional"),
    ("soc:unknown", "society_unknown", None, False,
     "Sem informação de estado: pessoas e empresas de algum estado, que a fonte não diz qual (D127)"),
    ("fin:credores", "creditors", None, False, "Credores da dívida pública"),
    ("ext:mundo", "world", None, False, "Exterior"),
]
for _uf in UFS:
    NODES.append((f"gov:uf:{_uf}", "gov_state", _uf, True,
                  "Governo do Distrito Federal" if _uf == "DF" else f"Governo do estado ({_uf})"))
    if _uf != "DF":  # the DF is state and municipality at once (spec 4.1)
        NODES.append((f"gov:mun:{_uf}", "gov_municipal", _uf, True, f"Prefeituras do estado ({_uf})"))
    NODES.append((f"soc:uf:{_uf}", "society_state", _uf, False, f"Pessoas e empresas do estado ({_uf})"))

FLOW_TYPES = [  # (id, nature, allows_negative, label)
    ("tax", "primary", True, "Imposto e contribuição"),
    ("public_payroll_withholding", "circular", True, "Imposto e contribuição retidos de salário público"),
    ("public_payroll_gross", "primary", True, "Salário bruto de servidor (ativos, aposentados e pensionistas)"),
    ("social_benefit", "primary", True, "Benefício (INSS, BPC, Bolsa Família, seguro-desemprego, abono)"),
    ("purchase", "primary", False, "Compra, obra e serviço"),
    ("court_order", "primary", True, "Sentença judicial e precatório"),
    ("subsidy", "primary", True, "Subsídio e subvenção"),
    ("transfer_to_society", "primary", True, "Transferência a pessoas, empresas, fundos e entidades"),
    ("mixed_spending", "primary", True, "Gasto que a fonte não separa (compra, repasse a estados e municípios e outros)"),
    ("transfer_union_to_subnational", "intergovernmental", True, "Repasse da União a estados e municípios"),
    ("transfer_state_to_municipal", "intergovernmental", True, "Repasse do estado aos municípios (parte das prefeituras e Fundeb)"),
    ("subnational_tax", "primary", True, "Imposto estadual e municipal"),
    ("dividend_royalty", "primary", True, "Dividendo e royalty"),
    ("other_revenue", "primary", True, "Outras receitas (concessões, receitas próprias e demais)"),
    ("interest", "financial", True, "Juros da dívida"),
    ("lending", "financial", True, "Empréstimo e devolução"),
    ("trade", "external", False, "Exportação e importação"),
]

RULES = [  # (id, version, method, description, evidence)
    ("no_state_in_source_v1", 1, "unallocated",
     "A fonte publica só o total do país. O fluxo fica marcado 'sem informação de estado' (pessoas e empresas, ou governos "
     "estaduais e municipais) até uma fonte oficial dizer o estado, nas fases 2 e 3. Nunca conta como dinheiro que ficou "
     "na União (D127).",
     "RTN Tabela 1.2 e base Despesas e Transferências Totais da União: nenhuma das duas tem estado"),
    ("fcdf_df_v1", 1, "direct", "O Fundo Constitucional do Distrito Federal vai ao governo do DF.",
     "Lei 10.633/2002, art. 1º"),
    ("no_state_endpoint_v1", 1, "direct", "Nenhuma das pontas tem estado: a União paga juros aos credores da dívida.",
     "spec, seção 4.1 (nó fin:credores)"),
]

METHOD = {r[0]: r[2] for r in RULES}


def seed(con):
    con.executemany("INSERT INTO node VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING", NODES)
    con.executemany("INSERT INTO flow_type VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING", FLOW_TYPES)
    con.executemany("INSERT INTO allocation_rule VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING", RULES)
    for table, key, rows in (("node", "node_id", NODES), ("flow_type", "flow_type_id", FLOW_TYPES),
                             ("allocation_rule", "rule_id", RULES)):
        if con.execute(f"SELECT * FROM {table} ORDER BY {key}").fetchall() != sorted(rows):
            raise SystemExit(f"{table}: the warehouse differs from reference.py; a changed row needs a new id")
