"""Gera data/politicians/<uf>-mayors.json: prefeitos e vice-prefeitos ELEITOS num estado nas eleições municipais
escolhidas, incluindo as eleições suplementares do mesmo ciclo. Generaliza o antigo build_sc_mayors.py (mesmo esquema).

Fontes (todas oficiais; nada gravado em disco: os zips do TSE são lidos por HTTP Range, só o CSV da UF):
- TSE, cadastro de candidaturas (consulta_cand) de cada ano;
- TSE, códigos oficiais de municípios segundo o TSE e o IBGE (municipio_tse_ibge);
- TSE, listagem das eleições suplementares de cada ciclo (conferência cruzada);
- TSE, votação nominal por município e zona (votacao_candidato_munzona), só para conferir os eleitos;
- IBGE, API de localidades (nome oficial do município e conferência dos códigos).

Checagens que barram a gravação (cada uma com controle plantado que tem de falhar, --control):
- coverage: todo município tem prefeito eleito na eleição ordinária de cada ano, ou a ausência está nos dados do TSE
  (eleição suplementar no ciclo, ou candidatura INAPTA no cadastro, ou votos anulados na votação nominal);
- totals: os prefeitos eleitos de cada ano são exatamente os eleitos da votação nominal do TSE na UF;
- vice: cada eleição com prefeito eleito tem um vice eleito da mesma chapa (mesmo número), e só ela.

Uso:
  python3 pipelines/politicians/build_mayors.py                    # SC, 2020 e 2024 (padrão)
  python3 pipelines/politicians/build_mayors.py --uf RS            # RS, 2016, 2020 e 2024
  python3 pipelines/politicians/build_mayors.py --uf RS --control totals   # tem de falhar e não gravar nada
  --out CAMINHO grava em outro lugar; --replace permite trocar um arquivo existente de conteúdo diferente.
Só biblioteca padrão do Python 3.
"""
import argparse
import csv
import gzip
import io
import json
import pathlib
import sys
import unicodedata
import urllib.request
import zipfile
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from tse_common import TSE_CAND_URL, UA, RemoteZip, br_date, uf_rows  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
CARGOS = {"PREFEITO": "mayor", "VICE-PREFEITO": "vice_mayor"}

# Cada estado guarda os anos e a data de coleta do arquivo publicado; SC é o arquivo de 2026-10-01, sem mudança.
STATES = {
    "SC": {"ibge": "42", "of_name": "de Santa Catarina", "municipalities": 295, "years": (2020, 2024),
           "collected_on": "2026-10-01"},
    "RS": {"ibge": "43", "of_name": "do Rio Grande do Sul", "municipalities": 497, "years": (2020, 2024),  # D80: from 2020, as SC
           "collected_on": "2026-10-04"},
}

CF_URL = "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"
# Art. 29, I e III, CF: mandato de quatro anos, posse em 1º de janeiro do ano seguinte à eleição.
MANDATES = {2016: ("2017-01-01", "2020-12-31"), 2020: ("2021-01-01", "2024-12-31"), 2024: ("2025-01-01", "2028-12-31")}

CROSSWALK_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/municipio_tse_ibge/municipio_tse_ibge.zip"
CROSSWALK_PAGE = "https://dadosabertos.tse.jus.br/dataset/codigos-oficiais-de-uf-e-municipios-segundo-o-tse-e-o-ibge"
SUPPL_LIST_URL = (
    "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes{year}/listaelesuplem/"
    "lista_eleicoes_suplementares_{year}.zip"
)
VOTES_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_{year}.zip"
IBGE_API_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/{ibge}/municipios"

RECORD_BASIS = "eleito: resultado da eleição no cadastro do TSE, não indica exercício do mandato"
TYPE_LABEL = {"ELEIÇÃO ORDINÁRIA": "ordinaria", "ELEIÇÃO SUPLEMENTAR": "suplementar"}
CONTROLS = ("coverage", "totals", "vice")


