"""The module with validators."""

from aiombus.exceptions import MBusValidationError


def validate_byte(nbr: int) -> int:
    """Validate an integer number to be a valid `bytes` type.

    In Python, a byte must be in range(0, 256).
    This is the range for 8-bit unsigned integer.

    Raises
    ------
    MbusValidationError: the value is out of the [0, 255] segment.

    Returns
    -------
    int - the validated byte
    """

    try:
        bytes([nbr])
    except ValueError as e:
        raise MBusValidationError from e

    return nbr
