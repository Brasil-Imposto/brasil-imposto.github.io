# Políticos por período: quem ocupava cada cargo, 2019 a 2026

> **Nota de 2026-10-14:** `build_sc_mayors.py` virou `pipelines/politicians/build_mayors.py --uf SC` (D71).

Coleta: 2026-10-01. Objetivo: para qualquer período que o usuário escolher no site (mês, ano ou mandato de 4 anos, de 2019-01 a 2026-10), mostrar quem ocupava cada cargo, com o partido na época e uma fonte para cada fato. Linguagem neutra: só cargos, datas, partidos e atos. Nada sobre candidaturas ou resultados das eleições de 2026.

## Arquivos

| Arquivo | Conteúdo | Script |
|---|---|---|
| `data/politicians/union.json` | Presidente, Vice-Presidente e ministro da área econômica (Economia 2019 a 2022, Fazenda desde 2023) | `pipelines/politicians/build_union.py` |
| `data/politicians/governors.json` | Governadores e vices das 27 UFs, com substituições | `pipelines/politicians/build_governors.py` e `governors_curated/<UF>.json` |
| `data/politicians/senators.json` | Senadores em exercício desde 2019-02-01, titulares e suplentes | `pipelines/politicians/build_senators.py` |
| `data/politicians/federal-deputies.json` | Deputados federais em exercício nas legislaturas 56 e 57 | `pipelines/politicians/build_federal_deputies.py` |
| `data/politicians/state-deputies.json` | Deputados estaduais e distritais **eleitos** em 2018 e 2022 | `pipelines/politicians/build_state_deputies.py` |
| `data/politicians/sc-mayors.json` | Prefeitos e vices **eleitos** em SC em 2020 e 2024, com código IBGE | `pipelines/politicians/build_sc_mayors.py` |

Módulos comuns: `tse_common.py` (lê o cadastro de candidaturas do TSE) e `commons_photos.py` (foto, autor e licença no Wikimedia Commons).

Como rodar (nenhuma chave, nenhum login; os downloads ficam fora do repositório):

```bash
export POLITICIANS_WORK=/tmp/politicians-work
cd ~/Documents/Brasil-Imposto/pipelines/politicians
python3 build_union.py
python3 build_governors.py
python3 build_senators.py
python3 build_federal_deputies.py
python3 build_state_deputies.py
python3 build_sc_mayors.py
```

## Convenções comuns

- **start** é o dia em que a pessoa assumiu; **end** é o dia em que deixou o cargo (em geral o mesmo dia em que o sucessor assume); **null** quando segue no cargo em 2026-10-01. Na troca, os dois aparecem no mesmo dia: o site deve mostrar quem assumiu.
- **Atos do DOU** valem a partir da publicação: a data usada é a da publicação, e a data do decreto fica no texto.
- **Partido na época:** o registro de candidatura no TSE dá o partido numa data conhecida (a da eleição); mudanças entre duas candidaturas só entram com data quando uma fonte a dá. A lista nominal de filiados não é dado aberto (o portal do TSE só publica o perfil agregado da filiação), então não há como datar toda troca de partido com o TSE.
- **verified** (governadores): true quando a data foi conferida no texto de uma fonte oficial; false quando a página não pôde ser lida (bloqueio de robôs, portal suspenso) ou só a imprensa confirma; o motivo fica em `note`.
- **Fotos:** só a URL remota; nada foi baixado. Licença, autor e página do arquivo como o Wikimedia Commons registra; null com motivo quando não há.

## União: Presidente, Vice e ministro da área econômica (`union.json`)

| Cargo | Pessoa | Início | Fim | Partido no início | Fonte principal |
|---|---|---|---|---|---|
| Presidente da República | Jair Bolsonaro | 2019-01-01 | 2023-01-01 | PSL | TSE 2018; CF, art. 82 |
| Presidente da República | Luiz Inácio Lula da Silva | 2023-01-01 | em exercício | PT | TSE 2022; CF, art. 82 |
| Vice-Presidente | Hamilton Mourão | 2019-01-01 | 2023-01-01 | PRTB | TSE 2018 |
| Vice-Presidente | Geraldo Alckmin | 2023-01-01 | em exercício | PSB | TSE 2022 |
| Ministro da Economia | Paulo Guedes | 2019-01-01 | 2023-01-01 | sem filiação encontrada | DOU: decreto de 1º/1/2019; decreto de 31/12/2022 publicado em 1º/1/2023 |
| Ministro da Fazenda | Fernando Haddad | 2023-01-01 | 2026-03-20 | PT | DOU: decreto de 1º/1/2023; exoneração a pedido, decreto de 19/3/2026 publicado em 20/3/2026 |
| Ministro da Fazenda | Dario Durigan | 2026-03-20 | em exercício | sem filiação encontrada | DOU: mesmo decreto de 19/3/2026; página do Ministério da Fazenda |

Achados e ressalvas:

- **Troca na Fazenda em 2026.** O DOU de 2026-03-20 (Seção 2, edição 54) traz os dois decretos de 19 de março de 2026: "EXONERAR, a pedido, FERNANDO HADDAD do cargo de Ministro de Estado da Fazenda" e "NOMEAR DARIO CARNEVALLI DURIGAN, para exercer o cargo de Ministro de Estado da Fazenda". A página do ministério (atualizada em 10/04/2026) confirma Durigan.
- **A exoneração de Paulo Guedes** foi assinada pelo "VICE-PRESIDENTE DA REPÚBLICA, no exercício do cargo de Presidente". Esse exercício curto do Vice (viagem do Presidente no fim de 2022) não entra como mandato, pela regra das substituições curtas.
- **Partido de Bolsonaro:** PSL na eleição de 2018 (TSE); carta de desfiliação assinada em 2019-11-19 (Agência Brasil, 19/11/2019); sem partido até 2021-11-30, quando assinou a filiação ao PL (Agência Brasil, 30/11/2021); PL na candidatura de 2022 (TSE). As duas datas vêm da Agência Brasil (EBC), não de registro do TSE.
- **Mourão e Alckmin:** o partido de 2018 e o de 2022 vêm do TSE; a data exata da troca não foi confirmada em fonte oficial (a API do Senado registra a filiação de Mourão ao Republicanos com a data da eleição, 2022-10-02). Entre as duas observações o partido fica sem data.
- **Mandato presidencial:** posse em 1º de janeiro até 2023; pela EC 111/2021, o mandato seguinte começa em 5 de janeiro de 2027 (fora do período).
- **Fotos (Commons):** Bolsonaro (domínio público, US Embassy Brasília), Lula (CC BY 2.0, Palácio do Planalto), Mourão (CC BY 2.0, Alan Santos/PR), Alckmin (CC BY-SA 4.0, Ricardo Stuckert), Guedes (CC BY 2.0, Marcos Corrêa; recorte de foto com outra pessoa), Haddad (CC BY 2.0, Ricardo Stuckert). Durigan: sem foto (não encontrado no Wikidata).

