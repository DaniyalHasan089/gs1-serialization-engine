"""Run:  python -m unittest discover tests
Round-trip test against libdmtx is skipped unless pylibdmtx + Pillow are installed."""

import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gs1 import GS, GS1Code, build_codes, datamatrix_gs1, generate_serials
from gs1.png import write_png
from gs1.validation import gtin_check_digit, validate_expiry, validate_gtin

GTIN = "05054563197276"


class Validation(unittest.TestCase):
    def test_gtin(self):
        self.assertEqual(validate_gtin(GTIN), GTIN)
        with self.assertRaises(ValueError):
            validate_gtin("5054563197276")      # 13 digits
        with self.assertRaises(ValueError):
            validate_gtin("05054563197277")     # bad check digit
        self.assertEqual(gtin_check_digit(GTIN[:13]), 6)

    def test_expiry(self):
        validate_expiry("301231")
        validate_expiry("301200")               # DD=00 allowed
        for bad in ("301331", "300230", "12345"):
            with self.assertRaises(ValueError):
                validate_expiry(bad)


class Serials(unittest.TestCase):
    def test_sequential_hex(self):
        s = generate_serials("A1B2C3D4E5F6", 3)
        self.assertEqual(s, ["A1B2C3D4E5F6", "A1B2C3D4E5F7", "A1B2C3D4E5F8"])

    def test_unique_random_step(self):
        s = generate_serials("A1B2C3D4E5F6A7B8", 500, random_step=True)
        self.assertEqual(len(set(s)), 500)

    def test_overflow(self):
        with self.assertRaises(OverflowError):
            generate_serials("FFFFFFFFFFFF", 2)


class Encoding(unittest.TestCase):
    def test_raw_format(self):
        c = GS1Code(GTIN, "301231", "LOT1", "A1B2C3D4E5F6")
        self.assertEqual(c.raw, f"01{GTIN}17301231" + "10LOT1" + GS + "21A1B2C3D4E5F6")

    def test_symbol_is_square(self):
        c = build_codes(GTIN, "301231", "LOT2026A", "A1B2C3D4E5F6A7B8", 1)[0]
        m = datamatrix_gs1(c.raw)
        self.assertEqual(len(m), len(m[0]))

    def test_roundtrip_with_decoder(self):
        try:
            from PIL import Image
            from pylibdmtx import pylibdmtx
        except Exception:
            self.skipTest("pylibdmtx/Pillow not installed")
        rnd = random.Random(1)
        with tempfile.TemporaryDirectory() as d:
            for _ in range(15):
                batch = "".join(rnd.choice("ABCxyz0123456789") for _ in range(rnd.randint(1, 20)))
                serial = "".join(rnd.choice("0123456789ABCDEF") for _ in range(rnd.randint(12, 20)))
                c = GS1Code(GTIN, "301231", batch, serial)
                p = Path(d) / "x.png"
                write_png(p, datamatrix_gs1(c.raw))
                r = pylibdmtx.decode(Image.open(p), timeout=5000)
                self.assertTrue(r)
                # libdmtx hides FNC1 markers, so compare without GS
                self.assertEqual(r[0].data.decode("latin1"), c.raw.replace(GS, ""))


if __name__ == "__main__":
    unittest.main()
