class MBusError(Exception):
    """Meter-Bus Base Error."""


class MBusDataError(MBusError):
    """Meter-Bus Data Error."""


class MBusDecodeError(MBusDataError):
    """Meter-Bus (Data) Decode Error."""


class MBusValidationError(MBusDataError):
    """Meter-Bus (Data) Validation Error."""
