"""Fills the SICONFI cache for the municipalities of one state (default Santa Catarina, 295; Rio Grande do Sul has 497):
RREO Anexos 01, 02, 03 and 06 of the 6th bimester of 2021 to 2025 and of the latest bimester published in 2026, and RGF
Anexo 02 of the last period filed in each year. Small municipalities file "RREO Simplificado" and a semiannual "RGF
Simplificado", so both report types and both periodicities are tried.
Run: python3 data/scripts/series/fetch_municipal_series.py [--uf RS] [--workers 6]   (resumes from the cache; at most
--workers requests at a time, default 6; the API answers HTTP 429 when pressed, and the client then waits longer)
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from fetch_state_series import fetch_rreo_period
from siconfi_client import CURRENT_YEAR, EntityCache, Progress, entes

YEARS = range(2021, CURRENT_YEAR)  # closed years: 6th bimester
RGF_YEAR_END = [("Q", 3, "RGF"), ("S", 2, "RGF Simplificado"), ("S", 2, "RGF"), ("Q", 3, "RGF Simplificado")]
RGF_PARTIAL = [("Q", 2, "RGF"), ("Q", 2, "RGF Simplificado"), ("S", 1, "RGF Simplificado"), ("S", 1, "RGF"),
               ("Q", 1, "RGF"), ("Q", 1, "RGF Simplificado")]


def last_closed_bimester(today=None):
    """The last bimester of the current year that has already ended (its report may or may not be filed yet)."""
    today = today or date.today()
    return (today.month - 1) // 2 if today.year == CURRENT_YEAR else 6


def current_year_rgf(today=None):
    today = today or date.today()
    q = (today.month - 1) // 4  # quadrimesters already ended
    s = (today.month - 1) // 6
    out = [(p, n, t) for (p, n, t) in RGF_PARTIAL if (p == "Q" and n <= q) or (p == "S" and n <= s)]
    return sorted(out, key=lambda x: -(x[1] * (4 if x[0] == "Q" else 6)))


def fetch_rgf(cache, ente, year, candidates):
    for periodicity, period, tipo in candidates:
        if cache.rgf(year, periodicity, period, tipo, "M", ente)["status"] == "ok":
            return periodicity, period, tipo
    return None


def fetch_municipality(ente):
    cache = EntityCache("M", ente)
    for year in YEARS:
        fetch_rreo_period(cache, "M", ente, year, 6)
        fetch_rgf(cache, ente, year, RGF_YEAR_END + RGF_PARTIAL)
    for period in range(last_closed_bimester(), 0, -1):
        tipo = fetch_rreo_period(cache, "M", ente, CURRENT_YEAR, period)
        if tipo:
            break
    # Municipalities under 50,000 inhabitants may publish Anexos 03 and 06 by semester (LRF art. 63, II, c): when
    # the latest bimester lacks them, also fetch the latest earlier bimester that has them.
    if tipo and not any(cache.rreo(CURRENT_YEAR, period, t, "M", ente, "RREO-Anexo 03")["status"] == "ok"
                        for t in (tipo,)):
        for earlier in range(period - 1, 0, -1):
            t = fetch_rreo_period(cache, "M", ente, CURRENT_YEAR, earlier)
            if t and cache.rreo(CURRENT_YEAR, earlier, t, "M", ente, "RREO-Anexo 03")["status"] == "ok":
                break
    fetch_rgf(cache, ente, CURRENT_YEAR, current_year_rgf())
    return ente


def uf_arg(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    return argv[argv.index("--uf") + 1].upper() if "--uf" in argv else "SC"


def municipalities(uf):
    return sorted((e for e in entes() if e["esfera"] == "M" and e["uf"] == uf), key=lambda e: e["cod_ibge"])


if __name__ == "__main__":
    UF = uf_arg()
    ms = municipalities(UF)
    print(len(ms), "municipalities in", UF, flush=True)
    progress = Progress(len(ms), every=15, label="municipalities")
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for _ in pool.map(fetch_municipality, [e["cod_ibge"] for e in ms]):
            progress.tick()
