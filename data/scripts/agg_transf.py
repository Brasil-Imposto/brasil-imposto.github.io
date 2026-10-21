import zipfile, csv, io, collections, json, sys, glob
year=sys.argv[1]
H=None
agg=collections.defaultdict(float)
nrows=0
for zp in sorted(glob.glob(f'transf/{year}??.zip')):
    z=zipfile.ZipFile(zp); n=z.namelist()[0]
    r=csv.reader(io.TextIOWrapper(z.open(n),encoding='latin1'),delimiter=';')
    h=next(r); ix={c:i for i,c in enumerate(h)}
    for row in r:
        nrows+=1
        v=float(row[ix['VALOR TRANSFERIDO']].replace('.','').replace(',','.')) if row[ix['VALOR TRANSFERIDO']] else 0.0
        key=(row[ix['UF']],row[ix['TIPO TRANSFERÊNCIA']],row[ix['TIPO FAVORECIDO']],row[ix['NOME UNIDADE GESTORA']],row[ix['CÓDIGO FUNÇÃO']],row[ix['AÇÃO']],row[ix['NOME AÇÃO']],row[ix['LINGUAGEM CIDADÃ']],row[ix['CÓDIGO MODALIDADE APLICAÇÃO DESPESA']], 'MUN' if row[ix['NOME MUNICÍPIO']] else 'NOMUN')
        agg[key]+=v
json.dump([list(k)+[v] for k,v in agg.items()],open(f'transf_agg_{year}.json','w'))
print('rows',nrows,'keys',len(agg),'total',round(sum(agg.values())/1e9,3))
