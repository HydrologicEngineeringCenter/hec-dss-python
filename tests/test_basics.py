"""Pytest module."""

import sys
sys.path.append(r'src')

from hecdss import Catalog, HecDss
from datetime import datetime



TEST_FP = "tests/data/sample7.dss"


def test_issue9():
    dss = HecDss(TEST_FP)
    pathnames = [
        "//SACRAMENTO/PRECIP-INC//1Day/OBS/",
        "/EF RUSSIAN/COYOTE/PRECIP-INC//1Hour/TB/"
        "/GREEN RIVER/OAKVILLE/ELEVATION//1Hour//",
    ]
    t1 = datetime(2006, 3, 1)
    t2 = datetime(2006, 3, 30)
    for path in pathnames:
        print(f"reading {path}")
        tsc = dss.get(path, t1, t2)
        print(f"len(tsc.values) = {len(tsc.values)}")
        assert len(tsc.values) > 1


def test_basic():
    dss = HecDss(TEST_FP)
    print("record count = " + str(dss.recordCount()))

    t1 = datetime(2005, 1, 1)
    t2 = datetime(2005, 1, 4)
    tsc = dss.get("//SACRAMENTO/PRECIP-INC//1Day/OBS/", t1, t2)
    tsc.print_to_console()
    assert len(tsc.values) > 0
    tsc2 = dss.get("//SACRAMENTO/TEMP-MAX//1Day/OBS/", t1, t2)
    tsc2.print_to_console()
    assert len(tsc2.values) > 0
    # save to a new path
    tsc.dsspath = "//SACRAMENTO/PRECIP-INC//1Day/OBS-modified/"
    dss.put(tsc)
    tsc3 = dss.get(tsc.dsspath, t1, t2)
    assert len(tsc3.values) == len(tsc.values)

def test_catalog():
    dss = HecDss(TEST_FP)
    catalog = dss.getCatalog()
    for ds in catalog:
        print(ds.recType,ds)

def test_new_catalog():
    rawPaths = [
        "//SACRAMENTO/TEMP-MIN/01Jan1989/1Day/OBS/",
        "//SACRAMENTO/TEMP-MIN/01Jan1990/1Day/OBS/",
        "//SACRAMENTO/TEMP-MIN/01Jan1991/1Day/OBS/",
        "//SACRAMENTO/TEMP-MIN/01Jan1992/1Day/OBS/",
        "//SACRAMENTO/TEMP-MIN/01Jan1993/1Day/OBS/",
    ]
    rt = [100, 100, 100, 100, 100]
    c = Catalog(rawPaths, rt)
    c.print()


if __name__ == "__main__":
    test_catalog()
    #test_issue9()
    #test_basic()
    #test_new_catalog()
