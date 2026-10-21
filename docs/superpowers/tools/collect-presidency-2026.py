#!/usr/bin/env python3
"""Collect 2026 public spending tied to the post of President of the Republic and to the President's spouse.

Sources: Portal da Transparencia bulk downloads (viagens 2026, cpgf monthly extracts already filtered by
collect-executive-2026.py). Stages: filter (zip -> filtered CSVs), build (filtered CSVs -> presidency-2026.json).
Run from the project root: .venv/bin/python -B docs/superpowers/tools/collect-presidency-2026.py filter|build
"""
import csv, io, json, re, sys, unicodedata, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/federal/raw-pay/presidency'
EXEC_FILTERED = ROOT / 'data/federal/raw-pay/executive/filtered'
OUT = ROOT / 'data/federal/presidency-2026.json'
ZIP = RAW / 'dl/2026_Viagens.zip'
FILTERED = RAW / 'filtered'
TODAY = '2026-10-21'
VIAGENS_URL = 'https://portaldatransparencia.gov.br/download-de-dados/viagens/2026'

csv.field_size_limit(10**9)


def norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


# Broad first cut; the build stage applies the narrow, documented rules.
BROAD = re.compile(r'presiden|lula|janja|rosangela|primeira.{0,3}dama|1a dama|comitiva|precurs|escalao avancado|'
                   r'seguranca presidencial|\bpr\b|sigil')


def open_member(z, name):
    return io.TextIOWrapper(z.open(name), encoding='cp1252', errors='replace', newline='')


def filter_stage():
    FILTERED.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(ZIP)
    names = {n.split('_', 1)[1].split('.')[0]: n for n in z.namelist()}
    ids = set()
    stats = {'viagem_rows': 0}
    with open_member(z, names['Viagem']) as f, open(FILTERED / 'viagem.csv', 'w', newline='', encoding='utf-8') as o:
        r = csv.reader(f, delimiter=';')
        w = csv.writer(o, delimiter=';')
        header = next(r)
        w.writerow(header)
        h = {k: i for i, k in enumerate(header)}
        for row in r:
            stats['viagem_rows'] += 1
            text = norm(' '.join([row[h['Motivo']], row[h['Nome']], row[h['Nome órgão solicitante']],
                                  row[h['Cargo']], row[h['Descrição Função']]]))
            if row[h['Código do órgão superior']] == '20000' or BROAD.search(text):
                w.writerow(row)
                ids.add(row[0])
    stats['viagem_kept'] = len(ids)
    for part in ('Pagamento', 'Passagem', 'Trecho'):
        kept = 0
        with open_member(z, names[part]) as f, open(FILTERED / f'{part.lower()}.csv', 'w', newline='', encoding='utf-8') as o:
            r = csv.reader(f, delimiter=';')
            w = csv.writer(o, delimiter=';')
            w.writerow(next(r))
            for row in r:
                if row[0] in ids:
                    w.writerow(row)
                    kept += 1
        stats[f'{part.lower()}_kept'] = kept
    json.dump(stats, open(FILTERED / 'stats.json', 'w'), indent=1)
    print(stats)


# ---- classification rules (the same rules work for any President and spouse) ----
# Organ names that contain "presidente" but say nothing about a trip of the President: removed before matching.
ORGAN_NAMES = re.compile(r'assessor(ia|a)?[- ]?(chefe )?(especial )?(da assessoria especial )?do presidente da republica|'
                         r'orgao de assessoramento do presidente da republica|gabinete pessoal do presidente da republica|'
                         r'assessor-chefe da assessoria especial do presidente da republica')
PRES_NAME = (r'((sr\.? |senhor |exmo\.? (sr\.? |senhor )?|excelentissimo senhor )?'
             r'(presidente da republica|presidenta da republica|presidente lula|presidente luiz)|'
             r'(sr\.? |senhor |exmo\.? (sr\.? |senhor )?|excelentissimo senhor )presidente\b)')
TRIP_WORD = (r'(viagem|viagens|visita|agenda|agendas|comitiva|deslocamento|missao|escav|escalao avancado|precursora|evento|'
             r'cerimonia|presenca|participacao|encontro|compromisso|programacao)')
