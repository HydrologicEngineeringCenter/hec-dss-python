"""Pytest module."""

import unittest

import numpy as np
from file_manager import FileManager

from hecdss import HecDss
from hecdss.gridded_data import GriddedData


NULL_INT = -3.4028234663852886e+38

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

    def test_null_consistency(self):
        """
        This test serves to ensure that the range limit table remains consistent with different cases of missing values.
        """
        gd_nan = self._create_half_nul_gd(np.nan)
        gd_negative = self._create_half_nul_gd(-9999)
        gd_null_int = self._create_half_nul_gd(NULL_INT)
        gd_zero = self._create_half_nul_gd(0)

        assert (gd_nan.numberOfRanges == 2)
        assert (gd_nan.numberOfRanges == gd_negative.numberOfRanges)
        assert (gd_nan.numberOfRanges == gd_null_int.numberOfRanges)
        assert (gd_nan.numberOfRanges == gd_zero.numberOfRanges)

        assert (gd_nan.maxDataValue == gd_negative.maxDataValue)
        assert (gd_nan.maxDataValue == gd_null_int.maxDataValue)
        assert (gd_nan.maxDataValue == gd_zero.maxDataValue)

        assert (gd_nan.minDataValue == gd_negative.minDataValue)
        assert (gd_nan.minDataValue == gd_null_int.minDataValue)
        assert (gd_nan.minDataValue == gd_zero.minDataValue)


    def test_all_null_grid(self):
        """
        A grid whose cells are all null (e.g. warped entirely outside the data
        coverage) must not raise when the grid info is computed.
        """
        for null_value in (NULL_INT, -9999, 0, np.nan):
            gd = GriddedData.create(
                data=[[null_value for _ in range(10)] for _ in range(10)],
                nullValue=null_value,
            )

            assert gd.numberOfRanges == 2
            assert not np.isnan(gd.minDataValue)
            assert not np.isnan(gd.maxDataValue)
            assert not np.isnan(gd.meanDataValue)
            assert gd.minDataValue == gd.maxDataValue
            assert np.all(gd.data == gd.nullValue) or np.all(np.isnan(gd.data))

    def test_nan_and_null_value_are_equivalent(self):
        """
        Undefined cells may arrive marked with the null value or with NaN;
        both conventions must produce the same grid.
        """
        base = np.arange(400, dtype=float).reshape(20, 20) % 50 + 1.0

        for undefined_fraction in (0.0, 0.5, 1.0):
            cut = int(400 * undefined_fraction)
            marked_null = base.copy().reshape(-1)
            marked_nan = base.copy().reshape(-1)
            marked_null[:cut] = NULL_INT
            marked_nan[:cut] = np.nan

            gd_null = GriddedData.create(
                data=marked_null.reshape(20, 20), nullValue=NULL_INT)
            gd_nan = GriddedData.create(
                data=marked_nan.reshape(20, 20), nullValue=NULL_INT)

            assert gd_null.minDataValue == gd_nan.minDataValue
            assert gd_null.maxDataValue == gd_nan.maxDataValue
            assert gd_null.meanDataValue == gd_nan.meanDataValue
            assert gd_null.numberOfRanges == gd_nan.numberOfRanges
            assert np.array_equal(gd_null.rangeLimitTable, gd_nan.rangeLimitTable)
            assert np.array_equal(gd_null.numberEqualOrExceedingRangeLimit,
                                  gd_nan.numberEqualOrExceedingRangeLimit)
            # NaN must never survive into the stored grid
            assert not np.isnan(gd_nan.data).any()
            assert np.array_equal(gd_null.data, gd_nan.data)

    def _create_half_nul_gd(self, default_value):
        gd_data = [[1 for _ in range(100)] for _ in range(50)]
        gd_data.extend([[default_value for _ in range(100)] for _ in range(50)])

        gd_test = GriddedData.create(
            data=gd_data,
            nullValue=default_value
        )

        return gd_test


if __name__ == "__main__":
    unittest.main()
