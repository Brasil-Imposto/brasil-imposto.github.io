# Folha de resposta: ataque à doação em cripto

Uma página, na ordem da folha de resposta da Security Alliance para um site comprometido (primeiro passo: tirar do ar). Vale para
qualquer alarme do monitor, um relato privado de falha, um endereço diferente no site, dinheiro saindo de um endereço do projeto,
ou um arquivo servido que não bate com o manifesto da publicação. Spec: `docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_seguranca-doacoes_2026-11-02.md`,
seções 4 e 10.

## 1. Tirar do ar (segundos)

Antes de entender o que houve, ninguém mais pode doar para um endereço trocado.

- Na tela: no repositório `Brasil-Imposto/brasil-imposto.github.io`, **Settings**, **Pages**, **Unpublish site**.
- Ou pelo terminal, com a conta de quem mantém: `gh api -X DELETE repos/Brasil-Imposto/brasil-imposto.github.io/pages`.
- O Pages guarda cópias por até 10 minutos (`cache-control: max-age=600`): conferir com `curl -s -o /dev/null -w '%{http_code}' "https://brasil-imposto.github.io/?n=$(date +%s)"` até dar 404.
- Se o problema é só uma moeda ou rede, e o site está íntegro, o passo 4 basta, sem tirar do ar.

## 2. Avisar

- Uma issue fixada no repositório: o que se sabe, desde quando, e que nenhuma doação deve ser feita até o aviso de volta. Sem
  detalhe que ajude o ataque.
- Quem relatou pelo relato privado recebe a resposta no próprio relato.

## 3. Apurar

- O log de auditoria da organização, na tela (organização gratuita: só na tela, por 180 dias): **Organization settings**, **Audit log**.
- As execuções do Actions dos dois repositórios e do monitor, e os e-mails de falha.
- O que mudou nos caminhos sensíveis: `git log -p -- data/support.json docs/superpowers/previews/assets/bi-cripto*.js .github/ deploy/ SECURITY.md`.
- O site no ar contra o manifesto da publicação: baixar o site e rodar `python3 docs/superpowers/tools/build-manifest.py verify <pasta>`.
- A configuração: `python3 docs/superpowers/tools/settings-check.py`.
- A blockchain: as saídas de cada endereço no explorador de cada rede (o registro de endereços está no `SECURITY.md`).

## 4. Pausar a moeda ou a rede

No `data/support.json`, o `status` da rede vira `"paused"`; o botão fica apagado com "Pausada" e o endereço sai de toda página.
Pull request para o `staging`, etiqueta `seguranca-revisada` depois do último push, merge, e a produção pelo caminho normal com o
aviso de produção.

## 5. Trocar os endereços

- Carteira nova, criada pela pessoa mantenedora fora de qualquer sessão de agente; a frase de recuperação nunca entra numa sessão.
- Pull request com os endereços novos no `data/support.json`, o teste dos endereços fixados e o registro do `SECURITY.md`, com o `guard`.
- A cópia de endereços do monitor (`pins.json` em `Brasil-Imposto/monitor`), por pull request lá.

## 6. Antes de voltar

- A causa achada e escrita na issue.
- A falha corrigida, com um teste que a veja falhar antes da correção.
- Uma publicação nova a partir de uma fonte conferida, com o manifesto novo.
- As credenciais trocadas: tokens e chaves de deploy dos repositórios, as sessões da conta do GitHub, a chave do GitHub App do monitor.
- Religar: `gh api -X POST repos/Brasil-Imposto/brasil-imposto.github.io/pages -f build_type=workflow` e `gh workflow run pages.yml -R Brasil-Imposto/brasil-imposto.github.io`, conferindo a página no ar.
- A issue fixada atualizada dizendo que voltou.
