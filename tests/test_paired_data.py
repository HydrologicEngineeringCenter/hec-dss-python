"""Pytest module."""

import copy
import unittest

import numpy as np
from file_manager import FileManager

from hecdss import HecDss
from hecdss.paired_data import PairedData


# update MODIFIED_TEST_DIR to be the path the folder containing dss files
# "sample7.dss" and "R703F3-PF_v7.dss" which are modified within these tests
# MODIFIED_TEST_DIR=r"C:\Users\oskar\Documents\dss"

class TestPairedData(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()
    
    def tearDown(self) -> None:
        self.test_files.cleanup()


    def test_paired_data_read(self):
        """
        read record from disk
        """
        path = "/MY BASIN/DEER CREEK/STAGE-FLOW///USGS/"
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            pd = dss.get(path)
        assert (5.1500 == float(str(pd.ordinates[2])[:6])), f"pd.ordinates[2] should be 5.1500. is {float(str(pd.ordinates[2])[:6])}"
        assert (19 == pd.values[2][0]), f"pd.values[2][0] should be 19. is {pd.values[2][0]}"
        assert ("" == pd.labels[0]), f"pd.labels[0] should be ''. is {pd.labels[0]}"
        assert ("FEET" == pd.units_independent), f"pd.units_independent should be 'FEET'. is {pd.units_independent}"
        assert ("UNT" == pd.type_independent), f"pd.type_independent should be 'UNT'. is {pd.type_independent}"
        assert ("CFS" == pd.units_dependent), f"pd.units_dependent should be 'CFS'. is {pd.units_dependent}"
        assert ("UNT" == pd.type_dependent), f"pd.type_dependent should be 'UNT'. is {pd.type_dependent}"

    def test_is_paired_data_type(self):
        """
        Test if dss.get() returns a record of type PairedData
        """
        path = "/MY BASIN/DEER CREEK/STAGE-FLOW///USGS/"
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            pd = dss.get(path)
        assert (type(pd) is PairedData), f"pd should be type PairedData. is {type(pd)}"

    def test_paired_data_create(self):
        """
        Generates a PairedData object
        """
        x_values = [00, 11, 22, 33, 44]
        y_values = [[j+i for j in range(3)] for i in x_values]
        pd = PairedData.create(x_values, y_values)

        pd.labels = ["x plus 0", "x plus 1", "x plus 2"]
        pd.units_independent = "cm"

        assert (type(pd) is PairedData), f"pd should be type PairedData. is {type(pd)}"
        assert (pd.ordinates[1] == 11), f"pd.ordinates[1] should be 11. is {pd.ordinates[1]}"
        assert (pd.values[4][2] == 46), f"pd.values[4][2] should be 46. is {pd.values[4][2]}"
        assert (len(pd.ordinates) == 5), f"len(pd.ordinates) should be 5. is {len(pd.ordinates)}"
        assert (pd.labels[1] == "x plus 1"), f"pd.labels[1] should be 'x plus 1'. is {pd.labels[1]}"

    def test_paired_data_create_store(self):
        """
        Generates a PairedData object then stores data on disk
        """
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            x_values = [00, 11, 22, 33, 44]
            y_values = [[j + i for j in range(3)] for i in x_values]
            pd = PairedData.create(x_values, y_values, path="/MY BASIN/DEER CREEK/STAGE-FLOW///USGS-create/")

            pd.labels = ["x plus 0", "x plus 1", "x plus 2"]
            pd.units_independent = "cm"

            status = dss.put(pd)

        assert (status == 0), f"status should be 0. is {status}"

    def test_paired_data_create_store_read(self):
        """
        Generates a PairedData object then stores data on disk
        """
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            x_values = [00, 11, 22, 33, 44]
            y_values = [[j + i for j in range(3)] for i in x_values]
            path = "/MY BASIN/DEER CREEK/STAGE-FLOW///USGS-create/"
            pd = PairedData.create(x_values, y_values, path=path)

            pd.labels = ["x plus 0", "x plus 1", "x plus 2"]
            pd.units_independent = "cm"

            dss.put(pd)

            pd2 = dss.get(path)

        assert (np.array_equal(pd.values, pd2.values)), f"pd.values contents is not equal to that of pd2.values. pd is {pd.values} and pd2 is {pd2.values}"
        assert (pd.labels == pd2.labels), f"pd.labels contents is not equal to that of pd2.labels. pd is {pd.labels} and pd2 is {pd2.labels}"
        assert (np.array_equal(pd.ordinates, pd2.ordinates)), f"pd.ordinates contents is not equal to that of pd2.ordinates. pd is {pd.ordinates} and pd2 is {pd2.ordinates}"

    def test_paired_data_read_store_read(self):
        """
        Generates a PairedData object then stores data on disk
        """
        with HecDss(self.test_files.get_copy("sample7.dss")) as dss:
            path = "/MY BASIN/DEER CREEK/STAGE-FLOW///USGS/"
            pd = dss.get(path)

            pd.labels = ['Flow']

            path2 = "/MY BASIN/DEER CREEK/STAGE-FLOW///USGS-modified/"
            pd2 = copy.deepcopy(pd)
            pd2.id = path2
            pd2.labels = ['Flow2']
            pd2.units_independent = "data"

            status = dss.put(pd2)  # save

            pd3 = dss.get(path2)

        assert (np.array_equal(pd.values, pd3.values)), f"pd.values contents is not equal to that of pd2.values. pd is {pd.values} and pd2 is {pd3.values}"
        assert (pd.labels[0] == "Flow"), f"pd.labels is not equal to 'Flow'. pd.labels[0] is {pd.labels[0]}"
        assert (pd3.labels[0] == "Flow2"), f"pd3.labels[0] is not equal to 'Flow2'. pd3.labels[0] is {pd3.labels[0]}"
        assert (np.array_equal(pd.ordinates, pd3.ordinates)), f"pd.ordinates contents is not equal to that of pd2.ordinates. pd is {pd.ordinates} and pd2 is {pd3.ordinates}"


    def test_paired_data_labels_bug(self):
        """
        Generates a PairedData object then stores data on disk
        """
        with HecDss(self.test_files.get_copy("R703F3-PF_v7.dss")) as dss:
            path = "/FOLSOM/AUXILIARY SPILLWAY-GATE RATING/ELEV-FLOW/PAIREDVALUESEXT///"
            pd = dss.get(path)

            path2 = "/FOLSOM/AUXILIARY SPILLWAY-GATE RATING/ELEV-FLOW/PAIREDVALUESEXT//modified/"
            pd2 = copy.deepcopy(pd)
            pd2.id = path2
            pd2.labels[3] = "New Label"

            status = dss.put(pd2)  # save

            pd3 = dss.get(path2)

        assert (np.array_equal(pd.values, pd3.values)), f"pd.values contents is not equal to that of pd2.values. pd is {pd.values} and pd2 is {pd3.values}"
        assert (pd3.labels[3] == "New Label"), f"pd3.labels[3] is not equal to 'New Label'. pd3.labels[3] is {pd3.labels[3]}"
        assert (np.array_equal(pd.ordinates, pd3.ordinates)), f"pd.ordinates contents is not equal to that of pd2.ordinates. pd is {pd.ordinates} and pd2 is {pd3.ordinates}"


if __name__ == "__main__":
    unittest.main()
