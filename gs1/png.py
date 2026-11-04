"""Minimal PNG writer (grayscale, no Pillow needed)."""

import struct
import zlib
from pathlib import Path


def _chunk(tag: bytes, body: bytes) -> bytes:
    return (struct.pack(">I", len(body)) + tag + body +
            struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF))


def write_png(path: Path, matrix: list[list[int]], scale: int = 10, quiet: int = 2) -> None:
    """Write a module matrix as PNG. `quiet` = blank border in modules."""
    n = len(matrix)
    total = n + 2 * quiet
    blank = b"\xff" * (total * scale)
    rows = []
    for r in range(-quiet, n + quiet):
        if 0 <= r < n:
            line = bytearray()
            for c in range(-quiet, n + quiet):
                dark = 0 <= c < n and matrix[r][c]
                line += (b"\x00" if dark else b"\xff") * scale
            line = bytes(line)
        else:
            line = blank
        rows.extend([b"\x00" + line] * scale)  # filter byte 0 per scanline

    side = total * scale
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", struct.pack(">IIBBBBB", side, side, 8, 0, 0, 0, 0))
           + _chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
           + _chunk(b"IEND", b""))
    Path(path).write_bytes(png)
