import csv, re, json
MES={'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}
def num(x):
    x=x.strip()
    if not x or x=='-' : return 0.0
    neg = x.startswith('(') or x.startswith('-') and len(x)>1
    x=x.strip('()').lstrip('-').strip()
    if x in ('','-'): return 0.0
    v=float(x.replace('.','').replace(',','.'))
    return -v if neg else v
def parse(f):
    rows=list(csv.reader(open(f,encoding='latin1'),delimiter=';'))
    hi=[i for i,r in enumerate(rows) if r and r[0].strip().upper() in ('ESTADOS','MUNICÍPIOS','UF','ESTADO')][0]
    h=rows[hi]
    cols=[]
    for j,c in enumerate(h):
        m=re.match(r'(\w+)/(\d\d)',c.strip())
        if m and m.group(1).lower() in MES: cols.append((j,2000+int(m.group(2)) if int(m.group(2))<90 else 1900+int(m.group(2)),MES[m.group(1).lower()]))
        elif c.strip(): cols.append((j,c.strip(),None))
    data={}; notes=[]
    for r in rows[hi+1:]:
        if len(r)>1 and re.fullmatch(r'[A-Z]{2}',r[1].strip()):
            data[r[1].strip()]={(y,m):num(r[j]) for j,y,m in cols if m and j<len(r)}
        elif any(x.strip() for x in r): notes.append(' | '.join(x.strip() for x in r if x.strip())[:300])
    return data, notes, [c for c in cols if not c[2]]
def annual(data,y):
    return {uf:sum(v for (yy,m),v in d.items() if yy==y) for uf,d in data.items()}
