from datetime import datetime

class TimeSeries:
    def __init__(self):
        self.times = []
        self.values = []
        self.units =""
        self.dataType =""
        self.dsspath = ""
        self.timeGranularity = 1

    def add_data_point(self, date, value):
        self.times.append(date)
        self.values.append(value)

    def array_to_data(self, arr, time_pos=0, val_pos=1):
        '''
        Taking an array, or embedded list, in the format of [[time, value]]. 
        If you have data in a different order, you can specify the position when calling the function.
        '''
        for item in arr:
            if type(item[time_pos]) != datetime:
                raise Exception('Please make sure times are in datetime format')
            self.times.append(item[time_pos])
            self.values.append(item[val_pos])

    def new_timeseries(self, units, dataType, data_arr, time_pos=0, val_pos=1):
        self.units = units
        self.dataType = dataType
        self.array_to_data(data_arr, time_pos, val_pos)

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
        print("dsspath='"+self.dsspath+"'")
        print("units='"+self.units+"'")
        print("dataType='"+self.dataType+"'")
        for time, value in zip(self.times, self.values):
            print(f"Time: {time}, Value: {value}")
