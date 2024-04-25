"""Docstring for public module."""
from hecdss.PairedData import PairedData
from hecdss.native import _Native
from hecdss.dateconverter import DateConverter
from hecdss.record_type import RecordType
from hecdss.timeseries import TimeSeries
from hecdss.catalog import Catalog


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
        print(f"hec_dss_recordType for '{pathname}' is {rt}")
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
        elif type == "grid":
            pass
        return

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
        print("Number of Ordinates:", numberOrdinates[0])
        print("Number of Curves:", numberCurves[0])
        print("length of labels:", labelsLength[0])

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
        pd.ordinates = doubleOrdinates

        n = numberCurves2[0].value
        pd.values = [doubleValues[i:i+n] for i in range(0, len(doubleValues), n)]

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
        print("Number of values:", numberValues[0])
        print("Quality element size:", qualityElementSize[0])

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
        print("julianBaseDate = " + str(julianBaseDate[0]))
        print("timeGranularitySeconds = " + str(timeGranularitySeconds[0]))
        ts = TimeSeries()
        ts.times = DateConverter.date_times_from_julian_array(
            times, timeGranularitySeconds[0], julianBaseDate[0]
        )
        ts.values = values
        ts.units = units[0]
        ts.dataType = dataType[0]
        ts.id = pathname
        return ts

    def put(self, rt):
        # TO DO.. save other types besides regular interval.
        # TO DO. check data type..
        # TO Do. is timezone needed?

        if type(rt) is TimeSeries:
            ts = rt
            # def hec_dss_tsStoreRegular(dss, pathname, startDate, startTime, valueArray, qualityArray,
            #                           saveAsFloat, units, type):
            startDate, startTime = DateConverter.dss_datetime_from_string(ts.times[0])
            quality = []  # TO DO

            self._native.hec_dss_tsStoreRegular(
                ts.id,
                startDate,
                startTime,
                ts.values,
                quality,
                False,
                ts.units,
                ts.dataType,
            )

        elif type(rt) is PairedData:
            pd = rt
            print(pd)
            return self._native.hec_dss_pdStore(pd)

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
