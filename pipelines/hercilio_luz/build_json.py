"""Build data/hercilio-luz.json from the contract extract, the CNPJ records, the payments query and
facts transcribed from official documents (each with its URL).

Usage: python3 build_json.py <ponte_rows.json> <cnpj_dir> <payments.json> <out.json> [contratos.csv]
  contratos.csv: needed for related records outside the base filter (DL-00001/2618-2019)
  ponte_rows.json: output of filter_contracts.py
  cnpj_dir: folder with <cnpj>.mr.json files (minhareceita.org, Receita open data, release 2026-09)
  payments.json: output of payments.py
"""
import json
import os
import sys

COLLECTED = "2026-09-29"
CSV_URL = "https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/ff7c3cac-3e38-4801-9fd8-e4ccb69ca31d/download/contratos.csv"
IDS = ["PJ-00170/2006", "PJ-00170/2006/PROSUL", "PJ-00264/2008", "PJ-00204/2014", "PJ-00012/2015",
       "PJ-00143/2015", "PJ-00001/2016/FARES", "PJ-00056/2016", "PJ-00093/2016", "PJ-00009/2019",
       "CT-00006/2019", "PJ-00060/2019", "CT-00026/2019"]
RELATED = ["DL-00001/2618-2019"]

DOE = {
    "18501": "https://acervo.arquivopublico.sc.gov.br/uploads/r/arquivo-publico-do-estado-de-santa-catarina-apesc/2/0/a/20aeb6bb94c901d551291669cdafd8ffcc4666ee096d1c9a171a01ac460b213f/f834b399-2a11-48ee-a8d5-ae5064bc61a3-14634-DOE_18501_02_12_2008_484F.pdf",
    "20010": "https://portal.doe.sea.sc.gov.br/repositorio/2015/20150227/Jornal/1129.pdf",
    "20260": "https://portal.doe.sea.sc.gov.br/repositorio/2016/20160316/Jornal/1383.pdf",
    "20278": "https://portal.doe.sea.sc.gov.br/repositorio/2016/20160414/Jornal/1401.pdf",
    "20283": "https://portal.doe.sea.sc.gov.br/repositorio/2016/20160425/Jornal/1406.pdf",
}
TCE_DLC462 = "http://consulta.tce.sc.gov.br/relatoriosdecisao/relatoriotecnico/3728501.PDF"
TCE_MPC = "https://consulta.tce.sc.gov.br/RelatoriosDecisao/Pareceres/4533480.HTM"
DOTC_2015 = "https://consulta.tce.sc.gov.br/Diario/dotc-e2015-12-04.pdf"
DOTC_2017A = "https://consulta.tce.sc.gov.br/Diario/dotc-e2017-11-06.pdf"
DOTC_2017B = "https://consulta.tce.sc.gov.br/Diario/dotc-e2017-12-01.pdf"
DOTC_2025 = "https://consulta.tce.sc.gov.br/Diario/dotc-e2025-08-19.pdf"
ALESC_CPI = "https://agenciaal.alesc.sc.gov.br/index.php/noticia_single/aprovado-relatorio-final-da-cpi-da-ponte-hercilio-luz"
ALESC_DA7566 = "https://www.alesc.sc.gov.br/wp-content/uploads/diarios/7566dia.pdf"
MPSC_ACP = "https://www.mpsc.mp.br/w/noticias/-ponte-hercilio-luz-mpsc-requer-devolucao-de-r-23367-milhoes-por-obra-nao-concluida"
MPSC_IC = "https://www.mpsc.mp.br/w/noticias/inquerito-civil-apura-andamento-de-reforma-da-ponte-hercilio-luz"
MEM = "https://memoriapolitica.alesc.sc.gov.br/biografia/"

