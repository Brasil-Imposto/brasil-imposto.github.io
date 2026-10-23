"""Builds data/works/ufsc-cfm-admin-building.json: the unfinished administrative building of the CFM (Centro de Ciências Físicas
e Matemáticas) on the UFSC Trindade campus, Florianópolis. Federal money (UFSC, autarchy of the Ministry of Education).

Usage:
  python3 build_ufsc_cfm_admin.py <workdir> --fetch    # downloads the official sources (about 20 MB; raw zips are not kept)
  python3 build_ufsc_cfm_admin.py <workdir>            # checks everything and writes the JSON
  python3 build_ufsc_cfm_admin.py <workdir> --control  # plants a R$ 500 error in the 2019 bid discount; the sum check must fail

Every number is read from the downloaded official text: Obrasgov.br API (UFSC entries), Contratos.gov.br API (contract
317/2019, its amendments, commitments and DOU extracts), Tesouro STA API (bank orders of each commitment), Portal da
Transparência open procurement files (contracts of 2013), the UFSC works department pages (dfo.ufsc.br, WordPress API),
UFSC news, CFM council minutes, the CGU report 201702650, the rescission term of 2023, PNCP (tender 90002/2026), the Receita
CNPJ open base (publica.cnpj.ws mirror) and IBGE IPCA. Literal quotes are checked against the source text
(roads_common.require_quote). Personal identifiers that some documents carry (CPF) are never copied.
The signature page of contract 317/2019 is a scanned PDF without text layer: its signer was read by OCR and checked by eye
(recorded in the JSON as such); it is not re-checked here.
"""
import csv, io, json, os, re, sys, time, urllib.parse, urllib.request, zipfile
from decimal import Decimal as D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roads_common as C

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SLUG = 'ufsc-cfm-admin-building'
OUT = os.path.join(ROOT, 'data', 'works', f'{SLUG}.json')
REPORT = f'docs/research/BRASIL-IMPOSTO_RESEARCH_case-{SLUG}_2026-10-06.md'
MEDIA = f'docs/superpowers/previews/assets/cases/{SLUG}'
COLLECTED = '2026-10-06'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36'

OG = 'https://api.obrasgov.gestao.gov.br/obrasgov/api'
OG_IDS = {'first': '59825.42-35', 'resumption': '59844.42-03'}
CT = 'https://contratos.comprasnet.gov.br/api/contrato'
CT_ID = 69937
STORAGE = 'https://contratos.comprasnet.gov.br/storage/contrato/69937_00317_2019/'
DFO = {'first': 7583, 'resumption': 11410, 'order_2013': 7574, 'cce': 7226, 'cfh': 7768}
DFO_URL = {'first': 'https://dfo.ufsc.br/bloco-administrativo-e-instalacao-de-elevador-no-bloco-29-do-cfm/',
           'resumption': 'https://dfo.ufsc.br/retomada-do-bloco-administrativo-do-cfm/',
           'order_2013': 'https://dfo.ufsc.br/assinada-mais-uma-ordem-de-servico-para-obra-no-campus-reitor-joao-david-ferreira-lima-8/',
           'cce': 'https://dfo.ufsc.br/7226-2/', 'cfh': 'https://dfo.ufsc.br/blocos-ef-e-anexo-e-do-cfh/'}
NEWS = {
    'rdc_2019': 'https://noticias.ufsc.br/2019/12/economia-gerada-por-licitacao-viabiliza-retomada-de-obra-na-ufsc/',
    'status_2026': 'https://noticias.ufsc.br/2026/02/administracao-central-da-ufsc-alinha-prioridades-para-inicio-do-ano-letivo-com-cfm-cfh-e-ccs/',
    'rector_2012': 'https://noticias.ufsc.br/2012/05/nova-reitora-da-ufsc-assume-nesta-quinta-2/',
    'rector_2016': 'https://noticias.ufsc.br/2016/05/nova-reitoria-da-ufsc-assume-cargos-em-cerimonia-no-dia-10-de-maio-as-19h/',
    'rector_2018': 'https://noticias.ufsc.br/2018/07/mec-nomeia-ubaldo-cesar-balthazar-reitor-da-ufsc/',
    'rector_2022': 'https://noticias.ufsc.br/2022/07/gestao-de-irineu-e-joana-assume-mandato-na-reitoria-em-sessao-solene/',
    'rector_2026': 'https://noticias.ufsc.br/2026/07/reitor-amir-de-oliveira-e-vice-reitora-felipa-amadigi-tomam-posse-na-ufsc/',
}
ATAS = {'2019_11_21': 'https://sitecfm.paginas.ufsc.br/files/2020/09/ATA_16_2019.pdf',
        '2023_08_10': 'https://sitecfm.paginas.ufsc.br/files/2018/06/ATA_07_2023.pdf',
        '2024_08_08': 'https://sitecfm.paginas.ufsc.br/files/2018/06/ATA_05_2024.pdf'}
CGU_URL = 'https://eaud.cgu.gov.br/relatorios/download/855692'
REL2013_URL = 'https://blogdagestao.ufsc.br/files/2014/05/Relat%C2%A2rio_imprensa_2013_FINAL-WEB.pdf'
RESCISSION_URL = STORAGE + 'b5qwZ0xGBRfwXEJ6EVHTtA1DdyCOk4EUIVRLiaRh.pdf'
CONTRACT_PDF_URL = STORAGE + 'e4aaac246dcaf2596a19097e975241b4.pdf'
COMPRAS = {'201307': ['1172013'], '201302': ['5052012'], '201310': ['1562013']}
COMPRAS_URL = 'https://portaldatransparencia.gov.br/download-de-dados/compras/{}'
COMPRAS_ZIP = 'https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/compras/{}_Compras.zip'
PNCP = 'https://pncp.gov.br/api/consulta/v1/orgaos/83899526000182/compras/2026/78'
PNCP_RES = 'https://pncp.gov.br/api/pncp/v1/orgaos/83899526000182/compras/2026/78/itens/1/resultados'
PNCP_PAGE = 'https://pncp.gov.br/app/editais/83899526000182/2026/78'
CNPJS = ['03611631000135', '13798155000167', '05901551000140', '83899526000182']
CNPJ_URL = 'https://publica.cnpj.ws/cnpj/{}'
IPCA_URL = 'https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/201302,201307,201309,202412?formato=json'
TSE = 'https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{}.zip'


def get(url, timeout=300, accept=None):
    h = {'User-Agent': UA}
    if accept:
        h['Accept'] = accept
    for attempt in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout).read()
        except Exception as e:
            print('  retry', url[:90], e, flush=True)
            time.sleep(20 * (attempt + 1))
    raise SystemExit(f'não consegui baixar {url}')


def fetch(W):
    os.makedirs(W, exist_ok=True)
    p = lambda *a: os.path.join(W, *a)
    save = lambda name, data: open(p(name), 'wb').write(data)
    for k, i in OG_IDS.items():
        save(f'og_fis_{k}.json', get(f'{OG}/execucao-fisica?idUnico={i}', accept='application/json'))
    save('og_inacabada.json', get(f'{OG}/projeto-investimento?uf=SC&situacao=Inacabada&pagina=0&tamanhoDaPagina=100', accept='application/json'))
    save('og_geo.json', get(f'{OG}/geometria?idUnico={OG_IDS["resumption"]}', accept='application/json'))
    save('ct_inativos.json', get(f'{CT}/inativo/ug/153163', timeout=600))
    for ep in ('historico', 'empenhos', 'publicacoes', 'garantias'):
        save(f'ct_{ep}.json', get(f'{CT}/{CT_ID}/{ep}'))
    for e in json.load(open(p('ct_empenhos.json'))):
        save(f'ob_{e["numero"]}.json', get(e['links']['documento_pagamento']))
        time.sleep(1)
    for k, i in DFO.items():
        save(f'dfo_{k}.json', get(f'https://dfo.ufsc.br/wp-json/wp/v2/pages/{i}'))
    for k, u in NEWS.items():
        save(f'news_{k}.html', get(u))
    for k, u in ATAS.items():
        save(f'ata_{k}.pdf', get(u))
    save('cgu_201702650.pdf', get(CGU_URL))
    save('rel2013.pdf', get(REL2013_URL))
    save('rescission_2023.pdf', get(RESCISSION_URL))
    for ym, nums in COMPRAS.items():
        z = zipfile.ZipFile(io.BytesIO(get(COMPRAS_ZIP.format(ym))))
        for name in z.namelist():
            if not (name.endswith('_Compras.csv') or name.endswith('_TermoAditivo.csv')):
                continue
            rows = list(csv.reader(io.StringIO(z.read(name).decode('latin1')), delimiter=';'))
            keep = [rows[0]] + [r for r in rows[1:] if r and r[0] in nums and '153163' in r]
            with open(p(f'compras_{ym}_{name.split("_", 1)[1]}'), 'w', newline='', encoding='utf-8') as f:
                csv.writer(f, delimiter=';').writerows(keep)
        time.sleep(6)
    save('pncp_compra.json', get(PNCP))
    save('pncp_resultados.json', get(PNCP_RES))
    for c in CNPJS:
        save(f'cnpj_{c}.json', get(CNPJ_URL.format(c)))
        time.sleep(21)  # the mirror allows 3 requests a minute
    save('ipca.json', get(IPCA_URL))
    print('fetch ok', W)


