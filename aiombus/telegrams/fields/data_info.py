from enum import IntEnum

from aiombus.telegrams.base import TelegramField


class DataInformationField(TelegramField):
    """Data Information Field (DIF) class.

    The structure of the DIF:
    --------------------------------------------------------------
    |  bit |     7     |          6         |   5  4   | 3 2 1 0 |
    +------+-----------+--------------------+----------+---------+
    | desc | extension | storage number LSB | function |   data  |
    --------------------------------------------------------------
    """

    DATA_FIELD_MASK = 0x0F  # 0b0000_1111
    FUNCTION_FIELD_MASK = 0x30  # 0b0011_0000
    STORAGE_NUMBER_LSB_MASK = 0x40  # 0b0100_0000
    EXTENSION_BIT_MASK = 0x80  # 0b1000_0000

    def __init__(self, byte: int):
        super().__init__(byte)

        self._data = byte & self.DATA_FIELD_MASK
        self._func = (byte & self.FUNCTION_FIELD_MASK) >> 4
        self._sn_lsb = int((byte & self.STORAGE_NUMBER_LSB_MASK) != 0)
        self._ext = int((byte & self.EXTENSION_BIT_MASK) != 0)

    @property
    def data(self) -> int:
        return self._data

    @property
    def function(self) -> int:
        return self._func

    @property
    def storage_number_lsb(self) -> int:
        return self._sn_lsb

    @property
    def extension(self) -> int:
        return self._ext


# BCD = Type A. Integer = Type B. Real = Type H.
class DataFieldCode(IntEnum):
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


class FunctionFieldCode(IntEnum):
    instantaneous = 0b00
    maximum = 0b01
    minimum = 0b10
    error = 0b11


class DataInformationFieldExtension(TelegramField):
    """Data Information Field Extension (DIFE) class.

    The structure of the DIFE:
    ----------------------------------------------------------------
    |  bit |     7     |       6       |   5  4   |   3  2  1  0   |
    +------+-----------+---------------+----------+----------------+
    | desc | extension | device (unit) |  tariff  | storage number |
    ----------------------------------------------------------------
    """

    STORAGE_NUMBER_MASK = 0x0F  # 0b0000_1111
    TARIFF_MASK = 0x30  # 0b0011_0000
    DEVICE_UNIT_MASK = 0x40  # 0b0100_0000
    EXTENSION_BIT_MASK = 0x80  # 0b1000_0000

    def __init__(self, byte: int):
        super().__init__(byte)

        self._storage_number = byte & self.STORAGE_NUMBER_MASK
        self._tariff = (byte & self.TARIFF_MASK) >> 4
        self._device_unit = int((byte & self.DEVICE_UNIT_MASK) != 0)
        self._ext = int((byte & self.EXTENSION_BIT_MASK) != 0)

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
    def extension(self) -> int:
        return self._ext
