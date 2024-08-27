from .dateconverter import DateConverter
from .dss_type import DssType
from .record_type import RecordType


class DssPath:
    """Manage parts of DSS path /A/B/C/D/E/F/ 
    condenses D part for timeseries records
    """

    _timeSeriesFamily = [RecordType.IrregularTimeSeries, RecordType.RegularTimeSeries,
                         RecordType.RegularTimeSeriesProfile]

    def __init__(self, path: str, recType = 0):
        """
        path is raw dss pathname
        recType is a RecordType , such as RecordType.RegularTimeSeries
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
        return str(self) == str(other)

    def __str__(self):
        return "/" + self.A + "/" + self.B + "/" + self.C + "/" + self.D + "/" + self.E + "/" + self.F + "/"

    def path_without_date(self):
        s = "/" + self.A + "/" + self.B + "/" + self.C + "//" + self.E + "/" + self.F + "/"
        rval = DssPath(s, self.recType)
        return rval

    def is_time_series(self):
        return self.recType in DssPath._timeSeriesFamily

    def print(self):
        print("a:" + self.path.A)
        print("b:" + self.path.B)
        print("c:" + self.path.C)
        print("d:" + self.path.D)
        print("e:" + self.path.E)
        print("f:" + self.path.F)

