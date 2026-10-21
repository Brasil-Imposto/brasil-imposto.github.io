"""Conversion to BRL of December 2024, same method as data/scripts/bridges/build.py.

(i)  FX:  amount_LCU * (BRL per USD / LCU per USD)[year] * IPCA[Dec 2024] / IPCA[year average]
(ii) PPP: amount_LCU * (BRL per intl $ / LCU per intl $)[year] * IPCA[Dec 2024] / IPCA[year average]
For amounts already in BRL both reduce to the IPCA correction. When the price base month is known
(Brazilian contracts), the monthly index of that month is used instead of the year average.
Inputs come from download.sh (ipca.json, wb_works_PA.NUS.FCRF.json, wb_works_PA.NUS.PPP.json).
"""
import json
import os

TARGET = "202412"
URL_IPCA = "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all?formato=json"
URL_WB = "https://api.worldbank.org/v2/country/BRA;USA/indicator/{ind}?format=json&per_page=1000&date=2015:2025"


class Converter:
    def __init__(self, workdir):
        rows = json.load(open(os.path.join(workdir, "ipca.json")))[1:]
        self.ipca = {r["D3C"]: float(r["V"]) for r in rows}
        self.fx, self.fx_updated = self._wb(workdir, "PA.NUS.FCRF")
        self.ppp, self.ppp_updated = self._wb(workdir, "PA.NUS.PPP")

    @staticmethod
    def _wb(workdir, ind):
        d = json.load(open(os.path.join(workdir, f"wb_works_{ind}.json")))
        out = {}
        for r in d[1]:
            if r["value"] is not None:
                out.setdefault(r["countryiso3code"], {})[int(r["date"])] = float(r["value"])
        return out, d[0].get("lastupdated")

    def year_avg(self, y):
        return sum(self.ipca[f"{y}{m:02d}"] for m in range(1, 13)) / 12

    def month_factor(self, yyyymm):
        return self.ipca[TARGET] / self.ipca[yyyymm]

    def brl_month(self, amount, yyyymm):
        f = self.month_factor(yyyymm)
        return {"amount_brl_nominal": amount, "price_month": yyyymm, "ipca_index_price_month": self.ipca[yyyymm],
                "ipca_index_dec2024": self.ipca[TARGET], "ipca_factor_to_dec2024": round(f, 6),
                "amount_brl_2024": round(amount * f, 2)}

    def foreign_year(self, amount, iso3, year):
        ipf = self.ipca[TARGET] / self.year_avg(year)
        fx_rate = self.fx["BRA"][year] / self.fx[iso3][year]
        ppp_rate = self.ppp["BRA"][year] / self.ppp[iso3][year]
        return {"amount_lcu": amount, "year": year, "ipca_year_avg": round(self.year_avg(year), 4),
                "ipca_factor_to_dec2024": round(ipf, 6), "fx_lcu_per_usd": self.fx[iso3][year],
                "fx_brl_per_usd": self.fx["BRA"][year], "ppp_lcu_per_intl_usd": self.ppp[iso3][year],
                "ppp_brl_per_intl_usd": self.ppp["BRA"][year],
                "amount_brl_2024_fx": round(amount * fx_rate * ipf, 2),
                "amount_brl_2024_ppp": round(amount * ppp_rate * ipf, 2)}

    def method(self, used_months, used_years):
        return {
            "target": "BRL de dezembro de 2024",
            "brl_rule": "Valores em BRL: correção pelo IPCA do mês-base do preço (ou do mês do gasto) até dez/2024.",
            "fx_method": "amount_LCU * (BRL por USD / LCU por USD) do ano do gasto * IPCA dez/2024 / média anual do IPCA do ano do gasto",
            "ppp_method": "amount_LCU * (fator PPP do Brasil / fator PPP do país) do ano do gasto * IPCA dez/2024 / média anual do IPCA do ano do gasto",
            "same_as": "data/scripts/bridges/build.py (mesmas fontes e fórmulas)",
            "ipca": {"source": URL_IPCA, "table": "SIDRA 1737, variável 2266, número-índice (dez/1993 = 100)",
                     "dec_2024": self.ipca[TARGET], "months_used": {m: self.ipca[m] for m in sorted(set(used_months))},
                     "year_averages_used": {y: round(self.year_avg(y), 4) for y in sorted(set(used_years))}},
            "fx": {"source": URL_WB.format(ind="PA.NUS.FCRF"), "indicator": "PA.NUS.FCRF, Official exchange rate (LCU per US$, period average), World Bank WDI",
                   "last_updated": self.fx_updated, "values": {c: {y: self.fx[c][y] for y in sorted(set(used_years)) if y in self.fx.get(c, {})} for c in ("BRA", "USA")}},
            "ppp": {"source": URL_WB.format(ind="PA.NUS.PPP"), "indicator": "PA.NUS.PPP, PPP conversion factor, GDP (LCU per international $), World Bank WDI / ICP",
                    "last_updated": self.ppp_updated, "values": {c: {y: self.ppp[c][y] for y in sorted(set(used_years)) if y in self.ppp.get(c, {})} for c in ("BRA", "USA")}},
        }


def no_dashes(obj):
    """Project style rule: the en dash and em dash of quoted originals become a plain hyphen."""
    if isinstance(obj, str):
        return obj.replace("\u2013", "-").replace("\u2014", "-")
    if isinstance(obj, list):
        return [no_dashes(x) for x in obj]
    if isinstance(obj, dict):
        return {k: no_dashes(v) for k, v in obj.items()}
    return obj
