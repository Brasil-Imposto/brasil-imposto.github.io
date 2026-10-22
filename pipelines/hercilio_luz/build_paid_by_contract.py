"""Total actually paid on the Ponte Hercilio Luz restoration, read per contract (not per company).

Source: SICOP statement of each contract on the SC transparency portal API (contratoResumoFinanceiro + contratoPagamento).
NUTITULO of each contract comes from the SIGEF/SICOP contract register (dados.sc.gov.br, column NUTITULO), read 2026-10-05.
Statements are fetched into memory (nothing written to disk) unless --from-dir points to saved copies.

Two passes must agree to the cent: pass 1 = integer cents of the yearly summary (vlpago); pass 2 = Decimal sum of the payment
lines. A planted R$ 0,01 control must make the check fail. Nothing is written if the check fails.

Audit of 2026-10-06 (cases, A1 and A2): the first stage of the restoration, contract PJ 015/2006 (Consórcio Roca-TEC,
2006 to 2009), is in neither the Portal nor the SIGEF register, but the ALESC CPI final report prints its payment tables
(Apêndice A, one per member of the consortium) and its signed value (item 6.11). The total paid 2006 to 2020 is read
contract by contract (D95): the ten contracts that start in 2011 or later from the Portal extracts, PJ-170/2006 (two
lines) and PJ-264/2008 from their CPI tables (read with the parser of pipelines/complete_totals/hercilio_luz_supervision_cpi.py),
and PJ 015/2006 from its two CPI tables. Pass 1 sums payment lines in Decimal; pass 2 starts from the Portal "vlpago"
summaries in integer cents and swaps in the CPI "PGTOS NO MÊS" columns; both must agree, and each CPI table must equal its
printed TOTAL. The initial contract of the work is the signed value of the first contracts (2006 to 2008), never the
sum of a rescinded contract and the one that replaced it. --control also adds R$ 0,01 to the first PJ 015/2006 line.
The CPI PDF (9 MB) is read in a temporary folder deleted at once, unless --cpi-pdf points to a local copy.
Usage: python3 pipelines/hercilio_luz/build_paid_by_contract.py [--from-dir DIR] [--cpi-pdf FILE] [--control]
"""
import json, re, shutil, subprocess, sys, tempfile, urllib.request
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data' / 'hercilio-luz-paid-by-contract.json'
API = 'https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro[]='
REGISTER = 'https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/ff7c3cac-3e38-4801-9fd8-e4ccb69ca31d/download/contratos.csv'
TCE_URL = 'http://consulta.tce.sc.gov.br/relatoriosdecisao/relatoriotecnico/3728501.PDF'
COLLECTED = '2026-10-05'
NUTITULO = {
    'PJ-00170/2006': '53682', 'PJ-00170/2006/PROSUL': '53663', 'PJ-00264/2008': '70204', 'PJ-00204/2014': '88906',
    'PJ-00012/2015': '89257', 'PJ-00143/2015': '90666', 'PJ-00001/2016/FARES': '91908', 'PJ-00056/2016': '91858',
    'PJ-00093/2016': '92132', 'PJ-00009/2019': '97701', 'CT-00006/2019': '98298', 'PJ-00060/2019': '98300',
    'CT-00026/2019': '98679', 'DL-00001/2618-2019': '98648',
}
TCE_CUMULATIVE = '38921239.05'      # TCE-SC DLC 462/2012, item 2.6, accumulated paid on PJ-00264/2008 up to May 2012
TCE_CUT = '2012-05-31'
CPI_URL = 'https://portalelegis.alesc.sc.gov.br/proposicoes/legado/RQC-0016.6-2019/anexo/10766/visualizar'
CPI_DOC = 'Relatório final da CPI da Ponte Hercílio Luz (Alesc)'
EN_DASH = chr(0x2013)  # the PDF table titles use an en dash
FIRST_STAGE = [('TEC', f'Contrato PJ 015/2006 {EN_DASH} TEC'), ('Roca', f'Contrato PJ 015/2006 {EN_DASH} Roca')]
CPI_TABLE_OF = {'PJ-00170/2006': 'Concremat', 'PJ-00170/2006/PROSUL': 'Prosul', 'PJ-00264/2008': 'Florianopolis Monumento'}
MONEY = re.compile(r'^\d{1,3}(\.\d{3})*,\d{2}$|^0$')
DMY = re.compile(r'^\d{2}/\d{2}/\d{4}$')


