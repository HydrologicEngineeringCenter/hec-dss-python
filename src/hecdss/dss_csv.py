# THESE ARE ALL HELPER FUNCTIONS, MEANT TO BE TREATED AS PRIVATE. These functions are internally called in their respective classes.

import csv
import re
from datetime import datetime, timedelta

from .dsspath import DssPath
from .irregular_timeseries import IrregularTimeSeries
from .paired_data import PairedData
from .regular_timeseries import RegularTimeSeries


ROUND_PRECISION: int = 4
DEFAULT_MISSING_VALUE = None


def timeseries_to_csv(
    series: RegularTimeSeries | IrregularTimeSeries, path: str, with_metadata: bool
) -> None:
    """
    Exports a timeseries (either regular or irregular) to a .csv file.

    Parameters:
        series: The timeseries object to export. Must be either a RegularTimeSeries or IrregularTimeSeries
        path (str): The file path where the .csv file will be exported.
        with_metadata (bool): Whether to include metadata in the .csv file.
    """
    if not isinstance(series, (RegularTimeSeries, IrregularTimeSeries)):
        raise TypeError("series must be a RegularTimeSeries or IrregularTimeSeries")

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if with_metadata:
            id_components: dict[str, str] = _id_to_path_parts(series.id)
            for letter, value in id_components.items():
                if letter == 'D':  # Skip D by convention # ts pattern
                    if value == "ts-pattern":
                        print("Warning: ts-pattern skipped")
                    continue
                writer.writerow([letter, "", "", value])  # Writing metadata rows
            writer.writerow(["Units", "", "", series.units])
        if len(series.quality) > 0:
            # Write column names with quality
            writer.writerow(["Type", "Date/Time", series.data_type, "Quality"])
        else:
            # Write column names without quality
            writer.writerow(["Type", "Date/Time", series.data_type])

        time_format: str = ("%d%b%Y %H%M%S" if _needs_second_precision(series) else "%d%b%Y %H%M")

        ordinate: int = 1
        if len(series.quality) > 0:
            for time, value, quality in zip(series.times, series.values, series.quality):
                formatted_time: str = time.strftime(time_format)
                writer.writerow([ordinate, formatted_time, value, quality])
                ordinate += 1
        else:
            for time, value in zip(series.times, series.values):
                formatted_time: str = time.strftime(time_format)
                writer.writerow([ordinate, formatted_time, value])
                ordinate += 1


def timeseries_read_csv(cls: type[RegularTimeSeries] | type[IrregularTimeSeries], path: str) -> RegularTimeSeries | IrregularTimeSeries:
    """
    Reads a .csv file and builds a new timeseries of the given type.

    Parameters:
        cls: the class to build - either RegularTimeSeries or IrregularTimeSeries
        path (str): File path to .csv that we are reading from

    Returns:
        An instance of cls populated from the .csv file.
    """
    if cls not in (RegularTimeSeries, IrregularTimeSeries):
        raise TypeError("cls must be RegularTimeSeries or IrregularTimeSeries")

    times, values, quality, units, data_type = [], [], [], "", ""
    path_parts: dict[str, str] = _empty_path_parts()
    has_quality: bool = False  # flags

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            # first item in the row we grabbed, the first column's item
            first_column_item: str = row[0].strip()
            # If the first column item is a path component (['A', 'B', 'C', 'D', 'E', 'F'])
            if first_column_item in path_parts:
                path_parts[first_column_item] = row[-1].strip()  # last cell in csv row (convention)
            elif first_column_item == "Units":
                units = row[-1].strip()
            elif first_column_item == "Type":  # reached the header
                if len(row) >= 3:  # ['Type', 'Date/Time', data_type, ...potentially more]
                    data_type = row[2].strip()
                # ['Type', 'Date/Time', data_type, 'Quality', ...potentially more]
                if len(row) >= 4 and row[3].strip() == "Quality":
                    has_quality = True
            else:  # Data row
                if len(row) < 3:
                    continue  # csv is malformed, something is missing

                raw_time: str = row[1].strip()
                # Time format is determined by length of raw_time
                time_format: str = _get_time_format(raw_time)
                if time_format is None:
                    # Time format is unrecognized
                    continue

                # Do we need to roll over the day date? Yes if time is 2400
                roll_day: bool = _need_roll_day(time_format, raw_time)
                if roll_day:  # 2400 isn't a valid hour, so roll it to 0000 before parsing and add a day after
                    raw_time = raw_time.replace(" 2400", " 0000")

                try:
                    time: datetime = datetime.strptime(raw_time, time_format)
                except ValueError:
                    continue  # Skip a malformed date

                if roll_day:  # Convert a 24:00 time to 00:00 of the next day
                    time += timedelta(days=1)

                value_str: str = row[2].strip()
                try:
                    value: float = float(value_str) if value_str else DEFAULT_MISSING_VALUE
                except ValueError:
                    value: float = DEFAULT_MISSING_VALUE  # If datetime is valid but not value, use DEFAULT_MISSING_VALUE

                times.append(time)
                values.append(value)
                if has_quality:  # Always keep quality index-aligned with values, defaulting a missing cell to 0
                    quality_str: str = row[3].strip() if len(row) >= 4 else ""
                    try:
                        quality.append(int(quality_str) if quality_str else 0)
                    except ValueError:
                        quality.append(0)

    id_path: str = _path_parts_to_id(path_parts)
    interval: str | int = path_parts["E"]

    return cls.create(
        values=values,
        times=times,
        quality=quality,
        units=units,
        data_type=data_type,
        interval=interval,
        path=id_path,
    )


