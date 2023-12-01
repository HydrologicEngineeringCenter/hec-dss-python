"""Pytest module."""



import unittest
import sys
from test_file_manager import TestFileManager
sys.path.append(r'src')

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
            "/EF RUSSIAN/COYOTE/PRECIP-INC//1Hour/TB/"
            "/GREEN RIVER/OAKVILLE/ELEVATION//1Hour//",
        ]
        t1 = datetime(2006, 3, 1)
        t2 = datetime(2006, 3, 30)
        for path in pathnames:
            print(f"reading {path}")
            tsc = dss.get(path, t1, t2)
            print(f"len(tsc.values) = {len(tsc.values)}")
            assert len(tsc.values) > 1
        dss.close()


    def test_basic(self):
        dss = HecDss(self.test_files.get_copy("sample7.dss"))
        print("record count = " + str(dss.recordCount()))

        t1 = datetime(2005, 1, 1)
        t2 = datetime(2005, 1, 4)
        tsc = dss.get("//SACRAMENTO/PRECIP-INC//1Day/OBS/", t1, t2)
        tsc.print_to_console()
        assert len(tsc.values) > 0
        tsc2 = dss.get("//SACRAMENTO/TEMP-MAX//1Day/OBS/", t1, t2)
        tsc2.print_to_console()
        assert len(tsc2.values) > 0
        # save to a new path
        tsc.dsspath = "//SACRAMENTO/PRECIP-INC//1Day/OBS-modified/"
        dss.put(tsc)
        tsc3 = dss.get(tsc.dsspath, t1, t2)
        assert len(tsc3.values) == len(tsc.values)
        dss.close()

    def test_catalog(self):
        dss = HecDss(self.test_files.get_copy("sample7.dss"))
        catalog = dss.getCatalog()
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
        rt = [100, 100, 100, 100, 100]
        c = Catalog(rawPaths, rt)
        c.print()

    def test_grid(self):
        dss = HecDss(self.test_files.get_copy("grid-example.dss"))

        dss.close()        


if __name__ == "__main__":
    unittest.main()
    # test_catalog()
    # test_issue9()
    # test_basic()
    # test_new_catalog()
