"""Glue: validated inputs -> list of GS1Code."""

from .models import GS1Code
from .serials import generate_serials
from .validation import (validate_batch, validate_expiry, validate_gtin,
                         validate_serial)


def build_codes(gtin: str, expiry: str, batch: str, first_serial: str, count: int,
                random_step: bool = False, max_step: int = 1000) -> list[GS1Code]:
    gtin = validate_gtin(gtin)
    expiry = validate_expiry(expiry)
    batch = validate_batch(batch)
    first_serial = validate_serial(first_serial)
    serials = generate_serials(first_serial, count, random_step, max_step)
    return [GS1Code(gtin, expiry, batch, s) for s in serials]
