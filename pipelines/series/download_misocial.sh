#!/usr/bin/env bash
# Usage: download_misocial.sh <workdir> [UF ...]. MDS MI Social (Solr API, no key), one CSV per year: all 5.571
# municipalities, or only those of the UFs given (e.g. SC RS), filtered by the API.
# Fields: Bolsa Familia (valor_repassado_bolsa_familia_f), Auxilio Brasil (pab_valor_pago_d, pab_extraordinario_valor_pago_d),
# families, and BPC / RMV paid in the municipality (bpc_val_f, bpc_ben_i, rmv_val_f).
set -euo pipefail
cd "${1:?workdir}" && mkdir -p misocial
shift
F="codigo_ibge,sigla_uf,municipio,anomes_s,valor_repassado_bolsa_familia_f,pab_valor_pago_d,pab_extraordinario_valor_pago_d,pbf_qtd_familias_benef_i,pab_qtd_fam_benef_i,bpc_val_f,bpc_ben_i,bpc_idoso_val_f,bpc_pcd_val_f,rmv_val_f"
UFQ=""
if [ "$#" -gt 0 ]; then
  UFQ="&fq=sigla_uf:($(printf '%s%%20OR%%20' "$@" | sed 's/%20OR%20$//'))"
fi
for y in 2019 2020 2021 2022 2023 2024 2025 2026; do
  curl -sS -m 600 -o "misocial/misocial_$y.csv" \
    "https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&fq=anomes_s:${y}*${UFQ}&fl=$F&rows=200000&wt=csv" \
    -w "misocial_$y %{http_code} %{size_download}\n"
done
