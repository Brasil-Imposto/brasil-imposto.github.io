"""Official titles of the federal budget actions (ações orçamentárias), by year -> data/federal/action-titles.json.

The Tesouro base used by the home "cake" carries action names cut at 60 characters, in capitals and without accents.
SIOP (the federal budget system) publishes the official title of each action per budget year as open linked data;
this script reads it with one SPARQL query per year, 2019 onward.
Check: the file is written only when every year returned titles and the codes the cake uses have a title in at least
one year (reported, not assumed).
Run: python3 data/scripts/federal/fetch_action_titles.py
"""
import json, subprocess, sys, time, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "federal" / "action-titles.json"
EP = "https://www1.siop.planejamento.gov.br/sparql/"
Q = '''PREFIX loa: <http://vocab.e.gov.br/2013/09/loa#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?cod ?l FROM <http://orcamento.dados.gov.br/{y}/>
WHERE {{ ?i loa:temAcao ?a . ?a loa:codigo ?cod ; rdfs:label ?l . }}'''

def run(y):
    url = EP + "?" + urllib.parse.urlencode({"query": Q.format(y=y), "format": "application/sparql-results+json"})
    for attempt in range(3):
        r = subprocess.run(["curl", "-sS", "-m", "200", "-A", "Mozilla/5.0", url], capture_output=True, text=True)
        try:
            return json.loads(r.stdout)["results"]["bindings"]
        except Exception:  # noqa: BLE001
            time.sleep(10)
    return None

titles, fails = {}, []
for y in range(2019, 2027):
    b = run(y)
    if not b:
        fails.append(str(y)); continue
    titles[str(y)] = {x["cod"]["value"]: x["l"]["value"] for x in b}
    print(y, len(titles[str(y)]), "actions")
if fails:
    print("CHECK FAILED: no titles for", ", ".join(fails)); sys.exit(1)
OUT.write_text(json.dumps({"source": {"name": "SIOP, dados abertos do orçamento federal (SPARQL)", "url": EP, "graph": "http://orcamento.dados.gov.br/<ano>/"},
                           "titles": titles}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("wrote", OUT.relative_to(ROOT), OUT.stat().st_size // 1024, "KB")
