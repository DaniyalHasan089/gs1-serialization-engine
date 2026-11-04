"""Writing results to disk: CSV + PNG images."""

import csv
from pathlib import Path
from typing import Callable, Optional

from .datamatrix import datamatrix_gs1
from .models import GS, GS1Code
from .png import write_png


def write_csv(codes: list[GS1Code], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["index", "gtin_01", "expiry_17", "batch_10", "serial_21",
                    "human_readable", "raw_data(<GS>=FNC1)"])
        for i, c in enumerate(codes, 1):
            w.writerow([i, c.gtin, c.expiry, c.batch, c.serial,
                        c.human, c.raw.replace(GS, "<GS>")])


def write_images(codes: list[GS1Code], folder: Path,
                 progress: Optional[Callable[[int, int], None]] = None) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(codes, 1):
        write_png(folder / f"{i:05d}_{c.serial}.png", datamatrix_gs1(c.raw))
        if progress:
            progress(i, len(codes))
