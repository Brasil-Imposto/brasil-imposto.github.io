"""Collect Senate 2026 office staff cost per senator from the Senado open data API.

Inputs (downloaded by curl into data/federal/raw-pay/senate/, gitignored):
  servidores.json        /api/v1/servidores/servidores (all servants, lotacao, situacao)
  rem-2026-MM.json       /api/v1/servidores/remuneracoes/2026/MM
  rec/<cod>.json         /api/v1/senadores/<cod>/recursos-utilizados?ano=2026
Output: data/federal/senate-2026.json (built by build_output at the end).
"""
import datetime as dt
import json
import subprocess
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/federal/raw-pay/senate"
API = "https://adm.senado.gov.br/adm-dadosabertos/api/v1"


def norm(text):
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z ]", "", text.lower()).strip()


def money(text):
    return float(text.replace(".", "").replace(",", ".")) if text else 0.0


def senators():
    data = json.loads((ROOT / "data/federal/raw-pay/senators-in-office.json").read_text())
    out = []
    for p in data["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]:
        ident = p["IdentificacaoParlamentar"]
        out.append({"code": ident["CodigoParlamentar"], "name": ident["NomeParlamentar"],
                    "full_name": ident["NomeCompletoParlamentar"], "uf": ident["UfParlamentar"], "raw": p})
    return out


def office_owner(lotacao_name):
    m = re.search(r"Senador[a]?\s+(.*)$", lotacao_name or "")
    return norm(m.group(1)) if m else None


def office_kind(sigla, name):
    if sigla.startswith("GS") and name.startswith("Gabinete"):
        return "gabinete"
    if sigla.startswith("E") and name.lower().startswith("escrit"):
        return "escritorio"
    return None


def map_offices(sens, servants):
    """sigla -> (senator code, kind, lotacao name).

    Gabinete: the lotacao name names the senator, or the senator's own row (vinculo PARLAMENTAR,
    matched on the full civil name) is lotado there. Escritorio de Apoio: sigla E + optional digit
    or A + the gabinete sigla suffix (GSARICK -> E1ARICK), or the lotacao name names the senator.
    """
    by_name = {norm(s["name"]): s["code"] for s in sens}
    by_full = {norm(s["full_name"]): s["code"] for s in sens}
    gab = {}
    names = {}
    for x in servants:
        l = x["lotacao"]
        if not l or not l["sigla"]:
            continue
        names[l["sigla"]] = l["nome"] or ""
        kind = office_kind(l["sigla"], l["nome"] or "")
        if kind == "gabinete":
            owner = office_owner(l["nome"])
            if owner in by_name:
                gab[l["sigla"]] = by_name[owner]
            elif x["vinculo"] == "PARLAMENTAR" and x["situacao"] == "ATIVO" and norm(x["nome"]) in by_full:
                gab[l["sigla"]] = by_full[norm(x["nome"])]
    lot = {sig: (code, "gabinete", names[sig]) for sig, code in gab.items()}
    suffix = {sig[2:]: code for sig, code in gab.items()}
    for sig, name in names.items():
        if office_kind(sig, name) != "escritorio":
            continue
        m = re.match(r"^E[0-9A]?(.+)$", sig)
        owner = office_owner(name)
        if m and m.group(1) in suffix:
            lot[sig] = (suffix[m.group(1)], "escritorio", name)
        elif owner in by_name:
            lot[sig] = (by_name[owner], "escritorio", name)
    return lot

GROSS = ["remuneracao_basica", "vantagens_pessoais", "funcao_comissionada", "gratificacao_natalina",
         "horas_extras", "outras_eventuais", "abono_permanencia", "reversao_teto_constitucional"]
INDEMNITY = ["diarias", "auxilios", "vantagens_indenizatorias"]
DEDUCTIONS = ["imposto_renda", "previdencia", "faltas"]
MONTHS = range(1, 13)


def office_costs(sens, servants, lot):
    """Monthly gross pay of office staff per senator, joined by servant NAME.

    The payroll's "sequencial" is not the servant list's "sequencial" (only 24 of 2,337 numeric
    matches in January carry the same name), so the join is by exact name. A payroll name is
    attributed to a senator only when every non-retired servant record with that name sits in
    that senator's offices; a name whose records point to two places is counted as ambiguous.
    """
    by_name = defaultdict(list)
    for x in servants:
        by_name[x["nome"]].append(x)
    owner = {}
    ambiguous = {}
    for name, recs in by_name.items():
        live = [r for r in recs if r["situacao"] != "APOSENTADO" and r["vinculo"] != "PARLAMENTAR"]
        targets = {lot[r["lotacao"]["sigla"]][0] if r["lotacao"] and r["lotacao"]["sigla"] in lot else None
                   for r in live}
        retired = any(r["situacao"] == "APOSENTADO" for r in recs)
        office_targets = {c for c in targets if c}
        if not office_targets:
            continue
        if len(targets) == 1 and not retired:
            owner[name] = office_targets.pop()
        else:
            for c in office_targets:
                ambiguous.setdefault(c, set()).add(name)
    gross = defaultdict(lambda: defaultdict(float))
    indem = defaultdict(float)
    amb_gross = defaultdict(float)
    people = defaultdict(set)
    published = []
    checked = 0
    for m in MONTHS:
        f = RAW / f"rem-2026-{m:02d}.json"
        if not f.exists():
            continue
        rows = json.loads(f.read_text())
        if not rows:
            continue
        published.append(m)
        for r in rows:
            g = sum(money(r[k]) for k in GROSS)
            net = g + sum(money(r[k]) for k in DEDUCTIONS)
            assert abs(net - money(r["remuneracao_liquida"])) < 0.011, (m, r["nome"])
            checked += 1
            c = owner.get(r["nome"])
            if c:
                gross[c][m] += g
                indem[c] += sum(money(r[k]) for k in INDEMNITY)
                people[c].add(r["nome"])
            else:
                for c2, names in ambiguous.items():
                    if r["nome"] in names:
                        amb_gross[c2] += g
    return {"gross": gross, "indemnity": indem, "ambiguous": ambiguous, "ambiguous_gross": amb_gross,
            "people": people, "published": published, "rows_checked": checked}


def exercise_intervals(raw):
    ex = raw["Mandato"].get("Exercicios", {}).get("Exercicio", [])
    ex = ex if isinstance(ex, list) else [ex]
    return sorted((e["DataInicio"], e.get("DataFim")) for e in ex)



READ_ON = "2026-10-21"
NORM_APR = "https://adm.senado.gov.br/normas/ui/pub/normaConsultada?0=&idNorma=14383699"
ANNEX_APR = "https://www.senado.leg.br/transparencia/SECRH/BASF/Anexo/A_01_2025_1761064.PDF"
NORM_ATC2 = "https://adm.senado.gov.br/normas/ui/pub/normaConsultada?idNorma=14380751"
APS5 = "https://www12.senado.leg.br/transparencia/leg/pdf/normas/APS-5-2014-compilado.pdf"
OLD_TABLE = "https://www12.senado.leg.br/transparencia/leg/pdf/CotaExercicioAtivParlamSenadores.pdf"
GUIDE = "https://www12.senado.leg.br/publicacoes/guias/parl_guia_old/gestao-administrativa/gabinete-parlamentar/composicao"
DECREE = "https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2006/decreto/d5978.htm"
REM_URL = API + "/servidores/remuneracoes/2026/{m}"
SERV_URL = API + "/servidores/servidores"
REC_URL = API + "/senadores/{c}/recursos-utilizados?ano=2026"
SEN_URL = "https://legis.senado.leg.br/dadosabertos/senador/lista/atual"
CEAPS_CSV = ROOT / "data/federal/raw/senado-ceaps-2026.csv"
UF_BY_STATE = {"acre": "AC", "alagoas": "AL", "amapa": "AP", "amazonas": "AM", "bahia": "BA", "ceara": "CE",
               "distrito federal": "DF", "espirito santo": "ES", "goias": "GO", "maranhao": "MA",
               "mato grosso": "MT", "mato grosso do sul": "MS", "minas gerais": "MG", "para": "PA",
               "paraiba": "PB", "parana": "PR", "pernambuco": "PE", "piaui": "PI", "rio de janeiro": "RJ",
               "rio grande do norte": "RN", "rio grande do sul": "RS", "rondonia": "RO", "roraima": "RR",
               "santa catarina": "SC", "sao paulo": "SP", "sergipe": "SE", "tocantins": "TO"}
MONTH_PT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def fetch(url, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-sS", "-L", "--compressed", "-A", "Mozilla/5.0", url, "-o", str(path)], check=True)
    return path


def ceaps_by_uf():
    text = subprocess.run(["pdftotext", "-layout", str(fetch(ANNEX_APR, RAW / "apr-8-2025-anexo.pdf")), "-"],
                          capture_output=True, text=True, check=True).stdout
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\s*([A-Za-zÀ-ú ]+?)\s{2,}([\d.]+,\d{2})\s*$", line)
        if m and norm(m.group(1)) in UF_BY_STATE:
            out[UF_BY_STATE[norm(m.group(1))]] = money(m.group(2))
    assert len(out) == 27, len(out)
    return dict(sorted(out.items()))


def full_months(intervals, year=2026):
    days = set()
    for start, end in intervals:
        a = dt.date.fromisoformat(start)
        b = dt.date.fromisoformat(end) if end else dt.date(year, 12, 31)
        d = max(a, dt.date(year, 1, 1))
        while d <= min(b, dt.date(year, 12, 31)):
            days.add(d)
            d += dt.timedelta(days=1)
    out = []
    for m in MONTHS:
        first = dt.date(year, m, 1)
        nxt = dt.date(year + (m == 12), m % 12 + 1, 1)
        if all(first + dt.timedelta(days=i) in days for i in range((nxt - first).days)):
            out.append(m)
    return out


def months_label(months):
    if not months:
        return None
    runs, cur = [], [months[0]]
    for m in months[1:]:
        if m == cur[-1] + 1:
            cur.append(m)
        else:
            runs.append(cur)
            cur = [m]
    runs.append(cur)
    parts = [MONTH_PT[r[0] - 1] if len(r) == 1 else f"{MONTH_PT[r[0] - 1]} a {MONTH_PT[r[-1] - 1]}" for r in runs]
    return ", ".join(parts) + " 2026"


def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def ceaps_lines():
    import csv
    with open(CEAPS_CSV, encoding="latin-1") as f:
        rows = list(csv.reader(f, delimiter=";"))[2:]
    out = Counter(norm(r[2]) for r in rows)
    return out


def build():
    sens = senators()
    fetch(SERV_URL, RAW / "servidores.json")
    for m in range(1, 10):
        fetch(REM_URL.format(m=m), RAW / f"rem-2026-{m:02d}.json")
    servants = json.loads((RAW / "servidores.json").read_text())
    lot = map_offices(sens, servants)
    assert len({c for c, _, _ in lot.values()}) == len(sens) == 81
    costs = office_costs(sens, servants, lot)
    published = costs["published"]
    lines = ceaps_lines()
    people = []
    staff_over_50 = []
    for s in sens:
        rec = json.loads(fetch(REC_URL.format(c=s["code"]), RAW / "rec" / f"{s['code']}.json").read_text())["data"][0]
        pessoal = rec.get("pessoal", [])
        staff = sum(p["quantidade"] for p in pessoal)
        comis = sum(v["quantidade"] for p in pessoal for v in p.get("vinculos", []) if v["vinculo"] == "Comissionado")
        if comis > 50:
            staff_over_50.append(f"{s['name']} ({comis})")
        intervals = exercise_intervals(s["raw"])
        current = [a for a, b in intervals if b is None]
        since = max(current) if current else None
        counted = [m for m in full_months(intervals) if m in published]
        skipped = [m for m in published if m not in counted]
        g = costs["gross"][s["code"]]
        by_month = {str(m): round(g[m], 2) for m in counted}
        total = round(sum(g[m] for m in counted), 2) if counted else None
        monthly = round(total / len(counted), 2) if counted else None
        amb = len(costs["ambiguous"].get(s["code"], ()))
        method = ("Soma, por mes, da remuneracao bruta paga aos servidores lotados no Gabinete e nos Escritorios de "
                  "Apoio do senador (remuneracao basica, vantagens pessoais, funcao comissionada, gratificacao "
                  "natalina, horas extras, outras eventuais, abono de permanencia, menos a reversao do teto), de "
                  "todas as folhas do mes (Normal e Suplementar). Fora do total: diarias, auxilios, vantagens "
                  "indenizatorias e encargos patronais (nao publicados). Lotacao tirada da lista atual de servidores "
                  "(/servidores/servidores; desligados mantem a ultima lotacao) e ligada a folha pelo nome exato, pois o "
                  "'sequencial' da folha nao e o da lista. Exclui o proprio senador (vinculo PARLAMENTAR). Conta so os "
                  "meses publicados em que o senador esteve em exercicio o mes inteiro. Servidor que mudou de unidade "
                  "durante 2026 fica inteiro na lotacao atual.")
        notes = []
        if skipped:
            notes.append("Meses publicados fora da conta por exercicio incompleto ou ausente: "
                         + ", ".join(MONTH_PT[m - 1] for m in skipped) + ".")
        if amb:
            notes.append(f"{amb} nome(s) da equipe ficaram fora por ambiguidade (homonimo, ou registro de "
                         "aposentado com o mesmo nome).")
        if counted:
            notes.append("Auxilios, diarias e indenizacoes da equipe, fora do total: "
                         + brl(costs["indemnity"][s["code"]]) + " no ano (jan a set, todos os meses).")
        notes.append(f"Equipe atual pelo Senado (recursos-utilizados): {staff} pessoas, {comis} comissionadas.")
        if lines[norm(s["name"])] == 0:
            notes.append("Sem nenhuma linha no arquivo CEAPS 2026 (atualizado em 02/10/2026, meses 1 a 9); "
                         "recursos-utilizados 2026 tambem mostra cota total 0.")
        role = s["raw"]["Mandato"].get("DescricaoParticipacao")
        tit = s["raw"]["Mandato"].get("Titular")
        if tit:
            notes.append(f"{role} de {tit['NomeParlamentar']}; exercicio atual desde {since}.")
        elif since and since >= "2025-01-01":
            notes.append(f"Titular; exercicio atual desde {since}.")
        office = {"uses": staff > 0 if pessoal else None, "monthly": monthly, "year_total": total,
                  "months": months_label(counted), "staff_count": staff if pessoal else None,
                  "by_month": by_month, "method": method,
                  "source": REM_URL.format(m="{mes}")}
        if not counted:
            office["by_month"] = {}
            notes.insert(0, "Nenhum mes publicado (jan a set 2026) com o senador em exercicio o mes inteiro, entao "
                            "nao ha custo de gabinete 2026 atribuivel a ele ainda.")
        people.append({"id": f"senado:{s['code']}", "name": s["name"],
                       "office": office,
                       "passport": {"uses": None, "source": DECREE,
                                    "note": "Direito previsto no Decreto 5.978/2006, Anexo, art. 6, IX (membros do "
                                            "Congresso Nacional). Nenhuma lista oficial de titulares de passaporte "
                                            "diplomatico publicada pelo Senado ou pelo Itamaraty foi encontrada."},
                       "exercise_since": since, "note": " ".join(notes)})
    return sens, people, costs, staff_over_50


def output(people, costs, staff_over_50):
    by_uf = ceaps_by_uf()
    return {
        "collected_on": READ_ON,
        "sources": [
            {"name": "Senado, dados abertos administrativos: remuneracoes dos servidores 2026 (meses 1 a 9)", "url": REM_URL.format(m="{mes}"), "read_on": READ_ON},
            {"name": "Senado, dados abertos administrativos: lista de servidores com lotacao", "url": SERV_URL, "read_on": READ_ON},
            {"name": "Senado, dados abertos administrativos: recursos utilizados por senador 2026 (pessoal, cotas)", "url": REC_URL.format(c="{codigoParlamentar}"), "read_on": READ_ON},
            {"name": "Senado, dados abertos legislativos: senadores em exercicio, mandatos e exercicios", "url": SEN_URL, "read_on": READ_ON},
            {"name": "Ato do Presidente do Senado n 8, de 2025 (valores da CEAPS), pagina da norma", "url": NORM_APR, "read_on": READ_ON},
            {"name": "Anexo ao Ato do Presidente n 8, de 2025 (tabela CEAPS por UF)", "url": ANNEX_APR, "read_on": READ_ON},
            {"name": "Ato da Comissao Diretora n 2, de 2023 (reajustes e 4 trechos aereos por mes)", "url": NORM_ATC2, "read_on": READ_ON},
            {"name": "Ato do Primeiro-Secretario n 5, de 2014, compilado (regras da CEAPS)", "url": APS5, "read_on": READ_ON},
            {"name": "Tabela antiga da CEAPS (PDF de 19/06/2017)", "url": OLD_TABLE, "read_on": READ_ON},
            {"name": "Guia do Parlamentar (versao antiga): composicao do gabinete", "url": GUIDE, "read_on": READ_ON},
            {"name": "Decreto 5.978/2006, Regulamento de Documentos de Viagem", "url": DECREE, "read_on": READ_ON},
        ],
        "ceaps_rules": {
            "act": "Ato do Presidente do Senado Federal n 8, de 28/02/2025, ad referendum da Comissao Diretora, "
                   "publicado no Boletim Administrativo do Senado Federal n 9678, secao 1, de 28/02/2025, p. 2; em "
                   "vigor desde 01/03/2025. Reajusta os valores do Anexo do Ato da Comissao Diretora n 2, de 2023. "
                   "Nenhum ato posterior que altere esse anexo aparece no sistema de normas do Senado (consulta de "
                   "2026-10-21).",
            "act_url": NORM_APR,
            "carries_over": True,
            "explanation": "Os valores de R$ 21.045,20 (DF) a R$ 44.276,60 (AM) vem de uma tabela de 2017, superada. "
                           "O Ato da Comissao Diretora n 2/2023 reajustou a CEAPS (6% em 2023, 6% em 2024, 6,13% em "
                           "2025) e criou, fora da CEAPS, 4 trechos aereos ida e volta por mes ate o DF (o saldo de "
                           "trechos passa para os meses seguintes, nunca para o ano seguinte); o Ato do Presidente n "
                           "8/2025 fixou os valores atuais, de R$ 36.582,46 (DF) a R$ 52.798,82 (AM), em vigor desde "
                           "01/03/2025. Pelo Ato do Primeiro-Secretario n 5/2014, art. 5, par. 5 a 7, o valor mensal "
                           "nao usado pode ser remanejado para os meses seguintes dentro do mesmo exercicio, nunca "
                           "para o exercicio seguinte, e pode pagar despesas de meses anteriores ao pedido; por isso "
                           "um mes isolado pode passar do valor mensal. Com os valores de 2025, nenhum dos 81 "
                           "senadores passou de 9 vezes o valor mensal de jan a set 2026 (maior: 8,99 vezes); Damares "
                           "Alves (R$ 301.972,81) e Izalci Lucas (R$ 313.534,64) ficam abaixo de 9 x R$ 36.582,46 = "
                           "R$ 329.242,14. carries_over = true vale so dentro do mesmo ano.",
            "monthly_by_uf": by_uf,
        },
        "office_rules": {
            "limit_note": "Pagina do Guia do Parlamentar marcada como versao antiga (sem data): em regra o gabinete "
                          "tem 5 Assessor Parlamentar (SF02), 6 Secretario Parlamentar (SF01) e 1 Motorista (AP04) "
                          "comissionados, mais funcoes para efetivos (1 Chefe de Gabinete FC-3, 1 Subchefe FC-2, 4 "
                          "Assistente Tecnico FC-1); os cargos SF02 podem ser desmembrados em cargos menores desde "
                          "que a soma nao passe da 'verba permitida ao Gabinete Parlamentar' (valor em reais nao "
                          "publicado na pagina); maximo de 50 comissionados por gabinete. A contagem atual do Senado "
                          "contradiz esse teto em: " + (", ".join(staff_over_50) or "nenhum") + " (comissionados de "
                          "Gabinete mais Escritorios de Apoio), entao o teto da pagina pode estar desatualizado ou "
                          "valer por unidade. O texto vigente do Regulamento Administrativo nao foi lido.",
            "source": GUIDE,
        },
        "people": people,
        "not_found": [
            {"what": "Valor em reais da verba de gabinete (limite de dinheiro por gabinete de senador)",
             "why": "A pagina oficial encontrada cita a 'verba permitida ao Gabinete Parlamentar' sem valor e e marcada como versao antiga; o OpenAPI do adm-dadosabertos nao tem endpoint de limite por gabinete.",
             "tried": [GUIDE, "https://adm.senado.gov.br/adm-dadosabertos/v3/api-docs"]},
            {"what": "Lista oficial de senadores com passaporte diplomatico",
             "why": "O Decreto 5.978/2006 da o direito aos membros do Congresso, mas nem o Senado nem o Itamaraty publicam lista de titulares; noticias citam listas obtidas so por pedido via Lei de Acesso a Informacao. O OpenAPI do Senado nao tem endpoint de passaporte.",
             "tried": [DECREE, "https://adm.senado.gov.br/adm-dadosabertos/v3/api-docs", "busca web: Itamaraty lista passaportes diplomaticos concedidos parlamentares"]},
            {"what": "Custo de gabinete 2026 de quem nao teve mes inteiro de exercicio entre jan e set 2026",
             "why": "A folha publicada vai de jan a set 2026; a lotacao e um retrato atual, entao meses fora do exercicio pagariam a equipe do antecessor.",
             "tried": [REM_URL.format(m=10)]},
            {"what": "Encargos patronais (previdencia patronal) da equipe de gabinete",
             "why": "A folha aberta publica so os valores do servidor (bruto, descontos, indenizacoes), nao a contribuicao do Senado.",
             "tried": [REM_URL.format(m="{mes}")]},
        ],
    }


if __name__ == "__main__":
    sens, people, costs, over50 = build()
    data = output(people, costs, over50)
    out = ROOT / "data/federal/senate-2026.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    n_cost = sum(1 for p in people if p["office"]["monthly"] is not None)
    print("payroll rows checked:", costs["rows_checked"], "months:", costs["published"])
    print("office cost:", n_cost, "of", len(people), "| staff counts:", sum(1 for p in people if p["office"]["staff_count"] is not None))
    print("no cost:", [p["name"] for p in people if p["office"]["monthly"] is None])
    print("partial months:", [(p["name"], p["office"]["months"]) for p in people if p["office"]["months"] not in (None, "jan a set 2026")])
    print("over 50:", over50)
    print("wrote", out)
