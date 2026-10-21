"""Monta data/works/br-470-duplicacao.json a partir das entradas baixadas por roads_download.sh.

Uso: python3 build_br470.py <workdir>
Números vêm dos arquivos oficiais do <workdir>; citações literais são conferidas contra o texto
do documento (common.require_quote) e o script para se alguma não bater.
"""
import csv, io, json, os, re, sys, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roads_common as C

W = sys.argv[1] if len(sys.argv) > 1 else '.'
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
OUT = os.path.join(ROOT, 'data', 'works', 'br-470-duplicacao.json')
COLLECTED = '2026-09-30'
C.self_test()
IPCA = C.load_ipca(W)
p = lambda *a: os.path.join(W, *a)
q = C.require_quote
n = C.num_br

CGOV = 'https://contratos.comprasnet.gov.br/api/contrato/{}/historico'
CGOV_UG = 'https://contratos.comprasnet.gov.br/api/contrato/ug/{}'
COMPRAS = 'https://dadosabertos.compras.gov.br/modulo-contratos/1_consultarContratos?codigoOrgao=39252&codigoUnidadeGestora=393013'
DOU = 'https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=3&pagina={p}&data={d}&captchafield=firstAccess'
TCU = 'https://pesquisa.apps.tcu.gov.br/doc/acordao-completo/{n}/{y}/Plen%C3%A1rio'
TCU_API = 'https://pesquisa.apps.tcu.gov.br/rest/publico/base/acordao-completo/documento?termo=KEY:ACORDAO-COMPLETO-{k}&quantidade=1&inicio=0'
PORTAL = 'https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/AAAAMM'
SIOP = 'https://www1.siop.planejamento.gov.br/sparql/'
API_SC = 'https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]='
URL_CSV = 'https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/ff7c3cac-3e38-4801-9fd8-e4ccb69ca31d/download/contratos.csv'
TSE = 'https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{}.zip'
PORTAL_PJ = 'https://portaldatransparencia.gov.br/pessoa-juridica/{}'

# ------------------------------------------------------------------ fontes
ug13 = {c['id']: c for c in json.load(open(p('br470', 'cgov_393013.json')))}
ug03 = {c['id']: c for c in json.load(open(p('br470', 'cgov_393003.json')))}
hist = lambda i: json.load(open(p('br470', 'cgov', f'{i}_historico.json')))
hist_text = lambda i: ' '.join((x.get('observacao') or '') for x in hist(i))
compras = {r['numeroContrato']: r for r in json.load(open(p('br470', 'comprasgov_br470.json'))) if r['codigoUnidadeGestora'] in ('393013', '393003')}
dou13 = C.pdf_text(p('br470', 'dou_26-07-2013_141.pdf'))
dou14a = C.pdf_text(p('br470', 'dou_14-02-2014_218.pdf'))
dou14b = C.pdf_text(p('br470', 'dou_29-05-2014_140.pdf'))
t1704 = C.tcu_text(p('br470', 'd_2362146.json'))
t1886 = C.tcu_text(p('br470', 'd_2535085.json'))
t2205 = C.tcu_text(p('br470', 'd_2683534.json'))
t2718 = C.tcu_text(p('br470', 'd_2733019.json'))
t2207 = C.tcu_text(p('br470', 'd_2632499.json'))

# ------------------------------------------------------------------ contratos dos 4 lotes
def aditivos(i):
    h = hist(i)
    ta = sorted({x['numero'] for x in h if x['tipo'] == 'Termo Aditivo'})
    ap = sorted({x['numero'] for x in h if x['tipo'] == 'Termo de Apostilamento'})
    last = max((x['data_assinatura'] for x in h if x['tipo'] != 'Contrato'), default=None)
    return {'termos_aditivos': len(ta), 'apostilamentos': len(ap), 'ultimo_ato': last,
            'value_changes': [{'date': x['data_assinatura'], 'number': x['numero'], 'type': x['tipo'],
                               'qualification': ', '.join(t['descricao'] for t in (x.get('qualificacao_termo') or [])),
                               'text': ' '.join((x['observacao'] or '').split())[:600]}
                              for x in sorted(h, key=lambda x: x['data_assinatura'] or '')
                              if any(t['descricao'] in ('ACRÉSCIMO / SUPRESSÃO', 'REAJUSTE') for t in (x.get('qualificacao_termo') or []))]}