## Governadores e vices (`governors.json`)

### Método

1. **Eleitos:** governador e vice eleitos em 2018 e 2022 em cada UF, do cadastro de candidaturas do TSE (`DS_SIT_TOT_TURNO = ELEITO`, 54 por eleição), com nome completo e partido na eleição. Datas do mandato pela CF, art. 28 (posse em 1º de janeiro).
2. **Substituições:** pista inicial nas listas de governadores e vices da Wikipédia em português (só como pista, nunca como fonte; vários erros encontrados, ver abaixo), depois cada mudança procurada em fonte oficial: assembleia legislativa, governo do estado, Diário Oficial, STJ, STF, TSE. Os mandatos conferidos ficam em `pipelines/politicians/governors_curated/<UF>.json`, um arquivo por UF, com a fonte e a frase-chave de cada data.
3. **Conferência automática:** `build_governors.py` cruza cada mandato "eleito" com o TSE (nome e partido) e acusa eleito ausente ou partido divergente (`checks.tse_cross_check_problems`, vazio na versão entregue).
4. **Partido:** `party_at_start` no mandato; em cada pessoa, `party_observations` traz o partido de cada registro de candidatura no TSE em 2018 e 2022, datado pela eleição. Trocas de partido no meio do mandato só aparecem com data quando uma fonte oficial a dá (exemplo: SC, Carlos Moisés, PSL para Republicanos em março de 2022, pela biografia da Alesc).
5. **Fotos:** imagem principal do verbete da Wikipédia em português, com licença e autor lidos no Commons. Para evitar homônimos, a foto só entra se o item do Wikidata da pessoa aparece como governador ou vice de uma UF com mandato desde 2019 (consulta SPARQL no Wikidata) ou se a descrição menciona o cargo. Esse filtro derrubou uma foto errada: o verbete "Wilson Lima" é de outro político (nascido em 1953), não do governador do Amazonas.

### Escopo

Entram as mudanças de quem exerce o cargo: renúncias (abril de 2022, março e abril de 2026), afastamentos judiciais e por impeachment com o interino, eleições indiretas, cassações e a saída do vice. O titular afastado mantém o mandato, e o afastamento aparece em `interruptions`. Os períodos de vice vago têm `kind: "vago"`. Não entram as substituições curtas por viagem ou licença do governador.

### Obstáculos de acesso (afetam a verificação)

- **Portais de notícias dos governos estaduais estão suspensos no período eleitoral** (Lei 9.504/97): A União (PB), agência do Acre e outros devolvem só o aviso "as notícias deste site/portal estão temporariamente suspensas". A cópia do Internet Archive resolveu na Paraíba; no Acre, não.
- **TSE, STJ e STF bloqueiam acesso automatizado** (403 ou "Access Denied"), e o Internet Archive não tinha cópia útil das páginas buscadas. As datas que dependem só dessas páginas ficam com `verified: false` e o motivo em `note`.
- As **assembleias legislativas** (Alepa, Aleto, ALE-AL) responderam e foram a melhor fonte oficial.

### Erros da pista (Wikipédia) corrigidos pela fonte oficial

- Tocantins: a lista diz que Wanderlei Barbosa ficou afastado de 3/9 a 5/11/2025. A Lei estadual 4.880, de 26/11/2025, foi sancionada pelo "VICE-GOVERNADOR DO ESTADO DO TOCANTINS, no exercício do cargo de GOVERNADOR"; o retorno veio com liminar do STF na sexta-feira, 5 de dezembro de 2025 (jornal regional publicado no site da Prefeitura de Praia Norte; data não conferida em fonte oficial).
- Tocantins: na posse definitiva de 2022-03-11, a Assembleia registra Wanderlei Barbosa "(sem partido)".
- Roraima: a lista atribui a cassação de Edilson Damião a um "Supremo Tribunal Eleitoral"; é o TSE (sessão de 2026-04-30). A eleição suplementar de 21/06/2026 não teve diplomação: o TSE suspendeu o prazo, e o presidente da Assembleia segue como governador interino nas fontes lidas. O resultado da votação não entra no arquivo.

### Resultado

27 UFs, 135 mandatos (54 com data conferida em fonte oficial), 92 pessoas, 76 com foto. UFs com substituições pesquisadas: 14 de 27; sem pesquisa de substituições (só eleitos do TSE, `verified: false`): AM, DF, ES, GO, MT, MS, MG, PR, RJ, RN, RS, RO, SP.

### Substituições, interinos, vacâncias e mandatos encerrados antes do fim

