"""The Data Record Header (DRH) module.

A DRH consists of a DI and a VI blocks,
where DI is Data Inforamtion (block)
and VI stands for Value Information (block).
"""

from aiombus.blocks.dib import DataInformationBlock
from aiombus.blocks.vib import ValueInformationBlock


class DataRecordHeader:
    """The Data Record Header class.

    DRH = DIB + VIB, where:

    - DIB = Data Information Block
    - VIB = Value Information Block
    """

    def __init__(self, frame: bytearray):
        iframe = iter(frame)

        self._frame = frame
        self._dib = DataInformationBlock.parse_frame(iframe)
        self._vib = ValueInformationBlock.parse_frame(iframe)
        self._data = bytearray(iframe)

    @property
    def dib(self) -> DataInformationBlock:
        return self._dib

    @property
    def vib(self) -> ValueInformationBlock:
        return self._vib

    @property
    def data(self) -> bytearray:
        return self._data
