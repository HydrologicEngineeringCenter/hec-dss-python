"""Pytest module."""

import unittest
import sys
import os


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


    def test_create_irregular_timeseries(self):
        """
        create regular timerseries
        """
        # path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        # rts = RegularTimeSeries.create(range(15), interval="5Second", startDate=datetime.today(), path=path)
        # print(rts)

        #
        file = "examples-all-data-types.dss"
        # file = "sample7.dss"
        dss = HecDss(self.test_files.get_copy(file))

        baseDateTime = datetime(1900, 1, 1) - timedelta(days=1)

        # irpath = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/01Jan1800/IR-Century/USGS/"

        irpath = "/regular-time-series/GAPT/FLOW/01Sep2021/6Hour/forecast1/"
        irts = IrregularTimeSeries()
        dates = [datetime.today()+(i * timedelta(hours=1)) for i in range(15)]
        irts.times = dates
        irts.values = list(range(15))
        irts.data_type = "INST-VAL"
        irts.id = irpath

        # dss.put(irts)

        read_irts = dss.get(irpath)

        assert (read_irts.times == irts.times), f"saved and read times should be identical saved times are" \
                                                f" \n{irts.times}\n and read times are \n{read_irts.times}"

        dss.close()


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
