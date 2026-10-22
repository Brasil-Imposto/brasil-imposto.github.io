"""Build data/bridge-comparables.json: cost per m2 of deck, in BRL of Dec 2024, for the
Ponte Hercilio Luz restoration and comparable bridges, by two conversion methods.

Run inside the working directory where download.sh saved its files:
    bash ~/Documents/Brasil-Imposto/pipelines/bridges/download.sh
    python3 ~/Documents/Brasil-Imposto/pipelines/bridges/build.py

Method (i)  FX:  amount_LCU * (BRL per USD / LCU per USD)[year] * IPCA[Dec 2024] / IPCA[year average]
Method (ii) PPP: amount_LCU * (BRL per intl $ / LCU per intl $)[year] * IPCA[Dec 2024] / IPCA[year average]
For amounts already in BRL both methods reduce to the IPCA correction.
"""
import csv, json, os, sys, unicodedata
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'data', 'bridge-comparables.json'))
COLLECTED = '2026-09-29'
TARGET = '202412'

URL_IPCA = 'https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all?formato=json'
URL_WB = 'https://api.worldbank.org/v2/country/BRA;HUN;CAN;VNM/indicator/{ind}?format=json&per_page=1000&date=1995:2025'
URL_CONTRACTS = 'https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/ff7c3cac-3e38-4801-9fd8-e4ccb69ca31d/download/contratos.csv'

# ---------------------------------------------------------------- factors
ipca_rows = json.load(open('ipca.json'))[1:]
IPCA = {r['D3C']: float(r['V']) for r in ipca_rows}

def ipca_year_avg(y):
    vals = [IPCA[f'{y}{m:02d}'] for m in range(1, 13)]
    return sum(vals) / 12

def wb(ind):
    d = json.load(open(f'wb_{ind}.json'))
    out = {}
    for r in d[1]:
        if r['value'] is not None:
            out.setdefault(r['countryiso3code'], {})[int(r['date'])] = float(r['value'])
    return out, d[0].get('lastupdated')

FX, FX_UPDATED = wb('PA.NUS.FCRF')
PPP, PPP_UPDATED = wb('PA.NUS.PPP')

def to_brl_2024(amount, iso3, year):
    """Return (fx_value, ppp_value, factors) for an amount in local currency spent in `year`."""
    ipf = IPCA[TARGET] / ipca_year_avg(year)
    if iso3 == 'BRA':
        fx_rate = ppp_rate = 1.0
    else:
        fx_rate = FX['BRA'][year] / FX[iso3][year]
        ppp_rate = PPP['BRA'][year] / PPP[iso3][year]
    f = {'year': year, 'ipca_year_avg': round(ipca_year_avg(year), 4), 'ipca_factor_to_dec2024': round(ipf, 6)}
    if iso3 != 'BRA':
        f.update({'fx_lcu_per_usd': FX[iso3][year], 'fx_brl_per_usd': FX['BRA'][year],
                  'ppp_lcu_per_intl_usd': PPP[iso3][year], 'ppp_brl_per_intl_usd': PPP['BRA'][year]})
    return amount * fx_rate * ipf, amount * ppp_rate * ipf, f

# ---------------------------------------------------------------- Hercilio Luz contracts
RESTORATION = ['PJ-00170/2006', 'PJ-00170/2006/PROSUL', 'PJ-00264/2008', 'PJ-00204/2014', 'PJ-00012/2015',
               'PJ-00143/2015', 'PJ-00001/2016/FARES', 'PJ-00056/2016', 'PJ-00093/2016', 'PJ-00009/2019',
               'CT-00006/2019', 'PJ-00060/2019', 'CT-00026/2019']

def norm(s):
    return unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().upper()

csv.field_size_limit(10**9)
matched = []
for r in csv.DictReader(open('contratos.csv', encoding='utf-8', errors='ignore'), delimiter=';'):
    txt = norm(' '.join(r.get(k) or '' for k in ('OBJETO', 'RESUMO', 'NMBEMPUBLICO', 'BEMPUBLICO')))
    if 'PONTE' in txt and 'HERCILIO' in txt:
        matched.append(r)
assert len(matched) == 26, len(matched)
hl = sorted([r for r in matched if r['NUCONTRATO'] in RESTORATION], key=lambda r: r['DTASSINATURA'])
assert len(hl) == 13, len(hl)
assert sum(Decimal(r['VLATUAL']) for r in hl) == Decimal('484645236.82')
assert sum(Decimal(r['VLORIGINAL']) for r in hl) == Decimal('465106951.83')

