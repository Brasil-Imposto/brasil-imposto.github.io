# Impostos pagos por quem vive em cada estado, 2024: método

**Data:** 2026-09-29
**Usado em:** a coluna amarela ("Pagou") do modal do estado, a partir do round 7 das prévias.

## O que a coluna soma

Os tributos pagos no território do estado em 2024, nas três esferas:

| Esfera | Tributos | Fonte |
|---|---|---|
| União | INSS, imposto de renda (IRPF, IRPJ, IRRF), COFINS e PIS, CSLL, IPI, imposto de importação, IOF, previdência dos servidores federais (PSS), outros (ITR, imposto de exportação, CIDE, demais receitas da Receita) | Receita Federal, arrecadação por estado (`data/uf-balance-2024.json`, campo `federal_revenue.by_tax`) |
| Estado | ICMS, IPVA, ITCD, imposto de renda retido na folha dos servidores estaduais, outros impostos e taxas | Tesouro Nacional, SICONFI, RREO Anexo 3 do governo estadual (`data/state-budgets-2024.json`) |
| Prefeituras | ISS, IPTU, ITBI, imposto de renda retido na folha dos servidores municipais, outras taxas | Tesouro Nacional, SICONFI, RREO Anexo 3 de cada uma das 5.570 prefeituras, somado por estado (`data/municipal-taxes-2024.json`, script `data/scripts/siconfi/build_municipal_taxes.py`) |

Todos os valores são brutos, do ano inteiro (coluna "TOTAL (ÚLTIMOS 12 MESES)" do 6º bimestre), nominais.

## Regras de montagem

1. **Sem dupla contagem entre esferas.** O ICMS e o IPVA entram uma vez, na esfera estadual. A parte que o estado repassa às prefeituras (25% do ICMS, 50% do IPVA) não é somada de novo na esfera municipal: na coluna amarela, o imposto conta onde foi pago, não onde terminou.
2. **Só tributos.** As "receitas administradas por outros órgãos" federais (R$ 106,85 bi no RJ, por exemplo) não são impostos e ficam fora da coluna amarela. Elas continuam no saldo com a União; a nota de rodapé do modal mostra o valor, para que a soma da União na coluna amarela não pareça divergir da barra "Foi para a União".
3. **Do maior para o menor**, com os 9 maiores tributos em cartões e os demais somados em "Demais tributos", que lista os três maiores itens de dentro.
4. **Cobertura municipal declarada.** Uma prefeitura que não enviou o relatório ao Tesouro não entra na soma; o rodapé do modal mostra quantas enviaram.

## Armadilha encontrada na coleta municipal

A primeira coleta pediu só o relatório "RREO" e marcou **2.329 prefeituras como "não enviou"** (MG ficou com 129 de 853). Todas as amostras conferidas tinham enviado, mas o **"RREO Simplificado"**, que os municípios pequenos podem usar. O script agora pede os dois tipos. Lição: um "não encontrado" em massa numa API oficial é primeiro um erro de consulta, depois uma falta de dado.

## Premissa a confirmar

- **Imposto de renda retido pelos governos estaduais e municipais.** A Constituição dá a estados e municípios o IR retido na folha dos seus servidores (CF art. 157, I, e art. 158, I). A premissa desta coluna é que esse valor fica com eles e **não** aparece na arrecadação por estado da Receita Federal, e por isso pode ser somado sem dupla contagem. Não foi encontrado texto oficial da Receita que diga isso de forma explícita. Se a premissa estiver errada, o total pago está superestimado pela soma dessas linhas (em SC, R$ 3,0 bi estaduais mais a parte municipal).

## Ressalvas herdadas

- **Efeito sede:** os tributos federais são contados onde a empresa que paga tem sede, o que aumenta SP, RJ e DF e diminui os demais (ver `BRASIL-IMPOSTO_RESEARCH_dados-por-uf_2026-09-25.md`, seção 6).
- **DF:** não tem prefeituras. Os tributos que nos estados são municipais (ISS, IPTU) ficam na linha "outros impostos e taxas" do próprio DF.
