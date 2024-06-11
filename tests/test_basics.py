"""Pytest module."""

import unittest
import sys
from test_file_manager import TestFileManager
sys.path.append(r'src')
import copy

from hecdss import Catalog, HecDss
from datetime import datetime

TEST_DIR="tests/data/"

class TestBasics(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = TestFileManager(TEST_DIR)
    
    def tearDown(self) -> None:
        self.test_files.cleanup()


    def test_issue9(self):
        dss = HecDss(self.test_files.get_copy("sample7.dss"))
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
        dss.close()


    def test_basic(self):
        dss = HecDss(self.test_files.get_copy("sample7.dss"))
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
        dss.close()

    def test_catalog(self):
        dss = HecDss(self.test_files.get_copy("sample7.dss"))
        catalog = dss.get_catalog()
        for ds in catalog:
            print(ds.recType,ds)

        dss.close()

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

    def test_grid(self):
        dss = HecDss(self.test_files.get_copy("grid-example.dss"))

        dss.close()        


    def test_paired_data(self):
        """
        read record from disk, add labels save to new path
        """
        path = "/MY BASIN/DEER CREEK/STAGE-FLOW///USGS/"
        dss = HecDss(self.test_files.get_copy("sample7.dss"))
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

    def write_regular_timeseries(self):
        dss = HecDss(self.test_files.get_copy("sample7.dss"))
        print("record count = " + str(dss.record_count()))

        t1 = datetime(2005, 1, 1)
        t2 = datetime(2005, 1, 4)
        tsc = dss.get("//SACRAMENTO/PRECIP-INC//1Day/OBS/", t1, t2)  # read float
        tsc.print_to_console()

        tsc.id="//SACRAMENTO/PRECIP-INC//1Day/OBS-double/"
        dss.put(tsc)  # write double
        tsc = dss.get(tsc.id)
        self.assertEquals(4,len(tsc.values))
        dss.close()



if __name__ == "__main__":
    unittest.main()
    # test_catalog()
    # test_issue9()
    # test_basic()
    # test_new_catalog()
