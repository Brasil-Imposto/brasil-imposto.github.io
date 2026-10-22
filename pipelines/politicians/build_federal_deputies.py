#!/usr/bin/env python3
"""Gera data/politicians/federal-deputies.json a partir da API de dados abertos da Camara dos Deputados.

Cobertura: todo deputado federal (titular ou suplente) que exerceu o mandato nas legislaturas 56
(2019-02-01 a 2023-01-31) e 57 (2023-02-01 a 2027-01-31), ate a data de coleta.
Fonte unica: https://dadosabertos.camara.leg.br/api/v2

Uso:
    POLITICIANS_WORK=/caminho/para/cache python3 build_federal_deputies.py

Somente biblioteca padrao do Python 3. As respostas brutas ficam em $POLITICIANS_WORK/api/camara/
para que uma nova execucao nao repita downloads. Apague essa pasta para forcar nova coleta.
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

API = "https://dadosabertos.camara.leg.br/api/v2"
WINDOW_START = "2019-02-01"
COLLECTED_ON = os.environ.get("POLITICIANS_COLLECTED_ON", dt.date.today().isoformat())
WORK = os.environ.get("POLITICIANS_WORK", "/tmp/politicians-work")
CACHE = os.path.join(WORK, "api", "camara")
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(REPO, "data", "politicians", "federal-deputies.json")
MAX_WORKERS = 8
LEGISLATURES = {56: ("2019-02-01", "2023-01-31"), 57: ("2023-02-01", "2027-01-31")}

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB",
       "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]

# Vagas por UF usadas apenas na conferencia (soma 513). Conferidas contra os proprios dados: numero de
# titulares empossados no primeiro dia de cada legislatura (ver checks.seats_observed_on_first_day).
SEATS = {"AC": 8, "AL": 9, "AM": 8, "AP": 8, "BA": 39, "CE": 22, "DF": 8, "ES": 10, "GO": 17, "MA": 18,
         "MG": 53, "MS": 8, "MT": 8, "PA": 17, "PB": 12, "PE": 25, "PI": 10, "PR": 30, "RJ": 46, "RN": 8,
         "RO": 8, "RR": 8, "RS": 31, "SC": 16, "SE": 8, "SP": 70, "TO": 8}

# Termos de uso lidos na pagina oficial da Camara em 2026-10-01 (ver nota de pesquisa). Citacao literal.
TERMS_URL = "https://www2.camara.leg.br/termo-de-uso-e-politica-de-privacidade"
PHOTO_LICENSE = {
    "holder": "Câmara dos Deputados",
    "terms": ("\"7. Você pode reproduzir gratuitamente dados, imagens e infografias publicados no portal da "
              "Câmara, desde que citada a fonte \"Câmara dos Deputados\" e a autoria da informação, quando "
              "houver.\" e \"29. Todas as informações publicadas no Portal da Câmara são de domínio público, "
              "gratuitas e podem ser reproduzidas desde que citada a fonte \"Câmara dos Deputados\" e a autoria "
              "da informação, quando houver.\" (Termo de uso e política de privacidade do portal da Câmara)"),
    "terms_source": TERMS_URL,
    "verified_on": "2026-10-01",
    "note": ("A API nao informa o fotografo de cada retrato oficial; o credito exigido e a fonte 'Câmara dos "
             "Deputados'. Nao foi encontrada licenca Creative Commons declarada para estas fotos."),
}
PHOTO_SHORT = "Reprodução gratuita com citação da fonte (Termo de uso do portal da Câmara)"


ENTRY_RE = re.compile(r"Entrada|Efetivação|Torna-se titular")


def cache_path(url):
    name = re.sub(r"[^A-Za-z0-9]+", "_", url.replace(API, "")).strip("_")
    return os.path.join(CACHE, name + ".json")


def fetch_json(url):
    """GET com cache em disco e novas tentativas em 429/5xx."""
    path = cache_path(url)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    last = None
    for attempt in range(7):
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
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as exc:
            last = exc
        time.sleep(min(2 ** attempt, 30))
    raise RuntimeError(f"falha ao obter {url}: {last}")


def head_ok(url):
    """Confere (sem baixar a imagem) se a URL da foto responde 200 com conteudo de imagem."""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, method="HEAD",
                                         headers={"User-Agent": "brasil-imposto-data/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.status == 200 and resp.headers.get("Content-Type", "").startswith("image/")
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 403, 410):
                return False
        except Exception:
            pass
        time.sleep(2 ** attempt)
    return False


def list_ids(leg):
    url = f"{API}/deputados?idLegislatura={leg}&itens=100&pagina=1&ordem=ASC&ordenarPor=nome"
    ids, pages = [], []
    while url:
        data = fetch_json(url)
        pages.append(url)
        ids.extend(d["id"] for d in data["dados"])
        url = next((l["href"] for l in data.get("links", []) if l["rel"] == "next"), None)
    return ids, pages


def day(ts):
    return ts[:10] if ts else None


def build_terms(dep_id, events):
    """Converte o historico de status em periodos de exercicio por legislatura."""
    hist_url = f"{API}/deputados/{dep_id}/historico"
    terms, issues = [], []
    for leg, (leg_start, leg_end) in LEGISLATURES.items():
        evs = sorted([e for e in events if e.get("idLegislatura") == leg and e.get("situacao")],
                     key=lambda e: e["dataHora"])
        periods, current = [], None
        ufs = set()
        for e in evs:
            ufs.add(e.get("siglaUf"))
            desc = (e.get("descricaoStatus") or "").strip()
            if e["situacao"] in ("Exercício", "CONVOCADO"):
                # So abre periodo um registro de entrada (posse, reassuncao, efetivacao) datado dentro da
                # legislatura. A API registra algumas reassuncoes de suplente com situacao 'CONVOCADO' e
                # descricao 'Entrada - Reassunção'. Registros administrativos (por exemplo 'Alteração de
                # partido' de suplente fora do exercicio, convocacoes, oficios anteriores a posse) nao abrem
                # nem fecham periodo.
                if current is None and day(e["dataHora"]) >= leg_start and ENTRY_RE.search(desc):
                    current = {"start": day(e["dataHora"]), "end": None,
                               "start_reason": (e.get("descricaoStatus") or "").strip() or None,
                               "end_reason": None,
                               "electoral_condition": e.get("condicaoEleitoral")}
            else:
                if current is not None:
                    current["end"] = day(e["dataHora"])
                    current["end_reason"] = (e.get("descricaoStatus") or "").strip() or None
                    periods.append(current)
                    current = None
        if current is not None:
            if leg_end < COLLECTED_ON:
                current["end"] = leg_end
                current["end_reason"] = "Término da legislatura (sem registro de saída no histórico da API)"
                issues.append(f"camara:{dep_id} leg {leg}: exercicio sem registro de saida")
            periods.append(current)
        clipped = []
        for p in periods:
            if p["end"] is not None and p["end"] < WINDOW_START:
                continue
            if p["start"] > COLLECTED_ON:
                continue
            if p["end"] is not None and p["end"] > COLLECTED_ON:
                p["end"], p["end_reason"] = None, None
            if p["start"] < WINDOW_START:
                p["start"] = WINDOW_START
                p["start_clipped_to_window"] = True
            clipped.append(p)
        if not clipped:
            continue
        ufs.discard(None)
        if len(ufs) != 1:
            issues.append(f"camara:{dep_id} leg {leg}: UFs {sorted(ufs)}")
        conds = {p["electoral_condition"] for p in clipped}
        terms.append({
            "legislature": leg,
            "legislature_start": leg_start,
            "legislature_end": leg_end,
            "uf": sorted(ufs)[0] if ufs else None,
            "kind": "titular" if clipped[0]["electoral_condition"] == "Titular" else "suplente",
            "electoral_conditions_seen": sorted(c for c in conds if c),
            "exercise": clipped,
            "source": hist_url,
        })
    return terms, issues


def build_parties(dep_id, events, terms):
    """Historico partidario datado a partir dos registros do historico (partido no momento de cada registro)."""
    hist_url = f"{API}/deputados/{dep_id}/historico"
    evs = sorted([e for e in events if e.get("situacao") and e.get("siglaPartido")
                  and e.get("idLegislatura") in LEGISLATURES], key=lambda e: e["dataHora"])
    segments = []
    for e in evs:
        party = e["siglaPartido"].strip()
        if segments and segments[-1]["party"] == party:
            continue
        if segments:
            segments[-1]["end"] = day(e["dataHora"])
        segments.append({"party": party, "start": day(e["dataHora"]), "end": None, "source": hist_url})
    last_end = None
    open_now = False
    for t in terms:
        for p in t["exercise"]:
            if p["end"] is None:
                open_now = True
            elif last_end is None or p["end"] > last_end:
                last_end = p["end"]
    if segments and not open_now:
        segments[-1]["end"] = last_end
    out = []
    for s in segments:
        if s["end"] is not None and s["end"] < WINDOW_START:
            continue
        if s["start"] > COLLECTED_ON:
            continue
        if s["start"] < WINDOW_START:
            s["start"] = WINDOW_START
        out.append(s)
    return out


def in_exercise_on(terms, d, end_of_day=True):
    """Estado no fim do dia D (convencao da conferencia): quem sai em D nao conta, quem entra em D conta.
    Com end_of_day=False, as duas pontas contam (datas inclusivas)."""
    for t in terms:
        for e in t["exercise"]:
            if e["start"] <= d and (e["end"] is None or (d < e["end"] if end_of_day else d <= e["end"])):
                return True
    return False


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
    all_ids, list_pages = [], []
    for leg in LEGISLATURES:
        ids, pages = list_ids(leg)
        all_ids.extend(ids)
        list_pages.extend(pages)
    ids = sorted(set(all_ids))
    print("ids:", len(ids), "paginas de lista:", len(list_pages), file=sys.stderr)

    def per_dep(dep_id):
        return dep_id, fetch_json(f"{API}/deputados/{dep_id}/historico"), fetch_json(f"{API}/deputados/{dep_id}")

    with concurrent.futures.ThreadPoolExecutor(MAX_WORKERS) as pool:
        raw = list(pool.map(per_dep, ids))

    photo_cache_path = os.path.join(WORK, "api", "camara_photo_head.json")
    photo_ok = {}
    if os.path.exists(photo_cache_path):
        photo_ok = json.load(open(photo_cache_path, encoding="utf-8"))

    persons, issues = [], []
    for dep_id, hist, detail in raw:
        events = hist.get("dados") or []
        terms, t_issues = build_terms(dep_id, events)
        issues.extend(t_issues)
        if not terms:
            continue
        info = detail.get("dados") or {}
        status = info.get("ultimoStatus") or {}
        name = (status.get("nome") or "").strip() or None
        if name is None:
            name = next((e.get("nome", "").strip() for e in sorted(events, key=lambda e: e["dataHora"], reverse=True)
                         if e.get("nome")), None)
        persons.append({
            "id": f"camara:{dep_id}",
            "name": name,
            "full_name": (info.get("nomeCivil") or "").strip() or None,
            "role": "Deputado federal",
            "terms": terms,
            "party_history": build_parties(dep_id, events, terms),
            "_photo": status.get("urlFoto"),
            "_detail_url": f"{API}/deputados/{dep_id}",
        })

    todo = [p["_photo"] for p in persons if p["_photo"] and p["_photo"] not in photo_ok]
    with concurrent.futures.ThreadPoolExecutor(MAX_WORKERS) as pool:
        for url, ok in zip(todo, pool.map(head_ok, todo)):
            photo_ok[url] = ok
    os.makedirs(os.path.dirname(photo_cache_path), exist_ok=True)
    json.dump(photo_ok, open(photo_cache_path, "w", encoding="utf-8"))

    for p in persons:
        url = p.pop("_photo")
        detail_url = p.pop("_detail_url")
        if url and photo_ok.get(url):
            p["photo"] = {"url": url, "license": PHOTO_SHORT, "author": "Câmara dos Deputados",
                          "terms_source": TERMS_URL, "source": detail_url}
        else:
            p["photo"] = None
            p["photo_null_reason"] = (f"URL de foto ausente em {detail_url}" if not url else
                                      f"URL informada pela API nao respondeu com imagem em {COLLECTED_ON}: {url}")

    by_uf = {uf: [] for uf in UFS}
    for p in persons:
        ufs = sorted({t["uf"] for t in p["terms"] if t["uf"]})
        if len(ufs) == 1:
            by_uf[ufs[0]].append(p)
        else:
            # Pessoa com mandatos por UFs diferentes: aparece em cada UF so com os mandatos daquela UF.
            for uf in ufs:
                q = dict(p)
                q["terms"] = [t for t in p["terms"] if t["uf"] == uf]
                by_uf[uf].append(q)
            issues.append(f"{p['id']} com mandatos em UFs diferentes: {ufs}")
    for uf in UFS:
        by_uf[uf].sort(key=lambda p: (min(e["start"] for t in p["terms"] for e in t["exercise"]), p["name"] or ""))

    days = month_starts()
    anomalies = []
    totals = {}
    for d in days:
        total = 0
        for uf in UFS:
            present = [p for p in by_uf[uf] if in_exercise_on(p["terms"], d)]
            n = len(present)
            total += n
            if n != SEATS[uf]:
                periods = [(p["name"], e) for p in by_uf[uf] for t in p["terms"] for e in t["exercise"]]
                item = {"uf": uf, "day": d, "in_exercise": n, "seats": SEATS[uf]}
                if n > SEATS[uf]:
                    item["cause"] = ("Transicao no mesmo dia: a API registra a saida de um deputado e a entrada "
                                     "de outro na mesma data (datas inclusivas)")
                    item["evidence"] = [{"name": nm, "start": e["start"], "end": e["end"],
                                         "start_reason": e["start_reason"], "end_reason": e["end_reason"]}
                                        for nm, e in periods if e["start"] == d or e["end"] == d]
                else:
                    exits = sorted([(e["end"], nm, e["end_reason"]) for nm, e in periods
                                    if e["end"] is not None and e["end"] < d])
                    entries = sorted([(e["start"], nm, e["start_reason"]) for nm, e in periods if e["start"] > d])
                    item["cause"] = "Vaga sem deputado em exercicio nesta data segundo o historico da API"
                    item["evidence"] = {
                        "last_exit_before": ({"name": exits[-1][1], "end": exits[-1][0],
                                              "end_reason": exits[-1][2]} if exits else None),
                        "next_entry_after": ({"name": entries[0][1], "start": entries[0][0],
                                              "start_reason": entries[0][2]} if entries else None),
                    }
                anomalies.append(item)
        totals[d] = total

    inclusive_anomalies = sum(1 for d in days for uf in UFS
                              if sum(1 for p in by_uf[uf] if in_exercise_on(p["terms"], d, False)) != SEATS[uf])

    seats_observed = {}
    for leg, (leg_start, _) in LEGISLATURES.items():
        seats_observed[str(leg)] = {uf: sum(1 for p in by_uf[uf] for t in p["terms"] if t["legislature"] == leg
                                            and t["exercise"][0]["start"] == leg_start
                                            and t["exercise"][0]["electoral_condition"] == "Titular")
                                    for uf in UFS}

    unique = {p["id"]: p for p in persons}
    all_terms = [t for p in persons for t in p["terms"]]
    counts = {
        "persons": len(unique),
        "terms": len(all_terms),
        "terms_by_legislature": {str(l): sum(1 for t in all_terms if t["legislature"] == l) for l in LEGISLATURES},
        "exercise_periods": sum(len(t["exercise"]) for t in all_terms),
        "persons_with_suplente_term": sum(1 for p in persons if any(t["kind"] == "suplente" for t in p["terms"])),
        "suplente_terms_by_legislature": {str(l): sum(1 for t in all_terms if t["legislature"] == l
                                                      and t["kind"] == "suplente") for l in LEGISLATURES},
        "persons_in_exercise_on_collection_day": sum(1 for p in persons if in_exercise_on(p["terms"], COLLECTED_ON)),
        "persons_without_photo": sum(1 for p in persons if p["photo"] is None),
        "by_uf": {uf: len(by_uf[uf]) for uf in UFS},
        "check_month_starts_sampled": len(days),
        "check_uf_days_not_equal_seats": len(anomalies),
        "check_days_total_not_513": sum(1 for d in days if totals[d] != 513),
        "check_uf_days_not_equal_seats_inclusive_dates": inclusive_anomalies,
    }
    out = {
        "dataset": "federal-deputies",
        "collected_on": COLLECTED_ON,
        "period": {"start": WINDOW_START, "end": COLLECTED_ON},
        "scope_note": (
            "Todos os deputados federais, titulares e suplentes, que exerceram o mandato nas legislaturas 56 "
            "(2019-02-01 a 2023-01-31) e 57 (2023-02-01 a 2027-01-31) entre " + WINDOW_START + " e " + COLLECTED_ON +
            ", agrupados pela UF do mandato. Os periodos de exercicio sao derivados do endpoint de historico da "
            "Camara: um periodo comeca no registro de entrada (descricaoStatus com 'Entrada', 'Efetivação' ou 'Torna-se "
            "titular', situacao 'Exercício' ou 'CONVOCADO') e termina no primeiro registro seguinte com situacao de "
            "saida (licenca, afastamento, suplencia, suspensao, vacancia, fim de mandato); 'start_reason' e "
            "'end_reason' sao o campo descricaoStatus desses registros. Datas sao o dia do registro (inclusivas); "
            "'end' null significa em exercicio na data da coleta. 'kind' e a condicao eleitoral no inicio do primeiro "
            "periodo da legislatura; 'electoral_condition' em cada periodo e a condicao no registro de entrada. "
            "Historico partidario: partido (siglaPartido) informado em cada registro do historico; cada trecho vai do "
            "primeiro registro com aquela sigla ate o registro com a sigla seguinte, e o ultimo trecho termina no fim "
            "do ultimo exercicio (partido registrado pela Camara durante o mandato, nao a filiacao fora dele). "
            "Nao inclui candidaturas nem resultados eleitorais."
        ),
        "sources": [
            {"name": "Câmara dos Deputados, Dados Abertos: deputados da legislatura 56 (paginado)",
             "url": f"{API}/deputados?idLegislatura=56&itens=100"},
            {"name": "Câmara dos Deputados, Dados Abertos: deputados da legislatura 57 (paginado)",
             "url": f"{API}/deputados?idLegislatura=57&itens=100"},
            {"name": "Câmara dos Deputados, Dados Abertos: historico de status por deputado",
             "url": f"{API}/deputados/{{id}}/historico"},
            {"name": "Câmara dos Deputados, Dados Abertos: dados cadastrais por deputado (nomeCivil, urlFoto)",
             "url": f"{API}/deputados/{{id}}"},
        ],
        "photo_license": PHOTO_LICENSE,
        "build_script": "pipelines/politicians/build_federal_deputies.py",
        "counts": counts,
        "checks": {
            "convention": ("Contagem no primeiro dia de cada mes, estado no fim do dia: quem sai na data nao conta, "
                           "quem entra na data conta."),
            "seats_used_for_check": SEATS,
            "seats_observed_on_first_day": seats_observed,
            "total_in_exercise_by_month_start": totals,
            "uf_days_not_equal_seats": anomalies,
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
