from datetime import datetime

from hecdss.hecdss import HecDss
from hecdss.hecdss import TimeSeries


class DssWriter:

    def __init__(self, filename):
        self.filename = filename

    def write_to_dss(self ,df, path):

        if len(df.columns) != 1:
            raise ValueError("DataFrame should contain only one column of data.")

        dss = HecDss(self.filename)
        print("record count = " + str(dss.record_count()))
        tsc = TimeSeries()
        tsc.id = path
        tsc.values = df[df.columns[0]].values.astype(float)
        tsc.times = df.index.tolist()
        tsc.units = df.units
        tsc.dataType = df.data_type

        dss.put(tsc)
        dss.close()

