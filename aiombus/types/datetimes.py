"""The Meter-Bus types."""

from datetime import date, datetime, time
from typing import Iterable, Self


YEAR_MASK_LSB = 0xE0
YEAR_MASK_MSB = 0xF0
MONTH_MASK = 0xF
DAY_MASK = 0x1F

HOUR_MASK = 0x1F
MINUTE_MASK = 0x3F
SECOND_MASK = 0x3F


## auxiliary entities


## Date section


def get_year(lsp: int, msp: int) -> int:
    """Return the value of years from `lsp` and `msp` parts."""

    year_lsp = lsp & YEAR_MASK_LSB
    year_msp = msp & YEAR_MASK_MSB

    # concatenating MS and LS parts
    year = (year_msp | (year_lsp >> 4)) >> 1

    if year < 81:
        return 2000 + year
    return 1900 + year


def get_month(byte: int) -> int:
    """Return the value of months from a byte."""

    return byte & MONTH_MASK


def get_day(byte: int) -> int:
    """Return the value of days from a byte."""

    return byte & DAY_MASK


def get_date(frame: bytearray) -> date:
    """Return the Python date from a binary frame."""

    dt0 = frame[0]
    dt1 = frame[1]

    return date(
        year=get_year(lsp=dt0, msp=dt1),
        month=get_month(byte=dt1),
        day=get_day(byte=dt0),
    )


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


def get_time(frame: bytearray) -> time:
    """Return the Python time from a binary frame."""

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


class Time:
    """Time class.

    Not a art of Meter-Bus standard types.
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
        time_ = get_time(frame)
        return cls.from_time(time_)

    @classmethod
    def from_hexstring(cls, hex: str) -> Self:
        barr = bytearray.fromhex(hex)
        return cls.from_bytearray(barr)

    @classmethod
    def from_integers(cls, ints: Iterable[int]) -> Self:
        barr = bytearray(iter(ints))
        return cls.from_bytearray(barr)

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


## DateTime section


def get_datetime(frame: bytearray) -> datetime:
    """Return the Python datetime from a binary frame."""

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
    def from_integers(cls, ints: Iterable[int]) -> Self:
        """Return a `DateTime` from a sequence of integers."""

        barr = bytearray(iter(ints))
        return cls.from_bytearray(barr)

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
