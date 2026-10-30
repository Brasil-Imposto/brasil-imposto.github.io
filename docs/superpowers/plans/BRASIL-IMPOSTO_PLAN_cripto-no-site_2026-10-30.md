# Plano: a doação em cripto feita dentro do site

> **Para quem executa:** siga as tarefas na ordem, marcando os passos (`- [ ]`). Cada teste é escrito antes do código e visto falhando; cada um tem o seu controle plantado (D3, seção 8 da spec). Texto de tela em português do Brasil; identificadores, chaves JSON e commits em inglês. Sem travessão em nada que se escreve; nenhum endereço de e-mail. Cada commit com `--signoff` (o `dco` do repositório recusa sem) e citando no código só decisões já públicas no ramo.

**Objetivo:** quem doa escolhe a moeda, a rede e o valor dentro do modal do Apoie, vê o endereço do projeto (mostrado, nunca digitado) e confirma; a confirmação final é na carteira dele (D207).

**Arquitetura:** o site continua estático. A página carrega um bloco JSON com o que o envio precisa, gerado de `data/support.json`; duas peças em `assets/`, carregadas só quando quem doa escolhe uma moeda: `bi-cripto-core.js` (contas e links, sem página nem carteira, testado no Node) e `bi-cripto.js` (tela e carteiras). Sem conta, sem chave, sem WalletConnect (D208); sem biblioteca de rede. O destino vem sempre do bloco JSON.

**Tecnologia:** Python 3 (`support_data.py`, `apoie.py`, `unittest`), JavaScript sem empacotador, `node --test`, `playwright-core` nas sondas. Duas bibliotecas MIT guardadas no próprio site: `qrcode-generator` 2.0.4 e `@crossmarkio/sdk` 0.4.0.

**Spec:** `docs/superpowers/specs/BRASIL-IMPOSTO_SPEC_cripto-no-site_2026-10-29.md` (aprovada, D209). **Desenho aprovado:** a rodada `cripto-envio-r1` (D208), gerador `private/apoie/build_cripto_envio_r1.py`.

---

## Arquivos

| Arquivo | O que faz |
|---|---|
| `data/support.json` | Ganha, por rede, `chain_id`, `tx_url`, `native_symbol`, `native_decimals`, `trust_coin_id`, `add_chain`, `first_min`; por moeda, `decimals`, `contract`, `issuer_listed` |
| `docs/superpowers/tools/support_data.py` | Confere as chaves novas; `send_data()` monta o bloco JSON da página |
| `docs/superpowers/tools/apoie.py` | A vista da cripto no desenho aprovado: moeda, rede, endereço, valor, botão |
| `docs/superpowers/tools/site_chrome.py` | Passa o perfil ao modal (no staging, o XRP abre para o primeiro envio do mantenedor, D206) |
| `docs/superpowers/previews/assets/bi-cripto-core.js` | Novo. Valor em unidades inteiras, dados do `transfer`, links, a entrada pelo link do site |
| `docs/superpowers/previews/assets/bi-cripto.js` | Novo. Tela e carteiras |
| `docs/superpowers/previews/assets/vendor/` | Novo. As duas bibliotecas MIT, com licença |
| `pipelines/tests/cripto_core.test.cjs`, `pipelines/tests/test_cripto_core.py` | Novos. Testes do núcleo no Node e o teste Python que os roda no `ci` |
| `pipelines/tests/test_support.py` | Dados, modal, lista fechada de métodos, peso |
| `docs/superpowers/tools/cripto-check.cjs` | Novo. Sonda com carteiras de mentira |
| `docs/superpowers/tools/apoie-check.cjs` | Segue a vista nova (uma linha de rede por vez) |

## Tarefa 0: ramo e dono (D164)

