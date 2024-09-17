from contextlib import nullcontext as does_not_raise
from typing import ContextManager

import pytest

from aiombus.blocks import (
    DataInformationField as DIF,
    DataInformationFieldExtension as DIFE,
)
from aiombus.exceptions import MBusValidationError


### the DIF section


@pytest.mark.parametrize(
    ("byte", "check_byte", "expectation"),
    [
        (-1, True, pytest.raises(MBusValidationError)),
        (-1, False, does_not_raise()),
        (0, True, does_not_raise()),
        (255, True, does_not_raise()),
        (256, True, pytest.raises(MBusValidationError)),
    ],
)
def test_dif_init(byte: int, check_byte: bool, expectation: ContextManager):
    with expectation:
        DIF(byte=byte, check_byte=check_byte)


@pytest.mark.parametrize(
    ("byte", "ext_bit"),
    [
        (0b1111_1111, 1),
        (0b0111_1111, 0),
    ],
)
def test_dif_extension_bit(byte: int, ext_bit: int):
    dif = DIF(byte=byte)

    assert dif.extension_bit == ext_bit


@pytest.mark.parametrize(
    ("byte", "sn_lsb"),
    [
        (0b1111_1111, 1),
        (0b1011_1111, 0),
    ],
)
def test_dif_storage_number_lsb(byte: int, sn_lsb: int):
    dif = DIF(byte=byte)

    assert dif.storage_number_lsb == sn_lsb


@pytest.mark.parametrize(
    ("byte", "function_field"),
    [
        (0b1100_1111, 0b00),
        (0b1101_1111, 0b01),
        (0b1010_1111, 0b10),
        (0b1011_1111, 0b11),
    ],
)
def test_dif_function_field(byte: int, function_field: int):
    dif = DIF(byte=byte)

    assert dif.function_field == function_field


@pytest.mark.parametrize(
    ("byte", "data_field"),
    [
        (0b1110_0000, 0b0000),
        (0b1110_1010, 0b1010),
        (0b1110_0101, 0b0101),
        (0b1100_1111, 0b1111),
    ],
)
def test_dif_data_field(byte: int, data_field: int):
    dif = DIF(byte=byte)

    assert dif.data_field == data_field


### the DIFE section


@pytest.mark.parametrize(
    ("byte", "check_byte", "expectation"),
    [
        (-1, True, pytest.raises(MBusValidationError)),
        (-1, False, does_not_raise()),
        (0, True, does_not_raise()),
        (255, True, does_not_raise()),
        (256, True, pytest.raises(MBusValidationError)),
    ],
)
def test_dife_init(byte: int, check_byte: bool, expectation: ContextManager):
    with expectation:
        DIFE(byte=byte, check_byte=check_byte)


@pytest.mark.parametrize(
    ("byte", "ext_bit"),
    [
        (0b1111_1111, 1),
        (0b0111_1111, 0),
    ],
)
def test_dife_extension_bit(byte: int, ext_bit: int):
    dif = DIFE(byte=byte)

    assert dif.extension_bit == ext_bit


@pytest.mark.parametrize(
    ("byte", "device_unit"),
    [
        (0b1111_1111, 1),
        (0b1011_1111, 0),
    ],
)
def test_dife_storage_number_lsb(byte: int, device_unit: int):
    dif = DIFE(byte=byte)

    assert dif.device_unit == device_unit


@pytest.mark.parametrize(
    ("byte", "tariff"),
    [
        (0b1100_1111, 0b00),
        (0b1101_1111, 0b01),
        (0b1010_1111, 0b10),
        (0b1011_1111, 0b11),
    ],
)
def test_dife_tariff(byte: int, tariff: int):
    dif = DIFE(byte=byte)

    assert dif.tariff == tariff


@pytest.mark.parametrize(
    ("byte", "storage_number"),
    [
        (0b1110_0000, 0b0000),
        (0b1110_1010, 0b1010),
        (0b1110_0101, 0b0101),
        (0b1100_1111, 0b1111),
    ],
)
def test_dife_storage_number(byte: int, storage_number: int):
    dif = DIFE(byte=byte)

    assert dif.storage_number == storage_number