contracts = []
tot_cur = tot_low = 0.0
for r in hl:
    ym = r['DTASSINATURA'][:4] + r['DTASSINATURA'][5:7]
    fac = IPCA[TARGET] / IPCA[ym]
    cur, orig = float(r['VLATUAL']), float(r['VLORIGINAL'])
    low = min(cur, orig)
    contracts.append({
        'contract': r['NUCONTRATO'], 'contractor': r['CONTRATADO'], 'signed': r['DTASSINATURA'][:10],
        'status': r['SITUACAO'], 'object': ' '.join((r['OBJETO'] or '').split()),
        'original_value_brl_nominal': orig, 'current_value_brl_nominal': cur,
        'ipca_index_signing_month': IPCA[ym], 'ipca_factor_to_dec2024': round(fac, 6),
        'current_value_brl_2024': round(cur * fac, 2),
        'lower_bound_value_brl_2024': round(low * fac, 2),
    })
    tot_cur += cur * fac
    tot_low += low * fac

HL_LENGTH = 821.0
HL_WIDTH = 9.2 + 2 * 2.5
HL_AREA = round(HL_LENGTH * HL_WIDTH, 2)

# first-stage access-viaduct works (2006), official timeline, approximate, NOT in the SIGEF CSV
stage1_nominal = 21_000_000.0
stage1_2024 = stage1_nominal * IPCA[TARGET] / IPCA['200602']

hercilio = {
    'name': 'Ponte Hercílio Luz (restauração)',
    'country': 'Brazil',
    'years': '2006-2019 (contratos assinados); obra principal 2016-2020',
    'scope': ('Substituição das barras de olhal, selas, rótulas (aparelhos de apoio) e pendurais; reforço de todas as fundações; '
              'estrutura provisória de sustentação sob o vão central com transferência de carga; substituição de cerca de 2.000 t '
              'de estrutura metálica; novo tabuleiro ortotrópico de aço (pista e dois passeios); substituição de rebites; '
              'pintura anticorrosiva de 70.000 m2; supervisão, projetos complementares e orçamento de referência.'),
    'length_m': HL_LENGTH, 'main_span_m': 339.471, 'deck_width_m': HL_WIDTH,
    'deck_width_note': 'Largura útil: pista de rolamento 9,2 m + dois passeios de 2,5 m (fonte: contratada). Largura total fora a fora não encontrada.',
    'deck_area_m2': HL_AREA,
    'cost_reported': {'amount': 484645236.82, 'currency': 'BRL', 'year': '2006-2019',
                      'basis': 'Soma do valor atual (com aditivos) dos 13 contratos de restauração, supervisão e projetos registrados no SIGEF; valor de contrato, nominal, não valor pago.'},
    'cost_brl_2024_fx': round(tot_cur, 2), 'cost_brl_2024_ppp': round(tot_cur, 2),
    'cost_per_m2_brl_2024_fx': round(tot_cur / HL_AREA, 2), 'cost_per_m2_brl_2024_ppp': round(tot_cur / HL_AREA, 2),
    'lower_bound_cost_brl_2024': round(tot_low, 2),
    'lower_bound_cost_per_m2_brl_2024': round(tot_low / HL_AREA, 2),
    'lower_bound_note': ('Para cada contrato, o menor entre valor original e valor atual, corrigido pelo IPCA desde a assinatura. '
                         'O valor atual inclui aditivos de reajuste, que já são correção monetária; corrigi-lo de novo desde a '
                         'assinatura conta parte da inflação duas vezes. O número real fica entre o limite inferior e o central.'),
    'not_included': {
        'first_stage_access_viaducts_2006': {'amount_brl_nominal_approx': stage1_nominal, 'signed_or_started': '2006-02-17',
                                             'amount_brl_2024_approx': round(stage1_2024, 2),
                                             'note': 'Primeira etapa (viadutos de acesso), "contratada por aproximadamente R$ 21 milhões" segundo a linha do tempo oficial do Governo de SC; não aparece no CSV do SIGEF.'},
        'before_2006': 'Nada de 1982 a 2005 está no registro de contratos (o CSV praticamente começa em 2006).',
        'after_reopening': '8 contratos posteriores (iluminação cênica, manutenção, entorno) ficam fora, como na verificação de 2026-09-25.',
    },
    'contracts': contracts,
    'sources': [
        {'field': 'contracts', 'url': URL_CONTRACTS},
        {'field': 'length_m, deck_width_m, scope', 'url': 'https://www.teixeiraduarteconstrucao.com.br/projetos/reabilitacao-e-restauro-da-ponte-hercilio-luz/'},
        {'field': 'length_m, main_span_m', 'url': 'https://grante.ufsc.br/graduacao_informacoes/historico/recuperacao-da-ponte-hercilio-luz/'},
        {'field': 'length_m (official, 821 m)', 'url': 'http://web.archive.org/web/20240807222022/https://www.sc.gov.br/vivaaponte/caracteristicas-da-ponte-hercilio-luz/'},
        {'field': 'scope (engineering)', 'url': 'https://www.abcem.org.br/construmetal/downloads/apresentacao/42_DESAFIOS-DA-REABILITACAO-DE-ESTRUTURAS-METALICAS-ANTIGAS-PONTE-HERCILIO-LUZ.pdf'},
        {'field': 'not_included.first_stage_access_viaducts_2006', 'url': 'http://web.archive.org/web/20240807221921/https://www.sc.gov.br/vivaaponte/linha-do-tempo/'},
    ],
}

