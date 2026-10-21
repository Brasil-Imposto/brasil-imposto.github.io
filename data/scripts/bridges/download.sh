#!/usr/bin/env bash
# Baixa as entradas oficiais da comparação de pontes (Ponte Hercílio Luz x comparáveis).
# Rodar dentro de um diretório de trabalho FORA do repositório (o CSV de contratos de SC tem ~73 MB).
set -euo pipefail
UA="Mozilla/5.0"
get() { curl -sS -L -g -A "$UA" -o "$1" "$2" -w "$1 %{http_code} %{size_download}\n"; }

# 1. IBGE/SIDRA: IPCA, número-índice mensal (tabela 1737, variável 2266, base dez/1993 = 100)
get ipca.json "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all?formato=json"

# 2. Banco Mundial (WDI): câmbio oficial médio anual (LCU por US$) e fator de conversão PPP do PIB (LCU por $ internacional)
for ind in PA.NUS.FCRF PA.NUS.PPP; do
  get "wb_$ind.json" "https://api.worldbank.org/v2/country/BRA;HUN;CAN;VNM/indicator/$ind?format=json&per_page=1000&date=1995:2025"
done

# 3. Portal de Dados Abertos de SC: contratos do Estado (SIGEF), CSV ";" em UTF-8
if [ ! -s contratos.csv ]; then
  get contratos.csv "https://dados.sc.gov.br/dataset/93dab950-e805-4388-8418-cfb3b73f1623/resource/ff7c3cac-3e38-4801-9fd8-e4ccb69ca31d/download/contratos.csv"
fi