SIGNATURES = {
    "PJ-00264/2008": {"state_signatory": "Romualdo Theophanes de França Júnior", "state_signatory_text": "Sr. Romualdo Theophanes de França Júnior pelo DEINFRA",
                      "contractor_signatories": ["Paulo Ney Almeida"], "contractor_signatory_text": "o Sr. Paulo Ney Almeida, pelo consórcio",
                      "act": "Extrato de Termo de Contrato PJ.264/2008 (Florianópolis, 27.11.2008)",
                      "source": {"doc": "DOE-SC nº 18.501, 2008-12-02, página 462 (cópia do Arquivo Público do Estado)", "url": DOE["18501"]}},
    "PJ-00012/2015": {"state_signatory": "Wanderley Teodoro Agostini", "state_signatory_text": "Wanderley Teodoro Agostini, pelo DEINFRA",
                      "contractor_signatories": ["João Pedro Carrilho Calado", "José Luís Batista Silva"], "contractor_signatory_text": "os Srs. João Pedro Carrilho Calado e José Luís Batista Silva, pela contratada",
                      "act": "Dispensa de Licitação nº 002/2015, PJ. 012/2015 (Florianópolis, 25.02.2015)",
                      "source": {"doc": "DOE-SC nº 20.010, 2015-02-27, página 321", "url": DOE["20010"]}},
    "PJ-00056/2016": {"state_signatory": "Wanderley Teodoro Agostini", "state_signatory_text": "Wanderley Teodoro Agostini, pelo DEINFRA",
                      "contractor_signatories": ["José Luís Batista Silva", "João Pedro Carrilho Calado Antunes Lopes"], "contractor_signatory_text": "o Sr. José Luís Batista Silva e João Pedro Carrilho Calado Antunes Lopes, pela contratada",
                      "act": "Dispensa de Licitação nº 001/2016, PJ. 056/2016 (Florianópolis, 10.03.2016); fundamentação impressa: Artigo 24, inciso XV da Lei nº 8.663 [sic]",
                      "source": {"doc": "DOE-SC nº 20.283, 2016-04-25, página 21", "url": DOE["20283"]}},
}


def brl_float(x):
    return float(x) if x not in (None, "") else None


