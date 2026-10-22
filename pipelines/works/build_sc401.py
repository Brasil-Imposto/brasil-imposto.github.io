"""Builds data/works/sc-401-terceira-faixa.json from the inputs downloaded by roads_download.sh.

Usage: python3 build_sc401.py <workdir>
Every number comes from the official files in <workdir>; the literal quotes are checked
against the text of the document (common.require_quote), and the script stops if any of them does not match.
"""
import csv, json, os, sys, zipfile, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roads_common as C

W = sys.argv[1] if len(sys.argv) > 1 else '.'
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'data', 'works', 'sc-401-terceira-faixa.json')
COLLECTED = '2026-09-30'
C.self_test()
IPCA = C.load_ipca(W)
p = lambda *a: os.path.join(W, *a)

URL_CSV = 'https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/ff7c3cac-3e38-4801-9fd8-e4ccb69ca31d/download/contratos.csv'
API_SC = 'https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]='
PNCP_CT = 'https://pncp.gov.br/api/pncp/v1/orgaos/82951344000140/contratos/2025/2'
PNCP_UI = 'https://pncp.gov.br/app/contratos/82951344000140/2025/2'
PNCP_COMPRA = 'https://pncp.gov.br/api/consulta/v1/orgaos/82951344000140/compras/2024/194'
PNCP_COMPRA_UI = 'https://pncp.gov.br/app/editais/82951344000140/2024/194'
DOE_22468 = 'https://portal.doe.sea.sc.gov.br/repositorio/2025/20250311/Jornal/22468.pdf'
DOE_22483 = 'https://portal.doe.sea.sc.gov.br/repositorio/2025/20250401/Jornal/22483.pdf'
DOTC = 'https://consulta.tce.sc.gov.br/Diario/dotc-e{}.pdf'
ALESC_JM = 'https://memoriapolitica.alesc.sc.gov.br/biografia/514-Jorginho_Mello'
ALESC_CM = 'https://memoriapolitica.alesc.sc.gov.br/biografia/1308-Carlos_Moises'
TSE = 'https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{}.zip'
PORTAL_SC = 'https://www.transparencia.sc.gov.br/fornecedores'
PORTAL_PJ = 'https://portaldatransparencia.gov.br/pessoa-juridica/{}'

# ------------------------------------------------------------------ contract register (SIGEF/SICOP)
csv.field_size_limit(10**9)
rows = {r['NUCONTRATO']: r for r in csv.DictReader(open(p('contratos.csv'), encoding='utf-8', errors='ignore'), delimiter=';')
        if r['NUCONTRATO'] in ('CT-00014/2025', 'CT-00018/2021', 'CT-00315/2022') and r['CDUNIDADEGESTORA'] == '530001'}
if not (len(rows) == 3):
    raise SystemExit(rows.keys())
sicop = {t: json.load(open(p('sc401', f'sicop_{t}.json'))) for t in ('104411', '101659', '103057')}
main = rows['CT-00014/2025']
ex = sicop['104411']
if not (float(main['VLORIGINAL']) == 55983533.75 and ex['contrato']['contrato'] == 'CT-00014/2025'):
    raise SystemExit("check failed: float(main['VLORIGINAL']) == 55983533.75 and ex['contrato']['contrato'] == 'CT-00014/2025'")
aditivo_valor = float(ex['contrato']['valoraditado'])
reajuste = float(ex['contrato']['valorreajustado'])
if not (round(float(main['VLORIGINAL']) + aditivo_valor + reajuste, 2) == float(main['VLATUAL'])):
    raise SystemExit("check failed: round(float(main['VLORIGINAL']) + aditivo_valor + reajuste, 2) == float(main['VLATUAL'])")

pncp_ct = json.load(open(p('sc401', 'contrato.json')))
pncp_compra = json.load(open(p('sc401', 'compra.json')))
pncp_res = json.load(open(p('sc401', 'resultados.json')))[0]
if not (pncp_ct['niFornecedor'] == '84689066000392' and pncp_compra['valorTotalHomologado'] == 55983533.75):
    raise SystemExit("check failed: pncp_ct['niFornecedor'] == '84689066000392' and pncp_compra['valorTotalHomologado'] == 55983533.75")

# ------------------------------------------------------------------ official texts
doe_ct = C.pdf_text(p('doe', 'doe_20250311_22468.pdf'))
doe_port = C.pdf_text(p('doe', 'doe_20250401_22483.pdf'))
edital = C.pdf_text(p('sc401', 'arq1.pdf'))
etp = C.pdf_text(p('sc401', 'arq9.pdf'))
proj = C.pdf_text(p('sc401', 'arq3.pdf'))
dt = {d: C.pdf_text(p('dotc', f'dotc-e{d}.pdf')) for d in ('2025-04-25', '2025-05-02', '2026-04-06', '2026-04-24', '2026-05-05', '2026-08-27', '2026-09-08')}
q = C.require_quote

