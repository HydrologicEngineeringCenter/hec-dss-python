
import hashlib
import multiprocessing
import os
import unittest
from datetime import datetime

from file_manager import FileManager

from hecdss import HecDss, OpenAccess


PATHNAME = "//SACRAMENTO/PRECIP-INC//1Day/OBS/"
START = datetime(2005, 1, 1)
END = datetime(2005, 1, 4)

READ_WRITE_ACCESS = [
    OpenAccess.GENERAL_ACCESS,
    OpenAccess.MULTI_USER_ACCESS,
    OpenAccess.SINGLE_USER_ADVISORY_ACCESS,
    OpenAccess.EXCLUSIVE_ACCESS,
]

PROCESS_COUNT = 4
READS_PER_PROCESS = 25

MP_TIMEOUT_SECONDS = 120


def _file_fingerprint(filename):
    """Returns (size, sha256) of a file, used to prove readers do not write."""
    with open(filename, "rb") as f:
        return os.path.getsize(filename), hashlib.sha256(f.read()).hexdigest()


def _read_once(filename):
    """Opens filename read-only and returns the values of PATHNAME."""
    HecDss.set_global_debug_level(0)
    with HecDss(filename, OpenAccess.READ_ACCESS) as dss:
        return list(dss.get(PATHNAME, START, END).values)


def _read_repeatedly(args):
    """Opens filename read-only once and reads PATHNAME repeatedly.

    Returns (pid, number_of_reads_that_returned_the_expected_values).
    """
    filename, iterations, expected = args
    HecDss.set_global_debug_level(0)
    matches = 0
    with HecDss(filename, OpenAccess.READ_ACCESS) as dss:
        for _ in range(iterations):
            if list(dss.get(PATHNAME, START, END).values) == expected:
                matches += 1
    return os.getpid(), matches


def _run_workers(func, arglist):
    """Runs func over arglist in separate spawned processes and returns results."""
    ctx = multiprocessing.get_context("spawn")
    with ctx.Pool(len(arglist)) as pool:
        return pool.map_async(func, arglist).get(timeout=MP_TIMEOUT_SECONDS)


class TestAccessModes(unittest.TestCase):
    """Opening a file with each of the access modes of hec_dss_open_ex."""

    def setUp(self) -> None:
        self.test_files = FileManager()
        HecDss.set_global_debug_level(0)

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_every_access_mode_reads_the_same_data(self):
        filename = self.test_files.get_copy("sample7.dss")

        with HecDss(filename) as dss:
            expected = list(dss.get(PATHNAME, START, END).values)
        self.assertTrue(expected, "test fixture returned no values")

        for access in OpenAccess:
            with self.subTest(access=access.name):
                # a fresh copy per mode, so a writable mode cannot affect the next
                filename = self.test_files.get_copy("sample7.dss")
                with HecDss(filename, access) as dss:
                    self.assertEqual(expected, list(dss.get(PATHNAME, START, END).values))

    def test_default_access_is_general_access(self):
        filename = self.test_files.get_copy("sample7.dss")

        with HecDss(filename) as dss:
            self.assertEqual(OpenAccess.GENERAL_ACCESS, dss.access)
            self.assertFalse(dss.readonly)

    def test_access_is_reported_and_plain_ints_are_accepted(self):
        filename = self.test_files.get_copy("sample7.dss")

        with HecDss(filename, 1) as dss:
            self.assertEqual(OpenAccess.READ_ACCESS, dss.access)
            self.assertTrue(dss.readonly)

    def test_invalid_access_raises_value_error(self):
        filename = self.test_files.get_copy("sample7.dss")

        for access in (-1, 5, "read"):
            with self.subTest(access=access):
                with self.assertRaises(ValueError):
                    HecDss(filename, access)

    def test_read_write_modes_can_write(self):
        for access in READ_WRITE_ACCESS:
            with self.subTest(access=access.name):
                filename = self.test_files.get_copy("sample7.dss")

                with HecDss(filename, access) as dss:
                    self.assertFalse(dss.readonly)
                    ts = dss.get(PATHNAME, START, END)
                    expected = list(ts.values * 2)
                    ts.values = ts.values * 2
                    self.assertEqual(0, dss.put(ts))

                with HecDss(filename, OpenAccess.READ_ACCESS) as dss:
                    self.assertEqual(expected, list(dss.get(PATHNAME, START, END).values))


