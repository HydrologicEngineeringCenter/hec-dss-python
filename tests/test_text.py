"""Pytest module."""

import unittest
import sys
import os

from hecdss.record_type import RecordType

sys.path.append(r'src')
sys.path.append(os.path.dirname(__file__))

from file_manager import FileManager
from hecdss import Catalog, HecDss


class TestText(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_ressim_global_variables(self):
        dss = HecDss(self.test_files.get_copy("TestAlt1-dss-v7.dss"))

        catalog = dss.get_catalog()
        for ds in catalog:
            print(ds.recType, ds)
            self.assertEqual(RecordType.Text, ds.recType)
        dss.close()


if __name__ == "__main__":
    unittest.main()
