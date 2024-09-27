from contextlib import nullcontext as does_not_raise
from typing import ContextManager, Iterable

import pytest

from aiombus.telegrams.blocks import DataInformationBlock as DIB
from aiombus.telegrams.fields import (
    DataInformationField as DIF,
    DataInformationFieldExtension as DIFE,
)
from aiombus.exceptions import MBusDecodeError, MBusValidationError


@pytest.mark.parametrize(
    ("ints", "expectation"),
    [
        ([-1], pytest.raises(ValueError)),
        ([256], pytest.raises(ValueError)),
        ([0b1000_1111, 0b0111_0000], does_not_raise()),
    ],
)
def test_dib_init_from_integers(ints: list[int], expectation: ContextManager):
    with expectation:
        dib = DIB.from_integers(ints)

        assert dib.to_bytearray() == bytearray(ints)


@pytest.mark.parametrize(
    ("hexstr", "expectation"),
    [
        ("123", pytest.raises(ValueError)),
        ("8f 70", does_not_raise()),
    ],
)
def test_dib_init_from_hexstring(hexstr: str, expectation: ContextManager):
    with expectation:
        dib = DIB.from_hexstring(hexstr)

        assert dib.to_bytearray() == bytearray.fromhex(hexstr)


@pytest.mark.parametrize(
    ("ints", "expectation"),
    [
        ([-1], pytest.raises(MBusValidationError)),
        ([256], pytest.raises(MBusValidationError)),
        ([0b0111_1111], does_not_raise()),
        ([0b1000_1111, 0b0111_0000], does_not_raise()),
        (
            [
                0b1000_1111,
                0b1000_0000,
                0b1000_0001,
                0b1000_0010,
                0b1000_0011,
                0b1000_0100,
                0b1000_0101,
                0b1000_0110,
                0b1000_0111,
                0b1000_1000,
                0b0000_1001,
            ],
            does_not_raise(),
        ),
        (
            [
                0b1000_1111,
                0b1000_0000,
                0b1000_0001,
                0b1000_0010,
                0b1000_0011,
                0b1000_0100,
                0b1000_0101,
                0b1000_0110,
                0b1000_0111,
                0b1000_1000,
                0b1000_1001,
            ],
            pytest.raises(MBusDecodeError),
        ),
    ],
)
def test_dib_init(ints: list[int], expectation: ContextManager):
    with expectation:
        dib = DIB(ints)

        assert dib.to_bytearray() == bytearray(ints)


@pytest.mark.parametrize(
    ("it",),
    [([0b1000_1111, 0b0111_0000],), ([0b1000_1111, 0b0111_0000],)],
)
def test_dib_repr_and_str(it: Iterable):
    dib = DIB(it)

    bts = bytes(it)
    repstr = f"DataInformationBlock(bytes={bts})"

    difes = it[1:] if len(it) > 1 else []
    strstr = str([DIF(it[0])] + [DIFE(bt) for bt in difes])

    assert repr(dib) == repstr
    assert str(dib) == strstr


def test_for_loop_over_dib():
    it = [0b1000_0000, 0b1000_0001, 0b0111_0010]
    dib = DIB(it)

    for df, byte in zip(dib, it):
        assert df.byte == byte