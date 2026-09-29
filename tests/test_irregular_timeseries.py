"""Pytest module."""

import os
import sys
import unittest
from datetime import datetime, timedelta

import numpy as np
from file_manager import FileManager

from hecdss import HecDss
from hecdss.irregular_timeseries import IrregularTimeSeries


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
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            irts = dss.get(path)
        assert (113 == irts.get_length()
                ), f"irts.get_length() should be 113. is {irts.get_length()}"
        assert (39000 == irts.values[18]), f"irts.values[18] should be 39000. is {irts.values[18]}"
        assert ("1924-02-09 00:00:00"
                == str(irts.times[19])), f"irts.times[19] should be '1924-02-09 00:00:00'. is {irts.times[19]}"
        assert ("CFS" == irts.units), f"irts.units should be 'CFS'. is {irts.units}"
        assert ("INST-VAL"
                == irts.data_type), f"irts.data_type should be 'INST-VAL'. is {irts.data_type}"
        assert (0 == irts.interval), f"irts.interval should be 0. is {irts.interval}"

    def test_is_irregular_timeseries_type(self):
        """
        Test if dss.get() returns a record of type IrregularTimeSeries
        """
        path = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS/"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            irts = dss.get(path)
        assert (
            type(irts) is IrregularTimeSeries), f"irts should be type IrregularTimeSeries. is {type(irts)}"

    def test_irregular_timeseries_create_store(self):
        """
        create IrregularTimeSeries and store to dss
        """
        file = "examples-all-data-types.dss"
        with HecDss(self.test_files.get_copy(file)) as dss:

            irpath = "/irregular-time-series/GAPT/FLOW//IR-Day/forecast6/"
            irts = IrregularTimeSeries()
            dates = [datetime.today().replace(second=0, microsecond=0)
                     + (i * timedelta(hours=2)) for i in range(15)]
            dates[1] = dates[1] - timedelta(seconds=60)
            irts = IrregularTimeSeries.create(times=dates, values=list(
                range(15)), data_type="INST-VAL", path=irpath)

            dss.put(irts)

    def test_irregular_timeseries_create_store_read(self):
        """
        Generates a IrregularTimeSeries object then stores data on disk and read result
        """
        file = "examples-all-data-types.dss"
        with HecDss(self.test_files.get_copy(file)) as dss:

            irpath = "/irregular-time-series/GAPT/FLOW//IR-Day/forecast6/"
            dates = [datetime.today().replace(microsecond=0) + (i * timedelta(hours=2))
                     for i in range(15)]
            dates[1] = dates[1] - timedelta(seconds=60)
            irts = IrregularTimeSeries.create(times=dates, values=list(
                range(15)), data_type="INST-VAL", path=irpath)

            dss.put(irts)

            read_irts = dss.get(irpath)

        assert (read_irts.times == irts.times), f"saved and read times should be identical saved times are" \
            f" \n{irts.times}\n and read times are \n{read_irts.times}"

    def test_irregular_timeseries_create_store_read_with_notes(self):
        """
        Notes written on an IrregularTimeSeries survive a put/get round trip.
        """
        file = "examples-all-data-types.dss"
        with HecDss(self.test_files.get_copy(file)) as dss:

            irpath = "/irregular-time-series/GAPT/FLOW//IR-Day/forecast7/"
            dates = [datetime.today().replace(microsecond=0) + (i * timedelta(hours=2))
                     for i in range(5)]
            notes = ["", "storm event", "", "gage malfunction", ""]
            irts = IrregularTimeSeries.create(times=dates, values=list(range(5)), data_type="INST-VAL",
                                              path=irpath, notes=notes)

            dss.put(irts)

            read_irts = dss.get(irpath)

        assert (read_irts.notes == notes), f"saved and read notes should be identical. saved notes are" \
            f" \n{notes}\n and read notes are \n{read_irts.notes}"

    def test_irregular_timeseries_create_store_read_with_quality(self):
        """
        Quality flags written on an IrregularTimeSeries survive a put/get round trip.
        """
        file = "examples-all-data-types.dss"
        with HecDss(self.test_files.get_copy(file)) as dss:

            irpath = "/irregular-time-series/GAPT/FLOW//IR-Day/forecast8/"
            dates = [datetime.today().replace(microsecond=0) + (i * timedelta(hours=2))
                     for i in range(5)]
            quality = [0, 1, 2, 3, 4]
            irts = IrregularTimeSeries.create(times=dates, values=list(range(5)), data_type="INST-VAL",
                                              path=irpath, quality=quality)

            dss.put(irts)

            read_irts = dss.get(irpath)

        assert (read_irts.quality == quality), f"saved and read quality should be identical. saved quality is" \
            f" \n{quality}\n and read quality is \n{read_irts.quality}"

    def test_irregular_timeseries_create_store_read_with_quality_and_notes(self):
        """
        Quality flags and notes written together on an IrregularTimeSeries survive a put/get round trip.
        """
        file = "examples-all-data-types.dss"
        with HecDss(self.test_files.get_copy(file)) as dss:

            irpath = "/irregular-time-series/GAPT/FLOW//IR-Day/forecast9/"
            dates = [datetime.today().replace(microsecond=0) + (i * timedelta(hours=2))
                     for i in range(5)]
            quality = [0, 1, 2, 3, 4]
            notes = ["", "storm event", "", "gage malfunction", ""]
            irts = IrregularTimeSeries.create(times=dates, values=list(range(5)), data_type="INST-VAL",
                                              path=irpath, quality=quality, notes=notes)

            dss.put(irts)

            read_irts = dss.get(irpath)

        assert (read_irts.quality == quality), f"saved and read quality should be identical. saved quality is" \
            f" \n{quality}\n and read quality is \n{read_irts.quality}"
        assert (read_irts.notes == notes), f"saved and read notes should be identical. saved notes are" \
            f" \n{notes}\n and read notes are \n{read_irts.notes}"

    def test_irregular_timeseries_read_store_read(self):
        """
        Read a IrregularTimeSeries object then stores data on disk and read again
        """
        path = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS/"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            irts = dss.get(path)

            path_modified = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS-modified/"

            irts.id = path_modified

            dss.put(irts)

            irts_modified = dss.get(path_modified)
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
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            irts = dss.get(path)

            irts.times[1] = irts.times[1] - timedelta(seconds=60)
            irts.values[3] = 75
            irts.units = "FEET"

            path_modified = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1900/IR-Century/USGS-modified/"

            irts.id = path_modified

            dss.put(irts)

            irts_modified = dss.get(path_modified)
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
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            irts = dss.get(path)

            irts.times[1] = irts.times[1] - timedelta(seconds=60)
            irts.values[3] = 75
            dss.put(irts)

            irts_modified = dss.get(path)
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

    def test_irregular_timeseries_delete_time_window(self):
        """
        delete a time window from an irregular time series; points inside the window are removed
        """
        path = "/a/b/stage//IR-Year/delete-window/"
        times = [datetime(2020, 1, 1, h) for h in (1, 3, 5, 7)]
        with HecDss(self.test_files.create_test_file(".dss")) as dss:
            dss.put(IrregularTimeSeries.create([1.0, 2.0, 3.0, 4.0], times, path=path))
            status = dss.delete(path, startdatetime=datetime(2020, 1, 1, 2), enddatetime=datetime(2020, 1, 1, 6))
            irts = dss.get(path, datetime(2020, 1, 1), datetime(2020, 1, 2))
        self.assertEqual(0, status)
        self.assertNotIn(datetime(2020, 1, 1, 3), irts.times)
        self.assertNotIn(datetime(2020, 1, 1, 5), irts.times)
        self.assertEqual(1.0, irts.values[0])
        self.assertEqual(4.0, irts.values[-1])


if __name__ == "__main__":
    unittest.main()
