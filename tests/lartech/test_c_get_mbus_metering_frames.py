from contextlib import AbstractContextManager, nullcontext
from typing import Any

import pytest

from aiombus.exceptions import MBusError
from aiombus.structures.fixed import MeasuredMedium
from aiombus.tables.di import DataFieldEnum
from aiombus.telegrams.blocks import (
    DataInformationBlock as DIB,
    ValueInformationBlock as VIB,
)
from aiombus.telegrams.fields import (
    DataInformationField as DIF,
    DataInformationFieldExtension as DIFE,
    ValueInformationField as VIF,
    ValueInformationFieldExtension as VIFE
)


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
    def _parse_data_field(field: DIF | DIFE):
        byte = field.data if isinstance(field, DIF) else field.storage_number
        return {
            "field": field,
            "encoding": DataFieldEnum(byte),
        }

    res: dict[str, Any] = {}

    res["dib"] = [_parse_data_field(dib.dif)]
    for dife in dib.difes:
        # Lartech thinks some of these blocks to be DIF
        record = _parse_data_field(dife)
        res["dib"].append(record)

    return res


def _parse_vib(vib: VIB) -> dict[str, Any]:
    res: dict[str, Any] = {}

    res["vib"] = [
        {
            "field": vib.vif,
            "unit_multiplier": None,
        }
    ]
    for vife in vib.vifes:
        record = {
            "field": vife
        }
        res["vib"].append(record)

    return res


def c_get_mbus_metering(hex: str) -> dict[str, Any]:
    res: dict[str, Any] = {}

    barr = bytearray.fromhex(hex)
    it = iter(barr)

    res |= _parse_first_byte(next(it))

    dib = DIB(it)
    res |= _parse_dib(dib)

    vib = VIB(it)
    res |= _parse_vib(vib)

    res["data"] = list(it)

    return res


### the main test suit


