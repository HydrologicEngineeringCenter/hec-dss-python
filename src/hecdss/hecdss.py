"""Docstring for public module."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import numpy as np

import hecdss.record_type
from hecdss.array_container import ArrayContainer
from hecdss.location_info import LocationInfo
from hecdss.text import Text
from hecdss.paired_data import PairedData
from hecdss.native import _Native
from hecdss.dateconverter import DateConverter
from hecdss.record_type import RecordType
from hecdss.regular_timeseries import RegularTimeSeries
from hecdss.irregular_timeseries import IrregularTimeSeries
from hecdss.catalog import Catalog
from hecdss.gridded_data import GriddedData
from hecdss.dsspath import DssPath

DSS_UNDEFINED_VALUE = -340282346638528859811704183484516925440.000000


class HecDss:
    """ Main class for working with DSS files
    """
    def __init__(self, filename:str):
        """constructor for HecDSS

        Args:
            filename (str): DSS filename to be opened; it will be created if it doesn't exist.
        """

        self._native = _Native()
        self._native.hec_dss_open(filename)
        self._catalog = None
        self._filename = filename
        self._closed = False

    def __enter__(self):
        """
        Enter the runtime context related to this object.

        Returns:
            HecDss: The HecDss object itself.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context related to this object and close the DSS file.

        Args:
            exc_type (type): The exception type.
            exc_val (Exception): The exception instance.
            exc_tb (traceback): The traceback object.
        """
        self.close()
    @staticmethod
    def set_global_debug_level(level: int) -> None:
        """
        Sets the library debug level
        Args:
            level (int): HEC-DSS message level (0-15)
                0: No messages (not recommended)
                1: Critical errors only
                2: Terse output (errors + file operations)
                3: General log messages (default)
                4: User diagnostic messages
                5: Internal debug level 1 (not recommended for users)
                6: Internal debug level 2 (full debug)
                7-15: Extended debug levels
        """
        # Set the native DLL level (controls what gets written)
        _Native().hec_dss_set_debug_level(level)
    def close(self):
        """closes the DSS file and releases any locks
        """
        if not self._closed:
            self._native.hec_dss_close()
            self._closed = True

    def get_record_type(self, pathname: str) -> RecordType:
        """
        Get the record type for a given DSS pathname.

        Args:
            pathname (str): The DSS pathname for which to get the record type.

        Returns:
            RecordType: The record type of the given DSS pathname.
        """
        if not self._catalog:
            self._catalog = self.get_catalog()
        rt = self._catalog.get_record_type(pathname)

        # print(f"hec_dss_recordType for '{pathname}' is {rt}")
        # TODO do native call.
        # rt = self._native.hec_dss_recordType(pathname)
        # print(f"hec_dss_recordType for '{pathname}' is {rt}")
        return rt

    def get(self, pathname: str, startdatetime=None, enddatetime=None, trim=False):
        pathname = str(pathname)
        type = self.get_record_type(pathname)
        """gets various types of data from the current DSS file

        Args:
            pathname (str): dss pathname
            startdatetime (datetime): start date for query
            enddatetime (datetime): end date for the query

        Returns:
            varies: RegularTimeSeries, PairedData, Grid, or Array.
        """
        if type == RecordType.RegularTimeSeries or type == RecordType.IrregularTimeSeries:
            new_pathname = pathname
            if(DssPath(pathname).D.lower() != "ts-pattern"):
                new_pathname = DssPath(pathname).path_without_date().__str__()
            elif type == RecordType.IrregularTimeSeries:
                raise ValueError("ts-pattern is not fully supported for irregular time series")
            ts = self._get_timeseries(new_pathname, startdatetime, enddatetime, trim)
            return ts
        elif type == RecordType.PairedData:
            return self._get_paired_data(pathname)
            # read paired data
        elif type == RecordType.Grid:
            return self._get_gridded_data(pathname)
        elif type == RecordType.Array:
            return self._get_array(pathname)
        elif type == RecordType.LocationInfo:
            return self._get_location_info(pathname)
        elif type == RecordType.Text:
            return self._get_text(pathname)
        return None

    def _get_text(self, pathname: str):
        textLength = 1024


        BUFFER_TOO_SMALL = -17
        textArray = []
        status = self._native.hec_dss_textRetrieve(pathname, textArray, textLength)
        while status == BUFFER_TOO_SMALL:
            textLength *= 2
            if textLength > 2*1048576:  # 2 MB
                print(f"Text record too large to read from '{pathname}'")
                return None
            textArray = [] # otherwise we get an entry for each attempt
            status = self._native.hec_dss_textRetrieve(pathname, textArray, textLength)

        if status != 0:
            print(f"Error reading text from '{pathname}'")
            return None
        text = Text()
        text.id = pathname
        text.text = textArray[0]
        return text

    def _get_array(self, pathname: str):
        intValuesCount = [0]
        floatValuesCount = [0]
        doubleValuesCount = [0]

        self._native.hec_dss_arrayRetrieveInfo(pathname, intValuesCount, floatValuesCount, doubleValuesCount)

        intValues = []
        floatValues = []
        doubleValues = []

        if intValuesCount[0] > 0:
            intValues = [0] * intValuesCount[0]
        if floatValuesCount[0] > 0:
            floatValues = [0] * floatValuesCount[0]
        if doubleValuesCount[0] > 0:
            doubleValues = [0] * doubleValuesCount[0]

        status = self._native.hec_dss_arrayRetrieve(pathname, intValues, floatValues, doubleValues)
        location_info = self._get_location_info(pathname)
        rval = ArrayContainer.create_array_container(intValues, floatValues, doubleValues, path=pathname, location_info=location_info)
        return rval

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
        gd.data_type = dataType[0]
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
        gd.data = np.array(data).reshape((numberOfCellsY[0], numberOfCellsX[0]))
        gd.id = pathname
        gd.location_info = self._get_location_info(pathname)

        return gd

    def _get_paired_data(self, pathname):
        numberOrdinates = [0]
        numberCurves = [0]
        unitsIndependent = [""]
        unitsDependent = [""]
        typeIndependent = [""]
        typeDependent = [""]
        labelsLength = [0]
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
        timeZoneName = [""]
        timeZoneNameLength = [""]
        status = self._native.hec_dss_pdRetrieve(pathname,
                                                 doubleOrdinates, numberOrdinates[0],
                                                 doubleValues, numberCurves[0] * numberOrdinates[0],
                                                 numberOrdinates2, numberCurves2,
                                                 unitsIndependent2, len(unitsIndependent[0]) + 1,
                                                 typeIndependent2, len(typeIndependent[0]) + 1,
                                                 unitsDependent2, len(unitsDependent[0]) + 1,
                                                 typeDependent2, len(typeDependent[0]) + 1,
                                                 labels, labelsLength[0],
                                                 timeZoneName, len(timeZoneNameLength[0]) + 1)

        if status != 0:
            print(f"Error reading paired-data from '{pathname}'")
            return None

        pd = PairedData()
        pd.ordinates = np.array(doubleOrdinates)

        n = numberCurves2[0].value
        ordinateCount = len(doubleOrdinates)
        if n > 1:
            # ---------------------------------------------------------------------------------------- #
            # rearrange from consecutive values for each curve to consecutive curves for each ordinate #
            # ---------------------------------------------------------------------------------------- #
            groups = [doubleValues[i*ordinateCount:(i+1)*ordinateCount] for i in range(n)]
            doubleValues = list(map(list, zip(*groups)))
        pd.values = np.array(doubleValues).reshape((len(doubleOrdinates), n))
        # pd.values = [doubleValues[i:i+n] for i in range(0, len(doubleValues), n)]
        pd.labels = labels
        pd.type_independent = typeIndependent2[0]
        pd.type_dependent = typeDependent2[0]
        pd.units_independent = unitsIndependent2[0]
        pd.units_dependent = unitsDependent2[0]
        pd.time_zone_name = timeZoneName[0]
        pd.id = pathname
        pd.location_info = self._get_location_info(pathname)

        return pd

    def _get_julian_time_range(self, pathname, boolFullSet):
        firstValidJulian = [0]
        firstSeconds = [0]
        lastValidJulian = [0]
        lastSeconds = [0]
        status = self._native.hec_dss_tsGetDateTimeRange(
            pathname,
            boolFullSet,
            firstValidJulian,
            firstSeconds,
            lastValidJulian,
            lastSeconds
        )

        return (firstValidJulian, firstSeconds, lastValidJulian, lastSeconds)

    def _get_date_time_range(self, pathname, boolFullSet):

        firstValidJulian, firstSeconds, lastValidJulian, lastSeconds = self._get_julian_time_range(pathname, boolFullSet)

        first = DateConverter.date_times_from_julian_array(firstSeconds, 1, firstValidJulian[0])[0]
        last = DateConverter.date_times_from_julian_array(lastSeconds, 1, lastValidJulian[0])[0]

        return (first, last)


    def _get_timeseries(self, pathname, startDateTime, endDateTime, trim):
        # get sizes
        firstValidJulian, firstSeconds, lastValidJulian, lastSeconds = self._get_julian_time_range(pathname, 1)
        if startDateTime is None:
            _startDateTime = DateConverter.date_time_from_julian_second(firstValidJulian[0], firstSeconds[0])
            firstSeconds, firstJulian = firstSeconds, firstValidJulian
        else:
            _startDateTime = startDateTime
            minutes = DateConverter.julian_array_from_date_times([startDateTime])[0]
            firstSeconds, firstJulian = [minutes % 1440 * 60], [minutes // 1440]
        if endDateTime is None:
            _endDateTime =  DateConverter.date_time_from_julian_second(lastValidJulian[0], lastSeconds[0])
            lastSeconds, lastJulian = lastSeconds, lastValidJulian
        else:
            _endDateTime = endDateTime
            minutes = DateConverter.julian_array_from_date_times([endDateTime])[0]
            lastSeconds, lastJulian = [minutes % 1440 * 60], [minutes // 1440]

        startDate = _startDateTime.strftime("%d%b%Y")
        startTime = _startDateTime.strftime("%H:%M:%S")
        endDate = _endDateTime.strftime("%d%b%Y")
        endTime = _endDateTime.strftime("%H:%M:%S")

        numberValues = [0]  # using array to allow modification
        qualityElementSize = [0]
        status = self._native.hec_dss_tsGetSizes(
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

        number_periods = numberValues[0]
        if RecordType.RegularTimeSeries == self.get_record_type(pathname):
            dsspath = DssPath(pathname)
            interval_seconds = DateConverter.intervalString_to_sec(dsspath.E)

            number_periods = self._native.hec_dss_numberPeriods(
                interval_seconds,
                firstJulian[0],
                firstSeconds[0],
                lastJulian[0],
                lastSeconds[0],
            )

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
        timeZoneName = [""]

        status = self._native.hec_dss_tsRetrieve(
            pathname,
            startDate,
            startTime,
            endDate,
            endTime,
            times,
            values,
            number_periods+1,
            numberValuesRead,
            quality,
            qualityElementSize[0],
            julianBaseDate,
            timeGranularitySeconds,
            units,
            bufferLength,
            dataType,
            bufferLength,
            timeZoneName,
            bufferLength
        )

        # print("units = "+units[0])
        # print("datatype = "+dataType[0])
        # print("times: ")
        # print(times)
        # print(values)
        # print("julianBaseDate = " + str(julianBaseDate[0]))
        # print("timeGranularitySeconds = " + str(timeGranularitySeconds[0]))
        if RecordType.IrregularTimeSeries == self.get_record_type(pathname):
            ts = IrregularTimeSeries()
        else:
            ts = RegularTimeSeries()
            if trim or not startDateTime or not endDateTime:
                trimmed_indices = [i for i, v in enumerate(values) if values[i] != DSS_UNDEFINED_VALUE]
                if not trimmed_indices:
                    times = []
                    values = []
                    quality = []
                else:
                    start = 0 if startDateTime and not trim else trimmed_indices[0]
                    end = len(times) if endDateTime and not trim else trimmed_indices[-1]+1
                    times = times[start:end]
                    values = values[start:end]
                    if quality != []:
                        quality = quality[start:end]
        new_times = DateConverter.date_times_from_julian_array(
            times, timeGranularitySeconds[0], julianBaseDate[0]
        )
        arr = np.array(values)
        if RecordType.IrregularTimeSeries == type(ts):
            indices = np.where(np.isclose(values, DSS_UNDEFINED_VALUE, rtol=0, atol=0, equal_nan=True))[0]
            arr = np.delete(arr, indices)
            new_times = [new_times[i] for i in range(len(new_times)) if not np.isin(i, indices)]
            quality = [quality[i] for i in range(len(quality)) if not np.isin(i, indices)]

        values = arr
        units = units[0]
        data_type = dataType[0]
        start_date = [] if len(new_times) == 0 else new_times[0]
        time_granularity_seconds = timeGranularitySeconds[0]
        julian_base_date = julianBaseDate[0]
        timeZoneName = timeZoneName[0]
        if(timeZoneName):
            try:
                new_times = [i.replace(tzinfo=ZoneInfo(timeZoneName)) for i in new_times]
            except ZoneInfoNotFoundError as e: 
                print(f"Warning: {e}. Using no zone instead.")
                timeZoneName = False
        elif (DssPath(pathname).D.lower() == "ts-pattern"):
            new_times = []
            start_date = _startDateTime - timedelta(seconds=interval_seconds)

        location_info = self._get_location_info(pathname)
        ts = ts.create(values=values, times=new_times, quality=quality, units=units, data_type=data_type, start_date=start_date, time_granularity_seconds=time_granularity_seconds, julian_base_date=julian_base_date, time_zone_name=timeZoneName, path=pathname, location_info=location_info)

        if (DssPath(pathname).D.lower() == "ts-pattern"):
            new_interval = ts._get_interval_path()
            ts._interval_to_times(new_interval)

        return ts

    def _get_location_info(self, pathname: str):
        x = [0.0]
        y = [0.0]
        z = [0.0]
        coordinateSystem = [0]
        coordinateID = [0]
        horizontalUnits = [0]
        horizontalDatum = [0]
        verticalUnits = [0]
        verticalDatum = [0]
        timeZoneName = [""]
        supplemental = [""]

        timeZoneNameLength = 40
        supplementalLength = 256

        status = self._native.hec_dss_locationRetrieve(
            pathname,
            x,
            y,
            z,
            coordinateSystem,
            coordinateID,
            horizontalUnits,
            horizontalDatum,
            verticalUnits,
            verticalDatum,
            timeZoneName,
            timeZoneNameLength,
            supplemental,
            supplementalLength
        )

        if status != 0:
            # print("Function call failed with result:", status)
            return None

        location_info = LocationInfo.create(
            x_values=[x[0]],
            y_values=[y[0]],
            z_values=[z[0]],
            coordinate_system=coordinateSystem[0],
            coordinate_id=coordinateID[0],
            horizontal_units=horizontalUnits[0],
            horizontal_datum=horizontalDatum[0],
            vertical_units=verticalUnits[0],
            vertical_datum=verticalDatum[0],
            time_zone_name=timeZoneName[0],
            supplemental=supplemental[0],
            path=pathname
        )

        return location_info

    def put(self, container) -> int:
        """puts data into the DSS file

        Args:
            container (varies): RegularTimeSeries, IrregularTimeSeries, PairedData, GriddedData, ArrayContainer

        Raises:
            NotImplementedError: if saving the type of container is not supported.

        Returns:
            int: status of zero when successful. Non zero for errors.
        """
        # TODO. is timezone needed?
        status = 0
        if type(container) is RegularTimeSeries:
            ts = container
            # def hec_dss_tsStoreRegular(dss, pathname, startDate, startTime, valueArray, qualityArray,
            #                           saveAsFloat, units, type):
            if not len(ts.times):
                raise Exception("Time Series has an empty times array")

            startDate, startTime = DateConverter.dss_datetime_strings_from_datetime(ts.times[0])
            quality = container.quality

            status = self._native.hec_dss_tsStoreRegular(
                ts.id,
                startDate,
                startTime,
                ts.values,
                quality,
                False,
                ts.units,
                ts.data_type,
                ts.time_zone_name,
                0
            )
            self._catalog = None
        elif type(container) is IrregularTimeSeries:
            its = container
            if (DssPath(its.id).D.lower() == "ts-pattern"):
                raise ValueError("ts-pattern is not fully supported for irregular time series")
            # def hec_dss_tsStoreRegular(dss, pathname, startDate, startTime, valueArray, qualityArray,
            #                           saveAsFloat, units, type):
            start_date_base = (datetime(1900, 1, 1)+timedelta(days=its.julian_base_date))
            startDate, startTime = DateConverter.dss_datetime_strings_from_datetime(start_date_base)
            quality = container.quality
            julian_times = DateConverter.julian_array_from_date_times(its.times, its.time_granularity_seconds, start_date_base)
            if max(julian_times) >= 2147483647:
                raise Exception("Julian times contains value larger than 2147483647, increase granularity or change "
                                "start_date_base to fix.")
            status = self._native.hec_dss_tsStoreIrregular(
                its.id,
                startDate,
                julian_times,
                its.time_granularity_seconds,
                its.values,
                quality,
                False,
                its.units,
                its.data_type,
                its.time_zone_name,
                1
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
        elif type(container) is ArrayContainer:
            status = self._native.hec_dss_arrayStore(container.id, container.int_values, container.float_values, container.double_values)
            self._catalog = None
        elif type(container) is LocationInfo:
            status = self._native.hec_dss_locationStore(container,1)
            self._catalog = None
        elif type(container) is Text:
            text = container
            status = self._native.hec_dss_textStore(text.id, text.text, len(text.text))
            self._catalog = None
        else:
            raise NotImplementedError(f"unsupported record_type: {type(container)}. Expected types are: {RecordType.SUPPORTED_RECORD_TYPES.value}")

        if hasattr(container, "location_info") and container.location_info is not None:
            status = self._native.hec_dss_locationStore(container.location_info,1)

        # TODO -- instead of invalidating catalog,with _catalog=None
        #  can we be smart?
        # TODO -- if we get smart, catalog has  recordTypeDict and timeSeriesDictNoDates
        # how about Catalog has method  catalog.notify_put(pathname,RecordType)
        #  and                          catalog.notify_delete(pathname, RecordType)
        # if not self._catalog is None:
        #     self._catalog.recordTypeDict[pd.id] = RecordType.PairedData

        return status


    def writePrecompressedGrid(self, gd, compressedData, CompressionSize):
        """
        puts pre-compressed gridded data into the DSS file

        Args
            compressedData (bytes): Compressed data.
            CompressionSize (int): Size of the compressed data.
        Returns:
            int: 0 if successful, -1 otherwise.
        """

        if compressedData and CompressionSize > 0:
            status = self._native.hec_dss_gridStore(gd, compressedData, CompressionSize)
            self._catalog = None
            return status
        return -1

    def delete(self, pathname: str, allrecords: bool = False, startdatetime=None, enddatetime=None) -> int:
        """deletes a record from the DSS file
        Args:
            pathname (str): dss pathname, if only the pathname is provided, delete only the record with this pathname
            allRecords (bool): if True, delete all records with this pathname that have different dates
            startdatetime (datetime): start date for query, if only start date is provided, delete all records at or after this date
            enddatetime (datetime): end date for the query, if only end date is provided, delete all records at or before this date
        Returns:
            int: status of zero when successful. Non zero for errors.
        """
        rt = self.get_record_type(pathname)
        delete_path = DssPath(pathname)
        if (rt == RecordType.RegularTimeSeries or rt == RecordType.IrregularTimeSeries) and allrecords:
            for i in self.get_catalog().uncondensed_paths:
                uncondensed_path = DssPath(i)
                if uncondensed_path.path_without_date().__eq__(delete_path.path_without_date()):
                    status = self._native.hec_dss_delete(i)
                    if status == 0:
                        self._catalog = None
        elif rt == RecordType.RegularTimeSeries and (startdatetime or enddatetime):
            newStartDateTime, newEndDateTime = self._get_date_time_range(pathname, 1)
            if startdatetime:
                newStartDateTime = startdatetime
            if enddatetime:
                newEndDateTime = enddatetime

            interval_seconds=DateConverter.intervalString_to_sec(delete_path.E)

            firstMinutes = DateConverter.julian_array_from_date_times([newStartDateTime])[0]
            firstSeconds, firstJulian = [firstMinutes % 1440 * 60], [firstMinutes // 1440]

            lastMinutes = DateConverter.julian_array_from_date_times([newEndDateTime])[0]
            lastSeconds, lastJulian = [lastMinutes % 1440 * 60], [lastMinutes // 1440]

            number_periods = self._native.hec_dss_numberPeriods(
                interval_seconds,
                firstJulian[0],
                firstSeconds[0],
                lastJulian[0],
                lastSeconds[0],
            )

            RTS = RegularTimeSeries()
            RTS.values = [DSS_UNDEFINED_VALUE]*number_periods
            RTS.times = [newStartDateTime, newEndDateTime]
            RTS.start_date = startdatetime
            RTS.id = pathname

            startDate, startTime = DateConverter.dss_datetime_strings_from_datetime(RTS.times[0])

            status = self._native.hec_dss_tsStoreRegular(
                RTS.id,
                startDate,
                startTime,
                RTS.values,
                RTS.quality,
                False,
                RTS.units,
                RTS.data_type,
                RTS.time_zone_name,
                3
            )
            self._catalog = None
        elif rt == RecordType.IrregularTimeSeries and (startdatetime or enddatetime):
            newStartDateTime, newEndDateTime = self._get_date_time_range(pathname, 1)
            if startdatetime:
                newStartDateTime = startdatetime
            if enddatetime:
                newEndDateTime = enddatetime

            IRTS = IrregularTimeSeries()
            IRTS.values = [DSS_UNDEFINED_VALUE, DSS_UNDEFINED_VALUE]
            IRTS.times = [newStartDateTime, newEndDateTime]
            IRTS.start_date = startdatetime
            IRTS.id = pathname

            dss.put(IRTS)
        else:
            status = self._native.hec_dss_delete(pathname)
            if status == 0:
                self._catalog = None
            else:
                print(f"Error deleting record from '{pathname}', Record does not exist or timeseries path must be uncondensed")
        return status

    def get_catalog(self) -> Catalog:
        """gets the DSS Catalog of all items in the DSS file

        Returns:
            Catalog: :class:`Catalog`
        """
        paths, recordTypes = self._native.hec_dss_catalog()
        return Catalog(paths, recordTypes)

    def record_count(self) -> int:
        """get the number of records stored in the dss file

        Returns:
            int: number of items  (includes aliases)
        """
        return self._native.hec_dss_record_count()

    def set_debug_level(self, level) -> int:
        """sets the DSS debug level.

        Args:
            level (int): a value between 0 and 15. Larger for more output.
                For level descriptions, see zdssMessages.h of the heclib source code,
                or documentation from the HEC-DSS Programmers Guide for C on the `mlvl` parameter of the `zset` utility function.

        Returns:
            int: _description_
        """
        return self._native.hec_dss_set_debug_level(level)


if __name__ == "__main__":
    # import pdb;pdb.set_trace()
    dss = HecDss("sample7.dss")
    catalog = dss.get_catalog()
    for p in catalog:
        print(p)
    # print(catalog[0:5])
    # dss.set_debug_level(15)
