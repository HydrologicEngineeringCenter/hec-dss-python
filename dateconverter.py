from datetime import datetime, timedelta

class DateConverter:
    @staticmethod
    def date_times_from_julian_array(times_julian, time_granularity_seconds, julian_base_date):
        if times_julian is None:
            raise ValueError("Time Series Times array was None. Something didn't work right in DSS.")
        
        times = []
        divisor = (60 * 60 * 24) / time_granularity_seconds
        print("times_julian[0]:"+str(times_julian[0]))
        print("julianBaseDate = "+str(julian_base_date))
        print("timeGranularitySeconds = "+str(time_granularity_seconds))
        print("divisor = "+str(divisor))
        for j in range(len(times_julian)):
            times.append(datetime.fromtimestamp((times_julian[j] / divisor) + julian_base_date + 1))
        
        return times

# Example usage
delta = timedelta(minutes=55226880)
dt = datetime(1970,1,1) + delta
print(dt)
#converter = DateConverter()
#converted_times = converter.date_times_from_julian_array(times_julian, time_granularity_seconds, julian_base_date)
#print(converted_times)
