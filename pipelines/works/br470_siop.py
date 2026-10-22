"""Execução orçamentária anual da ação da duplicação da BR-470/SC no SIOP (dados abertos do orçamento
federal, endpoint SPARQL público, sem login).

Endpoint: https://www1.siop.planejamento.gov.br/sparql/  (grafos http://orcamento.dados.gov.br/AAAA/)
Filtro: ações cujo rótulo contém "BR-470" e "Navegantes" (em 2024: ação 7530, "Adequação de Trecho
Rodoviário - Navegantes - Rio do Sul - na BR-470/SC").
Limite: `valorPago` é o pago no próprio exercício; restos a pagar pagos nos anos seguintes NÃO entram
(o vocabulário do SIOP não traz esse campo).
Uso: python3 br470_siop.py <out.json> [ano_ini] [ano_fim]
"""
import json, subprocess, sys, time, urllib.parse

EP = 'https://www1.siop.planejamento.gov.br/sparql/'
Q = '''PREFIX loa: <http://vocab.e.gov.br/2013/09/loa#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?acao ?acaoL ?sub ?subL (SUM(?pago) AS ?pagoT) (SUM(?liq) AS ?liqT) (SUM(?emp) AS ?empT) (SUM(?dot) AS ?dotT) (SUM(?lmc) AS ?lmcT)
FROM <http://orcamento.dados.gov.br/{y}/>
WHERE {{
 ?i loa:temAcao ?acao . ?acao rdfs:label ?acaoL .
 ?i loa:temSubtitulo ?sub . ?sub rdfs:label ?subL .
 FILTER(CONTAINS(?acaoL, "BR-470") && CONTAINS(?acaoL, "Navegantes"))
 OPTIONAL {{ ?i loa:valorPago ?pago }} OPTIONAL {{ ?i loa:valorLiquidado ?liq }}
 OPTIONAL {{ ?i loa:valorEmpenhado ?emp }} OPTIONAL {{ ?i loa:valorDotacaoInicial ?dot }}
 OPTIONAL {{ ?i loa:valorLeiMaisCredito ?lmc }}
}} GROUP BY ?acao ?acaoL ?sub ?subL'''


def run(y):
    url = EP + '?' + urllib.parse.urlencode({'query': Q.format(y=y), 'format': 'application/sparql-results+json'})
    for attempt in range(3):
        r = subprocess.run(['curl', '-sS', '-m', '200', '-A', 'Mozilla/5.0', url], capture_output=True, text=True)
        try:
            return url, json.loads(r.stdout)['results']['bindings']
        except Exception:  # noqa: BLE001
            time.sleep(10)
    return url, None


def main(out, y0=2010, y1=2026):
    res = {'endpoint': EP, 'note': 'valorPago = pago no exercício; restos a pagar pagos em anos seguintes não incluídos.', 'years': []}
    for y in range(int(y0), int(y1) + 1):
        url, rows = run(y)
        entry = {'year': y, 'query_url': url, 'rows': []}
        for b in rows or []:
            entry['rows'].append({k: b[k]['value'] for k in b})
        entry['status'] = 'ok' if rows is not None else 'erro'
        res['years'].append(entry)
        print(y, entry['status'], [(r['acaoL'][:60], r.get('pagoT')) for r in entry['rows']], flush=True)
    json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main(*sys.argv[1:])
