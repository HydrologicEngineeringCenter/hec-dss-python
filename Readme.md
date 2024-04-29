# HEC-DSS Python Wrapper

This repository contains a Python wrapper for the HEC-DSS file database C library. The provided DLL (`hecdss.dll` on Windows and `hecdss.so` on Linux) enables interaction with HEC-DSS files while abstracting memory management between Python and C.

## Getting Started

1. Clone this repository to your local machine.
2. Place the appropriate `hecdss.dll` or `hecdss.so` file for your platform in the repository's src/hecdss/lib directory. [hecdss.dll](https://github.com/HydrologicEngineeringCenter/hec-dss-python/releases/download/v0.0.1-alpha/hecdss.dll)
3. from the repo directory (hec-dss-python)
   ```
   C:\project\hec-dss-python>python tests\test_basics.py
   C:\project\hec-dss-python>python tests\test_pairedData.py
   ```


## Background

The HEC-DSS file database is a widely used data storage format for hydrological and environmental data. This repository provides a Python interface to interact with the HEC-DSS files using the provided C DLL. The primary goal is to enable Python applications to read data from and write data to HEC-DSS files. 

## Design 

These are the driving design ideas and goals of the hec-dss-python project (subject to updates)

| Feature |      What     | Why  |
| ------------- |-------------| -----|
| hecdss.dll/libhecdss.so  | cross platform (Linux,Windows,Mac), cross language ([.net](https://github.com/HydrologicEngineeringCenter/hec-dss-dotnet), [Python](https://github.com/HydrologicEngineeringCenter/hec-dss-python]), Java)  essential API |decouple from underlying HEC-DSS Fortran/C Library  (allow future DSS versions without C and Fortran backend)  |
| Support only DSS 7 | encourage migration from version 6  |  HEC is moving to DSS version 7 in 2023-2024. |
|Easy transition from Jython|HEC products use an existing [Java/Jython API](https://www.hec.usace.army.mil/confluence/dssdocs/dssvueum/scripting/reading-and-writing-to-hec-dss-files).  We will loosely follow that design | simplify porting from Jython|
| hec_dss_native.py | native binding layer   | isolate interactions with low level library(if performance is an issue this Ctypes layer can be replaced ) |
| hec_dss.py | Programmer entry point ; Python API  | Hides interactions with hec_dss_native, seek to be simple user experience|
|catalog.py|manage list of DSS objects (catalog) |create condensed catalog perspective|
|Pandas_Series_Utilities.py [future](https://github.com/HydrologicEngineeringCenter/hec-dss-python/issues/8) |NumPy/pandas support |provide features such as dataframes, separate from hec-dss.py; can be developed by different/parallel developers|
|Easy to get started |nothing to install, just copy python files and shared library   |require minimal privileges to install| 


## Features

- Read and write data from HEC-DSS files using the provided C DLL.
- Abstracted memory management: Python allocates memory for arrays passed to the DLL, which the C code then populates.
- Cross-platform support: `hecdss.dll` for Windows and `hecdss.so` for Linux.
- Potential for future storage backend expansion (e.g., SQLite, HDF5) without altering the API.
- Language-agnostic approach similar to the .NET implementation ([hec-dss-dotnet](https://github.com/HydrologicEngineeringCenter/hec-dss-dotnet)).
- No package installation required because the library is using python-ctypes to interact with the DLL.


## Contributing

Contributions to this project are welcome! If you find any issues, have suggestions, or want to add new features, please open an issue or submit a pull request.
