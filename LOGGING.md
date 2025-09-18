# HEC-DSS Python Logging Guide

## Overview

The hec-dss-python library provides comprehensive logging capabilities for both Python code and native DLL operations. The logging system is built on Python's standard `logging` module and follows Python library best practices.

## Quick Start

### Basic Setup

```python
import logging
from hecdss import HecDss, configure_logging

# Simple configuration - show warnings and above
configure_logging(python_level=logging.WARNING, dll_level=3)

# Or just use defaults (no output unless configured)
dss = HecDss("myfile.dss")
```

### Enable DLL Output Capture

```python
# Configure logging with DLL output capture
configure_logging(
    python_level=logging.INFO,
    dll_level=4,  # User diagnostic messages
    capture_dll_output=True
)

# Open DSS file with DLL logging enabled
with HecDss("myfile.dss", enable_dll_logging=True) as dss:
    # DLL messages now appear in Python logs
    catalog = dss.get_catalog()
```

## Logging Architecture

The library uses two separate loggers:

1. **`hecdss`** - Python code messages (errors, warnings, info from Python functions)
2. **`hecdss.dll`** - Native DLL messages (captured from the HEC-DSS C library)

### Default Behavior

By default, the library produces **no output** (uses `NullHandler`), following Python library best practices. Users must explicitly configure logging to see messages.

## DLL Message Levels

The DLL uses a 0-15 scale to control message verbosity:

| Level | Description | Recommended Use |
|-------|-------------|-----------------|
| 0 | No messages | Not recommended (hides errors) |
| 1 | Critical errors only | Minimal error reporting |
| 2 | Terse (errors + file operations) | Basic operation tracking |
| **3** | **General messages (default)** | **Normal operations** |
| 4 | User diagnostic messages | Troubleshooting |
| 5 | Internal diagnostics level 1 | Debugging (not for users) |
| 6 | Internal diagnostics level 2 | Full debugging |
| 7-15 | Extended debug levels | Development use |

## Configuration Functions

### `configure_logging()`

Main configuration function for common logging setups.

```python
configure_logging(
    python_level=None,        # Python code log level
    dll_level=None,           # DLL verbosity (0-15)
    combined_file=None,       # Single file for all logs
    python_file=None,         # File for Python logs only
    dll_file=None,           # File for DLL logs only
    console=True,            # Also output to console
    format_string=None,      # Custom format string
    capture_dll_output=False # Enable DLL capture setup
)
```

### `HecDss.set_global_debug_level()`

Set the DLL message level globally.

```python
HecDss.set_global_debug_level(4)  # User diagnostic level
```

## Common Usage Patterns

### 1. Development/Debugging

```python
# See everything
configure_logging(
    python_level=logging.DEBUG,
    dll_level=5,  # Internal diagnostics
    combined_file='debug.log'
)
```

### 2. Production Monitoring

```python
# Only errors and warnings
configure_logging(
    python_level=logging.WARNING,
    dll_level=2,  # Terse output
    combined_file='app.log'
)
```

### 3. Separate Python and DLL Logs

```python
configure_logging(
    python_file='python_ops.log',
    dll_file='dll_messages.log',
    python_level=logging.INFO,
    dll_level=3
)
```

### 4. Console Output Only

```python
configure_logging(
    python_level=logging.INFO,
    dll_level=3,
    console=True  # Default
)
```

### 5. Troubleshooting DSS Operations

```python
import logging
from hecdss import HecDss, configure_logging

# Enable detailed DLL output
configure_logging(
    python_level=logging.INFO,
    dll_level=4,  # User diagnostics
    capture_dll_output=True
)

# Create DSS with DLL logging
with HecDss("problem_file.dss", enable_dll_logging=True) as dss:
    # Increase verbosity for specific operation
    HecDss.set_global_debug_level(5)

    # Problematic operation
    data = dss.get("//LOCATION/FLOW//1HOUR/OBS/")

    # Reset to normal
    HecDss.set_global_debug_level(3)
```

## DLL Output Capture

The library can capture native DLL messages and route them through Python's logging system.

### How It Works

1. Creates a temporary log file for the DLL
2. Tells the DLL to write to this file (via `zopenLog()`)
3. Monitors the file in a background thread
4. Routes messages to Python logging with `[DLL]` prefix
5. Cleans up the temporary file on close

### Enabling DLL Capture

```python
# Step 1: Configure logging with capture
configure_logging(
    dll_level=4,
    capture_dll_output=True
)

# Step 2: Open DSS with DLL logging enabled
dss = HecDss("myfile.dss", enable_dll_logging=True)

# Now DLL messages appear in Python logs:
# 2024-01-15 10:23:45 - hecdss.dll - DLL - [DLL] DSS file opened successfully
# 2024-01-15 10:23:45 - hecdss.dll - DLL - [DLL] Reading catalog...
```

## Logging Methods

### Standard Python Logging

```python
import logging
logger = logging.getLogger('hecdss')

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### DLL Messages

All DLL messages appear at the `DLL` level (25), between INFO (20) and WARNING (30):

```python
dll_logger = logging.getLogger('hecdss.dll')
dll_logger.dll_message("Message from DLL")  # Custom method
```

### Catalog and Path Logging

```python
# Get catalog
catalog = dss.get_catalog()

