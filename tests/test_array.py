"""Pytest module."""

import unittest
import os
import sys

sys.path.append(r'src')
sys.path.append(os.path.dirname(__file__))
from file_manager import FileManager
from hecdss import Catalog, HecDss
from datetime import datetime


class TestArray(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_arrays(self):
        dss = HecDss("dss_array.dss")

        dss.put()


if __name__ == "__main__":
    unittest.main()
