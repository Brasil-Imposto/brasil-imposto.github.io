"""Every bill each federal parliamentarian in office has presented in their house, and what happened to it, for the
sheets of "Os 3 Poderes" (D142 and after).

Sources (official, open, no key):
  Câmara: dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-YYYY.csv and proposicoesAutores-YYYY.csv for
          every year from 1987 (the Constituinte) to the current one. A bill is kept when a deputy in office today is one
          of its proponents (proponente = 1); main author = ordemAssinatura 1 (RICD art. 102), the others are co-authors.
  Senado: legis.senado.leg.br/dadosabertos/processo?codigoParlamentarAutor=<code>, the whole record of each senator in
          office; main author = the senator is the first name in "autoria".
Bills: PL, PLP, PEC, PDL, plus the codes used before the 2019 unification (Câmara PDC; Senado PLS and PDS).
Outcome: pipelines/politicians/bill_outcomes.py, the same rules as the "Influência" counts (D62). A Câmara bill whose
file has no situation is "status_not_published", never "in_progress".
Raw files go to data/federal/raw-pay/bills/ (gitignored, the names legislative_activity.py reads with --raw); years before
2019 are deleted once read.
Output: data/federal/bills-2026-summary.json (counts per person) and docs/superpowers/previews/assets/tres-poderes-bills/
<house>-<id>.js, one file per person, loaded when the sheet opens.
Check: for each house, the distinct (person, bill) authorships in the source files equal the bills written to the lists.
The same run also checks a control copy with one bill dropped, which must fail (a re-run would re-download 30 years).
Nothing is written when the check fails or the control passes.

Usage: uv run python -B docs/superpowers/tools/build-tres-poderes-bills.py
"""
import collections, csv, json, os, re, subprocess, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "pipelines" / "politicians"))
from bill_outcomes import camara_outcome, senado_outcome  # noqa: E402

RAW = ROOT / "data" / "federal" / "raw-pay" / "bills"
OUT = ROOT / "data" / "federal" / "bills-2026-summary.json"
SHARDS = ROOT / "docs" / "superpowers" / "previews" / "assets" / "tres-poderes-bills"
YEARS = range(1987, 2027)
KEEP_FROM = 2019
CAMARA_BILLS = {"PL", "PLP", "PEC", "PDL", "PDC"}
SENADO_BILLS = {"PL", "PLP", "PEC", "PDL", "PLS", "PDS"}
csv.field_size_limit(10 ** 9)


def get(url, path, accept=None):
    if path.exists() and path.stat().st_size > 0:
        return
    cmd = ["curl", "-sS", "-L", "--compressed", "-m", "900", "-A", "Mozilla/5.0", "-o", str(path), url]
    if accept:
        cmd[1:1] = ["-H", f"Accept: {accept}"]
    subprocess.run(cmd, check=True)


people = [p for p in json.loads((ROOT / "data" / "federal" / "officeholders-2026.json").read_text())["people"] if p["house"] in ("camara", "senado")]
deputies = {p["id"].split(":")[1] for p in people if p["house"] == "camara"}
lists = collections.defaultdict(list)
expected = collections.Counter()
RAW.mkdir(parents=True, exist_ok=True)

# ---------- Câmara
seen = set()
for y in YEARS:
    pf, af = RAW / f"p{y}.csv", RAW / f"a{y}.csv"
    get(f"https://dadosabertos.camara.leg.br/arquivos/proposicoesAutores/csv/proposicoesAutores-{y}.csv", af)
    roles = collections.defaultdict(dict)  # bill id -> {deputy id: "m" | "c"}
    with af.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["proponente"] == "1" and r["idDeputadoAutor"] in deputies:
                d = roles[r["idProposicao"]]
                d[r["idDeputadoAutor"]] = "m" if r["ordemAssinatura"] == "1" or d.get(r["idDeputadoAutor"]) == "m" else "c"
    if roles:
        get(f"https://dadosabertos.camara.leg.br/arquivos/proposicoes/csv/proposicoes-{y}.csv", pf)
        with pf.open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f, delimiter=";"):
                if r["id"] not in roles or r["siglaTipo"] not in CAMARA_BILLS:
                    continue
                sit, desp = r["ultimoStatus_descricaoSituacao"] or "", r["ultimoStatus_despacho"] or ""
                bill = {"t": r["siglaTipo"], "n": r["numero"], "y": r["ano"], "e": (r["ementa"] or "").strip(), "d": r["dataApresentacao"][:10],
                        "o": camara_outcome(sit, desp) if sit else "status_not_published", "s": sit, "tr": r["ultimoStatus_descricaoTramitacao"] or "",
                        "u": (r["ultimoStatus_dataHora"] or "")[:10], "ds": desp[:400], "id": r["id"], "law": sit == "Transformado em Norma Jurídica"}
                for dep, role in roles[r["id"]].items():
                    if (dep, r["id"]) in seen:
                        continue
                    seen.add((dep, r["id"]))
                    expected["camara"] += 1
                    lists[f"camara:{dep}"].append(dict(bill, r=role))
    if y < KEEP_FROM:
        for p in (pf, af):
            p.unlink(missing_ok=True)
    print("camara", y, "bills so far", expected["camara"], flush=True)

