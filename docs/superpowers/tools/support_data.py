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
# Web3Forms' access key: a public UUID, "an alias to your email" (its FAQ); never the e-mail address itself
ACCESS_KEY = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
STATUSES = ("soon", "live")
WEB3FORMS = "https://api.web3forms.com/submit"


def load():
    return json.loads(Path(os.environ.get("BI_SUPPORT_JSON") or PATH).read_text(encoding="utf-8"))


def networks_of(data, coin):
    """Every (group, network, standard) that receives `coin`, in the order of the file."""
    return [(g, n, c["standard"]) for g in data["crypto"]["groups"] for n in g["networks"] for c in n["coins"]
            if c["coin"] == coin]


def live(data, channel):
    return data[channel]["status"] == "live"


def structure_problems(data):
    """What must hold whether the button is on or off: the statuses, the seven coins, each explorer with its address slot."""
    out = []
    for channel in ("sponsors", "crypto"):
        if data[channel].get("status") not in STATUSES:
            out.append(f"{channel}.status: one of {STATUSES}")
    if data["contact_form"].get("provider") != "web3forms":
        out.append("contact_form.provider: web3forms")
    for coin in COINS:
        if not networks_of(data, coin):
            out.append(f"no network receives {coin}")
    groups = data["crypto"]["groups"]
    extra = {c["coin"] for g in groups for n in g["networks"] for c in n["coins"]} - set(COINS)
    if extra:
        out.append(f"coins outside the list: {sorted(extra)}")
    for g in groups:
        if g["format"] not in FORMATS:
            out.append(f"{g['id']}: unknown address format {g['format']!r}")
        for n in g["networks"]:
            if not (n["explorer_url"].startswith("https://") and n["explorer_url"].count("{address}") == 1):
                out.append(f"{g['id']}/{n['id']}: the explorer URL needs https and one {{address}}")
    return out


def money_problem(data, key, where=None):
    v = (where or data).get(key)
    return None if not (isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0) else f"{key}: a value in reais above zero"


def channel_problems(data, channel):
    """What must hold before a channel goes live: every value of that channel filled in."""
    out = []
    if channel == "sponsors":
        c = data["sponsors"]
        if not (c.get("sponsors_url") or "").startswith("https://github.com/sponsors/"):
            out.append("sponsors.sponsors_url: a https://github.com/sponsors/ address")
        if not (c["fiscal_host"].get("name") and (c["fiscal_host"].get("url") or "").startswith("https://")):
            out.append("sponsors.fiscal_host: the name and a https URL")
    else:
        c = data["crypto"]
        m = money_problem(data, "unidentified_return_above_brl", c)
        if m:
            out.append("crypto." + m)
        for g in c["groups"]:
            a = g.get("address")
            if not a:
                out.append(f"crypto/{g['id']}: the address")
            elif g["format"] in FORMATS and not FORMATS[g["format"]].match(a):
                out.append(f"crypto/{g['id']}: {a!r} is not a {g['format']} address")
    return out


def problems(data):
    """Everything wrong with the file as it is: the structure always; with the button on, the form's access key; with a channel
    live, every value of that channel."""
    out = structure_problems(data)
    if data.get("enabled"):
        key = data["contact_form"].get("access_key")
        if not (isinstance(key, str) and ACCESS_KEY.match(key)):
            out.append("contact_form.access_key: the Web3Forms access key (a UUID, never an e-mail address)")
    open_channels = [c for c in ("sponsors", "crypto") if data[c].get("status") == "live"]
    for channel in open_channels:
        out += channel_problems(data, channel)
    if open_channels:  # the maintenance cap governs the money of either channel
        m = money_problem(data, "maintainer_cap_brl")
        if m:
            out.append(m)
    return out


def brl(value):
    """R$ 1.234,56, the screen's money format."""
    s = f"{Decimal(str(value)).quantize(Decimal('0.01')):,.2f}"
    return "R$ " + s.replace(",", "_").replace(".", ",").replace("_", ".")
