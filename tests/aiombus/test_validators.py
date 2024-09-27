from contextlib import nullcontext as does_not_raise
from typing import ContextManager

import pytest

from aiombus.exceptions import MBusValidationError
from aiombus.validators import validate_byte


@pytest.mark.parametrize(
    ("nbr", "expectation"),
    [
        (-129, pytest.raises(MBusValidationError)),
        (-1, pytest.raises(MBusValidationError)),
        (0, does_not_raise()),
        (255, does_not_raise()),
        (256, pytest.raises(MBusValidationError)),
    ],
)
def test_byte_size_validator(nbr: int, expectation: ContextManager):
    with expectation:
        validate_byte(nbr=nbr)
