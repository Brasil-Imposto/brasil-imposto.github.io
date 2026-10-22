#!/usr/bin/env bash
# Usage: download_inputs.sh <workdir>. Downloads the small inputs of the series builders (about 10 MB).
# Run order (all with the same <workdir>, python with openpyxl and xlrd, plus pdftotext):
#   1. download_inputs.sh            Receita (UF CSV, national series, 2026 monthly analysis PDF, per-municipality XLSX), Tesouro LC 176
#   2. download_misocial.sh [UF ...]  MDS MI Social, Bolsa Familia / Auxilio Brasil / BPC per municipality and month
#   3. agg_transfers_monthly.py <workdir> 201901 <last YYYYMM> [pace] [--ufs SC,RS]   Portal da Transparencia, streamed and deleted month by month
#   4. beps_rgps_by_uf.py            BEPS tables 18 and 19 (RGPS emitted by UF, monthly)
#   5. aeps_inss_by_uf.py            AEPS table B.15 (INSS emitted by UF, annual)
#   6. build_population.py [--uf SC,RS] -> data/series/population.json
#   7. build_federal_by_uf_monthly.py -> data/series/federal-by-uf-monthly.json
#   8. build_municipal_federal.py [--uf RS] -> data/series/{uf}-municipal-federal.json
# Optional: inss_emitidos_municipio.py streams one month of the INSS benefit microdata (0.55 to 1 GB) to test INSS by municipality.
set -euo pipefail
cd "${1:?workdir}" && mkdir -p rfbpdf rfbmun tt
get() { curl -sS -L -g -A "Mozilla/5.0" -m 600 -o "$1" "$2" -w "$1 %{http_code} %{size_download}\n"; }
R=https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao
get arrecadacao-estado.csv "https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv"
get serie-1994-2025.xlsx "$R/serie-historica/arrecadacao-das-receitas-federais-1994-a-2025.xlsx"
# latest monthly analysis of the year: its Tabela III holds the national monthly totals of 2026 (update the month when a new one is out)
get rfbpdf/analise-mensal-2026.pdf "https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/relatorios/arrecadacao-federal/2026/analise-mensal-ago-2026.pdf/@@download/file"
M="$R/copy_of_arrecadacao-das-receitas-administradas-pela-rfb-por-municipio/arrecadacao-das-receitas-administradas-pela-rfb"
for y in 2019 2020 2021 2022 2023 2024 2025; do
  get "rfbmun/rfb-mun-$y.xlsx" "$M/arrecadacao-da-receita-administrada-pela-rfb-por-municipio-$y.xlsx"
done
T=https://www.tesourotransparente.gov.br/ckan/dataset/f85b6632-1c9c-4beb-9e60-72e91156c984/resource
get tt/lc176est.csv "$T/a58f5b6d-4e1f-4571-9597-3c8cca6d8259/download/lc176est.csv"
get tt/lc176mun.csv "$T/b05b73e1-6189-4be3-8ea6-98d864db8a3c/download/lc176mun.csv"
