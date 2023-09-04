from record_type import RecordType
from dsspath import DssPath
from datetime import datetime

class Catalog:
    """manage list of objects inside a DSS database"""
    def __init__(self, items, recordTypes):
        self.rawCatalog = items
        self.rawRecordTypes = recordTypes
        self.timeSeriesDictNoDates = {}  # key is path without date, value is a list of paths with dates that match
        self.dataSets = self.__create_condensed_catalog()
 
    def __create_condensed_catalog(self):
        """
          condensed catalog combines time-series records into a single condensed path
          other record types are not condensed.
          time-series records must match all parts except the D (date) part to be combined.
        """
        rval = []
        for i in range(len(self.rawCatalog)):
            rawPath = self.rawCatalog[i]
            recordType = RecordType.RecordTypeFromInt(self.rawRecordTypes[i])
            path = DssPath(rawPath,recordType)

            # if timeseries - check for existing path to combine with
            if path.isTimeSeries():
                cleanPath = path.pathWithoutDate()
                tsRecords = self.timeSeriesDictNoDates.setdefault(cleanPath,[])
                t = datetime.strptime(path.D,"%d%b%Y")
                tsRecords.append(t)
            else: 
                # add NON time-series to list (nothing else needed)
                rval.append(path) 

        # go through each timeSeriesDictNoDates, and sort each list of dates
        # use first and last to create the condensed path 
        for key in self.timeSeriesDictNoDates:
            dateList = sorted(self.timeSeriesDictNoDates[key])
            condensedDpart = dateList[0].strftime("%d%b%Y")
            if len(dateList) >1:
                print(f"len(dateList)={len(dateList)}")
                condensedDpart +="-"+ dateList[-1].strftime("%d%b%Y")
            # insert condensed D part into path used as key
            #print(key)
            #print(type(key))
            p = DssPath(str(key),key.recType)
            p.D = condensedDpart
            print(p)
        return rval
    
    def print(self):
        for ds in self.dataSets:
            print(ds)

    
