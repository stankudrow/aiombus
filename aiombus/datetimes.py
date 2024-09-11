from datetime import datetime


YEAR_MASK_LSB = 0xE0
YEAR_MASK_MSB = 0xF0
MONTH_MASK = 0xF
DAY_MASK = 0x1F

HOUR_MASK = 0x1F
MINUTE_MASK = 0x3F
SECOND_MASK = 0x3F


def get_year(lsp: int, msp: int) -> int:
    """Return a year value from `lsp` and `msp` parts.

    Parameters
    ----------
    lsp - least significant part (!)
    msp - most significant part (!)

    Returns
    -------
    int - a parsed year
    """

    year_lsp = lsp & YEAR_MASK_LSB
    year_msp = msp & YEAR_MASK_MSB

    # concatenating MS and LS parts
    year = (year_msp | (year_lsp >> 4)) >> 1

    if year < 81:
        return 2000 + year
    return 1900 + year


def get_month(byte: int) -> int:
    """Return a month value from the `byte`."""

    return byte & MONTH_MASK


def get_day(byte: int) -> int:
    """Return a day value from the `byte`."""

    return byte & DAY_MASK


def get_hour(byte: int) -> int:
    """Return an hour value from the `byte`."""

    return byte & HOUR_MASK


def get_minute(byte: int) -> int:
    """Return a minute value from the `byte`."""

    return byte & MINUTE_MASK


def get_second(byte: int) -> int:
    """Return a second value from the `byte`."""

    return byte & SECOND_MASK


def get_datetime(frame: bytearray) -> datetime:
    """Return a `datetime.datetime` instance from the binary `frame`.

    Args:
        frame (bytearray): a binary frame for parsing datetime value

    Raises:
        ValueError: if the length of the frame is not equal to 5
    """

    if len(frame) != 5:
        msg = f"the length of datetime frame {frame} is not equal to 5"
        raise ValueError(msg)

    dt0 = frame[0]
    dt1 = frame[1]
    dt2 = frame[2]
    dt3 = frame[3]
    dt4 = frame[4]

    return datetime(
        year=get_year(lsp=dt2, msp=dt3),
        month=get_month(dt3),
        day=get_day(dt2),
        hour=get_hour(dt1),
        minute=get_minute(dt0),
        second=get_second(dt4),
    )
