#!/usr/bin/env bash
# Baixa todas as entradas oficiais usadas no balanço por UF de 2024.
# Rodar dentro de um diretório de trabalho FORA do repositório (os brutos somam ~150 MB compactados).
set -euo pipefail
UA="Mozilla/5.0"
get() { curl -sS -L -g -A "$UA" -o "$1" "$2" -w "$1 %{http_code} %{size_download}\n"; }

# 1. Receita Federal: arrecadação por UF (todos os anos) e série histórica nacional
get arrecadacao-estado.csv "https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv"
get serie-1994-2025.xlsx "https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/receitadata/arrecadacao/serie-historica/arrecadacao-das-receitas-federais-1994-a-2025.xlsx"

# 2. Portal da Transparência: transferências e execução da despesa, 12 meses de 2024
mkdir -p transf desp
for m in 01 02 03 04 05 06 07 08 09 10 11 12; do
  get "transf/2024$m.zip" "https://portaldatransparencia.gov.br/download-de-dados/transferencias/2024$m"
  get "desp/2024$m.zip" "https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/2024$m"
done

# 3. Tesouro Transparente: transferências obrigatórias (LC 176 por UF e conferência de FPE/FPM/IPI-Exp/ITR)
mkdir -p tt
B=https://www.tesourotransparente.gov.br/ckan/dataset/f85b6632-1c9c-4beb-9e60-72e91156c984/resource
get tt/fpe.csv      "$B/d99de819-0efe-4653-9a6d-1f46c208e740/download/fpe.csv"
get tt/fpm.csv      "$B/b4058cb2-3bcd-4565-be68-c3a697c40819/download/fpm.csv"
get tt/ipi-exp.csv  "$B/f2caeb29-1a84-4562-aedf-e578555278b1/download/ipi-exp.csv"
get tt/itr.csv      "$B/334a6d83-ee56-49a5-8723-b35a6c171923/download/itr.csv"
get tt/lc176est.csv "$B/a58f5b6d-4e1f-4571-9597-3c8cca6d8259/download/lc176est.csv"
get tt/lc176mun.csv "$B/b05b73e1-6189-4be3-8ea6-98d864db8a3c/download/lc176mun.csv"

# 4. Previdência: AEPS 2024 (tabelas 24SB15 e 24S13_03)
get aeps_2024.zip "https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/arquivos/aeps_2024.zip"
mkdir -p aeps && (cd aeps && unzip -q -o ../aeps_2024.zip || true)

# 5. MDS, Matriz de Informação Social: Bolsa Família por município e mês, 2024
get pbf_2024.csv "https://aplicacoes.mds.gov.br/sagi/servicos/misocial?q=*:*&fq=anomes_s:2024*&fl=codigo_ibge,sigla_uf,municipio,anomes_s,valor_repassado_bolsa_familia_f,pbf_qtd_familias_benef_i&rows=200000&wt=csv"

# 6. IBGE: estimativas de população (2024 a 2026) e PIB por UF 2023 (só comparação)
get ibge_pop.json "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2024|2025|2026/variaveis/9324?localidades=N3[all]|N1[all]"
get ibge_pib.json "https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/2023/variaveis/37?localidades=N3[all]|N1[all]"
