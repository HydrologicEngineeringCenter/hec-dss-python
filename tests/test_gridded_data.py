"""Pytest module."""

import unittest

import numpy as np
from file_manager import FileManager

from hecdss import HecDss
from hecdss.gridded_data import GriddedData


class TestGriddedData(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_gridded_data_read(self):
        """
        read GriddedData record from disk
        """
        path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        with HecDss(self.test_files.get_copy("grid-example.dss")) as dss:
            gd = dss.get(path)
            assert (gd.numberOfCellsX == 21), f"gd.numberOfCellsX should be 50. is {gd.numberOfCellsX}"
            assert (gd.numberOfCellsY == 28), f"gd.numberOfCellsY should be 50. is {gd.numberOfCellsY}"

    def test_is_gridded_data_type(self):
        """
        Test if dss.get() returns a record of type PairedData
        """
        path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        with HecDss(self.test_files.get_copy("grid-example.dss")) as dss:
            gd = dss.get(path)
            assert (type(gd) is GriddedData), f"gd should be type GriddedData. is {type(gd)}"

    def test_gridded_data_create(self):
        """
        Generates a GriddedData object
        """
        data = [[j + (50 * i) for j in range(50)] for i in range(50)]
        gd = GriddedData.create(data=data)
        assert (np.array_equal(gd.data, np.array(data))), f"gd.data should be {np.array(data)}. is {gd.data}"
        assert (gd.numberOfCellsX == 50), f"gd.numberOfCellsX should be 50. is {gd.numberOfCellsX}"
        assert (gd.numberOfCellsY == 50), f"gd.numberOfCellsY should be 50. is {gd.numberOfCellsY}"

    def test_gridded_data_create_store(self):
        """
        Generates a GriddedData object then stores data on disk
        """
        path = "/grid/new/gradient/01MAY2024:1400/01MAY2024:1400/new2-grad/"
        file = self.test_files.get_copy("grid-example.dss")
        with HecDss(file) as dss:
            # dss = HecDss(MODIFIED_TEST_DIR + r"\grid-example.dss")
            data = [[j + (50 * i) for j in range(50)] for i in range(50)]
            gd = GriddedData.create(data=data, path=path)

            status = dss.put(gd)

            gd2 = dss.get(path)


        assert (status == 0), f"status should be 0. is {status}"

    def test_gridded_data_read_store_read(self):
        """
        Generates a GriddedData object then stores data on disk
        """
        path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        with HecDss(self.test_files.get_copy("grid-example.dss")) as dss:
            # dss = HecDss(MODIFIED_TEST_DIR + r"\grid-example.dss")
            gd = dss.get(path)

            path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS-new/"
            gd.id = path
            status = dss.put(gd)

            assert (status == 0), f"status should be 0. is {status}"

            gd2 = dss.get(path)

            assert (np.array_equal(gd.data,
                                gd2.data)), f"gd.data contents is not equal to that of gd2.data. gd is {gd.data} and gd2 is {gd2.data}"
            assert (
                    gd.dataUnits == gd2.dataUnits), f"gd2.dataUnits is not equal to {gd.dataUnits}. gd2.dataUnits is {gd2.dataUnits}"

    def test_gridded_data_write_precompressed(self):
        """
        Test writing precompressed gridded data using zlib deflate.
        Reads existing grid data, compresses it, writes using writePrecompressedGrid, and compares.
        """
        import zlib

        # Read existing gridded data
        original_path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS/"
        file = self.test_files.get_copy("grid-example.dss")

        with HecDss(file) as dss:
            # Read the original grid
            gd_original = dss.get(original_path)

            # Compress the data using zlib deflate
            raw_bytes = gd_original.data.astype(np.float32).tobytes()
            compressed_data = zlib.compress(raw_bytes)
            compression_size = len(compressed_data)

            # Create a new GriddedData object with metadata from original
            # but pointing to a new path
            new_path = "/grid/EAU GALLA RIVER/SNOW MELT/02FEB2020:0600/03FEB2020:0600/SHG-SNODAS-COMPRESSED/"
            gd_original.id = new_path


            # Write the precompressed grid
            status = dss.writePrecompressedGrid(gd_original, compressed_data, compression_size)

            # Read back the compressed grid
            gd_readback = dss.get(new_path)

            # Compare the two grids
            assert status == 0, f"writePrecompressedGrid status should be 0, is {status}"
            assert np.array_equal(gd_original.data, gd_readback.data), "Data from original and compressed grid do not match"
            assert gd_original.numberOfCellsX == gd_readback.numberOfCellsX, "numberOfCellsX mismatch"
            assert gd_original.numberOfCellsY == gd_readback.numberOfCellsY, "numberOfCellsY mismatch"
            assert gd_original.dataUnits == gd_readback.dataUnits, "dataUnits mismatch"


if __name__ == "__main__":
    unittest.main()
