"""Pytest module."""

import unittest

from file_manager import FileManager

from hecdss import HecDss
from hecdss.record_type import RecordType


class TestText(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_ressim_global_variables(self):
        with HecDss(self.test_files.get_copy("TestAlt1-dss-v7.dss")) as dss:

            catalog = dss.get_catalog()
            for ds in catalog:
                print(ds.recType, ds)
                self.assertEqual(RecordType.Text, ds.recType)


if __name__ == "__main__":
    unittest.main()
