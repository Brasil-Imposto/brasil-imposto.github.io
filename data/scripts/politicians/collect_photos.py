"""Fotos de perfil dos politicos do site (decisao D61) -> data/politicians/photos.json.

Fonte principal: fotos de candidatos do TSE (Portal de Dados Abertos, licenca Creative Commons Atribuicao),
um ZIP por eleicao e UF. O ZIP nao e gravado em disco: o CDN do TSE aceita HTTP Range, entao o script le o
indice do ZIP e depois so as fotos das pessoas dos nossos arquivos (uma requisicao por foto, CRC conferido).
Cada foto e reduzida com sips para no maximo 200 px de altura (JPEG qualidade 85) e gravada em
docs/superpowers/previews/assets/photos/<office>/<id-sanitizado>.jpg. Fotos de quem nao esta nos nossos
arquivos nunca sao lidas.

Nomeados que nunca foram candidatos (ministro) vem de pagina oficial, listada em MANUAL.

Retoma de onde parou: quem ja tem arquivo e entrada em photos.json e pulado; quem esta em "missing" so e
tentado de novo com --retry-missing. O JSON e regravado depois de cada ZIP.

Uso:
  python3 data/scripts/politicians/collect_photos.py              # coleta (ou continua)
  python3 data/scripts/politicians/collect_photos.py --check      # confere o resultado, sem rede
  python3 data/scripts/politicians/collect_photos.py --check --control rs-mayors   # controle: tem de falhar
  python3 data/scripts/politicians/collect_photos.py --only governors,senators --retry-missing
"""
import argparse
import csv
import io
import json
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.request
import zipfile
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tse_common import RemoteZip, http_open as _open  # noqa: E402  (leitura por HTTP Range, compartilhada)

ROOT = Path(__file__).resolve().parents[3]
POL = ROOT / "data" / "politicians"
OUT_JSON = POL / "photos.json"
PHOTO_DIR = ROOT / "docs" / "superpowers" / "previews" / "assets" / "photos"
REL = lambda p: str(p.relative_to(ROOT))

MAX_HEIGHT = 200
JPEG_QUALITY = "85"
WORKERS = 8

PHOTO_ZIP = "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes{year}/fotos/foto_cand{year}_{uf}_div.zip"
CAND_ZIP = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{year}.zip"
DATASET = {2014: "candidatos-2014", 2016: "candidatos-2016", 2018: "candidatos-2018", 2020: "candidatos-2020-subtemas",
           2022: "candidatos-2022", 2024: "candidatos-2024"}
DATASET_PAGE = "https://dadosabertos.tse.jus.br/dataset/{}"
MEMBER = re.compile(r"^F([A-Z]{2})(\d+)_div\.(jpe?g|png|bmp|gif)$", re.I)

TERMS = {
    "tse": {
        "url": "https://dadosabertos.tse.jus.br/dataset/candidatos-2022",
        "quote": "Licença Creative Commons Attribution",
        "license_url": "http://www.opendefinition.org/licenses/cc-by",
        "datasets_checked": {str(y): DATASET_PAGE.format(d) for y, d in DATASET.items()},
        "datasets_note": "A mesma licença (license_id 'cc-by', 'Creative Commons Attribution') consta nos seis conjuntos "
                         "acima pela API do portal (package_show), conferida em 2026-10-02 (candidatos-2016 em 2026-10-04).",
        "faq_url": "https://dadosabertos.tse.jus.br/pages/perguntasfrequentes",
        "faq_quote": "São dados acessíveis ao público, representados em meio digital, estruturados em formato aberto, não "
                     "proprietário, processáveis por máquina, referenciados na Internet e disponibilizados sob licença aberta "
                     "que permita sua livre utilização, consumo ou cruzamento, limitando-se a creditar a autoria ou a fonte.",
        "readme_quote": "Este arquivo .ZIP contém as fotos divulgáveis e enviadas pelas candidatas e candidatos.",
        "readme_source": "leiame.pdf dentro de cada foto_cand<ano>_<UF>_div.zip",
        "credit": "Tribunal Superior Eleitoral, Portal de Dados Abertos",
        "verified_on": "2026-10-02",
    },
    "gov_br_fazenda": {
        "url": "https://www.gov.br/fazenda/pt-br/composicao/ministro",
        "quote": "Todo o conteúdo deste site está publicado sob a licença Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada.",
        "license_url": "https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR",
        "note": "Rodapé do site do Ministério da Fazenda. A foto foi só reduzida de tamanho, sem recorte nem outra alteração.",
        "verified_on": "2026-10-02",
    },
}

