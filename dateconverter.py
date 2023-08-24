from datetime import datetime, timedelta

class DateConverter:
    @staticmethod
    def date_times_from_julian_array(times_julian, time_granularity_seconds, julian_base_date):
        if times_julian is None:
            raise ValueError("Time Series Times array was None. Something didn't work right in DSS.")
        times = []
        for t in times_julian:
            baseDateTime =datetime(1899,12,31) + timedelta(days=julian_base_date)    
            delta = 0
            if time_granularity_seconds == 60:  # 60 seconds per minute
                delta =timedelta(minutes=t)
            elif time_granularity_seconds == 3600:  # 600 seconds per hour
                delta =timedelta(hours=t)
            elif time_granularity_seconds == 86400:  # 86400 seconds per day
                delta =timedelta(days=t)
            else:
                raise ValueError("Error converting time with time_granularity_seconds=%d" % time_granularity_seconds)

            times.append(baseDateTime+delta)

        return times


t = 55226880
delta = timedelta(minutes=t)
dt = datetime(1900,1,1) + delta 
print(dt)
        

# Example usage
t = 55226880
delta = timedelta(minutes=t)
dt = datetime(1900,1,1) + delta 
print(dt)
#converter = DateConverter()
#converted_times = converter.date_times_from_julian_array(times_julian, time_granularity_seconds, julian_base_date)
#print(converted_times)
