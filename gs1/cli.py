"""Interactive command-line front end."""

import datetime as dt
import sys
from pathlib import Path

from .batch import build_codes
from .export import write_csv, write_images
from .serials import random_serial
from .validation import (validate_batch, validate_expiry, validate_gtin,
                         validate_serial)


def _ask(label, parse, default=None):
    while True:
        hint = f" [{default}]" if default is not None else ""
        val = input(f"{label}{hint}: ").strip()
        if not val and default is not None:
            val = default
        try:
            return parse(val)
        except ValueError as e:
            print(f"   x {e}  Try again.\n")


def _count(v):
    if not v.isdigit() or int(v) < 1:
        raise ValueError("Enter a whole number of 1 or more.")
    if int(v) > 100000:
        raise ValueError("Maximum is 100000 per run.")
    return int(v)


def _length(v):
    if not v.isdigit() or not 12 <= int(v) <= 20:
        raise ValueError("Enter 12-20.")
    return int(v)


def _yes_no(v):
    if v.lower() in ("y", "yes"):
        return True
    if v.lower() in ("n", "no"):
        return False
    raise ValueError("Answer y or n.")


def _optional_serial(v):
    return validate_serial(v) if v else ""


def run() -> None:
    print("=" * 60)
    print("  GS1 DataMatrix Serialization Engine")
    print("=" * 60)
    gtin = _ask("(01) GTIN (14 digits)", validate_gtin)
    expiry = _ask("(17) Expiry date (YYMMDD)", validate_expiry)
    batch = _ask("(10) Batch/Lot (max 20 chars)", validate_batch)
    first = _ask("(21) First serial (12-20 alphanumeric, blank = auto random)",
                 _optional_serial, default="")
    if not first:
        first = random_serial(_ask("     Auto serial length (12-20)", _length, default="16"))
        print(f"     -> first serial: {first}")
    count = _ask("How many codes to generate", _count, default="50")
    rnd = _ask("Random gaps between serials instead of +1 each? (y/n)", _yes_no, default="n")
    images = _ask("Generate DataMatrix PNG images? (y/n)", _yes_no, default="y")
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = Path(_ask("Output folder", lambda v: v, default=f"gs1_output_{stamp}"))

    try:
        codes = build_codes(gtin, expiry, batch, first, count, random_step=rnd)
    except (ValueError, OverflowError) as e:
        sys.exit(f"\nError: {e}")

    folder.mkdir(parents=True, exist_ok=True)
    write_csv(codes, folder / "codes.csv")

    if images:
        print("\nRendering images...")
        write_images(codes, folder / "images",
                     progress=lambda i, n: print(f"   {i}/{n}", end="\r"))
        print()

    print("\nDone!")
    print(f"  Codes  : {len(codes)}")
    print(f"  First  : {codes[0].human}")
    print(f"  Last   : {codes[-1].human}")
    print(f"  CSV    : {folder / 'codes.csv'}")
    if images:
        print(f"  Images : {folder / 'images'}")


def main() -> None:
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