def read_from_csv(csv_path, number):
    import csv
    csv.field_size_limit(10**9)
    with open(csv_path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["NUCONTRATO"] == number:
                return r
    return None


def main(rows_path, cnpj_dir, pay_path, out, csv_path=None):
    rows = json.load(open(rows_path))
    by_id = {r["NUCONTRATO"]: r for r in rows}
    contracts = []
    for cid in IDS + RELATED:
        r = by_id.get(cid)
        if r is None and csv_path:
            r = read_from_csv(csv_path, cid)
        if r is None:
            raise SystemExit(f"missing {cid}")
        c = {
            "number": cid,
            "group": "restoration_2006_2019" if cid in IDS else "related_record_outside_original_filter",
            "object": " ".join((r["OBJETO"] or "").split()),
            "contractor_name_in_record": r["CONTRATADO"],
            "contractor_cnpj": r["IDCONTRATADO"].zfill(14),
            "managing_unit": {"code": r["CDUNIDADEGESTORA"], "name": r["NMUNIDADEGESTORA"]},
            "signed_on": r["DTASSINATURA"][:10],
            "start": (r["DTINICIO"] or "")[:10] or None,
            "end_original": (r["DTFIM"] or "")[:10] or None,
            "end_current": (r["DTFIMATUAL"] or "")[:10] or None,
            "value_original_brl": brl_float(r["VLORIGINAL"]),
            "value_current_brl": brl_float(r["VLATUAL"]),
            "value_amended_sicop_brl": brl_float(r["VLADITADO"]),
            "status_in_record": r["SITUACAO"],
            "process_sgpe": r["NUPROCESSO"] or None,
            "sicop_inspector_field_raw": r["NMFISCAL"] or None,
            "sicop_inspector_field_warning": "Campo NMFISCAL ('Nome do Fiscal do Contrato'). Mistura nomes do Estado e da contratada; não usar como lista de servidores.",
            "source": {"doc": "Registro de contratos SIGEF/SICOP, CGE-SC, dados.sc.gov.br", "url": CSV_URL, "collected_on": COLLECTED},
        }
        if cid in SIGNATURES:
            c["signing"] = SIGNATURES[cid]
        if cid == "PJ-00170/2006" or cid == "PJ-00170/2006/PROSUL":
            c["note"] = "Uma linha por empresa do Consórcio Prosul-Concremat (TCE-SC, Relatório DLC 462/2012, item 2.7). Valor inicial do contrato segundo o TCE-SC: R$ 9.811.282,66 (soma das duas linhas)."
        if cid == "PJ-00056/2016":
            c["note"] = "Unidade gestora 530001 no registro, unidade fiscalizadora 530025 (DEINFRA). Aprovação da dispensa: Resolução CA nº 0049/2016 do DEINFRA (DOE-SC nº 20.260). Fiscais designados pela Portaria DEINFRA nº 103/2016 (DOE-SC nº 20.278)."
        if cid == "DL-00001/2618-2019":
            c["note"] = "Não entrou no filtro original porque o texto diz 'PHL'. Citado pelo TCE-SC na Decisão 928/2025."
        contracts.append(c)

    companies = []
    for cnpj in sorted({c["contractor_cnpj"] for c in contracts}):
        f = os.path.join(cnpj_dir, f"{cnpj}.mr.json")
        d = json.load(open(f))
        comp = {
            "cnpj": cnpj, "legal_name": d.get("razao_social"), "trade_name": d.get("nome_fantasia") or None,
            "legal_nature": d.get("natureza_juridica"), "city": f"{d.get('municipio')}/{d.get('uf')}",
            "registration_status": d.get("descricao_situacao_cadastral"), "registration_status_date": d.get("data_situacao_cadastral"),
            "head_or_branch": d.get("descricao_identificador_matriz_filial"),
            "contracts": [c["number"] for c in contracts if c["contractor_cnpj"] == cnpj],
            "source": {"doc": "Base aberta do CNPJ da Receita Federal, release 2026-09, lida via espelho minhareceita.org (servidor oficial inacessível do exterior)",
                       "url": f"https://minhareceita.org/{cnpj}", "collected_on": COLLECTED},
        }
        if d.get("codigo_natureza_juridica") == 2151:
            comp["consortium_members_receita"] = [
                {"name": s.get("nome_socio"), "qualification": s.get("qualificacao_socio"), "since": s.get("data_entrada_sociedade")}
                for s in d.get("qsa") or [] if "Consorciad" in (s.get("qualificacao_socio") or "")]
            comp["consortium_members_tce_2012"] = {
                "text": "O primeiro, denominado Florianópolis Monumento, formado pelas empresas CSA Group Inc. e Construtora Espaço Aberto Ltda.",
                "context": "Composição na licitação de 2008; o mesmo relatório diz que o Segundo Termo Aditivo, de 19/06/2009, 'alterou o CNPJ do Consórcio'.",
                "source": {"doc": "TCE-SC, Relatório DLC 462/2012, itens 2.5 e 2.6", "url": TCE_DLC462}}
            comp["member_cnpjs"] = {"CASTOR CONSTRUTORA E INCORPORADORA LTDA": "76601343000173", "CSA GERENCIAMENTO LTDA.": "10680332000118"}
        companies.append(comp)
    companies.append({
        "cnpj": None, "legal_name": "Consórcio Prosul-Concremat (sem CNPJ próprio no registro)",
        "contracts": ["PJ-00170/2006", "PJ-00170/2006/PROSUL"],
        "consortium_members_tce_2012": {"text": "Consórcio Prosul - Projetos, Supervisão e Planejamento Ltda. / Concremar [sic] Engenharia e Tecnologia S.A.",
                                        "source": {"doc": "TCE-SC, Relatório DLC 462/2012, item 2.7", "url": TCE_DLC462}}})

    officials = [
        {"name": "Romualdo Theophanes de França Júnior", "role": "Presidente do DEINFRA", "body": "Departamento Estadual de Infraestrutura (DEINFRA)",
         "period": "no cargo em 2007-12-12 (Decisão TCE-SC 4067/2007) e em 2008-11-27 (assinatura do PJ-264/2008); datas de nomeação não encontradas",
         "source": [{"doc": "DOE-SC nº 18.501, p. 462", "url": DOE["18501"]}, {"doc": "TCE-SC, Relatório DLC 462/2012, item 2.5", "url": TCE_DLC462}],
         "signed": ["PJ-00264/2008"]},
        {"name": "Paulo Roberto Meller", "role": "Diretor Presidente do DEINFRA", "body": "DEINFRA",
         "period": "no cargo em 2012-08-02 (Relatório DLC 462/2012); datas de nomeação não encontradas",
         "source": [{"doc": "TCE-SC, Relatório DLC 462/2012, cabeçalho e item 3.2", "url": TCE_DLC462}], "signed": []},
        {"name": "Wanderley Teodoro Agostini", "role": "Presidente do DEINFRA (signatário pelo DEINFRA)", "body": "DEINFRA",
         "period": "aparece no cargo em atos datados de 2015-02-25 a 2016-04-05; datas de nomeação não encontradas",
         "source": [{"doc": "DOE-SC nº 20.010, p. 321", "url": DOE["20010"]}, {"doc": "DOE-SC nº 20.260, p. 19 (Resolução CA 0049/2016)", "url": DOE["20260"]},
                    {"doc": "DOE-SC nº 20.278, p. 11 (Portaria 103/2016)", "url": DOE["20278"]}, {"doc": "DOE-SC nº 20.283, p. 21", "url": DOE["20283"]}],
         "signed": ["PJ-00012/2015", "PJ-00056/2016"]},
        {"name": "Nelson Luiz Giorno Picanço", "role": "Consultor Executivo do DEINFRA", "body": "DEINFRA", "period": "papel registrado no Acórdão TCE-SC 0788/2015",
         "source": [{"doc": "DOTC-e nº 1845, 2015-12-04, p. 3", "url": DOTC_2015}], "signed": [],
         "note": "Falecido em 2015-11-19 segundo o parecer MPC/47.675/2017; multas canceladas pelo Acórdão 0635/2017."},
        {"name": "Wenceslau Jerônimo Diotallévy", "role": "Fiscal das Obras de restauração da Ponte Hercílio Luz (engenheiro do DEINFRA); coordenador da equipe de fiscalização do PJ-56/2016", "body": "DEINFRA",
         "period": "papel registrado no Acórdão 0788/2015 (fatos de 2008 a 2014) e na Portaria DEINFRA 103/2016 (2016-04-05)",
         "source": [{"doc": "DOTC-e nº 1845, p. 3", "url": DOTC_2015}, {"doc": "DOE-SC nº 20.278, p. 11", "url": DOE["20278"]}], "signed": []},
        {"name": "Lyana Carrilho Cardoso", "role": "Assistente Jurídica do DEINFRA", "body": "DEINFRA", "period": "papel registrado no Acórdão 0788/2015",
         "source": [{"doc": "DOTC-e nº 1845, p. 3", "url": DOTC_2015}], "signed": []},
    ]
    for n in ["Alvaro Alecio Ferreira", "Celio Aleatar da Silva", "Adolar Ferreira Filho", "Marcos Rogerio de Souza", "Samuel Tito Inacio", "Acacio Garibaldi S. Thiago Filho"]:
        officials.append({"name": n, "role": "Servidor designado para fiscalizar o PJ-56/2016 (Portaria DEINFRA nº 103, de 05/04/2016)", "body": "DEINFRA",
                          "period": "a partir de 2016-04-05", "source": [{"doc": "DOE-SC nº 20.278, p. 11", "url": DOE["20278"]}], "signed": [],
                          "display_recommendation": "baixa prioridade: papel técnico, sem achado associado"})

    governors = [
        {"name": "Luiz Henrique da Silveira", "start": "2003-01-01", "end": "2006-04-09", "condition": "titular, 1º mandato", "source": MEM + "638-Luiz_Henrique_da_Silveira"},
        {"name": "Eduardo Pinho Moreira", "start": "2006-04-09", "end": "2006-07-06", "condition": "interino (vice-governador)", "source": MEM + "1158-Eduardo_Pinho_Moreira"},
        {"name": "Pedro Manoel Abreu", "start": "2006-07-07", "end": "2006-07-14", "condition": "temporário (presidente do Tribunal de Justiça), segundo a biografia de Eduardo Pinho Moreira", "source": MEM + "1158-Eduardo_Pinho_Moreira"},
        {"name": "Eduardo Pinho Moreira", "start": "2006-07 (depois de 14/07)", "end": "2006-12-31", "condition": "efetivado", "source": MEM + "1158-Eduardo_Pinho_Moreira"},
        {"name": "Luiz Henrique da Silveira", "start": "2007-01-01", "end": "2010-03-25", "condition": "titular, 2º mandato; deixou o cargo para disputar o Senado", "source": MEM + "638-Luiz_Henrique_da_Silveira"},
        {"name": "Leonel Pavan", "start": "2010-03-25", "end": "2010-12-31", "condition": "vice-governador que assumiu", "source": MEM + "960-Leonel_Pavan"},
        {"name": "Raimundo Colombo", "start": "2011-01-01", "end": "2018-04-05", "condition": "titular, dois mandatos; renunciou em 2018-04-05", "source": MEM + "480-Raimundo_Colombo",
         "note": "A biografia registra só os anos 2011-2014 e 2015-2018; 2011-01-01 é a data de posse fixada pela Constituição Federal, art. 28 (redação da época)."},
        {"name": "Eduardo Pinho Moreira", "start": "2018-04-06", "end": "2018-12-31", "condition": "titular (posse na Alesc); já estava 'em exercício' antes dessa data, início não confirmado", "source": MEM + "1158-Eduardo_Pinho_Moreira",
         "source_2": "https://agenciaal.alesc.sc.gov.br/index.php/noticia_single/eduardo-pinho-moreira-toma-posse-como-governador-titular-em-solenidade-na-a"},
        {"name": "Carlos Moisés da Silva", "start": "2019-01-01", "end": "2023-01-01", "condition": "titular", "source": MEM + "1308-Carlos_Moises"},
    ]
    governors_note = "Partido omitido (regra do projeto). Substituições curtas por viagem ou licença não listadas. O governador não assina os contratos: nos extratos lidos, assina o dirigente do DEINFRA."

    pay = json.load(open(pay_path))
    payments = {
        "source": {"doc": "Portal da Transparência do Poder Executivo de SC, consulta Fornecedores (SIGEF, Secretaria de Estado da Fazenda)",
                   "url": "https://www.transparencia.sc.gov.br/fornecedores", "api": pay["api"], "collected_on": COLLECTED,
                   "script": "pipelines/hercilio_luz/payments.py"},
        "coverage": "2011 em diante (2008 a 2010 vazios no Portal)",
        "fields": {"vlbruto": "Valor bruto recebido pelo credor", "vlretido": "Valor retido", "vlliquido": "valor líquido (campo do Portal)",
                   "vlestorno": "Valor estornado (valor devolvido)"},
        "caveats": [
            "Pagamento ao credor, não ao contrato: inclui outros contratos da mesma empresa com o Poder Executivo.",
            "Não se sabe pelo dicionário se vlbruto já desconta vlestorno; os dois são mostrados separados.",
            "Valores nominais.",
            "Prosul: 114 contratos no registro; o total não se refere à ponte.",
        ],
        "companies": [],
        "official_pre2011_figure": {
            "company_cnpj": "10769406000197",
            "quote": "o último pagamento ocorreu em maio do corrente ano, referente aos meses de janeiro a março de 2012, acumulando R$ 38.921.239,05 e medições até junho de 2012, com saldo a pagar de R$ 1.595.516,86",
            "context": "Extrato do SICOP 'atualizado em julho de 2012', citado pelo TCE-SC; acumulado desde 2008",
            "source": {"doc": "TCE-SC, Relatório DLC 462/2012, item 2.6", "url": TCE_DLC462}},
    }
    for c in pay["companies"]:
        payments["companies"].append({
            "cnpj": c["cnpj"], "portal_creditor_ids": c["credor_ids"], "portal_creditor_names": c["credor_names"],
            "by_year": [{"year": r["year"], "all_units": r["all_units"], "unit_530025_DEINFRA": r["ug_530025_DEINFRA"] or {},
                         "unit_530001_SIE": r["ug_530001_SIE"] or {}, "query_url_all_units": r["url_all_units"]} for r in c["by_year"]],
            "total_gross_all_units_computed": round(sum(float(r["all_units"].get("vlbruto") or 0) for r in c["by_year"]), 2),
            "total_reversed_all_units_computed": round(sum(float(r["all_units"].get("vlestorno") or 0) for r in c["by_year"]), 2),
        })

    findings = [
        {"body": "TCE-SC", "process": "ELC 07/00582703", "date": "2007-12-12 e 2008-03-19",
         "summary_quote": "Decisão 4067/2007: 'Determinar, cautelarmente [...] que promova a sustação do procedimento licitatório'. Decisão 0594/2008: 'Conhecer do Edital de Concorrência Pública n. 044/2007 [...] considerando seus termos em consonância com as determinações do art. 40 da Lei Federal n. 8.666/93'.",
         "status": "encerrado; lido na transcrição do Relatório DLC 462/2012", "url": TCE_DLC462},
        {"body": "TCE-SC", "process": "RLA 12/00285490 (Acórdão 0788/2015)", "date": "2015-11-04 (sessão); 2015-12-04 (publicação)",
         "summary_quote": "Aplicar aos Responsáveis [...] as multas adiante relacionadas; por exemplo, 'por permitir que o Contrato n. PJ-264/2008 (restauração da ponte) sofresse acréscimo de 50,29% e supressão de 44,78% do seu valor por meio de Termos Aditivos, extrapolando o limite permitido no art. 65, §1º, da Lei n. 8.666/93'.",
         "status": "julgado com multas; alterado em recurso (ver Acórdãos 0632 a 0636/2017)", "url": DOTC_2015,
         "fines_original_brl": {"Paulo Roberto Meller": 24200.00, "Romualdo Theophanes de França Júnior": 24200.00, "Nelson Luiz Giorno Picanço": 11200.00,
                                "Wenceslau Jerônimo Diotallévy": 13000.00, "Lyana Carrilho Cardoso": 5000.00},
         "fines_note": "Somas calculadas a partir dos itens do acórdão.",
         "technical_report": {"doc": "Relatório DLC 462/2012 (preliminar)", "url": TCE_DLC462}},
        {"body": "TCE-SC", "process": "REC 16/00030243, 16/00030324, 16/00030405, 16/00030596, 16/00030677 (Acórdãos 0632 a 0636/2017)", "date": "2017-11-01 (sessão); 2017-12-01 (publicação)",
         "summary_quote": "0632/2017: 'dar-lhe provimento parcial para: 6.1.1. cancelar a multa estabelecida no subitem 6.2.4.1'; 0633/2017 e 0634/2017: 'negar-lhe provimento, ratificando na íntegra a deliberação recorrida'; 0635/2017: 'tornar insubsistentes os itens 6.2.3.1, 6.2.3.2 e 6.2.3.3 [...] cancelando as multas aplicadas'; 0636/2017: 'cancelar a multa estabelecida no subitem 6.2.1.2'.",
         "status": "decidido no TCE-SC após recurso; pagamento ou contestação judicial não verificados", "url": DOTC_2017B,
         "fines_after_appeal_brl_computed": {"Paulo Roberto Meller": 19200.00, "Romualdo Theophanes de França Júnior": 24200.00, "Nelson Luiz Giorno Picanço (espólio)": 0.00,
                                             "Wenceslau Jerônimo Diotallévy": 8000.00, "Lyana Carrilho Cardoso": 5000.00}},
        {"body": "TCE-SC", "process": "REP 14/00346689 (Acórdão 0585/2017)", "date": "2017-10-04 (sessão); 2017-11-06 (publicação)",
         "summary_quote": "Julgar procedente a Representação [...]. Aplicar ao Sr. Romualdo Theophanes de França Júnior - ex-Presidente do Departamento Estadual de Infraestrutura - DEINFRA [...] a multa no valor de R$ 1.136,52 [...] em face da omissão no poder-dever de fiscalização em relação à apresentação do 'Seguro de Riscos de Engenharia' pelo Consórcio Florianópolis Monumento, junto ao Termo de Contrato n. PJ 264/2008",
         "status": "julgado; recurso não verificado", "url": DOTC_2017A},
        {"body": "Alesc (CPI, Ato 0030-DL/2019)", "process": "CPI da Ponte Hercílio Luz", "date": "2019-12-18",
         "summary_quote": "O relatório aprovado suprime a palavra 'indiciamento' e a substitui por encaminhamento para apurar possíveis ilicitudes e o documento será encaminhado ao Ministério Público junto ao Tribunal de Contas (MPTC), Ministério Público (MP) e Tribunal de Contas do Estado (TCE).",
         "amounts_quote": "para que sejam analisadas possíveis irregularidades de R$ 24,6 milhões aos cofres públicos por parte do Consórcio Florianópolis Movimento [sic], de R$ 12,2 milhões pela Usimec (referente a contrato de 1982) e de outros R$ 5,2 milhões pela contratação da Steimann, em 1993.",
         "persons_cited_heading": "Pessoas citadas no relatório final da CPI",
         "persons_cited": ["Raul Ozório de Almeida", "Telmo Fernando Mattar de Souza", "Tolstói Maia Duarte", "Sidney Lourenço Dal Sasso", "Hubert Beck Júnior",
                           "Roberto Alexandre Zattar", "Paulo Ney Almeida", "Marcos Amin", "Luiz Antônio Ramos", "Justiniano Pedroso", "Olívio Karasek Rocha",
                           "Eduardo Hamond Régua", "Raimundo Colombo", "Paulo Meller", "Wenceslau Jerônimo Diotallévy", "Wilfredo Brillinger",
                           "Celso Magalhães Carvalho", "Romualdo Theophanes de França Junior", "Dalmo Pickler Baesso", "Ricardo Bridon Soares"],
         "companies_cited_heading": "Empresas citadas no relatório",
         "companies_cited": ["Construtora Roca", "TEC - Técnica de Engenharia Catarinense", "Prosul", "Construtora Espaço Aberto", "Consórcio Florianópolis Monumento", "CSA Group Florida e CSA"],
         "display_recommendation": "não exibir as listas de nomes até ler o relatório integral: a nota não liga cada nome a um fato; cobre fatos desde 1982",
         "status": "CPI encerrada; encaminhamento a MPTC, MP e TCE (não é acusação nem condenação); relatório integral não acessado", "url": ALESC_CPI,
         "related_minutes": {"doc": "Diário da Assembleia nº 7.566 (ata da 31ª reunião; texto do relatório depois rejeitado)", "url": ALESC_DA7566}},
        {"body": "TCE-SC", "process": "@REP 15/00524643 (Decisão 928/2025)", "date": "2025-08-08 (sessão); 2025-08-19 (publicação)",
         "summary_quote": "1. Reconhecer, de ofício, a prescrição das pretensões punitiva e ressarcitória deste Tribunal [...] em relação aos seguintes Contratos: [...] PJ 170/2006 [...] PJ 264/2008 [...] PJ 204/2014 [...] PJ 12/2015 e PJ 143/2015 [...] PJ 001/2016 [...] PJ 93/2016 [...] PJ 009/2019 [...] CT 026/2019, PJ 060/2019 e DL-00001/2618-2019 [...]. 2. [...] formação de autos apartados [...] Processo 1 - RMG Engenharia: Contrato CT 006/2019 [...] Processo 2 - Teixeira Duarte e EMPA: Contrato PJ 056/2016 [...]. 3. Julgar improcedente a Representação quanto ao Contrato PJ 046/90 [...]. 7. Determinar o arquivamento dos autos.",
         "status": "arquivado; prescrição reconhecida (sem julgamento de mérito sobre os contratos prescritos); dois processos novos determinados (PJ 056/2016 e CT 006/2019), número e andamento não encontrados",
         "url": DOTC_2025},
        {"body": "MPSC (26ª Promotoria de Justiça da Capital)", "process": "Ação civil pública por atos de improbidade administrativa (número não encontrado)", "date": "2018-12-17",
         "summary_quote": "A ação civil pública por atos de improbidade administrativa com pedido de ressarcimento de R$ 233.675.518,92 aos cofres públicos foi ajuizada, no final da tarde de segunda-feira (17/12)",
         "defendants_count_quote": "contra 12 envolvidos - oito com atuação no Departamento Estadual de Infraestrutura (Deinfra) e quatro empresas",
         "display_recommendation": "não exibir a lista de réus sem decisão judicial localizada",
         "status": "ajuizada; última informação oficial lida (2018-12-18): 'sob análise do Juiz de Direito da Vara da Fazenda Pública da comarca da Capital'; resultado judicial não encontrado",
         "url": MPSC_ACP},
        {"body": "MPSC (30ª Promotoria de Justiça da Capital)", "process": "Inquérito civil (número não informado)", "date": "2012-03-14 (notícia)",
         "summary_quote": "instaurou inquérito civil para apurar o andamento das obras de recuperação da Ponte Hercílio Luz",
         "status": "instaurado; desfecho não encontrado", "url": MPSC_IC},
    ]

    data = {
        "work": "Restauração da Ponte Hercílio Luz (Florianópolis, SC)",
        "collected_on": COLLECTED,
        "report": "docs/research/BRASIL-IMPOSTO_RESEARCH_ponte-hercilio-luz-responsaveis_2026-09-29.md",
        "rules": "Somente papéis e achados oficiais, com as palavras do órgão. Nenhuma inferência de irregularidade. Valores nominais, com fonte e data de coleta. Somas marcadas como computed/calculated são desta pesquisa.",
        "contracts_totals_computed": {
            "restoration_2006_2019_count": len(IDS),
            "value_original_brl": round(sum(c["value_original_brl"] for c in contracts if c["group"] == "restoration_2006_2019"), 2),
            "value_current_brl": round(sum(c["value_current_brl"] for c in contracts if c["group"] == "restoration_2006_2019"), 2)},
        "contracts": contracts,
        "companies": companies,
        "officials": officials,
        "governors": governors,
        "governors_note": governors_note,
        "payments": payments,
        "findings": findings,
        "terms_check": "Nenhum documento oficial lido usa 'superfaturamento' ou 'sobrepreço'.",
    }
    json.dump(data, open(out, "w"), ensure_ascii=False, indent=1)
    print("ok", len(contracts), len(companies), len(officials), len(findings))


if __name__ == "__main__":
    main(*sys.argv[1:6])
