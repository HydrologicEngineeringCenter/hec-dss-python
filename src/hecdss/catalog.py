from .record_type import RecordType
from .dsspath import DssPath
from datetime import datetime

class Catalog:
    """manage list of objects inside a DSS database"""
    def __init__(self, items, recordTypes):
        self.rawCatalog = items
        self.rawRecordTypes = recordTypes
        self.timeSeriesDictNoDates = {}  # key is path without date, value is a list dates
        self.recordTypeDict = {} # key is path w/o date, value is recordType
        self.__create_condensed_catalog()
 
    def __create_condensed_catalog(self):
        """
          condensed catalog combines time-series records into a single condensed path
          other record types are not condensed.
          time-series records must match all parts except the D (date) part to be combined.
        """
        self.items = []
        for i in range(len(self.rawCatalog)):
            rawPath = self.rawCatalog[i]
            recordType = RecordType.RecordTypeFromInt(self.rawRecordTypes[i])
            path = DssPath(rawPath,recordType)
            # if timeseries - accumulate dates within a dataset
            if path.is_time_series():
                cleanPath = str(path.path_without_date())
                self.recordTypeDict[cleanPath] = recordType
                tsRecords = self.timeSeriesDictNoDates.setdefault(cleanPath,[])
                t = datetime.strptime(path.D,"%d%b%Y")
                tsRecords.append(t)
            elif recordType == RecordType.PairedData:
                cleanPath = str(path)
                self.recordTypeDict[cleanPath] = recordType
                # add NON time-series to list (nothing else needed)
                self.items.append(path)
            elif recordType == RecordType.Grid:
                cleanPath = str(path)
                self.recordTypeDict[cleanPath] = recordType
                # add NON time-series to list (nothing else needed)
                self.items.append(path)
            else:
                Exception(f"unsupported record_type: {recordType}")



        # go through each timeSeriesDictNoDates, and sort each list of dates
        # use first and last to create the condensed path 
        for key in self.timeSeriesDictNoDates:
            dateList = sorted(self.timeSeriesDictNoDates[key])
            condensedDpart = dateList[0].strftime("%d%b%Y")
            if len(dateList) >1:
                condensedDpart +="-"+ dateList[-1].strftime("%d%b%Y")
            # insert condensed D part into path used as key
            rt = self.recordTypeDict[key]
            p = DssPath(key,rt)
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
