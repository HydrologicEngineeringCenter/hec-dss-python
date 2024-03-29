import os
import sys
import ctypes
from pathlib import Path


shared_lib_dir = Path(__file__).parent.joinpath("lib")

if sys.platform == "linux" or sys.platform == "darwin":
    try:
        os.environ["LD_LIBRARY_PATH"] = str(shared_lib_dir) + os.pathsep + os.environ['LD_LIBRARY_PATH']
    except KeyError:
        os.environ["LD_LIBRARY_PATH"] = str(shared_lib_dir)
else:
    os.environ['PATH'] = f"{shared_lib_dir};{os.environ['PATH']}"

from hecdss.catalog import Catalog
from hecdss.hecdss import HecDss
from hecdss.dsspath import DssPath
