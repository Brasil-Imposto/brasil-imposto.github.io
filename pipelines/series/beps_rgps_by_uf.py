"""RGPS benefits emitted by UF, monthly, from the Boletim Estatistico da Previdencia Social (BEPS), table 19.

Usage: beps_rgps_by_uf.py <workdir>   (needs xlrd; writes <workdir>/beps_rgps_uf.json)
Lists the BEPS folders on gov.br/previdencia (with pagination), downloads every .xls, reads table 19
("BENEFICIOS DO RGPS EMITIDOS, POR CLIENTELA, SEGUNDO AS UNIDADES DA FEDERACAO", the value the AEPS also uses, net of the
payroll-loan deductions) and table 18 ("... POR FAIXAS DE VALOR, SEGUNDO AS UNIDADES DA FEDERACAO", the benefit value before
deductions and without occasional credits), keeps quantity and value per UF,
takes the reference month from the date serial in the sheet header, and deletes the file.
When one month has several uploads (e.g. _final and _final-1), all are read and compared.
"""
import datetime, json, os, re, subprocess, sys, unicodedata
import xlrd

W = sys.argv[1]; D = os.path.join(W, "beps"); os.makedirs(D, exist_ok=True)
B = "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/Dados-estatisticos-previdencia-social-e-inss/boletins-da-previdencia-social"
FOLDERS = ["", "2019", "2020", "2021", "2022", "2023-1", "2024-1", "2025", "2026"]
UFN = {'Rondônia':'RO','Acre':'AC','Amazonas':'AM','Roraima':'RR','Pará':'PA','Amapá':'AP','Tocantins':'TO','Maranhão':'MA','Piauí':'PI','Ceará':'CE',
       'Rio Grande do Norte':'RN','Paraíba':'PB','Pernambuco':'PE','Alagoas':'AL','Sergipe':'SE','Bahia':'BA','Minas Gerais':'MG','Espírito Santo':'ES',
       'Rio de Janeiro':'RJ','São Paulo':'SP','Paraná':'PR','Santa Catarina':'SC','Rio Grande do Sul':'RS','Mato Grosso do Sul':'MS','Mato Grosso':'MT',
       'Goiás':'GO','Distrito Federal':'DF'}
def norm(s): return " ".join(unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper().split())
UFN = {norm(k): v for k, v in UFN.items()}

def get(url, out):
    return subprocess.run(["curl", "-sS", "-L", "-m", "300", "-A", "Mozilla/5.0", "-o", out, url]).returncode == 0

links = set()
for f in FOLDERS:
    for start in (0, 20, 40, 60):
        u = f"{B}/{f}" + (f"?b_start:int={start}" if start else "")
        p = os.path.join(D, "list.html")
        if not get(u, p): continue
        html = open(p, encoding="utf-8", errors="ignore").read()
        found = {re.sub(r"/view$", "", h) for h in re.findall(r'href="(https://www\.gov\.br/previdencia/[^"]+?\.xls(?:/view)?)"', html)}
        new = found - links
        links |= found
        if start and not new: break
os.remove(os.path.join(D, "list.html"))
links = sorted(l for l in links if "copy_of" not in l and "eng" not in l.lower() and "esp" not in l.lower().rsplit("/", 1)[-1][:12] + "")

def xl_month(serial):
    d = datetime.date(1899, 12, 30) + datetime.timedelta(days=int(serial))
    return f"{d.year}-{d.month:02d}"

res = {}
for url in links:
    fn = os.path.join(D, "tmp.xls")
    if not get(url, fn): print("FAIL", url, flush=True); continue
    try:
        wb = xlrd.open_workbook(fn)
    except Exception as e:
        print("NOT XLS", url, e, flush=True); os.remove(fn); continue
    sheet = sheet18 = None
    for s in wb.sheets():
        txt = " ".join(norm(s.cell_value(r, c)) for r in range(min(5, s.nrows)) for c in range(min(4, s.ncols)))
        if "EMITIDOS" in txt and "UNIDADES DA FEDERACAO" in txt and "RGPS" in txt:
            if "CLIENTELA" in txt and "FAIXAS" not in txt and sheet is None: sheet = s
            elif "FAIXAS" in txt and sheet18 is None: sheet18 = s
    if sheet is None:
        print("NO TABLE", url, flush=True); os.remove(fn); continue
    ref = None
    for r in range(3):
        for c in range(sheet.ncols):
            v = sheet.cell_value(r, c)
            if isinstance(v, float) and 36000 < v < 50000: ref = xl_month(v)
    def read(sh):
        # both layouts: quantity total first, then 5 more columns (shares or value bands), then VALUE total at position 6
        out = {}
        for r in range(sh.nrows):
            k = norm(sh.cell_value(r, 0))
            if k in UFN or k == "BRASIL":
                nums = [x for x in (sh.cell_value(r, c) for c in range(1, sh.ncols)) if isinstance(x, float)]
                out[UFN.get(k, "BR")] = {"quantity": nums[0], "value": nums[6]}
        return out
    uf = read(sheet); uf18 = read(sheet18) if sheet18 is not None else None
    os.remove(fn)
    res[url] = {"reference_month": ref, "sheet": sheet.name, "uf": uf, "sheet_18": sheet18.name if sheet18 is not None else None, "uf_18": uf18}
    print(ref, sheet.name, len(uf), round(uf.get("BR", {}).get("value", 0) / 1e9, 3), "t18", round((uf18 or {}).get("BR", {}).get("value", 0) / 1e9, 3), url.rsplit("/", 1)[-1], flush=True)
json.dump(res, open(os.path.join(W, "beps_rgps_uf.json"), "w"), ensure_ascii=False, indent=0)
print("DONE", len(res))
