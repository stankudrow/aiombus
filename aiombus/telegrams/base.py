from collections.abc import Generator, Iterable
from typing import Self

from aiombus.validators import validate_byte


class TelegramField:
    """The base "Field" class.

    It is a base wrapper for a byte value.
    Field is used in Frames, Blocks, Headers and so forth.
    """

    def __init__(self, byte: int):
        self._byte = validate_byte(byte)

    def __eq__(self, other) -> bool:
        sbyte = self._byte
        if isinstance(other, TelegramField):
            return sbyte == other.byte
        return sbyte == other

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(byte={self._byte})"

    @property
    def byte(self) -> int:
        """Return the byte value of the field."""

        return self._byte


class TelegramBlock:
    """The base class for M-Bus block types."""

    @classmethod
    def from_hexstring(cls, hex: str) -> Self:
        """Return a class instance from a hexadecimal string."""

        barr = bytearray.fromhex(hex)
        return cls(barr)

    @classmethod
    def from_integers(cls, ints: Iterable[int]) -> Self:
        """Return a class instance from a sequence of integers."""

        barr = bytearray(iter(ints))
        return cls(barr)

    def __eq__(self, other) -> bool:
        if isinstance(other, TelegramBlock):
            return self._bytes == other._bytes
        return self._bytes == other

    def __iter__(self) -> Generator[None, None, TelegramField]:
        return self._generate()

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(bytes={self._bytes})"

    def __str__(self) -> str:
        return str(list(self._generate()))

    @property
    def bytes(self) -> bytes:
        return self._bytes
