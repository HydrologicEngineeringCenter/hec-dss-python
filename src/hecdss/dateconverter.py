import copy
from datetime import datetime, timedelta, time

sec = [
    31536000,
    2592000,
    1296000,
    864000,
    604800,
    86400,
    43200,
    28800,
    21600,
    14400,
    10800,
    7200,
    3600,
    1800,
    1200,
    900,
    720,
    600,
    360,
    300,
    240,
    180,
    120,
    60,
    30,
    20,
    15,
    10,
    6,
    5,
    4,
    3,
    2,
    1,
    0
]
time_string = [
    "1Year",
    "1Month",
    "Semi-Month",
    "Tri-Month",
    "1Week",
    "1Day",
    "12Hour",
    "8Hour",
    "6Hour",
    "4Hour",
    "3Hour",
    "2Hour",
    "1Hour",
    "30Minute",
    "20Minute",
    "15Minute",
    "12Minute",
    "10Minute",
    "6Minute",
    "5Minute",
    "4Minute",
    "3Minute",
    "2Minute",
    "1Minute",
    "30Second",
    "20Second",
    "15Second",
    "10Second",
    "6Second",
    "5Second",
    "4Second",
    "3Second",
    "2Second",
    "1Second",
    "0Second"
]
class DateConverter:


    @staticmethod
    def dss_datetime_from_string(dt):
        """ 
        convert python datetime to DSS 24:00 style string
        2023-08-25 09:32:46.832952 -> 25Aug2023 09:23:47
        2023-08-25 00:00:00.0000000 -> 24Aug2023 24:00
        2023-08-25 00:10:00.0000000 -> 25Aug2023 00:10
        """
        if dt.time() == time(0, 0, 0, 0): # midnight
            # subract one day
            dtm1 = dt - timedelta(days=1)
            dtstr= dtm1.strftime('%d%b%Y 24:00:00')
        else:
            dtstr = dt.strftime('%d%b%Y %H:%M:%S')
        
        return dtstr[:9],dtstr[-8:]

    @staticmethod
    def date_time_from_julian_second(time_julian, seconds_julian):
        """"
        convert from DSS integer datetime to python datetime array
        """

        baseDateTime = datetime(1900, 1, 1) - timedelta(days=1)  # datetime.fromtimestamp(julian_base_date)

        days = timedelta(days=time_julian)
        seconds = timedelta(seconds=seconds_julian)

        return baseDateTime + days + seconds

    @staticmethod
    def date_times_from_julian_array(times_julian, time_granularity_seconds, julian_base_date):
        """"
        convert from DSS integer datetime array to python datetime array
        """
        if times_julian is None:
            raise ValueError("Time Series Times array was None. Something didn't work right in DSS.")
        
        times = []
        for t in times_julian:
            baseDateTime =datetime(1900,1,1)- timedelta(days=1)     #datetime.fromtimestamp(julian_base_date)
            delta = 0
            if time_granularity_seconds == 1:  # 1 second
                delta =timedelta(seconds=t)
            if time_granularity_seconds == 60:  # 60 seconds per minute
                delta =timedelta(minutes=t)
            if time_granularity_seconds == 3600:  # 600 seconds per hour
                delta =timedelta(hours=t)
            if time_granularity_seconds == 86400:  # 86400 seconds per day
                delta =timedelta(days=t)

            times.append(baseDateTime+delta+timedelta(days=julian_base_date))

        return times

    @staticmethod
    def julian_array_from_date_times(date_times, time_granularity_seconds=60):
        """"
        convert from DSS integer datetime array to python datetime array
        """
        if date_times is None:
            raise ValueError("Time Series Times array was None. Something didn't work right in DSS.")

        base_date_time = datetime(1900, 1, 1) - timedelta(days=1) # datetime.fromtimestamp(julian_base_date)
        return [int((i-base_date_time).days*86400/time_granularity_seconds+(i.hour * 3600 + i.minute * 60 + i.second)/time_granularity_seconds) for i in date_times]
    @staticmethod
    def intervalString_to_sec(interval):

        if time_string.__contains__(interval):
            i = time_string.index(interval)
            return sec[i]
        elif sec.__contains__(interval):
            return interval

        return "empty"

    @staticmethod
    def sec_to_intervalString(seconds: int):

        i = sec.index(seconds)

        return time_string[i]


if __name__ == "__main__":
    dt = datetime.today()
    x = DateConverter.dss_datetime_from_string(dt)
    print(x)
    midnight = datetime(2023,8,3,0,0,0)
    x = DateConverter.dss_datetime_from_string(midnight)
    print(x)

