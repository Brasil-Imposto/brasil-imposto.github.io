# Writes sources.json (sources per field) and direct_2024.json (INSS, BPC, Bolsa Família, FCDF by state).
# Inputs: aeps/ (tables 24SB15 and 24S13_03), pbf_2024.csv, fcdf_2024.json. Needs openpyxl.
import json, glob, csv, collections, openpyxl, warnings
warnings.filterwarnings('ignore')
C='2026-09-25'  # date of the original collection; update it when collecting again
PT='https://portaldatransparencia.gov.br/download-de-dados/transferencias/'
sources=[
 {'field':'population','url':'https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024|2025|2026/variaveis/9324?localidades=N3[all]|N1[all]','reference_year':2024,'collected_at':C,'note':'IBGE, Estimativas de População (tabela SIDRA 6579, variável 9324). population = estimativa 2024 (ano de referência do balanço); population_latest = estimativa 2026.'},
 {'field':'federal_revenue','url':'https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv','reference_year':2024,'collected_at':C,'note':'Receita Federal, Arrecadação por Estado (mensal, por tributo, preços correntes), soma de janeiro a dezembro de 2024. Página: https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/arrecadacao-por-estado/arrecadacao-por-estado'},
 {'field':'federal_revenue (conciliação nacional)','url':'https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/serie-historica/arrecadacao-das-receitas-federais-1994-a-2025.xlsx','reference_year':2024,'collected_at':C,'note':'Receita Federal, série histórica nacional, aba 2024, TOTAL GERAL.'},
 {'field':'transfers (exceto lc176_kandir_compensation)','url':PT+'202401 ... '+PT+'202412','reference_year':2024,'collected_at':C,'note':'CGU, Portal da Transparência, Transferências (12 arquivos mensais, coluna VALOR TRANSFERIDO). Só favorecidos da administração pública estadual e municipal; excluídas entidades privadas, organismos internacionais e registros sem UF.'},
 {'field':'transfers.by_category.lc176_kandir_compensation','url':'https://www.tesourotransparente.gov.br/ckan/dataset/f85b6632-1c9c-4beb-9e60-72e91156c984/resource/a58f5b6d-4e1f-4571-9597-3c8cca6d8259/download/lc176est.csv','reference_year':2024,'collected_at':C,'note':'Tesouro Nacional, Transferências Obrigatórias da União, LC176_EST mais LC176_MUN (https://www.tesourotransparente.gov.br/ckan/dataset/f85b6632-1c9c-4beb-9e60-72e91156c984/resource/b05b73e1-6189-4be3-8ea6-98d864db8a3c/download/lc176mun.csv). O Portal da Transparência registra esta transferência sem UF.'},
 {'field':'direct_spending.inss_benefits','url':'https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/arquivos/aeps_2024.zip','reference_year':2024,'collected_at':C,'note':'Ministério da Previdência Social, AEPS 2024, tabela B.15 (24SB15.xlsx): valor de benefícios emitidos, acumulado no ano, R$ mil convertido para R$. Inclui BPC/LOAS.'},
 {'field':'direct_spending.inss_bpc_loas_included','url':'https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/arquivos/aeps_2024.zip','reference_year':2024,'collected_at':C,'note':'AEPS 2024, tabela 13.3 (24S13_03.xlsx): amparos assistenciais emitidos, acumulado no ano. Já contido em inss_benefits; informativo, não somar.'},
 {'field':'direct_spending.bolsa_familia','url':'https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&fq=anomes_s:2024*&fl=codigo_ibge,sigla_uf,municipio,anomes_s,valor_repassado_bolsa_familia_f,pbf_qtd_familias_benef_i&rows=200000&wt=csv','reference_year':2024,'collected_at':C,'note':'MDS, Matriz de Informação Social (MI Social), campo valor_repassado_bolsa_familia_f, soma dos 12 meses de 2024 dos 5.571 municípios.'},
 {'field':'direct_spending.fcdf_df_constitutional_fund','url':'https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/202401 ... /202412','reference_year':2024,'collected_at':C,'note':'CGU, Portal da Transparência, Execução da Despesa, unidade orçamentária 73901 (FCDF), valor pago mais restos a pagar pagos em 2024. Só existe para o DF.'},
 {'field':'direct_spending.federal_payroll','url':None,'reference_year':2024,'collected_at':C,'note':'null: não foi encontrada fonte oficial com a folha federal anual por UF em formato aberto e de tamanho viável. Ver o relatório.'},
]
json.dump(sources,open('sources.json','w'),ensure_ascii=False,indent=1)
UFN={'Rondônia':'RO','Acre':'AC','Amazonas':'AM','Roraima':'RR','Pará':'PA','Amapá':'AP','Tocantins':'TO','Maranhão':'MA','Piauí':'PI','Ceará':'CE','Rio Grande do Norte':'RN','Paraíba':'PB','Pernambuco':'PE','Alagoas':'AL','Sergipe':'SE','Bahia':'BA','Minas Gerais':'MG','Espírito Santo':'ES','Rio de Janeiro':'RJ','São Paulo':'SP','Paraná':'PR','Santa Catarina':'SC','Rio Grande do Sul':'RS','Mato Grosso do Sul':'MS','Mato Grosso':'MT','Goiás':'GO','Distrito Federal':'DF'}
wb=openpyxl.load_workbook(glob.glob('aeps/**/24SB15.xlsx',recursive=True)[0],data_only=True)
inss={}
for row in wb.worksheets[0].iter_rows(values_only=True):
    if row[0] in UFN: inss[UFN[row[0]]]=row[3]*1000   # column Total 2024, R$ thousand
    if row[0]=='BRASIL': inss_br=row[3]*1000
wb=openpyxl.load_workbook(glob.glob('aeps/**/24S13_03.xlsx',recursive=True)[0],data_only=True)
bpc={}; cur=None
for ws in wb.worksheets:
    for row in ws.iter_rows(values_only=True):
        if row[0]: cur=row[0]
        if cur in UFN and row[1]=='2024': bpc[UFN[cur]]=row[2]*1000
        if cur=='BRASIL' and row[1]=='2024': bpc_br=row[2]*1000
pbf=collections.defaultdict(float)
for r in csv.DictReader(open('pbf_2024.csv')):
    if r['valor_repassado_bolsa_familia_f']: pbf[r['sigla_uf']]+=float(r['valor_repassado_bolsa_familia_f'])
fcdf=sum(json.load(open('fcdf_2024.json')).values())
if not (len(inss)==27 and len(bpc)==27 and len(pbf)==27):
    raise SystemExit('check failed: len(inss) == 27 and len(bpc) == 27 and (len(pbf) == 27)')
print('INSS sum UF',sum(inss.values()),'BR',inss_br,'| BPC sum',sum(bpc.values()),'BR',bpc_br,'| PBF',sum(pbf.values()),'| FCDF',fcdf)
D={}
for uf in inss:
    f=round(fcdf,2) if uf=='DF' else 0.0
    d={'inss_benefits':round(inss[uf],2),'inss_bpc_loas_included':round(bpc[uf],2),'bolsa_familia':round(pbf[uf],2),'fcdf_df_constitutional_fund':f,'federal_payroll':None}
    d['total_available']=round(d['inss_benefits']+d['bolsa_familia']+f,2)
    D[uf]=d
json.dump(D,open('direct_2024.json','w'),indent=1)
