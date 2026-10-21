"""Stream one month of the INSS "Beneficios emitidos" microdata and total the net value by UF and by municipality of residence.

Usage: curl -s <zip url> | tar -xOf - | python3 inss_emitidos_municipio.py <out.json> [UF name filter, e.g. "Santa Catarina"]
Source: INSS open data (CKAN https://dadosabertos.inss.gov.br/, dataset beneficios-emitidos-plano-de-dados-abertos-jun-2023-a-jun-2025),
files on S3 without login, 0.55 to 1 GB zipped per month. Nothing is written to disk except the small output JSON.
Columns: Especie;Despacho;Sexo;Clientela;Tipo Beneficio;UF;Meio pagamento;Banco;Mun Pagto;Mun Resid;Vl Liquido;Ramo Atividade;Dt inicio validade
Mun Resid is "<5-digit INSS code>-<uf>-<name truncated to 20 chars>"; Vl Liquido is the NET value (after deductions).
"""
import collections, io, json, sys

out, uf_filter = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else None)
f = io.TextIOWrapper(sys.stdin.buffer, encoding="latin1", newline="")
h = [c.strip() for c in f.readline().rstrip("\r\n").split(";")]
iu, imr, iv, ies = h.index("UF"), h.index("Mun Resid"), h.index("Vl Líquido"), h.index("Espécie")
by_uf, by_mun, by_esp, n, bad = collections.defaultdict(float), collections.defaultdict(float), collections.defaultdict(float), 0, 0
cnt_uf = collections.Counter()
for line in f:
    p = line.rstrip("\r\n").split(";")
    if len(p) < len(h): bad += 1; continue
    try: v = float(p[iv].strip().replace(".", "").replace(",", "."))
    except ValueError: bad += 1; continue
    uf = p[iu].strip(); n += 1
    by_uf[uf] += v; cnt_uf[uf] += 1
    if uf_filter is None or uf == uf_filter:
        by_mun[p[imr].strip()] += v
        by_esp[p[ies].strip()] += v
json.dump({"rows": n, "bad_rows": bad, "by_uf": by_uf, "count_by_uf": cnt_uf, "by_municipality_of_residence": by_mun, "by_species_filtered": by_esp},
          open(out, "w"), ensure_ascii=False, indent=0)
print("rows", n, "bad", bad, "total_bi", round(sum(by_uf.values()) / 1e9, 3), "filtered_bi", round(sum(by_mun.values()) / 1e9, 4))
