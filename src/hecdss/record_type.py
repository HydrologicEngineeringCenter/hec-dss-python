from enum import Enum

class RecordType(Enum):
    """ RecordType is an enumeration of DSS data types

    Returns:
        RecordType: the record type
    """
    Unknown = 0
    RegularTimeSeriesProfile = 1
    RegularTimeSeries = 2
    IrregularTimeSeries = 3
    PairedData = 4
    Text = 5
    Grid = 6
    Tin = 7
    LocationInfo = 8
    Array = 9

    SUPPORTED_RECORD_TYPES = [
        "IrregularTimeSeries",
        "RegularTimeSeries",
        "PairedData",
        "GriddedData",
        "ArrayContainer",
    ]

    @staticmethod
    def RecordTypeFromInt(recType):
        """
        Returns RecordType Enumeration from integer value
        """
        rval = RecordType.Unknown

        if 90 <= recType <= 93 :
            rval = RecordType.Array
        elif 100 <= recType < 110:
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