LOTS = [
    dict(lot='1', number='01093/2013', cid=80967, legacy=106726, km=(0.00, 18.61), base='201402', base_note='mês de assinatura',
         pi=235771658.01, pi_quote='R$ 235.771.658,01', pir=None,
         dou=(dou14a, 'Vigência: 13/02/2014 a 22/04/2018. Valor Total: R$192.987.332,27. Data de Assinatura: 13/02/2014.', '14/02/2014', 218),
         contractor='Consórcio Azza-Sogel (2014); Sucesso-Azza-Sogel (2017); Planaterra-Azza-Sogel (2020); Planaterra/Sogel (2025)',
         contractor_quote='o CONSÓRCIO AZZA - SOGEL', cnpj_record='82743832000162',
         cnpj_history=[('85115053000100', 'Terraplenagem Azza (CNPJ do contrato em 2014)'), ('09588906000143', 'Construtora Sucesso S.A. (líder a partir do TA 4/2017)'), ('82743832000162', 'Planaterra (líder a partir do TA 8/2020)')],
         original=192987332.27, tender='RDC presencial 200/2013', process='50616.000597/2013-55'),
    dict(lot='2', number='00355/2014', cid=80916, legacy=None, km=(18.61, 44.87), base='201305', base_note='data-base informada pelo TCU (Acórdão 1704/2019): maio/2013',
         pi=364979641.58, pi_quote='R$ 364.979.641,58', pir=528670647.76,
         dou=(dou14b, 'Vigência: 28/05/2014 a 04/08/2018. Valor Total: R$293.590.000,00.', '29/05/2014', 140),
         contractor='Consórcio Ivaí-Setep (Ivaí líder; participação 50%/50% desde o TA 1/2015)', contractor_quote='o CONSÓRCIO IVAÍ-SETEP',
         cnpj_record='76592542000162', cnpj_history=[('76592542000162', 'Ivaí Engenharia de Obras S.A. (líder)'), ('83665141000150', 'Setep Construções S.A.')],
         original=293590000.00, tender='RDC presencial 222/2013', process='50616.002153/2013-54'),
    dict(lot='3', number='00703/2013', cid=98313, legacy=76826, km=(44.87, 57.78), base='201307', base_note='mês de assinatura',
         pi=182249431.84, pi_quote='R$ 182.249.431,84', pir=350938127.82,
         dou=(dou13, 'Valor Total: R$167.555.244,30. Fonte: 100000000 - 2013NE801771. Data de Assinatura: 17/07/2013.', '26/07/2013', 141),
         contractor='Sulcatarinense Mineração, Artefatos de Cimento, Britagem e Construções Ltda.', contractor_quote='SULCATARINENSE',
         cnpj_record='76614254000161', cnpj_history=[('76614254000161', 'Sulcatarinense')],
         original=167555244.30, tender='RDC presencial 181/2012', process='50616.001430/2012-21'),
    dict(lot='4', number='00603/2013', cid=80873, legacy=None, km=(57.78, 73.18), base='201306', base_note='mês de assinatura',
         pi=209075950.13, pi_quote='R$ 209.075.950,13', pir=424765272.50,
         dou=(dou13, 'Valor Total: R$205.915.971,00. Fonte: 100000000 - 2013NE801467. Data de Assinatura: 13/06/2013.', '26/07/2013', 141),
         contractor='Sulcatarinense Mineração, Artefatos de Cimento, Britagem e Construções Ltda.', contractor_quote='SULCATARINENSE',
         cnpj_record='76614254000161', cnpj_history=[('76614254000161', 'Sulcatarinense')],
         original=205915971.00, tender='RDC presencial 191/2012', process='50616.001853/12-41'),
]
q('(data-base: maio/2013)', t1704, 'TCU 1704/2019')
q('VISSILAR PRETTO Superintendente', dou14b, 'DOU 29/05/2014')

contracts = []
for L in LOTS:
    rec = ug13[L['cid']]
    q(L['dou'][1], L['dou'][0], f"DOU lote {L['lot']}")
    q(L['contractor_quote'], L['dou'][0], f"DOU lote {L['lot']}")
    q(L['pi_quote'], hist_text(L['cid']), f"histórico lote {L['lot']}")
    if L['pir']:
        assert C.num_br(rec['valor_global']) == L['pir'], (L['lot'], rec['valor_global'])
    ad = aditivos(L['cid'])
    contracts.append({
        'group': 'obra', 'lot': L['lot'], 'number': L['number'], 'km_from': L['km'][0], 'km_to': L['km'][1], 'length_km': round(L['km'][1] - L['km'][0], 2),
        'object': ' '.join((compras.get(L['number'], {}).get('objeto') or rec['objeto']).split()),
        'company': L['contractor'], 'company_in_record': rec['fornecedor']['nome'], 'cnpj_in_record': L['cnpj_record'], 'cnpj_history': [{'cnpj': c, 'note': t} for c, t in L['cnpj_history']],
        'signed_on': rec['data_assinatura'], 'tender': L['tender'], 'process': L['process'],
        'term_original_in_dou': L['dou'][1], 'end_current': rec['vigencia_fim'],
        'value_original_brl': L['original'], 'value_current_initial_prices_brl': L['pi'],
        'value_global_current_brl': C.num_br(rec['valor_global']),
        'value_global_note': 'Valor global no registro (preços iniciais + reajustamento, inclusive reequilíbrios pelo preço do asfalto).' if L['pir'] else
                             'O registro mostra só o valor a preços iniciais; os reequilíbrios de asfalto deste lote (2021 a 2023) não somam valor global no registro.',
        'price_base_month': f"{L['base'][:4]}-{L['base'][4:]}", 'price_base_note': L['base_note'],
        'amendments': ad, 'status_in_record': rec['situacao'],
        'sources': [{'doc': f"Extrato no DOU, Seção 3, {L['dou'][2]}, p. {L['dou'][3]}", 'url': DOU.format(p=L['dou'][3], d=L['dou'][2])},
                    {'doc': 'Contratos.gov.br, histórico do contrato (API pública)', 'url': CGOV.format(L['cid'])},
                    {'doc': 'Contratos.gov.br, contratos da UG 393013 (SR/DNIT-SC)', 'url': CGOV_UG.format(393013)}]
                   + ([{'doc': 'Registro anterior do mesmo contrato', 'url': CGOV.format(L['legacy'])}] if L['legacy'] else []),
    })

