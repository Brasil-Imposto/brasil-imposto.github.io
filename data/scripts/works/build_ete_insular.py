"""Build data/works/ete-insular.json (ampliacao da ETE Insular, Casan, Florianopolis).

Run after (all inside one working directory outside the repository):
    bash download.sh                      # IPCA + World Bank
    python3 casan_fetch.py casan          # Casan contract register, SAP view, obras table, amendment PDFs
    python3 cnpj_fetch.py cnpj2 39673759000170 78739158000175 58793852000163 19862375000199
    python3 build_ete_insular.py .
Quotes from official pages that are not machine-readable (news of the Casan and of the State, Alesc
biographies, TCE-SC reports) were read on the collection date and are kept here with their URLs.
"""
import csv
import io
import json
import os
import sys
from datetime import datetime
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from convert import Converter, no_dashes  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "data", "works", "ete-insular.json")
COLLECTED = "2026-09-30"
T = "https://transparencia.casan.com.br"
CASAN_NEWS = {
    "tender_2020_01": "https://casan.com.br/noticia/index/url/tres-consorcios-se-habilitam-para-ampliar-a-maior-estacao-de-esgoto-do-estado",
    "bids_2020_07": "https://www.casan.com.br/noticia/index/url/no-dia-de-seu-aniversario-casan-licita-maior-obra-de-saneamento-do-estado",
    "progress_2025_12": "https://www.casan.com.br/noticia/index/url/obras-de-ampliacao-e-modernizacao-da-ete-insular-chegam-a-80-da-estrutura-civil",
    "progress_2026_01": "https://www.casan.com.br/noticia/index/url/trabalhos-na-obra-de-ampliacao-e-modernizacao-da-ete-insular-sao-retomados",
    "jica": "https://www.casan.com.br/menu-conteudo/index/url/japanese-international-cooperation-agency-jica",
    "board_2026": "https://www.casan.com.br/noticia/index/url/casan-tera-funcionario-de-carreira-como-novo-presidente",
    "potecas_2023_11": "https://www.casan.com.br/noticia/index/url/obra-da-ete-potecas-avanca-em-ritmo-acelerado-em-sao-jose",
}
RI = {"board_page": "https://ri.casan.com.br/governanca-corporativa/diretoria/",
      "fato_2026_04_13": "https://ri.casan.com.br/bfd_download/13-04-2026-eleicao-de-novo-diretor-presidente-e-alteracoes-na-diretoria-executiva-da-companhia/"}
ALESC = {
    "eduardo": "https://memoriapolitica.alesc.sc.gov.br/biografia/1158-Eduardo_Pinho_Moreira",
    "moises": "https://memoriapolitica.alesc.sc.gov.br/biografia/1308-Carlos_Moises",
    "daniela": "https://memoriapolitica.alesc.sc.gov.br/biografia/1386-Daniela_Reinehr",
    "jorginho": "https://memoriapolitica.alesc.sc.gov.br/biografia/514-Jorginho_Mello",
}


def br_date(s):
    d, m, y = s.split("/")
    return f"{y}-{m}-{d}"


def money(s):
    s = s.replace("R$", "").strip().replace(".", "").replace(",", ".")
    return float(s) if s not in ("-", "") else None


