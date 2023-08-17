import ctypes


DLL_PATH=r"C:\project\hec-dss\heclib\hecdss\x64\Release\hecdss.dll"

class HecDss:

    #def init():
    def open(self,dss_filename, check=False):
        self.dss_dll = ctypes.cdll.LoadLibrary(DLL_PATH)
        prototype_hec_dss_open = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p))
        hec_dss_open = prototype_hec_dss_open(("hec_dss_open", self.dss_dll))
        self.handle = ctypes.c_void_p()
        result = hec_dss_open(dss_filename.encode('utf-8'), ctypes.byref(self.handle))
        if check:
            # Check the result to see if the function call was successful
            if result == 0:
                print("hec_dss_open succeeded!")
                # Now you can use dss_file_ptr to access the struct or pass it to other functions as needed.
            else:
                print("hec_dss_open failed with error code:", result)

    def close(self,):
        dss_f = self.dss_dll.hec_dss_close
        #dss_f.argtypes = [self.handle]
        dss_f.argtypes = [ctypes.c_void_p()]
        dss_f.restype = ctypes.c_int

        return dss_f(self.handle)

    def record_count(self):
        dss_f = self.dss_dll.hec_dss_record_count
        #dss_f.argtypes = [self.handle]
        dss_f.argtypes = [ctypes.c_void_p()]
        dss_f.restype = ctypes.c_int

        return dss_f(self.handle)


    def read_timeseries(self):
        [numberValues,qualityElementSize] = self.get_sizes(selfpathname)
        pass

    def get_sizes(self):
        self.dss_dll.hec_dss_tsGetSizes.argtypes = [ ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) ]
        self.dss_dll.hec_dss_tsGetSizes.restype = ctypes.c_int
        
        numberValues = ctypes.c_int()
        qualityElementSize = ctypes.c_int()

         

        result = self.dss_dll.hec_dss_tsGetSizes(self.handle, pathname,
                                            startDate, startTime,
                                            endDate, endTime,
                                            ctypes.byref(numberValues),
                                            ctypes.byref(qualityElementSize))

        import pdb;pdb.set_trace()

        if result == 0:
            print("Function call successful:")
            print("Number of values:", numberValues.value)
            print("Quality element size:", qualityElementSize.value)
            return [ctypes.byref(numberValues), ctypes.byref(qualityElevmentSize)]
        else:
            print("Function call failed with result:", result)
            return [0,0]


ppp = "/AMERICAN/FOLSOM/FLOW-RES IN//1Day/OBS/"
sd = "12MAR2006"
ed = "05APR2006"
st = "1200"
et = "1200"
dss = HecDss()

dss.open(r"sample7.dss")
nnn = dss.record_count()
print ("record count = "+str(nnn))

#ttt = dss.read_timeseries(ppp,sd,st,ed,et)
dss.close()