"""Federal payments for the dualling (duplicação) of the BR-470/SC, by year, from the monthly
"Execução da despesa" files of the Portal da Transparência (CGU). No API key.

Source: https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/AAAAMM
(redirects to dadosabertos-download.cgu.gov.br). Each monthly file carries the amount paid in the month
(`Valor Pago (R$)`) and the restos a pagar (commitments carried over from earlier years) paid in the month
(`Valor Restos a Pagar Pagos (R$)`).

Filter: órgão DNIT (39252) and `Nome Ação`, `Nome Subtítulo`, `Nome Localizador` or `Plano Orçamentário` citing the BR-470.
Output: JSON with the sum by year, ação and localizador.
Usage: python3 br470_payments.py <workdir> <out.json> [first_year] [last_year]
Each ZIP is downloaded, read as a stream and deleted, so it does not take up disk space.
"""
import csv, io, json, os, re, subprocess, sys, zipfile, collections, time

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
BASE = 'https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/despesas-execucao/{ym}_Despesas.zip'
PORTAL = 'https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/{ym}'
PAT = re.compile(r'BR[\s\-/]*470', re.I)


def num(x):
    return float(x.replace('.', '').replace(',', '.')) if x else 0.0


def month(ym, work):
    zp = os.path.join(work, f'{ym}.zip')
    # curl with browser headers: the CGU CDN blocks clients without them (HTTP 403/405).
    for attempt in range(3):
        subprocess.run(['curl', '-sS', '-L', '-m', '600', '-A', UA, '-H', 'Accept: */*', '-o', zp, PORTAL.format(ym=ym)])
        if os.path.exists(zp) and zipfile.is_zipfile(zp):
            break
        print('retry', ym, flush=True)
        time.sleep(60)
    else:
        return None
    time.sleep(2)
    rows = []
    z = zipfile.ZipFile(zp)
    rd = csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding='latin1'), delimiter=';')
    h = next(rd)
    ix = {c: i for i, c in enumerate(h)}
    for row in rd:
        if row[ix['Código Órgão Subordinado']] != '39252' and row[ix['Código Órgão Superior']] != '39000':
            continue
        acao, loc = row[ix['Nome Ação']], row[ix['Nome Localizador']]
        sub, po = row[ix['Nome Subtítulo']], row[ix['Plano Orçamentário']]
        if not (PAT.search(acao) or PAT.search(loc) or PAT.search(sub) or PAT.search(po)):
            continue
        if row[ix['Código Órgão Subordinado']] != '39252':
            continue
        rows.append({
            'ym': ym, 'uf': row[ix['UF']], 'acao': row[ix['Código Ação']], 'acao_nome': acao,
            'localizador': row[ix['Código Localizador']], 'localizador_nome': loc, 'subtitulo': sub, 'po': po,
            'grupo': row[ix['Código Grupo de Despesa']],
            'pago': num(row[ix['Valor Pago (R$)']]),
            'rp_pago': num(row[ix['Valor Restos a Pagar Pagos (R$)']]),
            'liquidado': num(row[ix['Valor Liquidado (R$)']]),
            'empenhado': num(row[ix['Valor Empenhado (R$)']]),
        })
    z.close()
    os.remove(zp)
    return rows


def main(work, out, y0=2013, y1=2026):
    os.makedirs(work, exist_ok=True)
    allrows, missing = [], []
    for y in range(int(y0), int(y1) + 1):
        for m in range(1, 13):
            ym = f'{y}{m:02d}'
            r = month(ym, work)
            if r is None:
                missing.append(ym)
                continue
            allrows += r
            print(ym, len(r), flush=True)
    # second pass: the CGU CDN refuses bursts; months that failed usually download after a pause
    for ym in list(missing):
        time.sleep(90)
        r = month(ym, work)
        if r is not None:
            missing.remove(ym)
            allrows += r
            print('retry ok', ym, len(r), flush=True)
    agg = collections.defaultdict(lambda: {'pago': 0.0, 'rp_pago': 0.0, 'liquidado': 0.0, 'empenhado': 0.0})
    for r in allrows:
        k = (r['ym'][:4], r['uf'], r['acao'], r['acao_nome'], r['localizador'], r['localizador_nome'], r['subtitulo'], r['po'])
        for f in ('pago', 'rp_pago', 'liquidado', 'empenhado'):
            agg[k][f] += r[f]
    res = {'source': PORTAL, 'file_url_pattern': BASE, 'filter': 'Código Órgão Subordinado = 39252 (DNIT) e "BR-470" em Nome Ação, Nome Subtítulo, Nome Localizador ou Plano Orçamentário',
           'months_missing': missing,
           'by_year': [dict(zip(('year', 'uf', 'acao', 'acao_nome', 'localizador', 'localizador_nome', 'subtitulo', 'plano_orcamentario'), k), **{f: round(v, 2) for f, v in vals.items()})
                       for k, vals in sorted(agg.items())]}
    json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
    print('wrote', out, len(res['by_year']))


if __name__ == '__main__':
    main(*sys.argv[1:])