extrato = q('Local e data da assinatura: Florianópolis, 07/03/2025. Signatários: secretário Jerry Edson comper, pela siE e o sr. Jorge angelo coelho, pela contratada. Processo: siE 36159/2024.', doe_ct, 'DOE 22.468')
desconto_doe = q('Percentual de Desconto: 25% (vinte e cinco por cento)', doe_ct, 'DOE 22.468')
q('DESIGNAR, conforme o processo siE 10377/2025, o Gerente de Fiscalização de obras, LEANDRO DA COSTA VIEIRA', doe_port, 'DOE 22.483')
q('Jerry Edson Comper Secretário de Estado da Infraestrutura e Mobilidade', edital, 'edital CE 204/2024')
q('As Obras de Arte Especiais Inicialmente previstas em projetos serão licitadas posteriormente.', etp, 'ETP')
q('O projeto geométrico contemplou tres faixas de tráfego no dois sentidos', proj, 'relatório do projeto executivo')

# ------------------------------------------------------------------ contracts
def sicop_extract(t):
    e = sicop[t]
    return {
        'amendments': [{'number': a['numero'], 'date': a['data'][:10], 'justification': a['justificativa'],
                        'days_added': int(a['diasaditados']), 'amended_value_brl': float(a['valoraditado']),
                        'percent_in_record': float(a['percentual'])} for a in e['contratoAditivos']],
        'stoppages': [{'start': x['dataparalisacao'][:10], 'restart': (x['datareinicio'] or '')[:10] or None,
                       'days': int(x['diasparalisado']), 'note': x['observacao']} for x in e['contratoParalisacoes']],
    }

def contract_row(r, t, extra):
    e = sicop[t]['contrato']
    return dict({
        'number': r['NUCONTRATO'], 'object': ' '.join((r['OBJETO'] or '').split()),
        'company': r['CONTRATADO'], 'cnpj': r['IDCONTRATADO'],
        'signed_on': r['DTASSINATURA'][:10], 'start': r['DTINICIO'][:10],
        'end_original': r['DTFIM'][:10], 'end_current': r['DTFIMATUAL'][:10],
        'value_original_brl': float(r['VLORIGINAL']), 'value_current_brl': float(r['VLATUAL']),
        'value_amendments_brl': float(e['valoraditado']), 'value_price_adjustment_brl': float(e['valorreajustado']),
        'status_in_record': r['SITUACAO'], 'process_sgpe': f"SIE {r['NUPROCESSO']}",
        'managing_unit': {'code': r['CDUNIDADEGESTORA'], 'name': r['NMUNIDADEGESTORA']},
        'amendments': sicop_extract(t)['amendments'], 'stoppages': sicop_extract(t)['stoppages'],
        'inspector_field_raw': r['NMFISCAL'],
        'inspector_field_warning': 'Campo NMFISCAL do registro; o próprio SICOP classifica esses nomes como engenheiro fiscal, engenheiro da consultoria ou engenheiro da contratada (lista "contratoFiscais"). Não é lista de servidores.',
        'sources': [{'doc': 'Registro de contratos SIGEF/SICOP, CGE-SC (dados.sc.gov.br)', 'url': URL_CSV, 'collected_on': COLLECTED},
                    {'doc': 'Extrato SICOP do contrato, Portal da Transparência do Poder Executivo de SC (API)', 'url': API_SC + t, 'collected_on': COLLECTED}],
    }, **extra)

contracts = [
    contract_row(main, '104411', {
        'role_in_work': 'obra (execução)',
        'contractor_note': 'CNPJ de filial (0003-92, Palhoça/SC). Nome fantasia na Receita: MINERACAO SANTA BARBARA.',
        'tender': {'type': 'Concorrência eletrônica nº 204/2024 (Lei 14.133/2021, art. 28, II)',
                   'published_pncp': pncp_compra['dataPublicacaoPncp'][:10], 'proposals_closed': pncp_compra['dataEncerramentoProposta'][:10],
                   'estimated_value_brl': pncp_compra['valorTotalEstimado'], 'awarded_value_brl': pncp_compra['valorTotalHomologado'],
                   'discount_pct_pncp': pncp_res['percentualDesconto'], 'discount_in_doe_extract': desconto_doe,
                   'discount_note': 'O PNCP registra desconto de 5,9152% (o valor homologado é 5,92% menor que o orçamento estimado, cálculo). O extrato publicado no DOE-SC diz "25%". Os dois documentos oficiais divergem; o número que bate com os valores é o do PNCP.',
                   'estimated_budget_quote_etp': 'VALOR TOTAL DO ORÇAMENTO: R$ 59.503.283,51',
                   'scope_note': 'Contrato sem as obras de arte especiais (viadutos e retornos elevados), que o Estudo Técnico Preliminar diz que "serão licitadas posteriormente".',
                   'url': PNCP_COMPRA_UI, 'api': PNCP_COMPRA},
        'measured_to_date': {'measurements': len(ex['contratoMedicoes']), 'last_period_end': ex['contratoMedicoes'][-1]['periodomedicaotermino'][:10],
                             'accumulated_initial_prices_brl': round(sum(float(m['valormedicaopi']) for m in ex['contratoMedicoes']), 2),
                             'accumulated_price_adjustment_brl': round(sum(float(m['valormdeicaoreajuste']) for m in ex['contratoMedicoes']), 2),
                             'accumulated_total_brl': float(ex['contratoMedicoes'][-1]['vlacumuladototal'])},
        'signatories_doe': extrato,
        'extra_sources': [{'doc': 'Extrato de contrato no DOE-SC nº 22.468, 11/03/2025, p. 74', 'url': DOE_22468},
                          {'doc': 'Contrato no PNCP (82951344000140-2-000002/2025)', 'url': PNCP_UI, 'api': PNCP_CT}],
    }),
    contract_row(rows['CT-00018/2021'], '101659', {
        'role_in_work': 'projeto de engenharia do mesmo trecho (km 12+695 a 19+285, 10,07 km)',
        'contractor_note': 'O relatório do projeto executivo publicado no PNCP (anexo IV do edital) é desta empresa.'}),
    contract_row(rows['CT-00315/2022'], '103057', {
        'role_in_work': 'supervisão (ligação indicada pelo SICOP)',
        'link_note': 'O objeto fala em "restauração" da SC-401 e SC-404 (3 trechos). A ligação com a terceira faixa vem do SICOP: os três "engenheiros da consultoria" listados no CT-00014/2025 são os "engenheiros da contratada" deste contrato, e o mesmo fiscal foi designado para os dois a partir de 17/03/2025 (Portarias 324 e 325/2025, DOE-SC nº 22.483).'}),
]

