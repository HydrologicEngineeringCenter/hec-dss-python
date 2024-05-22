"""Pytest module."""

import unittest
import sys

import numpy as np

from test_file_manager import TestFileManager
sys.path.append(r'src')
import copy
from hecdss.paired_data import PairedData
from hecdss.gridded_data import GriddedData
from hecdss.regular_timeseries import RegularTimeSeries
from hecdss import Catalog, HecDss
from datetime import datetime, timedelta

TEST_DIR = "tests/data/"

class TestGriddedData(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = TestFileManager(TEST_DIR)
    
    def tearDown(self) -> None:
        self.test_files.cleanup()


    def test_create_regular_timeseries(self):
        """
        create regular timerseries
        """
        # path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        # rts = RegularTimeSeries.create(range(15), interval="5Second", startDate=datetime.today(), path=path)
        # print(rts)

        path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/1Day/SHG-SNODAS/"
        rts = RegularTimeSeries.create(range(15), startDate=datetime.today(), path=path)
        print(rts)

        path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        times = [datetime.today()+(i * timedelta(seconds=10)) for i in range(15)]
        rts = RegularTimeSeries.create(range(15), times=times, path=path)
        print(rts)

        # path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/1Day/SHG-SNODAS/"
        # times = [datetime.today() + (i * timedelta(seconds=10)) for i in range(15)]
        # rts = RegularTimeSeries.create(range(15), times=times, path=path)
        # print(rts)

        # path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        # dss = HecDss(self.test_files.get_copy("grid-example.dss"))
        # gd = dss.get(path)
        # dss.close()
        # assert (gd.numberOfCellsX == 21), f"gd.numberOfCellsX should be 50. is {gd.numberOfCellsX}"
        # assert (gd.numberOfCellsY == 28), f"gd.numberOfCellsY should be 50. is {gd.numberOfCellsY}"




if __name__ == "__main__":
    unittest.main()
