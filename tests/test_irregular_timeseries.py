"""Pytest module."""

import unittest
import sys
import os
import numpy as np


sys.path.append(r'src')
sys.path.append(os.path.dirname(__file__))

from file_manager import FileManager
from hecdss.irregular_timeseries import IrregularTimeSeries
from datetime import datetime, timedelta
from hecdss import HecDss

class TestRegularTimeSeries(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()
    
    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_irregular_timeseries_read(self):
        """
        read record from disk
        """
        path = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS/"
        dss = HecDss(self.test_files.get_copy("examples-all-data-types.dss"))
        irts = dss.get(path)
        dss.close()
        assert (113 == irts.get_length()), f"irts.get_length() should be 113. is {irts.get_length()}"
        assert (39000 == irts.values[18]), f"irts.values[18] should be 39000. is {irts.values[18]}"
        assert ("1924-02-09 00:00:00" == str(irts.times[19])), f"irts.times[19] should be '1924-02-09 00:00:00'. is {irts.times[19]}"
        assert ("CFS" == irts.units), f"irts.units should be 'CFS'. is {irts.units}"
        assert ("INST-VAL" == irts.data_type), f"irts.data_type should be 'INST-VAL'. is {irts.data_type}"
        assert (0 == irts.interval), f"irts.interval should be 0. is {irts.interval}"

    def test_is_irregular_timeseries_type(self):
        """
        Test if dss.get() returns a record of type IrregularTimeSeries
        """
        path = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS/"
        dss = HecDss(self.test_files.get_copy("examples-all-data-types.dss"))
        irts = dss.get(path)
        dss.close()
        assert (type(irts) is IrregularTimeSeries), f"irts should be type IrregularTimeSeries. is {type(irts)}"

    def test_irregular_timeseries_create_store(self):
        """
        create IrregularTimeSeries and store to dss
        """
        file = "examples-all-data-types.dss"
        dss = HecDss(self.test_files.get_copy(file))

        irpath = "/irregular-time-series/GAPT/FLOW//IR-Day/forecast6/"
        irts = IrregularTimeSeries()
        dates = [datetime.today().replace(second=0, microsecond=0)+(i * timedelta(hours=2)) for i in range(15)]
        dates[1] = dates[1] - timedelta(seconds=60)
        irts.times = dates
        irts.values = list(range(15))
        irts.data_type = "INST-VAL"
        irts.id = irpath

        dss.put(irts)

        dss.close()

    def test_irregular_timeseries_create_store_read(self):
        """
        Generates a IrregularTimeSeries object then stores data on disk and read result
        """
        file = "examples-all-data-types.dss"
        dss = HecDss(self.test_files.get_copy(file))

        irpath = "/irregular-time-series/GAPT/FLOW//IR-Day/forecast6/"
        irts = IrregularTimeSeries()
        dates = [datetime.today().replace(second=0, microsecond=0) + (i * timedelta(hours=2)) for i in range(15)]
        dates[1] = dates[1] - timedelta(seconds=60)
        irts.times = dates
        irts.values = list(range(15))
        irts.data_type = "INST-VAL"
        irts.id = irpath

        dss.put(irts)

        read_irts = dss.get(irpath)

        dss.close()

        assert (read_irts.times == irts.times), f"saved and read times should be identical saved times are" \
                                                f" \n{irts.times}\n and read times are \n{read_irts.times}"

    def test_irregular_timeseries_read_store_read(self):
        """
        Read a IrregularTimeSeries object then stores data on disk and read again
        """
        path = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS/"
        dss = HecDss(self.test_files.get_copy("examples-all-data-types.dss"))
        #dss = HecDss("C:/Users/q0hecoah/Documents/data/examples-all-data-types.dss")
        irts = dss.get(path)

        path_modified = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS-modified/"

        irts.id = path_modified

        dss.put(irts)

        irts_modified = dss.get(path_modified)
        dss.close()
        np.set_printoptions(suppress=True)
        assert (irts.get_length() == irts_modified.get_length()), f"irts.get_length() is not equal to irts_modified.get_length()." \
                                                                  f" irts.get_length() is {irts.get_length()}, irts_modified.get_length() is {irts_modified.get_length()}"
        assert (np.array_equal(irts.values, irts_modified.values)), f"irts.values is not equal to irts_modified.values." \
                                                      f" irts.values is {irts.values}, irts_modified.values is {irts_modified.values}"
        assert (np.array_equal(irts.times, irts_modified.times)), f"irts.times is not equal to irts_modified.times." \
                                                    f" irts.times is {irts.times}, irts_modified.times is {irts_modified.times}"
        assert (irts.units == irts_modified.units), f"irts.units is not equal to irts_modified.units." \
                                                    f" irts.units is {irts.units}, irts_modified.units is {irts_modified.units}"
        assert (irts.data_type == irts_modified.data_type), f"irts.data_type is not equal to irts_modified.data_type." \
                                                            f" irts.data_type is {irts.data_type}, irts_modified.data_type is {irts_modified.data_type}"
        assert (irts.interval == irts_modified.interval), f"irts.interval is not equal to irts_modified.interval." \
                                                          f" irts.interval is {irts.interval}, irts_modified.interval is {irts_modified.interval}"

    def test_irregular_timeseries_read_modify_store_modify_read(self):
        """
        Read a IrregularTimeSeries object, modify object then stores data on disk and read again
        """
        path = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS/"
        dss = HecDss(self.test_files.get_copy("examples-all-data-types.dss"))
        irts = dss.get(path)

        irts.times[1] = irts.times[1] - timedelta(seconds=60)
        irts.values[3] = 75
        irts.units = "FEET"

        path_modified = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS-modified/"

        irts.id = path_modified

        dss.put(irts)

        irts_modified = dss.get(path_modified)
        dss.close()
        np.set_printoptions(suppress=True)
        assert (irts.get_length() == irts_modified.get_length()), f"irts.get_length() is not equal to irts_modified.get_length()." \
                                                                  f" irts.get_length() is {irts.get_length()}, irts_modified.get_length() is {irts_modified.get_length()}"
        assert (np.array_equal(irts.values, irts_modified.values)), f"irts.values is not equal to irts_modified.values." \
                                                      f" irts.values is {irts.values}, irts_modified.values is {irts_modified.values}"
        assert (np.array_equal(irts.times, irts_modified.times)), f"irts.times is not equal to irts_modified.times." \
                                                    f" irts.times is {irts.times}, irts_modified.times is {irts_modified.times}"
        assert (irts.units == irts_modified.units), f"irts.units is not equal to irts_modified.units." \
                                                    f" irts.units is {irts.units}, irts_modified.units is {irts_modified.units}"
        assert (irts.data_type == irts_modified.data_type), f"irts.data_type is not equal to irts_modified.data_type." \
                                                            f" irts.data_type is {irts.data_type}, irts_modified.data_type is {irts_modified.data_type}"
        assert (irts.interval == irts_modified.interval), f"irts.interval is not equal to irts_modified.interval." \
                                                          f" irts.interval is {irts.interval}, irts_modified.interval is {irts_modified.interval}"

    def test_irregular_timeseries_read_modify_store_read(self):
        """
        Read a IrregularTimeSeries object, modify object then stores data on disk and read again
        """
        path = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS/"
        dss = HecDss(self.test_files.get_copy("examples-all-data-types.dss"))
        irts = dss.get(path)

        irts.times[1] = irts.times[1] - timedelta(seconds=60)
        irts.values[3] = 75
        dss.put(irts)

        irts_modified = dss.get(path)
        dss.close()
        np.set_printoptions(suppress=True)
        assert (irts.get_length() == irts_modified.get_length()), f"irts.get_length() is not equal to irts_modified.get_length()." \
                                                                  f" irts.get_length() is {irts.get_length()}, irts_modified.get_length() is {irts_modified.get_length()}"
        assert (np.array_equal(irts.values, irts_modified.values)), f"irts.values is not equal to irts_modified.values." \
                                                      f" irts.values is {irts.values}, irts_modified.values is {irts_modified.values}"
        assert (np.array_equal(irts.times, irts_modified.times)), f"irts.times is not equal to irts_modified.times." \
                                                    f" irts.times is {irts.times}, irts_modified.times is {irts_modified.times}"
        assert (irts.units == irts_modified.units), f"irts.units is not equal to irts_modified.units." \
                                                    f" irts.units is {irts.units}, irts_modified.units is {irts_modified.units}"
        assert (irts.data_type == irts_modified.data_type), f"irts.data_type is not equal to irts_modified.data_type." \
                                                            f" irts.data_type is {irts.data_type}, irts_modified.data_type is {irts_modified.data_type}"
        assert (irts.interval == irts_modified.interval), f"irts.interval is not equal to irts_modified.interval." \
                                                          f" irts.interval is {irts.interval}, irts_modified.interval is {irts_modified.interval}"


if __name__ == "__main__":
    unittest.main()
