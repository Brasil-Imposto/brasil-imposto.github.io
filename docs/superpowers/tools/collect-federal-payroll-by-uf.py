#!/usr/bin/env python3
"""Collects the 2024 federal payroll per UF from the Portal da Transparencia monthly servidores files.

Stage `fetch`: downloads each monthly zip one at a time (at least PAUSE seconds between request starts), sums the
Remuneracao file per UF of the person's cadastro rows, writes one summary per category and month, deletes the zip.
Resumable: a category and month whose summary exists is skipped; a downloaded zip still on disk is reused.
Stage `build`: writes data/federal/payroll-by-uf-2024.json from the summaries, with the national check and its control.
No estimate anywhere: a person with no UF, or with two UFs, in the file goes to no_uf.
"""
import collections
import copy
import csv
import gzip
import hashlib
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
import zipfile
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW = os.path.join(ROOT, 'data', 'federal', 'raw-pay', 'payroll')
SUMS = os.path.join(RAW, 'summaries')
MAPS = os.path.join(RAW, 'uf-maps')
OUT = os.path.join(ROOT, 'data', 'federal', 'payroll-by-uf-2024.json')
YEAR = 2024
MONTHS = [f'{YEAR}{m:02d}' for m in range(1, 13)]
PAGE = 'https://portaldatransparencia.gov.br/download-de-dados/servidores'
UA = 'Mozilla/5.0'
PAUSE = 75
KEEP_MONTHS = {'202401'}
UFS = set('AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO'.split())

# (id, origin on the Portal, label)
CORE = [
    ('civil_servants_siape', 'Servidores_SIAPE', 'Civil servants of the Executive paid through SIAPE (active staff)'),
    ('staff_bacen', 'Servidores_BACEN', 'Banco Central staff (active)'),
    ('military_active', 'Militares', 'Armed Forces, active military'),
    ('military_reserve_retired', 'Reserva_Reforma_Militares', 'Armed Forces, reserve and retired military (reserva e reforma)'),
    ('retirees_siape', 'Aposentados_SIAPE', 'Retired civil servants paid through SIAPE'),
    ('retirees_bacen', 'Aposentados_BACEN', 'Retired Banco Central staff'),
    ('pensioners_siape', 'Pensionistas_SIAPE', 'Pensioners of civil servants paid through SIAPE'),
    ('pensioners_bacen', 'Pensionistas_BACEN', 'Pensioners of Banco Central staff'),
    ('pensioners_defense', 'Pensionistas_DEFESA', 'Pensioners of the military, Ministry of Defence'),
]
SUPP = [
    ('attorney_fees', 'Honorarios_Advocaticios', 'Attorney fees (honorarios advocaticios) paid to federal public attorneys'),
    ('board_fees', 'Honorarios_Jetons', 'Board fees (jetons) paid by state-owned companies to federal officials'),
]
MAP_ORIGINS = ('civil_servants_siape', 'staff_bacen')
GROSS_R = ['REMUNERACAOBASICABRUTAR', 'ABATETETOR', 'GRATIFICACAONATALINAR', 'ABATETETODAGRATIFICACAONATALINAR', 'FERIASR',
           'OUTRASREMUNERACOESEVENTUAISR']
DED_R = {'irrf': 'IRRFR', 'pss': 'PSSRPGSR', 'other_deductions': 'DEMAISDEDUCOESR', 'military_pension': 'PENSAOMILITARR',
         'health_fund': 'FUNDODESAUDER', 'housing_fee': 'TAXADEOCUPACAOIMOVELFUNCIONALR'}
NET_R = 'REMUNERACAOAPOSDEDUCOESOBRIGATORIASR'
INDEM_R = 'TOTALDEVERBASINDENIZATORIASR'
NO_UF_KEYS = {'_missing_uf': 'missing_uf', '_conflicting_uf': 'conflicting_uf', '_not_in_cadastro': 'not_in_cadastro',
              '_no_uf_column': 'no_uf_column'}

_last_start = [0.0]


