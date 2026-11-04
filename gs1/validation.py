"""Input validation for the four Application Identifiers."""

import datetime as dt
import re

_AI82_RE = re.compile(r"^[!\"%&'()*+,\-./0-9:;<=>?A-Za-z_]+$")
_ALNUM_RE = re.compile(r"^[0-9A-Za-z]+$")


def gtin_check_digit(body13: str) -> int:
    """GS1 mod-10 check digit for the first 13 digits of a GTIN-14."""
    total = sum(int(ch) * (3 if i % 2 == 0 else 1)
                for i, ch in enumerate(reversed(body13)))
    return (10 - total % 10) % 10


def validate_gtin(v: str) -> str:
    if not re.fullmatch(r"\d{14}", v):
        raise ValueError("GTIN must be exactly 14 digits "
                         "(for a 13-digit EAN, add a leading 0).")
    expected = gtin_check_digit(v[:13])
    if int(v[-1]) != expected:
        raise ValueError(f"GTIN check digit is wrong (last digit should be {expected}).")
    return v


def validate_expiry(v: str) -> str:
    if not re.fullmatch(r"\d{6}", v):
        raise ValueError("Expiry must be 6 digits: YYMMDD.")
    yy, mm, dd = int(v[:2]), int(v[2:4]), int(v[4:])
    if not 1 <= mm <= 12:
        raise ValueError("Month must be 01-12.")
    if dd != 0:  # DD=00 is allowed by GS1 (= last day of month)
        try:
            dt.date(2000 + yy, mm, dd)
        except ValueError:
            raise ValueError("That is not a real calendar date.") from None
    return v


def validate_batch(v: str) -> str:
    if not 1 <= len(v) <= 20:
        raise ValueError("Batch/Lot must be 1-20 characters.")
    if not _AI82_RE.match(v):
        raise ValueError("Batch/Lot has characters GS1 does not allow (no spaces, #, @ ...).")
    return v


def validate_serial(v: str) -> str:
    if not 12 <= len(v) <= 20:
        raise ValueError("Serial must be 12-20 characters.")
    if not _ALNUM_RE.match(v):
        raise ValueError("Serial must be letters/digits only.")
    return v.upper()
