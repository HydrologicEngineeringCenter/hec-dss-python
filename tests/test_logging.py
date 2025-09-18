#!/usr/bin/env python
"""
Test script to demonstrate the new logging functionality in hec-dss-python.
"""

import logging
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hecdss import (
    HecDss,
    configure_logging,
    DLL_MESSAGE
)


def test_basic_logging():
    """Test basic logging configuration."""
    print("\n=== Test 1: Basic Logging Configuration ===")

    # Configure to show Python INFO and DLL general messages
    configure_logging(
        python_level=logging.INFO,
        dll_level=3,  # MESS_LEVEL_GENERAL
        format_string='%(name)s - %(levelname)s - %(message)s'
    )

    # Get a logger and test it
    logger = logging.getLogger('hecdss.test')
    logger.info("This is an INFO message from Python code")
    logger.debug("This DEBUG message should not appear (level too low)")

    print("Basic logging test completed.\n")


def test_separate_levels():
    """Test separate control of Python and DLL logging."""
    print("\n=== Test 2: Separate Python and DLL Levels ===")

    # Show only errors from Python but diagnostic messages from DLL
    configure_logging(
        python_level=logging.ERROR,
        dll_level=4  # MESS_LEVEL_USER_DIAG
    )

    logger = logging.getLogger('hecdss.test')
    logger.info("This INFO should NOT appear")
    logger.error("This ERROR should appear")

    # Test setting DLL level directly
    HecDss.set_global_debug_level(5)  # MESS_LEVEL_INTERNAL_DIAG_1
    print("DLL debug level set to 5 (internal diagnostics)\n")


def test_file_logging():
    """Test logging to files."""
    print("\n=== Test 3: File Logging ===")

    # Configure separate files for Python and DLL
    configure_logging(
        python_file='test_python.log',
        dll_file='test_dll.log',
        python_level=logging.DEBUG,
        dll_level=4,
        console=False  # Don't output to console
    )

    logger = logging.getLogger('hecdss.test')
    logger.debug("Debug message to Python log file")
    logger.info("Info message to Python log file")

    print("Check test_python.log and test_dll.log files for output.\n")


def test_custom_levels():
    """Test custom DLL message level."""
    print("\n=== Test 4: Custom DLL Message Level ===")

    # Configure to show DLL messages
    configure_logging(
        dll_level=4,  # Set DLL to user diagnostic level
        format_string='%(levelname)-15s - %(message)s'
    )

    # Get DLL logger to demonstrate the single DLL level
    dll_logger = logging.getLogger('hecdss.dll')

    # Use the single DLL message method
    dll_logger.dll_message("This is a DLL message")
    dll_logger.dll_message("All DLL messages use the same Python log level")
    dll_logger.dll_message("The DLL itself controls what gets written based on its debug level")

    print("Custom level test completed.\n")


def test_no_logging():
    """Test that logging can be completely disabled."""
    print("\n=== Test 5: No Logging (Default Behavior) ===")

    # Reset to default (no output)
    root_logger = logging.getLogger('hecdss')
    dll_logger = logging.getLogger('hecdss.dll')

    # Clear handlers
    root_logger.handlers.clear()
    dll_logger.handlers.clear()

    # Add only NullHandler (no output)
    root_logger.addHandler(logging.NullHandler())

    logger = logging.getLogger('hecdss.test')
    logger.info("This should not appear anywhere")
    logger.error("This error should also not appear")

    print("No output should have appeared from logging calls.")
    print("This maintains backward compatibility - no output by default.\n")


def test_with_dss_file():
    """Test logging with actual DSS file operations if available."""
    print("\n=== Test 6: DSS File Operations with Logging ===")

    # Configure logging to see what's happening
    configure_logging(
        python_level=logging.INFO,
        dll_level=3,  # General log messages
        format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    test_file = "test_logging.dss"

    try:
        # This will test the logging in actual DSS operations
        with HecDss(test_file) as dss:
            logger = logging.getLogger('hecdss.test')
            logger.info(f"Successfully opened {test_file}")

            # Get catalog (this might trigger some logging)
            catalog = dss.get_catalog()
            logger.info(f"Catalog has {len(catalog.items)} items")

            # Test the new log_items method if catalog has items
            if catalog.items:
                catalog.log_items(logging.INFO)

    except Exception as e:
        logger = logging.getLogger('hecdss.test')
        logger.error(f"Error during DSS operations: {e}")

    # Clean up test file if it was created
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"Cleaned up {test_file}")

    print("DSS file test completed.\n")


