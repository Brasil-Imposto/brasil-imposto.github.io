# Brasil-Imposto: padrões de colaboração em código aberto

Pesquisa de 2026-10-01 para decidir o modelo de colaboração do repositório no primeiro lançamento público (README D2, grill
GD1). Pedido do autor: *"faça uma pesquisa e encontre os melhores padrões e mais modernos mundialmente de colaboração em código
aberto do mundo (talvez o bitcoin e cripto no geral tenham bons exemplos - faça uma pesquisa profunda e encontre os melhores
exemplos)"*.

**Restrições já decididas, que esta pesquisa não reabre:** só o autor aprova Pull Requests no início (D2); AGPL-3.0 no código e
CC BY 4.0 nos dados e textos; nenhum número sem fonte oficial com link, ano de referência e data da coleta; neutralidade
partidária (GD10, GD17).

**Método.** Cada afirmação abaixo vem de uma página oficial aberta nesta sessão (arquivo bruto do repositório no GitHub, wiki ou
documentação do próprio projeto), com o link ao lado. O que não consegui abrir está na seção "Não consegui confirmar". Data de
todas as coletas: 2026-10-01.

**Passagem pelos registros antes de pesquisar.** O `README.md` (D2, Q5, Q6), o grill (GD1, G14, G17, G19, G20) e
`docs/ai/learned-patterns.md` não têm nenhuma decisão sobre o fluxo de colaboração além de D2 e das licenças; G14, G17, G19 e G20
seguem abertos e esta pesquisa serve a eles.

---

## 1. Governança: como se decide e como alguém vira mantenedor

### Bitcoin Core
- **Não existe "desenvolvedor do Bitcoin Core" privilegiado.** O CONTRIBUTING diz que não há "particular concept of Bitcoin
  Core developers in the sense of privileged people", mas que "some hierarchy is necessary for practical purposes": os
  mantenedores do repositório fazem o merge, o ciclo de versões e a moderação.
  ([CONTRIBUTING.md](https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md))
- **Quem decide o merge:** "Whether a pull request is merged into Bitcoin Core rests with the project merge maintainers", que
  julgam se o patch segue os princípios do projeto, se atende o padrão mínimo e "the general consensus of contributors".
  Todo PR precisa ter caso de uso claro, ser "well peer-reviewed", ter testes e não quebrar a suíte. (mesmo arquivo)
- **Revisão com vocabulário fixo (a cultura ACK/NACK).** `Concept ACK/NACK` (concordo ou não com o objetivo), `Approach
  ACK/NACK` (concordo com o objetivo, não com o jeito), e `ACK <commit>` seguido de como a revisão foi feita ("I have tested
  the code" ou "I have not tested the code, but I have reviewed it"). "A NACK needs to include a rationale... NACKs without
  accompanying reasoning may be disregarded." O mantenedor pode pesar a opinião de revisores com mais histórico. (mesmo
  arquivo, seção "Peer Review")
- **Revisar é a porta de entrada:** "In-depth reviewing and testing are the bottleneck of the project, and are the most
  effective way anyone can start to contribute." (mesmo arquivo)
