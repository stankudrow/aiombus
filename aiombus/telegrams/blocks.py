from collections.abc import Generator, Iterator

from aiombus.exceptions import MBusDecodeError
from aiombus.telegrams.base import TelegramBlock
from aiombus.telegrams.fields import (
    DataInformationField as DIF,
    DataInformationFieldExtension as DIFE,
    ValueInformationField as VIF,
    ValuenformationFieldExtension as VIFE,
)


DataFieldType = DIF | DIFE
ValueFieldType = VIF | VIFE


class DataInformationBlock(TelegramBlock):
    """The "Data Information Block" (DIB) class.

    The DIB describes the length, type and coding of the data.
    The DIB contains at least one byte (DIF - Data Information Field).
    The DIF of a DIB can be followed with DIF Extensions (DIFE):
    from 0 to 10 DIFE frames 1 byte each (as the DIF).

    The structure of the DIB:
    -------------------------------
    |   DIF  |        DIFE        |
    +--------+--------------------+
    | 1 byte | 0-10 (1 byte each) |
    -------------------------------
    """

    MAX_DIFE_FRAMES = 10

    def __init__(self, data):
        blocks = self._parse_blocks(iter(data))
        self._dif = blocks[0]
        self._difes = blocks[1:]

        self._bytes = bytes([self._dif.byte] + [dife.byte for dife in self._difes])

    @property
    def dif(self) -> DIF:
        return self._dif

    @property
    def difes(self) -> list[DIFE]:
        return self._difes

    def _generate(self) -> Generator[None, None, DIF | DIFE]:
        yield self._dif
        yield from self._difes

    def _parse_blocks(self, ibytes: Iterator[int]) -> list[DataFieldType]:
        dif = DIF(byte=next(ibytes))

        blocks: list[DataFieldType] = [dif]
        if not dif.extension_bit:
            return blocks

        pos = 1
        max_frame = self.MAX_DIFE_FRAMES + 1
        while byte := next(ibytes):
            dife = DIFE(byte=byte)
            blocks.append(dife)
            if not dife.extension_bit:
                break
            pos += 1
            if pos == max_frame:
                if dife.extension_bit:
                    msg = f"the last {dife} has the extension bit set"
                    raise MBusDecodeError(msg)
                break
        return blocks

    def to_bytearray(self) -> bytearray:
        return self._bytes
