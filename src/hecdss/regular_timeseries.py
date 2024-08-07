import numpy as np

from .dateconverter import DateConverter
from .dsspath import DssPath
from datetime import datetime, timedelta

class RegularTimeSeries:
    def __init__(self):
        self.times = []
        self.values = np.empty(0)
        self.quality = []
        self.units = ""
        self.dataType = ""
        self.interval = ""
        self.startDate = ""
        self.id = ""

    def add_data_point(self, date, value, flag=None):
        self.times.append(date)
        self.values.append(value)
        if flag is not None:
            self.quality.append(flag)

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
        print("Time,Value,Flag")
        if not len(self.quality) > 0:
            for time, value in zip(self.times, self.values):
                print(f"{time}, {value}")
        else:
            for time, value, flag in zip(self.times, self.values, self.quality):
                print(f"{time}, {value}, {flag}")

    def _get_interval_interval(self):
        result = DateConverter.intervalString_to_sec(self.interval)
        return result

    def _get_interval_path(self):
        if self.id is not None:
            return DateConverter.intervalString_to_sec(DssPath(self.id, type(self)).E)
        return "empty"

    def _get_interval_times(self):
        if len(self.times) > 1 and type(self.times[0]) == datetime:
            interval = self.times[1]-self.times[0]
            return int(interval.total_seconds())
        return "empty"
    def _interval_to_interval(self, new_interval):
        self.interval = new_interval

    def _interval_to_path(self, new_interval):
        if self.id != None:
            new_path = DssPath(self.id, type(self))
            new_path.E = DateConverter.sec_to_intervalString(new_interval)
            self.id = str(new_path)

    def _interval_to_times(self, new_interval):
        if type(self.startDate) == datetime:
            for i in range(len(self.values)):
                self.times.append(self.startDate + (i * timedelta(seconds=new_interval)))
    def _generate_times(self):
        if(len(self.times) > 0 and self.startDate == ""):
            self.startDate = self.times[0]

        x = [self._get_interval_times(), self._get_interval_path(), self._get_interval_interval()]
        x = [i for i in x if i != "empty"]
        print(x)
        if(not all(i == x[0] for i in x)):
            raise ValueError("inconsistent interval within arguments")
        elif len(x) != 3 and len(x) != 0:
            self._interval_to_interval(x[0])
            self._interval_to_path(x[0])
            self._interval_to_times(x[0])

    @staticmethod
    def create(values, times=[], units="", dataType="", interval="", startDate="", path=None):
        rts = RegularTimeSeries()
        rts.times = times
        rts.values = np.array(values)
        rts.units = units
        rts.dataType = dataType
        rts.interval = interval
        rts.startDate = startDate
        rts.id = path
        rts._generate_times()

        return rts