MANUAL = {
    "senado:415": {
        "office": "senators",
        "remote_url": "https://www.camara.leg.br/internet/deputado/bandep/74742.jpg",
        "source": "https://dadosabertos.camara.leg.br/api/v2/deputados/74742",
        "author": "Câmara dos Deputados",
        "license_or_terms": "Reprodução gratuita com citação da fonte 'Câmara dos Deputados' (itens 7 e 29 do Termo de uso do portal da Câmara)",
        "page": "https://www2.camara.leg.br/termo-de-uso-e-politica-de-privacidade",
        "note": "Retrato oficial de deputado federal (id 74742, nome civil LAEL VIEIRA VARELLA, MG, legislaturas 51 a 54), o mesmo "
                "nome completo do registro no Senado. Usado porque a foto do Senado não responde e o ZIP de fotos do TSE de 2014 "
                "(MG) não tem a foto do SQ_CANDIDATO dele. URL remota, como as dos deputados federais.",
        "fallback_only": True,
    },
    "dario-durigan": {
        "office": "union",
        "download": "https://web.archive.org/web/20260319180725id_/https://www.gov.br/fazenda/pt-br/composicao/secretaria-executiva/dario-carnevalli-durigan/@@images/image",
        "source": "https://www.gov.br/fazenda/pt-br/composicao/secretaria-executiva/dario-carnevalli-durigan/@@images/image",
        "author": "Washington Costa / Ministério da Fazenda (metadados XMP do arquivo oficial: dc:creator 'Washington Costa', "
                  "dc:rights 'Ministerio da Fazenda'; a página não traz crédito, e o Wikimedia Commons atribui a Diogo Zacarias)",
        "license_or_terms": "CC BY-ND 3.0, conforme o rodapé do site gov.br/fazenda; crédito: Washington Costa / Ministério da Fazenda",
        "page": "https://web.archive.org/web/20260319180720/https://www.gov.br/fazenda/pt-br/composicao/secretaria-executiva/dario-carnevalli-durigan",
        "note": "Foto oficial da página de Secretário-Executivo do Ministério da Fazenda (cópia do Internet Archive de 2026-03-19; a "
                "página saiu do ar quando ele assumiu o ministério, e a página atual do ministro, que o lista como Ministro da "
                "Fazenda, não traz foto). O arquivo do Commons com a mesma foto está marcado como PD-USGov, licença de obra do "
                "governo dos EUA que não se aplica; por isso não foi usado.",
    },
}


# ---------------------------------------------------------------- cadastro de candidaturas (para achar o SQ)

_cand_cache = {}


def cand_rows(year, uf):
    key = (year, uf)
    if key not in _cand_cache:
        rz = _cand_cache.setdefault(("zip", year), None) or RemoteZip(CAND_ZIP.format(year=year))
        _cand_cache[("zip", year)] = rz
        info = next(i for i in rz.infos if i.filename == f"consulta_cand_{year}_{uf}.csv")
        text = rz.read(info).decode("latin-1")
        _cand_cache[key] = list(csv.DictReader(io.StringIO(text), delimiter=";"))
    return _cand_cache[key]


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()


def find_sq(year, uf, full_name, cargos):
    hits = {r["SQ_CANDIDATO"]: r for r in cand_rows(year, uf)
            if norm(r["NM_CANDIDATO"]) == norm(full_name) and r["DS_CARGO"].upper() in cargos}
    return list(hits.values())


# ---------------------------------------------------------------- quem precisa de foto

def sanitize(pid):
    return re.sub(r"[^a-z0-9]+", "-", pid.lower()).strip("-")


def load(name):
    return json.loads((POL / f"{name}.json").read_text(encoding="utf-8"))


def has_photo(p):
    return bool((p.get("photo") or {}).get("url"))