- [ ] **Passo 1:** conferir que ninguém mais tem esta tarefa: `gh pr list --search cripto`, `git ls-remote --heads origin | grep -i cripto`, `ListAgents`. Achou dono: parar e avisar o autor.
- [ ] **Passo 2:** criar o ramo a partir do `staging`, que já tem a vista da cripto e os ícones (#163):
```bash
cd ~/Documents/Brasil-Imposto
git fetch origin
git worktree add .worktrees/cripto-envio -b feat/cripto-envio origin/staging
```
Rodar tudo daqui em diante dentro de `.worktrees/cripto-envio`. O pull request abre para `staging`.

## Tarefa 1: os dados do envio

**Arquivos:** `data/support.json`, `docs/superpowers/tools/support_data.py`, `pipelines/tests/test_support.py`.

- [ ] **Passo 1: escrever os testes** em `pipelines/tests/test_support.py`, antes de `class RulesTest`:

```python
# The contracts of the tokens, read on each issuer's own page on 2026-10-29 (the two of BNB Smart Chain from the chain: neither
# issuer lists them). data/support.json must hold exactly these, like the addresses in PINNED.
PINNED_TOKENS = {("ethereum", "USDT"): ("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6, True),
                 ("ethereum", "USDC"): ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6, True),
                 ("bsc", "USDT"): ("0x55d398326f99059fF775485246999027B3197955", 18, False),
                 ("bsc", "USDC"): ("0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", 18, False),
                 ("solana", "USDT"): ("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", 6, True),
                 ("solana", "USDC"): ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 6, True),
                 ("tron", "USDT"): ("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", 6, True)}


def token_diff(data):
    """The tokens of data that differ from PINNED_TOKENS (an empty list: every contract as pinned)."""
    found = {(n["id"], c["coin"]): (c["contract"], c["decimals"], c["issuer_listed"])
             for g in data["crypto"]["groups"] for n in g["networks"] for c in n["coins"] if c.get("contract")}
    return sorted(k for k in set(found) | set(PINNED_TOKENS) if found.get(k) != PINNED_TOKENS.get(k))


class SendDataTest(unittest.TestCase):
    def test_the_contracts_are_the_pinned_ones(self):
        self.assertEqual(token_diff(committed()), [])

    def test_control_a_changed_contract_is_caught(self):
        d = committed()
        coin = next(c for n in d["crypto"]["groups"][1]["networks"] for c in n["coins"] if c["coin"] == "USDT")
        coin["contract"] = "0x" + "1" * 40
        self.assertEqual(token_diff(d), [("ethereum", "USDT")])

    def test_each_contract_passes_its_network_checksum(self):
        d = committed()
        for g in d["crypto"]["groups"]:
            for n in g["networks"]:
                for c in n["coins"]:
                    if c.get("contract"):
                        self.assertIsNone(support_data.address_problem(g["format"], c["contract"]), c["contract"])

    def test_a_bad_value_of_the_send_fails(self):
        cases = {"tx_url": lambda n, c: n.update(tx_url="https://x.org/tx"), "decimals": lambda n, c: c.update(decimals=None),
                 "native_decimals": lambda n, c: n.update(native_decimals="6"), "chain_id": lambda n, c: n.update(chain_id=None)}
        for name, change in cases.items():
            with self.subTest(key=name):
                d = committed()
                n = d["crypto"]["groups"][1]["networks"][0]
                change(n, n["coins"][0])
                self.assertTrue(any(name in p for p in support_data.problems(d)), name)

    def test_control_a_token_without_contract_or_with_a_bad_one_fails(self):
        for bad in (None, "0x" + "aB" * 20):   # all digits would pass EIP-55: it has no letters to check
            d = committed()
            coin = next(c for n in d["crypto"]["groups"][1]["networks"] for c in n["coins"] if c["coin"] == "USDC")
            coin["contract"] = bad
            self.assertTrue(any("USDC" in p for p in support_data.problems(d)), bad)

    def test_the_page_block_holds_only_open_networks_and_never_more_than_the_send_needs(self):
        d = committed()
        blob = support_data.send_data(d)
        self.assertEqual([n["id"] for n in blob["networks"]], ["bitcoin", "ethereum", "bsc", "solana", "tron"])
        tron = next(n for n in blob["networks"] if n["id"] == "tron")
        self.assertEqual(tron["address"], PINNED["tron"])
        self.assertEqual(tron["coins"]["USDT"], {"contract": PINNED_TOKENS[("tron", "USDT")][0], "decimals": 6, "issuer_listed": True})
        self.assertEqual(support_data.send_data(d, staging=True)["networks"][-1]["id"], "xrp-ledger", "D206: staging opens XRP")
        self.assertEqual(support_data.send_data(d, staging=True)["networks"][-1]["first_min"], "1")
```

- [ ] **Passo 2: rodar e ver falhar**

Rodar: `uv run --locked python -B -m unittest pipelines.tests.test_support.SendDataTest`
Esperado: FAIL (`KeyError` ou `AttributeError: send_data`).

- [ ] **Passo 3: pôr os dados.** Script único, rodado uma vez a partir da raiz do ramo:

```python
import json
p = "data/support.json"
d = json.load(open(p, encoding="utf-8"))
TOK = {("ethereum", "USDT"): ("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6, True), ("ethereum", "USDC"): ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6, True),
       ("bsc", "USDT"): ("0x55d398326f99059fF775485246999027B3197955", 18, False), ("bsc", "USDC"): ("0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", 18, False),
       ("solana", "USDT"): ("Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", 6, True), ("solana", "USDC"): ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 6, True),
       ("tron", "USDT"): ("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", 6, True)}
NET = {"bitcoin": dict(native_symbol="BTC", native_decimals=8, tx_url="https://mempool.space/tx/{tx}"),
       "ethereum": dict(native_symbol="ETH", native_decimals=18, tx_url="https://etherscan.io/tx/{tx}", chain_id=1, trust_coin_id=60),
       "bsc": dict(native_symbol="BNB", native_decimals=18, tx_url="https://bscscan.com/tx/{tx}", chain_id=56, trust_coin_id=20000714,
                   add_chain={"chainName": "BNB Smart Chain", "nativeCurrency": {"name": "BNB", "symbol": "BNB", "decimals": 18},
                              "rpcUrls": ["https://bsc-dataseed.bnbchain.org"], "blockExplorerUrls": ["https://bscscan.com"]}),
       "solana": dict(native_symbol="SOL", native_decimals=9, tx_url="https://solscan.io/tx/{tx}"),
       "tron": dict(native_symbol="TRX", native_decimals=6, tx_url="https://tronscan.org/#/transaction/{tx}"),
       "xrp-ledger": dict(native_symbol="XRP", native_decimals=6, tx_url="https://xrpscan.com/tx/{tx}", first_min="1")}
for g in d["crypto"]["groups"]:
    for n in g["networks"]:
        n.update(NET[n["id"]])
        for c in n["coins"]:
            if (n["id"], c["coin"]) in TOK:
                c["contract"], c["decimals"], c["issuer_listed"] = TOK[(n["id"], c["coin"])]
            else:
                c["contract"], c["decimals"], c["issuer_listed"] = None, n["native_decimals"], True
open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
```

Conferir com `git diff --stat data/support.json` que nenhuma linha antiga mudou de valor. O endereço de transação da Tronscan não abriu fora de um navegador: conferir no teste do mantenedor (Tarefa 7).

- [ ] **Passo 4: a regra em `support_data.py`.** Dentro do laço `for n in g["networks"]:` de `structure_problems`, depois da conferência do `explorer_url`:

```python
            if not (str(n.get("tx_url", "")).startswith("https://") and str(n.get("tx_url", "")).count("{tx}") == 1):
                out.append(f"{g['id']}/{n['id']}.tx_url: needs https and one {{tx}}")
            if not isinstance(n.get("native_decimals"), int) or isinstance(n.get("native_decimals"), bool):
                out.append(f"{g['id']}/{n['id']}.native_decimals: a whole number")
            if g["format"] == "evm" and not isinstance(n.get("chain_id"), int):
                out.append(f"{g['id']}/{n['id']}.chain_id: a whole number")
            for c in n["coins"]:
                if not isinstance(c.get("decimals"), int) or isinstance(c.get("decimals"), bool):
                    out.append(f"{g['id']}/{n['id']}/{c['coin']}.decimals: a whole number")
                if c["coin"] != n.get("native_symbol") and (not c.get("contract") or address_problem(g["format"], c["contract"])):
                    out.append(f"{g['id']}/{n['id']}/{c['coin']}: a valid contract")
```

E uma função nova, depois de `networks_of`:

```python
def send_data(data, staging=False):
    """What the send in the modal reads from the page: only the networks open in this build (staging also opens those on soon, so the
    maintainer can make the first XRP donation through the site). The destination the page sends to is the address here, and only it."""
    keep = ("chain_id", "trust_coin_id", "add_chain", "first_min")
    nets = []
    for g in data["crypto"]["groups"]:
        for n in g["networks"]:
            if n["status"] == "live" or staging:
                nets.append({"id": n["id"], "name": n["name"], "family": g["format"], "address": g["address"], "tx_url": n["tx_url"],
                             "native_symbol": n["native_symbol"], **{k: n[k] for k in keep if k in n},
                             "coins": {c["coin"]: {"contract": c["contract"], "decimals": c["decimals"], "issuer_listed": c["issuer_listed"]}
                                       for c in n["coins"]}})
    return {"networks": nets}
```

- [ ] **Passo 5: rodar e ver passar**

Rodar: `uv run --locked python -B -m unittest pipelines.tests.test_support`
Esperado: OK.

- [ ] **Passo 6: commit**

```bash
git add data/support.json docs/superpowers/tools/support_data.py pipelines/tests/test_support.py
git commit --signoff -m "feat(apoie): the data of the crypto send, each contract pinned (spec cripto-no-site, 5 and 6)"
```

## Tarefa 2: o núcleo (contas e links, sem página)

**Arquivos:** criar `docs/superpowers/previews/assets/bi-cripto-core.js`, `pipelines/tests/cripto_core.test.cjs`, `pipelines/tests/test_cripto_core.py`.

- [ ] **Passo 1: escrever os testes do Node** em `pipelines/tests/cripto_core.test.cjs`:

```js
// The pure part of the crypto send (spec cripto-no-site, section 8, items 1 to 3). BI_CORE points at another copy for the control.
const test = require('node:test');
const assert = require('node:assert');
const path = require('path');
const C = require(process.env.BI_CORE || path.join(__dirname, '..', '..', 'docs', 'superpowers', 'previews', 'assets', 'bi-cripto-core.js'));

test('a typed value becomes whole units, with comma or point, and never rounds', () => {
  assert.strictEqual(C.toUnits('10', 6).units, 10000000n);
  assert.strictEqual(C.toUnits('0,005', 8).units, 500000n);
  assert.strictEqual(C.toUnits('1.5', 18).units, 1500000000000000000n);
  assert.strictEqual(C.toUnits('.5', 6).units, 500000n);
  assert.strictEqual(C.toUnits('0.0000001', 6).code, 'too_many_decimals');
  for (const bad of ['', ' ', 'abc', '0', '0,00', '-1', '1.000,50', '1e3', '0x10']) assert.strictEqual(C.toUnits(bad, 6).code, 'invalid', bad);
});

test('the same value differs between chains: 1 USDT is 6 places on Tron and 18 on BNB Smart Chain', () => {
  assert.strictEqual(C.toUnits('1', 6).units, 1000000n);
  assert.strictEqual(C.toUnits('1', 18).units, 1000000000000000000n);
});

test('the minimum of the first XRP', () => {
  assert.strictEqual(C.belowMin(C.toUnits('0.5', 6).units, '1', 6), true);
  assert.strictEqual(C.belowMin(C.toUnits('1', 6).units, '1', 6), false);
  assert.strictEqual(C.belowMin(C.toUnits('0.5', 6).units, undefined, 6), false);
});

test('the transfer call data', () => {
  assert.strictEqual(C.erc20Transfer('0xb947cC8445841cf40AFCA723804d06855bea7bc7', 1000000n),
    '0xa9059cbb000000000000000000000000b947cc8445841cf40afca723804d06855bea7bc7'
    + '00000000000000000000000000000000000000000000000000000000000f4240');
  assert.strictEqual(C.hex(255n), '0xff');
});

test('whole units back to plain decimal text', () => {
  assert.strictEqual(C.decimalText(1500000n, 6), '1.5');
  assert.strictEqual(C.decimalText(1000000n, 6), '1');
  assert.strictEqual(C.decimalText(5n, 8), '0.00000005');
});

test('payment links in each standard form', () => {
  const sol = 'FUYqFTFwvF8fgm1NmbRXAEERtRLDry1DCQfNgbZyFv8f', btc = 'bc1qevkvnl6rvpfyyyjzk08lckz9xn3936qhp86zna', xrp = 'rwJXvMdap5E7C49ZkfAjpeAMLd15UmEch2';
  assert.strictEqual(C.paymentLink('solana', sol, 1500000000n, 9, null), `solana:${sol}?amount=1.5&label=Brasil-Imposto`);
  assert.strictEqual(C.paymentLink('solana', sol, 2000000n, 6, 'MINT'), `solana:${sol}?amount=2&spl-token=MINT&label=Brasil-Imposto`);
  assert.strictEqual(C.paymentLink('bitcoin', btc, 500000n, 8, null), `bitcoin:${btc}?amount=0.005&label=Brasil-Imposto`);
  assert.strictEqual(C.paymentLink('xrp', xrp, 1000000n, 6, null), `https://xaman.app/detect/request:${xrp}?amount=1&network=XRPL`);
  assert.strictEqual(C.paymentLink('evm', '0x', 1n, 18, null), null);
});

test('opening the site inside a wallet app carries the choice and never an address', () => {
  const url = C.siteLink('https://brasil-imposto.github.io/', 'USDT', 'bsc', '10');
  assert.strictEqual(url, 'https://brasil-imposto.github.io/#apoie-cripto?moeda=USDT&rede=bsc&valor=10');
  assert.strictEqual(C.openInApp('metamask', url, 20000714), 'https://link.metamask.io/dapp/brasil-imposto.github.io/#apoie-cripto?moeda=USDT&rede=bsc&valor=10');
  assert.strictEqual(C.openInApp('trust', url, 20000714), 'https://link.trustwallet.com/open_url?coin_id=20000714&url=' + encodeURIComponent(url));
  assert.strictEqual(C.openInApp('outra', url, 60), null);
});

