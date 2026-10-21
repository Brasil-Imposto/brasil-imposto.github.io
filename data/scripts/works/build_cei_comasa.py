"""Build data/works/cei-comasa-joinville.json (CEI Manoel Antonio da Rosa, antigo CEI Rio Negro, Joinville).

Inputs (one working directory outside the repository):
    bash download.sh                                        # IPCA + World Bank
    python3 joinville_payments.py jlle 03.184.733/0001-11 366/2023 2023-02 2026-09 2023 2024 2025 2026
    python3 joinville_gazette_scan.py jgazette 42 45 "366/2023" "Rio Negro" > jgazette_scan.log
    python3 joinville_gazette_scan.py jgazette2 16 41 "Contrato n.{0,3}\\s*366/2023" > jgazette_scan2_p16_41.log
    (any number of logs named jgazette_scan2_*.log are read; for each act the longest passage is kept)
    python3 cnpj_fetch.py cnpj2 03184733000111
    contract API files jc_api_<year>.json (see joinville_payments.py, contrato endpoint) for 2023 to 2026
    PNCP records of the comparables in pncp/<name>.json (pncp.gov.br/api/pncp/v1/orgaos/<cnpj>/contratos/<ano>/<seq>)
    sinapi_m2.json: https://apisidra.ibge.gov.br/values/t/2296/n3/42,31,50,43/v/48/p/202301-202608?formato=json
    tse/consulta_cand_<year>_SC.csv from https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_<year>.zip
    python3 build_cei_comasa.py .
"""
import collections
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from convert import Converter, no_dashes  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "data", "works", "cei-comasa-joinville.json")
COLLECTED = "2026-09-30"
API = "https://transparencia.joinville.sc.gov.br/epublica-portal/rest/joinville/api/v1"
CONTRACT = "366/2023"
CNPJ = "03.184.733/0001-11"
NEWS = {
    "inauguration": "https://www.joinville.sc.gov.br/noticias/prefeitura-de-joinville-inaugura-primeiro-mega-centro-de-educacao-infantil-com-capacidade-para-ate-600-criancas/",
    "second_mega": "https://www.joinville.sc.gov.br/noticias/com-investimento-de-r-19-milhoes-prefeitura-de-joinville-inaugura-mega-centro-de-educacao-infantil-no-bairro-vila-cubatao/",
    "program_226": "https://www.joinville.sc.gov.br/noticias/prefeitura-de-joinville-investe-r-226-milhoes-na-construcao-de-15-novos-centos-de-educacao-infantil/",
    "comasa_vagas": "https://www.joinville.sc.gov.br/noticias/educacao-de-joinville-divulga-primeiro-quadro-de-vagas-para-novo-cei-no-bairro-comasa/",
    "os_contract": "https://www.joinville.sc.gov.br/noticias/prefeitura-de-joinville-assina-contrato-para-gestao-do-cei-manoel-antonio-da-rosa/",
}
MPSC = {
    "tac_2023": "https://www.mpsc.mp.br/w/noticias/mpsc-e-municipio-de-joinville-firmam-acordo-para-zerar-filas-de-espera-na-educacao-infantil-",
    "rec_2026": "https://www.mpsc.mp.br/w/recomenda%C3%A7%C3%A3o-do-mpsc-requer-mudan%C3%A7as-na-fila-de-creches-em-joinville",
}
FNDE_MANUAL = "https://www.fnde.gov.br/phocadownload/programas/pro_infancia/cheche-tipo-1/proinfancia_tipo_1-2_manual-reformulacao-mi-convencional.pdf"
SINAPI_URL = "https://apisidra.ibge.gov.br/values/t/2296/n3/42,31,50,43/v/48/p/202301-202608?formato=json"
MONTHS = {m: i for i, m in enumerate(["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"], 1)}


def parse_scan(path):
    """Return passages from a joinville_gazette_scan.py log, with edition number and date."""
    out = []
    text = "\n" + open(path, encoding="utf-8", errors="ignore").read()
    for block in text.split("\n== ")[1:]:
        head, body = block.split("\n", 1)
        m = re.search(r"(https://\S+\.pdf) \| .*?Nº (\d+), \S+, (\d+) de (\S+) de (\d{4})", head)
        if not m:
            continue
        mon = MONTHS.get(m.group(4).lower().replace("Ã§", "ç"), None)
        date = f"{m.group(5)}-{mon:02d}-{int(m.group(3)):02d}" if mon else None
        out.append({"pdf": m.group(1), "edition": int(m.group(2)), "date": date, "text": body.split("\npage ")[0]})
    return out