# ---------- Senado
plain = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower())
sen = json.loads((ROOT / "data" / "federal" / "raw-pay" / "senators-in-office.json").read_text())["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]
(RAW / "sen").mkdir(exist_ok=True)
for s in sen:
    i = s["IdentificacaoParlamentar"]; code = i["CodigoParlamentar"]
    f = RAW / "sen" / f"{code}.json"
    get(f"https://legis.senado.leg.br/dadosabertos/processo?codigoParlamentarAutor={code}", f, "application/json")
    names = {plain(i["NomeParlamentar"]), plain(i.get("NomeCompletoParlamentar"))}
    done = set()
    for x in json.loads(f.read_text()):
        ident = (x.get("identificacao") or "").strip()
        t = ident.split(" ")[0]
        if t not in SENADO_BILLS or x.get("codigoMateria") in done:
            continue
        done.add(x.get("codigoMateria"))
        first = plain(re.sub(r"^Senador[a]?\s+", "", (x.get("autoria") or "").split(",")[0].split("(")[0]).strip())
        num = re.match(r"\S+\s+(\d+)/(\d{4})", ident)
        sit = x.get("situacaoAtual") or ""
        expected["senado"] += 1
        lists[f"senado:{code}"].append({"t": t, "n": num.group(1) if num else "", "y": num.group(2) if num else "", "e": (x.get("ementa") or "").strip(),
            "d": (x.get("dataApresentacao") or "")[:10], "o": senado_outcome(x), "s": sit, "u": (x.get("dataSituacaoAtual") or "")[:10],
            "norma": x.get("normaGerada") or "", "id": x.get("codigoMateria"), "law": bool(x.get("normaGerada")) or "NORMA JUR" in sit.upper(),
            "r": "m" if any(n and (first.startswith(n) or n.startswith(first)) for n in names) else "c"})
    print("senado", i["NomeParlamentar"], len(lists[f"senado:{code}"]), flush=True)

written = lambda ls: collections.Counter({h: sum(len(v) for k, v in ls.items() if k.startswith(h + ":")) for h in ("camara", "senado")})
counted = written(lists)
control = {k: list(v) for k, v in lists.items()}
control[next(k for k in control if control[k])].pop()
check = {"camara_authorships": expected["camara"], "camara_written": counted["camara"], "senado_authorships": expected["senado"],
         "senado_written": counted["senado"], "passed": expected == counted, "control_with_one_bill_dropped_fails": written(control) != expected}
print(json.dumps(check))
if not (check["passed"] and check["control_with_one_bill_dropped_fails"]):
    raise SystemExit("CHECK FAILED")

SHARDS.mkdir(parents=True, exist_ok=True)
summary = {}
for p in people:
    bills = sorted(lists.get(p["id"], []), key=lambda b: (b["d"], b["t"], b["n"]), reverse=True)
    c = {"main": collections.Counter(b["o"] for b in bills if b["r"] == "m"), "co": collections.Counter(b["o"] for b in bills if b["r"] == "c")}
    summary[p["id"]] = {"main": dict(c["main"]), "co": dict(c["co"]), "laws_main": sum(1 for b in bills if b["r"] == "m" and b["law"]),
                        "laws_co": sum(1 for b in bills if b["r"] == "c" and b["law"]), "first_year": min((b["d"][:4] for b in bills if b["d"]), default=None)}
    (SHARDS / f"{p['id'].replace(':', '-')}.js").write_text(
        "window.TP3B = window.TP3B || {};\nwindow.TP3B[" + json.dumps(p["id"]) + "] = " + json.dumps(bills, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
OUT.write_text(json.dumps({"built_on": "2026-10-21", "years": [YEARS.start, YEARS.stop - 1], "check": check, "people": summary}, ensure_ascii=False, indent=1), encoding="utf-8")
print("written", len(summary), "people;", sum(len(v) for v in lists.values()), "authorships")
