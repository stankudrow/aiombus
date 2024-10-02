"""The Meter-Bus type classes and functions.

Glossary:

- a byte = 8 bits
- a nibble = 4 bits
- a BCD = a "Binary-Coded Decimal".

The standard IEC 870-5-4 defines the following data types for usage inside the application
layer:

- Type A = Unsigned Integer BCD;
- Type B = Binary Integer;
- Type C = Unsigned Integer;
- Type D = Boolean (can be a subtype of Integer);
- Type E = Compound CP16 -> types and units information;
- Type F = Compound CP32 -> date and time;
- Type G = Compound CP16 -> date;


Type A, or Unsigned Integer BCD -> 1 or more bytes.
Decoded per nibbles (4 bits).

Type B, or Signed Binary Integer -> 1 or more bytes.
The most significant bit (MSB) of the last byte denotes the sign (S):
if S is 0 (zero), the number is positive,
otherwise, the rest bits are negative values in two's complement.

Type C, or Unsigned Integer -> 1 or more bytes.
Computed as a unit of concatenated bytes.

Type D, or Boolean -> 1 or more bytes.
The boolean of a unit of concatenated bytes.

Type E, or Compound CP16 (types and units information) -> 2 bytes.

Type F = Compound CP32: Date and Time -> 4 bytes.

Type G, or Compound CP16: Date -> 2 bytes.
"""

from collections.abc import Iterable, Iterator
from datetime import date, datetime, time
from typing import Self

from aiombus.constants import BIG_ENDIAN, BYTE, NIBBLE
from aiombus.exceptions import MBusError

# TODO: type A, type H
# TODO: a unified integer type: as_uint, as_bcd etc.

BytesType = bytes | bytearray | Iterable[int]


## Integer types section


def parse_binary_integer(ibytes: BytesType) -> int:
    """Returns the signed binary integer from `bytez`.

    The "Binary Integer" type = "Type B".
    The bytes are parsed along the Big endian order.

    Parameters
    ----------
    ibytes: bytes | bytearray
        the sequence of bytes for "Type B" parsing

    Raises
    ------
    MBusDecodeError
        if an empty byte sequence is given

    Returns
    -------
    int
    """

    _bytes = bytes(reversed(ibytes))
    if not _bytes:
        msg = "cannot parse empty bytes"
        raise MBusError(msg)

    # the sequence is reversed, the last got the first
    neg_sign = _bytes[0] & 0x80
    value = 0

    for byte in _bytes:
        value = value << BYTE

        if neg_sign:
            value += byte ^ 0xFF  # two's compliment
        else:
            value += byte

    if neg_sign:
        value = (-value) - 1  # two's compliment

    return value


def parse_unsigned_integer(ibytes: BytesType) -> int:
    """Returns the unsigned integer from `bytez`.

    The "Unsigned Integer" type = "Type C".
    The bytes are parsed along the Big endian order.

    Parameters
    ----------
    ibytes: bytes | bytearray
        the sequence of bytes for "Type C" parsing

    Raises
    ------
    MBusDecodeError
        if an empty byte sequence is given

    Returns
    -------
    int
    """

    _bytes = bytes(ibytes)
    if not _bytes:
        msg = "cannot parse empty bytes"
        raise MBusError(msg)

    return int.from_bytes(_bytes, byteorder=BIG_ENDIAN, signed=False)


def parse_boolean(ibytes: BytesType) -> bool:
    """Returns the boolean value from `bytez`.

    The "Boolean" type = "Type D".
    The bytes are parsed along the Big endian order.

    Parameters
    ----------
    ibytes: bytes | bytearray
        the sequence of bytes for "Type D" parsing

    Raises
    ------
    MBusDecodeError
        if an empty byte sequence is given

    Returns
    -------
    bool
    """

    return bool(parse_unsigned_integer(ibytes))


## date, time and datetime types section


YEAR_MASK_LSB = 0xE0
YEAR_MASK_MSB = 0xF0
MONTH_MASK = 0xF
DAY_MASK = 0x1F

HOUR_MASK = 0x1F
MINUTE_MASK = 0x3F
SECOND_MASK = 0x3F


### Date section


def get_year(lsp: int, msp: int) -> int:
    """Return the value of years from `lsp` and `msp` parts."""

    year_lsp = lsp & YEAR_MASK_LSB
    year_msp = msp & YEAR_MASK_MSB

    # concatenating MS and LS parts
    year = (year_msp | (year_lsp >> NIBBLE)) >> 1

    if year < 81:
        return 2000 + year
    return 1900 + year


def get_month(byte: int) -> int:
    """Return the value of months from a byte."""

    return byte & MONTH_MASK


