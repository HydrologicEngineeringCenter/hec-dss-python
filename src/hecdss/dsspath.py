import logging
from .dateconverter import DateConverter
from .dss_type import DssType
from .record_type import RecordType

# Get logger for this module
logger = logging.getLogger(__name__)

class DssPath:
    """
    Manage parts of DSS path /A/B/C/D/E/F/
    condenses D part for timeseries records
    """

    _timeSeriesFamily = [RecordType.IrregularTimeSeries, RecordType.RegularTimeSeries,
                         RecordType.RegularTimeSeriesProfile]

    def __init__(self, path: str, recType = 0):
        """
        Initialize a DssPath object.

        Args:
            path (str): Raw DSS pathname.
            recType (RecordType, optional): Type of the record, such as RecordType.RegularTimeSeries. Defaults to 0.

        Raises:
            Exception: If the DSS path is invalid.
        """
        # path should be at least 7 slash characters ///////
        if len(path.strip()) < 7 or path[0] != '/' or path[-1] != '/':
            raise Exception("Invalid DSS Path: '" + path + "'")
        path = path[1:-1]  # remove beginning and ending '/'
        # self.rawPath= path

        split_parts = path.split('/')
        if len(split_parts) >= 6:
            self.A, self.B, self.C, self.D, self.E, self.F = split_parts[:6]
        self.recType = recType

    def __eq__(self, other):
        """
        Check if two DssPath objects are equal.

        Args:
            other (DssPath): Another DssPath object to compare with.

        Returns:
            bool: True if both DssPath objects are equal, False otherwise.
        """
        return str(self) == str(other)

    def __str__(self):
        """
        Returns:
            str: The DSS path as a string.
        """
        return "/" + self.A + "/" + self.B + "/" + self.C + "/" + self.D + "/" + self.E + "/" + self.F + "/"

    def path_without_date(self):
        """
        Get the DSS path without the date part (D part).

        Returns:
            DssPath: A new DssPath object without the date part.
        """
        s = "/" + self.A + "/" + self.B + "/" + self.C + "//" + self.E + "/" + self.F + "/"
        rval = DssPath(s, self.recType)
        return rval

    def path_location_info(self):
        s = "/" + self.A + "/" + self.B + "/" + self.C + "////"
        rval = DssPath(s, self.recType)
        return rval

    def is_time_series(self):
        """
        Check if the DSS path is a time series.

        Returns:
            bool: True if the DSS path is a time series, False otherwise.
        """
        return self.recType in DssPath._timeSeriesFamily

    def print(self):
        """
        Print the parts of the DSS path to stdout.
        """
        print("a:" + self.A)
        print("b:" + self.B)
        print("c:" + self.C)
        print("d:" + self.D)
        print("e:" + self.E)
        print("f:" + self.F)

    def log_path(self, level=logging.INFO):
        """Log the DSS path parts at the specified logging level.

        Args:
            level: Logging level (default: logging.INFO)
        """
        logger.log(level, "DssPath: %s", str(self))
        logger.log(level, "  A (Group/Project/Watershed): %s", self.A)
        logger.log(level, "  B (Location): %s", self.B)
        logger.log(level, "  C (Parameter): %s", self.C)
        logger.log(level, "  D (Block Start Date/Time): %s", self.D)
        logger.log(level, "  E (Time Interval/Block Length): %s", self.E)
        logger.log(level, "  F (Descriptor): %s", self.F)