PRES = re.compile(TRIP_WORD + r'( [\w\-/.,]+){0,5} (d[oa]|com o|pelo|ao) ' + PRES_NAME + '|'
                  + TRIP_WORD + r' presidencia(l|is)\b|\bcomitiva presidencial|\bescav presidencial|'
                  r'\b(viagem|visita|agenda|comitiva|missao|escav|deslocamento) do pr\b|\b(sr|senhor)\.? pr\b')
FOREIGN_AFTER = re.compile(r'^[ ,]*(d[aoe]s? (?!republica\b|brasil\b|federativa\b|sr\b)|'
                           r'(francesa|portuguesa|italiana|argentina|chilena|angolana|popular|democratica|oriental|'
                           r'islamica|socialista|eslovaca|tcheca|coreana|sul-coreana|do chile|de portugal)\b)')
NOT_HIM = re.compile(r'(vice|ex)[- ]?presidente|lei n[o ]*7\.?474|decreto n[o ]*6\.?381')
SPOUSE = re.compile(r'janja|rosangela lula|rosangela da silva|primeira[ -]?dama|1a\.? dama|'
                    r'(esposa|conjuge) do (sr\.? |senhor )?presidente da republica')
ACTION = re.compile(r'acompanh|acompahar|comitiva|precurs|escalao avancado|\bescav\b|equipe avancada|prepar|apoio|'
                    r'apoiar|seguranca|cerimonial|organiza|logistic|montagem|cobertura|\bcompor\b|integrar|assessorar|'
                    r'vistoria|coordena|filmagem|fotograf|transmissao|imprensa|recepcao|\breceber\b')
ROLES = [('preparacao', re.compile(r'precurs|escalao avancado|\bescav\b|equipe avancada|prepar|vistoria')),
         ('seguranca', re.compile(r'seguranca (presidencial|do (sr\.? |senhor )?presidente|da comitiva|de dignitario|'
                                  r'pessoal|aproximada)|\bgsi\b')),
         ('cobertura', re.compile(r'cobertura|imprensa|filmagem|fotograf|transmissao')),
         ('acompanhamento', re.compile(r'acompanh|acompahar|comitiva')),
         ('apoio', ACTION)]
ROLE_LABEL = {'preparacao': 'preparação (escalão avançado, precursora)', 'seguranca': 'segurança',
              'cobertura': 'cobertura de imprensa', 'acompanhamento': 'acompanhamento e comitiva',
              'apoio': 'apoio, cerimonial e logística'}
# A purpose that is the President's trip itself, with no participation verb, is part of the entourage.
TRIP_ITSELF = re.compile(r'(viagem|viagens|missao|deslocamento) (nacional |internacional |oficial )?(presidencia(l|is)|'
                         r'd[oa] (sr\.? |senhor |exmo\.? (sr\.? )?)?presidente da republica)')
PARTICIPATION = re.compile(r'participa|representa|convid|presenca|reuniao|palestra|delegacao|forum|seminario|conferencia')
TRAVEL_DESK = re.compile(r'conforme solicita\w* n?[o ]*\d+/\d+ da coordena\w* d[ae] viage')
SECRET = 'sigil'


def mentions(rx, m):
    for x in rx.finditer(m):
        tail = m[x.end():x.end() + 40]
        if not FOREIGN_AFTER.search(tail):
            return True
    return False


def classify(motivo):
    """(card, role) for a purpose text. card: president | spouse | None. role: one of ROLES or 'evento'."""
    m = ORGAN_NAMES.sub(' ', norm(motivo))
    if NOT_HIM.search(m) and not SPOUSE.search(m):
        p = False
    else:
        p = mentions(PRES, re.sub(r'(vice|ex)[- ]?presidente', ' ', m))
    s = mentions(SPOUSE, m)
    if not (p or s):
        return None, None, False
    role = next((name for name, rx in ROLES if rx.search(m)), 'evento')
    if role == 'evento' and TRIP_ITSELF.search(m) and not PARTICIPATION.search(m):
        role = 'acompanhamento'
    return ('president' if p else 'spouse'), role, (p and s)


