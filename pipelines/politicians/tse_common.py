"""Leitura do cadastro de candidaturas do TSE (consulta_cand), compartilhada pelos scripts de politicos.

Os zips ficam num diretorio de trabalho fora do repositorio (variavel POLITICIANS_WORK,
padrao /tmp/politicians-work). Cada zip traz um CSV por UF, em latin-1, separado por ';'.

RemoteZip le um zip do CDN do TSE por HTTP Range, sem grava-lo em disco: o indice e depois so os membros pedidos
(usado por build_mayors.py e collect_photos.py).
"""
import csv
import io
import os
import pathlib
import time
import urllib.request
import zipfile
import zlib

TSE_CAND_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{year}.zip"
WORK = pathlib.Path(os.environ.get("POLITICIANS_WORK", "/tmp/politicians-work"))
ELECTED = {"ELEITO", "ELEITO POR QP", "ELEITO POR MÉDIA"}
UA = "BrasilImposto/0.1 (pesquisa civica; dados abertos do TSE)"


def cand_zip(year):
    """Baixa (uma vez) e devolve o caminho do zip do ano."""
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK / "tse" / f"consulta_cand_{year}.zip"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        urllib.request.urlretrieve(TSE_CAND_URL.format(year=year), path)
    return path


def iter_rows(year, ufs=None, cargos=None, elected_only=True):
    """Linhas do consulta_cand do ano, filtradas por UF, cargo e situacao final."""
    z = zipfile.ZipFile(cand_zip(year))
    for name in sorted(z.namelist()):
        if not name.endswith(".csv") or name.endswith("_BRASIL.csv"):
            continue
        uf = name.rsplit("_", 1)[1][:-4]
        if ufs and uf not in ufs:
            continue
        reader = csv.DictReader(io.TextIOWrapper(z.open(name), encoding="latin-1"), delimiter=";")
        for row in reader:
            if cargos and row["DS_CARGO"] not in cargos:
                continue
            if elected_only and row["DS_SIT_TOT_TURNO"] not in ELECTED:
                continue
            yield row


def br_date(s):
    """'dd/mm/aaaa' para 'aaaa-mm-dd'; None se vazio ou nulo."""
    if not s or s.startswith("#"):
        return None
    d, m, y = s.split("/")
    return f"{y}-{m}-{d}"


# ---------------------------------------------------------------- HTTP com Range

def http_open(url, headers=None, tries=6):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.status, dict(r.headers), r.read()
        except Exception as e:  # rede instavel: tenta de novo com espera crescente
            if attempt == tries - 1:
                raise RuntimeError(f"{url}: {e}") from e
            time.sleep(2 * (attempt + 1))


def http_size(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.headers.get("Accept-Ranges", "").lower() != "bytes":
            raise RuntimeError(f"{url}: servidor nao anuncia Range")
        return int(r.headers["Content-Length"])


def http_range(url, start, end):
    status, _, body = http_open(url, {"Range": f"bytes={start}-{end - 1}"})
    if status != 206:
        raise RuntimeError(f"{url}: Range devolveu {status}")
    return body


class RangeFile(io.RawIOBase):
    """Arquivo remoto somente leitura, com leitura antecipada de 256 KB, para o zipfile ler o indice."""

    def __init__(self, url, size):
        self.url, self.size, self.pos, self.buf_start, self.buf = url, size, 0, -1, b""

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        end = min(self.pos + n, self.size)
        if end <= self.pos:
            return b""
        if not (self.buf_start <= self.pos and end <= self.buf_start + len(self.buf)):
            self.buf_start = self.pos
            self.buf = http_range(self.url, self.pos, min(max(end, self.pos + 262144), self.size))
        o = self.pos - self.buf_start
        out = self.buf[o:o + end - self.pos]
        self.pos += len(out)
        return out


class RemoteZip:
    def __init__(self, url):
        self.url = url
        self.size = http_size(url)
        self.infos = zipfile.ZipFile(RangeFile(url, self.size)).infolist()

    def read(self, info):
        """Uma requisicao por membro: cabecalho local + dados; confere o CRC."""
        start = info.header_offset
        end = min(start + 30 + len(info.filename.encode()) + 2048 + info.compress_size, self.size)
        b = http_range(self.url, start, end)
        if b[:4] != b"PK\x03\x04":
            raise RuntimeError(f"{info.filename}: cabecalho local invalido")
        n, e = int.from_bytes(b[26:28], "little"), int.from_bytes(b[28:30], "little")
        data = b[30 + n + e:30 + n + e + info.compress_size]
        if len(data) < info.compress_size:
            data += http_range(self.url, start + 30 + n + e + len(data), start + 30 + n + e + info.compress_size)
        if info.compress_type == zipfile.ZIP_DEFLATED:
            data = zlib.decompressobj(-15).decompress(data)
        elif info.compress_type != zipfile.ZIP_STORED:
            raise RuntimeError(f"{info.filename}: compressao {info.compress_type} nao suportada")
        if zlib.crc32(data) & 0xFFFFFFFF != info.CRC:
            raise RuntimeError(f"{info.filename}: CRC nao confere")
        return data

    def member(self, name):
        """Bytes de um membro pelo nome exato."""
        return self.read(next(i for i in self.infos if i.filename == name))


def uf_rows(year, uf, cargos=None, elected_only=False):
    """Linhas do consulta_cand do ano so para a UF, lidas por HTTP Range (nada gravado em disco)."""
    data = RemoteZip(TSE_CAND_URL.format(year=year)).member(f"consulta_cand_{year}_{uf}.csv")
    # Mesma decodificacao de iter_rows (TextIOWrapper em latin-1), para as linhas sairem iguais as do zip inteiro.
    for row in csv.DictReader(io.TextIOWrapper(io.BytesIO(data), encoding="latin-1"), delimiter=";"):
        if cargos and row["DS_CARGO"] not in cargos:
            continue
        if elected_only and row["DS_SIT_TOT_TURNO"] not in ELECTED:
            continue
        yield row
