"""Telegram frames of the M-Bus protocol.

The fields:

- A = address
- C = control
- CI = control information
- L = length

"""

from collections.abc import Generator, Iterable, Iterator
from typing import Self

from aiombus.exceptions import MBusDecodeError
from aiombus.telegrams.fields import (
    TelegramField as Field,
    AddressField,
    ControlField,
)


ACK_BYTE = 0xE5

FRAME_STOP_BYTE = 0x16

SHORT_FRAME_START_BYTE = 0x10
CONTROL_FRAME_START_BYTE = 0x68
LONG_FRAME_START_BYTE = CONTROL_FRAME_START_BYTE


class TelegramFrame:
    """The base class for Frame type."""

    def __getitem__(self, idx: int) -> Field:
        return self._frame[idx]

    def __iter__(self) -> Generator[None, None, Field]:
        for field in self._frame:
            yield field

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(frame={self._frame})"

    def __str__(self) -> str:
        return str(list(self))


class SingleFrame(TelegramFrame):
    """The "Single Character" Frame class.

    This format consists of a single character, namely the 0xE5 (229),
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
        self._frame = [Field(ACK_BYTE)]

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}()"


class ShortFrame(TelegramFrame):
    """The "Short Frame" class.

    This format with a fixed length begins with the start character 10h,
    and besides the C and A fields includes the check sum
    (this is made up from the two last mentioned characters),
    and the stop character 16h.This format consists of a single character, namely the E5h (decimal 229),
    and serves to acknowledge receipt of transmissions.

    The "Short Frame" elements scheme:

    1. start 0x10;
    2. C field;
    3. A field;
    4. check sum;
    5. stop 0x16.
    """

    def __init__(self, frame: Iterable[int]):
        _frame = list(frame)
        try:
            self._parse_frame(iter(_frame))
        except StopIteration as e:
            msg = f"invalid data for ShortFrame: {_frame}"
            raise MBusDecodeError(msg) from e

        self._frame: list[Field] = [
            self._start,
            self._c_field,
            self._a_field,
            self._check_sum,
            self._stop,
        ]

    def _parse_frame(self, it: Iterator[int]):
        field = Field(next(it))
        if (byte := field.byte) != SHORT_FRAME_START_BYTE:
            msg = f"the first byte {byte!r} is invalid for the Short Frame start byte"
            raise MBusDecodeError(msg)
        self._start = field

        self._c_field = ControlField(next(it))
        self._a_field = AddressField(next(it))
        self._check_sum = next(it)

        field = Field(next(it))
        if (byte := field.byte) != FRAME_STOP_BYTE:
            msg = f"the fifth byte {byte!r} is invalid for the Short Frame stop byte"
            raise MBusDecodeError(msg)
        self._stop = Field(byte)


# class ControlFrame(TelegramFrame):
#     """The "Control Frame" class.

#     The control sentence conforms to the long sentence without user data,
#     with an L field from the contents of 3. The check sum is calculated
#     at this point from the fields C, A and CI.

#     The "Control Frame" elements scheme:

#     1. start 0x68;
#     2. L field = 3;
#     3. L field = 3;
#     4. start 0x68;
#     5. C field;
#     6. A field;
#     7. CI field;
#     8. check sum;
#     9. stop 0x16.
#     """

#     def __init__(self, data, *, strict_length: bool = False):
#         self._check_length(data, strict_length=strict_length)
#         self._parse_frame(data)

#     def _check_length(self, data, *, strict_length: bool = False):
#         length = len(data)
#         bound = 9

#         length_check_failed = (length != bound) if strict_length else (length < bound)
#         if length_check_failed:
#             msg = f"the {data!r} has invalid length for the ShortFrame class"
#             raise MBusDecodeError(msg)

#     def _parse_frame(self, data):
#         byte = data[0]
#         if byte != CONTROL_FRAME_START_BYTE:
#             msg = f"the first byte {byte!r} is invalid for the Control Frame start byte"
#             raise MBusDecodeError(msg)
#         self._start_byte = byte

#         self._c_field = ControlField(data[1])
#         self._a_field = AddressField(data[2])
#         self._check_sum = data[3]

#         byte = data[4]
#         if byte != FRAME_STOP_BYTE:
#             msg = f"the fifth byte {byte!r} is invalid for the Short Frame stop byte"
#             raise MBusDecodeError(msg)
#         self._stop_byte = byte
