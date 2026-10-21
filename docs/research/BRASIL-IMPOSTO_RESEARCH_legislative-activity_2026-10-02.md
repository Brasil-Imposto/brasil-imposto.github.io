# Atividade legislativa por político (D62): dados para a barra "Influência"

Coleta de 2026-10-02. Relatório em construção: as seções abaixo são preenchidas à medida que a coleta avança.

## Notas de trabalho (rascunho)
- Câmara: arquivos em lote confirmados no swagger (seção Arquivos): `proposicoes-{ano}.csv` e `proposicoesAutores-{ano}.csv`.
  Campos de autoria: `ordemAssinatura` e `proponente` (art. 102 do RICD: proponentes e apoiadores são autores; só o primeiro
  signatário justifica).
- A situação "Arquivada" da Câmara não diz o motivo; o motivo está no despacho (art. 105, art. 133, prejudicialidade, art. 54).
- Senado: `/dadosabertos/processo?codigoParlamentarAutor=` devolve as autorias com `autoria` (texto em ordem), `situacaoAtual`
  e `siglaTipoDeliberacao`; os endpoints `senador/{codigo}/autorias` e `materia/*` estão marcados DEPRECATED.
