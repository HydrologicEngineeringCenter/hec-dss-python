
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
    #entry =catalog.items[0]
    #print(entry)
    #rt = dss.get_record_type(str(entry))
    #print(f"record type = {rt}")

test_record_type()