def cents(s):
    """Pass 1 arithmetic: exact integer cents from the portal's decimal string, no float, no Decimal."""
    s = s.strip(); neg = s.startswith('-'); s = s.lstrip('-')
    whole, _, frac = s.partition('.')
    v = int(whole) * 100 + int((frac + '00')[:2])
    if not (len(frac) <= 2):
        raise SystemExit(s)
    return -v if neg else v


def brl(c):
    return round(c / 100, 2)


def pt(v):
    s = f'{v:,.2f}'
    return 'R$ ' + s.replace(',', '_').replace('.', ',').replace('_', '.')


def brl_dec(tok):
    return Decimal(tok.replace('.', '').replace(',', '.')) if tok != '0' else Decimal(0)


def cpi_text(pdf_path=None):
    """Text of the CPI final report; the PDF is downloaded into a temporary folder deleted at once."""
    folder = tempfile.mkdtemp(prefix='cpi_')
    try:
        pdf = pdf_path or f'{folder}/cpi.pdf'
        if not pdf_path:
            req = urllib.request.Request(CPI_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=600) as resp, open(pdf, 'wb') as out:
                out.write(resp.read())
        subprocess.run(['pdftotext', '-layout', pdf, f'{folder}/cpi.txt'], check=True)
        return open(f'{folder}/cpi.txt', encoding='utf-8', errors='replace').read()
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def first_stage_table(text, title):
    """One CPI table of PJ 015/2006: per measurement, VALOR MEDIDO (the third money column) and the payment date; the
    PGTOS NO MÊS column in integer cents; the TOTAL line."""
    rows, month_cents, total = [], 0, None
    for line in text[text.index(title) + len(title):].splitlines():
        tok = line.split()
        if tok[:1] in (['TOTAL'], ['VALOR']) and 'TOTAL' in tok[:2]:
            total = brl_dec([x for x in tok if MONEY.match(x)][0])
            break
        if len(tok) < 7 or not tok[0].isdigit() or tok[2] != 'a' or not DMY.match(tok[1]) or not DMY.match(tok[3]):
            continue
        rest = tok[7:]
        paid_on = rest[0] if rest and DMY.match(rest[0]) else None
        extra = [x for x in (rest[1:] if paid_on else rest) if MONEY.match(x)]
        if len(extra) == 2:
            month_cents += cents(f'{brl_dec(extra[0]):.2f}')
        rows.append({'measurement': int(tok[0]), 'measured': brl_dec(tok[6]), 'paid_on': paid_on})
    return rows, month_cents, total


def load(t, from_dir):
    if from_dir:
        return json.load(open(Path(from_dir) / f'x_{t}.json'))
    req = urllib.request.Request(API + t, headers={'Referer': 'https://www.transparencia.sc.gov.br/'})
    return json.load(urllib.request.urlopen(req, timeout=120))


