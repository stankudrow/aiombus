from contextlib import AbstractContextManager, nullcontext as does_not_raise
from datetime import date, datetime, time

import pytest

from aiombus.types import Date, DateTime, Time


### date section


@pytest.mark.parametrize(
    ("year", "month", "day", "expectation"),
    [
        (2000, 1, 2, does_not_raise()),
        (0, 0, 0, pytest.raises(ValueError, match="year 0 is out of range")),
        (1, 0, 0, pytest.raises(ValueError, match="month must be in 1..12")),
        (1, 1, 0, pytest.raises(ValueError, match="day is out of range for month")),
        (1, 1, 1, does_not_raise()),
    ],
)
def test_date_init(
    year: int, month: int, day: None | int, expectation: AbstractContextManager
):
    with expectation:
        date_ = Date(year=year, month=month, day=day)

        assert date_ == date_
        assert date_ == date(year=year, month=month, day=day)
        assert date_ == (year, month, day)


@pytest.mark.parametrize(
    ("hexdata", "dt"),
    [
        (
            "0A 25",
            date(year=2016, month=5, day=10),
        ),
        (
            "6A 28",
            date(year=2019, month=8, day=10),
        ),
        (
            "45 2C",
            date(year=2018, month=12, day=5),
        ),
        (
            "6A 25",
            date(year=2019, month=5, day=10),
        ),
    ],
)
def test_parse_date(hexdata: str, dt: str):
    bindata = bytearray.fromhex(hexdata)
    integers = list(bindata)  # or list(map(int, bindata))

    assert Date.from_bytearray(bindata) == dt
    assert Date.from_hexstring(hexdata) == dt
    assert Date.from_integers(integers) == dt


@pytest.mark.parametrize(
    ("year", "month", "day"),
    [
        (2000, 4, 17),
        (2000, 2, 29),
    ],
)
def test_date_equality(year: int, month: int, day: int):
    date_ = Date(year=year, month=month, day=day)

    assert date_ == date_
    assert date_ == date(year=year, month=month, day=day)
    assert date_ == (year, month, day)


def test_date_repr():
    year, month, day = 2000, 11, 23

    date_ = Date(year=year, month=month, day=day)

    assert repr(date_) == f"Date(year={year}, month={month}, day={day})"


def test_date_to_iso():
    year, month, day = 2000, 11, 23

    date_ = Date(year=year, month=month, day=day)

    assert date_.to_iso_format() == f"{year}-{month}-{day}"


### time section


@pytest.mark.parametrize(
    ("hour", "minute", "second", "expectation"),
    [
        (23, 59, 59, does_not_raise()),
        (0, 0, 0, does_not_raise()),
        (1, 2, None, does_not_raise()),
    ],
)
def test_time_init(
    hour: int, minute: int, second: None | int, expectation: AbstractContextManager
):
    with expectation:
        if second is None:
            time_ = Time(hour=hour, minute=minute)
            assert time_.second == 0
        else:
            time_ = Time(hour=hour, minute=minute, second=second)


@pytest.mark.parametrize(
    ("hexdata", "dt"),
    [
        (
            "1E 0A",
            time(hour=10, minute=30, second=0),
        ),
        (
            "1E 09 0F",
            time(hour=9, minute=30, second=15),
        ),
        (
            "1E 0B 37",
            time(hour=11, minute=30, second=55),
        ),
        (
            "3B 17 3B",
            time(hour=23, minute=59, second=59),
        ),
    ],
)
def test_parse_time(hexdata: str, dt: str):
    bindata = bytearray.fromhex(hexdata)
    integers = list(bindata)  # or list(map(int, bindata))

    assert Time.from_bytearray(bindata) == dt
    assert Time.from_hexstring(hexdata) == dt
    assert Time.from_integers(integers) == dt


@pytest.mark.parametrize(
    ("hour", "minute", "second"),
    [
        (23, 59, 59),
        (0, 0, 0),
    ],
)
def test_time_equality(hour: int, minute: int, second: int):
    time_ = Time(hour=hour, minute=minute, second=second)

    assert time_ == time_
    assert time_ == time(hour=hour, minute=minute, second=second)
    assert time_ == (hour, minute, second)


def test_time_repr():
    hour, minute, second = 23, 59, 59

    time_ = Time(hour=hour, minute=minute, second=second)

    assert repr(time_) == f"Time(hour={hour}, minute={minute}, second={second})"


def test_time_to_iso():
    hour, minute, second = 23, 59, 59

    time_ = Time(hour=hour, minute=minute, second=second)

    assert time_.to_iso_format() == f"{hour}:{minute}:{second}"


def test_time_to_strings():
    hour, minute, second = 23, 59, 59

    time_ = Time(hour=hour, minute=minute, second=second)

    assert time_.to_iso_format() == time_.to_hhmmss_format()
    assert time_.to_hhmm_format() == f"{hour}:{minute}"


@pytest.mark.parametrize(
    ("hexdata", "dt"),
    [
        (
            "1E 0A 0A 25 0F",
            datetime(year=2016, month=5, day=10, hour=10, minute=30, second=15),
        ),
        (
            "1E 09 6A 28 00",
            datetime(year=2019, month=8, day=10, hour=9, minute=30, second=0),
        ),
        (
            "1E 0B 45 2C 37",
            datetime(year=2018, month=12, day=5, hour=11, minute=30, second=55),
        ),
        (
            "3B 17 6A 25 3B",
            datetime(year=2019, month=5, day=10, hour=23, minute=59, second=59),
        ),
    ],
)
def test_parse_datetime(hexdata: str, dt: str):
    bindata = bytearray.fromhex(hexdata)
    integers = list(bindata)  # or list(map(int, bindata))

    assert DateTime.from_bytearray(bindata) == dt
    assert DateTime.from_hexstring(hexdata) == dt
    assert DateTime.from_integers(integers) == dt


def test_datetime_to_iso():
    year, month, day, hour, minute, second = 1999, 12, 31, 23, 59, 59

    datetime_ = DateTime(
        year=year, month=month, day=day, hour=hour, minute=minute, second=second
    )

    assert datetime_.to_iso_format() == f"{year}-{month}-{day}T{hour}:{minute}:{second}"


def test_datetime_to_strings():
    year, month, day, hour, minute, second = 1999, 12, 31, 23, 59, 59

    datetime_ = DateTime(
        year=year, month=month, day=day, hour=hour, minute=minute, second=second
    )

    assert datetime_.to_iso_format() == datetime_.to_datetime_with_sec()
    assert datetime_.to_datetime_no_sec() == f"{year}-{month}-{day}T{hour}:{minute}"
