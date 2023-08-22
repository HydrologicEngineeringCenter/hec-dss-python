from datetime import datetime, timedelta

class DateConverter:
    @staticmethod
    def date_times_from_julian_array(times_julian, time_granularity_seconds, julian_base_date):
        if times_julian is None:
            raise ValueError("Time Series Times array was None. Something didn't work right in DSS.")
        
        times = []
        divisor = (60 * 60 * 24) / time_granularity_seconds
        
        for j in range(len(times_julian)):
            # There appears to be an off-by-1-day error common to julian dates - DEC 1899 vs JAN 1900
            times.append(datetime.fromtimestamp((times_julian[j] / divisor) + julian_base_date + 1))
        
        return times

# Example usage
times_julian = [2451234, 2451235, 2451236]
time_granularity_seconds = 86400
julian_base_date = 2415020

converter = DateConverter()
converted_times = converter.date_times_from_julian_array(times_julian, time_granularity_seconds, julian_base_date)
print(converted_times)