def test_dll_output_capture():
    """Test capturing DLL output to Python logging."""
    print("\n=== Test 7: DLL Output Capture ===")

    # Configure logging with DLL output capture
    configure_logging(
        python_level=logging.INFO,
        dll_level=4,  # User diagnostic messages
        format_string='%(name)-20s - %(levelname)-10s - %(message)s',
        capture_dll_output=True  # Enable DLL capture setup
    )

    test_file = "test_dll_capture.dss"

    try:
        # Create HecDss with DLL logging enabled
        with HecDss(test_file, enable_dll_logging=True) as dss:
            logger = logging.getLogger('hecdss.test')
            logger.info(f"Opened {test_file} with DLL logging enabled")

            # Set higher debug level to see more DLL messages
            HecDss.set_global_debug_level(5)  # Internal diagnostics level 1

            # Perform operations that should trigger DLL messages
            catalog = dss.get_catalog()
            logger.info(f"Retrieved catalog with {len(catalog.items)} items")

            # The DLL messages should now appear in the Python logs with [DLL] prefix

    except Exception as e:
        logger = logging.getLogger('hecdss.test')
        logger.error(f"Error during DLL capture test: {e}")

    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"Cleaned up {test_file}")

    print("DLL output capture test completed.\n")


def test_silent_by_default():
    """Test that hec-dss-python produces NO output by default."""
    print("\n=== Test 8: Silent by Default (Best Practice) ===")

    import io
    from contextlib import redirect_stdout, redirect_stderr

    # Capture all output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    test_file = "test_silent.dss"

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Fresh import simulation - clear any existing handlers
            root_logger = logging.getLogger('hecdss')
            dll_logger = logging.getLogger('hecdss.dll')
            root_logger.handlers.clear()
            dll_logger.handlers.clear()

            # Re-setup default (what happens on import)
            from hecdss import setup_default_logging
            setup_default_logging()

            # Use the library normally
            dss = HecDss(test_file)
            catalog = dss.get_catalog()

            # Try logging - should produce nothing
            logger = logging.getLogger('hecdss')
            logger.info("This should not appear")
            logger.error("This should not appear either")

            # DLL logger too
            dll_logger = logging.getLogger('hecdss.dll')
            dll_logger.dll_message("This DLL message should not appear")

            dss.close()

    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

    # Get captured output
    stdout_text = stdout_capture.getvalue()
    stderr_text = stderr_capture.getvalue()

    # Report results
    if stdout_text == "" and stderr_text == "":
        print("✓ PASS: No output produced by default (follows Python best practices)")
    else:
        print("✗ FAIL: Unexpected output detected!")
        if stdout_text:
            print(f"  stdout: {repr(stdout_text[:100])}")
        if stderr_text:
            print(f"  stderr: {repr(stderr_text[:100])}")

    print("This ensures the library is silent unless explicitly configured.\n")


def test_explicit_print_still_works():
    """Test that explicit print methods work when called."""
    print("\n=== Test 9: Explicit print() Methods Still Work ===")

    import io
    from contextlib import redirect_stdout
    from hecdss import DssPath

    stdout_capture = io.StringIO()

    with redirect_stdout(stdout_capture):
        # Create a path and explicitly call print
        path = DssPath("/A/B/C/01Jan2024/1Hour/F/")
        path.print()  # This SHOULD produce output

    output = stdout_capture.getvalue()

    # Should see the path parts
    if "a:" in output and "b:" in output:
        print("✓ PASS: Explicit print() methods work when called")
    else:
        print("✗ FAIL: print() method did not produce expected output")
        print(f"  Output: {repr(output[:100])}")

    print("Users can still use print() methods when they want output.\n")


def main():
    """Run all logging tests."""
    print("=" * 60)
    print("HEC-DSS Python Logging Test Suite")
    print("=" * 60)

    # Run tests
    test_basic_logging()
    test_separate_levels()
    test_file_logging()
    test_custom_levels()
    test_no_logging()
    test_with_dss_file()
    test_dll_output_capture()
    test_silent_by_default()
    test_explicit_print_still_works()

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)

    # Clean up any log files created
    for log_file in ['test_python.log', 'test_dll.log']:
        if os.path.exists(log_file):
            os.remove(log_file)
            print(f"Cleaned up {log_file}")


if __name__ == "__main__":
    main()