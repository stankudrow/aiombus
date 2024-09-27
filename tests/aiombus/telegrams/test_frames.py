from contextlib import nullcontext as does_not_raise
from typing import ContextManager, Iterable

import pytest

from aiombus.telegrams.frames import (
    ACK_BYTE,
    SHORT_FRAME_START_BYTE,
    FRAME_STOP_BYTE,
    SingleFrame,
    ShortFrame,
)
from aiombus.exceptions import MBusDecodeError


@pytest.mark.parametrize(
    ("byte", "expectation"),
    [
        (ACK_BYTE, does_not_raise()),
        (ACK_BYTE - 1, pytest.raises(MBusDecodeError)),
    ],
)
def test_single_frame_init(byte: int, expectation: ContextManager):
    with expectation:
        SingleFrame.from_byte(byte)


@pytest.mark.parametrize(
    ("data", "expectation"),
    [
        ([1], pytest.raises(MBusDecodeError)),
        (
            [SHORT_FRAME_START_BYTE, 2, 3, 4, FRAME_STOP_BYTE],
            does_not_raise(),
        ),
        (
            [SHORT_FRAME_START_BYTE, 2, 3, 4, 6, FRAME_STOP_BYTE],
            pytest.raises(MBusDecodeError),
        ),
        (
            [SHORT_FRAME_START_BYTE, 2, 3, FRAME_STOP_BYTE],
            pytest.raises(MBusDecodeError),
        ),
    ],
)
def test_short_frame_init(data: Iterable, expectation: ContextManager):
    with expectation:
        ShortFrame(data)
