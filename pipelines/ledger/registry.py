"""Source registry (spec 4.5): fetch a source once, hash it while it streams, record the release.

Raw files are never kept: fetch() writes into a temporary folder that is deleted when the with-block ends.
Disk rules: nothing above 200 MB, and stop when the free space falls below 5 GB.
Downloads go through curl, which uses the system's certificate store (some Python builds ship without one);
the bytes are hashed as they come out of curl."""
import contextlib
import hashlib
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

MAX_BYTES = 200 * 1024 * 1024
MIN_FREE = 5 * 1024 ** 3
CHUNK = 1 << 20
UA = "Mozilla/5.0 (Brasil-Imposto ledger)"


class TooBig(Exception):
    pass


class LowDisk(Exception):
    pass


class DownloadError(Exception):
    pass


@dataclass
class Fetched:
    url: str
    sha256: str
    bytes: int
    path: Path          # temporary; gone after the with-block
    fetched_at: datetime


def _download(url, out, data, headers, max_bytes, timeout):
    cmd = ["curl", "-sS", "-L", "--fail", "--max-time", str(timeout), "--max-filesize", str(max_bytes), "-A", UA]
    for name, value in (headers or {}).items():
        cmd += ["-H", f"{name}: {value}"]
    if data is not None:
        cmd += ["--data-binary", "@-"]
    digest, n = hashlib.sha256(), 0
    stdin = subprocess.PIPE if data is not None else subprocess.DEVNULL
    with subprocess.Popen(cmd + [url], stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc, \
            open(out, "wb") as f:
        if data is not None:
            proc.stdin.write(data)
            proc.stdin.close()
        while chunk := proc.stdout.read(CHUNK):
            n += len(chunk)
            if n > max_bytes:
                proc.kill()
                raise TooBig(f"{url} passed {max_bytes} bytes while downloading")
            digest.update(chunk)
            f.write(chunk)
        err = proc.stderr.read().decode("utf-8", "replace").strip()
        code = proc.wait()
    if code == 63:
        raise TooBig(f"{url} announces more than {max_bytes} bytes")
    if code != 0:
        raise DownloadError(f"curl exit {code} for {url}: {err}")
    return digest.hexdigest(), n


@contextlib.contextmanager
def fetch(url, *, data=None, headers=None, suffix="", max_bytes=MAX_BYTES, min_free=MIN_FREE, timeout=600, attempts=3):
    free = shutil.disk_usage(Path.home()).free
    if free < min_free:
        raise LowDisk(f"free disk {free / 1024 ** 3:.1f} GB is below {min_free / 1024 ** 3:.0f} GB")
    tmp = Path(tempfile.mkdtemp(prefix="bi-ledger-"))
    try:
        out = tmp / f"source{suffix}"   # openpyxl reads a workbook only when the name ends in .xlsx
        for attempt in range(1, attempts + 1):
            try:
                sha, n = _download(url, out, data, headers, max_bytes, timeout)
                break
            except (DownloadError, OSError):
                if attempt == attempts:
                    raise
                time.sleep(10 * attempt)
        yield Fetched(url, sha, n, out, datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def current(con, dataset):
    rows = con.execute("SELECT source_id FROM current_release WHERE dataset = ? ORDER BY source_id", [dataset]).fetchall()
    return [r[0] for r in rows]


def register(con, dataset, fx, *, title, publisher, loader, url=None, page_url=None, published_on=None,
             published_note=None):
    """(source_id, is_new). The same file twice is one release; a different file supersedes the current one. When the
    publisher puts back a file it had replaced (A, B, A), that release is the current one again: it supersedes what was current,
    and its own old supersede record goes, since a release is superseded at most once (release_supersede's key)."""
    row = con.execute("SELECT source_id FROM source_release WHERE dataset = ? AND sha256 = ?", [dataset, fx.sha256]).fetchone()
    if row:
        known = row[0]
        previous = current(con, dataset)
        if known not in previous:
            con.execute("DELETE FROM release_supersede WHERE old_source_id = ?", [known])
            for old in previous:
                con.execute("INSERT INTO release_supersede VALUES (?, ?, ?)", [old, known, fx.fetched_at])
        return known, False
    source_id = f"{dataset}@{fx.sha256[:12]}"
    previous = current(con, dataset)
    con.execute("INSERT INTO source_release VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [source_id, dataset, title, publisher, url or fx.url, page_url, published_on, published_note,
                 fx.sha256, fx.bytes, fx.fetched_at, loader])
    for old in previous:
        con.execute("INSERT INTO release_supersede VALUES (?, ?, ?)", [old, source_id, fx.fetched_at])
    return source_id, True