# ---------------------------------------------------------------- comparables
def build(p):
    tranches = p.pop('_tranches')
    fx_tot = ppp_tot = 0.0
    fdetail = []
    for year, amt in tranches:
        fxv, pppv, f = to_brl_2024(amt, p['_iso3'], year)
        fx_tot += fxv
        ppp_tot += pppv
        f['amount_lcu'] = amt
        f['amount_brl_2024_fx'] = round(fxv, 2)
        f['amount_brl_2024_ppp'] = round(pppv, 2)
        fdetail.append(f)
    p.pop('_iso3')
    p['conversion'] = fdetail
    p['cost_brl_2024_fx'] = round(fx_tot, 2)
    p['cost_brl_2024_ppp'] = round(ppp_tot, 2)
    p['cost_per_m2_brl_2024_fx'] = round(fx_tot / p['deck_area_m2'], 2)
    p['cost_per_m2_brl_2024_ppp'] = round(ppp_tot / p['deck_area_m2'], 2)
    return p

HU_TRANCHES_MHUF = [(2019, 22.530), (2020, 0.370), (2021, 7852.568), (2022, 9280.355), (2023, 9556.108), (2024, 39.230)]
szechenyi = {
    'name': 'Széchenyi Lánchíd (Ponte das Correntes), Budapeste',
    'country': 'Hungary', 'category': 'restoration_historic_chain_bridge',
    'years': '2021-2023 (obra); orçamento programado de 2019 a 2024',
    'scope': ('Ponte pênsil de correntes de barras de olhal (1849, reconstruída 1947-1949). Demolição do tabuleiro de concreto e '
              'novo tabuleiro ortotrópico de aço; passeios reconstruídos em aço; reparo e proteção anticorrosiva da estrutura '
              'metálica que ficou e das correntes (acima do tabuleiro, nos canais e nas câmaras de ancoragem); restauro de pedra, '
              'leões e guarda-corpos; nova iluminação; remanejamento de redes; impermeabilização das câmaras de ancoragem. '
              'As correntes foram tratadas, não substituídas.'),
    'length_m': 380.02, 'main_span_m': None,
    'main_span_note': 'Vão central não encontrado nas páginas oficiais lidas; deixado nulo.',
    'deck_width_m': round(6.45 + 2 * 2.17, 2),
    'deck_width_note': 'Largura útil: pista 6,45 m + dois passeios de 2,17 m. Largura total oficial: 14,5 m (inclui as vigas de rigidez entre pista e passeios).',
    'deck_area_m2': round(380.02 * (6.45 + 2 * 2.17), 2),
    'deck_area_m2_total_width': round(380.02 * 14.5, 2),
    'cost_reported': {'amount': 26751161000, 'currency': 'HUF', 'year': '2019-2024',
                      'basis': 'Custo total previsto, bruto (com IVA de 27%), do Megvalósítási megállapodás, 3ª alteração (18/01/2021), fixado depois da licitação; líquido: HUF 21.063.907.000. Inclui obra (HUF 20.593.332.000 líquidos), gestão e outros. É orçamento aprovado, não custo final auditado.'},
    '_iso3': 'HUN', '_tranches': [(y, v * 1e6) for y, v in HU_TRANCHES_MHUF],
    'spending_year_rule': 'Cada parcela anual do cronograma oficial convertida pelos fatores do seu próprio ano.',
    'sources': [
        {'field': 'cost_reported, annual schedule', 'url': 'https://bkk.hu/downloads/5957/'},
        {'field': 'cost_reported (gross 26,751 bn)', 'url': 'https://bkk.hu/fejlesztesek/kiemelt-fejlesztesek/archivum/a-lanchid-felujitasa/dokumentumok-kozbeszerzes-kozerdeku-adatok/'},
        {'field': 'length_m, deck_width_m', 'url': 'https://bkk.hu/fejlesztesek/kiemelt-fejlesztesek/archivum/fovarosi-fejlesztesek/kozteruleti-fejlesztesek/-a-szechenyi-lanchid-rekonstrukcioja.5786/'},
        {'field': 'scope', 'url': 'https://bkk.hu/blog/rozsdas-volt-ragyogo-lett-a-lanchid-felujitas-kulisszatitkai.10600/'},
        {'field': 'years (reopened 2023-08-04)', 'url': 'https://www.budapestkozut.hu/mernok-igazgatosag/szechenyi-lanchid/'},
    ],
}

