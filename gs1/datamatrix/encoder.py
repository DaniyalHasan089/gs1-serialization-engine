"""GS1 DataMatrix (ECC200) encoder: text -> matrix of 0/1 modules."""

from ..models import GS
from .galois import rs_ecc
from .placement import place_codewords
from .tables import pick_symbol

FNC1 = 232


def encode_codewords(data: str) -> list[int]:
    """ASCII-mode codewords. Leading FNC1 marks a GS1 symbol, GS becomes FNC1,
    consecutive digit pairs are packed into one codeword."""
    cw = [FNC1]
    i = 0
    while i < len(data):
        ch = data[i]
        if ch == GS:
            cw.append(FNC1)
            i += 1
        elif ch.isdigit() and i + 1 < len(data) and data[i + 1].isdigit():
            cw.append(130 + int(data[i:i + 2]))
            i += 2
        else:
            cw.append(ord(ch) + 1)
            i += 1
    return cw


def _pad(cws: list[int], capacity: int) -> list[int]:
    start = len(cws)
    for pos in range(start, capacity):
        if pos == start:
            cws.append(129)
        else:
            v = 129 + ((149 * (pos + 1)) % 253) + 1
            cws.append(v - 254 if v > 254 else v)
    return cws


def _assemble(mapping, size, ds, reg):
    """Add finder (solid L) and clock (alternating) borders around each region."""
    sym = [[0] * size for _ in range(size)]
    rs = ds + 2
    for ri in range(reg):
        for ci in range(reg):
            for r in range(rs):
                for c in range(rs):
                    if c == 0 or r == rs - 1:
                        v = 1
                    elif r == 0:
                        v = 1 if c % 2 == 0 else 0
                    elif c == rs - 1:
                        v = 1 if r % 2 == 1 else 0
                    else:
                        v = mapping[ri * ds + r - 1][ci * ds + c - 1]
                    sym[ri * rs + r][ci * rs + c] = v
    return sym


def datamatrix_gs1(data: str) -> list[list[int]]:
    """Return the symbol as a 2-D list (1 = dark module)."""
    cws = encode_codewords(data)
    size, ds, reg, n_data, n_ecc = pick_symbol(len(cws))
    cws = _pad(cws, n_data)
    cws += rs_ecc(cws, n_ecc)
    mapping = place_codewords(reg * ds, reg * ds, cws)
    return _assemble(mapping, size, ds, reg)
