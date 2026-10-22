# Reconciliation: the sum of the 27 UFs (arrecadacao-estado.csv) against the national historical series, 2024 and 2025.
# Inputs: arrecadacao-estado.csv, serie-1994-2025.xlsx. Outputs: recon.json, tableRecon.md. Needs openpyxl.
import sys, os, json, openpyxl
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from parse_rfb import agg, h
from taxmap import TAXMAP, NATMAP
wb=openpyxl.load_workbook('serie-1994-2025.xlsx',data_only=True)
used=set(c for v in TAXMAP.values() for c in v)
if not (used==set(h[3:])):
    raise SystemExit(set(h[3:])-used)
out={}
for y in ['2024','2025']:
    nat={row[0]:row[-1] for row in wb[y].iter_rows(values_only=True) if row[0]}
    a=agg(y); rec=[]
    for k,cols in TAXMAP.items():
        uf=sum(v[c] for v in a.values() for c in cols); n=nat[NATMAP[k]]*1e6
        rec.append((k,uf,n,uf-n))
    tu=sum(sum(v.values()) for v in a.values()); tn=nat[NATMAP['TOTAL']]*1e6
    rec.append(('TOTAL',tu,tn,tu-tn)); out[y]=rec
    print('=====',y)
    for k,uf,n,dd in rec: print('%-40s UF %12.1f  NAT %12.1f  diff %10.2f mi'%(k,uf/1e6,n/1e6,dd/1e6))
json.dump(out,open('recon.json','w'))
def br(x,d=2):
    s=f'{x:,.{d}f}'; s=s.replace(',','X').replace('.',',').replace('X','.')
    return '0,0' if s in ('-0,0','-0,00') else s
NOMES={'import_tax':'Imposto de Importação','export_tax':'Imposto de Exportação','ipi':'IPI','irpf':'IRPF','irpj':'IRPJ','irrf':'IRRF','iof':'IOF','itr':'ITR','cofins':'COFINS','pis_pasep':'PIS/PASEP','csll':'CSLL','cide_fuels':'CIDE-Combustíveis','civil_servant_social_security_pss':'PSS (servidores)','other_rfb_revenue':'Outras receitas administradas','social_security_contributions_rgps':'Receita previdenciária (RGPS)','administered_by_other_agencies':'Administradas por outros órgãos','TOTAL':'**TOTAL GERAL**'}
L=['| Tributo | Soma das UFs 2024 (R$ mi) | Nacional 2024 (R$ mi) | Diferença 2024 (R$ mi) | Soma das UFs 2025 (R$ mi) | Nacional 2025 (R$ mi) | Diferença 2025 (R$ mi) |','|---|---:|---:|---:|---:|---:|---:|']
d4={k:(u,n,x) for k,u,n,x in out['2024']}; d5={k:(u,n,x) for k,u,n,x in out['2025']}
for k in d4:
    a=d4[k]; b=d5[k]
    L.append(f'| {NOMES[k]} | {br(a[0]/1e6,1)} | {br(a[1]/1e6,1)} | {br(a[2]/1e6,1)} | {br(b[0]/1e6,1)} | {br(b[1]/1e6,1)} | {br(b[2]/1e6,1)} |')
open('tableRecon.md','w').write('\n'.join(L)+'\n')
