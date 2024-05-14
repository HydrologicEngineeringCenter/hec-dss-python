import numpy as np


class TimeSeries:
    def __init__(self):
        self.times = []
        self.values = np.empty(0)
        self.units =""
        self.dataType =""
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
        print("dataType='"+self.dataType+"'")
        for time, value in zip(self.times, self.values):
            print(f"Time: {time}, Value: {value}")
