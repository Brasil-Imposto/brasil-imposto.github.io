"""The data of a test build for phase 6 (spec seguranca-doacoes, section 14): data/support.json with Ethereum on Sepolia, the BNB
Smart Chain on its testnet and Tron on Nile, each sending to a test address of wallet-keys.py, never to the project's. Bitcoin, the
XRP Ledger and Solana keep their real data: a wallet on a test network must be refused there (section 11). The output goes outside
git (support_data.py: "a test build with dummy addresses that is never committed"); build with BI_SUPPORT_JSON pointing at it.

Run: python3 docs/superpowers/tools/testnet-support.py OUT.json
Sources, read 2026-11-04: Circle's USDC contract addresses (Sepolia); BNB Chain's JSON-RPC page (BSC testnet, chain 97, its RPC);
Tron's networks page and the Nile faucet (nile.trongrid.io; the USDT test token); publicnode.com (Sepolia and BSC testnet nodes,
which answer any origin). No issuer publishes USDT on Sepolia or USDT and USDC on the BSC testnet: there the test build points at
Circle's Sepolia USDC so the token path runs; those three are not tested as themselves.
"""
import copy
import importlib.util
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
_spec = importlib.util.spec_from_file_location("wallet_keys", TOOLS / "wallet-keys.py")
wallet_keys = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wallet_keys)
SEPOLIA_USDC = "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
NILE_USDT = "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"
TESTNETS = {
    "ethereum": {"name": "Ethereum Sepolia", "explorer": "Etherscan Sepolia", "explorer_url": "https://sepolia.etherscan.io/address/{address}",
                 "tx_url": "https://sepolia.etherscan.io/tx/{tx}", "node": "https://ethereum-sepolia-rpc.publicnode.com", "chain_id": 11155111,
                 "contracts": {"USDT": SEPOLIA_USDC, "USDC": SEPOLIA_USDC}},
    "bsc": {"name": "BNB Smart Chain Testnet", "explorer": "BscScan Testnet", "explorer_url": "https://testnet.bscscan.com/address/{address}",
            "tx_url": "https://testnet.bscscan.com/tx/{tx}", "node": "https://bsc-testnet-rpc.publicnode.com", "chain_id": 97,
            "add_chain": {"chainName": "BNB Smart Chain Testnet", "nativeCurrency": {"name": "tBNB", "symbol": "tBNB", "decimals": 18},
                          "rpcUrls": ["https://bsc-testnet-dataseed.bnbchain.org"], "blockExplorerUrls": ["https://testnet.bscscan.com"]},
            "contracts": {"USDT": SEPOLIA_USDC, "USDC": SEPOLIA_USDC}},
    "tron": {"name": "Tron Nile", "explorer": "Tronscan Nile", "explorer_url": "https://nile.tronscan.org/#/address/{address}",
             "tx_url": "https://nile.tronscan.org/#/transaction/{tx}", "node": "https://nile.trongrid.io/wallet/gettransactioninfobyid",
             "contracts": {"USDT": NILE_USDT}},
}


def testnet(data, test_addresses):
    out = copy.deepcopy(data)
    for g in out["crypto"]["groups"]:
        if g["format"] in ("evm", "tron"):
            g["address"] = test_addresses[f"{g['format']}-project"]
        for n in g["networks"]:
            t = TESTNETS.get(n["id"])
            if not t:
                continue
            n.update({k: v for k, v in t.items() if k != "contracts"})
            for c in n["coins"]:
                if c["coin"] in t["contracts"]:
                    c["contract"], c["decimals"] = t["contracts"][c["coin"]], 6
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    data = json.loads((ROOT / "data" / "support.json").read_text(encoding="utf-8"))
    Path(sys.argv[1]).write_text(json.dumps(testnet(data, wallet_keys.addresses()), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {sys.argv[1]}: Sepolia, BSC testnet and Nile to the test addresses; Bitcoin, XRP Ledger and Solana unchanged")
