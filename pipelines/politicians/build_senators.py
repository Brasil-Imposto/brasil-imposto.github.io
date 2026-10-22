#!/usr/bin/env python3
"""Builds data/politicians/senators.json from the open data API of the Senado Federal.

Coverage: every senator (full member or substitute) with any period in office between
2019-02-01 and the collection date. Single source: https://legis.senado.leg.br/dadosabertos

Usage:
    POLITICIANS_WORK=/path/to/cache python3 build_senators.py

Python 3 standard library only. The raw API responses are kept in
$POLITICIANS_WORK/api/senado/ so that a new run does not repeat downloads.
Delete that folder to force a new collection.
"""
import concurrent.futures
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://legis.senado.leg.br/dadosabertos"
WINDOW_START = "2019-02-01"
COLLECTED_ON = os.environ.get("POLITICIANS_COLLECTED_ON", dt.date.today().isoformat())
WORK = os.environ.get("POLITICIANS_WORK", "/tmp/politicians-work")
CACHE = os.path.join(WORK, "api", "senado")
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(REPO, "data", "politicians", "senators.json")
MAX_WORKERS = 8

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB",
       "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]

# Terms of use of the photos, read on the Senado's official pages on 2026-10-01 (see research note).
# Literal citations; no Creative Commons license is declared for the official photos.
PORTAL_TERMS_URL = "https://www12.senado.leg.br/institucional/documentos/politica-de-uso-do-portal-do-senado-federal"
AGENCIA_TERMS_URL = "https://www12.senado.leg.br/noticias/politica-de-uso"
PHOTO_LICENSE = {
    "license": "Uso permitido com citacao da fonte (Politica de Uso do Portal do Senado Federal)",
    "author": "Senado Federal",
    "terms_source": PORTAL_TERMS_URL,
    "block": {
        "holder": "Senado Federal",
        "terms": ("\"Todo o conteúdo deste Portal é de propriedade autoral do Senado Federal, mas pode ser "
                  "utilizado pelos usuários, desde que seja citada a fonte e para fins lícitos.\" "
                  "(Política de Uso do Portal do Senado Federal). Termo complementar da Agência Senado, "
                  "para fotografias publicadas pela agência: \"A reprodução de matérias e fotografias é livre, "
                  "desde que não haja descaracterização de conteúdo e mediante a citação da Agência Senado "
                  "e do autor.\" (" + AGENCIA_TERMS_URL + ")"),
        "terms_source": PORTAL_TERMS_URL,
        "verified_on": "2026-10-01",
        "note": ("As fotos oficiais sao servidas pelo portal senado.leg.br (URL informada pela API). A API "
                 "nao informa o fotografo de cada retrato; o credito exigido e a fonte 'Senado Federal'. "
                 "Nao foi encontrada licenca Creative Commons declarada para estas fotos."),
    },
}


def as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def cache_path(url):
    name = re.sub(r"[^A-Za-z0-9]+", "_", url.replace(API, "")).strip("_")
    return os.path.join(CACHE, name + ".json")