# ------------------------------------------------------------------ payments
def resumo(t):
    return [{'year': int(r['ano']), 'committed_brl': float(r['vlempenhado']), 'liquidated_brl': float(r['vlliquidado']), 'paid_brl': float(r['vlpago'])}
            for r in sicop[t]['contratoResumoFinanceiro']]
paid_main = resumo('104411')
payments = {
    'source': {'doc': 'Extrato SICOP do contrato ("contratoResumoFinanceiro" e "contratoPagamento"), Portal da Transparência do Poder Executivo de SC', 'url': API_SC + '104411', 'collected_on': COLLECTED},
    'by_contract': {'CT-00014/2025': paid_main, 'CT-00018/2021': resumo('101659'), 'CT-00315/2022': resumo('103057')},
    'total_paid_ct_00014_2025_brl_computed': round(sum(r['paid_brl'] for r in paid_main), 2),
    'checks': ['Em cada ano, a soma das linhas de pagamento do extrato (despesa paga + retenções de INSS, IRRF e ISS - estornos) é igual ao "vlpago" do resumo, ao centavo.',
               'Pagamento por contrato, não por credor: a consulta por credor (Britagem Vogelsanger, filial 0003) mistura outros contratos da mesma empresa com o Estado (ex.: CT-00225/2022, SC-108, R$ 168 mi).'],
    'coverage': 'Até a carga do Portal em 2026-09-30; 2026 é parcial.',
}

# ------------------------------------------------------------------ companies
def receita(cnpj):
    for f in (p('rf', f'{cnpj}.json'), p('rf', f'ba_{cnpj}.json')):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d.get('razao_social'):
            return d, ('https://minhareceita.org/' if 'ba_' not in f else 'https://brasilapi.com.br/api/cnpj/v1/') + cnpj
    return None, None

companies = []
for cnpj, contracts_of in (('84689066000392', ['CT-00014/2025']), ('03616409000125', ['CT-00018/2021']), ('83256172000158', ['CT-00315/2022'])):
    d, url = receita(cnpj)
    companies.append({
        'cnpj': cnpj, 'legal_name': d and d['razao_social'], 'trade_name': d and (d.get('nome_fantasia') or None),
        'head_or_branch': d and d.get('descricao_identificador_matriz_filial'), 'city': d and f"{d.get('municipio')}/{d.get('uf')}",
        'registration_status': d and d.get('descricao_situacao_cadastral'), 'registration_status_date': d and d.get('data_situacao_cadastral'),
        'legal_nature': d and d.get('natureza_juridica'), 'contracts': contracts_of,
        'official_website': None, 'official_website_note': 'Não verificado nesta coleta; deixado vazio pela regra do projeto (só com correspondência sem ambiguidade).',
        'transparency_links': [PORTAL_PJ.format(cnpj), PORTAL_SC],
        'source': {'doc': 'Base aberta do CNPJ da Receita Federal, lida via espelho (servidor oficial inacessível do exterior)', 'url': url, 'collected_on': COLLECTED} if d else
                  {'doc': 'Cadastro não lido: espelhos da Receita indisponíveis (HTTP 503) em 2026-09-30', 'url': None},
    })

# ------------------------------------------------------------------ people
def tse_party(year, name, office):
    z = zipfile.ZipFile(p('tse', f'consulta_cand_{year}.zip'))
    r = csv.reader(io.TextIOWrapper(z.open(f'consulta_cand_{year}_SC.csv'), encoding='latin1'), delimiter=';')
    h = next(r); ix = {c: i for i, c in enumerate(h)}
    for row in r:
        if name in row[ix['NM_CANDIDATO']] and row[ix['DS_CARGO']] == office:
            return row[ix['SG_PARTIDO']], row[ix['NM_PARTIDO']]
    raise KeyError(name)

