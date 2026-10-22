import csv, re, json
rows=list(csv.reader(open('arrecadacao-estado.csv',encoding='latin1'),delimiter=';'))
h=rows[0]
def f(x):
    x=x.strip()
    if not x: return 0.0
    if re.fullmatch(r'-?\d{1,3}(\.\d{3})+(,\d+)?',x): x=x.replace('.','')
    return float(x.replace(',','.'))
def agg(y):
    out={}
    for r in rows[1:]:
        if r[0]!=y: continue
        d=out.setdefault(r[2],{c:0.0 for c in h[3:]})
        for c,x in zip(h[3:],r[3:]): d[c]+=f(x)
    return out
if __name__=='__main__':
    for y in ['2024','2025']:
        a=agg(y)
        tot=sum(sum(v.values()) for v in a.values())
        outros=sum(v['ADMINISTRADAS POR OUTROS ÓRGÃOS'] for v in a.values())
        prev=sum(v['RECEITA PREVIDENCIÁRIA'] for v in a.values())
        print(y,'UFs',len(a),'total',round(tot,2),'outros orgaos',round(outros,2),'RFB',round(tot-outros,2),'prev',round(prev,2))
        top=sorted(((k,sum(v.values())) for k,v in a.items()),key=lambda t:-t[1])
        print([ (k,round(s/1e9,1)) for k,s in top])
