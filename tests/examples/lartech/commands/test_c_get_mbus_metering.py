from typing import Any

import pytest

from aiombus.structures import MeasuredMedium


def _parse_electricity_specific(byte: int) -> str:
    key = byte & 0b0000_1111
    ext = byte & 0b1000_0000

    if ext:
        return {
            0b0000_0001: "Активная потреблённая А+",
            0b0000_0010: "Активная выданная А-",
            0b0000_0100: "Реактивная потреблённая R+",
            0b0000_1000: "Реактивная выданная R-",
            0b0000_1111: "Все квадранты, поддерживаемые конкретным ПУ",
        }[key]
    return {
        0b0000_0001: "Тариф Т0 (сумма по всем тарифам)",
        0b0000_0010: "Тариф Т1",
        0b0000_0100: "Тариф Т2",
        0b0000_1000: "Тариф Т3",
        0b0000_1111: "Все тарифы, поддерживаемые конкретным ПУ",
    }[key]


def _parse_first_byte(byte: int) -> dict[str, Any]:
    key = "metering"
    res: dict[str, Any] = {key: {}}

    medium = MeasuredMedium(byte & 0b0000_1111)
    mtype = (byte & 0b1111_0000) >> 4

    res[key]["medium"] = medium
    res[key]["type"] = "simple" if mtype == 0b0000_0010 else "other"

    return res


def _parse_dif(byte: int) -> dict[str, Any]:
    key = "metering"
    res: dict[str, Any] = {key: {}}

    medium = MeasuredMedium(byte & 0b0000_1111)
    mtype = (byte & 0b1111_0000) >> 4

    res[key]["medium"] = medium
    res[key]["type"] = "simple" if mtype == 0b0000_0010 else "other"

    return res


def c_get_mbus_metering(hex: str) -> dict[str, Any]:
    barr = bytearray.fromhex(hex)

    res: dict[str, Any] = {}
    res |= _parse_first_byte(barr[0])

    return res


@pytest.mark.parametrize(
    ("hex", "answer"),
    [
        (
            "22 04 A9 FF 81 80 6D 1E 0A 6A 28",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.electricity,
                }
            },
        )
    ],
)
def test_c_get_mbus_metering(hex: str, answer: dict[str, Any]):
    assert c_get_mbus_metering(hex) == answer
