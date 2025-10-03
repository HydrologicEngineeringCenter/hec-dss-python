"""Pytest module for testing logging functionality in hec-dss-python."""

import logging
import os
import io
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from file_manager import FileManager

from hecdss import (
    HecDss,
    configure_logging,
    DLL_MESSAGE,
    setup_default_logging,
    DssPath
)


class TestLogging(unittest.TestCase):

    def setUp(self) -> None:
        """Set up test environment before each test."""
        self.test_files = FileManager()
        # Clear any existing logging handlers, closing them first
        root_logger = logging.getLogger('hecdss')
        dll_logger = logging.getLogger('hecdss.dll')

        # Close file handlers before clearing
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)

        for handler in dll_logger.handlers[:]:
            handler.close()
            dll_logger.removeHandler(handler)

        # Reset DLL debug level to silent
        HecDss.set_global_debug_level(0)

    def tearDown(self) -> None:
        """Clean up after each test."""
        self.test_files.cleanup()

        # Close any remaining handlers
        root_logger = logging.getLogger('hecdss')
        dll_logger = logging.getLogger('hecdss.dll')

        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)

        for handler in dll_logger.handlers[:]:
            handler.close()
            dll_logger.removeHandler(handler)

        # Clean up any log files created during tests
        for log_file in ['test_python.log', 'test_dll.log']:
            if os.path.exists(log_file):
                try:
                    os.remove(log_file)
                except PermissionError:
                    pass  # File might still be in use

    def test_basic_logging(self):
        """Test basic logging configuration."""
        # Configure to show Python INFO and DLL general messages
        configure_logging(
            python_level=logging.INFO,
            dll_level=3,  # MESS_LEVEL_GENERAL
            format_string='%(name)s - %(levelname)s - %(message)s'
        )

        # Get a logger and test it
        logger = logging.getLogger('hecdss.test')

        # Capture log output
        with self.assertLogs('hecdss.test', level=logging.INFO) as cm:
            logger.info("This is an INFO message from Python code")
            logger.debug("This DEBUG message should not appear (level too low)")

        # Check that only INFO message was logged
        self.assertEqual(len(cm.output), 1)
        self.assertIn("INFO", cm.output[0])
        self.assertIn("This is an INFO message", cm.output[0])

    def test_separate_levels(self):
        """Test separate control of Python and DLL logging."""
        # Show only errors from Python but diagnostic messages from DLL
        configure_logging(
            python_level=logging.ERROR,
            dll_level=4  # MESS_LEVEL_USER_DIAG
        )

        logger = logging.getLogger('hecdss.test')

        # INFO should not appear, but ERROR should
        with self.assertLogs('hecdss.test', level=logging.ERROR) as cm:
            logger.info("This INFO should NOT appear")
            logger.error("This ERROR should appear")

        self.assertEqual(len(cm.output), 1)
        self.assertIn("ERROR", cm.output[0])
        self.assertIn("This ERROR should appear", cm.output[0])

    def test_file_logging(self):
        """Test logging to files."""
        # Use temporary directory for log files
        with tempfile.TemporaryDirectory() as tmpdir:
            python_log = os.path.join(tmpdir, 'test_python.log')
            dll_log = os.path.join(tmpdir, 'test_dll.log')

            # Configure separate files for Python and DLL
            configure_logging(
                python_file=python_log,
                dll_file=dll_log,
                python_level=logging.DEBUG,
                dll_level=4,
                console=False  # Don't output to console
            )

            logger = logging.getLogger('hecdss.test')
            logger.debug("Debug message to Python log file")
            logger.info("Info message to Python log file")

            # Check that log file was created and has content
            self.assertTrue(os.path.exists(python_log))
            with open(python_log, 'r') as f:
                content = f.read()
                self.assertIn("Debug message", content)
                self.assertIn("Info message", content)

            # Important: Close and remove all file handlers before exiting
            root_logger = logging.getLogger('hecdss')
            dll_logger = logging.getLogger('hecdss.dll')

            handlers_to_remove = []

            # Collect all file handlers
            for handler in root_logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handlers_to_remove.append((root_logger, handler))

            for handler in dll_logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handlers_to_remove.append((dll_logger, handler))

            # Close and remove them
            for logger_ref, handler in handlers_to_remove:
                handler.close()
                logger_ref.removeHandler(handler)

    def test_custom_dll_message_level(self):
        """Test custom DLL message level."""
        # Configure to show DLL messages
        configure_logging(
            dll_level=4,  # Set DLL to user diagnostic level
            format_string='%(levelname)-15s - %(message)s'
        )

        # Get DLL logger to demonstrate the single DLL level
        dll_logger = logging.getLogger('hecdss.dll')

        # Test that dll_message method exists and works
        with self.assertLogs('hecdss.dll', level=DLL_MESSAGE) as cm:
            dll_logger.dll_message("This is a DLL message")
            dll_logger.dll_message("All DLL messages use the same Python log level")

        self.assertEqual(len(cm.output), 2)
        self.assertIn("DLL", cm.output[0])

    def test_no_logging_by_default(self):
        """Test that logging can be completely disabled."""
        # Reset to default (no output)
        setup_default_logging()

        logger = logging.getLogger('hecdss.test')

        # Should not raise because of NullHandler
        logger.info("This should not appear anywhere")
        logger.error("This error should also not appear")

        # Check that root logger has NullHandler
        root_logger = logging.getLogger('hecdss')
        self.assertTrue(any(isinstance(h, logging.NullHandler) for h in root_logger.handlers))

    def test_with_dss_file(self):
        """Test logging with actual DSS file operations."""
        # Configure logging to see what's happening
        configure_logging(
            python_level=logging.INFO,
            dll_level=3,  # General log messages
            format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        test_file = self.test_files.create_test_file(".dss")

        with HecDss(test_file) as dss:
            logger = logging.getLogger('hecdss.test')

            with self.assertLogs('hecdss', level=logging.INFO) as cm:
                logger.info(f"Successfully opened {test_file}")
                catalog = dss.get_catalog()
                logger.info(f"Catalog has {len(catalog.items)} items")

            # Should have at least the two info messages
            self.assertGreaterEqual(len(cm.output), 2)

    def test_dll_output_capture_without_zopen_log(self):
        """Test that DLL output capture fails gracefully without zopenLog."""
        # Configure logging with DLL output capture
        configure_logging(
            python_level=logging.INFO,
            dll_level=4,  # User diagnostic messages
            capture_dll_output=True  # Enable DLL capture setup
        )

        test_file = self.test_files.create_test_file(".dss")

        # Create HecDss with DLL logging enabled
        # This should fail gracefully if zopenLog is not available
        with HecDss(test_file, enable_dll_logging=True, message_level=0) as dss:
            # Should work without errors even if zopenLog isn't available
            catalog = dss.get_catalog()
            self.assertIsNotNone(catalog)

    def test_silent_by_default(self):
        """Test that hec-dss-python produces NO output by default."""
        # Capture all output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        test_file = self.test_files.create_test_file(".dss")

        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Fresh setup - clear any existing handlers
            root_logger = logging.getLogger('hecdss')
            dll_logger = logging.getLogger('hecdss.dll')
            root_logger.handlers.clear()
            dll_logger.handlers.clear()

            # Re-setup default (what happens on import)
            setup_default_logging()

            # Use the library normally
            with HecDss(test_file, message_level=0) as dss:
                catalog = dss.get_catalog()

                # Try logging - should produce nothing
                logger = logging.getLogger('hecdss')
                logger.info("This should not appear")
                logger.error("This should not appear either")

                # DLL logger too
                dll_logger = logging.getLogger('hecdss.dll')
                dll_logger.dll_message("This DLL message should not appear")

        # Get captured output
        stdout_text = stdout_capture.getvalue()
        stderr_text = stderr_capture.getvalue()

        # Should be completely silent
        self.assertEqual(stdout_text, "")
        self.assertEqual(stderr_text, "")

    def test_explicit_print_still_works(self):
        """Test that explicit print methods work when called."""
        stdout_capture = io.StringIO()

        with redirect_stdout(stdout_capture):
            # Create a path and explicitly call print
            path = DssPath("/A/B/C/01Jan2024/1Hour/F/")
            path.print()  # This SHOULD produce output

        output = stdout_capture.getvalue()

        # Should see the path parts
        self.assertIn("a:", output)
        self.assertIn("b:", output)
        self.assertIn("c:", output)

    def test_set_global_debug_level(self):
        """Test setting global DLL debug level."""
        # This should work without errors
        HecDss.set_global_debug_level(0)  # Silent
        HecDss.set_global_debug_level(3)  # General

        # Test higher levels briefly
        HecDss.set_global_debug_level(6)  # Full debug
        # Immediately set back to silent to avoid debug output
        HecDss.set_global_debug_level(0)

        # Test that level is clamped to valid range
        HecDss.set_global_debug_level(-1)  # Should become 0
        HecDss.set_global_debug_level(20)  # Should become 15
        # Set back to silent
        HecDss.set_global_debug_level(0)

        # No assertions needed - just checking it doesn't crash

    def test_dll_message_level_enum(self):
        """Test that DLL_MESSAGE level is properly defined."""
        self.assertEqual(DLL_MESSAGE, 25)
        self.assertTrue(logging.INFO < DLL_MESSAGE < logging.WARNING)


if __name__ == "__main__":
    unittest.main()