def fetch_json(url):
    """GET with an on-disk cache and retries on 429/5xx."""
    path = cache_path(url)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    last = None
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={
                "Accept": "application/json",
                "User-Agent": "brasil-imposto-data/1.0 (pesquisa civica; dados abertos)"})
            with urllib.request.urlopen(req, timeout=90) as resp:
                body = resp.read()
            data = json.loads(body.decode("utf-8"))
            os.makedirs(CACHE, exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False)
            return data
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code not in (429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last = exc
        time.sleep(2 ** attempt)
    raise RuntimeError(f"falha ao obter {url}: {last}")


def head_ok(url):
    """Checks (without downloading the image) that the photo URL answers 200 with image content."""
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "brasil-imposto-data/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status == 200 and resp.headers.get("Content-Type", "").startswith("image/")
    except Exception:
        return False


def build():
    list_url = f"{API}/senador/lista/legislatura/56/57.json"
    listing = fetch_json(list_url)
    parl = as_list(listing["ListaParlamentarLegislatura"]["Parlamentares"]["Parlamentar"])
    ident_by_code = {p["IdentificacaoParlamentar"]["CodigoParlamentar"]: p["IdentificacaoParlamentar"]
                     for p in parl}
    codes = sorted(ident_by_code, key=int)

    def per_senator(code):
        murl = f"{API}/senador/{code}/mandatos.json"
        furl = f"{API}/senador/{code}/filiacoes.json"
        return code, murl, fetch_json(murl), furl, fetch_json(furl)

    with concurrent.futures.ThreadPoolExecutor(MAX_WORKERS) as pool:
        results = list(pool.map(per_senator, codes))

    by_uf = {uf: [] for uf in UFS}
    issues = []
    photo_checks = []
    for code, murl, mdata, furl, fdata in results:
        ident = ident_by_code[code]
        mandates = as_list(mdata["MandatoParlamentar"]["Parlamentar"].get("Mandatos", {}).get("Mandato"))
        terms = []
        ufs = set()
        for m in mandates:
            first = m["PrimeiraLegislaturaDoMandato"]
            second = m["SegundaLegislaturaDoMandato"]
            mandate_start, mandate_end = first["DataInicio"], second["DataFim"]
            if mandate_end < WINDOW_START or mandate_start > COLLECTED_ON:
                continue
            participation = m.get("DescricaoParticipacao", "")
            kind = "titular" if participation.strip().lower() == "titular" else "suplente"
            exercise = []
            for e in sorted(as_list((m.get("Exercicios") or {}).get("Exercicio")),
                            key=lambda x: x["DataInicio"]):
                start, end = e["DataInicio"], e.get("DataFim")
                end_reason = e.get("DescricaoCausaAfastamento")
                if end is None and mandate_end < COLLECTED_ON:
                    # The API returned no DataFim, but the term has already ended: records the end of the term.
                    end = mandate_end
                    end_reason = "Término do mandato (DataFim ausente na API; usado o fim do mandato)"
                    issues.append(f"senado:{code} exercicio {e.get('CodigoExercicio')} sem DataFim")
                if end is not None and end < WINDOW_START:
                    continue
                if start > COLLECTED_ON:
                    continue
                c_start = max(start, WINDOW_START)
                c_end = end if (end is not None and end <= COLLECTED_ON) else None
                if end is not None and end > COLLECTED_ON:
                    end_reason = None
                exercise.append({
                    "start": c_start,
                    "end": c_end,
                    "start_reason": None,
                    "end_reason": end_reason if c_end is not None else None,
                    "start_clipped_to_window": start < WINDOW_START,
                    "api_exercise_code": e.get("CodigoExercicio"),
                })
            if not exercise:
                continue
            ufs.add(m["UfParlamentar"])
            term = {
                "mandate_start": mandate_start,
                "mandate_end": mandate_end,
                "legislatures": [int(first["NumeroLegislatura"]), int(second["NumeroLegislatura"])],
                "uf": m["UfParlamentar"],
                "kind": kind,
                "participation": participation.strip(),
                "exercise": exercise,
                "source": murl,
            }
            if kind == "suplente" and m.get("Titular"):
                term["titular"] = {"id": "senado:" + m["Titular"]["CodigoParlamentar"],
                                   "name": m["Titular"]["NomeParlamentar"]}
            terms.append(term)
        if not terms:
            continue
        if len(ufs) != 1:
            issues.append(f"senado:{code} com exercicio em mais de uma UF: {sorted(ufs)}")
        uf = sorted(ufs)[0]

        parties = []
        filiacoes = as_list(fdata["FiliacaoParlamentar"]["Parlamentar"].get("Filiacoes", {}).get("Filiacao"))
        for f in sorted(filiacoes, key=lambda x: x.get("DataFiliacao") or ""):
            start, end = f.get("DataFiliacao"), f.get("DataDesfiliacao")
            if end is not None and end < WINDOW_START:
                continue
            if start is not None and start > COLLECTED_ON:
                continue
            parties.append({"party": f["Partido"]["SiglaPartido"], "party_name": f["Partido"].get("NomePartido"),
                            "start": start, "end": end, "source": furl})
        if not parties:
            issues.append(f"senado:{code} sem filiacao na janela")

        raw_photo = ident.get("UrlFotoParlamentar")
        photo = None
        photo_null_reason = None
        if raw_photo:
            https_photo = raw_photo.replace("http://", "https://", 1)
            photo_checks.append((code, https_photo))
            photo = {
                "url": https_photo,
                "api_url": raw_photo,
                "license": PHOTO_LICENSE["license"],
                "author": PHOTO_LICENSE["author"],
                "terms_source": PHOTO_LICENSE["terms_source"],
                "source": list_url,
            }
        else:
            photo_null_reason = ("A API do Senado nao informa UrlFotoParlamentar para este codigo "
                                 f"em {list_url}")

        person = {
            "id": f"senado:{code}",
            "name": ident["NomeParlamentar"],
            "full_name": ident.get("NomeCompletoParlamentar"),
            "role": "Senador",
            "terms": terms,
            "party_history": parties,
            "photo": photo,
        }
        if photo is None:
            person["photo_null_reason"] = photo_null_reason
        by_uf[uf].append(person)

    # Checks that each photo exists (HEAD, without downloading the file). The result is cached.
    head_cache_path = os.path.join(WORK, "api", "senado_photo_head.json")
    head_cache = json.load(open(head_cache_path, encoding="utf-8")) if os.path.exists(head_cache_path) else {}
    todo = [u for _, u in photo_checks if u not in head_cache]
    with concurrent.futures.ThreadPoolExecutor(MAX_WORKERS) as pool:
        for url, result in zip(todo, pool.map(head_ok, todo)):
            head_cache[url] = result
    with open(head_cache_path, "w", encoding="utf-8") as fh:
        json.dump(head_cache, fh)
    ok = {c: head_cache.get(u, False) for c, u in photo_checks}
    for uf in UFS:
        for p in by_uf[uf]:
            code = p["id"].split(":")[1]
            if p["photo"] is not None and not ok.get(code):
                p["photo_null_reason"] = f"URL informada pela API nao respondeu com imagem em {COLLECTED_ON}: {p['photo']['url']}"
                p["photo"] = None
        by_uf[uf].sort(key=lambda p: (min(e["start"] for t in p["terms"] for e in t["exercise"]), p["name"]))

    return list_url, by_uf, issues


def in_exercise_on(person, day, end_of_day=False):
    """Default: inclusive dates, as the Senado API records them (DataFim is the last day in office).
    With end_of_day=True, whoever leaves on that date does not count (the state at the end of the day)."""
    for t in person["terms"]:
        for e in t["exercise"]:
            if e["start"] <= day and (e["end"] is None or (day < e["end"] if end_of_day else day <= e["end"])):
                return True
    return False


def explain_anomaly(people, uf, day, n):
    """Describes, with API data only, why the day's count differs from 3."""
    periods = [(p["name"], e) for p in people for t in p["terms"] for e in t["exercise"]]
    item = {"uf": uf, "day": day, "in_exercise": n,
            "who": [p["name"] for p in people if in_exercise_on(p, day)]}
    if n > 3:
        same_day = [{"name": name, "start": e["start"], "end": e["end"], "end_reason": e["end_reason"]}
                    for name, e in periods if e["start"] == day or e["end"] == day]
        item["cause"] = ("Transicao no mesmo dia: a API registra o fim de um exercicio e o inicio de outro "
                         "na mesma data (datas inclusivas)")
        item["evidence"] = same_day
    else:
        exits = sorted([(e["end"], name, e["end_reason"]) for name, e in periods
                        if e["end"] is not None and e["end"] < day])
        entries = sorted([(e["start"], name) for name, e in periods if e["start"] > day])
        item["cause"] = "Cadeira sem senador em exercicio nesta data segundo os registros de exercicio da API"
        item["evidence"] = {
            "last_exit_before": ({"name": exits[-1][1], "end": exits[-1][0], "end_reason": exits[-1][2]}
                                 if exits else None),
            "next_entry_after": ({"name": entries[0][1], "start": entries[0][0]} if entries else None),
        }
    return item


def month_starts():
    y, m = 2019, 2
    out = []
    while f"{y:04d}-{m:02d}-01" <= COLLECTED_ON:
        out.append(f"{y:04d}-{m:02d}-01")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def main():
    list_url, by_uf, issues = build()
    persons = [p for uf in UFS for p in by_uf[uf]]
    days = month_starts()
    anomalies = []
    for uf in UFS:
        for d in days:
            n = sum(1 for p in by_uf[uf] if in_exercise_on(p, d))
            if n != 3:
                anomalies.append(explain_anomaly(by_uf[uf], uf, d, n))
    end_of_day_anomalies = sum(1 for uf in UFS for d in days
                               if sum(1 for p in by_uf[uf] if in_exercise_on(p, d, True)) != 3)
    counts = {
        "persons": len(persons),
        "terms": sum(len(p["terms"]) for p in persons),
        "exercise_periods": sum(len(t["exercise"]) for p in persons for t in p["terms"]),
        "persons_with_suplente_exercise": sum(1 for p in persons if any(t["kind"] == "suplente" for t in p["terms"])),
        "persons_titular_only": sum(1 for p in persons if all(t["kind"] == "titular" for t in p["terms"])),
        "persons_in_exercise_on_collection_day": sum(1 for p in persons if in_exercise_on(p, COLLECTED_ON)),
        "persons_without_photo": sum(1 for p in persons if p["photo"] is None),
        "by_uf": {uf: len(by_uf[uf]) for uf in UFS},
        "check_month_starts_sampled": len(days),
        "check_uf_days_not_equal_3": len(anomalies),
        "check_uf_days_not_equal_3_end_of_day": end_of_day_anomalies,
    }
    out = {
        "dataset": "senators",
        "collected_on": COLLECTED_ON,
        "period": {"start": WINDOW_START, "end": COLLECTED_ON},
        "scope_note": (
            "Todos os senadores, titulares e suplentes, com ao menos um periodo de exercicio do mandato entre "
            f"{WINDOW_START} e {COLLECTED_ON}, agrupados pela UF do mandato. Os periodos de exercicio vem dos "
            "registros Exercicios (DataInicio, DataFim, DescricaoCausaAfastamento) do endpoint de mandatos do "
            "Senado; 'end_reason' e a causa de afastamento informada pela API ao fim do periodo; 'start_reason' e "
            "null porque a API nao informa motivo de inicio. Intervalos recortados na janela da coleta "
            "('start_clipped_to_window' indica inicio anterior a 2019-02-01). 'end' null significa em exercicio na "
            "data da coleta. Datas de 'end' sao o ultimo dia de exercicio registrado pela API (inclusive). "
            "Historico partidario: endpoint de filiacoes, somente filiacoes que se sobrepoem a janela. "
            "Nao inclui candidaturas nem resultados eleitorais. A URL da foto e a informada pela API, com o "
            "esquema trocado de http para https (o servidor redireciona para a mesma imagem)."
        ),
        "sources": [
            {"name": "Senado Federal, Dados Abertos: lista de senadores das legislaturas 56 e 57", "url": list_url},
            {"name": "Senado Federal, Dados Abertos: mandatos e exercicios por senador", "url": f"{API}/senador/{{codigo}}/mandatos.json"},
            {"name": "Senado Federal, Dados Abertos: filiacoes partidarias por senador", "url": f"{API}/senador/{{codigo}}/filiacoes.json"},
        ],
        "photo_license": PHOTO_LICENSE["block"],
        "build_script": "pipelines/politicians/build_senators.py",
        "counts": counts,
        "checks": {
            "convention": ("Contagem no primeiro dia de cada mes com datas inclusivas, como a API do Senado registra "
                           "(DataFim e o ultimo dia de exercicio): numa troca registrada no mesmo dia, as duas pessoas "
                           "contam."),
            "uf_days_not_equal_3": anomalies,
            "data_issues": issues,
        },
        "by_uf": by_uf,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(json.dumps(counts, ensure_ascii=False))
    print("anomalias:", len(anomalies), "issues:", len(issues))


if __name__ == "__main__":
    sys.exit(main())
