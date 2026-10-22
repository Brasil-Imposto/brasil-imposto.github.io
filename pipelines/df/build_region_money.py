"""Money by Regional Administration (RA) of the Federal District, from the GDF transparency portal.

Sources (all official, Portal da Transparencia do DF, SEEC/CGDF, data from SIGGo):
  /api/despesa/detalhamento?anoExercicio=Y            spending by managing unit (UG): initial, authorized, committed, liquidated
  /api/despesa/detalhamento/Y/<UG>                     same, by budget subtitle (the subtitle text carries the location)
  /api/v2/despesas-ras?exercicio=Y                     the portal's own "Despesas Regionais" panel: paid per Administracao Regional
  /api/servidor?nomeFuncao=ADMINISTRADOR REGIONAL      payroll register: who holds the post of regional administrator
  /api/dataAtualizacao/detalhamento                    when the portal last refreshed the spending data

Rule for localized spending: a subtitle counts for an RA when its LAST segment (the localizer the GDF writes after the
final hyphen) names exactly one RA; if that segment is DF-wide it is "not by region"; if the last segment names no place,
the whole subtitle text is used; two or more RAs in the text go to "multiple_regions". Spending of each Administracao
Regional's own UG counts for its RA regardless of the text. Values are LIQUIDATED (paid is not published per subtitle).

Check: sum over RAs + not_by_region buckets == portal total (totalizador.valorLiquidado) for every year.
Control (--control or always at the end): the same check on a copy with one row dropped must FAIL.

Usage: python3 pipelines/df/build_region_money.py [--rows-cache DIR]
"""
import json, os, re, shutil, sys, tempfile, time, unicodedata, urllib.parse, urllib.request, uuid
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data", "df", "region-money.json")
REGIONS = os.path.join(ROOT, "data", "df", "regions.json")
API = "https://www.transparencia.df.gov.br/api"
PORTAL = "https://www.transparencia.df.gov.br"
YEARS = list(range(2019, 2027))
CLIENT_ID = str(uuid.uuid4())  # the portal requires an x-client-id header (a random UUID, as its own app sends)


