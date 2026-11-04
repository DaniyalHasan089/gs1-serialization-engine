"""Serial number generation: first serial -> N unique serials."""

import re
import secrets

_HEX_RE = re.compile(r"^[0-9A-Fa-f]+$")
_B36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_B16 = "0123456789ABCDEF"


def random_serial(length: int = 16) -> str:
    """Random uppercase-hex serial of the given length (12-20)."""
    if not 12 <= length <= 20:
        raise ValueError("Serial length must be 12-20.")
    return secrets.token_hex(length)[:length].upper()


def _to_text(value: int, radix: int, width: int) -> str:
    digits = _B16 if radix == 16 else _B36
    out = []
    while value:
        value, r = divmod(value, radix)
        out.append(digits[r])
    s = "".join(reversed(out)) or "0"
    if len(s) > width:
        raise OverflowError("Serial range exhausted - use a lower first serial or a longer one.")
    return s.rjust(width, "0")


def generate_serials(first: str, count: int, random_step: bool = False,
                     max_step: int = 1000) -> list[str]:
    """
    first, then each next serial = previous + step.
    step is 1 (sequential) or random 1..max_step (random_step=True).
    Hex serials stay hex; anything else is incremented in base 36.
    """
    if count < 1:
        raise ValueError("Count must be >= 1.")
    radix = 16 if _HEX_RE.match(first) else 36
    current = int(first, radix)
    serials = [first]
    for _ in range(count - 1):
        current += (secrets.randbelow(max_step) + 1) if random_step else 1
        serials.append(_to_text(current, radix, len(first)))
    assert len(set(serials)) == len(serials)
    return serials