def get_day(byte: int) -> int:
    """Return the value of days from a byte."""

    return byte & DAY_MASK


def get_date(ibytes: BytesType) -> date:
    """Return the Python date from a binary frame."""

    frame = bytes(ibytes)

    dt0 = frame[0]
    dt1 = frame[1]

    return date(
        year=get_year(lsp=dt0, msp=dt1),
        month=get_month(byte=dt1),
        day=get_day(byte=dt0),
    )


def parse_date(frame: Iterator[int]) -> date:
    """Return the Python date from a byte iterator.

    Parameters
    ----------
    frame: Iterator[int]
        a frame of bytes for date parsing

    Returns
    -------
    date
    """

    it = iter(frame)
    lst = [next(it) for _ in range(2)]

    return get_date(bytearray(lst))


class Date:
    """Type G = Compound CP16: Date."""

    @classmethod
    def from_date(cls, date_: date) -> Self:
        """Return a `Date` from a Python date."""

        return cls(year=date_.year, month=date_.month, day=date_.day)

    @classmethod
    def from_bytearray(cls, frame: bytearray) -> Self:
        """Return a `Date` from an array of bytes."""

        date_ = get_date(frame)
        return cls.from_date(date_)

    @classmethod
    def from_hexstring(cls, hex: str) -> Self:
        """Return a `Date` from a hexadecimal string."""

        barr = bytearray.fromhex(hex)
        return cls.from_bytearray(barr)

    @classmethod
    def from_integers(cls, ints: Iterable[int]) -> Self:
        """Return a `Date` from a sequence of integers."""

        barr = bytearray(iter(ints))
        return cls.from_bytearray(barr)

    def __init__(self, year: int, month: int, day: int):
        self._date = date(year=year, month=month, day=day)

    def __eq__(self, other) -> bool:
        if isinstance(other, Date):
            return self._date == other.date
        if isinstance(other, date):
            return self._date == other
        return self._date == date(*other)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(year={self.year}, month={self.month}, day={self.day})"

    @property
    def year(self) -> int:
        return self._date.year

    @property
    def month(self) -> int:
        return self._date.month

    @property
    def day(self) -> int:
        return self._date.day

    @property
    def date(self) -> date:
        return self._date

    def to_iso_format(self) -> str:
        return self._date.isoformat()


### Time section


def get_hour(byte: int) -> int:
    """Return the value of hours from a byte."""

    return byte & HOUR_MASK


def get_minute(byte: int) -> int:
    """Return the value of minutes from a byte."""

    return byte & MINUTE_MASK


def get_second(byte: int) -> int:
    """Return the value of seconds from a byte."""

    return byte & SECOND_MASK


def get_time(ibytes: BytesType) -> time:
    """Return the Python time from a binary frame."""

    frame = bytes(ibytes)

    dt0 = frame[0]
    dt1 = frame[1]
    sec_byte = 0

    frame_length = len(frame)
    if frame_length == 3:
        sec_byte = frame[2]
    if frame_length == 5:
        sec_byte = frame[4]

    return time(
        hour=get_hour(byte=dt1),
        minute=get_minute(byte=dt0),
        second=get_second(byte=sec_byte),
    )


def parse_time(frame: Iterator[int]) -> time:
    """Return the Python time from a byte iterator.

    Parameters
    ----------
    frame: Iterator[int]
        a frame of bytes for time parsing

    Returns
    -------
    time
    """

    it = iter(frame)
    lst = [next(it) for _ in range(2)]

    sec_byte: None | int = None
    try:
        sec_byte = next(it)
        next(it)
        sec_byte = next(it)
    except StopIteration:
        pass

    if sec_byte:
        lst += [sec_byte]

    return get_time(bytearray(lst))


