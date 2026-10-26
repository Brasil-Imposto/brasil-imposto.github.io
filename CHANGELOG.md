# Mudanças publicadas

Uma seção por dia com mudanças na produção (`https://brasil-imposto.github.io`), uma linha por tarefa, com o pull request que a
levou para a `main` (D166, D190). A data é a de Brasília. A versão do dia, quando existe, está nas
[versões do GitHub](https://github.com/Brasil-Imposto/brasil-imposto.github.io/releases).

## 2026-10-26

- docs(tools): the review copies carry the decided logo and the site's favicon (#132)
- docs(decisions): the author's answers to round 1 of the open questions (D172 to D182) (#134)
- chore(github): CODEOWNERS names the maintainers team, not a person (D172, question 3) (#135)
- docs(security): who handles each alert and how fast (Phase 2, P8) (#136)
- ci(pages): the data tests and the page check run before production is uploaded (Phase 2, P2) (#137)
- docs(decisions): the cargos filters in a tab, partial data in place, and a preview round for every new design (D183 to D186) (#138)
- docs: round 2 answers and the cargos filters spec, approved (D187 to D191) (#139)
- docs(governance): how a dispute over a number or a reading is settled (Phase 2, P6; D189) (#140)
- ci: weekly dependency updates by Dependabot, into staging (D2) (#141)
- feat(tres-poderes): the cargos filters in a tab with a drawer (spec filtros-cargos, D187) (#142)
- docs(release): one release per production day and CHANGELOG.md (trust spec G3, D190) (#143)
- feat(site): the money network preview leaves production and stays in staging (Q-A2, D172) (#144)

## 2026-10-25

- ci(pages): actions pinned by commit and Pages writes only in deploy (D1) (#105)
- feat(apoie): the contact form on, with the maintainer's Web3Forms key (D168) (#99)
- refactor(data): the last three source ids of release-dates.json in English (#8) (#101)
- docs: production receives one approved task at a time (D166) (#100)
- test(data): the unexplained differences listed and locked (A4, #66) (#102)
- docs(decisions): publish D166 to D171 and the answered questions (#103)
- docs: a developer guide and one command that checks what the ci checks (P1, F1) (#104)
- test(data): the divisions of "Como o dinheiro anda" add up (B4) (#106)
- test(data): every state and the União block checked to the cent (B1, #66) (#107)
- test(docs): every decision cited in specs, data and code is in the public record (G1) (#108)
- test(data): no money counted twice between "Voltou" and the spending (#66) (#109)
- docs(learn): per-task promotion, trust tests and closing, from the session of 2026-10-24 and 25 (#113)
- docs(readme): the test site is rebuilt by the maintainer until its deploy is automatic (#115)

## 2026-10-24

- release: 2026-10-24 (#60)
- docs(research): phase 1 complement, provenance, accounts method, DF alternatives and page links (#66) (#71)
- test(df): the DF balance checked to the cent on every period of the selector (A1) (#74)
- docs(agents): antes de começar, conferir se a tarefa já tem dono (#76)
- docs(contributing): antes de começar, conferir se a tarefa já tem dono (#77)
- docs(learn): polish: publish D155 to D165 and Q81 to Q86, restore four lost decisions (#78)
- docs: phase 2 assessment and spec, the project as professional open source (#64) (#79)
- docs(learn): staging, promotion and production checks of 2026-10-23 and 24 (#80)

## 2026-10-23

- docs(spec): staging environment and feature switches (#47)
- feat(site): the Apoie button and its modal, built switched off (#46)
- docs(spec): a shorter Início, with the trade section only in staging (#48)
- docs: consistency audit, part 1, with cleanup tasks 6 and 7 (#45)
- Apoie no ar: os canais "Em breve" e o formulário de contato pelo Web3Forms (#49)
- fix(site): every link to Início goes to the site's root, and the old address forwards there (#51)
- docs(plan): close phase 1 of the cleanup audit (task 8) (#53)
- feat(site): the Apoie button on in production, the form when the key arrives (#54)
- feat(site): staging and production profiles, with the feature switches (#52)

## 2026-10-22

- docs(spec): propose the Astro phase B0 section for approval (#18)
- fix(site): remove the design-round notes from Os 3 Poderes and Como o dinheiro anda (#20)
- ci(pages): publish only the three site pages (#21)
- docs: approve phase B0 with the recommended answers (D150, D151) (#22)
- docs(spec): one header, a footer and a real-progress map loader (D152) (#24)
- refactor: move data/scripts to pipelines/ and add the ci workflow (#23)
- build: manage Python with uv (pyproject.toml, uv.lock, Python 3.12) (#25)
- refactor: give pipelines and data files English names (#26)
- feat(site): one fixed header for the three published pages (#27)
- feat(site): one footer for the three published pages (#28)
- docs(learn): GitHub publication, the cloud session and the logo rules (#29)
- docs(learn): polish: current state in the decision log and spec status lines (#30)
- feat(site): map loader with the true download percentage (L1) (#31)
- docs(data): inventory of the English names for data/ keys, with a proven rename tool (#32)
- docs(data): complete the keys inventory as #32 describes (#33)
- feat(data): JSON Schemas and the per-entity export, generated at build time (#34)
- feat(site): Astro 7 skeleton with types generated from the schemas (#35)
- docs(judiciary): audit of STF pay on Os 3 Poderes and the data spec (#36)
- feat(site): the logo in the header and footer, and the tab icons (D153) (#37)
- docs(decisions): judiciary data spec approved with every recommendation (D154) (#38)
- docs(decisions): publish the logo decision (D153) and Q80 (#39)
- feat(judiciary): STF averages, dates and payroll zeros as the approved spec reads them (D154) (#40)
- feat(judiciary): STJ, TST, STM and TSE on the same rules as the STF (D154) (#41)
- feat(site): the social preview image and its tags (D153) (#42)
- docs: README with the logo and screenshots; the rules on the organization page (#44)
- fix(site): overlays above the header and jumps below it on the three pages (#43)
