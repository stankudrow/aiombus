"""The module with validators."""

from aiombus.exceptions import MBusValidationError


def validate_byte(nbr: int) -> int:
    """Validate the `nbr` to be a valid `bytes` value.

    In Python, bytest must be in range(0, 256).
    This is the range for 8 bit unsigned integer.

    Raises
    ------
    MbusDataError: the value is out of [0, 255] segment.

    Returns
    -------
    int - the validated byte
    """

    try:
        bytes([nbr])
    except ValueError as e:
        raise MBusValidationError from e

    return nbr
