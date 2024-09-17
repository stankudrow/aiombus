"""The Field's module.

The Fields are part of Telegram Frames.
"""

from aiombus.validators import validate_byte

AF_UNCONFIGURED_SLAVE_BYTE = 0x00
AF_SLAVE_MIN_RANGE_VALUE_BYTE = 0x01
AF_SLAVE_MAX_RANGE_VALUE_BYTE = 0xFA

AF_BROADCAST_ALL_SLAVES_REPLY_BYTE = 0xFE
AF_BROADCAST_NO_SLAVE_REPLIES_BYTE = 0xFF

AF_NETWORK_LAYER_BYTE = 0xFD


class AddressField:
    """The Address (A) Field class.

    The address field serves to address the recipient in the calling direction,
    and to identify the sender of information in the receiving direction.

    The size of this field is one Byte, and can therefore take values from 0 to 255.
    The addresses 1 to 250 can be allocated to the individual slaves, up to a maximum of 250.
    Unconfigured slaves are given the address 0 at manufacture,
    and as a rule are allocated one of these addresses when connected to the M-Bus.

    The addresses 254 (FEh) and 255 (FFh) are used to transmit
    information to all participants (Broadcast). With address 255 none of the slaves reply,
    and with address 254 all slaves reply with their own addresses.
    The latter case naturally results in collisions when two or more slaves are connected,
    and should only be used for test purposes.

    The address 253 (FDh) indicates that the adressing has been performed in the Network Layer
    instead of Data Link Layer.

    The remaining addresses 251 and 252 have been kept for future applications.
    """

    def __init__(self, byte: int):
        self._a_field = validate_byte(byte)

    def is_unconfigured_slave(self) -> bool:
        return self._a_field == AF_UNCONFIGURED_SLAVE_BYTE

    def is_configured_slave(self) -> bool:
        return (
            AF_SLAVE_MIN_RANGE_VALUE_BYTE
            <= self._a_field
            <= AF_SLAVE_MAX_RANGE_VALUE_BYTE
        )

    def is_slave(self) -> bool:
        return (
            AF_UNCONFIGURED_SLAVE_BYTE <= self._a_field <= AF_SLAVE_MAX_RANGE_VALUE_BYTE
        )

    def is_broadcast_all_reply(self) -> bool:
        return self._a_field == AF_BROADCAST_ALL_SLAVES_REPLY_BYTE

    def is_broadcast_no_replies(self) -> bool:
        return self._a_field == AF_BROADCAST_NO_SLAVE_REPLIES_BYTE

    def is_broadcast(self) -> bool:
        return self.is_broadcast_all_reply() or self.is_broadcast_no_replies()

    def is_network_layer(self) -> bool:
        return self._a_field == AF_NETWORK_LAYER_BYTE


class _ControlFieldCallingDirection:
    """The Control (C) Field Calling Direction class."""

    def __init__(self, byte: int):
        validate_byte(byte)
        self._fields = byte & 0x0F
        self._fcv = byte & 0x10
        self._fcb = byte & 0x20


class ControlField:
    """"""

    def __init__(self, byte: int):
        self._direction = self._parse_direction(byte)

    def _parse_direction(self, byte: int) -> None:
        pass


class ControlInformationField:
    """The Control Information (CI) Field class.

    It was included in the telegram format used, in order to distinguish
    between the formats of the long and the control frames.
    The control information allows the implementation of a variety of actions
    in the master or the slaves.
    """