def fetch(url):
    """Baixa para a memória (arquivos pequenos: tabela TSE-IBGE, listagens, API do IBGE)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read()
        # A API do IBGE responde em gzip mesmo sem Accept-Encoding (visto em 2026-10-04).
        return gzip.decompress(body) if r.headers.get("Content-Encoding") == "gzip" else body


def tse_csv(data):
    """Linhas do único CSV de um zip do TSE (latin-1, ';')."""
    z = zipfile.ZipFile(io.BytesIO(data))
    name = next(n for n in z.namelist() if n.endswith(".csv"))
    return list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="latin-1"), delimiter=";"))


def norm(s):
    """Nome normalizado para conferência: sem acento, minúsculo, sem apóstrofo, hífen nem espaço repetido."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    for ch in "'’`-":
        s = s.replace(ch, " ")
    return " ".join(s.split())


def null_if_tse_blank(v):
    """O TSE usa #NULO / #NULO# / #NE para campo vazio."""
    return None if not v or v.startswith("#") else v


def join_pt(items):
    items = [str(i) for i in items]
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " e " + items[-1]


def load_crosswalk(uf):
    rows = [r for r in tse_csv(fetch(CROSSWALK_URL)) if r["SG_UF"] == uf]
    tse_to_ibge = {r["CD_MUNICIPIO_TSE"]: str(r["CD_MUNICIPIO_IBGE"]) for r in rows}
    ibge_to_tse = {v: k for k, v in tse_to_ibge.items()}
    if not (len(rows) == len(tse_to_ibge) == len(ibge_to_tse)):
        raise SystemExit(f"tabela TSE-IBGE não é um para um em {uf}")
    generated = rows[0]["DT_GERACAO"] if rows else None
    return tse_to_ibge, generated


def load_ibge_names(ibge_uf):
    data = json.loads(fetch(IBGE_API_URL.format(ibge=ibge_uf)).decode("utf-8"))
    return {str(m["id"]): m["nome"] for m in data}


def load_suppl_list(year, uf):
    rows = tse_csv(fetch(SUPPL_LIST_URL.format(year=year)))
    return {(r["CD_MUNICIPIO"], r["CD_ELEICAO"]) for r in rows if r["SG_UF"] == uf and r["DS_CARGO"].upper() == "PREFEITO"}


def load_votes(year, uf):
    """Votação nominal do TSE na UF: SQ dos prefeitos eleitos, e os municípios em que o mais votado para prefeito no
    1º turno da eleição ordinária teve os votos anulados."""
    data = RemoteZip(VOTES_URL.format(year=year)).member(f"votacao_candidato_munzona_{year}_{uf}.csv")
    elected = set()
    votes = defaultdict(lambda: defaultdict(int))  # sg_ue -> sq -> votos nominais no 1º turno da ordinária
    annulled_sq = set()
    for r in csv.DictReader(io.TextIOWrapper(io.BytesIO(data), encoding="latin-1"), delimiter=";"):
        if r["DS_CARGO"].upper() != "PREFEITO":
            continue
        if r["DS_SIT_TOT_TURNO"] == "ELEITO":
            elected.add(r["SQ_CANDIDATO"])
        if r["NM_TIPO_ELEICAO"].startswith("Eleição Ordin") and r["NR_TURNO"] == "1":
            votes[r["SG_UE"]][r["SQ_CANDIDATO"]] += int(r["QT_VOTOS_NOMINAIS"])
            if r["NM_TIPO_DESTINACAO_VOTOS"].startswith("Anulado"):
                annulled_sq.add(r["SQ_CANDIDATO"])
    top_annulled = {ue for ue, by_sq in votes.items() if max(by_sq, key=by_sq.get) in annulled_sq}
    return elected, top_annulled


def person(row, year, mandate):
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
        "mandate": mandate,
        "record_basis": RECORD_BASIS,
        "source": TSE_CAND_URL.format(year=year),
    }


def mandate_for(year, kind):
    start, end = MANDATES[year]
    if kind == "ordinaria":
        return {"start": start, "end": end, "source": CF_URL}
    return {
        "start": None,
        "end": end,
        "note": (
            "Eleição suplementar do mesmo ciclo: o cadastro do TSE não informa a data de posse. "
            f"O fim é o do mandato do ciclo ({end}, art. 29 da CF)."
        ),
        "source": CF_URL,
    }