lions_gate = {
    'name': "Lions' Gate Bridge, Vancouver (substituição da estrutura suspensa)",
    'country': 'Canada', 'category': 'restoration_suspension_deck_replacement',
    'years': '1999-2002 (contrato abril/1999; troca set/2000 a set/2001; pavimentação 2002)',
    'scope': ('Ponte pênsil de cabos (1938). Substituição de toda a estrutura suspensa (tabuleiro, passeios, treliças de rigidez e '
              'pendurais) com tabuleiro ortotrópico mais largo, feita em fechamentos noturnos; reforço sísmico. Torres, cabos '
              'principais e ancoragens mantidos.'),
    'length_m': 847.0, 'main_span_m': 472.0, 'deck_width_m': 16.2,
    'deck_width_note': 'Nova seção: 3 faixas de 3,6 m + 2 passeios de 2,7 m = 16,2 m.',
    'deck_area_m2': round(847.0 * 16.2, 2),
    'cost_reported': {'amount': 66000000, 'currency': 'CAD', 'year': 2001,
                      'basis': '"Approximately $66 million": parcela da ponte pênsil dentro do contrato de CAD 86,5 milhões (que inclui a via elevada e acessos). Só construção; não inclui projeto nem supervisão.'},
    '_iso3': 'CAN', '_tranches': [(2001, 66_000_000.0)],
    'spending_year_rule': '2001: a troca ocorreu de setembro/2000 a setembro/2001 (ponto médio em 2001). Não há cronograma anual publicado.',
    'source_type': 'Fonte de engenharia: artigo técnico do engenheiro do proprietário (Buckland & Taylor), conferência da Transportation Association of Canada. Não é documento do governo.',
    'sources': [
        {'field': 'cost_reported, length_m, main_span_m, deck_width_m, scope, years', 'url': 'https://www.tac-atc.ca/wp-content/uploads/Matson.pdf'},
    ],
}

alves_lima = {
    'name': 'Ponte Pênsil Alves de Lima, Chavantes (SP)',
    'country': 'Brazil', 'category': 'restoration_historic_suspension_light_scope',
    'years': '2023 (entregue em 20/10/2023)',
    'scope': 'Ponte pênsil de 1920, tombada. Reparos com substituição de componentes de madeira do guarda-corpo e do tabuleiro (95 m3 de madeira, 21 t de aço). Escopo leve.',
    'length_m': 164.0, 'main_span_m': 80.0, 'deck_width_m': 4.0,
    'deck_area_m2': 164.0 * 4.0,
    'cost_reported': {'amount': 5900000, 'currency': 'BRL', 'year': 2023, 'basis': 'Investimento informado pelo DER-SP na entrega.'},
    '_iso3': 'BRA', '_tranches': [(2023, 5_900_000.0)],
    'spending_year_rule': '2023, ano da entrega; data de início não publicada na nota. Suposição sinalizada.',
    'sources': [
        {'field': 'cost_reported, length_m, main_span_m, deck_width_m, scope, years', 'url': 'http://web.archive.org/web/20260413175100/http://www.der.sp.gov.br/WebSite/Comunicacao/SalaImprensa.aspx?idNoticia=1659'},
    ],
}