| UF | Cargo | Pessoa | Tipo | Início | Fim | Motivo | Data conferida |
|---|---|---|---|---|---|---|---|
| AC | governador | Gladson Cameli | eleito | 2023-01-01 | 2026-04-02 | renúncia | não |
| AC | vice-governador | Mailza Assis | eleito | 2023-01-01 | 2026-04-02 | assumiu o cargo de governadora | não |
| AC | governador | Mailza Assis | vice no cargo de titular | 2026-04-02 | em exercício | renúncia do titular | não |
| AC | vice-governador | (vago) | vago | 2026-04-02 | em exercício | a vice-governadora assumiu o cargo de governadora | não |
| AL | governador | Renan Filho | eleito | 2019-01-01 | 2022-04-02 | renúncia | não |
| AL | governador | Klever Loureiro | interino | 2022-04-02 | 2022-05-15 | posse do governador eleito pela Assembleia | não |
| AL | governador | Paulo Dantas | eleito indiretamente | 2022-05-15 | 2023-01-01 | fim do mandato; afastamentos: 2022-10-11 a 2022-10-24 | sim |
| AL | vice-governador | José Wanderley Neto | eleito indiretamente | 2022-05-15 | 2023-01-01 | fim do mandato | sim |
| AL | governador | José Wanderley Neto | interino | 2022-10-11 | 2022-10-24 | retorno do titular por decisão do STF | não |
| AL | vice-governador | Luciano Barbosa | eleito | 2019-01-01 | 2021-01-01 | deixou o cargo para assumir a Prefeitura de Arapiraca | não |
| AL | vice-governador | (vago) | vago | 2021-01-01 | 2022-05-15 | renúncia do vice-governador | sim |
| CE | governador | Camilo Santana | eleito | 2019-01-01 | 2022-04-02 | renúncia | não |
| CE | vice-governador | Izolda Cela | eleito | 2019-01-01 | 2022-04-02 | assumiu o cargo de governadora | não |
| CE | governador | Izolda Cela | vice no cargo de titular | 2022-04-02 | 2023-01-01 | fim do mandato | não |
| CE | vice-governador | (vago) | vago | 2022-04-02 | 2023-01-01 | a vice-governadora assumiu o cargo de governadora | não |
| MA | governador | Flávio Dino | eleito | 2019-01-01 | 2022-04-02 | renúncia | não |
| MA | vice-governador | Carlos Brandão | eleito | 2019-01-01 | 2022-04-02 | assumiu o cargo de governador | não |
| MA | governador | Carlos Brandão | vice no cargo de titular | 2022-04-02 | 2023-01-01 | fim do mandato | não |
| MA | vice-governador | (vago) | vago | 2022-04-02 | 2023-01-01 | o vice-governador assumiu o cargo de governador | não |
| PA | vice-governador | Lúcio Vale | eleito | 2019-01-01 | 2021-04-26 | deixou o cargo para assumir vaga de conselheiro do Tribunal de Contas dos Municípios | não |
| PA | vice-governador | (vago) | vago | 2021-04-26 | 2023-01-01 | saída do vice-governador | não |
| PA | governador | Helder Barbalho | eleito | 2023-01-01 | 2026-04-02 | renúncia | sim |
| PA | vice-governador | Hana Ghassan | eleito | 2023-01-01 | 2026-04-02 | assumiu o cargo de governadora | sim |
| PA | governador | Hana Ghassan | vice no cargo de titular | 2026-04-02 | em exercício | renúncia do titular | sim |
| PA | vice-governador | (vago) | vago | 2026-04-02 | em exercício | a vice-governadora assumiu o cargo de governadora | sim |
| PB | governador | João Azevêdo | eleito | 2023-01-01 | 2026-04-02 | renúncia | sim |
| PB | vice-governador | Lucas Ribeiro | eleito | 2023-01-01 | 2026-04-02 | assumiu o cargo de governador | sim |
| PB | governador | Lucas Ribeiro | vice no cargo de titular | 2026-04-02 | em exercício | renúncia do titular | sim |
| PB | vice-governador | (vago) | vago | 2026-04-02 | em exercício | o vice-governador assumiu o cargo de governador | sim |
| PI | governador | Wellington Dias | eleito | 2019-01-01 | 2022-03-31 | renúncia | não |
| PI | vice-governador | Regina Sousa | eleito | 2019-01-01 | 2022-03-31 | assumiu o cargo de governadora | não |
| PI | governador | Regina Sousa | vice no cargo de titular | 2022-03-31 | 2023-01-01 | fim do mandato | não |
| PI | vice-governador | (vago) | vago | 2022-03-31 | 2023-01-01 | a vice-governadora assumiu o cargo de governadora | não |
| RR | governador | Antonio Denarium | eleito | 2023-01-01 | 2026-03-27 | renúncia | não |
| RR | vice-governador | Edilson Damião | eleito | 2023-01-01 | 2026-03-27 | assumiu o cargo de governador | não |
| RR | governador | Edilson Damião | vice no cargo de titular | 2026-03-27 | 2026-04-30 | cassação do mandato pelo TSE (chapa eleita em 2022) | não |
| RR | vice-governador | (vago) | vago | 2026-03-27 | em exercício | o vice-governador assumiu o cargo de governador | não |
| RR | governador | Soldado Sampaio | interino | 2026-04-30 | em exercício | cassação da chapa eleita; assumiu como presidente da Assembleia Legislativa | não |
| SC | governador | Carlos Moisés | eleito | 2019-01-01 | 2023-01-01 | fim do mandato; afastamentos: 2020-10-26 a 2020-11-27, 2021-03-30 a 2021-05-07 | sim |
| SC | governador | Daniela Reinehr | interino | 2020-10-26 | 2020-11-27 | retorno do titular | sim |
| SC | governador | Daniela Reinehr | interino | 2021-03-30 | 2021-05-07 | retorno do titular | sim |
| TO | governador | Mauro Carlesse | eleito | 2019-01-01 | 2022-03-11 | renúncia; afastamentos: 2021-10-20 a 2022-03-11 | sim |
| TO | vice-governador | Wanderlei Barbosa | eleito | 2019-01-01 | 2022-03-11 | assumiu o cargo de governador | sim |
| TO | governador | Wanderlei Barbosa | interino | 2021-10-20 | 2022-03-11 | posse definitiva após a renúncia do titular | não |
| TO | governador | Wanderlei Barbosa | vice no cargo de titular | 2022-03-11 | 2023-01-01 | fim do mandato | sim |
| TO | vice-governador | (vago) | vago | 2022-03-11 | 2023-01-01 | o vice-governador assumiu o cargo de governador | sim |
| TO | governador | Wanderlei Barbosa | eleito | 2023-01-01 | em exercício | posse após a eleição de 2022; afastamentos: 2025-09-03 a 2025-12-05 | sim |
| TO | governador | Laurez Moreira | interino | 2025-09-03 | 2025-12-05 | retorno do titular autorizado por liminar do STF | não |

