"""ECC200 square symbol sizes (single-block range, enough for GS1 payloads here)."""

# (symbol size, data-region size, regions per side, data codewords, ecc codewords)
SYMBOLS = [
    (10, 8, 1, 3, 5), (12, 10, 1, 5, 7), (14, 12, 1, 8, 10), (16, 14, 1, 12, 12),
    (18, 16, 1, 18, 14), (20, 18, 1, 22, 18), (22, 20, 1, 30, 20), (24, 22, 1, 36, 24),
    (26, 24, 1, 44, 28), (32, 14, 2, 62, 36), (36, 16, 2, 86, 42), (40, 18, 2, 114, 48),
    (44, 20, 2, 144, 56), (48, 22, 2, 174, 68),
]


def pick_symbol(n_codewords: int):
    """Smallest symbol whose data capacity fits `n_codewords`."""
    for sym in SYMBOLS:
        if n_codewords <= sym[3]:
            return sym
    raise ValueError("Data too long for the supported symbol sizes.")
