"""Pytest module."""

import unittest
import sys

from test_file_manager import TestFileManager
sys.path.append(r'src')
import copy
from hecdss.PairedData import PairedData
from hecdss.gridded_data import GriddedData
from hecdss import Catalog, HecDss
from datetime import datetime

TEST_DIR="tests/data/"

# update MODIFIED_TEST_DIR to be the path the folder containing dss files
# "sample7.dss" and "R703F3-PF_v7.dss" which are modified within these tests
MODIFIED_TEST_DIR=r"C:\Users\oskar\Documents\dss"

class Test_Grid_Data(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = TestFileManager(TEST_DIR)
    
    def tearDown(self) -> None:
        self.test_files.cleanup()


    def test_gridded_data_read(self):
        """
        read record from disk
        """
        path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        dss = HecDss(self.test_files.get_copy("grid-example.dss"))
        gd = dss.get(path)
        dss.close()
        assert (gd.numberOfCellsX == 21), f"gd.numberOfCellsX should be 50. is {gd.numberOfCellsX}"
        assert (gd.numberOfCellsY == 28), f"gd.numberOfCellsY should be 50. is {gd.numberOfCellsY}"

    def test_is_gridded_data_type(self):
        """
        Test if dss.get() returns a record of type PairedData
        """
        path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        dss = HecDss(self.test_files.get_copy("grid-example.dss"))
        gd = dss.get(path)
        dss.close()
        assert (type(gd) is GriddedData), f"gd should be type GriddedData. is {type(gd)}"

    def test_gridded_data_create(self):
        """
        Generates a PairedData object
        """
        data = [[j+(50*i) for j in range(50)] for i in range(50)]
        gd = GriddedData.create(data=data)
        assert (gd.data == data), f"gd.data should be {data}. is {gd.data}"
        assert (gd.numberOfCellsX == 50), f"gd.numberOfCellsX should be 50. is {gd.numberOfCellsX}"
        assert (gd.numberOfCellsY == 50), f"gd.numberOfCellsY should be 50. is {gd.numberOfCellsY }"

    def test_gridded_data_create_store(self):
        """
        Generates a PairedData object then stores data on disk
        """
        path = "/grid/new/gradient/01MAY2024:1400/01MAY2024:1400/new2-grad/"
        # file = self.test_files.get_copy("grid-example.dss")
        # dss = HecDss(file)
        dss = HecDss(MODIFIED_TEST_DIR + r"\grid-example.dss")
        data = [[j + (50 * i) for j in range(50)] for i in range(50)]
        gd = GriddedData.create(data=data, path=path)

        status = dss.put(gd)

        gd2 = dss.get(path)

        dss.close()

        assert (status == 0), f"status should be 0. is {status}"
    #
    # def test_paired_data_create_store_read(self):
    #     """
    #     Generates a PairedData object then stores data on disk
    #     """
    #     dss = HecDss(self.test_files.get_copy("sample7.dss"))
    #     # dss = HecDss(MODIFIED_TEST_DIR+r"\sample7.dss")
    #     x_values = [00, 11, 22, 33, 44]
    #     y_values = [[j + i for j in range(3)] for i in x_values]
    #     path = "/MY BASIN/DEER CREEK/STAGE-FLOW///USGS-create/"
    #     pd = PairedData.create(x_values, y_values, path=path)
    #
    #     pd.labels = ["x plus 0", "x plus 1", "x plus 2"]
    #     pd.units_independent = "cm"
    #
    #     dss.put(pd)
    #
    #     pd2 = dss.get(path)
    #     dss.close()
    #
    #     assert (pd.values == pd2.values), f"pd.values contents is not equal to that of pd2.values. pd is {pd.values} and pd2 is {pd2.values}"
    #     assert (pd.labels == pd2.labels), f"pd.labels contents is not equal to that of pd2.labels. pd is {pd.labels} and pd2 is {pd2.labels}"
    #     assert (pd.ordinates == pd2.ordinates), f"pd.ordinates contents is not equal to that of pd2.ordinates. pd is {pd.ordinates} and pd2 is {pd2.ordinates}"
    #
    def test_paired_data_read_store_read(self):
        """
        Generates a PairedData object then stores data on disk
        """
        path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        # dss = HecDss(self.test_files.get_copy("grid-example.dss"))
        dss = HecDss(MODIFIED_TEST_DIR + r"\grid-example.dss")
        gd = dss.get(path)

        path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS-new/"
        gd.id = path
        status = dss.put(gd)

        assert (status == 0), f"status should be 0. is {status}"

        gd2 = dss.get(path)

        # assert (pd.values == pd3.values), f"pd.values contents is not equal to that of pd2.values. pd is {pd.values} and pd2 is {pd3.values}"
        # assert (pd.labels[0] == "Flow"), f"pd.labels is not equal to 'Flow'. pd.labels[0] is {pd.labels[0]}"
        # assert (pd3.labels[0] == "Flow2"), f"pd3.labels[0] is not equal to 'Flow2'. pd3.labels[0] is {pd3.labels[0]}"
        # assert (pd.ordinates == pd3.ordinates), f"pd.ordinates contents is not equal to that of pd2.ordinates. pd is {pd.ordinates} and pd2 is {pd3.ordinates}"


        dss.close()
    #
    # def test_paired_data_labels_bug(self):
    #     """
    #     Generates a PairedData object then stores data on disk
    #     """
    #     dss = HecDss(self.test_files.get_copy("R703F3-PF_v7.dss"))
    #     # dss = HecDss(MODIFIED_TEST_DIR + r"\R703F3-PF_v7.dss")
    #     path = "/FOLSOM/AUXILIARY SPILLWAY-GATE RATING/ELEV-FLOW/PAIREDVALUESEXT///"
    #     pd = dss.get(path)
    #
    #     path2 = "/FOLSOM/AUXILIARY SPILLWAY-GATE RATING/ELEV-FLOW/PAIREDVALUESEXT//modified/"
    #     pd2 = copy.deepcopy(pd)
    #     pd2.id = path2
    #     pd2.labels[3] = "New Label"
    #
    #     status = dss.put(pd2)  # save
    #
    #     pd3 = dss.get(path2)
    #
    #     assert (pd.values == pd3.values), f"pd.values contents is not equal to that of pd2.values. pd is {pd.values} and pd2 is {pd3.values}"
    #     assert (pd3.labels[3] == "New Label"), f"pd3.labels[3] is not equal to 'New Label'. pd3.labels[3] is {pd3.labels[3]}"
    #     assert (pd.ordinates == pd3.ordinates), f"pd.ordinates contents is not equal to that of pd2.ordinates. pd is {pd.ordinates} and pd2 is {pd3.ordinates}"
    #
    #
    #     dss.close()

if __name__ == "__main__":
    unittest.main()