def support(number, cid=None, ug=None, role=''):
    if cid:
        rec = (ug13.get(cid) or ug03.get(cid))
        return {'group': 'apoio', 'number': number, 'role': role, 'object': ' '.join(rec['objeto'].split()),
                'company': rec['fornecedor']['nome'], 'cnpj_in_record': re.sub(r'\D', '', rec['fornecedor']['cnpj_cpf_idgener']),
                'signed_on': rec['data_assinatura'], 'end_current': rec['vigencia_fim'],
                'value_original_brl': C.num_br(rec['valor_inicial']), 'value_global_current_brl': C.num_br(rec['valor_global']),
                'sources': [{'doc': 'Contratos.gov.br (API pública)', 'url': CGOV.format(cid)}]}
    r = compras[number]
    return {'group': 'apoio', 'number': number, 'role': role, 'object': ' '.join(r['objeto'].split()),
            'company': r['nomeRazaoSocialFornecedor'], 'cnpj_in_record': r['niFornecedor'],
            'signed_on': None, 'start': r['dataVigenciaInicial'][:10], 'end_current': r['dataVigenciaFinal'][:10],
            'value_original_brl': None, 'value_global_current_brl': r['valorGlobal'],
            'value_note': 'Só o "valor global" do registro de compras; histórico de aditivos não disponível (contrato encerrado, fora da API de contratos ativos).',
            'sources': [{'doc': 'Dados abertos de compras do governo federal, módulo contratos', 'url': COMPRAS}]}

contracts += [
    support('00729/2013', role='supervisão dos lotes 3 e 4 (lote único na licitação)'),
    support('00563/2014', role='supervisão dos lotes 1 e 2'),
    support('01055/2013', cid=80935, role='gestão ambiental (2013 a 2023)'),
    support('00059/2023', role='supervisão (consórcio MPB-Enecon, 2023 a 2024)'),
    support('00332/2023', cid=204225, role='gestão ambiental (desde 2023)'),
    support('00606/2024', cid=327515, role='supervisão (desde 2024)'),
]
works = [c for c in contracts if c['group'] == 'obra']
totals = {
    'works_contracts': 4, 'length_km': round(sum(c['length_km'] for c in works), 2),
    'value_original_brl': round(sum(c['value_original_brl'] for c in works), 2),
    'value_current_initial_prices_brl': round(sum(c['value_current_initial_prices_brl'] for c in works), 2),
    'value_global_current_brl_as_recorded': round(sum(c['value_global_current_brl'] for c in works), 2),
    'support_contracts_value_brl_as_recorded': round(sum(c['value_global_current_brl'] or 0 for c in contracts if c['group'] == 'apoio'), 2),
    'note': 'Somas calculadas. O total "como registrado" mistura o lote 1 (só preços iniciais) com os lotes 2 a 4 (preços iniciais + reajustamento).',
}

# ------------------------------------------------------------------ pagamentos (União + Estado)
pay = C.require_complete_months(json.load(open(p('br470', 'br470_payments.json'))), 'br470_payments.json')
siop = {y['year']: sum(float(r.get('pagoT') or 0) for r in y['rows']) for y in json.load(open(p('br470', 'siop_br470.json')))['years']}
by = collections.defaultdict(lambda: {'paid_in_year_brl': 0.0, 'prior_year_commitments_paid_brl': 0.0})
by_plan = collections.defaultdict(float)
for r in pay['by_year']:
    if r['acao'] in ('7530', '7X58'):
        by[int(r['year'])]['paid_in_year_brl'] += r['pago']
        by[int(r['year'])]['prior_year_commitments_paid_brl'] += r['rp_pago']
        by_plan[r['plano_orcamentario']] += r['pago'] + r['rp_pago']
fed_rows = []
for y in sorted(by):
    v = by[y]
    fed_rows.append({'year': y, 'paid_in_year_brl': round(v['paid_in_year_brl'], 2), 'prior_year_commitments_paid_brl': round(v['prior_year_commitments_paid_brl'], 2),
                     'total_brl': round(v['paid_in_year_brl'] + v['prior_year_commitments_paid_brl'], 2),
                     'siop_paid_in_year_brl': siop.get(y), 'diff_vs_siop_brl': round(v['paid_in_year_brl'] - siop.get(y, 0), 2)})
    if y <= 2025:
        assert abs(v['paid_in_year_brl'] - siop.get(y, 0)) < 1.0, (y, v, siop.get(y))
fed_total = round(sum(r['total_brl'] for r in fed_rows), 2)

tc = json.load(open(p('br470', 'sc_tc470.json')))
state_rows = collections.defaultdict(float)
state_by_record = []
for k, v in tc.items():
    res = v['extrato']['contratoResumoFinanceiro']
    for r in res:
        state_rows[int(r['ano'])] += float(r['vlpago'])
    state_by_record.append({'record': k, 'company': v['row']['CONTRATADO'], 'cnpj': v['row']['IDCONTRATADO'],
                            'value_current_brl': float(v['row']['VLATUAL']), 'status': v['row']['SITUACAO'],
                            'paid_by_year_brl': {r['ano']: float(r['vlpago']) for r in res}, 'url': v['url'].replace('%5B%5D', '[]')})
