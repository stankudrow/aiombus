"""The Value Information Block (VIB) module.

The VIB describes the value and the multiplier of the data.
The VIB describes the length, type and coding of the data.
The VIB contains at least one byte (VIF - Value Information Field).
The VIF of a VIB can be followed with VIF Extensions (VIFE):
from 0 to 10 VIFE frames 1 byte each (as the VIF frame).

The structure:
-------------------------------
|   VIF  |        VIFE        |
+--------+--------------------+
| 1 byte | 0-10 (1 byte each) |
-------------------------------
"""

from typing import Iterable, Self


class ValueInformationBlock:
    """Value Information Block (VIB) class."""

    # TODO: TEST PURITY
    @classmethod
    def from_hexstring(cls, hex: str) -> Self:
        """Return a `ValueInformationBlock` from a hexadecimal string."""

        barr = bytearray.fromhex(iter(hex))
        return cls(barr)

    @classmethod
    def from_integers(cls, ints: Iterable[int]) -> Self:
        """Return a `ValueInformationBlock` from a sequence of integers."""

        barr = bytearray(iter(ints))
        return cls(barr)

    # MUST AFFECT frame and wind it
    @classmethod
    def parse_frame(cls):
        pass

    # TODO: iterable and `async for`able`
