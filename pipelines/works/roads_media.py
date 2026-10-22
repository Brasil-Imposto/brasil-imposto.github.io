"""Baixa as fotos (licença livre, Wikimedia Commons) das fichas de obra, a ~1000 px de largura, e grava credits.json
no formato de docs/superpowers/previews/assets/cases/hercilio-luz/credits.json.

Uso: python3 roads_media.py      (grava direto em docs/superpowers/previews/assets/cases/<slug>/)
Fonte dos metadados: API do Commons (prop=imageinfo, extmetadata). Coleta original: 2026-09-30.
"""
import json, os, re, subprocess, time, urllib.parse

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'docs', 'superpowers', 'previews', 'assets', 'cases')
UA = 'BrasilImpostoResearch/0.1 (civic research) curl'
API = 'https://commons.wikimedia.org/w/api.php'
LICENSE_URL = {'CC BY 3.0': 'https://creativecommons.org/licenses/by/3.0',
               'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0',
               'CC BY-SA 3.0': 'https://creativecommons.org/licenses/by-sa/3.0'}

PHOTOS = {
    'br-470-duplicacao': [
        ('road-indaial-2011.jpg', 'File:BR 470 Indaial - panoramio.jpg'),
        ('urban-indaial-2011.jpg', 'File:Uniasselvi Indaial ao lado direito - BR 470 - panoramio.jpg'),
        ('trucks-indaial-2011.jpg', 'File:Caminhoes parados em Indaial - Br 470 - panoramio.jpg'),
    ],
    'sc-401-terceira-faixa': [
        ('centro-administrativo-2014.jpg', 'File:Centro Administrativo de Santa Catarina.jpg'),
        ('saco-grande-2023.jpg', 'File:Floripa Shopping - 2.jpg'),
        ('sc-401-margin-2015.jpg', 'File:Banco do Brasil SC-401.jpg'),
    ],
}


def strip(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


def meta(title):
    q = urllib.parse.urlencode({'action': 'query', 'titles': title, 'prop': 'imageinfo',
                                'iiprop': 'url|size|extmetadata', 'iiurlwidth': 1000, 'format': 'json'})
    r = subprocess.run(['curl', '-sS', '-m', '60', '-A', UA, f'{API}?{q}'], capture_output=True, text=True)
    page = next(iter(json.loads(r.stdout)['query']['pages'].values()))
    return page['imageinfo'][0]


def main():
    for slug, items in PHOTOS.items():
        d = os.path.join(OUT, slug)
        os.makedirs(d, exist_ok=True)
        credits = {}
        for fname, title in items:
            ii = meta(title)
            em = ii.get('extmetadata', {})
            g = lambda k: strip((em.get(k) or {}).get('value'))
            path = os.path.join(d, fname)
            subprocess.run(['curl', '-sS', '-m', '120', '-A', UA, '-o', path, ii['thumburl']], check=True)
            lic = g('LicenseShortName')
            credits[fname] = {
                'file': fname, 'commons': ii['descriptionurl'], 'license': lic,
                'license_url': LICENSE_URL.get(lic), 'author': g('Artist'), 'date': g('DateTimeOriginal') or None,
                'description': g('ImageDescription'), 'width_px': ii.get('thumbwidth'), 'height_px': ii.get('thumbheight'),
                'gps': [g('GPSLatitude') or None, g('GPSLongitude') or None], 'bytes': os.path.getsize(path),
            }
            print(slug, fname, lic, credits[fname]['author'], ii.get('thumbwidth'), flush=True)
            time.sleep(3)
        json.dump(credits, open(os.path.join(d, 'credits.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
