"""Pytest module."""

import unittest
import os
import sys
import numpy as np

sys.path.append(r'src')
sys.path.append(os.path.dirname(__file__))
from file_manager import FileManager
from hecdss import HecDss, ArrayContainer


class TestArray(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_arrays(self):
        a = ArrayContainer.create_float_array([1.0, 3.0, 5.0, 7.0])
        a.id = "/test/float-array/redshift////"

        dss = HecDss(self.test_files.create_test_file(".dss"))
        print(f" record_count = {dss.record_count()}")
        dss.put(a)
        # dss.set_debug_level(15)
        print(f"record_type = {dss.get_record_type(a.id)}")
        b = dss.get(a.id)
        print(b)
        np.testing.assert_array_equal(b.values, a.values)


if __name__ == "__main__":
    unittest.main()
