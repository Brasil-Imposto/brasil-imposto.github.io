"""The core of the address fuzzer (pipelines/fuzz/fuzz_addresses.py, D228) runs here without atheris: every seed passes, a few
hand-made inputs pass, and the planted crash raises (the ci runs the fuzzer itself, on Linux x86_64)."""
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

    def test_control_the_planted_crash_raises(self):
        seed = fuzz.seeds()[0]
        fuzz.check_one(seed + b"!")
        with self.assertRaisesRegex(RuntimeError, "planted"):
            fuzz.check_one(seed + b"!", planted=True)


if __name__ == "__main__":
    unittest.main()
