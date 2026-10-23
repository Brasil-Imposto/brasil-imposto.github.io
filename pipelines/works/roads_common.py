"""Helpers shared by the road works fact sheets (SC-401 and BR-470): IPCA, reading official texts and checking quotes.

Every literal quote used in the JSON files is checked against the text of the downloaded official document
(`require_quote`). The comparison normalises case, accents and punctuation, because the DOE-SC PDF
turns dots into invalid characters when its text is extracted.
"""
import html, json, os, re, subprocess, unicodedata

TARGET = '202412'


def load_ipca(work):
    rows = json.load(open(os.path.join(work, 'ipca.json')))[1:]
    return {r['D3C']: float(r['V']) for r in rows if r['V'] not in ('...', '-', '')}


def ipca_factor(ipca, ym):
    """Factor that brings a value of the month `ym` (YYYYMM) to reais of December 2024."""
    return ipca[TARGET] / ipca[ym]


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', s)


def pdf_text(path):
    """Text of the PDF in two readings (with and without -layout): gazettes set in columns stay contiguous in only one."""
    out = []
    for flag, suffix in (('-layout', '.layout.txt'), (None, '.raw.txt')):
        txt = path[:-4] + suffix
        if not os.path.exists(txt):
            subprocess.run(['pdftotext'] + ([flag] if flag else []) + [path, txt], check=True)
        out.append(open(txt, encoding='utf-8', errors='ignore').read())
    return '\n'.join(out)


def clean_html(s):
    s = re.sub(r'<script.*?</script>|<style.*?</style>', '', s or '', flags=re.S)
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)))


def tcu_text(path):
    x = json.load(open(path))['documentos'][0]
    return ' '.join(clean_html(x.get(k)) for k in ('TITULO', 'SUMARIO', 'INTERESSADOS', 'ACORDAO', 'RELATORIO', 'VOTO'))


def numbers(s):
    """Every number of a text with its separators. The DOE-SC PDF extracts the thousands dot as an invalid character, so a
    symbol between two digits reads as a dot; a comma, a space or a letter between digits never does."""
    fixed = re.sub(r'(?<=\d)[^\d,\s\w](?=\d)', '.', s or '')
    return re.findall(r'\d+(?:[.,]\d+)*', fixed)


def require_quote(quote, source_text, label):
    parts = [norm(p) for p in quote.split('[...]') if norm(p)]
    src = norm(source_text)
    missing = [p for p in parts if p not in src]
    if missing:
        raise AssertionError(f'citação não encontrada na fonte ({label}): {quote[:120]}')
    # the letters-and-digits comparison above ignores punctuation, so "R$ 113.652" would pass for "R$ 1.136,52": every
    # number of the quote must also be in the source with the same separators
    src_numbers = set(numbers(source_text))
    wrong = [n for n in numbers(quote.replace('[...]', ' ')) if n not in src_numbers]
    if wrong:
        raise AssertionError(f'número da citação não está na fonte com os mesmos separadores ({label}): {wrong[:3]} em {quote[:120]}')
    return quote


def require_complete_months(payments, label):
    """A payments file with months that failed to download is incomplete: it never feeds a total."""
    if payments.get('months_missing'):
        raise SystemExit(f'{label}: meses sem download {payments["months_missing"]}; o total ficaria menor sem aviso')
    return payments


def self_test():
    """Controls: the exact quote passes, also over a PDF that broke the thousands dot; an invented sentence and the same amount
    with a misplaced separator or a different digit fail; a payments file with a missing month stops."""
    src = 'Multa de R$ 1.136,52 ao então presidente do DEINFRA'
    broken = src.replace('1.136', '1' + chr(0xFFFD) + '136')
    require_quote('Multa de R$ 1.136,52', src, 'controle exato')
    require_quote('Multa de R$ 1.136,52', broken, 'controle com o ponto quebrado no PDF')
    for bad in ('esta frase não existe em lugar nenhum', 'Multa de R$ 11.365,2', 'Multa de R$ 113.652', 'Multa de R$ 1.136,53'):
        try:
            require_quote(bad, src, 'controle')
        except AssertionError:
            continue
        raise SystemExit(f'checagem de citações não está funcionando: passou {bad!r}')
    try:
        require_complete_months({'months_missing': ['202401']}, 'controle')
    except SystemExit:
        return True
    raise SystemExit('checagem de meses faltando não está funcionando')


def brl(x):
    return None if x is None else round(float(x), 2)


def num_br(s):
    return float(str(s).replace('.', '').replace(',', '.'))


def no_dashes(obj):
    """Replaces em dashes and en dashes with a hyphen in every string (the project's style rule; the quotes were
    already checked before this step)."""
    if isinstance(obj, str):
        return obj.replace('\u2014', '-').replace('\u2013', '-')
    if isinstance(obj, list):
        return [no_dashes(x) for x in obj]
    if isinstance(obj, dict):
        return {no_dashes(k): no_dashes(v) for k, v in obj.items()}
    return obj