def main():
    args = sys.argv[1:]
    from_dir = args[args.index('--from-dir') + 1] if '--from-dir' in args else None
    cpi_pdf = args[args.index('--cpi-pdf') + 1] if '--cpi-pdf' in args else None
    control = '--control' in args
    base = json.load(open(ROOT / 'data' / 'hercilio-luz.json'))
    rows = [c for c in base['contracts'] if c['group'] == 'restoration_2006_2019']
    related = [c for c in base['contracts'] if c['group'] != 'restoration_2006_2019']
    if not (len(rows) == 13):
        raise SystemExit(len(rows))

    contracts, related_out, problems = [], [], []
    pass1_total = 0
    pass2_total = Decimal('0')
    stmt_by_number = {}
    net_dec, net_cents = {}, {}  # per contract: payment lines in Decimal, and the yearly vlpago summaries in cents
    for c in rows + related:
        t = NUTITULO[c['number']]
        e = load(t, from_dir)
        stmt_by_number[c['number']] = e
        if not (e['contrato']['contrato'] == c['number']):
            raise SystemExit((e['contrato']['contrato'], c['number']))
        lines = e['contratoPagamento']
        res = e['contratoResumoFinanceiro']
        p1_year = defaultdict(int)
        for r in res:
            p1_year[r['ano']] += cents(r['vlpago'])
        p2_year = defaultdict(Decimal)
        for i, p in enumerate(lines):
            v = Decimal(p['valor'])
            if control and c['number'] == 'PJ-00056/2016' and i == 0:
                v += Decimal('0.01')
            p2_year[p['ano']] += v
        for y in sorted(set(p1_year) | set(p2_year)):
            if Decimal(p1_year.get(y, 0)) / 100 != p2_year.get(y, Decimal('0')):
                problems.append(f"{c['number']} {y}: summary {brl(p1_year.get(y, 0))} vs lines {p2_year.get(y)}")
        pos = sum((Decimal(p['valor']) for p in lines if Decimal(p['valor']) > 0), Decimal('0'))
        neg = sum((Decimal(p['valor']) for p in lines if Decimal(p['valor']) < 0), Decimal('0'))
        dates = sorted(p['dtreferencia'][:10] for p in lines if Decimal(p['valor']) > 0)
        net1 = sum(p1_year.values())
        net2 = sum(p2_year.values(), Decimal('0'))
        net_dec[c['number']], net_cents[c['number']] = net2, net1
        med = e['contratoMedicoes']
        item = {
            'number': c['number'], 'company': c['contractor_name_in_record'], 'cnpj': c['contractor_cnpj'], 'nutitulo': t,
            'paid_brl': float(pos), 'reversed_brl': float(-neg), 'net_paid_brl': brl(net1),
            'first_payment': dates[0] if dates else None, 'last_payment': dates[-1] if dates else None,
            'years_in_portal': sorted(int(y) for y, v in p1_year.items() if v != 0),
            'by_year': [{'year': int(y), 'net_paid_brl': brl(p1_year[y])} for y in sorted(p1_year)],
            'payment_lines': len(lines),
            'value_current_brl': c['value_current_brl'],
            'final_measured_accumulated_brl': float(Decimal(med[-1]['vlacumuladototal'])) if med else None,
            'source_url': API + t,
        }
        if c in rows:
            contracts.append(item)
            pass1_total += net1
            pass2_total += net2
        else:
            item['object'] = ' '.join(e['contrato']['objeto'].split())
            item['note'] = 'Registro ligado à ponte fora dos 13 contratos (grupo "related_record_outside_original_filter" em data/hercilio-luz.json). Não entra no total.'
            related_out.append(item)

    # Pre-portal: PJ-00264/2008, TCE-SC cumulative to May 2012 replaces the portal's Jan 2011 to May 2012 lines.
    e = stmt_by_number['PJ-00264/2008']
    upto_c = sum(cents(p['valor']) for p in e['contratoPagamento'] if p['dtreferencia'][:10] <= TCE_CUT)
    after_c = sum(cents(p['valor']) for p in e['contratoPagamento'] if p['dtreferencia'][:10] > TCE_CUT)
    tce_c = cents(TCE_CUMULATIVE)
    pre_c = tce_c - upto_c
    final_med_c = cents(e['contratoMedicoes'][-1]['vlacumuladototal'])
    med_at_cut = [m for m in e['contratoMedicoes'] if cents(m['vlacumuladototal']) == tce_c]
    upto_d = sum((Decimal(p['valor']) for p in e['contratoPagamento'] if p['dtreferencia'][:10] <= TCE_CUT), Decimal('0'))
    pre_d = Decimal(TCE_CUMULATIVE) - upto_d
    cross_ok = tce_c + after_c == final_med_c == cents(f"{Decimal(str(rows[2]['value_current_brl'])):.2f}")
    if not cross_ok:
        problems.append('PJ-00264/2008: TCE cumulative + portal after May 2012 != final measurement / current value')
    supervision = []
    for num in ('PJ-00170/2006', 'PJ-00170/2006/PROSUL'):
        m = [x for x in stmt_by_number[num]['contratoMedicoes'] if x['periodomedicaotermino'][:10] <= '2010-12-31']
        supervision.append({'number': num, 'measurement': m[-1]['descricao'], 'period_end': m[-1]['periodomedicaotermino'][:10],
                            'measured_accumulated_brl': float(Decimal(m[-1]['vlacumuladototal']))})
    pre_portal = [
        {
            'number': 'PJ-00264/2008', 'company': 'Consórcio Florianópolis Monumento', 'cnpj': '10769406000197',
            'official_figure_brl': float(Decimal(TCE_CUMULATIVE)),
            'official_figure_covers': 'Pago acumulado no contrato desde 2008 até o último pagamento, em maio de 2012 (medições até março de 2012).',
            'quote': 'Conforme extrato do Sistema Integrado de Controle de Obras Públicas - SICOP da Administração Estadual, atualizado em julho de 2012, o último pagamento ocorreu em maio do corrente ano, referente aos meses de janeiro a março de 2012, acumulando R$ 38.921.239,05',
            'source': {'doc': 'TCE-SC, Relatório DLC 462/2012 (processo RLA-12/00285490), item 2.6', 'url': TCE_URL},
            'portal_paid_2011_01_to_2012_05_brl': brl(upto_c),
            'portal_paid_after_2012_05_brl': brl(after_c),
            'pre_2011_paid_brl_computed': brl(pre_c),
            'pre_2011_note': 'Diferença calculada entre dois números oficiais (o acumulado do TCE-SC até maio de 2012 menos as linhas de pagamento do Portal de janeiro de 2011 a maio de 2012). Não é estimativa, mas nenhum documento imprime este valor.',
            'included_in_total': True,
            'cross_checks': [
                f"O acumulado do TCE-SC é igual, ao centavo, ao acumulado da {med_at_cut[0]['descricao'] if med_at_cut else '?'} do SICOP (período até {med_at_cut[0]['periodomedicaotermino'][:10] if med_at_cut else '?'}).",
                f"Acumulado do TCE-SC + pagamentos do Portal depois de maio de 2012 = {brl(tce_c + after_c)}; medição final acumulada no SICOP = {brl(final_med_c)}; valor atual do contrato no registro = {rows[2]['value_current_brl']}. {'Iguais ao centavo.' if cross_ok else 'DIFERENTES.'}",
                'No extrato do Portal não há pagamento entre 29/05/2012 e 17/08/2012, o que bate com "último pagamento em maio" num extrato atualizado em julho de 2012.',
            ],
        },
        {
            'number': 'PJ-00170/2006 e PJ-00170/2006/PROSUL', 'company': 'Consórcio Prosul-Concremat (uma linha por empresa no registro)',
            'official_figure_brl': None,
            'official_figure_covers': 'Nenhum número oficial de valor PAGO de 2006 a 2010 foi encontrado. O Relatório DLC 462/2012 do TCE-SC dá valor inicial, aditivos e o custo mensal da supervisão (R$ 117.616,86, base abril de 2012), não o pago acumulado.',
            'measured_up_to_2010_for_context_only': supervision,
            'measured_note': 'Valor MEDIDO acumulado no SICOP até dezembro de 2010; medido não é pago. Só contexto, fora do total.',
            'source': {'doc': 'Extrato SICOP dos contratos (contratoMedicoes) e TCE-SC DLC 462/2012, item 2.7', 'url': API + '53682'},
            'included_in_total': False,
        },
    ]

    # Creditor cross-check (company totals from data/hercilio-luz.json) for company-years with only bridge contracts.
    by_cnpj_year = defaultdict(int)
    for c in contracts + related_out:
        for y in c['by_year']:
            by_cnpj_year[(c['cnpj'], y['year'])] += round(y['net_paid_brl'] * 100)
    creditor = []
    for comp in base['payments']['companies']:
        for y in comp['by_year']:
            vb = y['all_units'].get('vlbruto')
            if vb is None:
                continue
            k = (comp['cnpj'], y['year'])
            if k in by_cnpj_year:
                creditor.append({'cnpj': comp['cnpj'], 'year': y['year'], 'creditor_gross_brl': round(vb, 2),
                                 'contracts_net_paid_brl': brl(by_cnpj_year[k]), 'equal': round(vb * 100) == by_cnpj_year[k]})

    total_c = pass1_total + pre_c
    total_d = pass2_total + pre_d
    match = (Decimal(pass1_total) / 100 == pass2_total) and (Decimal(total_c) / 100 == total_d) and not problems
    print('pass1 portal total', brl(pass1_total), '| pass2', pass2_total, '| with pre-portal', brl(total_c), total_d)

    # ---------- First stage PJ 015/2006 and the total paid 2006 to 2020, contract by contract (audit of 2026-10-06, A1 and A2)
    text = cpi_text(cpi_pdf)
    flat = ' '.join(text.split())
    sys.path.insert(0, str(ROOT / 'pipelines' / 'complete_totals'))
    from hercilio_luz_supervision_cpi import parse as cpi_parse, SECTIONS as CPI_SECTIONS
    cpi_problems = []

    def quote(q):
        if q not in flat:
            cpi_problems.append(f'quote not found in the CPI report: {q}')
        return q
    members, fs_lines, fs_cents = [], Decimal(0), 0
    for name, title in FIRST_STAGE:
        rows_fs, month_cents, total_fs = first_stage_table(text, title)
        if control and name == 'TEC':
            rows_fs[0]['measured'] += Decimal('0.01')
        measured = sum((r['measured'] for r in rows_fs), Decimal(0))
        if [r['measurement'] for r in rows_fs] != list(range(1, 43)):
            cpi_problems.append(f'PJ 015/2006 {name}: the measurements are not 1 to 42')
        if measured != total_fs:
            cpi_problems.append(f'PJ 015/2006 {name}: VALOR MEDIDO column {measured} != TOTAL {total_fs}')
        if Decimal(month_cents) / 100 != total_fs:
            cpi_problems.append(f'PJ 015/2006 {name}: PGTOS NO MÊS column {Decimal(month_cents) / 100} != TOTAL {total_fs}')
        paid_on = sorted(f'{d[6:]}-{d[3:5]}-{d[:2]}' for d in (r['paid_on'] for r in rows_fs) if d)
        members.append({'member': name, 'paid_brl': float(total_fs), 'measurements': len(rows_fs),
                        'first_payment': paid_on[0], 'last_payment': paid_on[-1],
                        'table': f'Apêndice A, tabela "Contrato PJ 015/2006 - {name}" (linha TOTAL)'})
        fs_lines += measured
        fs_cents += month_cents
    i611 = flat.index('6.11. Contrato PJ 015/2006 firmado entre o DEINFRA')
    v015 = re.search(r'firmada no valor original de R\$ ([\d.]+,\d{2})', flat[i611:]).group(1)
    v015_amended = re.search(r'totalizando um valor histórico contratado de R\$ ([\d.]+,\d{2})', flat[i611:]).group(1)
    signed_015 = quote('Em 16 de fevereiro de 2006 foi assinado o Contrato PJ 015/2006')
    i612 = flat.index('6.12. Contrato PJ 170/2006 firmado entre o DEINFRA')
    v170 = re.search(r'valor histórico de R\$ ([\d.]+,\d{2})', flat[i612:]).group(1)
    v170_register = sum(Decimal(str(c['value_original_brl'])) for c in rows if c['number'].startswith('PJ-00170/2006'))
    if brl_dec(v170) != v170_register:
        cpi_problems.append(f'PJ-170/2006: CPI historic value {v170} != register lines {v170_register}')
    reg = {c['number']: c for c in rows}
    v264 = Decimal(str(reg['PJ-00264/2008']['value_original_brl']))
    if Decimal(stmt_by_number['PJ-00264/2008']['contrato']['valororiginal']) != v264:
        cpi_problems.append('PJ-00264/2008: SICOP valororiginal differs from the register')
    cpi_tables = {}
    for name, start, end, _ in CPI_SECTIONS:
        pays, month_col, tot = cpi_parse(text, start, end)
        lines_sum = sum((x['value'] for x in pays), Decimal(0))
        if lines_sum != tot or month_col != tot:
            cpi_problems.append(f'CPI table {name}: lines {lines_sum}, PGTOS NO MÊS {month_col}, TOTAL {tot}')
        cpi_tables[name] = {'lines': lines_sum, 'month_column': month_col, 'total': tot}
    # pass 1: payment lines (Portal lines, CPI lines, PJ 015/2006 measured column), Decimal, contract by contract
    full_1 = fs_lines + sum((cpi_tables[CPI_TABLE_OF[c['number']]]['lines'] if c['number'] in CPI_TABLE_OF else net_dec[c['number']]
                             for c in rows), Decimal(0))
    # pass 2: integer cents, the Portal vlpago grand total with the three pre-2011 contracts swapped for the CPI columns
    full_2 = pass1_total + fs_cents + sum(cents(f"{cpi_tables[CPI_TABLE_OF[n]]['month_column']:.2f}") - net_cents[n] for n in CPI_TABLE_OF)
    full_match = Decimal(full_2) / 100 == full_1 and not cpi_problems
    fs_total_c = cents(f'{sum((Decimal(str(m["paid_brl"])) for m in members), Decimal(0)):.2f}')
    parts = {'ten_contracts_portal': brl(sum(net_cents[c['number']] for c in rows if c['number'] not in CPI_TABLE_OF)),
             'PJ-170/2006_cpi': float(cpi_tables['Prosul']['total'] + cpi_tables['Concremat']['total']),
             'PJ-264/2008_cpi': float(cpi_tables['Florianopolis Monumento']['total']),
             'PJ-015/2006_cpi': brl(fs_total_c)}
    initial = [
        {'number': 'PJ 015/2006', 'what': 'restauração, etapa 1 (viadutos de acesso), Consórcio Roca-TEC', 'signed_on': '2006-02-16',
         'value_original_brl': float(brl_dec(v015)),
         'source': {'doc': CPI_DOC + ', item 6.11', 'url': CPI_URL, 'quote': quote(f'firmada no valor original de R$ {v015}')}},
        {'number': 'PJ-00170/2006', 'what': 'supervisão da restauração, Consórcio Prosul-Concremat (duas linhas no registro do Estado, uma por empresa)',
         'signed_on': reg['PJ-00170/2006']['signed_on'], 'value_original_brl': float(v170_register),
         'source': {'doc': CPI_DOC + ', item 6.12, e registro de contratos SIGEF/SICOP', 'url': CPI_URL, 'quote': quote(f'valor histórico de R$ {v170}')}},
        {'number': 'PJ-00264/2008', 'what': 'restauração, etapa 2, Consórcio Florianópolis Monumento', 'signed_on': reg['PJ-00264/2008']['signed_on'],
         'value_original_brl': float(v264),
         'note': f"Rescindido (SICOP: valor rescindido {pt(float(Decimal(stmt_by_number['PJ-00264/2008']['contrato']['valorrescindido'])))}). A obra foi contratada de novo em 2016 (PJ-00056/2016, {pt(reg['PJ-00056/2016']['value_original_brl'])} assinados), que não entra no contrato inicial: somar os dois contaria a mesma obra duas vezes.",
         'source': {'doc': 'Extrato SICOP do contrato, campo valororiginal', 'url': API + NUTITULO['PJ-00264/2008']}},
    ]
    initial_c = sum(cents(f"{Decimal(str(x['value_original_brl'])):.2f}") for x in initial)
    print('first stage PJ 015/2006', [(m['member'], m['paid_brl']) for m in members], '| total 2006-2020 pass 1', full_1, '| pass 2', brl(full_2),
          '| initial contracts 2006-2008', brl(initial_c))
    match = match and full_match
    for p in problems + cpi_problems:
        print('PROBLEM', p)
    if control:
        print('CONTROL: check', 'FAILED as expected' if not match else 'PASSED (control broken!)')
        sys.exit(0 if not match else 1)
    if not match:
        print('CHECK FAILED, nothing written'); sys.exit(1)

    out = {
        'collected_on': date.today().isoformat(),
        'source': {'doc': 'Extrato SICOP de cada contrato ("contratoResumoFinanceiro" e "contratoPagamento"), Portal da Transparência do Poder Executivo de SC',
                   'api': API + '<NUTITULO>',
                   'nutitulo_from': {'doc': 'Registro de contratos SIGEF/SICOP, CGE-SC, coluna NUTITULO', 'url': REGISTER, 'read_on': COLLECTED},
                   'script': 'pipelines/hercilio_luz/build_paid_by_contract.py'},
        'method': [
            'Pago por contrato = soma de todas as linhas de "contratoPagamento" do extrato (despesa paga, retenções de ISS, IRRF, INSS e caução, e estornos com sinal negativo). Em cada contrato e cada ano, essa soma é igual ao "vlpago" do "contratoResumoFinanceiro", ao centavo.',
            'paid_brl = soma das linhas positivas; reversed_brl = soma das linhas negativas (estornos), em valor absoluto; net_paid_brl = paid_brl - reversed_brl = soma do "vlpago" anual.',
            'Linhas com situação "PP Resolvida por outra PP" (2 linhas, PJ-00056/2016) e "Paga e Estornada por NE" (2 linhas, PJ-00056/2016) entram, porque o "vlpago" oficial as inclui; retenções de IRRF "Canceladas pelo usuário" entram junto com o estorno que as anula (somam zero ou fecham o ano com o resumo).',
            'first_payment e last_payment: data de referência da primeira e da última linha positiva do extrato.',
            'Valores nominais, sem correção.',
        ],
        'coverage': {
            'portal': 'O extrato SICOP do Portal tem linhas de pagamento só de 2011 em diante (SIGEF). Nos três contratos anteriores a 2011 (PJ-00170/2006, nas duas linhas, e PJ-00264/2008), não há linha antes de 2011.',
            'portal_years_by_contract': {c['number']: c['years_in_portal'] for c in contracts},
            'last_load': f"Carga do Portal lida em {date.today().isoformat()}; o último pagamento dos 13 registros é de {max(c['last_payment'] for c in contracts)}.",
        },
        'contracts': contracts,
        'related_records': related_out,
        'pre_portal': pre_portal,
        'total_net_paid_portal_brl': brl(pass1_total),
        'total_net_paid_brl': brl(total_c),
        'total_includes': 'Os 13 contratos da restauração (2006 a 2019), pagamentos do Poder Executivo de SC lidos por contrato no Portal (2011 a 2020), mais o pago antes de 2011 no contrato PJ-00264/2008, tirado do acumulado oficial do TCE-SC (R$ 38.921.239,05 até maio de 2012) no lugar das linhas do Portal até maio de 2012.',
        'first_stage_pj015_2006': {
            'number': 'PJ 015/2006', 'company': 'Consórcio Roca-TEC (uma tabela de pagamentos por empresa)', 'signed_on': '2006-02-16',
            'signed_quote': signed_015,
            'object': 'restauração, reabilitação e manutenção da Ponte Hercílio Luz, etapa 1, viadutos de acesso',
            'value_original_brl': float(brl_dec(v015)), 'value_with_amendments_brl': float(brl_dec(v015_amended)),
            'paid_brl': brl(fs_total_c), 'members': members,
            'source': {'doc': CPI_DOC + ': Apêndice A, tabelas "Contrato PJ 015/2006 - TEC" e "Contrato PJ 015/2006 - Roca"; item 6.11', 'url': CPI_URL},
            'note': 'Fora do Portal (os extratos começam em 2011) e fora do registro SIGEF (13 registros da restauração). As duas tabelas trazem as mesmas 42 medições, cada uma com a parte de uma empresa do consórcio. O quadro-resumo da CPI (p. 1344) dá R$ 12.487.834 para a TEC; vale a tabela de pagamentos, que fecha com a sua linha TOTAL.',
        },
        'initial_contracts_2006_2008': {
            'contracts': initial, 'value_original_brl': brl(initial_c),
            'rule': 'Contrato inicial da obra = valores assinados dos primeiros contratos (2006 a 2008): 1ª etapa, supervisão e 2ª etapa. Um contrato que substitui um contrato rescindido não entra (D95: ler contrato por contrato, sem somar contratos que se sobrepõem).',
        },
        'total_paid_2006_2020_brl': brl(full_2),
        'total_paid_2006_2020_parts_brl': parts,
        'total_paid_2006_2020_includes': 'Pago contrato por contrato, valores nominais: os 10 contratos de 2011 em diante pelos extratos do Portal de SC; PJ-00170/2006 (Prosul e Concremat) e PJ-00264/2008 pelas tabelas de pagamento da CPI da Alesc (começaram antes do Portal); e a 1ª etapa, PJ 015/2006, pelas suas duas tabelas na CPI.',
        'total_paid_2006_2020_not_included': [
            'DL-00001/2618-2019 (RMG, ' + pt(related_out[0]['net_paid_brl']) + ' pagos em 2019, supervisão fora do escopo do PJ-00093/2016): registro à parte (related_records), fora desta soma até decisão do autor.',
            'Pagamentos que não estão ligados ao contrato no extrato (PJ-00060/2019, R$ 16.002,61) e obras da ponte antes de 2006 ou depois de 2019: fora do escopo.',
        ],
        'total_missing': [
            'Pagamentos de 2006 a 2010 no contrato de supervisão PJ-00170/2006 (Prosul e Concremat): fora deste total (Portal e TCE-SC). O SICOP mede ' + pt(supervision[0]['measured_accumulated_brl'] + supervision[1]['measured_accumulated_brl']) + ' acumulados até dezembro de 2010 nas duas linhas, mas medido não é pago. Os pagamentos estão nas tabelas da CPI e entram em total_paid_2006_2020_brl.',
            'PJ-00060/2019 (Geoarqueologia): a consulta por credor mostra R$ 16.402,68 pagos em 2019, e o extrato do contrato mostra só R$ 400,07 nesse ano; a diferença de R$ 16.002,61 não está ligada ao contrato no extrato e fica fora do total.',
            'DL-00001/2618-2019 (RMG, R$ 1.451.313,01 pagos em 2019, "pagamento realizado na supervisão da PHL e que não estava no escopo do Contrato PJ 093/2016"): fora dos 13 contratos, mostrado em related_records e fora do total.',
            'PJ-00170/2006 (Concremat), 2011: o extrato do contrato soma R$ 1.104.600,17 e a consulta por credor (CNPJ 33.146.648/0003-91) mostra R$ 993.730,38 para a empresa inteira no ano. A diferença de R$ 110.869,79 não foi explicada (talvez pagamentos do contrato registrados em outro CNPJ ou credor). O total usa o extrato do contrato.',
            'Obras e contratos da ponte anteriores a 2006 e posteriores a 2019 (iluminação, manutenção) e gastos de outros órgãos: fora do escopo.',
        ],
        'check': {
            'pass_1': 'Inteiros em centavos a partir do "vlpago" anual do resumo de cada contrato.',
            'pass_2': 'Decimal, soma das linhas de pagamento de cada contrato.',
            'per_contract_per_year_equal': not problems,
            'total_portal_pass_1_brl': brl(pass1_total), 'total_portal_pass_2_brl': str(pass2_total),
            'total_with_pre_portal_pass_1_brl': brl(total_c), 'total_with_pre_portal_pass_2_brl': str(total_d),
            'match_to_the_cent': match,
            'total_2006_2020_pass_1_brl': str(full_1), 'total_2006_2020_pass_2_brl': brl(full_2),
            'total_2006_2020_pass_1': 'Decimal, contrato por contrato: linhas de pagamento do Portal; linhas das tabelas da CPI; coluna VALOR MEDIDO das duas tabelas do PJ 015/2006.',
            'total_2006_2020_pass_2': 'Inteiros em centavos: total do "vlpago" do Portal, trocando os três contratos anteriores a 2011 pela coluna PGTOS NO MÊS das tabelas da CPI, mais a mesma coluna do PJ 015/2006.',
            'cpi_tables_equal_their_total_line': not cpi_problems,
            'control': 'Rodar com --control soma R$ 0,01 à primeira linha do PJ-00056/2016 e à primeira medição do PJ 015/2006 (TEC); a checagem tem de falhar e nada é gravado.',
            'creditor_cross_check': creditor,
            'creditor_note': 'Total por credor (data/hercilio-luz.json, consulta Fornecedores) contra a soma dos contratos da ponte da mesma empresa no mesmo ano. Diferença esperada onde a empresa tem outros contratos com o Estado. Onde é igual, mostra também que o "vlbruto" do credor já desconta os estornos.',
        },
    }
    tmp = OUT.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    tmp.replace(OUT)
    print('written', OUT)


if __name__ == '__main__':
    main()
