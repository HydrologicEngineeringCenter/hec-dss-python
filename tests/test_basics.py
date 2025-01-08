"""Pytest module."""

import unittest
import os
import sys

sys.path.append(r'src')
sys.path.append(os.path.dirname(__file__))
from file_manager import FileManager
from hecdss import Catalog, HecDss
from datetime import datetime


class TestBasics(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_issue9(self):
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            pathnames = [
                "//SACRAMENTO/PRECIP-INC//1Day/OBS/",
                "/EF RUSSIAN/COYOTE/PRECIP-INC//1Hour/TB/",
                "/GREEN RIVER/OAKVILLE/ELEVATION//1Hour/OBS/",
            ]
            t1 = datetime(2006, 3, 1)
            t2 = datetime(2006, 3, 30)
            for path in pathnames:
                print(f"reading {path}")
                tsc = dss.get(path, t1, t2)
                print(f"len(tsc.values) = {len(tsc.values)}")
                # assert len(tsc.values) > 1

    def test_basic(self):
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            print("record count = " + str(dss.record_count()))

            t1 = datetime(2005, 1, 1)
            t2 = datetime(2005, 1, 4)
            tsc = dss.get("//SACRAMENTO/PRECIP-INC//1Day/OBS/", t1, t2)
            tsc.print_to_console()
            assert len(tsc.values) > 0
            tsc2 = dss.get("//SACRAMENTO/TEMP-MAX//1Day/OBS/", t1, t2)
            tsc2.print_to_console()
            assert len(tsc2.values) > 0
            # save to a new path
            tsc.id = "//SACRAMENTO/PRECIP-INC//1Day/OBS-modified/"
            dss.put(tsc)
            tsc3 = dss.get(tsc.id, t1, t2)
            assert len(tsc3.values) == len(tsc.values)

    def test_catalog(self):
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            catalog = dss.get_catalog()
            for ds in catalog:
                print(ds.recType, ds)


    def test_catalog_get(self):
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            catalog = dss.get_catalog()
            ts = dss.get(catalog.items[0])


    def test_with_block(self):

        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            catalog = dss.get_catalog()
            ts = dss.get(catalog.items[0])




    def test_new_catalog(self):
        rawPaths = [
            "//SACRAMENTO/TEMP-MIN/01Jan1989/1Day/OBS/",
            "//SACRAMENTO/TEMP-MIN/01Jan1990/1Day/OBS/",
            "//SACRAMENTO/TEMP-MIN/01Jan1991/1Day/OBS/",
            "//SACRAMENTO/TEMP-MIN/01Jan1992/1Day/OBS/",
            "//SACRAMENTO/TEMP-MIN/01Jan1993/1Day/OBS/",
        ]
        recordType = [100, 100, 100, 100, 100]
        c = Catalog(rawPaths, recordType)
        c.print()


    def test_paired_data(self):
        """
        read record from disk, add labels save to new path
        """
        path = "/MY BASIN/DEER CREEK/STAGE-FLOW///USGS/"
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            dss.get(path)
        # pd.labels=['Flow']
        #
        # pd2 = copy.deepcopy(pd)
        # pd2.id ="/MY BASIN/DEER CREEK/STAGE-FLOW///USGS-modified/"
        # pd2.labels = ['Flow']
        # dss.put(pd2) # save
        #
        # pd3 = dss.get(path)
        # dss.close()
        # assert(1,len(pd.labels))
        # assert("Flow",pd3.labels[0])

    def test_write_regular_timeseries(self):
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            print("record count = " + str(dss.record_count()))

            t1 = datetime(2005, 1, 1)
            t2 = datetime(2005, 1, 4)
            tsc = dss.get("//SACRAMENTO/PRECIP-INC//1Day/OBS/", t1, t2)  # read float
            tsc.print_to_console()

            tsc.id = "//SACRAMENTO/PRECIP-INC/01Jan2005/1Day/OBS-double/"
            dss.put(tsc)  # write double
            tsc = dss.get(tsc.id, t1, t2)
            tsc.print_to_console()
            self.assertEqual(4, len(tsc.values))

    def test_missing_values(self):
        with HecDss(self.test_files.get_copy("missing_data.dss")) as dss:
            print("record count = " + str(dss.record_count()))
            tsc = dss.get("/CUMBERLAND RIVER/CUMBERLAND FALLS/FLOW//30Minute/MISSING/", datetime(2020, 1, 3, 11, 0),
                        datetime(2020, 1, 13, 0, 0))
            tsc.print_to_console()

    # values = ts.values
    # MISSING = -3.4028234663852886e+38
    # tolerance = 100000
    # values = [None if abs(x - MISSING) < tolerance else x for x in values]
    def test_read_regular_timeseries_with_quality(self):

        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            print("record count = " + str(dss.record_count()))
            t1 = datetime(2021, 9, 15, 7)
            t2 = datetime(2021, 10, 4, 7)
            tsc = dss.get("/regular-time-series/GAPT/FLOW//6Hour/forecast1/", t1, t2)
            tsc.print_to_console()
            self.assertEqual(77, len(tsc.values))

    def test_incorrect_path(self):
        with self.assertRaises(Exception):
            with HecDss(self.test_files.get_copy("incorrect_path.dss")) as dss:
                pass

if __name__ == "__main__":
    unittest.main()
    # test_catalog()
    # test_issue9()
    # test_basic()
    # test_new_catalog()