@pytest.mark.parametrize(
    ("hex", "answer", "expectation"),
    [
        (
            "22 82 82 82 82 81 04 FF A1 A4 A8 A7 B0 6D 59 01 00 0B 00 C8 13 88 01 1A 0C 10 3A",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.electricity,
                },
                "dib": [
                    {
                        "field": DIF(0x82),
                        "encoding": DataFieldEnum.int16,
                    },
                    {
                        "field": DIFE(0x82),
                        "encoding": DataFieldEnum.int16,
                    },
                    {
                        "field": DIFE(0x82),
                        "encoding": DataFieldEnum.int16,
                    },
                    {
                        "field": DIFE(0x82),
                        "encoding": DataFieldEnum.int16,
                    },
                    {
                        "field": DIFE(0x81),
                        "encoding": DataFieldEnum.int8,
                    },
                    {
                        "field": DIFE(0x04),
                        "encoding": DataFieldEnum.int32,
                    },
                ],
                "vib": [
                    {
                        "field": VIF(0xFF),
                        "unit_multiplier": None
                    },
                    {
                        "field": VIFE(0xA1),
                    },
                    {
                        "field": VIFE(0xA4),
                    },
                    {
                        "field": VIFE(0xA8),
                    },
                    {
                        "field": VIFE(0xA7),
                    },
                    {
                        "field": VIFE(0xB0),
                    },
                    {
                        "field": VIFE(0x6D),
                    },
                ],
                "data": [
                    0x59, 0x01,
                    0x00, 0x0B,
                    0x00, 0xC8,
                    0x13, 0x88,
                    0x01,
                    0x1A, 0x0C, 0x10, 0x3A
                ]
            },
            nullcontext(),
        ),
        (
            "27 84 02 93 FF 80 6C 00 00 17 F4 6A 28",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.water,
                },
                "dib": [
                    {
                        "field": DIF(0x84),
                        "encoding": DataFieldEnum.int32,
                    },
                    {
                        "field": DIFE(0x02),
                        "encoding": DataFieldEnum.int16,
                    },
                ],
                "vib": [
                    {
                        "field": VIF(0x93),
                        "unit_multiplier": None
                    },
                    {
                        "field": VIFE(0xFF),
                    },
                    {
                        "field": VIFE(0x80),
                    },
                    {
                        "field": VIFE(0x6C),
                    },
                ],
                "data": [
                    0x00, 0x00, 0x17, 0xF4,
                    0x6A, 0x28,
                ]
            },
            nullcontext(),
        ),
        (
            "26 84 04 93 FF 81 6D 00 00 00 2F 00 0B 4F 25",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.hot_water,
                },
                "dib": [
                    {
                        "field": DIF(0x84),
                        "encoding": DataFieldEnum.int32,
                    },
                    {
                        "field": DIFE(0x04),
                        "encoding": DataFieldEnum.int32,
                    },
                ],
                "vib": [
                    {
                        "field": VIF(0x93),
                        "unit_multiplier": None
                    },
                    {
                        "field": VIFE(0xFF),
                    },
                    {
                        "field": VIFE(0x81),
                    },
                    {
                        "field": VIFE(0x6D),
                    },
                ],
                "data": [
                    0x00, 0x00, 0x00, 0x2F,
                    0x00, 0x0B, 0x4F, 0x25,
                ]
            },
            nullcontext(),
        ),
        (
            "24 84 02 AD FF 80 6C 00 00 17 F4 41 25",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.heat,
                },
                "dib": [
                    {
                        "field": DIF(0x84),
                        "encoding": DataFieldEnum.int32,
                    },
                    {
                        "field": DIFE(0x02),
                        "encoding": DataFieldEnum.int16,
                    },
                ],
                "vib": [
                    {
                        "field": VIF(0xAD),
                        "unit_multiplier": None
                    },
                    {
                        "field": VIFE(0xFF),
                    },
                    {
                        "field": VIFE(0x80),
                    },
                    {
                        "field": VIFE(0x6C),
                    },
                ],
                "data": [
                    0x00, 0x00, 0x17, 0xF4,
                    0x41, 0x25,
                ]
            },
            nullcontext(),
        ),
        (
            "24 84 84 84 82 02 AC FF 80 ED DD 5D 00 00 0C 72 1E 0F 9D 22 07 6D 07 12",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.heat,
                },
                "dib": [
                    {
                        "field": DIF(0x84),
                        "encoding": DataFieldEnum.int32,
                    },
                    {
                        "field": DIFE(0x84),
                        "encoding": DataFieldEnum.int32,
                    },
                    {
                        "field": DIFE(0x84),
                        "encoding": DataFieldEnum.int32,
                    },
                    {
                        "field": DIFE(0x82),
                        "encoding": DataFieldEnum.int16,
                    },
                    {
                        "field": DIFE(0x02),
                        "encoding": DataFieldEnum.int16,
                    },
                ],
                "vib": [
                    {
                        "field": VIF(0xAC),
                        "unit_multiplier": None
                    },
                    {
                        "field": VIFE(0xFF),
                    },
                    {
                        "field": VIFE(0x80),
                    },
                    {
                        "field": VIFE(0xED),
                    },
                    {
                        "field": VIFE(0xDD),
                    },
                    {
                        "field": VIFE(0x5D),
                    },
                ],
                "data": [
                    0x00, 0x00, 0x0C, 0x72,
                    0x1E, 0x0F, 0x9D, 0x22,
                    0x07, 0x6D,
                    0x07, 0x12,
                ]
            },
            nullcontext(),
        ),
        (
            "22 82 82 82 82 82 82 82 82 82 82 82 82 82 81 04 FF A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AC AD AE B0 6D 59 A8 59 EE 59 89 00 00 00 00 00 00 13 88 00 00 00 00 00 00 9B 8E 2E 6B 5D A0 01 1A 0C 10 3A",
            None,
            pytest.raises(MBusError),
        )
    ],
)
def test_c_get_mbus_metering(
    hex: str, answer: None | dict[str, Any], expectation: AbstractContextManager
):
    with expectation:
        assert c_get_mbus_metering(hex) == answer
