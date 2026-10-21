"""INSS benefits emitted by UF, annual, from the Anuario Estatistico da Previdencia Social (AEPS), table B.15 (includes BPC/LOAS).

Usage: aeps_inss_by_uf.py <workdir>   (needs openpyxl; downloads each AEPS zip into <workdir>/aeps, reads B.15, deletes the zip)
Each edition's B.15 carries three years; the value used for year Y is the one in edition Y, and the later editions are kept
under "revisions" so any change is visible. Values in the table are R$ mil; the output is in R$.
"""
import io, json, os, subprocess, sys, unicodedata, warnings, zipfile
import openpyxl
warnings.filterwarnings("ignore")
W = os.path.join(sys.argv[1], "aeps"); os.makedirs(W, exist_ok=True)
A = "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/arquivos/"
EDITIONS = {2019: "aeps-2019-xlsx-3.zip", 2020: "aeps_2020_xlsx-2.zip", 2021: "aeps_2021-xls.zip", 2022: "aeps_2022_xlsx.zip",
            2023: "aeps_2023_xlsx.zip", 2024: "aeps_2024.zip"}
UFN = {'Rondônia':'RO','Acre':'AC','Amazonas':'AM','Roraima':'RR','Pará':'PA','Amapá':'AP','Tocantins':'TO','Maranhão':'MA','Piauí':'PI','Ceará':'CE',
       'Rio Grande do Norte':'RN','Paraíba':'PB','Pernambuco':'PE','Alagoas':'AL','Sergipe':'SE','Bahia':'BA','Minas Gerais':'MG','Espírito Santo':'ES',
       'Rio de Janeiro':'RJ','São Paulo':'SP','Paraná':'PR','Santa Catarina':'SC','Rio Grande do Sul':'RS','Mato Grosso do Sul':'MS','Mato Grosso':'MT',
       'Goiás':'GO','Distrito Federal':'DF','BRASIL':'BR'}
def norm(s): return " ".join(unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper().split())
UFN = {norm(k): v for k, v in UFN.items()}

out = {"by_edition": {}, "files": {}}
for ed, fn in EDITIONS.items():
    zp = os.path.join(W, f"aeps_{ed}.zip")
    if not (os.path.exists(zp) and zipfile.is_zipfile(zp)):
        for _ in range(3):
            subprocess.run(["curl", "-sS", "-L", "-A", "Mozilla/5.0", "-m", "600", "-C", "-", "-o", zp, A + fn])
            if zipfile.is_zipfile(zp): break
    z = zipfile.ZipFile(zp)
    found = None
    for info in z.infolist():
        base = info.filename.rsplit("/", 1)[-1].upper()
        if not base.endswith(".XLSX") or "EMITIDOS" not in info.filename.upper(): continue
        if not ("SB15" in base or "SB_15" in base): continue
        found = info.filename
    if not found:
        print(ed, "B.15 not found"); continue
    ws = openpyxl.load_workbook(io.BytesIO(z.read(found)), read_only=True, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    title = " ".join(str(c) for r in rows[:3] for c in r if c)
    assert "B.15" in title and "emitidos" in title.lower(), title
    yr_row = next(r for r in rows if r and any(isinstance(c, (int, float)) and 2000 < c < 2100 or (isinstance(c, str) and c.strip().isdigit() and 2000 < int(c) < 2100) for c in r[1:4]))
    years = [int(c) for c in yr_row[1:4]]
    vals = {}
    for r in rows:
        k = norm(r[0]) if r and r[0] else ""
        if k in UFN:
            vals[UFN[k]] = {y: float(r[1 + i]) * 1000 for i, y in enumerate(years)}
    out["by_edition"][ed] = vals
    out["files"][ed] = {"url": A + fn, "table": found.rsplit("/", 1)[-1], "years_in_table": years}
    z.close(); os.remove(zp)
    print(ed, found.rsplit("/", 1)[-1], years, "UFs", len(vals), "BR", {y: round(v / 1e9, 2) for y, v in vals["BR"].items()}, flush=True)

annual, revisions = {}, {}
for y in range(2019, 2025):
    ed = out["by_edition"].get(y)
    annual[y] = {uf: v[y] for uf, v in ed.items()} if ed else None
    for later in range(y + 1, 2025):
        e2 = out["by_edition"].get(later)
        if e2 and ed and y in e2["BR"]:
            diff = {uf: round(e2[uf][y] - ed[uf][y], 2) for uf in ed if uf in e2 and abs(e2[uf][y] - ed[uf][y]) > 0.5}
            if diff: revisions.setdefault(y, {})[later] = diff
out["annual"] = annual; out["revisions"] = revisions
json.dump(out, open(os.path.join(sys.argv[1], "aeps_inss_uf.json"), "w"), ensure_ascii=False, indent=0)
print("revisions:", {y: {e: len(d) for e, d in v.items()} for y, v in revisions.items()})
