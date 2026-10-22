"""Gera data/politicians/state-deputies.json: deputados estaduais (e distritais, no DF) ELEITOS em 2018 e 2022,
por UF, a partir do cadastro de candidaturas do TSE (consulta_cand).

Uso: POLITICIANS_WORK=/caminho/de/trabalho python3 build_state_deputies.py
Só biblioteca padrão do Python 3.
"""
import json
import pathlib
import sys
from collections import Counter, defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from tse_common import ELECTED, TSE_CAND_URL, br_date, iter_rows  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = REPO / "data" / "politicians" / "state-deputies.json"
COLLECTED_ON = "2026-10-01"
YEARS = (2018, 2022)
CARGOS = {"DEPUTADO ESTADUAL", "DEPUTADO DISTRITAL"}
CF_URL = "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"
RECORD_BASIS = "eleito: resultado da eleição no cadastro do TSE, não indica exercício do mandato"

# Tamanho das assembleias, usado só como conferência: art. 27, caput, da CF (o triplo da bancada federal
# até 36; acima disso, mais um por deputado federal além de 12) aplicado às bancadas federais em vigor em
# 2018 e 2022; a Câmara Legislativa do DF segue a mesma regra (art. 32, par. 3).
EXPECTED_SEATS = {
    "SP": 94, "MG": 77, "RJ": 70, "BA": 63, "RS": 55, "PR": 54, "PE": 49, "CE": 46, "MA": 42,
    "GO": 41, "PA": 41, "SC": 40, "PB": 36, "ES": 30, "PI": 30, "AL": 27,
    "AC": 24, "AM": 24, "AP": 24, "DF": 24, "MS": 24, "MT": 24, "RN": 24, "RO": 24, "RR": 24, "SE": 24, "TO": 24,
}


def null_if_tse_blank(v):
    """O TSE usa #NULO / #NULO# / #NE para campo vazio."""
    return None if not v or v.startswith("#") else v


def person(row, year):
    return {
        "id": f"tse:{row['ANO_ELEICAO']}:{row['SQ_CANDIDATO']}",
        "name": row["NM_URNA_CANDIDATO"].strip(),
        "full_name": row["NM_CANDIDATO"].strip(),
        "role": row["DS_CARGO"],
        "party": row["SG_PARTIDO"],
        "party_name": row["NM_PARTIDO"],
        "federation": null_if_tse_blank(row["SG_FEDERACAO"]),
        "status": row["DS_SIT_TOT_TURNO"],
        "round": int(row["NR_TURNO"]),
        "mandate": {
            "start": None,
            "end": None,
            "duration_years": 4,
            "note": (
                "Mandato de quatro anos (art. 27, par. 1, CF). As datas de posse e de fim seguem a Constituição de cada "
                "estado (e a Lei Orgânica do DF) e não constam do cadastro do TSE."
            ),
            "source": CF_URL,
        },
        "record_basis": RECORD_BASIS,
        "source": TSE_CAND_URL.format(year=year),
    }


def main():
    by_uf = defaultdict(dict)
    counts = {"total": {}, "by_uf": defaultdict(dict), "by_status": {}, "with_federation": {}}
    checks = {}
    for year in YEARS:
        people = defaultdict(list)
        status = Counter()
        elections = Counter()
        for row in iter_rows(year, cargos=CARGOS, elected_only=True):
            assert row["DS_SIT_TOT_TURNO"] in ELECTED
            people[row["SG_UF"]].append(person(row, year))
            status[row["DS_SIT_TOT_TURNO"]] += 1
            elections[(row["NM_TIPO_ELEICAO"], row["DS_ELEICAO"], br_date(row["DT_ELEICAO"]))] += 1
        assert len(elections) == 1, f"{year}: mais de uma eleição no recorte: {elections}"
        ids = [p["id"] for ps in people.values() for p in ps]
        assert len(ids) == len(set(ids)), f"{year}: SQ_CANDIDATO repetido"
        mismatches = {uf: len(people.get(uf, [])) for uf in EXPECTED_SEATS if len(people.get(uf, [])) != EXPECTED_SEATS[uf]}
        assert not mismatches, f"{year}: contagem por UF difere do tamanho da assembleia: {mismatches}"
        roles = {(uf, p["role"]) for uf, ps in people.items() for p in ps}
        assert all((r == "DEPUTADO DISTRITAL") == (uf == "DF") for uf, r in roles), "cargo incompatível com a UF"
        for uf, ps in people.items():
            by_uf[uf][str(year)] = sorted(ps, key=lambda p: (p["name"], p["id"]))
            counts["by_uf"][uf][str(year)] = len(ps)
        counts["total"][str(year)] = {
            "deputado_estadual": sum(len(ps) for uf, ps in people.items() if uf != "DF"),
            "deputado_distrital": len(people.get("DF", [])),
        }
        counts["by_status"][str(year)] = dict(status)
        counts["with_federation"][str(year)] = sum(1 for ps in people.values() for p in ps if p["federation"])
        checks[f"election_{year}"] = dict(zip(("type", "description", "date"), next(iter(elections))))
    checks["count_per_uf_equals_assembly_size"] = True
    checks["unique_candidate_ids"] = True
    counts["by_uf"] = dict(sorted(counts["by_uf"].items()))

    doc = {
        "dataset": "state-deputies",
        "collected_on": COLLECTED_ON,
        "scope_note": (
            "Deputados estaduais (e deputados distritais, no DF) ELEITOS nas eleições gerais de 2018 e 2022, por UF, "
            "segundo o cadastro de candidaturas do TSE (situação final 'ELEITO POR QP' ou 'ELEITO POR MÉDIA'). São "
            "'eleitos', não 'em exercício': suplentes que assumiram, substituições, licenças, cassações, recontagens "
            "posteriores à geração do arquivo e trocas de partido depois da eleição não estão cobertos. O partido é o da "
            "candidatura (party at the time); 'federation' traz a sigla da federação partidária registrada pelo TSE em 2022 "
            "(não existiam federações em 2018). O cadastro do TSE não informa datas de posse; o mandato é de quatro anos "
            "(art. 27, par. 1, da Constituição Federal) e as datas de início e fim seguem a Constituição de cada estado. Sem "
            "dados pessoais: só nome, cargo, partido e dados da eleição."
        ),
        "sources": [
            {"name": "TSE, Cadastro de candidaturas 2018 (consulta_cand)", "url": TSE_CAND_URL.format(year=2018)},
            {"name": "TSE, Cadastro de candidaturas 2022 (consulta_cand)", "url": TSE_CAND_URL.format(year=2022)},
            {"name": "Constituição Federal, arts. 27 e 32 (assembleias estaduais e Câmara Legislativa do DF)", "url": CF_URL},
        ],
        "build_script": "pipelines/politicians/build_state_deputies.py",
        "counts": counts,
        "checks": checks,
        "by_uf": dict(sorted(by_uf.items())),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"counts": {k: v for k, v in counts.items() if k != "by_uf"}, "checks": checks}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