def targets(lookup=True):
    """(tse, manual, missing, inventory). tse = lista de dicts {id, office, year, uf, sq, name}."""
    tse, manual, missing = [], [], {}
    inv = {}

    u = load("union")
    inv["union"] = {"people": len(u["people"]), "without_photo": [k for k, p in u["people"].items() if not has_photo(p)]}
    for pid in inv["union"]["without_photo"]:
        if pid in MANUAL and not MANUAL[pid].get("fallback_only"):
            manual.append(pid)
        else:
            missing[pid] = "nomeado sem foto oficial localizada"

    g = load("governors")
    inv["governors"] = {"people": len(g["people"]), "without_photo": [k for k, p in g["people"].items() if not has_photo(p)]}
    for pid in inv["governors"]["without_photo"]:
        if not lookup:
            continue
        p = g["people"][pid]
        years = sorted({int(o["observed_on"][:4]) for o in p.get("party_observations", [])
                        if re.search(r"\((vice-)?governador,", o.get("basis", ""))}, reverse=True)
        found = None
        for y in years:
            hits = find_sq(y, p["uf"], p["full_name"], {"GOVERNADOR", "VICE-GOVERNADOR"})
            if len(hits) == 1:
                found = (y, hits[0])
                break
        if not found:
            missing[pid] = f"candidatura a governador ou vice não localizada no consulta_cand ({years}, {p['uf']}) pelo nome completo"
            continue
        y, r = found
        tse.append({"id": pid, "office": "governors", "year": y, "uf": p["uf"], "sq": r["SQ_CANDIDATO"], "name": p["name"],
                    "tse_id": f"tse:{y}:{r['SQ_CANDIDATO']}", "tse_cargo": r["DS_CARGO"]})

    s = load("senators")
    rows = [(uf, r) for uf, lst in s["by_uf"].items() for r in lst]
    inv["senators"] = {"people": len(rows), "without_photo": [r["id"] for _, r in rows if not has_photo(r)]}
    for uf, r in rows:
        if has_photo(r) or not lookup:
            continue
        found = None
        for t in r.get("terms", []):
            y = int(t["mandate_start"][:4]) - 1  # mandato de senador começa no ano seguinte à eleição
            hits = find_sq(y, t["uf"], r["full_name"], {"SENADOR", "1º SUPLENTE", "2º SUPLENTE", "1O SUPLENTE", "2O SUPLENTE"})
            if len(hits) == 1:
                found = (y, t["uf"], hits[0])
        if not found:
            missing[r["id"]] = "candidatura ao Senado não localizada no consulta_cand pelo nome completo"
            continue
        y, tuf, h = found
        tse.append({"id": r["id"], "office": "senators", "year": y, "uf": tuf, "sq": h["SQ_CANDIDATO"], "name": r["name"],
                    "tse_id": f"tse:{y}:{h['SQ_CANDIDATO']}", "tse_cargo": h["DS_CARGO"]})

    f = load("federal-deputies")
    rows = [r for lst in f["by_uf"].values() for r in lst]
    inv["federal-deputies"] = {"people": len(rows), "without_photo": [r["id"] for r in rows if not has_photo(r)]}
    for pid in inv["federal-deputies"]["without_photo"]:
        missing[pid] = "sem foto na Câmara; busca no TSE não implementada para deputado federal"

    d = load("state-deputies")
    ids = []
    for uf, years in d["by_uf"].items():
        for y, lst in years.items():
            for r in lst:
                _, yy, sq = r["id"].split(":")
                ids.append(r["id"])
                tse.append({"id": r["id"], "office": "state-deputies", "year": int(yy), "uf": uf, "sq": sq, "name": r["name"]})
    inv["state-deputies"] = {"people": len(ids), "without_photo": ids}

    for path in sorted(POL.glob("*-mayors.json")):  # sc-mayors.json, rs-mayors.json (build_mayors.py)
        office = path.stem
        uf = office.split("-")[0].upper()
        m = load(office)
        ids = []
        for mu in m["municipalities"]:
            for e in mu["elections"]:
                for k in ("mayor", "vice_mayor"):
                    x = e.get(k)
                    if not x:
                        continue
                    _, yy, sq = x["id"].split(":")
                    ids.append(x["id"])
                    tse.append({"id": x["id"], "office": office, "year": int(yy), "uf": uf, "sq": sq, "name": x["name"],
                                "role": k, "municipality": mu["name"]})
        inv[office] = {"people": len(ids), "without_photo": ids}
    return tse, manual, missing, inv