def load(name, folder=None):
    rows = list(csv.reader(open((folder or FILTERED) / name, encoding='utf-8'), delimiter=';'))
    return {k.strip(): i for i, k in enumerate(rows[0])}, rows[1:]


def num(s):
    return float(s.replace('.', '').replace(',', '.')) if s and s.strip() else 0.0


def iso(d):
    return f'{d[6:10]}-{d[3:5]}-{d[0:2]}' if len(d) == 10 else None


def short(text, n=300):
    text = ' '.join(text.split())
    return text if len(text) <= n else text[:n].rsplit(' ', 1)[0] + ' (...)'


def trip_rows():
    """Every trip of jan..ago 2026 in the filtered extract, with its values and classification."""
    h, rows = load('viagem.csv')
    out = []
    for r in rows:
        start = iso(r[h['Período - Data de início']])
        if not start or not ('2026-01' <= start[:7] <= '2026-08'):
            continue
        card, role, both = classify(r[h['Motivo']])
        m = norm(r[h['Motivo']])
        out.append({
            'id': r[0], 'organ_code': r[h['Código órgão solicitante']], 'organ': r[h['Nome órgão solicitante']],
            'superior': r[h['Código do órgão superior']], 'status': r[h['Situação']],
            'name': r[h['Nome']], 'cpf': r[h['CPF viajante']], 'start': start, 'end': iso(r[h['Período - Data de fim']]),
            'month': str(int(start[5:7])), 'destinations': r[h['Destinos']], 'purpose': r[h['Motivo']],
            'per_diems': num(r[h['Valor diárias']]), 'tickets': num(r[h['Valor passagens']]),
            'refund': num(r[h['Valor devolução']]), 'other': num(r[h['Valor outros gastos']]),
            'card': card, 'role': role, 'both': both,
            'secret': SECRET in m and SECRET in norm(r[h['Nome']]),
            'desk': bool(TRAVEL_DESK.search(m)),
        })
    for t in out:
        t['total'] = round(t['per_diems'] + t['tickets'] + t['other'] - t['refund'], 2)
    return out


def summarise(trips):
    by_month, sums = {}, {'tickets': 0.0, 'per_diems': 0.0, 'other': 0.0, 'refund': 0.0, 'total': 0.0}
    for t in trips:
        by_month[t['month']] = round(by_month.get(t['month'], 0.0) + t['total'], 2)
        for k in sums:
            sums[k] += t[k]
    trav = {(t['name'], t['cpf']) for t in trips if 'sigil' not in norm(t['name'])}
    return {'by_month': dict(sorted(by_month.items(), key=lambda kv: int(kv[0]))),
            'sums': {k: round(v, 2) for k, v in sums.items()}, 'trips': len(trips), 'travellers': len(trav)}


def brl(v):
    s = f'{v:,.2f}'
    return 'R$ ' + s.replace(',', 'X').replace('.', ',').replace('X', '.')


def month_counts(trips):
    c = {}
    for t in trips:
        c[t['month']] = c.get(t['month'], 0) + 1
    return ', '.join(f'{MONTHS[int(k) - 1]} {v}' for k, v in sorted(c.items(), key=lambda kv: int(kv[0])))


MONTHS = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']


def cluster(trips):
    """Group entourage trips that share the first destination and overlapping dates (2-day gap)."""
    key = lambda t: norm(t['destinations'].split(',')[0].strip())
    groups = []
    for t in sorted(trips, key=lambda t: (key(t), t['start'])):
        g = groups[-1] if groups else None
        if g and g['key'] == key(t) and t['start'] <= add_days(g['end'], 2):
            g['items'].append(t)
            g['end'] = max(g['end'], t['end'] or t['start'])
        else:
            groups.append({'key': key(t), 'start': t['start'], 'end': t['end'] or t['start'], 'items': [t]})
    out = []
    for g in groups:
        import collections
        dest = collections.Counter(t['destinations'] for t in g['items']).most_common(1)[0][0]
        purpose = collections.Counter(t['purpose'] for t in g['items']).most_common(1)[0][0]
        s = summarise(g['items'])['sums']
        out.append({'start': g['start'], 'end': g['end'], 'destinations': dest, 'purpose': short(purpose),
                    'travellers': len({(t['name'], t['cpf']) for t in g['items']}),
                    'tickets': s['tickets'], 'per_diems': s['per_diems'], 'other': s['other'], 'total': s['total'],
                    'confidential': False, 'source': VIAGENS_URL})
    return sorted(out, key=lambda x: (x['start'], x['destinations']))


