"""Fills the SICONFI cache for the 27 state governments: RREO Anexos 01, 02, 03 and 06 for every bimester from 2019
to the latest published, and RGF Anexo 02 (the last quadrimester filed in each year, which carries the earlier
quadrimesters as columns). Both report types are tried ("RREO" then "RREO Simplificado"; "RGF" then
"RGF Simplificado"), a lesson from the municipal collection.
Run: python3 data/scripts/series/fetch_state_series.py   (resumes from the cache; at most 6 requests at a time)
"""
from concurrent.futures import ThreadPoolExecutor

from siconfi_client import CURRENT_YEAR, EntityCache, Progress

UF_CODES = {11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO", 21: "MA", 22: "PI", 23: "CE",
            24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA", 31: "MG", 32: "ES", 33: "RJ", 35: "SP",
            41: "PR", 42: "SC", 43: "RS", 50: "MS", 51: "MT", 52: "GO", 53: "DF"}
FIRST_YEAR = 2019
RREO_TYPES = ["RREO", "RREO Simplificado"]
RGF_TYPES = ["RGF", "RGF Simplificado"]
ANNEXES = ["RREO-Anexo 01", "RREO-Anexo 02", "RREO-Anexo 03", "RREO-Anexo 06"]


def fetch_rreo_period(cache, esfera, ente, year, period, annexes=ANNEXES):
    """Returns the report type that answered, or None. Anexo 01 decides the type; the others follow it."""
    for tipo in RREO_TYPES:
        if cache.rreo(year, period, tipo, esfera, ente, annexes[0])["status"] == "ok":
            for anexo in annexes[1:]:
                if cache.rreo(year, period, tipo, esfera, ente, anexo)["status"] != "ok":
                    other = [t for t in RREO_TYPES if t != tipo][0]
                    cache.rreo(year, period, other, esfera, ente, anexo)
            return tipo
    return None


def fetch_rgf_year(cache, esfera, ente, year):
    """The last period filed in the year: quadrimester 3..1 or semester 2..1, both report types."""
    for periodicity, periods in (("Q", (3, 2, 1)), ("S", (2, 1))):
        for period in periods:
            for tipo in RGF_TYPES:
                if cache.rgf(year, periodicity, period, tipo, esfera, ente)["status"] == "ok":
                    return periodicity, period, tipo
    return None


def fetch_state(code):
    cache = EntityCache("E", code)
    for year in range(FIRST_YEAR, CURRENT_YEAR + 1):
        for period in range(1, 7):
            tipo = fetch_rreo_period(cache, "E", code, year, period)
            if tipo is None and year == CURRENT_YEAR:
                break  # later bimesters of the current year are not published yet
        fetch_rgf_year(cache, "E", code, year)
    return code


if __name__ == "__main__":
    progress = Progress(len(UF_CODES), every=1, label="states")
    with ThreadPoolExecutor(max_workers=6) as pool:
        for code in pool.map(fetch_state, UF_CODES):
            print(UF_CODES[code], "done", flush=True)
            progress.tick()
