"""Fuzzing of the address checks (D228): atheris feeds random input to support_data.address_problem, the hand-written base58check,
bech32 and bech32m, keccak-256 and EIP-55 code that checks the donation addresses before every build. An exception is a crash; an
EIP-55 form must be its own EIP-55 form and pass the check. Seeds: the addresses of data/support.json.

Usage (the ci, on Linux x86_64, where atheris has wheels; pyproject.toml leaves it out elsewhere):
  python pipelines/fuzz/fuzz_addresses.py run 60    fuzz for 60 seconds; exits 0 when nothing crashed
  python pipelines/fuzz/fuzz_addresses.py control   plants a crash (an address with "!") and exits 0 only when the fuzzer finds it
The first byte of an input picks the format, the rest is the address (UTF-8, bad bytes replaced).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLANT = "planted crash: an address with '!'"
support_data = None


def load():
    """Import support_data; the run imports it inside atheris.instrument_imports() so the fuzzer sees its branches."""
    global support_data
    sys.path.insert(0, str(ROOT / "docs" / "superpowers" / "tools"))
    import support_data as module
    support_data = module


def formats():
    return sorted(support_data.FORMATS)


def check_one(data, planted=False):
    """One input: raises on a crash or a broken property, returns None otherwise."""
    if not data:
        return
    fmt = formats()[data[0] % len(formats())]
    address = data[1:].decode("utf-8", "replace")
    if planted and "!" in address:
        raise RuntimeError(PLANT)
    result = support_data.address_problem(fmt, address)
    if not (result is None or isinstance(result, str)):
        raise AssertionError(f"address_problem returned {result!r}")
    if fmt == "evm" and support_data.FORMATS["evm"].match(address):
        form = support_data.eip55(address)
        if support_data.eip55(form) != form or support_data.address_problem("evm", form) is not None:
            raise AssertionError(f"the EIP-55 form of {address!r} is not stable")


def seeds():
    data = json.loads((ROOT / "data" / "support.json").read_text(encoding="utf-8"))
    return [bytes([formats().index(g["format"])]) + g["address"].encode() for g in data["crypto"]["groups"] if g.get("address")]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "control":
        r = subprocess.run([sys.executable, __file__, "plant", "60"], capture_output=True, text=True)
        found = r.returncode != 0 and PLANT in r.stdout + r.stderr
        print("the fuzzer found the planted crash" if found else f"the planted crash was NOT found (exit {r.returncode})\n"
              + (r.stdout + r.stderr)[-3000:])
        return 0 if found else 1
    if mode not in ("run", "plant") or len(sys.argv) != 3 or not sys.argv[2].isdigit():
        print(__doc__)
        return 2
    import atheris
    with atheris.instrument_imports():
        load()
    planted = mode == "plant"
    with tempfile.TemporaryDirectory(prefix="bi-fuzz-") as tmp:
        corpus = Path(tmp) / "corpus"
        corpus.mkdir()
        for n, seed in enumerate(seeds()):
            (corpus / f"seed-{n}").write_bytes(seed)
        atheris.Setup([sys.argv[0], f"-max_total_time={sys.argv[2]}", f"-artifact_prefix={tmp}/", str(corpus)],
                      lambda data: check_one(data, planted))
        atheris.Fuzz()
    return 0


if __name__ == "__main__":
    sys.exit(main())