def clip(s, start, end_markers=("Documento assinado", "A autenticidade", "Justifica-se")):
    s = s[start:]
    cut = min([s.find(e) for e in end_markers if s.find(e) > 0] or [len(s)])
    return " ".join(s[:cut].split())


def main(work):
    conv = Converter(work)
    # ---------------------------------------------------------------- contract register (open-data API)
    reg = None
    program = []
    for y in (2023, 2024, 2025, 2026):
        d = json.load(open(os.path.join(work, f"jc_api_{y}.json")))
        for r in d["registros"]:
            rr = r["registro"]
            c = rr["contrato"]
            o = c["objetoResumido"].upper()
            if c["numero"] == CONTRACT:
                reg = rr
            if ("EDUCAÇÃO INFANTIL" in o or re.search(r"\bCEI\b", o)) and "CONSTRU" in o and (c["valorTotal"] or 0) > 3e6:
                program.append({"number": c["numero"], "signed_on": c["assinatura"], "value_original_brl": c["valorTotal"],
                                "company": rr["fornecedor"]["pessoa"]["nome"], "company_cnpj": rr["fornecedor"]["pessoa"].get("cpfCnpj"),
                                "object": " ".join(c["objetoResumido"].split())})
    assert reg is not None
    program.sort(key=lambda x: x["signed_on"])

    # ---------------------------------------------------------------- gazette passages
    g1 = parse_scan(os.path.join(work, "jgazette_scan.log"))
    g2 = []
    for name in sorted(os.listdir(work)):
        if name.startswith("jgazette_scan2_") and name.endswith(".log"):
            g2 += parse_scan(os.path.join(work, name))
    acts = {}
    for p in g1 + g2:
        t = p["text"]
        for m in re.finditer(r"Extrato d[oa] (?:(\d+)[º°] )?(Termo Aditivo|Apostilamento|Termo de Contrato)(?:[^.]{0,40}?Contrato)? n[º°]\s*366/2023", t):
            kind = m.group(2)
            num = m.group(1) or "0"
            passage = clip(t, m.start())
            if kind == "Termo de Contrato" and "807/2022" not in passage:
                continue  # the extract of contract 364/2023 printed with the wrong number (corrected by errata)
            key = (kind, num)
            if key not in acts or len(passage) > len(acts[key]["text"]):
                acts[key] = {"act": ("Extrato do Termo de Contrato" if kind == "Termo de Contrato" else f"{num}º {kind}"),
                             "gazette_edition": p["edition"], "gazette_date": p["date"], "gazette_pdf": p["pdf"], "text": passage}
        mp = re.search(r"Fiscalização do Contrato nº 366/2023.{0,400}?I [\u2013-] Titulares: .*? II [\u2013-] Suplentes: .*?(?= Art\. 2)", t)
        if mp and ("Portaria", "0") not in acts:
            acts[("Portaria", "0")] = {"act": "Designação da comissão de fiscalização", "gazette_edition": p["edition"], "gazette_date": p["date"],
                                        "gazette_pdf": p["pdf"], "text": " ".join(mp.group(0).split())}
        j = t.find("ERRATA AO EXTRATO DE PUBLICAÇÃO")
        if j > 0 and "366/2023" in t[j:j + 1500] and ("Errata", "0") not in acts:
            acts[("Errata", "0")] = {"act": "Errata ao extrato (troca de número entre os contratos 364/2023 e 366/2023)", "gazette_edition": p["edition"],
                                      "gazette_date": p["date"], "gazette_pdf": p["pdf"], "text": " ".join(t[j:j + 1400].split())}
    ext = acts[("Termo de Contrato", "0")]
    m = re.search(r"assinado em (\d{2})/(\d{2})/(\d{4}), com a vigência de (\d+) \(\w+\) meses, no valor de R\$ ([\d.,]+)", ext["text"])
    signed_on = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    value_orig = float(m.group(5).replace(".", "").replace(",", "."))
    assert abs(value_orig - reg["contrato"]["valorTotal"]) < 0.01

    amendments, added, removed = [], 0.0, 0.0
    for key in sorted(acts, key=lambda k: (acts[k]["gazette_date"] or "", k)):
        a = acts[key]
        if key[0] not in ("Termo Aditivo", "Apostilamento"):
            continue
        t = a["text"]
        rec = {"act": a["act"], "published_in": f"Diário Oficial Eletrônico do Município de Joinville nº {a['gazette_edition']}, {a['gazette_date']}",
               "url": a["gazette_pdf"], "text": t}
        for mm in re.finditer(r"acrescendo-o (\w+) em ([\d,]+)%(?: \([^)]*\))?, equivalente ao valor de R\$ ([\d.,]+)", t):
            v = float(mm.group(3).replace(".", "").replace(",", "."))
            rec.setdefault("value_added_brl", 0.0)
            rec["value_added_brl"] += v
            added += v
        for mm in re.finditer(r"suprimindo-o em ([\d,]+)%, equivalente ao valor de R\$ ([\d.,]+)", t):
            v = float(mm.group(2).replace(".", "").replace(",", "."))
            rec["value_removed_brl"] = v
            removed += v
        mm = re.search(r"saldo contratual de R\$ ([\d.,]+) \([^)]*\) para R\$ ([\d.,]+)", t)
        if mm:
            a0 = float(mm.group(1).replace(".", "").replace(",", "."))
            a1 = float(mm.group(2).replace(".", "").replace(",", "."))
            rec["readjustment_brl_computed"] = round(a1 - a0, 2)
        amendments.append(rec)
    readjust = sum(a.get("readjustment_brl_computed", 0.0) for a in amendments)
    value_current = round(value_orig + added - removed + readjust, 2)

    # ---------------------------------------------------------------- payments (open-data API, movements per commitment)
    raw = json.load(open(os.path.join(work, "jlle", "joinville_raw.json")))
    movs = set()
    emps = {}
    for r in raw["despesa"]:
        e = r["empenho"]
        if e.get("contrato") != CONTRACT:
            continue
        ex = r["exercicio"]["exercicio"]
        emps[(e["numero"], ex)] = {"number": e["numero"], "fiscal_year": ex, "issued": e["emissao"], "type": e["especie"],
                                   "action": r["despesa"]["acao"]["denominacao"], "function": r["despesa"]["funcao"]["denominacao"],
                                   "subfunction": r["despesa"]["subfuncao"]["denominacao"], "source_of_funds": r["fonteRecurso"]["denominacao"]}
        for mv in r.get("listMovimentos") or []:
            movs.add((e["numero"], ex, mv["dataMovimento"], mv["tipoMovimento"], round(mv["valorMovimento"], 2)))
    by_year = collections.defaultdict(lambda: collections.Counter())
    by_month = collections.Counter()
    for (_, _, dt, tp, v) in movs:
        by_year[dt[:4]][tp] += v
        if tp.startswith("Pagamento"):
            by_month[dt[:7].replace("-", "")] += v
        if tp.startswith("Retenção"):
            by_month[dt[:7].replace("-", "")] += v
        if tp.startswith("Estorno de pagamento") or tp.startswith("Estorno de retenção"):
            by_month[dt[:7].replace("-", "")] -= v
    years = []
    for y in sorted(by_year):
        a = by_year[y]
        paid = a["Pagamento de empenho"] + a["Pagamento de restos a pagar"] - a["Estorno de pagamento de empenho"]
        ret = a["Retenção de empenho"] + a["Retenção de restos a pagar"] - a["Estorno de retenção de empenho"]
        years.append({"year": int(y), "paid_to_supplier_brl": round(paid, 2), "withheld_brl": round(ret, 2),
                      "gross_brl": round(paid + ret, 2)})
    gross_total = round(sum(x["gross_brl"] for x in years), 2)
    by_source = collections.Counter()
    for (num, ex, dt, tp, v) in movs:
        src = emps[(num, ex)]["source_of_funds"]
        if tp.startswith("Pagamento") or tp.startswith("Retenção"):
            by_source[src] += v
        if tp.startswith("Estorno de pagamento") or tp.startswith("Estorno de retenção"):
            by_source[src] -= v
    assert abs(sum(by_source.values()) - gross_total) < 0.05
    paid_2024 = round(sum(v * conv.month_factor(m) for m, v in by_month.items()), 2)
    payments = {
        "source": {"doc": "API de dados abertos do Portal da Transparência de Joinville (e-Pública), despesa por mês, movimentos de cada empenho",
                   "url": f"{API}/despesa?periodo_inicial=MM/AAAA&periodo_final=MM/AAAA&codigo_unidade=0", "collected_on": COLLECTED,
                   "script": "data/scripts/works/joinville_payments.py", "months_queried": f"{raw['queries'][4]['url'].split('periodo_inicial=')[1][:7]} em diante"},
        "by_year": years,
        "total_gross_brl": gross_total,
        "total_paid_to_supplier_brl": round(sum(x["paid_to_supplier_brl"] for x in years), 2),
        "total_withheld_brl": round(sum(x["withheld_brl"] for x in years), 2),
        "total_gross_brl_2024_computed": paid_2024,
        "gross_by_source_of_funds_computed": {k: round(v, 2) for k, v in by_source.most_common()},
        "gross_vs_contract_current_computed": round(gross_total - value_current, 2),
        "gross_vs_contract_current_note": ("O bruto liquidado supera o valor atualizado calculado pelos extratos publicados. A diferença não foi explicada "
                                           "nesta coleta: edições do Diário Oficial de mar/2023 a jul/2025 foram lidas e nenhum outro aditivo ou "
                                           "apostilamento do contrato 366/2023 apareceu; um reajuste posterior não localizado é a hipótese mais simples, não verificada."),
        "definitions": {"paid_to_supplier_brl": "Soma dos movimentos 'Pagamento de empenho' e 'Pagamento de restos a pagar', menos estornos.",
                        "withheld_brl": "Retenções (tributos retidos na fonte) dos mesmos empenhos; somadas ao pago dão o valor bruto liquidado."},
        "commitments": sorted(emps.values(), key=lambda e: (e["fiscal_year"], e["number"])),
        "caveat": "Empenhos filtrados pelo campo 'contrato' = 366/2023. Os empenhos de 2023 a 2025 foram lidos nos meses em que tiveram movimento.",
    }

    # ---------------------------------------------------------------- company and people
    cj = json.load(open(os.path.join(work, "cnpj2", "03184733000111.json")))
    est = cj.get("estabelecimento") or {}
    seen, partners = set(), []
    for s in cj.get("socios") or []:
        k = s.get("nome")
        if k in seen:
            continue
        seen.add(k)
        partners.append({"name": s.get("nome"), "qualification": (s.get("qualificacao_socio") or {}).get("descricao", "").strip(), "since": s.get("data_entrada")})
    companies = [{
        "cnpj": "03184733000111", "legal_name": cj.get("razao_social"), "trade_name": est.get("nome_fantasia"),
        "legal_nature": (cj.get("natureza_juridica") or {}).get("descricao"),
        "city": f"{(est.get('cidade') or {}).get('nome')}/{(est.get('estado') or {}).get('sigla')}",
        "registration_status": est.get("situacao_cadastral"), "registration_status_date": est.get("data_situacao_cadastral"),
        "activity_start": est.get("data_inicio_atividade"), "partners": partners,
        "partners_official_text": "cujo quadro societário é formado por Alexandra Correa Gayoso Neves e Manuel Carlos Maia de Oliveira (extratos dos termos aditivos no Diário Oficial do Município)",
        "contracts": [CONTRACT, "364/2023 (outro CEI do mesmo programa)"],
        "official_website": "https://construtoraviseu.com.br/",
        "official_website_evidence": "Título 'Construtora Viseu' e endereço em Joinville, mesma cidade e nome do cadastro; o site não mostra o CNPJ.",
        "portal_transparencia_federal": "https://portaldatransparencia.gov.br/pessoa-juridica/03184733000111",
        "source": {"doc": "Base aberta do CNPJ da Receita Federal, lida via espelho " + cj["_mirror"], "url": cj["_url"], "collected_on": COLLECTED},
    }]

    tse_rows = {}
    for y in (2020, 2024):
        p = os.path.join(work, "tse", f"consulta_cand_{y}_SC.csv")
        for row in csv.DictReader(open(p, encoding="latin1"), delimiter=";"):
            if row["NM_CANDIDATO"] == "ADRIANO BORNSCHEIN SILVA":
                tse_rows[(y, row["NR_TURNO"])] = {"year": y, "office": row["DS_CARGO"], "unit": row["NM_UE"], "party": row["SG_PARTIDO"],
                                                   "result": row["DS_SIT_TOT_TURNO"], "turn": row["NR_TURNO"]}
    mayor = {"name": "Adriano Bornschein Silva (Adriano Silva)", "office": "Prefeito de Joinville",
             "terms": ["2021-2024 (eleito em 2020, 2º turno)", "2025-2028 (eleito em 2024)"],
             "party_at_time": "NOVO", "tse_records": sorted(tse_rows.values(), key=lambda r: (r["year"], r["turn"])),
             "source": "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2020.zip (e 2024)",
             "relevant_dates": ["2023-03-01 (assinatura do contrato)", "2023-05-15 (TAC com o MPSC, no gabinete do prefeito)", "2025-03-07 (inauguração)"]}
    ex_text = ext["text"]
    people = [
        {"name": "Diego Calegari Feldhaus", "role": "Secretário de Educação de Joinville; representou o Município no contrato e nos seis termos aditivos",
         "role_source": ext["gazette_pdf"], "signed": [{"act": "Termo de Contrato 366/2023", "date": signed_on, "url": ext["gazette_pdf"]}] +
         [{"act": a["act"], "date": a["published_in"].split(", ")[-1], "url": a["url"]} for a in amendments if "Termo Aditivo" in a["act"]]},
        {"name": "Manuel Carlos Maia de Oliveira", "role": "representou a Construtora Viseu Ltda no contrato e nos aditivos; sócio-administrador na Receita", "side": "contratada",
         "role_source": ext["gazette_pdf"], "signed": [{"act": "Termo de Contrato 366/2023", "date": signed_on, "url": ext["gazette_pdf"]}]},
        {"name": "Silvia Cristina Bello", "role": "Diretora Executiva; assinou eletronicamente o extrato publicado", "role_source": ext["gazette_pdf"], "signed": []},
    ]
    port = acts.get(("Portaria", "0"))
    if port:
        mm = re.search(r"I [\u2013-] Titulares: .*$", port["text"])
        people.append({"group": "Comissão de Acompanhamento e Fiscalização do Contrato nº 366/2023", "designated_by": "Secretário de Educação",
                       "members_text": mm.group(0).strip() if mm else port["text"][-400:], "published_in": f"DOE Joinville nº {port['gazette_edition']}, {port['gazette_date']}",
                       "url": port["gazette_pdf"], "note": "Servidores designados como fiscais; papel administrativo, sem qualquer achado associado."})

    # ---------------------------------------------------------------- comparison
    sinapi = {(r["D1N"], r["D3C"]): float(r["V"]) for r in json.load(open(os.path.join(work, "sinapi_m2.json")))[1:]}
    SC, MG, MS, RS = "Santa Catarina", "Minas Gerais", "Mato Grosso do Sul", "Rio Grande do Sul"
    area_j, cap_j = 2900.0, 600
    base_month = signed_on[:7].replace("-", "")
    cj_orig = conv.brl_month(value_orig, base_month)
    comp = [{
        "id": "cei-comasa", "name": "CEI Manoel Antônio da Rosa (contrato do 'CEI Rio Negro')", "place": "Joinville/SC", "is_subject": True,
        "project": "projeto próprio do Município ('uma obra pensada para ser creche, que inclusive ganhou prêmio de arquitetura', segundo o prefeito)",
        "area_m2": area_j, "capacity_two_shifts": cap_j, "capacity_note": "600 se todas as vagas fossem de um turno; atende 462 com vagas parciais e integrais",
        "contract_value_brl": value_orig, "contract_month": base_month, "conversion": cj_orig, "cost_brl_2024": cj_orig["amount_brl_2024"],
        "final_paid_gross_brl": gross_total, "final_paid_gross_brl_2024": paid_2024,
        "sinapi_uf": SC, "sinapi_m2_contract_month": sinapi[(SC, base_month)],
        "sources": [{"field": "value", "url": ext["gazette_pdf"]}, {"field": "area, capacity", "url": NEWS["inauguration"]}]}]
    fnde = {"Tipo 1": {"area_m2": 1513.16, "cap": 376, "cap_integral": 188}, "Tipo 2": {"area_m2": 895.53, "cap": 188, "cap_integral": 94}}
    for key, name, place, uf, tipo in (("itajai", "Creche Proinfância Tipo 2, Loteamento Santa Regina", "Itajaí/SC", SC, "Tipo 2"),
                                        ("araujos", "Creche Proinfância Tipo 1", "Araújos/MG", MG, "Tipo 1"),
                                        ("navirai_127", "Creche Proinfância Tipo 1, bairro Nelson Trad", "Naviraí/MS", MS, "Tipo 1"),
                                        ("caraa", "Creche Proinfância Tipo 1", "Caraá/RS", RS, "Tipo 1")):
        p = json.load(open(os.path.join(work, "pncp", f"{key}.json")))
        month = p["dataAssinatura"][:7].replace("-", "")
        cv = conv.brl_month(p["valorInicial"], month)
        comp.append({"id": key, "name": name, "place": place, "project": f"projeto padrão FNDE Proinfância {tipo}",
                     "area_m2": fnde[tipo]["area_m2"], "capacity_two_shifts": fnde[tipo]["cap"], "capacity_integral": fnde[tipo]["cap_integral"],
                     "contract_value_brl": p["valorInicial"], "contract_month": month, "company": p["nomeRazaoSocialFornecedor"], "company_cnpj": p["niFornecedor"],
                     "contract_number": p.get("numeroContratoEmpenho"), "pncp_id": p.get("numeroControlePNCP"),
                     "conversion": cv, "cost_brl_2024": cv["amount_brl_2024"], "sinapi_uf": uf, "sinapi_m2_contract_month": sinapi[(uf, month)],
                     "object": " ".join((p.get("objetoContrato") or "").split())[:260],
                     "sources": [{"field": "value", "url": f"https://pncp.gov.br/app/contratos/{p['orgaoEntidade']['cnpj']}/{p['anoContrato']}/{p['sequencialContrato']}"},
                                 {"field": "area, capacity", "url": FNDE_MANUAL}]})
    for c in comp:
        c["cost_per_place_brl_2024"] = round(c["cost_brl_2024"] / c["capacity_two_shifts"], 2)
        c["cost_per_m2_brl_2024"] = round(c["cost_brl_2024"] / c["area_m2"], 2)
        c["m2_per_place"] = round(c["area_m2"] / c["capacity_two_shifts"], 2)
        c["multiple_of_sinapi_m2_computed"] = round((c["contract_value_brl"] / c["area_m2"]) / c["sinapi_m2_contract_month"], 2)
    j = comp[0]
    others = comp[1:]
    comparison = {
        "unit": "R$ de dez/2024 por vaga (capacidade em dois turnos parciais) e por m² construído",
        "unit_note": ("Valores de contrato assinado (antes de aditivos), para comparar igual com igual; o valor final pago do CEI de Joinville aparece à parte. "
                      "Contratos assinados depois de dez/2024 (Itajaí, Naviraí, Caraá) são deflacionados pelo IPCA até dez/2024. "
                      "A área FNDE é a do projeto padrão 'incluindo projeção da cobertura'; a área de Joinville é a informada pela Prefeitura (2,9 mil m²), sem definição publicada."),
        "items": comp,
        "ratios_computed": {c["id"]: {"per_place": round(j["cost_per_place_brl_2024"] / c["cost_per_place_brl_2024"], 2),
                                      "per_m2": round(j["cost_per_m2_brl_2024"] / c["cost_per_m2_brl_2024"], 2)} for c in others},
        "regional_check": {"doc": "IBGE, SINAPI, custo médio do m² por UF (tabela 2296, variável 48), mês de assinatura de cada contrato", "url": SINAPI_URL,
                           "reading": "Divide o custo por m² do contrato pelo m² SINAPI da UF no mesmo mês; tira a diferença regional de preços. O SINAPI mede projetos residenciais padrão, então serve só como régua regional."},
        "method": conv.method([c["contract_month"] for c in comp] + list(by_month), []),
        "excluded_candidates": [
            {"name": "CEIs do mesmo programa de Joinville (ex.: CEI Iramar João Viana, R$ 19 milhões, 2,8 mil m²)", "reason": "Mesma cidade e mesmo programa; listados em program_context, não usados como comparáveis."},
            {"name": "CEIM Cristo Rei, Chapecó/SC (R$ 3,97 milhões, 2024)", "reason": "Área e capacidade não publicadas no registro do PNCP lido."},
            {"name": "Contratos de 'remanescente' ou 'conclusão' de creches FNDE", "reason": "Cobrem só parte da obra."},
        ],
    }
    fmt = lambda x: f"{x:.1f}".replace(".", ",")  # noqa: E731
    r_it = comparison["ratios_computed"]["itajai"]
    r_t1 = [comparison["ratios_computed"][k] for k in ("araujos", "navirai_127", "caraa")]
    comparison["reading"] = (
        f"Pelo valor de contrato, o CEI de Joinville custou {fmt(r_it['per_m2'])} vezes o m² da creche FNDE Tipo 2 de Itajaí (mesmo estado) e "
        f"de {fmt(min(r['per_m2'] for r in r_t1))} a {fmt(max(r['per_m2'] for r in r_t1))} vezes o m² das creches FNDE Tipo 1 de MG, MS e RS; "
        f"por vaga, {fmt(r_it['per_place'])} vezes Itajaí e de {fmt(min(r['per_place'] for r in r_t1))} a {fmt(max(r['per_place'] for r in r_t1))} vezes as Tipo 1. "
        f"A diferença não é só regional: medido em múltiplos do m² SINAPI da própria UF, Joinville fica em {fmt(j['multiple_of_sinapi_m2_computed'])} "
        f"e os outros entre {fmt(min(c['multiple_of_sinapi_m2_computed'] for c in others))} e {fmt(max(c['multiple_of_sinapi_m2_computed'] for c in others))}. "
        "O prédio de Joinville é projeto próprio, maior e premiado, e os valores dos outros são de contrato recém-assinado (podem subir com aditivos); "
        "a comparação mostra uma diferença de custo que o registro oficial não explica, sem afirmar irregularidade.")

    # ---------------------------------------------------------------- findings
    findings = [
        {"body": "MPSC (4ª Promotoria de Justiça da Comarca de Joinville) e Município", "kind": "termo de ajustamento de conduta (acordo) em ação civil pública",
         "process": "Ação Civil Pública n. 0905644-43.2017.8.24.0038; acordo assinado em 15/05/2023", "date": "2023-05-15",
         "summary_quote": "o poder público municipal se comprometeu a seguir o Plano de Expansão de Vagas, que estabelece o mês de junho de 2025 como limite para a finalização da construção das 15 unidades de educação infantil",
         "status": "em vigor; o Município pediu em junho de 2026 a prorrogação dos prazos (MPSC, 17/07/2026)", "url": MPSC["tac_2023"]},
        {"body": "MPSC (12ª Promotoria de Justiça de Joinville)", "kind": "recomendação em inquérito civil (fila de vagas)",
         "process": "Inquérito Civil n. 06.2026.00002283-7", "date": "2026-07-17",
         "summary_quote": "Das unidades previstas, quatro já foram entregues, duas seguem dentro do cronograma e nove apresentam atrasos. Segundo a Secretaria Municipal de Educação, os problemas são atribuídos ao descumprimento de contratos, à baixa produtividade e a falhas técnicas das empresas responsáveis pelas obras.",
         "about_this_contract": "A nota cita o CEI do Comasa entre os já inaugurados; os atrasos e multas citados são de outras obras do programa (a nota nomeia o CEI Minas Gerais).",
         "status": "recomendação acolhida pelo Município, segundo o MPSC; procedimento de monitoramento a instaurar", "url": MPSC["rec_2026"]},
    ]
    findings_none = ("Nenhum achado do TCE-SC, da CGU, do TCU, do MPF ou decisão judicial sobre o contrato 366/2023 foi localizado. "
                     "Os documentos do MPSC tratam do programa de 15 CEIs e da fila de vagas, não de irregularidade neste contrato.")

    # ---------------------------------------------------------------- work, card
    work_obj = {
        "name": "Construção do Centro de Educação Infantil (CEI) Manoel Antônio da Rosa, no bairro Comasa (contrato 'CEI Rio Negro')",
        "short_name": "CEI Comasa (Manoel Antônio da Rosa)",
        "municipalities": [{"name": "Joinville", "uf": "SC", "ibge_code": 4209102}],
        "level": "municipal", "agency": {"name": "Prefeitura de Joinville, Secretaria de Educação (SED)", "cnpj": "83169623000110"},
        "siconfi_function": "Educação", "siconfi_function_code": 12,
        "siconfi_subfunctions": ["365 Educação Infantil", "361 Ensino Fundamental (uma das dotações do 3º apostilamento)"],
        "funding_quote": "Dotações dos apostilamentos: 'Fonte 336 - Recursos Superávit Salário-Educação' (1º e 3º), 'Fonte 136 - Salário-Educação' e 'Fonte 119 - Transferências do FUNDEB' (2º). A Prefeitura divulgou 'recursos próprios da Prefeitura'. O pago por fonte está em payments.gross_by_source_of_funds_computed.",
        "status": "concluída e em funcionamento", "status_detail": [{"text": "inaugurado em 07/03/2025; aulas a partir de 10/03/2025", "url": NEWS["inauguration"]}],
        "dates": {"contract_signed": signed_on, "contract_signed_register": reg["contrato"]["assinatura"],
                  "contract_signed_note": "O extrato no Diário Oficial diz 'assinado em 01/03/2023'; o registro de contratos da Prefeitura traz 23/02/2023.",
                  "first_commitment": "2023-03-06", "inauguration": "2025-03-07", "last_payment": (lambda m: f"{m[:4]}-{m[4:]}")(max(by_month)) if by_month else None,
                  "tac_deadline_original": "2025-06"},
        "capacity": {"places_single_shift_type": 600, "children_served_2025": 462, "classrooms": 17, "area_m2": 2900, "source": NEWS["inauguration"]},
        "operation": "Gestão por organização social (ABCD da Educação), vencedora de chamamento público; ensino gratuito.",
        "operation_source": NEWS["inauguration"],
        "description_plain": ("Creche municipal para 462 crianças de 0 a 5 anos, com 2,9 mil m² e 17 salas, a primeira das 15 que Joinville se comprometeu "
                              "com o MPSC a construir para zerar a fila de vagas. Contratada em março de 2023 por R$ 15,1 milhões, teve seis termos aditivos e "
                              "quatro apostilamentos; os pagamentos somam R$ 16,25 milhões. Inaugurada em março de 2025, é administrada por uma organização social."),
        "program_context": {"summary": "Contratos de construção de CEIs registrados na API de contratos da Prefeitura (2023 a 2026), valores originais",
                            "contracts": program, "count": len(program), "total_original_brl_computed": round(sum(p["value_original_brl"] for p in program), 2),
                            "official_total": "'R$ 226 milhões na construção de 15 novos Centros de Educação Infantil' (Prefeitura)", "official_total_url": NEWS["program_226"]},
        "sources": [NEWS["inauguration"], ext["gazette_pdf"]],
    }
    card = {
        "title": "CEI Comasa", "subtitle": "Primeiro 'mega CEI' de Joinville", "place": "Joinville",
        "stats": [
            {"label": "Pago", "value": gross_total, "unit": "BRL", "display": "R$ 16,25 mi", "note": f"contrato original R$ {value_orig/1e6:.2f} mi".replace(".", ",")},
            {"label": "Vagas", "value": 462, "unit": "crianças", "display": "462 (até 600)", "note": "Prefeitura"},
            {"label": "Por vaga", "value": j["cost_per_place_brl_2024"], "unit": "BRL 2024", "display": f"R$ {j['cost_per_place_brl_2024']/1000:.1f} mil".replace(".", ","), "note": "contrato, capacidade 600"},
            {"label": "vs creche FNDE em SC", "value": r_it["per_place"], "unit": "x", "display": f"{fmt(r_it['per_place'])}x por vaga", "note": "Itajaí, Tipo 2, 2025"},
        ],
        "photo": "docs/superpowers/previews/assets/cases/cei-comasa-joinville/joinville-zona-leste.jpg",
    }
    out = {
        "slug": "cei-comasa-joinville", "collected_on": COLLECTED,
        "report": "docs/research/BRASIL-IMPOSTO_RESEARCH_obras-sc-cei-comasa-joinville_2026-09-30.md",
        "rules": "Somente papéis e atos oficiais, com as palavras do órgão. Nenhuma inferência de irregularidade. Valores nominais com fonte e data de coleta; somas e razões marcadas como computed são desta pesquisa.",
        "work": work_obj,
        "contracts": [{
            "number": CONTRACT, "tender": "Concorrência nº 807/2022", "object": " ".join(reg["contrato"]["objetoResumido"].split()),
            "company": "CONSTRUTORA VISEU LTDA", "company_cnpj": "03184733000111", "signed_on": signed_on,
            "duration_months_original": 18, "value_original_brl": value_orig,
            "value_current_brl": value_current,
            "value_current_note": "Calculado: original + acréscimos - supressões dos termos aditivos + reajustes dos apostilamentos publicados no Diário Oficial do Município. Não há campo de valor atualizado nas bases abertas lidas.",
            "added_by_amendments_brl": round(added, 2), "removed_by_amendments_brl": round(removed, 2), "readjustments_brl_computed": round(readjust, 2),
            "status": "concluído (obra inaugurada em 07/03/2025); último pagamento em " + ((lambda m: f"{m[:4]}-{m[4:]}")(max(by_month)) if by_month else "?"),
            "amendments": amendments,
            "extract": {"text": ext["text"], "published_in": f"Diário Oficial Eletrônico do Município de Joinville nº {ext['gazette_edition']}, {ext['gazette_date']}", "url": ext["gazette_pdf"]},
            "errata": acts.get(("Errata", "0")),
            "register_record": {"url": f"{API}/contrato?periodo_inicial=01/01/2023&periodo_final=31/12/2023&codigo_unidade=0",
                                "signed_on": reg["contrato"]["assinatura"], "end": reg["contrato"]["vencimento"], "value": reg["contrato"]["valorTotal"]},
            "source": {"doc": "Diário Oficial Eletrônico do Município de Joinville e API de contratos do Portal da Transparência", "collected_on": COLLECTED},
        }],
        "payments": payments, "companies": companies, "people": people, "head_of_government": [mayor],
        "head_of_government_note": "O prefeito não assina o contrato: assina o Secretário de Educação. O acordo com o MPSC foi assinado no gabinete do prefeito (MPSC, 15/05/2023).",
        "findings": findings, "findings_none_note": findings_none,
        "media": "docs/superpowers/previews/assets/cases/cei-comasa-joinville/credits.json",
        "comparison": comparison, "card": card,
        "terms_check": "Nenhum documento oficial lido usa 'superfaturamento', 'sobrepreço' ou 'desvio' para esta obra.",
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out = no_dashes(out)
    out = json.loads(re.sub(r"CPF n[º°]\s*[\dxX.\-]+", "CPF [omitido]", json.dumps(out, ensure_ascii=False)))
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
    print("wrote", OUT)
    print("orig", value_orig, "added", added, "removed", removed, "readj", readjust, "current", value_current, "paid gross", gross_total, "2024", paid_2024)
    for c in comp:
        print(c["id"], c["cost_brl_2024"], "per place", c["cost_per_place_brl_2024"], "per m2", c["cost_per_m2_brl_2024"], "xSINAPI", c["multiple_of_sinapi_m2_computed"])
    print([a["act"] for a in amendments])
    print(comparison["reading"])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
