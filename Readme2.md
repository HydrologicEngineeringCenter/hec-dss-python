# HEC DSS Python Package (hecdss)

## Overview
`hecdss` is a Python package designed to open, edit, and store DSS files. This package provides functionality to interact with DSS files, utilizing a range of methods and attributes.

## Methods and Attributes

### DSS file methods
1. `HecDss(file_path: str)`: Opens a DSS file located at the provided file path.
   
2. `get()`: Edits the content of the currently opened DSS file.

3. `put()`: Saves the changes made to the DSS file.

### Catalog object methods
1. `get_data(data_path: str)`: Retrieves data stored at the specified data path.
  
2. `store_data(data: Any, data_path: str)`: Stores data at the specified data path within the DSS file.

### Methods and Attributes of Functions

- `open_file()`
  - `file_path`: A string specifying the path to the DSS file.
  
- `get_data()`
  - `data_path`: A string representing the path to the data stored in the DSS file.

## Supported Data Types

### Time Series Data
- **Stored object in Python**: Time series data is stored as a Pandas DataFrame.

### Scaled Data
- **Stored object in Python**: Scaled data is stored as a NumPy array.

### Statistical Data
- **Stored object in Python**: Statistical data is stored as a dictionary.

## Installation

To install `hecdss`, use the following command:
```bash
pip install hecdss
```

```bash
from hecdss import DssFile

# Open a DSS file
file_path = "example.dss"
dss_file = DssFile()
dss_file.open_file(file_path)

# Retrieve and print data
data_path = "/example/data"
data = dss_file.get_data(data_path)
print(data)

# Save changes to DSS file
dss_file.save_file()

