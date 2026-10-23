"""Writes one JSON file per entity (phase B0, D151): the country, the 27 states, the municipalities of SC and RS, the
federal deputies and senators, and the cases, from the published data in data/. English keys; every series carries its
source (agency, dataset, official link, collection date, the source's own note). Each entity is validated against its
schema in schemas/ before anything is written; if one fails, nothing is written and the exit code is 1.

The files are generated at build time and never committed (D151, answer 3): the default output folder,
site/src/generated/entities/, is ignored by git.

Run: uv run python pipelines/export/build_entities.py [OUT_DIR]
"""
import json
import shutil
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data"
SCHEMAS = REPO / "schemas"
DEFAULT_OUT = REPO / "site" / "src" / "generated" / "entities"


def load(rel):
    return json.loads((DATA / rel).read_text(encoding="utf-8"))


def _registry():
    resources = []
    for p in sorted(SCHEMAS.glob("*.schema.json")):
        schema = json.loads(p.read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


REGISTRY = _registry()
VALIDATORS = {}


def validate(entity):
    """The schema errors of one entity, as readable strings (empty when it is valid)."""
    kind = entity.get("type")
    if kind not in VALIDATORS:
        p = SCHEMAS / f"{kind}.schema.json"
        if not p.exists():
            return [f"no schema for type {kind!r}"]
        VALIDATORS[kind] = Draft202012Validator(json.loads(p.read_text(encoding="utf-8")), registry=REGISTRY)
    return [f"{entity.get('id')}: {'/'.join(map(str, e.absolute_path))}: {e.message}" for e in VALIDATORS[kind].iter_errors(entity)]


def _source_for(sources, field):
    hit = [s for s in sources if s["field"] == field]
    if not (len(hit) == 1):
        raise SystemExit(f"source of {field}: {len(hit)} found")
    return hit[0]


def entities():
    monthly = load("series/federal-by-uf-monthly.json")
    pop = load("series/population.json")
    months = monthly["months"]
    m_src = monthly["sources"]
    when = monthly["collected_at"]

    def src(field, agency, dataset):
        s = _source_for(m_src, field)
        return {"agency": agency, "dataset": dataset, "url": s["url"], "collected_at": when, "note": s.get("note", "")}

    def series(values, source):
        if not (len(values) == len(months)):
            raise SystemExit((source["dataset"], len(values)))
        return {"unit": "BRL", "months": months, "values": values, "source": source}

    pop_src = {"agency": "IBGE", "dataset": "Estimativas da População e Censo 2022",
               "url": _source_for(pop["sources"], "population (estimativas)")["url"], "collected_at": pop["collected_at"],
               "note": "2019 a 2021 e 2024 a 2026: estimativas; 2022: Censo; 2023: sem estimativa publicada (null)."}
    years = [int(y) for y in pop["years"]]

    def population(by_year):
        return {"unit": "people", "years": years, "values": [by_year[str(y)] for y in years], "source": pop_src}

    sources = {
        "federal_revenue": src("uf.*.federal_revenue", "Receita Federal", "Arrecadação por Estado"),
        "transfers": src("uf.*.transfers", "CGU, Portal da Transparência", "Transferências"),
        "bolsa_familia": src("uf.*.bolsa_familia", "MDS", "Matriz de Informação Social (Bolsa Família)"),
        "bpc": src("uf.*.bpc", "MDS", "Matriz de Informação Social (BPC)"),
        "inss": src("uf.*.inss", "Previdência Social", "Boletim Estatístico da Previdência Social (BEPS)"),
    }
    yield {"type": "country", "id": "BR", "name": "Brasil", "series": {"federal_revenue": series(
        monthly["national"]["federal_revenue_total_receita"],
        src("national.federal_revenue_total_receita (2019 a 2025)", "Receita Federal", "Arrecadação das Receitas Federais, Total Geral"))}}
    for uf in sorted(monthly["uf"]):
        s, p = monthly["uf"][uf], pop["uf"][uf]
        yield {"type": "state", "id": uf, "name": p["name"], "ibge_code": p["ibge_code"], "population": population(p["population"]),
               "series": {"federal_revenue": series(s["federal_revenue"]["total"], sources["federal_revenue"]),
                          "transfers": series(s["transfers"]["total"], sources["transfers"]),
                          "bolsa_familia": series(s["bolsa_familia"], sources["bolsa_familia"]),
                          "bpc": series(s["bpc"], sources["bpc"]), "inss": series(s["inss"], sources["inss"])}}
    for uf in ("SC", "RS"):
        for code, m in sorted(pop[f"{uf.lower()}_municipalities"].items()):
            yield {"type": "municipality", "id": code, "name": m["name"], "uf": uf, "population": population(m["population"])}
    for rel, house, start, end in (("politicians/federal-deputies.json", "camara", "legislature_start", "legislature_end"),
                                   ("politicians/senators.json", "senado", "mandate_start", "mandate_end")):
        for people in load(rel)["by_uf"].values():
            for x in people:
                yield {"type": "person", "id": x["id"], "name": x["name"], "full_name": x["full_name"],
                       "terms": [{"house": house, "role": x["role"], "uf": t["uf"], "start": t[start], "end": t[end],
                                  "kind": t["kind"], "source": t["source"]} for t in x["terms"]]}
    for p in sorted((DATA / "cases").glob("*.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        yield {"type": "case", "id": c["case_id"], "title": c["title"], "collected_at": c["collected_on"]}


def path_of(out, e):
    return out / e["type"] / (e["id"].replace(":", "-") + ".json")


def build(out=DEFAULT_OUT):
    """Validates every entity, then writes them all; returns how many were written."""
    out = Path(out)
    all_entities = list(entities())
    problems = [p for e in all_entities for p in validate(e)]
    if problems:
        raise SystemExit("schema errors, nothing written:\n" + "\n".join(problems[:20]))
    seen = set()
    for e in all_entities:
        key = (e["type"], e["id"])
        if not (key not in seen):
            raise SystemExit(f"duplicate entity {key}")
        seen.add(key)
    if out.exists():
        shutil.rmtree(out)
    for e in all_entities:
        p = path_of(out, e)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(e, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(all_entities)


if __name__ == "__main__":
    n = build(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT)
    print(f"{n} entity files written")
