from datetime import datetime

import numpy as np


class IrregularTimeSeries:
    """ container for time-series data that is not at a consistent interval.
    data is stored internally as a numpy array
    """
    def __init__(self):
        self.times = []
        self.values = np.empty(0)
        self.quality = []
        self.units = ""
        self.data_type = ""
        self.interval = 0
        self.start_date = ""
        self.time_granularity_seconds = 1
        self.julian_base_date = 0
        self.id = ""

    def add_data_point(self, date, value):
        self.times.append(date)
        self.values.append(value)

    def get_value_at(self, date):
        if date in self.times:
            index = self.times.index(date)
            return self.values[index]
        else:
            return None

    def get_values(self):
        return self.values

    def get_dates(self):
        return self.times

    def get_length(self):
        return len(self.times)

    def print_to_console(self):
        print("dsspath='" + self.id + "'")
        print("units='"+self.units+"'")
        print("dataType='" + self.data_type + "'")
        for time, value in zip(self.times, self.values):
            print(f"Time: {time}, Value: {value}")

    @staticmethod
    def create(values, times, quality=[], units="", data_type="", interval=0, start_date="", time_granularity_seconds=1, julian_base_date=None, path=None):
        irts = IrregularTimeSeries()
        irts.times = times
        irts.values = np.array(values)
        irts.quality = quality
        irts.units = units
        irts.data_type = data_type
        irts.interval = interval
        irts.start_date = start_date
        irts.time_granularity_seconds = time_granularity_seconds
        irts.julian_base_date = 0
        if julian_base_date is None and len(times):
            irts.julian_base_date = (times[0]-datetime(1900, 1, 1)).days
        irts.id = path
        return irts
