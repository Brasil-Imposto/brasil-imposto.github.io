"""Primary result of the whole public sector (Union, states, municipalities and state companies), monthly, Banco Central.

Usage: python3 pipelines/series/fetch_public_sector_primary.py [--control]
Source: Banco Central do Brasil, SGS 4649 (NFSP sem desvalorização cambial, fluxo mensal corrente, resultado primário,
setor público consolidado) and SGS 4639 (the same for Governo Federal e Banco Central), read through the SGS web service
(www3.bcb.gov.br/wssgs; on 2026-10-03 api.bcb.gov.br served a certificate for another host). NFSP is the need for
financing, so the sign is flipped: positive = surplus (sobrou), negative = deficit.
Check: the federal series (4639) must equal, month by month, the "abaixo da linha" line already in data/series/union.json
(Tesouro RTN, Tabela 1.1, line 8, which reproduces the Banco Central), within half of the SGS precision: SGS publishes
R$ milhões with two decimals (R$ 10 mil). On 2026-10-03, 90 of 92 months agreed within half a unit (R$ 5 mil) and two
(2023-10, 2024-04) by R$ 5,9 mil, so the tolerance is one published unit (R$ 10 mil); against values of tens of billions
this proves it is the same series. --control moves one month by two units (R$ 20 mil) and must fail.
Nothing is written when the check fails.
Output: data/series/public-sector-primary.json
"""
import html, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
CONTROL = "--control" in sys.argv
URL = "https://www3.bcb.gov.br/wssgs/services/FachadaWSSGS"
body = """<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pub="http://publico.ws.casosdeuso.sgs.pec.bcb.gov.br"><soapenv:Body><pub:getValoresSeriesXML><codigosSeries><item>4649</item><item>4639</item></codigosSeries><dataInicio>01/01/2019</dataInicio><dataFim>31/12/2026</dataFim></pub:getValoresSeriesXML></soapenv:Body></soapenv:Envelope>"""
raw = subprocess.run(["curl", "-sS", "-m", "120", "-H", "Content-Type: text/xml; charset=utf-8", "-H", "SOAPAction: getValoresSeriesXML",
                      "--data-binary", "@-", URL], input=body, capture_output=True, text=True, check=True).stdout
t = html.unescape(raw)
series = {}
for sid, b in re.findall(r"<SERIE ID='(\d+)'>(.*?)</SERIE>", t, re.S):
    series[sid] = {f"{y}-{int(m):02d}": round(-float(v.replace(",", ".")) * 1e6, 2)
                   for m, y, v in re.findall(r"<DATA>(\d+)/(\d+)</DATA>\s*<VALOR>([^<]*)</VALOR>", b)}
u = json.load(open(P("data/series/union.json")))
months = [m for m in u["months"] if m in series["4639"]]
fed = dict(series["4639"])
if CONTROL:
    fed[months[-1]] = round(fed[months[-1]] + 20000, 2)
c = lambda v: int(round(v * 100))
diff = {m: c(fed[m]) - c(u["primary_result_below_line"][u["months"].index(m)]) for m in months}
bad = {m: d for m, d in diff.items() if abs(d) > 1000000}
check = {"federal_4639_vs_union_below_line_months": len(months), "max_abs_difference_brl": max(abs(d) for d in diff.values()) / 100,
         "months_off_by_more_than_one_published_unit": bad, "passed": not bad, "control_run": CONTROL}
print(json.dumps(check, indent=1))
if not check["passed"]:
    raise SystemExit("CHECK FAILED")
if not CONTROL:
    ms = sorted(series["4649"])
    json.dump({"title": "Primary result of the consolidated public sector (Union, states, municipalities, state companies), monthly",
               "unit": "BRL (reais correntes)", "sign": "positive = surplus (sobrou dinheiro antes dos juros); negative = deficit",
               "months": ms, "primary_result": [series["4649"][m] for m in ms],
               "federal_primary_result_bcb": [series["4639"].get(m) for m in ms],
               "source": {"body": "Banco Central do Brasil", "series": "SGS 4649 (setor público consolidado) e SGS 4639 (Governo Federal e Banco Central), NFSP sem desvalorização cambial, fluxo mensal corrente, resultado primário",
                          "url": "https://www3.bcb.gov.br/sgspub/", "service": URL},
               "check": check, "collected_at": "2026-10-03"},
              open(P("data/series/public-sector-primary.json"), "w"), ensure_ascii=False)
