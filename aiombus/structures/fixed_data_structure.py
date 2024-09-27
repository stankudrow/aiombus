from enum import IntEnum


class MeasuredMedium(IntEnum):
    """Measured Medium Fixed Structure

    1. Record Medium/Unit is always least significant byte first.
    2. H.C.A. = Heat Cost Allocator.
    3. Media from "Gas Mode2" to "H.C.A. Mode2" are defined in EN1434-3
       for some existing meters with CI-Field 73h (intentionally mode1),
       which transmit the multibyte records with high byte first
       in contrast to the CI-Field. The master must know that
       these media codes mean mode 2 or high byte first.
       Further use of these codes for "pseudo media"
       is NOT ALLOWED for new developments.
    """

    other = 0x00  # 0000
    oil = 0x01  # 0001
    electricity = 0x02  # 0010
    gas = 0x03  # 0011
    heat = 0x04  # 0100
    steam = 0x05  # 0101
    hot_water = 0x06  # 0110
    water = 0x07  # 0111
    hca = 0x08  # 1000
    reserved1 = 0x09  # 1001
    gas_mode_2 = 0x0A  # 1010
    heat_mode_2 = 0x0B  # 1011
    hot_water_mode_2 = 0x0C  # 1100
    water_mode_2 = 0x0D  # 1101
    hca_mode_2 = 0x0E  # 1110
    reserved2 = 0x0F  # 1111


class PhysicalUnits(IntEnum):
    """The table (enum) of physical units."""

    hms = 0x00  # hours, minutes, seconds
    dmy = 0x01  # days, months, years

    Wh = 0x02  # Watt-hour
    Wh_times_10 = 0x03  # Watt-hour * 10
    Wh_times_100 = 0x04  # Watt-hour * 100

    kWh = 0x05  # kilo Watt-hour
    kWh_times_10 = 0x06  # kilo Watt-hour * 10
    kWh_times_100 = 0x07  # kilo Watt-hour * 100

    MWh = 0x08  # Mega Watt-hour
    MWh_times_10 = 0x09  # Mega Watt-hour * 10
    MWh_times_100 = 0x0A  # Mega Watt-hour * 100

    kJ = 0x0B  # kilo Joule
    kJ_times_10 = 0x0C  # kilo Joule * 10
    kJ_times_100 = 0x0D  # kilo Joule * 100

    MJ = 0x0E  # Mega Joule
    MJ_times_10 = 0x0F  # Mega Joule * 10
    MJ_times_100 = 0x10  # Mega Joule * 100

    GJ = 0x11  # Giga Joule
    GJ_times_10 = 0x12  # Giga Joule * 10
    GJ_times_100 = 0x13  # Giga Joule * 100

    W = 0x14  # Watt
    W_times_10 = 0x15  # Watt * 10
    W_times_100 = 0x16  # Watt * 100

    kW = 0x17  # kilo Watt
    kW_times_10 = 0x18  # kilo Watt * 10
    kW_times100 = 0x19  # kilo Watt * 100

    MW = 0x1A  # Mega Watt
    MW_times_10 = 0x1B  # Mega Watt * 10
    MW_times_100 = 0x1C  # Mega Watt * 100

    kJ_per_h = 0x1D  # kilo Joule per hour
    kJ_per_h_times_10 = 0x1E  # kilo Joule per hour
    kJ_per_h_times_100 = 0x1F  # kilo Joule per hour

    MJ_per_h = 0x20  # Mega Joule per hour
    MJ_per_h_times_10 = 0x21  # Mega Joule per hour
    MJ_per_h_times_100 = 0x22  # Mega Joule per hour
    GJ_per_h = 0x23  # Giga Joule per hour

    GJ_per_h_times_10 = 0x24  # Giga Joule per hour
    GJ_per_h_times_100 = 0x25  # Giga Joule per hour

    ml = 0x26  # milli liter
    ml_times_10 = 0x27  # milli liter
    ml_times_100 = 0x28  # milli liter

    l = 0x29  # liter
    l_times_10 = 0x2A  # liter * 10
    l_times_100 = 0x2B  # liter * 100

    m_cubic = 0x2C  # meter cubic
    m_cubic_times_10 = 0x2D  # meter cubic * 10
    m_cubic_times_100 = 0x2E  # meter cubic * 100

    ml_per_h = 0x2F  # milli liter per hour
    ml_per_h_times_10 = 0x30  # milli liter per hour * 10
    ml_per_h_times_100 = 0x31  # milli liter per hour * 100

    l_per_h = 0x32  # liter per hour
    l_per_h_times_10 = 0x33  # liter per hour * 10
    l_per_h_times_100 = 0x34  # liter per hour * 100

    m_cubic_per_h = 0x35  # meter cubic per hour
    m_cubic_per_h_times_10 = 0x36  # meter cubic per hour * 10
    m_cubic_per_h_times_100 = 0x37  # meter cubic per hour * 100

    celsius_times_10_to_minus3 = 0x38  # Celsius * 10^(-3)

    units_for_hca = 0x39  # H.C.A. = Heat Cost Allocator

    reserved1 = 0x3A
    reserved2 = 0x3B
    reserved3 = 0x3C
    reserved4 = 0x3D

    same_but_historic = 0x3E

    without_units = 0x3F  # dimensionless
