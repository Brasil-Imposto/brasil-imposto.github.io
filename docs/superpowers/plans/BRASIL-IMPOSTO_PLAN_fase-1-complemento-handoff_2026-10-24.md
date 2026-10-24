# Fase 1, complemento: arquivo de passagem para a sessão local

Issue #66. Ramo `docs/phase-1-complement`, saindo do `staging` em `7a239b1`. A sessão na nuvem está com poucos créditos; este
arquivo diz exatamente o que falta e como continuar.

## Prompt para colar na sessão local

> Continue o complemento da Fase 1 do Brasil·Imposto (issue #66) no ramo `docs/phase-1-complement`. Leia este arquivo inteiro,
> depois a auditoria `docs/research/BRASIL-IMPOSTO_RESEARCH_auditoria-confianca_2026-10-23.md` e a spec
> `docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_confianca_2026-10-23.md`. Não repita o que elas já entregam: complete o que a
> tabela "O que falta" lista.
>
> Primeiro entregue UM pull request de documentos para o `staging`, sem merge, com:
> - o relatório `docs/research/BRASIL-IMPOSTO_RESEARCH_fase-1-complemento_2026-10-24.md`, que cobre os itens 1 a 5;
> - um apêndice de proveniência em JSON ou CSV, um registro por indicador.
>
> Depois, um pull request por teste do item 6. Regras de sempre:
> - confirmar no código, nunca só na documentação;
> - não inventar metadado: escreva "não comprovado" onde faltar;
> - nenhum número publicado muda sem tabela antes e depois e o sim do mantenedor;
> - cada teste com um controle plantado que falha pelo motivo plantado;
> - commits com `-s`, nada de e-mail, nenhum nome de fora do projeto, prosa sem travessões.
>
> Não comece a Fase 2: o pull request #65 espera este complemento.

## O pedido da Fase 1 e o que já existe

O pedido do mantenedor (2026-10-24) pede nove entregáveis. A auditoria de 2026-10-23 (#55) entregou quatro:
- os problemas por gravidade;
- os testes executados;
- as questões abertas;
- o plano.

## O que falta

| # | Entregável | O que fazer | Onde começar |
|---|---|---|---|
| 1 | Arquitetura dos dados | Um desenho do caminho fonte, coleta, bruto, tratado, cálculo, publicado e página, para cada família. As famílias: o mapa federal por UF, a Rede do dinheiro, o DF por região, os 3 Poderes, o Judiciário, o comércio exterior, os casos e Como o dinheiro anda | Seção 2.1 da auditoria; `pipelines/`; `build-standalone-data.py` (lista cada arquivo de `data/` e o script que o faz); `site_chrome.py`; os construtores de página |
| 2 | Proveniência por indicador | Um registro por indicador da tela com os campos do pedido: órgão, URL, base, data da coleta, período, unidade, conversão, cobertura, transformações, fórmula, ausentes, revisões, estimativas, testes, limitações, arquivo, chave e componente. Onde o dado não comprova, escrever "não comprovado" | `data/release-dates.json`; `map-notes-model.js` (as notas do mapa dizem muito do método); `serieslayer.js` (`BIL.federalAt`); `data/series/*.json`; o Judiciário em `docs/research/judiciario-auditoria-2026-10-22/` |
| 3 | DF com alternativas | Para cada ponto do pedido (atribuição da Receita, retenções na fonte, teto pelo PIB, gasto federal no DF, transferências e FCDF, servidores, aposentadorias e benefícios, observado ou estimado, períodos incompletos), dizer o que o código faz hoje, as alternativas e o efeito de cada uma no saldo do DF e no da União | Seção 1 da auditoria (DF-1 a DF-7, recomputação ao centavo em `df_recompute.py`); D146; `BIL.federalAt`; a pergunta DF-5 (PIB de 2023 ou de cada ano). Os efeitos são calculados, nunca estimados de cabeça. Nenhuma mudança na tela neste pull request |
| 4 | Integração das páginas | O que liga de fato o mapa, Os 3 Poderes e Como o dinheiro anda. Por exemplo: a despesa com pessoal da União (RTN, Portal) contra as remunerações individuais (folhas do Judiciário, Câmara, Senado) contra Pessoal pago pela União (`federal_servants`). Dizer o que é comprovável, o que já está contado dentro de outro número e o que precisa de dado novo. Propor contratos e ligações, sem somar remuneração individual a despesa agregada | `data/federal/`; `data/politicians/`; `federal-section.js`; `dinheiro-r1-data.js`; o catálogo de indicadores proposto em P3 da spec da Fase 2 (#65) é um candidato de contrato |
| 5 | Método das contas públicas | Definir, como estão hoje no código, cada métrica: arrecadação atribuída, transferência recebida, despesa territorial, saldo, níveis de governo, período, per capita, juros, dívida, previdência. Mostrar onde uma transferência poderia contar duas vezes e se conta | As notas do mapa em `map-notes-model.js` (o que é "Voltou", o que não tem estado); `docs/research/BRASIL-IMPOSTO_RESEARCH_dados-por-uf_2026-09-25.md`; D-decisões do registro |
| 6 | Testes implementados | A1 (o saldo do DF conferido no `ci`), A4 (as diferenças sem explicação travadas), B1 (os 27 estados e a União no `ci`), depois um teste de dupla contagem entre "Voltou" e as transferências, e um de consistência entre páginas (o mesmo número em duas páginas vem da mesma chave) | Seções A1, A4 e B1 da spec de confiança; `df_recompute.py` (apêndice B da auditoria) |

## Estado

- [x] Lacunas medidas contra a auditoria de 2026-10-23 (esta tabela).
- [x] Issue #66 aberta.
- [x] Relatório do complemento (itens 1 a 5): `docs/research/BRASIL-IMPOSTO_RESEARCH_fase-1-complemento_2026-10-24.md`, com as alternativas do DF calculadas (`df_alternatives.cjs`).
- [x] Apêndice de proveniência: `docs/research/fase-1-complemento-2026-10-24/provenance.json` (13 indicadores).
- [ ] Pull request de documentos para o `staging`, sem merge.
- [ ] Testes do item 6, um pull request cada.
