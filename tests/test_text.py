"""Pytest module."""

import unittest

from file_manager import FileManager

from hecdss import HecDss
from hecdss.record_type import RecordType
from hecdss.text import Text


class TestText(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()


    def test_text_from_scratch(self):
        with HecDss(self.test_files.get_copy("TestAlt1-dss-v7.dss")) as dss:
            path = "/A/B/C/D/E/F/"
            text = "This is a test\nof text data\nin a DSS file.\n"
            test_txt = Text.create(path, text)
            dss.put(test_txt)
            txt = dss.get(path)
            self.assertEqual(test_txt.text, txt.text)


if __name__ == "__main__":
    unittest.main()
