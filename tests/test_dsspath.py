"""Pytest module."""

import unittest
import os
import sys

from hecdss.cwms_utility import CwmsUtility
from hecdss.dss_type import DssType

sys.path.append(r'src')
sys.path.append(os.path.dirname(__file__))
from hecdss import DssPath


class TestDssPath(unittest.TestCase):

    def test_convert_to_tsid(self):
        dp = DssPath("/TULA//Flow/17Aug2024 - 22Aug2024/1Hour/Ccp-Rev/")
        tsid = dp.to_cwms_tsid(DssType.PER_AVER)
        # [Location]-[sub-location].[Parameter]-[sub-parameter].[Type].[Interval].[Duration].[Version]
        # assert (tsid == "Tula.Flow.PER-AVER")

    def test_convert_to_dsspath(self):
        examples = [
            ["NORK-Norton-Prairie_Dog.Stage.Inst.15Minutes.0.nwklrgs-raw",
             "//NORK-Norton-Prairie_Dog/Stage/01Apr2024/15Minute/nwklrgs-raw/", DssType.INST_VAL],
            ["FTPK.%-DissolvedOxygen.Inst.1Hour.0.Best-MRBWM",
             "//FTPK/%-DissolvedOxygen/01Apr2024/1Hour/Best-MRBWM/", DssType.INST_VAL],
            ["FTPK.Code-Outages.Const.~1Day.0.Rev-MRBWM-Manual",
             "//FTPK/Code-Outages/01Jan2024/~1Day/Rev-MRBWM-Manual/", DssType.INST_VAL],
            ["03045.Code.Inst.1Hour.0.Test",
             "//03045/Code/01Jun2021/1Hour/Test/", DssType.INST_VAL],
            ["NOMS2-D40in.%-SoilMoisture.Inst.1Hour.0.Raw-MADIS",
             "//NOMS2-D40in/%-SoilMoisture/01Nov2022/1Hour/Raw-MADIS/",DssType.INST_VAL],
            ["WILN.Elev.Inst.6Hours.0.Fcst-NWK-ResSim",
             "//WILN/Elev/01Aug2023/6Hour/Fcst-NWK-ResSim/",DssType.INST_VAL],
            ["NOMS2.%-RelativeHumidity.Ave.5Minutes.5Minutes.Raw-MADIS",
             "//NOMS2/%-RelativeHumidity/15Nov2022/5Minute/Raw-MADIS/", DssType.PER_AVER],
            ["BDMW4.Precip.Total.5Minutes.5Minutes.Raw-MADIS",
             "//BDMW4/Precip/05May2024 - 15May2024/5Minute/Raw-MADIS/", DssType.PER_CUM],
            ["BOSD-Brookings-Big_Sioux.Precip.Inst.15Minutes.0.nwklrgs-raw",
             "//BOSD-Brookings-Big_Sioux/Precip/06May2024 - 15May2024/15Minute/nwklrgs-raw/", DssType.INST_CUM]

        ]
        # test converting dss to cwms-tsid
        for row in examples:
            pathname = row[1]
            dss_type = row[2]
            tsid = CwmsUtility.pathname_to_cwms_tsid(pathname, dss_type)
            if tsid != row[0]:
                print(f"error converting to tsid. expected '{row[0]}', actual: '{tsid}'")

        # test converting cwms-tsid to dss path
        for row in examples:
            tsid = row[0]
            expected_pathname = row[1]
            pathname = CwmsUtility.cwms_ts_id_to_pathname(tsid)
            if expected_pathname != pathname:
                print(f"error converting to path. expected '{expected_pathname}', actual: '{pathname}'")