thuan_phuoc = {
    'name': 'Cầu Thuận Phước, Da Nang (ponte pênsil nova)',
    'country': 'Vietnam', 'category': 'new_suspension_bridge',
    'years': '2003-2009 (início 17/01/2003; inauguração 19/07/2009)',
    'scope': ('Ponte nova. Trecho pênsil de 655 m (125 + 405 + 125 m) com viga caixão de aço e cabos principais de 360 mm, '
              'mais viadutos de acesso de concreto protendido de 600 m de cada lado. 4 faixas, 2 passeios, 2 faixas para bicicleta.'),
    'length_m': 1856.0, 'main_span_m': 405.0, 'deck_width_m': 18.0,
    'deck_area_m2': 1856.0 * 18.0,
    'deck_area_m2_suspension_part_only': 655.0 * 18.0,
    'cost_reported': {'amount': 1_000_000_000_000, 'currency': 'VND', 'year': '2003-2009',
                      'basis': '"Tổng vốn đầu tư gần 1.000 tỷ đồng" (investimento total de quase 1 trilhão de dong), dito na inauguração. Aproximado. Orçamento inicial de 2003: pouco mais de 587 bilhões, ajustado quatro vezes.'},
    '_iso3': 'VNM', '_tranches': [(2006, 1_000_000_000_000.0)],
    'spending_year_rule': '2006, ponto médio entre início (jan/2003) e inauguração (jul/2009); não há cronograma anual publicado.',
    'source_type': 'Geometria: portal oficial da cidade de Da Nang. Custo: FONTE SECUNDÁRIA (imprensa: Sài Gòn Giải Phóng, 19/07/2009), valor aproximado; nenhum documento oficial com o custo foi encontrado.',
    'sources': [
        {'field': 'length_m, main_span_m, deck_width_m, scope, years (opening)', 'url': 'https://danang.gov.vn/vi/web/dng/w/cau-thuan-phuoc-dai-lua-noi-doi-bo-song-han-i'},
        {'field': 'cost_reported (secondary, press)', 'url': 'https://www.sggp.org.vn/thanh-pho-da-nang-khanh-thanh-cau-thuan-phuoc-khoi-cong-xay-dung-cau-rong-post183851.html'},
        {'field': 'years (start 2003-01-17), budget history (secondary, press)', 'url': 'https://tuoitre.vn/cau-thuan-phuoc-bon-lan-nang-von-262119.htm'},
    ],
}

projects = [build(p) for p in (szechenyi, lions_gate, alves_lima, thuan_phuoc)]

# Szechenyi sensitivity on total width
sz = projects[0]
sz['cost_per_m2_brl_2024_fx_total_width'] = round(sz['cost_brl_2024_fx'] / sz['deck_area_m2_total_width'], 2)
sz['cost_per_m2_brl_2024_ppp_total_width'] = round(sz['cost_brl_2024_ppp'] / sz['deck_area_m2_total_width'], 2)
tp = projects[3]
tp['cost_per_m2_brl_2024_fx_suspension_part_only'] = round(tp['cost_brl_2024_fx'] / tp['deck_area_m2_suspension_part_only'], 2)
tp['cost_per_m2_brl_2024_ppp_suspension_part_only'] = round(tp['cost_brl_2024_ppp'] / tp['deck_area_m2_suspension_part_only'], 2)

