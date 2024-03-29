from datetime import datetime

from hecdss.hec_dss import HecDss
from hecdss.hec_dss import TimeSeries


class DssWriter:

    def __init__(self, filename):
        self.filename = filename

    def write_to_dss(self ,df, path):

        if len(df.columns) != 1:
            raise ValueError("DataFrame should contain only one column of data.")

        dss = HecDss(self.filename)
        print("record count = " + str(dss.recordCount()))
        tsc = TimeSeries()
        tsc.dsspath = path
        tsc.values = df[df.columns[0]].values.astype(float)
        tsc.times = df.index.tolist()

        dss.put(tsc)
        dss.close()

