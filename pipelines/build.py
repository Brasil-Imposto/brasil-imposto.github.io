import sys, json, csv, collections, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
YEAR=2024
# every input is required: a missing one stops the build, naming the script that writes it (pipelines/README.md, table); checked before
# the imports, because parse_rfb reads its CSV when imported
NEEDED={'arrecadacao-estado.csv':'download.sh','ibge_pop.json':'download.sh',f'transf_agg_{YEAR}.json':f'agg_transfers.py {YEAR}',
        'tt/lc176est.csv':'download.sh','tt/lc176mun.csv':'download.sh','direct_2024.json':'build_direct.py','sources.json':'build_direct.py'}
missing=[f'{f} (written by {w})' for f,w in NEEDED.items() if not os.path.exists(f)]
if missing:
    sys.exit('build.py: missing input in '+os.getcwd()+': '+'; '.join(missing))
from parse_rfb import agg as rfb_agg
from taxmap import TAXMAP
from parse_tt import parse as tt_parse, annual as tt_annual

COLLECTED='2026-09-25'
UFS={'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO','21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA','31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS','50':'MS','51':'MT','52':'GO','53':'DF'}
NAMES={}
out={}
# population
pop=json.load(open('ibge_pop.json'))[0]['resultados'][0]['series']
P={}
for s in pop:
    lid=s['localidade']['id']
    if lid in UFS:
        uf=UFS[lid]; NAMES[uf]=s['localidade']['nome']
        P[uf]={int(y):int(v) for y,v in s["serie"].items()}
# revenue
R=rfb_agg(str(YEAR))
def rev(uf):
    d=R[uf]
    bt={k:round(sum(d[c] for c in cols),2) for k,cols in TAXMAP.items()}
    tot=round(sum(d.values()),2)
    return {'total':tot,'rfb_administered':round(tot-bt['administered_by_other_agencies'],2),'by_tax':bt}
# transfers
T={}
if os.path.exists(f'transf_agg_{YEAR}.json'):
    rows=json.load(open(f'transf_agg_{YEAR}.json'))
    CONST={'0044':'fpe_net_of_fundeb','0045':'fpm_net_of_fundeb','0046':'ipi_exports_net_of_fundeb','006M':'itr_municipal_share_net_of_fundeb',
           '0C33':'fundeb_retention_on_federal_transfers','00SB':'fundeb_federal_complement','0A53':'oil_gas_royalties',
           '0547':'mineral_royalties_cfem','0546':'water_resources_compensation','0223':'water_resources_compensation',
           '0999':'cide_fuels_share','00H6':'iof_gold','0369':'salario_educacao_quotas'}
    cats=['fpe_net_of_fundeb','fpm_net_of_fundeb','ipi_exports_net_of_fundeb','itr_municipal_share_net_of_fundeb','fundeb_retention_on_federal_transfers',
          'fundeb_federal_complement','oil_gas_royalties','mineral_royalties_cfem','water_resources_compensation','cide_fuels_share','iof_gold',
          'lc176_kandir_compensation','salario_educacao_quotas','sus_health','education_fnde_and_other','social_assistance_suas','special_transfers_emendas_pix','other_legal_and_voluntary']
    excluded=collections.defaultdict(float)
    for uf in UFS.values(): T[uf]={c:0.0 for c in cats}
    for uf_,tipo,fav,ug,func,acao,nome,ling,modal,mun,v in rows:
        pub = fav in ('Administração Pública Municipal','Administração Pública Estadual ou do Distrito Federal') or (fav=='Administração Pública' and modal!='80') or (fav=='Agentes Intermediários' and acao in ('00VP','00WF'))
        if uf_ not in T or not pub or acao=='00SE':
            excluded[(uf_ if uf_ in T else 'sem_uf', fav if not pub else ('LC176 sem UF' if acao=='00SE' else 'pub'))]+=v
            continue
        if acao in CONST: c=CONST[acao]
        elif acao=='0EC2': c='special_transfers_emendas_pix'
        elif func=='10': c='sus_health'
        elif func=='12': c='education_fnde_and_other'
        elif func=='08': c='social_assistance_suas'
        else: c='other_legal_and_voluntary'
        T[uf_][c]+=v
    # LC 176 from Tesouro (Portal records it without UF)
    de,_,_=tt_parse('tt/lc176est.csv'); dm,_,_=tt_parse('tt/lc176mun.csv')
    ae=tt_annual(de,YEAR); am=tt_annual(dm,YEAR)
    for uf in T: T[uf]['lc176_kandir_compensation']=ae.get(uf,0.0)+am.get(uf,0.0)
    json.dump({'|'.join(k):v for k,v in excluded.items()},open(f'transf_excluded_{YEAR}.json','w'),ensure_ascii=False)
# direct spending
D={}
if os.path.exists('direct_2024.json'):
    D=json.load(open('direct_2024.json'))
SRC_REV='https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv'
res=[]
for uf in sorted(UFS.values()):
    o={'uf':uf,'name':NAMES[uf],'population':P[uf][YEAR],'population_latest':P[uf][max(P[uf])],'population_latest_year':max(int(y) for y in P[uf]),
       'federal_revenue':rev(uf)}
    if T:
        bc={k:round(v,2) for k,v in T[uf].items()}
        o['transfers']={'total':round(sum(bc.values()),2),'by_category':bc}
    if D:
        d=D[uf]
        o['direct_spending']=d
    o['sources']=json.load(open('sources.json'))
    res.append(o)
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data',f'uf-balance-{YEAR}.json')
# written to a temporary file first, so a failure halfway never leaves a cut file in place of the published one
with open(OUT+'.tmp','w') as f:
    json.dump(res,f,ensure_ascii=False,indent=1)
os.replace(OUT+'.tmp',OUT)
print('written',len(res))
