from datetime import datetime

import pytest

from aiombus.datetimes import get_datetime


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
def test_datetime_parsing(hexdata: str, dt: str):
    bindata = bytearray.fromhex(hexdata)

    result = get_datetime(bindata)

    assert result == dt


def test_datetime_parsing_invalid_frame_length():
    bindata = bytearray.fromhex("1E 0A 0A 25")
    with pytest.raises(ValueError):
        get_datetime(bindata)
