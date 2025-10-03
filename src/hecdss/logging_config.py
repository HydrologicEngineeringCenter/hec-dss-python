"""
Logging configuration for hec-dss-python library.

This module provides custom logging levels that map to HEC-DSS DLL message levels,
and utilities for configuring logging for both Python code and DLL output.

HEC-DSS Message Levels (from heclib):
    MESS_LEVEL_NONE              0: No messages, including error (not guaranteed). Highly discouraged
    MESS_LEVEL_CRITICAL          1: Critical (Error) Messages. Discouraged.
    MESS_LEVEL_TERSE             2: Minimal (terse) output: zopen, zclose, critical errors.
    MESS_LEVEL_GENERAL           3: General Log Messages. Default.
    MESS_LEVEL_USER_DIAG         4: Diagnostic User Messages (e.g., input parameters)
    MESS_LEVEL_INTERNAL_DIAG_1   5: Diagnostic Internal Messages level 1 (debug). Not recommended for users
    MESS_LEVEL_INTERNAL_DIAG_2   6: Diagnostic Internal Messages level 2 (full debug)
    Levels 7-15: Additional verbose debug levels for development
"""

import logging
import sys
from typing import Optional, Union


# Define a single custom level for all DLL messages
# This simplifies routing since we're just capturing whatever the DLL outputs
DLL_MESSAGE = 25  # Between INFO (20) and WARNING (30)

# Register the custom DLL message level
logging.addLevelName(DLL_MESSAGE, "DLL")


# HEC-DSS Message Levels (for reference, but not mapped to Python levels)
# These control what the DLL writes to its log file:
# 0: No messages (not recommended)
# 1: Critical errors only
# 2: Terse output (errors + file operations)
# 3: General log messages (default)
# 4: User diagnostic messages
# 5: Internal debug level 1
# 6: Internal debug level 2 (full debug)
# 7-15: Extended debug levels


# Add convenience method for DLL messages
def dll_message(self, message, *args, **kwargs):
    """Log a DLL message at the DLL level."""
    if self.isEnabledFor(DLL_MESSAGE):
        self._log(DLL_MESSAGE, message, args, **kwargs)

# Add the method to Logger class
logging.Logger.dll_message = dll_message


def setup_default_logging():
    """
    Set up default logging configuration for the library.
    By default, uses NullHandler (no output) following Python library best practices.
    """
    # Root logger for the library
    root_logger = logging.getLogger('hecdss')
    if not root_logger.handlers:
        root_logger.addHandler(logging.NullHandler())
    root_logger.setLevel(logging.DEBUG)  # Capture everything, let handlers filter

    # DLL output logger (separate hierarchy for flexibility)
    dll_logger = logging.getLogger('hecdss.dll')
    dll_logger.setLevel(logging.DEBUG)  # Capture everything by default

    return root_logger, dll_logger


