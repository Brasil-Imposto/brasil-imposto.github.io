# Fase 2: arquivo de passagem para a sessão local

Este arquivo existe para que a sessão local continue a Fase 2 se a sessão na nuvem parar no meio (créditos). Ele é atualizado a
cada passo concluído. Issue: #64. Ramo: `docs/phase-2-professionalization`, saindo do `staging`.

## Prompt para colar na sessão local

> Continue a Fase 2 do Brasil·Imposto (issue #64) a partir do ramo `docs/phase-2-professionalization`. Leia primeiro este arquivo,
> `docs/superpowers/plans/BRASIL-IMPOSTO_PLAN_fase-2-handoff_2026-10-24.md`, e siga a seção "Onde parou". A regra do projeto vale:
> nada de código nem workflow antes de a spec ser aprovada pelo mantenedor. A entrega desta etapa é UM pull request de documentos
> para o `staging`, sem merge, com:
> - o relatório `docs/research/BRASIL-IMPOSTO_RESEARCH_fase-2-avaliacao_2026-10-24.md`;
> - a spec `docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_fase-2-profissionalizacao_2026-10-24.md`;
> - este arquivo.
>
> Commits com `git commit -s`; nada de e-mail em nenhum arquivo; nenhum nome de projeto ou empresa de fora do Brasil·Imposto; prosa
> sem travessões. Antes do push, rode `uv run --locked python -m unittest discover -s pipelines/tests` e confira que o ramo saiu do
> `staging` atual (`git fetch origin +refs/heads/staging:refs/remotes/origin/staging`).

## O pedido (resumo)

Elevar o projeto a um padrão profissional sem contradizer a Fase 1:
- auditoria de confiança e spec `BRASIL-IMPOSTO_SPEC_confianca_2026-10-23.md`;
- spec do staging;
- decisões D1 em diante.

As dez partes do pedido do mantenedor (2026-10-24):
1. referências (Home Assistant, VS Code, OpenStreetMap, Bitcoin Core, OpenFisca), comparadas por prática, nunca pelo tamanho da
   comunidade;
2. experiência de quem contribui pela primeira vez;
3. integração entre as páginas (contratos, identificadores, estimado e oficial);
4. automação;
5. segurança e cadeia de fornecimento;
6. governança e tarefas iniciais;
7. documentação para desenvolvedores e para cidadãos;
8. implementação incremental;
9. critérios de sucesso;
10. relatório final, que separa o implementado, o testado, o recomendado e o que depende do mantenedor, mais o roteiro de três meses.

## Onde parou

- [x] Issue #64 aberta; ramo criado do `staging` em `7a239b1`.
- [x] Medir o estado inicial (clone limpo: os construtores rodam em cerca de 20 s, os testes em cerca de 40 s; regras dos ramos e segurança lidas pela API).
- [x] Relatório de avaliação: `docs/research/BRASIL-IMPOSTO_RESEARCH_fase-2-avaliacao_2026-10-24.md`.
- [x] Spec: `docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_fase-2-profissionalizacao_2026-10-24.md` (itens P1 a P8 e as perguntas Q-F2-1 a Q-F2-6).
- [x] Rascunhos das tarefas iniciais: seção 5 da spec (as issues só depois da aprovação).
- [ ] Pull request para o `staging`, sem merge.
