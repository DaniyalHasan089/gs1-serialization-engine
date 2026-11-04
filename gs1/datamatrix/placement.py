"""ECC200 'Utah' module placement (ISO/IEC 16022 Annex F)."""


def place_codewords(nrow: int, ncol: int, cws: list[int]) -> list[list[int]]:
    arr = [[-1] * ncol for _ in range(nrow)]

    def mod(r, c, ch, bit):
        if r < 0:
            r += nrow
            c += 4 - ((nrow + 4) % 8)
        if c < 0:
            c += ncol
            r += 4 - ((ncol + 4) % 8)
        arr[r][c] = (cws[ch - 1] >> (8 - bit)) & 1

    def utah(r, c, ch):
        for dr, dc, b in ((-2, -2, 1), (-2, -1, 2), (-1, -2, 3), (-1, -1, 4),
                          (-1, 0, 5), (0, -2, 6), (0, -1, 7), (0, 0, 8)):
            mod(r + dr, c + dc, ch, b)

    def corner(ch, pts):
        for (r, c), b in zip(pts, range(1, 9)):
            mod(r, c, ch, b)

    R, C = nrow, ncol
    ch, r, c = 1, 4, 0
    while True:
        if r == R and c == 0:
            corner(ch, [(R-1, 0), (R-1, 1), (R-1, 2), (0, C-2), (0, C-1), (1, C-1), (2, C-1), (3, C-1)]); ch += 1
        if r == R - 2 and c == 0 and C % 4:
            corner(ch, [(R-3, 0), (R-2, 0), (R-1, 0), (0, C-4), (0, C-3), (0, C-2), (0, C-1), (1, C-1)]); ch += 1
        if r == R - 2 and c == 0 and C % 8 == 4:
            corner(ch, [(R-3, 0), (R-2, 0), (R-1, 0), (0, C-2), (0, C-1), (1, C-1), (2, C-1), (3, C-1)]); ch += 1
        if r == R + 4 and c == 2 and C % 8 == 0:
            corner(ch, [(R-1, 0), (R-1, C-1), (0, C-3), (0, C-2), (0, C-1), (1, C-3), (1, C-2), (1, C-1)]); ch += 1
        while True:  # sweep up-right
            if 0 <= r < R and 0 <= c < C and arr[r][c] == -1:
                utah(r, c, ch); ch += 1
            r -= 2; c += 2
            if not (r >= 0 and c < C):
                break
        r += 1; c += 3
        while True:  # sweep down-left
            if 0 <= r < R and 0 <= c < C and arr[r][c] == -1:
                utah(r, c, ch); ch += 1
            r += 2; c -= 2
            if not (r < R and c >= 0):
                break
        r += 3; c += 1
        if not (r < R or c < C):
            break
    if arr[R - 1][C - 1] == -1:  # fixed pattern, lower-right corner
        arr[R - 1][C - 1] = arr[R - 2][C - 2] = 1
    return [[1 if v == 1 else 0 for v in row] for row in arr]
