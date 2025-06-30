import unittest

from hecdss.dss_type import DssType


class TestBasics(unittest.TestCase):


    def test_to_string(self):
        """ This is testing the __str__ method  in DssType """
        t = DssType.PER_CUM
        s = str(t)
        assert s == "PER-CUM", f"actual:{s},  expected 'PER-CUM'"

