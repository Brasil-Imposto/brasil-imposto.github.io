import zipfile, csv, io, collections, json, glob, sys
year=sys.argv[1]
agg=collections.defaultdict(lambda:[0.0,0.0,0.0])
n=0
def f(x): return float(x.replace('.','').replace(',','.')) if x else 0.0
for zp in sorted(glob.glob(f'desp/{year}??.zip')):
    z=zipfile.ZipFile(zp)
    r=csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]),encoding='latin1'),delimiter=';')
    h=next(r); ix={c:i for i,c in enumerate(h)}
    for row in r:
        n+=1
        key=(row[ix['UF']],row[ix['Código Órgão Superior']],row[ix['Nome Órgão Superior']][:60],row[ix['Código Grupo de Despesa']],row[ix['Código Modalidade da Despesa']],row[ix['Código Função']],row[ix['Código Ação']],row[ix['Nome Ação']][:90],row[ix['Nome Localizador']][-30:] if False else row[ix['Código Localizador']])
        a=agg[key]
        a[0]+=f(row[ix['Valor Pago (R$)']]); a[1]+=f(row[ix['Valor Restos a Pagar Pagos (R$)']]); a[2]+=f(row[ix['Valor Liquidado (R$)']])
json.dump([list(k)+v for k,v in agg.items()],open(f'desp_agg_{year}.json','w'))
print('rows',n,'keys',len(agg),'pago %.1f bn'%(sum(v[0] for v in agg.values())/1e9),'rp pagos %.1f bn'%(sum(v[1] for v in agg.values())/1e9))
