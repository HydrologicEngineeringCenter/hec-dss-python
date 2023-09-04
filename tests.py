from hec_dss import HecDss
from datetime import datetime
from catalog import Catalog
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

   @staticmethod
   def basic_tests():
        dss = HecDss("sample7.dss")
        print("record count = "+str(dss.recordCount()))
        catalog = dss.getCatalog()
        print(catalog[0:5])

        t1 = datetime(2005, 1, 1)
        t2 = datetime(2005, 1 ,4)
        tsc = dss.get("//SACRAMENTO/PRECIP-INC//1Day/OBS/",t1,t2)
        tsc.print_to_console()
        assert(len(tsc.values)>0)
        tsc2 = dss.get("//SACRAMENTO/TEMP-MAX//1Day/OBS/",t1,t2)
        tsc2.print_to_console()
        assert(len(tsc2.values)>0)
        # save to a new path
        tsc.pathname = "//SACRAMENTO/PRECIP-INC//1Day/OBS-modified/"
        dss.put(tsc)
        tsc3 = dss.get(tsc.pathname,t1,t2)
        assert(len(tsc3.values)== len(tsc.values))

   @staticmethod
   def catalog_test():
    rawPaths = [
      "//SACRAMENTO/TEMP-MIN/01Jan1989/1Day/OBS/",
      "//SACRAMENTO/TEMP-MIN/01Jan1990/1Day/OBS/",
      "//SACRAMENTO/TEMP-MIN/01Jan1991/1Day/OBS/",
      "//SACRAMENTO/TEMP-MIN/01Jan1992/1Day/OBS/",
      "//SACRAMENTO/TEMP-MIN/01Jan1993/1Day/OBS/"
    ]
    rt = [100,100,100,100,100]
    c = Catalog(rawPaths,rt)
    c.print()


if __name__ == "__main__":
   #Tests.test_issue9()
   #Tests.basic_tests()
   Tests.catalog_test()
