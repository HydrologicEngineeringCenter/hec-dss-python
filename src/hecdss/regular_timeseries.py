import numpy as np

from .dateconverter import DateConverter
from .dsspath import DssPath
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class RegularTimeSeries:
    def __init__(self):
        """
        Initializes a new instance of the RegularTimeSeries class.
        """
        self.times = []
        self.values = np.empty(0)
        self.quality = []
        self.units = ""
        self.data_type = ""
        self.interval = ""
        self.start_date = ""
        self.time_granularity_seconds = 1
        self.julian_base_date = 0
        self.time_zone_name = ""
        self.id = ""
        self.location_info = None

    def add_data_point(self, date, value, flag=None):
        """
        Adds a data point to the time series.

        Args:
            date (datetime): The date of the data point.
            value (float): The value of the data point.
            flag (int, optional): The quality flag of the data point. Defaults to None.
        """
        self.times.append(date)
        self.values.append(value)
        if flag is not None:
            self.quality.append(flag)

    def get_value_at(self, date):
        """
        Retrieves the value at a specific date.

        Args:
            date (datetime): The date for which to retrieve the value.

        Returns:
            float: The value at the specified date, or None if the date is not found.
        """
        if date in self.times:
            index = self.times.index(date)
            return self.values[index]
        else:
            return None

    def get_values(self):
        """
        Retrieves all values in the time series.

        Returns:
            numpy.ndarray: An array of all values in the time series.
        """
        return self.values

    def get_dates(self):
        """
        Retrieves all dates in the time series.

        Returns:
            list: A list of all dates in the time series.
        """
        return self.times

    def get_length(self):
        """
        Retrieves the number of data points in the time series.

        Returns:
            int: The number of data points in the time series.
        """
        return len(self.times)

    def print_to_console(self):
        """
        Prints the time series data to the console.
        """
        print("dsspath='" + self.id + "'")
        print("units='"+self.units+"'")
        print("dataType='" + self.data_type + "'")
        print("Time,Value,Flag")
        if not len(self.quality) > 0:
            for time, value in zip(self.times, self.values):
                print(f"{time}, {value}")
        else:
            for time, value, flag in zip(self.times, self.values, self.quality):
                print(f"{time}, {value}, {flag}")

    def _get_interval_interval(self):
        """
        Converts the interval string to seconds.

        Returns:
            int: The interval in seconds.
        """
        result = DateConverter.intervalString_to_sec(self.interval)
        return result

    def _get_interval_path(self):
        """
        Converts the interval string of the DSS path to seconds.

        Returns:
            int: The interval in seconds, or "empty" if the id is None.
        """
        if self.id is not None:
            return DateConverter.intervalString_to_sec(DssPath(self.id, type(self)).E)
        return "empty"

    def _get_interval_times(self):
        """
        Calculates the interval between the first two dates in the time series.

        Returns:
            int: The interval in seconds, or "empty" if there are fewer than two dates.
        """
        if len(self.times) > 1 and type(self.times[0]) == datetime:
            interval = self.times[1]-self.times[0]
            total_seconds = interval.total_seconds()
            if total_seconds > 86400:
                return "empty"
            return int(interval.total_seconds())
        return "empty"

    def _interval_to_interval(self, new_interval):
        """
        Sets the interval to a new value.

        Args:
            new_interval (int): The new interval in seconds.
        """
        self.interval = new_interval

    def _interval_to_path(self, new_interval):
        """
        Updates the DSS path with a new interval.

        Args:
            new_interval (int): The new interval in seconds.
        """
        if self.id != None:
            new_path = DssPath(self.id, type(self))
            new_path.E = DateConverter.sec_to_intervalString(new_interval)
            self.id = str(new_path)

    def _interval_to_times(self, new_interval):
        """
        Updates the times in the time series based on a new interval.

        Args:
            new_interval (int): The new interval in seconds.
        """
        is_leap = lambda y: y % 4 == 0 and y % 100 != 0 or y % 400 == 0
        last_day = lambda y, m: 31 if m in (1,3,5,7,8,10,12) else 30 if m in (4,6,9,11) else 29 if is_leap(y) else 28
        if type(self.start_date) == datetime:
            tz = ZoneInfo(self.time_zone_name) if self.time_zone_name else None
            first_time = self.start_date.replace(microsecond=0, tzinfo=tz)
            count = len(self.values)
            if new_interval <= 604800:
                # --------------------- #
                # non-calendar interval #
                # --------------------- #
                span = timedelta(seconds=new_interval)
                self.times = [(first_time + i * span) for i in range(count)]
            elif new_interval == 864000:
                # ------------------ #
                # Tri-Month interval #
                # ------------------ #
                raise ValueError("Tri-Month interval not currently supported")
            elif new_interval == 1296000:
                # ------------------- #
                # Semi-Month interval #
                # ------------------- #
                raise ValueError("Semi-Month interval not currently supported")
            elif new_interval == 2592000:
                # ---------------- #
                # 1-Month interval #
                # ---------------- #
                self.times = [first_time]
                for i in range(1, count):
                    y, m, d, h, n, s = self.times[-1].timetuple()[:6]
                    if m == 12:
                        y += 1
                        m = 1
                    else:
                        m += 1
                    d = min(last_day(y, m), first_time.day)
                    self.times.append(datetime(y, m, d, h, n, s, tzinfo=tz))
            elif new_interval == 31536000:
                # --------------- #
                # 1-Year interval #
                # --------------- #
                self.times = [first_time]
                for i in range(1, count):
                    y, m, d, h, n, s = self.times[-1].timetuple()[:6]
                    y += 1
                    d = min(last_day(y, m), first_time.day)
                    self.times.append(datetime(y, m, d, h, n, s, tzinfo=tz))
            else:
                raise ValueError(f"Invalid interval seconds: {new_interval}")


    def _generate_times(self):
        """
        Generates times for the time series based on the interval and start date.
        """
        if(len(self.times) > 0 and self.start_date == ""):
            self.start_date = self.times[0]

        x = [self._get_interval_times(), self._get_interval_path(), self._get_interval_interval()]
        x = [i for i in x if i != "empty"]
        if(not all(i == x[0] for i in x)):
            raise ValueError("inconsistent interval within arguments")
        elif len(x) != 3 and len(x) != 0:
            self._interval_to_interval(x[0])
            self._interval_to_path(x[0])
            self._interval_to_times(x[0])

    @staticmethod
    def create(values, times=[], quality=[], units="", data_type="", interval="", start_date="", time_granularity_seconds=1, julian_base_date=0, time_zone_name="", path=None, location_info = None):
        """
        Creates a new instance of the RegularTimeSeries class with the specified parameters.

        Args:
            values (list): List of data values.
            times (list, optional): List of time values. Defaults to [].
            quality (list, optional): List of quality values. Defaults to [].
            units (str, optional): Units of the data. Defaults to "".
            data_type (str, optional): Type of the data. Defaults to "".
            interval (str, optional): Interval of the time series. Defaults to "".
            start_date (str, optional): Start date of the time series. Defaults to "".
            time_granularity_seconds (int, optional): Time granularity in seconds. Defaults to 1.
            julian_base_date (int, optional): Julian base date. Defaults to 0.
            path (str, optional): DSS path. Defaults to None.
            location_info (LocationInfo, optional): Location info assotiated with record container.

        Returns:
            RegularTimeSeries: A new instance of the RegularTimeSeries class.
        """
        rts = RegularTimeSeries()
        rts.times = [i.replace(microsecond=0) for i in times]
        rts.values = np.array(values)
        rts.quality = quality
        rts.units = units
        rts.data_type = data_type
        rts.interval = interval
        rts.start_date = start_date
        rts.time_granularity_seconds = time_granularity_seconds
        rts.julian_base_date = julian_base_date
        rts.time_zone_name = time_zone_name
        rts.id = path
        rts.location_info = location_info
        rts._generate_times()

        return rts