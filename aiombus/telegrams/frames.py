"""Telegram frames of the M-Bus protocol."""

from typing import Self

from aiombus.exceptions import MBusDecodeError
from aiombus.telegrams.fields import AddressField, ControlField


ACK_BYTE = 0xE5

SHORT_FRAME_START_BYTE = 0x10
SHORT_FRAME_STOP_BYTE = 0x16


class SingleFrame:
    """The Single Character Frame class.

    This format consists of a single character, namely the E5h (decimal 229),
    and serves to acknowledge receipt of transmissions.
    """

    @classmethod
    def from_byte(cls, byte: int) -> Self:
        """Decode a Single (ACK) Frame from a byte integer.

        Parameters
        ----------
        byte: int
            a byte integer candidate for being a Single Character (ACK) Frame.

        Raises
        ------
        MBusDecodeError:
            if the byte integer is not a Single Character Frame.

        Returns
        -------
        Self
        """

        if byte != ACK_BYTE:
            msg = f"the {byte!r} is not a valid Single (ACK) Frame"
            raise MBusDecodeError(msg)

        return SingleFrame()

    def __init__(self):
        self._ack = ACK_BYTE


class ShortFrame:
    """The Short Character Frame class.

    This format with a fixed length begins with the start character 10h,
    and besides the C and A fields includes the check sum
    (this is made up from the two last mentioned characters),
    and the stop character 16h.This format consists of a single character, namely the E5h (decimal 229),
    and serves to acknowledge receipt of transmissions.

    The "Short Frame" 5 elements scheme:

    1. start 0x10 (10h);
    2. C field;
    3. A field;
    4. check sum;
    5. stop 0x16 (16h)
    """

    def __init__(self, data, *, strict_length: bool = False):
        self._check_length(data, strict_length=strict_length)
        self._parse_frame(data)

    def _check_length(self, data, *, strict_length: bool = False):
        length = len(data)

        length_check_failed = (length != 5) if strict_length else (length < 5)
        if length_check_failed:
            msg = f"the {data!r} has invalid length for the ShortFrame class"
            raise MBusDecodeError(msg)

    def _parse_frame(self, data):
        byte = data[0]
        if byte != SHORT_FRAME_START_BYTE:
            msg = f"the first byte {byte!r} is invalid for the Short Frame start byte"
            raise MBusDecodeError(msg)
        self._start_byte = byte

        self._c_field = ControlField(data[1])
        self._a_field = AddressField(data[2])
        self._check_sum = data[3]

        byte = data[4]
        if byte != SHORT_FRAME_STOP_BYTE:
            msg = f"the fifth byte {byte!r} is invalid for the Short Frame stop byte"
            raise MBusDecodeError(msg)
        self._stop_byte = byte

    @property
    def start_byte(self) -> int:
        return self._start_byte

    @property
    def control_field(self) -> int:
        return self._c_field

    @property
    def address_field(self) -> int:
        return self._a_field

    @property
    def check_sum(self) -> int:
        return self._check_sum

    @property
    def stop_byte(self) -> int:
        return self._stop_byte