# Print to console (unchanged)
catalog.print()

# Log to Python logging
catalog.log_items(logging.INFO)

# Path logging
path = DssPath("/A/B/C/01Jan2024/1Hour/F/")
path.print()  # Console output
path.log_path(logging.DEBUG)  # Python logging
```

## Custom Log Formatting

```python
configure_logging(
    format_string='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
    python_level=logging.INFO
)

# Output:
# 2024-01-15 10:23:45 | hecdss              | INFO     | Opening DSS file
# 2024-01-15 10:23:45 | hecdss.dll          | DLL      | [DLL] File opened
```

## Filtering

### Show Only Python Messages

```python
configure_logging(
    python_level=logging.INFO,
    dll_level=0  # No DLL output
)
```

### Show Only DLL Messages

```python
import logging

# Configure
configure_logging(dll_level=4, capture_dll_output=True)

# Suppress Python messages
logging.getLogger('hecdss').setLevel(logging.CRITICAL)
```

### Filter by Logger Name

```python
# Only show messages from specific module
logging.getLogger('hecdss.catalog').setLevel(logging.DEBUG)
logging.getLogger('hecdss.native').setLevel(logging.WARNING)
```

## Integration with Application Logging

```python
import logging
import logging.config

# Your app's logging config
LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'detailed'
        }
    },
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(name)s %(levelname)s: %(message)s'
        }
    },
    'loggers': {
        'hecdss': {
            'level': 'INFO',
            'handlers': ['file']
        },
        'hecdss.dll': {
            'level': 'DEBUG',
            'handlers': ['file']
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

# Now use HecDss normally
dss = HecDss("myfile.dss", enable_dll_logging=True)
```

## Troubleshooting

### No Output Appearing

Check that logging is configured:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### DLL Messages Not Captured

Ensure both steps are done:
1. `capture_dll_output=True` in configure_logging()
2. `enable_dll_logging=True` when creating HecDss

### Too Much Output

Reduce verbosity:
```python
# Less Python output
configure_logging(python_level=logging.WARNING)

# Less DLL output
HecDss.set_global_debug_level(2)  # Terse only
```

### Performance Impact

DLL logging has minimal overhead (~50ms file check interval). For production:
```python
# Disable DLL capture for performance
dss = HecDss("myfile.dss", enable_dll_logging=False)  # Default
```

## Best Practices

1. **Development**: Use higher verbosity (dll_level=4-5) with file logging
2. **Production**: Use lower verbosity (dll_level=2-3) with error tracking
3. **Testing**: Capture both Python and DLL logs to separate files
4. **Performance**: Disable DLL capture when not needed
5. **Security**: Never log sensitive data; logs may contain file paths

## Example: Complete Application

```python
#!/usr/bin/env python
"""Example application with full logging."""

import logging
import sys
from hecdss import HecDss, configure_logging

def setup_logging(debug=False):
    """Setup application logging."""
    level = logging.DEBUG if debug else logging.INFO

    configure_logging(
        python_level=level,
        dll_level=4 if debug else 3,
        combined_file='app.log',
        console=True,
        capture_dll_output=debug,
        format_string='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

def main():
    # Parse arguments
    debug = '--debug' in sys.argv

    # Setup logging
    setup_logging(debug)
    logger = logging.getLogger(__name__)

    logger.info("Application starting")

    try:
        # Open DSS file
        filename = sys.argv[1] if len(sys.argv) > 1 else "test.dss"

        with HecDss(filename, enable_dll_logging=debug) as dss:
            logger.info(f"Opened {filename}")

            # Get catalog
            catalog = dss.get_catalog()
            logger.info(f"Found {len(catalog.items)} records")

            # Log catalog items if debugging
            if debug:
                catalog.log_items(logging.DEBUG)

            # Process data...

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

    logger.info("Application complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## API Reference

### Functions

- `configure_logging(**kwargs)` - Configure library logging
- `HecDss.set_global_debug_level(level)` - Set DLL verbosity (0-15)

### Classes

- `HecDss(filename, enable_dll_logging=False)` - Main DSS interface

### Logger Names

- `hecdss` - Root logger for Python code
- `hecdss.dll` - Logger for DLL messages
- `hecdss.catalog` - Catalog operations
- `hecdss.native` - Native library interface
- `hecdss.hecdss` - Main HecDss class

### Log Levels

- Standard Python: `DEBUG` (10), `INFO` (20), `WARNING` (30), `ERROR` (40), `CRITICAL` (50)
- Custom: `DLL` (25) - All DLL messages

## See Also

- [Python logging documentation](https://docs.python.org/3/library/logging.html)
- [HEC-DSS Programmers Guide](https://www.hec.usace.army.mil/confluence/dssdocs/dsscprogrammer)
- [HEC-DSS Message Levels](https://github.com/HydrologicEngineeringCenter/hec-dss/blob/master/heclib/heclib_c/src/headers/zdssMessages.h)