### Fotos sem resultado

16 pessoas sem foto: Luciano Barbosa (AL), Jaime Nunes (AP), Teles Júnior (AP), Wilson Lima (AM), Defensor Carlos Almeida (AM), Tadeu De Souza (AM), Celina Leão (DF), Daniel Vilela (GO), Barbosinha (MS), Professor Mateus  (MG), Claudio Castro (RJ), Fatima Bezerra (RN), Ze Jodan (RO), Sérgio Gonçalves (RO), Frutuoso Lins (RR), Tarcísio (SP).

## Senadores e deputados federais (coleta de 2026-10-01)

Arquivos: `data/politicians/senators.json` e `data/politicians/federal-deputies.json`.
Scripts: `pipelines/politicians/build_senators.py` e `pipelines/politicians/build_federal_deputies.py`
(Python 3, só biblioteca padrão; cache das respostas brutas em `$POLITICIANS_WORK/api/senado/` e `$POLITICIANS_WORK/api/camara/`;
data de coleta fixável com `POLITICIANS_COLLECTED_ON=2026-10-01`). Janela: 2019-02-01 a 2026-10-01.
Não há nada sobre candidaturas nem resultados eleitorais.

### Método: Senado

Endpoints (API de dados abertos do Senado, resposta JSON pelo sufixo `.json`; todos responderam em 2026-10-01 com `VersaoServico` 4 ou 5):

- `https://legis.senado.leg.br/dadosabertos/senador/lista/legislatura/56/57.json`: 318 parlamentares com mandato nas legislaturas 56 ou 57 (inclui suplentes que nunca exerceram).
- `https://legis.senado.leg.br/dadosabertos/senador/{codigo}/mandatos.json`: mandatos com o bloco `Exercicios` (`DataInicio`, `DataFim`, `SiglaCausaAfastamento`, `DescricaoCausaAfastamento`).
- `https://legis.senado.leg.br/dadosabertos/senador/{codigo}/filiacoes.json`: filiações com `DataFiliacao` e `DataDesfiliacao`.

Regras:

- Um período de exercício por registro `Exercicio`, recortado na janela. `end_reason` é a `DescricaoCausaAfastamento` (por exemplo "Retorno do titular", "Licença com convocação de suplente (sup 120 dias)", "Afastamento do exercício", "Renúncia", "Falecimento", "Término do mandato", "Cassação de registro/diploma pela Justiça Eleitoral"). `start_reason` é sempre null: a API não informa motivo de início.
- `DataFim` é tratada como o último dia de exercício (inclusiva). `end` null significa em exercício na data da coleta.
- `kind` vem de `DescricaoParticipacao` do mandato ("Titular" ou "1º/2º Suplente"); para suplentes o JSON traz o titular (`titular.id`).
- Partido: filiações que se sobrepõem à janela, com as datas da API (o início pode ser anterior a 2019; para suplentes o Senado costuma registrar a filiação a partir da data do primeiro exercício).
- Foto: `UrlFotoParlamentar` da lista, com o esquema trocado de http para https (o servidor redireciona para a mesma imagem); existência conferida por HEAD, sem baixar a imagem.

Contagens: 157 pessoas, 163 mandatos (107 de titular, 56 de suplente), 241 períodos de exercício; 56 suplentes exerceram; 81 em exercício em 2026-10-01; 71 pessoas com mais de um partido na janela.
Por UF: AC 7, AL 8, AM 3, AP 4, BA 3, CE 10, DF 4, ES 5, GO 5, MA 8, MG 8, MS 4, MT 9, PA 4, PB 9, PE 5, PI 6, PR 4, RJ 5, RN 5, RO 6, RR 5, RS 5, SC 7, SE 5, SP 6, TO 7.

### Método: Câmara

Endpoints (API v2 da Câmara, `Accept: application/json`, no máximo 8 requisições simultâneas, novas tentativas em 429/5xx):

- `https://dadosabertos.camara.leg.br/api/v2/deputados?idLegislatura=56&itens=100` e `idLegislatura=57`, paginados pelo link `rel=next`. A lista devolve linhas repetidas por pessoa (1.073 linhas para 613 ids na 56; 879 linhas para 648 ids na 57); a coleta deduplica por id: 929 pessoas.
- `https://dadosabertos.camara.leg.br/api/v2/deputados/{id}/historico`: cada mudança de status com `dataHora`, `situacao`, `condicaoEleitoral`, `descricaoStatus`, `siglaPartido`, `siglaUf`, `idLegislatura`.
- `https://dadosabertos.camara.leg.br/api/v2/deputados/{id}`: `nomeCivil` e `ultimoStatus` (`nome`, `urlFoto`).

Regras derivadas da leitura dos dados (cada uma corrigiu um erro visível na conferência de vagas):

