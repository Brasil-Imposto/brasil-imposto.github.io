"""Legislative activity of each politician (D62, the "Influência" bar): bills authored and what happened to each one.

Usage: python3 pipelines/politicians/legislative_activity.py [--raw DIR] [--control]
Sources (official, open):
  Câmara: dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-YYYY.csv and
          .../proposicoesAutores/csv/proposicoesAutores-YYYY.csv (2019 to the current year)
  Senado: legis.senado.leg.br/dadosabertos/processo?codigoParlamentarAutor=<code> (one file per senator)
  Medidas provisórias of the President: legis.senado.leg.br/dadosabertos/processo?sigla=MPV&ano=YYYY
Disk: every raw file goes to a temporary folder and is deleted at the end (--raw reuses a folder that already holds them).
Output: data/politicians/legislative-activity.json (English keys). Counts only; how the bar is drawn is decided on screen.
Check: per house, the authorships counted for people equal the authorship rows in the files for the same scope;
--control drops one authorship and must fail. Nothing is written when the check fails.
"""
import collections, csv, json, os, re, shutil, subprocess, sys, tempfile
from bill_outcomes import OUTCOMES, camara_outcome, senado_outcome

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
CONTROL = "--control" in sys.argv
RAW = sys.argv[sys.argv.index("--raw") + 1] if "--raw" in sys.argv else None
TMP = RAW or tempfile.mkdtemp(prefix="bi-activity-")
YEARS = range(2019, 2027)
START = "2019-02-01"
BILLS = {"PL", "PLP", "PEC", "PDL"}
get = lambda url, path: os.path.exists(path) or subprocess.run(["curl", "-sS", "-L", "-m", "600", "-A", "Mozilla/5.0", "-o", path, url], check=True)
# ---------- Câmara: the last official status of each bill (bill_outcomes.camara_outcome)
people = collections.defaultdict(lambda: {"main_author": collections.defaultdict(lambda: collections.Counter()),
                                          "co_author": collections.defaultdict(lambda: collections.Counter())})
