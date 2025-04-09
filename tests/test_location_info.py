"""Pytest module."""

import unittest
import sys
import os
import numpy as np

sys.path.append(r'src')
sys.path.append(os.path.dirname(__file__))

from file_manager import FileManager
import copy
from hecdss.paired_data import PairedData
from hecdss.location_info import LocationInfo
from hecdss import HecDss


# update MODIFIED_TEST_DIR to be the path the folder containing dss files
# "sample7.dss" and "R703F3-PF_v7.dss" which are modified within these tests
# MODIFIED_TEST_DIR=r"C:\Users\oskar\Documents\dss"

class TestLocationInfo(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()
    
    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_location_info_read(self):
        """
        Read a IrregularTimeSeries object, modify object then stores data on disk and read again
        """
        path = "/irregular-time-series/FAIR OAKS CA/Location Info////"
        dss = HecDss(self.test_files.get_copy("examples-all-data-types.dss"))
        location = dss.get(path)

    def test_location_info_read_write(self):
        """
        Read a IrregularTimeSeries object, modify object then stores data on disk and read again
        """
        path = "/irregular-time-series/FAIR OAKS CA/Location Info////"
        dss = HecDss(self.test_files.get_copy("examples-all-data-types.dss"))
        location = dss.get(path)

        dss.put(location)

    def test_location_info_read_write_read(self):
        """
        Read a IrregularTimeSeries object, modify object then stores data on disk and read again
        """
        path = "/irregular-time-series/FAIR OAKS CA/Location Info////"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            location = dss.get(path)
            location.id = path
            dss.put(location)

            location2 = dss.get(location.id)

        assert location.x == location2.x, f"Expected x: {location.x}, but got: {location2.x}"
        assert location.y == location2.y, f"Expected y: {location.y}, but got: {location2.y}"
        assert location.z == location2.z, f"Expected z: {location.z}, but got: {location2.z}"
        assert location.coordinate_system == location2.coordinate_system, f"Expected coordinate_system: {location.coordinate_system}, but got: {location2.coordinate_system}"
        assert location.coordinate_id == location2.coordinate_id, f"Expected coordinate_id: {location.coordinate_id}, but got: {location2.coordinate_id}"
        assert location.horizontal_units == location2.horizontal_units, f"Expected horizontal_units: {location.horizontal_units}, but got: {location2.horizontal_units}"
        assert location.horizontal_datum == location2.horizontal_datum, f"Expected horizontal_datum: {location.horizontal_datum}, but got: {location2.horizontal_datum}"
        assert location.vertical_units == location2.vertical_units, f"Expected vertical_units: {location.vertical_units}, but got: {location2.vertical_units}"
        assert location.vertical_datum == location2.vertical_datum, f"Expected vertical_datum: {location.vertical_datum}, but got: {location2.vertical_datum}"
        assert location.time_zone_name == location2.time_zone_name, f"Expected time_zone_name: {location.time_zone_name}, but got: {location2.time_zone_name}"
        assert location.supplemental == location2.supplemental, f"Expected supplemental: {location.supplemental}, but got: {location2.supplemental}"

    def test_location_info_read_new_path_write_read(self):
        """
        Read a IrregularTimeSeries object, modify object then stores data on disk and read again
        """
        path = "/irregular-time-series/FAIR OAKS CA/Location Info////"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            location = dss.get(path)
            path2 = "/irregular-time-series/FAIR OAKS CA/Location Info///newPath/"
            location.id = path2
            location.x += 1
            dss.put(location)

            location2 = dss.get(location.id)


        assert location.x == location2.x, f"Expected x: {location.x}, but got: {location2.x}"
        assert location.y == location2.y, f"Expected y: {location.y}, but got: {location2.y}"
        assert location.z == location2.z, f"Expected z: {location.z}, but got: {location2.z}"
        assert location.coordinate_system == location2.coordinate_system, f"Expected coordinate_system: {location.coordinate_system}, but got: {location2.coordinate_system}"
        assert location.coordinate_id == location2.coordinate_id, f"Expected coordinate_id: {location.coordinate_id}, but got: {location2.coordinate_id}"
        assert location.horizontal_units == location2.horizontal_units, f"Expected horizontal_units: {location.horizontal_units}, but got: {location2.horizontal_units}"
        assert location.horizontal_datum == location2.horizontal_datum, f"Expected horizontal_datum: {location.horizontal_datum}, but got: {location2.horizontal_datum}"
        assert location.vertical_units == location2.vertical_units, f"Expected vertical_units: {location.vertical_units}, but got: {location2.vertical_units}"
        assert location.vertical_datum == location2.vertical_datum, f"Expected vertical_datum: {location.vertical_datum}, but got: {location2.vertical_datum}"
        assert location.time_zone_name == location2.time_zone_name, f"Expected time_zone_name: {location.time_zone_name}, but got: {location2.time_zone_name}"
        assert location.supplemental == location2.supplemental, f"Expected supplemental: {location.supplemental}, but got: {location2.supplemental}"

    def test_location_info_container_read_write(self):
        """
        Read a IrregularTimeSeries object, modify object then stores data on disk and read again
        """
        path = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/10Jan1862 - 10Feb2017/IR-Century/USGS/"
        dss = HecDss(self.test_files.get_copy("examples-all-data-types.dss"))
        IRTS = dss.get(path)

        assert IRTS.location_info is not None, f"Expected location_info to be not None, but got: None"

        dss.put(IRTS)

    def test_location_info_container_read_new_path_write_read(self):
        """
        Read a IrregularTimeSeries object, modify object then stores data on disk and read again
        """
        path = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/10Jan1862 - 10Feb2017/IR-Century/USGS/"
        with HecDss(self.test_files.get_copy("examples-all-data-types.dss")) as dss:
            IRTS = dss.get(path)
            path2 = "/irregular-time-series/FAIR OAKS CA/FLOW-ANNUAL PEAK/10Jan1862 - 10Feb2017/IR-Century/USGS_newPath/"
            IRTS.id = path2
            dss.put(IRTS)

            IRTS2 = dss.get(IRTS.id)

        assert IRTS.location_info.x == IRTS2.location_info.x, f"Expected x: {IRTS.location_info.x}, but got: {IRTS2.location_info.x}"
        assert IRTS.location_info.y == IRTS2.location_info.y, f"Expected y: {IRTS.location_info.y}, but got: {IRTS2.location_info.y}"
        assert IRTS.location_info.z == IRTS2.location_info.z, f"Expected z: {IRTS.location_info.z}, but got: {IRTS2.location_info.z}"
        assert IRTS.location_info.coordinate_system == IRTS2.location_info.coordinate_system, f"Expected coordinate_system: {IRTS.location_info.coordinate_system}, but got: {IRTS2.location_info.coordinate_system}"
        assert IRTS.location_info.coordinate_id == IRTS2.location_info.coordinate_id, f"Expected coordinate_id: {IRTS.location_info.coordinate_id}, but got: {IRTS2.location_info.coordinate_id}"
        assert IRTS.location_info.horizontal_units == IRTS2.location_info.horizontal_units, f"Expected horizontal_units: {IRTS.location_info.horizontal_units}, but got: {IRTS2.location_info.horizontal_units}"
        assert IRTS.location_info.horizontal_datum == IRTS2.location_info.horizontal_datum, f"Expected horizontal_datum: {IRTS.location_info.horizontal_datum}, but got: {IRTS2.location_info.horizontal_datum}"
        assert IRTS.location_info.vertical_units == IRTS2.location_info.vertical_units, f"Expected vertical_units: {IRTS.location_info.vertical_units}, but got: {IRTS2.location_info.vertical_units}"
        assert IRTS.location_info.vertical_datum == IRTS2.location_info.vertical_datum, f"Expected vertical_datum: {IRTS.location_info.vertical_datum}, but got: {IRTS2.location_info.vertical_datum}"
        assert IRTS.location_info.time_zone_name == IRTS2.location_info.time_zone_name, f"Expected time_zone_name: {IRTS.location_info.time_zone_name}, but got: {IRTS2.location_info.time_zone_name}"
        assert IRTS.location_info.supplemental == IRTS2.location_info.supplemental, f"Expected supplemental: {IRTS.location_info.supplemental}, but got: {IRTS2.location_info.supplemental}"

if __name__ == "__main__":
    unittest.main()
