from hec_dss_native import HecDssNative
from datetime import datetime
from dateconverter import DateConverter
from timeseries import TimeSeries

class HecDss:

    def __init__(self,filename):
        self._native = HecDssNative()
        self._native.hec_dss_open(filename)
	
    def get(self,pathname,startDateTime, endDateTime):
        # get sizes
        startDate = startDateTime.strftime('%d%b%Y')
        startTime = startDateTime.strftime('%H:%M')
        endDate = endDateTime.strftime('%d%b%Y')
        endTime = startDateTime.strftime('%H:%M')
        numberValues = [0] # using array to allow modification
        qualityElementSize = [0]
        self._native.hec_dss_tsGetSizes(pathname,
                            startDate, startTime,
                            endDate, endTime,numberValues,qualityElementSize)
        print("Number of values:", numberValues[0])
        print("Quality element size:", qualityElementSize[0])

        
        # tsRetrive

        times=[0,1]
        values=[]
        numberValuesRead=[0]
        quality=[]
        julianBaseDate =[0]
        timeGranularitySeconds =[0]
        units = [""]
        bufferLength=40
        dataType =[""]


        self._native.hec_dss_tsRetrieve(pathname, 
            startDate, startTime, endDate, endTime, times,
            values, numberValues[0],
            numberValuesRead, quality, qualityElementSize[0], 
            julianBaseDate, timeGranularitySeconds,
            units, bufferLength, dataType, bufferLength)

        #print("units = "+units[0])
        #print("datatype = "+dataType[0])
        #print("times: ")
        #print(times)
        #print(values)
        print("julianBaseDate = "+str(julianBaseDate[0]))
        print("timeGranularitySeconds = "+str(timeGranularitySeconds[0]))
        ts = TimeSeries()
        ts.times=DateConverter.date_times_from_julian_array(times,timeGranularitySeconds[0],julianBaseDate[0])
        ts.values=values
        ts.units=units[0]
        ts.dataType=dataType[0]
        ts.dsspath=pathname
        return ts

    def recordCount(self):
        return self._native.hec_dss_record_count()
			
#import pdb;pdb.set_trace()
dss = HecDss("sample7.dss")
print("record count = "+str(dss.recordCount()))
t1 = datetime(2005, 1, 1)
t2 = datetime(2005, 1 ,4)
tsc = dss.get("//SACRAMENTO/PRECIP-INC//1Day/OBS/",t1,t2)
tsc.print_to_console()