"""The core of the address fuzzer (pipelines/fuzz/fuzz_addresses.py, D228) runs here without atheris: every seed passes, a few
hand-made inputs pass, and the planted crash raises (the ci runs the fuzzer itself, on Linux x86_64)."""
import base64
import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("fuzz_addresses", REPO / "pipelines" / "fuzz" / "fuzz_addresses.py")
fuzz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fuzz)
fuzz.load()


class FuzzCoreTest(unittest.TestCase):
    def test_every_seed_is_a_valid_address(self):
        seeds = fuzz.seeds()
        self.assertGreaterEqual(len(seeds), 5)
        for s in seeds:
            fmt = fuzz.formats()[s[0]]
            self.assertIsNone(fuzz.support_data.address_problem(fmt, s[1:].decode()), s)
            fuzz.check_one(s)

    def test_odd_inputs_do_not_crash(self):
        for data in (b"", b"\x00", b"\x01" + b"0x" + b"f" * 40, b"\x02bc1" + b"q" * 80, b"\xff\xfe\xfd", b"\x03T" + "é".encode() * 40):
            fuzz.check_one(data)

    def test_the_crash_the_ci_fuzzer_found_on_2026_11_08(self):
        # an EVM address with a final line break: the harness filtered with match (whose $ lets the break in, D229), so eip55()
        # kept the break and the harness called its own form unstable; address_problem refuses the address, as it must
        data = base64.b64decode("ATB4Yjk0N2NDODQ0NTg0MWNmNDBBRkNBNzIzODA0ZDA2ODU1YmVhN2JjNwo=")
        self.assertEqual(fuzz.formats()[data[0] % len(fuzz.formats())], "evm")
        self.assertTrue(data.endswith(b"\n"))
        fuzz.check_one(data)
        self.assertIsNotNone(fuzz.support_data.address_problem("evm", data[1:].decode()))

    def test_control_the_planted_crash_raises(self):
        seed = fuzz.seeds()[0]
        fuzz.check_one(seed + b"!")
        with self.assertRaisesRegex(RuntimeError, "planted"):
            fuzz.check_one(seed + b"!", planted=True)


if __name__ == "__main__":
    unittest.main()
