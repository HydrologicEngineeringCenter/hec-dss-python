"""Pytest module."""

import unittest

import numpy as np
from file_manager import FileManager

from hecdss import ArrayContainer, HecDss


class TestArray(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_arrays(self):
        a = ArrayContainer.create_array_container(float_values=[1.0, 3.0, 5.0, 7.0])
        a.id = "/test/float-array/redshift////"

        with HecDss(self.test_files.create_test_file(".dss")) as dss:
            print(f" record_count = {dss.record_count()}")
            dss.put(a)
            # dss.set_debug_level(15)
            print(f"record_type = {dss.get_record_type(a.id)}")
            b = dss.get(a.id)
            print(b)
            np.testing.assert_array_equal(b.float_values, a.float_values)

    def test2_arrays(self):
        # Open a DSS file
        with HecDss(self.test_files.create_test_file(".dss")) as dss:

            # Retrieve and print data
            data_path = "/test/float-array/redshift////"
            iarray = list(range(15))
            farray = np.float32([1.0, 3.0, 5.0, 7.0])
            darray = np.float64([32.3*i for i in range(8)])
            a = ArrayContainer.create_array_container(int_values=iarray, float_values=farray, double_values=darray)
            a.id = data_path

            dss.put(a)

            b = dss.get(data_path)

            np.testing.assert_array_equal(b.int_values, a.int_values)
            np.testing.assert_array_equal(b.float_values, a.float_values)
            np.testing.assert_array_equal(b.double_values, a.double_values)

            b.values = b.double_values * 2

            data_path_modify = "/test/float-array/redshift///modify/"
            b.id = data_path_modify

            dss.put(b)

            c = dss.get(data_path_modify)

            np.testing.assert_array_equal(b.int_values, c.int_values)
            np.testing.assert_array_equal(b.float_values, c.float_values)
            np.testing.assert_array_equal(b.double_values, c.double_values)



if __name__ == "__main__":
    unittest.main()
