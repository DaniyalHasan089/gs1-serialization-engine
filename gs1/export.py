"""Writing results to disk and memory: CSV + PNG images + ZIP archives."""

import csv
import io
import zipfile
from pathlib import Path
from typing import Callable, Optional

from .datamatrix import datamatrix_gs1
from .models import GS, GS1Code
from .png import create_png, write_png


def generate_csv_string(codes: list[GS1Code]) -> str:
    """Generate CSV string for the given GS1 codes in memory."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["index", "gtin_01", "expiry_17", "batch_10", "serial_21",
                "human_readable", "raw_data(<GS>=FNC1)"])
    for i, c in enumerate(codes, 1):
        w.writerow([i, c.gtin, c.expiry, c.batch, c.serial,
                    c.human, c.raw.replace(GS, "<GS>")])
    return buf.getvalue()


def write_csv(codes: list[GS1Code], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(generate_csv_string(codes))


def generate_zip_bytes(codes: list[GS1Code], scale: int = 10, quiet: int = 2,
                       include_csv: bool = True) -> bytes:
    """Generate in-memory ZIP archive bytes containing codes.csv and PNG barcode images."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if include_csv:
            zf.writestr("codes.csv", generate_csv_string(codes))
        for i, c in enumerate(codes, 1):
            png_bytes = create_png(datamatrix_gs1(c.raw), scale=scale, quiet=quiet)
            zf.writestr(f"images/{i:05d}_{c.serial}.png", png_bytes)
    return buf.getvalue()


def write_images(codes: list[GS1Code], folder: Path,
                 progress: Optional[Callable[[int, int], None]] = None) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(codes, 1):
        write_png(folder / f"{i:05d}_{c.serial}.png", datamatrix_gs1(c.raw))
        if progress:
            progress(i, len(codes))

