#!/usr/bin/env bash
# Downloads the conversion inputs for the works comparisons (same sources and method as data/scripts/bridges/).
# Used by build_ete_insular.py, build_cei_comasa.py and convert.py. The road works use roads_download.sh.
# Run inside a working directory OUTSIDE the repository.
set -euo pipefail
UA="Mozilla/5.0"
get() { curl -sS -L -g -A "$UA" -o "$1" "$2" -w "$1 %{http_code} %{size_download}\n"; }

# 1. IBGE/SIDRA: IPCA, monthly index number (table 1737, variable 2266, base Dec/1993 = 100)
get ipca.json "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all?formato=json"

# 2. World Bank (WDI): official exchange rate (LCU per US$) and PPP conversion factor (LCU per international $)
for ind in PA.NUS.FCRF PA.NUS.PPP; do
  get "wb_works_$ind.json" "https://api.worldbank.org/v2/country/BRA;USA/indicator/$ind?format=json&per_page=1000&date=2015:2025"
done
