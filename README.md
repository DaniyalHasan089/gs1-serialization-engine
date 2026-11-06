# GS1 DataMatrix Serialization Engine (FastAPI)

A high-performance GS1 DataMatrix serialization service and web application. Generates GS1-compliant 2D barcodes, sequential and random-stepped serials, CSV exports, and zip archives of PNG images with zero C/external barcode library dependencies.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

### 1. Web & REST API Server (FastAPI)
Run with Uvicorn:
```bash
uvicorn main:app --reload
```
or run `main.py` directly:
```bash
python main.py
```

- **Interactive Web Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 2. Interactive CLI Mode
The original interactive terminal wizard remains fully accessible:
```bash
python main.py --cli
```

### 3. Running Tests
```bash
python -m unittest discover tests
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web dashboard for generating codes and live preview |
| `GET` | `/api/v1/health` | Service health check |
| `POST` | `/api/v1/generate` | Generate serialized GS1 codes with human and raw values |
| `POST` | `/api/v1/export/csv` | Download generated serials directly as `codes.csv` |
| `POST` | `/api/v1/export/zip` | Download archive with `codes.csv` and all PNG barcodes |
| `GET` | `/api/v1/barcode` | Render on-the-fly DataMatrix PNG for given GS1 elements |
| `GET` | `/api/v1/serial/random` | Generate an auto-random starting serial (length 12-20) |
| `POST` | `/api/v1/validate` | Validate GTIN, Expiry, Batch, or Serial without generating |

---

## Project Layout

```
main.py                  Entry point (FastAPI ASGI app + CLI fallback)
requirements.txt         Dependencies (fastapi, uvicorn, pydantic)
static/
  index.html             Standalone web dashboard interface
gs1/
  api.py                 FastAPI application, routes, models, and endpoints
  models.py              GS1Code dataclass (human + raw data stream)
  validation.py          GTIN check digit, expiry, batch, serial rules
  serials.py             first serial -> N unique serials
  batch.py               validated inputs -> list[GS1Code]
  export.py              CSV, in-memory PNG, and ZIP output
  png.py                 Pure-Python PNG writer (in-memory + disk)
  cli.py                 Interactive terminal prompts
  datamatrix/            Pure-Python ECC200 DataMatrix generator
    tables.py            ECC200 symbol sizes
    galois.py            Reed-Solomon (GF(256))
    placement.py         Module placement algorithm
    encoder.py           Codewords + assembly -> module matrix
tests/
  test_engine.py         Unit tests for core GS1 engine & DataMatrix
  test_api.py            Unit tests for FastAPI endpoints & schemas
```
