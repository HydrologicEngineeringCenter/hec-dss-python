import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

from file_manager import FileManager

from hecdss import HecDss
from hecdss.irregular_timeseries import IrregularTimeSeries
from hecdss.regular_timeseries import RegularTimeSeries


class TestCSV(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_to_csv_writes_correct_structure(self):
        # Create a dummy RegularTimeSeries instance
        rts = RegularTimeSeries.create(
            values=[10.5, 20.0],
            times=[datetime(2021, 9, 1, 6, 0), datetime(2021, 9, 1, 12, 0)],
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C/01Sep2021/6Hour/F/",
        )

        # Mock 'open' and capture written content
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            rts.to_csv("fake_path.csv", with_metadata=True)

        # Assert that open was called with correct parameters
        mock_file.assert_called_once_with(
            "fake_path.csv", "w", newline="", encoding="utf-8"
        )

        # Extract all written data
        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)

        # Assertions on the CSV content structure
        self.assertIn("A,,,A", written_data)
        self.assertIn("B,,,B", written_data)
        self.assertIn("C,,,C", written_data)
        self.assertIn("Units,,,CFS", written_data)
        self.assertIn("Type,Date/Time,INST-VAL", written_data)
        self.assertIn("1,01Sep2021 0600,10.5", written_data)
        self.assertIn("2,01Sep2021 1200,20.0", written_data)

    def test_to_csv_without_metadata(self):
        """No metadata rows should be written; only data rows."""
        rts = RegularTimeSeries.create(
            values=[1.0, 2.0],
            times=[datetime(2021, 9, 1, 6, 0), datetime(2021, 9, 1, 12, 0)],
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C//6Hour/F/",
        )
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            rts.to_csv("fake.csv", with_metadata=False)
        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertNotIn("Units", written)
        self.assertNotIn("Type,Date/Time", written)
        self.assertIn("1,01Sep2021 0600,1.0", written)

    def test_to_csv_empty_times(self):
        rts = RegularTimeSeries.create(
            values=[],
            times=[],
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C//6Hour/F/",
        )

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            rts.to_csv("fake_path.csv", with_metadata=True)

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)

        self.assertIn("Units,,,CFS", written_data)
        self.assertIn("Type,Date/Time,INST-VAL", written_data)
        self.assertNotIn("1,", written_data)  # No data rows should be present

    def test_to_csv_second_precision(self):
        rts = RegularTimeSeries.create(
            values=[i for i in range(10)],
            times=[datetime(2021, 9, 1, 6, 0, i) for i in range(10)],
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C//1Second/F/",
        )

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            rts.to_csv("fake_path.csv", with_metadata=True)

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn("Type,Date/Time,INST-VAL", written_data)
        for i in range(10):
            self.assertIn(f"{i + 1},01Sep2021 06000{i},", written_data)

    def test_to_csv_with_quality(self):
        """When quality is present, header gets 'Quality' col and rows get flags."""
        rts = RegularTimeSeries.create(
            values=[1.0, 2.0],
            times=[datetime(2021, 9, 1, 6, 0), datetime(2021, 9, 1, 12, 0)],
            quality=[0, 5],
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C//6Hour/F/",
        )
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            rts.to_csv("fake.csv", with_metadata=True)
        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn("Type,Date/Time,INST-VAL,Quality", written)
        self.assertIn("1,01Sep2021 0600,1.0,0", written)
        self.assertIn("2,01Sep2021 1200,2.0,5", written)

    def read_rts_from_string(self, content):
        """Helper to run read_csv against an in-memory CSV string."""
        m = mock_open(read_data=content)
        with patch("builtins.open", m):
            return RegularTimeSeries.read_csv("fake.csv")

    def test_read_csv_basic(self):
        content = (
            "A,,,A\n"
            "B,,,B\n"
            "C,,,FLOW\n"
            "E,,,6Hour\n"
            "F,,,F\n"
            "Units,,,CFS\n"
            "Type,Date/Time,INST-VAL\n"
            "1,01Sep2021 0600,10.5\n"
            "2,01Sep2021 1200,20.0\n"
        )
        rts = self.read_rts_from_string(content)
        self.assertEqual(rts.units, "CFS")
        self.assertEqual(rts.data_type, "INST-VAL")
        self.assertEqual(rts.values.tolist(), [10.5, 20.0])
        self.assertEqual(rts.times[0], datetime(2021, 9, 1, 6, 0))

    def test_read_csv_midnight_2400_rolls_to_next_day(self):
        content = (
            "E,,,1Day\n"
            "Type,Date/Time,INST-VAL\n"
            "1,31Aug2021 2400,10.5\n"
            "2,01Sep2021 2400,20.0\n"
        )
        rts = self.read_rts_from_string(content)
        self.assertEqual(
            rts.times, [datetime(2021, 9, 1, 0, 0), datetime(2021, 9, 2, 0, 0)]
        )
        self.assertEqual(rts.values.tolist(), [10.5, 20.0])

    def test_read_csv_with_quality(self):
        content = (
            "Type,Date/Time,INST-VAL,Quality\n"
            "1,01Sep2021 0600,10.5,0\n"
            "2,01Sep2021 1200,20.0,5\n"
        )
        rts = self.read_rts_from_string(content)
        self.assertEqual(rts.values.tolist(), [10.5, 20.0])
        self.assertEqual(rts.quality, [0, 5])

    def test_read_csv_with_partial_quality(self):
        content: tuple[str] = (
            "Type,Date/Time,INST-VAL,Quality\n"
            "1,05Nov2004 0200,8,0\n"
            "2,05Nov2004 0300,9\n"  # missing quality!
            "3,05Nov2004 0400,10,1\n"
        )
        rts = self.read_rts_from_string(content)
        self.assertEqual(rts.values.tolist()[0], 8)
        self.assertEqual(rts.values.tolist()[2], 10)
        self.assertEqual(rts.quality[0], 0)
        self.assertEqual(rts.quality[2], 1)

    def test_read_csv_skips_malformed_rows(self):
        content = (
            "Type,Date/Time,INST-VAL\n"
            "1,01Sep2021 0600,10.5\n"
            "2,not-a-date,20.0\n"
            "3,01Sep2021 1200,not-a-number\n"
            "4,01Sep2021 1800,30.0\n"
        )
        rts = self.read_rts_from_string(content)
        self.assertEqual(rts.values.tolist(), [10.5, 30.0])
        self.assertEqual(
            rts.times, [datetime(2021, 9, 1, 6, 0), datetime(2021, 9, 1, 18, 0)]
        )

    def test_read_csv_seconds_precision_basic(self):
        """Reading HHMMSS (seconds-precision) timestamps with no 2400 rollover involved.
        Uses a 15-second gap (a standard DSS interval) so RegularTimeSeries can infer
        the interval from the deltas without a metadata E row."""
        content = (
            "Type,Date/Time,INST-VAL\n"
            "1,01Sep2021 060000,10.5\n"
            "2,01Sep2021 060015,20.0\n"
        )
        rts = self.read_rts_from_string(content)
        self.assertEqual(rts.values.tolist(), [10.5, 20.0])
        self.assertEqual(
            rts.times,
            [datetime(2021, 9, 1, 6, 0, 0), datetime(2021, 9, 1, 6, 0, 15)],
        )

    def test_read_csv_skips_wrong_length_time(self):
        """A time field that isn't 4 (minutes) or 6 (seconds) digits doesn't match
        either DSS format, so the row should be skipped rather than raise."""
        content = (
            "Type,Date/Time,INST-VAL\n"
            "1,01Sep2021 0600,10.5\n"
            "2,01Sep2021 12345,20.0\n"  # 5-digit clock -- not a valid DSS format
            "3,01Sep2021 1800,30.0\n"
        )
        rts = self.read_rts_from_string(content)
        self.assertEqual(rts.values.tolist(), [10.5, 30.0])
        self.assertEqual(
            rts.times, [datetime(2021, 9, 1, 6, 0), datetime(2021, 9, 1, 18, 0)]
        )

    def test_read_csv_single_digit_day_skipped(self):
        """The format regex requires a zero-padded 2-digit day (matching this
        library's own writer output), so a single-digit day doesn't match
        and the row is skipped."""
        content = (
            "Type,Date/Time,INST-VAL\n"
            "1,1Sep2021 0600,10.5\n"  # single-digit day
            "2,01Sep2021 1200,20.0\n"
        )
        rts = self.read_rts_from_string(content)
        self.assertEqual(rts.values.tolist(), [20.0])
        self.assertEqual(rts.times, [datetime(2021, 9, 1, 12, 0)])

    def test_read_csv_month_case_mismatch_skipped(self):
        """The format regex requires a title-case month abbreviation (matching
        this library's own writer output); other casings don't match and are
        skipped, even though datetime.strptime itself would accept them."""
        content = (
            "Type,Date/Time,INST-VAL\n"
            "1,01SEP2021 0600,10.5\n"  # all-caps month
            "2,01sep2021 1200,20.0\n"  # all-lowercase month
            "3,01Sep2021 1800,30.0\n"
        )
        rts = self.read_rts_from_string(content)
        self.assertEqual(rts.values.tolist(), [30.0])
        self.assertEqual(rts.times, [datetime(2021, 9, 1, 18, 0)])

    def test_read_csv_2400_with_nonzero_seconds_not_treated_as_rollover(self):
        """24:00:15 is not a valid DSS midnight-rollover (only 24:00:00 is) and
        should be rejected as malformed rather than silently rolled to the
        next day with the seconds preserved. Covers the same edge case as
        test_year_is_2400, but for the RegularTimeSeries read path."""
        content = (
            "Type,Date/Time,INST-VAL\n"
            "1,15Sep2021 240015,10.5\n"
        )
        rts = self.read_rts_from_string(content)
        self.assertEqual(rts.values.tolist(), [])
        self.assertEqual(rts.times, [])

    def test_read_csv_empty_file(self):
        rts = self.read_rts_from_string("")
        self.assertEqual(rts.values.tolist(), [])
        self.assertEqual(rts.times, [])

    def test_read_csv_single_row_uses_path_interval(self):
        content = "E,,,6Hour\n" "Type,Date/Time,INST-VAL\n" "1,01Sep2021 0600,10.5\n"
        rts = self.read_rts_from_string(content)
        self.assertEqual(rts.values.tolist(), [10.5])
        self.assertEqual(rts.times, [datetime(2021, 9, 1, 6, 0)])

    def test_read_csv_irregular_interval_raises(self):
        """RegularTimeSeries.read_csv expects a genuinely regular interval;
        data implying an irregular gap (with no usable E row) is not valid
        input for this class (that's what IrregularTimeSeries is for)."""
        content = (
            "Type,Date/Time,INST-VAL\n"
            "1,01Sep2021 0600,10.5\n"
            "2,01Sep2021 0637,20.0\n"
        )
        with self.assertRaises(ValueError):
            self.read_rts_from_string(content)

    def test_round_trip_basic(self):
        path = self.test_files.create_test_file(".csv")
        rts = RegularTimeSeries.create(
            values=[10.5, 20.0],
            times=[datetime(2021, 9, 1, 6, 0), datetime(2021, 9, 1, 12, 0)],
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C/01Sep2021/6Hour/F/",
        )
        rts.to_csv(path, with_metadata=True)
        result = RegularTimeSeries.read_csv(path)

        self.assertEqual(result.units, "CFS")
        self.assertEqual(result.data_type, "INST-VAL")
        self.assertEqual(result.interval, "6Hour")
        self.assertEqual(result.id, "/A/B/C//6Hour/F/")
        self.assertEqual(result.values.tolist(), [10.5, 20.0])
        self.assertEqual(
            result.times,
            [datetime(2021, 9, 1, 6, 0), datetime(2021, 9, 1, 12, 0)],
        )

    def test_round_trip_with_quality(self):
        path = self.test_files.create_test_file(".csv")
        rts = RegularTimeSeries.create(
            values=[1.0, 2.0, 3.0],
            times=[
                datetime(2021, 9, 1, 6, 0),
                datetime(2021, 9, 1, 12, 0),
                datetime(2021, 9, 1, 18, 0),
            ],
            quality=[0, 5, 10],
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C//6Hour/F/",
        )
        rts.to_csv(path, with_metadata=True)
        result = RegularTimeSeries.read_csv(path)

        self.assertEqual(result.values.tolist(), [1.0, 2.0, 3.0])
        self.assertEqual(result.quality, [0, 5, 10])

    def test_round_trip_without_metadata_infers_interval_from_times(self):
        """With no metadata rows, units/data_type come back empty but values,
        times, and the interval/id (inferred from the time deltas) are still
        recovered correctly."""
        path = self.test_files.create_test_file(".csv")
        rts = RegularTimeSeries.create(
            values=[1.0, 2.0],
            times=[datetime(2021, 9, 1, 6, 0), datetime(2021, 9, 1, 12, 0)],
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C//6Hour/F/",
        )
        rts.to_csv(path, with_metadata=False)
        result = RegularTimeSeries.read_csv(path)

        self.assertEqual(result.units, "")
        self.assertEqual(result.data_type, "")
        self.assertEqual(result.interval, 21600)
        self.assertEqual(result.id, "/////6Hour//")
        self.assertEqual(result.values.tolist(), [1.0, 2.0])
        self.assertEqual(
            result.times,
            [datetime(2021, 9, 1, 6, 0), datetime(2021, 9, 1, 12, 0)],
        )

    # IRREGULAR TIME SERIES TESTS:

    def test_basic_to_csv_irregular(self):
        """
        Basic structure test for irregular time series to_csv
        """
        # Create a dummy IrregularTimeSeries instance
        its = IrregularTimeSeries.create(
            values=[10.5, 20.0, 42.0],
            times=[
                datetime(2021, 9, 1, 0, 0),
                datetime(2021, 9, 2, 0, 0),
                datetime(2021, 9, 4, 0, 0),
            ],  # inconsistent time interval
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C/01Sep2021/E/F/",
        )

        # Mock 'open' and capture written content
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            its.to_csv("fake_path.csv", with_metadata=True)

        # Assert that open was called with correct parameters
        mock_file.assert_called_once_with(
            "fake_path.csv", "w", newline="", encoding="utf-8"
        )

        # Extract all written data
        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)

        # Assertions on the CSV content structure
        self.assertIn("A,,,A", written_data)
        self.assertIn("B,,,B", written_data)
        self.assertIn("C,,,C", written_data)
        self.assertIn("Units,,,CFS", written_data)
        self.assertIn("Type,Date/Time,INST-VAL", written_data)
        self.assertIn("1,01Sep2021 0000,10.5", written_data)
        self.assertIn("2,02Sep2021 0000,20.0", written_data)
        self.assertIn("3,04Sep2021 0000,42.0", written_data)

    def test_irregular_to_csv_without_metadata(self):
        """No metadata rows should be written; only data rows."""
        its = IrregularTimeSeries.create(
            values=[10.5, 20.0, 42.0],
            times=[
                datetime(2021, 9, 1, 0, 0),
                datetime(2021, 9, 2, 0, 0),
                datetime(2021, 9, 4, 0, 0),
            ],  # inconsistent time interval
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C/01Sep2021/E/F/",
        )
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            its.to_csv("fake.csv", with_metadata=False)
        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertNotIn("Units", written)
        self.assertNotIn("Type,Date/Time", written)
        self.assertIn("1,01Sep2021 0000,10.5", written)
        self.assertIn("2,02Sep2021 0000,20.0", written)
        self.assertIn("3,04Sep2021 0000,42.0", written)

    def test_irregular_to_csv_empty_times(self):
        its = IrregularTimeSeries.create(
            values=[],
            times=[],
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C//E/F/",
        )

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            its.to_csv("fake_path.csv", with_metadata=True)

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)

        self.assertIn("Units,,,CFS", written_data)
        self.assertIn("Type,Date/Time,INST-VAL", written_data)
        self.assertNotIn("1,", written_data)  # No data rows should be present

    def test_irregular_to_csv_second_precision(self):
        its = IrregularTimeSeries.create(
            values=[i for i in range(3)],
            times=[
                datetime(2021, 9, 1, 6, 0, 0),
                datetime(2021, 9, 1, 6, 0, 1),
                datetime(2021, 9, 1, 6, 0, 4),
            ],
            units="CFS",
            data_type="INST-VAL",
            path="/A/B/C//E/F/",
        )

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            its.to_csv("fake_path.csv", with_metadata=True)

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn("Type,Date/Time,INST-VAL", written_data)
        self.assertIn("1,01Sep2021 060000,0", written_data)
        self.assertIn("2,01Sep2021 060001,1", written_data)
        self.assertIn("3,01Sep2021 060004,2", written_data)

    def read_its_from_string(self, content):
        """Helper to run read_csv against an in-memory CSV string."""
        m = mock_open(read_data=content)
        with patch("builtins.open", m):
            return IrregularTimeSeries.read_csv("fake.csv")

    def test_irregular_read_csv_basic(self):
        content = (
            "A,,,A\n"
            "B,,,B\n"
            "C,,,FLOW\n"
            "E,,,IR-Year\n"
            "F,,,F\n"
            "Units,,,CFS\n"
            "Type,Date/Time,INST-VAL\n"
            "1,01Sep2021 0000,10.5\n"
            "2,02Sep2021 0000,20.0\n"
            "3,04Sep2021 0000,20.0\n"
        )
        its = self.read_its_from_string(content)
        self.assertEqual(its.units, "CFS")
        self.assertEqual(its.data_type, "INST-VAL")
        self.assertEqual(its.values.tolist(), [10.5, 20.0, 20.0])
        self.assertEqual(
            its.times,
            [datetime(2021, 9, 1), datetime(2021, 9, 2), datetime(2021, 9, 4)],
        )

    # EDGE CASE TESTS:

    def test_roll_day_edge_case(self):
        content = (
            "A,,,A\n"
            "B,,,B\n"
            "C,,,FLOW\n"
            "E,,,IR-Day\n"
            "F,,,F\n"
            "Units,,,CFS\n"
            "Type,Date/Time,INST-VAL\n"
            "1,01Sep2021 002400,1\n"  # 12:24 AM
            "2,02Sep2021 024000,1\n"  # 2:40 AM
            "3,03Sep2021 240000,1\n"  # 12:00 AM Next day
        )
        its = self.read_its_from_string(content)
        self.assertEqual(its.units, "CFS")
        self.assertEqual(its.data_type, "INST-VAL")
        self.assertEqual(its.values.tolist(), [1, 1, 1])
        self.assertEqual(its.times, [datetime(2021, 9, 1, 0, 24, 0), datetime(
            2021, 9, 2, 2, 40, 0), datetime(2021, 9, 4, 0, 0, 0)])

    def test_year_is_2400(self):
        content = (
            "A,,,A\n"
            "B,,,B\n"
            "C,,,FLOW\n"
            "E,,,IR-Day\n"
            "F,,,F\n"
            "Units,,,CFS\n"
            "Type,Date/Time,INST-VAL\n"
            "1,01Sep2400 000000,1\n"
            "2,01Sep2400 240000,1\n"
            "3,01Sep2400 240015,1\n"  # Should not be accepted
            "4,01Sep2400 24000,1\n"  # Should not be accepted
        )
        its = self.read_its_from_string(content)
        self.assertEqual(its.units, "CFS")
        self.assertEqual(its.data_type, "INST-VAL")
        self.assertEqual(its.values.tolist(), [1, 1])
        self.assertEqual(its.times, [datetime(2400, 9, 1, 0, 0, 0), datetime(2400, 9, 2, 0, 0, 0)])


if __name__ == "__main__":
    unittest.main()