- Um período começa num registro de entrada: `descricaoStatus` contendo "Entrada", "Efetivação" ou "Torna-se titular", com `situacao` "Exercício" ou "CONVOCADO", datado a partir do início da legislatura. A API registra algumas reassunções de suplente com `situacao` "CONVOCADO" e descrição "Entrada - Reassunção / DIVERSO - Convocação Eleito ou Suplente" (16 registros); sem essa regra, vagas da BA em 2019 e 2020 apareciam vazias por meses.
- Registros administrativos com `situacao` "Exercício" não abrem período: "Alteração de partido" de suplente fora do exercício (há um de 2022-03-31 marcado na legislatura 57), ofícios anteriores à posse ("Of. s/n/2023", "Carta s/n/2023") e "Alteração solicitada via Gabinete Digital, em data anterior à posse". Registros "CONVOCADO" sem "Entrada" não alteram o estado.
- Um período termina no primeiro registro seguinte com situação de saída: "Licença", "SUPLENCIA", "VACANCIA", "FIM_MANDATO", "SUSPENSO" ou "Afastado". `start_reason` e `end_reason` são a `descricaoStatus` desses registros. Datas são o dia do registro.
- `kind`: condição eleitoral no primeiro período da legislatura; cada período traz `electoral_condition` (Titular, Suplente ou EFETIVADO).
- Partido: sigla de cada registro do histórico das legislaturas 56 e 57, em ordem de `dataHora`; um trecho vai do primeiro registro com a sigla até o registro com a sigla seguinte; o último trecho termina no fim do último exercício (null se em exercício). É o partido registrado pela Câmara durante o mandato, não a filiação partidária fora dele.
- Nome: `ultimoStatus.nome` (nome parlamentar atual); `full_name`: `nomeCivil` como a API devolve (em maiúsculas em parte dos casos).
- Foto: `ultimoStatus.urlFoto` (retrato atual, sem data); as 929 URLs responderam com imagem no HEAD.

Contagens: 929 pessoas, 1.261 mandatos por legislatura (613 na 56, 648 na 57), 1.794 períodos de exercício; mandatos de suplente que exerceu: 227 (100 na 56, 127 na 57), em 214 pessoas; 513 em exercício em 2026-10-01; 428 pessoas com mais de um partido no período.
Por UF: AC 19, AL 15, AM 14, AP 21, BA 58, CE 49, DF 19, ES 17, GO 28, MA 41, MG 85, MS 13, MT 18, PA 28, PB 23, PE 42, PI 20, PR 54, RJ 87, RN 14, RO 15, RR 16, RS 49, SC 29, SE 18, SP 121, TO 16.

### Conferências

Amostra: dia 1º de cada mês de 2019-02 a 2026-10 (93 dias) por UF. Os detalhes de cada desvio, com evidência, estão no bloco `checks` de cada JSON.

Senado (datas inclusivas, como a API registra; esperado 3 por UF): 15 UF-dias diferentes de 3.

- 6 dias com 4: troca registrada no mesmo dia (DataFim de um e DataInicio de outro na mesma data): AL 2026-04-01, CE 2025-02-01, GO 2025-07-01, MT 2025-02-01, MT 2025-10-01, PI 2025-02-01. Em 2025-02-01, titulares afastados (CE, MT, PI) têm exercício de 2025-02-01 a 2025-02-02 ou 2025-02-03 com fim "Afastamento do exercício".
- 9 dias com 2: cadeira sem senador em exercício segundo a API: RJ 2020-11-01 (Arolde de Oliveira, "Falecimento" em 2020-10-21; Carlos Portinho a partir de 2020-11-03); RR 2020-11-01 a 2021-02-01 (Chico Rodrigues, "Licença Particular" até 2020-10-20, retorno em 2021-02-18, sem suplente em exercício no intervalo); CE 2021-11-01 (Tasso Jereissati até 2021-10-29, Chiquinho Feitosa a partir de 2021-11-03); CE 2024-04-01 (Augusta Brito até 2024-03-31, Janaína Farias a partir de 2024-04-02); PE 2022-12-01 (Jarbas Vasconcelos até 2022-11-21, Fernando Dueire a partir de 2022-12-07); MA 2026-08-01 (Ana Paula Lobato até 2026-07-30, Lourdinha Pereira a partir de 2026-08-05).
- Com a convenção "estado no fim do dia" seriam 16 desvios (os dias de troca deixam de contar 4, mas aparecem dias em que alguém tem DataFim no dia 1º e o sucessor só começa depois).

Câmara (estado no fim do dia: quem sai na data não conta, quem entra conta; esperado o número de vagas da UF, soma 513):

- Vagas usadas: AC 8, AL 9, AM 8, AP 8, BA 39, CE 22, DF 8, ES 10, GO 17, MA 18, MG 53, MS 8, MT 8, PA 17, PB 12, PE 25, PI 10, PR 30, RJ 46, RN 8, RO 8, RR 8, RS 31, SC 16, SE 8, SP 70, TO 8. A tabela está no script e foi conferida contra os próprios dados: titulares empossados no primeiro dia da legislatura batem com ela, exceto MG 52 e RJ 44 em 2019-02-01 e PI 9 em 2023-02-01 (posse individual em data posterior, por exemplo Marcelo Álvaro Antônio em 2019-02-06).
- Total nacional igual a 513 em 63 dos 93 dias; nos outros 30, entre 510 e 512. Nenhum dia acima de 513.
- 36 UF-dias abaixo do número de vagas (por 1 ou 2), todos com uma saída registrada antes e uma entrada depois: licença ou afastamento do titular com posse do suplente dias depois (por exemplo DF 2021-04-01: Flávia Arruda sai em 2021-03-31 com "Saída - Afastamento sem prazo determinado - Ministro de Estado", Laerte Bessa toma posse em 2021-04-07), suspensões (ES 2025-06-01 a 2025-08-01; MG 2025-08-01 a 2025-10-01), afastamento por decisão judicial (PB 2020-01-01 e 2020-02-01), retotalização (CE 2026-08-01), renúncia (SP 2023-10-01). A evidência gravada no JSON é a saída mais recente e a entrada seguinte na UF, uma aproximação que nem sempre aponta a cadeira exata.
- Com datas inclusivas seriam 63 desvios (trocas no mesmo dia contadas em dobro, por exemplo posses de 1º de janeiro).

### Termos de uso das fotos

Senado Federal. Página: https://www12.senado.leg.br/institucional/documentos/politica-de-uso-do-portal-do-senado-federal (lida em 2026-10-01):

> "Todo o conteúdo deste Portal é de propriedade autoral do Senado Federal, mas pode ser utilizado pelos usuários, desde que seja citada a fonte e para fins lícitos."

Termo da Agência Senado, para matérias e fotografias da agência. Página: https://www12.senado.leg.br/noticias/politica-de-uso (lida em 2026-10-01):

