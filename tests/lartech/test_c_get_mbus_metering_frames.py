from contextlib import AbstractContextManager, nullcontext
from typing import Any

import pytest

from aiombus.exceptions import MBusError
from aiombus.structures.fixed import MeasuredMedium
from aiombus.telegrams.codes.value_info import (
    EnergyWattHourVIFCode,
    PowerWattVIFCode,
    VolumeMeterCubeVIFCode,
    get_vif_code,
)
from aiombus.telegrams.fields.data_info import (
    DataFieldCode as DataFieldEnum,
    DataInformationField as DIF,
    DataInformationFieldExtension as DIFE,
)
from aiombus.telegrams.blocks.data_info import DataInformationBlock as DIB
from aiombus.telegrams.blocks.value_info import (
    ValueInformationBlock as VIB,
)
from aiombus.telegrams.fields.value_info import (
    ValueInformationField as VIF,
    ValueInformationFieldExtension as VIFE,
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

    vif = vib.vif
    vif_code = get_vif_code(vif)
    unit_multiplier = vif_code.multiplier if vif_code else vif_code
    res["vib"] = [
        {
            "field": vib.vif,
            "unit_kind": type(vif_code),
            "unit_multiplier": unit_multiplier,
        }
    ]
    for vife in vib.vifes:
        record = {"field": vife}
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
            "22 04 A9 FF 81 80 6D 1E 0A 6A 28",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.electricity,
                },
                "dib": [
                    {
                        "field": DIF(0x04),
                        "encoding": DataFieldEnum.int32,
                    },
                ],
                "vib": [
                    {
                        "field": VIF(0xA9),
                        "unit_kind": PowerWattVIFCode,
                        "unit_multiplier": 0.01,
                    },
                    {
                        "field": VIFE(0xFF),
                    },
                    {
                        "field": VIFE(0x81),
                    },
                    {
                        "field": VIFE(0x80),
                    },
                    {
                        "field": VIFE(0x6D),
                    },
                ],
                "data": [
                    0x1E,
                    0x0A,
                    0x6A,
                    0x28,
                ],
            },
            nullcontext(),
        ),
        (
            "22 02 83 FF 81 81 6C 40 25",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.electricity,
                },
                "dib": [
                    {
                        "field": DIF(0x02),
                        "encoding": DataFieldEnum.int16,
                    },
                ],
                "vib": [
                    {
                        "field": VIF(0x83),
                        "unit_kind": EnergyWattHourVIFCode,
                        "unit_multiplier": 1,
                    },
                    {
                        "field": VIFE(0xFF),
                    },
                    {
                        "field": VIFE(0x81),
                    },
                    {
                        "field": VIFE(0x81),
                    },
                    {
                        "field": VIFE(0x6C),
                    },
                ],
                "data": [
                    0x40,
                    0x25,
                ],
            },
            nullcontext(),
        ),
        (
            "27 02 93 FF 80 6C 6A 28",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.water,
                },
                "dib": [
                    {
                        "field": DIF(0x02),
                        "encoding": DataFieldEnum.int16,
                    },
                ],
                "vib": [
                    {
                        "field": VIF(0x93),
                        "unit_kind": VolumeMeterCubeVIFCode,
                        "unit_multiplier": 0.001,
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
                    0x6A,
                    0x28,
                ],
            },
            nullcontext(),
        ),
        (
            "27 02 93 FF 80 6C 40 25",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.water,
                },
                "dib": [
                    {
                        "field": DIF(0x02),
                        "encoding": DataFieldEnum.int16,
                    },
                ],
                "vib": [
                    {
                        "field": VIF(0x93),
                        "unit_kind": VolumeMeterCubeVIFCode,
                        "unit_multiplier": 0.001,
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
                    0x40,
                    0x25,
                ],
            },
            nullcontext(),
        ),
        (
            "24 02 AD FF 80 6C 40 25",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.heat,
                },
                "dib": [
                    {
                        "field": DIF(0x02),
                        "encoding": DataFieldEnum.int16,
                    },
                ],
                "vib": [
                    {
                        "field": VIF(0xAD),
                        "unit_kind": PowerWattVIFCode,
                        "unit_multiplier": 100,
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
                    0x40,
                    0x25,
                ],
            },
            nullcontext(),
        ),
        (
            "22 84 04 A9 FF 81 80 6D 00 00 1F 40 1E 0A 6A 28",
            {
                "metering": {
                    "type": "simple",
                    "medium": MeasuredMedium.electricity,
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
                        "field": VIF(0xA9),
                        "unit_kind": PowerWattVIFCode,
                        "unit_multiplier": 0.01,
                    },
                    {
                        "field": VIFE(0xFF),
                    },
                    {
                        "field": VIFE(0x81),
                    },
                    {
                        "field": VIFE(0x80),
                    },
                    {
                        "field": VIFE(0x6D),
                    },
                ],
                "data": [
                    0x00,
                    0x00,
                    0x1F,
                    0x40,
                    0x1E,
                    0x0A,
                    0x6A,
                    0x28,
                ],
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
                        "unit_kind": PowerWattVIFCode,
                        "unit_multiplier": 10,
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
                    0x00,
                    0x00,
                    0x0C,
                    0x72,
                    0x1E,
                    0x0F,
                    0x9D,
                    0x22,
                    0x07,
                    0x6D,
                    0x07,
                    0x12,
                ],
            },
            nullcontext(),
        ),
        (
            "22 82 82 82 82 82 82 82 82 82 82 82 82 82 81 04 FF A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AC AD AE B0 6D 59 A8 59 EE 59 89 00 00 00 00 00 00 13 88 00 00 00 00 00 00 9B 8E 2E 6B 5D A0 01 1A 0C 10 3A",
            None,
            pytest.raises(MBusError),
        ),
    ],
)
def test_c_get_mbus_metering(
    hex: str, answer: None | dict[str, Any], expectation: AbstractContextManager
):
    with expectation:
        assert c_get_mbus_metering(hex) == answer
