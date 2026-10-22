"""Gera data/politicians/governors.json: governadores e vice-governadores das 27 UFs, 2019-01-01 ate hoje.

Entradas:
- cadastro de candidaturas do TSE (2018 e 2022): eleitos, nome completo e partido na eleicao;
- governors_curated/<UF>.json: mandatos conferidos a mao, com as substituicoes (renuncias, afastamentos,
  interinos, eleicoes indiretas, cassacoes) e a fonte de cada uma;
- Wikidata e Wikimedia Commons: foto, autor e licenca (commons_photos.py).
Para uma UF sem arquivo curado, saem so os eleitos do TSE, marcados como nao verificados.
Rodar: POLITICIANS_WORK=/tmp/politicians-work python3 build_governors.py
"""
import json
import pathlib
import re
import unicodedata

import commons_photos
import tse_common
from tse_common import br_date

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parents[1] / "data" / "politicians" / "governors.json"
CURATED = HERE / "governors_curated"
UFS = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()
TSE = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{y}.zip"
CF = "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"
CARGO = {"governador": "GOVERNADOR", "vice-governador": "VICE-GOVERNADOR"}


def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").upper()).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z ]", " ", s).split()


def slug(s):
    return "-".join(norm(s)).lower()


def same_person(a, b):
    """Nome de uso contra nome do TSE: todas as palavras do nome curto aparecem no outro."""
    na, nb = set(norm(a)), set(norm(b))
    na -= {"DE", "DA", "DO", "DOS", "DAS", "E", "JR", "JUNIOR", "FILHO"}
    return bool(na) and len(na & nb) >= max(1, len(na) - 1)


def tse_elected():
    out = {}
    for y in (2018, 2022):
        for r in tse_common.iter_rows(y, cargos=set(CARGO.values())):
            out.setdefault((r["SG_UF"], y, r["DS_CARGO"]), r)
    return out


def tse_index():
    """Todas as candidaturas de 2018 e 2022 (eleitas ou nao), por nome completo e por nome de urna na UF."""
    by_full, by_urna = {}, {}
    for y in (2018, 2022):
        for r in tse_common.iter_rows(y, elected_only=False):
            obs = {"party": r["SG_PARTIDO"], "observed_on": br_date(r["DT_ELEICAO"]), "basis": f"registro de candidatura no TSE ({r['DS_CARGO'].lower()}, {r['SG_UF']}, eleição de {y})", "source": TSE.format(y=y)}
            by_full.setdefault(" ".join(norm(r["NM_CANDIDATO"])), {})[(y, r["DS_CARGO"])] = (obs, r["NM_CANDIDATO"])
            by_urna.setdefault((r["SG_UF"], " ".join(norm(r["NM_URNA_CANDIDATO"]))), {})[(y, r["DS_CARGO"])] = (obs, r["NM_CANDIDATO"])
    return by_full, by_urna


SPARQL = """SELECT DISTINCT ?person WHERE {
  ?state wdt:P31 wd:Q485258 . ?pos wdt:P1001 ?state . ?pos rdfs:label ?pl .
  FILTER(LANG(?pl)="pt" && REGEX(?pl, "^(vice-)?governador", "i"))
  ?person p:P39 ?st . ?st ps:P39 ?pos . OPTIONAL { ?st pq:P582 ?end }
  FILTER(!BOUND(?end) || ?end >= "2019-01-01"^^xsd:dateTime) }"""


def governor_qids():
    """Pessoas que o Wikidata registra como governador ou vice de uma UF com mandato em 2019 ou depois."""
    import urllib.parse
    d = commons_photos._get("https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": SPARQL, "format": "json"}))
    return {b["person"]["value"].rsplit("/", 1)[1] for b in d["results"]["bindings"]}


def default_terms(uf, el):
    terms = []
    for y, start, end in ((2018, "2019-01-01", "2023-01-01"), (2022, "2023-01-01", None)):
        for role, cargo in CARGO.items():
            r = el[(uf, y, cargo)]
            terms.append({"role": role, "name": r["NM_URNA_CANDIDATO"].title(), "full_name": r["NM_CANDIDATO"], "kind": "eleito",
                          "start": start, "end": end, "start_reason": f"posse após a eleição de {y}", "end_reason": "fim do mandato" if end else None,
                          "party_at_start": r["SG_PARTIDO"], "party_changes": [],
                          "sources": [{"fact": "eleição e partido na eleição", "url": TSE.format(y=y), "type": "oficial"}, {"fact": "datas do mandato (CF, art. 28)", "url": CF, "type": "oficial"}],
                          "verified": False, "note": "Substituições não pesquisadas para esta UF: só os eleitos do TSE com as datas constitucionais do mandato."})
    return terms


