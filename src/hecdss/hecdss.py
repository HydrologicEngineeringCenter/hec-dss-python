from hec_dss_native import HecDssNative
from dateconverter import DateConverter
from timeseries import TimeSeries
from catalog import Catalog


class HecDss:

    def __init__(self,filename):
        self._native = HecDssNative()
        self._native.hec_dss_open(filename)
	

    def get(self,pathname,startDateTime, endDateTime):
        # get sizes

        #BE SURE THAT DATETIME STUFF IS IN THE PROPER DATETIMESTAMP FORMAT
        startDate = startDateTime.strftime('%d%b%Y')
        startTime = startDateTime.strftime('%H:%M')
        endDate = endDateTime.strftime('%d%b%Y')
        endTime = startDateTime.strftime('%H:%M')
        numberValues = [0] # using array to allow modification
        qualityElementSize = [0]
        numberValues, qualityElementSize = self._native.hec_dss_tsGetSizes(pathname,
                            startDate, startTime,
                            endDate, endTime,numberValues,qualityElementSize)

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
            values, numberValues,
            numberValuesRead,
            quality, 
            qualityElementSize, 
            julianBaseDate, 
            timeGranularitySeconds,
            units, 
            bufferLength, 
            dataType, 
            bufferLength)


        ts = TimeSeries()
        ts.times=DateConverter.date_times_from_julian_array(times,timeGranularitySeconds[0],julianBaseDate[0])
        ts.values=values
        ts.units=units[0]
        ts.dataType=dataType[0]
        ts.dsspath=pathname
        ts.timeGranularity=timeGranularitySeconds[0]
        return ts
    
    def put(self,ts):
        #Timeseries should be already created using the TimeSeries object defined in timeseries.py

        # TO DO.. save other types besides regular interval.
        # TO DO. check data type..
        # TO Do. is timezone needed?
        #def hec_dss_tsStoreRegular(dss, pathname, startDate, startTime, valueArray, qualityArray,
        #                           saveAsFloat, units, type):
        min_datetime = min(ts.times)
        startDate, startTime = DateConverter.dss_datetime_from_string(min_datetime)
        quality = []  # TO DO

        # tsRetrive
        #convert times to HEC DSS format
        #ts.times = DateConverter.julian_times_from_datetime_array(ts.times, ts.timeGranularity)
        #print('time conversion done')
        print('Storing function called')

        self._native.hec_dss_tsStoreRegular(ts.pathname,startDate,startTime,ts.values,quality,False,ts.units,ts.dataType)
    
    #Timeseries
    def createNewTimeseries(self, pathname, arr, units, dataType, timeGranularitySeconds, time_pos=0, val_pos=1):
        '''
        This function creates a new timeseries, using an array. See the Timeseries object for reference.
        '''
        new_ts = TimeSeries()
        new_ts.units = str(units)
        new_ts.pathname = str(pathname)
        new_ts.dataType = str(dataType)
        new_ts.timeGranularity = int(timeGranularitySeconds)

        #Adding data
        new_ts.array_to_data(arr, time_pos, val_pos)

        return new_ts

    
    def getCatalog(self):
        paths,recordTypes = self._native.hec_dss_catalog()
        return Catalog(paths,recordTypes)

    def recordCount(self):
        return self._native.hec_dss_record_count()

    def setDebugLevel(self,level):
        return self._native.hec_dss_set_debug_level(level)


#if __name__ == "__main__":
#    #import pdb;pdb.set_trace()
#    dss = HecDss("sample7.dss")
#    catalog = dss.getCatalog()
#    for p in catalog:
#        print(p)
    #print(catalog[0:5])
    #dss.setDebugLevel(15)