test('the entry link is read with care: only coin, network and value, each checked', () => {
  const nets = [{ id: 'tron', coins: { USDT: {} } }];
  assert.deepStrictEqual(C.parseEntry('#apoie-cripto?moeda=USDT&rede=tron&valor=10', nets), { coin: 'USDT', net: 'tron', amount: '10' });
  assert.deepStrictEqual(C.parseEntry('#apoie-cripto?moeda=USDT&rede=tron&valor=10&address=rGolpe', nets), { coin: 'USDT', net: 'tron', amount: '10' });
  assert.strictEqual(C.parseEntry('#apoie-cripto?moeda=DOGE&rede=tron', nets), null);
  assert.strictEqual(C.parseEntry('#apoie-cripto?moeda=USDT&rede=marte', nets), null);
  assert.deepStrictEqual(C.parseEntry('#apoie-cripto?moeda=USDT&rede=tron&valor=<script>', nets), { coin: 'USDT', net: 'tron', amount: '' });
  assert.strictEqual(C.parseEntry('#outra', nets), null);
});
```

- [ ] **Passo 2: o teste Python que os roda no `ci`,** `pipelines/tests/test_cripto_core.py`:

```python
"""Runs the tests of the crypto send's pure core (bi-cripto-core.js) in node, as pipelines/tests/test_df_balance.py does for a page's own
code, and proves they can fail: a copy of the core with the decimals rule broken must not pass."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parents[1] / "docs" / "superpowers" / "previews" / "assets" / "bi-cripto-core.js"


def run(core=None):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is needed to run the crypto core's tests (the ci runner has it)")
    env = dict(os.environ, **({"BI_CORE": str(core)} if core else {}))
    return subprocess.run([node, "--test", str(HERE / "cripto_core.test.cjs")], env=env, capture_output=True, text=True).returncode


class CryptoCoreTest(unittest.TestCase):
    def test_the_core_passes(self):
        self.assertEqual(run(), 0)

    def test_control_a_broken_decimals_rule_fails(self):
        text = CORE.read_text(encoding="utf-8")
        broken = text.replace("frac.length > decimals", "frac.length > decimals + 9")
        self.assertNotEqual(broken, text, "the plant landed")
        with tempfile.TemporaryDirectory() as d:
            copy = Path(d) / "bi-cripto-core.js"
            copy.write_text(broken, encoding="utf-8")
            self.assertNotEqual(run(copy), 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Passo 3: rodar e ver falhar**

Rodar: `uv run --locked python -B -m unittest pipelines.tests.test_cripto_core`
Esperado: FAIL ou ERROR (o arquivo do núcleo ainda não existe).

- [ ] **Passo 4: escrever o núcleo,** `docs/superpowers/previews/assets/bi-cripto-core.js`:

```js
// The pure part of the crypto send (spec cripto-no-site): no page and no wallet, so node can test it. Every value in whole units is a
// BigInt: never a floating point number.
(function (root, make) {
  if (typeof module === 'object' && module.exports) module.exports = make(); else root.BiCriptoCore = make();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const fail = (code, extra) => Object.assign({ ok: false, code }, extra);

  // "10", "0,005" or ".5" to whole units. More decimal places than the coin has is an error, never a rounding.
  function toUnits(text, decimals) {
    const s = String(text).trim().replace(',', '.');
    if (!/^(\d+(\.\d+)?|\.\d+)$/.test(s)) return fail('invalid');
    const [whole, frac = ''] = s.split('.');
    if (frac.length > decimals) return fail('too_many_decimals', { decimals });
    const units = BigInt((whole || '0') + frac.padEnd(decimals, '0'));
    return units > 0n ? { ok: true, units } : fail('invalid');
  }
  const belowMin = (units, min, decimals) => min !== undefined && units < toUnits(min, decimals).units;
  const pad = (hex) => hex.padStart(64, '0');
  const erc20Transfer = (to, units) => '0xa9059cbb' + pad(to.slice(2).toLowerCase()) + pad(units.toString(16));
  const hex = (units) => '0x' + units.toString(16);

  function decimalText(units, decimals) {
    const s = units.toString().padStart(decimals + 1, '0');
    const frac = s.slice(s.length - decimals).replace(/0+$/, '');
    return s.slice(0, s.length - decimals) + (frac ? '.' + frac : '');
  }
  // A link the wallet itself turns into the transaction (Solana Pay, BIP-321, Xaman's payment request); null where a network has none.
  function paymentLink(family, address, units, decimals, token) {
    const n = decimalText(units, decimals);
    if (family === 'solana') return `solana:${address}?amount=${n}${token ? `&spl-token=${token}` : ''}&label=Brasil-Imposto`;
    if (family === 'bitcoin') return `bitcoin:${address}?amount=${n}&label=Brasil-Imposto`;
    if (family === 'xrp') return `https://xaman.app/detect/request:${address}?amount=${n}&network=XRPL`;
    return null;
  }
  const siteLink = (base, coin, net, amount) => `${base}#apoie-cripto?moeda=${encodeURIComponent(coin)}&rede=${encodeURIComponent(net)}&valor=${encodeURIComponent(amount)}`;
  function openInApp(wallet, url, coinId) {
    if (wallet === 'metamask') return 'https://link.metamask.io/dapp/' + url.replace(/^https?:\/\//, '');
    if (wallet === 'trust') return `https://link.trustwallet.com/open_url?coin_id=${coinId}&url=${encodeURIComponent(url)}`;
    return null;
  }
  // The site's own link only ever chooses: the coin and the network must exist in the page's data, and nothing else in it is read.
  function parseEntry(hash, networks) {
    const m = /^#apoie-cripto\?(.*)$/.exec(hash || '');
    if (!m) return null;
    const q = new URLSearchParams(m[1]), coin = q.get('moeda'), net = q.get('rede'), valor = q.get('valor') || '';
    const n = networks.find((x) => x.id === net);
    if (!n || !Object.prototype.hasOwnProperty.call(n.coins, coin)) return null;
    return { coin, net, amount: /^[\d.,]{1,30}$/.test(valor) ? valor : '' };
  }
  return { toUnits, belowMin, erc20Transfer, hex, decimalText, paymentLink, siteLink, openInApp, parseEntry };
}));
```

- [ ] **Passo 5: rodar e ver passar**

Rodar: `uv run --locked python -B -m unittest pipelines.tests.test_cripto_core`
Esperado: OK (2 testes).

- [ ] **Passo 6: commit**

```bash
git add docs/superpowers/previews/assets/bi-cripto-core.js pipelines/tests/cripto_core.test.cjs pipelines/tests/test_cripto_core.py
git commit --signoff -m "feat(apoie): the pure core of the crypto send, tested in node (spec cripto-no-site, 8)"
```

## Tarefa 3: as duas bibliotecas, guardadas no site

**Arquivos:** criar `docs/superpowers/previews/assets/vendor/qrcode.js`, `crossmark-sdk.js`, `LICENSE.txt`; `pipelines/tests/test_support.py`.

- [ ] **Passo 1: o teste que fixa os arquivos,** em `pipelines/tests/test_support.py`, antes de `class RulesTest`:

```python
VENDOR = REPO / "docs" / "superpowers" / "previews" / "assets" / "vendor"
VENDORED = {"qrcode.js": "79ec86f82856005b1c887905cfccfcfbec3821ca61c7fd5a952faa5f778f791c",      # qrcode-generator 2.0.4, MIT
            "crossmark-sdk.js": "785beebb27c7d6f200b1827a25b2351fc22721b610a028abdf88295ad711de59"}  # @crossmarkio/sdk 0.4.0, MIT


class VendoredTest(unittest.TestCase):
    def test_each_library_is_the_exact_file_reviewed(self):
        for name, want in VENDORED.items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256((VENDOR / name).read_bytes()).hexdigest(), want)
        self.assertIn("MIT", (VENDOR / "LICENSE.txt").read_text(encoding="utf-8"))

    def test_control_a_changed_byte_is_caught(self):
        b = bytearray((VENDOR / "qrcode.js").read_bytes())
        b[0] ^= 1
        self.assertNotEqual(hashlib.sha256(bytes(b)).hexdigest(), VENDORED["qrcode.js"])
```

- [ ] **Passo 2: rodar e ver falhar:** `uv run --locked python -B -m unittest pipelines.tests.test_support.VendoredTest` (FAIL: arquivo não existe).

- [ ] **Passo 3: baixar as duas e escrever a licença**

```bash
V=docs/superpowers/previews/assets/vendor; mkdir -p $V
curl -sL -o $V/qrcode.js "https://cdn.jsdelivr.net/npm/qrcode-generator@2.0.4/dist/qrcode.js"
curl -sL -o $V/crossmark-sdk.js "https://cdn.jsdelivr.net/npm/@crossmarkio/sdk@0.4.0/pack/umd/index.js"
curl -sL "https://cdn.jsdelivr.net/npm/qrcode-generator@2.0.4/LICENSE" > $V/LICENSE.txt
printf '\n---\n@crossmarkio/sdk 0.4.0: licença MIT (package.json do pacote).\n' >> $V/LICENSE.txt
```

Conferir que `LICENSE.txt` tem o texto MIT do `qrcode-generator`. Se o arquivo `LICENSE` não vier, baixar `LICENSE.md` do mesmo pacote (`npm view` não é preciso: a lista está em `https://data.jsdelivr.com/v1/packages/npm/qrcode-generator@2.0.4`).

- [ ] **Passo 4: rodar e ver passar** (o mesmo comando do passo 2). Um hash diferente é para parar: o arquivo não é o que foi lido em 2026-10-30.

- [ ] **Passo 5: commit**

```bash
git add docs/superpowers/previews/assets/vendor pipelines/tests/test_support.py
git commit --signoff -m "feat(apoie): the QR and Crossmark libraries kept in the site, each file pinned by hash"
```

## Tarefa 4: a vista da cripto no desenho aprovado

**Arquivos:** `docs/superpowers/tools/apoie.py`, `docs/superpowers/tools/site_chrome.py`, `docs/superpowers/tools/apoie-check.cjs`, `pipelines/tests/test_support.py`, as quatro páginas publicadas (reconstruídas).

O desenho aprovado (rodada `cripto-envio-r1`): moeda (com ícone), rede (botões), o endereço da rede escolhida com "Copiar" e o explorador, valor, botão, a linha da corretora e o aviso. Hoje a vista mostra todas as redes da moeda ao mesmo tempo: passa a mostrar uma linha por vez. Sem JavaScript do envio (arquivo que não carregou), a escolha de moeda e rede e o "Copiar" continuam funcionando: é a reserva.

- [ ] **Passo 1: escrever os testes** em `pipelines/tests/test_support.py`, antes de `class RulesTest`:

```python
class SendViewTest(unittest.TestCase):
    def view(self, profile="production"):
        return build(on_soon_crypto_live(), profile=profile)["inicio"]["header"]

    def test_the_order_of_the_view(self):
        t = text(self.view())
        self.assertTrue(in_order(t, ["Apoiar com cripto", "Moeda", "Rede", "Valor", apoie.EXCHANGE_LINE, apoie.WARNING]))

    def test_each_network_has_its_button_and_only_the_first_row_shows(self):
        h = self.view()
        usdt = re.search(r'<div class="bi-ap-coin" data-coin="USDT" hidden>(.*?)<p class="bi-ap-pick">', h, re.S).group(1)
        self.assertEqual(re.findall(r'data-net-btn="([^"]+)"', usdt), ["ethereum", "bsc", "solana", "tron"])
        self.assertEqual(re.findall(r'<div class="bi-ap-net" data-net="([^"]+)"( hidden)?>', usdt),
                         [("ethereum", ""), ("bsc", " hidden"), ("solana", " hidden"), ("tron", " hidden")])

    def test_the_send_block_and_the_data_block_are_in_the_page(self):
        h = self.view()
        self.assertEqual(h.count('class="bi-ap-send"'), 1)
        self.assertIn('id="bi-ap-amount"', h)
        self.assertIn('data-send', h)
        blob = json.loads(re.search(r'<script type="application/json" id="bi-cripto-data">(.*?)</script>', h, re.S).group(1))
        self.assertEqual(blob, support_data.send_data(on_soon_crypto_live()))

    def test_staging_opens_xrp_and_production_does_not(self):
        self.assertNotIn(PINNED["xrp"], self.view("production"))
        self.assertIn(PINNED["xrp"], self.view("staging"))

    def test_the_note_of_the_tokens_the_issuer_does_not_list_and_the_seed_line(self):
        self.assertIn(apoie.NOT_ISSUER, self.view())
        self.assertIn(apoie.NO_SEED, self.view())

    def test_control_the_order_check_catches_a_moved_warning(self):
        h = self.view()
        moved = h.replace(f'<p class="bi-ap-warn">{apoie.escape(apoie.WARNING)}</p>', "")
        moved = moved.replace("<h2 tabindex=\"-1\">Apoiar com cripto</h2>", f"<h2 tabindex=\"-1\">Apoiar com cripto</h2><p>{apoie.escape(apoie.WARNING)}</p>")
        self.assertNotEqual(moved, h, "the plant landed")
        self.assertFalse(in_order(text(moved), ["Apoiar com cripto", "Moeda", "Rede", "Valor", apoie.EXCHANGE_LINE, apoie.WARNING]))
```

- [ ] **Passo 2: rodar e ver falhar:** `uv run --locked python -B -m unittest pipelines.tests.test_support.SendViewTest` (FAIL ou ERROR).

- [ ] **Passo 3: `apoie.py`, os textos,** ao lado de `WARNING`:

```python
EXCHANGE_LINE = "Vai enviar de uma corretora? Copie o endereço acima e envie pela mesma rede."
NOT_ISSUER = "Nesta rede, o USDT e o USDC não são emitidos pela Tether nem pela Circle: são versões de terceiros."
NO_SEED = "O site nunca pede a sua frase de recuperação nem a sua chave privada."
```

- [ ] **Passo 4: `apoie.py`, a linha de rede e a vista.** Trocar `_row` e o trecho da vista da cripto em `modal`:

```python
def _row(group, network, standard, first=True):
    name = network["name"] + (f" ({standard})" if standard else "")
    a = group["address"]
    url = network["explorer_url"].replace("{address}", a)
    return (f'<div class="bi-ap-net" data-net="{escape(network["id"])}"{"" if first else " hidden"}><div class="bi-ap-net-name">{escape(name)}</div><code>{escape(a)}</code>'
            f'<div class="bi-ap-net-act"><button type="button" class="bi-ap-copy" data-copy="{escape(a)}">Copiar</button>'
            f'<a href="{escape(url)}" target="_blank" rel="noopener">{escape(network["explorer"])}</a></div></div>')


def _net_buttons(rows):
    out = "".join(f'<button type="button" class="bi-ap-netbtn" data-net-btn="{escape(n["id"])}" aria-pressed="{"true" if i == 0 else "false"}">'
                  f'{escape(n["name"] + (f" ({s})" if s else ""))}</button>' for i, (_g, n, s) in enumerate(rows))
    return f'<span class="bi-ap-lab">Rede</span><div class="bi-ap-nets">{out}</div>'
```

No corpo de `modal`, com um parâmetro novo `staging=False` (assinatura `def modal(data, keyless=False, staging=False):`):

```python
    crypto = ""
    if crypto_live:
        coins, panels = "", ""
        for c in support_data.COINS:
            rows = support_data.networks_of(data, c, live=not staging)
            icon = f'<img src="assets/cripto/{c.lower()}.svg" alt="" width="20" height="20" loading="lazy">'
            if not rows:
                coins += f'<button type="button" class="bi-ap-coinbtn bi-ap-coinsoon" disabled>{icon}{c} <span class="bi-ap-tag">{SOON}</span></button>'
                continue
            coins += f'<button type="button" class="bi-ap-coinbtn" data-coin-btn="{c}" aria-pressed="false">{icon}{c}</button>'
            panels += (f'<div class="bi-ap-coin" data-coin="{c}" hidden>' + _net_buttons(rows)
                       + '<span class="bi-ap-lab">Endereço do Brasil-Imposto</span>'
                       + "".join(_row(*r, first=i == 0) for i, r in enumerate(rows))
                       + (f'<p class="bi-ap-pick">{escape(PICK_NETWORK)}</p>' if len(rows) > 1 else "") + '</div>')
        blob = json.dumps(support_data.send_data(data, staging), ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
        send = ('<div class="bi-ap-send" hidden><label class="bi-ap-lab" for="bi-ap-amount">Valor</label>'
                '<div class="bi-ap-amt"><input id="bi-ap-amount" inputmode="decimal" autocomplete="off" placeholder="0"><span data-unit></span></div>'
                '<p class="bi-ap-err" data-msg hidden></p><p class="bi-ap-note" data-note></p>'
                f'<p class="bi-ap-note" data-issuer hidden>{escape(NOT_ISSUER)}</p>'
                '<div class="bi-ap-wallets" data-wallets hidden></div><div class="bi-ap-qr" data-qr hidden></div>'
                '<button type="button" class="bi-ap-cta bi-ap-sendbtn" data-send disabled>Conectar carteira</button>'
                '<a class="bi-ap-cta bi-ap-sendbtn" data-pay hidden></a>'
                f'<p class="bi-ap-alt">{escape(EXCHANGE_LINE)}</p><p class="bi-ap-note">{escape(NO_SEED)}</p></div>'
                '<div class="bi-ap-done" data-done hidden></div>')
        crypto = ('<section class="bi-ap-view" data-view="crypto" hidden><h2 tabindex="-1">Apoiar com cripto</h2>'
                  f'<span class="bi-ap-lab">Moeda</span><div class="bi-ap-coins">{coins}</div>{panels}{send}'
                  f'<p class="bi-ap-warn">{escape(WARNING)}</p>'
                  f'<script type="application/json" id="bi-cripto-data">{blob}</script></section>')
```

Em `site_chrome.py`, `with_support(head, data, keyless=False)` passa `keyless` também como `staging` (`apoie.modal(data, keyless, staging=keyless)`): `keyless` já é "o perfil é staging". Pôr `import json` no topo de `apoie.py`.

- [ ] **Passo 5: `apoie.py`, os estilos,** depois de `.bi-ap-pick`:

```css
.bi-ap-lab { display: block; margin: 16px 0 8px; font: 800 12px Manrope, system-ui, sans-serif; letter-spacing: .06em; text-transform: uppercase; color: #5B6773; }
.bi-ap-nets { display: flex; flex-wrap: wrap; gap: 8px; }
.bi-ap-netbtn { height: 36px; padding: 0 13px; border: 1px solid #D5DBE1; border-radius: 10px; background: #fff; color: #14202B; font: 700 13px Manrope, system-ui, sans-serif; cursor: pointer; }
.bi-ap-netbtn[aria-pressed="true"] { border: 2px solid #12803F; background: #EFF7F1; color: #12803F; }
.bi-ap-amt { display: flex; align-items: center; height: 52px; padding: 0 14px; border: 2px solid #14202B; border-radius: 12px; }
.bi-ap-amt input { flex: 1; min-width: 0; border: 0; outline: 0; font: 800 22px Manrope, system-ui, sans-serif; color: #14202B; background: transparent; }
.bi-ap-amt span { font: 800 15px "JetBrains Mono", ui-monospace, monospace; color: #5B6773; }
.bi-ap-note { margin: 6px 0 0 !important; font-size: 13px !important; color: #5B6773 !important; }
.bi-ap-sendbtn { display: flex; align-items: center; justify-content: center; box-sizing: border-box; width: 100%; height: 50px; margin-top: 16px; border-radius: 12px; font-size: 16px; text-decoration: none; }
.bi-ap-sendbtn[disabled] { opacity: .5; cursor: default; }
.bi-ap-alt { margin: 10px 0 0 !important; font-size: 13px !important; text-align: center; color: #5B6773 !important; }
.bi-ap-wallets { display: grid; gap: 8px; margin-top: 14px; }
.bi-ap-wallets button, .bi-ap-wallets a { display: flex; align-items: center; gap: 10px; height: 44px; padding: 0 12px; border: 1px solid #D5DBE1; border-radius: 10px; background: #fff; color: #14202B; font: 700 14px Manrope, system-ui, sans-serif; text-decoration: none; cursor: pointer; }
.bi-ap-wallets img { width: 24px; height: 24px; border-radius: 6px; }
.bi-ap-qr { margin: 14px auto 0; width: 200px; }
.bi-ap-qr svg { display: block; width: 100%; height: auto; }
.bi-ap-done { text-align: center; padding: 10px 0 4px; }
.bi-ap-done h3 { margin: 12px 0 4px !important; }
```

- [ ] **Passo 6: `apoie.py`, o script do modal.** Trocar o manipulador de `[data-coin-btn]` por:

```js
  // The crypto view: a coin shows its networks, one address row at a time, and opens the send block; the send's own two files load
  // only then, and if they fail the choice and "Copiar" still work.
  const sendBlock = root.querySelector('.bi-ap-send');
  let sendAsked = false;
  const loadSend = () => {
    if (sendAsked) return; sendAsked = true;
    ['assets/bi-cripto-core.js', 'assets/bi-cripto.js'].reduce((p, src) => p.then(() => new Promise((ok, no) => {
      const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = no; document.head.appendChild(s);
    })), Promise.resolve()).catch(() => { if (sendBlock) sendBlock.hidden = true; });
  };
  const picked = (coin, net) => { root.dataset.coin = coin; root.dataset.net = net; root.dispatchEvent(new CustomEvent('bi-cripto-pick')); };
  const pickNet = (panel, id) => {
    panel.querySelectorAll('[data-net-btn]').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.netBtn === id)));
    panel.querySelectorAll('.bi-ap-net').forEach((r) => { r.hidden = r.dataset.net !== id; });
    picked(panel.dataset.coin, id);
  };
  root.querySelectorAll('[data-net-btn]').forEach((b) => b.addEventListener('click', () => pickNet(b.closest('.bi-ap-coin'), b.dataset.netBtn)));
  const pickCoin = (b, net) => {
    const c = b.dataset.coinBtn;
    root.querySelectorAll('[data-coin-btn]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    root.querySelectorAll('.bi-ap-coin').forEach((p) => { p.hidden = p.dataset.coin !== c; });
    const panel = root.querySelector(`.bi-ap-coin[data-coin="${c}"]`);
    if (sendBlock) sendBlock.hidden = false;
    loadSend();
    pickNet(panel, net || panel.querySelector('[data-net-btn]').dataset.netBtn);
  };
  root.querySelectorAll('[data-coin-btn]').forEach((b) => b.addEventListener('click', () => pickCoin(b)));
  // The site's own link (#apoie-cripto?moeda=USDT&rede=tron&valor=10), used to open the site inside a wallet app: it only chooses.
  const entry = /^#apoie-cripto\?(.*)$/.exec(location.hash);
  if (entry) {
    const q = new URLSearchParams(entry[1]);
    const b = [...root.querySelectorAll('[data-coin-btn]')].find((x) => x.dataset.coinBtn === q.get('moeda'));
    if (b) { const net = [...root.querySelectorAll(`.bi-ap-coin[data-coin="${b.dataset.coinBtn}"] [data-net-btn]`)].find((x) => x.dataset.netBtn === q.get('rede'));
      opener.click(); show('crypto'); pickCoin(b, net && net.dataset.netBtn); }
  }
```

Conferir o nome da função que abre o modal no script (`open`, ligada ao `opener`): o trecho usa `opener.click()`, que passa por ela.

- [ ] **Passo 7: `apoie-check.cjs` segue a vista nova.** Em `expected()`, cada linha passa a levar `id: n.id`. Na conferência `coins`, trocar a contagem das linhas visíveis por:

```js
            const nets = await p.$$eval(`.bi-ap-coin[data-coin="${coin}"] [data-net-btn]`, (es) => es.filter((e) => e.getClientRects().length).length);
            const rowsShown = await p.$$eval(`.bi-ap-coin[data-coin="${coin}"] .bi-ap-net`, (es) => es.filter((e) => e.getClientRects().length).length);
            if (!(c.length === 1 && c[0] === coin && nets === n && rowsShown === 1)) bad.push(`${coin}: panels ${JSON.stringify(c)}, ${nets} networks, ${rowsShown} rows shown`);
```

Na conferência `addresses`, antes de ler cada linha, tocar no botão da rede dela, e ler só a linha visível:

```js
            const want = expected(coin);
            for (const [i, e] of want.entries()) {
              await tap(p, `.bi-ap-coin[data-coin="${coin}"] [data-net-btn="${e.id}"]`); await p.waitForTimeout(60);
              const sel = `.bi-ap-coin[data-coin="${coin}"] .bi-ap-net[data-net="${e.id}"]`;
              const r = await p.$eval(sel, (x) => ({ name: x.querySelector('.bi-ap-net-name').textContent.trim(), shown: x.querySelector('code').textContent.trim(),
                href: x.querySelector('a').getAttribute('href'), explorer: x.querySelector('a').textContent.trim() }));
              await p.evaluate(() => navigator.clipboard.writeText(''));
              await p.locator(`${sel} [data-copy]`).click(); await p.waitForTimeout(80);
              const copied = await p.evaluate(() => navigator.clipboard.readText()).catch((x) => `(clipboard not readable: ${x.message})`);
              rowsSeen += 1;
              for (const [what, got, ok] of [['name', r.name, e.name], ['shown', r.shown, e.address], ['copied', copied, e.address],
                ['explorer link', r.href, e.href], ['explorer name', r.explorer, e.explorer]]) {
                if (got !== ok) wrong.push(`${coin} ${r.name}: ${what} ${JSON.stringify(got)}, the file has ${JSON.stringify(ok)}`);
              }
            }
```

Esse trecho substitui o laço `for (const [i, r] of rows.entries())` e a leitura de `rows` que vem antes dele. Rodar depois do passo 8.

- [ ] **Passo 8: reconstruir as páginas e rodar**

```bash
cd docs/superpowers/tools && env -u BI_SUPPORT_JSON python3 -B build-platform-preview.py && env -u BI_SUPPORT_JSON python3 -B build-site-chrome.py && env -u BI_SUPPORT_JSON python3 -B build-notes-page.py && cd ../../..
uv run --locked python -B -m unittest discover -s pipelines/tests
```
Esperado: OK. Testes antigos que contavam linhas de rede visíveis mudam junto, mantendo a intenção.

- [ ] **Passo 9: montar e rodar a sonda** (`apoie-check.cjs` normal e `--control`, no staging e na produção; ver o método em `CONTRIBUTING.md`). Esperado: 0 falhas; no controle, tudo falha, menos o `top` conhecido do staging em 420 e 320 px. Screenshot da vista em 1440 e 390 px, conferido contra a rodada `cripto-envio-r1`.

- [ ] **Passo 10: commit**

```bash
git add -A docs/superpowers/tools docs/superpowers/previews pipelines/tests
git commit --signoff -m "feat(apoie): the crypto view as drawn: coin, network, one address row, amount and the send button"
```

## Tarefa 5: o envio (a sonda primeiro, depois o código)

**Arquivos:** criar `docs/superpowers/tools/cripto-check.cjs` e `docs/superpowers/previews/assets/bi-cripto.js`.

- [ ] **Passo 1: escrever a sonda,** `docs/superpowers/tools/cripto-check.cjs`:

```js
// The crypto send (spec cripto-no-site, section 8, item 4) in a real browser with fake wallets: nothing leaves the machine. For every coin
// and network open in the build, the request the wallet receives must hold the address, contract, value and chain of data/support.json;
// and the cases of section 3.3: refusals, a wrong network, a double click, the links on a phone.
// Usage: node cripto-check.cjs <base url of a served staging build> [--control]
// --control swaps the address in the page's data block for another one: every send check must then fail.
// Env: PW_CORE, CHROME_HEADLESS, BI_SUPPORT_JSON (optional).
const fs = require('fs');
const path = require('path');
const SUPPORT = JSON.parse(fs.readFileSync(process.env.BI_SUPPORT_JSON || path.join(__dirname, '..', '..', '..', 'data', 'support.json'), 'utf8'));
const FROM = '0x1111111111111111111111111111111111111111';
const fakeWallets = () => {
  window.__calls = []; window.__fake = { chain: '0x1', reject: null, noChain: false };
  const f = window.__fake, refuse = () => Object.assign(new Error('refused'), { code: 4001 });
  const evm = { request: async ({ method, params }) => {
    window.__calls.push({ method, params });
    if (f.reject === method) throw refuse();
    if (method === 'eth_requestAccounts') return ['0x1111111111111111111111111111111111111111'];
    if (method === 'eth_chainId') return f.chain;
    if (method === 'wallet_switchEthereumChain') { if (f.noChain) { f.noChain = false; throw Object.assign(new Error('x'), { code: 4902 }); } f.chain = params[0].chainId; return null; }
    if (method === 'wallet_addEthereumChain') return null;
    if (method === 'eth_sendTransaction') return '0xabc';
    throw new Error('unexpected ' + method);
  } };
  addEventListener('eip6963:requestProvider', () => dispatchEvent(new CustomEvent('eip6963:announceProvider', { detail: {
    info: { uuid: 'u1', name: 'Fake', icon: 'data:image/gif;base64,R0lGODlhAQABAAAAACw=', rdns: 'x.fake' }, provider: evm } })));
  const tronWeb = { transactionBuilder: { triggerSmartContract: async (contract, fn, opts, params, from) => { window.__calls.push({ method: 'trigger', contract, fn, params, from }); return { transaction: { txID: 'tx1' } }; } },
    trx: { sign: async (t) => { window.__calls.push({ method: 'sign' }); if (f.reject === 'sign') throw 'Confirmation declined by user'; return t; }, sendRawTransaction: async () => ({ result: true, txid: 'tx1' }) } };
  window.tron = { isTronLink: true, tronWeb, request: async ({ method }) => { window.__calls.push({ method: 'tron:' + method }); return ['TQ7vFakeFakeFakeFakeFakeFakeFakek2Pd']; } };
  window.unisat = { requestAccounts: async () => ['bc1qfake'], sendBitcoin: async (to, sats) => { window.__calls.push({ method: 'sendBitcoin', to, sats }); return 'btctx'; } };
};
const nets = () => SUPPORT.crypto.groups.flatMap((g) => g.networks.map((n) => ({ ...n, address: g.address, family: g.format })));
const units = (text, decimals) => { const [w, f = ''] = text.split('.'); return BigInt(w + f.padEnd(decimals, '0')); };

(async () => {
  const args = process.argv.slice(2), base = args.find((a) => !a.startsWith('--')).replace(/\/?$/, '/'), control = args.includes('--control');
  const { chromium } = require(process.env.PW_CORE || 'playwright-core');
  const browser = await chromium.launch({ executablePath: process.env.CHROME_HEADLESS, args: ['--no-sandbox'] });
  const rows = [], report = (name, ok, detail) => rows.push({ name, ok, detail });
  const open = async (phone) => {
    const ctx = await browser.newContext(phone ? { viewport: { width: 390, height: 800 }, isMobile: true, hasTouch: true,
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1' } : { viewport: { width: 1280, height: 860 } });
    await ctx.route('**/*', async (r) => {
      const u = r.request().url();
      if (!u.startsWith(base)) return r.abort();
      if (control && r.request().resourceType() === 'document') {
        const res = await r.fetch();
        return r.fulfill({ response: res, body: (await res.text()).replaceAll(SUPPORT.crypto.groups[1].address, '0x2222222222222222222222222222222222222222').replaceAll(SUPPORT.crypto.groups[3].address, 'TQ7vFakeFakeFakeFakeFakeFakeFakek2Pd').replaceAll(SUPPORT.crypto.groups[0].address, 'bc1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq').replaceAll(SUPPORT.crypto.groups[2].address, '1'.repeat(32)).replaceAll(SUPPORT.crypto.groups[4].address, 'rrrrrrrrrrrrrrrrrrrrBZbvji') });
      }
      return r.continue();
    });
    if (!phone) await ctx.addInitScript(fakeWallets);
    const p = await ctx.newPage();
    await p.goto(base + 'como-ler-o-mapa.html'); await p.waitForSelector('.bi-apoie-btn');
    await p.$eval('.bi-apoie-btn', (e) => e.click()); await p.waitForTimeout(150);
    await p.$eval('.bi-ap-view[data-view="main"] [data-go="crypto"]', (e) => e.click()); await p.waitForTimeout(150);
    return { ctx, p };
  };
  const pick = async (p, coin, net) => { await p.click(`[data-coin-btn="${coin}"]`); await p.click(`.bi-ap-coin[data-coin="${coin}"] [data-net-btn="${net}"]`);
    await p.waitForFunction(() => window.BiCripto && window.BiCripto.ready); };
  const send = async (p, amount) => { await p.fill('#bi-ap-amount', amount); await p.click('[data-send]'); await p.waitForTimeout(150);
    if (await p.$('[data-wallets] button')) { await p.click('[data-wallets] button'); await p.waitForTimeout(150); }
    await p.click('[data-send]'); await p.waitForTimeout(250); };
  // every coin and network with a browser wallet
  for (const n of nets().filter((x) => ['evm', 'tron', 'bitcoin'].includes(x.family))) {
    for (const c of n.coins) {
      const { ctx, p } = await open(false);
      await pick(p, c.coin, n.id); await send(p, '1.5');
      const calls = await p.evaluate(() => window.__calls);
      const done = await p.$eval('[data-done]', (e) => e.textContent).catch(() => '');
      const want = units('1.5', c.decimals);
      let ok;
      if (n.family === 'evm') {
        const tx = (calls.find((x) => x.method === 'eth_sendTransaction') || { params: [{}] }).params[0];
        const pad = (h) => h.padStart(64, '0');
        ok = c.contract ? tx.to === c.contract && tx.data === '0xa9059cbb' + pad(n.address.slice(2).toLowerCase()) + pad(want.toString(16)) && !tx.value
          : tx.to === n.address && tx.value === '0x' + want.toString(16) && !tx.data;
        ok = ok && tx.from === FROM && calls.some((x) => x.method === 'wallet_switchEthereumChain' || n.chain_id === 1);
      } else if (n.family === 'tron') {
        const t = calls.find((x) => x.method === 'trigger') || { params: [] };
        ok = t.contract === c.contract && t.params[0].value === n.address && t.params[1].value === want.toString();
      } else {
        const b = calls.find((x) => x.method === 'sendBitcoin') || {};
        ok = b.to === n.address && BigInt(b.sats || 0) === want;
      }
      report(`send ${c.coin} on ${n.id}`, !!ok && /Doação enviada/.test(done), JSON.stringify(calls.slice(-1)).slice(0, 160));
      await ctx.close();
    }
  }
  // the links on a phone (no wallet injected): Solana, Bitcoin, XRP Ledger
  for (const n of nets().filter((x) => ['solana', 'bitcoin', 'xrp'].includes(x.family))) {
    for (const c of n.coins) {
      const { ctx, p } = await open(true);
      await pick(p, c.coin, n.id); await p.fill('#bi-ap-amount', '1.5'); await p.waitForTimeout(150);
      const href = await p.$eval('[data-pay]', (a) => a.getAttribute('href') || '');
      report(`link ${c.coin} on ${n.id}`, href.includes(n.address) && href.includes('amount=1.5') && (!c.contract || href.includes(c.contract)), href.slice(0, 120));
      await ctx.close();
    }
  }
  // section 3.3
  const c1 = await open(false); await pick(c1.p, 'ETH', 'ethereum');
  await c1.p.evaluate(() => { window.__fake.reject = 'eth_sendTransaction'; }); await send(c1.p, '0.1');
  report('refused on the wallet', /Envio cancelado na carteira/.test(await c1.p.$eval('[data-msg]', (e) => e.textContent)), 'message'); await c1.ctx.close();
  const c2 = await open(false); await pick(c2.p, 'BNB', 'bsc');
  await c2.p.evaluate(() => { window.__fake.reject = 'wallet_switchEthereumChain'; }); await send(c2.p, '0.1');
  const noSend = await c2.p.evaluate(() => !window.__calls.some((x) => x.method === 'eth_sendTransaction'));
  report('a refused network change sends nothing', noSend && /Troque para BNB Smart Chain/.test(await c2.p.$eval('[data-msg]', (e) => e.textContent)), `no send: ${noSend}`); await c2.ctx.close();
  const c3 = await open(false); await pick(c3.p, 'BNB', 'bsc');
  await c3.p.evaluate(() => { window.__fake.noChain = true; }); await send(c3.p, '0.1');
  report('a missing network is added', await c3.p.evaluate(() => window.__calls.some((x) => x.method === 'wallet_addEthereumChain')), 'add'); await c3.ctx.close();
  const c4 = await open(false); await pick(c4.p, 'USDT', 'tron'); await c4.p.fill('#bi-ap-amount', '0.0000001'); await c4.p.waitForTimeout(100);
  report('too many decimals', /até 6 casas/.test(await c4.p.$eval('[data-msg]', (e) => e.textContent)) && await c4.p.$eval('[data-send]', (b) => b.disabled), 'message and disabled'); await c4.ctx.close();
  const c5 = await open(false); await pick(c5.p, 'ETH', 'ethereum'); await c5.p.fill('#bi-ap-amount', '0.1'); await c5.p.click('[data-send]'); await c5.p.waitForTimeout(150);
  await c5.p.evaluate(() => { const b = document.querySelector('[data-send]'); b.click(); b.click(); }); await c5.p.waitForTimeout(250);
  report('a double click sends once', (await c5.p.evaluate(() => window.__calls.filter((x) => x.method === 'eth_sendTransaction').length)) === 1, 'once'); await c5.ctx.close();
  await browser.close();
  for (const r of rows) console.log(`${r.ok ? 'PASS' : 'FAIL'} ${r.name}: ${r.detail}`);
  const bad = rows.filter((r) => !r.ok), sends = rows.filter((r) => /^(send|link) /.test(r.name));
  console.log(`${rows.length} checks, ${bad.length} failed${control ? ' (control run)' : ''}`);
  if (control) { const passed = sends.filter((r) => r.ok); console.log(passed.length ? `BROKEN CONTROL: ${passed.map((r) => r.name).join(', ')}` : 'control: every send check failed, as it must'); process.exit(passed.length ? 1 : 0); }
  process.exit(bad.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
```

- [ ] **Passo 2: montar o staging e ver a sonda falhar**

Rodar: `uv run --locked python -B docs/superpowers/tools/build-site.py --profile staging --out /tmp/bi-stag`, servir essa pasta (`python3 -m http.server 8742 --bind 127.0.0.1`) e `node docs/superpowers/tools/cripto-check.cjs http://127.0.0.1:8742/`.
Esperado: erro ou FAIL (`bi-cripto.js` não existe, `window.BiCripto` nunca chega).

- [ ] **Passo 3: escrever o envio,** `docs/superpowers/previews/assets/bi-cripto.js`:

```js
// The crypto send inside the Apoie modal (spec cripto-no-site). The destination only ever comes from the block the page carries
// (#bi-cripto-data, built from data/support.json): a link, a field or a wallet never supplies it. Only plain transfers: the wallet
// methods used here are a closed list, checked by pipelines/tests/test_support.py.
(function () {
  'use strict';
  const C = window.BiCriptoCore, root = document.getElementById('bi-apoie');
  const data = JSON.parse(document.getElementById('bi-cripto-data').textContent);
  const $ = (s) => root.querySelector(s);
  const input = $('#bi-ap-amount'), unit = $('[data-unit]'), msg = $('[data-msg]'), note = $('[data-note]'), issuer = $('[data-issuer]');
  const wallets = $('[data-wallets]'), qrBox = $('[data-qr]'), sendBtn = $('[data-send]'), payLink = $('[data-pay]'), done = $('[data-done]'), block = $('.bi-ap-send');
  const phone = navigator.maxTouchPoints > 0 && /Android|iPhone|iPad/.test(navigator.userAgent);
  const state = { wallet: null, account: null, busy: false };
  const evmFound = [], tronFound = [];
  addEventListener('eip6963:announceProvider', (e) => { if (!evmFound.some((w) => w.info.uuid === e.detail.info.uuid)) { evmFound.push(e.detail); render(); } });
  addEventListener('TIP6963:announceProvider', (e) => { if (!tronFound.some((w) => w.info.uuid === e.detail.info.uuid)) { tronFound.push(e.detail); render(); } });
  dispatchEvent(new Event('eip6963:requestProvider'));
  dispatchEvent(new Event('TIP6963:requestProvider'));

  const net = () => data.networks.find((n) => n.id === root.dataset.net);
  const coin = () => net() && net().coins[root.dataset.coin];
  const say = (text) => { msg.textContent = text || ''; msg.hidden = !text; };
  const show = (el, on) => { el.hidden = !on; };

  // The wallets of this browser for a network: announced ones first, then what older wallets and app browsers inject.
  function found(family) {
    if (family === 'evm') return evmFound.length ? evmFound : window.ethereum ? [{ info: { uuid: 'injected', name: 'Carteira deste navegador' }, provider: window.ethereum }] : [];
    if (family === 'tron') return tronFound.length ? tronFound : window.tron ? [{ info: { uuid: 'tron', name: 'TronLink' }, provider: window.tron }] : [];
    if (family === 'bitcoin') return window.unisat ? [{ info: { uuid: 'unisat', name: 'UniSat' }, provider: window.unisat }] : [];
    if (family === 'xrp') return window.xrpl && window.xrpl.isCrossmark ? [{ info: { uuid: 'crossmark', name: 'Crossmark' }, provider: null }] : [];
    return [];
  }

  function amount() {
    const n = net(), c = coin();
    if (!c) return null;
    if (!input.value.trim()) { say(''); return null; }
    const r = C.toUnits(input.value, c.decimals);
    if (!r.ok) { say(r.code === 'too_many_decimals' ? `${root.dataset.coin} aceita até ${c.decimals} casas depois da vírgula.` : 'Informe um valor maior que zero.'); return null; }
    if (C.belowMin(r.units, n.first_min, c.decimals)) { say(`O primeiro envio para esta conta precisa ser de ${n.first_min} ${root.dataset.coin} ou mais (a reserva da rede).`); return null; }
    say('');
    return r.units;
  }

  function render() {
    const n = net(), c = coin();
    if (!n) return;
    const units = amount(), text = units === null ? '' : C.decimalText(units, c.decimals);
    unit.textContent = root.dataset.coin;
    const end = n.address.slice(-4);
    note.textContent = state.busy && state.wallet ? `Confirme na janela da sua carteira. Confira se o endereço termina em ${end}.`
      : state.wallet ? `Na carteira, confira se o endereço termina em ${end}.`
        : c.contract ? `Você vai precisar de um pouco de ${n.native_symbol} na carteira para a taxa da rede.` : 'A taxa da rede é paga pela sua carteira.';
    show(issuer, !c.issuer_listed);
    const here = found(n.family);
    const link = units === null ? null : C.paymentLink(n.family, n.address, units, c.decimals, c.contract);
    show(qrBox, false); show(payLink, false); show(sendBtn, false); show(wallets, false);
    if (state.wallet) {                                                     // connected: the last step
      show(sendBtn, true); sendBtn.textContent = text ? `Confirmar doação de ${text} ${root.dataset.coin}` : 'Confirmar doação'; sendBtn.disabled = units === null || state.busy;
    } else if (here.length) {                                               // a wallet in this browser
      show(sendBtn, true); sendBtn.textContent = 'Conectar carteira'; sendBtn.disabled = units === null || state.busy;
    } else if (phone && link) {                                             // the wallet app, filled in by a payment link
      show(payLink, true); payLink.textContent = `Confirmar doação de ${text} ${root.dataset.coin}`; payLink.href = link;
      note.textContent += ` Se a carteira não trouxer o valor, digite ${text} ${root.dataset.coin}. Confira se o endereço termina em ${end}.`;
    } else if (phone && (n.family === 'evm' || n.family === 'tron')) {      // the site inside the wallet app, where the same flow runs
      wallets.replaceChildren(...appLinks(n, input.value)); show(wallets, wallets.children.length > 0);
      if (!wallets.children.length) say(`Abra esta página no navegador do app da sua carteira, ou copie o endereço acima.`);
    } else if (link) {                                                      // a computer with no wallet: a QR code for the phone
      show(qrBox, true); drawQr(link);
    } else if (units !== null) {
      say(`Nenhuma carteira de ${n.name} neste navegador. Instale uma extensão ou copie o endereço acima.`);
    }
  }

  function appLinks(n, value) {
    const url = C.siteLink(location.href.split('#')[0], root.dataset.coin, n.id, value);
    return [['metamask', 'Abrir na MetaMask'], ['trust', 'Abrir na Trust Wallet']].filter(() => n.family === 'evm').map(([id, label]) => {
      const a = document.createElement('a'); a.href = C.openInApp(id, url, n.trust_coin_id); a.textContent = label; return a;
    });
  }

  let qrLoading = null;
  function drawQr(link) {
    qrLoading = qrLoading || new Promise((ok, no) => { const s = document.createElement('script'); s.src = 'assets/vendor/qrcode.js'; s.onload = ok; s.onerror = no; document.head.appendChild(s); });
    qrLoading.then(() => { const q = window.qrcode(0, 'M'); q.addData(link); q.make(); qrBox.innerHTML = q.createSvgTag({ cellSize: 4, margin: 2 }); }).catch(() => show(qrBox, false));
  }

  async function ensureChain(p, n) {
    const want = C.hex(BigInt(n.chain_id));
    if (await p.request({ method: 'eth_chainId' }) !== want) {
      try { await p.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: want }] }); } catch (e) {
        if (e.code !== 4902 || !n.add_chain) throw e;
        await p.request({ method: 'wallet_addEthereumChain', params: [Object.assign({ chainId: want }, n.add_chain)] });
        await p.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: want }] });
      }
    }
    if (await p.request({ method: 'eth_chainId' }) !== want) throw { code: 'wrong_chain' };
  }

  async function connect(w, n) {
    if (n.family === 'evm' || n.family === 'tron') return (await w.provider.request({ method: 'eth_requestAccounts' }))[0];
    if (n.family === 'bitcoin') return (await w.provider.requestAccounts())[0];
    await new Promise((ok, no) => { const s = document.createElement('script'); s.src = 'assets/vendor/crossmark-sdk.js'; s.onload = ok; s.onerror = no; document.head.appendChild(s); });
    for (let i = 0; i < 40 && !(window.crossmark && window.crossmark.methods); i++) await new Promise((ok) => setTimeout(ok, 100));
    const r = await window.crossmark.methods.signInAndWait();
    return r.response.data.address;
  }

  async function transfer(w, n, c, units) {
    if (n.family === 'evm') {
      await ensureChain(w.provider, n);
      const tx = c.contract ? { from: state.account, to: c.contract, data: C.erc20Transfer(n.address, units) } : { from: state.account, to: n.address, value: C.hex(units) };
      return w.provider.request({ method: 'eth_sendTransaction', params: [tx] });
    }
    if (n.family === 'tron') {
      const t = w.provider.tronWeb;
      const { transaction } = await t.transactionBuilder.triggerSmartContract(c.contract, 'transfer(address,uint256)', { feeLimit: 100000000 },
        [{ type: 'address', value: n.address }, { type: 'uint256', value: units.toString() }], state.account);
      const r = await t.trx.sendRawTransaction(await t.trx.sign(transaction));
      if (!r.result) throw { code: 'refused' };
      return r.txid || transaction.txID;
    }
    if (n.family === 'bitcoin') return w.provider.sendBitcoin(n.address, Number(units));
    const r = await window.crossmark.methods.signAndSubmitAndWait({ TransactionType: 'Payment', Account: state.account, Destination: n.address, Amount: units.toString() });
    return r.response.data.resp.result.hash;
  }

  const refused = (e) => e === 'Confirmation declined by user' || (e && e.code === 4001);
  function explain(e, n, step) {
    if (e && e.code === -32002) return say('Abra a carteira: há um pedido esperando a sua resposta.');
    if (e && e.code === 'wrong_chain') return say(`A carteira continua em outra rede. Troque para ${n.name} para enviar.`);
    if (step === 'connect') return say(refused(e) ? 'Conexão recusada na carteira. Nada foi enviado.' : 'Desbloqueie a carteira e tente de novo.');
    if (refused(e) && state.switching) return say(`A carteira continua em outra rede. Troque para ${n.name} para enviar.`);
    if (refused(e)) return say('Envio cancelado na carteira. Nada foi enviado.');
    return say('A carteira recusou o envio: saldo insuficiente para o valor e a taxa.');
  }

  function finished(hash, n, text) {
    const url = n.tx_url.replace('{tx}', encodeURIComponent(hash));
    block.hidden = true; done.hidden = false; done.replaceChildren();
    const h = document.createElement('h3'); h.textContent = 'Doação enviada. Obrigado!';
    const p = document.createElement('p'); p.textContent = `${text} ${root.dataset.coin} pela rede ${n.name}.`;
    const a = document.createElement('a'); a.href = url; a.target = '_blank'; a.rel = 'noopener'; a.textContent = 'Ver a transação no explorador';
    const q = document.createElement('p'); q.textContent = 'Pode levar alguns minutos para aparecer.';
    done.append(h, p, a, q);
  }

  sendBtn.addEventListener('click', async () => {
    const n = net(), c = coin(), units = amount();
    if (units === null || state.busy) return;
    if (!state.wallet) {
      const here = found(n.family);
      if (here.length > 1 && !state.choosing) {
        state.choosing = true;
        wallets.replaceChildren(...here.map((w) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = w.info.name;
          if (w.info.icon) { const i = document.createElement('img'); i.src = w.info.icon; i.alt = ''; b.prepend(i); }
          b.addEventListener('click', () => pickWallet(w, n)); return b; }));
        show(wallets, true); return;
      }
      return pickWallet(here[0], n);
    }
    state.busy = true; render(); say('');
    try {
      const was = n.family === 'evm' ? await state.wallet.provider.request({ method: 'eth_chainId' }) : null;
      state.switching = n.family === 'evm' && was !== C.hex(BigInt(n.chain_id));
      const hash = await transfer(state.wallet, n, c, units);
      finished(hash, n, C.decimalText(units, c.decimals));
    } catch (e) { explain(e, n, 'send'); } finally { state.busy = false; state.switching = false; render(); }
  });

  async function pickWallet(w, n) {
    state.busy = true; render();
    try {
      state.account = await connect(w, n); state.wallet = w; say('');
      if (w.provider && w.provider.on) w.provider.on('accountsChanged', (a) => { state.account = a[0]; if (!a[0]) state.wallet = null; render(); });
    } catch (e) { explain(e, n, 'connect'); }
    finally { state.busy = false; state.choosing = false; render(); }
  }

  payLink.addEventListener('click', () => setTimeout(() => {
    if (document.visibilityState === 'visible') say('Nenhum app abriu? Use o QR em outro aparelho ou copie o endereço acima.');
  }, 2500));
  input.addEventListener('input', render);
  root.addEventListener('bi-cripto-pick', () => { state.wallet = null; state.account = null; block.hidden = false; done.hidden = true; render(); });
  const entry = C.parseEntry(location.hash, data.networks);
  if (entry && entry.amount) input.value = entry.amount;
  render();
  window.BiCripto = { ready: true };
})();
```

- [ ] **Passo 4: remontar e rodar a sonda**

Remontar o staging (o `build-site.py` copia `assets/`) e rodar `cripto-check.cjs`. Esperado: 0 falhas. Rodar com `--control`. Esperado: `control: every send check failed, as it must`.

Com um clique só, a sonda cobre uma carteira (a de mentira). Com duas ou mais carteiras, `sendBtn` mostra a lista: a sonda não cobre esse caso; conferir à mão no teste do mantenedor.

- [ ] **Passo 5: commit**

```bash
git add docs/superpowers/tools/cripto-check.cjs docs/superpowers/previews/assets/bi-cripto.js
git commit --signoff -m "feat(apoie): send crypto from the modal: EVM, Tron, UniSat, Crossmark and wallet links (spec cripto-no-site)"
```

## Tarefa 6: as travas de segurança e o peso

**Arquivos:** `pipelines/tests/test_support.py`.

- [ ] **Passo 1: escrever os testes,** antes de `class RulesTest`:

```python
SEND_JS = REPO / "docs" / "superpowers" / "previews" / "assets" / "bi-cripto.js"
CORE_JS = SEND_JS.with_name("bi-cripto-core.js")
ALLOWED_METHODS = {"eth_requestAccounts", "eth_chainId", "wallet_switchEthereumChain", "wallet_addEthereumChain", "eth_sendTransaction"}
FORBIDDEN = re.compile(r"personal_sign|eth_sign|signTypedData|signMessage|approve|permit|setApprovalForAll|seed|mnemonic|privateKey", re.I)


def method_problems(js):
    """A wallet method outside the closed list, or a word that asks for more than a plain transfer (an empty list: clean). Section 5, rule 4."""
    return sorted(set(re.findall(r"method:\s*'([^']+)'", js)) - ALLOWED_METHODS) + FORBIDDEN.findall(js)


class SendRulesTest(unittest.TestCase):
    def test_only_the_closed_list_of_wallet_methods(self):
        self.assertEqual(method_problems(SEND_JS.read_text(encoding="utf-8")), [])

    def test_control_another_method_or_a_signature_is_caught(self):
        js = SEND_JS.read_text(encoding="utf-8")
        for plant in ("p.request({ method: 'personal_sign' })", "p.request({ method: 'eth_accounts' })", "token.approve(x)"):
            with self.subTest(plant=plant):
                self.assertNotEqual(method_problems(js + plant), [])

    def test_the_destination_comes_only_from_the_page_block(self):
        js = SEND_JS.read_text(encoding="utf-8")
        self.assertNotRegex(js, r"Destination:\s*(?!n\.address)|sendBitcoin\((?!n\.address)|to:\s*(?!n\.address|c\.contract)")
        self.assertNotIn("URLSearchParams", js, "the entry link goes through the core, which never reads an address")

    def test_control_a_destination_from_a_field_is_caught(self):
        js = SEND_JS.read_text(encoding="utf-8").replace("to: n.address, value", "to: input.value, value")
        self.assertRegex(js, r"to:\s*(?!n\.address|c\.contract)")

    def test_the_weight_of_the_send(self):
        for f in (SEND_JS, CORE_JS):
            self.assertLess(len(gzip.compress(f.read_bytes(), 9)), 15 * 1024, f.name)
        self.assertLess(sum(len(gzip.compress(f.read_bytes(), 9)) for f in (SEND_JS, CORE_JS)), 15 * 1024, "section 7: under 15 KB together")

    def test_the_send_is_not_in_the_page_until_asked(self):
        h = build(on_soon_crypto_live())["inicio"]
        self.assertNotIn('src="assets/bi-cripto', h["header"] + h["js"])
```

Pôr `import gzip` no topo do arquivo.

- [ ] **Passo 2: rodar:** `uv run --locked python -B -m unittest pipelines.tests.test_support.SendRulesTest`. Os controles passam; se um teste de regra falhar, corrigir o código, nunca a regra. Se `seed` ou `permit` aparecer num nome inocente, trocar o nome.

- [ ] **Passo 3: commit**

```bash
git add pipelines/tests/test_support.py
git commit --signoff -m "test(apoie): the closed list of wallet methods, the destination rule and the weight of the send"
```

## Tarefa 7: registro, pull request e o teste de verdade

- [ ] **Passo 1:** rodar tudo de novo: `uv run --locked python -B -m unittest discover -s pipelines/tests`, `apoie-check.cjs` e `cripto-check.cjs` nas duas montagens, com controle. Parar os servidores (`lsof -nP -iTCP:8742 -sTCP:LISTEN -t`).
- [ ] **Passo 2:** acrescentar à spec a seção "Como foi construído" e a linha de `cripto-check.cjs` em `CONTRIBUTING.md`, junto da de `apoie-check.cjs`.
- [ ] **Passo 3:** abrir o pull request para `staging` (`--body-file -` com heredoc entre aspas). Conferir `dco`, `ci`, `visible-text` e CodeQL.
- [ ] **Passo 4: o teste do mantenedor no site de testes** (D205). Ele manda um valor pequeno em cada linha; a sessão confere a chegada no explorador e na API da rede, e marca o que cada carteira de verdade mostrou. Um caminho que não funcionar fica com a reserva (copiar o endereço) até a correção.

| Moeda | Rede | Computador | Celular | Chegou |
|---|---|---|---|---|
| ETH | Ethereum | | | |
| USDT, USDC | Ethereum | | | |
| BNB | BNB Smart Chain | | | |
| USDT, USDC | BNB Smart Chain | | | |
| SOL, USDT, USDC | Solana | QR | link | |
| USDT | Tron | | | |
| BTC | Bitcoin | | | |
| XRP (1 ou mais) | XRP Ledger | | link | |

O que este teste decide, porque as páginas das carteiras não dizem e só uma carteira de verdade, no site publicado, mostra: se os navegadores dos apps injetam a carteira; se o endereço de transação da Tronscan abre; se o Xaman abre preenchido; se a carteira cria a conta de token do destino na Solana; a resposta real da Crossmark (`signInAndWait` e `signAndSubmitAndWait`).

- [ ] **Passo 5:** depois do primeiro 1 XRP: `status` do `xrp-ledger` em `"live"` e sem `first_min`, num commit próprio. A produção só no lote (D192), com o PROD WARNING e o "pode" do autor.