state_total = round(sum(state_rows.values()), 2)

payments = {
    'federal': {
        'source': {'doc': 'Portal da Transparência (CGU), arquivos mensais de execução da despesa; conferido com o SIOP (dados abertos do orçamento)', 'url': PORTAL, 'check_url': SIOP, 'collected_on': COLLECTED},
        'budget_actions': ['7530 Adequação de Trecho Rodoviário - Navegantes - Rio do Sul - na BR-470/SC', '7X58 Adequação de Trecho Rodoviário - Navegantes - Indaial - na BR-470/SC (só em 2017)'],
        'by_year': fed_rows, 'total_2014_to_sep2026_brl_computed': fed_total,
        'by_budget_plan_brl_computed': {k: round(v, 2) for k, v in sorted(by_plan.items(), key=lambda x: -x[1])},
        'checks': ['O valor pago no próprio ano bate com o SIOP ao centavo de 2014 a 2025 (arredondamento do SIOP). 2026 difere em R$ 13 mil porque as duas bases têm datas de carga diferentes.'],
        'caveats': ['É pagamento da ação orçamentária, não de um contrato: inclui obra, supervisão, gestão ambiental e desapropriações do trecho Navegantes - Rio do Sul.',
                    '2013: os arquivos mensais do Portal devolveram HTTP 403; o SIOP registra pagamento no ano de R$ 0 em 2013 (restos a pagar de 2013 não verificados).',
                    'Meses de out a dez/2026 ainda não existem.'],
    },
    'state_of_sc': {
        'source': {'doc': 'Registro de contratos SIGEF (dados.sc.gov.br) e extratos SICOP: registros "TC-00470/2021" do Termo de Cooperação com o DNIT (processo 50600.020368/2021-36, SIE 21994/2021)', 'url': URL_CSV, 'collected_on': COLLECTED},
        'by_year_brl': {y: round(v, 2) for y, v in sorted(state_rows.items())}, 'total_brl_computed': state_total,
        'by_record': state_by_record,
        'note': 'O Estado pagou diretamente às contratadas dos lotes 1, 3 e 4, da supervisão e da gestão ambiental, como aporte a obra federal. O lote 2 não aparece entre esses registros.',
    },
    'total_public_paid_brl_computed': round(fed_total + state_total, 2),
    'tcu_execution_quote': q('Duplicação da BR-470/SC (Navegantes - Rio do Sul) (04 lotes) 1.669.899.804,20 1.896.069.990,08 79% 1,14', t2205, 'TCU 2205/2024'),
}

