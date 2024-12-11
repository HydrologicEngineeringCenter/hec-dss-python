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
    def create(values, times=[], quality=[], units="", data_type="", interval=0, start_date="", path=None):
        irts = IrregularTimeSeries()
        irts.times = times
        irts.values = np.array(values)
        irts.quality = quality
        irts.units = units
        irts.data_type = data_type
        irts.interval = interval
        irts.start_date = start_date
        irts.id = path
        return irts
