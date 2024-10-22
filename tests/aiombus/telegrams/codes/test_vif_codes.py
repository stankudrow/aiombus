# import pytest

# from aiombus.telegrams.codes.value_info import (
#     ValueInformationFieldCode as VIFC,
#     EnergyWattHourVIFCode,
#     EnergyJouleVIFCode,
#     get_vifcode_type,
# )
# from aiombus.telegrams.fields.value_info import (
#     ValueInformationField as VIF
# )


# @pytest.mark.parametrize(
#     ("vif", "code_type"),
#     [
#         (
#             VIF(0b0000_0000),
#             EnergyWattHourVIFCode,
#         ),
#         (
#             VIF(0b1000_0111),
#             EnergyWattHourVIFCode,
#         ),
#         (
#             VIF(0b0000_0000),
#             EnergyWattHourVIFCode,
#         ),
#         (
#             VIF(0b1000_0111),
#             EnergyWattHourVIFCode,
#         ),
#     ]
# )
# def test_get_vifcode_energy(vif: VIF, code_type: VIFC):
#     res = get_vifcode_type(vif)
#     assert res is code_type