used_years = sorted({f['year'] for p in projects for f in p['conversion']})
method = {
    'target': 'BRL de dezembro de 2024',
    'fx_method': 'amount_LCU * (BRL por USD / LCU por USD) do ano do gasto * IPCA dez/2024 / média anual do IPCA do ano do gasto',
    'ppp_method': 'amount_LCU * (fator PPP do Brasil / fator PPP do país) do ano do gasto * IPCA dez/2024 / média anual do IPCA do ano do gasto',
    'brl_projects': 'Valores em BRL: só a correção pelo IPCA. Na Ponte Hercílio Luz, do mês de assinatura de cada contrato até dez/2024.',
    'deck_area_rule': 'Comprimento total da obra x largura útil (pista + passeios) quando a fonte a traz; alternativas mostradas à parte.',
    'ipca': {'source': URL_IPCA, 'table': 'SIDRA 1737, variável 2266, número-índice (dez/1993 = 100)',
             'dec_2024': IPCA[TARGET],
             'year_averages': {y: round(ipca_year_avg(y), 4) for y in used_years}},
    'fx': {'source': URL_WB.format(ind='PA.NUS.FCRF'), 'indicator': 'PA.NUS.FCRF, Official exchange rate (LCU per US$, period average), World Bank WDI',
           'last_updated': FX_UPDATED,
           'values': {c: {y: FX[c][y] for y in used_years if y in FX.get(c, {})} for c in ('BRA', 'HUN', 'CAN', 'VNM')}},
    'ppp': {'source': URL_WB.format(ind='PA.NUS.PPP'), 'indicator': 'PA.NUS.PPP, PPP conversion factor, GDP (LCU per international $), World Bank WDI / ICP',
            'last_updated': PPP_UPDATED,
            'values': {c: {y: PPP[c][y] for y in used_years if y in PPP.get(c, {})} for c in ('BRA', 'HUN', 'CAN', 'VNM')}},
    'collected': COLLECTED,
}

excluded = [
    {'name': 'Clifton Suspension Bridge (Reino Unido)', 'reason': 'Não verificado nesta coleta (limite de buscas); nenhuma obra de restauração com custo publicado apareceu nas buscas feitas. Candidato a verificar.'},
    {'name': 'Hammersmith Bridge (Reino Unido)', 'reason': 'Não verificado nesta coleta (limite de buscas). Até onde se sabe, a restauração completa não foi executada, então não haveria custo realizado; candidato a verificar.'},
    {'name': 'Menai Suspension Bridge (País de Gales)', 'reason': 'Obras em andamento; a imprensa técnica (New Civil Engineer, 27/01/2026) fala em conclusão em 2027. Sem custo final; não verificado em fonte oficial.'},
    {'name': 'Brooklyn Bridge (EUA)', 'reason': 'Programa de reconstrução em contratos de 1980 a 2023; NYC DOT publica valores por contrato (ex.: Contrato 6, 2010-2017, US$ 650 milhões, acessos e pintura), mas não o total da restauração nem a distribuição anual; a soma não seria comparável.'},
    {'name': 'Angus L. Macdonald Bridge "Big Lift" (Canadá)', 'reason': 'Escopo muito parecido (troca da estrutura suspensa, 2015-2019), mas o custo final não aparece nos relatórios anuais da Halifax Harbour Bridges; a estimativa oficial de 2014 era "na faixa de CAD 150 milhões" só para a construção, e a largura do tabuleiro publicada é inconsistente (11,5 m ou 34,8 pés).'},
    {'name': 'Pont de Tancarville (França)', 'reason': 'Troca da suspensão de 1996 a 1999 (página oficial da CCI), sem troca de tabuleiro; o custo de 240 milhões de francos só apareceu em fonte secundária.'},
]

out = {'generated': COLLECTED, 'hercilio_luz': hercilio, 'comparables': projects, 'excluded_candidates': excluded, 'method': method}
json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
print('wrote', OUT)

# ---------------------------------------------------------------- console tables
def brl(x):
    return f"{x:,.0f}".replace(',', '.')
print('\nHercilio Luz contracts')
for c in contracts:
    print(c['signed'], c['contract'], brl(c['current_value_brl_nominal']), c['ipca_factor_to_dec2024'], brl(c['current_value_brl_2024']), brl(c['lower_bound_value_brl_2024']))
print('HL total 2024 central', brl(tot_cur), 'lower', brl(tot_low), 'area', HL_AREA, 'per m2', brl(tot_cur / HL_AREA), 'lower per m2', brl(tot_low / HL_AREA))
print('stage1 2006 approx 2024', brl(stage1_2024))
print('\nComparables')
for p in projects:
    print(p['name'], '| area', p['deck_area_m2'], '| fx', brl(p['cost_brl_2024_fx']), '| ppp', brl(p['cost_brl_2024_ppp']), '| /m2 fx', brl(p['cost_per_m2_brl_2024_fx']), '| /m2 ppp', brl(p['cost_per_m2_brl_2024_ppp']))
    for f in p['conversion']:
        print('   ', f)
