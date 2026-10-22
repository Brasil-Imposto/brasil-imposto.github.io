# Saldo com a União dos municípios de um estado, 2024 (SC, RS)

1. `download.sh <pasta> [UF]`: baixa os insumos pequenos (arrecadação federal por município da Receita, malha, nomes e população dos municípios do IBGE, Bolsa Família do MDS). UF padrão: SC.
2. `python3 pipelines/series/agg_transfers_monthly.py <pasta> 202401 202412 90 --ufs <UF>`: transferências de 2024 do Portal da Transparência, um arquivo por vez, agregado e apagado (a série mensal já deixa esses arquivos em `pipelines/series/cache/municipal-federal/cache`).
3. `build_municipal_balance.py <pasta> --uf <UF> [--transfers <pasta dos transf_2024MM.json>]`: gera `data/<uf>-municipal-balance-2024.json` (precisa de `openpyxl`).
4. `node docs/superpowers/tools/build-geo-state.cjs <UF> <pasta>/mesh.json <pasta>/nomes.json`: gera `geo-<uf>.json`, a geometria do mapa do estado (malha e nomes do IBGE, endereços no topo do script).

Saldo = arrecadação federal registrada no município menos (transferências federais à prefeitura + Bolsa Família).
Não entram o INSS e a folha federal: não há dado aberto por município sem login no dados.gov.br.
Os impostos municipais vêm da coleta de todas as prefeituras (`pipelines/siconfi/build_municipal_taxes.py`).
Os nomes da Receita e do Portal são ligados ao código do IBGE por `pipelines/series/municipality_names.py`.
