
This library is CTypes, which is built into python to call native C functions in a DLL (hecdss.dll)

For reading data, python allocates memory and passes allocated arrays into hecdss.dll.  Hecdss.dll will load the 'results' into the allocated arrays. This way Python and C only share memory during function calls,and manage memory for themselfs otherwise.

Python then converts the allocated arrays into python arrays.


| boundary|   functionality   | Why  |
| ------------- |-------------| -----|
| hec_dss_native.py | native binding layer(defines C API calls)   |
| hec_dss.py | python friendly entry point ; Python API manages calling hec_dss_native, copies data between C and Python memory  | 

## Data type details, for calling C DLL from python. 


| Purpose          | Native C         | call from hec_dss.py       | ctypes arg Definition | change before calling C method…                                                                                                            | Upper Layer                                     |
|------------------|------------------|----------------------------|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| open DSS handle  | `dss_file** dss` | `hec_dss_native only`      | `POINTER(c_void_p)`   | `self.handle = c_void_p()`<br>`function_call(byref(self.handle)`                                                                          |                                                 |
| use DSS handle   | `dss_file *dss`  | `hec_dss_native only`      | `c_void_p()`          | `function_call(self.handle)`                                                                                                               |                                                 |
| ummutable string | `const char* s`  | `str`                       | `c_char_p`            | `s.encode("utf-8")` OR `define s=b"my string"`                                                                                            |                                                 |
| string by ref    | `char* units`    | `units =[""]`               | `c_char_p`            | `c_units = create_string_buffer(buff_size)`<br>`// call C method…`<br>`c_units.value.decode("utf-8")`                                      | `units = [""]`<br>`function(units)`<br>`ts.units = units[0]` |
| array ref        | `int* times`     | `times = []`                | `POINTER(c_int)`      | `c_times = (c_int32 * arraySize)()`                                                                                                        |                                                 |
| array ref        | `double *valueArray` | `values=[]`             | `POINTER(c_double)`   | `c_values = (c_double * arraySize)()`                                                                                                      |                                                 |
| pass by value    | `int arraySize`  | `int`                       | `c_int`               | `c_arraySize = c_int(arraySize)`                                                                                                            |                                                 |
| pass by ref      | `int* numValues` | `numberValues=[0]`          | `POINTER(c_int)`      | `c_numberValues = c_int(0),`<br>`then pass byref(c_numberValues)`                                                                          |                                                 |
| return value     | `int i`          | `n/a`                       | `c_int`               | `automatic conversion`                                                                                                                     |                                                 |




The following prompt template has been useful in generating the wrapper layer.

I need to call a C method inside a DLL, using python ctypes.  Also please create a python wrapper function , with the same function name.  Include the argtypes, inside the function, with each argtype on a separate lines with the names as comments. 


 Here is the C method:

<C function declaration here>