def plant(control, elections, elected, cand_rows):
    """Defeito de controle: a checagem correspondente tem de falhar."""
    ords = sorted(k for k in elections if k[2] == "ELEIÇÃO ORDINÁRIA" and elected[k].get("PREFEITO"))
    if control == "coverage":  # some o prefeito eleito de uma eleição ordinária sem nenhuma explicação nos dados
        suppl_ues = {(k[0], k[1]) for k in elections if k[2] != "ELEIÇÃO ORDINÁRIA"}
        k = next(k for k in ords if (k[0], k[1]) not in suppl_ues and not any(
            r["DS_SITUACAO_CANDIDATURA"] == "INAPTO" for r in cand_rows[k]))
        elected[k]["PREFEITO"] = []
    elif control == "totals":  # troca o eleito pelo segundo colocado da mesma eleição
        k = next(k for k in ords if any(r["DS_CARGO"] == "PREFEITO" and r["DS_SIT_TOT_TURNO"] == "NÃO ELEITO" for r in cand_rows[k]))
        elected[k]["PREFEITO"] = [next(r for r in cand_rows[k] if r["DS_CARGO"] == "PREFEITO" and r["DS_SIT_TOT_TURNO"] == "NÃO ELEITO")]
    elif control == "vice":  # some o vice eleito de uma chapa eleita
        elected[ords[0]]["VICE-PREFEITO"] = []
    print(f"CONTROLE '{control}' plantado em {k if control != 'vice' else ords[0]}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uf", default="SC", choices=sorted(STATES))
    ap.add_argument("--out", help="arquivo de saída (padrão: data/politicians/<uf>-mayors.json)")
    ap.add_argument("--replace", action="store_true", help="permite trocar um arquivo existente de conteúdo diferente")
    ap.add_argument("--control", choices=CONTROLS, help="planta um defeito; a checagem tem de falhar e nada é gravado")
    args = ap.parse_args()
    UF = args.uf
    cfg = STATES[UF]
    YEARS = cfg["years"]
    N = cfg["municipalities"]
    out = pathlib.Path(args.out) if args.out else REPO / "data" / "politicians" / f"{UF.lower()}-mayors.json"
    ibge_api_url = IBGE_API_URL.format(ibge=cfg["ibge"])

    tse_to_ibge, crosswalk_generated = load_crosswalk(UF)
    ibge_names = load_ibge_names(cfg["ibge"])
    checks = {}

    # Cruzamento 1:1 nos dois sentidos, contra a API do IBGE.
    if not (len(tse_to_ibge) == N):
        raise SystemExit(len(tse_to_ibge))
    if not (set(tse_to_ibge.values()) == set(ibge_names)):
        raise SystemExit("códigos IBGE da tabela do TSE diferem da API do IBGE")

    # Chave da eleição: (sg_ue, ano, tipo, descrição). O 2º turno tem CD_ELEICAO próprio no TSE,
    # então os códigos e as datas ficam guardados por turno dentro da mesma eleição.
    elections = defaultdict(dict)  # chave -> metadados
    elected = defaultdict(lambda: defaultdict(list))  # chave -> cargo -> linhas ELEITO
    cand_rows = defaultdict(list)  # chave -> todas as linhas (só para as checagens)
    tse_names = {}
    for year in YEARS:
        for row in uf_rows(year, UF, cargos=set(CARGOS), elected_only=False):
            key = (row["SG_UE"], year, row["NM_TIPO_ELEICAO"], row["DS_ELEICAO"])
            tse_names[row["SG_UE"]] = row["NM_UE"]
            meta = elections[key]
            meta.setdefault("rounds", {})[int(row["NR_TURNO"])] = (row["CD_ELEICAO"], br_date(row["DT_ELEICAO"]))
            cand_rows[key].append(row)
            if row["DS_SIT_TOT_TURNO"] == "ELEITO":
                elected[key][row["DS_CARGO"]].append(row)
        print(f"{UF} {year}: cadastro lido", flush=True)
    if args.control:
        plant(args.control, elections, elected, cand_rows)

    unmapped = sorted(set(tse_names) - set(tse_to_ibge))
    if not (not unmapped):
        raise SystemExit(f"SG_UE sem código IBGE: {unmapped}")
    if not (set(tse_names) == set(tse_to_ibge)):
        raise SystemExit("municípios do cadastro diferem da tabela TSE-IBGE")

    # Nomes TSE x IBGE: só conferência, o nome publicado é o do IBGE.
    name_diffs = sorted(
        f"{tse_names[u]} / {ibge_names[tse_to_ibge[u]]}"
        for u in tse_names
        if norm(tse_names[u]) != norm(ibge_names[tse_to_ibge[u]])
    )

    suppl_listed = {y: load_suppl_list(y, UF) for y in YEARS}
    # Suplementar que está no cadastro e não está na listagem do TSE (ex.: marcada e sem resultado).
    unlisted = {
        (k[0], k[1], elections[k]["rounds"][1][0])
        for k in elections
        if k[2] != "ELEIÇÃO ORDINÁRIA" and (k[0], elections[k]["rounds"][1][0]) not in suppl_listed[k[1]]
    }
    counts = {"municipalities": len(tse_to_ibge), "by_year": {}}
    exceptions = defaultdict(list)
    municipalities = []
    for sg_ue, ibge in sorted(tse_to_ibge.items(), key=lambda kv: ibge_names[kv[1]]):
        records = []
        for key in sorted(k for k in elections if k[0] == sg_ue):
            _, year, type_tse, description = key
            rounds = elections[key]["rounds"]
            if not (set(rounds) in ({1}, {1, 2})):
                raise SystemExit(f"turnos inesperados em {key}")
            kind = TYPE_LABEL[type_tse]
            people = {}
            for cargo, field in CARGOS.items():
                rows = elected[key].get(cargo, [])
                if not (len(rows) <= 1):
                    raise SystemExit(f"mais de um {cargo} ELEITO em {key}")
                people[field] = person(rows[0], year, mandate_for(year, kind)) if rows else None
            notes = []
            if people["mayor"] is None:
                notes.append(
                    "Nenhuma candidatura a prefeito com situação final 'ELEITO' nesta eleição no cadastro do TSE."
                )
                exceptions[str(year)].append(
                    {"municipality": ibge_names[ibge], "tse_code": sg_ue, "election": description, "issue": "sem prefeito eleito"}
                )
            if (sg_ue, year, rounds[1][0]) in unlisted:
                notes.append(f"Esta eleição não consta da listagem de eleições suplementares do TSE do ciclo {year}.")
                if rounds[1][1] and rounds[1][1] > cfg["collected_on"]:
                    notes.append(f"A data da eleição é posterior à coleta ({cfg['collected_on']}).")
                exceptions[str(year)].append(
                    {"municipality": ibge_names[ibge], "tse_code": sg_ue, "election": f"{description} ({rounds[1][1]})",
                     "issue": "eleição suplementar no cadastro, fora da listagem do TSE"}
                )
            records.append(
                {
                    "year": year,
                    "type": kind,
                    "election_type_tse": type_tse,
                    "election_code_tse": rounds[1][0],
                    "election_date": rounds[1][1],
                    "description": description,
                    "rounds_held": max(rounds),
                    "second_round": {"election_code_tse": rounds[2][0], "date": rounds[2][1]} if 2 in rounds else None,
                    "mayor": people["mayor"],
                    "vice_mayor": people["vice_mayor"],
                    "note": " ".join(notes) or None,
                }
            )
        # Eleição suplementar no ciclo: registra o fato no registro da ordinária, sem inferir exercício.
        for rec in records:
            if rec["type"] != "ordinaria":
                continue
            suppl = [r for r in records if r["year"] == rec["year"] and r["type"] == "suplementar"]
            if not suppl and rec["mayor"] is None:
                rec["note"] += (
                    f" A listagem de eleições suplementares do TSE para o ciclo {rec['year']} não registra "
                    "eleição suplementar para este município. Este arquivo não informa quem exerceu o cargo."
                )
            if suppl:
                txt = "; ".join(f"{s['description']} ({s['election_date']})" for s in suppl)
                extra = (
                    f"O cadastro do TSE registra eleição suplementar para prefeito no mesmo ciclo: {txt}. "
                    "Este arquivo não informa quem exerceu o cargo nem em que período."
                )
                rec["note"] = f"{rec['note']} {extra}" if rec["note"] else extra
                exceptions[str(rec["year"])].append(
                    {"municipality": ibge_names[ibge], "tse_code": sg_ue, "election": txt, "issue": "eleição suplementar no ciclo"}
                )
        municipalities.append(
            {
                "ibge_code": ibge,
                "tse_code": sg_ue,
                "name": ibge_names[ibge],
                "name_tse": tse_names[sg_ue],
                "elections": records,
            }
        )

    # Checagens por ano.
    failures = []
    for year in YEARS:
        ords = [(m, r) for m in municipalities for r in m["elections"] if r["year"] == year and r["type"] == "ordinaria"]
        sups = [(m, r) for m in municipalities for r in m["elections"] if r["year"] == year and r["type"] == "suplementar"]
        per_muni = defaultdict(int)
        for m, _ in ords:
            per_muni[m["tse_code"]] += 1
        if not (len(per_muni) == N and set(per_muni.values()) == {1}):
            raise SystemExit(f"{year}: eleição ordinária não é única por município")
        found_suppl = {(m["tse_code"], r["election_code_tse"]) for m, r in sups}
        if not (suppl_listed[year] <= found_suppl):
            raise SystemExit(f"{year}: suplementar da listagem do TSE ausente do cadastro")
        for m, r in sups:
            if (m["tse_code"], year, r["election_code_tse"]) in unlisted:
                if not (r["mayor"] is None):
                    raise SystemExit(f"{year}: suplementar com eleito fora da listagem do TSE: {m['name']}")
        counts["by_year"][str(year)] = {
            "ordinary_elections": len(ords),
            "ordinary_mayors_elected": sum(1 for _, r in ords if r["mayor"]),
            "ordinary_vice_mayors_elected": sum(1 for _, r in ords if r["vice_mayor"]),
            "ordinary_second_round": sum(1 for _, r in ords if r["rounds_held"] == 2),
            "supplementary_elections": len(sups),
            "supplementary_mayors_elected": sum(1 for _, r in sups if r["mayor"]),
            "supplementary_vice_mayors_elected": sum(1 for _, r in sups if r["vice_mayor"]),
        }

        # coverage: prefeito eleito na ordinária, ou ausência explicada pelos dados do TSE.
        votes_elected, votes_annulled = load_votes(year, UF)
        for m, r in ords:
            if r["mayor"]:
                continue
            key = next(k for k in elections if k[0] == m["tse_code"] and k[1] == year and k[2] == "ELEIÇÃO ORDINÁRIA")
            why = []
            if any(s["year"] == year and s["type"] == "suplementar" for s in m["elections"]):
                why.append("eleição suplementar no ciclo")
            if any(x["DS_CARGO"] == "PREFEITO" and x["DS_SITUACAO_CANDIDATURA"] == "INAPTO" for x in cand_rows[key]):
                why.append("candidatura INAPTA no cadastro")
            if m["tse_code"] in votes_annulled:
                why.append("o mais votado no 1º turno teve os votos anulados (votação nominal)")
            print(f"  coverage {year} {m['name']}: sem prefeito eleito na ordinária; explicação: {'; '.join(why) or 'NENHUMA'}")
            if not why:
                failures.append(f"coverage {year}: {m['name']} sem prefeito eleito e sem explicação nos dados do TSE")

        # totals: eleitos do cadastro = eleitos da votação nominal do TSE na UF.
        ours = {r[k]["id"].split(":")[2] for _, r in ords + sups for k in ("mayor",) if r[k]}
        if ours != votes_elected:
            failures.append(f"totals {year}: cadastro {len(ours)} x votação {len(votes_elected)}; "
                            f"só no cadastro {sorted(ours - votes_elected)[:5]}, só na votação {sorted(votes_elected - ours)[:5]}")
        print(f"  totals {year}: prefeitos eleitos no arquivo {len(ours)}, na votação nominal do TSE {len(votes_elected)}")

        # vice: um vice eleito da mesma chapa (mesmo número) onde há prefeito eleito, e nenhum onde não há.
        bad = []
        for m, r in ords + sups:
            key = next(k for k in elections if k[0] == m["tse_code"] and k[1] == year and k[3] == r["description"])
            mayor_rows, vice_rows = elected[key].get("PREFEITO", []), elected[key].get("VICE-PREFEITO", [])
            if len(mayor_rows) != len(vice_rows) or any(a["NR_CANDIDATO"] != b["NR_CANDIDATO"] for a, b in zip(mayor_rows, vice_rows)):
                bad.append(f"{m['name']} ({r['description']})")
        if bad:
            failures.append(f"vice {year}: {len(bad)} eleições sem par prefeito e vice da mesma chapa: {bad[:5]}")
        print(f"  vice {year}: {sum(1 for _, r in ords + sups if r['vice_mayor'])} vices eleitos; eleições sem par: {len(bad)}")

    if failures:
        for f in failures:
            print("CHECK FAILED", f)
        raise SystemExit(f"{len(failures)} checagem(ns) falharam; nada gravado")

    checks["tse_ibge_one_to_one"] = True
    checks["tse_ibge_codes_equal_ibge_api"] = True
    checks["one_ordinary_election_per_municipality_per_year"] = True
    checks["supplementary_match_tse_list"] = not unlisted
    checks["name_differences_tse_vs_ibge"] = name_diffs
    checks["exceptions"] = dict(exceptions)

    mandates_txt = join_pt(f"{MANDATES[y][0]} a {MANDATES[y][1]} ({y})" for y in YEARS)
    doc = {
        "dataset": f"{UF.lower()}-mayors",
        "collected_on": cfg["collected_on"],
        "scope_note": (
            f"Prefeitos e vice-prefeitos ELEITOS nos {N} municípios {cfg['of_name']} nas eleições municipais de {join_pt(YEARS)}, "
            "segundo o cadastro de candidaturas do TSE (situação final 'ELEITO'; no segundo turno vale a linha do turno final). "
            "São 'eleitos', não 'em exercício': cassações, renúncias, afastamentos, posse de vice ou de presidente da Câmara e "
            "trocas de partido depois da eleição não estão cobertos. As eleições suplementares do mesmo ciclo aparecem como "
            "registros separados (type 'suplementar', com data e descrição do TSE); o arquivo não diz quem exerceu o cargo nem "
            f"por quanto tempo. Mandato das eleições ordinárias: {mandates_txt}, "
            "art. 29 da Constituição Federal. O partido é o da candidatura (party at the time). O código IBGE vem da tabela "
            f"oficial do TSE 'Códigos oficiais de UF e municípios segundo o TSE e o IBGE' (correspondência um para um em {UF}, "
            f"{N}/{N}, conferida contra a API de localidades do IBGE); o nome do município é o da API do IBGE. Sem dados pessoais: "
            "só nome, cargo, partido e dados da eleição."
        ),
        "sources": [
            *({"name": f"TSE, Cadastro de candidaturas {y} (consulta_cand)", "url": TSE_CAND_URL.format(year=y)} for y in YEARS),
            {
                "name": f"TSE, Códigos oficiais de UF e municípios segundo o TSE e o IBGE (gerado em {crosswalk_generated})",
                "url": CROSSWALK_URL,
            },
            {"name": "TSE, Portal de Dados Abertos, página da tabela TSE-IBGE", "url": CROSSWALK_PAGE},
            *({"name": f"TSE, Listagem das eleições suplementares, ciclo {y}", "url": SUPPL_LIST_URL.format(year=y)} for y in YEARS),
            {"name": f"IBGE, API de localidades, municípios de {UF}", "url": ibge_api_url},
            {"name": "Constituição Federal, art. 29 (mandato e posse de prefeito)", "url": CF_URL},
        ],
        "build_script": "pipelines/politicians/build_mayors.py",
        "counts": counts,
        "checks": checks,
        "municipalities": municipalities,
    }
    text = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    if out.exists() and out.read_text(encoding="utf-8") != text and not args.replace:
        raise SystemExit(f"{out} existe com outro conteúdo; nada gravado (use --replace depois de conferir a diferença, ou --out)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(json.dumps({"out": str(out), "counts": counts, "checks": {k: v for k, v in checks.items() if k != "exceptions"}},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
