import ctypes
from ctypes import c_char, c_double, c_int,byref, create_string_buffer
import array


class HecDssNative:
    """Wrapper for Native method calls to hecdss.dll or libhecdss.so """

    def __init__(self):
        self.dll = ctypes.CDLL("hecdss")
    
    def hec_dss_open(self,dss_filename):
        self.dll.hec_dss_open.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self.dll.hec_dss_open.restype = ctypes.c_int
        self.handle = ctypes.c_void_p()
        rval = self.dll.hec_dss_open(dss_filename.encode('utf-8'),ctypes.byref(self.handle))
        if rval == 0:
            print("DSS file opened successfully.")
        else:
            print("Error opening DSS file.")
        return rval

    def hec_dss_close(self):
        f = self.dll.hec_dss_close
        f.argtypes = [ctypes.c_void_p()]
        f.restype = ctypes.c_int
        return f(self.handle)
		
    def hec_dss_record_count(self):
        f = self.dll.hec_dss_record_count
        f.argtypes = [ctypes.c_void_p()]
        f.restype = ctypes.c_int
        return f(self.handle)

    # set a integer setting by name
    def __hec_dss_set_value(self,name,value):
        f = self.dll.hec_dss_set_value
        f.argtypes = [ctypes.c_char_p,ctypes.c_int]
        f.restype = ctypes.c_int
        f(name.encode('utf-8'),value)

    # set debug level (0-15)
    # 0 - no output
    # 15 - max output
    def hec_dss_set_debug_level(self,value):
        self.__hec_dss_set_value("mlvl",value)

    

    def hec_dss_export_to_file(self,path,outputFile,startDate,startTime,endDate,endTime):
        
        self.dll.hec_dss_export_to_file.argtypes = [
            ctypes.c_void_p(),  # dss
            ctypes.c_char_p,  # path
            ctypes.c_char_p,  # outputFile
            ctypes.c_char_p,  # startDate
            ctypes.c_char_p,  # startTime
            ctypes.c_char_p,  # endDate
            ctypes.c_char_p   # endTime
        ]
        self.dll.hec_dss_export_to_file.restype = ctypes.c_int

        result = self.dll.hec_dss_export_to_file(self.handle,path, outputFile, startDate, startTime, endDate, endTime)

    def hec_dss_CONSTANT_MAX_PATH_SIZE(self): 
        f = self.dll.hec_dss_CONSTANT_MAX_PATH_SIZE
        f.restype = ctypes.c_int
        return f()

    def hec_dss_catalog(self,filter=""):
        """
        retrieves a list of objects in a DSS database

        returns a list of paths, and recordTypes

        """
        count = self.hec_dss_record_count()
        pathBufferSize = self.hec_dss_CONSTANT_MAX_PATH_SIZE()
        self.dll.hec_dss_catalog.argtypes = [
            ctypes.c_void_p,        # dss (assuming it's a pointer)
            ctypes.c_char_p,        # pathBuffer
            ctypes.POINTER(ctypes.c_int),  # recordTypes
            ctypes.c_char_p,        # pathFilter
            ctypes.c_int,           # count
            ctypes.c_int            # pathBufferItemSize
        ]
        self.dll.hec_dss_catalog.restype = ctypes.c_int

        c_rawCatalog = create_string_buffer(count * pathBufferSize)
        pathFilter = filter.encode("ascii")
        recordTypes = (ctypes.c_int32 * count)()

        pathNameList = []
        
        numRecords = self.dll.hec_dss_catalog(self.handle,c_rawCatalog, recordTypes, pathFilter, count, pathBufferSize)
        recordTypeArray =[]
        recordTypeArray.extend(list(recordTypes[:count]))
        for i in range(numRecords):
            start = i * pathBufferSize
            end = start + pathBufferSize
            s = c_rawCatalog[start:end].decode('ascii').replace('\x00','')
            #print(f"str='{s}'")
            pathNameList.append(s)
        
        return pathNameList,recordTypeArray


    def hec_dss_tsGetSizes(self,pathname,
                            startDate, startTime,
                            endDate, endTime,numberValues,qualityElementSize):
        self.dll.hec_dss_tsGetSizes.argtypes = [
            ctypes.c_void_p(), # dss
            ctypes.c_char_p,  # path
            ctypes.c_char_p,  # startDate
            ctypes.c_char_p,  # startTime
            ctypes.c_char_p,  # endDate
            ctypes.c_char_p,  # endTime
            ctypes.POINTER(ctypes.c_int), #numberValues
            ctypes.POINTER(ctypes.c_int)  #qualityElementSize
        ]
        self.dll.hec_dss_tsGetSizes.restype = ctypes.c_int
        
        nv = ctypes.c_int()
        qes = ctypes.c_int()

        result = self.dll.hec_dss_tsGetSizes(self.handle, pathname.encode('utf-8'),
                                            startDate.encode('utf-8'), startTime.encode('utf-8'),
                                            endDate.encode('utf-8'), endTime.encode('utf-8'),
                                            ctypes.byref(nv),
                                            ctypes.byref(qes))

        numberValues[0] = nv.value
        qualityElementSize[0] = qes.value
        #import pdb;pdb.set_trace()

        if result == 0:
            print("Function call successful:")
            print("Number of values:", numberValues[0])
            print("Quality element size:", qualityElementSize[0])
        else:
            print("Function call failed with result:", result)

        return result
        
    def hec_dss_tsRetrieve(self,pathname, 
        startDate, startTime, endDate, endTime, 
        times, values, arraySize,
        numberValuesRead, quality, qualityLength, 
        julianBaseDate, timeGranularitySeconds,
        units, unitsLength, dataType, typeLength):

        f = self.dll.hec_dss_tsRetrieve
        f.argtypes = [
            ctypes.c_void_p,           # dss
            ctypes.c_char_p,           # pathname
            ctypes.c_char_p,           # startDate
            ctypes.c_char_p,           # startTime
            ctypes.c_char_p,           # endDate
            ctypes.c_char_p,           # endTime
            ctypes.POINTER(ctypes.c_int),    # timeArray
            ctypes.POINTER(ctypes.c_double), # valueArray
            ctypes.c_int,              # arraySize
            ctypes.POINTER(ctypes.c_int),    # numberValuesRead
            ctypes.POINTER(ctypes.c_int),    # quality
            ctypes.c_int,               # qualityLength
            ctypes.POINTER(ctypes.c_int),    # julianBaseDate
            ctypes.POINTER(ctypes.c_int),    # timeGranularitySeconds
            ctypes.c_char_p,           # units
            ctypes.c_int,              # unitsLength
            ctypes.c_char_p,           # dataType
            ctypes.c_int               # typeLength
            ]
        f.restype = ctypes.c_int

        c_arraySize = c_int(arraySize)
        c_times = (ctypes.c_int32 * arraySize)()
        c_values = (c_double * arraySize)()
        c_numberValuesRead = c_int(0)
        size = qualityLength*arraySize

        c_quality =(c_int * size)()
        c_julianBaseDate = c_int(0)
        c_timeGranularitySeconds = c_int(0)
  
        buff_size = unitsLength
        c_units = create_string_buffer(buff_size)
        c_unitsLength = c_int(buff_size)
  
        buff_size = typeLength
        c_dataType = create_string_buffer(buff_size)
        c_typeLength =  c_int(buff_size)
        c_julianBaseDate = c_int()
        c_timeGranularitySeconds = c_int()

        rval = f(self.handle,
          pathname.encode('utf-8'), 
          startDate.encode('utf-8'),
          startTime.encode('utf-8'), 
          endDate.encode('utf-8'), 
          endTime.encode('utf-8'), 
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
          c_typeLength)

        times.clear()
        times.extend(list(c_times[:c_numberValuesRead.value]))
        values.clear()
        values.extend(list(c_values[:c_numberValuesRead.value]))
        units[0] = c_units.value.decode('utf-8')
        dataType[0] = c_dataType.value.decode('utf-8')
        julianBaseDate[0] = c_julianBaseDate.value
        timeGranularitySeconds[0] = c_timeGranularitySeconds.value

        return rval

		

    def hec_dss_tsStoreRegular(self, pathname, startDate, startTime, valueArray, qualityArray,
                                    saveAsFloat, units, dataType): 

        self.dll.hec_dss_tsStoreRegular.restype = ctypes.c_int
        self.dll.hec_dss_tsStoreRegular.argtypes = [
        ctypes.c_void_p,    # dss (void*)
        ctypes.c_char_p,    # pathname (const char*)
        ctypes.c_char_p,    # startDate (const char*)
        ctypes.c_char_p,    # startTime (const char*)
        ctypes.POINTER(ctypes.c_double),  # valueArray (double*)
        ctypes.c_int,       # valueArraySize (int)
        ctypes.POINTER(ctypes.c_int),     # qualityArray (int*)
        ctypes.c_int,       # qualityArraySize (int)
        ctypes.c_int,       # saveAsFloat (int)
        ctypes.c_char_p,    # units (const char*)
        ctypes.c_char_p    # type (const char*)
        ]

        pathname_c = ctypes.c_char_p(pathname.encode("utf-8"))
        startDate_c = ctypes.c_char_p(startDate.encode("utf-8"))
        startTime_c = ctypes.c_char_p(startTime.encode("utf-8"))
        units_c = ctypes.c_char_p(units.encode("utf-8"))
        type_c = ctypes.c_char_p(dataType.encode("utf-8"))
        
        print(valueArray)
        valueArray_c = (ctypes.c_double * len(valueArray))(*valueArray)
        qualityArray_c = (ctypes.c_int * len(qualityArray))(*qualityArray)
        #import pdb;pdb.set_trace()
        return self.dll.hec_dss_tsStoreRegular(self.handle, pathname_c, startDate_c, startTime_c,
                                            valueArray_c, len(valueArray), qualityArray_c,
                                            len(qualityArray), int(saveAsFloat), units_c, type_c)



    def test():
        dss = HecDssNative()
        outputFile=b"output.txt"

        dss.hec_dss_open(b"sample7.dss")
        nnn = dss.hec_dss_record_count()
        print ("record count = "+str(nnn))		


        times = [0,0,0,0,0]
        numberValues =len(times)
        times_int = (ctypes.c_int * numberValues)(*times)
        values = [0,0,0,0,0]
        values_double = (ctypes.c_double * numberValues)(*values)

        numberValuesRead = ctypes.c_int()
        quality = []
        qualityLength = ctypes.c_int(len(quality))
        quality_int = (ctypes.c_int * len(quality))(*quality)

        julianBaseDate = ctypes.c_int()
        timeGranularitySeconds = ctypes.c_int()
        buffer_size = 20
        units = ctypes.create_string_buffer(buffer_size)
        dataType = ctypes.create_string_buffer(buffer_size)

        result = dss.hec_dss_tsRetrieve(b"//SACRAMENTO/PRECIP-INC//1Day/OBS/", 
                b"01Jan1924",b"0100", b"01Jan2005", b"2400", times_int, values_double, numberValues,
                ctypes.byref(numberValuesRead), quality_int, qualityLength, ctypes.byref(julianBaseDate), ctypes.byref(timeGranularitySeconds),
                units, buffer_size, dataType, buffer_size)

        if result == 0:
            print("Function call successful.")
        else:
            print("Function call failed."+str(result))

        print(units.value.decode('utf-8'))


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