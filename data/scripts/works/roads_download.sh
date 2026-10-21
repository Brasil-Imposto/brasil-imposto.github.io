#!/usr/bin/env bash
# Baixa as entradas oficiais das fichas de obra (SC-401 terceira faixa e duplicação da BR-470/SC).
# Rodar num diretório de trabalho FORA do repositório: bash roads_download.sh <workdir>
# Nenhuma chave de API. Coleta original: 2026-09-30, de um IP nos EUA.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=${1:-.}; mkdir -p "$W"/{sc401,br470/cgov,comp,tse,dotc,doe}; cd "$W"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
get() { curl -sS -L -g -A "$UA" -o "$1" "$2" -w "$1 %{http_code} %{size_download}\n"; sleep 1; }

# 1. IPCA (IBGE/SIDRA 1737, número-índice)
get ipca.json "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all?formato=json"

# 2. SC: registro de contratos (SIGEF/SICOP, CGE-SC) e extratos SICOP do Portal da Transparência de SC
[ -s contratos.csv ] || get contratos.csv "https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/ff7c3cac-3e38-4801-9fd8-e4ccb69ca31d/download/contratos.csv"
API=https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api
for t in 104411 103057 101659; do
  curl -sS -g -H "Referer: https://www.transparencia.sc.gov.br/" -o "sc401/sicop_$t.json" "$API/contratos/extratosicop?nutitulofiltro[]=$t"; sleep 1
done

# 3. PNCP: contrato CT-00014/2025, licitação CE 204/2024, resultado e documentos (ETP, relatórios do projeto)
get sc401/contrato.json "https://pncp.gov.br/api/pncp/v1/orgaos/82951344000140/contratos/2025/2"
get sc401/compra.json "https://pncp.gov.br/api/consulta/v1/orgaos/82951344000140/compras/2024/194"
get sc401/resultados.json "https://pncp.gov.br/api/pncp/v1/orgaos/82951344000140/compras/2024/194/itens/1/resultados"
for n in 1 2 3 9; do get "sc401/arq$n.pdf" "https://pncp.gov.br/pncp-api/v1/orgaos/82951344000140/compras/2024/194/arquivos/$n"; done

# 4. DOE-SC: extrato do contrato (nº 22.468, 11/03/2025, p. 74) e portaria do fiscal (nº 22.483, 01/04/2025, p. 5)
get doe/doe_20250311_22468.pdf "https://portal.doe.sea.sc.gov.br/repositorio/2025/20250311/Jornal/22468.pdf"
get doe/doe_20250401_22483.pdf "https://portal.doe.sea.sc.gov.br/repositorio/2025/20250401/Jornal/22483.pdf"
get doe/doe_20250327_22480.pdf "https://portal.doe.sea.sc.gov.br/repositorio/2025/20250327/Jornal/22480.pdf"

# 5. TCE-SC: Diário Oficial Eletrônico com as decisões sobre a SC-401
for d in 2025-04-25 2025-05-02 2026-04-06 2026-04-22 2026-04-24 2026-05-05 2026-08-27 2026-09-08; do
  get "dotc/dotc-e$d.pdf" "https://consulta.tce.sc.gov.br/Diario/dotc-e$d.pdf"
done

# 6. Contratos.gov.br (API pública): contratos ativos das UG do DNIT (SC, sede, PE, BA, RS, PB) e históricos
for ug in 393013 393003 393029 393027 393012 393017; do get "comp/cgov_$ug.json" "https://contratos.comprasnet.gov.br/api/contrato/ug/$ug"; done
cp comp/cgov_393013.json br470/cgov_393013.json; cp comp/cgov_393003.json br470/cgov_393003.json
for id in 80967 106726 80916 98313 76826 80873 327515 204225 80935; do
  for l in historico empenhos faturas; do get "br470/cgov/${id}_$l.json" "https://contratos.comprasnet.gov.br/api/contrato/$id/$l"; done
done
# comparáveis: SC-401 (99884 Petrolina, 185752 Juazeiro, 568641 Feira de Santana, 352579 Maravilha);
# BR-470 (80981, 81007, 81065 BR-280/SC; 76890, 76891, 82000 BR-101/BA; 81013 BR-230/PB)
for id in 99884 185752 568641 352579 80981 81007 81065 76890 76891 82000 81013; do get "comp/h_$id.json" "https://contratos.comprasnet.gov.br/api/contrato/$id/historico"; done
get comp/mg230.json "https://pncp.gov.br/api/pncp/v1/orgaos/17309790000194/contratos/2026/293"

