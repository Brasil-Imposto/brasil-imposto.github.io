"""Builds the compact `politicians_view` the previews read (assets/politicians.js) from data/politicians/*.json.

person = {name, role, start, end, parties: [{party, from}], photo: {url, credit, link} | None, links: [{label, url}]}
Every source file keeps its own detail; this view keeps only what the screen shows.
"""
import json
from pathlib import Path


def _photo(p):
    if not p or not p.get("url"):
        return None
    credit = ", ".join(x for x in (p.get("author"), p.get("license")) if x)
    return {"url": p["url"], "credit": credit, "link": p.get("file_page") or p.get("terms_source") or p.get("source") or p["url"]}


def _collected(entry):
    """A photo collected by pipelines/politicians/collect_photos.py (D61): a local file under previews/assets/photos."""
    if not entry or not (entry.get("file") or entry.get("url")):
        return None
    url = entry["file"].replace("docs/superpowers/previews/", "") if entry.get("file") else entry["url"]
    credit = "Tribunal Superior Eleitoral (CC BY)" if "tse" in (entry.get("source") or "") else ", ".join(x for x in (entry.get("author"), entry.get("license_or_terms")) if x)
    return {"url": url, "credit": credit, "link": entry.get("page") or entry.get("source") or url}


OUTCOME_GROUP = {"approved": "approved", "approved_with_another_bill": "approved", "rejected": "rejected", "vetoed": "rejected"}


def _activity(entry):
    """Bills authored since 2019-02-01 (D62): totals by outcome group, main author and co-author kept apart."""
    if not entry:
        return None
    out = {}
    for role in ("main_author", "co_author"):
        tot = {"total": 0, "approved": 0, "rejected": 0, "other": 0}
        for counts in entry.get(role, {}).values():
            for k, v in counts.items():
                tot["total"] += v
                tot[OUTCOME_GROUP.get(k, "other")] += v
        out[role] = tot
    return out


def _parties(history, fallback=None, fallback_from=None):
    dated = [{"party": h.get("party") or h.get("label") or "sem partido", "from": h.get("start") or "0000-00-00"} for h in history or []]
    if dated and not all(d["from"] == "0000-00-00" for d in dated[1:]):
        return dated
    if fallback:
        return [{"party": fallback, "from": fallback_from or "0000-00-00"}]
    return dated[:1]


def _end(d):
    """Exclusive end dates (a mandate 'ends' on the day the next one starts) are kept as given."""
    return d


