from enum import Enum

class RecordType(Enum):
    Unknown = 0
    RegularTimeSeriesProfile = 1
    RegularTimeSeries = 2
    IrregularTimeSeries = 3
    PairedData = 4
    Text = 5
    Grid = 6
    Tin = 7
    LocationInfo = 8

    @staticmethod
    def RecordTypeFromInt(recType):
        rval = RecordType.Unknown

        if 100 <= recType < 110:
            if recType == 102 or recType == 107:
                rval = RecordType.RegularTimeSeriesProfile
            else:
                rval = RecordType.RegularTimeSeries
        elif 110 <= recType < 200:
            rval = RecordType.IrregularTimeSeries
        elif 200 <= recType < 300:
            rval = RecordType.PairedData
        elif 300 <= recType < 400:
            rval = RecordType.Text
        elif 400 <= recType < 450:
            rval = RecordType.Grid
        elif recType == 450:
            rval = RecordType.Tin
        elif recType == 20:
            rval = RecordType.LocationInfo

        return rval
