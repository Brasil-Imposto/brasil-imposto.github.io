"""The data of the Apoie button and its modal (spec BRASIL-IMPOSTO_SPEC_apoie_2026-10-23): read, checked and formatted here, so
the pages (apoie.py, through site_chrome.py) and the tests (pipelines/tests/test_support.py) use one rule.

The file is data/support.json. BI_SUPPORT_JSON points at another file, for a test build with dummy addresses that is never
committed."""
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

PATH = Path(__file__).resolve().parents[3] / "data" / "support.json"
COINS = ("BTC", "ETH", "SOL", "USDT", "USDC", "XRP", "BNB")   # the order of the coin buttons
B58 = "1-9A-HJ-NP-Za-km-z"                                    # base58: no 0, O, I or l
BITCOIN_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"   # Bitcoin's order, also Solana's and Tron's
XRP_B58 = "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz"       # the XRP Ledger's order (xrpl.org, Addresses)
BECH32 = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
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
CHANNELS = ("pix", "sponsors", "crypto")                       # the order of the cards and of "Quem recebe"
VAKINHA_HOSTS = ("vakinha.com.br", "www.vakinha.com.br")
WEB3FORMS = "https://api.web3forms.com/submit"


def load():
    return json.loads(Path(os.environ.get("BI_SUPPORT_JSON") or PATH).read_text(encoding="utf-8"))


def networks_of(data, coin, live=False):
    """Every (group, network, standard) that receives `coin`, in the order of the file; with live, only the networks on "live"
    (a network on "soon" shows no address, spec section 10)."""
    return [(g, n, c["standard"]) for g in data["crypto"]["groups"] for n in g["networks"] for c in n["coins"]
            if c["coin"] == coin and (not live or n.get("status") == "live")]


def live(data, channel):
    return data[channel]["status"] == "live"


def structure_problems(data):
    """What must hold whether the button is on or off: the statuses, the seven coins, each explorer with its address slot."""
    out = []
    for channel in CHANNELS:
        if data[channel].get("status") not in STATUSES:
            out.append(f"{channel}.status: one of {STATUSES}")
    if data["pix"].get("provider") != "Vakinha":
        out.append("pix.provider: Vakinha")
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
            if n.get("status") not in STATUSES:
                out.append(f"{g['id']}/{n['id']}.status: one of {STATUSES}")
            if not (n["explorer_url"].startswith("https://") and n["explorer_url"].count("{address}") == 1):
                out.append(f"{g['id']}/{n['id']}: the explorer URL needs https and one {{address}}")
    return out


# --- the checksum of each network's address (spec section 10.2, item 1), with no dependency ----------------------------------

def b58decode(s, alphabet):
    """The bytes of a base58 string; each leading zero character (the alphabet's first) is a zero byte."""
    n = 0
    for ch in s:
        n = n * 58 + alphabet.index(ch)
    return b"\0" * (len(s) - len(s.lstrip(alphabet[0]))) + n.to_bytes((n.bit_length() + 7) // 8, "big")


def base58check(s, alphabet):
    """The payload of a base58check string, its version byte first, when its last 4 bytes are the first 4 of the double SHA-256 of
    the rest; otherwise None."""
    raw = b58decode(s, alphabet)
    payload = raw[:-4]
    return payload if len(raw) > 4 and hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4] == raw[-4:] else None


def _polymod(values):
    chk = 1
    for v in values:
        top, chk = chk >> 25, (chk & 0x1ffffff) << 5 ^ v
        for i, g in enumerate((0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3)):
            chk ^= g if (top >> i) & 1 else 0
    return chk


def segwit_program(address, hrp="bc"):
    """The witness version and program of a segwit address (BIP-173 and BIP-350: bech32 at version 0, bech32m at 1 to 16), or
    None."""
    if address not in (address.lower(), address.upper()):
        return None
    a = address.lower()
    pos = a.rfind("1")
    if a[:pos] != hrp or len(a) > 90 or any(c not in BECH32 for c in a[pos + 1:]) or len(a) - pos - 1 < 7:
        return None
    data = [BECH32.index(c) for c in a[pos + 1:]]
    if _polymod([ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp] + data) != (1 if data[0] == 0 else 0x2bc830a3):
        return None
    acc = bits = 0
    program = []
    for v in data[1:-6]:                                        # 5-bit groups to bytes, no padding allowed past 4 zero bits
        acc, bits = acc << 5 | v, bits + 5
        while bits >= 8:
            bits -= 8
            program.append(acc >> bits & 255)
    if bits >= 5 or (acc << (8 - bits)) & 255 or data[0] > 16 or not 2 <= len(program) <= 40 \
            or (data[0] == 0 and len(program) not in (20, 32)):
        return None
    return data[0], bytes(program)


def _rc(t):
    """One bit of the round constants of Keccak-f (FIPS 202, algorithm 5)."""
    r = 1
    for _ in range(t % 255):
        r <<= 1
        if r & 0x100:
            r ^= 0x171
    return r & 1


_ROUNDS = [sum(_rc(j + 7 * i) << ((1 << j) - 1) for j in range(7)) for i in range(24)]
_ROT = [0] * 25                                                 # the rotation of each lane (x + 5y), FIPS 202 algorithm 2
_x, _y = 1, 0
for _t in range(24):
    _ROT[_x + 5 * _y] = (_t + 1) * (_t + 2) // 2 % 64
    _x, _y = _y, (2 * _x + 3 * _y) % 5
_MASK = (1 << 64) - 1


def _rol(v, n):
    return (v << n | v >> (64 - n)) & _MASK


