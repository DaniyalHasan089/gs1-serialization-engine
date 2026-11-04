"""Reed-Solomon error correction over GF(256), primitive polynomial 0x12D."""

_EXP = [0] * 512
_LOG = [0] * 256

_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x12D
for _i in range(255, 512):
    _EXP[_i] = _EXP[_i - 255]


def _mul(a: int, b: int) -> int:
    return 0 if a == 0 or b == 0 else _EXP[_LOG[a] + _LOG[b]]


def rs_ecc(data: list[int], n: int) -> list[int]:
    """Return `n` error-correction codewords for `data`."""
    gen = [1]
    for i in range(1, n + 1):
        nxt = [0] * (len(gen) + 1)
        for j, g in enumerate(gen):
            nxt[j] ^= g
            nxt[j + 1] ^= _mul(g, _EXP[i])
        gen = nxt
    res = [0] * n
    for d in data:
        fb = d ^ res[0]
        res = res[1:] + [0]
        if fb:
            for j in range(n):
                res[j] ^= _mul(gen[j + 1], fb)
    return res