def main(work):
    conv = Converter(work)
    raw = json.load(open(os.path.join(work, "casan", "casan_raw.json")))
    raw["sap_updated"]["dataAtualizacao"] = datetime.strptime(raw["sap_updated"]["dataAtualizacao"], "%b %d, %Y, %I:%M:%S %p").strftime("%Y-%m-%d")
    pntp = raw["pntp"]
    sap = raw["sap"]

    # ---------------------------------------------------------------- Casan "Obras de expansao" table
    text = open(os.path.join(work, "casan", "casan_obras_expansao.csv"), encoding="latin1").read()
    rows = list(csv.reader(io.StringIO(text), delimiter=";"))
    obras = {r[1].strip(): r for r in rows[1:] if len(r) > 7 and r[1].strip()}
    ins = obras["SES Insular - Ampliação ETE e Bacias D/F"]
    pot = obras["Nova ETE Potecas"]
    ins_principal = money(ins[6])
    ins_billed = money(ins[7])
    pot_principal = money(pot[6])
    footer = [r for r in rows if r and r[0].startswith("Dados atualizados")][0][0]

    # ---------------------------------------------------------------- contracts
    def adds(rec, kinds=None):
        out = []
        for a in rec["aditivos"]:
            out.append({"act": a["aditivo"], "date": br_date(a["inicioVigencia"]) if a.get("inicioVigencia") else None,
                        "value_added_brl": a.get("valorAditivado"), "value_removed_brl": a.get("valorSuprimido"),
                        "new_end": br_date(a["vencimentoVigencia"]) if a.get("vencimentoVigencia") else None,
                        "object": " ".join((a.get("objeto") or "").split()),
                        "files": [{"name": f["nome"], "url": f"{T}/data/contrato/arquivo/{f['id']}"} for f in a.get("arquivos") or []]})
        return out

    r20 = pntp["EOC1246/2020/MAT"]["record"]
    add_sum = sum(Decimal(str(a.get("valorAditivado") or 0)) for a in r20["aditivos"])
    sup_sum = sum(Decimal(str(a.get("valorSuprimido") or 0)) for a in r20["aditivos"])
    readj = sum(Decimal(str(a.get("valorAditivado") or 0)) for a in r20["aditivos"] if a["aditivo"].startswith("REAJUSTE"))
    current_pntp = Decimal(str(r20["valor"])) + add_sum - sup_sum
    principal_pntp = current_pntp - readj
    assert abs(float(principal_pntp) - ins_principal) < 0.01, (principal_pntp, ins_principal)

    sap_2020 = [x for x in sap["2000009269"]["rows"] if x["numeroContrato"] == "EOC001246/2020"][0]
    sap_2018 = [x for s in ("2000004715", "2000005225") for x in sap[s]["rows"] if x["numeroContrato"].startswith("EOC001151/2018")]
    assert len(sap_2018) == 2 and all(x["valorConsumido"] == 0.0 for x in sap_2018)
    r18 = pntp["EOC1151/2018/MAT"]["record"]
    assert abs(sum(x["valorContrato"] for x in sap_2018) - r18["valor"]) < 0.01
    r26 = pntp["EOC1534/2026/MAT"]["record"]
    r17 = pntp["EOC1119/2017/MAT"]["record"]

    contracts = [
        {
            "number": "EOC 1151/2018 (EOC001151/2018-A e -B no SAP)",
            "role": "primeiro contrato da ampliação; rescindido",
            "tender": "Concorrência Pública Internacional nº 7/2017 (CI 7/2017)",
            "object": " ".join(r18["objeto"].split()),
            "company": r18["empresa"],
            "company_cnpj": None,
            "company_cnpj_note": "O registro da Casan e as Resoluções que rescindiram o contrato não trazem CNPJ; as consorciadas são TRIX Engenharia Civil Ltda e INFRACON Engenharia e Comércio Ltda (Resolução 213/2019).",
            "signed_on": br_date(r18["inicioVigencia"]),
            "signed_on_note": "Início de vigência no registro da Casan; data de assinatura não publicada no registro.",
            "value_original_brl": r18["valor"],
            "value_current_brl": r18["valor"],
            "value_by_company_sap_brl": {x["numeroContrato"]: x["valorContrato"] for x in sap_2018},
            "amount_consumed_sap_brl": sum(x["valorConsumido"] for x in sap_2018),
            "duration_days": r18.get("prazo"),
            "status": r18["situacao"],
            "amendments": adds(r18),
            "manager_in_record": r18.get("gestor"),
            "source": {"doc": "Portal da Transparência da Casan, Contratos (vista PNTP) e Saldos contratuais (SAP)",
                       "url": pntp["EOC1151/2018/MAT"]["query_url"], "url_sap": sap["2000004715"]["query_url"],
                       "collected_on": COLLECTED},
        },
        {
            "number": "EOC 1246/2020 (EOC001246/2020)",
            "role": "contrato principal em execução",
            "tender": "Concorrência nº 01/2019 (CN 1/2019; nos documentos, 'CP 01/2019')",
            "object": " ".join(r20["objeto"].split()),
            "object_full": " ".join(sap_2020["objeto"].split()),
            "company": "CONSÓRCIO ITAJUÍ/CONSTRUTAMI ETE INSULAR",
            "company_cnpj": "39673759000170",
            "signed_on": br_date(r20["inicioVigencia"]),
            "signed_on_source": "Termos aditivos: 'celebrado em 06/11/2020'",
            "value_original_brl": r20["valor"],
            "value_current_brl": float(current_pntp),
            "value_current_note": "Calculado: valor original + aditivos - supressões do registro PNTP da Casan (inclui reajustes contratuais).",
            "value_principal_brl": ins_principal,
            "value_principal_note": "Valor original + termos aditivos, sem os reajustes (tabela 'Obras de expansão' da Casan; igual ao cálculo pelo registro, ao centavo).",
            "readjustments_total_brl": float(readj),
            "value_contract_sap_brl": sap_2020["valorContrato"],
            "value_contract_sap_note": "O SAP (base de " + raw["sap_updated"]["dataAtualizacao"] + ") ainda não incorpora o TA 7/2025 (R$ 4.719.562,01) e o reajuste 6/2026 (R$ 6.121.290,51); a soma dos dois fecha a diferença.",
            "duration_days_original": r20.get("prazo"),
            "end_original_computed": "2025-04-14",
            "end_current": br_date(r20["vencimentoVigencia"]),
            "status": r20["situacao"],
            "amendments": adds(r20),
            "manager_in_record": r20.get("gestor"),
            "inspectors_in_record": r20.get("fiscal"),
            "financing": "JICA (Agência de Cooperação Internacional do Japão), segundo os termos aditivos ('Os recursos financeiros [...] são provenientes da Agência de Cooperação Internacional do Japão - JICA').",
            "source": {"doc": "Portal da Transparência da Casan, Contratos (vista PNTP), Saldos contratuais (SAP) e PDFs dos aditivos",
                       "url": pntp["EOC1246/2020/MAT"]["query_url"], "url_sap": sap["2000009269"]["query_url"],
                       "collected_on": COLLECTED},
        },
        {
            "number": "EOC 1534/2026",
            "role": "obra ligada: emissário de esgoto bruto do SES Insular (junto com adutora de água do Sul da Ilha)",
            "tender": r26["licitacao"],
            "object": " ".join(r26["objeto"].split()),
            "company": r26["empresa"],
            "company_cnpj": "19862375000199",
            "signed_on": "2026-09-15",
            "signed_on_source": "Contrato: 'Lavrado na sede da CASAN [...] aos 15/09/2026'; assinaturas digitais de 15 e 17/09/2026",
            "value_original_brl": r26["valor"],
            "value_current_brl": r26["valor"],
            "value_split_quote": "O valor relativo à mão de obra é R$ 6.737.130,13 [...] O valor relativo aos materiais e equipamentos é R$ 24.453.287,15",
            "end_current": br_date(r26["vencimentoVigencia"]),
            "status": r26["situacao"],
            "funding_quote": "Os recursos financeiros destinados ao pagamento dos serviços, objeto deste Contrato, são provenientes do Orçamento de 2026, 2027 e 2028 da CASAN",
            "amendments": [],
            "manager_in_record": r26.get("gestor"),
            "inspectors_in_record": r26.get("fiscal"),
            "note": "Mistura esgoto (SES Insular) e água (SAA Sul da Ilha); fica fora das somas e da comparação.",
            "source": {"doc": "Portal da Transparência da Casan, Contratos (vista PNTP) e PDF do contrato",
                       "url": pntp["EOC1534/2026/MAT"]["query_url"],
                       "contract_pdf": f"{T}/data/contrato/arquivo/{r26['arquivos'][0]['id']}", "collected_on": COLLECTED},
        },
    ]
    context_contracts = [{
        "number": "EOC 1119/2017",
        "role": "contexto: sistema complementar da Beira-Mar Norte (URA), do mesmo SES Insular; não é a ampliação da ETE",
        "company": r17["empresa"], "value_original_brl": r17["valor"], "signed_on": br_date(r17["inicioVigencia"]),
        "status": r17["situacao"], "object": " ".join(r17["objeto"].split()),
        "source": {"url": pntp["EOC1119/2017/MAT"]["query_url"], "collected_on": COLLECTED},
    }]

    # ---------------------------------------------------------------- payments
    payments = {
        "by_year": None,
        "by_year_reason": ("A Casan é empresa estatal e não paga pelo SIGEF: os pagamentos não aparecem no Portal da Transparência "
                           "do Poder Executivo de SC. O portal da Casan publica, por contrato, só o acumulado ('valor consumido') e o "
                           "saldo; a página 'Despesa da Empresa' remete às demonstrações financeiras, que não abrem por contrato."),
        "cumulative": [
            {"measure": "Valor consumido do contrato (SAP)", "contract": "EOC001246/2020", "amount_brl": sap_2020["valorConsumido"],
             "balance_brl": sap_2020["valorAtual"], "as_of": raw["sap_updated"]["dataAtualizacao"],
             "note": "Campo 'valorConsumido' do SAP da Casan; inclui reajustes. Não é, por definição publicada, 'valor pago'.",
             "source": sap["2000009269"]["query_url"]},
            {"measure": "Valor principal faturado (sem reajustes)", "contract": "EOC001246/2020", "amount_brl": ins_billed,
             "of_principal_brl": ins_principal, "as_of": footer,
             "source": raw["obras_csv"]["url"], "source_label": raw["obras_csv"]["label"]},
            {"measure": "Valor consumido do contrato rescindido (SAP)", "contract": "EOC001151/2018", "amount_brl": 0.0,
             "note": "As duas linhas do consórcio Trix-Infracon aparecem com valor consumido zero.",
             "source": sap["2000004715"]["query_url"]},
        ],
        "share_billed_computed": round(ins_billed / ins_principal, 4),
    }

    # ---------------------------------------------------------------- companies
    def cnpj_rec(c):
        p = os.path.join(work, "cnpj2", f"{c}.json")
        return json.load(open(p)) if os.path.exists(p) else None

    def company(c, contracts_list, website=None, website_evidence=None):
        d = cnpj_rec(c)
        if d is None:
            return {"cnpj": c, "legal_name": None, "note": "registro não obtido"}
        if d["_mirror"] == "minhareceita.org":
            rec = {"legal_name": d.get("razao_social"), "trade_name": d.get("nome_fantasia") or None,
                   "legal_nature": d.get("natureza_juridica"), "city": f"{d.get('municipio')}/{d.get('uf')}",
                   "registration_status": d.get("descricao_situacao_cadastral"), "registration_status_date": d.get("data_situacao_cadastral"),
                   "partners": [{"name": s.get("nome_socio"), "qualification": s.get("qualificacao_socio"), "since": s.get("data_entrada_sociedade")} for s in d.get("qsa") or []]}
        else:
            e = d.get("estabelecimento") or {}
            seen, partners = set(), []
            for s in d.get("socios") or []:
                k = (s.get("nome"), s.get("data_entrada"))
                if k in seen:
                    continue
                seen.add(k)
                partners.append({"name": s.get("nome"), "qualification": (s.get("qualificacao_socio") or {}).get("descricao", "").strip(),
                                 "since": s.get("data_entrada")})
            rec = {"legal_name": d.get("razao_social"), "trade_name": e.get("nome_fantasia"),
                   "legal_nature": (d.get("natureza_juridica") or {}).get("descricao"),
                   "city": f"{(e.get('cidade') or {}).get('nome')}/{(e.get('estado') or {}).get('sigla')}",
                   "registration_status": e.get("situacao_cadastral"), "registration_status_date": e.get("data_situacao_cadastral"),
                   "partners": partners}
        rec.update({"cnpj": c, "contracts": contracts_list, "official_website": website, "official_website_evidence": website_evidence,
                    "portal_transparencia_federal": f"https://portaldatransparencia.gov.br/pessoa-juridica/{c}",
                    "source": {"doc": "Base aberta do CNPJ da Receita Federal, lida via espelho " + d["_mirror"] + " (servidor oficial inacessível do exterior)",
                               "url": d["_url"], "collected_on": COLLECTED}})
        return rec

    companies = [
        company("39673759000170", ["EOC 1246/2020"]),
        company("78739158000175", ["EOC 1246/2020 (líder do consórcio)"], "https://www.itajui.com.br/",
                "Título do site 'Itajui - Engenharia de Obras Ltda'; o e-mail do consórcio na Autorização Contratual da Casan é do mesmo domínio (itajui.com.br)."),
        company("58793852000163", ["EOC 1246/2020 (consorciada)"], "https://www.construtami.com.br/",
                "Logotipo 'CONSTRUTAMI', e-mail construtami@construtami.com.br e endereço em São Paulo, mesma cidade da Receita."),
        company("19862375000199", ["EOC 1534/2026"], "https://www.cfo.eng.br/",
                "Título do site traz o mesmo endereço do contrato (Rua Araci Vaz Callado, 1201, Estreito, Florianópolis) e o e-mail contato@cfo.eng.br consta na Autorização Contratual."),
        {"cnpj": None, "legal_name": "TRIX ENGENHARIA CIVIL LTDA", "contracts": ["EOC 1151/2018 (consorciada, contrato rescindido)"],
         "note": "CNPJ não consta nos documentos da Casan lidos; nome como grafado na Resolução 213/2019 e no SAP (fornecedor 2000004715).",
         "official_website": None, "source": {"url": sap["2000004715"]["query_url"], "collected_on": COLLECTED}},
        {"cnpj": None, "legal_name": "INFRACON ENGENHARIA E COMÉRCIO LTDA", "contracts": ["EOC 1151/2018 (consorciada, contrato rescindido)"],
         "note": "CNPJ não consta nos documentos da Casan lidos; no SAP: 'INFRACON ENG. E COM. LTDA' (fornecedor 2000005225).",
         "official_website": None, "source": {"url": sap["2000005225"]["query_url"], "collected_on": COLLECTED}},
    ]

    # ---------------------------------------------------------------- people
    ta = lambda i: f"{T}/data/contrato/arquivo/{i}"  # noqa: E731
    people = [
        {"name": "Roberta Maas dos Anjos", "role": "Diretora-Presidente da Casan",
         "role_source": "Resoluções da Diretoria 213/2019, 264/2019 e 135/2021 (texto no registro de contratos da Casan)",
         "signed": [{"act": "TA 01/2021 ao EOC 1246/2020 (reequilíbrio de 14,84%)", "date": "2021-10-21", "url": ta(134841)},
                    {"act": "TA 02/2023 ao EOC 1246/2020 (acréscimo de 6,46%)", "date": "2023-01-04", "url": ta(134842)},
                    {"act": "Resoluções 213/2019 (rescisão do EOC 1151/2018), 264/2019 e 135/2021", "date": "2019-08-19 a 2021-04-19",
                     "url": pntp["EOC1151/2018/MAT"]["query_url"]}]},
        {"name": "Fábio Cesar F. Krieger", "role": "Diretor de Operação e Expansão da Casan", "role_source": "Resoluções 213/2019, 264/2019 e 135/2021; notícia da Casan de 02/07/2020",
         "signed": [{"act": "Resoluções 213/2019, 264/2019 e 135/2021 (contrato EOC 1151/2018)", "date": "2019-08-19 a 2021-04-19",
                     "url": pntp["EOC1151/2018/MAT"]["query_url"]}]},
        {"name": "Pedro Joel Horstmann", "role": "Diretor de Operação e Expansão desde 19/07/2021; Diretor-Presidente desde 15/04/2026 (acumula)",
         "role_source": RI["fato_2026_04_13"],
         "signed": [{"act": "TA 01/2021", "date": "2021-10-20", "url": ta(134841)}, {"act": "TA 02/2023", "date": "2023-01-04", "url": ta(134842)},
                    {"act": "TA 03/2023", "date": "2023-10-24", "url": ta(134843)}, {"act": "TA 04/2024", "date": "2024-09-02", "url": ta(134844)},
                    {"act": "TA 05/2024", "date": "2024-10-14", "url": ta(124795)}, {"act": "TA 06/2025 (prazo)", "date": "2025-04-08", "url": ta(140141)},
                    {"act": "TA 08/2026 (prazo)", "date": "2026-03-12", "url": ta(175242)},
                    {"act": "Contrato EOC 1534/2026", "date": "2026-09-17", "url": contracts[2]["source"]["contract_pdf"]}]},
        {"name": "Edson Moritz Martins da Silva", "role": "Diretor-Presidente da Casan (agosto de 2023 a 14/04/2026)",
         "role_source": [RI["fato_2026_04_13"], CASAN_NEWS["board_2026"]],
         "signed": [{"act": "TA 03/2023", "date": "2023-10-24", "url": ta(134843)}, {"act": "TA 04/2024", "date": "2024-09-04", "url": ta(134844)},
                    {"act": "TA 05/2024", "date": "2024-10-15", "url": ta(124795)}, {"act": "TA 06/2025 (prazo)", "date": "2025-04-09", "url": ta(140141)},
                    {"act": "TA 07/2025 (acréscimo de 3,26%)", "date": "2025-08-15", "url": ta(154641)}]},
        {"name": "Rosane Vettori", "role": "Diretora Administrativa da Casan (e de Inovação e Negócios desde 15/04/2026)",
         "role_source": [RI["board_page"], RI["fato_2026_04_13"]],
         "signed": [{"act": "TA 07/2025", "date": "2025-08-14", "url": ta(154641)}, {"act": "TA 08/2026 (prazo)", "date": "2026-03-10", "url": ta(175242)}]},
        {"name": "Carlos Ivan Sturzbecher", "role": "Diretor Financeiro e de Relações com os Investidores da Casan",
         "role_source": [RI["board_page"], RI["fato_2026_04_13"]],
         "signed": [{"act": "Contrato EOC 1534/2026", "date": "2026-09-15", "url": contracts[2]["source"]["contract_pdf"]}]},
        {"name": "Paulo Cesar Varassin", "role": "assinou pela contratada (certificado digital no TA 01/2021); sócio-administrador da Itajuí Engenharia de Obras Ltda na Receita",
         "role_source": [ta(134841), "https://publica.cnpj.ws/cnpj/78739158000175"], "side": "contratada",
         "signed": [{"act": "TA 01/2021", "date": "2021-10-25", "url": ta(134841)}]},
        {"name": "Lorenzo Varassin", "role": "assinou pela contratada (certificado digital nos TAs de 2023 em diante); administrador do consórcio na Receita",
         "role_source": [ta(134842), "https://publica.cnpj.ws/cnpj/39673759000170"], "side": "contratada",
         "signed": [{"act": "TA 02/2023 e TA 03/2023", "date": "2023", "url": ta(134842)}]},
        {"name": "Evandro André Martins", "role": "gestor do contrato EOC 1246/2020 no registro da Casan (campo 'gestor')", "role_source": pntp["EOC1246/2020/MAT"]["query_url"], "signed": []},
    ]
    governors = [
        {"name": "Eduardo Pinho Moreira", "office": "Governador (titular)", "start": "2018-04-06", "end": "2018-12-31",
         "party_at_time": "MDB", "party_quote": "Com a mudança de nome do partido, Eduardo Pinho filiou-se ao Movimento Democrático Brasileiro (MDB) e assumiu efetivamente como Governador em 6 de abril de 2018",
         "relevant_dates": ["2018-09-10 (início do EOC 1151/2018)"], "source": ALESC["eduardo"]},
        {"name": "Daniela Reinehr", "office": "Governadora interina", "start": "2020-10-26", "end": "2020-11-27",
         "party_at_time": "sem partido", "party_quote": "Atualmente sem Partido, Daniela participa da organização do partido Aliança pelo Brasil",
         "party_note": "Frase da própria biografia, escrita em 2020; a tabela de mandatos da mesma página rotula os períodos de forma inconsistente (PSL e 'Partido Liberal').",
         "relevant_dates": ["2020-11-06 (assinatura do EOC 1246/2020)"], "source": ALESC["daniela"], "source_period": ALESC["moises"]},
        {"name": "Carlos Moisés da Silva", "office": "Governador (titular)", "start": "2019-01-01", "end": "2023-01-01",
         "party_at_time": "PSL (Republicanos a partir de março de 2022)", "party_quote": "No ano de 2018, filiou-se ao Partido Social Liberal (PSL) [...] a partir de março do ano que concorrerá à reeleição, passou para a sigla Republicanos",
         "interruptions": ["afastado de 2020-10-26 a 2020-11-27 e de 2021-03-30 a 2021-05-07 (Daniela Reinehr interina)"],
         "relevant_dates": ["2019-08-19 (rescisão do EOC 1151/2018)", "2021-10-20 (TA 01/2021)"], "source": ALESC["moises"]},
        {"name": "Jorginho Mello", "office": "Governador (titular)", "start": "2023-01-01", "end": None,
         "party_at_time": "PL", "party_quote": "Mandatos: Governador(a) 01/02/2023 - 31/01/2027 Partido Liberal",
         "start_note": "A tabela da Alesc registra 01/02/2023; a posse constitucional foi em 01/01/2023.",
         "relevant_dates": ["2023-01-04 (TA 02/2023) em diante", "2026-09-15 (EOC 1534/2026)"], "source": ALESC["jorginho"]},
    ]
    governors_note = ("O governador não assina os contratos da Casan: nos documentos lidos assinam os diretores da companhia. "
                      "Os mandatos vêm das biografias da Alesc.")

    # ---------------------------------------------------------------- findings
    findings = [
        {"body": "Casan (Diretoria Executiva)", "kind": "ato administrativo da contratante", "process": "Resolução nº 213/2019 (protocolo 2019/33106)", "date": "2019-08-19",
         "summary_quote": "Aplicar as Empresas TRIX Engenharia Civil Ltda e INFRACON Engenharia e Comércio Ltda., componentes do Consórcio TRIX-INFRACON INSULAR, a penalidade de \"Suspensão Temporária por 2 (dois) anos\" para participar de licitação, impedimento de contratar com a CASAN e rescisão unilateral do Contrato EOC n.º 1.151/2018 [...] tendo em vista o descumprimento das obrigações contratuais.",
         "status": "rescisão mantida (Resolução 264/2019); suspensão com efeito suspensivo (264/2019) e substituída por advertência e multa em acordo judicial (135/2021)",
         "url": pntp["EOC1151/2018/MAT"]["query_url"]},
        {"body": "Casan (Diretoria Executiva)", "kind": "ato administrativo da contratante", "process": "Resolução nº 264/2019 (protocolo 2019/47101)", "date": "2019-10-07",
         "summary_quote": "Atribuir efeito suspensivo à penalidade [...] Manter a decisão de rescisão unilateral [...] do Contrato EOC n.º 1.151/2018",
         "status": "decidido", "url": pntp["EOC1151/2018/MAT"]["query_url"]},
        {"body": "Justiça de SC (4ª Vara Cível da Comarca de Florianópolis) e Casan", "kind": "acordo judicial homologado, registrado em ato da Casan",
         "process": "Autos nº 5006866-60.2019.8.24.0023; Mandado de Segurança nº 5006892-58.2019.8.24.0023 (citados pela Casan); Resolução Casan nº 135/2021",
         "date": "2020-12-10 (acordo); 2020-12-17 (homologação); 2021-04-19 (resolução)",
         "summary_quote": "Aplicar às Empresas integrantes do Consórcio TRIX-INFRACON INSULAR, a penalidade de 'Advertência e multa no valor de R$ 198.466,16' [...] conforme acordo judicial celebrado entre o referido consórcio e a CASAN, em virtude da rescisão do Contrato EOC n° 1151/2018 e aplicação de penalidades, que foram objeto de judicialização",
         "status": "acordo homologado por sentença (segundo a Casan); autos do TJSC não consultados (consulta exige acesso do Brasil)",
         "url": pntp["EOC1151/2018/MAT"]["query_url"]},
        {"body": "Casan", "kind": "versão da contratante sobre o atraso", "process": "Notícia oficial de 02/07/2020", "date": "2020-07-02",
         "summary_quote": "A licitação teve de ser relançada em 2019, pois o consórcio vencedor do processo licitatório anterior se recusou a executar a obra nos moldes previstos no Termo de Referência, forçando a rescisão do contrato e atraso do empreendimento.",
         "status": "afirmação de uma das partes; o acordo judicial de 2020 encerrou a disputa", "url": CASAN_NEWS["bids_2020_07"]},
        {"body": "TCE-SC", "kind": "auditoria operacional da ETE Insular existente (antes da ampliação)",
         "process": "AOR 04/05801564 e PMO 07/00627901 (Decisão 3567/2010, sobre o Relatório de Monitoramento DAE 020/2010)",
         "date": "2010-08-16 (sessão)",
         "summary_quote": "6.1.3. reiterar a implantação das recomendações 6.2.4 e 6.2.6 da Decisão n. 1457/2008, que não foram cumpridas, com prazo de vencimento em 30/11/2010",
         "context_quote": "Reiterar a realização de avaliação técnica sobre a capacidade da ETE Insular, com o objetivo de verificar se a Estação tem condições de receber novas ligações de esgoto (Decisão 1457/2008, item 6.2.1)",
         "status": "monitoramento de plano de ação de 2010; desfecho final não localizado. Trata da estação antiga, não do contrato de ampliação.",
         "url": "https://www.tcesc.tc.br/sites/default/files/ETE%20insular%20PM.pdf"},
        {"body": "TCE-SC (Diretoria de Licitações e Contratações)", "kind": "relatório técnico sobre contrato vizinho do mesmo sistema (não é a ampliação da ETE)",
         "process": "@REP 20/00098007, Relatório DLC 408/2022 (Contrato EOC 1119/2017, URA Beira-Mar Norte)", "date": "2022-05-17",
         "summary_quote": "A Casan informa a ampliação da ETE Insular, no valor de R$ 144,8 milhões de investimento. [...] se demonstra que a ETE Insular está apresentando eficiência no tratamento dos efluentes.",
         "status": "sugestão da área técnica ao relator; decisão do Pleno não localizada", "url": "https://consulta.tce.sc.gov.br/RelatoriosDecisao/ConsultaRelatorioNovo/2000098007_16773723.pdf"},
    ]
    findings_none = ("Nenhuma decisão do TCE-SC, do MPSC, da CGU, do TCU ou do MPF específica sobre a Concorrência 01/2019 ou o contrato EOC 1246/2020 "
                     "foi localizada nesta coleta. Limites: o Diário do TCE-SC não foi lido dia a dia (como na pesquisa da ponte) e o TJSC não foi consultado.")

    # ---------------------------------------------------------------- comparison
    used_months, used_years = ["202001", "202204", "202205", "202312", "202407"], [2024]
    ins_conv = conv.brl_month(ins_principal, "202001")
    pot_parts = []
    for num, base in (("EOC1314/2022/MAT", "202205"), ("EOC1377/2024/MAT", "202312"), ("EOC1399/2024/MAT", "202407")):
        rec = pntp[num]["record"]
        principal = Decimal(str(rec["valor"])) + sum(Decimal(str(a.get("valorAditivado") or 0)) for a in rec["aditivos"] if not a["aditivo"].startswith("REAJUSTE")) \
            - sum(Decimal(str(a.get("valorSuprimido") or 0)) for a in rec["aditivos"])
        c = conv.brl_month(float(principal), base)
        c.update({"contract": num, "company": rec["empresa"], "price_base_note": "mês-base dos reajustes do próprio contrato",
                  "object": " ".join(rec["objeto"].split())[:200], "source": pntp[num]["query_url"]})
        pot_parts.append(c)
    assert abs(sum(p["amount_brl_nominal"] for p in pot_parts) - pot_principal) < 0.02, (sum(p["amount_brl_nominal"] for p in pot_parts), pot_principal)
    pot_2024 = sum(p["amount_brl_2024"] for p in pot_parts)
    belem = conv.brl_month(140_000_000.0, "202204")
    mgd = 1_000_000 * 3.785411784 / 86400.0
    fred = conv.foreign_year(180_000_000.0, "USA", 2024)

    def per(v, q):
        return round(v / q, 2) if q else None

    items = [
        {"id": "ete-insular", "name": "ETE Insular (ampliação e modernização, com Bacias D e F)", "place": "Florianópolis/SC", "country": "Brazil", "is_subject": True,
         "years": "2020-2027 (contrato); preços-base de jan/2020", "treatment": "terciário com remoção de nitrogênio e fósforo (Casan, 24/01/2020)",
         "capacity_final_l_s": 612, "capacity_added_l_s": 612 - 296, "population_served_after": 225000,
         "scope_note": "O contrato inclui redes: 12.209 m de rede coletora, 6 estações elevatórias, 9.512 m de emissários e 3.753 ligações (Casan, 02/07/2020). Não há valor separado da estação no registro; o custo por L/s aqui é um limite superior do custo só da ETE.",
         "cost_reported": {"amount": ins_principal, "currency": "BRL", "basis": "Valor principal (original + aditivos, sem reajustes), tabela 'Obras de expansão' da Casan, " + footer},
         "conversion": ins_conv, "cost_brl_2024": ins_conv["amount_brl_2024"],
         "sources": [{"field": "cost", "url": raw["obras_csv"]["url"]}, {"field": "capacity, population", "url": CASAN_NEWS["tender_2020_01"]},
                     {"field": "scope", "url": CASAN_NEWS["bids_2020_07"]}]},
        {"id": "ete-potecas", "name": "Nova ETE Potecas (primeira etapa)", "place": "São José/SC", "country": "Brazil",
         "years": "2022-2026 (contratos); preços-base de mai/2022, dez/2023 e jul/2024", "treatment": "lodos ativados por aeração prolongada, com remoção complementar de fósforo (Casan, 07/12/2023)",
         "capacity_final_l_s": 600, "capacity_added_l_s": None, "capacity_note": "Estação nova que substitui lagoas de 423 L/s; a segunda etapa prevê 800 L/s.",
         "population_served_after": 328494,
         "scope_note": "Três contratos da mesma estação (obra principal, emissários com tratamento preliminar e desidratação de lodo, elétrica e automação). Sem redes coletoras.",
         "cost_reported": {"amount": pot_principal, "currency": "BRL", "basis": "Valor principal da 'Nova ETE Potecas' na mesma tabela da Casan (soma dos três contratos, sem reajustes; conferido pelo registro)"},
         "conversion": pot_parts, "cost_brl_2024": round(pot_2024, 2),
         "sources": [{"field": "cost", "url": raw["obras_csv"]["url"]}, {"field": "capacity, population", "url": CASAN_NEWS["potecas_2023_11"]},
                     {"field": "treatment", "url": "https://www.casan.com.br/noticia/index/url/sao-jose-obras-avancam-para-tornar-tratamento-de-esgoto-em-potecas-mais-moderno"}]},
        {"id": "ete-belem", "name": "ETE Belém (ampliação, Sanepar)", "place": "Curitiba/PR", "country": "Brazil",
         "years": "duas etapas, concluídas em 28/04/2022", "treatment": "ampliação com decantadores primários (processo existente mantido); remoção de nutrientes não citada na fonte",
         "capacity_final_l_s": 2520, "capacity_added_l_s": 1020, "population_served_after": None,
         "population_note": "A fonte fala em 'cerca de 800 mil moradores' atendidos hoje; é população atual, não de projeto.",
         "scope_note": "Só a estação. Escala 4 vezes maior que a Insular, o que barateia o L/s.",
         "cost_reported": {"amount": 140_000_000.0, "currency": "BRL", "basis": "'O investimento, feito em duas as etapas, é de cerca de R$ 140 milhões' (valor aproximado, nominal)"},
         "conversion": belem, "cost_brl_2024": belem["amount_brl_2024"],
         "conversion_note": "Corrigido desde abr/2022 (data da notícia). Como parte foi gasta antes, a correção fica abaixo da real: é um limite inferior.",
         "source_type": "Agência Estadual de Notícias do Paraná (governo do estado), lida em cópia do Internet Archive porque a página original responde 404.",
         "sources": [{"field": "cost, capacity", "url": "https://web.archive.org/web/20251114233919/https://www.parana.pr.gov.br/aen/Noticia/Inaugurada-ampliacao-da-Estacao-de-Tratamento-de-Esgoto-Belem-maior-da-Sanepar-no-PR"}]},
        {"id": "fredericksburg", "name": "Fredericksburg Wastewater Treatment Plant Upgrade", "place": "Fredericksburg, Virginia", "country": "United States",
         "years": "acordo de projeto e obra em 2024; obra de cerca de 4 anos", "treatment": "remoção avançada de nitrogênio e fósforo ('enhanced nutrient removal')",
         "capacity_final_l_s": round(6.0 * mgd, 1), "capacity_added_l_s": round(1.5 * mgd, 1), "capacity_note": "4,5 para 6,0 milhões de galões por dia (1 MGD = 43,81 L/s).",
         "population_served_after": None,
         "scope_note": "Só a estação (ampliação e modernização de planta dos anos 1950). Orçamento, não custo final.",
         "cost_reported": {"amount": 180_000_000.0, "currency": "USD", "basis": "'The $180 million project' (página oficial da prefeitura)"},
         "conversion": fred, "cost_brl_2024": fred["amount_brl_2024_fx"], "cost_brl_2024_ppp": fred["amount_brl_2024_ppp"],
         "conversion_note": "Convertido pelos fatores de 2024 (ano do acordo); o gasto se estende até cerca de 2028, sem cronograma anual publicado.",
         "sources": [{"field": "cost, capacity, scope", "url": "https://www.fredericksburgva.gov/1883/Wastewater-Treatment-Plant-Upgrade"}]},
    ]
    for it in items:
        it["cost_per_l_s_final_brl_2024"] = per(it["cost_brl_2024"], it["capacity_final_l_s"])
        it["cost_per_l_s_added_brl_2024"] = per(it["cost_brl_2024"], it.get("capacity_added_l_s"))
        if it.get("population_served_after"):
            it["cost_per_inhabitant_brl_2024"] = per(it["cost_brl_2024"], it["population_served_after"])
        if "cost_brl_2024_ppp" in it:
            it["cost_per_l_s_final_brl_2024_ppp"] = per(it["cost_brl_2024_ppp"], it["capacity_final_l_s"])
            it["cost_per_l_s_added_brl_2024_ppp"] = per(it["cost_brl_2024_ppp"], it["capacity_added_l_s"])
    subj = items[0]["cost_per_l_s_final_brl_2024"]
    byid = {it["id"]: it for it in items}
    r_pot = byid["ete-potecas"]["cost_per_l_s_final_brl_2024"] / subj
    r_bel = subj / byid["ete-belem"]["cost_per_l_s_final_brl_2024"]
    r_fx = byid["fredericksburg"]["cost_per_l_s_final_brl_2024"] / subj
    r_ppp = byid["fredericksburg"]["cost_per_l_s_final_brl_2024_ppp"] / subj
    fmt = lambda x: f"{x:.1f}".replace(".", ",")  # noqa: E731
    reading = (f"Por L/s de capacidade final, a Insular custa quase o mesmo que a nova ETE Potecas, da mesma Casan "
               f"(a Potecas sai {round((r_pot - 1) * 100):d}% mais cara por L/s), mesmo com redes dentro do contrato da Insular; custa {fmt(r_bel)} vezes o L/s da "
               f"ampliação da ETE Belém, que é 4 vezes maior e cuja fonte não cita redes nem tratamento terciário; e custa menos que a ampliação "
               f"com remoção de nutrientes de Fredericksburg (EUA): esta sai {fmt(r_fx)} vezes mais cara pelo câmbio e {fmt(r_ppp)} vezes pela PPP. "
               "Nada disso, sozinho, indica preço acima do mercado: as diferenças de escala e de escopo são grandes e estão anotadas em cada item.")
    comparison = {
        "unit": "R$ de dez/2024 por litro por segundo (L/s) de capacidade de tratamento ao fim da obra",
        "unit_secondary": ["R$ por L/s acrescentado", "R$ por habitante de projeto (quando a fonte informa)"],
        "items": items,
        "ratios_computed": {it["id"]: round(it["cost_per_l_s_final_brl_2024"] / subj, 3) for it in items},
        "reading": reading,
        "excluded_candidates": [
            {"name": "Outras obras de esgoto da Casan com redes (SES Ingleses, Saco Grande)", "reason": "Mesma cidade; escopos dominados por redes, sem capacidade de estação comparável publicada na mesma fonte."},
            {"name": "ETE Alambari, Cambará/PR (Sanepar, R$ 13 milhões)", "reason": "A página oficial da Sanepar respondeu 403 do exterior; vazão não confirmada em fonte oficial."},
            {"name": "ETE Mampituba, Torres/RS (Corsan, R$ 24 milhões)", "reason": "A Corsan foi privatizada em 2023; a nota é de empresa privada, não de órgão público."},
        ],
        "method": conv.method(used_months, used_years),
    }

    # ---------------------------------------------------------------- work + card
    work_obj = {
        "name": "Ampliação e modernização da Estação de Tratamento de Esgoto (ETE) Insular e das Bacias D e F",
        "short_name": "ETE Insular",
        "municipalities": [{"name": "Florianópolis", "uf": "SC", "ibge_code": 4205407}],
        "level": "state",
        "level_note": "Obra da Casan, sociedade de economia mista controlada pelo Estado de SC. A Casan não usa o SIGEF: seus contratos e gastos ficam no portal próprio da companhia.",
        "agency": {"name": "Companhia Catarinense de Águas e Saneamento (Casan)", "cnpj": "82508433000117"},
        "financing": "Financiamento da JICA (Programa de Saneamento Ambiental de Santa Catarina, contrato de 2010)",
        "financing_source": CASAN_NEWS["jica"],
        "siconfi_function": "Saneamento",
        "siconfi_function_code": 17,
        "siconfi_note": "Função de governo em que a obra se enquadra (Portaria MOG 42/1999). Como é gasto de empresa estatal, não aparece nos balanços do Estado no SICONFI.",
        "status": "em execução",
        "status_detail": [
            {"text": "82,87% da estrutura civil concluída; 'Já para 2026, a CASAN vai trabalhar para a conclusão das estruturas em andamento com o objetivo de iniciar a operação.'", "date": "2026-01-20", "url": CASAN_NEWS["progress_2026_01"]},
            {"text": "Situação 'Andamento', início nov/20, término abr/27", "date": "2026-08-30", "url": raw["obras_csv"]["url"]},
            {"text": "Vigência prorrogada até 14/04/2027 (TA 08/2026)", "date": "2026-03-10", "url": ta(175242)},
        ],
        "dates": {"first_contract_start": "2018-09-10", "first_contract_rescinded": "2019-08-19", "new_tender_bids": "2020-01-23",
                  "current_contract_signed": "2020-11-06", "current_contract_end_original": "2025-04-14", "current_contract_end_now": "2027-04-14",
                  "expected_operation": "2026 (meta da Casan); contrato até abr/2027"},
        "capacity": {"before_l_s": 296, "after_l_s": 612, "population_before": 150000, "population_after": 225000,
                     "source": CASAN_NEWS["tender_2020_01"], "source_2": CASAN_NEWS["bids_2020_07"]},
        "description_plain": ("A ETE Insular é a maior estação de esgoto do estado e trata o esgoto do Centro e de bairros vizinhos de Florianópolis. "
                              "A obra quase dobra a capacidade (de 296 para 612 litros por segundo), troca o tratamento por um que também tira nitrogênio "
                              "e fósforo, e leva redes de coleta a bairros ainda sem ligação (José Mendes, Morro da Lagoa e partes de Itacorubi, Pantanal e Córrego Grande). "
                              "O primeiro contrato, de 2018, foi rescindido em 2019 sem pagamento registrado; o atual começou em novembro de 2020 e deveria acabar "
                              "em abril de 2025, mas foi prorrogado até abril de 2027."),
        "location_note": "'Localizada na entrada da Ilha de Santa Catarina' (Casan, 02/07/2020). A foto do cartão mostra a Baía Sul, não a estação: não há foto livre da ETE no Wikimedia Commons.",
        "sources": [CASAN_NEWS["tender_2020_01"], CASAN_NEWS["bids_2020_07"], CASAN_NEWS["progress_2025_12"], CASAN_NEWS["progress_2026_01"]],
    }
    card = {
        "title": "ETE Insular",
        "subtitle": "Ampliação da estação que a Casan chama de maior do estado",
        "place": "Florianópolis",
        "stats": [
            {"label": "Contrato atual", "value": round(float(current_pntp), 2), "unit": "BRL", "display": "R$ 261,9 mi", "note": "com aditivos e reajustes; original R$ 144,9 mi"},
            {"label": "Capacidade", "value": 612, "unit": "L/s", "display": "296 → 612 L/s", "note": "Casan"},
            {"label": "Já consumido", "value": sap_2020["valorConsumido"], "unit": "BRL", "display": "R$ 177,4 mi", "note": "SAP da Casan, base de " + raw["sap_updated"]["dataAtualizacao"]},
            {"label": "Atraso", "value": 24, "unit": "meses", "display": "+2 anos", "note": "fim previsto abr/2025, prorrogado para abr/2027"},
        ],
        "photo": "docs/superpowers/previews/assets/cases/ete-insular/baia-sul.jpg",
    }
    terms_check = ("Nenhum documento oficial lido usa 'superfaturamento', 'sobrepreço' ou 'desvio' para esta obra. "
                   "O termo usado pela Casan para o primeiro contrato é 'descumprimento das obrigações contratuais'.")

    out = {
        "slug": "ete-insular", "collected_on": COLLECTED,
        "report": "docs/research/BRASIL-IMPOSTO_RESEARCH_obras-sc-ete-insular_2026-09-30.md",
        "rules": "Somente papéis e atos oficiais, com as palavras do órgão. Nenhuma inferência de irregularidade. Valores nominais com fonte e data de coleta; somas e razões marcadas como computed são desta pesquisa.",
        "work": work_obj,
        "contracts": contracts, "context_contracts": context_contracts,
        "contracts_totals_computed": {"main_contract_original_brl": r20["valor"], "main_contract_current_brl": float(current_pntp),
                                       "main_contract_principal_brl": ins_principal, "main_contract_readjustments_brl": float(readj),
                                       "growth_over_original_pct": round((float(current_pntp) / r20["valor"] - 1) * 100, 2),
                                       "growth_principal_over_original_pct": round((ins_principal / r20["valor"] - 1) * 100, 2)},
        "payments": payments, "companies": companies, "people": people,
        "governors": governors, "governors_note": governors_note,
        "findings": findings, "findings_none_note": findings_none,
        "media": "docs/superpowers/previews/assets/cases/ete-insular/credits.json",
        "comparison": comparison, "card": card, "terms_check": terms_check,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out = no_dashes(out)
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
    print("wrote", OUT)
    for it in items:
        print(it["id"], it["cost_brl_2024"], "per L/s", it["cost_per_l_s_final_brl_2024"], "added", it["cost_per_l_s_added_brl_2024"], it.get("cost_per_l_s_final_brl_2024_ppp"))
    print("current", current_pntp, "principal", principal_pntp, "readj", readj)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
