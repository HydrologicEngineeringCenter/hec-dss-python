"""Pytest module."""

import unittest
from datetime import datetime, timedelta

import numpy as np
from file_manager import FileManager

from hecdss import HecDss
from hecdss.regular_timeseries import RegularTimeSeries


class TestRegularTimeSeries(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()
    
    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_regular_timeseries_read(self):
        """
        read record from disk
        """
        path = "/regular-time-series-many-points/unknown/flow/01Sep2004/15Minute//"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            rts = dss.get(path)
        assert (553486 == rts.get_length()), f"irts.get_length() should be 553486. is {rts.get_length()}"
        assert (12.300 == rts.values[18]), f"irts.values[18] should be 39000. is {rts.values[18]}"
        assert ("2004-09-30 23:00:00" == str(rts.times[19])), f"irts.times[19] should be '2004-09-30 23:00:00'. is {rts.times[19]}"
        assert ("CFS" == rts.units), f"irts.units should be 'CFS'. is {rts.units}"
        assert ("FLOW" == rts.data_type), f"irts.data_type should be 'FLOW'. is {rts.data_type}"
        assert (900 == rts.interval), f"irts.interval should be 900. is {rts.interval}"

    def test_is_regular_timeseries_type(self):
        """
        Test if dss.get() returns a record of type IrregularTimeSeries
        """
        path = "/regular-time-series-many-points/unknown/flow/01Sep2004/15Minute//"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            rts = dss.get(path, startdatetime=datetime(2004, 9, 1), enddatetime=datetime(2004, 9, 30))
        assert (type(rts) is RegularTimeSeries), f"rts should be type RegularTimeSeries. is {type(rts)}"

    def test_regular_timeseries_create(self):
        """
        create regular timerseries
        """
        path = "//EAU GALLA RIVER/Flow//1Day//"
        rts = RegularTimeSeries.create(range(15), start_date=datetime.today(), path=path)
        self.assertEqual(86400, rts.interval)
        print(rts)


        path = "//EAU GALLA RIVER/Flow////"
        times = [datetime.today()+(i * timedelta(seconds=10)) for i in range(15)]
        rts = RegularTimeSeries.create(range(15), times=times, path=path)
        self.assertEqual("//EAU GALLA RIVER/Flow//10Second//", rts.id)

    def test_regular_timeseries_create_fail(self):
        """
        create regular timerseries
        """
        path = "//EAU GALLA RIVER/Flow//1Day//"
        times = [datetime.today()+(i * timedelta(seconds=10)) for i in range(15)]
        try:
            RegularTimeSeries.create(range(15), times=times, path=path)
        except:
            return
        self.assertTrue(False, "create TimeSeries should fail due to inconsistent interval")

    def test_regular_timeseries_create_store(self):
        """
        create IrregularTimeSeries and store to dss
        """
        path = "/regular-time-series/test/CFS//15Minute/store-test/"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            rts = RegularTimeSeries.create(range(15), start_date=datetime.today(), units="CFS", path=path)
            dss.put(rts)

    def test_regular_timeseries_create_store_read(self):
        """
        Generates a IrregularTimeSeries object then stores data on disk and read result
        """
        path = "/regular-time-series/test/CFS//10Second/store-test/"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            rts = RegularTimeSeries.create(range(15), start_date=datetime.today(), units="CFS", path=path)
            dss.put(rts)

            read_rts = dss.get(path)

        assert (read_rts.times == rts.times), f"saved and read times should be identical saved times are" \
                                                f" \n{rts.times}\n and read times are \n{read_rts.times}"

    def test_regular_timeseries_read_store_read(self):
        """
        Read a IrregularTimeSeries object then stores data on disk and read again
        """
        path = "/regular-time-series-many-points/unknown/flow/01Oct2004/15Minute//"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            rts = dss.get(path, startdatetime=datetime(2004, 10, 1), enddatetime=datetime(2004, 10, 30))

            path_modified = "/regular-time-series-many-points/unknown/flow/01Oct2004/15Minute/test-store/"

            rts.id = path_modified

            dss.put(rts)

            rts_modified = dss.get(path_modified)
        np.set_printoptions(suppress=True)
        assert (rts.get_length() == rts_modified.get_length()), f"irts.get_length() is not equal to irts_modified.get_length()." \
                                                                  f" irts.get_length() is {rts.get_length()}, irts_modified.get_length() is {rts_modified.get_length()}"
        assert (np.array_equal(rts.values, rts_modified.values)), f"irts.values is not equal to irts_modified.values." \
                                                      f" irts.values is {rts.values}, irts_modified.values is {rts_modified.values}"
        assert (np.array_equal(rts.times, rts_modified.times)), f"irts.times is not equal to irts_modified.times." \
                                                    f" irts.times is {rts.times}, irts_modified.times is {rts_modified.times}"
        assert (rts.units == rts_modified.units), f"irts.units is not equal to irts_modified.units." \
                                                    f" irts.units is {rts.units}, irts_modified.units is {rts_modified.units}"
        assert (rts.data_type == rts_modified.data_type), f"irts.data_type is not equal to irts_modified.data_type." \
                                                            f" irts.data_type is {rts.data_type}, irts_modified.data_type is {rts_modified.data_type}"
        assert (rts.interval == rts_modified.interval), f"irts.interval is not equal to irts_modified.interval." \
                                                          f" irts.interval is {rts.interval}, irts_modified.interval is {rts_modified.interval}"

    def test_regular_timeseries_read_modify_store_modify_read(self):
        """
        Read a IrregularTimeSeries object, modify object then stores data on disk and read again
        """
        path = "/regular-time-series-many-points/unknown/flow/01Oct2004/15Minute//"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            rts = dss.get(path, startdatetime=datetime(2004, 10, 1), enddatetime=datetime(2004, 10, 30))

            rts.values[3] = 75
            rts.units = "FEET"

            path_modified = "/regular-time-series-many-points/unknown/flow/01Oct2004/15Minute/test-store/"

            rts.id = path_modified

            dss.put(rts)

            rts_modified = dss.get(path_modified)
        np.set_printoptions(suppress=True)
        assert (rts.get_length() == rts_modified.get_length()), f"irts.get_length() is not equal to irts_modified.get_length()." \
                                                                  f" irts.get_length() is {rts.get_length()}, irts_modified.get_length() is {rts_modified.get_length()}"
        assert (np.array_equal(rts.values, rts_modified.values)), f"irts.values is not equal to irts_modified.values." \
                                                      f" irts.values is {rts.values}, irts_modified.values is {rts_modified.values}"
        assert (np.array_equal(rts.times, rts_modified.times)), f"irts.times is not equal to irts_modified.times." \
                                                    f" irts.times is {rts.times}, irts_modified.times is {rts_modified.times}"
        assert (rts.units == rts_modified.units), f"irts.units is not equal to irts_modified.units." \
                                                    f" irts.units is {rts.units}, irts_modified.units is {rts_modified.units}"
        assert (rts.data_type == rts_modified.data_type), f"irts.data_type is not equal to irts_modified.data_type." \
                                                            f" irts.data_type is {rts.data_type}, irts_modified.data_type is {rts_modified.data_type}"
        assert (rts.interval == rts_modified.interval), f"irts.interval is not equal to irts_modified.interval." \
                                                          f" irts.interval is {rts.interval}, irts_modified.interval is {rts_modified.interval}"

    def test_regular_timeseries_read_modify_store_read(self):
        """
        Read a IrregularTimeSeries object, modify object then stores data on disk and read again
        """
        path = "/regular-time-series-many-points/unknown/flow/01Oct2004/15Minute//"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            rts = dss.get(path, startdatetime=datetime(2004, 10, 1), enddatetime=datetime(2004, 10, 30))

            rts.values[3] = 75
            rts.units = "FEET"

            dss.put(rts)

            rts_modified = dss.get(path, startdatetime=datetime(2004, 10, 1), enddatetime=datetime(2004, 10, 30))
        np.set_printoptions(suppress=True)
        assert (
                    rts.get_length() == rts_modified.get_length()), f"irts.get_length() is not equal to irts_modified.get_length()." \
                                                                    f" irts.get_length() is {rts.get_length()}, irts_modified.get_length() is {rts_modified.get_length()}"
        assert (np.array_equal(rts.values, rts_modified.values)), f"irts.values is not equal to irts_modified.values." \
                                                                  f" irts.values is {rts.values}, irts_modified.values is {rts_modified.values}"
        assert (np.array_equal(rts.times, rts_modified.times)), f"irts.times is not equal to irts_modified.times." \
                                                                f" irts.times is {rts.times}, irts_modified.times is {rts_modified.times}"
        assert (rts.units == rts_modified.units), f"irts.units is not equal to irts_modified.units." \
                                                  f" irts.units is {rts.units}, irts_modified.units is {rts_modified.units}"
        assert (rts.data_type == rts_modified.data_type), f"irts.data_type is not equal to irts_modified.data_type." \
                                                          f" irts.data_type is {rts.data_type}, irts_modified.data_type is {rts_modified.data_type}"
        assert (rts.interval == rts_modified.interval), f"irts.interval is not equal to irts_modified.interval." \
                                                        f" irts.interval is {rts.interval}, irts_modified.interval is {rts_modified.interval}"

    def test_regular_timeseries_empty_blocks(self):
        """ test reading time-series with discontinuous blocks"""
        pathname = "//SSPM5/ELEV/01Nov1991/1Hour/DCP-REV/"
        filename = self.test_files.create_test_file(".dss")
        with HecDss(filename) as dss:
            rts = RegularTimeSeries.create(range(10), start_date=datetime(1988, 1, 1, 8, 0, 0), interval="1Hour",
                                           units="cfs", path=pathname)
            dss.put(rts)
            rts = RegularTimeSeries.create(range(10), start_date=datetime(2016, 10, 11, 7, 0, 0), interval="1Hour",
                                           units="cfs", path=pathname)
            dss.put(rts)
            ts = dss.get(pathname)
            expected_count = 252273
            assert ts.get_length() == expected_count, f" expected {expected_count} values, found {ts.get_length()}"

    def test_regular_timeseries_timezone(self):
        """ test reading time-series with timezone information """
        pathname = "/regular-time-series/GAPT/FLOW/01Sep2021 - 31Oct2021/6Hour/forecast1/"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            rts = dss.get(pathname)
            assert rts.times[0].tzinfo is not None, f"expected timezone information, found None"
            assert rts.times[0].tzinfo.key == "UTC", f"expected UTC timezone, found {rts.times[0].tzinfo.zone}"

if __name__ == "__main__":
    unittest.main()
