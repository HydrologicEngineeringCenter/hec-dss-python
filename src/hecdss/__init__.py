import os
import sys
from pathlib import Path


shared_lib_dir = Path(__file__).parent.joinpath("lib")

if sys.platform == "linux" or sys.platform == "darwin":
    try:
        os.environ["LD_LIBRARY_PATH"] = str(shared_lib_dir) + os.pathsep + os.environ['LD_LIBRARY_PATH']
    except KeyError:
        os.environ["LD_LIBRARY_PATH"] = str(shared_lib_dir)
else:
    os.add_dll_directory(shared_lib_dir)

from hecdss.catalog import Catalog
from hecdss.hec_dss import HecDss
from hecdss.dsspath import DssPath
