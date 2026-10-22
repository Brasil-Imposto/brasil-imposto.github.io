# Sums the Fundo Constitucional do DF (UO 73901) in 2024: amount paid + unpaid commitments of earlier years paid (restos a pagar pagos).
# Input: desp/2024MM.zip. Output: fcdf_2024.json
import zipfile, csv, io, collections, glob, json
agg=collections.defaultdict(float)
def f(x): return float(x.replace('.','').replace(',','.')) if x else 0.0
for zp in sorted(glob.glob('desp/2024??.zip')):
    z=zipfile.ZipFile(zp)
    r=csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]),encoding='latin1'),delimiter=';')
    h=next(r); ix={c:i for i,c in enumerate(h)}
    for row in r:
        if 'CONSTITUCIONAL DO DISTRITO' in row[ix['Nome Unidade Orçamentária']].upper() or 'FCDF' in row[ix['Nome Unidade Orçamentária']].upper():
            agg[(row[ix['Código Unidade Orçamentária']],row[ix['Nome Unidade Orçamentária']],row[ix['UF']],row[ix['Código Grupo de Despesa']],row[ix['Código Modalidade da Despesa']])]+=f(row[ix['Valor Pago (R$)']])+f(row[ix['Valor Restos a Pagar Pagos (R$)']])
for k,v in sorted(agg.items(),key=lambda t:-t[1]): print(k,round(v,2))
print('TOTAL', round(sum(agg.values()),2))
json.dump({'|'.join(k):v for k,v in agg.items()},open('fcdf_2024.json','w'))
