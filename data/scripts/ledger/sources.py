"""The phase-1 sources: where each one lives and what it measures (spec section 9, D121)."""
from datetime import date

FIRST = date(2019, 1, 1)
LAST = date(2026, 8, 1)


def months(first=FIRST, last=LAST):
    out, y, m = [], first.year, first.month
    while (y, m) <= (last.year, last.month):
        out.append(date(y, m, 1))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


RTN = {
    "dataset": "tesouro.rtn.serie_historica",
    "title": "Resultado do Tesouro Nacional (RTN), série histórica, Tabela 1.2 (Governo Central, mensal, R$ milhões correntes)",
    "publisher": "Secretaria do Tesouro Nacional",
    "url": "https://thot-arquivos.tesouro.gov.br/publicacao-anexo/29326",
    "page_url": "https://www.tesourotransparente.gov.br/publicacoes/boletim-resultado-do-tesouro-nacional-rtn/2026/8",
    "published_on": date(2026, 9, 29),
    "published_note": "data da publicação do RTN de agosto de 2026 na página do Tesouro",
    "sheet": "1.2",
}

SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial={first}&dataFinal={last}"
SGS_SOAP = "https://www3.bcb.gov.br/wssgs/services/FachadaWSSGS"
SGS = {  # code -> (line_key, the RTN line it mirrors with the sign flipped, official name)
    4606: ("sgs:4606", "9", "NFSP sem desvalorização cambial - Fluxo mensal corrente - Juros nominais - Total - "
                            "Governo Federal e Banco Central"),
    4639: ("sgs:4639", "8", "NFSP sem desvalorização cambial - Fluxo mensal corrente - Resultado primário - Total - "
                            "Governo Federal e Banco Central"),
    4573: ("sgs:4573", "10", "NFSP sem desvalorização cambial - Fluxo mensal corrente - Resultado nominal - Total - "
                             "Governo Federal e Banco Central"),
}
SGS_UNIT_CENTS = 1_000_000  # the SGS prints R$ milhões with two decimals: one printed unit is R$ 10 mil

DTT_CKAN = "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id=despesas-e-transferencias-totais"
DTT_PAGE = "https://www.tesourotransparente.gov.br/ckan/dataset/despesas-e-transferencias-totais"
DTT_YEARS = tuple(range(FIRST.year, LAST.year + 1))
DTT_INTEREST_GROUP = "2"                 # grupo de natureza de despesa 2: Juros e Encargos da Dívida
DTT_INTERNAL_ACTIONS = {"0669": "bcb"}   # Cobertura do resultado negativo apurado no Banco Central: Tesouro to Banco Central
DTT_INTRA_MODALITY = "91"                # aplicação direta intra-orçamentária: inside the União

RREO_URL = ("https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo?an_exercicio={year}&nr_periodo={bim}"
            "&co_tipo_demonstrativo=RREO&no_anexo=RREO-Anexo%2001&co_esfera=U&id_ente=1")
RREO_PAGE = "https://siconfi.tesouro.gov.br/siconfi/pages/public/consulta_finbra_rreo/finbra_rreo_list.jsf"
RREO_ACCOUNT = "JurosEEncargosDaDivida"
RREO_PAID_COLUMN = "DESPESAS PAGAS ATÉ O BIMESTRE"
RREO_WHOLE_REAIS_UNIT_CENTS = 100   # 2019 to 2023 the RREO prints whole reais: one printed unit is R$ 1 (D122)
RREO_KNOWN_GAPS = {                 # checkpoint -> DTT minus RREO in cents, beyond the RREO's rounding; cause not found (D122)
    date(2023, 10, 1): -96,
    date(2023, 12, 1): -379,
}


def rreo_bimesters():
    for y in range(FIRST.year, LAST.year + 1):
        for b in range(1, (6 if y < LAST.year else LAST.month // 2) + 1):
            yield y, b