jm_party = tse_party(2022, 'JORGINHO DOS SANTOS MELLO', 'GOVERNADOR')
cm_party_2022 = tse_party(2022, 'CARLOS MOIS', 'GOVERNADOR')
bio_jm = C.clean_html(open(p('alesc', 'bio_514_jorginho_mello.html'), encoding='utf-8', errors='ignore').read())
bio_cm = C.clean_html(open(p('alesc', 'bio_1308_carlos_moises.html'), encoding='utf-8', errors='ignore').read())
q('A chapa vencedora é composta por dois representates do mesmo partido, o PL, Jorginho Mello, o Governador', bio_jm, 'Alesc JM')
q('No ano de 2018, filiou-se ao Partido Social Liberal (PSL)', bio_cm, 'Alesc CM')
q('a partir de março do ano que concorrerá à reeleição, passou para a sigla Republicanos', bio_cm, 'Alesc CM')
q('Daniela deixou a interinidade no comando do Executivo e Carlos Moisés reassumiu as funções', bio_cm, 'Alesc CM')

t0426 = dt['2026-04-24']
q('DETERMINAR, CAUTELARMENTE, ao Sr. Ricardo Euclides Grando, Secretário de Estado da Infraestrutura e Mobilidade', t0426, 'DOTC 24/04/2026')
q('Luiz Ernesto Pantoja Telles de Menezes, Diretor de Fiscalização de Obras de Infraestrutura', t0426, 'DOTC 24/04/2026')

people = [
    {'name': 'Jerry Edson Comper', 'role': 'Secretário de Estado da Infraestrutura e Mobilidade (SIE)',
     'signed': ['CT-00014/2025 (07/03/2025)', 'Edital da Concorrência 204/2024 (08/11/2024)'],
     'source': [{'doc': 'Extrato do contrato, DOE-SC nº 22.468, 11/03/2025, p. 74', 'url': DOE_22468},
                {'doc': 'Edital CE 204/2024 no PNCP (assinatura na p. 37)', 'url': PNCP_COMPRA_UI}]},
    {'name': 'Adalberto Cervino Ventura', 'role': 'Diretor de Administração e Finanças da SIE',
     'signed': ['Portaria 325/2025 (designação do fiscal do CT-014/2025)', 'Portaria 312/2025 (comissão de desapropriação do CT-014/2025)'],
     'source': [{'doc': 'DOE-SC nº 22.483, 01/04/2025, p. 5', 'url': DOE_22483},
                {'doc': 'DOE-SC nº 22.480, 27/03/2025, p. 7', 'url': 'https://portal.doe.sea.sc.gov.br/repositorio/2025/20250327/Jornal/22480.pdf'}]},
    {'name': 'Leandro da Costa Vieira', 'role': 'Gerente de Fiscalização de Obras da SIE; fiscal do contrato a partir de 17/03/2025',
     'signed': [], 'source': [{'doc': 'Portaria 325/2025, DOE-SC nº 22.483, p. 5', 'url': DOE_22483}]},
    {'name': 'Ricardo Euclides Grando', 'role': 'Secretário de Estado da Infraestrutura e Mobilidade na data das decisões do TCE-SC de 2026 (destinatário da cautelar)',
     'signed': [], 'note': 'Assinatura dos aditivos de 2026 não verificada nesta coleta.',
     'source': [{'doc': 'Decisão Singular GAC/WWD 190/2026, DOTC-e nº 4301, 24/04/2026', 'url': DOTC.format('2026-04-24')}]},
    {'name': 'Luiz Ernesto Pantoja Telles de Menezes', 'role': 'Diretor de Fiscalização de Obras de Infraestrutura da SIE (destinatário de diligência do TCE-SC)',
     'signed': [], 'source': [{'doc': 'Decisão Singular GAC/WWD 190/2026 e 451/2026', 'url': DOTC.format('2026-08-27')}]},
    {'name': 'Jorginho Mello', 'full_name': 'Jorginho dos Santos Mello', 'role': 'Governador', 'head_of_government': True,
     'on_dates': ['2024-11-08 (edital)', '2025-03-07 (CT-00014/2025)', '2026-03-31 (1º aditivo)', '2026-08-21 (aditivo de prazo)'],
     'party_at_time': jm_party[0], 'party_name': jm_party[1].title(),
     'term': {'start': '2023-01-01', 'start_note': 'Data de posse fixada pela Constituição; a biografia da Alesc registra o mandato como "01/02/2023 - 31/01/2027".', 'end': None},
     'note': 'O governador não assina o contrato: no extrato, assina o secretário da SIE.',
     'source': [{'doc': 'Biografia, Memória Política de SC (Alesc)', 'url': ALESC_JM},
                {'doc': 'TSE, candidaturas 2022 (SC), partido na eleição', 'url': TSE.format(2022)}]},
    {'name': 'Carlos Moisés da Silva', 'role': 'Governador', 'head_of_government': True,
     'on_dates': ['2021-03-09 (CT-00018/2021, projeto)', '2022-11-21 (CT-00315/2022, supervisão)'],
     'party_at_time': {'2021-03-09': 'PSL', '2022-11-21': cm_party_2022[0]},
     'party_note': 'Filiou-se ao PSL em 2018; passou ao Republicanos em março de 2022 (biografia da Alesc). Em 2021-03-09 estava no exercício do cargo (afastamentos: 26/10 a 27/11/2020 e 30/03 a 07/05/2021).',
     'source': [{'doc': 'Biografia, Memória Política de SC (Alesc)', 'url': ALESC_CM},
                {'doc': 'TSE, candidaturas 2022 (SC)', 'url': TSE.format(2022)}]},
]

