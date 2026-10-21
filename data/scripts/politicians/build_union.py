"""Gera data/politicians/union.json: Presidente, Vice-Presidente e ministro da area economica, 2019-01-01 ate hoje.

Os fatos (datas, atos, partidos) foram conferidos a mao nas fontes citadas em cada registro; o script
confere os eleitos e o partido na eleicao contra o cadastro do TSE e busca a foto no Wikimedia Commons.
Rodar: POLITICIANS_WORK=/tmp/politicians-work python3 build_union.py
"""
import json
import pathlib

import commons_photos
import tse_common

OUT = pathlib.Path(__file__).resolve().parents[2] / "politicians" / "union.json"
TSE = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_{y}.zip"
CF = "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"
EC111 = "https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc111.htm"
DOU_GUEDES_IN = "https://www.in.gov.br/web/dou/-/decreto-de-1-de-janeiro-de-2019-57510644"
DOU_GUEDES_OUT = "https://www.in.gov.br/web/dou/-/decretos-de-31-de-dezembro-de-2022-455342941"
DOU_HADDAD_IN = "https://www.in.gov.br/web/dou/-/decreto-de-1-de-janeiro-de-2023-455346888"
DOU_HADDAD_OUT = "https://www.in.gov.br/web/dou/-/decretos-de-19-de-marco-de-2026-694021652"
MF_PAGE = "https://www.gov.br/fazenda/pt-br/composicao/ministro"
AB_PSL = "https://agenciabrasil.ebc.com.br/politica/noticia/2019-11/bolsonaro-assinou-carta-de-desfiliacao-do-psl-anuncia-advogada"
AB_PL = "https://agenciabrasil.ebc.com.br/politica/noticia/2021-11/presidente-bolsonaro-assina-filiacao-ao-pl"
AB_ALCKMIN = "https://agenciabrasil.ebc.com.br/politica/noticia/2022-12/conheca-a-trajetoria-politica-de-geraldo-alckmin"
SENADO_MOURAO = "https://legis.senado.leg.br/dadosabertos/senador/6341/filiacoes.json"


def src(fact, url, typ="oficial"):
    return {"fact": fact, "url": url, "type": typ}


def tse_party(year, cargo, urna_name):
    for r in tse_common.iter_rows(year, ufs={"BR"}, cargos={cargo}):
        if r["NM_URNA_CANDIDATO"].upper() == urna_name.upper():
            return r["SG_PARTIDO"], r["NM_CANDIDATO"]
    raise SystemExit(f"TSE {year} {cargo}: {urna_name} nao encontrado entre os eleitos")


def tse_any(year, name_full):
    """Partido numa candidatura (eleito ou nao) de qualquer UF, pelo nome completo."""
    import unicodedata
    norm = lambda s: unicodedata.normalize("NFKD", s.upper()).encode("ascii", "ignore").decode()
    for r in tse_common.iter_rows(year, elected_only=False):
        if norm(r["NM_CANDIDATO"]) == norm(name_full):
            return r["SG_PARTIDO"], r["DS_CARGO"], r["SG_UF"]
    return None


