set -u
# Usage: download.sh <workdir> [UF, default SC]. Downloads the small raw inputs of build_municipal_balance.py into <workdir>:
# the Receita file of 2024, the IBGE mesh, names and 2024 population of the state's municipalities, and Bolsa Família 2024.
# The 2024 federal transfers come from the monthly Portal caches (one raw file on disk at a time):
#   python3 pipelines/series/agg_transfers_monthly.py <workdir> 202401 202412 90 --ufs <UF>
UF=${2:-SC}; uf=$(echo "$UF" | tr 'A-Z' 'a-z')
case "$UF" in SC) C=42;; RS) C=43;; *) echo "IBGE code of $UF not listed in download.sh"; exit 1;; esac
cd "${1:?workdir}" || exit 1
B="https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/copy_of_arrecadacao-das-receitas-administradas-pela-rfb-por-municipio"
[ -s rfb-mun-2024.xlsx ] || curl -s -m 200 -L -A "Mozilla/5.0" -o rfb-mun-2024.xlsx "$B/arrecadacao-das-receitas-administradas-pela-rfb/arrecadacao-da-receita-administrada-pela-rfb-por-municipio-2024.xlsx"; echo "rfb $(wc -c < rfb-mun-2024.xlsx)"
curl -s -m 200 -o "mesh-$uf.json" "https://servicodados.ibge.gov.br/api/v3/malhas/estados/$C?formato=application/vnd.geo+json&qualidade=intermediaria&intrarregiao=municipio"; echo "mesh $(wc -c < "mesh-$uf.json")"
curl -s -m 200 -o "mun-$uf.json" "https://servicodados.ibge.gov.br/api/v1/localidades/estados/$C/municipios"; echo "names $(wc -c < "mun-$uf.json")"
curl -s -m 200 -o "pop-$uf.json" "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024/variaveis/9324?localidades=N6%5BN3%5B$C%5D%5D"; echo "pop $(wc -c < "pop-$uf.json")"
curl -s -m 300 -o "bf-$uf.csv" "https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&fq=anomes_s:2024*&fq=sigla_uf:$UF&fl=codigo_ibge,anomes_s,valor_repassado_bolsa_familia_f&rows=20000&wt=csv"; echo "bf $(wc -l < "bf-$uf.csv")"
echo DONE