def paired_data_to_csv(paired_data: PairedData, path: str, with_metadata: bool) -> None:
    """
    Exports a PairedData object to a .csv file.

    Parameters:
        paired_data (PairedData): Paired Data object to convert to csv.
        path: (str): file path to export csv to.
        with_metadata (bool): whether or not to include metadata in the csv file.

    Returns:
        None
    """
    if not isinstance(paired_data, PairedData):
        raise TypeError("paired_data must be a PairedData!")

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if with_metadata:
            id_components: dict[str, str] = _id_to_path_parts(paired_data.id)
            for letter, value in id_components.items():
                if letter == 'D':  # Skipping D by convention
                    continue
                writer.writerow([letter, "", value])  # Writing metadata rows
            labels: list[str] = ["Labels", ""]
            for label in paired_data.labels:
                labels.append(label)
            writer.writerow(labels)
            writer.writerow(["Units", paired_data.units_independent, paired_data.units_dependent])
        writer.writerow(["Type", paired_data.type_independent, paired_data.type_dependent])

        counter: int = 1  # 1st column index
        x: float  # x is the same as "ordinate"
        y_row: list[float]  # Each y_row is one row of y_values, as paired_data.values is Row-Major
        for x, y_row in zip(paired_data.ordinates, paired_data.values):
            full_row: list[float] = [_round_or_none(x)] + \
                [_round_or_none(y) for y in y_row]
            writer.writerow([counter] + full_row)
            counter += 1
    return


def paired_data_read_csv(cls: type[PairedData], path: str) -> PairedData:
    """
    Reads a .csv file and builds a new paired data of the given type.

    Parameters:
        cls: the class to build - PairedData
        path (str): File path to .csv that we are reading from

    Returns:
        An instance of cls populated from the .csv file.
    """
    if cls is not PairedData:
        raise TypeError("cls must be PairedData")

    x_values: list[float] = []
    y_values: list[list[float]] = []
    labels: list[str] = []
    x_units: str = ""
    x_type: str = ""
    y_units: str = ""
    y_type: str = ""
    path_parts: dict[str, str] = _empty_path_parts()

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        row: list[str]
        for row in reader:
            if not row:
                continue
            # first item in the row we grabbed, the first column's item
            first_column_item: str = row[0].strip()
            # If the first column item is a path component (['A', 'B', 'C', 'D', 'E', 'F'])
            if first_column_item in path_parts:
                path_parts[first_column_item] = row[-1].strip()  # last cell in csv row (convention)
            elif first_column_item == "Labels":
                for label in row[2:]:  # First two elements of row are not labels
                    labels.append(label)
            elif first_column_item == "Units":
                if len(row) < 2:
                    continue
                x_units = row[1].strip()
                if len(row) < 3:
                    continue
                y_units = row[2].strip()  # If units change to a list, will have to update this
            elif first_column_item == "Type":
                if len(row) < 2:
                    continue
                x_type = row[1].strip()
                if len(row) < 3:
                    continue
                y_type = row[2].strip()  # If type changes to a list, will also have to update this
            else:  # Data row
                if len(row) < 3:
                    continue  # csv is malformed, something is missing
                x_str: str = row[1].strip()
                try:
                    x: float = float(x_str) if x_str else DEFAULT_MISSING_VALUE
                except ValueError:
                    x: float = DEFAULT_MISSING_VALUE
                x_values.append(x)

                y_row: list[float] = []
                y_row_str: list[str] = row[2:]
                y_str: str
                for y_str in y_row_str:
                    try:
                        y: float = float(y_str) if y_str else DEFAULT_MISSING_VALUE
                    except ValueError:
                        y: float = DEFAULT_MISSING_VALUE
                    y_row.append(y)
                y_values.append(y_row)

    id_path: str = _path_parts_to_id(path_parts)

    return cls.create(
        x_values=x_values,
        y_values=y_values,
        labels=labels,
        x_units=x_units,
        x_type=x_type,
        y_units=y_units,
        y_type=y_type,
        path=id_path,
    )