class Time:
    """Time class.

    Not a part of the Meter-Bus defined types.
    A custom type to facilitate time operations.
    """

    _sep: str = ":"

    @classmethod
    def from_time(cls, time_: time) -> Self:
        return cls(
            hour=time_.hour,
            minute=time_.minute,
            second=time_.second,
        )

    @classmethod
    def from_bytearray(cls, frame: bytearray) -> Self:
        """Return a `Time` from an array of bytes."""

        time_ = get_time(frame)
        return cls.from_time(time_)

    @classmethod
    def from_hexstring(cls, hex: str) -> Self:
        """Return a `Time` from a hexadecimal string."""

        barr = bytearray.fromhex(hex)
        return cls.from_bytearray(barr)

    @classmethod
    def from_integers(cls, it: Iterable[int]) -> Self:
        """Return a `Time` from an iterable of integers."""

        time_ = parse_time(iter(it))
        return cls.from_time(time_)

    def __init__(self, hour: int, minute: int, second: int = 0):
        self._time = time(hour=hour, minute=minute, second=second)

    def __eq__(self, other) -> bool:
        if isinstance(other, Time):
            return self._time == other.time
        if isinstance(other, time):
            return self._time == other
        return self._time == time(*other)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return (
            f"{cls_name}(hour={self.hour}, minute={self.minute}, second={self.second})"
        )

    @property
    def hour(self) -> int:
        return self._time.hour

    @property
    def minute(self) -> int:
        return self._time.minute

    @property
    def second(self) -> int:
        return self._time.second

    @property
    def time(self) -> time:
        return self._time

    def to_iso_format(self, *, timespec: str = "auto") -> str:
        return self._time.isoformat(timespec=timespec)

    def to_hhmm_format(self) -> str:
        fmt = self._time.isoformat()
        return self._sep.join(fmt.split(self._sep)[:2])

    def to_hhmmss_format(self) -> str:
        fmt = self._time.isoformat()
        return self._sep.join(fmt.split(self._sep)[:3])


### DateTime section


def get_datetime(ibytes: BytesType) -> datetime:
    """Return the Python datetime from a binary frame."""

    frame = bytes(ibytes)

    dt0 = frame[0]
    dt1 = frame[1]
    dt2 = frame[2]
    dt3 = frame[3]

    dt4 = 0
    if len(frame) == 5:
        dt4 = frame[4]

    return datetime(
        year=get_year(lsp=dt2, msp=dt3),
        month=get_month(dt3),
        day=get_day(dt2),
        hour=get_hour(dt1),
        minute=get_minute(dt0),
        second=get_second(dt4),
    )


def parse_datetime(frame: Iterator[int]) -> datetime:
    """Return the Python datetime from a byte iterator.

    Parameters
    ----------
    frame: Iterator[int]
        a frame of bytes for datetime parsing

    Returns
    -------
    datetime
    """

    it = iter(frame)
    lst = [next(it) for _ in range(4)]

    try:
        lst += [next(it)]
    except StopIteration:
        pass

    return get_datetime(bytearray(lst))


class DateTime:
    """Type F = Compound CP32: Date and Time."""

    @classmethod
    def from_datetime(cls, datetime_: datetime) -> Self:
        """Return a `DateTime` from a Python datetime."""

        return cls(
            year=datetime_.year,
            month=datetime_.month,
            day=datetime_.day,
            hour=datetime_.hour,
            minute=datetime_.minute,
            second=datetime_.second,
        )

    @classmethod
    def from_bytearray(cls, frame: bytearray) -> Self:
        """Return a `DateTime` from an array of bytes."""

        datetime_ = get_datetime(frame)
        return cls.from_datetime(datetime_)

    @classmethod
    def from_hexstring(cls, hex: str) -> Self:
        """Return a `DateTime` from a hexadecimal string."""

        barr = bytearray.fromhex(hex)
        return cls.from_bytearray(barr)

    @classmethod
    def from_integers(cls, it: Iterable[int]) -> Self:
        """Return a `DateTime` from an iterable of integers."""

        datetime_ = parse_datetime(iter(it))
        return cls.from_datetime(datetime_)

    def __init__(
        self, year: int, month: int, day: int, hour: int, minute: int, second: int = 0
    ):
        self._datetime = datetime(
            year=year, month=month, day=day, hour=hour, minute=minute, second=second
        )

    def __eq__(self, other) -> bool:
        if isinstance(other, DateTime):
            return self._datetime == other.datetime
        if isinstance(other, datetime):
            return self._datetime == other
        return self._datetime == datetime(*other)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return (
            f"{cls_name}("
            f"year={self.year}, month={self.month}, day={self.day}, "
            f"hour={self.hour}, minute={self.minute}, second={self.second})"
        )

    @property
    def year(self) -> int:
        return self._datetime.year

    @property
    def month(self) -> int:
        return self._datetime.month

    @property
    def day(self) -> int:
        return self._datetime.day

    @property
    def hour(self) -> int:
        return self._datetime.hour

    @property
    def minute(self) -> int:
        return self._datetime.minute

    @property
    def second(self) -> int:
        return self._datetime.second

    @property
    def datetime(self) -> datetime:
        return self._datetime

    def to_datetime_no_sec(self) -> str:
        iso_fmt = self.to_iso_format()
        return ":".join(iso_fmt.split(":")[:-1])

    def to_datetime_with_sec(self) -> str:
        return self.to_iso_format()

    def to_iso_format(self) -> str:
        return self._datetime.isoformat()
