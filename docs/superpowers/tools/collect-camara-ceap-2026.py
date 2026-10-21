"""The housing-allowance complement each deputy is paid out of the cota (CEAP) in 2026, month by month, from the Câmara's
own file of every cota reimbursement.

Why: a deputy who receives the housing allowance can have it topped up from the cota ("Complementação do auxílio-moradia").
The deputy's page counts that money as cota used, so on the sheet it sat in "mandato e equipe"; it is housing paid to the
person, so the sheet shows it as its own row on the person's side. Checked on Erika Hilton, 2026-10-21: the gap between her
deputy page and the Câmara's cota consultation is exactly twice the complement every month (the page adds it, the
consultation subtracts it, as the file records it with a negative net value).

Source: https://www.camara.leg.br/cotas/Ano-2026.csv.zip (one line per document; txtDescricao, vlrDocumento, numMes, ideCadastro).
Usage: .venv/bin/python -B docs/superpowers/tools/collect-camara-ceap-2026.py
Writes data/federal/raw-pay/camara-ceap/housing-complement-2026.json (gitignored folder) and deletes the unzipped CSV.
"""
import csv, json, subprocess, zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "federal" / "raw-pay" / "camara-ceap"
ZIP = RAW / "Ano-2026.csv.zip"
RAW.mkdir(parents=True, exist_ok=True)
subprocess.run(["curl", "-sS", "-L", "--compressed", "-m", "900", "-A", "Mozilla/5.0", "-o", str(ZIP), "https://www.camara.leg.br/cotas/Ano-2026.csv.zip"], check=True)
by_dep = defaultdict(lambda: defaultdict(float))
lines = 0
with zipfile.ZipFile(ZIP) as z, z.open(z.namelist()[0]) as fh:
    for r in csv.DictReader((l.decode("utf-8-sig") for l in fh), delimiter=";"):
        if r["txtDescricao"].strip().upper().startswith("COMPLEMENTAÇÃO DO AUXÍLIO-MORADIA") and r["ideCadastro"]:
            by_dep[r["ideCadastro"]][int(r["numMes"])] += float(r["vlrDocumento"] or 0)
            lines += 1
out = {"read_on": "2026-10-21", "source": "https://www.camara.leg.br/cotas/Ano-2026.csv.zip", "lines": lines,
       "by_deputy": {d: {str(m): round(v, 2) for m, v in sorted(ms.items())} for d, ms in sorted(by_dep.items())}}
(RAW / "housing-complement-2026.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("deputies with a complement:", len(by_dep), "| lines:", lines)