# ------------------------------------------------------------------ official findings
f1 = q('a demanda surgiu em decorrência da ausência de atenção ao Plano de Mobilidade Urbana Sustentável da Grande Florianópolis (PLAMUS) e da falta de interlocução entre a Secretaria de Estado da Infraestrutura e Mobilidade (SIE) e a Prefeitura de Florianópolis', dt['2025-04-25'], 'GAC/AMF 216/2025')
f1b = q('onde se lê “para a realização de Acompanhamento (ACO)”, leia-se “para a realização de Auditoria (RLA)”', dt['2025-05-02'], 'despacho 2025-05-02')
f2 = q('que se abstenha da liberação de novos trechos da terceira faixa da rodovia SC-401, sem a necessária e cogente segurança viária', t0426, 'GAC/WWD 190/2026')
f2b = q('a liberação precoce de alguns trechos da rodovia SC 401, com serviços inacabados, redução das seções das faixas, ausência de dispositivos de proteção e segurança, mudanças abruptas de faixa e presença de obstáculos fixos próximos a faixa de rolamento', t0426, 'GAC/WWD 190/2026')
f2c = q('21.857m³ de material de terceira, que equivaleria a R$ 4.719.144,87, no trecho entre as estacas 26+0 até 52+0', t0426, 'GAC/WWD 190/2026')
f2r = q('ACO 25/80006863 pelo(a) Conselheiro Wilson Rogério Wan-Dall em 22/04/2026, Decisão Singular GAC/WWD - 190/2026', dt['2026-05-05'], 'ratificação')
t0827 = dt['2026-08-27']
f3 = q('entendo que não restou comprovado o saneamento das inconformidades que embasaram a medida cautelar', t0827, 'GAC/WWD 451/2026')
f3b = q('considerando o término previsto para 08/09/2026, percentual físico-financeiro executado de 61,86%, enquanto o percentual projetado para o período era 91,75%', t0827, 'GAC/WWD 451/2026')
f3c = q('ao acidente ocorrido em 31/03/2026, no qual um veículo saiu da pista e caiu sobre uma residência situada em cota inferior à do pavimento', t0827, 'GAC/WWD 451/2026')
f3d = q('os achados não apontam, neste momento, para uma deficiência de espessura capaz de indicar prejuízo quantitativo à administração pública', t0827, 'GAC/WWD 451/2026')
f3r = q('ACO 25/80006863 pelo(a) Conselheiro Wilson Rogério Wan-Dall em 24/08/2026, Decisão Singular GAC/WWD - 451/2026', dt['2026-09-08'], 'ratificação')
f4 = q('Determinar o arquivamento dos autos por perda de objeto, haja vista a inclusão do mesmo tema no Processo n. RLA 25/80004143', dt['2026-04-06'], 'Decisão 424/2026')

import re as _re
term_check = {}
for d, span in (('2025-04-25', (f1[:40], 'PROCESSO Nº: @PPA')), ('2026-04-24', ('PROCESSO Nº: ACO 25/80006863', 'Autarquias')), ('2026-08-27', ('PROCESSO Nº: ACO 25/80006863', 'Autarquias'))):
    t = dt[d]
    i = t.find(span[0]) if span[0] in t else 0
    j = t.find(span[1], i + 10)
    seg = t[i:j if j > 0 else None]
    term_check[d] = sorted(set(m.lower() for m in _re.findall(r'(?i)superfatur\w*|sobrepre\w*|desvio\w*', seg)))
if not (_re.findall(r'(?i)superfatur\w*|sobrepre\w*', 'houve sobrepreço e superfaturamento')):
    raise SystemExit("check failed: _re.findall('(?i)superfatur\\\\w*|sobrepre\\\\w*', 'houve sobrepreço e superfaturamento')") # control

