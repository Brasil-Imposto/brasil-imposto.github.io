#!/usr/bin/env python3
"""Collects 2026 pay data of the federal Executive's top officeholders from official open data.

Stage `fetch`: downloads the Portal da Transparencia monthly files (servidores SIAPE, Honorarios Jetons, CPGF) one at a
time, keeps only the rows needed and deletes each zip. Resumable: a month already filtered is skipped.
Stage `build`: writes data/federal/executive-2026.json from the filtered files plus the people sheet in this script.
"""
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW = os.path.join(ROOT, 'data', 'federal', 'raw-pay', 'executive')
FILT = os.path.join(RAW, 'filtered')
MONTHS = [f'2026{m:02d}' for m in range(1, 9)]
PORTAL = 'https://portaldatransparencia.gov.br/download-de-dados/'
TOP_CARGOS = {'MINISTRO DE ESTADO', 'PRESIDENTE DA REPUBLICA', 'VICE-PRESIDENTE DA REPUBLICA'}
UA = 'Mozilla/5.0'
PAUSE = 75

PLANALTO_LIST = 'https://www.gov.br/planalto/pt-br/conheca-a-presidencia/ministros-e-ministras'
# (siape_id, position, name as on the Planalto list, role as on the Planalto list, ministry, common name for Wikidata search)
PEOPLE = [
    ('3116237', 'presidente', 'Luiz Inácio Lula da Silva', 'Presidente da República', 'Presidência da República', None),
    ('559168', 'vice', 'Geraldo José Rodrigues Alckmin Filho', 'Vice-Presidente da República', 'Vice-Presidência da República', None),
    ('2009207', 'ministros', 'Miriam Belchior', 'Ministra de Estado da Casa Civil da Presidência da República', 'Casa Civil da Presidência da República', 'Miriam Belchior'),
    ('4154185', 'ministros', 'Guilherme Castro Boulos', 'Ministro de Estado da Secretaria-Geral da Presidência da República', 'Secretaria-Geral da Presidência da República', 'Guilherme Boulos'),
    ('4253827', 'ministros', 'José Nobre Guimarães', 'Ministro de Estado da Secretaria de Relações Institucionais da Presidência da República', 'Secretaria de Relações Institucionais da Presidência da República', 'José Guimarães'),
    ('4000583', 'ministros', 'Sidônio Palmeira', 'Ministro de Estado da Secretaria de Comunicação Social da Presidência da República', 'Secretaria de Comunicação Social da Presidência da República', 'Sidônio Palmeira'),
    ('2318094', 'ministros', 'Marcos Antonio Amaro dos Santos', 'Ministro de Estado Chefe do Gabinete de Segurança Institucional da Presidência da República', 'Gabinete de Segurança Institucional da Presidência da República', 'Marcos Antonio Amaro dos Santos'),
    ('3741863', 'ministros', 'Jorge Rodrigo Araújo Messias', 'Advogado-Geral da União', 'Advocacia-Geral da União', 'Jorge Messias'),
    ('1078915', 'ministros', 'Vinícius Marques de Carvalho', 'Ministro de Estado da Controladoria-Geral da União', 'Controladoria-Geral da União', 'Vinícius Marques de Carvalho'),
    ('1810792', 'ministros', 'André Carlos Alves de Paula Filho', 'Ministro de Estado da Agricultura e Pecuária', 'Ministério da Agricultura e Pecuária', 'André de Paula'),
    ('2275732', 'ministros', 'Antonio Vladimir Moura Lima', 'Ministro de Estado das Cidades', 'Ministério das Cidades', 'Vladimir Lima'),
    ('1570631', 'ministros', 'Luciana Barbosa de Oliveira Santos', 'Ministra de Estado da Ciência, Tecnologia e Inovação', 'Ministério da Ciência, Tecnologia e Inovação', 'Luciana Santos'),
    ('3447356', 'ministros', 'Frederico de Siqueira Filho', 'Ministro de Estado das Comunicações', 'Ministério das Comunicações', 'Frederico de Siqueira Filho'),
    ('3659914', 'ministros', 'Margareth Menezes da Purificação Costa', 'Ministra de Estado da Cultura', 'Ministério da Cultura', 'Margareth Menezes'),
    ('2415765', 'ministros', 'José Mucio Monteiro Filho', 'Ministro de Estado da Defesa', 'Ministério da Defesa', 'José Múcio'),
    ('1123135', 'ministros', 'Fernanda Machiaveli Morão de Oliveira', 'Ministra de Estado do Desenvolvimento Agrário e Agricultura Familiar', 'Ministério do Desenvolvimento Agrário e Agricultura Familiar', 'Fernanda Machiaveli'),
    ('3035730', 'ministros', 'José Wellington Barroso de Araujo Dias', 'Ministro de Estado do Desenvolvimento e Assistência Social, Família e Combate à Fome', 'Ministério do Desenvolvimento e Assistência Social, Família e Combate à Fome', 'Wellington Dias'),
    ('791886', 'ministros', 'Márcio Fernando Elias Rosa', 'Ministro de Estado do Desenvolvimento, Indústria, Comércio e Serviços', 'Ministério do Desenvolvimento, Indústria, Comércio e Serviços', 'Márcio Elias Rosa'),
    ('1079045', 'ministros', 'Janine Mello dos Santos', 'Ministra de Estado dos Direitos Humanos e da Cidadania', 'Ministério dos Direitos Humanos e da Cidadania', 'Janine Mello'),
    ('1506628', 'ministros', 'Leonardo Osvaldo Barchini Rosa', 'Ministro de Estado da Educação', 'Ministério da Educação', 'Leonardo Barchini'),
    ('3317179', 'ministros', 'Paulo Henrique Rodrigues Pereira', 'Ministro de Estado do Empreendedorismo, da Microempresa e da Empresa de Pequeno Porte', 'Ministério do Empreendedorismo, da Microempresa e da Empresa de Pequeno Porte', None),
    ('3699144', 'ministros', 'Paulo Henrique Perna Cordeiro', 'Ministro de Estado do Esporte', 'Ministério do Esporte', None),
    ('96103', 'ministros', 'Dario Carnevalli Durigan', 'Ministro de Estado da Fazenda', 'Ministério da Fazenda', 'Dario Durigan'),
    ('3534935', 'ministros', 'Esther Dweck', 'Ministra de Estado da Gestão e da Inovação em Serviços Públicos', 'Ministério da Gestão e da Inovação em Serviços Públicos', 'Esther Dweck'),
    ('3660362', 'ministros', 'Rachel Barros de Oliveira', 'Ministra de Estado da Igualdade Racial', 'Ministério da Igualdade Racial', None),
    ('1547434', 'ministros', 'Antônio Waldez Góes da Silva', 'Ministro de Estado da Integração e do Desenvolvimento Regional', 'Ministério da Integração e do Desenvolvimento Regional', 'Waldez Góes'),
    ('2961013', 'ministros', 'Wellington César Lima e Silva', 'Ministro de Estado da Justiça e Segurança Pública', 'Ministério da Justiça e Segurança Pública', 'Wellington César Lima e Silva'),
    ('1198450', 'ministros', 'João Paulo Ribeiro Capobianco', 'Ministro de Estado do Meio Ambiente e Mudança do Clima', 'Ministério do Meio Ambiente e Mudança do Clima', 'João Paulo Capobianco'),
    ('688218', 'ministros', 'Alexandre Silveira de Oliveira', 'Ministro de Estado de Minas e Energia', 'Ministério de Minas e Energia', 'Alexandre Silveira'),
    ('797817', 'ministros', 'Márcia Helena Carvalho Lopes', 'Ministra de Estado das Mulheres', 'Ministério das Mulheres', 'Márcia Lopes'),
    ('1096103', 'ministros', 'Rivetla Edipo Araujo Cruz', 'Ministro de Estado da Pesca e Aquicultura', 'Ministério da Pesca e Aquicultura', None),
    ('299246', 'ministros', 'Bruno Moretti', 'Ministro de Estado do Planejamento e Orçamento', 'Ministério do Planejamento e Orçamento', 'Bruno Moretti'),
    ('3854511', 'ministros', 'Tomé Monteiro da Franca', 'Ministro de Estado de Portos e Aeroportos', 'Ministério de Portos e Aeroportos', 'Tomé Franca'),
    ('1965666', 'ministros', 'Luiz Henrique Eloy Amado', 'Ministro de Estado dos Povos Indígenas', 'Ministério dos Povos Indígenas', 'Luiz Eloy Terena'),
    ('526346', 'ministros', 'Wolney Queiroz Maciel', 'Ministro de Estado da Previdência Social', 'Ministério da Previdência Social', 'Wolney Queiroz'),
    ('404488', 'ministros', 'Mauro Luiz Iecker Vieira', 'Ministro de Estado das Relações Exteriores', 'Ministério das Relações Exteriores', 'Mauro Vieira'),
    ('2458750', 'ministros', 'Alexandre Rocha Santos Padilha', 'Ministro de Estado da Saúde', 'Ministério da Saúde', 'Alexandre Padilha'),
    ('1041155', 'ministros', 'Luiz Marinho', 'Ministro de Estado do Trabalho e Emprego', 'Ministério do Trabalho e Emprego', 'Luiz Marinho'),
    ('767332', 'ministros', 'George Santoro', 'Ministro de Estado dos Transportes', 'Ministério dos Transportes', 'George Santoro'),
    ('4162993', 'ministros', 'Gustavo Costa Feliciano', 'Ministro de Estado do Turismo', 'Ministério do Turismo', 'Gustavo Feliciano'),
]


