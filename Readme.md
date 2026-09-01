# HEC-DSS Python Wrapper

This repository contains a Python package for working with HEC-DSS files.

Read about HEC-DSS [here.](https://www.hec.usace.army.mil/software/hec-dss/)

## Installation

To install `hecdss`, use the following command:
```bash
pip install hecdss
```
## API full documentation

[API Documentation](https://hydrologicengineeringcenter.github.io/hec-dss-python/)

### DSS file methods
1. `HecDss(file_path: str, access: OpenAccess = OpenAccess.GENERAL_ACCESS)`: Opens a DSS file located at the provided file path.  See [File Access Modes](#file-access-modes).
   
2. `get(record_path: str)`: Retrieves the record data from the currently opened DSS file of the designated path.

3. `put(new_record: recordType)`: Stores recordType object to the DSS file at designated path.

4. `close()`: Closes the currently opened DSS file.

### Catalog object methods
1. `get_catalog()`: Retrieves the catalog of all paths  stored in the Dss file.
   - `rawCatalog` - list of records within the Dss file.
   - `rawRecordtypes` - list of record types within the Dss file.

## Supported Data Types

### Regular TimeSeries Data
- **Stored object in Python**: Regular Timeseries data is stored as 2 arrays of values and times/interval and startdate.
- **Attributes**: The TimeSeries object has the following attributes:
  - `start_date (str)`: The start date of the time series data.
  - `times (list[datetime])`: The times of the time series data.
  - `values (nd.nparray[float])`: The values of the time series data.
  - `quality (list[int])`: The quality flags of the time series data.
  - `notes (list[str])`: The notes of the time series data. 
  - `interval (str)`: The interval of the time series data.
  - `data_type (str)`: the dss data type ("PER-AVER","PER-CUM", "INST-VAL", "INST-CUM", .. )
  - `units (str)`: The units of the time series data.
  - `id (str)`: The Path of the time series data (Format: "/A/B/C/D/E/F/").
  
```python
# example working with time-series data
from hecdss import HecDss

# Open a DSS file
file_path = "example.dss"
with HecDss(file_path) as dss:
# Retrieve and print data
  data_path = "/example/data/////"
  data = dss.get(data_path)
  print(data)
  data.values = data.values * 2
  # Save changes to DSS file
  dss.put(data)
```

### Irregular TimeSeries Data
- **Stored object in Python**: Irregular Timeseries data is stored as 2 arrays of values and times.
- **Attributes**: The TimeSeries object has the following attributes:
  - `times (list[datetime])`: The times of the time series data.
  - `values (np.ndarray[float])`: The values of the time series data.
  - `units`: The units of the time series data.
  - `quality (list[int])`: The quality flags of the time series data.
  - `notes (list[str])`: The notes of the time series data. 
  - `data_type (str)`: the dss data type ('INST-VAL', 'INST-CUM')
  - `id (str)`: The Path of the time series data (Format: "/A/B/C/D/E/F/").


### Paired Data
- **Stored object in Python**: Paired data stored as aa (x, y) where y could be stored as a 2d numpy matrix.
- **Attributes**: The PairedData object has the following attributes:
  - `ordinates (np.ndarray)`: The x values of the paired data
  - `values (np.ndarray[float])`: y values of the paired data stored as 2d numpy array.
  - `labels (list[str])`: The labels of the paired data.
  - `id (str)`: The Path of the paired data.

### Gridded Data
- **Stored object in Python**: A 2d matrix stored as a numpy 2d object.
- **Attributes**: The GriddedData object has the following attributes:
  - `data`: The data of the gridded data object.
  - `id`: The Path of the gridded data.


### Array Data
- * Supports storing and reading arrays of integers, floats, or doubles.
- * Arrays are managed with ArrayContainer
   
   
```python
  # Example working with an array
  with HecDss("my-dss-file.dss") as dss:
    print(f" record_count = {dss.record_count()}")
    array_ints = ArrayContainer.create_float_array([1.0, 3.0, 5.0, 7.0])
    array_ints.id = "/test/float-array/redshift////"
    dss.put(array_ints)
    print(f"record_type = {dss.get_record_type(array_ints.id)}")
    read_array = dss.get(array_ints.id)
```

## CSV Functionality

### Time Series
The `rts.to_csv` and `RegularTimeSeries.read_csv` methods can be used to convert time series data to `.csv` format. This can also be utilized alongside `pandas` methods to convert time series data to pandas DataFrames.

```python
  # Round trip CSV example with RegularTimeSeries and Pandas DataFrame
  import pandas as pd
  
  file_path: str = "my-dss-file.dss"
  with HecDss(file_path) as dss:
    data_path: str = "/example/data/////"
    rts: RegularTimeSeries = dss.get(data_path)

    csv_out: str = "example.csv"
    rts.to_csv(csv_out) # RegularTimeSeries -> CSV

  df: pd.DataFrame = pd.read_csv(csv_out) # CSV -> DataFrame
  df_csv_path: str = "df_example.csv"
  # Index needs to be false for round-trip support
  df.to_csv(df_csv_path, index=False) # DataFrame -> CSV

  with HecDss(file_path) as dss:
    RegularTimeSeries.read_csv(df_csv_path) # CSV -> RegularTimeSeries
```

Additionally, `IrregularTimeSeries` and `PairedData` both have equivalent functionality with `.csv` conversion.


### This libray is built using the API for future versions of HEC-DSS 

This library uses (`hecdss.dll` on Windows and `libhecdss.so` on Unix/Linux).  hecdss.dll is the API being used for new development with HEC-DSS. For example a companion project https://github.com/HydrologicEngineeringCenter/hec-dss-dotnet is a .net library that uses hecdss.dll. This library is loosely coupled to HEC-DSS source code (Fortran and C)

## Developer Setup

1. Clone this repository to your local machine.
2. Place the appropriate `hecdss.dll` or `hecdss.so` file for your platform in the repository's src/hecdss/lib directory.
   1. One option is to download it from provided link [hecdss.dll](https://github.com/HydrologicEngineeringCenter/hec-dss-python/releases/download/v0.0.1-alpha/hecdss.dll)
   2. Second option is to run the following python script in the repository directory:
      ```
      python src\hecdss\download_hecdss.py
      ```
3. from the repo directory (hec-dss-python)
   ```
   python tests\test_basics.py
   ```


## File Access Modes

`HecDss` takes an optional `access` argument that controls how the DSS file is opened.  These
modes map directly to the `access` argument of `hec_dss_open_ex` in the HEC-DSS C library.

| `OpenAccess` | Value | Description |
| ----------- | ----- | ----------- |
| `GENERAL_ACCESS` | 0 | Read, or read/write when the file allows it.  No error when the file does not have write permission.  This is the default. |
| `READ_ACCESS` | 1 | Read only.  The file must already exist and is never written to, so several processes can read the same file at the same time. |
| `MULTI_USER_ACCESS` | 2 | Read/write with full multi-user access.  Usually slow, but necessary when more than one process writes to the file. |
| `SINGLE_USER_ADVISORY_ACCESS` | 3 | Read/write with multi-user advisory access.  Errors when the file is read only. |
| `EXCLUSIVE_ACCESS` | 4 | Exclusive write, used for squeezing.  Errors when exclusive access is not available. |

```python
from hecdss import OpenAccess, HecDss

# open a file read only; several processes can do this at the same time
with HecDss("example.dss", OpenAccess.READ_ACCESS) as dss:
    data = dss.get("/example/data/////")
    print(dss.access, dss.readonly)  # OpenAccess.READ_ACCESS True
```

A file opened with `READ_ACCESS` must already exist; opening a missing file raises `FileNotFoundError`
instead of creating it.  Methods that modify the file (`put`, `delete`, `writePrecompressedGrid`)
raise `PermissionError` on a `READ_ACCESS` file.

## Message Levels

Message levels can be set using `set_global_debug_level` or `set_debug_level`, for example:

```python
from hecdss import HecDss
mlvl: int = 4
HecDss.set_global_debug_level(mlvl)
```

Common levels are described in the documentation for the `mlvl` parameter of the `zset` utility function from the [HEC-DSS Programmers Guide for C](https://www.hec.usace.army.mil/confluence/dssdocs/dsscprogrammer)

Additional levels are described in the heclib source code C headers in [zdssMessages.h](https://github.com/HydrologicEngineeringCenter/hec-dss/blob/master/heclib/heclib_c/src/headers/zdssMessages.h)


## how to generate documentation

pdoc -o docs -d google --no-show-source .\src


## Design 

These are the driving design ideas and goals of the hec-dss-python project (subject to updates)

| Feature |      What     | Why                                                                                                              |
| ------------- |-------------|------------------------------------------------------------------------------------------------------------------|
| hecdss.dll/libhecdss.so  | cross platform (Linux,Windows,Mac), cross language ([.net](https://github.com/HydrologicEngineeringCenter/hec-dss-dotnet), [Python](https://github.com/HydrologicEngineeringCenter/hec-dss-python]), Java)  essential API | decouple from underlying HEC-DSS Fortran/C Library  (allow future DSS versions without C and Fortran backend)    |
| Support only DSS 7 | encourage migration from version 6  | HEC stopped DSS version 6 support July 31,2024.                                                                  |
|Easy transition from Jython|HEC products use an existing [Java/Jython API](https://www.hec.usace.army.mil/confluence/dssdocs/dssvueum/scripting/reading-and-writing-to-hec-dss-files).  We will loosely follow that design | simplify porting from Jython                                                                                     |
| hec_dss_native.py | native binding layer   | isolate interactions with low level library(if performance is an issue this Ctypes layer can be replaced )       |
| hec_dss.py | Programmer entry point ; Python API  | Hides interactions with hec_dss_native, seek to be simple user experience                                        |
|catalog.py|manage list of DSS objects (catalog) | create condensed catalog perspective                                                                             |
|Easy to get started |nothing to install, just copy python files and shared library   | require minimal privileges to install                                                                            | 


## Features

- Read and write data from HEC-DSS files using the provided C DLL.
- Abstracted memory management: Python allocates memory for arrays passed to the DLL, which the C code then populates.
- Cross-platform support: `hecdss.dll` for Windows and `hecdss.so` for Linux.
- Potential for future storage backend expansion (e.g., SQLite, HDF5) without altering the API.
- Language-agnostic approach similar to the .NET implementation ([hec-dss-dotnet](https://github.com/HydrologicEngineeringCenter/hec-dss-dotnet)).
- No package installation required because the library is using python-ctypes to interact with the DLL.


## Contributing

Contributions to this project are welcome! If you find any issues, have suggestions, or want to add new features, please open an issue or submit a pull request.