> "A reprodução de matérias e fotografias é livre, desde que não haja descaracterização de conteúdo e mediante a citação da Agência Senado e do autor."

As fotos oficiais são servidas pelo portal (`https://www.senado.leg.br/senadores/img/fotos-oficiais/senador{codigo}.jpg`, que redireciona para `https://legis.senado.leg.br/senadores/fotos-oficiais/{codigo}`), por isso o JSON aplica o termo do portal: crédito "Senado Federal". A API não informa o fotógrafo. Não foi encontrada licença Creative Commons declarada para essas fotos.

Câmara dos Deputados. Página: https://www2.camara.leg.br/termo-de-uso-e-politica-de-privacidade (ligada no rodapé de https://www.camara.leg.br/ como "Termos de uso"; lida em 2026-10-01):

> "7. Você pode reproduzir gratuitamente dados, imagens e infografias publicados no portal da Câmara, desde que citada a fonte "Câmara dos Deputados" e a autoria da informação, quando houver."

> "29. Todas as informações publicadas no Portal da Câmara são de domínio público, gratuitas e podem ser reproduzidas desde que citada a fonte "Câmara dos Deputados" e a autoria da informação, quando houver."

Crédito no JSON: "Câmara dos Deputados". A API não informa o fotógrafo de cada retrato. O site https://dadosabertos.camara.leg.br/ não traz texto de licença próprio na página inicial. Não foi encontrada licença Creative Commons declarada para essas fotos.

Só as URLs remotas são guardadas; nenhuma imagem foi baixada.

### Lacunas

- Senado: `start_reason` sempre null (a API não informa). "Afastamento do exercício" (AFO) não diz qual cargo o senador assumiu; o JSON não completa isso.
- Senado: 1 pessoa sem foto: Lael Varella (`senado:415`); a URL informada pela API responde 404 em 2026-10-01 (`photo_null_reason` no registro).
- Senado: a lista 56/57 só cobre mandatos que tocam essas legislaturas; isso basta para a janela, mas suplentes de mandatos anteriores a 2015 não entram (não exerceriam depois de 2019).
- Câmara: as regras de entrada e saída são derivadas do texto de `descricaoStatus`; um registro de entrada com texto fora do padrão seria perdido. A conferência de vagas não mostra nenhum dia acima de 513 nem vaga sem saída explicada, mas não prova a ausência de erro em trocas que se compensam no mesmo mês.
- Câmara: o histórico partidário é datado pelos registros de status. Uma troca de partido sem registro próprio aparece na data do próximo registro que a mostre.
- Câmara: `name` é o nome parlamentar atual (`ultimoStatus`), não necessariamente o usado em 2019; a foto também é a atual.
- As duas bases tratam datas em dia, sem hora; trocas no mesmo dia são ambíguas e a convenção de cada conferência está no próprio JSON.
- Vagas por UF da Câmara: a tabela foi conferida contra os dados, mas o JSON não cita a norma que a fixa.

## Deputados estaduais (2018, 2022) e prefeitos de SC (2020, 2024): eleitos

Coleta em 2026-10-01. Os dois arquivos registram **eleitos**, não **em exercício**: o que mostram é o resultado da eleição no cadastro de candidaturas do TSE. Posse, licenças, cassações, renúncias, suplentes que assumiram e trocas de partido depois da eleição não estão cobertos. O partido é o da candidatura.

### Arquivos gerados

| Arquivo | Script |
|---|---|
| `data/politicians/sc-mayors.json` | `pipelines/politicians/build_sc_mayors.py` |
| `data/politicians/state-deputies.json` | `pipelines/politicians/build_state_deputies.py` |

Os dois scripts usam só a biblioteca padrão do Python 3 e reaproveitam `tse_common.py` (`iter_rows`, `br_date`, `TSE_CAND_URL`, `ELECTED`, `WORK`) sem alterá-lo. Rodar com `POLITICIANS_WORK=<dir> python3 <script>`.

### Fontes

| Fonte | URL | Gerado em |
|---|---|---|
| TSE, cadastro de candidaturas 2018 | https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2018.zip | 13/11/2024 |
| TSE, cadastro de candidaturas 2020 | https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2020.zip | 06/01/2026 |
| TSE, cadastro de candidaturas 2022 | https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2022.zip | 30/09/2026 |
| TSE, cadastro de candidaturas 2024 | https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2024.zip | 30/09/2026 |
| TSE, códigos oficiais de UF e municípios segundo o TSE e o IBGE | https://cdn.tse.jus.br/estatistica/sead/odsele/municipio_tse_ibge/municipio_tse_ibge.zip (página: https://dadosabertos.tse.jus.br/dataset/codigos-oficiais-de-uf-e-municipios-segundo-o-tse-e-o-ibge) | 27/09/2026 |
| TSE, listagem das eleições suplementares, ciclo 2020 | https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2020/listaelesuplem/lista_eleicoes_suplementares_2020.zip | 06/12/2024 (data do arquivo no zip) |
| TSE, listagem das eleições suplementares, ciclo 2024 | https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2024/listaelesuplem/lista_eleicoes_suplementares_2024.zip | 22/06/2026 (data do arquivo no zip) |
| IBGE, API de localidades, municípios de SC | https://servicodados.ibge.gov.br/api/v1/localidades/estados/42/municipios | consulta em 2026-10-01 |
| Constituição Federal (arts. 27, 29, 32) | https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm | |

O cadastro de 2026 existe no disco e foi ignorado.

### Método

