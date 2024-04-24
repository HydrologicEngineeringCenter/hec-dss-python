import ctypes
from ctypes import c_float, c_double, c_char_p, c_int, c_void_p,POINTER
from ctypes import c_int32
from ctypes import byref, create_string_buffer
from ctypes.util import find_library
import os
import sys
from typing import List

class _Native:
    """Wrapper for Native method calls to hecdss.dll or libhecdss.so"""

    def __init__(self):
        if sys.platform == "linux" or sys.platform == "darwin":
            libc_path = (
                "libhecdss.so"
                if find_library("libhecdss")
                else os.path.join(os.environ["LD_LIBRARY_PATH"], "libhecdss.so")
            )
            self.dll = ctypes.CDLL(libc_path)
        elif sys.platform == "win32":
            self.dll = ctypes.CDLL("hecdss")
        else:
            raise Exception("Unsupported platform")

    def hec_dss_open(self, dss_filename: str):
        f = self.dll.hec_dss_open
        f.argtypes = [
            c_char_p,
            POINTER(c_void_p),
        ]
        f.restype = c_int
        self.handle = c_void_p()
        rval = f(dss_filename.encode("utf-8"), ctypes.byref(self.handle))
        if rval == 0:
            print("DSS file opened successfully.")
        else:
            print("Error opening DSS file.")
        return rval

    def hec_dss_close(self):
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
    def __hec_dss_set_value(self, name:str, value:int):
        f = self.dll.hec_dss_set_value
        f.argtypes = [c_char_p, c_int]
        f.restype = c_int
        f(name.encode("utf-8"), value)

    # set debug level (0-15)
    # 0 - no output
    # 15 - max output
    def hec_dss_set_debug_level(self, value:int):
        self.__hec_dss_set_value("mlvl", value)

    def hec_dss_export_to_file(
        self, path:str, outputFile:str, startDate:str, startTime:str, endDate:str, endTime:str
    ):
        f=self.dll.hec_dss_export_to_file
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

    def hec_dss_pdRetrieveInfo(self, pathname,
                               numberOrdinates:List[int], numberCurves:List[int],
                               unitsIndependent:List[str],
                               unitsDependent:List[str],
                               typeIndependent:List[str],
                               typeDependent:List[str],
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
        c_unitsDependent= create_string_buffer(buff_size)
        c_typeIndependent= create_string_buffer(buff_size)
        c_typeDependent= create_string_buffer(buff_size)

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

        numberOrdinates[0] = numberOrdinates_val.value
        numberCurves[0] = numberCurves_val.value
        labelsLength[0] = labelsLength_val.value

#units[0] = c_units.value.decode("utf-8")
        unitsIndependent[0] = c_unitsIndependent.value.decode('utf-8')
        unitsDependent[0] = c_unitsDependent.value.decode('utf-8')
        typeIndependent[0] = c_typeIndependent.value.decode('utf-8')
        typeDependent[0] = c_typeDependent.value.decode('utf-8')

        if result == 0:
            print("Function call successful:")
            print("Number of ordinates:", numberOrdinates[0])
            print("Number of curves:", numberCurves[0])
            print("Labels length:", labelsLength[0])
        else:
            print("Function call failed with result:", result)

        return result

    def hec_dss_pdRetrieve(self, pathname:str,
                           doubleOrdinates:List[float], doubleOrdinatesLength:int,
                           doubleValues:List[float], doubleValuesLength:int,
                           numberOrdinates:List[int], numberCurves:List[int],
                           unitsIndependent:List[str], unitsIndependentLength:int,
                           typeIndependent:List[str],typeIndependentLength:int,
                           unitsDependent:List[str], unitsDependentLength:int,
                           typeDependent:List[str], typeDependentLength:int,
                           labels:List[str], labelsLength:int):

        self.dll.hec_dss_pdRetrieve.argtypes = [c_void_p, c_char_p,
                                           POINTER(c_double), c_int,
                                           POINTER(c_double), c_int,
                                           POINTER(c_int), POINTER(c_int),
                                           c_char_p, c_int,
                                           c_char_p, c_int,
                                           c_char_p, c_int,
                                           c_char_p, c_int,
                                           c_char_p, c_int]

        self.dll.hec_dss_pdRetrieve.restype = c_int

        c_doubleOrdinates = ( c_double * doubleOrdinatesLength)()
        c_doubleValues =  ( c_double * doubleValuesLength)()
        c_numberOrdinates = c_int()
        c_numberCurves = c_int()

        c_labels = create_string_buffer(labelsLength)
        c_unitsIndependent = create_string_buffer(unitsIndependentLength)
        c_unitsDependent = create_string_buffer(unitsDependentLength)
        c_typeIndependent = create_string_buffer(typeIndependentLength)
        c_typeDependent = create_string_buffer(typeDependentLength)

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
                                        c_labels, labelsLength)

        unitsIndependent[0] = c_unitsIndependent.value.decode('utf-8')
        unitsDependent[0] = c_unitsDependent.value.decode('utf-8')
        typeIndependent[0] = c_typeIndependent.value.decode('utf-8')
        typeDependent[0] = c_typeDependent.value.decode('utf-8')

        doubleOrdinates.extend(list(c_doubleOrdinates))
        doubleValues.extend(list(c_doubleValues))
        numberOrdinates[0]=c_numberOrdinates
        numberCurves[0]=c_numberCurves
        labels.extend(c_labels.value.decode('utf-8').split("\0"))

        if result == 0:
            print("Function call successful:")
            print("ordinates:", doubleOrdinates)
            print("curves:", doubleValues)
            print("Labels length:", labels)
        else:
            print("Function call failed with result:", result)

        return result

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
            ctypes.byref(nv),
            ctypes.byref(qes),
        )

        numberValues[0] = nv.value
        qualityElementSize[0] = qes.value
        # import pdb;pdb.set_trace()

        if result == 0:
            print("Function call successful:")
            print("Number of values:", numberValues[0])
            print("Quality element size:", qualityElementSize[0])
        else:
            print("Function call failed with result:", result)

        return result

    def hec_dss_tsRetrieve(
        self,
        pathname:str,
        startDate:str,
        startTime:str,
        endDate:str,
        endTime:str,
        times:List[int],
        values:List[float],
        arraySize:str,
        numberValuesRead,
        quality,
        qualityLength:int,
        julianBaseDate:int,
        timeGranularitySeconds:int,
        units:List[str],
        unitsLength:int,
        dataType:List[str],
        typeLength:int,
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
        )

        times.clear()
        times.extend(list(c_times[: c_numberValuesRead.value]))
        values.clear()
        values.extend(list(c_values[: c_numberValuesRead.value]))
        units[0] = c_units.value.decode("utf-8")
        dataType[0] = c_dataType.value.decode("utf-8")
        julianBaseDate[0] = c_julianBaseDate.value
        timeGranularitySeconds[0] = c_timeGranularitySeconds.value

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
        ]

        pathname_c = c_char_p(pathname.encode("utf-8"))
        startDate_c = c_char_p(startDate.encode("utf-8"))
        startTime_c = c_char_p(startTime.encode("utf-8"))
        units_c = c_char_p(units.encode("utf-8"))
        type_c = c_char_p(dataType.encode("utf-8"))

        print(valueArray)
        valueArray_c = (c_double * len(valueArray))(*valueArray)
        qualityArray_c = (c_int * len(qualityArray))(*qualityArray)
        # import pdb;pdb.set_trace()
        return self.dll.hec_dss_tsStoreRegular(
            self.handle,
            pathname_c,
            startDate_c,
            startTime_c,
            valueArray_c,
            len(valueArray),
            qualityArray_c,
            len(qualityArray),
            int(saveAsFloat),
            units_c,
            type_c,
        )

    def hec_dss_gridRetrieve(self,dss, pathname, boolRetrieveData, type_, dataType,
                         lowerLeftCellX, lowerLeftCellY, numberOfCellsX, numberOfCellsY,
                         numberOfRanges, srsDefinitionType, timeZoneRawOffset, isInterval,
                         isTimeStamped, dataUnits, dataUnitsLength, dataSource, dataSourceLength,
                         srsName, srsNameLength, srsDefinition, srsDefinitionLength, timeZoneID,
                         timeZoneIDLength, cellSize, xCoordOfGridCellZero, yCoordOfGridCellZero,
                         nullValue, maxDataValue, minDataValue, meanDataValue, rangeLimitTable,
                         rangeTablesLength, numberEqualOrExceedingRangeLimit, data, dataLength):
    
    # Define the argument types for the C function
        self.dll.hec_dss_gridRetrieve.argtypes = [
        POINTER(dss),             # dss_file* dss
        c_char_p,                 # const char* pathname
        c_int,                    # int boolRetrieveData
        POINTER(c_int),    # int* type
        POINTER(c_int),    # int* dataType
        POINTER(c_int),    # int* lowerLeftCellX
        POINTER(c_int),    # int* lowerLeftCellY
        POINTER(c_int),    # int* numberOfCellsX
        POINTER(c_int),    # int* numberOfCellsY
        POINTER(c_int),    # int* numberOfRanges
        POINTER(c_int),    # int* srsDefinitionType
        POINTER(c_int),    # int* timeZoneRawOffset
        POINTER(c_int),    # int* isInterval
        POINTER(c_int),    # int* isTimeStamped
        c_char_p,                 # char* dataUnits
        c_int,                    # const int dataUnitsLength
        c_char_p,                 # char* dataSource
        c_int,                    # const int dataSourceLength
        c_char_p,                 # char* srsName
        c_int,                    # const int srsNameLength
        c_char_p,                 # char* srsDefinition
        c_int,                    # const int srsDefinitionLength
        c_char_p,                 # char* timeZoneID
        c_int,                    # const int timeZoneIDLength
        POINTER(c_float),  # float* cellSize
        POINTER(c_float),  # float* xCoordOfGridCellZero
        POINTER(c_float),  # float* yCoordOfGridCellZero
        POINTER(c_float),  # float* nullValue
        POINTER(c_float),  # float* maxDataValue
        POINTER(c_float),  # float* minDataValue
        POINTER(c_float),  # float* meanDataValue
        POINTER(c_float),  # float* rangeLimitTable
        c_int,                    # const int rangeTablesLength
        POINTER(c_int),    # int* numberEqualOrExceedingRangeLimit
        POINTER(c_float),  # float* data
        c_int                     # const int dataLength
        ]

        # Define the return type for the C function
        self.dll.hec_dss_gridRetrieve.restype = c_int

        # Call the C function
        return self.dll.hec_dss_gridRetrieve(
        dss, pathname, boolRetrieveData, type_, dataType, 
        lowerLeftCellX, lowerLeftCellY, numberOfCellsX, numberOfCellsY,
        numberOfRanges, srsDefinitionType, timeZoneRawOffset, isInterval,
        isTimeStamped, dataUnits, dataUnitsLength, dataSource, dataSourceLength,
        srsName, srsNameLength, srsDefinition, srsDefinitionLength, timeZoneID,
        timeZoneIDLength, cellSize, xCoordOfGridCellZero, yCoordOfGridCellZero,
        nullValue, maxDataValue, minDataValue, meanDataValue, rangeLimitTable,
        rangeTablesLength, numberEqualOrExceedingRangeLimit, data, dataLength)

    def hec_dss_recordType(self, pathname):
        f= self.dll.hec_dss_recordType
        f.argtypes = [
            c_void_p,
            c_char_p
            ]
        f.restype = c_int
        c_str = c_char_p(pathname.encode("utf-8"))
        return f(self.handle,c_str)


    def test():
        dss = HecDssNative()
        outputFile = b"output.txt"

        dss.hec_dss_open(b"sample7.dss")
        nnn = dss.hec_dss_record_count()
        print("record count = " + str(nnn))

        times = [0, 0, 0, 0, 0]
        numberValues = len(times)
        times_int = (c_int * numberValues)(*times)
        values = [0, 0, 0, 0, 0]
        values_double = (c_double * numberValues)(*values)

        numberValuesRead = c_int()
        quality = []
        qualityLength = c_int(len(quality))
        quality_int = (c_int * len(quality))(*quality)

        julianBaseDate = c_int()
        timeGranularitySeconds = c_int()
        buffer_size = 20
        units = ctypes.create_string_buffer(buffer_size)
        dataType = ctypes.create_string_buffer(buffer_size)

        result = dss.hec_dss_tsRetrieve(
            b"//SACRAMENTO/PRECIP-INC//1Day/OBS/",
            b"01Jan1924",
            b"0100",
            b"01Jan2005",
            b"2400",
            times_int,
            values_double,
            numberValues,
            ctypes.byref(numberValuesRead),
            quality_int,
            qualityLength,
            ctypes.byref(julianBaseDate),
            ctypes.byref(timeGranularitySeconds),
            units,
            buffer_size,
            dataType,
            buffer_size,
        )

        if result == 0:
            print("Function call successful.")
        else:
            print("Function call failed." + str(result))

        print(units.value.decode("utf-8"))

        # ppp = b"/AMERICAN/FOLSOM/FLOW-RES IN/01JAN2006/1Day/OBS/"
        # sd = b"12MAR2006"
        # ed = b"05APR2006"
        # st = b"1200"
        # et = b"1200"
        # dss = HecDss()
        # outputFile=b"output.txt"
        #
        # dss.open("sample7.dss")
        # nnn = dss.record_count()
        # print ("record count = "+str(nnn))
        # ttt = dss.hec_dss_export_to_file(ppp,outputFile,sd,st,ed,et)
        # dss.close()




