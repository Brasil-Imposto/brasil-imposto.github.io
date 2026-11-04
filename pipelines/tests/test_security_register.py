"""The register of the donation addresses in SECURITY.md (spec seguranca-doacoes, section 10; D219: a plain list with dates and the git
history, as the EFF and the Tor Project list theirs) and security.txt (RFC 9116; github.com's Contact is a link, no e-mail)."""
import datetime
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def register(text):
    """(network ids, address) of each row of the register table."""
    part = text.split("## Endereços de doação em cripto", 1)[1].split("\n## ", 1)[0]
    return [(row[0], row[1]) for row in (re.findall(r"^\| ([^|]+?) \| `([^`]+)` \|", part, re.M))]


class RegisterTest(unittest.TestCase):
    def test_the_register_lists_exactly_the_addresses_of_the_data(self):
        data = json.loads((REPO / "data" / "support.json").read_text(encoding="utf-8"))
        want = sorted(g["address"] for g in data["crypto"]["groups"])
        got = sorted(a for _n, a in register((REPO / "SECURITY.md").read_text(encoding="utf-8")))
        self.assertEqual(got, want)

    def test_control_a_planted_address_is_seen(self):
        text = (REPO / "SECURITY.md").read_text(encoding="utf-8")
        first = register(text)[0][1]
        planted = text.replace(first, "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE", 1)
        data = json.loads((REPO / "data" / "support.json").read_text(encoding="utf-8"))
        self.assertNotEqual(sorted(a for _n, a in register(planted)), sorted(g["address"] for g in data["crypto"]["groups"]))


class SecurityTxtTest(unittest.TestCase):
    def fields(self, text):
        return {k.lower(): v.strip() for k, v in re.findall(r"^([A-Za-z-]+):\s*(.+)$", text, re.M)}

    def text(self):
        return (REPO / "docs" / "superpowers" / "previews" / ".well-known" / "security.txt").read_text(encoding="utf-8")

    def test_rfc_9116_fields_with_a_link_and_no_email(self):
        f = self.fields(self.text())
        self.assertEqual(f["contact"], "https://github.com/Brasil-Imposto/brasil-imposto.github.io/security/advisories/new")
        self.assertEqual(f["canonical"], "https://brasil-imposto.github.io/.well-known/security.txt")
        expires = datetime.datetime.strptime(f["expires"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        now = datetime.datetime.now(datetime.timezone.utc)
        self.assertGreater(expires, now, "renew security.txt: its Expires has passed")
        self.assertLess(expires - now, datetime.timedelta(days=366), "RFC 9116: Expires less than a year ahead")
        self.assertNotIn("@", self.text())

    def test_control_an_email_line_is_seen(self):
        self.assertIn("@", self.text() + "Contact: mailto:" + chr(64) + "\n")   # the check sees an at sign wherever it is


if __name__ == "__main__":
    unittest.main()
