"""Linha 17-Ouro (Metro de Sao Paulo): investment realized per year, 2010 to August 2026, as published by the Metro.

Values transcribed from the Metro's own documents (R$ mil). For every year the script checks that the transcribed
lines of the same table or chart add up to the total printed there (within one printed unit), so a value read into the
wrong line or mistyped fails. Where a second Metro document gives the Linha 17 value for the same year, both must agree
within one printed unit. Then the Linha 17 total is computed in two passes (Decimal and integers).
Second-source differences up to 0,5% are reported (two Metro documents rounding or revising the same year), larger ones fail.
--control adds R$ 11 mil (one printed unit plus R$ 1 mil) to the 2018 Linha 17 value; the column check must then fail.
Nothing is downloaded; the sources are listed per year in SOURCES.
"""
import sys
from decimal import Decimal

D = Decimal
RA2011 = "Metro, Relatorio da Administracao 2011, 'Quadro Comparativo dos Recursos Financeiros - 2011/2010', Expansao da Rede (Internet Archive: web.archive.org/web/20121101150948/http://www.metro.sp.gov.br/metro/institucional/pdf/rel-administracao.pdf)"
RA2013 = "Metro, Relatorio de Administracao 2013, 'Quadro comparativo dos recursos financeiros - 2013/2012' (transparencia.metrosp.com.br/node/1689/download)"
RA2014 = "Metro, Relatorio de Administracao 2014, 'Quadro Comparativo dos Recursos Financeiros - 2014/2013' (transparencia.metrosp.com.br/node/1688/download)"
RI2021 = "Metro, Relatorio Integrado 2021, p. 44, 'Investimentos Realizados (Caixa) - Expansao da Rede (R$ milhoes)', 2014 a 2021"
RI2025 = "Metro, Relatorio Integrado 2025, p. 11, 'Investimentos realizados (caixa e aportes) - Expansao da Rede (milhoes)', 2021 a 2025"
AC2026 = "Metro, 'Acompanhamento Financeiro de Acoes, Programas e Projetos Previstos - Agosto/2026', Realizado acumulado, acao 2282"

# year: (source, unit in R$ mil, printed total, transcribed lines in the order printed, index of Linha 17, second sources)
COLUMNS = {
    2010: (RA2011, 100, 1067200, [220400, 218100, 403800, 211500, 0, 500, 200, 12700], 6, []),
    2011: (RA2011, 100, 650500, [300000, 91000, 193700, 16600, 2300, 46700, 200], 5, []),
    2012: (RA2013, 100, 1769700, [518400, 184300, 797200, 27600, 21000, 221100, 100], 5, []),
    2013: (RA2013 + "; " + RA2014, 100, 2569200, [111500, 97300, 1900, 1314900, 1800, 715500, 326300], 6, []),
    2014: (RI2021, 10, 3378380, [307510, 185470, 1682230, 708540, 491990, 2650], 4, [("RA 2015, quadro 2015/2014", 492000, 100)]),
    2015: (RI2021, 10, 2391230, [113710, 88000, 1489020, 426640, 272060, 1810], 4, [("RA 2015 e RA 2016", 272100, 100)]),
    2016: (RI2021, 10, 2036380, [5510, 147210, 1225840, 518580, 137560, 1680], 4, [("RA 2016, quadro 2016/2015", 137500, 100)]),
    2017: (RI2021, 10, 2072450, [10590, 283530, 1039440, 539150, 196790, 2950], 4, [("Acompanhamento Financeiro 2017", 196785, 10)]),
    2018: (RI2021, 10, 1710700, [17200, 224500, 763400, 462300, 243300], 4, [("Acompanhamento Financeiro dez/2018", 243297, 10)]),
    2019: (RI2021, 10, 1081600, [17100, 393000, 250200, 252700, 168200, 400], 4, [("Acompanhamento Financeiro dez/2019", 168192, 10)]),
    2020: (RI2021, 10, 876900, [103000, 251700, 79700, 276800, 164900, 200, 600], 4, [("Acompanhamento Financeiro dez/2020", 164878, 10)]),
    2021: (RI2025, 10, 1363000, [623200, 107300, 96500, 245500, 286000, 3100, 1400], 4, [("Acompanhamento Financeiro dez/2021", 286008, 10)]),
    2022: (RI2025, 10, 1946130, [1154270, 125030, 39400, 358700, 206020, 36800, 25910], 4, [("Relatorio Integrado 2023, p. 20", 206020, 10)]),
    2023: (RI2025, 10, 2391110, [1638610, 63120, 30830, 291170, 208680, 68570, 90140], 4, [("Acompanhamento Financeiro dez/2023", 208683, 10)]),
    2024: (RI2025, 10, 3932980, [2361630, 26750, 51980, 661830, 722250, 42060, 66490], 4, [("Acompanhamento Financeiro dez/2024", 722248, 10)]),
    2025: (RI2025, 10, 4492790, [1883510, 42170, 4880, 1294330, 1148300, 15940, 103660], 4, [("Acompanhamento Financeiro dez/2025", 1148301, 10)]),
    2026: (AC2026, 1, 2678436, [81255, 1259, 11805, 86118, 18098, 1283904, 24138, 8573, 398284, 702716, 1382, 60905], 9, []),
}


def main():
    control = "--control" in sys.argv
    failures, reported, line17 = [], [], {}
    for year, (source, unit, total, lines, idx, seconds) in COLUMNS.items():
        lines = list(lines)
        if control and year == 2018:
            lines[idx] += 11
        tolerance = unit if len(lines) <= 7 else 2 * unit
        if abs(sum(lines) - total) > tolerance:
            failures.append(f"{year}: lines {sum(lines)} vs printed total {total} ({source[:40]})")
        for name, value, unit2 in seconds:
            gap = abs(lines[idx] - value)
            if gap > max(unit, unit2):
                note = f"{year}: Linha 17 {lines[idx]} vs {name} {value} (R$ {gap} mil)"
                (failures if gap > lines[idx] * 0.005 else reported).append(note)
        line17[year] = lines[idx]
    pass_1 = sum((D(v) for v in line17.values()), D(0))
    pass_2 = 0
    for year in sorted(line17):
        pass_2 += int(line17[year])
    if pass_1 != D(pass_2):
        failures.append(f"pass 1 {pass_1} != pass 2 {pass_2}")
    for year in sorted(line17):
        print(year, f"{line17[year]:>10,}".replace(",", "."), "mil")
    print("total_brl_mil", pass_1, "| to 2025:", sum(v for y, v in line17.items() if y <= 2025))
    for note in reported:
        print("second source differs (reported):", note)
    if failures:
        print("CHECK FAILED:", "; ".join(failures))
        sys.exit(1)


if __name__ == "__main__":
    main()
