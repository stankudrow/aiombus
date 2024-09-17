"""The module on Data Information Block (DIB).

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

The structure of the DIF:
--------------------------------------------------------------
|  bit |     7     |          6         |   5  4   | 3 2 1 0 |
+------+-----------+--------------------+----------+---------+
| desc | extension | storage number LSB | function |   data  |
--------------------------------------------------------------

The structure of the DIFE:
----------------------------------------------------------------
|  bit |     7     |       6       |   5  4   |   3  2  1  0   |
+------+-----------+---------------+----------+----------------+
| desc | extension | device (unit) |  tariff  | storage number |
----------------------------------------------------------------
"""

from enum import IntEnum
from typing import Iterable, Self

from aiombus.validators import validate_byte


# BCD = Type A. Integer = Type B. Real = Type H.
class DataFieldCodes(IntEnum):
    no_data = 0b0000
    int8 = 0b0001
    int16 = 0b0010
    int24 = 0b0011
    int32 = 0b0100
    real32 = 0b0101
    int48 = 0b0110
    int64 = 0b0111
    readout = 0b1000
    bcd2 = 0b1001
    bcd4 = 0b1010
    bcd6 = 0b1011
    bcd8 = 0b1100
    varlen = 0b1101
    bcd12 = 0b1110
    special_func = 0b1111


class FunctionFieldValues(IntEnum):
    instantaneous = 0b00
    maximum = 0b01
    minimum = 0b10
    error = 0b11


class DataInformationField:
    """Data Information Field (DIF) class.

    The structure of the DIB:
    -------------------------------
    |   DIF  |        DIFE        |
    +--------+--------------------+
    | 1 byte | 0-10 (1 byte each) |
    -------------------------------

    The structure of the DIF:
    --------------------------------------------------------------
    |  bit |     7     |          6         |   5  4   | 3 2 1 0 |
    +------+-----------+--------------------+----------+---------+
    | desc | extension | storage number LSB | function |   data  |
    --------------------------------------------------------------
    """

    DATA_FIELD_MASK = 0x0F  # 0000_1111
    FUNCTION_FIELD_MASK = 0x30  # 0011_0000
    STORAGE_NUMBER_LSB_MASK = 0x40  # 0100_0000
    EXTENSION_BIT_MASK = 0x80  # 1000_0000

    def __init__(self, byte: int, *, check_byte: bool = False):
        if check_byte:
            validate_byte(byte)

        self._byte_chk = check_byte
        self._byte = byte

        self._data = byte & self.DATA_FIELD_MASK
        self._func = (byte & self.FUNCTION_FIELD_MASK) >> 4
        self._sn_lsb = int((byte & self.STORAGE_NUMBER_LSB_MASK) != 0)
        self._ext = int((byte & self.EXTENSION_BIT_MASK) != 0)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(byte={self._byte}, check_byte={self._byte_chk})"

    @property
    def data_field(self) -> int:
        return self._data

    @property
    def function_field(self) -> int:
        return self._func

    @property
    def storage_number_lsb(self) -> int:
        return self._sn_lsb

    @property
    def extension_bit(self) -> int:
        return self._ext


class DataInformationFieldExtension:
    """Data Information Field Extension (DIFE) class.

    The structure of the DIB:
    -------------------------------
    |   DIF  |        DIFE        |
    +--------+--------------------+
    | 1 byte | 0-10 (1 byte each) |
    -------------------------------

    The structure of the DIFE:
    ----------------------------------------------------------------
    |  bit |     7     |       6       |   5  4   |   3  2  1  0   |
    +------+-----------+---------------+----------+----------------+
    | desc | extension | device (unit) |  tariff  | storage number |
    ----------------------------------------------------------------
    """

    STORAGE_NUMBER_MASK = 0x0F  # 0000_1111
    TARIFF_MASK = 0x30  # 0011_0000
    DEVICE_UNIT_MASK = 0x40  # 0100_0000
    EXTENSION_BIT_MASK = 0x80  # 1000_0000

    def __init__(self, byte: int, *, check_byte: bool = False):
        if check_byte:
            validate_byte(byte)

        self._byte_chk = check_byte
        self._byte = byte

        self._storage_number = byte & self.STORAGE_NUMBER_MASK
        self._tariff = (byte & self.TARIFF_MASK) >> 4
        self._device_unit = int((byte & self.DEVICE_UNIT_MASK) != 0)
        self._ext = int((byte & self.EXTENSION_BIT_MASK) != 0)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(byte={self._byte}, check_byte={self._byte_chk})"

    @property
    def storage_number(self) -> int:
        return self._storage_number

    @property
    def tariff(self) -> int:
        return self._tariff

    @property
    def device_unit(self) -> int:
        return self._device_unit

    @property
    def extension_bit(self) -> int:
        return self._ext


class DataInformationBlock:
    """Data Information Block (DIB) class.

    The DIB contains at least one byte (DIF, data information field),
    and can be extended by a maximum of ten DIFE's (DIF extensions).
    """

    MAX_DIFE_FRAMES = 10

    # TODO: TEST PURITY
    @classmethod
    def from_hexstring(cls, hex: str) -> Self:
        """Return a `DataInformationBlock` from a hexadecimal string."""

        barr = bytearray.fromhex(iter(hex))
        return cls(barr)

    @classmethod
    def from_integers(cls, ints: Iterable[int]) -> Self:
        """Return a `DataInformationBlock` from a sequence of integers."""

        barr = bytearray(iter(ints))
        return cls(barr)

    # MUST AFFECT frame and wind it
    @classmethod
    def parse_frame(cls):
        pass

    def __init__(self, bytes_: bytearray):
        self._bytes = bytes_
        self._dif = DataInformationField(bytes_[0], check_byte=True)
        self._difes = self._parse_dife_blocks(bytes_, check_bytes=True)

    # TODO: iterable and `async for`able`

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(bytes_={self._bytes})"

    def __str__(self) -> str:
        return str([self._dif] + self._difes)

    def _parse_dife_blocks(
        self, bytes_: bytearray, *, check_bytes: bool = False
    ) -> list[DataInformationFieldExtension]:
        dif = DataInformationField(byte=bytes_[0], check_byte=check_bytes)
        difes: list[DataInformationFieldExtension] = []

        if not dif.extension_bit:
            return difes

        pos = 1
        max_frame = self.MAX_DIFE_FRAMES + 1
        while byte := bytes_[pos]:
            dife = DataInformationFieldExtension(byte=byte, check_byte=check_bytes)
            difes.append(dife)
            if not dife.extension_bit:
                break
            pos += 1
            if pos == max_frame:
                break
        return difes