findings = [
    {'body': 'TCE-SC', 'process': '@PAF 25/80004143, convertido em auditoria RLA 25/80004143', 'decision': 'Decisão Singular GAC/AMF 216/2025 (relator Adircélio de Moraes Ferreira Júnior)',
     'date': '2025-04-25 (publicação); retificação em 2025-05-02', 'summary_quote': f1, 'correction_quote': f1b,
     'status': 'auditoria autorizada sobre as obras de aumento de capacidade da SC-401 Norte; decisão de mérito não localizada até 2026-09-30',
     'url': DOTC.format('2025-04-25'), 'extra_urls': [DOTC.format('2025-05-02')]},
    {'body': 'TCE-SC', 'process': 'REP 25/00183305', 'decision': 'Decisão 424/2026, Tribunal Pleno (sessão virtual de 20/03/2026)',
     'date': '2026-03-20 (sessão); 2026-04-06 (publicação)',
     'summary_quote': f4, 'context': 'Representação do deputado estadual Marcos José de Abreu (Marquito), a partir da Indicação 1133/2025, sobre drenagem e outros aspectos da terceira pista (texto da decisão).',
     'status': 'arquivada por perda de objeto; o tema segue na auditoria RLA 25/80004143', 'url': DOTC.format('2026-04-06')},
    {'body': 'TCE-SC', 'process': 'ACO 25/80006863 (acompanhamento do Contrato 14/2025)', 'decision': 'Decisão Singular GAC/WWD 190/2026 (relator Wilson Rogério Wan-Dall), medida cautelar',
     'date': '2026-04-22 (decisão); 2026-04-24 (publicação)', 'summary_quote': f2, 'technical_quote': f2b, 'quantities_quote': f2c,
     'addressee_as_in_text': 'Secretário de Estado da Infraestrutura e Mobilidade (Ricardo Euclides Grando), com diligências ao Diretor de Fiscalização de Obras e ao fiscal do contrato',
     'ratification_quote': f2r,
     'status': 'cautelar ratificada pela Primeira Câmara (sessão virtual iniciada em 24/04/2026); é determinação preventiva, não julgamento de mérito nem sanção',
     'url': DOTC.format('2026-04-24'), 'extra_urls': [DOTC.format('2026-05-05')]},
    {'body': 'TCE-SC', 'process': 'ACO 25/80006863', 'decision': 'Decisão Singular GAC/WWD 451/2026 (relator Wilson Rogério Wan-Dall)',
     'date': '2026-08-24 (decisão); 2026-08-27 (publicação)', 'summary_quote': f3, 'schedule_quote': f3b, 'accident_quote': f3c, 'pavement_quote': f3d,
     'ratification_quote': f3r,
     'status': 'cautelar mantida e ratificada (Primeira Câmara, sessão virtual iniciada em 28/08/2026); diligências com prazo de 20 dias; processo em andamento',
     'url': DOTC.format('2026-08-27'), 'extra_urls': [DOTC.format('2026-09-08')]},
    {'body': 'MPSC, MPF, Justiça', 'process': None, 'summary_quote': None,
     'status': 'Nenhum procedimento localizado nesta coleta (uma busca na web; os sistemas do MPSC e do TJSC não foram consultados por número).', 'url': None},
]

# ------------------------------------------------------------------ comparison (cost per km, in reais of Dec 2024)
def comp(name, value, ym, km, scope, lanes, source, value_basis, category, alt_km=None):
    f = C.ipca_factor(IPCA, ym)
    d = {'name': name, 'category': category, 'scope': scope, 'lanes': lanes, 'length_km': km,
         'cost_reported_brl': value, 'cost_basis': value_basis, 'price_base_month': f'{ym[:4]}-{ym[4:]}',
         'ipca_index_base_month': IPCA[ym], 'ipca_factor_to_dec2024': round(f, 6),
         'cost_brl_2024': round(value * f, 2), 'cost_per_km_brl_2024': round(value * f / km, 2), 'sources': source}
    if alt_km:
        d['cost_per_km_brl_2024_alt'] = {'length_km': alt_km, 'value': round(value * f / alt_km, 2),
                                         'note': 'Só o eixo principal (km 12+695 a 19+285); os 10,07 km somam as vias marginais.'}
    return d

sc401_value = round(float(main['VLORIGINAL']) + aditivo_valor, 2)
cgov = lambda i: f'https://contratos.comprasnet.gov.br/api/contrato/{i}/historico'
mg = json.load(open(p('comp', 'mg230.json')))
_h = lambda i: ' '.join((x.get('observacao') or '') for x in json.load(open(p('comp', f'h_{i}.json'))))
q('PASSA PARA R$ 50.708.357,79', _h(99884), 'Petrolina')
_ug = lambda ug: {c['id']: c for c in json.load(open(p('comp', f'cgov_{ug}.json')))}
if not (C.num_br(_ug('393013')[352579]['valor_global']) == 28572115.68 and _ug('393013')[352579]['data_assinatura'] == '2024-12-02'):
    raise SystemExit("check failed: C.num_br(_ug('393013')[352579]['valor_global']) == 28572115.68 and _ug('393013')[352579]['data_assinatura'] == '2024-12-02'")
if not (C.num_br(_ug('393027')[568641]['valor_global']) == 179422844.66 and _ug('393027')[568641]['data_assinatura'] == '2025-06-05'):
    raise SystemExit("check failed: C.num_br(_ug('393027')[568641]['valor_global']) == 179422844.66 and _ug('393027')[568641]['data_assinatura'] == '2025-06-05'")
if not (_ug('393029')[99884]['data_assinatura'] == '2020-12-30'):
    raise SystemExit("check failed: _ug('393029')[99884]['data_assinatura'] == '2020-12-30'")
if not (mg['valorGlobal'] == 34487308.95):
    raise SystemExit("check failed: mg['valorGlobal'] == 34487308.95")