def add_days(d, n):
    import datetime
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


# ---- CPGF (corporate card) of the Presidencia, from the extracts collected by collect-executive-2026.py ----
PRESIDENT_UGS = {'110001': 'Secretaria de Administração/PR', '110809': 'Secretaria de Administração, Peculiaridades',
                 '110322': 'Gabinete de Segurança Institucional/PR'}
OTHER_UGS = {'110120': 'Agência Brasileira de Inteligência (ABIN)', '110538': 'Agência Brasileira de Inteligência (ABIN)',
             '110245': 'Fundo de Imprensa Nacional', '115406': 'Empresa Brasil de Comunicação (EBC)',
             '110101': 'Vice-Presidência da República', '110766': 'Vice-Presidência da República'}
# What the itemised rows pay for, read from the payee's registered name only (rule written here, applied to every row).
CATEGORIES = [('hospedagem', re.compile(r'hotel|hoteis|pousada|hospedag|resort|flat\b|suites|hostel|inn\b|palace|apart')),
              ('transporte', re.compile(r'posto|combust|petrol|locadora|localiza|movida|unidas|taxi|uber|aviacao|aereo|'
                                        r'aeroporto|transporte|estacionamento|pedagio|parking|shell|ipiranga|rent a car')),
              ('alimentação', re.compile(r'restaurante|lanchonete|padaria|aliment|churrasc|pizz|\bbar\b|cafe|supermerc|'
                                         r'atacad|mercado|buffet|refeic|panific|food|grill|cozinha|sorvet|doceria|carrefour|'
                                         r'assai|hortifruti|emporio|pao de acucar|confeitaria|bistro'))]


def cpgf_rows():
    import glob
    out = []
    for p in sorted(glob.glob(str(EXEC_FILTERED / 'cpgf-2026*-presidencia.csv'))):
        h, rows = load(Path(p).name, EXEC_FILTERED)
        for r in rows:
            out.append({'ug': r[h['CÓDIGO UNIDADE GESTORA']], 'ug_name': r[h['NOME UNIDADE GESTORA']],
                        'month': str(int(r[h['MÊS EXTRATO']])), 'payee': r[h['NOME FAVORECIDO']],
                        'tx': r[h['TRANSAÇÃO']], 'value': num(r[h['VALOR TRANSAÇÃO']]),
                        'secret': 'sigil' in norm(r[h['TRANSAÇÃO']])})
    return out


def category(row):
    if 'saque' in norm(row['tx']):
        return 'saque em dinheiro'
    n = norm(row['payee'])
    return next((c for c, rx in CATEGORIES if rx.search(n)), 'outros')


def cpgf_url(m):
    return f'https://portaldatransparencia.gov.br/download-de-dados/cpgf/2026{int(m):02d}'


def review_stage():
    import collections, random
    trips = trip_rows()
    c = collections.Counter((t['card'], t['role']) for t in trips if t['card'])
    for k, v in sorted(c.items(), key=str):
        print(k, v, brl(sum(t['total'] for t in trips if (t['card'], t['role']) == k)))
    print('both named', sum(t['both'] for t in trips))
    pres = [t for t in trips if t['superior'] == '20000' and t['organ_code'] in ('20101', '20000')]
    print('presidency secret', sum(t['secret'] for t in pres), 'desk', sum(t['desk'] and not t['card'] for t in pres))
    random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    for k in sorted(c, key=str):
        ex = [t for t in trips if (t['card'], t['role']) == k]
        print('==', k)
        for t in random.sample(ex, min(len(ex), n)):
            print('  -', t['organ'][:28], '|', norm(t['purpose'])[:200])


