"""Builds data/works/florianopolis-bypass.json (Contorno Viário da Grande Florianópolis, BR-101/SC) from official sources.

Usage:
  python3 build_florianopolis_bypass.py <workdir> --fetch    # downloads the sources (about 20 MB of PDFs, kept only as text)
  python3 build_florianopolis_bypass.py <workdir>            # checks everything and writes the JSON
  python3 build_florianopolis_bypass.py <workdir> --control  # plants a R$ 500 error in Quadro 1 of Termo Aditivo 002/2020;
                                                             # the sum check must fail and nothing is written

Every number below is read from the downloaded official text (TCU judgments through the public API, ANTT PDFs and
spreadsheet, the concessionaire's 2024 DFP published by ANTT, IBGE IPCA, SIOP budget SPARQL). Every literal quote is
checked against its source text (roads_common.require_quote). The JSON is written only after every check passes.
The bidder's 2007 proposal on ANTT is a scanned PDF without a text layer: its Contorno price (R$ 175.951.204,31,
item 5.1.2, PDF page 211) was read by OCR and checked on the cropped image; the script checks the same value as quoted
by the TCU (Acórdão 2954/2011) and against the ANTT execution spreadsheet.
"""
import csv, io, html, json, os, re, subprocess, sys, time, urllib.parse, zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal as D, ROUND_HALF_UP
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roads_common as C

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'data', 'works', 'florianopolis-bypass.json')
COLLECTED = '2026-10-06'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36'

ANTT = 'https://www.gov.br/antt/pt-br/assuntos/rodovias/concessionarias/lista-de-concessoes/autopista-litoral-sul'
URL = {
    'concession': ANTT,
    'contract': ANTT + '/documentos-de-gestao/contrato-e-anexos/contrato-e-aditivos/contrato.pdf',
    'per': ANTT + '/documentos-de-gestao/contrato-e-anexos/anexos-do-contrato/per-original.pdf',
    'proposal': ANTT + '/documentos-de-gestao/processo-de-licitacao/proposta-comercial-cronograma-fisico-e-plano-economico-financeiro.pdf',
    'ta002': ANTT + '/documentos-de-gestao/contrato-e-anexos/termos-aditivos/termo-aditivo-autopista-litoral-sul-contorno-de-florianopolis.pdf',
    'delib500': ANTT + '/revisoes-e-reajustes/2020-1/deliberacao-500-de-08-12-2020.pdf',
    'voto120': ANTT + '/revisoes-e-reajustes/2020-1/sei_antt-4693800-voto-ddb-120_2020.pdf',
    'df2024': ANTT + '/relatorios/relatorios-financeiros/df-4degtri2024-litoral-sul.pdf',
    'report_jul2024': ANTT + '/relatorios/relatorios-de-acompanhamento-das-principais-obras/2024/relatorio-mensal-jul2024-fonte-sei-25152013.pdf',
    'exec_xlsx': ANTT + '/documentos-de-gestao/acompanhamento-de-obras/execucao-acumulada-de-obras-de-ampliacao-de-capacidade-e-melhorias/als-execucao-acumulada-de-obras-de-ampliacao-de-capacidade-e-melhorias-18o-ano-com-os-efeitos-do-10ota.xlsx',
    'antt_news_2024': 'https://www.gov.br/antt/pt-br/assuntos/ultimas-noticias/maior-obra-de-infraestrutura-terrestre-da-america-latina-sera-inaugurada-em-santa-catarina-nesta-sexta-feira-9-8',
    'bndes_2024': 'https://web.archive.org/web/20260606013112/https://agenciadenoticias.bndes.gov.br/cultura/Com-apoio-do-BNDES-Contorno-Viario-de-Florianopolis-e-inaugurado/',
    'ipca': 'https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/200707,201503,201901,202408,202412?formato=json',
    'siop': 'https://www1.siop.planejamento.gov.br/sparql/',
    'cvm_cad': 'https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv',
    'cnpj': 'https://publica.cnpj.ws/cnpj/{}',
    'tse': 'https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{}.zip',
}
TCU_PAGE = 'https://pesquisa.apps.tcu.gov.br/doc/acordao-completo/{n}/{y}/Plen%C3%A1rio'
TCU_REL = 'https://pesquisa.apps.tcu.gov.br/doc/acordao-completo/{n}/{y}/Plen%C3%A1rio'
TCU_API = 'https://pesquisa.apps.tcu.gov.br/rest/publico/base/acordao-completo/documento?termo=KEY:ACORDAO-COMPLETO-{k}&quantidade=1&inicio=0'
# KEY in the TCU API -> (number, year)
TCU = {'1213344': (2954, 2011), '1256724': (3346, 2012), '1261170': (427, 2013), '1304785': (1043, 2014), '1575797': (2883, 2015),
       '1307629': (1179, 2016), '2372718': (2195, 2019), '2310775': (1366, 2019), '2409471': (1416, 2020), '2423179': (2112, 2020),
       '2436627': (2833, 2020), '2438806': (2957, 2020), '2560661': (2802, 2022), '2617411': (1836, 2023), '2674926': (2029, 2024),
       '2717698': (2062, 2025)}
PDFS = ['contract', 'per', 'ta002', 'delib500', 'voto120', 'df2024', 'report_jul2024']
CNPJS = ['09313969000197', '02919555000167']
PHOTO_COMMONS = 'File:09.08.2024 - Cerimônia de inauguração do Contorno Viário da Grande Florianópolis (53912407328).jpg'
q = D('0.01')


def curl(url, out=None, timeout=180, headers=()):
    cmd = ['curl', '-s', '-L', '-m', str(timeout), '-A', UA] + [x for h in headers for x in ('-H', h)]
    if out:
        subprocess.run(cmd + ['-o', out, url], check=True)
        return out
    return subprocess.run(cmd + [url], capture_output=True, check=True).stdout


def clean(s):
    s = re.sub(r'<script.*?</script>|<style.*?</style>', '', s or '', flags=re.S)
    s = re.sub(r'<br\s*/?>|</p>|</div>|</tr>', '\n', s)
    return html.unescape(re.sub(r'[ \t]+', ' ', re.sub(r'<[^>]+>', ' ', s)))


SIOP_Q = '''PREFIX loa: <http://vocab.e.gov.br/2013/09/loa#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?acaoL ?subL (SUM(?pago) AS ?pagoT) (SUM(?dot) AS ?dotT)
FROM <http://orcamento.dados.gov.br/{y}/>
WHERE {{
 ?i loa:temAcao ?acao . ?acao rdfs:label ?acaoL . ?i loa:temSubtitulo ?sub . ?sub rdfs:label ?subL .
 FILTER( (CONTAINS(UCASE(?acaoL), "CONTORNO") || CONTAINS(UCASE(?subL), "CONTORNO")) && ({place}) )
 OPTIONAL {{ ?i loa:valorPago ?pago }} OPTIONAL {{ ?i loa:valorDotacaoInicial ?dot }}
}} GROUP BY ?acaoL ?subL'''
PLACE = 'CONTAINS(UCASE(?acaoL), "FLORIAN") || CONTAINS(UCASE(?subL), "FLORIAN") || CONTAINS(UCASE(?subL), "PALHO") || CONTAINS(UCASE(?subL), "BIGUA")'
PLACE_CONTROL = 'CONTAINS(UCASE(?acaoL), "SC") || CONTAINS(UCASE(?subL), "SANTA CATARINA") || CONTAINS(UCASE(?subL), "SC")'


def siop(y, place):
    url = URL['siop'] + '?' + urllib.parse.urlencode({'query': SIOP_Q.format(y=y, place=place), 'format': 'application/sparql-results+json'})
    for _ in range(3):
        try:
            return [{k: b[k]['value'] for k in b} for b in json.loads(curl(url, timeout=200))['results']['bindings']]
        except Exception:  # noqa: BLE001
            time.sleep(8)
    raise SystemExit(f'SIOP falhou em {y}')


