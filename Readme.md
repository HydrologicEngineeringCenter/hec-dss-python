# HEC-DSS Python Wrapper

This repository contains a Python wrapper for the HEC-DSS file database C library. The provided DLL (`hecdss.dll` on Windows and `hecdss.so` on Linux) enables interaction with HEC-DSS files while abstracting memory management between Python and C.

## Background

The HEC-DSS file database is a widely used data storage format for hydrological and environmental data. This repository provides a Python interface to interact with the HEC-DSS files using the provided C DLL. The primary goal is to enable Python applications to read data from and write data to HEC-DSS files. 

## Features

- Read and write data from HEC-DSS files using the provided C DLL.
- Abstracted memory management: Python allocates memory for arrays passed to the DLL, which the C code then populates.
- Cross-platform support: `hecdss.dll` for Windows and `hecdss.so` for Linux.
- Potential for future storage backend expansion (e.g., SQLite, HDF5) without altering the API.
- Language-agnostic approach similar to the .NET implementation ([hec-dss-dotnet](https://github.com/HydrologicEngineeringCenter/hec-dss-dotnet)).
- No package installation required because the library is using python-ctypes to interact with the DLL.

## Getting Started

1. Clone this repository to your local machine.
2. Place the appropriate `hecdss.dll` or `hecdss.so` file for your platform in the repository's root directory.

## Contributing

Contributions to this project are welcome! If you find any issues, have suggestions, or want to add new features, please open an issue or submit a pull request.
