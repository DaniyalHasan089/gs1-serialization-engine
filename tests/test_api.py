"""Tests for FastAPI endpoints and OpenAPI schema."""

import io
import sys
import unittest
import zipfile
from pathlib import Path
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gs1.api import (
    app,
    health_check,
    get_random_serial,
    validate_inputs,
    generate_codes_api,
    export_csv_api,
    export_zip_api,
    get_barcode_image,
    serve_dashboard,
    GenerateRequest,
    ValidateRequest,
)

GTIN = "05054563197276"


class TestFastAPI(unittest.TestCase):
    def test_openapi_schema(self):
        schema = app.openapi()
        self.assertEqual(schema["info"]["title"], "GS1 DataMatrix Serialization Engine")
        expected_paths = [
            "/api/v1/health",
            "/api/v1/serial/random",
            "/api/v1/validate",
            "/api/v1/generate",
            "/api/v1/export/csv",
            "/api/v1/export/zip",
            "/api/v1/barcode",
        ]
        for p in expected_paths:
            self.assertIn(p, schema["paths"])

    def test_health(self):
        res = health_check()
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["version"], "1.0.0")

    def test_dashboard_html(self):
        res = serve_dashboard()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.media_type, "text/html")
        self.assertTrue(Path(res.path).is_file())
        content = Path(res.path).read_text(encoding="utf-8")
        self.assertIn("GS1 DataMatrix Serialization Engine", content)

    def test_random_serial(self):
        res = get_random_serial(length=14)
        self.assertEqual(len(res["serial"]), 14)
        with self.assertRaises(HTTPException):
            get_random_serial(length=10)

    def test_validate_inputs(self):
        req = ValidateRequest(
            gtin=GTIN,
            expiry="301231",
            batch="LOT123",
            serial="A1B2C3D4E5F6",
        )
        res = validate_inputs(req)
        self.assertTrue(res.valid)
        self.assertEqual(res.errors, {})

        # Test invalid GTIN
        req_bad = ValidateRequest(gtin="12345")
        res_bad = validate_inputs(req_bad)
        self.assertFalse(res_bad.valid)
        self.assertIn("gtin", res_bad.errors)

    def test_generate_codes(self):
        req = GenerateRequest(
            gtin=GTIN,
            expiry="301231",
            batch="LOT2026A",
            first_serial="A1B2C3D4E5F6",
            count=5,
        )
        res = generate_codes_api(req)
        self.assertEqual(res.count, 5)
        self.assertEqual(len(res.codes), 5)
        self.assertEqual(res.codes[0].serial, "A1B2C3D4E5F6")
        self.assertTrue(res.codes[0].human.startswith(f"(01){GTIN}"))
        self.assertIn("<GS>", res.codes[0].raw)
        self.assertIn("/api/v1/barcode", res.codes[0].barcode_url)

    def test_generate_invalid_data(self):
        req = GenerateRequest(
            gtin="05054563197277",  # wrong check digit
            expiry="301231",
            batch="LOT1",
            count=5,
        )
        with self.assertRaises(HTTPException) as ctx:
            generate_codes_api(req)
        self.assertEqual(ctx.exception.status_code, 400)

    def test_export_csv(self):
        req = GenerateRequest(
            gtin=GTIN,
            expiry="301231",
            batch="LOT2026A",
            first_serial="A1B2C3D4E5F6",
            count=3,
        )
        res = export_csv_api(req)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.media_type, "text/csv")
        content = res.body.decode("utf-8")
        lines = content.strip().splitlines()
        self.assertEqual(len(lines), 4)  # 1 header + 3 data rows
        self.assertTrue(lines[0].startswith("index,gtin_01"))

    def test_export_zip(self):
        req = GenerateRequest(
            gtin=GTIN,
            expiry="301231",
            batch="LOT2026A",
            first_serial="A1B2C3D4E5F6",
            count=2,
        )
        res = export_zip_api(req, scale=6, quiet=2)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.media_type, "application/zip")

        # Validate zip structure
        zf = zipfile.ZipFile(io.BytesIO(res.body))
        names = zf.namelist()
        self.assertIn("codes.csv", names)
        self.assertIn("images/00001_A1B2C3D4E5F6.png", names)
        self.assertIn("images/00002_A1B2C3D4E5F7.png", names)

    def test_barcode_png(self):
        res = get_barcode_image(
            gtin=GTIN,
            expiry="301231",
            batch="LOT1",
            serial="A1B2C3D4E5F6",
            scale=5,
            quiet=2,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.media_type, "image/png")
        self.assertTrue(res.body.startswith(b"\x89PNG\r\n\x1a\n"))


if __name__ == "__main__":
    unittest.main()