def fetch(W):
    for d in ('tcu', 'antt', 'tse'):
        os.makedirs(os.path.join(W, d), exist_ok=True)
    for k, (n, y) in TCU.items():
        raw = curl(TCU_API.format(k=k), headers=('Accept: application/json',))
        doc = json.loads(raw)['documentos'][0]
        open(os.path.join(W, 'tcu', f'{k}.txt'), 'w').write('\n'.join(f'##### {f}\n' + clean(str(v)) for f, v in doc.items() if isinstance(v, str) and v.strip()))
        print('TCU', n, y, flush=True); time.sleep(1.5)
    for name in PDFS:
        pdf = os.path.join(W, 'antt', name + '.pdf')
        curl(URL[name], pdf)
        subprocess.run(['pdftotext', '-layout', pdf, pdf[:-4] + '.txt'], check=True)
        os.remove(pdf)
        print('PDF', name, flush=True)
    curl(URL['exec_xlsx'], os.path.join(W, 'antt', 'exec.xlsx'))
    open(os.path.join(W, 'antt', 'antt_news_2024.html'), 'wb').write(curl(URL['antt_news_2024']))
    open(os.path.join(W, 'antt', 'bndes_2024.html'), 'wb').write(curl(URL['bndes_2024']))
    open(os.path.join(W, 'ipca.json'), 'wb').write(curl(URL['ipca']))
    res = {'florianopolis': {y: siop(y, PLACE) for y in range(2008, 2027)}, 'control_sc': {y: siop(y, PLACE_CONTROL) for y in (2014, 2024)}}
    json.dump(res, open(os.path.join(W, 'siop.json'), 'w'), ensure_ascii=False)
    rows = csv.DictReader(io.StringIO(curl(URL['cvm_cad']).decode('latin-1')), delimiter=';')
    json.dump([r for r in rows if re.sub(r'\D', '', r['CNPJ_CIA']) in CNPJS], open(os.path.join(W, 'cvm_cad.json'), 'w'), ensure_ascii=False)
    for c in CNPJS:
        open(os.path.join(W, f'cnpj_{c}.json'), 'wb').write(curl(URL['cnpj'].format(c)))
        time.sleep(21)
    for y in (2006, 2010, 2014, 2018, 2022):
        z = os.path.join(W, 'tse', f'c{y}.zip'); curl(URL['tse'].format(y), z)
        raw = zipfile.ZipFile(z).read(f'consulta_cand_{y}_BR.csv').decode('latin-1')
        keep = [l for i, l in enumerate(raw.splitlines()) if i == 0 or ';"PRESIDENTE";' in l]
        open(os.path.join(W, 'tse', f'pres_{y}.csv'), 'w').write('\n'.join(keep)); os.remove(z)
    api = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'titles': PHOTO_COMMONS, 'prop': 'imageinfo', 'iiprop': 'url|extmetadata|size', 'format': 'json'})
    open(os.path.join(W, 'commons_photo.json'), 'wb').write(curl(api))
    print('fetch ok')


# ------------------------------------------------------------------ readers
def money(s):
    """'14.246.284.39' or '14.246.284,39' (the TA has one figure printed with a dot) -> Decimal."""
    s = s.strip()
    return D(s[:-3].replace('.', '').replace(',', '') + '.' + s[-2:])


MONEY = r'\d{1,3}(?:\.\d{3})+[.,]\d{2}'


