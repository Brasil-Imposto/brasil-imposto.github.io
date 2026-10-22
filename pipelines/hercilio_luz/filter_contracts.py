"""Filter the SC state contracts CSV (dados.sc.gov.br, SEF/SIGEF) for Ponte Hercilio Luz records.

Usage: python3 filter_contracts.py <contratos.csv> <out.json>
Filter: "PONTE" and "HERCILIO" (accent-insensitive) in OBJETO, RESUMO or NMBEMPUBLICO/BEMPUBLICO.
"""
import csv
import json
import sys
import unicodedata

csv.field_size_limit(10**9)


def norm(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()


def main(src, dst):
    rows = []
    with open(src, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f, delimiter=";")
        for row in r:
            hay = norm(" ".join((row.get(k) or "") for k in ("OBJETO", "RESUMO", "NMBEMPUBLICO", "BEMPUBLICO")))
            if "PONTE" in hay and "HERCILIO" in hay:
                rows.append(row)
    rows.sort(key=lambda x: x["DTASSINATURA"])
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print(len(rows), "rows")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