def build():
    p18, bolso = tse_party(2018, "PRESIDENTE", "JAIR BOLSONARO")
    v18, mourao = tse_party(2018, "VICE-PRESIDENTE", "GENERAL MOURÃO")
    p22, lula = tse_party(2022, "PRESIDENTE", "LULA")
    v22, alckmin = tse_party(2022, "VICE-PRESIDENTE", "GERALDO ALCKMIN")
    bolso22 = tse_any(2022, bolso)
    mourao22 = tse_any(2022, mourao)
    alckmin18 = tse_any(2018, alckmin)
    haddad22 = tse_any(2022, "FERNANDO HADDAD")
    assert bolso22 and mourao22 and alckmin18 and haddad22, "candidaturas de conferencia nao encontradas"

    people = {
        "jair-bolsonaro": {"name": "Jair Bolsonaro", "full_name": bolso, "photo_query": "Jair Bolsonaro",
            "party_history": [
                {"party": p18, "start": None, "end": "2019-11-19", "basis": "eleito pelo partido em 2018 (TSE); carta de desfiliacao assinada em 2019-11-19 (Agência Brasil)", "sources": [TSE.format(y=2018), AB_PSL]},
                {"party": None, "label": "sem partido", "start": "2019-11-19", "end": "2021-11-30", "basis": "Agência Brasil, 2021-11-30: 'deixou o partido em novembro de 2019 e não estava filiado a nenhum partido'", "sources": [AB_PL]},
                {"party": bolso22[0], "start": "2021-11-30", "end": None, "basis": "ficha de filiacao assinada em 2021-11-30 (Agência Brasil); candidatura de 2022 pelo mesmo partido (TSE)", "sources": [AB_PL, TSE.format(y=2022)]}],
            "party_sources_note": "A desfiliacao e a filiacao sao datadas pela Agência Brasil (EBC, empresa publica federal), não por registro do TSE: a lista nominal de filiados não é dado aberto."},
        "hamilton-mourao": {"name": "Hamilton Mourão", "full_name": mourao, "photo_query": "Hamilton Mourão",
            "party_history": [
                {"party": v18, "start": None, "end": None, "observed_on": "2018-10-28", "basis": "eleito vice-presidente pelo partido em 2018 (TSE)", "sources": [TSE.format(y=2018)]},
                {"party": mourao22[0], "start": None, "end": None, "observed_on": "2022-10-02", "basis": "candidatura de 2022 (TSE); o Senado registra a filiação na data da eleição, 2022-10-02, não na data da mudança", "sources": [TSE.format(y=2022), SENADO_MOURAO]}],
            "party_sources_note": "Data exata da troca de partido não confirmada em fonte oficial; entre as duas observações, o partido é desconhecido."},
        "lula": {"name": "Luiz Inácio Lula da Silva", "full_name": lula, "photo_query": "Luiz Inácio Lula da Silva",
            "party_history": [{"party": p22, "start": None, "end": None, "observed_on": "2022-10-30", "basis": "eleito pelo partido em 2022 (TSE)", "sources": [TSE.format(y=2022)]}]},
        "geraldo-alckmin": {"name": "Geraldo Alckmin", "full_name": alckmin, "photo_query": "Geraldo Alckmin",
            "party_history": [
                {"party": alckmin18[0], "start": None, "end": None, "observed_on": "2018-10-07", "basis": "candidatura de 2018 (TSE)", "sources": [TSE.format(y=2018)]},
                {"party": v22, "start": None, "end": None, "observed_on": "2022-10-30", "basis": "eleito vice-presidente pelo partido em 2022 (TSE); Agência Brasil: 'ele deixou o PSDB e filiou-se ao Partido Socialista Brasileiro (PSB)', sem data no texto", "sources": [TSE.format(y=2022), AB_ALCKMIN]}],
            "party_sources_note": "Data exata da troca de partido não conferida em fonte oficial."},
        "paulo-guedes": {"name": "Paulo Guedes", "full_name": "Paulo Roberto Nunes Guedes", "photo_query": "Paulo Guedes",
            "party_history": [], "party_null_reason": "nenhuma filiação encontrada nas fontes oficiais consultadas; o cargo de ministro não exige filiação"},
        "fernando-haddad": {"name": "Fernando Haddad", "full_name": "Fernando Haddad", "photo_query": "Fernando Haddad",
            "party_history": [{"party": haddad22[0], "start": None, "end": None, "observed_on": "2022-10-02", "basis": "candidatura de 2022 (TSE)", "sources": [TSE.format(y=2022)]}]},
        "dario-durigan": {"name": "Dario Durigan", "full_name": "Dario Carnevalli Durigan", "photo_query": "Dario Durigan",
            "party_history": [], "party_null_reason": "nenhuma filiação encontrada nas fontes oficiais consultadas; o cargo de ministro não exige filiação"},
    }

    offices = [
        {"office": "Presidente da República", "person_id": "jair-bolsonaro", "kind": "eleito", "start": "2019-01-01", "end": "2023-01-01",
         "start_reason": "posse após a eleição de 2018", "end_reason": "fim do mandato", "party_at_start": p18,
         "sources": [src("eleição e partido", TSE.format(y=2018)), src("início e duração do mandato (art. 82)", CF)]},
        {"office": "Presidente da República", "person_id": "lula", "kind": "eleito", "start": "2023-01-01", "end": None,
         "start_reason": "posse após a eleição de 2022", "end_reason": None, "party_at_start": p22,
         "sources": [src("eleição e partido", TSE.format(y=2022)), src("início do mandato (art. 82)", CF), src("o mandato seguinte começa em 5 de janeiro (EC 111/2021)", EC111)]},
        {"office": "Vice-Presidente da República", "person_id": "hamilton-mourao", "kind": "eleito", "start": "2019-01-01", "end": "2023-01-01",
         "start_reason": "posse após a eleição de 2018", "end_reason": "fim do mandato", "party_at_start": v18,
         "sources": [src("eleição e partido", TSE.format(y=2018)), src("mandato (art. 82)", CF)]},
        {"office": "Vice-Presidente da República", "person_id": "geraldo-alckmin", "kind": "eleito", "start": "2023-01-01", "end": None,
         "start_reason": "posse após a eleição de 2022", "end_reason": None, "party_at_start": v22,
         "sources": [src("eleição e partido", TSE.format(y=2022)), src("mandato (art. 82)", CF)]},
        {"office": "Ministro de Estado da Economia", "person_id": "paulo-guedes", "kind": "nomeado", "start": "2019-01-01", "end": "2023-01-01",
         "start_reason": "nomeação (Decreto de 1º de janeiro de 2019, DOU edição especial)", "end_reason": "exoneração (Decreto de 31 de dezembro de 2022, publicado no DOU de 2023-01-01)", "party_at_start": None,
         "sources": [src("nomeação", DOU_GUEDES_IN), src("exoneração", DOU_GUEDES_OUT)],
         "note": "O decreto de exoneração foi assinado pelo Vice-Presidente 'no exercício do cargo de Presidente da República'. O Ministério da Economia existiu de 2019 a 2022; em 2023 a pasta econômica passou a ser o Ministério da Fazenda."},
        {"office": "Ministro de Estado da Fazenda", "person_id": "fernando-haddad", "kind": "nomeado", "start": "2023-01-01", "end": "2026-03-20",
         "start_reason": "nomeação (Decreto de 1º de janeiro de 2023)", "end_reason": "exoneração a pedido (Decreto de 19 de março de 2026, publicado no DOU de 2026-03-20)", "party_at_start": haddad22[0],
         "sources": [src("nomeação", DOU_HADDAD_IN), src("exoneração", DOU_HADDAD_OUT)]},
        {"office": "Ministro de Estado da Fazenda", "person_id": "dario-durigan", "kind": "nomeado", "start": "2026-03-20", "end": None,
         "start_reason": "nomeação (Decreto de 19 de março de 2026, publicado no DOU de 2026-03-20)", "end_reason": None, "party_at_start": None,
         "sources": [src("nomeação", DOU_HADDAD_OUT), src("ministro atual na página do Ministério da Fazenda (atualizada em 10/04/2026)", MF_PAGE)]},
    ]

    for pid, p in people.items():
        q = p.pop("photo_query")
        ph, why = commons_photos.photo(q) if q else (None, "pessoa sem item no Wikidata com imagem")
        p["photo"] = ph
        if not ph:
            p["photo_null_reason"] = why

    data = {
        "dataset": "union",
        "collected_on": "2026-10-01",
        "period": {"start": "2019-01-01", "end": "2026-10-01"},
        "scope_note": ("Presidente, Vice-Presidente e ministro da área econômica (Economia de 2019 a 2022, Fazenda a partir de 2023). "
                       "start é o dia em que a pessoa assumiu; end é o dia em que deixou o cargo (em geral o mesmo dia em que o sucessor assume); null quando segue no cargo. "
                       "Atos publicados no DOU valem a partir da publicação: a data usada é a da publicação, e a data do decreto fica no texto. "
                       "Substituições curtas (viagens do Presidente, ministro substituto em férias) não entram. "
                       "Partido: observed_on é a data da eleição em que o registro de candidatura do TSE mostra aquele partido; observações datadas (registro de candidatura no TSE) e mudanças com data apenas quando há fonte; o resto fica sem data."),
        "sources": [
            {"name": "TSE, candidaturas 2018 e 2022 (consulta_cand)", "url": TSE.format(y="{2018,2022}")},
            {"name": "Diário Oficial da União (Imprensa Nacional)", "url": "https://www.in.gov.br/"},
            {"name": "Constituição Federal", "url": CF},
            {"name": "Agência Brasil (EBC)", "url": "https://agenciabrasil.ebc.com.br/"},
            {"name": "Wikimedia Commons e Wikidata (fotos)", "url": "https://commons.wikimedia.org/"},
        ],
        "photo_policy": "URL remota do Wikimedia Commons; licença, autor e página do arquivo em cada foto, como o Commons registra.",
        "build_script": "data/scripts/politicians/build_union.py",
        "offices": offices,
        "people": people,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print("ok", OUT, len(offices), "mandatos,", len(people), "pessoas")


if __name__ == "__main__":
    build()