# ------------------------------------------------------------------ empresas
def receita(cnpj):
    for f, base in ((p('rf', f'{cnpj}.json'), 'https://minhareceita.org/'), (p('rf', f'ba_{cnpj}.json'), 'https://brasilapi.com.br/api/cnpj/v1/')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d.get('razao_social'):
            return d, base + cnpj
    return None, None

registry_names = {}
for c in contracts:
    registry_names.setdefault(c['cnpj_in_record'], c.get('company_in_record') or c['company'])
extra = {'85115053000100': 'TERRAPLENAGEM AZZA (nome no DOU de 14/02/2014)', '09588906000143': 'CONSTRUTORA SUCESSO SA (registro do TA 4/2017)',
         '83665141000150': 'SETEP CONSTRUCOES S.A (consorciada do lote 2)', '92694348000144': 'SOCIEDADE GERAL DE EMPREITADAS LIMITADA (SOGEL)'}
companies = []
role = {'82743832000162': ['01093/2013 (lote 1, líder desde 2020)'], '85115053000100': ['01093/2013 (lote 1, líder em 2014)'],
        '09588906000143': ['01093/2013 (lote 1, líder de 2017 a 2020)'], '92694348000144': ['01093/2013 (lote 1, consorciada "Sogel")'],
        '76592542000162': ['00355/2014 (lote 2, líder)'], '83665141000150': ['00355/2014 (lote 2, consorciada)'],
        '76614254000161': ['00703/2013 (lote 3)', '00603/2013 (lote 4)'], '83256172000158': ['00729/2013 (supervisão)'],
        '80996861000100': ['00563/2014 e 00606/2024 (supervisão)'], '78221066000107': ['01055/2013 e 00332/2023 (gestão ambiental); 00059/2023 (supervisão, líder do consórcio)']}
for cnpj, contracts_of in role.items():
    d, url = receita(cnpj)
    companies.append({
        'cnpj': cnpj, 'legal_name': (d and d['razao_social']) or None, 'name_in_contract_record': registry_names.get(cnpj) or extra.get(cnpj),
        'trade_name': d and (d.get('nome_fantasia') or None), 'city': d and f"{d.get('municipio')}/{d.get('uf')}",
        'registration_status': d and d.get('descricao_situacao_cadastral'), 'head_or_branch': d and d.get('descricao_identificador_matriz_filial'),
        'contracts': contracts_of,
        'identity_note': 'Sogel: ligação ao consórcio só pelo nome "SOGEL" nos termos aditivos; o CNPJ vem de outro contrato do DNIT com a "SOCIEDADE GERAL DE EMPREITADAS LTDA - SOGEL".' if cnpj == '92694348000144' else None,
        'official_website': None, 'official_website_note': 'Não verificado nesta coleta; deixado vazio pela regra do projeto.',
        'transparency_links': [PORTAL_PJ.format(cnpj)],
        'source': {'doc': 'Base aberta do CNPJ da Receita Federal via espelho', 'url': url, 'collected_on': COLLECTED} if d else
                  {'doc': 'Cadastro da Receita não lido (espelhos indisponíveis, HTTP 503, em 2026-09-30); nome conforme o registro de contratos', 'url': None},
    })

# ------------------------------------------------------------------ pessoas
def tse(year, uf, name, office):
    z = zipfile.ZipFile(p('tse', f'consulta_cand_{year}.zip'))
    r = csv.reader(io.TextIOWrapper(z.open(f'consulta_cand_{year}_{uf}.csv'), encoding='latin1'), delimiter=';')
    h = next(r); ix = {c: i for i, c in enumerate(h)}
    for row in r:
        if name in row[ix['NM_CANDIDATO']] and row[ix['DS_CARGO']] == office and row[ix['DS_SIT_TOT_TURNO']] == 'ELEITO':
            return row[ix['SG_PARTIDO']], row[ix['NM_PARTIDO']]
    raise KeyError(name)

dilma = tse(2010, 'BR', 'DILMA VANA ROUSSEFF', 'PRESIDENTE')
lula = tse(2022, 'BR', 'LUIZ INÁCIO LULA DA SILVA', 'PRESIDENTE')
people = [
    {'name': 'Vissilar Pretto', 'role': 'Superintendente Regional do DNIT em Santa Catarina (unidade contratante, UASG 393013)',
     'on_dates': ['2014-05-28 (assinatura do lote 2)'],
     'note': 'Os extratos dos contratos no DOU (formato SICON) não trazem o nome de quem assinou. Na mesma edição de 29/05/2014, ele assina como Superintendente um aviso de licitação da mesma unidade, datado de 28/05/2014.',
     'source': [{'doc': 'DOU, Seção 3, 29/05/2014, p. 140', 'url': DOU.format(p=140, d='29/05/2014')}]},
    {'name': 'Dilma Rousseff', 'full_name': 'Dilma Vana Rousseff', 'role': 'Presidenta da República', 'head_of_government': True,
     'on_dates': ['2013-06-13 (lote 4)', '2013-07-17 (lote 3)', '2014-02-13 (lote 1)', '2014-05-28 (lote 2)'],
     'party_at_time': dilma[0], 'party_name': dilma[1].title(),
     'term_note': 'Eleita em 2010 para o mandato 2011 a 2014 (TSE). A biografia oficial da Biblioteca da Presidência estava "em manutenção" na coleta.',
     'source': [{'doc': 'TSE, candidaturas 2010 (BR), situação "ELEITO" no 2º turno', 'url': TSE.format(2010)}]},
    {'name': 'Luiz Inácio Lula da Silva', 'role': 'Presidente da República', 'head_of_government': True,
     'on_dates': ['2024-10-18 (supervisão 00606/2024)', '2026-09-28 (reequilíbrios dos lotes 2, 3 e 4)'],
     'party_at_time': lula[0], 'party_name': lula[1].title(),
     'term_note': 'Eleito em 2022 para o mandato 2023 a 2026 (TSE).',
     'source': [{'doc': 'TSE, candidaturas 2022 (BR)', 'url': TSE.format(2022)}]},
]
people_gaps = ['Superintendente Regional do DNIT em SC nas assinaturas de 2013 (lotes 3 e 4) e de fevereiro de 2014 (lote 1): não encontrado nas páginas do DOU lidas.',
               'Diretor-Geral do DNIT nas datas das assinaturas: não verificado.',
               'Governadores de SC não entram: a obra é federal. O Estado aportou recursos a partir de 2021 (ver pagamentos).']

# ------------------------------------------------------------------ achados
f1 = q('determinar ao Dnit que, no prazo de 60 (sessenta) dias, apresente a este Tribunal documento probatório da obtenção das autorizações de proprietários para uso dos terrenos privados ao longo da faixa de domínio, em especial, daqueles em que já houverem sido executadas intervenções no âmbito do Contrato 355/2014', t1704, 'TCU 1704/2019')
f2 = q('sobrepreço no orçamento de referência decorrente da previsão em duplicidade de equipamentos para a fabricação de concreto', t1886, 'TCU 1886/2022')
f2b = q('emissão da ordem de serviço das obras sem a prévia publicação da Declaração de Utilidade Pública dos imóveis abrangidos pelo empreendimento', t1886, 'TCU 1886/2022')
f2c = q('Assim, o possível sobrepreço de R$ 510.205,50 corresponderia a somente 0,3% do valor contratado, sendo considerado de baixa materialidade frente ao desconto concedido pela empresa', t1886, 'TCU 1886/2022')
f3 = q('Duplicação da BR-470/SC (Navegantes - Rio do Sul) (04 lotes) 4,9 13,6 2,79 NNN', t2205, 'TCU 2205/2024')
f3b = q('Duplicação da BR-470/SC (Navegantes - Rio do Sul) (04 lotes) 1.669.899.804,20 1.896.069.990,08', t2718, 'TCU 2718/2025')
f4 = q('BR-470/SC - Adequação - Navegantes - Rio do Sul 8% 207%', t2207, 'TCU 2207/2023')
terms = {}
for lab, t in (('1704/2019', t1704), ('1886/2022', t1886)):
    terms[lab] = sorted(set(m.lower() for m in re.findall(r'(?i)superfatur\w*|sobrepre\w*|desvio\w*', t)))
assert re.findall(r'(?i)superfatur\w*|sobrepre\w*', 'houve sobrepreço e superfaturamento')

findings = [
    {'body': 'TCU', 'process': 'TC 016.019/2017-2', 'decision': 'Acórdão 1704/2019-Plenário (relator Bruno Dantas)', 'date': '2019-07-24',
     'scope': 'Auditoria do lote 2 (Contrato 355/2014)', 'summary_quote': f1,
     'status': 'determinação ao DNIT com monitoramento pela unidade técnica; resultado do monitoramento não localizado',
     'url': TCU.format(n=1704, y=2019), 'api': TCU_API.format(k=2362146)},
    {'body': 'TCU', 'process': 'TC 014.951/2021-5', 'decision': 'Acórdão 1886/2022-Plenário (relator Bruno Dantas)', 'date': '2022-08-17',
     'scope': 'Auditoria do lote 3 (Contrato 703/2013)', 'summary_quote': f2, 'second_quote': f2b, 'materiality_quote': f2c,
     'status': 'ciência ao DNIT ("para que sejam adotadas medidas internas com vistas à prevenção de outras ocorrências semelhantes") e arquivamento; sem multa nem débito',
     'names_note': 'O cabeçalho lista dois "responsáveis" (termo processual); o acórdão não aplicou sanção a pessoas, e por isso os nomes não são reproduzidos aqui.',
     'url': TCU.format(n=1886, y=2022), 'api': TCU_API.format(k=2535085)},
    {'body': 'TCU', 'process': 'TC 014.989/2024-7 e TC 000.866/2025-3', 'decision': 'Acórdãos 2205/2024 e 2718/2025-Plenário (indicadores de valor e de prazo de obras)',
     'date': '2024-10-16 e 2025-11-18', 'summary_quote': f3, 'value_quote': f3b,
     'reading': 'Valor inicial de referência R$ 1,670 bi e valor final atual R$ 1,896 bi (ambos corrigidos pelo IPCA pelo TCU): iValor 1,14, isto é, 14% acima. Prazo inicial de 4,9 anos e prazo final atual de 13,6 anos: iPrazo 2,79. "NNN" é a pior classe da expectativa de prazo na escala do TCU.',
     'status': 'avaliação de desempenho; não é achado de irregularidade', 'url': TCU.format(n=2205, y=2024), 'extra_urls': [TCU.format(n=2718, y=2025)]},
    {'body': 'TCU', 'process': 'TC 021.176/2022-1', 'decision': 'Acórdão 2207/2023-Plenário (Fiscobras 2023)', 'date': '2023-11-01', 'summary_quote': f4,
     'status': 'teste dos indicadores (versão anterior da fórmula); sem determinação sobre a obra', 'url': TCU.format(n=2207, y=2023)},
    {'body': 'CGU, MPF, Justiça Federal', 'process': None, 'summary_quote': None,
     'status': 'Nenhum relatório da CGU, ação do MPF ou decisão judicial sobre a duplicação localizada nesta coleta (uma busca na web; sistemas da CGU, do MPF e do TRF4 não consultados por número).', 'url': None},
]

# ------------------------------------------------------------------ comparação
ug27 = {c['id']: c for c in json.load(open(p('comp', 'cgov_393027.json')))}
ug17 = {c['id']: c for c in json.load(open(p('comp', 'cgov_393017.json')))}
ug13c = {c['id']: c for c in json.load(open(p('comp', 'cgov_393013.json')))}
htxt = lambda i: ' '.join((x.get('observacao') or '') for x in json.load(open(p('comp', f'h_{i}.json'))))
q('R$ R$ 344.301.403,99', htxt(80981), 'BR-280 lote 1')
q('MÊS-BASE DE MARÇO DE 2014', htxt(80981), 'BR-280 lote 1')
q('PARA R$ 151.206.675,59', htxt(81007), 'BR-280 lote 2.1')
q('R$ 596.092.029,89', htxt(81065), 'BR-280 lote 2.2')
q('PARA R$ 317.837.148,73, A PREÇOS INICIAIS', htxt(81013), 'BR-230/PB')

def part(value, ym, km):
    f = C.ipca_factor(IPCA, ym)
    return {'value_brl': value, 'price_base_month': f'{ym[:4]}-{ym[4:]}', 'ipca_index_base_month': IPCA[ym],
            'ipca_factor_to_dec2024': round(f, 6), 'value_brl_2024': round(value * f, 2), 'length_km': km}

def comp(name, parts, scope, category, sources, basis):
    tot = sum(x['value_brl_2024'] for x in parts); km = round(sum(x['length_km'] for x in parts), 2)
    return {'name': name, 'category': category, 'scope': scope, 'lanes': '2 para 4 faixas (duplicação)', 'length_km': km,
            'cost_reported_brl': round(sum(x['value_brl'] for x in parts), 2), 'cost_basis': basis, 'parts': parts,
            'cost_brl_2024': round(tot, 2), 'cost_per_km_brl_2024': round(tot / km, 2), 'sources': sources}

this = comp('BR-470/SC, duplicação Navegantes - Indaial (4 lotes)',
            [part(L['pi'], L['base'], round(L['km'][1] - L['km'][0], 2)) for L in LOTS],
            'Duplicação, restauração da pista existente, ruas laterais, viadutos e pontes; trecho urbano e periurbano no Vale do Itajaí.',
            'SC, urbana e periurbana, com obras de arte', [{'url': CGOV.format(L['cid'])} for L in LOTS],
            'Soma dos 4 contratos de obra a preços iniciais vigentes (com aditivos de quantidade, sem reajustamento). Supervisão, gestão ambiental e desapropriações ficam fora.')
comparables = [
    comp('BR-280/SC, duplicação São Francisco do Sul - Jaraguá do Sul (3 lotes)',
         [part(344301403.99, '201403', 36.00), part(151206675.59, '201306', 14.06), part(596092029.89, '201306', 23.84)],
         'Duplicação com restauração e melhoramentos para capacidade e segurança, km 0,70 a 74,58; mesma superintendência do DNIT e mesma época.',
         'SC, urbana e periurbana, com obras de arte', [{'url': CGOV.format(80981)}, {'url': CGOV.format(81007)}, {'url': CGOV.format(81065)}],
         'Preços iniciais vigentes: lote 1 (967/2014) R$ 344.301.403,99, mês-base mar/2014; lote 2.1 (574/2013) e lote 2.2 (614/2013), mês de assinatura (jun/2013).'),
    comp('BR-101/BA, duplicação Divisa SE/BA - Conceição do Jacuípe (lotes 1, 2 e 4)',
         [part(C.num_br(ug27[i]['valor_global']), '201409', km) for i, km in ((76890, 41.6), (76891, 41.98), (82000, 40.8))],
         'Contratação integrada (projeto e obra) de duplicação e restauração com obras de arte especiais; rodovia rural.',
         'BA, rural, com obras de arte', [{'url': CGOV.format(i)} for i in (76890, 76891, 82000)],
         'Valor dos contratos 748, 749 e 751/2014 (sem alteração de valor no registro). O lote 3 (750/2014) não está entre os contratos ativos da API e ficou fora.'),
    comp('BR-230/PB, duplicação e contorno Campina Grande - Farinha',
         [part(317837148.73, '201712', 31.6)],
         'Contratação integrada de duplicação, contorno, restauração e obras de arte especiais, km 152,3 a 183,9.',
         'PB, periurbana, com contorno e obras de arte', [{'url': CGOV.format(81013)}],
         'Preços iniciais vigentes depois do TA 11/2026; contrato 938/2017, assinado em 28/12/2017.'),
]
tcu_ref = q('Duplicação da BR-280/SC (São Francisco do Sul - Jaraguá do Sul) (03 lotes) 1.886.513.773,75 2.048.721.093,54 54% 1,09', t2205, 'TCU 2205/2024')
mi = lambda x: f"{x / 1e6:.1f}".replace('.', ',')
b280 = comparables[0]
cheaper = [c for c in comparables if c['cost_per_km_brl_2024'] < this['cost_per_km_brl_2024']]
cheaper_text = '; '.join(f"{c['name'].split(',')[0]}: R$ {mi(c['cost_per_km_brl_2024'])} mi/km" for c in cheaper)
comparison = {
    'unit': 'R$ por km de rodovia duplicada, em reais de dezembro de 2024',
    'method': 'Contratos a preços iniciais com aditivos de quantidade (sem reajustamento), corrigidos pelo IPCA do mês-base até dez/2024 (IBGE/SIDRA 1737). Mês-base = data-base oficial quando o documento a informa; senão, mês de assinatura. Tudo em reais: sem câmbio.',
    'ipca_dec_2024': IPCA['202412'], 'ipca_source': 'https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all?formato=json',
    'this_work': this, 'comparables': comparables,
    'cross_check_tcu': {'quote_br470': payments['tcu_execution_quote'], 'quote_br280': tcu_ref,
                        'reading': 'No quadro do TCU (mesma data-base para todos), a BR-280/SC também custa mais por km que a BR-470: R$ 2,049 bi para 73,9 km contra R$ 1,896 bi para 73,18 km.',
                        'url': TCU.format(n=2205, y=2024)},
    'result': (f"A BR-470 custou R$ {mi(this['cost_per_km_brl_2024'])} mi por km (dez/2024), MENOS que a obra mais parecida, a BR-280/SC "
               f"(R$ {mi(b280['cost_per_km_brl_2024'])} mi/km, mesma época e mesma superintendência), e mais que duplicações rurais ou com menos travessias urbanas "
               f"({cheaper_text})."),
    'caveats': ['Valores de contrato, não custo final: as quatro obras comparadas ainda têm contratos em andamento.',
                'O mês-base real dos preços pode ser anterior à assinatura; nesse caso a correção pelo IPCA fica um pouco subestimada em todos os casos.',
                'Os reequilíbrios pelo preço do asfalto (2021 a 2026) ficam fora da comparação: são parcela de reajuste, e corrigi-los pelo IPCA contaria a inflação duas vezes.',
                'Duplicações rurais em relevo plano (BR-101/BA) custam menos por km; a BR-470 atravessa áreas urbanas, com ruas laterais e muitos viadutos.'],
}

# ------------------------------------------------------------------ montagem
credits = json.load(open(os.path.join(ROOT, 'docs', 'superpowers', 'previews', 'assets', 'cases', 'br-470-duplicacao', 'credits.json')))
captions = {'road-indaial-2011.jpg': '2011: BR-470 em Indaial, ainda em pista simples',
            'urban-indaial-2011.jpg': '2011: trecho urbano da BR-470 em Indaial, antes da duplicação',
            'trucks-indaial-2011.jpg': '2011: caminhões parados na BR-470 em Indaial'}
media = [{'file': f"docs/superpowers/previews/assets/cases/br-470-duplicacao/{k}", 'caption': captions[k], 'author': v['author'],
          'license': v['license'], 'license_url': v['license_url'], 'page': v['commons'], 'date': v['date']} for k, v in credits.items()]

out = {
    'slug': 'br-470-duplicacao', 'collected_on': COLLECTED,
    'report': 'docs/research/BRASIL-IMPOSTO_RESEARCH_obras-sc-br-470-duplicacao_2026-09-30.md',
    'rules': 'Somente papéis e achados oficiais, com as palavras do órgão. Nenhuma inferência de irregularidade. Valores nominais salvo quando marcados como reais de dez/2024. Somas marcadas como computed são desta pesquisa.',
    'work': {
        'name': 'Duplicação da BR-470/SC entre Navegantes e Indaial (km 0,00 a 73,18)',
        'municipalities_ibge': [{'code': '4211306', 'name': 'Navegantes'}, {'code': '4207106', 'name': 'Ilhota'}, {'code': '4205902', 'name': 'Gaspar'},
                                {'code': '4202404', 'name': 'Blumenau', 'note': 'trecho entre Gaspar e Indaial; o nome não aparece nos documentos oficiais lidos'},
                                {'code': '4207502', 'name': 'Indaial'}],
        'level': 'federal', 'agency': {'name': 'DNIT, Superintendência Regional em Santa Catarina', 'uasg': '393013'},
        'status': 'Em execução nos quatro lotes. O TCU registrava 79% de execução financeira no quadro de 2024; contratos vigentes até 2026 e 2027.',
        'dates': {'start': '2013-07-30', 'start_note': 'Ordem de serviço do lote 3 (TCU, Acórdão 1886/2022) e início de vigência dos lotes 3 e 4 (DOU 26/07/2013)',
                  'planned_end': '2018-08-04', 'planned_end_note': 'Fim de vigência mais tardio nos extratos originais (lote 2); os lotes 3 e 4 terminavam em 06/10/2017 e o lote 1 em 22/04/2018',
                  'planned_end_current': max(c['end_current'] for c in works), 'actual_end': None,
                  'tcu_initial_vs_current_term_years': [4.9, 13.6]},
        'length_km': 73.18,
        'description': ('Obra do governo federal (DNIT) que transforma em pista dupla os primeiros 73 km da BR-470, de Navegantes, no litoral, até Indaial, '
                        'passando por Ilhota, Gaspar e Blumenau, no Vale do Itajaí. Além da segunda pista, inclui restaurar a pista antiga, ruas laterais '
                        'para o trânsito local e viadutos e pontes. Foi licitada em 2012 e 2013, em quatro lotes, e começou em julho de 2013 para durar '
                        'cerca de quatro anos; em 2026 os contratos ainda estão em andamento, com prazo até 2027.'),
        'siconfi_function': 'Transporte',
    },
    'contracts': contracts, 'contracts_totals_computed': totals,
    'payments': payments, 'companies': companies, 'people': people, 'people_gaps': people_gaps,
    'findings': findings,
    'terms_check': {'terms': ['superfaturamento', 'sobrepreço', 'desvio'], 'found': terms,
                    'note': 'O Acórdão 1886/2022 usa "sobrepreço" (R$ 510.205,50, 0,3% do contrato do lote 3, considerado de baixa materialidade). Nenhum dos dois acórdãos de auditoria usa "superfaturamento" ou "desvio". Controle positivo conferido.'},
    'media': media,
    'media_note': 'Não há no Wikimedia Commons foto com licença livre das obras de duplicação (buscas: "BR-470", "BR 470", "BR-470 duplicação", "BR-470 Gaspar/Blumenau/Navegantes/Indaial"). As fotos são de 2011, antes da obra, no fim do trecho (Indaial).',
    'comparison': comparison,
    'card': {'image': 'docs/superpowers/previews/assets/cases/br-470-duplicacao/urban-indaial-2011.jpg',
             'stats': [['Contratos de obra (preço inicial)', f"R$ {mi(totals['value_current_initial_prices_brl'])} mi"],
                       ['Pago (União e Estado)', f"R$ {payments['total_public_paid_brl_computed'] / 1e9:.2f} bi".replace('.', ',')],
                       ['Prazo', '13,6 anos (previsto 4,9)'],
                       ['Custo por km (dez/2024)', f"R$ {mi(this['cost_per_km_brl_2024'])} mi"]]},
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(C.no_dashes(out), open(OUT, 'w'), ensure_ascii=False, indent=1)
print('wrote', OUT)
print(comparison['result'])
print('fed', fed_total, 'state', state_total, 'totals', totals)
