"""The data of the Apoie button and its modal (spec BRASIL-IMPOSTO_SPEC_apoie_2026-10-23): read, checked and formatted here, so
the pages (apoie.py, through site_chrome.py) and the tests (pipelines/tests/test_support.py) use one rule.

The file is data/support.json. BI_SUPPORT_JSON points at another file, for a test build with dummy addresses that is never
committed."""
import json
import os
import re
from decimal import Decimal
from pathlib import Path

PATH = Path(__file__).resolve().parents[3] / "data" / "support.json"
COINS = ("BTC", "ETH", "SOL", "USDT", "USDC", "XRP", "BNB")   # the order of the coin buttons
B58 = "1-9A-HJ-NP-Za-km-z"                                    # base58: no 0, O, I or l
FORMATS = {
    "bitcoin": re.compile(rf"^(bc1[ac-hj-np-z02-9]{{11,71}}|[13][{B58}]{{25,34}})$"),
    "evm": re.compile(r"^0x[0-9a-fA-F]{40}$"),
    "solana": re.compile(rf"^[{B58}]{{32,44}}$"),
    "tron": re.compile(rf"^T[{B58}]{{33}}$"),
    "xrp": re.compile(rf"^r[{B58}]{{24,34}}$"),
}
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$")


def load():
    return json.loads(Path(os.environ.get("BI_SUPPORT_JSON") or PATH).read_text(encoding="utf-8"))


def networks_of(data, coin):
    """Every (group, network, standard) that receives `coin`, in the order of the file."""
    return [(g, n, c["standard"]) for g in data["crypto"] for n in g["networks"] for c in n["coins"] if c["coin"] == coin]


def structure_problems(data):
    """What must hold whether the button is on or off: the seven coins, each network's explorer with its address slot."""
    out = []
    for coin in COINS:
        if not networks_of(data, coin):
            out.append(f"no network receives {coin}")
    extra = {c["coin"] for g in data["crypto"] for n in g["networks"] for c in n["coins"]} - set(COINS)
    if extra:
        out.append(f"coins outside the list: {sorted(extra)}")
    for g in data["crypto"]:
        if g["format"] not in FORMATS:
            out.append(f"{g['id']}: unknown address format {g['format']!r}")
        for n in g["networks"]:
            if not (n["explorer_url"].startswith("https://") and n["explorer_url"].count("{address}") == 1):
                out.append(f"{g['id']}/{n['id']}: the explorer URL needs https and one {{address}}")
    return out


def filled_problems(data):
    """What must hold before `enabled` can be true: every value filled in and every address in its network's format."""
    out = []
    if not (data.get("sponsors_url") or "").startswith("https://github.com/sponsors/"):
        out.append("sponsors_url: a https://github.com/sponsors/ address")
    if not (data["fiscal_host"].get("name") and (data["fiscal_host"].get("url") or "").startswith("https://")):
        out.append("fiscal_host: the name and a https URL")
    for key in ("maintainer_cap_brl", "unidentified_return_above_brl"):
        v = data.get(key)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
            out.append(f"{key}: a value in reais above zero")
    if not EMAIL.match(data.get("contact_email") or ""):
        out.append("contact_email: an e-mail address")
    for g in data["crypto"]:
        a = g.get("address")
        if not a:
            out.append(f"{g['id']}: the address")
        elif g["format"] in FORMATS and not FORMATS[g["format"]].match(a):
            out.append(f"{g['id']}: {a!r} is not a {g['format']} address")
    return out


def problems(data):
    """Everything wrong with the file as it is: the structure always, the filled values when the button is on."""
    return structure_problems(data) + (filled_problems(data) if data.get("enabled") else [])


def brl(value):
    """R$ 1.234,56, the screen's money format."""
    s = f"{Decimal(str(value)).quantize(Decimal('0.01')):,.2f}"
    return "R$ " + s.replace(",", "_").replace(".", ",").replace("_", ".")
