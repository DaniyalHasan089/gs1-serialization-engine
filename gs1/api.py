"""FastAPI REST API and Web Interface for GS1 DataMatrix Serialization Engine."""

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .batch import build_codes
from .datamatrix import datamatrix_gs1
from .export import generate_csv_string, generate_zip_bytes
from .models import GS, GS1Code
from .png import create_png
from .serials import random_serial
from .validation import (validate_batch, validate_expiry, validate_gtin,
                         validate_serial)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
INDEX_HTML_PATH = STATIC_DIR / "index.html"

app = FastAPI(
    title="GS1 DataMatrix Serialization Engine",
    description="REST API and Web UI for generating GS1 DataMatrix barcodes, sequential/random serials, CSVs, and PNG archives.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class GenerateRequest(BaseModel):
    gtin: str = Field(..., description="14-digit GTIN (with valid check digit)", example="05054563197276")
    expiry: str = Field(..., description="Expiry date in YYMMDD format", example="301231")
    batch: str = Field(..., description="Batch or Lot number (max 20 characters)", example="LOT2026A")
    first_serial: Optional[str] = Field(None, description="Starting serial (12-20 alphanumeric). If omitted, an auto random serial is generated.", example="A1B2C3D4E5F6")
    serial_length: int = Field(16, ge=12, le=20, description="Length of serial if auto-generated")
    count: int = Field(50, ge=1, le=100000, description="Number of codes to generate")
    random_step: bool = Field(False, description="Use random gaps between serials instead of sequential +1")
    max_step: int = Field(1000, ge=1, le=100000, description="Maximum step size when random_step is true")


class CodeItem(BaseModel):
    index: int
    gtin: str
    expiry: str
    batch: str
    serial: str
    human: str
    raw: str
    barcode_url: str


class GenerateResponse(BaseModel):
    count: int
    codes: list[CodeItem]


class ValidateRequest(BaseModel):
    gtin: Optional[str] = None
    expiry: Optional[str] = None
    batch: Optional[str] = None
    serial: Optional[str] = None


class ValidateResponse(BaseModel):
    valid: bool
    errors: dict[str, str]


def _build_codes_from_request(req: GenerateRequest) -> list[GS1Code]:
    first = req.first_serial
    if not first:
        first = random_serial(req.serial_length)
    try:
        return build_codes(
            gtin=req.gtin,
            expiry=req.expiry,
            batch=req.batch,
            first_serial=first,
            count=req.count,
            random_step=req.random_step,
            max_step=req.max_step,
        )
    except (ValueError, OverflowError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@app.get("/", response_class=FileResponse, include_in_schema=False)
def serve_dashboard():
    if not INDEX_HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(INDEX_HTML_PATH, media_type="text/html")


@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {"status": "ok", "app": "GS1 DataMatrix Serialization Engine", "version": "1.0.0"}


@app.get("/api/v1/serial/random", tags=["Serials"])
def get_random_serial(length: int = Query(16, ge=12, le=20, description="Serial length (12-20)")):
    try:
        return {"serial": random_serial(length)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/v1/validate", response_model=ValidateResponse, tags=["Validation"])
def validate_inputs(req: ValidateRequest):
    errors: dict[str, str] = {}
    if req.gtin is not None:
        try:
            validate_gtin(req.gtin)
        except ValueError as e:
            errors["gtin"] = str(e)

    if req.expiry is not None:
        try:
            validate_expiry(req.expiry)
        except ValueError as e:
            errors["expiry"] = str(e)

    if req.batch is not None:
        try:
            validate_batch(req.batch)
        except ValueError as e:
            errors["batch"] = str(e)

    if req.serial is not None:
        try:
            validate_serial(req.serial)
        except ValueError as e:
            errors["serial"] = str(e)

    return ValidateResponse(valid=len(errors) == 0, errors=errors)


@app.post("/api/v1/generate", response_model=GenerateResponse, tags=["Codes"])
def generate_codes_api(req: GenerateRequest):
    codes = _build_codes_from_request(req)
    items = []
    for i, c in enumerate(codes, 1):
        items.append(
            CodeItem(
                index=i,
                gtin=c.gtin,
                expiry=c.expiry,
                batch=c.batch,
                serial=c.serial,
                human=c.human,
                raw=c.raw.replace(GS, "<GS>"),
                barcode_url=f"/api/v1/barcode?gtin={c.gtin}&expiry={c.expiry}&batch={c.batch}&serial={c.serial}",
            )
        )
    return GenerateResponse(count=len(items), codes=items)


@app.post("/api/v1/export/csv", tags=["Export"])
def export_csv_api(req: GenerateRequest):
    codes = _build_codes_from_request(req)
    csv_content = generate_csv_string(codes)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="codes.csv"'},
    )


@app.post("/api/v1/export/zip", tags=["Export"])
def export_zip_api(
    req: GenerateRequest,
    scale: int = Query(10, ge=1, le=30),
    quiet: int = Query(2, ge=0, le=10),
):
    codes = _build_codes_from_request(req)
    zip_bytes = generate_zip_bytes(codes, scale=scale, quiet=quiet, include_csv=True)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="gs1_codes.zip"'},
    )


@app.get("/api/v1/barcode", tags=["Barcode"])
def get_barcode_image(
    gtin: str = Query(..., description="14-digit GTIN"),
    expiry: str = Query(..., description="YYMMDD Expiry"),
    batch: str = Query(..., description="Batch/Lot string"),
    serial: str = Query(..., description="Serial string"),
    scale: int = Query(10, ge=1, le=30, description="Pixel multiplier per module"),
    quiet: int = Query(2, ge=0, le=10, description="Quiet zone border in modules"),
):
    try:
        gtin = validate_gtin(gtin)
        expiry = validate_expiry(expiry)
        batch = validate_batch(batch)
        serial = validate_serial(serial)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    code = GS1Code(gtin, expiry, batch, serial)
    matrix = datamatrix_gs1(code.raw)
    png_bytes = create_png(matrix, scale=scale, quiet=quiet)
    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )
