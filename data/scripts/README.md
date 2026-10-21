# Scripts do balanço federal por UF (2024)

Reproduzem `data/uf-balance-2024.json` e as tabelas do relatório `docs/research/BRASIL-IMPOSTO_RESEARCH_dados-por-uf_2026-09-25.md`.

## Pré-requisitos

- `bash`, `curl`, `unzip`, Python 3.
- `openpyxl` (só para `build_direct.py`, `recon.py` e a seção 4 de `checks.py`): `python3 -m venv .venv && .venv/bin/pip install openpyxl`.
- Nenhuma chave de API, nenhum login.

## Como rodar

Os downloads brutos somam cerca de 150 MB compactados e **não** ficam no repositório. Rode tudo a partir de um diretório de trabalho fora do repo:

```bash
SCRIPTS=~/Documents/Brasil-Imposto/data/scripts
mkdir -p /tmp/uf-data && cd /tmp/uf-data
bash $SCRIPTS/download.sh
python3 $SCRIPTS/agg_transf.py 2024
python3 $SCRIPTS/agg_desp.py 2024
python3 $SCRIPTS/agg_fcdf.py
python3 $SCRIPTS/build_direct.py
python3 $SCRIPTS/build.py
python3 $SCRIPTS/recon.py
python3 $SCRIPTS/tables.py
python3 $SCRIPTS/checks.py
```

(`python3` com `openpyxl` instalado; se usar o venv, troque por `.venv/bin/python`.)

## Ordem, entradas e saídas

| # | Script | Entradas (no diretório de trabalho) | Saídas |
|---|---|---|---|
| 1 | `download.sh` | nenhuma | `arrecadacao-estado.csv`, `serie-1994-2025.xlsx`, `transf/2024MM.zip`, `desp/2024MM.zip`, `tt/*.csv`, `aeps_2024.zip` e `aeps/`, `pbf_2024.csv`, `ibge_pop.json`, `ibge_pib.json` |
| 2 | `agg_transf.py 2024` | `transf/2024MM.zip` | `transf_agg_2024.json` (soma por UF, tipo, favorecido, função, ação, modalidade) |
| 3 | `agg_desp.py 2024` | `desp/2024MM.zip` | `desp_agg_2024.json` (valor pago e restos a pagar pagos por UF, órgão, grupo, modalidade, ação, localizador) |
| 4 | `agg_fcdf.py` | `desp/2024MM.zip` | `fcdf_2024.json` (Fundo Constitucional do DF, UO 73901) |
| 5 | `build_direct.py` | `aeps/`, `pbf_2024.csv`, `fcdf_2024.json` | `sources.json`, `direct_2024.json` |
| 6 | `build.py` | `arrecadacao-estado.csv`, `ibge_pop.json`, `transf_agg_2024.json`, `tt/lc176*.csv`, `direct_2024.json`, `sources.json` | `data/uf-balance-2024.json` (no repo), `transf_excluded_2024.json` |
| 7 | `recon.py` | `arrecadacao-estado.csv`, `serie-1994-2025.xlsx` | `recon.json`, `tableRecon.md` (conciliação 2024 e 2025) |
| 8 | `tables.py` | `data/uf-balance-2024.json`, `arrecadacao-estado.csv`, `ibge_pib.json` | `tableA.md`, `tableD.md`, `tableT.md`, `table2025.md`, `tableDom.md` |
| 9 | `checks.py` | as mesmas acima | só imprime: formatos numéricos, quebra do DF em 2025, setembro de 2024, Portal x Tesouro, quanto do gasto direto tem UF |

Módulos auxiliares (importados, não rodam sozinhos): `parse_rfb.py` (lê o CSV da Receita, que mistura formatos numéricos), `taxmap.py` (colunas da Receita para as chaves do JSON e linhas da série nacional), `parse_tt.py` (lê os CSVs largos do Tesouro).

## Observações

- `build_direct.py` grava `collected_at = 2026-09-25`. Ao recoletar, atualize essa data.
- Os arquivos da Receita, do Portal e do Tesouro podem ser revisados pelos órgãos; uma nova coleta pode dar números um pouco diferentes. Ao reproduzir, rode `checks.py` e compare com o relatório.
- Para 2025, troque o ano nos downloads e nos scripts, mas leia antes a seção 1.3 do relatório: a distribuição por UF da Receita em 2025 está quebrada.
