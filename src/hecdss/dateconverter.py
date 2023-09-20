from datetime import datetime, timedelta, time

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
            dtstr= dtm1.strftime('%d%b%Y 24:00')      
        else:
            dtstr = dt.strftime('%d%b%Y %H:%M')      
        
        return dtstr[:9],dtstr[-5:]


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
            if time_granularity_seconds == 60:  # 60 seconds per minute
                delta =timedelta(minutes=t)
            if time_granularity_seconds == 3600:  # 600 seconds per hour
                delta =timedelta(hours=t)
            if time_granularity_seconds == 86400:  # 86400 seconds per day
                delta =timedelta(days=t)

            times.append(baseDateTime+delta)

        return times



if __name__ == "__main__":
    dt = datetime.today()
    x = DateConverter.dss_datetime_from_string(dt)
    print(x)
    midnight = datetime(2023,8,3,0,0,0)
    x = DateConverter.dss_datetime_from_string(midnight)
    print(x)