def build_stage():
    import collections
    trips = trip_rows()
    manual = json.load(open(RAW / 'manual.json', encoding='utf-8')) if (RAW / 'manual.json').exists() else {}
    ent = [t for t in trips if t['card'] == 'president' and t['role'] != 'evento']
    evt = [t for t in trips if t['card'] == 'president' and t['role'] == 'evento']
    pres_org = [t for t in trips if t['superior'] == '20000' and t['organ_code'] in ('20101', '20000')]
    secret = [t for t in pres_org if t['secret']]
    desk = [t for t in pres_org if t['desk'] and not t['card'] and not t['secret']]
    sp = [t for t in trips if t['card'] == 'spouse' and t['role'] != 'evento']
    sp_evt = [t for t in trips if t['card'] == 'spouse' and t['role'] == 'evento']
    both = [t for t in trips if t['both']]
    se, sv, ss, sd = summarise(ent), summarise(evt), summarise(secret), summarise(desk)

    def parts(s):
        x = s['sums']
        return (f"passagens {brl(x['tickets'])}, diárias {brl(x['per_diems'])}, outros gastos {brl(x['other'])}, "
                f"devoluções {brl(x['refund'])}")

    by_role = collections.Counter()
    for t in ent:
        by_role[t['role']] += t['total']
    by_org = collections.Counter()
    for t in ent:
        by_org[t['organ']] += t['total']
    rule = ('Regra: o motivo da viagem cita uma viagem, agenda, visita, comitiva ou presença do Presidente da República '
            '(nunca do Vice, de ex-presidentes ou de chefes de Estado estrangeiros) e declara uma função de apoio '
            '(acompanhar, compor comitiva, escalão avançado, precursora, segurança, cerimonial, logística, cobertura '
            'de imprensa), ou é a própria viagem presidencial sem verbo de participação. Total = passagens + diárias + '
            'outros gastos menos devoluções, mês de início da viagem.')
    items = [
        {'key': 'trips_entourage', 'label': 'Viagens de servidores para acompanhar, preparar, proteger ou apoiar viagens do Presidente (gasto público ligado ao cargo)',
         'year_total': se['sums']['total'], 'by_month': se['by_month'], 'confidential_total': None,
         'note': (f"{se['trips']} viagens, {se['travellers']} viajantes, de {len(by_org)} órgãos federais. {parts(se)}. "
                  'Por função: ' + '; '.join(f'{ROLE_LABEL[k]} {brl(v)}' for k, v in by_role.most_common()) + '. '
                  'Órgãos com maior gasto: ' + '; '.join(f'{k} {brl(v)}' for k, v in by_org.most_common(5)) + '. '
                  + rule + ' Viagens por mês: ' + month_counts(ent) + '. A lista president.trips agrupa essas viagens pelo primeiro '
                  'destino e por datas que se sobrepõem; as datas são as da comitiva, não as do Presidente.'),
         'source': VIAGENS_URL},
        {'key': 'trips_events_with_president', 'label': 'Viagens de servidores para participar de agendas com a presença do Presidente (sem função de apoio declarada)',
         'year_total': sv['sums']['total'], 'by_month': sv['by_month'], 'confidential_total': None,
         'note': (f"{sv['trips']} viagens, {sv['travellers']} viajantes. {parts(sv)}. O motivo cita a agenda ou a presença do "
                  'Presidente, mas a função declarada é participar, representar o órgão ou ser convidado. Não somado às viagens de apoio.'),
         'source': VIAGENS_URL},
        {'key': 'trips_presidency_travel_desk', 'label': 'Viagens da Presidência "conforme solicitação da coordenação de viagem" (o motivo não cita o Presidente)',
         'year_total': sd['sums']['total'], 'by_month': sd['by_month'], 'confidential_total': None,
         'note': (f"{sd['trips']} viagens, {sd['travellers']} viajantes da Presidência da República. {parts(sd)}. O motivo diz só "
                  '"deslocamento para <cidade>, conforme solicitação nº N/26 da coordenação de viagem", sem dizer de quem é a viagem; '
                  'por isso não está somado às viagens ligadas ao Presidente.'),
         'source': VIAGENS_URL},
        {'key': 'trips_presidency_confidential', 'label': 'Viagens sigilosas da Presidência da República (motivo e destino protegidos por sigilo)',
         'year_total': None, 'by_month': ss['by_month'], 'confidential_total': ss['sums']['total'],
         'note': (f"{ss['trips']} viagens com viajante, destino e motivo marcados \"Informações protegidas por sigilo\"; os valores são publicados. "
                  f"{parts(ss)}. Sem motivo publicado não se sabe se estão ligadas a viagens do Presidente. Viagens sigilosas de outros "
                  'órgãos (Polícia Federal, PRF e outros) também não têm motivo publicado e não entram aqui.'),
         'source': VIAGENS_URL},
    ]
    # CPGF by unit
    cp = cpgf_rows()
    for ug, name in PRESIDENT_UGS.items():
        rows = [r for r in cp if r['ug'] == ug]
        bm = {}
        for r in rows:
            bm[r['month']] = round(bm.get(r['month'], 0.0) + r['value'], 2)
        conf = round(sum(r['value'] for r in rows if r['secret']), 2)
        itemised = [r for r in rows if not r['secret']]
        cat = collections.defaultdict(lambda: collections.defaultdict(float))
        for r in itemised:
            cat[category(r)][r['month']] += r['value']
        cat_txt = '; '.join(f"{c} {brl(sum(v.values()))} (" + ', '.join(f'{MONTHS[int(m) - 1]} {brl(x)}' for m, x in sorted(v.items(), key=lambda kv: int(kv[0]))) + ')'
                            for c, v in sorted(cat.items(), key=lambda kv: -sum(kv[1].values())))
        intl = round(sum(r['value'] for r in itemised if 'int$' in norm(r['tx'])), 2)
        note = (f'{len(rows)} lançamentos de jan a ago 2026: {brl(conf)} marcados "Informações protegidas por sigilo", '
                f'{brl(round(sum(r["value"] for r in itemised), 2))} detalhados.')
        if itemised:
            note += (f' Parte detalhada pelo nome do favorecido (regra de palavras no nome registrado): {cat_txt}. '
                     f'Compras e saques no exterior (INT$): {brl(intl)}.')
        note += ' Gasto da unidade com o cartão; o arquivo não diz quais compras se referem a atividades do Presidente.'
        items.append({'key': 'cpgf_' + slug(name), 'label': f'Cartão corporativo: {name} (gasto público ligado ao cargo)',
                      'year_total': round(sum(r['value'] for r in rows), 2), 'by_month': dict(sorted(bm.items(), key=lambda kv: int(kv[0]))),
                      'confidential_total': conf, 'note': note, 'source': cpgf_url(8)})
    pu = [r for r in cp if r['ug'] in PRESIDENT_UGS]
    bm = {}
    for r in pu:
        bm[r['month']] = round(bm.get(r['month'], 0.0) + r['value'], 2)
    items.insert(4, {'key': 'cpgf_president_units', 'label': 'Cartão corporativo das unidades da Presidência ligadas ao Presidente (total)',
                     'year_total': round(sum(r['value'] for r in pu), 2), 'by_month': dict(sorted(bm.items(), key=lambda kv: int(kv[0]))),
                     'confidential_total': round(sum(r['value'] for r in pu if r['secret']), 2),
                     'note': 'Soma de: ' + ', '.join(PRESIDENT_UGS.values()) + '. ABIN, Fundo de Imprensa Nacional, EBC e Vice-Presidência ficam em other_units. Arquivos mensais do CPGF, jan a ago 2026.',
                     'source': cpgf_url(8)})
    other = collections.defaultdict(float)
    otherc = collections.defaultdict(float)
    for r in cp:
        if r['ug'] in OTHER_UGS:
            other[OTHER_UGS[r['ug']]] += r['value']
            if r['secret']:
                otherc[OTHER_UGS[r['ug']]] += r['value']
    unknown = sorted({(r['ug'], r['ug_name']) for r in cp if r['ug'] not in OTHER_UGS and r['ug'] not in PRESIDENT_UGS})
    assert not unknown, unknown
    other_units = [{'unit': k, 'year_total': round(v, 2),
                    'note': f'Cartão corporativo jan a ago 2026, {brl(round(otherc[k], 2))} sob sigilo. Unidade da Presidência sem ligação declarada com a atividade do Presidente; listada à parte.'}
                   for k, v in sorted(other.items(), key=lambda kv: -kv[1])]
    # spouse
    ss_ = summarise(sp)
    sp_items = [
        {'key': 'trips_support', 'label': 'Viagens de servidores para preparar, acompanhar ou apoiar agendas dela (gasto público ligado a ela)',
         'year_total': ss_['sums']['total'] if sp else None, 'by_month': ss_['by_month'] if sp else None,
         'note': (f"{ss_['trips']} viagens, {ss_['travellers']} viajantes, de {len({t['organ'] for t in sp})} órgãos. {parts(ss_)}. "
                  'Regra: o motivo cita a primeira-dama, Janja ou Rosângela Lula da Silva (nunca cônjuges de chefes de Estado estrangeiros) '
                  'e declara uma função de apoio. Viagens que citam o Presidente e ela ao mesmo tempo ficam no cartão do Presidente: '
                  f"{len(both)} viagem, {brl(round(sum(t['total'] for t in both), 2))}. Em parte das viagens o apoio é à agenda de um ministro "
                  'da qual ela participa; o motivo de cada viagem está na lista. Nenhuma viagem de 2026 a tem como viajante.'),
         'source': VIAGENS_URL},
        {'key': 'trips_events_with_spouse', 'label': 'Viagens de servidores para participar de agendas com a presença dela (sem função de apoio declarada)',
         'year_total': summarise(sp_evt)['sums']['total'] if sp_evt else None, 'by_month': summarise(sp_evt)['by_month'] if sp_evt else None,
         'note': f'{len(sp_evt)} viagens. Não somado às viagens de apoio.', 'source': VIAGENS_URL},
    ] + manual.get('spouse_items', [])
    sp_trips = [{'start': t['start'], 'end': t['end'], 'destinations': t['destinations'], 'purpose': short(t['purpose']),
                 'travellers': 1, 'tickets': t['tickets'], 'per_diems': t['per_diems'], 'other': t['other'], 'total': t['total'],
                 'confidential': False, 'source': VIAGENS_URL, 'traveller': 'equipe de apoio'} for t in sorted(sp, key=lambda t: t['start'])]
    out = {
        'collected_on': TODAY, 'months_published': 'jan a ago 2026',
        'sources': [{'name': 'Portal da Transparência: Viagens a serviço 2026 (arquivo de 20/09/2026)', 'url': VIAGENS_URL, 'read_on': TODAY}]
        + [{'name': f'Portal da Transparência: Cartão de Pagamento do Governo Federal {MONTHS[m - 1]} 2026', 'url': cpgf_url(m), 'read_on': TODAY} for m in range(1, 9)]
        + manual.get('sources', []),
        'president': {'items': items, 'trips': cluster(ent), 'other_units': other_units},
        'spouse': {'name': 'Rosângela Lula da Silva', 'known_as': 'Janja', 'public_office': None,
                   'photo': manual.get('photo'), 'photo_credit': manual.get('photo_credit'),
                   'items': sp_items, 'trips': sp_trips, 'structure': manual.get('structure', [])},
        'not_found': manual.get('not_found', []),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('trips_entourage', brl(se['sums']['total']), se['trips'], 'clusters', len(out['president']['trips']))
    print('events', brl(sv['sums']['total']), 'desk', brl(sd['sums']['total']), sd['trips'], 'secret', brl(ss['sums']['total']), ss['trips'])
    for i in items:
        print(i['key'], i['year_total'], i['confidential_total'])
    print('other', [(o['unit'], o['year_total']) for o in other_units])
    print('spouse', brl(ss_['sums']['total']), len(sp), 'events', len(sp_evt), 'both', len(both))


def slug(s):
    return re.sub(r'[^a-z0-9]+', '_', norm(s)).strip('_')


if __name__ == '__main__':
    {'filter': filter_stage, 'review': review_stage, 'build': build_stage}[sys.argv[1]]()
