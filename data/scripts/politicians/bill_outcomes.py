"""What happened to a bill, from its last official status. Shared by legislative_activity.py (the counts behind the
"Influência" bar, D62) and docs/superpowers/tools/build-tres-poderes-bills.py (each bill on a parliamentarian's sheet),
so both classify every bill the same way."""

OUTCOMES = ["approved", "approved_with_another_bill", "rejected", "vetoed", "prejudged", "withdrawn", "returned_to_author",
            "archived_end_of_term", "archived_reason_not_stated", "in_progress"]

# ---------- Câmara: the last official status of each bill, and for "Arquivada" the reason written in the despacho
APPROVED_SITUATIONS = {"Transformado em Norma Jurídica", "Transformado em nova proposição", "Aguardando Apreciação pelo Senado Federal",
                       "Aguardando Envio ao Senado Federal", "Aguardando Sanção", "Aguardando Autógrafos na Mesa",
                       "Aguardando Apreciação do Veto", "Aguardando Redação Final"}


def camara_outcome(sit, despacho):
    d = despacho.lower()
    if sit in APPROVED_SITUATIONS: return "approved"
    if sit == "Vetado totalmente": return "vetoed"
    if sit == "Retirado pelo(a) Autor(a)": return "withdrawn"
    if sit == "Devolvida ao(à) Autor(a)": return "returned_to_author"
    if sit == "Arquivada":
        if d.startswith("matéria aprovada na forma") or d.startswith("em face da aprovação"): return "approved_with_another_bill"
        if "rejei" in d or "inadequação financeira" in d or "inconstitucionalidade" in d: return "rejected"
        if "prejudic" in d or "desapensação" in d or "art. 163" in d: return "prejudged"
        if "art. 105" in d: return "archived_end_of_term"
        return "archived_reason_not_stated"
    return "in_progress"


# ---------- Senado: the deliberation code and the current situation
DELIB = {"APROVADA_EM_COMISSAO_TERMINATIVA": "approved", "APROVADA_NO_PLENARIO": "approved", "APROVADA_PARCIALMENTE": "approved",
         "APROVADO_NA_INTEGRA": "approved", "APROVADO_PLV": "approved", "TRANSF_PROJ_LEI_SEN": "approved", "REJEITADO_COMISSAO_NAO_TERM": "rejected",
         "REJEITADO_COMISSAO_TERM": "rejected", "REJEITADO_INCONSTICIONALIDADE_CCJ": "rejected", "REJEITADO_PLENARIO": "rejected",
         "REJEITADO_PLENARIO_CD": "rejected", "ARQUIVADO_FIM_LEGISLATURA": "archived_end_of_term", "RETIRADO_PELO_AUTOR": "withdrawn",
         "PREJUDICADO": "prejudged"}


def senado_outcome(x):
    s = (x.get("situacaoAtual") or "").upper()
    if "NORMA JUR" in s: return "approved"
    if x.get("siglaTipoDeliberacao") in DELIB: return DELIB[x["siglaTipoDeliberacao"]]
    return "in_progress" if x.get("tramitando") == "Sim" else "archived_reason_not_stated"