# ---------------------------------------------------------------- foto: reduzir e gravar

def sips_height(path):
    out = subprocess.run(["sips", "-g", "pixelHeight", str(path)], capture_output=True, text=True).stdout
    m = re.search(r"pixelHeight: (\d+)", out)
    return int(m.group(1)) if m else None


def _segments(b):
    """Segmentos de um JPEG ate o SOS: (marcador, inicio, fim). Vazio se nao for JPEG."""
    if b[:2] != b"\xff\xd8":
        return [], 0
    segs, i = [], 2
    while i + 4 <= len(b) and b[i] == 0xFF:
        m = b[i + 1]
        if m == 0xFF:
            i += 1
            continue
        if m == 0xDA:
            break
        ln = int.from_bytes(b[i + 2:i + 4], "big")
        segs.append((m, i, i + 2 + ln))
        i += 2 + ln
    return segs, i


def exif_orientation(b):
    segs, _ = _segments(b)
    for m, s, e in segs:
        if m == 0xE1 and b[s + 4:s + 10] == b"Exif\x00\x00":
            tf = b[s + 10:e]
            order = "little" if tf[:2] == b"II" else "big"
            u16 = lambda o: int.from_bytes(tf[o:o + 2], order)
            ifd = int.from_bytes(tf[4:8], order)
            for k in range(u16(ifd) if ifd + 2 <= len(tf) else 0):
                ent = ifd + 2 + 12 * k
                if u16(ent) == 0x0112:
                    return u16(ent + 8)
    return 1


def strip_metadata(b):
    """Tira APP1 (EXIF e XMP), APP13 (Photoshop/IPTC) e comentarios; mantem JFIF, ICC e os dados da imagem."""
    segs, sos = _segments(b)
    out = bytearray(b[:2])
    for m, s, e in segs:
        if m not in (0xE1, 0xED, 0xFE):
            out += b[s:e]
    return bytes(out + b[sos:])


# orientacao EXIF -> operacoes do sips para deixar os pixels na posicao em que o navegador mostraria
ORIENT = {2: [["-f", "horizontal"]], 3: [["-r", "180"]], 4: [["-f", "vertical"]], 5: [["-f", "horizontal"], ["-r", "270"]],
          6: [["-r", "90"]], 7: [["-f", "horizontal"], ["-r", "90"]], 8: [["-r", "270"]]}


