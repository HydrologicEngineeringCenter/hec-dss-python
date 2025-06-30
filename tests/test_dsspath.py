"""Pytest module."""

import unittest

from hecdss import DssPath
from hecdss.cwms_utility import CwmsUtility
from hecdss.dss_type import DssType


class TestDssPath(unittest.TestCase):

    def setUp(self) -> None:
        # the example data includes: [ tsid, dsspath, dss_type, cwms_duration ]
        self.example_data = [
            ["NORK-Norton-Prairie_Dog.Stage.Inst.15Minutes.0.nwklrgs-raw",
             "//NORK-Norton-Prairie_Dog/Stage/01Apr2024/15Minute/nwklrgs-raw/", DssType.INST_VAL, "0"],
            ["FTPK.%-DissolvedOxygen.Inst.1Hour.0.Best-MRBWM",
             "//FTPK/%-DissolvedOxygen/01Apr2024/1Hour/Best-MRBWM/", DssType.INST_VAL, "0"],
            ["FTPK.Code-Outages.Const.~1Day.0.Rev-MRBWM-Manual",
             "//FTPK/Code-Outages/01Jan2024/~1Day/Rev-MRBWM-Manual/", DssType.CONST, "0"],
            ["03045.Code.Inst.1Hour.0.Test",
             "//03045/Code/01Jun2021/1Hour/Test/", DssType.INST_VAL, "0"],
            ["NOMS2-D40in.%-SoilMoisture.Inst.1Hour.0.Raw-MADIS",
             "//NOMS2-D40in/%-SoilMoisture/01Nov2022/1Hour/Raw-MADIS/", DssType.INST_VAL, "0"],
            ["WILN.Elev.Inst.6Hours.0.Fcst-NWK-ResSim",
             "//WILN/Elev/01Aug2023/6Hour/Fcst-NWK-ResSim/", DssType.INST_VAL, "0"],
            ["NOMS2.%-RelativeHumidity.Ave.5Minutes.5Minutes.Raw-MADIS",
             "//NOMS2/%-RelativeHumidity/15Nov2022/5Minute/Raw-MADIS/", DssType.PER_AVER, "5Minutes"],
            ["BDMW4.Precip.Total.5Minutes.5Minutes.Raw-MADIS",
             "//BDMW4/Precip/05May2024 - 15May2024/5Minute/Raw-MADIS/", DssType.PER_CUM, "5Minutes"],
            ["BOSD-Brookings-Big_Sioux.Precip.Inst.15Minutes.0.nwklrgs-raw",
             "//BOSD-Brookings-Big_Sioux/Precip/06May2024 - 15May2024/15Minute/nwklrgs-raw/", DssType.INST_CUM, "0"]

        ]

    def test_convert_dsspath_to_tsid(self):
        for row in self.example_data:
            pathname = row[1]
            dss_type = row[2]
            duration = row[3]
            tsid = CwmsUtility.pathname_to_cwms_tsid(pathname, dss_type, duration)
            if tsid != row[0]:
                print(f"error converting to tsid. expected '{row[0]}', actual: '{tsid}'")
                assert tsid == row[0]

    def test_convert_cwms_tsid_to_dss_path(self):
        for row in self.example_data:
            tsid = row[0]
            expected_pathname = row[1]
            pathname = CwmsUtility.cwms_ts_id_to_dss_path(tsid)
            expected_pathname_without_date = DssPath(str(expected_pathname)).path_without_date()
            if expected_pathname_without_date != pathname:
                print(f"error converting to path. expected '{expected_pathname_without_date}', actual: '{pathname}'")
                assert expected_pathname_without_date == pathname

    def test_strict_cwms_id(self):
        dss_path = self.example_data[0][1]
        tsid = CwmsUtility.pathname_to_cwms_tsid(dss_path, DssType.INST_VAL, "0")
        assert tsid == self.example_data[0][0]
        strict_expected = "Nork-Norton-Prairie_Dog.Stage.Inst.15Minutes.0.Nwklrgs-Raw"
        tsid = CwmsUtility.pathname_to_cwms_tsid(dss_path, DssType.INST_VAL, "0", True)
        assert tsid == strict_expected

# t = TestDssPath()
# t.test_convert_cwms_tsid_to_dss_path()
# t.test_convert_dsspath_to_tsid()