def log(msg):
    line = time.strftime('%Y-%m-%d %H:%M:%S ') + msg
    print(line, flush=True)
    with open(os.path.join(RAW, 'fetch.log'), 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def norm(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^A-Z0-9]', '', s.upper())


def usd(name):
    return name[:-1] + 'U'


def cents(v):
    v = v.strip()
    if not v:
        return 0
    if ',' in v:
        v2 = v.replace('.', '')
        i = v2.index(',')
        frac = v2[i + 1:]
        if len(frac) == 2:
            return int(v2[:i] + frac)
        if len(frac) == 1:
            return int(v2[:i] + frac + '0')
        raise ValueError(f'money value {v!r}')
    if '.' in v:
        raise ValueError(f'money value {v!r}')
    return int(v) * 100


def dec(v):
    v = v.strip()
    return Decimal(v.replace('.', '').replace(',', '.')) if v else Decimal(0)


def download(url, dest, tries=7):
    wait = 120
    for i in range(tries):
        gap = _last_start[0] + PAUSE - time.time()
        if gap > 0:
            time.sleep(gap)
        _last_start[0] = time.time()
        part = dest + '.part'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            h = hashlib.sha256()
            n = 0
            with urllib.request.urlopen(req, timeout=600) as r, open(part, 'wb') as f:
                final = r.geturl()
                last_modified = r.headers.get('Last-Modified')
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    h.update(chunk)
                    n += len(chunk)
            if zipfile.is_zipfile(part):
                os.replace(part, dest)
                info = {'url': url, 'final_url': final, 'last_modified': last_modified, 'bytes': n,
                        'sha256': h.hexdigest(), 'read_on': time.strftime('%Y-%m-%d')}
                json.dump(info, open(dest + '.json', 'w'), indent=1)
                return info
            log(f'not a zip from {url} ({n} bytes, try {i + 1}), waiting {wait}s')
        except Exception as e:  # network errors and WAF refusals are retried
            log(f'error {e!r} on {url} (try {i + 1}), waiting {wait}s')
        if os.path.exists(part):
            os.remove(part)
        time.sleep(wait)
        wait *= 2
    raise SystemExit(f'gave up on {url}')


def member(z, part):
    names = [n for n in z.namelist() if part.lower() in n.lower()]
    if len(names) != 1:
        return None, names
    return io.TextIOWrapper(z.open(names[0]), encoding='latin-1', newline=''), names[0]


def read_cadastro(z):
    f, name = member(z, 'Cadastro')
    if f is None:
        return {'member': name, 'uf_column': None, 'uf_columns_in_header': []}, {}, {}, {}
    r = csv.reader(f, delimiter=';')
    h = next(r)
    hn = [norm(x) for x in h]
    idi = hn.index('IDSERVIDORPORTAL')
    ufcols = [x.strip() for x in h if re.search(r'(^|_)UF(_|$)', x.strip().upper())]
    if 'UF_EXERCICIO' in [x.strip().upper() for x in h]:
        ufname = 'UF_EXERCICIO'
    else:
        ufname = ufcols[0] if ufcols else None
    ufi = [x.strip().upper() for x in h].index(ufname.upper()) if ufname else None
    org_i = [hn.index(c) for c in ('CODORGEXERCICIO', 'ORGEXERCICIO') if c in hn]
    sit_i = hn.index('SITUACAOVINCULO') if 'SITUACAOVINCULO' in hn else None
    uf_of, df_org, df_sit = {}, collections.defaultdict(set), collections.defaultdict(set)
    invalid = collections.Counter()
    values = collections.Counter()
    rows = 0
    for row in r:
        rows += 1
        pid = row[idi]
        u = row[ufi].strip().upper() if ufi is not None else ''
        if ufi is not None:
            values[u] += 1
        if u not in UFS:
            if ufi is not None:
                invalid[u] += 1
            u = ''
        prev = uf_of.get(pid)
        if prev is None:
            uf_of[pid] = u
        elif u and prev != u:
            uf_of[pid] = u if prev == '' else '*'
        if u == 'DF':
            if org_i:
                df_org[pid].add(' '.join(row[i].strip() for i in org_i))
            if sit_i is not None:
                df_sit[pid].add(row[sit_i].strip())
    status = collections.Counter('conflicting' if v == '*' else ('missing' if v == '' else 'single') for v in uf_of.values())
    meta = {'member': name, 'header': h, 'uf_columns_in_header': ufcols, 'uf_column': ufname, 'rows': rows,
            'ids': len(uf_of), 'ids_by_uf_status': dict(status), 'uf_values_not_a_uf': dict(invalid.most_common(20)),
            'rows_by_uf_value': dict(values)}
    return meta, uf_of, df_org, df_sit


def load_map(ym):
    combined = {}
    found = []
    for cat in MAP_ORIGINS:
        p = os.path.join(MAPS, f'{cat}-{ym}.csv.gz')
        if not os.path.exists(p):
            return None, found
        found.append(cat)
        with gzip.open(p, 'rt', encoding='utf-8') as f:
            for line in f:
                pid, u = line.rstrip('\n').split(';')
                prev = combined.get(pid)
                if prev is None:
                    combined[pid] = u
                elif u and prev != u:
                    combined[pid] = u if prev == '' else '*'
    return combined, found


def summarize(zpath, cat, ym, supp):
    z = zipfile.ZipFile(zpath)
    summary = {'category': cat, 'ym': ym, 'members': z.namelist()}
    if supp:
        uf_of, maps = load_map(ym)
        if uf_of is None:
            raise RuntimeError(f'uf maps of {ym} missing')
        df_org, df_sit = {}, {}
        summary['cadastro'] = {'uf_column': 'UF_EXERCICIO of the same Id_SERVIDOR_PORTAL in the cadastro of ' +
                               ' and '.join(maps) + f' {ym}', 'uf_columns_in_header': []}
        has_uf = True
    else:
        meta, uf_of, df_org, df_sit = read_cadastro(z)
        summary['cadastro'] = meta
        has_uf = meta.get('uf_column') is not None
        if cat in MAP_ORIGINS:
            os.makedirs(MAPS, exist_ok=True)
            with gzip.open(os.path.join(MAPS, f'{cat}-{ym}.csv.gz'), 'wt', encoding='utf-8') as f:
                for pid, u in uf_of.items():
                    f.write(f'{pid};{u}\n')
    f, rname = member(z, 'Remuneracao')
    if f is None:
        f, rname = member(z, ym)  # supplementary zips hold a single csv
        if f is None:
            raise RuntimeError(f'no remuneracao member in {z.namelist()}')
    r = csv.reader(f, delimiter=';')
    h = next(r)
    hn = [norm(x) for x in h]
    idi = hn.index('IDSERVIDORPORTAL')
    money = [i for i, x in enumerate(h) if '(R$)' in x or '(U$)' in x or norm(x).startswith('VALOR')]
    names = [hn[i] for i in money]
    pos = {n: j for j, n in enumerate(names)}
    if supp:
        gross_j = [j for j, n in enumerate(names) if n.startswith('VALOR')]
        gross_uj = []
    else:
        gross_j = [pos[n] for n in GROSS_R if n in pos]
        gross_uj = [pos[usd(n)] for n in GROSS_R if usd(n) in pos]
        assert pos.get('REMUNERACAOBASICABRUTAR') is not None, names
    ded_j = [pos[n] for n in DED_R.values() if n in pos]
    net_j = pos.get(NET_R)
    buckets = {}
    people = collections.defaultdict(set)
    row_count = collections.Counter()
    df_org_acc = collections.defaultdict(lambda: [0] * len(names))
    df_org_people = collections.defaultdict(set)
    df_sit_acc = collections.defaultdict(lambda: [0] * len(names))
    df_sit_people = collections.defaultdict(set)
    ident_fail = 0
    ident_diff = 0
    rows = 0
    for row in r:
        rows += 1
        vals = [cents(row[i]) for i in money]
        pid = row[idi]
        if not has_uf:
            key = '_no_uf_column'
        else:
            u = uf_of.get(pid)
            key = '_not_in_cadastro' if u is None else ('_conflicting_uf' if u == '*' else ('_missing_uf' if u == '' else u))
        acc = buckets.get(key)
        if acc is None:
            acc = buckets[key] = [0] * len(names)
        for j, v in enumerate(vals):
            acc[j] += v
        row_count[key] += 1
        g = sum(vals[j] for j in gross_j)
        gu = sum(vals[j] for j in gross_uj)
        if g > 0 or gu > 0:
            people[key].add(pid)
        if net_j is not None:
            d = g + sum(vals[j] for j in ded_j) - vals[net_j]
            if d:
                ident_fail += 1
                ident_diff += d
        if key == 'DF':
            for src, acc2, ppl in ((df_org, df_org_acc, df_org_people), (df_sit, df_sit_acc, df_sit_people)):
                k = ' | '.join(sorted(src.get(pid, ()))) or '(not read)'
                a2 = acc2[k]
                for j, v in enumerate(vals):
                    a2[j] += v
                if g > 0 or gu > 0:
                    ppl[k].add(pid)
    # independent pass: plain Decimal sums of every money column over the whole file, no UF logic
    f2, _ = member(z, rname)
    r2 = csv.reader(f2, delimiter=';')
    next(r2)
    tot = [Decimal(0)] * len(money)
    rows2 = 0
    for row in r2:
        rows2 += 1
        for j, i in enumerate(money):
            tot[j] += dec(row[i])
    national = {}
    for n, d in zip(names, tot):
        c = d * 100
        assert c == c.to_integral_value(), (n, d)
        national[n] = int(c)
    summary['remuneracao'] = {'member': rname, 'header': h, 'money_columns': names, 'rows': rows, 'rows_second_pass': rows2,
                              'gross_columns': [names[j] for j in gross_j + gross_uj],
                              'deduction_columns': [names[j] for j in ded_j], 'net_column': names[net_j] if net_j is not None else None}
    summary['buckets'] = {k: {'sums': dict(zip(names, v)), 'people': len(people[k]), 'rows': row_count[k]} for k, v in buckets.items()}
    summary['national_independent'] = national
    summary['identity'] = {'rows_gross_minus_deductions_not_net': ident_fail, 'sum_diff_cents': ident_diff}
    summary['df_by_org_exercicio'] = {k: {'sums': dict(zip(names, v)), 'people': len(df_org_people[k])} for k, v in df_org_acc.items()}
    summary['df_by_situacao_vinculo'] = {k: {'sums': dict(zip(names, v)), 'people': len(df_sit_people[k])} for k, v in df_sit_acc.items()}
    return summary


def fetch(months, cats):
    os.makedirs(SUMS, exist_ok=True)
    jobs = [(ym, c, False) for ym in months for c in CORE if c[0] in cats]
    jobs += [(ym, c, True) for ym in months for c in SUPP if c[0] in cats]
    for ym, (cat, origin, _label), supp in jobs:
        spath = os.path.join(SUMS, f'{cat}-{ym}.json')
        if os.path.exists(spath):
            continue
        if supp and load_map(ym)[0] is None:
            log(f'skip {cat}-{ym}: uf maps of {ym} not ready')
            continue
        zpath = os.path.join(RAW, f'{cat}-{ym}.zip')
        url = f'{PAGE}/{ym}_{origin}'
        if os.path.exists(zpath) and zipfile.is_zipfile(zpath) and os.path.exists(zpath + '.json'):
            info = json.load(open(zpath + '.json'))
            log(f'reusing {zpath}')
        else:
            log(f'downloading {cat}-{ym}')
            info = download(url, zpath)
            log(f'got {info["bytes"]} bytes, last-modified {info["last_modified"]}')
        t0 = time.time()
        s = summarize(zpath, cat, ym, supp)
        s['origin'] = origin
        s['source'] = info
        tmp = spath + '.tmp'
        json.dump(s, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
        os.replace(tmp, spath)
        b = s['buckets']
        g = sum(v['sums'].get('REMUNERACAOBASICABRUTAR', 0) + sum(v['sums'].get(n, 0) for n in GROSS_R[1:]) for v in b.values())
        log(f'{cat}-{ym} summed in {time.time() - t0:.0f}s: rows {s["remuneracao"]["rows"]}, buckets {len(b)}, '
            f'gross R$ {g / 100:,.2f}, DF gross R$ {sum(b.get("DF", {}).get("sums", {}).get(n, 0) for n in GROSS_R) / 100:,.2f}, '
            f'identity fails {s["identity"]["rows_gross_minus_deductions_not_net"]}, uf column {s["cadastro"].get("uf_column")}')
        if ym not in KEEP_MONTHS:
            os.remove(zpath)
            os.remove(zpath + '.json')
    log('fetch pass complete')


# ---------------- build ----------------

def fields(sums, supp):
    """Named amounts in cents from a column-sum dict; None when the file has no such column."""
    def has(n):
        return n in sums
    if supp:
        g = sum(v for n, v in sums.items() if n.startswith('VALOR'))
        return {'gross': g, 'irrf': None, 'pension': None, 'pss': None, 'military_pension': None, 'health_fund': None,
                'housing_fee': None, 'other_deductions': None, 'net': None, 'indemnities': None}
    out = {'gross': sum(sums.get(n, 0) for n in GROSS_R)}
    for k, n in DED_R.items():
        out[k] = -sums[n] if has(n) else None
    out['pension'] = None if out['pss'] is None and out['military_pension'] is None else (out['pss'] or 0) + (out['military_pension'] or 0)
    out['net'] = sums[NET_R] if has(NET_R) else None
    out['indemnities'] = sums[INDEM_R] if has(INDEM_R) else None
    u = {'gross': sum(sums.get(usd(n), 0) for n in GROSS_R),
         'irrf': -sums.get(usd(DED_R['irrf']), 0),
         'pension': -sums.get(usd(DED_R['pss']), 0) - sums.get(usd(DED_R['military_pension']), 0),
         'net': sums.get(usd(NET_R), 0), 'indemnities': sums.get(usd(INDEM_R), 0)}
    out['usd'] = u
    return out


def add(a, b):
    for n, v in b.items():
        a[n] = a.get(n, 0) + v


def money(c):
    return None if c is None else round(c / 100, 2)


def render(f, people_by_month):
    out = {}
    if people_by_month is not None:
        ms = [p for p in people_by_month.values()]
        out['people_avg'] = int(round(sum(ms) / len(ms))) if ms else 0
    for k in ('gross', 'irrf', 'pension', 'pss', 'military_pension', 'health_fund', 'housing_fee', 'other_deductions', 'net', 'indemnities'):
        out[k] = money(f[k])
    if 'usd' in f:
        out['usd_not_converted'] = {k: money(v) for k, v in f['usd'].items()}
    return out


def run_check(summ):
    comps = 0
    misses = []
    for (cat, ym), s in summ.items():
        tot = {}
        for b in s['buckets'].values():
            add(tot, b['sums'])
        for n, v in s['national_independent'].items():
            comps += 1
            if tot.get(n, 0) != v:
                misses.append(f'{cat} {ym} {n}: buckets {tot.get(n, 0)} vs national {v} cents')
        if s['remuneracao']['rows'] != s['remuneracao']['rows_second_pass']:
            misses.append(f'{cat} {ym}: row counts differ')
    return comps, misses


def build():
    summ = {}
    for fn in sorted(os.listdir(SUMS)):
        if fn.endswith('.json'):
            s = json.load(open(os.path.join(SUMS, fn), encoding='utf-8'))
            summ[(s['category'], s['ym'])] = s
    allcats = CORE + SUPP
    supp_ids = {c[0] for c in SUPP}
    missing = [f'{c[0]} {ym}' for c in allcats for ym in MONTHS if (c[0], ym) not in summ]
    comps, misses = run_check(summ)
    # planted control: one cent added to one bucket must make the check fail
    ctrl = copy.deepcopy(summ)
    k0 = sorted(ctrl)[0]
    b0 = 'DF' if 'DF' in ctrl[k0]['buckets'] else sorted(ctrl[k0]['buckets'])[0]
    n0 = next(iter(ctrl[k0]['buckets'][b0]['sums']))
    ctrl[k0]['buckets'][b0]['sums'][n0] += 1
    _, cmiss = run_check(ctrl)
    assert len(cmiss) == 1, cmiss
    sources, categories, by_uf, national, df_detail, identity, summary = [], [], {}, {}, {}, {}, {}
    for cat, origin, label in allcats:
        months = {ym: summ[(cat, ym)] for ym in MONTHS if (cat, ym) in summ}
        if not months:
            continue
        supp = cat in supp_ids
        for ym, s in months.items():
            src = s['source']
            sources.append({'name': f'Portal da Transparencia, servidores, {origin}, {ym}', 'url': src['url'],
                            'final_url': src['final_url'], 'last_modified': src['last_modified'], 'bytes': src['bytes'],
                            'sha256': src['sha256'], 'read_on': src['read_on']})
        ufcols = sorted({str(s['cadastro'].get('uf_column')) for s in months.values()})
        first = next(iter(months.values()))
        categories.append({'id': cat, 'label': label, 'origin': origin, 'supplementary': supp,
                           'files': f'{PAGE}/<YYYYMM>_{origin} (zip members: ' + ', '.join(first['members']) + ')',
                           'uf_column': ufcols[0] if len(ufcols) == 1 else ufcols,
                           'uf_columns_in_cadastro_header': first['cadastro'].get('uf_columns_in_header'),
                           'months': [int(ym[4:]) for ym in months]})
        identity[cat] = {str(int(ym[4:])): s['identity'] for ym, s in months.items()}
        # per bucket
        keys = sorted({k for s in months.values() for k in s['buckets']})
        groups = collections.defaultdict(list)
        for k in keys:
            groups['no_uf' if k in NO_UF_KEYS else k].append(k)
        nat_cols, nat_people = {}, {}
        nat_month = {}
        for ym, s in months.items():
            add(nat_cols, s['national_independent'])
            nat_people[ym] = sum(b['people'] for b in s['buckets'].values())
            fm = fields(s['national_independent'], supp)
            nat_month[str(int(ym[4:]))] = dict(render(fm, None), people=nat_people[ym])
        national[cat] = dict(render(fields(nat_cols, supp), nat_people), by_month=nat_month)
        for g, ks in groups.items():
            cols, ppl, bm = {}, {}, {}
            for ym, s in months.items():
                mc = {}
                mp = 0
                for k in ks:
                    b = s['buckets'].get(k)
                    if b:
                        add(mc, b['sums'])
                        mp += b['people']
                if not mc:
                    continue
                add(cols, mc)
                ppl[ym] = mp
                bm[str(int(ym[4:]))] = dict(render(fields(mc, supp), None), people=mp)
            entry = dict(render(fields(cols, supp), ppl), by_month=bm)
            if g == 'no_uf':
                reasons = {}
                for k in ks:
                    rc, rp = {}, {}
                    for ym, s in months.items():
                        b = s['buckets'].get(k)
                        if b:
                            add(rc, b['sums'])
                            rp[ym] = b['people']
                    reasons[NO_UF_KEYS[k]] = render(fields(rc, supp), rp)
                entry['reasons'] = reasons
            by_uf.setdefault(g, {})[cat] = entry
        nat_g = fields(nat_cols, supp)['gross']
        located = 0
        for ym, s in months.items():
            for k, b in s['buckets'].items():
                if k not in NO_UF_KEYS:
                    located += fields(b['sums'], supp)['gross']
        summary[cat] = {'national_gross': money(nat_g), 'gross_with_uf': money(located), 'gross_no_uf': money(nat_g - located),
                        'share_with_uf': round(located / nat_g, 4) if nat_g else None,
                        'df_gross': by_uf.get('DF', {}).get(cat, {}).get('gross'), 'months': len(months)}
        # DF detail
        org, sit = {}, {}
        for ym, s in months.items():
            for src, dst in ((s['df_by_org_exercicio'], org), (s['df_by_situacao_vinculo'], sit)):
                for k, v in src.items():
                    d = dst.setdefault(k, {'cols': {}, 'people': {}})
                    add(d['cols'], v['sums'])
                    d['people'][ym] = v['people']
        if org or sit:
            def fmt(dct):
                rows = {k: dict(render(fields(v['cols'], supp), {ym: v['people'].get(ym, 0) for ym in months}))
                        for k, v in dct.items()}
                return dict(sorted(rows.items(), key=lambda kv: -(kv[1]['gross'] or 0)))
            df_detail[cat] = {'by_org_exercicio': fmt(org), 'by_situacao_vinculo': fmt(sit),
                              'note': 'annual sums of the people placed in DF; people_avg over the 12 months (0 in months absent)'}
    uf_order = sorted(k for k in by_uf if k != 'no_uf') + (['no_uf'] if 'no_uf' in by_uf else [])
    by_uf = {k: by_uf[k] for k in uf_order}
    ok = not misses and not missing
    details = (f'{comps} comparisons (every money column of every category and month: sum of the UF buckets plus the '
               f'no_uf buckets, integer cents from the per-row pass, against an independent Decimal pass over the whole '
               f'Remuneracao file with no UF logic): {len(misses)} misses. Planted control: 1 cent added to {b0} '
               f'{k0[0]} {k0[1]} {n0} gave {len(cmiss)} miss ({cmiss[0]}).')
    if missing:
        details += f' Months not collected: {", ".join(missing)}.'
    out = {
        'year': YEAR,
        'generated_on': time.strftime('%Y-%m-%d'),
        'generated_by': 'docs/superpowers/tools/collect-federal-payroll-by-uf.py',
        'method': {
            'gross': 'sum of the R$ columns ' + ', '.join(GROSS_R) + ' (abate-teto is negative in the file, so gross is after the cap)',
            'irrf': 'IRRF (R$), sign flipped', 'pss': 'PSS/RPGS (R$), sign flipped', 'military_pension': 'PENSAO MILITAR (R$), sign flipped',
            'pension': 'pss + military_pension',
            'net': 'REMUNERACAO APOS DEDUCOES OBRIGATORIAS (R$), the file\'s own column',
            'indemnities': 'TOTAL DE VERBAS INDENIZATORIAS (R$): paid but not salary, outside gross and net',
            'usd_not_converted': 'the U$ columns summed in US dollars, never converted',
            'uf': 'distinct valid UF codes of the person\'s cadastro rows in the same zip: one UF places the person there; none or '
                  'two or more go to no_uf (reasons missing_uf, conflicting_uf); a Remuneracao Id absent from the cadastro goes to '
                  'no_uf (not_in_cadastro); a file with no UF column goes to no_uf (no_uf_column). Nothing is allocated.',
            'people': 'distinct Id_SERVIDOR_PORTAL with gross R$ or U$ above zero in the month; people_avg = mean of the months',
        },
        'sources': [{'name': 'Portal da Transparencia, download de dados, servidores (page listing the files)', 'url': PAGE,
                     'read_on': '2026-10-21'}] + sources,
        'categories': categories,
        'summary': summary,
        'by_uf': by_uf,
        'national': national,
        'check': {'uf_plus_no_uf_equals_national': ok, 'details': details, 'misses': misses[:50],
                  'net_identity_by_month': identity},
        'df_detail': df_detail,
        'not_found': NOT_FOUND,
    }
    tmp = OUT + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(json.dumps(summary, indent=1))
    print(details)


NOT_FOUND = [
    {'what': 'UF of active military (Militares)',
     'why': 'the cadastro has a UF_EXERCICIO column but every row carries -1 (345.468 of 345.468 rows in 2024-01, same check every month in the summaries)',
     'tried': 'Portal Militares monthly zips 2024-01 to 2024-12, cadastro column UF_EXERCICIO; prior research: SIAFI pays them through three national units'},
    {'what': 'UF of reserve and retired military, civil retirees, and all pensioners (Reserva_Reforma_Militares, Aposentados_SIAPE, '
             'Aposentados_BACEN, Pensionistas_SIAPE, Pensionistas_BACEN, Pensionistas_DEFESA)',
     'why': 'their cadastro has no UF column at all (no residence, no UF of a unit); only the name of the last organisation of lotacao '
            '(of the instituidor, for pensions), which says nothing about where the person lives',
     'tried': 'every column of the cadastro headers of the 2024 zips (listed in categories[].uf_columns_in_cadastro_header)'},
    {'what': 'UF of Banco Central staff (Servidores_BACEN)',
     'why': 'UF_EXERCICIO is -1 in every cadastro row (4.560 of 4.560 in 2024-01)',
     'tried': 'Portal Servidores_BACEN monthly zips 2024'},
    {'what': 'UF of the SIAPE civil servants whose cadastro rows carry UF_EXERCICIO -1 (no_uf.civil_servants_siape, reason missing_uf)',
     'why': 'the file gives no UF for them (186.916 of 598.999 ids in 2024-01; mostly Ministerio da Educacao universities and institutes, '
            '"Sem informacao", Presidencia); their ORG_EXERCICIO names often name a state, but placing people by an organisation name '
            'is an inference and was not done',
     'tried': 'UF_EXERCICIO of every cadastro row of the person; a future step could join COD_ORG_EXERCICIO to an official register of '
              'organisations with their UF (SIORG), stated as a rule before use'},
    {'what': 'Legislative, Judiciary, MPU, DPU payrolls and the FCDF personnel (PCDF, PMDF, CBMDF)',
     'why': 'not in the Portal servidores files, which cover the Executive (SIAPE), the Banco Central and the Armed Forces; no PCDF, '
            'PMDF or CBMDF organisation appears among the DF organisations of exercise in SIAPE 2024-01',
     'tried': 'download page origins (11 for 2024) and the DF ORG_EXERCICIO list of SIAPE 2024-01'},
]

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0] not in ('fetch', 'build'):
        raise SystemExit('usage: collect-federal-payroll-by-uf.py fetch [--months 202401,202402] [--cats a,b] | build')
    months, cats = MONTHS, {c[0] for c in CORE + SUPP}
    if '--months' in args:
        months = args[args.index('--months') + 1].split(',')
    if '--cats' in args:
        cats = set(args[args.index('--cats') + 1].split(','))
    if args[0] == 'fetch':
        fetch(months, cats)
    else:
        build()
