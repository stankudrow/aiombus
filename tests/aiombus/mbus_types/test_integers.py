from collections.abc import Iterable

import pytest

from aiombus.types import (
    parse_binary_integer,
    parse_unsigned_integer,
    parse_boolean,
)


@pytest.mark.parametrize(
    ("it", "answer"),
    [
        ([0b0000_0000], 0),
        ([0b1000_0000], -128),
        ([0b1000_0001], -127),
        ([0b0111_1111], 127),
        ([0b1111_1111], -1),
        (
            # 0b0000_0001 <+> 0b1111_1111
            # 256 + 255 = 511
            [0b1111_1111, 0b0000_0001],
            511,
        ),
        (
            # 0b1000_0001 <+> 0b1111_1111
            # 0b0111_1110 <+> 0b0000_0000
            # -(0b0111_1110_0000_0000 + 1)
            # -(32356 + 1) -> -32257
            [0b1111_1111, 0b1000_0001],
            -32257,
        ),
    ],
)
def test_type_b_signed_integer_parsing(it: Iterable, answer: int):
    assert parse_binary_integer(bytes(it)) == answer


@pytest.mark.parametrize(
    ("it", "answer"),
    [
        ([0b0000_0000], 0),
        ([0b1000_0000], 128),
        ([0b1111_1111], 255),
        (
            # 0b0000_0001 <+> 0b1111_1111
            # 256 + 255 = 511
            [0b0000_0001, 0b1111_1111],
            511,
        ),
    ],
)
def test_type_c_unsigned_integer_parsing(it: Iterable, answer: int):
    assert parse_unsigned_integer(bytes(it)) == answer


@pytest.mark.parametrize(
    ("it", "answer"),
    [
        ([0b0000_0000], False),
        ([0b0000_0001], True),
        ([0b0000_0000, 0b0000_0001], True),
        ([0b0000_0001, 0b0000_0000], True),
        ([0b0000_0000, 0b0000_0000], False),
    ],
)
def test_type_d_boolean_parsing(it: Iterable, answer: int):
    assert parse_boolean(bytes(it)) == answer
