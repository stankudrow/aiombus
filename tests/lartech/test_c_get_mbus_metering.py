from collections.abc import Iterable
from typing import Any

import pytest

from aiombus.structures.fixed import MeasuredMedium
from aiombus.tables.di import DataFieldEnum
from aiombus.telegrams.blocks import (
    DataInformationBlock as DIB,
    ValueInformationBlock as VIB,
)
from aiombus.types import (
    Date,
    DateTime,
)


### specific constants

ACTIVE_A_PLUS = "Активная потреблённая А+"
ACTIVE_A_MINUS = "Активная выданная А-"
REACTIVE_R_PLUS = "Реактивная потреблённая R+"
REACTIVE_R_MINUS = "Реактивная выданная R-"
ALL_QUADRANTS = "Все квадранты, поддерживаемые конкретным ПУ"


TARIFF_0 = ("Тариф Т0 (сумма по всем тарифам)",)
TARIFF_1 = ("Тариф Т1",)
TARIFF_2 = ("Тариф Т2",)
TARIFF_3 = ("Тариф Т3",)
ALL_TARIFFS = ("Все тарифы, поддерживаемые конкретным ПУ",)

### specific getters


def _get_electricity(byte: int) -> None | str:
    key = byte & 0b0000_1111
    ext = byte & 0b1000_0000

    if ext:
        return {
            0b0000_0001: ACTIVE_A_PLUS,
            0b0000_0010: ACTIVE_A_MINUS,
            0b0000_0100: REACTIVE_R_PLUS,
            0b0000_1000: REACTIVE_R_MINUS,
            0b0000_1111: ALL_QUADRANTS,
        }.get(key, None)
    return {
        0b0000_0001: TARIFF_0,
        0b0000_0010: TARIFF_1,
        0b0000_0100: TARIFF_2,
        0b0000_1000: TARIFF_2,
        0b0000_1111: ALL_TARIFFS,
    }.get(key, None)


def _get_time_point_class(byte: int) -> None | Date | DateTime:
    mask = 0b0110_1100

    if (byte & mask) != mask:
        return None

    if byte & 0x01:  # checking the last bit
        return DateTime
    return Date


### frame parsers


def _parse_first_byte(byte: int) -> dict[str, Any]:
    key = "metering"
    res: dict[str, Any] = {key: {}}

    medium = MeasuredMedium(byte & 0b0000_1111)
    mtype = (byte & 0b1111_0000) >> 4

    res[key]["medium"] = medium
    res[key]["type"] = "simple" if mtype == 0b0000_0010 else "other"

    return res


def _parse_dib(dib: DIB) -> dict[str, Any]:
    res: dict[str, Any] = {}

    res["type"] = DataFieldEnum(dib.dif.data)

    return res


def _parse_vib(vib: VIB) -> dict[str, Any]:
    res: dict[str, Any] = {}

    # res["unit"] = ValueInformationFieldEnum(vib.vif.data)

    if not (vifes := vib.vifes):
        return res

    vife1 = vifes[0]
    if vife1 == 0b1111_1111:
        vife2 = vifes[1]
        res["unit_kind"] = _get_electricity(vife2.byte)

        vife3 = vifes[2]
        res["tariff"] = _get_electricity(vife3.byte)

    return res


def _parse_data(vib: VIB, data: Iterable) -> dict[str, Any]:
    res: dict[str, Any] = {}

    last_vife = vib.vifes[-1]

    cls = _get_time_point_class(last_vife.byte)
    dto = cls.from_integers(iter(data))

    if cls is Date:
        res["date"] = dto
    if cls is DateTime:
        res["datetime"] = dto

    return res


def c_get_mbus_metering(hex: str) -> dict[str, Any]:
    res: dict[str, Any] = {}

    barr = bytearray.fromhex(hex)
    print(f"BARR = {barr}")
    it = iter(barr)

    res |= _parse_first_byte(next(it))

    dib = DIB(it)
    res |= _parse_dib(dib)
    print(f"DIB = {dib}")

    vib = VIB(it)
    print(f"VIB = {vib}")
    res |= _parse_vib(vib)

    res |= _parse_data(vib, it)

    return res


### the main test suit


@pytest.mark.parametrize(
    ("hex", "answer"),
    [
        (
            "22 04 A9 FF 81 80 6D 1E 0A 6A 28",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.electricity,
                },
                "type": DataFieldEnum.int32,
                "unit_kind": ACTIVE_A_PLUS,
                "tariff": None,
                "datetime": DateTime(
                    year=2019,
                    month=8,
                    day=10,
                    hour=10,
                    minute=30,
                ),
            },
        )
    ],
)
def test_c_get_mbus_metering(hex: str, answer: dict[str, Any]):
    assert c_get_mbus_metering(hex) == answer
