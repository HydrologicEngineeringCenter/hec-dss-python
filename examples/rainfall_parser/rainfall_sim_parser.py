import warnings

from DssWriter import DssWriter

warnings.filterwarnings("ignore", category=DeprecationWarning)

from datetime import datetime, timedelta
import pandas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

def plot_data_frames(data_frames, labels, markers, title, ylabel):
    # Plot the data frames
    for df, label, marker in zip(data_frames, labels, markers):
        for column in df.columns:
            plt.plot(df.index, df[column], label=label, marker=marker)

    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.legend()
    plt.show()


def extract_raw_timeseries(df, site_id, year, plot_number, condition, column_name):
    """
    reads timeseries data from a subset of the input data
    The input data column 'Time' is fractional number of minutes
    The time 'overflows' each minute, that is detected with either
     a zero value or decreasing from previous value
    """
    filtered_data = df[(df["Site ID"] == site_id) & (df["Year"] == year)
                       & (df["Plot number"] == plot_number)
                       & (df["Condition"].str.strip() == condition)
                       ].reset_index(drop=True)

    rows = []
    prev_row = None
    extra_t = 0  # used to accumulate minutes, when the fractional minutes 'Time' column resets with 0
    delta_t = 0
    for _, row in filtered_data.iterrows():
        year = row['Year']
        month = row['Month']
        day = row['Day']
        time = row['Time']
        if prev_row is not None:
            delta_t = time - prev_row['Time']
        # minute_overflow = prev_row is not None and delta_t < 0

        if delta_t < 0:
            extra_t = extra_t + 60

        date = datetime(year=int(year), month=int(month), day=int(day))
        t = date + timedelta(minutes=time + extra_t)

        prev_row = row
        rows.append([t, row[column_name]])
        # print(f"{t},{row['Precipitation (mm/hr)']},{row['Runoff (mm/hr)']}")
    out = pandas.DataFrame(rows, columns=['timestamp', column_name])
    out.set_index('timestamp', inplace=True)
    return out


def filter_out_timesteps_less_than_1minute(df):
    # Calculate time difference between consecutive rows
    df['time_diff'] = df['timestamp'].diff()
    # Filter out rows with time steps less than 1 minute
    df_filtered = df[df['time_diff'] >= pandas.Timedelta(minutes=1)]
    # Drop the 'time_diff' column if not needed
    df_filtered = df_filtered.drop(columns=['time_diff'])
    return df_filtered


def condition_timeseries_to_precip(df):
    """
    condition_timeseries_to_precip inserts extra data points to
    avoid incorrectly interpolating across steady-state gaps in the data.

    insert zero precip values 1-minute before precip resumes (after period of zero-precip)
    insert previous precip value 1-minute before precip stops (after period of non-zero precip)
    """
    data_column = df.columns[0]
    modified_df = df.copy()  # Create a copy of the input DataFrame
    prev_row = None

    for t, row in df.iterrows():

        have_prev_precip = prev_row is not None and prev_row[data_column] != 0
        precip_stopped = row[data_column] == 0 and have_prev_precip
        precip_started = prev_row is not None and row[data_column] != 0 and prev_row[data_column] == 0
        more_than_1minute_gap = prev_row is not None and t - prev_row.name > timedelta(minutes=1)

        if precip_started:
            print("precip started")

        if precip_stopped and more_than_1minute_gap:
            print(f"Found value 0 at time: {t}, previous precip = {prev_row[data_column]}")
            new_time = t - timedelta(minutes=1)
            new_entry = prev_row.copy()
            modified_df.loc[new_time] = new_entry
        elif precip_started and more_than_1minute_gap:
            print(f"precip started with {row[data_column]}, at time: {t}, previous precip = {prev_row[data_column]}")
            new_time = t - timedelta(seconds=15)
            modified_df.loc[new_time] = 0

        prev_row = row

    modified_df.sort_index(inplace=True)
    return modified_df


def interpolate_1minute_timeseries(df):
    # df2 = df[~df.index.duplicated()]
    s = df.resample('1min').ffill()
    return s


def generate_1minute_precip(filename, siteid, plot_number, year, condition,dss_filename):
    output_filename = f"{siteid}_plot_{plot_number}_{year}_{condition}.csv"
    series_name = 'Precipitation (mm/hr)'
    units = re.findall(r'\((.*?)\)', series_name)[0]
    series_name_min = 'Precipitation (mm/min)'

    data = pandas.read_csv(filename)
    data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    raw_ts = extract_raw_timeseries(data, siteid, year, plot_number, condition, series_name)
    # print(raw_ts.to_string())
    print(f"raw data has {raw_ts.size} rows")
    # detect precipitation going off - (use previous precipitation one minute prior to zero )
    # insert values to enhance interpolation
    ts_conditioned = condition_timeseries_to_precip(raw_ts)
    # ts_conditioned.to_csv('conditioned.csv')
    # plot_data_frames([raw_ts, ts_conditioned],["raw","conditioned"],['o','x',],"tst")
    ts_1minute = interpolate_1minute_timeseries(ts_conditioned)
    # print(ts_1minute.to_string())
    title = f"{siteid} {year} plot number:{plot_number} condition:{condition} "
    plot_data_frames([raw_ts, ts_conditioned, ts_1minute], ["raw", "conditioned", "1minute"], ['o', 'x', '*'], title,units)
    # convert from mm/hour to mm/minute
    ts_1minute[series_name] = ts_1minute[series_name] / 60
    ts_1minute = ts_1minute.rename(columns={series_name: series_name_min})
    #ts_1minute.to_csv(output_filename)
    path = f"/{siteid}/{condition}{plot_number}-{year}/Precip//1Minute/USDA Walnut Gulch/"
    dss = DssWriter(dss_filename)
    dss.write_to_dss(ts_1minute,path)


f = 'rainfall_sim.csv'
dssf = 'rain_sim.dss'
generate_1minute_precip(filename=f, siteid='Wi', plot_number=1, year=2006, condition='B',dss_filename=dssf)

# generate_1minute_precip(filename=f, siteid='Ab', plot_number=2, year=2004, condition='N',dss_filename=dssf)
# generate_1minute_precip(filename=f, siteid='Ab', plot_number=2, year=2004, condition='B',dss_filename=dssf)
# generate_1minute_precip(filename=f, siteid='Ab', plot_number=3, year=2004, condition='N',dss_filename=dssf)
# generate_1minute_precip(filename=f, siteid='Ab', plot_number=3, year=2004, condition='B',dss_filename=dssf)
