"""Data model for one serialized GS1 code."""

from dataclasses import dataclass

GS = "\x1d"  # Group Separator (ASCII 29), carried inside the symbol as FNC1


@dataclass(frozen=True)
class GS1Code:
    gtin: str     # (01)
    expiry: str   # (17) YYMMDD
    batch: str    # (10)
    serial: str   # (21)

    @property
    def human(self) -> str:
        """Human-readable form with parenthesised AIs."""
        return f"(01){self.gtin}(17){self.expiry}(10){self.batch}(21){self.serial}"

    @property
    def raw(self) -> str:
        """Data stream: (01)/(17) are fixed length, (10) is variable so it is
        followed by GS, (21) is last so nothing follows it."""
        return f"01{self.gtin}17{self.expiry}10{self.batch}{GS}21{self.serial}"
