
This library is CTypes, which is built into python to call native C functions in a DLL (hecdss.dll)

For reading data, python allocates memory and passes allocated arrays into hecdss.dll.  Hecdss.dll will load the 'results' into the allocated arrays. This way Python and C only share memory during function calls,and manage memory for themselfs otherwise.

Python then converts the allocated arrays into python arrays.


| boundary|   functionality   | Why  |
| ------------- |-------------| -----|
| hec_dss_native.py | native binding layer(defines C API calls)   |
| hec_dss.py | python friendly entry point ; Python API allocates C arrays before calling hec_dss_native, copies data between C and Python memory  | 



The following prompt template has been useful in generating the wrapper layer.

I need to call a C method inside a DLL, using python ctypes.  Also please create a python wrapper function , with the same function name.  Include the argtypes, inside the function, with each argtype on a separate lines with the names as comments. 


 Here is the C method:

<C function declaration here>