# 6b. Dados abertos de compras (módulo contratos): contratos do DNIT que citam a BR-470 (inclui os encerrados)
python3 - <<'PYC'
import json, re, time, urllib.parse, urllib.request
out = []
for y in range(2008, 2027):
    pg = 1
    while True:
        qs = urllib.parse.urlencode({'pagina': pg, 'tamanhoPagina': 500, 'codigoOrgao': '39252',
                                     'dataVigenciaInicialMin': f'{y}-01-01', 'dataVigenciaInicialMax': f'{y}-12-31'})
        d = json.load(urllib.request.urlopen(urllib.request.Request(
            'https://dadosabertos.compras.gov.br/modulo-contratos/1_consultarContratos?' + qs, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120))
        out += [r for r in d['resultado'] if re.search(r'BR[\s\-/]*470', (r.get('objeto') or '').upper())]
        if d['paginasRestantes'] == 0:
            break
        pg += 1
        time.sleep(1)
json.dump(out, open('br470/comprasgov_br470.json', 'w'), ensure_ascii=False)
print('comprasgov_br470.json', len(out))
PYC

# 6c. SC: aporte do Estado às obras federais (registros TC-00470/2021 no SIGEF) e seus extratos SICOP
python3 - <<'PYC'
import csv, json, urllib.request
csv.field_size_limit(10**9)
API = 'https://api-portal-transparencia.apps.sm.okd4.ciasc.sc.gov.br/api/contratos/extratosicop?nutitulofiltro%5B%5D='
out = {}
for r in csv.DictReader(open('contratos.csv', encoding='utf-8', errors='ignore'), delimiter=';'):
    if (r['NUCONTRATO'] or '').startswith('TC-00470') and r['NUTITULO']:
        d = json.load(urllib.request.urlopen(urllib.request.Request(API + r['NUTITULO'], headers={'Referer': 'https://www.transparencia.sc.gov.br/'}), timeout=120))
        out[r['NUCONTRATO']] = {'row': r, 'extrato': d, 'url': API + r['NUTITULO']}
json.dump(out, open('br470/sc_tc470.json', 'w'), ensure_ascii=False)
print('sc_tc470.json', len(out))
PYC

# 7. TCU: íntegra dos acórdãos (API da pesquisa textual; exige cabeçalhos de navegador)
for k in 2535085 2362146 2683534 2733019 2632499; do
  curl -sS -A "$UA" -H "Accept: application/json, text/plain, */*" -H "Referer: https://pesquisa.apps.tcu.gov.br/" -G \
    "https://pesquisa.apps.tcu.gov.br/rest/publico/base/acordao-completo/documento" \
    --data-urlencode "termo=KEY:ACORDAO-COMPLETO-$k" --data-urlencode "quantidade=1" --data-urlencode "inicio=0" -o "br470/d_$k.json"; sleep 2
done

# 8. DOU (Seção 3): extratos dos contratos dos 4 lotes da BR-470 (páginas da Imprensa Nacional)
for p in "26/07/2013 141" "14/02/2014 218" "29/05/2014 140"; do
  set -- $p; get "br470/dou_$(echo $1 | tr '/' '-')_$2.pdf" "https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=3&pagina=$2&data=$1&captchafield=firstAccess"
done

# 8b. Alesc, Memória Política: biografias dos governadores
mkdir -p alesc rf
get alesc/bio_514_jorginho_mello.html "https://memoriapolitica.alesc.sc.gov.br/biografia/514-Jorginho_Mello"
get alesc/bio_1308_carlos_moises.html "https://memoriapolitica.alesc.sc.gov.br/biografia/1308-Carlos_Moises"
get alesc/bio_1386_daniela_reinehr.html "https://memoriapolitica.alesc.sc.gov.br/biografia/1386-Daniela_Reinehr"

# 8c. Cadastro das empresas (base aberta da Receita via espelhos; o servidor oficial não responde do exterior)
for c in 84689066000392 03616409000125 83256172000158 82743832000162 85115053000100 92694348000144 09588906000143 76592542000162 83665141000150 76614254000161 80996861000100 78221066000107; do
  get "rf/$c.json" "https://minhareceita.org/$c"; sleep 5
  get "rf/ba_$c.json" "https://brasilapi.com.br/api/cnpj/v1/$c"; sleep 5
done

# 9. TSE: candidaturas 2010 e 2022 (partido na eleição)
for y in 2010 2022; do get "tse/consulta_cand_$y.zip" "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_$y.zip"; done

# 10. Execução orçamentária da BR-470 (SIOP) e pagamentos com restos a pagar (Portal da Transparência)
python3 "$HERE/br470_siop.py" br470/siop_br470.json 2010 2026 || true
echo "Depois: python3 $HERE/br470_payments.py br470/desp br470/br470_payments.json 2014 2026 (baixa ~150 arquivos mensais)"
echo "Por fim: python3 $HERE/build_sc401.py . && python3 $HERE/build_br470.py ."