def get(path, tries=4):
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(API + path, headers={"x-client-id": CLIENT_ID, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except Exception as e:  # network hiccups: retry with backoff
            err = e
            time.sleep(3 * (i + 1))
    raise err


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", s.replace("\t", " ")).strip()


# Place names as the GDF writes them in subtitles (accent-free, upper case). Overlaps such as
# SOBRADINHO / SOBRADINHO II are handled with lookaheads; LAGO PARANOA (the lake) is not the RA.
PATTERNS = {
    "RA-I": [r"\bPLANO PILOTO\b", r"\bASA NORTE\b", r"\bASA SUL\b", r"\bSETOR NOROESTE\b"],
    "RA-II": [r"\bGAMA\b"],
    "RA-III": [r"\bTAGUATINGA\b"],
    "RA-IV": [r"\bBRAZLANDIA\b"],
    "RA-V": [r"\bSOBRADINHO(?! ?II\b)(?! ?2\b)"],
    "RA-VI": [r"\bPLANALTINA\b(?! DE GOIAS)(?! ?[-/] ?GO\b)"],
    "RA-VII": [r"(?<!LAGO )\bPARANOA\b"],
    "RA-VIII": [r"\bNUCLEO BANDEIRANTE\b"],
    "RA-IX": [r"\bCEILANDIA\b"],
    "RA-X": [r"\bGUARA\b"],
    "RA-XI": [r"\bCRUZEIRO\b"],
    "RA-XII": [r"\bSAMAMBAIA\b"],
    "RA-XIII": [r"\bSANTA MARIA\b"],
    "RA-XIV": [r"\bSAO SEBASTIAO\b"],
    "RA-XV": [r"\bRECANTO DAS EMAS\b"],
    "RA-XVI": [r"\bLAGO SUL\b"],
    "RA-XVII": [r"\bRIACHO FUNDO(?! ?II\b)(?! ?2\b)"],
    "RA-XVIII": [r"\bLAGO NORTE\b"],
    "RA-XIX": [r"\bCANDANGOLANDIA\b"],
    "RA-XX": [r"\bAGUAS CLARAS\b"],
    "RA-XXI": [r"\bRIACHO FUNDO ?(II|2)\b"],
    "RA-XXII": [r"\bSUDOESTE ?(/|E) ?OCTOGONAL\b", r"\bOCTOGONAL\b", r"\bSETOR SUDOESTE\b"],
    "RA-XXIII": [r"\bVARJAO\b"],
    "RA-XXIV": [r"\bPARK WAY\b"],
    "RA-XXV": [r"\bSCIA\b", r"\bCIDADE ESTRUTURAL\b", r"/ ?ESTRUTURAL\b", r"\bSETOR COMPL(\.|EMENTAR)? (DE )?IND(\.|USTRIA)? E ABAST"],
    "RA-XXVI": [r"\bSOBRADINHO ?(II|2)\b"],
    "RA-XXVII": [r"\bJARDIM BOTANICO\b(?! DE BRASILIA)"],
    "RA-XXVIII": [r"\bITAPOA\b"],
    "RA-XXIX": [r"\bSIA\b", r"(?<!COMPL\. DE )(?<!COMPLEMENTAR DE )\bSETOR DE IND(\.|USTRIA)? E ABAST"],
    "RA-XXX": [r"\bVICENTE PIRES\b"],
    "RA-XXXI": [r"\bFERCAL\b"],
    "RA-XXXII": [r"\bSOL NASCENTE\b", r"\bPOR DO SOL\b"],
    "RA-XXXIII": [r"\bARNIQUEIRAS?\b"],
    "RA-XXXIV": [r"\bARAPOANGA\b"],
    "RA-XXXV": [r"\bAGUA QUENTE\b"],
    "RA-XXXVI": [r"\b26 DE SETEMBRO\b"],
    "RA-XXXVII": [r"\bPONTE ALTA\b"],
}
COMPILED = {ra: [re.compile(p) for p in ps] for ra, ps in PATTERNS.items()}
DF_WIDE = re.compile(r"^(NO |EM TODO O |TODO O )?(DISTRITO FEDERAL|DF)\b")
WORK_WORDS = re.compile(r"CONSTRU|REFORMA|OBRA|AMPLIA|PAVIMENT|URBANIZ|IMPLANT|DRENAG|RECUPERA|REVITALIZ|DUPLICA|TUNEL|VIADUTO|RESTAURA|EDIFICA")


def regions_in(text):
    t = norm(text)
    return sorted({ra for ra, ps in COMPILED.items() if any(p.search(t) for p in ps)})


def localizer(subtitle):
    """Last hyphen-separated segment that is not just a year or punctuation."""
    parts = [p.strip(" .") for p in re.split(r"\s*-+\s*", norm(subtitle))]
    parts = [p for p in parts if p and not re.fullmatch(r"\d{4}|[\W_]+", p)]
    return parts[-1] if parts else ""


def classify(subtitle):
    """Returns (bucket, rule). bucket is an RA code, 'df_wide', 'multiple_regions' or 'not_located'."""
    tail = localizer(subtitle)
    in_tail = regions_in(tail)
    if len(in_tail) == 1:
        return in_tail[0], "localizer"
    if len(in_tail) > 1:
        return "multiple_regions", "localizer"
    if DF_WIDE.match(tail):
        return "df_wide", "localizer"
    in_text = regions_in(subtitle)
    if len(in_text) == 1:
        return in_text[0], "full_text"
    if len(in_text) > 1:
        return "multiple_regions", "full_text"
    return "not_located", "none"


def is_work(project_code, name):
    """Budget 'projeto' (GDF action codes starting with 1, 3, 5 or 7) whose name describes a construction work."""
    return str(project_code or "")[:1] in "1357" and bool(WORK_WORDS.search(norm(name)))


def fetch_year(year, cache):
    """UG list with portal total, then subtitle rows for every UG. Cached as compact JSON (kept only if --rows-cache)."""
    ug_path, rows_path = os.path.join(cache, f"ug_{year}.json"), os.path.join(cache, f"rows_{year}.json")
    if os.path.exists(ug_path) and os.path.exists(rows_path):
        return json.load(open(ug_path)), json.load(open(rows_path))
    ugs, page = [], 0
    while True:
        d = get(f"/despesa/detalhamento?anoExercicio={year}&page={page}")
        ugs += d["content"]
        if d["last"]:
            break
        page += 1
    ug = {"totalizador": d["totalizador"], "ugs": ugs}
    rows = []
    for u in ugs:
        code = u["codigoUnidadeGestora"]
        for r in get(f"/despesa/detalhamento/{year}/{code}"):
            rows.append([code, r.get("codigoPrograma"), r.get("codigoProjeto"), r.get("codigoSubtitulo"), r.get("nomeProjeto"),
                         r.get("nomeSubtitulo"), r["valorLei"], r["valorDespesaAutorizada"], r["valorEmpenhado"], r["valorLiquidado"]])
        time.sleep(0.2)
    json.dump(ug, open(ug_path, "w"), ensure_ascii=False)
    json.dump(rows, open(rows_path, "w"), ensure_ascii=False)
    return ug, rows


def admin_ug_to_ra(ug_names):
    """Map each Administracao Regional UG code to its RA by the UG's own name."""
    out = {}
    for code, name in ug_names.items():
        n = norm(name)
        if not (n.startswith("ADMINISTRACAO REGIONAL") or n.startswith("REGIAO ADMINISTRATIVA")):
            continue
        n = re.sub(r"\s*-\s*RA\s+[IVXL]+$", "", n)
        n = n.replace("SETOR COMPL. IND. E ABAST.", "SETOR COMPL. DE IND. E ABAST.").replace("SETOR IND. E ABASTECIMENTO", "SIA")
        found = regions_in(n)
        assert len(found) == 1, (code, name, found)
        out[code] = found[0]
    return out


def bucket_rows(rows, admin_map):
    """Assign every subtitle row to exactly one bucket. Returns list of (bucket, rule, row)."""
    out = []
    for r in rows:
        bucket, rule = classify(r[5])
        if not bucket.startswith("RA-") and r[0] in admin_map:
            bucket, rule = admin_map[r[0]], "administration_ug"
        out.append((bucket, rule, r))
    return out


def check_year(bucketed, total):
    s = sum(r[9] for _, _, r in bucketed)
    return {"sum_of_buckets": round(s, 2), "portal_total_liquidated": round(total, 2), "ok": abs(s - total) < 0.5}


def updated_on(key):
    try:
        ms = get(f"/dataAtualizacao/{key}")
        return datetime.fromtimestamp(int(ms) / 1000, timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return None


def administrators():
    """Holders of the function ADMINISTRADOR REGIONAL in the latest month of the GDF payroll register."""
    func = urllib.parse.quote("ADMINISTRADOR REGIONAL")
    for year in (2026, 2025):
        for month in range(12, 0, -1):
            path = f"/servidor?page=0&size=200&nomeFuncao={func}&exercicio={year}&mesReferencia={month}"
            d = get(path)
            if d.get("totalElements"):
                return year, month, path, d["content"]
    return None, None, None, []


def r2(x):
    return None if x is None else round(x, 2)


def main():
    keep = "--rows-cache" in sys.argv
    cache = sys.argv[sys.argv.index("--rows-cache") + 1] if keep else tempfile.mkdtemp(prefix="df-region-money-")
    os.makedirs(cache, exist_ok=True)
    try:
        build(cache)
    finally:
        if not keep:
            shutil.rmtree(cache, ignore_errors=True)


def build(cache):
    regions = json.load(open(REGIONS))["regions"]
    out_regions = {ra: {"name": v["name"], "administration_ug": None, "administration_budget": {}, "localized_gdf_spending": {},
                        "localized_of_which_administration": {}, "top_localized_items_2025": [], "administrator": None,
                        "works": [], "published_on": None} for ra, v in regions.items()}
    not_by_region, checks, controls, rules_total = {}, {}, {}, {}
    works = {}
    detail_date = updated_on("detalhamento")
    for year in YEARS:
        ug, rows = fetch_year(year, cache)
        names = {u["codigoUnidadeGestora"]: u["nomeUnidadeGestora"] for u in ug["ugs"]}
        admin_map = admin_ug_to_ra(names)
        paid = {norm(r["nomeRA"]): r for r in get(f"/v2/despesas-ras?exercicio={year}")}
        for u in ug["ugs"]:
            ra = admin_map.get(u["codigoUnidadeGestora"])
            if not ra:
                continue
            p = paid.get(norm(u["nomeUnidadeGestora"]))
            reg = out_regions[ra]
            reg["administration_ug"] = {"code": u["codigoUnidadeGestora"], "name": u["nomeUnidadeGestora"].strip()}
            prev = reg["administration_budget"].get(str(year))
            entry = {"initial": u["valorLei"], "authorized": u["valorDespesaAutorizada"], "committed": u["valorEmpenhado"],
                     "liquidated": u["valorLiquidado"], "paid": p["valorPago"] if p else None}
            if prev:  # two UGs mapped to one RA in the same year: add up
                entry = {k: (None if prev[k] is None or entry[k] is None else prev[k] + entry[k]) for k in entry}
            reg["administration_budget"][str(year)] = {k: r2(v) for k, v in entry.items()}
        bucketed = bucket_rows(rows, admin_map)
        checks[str(year)] = check_year(bucketed, ug["totalizador"]["valorLiquidado"])
        biggest = max(range(len(bucketed)), key=lambda i: bucketed[i][2][9])
        broken = bucketed[:biggest] + bucketed[biggest + 1:]  # control: drop the largest row, the check must fail
        controls[str(year)] = check_year(broken, ug["totalizador"]["valorLiquidado"])["ok"] is False
        sums, admin_sums, nbr, by_rule = {}, {}, {"df_wide": 0.0, "not_located": 0.0, "multiple_regions": 0.0}, {}
        top = {}
        for bucket, rule, r in bucketed:
            by_rule[rule] = by_rule.get(rule, 0.0) + r[9]
            if bucket in nbr:
                nbr[bucket] += r[9]
                continue
            sums[bucket] = sums.get(bucket, 0.0) + r[9]
            if admin_map.get(r[0]) == bucket:
                admin_sums[bucket] = admin_sums.get(bucket, 0.0) + r[9]
            if year == 2025 and r[9] > 0:
                top.setdefault(bucket, []).append({"ug": names[r[0]].strip(), "action": (r[4] or "").strip(),
                                                   "subtitle": re.sub(r"\s+", " ", r[5] or "").strip(), "liquidated": r2(r[9]), "rule": rule})
            if is_work(r[2], f"{r[4]} {r[5]}") and r[9] > 0:
                key = (bucket, r[0], r[2], norm(r[5]))
                w = works.setdefault(key, {"ug": names[r[0]].strip(), "action_code": r[2], "action": (r[4] or "").strip(),
                                           "subtitle": re.sub(r"\s+", " ", r[5] or "").strip(), "liquidated": 0.0, "years": []})
                w["liquidated"] += r[9]
                w["years"].append(year)
        for ra in out_regions:
            out_regions[ra]["localized_gdf_spending"][str(year)] = r2(sums.get(ra, 0.0))
            out_regions[ra]["localized_of_which_administration"][str(year)] = r2(admin_sums.get(ra, 0.0))
            if year == 2025:
                out_regions[ra]["top_localized_items_2025"] = sorted(top.get(ra, []), key=lambda x: -x["liquidated"])[:3]
        not_by_region[str(year)] = {k: r2(v) for k, v in nbr.items()}
        rules_total[str(year)] = {k: r2(v) for k, v in by_rule.items()}
        print(year, checks[str(year)], "control_fails:", controls[str(year)], flush=True)

    for (ra, *_), w in works.items():
        out_regions[ra]["works"].append(w)
    for ra, reg in out_regions.items():
        reg["works"] = sorted(reg["works"], key=lambda w: -w["liquidated"])[:3]
        for w in reg["works"]:
            w["liquidated"] = r2(w["liquidated"])
            w["years"] = sorted(set(w["years"]))
            w["company"] = None  # not published per subtitle; see report
        reg["published_on"] = detail_date

    year, month, path, holders = administrators()
    by_ra = {}
    for h in holders:
        n = norm(h["nomeOrgao"]).replace("ADMINISTRACAO REGIONAL", "").strip()
        found = regions_in(n)
        assert len(found) == 1, (h["nomeOrgao"], found)
        by_ra.setdefault(found[0], []).append(h)
    for ra, reg in out_regions.items():
        hs = by_ra.get(ra, [])
        base = {"name": None, "since": None, "act": None, "url": API + path if path else None, "photo": None,
                "payroll_reference": f"{year}-{month:02d}" if year else None, "payroll_admission_date": None}
        if len(hs) == 1:
            base["name"] = re.sub(r"\s+", " ", hs[0]["nome"]).strip()
            base["payroll_admission_date"] = hs[0]["dataAdmissaoFormatada"]
        elif len(hs) > 1:
            base["payroll_holders"] = [{"name": re.sub(r"\s+", " ", h["nome"]).strip(), "payroll_admission_date": h["dataAdmissaoFormatada"]} for h in hs]
        reg["administrator"] = base

    assert all(c["ok"] for c in checks.values()), checks
    assert all(controls.values()), controls
    result = {
        "collected_on": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "sources": [
            {"name": "Portal da Transparência do DF, Detalhamento da Despesa (por UG e por subtítulo), dados do SIGGo",
             "url": PORTAL + "/#/despesas/detalhamento", "api": API + "/despesa/detalhamento?anoExercicio=YYYY ; " + API + "/despesa/detalhamento/YYYY/<UG>",
             "updated_on": detail_date},
            {"name": "Portal da Transparência do DF, painel Despesas Regionais (valor pago por Administração Regional)",
             "url": PORTAL, "api": API + "/v2/despesas-ras?exercicio=YYYY", "updated_on": updated_on("painel-despesas")},
            {"name": "Portal da Transparência do DF, Servidores (função ADMINISTRADOR REGIONAL)",
             "url": PORTAL + "/#/servidores/orgao", "api": API + (path or ""), "updated_on": updated_on("servidores-por-orgao")},
        ],
        "notes": {
            "values": "R$ nominais. administration_budget: initial = valorLei (LOA), authorized = valorDespesaAutorizada, committed = empenhado, liquidated = liquidado (Detalhamento por UG); paid = valorPago do painel Despesas Regionais (null onde o painel não traz a UG). localized_gdf_spending = liquidado (o pago não é publicado por subtítulo).",
            "rule": "Subtítulo conta para uma RA quando o último trecho (o localizador que o GDF escreve depois do último hífen) cita exatamente uma RA; trecho 'DISTRITO FEDERAL'/'DF' = df_wide; se o último trecho não cita lugar, vale o texto inteiro; duas RAs = multiple_regions. Linhas da própria Administração Regional sem lugar no texto contam para a RA dela.",
            "year_2026": "parcial, até a data de atualização do portal",
            "administrator": "nome da folha de pagamento do GDF (função ADMINISTRADOR REGIONAL, mês de referência indicado); since e act ficam null porque o DODF não abriu; payroll_admission_date é a data de admissão registrada na folha, não o ato de nomeação.",
        },
        "regions": out_regions,
        "not_by_region": not_by_region,
        "classification_by_rule": rules_total,
        "check": {"rule": "soma das RAs + df_wide + not_located + multiple_regions = total liquidado do portal (totalizador)", "years": checks,
                  "control_drop_one_row_fails": controls},
    }
    json.dump(result, open(OUT, "w"), ensure_ascii=False, indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
