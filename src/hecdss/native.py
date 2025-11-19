import ctypes
from ctypes import c_float, c_double, c_char_p, c_int, c_void_p, POINTER
from ctypes import c_int32
from ctypes import byref, create_string_buffer
from ctypes.util import find_library
import numpy as np
from importlib import resources
import io
import os
import sys
from typing import List

# from hecdss.location_info import LocationInfo


class _Native:
    """Wrapper for Native method calls to hecdss.dll or libhecdss.so
    _Native should not be used directly; Use HecDss
    """

    def load_hecdss_library(self, libname):
        """
        searches and loads [lib]hecdss.[dll|so]
        """
        paths_to_try = [
            libname,
            os.path.join(os.path.dirname(__file__), 'lib', libname),
            find_library("hecdss")
        ]
        found_libs = [path for path in paths_to_try if path is not None and os.path.exists(path)]
        if len(found_libs) == 0:
            raise FileNotFoundError(f"{libname} not found Paths searched: {paths_to_try}")
        return ctypes.CDLL(found_libs[0])


    def __init__(self):
        """Loads the hecdss shared library from disk"""

        self.handle = None
        if sys.platform == "win32":
            self.dll = self.load_hecdss_library("hecdss.dll")
        else:
            self.dll = self.load_hecdss_library("libhecdss.so")

    def hec_dss_open(self, dss_filename: str) -> int:
        """opens a DSS file and gets a handle

        Args:
            dss_filename (str): filename to open

        Returns:
            int: status of zero when successful, non-zero on error.
        """
        f = self.dll.hec_dss_open
        f.argtypes = [
            c_char_p,
            POINTER(c_void_p),
        ]
        f.restype = c_int
        self.handle = c_void_p()
        rval = f(dss_filename.encode("utf-8"), ctypes.byref(self.handle))
        if rval != 0:
            raise Exception("Error opening DSS file.")
        return rval

    def hec_dss_close(self):
        """close the DSS file

        Returns:
            int: status of zero when successful, non-zero on error.
        """
        f = self.dll.hec_dss_close
        f.argtypes = [c_void_p()]
        f.restype = c_int
        return f(self.handle)

    def hec_dss_record_count(self):
        f = self.dll.hec_dss_record_count
        f.argtypes = [c_void_p()]
        f.restype = c_int
        return f(self.handle)

    # set a integer setting by name
    def __hec_dss_set_value(self, name: str, value: int):
        f = self.dll.hec_dss_set_value
        f.argtypes = [c_char_p, c_int]
        f.restype = c_int
        f(name.encode("utf-8"), value)

    # set debug level (0-15)
    # 0 - no output
    # 15 - max output
    # for additional levels: see zdssMessages.h of the heclib source code,
    # or documentation from the HEC-DSS Programmers Guide for C on `mlvl` parameter of the `zset` utility function.
    def hec_dss_set_debug_level(self, value: int):
        self.__hec_dss_set_value("mlvl", value)

    def hec_dss_export_to_file(
            self, path: str, outputFile: str, startDate: str, startTime: str, endDate: str, endTime: str
    ):
        f = self.dll.hec_dss_export_to_file
        f.argtypes = [
            c_void_p(),  # dss
            c_char_p,  # path
            c_char_p,  # outputFile
            c_char_p,  # startDate
            c_char_p,  # startTime
            c_char_p,  # endDate
            c_char_p,  # endTime
        ]
        f.restype = c_int

        result = f(
            self.handle, path, outputFile, startDate, startTime, endDate, endTime
        )

    def hec_dss_CONSTANT_MAX_PATH_SIZE(self):
        f = self.dll.hec_dss_CONSTANT_MAX_PATH_SIZE
        f.restype = c_int
        return f()

    def hec_dss_catalog(self, filter=""):
        """
        retrieves a list of objects in a DSS database

        returns a list of paths, and recordTypes

        """
        count = self.hec_dss_record_count()
        pathBufferSize = self.hec_dss_CONSTANT_MAX_PATH_SIZE()
        self.dll.hec_dss_catalog.argtypes = [
            c_void_p,  # dss (assuming it's a pointer)
            c_char_p,  # pathBuffer
            POINTER(c_int),  # recordTypes
            c_char_p,  # pathFilter
            c_int,  # count
            c_int,  # pathBufferItemSize
        ]
        self.dll.hec_dss_catalog.restype = c_int

        c_rawCatalog = create_string_buffer(count * pathBufferSize)
        pathFilter = filter.encode("ascii")
        recordTypes = (c_int32 * count)()

        pathNameList = []

        numRecords = self.dll.hec_dss_catalog(
            self.handle, c_rawCatalog, recordTypes, pathFilter, count, pathBufferSize
        )
        recordTypeArray = []
        recordTypeArray.extend(list(recordTypes[:count]))
        for i in range(numRecords):
            start = i * pathBufferSize
            end = start + pathBufferSize
            s = c_rawCatalog[start:end].decode("ascii").replace("\x00", "")
            # print(f"str='{s}'")
            pathNameList.append(s)

        return pathNameList, recordTypeArray

    def hec_dss_gridRetrieve(self, pathname: str,
                             gridType: List[int], dataType: List[int],
                             lowerLeftCellX: List[int], lowerLeftCellY: List[int],
                             numberOfCellsX: List[int], numberOfCellsY: List[int],
                             numberOfRanges: List[int], srsDefinitionType: List[int],
                             timeZoneRawOffset: List[int], isInterval: List[int],
                             isTimeStamped: List[int],
                             dataUnits: List[str],
                             dataSource: List[str],
                             srsName: List[str],
                             srsDefinition: List[str],
                             timeZoneID: List[str],
                             cellSize: List[float], xCoordOfGridCellZero: List[float],
                             yCoordOfGridCellZero: List[float], nullValue: List[float],
                             maxDataValue: List[float], minDataValue: List[float],
                             meanDataValue: List[float],
                             rangeLimitTable: List[float],
                             numberEqualOrExceedingRangeLimit: List[int],
                             data: List[float], dataLength: int = 0,
                             dataUnitsLength: int = 40, dataSourceLength: int = 40,
                             srsNameLength: int = 40, srsDefinitionLength: int = 600,
                             timeZoneIDLength: int = 40, rangeTablesLength: int = 0, ):

        self.dll.hec_dss_gridRetrieve.argtypes = [c_void_p, c_char_p, c_int,
                                                  POINTER(c_int), POINTER(c_int),
                                                  POINTER(c_int), POINTER(c_int),
                                                  POINTER(c_int), POINTER(c_int),
                                                  POINTER(c_int), POINTER(c_int),
                                                  POINTER(c_int), POINTER(c_int),
                                                  POINTER(c_int),
                                                  c_char_p, c_int,
                                                  c_char_p, c_int,
                                                  c_char_p, c_int,
                                                  c_char_p, c_int,
                                                  c_char_p, c_int,
                                                  POINTER(c_float), POINTER(c_float),
                                                  POINTER(c_float), POINTER(c_float),
                                                  POINTER(c_float), POINTER(c_float),
                                                  POINTER(c_float),
                                                  POINTER(c_float), c_int,
                                                  POINTER(c_int),
                                                  POINTER(c_float), c_int]

        self.dll.hec_dss_gridRetrieve.restype = c_int

        # Type conversions and buffer initializations
        type_pointer = c_int()
        dataType_pointer = c_int()

        c_lowerLeftCellX = c_int()
        c_lowerLeftCellY = c_int()
        c_numberOfCellsX = c_int()
        c_numberOfCellsY = c_int()
        c_numberOfRanges = c_int()
        c_srsDefinitionType = c_int()

        c_timeZoneRawOffset = c_int()
        c_isInterval = c_int()
        c_isTimeStamped = c_int()

        c_dataUnits = create_string_buffer(dataUnitsLength)
        c_dataSource = create_string_buffer(dataSourceLength)
        c_srsName = create_string_buffer(srsNameLength)
        c_srsDefinition = create_string_buffer(srsDefinitionLength)
        c_timeZoneID = create_string_buffer(timeZoneIDLength)

        c_cellSize = c_float()
        c_xCoordOfGridCellZero = c_float()
        c_yCoordOfGridCellZero = c_float()
        c_nullValue = c_float()
        c_maxDataValue = c_float()
        c_minDataValue = c_float()
        c_meanDataValue = c_float()

        c_rangeLimitTable = (c_float * rangeTablesLength)()

        c_numberEqualOrExceedingRangeLimit = (c_int * rangeTablesLength)()

        c_data = (c_float * 0)()

        result = self.dll.hec_dss_gridRetrieve(self.handle, pathname.encode("utf-8"), False,
                                               ctypes.byref(type_pointer), ctypes.byref(dataType_pointer),
                                               c_lowerLeftCellX, c_lowerLeftCellY,
                                               c_numberOfCellsX, c_numberOfCellsY,
                                               c_numberOfRanges, c_srsDefinitionType,
                                               ctypes.byref(c_timeZoneRawOffset), c_isInterval,
                                               c_isTimeStamped,
                                               c_dataUnits, dataUnitsLength,
                                               c_dataSource, dataSourceLength,
                                               c_srsName, srsNameLength,
                                               c_srsDefinition, srsDefinitionLength,
                                               c_timeZoneID, timeZoneIDLength,
                                               ctypes.byref(c_cellSize), ctypes.byref(c_xCoordOfGridCellZero),
                                               ctypes.byref(c_yCoordOfGridCellZero), ctypes.byref(c_nullValue),
                                               ctypes.byref(c_maxDataValue), ctypes.byref(c_minDataValue),
                                               ctypes.byref(c_meanDataValue),
                                               c_rangeLimitTable, rangeTablesLength,
                                               c_numberEqualOrExceedingRangeLimit,
                                               c_data, dataLength)
        if result != 0:
            print("boolRetriveData False, Function call failed with result:", result)
            return result

        rangeTablesLength = c_numberOfRanges.value
        c_rangeLimitTable = (c_float * rangeTablesLength)()
        c_numberEqualOrExceedingRangeLimit = (c_int * rangeTablesLength)()

        dataLength = dataLength if dataLength else c_numberOfCellsX.value * c_numberOfCellsY.value
        c_data = (c_float * dataLength)()

        result = self.dll.hec_dss_gridRetrieve(self.handle, pathname.encode("utf-8"), True,
                                               ctypes.byref(type_pointer), ctypes.byref(dataType_pointer),
                                               c_lowerLeftCellX, c_lowerLeftCellY,
                                               c_numberOfCellsX, c_numberOfCellsY,
                                               c_numberOfRanges, c_srsDefinitionType,
                                               ctypes.byref(c_timeZoneRawOffset), c_isInterval,
                                               c_isTimeStamped,
                                               c_dataUnits, dataUnitsLength,
                                               c_dataSource, dataSourceLength,
                                               c_srsName, srsNameLength,
                                               c_srsDefinition, srsDefinitionLength,
                                               c_timeZoneID, timeZoneIDLength,
                                               ctypes.byref(c_cellSize), ctypes.byref(c_xCoordOfGridCellZero),
                                               ctypes.byref(c_yCoordOfGridCellZero), ctypes.byref(c_nullValue),
                                               ctypes.byref(c_maxDataValue), ctypes.byref(c_minDataValue),
                                               ctypes.byref(c_meanDataValue),
                                               c_rangeLimitTable, rangeTablesLength,
                                               c_numberEqualOrExceedingRangeLimit,
                                               c_data, dataLength)

        # Processing results
        if result == 0:

            gridType[0] = type_pointer.value
            dataType[0] = dataType_pointer.value

            lowerLeftCellX[0] = c_lowerLeftCellX.value
            lowerLeftCellY[0] = c_lowerLeftCellY.value
            numberOfCellsX[0] = c_numberOfCellsX.value
            numberOfCellsY[0] = c_numberOfCellsY.value
            numberOfRanges[0] = c_numberOfRanges.value

            srsDefinitionType[0] = c_srsDefinitionType.value
            timeZoneRawOffset[0] = c_timeZoneRawOffset.value
            isInterval[0] = c_isInterval.value
            isTimeStamped[0] = c_isTimeStamped.value

            dataUnits[0] = c_dataUnits.value.decode('utf-8')
            dataSource[0] = c_dataSource.value.decode('utf-8')
            srsName[0] = c_srsName.value.decode('utf-8')
            srsDefinition[0] = c_srsDefinition.value.decode('utf-8')
            timeZoneID[0] = c_timeZoneID.value.decode('utf-8')

            cellSize[0] = c_cellSize.value
            xCoordOfGridCellZero[0] = c_xCoordOfGridCellZero.value
            yCoordOfGridCellZero[0] = c_yCoordOfGridCellZero.value
            nullValue[0] = c_nullValue.value
            maxDataValue[0] = c_maxDataValue.value
            minDataValue[0] = c_minDataValue.value
            meanDataValue[0] = c_meanDataValue.value

            rangeLimitTable.extend(list(c_rangeLimitTable))
            numberEqualOrExceedingRangeLimit.extend(list(c_numberEqualOrExceedingRangeLimit))
            data.extend(list(c_data))

            # print("Function call successful:")
        else:
            print("Function call failed with result:", result)

        return result

    def hec_dss_gridStore(
            self,
            gd,
            compressedData=None,
            compressionSize=0,
    ):
        self.dll.hec_dss_pdStore.restype = c_int
        self.dll.hec_dss_pdStore.argtypes = [
            ctypes.POINTER(ctypes.c_void_p),  # dss (dss file pointer)
            ctypes.c_char_p,  # pathname
            ctypes.c_int,  # gridType
            ctypes.c_int,  # dataType
            ctypes.c_int,  # lowerLeftCellX
            ctypes.c_int,  # lowerLeftCellY
            ctypes.c_int,  # numberOfCellsX
            ctypes.c_int,  # numberOfCellsY
            ctypes.c_int,  # numberOfRanges
            ctypes.c_int,  # srsDefinitionType
            ctypes.c_int,  # timeZoneRawOffset
            ctypes.c_int,  # isInterval
            ctypes.c_int,  # isTimeStamped
            ctypes.c_int,  # compressionSize
            ctypes.c_char_p,  # dataUnits
            ctypes.c_char_p,  # dataSource
            ctypes.c_char_p,  # srsName
            ctypes.c_char_p,  # srsDefinition
            ctypes.c_char_p,  # timeZoneID
            ctypes.c_float,  # cellSize
            ctypes.c_float,  # xCoordOfGridCellZero
            ctypes.c_float,  # yCoordOfGridCellZero
            ctypes.c_float,  # nullValue
            ctypes.c_float,  # maxDataValue
            ctypes.c_float,  # minDataValue
            ctypes.c_float,  # meanDataValue
            ctypes.POINTER(ctypes.c_float),  # rangeLimitTable
            ctypes.POINTER(ctypes.c_int),  # numberEqualOrExceedingRangeLimit
            ctypes.POINTER(ctypes.c_float)  # data
        ]

        c_pathname = c_char_p(gd.id.encode("utf-8"))

        c_gridType = c_int(gd.type)
        c_dataType = c_int(gd.data_type)
        c_lowerLeftCellX = c_int(gd.lowerLeftCellX)
        c_lowerLeftCellY = c_int(gd.lowerLeftCellY)
        c_numberOfCellsX = c_int(gd.numberOfCellsX)
        c_numberOfCellsY = c_int(gd.numberOfCellsY)
        c_numberOfRanges = c_int(gd.numberOfRanges)
        c_srsDefinitionType = c_int(gd.srsDefinitionType)
        c_timeZoneRawOffset = c_int(gd.timeZoneRawOffset)
        c_isInterval = c_int(gd.isInterval)
        c_isTimeStamped = c_int(gd.isTimeStamped)
        c_compressionSize = c_int(compressionSize)  # default compression

        c_dataUnits = c_char_p(gd.dataUnits.encode("utf-8"))
        c_dataSource = c_char_p(gd.dataSource.encode("utf-8"))
        c_srsName = c_char_p(gd.srsName.encode("utf-8"))
        c_srsDefinition = c_char_p(gd.srsDefinition.encode("utf-8"))
        c_timeZoneID = c_char_p(gd.timeZoneID.encode("utf-8"))

        c_cellSize = c_float(gd.cellSize)
        c_xCoordOfGridCellZero = c_float(gd.xCoordOfGridCellZero)
        c_yCoordOfGridCellZero = c_float(gd.yCoordOfGridCellZero)
        c_nullValue = c_float(gd.nullValue)
        c_maxDataValue = c_float(gd.maxDataValue)
        c_minDataValue = c_float(gd.minDataValue)
        c_meanDataValue = c_float(gd.meanDataValue)

        c_rangeLimitTable = (c_float * len(gd.rangeLimitTable))(*gd.rangeLimitTable)
        c_numberEqualOrExceedingRangeLimit = (c_int * len(gd.numberEqualOrExceedingRangeLimit))(
            *gd.numberEqualOrExceedingRangeLimit)

        if compressedData is not None and compressionSize:
            # Treat compressed data as raw bytes, not float32
            c_data = ctypes.cast(compressedData, ctypes.POINTER(ctypes.c_float))
        else:
            arr = gd.data.astype('float32', copy=False)
            c_data = arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        return self.dll.hec_dss_gridStore(self.handle, c_pathname, c_gridType, c_dataType,
                                          c_lowerLeftCellX, c_lowerLeftCellY,
                                          c_numberOfCellsX, c_numberOfCellsY,
                                          c_numberOfRanges, c_srsDefinitionType,
                                          c_timeZoneRawOffset, c_isInterval,
                                          c_isTimeStamped, c_compressionSize,
                                          c_dataUnits, c_dataSource,
                                          c_srsName, c_srsDefinition, c_timeZoneID,
                                          c_cellSize, c_xCoordOfGridCellZero,
                                          c_yCoordOfGridCellZero, c_nullValue,
                                          c_maxDataValue, c_minDataValue, c_meanDataValue,
                                          c_rangeLimitTable, c_numberEqualOrExceedingRangeLimit, c_data)

    def hec_dss_pdRetrieveInfo(self, pathname,
                               numberOrdinates: List[int], numberCurves: List[int],
                               unitsIndependent: List[str],
                               unitsDependent: List[str],
                               typeIndependent: List[str],
                               typeDependent: List[str],
                               labelsLength):
        self.dll.hec_dss_pdRetrieveInfo.argtypes = [c_void_p, c_char_p,
                                                    POINTER(c_int), POINTER(c_int),
                                                    c_char_p, c_int,
                                                    c_char_p, c_int,
                                                    c_char_p, c_int,
                                                    c_char_p]

        self.dll.hec_dss_pdRetrieveInfo.restype = c_int
        numberOrdinates_val = c_int()
        numberCurves_val = c_int()
        labelsLength_val = c_int()

        buff_size = 40
        c_unitsIndependent = create_string_buffer(buff_size)
        c_string_length = c_int(buff_size)
        c_unitsDependent = create_string_buffer(buff_size)
        c_typeIndependent = create_string_buffer(buff_size)
        c_typeDependent = create_string_buffer(buff_size)

        result = self.dll.hec_dss_pdRetrieveInfo(
            self.handle,
            pathname.encode("utf-8"),
            ctypes.byref(numberOrdinates_val),
            ctypes.byref(numberCurves_val),
            c_unitsIndependent,
            c_string_length,
            c_unitsDependent,
            c_string_length,
            c_typeIndependent,
            c_string_length,
            c_typeDependent,
            c_string_length,
            ctypes.byref(labelsLength_val),
        )

        if result == 0:
            numberOrdinates[0] = numberOrdinates_val.value
            numberCurves[0] = numberCurves_val.value
            labelsLength[0] = labelsLength_val.value

            unitsIndependent[0] = c_unitsIndependent.value.decode('utf-8')
            unitsDependent[0] = c_unitsDependent.value.decode('utf-8')
            typeIndependent[0] = c_typeIndependent.value.decode('utf-8')
            typeDependent[0] = c_typeDependent.value.decode('utf-8')
        else:
            print("Function call failed with result:", result)

        return result

    def hec_dss_pdRetrieve(self, pathname: str,
                           doubleOrdinates: List[float], doubleOrdinatesLength: int,
                           doubleValues: List[float], doubleValuesLength: int,
                           numberOrdinates: List[int], numberCurves: List[int],
                           unitsIndependent: List[str], unitsIndependentLength: int,
                           typeIndependent: List[str], typeIndependentLength: int,
                           unitsDependent: List[str], unitsDependentLength: int,
                           typeDependent: List[str], typeDependentLength: int,
                           labels: List[str], labelsLength: int,
                           timeZoneName: List[str], timeZoneNameLength: int):

        self.dll.hec_dss_pdRetrieve.argtypes = [c_void_p, c_char_p,
                                                POINTER(c_double), c_int,
                                                POINTER(c_double), c_int,
                                                POINTER(c_int), POINTER(c_int),
                                                c_char_p, c_int,
                                                c_char_p, c_int,
                                                c_char_p, c_int,
                                                c_char_p, c_int,
                                                c_char_p, c_int,
                                                c_char_p, c_int]

        self.dll.hec_dss_pdRetrieve.restype = c_int

        c_doubleOrdinates = (c_double * doubleOrdinatesLength)()
        c_doubleValues = (c_double * doubleValuesLength)()
        c_numberOrdinates = c_int()
        c_numberCurves = c_int()

        c_labels = create_string_buffer(labelsLength)
        c_unitsIndependent = create_string_buffer(unitsIndependentLength)
        c_unitsDependent = create_string_buffer(unitsDependentLength)
        c_typeIndependent = create_string_buffer(typeIndependentLength)
        c_typeDependent = create_string_buffer(typeDependentLength)

        c_timeZoneName = create_string_buffer(timeZoneNameLength)

        result = self.dll.hec_dss_pdRetrieve(self.handle,
                                             pathname.encode("utf-8"),
                                             c_doubleOrdinates, doubleOrdinatesLength,
                                             c_doubleValues, doubleValuesLength,
                                             ctypes.byref(c_numberOrdinates),
                                             ctypes.byref(c_numberCurves),
                                             c_unitsIndependent, unitsIndependentLength,
                                             c_typeIndependent, typeIndependentLength,
                                             c_unitsDependent, unitsDependentLength,
                                             c_typeDependent, typeDependentLength,
                                             c_labels, labelsLength,
                                             c_timeZoneName, timeZoneNameLength)

        if result == 0:
            unitsIndependent[0] = c_unitsIndependent.value.decode('utf-8')
            unitsDependent[0] = c_unitsDependent.value.decode('utf-8')
            typeIndependent[0] = c_typeIndependent.value.decode('utf-8')
            typeDependent[0] = c_typeDependent.value.decode('utf-8')

            doubleOrdinates.extend(list(c_doubleOrdinates))
            doubleValues.extend(list(c_doubleValues))
            numberOrdinates[0] = c_numberOrdinates
            numberCurves[0] = c_numberCurves
            labels.extend(c_labels.raw.decode('utf-8').split("\0")[:c_numberCurves.value])

            timeZoneName[0] = c_timeZoneName.value.decode("utf-8")
        else:
            print("Function call failed with result:", result)

        return result

    def hec_dss_pdStore(
            self,
            pd,
    ):

        self.dll.hec_dss_pdStore.restype = c_int
        self.dll.hec_dss_pdStore.argtypes = [
            c_void_p,  # dss (void*)
            c_char_p,  # pathname (const char*)
            POINTER(c_double),  # ordinatesArray (double*)
            c_int,  # ordinatesLength (int)
            POINTER(c_double),  # valuesArray (double*)
            c_int,  # valuesLength (int)
            c_int,  # numberOrdinates (int)
            c_int,  # NumberCurves (int)
            c_char_p,  # unitsIndependent (const char*)
            c_char_p,  # typeIndependent (const char*)
            c_char_p,  # unitsDependent (const char*)
            c_char_p,  # typeDependent (const char*)
            c_char_p,  # labels (const char*)
            c_int,  # labelsLength (int)
            c_char_p,  # timeZoneName (const char*) - New argument
        ]

        numberCurves = len(pd.values[0])
        if numberCurves > 1:
            _values = pd.values.tolist()
            if len(_values[0]) > 1:
                _values = [[_values[i][j] for i in range(len(_values))] for j in range(len(_values[0]))]
            values2 = np.array(_values)
        else:
            values2 = pd.values
        c_pathname = c_char_p(pd.id.encode("utf-8"))
        c_Ordinates = (c_double * len(pd.ordinates))(*pd.ordinates)
        c_OrdinatesLength = len(pd.ordinates)
        flat_list = values2.flatten()
        c_Values = (c_double * len(flat_list))(*flat_list)
        c_ValuesLength = len(flat_list)
        c_numberOrdinates = len(pd.ordinates)
        c_numberCurves = numberCurves
        c_unitsIndependent = c_char_p(pd.units_independent.encode("utf-8"))
        c_typeIndependent = c_char_p(pd.type_independent.encode("utf-8"))
        c_unitsDependent = c_char_p(pd.units_dependent.encode("utf-8"))
        c_typeDependent = c_char_p(pd.type_dependent.encode("utf-8"))
        flat_labels = "\0".join(pd.labels)
        c_labels = c_char_p(flat_labels.encode("utf-8"))
        c_labelsLength = len(flat_labels)
        c_timeZoneName = c_char_p(pd.time_zone_name.encode("utf-8"))  # New argument

        return self.dll.hec_dss_pdStore(
            self.handle,
            c_pathname,
            c_Ordinates,
            c_OrdinatesLength,
            c_Values,
            c_ValuesLength,
            c_numberOrdinates,
            c_numberCurves,
            c_unitsIndependent,
            c_typeIndependent,
            c_unitsDependent,
            c_typeDependent,
            c_labels,
            c_labelsLength,
            c_timeZoneName,  # Pass the new argument
        )

    def hec_dss_tsGetSizes(
            self,
            pathname,
            startDate,
            startTime,
            endDate,
            endTime,
            numberValues,
            qualityElementSize,
    ):
        self.dll.hec_dss_tsGetSizes.argtypes = [
            c_void_p(),  # dss
            c_char_p,  # path
            c_char_p,  # startDate
            c_char_p,  # startTime
            c_char_p,  # endDate
            c_char_p,  # endTime
            POINTER(c_int),  # numberValues
            POINTER(c_int),  # qualityElementSize
        ]
        self.dll.hec_dss_tsGetSizes.restype = c_int

        nv = c_int()
        qes = c_int()

        result = self.dll.hec_dss_tsGetSizes(
            self.handle,
            pathname.encode("utf-8"),
            startDate.encode("utf-8"),
            startTime.encode("utf-8"),
            endDate.encode("utf-8"),
            endTime.encode("utf-8"),
            byref(nv),
            byref(qes),
        )

        if result == 0:
            numberValues[0] = nv.value
            qualityElementSize[0] = qes.value
        else:
            print("Function call failed with result:", result)

        return result

    def hec_dss_tsGetDateTimeRange(
            self,
            pathname,
            boolFullSet,
            firstValidJulian,
            firstSeconds,
            lastValidJulian,
            lastSeconds,
    ):
        self.dll.hec_dss_tsGetDateTimeRange.argtypes = [
            c_void_p(),  # dss
            c_char_p,  # path
            c_int,  # boolFullSet
            POINTER(c_int),  # firstValidJulian
            POINTER(c_int),  # firstSeconds
            POINTER(c_int),  # lastValidJulian
            POINTER(c_int),  # lastSeconds
        ]
        self.dll.hec_dss_tsGetDateTimeRange.restype = c_int

        fjul = c_int()
        fsec = c_int()

        ljul = c_int()
        lsec = c_int()

        result = self.dll.hec_dss_tsGetDateTimeRange(
            self.handle,
            pathname.encode("utf-8"),
            c_int(boolFullSet),
            byref(fjul),
            byref(fsec),
            byref(ljul),
            byref(lsec),
        )

        if result == 0:
            firstValidJulian[0] = fjul.value
            firstSeconds[0] = fsec.value
            lastValidJulian[0] = ljul.value
            lastSeconds[0] = lsec.value
        else:
            print("Function call failed with result:", result)

        return result

    def hec_dss_numberPeriods(
            self,
            intervalSeconds,
            julianStart,
            startSeconds,
            julianEnd,
            endSeconds,
    ):
        self.dll.hec_dss_numberPeriods.argtypes = [
            c_int,  # intervalSeconds
            c_int,  # julianStart
            c_int,  # startSeconds
            c_int,  # julianEnd
            c_int,  # endSeconds
        ]
        self.dll.hec_dss_numberPeriods.restype = c_int

        result = self.dll.hec_dss_numberPeriods(
            intervalSeconds,
            julianStart,
            startSeconds,
            julianEnd,
            endSeconds,
        )

        return result

    def hec_dss_tsRetrieve(
            self,
            pathname: str,
            startDate: str,
            startTime: str,
            endDate: str,
            endTime: str,
            times: List[int],
            values: List[float],
            arraySize: str,
            numberValuesRead,
            quality: List[int],
            qualityLength: int,
            julianBaseDate: List[int],
            timeGranularitySeconds: List[int],
            units: List[str],
            unitsLength: int,
            dataType: List[str],
            typeLength: int,
            timeZoneName: List[str],
            timeZoneNameLength: int,
    ):

        f = self.dll.hec_dss_tsRetrieve
        f.argtypes = [
            c_void_p,  # dss
            c_char_p,  # pathname
            c_char_p,  # startDate
            c_char_p,  # startTime
            c_char_p,  # endDate
            c_char_p,  # endTime
            POINTER(c_int),  # timeArray
            POINTER(c_double),  # valueArray
            c_int,  # arraySize
            POINTER(c_int),  # numberValuesRead
            POINTER(c_int),  # quality
            c_int,  # qualityLength
            POINTER(c_int),  # julianBaseDate
            POINTER(c_int),  # timeGranularitySeconds
            c_char_p,  # units
            c_int,  # unitsLength
            c_char_p,  # dataType
            c_int,  # typeLength
            c_char_p,  # timeZoneName
            c_int,  # timeZoneNameLength
        ]
        f.restype = c_int

        c_arraySize = c_int(arraySize)
        c_times = (c_int32 * arraySize)()
        c_values = (c_double * arraySize)()
        c_numberValuesRead = c_int(0)
        size = qualityLength * arraySize

        c_quality = (c_int * size)()
        c_julianBaseDate = c_int(0)
        c_timeGranularitySeconds = c_int(0)

        buff_size = unitsLength
        c_units = create_string_buffer(buff_size)
        c_unitsLength = c_int(buff_size)

        buff_size = typeLength
        c_dataType = create_string_buffer(buff_size)
        c_typeLength = c_int(buff_size)
        c_julianBaseDate = c_int()
        c_timeGranularitySeconds = c_int()

        c_timeZoneName = create_string_buffer(timeZoneNameLength)

        rval = f(
            self.handle,
            pathname.encode("utf-8"),
            startDate.encode("utf-8"),
            startTime.encode("utf-8"),
            endDate.encode("utf-8"),
            endTime.encode("utf-8"),
            c_times,
            c_values,
            c_arraySize,
            byref(c_numberValuesRead),
            c_quality,
            qualityLength,
            byref(c_julianBaseDate),
            byref(c_timeGranularitySeconds),
            c_units,
            c_unitsLength,
            c_dataType,
            c_typeLength,
            c_timeZoneName,
            timeZoneNameLength,
        )

        times.clear()
        times.extend(list(c_times[: c_numberValuesRead.value]))
        values.clear()
        values.extend(list(c_values[: c_numberValuesRead.value]))
        quality.clear()
        quality.extend(list(c_quality[: c_numberValuesRead.value]))
        units[0] = c_units.value.decode("utf-8")
        dataType[0] = c_dataType.value.decode("utf-8")
        julianBaseDate[0] = c_julianBaseDate.value
        timeGranularitySeconds[0] = c_timeGranularitySeconds.value
        timeZoneName[0] = c_timeZoneName.value.decode("utf-8")

        return rval

    def hec_dss_tsStoreRegular(
            self,
            pathname,
            startDate,
            startTime,
            valueArray,
            qualityArray,
            saveAsFloat,
            units,
            dataType,
            timeZoneName,
            storageFlag,
    ):

        self.dll.hec_dss_tsStoreRegular.restype = c_int
        self.dll.hec_dss_tsStoreRegular.argtypes = [
            c_void_p,  # dss (void*)
            c_char_p,  # pathname (const char*)
            c_char_p,  # startDate (const char*)
            c_char_p,  # startTime (const char*)
            POINTER(c_double),  # valueArray (double*)
            c_int,  # valueArraySize (int)
            POINTER(c_int),  # qualityArray (int*)
            c_int,  # qualityArraySize (int)
            c_int,  # saveAsFloat (int)
            c_char_p,  # units (const char*)
            c_char_p,  # type (const char*)
            c_char_p,  # timeZoneName (const char*)
            c_int,  # storageFlag (int)
        ]

        c_pathname = c_char_p(pathname.encode("utf-8"))
        c_startDate = c_char_p(startDate.encode("utf-8"))
        c_startTime = c_char_p(startTime.encode("utf-8"))
        c_units = c_char_p(units.encode("utf-8"))
        c_type = c_char_p(dataType.encode("utf-8"))
        c_timeZoneName = c_char_p(timeZoneName.encode("utf-8"))  # New argument

        c_valueArray = (c_double * len(valueArray))(*valueArray)
        c_qualityArray = (c_int * len(qualityArray))(*qualityArray)

        return self.dll.hec_dss_tsStoreRegular(
            self.handle,
            c_pathname,
            c_startDate,
            c_startTime,
            c_valueArray,
            len(valueArray),
            c_qualityArray,
            len(qualityArray),
            int(saveAsFloat),
            c_units,
            c_type,
            c_timeZoneName,
            int(storageFlag),
        )

    def hec_dss_tsStoreIrregular(
            self,
            pathname,
            startDateBase,
            times,
            timeGranularitySeconds,
            valueArray,
            qualityArray,
            saveAsFloat,
            units,
            dataType,
            timeZoneName,
            storageFlag,
    ):

        self.dll.hec_dss_tsStoreIregular.restype = c_int
        self.dll.hec_dss_tsStoreIregular.argtypes = [
            c_void_p,  # dss (void*)
            c_char_p,  # pathname (const char*)
            c_char_p,  # startDateBase (const char*)
            POINTER(c_int),  # times (int*)
            c_int,  # timeGranularitySeconds (int)
            POINTER(c_double),  # valueArray (double*)
            c_int,  # valueArraySize (int)
            POINTER(c_int),  # qualityArray (int*)
            c_int,  # qualityArraySize (int)
            c_int,  # saveAsFloat (int)
            c_char_p,  # units (const char*)
            c_char_p,  # type (const char*)
            c_char_p,  # timeZoneName (const char*)
            c_int, # storageFlag (int)
        ]

        c_pathname = c_char_p(pathname.encode("utf-8"))
        c_startDateBase = c_char_p(startDateBase.encode("utf-8"))
        c_units = c_char_p(units.encode("utf-8"))
        c_type = c_char_p(dataType.encode("utf-8"))
        c_timeZoneName = c_char_p(timeZoneName.encode("utf-8"))  # New argument

        c_valueArray = (c_double * len(valueArray))(*valueArray)
        c_times = (c_int * len(times))(*times)
        c_qualityArray = (c_int * len(qualityArray))(*qualityArray)

        return self.dll.hec_dss_tsStoreIregular(
            self.handle,
            c_pathname,
            c_startDateBase,
            c_times,
            int(timeGranularitySeconds),
            c_valueArray,
            len(valueArray),
            c_qualityArray,
            len(qualityArray),
            int(saveAsFloat),
            c_units,
            c_type,
            c_timeZoneName,
            int(storageFlag),
        )

    def hec_dss_recordType(self, pathname):
        f = self.dll.hec_dss_recordType
        f.argtypes = [
            c_void_p,
            c_char_p
        ]
        f.restype = c_int
        c_str = c_char_p(pathname.encode("utf-8"))
        return f(self.handle, c_str)

    def hec_dss_arrayRetrieveInfo(self, pathname: str, intValuesRead: List[int], floatValuesRead: List[int],
                                  doubleValuesRead: List[int]):
        f = self.dll.hec_dss_arrayRetrieveInfo
        f.argtypes = [
            c_void_p(),  # dss_file* dss
            c_char_p,  # const char* pathname
            POINTER(c_int),  # int* intValuesRead
            POINTER(c_int),  # int* floatValuesRead
            POINTER(c_int)  # int* doubleValuesRead
        ]
        f.restype = c_int

        c_intValuesRead = c_int()
        c_floatValuesRead = c_int()
        c_doubleValuesRead = c_int()
        result = f(self.handle, pathname.encode("utf-8"), byref(c_intValuesRead), byref(c_floatValuesRead),
                   byref(c_doubleValuesRead))

        intValuesRead[0] = c_intValuesRead.value
        floatValuesRead[0] = c_floatValuesRead.value
        doubleValuesRead[0] = c_doubleValuesRead.value

        return result

    def hec_dss_arrayStore(self, pathname: str, intValues: List[int], floatValues: List[float],
                           doubleValues: List[float]):
        f = self.dll.hec_dss_arrayStore
        f.argtypes = [
            c_void_p,  # dss_file* dss
            c_char_p,  # const char* pathname
            POINTER(c_int),  # int* intValues
            c_int,  # const int intValuesLength
            POINTER(c_float),  # float* floatValues
            c_int,  # const int floatValuesLength
            POINTER(c_double),  # double* doubleValues
            c_int  # const int doubleValuesLength
        ]
        f.restype = c_int

        c_intValues = (c_int32 * len(intValues))(*intValues)
        c_floatValues = (c_float * len(floatValues))(*floatValues)
        c_doubleValues = (c_double * len(doubleValues))(*doubleValues)
        return f(self.handle, pathname.encode('utf-8'), c_intValues, len(intValues),
                 c_floatValues, len(floatValues),
                 c_doubleValues, len(doubleValues))

    def hec_dss_arrayRetrieve(self, pathname, intValues: List[int], floatValues: List[float],
                              doubleValues: List[float]):
        f = self.dll.hec_dss_arrayRetrieve

        f.argtypes = (
            c_void_p,  # dss_file*
            c_char_p,  # const char* - pathname
            POINTER(c_int),  # int* intValues
            c_int,  # const int intValuesLength
            POINTER(c_float),  # float* floatValues
            c_int,  # const int floatValuesLength
            POINTER(c_double),  # double* doubleValues
            c_int  # const int doubleValuesLength
        )
        f.restype = c_int

        c_intValues = (c_int32 * len(intValues))(*intValues)
        c_floatValues = (c_float * len(floatValues))(*floatValues)
        c_doubleValues = (c_double * len(doubleValues))(*doubleValues)

        status = f(self.handle, pathname.encode('utf-8'),
                   c_intValues, len(intValues),
                   c_floatValues, len(floatValues),
                   c_doubleValues, len(doubleValues))

        if status == 0:
            if len(intValues) > 0:
                intValues[:] = np.ctypeslib.as_array(c_intValues, shape=(len(intValues),))
            if len(floatValues) > 0:
                floatValues[:] = np.ctypeslib.as_array(c_floatValues, shape=(len(floatValues),))
            if len(doubleValues) > 0:
                doubleValues[:] = np.ctypeslib.as_array(c_doubleValues, shape=(len(doubleValues),))


        else:
            print("Error reading array status = {status}")

    def hec_dss_locationRetrieve(self, fullPath: str, x: List[float], y: List[float], z: List[float],
                                 coordinateSystem: List[int], coordinateID: List[int], horizontalUnits: List[int],
                                 horizontalDatum: List[int], verticalUnits: List[int], verticalDatum: List[int],
                                 timeZoneName: List[str], timeZoneNameLength: int, supplemental: List[str],
                                 supplementalLength: int):
        self.dll.hec_dss_locationRetrieve.argtypes = [
            c_void_p,  # dss
            c_char_p,  # fullPath
            POINTER(c_double),  # x
            POINTER(c_double),  # y
            POINTER(c_double),  # z
            POINTER(c_int),  # coordinateSystem
            POINTER(c_int),  # coordinateID
            POINTER(c_int),  # horizontalUnits
            POINTER(c_int),  # horizontalDatum
            POINTER(c_int),  # verticalUnits
            POINTER(c_int),  # verticalDatum
            c_char_p,  # timeZoneName
            c_int,  # timeZoneNameLength
            c_char_p,  # supplemental
            c_int  # supplementalLength
        ]
        self.dll.hec_dss_locationRetrieve.restype = c_int

        c_x = c_double()
        c_y = c_double()
        c_z = c_double()
        c_coordinateSystem = c_int()
        c_coordinateID = c_int()
        c_horizontalUnits = c_int()
        c_horizontalDatum = c_int()
        c_verticalUnits = c_int()
        c_verticalDatum = c_int()
        c_timeZoneName = create_string_buffer(timeZoneNameLength)
        c_supplemental = create_string_buffer(supplementalLength)

        result = self.dll.hec_dss_locationRetrieve(
            self.handle,
            fullPath.encode("utf-8"),
            byref(c_x),
            byref(c_y),
            byref(c_z),
            byref(c_coordinateSystem),
            byref(c_coordinateID),
            byref(c_horizontalUnits),
            byref(c_horizontalDatum),
            byref(c_verticalUnits),
            byref(c_verticalDatum),
            c_timeZoneName,
            timeZoneNameLength,
            c_supplemental,
            supplementalLength
        )

        if result == 0:
            x[0] = c_x.value
            y[0] = c_y.value
            z[0] = c_z.value
            coordinateSystem[0] = c_coordinateSystem.value
            coordinateID[0] = c_coordinateID.value
            horizontalUnits[0] = c_horizontalUnits.value
            horizontalDatum[0] = c_horizontalDatum.value
            verticalUnits[0] = c_verticalUnits.value
            verticalDatum[0] = c_verticalDatum.value
            timeZoneName[0] = c_timeZoneName.value.decode("utf-8")
            supplemental[0] = c_supplemental.value.decode("utf-8")
        # else:
        #     print("Unable to read location information, Function call failed with result:", result)

        return result

    def hec_dss_locationStore(self, location_info, replace: int) -> int:
        self.dll.hec_dss_locationStore.argtypes = [
            c_void_p,  # dss
            c_char_p,  # fullPath
            c_double,  # x
            c_double,  # y
            c_double,  # z
            c_int,  # coordinateSystem
            c_int,  # coordinateID
            c_int,  # horizontalUnits
            c_int,  # horizontalDatum
            c_int,  # verticalUnits
            c_int,  # verticalDatum
            c_char_p,  # timeZoneName
            c_char_p,  # supplemental
            c_int  # replace
        ]
        self.dll.hec_dss_locationStore.restype = c_int

        result = self.dll.hec_dss_locationStore(
            self.handle,
            location_info.id.encode("utf-8"),
            location_info.x[0],
            location_info.y[0],
            location_info.z[0],
            location_info.coordinate_system,
            location_info.coordinate_id,
            location_info.horizontal_units,
            location_info.horizontal_datum,
            location_info.vertical_units,
            location_info.vertical_datum,
            location_info.time_zone_name.encode("utf-8"),
            location_info.supplemental.encode("utf-8"),
            replace
        )

        if result != 0:
            print("Function call failed with result:", result)

        return result

    def hec_dss_delete(self, pathname: str) -> int:
            """
            Deletes a record from the DSS file.

            Args:
                pathname (str): The pathname of the record to delete.

            Returns:
                int: Status of zero when successful, non-zero on error.
            """
            f = self.dll.hec_dss_delete
            f.argtypes = [
                c_void_p,  # dss_file* dss
                c_char_p   # const char* pathname
            ]
            f.restype = c_int

            result = f(self.handle, pathname.encode("utf-8"))

            if result != 0:
                print("Function call failed with result:", result)

            return result

    def hec_dss_textStore(self, pathname, text, length=None):
        """
        Store text data in a DSS file.
        Args:
            pathname (str): The DSS pathname where the text will be stored.
            text (str): The text data to store.
            length (int, optional): The length of the text. If None, it will be set to the length of the text.
        """
        f = self.dll.hec_dss_textStore
        f.argtypes = [
            c_void_p,  # dss
            c_char_p,  # pathname
            c_char_p,  # text
            c_int      # length
        ]
        f.restype = c_int

        result = f(self.handle, pathname.encode("utf-8"),
                    text.encode("utf-8"), 
                    length if length is not None else len(text))
    
        return result
    
    def hec_dss_textRetrieve(self, pathname, buffer :List[str], buff_size: int) -> int:
        """
        Store text data in a DSS file.
        Args:
            pathname (str): The DSS pathname where the text will be stored.
            text (str): The text data to store.
            length (int, optional): The length of the text. If None, it will be set to the length of the text.
        """
        f = self.dll.hec_dss_textRetrieve
        f.argtypes = [
            c_void_p,  # dss
            c_char_p,  # pathname
            c_char_p,  # buffer
            c_int      # buff_size
        ]
        f.restype = c_int

        c_buffer = create_string_buffer(buff_size)
        result = f(self.handle, pathname.encode("utf-8"),
                    c_buffer, 
                    buff_size)
    
        buffer.append(c_buffer.value.decode("utf-8"))
        return result