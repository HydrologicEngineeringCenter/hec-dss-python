import numpy as np

class LocationInfo:
    def __init__(self):
        self.x = np.empty(0)
        self.y = np.empty(0)
        self.z = np.empty(0)
        self.coordinate_system = None
        self.coordinate_id = None
        self.horizontal_units = None
        self.horizontal_datum = None
        self.vertical_units = None
        self.vertical_datum = None
        self.time_zone_name = ""
        self.supplemental = ""
        self.id = None

    @staticmethod
    def create(x_values, y_values, z_values, coordinate_system, coordinate_id, horizontal_units, horizontal_datum, vertical_units, vertical_datum, time_zone_name, supplemental, path=None):
        location_info = LocationInfo()
        location_info.x = np.array(x_values)
        location_info.y = np.array(y_values)
        location_info.z = np.array(z_values)
        location_info.coordinate_system = coordinate_system
        location_info.coordinate_id = coordinate_id
        location_info.horizontal_units = horizontal_units
        location_info.horizontal_datum = horizontal_datum
        location_info.vertical_units = vertical_units
        location_info.vertical_datum = vertical_datum
        location_info.time_zone_name = time_zone_name
        location_info.supplemental = supplemental
        location_info.id = path
        return location_info