**Prefeitos de SC.** Linhas de `PREFEITO` e `VICE-PREFEITO` com `SG_UF = SC` dos cadastros 2020 e 2024. Cada eleição é agrupada por município (`SG_UE`), ano do cadastro, tipo (`NM_TIPO_ELEICAO`) e descrição (`DS_ELEICAO`). O segundo turno tem `CD_ELEICAO` próprio no TSE (426 no 1º turno de 2020, 427 no 2º), por isso o registro guarda o código e a data do 1º turno e, quando houver, um objeto `second_round` com código e data. O eleito é a linha com `DS_SIT_TOT_TURNO = 'ELEITO'`; no 2º turno, a linha do 1º turno tem situação `2º TURNO` e a do turno final tem `ELEITO`, então só a final entra (`round: 2`). Eleições suplementares (`ELEIÇÃO SUPLEMENTAR`) viram registros separados com `type: "suplementar"`, data (`DT_ELEICAO`) e descrição (`DS_ELEICAO`) do TSE. Mandato das ordinárias: 2021-01-01 a 2024-12-31 (2020) e 2025-01-01 a 2028-12-31 (2024), art. 29 da CF. Nas suplementares, `start` é null (o cadastro não informa posse) e `end` é 2024-12-31, o fim do mandato do ciclo. Quando há suplementar no ciclo, o registro da eleição ordinária ganha uma nota factual dizendo isso, sem afirmar quem exerceu o cargo.

**Deputados estaduais.** Linhas de `DEPUTADO ESTADUAL` e `DEPUTADO DISTRITAL` dos cadastros 2018 e 2022 com situação final `ELEITO POR QP` ou `ELEITO POR MÉDIA` (o conjunto `ELECTED` de `tse_common`), agrupadas por `SG_UF`. `federation` é o `SG_FEDERACAO` (null quando o TSE grava `#NULO`/`#NULO#`). O cadastro não informa datas de posse e elas variam por Constituição estadual, então `mandate.start` e `mandate.end` são null, com `duration_years: 4` (art. 27, par. 1, CF) e nota.

Nos dois arquivos, cada pessoa traz `record_basis` ("eleito: resultado da eleição no cadastro do TSE, não indica exercício do mandato"). Nenhuma coluna de dado pessoal é publicada (CPF, e-mail, título, nascimento, gênero, raça, instrução, ocupação ficam de fora).

### Tabela TSE-IBGE: existe e é oficial

A busca no portal de dados abertos do TSE (`https://dadosabertos.tse.jus.br/api/3/action/package_search?q=ibge`) devolve um único pacote, "Códigos oficiais de UF e municípios segundo o TSE e o IBGE", com o arquivo `municipio_tse_ibge.csv` (colunas `CD_MUNICIPIO_TSE`, `NM_MUNICIPIO_TSE`, `CD_MUNICIPIO_IBGE`, `NM_MUNICIPIO_IBGE`; 5.571 municípios, gerado em 27/09/2026). Para SC: 295 linhas, correspondência um para um nos dois sentidos. Conferência contra a API de localidades do IBGE: os 295 códigos IBGE da tabela do TSE são exatamente os 295 da API, e os 295 `SG_UE` dos cadastros 2020 e 2024 são exatamente os 295 da tabela. Os nomes do cadastro (`NM_UE`) e da API do IBGE coincidem nos 295 casos depois de normalizar acento, caixa, apóstrofo e hífen. **Nenhuma regra manual de nome foi necessária**, e o casamento por nome não foi usado para gerar o código: ele serve só de conferência. O nome publicado em `name` é o da API do IBGE; `name_tse` guarda o do TSE.

### Contagens

**Prefeitos de SC (295 municípios)**

| | 2020 | 2024 |
|---|---|---|
| Eleições ordinárias | 295 | 295 |
| Prefeitos eleitos na ordinária | 293 | 295 |
| Vice-prefeitos eleitos na ordinária | 293 | 295 |
| Ordinárias com 2º turno | 2 (Blumenau, Joinville) | 0 |
| Eleições suplementares no ciclo | 6 | 0 |
| Prefeitos e vices eleitos em suplementar | 6 e 6 | 0 |

Total de pessoas-registro: 1.188 (2 x (293 + 6 + 295)), todos com `id` único.

**Eleições suplementares do ciclo 2020 em SC** (as mesmas seis da listagem oficial do TSE para o ciclo):

| Município | Descrição no TSE | Data | Prefeito eleito (partido) | Vice eleito (partido) |
|---|---|---|---|---|
| Petrolândia | Nova Eleição Petrolândia | 2021-06-13 | IRONE (PP) | EGON (PSD) |
| Porto Belo | Nova Eleição - Porto Belo | 2022-06-05 | JOEL (MDB) | AILTO (PL) |
| Presidente Castello Branco | Nova Eleição - Pres. Castello Branco | 2022-06-05 | NEIVA KLEEMANN TONIELO (MDB) | ALFEU MIOTTO (PL) |
| Canoinhas | Eleição Suplementar Canoinhas 2022 | 2022-10-30 | JULIANA MACIEL (PSDB) | MARCOS HOMER (PODE) |
| Xavantina | Eleição Suplementar Xavantina 2023 | 2023-05-07 | LUCIANO ANTONIO ALTENHOFEN (PL) | ACACIO MOLOZZI (PT) |
| Brusque | Eleição Suplementar Brusque Set/2023 | 2023-09-03 | ANDRE VECHI (DC) | DECO BATISTI (PL) |

(A descrição de Canoinhas tem dois espaços no TSE; o JSON guarda o texto como veio.)

**Exceções na eleição ordinária de 2020**

- **Itapoá (TSE 81663, IBGE 4208450):** nenhuma candidatura a prefeito ou vice com situação final `ELEITO`; todas aparecem como `NÃO ELEITO`, e duas delas (uma a prefeito, uma a vice) têm candidatura `INAPTO`. A listagem oficial de suplementares do ciclo 2020 não traz Itapoá. O registro sai com `mayor: null` e `vice_mayor: null` e nota. Quem exerceu o cargo em Itapoá entre 2021 e 2024 não está nesses dados.
- **Petrolândia (TSE 82490):** nenhuma candidatura com `ELEITO` na ordinária; houve nova eleição em 2021-06-13 (registro suplementar acima).
- Em 2024 não há exceção: 295 municípios, um prefeito e um vice eleitos em cada, nenhum 2º turno e nenhuma suplementar no cadastro de SC.

**Deputados estaduais e distritais**