mapping = collections.defaultdict(collections.Counter)
expected_camara = counted_camara = 0
for y in YEARS:
    p, a = os.path.join(TMP, f"p{y}.csv"), os.path.join(TMP, f"a{y}.csv")
    get(f"https://dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-{y}.csv", p)
    get(f"https://dadosabertos.camara.leg.br/arquivos/proposicoesAutores/csv/proposicoesAutores-{y}.csv", a)
    bills = {}
    with open(p, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["siglaTipo"] in BILLS and r["dataApresentacao"][:10] >= START:
                o = camara_outcome(r["ultimoStatus_descricaoSituacao"], r["ultimoStatus_despacho"])
                bills[r["id"]] = (r["siglaTipo"], o); mapping[r["ultimoStatus_descricaoSituacao"] or "(vazio)"][o] += 1
    with open(a, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            b = bills.get(r["idProposicao"])
            if not b or not r["idDeputadoAutor"] or r["proponente"] != "1": continue
            expected_camara += 1
            role = "main_author" if r["ordemAssinatura"] == "1" else "co_author"
            people[f"camara:{r['idDeputadoAutor']}"][role][b[0]][b[1]] += 1
counted_camara = sum(sum(c.values()) for k, v in people.items() if k.startswith("camara:") for role in v.values() for c in role.values())

# ---------- Senado: one file per senator of the period; main author = the senator is the first name in "autoria"
norm = lambda s: re.sub(r"[^a-z]", "", s.lower().encode("ascii", "ignore").decode())
sen = json.load(open(P("data/politicians/senators.json")))
senators = {p["id"]: p for v in sen["by_uf"].values() for p in (v if isinstance(v, list) else [])}
os.makedirs(os.path.join(TMP, "sen"), exist_ok=True)
expected_senado = 0
for sid, sp in senators.items():
    code = sid.split(":")[1]; f = os.path.join(TMP, "sen", f"{code}.json")
    get(f"https://legis.senado.leg.br/dadosabertos/processo?codigoParlamentarAutor={code}", f)
    names = {norm(sp["name"]), norm(sp.get("full_name", ""))}
    for x in json.load(open(f)):
        t = (x.get("identificacao") or "").split(" ")[0]
        if t not in BILLS or (x.get("dataApresentacao") or "")[:10] < START: continue
        first = norm(re.sub(r"^Senador[a]?\s+", "", (x.get("autoria") or "").split(",")[0].split("(")[0]).strip())
        o = senado_outcome(x); mapping[f"Senado: {x.get('siglaTipoDeliberacao') or '(sem deliberação)'} / tramitando={x.get('tramitando')}"][o] += 1
        people[sid]["main_author" if any(n and (first.startswith(n) or n.startswith(first)) for n in names) else "co_author"][t][o] += 1
        expected_senado += 1
counted_senado = sum(sum(c.values()) for k, v in people.items() if k.startswith("senado:") for role in v.values() for c in role.values())

# ---------- President: medidas provisórias issued in the period and what became of each
MPV = {"approved": "converted_into_law", "rejected": "rejected"}
mps = collections.defaultdict(collections.Counter)
for y in YEARS:
    f = os.path.join(TMP, f"mpv{y}.json")
    get(f"https://legis.senado.leg.br/dadosabertos/processo?sigla=MPV&ano={y}", f)
    for x in json.load(open(f)):
        if (x.get("identificacao") or "").startswith("MPV") and (x.get("dataApresentacao") or "") >= "2019-01-01":
            d = x.get("siglaTipoDeliberacao")
            o = "converted_into_law" if d == "APROVADO_PLV" or d == "APROVADO_NA_INTEGRA" or "NORMA JUR" in (x.get("situacaoAtual") or "").upper() else \
                "rejected" if (d or "").startswith("REJEITADO") else "lost_efficacy" if d in ("PERDA_EFICACIA", "SEM_EFICACIA") else \
                "in_progress" if x.get("tramitando") == "Sim" else "other"
            mps[x["dataApresentacao"][:4]][o] += 1

if CONTROL:
    k = next(k for k in people if k.startswith("camara:")); role = people[k]["main_author"] or people[k]["co_author"]
    t = next(iter(role)); role[t][next(iter(role[t]))] -= 1; counted_camara -= 1
check = {"camara_authorship_rows": expected_camara, "camara_counted": counted_camara,
         "senado_authorship_rows": expected_senado, "senado_counted": counted_senado,
         "passed": expected_camara == counted_camara and expected_senado == counted_senado, "control_run": CONTROL}
print(json.dumps(check, indent=1))
if not check["passed"]:
    raise SystemExit("CHECK FAILED")  # nothing is written when the check fails
if not CONTROL:
    out = {"title": "Legislative activity per politician, 2019-02-01 to the collection date", "collected_on": "2026-10-02", "period": [START, "2026-10-02"],
           "definitions": {"scope": "Bills (PL, PLP, PEC, PDL) presented in the period. Câmara: proponente = 1; main author = first signatory (ordemAssinatura 1), co-author = the other proponents (RICD art. 102). Senado: main author = first name in the 'autoria' field.",
                           "outcome": "Last official status of each bill. Câmara: the situation, and for 'Arquivada' the reason written in the despacho. Senado: the deliberation code (siglaTipoDeliberacao) and the current situation.",
                           "outcomes": OUTCOMES},
           "status_mapping": {k: dict(v) for k, v in sorted(mapping.items())},
           "people": {k: {role: {t: dict(c) for t, c in v[role].items()} for role in ("main_author", "co_author")} for k, v in people.items()},
           "president_mps": {y: dict(c) for y, c in sorted(mps.items())},
           "state_deputies": {"available": False, "reason": "No uniform open source covers the 27 state assemblies."},
           "sources": ["https://dadosabertos.camara.leg.br/swagger/api.html (Arquivos: proposicoes, proposicoesAutores)",
                       "https://legis.senado.leg.br/dadosabertos/processo", "https://legis.senado.leg.br/dadosabertos/processo?sigla=MPV"],
           "check": check}
    json.dump(out, open(P("data/politicians/legislative-activity.json"), "w"), ensure_ascii=False)
if not RAW: shutil.rmtree(TMP, ignore_errors=True)