comparison = {
    'unit': 'R$ por km de extensão contratada, em reais de dezembro de 2024',
    'method': 'Valor do contrato a preços iniciais (sem reajuste) com aditivos de valor, corrigido pelo IPCA do mês de assinatura até dez/2024 (IBGE/SIDRA 1737). Todos os valores já estão em reais: não há conversão de câmbio. Fator = IPCA dez/2024 / IPCA do mês-base.',
    'ipca_dec_2024': IPCA['202412'], 'ipca_source': 'https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all?formato=json',
    'this_work': comp('SC-401, terceira faixa (Florianópolis/SC)', sc401_value, '202503', 10.07,
                      'Terceira faixa nos dois sentidos, vias marginais, ciclofaixa, drenagem e contenções, em área urbana; SEM viadutos e retornos elevados (licitados à parte).',
                      '2+2 para 3+3 faixas', [{'url': API_SC + '104411'}, {'url': PNCP_UI}],
                      'Valor original R$ 55.983.533,75 + aditivo de R$ 6.732.194,70 (preços iniciais). O valor atual no SIGEF, R$ 64.185.445,29, inclui ainda R$ 1.469.716,84 de reajuste.',
                      'urbana, sem obras de arte especiais', alt_km=6.59),
    'comparables': [
        comp('BR-428/PE, duplicação da travessia urbana de Petrolina (DNIT)', 50708357.79, '202012', 7.11,
             'Duplicação para adequação de capacidade em travessia urbana, km 180,89 a 188,00.', '2 para 4 faixas',
             [{'url': cgov(99884)}], 'Valor a preços iniciais vigente depois do 8º termo aditivo (R$ 50.708.357,79); contrato 921/2020, assinado em 30/12/2020.',
             'urbana, sem obras de arte especiais no objeto'),
        comp('BR-282/SC, ruas laterais e ponto crítico na travessia urbana de Maravilha (DNIT)', 28572115.68, '202412', 3.4,
             'Correção de ponto crítico e implantação e pavimentação de ruas laterais, km 604,3 a 607,7.', 'pista existente + ruas laterais',
             [{'url': cgov(352579)}], 'Valor do contrato 674/2024 (sem aditivo de valor até 2026-06).', 'urbana, sem obras de arte especiais no objeto'),
        comp('BR-324/BA, travessia urbana de Feira de Santana (DNIT)', 179422844.66, '202506', 7.2,
             'Implantação/duplicação, adequação de capacidade e eliminação de segmentos críticos, INCLUINDO obras de arte especiais, km 512,5 a 519,7.', '2 para 4 faixas + obras de arte',
             [{'url': cgov(568641)}], 'Valor do contrato 287/2025 (sem aditivo de valor até 2026-06).', 'urbana, com obras de arte especiais'),
        comp('MG-230, restauração e terceira faixa, Serra do Salitre a Salitre de Minas (DER-MG)', mg['valorGlobal'], '202608', 15.04,
             'Restauração e aumento de capacidade com terceira faixa, rodovia rural.', '2 para 3 faixas (terceira faixa)',
             [{'url': 'https://pncp.gov.br/app/contratos/17309790000194/2026/293'}], 'Valor do contrato no PNCP, assinado em 11/08/2026.', 'rural'),
    ],
}
urban = [c for c in comparison['comparables'] if c['category'].startswith('urbana, sem')]
me = comparison['this_work']
mi = lambda x: f"{x / 1e6:.1f}".replace('.', ',')
urban_txt = ' e '.join(f"R$ {mi(c['cost_per_km_brl_2024'])}" for c in urban)
comparison['result'] = (f"Por km de extensão contratada, a SC-401 custou R$ {mi(me['cost_per_km_brl_2024'])} mi/km (dez/2024), MENOS que as duas "
                        f"obras urbanas comparáveis sem obras de arte ({urban_txt} mi/km). Contando só o eixo principal (6,59 km), fica em "
                        f"R$ {mi(me['cost_per_km_brl_2024_alt']['value'])} mi/km, no mesmo patamar delas.")
comparison['caveats'] = [
    'O contrato da SC-401 não inclui os viadutos e retornos elevados; quando forem contratados, o custo da obra completa sobe.',
    'O TCE-SC registra que os quantitativos de escavação, terraplenagem e pavimentação estão se esgotando antes do fim da obra e pede a atualização dos quantitativos e do impacto financeiro: o valor final deve ser maior que o atual.',
    'Os comparáveis são contratos (valor contratado), não custo final auditado; três ainda estão em execução.',
    'Extensões diferentes medem coisas diferentes: os 10,07 km da SC-401 somam eixo e vias marginais.',
]

# ------------------------------------------------------------------ assembly
credits = json.load(open(os.path.join(ROOT, 'docs', 'superpowers', 'previews', 'assets', 'cases', 'sc-401-terceira-faixa', 'credits.json')))
captions = {'centro-administrativo-2014.jpg': '2014: Centro Administrativo do Governo de SC, na SC-401 (km 15, Saco Grande), dentro do trecho da obra',
            'saco-grande-2023.jpg': '2023: bairro Saco Grande, cortado pela SC-401, visto do Floripa Shopping',
            'sc-401-margin-2015.jpg': '2015: agência bancária às margens da SC-401, no complexo do Centro Administrativo'}
