# HEC DSS Python Package (hecdss)

## Overview
`hecdss` is a Python package designed to open, edit, and store DSS files. This package provides functionality to interact with DSS files, utilizing a range of methods and attributes.

## Methods and Attributes

### DSS file methods
1. `HecDss(file_path: str)`: Opens a DSS file located at the provided file path.
   
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
  - `start_date`: The start date of the time series data.
  - `times`: The times of the time series data.
  - `values`: The values of the time series data.
  - `interval`: The interval of the time series data.
  - `units`: The units of the time series data.
  - `id`: The Path of the time series data.

### Irregular TimeSeries Data
- **Stored object in Python**: Irregular Timeseries data is stored as 2 arrays of values and times.
- **Attributes**: The TimeSeries object has the following attributes:
  - `times`: The times of the time series data.
  - `values`: The values of the time series data.
  - `units`: The units of the time series data.
  - `data`: The time series data.
  - `id`: The Path of the time series data.


### Paired Data
- **Stored object in Python**: Paired data stored as aa (x, y) where y could be stored as a 2d numpy matrix.
- **Attributes**: The PairedData object has the following attributes:
  - `ordinates`: The x values of the paired data
  - `values`: y values of the paired data stored as 2d numpy array.
  - `labels`: The labels of the paired data.
  - `id`: The Path of the paired data.

### Gridded Data
- **Stored object in Python**: A 2d matrix stored as a numpy 2d object.
- **Attributes**: The GriddedData object has the following attributes:
  - `data`: The data of the gridded data object.
  - `id`: The Path of the gridded data.

## Installation

To install `hecdss`, use the following command:
```bash
pip install -i https://test.pypi.org/simple/ hecdss
```

```bash
from hecdss import DssFile

# Open a DSS file
file_path = "example.dss"
dss = DssFile(file_path)

# Retrieve and print data
data_path = "/example/data/////"
data = dss.get(data_path)
print(data)

dss.values = dss.values * 2

# Save changes to DSS file
dss.put(data_path)

dss.close()