def money(s):
    return D(str(s).strip().replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.'))


def dfo_text(W, k):
    """DFO pages are WordPress tables, one field per cell: cells become ' | ' separators before the tags are removed."""
    d = json.load(open(os.path.join(W, f'dfo_{k}.json')))
    raw = re.sub(r'</t[dh]>|</p>|<br\s*/?>', ' | ', d['content']['rendered'])
    return C.clean_html(raw), d


def dfo_field(txt, label):
    m = re.search(re.escape(label) + r'\s*:?\s*(.+?)\s*\|', txt)
    if not (m):
        raise SystemExit(f'campo {label} não achado')
    return m.group(1).strip()


def ata_text(path):
    """CFM minutes number every line; the numbers are removed before quotes are compared."""
    raw = C.pdf_text(path)
    return re.sub(r'(?m)^\s*\d{1,3}\s{2,}', '', raw)


def main(W, control=False):
    C.self_test()
    p = lambda *a: os.path.join(W, *a)
    rq = C.require_quote
    checks = []

    def check(label, got, expected, tol=D('0')):
        diff = (got - expected) if isinstance(got, D) else None
        ok = (abs(diff) <= tol) if diff is not None else got == expected
        checks.append({'check': label, 'computed': str(got), 'official': str(expected), 'ok': bool(ok)})
        if not ok:
            raise SystemExit(f'CHECAGEM FALHOU: {label}: calculado {got} contra oficial {expected}')

    # ---------------- Obrasgov.br (UFSC entries)
    fis = {k: json.load(open(p(f'og_fis_{k}.json')))['content'][0] for k in OG_IDS}
    proj = {x['idUnico']: x for x in json.load(open(p('og_inacabada.json')))['content']}
    pf, pr = proj[OG_IDS['first']], proj[OG_IDS['resumption']]
    check('Obrasgov 59825.42-35: situação', fis['first']['situacao'], 'Inacabada')
    check('Obrasgov 59844.42-03: situação', fis['resumption']['situacao'], 'Inacabada')
    check('Obrasgov 59825.42-35: data da situação', fis['first']['dataSituacao'][:10], '2015-06-01')
    check('Obrasgov 59844.42-03: data da situação', fis['resumption']['dataSituacao'][:10], '2023-05-23')
    check('Obrasgov: executor é a UFSC', pf['executores'][0]['nome'], 'UNIVERSIDADE FEDERAL DE SANTA CATARINA')
    check('Obrasgov 59825.42-35: valor previsto = contrato de 2013', D(str(pf['fontesDeRecurso'][0]['valorInvestimentoPrevisto'])), D('7077758.10'))
    check('Obrasgov 59844.42-03: valor previsto = contrato de 2019', D(str(pr['fontesDeRecurso'][0]['valorInvestimentoPrevisto'])), D('6751904.72'))
    rq('totalizando área aproximada de 3.441,88 m2', pr['descricao'], 'Obrasgov descrição')
    just_first = fis['first']['cancelamentosParalisacoes'][0]
    just_res = fis['resumption']['cancelamentosParalisacoes'][0]
    rq('presentes no MEMORANDO 012/2014/RJ (anexo) e no TERMO DE RESCISÃO UNILATERAL (anexo)', just_first['justificativa'], 'Obrasgov justificativa 1')
    rq('presentes no OFÍCIO 098/2022/DFO-SEOMA (anexo) e no TERMO DE RESCISÃO AMIGÁVEL (anexo)', just_res['justificativa'], 'Obrasgov justificativa 2')
    rq('abertura de nova licitação prevista para o segundo semestre de 2025', just_first['faseTratativa'], 'Obrasgov tratativa')
    motives_first = [m['descricao'] for m in just_first['motivosParalisacao']]
    check('Obrasgov 59825.42-35: motivos', sorted(motives_first), ['Inadimplência da empresa executora', 'Rescisão contratual'])
    geo = json.load(open(p('og_geo.json')))[0]
    pts = [tuple(map(float, xy.split())) for xy in re.findall(r'-?\d+\.\d+ -?\d+\.\d+', geo['geometriaWkt'])]
    lon = round(sum(x for x, _ in pts) / len(pts), 5)
    lat = round(sum(y for _, y in pts) / len(pts), 5)

    # ---------------- DFO/UFSC pages
    f_txt, f_meta = dfo_text(W, 'first')
    r_txt, r_meta = dfo_text(W, 'resumption')
    o_txt, _ = dfo_text(W, 'order_2013')
    check('DFO 2013: valor contratado', money(dfo_field(f_txt, 'Valor Contratado')), D('7077758.10'))
    check('DFO 2013: empresa', dfo_field(f_txt, 'Empresa Contratada'), 'LIMA E SILVA ENGENHARIA E CONSTRUTORA LTDA – EPP')
    check('DFO 2013: percentual executado', dfo_field(f_txt, 'Percentual Executado'), '43,26%')
    check('DFO 2013: rescisão', dfo_field(f_txt, 'Data de Conclusão do Contrato'), 'CONTRATO RESCINDIDO EM 01/06/2015')
    check('DFO 2019: valor contratado', money(dfo_field(r_txt, 'Valor Contratado')), D('6751904.72'))
    paid_txt = dfo_field(r_txt, 'Percentual Executado')
    m = re.search(r'([\d,]+)% \(Valor total pago = R\$ ([\d.,]+)\)', paid_txt)
    pct_res, paid_res = m.group(1), money(m.group(2))
    check('DFO 2019: valor total pago', paid_res, D('1336183.59'))
    check('DFO 2019: rescisão', dfo_field(r_txt, 'Data de Conclusão do Contrato'), 'CONTRATO RESCINDIDO EM 23/05/2023')
    check('DFO 2019: fonte de recursos', dfo_field(r_txt, 'Fonte de Recursos'), 'Orçamento UFSC')
    rq('assinou na data de hoje, a ordem de serviço de uma obra com início previsto para julho de 2013, mais precisamente no dia 29', o_txt, 'DFO OS 2013')

    # ---------------- Contract 117/2013 (Portal da Transparência, open procurement files)
    rows = {}
    for ym in COMPRAS:
        rd = list(csv.reader(open(p(f'compras_{ym}_Compras.csv'), encoding='utf-8'), delimiter=';'))
        hdr = rd[0]
        for r in rd[1:]:
            rows[r[0]] = dict(zip(hdr, r))
    c13 = rows['1172013']
    check('Portal 117/2013: contratado (CNPJ)', c13['Código Contratado'], '03611631000135')
    check('Portal 117/2013: valor inicial', money(c13['Valor Inicial Compra']), D('7077758.10'))
    check('Portal 117/2013: valor final', money(c13['Valor Final Compra']), D('7077758.10'))
    check('Portal 117/2013: situação', c13['Situação Contrato'], 'Rescindido - Publicado')
    check('Portal 117/2013: licitação', c13['Número Licitação'], '000112012')
    ta13 = list(csv.reader(open(p('compras_201307_TermoAditivo.csv'), encoding='utf-8'), delimiter=';'))[1:]
    ta13 = {r[7]: r for r in ta13}
    check('Portal 117/2013: termos aditivos registrados', sorted(ta13), ['12014'])
    rq('SUBSTITUIÇÃO DE SERVIÇOS especificados no ANEXO Nº 01', ta13['12014'][9], 'TA 1/2014')

    # ---------------- CGU report 201702650
    cgu = C.pdf_text(p('cgu_201702650.pdf'))
    q_cgu_1 = rq('A obra do prédio administrativo do Centro de Ciências Físicas e Matemáticas (CFM) está paralisada desde a rescisão unilateral do contrato, em 1º de junho de 2015.', cgu, 'CGU 1.3')
    q_cgu_2 = rq('O valor contratado da obra foi de R$ 7.077.758,10 e foram executados R$ 3.061.830,69, antes da paralisação.', cgu, 'CGU 1.1.1.6')
    q_cgu_3 = rq('A UFSC informou que, como o contrato foi rescindido, necessita da contratação de uma próxima etapa para conclusão da edificação.', cgu, 'CGU 1.1.1.6 b')
    q_cgu_4 = rq('ocorreu afronta ao artigo 45 da Lei de Responsabilidade Fiscal, pois foram inseridas novas obras, em lei orçamentária, sem a garantia de recursos para a conclusão dos projetos existentes', cgu, 'CGU conclusão')
    q_cgu_5 = rq('Priorizar a finalização de edificações inacabadas nos campi da UFSC', cgu, 'CGU recomendação')
    q_cgu_6 = rq('O impacto social se dá, principalmente, pela falta de estrutura adequada para os estudantes, servidores e professores do CFM.', cgu, 'CGU impacto')
    executed_13 = D('3061830.69')

    # ---------------- UFSC 2013 report (two-column PDF: fragments are checked one by one)
    rel = C.pdf_text(p('rel2013.pdf'))
    for frag in ('A empresa contratada é a Lima e Silva Engenharia', 'e Construtora Ltda – EPP',
                 'No final do mês de julho começaram as obras', 'no CFM, que compreendem a construção do prédio',
                 'vê área construída de 3.441,88 metros quadrados', 'com previsão para conclusão em novembro de 2014',
                 'Biblioteca setorial, anfiteatro para 150 pessoas', 'Os recursos são do Programa de Apoio',
                 'centro, construídos na década de 1960'):
        rq(frag, rel, 'Relatório imprensa 2013')

    # ---------------- RDC 007/2019 and contract 317/2019
    n19 = C.clean_html(open(p('news_rdc_2019.html'), encoding='utf-8', errors='ignore').read())
    q_rdc = rq('A obra para o CFM estava paralisada desde junho de 2015 e era orçada em R$ 8.284.545,67.', n19, 'notícia RDC')
    rq('produzindo uma economicidade de R$ 1.532.640,95', n19, 'notícia RDC')
    rq('foi homologado pelo Departamento de Licitações (DPL) da UFSC, no dia 27 de novembro de 2019', n19, 'notícia RDC')
    estimate_19, saving_19 = D('8284545.67'), D('1532640.95')
    inativos = json.load(open(p('ct_inativos.json')))
    c19 = next(c for c in inativos if c['id'] == CT_ID)
    check('Contratos.gov.br 317/2019: número', c19['numero'], '00317/2019')
    check('Contratos.gov.br 317/2019: CNPJ', c19['fornecedor']['cnpj_cpf_idgener'], '13.798.155/0001-67')
    check('Contratos.gov.br 317/2019: justificativa', c19['justificativa_inativo'], 'Rescindido')
    check('Contratos.gov.br 317/2019: fim da vigência', c19['vigencia_fim'], '2023-05-23')
    value_19 = money(c19['valor_global'])
    if control:
        saving_19 += D('500.00')  # planted error: the check below must fail
    check('RDC 007/2019: orçamento menos economia = valor do contrato 317/2019', estimate_19 - saving_19, value_19)
    check('RDC 007/2019: desconto de 18,50%', (saving_19 / estimate_19 * 100).quantize(D('0.01')), D('18.50'))
    hist = {h['numero']: h for h in json.load(open(p('ct_historico.json')))}
    check('317/2019: termos aditivos', sorted(k for k in hist if k != '00317/2019'), ['00001/2021', '00002/2022'])
    for k in ('00001/2021', '00002/2022'):
        check(f'317/2019: {k} não muda o valor', money(hist[k]['valor_global']), value_19)
    pubs = json.load(open(p('ct_publicacoes.json')))
    dou_resc = next(x for x in pubs if 'RESCISÃO' in (x['texto_dou'] or ''))
    q_dou = rq('rescisão total e amigável do contrato nº 317/ufsc/2019, firmado em 11 de dezembro de 2019, entre a universidade federal de santa catarina e a empresa mendonça & gonçalves construções e incorporações ltda., com fundamento no art. 79, inciso ii, da lei n. 8.666/93, por razões de conveniência da administração', dou_resc['texto_dou'], 'DOU rescisão')
    dou_ret = next(x for x in pubs if 'RETIFICAÇÃO DO TERMO ADITIVO' in (x['texto_dou'] or ''))
    rq('O antigo representante legal da empresa Gabriel Mendonça Gonçalves foi retirado da sociedade e substituído por Igor Mendonça Gonçalves', dou_ret['texto_dou'], 'DOU retificação')
    guarantee = money(json.load(open(p('ct_garantias.json')))[0]['valor'])
    resc = C.pdf_text(p('rescission_2023.pdf'))
    q_resc_1 = rq('A motivação para a rescisão do presente contrato está presente no Ofício nº 098/2022/DFO-SEOMA', resc, 'termo de rescisão')
    q_resc_2 = rq('Termo Aditivo de acréscimo de quantitativo de serviços que fora autorizado, instruído, executado, porém não celebrado em razão das circunstâncias enfrentadas à época', resc, 'termo de rescisão')
    rq('representada neste ato pelo Prefeito Universitário, Hélio Rodak de Quadros Junior', resc, 'termo de rescisão')
    extra, complement = D('49952.64'), D('28928.59')
    rq('que receberá o valor de R$ 49.952,64', resc, 'termo de rescisão')
    rq('que receberá o valor de R$ 28.928,59', resc, 'termo de rescisão')

    # ---------------- Bank orders of contract 317/2019 (Tesouro STA API, one list per commitment)
    emps = json.load(open(p('ct_empenhos.json')))
    obs = {}
    for e in emps:
        for o in json.load(open(p(f'ob_{e["numero"]}.json'))):
            obs.setdefault(o['numero'], o)  # one bank order can pay several commitments: count it once
    check('ordens bancárias: nenhuma cancelada', [o['numero'] for o in obs.values() if o['cancelamentoob'] != '0'], [])
    to_company = sum(D(o['valor']) for o in obs.values() if o['favorecidocodigo'] == '13.798.155/0001-67')
    iss = sum(D(o['valor']) for o in obs.values() if 'FLORIANOPOLIS' in o['favorecidonome'])
    check('ordens bancárias: só empresa e ISS', len([o for o in obs.values() if o['favorecidocodigo'] != '13.798.155/0001-67' and 'FLORIANOPOLIS' not in o['favorecidonome']]), 0)
    check('ordens bancárias: todas citam o contrato 317/2019', all(re.search(r'CONTRATO (00)?317/2019', o['observacao']) for o in obs.values()), True)
    by_year = {}
    for o in obs.values():
        by_year[o['emissao'][:4]] = by_year.get(o['emissao'][:4], D('0')) + D(o['valor'])
    ob_total = to_company + iss
    check('ordens bancárias (líquido + ISS) ficam abaixo do pago bruto da UFSC', ob_total < paid_res, True)
    e808 = next(e for e in emps if e['numero'] == '2020NE800808')
    check('rescisão: serviços extras + medição complementar = restos a pagar pagos em 2023 (1 centavo de arredondamento)',
          extra + complement, money(e808['rppago']), tol=D('0.01'))
    check('rescisão: ordens bancárias de 2023 (líquido + ISS) abaixo do bruto', by_year['2023'] < extra + complement, True)
    e1646 = next(e for e in emps if e['numero'] == '2020NE801646')

    # ---------------- CFM council minutes and UFSC news on the current state
    A = {k: ata_text(p(f'ata_{k}.pdf')) for k in ATAS}
    q_ata19 = rq('será aberta a licitação para a conclusão do prédio administrativo do CFM, com a previsão inicial para finalização no segundo semestre de 2021', A['2019_11_21'], 'ata 2019')
    q_ata23 = rq('o recurso destinado à continuidade da obra será devolvido novamente ao Ministério da Educação, não havendo previsão, portanto, para retomada das obras', A['2023_08_10'], 'ata 2023')
    q_ata24 = rq('deve-se entender o motivo pelo qual o prédio administrativo do CFM não foi contemplado', A['2024_08_08'], 'ata 2024')
    n26 = C.clean_html(open(p('news_status_2026.html'), encoding='utf-8', errors='ignore').read())
    q_status = rq('há um prédio inacabado, paralisado há mais de dez anos, o que agrava riscos e custos e dificulta o funcionamento cotidiano', n26, 'notícia 2026')
    rq('10/02/2026', n26, 'data da notícia 2026')
    rq('foram realizadas reuniões no Centro de Ciências Físicas e Matemáticas (CFM), na sexta-feira (6 de fevereiro)', n26, 'notícia 2026')

    # ---------------- Tender 90002/2026 (PNCP)
    pc = json.load(open(p('pncp_compra.json')))
    pres = json.load(open(p('pncp_resultados.json')))[0]
    est_26, hom_26 = D(str(pc['valorTotalEstimado'])), D(str(pres['valorTotalHomologado'])).quantize(D('0.01'))
    check('PNCP 90002/2026: número', pc['numeroCompra'], '90002')
    check('PNCP 90002/2026: valor estimado', est_26, D('27458789.03'))
    check('PNCP 90002/2026: homologado (compra) = resultado do item', D(str(pc['valorTotalHomologado'])), hom_26)
    rq('retomada da obra da edificação CFM administrativo e construção do bloco de salas de aula anexo', pc['objetoCompra'], 'PNCP objeto')
    rq('com área de 5.101,16 m²', pc['objetoCompra'], 'PNCP objeto')

    # ---------------- Rectors (UFSC news)
    NW = {k: C.clean_html(open(p(f'news_{k}.html'), encoding='utf-8', errors='ignore').read()) for k in NEWS if k.startswith('rector')}
    rq('Oficialmente, Roselane e Lúcia tomaram posse na tarde da terça, 08/05, no Ministério da Educação', NW['rector_2012'], 'posse 2012')
    rq('Os convites assinados pela reitora, Roselane Neckel', NW['rector_2016'], 'transmissão 2016')
    rq('a nomeação do professor Ubaldo Cesar Balthazar para o cargo de reitor da Universidade Federal de Santa Catarina (UFSC), em mandato de quatro anos', NW['rector_2018'], 'nomeação 2018')
    rq('Estava respondendo como Reitor Pro Tempore da UFSC desde 27 de novembro do ano passado', NW['rector_2018'], 'nomeação 2018')
    rq('Desde segunda-feira, 4 de julho, eles estão à frente da gestão da UFSC', NW['rector_2022'], 'posse 2022')
    rq('nomeados em ato presidencial', NW['rector_2022'], 'posse 2022')
    rq('tomaram posse na noite desta segunda-feira, 6 de julho', NW['rector_2026'], 'posse 2026')

    # ---------------- Companies (Receita open base, mirror)
    reg = {}
    for c in CNPJS:
        d = json.load(open(p(f'cnpj_{c}.json')))
        e = d['estabelecimento']
        reg[c] = {'legal_name': d['razao_social'], 'trade_name': e.get('nome_fantasia'), 'city': f"{e['cidade']['nome']}/{e['estado']['sigla']}",
                  'registration_status': e['situacao_cadastral'], 'registration_status_date': e['data_situacao_cadastral'],
                  'activity_start': e['data_inicio_atividade'], 'size': (d.get('porte') or {}).get('descricao'),
                  'main_activity': (e.get('atividade_principal') or {}).get('descricao'),
                  'partners': [{'name': s['nome'], 'qualification': (s.get('qualificacao_socio') or {}).get('descricao', '').strip(), 'since': s.get('data_entrada')} for s in d.get('socios', [])],
                  'base_date': d.get('atualizado_em', '')[:10]}
    check('Receita: contratada de 2013', reg['03611631000135']['legal_name'], 'JULIO CESAR DE LIMA E SILVA LTDA')
    check('Receita: contratada de 2019', reg['13798155000167']['legal_name'], 'MENDONCA E GONCALVES CONSTRUCOES E INCORPORACOES LTDA')
    check('Receita: CNPJ da UFSC', reg['83899526000182']['legal_name'], 'UNIVERSIDADE FEDERAL DE SANTA CATARINA')

    # ---------------- Comparison: three UFSC buildings contracted in 2013 on the same campus
    ipca = C.load_ipca(W)
    cce_txt, _ = dfo_text(W, 'cce')
    cfh_txt, _ = dfo_text(W, 'cfh')
    check('DFO CCE: obra concluída', dfo_field(cce_txt, 'Descrição dos Serviços'), 'Obra concluída.')
    check('DFO CFH: obra concluída', dfo_field(cfh_txt, 'Descrição dos Serviços'), 'Obra concluída.')
    area = lambda t: D(dfo_field(t, 'Área Construída').replace('m²', '').replace('m2', '').strip().replace('.', '').replace(',', '.'))
    comp = []
    for key, num, txt, url_dfo, ym, place in (('cfm', '1172013', f_txt, DFO_URL['first'], '201307', 'UFSC, campus Trindade'),
                                               ('cce', '5052012', cce_txt, DFO_URL['cce'], '201302', 'UFSC, campus Trindade'),
                                               ('cfh', '1562013', cfh_txt, DFO_URL['cfh'], '201309', 'UFSC, campus Trindade')):
        r = rows[num]
        a = area(txt)
        v = money(r['Valor Inicial Compra'])
        per = (v / a).quantize(D('0.01'))
        fac = D(str(C.ipca_factor(ipca, ym))).quantize(D('0.000001'))
        comp.append({'key': key, 'contract': r['Número do Contrato'], 'company': r['Nome Contratado'], 'cnpj': r['Código Contratado'],
                     'signed_on': r['Data Assinatura Contrato'], 'value': v, 'final': money(r['Valor Final Compra']), 'area': a,
                     'per': per, 'fac': fac, 'per24': (per * fac).quantize(D('0.01')), 'ym': ym, 'url_dfo': url_dfo,
                     'object': r['Objeto'], 'place': place, 'dfo_value': money(dfo_field(txt, 'Valor Contratado'))})
    check('comparação: área do CFM', comp[0]['area'], D('3441.88'))

    # ---------------- money summary (labelled sum of two different official measures of the same building)
    total_known = executed_13 + paid_res
    check('soma conhecida = executado 2013 + pago 2019', total_known, D('4398014.28'))
    disp = lambda v: f"R$ {float(v) / 1e6:.1f} mi".replace('.', ',')
    check('a soma fecha com os valores como aparecem na tela (mi, uma casa)',
          D(disp(executed_13)[3:-3].replace(',', '.')) + D(disp(paid_res)[3:-3].replace(',', '.')), D(disp(total_known)[3:-3].replace(',', '.')))

    # ---------------- terms check (positive control first)
    bad_terms = ('superfatur', 'sobrepreço', 'desvio', 'improbidade')
    if not any(t in 'controle superfaturamento' for t in bad_terms):
        raise SystemExit('checagem de termos não acha o controle')
    sources_text = {'CGU 201702650': cgu, 'termo de rescisão': resc, 'atas do CFM': ' '.join(A.values()), 'notícias UFSC': n19 + n26}
    terms_found = {k: [t for t in bad_terms if t in v.lower()] for k, v in sources_text.items()}

    brl = lambda v: float(v)
    tse_src = lambda *ys: ' (e '.join(TSE.format(y) for y in ys) + (')' if len(ys) > 1 else '')
    rec = {
        'slug': SLUG, 'uf': 'SC', 'collected_on': COLLECTED, 'report': REPORT,
        'rules': 'Somente documentos oficiais, com as palavras do órgão. Nenhuma inferência de irregularidade. Valores nominais salvo quando marcados (reais de dez/2024 pelo IPCA). Somas marcadas como computed são desta pesquisa. CPFs que alguns documentos trazem não foram copiados.',
        'status': 'abandonado',
        'status_source': {'url': NEWS['status_2026'], 'date': '2026-02-10', 'quote': q_status,
                          'context': 'Notícia oficial da UFSC sobre a reunião do Gabinete da Reitoria no CFM em 06/02/2026. A notícia não nomeia o prédio; o único prédio do CFM com situação "Inacabada" no Obrasgov.br é este (fichas 59825.42-35 e 59844.42-03).',
                          'also': [{'source': 'Obrasgov.br, ficha 59844.42-03 (execução física)', 'url': f'{OG}/execucao-fisica?idUnico={OG_IDS["resumption"]}', 'quote': '"situacao":"Inacabada", "dataSituacao":"2023-05-23"'},
                                   {'source': 'CGU, Relatório 201702650 (05/12/2019)', 'url': CGU_URL, 'quote': q_cgu_1},
                                   {'source': 'Ata nº 7 do Conselho da Unidade do CFM (10/08/2023)', 'url': ATAS['2023_08_10'], 'quote': q_ata23}]},
        'work': {
            'name': 'Bloco Administrativo do Centro de Ciências Físicas e Matemáticas (CFM) da UFSC, com elevador no Bloco 29 da Química',
            'short_name': 'Prédio administrativo do CFM (UFSC)',
            'municipalities': [{'name': 'Florianópolis', 'uf': 'SC', 'ibge_code': 4205407}],
            'level': 'federal',
            'agency': {'name': 'Universidade Federal de Santa Catarina (UFSC), autarquia federal vinculada ao Ministério da Educação', 'cnpj': '83899526000182'},
            'financing': 'Reuni, do Governo Federal, no contrato de 2013 (relatório da gestão da UFSC); orçamento da UFSC na retomada de 2019 (DFO)',
            'financing_source': [REL2013_URL, DFO_URL['resumption']],
            'siconfi_function': 'Educação', 'siconfi_function_code': 12,
            'status': 'abandonado: inacabado e parado desde maio de 2023 (antes, de junho de 2015 a janeiro de 2020); licitação de 2026 homologada, contrato não localizado',
            'status_detail': [
                {'date': '2013-07-18', 'text': 'Contrato 117/2013 assinado com Julio Cesar de Lima e Silva Ltda (Concorrência 11/2012), R$ 7.077.758,10', 'url': COMPRAS_URL.format('201307')},
                {'date': '2013-07-29', 'text': 'Início da obra; término previsto para 20/11/2014 (DFO)', 'url': DFO_URL['first']},
                {'date': '2014-12-15', 'text': 'Última vistoria do DFO: 43,26% executado', 'url': DFO_URL['first']},
                {'date': '2015-06-01', 'text': 'Contrato rescindido de forma unilateral; motivos registrados no Obrasgov: "Rescisão contratual" e "Inadimplência da empresa executora"', 'url': f'{OG}/execucao-fisica?idUnico={OG_IDS["first"]}'},
                {'date': '2018-10', 'text': 'CGU: "A obra do prédio administrativo do Centro de Ciências Físicas e Matemáticas (CFM) está paralisada desde a rescisão unilateral do contrato, em 1º de junho de 2015." (relatório publicado em 05/12/2019)', 'url': CGU_URL},
                {'date': '2019-11-27', 'text': 'RDC 007/2019 homologado: orçamento de R$ 8.284.545,67, desconto de 18,50%', 'url': NEWS['rdc_2019']},
                {'date': '2019-12-11', 'text': 'Contrato 317/2019 assinado com Mendonça e Gonçalves Construções e Incorporações Ltda, R$ 6.751.904,72; obra retomada em 09/01/2020 com término previsto para 01/07/2021', 'url': DFO_URL['resumption']},
                {'date': '2021-11-29', 'text': 'Termo aditivo 1/2021: prazo do contrato prorrogado até 24/11/2022, sem mudar o valor', 'url': f'{CT}/{CT_ID}/historico'},
                {'date': '2022-11-24', 'text': 'Termo aditivo 2/2022: prazo prorrogado até 23/05/2023, sem mudar o valor', 'url': f'{CT}/{CT_ID}/historico'},
                {'date': '2023-05-23', 'text': 'Rescisão amigável "por razões de conveniência da Administração", com 19,79% executado e R$ 1.336.183,59 pagos (DFO)', 'url': RESCISSION_URL},
                {'date': '2023-08-10', 'text': 'Conselho do CFM: "o recurso destinado à continuidade da obra será devolvido novamente ao Ministério da Educação, não havendo previsão, portanto, para retomada das obras"', 'url': ATAS['2023_08_10']},
                {'date': '2024-08-08', 'text': 'Conselho do CFM pede à Administração Central os documentos dos projetos do PAC para "entender o motivo pelo qual o prédio administrativo do CFM não foi contemplado"', 'url': ATAS['2024_08_08']},
                {'date': '2026-02-06', 'text': 'Reunião da Reitoria no CFM: "há um prédio inacabado, paralisado há mais de dez anos" (notícia de 10/02/2026)', 'url': NEWS['status_2026']},
                {'date': '2026-06-12', 'text': 'Concorrência 90002/2026 publicada: retomada do prédio e construção de um bloco de salas de aula anexo, 5.101,16 m², estimativa de R$ 27.458.789,03', 'url': PNCP_PAGE},
                {'date': '2026-08-10', 'text': 'Resultado da Concorrência 90002/2026: Embracol Obras Ltda, R$ 20.594.091,77 homologados; contrato não localizado até 06/10/2026', 'url': PNCP_PAGE},
            ],
            'dates': {'tender_1': 'Concorrência 11/2012', 'contract_1_signed': '2013-07-18', 'contract_1_dou': '2013-07-23', 'works_start_1': '2013-07-29',
                      'planned_end_1': '2014-11-20', 'last_inspection_1': '2014-12-15', 'stopped_1': '2015-06-01',
                      'tender_2_homologated': '2019-11-27', 'contract_2_signed': '2019-12-11', 'works_start_2': '2020-01-09',
                      'planned_end_2': '2021-07-01', 'stopped_2': '2023-05-23', 'tender_3_published': '2026-06-12', 'tender_3_result': '2026-08-10',
                      'years_stopped_note': 'parado de jun/2015 a jan/2020 e desde mai/2023; previsto para nov/2014 no primeiro contrato'},
            'area_m2': brl(comp[0]['area']),
            'execution': {'contract_1_pct': 43.26, 'contract_1_pct_source': DFO_URL['first'],
                          'contract_2_pct': float(pct_res.replace(',', '.')), 'contract_2_pct_source': DFO_URL['resumption'],
                          'obrasgov_pct': {'59825.42-35': fis['first']['percentual'], '59844.42-03': fis['resumption']['percentual']},
                          'note': 'Os percentuais são de cada contrato, como o DFO e o Obrasgov os publicam; nenhum documento lido dá o percentual do prédio inteiro.'},
            'location': {'lat': lat, 'lon': lon, 'source': f'{OG}/geometria?idUnico={OG_IDS["resumption"]}',
                         'note': 'centro do polígono da ficha do Obrasgov (SIRGAS 2000), área executora "Departamento de Gestão de Imóveis - DGI/UFSC"'},
            'description_plain': 'Prédio de cinco pavimentos e 3.441,88 m² para a direção, as coordenações de curso, a biblioteca setorial e um auditório do Centro de Ciências Físicas e Matemáticas, no meio do campus Trindade da UFSC. A obra começou em julho de 2013 e devia acabar em novembro de 2014. Dois contratos foram rescindidos (2015 e 2023) e o prédio segue inacabado; em 2026 a UFSC licitou de novo a conclusão, junto com um bloco de salas de aula.',
            'program_context': 'O prédio devia tirar a direção e as coordenações do CFM dos "blocos modulados do centro, construídos na década de 1960" (relatório da gestão da UFSC de 2013); em 2023 a UFSC divulgou o plano de demolição dos modulados.',
            'obrasgov': {'ids': OG_IDS, 'names': {OG_IDS['first']: pf['nome'], OG_IDS['resumption']: pr['nome']},
                         'motives_first': motives_first, 'justification_first': just_first['justificativa'].strip(),
                         'justification_resumption': just_res['justificativa'].strip(), 'next_step': just_first['faseTratativa'].strip(),
                         'registered_on': pr['dataCadastro'], 'api': f'{OG}/execucao-fisica?idUnico=<id>'},
            'sources': [DFO_URL['first'], DFO_URL['resumption'], CGU_URL, NEWS['status_2026'], PNCP_PAGE, COMPRAS_URL.format('201307')],
        },
        'contracts': [
            {'number': '117/2013', 'tender': 'Concorrência nº 11/2012', 'process': None,
             'object': c13['Objeto'].replace('Objeto: ', ''),
             'object_plain': 'Construção do prédio administrativo do CFM (laboratórios, salas de apoio, biblioteca, auditório) e de um elevador no Bloco 29 da Química, 3.441,88 m².',
             'company': 'Julio Cesar de Lima e Silva Ltda (L&S Engenharia; o DFO escreve "Lima e Silva Engenharia e Construtora Ltda - EPP")',
             'company_cnpj': '03611631000135', 'signed_on': '2013-07-18', 'dou_on': '2013-07-23',
             'term_in_record': {'start': '2013-07-18', 'end': '2015-03-24'},
             'value_original_brl': brl(money(c13['Valor Inicial Compra'])), 'value_current_brl': brl(money(c13['Valor Final Compra'])),
             'value_current_note': 'valor final no cadastro de contratos do Portal da Transparência; o único termo aditivo registrado (1/2014) substituiu serviços',
             'executed_brl': brl(executed_13), 'executed_source': {'url': CGU_URL, 'quote': q_cgu_2},
             'status': 'rescindido unilateralmente pela UFSC em 01/06/2015, com 43,26% executado',
             'amendments': [{'act': 'Termo Aditivo 1/2014', 'date': '2014-05-26', 'text': ta13['12014'][9].replace('Objeto: ', ''), 'url': COMPRAS_URL.format('201307')}],
             'source': {'doc': 'Portal da Transparência, dados abertos de Compras (jul/2013)', 'url': COMPRAS_URL.format('201307')},
             'register_record': DFO_URL['first']},
            {'number': '317/2019', 'tender': 'RDC Eletrônico nº 007/2019', 'process': c19['processo'],
             'object': c19['objeto'], 'object_plain': 'Retomada da obra do prédio administrativo do CFM, 3.441,88 m².',
             'company': 'Mendonça e Gonçalves Construções e Incorporações Ltda', 'company_cnpj': '13798155000167',
             'signed_on': c19['data_assinatura'], 'dou_on': c19['data_publicacao'],
             'value_original_brl': brl(value_19), 'value_current_brl': brl(money(hist['00002/2022']['valor_global'])),
             'value_current_note': 'os dois termos aditivos só prorrogaram o prazo; nenhum alterou o valor global (Contratos.gov.br)',
             'bid_estimate_brl': brl(estimate_19), 'bid_saving_brl': brl(saving_19), 'bid_quote': q_rdc,
             'guarantee_brl': brl(guarantee),
             'status': 'rescindido de forma amigável em 23/05/2023 "por razões de conveniência da Administração", com 19,79% executado',
             'amendments': [{'act': f"Termo Aditivo {k.lstrip('0')}", 'date': hist[k]['data_assinatura'], 'text': hist[k]['observacao'].capitalize(), 'url': f'{CT}/{CT_ID}/historico'} for k in ('00001/2021', '00002/2022')],
             'rescission': {'date': '2023-05-23', 'kind': 'amigável', 'legal_basis': 'art. 79, inciso II, da Lei 8.666/93', 'dou_quote': q_dou,
                            'reason_quote': q_resc_1, 'reason_document_public': False, 'extra_services_quote': q_resc_2,
                            'paid_on_rescission_brl': {'extra_services': brl(extra), 'complementary_measurement': brl(complement)}, 'url': RESCISSION_URL},
             'signer_ufsc': {'name': 'Paulo Roberto Pinto da Luz', 'role': 'Secretário de Obras, Manutenção e Ambiente', 'how_read': 'OCR (macOS Vision) da página 34 do PDF digitalizado do contrato, conferido a olho', 'url': CONTRACT_PDF_URL},
             'source': {'doc': 'Contratos.gov.br, contrato 69937', 'url': f'{CT}/inativo/ug/153163'},
             'register_record': DFO_URL['resumption']},
        ],
        'tenders_after': [{'number': 'Concorrência Eletrônica nº 90002/2026', 'pncp': pc['numeroControlePNCP'], 'process': '23080.061723/2025-02',
                           'object': pc['objetoCompra'], 'published_on': pc['dataPublicacaoPncp'][:10], 'estimate_brl': brl(est_26),
                           'estimate_per_m2_brl': 5382.85, 'estimate_per_m2_note': 'edital, resumo do orçamento, data base fev/2026; o resumo não separa o prédio do CFM do bloco novo',
                           'result': {'company': pres['nomeRazaoSocialFornecedor'], 'cnpj': pres['niFornecedor'], 'value_brl': brl(hom_26), 'date': pres['dataResultado']},
                           'contract_found': False, 'contract_note': 'nenhum contrato com este objeto na lista de contratos ativos da UFSC no Contratos.gov.br (assinados até 05/10/2026) nem na busca do PNCP, lidos em 2026-10-06',
                           'registry_name_note': f"a Receita (base de {reg['05901551000140']['base_date']}) traz para este CNPJ a razão social {reg['05901551000140']['legal_name']}, {reg['05901551000140']['city']}; a diferença de nome não foi explicada",
                           'url': PNCP_PAGE, 'api': PNCP}],
        'payments': {
            'total_known_brl_computed': brl(total_known),
            'total_known_note': 'Soma de duas medidas oficiais diferentes do mesmo prédio: o executado no contrato de 2013 (CGU) e o pago no de 2019 (DFO). Valores nominais.',
            'parts': [
                {'contract': '117/2013', 'measure': 'executado antes da paralisação', 'value_brl': brl(executed_13), 'quote': q_cgu_2, 'url': CGU_URL,
                 'paid_brl': None, 'paid_note': 'O total pago à Julio Cesar de Lima e Silva Ltda não foi localizado em fonte aberta lida. Fonte que traz o valor: Portal da Transparência, despesas por favorecido (CNPJ 03.611.631/0001-35, UG 153163, 2013 a 2015), que nesta coleta só respondeu com desafio anti-robô; ou as ordens bancárias do SIAFI desses anos, que a API do Tesouro (STA) não listou para 2013.'},
                {'contract': '317/2019', 'measure': 'pago (bruto)', 'value_brl': brl(paid_res), 'quote': f'Percentual Executado: {pct_res}% (Valor total pago = R$ 1.336.183,59)', 'url': DFO_URL['resumption']}],
            'bank_orders_317_2019': {'source': 'API do Tesouro (sta.api.gov.br), ordens bancárias de cada empenho do contrato no Contratos.gov.br', 'api': f'{CT}/{CT_ID}/empenhos',
                                     'count': len(obs), 'to_company_brl': brl(to_company), 'iss_to_florianopolis_brl': brl(iss), 'total_brl': brl(ob_total),
                                     'by_year_brl': {k: brl(v) for k, v in sorted(by_year.items())},
                                     'note': 'Ordens bancárias líquidas para a empresa e o ISS pago à Prefeitura. Ficam abaixo do pago bruto do DFO porque as retenções federais (DARF e GPS) não são ordens bancárias para esses favorecidos; a diferença não foi conferida documento por documento.'},
            'commitment_without_payment': {'number': e1646['numero'], 'issued_on': e1646['data_emissao'], 'plano_interno': e1646['planointerno'],
                                           'fields_as_published': {k: e1646[k] for k in ('rpinscrito', 'rpliquidado', 'rppago')},
                                           'bank_orders': 0, 'note': 'Empenho de R$ 4.000.000,00 ligado ao contrato, sem ordem bancária na API do Tesouro. Os campos são reproduzidos como publicados; esta pesquisa não interpreta o destino do valor.'},
        },
        'companies': [
            {'cnpj': '03611631000135', **{k: reg['03611631000135'][k] for k in ('legal_name', 'trade_name', 'city', 'registration_status', 'registration_status_date', 'activity_start', 'size', 'main_activity', 'partners')},
             'name_in_ufsc_pages': 'LIMA E SILVA ENGENHARIA E CONSTRUTORA LTDA – EPP', 'contracts': ['117/2013'],
             'portal_transparencia_federal': 'https://portaldatransparencia.gov.br/pessoa-juridica/03611631000135',
             'sanctions_note': 'não consta do CEIS (arquivo de 06/10/2026 do Portal da Transparência), que lista só sanções vigentes',
             'source': {'doc': 'Base aberta do CNPJ da Receita Federal, lida via espelho publica.cnpj.ws', 'url': CNPJ_URL.format('03611631000135'), 'base_date': reg['03611631000135']['base_date']}},
            {'cnpj': '13798155000167', **{k: reg['13798155000167'][k] for k in ('legal_name', 'trade_name', 'city', 'registration_status', 'registration_status_date', 'activity_start', 'size', 'main_activity', 'partners')},
             'contracts': ['317/2019'], 'portal_transparencia_federal': 'https://portaldatransparencia.gov.br/pessoa-juridica/13798155000167',
             'sanctions_note': 'não consta do CEIS (arquivo de 06/10/2026)',
             'name_history': 'em 2021 o DOU registrou a mudança para "Mendonça & Gonçalves Construções e Incorporações Eireli" e a troca do representante legal (retificação do Termo Aditivo 1/2021); a Receita traz hoje a razão social Ltda',
             'source': {'doc': 'Base aberta do CNPJ da Receita Federal, lida via espelho publica.cnpj.ws', 'url': CNPJ_URL.format('13798155000167'), 'base_date': reg['13798155000167']['base_date']}},
        ],
        'people': [
            {'name': 'Rodrigo Bossle Fagundes', 'role': 'Diretor do Departamento de Fiscalização de Obras (DFO) da UFSC', 'side': 'contratante', 'party_at_time': None,
             'role_source': DFO_URL['order_2013'], 'signed': [{'act': 'Ordem de serviço do contrato 117/2013', 'date': '2013-07-22', 'url': DFO_URL['order_2013']}]},
            {'name': 'Paulo Roberto Pinto da Luz', 'role': 'Secretário de Obras, Manutenção e Ambiente (SEOMA) da UFSC', 'side': 'contratante', 'party_at_time': None,
             'role_source': ATAS['2019_11_21'], 'signed': [{'act': 'Contrato 317/2019', 'date': '2019-12-11', 'url': CONTRACT_PDF_URL}],
             'note': 'assinatura lida por OCR na página 34 do contrato digitalizado'},
            {'name': 'Hélio Rodak de Quadros Junior', 'role': 'Prefeito Universitário da UFSC', 'side': 'contratante', 'party_at_time': None,
             'role_source': RESCISSION_URL, 'signed': [{'act': 'Termo de rescisão amigável do contrato 317/2019', 'date': '2023-05-23', 'url': RESCISSION_URL}]},
            {'name': 'Gabriel Mendonça Gonçalves', 'role': 'sócio da contratada (assinou o contrato 317/2019)', 'side': 'contratada', 'role_source': CONTRACT_PDF_URL},
            {'name': 'Igor Mendonça Gonçalves', 'role': 'representante legal da contratada (assinou a rescisão de 2023)', 'side': 'contratada', 'role_source': RESCISSION_URL},
        ],
        'people_note': 'Quem assinou o contrato 117/2013 e a rescisão unilateral de 2015 pela UFSC não aparece em documento aberto lido (o termo de rescisão e o memorando 012/2014/RJ estão só como anexos do Obrasgov, sem link público). Fiscais dos contratos ficam fora da página.',
        'head_of_government': [
            {'name': 'Dilma Rousseff', 'office': 'Presidenta da República', 'party_at_time': 'PT', 'party_note': 'eleita pelo PT em 2010 e em 2014 (TSE)',
             'source': tse_src(2010, 2014), 'relevant_dates': ['2013-07-18 (contrato 117/2013)', '2015-06-01 (rescisão unilateral)']},
            {'name': 'Jair Bolsonaro', 'office': 'Presidente da República', 'party_at_time': None,
             'party_note': 'eleito em 2018 pelo PSL e candidato em 2022 pelo PL (TSE); a filiação na data do contrato de dez/2019 não está em fonte oficial aberta encontrada',
             'source': tse_src(2018, 2022), 'relevant_dates': ['2019-12-11 (contrato 317/2019)']},
            {'name': 'Luiz Inácio Lula da Silva', 'office': 'Presidente da República', 'party_at_time': 'PT', 'party_note': 'eleito pelo PT em 2022 (TSE)',
             'source': tse_src(2022), 'relevant_dates': ['2023-05-23 (rescisão amigável)', '2026-08-10 (resultado da licitação de 2026)']},
            {'name': 'Roselane Neckel', 'office': 'Reitora da UFSC (posse em 08/05/2012; transmitiu o cargo em 10/05/2016)', 'party_at_time': None,
             'party_note': 'reitor de universidade federal não é eleito por partido', 'source': NEWS['rector_2012'] + ' ' + NEWS['rector_2016'],
             'relevant_dates': ['2013-07-18 (contrato 117/2013)', '2015-06-01 (rescisão unilateral)']},
            {'name': 'Ubaldo Cesar Balthazar', 'office': 'Reitor da UFSC (pro tempore desde 27/11/2017; nomeado em 04/07/2018; transmitiu o cargo em 2022)', 'party_at_time': None,
             'party_note': 'reitor de universidade federal não é eleito por partido', 'source': NEWS['rector_2018'],
             'relevant_dates': ['2019-11-27 (RDC 007/2019 homologado)', '2019-12-11 (contrato 317/2019)']},
            {'name': 'Irineu Manoel de Souza', 'office': 'Reitor da UFSC (de 04/07/2022 a 06/07/2026)', 'party_at_time': None,
             'party_note': 'reitor de universidade federal não é eleito por partido', 'source': NEWS['rector_2022'],
             'relevant_dates': ['2023-05-23 (rescisão amigável)', '2026-02-06 (reunião no CFM)', '2026-06-12 (licitação publicada)']},
            {'name': 'Amir de Oliveira', 'office': 'Reitor da UFSC (posse em 06/07/2026)', 'party_at_time': None,
             'party_note': 'reitor de universidade federal não é eleito por partido', 'source': NEWS['rector_2026'],
             'relevant_dates': ['2026-08-10 (resultado da licitação de 2026)']},
        ],
        'head_of_government_note': 'Obra federal: o Presidente da República e o reitor da UFSC na data de cada ato. Nenhum dos dois assina os contratos: assinam a Secretaria de Obras e a Prefeitura Universitária. Partido dos presidentes conforme o registro de candidaturas do TSE.',
        'findings': [
            {'body': 'CGU', 'kind': 'relatório de avaliação dos resultados da gestão', 'process': 'Relatório nº 201702650, constatação 1.1.1.6', 'date': '2019-12-05',
             'summary_quote': q_cgu_2 + ' ' + q_cgu_3,
             'status': 'constatação geral sobre obras paralisadas da UFSC ("ocorreu afronta ao artigo 45 da Lei de Responsabilidade Fiscal"), com recomendação de "Priorizar a finalização de edificações inacabadas nos campi da UFSC"',
             'about_this_contract': 'o CFM aparece como uma das obras paralisadas; a CGU não aponta irregularidade nos contratos do prédio',
             'quotes': {'answer_1_3': q_cgu_1, 'impact': q_cgu_6, 'conclusion': q_cgu_4, 'recommendation': q_cgu_5}, 'url': CGU_URL},
        ],
        'findings_none_note': 'Nenhum acórdão do TCU sobre esta obra foi localizado (pesquisa de acórdãos com quatro combinações de termos em 2026-10-06); nenhuma ação do MPF foi localizada; a busca no MPF não foi feita a fundo.',
        'media': f'{MEDIA}/credits.json',
        'media_note': 'Nenhuma foto de uso livre do prédio foi achada (Wikimedia Commons, por texto e pelos arquivos com coordenada mais próximos); as fotos oficiais da galeria do DFO/UFSC não publicam termos que permitam reutilização. O cartão usa uma foto livre do campus (Reitoria, 2013), com legenda que diz isso.',
        'comparison': {
            'title': 'Custo por m² no contrato assinado, em reais de 2024',
            'subtitle': 'Três prédios contratados pela UFSC em 2013 no campus Trindade: valor inicial do contrato (Portal da Transparência) dividido pela área (DFO/UFSC), corrigido pelo IPCA do mês da assinatura até dez/2024.',
            'unit': 'R$ de dez/2024 por m² construído (valor inicial do contrato)', 'unit_short': 'm²', 'value_key': 'cost_per_m2_brl_2024',
            'method': {'brl_rule': 'IPCA (IBGE, SIDRA 1737) do mês da assinatura até dez/2024', 'value_source': 'Valor Inicial Compra, dados abertos de Compras do Portal da Transparência', 'area_source': 'Área Construída, páginas do DFO/UFSC', 'ipca_url': IPCA_URL},
            'items': [{'id': x['key'], 'name': {'cfm': 'Bloco Administrativo do CFM', 'cce': 'Salas de Aula e Laboratórios de Ensino do CCE', 'cfh': 'Blocos E, F e Anexo E do CFH'}[x['key']],
                       'place': x['place'], 'is_subject': x['key'] == 'cfm',
                       'years': {'cfm': 'contrato de jul/2013; rescindido em 2015, inacabado', 'cce': 'contrato de fev/2013; concluído em 25/01/2017', 'cfh': 'contrato de set/2013; concluído em 06/12/2017'}[x['key']],
                       'contract': x['contract'], 'company': x['company'], 'company_cnpj': x['cnpj'], 'signed_on': x['signed_on'],
                       'contract_value_brl': brl(x['value']), 'contract_final_value_brl': brl(x['final']), 'dfo_contract_value_brl': brl(x['dfo_value']),
                       'area_m2': brl(x['area']), 'contract_month': x['ym'], 'ipca_factor_to_dec2024': brl(x['fac']),
                       'cost_per_m2_brl_nominal': brl(x['per']), 'cost_per_m2_brl_2024': brl(x['per24']),
                       'scope_note': {'cfm': 'prédio administrativo com biblioteca e auditório, mais um elevador no Bloco 29 da Química', 'cce': 'salas de aula e laboratórios de ensino de Design, Artes Cênicas e Cinema', 'cfh': 'laboratórios de ensino e pesquisa de Geologia e Oceanografia; recursos da Petrobras e da UFSC (DFO)'}[x['key']],
                       'sources': [{'field': 'valor', 'url': COMPRAS_URL.format({'201307': '201307', '201302': '201302', '201309': '201310'}[x['ym']])}, {'field': 'área e situação', 'url': x['url_dfo']}]} for x in comp],
            'gap_flag': False,
            'reading': ('No contrato assinado, o metro quadrado do prédio do CFM (R$ {cfm} em reais de 2024) ficou abaixo do dos dois outros prédios '
                        'contratados pela UFSC no mesmo ano e campus (R$ {cce} no CCE e R$ {cfh} no CFH). Os dois foram concluídos em 2017; '
                        'o do CFM teve o contrato rescindido em 2015 com 43,26% executado e segue inacabado.').format(
                **{x['key']: f"{float(x['per24']):,.0f}".replace(',', '.') for x in comp}),
            'caveats': ['Valores de contrato assinado, não de pagamento.',
                        'As páginas do DFO trazem "Valor Contratado" diferente do valor inicial do Portal no CCE (R$ 13.095.521,80) e no CFH (R$ 18.668.699,57); no CFM os dois batem. A comparação usa o valor inicial do Portal nos três.',
                        'O contrato do CFM inclui um elevador no Bloco 29 da Química.'],
        },
        'card': {
            'title': 'Prédio do CFM (UFSC)', 'subtitle': 'Prédio começado em 2013 e parado desde 2023', 'place': 'Florianópolis',
            'stats': [
                {'label': 'Investimento total (executado e pago)', 'value': brl(total_known), 'unit': 'BRL', 'display': disp(total_known),
                 'note': f'{disp(executed_13)} executados no contrato de 2013 (CGU) e {disp(paid_res)} pagos no de 2019 (UFSC); valores nominais'},
                {'label': 'Contrato inicial (2013)', 'value': brl(money(c13['Valor Inicial Compra'])), 'unit': 'BRL', 'display': disp(money(c13['Valor Inicial Compra'])),
                 'note': 'Julio Cesar de Lima e Silva Ltda; 3.441,88 m²'},
                {'label': 'Parado', 'value': '2023-05-23', 'unit': 'date', 'display': 'desde mai/2023',
                 'note': 'e de jun/2015 a jan/2020; "paralisado há mais de dez anos" (UFSC, fev/2026)'},
                {'label': 'Licitação de 2026', 'value': brl(hom_26), 'unit': 'BRL', 'display': disp(hom_26),
                 'note': 'homologada em 10/08/2026, com um bloco novo de salas (5.101,16 m² no total); contrato não localizado'},
            ],
            'head': {'investment_total': {'label': 'Investimento total (executado e pago)', 'value_brl': brl(total_known), 'display': disp(total_known),
                                          'note': f'{disp(executed_13)} executados no contrato de 2013 (CGU, Relatório 201702650) e {disp(paid_res)} pagos no contrato de 2019 (DFO/UFSC); valores nominais; o pago do contrato de 2013 não foi localizado'},
                     'initial_contract': {'label': 'Contrato inicial (2013)', 'value_brl': brl(money(c13['Valor Inicial Compra'])), 'display': disp(money(c13['Valor Inicial Compra'])),
                                          'note': 'contrato 117/2013, Julio Cesar de Lima e Silva Ltda'}},
            'photo': f'{MEDIA}/campus-trindade-reitoria-2013.jpg',
        },
        'terms_check': 'Nenhuma fonte lida usa "superfaturamento", "sobrepreço", "desvio" ou "improbidade" para esta obra: ' + '; '.join(f"{k}: {', '.join(v) if v else 'nenhum'}" for k, v in terms_found.items()) + '.',
        'gaps': [
            'Total pago no contrato 117/2013 (2013 a 2015): não publicado em fonte aberta lida; a CGU dá o executado (R$ 3.061.830,69).',
            'Quem assinou o contrato de 2013 e a rescisão de 2015 pela UFSC.',
            'Motivo detalhado das duas rescisões: o memorando 012/2014/RJ, o termo de rescisão unilateral de 2015 e o Ofício 098/2022/DFO-SEOMA não estão publicados.',
            'Se a Concorrência 90002/2026 virou contrato: nenhum contrato localizado até 06/10/2026.',
            'Quanto custa só terminar o prédio do CFM: o orçamento de 2026 (R$ 27.458.789,03) junta a conclusão com um bloco novo de salas e não separa as partes.',
            'Foto de uso livre do prédio.',
        ],
    }

    # dashes: the record must not carry em or en dashes (control first)
    bad = (chr(0x2014), chr(0x2013))
    if not any(b in 'controle ' + chr(0x2014) for b in bad):
        raise SystemExit('checagem de travessões não acha o controle')
    rec = C.no_dashes(rec)
    check('JSON sem travessão nem meia-risca', sum(json.dumps(rec, ensure_ascii=False).count(b) for b in bad), 0)
    rec['checks'] = checks
    json.dump(rec, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(f'{len(checks)} checagens ok; gravado {os.path.relpath(OUT, ROOT)}')


if __name__ == '__main__':
    W = sys.argv[1]
    if '--fetch' in sys.argv:
        fetch(W)
    else:
        main(W, control='--control' in sys.argv)
