"""The test wallets of phase 6 (spec seguranca-doacoes, section 14, D217): keys made here go straight into the macOS Keychain and
are never printed; only public addresses are. The wallet probe reads them from the Keychain at use time and types them into the
extension, so no key passes through a terminal, a log or a conversation. Test networks only: none of these keys ever holds value.

Run: python3 docs/superpowers/tools/wallet-keys.py make      (creates the missing entries; an existing entry is never replaced)
     python3 docs/superpowers/tools/wallet-keys.py addresses (the public addresses of the keys in the Keychain)
     python3 docs/superpowers/tools/wallet-keys.py --control (the derivation against known vectors; exit 1 if any differs)

Entries (account "pegaso", the Keychain label of this machine): bi-test-wallet-password (unlocks every test extension),
bi-test-evm-donor and bi-test-evm-project (Sepolia and the BSC testnet), bi-test-tron-donor and bi-test-tron-project (Nile),
bi-test-btc-donor (testnet4 or signet, WIF), bi-test-xrpl-donor (the XRP Ledger testnet, a family seed).
"""
import hashlib
import secrets
import subprocess
import sys

ACCOUNT = "pegaso"
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
XRP_B58 = "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz"   # the XRP Ledger's order (xrpl.org, Addresses)


def add(p, q):
    if p is None:
        return q
    if q is None:
        return p
    if p[0] == q[0] and (p[1] + q[1]) % P == 0:
        return None
    lam = (3 * p[0] * p[0] * pow(2 * p[1], -1, P)) if p == q else ((q[1] - p[1]) * pow(q[0] - p[0], -1, P))
    x = (lam * lam - p[0] - q[0]) % P
    return x, (lam * (p[0] - x) - p[1]) % P


def mul(k, point=G):
    out = None
    while k:
        if k & 1:
            out = add(out, point)
        point, k = add(point, point), k >> 1
    return out


def keccak256(data):
    """Keccak-256 as Ethereum uses it (the original padding 0x01, not SHA3's 0x06)."""
    rc = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
          0x8000000080008081, 0x8000000000008009, 0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
          0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
          0x000000000000800A, 0x800000008000000A, 0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
    rot = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
    mask = (1 << 64) - 1
    rate = 136
    msg = bytearray(data) + b"\x01"
    msg += b"\x00" * (-len(msg) % rate)
    msg[-1] |= 0x80
    s = [[0] * 5 for _ in range(5)]
    for off in range(0, len(msg), rate):
        for i in range(rate // 8):
            s[i % 5][i // 5] ^= int.from_bytes(msg[off + 8 * i: off + 8 * i + 8], "little")
        for r in rc:
            c = [s[x][0] ^ s[x][1] ^ s[x][2] ^ s[x][3] ^ s[x][4] for x in range(5)]
            d = [c[(x - 1) % 5] ^ (((c[(x + 1) % 5] << 1) | (c[(x + 1) % 5] >> 63)) & mask) for x in range(5)]
            s = [[s[x][y] ^ d[x] for y in range(5)] for x in range(5)]
            b = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    v, n = s[x][y], rot[x][y]
                    b[y][(2 * x + 3 * y) % 5] = ((v << n) | (v >> (64 - n))) & mask if n else v
            s = [[b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y]) for y in range(5)] for x in range(5)]
            s[0][0] ^= r
    return b"".join(s[i % 5][i // 5].to_bytes(8, "little") for i in range(4))


def b58check(payload, alphabet=B58):
    raw = payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    n, out = int.from_bytes(raw, "big"), ""
    while n:
        n, r = divmod(n, 58)
        out = alphabet[r] + out
    return alphabet[0] * (len(raw) - len(raw.lstrip(b"\0"))) + out


def evm_address(key):
    x, y = mul(key)
    a = keccak256(x.to_bytes(32, "big") + y.to_bytes(32, "big"))[-20:].hex()
    h = keccak256(a.encode()).hex()
    return "0x" + "".join(c.upper() if int(h[i], 16) >= 8 else c for i, c in enumerate(a))   # EIP-55


def tron_address(key):
    return b58check(b"\x41" + bytes.fromhex(evm_address(key)[2:]))


def new_key():
    while True:
        k = int.from_bytes(secrets.token_bytes(32), "big")
        if 1 <= k < N:
            return k


def keychain_has(service):
    return subprocess.run(["security", "find-generic-password", "-a", ACCOUNT, "-s", service],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def keychain_read(service):
    return subprocess.run(["security", "find-generic-password", "-a", ACCOUNT, "-s", service, "-w"],
                          capture_output=True, text=True, check=True).stdout.strip()


def keychain_write(service, secret):
    subprocess.run(["security", "add-generic-password", "-a", ACCOUNT, "-s", service, "-w", secret],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def makers():
    return {
        "bi-test-wallet-password": lambda: secrets.token_urlsafe(18) + "Aa1!",
        "bi-test-evm-donor": lambda: f"{new_key():064x}",
        "bi-test-evm-project": lambda: f"{new_key():064x}",
        "bi-test-tron-donor": lambda: f"{new_key():064x}",
        "bi-test-tron-project": lambda: f"{new_key():064x}",
        "bi-test-btc-donor": lambda: b58check(b"\xef" + new_key().to_bytes(32, "big") + b"\x01"),   # testnet WIF, compressed
        "bi-test-xrpl-donor": lambda: b58check(b"\x21" + secrets.token_bytes(16), XRP_B58),        # a family seed, "s..."
    }


def addresses():
    out = {}
    for who in ("donor", "project"):
        if keychain_has(f"bi-test-evm-{who}"):
            out[f"evm-{who}"] = evm_address(int(keychain_read(f"bi-test-evm-{who}"), 16))
        if keychain_has(f"bi-test-tron-{who}"):
            out[f"tron-{who}"] = tron_address(int(keychain_read(f"bi-test-tron-{who}"), 16))
    return out


def control():
    """Known vectors: the key 1 is Ethereum's well-known 0x7E5F...5Bdf; keccak256 of the empty string; EIP-55's own examples."""
    checks = [
        ("keccak256('')", keccak256(b"").hex(), "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"),
        ("address of key 1", evm_address(1), "0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf"),
        ("address of key 2", evm_address(2), "0x2B5AD5c4795c026514f8317c7a215E218DcCD6cF"),
        ("planted: key 3 is not key 1's address", evm_address(3) != "0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf", True),
    ]
    bad = [name for name, got, want in checks if got != want]
    for name, got, want in checks:
        print(f"{'ok  ' if got == want else 'FAIL'} {name}")
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--control"]:
        sys.exit(control())
    if sys.argv[1:] == ["make"]:
        for service, make in makers().items():
            if keychain_has(service):
                print(f"kept  {service} (already in the Keychain)")
            else:
                keychain_write(service, make())
                print(f"made  {service}")
        sys.argv[1:] = ["addresses"]
    if sys.argv[1:] == ["addresses"]:
        for name, a in addresses().items():
            print(f"{name}: {a}")
        sys.exit(0)
    raise SystemExit(__doc__)
