import json, sys, collections, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from parse_rfb import agg
J=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','uf-balance-2024.json')))
def br(x,d=2):
    s=f'{x:,.{d}f}'
    return s.replace(',','X').replace('.',',').replace('X','.')
REG=['RO','AC','AM','RR','PA','AP','TO','MA','PI','CE','RN','PB','PE','AL','SE','BA','MG','ES','RJ','SP','PR','SC','RS','MS','MT','GO','DF']
by={o['uf']:o for o in J}
lines=['| UF | População 2024 | Arrecadação federal (R$ bi) | Transferências (R$ bi) | Gasto direto disponível (R$ bi) | Saldo (a) R$ bi | Saldo (a) R$/hab | Saldo (b) R$ bi | Saldo (b) R$/hab |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
T=collections.defaultdict(float)
rowsA=[]
for uf in REG:
    o=by[uf]; p=o['population']; r=o['federal_revenue']['total']; t=o['transfers']['total']; d=o['direct_spending']['total_available']
    a=r-t; b=r-t-d
    T['p']+=p; T['r']+=r; T['t']+=t; T['d']+=d
    rowsA.append((uf,a/p,b/p))
    lines.append(f"| {uf} | {br(p,0)} | {br(r/1e9)} | {br(t/1e9)} | {br(d/1e9)} | {br(a/1e9)} | {br(a/p,0)} | {br(b/1e9)} | {br(b/p,0)} |")
a=T['r']-T['t']; b=a-T['d']
lines.append(f"| **Soma 27 UFs** | {br(T['p'],0)} | {br(T['r']/1e9)} | {br(T['t']/1e9)} | {br(T['d']/1e9)} | {br(a/1e9)} | {br(a/T['p'],0)} | {br(b/1e9)} | {br(b/T['p'],0)} |")
open('tableA.md','w').write('\n'.join(lines)+'\n')
print('\n'.join(lines))
print('neg a:',[u for u,x,y in rowsA if x<0]); print('neg b:',[u for u,x,y in rowsA if y<0])
# detail table: revenue by main taxes? and direct spending breakdown
L=['| UF | INSS (benefícios emitidos, R$ bi) | dos quais BPC/LOAS (R$ bi) | Bolsa Família (R$ bi) | FCDF (R$ bi) | Folha federal |','|---|---:|---:|---:|---:|---|']
for uf in REG:
    d=by[uf]['direct_spending']
    L.append(f"| {uf} | {br(d['inss_benefits']/1e9)} | {br(d['inss_bpc_loas_included']/1e9)} | {br(d['bolsa_familia']/1e9)} | {br(d['fcdf_df_constitutional_fund']/1e9)} | null |")
open('tableD.md','w').write('\n'.join(L)+'\n')
# transfers main categories per UF
cats=[('FPE','fpe_net_of_fundeb'),('FPM','fpm_net_of_fundeb'),('Fundeb (retenção + complementação)',None),('Royalties e compensações',None),('SUS','sus_health'),('Educação (salário-educação + FNDE)',None),('Demais',None)]
L=['| UF | FPE líq. | FPM líq. | Fundeb: retenção 20% das transf. federais | Fundeb: complementação da União | Royalties e compensações financeiras | SUS fundo a fundo | Salário-educação + FNDE | Demais (IPI-Exp, ITR, CIDE, IOF-Ouro, LC 176, SUAS, emendas Pix, outras) | Total |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for uf in REG:
    c=by[uf]['transfers']['by_category']
    fpe=c['fpe_net_of_fundeb']; fpm=c['fpm_net_of_fundeb']; fr=c['fundeb_retention_on_federal_transfers']; fc=c['fundeb_federal_complement']
    roy=c['oil_gas_royalties']+c['mineral_royalties_cfem']+c['water_resources_compensation']
    sus=c['sus_health']; edu=c['salario_educacao_quotas']+c['education_fnde_and_other']
    tot=by[uf]['transfers']['total']; rest=tot-fpe-fpm-fr-fc-roy-sus-edu
    L.append(f"| {uf} | "+' | '.join(br(x/1e9) for x in [fpe,fpm,fr,fc,roy,sus,edu,rest,tot])+' |')
open('tableT.md','w').write('\n'.join(L)+'\n')
# revenue 2024 vs 2025
a4=agg('2024'); a5=agg('2025')
L=['| UF | 2024 (R$ bi) | 2025 (R$ bi) | Variação (R$ bi) | Participação 2024 | Participação 2025 |','|---|---:|---:|---:|---:|---:|']
t4=sum(sum(v.values()) for v in a4.values()); t5=sum(sum(v.values()) for v in a5.values())
for uf in sorted(REG,key=lambda u:-sum(a4[u].values())):
    x=sum(a4[uf].values()); y=sum(a5[uf].values())
    L.append(f"| {uf} | {br(x/1e9)} | {br(y/1e9)} | {br((y-x)/1e9)} | {br(100*x/t4,1)}% | {br(100*y/t5,1)}% |")
L.append(f"| **Soma** | {br(t4/1e9)} | {br(t5/1e9)} | {br((t5-t4)/1e9)} | 100% | 100% |")
open('table2025.md','w').write('\n'.join(L)+'\n')
# domicile shares
pib=json.load(open('ibge_pib.json'))[0]['resultados'][0]['series']
NM={o['name']:o['uf'] for o in J}
PIB={NM[s['localidade']['nome']]:float(s['serie']['2023'])*1000 for s in pib if s['localidade']['nome'] in NM}
tp=sum(PIB.values()); tpop=T['p']; tr=T['r']
L=['| UF | Participação na arrecadação federal 2024 | Participação no PIB 2023 (IBGE) | Participação na população 2024 |','|---|---:|---:|---:|']
for uf in ['SP','RJ','DF','MG','RS','PR','SC','BA']:
    L.append(f"| {uf} | {br(100*by[uf]['federal_revenue']['total']/tr,1)}% | {br(100*PIB[uf]/tp,1)}% | {br(100*by[uf]['population']/tpop,1)}% |")
open('tableDom.md','w').write('\n'.join(L)+'\n')
print(open('tableDom.md').read())
# specific DF/RJ numbers
for uf in ['DF','RJ','SP']:
    bt=by[uf]['federal_revenue']['by_tax']
    print(uf,{k:round(v/1e9,2) for k,v in bt.items()})
nat=collections.defaultdict(float)
for o in J:
    for k,v in o['federal_revenue']['by_tax'].items(): nat[k]+=v
print('NAT',{k:round(v/1e9,2) for k,v in nat.items()})
c='IRRF - RENDIMENTOS DO TRABALHO'
print('IRRF trabalho DF 2024 %.2f of %.2f'%(a4['DF'][c]/1e9,sum(v[c] for v in a4.values())/1e9))
print('PIB total 2023', tp)