def _keccak_f(a):
    for rc in _ROUNDS:
        c = [a[x] ^ a[x + 5] ^ a[x + 10] ^ a[x + 15] ^ a[x + 20] for x in range(5)]
        for i in range(25):
            a[i] ^= c[(i - 1) % 5] ^ _rol(c[(i + 1) % 5], 1)
        b = [0] * 25
        for x in range(5):
            for y in range(5):
                b[y + 5 * ((2 * x + 3 * y) % 5)] = _rol(a[x + 5 * y], _ROT[x + 5 * y])
        for i in range(25):
            a[i] = b[i] ^ (~b[i - i % 5 + (i + 1) % 5] & b[i - i % 5 + (i + 2) % 5])
        a[0] ^= rc


def sponge(data, suffix, rate=136, size=32):
    """A Keccak-f[1600] sponge with a 136-byte block: suffix 0x01 is the original Keccak (keccak_256, what EIP-55 uses), 0x06 is
    SHA-3 (the tests compare it with hashlib.sha3_256)."""
    lanes = [0] * 25
    padded = bytearray(data) + bytes([suffix]) + bytes(-(len(data) + 1) % rate)
    padded[-1] |= 0x80
    for at in range(0, len(padded), rate):
        for i in range(rate // 8):
            lanes[i] ^= int.from_bytes(padded[at + 8 * i:at + 8 * i + 8], "little")
        _keccak_f(lanes)
    return b"".join(v.to_bytes(8, "little") for v in lanes)[:size]


def keccak_256(data):
    return sponge(data, 0x01)


def eip55(address):
    """The EIP-55 form of a 0x address: a letter is a capital where the same position of keccak_256(the lowercase hex) is 8 or more."""
    low = address[2:].lower()
    h = keccak_256(low.encode("ascii")).hex()
    return "0x" + "".join(c.upper() if int(h[i], 16) >= 8 else c for i, c in enumerate(low))


def _payload_is(address, alphabet, size, versions):
    p = base58check(address, alphabet)
    return p is not None and len(p) == size and p[0] in versions


def address_problem(fmt, address):
    """None when `address` is a valid address of its format, its network's checksum included; otherwise what is wrong. Bitcoin:
    bech32 or bech32m on bc1, base58check version 0x00 or 0x05 on 1 and 3. The 0x address: exactly its EIP-55 form. Tron:
    base58check version 0x41. XRP: base58check version 0x00 in the XRP alphabet. Solana: 32 bytes (it has no checksum)."""
    bad = f"{address!r} is not a valid {fmt} address"
    if fmt not in FORMATS or not isinstance(address, str) or not FORMATS[fmt].match(address):
        return bad + " (its shape)"
    if fmt == "bitcoin":
        ok = segwit_program(address) is not None if address.startswith("bc1") else _payload_is(address, BITCOIN_B58, 21, (0, 5))
    elif fmt == "evm":
        ok = address == eip55(address)
    elif fmt == "tron":
        ok = _payload_is(address, BITCOIN_B58, 21, (0x41,))
    elif fmt == "xrp":
        ok = _payload_is(address, XRP_B58, 21, (0,))
    else:
        ok = len(b58decode(address, BITCOIN_B58)) == 32
    return None if ok else bad + " (its checksum)"


def channel_problems(data, channel):
    """What must hold before a channel goes live: every value of that channel filled in."""
    out = []
    if channel == "pix":
        c = data["pix"]
        u = urlsplit(c.get("campaign_url") or "")
        if not (u.scheme == "https" and u.hostname in VAKINHA_HOSTS and u.path.strip("/")):
            out.append("pix.campaign_url: a https:// address on vakinha.com.br")
        if not (isinstance(c.get("bank_screen_name"), str) and c["bank_screen_name"].strip()):
            out.append("pix.bank_screen_name: the name the bank app shows before the Pix is confirmed")
    elif channel == "sponsors":
        c = data["sponsors"]
        if not (c.get("sponsors_url") or "").startswith("https://github.com/sponsors/"):
            out.append("sponsors.sponsors_url: a https://github.com/sponsors/ address")
        if not (c["fiscal_host"].get("name") and (c["fiscal_host"].get("url") or "").startswith("https://")):
            out.append("sponsors.fiscal_host: the name and a https URL")
    else:
        for g in data["crypto"]["groups"]:
            if not g.get("address"):
                out.append(f"crypto/{g['id']}: the address")
        if not any(n.get("status") == "live" for g in data["crypto"]["groups"] for n in g["networks"]):
            out.append("crypto: at least one network on live")
    return out


def problems(data):
    """Everything wrong with the file as it is: the structure always; the form's access key, when there is one, must be a Web3Forms
    access key (the button may be on without it: production then leaves the contact form out until the key is filled, D162, and
    staging draws the form, whose send shows the error line); every address filled in, in any status, valid with its checksum;
    with a channel live, every value of that channel."""
    out = structure_problems(data)
    for g in data["crypto"]["groups"]:
        if g.get("address") is not None and g["format"] in FORMATS:
            p = address_problem(g["format"], g["address"])
            if p:
                out.append(f"crypto/{g['id']}: {p}")
    key = data["contact_form"].get("access_key")
    if key is not None and not (isinstance(key, str) and ACCESS_KEY.match(key)):
        out.append("contact_form.access_key: the Web3Forms access key (a UUID, never an e-mail address)")
    for channel in CHANNELS:
        if data[channel].get("status") == "live":
            out += channel_problems(data, channel)
    return out