def build():
    el = tse_elected()
    by_full, by_urna = tse_index()
    by_uf, people, problems = {}, {}, []
    for uf in UFS:
        path = CURATED / f"{uf}.json"
        cur = json.loads(path.read_text()) if path.exists() else None
        terms = cur["terms"] if cur else default_terms(uf, el)
        # confere os eleitos contra o TSE e completa nome completo e partido
        for t in terms:
            if t["kind"] != "eleito":
                continue
            y = 2018 if t["start"] < "2023-01-01" else 2022
            r = el.get((uf, y, CARGO[t["role"]]))
            if not r or not same_person(t["name"], r["NM_CANDIDATO"] + " " + r["NM_URNA_CANDIDATO"]):
                problems.append(f"{uf} {t['role']} {y}: '{t['name']}' não bate com o TSE ({r and r['NM_CANDIDATO']})")
                continue
            t["full_name"] = t.get("full_name") or r["NM_CANDIDATO"]
            if t.get("party_at_start") and t["party_at_start"] != r["SG_PARTIDO"]:
                problems.append(f"{uf} {t['name']}: partido curado {t['party_at_start']} != TSE {r['SG_PARTIDO']}")
            t["party_at_start"] = r["SG_PARTIDO"]
        for y in (2018, 2022):
            for role, cargo in CARGO.items():
                r = el[(uf, y, cargo)]
                if not any(t["kind"] == "eleito" and t["role"] == role and (t["start"] < "2023-01-01") == (y == 2018) for t in terms):
                    problems.append(f"{uf} {role} {y}: eleito do TSE ({r['NM_CANDIDATO']}) ausente dos mandatos")
        # nome curto sem nome completo (vice que assumiu, interino): herda o nome completo do mesmo eleito na UF
        for t in terms:
            if t.get("name") and not t.get("full_name"):
                for e in terms:
                    if e["kind"] == "eleito" and e.get("full_name") and same_person(t["name"], e["name"] + " " + e["full_name"]):
                        t["full_name"] = e["full_name"]
                        break
        # pessoas: id, nome completo, partido observado no TSE, foto
        for t in terms:
            if not t.get("name"):
                t["person_id"] = None
                continue
            pid = slug(t.get("full_name") or t["name"]) + "-" + uf.lower()
            t["person_id"] = pid
            if pid in people:
                continue
            hits = {}
            if t.get("full_name"):
                hits = by_full.get(" ".join(norm(t["full_name"])), {})
            if not hits:
                hits = by_urna.get((uf, " ".join(norm(t["name"]))), {})
            full = t.get("full_name") or (next(iter(hits.values()))[1] if hits else None)
            obs = [o for (_, (o, _n)) in sorted(hits.items(), key=lambda kv: kv[1][0]["observed_on"] or "")]
            people[pid] = {"name": t["name"], "full_name": full, "uf": uf, "party_observations": obs,
                           "party_observations_note": "Partido em cada registro de candidatura no TSE (2018 e 2022), datado pela eleição; mudanças entre registros só aparecem nos mandatos quando há fonte datada."}
        for t in terms:
            for k in ("party_at_start", "party_changes", "interruptions", "note"):
                t.setdefault(k, [] if k in ("party_changes", "interruptions") else None)
        by_uf[uf] = {"curated": bool(cur), "terms": terms, "gaps": (cur or {}).get("gaps", []) or ([] if cur else ["Substituições não pesquisadas: só os eleitos do TSE."])}
    res = commons_photos.photos_batch(sorted({p["name"] for p in people.values()}))
    gov_qids = governor_qids()
    for pid, p in people.items():
        ph, why = res[p["name"]]
        if ph and ph["wikidata"] not in gov_qids and not re.search(r"governador|governadora", ph["match_note"], re.I):
            ph, why = None, f"verbete encontrado ({ph['wikipedia_page']}) não confirmado como governador ou vice no Wikidata nem na descrição; foto omitida para não arriscar homônimo"
        p["photo"] = ph
        if not ph:
            p["photo_null_reason"] = why
    n_terms = sum(len(v["terms"]) for v in by_uf.values())
    data = {
        "dataset": "governors",
        "collected_on": "2026-10-01",
        "period": {"start": "2019-01-01", "end": "2026-10-01"},
        "scope_note": ("Governadores e vice-governadores das 27 UFs que exerceram o cargo entre 2019-01-01 e 2026-10-01. "
                       "start é o dia em que a pessoa assumiu; end é o dia em que deixou o cargo (em geral o mesmo dia em que o sucessor assume); null quando segue no cargo. "
                       "Entram as mudanças de quem exerce o cargo: renúncias (inclusive as de abril de 2022 e de março e abril de 2026), afastamentos judiciais e por impeachment com o interino, "
                       "eleições indiretas, cassações e a saída do vice; o titular afastado mantém o mandato e o afastamento aparece em interruptions. "
                       "Não entram as substituições curtas por viagem ou licença. Os períodos de vice-governador vago aparecem com kind 'vago'. "
                       "verified = true quando a data foi conferida no texto de uma fonte oficial; false quando a fonte não pôde ser lida ou só a imprensa confirma (ver note). "
                       "Nada sobre candidaturas ou resultados das eleições de 2026."),
        "sources": [
            {"name": "TSE, candidaturas 2018 e 2022 (consulta_cand)", "url": "https://dadosabertos.tse.jus.br/dataset/candidatos-2022"},
            {"name": "Assembleias legislativas, governos estaduais, tribunais: ver cada mandato", "url": None},
            {"name": "Constituição Federal (art. 28: posse em 1º de janeiro)", "url": CF},
            {"name": "Wikimedia Commons e Wikidata (fotos)", "url": "https://commons.wikimedia.org/"},
        ],
        "photo_policy": "URL remota do Wikimedia Commons; licença, autor e página do arquivo como o Commons registra; null com motivo quando não há.",
        "build_script": "pipelines/politicians/build_governors.py",
        "counts": {"ufs": len(by_uf), "ufs_curated": sum(v["curated"] for v in by_uf.values()), "terms": n_terms,
                   "terms_verified": sum(t["verified"] for v in by_uf.values() for t in v["terms"]),
                   "people": len(people), "people_with_photo": sum(1 for p in people.values() if p["photo"])},
        "checks": {"tse_cross_check_problems": problems},
        "by_uf": by_uf,
        "people": people,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print("ok", OUT, data["counts"])
    for p in problems:
        print("  problema:", p)


if __name__ == "__main__":
    build()
