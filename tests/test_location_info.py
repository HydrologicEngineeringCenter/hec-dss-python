"""Pytest module."""

import unittest

from file_manager import FileManager

from hecdss import HecDss
from hecdss.location_info import LocationInfo


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
            dss.put(location)

            location2 = dss.get(location.id)

        assert_location_info_equal(location, location2)

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


        assert_location_info_equal(location, location2)

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

        assert_location_info_equal(IRTS.location_info, IRTS2.location_info)

def assert_location_info_equal(location1: LocationInfo, location2: LocationInfo):
    """
    Asserts that two LocationInfo objects are equal.
    """
    assert location1.x == location2.x, f"Expected x: {location1.x}, but got: {location2.x}"
    assert location1.y == location2.y, f"Expected y: {location1.y}, but got: {location2.y}"
    assert location1.z == location2.z, f"Expected z: {location1.z}, but got: {location2.z}"
    assert location1.coordinate_system == location2.coordinate_system, f"Expected coordinate_system: {location1.coordinate_system}, but got: {location2.coordinate_system}"
    assert location1.coordinate_id == location2.coordinate_id, f"Expected coordinate_id: {location1.coordinate_id}, but got: {location2.coordinate_id}"
    assert location1.horizontal_units == location2.horizontal_units, f"Expected horizontal_units: {location1.horizontal_units}, but got: {location2.horizontal_units}"
    assert location1.horizontal_datum == location2.horizontal_datum, f"Expected horizontal_datum: {location1.horizontal_datum}, but got: {location2.horizontal_datum}"
    assert location1.vertical_units == location2.vertical_units, f"Expected vertical_units: {location1.vertical_units}, but got: {location2.vertical_units}"
    assert location1.vertical_datum == location2.vertical_datum, f"Expected vertical_datum: {location1.vertical_datum}, but got: {location2.vertical_datum}"
    assert location1.time_zone_name == location2.time_zone_name, f"Expected time_zone_name: {location1.time_zone_name}, but got: {location2.time_zone_name}"
    assert location1.supplemental == location2.supplemental, f"Expected supplemental: {location1.supplemental}, but got: {location2.supplemental}"

if __name__ == "__main__":
    unittest.main()