def build(pol_dir: Path):
    view = {"note": "Cargos, datas e partidos de fontes oficiais (TSE, Planalto, Senado, Câmara, assembleias). Fotos com autor e licença no link de cada foto.",
            "union": {}, "uf": {}, "mayors": {}}
    load = lambda n: json.loads((pol_dir / f"{n}.json").read_text(encoding="utf-8")) if (pol_dir / f"{n}.json").exists() else None
    photos = (load("photos") or {}).get("people", {})
    activity = load("legislative-activity") or {}
    acts = activity.get("people", {})
    view["activity_note"] = ("Projetos de lei (PL, PLP, PEC, PDL) apresentados desde 01/02/2019, pela última situação oficial na Câmara e no Senado. "
                             "Aprovados: viraram lei ou foram aprovados na Casa (inclui os aprovados junto com outro projeto). Rejeitados: rejeitados ou vetados. "
                             "Os demais estão em tramitação, foram arquivados, retirados ou prejudicados.") if acts else None
    view["president_mps"] = activity.get("president_mps")

    u = load("union")
    if u:
        key = {"Presidente da República": "president", "Vice-Presidente da República": "vice"}
        for o in u["offices"]:
            k = key.get(o["office"], "economy" if o["office"].startswith("Ministro") else None)
            if not k:
                continue
            p = u["people"][o["person_id"]]
            links = [{"label": s.get("fact", "fonte")[:28], "url": s["url"]} for s in o.get("sources", [])[:2] if s.get("url", "").startswith("http")]
            view["union"].setdefault(k, []).append({
                "name": p["name"], "role": o["office"], "start": o["start"], "end": _end(o["end"]),
                "parties": _parties(p.get("party_history"), o.get("party_at_start"), o["start"]),
                "photo": _photo(p.get("photo")) or _collected(photos.get(o["person_id"])), "links": links})

    def exercise_people(rows, role):
        out = []
        for p in rows:
            parties = [{"party": h["party"], "from": h.get("start") or "0000-00-00"} for h in p.get("party_history", [])]
            for t in p.get("terms", []):
                for e in t.get("exercise", []):
                    out.append({"name": p["name"], "role": role, "start": e["start"], "end": e.get("end"), "parties": parties,
                                "photo": _photo(p.get("photo")) or _collected(photos.get(p["id"])), "activity": _activity(acts.get(p["id"])),
                                "links": [{"label": "Fonte oficial", "url": t["source"]}] if t.get("source") else []})
        return out

    s = load("senators")
    if s:
        for uf, rows in s["by_uf"].items():
            view["uf"].setdefault(uf, {})["senators"] = exercise_people(rows, "Senador")
    f = load("federal-deputies")
    if f:
        for uf, rows in f["by_uf"].items():
            view["uf"].setdefault(uf, {})["federal_deputies"] = exercise_people(rows, "Deputado federal")
    d = load("state-deputies")
    if d:
        for uf, years in d["by_uf"].items():
            view["uf"].setdefault(uf, {})["state_deputies"] = {
                y: [{"name": x["name"].title(), "role": x["role"].capitalize(), "start": None, "end": None,
                     "parties": [{"party": x["party"], "from": "0000-00-00"}], "photo": _collected(photos.get(x["id"])), "links": []} for x in rows]
                for y, rows in years.items()}
    g = load("governors")
    if g:
        people = g.get("people", {})
        for uf, block in g["by_uf"].items():
            view["uf"].setdefault(uf, {})["governors_curated"] = bool(block.get("curated"))
            for x in block["terms"]:
                k = "vice" if x["role"].startswith("vice") else "governor"
                parties = [{"party": x.get("party_at_start") or "sem partido", "from": x["start"]}]
                parties += [{"party": c["party"], "from": (c["date"] + "-01")[:10] if len(c["date"]) == 7 else c["date"]} for c in x.get("party_changes", [])]
                role = {"governor": "Governador", "vice_governor": "Vice-governador"}[x["role"]] + (" interino" if x.get("kind") == "acting" else "")
                person = people.get(x.get("person_id"), {})
                view["uf"].setdefault(uf, {}).setdefault(k, []).append({
                    "name": x["name"], "role": role, "start": x["start"], "end": x.get("end"), "parties": [] if x.get("kind") == "vacant" else parties,
                    "vacant": x.get("kind") == "vacant", "reason": x.get("start_reason") if x.get("kind") == "vacant" else None,
                    "photo": _photo(person.get("photo")) or _collected(photos.get(x.get("person_id"))), "verified": bool(x.get("verified")),
                    "links": [{"label": s.get("fact", "fonte")[:28], "url": s["url"]} for s in x.get("sources", [])[-2:] if s.get("url")]})
    # Elected mayors of every state with a municipal map (SC, RS), keyed by IBGE code (unique across states).
    # D81: a by-election winner starts on the by-election date (the TSE file has no swearing-in date) and the regular
    # winner of the same cycle ends on it; a cycle with nobody elected gets a note for the gap, in the TSE record's terms.
    br = lambda d: f"{d[8:10]}/{d[5:7]}/{d[:4]}"
    for m in filter(None, (load(f"{u}-mayors") for u in ("sc", "rs"))):
        for mu in m["municipalities"]:
            lst, notes = [], []
            els = sorted(mu["elections"], key=lambda e: e["election_date"])
            for e in els:
                x = e.get("mayor")
                if not x:
                    continue
                md = x.get("mandate") or {}
                by = e["type"] != "ordinaria"
                role = "Prefeito" if x.get("role", "").upper().startswith("PREFEITO") else x.get("role", "Prefeito").capitalize()
                lst.append({"name": x["name"].title(), "role": f"{role}, eleição suplementar de {br(e['election_date'])}" if by else role,
                            "start": e["election_date"] if by else md.get("start"), "end": md.get("end"), "cycle": e["year"], "by_election": by,
                            "parties": [{"party": x["party"], "from": "0000-00-00"}], "photo": _collected(photos.get(x.get("id"))),
                            "links": [{"label": "TSE", "url": x["source"]}] if x.get("source") else []})
            for y in sorted({e["year"] for e in els}):
                sup = [e for e in els if e["year"] == y and e["type"] != "ordinaria"]
                held = [e for e in sup if e.get("mayor")]
                for p in lst:  # the regular winner leaves when a by-election of the same cycle elects someone
                    if p["cycle"] == y and not p["by_election"] and held:
                        p["end"] = min(p["end"] or "9999", held[0]["election_date"])
                if held:
                    notes.append({"from": held[0]["election_date"], "to": f"{y + 4}-12-31",
                                  "text": f"Houve eleição suplementar em {br(held[0]['election_date'])}. As datas vêm das eleições: o TSE não traz a data da posse nem quem exerceu o cargo entre a saída do eleito anterior e a posse do novo."})
                ordinary = next((e for e in els if e["year"] == y and e["type"] == "ordinaria"), None)
                if ordinary and not ordinary.get("mayor"):
                    nxt = next((e for e in sup if e.get("mayor")), None) or (sup[0] if sup else None)
                    when = (f"a eleição suplementar foi em {br(nxt['election_date'])}" if nxt and nxt.get("mayor")
                            else f"a eleição suplementar está marcada para {br(nxt['election_date'])}" if nxt else "não há eleição suplementar registrada")
                    notes.append({"from": f"{y + 1}-01-01", "to": nxt["election_date"] if nxt and nxt.get("mayor") else f"{y + 4}-12-31",
                                  "text": f"O TSE não registra prefeito eleito na eleição de {y}; {when}. Este site não tem quem exerceu o cargo nesse intervalo."})
            for p in lst:
                del p["cycle"], p["by_election"]
            view["mayors"][mu["ibge_code"]] = lst
            if notes:
                view.setdefault("mayor_notes", {})[mu["ibge_code"]] = notes
    # Reference for the bar length: the 95th percentile of bills as main author among all federal legislators, so one
    # outlier does not flatten every other bar.
    totals = sorted(a["main_author"]["total"] for a in (_activity(x) for x in acts.values()) if a)
    view["activity_ref"] = totals[int(len(totals) * 0.95)] if totals else None
    return view
