from .record_type import RecordType
from .dsspath import DssPath
from datetime import datetime
import re

class Catalog:
    """manage list of objects inside a DSS database"""
    def __init__(self, uncondensed_paths, recordTypes):
        self.uncondensed_paths = uncondensed_paths
        self.rawRecordTypes = recordTypes
        self.timeSeriesDictNoDates = {}  # key is path without date, value is a list of dates
        self.recordTypeDict = {} # key is path w/o date, value is recordType
        self.__create_condensed_catalog()

    def get_record_type(self, pathname):
        """gets the record type for a given path

                Args:
                    pathname (str): dss pathname

                Returns:
                    RecordType: the record type :class:`hecdss.RecordType` of DSS data stored in this pathname
                """
        if pathname.lower() in self.recordTypeDict:
            rt = self.recordTypeDict[pathname.lower()]
        else:
            path = DssPath(pathname, RecordType.Unknown)
            if( path.path_without_date().__str__().lower() in self.recordTypeDict):
                rt = self.recordTypeDict[path.path_without_date().__str__().lower()]
            else:
                rt = self.recordTypeDict[path.path_location_info().__str__().lower()]
        return rt

    def __create_condensed_catalog(self):
        """
          condensed catalog combines time-series records into a single condensed path
          other record types are not condensed.
          time-series records must match all parts except the D (date) part to be combined.
        """
        self.items = []
        raw_paths = {}
        for i in range(len(self.uncondensed_paths)):
            rawPath = self.uncondensed_paths[i]
            recordType = RecordType.RecordTypeFromInt(self.rawRecordTypes[i])
            path = DssPath(rawPath,recordType)
            # if timeseries - accumulate dates within a dataset
            if path.is_time_series():
                cleanPath = str(path.path_without_date())
                raw_paths[cleanPath.lower()] = rawPath
                self.recordTypeDict[cleanPath.lower()] = recordType
                if re.match(r"^\d{2}[A-Za-z]{3}\d{4}$", path.D):  # Check if path.D matches the format 'DDMMMYYYY'
                    tsRecords = self.timeSeriesDictNoDates.setdefault(cleanPath.lower(), [])
                    t = datetime.strptime(path.D,"%d%b%Y")
                    tsRecords.append(t)
            elif recordType in [RecordType.PairedData, RecordType.Grid, RecordType.Text,
                                RecordType.LocationInfo, RecordType.Array]:
                raw_paths[rawPath] = rawPath
                self.recordTypeDict[str(path).lower()] = recordType
                self.items.append(path)
            else:
                raise Exception(f"unsupported record_type: {recordType}")



        # go through each timeSeriesDictNoDates, and sort each list of dates
        # use first and last to create the condensed path 
        for key in self.timeSeriesDictNoDates.keys():
            dateList = sorted(self.timeSeriesDictNoDates[key])
            condensedDpart = dateList[0].strftime("%d%b%Y")
            if len(dateList) >1:
                condensedDpart +="-"+ dateList[-1].strftime("%d%b%Y")
            # insert condensed D part into path used as key
            rt = self.recordTypeDict[key]
            p = DssPath(raw_paths[key],rt)
            p.D = condensedDpart
            self.items.append(p)

    def print(self):
        for ds in self.items:
            print(ds)

    def __iter__(self):
        self.index = 0  # Initialize the index to 0
        return self

    def __next__(self):
        if self.index < len(self.items):
            result = self.items[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration
