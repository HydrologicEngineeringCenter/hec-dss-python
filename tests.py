from hec_dss import HecDss
from datetime import datetime

class Tests:

   @staticmethod
   def test_issue9():
        dss = HecDss("sample7.dss")
        pathnames = [
        "//SACRAMENTO/PRECIP-INC//1Day/OBS/",
        "/EF RUSSIAN/COYOTE/PRECIP-INC//1Hour/TB/"
        "/GREEN RIVER/OAKVILLE/ELEVATION//1Hour//"
        ]
        t1 = datetime(2006, 3, 1)
        t2 = datetime(2006, 3 ,30)
        for path in pathnames:
            print(f"reading {path}")
            tsc = dss.get(path,t1,t2)
            print(f"len(tsc.values) = {len(tsc.values)}")
            assert(len(tsc.values)>1)


Tests.test_issue9()