| | 2018 | 2022 |
|---|---|---|
| Deputados estaduais (26 UFs) | 1.035 | 1.035 |
| Deputados distritais (DF) | 24 | 24 |
| ELEITO POR QP | 886 | 847 |
| ELEITO POR MÉDIA | 173 | 212 |
| Com federação registrada | 0 | 258 |

Por UF (iguais em 2018 e 2022): SP 94, MG 77, RJ 70, BA 63, RS 55, PR 54, PE 49, CE 46, MA 42, GO 41, PA 41, SC 40, PB 36, ES 30, PI 30, AL 27, e 24 em AC, AM, AP, DF, MS, MT, RN, RO, RR, SE, TO.

### Checagens (todas passaram; as de número 1 a 4 foram provadas contra um controle quebrado)

1. Tabela TSE-IBGE um para um em SC (295/295) e códigos IBGE iguais aos da API do IBGE. Controle: removida uma linha (Florianópolis), a checagem disparou.
2. Cada município tem exatamente uma eleição ordinária por ano (2020 e 2024) e no máximo um prefeito e um vice `ELEITO` por eleição. Esta checagem disparou de verdade na primeira versão do script, que separava o 2º turno como outra eleição (Blumenau e Joinville), e levou à correção do agrupamento.
3. Suplementares do cadastro iguais à listagem oficial de eleições suplementares do TSE (ciclos 2020 e 2024). Controle: retirada Brusque da listagem, a checagem disparou.
4. Deputados: contagem por UF igual ao tamanho da assembleia (art. 27 da CF aplicado às bancadas federais em vigor; art. 32, par. 3, para o DF) e totais 1.035 + 24 nos dois anos. Controle: com SC esperado em 41, a checagem disparou.
5. `SQ_CANDIDATO` sem repetição; cargo distrital só no DF; uma única eleição (ordinária, 1º turno) por ano no recorte de deputados.
6. Nenhum travessão (U+2014) nem meia-risca (U+2013) nos JSON, scripts e nesta nota; o grep foi provado antes num arquivo de controle que contém os dois.

### Lacunas

- **Eleitos, não em exercício.** Os arquivos não dizem quem tomou posse, quem foi cassado, afastado ou substituído, nem quando. Isso vale para os prefeitos eleitos na ordinária de municípios que tiveram suplementar (Porto Belo, Presidente Castello Branco, Canoinhas, Xavantina, Brusque): o JSON registra o fato da nova eleição, não o motivo nem as datas.
- **Itapoá 2020** fica sem prefeito eleito nesses dados. Preencher exige outra fonte oficial (TRE-SC, Câmara Municipal ou o TCE-SC).
- **Datas de posse** de suplementares e de deputados estaduais não constam do cadastro do TSE. Para deputados, a data varia por Constituição estadual; o campo fica null.
- **Partido depois da eleição:** só o partido da candidatura. Mudanças de filiação não estão cobertas.
- **Federação:** só a sigla (`SG_FEDERACAO`, por exemplo `PT/PC do B/PV`); o nome por extenso (`NM_FEDERACAO`) não foi publicado, para manter o formato comum.
- **Instantâneo do cadastro:** cada zip reflete a data de geração indicada acima. Decisões judiciais posteriores (recontagens, anulação de votos) só aparecem se o TSE regerar o arquivo.

## Licenças das fotos (resumo)

| Origem | Termos | Onde foram lidos |
|---|---|---|
| Senado Federal (`UrlFotoParlamentar`) | "Todo o conteúdo deste Portal é de propriedade autoral do Senado Federal, mas pode ser utilizado pelos usuários, desde que seja citada a fonte e para fins lícitos." Sem licença Creative Commons declarada; crédito "Senado Federal". | https://www12.senado.leg.br/institucional/documentos/politica-de-uso-do-portal-do-senado-federal (e a política da Agência Senado, https://www12.senado.leg.br/noticias/politica-de-uso) |
| Câmara dos Deputados (`urlFoto`) | "Você pode reproduzir gratuitamente dados, imagens e infografias publicados no portal da Câmara, desde que citada a fonte "Câmara dos Deputados" e a autoria da informação, quando houver." Sem licença Creative Commons declarada; a API não informa o fotógrafo. | https://www2.camara.leg.br/termo-de-uso-e-politica-de-privacidade |
| Wikimedia Commons (União e governadores) | A licença de cada arquivo (CC BY, CC BY-SA, CC0, domínio público e outras), o autor e a página do arquivo ficam em cada foto, como o Commons registra. | página de cada arquivo (`file_page`) |

Nenhuma imagem foi baixada: os arquivos guardam só a URL remota.

## Diferenças de convenção entre os arquivos

- `union.json` e `governors.json`: `end` é o dia em que a pessoa deixou o cargo (o mesmo dia da posse do sucessor).
- `senators.json`: `end` é o último dia de exercício, como o Senado registra (`DataFim` inclusiva).
- `federal-deputies.json`: datas derivadas do histórico da Câmara, que tem hora; contagem ao fim do dia.
- `state-deputies.json` e `sc-mayors.json`: **eleitos**, não em exercício; sem datas de posse quando o TSE não as dá.

O site deve tratar a troca no mesmo dia mostrando quem assumiu.

## Lacunas gerais

- **Troca de partido no meio do mandato:** a lista nominal de filiados do TSE não é dado aberto. Governadores e cargos da União têm o partido de cada candidatura (2018 e 2022) e as trocas com data só quando uma fonte oficial ou a Agência Brasil dá a data. Mudanças de 2023 a 2026 sem fonte datada não foram registradas.
- **Candidaturas de 2026:** fora de todos os arquivos, por regra do projeto, inclusive como pista de partido.
- **Datas não conferidas no texto:** marcadas `verified: false` com o motivo (portal suspenso no período eleitoral, bloqueio de robôs no TSE, STJ e STF).
- **Fotos de governadores:** a escolha passa por nome e item do Wikidata; o QID e a página da Wikipédia ficam no dado para conferência humana antes de publicar.