def _round_or_none(value: float | None) -> float | None:
    """
    Rounds a numeric value to ROUND_PRECISION, passing None through unchanged.

    Parameters:
        value (float | None): the value to round, or None if missing

    Returns:
        float | None: the rounded value, or None if value was None
    """
    return round(value, ROUND_PRECISION) if value is not None else None


def _empty_path_parts() -> dict[str, str]:
    """
    Returns a fresh dict of empty A-F DSS path components.

    Returns:
        dict[str, str]: mapping of each path part letter to an empty string
    """
    return {"A": "", "B": "", "C": "", "D": "", "E": "", "F": ""}


def _id_to_path_parts(dss_id: str | None) -> dict[str, str]:
    """
    Splits a DSS id string into its A-F components, or returns empties if id is missing.

    Parameters:
        dss_id (str | None): the DSS pathname to split, or None

    Returns:
        dict[str, str]: mapping of each path part letter to its value
    """
    if dss_id:
        return DssPath(dss_id).path_to_dict()
    return _empty_path_parts()


def _path_parts_to_id(path_parts: dict[str, str]) -> str:
    """
    Rebuilds a '/A/B/C/D/E/F/' DSS id string from its component dict.

    Parameters:
        path_parts (dict[str, str]): mapping of each path part letter to its value

    Returns:
        str: the reconstructed DSS pathname
    """
    return f"/{path_parts['A']}/{path_parts['B']}/{path_parts['C']}/{path_parts['D']}/{path_parts['E']}/{path_parts['F']}/"


def _needs_second_precision(series: RegularTimeSeries | IrregularTimeSeries) -> bool:
    """
    Returns True if any datetime in the series has a non-zero seconds component

    Parameters:
        series: must be either a RegularTimeSeries or IrregularTimeSeries

    Returns:
        bool: whether we need seconds precision or not
    """
    return any(getattr(t, "second", 0) != 0 for t in series.times)


def _get_time_format(raw_time: str) -> str | None:
    """
    Given a raw DSS time string, detect and return the correct time format, whether it be minutes or seconds precision.

    Parameters:
        raw_time (str): time in DSS string format

    Returns:
        str | None: time format to use to convert to datetime 
    """
    dss_minutes_pattern: str = r"^\d{2}[A-Z][a-z]{2}\d{4} \d{4}$"
    dss_seconds_pattern: str = r"^\d{2}[A-Z][a-z]{2}\d{4} \d{6}$"

    if re.fullmatch(dss_minutes_pattern, raw_time):
        return "%d%b%Y %H%M"
    elif re.fullmatch(dss_seconds_pattern, raw_time):
        return "%d%b%Y %H%M%S"
    else:
        return None


def _need_roll_day(time_format: str, raw_time: str) -> bool:
    """
    Primarily to deal with the DSS time sometimes being "2400" and needing to roll over.

    Parameters:
        time_format (str): time format being used
        raw_time (str): raw time string extracted from csv

    Returns: 
        bool: whether or not we need to roll over to the next day
    """
    if time_format != r"%d%b%Y %H%M" and time_format != r"%d%b%Y %H%M%S":
        return False  # Only DSS formats can return True

    # This should correctly catch if we need to roll day
    roll_day_pattern: str = r"^\d{2}[A-Z][a-z]{2}\d{4} 2400(00)?$"

    if re.fullmatch(roll_day_pattern, raw_time):
        return True

    return False