def configure_logging(
    python_level: Optional[Union[int, str]] = None,
    dll_level: Optional[Union[int, str]] = None,
    combined_file: Optional[str] = None,
    python_file: Optional[str] = None,
    dll_file: Optional[str] = None,
    console: bool = True,
    format_string: Optional[str] = None,
    capture_dll_output: bool = False
):
    """
    Configure logging for the hec-dss-python library.

    This provides an easy way to set up common logging configurations.
    Users can control Python code logging and DLL output logging independently.

    Args:
        python_level: Log level for Python code (e.g., logging.INFO or "INFO")
        dll_level: Either DLL message level (0-15) or Python log level for DLL output
                   0: No messages (not recommended)
                   1: Critical errors only
                   2: Terse output (errors + file operations)
                   3: General log messages (default)
                   4: User diagnostic messages
                   5: Internal debug level 1
                   6: Internal debug level 2 (full debug)
                   7-15: Extended debug levels
        combined_file: If provided, both Python and DLL logs go to this file
        python_file: If provided, Python logs go to this file
        dll_file: If provided, DLL logs go to this file
        console: If True (default), also output to console
        format_string: Custom format string for log messages
        capture_dll_output: If True, setup global DLL output capture (see Note below)

    Note:
        The capture_dll_output parameter sets up global monitoring but actual capture
        requires HecDss instances to be created with enable_dll_logging=True.

    Examples:
        # Default operation (general messages only)
        configure_logging(dll_level=3)

        # Show errors only
        configure_logging(python_level=logging.ERROR, dll_level=1)

        # Enable user diagnostics
        configure_logging(dll_level=4)

        # Enable internal debugging (not recommended for users)
        configure_logging(dll_level=5)

        # Everything to one file
        configure_logging(combined_file='debug.log', dll_level=6)

        # Separate files for Python and DLL
        configure_logging(python_file='python.log', dll_file='dll.log', dll_level=3)
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    formatter = logging.Formatter(format_string)

    # Get loggers
    python_logger = logging.getLogger('hecdss')
    dll_logger = logging.getLogger('hecdss.dll')

    # Clear existing handlers (except NullHandler)
    for logger in [python_logger, dll_logger]:
        logger.handlers = [h for h in logger.handlers if isinstance(h, logging.NullHandler)]

    # Set levels
    if python_level is not None:
        if isinstance(python_level, str):
            python_level = getattr(logging, python_level.upper())
        python_logger.setLevel(python_level)

    if dll_level is not None:
        # Set the DLL debug level (0-15) which controls what the DLL writes
        if isinstance(dll_level, int) and 0 <= dll_level <= 15:
            from hecdss import HecDss
            HecDss.set_global_debug_level(dll_level)

        # Always show DLL messages if they're being captured
        # The DLL level controls what gets written, we just display what's captured
        dll_logger.setLevel(DLL_MESSAGE)

    # Configure handlers
    handlers_added = False

    # Combined file handler
    if combined_file:
        file_handler = logging.FileHandler(combined_file)
        file_handler.setFormatter(formatter)
        python_logger.addHandler(file_handler)
        dll_logger.addHandler(file_handler)
        handlers_added = True

    # Separate file handlers
    if python_file:
        python_handler = logging.FileHandler(python_file)
        python_handler.setFormatter(formatter)
        python_logger.addHandler(python_handler)
        handlers_added = True

    if dll_file:
        dll_handler = logging.FileHandler(dll_file)
        dll_handler.setFormatter(formatter)
        dll_logger.addHandler(dll_handler)
        handlers_added = True

    # Console handler
    if console and handlers_added:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        if python_level is not None:
            python_logger.addHandler(console_handler)
        if dll_level is not None:
            dll_logger.addHandler(console_handler)

    # Setup DLL output capture if requested
    if capture_dll_output:
        monitor = get_dll_monitor()
        logger.info("DLL output capture configured. Use HecDss(..., enable_dll_logging=True) to activate.")


import threading
import tempfile
import time
import os
from pathlib import Path
from typing import Optional


class DllLogMonitor:
    """
    Monitors HEC-DSS log file and routes messages to Python logging.
    Uses a temporary log file approach to capture DLL output when zopenLog is available.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.log_file_path = None
        self.temp_file = None
        self.monitoring = False
        self.monitor_thread = None
        self._last_position = 0
        self._current_dll_level = 3  # Default to GENERAL

    def setup_temp_log_file(self) -> str:
        """Create a temporary log file for DLL output."""
        # Create temporary file but keep it open for DLL to write to
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w+',
            suffix='_hecdss.log',
            prefix='dll_',
            delete=False
        )
        self.log_file_path = self.temp_file.name
        self.temp_file.close()  # Close our handle, DLL will open its own

        self.logger.debug("Created temporary DLL log file: %s", self.log_file_path)
        return self.log_file_path

    def start_monitoring(self):
        """Start monitoring the log file in a separate thread."""
        if not self.log_file_path:
            self.setup_temp_log_file()

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="DLL-Log-Monitor"
        )
        self.monitor_thread.start()
        self.logger.debug("Started monitoring DLL log file")

    def stop_monitoring(self):
        """Stop monitoring and clean up."""
        self.monitoring = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

        # Clean up temporary file
        if self.log_file_path and os.path.exists(self.log_file_path):
            try:
                os.remove(self.log_file_path)
                self.logger.debug("Cleaned up temporary log file: %s", self.log_file_path)
            except Exception as e:
                self.logger.warning("Could not remove temp log file %s: %s",
                                   self.log_file_path, e)

    def _monitor_loop(self):
        """Watch log file for new content."""
        while self.monitoring:
            try:
                if self.log_file_path and os.path.exists(self.log_file_path):
                    with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        # Seek to last read position
                        f.seek(self._last_position)

                        # Read new lines
                        new_content = f.read()
                        if new_content:
                            self._last_position = f.tell()

                            # Process each line
                            for line in new_content.splitlines():
                                if line.strip():
                                    self._route_to_logger(line)

            except Exception as e:
                self.logger.debug("Error reading DLL log: %s", e)

            time.sleep(0.05)  # Check every 50ms

    def _route_to_logger(self, message: str):
        """Route DLL message to Python logging at the DLL_MESSAGE level."""
        # Remove timestamp if present (HEC-DSS adds its own)
        # Format is typically: "DD-MMM-YYYY HH:MM:SS  MESSAGE"
        if len(message) > 22 and message[2] == '-' and message[6] == '-':
            message = message[22:].strip()

        # All DLL messages go to the same level - the DLL itself controls verbosity
        self.logger.log(DLL_MESSAGE, "[DLL] %s", message)

    def set_dll_level(self, level: int):
        """Update the current DLL message level."""
        self._current_dll_level = level


# Global instance for DLL monitoring
_dll_monitor: Optional[DllLogMonitor] = None


def get_dll_monitor() -> DllLogMonitor:
    """Get or create the global DLL log monitor."""
    global _dll_monitor
    if _dll_monitor is None:
        dll_logger = logging.getLogger('hecdss.dll')
        _dll_monitor = DllLogMonitor(dll_logger)
    return _dll_monitor