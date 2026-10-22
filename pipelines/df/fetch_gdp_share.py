"""The DF's share of Brazil's GDP, for the DF estimate on the map (D146): IBGE, SIDRA table 5938 (PIB dos Municípios),
variable 37 (PIB a preços correntes), latest year, Brasil and the DF.

Usage: uv run python -B pipelines/df/fetch_gdp_share.py
Writes data/df/gdp-share.json
"""
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URL = "https://apisidra.ibge.gov.br/values/t/5938/n1/all/n3/53/v/37/p/last%201"
rows = json.loads(subprocess.run(["curl", "-sS", "-m", "120", URL], capture_output=True, text=True, check=True).stdout)[1:]
by = {r["D1N"]: (int(r["V"]), r["D3N"]) for r in rows}
(br, year), (df, year_df) = by["Brasil"], by["Distrito Federal"]
assert year == year_df and rows[0]["MN"] == "Mil Reais"
out = {"year": int(year), "gdp_brasil_thousand_reais": br, "gdp_df_thousand_reais": df, "share": df / br, "source": URL,
       "source_name": "IBGE, PIB dos Municípios (SIDRA, tabela 5938, variável 37, PIB a preços correntes)", "read_on": "2026-10-21"}
(ROOT / "data" / "df" / "gdp-share.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(out["year"], round(out["share"] * 100, 4), "%")
