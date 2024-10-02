from collections.abc import Iterator

from aiombus.exceptions import MBusError
from aiombus.telegrams.base import TelegramBytesType, TelegramContainer
from aiombus.telegrams.fields import (
    DataInformationField as DIF,
    DataInformationFieldExtension as DIFE,
    ValueInformationField as VIF,
    ValueInformationFieldExtension as VIFE,
)


DataFieldType = DIF | DIFE
ValueFieldType = VIF | VIFE


class TelegramBlock(TelegramContainer):
    """Base Telegram Block class."""


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

    def __init__(self, ibytes: TelegramBytesType):
        try:
            blocks = self._parse_blocks(iter(ibytes))
        except StopIteration as e:
            cls_name = self.__class__.__name__
            msg = f"failed to parse {ibytes} as {cls_name}"
            raise MBusError(msg) from e

        self._dif = blocks[0]
        self._difes = blocks[1:]

        self._fields = blocks

    @property
    def dif(self) -> DIF:
        return self._dif

    @property
    def difes(self) -> list[DIFE]:
        return self._difes

    def _parse_blocks(self, ibytes: Iterator[int]) -> list[DataFieldType]:
        dif = DIF(byte=next(ibytes))

        blocks: list[DataFieldType] = [dif]
        if not dif.extension:
            return blocks

        pos = 1
        max_frame = self.MAX_DIFE_FRAMES + 1
        while byte := next(ibytes):
            dife = DIFE(byte=byte)
            blocks.append(dife)
            if not dife.extension:
                break
            pos += 1
            if pos == max_frame:
                if dife.extension:
                    msg = f"the last {dife} has the extension bit set"
                    raise MBusError(msg)
                break
        return blocks


class ValueInformationBlock(TelegramBlock):
    """The "Value Information Block" (VIB) class.

    The VIB describes the value of the unit and the multiplier.
    The VIB contains at least one byte (VIF - Value Information Field).
    The VIF of a VIB can be followed with VIF Extensions (VIFE):
    from 0 to 10 VIFE frames 1 byte each (as the VIF).

    The structure of the VIB:
    -------------------------------
    |   VIF  |        VIFE        |
    +--------+--------------------+
    | 1 byte | 0-10 (1 byte each) |
    -------------------------------
    """

    MAX_VIFE_FRAMES = 10

    def __init__(self, ibytes: TelegramBytesType):
        try:
            blocks = self._parse_blocks(iter(ibytes))
        except StopIteration as e:
            cls_name = self.__class__.__name__
            msg = f"failed to parse {ibytes} as {cls_name}"
            raise MBusError(msg) from e

        self._vif = blocks[0]
        self._vifes = blocks[1:]

        self._fields = blocks

    @property
    def vif(self) -> VIF:
        return self._vif

    @property
    def vifes(self) -> list[VIFE]:
        return self._vifes

    def _parse_blocks(self, ibytes: Iterator[int]) -> list[ValueFieldType]:
        vif = VIF(byte=next(ibytes))

        blocks: list[ValueFieldType] = [vif]
        if not vif.extension:
            return blocks

        pos = 1
        max_frame = self.MAX_VIFE_FRAMES + 1
        while byte := next(ibytes):
            vife = VIFE(byte=byte)
            blocks.append(vife)
            if not vife.extension:
                break
            pos += 1
            if pos == max_frame:
                if vife.extension:
                    msg = f"the last {vife} has the extension bit set"
                    raise MBusError(msg)
                break
        return blocks