media = [{'file': f"docs/superpowers/previews/assets/cases/sc-401-terceira-faixa/{k}", 'caption': captions[k], 'author': v['author'],
          'license': v['license'], 'license_url': v['license_url'], 'page': v['commons'], 'date': v['date']} for k, v in credits.items()]

paid_total = payments['total_paid_ct_00014_2025_brl_computed']
out = {
    'slug': 'sc-401-terceira-faixa', 'collected_on': COLLECTED,
    'report': 'docs/research/BRASIL-IMPOSTO_RESEARCH_obras-sc-sc-401-terceira-faixa_2026-09-30.md',
    'rules': 'Somente papéis e achados oficiais, com as palavras do órgão. Nenhuma inferência de irregularidade. Valores nominais salvo quando marcados como reais de dez/2024. Somas marcadas como computed são desta pesquisa.',
    'work': {
        'name': 'Terceira faixa da SC-401 (melhoramento com aumento de capacidade entre o acesso a Santo Antônio de Lisboa e a SC-404)',
        'municipalities_ibge': [{'code': '4205407', 'name': 'Florianópolis'}], 'level': 'state',
        'agency': {'name': 'Secretaria de Estado da Infraestrutura e Mobilidade (SIE)', 'cnpj': '82951344000140', 'managing_unit': '530001'},
        'status': 'Em execução. Prazo prorrogado para 19/02/2027. Liberação de novos trechos da terceira faixa suspensa por cautelar do TCE-SC desde 22/04/2026.',
        'dates': {'start': ex['contrato']['datainicio'][:10], 'start_note': 'Ordem de serviço OS OBR 008/2025', 'planned_end': ex['contrato']['datatermino'][:10],
                  'planned_end_current': ex['contrato']['dataterminoatual'][:10], 'actual_end': None,
                  'first_partial_release': '2025-12-18', 'first_partial_release_source': DOTC.format('2026-04-24')},
        'length_km': 10.07, 'main_axis_km': {'from': '12+695', 'to': '19+285', 'length': 6.59},
        'description': ('Obra do Governo do Estado na rodovia mais movimentada de Santa Catarina, no norte da Ilha de Santa Catarina. '
                        'Acrescenta uma terceira faixa em cada sentido entre o km 12,7 e o km 19,3, com vias marginais para o trânsito local, '
                        'ciclofaixa, drenagem e contenções, em 10,07 km no total. Os viadutos e retornos elevados previstos no projeto ficaram '
                        'para outra licitação. Começou em março de 2025 para durar 18 meses; o prazo foi estendido para fevereiro de 2027.'),
        'traffic_quote': q('a rodovia, no seu trecho norte, registra tráfego médio diário de 60.592 veículos, sendo que em janeiro de 2025, essa média se elevou para 98.965 veículos', t0426, 'GAC/WWD 190/2026'),
        'siconfi_function': 'Transporte',
        'budget_source': 'Empenhos na unidade orçamentária 53001 (SIE), subação 14465, fonte 1500100000 (recursos do Tesouro do Estado), segundo o extrato SICOP.',
    },
    'contracts': contracts,
    'contracts_totals_computed': {'ct_00014_2025_initial_prices_with_amendment_brl': sc401_value,
                                  'all_three_current_brl': round(sum(c['value_current_brl'] for c in contracts), 2)},
    'payments': payments, 'companies': companies, 'people': people,
    'people_note': 'Só papéis, com fonte. A presença de um nome numa decisão do TCE-SC como destinatário de cautelar ou diligência não é acusação nem sanção.',
    'findings': findings,
    'terms_check': {'terms': ['superfaturamento', 'sobrepreço', 'desvio'], 'found_in_sc401_decisions': term_check,
                    'note': 'Busca feita só no trecho de cada DOTC-e que trata da SC-401 (as mesmas edições trazem esses termos em outros processos). Controle positivo conferido.'},
    'media': media,
    'media_note': 'Não há no Wikimedia Commons foto com licença livre da obra da terceira faixa (buscas: "SC-401", "Rodovia SC-401", "Cacupé", "Saco Grande", geobusca num raio de 2,5 km do trecho). As fotos mostram o entorno do trecho.',
    'comparison': comparison,
    'card': {'image': 'docs/superpowers/previews/assets/cases/sc-401-terceira-faixa/centro-administrativo-2014.jpg',
             'stats': [['Valor atual do contrato', 'R$ 64,2 mi'], ['Aditivo de valor', '+12%'],
                       ['Pago até set/2026', f'R$ {paid_total/1e6:.1f} mi'.replace('.', ',')],
                       ['Custo por km (dez/2024)', f"R$ {me['cost_per_km_brl_2024']/1e6:.1f} mi".replace('.', ',')]]},
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(C.no_dashes(out), open(OUT, 'w'), ensure_ascii=False, indent=1)
print('wrote', OUT)
print(json.dumps({k: (v['cost_per_km_brl_2024'], v['cost_brl_2024']) for k, v in [('sc401', me)] + [(c['name'][:30], c) for c in comparison['comparables']]}, ensure_ascii=False, indent=0))
print(comparison['result'])