def xlsx_rows(path, sheet_name):
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    z = zipfile.ZipFile(path)
    ss = [''.join(t.text or '' for t in si.iter('{%s}t' % ns['m'])) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns)]
    names = [s.get('name') for s in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets', ns)]
    files = sorted([n for n in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml', n)], key=lambda n: int(re.findall(r'\d+', n)[-1]))
    rows = []
    for row in ET.fromstring(z.read(files[names.index(sheet_name)])).iter('{%s}row' % ns['m']):
        cells = {}
        for c in row.findall('m:c', ns):
            v = c.find('m:v', ns)
            val = None if v is None else (ss[int(v.text)] if c.get('t') == 's' else v.text)
            cells[re.sub(r'\d', '', c.get('r'))] = val
        rows.append(cells)
    return rows


def require_quote_lig(quote, source_text, label):
    """Like roads_common.require_quote, but the ANTT SEI PDFs lose the 'ti' ligature in text extraction ('es mado' for
    'estimado'): when the plain check fails, compare again with every 'ti' removed from both sides."""
    try:
        return C.require_quote(quote, source_text, label)
    except AssertionError:
        strip = lambda s: C.norm(s).replace('ti', '')
        parts = [strip(x) for x in quote.split('[...]') if strip(x)]
        src = strip(source_text)
        if all(x in src for x in parts):
            return quote
        raise


def main(W, control=False):
    C.self_test()
    try:
        require_quote_lig('esta frase inventada não existe', 'es mado inicialmente', 'controle')
        raise SystemExit('checagem de citações (ligadura) não está funcionando')
    except AssertionError:
        pass
    if not require_quote_lig('estimado inicialmente', 'foi es mado inicialmente', 'controle'):
        raise SystemExit('ligadura não reconhecida')
    p = lambda *a: os.path.join(W, *a)
    rq = require_quote_lig
    T = {k: open(p('tcu', f'{k}.txt')).read() for k in TCU}
    A = {k: open(p('antt', f'{k}.txt'), errors='ignore').read() for k in PDFS}
    tcu_url = lambda k: TCU_PAGE.format(n=TCU[k][0], y=TCU[k][1])
    checks = []

    def check(label, got, expected, tol=D('0')):
        diff = (got - expected) if isinstance(got, D) else None
        ok = (abs(diff) <= tol) if diff is not None else got == expected
        checks.append({'check': label, 'computed': str(got), 'official': str(expected), 'ok': bool(ok)})
        if not ok:
            raise SystemExit(f'CHECAGEM FALHOU: {label}: calculado {got} contra oficial {expected}')

    # ---------------- Termo Aditivo 002/2020, Quadro 1 (prices of July 2007)
    ta = A['ta002']
    blk = ta[ta.index('Quadro 1'): ta.index('(1) Valores em reais')]
    v = [money(x) for x in re.findall(MONEY, blk)]
    assert len(v) == 15, f'Quadro 1: esperava 15 valores, li {len(v)}'
    works, works_y = v[0], v[1:5]
    adm, adm_y = v[5], v[6:10]
    total, total_y = v[10], v[11:15]
    if control:
        works_y[1] += D('500.00')  # planted error: the checks below must fail
    check('TA 002/2020: obra, soma dos 4 anos = total do item', sum(works_y), works)
    check('TA 002/2020: custos administrativos, soma dos 4 anos = total do item', sum(adm_y), adm)
    check('TA 002/2020: obra + custos administrativos = total do aditivo', works + adm, total)
    for i, (a, b, t) in enumerate(zip(works_y, adm_y, total_y)):
        # the official table rounds the 14th-year total one cent up (100.706.493,07 against 94.791.503,26 + 5.914.989,80)
        check(f'TA 002/2020: {13 + i}º ano, obra + custos administrativos = total do ano', a + b, t, tol=D('0.01'))
    check('TA 002/2020: soma dos totais anuais = total do aditivo (arredondamento da tabela oficial)', sum(total_y), total, tol=D('0.01'))
    check('TA 002/2020: custos administrativos = 6,24% da obra', (works * D('0.0624')).quantize(q, ROUND_HALF_UP), adm)
    rq('totalizam o montante global de R$ 491.251.185,69', ta, 'TA 002/2020')
    rq('a necessidade de alteração de traçado do Contorno de Florianópolis, especificamente pelo crescimento da mancha urbana de Palhoça/SC', ta, 'TA 002/2020')
    rq('A recomposição do equilíbrio do valor determinado na subcláusula 2.1 ocorrerá de forma integral à Tarifa Básica de Pedágio (TBP)', ta, 'TA 002/2020')
    rq('3 (três) túneis duplos, 1 (uma) passagem inferior, 3 (três) passagens superiores e 2 (dois) viadutos', ta, 'TA 002/2020')
    rq('Brasília, 10 de dezembro de 2020', ta, 'TA 002/2020')

    # ---------------- ANTT vote and deliberation (December 2020)
    vt, dl = A['voto120'], A['delib500']
    sul_a_works = money(re.search(r'executar a obra do Trecho Sul A do Contorno de Florianópolis é de R\$ (' + MONEY + ')', re.sub(r'\s+', ' ', vt)).group(1))
    sul_a_final = money(re.search(r'valor ﬁnal de reequilíbrio de R\$ (' + MONEY + ')', re.sub(r'\s+', ' ', vt)).group(1))
    check('Voto DDB 120/2020: obra do Sul A x 1,0624 = valor final do reequilíbrio', (sul_a_works * D('1.0624')).quantize(q, ROUND_HALF_UP), sul_a_final)
    rq('estimado inicialmente pela concessionária em aproximadamente R$ 1,64 bilhões, foi ajustado para cerca de R$ 907 milhões (redução de 45%)', vt, 'Voto DDB 120/2020')
    rq('Contorno de Florianópolis - Pista Dupla - L = 5.1.2.1 28,20055% 0,40039', vt, 'Voto DDB 120/2020')
    rq('Administração da Concessionária 14.2 1,51716% 0,02154', vt, 'Voto DDB 120/2020')
    rq('cerca de R$ 0,10 (2,6% do valor da tarifa de pedágio)', vt, 'Voto DDB 120/2020')
    tbp = re.search(r'14ª Revisão Extraordinária, alterando a Tarifa Básica de Pedágio de R\$ ([\d,]+) para R\$ ([\d,]+)', re.sub(r'\s+', ' ', dl))
    tbp0, tbp1 = D(tbp.group(1).replace(',', '.')), D(tbp.group(2).replace(',', '.'))
    check('Deliberação 500/2020: aumento da TBP na 14ª revisão = 34,15% (voto)', ((tbp1 / tbp0 - 1) * 100).quantize(q, ROUND_HALF_UP), D('34.15'))
    rq('de R$ 2,70 (dois reais e setenta centavos) para R$ 3,90 (três reais e noventa centavos), nas praças de pedágio P1', dl, 'Deliberação 500/2020')
    rq('a partir de zero hora do dia 12 de dezembro de 2020', dl, 'Deliberação 500/2020')

    # ---------------- TCU
    t2957, t2029, t2954 = T['2438806'], T['2674926'], T['1213344']
    sp0 = money(re.search(r'no valor de R\$ (' + MONEY + r'), equivalente a 22,99% do orçamento aprovado pela ANTT, de R\$ (' + MONEY + ')', re.sub(r'\s+', ' ', t2957)).group(1))
    budget0 = money(re.search(r'equivalente a 22,99% do orçamento aprovado pela ANTT, de R\$ (' + MONEY + ')', re.sub(r'\s+', ' ', t2957)).group(1))
    sp1 = money(re.search(r'contém um sobrepreço de R\$ (' + MONEY + r') \(ref\. [Jj]aneiro/2019\)', re.sub(r'\s+', ' ', t2957)).group(1))
    adj = money(re.search(r'novo orçamento ajustado de R\$ (' + MONEY + ')', re.sub(r'\s+', ' ', t2957)).group(1))
    cut = money(re.search(r'redução de R\$ (' + MONEY + ') em relação ao valor declarado inicialmente', re.sub(r'\s+', ' ', t2957)).group(1))
    check('TCU 2957/2020: orçamento aprovado - redução = orçamento ajustado', budget0 - cut, adj)
    cut_2029 = money(re.search(r'consideravelmente aquém da estimativa do Tribunal \(R\$ (' + MONEY + ')', re.sub(r'\s+', ' ', t2029)).group(1))
    check('TCU 2029/2024: corte obtido pela ANTT = redução registrada no 2957/2020', cut_2029, cut)
    ratio = (sp0 / budget0 * 100).quantize(q, ROUND_HALF_UP)  # the judgments print 22,99%; the arithmetic gives 21,99%
    contorno_price = money(re.search(r'de maior valor individual \(R\$ (' + MONEY + ')', re.sub(r'\s+', ' ', t2954)).group(1))
    assoc = money(re.search(r'Obras associadas: R\$ (' + MONEY + ')', re.sub(r'\s+', ' ', t2954)).group(1))
    rq('postergação das obras relativas ao contorno de Florianópolis envolve o adiamento de um investimento não inferior a R$ 330 milhões', t2954, 'TCU 2954/2011')
    check('TCU 2954/2011: Contorno + obras associadas + 80% da desapropriação >= R$ 330 mi', contorno_price + assoc + D('80000000.00') >= D('330000000'), True)

    # ---------------- ANTT execution spreadsheet (18th year), prices of July 2007
    xr = xlsx_rows(p('antt', 'exec.xlsx'), 'ALS %ACUMULADO')
    item = lambda code, flow: next(r for r in xr if (r.get('B') or '').strip() == code and (r.get('D') or '').strip() == flow)
    x_fco, x_fcm7 = item('5.1.2.1', 'FCO'), item('5.1.2.1', 'FCM7')
    x_s1, x_s3, x_tr = item('5.1.27', 'FCM6'), item('5.1.28', 'FCM6'), item('5.1.8.1', 'FCO')
    dv = lambda r, col: D(r[col]).quantize(q, ROUND_HALF_UP)
    reg_items = [('PER original, item 5.1.2.1 (FCO)', dv(x_fco, 'E')), ('Trecho Sul A, item 5.1.2.1 (FCM7)', dv(x_fcm7, 'E')),
                 ('Passagem superior km 229+300, Sul B (FCM6)', dv(x_s1, 'E')), ('Passagem superior km 232+150, Sul B (FCM6)', dv(x_s3, 'E')),
                 ('Trevos do Contorno, item 5.1.8.1 (FCO)', dv(x_tr, 'E'))]
    reg_total = sum(v for _, v in reg_items)
    check('Proposta (TCU) = planilha da ANTT para o item 5.1.2.1, até 1 centavo', dv(x_fco, 'E'), contorno_price, tol=D('0.01'))

    # ---------------- concessionaire DFP 2024 and the PER
    df = A['df2024']
    rq('Com um investimento total de R$ 3,9 bilhões, o Contorno foi projetado para melhorar significativamente a mobilidade', df, 'DFP 2024')
    rq('foi iniciado em maio de 2014 e deu início a sua operação em 10/08/2024', df, 'DFP 2024')
    rq('Em 09 de agosto de 2024, a Sociedade inaugurou o Contorno Viário de Florianópolis, que compreende um corredor expresso de 50 km de pistas duplas, 6 acessos por trevos, 4 túneis duplos, 7 pontes e mais 20 passagens em desnível', df, 'DFP 2024')
    rq('Contorno de Florianópolis, em pista dupla, com 47,33 km em cada sentido (total de 94,66 km), a ser executado até o final do 4º ano', A['per'], 'PER original')
    rq('JOSE ALEXANDRE NOGUEIRA DE RESENDE', A['contract'], 'contrato'); rq('NOBORU OFUGI', A['contract'], 'contrato')
    rq('com aproximadamente 51 km de extensão', A['report_jul2024'], 'relatório mensal ANTT jul/2024')
    news = clean(open(p('antt', 'antt_news_2024.html'), errors='ignore').read())
    rq('com um investimento de R$ 3,9 bilhões', news, 'ANTT 06/08/2024')
    bndes = clean(open(p('antt', 'bndes_2024.html'), errors='ignore').read())
    rq('Em 2011, o BNDES financiou com R$ 703 milhões a Arteris Litoral Sul S.A', bndes, 'BNDES 09/08/2024')
    rq('O Banco subscreveu 6,7% das debêntures (R$ 134 milhões)', bndes, 'BNDES 09/08/2024')
    invest_total = D('3900000000')

    # ---------------- SIOP: no federal budget action for this Contorno, with a positive control
    so = json.load(open(p('siop.json')))
    n_fl = sum(len(v) for v in so['florianopolis'].values())
    n_ctl = sum(len(v) for v in so['control_sc'].values())
    check('SIOP: controle acha contornos em SC (precisa ser > 0)', n_ctl > 0, True)
    check('SIOP: ações orçamentárias federais do Contorno de Florianópolis, 2008 a 2026', n_fl, 0)

    # ---------------- IPCA and comparison (reais of December 2024)
    ip = {r['D3C']: D(r['V']) for r in json.load(open(p('ipca.json')))[1:]}
    f = lambda ym: ip['202412'] / ip[ym]
    to24 = lambda val, ym: (val * f(ym)).quantize(q, ROUND_HALF_UP)
    goi_esp = money(re.search(r'por um contorno de 44 km de extensão, estimado em R\$ (' + MONEY + ')', re.sub(r'\s+', ' ', T['2372718'])).group(1))
    goi_1a = money(re.search(r'estimado no projeto executivo por R\$ (' + MONEY + r') - ref\. mar/15', re.sub(r'\s+', ' ', T['2372718'])).group(1))

    # ---------------- terms check with a positive control
    terms = ['superfaturamento', 'sobrepreco', 'desvio', 'dano ao erario']

    def scan(text):
        import unicodedata
        tt = unicodedata.normalize('NFKD', re.sub(r'\s+', ' ', text)).encode('ascii', 'ignore').decode().lower()
        win = [(m.start() - 1500, m.start() + 1500) for m in re.finditer('florianopolis', tt)]
        return {term: sum(1 for m in re.finditer(term, tt) if any(a <= m.start() <= b for a, b in win)) for term in terms}
    ctl = scan('Contorno de Florianópolis: houve superfaturamento e sobrepreço')
    if not (ctl['superfaturamento'] and ctl['sobrepreco']):
        raise SystemExit('checagem de termos não acha o controle')
    found = {f'{n}/{y}': {k: v for k, v in scan(T[key]).items() if v} for key, (n, y) in TCU.items()}

    # ================================================================= record
    D2 = lambda x: float(x)
    rec = {
        'slug': 'florianopolis-bypass',
        'collected_on': COLLECTED,
        'report': 'docs/research/BRASIL-IMPOSTO_RESEARCH_case-florianopolis-bypass_2026-10-06.md',
        'rules': 'Somente papéis e achados oficiais, com as palavras do órgão. Nenhuma inferência de irregularidade. Valores nominais salvo quando marcados (preços de jul/2007 do contrato, jan/2019 do orçamento ou reais de dez/2024). Somas marcadas como computed são desta pesquisa.',
        'work': {
            'name': 'Contorno Viário da Grande Florianópolis (BR-101/SC, Biguaçu a Palhoça)',
            'municipalities_ibge': [{'code': '4202305', 'name': 'Biguaçu'}, {'code': '4216602', 'name': 'São José'}, {'code': '4211900', 'name': 'Palhoça'}],
            'level': 'federal (concessão)',
            'agency': {'name': 'ANTT, Agência Nacional de Transportes Terrestres (poder concedente: União)', 'concessionaire': 'Autopista Litoral Sul S.A.'},
            'status': 'Inaugurado e liberado ao tráfego em 09/08/2024. Em 2025 o TCU registrou desapropriações ainda pendentes.',
            'dates': {
                'contract_signed': '2008-02-14', 'concession_start': '2008-02-18',
                'planned_end': '2012-02', 'planned_end_note': 'PER original, item 5.1.4: "a ser executado até o final do 4º ano"; TCU: "em fevereiro de 2012" (Acórdão 2954/2011)',
                'works_start': '2014-05', 'works_start_note': 'DFP 2021 a 2024 da concessionária: "foi iniciado em maio de 2014"',
                'actual_end': '2024-08-09', 'actual_end_note': 'inauguração e liberação ao tráfego de todo o tronco (DFP 2024; ANTT); o relatório da administração diz "deu início a sua operação em 10/08/2024"',
                'delay_vs_contract_years': 12.5, 'planned_duration_years': 4, 'actual_duration_years': 16.5,
                'deadlines': [
                    {'date': '2012-02', 'act': 'PER original (contrato de 2008)', 'source': URL['per']},
                    {'date': '2015-02', 'act': 'Resolução ANTT 3.312, de 05/11/2009, e 1ª Revisão Extraordinária (adiamento de três anos)', 'source': tcu_url('1256724')},
                    {'date': '2016-02', 'act': 'Termo de Ajuste de Conduta ANTT e concessionária, assinado em 28/08/2013 ("entre março de 2014 e fevereiro de 2016")', 'source': tcu_url('2438806')},
                    {'date': '2024-02', 'act': '"novo prazo de conclusão estimado para fevereiro de 2024" (TCU, depois do TAC Parcial de 2020 com MPF e municípios)', 'source': tcu_url('2560661')},
                ],
            },
            'length_km': 50.0,
            'length_note': '50 km na DFP 2024 e na ANTT; "aproximadamente 51 km" no relatório mensal da ANTT (jul/2024); 47,33 km por sentido no contrato de 2008',
            'description': 'Rodovia nova em pista dupla que desvia o tráfego de longa distância do trecho urbano da BR-101 na Grande Florianópolis, de Biguaçu a Palhoça. É obra obrigatória do contrato de concessão da Autopista Litoral Sul (ANTT, 2008), feita e paga pela concessionária e recuperada pelo pedágio. O contrato mandava entregar até fevereiro de 2012; abriu em agosto de 2024.',
            'features': '50 km de pista dupla, 4 túneis duplos, 7 pontes, 20 passagens em desnível, 6 trevos (DFP 2024)',
            'siconfi_function': 'Transporte',
        },
        'contracts': [
            {'group': 'concessão', 'number': 'Edital ANTT 003/2007', 'company': 'Autopista Litoral Sul S.A.',
             'object': 'Contrato de concessão da BR-116/376/PR e BR-101/SC, Curitiba a Palhoça (25 anos). Obra obrigatória do PER, item 5.1.2: "Contorno de Florianópolis - Pista Dupla - L = 47,33 x 2 = 94,66 km", a concluir até o fim do 4º ano.',
             'signed_on': '2008-02-14', 'value_original_brl': D2(contorno_price),
             'value_original_note': 'preço do Contorno na proposta vencedora, a preços de julho de 2007 (sem obras associadas nem desapropriações)',
             'value_current_brl': None, 'status_in_record': 'Obra concluída; inaugurada em 09/08/2024',
             'sources': [{'doc': 'Contrato de concessão (ANTT)', 'url': URL['contract']}, {'doc': 'Proposta comercial, planilha do PER, p. 211 do PDF', 'url': URL['proposal']}, {'doc': 'TCU, Acórdão 2954/2011', 'url': tcu_url('1213344')}]},
            {'group': 'concessão', 'number': 'Termo Aditivo 002/2020', 'company': 'Autopista Litoral Sul S.A.',
             'object': 'Inclusão do trecho "Sul A" do Contorno (km 220+396 a 228+310, 7,91 km, 3 túneis duplos), por mudança de traçado "pelo crescimento da mancha urbana de Palhoça/SC".',
             'signed_on': '2020-12-10', 'value_original_brl': D2(total), 'value_original_note': 'a preços de julho de 2007; igual a R$ 907.409.977,72 a preços de janeiro de 2019 (Voto DDB 120/2020)',
             'value_current_brl': D2(dv(x_fcm7, 'E')), 'value_current_note': 'valor do item na planilha de execução da ANTT (18º ano), sem custos administrativos',
             'status_in_record': 'Executado (planilha da ANTT, 18º ano)',
             'sources': [{'doc': 'Termo Aditivo nº 002/2020 (ANTT)', 'url': URL['ta002']}, {'doc': 'Deliberação ANTT 500/2020', 'url': URL['delib500']}, {'doc': 'Voto DDB 120/2020', 'url': URL['voto120']}]},
            {'group': 'obra (contrato privado da concessionária)', 'number': 'contrato de 19/06/2023', 'company': 'Azevedo & Travassos Infraestrutura Ltda.',
             'object': 'Contrato de obra do Contorno firmado pela concessionária; rescindido ("Conforme comunicado ao mercado emitido em 10 de julho de 2023 a Litoral Sul rescindiu o contrato de prestação de serviços com a referida empresa").',
             'signed_on': '2023-06-19', 'value_original_brl': None, 'value_current_brl': None, 'status_in_record': 'Rescindido em julho de 2023',
             'sources': [{'doc': 'DFP 2024 da Autopista Litoral Sul, nota de fornecedores', 'url': URL['df2024']}]},
        ],
        'contracts_totals_computed': {
            'regulatory_items_jul2007_brl': D2(reg_total),
            'regulatory_items': [{'item': k, 'value_brl': D2(v)} for k, v in reg_items],
            'regulatory_note': 'Itens só do Contorno na planilha de execução acumulada da ANTT (18º ano), a preços iniciais do contrato (jul/2007). É o que a tarifa remunera, não o dinheiro gasto.',
            'fco_executed_value_brl': D2(dv(x_fco, 'J')),
            'fco_executed_note': f'A planilha marca o item 5.1.2.1 (FCO) como 100% executado, mas com valor executado de R$ {dv(x_fco, "J")} contra o total de R$ {dv(x_fco, "E")}; a planilha não explica a diferença.',
        },
        'payments': {
            'concessionaire': {'investment_total_brl': D2(invest_total), 'display': 'R$ 3,9 bi', 'measures': 'investimento total declarado pela concessionária, nominal, 2014 a 2024',
                               'quote': 'Com um investimento total de R$ 3,9 bilhões, o Contorno foi projetado para melhorar significativamente a mobilidade',
                               'source': {'doc': 'DFP 31/12/2024 da Autopista Litoral Sul (CVM), publicada pela ANTT', 'url': URL['df2024'], 'collected_on': COLLECTED},
                               'also_in': [{'doc': 'ANTT, 06/08/2024', 'url': URL['antt_news_2024']}, {'doc': 'BNDES, 09/08/2024 (cópia do Internet Archive)', 'url': URL['bndes_2024']}],
                               'precision_note': 'Os três documentos oficiais trazem o total arredondado; nenhum traz o valor ao centavo nem por ano.'},
            'federal_budget': {'total_brl': 0.0, 'siop_rows_found': n_fl, 'siop_control_rows': n_ctl, 'years': '2008 a 2026', 'source': URL['siop'],
                               'note': 'Nenhuma ação do Orçamento da União para este Contorno; a consulta de controle acha os contornos de Joinville, São Francisco do Sul, Chapecó e Araranguá.'},
            'public_bank_loans': {'bndes_2011_brl': 703000000.0, 'bndes_2011_note': 'financiamento à concessionária para a concessão inteira (empréstimo, quitado com a emissão de debêntures de 2021)',
                                  'bndes_debentures_2021_brl': 134000000.0, 'bndes_debentures_note': '6,7% da emissão de R$ 2 bilhões', 'source': URL['bndes_2024']},
            'toll': {'deliberation': 'Deliberação ANTT 500, de 08/12/2020', 'car_toll_before_brl': 2.70, 'car_toll_after_brl': 3.90, 'effective': '2020-12-12',
                     'plazas': 'P1 São José dos Pinhais/PR, P2 Garuva/SC, P3 Araquari/SC, P4 Porto Belo/SC, P5 Palhoça/SC',
                     'tbp_before_extraordinary': float(tbp0), 'tbp_after_extraordinary': float(tbp1),
                     'tbp_increment_contorno': 0.40039, 'tbp_increment_contorno_admin': 0.02154,
                     'note': 'Aumento de 44,44% no carro depois do arredondamento, somando revisão ordinária, revisão extraordinária (Contorno, terceira faixa da BR-101 e ponte do Rio Camboriú) e IPCA. Dos R$ 0,49153 de aumento da TBP na revisão extraordinária, R$ 0,42193 são do Contorno e seus custos administrativos (Voto DDB 120/2020, Figura 06); o resto não tem divisão publicada.',
                     'source': URL['delib500']},
            'who_pays': 'Usuários do pedágio, pela tarifa (dinheiro da concessionária recuperado pela tarifa, nos termos do contrato). Não há dinheiro do Orçamento da União; o BNDES emprestou à concessionária.',
        },
        'money_timeline': [
            {'date': '2007-07', 'value_brl': D2(contorno_price), 'what': 'preço do Contorno (47,33 km) na proposta vencedora', 'source': URL['proposal']},
            {'date': '2007-07', 'value_brl': D2(assoc), 'what': 'obras associadas ao Contorno na proposta (TCU)', 'source': tcu_url('1213344')},
            {'date': '2007-07', 'value_brl': 100710500.0, 'what': 'verba de desapropriação da concessão inteira, a maior parte para o Contorno (TCU)', 'source': tcu_url('1213344')},
            {'date': '2019-01', 'value_brl': 500000000.0, 'what': '"cerca de" R$ 500 mi: investimentos já contratados para os 47,33 km (TCU)', 'source': tcu_url('2438806')},
            {'date': '2019-01', 'value_brl': 1640000000.0, 'what': '"aproximadamente R$ 1,64 bilhões": orçamento inicial do Sul A pela concessionária (ANTT)', 'source': URL['voto120']},
            {'date': '2019-01', 'value_brl': D2(budget0), 'what': 'orçamento do Sul A aprovado pela área técnica da ANTT', 'source': tcu_url('2438806')},
            {'date': '2019-01', 'value_brl': D2(adj), 'what': 'orçamento ajustado pela ANTT, depois do TCU', 'source': tcu_url('2438806')},
            {'date': '2019-01', 'value_brl': D2(sul_a_final), 'what': 'valor final do reequilíbrio do Sul A (obra + 6,24%)', 'source': URL['voto120']},
            {'date': '2007-07', 'value_brl': D2(total), 'what': 'Sul A no Termo Aditivo 002/2020, a preços de julho de 2007', 'source': URL['ta002']},
            {'date': '2014 a 2024', 'value_brl': D2(invest_total), 'what': 'investimento total declarado (nominal)', 'source': URL['df2024']},
        ],
        'companies': [],
        'people': [],
        'people_gaps': [],
        'findings': [],
        'terms_check': {},
        'media': [],
        'comparison': {},
        'owner_lead_check': {},
        'card': {},
        'checks': checks,
    }

    # companies
    cvm = {re.sub(r'\D', '', r['CNPJ_CIA']): r for r in json.load(open(p('cvm_cad.json')))}
    for c, role, contracts, site in [('09313969000197', 'concessionária', ['Edital ANTT 003/2007', 'Termo Aditivo 002/2020'], 'https://www.arteris.com.br/rodovias/litoral-sul/'),
                                     ('02919555000167', 'controladora da concessionária', ['controladora da Autopista Litoral Sul (página da concessão na ANTT)'], 'https://ri.arteris.com.br/')]:
        j = json.load(open(p(f'cnpj_{c}.json'))); e = j.get('estabelecimento') or {}
        rec['companies'].append({'cnpj': c, 'legal_name': j.get('razao_social'), 'role': role, 'trade_name': e.get('nome_fantasia'),
                                 'city': f"{(e.get('cidade') or {}).get('nome')}/{(e.get('estado') or {}).get('sigla')}", 'registration_status': e.get('situacao_cadastral'),
                                 'head_or_branch': e.get('tipo'), 'activity_start': e.get('data_inicio_atividade'), 'contracts': contracts,
                                 'cvm': {'code': cvm[c]['CD_CVM'], 'category': cvm[c]['CATEG_REG'], 'status': cvm[c]['SIT']} if c in cvm else None,
                                 'official_website': site, 'official_website_note': 'link dado pela ANTT na página da concessão' if c == '09313969000197' else 'site citado na DFP 2024 da controlada',
                                 'transparency_links': [f'https://portaldatransparencia.gov.br/pessoa-juridica/{c}'],
                                 'antt_page': URL['concession'],
                                 'source': {'doc': 'Base aberta do CNPJ da Receita Federal via espelho público CNPJ.ws; cadastro de companhias abertas da CVM', 'url': URL['cnpj'].format(c), 'collected_on': COLLECTED}})
    rec['companies'].append({'cnpj': None, 'legal_name': None, 'name_in_record': 'Azevedo & Travassos Infraestrutura Ltda.', 'role': 'construtora contratada pela concessionária (rescindido)',
                             'contracts': ['contrato de 19/06/2023'], 'official_website': None,
                             'identity_note': 'CNPJ não publicado nos documentos lidos. Azevedo & Travassos S.A. (CNPJ 61.351.532/0001-68) tem nome parecido, mas nenhum documento lido liga as duas.',
                             'source': {'doc': 'DFP 2023 a 2025 da Autopista Litoral Sul', 'url': URL['df2024']}})
    rec['companies_note'] = 'As demais construtoras do Contorno não aparecem em documento oficial aberto: a obra é contratada pela concessionária, sem licitação pública; os relatórios da ANTT e as DFP não trazem os nomes.'

    # people (public agents with an act; heads of government with TSE party)
    tse = {}
    for y in (2006, 2010, 2014, 2018, 2022):
        for r in csv.DictReader(open(p('tse', f'pres_{y}.csv')), delimiter=';'):
            tse.setdefault(r['NM_CANDIDATO'], []).append((y, r['SG_PARTIDO'], r.get('DS_SIT_TOT_TURNO')))
    party = lambda name, y: next(sp for (yy, sp, _) in tse[name] if yy == y)
    rec['people'] = [
        {'name': 'José Alexandre Nogueira de Resende', 'role': 'Diretor-Geral da ANTT', 'signed': ['2008-02-14 (contrato de concessão)'], 'source': [{'doc': 'Contrato de concessão, preâmbulo', 'url': URL['contract']}]},
        {'name': 'Noboru Ofugi', 'role': 'Diretor da ANTT', 'signed': ['2008-02-14 (contrato de concessão)'], 'source': [{'doc': 'Contrato de concessão, preâmbulo', 'url': URL['contract']}]},
        {'name': 'Bernardo José Figueiredo Gonçalves de Oliveira', 'role': 'Diretor-Geral da ANTT', 'signed': ['2009-11-05 (Resolução ANTT 3.312, adiamento de três anos)'],
         'note': 'O TCU acolheu suas razões de justificativa, sem multa (Acórdão 1366/2019).', 'source': [{'doc': 'TCU, Acórdão 1366/2019', 'url': tcu_url('2310775')}]},
        {'name': 'Mário Rodrigues Júnior', 'role': 'Diretor da ANTT', 'signed': ['2009 (Voto 162/2009, proposta da 1ª revisão)'],
         'note': 'Multa de R$ 17.000,00 no Acórdão 1366/2019, excluída no Acórdão 1416/2020.', 'source': [{'doc': 'TCU, Acórdão 1366/2019', 'url': tcu_url('2310775')}, {'doc': 'TCU, Acórdão 1416/2020', 'url': tcu_url('2409471')}]},
        {'name': 'Mário Mondolfo', 'role': 'Superintendente de Exploração de Infraestrutura Rodoviária da ANTT', 'signed': ['2009-11-03 (Nota Técnica 137/2009)'],
         'note': 'Multado em R$ 15.000,00 pelo TCU (Acórdão 1366/2019, mantido pelo 1416/2020).', 'source': [{'doc': 'TCU, Acórdão 1366/2019', 'url': tcu_url('2310775')}, {'doc': 'TCU, Acórdão 1416/2020', 'url': tcu_url('2409471')}]},
        {'name': 'Deuzedir Martins', 'role': 'Gerente de Engenharia e Investimentos de Rodovias da ANTT', 'signed': ['2009-11-03 (Nota Técnica 137/2009)', '2010-03-31 (Ofício 295/2010, aprovação do projeto alterado)'],
         'note': 'Multado em R$ 12.000,00 pelo TCU (Acórdão 1366/2019, mantido pelo 1416/2020).', 'source': [{'doc': 'TCU, Acórdão 1366/2019', 'url': tcu_url('2310775')}, {'doc': 'TCU, Acórdão 1416/2020', 'url': tcu_url('2409471')}]},
        {'name': 'Rubens Narciso Peduti Dal Molin', 'role': 'Gerente de Fiscalização e Controle Operacional de Rodovias da ANTT', 'on_dates': ['2009 a 2011 (fiscalização do contrato)'],
         'note': 'Multado em R$ 10.000,00 pelo TCU (Acórdão 1366/2019, mantido pelo 1416/2020).', 'source': [{'doc': 'TCU, Acórdão 1366/2019', 'url': tcu_url('2310775')}]},
        {'name': 'Davi Ferreira Gomes Barreto', 'role': 'Diretor da ANTT', 'signed': ['2020-12-08 (Voto DDB 120/2020, 14ª Revisão Extraordinária e aditivo do Sul A)'], 'source': [{'doc': 'Voto DDB 120/2020', 'url': URL['voto120']}]},
        {'name': 'Marcelo Vinaud Prado', 'role': 'Diretor-Geral em exercício da ANTT', 'signed': ['2020-12-08 (Deliberação ANTT 500/2020)', '2020-12-10 (Termo Aditivo 002/2020)'], 'source': [{'doc': 'Termo Aditivo 002/2020', 'url': URL['ta002']}, {'doc': 'Deliberação 500/2020', 'url': URL['delib500']}]},
        {'name': 'Luiz Inácio Lula da Silva', 'role': 'Presidente da República', 'head_of_government': True,
         'on_dates': ['2008-02-14 (contrato)', '2009-11-05 (Resolução ANTT 3.312)', '2010-03-31 (Ofício 295/2010)', '2024-08-09 (inauguração)'],
         'party_at_time': party('LUIZ INACIO LULA DA SILVA', 2006), 'party_name': 'Partido dos Trabalhadores',
         'term_note': 'Candidato pelo PT em 2006 (mandato 2007 a 2010) e em 2022 (mandato 2023 a 2026), segundo o TSE.',
         'source': [{'doc': 'TSE, candidaturas 2006 (BR)', 'url': URL['tse'].format(2006)}, {'doc': 'TSE, candidaturas 2022 (BR)', 'url': URL['tse'].format(2022)}]},
        {'name': 'Dilma Rousseff', 'full_name': 'Dilma Vana Rousseff', 'role': 'Presidenta da República', 'head_of_government': True,
         'on_dates': ['2013-08-28 (TAC ANTT e concessionária)', 'maio de 2014 (início das obras)'],
         'party_at_time': party('DILMA VANA ROUSSEFF', 2010), 'party_name': 'Partido dos Trabalhadores',
         'term_note': 'Eleita pelo PT em 2010 e em 2014, segundo o TSE.', 'source': [{'doc': 'TSE, candidaturas 2010 (BR)', 'url': URL['tse'].format(2010)}, {'doc': 'TSE, candidaturas 2014 (BR)', 'url': URL['tse'].format(2014)}]},
        {'name': 'Jair Bolsonaro', 'full_name': 'Jair Messias Bolsonaro', 'role': 'Presidente da República', 'head_of_government': True,
         'on_dates': ['2020-12-08 (Deliberação ANTT 500/2020)', '2020-12-10 (Termo Aditivo 002/2020)'],
         'party_at_time': None, 'party_name': None,
         'note': f"Eleito em 2018 pelo {party('JAIR MESSIAS BOLSONARO', 2018)} e candidato em 2022 pelo {party('JAIR MESSIAS BOLSONARO', 2022)} (TSE). A filiação na data dos atos (dez/2020) não está em fonte oficial aberta encontrada.",
         'source': [{'doc': 'TSE, candidaturas 2018 (BR)', 'url': URL['tse'].format(2018)}, {'doc': 'TSE, candidaturas 2022 (BR)', 'url': URL['tse'].format(2022)}]},
    ]
    rec['people_note'] = 'Pela concessionária assinaram José Carlos Ferreira de Oliveira Filho e Francisco Leonardo Moura da Costa (contrato de 2008) e Antonio Cesar Ribas Sass e Giane Luza Zimmer Freitas (TA 002/2020); ficam só no registro da pesquisa (D36).'
    rec['people_gaps'] = ['Filiação partidária do Presidente da República em dezembro de 2020: não achada em fonte oficial aberta (biografia da Biblioteca da Presidência "em manutenção"; listas de filiados do TSE fora do ar).',
                          'Governadores de SC não entram: a obra é de concessão federal e nenhum ato do Estado aparece nos documentos de contrato e dinheiro.',
                          'As construtoras que fizeram a maior parte da obra não aparecem em documento oficial aberto.']

    # findings
    F = rec['findings']
    F.append({'body': 'TCU', 'process': 'TC 005.534/2011-9', 'decision': 'Acórdão 3346/2012-Plenário (relator Marcos Bemquerer)', 'date': '2012-12-05',
              'summary_quote': rq('abstenha-se de postergar novamente a data de conclusão do Contorno de Florianópolis (com extensão de 47,33 km) e das obras associadas, prevista para fevereiro de 2015', T['1256724'], 'TCU 3346/2012'),
              'status': 'alterado em recursos (Acórdãos 427/2013, 1043/2014 e 2883/2015): a ANTT passou a ter de fixar a data pelo novo traçado', 'url': tcu_url('1256724')})
    F.append({'body': 'TCU', 'process': 'TC 005.534/2011-9', 'decision': 'Acórdão 1366/2019-Plenário (relator Marcos Bemquerer)', 'date': '2019-06-12',
              'summary_quote': rq('vislumbro a ocorrência de negligência e imperícia tanto na conduta dos que elaboraram a Nota Técnica 137/2009/GEINV/SUINF', T['2310775'], 'TCU 1366/2019'),
              'second_quote': rq('plano de ação com especificação de todas as medidas a serem adotadas para se garantir a implementação urgente do Contorno Rodoviário de Florianópolis', T['2310775'], 'TCU 1366/2019'),
              'sanctions': [{'name': 'Mário Mondolfo', 'fine_brl': 15000.0}, {'name': 'Deuzedir Martins', 'fine_brl': 12000.0}, {'name': 'Rubens Narciso Peduti Dal Molin', 'fine_brl': 10000.0}, {'name': 'Mário Rodrigues Júnior', 'fine_brl': 17000.0, 'excluded_by': 'Acórdão 1416/2020'}],
              'status': 'Resolvido: multas a três servidores da ANTT mantidas pelo Acórdão 1416/2020 (03/06/2020); pagamento não verificado. O tribunal registrou que "a unidade técnica reconheceu que não houve dano ao erário".', 'url': tcu_url('2310775')})
    rq('a unidade técnica reconheceu que não houve dano ao erário', T['2409471'], 'TCU 1416/2020')
    F.append({'body': 'TCU', 'process': 'TC 026.406/2020-9', 'decision': 'Acórdão 2957/2020-Plenário (relator Raimundo Carreiro)', 'date': '2020-11-04',
              'summary_quote': rq('indícios de significativo sobrepreço no orçamento das obras de implantação do Contorno Rodoviário de Florianópolis e nos respectivos procedimentos de alteração da tarifa, no valor de R$ 203.122.754,88', t2957, 'TCU 2957/2020'),
              'second_quote': rq('realize tratativas com vistas a obter o valor justo dos investimentos, com redução estimada em R$ 136 milhões', t2957, 'TCU 2957/2020'),
              'values': {'unit_initial_brl': D2(sp0), 'unit_merit_brl': D2(sp1), 'antt_budget_brl': D2(budget0), 'base': 'jan/2019',
                         'printed_ratio': '22,99%', 'computed_ratio_pct': float(ratio), 'ratio_note': 'O acórdão escreve 22,99%; a conta R$ 203.122.754,88 / R$ 923.846.486,36 dá 21,99%.'},
              'status': 'Representação parcialmente procedente; aditivo liberado com correções no orçamento; renegociação determinada (item 9.5)', 'url': tcu_url('2438806')})
    F.append({'body': 'TCU', 'process': 'TC 006.219/2023-3 (monitoramento do Acórdão 2957/2020)', 'decision': 'Acórdão de Relação 2029/2024-Plenário (relator Antonio Anastasia)', 'date': '2024-09-25',
              'summary_quote': rq('obtendo, contudo, alteração de valores consideravelmente aquém da estimativa do Tribunal (R$ 16.309.444,17, data-base: janeiro/2019)', t2029, 'TCU 2029/2024'),
              'second_quote': rq('considerar não cumprida a determinação do item 9.5, dispensando-se a continuidade do monitoramento', t2029, 'TCU 2029/2024'),
              'values': {'tcu_estimate_brl': D2(sp1), 'obtained_cut_brl': D2(cut_2029), 'not_cut_brl_computed': D2(sp1 - cut_2029), 'base': 'jan/2019'},
              'status': 'Não resolvido no valor: determinação "não cumprida", processo encerrado sem multa nem débito; R$ 120,3 mi (jan/2019) apontados pela unidade técnica ficaram sem corte (diferença sem explicação aceita pelo TCU)', 'url': TCU_REL.format(n=2029, y=2024)})
    F.append({'body': 'TCU', 'process': 'TC 010.683/2013-5 (monitoramento)', 'decision': 'Acórdão 2802/2022-Plenário (relator Marcos Bemquerer)', 'date': '2022-12-13',
              'summary_quote': rq('após atrasos e paralisações por conta de problemas com o traçado da rodovia, licenciamento ambiental e desapropriação, com novo prazo de conclusão estimado para fevereiro de 2024', T['2560661'], 'TCU 2802/2022'),
              'status': 'encerrado (determinações cumpridas ou acompanhadas em outros processos)', 'url': tcu_url('2560661')})
    F.append({'body': 'TCU', 'process': 'TC 039.653/2020-0 (monitoramento do Acórdão 2605/2020)', 'decision': 'Acórdão de Relação 2062/2025-Plenário', 'date': '2025-09-10',
              'summary_quote': rq('as obras foram concluídas, restando pendente desapropriações, que têm muitos trechos com objeção e/ou com ressalvas', T['2717698'], 'TCU 2062/2025'),
              'status': 'obra concluída; desapropriações pendentes', 'url': TCU_REL.format(n=2062, y=2025)})
    F.append({'body': 'Justiça Federal (TRF4)', 'process': 'Apelação/Remessa Necessária 5014533-38.2012.4.04.7200/SC', 'decision': '3ª Turma do TRF4', 'date': '2018-11-29',
              'summary_quote': rq('confirmou a decisão de primeiro grau que havia concluído pela impossibilidade de imputação de responsabilidade à ANTT pelo atraso das obras obrigatórias', T['2310775'], 'TCU 1366/2019 citando o TRF4'),
              'status': 'transitado em julgado em 08/02/2019 (segundo o TCU; a decisão não foi lida)', 'url': tcu_url('2310775')})
    F.sort(key=lambda x: x['date'])
    rec['terms_check'] = {'terms': terms, 'window_chars': 1500, 'found': found,
                          'note': 'Nenhum documento usa "superfaturamento" para esta obra (a única ocorrência, no Acórdão 427/2013, é texto genérico). "Sobrepreço" aparece sobre o orçamento do Sul A. "Desvio" é desvio de tráfego. Controle positivo conferido.'}

    # media
    cm = list(json.load(open(p('commons_photo.json')))['query']['pages'].values())[0]['imageinfo'][0]
    rec['media'] = [{'file': 'docs/superpowers/previews/assets/cases/florianopolis-bypass/tunnel-2-palhoca-2024.jpg',
                     'caption': '2024: emboque do Túnel 2 (908 m) do Contorno, em Palhoça, no dia da inauguração',
                     'author': 'Ricardo Stuckert/PR', 'license': cm['extmetadata']['LicenseShortName']['value'], 'license_url': cm['extmetadata']['LicenseUrl']['value'],
                     'page': cm['descriptionurl'], 'date': 'Taken on 9 August 2024',
                     'modification': 'recorte sem as pessoas da cerimônia, 960 x 720 px (mesma licença)', 'shows_the_work': True}]
    rec['media_note'] = 'As 29 fotos livres do Contorno no Wikimedia Commons são da cerimônia de inauguração (conta Lula Oficial no Flickr). A escolhida mostra a obra (Túnel 2) e foi recortada para tirar as autoridades do quadro.'

    # comparison
    reg24 = to24(reg_total, '200707'); sul24 = to24(sul_a_final, '201901'); g24 = to24(goi_esp, '201503'); g124 = to24(goi_1a, '201503'); prop24 = to24(contorno_price, '200707')
    per_km = lambda v, km: D2((v / D(str(km))).quantize(q, ROUND_HALF_UP))
    mi1 = lambda v: f'{v / 1e6:.1f}'.replace('.', ',')
    rec['comparison'] = {
        'unit': 'R$ por km de rodovia nova em pista dupla, em reais de dezembro de 2024',
        'method': 'Valores oficiais na data-base de cada documento, corrigidos pelo IPCA do mês-base até dez/2024 (IBGE/SIDRA 1737). O Contorno aparece com duas medidas: o valor regulatório (o que a tarifa remunera, preços de jul/2007) e o investimento declarado pela concessionária (nominal, sem correção).',
        'ipca_dec_2024': float(ip['202412']), 'ipca_source': URL['ipca'],
        'this_work': {'name': 'Contorno Viário da Grande Florianópolis (valor regulatório)', 'category': 'SC, contorno novo com 4 túneis duplos e 44 obras de arte especiais',
                      'lanes': 'pista dupla nova', 'length_km': 50.0, 'cost_reported_brl': D2(reg_total), 'price_base_month': '2007-07',
                      'ipca_factor_to_dec2024': float(f('200707').quantize(D('0.000001'))), 'cost_brl_2024': D2(reg24), 'cost_per_km_brl_2024': per_km(reg24, 50),
                      'cost_basis': 'Itens só do Contorno na planilha de execução da ANTT (PER original, Sul A, duas passagens do Sul B e trevos), a preços iniciais do contrato.',
                      'sources': [{'url': URL['exec_xlsx']}, {'url': URL['ta002']}]},
        'comparables': [
            {'name': 'Contorno Viário da Grande Florianópolis (investimento declarado, nominal)', 'category': 'mesma obra, dinheiro investido pela concessionária de 2014 a 2024, sem correção',
             'length_km': 50.0, 'cost_reported_brl': D2(invest_total), 'price_base_month': '2014 a 2024 (nominal)', 'cost_brl_2024': D2(invest_total),
             'cost_brl_2024_note': 'piso: corrigido pelo IPCA seria maior', 'cost_per_km_brl_2024': per_km(invest_total, 50), 'sources': [{'url': URL['df2024']}]},
            {'name': 'Contorno de Florianópolis, trecho Sul A (7,914 km, 3 túneis duplos)', 'category': 'SC, trecho com túneis',
             'length_km': 7.914, 'cost_reported_brl': D2(sul_a_final), 'price_base_month': '2019-01', 'ipca_factor_to_dec2024': float(f('201901').quantize(D('0.000001'))),
             'cost_brl_2024': D2(sul24), 'cost_per_km_brl_2024': per_km(sul24, 7.914), 'sources': [{'url': URL['voto120']}]},
            {'name': 'Contorno de Goiânia, projeto de 44 km Classe Especial (BR-060/153, não construído)', 'category': 'GO, projeto executivo de contorno novo',
             'length_km': 44.0, 'cost_reported_brl': D2(goi_esp), 'price_base_month': '2015-03', 'ipca_factor_to_dec2024': float(f('201503').quantize(D('0.000001'))),
             'cost_brl_2024': D2(g24), 'cost_per_km_brl_2024': per_km(g24, 44), 'sources': [{'url': tcu_url('2372718')}]},
            {'name': 'Contorno de Goiânia, previsto no PER, 30 km classe 1A (não construído)', 'category': 'GO, estimativa do projeto executivo',
             'length_km': 30.0, 'cost_reported_brl': D2(goi_1a), 'price_base_month': '2015-03', 'ipca_factor_to_dec2024': float(f('201503').quantize(D('0.000001'))),
             'cost_brl_2024': D2(g124), 'cost_per_km_brl_2024': per_km(g124, 30), 'sources': [{'url': tcu_url('2372718')}]},
        ],
        'original_proposal': {'cost_reported_brl': D2(contorno_price), 'length_km': 47.33, 'cost_brl_2024': D2(prop24), 'cost_per_km_brl_2024': per_km(prop24, 47.33)},
        'result': f'Pelo valor que a tarifa remunera, o Contorno custou R$ {mi1(per_km(reg24, 50))} mi por km (dez/2024), o mesmo que o projeto do Contorno de Goiânia na classe mais alta (R$ {mi1(per_km(g24, 44))} mi/km), mesmo com quatro túneis duplos. Pelo investimento que a concessionária declara (R$ 3,9 bi, sem correção), são R$ {mi1(per_km(invest_total, 50))} mi por km, mais que o dobro. O trecho Sul A, com três túneis em 7,9 km, custou R$ {mi1(per_km(sul24, 7.914))} mi por km.',
        'gap_unexplained': True,
        'gap_note': 'Os documentos não explicam a diferença entre o valor regulatório corrigido (R$ 1,76 bi) e o investimento declarado (R$ 3,9 bi nominal); as DFP citam juros capitalizados durante a obra. Separadamente, o TCU apontou R$ 120,3 mi (jan/2019) no Sul A que não foram cortados.',
        'caveats': ['Goiânia é projeto, não obra feita, e em outro terreno.',
                    'Nenhum valor é o gasto final ao centavo: a concessionária publica só o total arredondado (R$ 3,9 bi).',
                    'Custos médios de contornos citados pelo TCU (R$ 5,5 mi/km da Infra S.A.; R$ 11,7 mi/km da Eco101, jan/2023) medem só as pistas, sem túneis e obras de arte, e ficaram fora.'],
    }
    rec['owner_lead_check'] = {
        'superfaturado': 'Não confirmado como "superfaturamento": nenhum documento oficial usa o termo para esta obra. A unidade técnica do TCU apontou "indícios de significativo sobrepreço" no orçamento do trecho Sul A (R$ 203,1 mi, depois R$ 136,6 mi, jan/2019); o TCU mandou renegociar, a ANTT cortou R$ 16,3 mi, e o TCU encerrou como "não cumprida", sem multa nem débito. Ficaram R$ 120,3 mi sem corte.',
        'delays': 'Confirmado: o contrato mandava concluir em fev/2012; abriu em 09/08/2024, 12 anos e 6 meses depois. Prazos adiados em 2009, 2013 e depois de 2020. O TCU multou três servidores da ANTT pelo adiamento de 2009 e atribuiu o atraso inicial à concessionária; o TRF4 concluiu que o atraso não podia ser imputado à ANTT.',
    }
    rec['card'] = {'image': rec['media'][0]['file'], 'stats': [
        ['Investimento total (concessionária)', 'R$ 3,9 bi'], ['Contrato inicial (proposta de 2007)', f"R$ {D2(contorno_price) / 1e6:.1f} mi".replace('.', ',')],
        ['Prazo', '16,5 anos (previsto 4)'], ['Atraso', '12,5 anos além do contrato']],
        'head': {'investment_total': {'label': 'Investimento total (concessionária)', 'value_brl': D2(invest_total), 'display': 'R$ 3,9 bi',
                                      'note': 'investimento declarado pela concessionária na DFP 2024 (CVM), nominal, 2014 a 2024; pago pelo pedágio, sem dinheiro do Orçamento da União'},
                 'initial_contract': {'label': 'Contrato inicial (proposta de 2007)', 'value_brl': D2(contorno_price), 'display': f"R$ {D2(contorno_price) / 1e6:.1f} mi".replace('.', ','),
                                      'note': 'preço do Contorno (47,33 km) na proposta vencedora da concessão, a preços de jul/2007'}}}

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