class TestReadAccess(unittest.TestCase):
    """Read-only behavior in a single process."""

    def setUp(self) -> None:
        self.test_files = FileManager()
        HecDss.set_global_debug_level(0)

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_readonly_catalog_and_record_count(self):
        """Read paths other than get() also work on a read-only handle."""
        filename = self.test_files.get_copy("sample7.dss")

        with HecDss(filename) as dss:
            expected_count = dss.record_count()

        with HecDss(filename, OpenAccess.READ_ACCESS) as dss:
            self.assertEqual(expected_count, dss.record_count())
            self.assertTrue(len(dss.get_catalog().uncondensed_paths) > 0)

    def test_readonly_missing_file_raises_and_does_not_create_it(self):
        missing = self.test_files.create_test_file(".dss")
        self.assertFalse(os.path.exists(missing))

        with self.assertRaises(FileNotFoundError):
            HecDss(missing, OpenAccess.READ_ACCESS)

        self.assertFalse(
            os.path.exists(missing),
            "read-only open must not create the file",
        )

    def test_readwrite_still_creates_missing_file(self):
        """The default path is unchanged by the access argument."""
        filename = self.test_files.create_test_file(".dss")

        with HecDss(filename) as dss:
            self.assertEqual(0, dss.record_count())

        self.assertTrue(os.path.exists(filename))

    def test_put_on_readonly_raises(self):
        filename = self.test_files.get_copy("sample7.dss")

        with HecDss(filename) as dss:
            container = dss.get(PATHNAME, START, END)

        with HecDss(filename, OpenAccess.READ_ACCESS) as dss:
            with self.assertRaises(PermissionError):
                dss.put(container)

    def test_delete_on_readonly_raises(self):
        filename = self.test_files.get_copy("sample7.dss")

        with HecDss(filename, OpenAccess.READ_ACCESS) as dss:
            with self.assertRaises(PermissionError):
                dss.delete(PATHNAME)

    def test_write_precompressed_grid_on_readonly_raises(self):
        filename = self.test_files.get_copy("sample7.dss")

        with HecDss(filename, OpenAccess.READ_ACCESS) as dss:
            with self.assertRaises(PermissionError):
                dss.writePrecompressedGrid(None, b"\x00", 1)

    def test_readonly_reads_do_not_modify_the_file(self):
        filename = self.test_files.get_copy("sample7.dss")
        before = _file_fingerprint(filename)

        with HecDss(filename, OpenAccess.READ_ACCESS) as dss:
            for _ in range(10):
                dss.get(PATHNAME, START, END)

        self.assertEqual(before, _file_fingerprint(filename))

    def test_two_readonly_handles_open_at_once(self):
        """Two handles on one file within a single process."""
        filename = self.test_files.get_copy("sample7.dss")

        first = HecDss(filename, OpenAccess.READ_ACCESS)
        second = HecDss(filename, OpenAccess.READ_ACCESS)
        try:
            values_first = list(first.get(PATHNAME, START, END).values)
            values_second = list(second.get(PATHNAME, START, END).values)
            self.assertEqual(values_first, values_second)
        finally:
            first.close()
            second.close()


class TestMultiProcessRead(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()
        HecDss.set_global_debug_level(0)
        self.filename = self.test_files.get_copy("sample7.dss")
        with HecDss(self.filename) as dss:
            self.expected = list(dss.get(PATHNAME, START, END).values)
        self.assertTrue(self.expected, "test fixture returned no values")

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_concurrent_processes_read_the_same_file(self):
        results = _run_workers(_read_once, [self.filename] * PROCESS_COUNT)

        self.assertEqual(PROCESS_COUNT, len(results))
        for values in results:
            self.assertEqual(self.expected, values)

    def test_concurrent_processes_read_repeatedly(self):
        args = [
            (self.filename, READS_PER_PROCESS, self.expected)
            for _ in range(PROCESS_COUNT)
        ]
        results = _run_workers(_read_repeatedly, args)

        pids = {pid for pid, _ in results}
        self.assertEqual(
            PROCESS_COUNT,
            len(pids),
            f"expected {PROCESS_COUNT} distinct worker processes, got {pids}",
        )

        total = sum(matches for _, matches in results)
        self.assertEqual(PROCESS_COUNT * READS_PER_PROCESS, total)

    def test_concurrent_readers_leave_the_file_unchanged(self):
        before = _file_fingerprint(self.filename)

        _run_workers(_read_once, [self.filename] * PROCESS_COUNT)

        self.assertEqual(
            before,
            _file_fingerprint(self.filename),
            "concurrent read-only readers modified the file",
        )

    def test_concurrent_readers_alongside_a_reader_in_this_process(self):
        """A read-only handle here stays usable while workers read the file."""
        with HecDss(self.filename, OpenAccess.READ_ACCESS) as dss:
            results = _run_workers(_read_once, [self.filename] * PROCESS_COUNT)
            after = list(dss.get(PATHNAME, START, END).values)

        for values in results:
            self.assertEqual(self.expected, values)
        self.assertEqual(self.expected, after)


if __name__ == "__main__":
    unittest.main()
