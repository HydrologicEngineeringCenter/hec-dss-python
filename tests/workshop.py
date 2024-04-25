
"""Pytest module."""

import unittest
import sys
from test_file_manager import TestFileManager
sys.path.append(r'src')
import copy

from hecdss import Catalog, HecDss
from datetime import datetime



def test_record_type():
    print("--------------------- test_record_type --------------")
    dss = HecDss(r"c:\tmp\sample7.dss")
    catalog = dss.get_catalog()
    path = "/FISHKILL CREEK/BEACON NY/FREQ-FLOW///USGS/"
    pd = dss.get(path)
    print(pd.values)

    pd.labels = ['Flow']

    print(pd.labels)

    pd2 = copy.deepcopy(pd)
    pd2.id ="/MY BASIN/DEER CREEK/STAGE-FLOW///USGS-modified/"
    pd2.labels = ['Flow2']
    pd2.units_independent = "data"

    print(pd2.labels)

    status = dss.put(pd2)  # save

    print(status)

    path = "/MY BASIN/DEER CREEK/STAGE-FLOW///USGS-modified/"
    pd3 = dss.get(path)
    dss.close()

    print(f"saved labels: {pd3.labels}")
    print(f"saved units: {pd3.units_independent}")
    # assert(1,len(pd.labels))
    # assert("Flow",pd3.labels[0])

    #entry =catalog.items[0]
    #print(entry)
    #rt = dss.get_record_type(str(entry))
    #print(f"record type = {rt}")

test_record_type()


