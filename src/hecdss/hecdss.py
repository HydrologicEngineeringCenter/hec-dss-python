"""Docstring for public module."""
import numpy as np

from hecdss.paired_data import PairedData
from hecdss.native import _Native
from hecdss.dateconverter import DateConverter
from hecdss.record_type import RecordType
from hecdss.timeseries import TimeSeries
from hecdss.catalog import Catalog
from hecdss.gridded_data import GriddedData


class HecDss:
    def __init__(self, filename):
        self._native = _Native()
        self._native.hec_dss_open(filename)
        self._catalog = None

    def close(self):
        self._native.hec_dss_close()

    def get_record_type(self,pathname):

        if not self._catalog:
          self._catalog = self.get_catalog()

        rt = self._catalog.recordTypeDict[pathname]
        # print(f"hec_dss_recordType for '{pathname}' is {rt}")
        # TODO do native call.
        # rt = self._native.hec_dss_recordType(pathname)
        # print(f"hec_dss_recordType for '{pathname}' is {rt}")
        return rt

    def get(self, pathname, startdatetime=None, enddatetime=None):
        type = self.get_record_type(pathname)

        if type == RecordType.RegularTimeSeries:
            return self._get_timeseries(pathname, startdatetime, enddatetime)
        elif type == RecordType.PairedData:
            return self._get_paired_data(pathname)
            # read paired data
        elif type == RecordType.Grid:
            return self._get_gridded_data(pathname)
        return

    def _get_gridded_data(self, pathname):
        gridType = [0]
        dataType = [0]
        lowerLeftCellX = [0]
        lowerLeftCellY = [0]
        numberOfCellsX = [0]
        numberOfCellsY = [0]
        numberOfRanges = [0]
        srsDefinitionType = [0]
        timeZoneRawOffset = [0]
        isInterval = [0]
        isTimeStamped = [0]
        dataUnits = [""]
        dataSource = [""]
        srsName = [""]
        srsDefinition = [""]
        timeZoneID = [""]
        cellSize = [0.0]
        xCoordOfGridCellZero = [0.0]
        yCoordOfGridCellZero = [0.0]
        nullValue = [0.0]
        maxDataValue = [0.0]
        minDataValue = [0.0]
        meanDataValue = [0.0]
        rangeLimitTable = []
        numberEqualOrExceedingRangeLimit = []
        data = []

        status = self._native.hec_dss_gridRetrieve(
            pathname=pathname,
            gridType=gridType,
            dataType=dataType,
            lowerLeftCellX=lowerLeftCellX,
            lowerLeftCellY=lowerLeftCellY,
            numberOfCellsX=numberOfCellsX,
            numberOfCellsY=numberOfCellsY,
            numberOfRanges=numberOfRanges,
            srsDefinitionType=srsDefinitionType,
            timeZoneRawOffset=timeZoneRawOffset,
            isInterval=isInterval,
            isTimeStamped=isTimeStamped,
            dataUnits=dataUnits,
            dataSource=dataSource,
            srsName=srsName,
            srsDefinition=srsDefinition,
            timeZoneID=timeZoneID,
            cellSize=cellSize,
            xCoordOfGridCellZero=xCoordOfGridCellZero,
            yCoordOfGridCellZero=yCoordOfGridCellZero,
            nullValue=nullValue,
            maxDataValue=maxDataValue,
            minDataValue=minDataValue,
            meanDataValue=meanDataValue,
            rangeLimitTable=rangeLimitTable,
            numberEqualOrExceedingRangeLimit=numberEqualOrExceedingRangeLimit,
            data=data,
            # dataLength=0,
            # dataUnitsLength=40,
            # dataSourceLength=40,
            # srsNameLength=40,
            # srsDefinitionLength=40,
            # timeZoneIDLength=40,
            # rangeTablesLength=40,
        )

        if status != 0:
            print(f"Error reading gridded-data from '{pathname}'")
            return None

        gd = GriddedData()
        gd.type = gridType[0]
        gd.dataType = dataType[0]
        gd.lowerLeftCellX = lowerLeftCellX[0]
        gd.lowerLeftCellY = lowerLeftCellY[0]
        gd.numberOfCellsX = numberOfCellsX[0]
        gd.numberOfCellsY = numberOfCellsY[0]
        gd.numberOfRanges = numberOfRanges[0]
        gd.srsDefinitionType = srsDefinitionType[0]
        gd.timeZoneRawOffset = timeZoneRawOffset[0]
        gd.isInterval = isInterval[0]
        gd.isTimeStamped = isTimeStamped[0]
        gd.dataUnits = dataUnits[0]
        gd.dataSource = dataSource[0]
        gd.srsName = srsName[0]
        gd.srsDefinition = srsDefinition[0]
        gd.timeZoneID = timeZoneID[0]
        gd.cellSize = cellSize[0]
        gd.xCoordOfGridCellZero = xCoordOfGridCellZero[0]
        gd.yCoordOfGridCellZero = yCoordOfGridCellZero[0]
        gd.nullValue = nullValue[0]
        gd.maxDataValue = maxDataValue[0]
        gd.minDataValue = minDataValue[0]
        gd.meanDataValue = meanDataValue[0]
        gd.rangeLimitTable = rangeLimitTable
        gd.numberEqualOrExceedingRangeLimit = numberEqualOrExceedingRangeLimit
        # gd.data = [[data[(i*numberOfCellsX[0])+j] for j in range(numberOfCellsX[0])] for i in range(numberOfCellsY[0])]
        gd.data = np.array(data).reshape((numberOfCellsX[0], numberOfCellsY[0]))
        gd.id = pathname

        return gd

    def _get_paired_data(self, pathname):
        numberOrdinates = [0]
        numberCurves = [0]
        unitsIndependent  =[""]
        unitsDependent = [""]
        typeIndependent = [""]
        typeDependent =[""]
        labelsLength =[0]
        self._native.hec_dss_pdRetrieveInfo(
            pathname,
            numberOrdinates,
            numberCurves,
            unitsIndependent,
            unitsDependent,
            typeIndependent,
            typeDependent,
            labelsLength
        )
        # print("Number of Ordinates:", numberOrdinates[0])
        # print("Number of Curves:", numberCurves[0])
        # print("length of labels:", labelsLength[0])

        doubleOrdinates = []
        doubleValues = []
        labels = []
        # suffix of '2' so w don't info from calling hec_dss_pdRetrieveInfo
        numberOrdinates2 = [0]
        numberCurves2 = [0]
        unitsIndependent2 = [""]
        unitsDependent2 = [""]
        typeIndependent2 = [""]
        typeDependent2 = [""]
        status = self._native.hec_dss_pdRetrieve(pathname,
                                        doubleOrdinates,numberOrdinates[0],
                                        doubleValues,numberCurves[0]*numberOrdinates[0],
                                        numberOrdinates2,numberCurves2,
                                        unitsIndependent2,len(unitsIndependent[0])+1,
                                        typeIndependent2,len(typeIndependent[0])+1,
                                        unitsDependent2,len(unitsDependent[0])+1,
                                        typeDependent2,len(typeDependent[0])+1,
                                        labels, labelsLength[0])

        if status != 0:
            print(f"Error reading paired-data from '{pathname}'")
            return None

        pd = PairedData()
        pd.ordinates = np.array(doubleOrdinates)

        n = numberCurves2[0].value
        pd.values = np.array(doubleValues).reshape((len(doubleOrdinates), n))
        # pd.values = [doubleValues[i:i+n] for i in range(0, len(doubleValues), n)]
        pd.labels = labels
        pd.type_independent = typeIndependent2[0]
        pd.type_dependent = typeDependent2[0]
        pd.units_independent = unitsIndependent2[0]
        pd.units_dependent = unitsDependent2[0]
        pd.id = pathname

        return pd

    def _get_timeseries(self,pathname,startDateTime,endDateTime):
        # get sizes
        if not (startDateTime and endDateTime):
            startDate = ""
            startTime = ""
            endDate = ""
            endTime = ""
        else:
            startDate = startDateTime.strftime("%d%b%Y")
            startTime = startDateTime.strftime("%H:%M")
            endDate = endDateTime.strftime("%d%b%Y")
            endTime = endDateTime.strftime("%H:%M")
        numberValues = [0]  # using array to allow modification
        qualityElementSize = [0]
        self._native.hec_dss_tsGetSizes(
            pathname,
            startDate,
            startTime,
            endDate,
            endTime,
            numberValues,
            qualityElementSize,
        )
        # print("Number of values:", numberValues[0])
        # print("Quality element size:", qualityElementSize[0])

        # tsRetrive

        times = [0]
        values = []
        numberValuesRead = [0]
        quality = []
        julianBaseDate = [0]
        timeGranularitySeconds = [0]
        units = [""]
        bufferLength = 40
        dataType = [""]

        status = self._native.hec_dss_tsRetrieve(
            pathname,
            startDate,
            startTime,
            endDate,
            endTime,
            times,
            values,
            numberValues[0],
            numberValuesRead,
            quality,
            qualityElementSize[0],
            julianBaseDate,
            timeGranularitySeconds,
            units,
            bufferLength,
            dataType,
            bufferLength,
        )

        # print("units = "+units[0])
        # print("datatype = "+dataType[0])
        # print("times: ")
        # print(times)
        # print(values)
        # print("julianBaseDate = " + str(julianBaseDate[0]))
        # print("timeGranularitySeconds = " + str(timeGranularitySeconds[0]))
        ts = TimeSeries()
        ts.times = DateConverter.date_times_from_julian_array(
            times, timeGranularitySeconds[0], julianBaseDate[0]
        )
        ts.values = np.array(values)
        ts.units = units[0]
        ts.dataType = dataType[0]
        ts.id = pathname
        return ts

    def put(self, container):
        # TO DO.. save other types besides regular interval.
        # TO DO. check data type..
        # TO Do. is timezone needed?
        status = 0
        if type(container) is TimeSeries:
            ts = container
            # def hec_dss_tsStoreRegular(dss, pathname, startDate, startTime, valueArray, qualityArray,
            #                           saveAsFloat, units, type):
            startDate, startTime = DateConverter.dss_datetime_from_string(ts.times[0])
            quality = []  # TO DO

            status = self._native.hec_dss_tsStoreRegular(
                ts.id,
                startDate,
                startTime,
                ts.values,
                quality,
                False,
                ts.units,
                ts.dataType,
            )
            self._catalog = None

        elif type(container) is PairedData:
            pd = container
            # print(pd)
            status = self._native.hec_dss_pdStore(pd)
            self._catalog = None
        elif type(container) is GriddedData:
            gd = container
            status = self._native.hec_dss_gridStore(gd)
            self._catalog = None
        else:
            Exception(f"unsupported record_type: {type(container)}")

        # TODO -- instead of invalidating catalog,with _catalog=None
        #  can we be smart?
        # TODO -- if we get smart, catalog has  recordTypeDict and timeSeriesDictNoDates
        # how about Catalog has method  catalog.notify_put(pathname,RecordType)
        #  and                          catalog.notify_delete(pathname, RecordType)
        # if not self._catalog is None:
        #     self._catalog.recordTypeDict[pd.id] = RecordType.PairedData

        return status

    def get_catalog(self):
        paths, recordTypes = self._native.hec_dss_catalog()
        return Catalog(paths, recordTypes)

    def record_count(self):
        return self._native.hec_dss_record_count()

    def set_debug_level(self, level):
        return self._native.hec_dss_set_debug_level(level)


if __name__ == "__main__":
    # import pdb;pdb.set_trace()
    dss = HecDss("sample7.dss")
    catalog = dss.get_catalog()
    for p in catalog:
        print(p)
    # print(catalog[0:5])
    # dss.set_debug_level(15)
