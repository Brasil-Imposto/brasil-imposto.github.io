"""Transfer classification shared by the series builders. Same rules as pipelines/build.py (2024), made explicit per row.

Recipient rule (build.py): public administration only.
  - "Administração Pública Estadual ou do Distrito Federal" -> state government
  - "Administração Pública Municipal"                        -> municipalities
  - "Administração Pública" (generic), except modality 80 (abroad): modality 3x -> state; otherwise municipalities when the row
    names a municipality, else state
  - "Agentes Intermediários": build.py admitted the two 2024 actions that carry a UF (00VP to the RS state, 00WF to RS
    municipalities). Generalised as: rows WITH a UF and a state (3x) or municipal (4x) modality. In 2024 this selects exactly
    00VP and 00WF. Rows WITHOUT a UF (LC 176 00SE, cessão onerosa 00RX in 2019, LC 173 COVID aid 00S7 in 2020) cannot be
    placed in a UF and are reported as unattributed; LC 176 is replaced by the Tesouro files per UF, as in build.py.
Category rule (build.py CONST map, then function 10/12/08, then other). One addition, documented in the report:
  0E36 = "Complementação da União ao Fundeb" of the Fundeb that ran until 2020 -> fundeb_federal_complement (00SB is the
  same transfer under the Fundeb of EC 108/2020). Without it the 2019 and 2020 complement would fall in education_fnde_and_other.
"""
CONST = {'0044': 'fpe_net_of_fundeb', '0045': 'fpm_net_of_fundeb', '0046': 'ipi_exports_net_of_fundeb', '006M': 'itr_municipal_share_net_of_fundeb',
         '0C33': 'fundeb_retention_on_federal_transfers', '00SB': 'fundeb_federal_complement', '0E36': 'fundeb_federal_complement',
         '0A53': 'oil_gas_royalties', '0547': 'mineral_royalties_cfem', '0546': 'water_resources_compensation', '0223': 'water_resources_compensation',
         '0999': 'cide_fuels_share', '00H6': 'iof_gold', '0369': 'salario_educacao_quotas'}
CATS = ['fpe_net_of_fundeb', 'fpm_net_of_fundeb', 'ipi_exports_net_of_fundeb', 'itr_municipal_share_net_of_fundeb', 'fundeb_retention_on_federal_transfers',
        'fundeb_federal_complement', 'oil_gas_royalties', 'mineral_royalties_cfem', 'water_resources_compensation', 'cide_fuels_share', 'iof_gold',
        'lc176_kandir_compensation', 'salario_educacao_quotas', 'sus_health', 'education_fnde_and_other', 'social_assistance_suas',
        'special_transfers_emendas_pix', 'other_legal_and_voluntary']
UFS = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
STATE, MUNI = 'to_state_government', 'to_municipalities'

def classify(uf, fav, func, acao, modal, mun):
    """Return (sphere, category) for an included row, or (None, reason) for an excluded one."""
    if fav == 'Administração Pública Estadual ou do Distrito Federal': sphere = STATE
    elif fav == 'Administração Pública Municipal': sphere = MUNI
    elif fav == 'Administração Pública' and modal != '80':
        sphere = STATE if modal.startswith('3') else (MUNI if mun == 'MUN' else STATE)
    elif fav == 'Agentes Intermediários' and modal[:1] in ('3', '4'):
        sphere = STATE if modal.startswith('3') else MUNI   # without a UF it is reported below as public_without_uf
    else:
        return None, ('private_or_international:' + fav)
    if uf not in UFS: return None, 'public_without_uf:' + acao
    if acao == '00SE': return None, 'lc176_replaced_by_tesouro'
    if acao in CONST: c = CONST[acao]
    elif acao == '0EC2': c = 'special_transfers_emendas_pix'
    elif func == '10': c = 'sus_health'
    elif func == '12': c = 'education_fnde_and_other'
    elif func == '08': c = 'social_assistance_suas'
    else: c = 'other_legal_and_voluntary'
    return sphere, c

def municipal_government(fav, modal):
    """Transfers to the municipal government (rule of the 2024 municipal balance, pipelines/municipalities/build_municipal_balance.py)."""
    return fav == 'Administração Pública Municipal' or (fav == 'Administração Pública' and modal in ('40', '41'))