def log(msg):
    line = time.strftime('%H:%M:%S ') + msg
    print(line, flush=True)
    with open(os.path.join(RAW, 'fetch.log'), 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def load_manifest():
    p = os.path.join(FILT, 'manifest.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def save_manifest(m):
    tmp = os.path.join(FILT, 'manifest.json.tmp')
    json.dump(m, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(FILT, 'manifest.json'))


def download(url, dest, tries=6):
    wait = 90
    for i in range(tries):
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                data = r.read()
                final = r.geturl()
                last_modified = r.headers.get('Last-Modified')
            if data[:2] == b'PK':
                with open(dest, 'wb') as f:
                    f.write(data)
                return {'url': url, 'final_url': final, 'last_modified': last_modified, 'bytes': len(data),
                        'sha256': hashlib.sha256(data).hexdigest(), 'read_on': time.strftime('%Y-%m-%d')}
            log(f'not a zip from {url} (try {i + 1}), waiting {wait}s')
        except Exception as e:  # network errors and WAF refusals are retried
            log(f'error {e!r} on {url} (try {i + 1}), waiting {wait}s')
        time.sleep(wait)
        wait *= 2
    raise SystemExit(f'gave up on {url}')


def member(z, part):
    names = [n for n in z.namelist() if part in n]
    assert len(names) == 1, (part, z.namelist())
    return io.TextIOWrapper(z.open(names[0]), encoding='latin-1', newline='')


def write_rows(path, header, rows):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(header)
        w.writerows(rows)


def filter_siape(zpath, ym):
    z = zipfile.ZipFile(zpath)
    ids = set()
    r = csv.reader(member(z, 'Cadastro'), delimiter=';')
    header = next(r)
    for row in r:
        if row[4].strip().upper() in TOP_CARGOS:
            ids.add(row[0])
    r = csv.reader(member(z, 'Cadastro'), delimiter=';')
    next(r)
    cad = [row for row in r if row[0] in ids]
    write_rows(os.path.join(FILT, f'siape-{ym}-cadastro.csv'), header, cad)
    r = csv.reader(member(z, 'Remuneracao'), delimiter=';')
    rheader = next(r)
    rem = [row for row in r if row[2] in ids]
    write_rows(os.path.join(FILT, f'siape-{ym}-remuneracao.csv'), rheader, rem)
    r = csv.reader(member(z, 'Observacoes'), delimiter=';')
    oheader = next(r)
    obs = [row for row in r if len(row) > 2 and row[2] in ids]
    write_rows(os.path.join(FILT, f'siape-{ym}-observacoes.csv'), oheader, obs)
    return {'ids': len(ids), 'cadastro_rows': len(cad), 'remuneracao_rows': len(rem), 'observacoes_rows': len(obs)}


def filter_jetons(zpath, ym):
    z = zipfile.ZipFile(zpath)
    rows = list(csv.reader(member(z, 'Jetons'), delimiter=';'))
    write_rows(os.path.join(FILT, f'jetons-{ym}.csv'), rows[0], rows[1:])
    return {'rows': len(rows) - 1}


def filter_cpgf(zpath, ym):
    z = zipfile.ZipFile(zpath)
    r = csv.reader(member(z, 'CPGF'), delimiter=';')
    header = next(r)
    col = [i for i, h in enumerate(header) if 'DIGO' in h.upper() and 'SUPERIOR' in h.upper()]
    assert len(col) == 1, header
    rows = [row for row in r if row[col[0]].strip() == '20000']
    write_rows(os.path.join(FILT, f'cpgf-{ym}-presidencia.csv'), header, rows)
    return {'rows_presidencia': len(rows)}


def fetch():
    os.makedirs(FILT, exist_ok=True)
    manifest = load_manifest()
    jobs = []
    for ym in MONTHS:
        jobs.append((f'siape-{ym}', PORTAL + f'servidores/{ym}_Servidores_SIAPE', filter_siape, ym))
        jobs.append((f'jetons-{ym}', PORTAL + f'servidores/{ym}_Honorarios_Jetons', filter_jetons, ym))
        jobs.append((f'cpgf-{ym}', PORTAL + f'cpgf/{ym}', filter_cpgf, ym))
    first = True
    for key, url, fn, ym in jobs:
        if key in manifest and manifest[key].get('filtered'):
            continue
        zpath = os.path.join(RAW, key + '.zip')
        if os.path.exists(zpath) and zipfile.is_zipfile(zpath) and key in manifest:
            info = manifest[key]
        else:
            if not first:
                time.sleep(PAUSE)
            first = False
            log(f'downloading {key}')
            info = download(url, zpath)
            manifest[key] = info
            save_manifest(manifest)
        info['filtered'] = fn(zpath, ym)
        manifest[key] = info
        save_manifest(manifest)
        os.remove(zpath)
        log(f'{key} done: {info["filtered"]}')
    log('fetch complete')


def get_json(url):
    import urllib.error
    wait = 10
    for _ in range(6):
        req = urllib.request.Request(url, headers={'User-Agent': 'BrasilImposto/0.1 (civic open data; contact via project)', 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            ra = e.headers.get('Retry-After')
            time.sleep(int(ra) if ra and ra.isdigit() else wait)
            wait *= 2
    raise RuntimeError(f'rate limited: {url}')


def lookup():
    """Official parliamentary status (Camara and Senado open data) and Wikimedia Commons portraits."""
    from urllib.parse import quote
    out = {'camara': {}, 'senado_afastados': None, 'photos': {}}
    for _, _, name, _, _, common in PEOPLE:
        q = common or name
        url = f'https://dadosabertos.camara.leg.br/api/v2/deputados?nome={quote(q)}&idLegislatura=57'
        try:
            dados = get_json(url)['dados']
        except Exception as e:
            dados = []
            log(f'camara search failed for {q}: {e!r}')
        for d in dados:
            det_url = f'https://dadosabertos.camara.leg.br/api/v2/deputados/{d["id"]}'
            det = get_json(det_url)['dados']
            out['camara'].setdefault(name, []).append({'search_url': url, 'url': det_url, 'nome_civil': det.get('nomeCivil'),
                                                       'ultimo_status': det.get('ultimoStatus')})
        time.sleep(0.4)
    sen_url = 'https://legis.senado.leg.br/dadosabertos/senador/afastados.json'
    try:
        out['senado_afastados'] = {'url': sen_url, 'data': get_json(sen_url)}
    except Exception as e:
        log(f'senado afastados failed: {e!r}')
    api = 'https://www.wikidata.org/w/api.php?format=json&'
    for _, _, name, _, _, common in PEOPLE:
        hits = []
        for q in [x for x in (common, name) if x]:
            res = get_json(api + f'action=wbsearchentities&language=pt&uselang=pt&type=item&limit=5&search={quote(q)}')
            hits += [h for h in res.get('search', []) if h['id'] not in [x['id'] for x in hits]]
            time.sleep(1.5)
        cands = []
        if hits:
            ents = get_json(api + 'action=wbgetentities&props=claims|descriptions|labels&languages=pt|en&ids=' + '|'.join(h['id'] for h in hits))['entities']
            for qid, e in ents.items():
                claims = e.get('claims', {})
                citizen = [c['mainsnak'].get('datavalue', {}).get('value', {}).get('id') for c in claims.get('P27', [])]
                p18 = [c['mainsnak'].get('datavalue', {}).get('value') for c in claims.get('P18', [])]
                cands.append({'qid': qid, 'label': e.get('labels', {}).get('pt', {}).get('value'),
                              'description': e.get('descriptions', {}).get('pt', {}).get('value'),
                              'brazilian': 'Q155' in citizen, 'p18': p18})
        chosen = [c for c in cands if c['brazilian'] and c['p18']]
        rec = {'candidates': cands}
        if chosen:
            f = chosen[0]['p18'][0]
            info = get_json('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=500&titles=' + quote('File:' + f))
            page = next(iter(info['query']['pages'].values()))
            ii = page.get('imageinfo', [{}])[0]
            meta = ii.get('extmetadata', {})
            rec.update({'qid': chosen[0]['qid'], 'file': f, 'thumb': ii.get('thumburl'), 'original': ii.get('url'),
                        'file_page': ii.get('descriptionurl'),
                        'artist': meta.get('Artist', {}).get('value'), 'credit': meta.get('Credit', {}).get('value'),
                        'license': meta.get('LicenseShortName', {}).get('value'), 'date': meta.get('DateTimeOriginal', {}).get('value')})
        out['photos'][name] = rec
        time.sleep(1.5)
    json.dump(out, open(os.path.join(RAW, 'lookup.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log('lookup complete')


TODAY = '2026-10-21'
OFFICIAL_AUTHORS = ('Palácio do Planalto', 'Agência Senado', 'Câmara dos Deputados', 'Agência Brasil', 'ABr', 'Ministério',
                    'Lula Oficial', 'Superior Tribunal de Justiça', 'Ricardo Stuckert')
NOT_FOUND_FIXED = [
    {'what': 'Remuneração, jetons e cartão de setembro e outubro de 2026',
     'why': 'O Portal da Transparência publica até agosto de 2026 (arquivos 202608 gerados em 08 e 09/10/2026; CPGF 202608 em 17/09/2026).',
     'tried': ['https://portaldatransparencia.gov.br/download-de-dados/servidores', 'https://portaldatransparencia.gov.br/download-de-dados/cpgf']},
    {'what': 'Auxílio-moradia recebido por cada ministro',
     'why': 'O arquivo de remuneração do SIAPE soma todas as verbas indenizatórias num total só; a página de cada servidor no Portal pede verificação humana (HTTP 405) e não foi lida.',
     'tried': ['https://portaldatransparencia.gov.br/download-de-dados/servidores/202608_Servidores_SIAPE', 'https://portaldatransparencia.gov.br/servidores/3116237']},
    {'what': 'Valor em reais das residências oficiais (Alvorada e Jaburu) e dos imóveis funcionais',
     'why': 'As páginas do Planalto descrevem os palácios como residências oficiais, sem valor em reais; nenhum valor de uso de imóvel funcional por pessoa é publicado.',
     'tried': ['https://www.gov.br/planalto/pt-br/conheca-a-presidencia/palacios-e-residencias/palacio-da-alvorada', 'https://www.gov.br/planalto/pt-br/conheca-a-presidencia/palacios-e-residencias/palacio-jaburu']},
    {'what': 'Remuneração dos ministros que são deputados ou senadores licenciados e não têm linha no SIAPE',
     'why': 'O arquivo do SIAPE não traz pagamento para eles; se optaram pela remuneração do mandato (CF art. 56 § 3º), ela é paga pela Câmara ou pelo Senado e não foi coletada aqui.',
     'tried': ['https://portaldatransparencia.gov.br/download-de-dados/servidores/202608_Servidores_SIAPE']},
    {'what': 'Natureza das "outras remunerações eventuais" (muitos ministros com R$ 11.500,00 ou R$ 11.591,55 por mês)',
     'why': 'O arquivo só dá o total da coluna; não está no arquivo de jetons para as mesmas pessoas; o arquivo de observações não explica.',
     'tried': ['https://portaldatransparencia.gov.br/download-de-dados/servidores/202608_Servidores_SIAPE', 'https://portaldatransparencia.gov.br/download-de-dados/servidores/202608_Honorarios_Jetons']},
]
MONTH_PT = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
DL172 = 'https://www2.camara.leg.br/legin/fed/decleg/2022/decretolegislativo-172-21-dezembro-2022-793529-publicacaooriginal-166604-pl.html'
L8112 = 'https://www.planalto.gov.br/ccivil_03/leis/l8112cons.htm'
L9292 = 'https://www.planalto.gov.br/ccivil_03/leis/l9292.htm'
L13303 = 'https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/lei/l13303.htm'
CF = 'https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm'
ALVORADA = 'https://www.gov.br/planalto/pt-br/conheca-a-presidencia/palacios-e-residencias/palacio-da-alvorada'
JABURU = 'https://www.gov.br/planalto/pt-br/conheca-a-presidencia/palacios-e-residencias/palacio-jaburu'
SALARY = 46366.19
BIO_PRESIDENT = 'https://www.gov.br/planalto/pt-br/conheca-a-presidencia/biografia-do-presidente'
BIO_VICE = 'https://www.gov.br/planalto/pt-br/vice-presidencia/acesso-a-informacao/institucional/biografia-do-vice-presidente-da-republica-1'
REM_COLS = {
    'salary': ('REMUNERAÇÃO BÁSICA BRUTA (R$)', 'Remuneração básica bruta (salário e, quando houver, o cargo de origem)'),
    'ceiling_cut': ('ABATE-TETO (R$)', 'Abate-teto (corte do que passa do teto constitucional)'),
    'christmas_bonus': ('GRATIFICAÇÃO NATALINA (R$)', 'Gratificação natalina (13º)'),
    'vacation': ('FÉRIAS (R$)', 'Férias (adicional de um terço)'),
    'other_pay': ('OUTRAS REMUNERAÇÕES EVENTUAIS (R$)', 'Outras remunerações eventuais (o arquivo não diz a natureza)'),
    'indemnities': ('TOTAL DE VERBAS INDENIZATÓRIAS (R$)(*)', 'Verbas indenizatórias (auxílios somados num total só; o arquivo não separa cada um)'),
    'functional_property_fee': ('TAXA DE OCUPAÇÃO IMÓVEL FUNCIONAL (R$)', 'Taxa de ocupação de imóvel funcional (desconto de quem mora em imóvel da União)'),
    'net_pay': ('REMUNERAÇÃO APÓS DEDUÇÕES OBRIGATÓRIAS (R$)', 'Remuneração líquida depois de imposto e previdência'),
}


def brl(v):
    return 'R$ ' + f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def num(s):
    s = (s or '').strip()
    if not s:
        return 0.0
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    return float(s)


def read_csv(path):
    if not os.path.exists(path):
        return None, []
    rows = list(csv.reader(open(path, encoding='utf-8', newline=''), delimiter=';'))
    return rows[0], rows[1:]


def norm(s):
    import re
    import unicodedata
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().upper()
    return re.sub(r'\s+', ' ', re.sub(r'[^A-Z ]', ' ', s)).strip()


def slug(s):
    return norm(s).lower().replace(' ', '-')


def months_label(ms):
    if not ms:
        return None
    a, b = min(ms), max(ms)
    if a == b:
        return f'{MONTH_PT[a - 1]} 2026'
    gaps = '' if len(ms) == b - a + 1 else ' (com meses sem pagamento)'
    return f'{MONTH_PT[a - 1]} a {MONTH_PT[b - 1]} 2026' + gaps


def portal_url(kind, ym):
    return {'siape': PORTAL + f'servidores/{ym}_Servidores_SIAPE', 'jetons': PORTAL + f'servidores/{ym}_Honorarios_Jetons',
            'cpgf': PORTAL + f'cpgf/{ym}'}[kind]


def build():
    import re
    manifest = load_manifest()
    lookup_data = json.load(open(os.path.join(RAW, 'lookup.json'), encoding='utf-8')) if os.path.exists(os.path.join(RAW, 'lookup.json')) else {}
    union = json.load(open(os.path.join(ROOT, 'data', 'politicians', 'union.json'), encoding='utf-8'))
    months = [ym for ym in MONTHS if manifest.get(f'siape-{ym}', {}).get('filtered')]
    last = months[-1]
    cad, rem, obs, jet = {}, {}, {}, {}
    for ym in months:
        m = int(ym[4:])
        h, rows = read_csv(os.path.join(FILT, f'siape-{ym}-cadastro.csv'))
        for r in rows:
            cad.setdefault(r[0], {}).setdefault(m, []).append(dict(zip(h, r)))
        h, rows = read_csv(os.path.join(FILT, f'siape-{ym}-remuneracao.csv'))
        for r in rows:
            rem.setdefault(r[2], {}).setdefault(m, []).append(dict(zip(h, r)))
        h, rows = read_csv(os.path.join(FILT, f'siape-{ym}-observacoes.csv'))
        for r in rows:
            obs.setdefault(r[2], set()).add(r[-1].strip().capitalize())
    jet_months = [ym for ym in MONTHS if manifest.get(f'jetons-{ym}', {}).get('filtered')]
    for ym in jet_months:
        h, rows = read_csv(os.path.join(FILT, f'jetons-{ym}.csv'))
        for r in rows:
            jet.setdefault(r[2], []).append({'month': int(ym[4:]), 'company': r[5].strip(), 'value': num(r[6]), 'name': r[4]})
    not_found = []
    people = []
    senators_away = (((lookup_data.get('senado_afastados') or {}).get('data') or {}).get('AfastamentoAtual', {})
                     .get('Parlamentares', {}).get('Parlamentar', []))
    for sid, position, name, role, ministry, common in PEOPLE:
        c_months = cad.get(sid, {})
        top_rows = [r for m in sorted(c_months) for r in c_months[m] if r['DESCRICAO_CARGO'].strip().upper() in TOP_CARGOS]
        siape_name = top_rows[-1]['NOME'] if top_rows else None
        since = None
        if top_rows:
            d = top_rows[-1]['DATA_INGRESSO_CARGOFUNCAO']
            if re.match(r'\d\d/\d\d/\d{4}$', d):
                since = f'{d[6:]}-{d[3:5]}-{d[:2]}'
        lot = sorted({r['ORG_LOTACAO'] for m in c_months for r in c_months[m]})
        top_months = sorted({m for m in c_months if any(r['DESCRICAO_CARGO'].strip().upper() in TOP_CARGOS for r in c_months[m])})
        siape_src = portal_url('siape', last)
        items = []
        r_months = rem.get(sid, {})
        observations = sorted(obs.get(sid, []))
        for key, (col, label) in REM_COLS.items():
            by = {}
            for m, rows in sorted(r_months.items()):
                v = round(sum(num(r.get(col)) for r in rows), 2)
                if v != 0:
                    by[str(m)] = v
            if not r_months:
                if key != 'salary':
                    continue
                note = ('Sem linha de remuneração no arquivo do SIAPE nos meses em que o cadastro mostra o cargo. '
                        f'Órgão de lotação no cadastro: {", ".join(lot)}. A Constituição permite ao deputado ou senador '
                        'nomeado ministro optar pela remuneração do mandato (art. 56, § 3º), que então é paga pela Casa legislativa.')
                items.append({'key': 'salary', 'label': 'Salário (subsídio)', 'uses': None, 'monthly': None, 'year_total': None,
                              'months': None, 'by_month': None, 'note': note, 'source': siape_src})
                continue
            if not by and key not in ('salary', 'functional_property_fee'):
                continue
            ms = [int(k) for k in by]
            uses = bool(by) if key != 'functional_property_fee' else (True if by else None)
            if key == 'salary' and not by:
                uses = None
            note = f'Do arquivo mensal de remuneração do SIAPE (Portal da Transparência, Id do Portal {sid}), meses em que o cadastro mostra o cargo: {months_label(top_months)}. "monthly" é o valor de {MONTH_PT[int(last[4:]) - 1]}/2026.'
            if key == 'functional_property_fee':
                note = ('Desconto cobrado de quem ocupa imóvel funcional; quando aparece, a pessoa usa um imóvel da União.' if by else
                        'O arquivo não mostra taxa de ocupação de imóvel funcional; isso não prova que a pessoa não use um imóvel funcional nem uma residência oficial.')
            if key == 'salary' and not by:
                note = ('O SIAPE não paga remuneração básica a esta pessoa (coluna zerada em todos os meses). Órgão de lotação no cadastro: '
                        f'{", ".join(lot)}. A Constituição permite ao parlamentar nomeado ministro optar pela remuneração do mandato (art. 56, § 3º).')
            if key == 'salary':
                orgs = {}
                for m in top_months:
                    org = next(r['ORG_EXERCICIO'] for r in c_months[m] if r['DESCRICAO_CARGO'].strip().upper() in TOP_CARGOS)
                    orgs.setdefault(org, []).append(m)
                if len(orgs) > 1:
                    note += ' Órgão de exercício no cadastro, por mês: ' + '; '.join(f'{months_label(v)}: {k}' for k, v in orgs.items()) + '.'
            if key == 'salary' and observations:
                note += ' Observações do Portal: ' + ' '.join(o.rstrip('.') + '.' for o in observations)
            items.append({'key': key, 'label': label, 'uses': uses,
                          'monthly': by.get(str(int(last[4:]))) if by else None,
                          'year_total': round(sum(by.values()), 2) if by else None,
                          'months': months_label(ms), 'by_month': {k: v for k, v in sorted(by.items(), key=lambda x: int(x[0]))} or None,
                          'note': note, 'source': siape_src})
        if position == 'ministros':
            items.append({'key': 'housing', 'label': 'Auxílio-moradia', 'uses': None, 'monthly': None, 'year_total': None, 'months': None,
                          'by_month': None,
                          'note': 'Não há fonte por pessoa: o arquivo de remuneração soma todas as verbas indenizatórias num total só (item "indemnities"), sem dizer se há auxílio-moradia.',
                          'source': siape_src})
        js = [j for j in jet.get(sid, []) if j['month'] in top_months]
        if js:
            by = {}
            for j in js:
                by[str(j['month'])] = round(by.get(str(j['month']), 0) + j['value'], 2)
            boards = sorted({j['company'] for j in js})
            ms = [int(k) for k in by]
            items.append({'key': 'jetons', 'label': 'Jetons de conselhos', 'uses': True,
                          'monthly': by.get(str(max(ms))), 'year_total': round(sum(by.values()), 2), 'months': months_label(ms),
                          'by_month': dict(sorted(by.items(), key=lambda x: int(x[0]))),
                          'note': 'Conselhos: ' + '; '.join(boards) + '. Arquivo "Honorários (Jetons)" do Portal da Transparência, ligado à pessoa pelo Id do Portal; só os meses em que o cadastro mostra o cargo.',
                          'source': portal_url('jetons', jet_months[-1])})
        else:
            items.append({'key': 'jetons', 'label': 'Jetons de conselhos', 'uses': False, 'monthly': None, 'year_total': None,
                          'months': None, 'by_month': None,
                          'note': f'Nenhum jeton no arquivo "Honorários (Jetons)" do Portal de jan a {MONTH_PT[int(jet_months[-1][4:]) - 1]} 2026. O arquivo traz o que as empresas informam ao Portal.',
                          'source': portal_url('jetons', jet_months[-1])})
        party = None
        for rec in (lookup_data.get('camara', {}).get(name) or []):
            st = rec.get('ultimo_status') or {}
            if siape_name and norm(rec.get('nome_civil')) == norm(siape_name):
                party = st.get('siglaPartido')
                items.append({'key': 'mandate', 'label': 'Mandato de deputado federal', 'uses': None, 'monthly': None, 'year_total': None,
                              'months': None, 'by_month': None,
                              'note': f'Câmara dos Deputados, dados abertos: situação "{st.get("situacao")}", partido {st.get("siglaPartido")}-{st.get("siglaUf")} (registro de {st.get("data")}).',
                              'source': rec['url']})
        official_photo = None
        for rec in (lookup_data.get('camara', {}).get(name) or []):
            st = rec.get('ultimo_status') or {}
            if siape_name and norm(rec.get('nome_civil')) == norm(siape_name) and st.get('urlFoto'):
                official_photo = (st['urlFoto'], 'Câmara dos Deputados (foto oficial do deputado)')
        for sen in senators_away:
            ident = sen['IdentificacaoParlamentar']
            if siape_name and norm(ident['NomeCompletoParlamentar']) == norm(siape_name):
                mandate = sen.get('Mandato', {})
                ex = mandate.get('Exercicios', {}).get('Exercicio', [])
                ex = ex if isinstance(ex, list) else [ex]
                cause = ex[-1].get('DescricaoCausaAfastamento') if ex else None
                party = ident.get('SiglaPartidoParlamentar')
                official_photo = (ident['UrlFotoParlamentar'].replace('http://', 'https://'), 'Senado Federal (foto oficial do senador)')
                items.append({'key': 'mandate', 'label': 'Mandato de senador', 'uses': None, 'monthly': None, 'year_total': None,
                              'months': None, 'by_month': None,
                              'note': f'Senado Federal, dados abertos: senador afastado ({mandate.get("DescricaoParticipacao")}), partido {party}-{mandate.get("UfParlamentar")}, causa do afastamento: {cause}.',
                              'source': lookup_data['senado_afastados']['url']})
        photo = photo_credit = None
        uperson = {'presidente': 'lula', 'vice': 'geraldo-alckmin'}.get(position) or ('dario-durigan' if sid == '96103' else None)
        uph = (union['people'].get(uperson) or {}).get('photo') if uperson else None
        if official_photo:
            photo, photo_credit = official_photo
        elif uph:
            photo = uph['url']
            photo_credit = f'{uph.get("author") or uph.get("artist") or ""}, {uph.get("license")}, Wikimedia Commons ({uph.get("file_page")})'.strip(', ')
        else:
            ph = lookup_data.get('photos', {}).get(name) or {}
            label = next((c['label'] for c in ph.get('candidates', []) if c['qid'] == ph.get('qid')), '')
            last_token = norm(common or name).split()[-1]
            artist_text = re.sub(r'<[^>]+>', '', ph.get('artist') or '')
            official = any(w in (ph.get('file') or '').lower() for w in ('oficia', 'institucional', 'posse')) or any(
                w in artist_text for w in OFFICIAL_AUTHORS)
            if ph.get('thumb') and last_token in norm(label) and official:
                photo = ph['thumb']
                artist = re.sub(r'<[^>]+>', '', ph.get('artist') or '').strip()
                photo_credit = f'{artist}, {ph.get("license")}, Wikimedia Commons ({ph.get("file_page")})'
            else:
                why = ('Só há foto de autor não oficial no Wikimedia Commons; ' if ph.get('thumb') else 'Sem foto no Wikidata/Wikimedia Commons; ')
                not_found.append({'what': f'Foto oficial de {name}', 'why': why + 'a lista do Planalto não traz fotos e as páginas de cada ministério não foram lidas.',
                                  'tried': [PLANALTO_LIST, 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=' + (common or name)]})
        people.append({'id': 'exec:' + slug(name), 'position': position, 'name': name, 'role': role, 'ministry': ministry,
                       'party': party, 'since': since, 'photo': photo, 'photo_credit': photo_credit,
                       'page': {'ministros': PLANALTO_LIST, 'presidente': BIO_PRESIDENT, 'vice': BIO_VICE}[position],
                       'items': items, 'data_as_of': f'{last[:4]}-{last[4:]}'})
    sheet_ids = {x[0] for x in PEOPLE}
    last_m = int(last[4:])
    holders = {}
    for sid, by_month in cad.items():
        for r in by_month.get(last_m, []):
            if r['DESCRICAO_CARGO'].strip().upper() in TOP_CARGOS:
                holders.setdefault(r['ORG_EXERCICIO'], []).append(sid)
    for sid, by_month in cad.items():
        for r in by_month.get(last_m, []):
            if r['DESCRICAO_CARGO'].strip().upper() in TOP_CARGOS and sid not in sheet_ids:
                others = [x for x in holders.get(r['ORG_EXERCICIO'], []) if x != sid]
                other_names = [next(q[2] for q in PEOPLE if q[0] == x) for x in others if x in sheet_ids]
                not_found.append({'what': f'{r["NOME"]}: aparece como {r["DESCRICAO_CARGO"]} ({r["ORG_EXERCICIO"]}) no cadastro do SIAPE de {MONTH_PT[last_m - 1]}/2026, mas não está na lista do Planalto',
                                  'why': ('Os dois registros oficiais discordam: no mesmo cadastro, o mesmo órgão tem também ' + ', '.join(other_names)
                                          + ', que é quem a lista do Planalto (atualizada em 05/05/2026) nomeia; a pessoa ficou fora de "people". Remuneração básica bruta no SIAPE por mês de 2026: '
                                          + json.dumps({str(m): round(sum(num(x.get('REMUNERAÇÃO BÁSICA BRUTA (R$)')) for x in rows), 2) for m, rows in sorted(rem.get(sid, {}).items())}, ensure_ascii=False)
                                          + '. Precisa do ato de exoneração ou nomeação no Diário Oficial para resolver.'),
                                  'tried': [PLANALTO_LIST, portal_url('siape', last)]})
    cp = cpgf_summary(manifest)
    for p in people:
        if p['position'] in cp['by_person']:
            p['items'].append(cp['by_person'][p['position']])
    out = {
        'collected_on': TODAY,
        'sources': sources(manifest),
        'positions': positions(cp),
        'people': people,
        'not_found': not_found + NOT_FOUND_FIXED,
    }
    dest = os.path.join(ROOT, 'data', 'federal', 'executive-2026.json')
    json.dump(out, open(dest, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', dest, len(people), 'people')


def cpgf_summary(manifest):
    months = [ym for ym in MONTHS if manifest.get(f'cpgf-{ym}', {}).get('filtered')]
    tot, vice, units, secret = {}, {}, {}, {}
    for ym in months:
        h, rows = read_csv(os.path.join(FILT, f'cpgf-{ym}-presidencia.csv'))
        ix = {k: i for i, k in enumerate(h)}
        m = str(int(ym[4:]))
        for r in rows:
            v = num(r[ix['VALOR TRANSAÇÃO']])
            tot[m] = round(tot.get(m, 0) + v, 2)
            unit = r[ix['NOME UNIDADE GESTORA']].strip()
            units.setdefault(unit, {})
            units[unit][m] = round(units[unit].get(m, 0) + v, 2)
            if r[ix['CÓDIGO ÓRGÃO']].strip() == '60000':
                vice[m] = round(vice.get(m, 0) + v, 2)
            if 'SIGIL' in (r[ix['NOME PORTADOR']] + r[ix['TRANSAÇÃO']] + r[ix['NOME FAVORECIDO']]).upper():
                secret[m] = round(secret.get(m, 0) + v, 2)
    pres = {m: round(tot[m] - vice.get(m, 0), 2) for m in tot}
    ms = [int(m) for m in tot]
    src = portal_url('cpgf', months[-1])
    note_common = ('Gasto com o Cartão de Pagamento do Governo Federal das unidades do órgão Presidência da República no extrato do mês; '
                   'não é renda pessoal. Mês = mês do extrato do arquivo do Portal.')
    by_person = {
        'presidente': {'key': 'cpgf', 'label': 'Cartão corporativo da Presidência (gasto das unidades)', 'uses': None,
                       'monthly': pres.get(str(max(ms))), 'year_total': round(sum(pres.values()), 2), 'months': months_label(ms),
                       'by_month': dict(sorted(pres.items(), key=lambda x: int(x[0]))),
                       'note': note_common + ' Sem as unidades da Vice-Presidência. Unidades: ' + '; '.join(u for u in sorted(units) if 'VICE' not in u)
                               + f'. Das despesas de todo o órgão (com a Vice), {brl(sum(secret.values()))} de {brl(sum(tot.values()))} aparecem como "Informações protegidas por sigilo", sem portador nem favorecido. Total por unidade, '
                               + months_label(ms) + ': ' + '; '.join(f'{u}: {brl(sum(v.values()))}' for u, v in sorted(units.items())) + '.',
                       'source': src},
        'vice': {'key': 'cpgf', 'label': 'Cartão corporativo da Vice-Presidência (gasto das unidades)', 'uses': None,
                 'monthly': vice.get(str(max(ms))), 'year_total': round(sum(vice.values()), 2), 'months': months_label(ms),
                 'by_month': dict(sorted(vice.items(), key=lambda x: int(x[0]))), 'note': note_common + ' Só o Gabinete da Vice-Presidência (órgão 60000).',
                 'source': src},
    }
    detail = {'note': note_common, 'source_files': [portal_url('cpgf', ym) for ym in months],
              'total_by_month': dict(sorted(tot.items(), key=lambda x: int(x[0]))), 'total': round(sum(tot.values()), 2),
              'secret_by_month': dict(sorted(secret.items(), key=lambda x: int(x[0]))),
              'by_unit': {u: dict(sorted(v.items(), key=lambda x: int(x[0]))) for u, v in sorted(units.items())}}
    return {'by_person': by_person, 'detail': detail}


def positions(cp):
    sal = {'key': 'salary', 'label': 'Salário (subsídio)', 'value_monthly': SALARY,
           'rule': 'Decreto Legislativo 172/2022: R$ 46.366,19 por mês desde 1º de fevereiro de 2025, igual para Presidente, Vice e Ministros de Estado.',
           'source': DL172}
    tot = cp['by_person']['presidente']
    return [
        {'id': 'presidente', 'items': [sal,
            {'key': 'residence', 'label': 'Residência oficial (Palácio da Alvorada)', 'value_monthly': None,
             'rule': 'Residência oficial do Presidente da República, em espécie; nenhum valor em reais publicado.', 'source': ALVORADA},
            {'key': 'cpgf', 'label': 'Cartão corporativo da Presidência (gasto das unidades)', 'value_monthly': None,
             'rule': f'Gasto das unidades da Presidência (sem a Vice) com o cartão, {tot["months"]}: {brl(tot["year_total"])} no total. Não é renda pessoal.',
             'source': tot['source']}]},
        {'id': 'vice', 'items': [sal,
            {'key': 'residence', 'label': 'Residência oficial (Palácio do Jaburu)', 'value_monthly': None,
             'rule': 'Residência oficial do Vice-Presidente, em espécie; nenhum valor em reais publicado.', 'source': JABURU}]},
        {'id': 'ministros', 'items': [sal,
            {'key': 'housing', 'label': 'Auxílio-moradia (teto)', 'value_monthly': round(SALARY * 0.25, 2),
             'rule': 'Lei 8.112/1990 arts. 60-A a 60-E: ressarcimento de aluguel ou hotel, só sem imóvel funcional disponível e sem imóvel próprio na cidade nos 12 meses antes da nomeação; teto de 25% do valor do cargo de Ministro de Estado (art. 60-D) e piso garantido de R$ 1.800,00 (§ 2º). O teto é 25% de R$ 46.366,19.',
             'source': L8112},
            {'key': 'functional_property', 'label': 'Imóvel funcional', 'value_monthly': None,
             'rule': 'O auxílio-moradia só cabe quando não há imóvel funcional disponível (Lei 8.112 art. 60-B, I); quem ocupa paga taxa de ocupação, que aparece no arquivo de remuneração do Portal. Sem valor do imóvel publicado.',
             'source': L8112},
            {'key': 'jetons', 'label': 'Jetons de conselhos de estatais', 'value_monthly': None,
             'rule': 'Permitidos pela Lei 8.112 art. 119, parágrafo único; cada jeton limitado a 10% da remuneração mensal média dos diretores da empresa (Lei 9.292/1996 art. 1º), em no máximo 2 conselhos remunerados (Lei 13.303/2016 art. 20). Sem valor único: depende da empresa.',
             'source': L9292}]},
    ]


def sources(manifest):
    s = [
        {'name': 'Decreto Legislativo 172/2022 (subsídios)', 'url': DL172, 'read_on': TODAY},
        {'name': 'Lei 8.112/1990, texto compilado (auxílio-moradia, jetons)', 'url': L8112, 'read_on': TODAY},
        {'name': 'Lei 9.292/1996 (limite dos jetons)', 'url': L9292, 'read_on': TODAY},
        {'name': 'Lei 13.303/2016 art. 20 (até dois conselhos)', 'url': L13303, 'read_on': TODAY},
        {'name': 'Constituição Federal, art. 56 § 3º', 'url': CF, 'read_on': TODAY},
        {'name': 'Planalto: Ministros e Ministras (atualizado em 05/05/2026)', 'url': PLANALTO_LIST, 'read_on': TODAY},
        {'name': 'Planalto: Palácio da Alvorada', 'url': ALVORADA, 'read_on': TODAY},
        {'name': 'Câmara dos Deputados, dados abertos (deputados)', 'url': 'https://dadosabertos.camara.leg.br/api/v2/deputados', 'read_on': TODAY},
        {'name': 'Senado Federal, dados abertos (senadores afastados)', 'url': 'https://legis.senado.leg.br/dadosabertos/senador/afastados.json', 'read_on': TODAY},
        {'name': 'Wikimedia Commons e Wikidata (fotos)', 'url': 'https://commons.wikimedia.org/', 'read_on': TODAY},
    ]
    for key, info in sorted(manifest.items()):
        s.append({'name': f'Portal da Transparência, {key} (Last-Modified {info.get("last_modified")}, sha256 {info.get("sha256", "")[:12]})',
                  'url': info['url'], 'read_on': info.get('read_on', TODAY)})
    return s


if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv) > 1 else ''
    if stage == 'fetch':
        fetch()
    elif stage == 'lookup':
        lookup()
    elif stage == 'build':
        build()
    else:
        raise SystemExit('usage: collect-executive-2026.py fetch|build')