def save_photo(raw, out):
    """Gira conforme a orientacao EXIF, reduz para no maximo MAX_HEIGHT de altura (nunca amplia), grava JPEG
    e remove os metadados (o sips preserva EXIF/XMP, inclusive numero de serie de camera). Devolve (w, h, orientacao)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    orient = exif_orientation(raw)
    with tempfile.NamedTemporaryFile(suffix=".img", dir=out.parent, delete=True) as tmp:
        tmp.write(raw)
        tmp.flush()
        for op in ORIENT.get(orient, []):
            subprocess.run(["sips"] + op + [tmp.name], capture_output=True, check=True)
        h = sips_height(tmp.name)
        if not h:
            raise RuntimeError("imagem ilegivel para o sips")
        args = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", JPEG_QUALITY]
        if h > MAX_HEIGHT:
            args += ["--resampleHeight", str(MAX_HEIGHT)]
        r = subprocess.run(args + [tmp.name, "--out", str(out)], capture_output=True, text=True)
        if r.returncode != 0 or not out.exists():
            raise RuntimeError("sips falhou: " + (r.stderr or r.stdout)[:200])
    out.write_bytes(strip_metadata(out.read_bytes()))
    o = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(out)], capture_output=True, text=True).stdout
    return int(re.search(r"pixelWidth: (\d+)", o).group(1)), int(re.search(r"pixelHeight: (\d+)", o).group(1)), orient


# ---------------------------------------------------------------- photos.json

def load_state():
    if OUT_JSON.exists():
        return json.loads(OUT_JSON.read_text(encoding="utf-8"))
    return {"collected_on": None, "sources": [], "terms": TERMS, "people": {}, "missing": {}}


def write_state(st):
    st["collected_on"] = time.strftime("%Y-%m-%d")
    st["terms"] = TERMS
    st["people"] = dict(sorted(st["people"].items()))
    st["missing"] = dict(sorted(st["missing"].items()))
    tmp = OUT_JSON.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(OUT_JSON)


def add_source(st, name, url):
    if not any(s["url"] == url for s in st["sources"]):
        st["sources"].append({"name": name, "url": url})


def done(st, pid, retry_missing):
    e = st["people"].get(pid)
    if e and ((e.get("file") and (ROOT / e["file"]).exists()) or (not e.get("file") and e.get("url"))):
        return True
    return pid in st["missing"] and not retry_missing


def tse_entry(t, url, member, size):
    e = {"file": None, "url": None, "source": url,
         "author": "Foto enviada pela candidatura no registro de candidatura; publicada pelo Tribunal Superior Eleitoral",
         "license_or_terms": f"Creative Commons Atribuição (CC BY), licença do conjunto '{DATASET[t['year']]}' do Portal de Dados "
                             "Abertos do TSE; crédito: Tribunal Superior Eleitoral",
         "page": DATASET_PAGE.format(DATASET[t["year"]]),
         "office": t["office"], "election_year": t["year"], "uf": t["uf"], "zip_member": member, "size_px": list(size)}
    if t.get("tse_id"):
        e["tse_id"], e["tse_cargo"] = t["tse_id"], t["tse_cargo"]
    return e


def run_zip(st, year, uf, items):
    url = PHOTO_ZIP.format(year=year, uf=uf)
    try:
        rz = RemoteZip(url)
    except Exception as e:
        for t in items:
            st["missing"][t["id"]] = f"ZIP de fotos do TSE indisponível ({url}): {e}"
        return 0
    add_source(st, f"TSE, fotos de candidatos {year}, {uf}", url)
    by_sq = {}
    for i in rz.infos:
        m = MEMBER.match(i.filename)
        if m and m.group(1).upper() == uf:
            by_sq.setdefault(m.group(2), i)

    def one(t):
        info = by_sq.get(t["sq"])
        if not info:
            return t, None, f"o ZIP {url.rsplit('/', 1)[1]} não tem foto para o SQ_CANDIDATO {t['sq']} (foto não divulgada pelo TSE)"
        out = PHOTO_DIR / t["office"] / (sanitize(t["id"]) + ".jpg")
        try:
            w, h, orient = save_photo(rz.read(info), out)
        except Exception as e:
            return t, None, f"falha ao ler ou converter {info.filename}: {e}"
        entry = tse_entry(t, url, info.filename, (w, h))
        if orient != 1:
            entry["exif_orientation_applied"] = orient
        entry["file"] = REL(out)
        return t, entry, None

    ok = 0
    with ThreadPoolExecutor(WORKERS) as ex:
        for t, entry, err in ex.map(one, items):
            if entry:
                st["people"][t["id"]] = entry
                st["missing"].pop(t["id"], None)
                ok += 1
            else:
                st["missing"][t["id"]] = err
    return ok


def run_manual(st, pid):
    m = MANUAL[pid]
    if m.get("remote_url"):
        status, headers, _ = _open(m["remote_url"])
        if status != 200 or not headers.get("Content-Type", "").startswith("image/"):
            st["missing"][pid] = f"foto oficial remota não respondeu com imagem: {m['remote_url']}"
            return
        st["people"][pid] = {"file": None, "url": m["remote_url"], "source": m["source"], "author": m["author"],
                             "license_or_terms": m["license_or_terms"], "page": m["page"], "office": m["office"], "note": m["note"]}
        st["missing"].pop(pid, None)
        add_source(st, "Câmara dos Deputados, Dados Abertos (retrato oficial)", m["source"])
        return
    out = PHOTO_DIR / m["office"] / (sanitize(pid) + ".jpg")
    try:
        _, headers, raw = _open(m["download"])
        if not headers.get("Content-Type", "").startswith("image/"):
            raise RuntimeError("resposta não é imagem")
        w, h, _ = save_photo(raw, out)
    except Exception as e:
        st["missing"][pid] = f"foto oficial não baixada: {e}"
        return
    st["people"][pid] = {"file": REL(out), "url": None, "source": m["source"], "author": m["author"],
                         "license_or_terms": m["license_or_terms"], "page": m["page"], "office": m["office"],
                         "size_px": [w, h], "note": m["note"]}
    st["missing"].pop(pid, None)
    add_source(st, "Ministério da Fazenda, página oficial (cópia do Internet Archive)", m["page"])


# ---------------------------------------------------------------- conferência

def check(control=None):
    st = load_state()
    _, _, _, inv = targets(lookup=False)
    if control:  # controle plantado: some a foto de uma pessoa do office; a conferência tem de acusar
        pid = next(k for k, e in sorted(st["people"].items()) if e.get("office") == control)
        del st["people"][pid]
        print(f"CONTROLE: foto de {pid} ({control}) retirada em memória")
    expected = {pid for v in inv.values() for pid in v["without_photo"]}
    problems = []
    for pid, e in st["people"].items():
        if pid not in expected:
            problems.append(f"{pid}: pessoa fora dos nossos arquivos")
        if not e.get("file") and e.get("url", "").startswith("https://"):
            continue  # foto remota oficial
        p = ROOT / e["file"] if e.get("file") else None
        if not p or not p.exists():
            problems.append(f"{pid}: arquivo ausente")
            continue
        if p.read_bytes()[:3] != b"\xff\xd8\xff":
            problems.append(f"{pid}: não é JPEG")
        h = sips_height(p)
        if not h or h > MAX_HEIGHT:
            problems.append(f"{pid}: altura {h}")
        if any(m in (0xE1, 0xED, 0xFE) for m, _, _ in _segments(p.read_bytes())[0]):
            problems.append(f"{pid}: metadados EXIF/XMP/IPTC no arquivo")
        if pid in st["missing"]:
            problems.append(f"{pid}: em people e em missing")
    for pid in expected:
        if pid not in st["people"] and pid not in st["missing"]:
            problems.append(f"{pid}: sem foto e sem motivo")
    referenced = {str(ROOT / e["file"]) for e in st["people"].values() if e.get("file")}
    for f in PHOTO_DIR.rglob("*"):
        if f.is_file() and str(f) not in referenced:
            problems.append(f"{REL(f)}: arquivo órfão (não está em photos.json)")
    total = sum(f.stat().st_size for f in PHOTO_DIR.rglob("*.jpg"))
    print(f"people={len(st['people'])} missing={len(st['missing'])} expected={len(expected)} "
          f"files_bytes={total} problems={len(problems)}")
    for p in problems[:40]:
        print("  ", p)
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="lista de offices: union,governors,senators,state-deputies,sc-mayors,rs-mayors")
    ap.add_argument("--retry-missing", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--control", help="com --check: retira em memória a foto de uma pessoa deste office (ex.: rs-mayors); "
                                      "a conferência tem de falhar")
    a = ap.parse_args()
    if a.check:
        sys.exit(check(a.control))
    only = set(a.only.split(",")) if a.only else None
    st = load_state()
    tse, manual, missing0, inv = targets()
    print("inventario:", {k: (v["people"], len(v["without_photo"])) for k, v in inv.items()}, flush=True)
    for pid, why in missing0.items():
        if not only or any(pid in inv[o]["without_photo"] for o in only if o in inv):
            st["missing"].setdefault(pid, why)
    for pid in manual:
        if (not only or MANUAL[pid]["office"] in only) and not done(st, pid, a.retry_missing):
            run_manual(st, pid)
    write_state(st)
    groups = {}
    for t in tse:
        if only and t["office"] not in only:
            continue
        if done(st, t["id"], a.retry_missing):
            continue
        groups.setdefault((t["year"], t["uf"]), []).append(t)
    for i, ((year, uf), items) in enumerate(sorted(groups.items(), key=lambda kv: (kv[0][0] in (2020, 2024), kv[0]))):
        t0 = time.time()
        ok = run_zip(st, year, uf, items)
        write_state(st)
        print(f"[{i + 1}/{len(groups)}] {year} {uf}: {ok}/{len(items)} fotos em {time.time() - t0:.0f}s", flush=True)
    for pid, m in MANUAL.items():  # recurso final: foto oficial fora do TSE para quem o TSE não cobriu
        if m.get("fallback_only") and pid in st["missing"] and (not only or m["office"] in only):
            run_manual(st, pid)
    write_state(st)
    sys.exit(check())


if __name__ == "__main__":
    main()