- **Política de IA (nova):** IA como ferramenta é bem-vinda, mas "Pull requests should not be opened or driven by autonomous
  agents", comentários a mantenedores devem ser escritos por humanos e o autor tem de saber explicar o PR com as próprias
  palavras. Adaptada das políticas do ripgrep e do uv. ([doc/AI_POLICY.md](https://github.com/bitcoin/bitcoin/blob/master/doc/AI_POLICY.md))
- **Mudanças de protocolo vão por BIP.** O BIP 3 (status Deployed, substitui o BIP 2) reduziu os status de nove para quatro
  (Draft, Complete, Deployed, Closed). Pontos úteis: a ideia é discutida publicamente na lista antes de qualquer PR ("Authors
  should avoid opening a pull request with a BIP draft out of the blue"); os editores fazem só o trabalho editorial e "do NOT
  evaluate whether the proposal is likely to be adopted"; "No formal or informal decision body governs Bitcoin development
  or decides adoption of BIPs"; a seção Changelog registra mudanças depois de Complete.
  ([bip-0003.md](https://github.com/bitcoin/bips/blob/master/bip-0003.md))

### Ethereum (EIPs)
- O EIP-1 descende do BIP-1, que descende do PEP-1 (o próprio EIP-1 diz que "In many places text was simply copied").
  ([EIP-1](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1.md))
- **Ciclo com prazos explícitos:** Idea (fora do repositório, no fórum Ethereum Magicians), Draft, Review, **Last Call** (janela
  final de revisão com data de fim, "typically 14 days later"), Final, Stagnant (6 meses sem atividade), Withdrawn, Living.
- **Editores não julgam mérito:** "The editors don't pass judgment on EIPs. We merely do the administrative & editorial part."
- **Seção de segurança obrigatória:** "EIP submissions missing the 'Security Considerations' section will be rejected."
- **Links externos restritos:** "links to external resources SHOULD NOT be included. External resources may disappear, move, or
  change unexpectedly", com exceções listadas por padrão de URL (EIP-5757). Lição direta para um projeto de dados cujas fontes
  são sites de governo que mudam de endereço.
- O próprio EIP-1 avisa um limite: o processo "were not designed to address contentious non-technical issues, but... often end
  up entangled in them".

### Rust (RFCs e times)
- **Quando precisa de RFC:** mudanças "substantial"; não precisam "Rephrasing, reorganizing, refactoring" nem "Additions that
  strictly improve objective, numerical quality criteria". Um PR de recurso novo sem RFC "may be closed with a polite request
  to submit an RFC first". ([rust-lang/rfcs README](https://github.com/rust-lang/rfcs/blob/master/README.md))
- **Final Comment Period (FCP):** um membro do time propõe a disposição (merge, close ou postpone) com um *summary comment*;
  todos os membros do time precisam assinar; o FCP dura **dez dias corridos** e é anunciado no This Week in Rust "so that all
  stakeholders have a chance to lodge any final objections". Não exige consenso de todos no tópico, mas não pode haver
  "strong consensus *against*" fora do time. (mesmo arquivo)
- **Conselho de Liderança (RFC 3392):** um representante por time de topo, mandato de um ano, limite flexível de três mandatos,
  troca de metade em março e metade em setembro, decisão por consentimento. **Limite por empresa:** com 5 ou menos
  representantes, no máximo 1 com a mesma afiliação; com 6 ou mais, no máximo 2; afiliação é tirar "a substantive fraction of
  their income" da entidade (empregador, cliente ou "major sponsor"), com dever de declarar mudanças.
  ([RFC 3392](https://github.com/rust-lang/rfcs/blob/master/text/3392-leadership-council.md))

### Linux (hierarquia de mantenedores e DCO)
- **Cadeia de confiança:** o código é dividido em subsistemas, cada um com mantenedor que é "gatekeeper"; na janela de merge os
  mantenedores de topo pedem ao Linus que puxe as árvores deles, e "Linus trusts the subsystem maintainers to not send bad
  patches upstream". A cadeia "rarely exceeds two or three links".
  ([Documentation/process/2.Process.rst](https://github.com/torvalds/linux/blob/master/Documentation/process/2.Process.rst))
- **Arquivo MAINTAINERS:** cada área lista M (mantenedor), R (revisor designado), L (lista), **S (status: Supported, Maintained,
  Odd Fixes, Orphan, Obsolete)** e F (padrões de arquivo). O status "Orphan" convida quem chega: "maybe you could take the role
  as you write your new code". ([MAINTAINERS](https://github.com/torvalds/linux/blob/master/MAINTAINERS))
- **DCO:** ver a seção 2.

### Kubernetes (OWNERS e SIGs)
- **Arquivos OWNERS por pasta:** `approvers` (podem dar `/approve`), `reviewers` (bons candidatos a `/lgtm`), `labels` aplicados
  automaticamente e `emeritus_approvers` para quem parou de aprovar. O robô (Prow) atribui revisores pela pasta tocada.
  ([contributors/guide/owners.md](https://github.com/kubernetes/community/blob/master/contributors/guide/owners.md))
- **Escada de papéis com critério numérico** ([community-membership.md](https://github.com/kubernetes/community/blob/master/community-membership.md)):

  | Papel | Requisitos publicados |
  |---|---|
  | Member | 2FA ligado; várias contribuições, ao menos um PR com merge; patrocinado por 2 revisores **de empresas diferentes** |
  | Reviewer | Member há 3 meses; revisor principal de 5 PRs; revisou ou fez merge de 20 PRs; patrocinado por um approver, sem objeção dos outros |
  | Approver | Reviewer há 3 meses; revisor principal de 10 PRs; 30 PRs revisados; indicado pelo dono do subprojeto, por PR no OWNERS |

- O status de revisor e de approver vale **só para uma parte do código** ("scoped to a part of the codebase").

### Python (PEPs e Steering Council)
- **BDFL até 2018, conselho depois:** "Guido van Rossum... served as its Benevolent Dictator for Life (BDFL) from inception until
  July 2018"; o PEP 13 (criado em 16/12/2018) instituiu um conselho de 5 pessoas eleito pelo core team, que deve usar os poderes
  "as little as possible". Quem tem conflito de interesse num voto "must abstain". **No máximo 2 dos 5 podem trabalhar para o
  mesmo empregador.** Existe voto de desconfiança. ([PEP 13](https://peps.python.org/pep-0013/))
- **Como alguém entra no core team:** contribuições consistentes "without requiring extensive rewrites"; um membro oferece
  mentoria, abre uma votação de 7 dias e precisa de dois terços de votos positivos; o conselho só pode vetar.
  ([devguide, join-team](https://github.com/python/devguide/blob/main/core-team/join-team.rst))
- **PEP 1:** todo PEP tem um *champion* que testa a ideia no Discourse antes de escrever; quem não é do core precisa de um
  *sponsor*. ([PEP 1](https://peps.python.org/pep-0001/))

### O que serve para um projeto pequeno, com um mantenedor só no início

| Padrão | Serve agora? | Por quê |
|---|---|---|
| BDFL declarado, com plano de transição escrito (Python antes de 2018, PEP 13 depois) | **Sim** | É exatamente D2. Escrever desde o dia 1 o gatilho e o formato da transição evita que a passagem vire crise. |
| Mantenedores julgam consenso, não votam (Bitcoin Core) | **Sim** | Com um mantenedor, a regra "decido, mas explico o motivo por escrito no PR" é o que dá legitimidade. |
| Vocabulário de revisão Concept, Approach e ACK com o commit (Bitcoin Core) | **Sim** | Barato, deixa a revisão auditável e convida quem não escreve código a revisar fontes. |
| Proposta escrita antes de código para mudança grande (BIP, EIP, RFC, PEP) | **Sim, leve** | Uma issue com modelo "Proposta" basta; RFC em repositório separado é pesado demais. |
| Janela final de comentário com prazo (FCP de 10 dias do Rust, Last Call de 14 dias do EIP) | **Sim** | Para mudança de método (como se conta um número no mapa), anunciar e esperar 7 a 10 dias protege contra acusação de mudança às escuras. |
| Escada de papéis com critério numérico e escopo por pasta (Kubernetes) | **Mais tarde** | Escrever os critérios já, aplicar quando houver 3 ou mais contribuidores recorrentes. |
| Arquivo de mantenedores com status por área (Linux S: Orphan, Maintained) | **Sim** | Mostra a quem chega quais estados e quais dados não têm dono. |
| Limite de afiliação no corpo de mantenedores (Rust RFC 3392, PEP 13) | **Sim, adaptado** | Trocar "empresa" por "partido": base concreta para a neutralidade quando entrarem novos mantenedores. |
| Conselho eleito, votos, SIGs (Python, Kubernetes, Rust) | **Não agora** | Exige gente que ainda não existe. |

---

## 2. Fluxo de contribuição de código

### O que as referências fazem
- **Todo mundo entra por PR, sem exceção (Bitcoin Core).** "everyone without exception contributes patch proposals using pull
  requests". O autor do PR precisa ter testado e dizer quais testes cobrem a mudança; commits atômicos, cada um compilando
  sozinho; título com o prefixo da área (`consensus:`, `doc:`, `test:`...); o corpo explica o porquê; PR focado ("a feature, fix
  a bug, or refactor code; but not a mixture"); quem propõe recurso novo deve se dispor a mantê-lo, senão "they may be removed".
  ([CONTRIBUTING.md](https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md))
- **Histórico auditável (Bitcoin Core).** Mudança de código só em commits que não são de merge; "Merge commits should be signed,
  and the resulting git tree hash must be deterministic and reproducible", conferido pelo script `contrib/verify-commits`, que
  checa as assinaturas contra uma lista de chaves confiáveis (`trusted-keys`) a partir de um commit raiz. Aviso do próprio
  README: "you can't use an untrusted script to verify itself".
  ([contrib/verify-commits](https://github.com/bitcoin/bitcoin/blob/master/contrib/verify-commits/README.md))
- **Builds reproduzíveis (Bitcoin Core com Guix).** O objetivo é "audit and reproduce our toolchain instead of blindly trusting
  binary downloads". Várias pessoas compilam a mesma versão e publicam as assinaturas do resultado no repositório `guix.sigs`;
  qualquer um verifica com `guix-verify` "after at least one other signer has uploaded their signatures". Exige 16 GB livres e
  mais 8 GB por plataforma. ([contrib/guix/README.md](https://github.com/bitcoin/bitcoin/blob/master/contrib/guix/README.md))
- **DCO (Linux).** Cada commit leva `Signed-off-by: Nome <email>` (feito por `git commit -s`), que certifica os itens (a) a (d) do
  Developer Certificate of Origin 1.1: escrevi ou tenho direito de enviar sob a licença do arquivo, e sei que o registro é
  público e permanente. O kernel pede "a known identity (sorry, no anonymous contributions.)". Outras etiquetas: `Acked-by`,
  `Reviewed-by`, `Co-developed-by`.
  ([submitting-patches.rst](https://github.com/torvalds/linux/blob/master/Documentation/process/submitting-patches.rst),
  [developercertificate.org](https://developercertificate.org/))
- **DCO contra CLA.** O Bitcoin Core não usa CLA: "By contributing to this repository, you agree to license your work under the
  MIT license" (a contribuição entra com a mesma licença com que o projeto sai). O GitLab trocou o CLA pelo DCO em 2017 a pedido
  de desenvolvedores do Debian: o CLA "is unpopular with developers, who don't want to enter into legal terms... and potentially
  give up some of their rights", e o DCO "gives developers greater flexibility and portability for their contributions".
  ([blog do GitLab](https://about.gitlab.com/blog/gitlab-switches-to-dco-license/))
- **Política de IA (Bitcoin Core, 2026):** ver seção 1. Relevante porque o próprio Brasil-Imposto é construído com agentes.

### O que o GitHub oferece de graça num repositório público
| Recurso | Disponível no plano gratuito? | Fonte |
|---|---|---|
| Rulesets (proteção de branch nova): exigir PR, exigir checks verdes, exigir commits assinados, histórico linear, bloquear exclusão e force push | Sim, em repositório público | [about-rulesets](https://github.com/github/docs/blob/main/content/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets.md), [regras](https://github.com/github/docs/blob/main/content/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets.md), [disponibilidade](https://github.com/github/docs/blob/main/data/reusables/gated-features/repo-rules.md) |
| CODEOWNERS (dono por pasta, revisão obrigatória do dono) | Sim, em repositório público; o dono precisa ter permissão de escrita | [about-code-owners](https://github.com/github/docs/blob/main/content/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners.md) |
| Sign-off obrigatório nos commits feitos pela interface web | Sim; pela linha de comando o autor usa `--signoff` | [commit signoff policy](https://github.com/github/docs/blob/main/content/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-the-commit-signoff-policy-for-your-repository.md) |
| App DCO (bloqueia o PR se faltar `Signed-off-by` com o email do autor) | Sim, app de código aberto (licença ISC) | [dcoapp/app](https://github.com/dcoapp/app) |
| Assinatura de commit (GPG, SSH ou S/MIME, selo "Verified") | Sim | [commit signature verification](https://github.com/github/docs/blob/main/content/authentication/managing-commit-signature-verification/about-commit-signature-verification.md) |
| GitHub Actions (CI) | Grátis em repositório público com os runners padrão | [billing de Actions](https://github.com/github/docs/blob/main/content/billing/concepts/product-billing/github-actions.md) |
| Artifact attestations (prova de onde e como o artefato foi gerado; SLSA Build Level 2) | Sim; em repositório público vão para o log de transparência público do Sigstore | [artifact attestations](https://github.com/github/docs/blob/main/content/actions/concepts/security/artifact-attestations.md) |
| OpenSSF Scorecard (nota pública de práticas: Branch-Protection, Code-Review, Signed-Releases, Security-Policy, Pinned-Dependencies...) | Sim, como GitHub Action | [ossf/scorecard](https://github.com/ossf/scorecard) |

**Armadilha de quem mantém sozinho.** Com revisão obrigatória, só conta a aprovação de quem tem permissão de escrita, e ninguém
aprova o próprio PR. Se a regra exigir 1 aprovação enquanto o autor é o único mantenedor, os PRs dele próprio só passam com
bypass, que fica visível apenas nas configurações (Rule Insights), não para o público. A saída limpa: **exigir PR com 0
aprovações e checks verdes** enquanto houver um mantenedor (PRs de fora continuam dependendo do autor, o único que pode fazer
merge), e subir para 1 aprovação de outra pessoa no dia em que entrar o segundo mantenedor. O GitHub também oferece "approval
from someone other than the last person to push", útil a partir daí.

### O que serve para o Brasil-Imposto
| Padrão | Recomendação | Motivo |
|---|---|---|
| Tudo por PR, inclusive o autor | **Adotar já** | Cada mudança de número fica com um registro público (o PR) com o porquê; é a base da defesa contra acusação de manipulação. |
| DCO com `Signed-off-by` e o app DCO | **Adotar já, no lugar de CLA** | Com AGPL-3.0 e CC BY 4.0, a contribuição entra com a mesma licença com que sai. Um CLA daria ao autor o poder de relicenciar, o que num projeto cívico vira suspeita. |
| Identidade conhecida (Linux) | **Adaptar** | Para dados públicos e politicamente sensíveis, aceitar pseudônimo estável (a conta do GitHub) com email válido, e dizer isso no CONTRIBUTING. Exigir nome civil pode afastar servidor público que conhece o dado. Ponto para o autor decidir. |
| Commits assinados obrigatórios | **Só para o mantenedor no começo** | O autor assina os commits dele e os de merge (padrão do Bitcoin Core para merges); exigir de todos trava quem chega. |
| Build reproduzível com Guix | **Não** | Feito para binários que guardam dinheiro. O equivalente aqui é **dado reproduzível**: os scripts de `data/scripts/` já reproduzem os JSON byte a byte (README); o CI roda os scripts e compara o hash. |
| Artifact attestation do pacote de dados publicado | **Depois do lançamento** | Barato e grátis; prova que o `bi-data.js` publicado saiu daquele commit, por aquele workflow. |
| Scorecard | **Adotar já** | Uma Action; a nota pública mostra ao visitante que o repositório segue boas práticas. |
| Política de IA (Bitcoin Core) | **Adotar, adaptada** | O projeto é feito com agentes: aceitar código gerado com IA, mas o humano responde pelo PR e pela fonte de cada número. |

---

## 3. Contribuição de DADOS com proveniência

### Wikipedia: verificabilidade e ônus da prova
- "each fact or claim must be attributable to reliable, published sources"; o que for contestado ou provável de ser contestado
  precisa de citação na linha, a uma fonte que "directly supports" o texto. **"The burden to demonstrate verifiability lies with
  the editor who adds or restores material."** Sem fonte, "may be removed" e não volta sem citação. Material polêmico sem fonte
  sobre pessoas vivas sai na hora. O limiar histórico: "verifiability, not truth".
  ([WP:V](https://en.wikipedia.org/wiki/Wikipedia:Verifiability); na versão em português, "O ónus da prova reside nos editores que
  introduziram determinada informação", [WP:V pt](https://pt.wikipedia.org/wiki/Wikip%C3%A9dia:Verificabilidade))
- **Revisão passo a passo, sem apagar no ato:** marcar `{{citation needed}}`, `{{verification needed}}` ou `{{failed
  verification}}`, explicar o motivo, e não concentrar remoções "only on material of a particular point of view". (WP:V)
- **Neutralidade:** "Articles must not take sides, but should explain the sides, fairly and without editorial bias. This applies
  to both what you say and how you say it." ([WP:NPOV](https://en.wikipedia.org/wiki/Wikipedia:Neutral_point_of_view))
- **Link morto:** "URLs have a median lifespan of about one year"; a orientação é guardar `archive-url` e `archive-date` (Internet
  Archive) e `access-date` em cada citação. ([WP:Link rot](https://en.wikipedia.org/wiki/Wikipedia:Link_rot))

### OpenStreetMap: licença da fonte, verificabilidade e importação planejada
- **Fonte com licença incompatível é proibida:** "Do not use data from copyrighted maps or any other proprietary data!"
  ([Copyright](https://wiki.openstreetmap.org/wiki/Copyright))
- **Verificável quer dizer reproduzível:** um dado é verificável "if and only if independent users observing the same feature
  would make the same observation every time". ([Verifiability](https://wiki.openstreetmap.org/wiki/Verifiability))
- **A fonte vai no conjunto de mudanças, não no objeto:** a chave `source` "should typically be added... to the changeset when a
  change is made"; e "limit your modifications thematically by the source you use so as to unambiguously attribute the source
  data, and allow validation". ([Key:source](https://wiki.openstreetmap.org/wiki/Key:source))
- **Importação em massa tem rito próprio:** plano escrito na wiki, licença conferida ("If the license of the data is not
  compatible with the... ODbL, you can not use the data"), discussão com a comunidade local e no fórum com modelo de post,
  conta dedicada `<usuario>_Import`, e o importador "must not claim an additional copyright".
  ([Import/Guidelines](https://wiki.openstreetmap.org/wiki/Import/Guidelines))

### Querido Diário (Open Knowledge Brasil)
- Repositório ativo (último push em 2026-09-23, licença MIT, conferido na API do GitHub).
- **Checklist obrigatório no PR de dados:** o modelo de PR exige marcar cada item e "Caso algum item não seja marcado, JUSTIFIQUE o
  motivo": atributos obrigatórios, `start_date` igual à edição mais antiga do site, e **três coletas de teste com os `.log` e `.csv`
  anexados** (última edição, intervalo arbitrário, coleta completa), além de abrir alguns diários coletados e conferir.
  ([pull_request_template.md](https://github.com/okfn-brasil/querido-diario/blob/main/.github/pull_request_template.md))
- **Revisor confere a checklist, não confia nela:** "É esperado que a pessoa contribuidora faça todas as verificações contidas na
  checklist, mas também é responsabilidade da pessoa revisora conferir os itens."
  ([docs/CONTRIBUTING.md](https://github.com/okfn-brasil/querido-diario/blob/main/docs/CONTRIBUTING.md))
- **Prioridades públicas e trilha de dificuldade:** tabela de prioridade (1 manutenção do que está no ar, 2 pedidos de parceiros,
  ... 8 sem meta), rótulos `dificuldade:baixa/media/alta`, `good first issue` para "município replicado" (pede de 5 a 10
  municípios por PR para valer a revisão), um esquema para validar os dados de coleta e um quadro público de expansão de cidades.
  (mesmo arquivo)

### Operação Serenata de Amor (Open Knowledge Brasil)
- Repositório sem push desde 2024-01-31 (API do GitHub). O README diz com franqueza: "we have no public roadmap, barely an internal
  one"; a IA (Rosie) aponta gastos suspeitos da cota parlamentar e o site (Jarbas) é "the starting point to validate a
  suspicion". Comunidade técnica no Telegram com "700+ members"; financiamento coletivo no Catarse em 2016 e botão de doação no
  apoia.se. ([README](https://github.com/okfn-brasil/serenata-de-amor/blob/main/README.md),
  [CONTRIBUTING](https://github.com/okfn-brasil/serenata-de-amor/blob/main/CONTRIBUTING.md))
- Lição para o Brasil-Imposto: o achado automático é chamado de "suspeita" a validar, nunca de conclusão; e sem roadmap público a
  contribuição dependeu do núcleo e parou com ele.

### Brasil.io e o mutirão da COVID-19
- Brasil.io: "libertação de dados" (coleta, limpeza e enriquecimento automatizados) e ativismo com a LAI; GPL-3.0; doações no
  apoia.se; sugestão de dataset por formulário. ([README](https://github.com/turicas/brasil.io/blob/develop/README.md))
- **O exemplo brasileiro mais próximo do Brasil-Imposto:** o `covid19-br` juntou voluntários para transcrever boletins das
  secretarias estaduais. A cada atualização o voluntário tinha de "informar a data de referência dos dados; anexar a planilha
  preenchida; informar o(s) link(s) onde as informações foram obtidas; informar observações relevantes". A linha `TOTAL NO
  ESTADO` "deve ser preenchida sempre com o total informado pela SES (e não pela soma dos municípios)", o que deixa a soma dos
  municípios conferível contra o total oficial. Coordenadores por região "cobrar as checagens". Os dados seguem Data Package e
  Table Schema e são validados por máquina (`goodtables data/datapackage.json`). Licença dos dados CC BY-SA 4.0, com a forma de
  citar: "Fonte: Secretarias de Saúde das Unidades Federativas, dados tratados por...".
  ([README](https://github.com/turicas/covid19-br/blob/master/README.md),
  [CONTRIBUTING](https://github.com/turicas/covid19-br/blob/master/CONTRIBUTING.md))

### Base dos Dados
- **Fonte original é campo obrigatório** no formulário de issue de nova base (`required: true`).
  ([new-data.yml](https://github.com/basedosdados/pipelines/blob/main/.github/ISSUE_TEMPLATE/new-data.yml))
- **Estrutura antes do código:** "Tabelas de arquitetura" (nome, ordem, metadados e unidade de medida de cada variável) são
  validadas pela equipe antes de escrever a captura; depois, código de captura e limpeza, testes no dbt, e PR com o rótulo
  `table-approve` para a equipe de dados revisar "dados e metadados"; no merge, publicação automática.
  ([colab_data](https://github.com/basedosdados/website/blob/main/next/content/docs/pt/colab_data.md))

### mySociety (TheyWorkForYou) e OpenSpending
- **TheyWorkForYou separa o coletor do site:** o ParlParse baixa o Hansard (registro oficial do Parlamento), "stores it as an HTML
  file for each day" e gera XML; erros do próprio registro oficial são corrigidos por um pré-processador que "applies patches to
  Hansard to fix uncommon errors" com `patch` e `diff`: a correção fica visível e versionada, separada do bruto.
  ([parser](https://parser.theyworkforyou.com/parser.html), [README](https://github.com/mysociety/theyworkforyou))
- **OpenSpending** começou como "Where does my money go" (finanças do Reino Unido), o mesmo propósito do Brasil-Imposto; virou uma
  plataforma de microsserviços em 8 repositórios, e o repositório central não recebe push desde 2020-07-30 (API do GitHub).
  Deixou o padrão Fiscal Data Package ("a lightweight and user-oriented format for publishing and consuming fiscal data", com
  uma taxonomia de orçamento). ([README](https://github.com/openspending/openspending),
  [fiscal.datapackage.org](https://fiscal.datapackage.org/))
- **Data Package (Frictionless):** a propriedade `sources` "MUST be an array of Source objects", cada um com `title` e `path`
  (URL). ([datapackage.org](https://datapackage.org/standard/data-package/))

### Como cada um impede número sem fonte

| Projeto | Onde a fonte fica | Quem confere | Barreira automática |
|---|---|---|---|
| Wikipedia | Citação na linha, com data de acesso e arquivo | Qualquer editor; ônus em quem adiciona | Marcação "citation needed"; remoção permitida |
| OpenStreetMap | `source` no conjunto de mudanças; plano de importação na wiki | Comunidade local e fórum | Revisão de licença antes de importar |
| Querido Diário | Raspador por município, com coleta de teste anexada | Revisor confere a checklist | Esquema de validação e CI |
| covid19-br (Brasil.io) | Link do boletim e data de referência a cada envio | Coordenador regional | Data Package validado pelo goodtables; total oficial contra a soma |
| Base dos Dados | Campo obrigatório "Fonte original" e tabela de arquitetura | Equipe de dados | Testes do dbt |
| TheyWorkForYou | Bruto do Hansard guardado por dia; correções em patches | Equipe da mySociety | Parser reproduzível |

---

## 4. Integridade e neutralidade

### Contra alteração maliciosa
| Ameaça | Como as referências se protegem | Fonte |
|---|---|---|
| Contribuidor muda um número de forma sutil num PR grande | PR focado, um assunto por vez; revisão com `ACK <commit>` dizendo como foi feita; o dado é recalculado a partir da fonte e conferido contra o total oficial | Bitcoin Core CONTRIBUTING; covid19-br (`TOTAL NO ESTADO` pela secretaria, não pela soma) |
| Conta do mantenedor invadida | 2FA obrigatório (Kubernetes exige de todo membro; o GitHub permite à organização exigir de membros e colaboradores externos, no plano gratuito); commits de merge assinados e conferidos contra uma lista de chaves confiáveis | [community-membership.md](https://github.com/kubernetes/community/blob/master/community-membership.md); [GitHub, 2FA na organização](https://github.com/github/docs/blob/main/content/organizations/keeping-your-organization-secure/managing-two-factor-authentication-for-your-organization/requiring-two-factor-authentication-in-your-organization.md); [verify-commits](https://github.com/bitcoin/bitcoin/blob/master/contrib/verify-commits/README.md) |
| Status de CI falsificado | O ruleset pode aceitar o check só de um app específico: "If the status is set by any other person or integration, merging won't be allowed" | [regras de ruleset](https://github.com/github/docs/blob/main/content/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets.md) |
| CI que roda código do PR com segredos | O Scorecard marca como risco "Critical" usar `pull_request_target` ou `workflow_run` com checkout do PR, e injeção de texto de issue em scripts | [Scorecard, Dangerous-Workflow](https://github.com/ossf/scorecard/blob/main/docs/checks.md) |
| Artefato publicado diferente do código | Build reproduzível com várias assinaturas independentes (Guix); attestation do GitHub no log público do Sigstore | [guix](https://github.com/bitcoin/bitcoin/blob/master/contrib/guix/README.md); [attestations](https://github.com/github/docs/blob/main/content/actions/concepts/security/artifact-attestations.md) |
| Falha de segurança divulgada em público antes da correção | `SECURITY.md` com email e chaves (Bitcoin Core); relato privado de vulnerabilidade do GitHub, ligado pelo dono num repositório público | [SECURITY.md](https://github.com/bitcoin/bitcoin/blob/master/SECURITY.md); [private vulnerability reporting](https://github.com/github/docs/blob/main/content/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository.md) |
| PR aberto e conduzido por agente autônomo, em volume | "Pull requests should not be opened or driven by autonomous agents"; comentários parecendo escritos por IA "may be moderated" | [AI_POLICY.md](https://github.com/bitcoin/bitcoin/blob/master/doc/AI_POLICY.md) |

### Contra acusação de viés
- **Mesmo critério para todos, escrito e público (IFCN, princípio 1):** checar "using the same high standards of evidence and
  judgment for equivalent claims regardless of who made the claim"; não concentrar "on any one side"; publicar como os casos são
  escolhidos; a organização não é "affiliated with nor declares or shows support for any party, any politician or political
  candidate"; política de não partidarismo para a equipe no site. O selo não vai para organização cuja linha editorial "is
  controlled by the state, a political party or politician".
  ([IFCN Code of Principles](https://ifcncodeofprinciples.poynter.org/the-commitments))
- **Fontes que o leitor consegue refazer (IFCN, princípio 2):** fontes "in enough detail that readers can replicate their work";
  fonte primária sempre que existir (e explicar quando não); conferir os elementos centrais "against more than one named source"
  quando houver mais de uma.
- **Método publicado (IFCN, princípio 4):** mostrar a evidência que sustenta e também a que enfraquece; procurar quem fez a
  afirmação quando possível. Para o Brasil-Imposto, é a regra "Comparação honesta" do README, já em vigor.
- **Correções abertas (IFCN, princípio 5):** política de correções visível; "Where credible evidence is provided that the
  applicant has made a mistake worthy of correction, the applicant makes corrections openly and transparently, seeking as far
  as possible to ensure that users of the original see the correction".
- **Limite de afiliação no corpo que decide:** Rust (no máximo 1 de 5, ou 2 de 6 ou mais, com a mesma afiliação; afiliação inclui
  "major sponsor") e Python (no máximo 2 dos 5 do conselho com o mesmo empregador; quem tem conflito num voto "must abstain").
  ([RFC 3392](https://github.com/rust-lang/rfcs/blob/master/text/3392-leadership-council.md), [PEP 13](https://peps.python.org/pep-0013/))
  Adaptado ao Brasil-Imposto: mantenedores declaram filiação partidária e cargos públicos; nunca mais de um mantenedor filiado ao
  mesmo partido; quem é filiado não aprova sozinho PR que trate do próprio partido.
- **Conselho com mais de um lado (Full Fact):** "cross-party board", "fundraising safeguards", "a conflict of interests policy,
  restrictions on staff political activity". ([Full Fact, funding](https://fullfact.org/about/funding/))
- **Wikipedia, NPOV:** "explain the sides, fairly"; e ao remover texto sem fonte, não concentrar a limpeza "only on material of a
  particular point of view".

### Registro público de decisões
- **Toda mudança de status num PR próprio:** o EIP-1 pede que o PR que leva um EIP a Final "SHOULD contain no changes other than
  the status update". O BIP 3 criou a seção Changelog para registrar mudanças depois de Complete. O Rust anuncia cada FCP
  publicamente por dez dias com um resumo dos argumentos. ([EIP-1](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1.md),
  [BIP 3](https://github.com/bitcoin/bips/blob/master/bip-0003.md), [RFCs](https://github.com/rust-lang/rfcs))
- O Brasil-Imposto já tem o embrião: a tabela D do README e o registro GD do grill, com as palavras do autor. No repositório
  público, isso vira `docs/decisions/` (uma decisão por arquivo, ou a tabela atual) e toda mudança de método passa por ele.

### Transparência de quem financia
- **IFCN, princípio 3:** página com "each source of funding accounting for 5% or more of total revenue for its previous
  financial year", a forma jurídica, a estrutura e quem exerce o controle editorial.
- **Full Fact:** lista toda doação acima de £ 25.000 com valor e finalidade; em 2025, receita total de £ 3.054.478.
- **mySociety:** explica as três origens (fundações, doações individuais, receita comercial da subsidiária) e remete às contas
  publicadas na Charity Commission. ([mySociety, funding](https://www.mysociety.org/about/funding/))
- **Open Collective** (seção 6) mostra cada entrada e saída em público por padrão; é a forma mais barata de cumprir o princípio 3
  sem montar uma página à mão.


---

> As seções 5 a 9 foram escritas em 2026-10-02, a partir de páginas abertas nesse dia (data de coleta: 2026-10-02).

## 5. Comunicação e comunidade, grátis

### O que as referências fazem
- **Querido Diário: trilha de entrada visível e quadro público.** Tarefas marcadas com `good first issue` (municípios
  replicados), `spider` e `dificuldade:baixa/media/alta`, e um [Quadro de Expansão de Cidades](https://github.com/orgs/okfn-brasil/projects/12/views/13)
  público no GitHub Projects. A conversa fica num servidor do Discord da Open Knowledge Brasil, para "trocas sobre os projetos,
  dúvidas, pedidos de ajuda com contribuição". As propostas de trabalho entram por três formulários de issue
  (`novo_municipio.yaml`, `novo_sistema_replicavel.yaml`, `revisao_retroativa.yaml`), com campos obrigatórios e rótulo aplicado
  pelo próprio formulário. ([docs/CONTRIBUTING.md](https://github.com/okfn-brasil/querido-diario/blob/main/docs/CONTRIBUTING.md),
  [README](https://github.com/okfn-brasil/querido-diario/blob/main/README.md),
  [ISSUE_TEMPLATE](https://github.com/okfn-brasil/querido-diario/tree/main/.github/ISSUE_TEMPLATE))
- **Bitcoin Core: chat aberto, registro público fora do chat.** "Most communication about Bitcoin Core development happens on
  IRC, in the `#bitcoin-core-dev` channel on Libera Chat", com o histórico publicado em dois sites de log. As decisões, porém,
  ficam nos PRs (seção 1). ([CONTRIBUTING.md](https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md))
- **Kubernetes: chat "searchable and public", mas o arquivo depende de tempo livre.** O Slack do projeto avisa que "Chat is
  searchable and public", e o histórico é arquivado "when the administrators have time. There is no explicit interval."
  ([slack-guidelines.md](https://github.com/kubernetes/community/blob/master/communication/slack-guidelines.md))
- **Serenata de Amor: comunidade no Telegram, sem roadmap público** (seção 3). Com mais de 700 pessoas no chat e nenhum roadmap
  aberto, o trabalho dependeu do núcleo e parou com ele.

### O que existe de graça
| Canal | O que oferece | Custo e limite | Fonte |
|---|---|---|---|
| GitHub Discussions | Perguntas com resposta marcada, anúncios, enquetes, categorias definidas pelo dono, conversão de issue em discussão e trava de discussão que esquentou; só o administrador liga o recurso | Grátis (disponível no plano gratuito) | [about-discussions](https://github.com/github/docs/blob/main/content/discussions/collaborating-with-your-community-using-discussions/about-discussions.md) |
| Formulários de issue | Campos tipados, rótulos aplicados pelo formulário, campo obrigatório ("Only for public repositories") | Grátis | [syntax-for-issue-forms](https://github.com/github/docs/blob/main/content/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms.md), [form schema](https://github.com/github/docs/blob/main/content/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema.md) |
| Link que abre a issue já preenchida | Parâmetros `template`, `title`, `labels`, `body` e o `id` de cada campo do formulário na URL de `issues/new` | Grátis; quem abre precisa de conta no GitHub, e o parâmetro `labels` na URL exige permissão de rotular (o rótulo do próprio formulário não exige) | [creating-an-issue, "Creating an issue from a URL query"](https://github.com/github/docs/blob/main/content/issues/tracking-your-work-with-issues/using-issues/creating-an-issue.md) |
| Rótulos padrão | `bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`, `accessibility` em todo repositório novo; as issues com `good first issue` alimentam a página `/contribute` e o algoritmo de issues fáceis do GitHub | Grátis | [managing-labels](https://github.com/github/docs/blob/main/content/issues/using-labels-and-milestones-to-track-work/managing-labels.md), [good first issue](https://github.com/github/docs/blob/main/content/communities/setting-up-your-project-for-healthy-contributions/encouraging-helpful-contributions-to-your-project-with-labels.md) |
| Roadmap público | GitHub Projects com visão de linha do tempo (roadmap layout) e visibilidade pública | Grátis | [roadmap layout](https://github.com/github/docs/blob/main/content/issues/planning-and-tracking-with-projects/customizing-views-in-your-project/customizing-the-roadmap-layout.md), [visibilidade](https://github.com/github/docs/blob/main/content/issues/planning-and-tracking-with-projects/managing-your-project/managing-visibility-of-your-projects.md) |
| Matrix | "An open network for secure, decentralised communication"; a conta pode ficar em qualquer servidor | O servidor público matrix.org está introduzindo contas premium; no plano grátis, anexos de até 10 MB e 100 MB por dia; "Details of pricing have not yet been finalised" | [matrix.org](https://matrix.org/), [homeserver pricing](https://matrix.org/homeserver/pricing/) |
| Discord | Servidor com recursos de comunidade; para ligá-los, exige email verificado de quem escreve, filtro de mídia explícita e um canal de regras | Grátis na forma usada pelo Querido Diário; a conversa fica dentro do Discord, para quem tem conta | [Enabling Your Community Server](https://support.discord.com/hc/en-us/articles/360047132851-Enabling-Your-Community-Server) |

### O que serve para o Brasil-Imposto
| Padrão | Recomendação | Motivo |
|---|---|---|
| Um canal só no lançamento: Issues para o que pede ação, Discussions para o resto | **Adotar já** | Com um mantenedor, cada canal a mais divide a atenção. Discussions com quatro categorias: Perguntas, Ideias, Propostas de método e Anúncios. |
| Chat (Matrix ou Discord) | **Não no lançamento** | O que se decide em chat some (Kubernetes arquiva "when the administrators have time"); num projeto acusável de viés, a decisão tem de estar num PR ou numa issue com link. Se um dia houver chat, escrever no CONTRIBUTING que nada decidido ali vale até virar issue. Entre os dois, Matrix é aberto; Discord é onde o público brasileiro de dados cívicos já está (Querido Diário). |
| Botão "pedir correção" como link para `issues/new?template=...` com a página, o número e o período já preenchidos pelos `id` dos campos | **Adotar já** | É grátis e público (IFCN, princípio 5). O rótulo vem do formulário, não da URL, porque o visitante não tem permissão de rotular. Limite a dizer na própria página: quem pede correção precisa de conta no GitHub. |
| `good first issue` e rótulos de dificuldade (Querido Diário) | **Adotar já** | A tarefa de entrada natural é "acrescentar o orçamento do estado X" ou "conferir a fonte do número Y", no molde do "município replicado". |
| Quadro público de cobertura, um cartão por estado e por base de dados (Quadro de Expansão do Querido Diário) | **Adotar já** | GD34 deixa os outros estados para contribuidores; o quadro mostra o que falta e evita o erro do Serenata (sem roadmap público, a contribuição parou com o núcleo). As "notas" de usuários e os pedidos pela Lei de Acesso entram nele como trabalho futuro. |

---

## 6. Financiamento grátis de montar

O projeto não tem custo hoje (GitHub Pages, sem domínio pago), então não há conta a pagar. Esta seção serve para o dia em que
houver doação, e para que a forma de receber não crie suspeita de quem financia.

### As opções, com taxas
| Opção | Montar custa | Taxa sobre cada doação | Exige | Fonte |
|---|---|---|---|---|
| GitHub Sponsors | Nada | **0%** quando quem doa é conta pessoal; **até 6%** quando é conta de organização (3% de cartão e 3% de serviço do GitHub) | Morar ou operar em região aceita (o **Brasil** está na lista); recebe em conta bancária própria da organização, conta pessoal ou por um *fiscal host*; formulário fiscal W-8BEN para quem não é dos EUA | [about-github-sponsors](https://github.com/github/docs/blob/main/content/sponsors/getting-started-with-github-sponsors/about-github-sponsors.md), [taxas](https://github.com/github/docs/blob/main/data/reusables/sponsors/no-fees.md), [organização](https://github.com/github/docs/blob/main/content/sponsors/receiving-sponsorships-through-github-sponsors/setting-up-github-sponsors-for-your-organization.md), [impostos](https://github.com/github/docs/blob/main/content/sponsors/receiving-sponsorships-through-github-sponsors/tax-information-for-github-sponsors.md) |
| Open Collective, pela Open Source Collective (OSC) como *fiscal host* | Nada ("no setup fees, minimum balances, or recurring charges") | **10%** de taxa do host sobre o que entra, mais a taxa do processador (Stripe, PayPal, Wise), que "vary based on payment method, currency, and the country"; sem desconto | Licença aberta reconhecida (AGPL-3.0 serve); atividade recente ou uso relevante; quem pede tem de ser mantenedor. Para projeto de uma pessoa, a OSC procura contribuidores além do dono, repositório fora da conta pessoal, código de conduta, guia de contribuição, documento de governança e site | [OSC, fees](https://docs.oscollective.org/welcome-and-introduction-to-osc/fees), [eligibility](https://docs.oscollective.org/interested-in-joining-osc/acceptance-criteria), [one-person project](https://docs.oscollective.org/resources/resources/growing-from-a-one-person-project-to-a-collective) |
| Open Collective como plataforma, para quem tem pessoa jurídica própria | Plano "Discover" a US$ 0 por mês para organizações novas (preços de março de 2026) | Grátis com as gorjetas da plataforma ligadas, ou **5%** fixos no lugar das gorjetas; os Collectives hospedados não entram nessa tabela | Ser "a legal entity (such as a company, non-profit, cooperative, or similar)" | [opencollective.com/pricing](https://opencollective.com/pricing) |
| Gitcoin Grants | Nada para se inscrever | Não encontrei taxa publicada para o projeto que recebe | Rodadas periódicas e temáticas. O GG24 (doações de 14 a 28/out/2025) distribuiu cerca de US$ 1,8 mi em seis domínios, todos do ecossistema Ethereum (ferramentas, privacidade, interoperabilidade, P&D de bens públicos, adoção, InfoFi); requisito básico "Open-source projects contributing to public goods" com "verifiable team"; doações e pagamentos em cripto (Arbitrum, Celo, Ethereum); o Grants Stack foi desligado em maio de 2025 | [GG24](https://gitcoin.co/campaigns/gitcoin-grants-24-gg24), [quadratic funding](https://gitcoin.co/mechanisms/quadratic-funding) |
| O que a Open Knowledge Brasil usa | Nada para abrir as campanhas | Não consegui confirmar as taxas de Catarse, apoia.se e Benfeitoria (páginas montadas por JavaScript; seção 9) | Pessoa jurídica (a OKBR é associação sem fins lucrativos, recebe por PIX e transferência no CNPJ) | [ok.org.br/apoie](https://ok.org.br/apoie/), [prestação de contas](https://ok.org.br/transparencia/) |

### Como a Open Knowledge Brasil faz
- **Campanha por projeto, em plataformas brasileiras.** Catarse para o Querido Diário (campanha mantida desde setembro de 2020,
  também no selo do README), apoia.se para a Serenata de Amor (mensal), Benfeitoria para a Escola de Dados, além de PagSeguro,
  PayPal, transferência e PIX no CNPJ. Histórico publicado: a primeira campanha, para a Serenata em setembro de 2016,
  "conseguiu arrecadar aproximadamente R$ 80 mil, 30% mais do que o valor pedido, o suficiente para custear as operações do time
  pelos primeiros 90 dias"; R$ 49.000 em julho de 2019 para a Escola de Dados. ([apoie](https://ok.org.br/apoie/))
- **Prestação de contas aberta.** Estatuto, atas das assembleias, relatórios anuais de 2018 a 2025, balanços, parecer de
  auditoria e "um painel de transparência de contas, que contém os dados extraídos diretamente dos extratos bancários".
  ([transparência](https://ok.org.br/transparencia/))

### O que serve para o Brasil-Imposto
| Padrão | Recomendação | Motivo |
|---|---|---|
| Não pedir dinheiro no lançamento | **Adotar já** | Não há custo a cobrir. Pedir doação antes de haver quem confira os números convida a pergunta "quem paga?". |
| GitHub Sponsors na organização `brasil-imposto`, com `.github/FUNDING.yml` | **Quando houver custo** | Grátis de montar e 0% de taxa em doação de pessoa física; o Brasil é região aceita. O arquivo `FUNDING.yml` põe o botão no repositório e aceita também `open_collective` e até quatro links próprios ([sponsor button](https://github.com/github/docs/blob/main/content/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository.md)). Ponto para o autor: sem pessoa jurídica, o dinheiro cai numa conta pessoal. |
| Open Collective pela OSC | **Mais tarde** | O livro-caixa público cumpre o princípio 3 da IFCN sem página feita à mão (seção 4), mas custa 10% mais o processador, a OSC é uma entidade dos EUA e hoje o projeto não passa no critério de comunidade (uma pessoa, repositório ainda não publicado). |
| Gitcoin | **Não** | Os domínios são do ecossistema Ethereum, o dinheiro chega em cripto e doador anônimo em cripto atrapalha a regra de dizer quem financia. |
| Campanha no Catarse ou no apoia.se, como a OKBR | **Mais tarde** | É o caminho que o público brasileiro conhece, mas a OKBR recebe como associação, com CNPJ e contas auditadas; não conferi as taxas nem se aceitam pessoa física (seção 9). |
| Regra de quem pode doar, escrita antes da primeira doação | **Adotar já, no GOVERNANCE.md** | Recusar dinheiro de partido, candidato e ocupante de cargo eletivo; publicar toda fonte com 5% ou mais da receita do ano (IFCN, princípio 3) e o "fundraising safeguards" do Full Fact (seção 4). |

---

## 7. Pacote recomendado para o Brasil-Imposto

Nomes de arquivo, rótulos e identificadores em inglês; o texto dos arquivos e dos formulários em português. Tudo abaixo é grátis
num repositório público. Ordem: o que precisa existir no dia em que o repositório abrir, depois o que entra com o segundo
mantenedor.

| Item | O que é | De onde vem | Por quê |
|---|---|---|---|
| `GOVERNANCE.md` | Quem decide hoje (o autor, D2), como decide (explica por escrito no PR o motivo de aceitar ou recusar), o gatilho e o formato da passagem para mais mantenedores, a regra de afiliação (mantenedores declaram filiação partidária e cargo público; nunca dois do mesmo partido; filiado não aprova sozinho PR sobre o próprio partido), a regra de quem pode doar (seção 6) e um quadro de áreas com status (Maintained, Orphan) | BDFL com transição escrita: [PEP 13](https://peps.python.org/pep-0013/); mantenedor julga consenso: [Bitcoin Core CONTRIBUTING](https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md); limite de afiliação: [Rust RFC 3392](https://github.com/rust-lang/rfcs/blob/master/text/3392-leadership-council.md); status por área: [Linux MAINTAINERS](https://github.com/torvalds/linux/blob/master/MAINTAINERS) | D2 vira regra pública em vez de hábito. A OSC pede "Governance documentation" antes de hospedar um projeto ([one-person project](https://docs.oscollective.org/resources/resources/growing-from-a-one-person-project-to-a-collective)). |
| `CONTRIBUTING.md` | Tudo entra por PR, inclusive do autor; PR com um assunto só; título com a área (`data:`, `map:`, `docs:`); identidade: conta do GitHub com email válido, pseudônimo estável aceito; vocabulário de revisão (Concept, Approach, `ACK <commit>` dizendo como revisou); política de IA (o humano responde pelo PR e pela fonte de cada número; nada de PR aberto por agente autônomo); tarefas por dificuldade | [Bitcoin Core CONTRIBUTING](https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md), [AI_POLICY.md](https://github.com/bitcoin/bitcoin/blob/master/doc/AI_POLICY.md), [Querido Diário CONTRIBUTING](https://github.com/okfn-brasil/querido-diario/blob/main/docs/CONTRIBUTING.md) | O PR é o registro público do porquê de cada número mudar (seção 2). O projeto é feito com agentes, então a regra de IA tem de estar escrita desde o dia 1. |
| `CODE_OF_CONDUCT.md` | Contributor Covenant 3.0, com um contato que não seja só o autor quando houver segundo mantenedor; acrescentar uma linha: discussão partidária e ataque a pessoa citada no site saem do repositório | [Contributor Covenant 3.0](https://www.contributor-covenant.org/version/3/0/code_of_conduct/) (o Querido Diário escreveu o próprio: [CODE_OF_CONDUCT](https://github.com/okfn-brasil/querido-diario/blob/main/docs/CODE_OF_CONDUCT.md)) | É um dos itens que a OSC procura e o que o GitHub mostra no perfil de comunidade. Atenção: o texto do Covenant é CC BY-SA 4.0, então o arquivo fica com essa licença, exceção à CC BY 4.0 dos textos; a tradução para o português do Brasil existe só para a versão 2.1 ([translations](https://www.contributor-covenant.org/translations/)). |
| `SECURITY.md` | Como relatar falha sem expor: relato privado de vulnerabilidade do GitHub ligado no repositório, e um email | [Bitcoin Core SECURITY.md](https://github.com/bitcoin/bitcoin/blob/master/SECURITY.md), [private vulnerability reporting](https://github.com/github/docs/blob/main/content/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository.md) | O site não guarda dado pessoal, mas uma falha no pipeline de dados pode trocar números em produção; o relato não pode nascer público. |
| `.github/ISSUE_TEMPLATE/data-correction.yml` ("Pedir correção") | Formulário com campos obrigatórios: página ou número contestado, período, o que está errado, **link da fonte oficial que mostra o valor certo**, data em que a fonte foi aberta; rótulo `data-correction` aplicado pelo formulário. O botão de cada página abre este formulário pela URL, com página, número e período já preenchidos | Formulários e URL: [issue forms](https://github.com/github/docs/blob/main/content/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms.md), [URL query](https://github.com/github/docs/blob/main/content/issues/tracking-your-work-with-issues/using-issues/creating-an-issue.md); ônus em quem afirma: [WP:V](https://en.wikipedia.org/wiki/Wikipedia:Verifiability); correção aberta: [IFCN, princípio 5](https://ifcncodeofprinciples.poynter.org/the-commitments) | A correção fica pública, com a fonte, como pede a IFCN. Campo obrigatório só vale em repositório público, que é o caso. |
| `.github/ISSUE_TEMPLATE/add-source.yml` ("Acrescentar fonte") | Formulário com campos obrigatórios: órgão e nome da base, link oficial, licença ou termo de uso, frequência de publicação, ano de referência, unidade de medida, e qual número do site a base sustenta ou acrescenta | Fonte original obrigatória: [Base dos Dados, new-data.yml](https://github.com/basedosdados/pipelines/blob/main/.github/ISSUE_TEMPLATE/new-data.yml); licença conferida antes: [OSM Import/Guidelines](https://wiki.openstreetmap.org/wiki/Import/Guidelines); data de referência e link a cada envio: [covid19-br CONTRIBUTING](https://github.com/turicas/covid19-br/blob/master/CONTRIBUTING.md) | Estrutura antes do código (Base dos Dados): o mantenedor aceita a fonte e o formato antes de alguém escrever o coletor. |
| Outros formulários: `method-proposal.yml`, `bug-report.yml` | "Proposta de método" para mudar como um número é calculado (abre a janela final de comentário); defeito de tela ou de código | Proposta escrita antes do código: [Rust RFCs](https://github.com/rust-lang/rfcs/blob/master/README.md), [EIP-1](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1.md) | Mudança de método é onde nasce a acusação de viés; precisa de rito próprio. |
| `.github/pull_request_template.md` | Checklist que exige justificativa para item não marcado: cada número novo ou alterado tem link oficial, ano de referência e data de coleta; o script em `data/scripts/` reproduz o JSON; o total confere com o total oficial publicado; nenhum texto toma partido; foto com licença livre e crédito | [Querido Diário, pull_request_template.md](https://github.com/okfn-brasil/querido-diario/blob/main/.github/pull_request_template.md) ("Caso algum item não seja marcado, JUSTIFIQUE o motivo") | O revisor confere a checklist em vez de confiar nela, como manda o CONTRIBUTING do Querido Diário. |
| `.github/CODEOWNERS` | Dono por pasta: hoje o autor em tudo; depois, um dono para `data/` e outro para o site | [about-code-owners](https://github.com/github/docs/blob/main/content/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners.md); escopo por pasta: [Kubernetes OWNERS](https://github.com/kubernetes/community/blob/master/contributors/guide/owners.md) | Quando entrar o segundo mantenedor, quem entende do dado revisa o dado, sem precisar de permissão em tudo. |
| Rótulos | Os padrões do GitHub (`good first issue`, `help wanted`, `bug`, `documentation`...) mais `data-correction`, `new-source`, `method-change`, `needs-source`, `uf:sc` (um por estado) e `difficulty:low`, `difficulty:medium`, `difficulty:high` | [managing-labels](https://github.com/github/docs/blob/main/content/issues/using-labels-and-milestones-to-track-work/managing-labels.md); dificuldade e `good first issue`: [Querido Diário](https://github.com/okfn-brasil/querido-diario/blob/main/docs/CONTRIBUTING.md); marcação sem apagar: `{{citation needed}}` da [WP:V](https://en.wikipedia.org/wiki/Wikipedia:Verifiability) | `needs-source` é o "citation needed" do projeto: o número fica marcado e sai da tela se a fonte não vier. |
| DCO no lugar de CLA | `Signed-off-by` em cada commit (`git commit -s`), conferido pelo app DCO; sign-off obrigatório também nos commits pela interface web | [DCO 1.1](https://developercertificate.org/), [dcoapp/app](https://github.com/dcoapp/app), [GitLab trocou CLA por DCO](https://about.gitlab.com/blog/gitlab-switches-to-dco-license/), [commit signoff policy](https://github.com/github/docs/blob/main/content/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-the-commit-signoff-policy-for-your-repository.md) | Com AGPL-3.0 e CC BY 4.0 a contribuição entra com a mesma licença com que sai; um CLA daria ao autor o poder de relicenciar, o que num projeto cívico vira suspeita (seção 2). |
| Proteção de branch (ruleset em `main`) | Exigir PR, **0 aprovações** enquanto houver um mantenedor e 1 aprovação de outra pessoa depois; checks verdes exigidos e aceitos só do GitHub Actions; histórico linear; bloquear force push e exclusão; 2FA obrigatório na organização | [rulesets](https://github.com/github/docs/blob/main/content/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets.md), [2FA na organização](https://github.com/github/docs/blob/main/content/organizations/keeping-your-organization-secure/managing-two-factor-authentication-for-your-organization/requiring-two-factor-authentication-in-your-organization.md); 2FA de todo membro: [Kubernetes](https://github.com/kubernetes/community/blob/master/community-membership.md) | Exigir 1 aprovação com um mantenedor só obriga a usar bypass, que o público não vê (armadilha da seção 2). |
| Commits assinados | O autor assina os commits dele e os de merge; não exigir de quem chega | [verify-commits](https://github.com/bitcoin/bitcoin/blob/master/contrib/verify-commits/README.md), [commit signature verification](https://github.com/github/docs/blob/main/content/authentication/managing-commit-signature-verification/about-commit-signature-verification.md) | Prova que o merge saiu da conta do mantenedor sem travar o primeiro PR de ninguém. |
| CI de proveniência dos dados (GitHub Actions) | (1) esquema que recusa número sem `source` com link, ano de referência, data de coleta e cópia arquivada; (2) roda `data/scripts/` sobre o bruto guardado no repositório e compara o hash com o JSON; (3) confere a soma das partes contra o total oficial; (4) OpenSSF Scorecard; nunca `pull_request_target` com checkout do PR | `sources` obrigatório: [Data Package](https://datapackage.org/standard/data-package/); validação por máquina e total oficial contra a soma: [covid19-br](https://github.com/turicas/covid19-br/blob/master/README.md); bruto guardado e correção por patch: [ParlParse](https://parser.theyworkforyou.com/parser.html); `archive-url` e `access-date`: [WP:Link rot](https://en.wikipedia.org/wiki/Wikipedia:Link_rot); [Scorecard](https://github.com/ossf/scorecard), [Dangerous-Workflow](https://github.com/ossf/scorecard/blob/main/docs/checks.md) | É a regra 1 do projeto ("nenhum número sem fonte") virando barreira automática. Rodar sobre o bruto guardado, e não baixando de novo, porque os servidores do governo bloqueiam coleta (Q32) e mudam de endereço (lição do EIP-1). |
| Registro de decisões (`docs/decisions/`) | Uma decisão por arquivo, com data, contexto, alternativas e o link do PR; mudança de método anunciada em Discussions com 7 a 10 dias de comentário antes do merge; o PR que muda o status de uma decisão não muda mais nada | Janela final: [Rust FCP](https://github.com/rust-lang/rfcs/blob/master/README.md), Last Call do [EIP-1](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1.md); Changelog depois de Complete: [BIP 3](https://github.com/bitcoin/bips/blob/master/bip-0003.md) | O projeto já tem o embrião (tabela D do README, registro GD do grill); no repositório público, é a defesa contra a acusação de mudar número às escuras. |

**Também entram, já recomendados nas seções 2 e 5:** GitHub Discussions com quatro categorias; o quadro público de cobertura
por estado (GitHub Projects), onde as "notas" de usuários e os pedidos pela Lei de Acesso ficam como trabalho futuro
documentado; e, depois do lançamento, a attestation do pacote de dados publicado.

---

## 8. Os 3 exemplos mais fortes para este projeto

**1. covid19-br (Brasil.io): voluntários transcrevendo dado oficial, com a fonte a cada envio.** É o mais parecido com o que o
Brasil-Imposto pede de quem chega: pessoas de fora transcrevem números publicados pelo governo, e cada atualização leva a data de
referência, a planilha, o link de onde o número saiu e as observações. O desenho tem a checagem que mais importa num projeto de
números públicos: a linha do total do estado é preenchida com o total da secretaria, nunca com a soma dos municípios, e a
diferença fica à vista. Os dados seguem Data Package, são validados por máquina e saem com licença aberta e a forma de citar. É o
modelo do formulário "Acrescentar fonte", do checklist do PR e do CI de proveniência.
([README](https://github.com/turicas/covid19-br/blob/master/README.md),
[CONTRIBUTING](https://github.com/turicas/covid19-br/blob/master/CONTRIBUTING.md))

**2. Querido Diário (Open Knowledge Brasil): o projeto cívico brasileiro que segue vivo com comunidade.** Ativo (push em
setembro de 2026), mostra o caminho inteiro de um projeto que depende de voluntários para cobrir o Brasil município por
município, exatamente o que GD34 espera para os outros estados. Formulários de issue com campos obrigatórios, PR de dados com
checklist em que todo item não marcado exige justificativa, revisor que confere a checklist em vez de confiar nela, rótulos de
dificuldade, `good first issue` com um tamanho de tarefa que vale a revisão, quadro público de expansão, comunidade no Discord e
financiamento coletivo com prestação de contas da OKBR. Também mostra o contraste com o irmão Serenata de Amor, que sem roadmap
público parou com o núcleo. ([docs/CONTRIBUTING.md](https://github.com/okfn-brasil/querido-diario/blob/main/docs/CONTRIBUTING.md),
[pull_request_template.md](https://github.com/okfn-brasil/querido-diario/blob/main/.github/pull_request_template.md))

**3. Bitcoin Core: governança para um projeto em que a confiança é o produto.** Um projeto cujo valor depende de ninguém
conseguir mudar uma regra às escondidas resolveu o problema sem conselho nem votação: todo mundo, sem exceção, entra por PR; os
mantenedores de merge julgam o consenso e o padrão mínimo, e não o próprio gosto; a revisão usa um vocabulário fixo que diz o
que foi conferido e como (`Concept ACK`, `Approach NACK`, `ACK <commit>` com "I have tested the code"); NACK sem motivo pode ser
ignorado; os commits de merge são assinados e conferíveis contra uma lista de chaves; e há uma política de IA que aceita a
ferramenta, mas não o PR conduzido por agente autônomo. É o modelo que cabe em D2 (um mantenedor no início) e continua servindo
quando entrarem outros, e responde ao risco particular deste projeto, que é feito com agentes.
([CONTRIBUTING.md](https://github.com/bitcoin/bitcoin/blob/master/CONTRIBUTING.md),
[AI_POLICY.md](https://github.com/bitcoin/bitcoin/blob/master/doc/AI_POLICY.md),
[verify-commits](https://github.com/bitcoin/bitcoin/blob/master/contrib/verify-commits/README.md))

Menção honrosa: a regra de verificabilidade da Wikipedia ("The burden to demonstrate verifiability lies with the editor who adds
or restores material") é a frase que o `CONTRIBUTING.md` e o formulário "Pedir correção" deveriam citar.

---

## 9. Não consegui confirmar

- **Taxas de Catarse, apoia.se e Benfeitoria**, e se aceitam campanha de pessoa física: as páginas são montadas por JavaScript e
  a busca da central de ajuda do Catarse respondeu 404; três artigos da central abertos não falam de taxa.
- **Taxa do Gitcoin para quem recebe**, e se existe hoje alguma rodada aberta a um projeto cívico sem ligação com Ethereum: li
  só a página do GG24 (2025) e o mecanismo de *quadratic funding*.
- **Existência de um *fiscal host* brasileiro no Open Collective**: não procurei. Também não conferi a afirmação da seção 4 de
  que o Open Collective mostra cada entrada e saída "em público por padrão" para todo coletivo: confirmei só que a OSC publica
  o próprio orçamento lá ("Our budget is fully transparent") e que a plataforma se apresenta como "Collect and spend money
  transparently".
- **GitHub Sponsors para uma organização sem pessoa jurídica**: a documentação aceita conta bancária pessoal, mas também diz que
  a organização elegível é a que "legally operates in a supported region"; não achei texto que resolva o caso de uma
  organização do GitHub mantida por uma pessoa física.
- **Rótulo aplicado pelo formulário de issue para quem não tem permissão de rotular**: a documentação não diz isso com todas as
  letras. É uma inferência: a chave `projects` traz o aviso de que quem abre precisa de permissão de escrita, e a chave `labels`
  não traz; e o Querido Diário usa rótulos nos formulários que pessoas de fora abrem.
- **Discord**: não conferi se a conversa de um servidor pode ficar pública ou ser encontrada por buscador; a seção 5 diz só o que
  a página de suporte confirma (requisitos para ligar os recursos de comunidade).
- **Preço do servidor matrix.org**: a própria página diz que "Details of pricing have not yet been finalised".
- **Decisões do grill citadas no pedido desta pesquisa**: quando este agente leu o grill, o registro terminava em GD37. Nota do
  agente principal (2026-10-02): GD38 a GD44 foram registradas logo depois; o botão "pedir correção" (GD38), as notas como
  trabalho futuro (GD41) e o código em inglês (GD43) são decisões do autor.
