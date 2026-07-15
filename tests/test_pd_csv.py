import math
import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

from file_manager import FileManager

from hecdss import HecDss
from hecdss.dss_csv import (
    DEFAULT_MISSING_VALUE,
    paired_data_read_csv,
    paired_data_to_csv,
)
from hecdss.paired_data import PairedData
from hecdss.regular_timeseries import RegularTimeSeries


class TestCSV(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def read_pd_from_string(self, content: str) -> PairedData:
        """
        Helper to run read_csv against an in-memory CSV string.

        Parameters:
            content (str): PairedData CSV string

        Returns:
            PairedData: PairedData object read from string CSV
        """
        m = mock_open(read_data=content)
        with patch("builtins.open", m):
            return PairedData.read_csv("fake.csv")

    def write_pd_to_string(self, pd: PairedData, with_metadata: bool = True) -> str:
        """
        Helper to run to_csv against a mocked file and return everything written.

        Parameters:
            pd (PairedData): the object to export
            with_metadata (bool): whether metadata rows are written

        Returns:
            str: the full CSV text that to_csv wrote
        """
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            pd.to_csv("fake_path.csv", with_metadata=with_metadata)
        handle = mock_file()
        return "".join(call.args[0] for call in handle.write.call_args_list)

    @staticmethod
    def make_pd(**overrides) -> PairedData:
        """A small, fully-populated PairedData with fields overridable per test."""
        params = dict(
            x_values=[1.0, 2.0],
            y_values=[[10.0, 100.0], [20.0, 200.0]],
            labels=["L1", "L2"],
            x_units="FEET",
            x_type="UNT",
            y_units="CFS",
            y_type="LINEAR",
            path="/A/B/C/DATE/E/F/",
        )
        params.update(overrides)
        return PairedData.create(**params)

    # ================================================================== #
    # to_csv  (write)
    # ================================================================== #

    def test_multiple_curves_to_csv(self):
        """
        This test ensures that the data values for a PairedData object with multiple curves are correct.
        This has no checks related to units or labels.
        """
        num_curves: int = 3
        x_values: list[float] = [1.0, 1.5, 4.0]
        y_values: list[list[float]] = [[x * i for i in range(num_curves)] for x in x_values]
        labels: list[str] = [f"x times {i}" for i in range(num_curves)]
        path: str = "/A/B/C///Source: I made it up/"
        pd: PairedData = PairedData.create(
            x_values=x_values,
            y_values=y_values,
            labels=labels,
            path=path
        )

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            pd.to_csv("fake_path.csv", with_metadata=True)

        mock_file.assert_called_once_with(
            "fake_path.csv", "w", newline="", encoding="utf-8"
        )

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)

        self.assertIn("A,,A", written_data)
        self.assertIn("B,,B", written_data)
        self.assertIn("C,,C", written_data)
        self.assertIn("1,1.0,0.0,1.0,2.0", written_data)
        self.assertIn("2,1.5,0.0,1.5,3.0", written_data)
        self.assertIn("3,4.0,0.0,4.0,8.0", written_data)

    def test_to_csv_without_metadata(self):
        num_curves: int = 3
        x_values: list[float] = [1.0, 1.5, 4.0]
        y_values: list[list[float]] = [[x * i for i in range(num_curves)] for x in x_values]
        labels: list[str] = [f"x times {i}" for i in range(num_curves)]
        path: str = "/A/B/C///Source: I made it up/"
        pd: PairedData = PairedData.create(
            x_values=x_values,
            y_values=y_values,
            labels=labels,
            path=path
        )

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            pd.to_csv("fake_path.csv", with_metadata=False)

        mock_file.assert_called_once_with(
            "fake_path.csv", "w", newline="", encoding="utf-8"
        )

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)

        self.assertNotIn("A,,A", written_data)
        self.assertNotIn("B,,B", written_data)
        self.assertNotIn("C,,C", written_data)
        self.assertNotIn("F,,Source: I made it up", written_data)
        self.assertNotIn("Labels", written_data)
        self.assertIn("Type", written_data)
        self.assertIn("1,1.0,0.0,1.0,2.0", written_data)
        self.assertIn("2,1.5,0.0,1.5,3.0", written_data)
        self.assertIn("3,4.0,0.0,4.0,8.0", written_data)

    # def test_temp(self):
    #     file_path: str = "./tests/data/examples-all-data-types.dss"
    #     with HecDss(file_path) as dss:
    #         data_path: str = "/paired-data-multi-column/RIVERDALE/FREQ-FLOW/MAX ANALYTICAL//1969-01 H33(MAX)/"
    #         data: PairedData = dss.get(data_path)
    #         export_path: str = "./tests/csv_testing/paired_data_test.csv"
    #         data.to_csv(export_path)

    def test_to_csv_metadata_rows_present(self):
        """Every metadata row (path parts, labels, units, type) is written."""
        written = self.write_pd_to_string(self.make_pd(), with_metadata=True)
        self.assertIn("A,,A", written)
        self.assertIn("B,,B", written)
        self.assertIn("C,,C", written)
        self.assertIn("E,,E", written)
        self.assertIn("F,,F", written)
        self.assertIn("Labels,,L1,L2", written)
        self.assertIn("Units,FEET,CFS", written)
        self.assertIn("Type,UNT,LINEAR", written)

    def test_to_csv_skips_d_part(self):
        """The D (date) path part is dropped by convention; E is still written."""
        pd = self.make_pd(path="/A/B/C/DPART/EPART/FPART/")
        written = self.write_pd_to_string(pd, with_metadata=True)
        self.assertNotIn("DPART", written)
        self.assertIn("E,,EPART", written)
        self.assertIn("F,,FPART", written)

    def test_to_csv_data_rows(self):
        """Data rows are index, x, then the row-major y values."""
        written = self.write_pd_to_string(self.make_pd(), with_metadata=True)
        self.assertIn("1,1.0,10.0,100.0", written)
        self.assertIn("2,2.0,20.0,200.0", written)

    def test_to_csv_ordinate_counter_increments(self):
        """The leading index column counts up from 1, one per ordinate."""
        pd = self.make_pd(
            x_values=[5.0, 6.0, 7.0],
            y_values=[[1.0], [2.0], [3.0]],
        )
        written = self.write_pd_to_string(pd, with_metadata=False)
        self.assertIn("1,5.0,1.0", written)
        self.assertIn("2,6.0,2.0", written)
        self.assertIn("3,7.0,3.0", written)

    def test_to_csv_single_curve(self):
        """A single dependent column round-trips through the writer fine."""
        pd = self.make_pd(y_values=[[10.0], [20.0]], labels=["only"])
        written = self.write_pd_to_string(pd, with_metadata=True)
        self.assertIn("Labels,,only", written)
        self.assertIn("1,1.0,10.0", written)
        self.assertIn("2,2.0,20.0", written)

    def test_to_csv_rounds_to_four_decimals(self):
        """x and y are rounded to ROUND_PRECISION (4) decimal places."""
        pd = self.make_pd(x_values=[1.23456], y_values=[[9.87654]], labels=["a"])
        written = self.write_pd_to_string(pd, with_metadata=False)
        self.assertIn("1,1.2346,9.8765", written)

    def test_to_csv_negative_values(self):
        """Negative x/y values are written verbatim."""
        pd = self.make_pd(x_values=[-1.0], y_values=[[-5.5, -0.25]], labels=["a", "b"])
        written = self.write_pd_to_string(pd, with_metadata=False)
        self.assertIn("1,-1.0,-5.5,-0.25", written)

    def test_to_csv_empty_ordinates_writes_no_data_rows(self):
        """No ordinates -> metadata is present but there are no numbered data rows."""
        # Labels avoid digits so the "no data row" check can't collide with a label.
        pd = self.make_pd(x_values=[], y_values=[], labels=["aa", "bb"])
        written = self.write_pd_to_string(pd, with_metadata=True)
        self.assertIn("Units,FEET,CFS", written)
        self.assertIn("Type,UNT,LINEAR", written)
        self.assertNotIn("1,", written)  # no data rows

    def test_to_csv_none_id_writes_empty_path_parts(self):
        """A None id still emits empty A-F rows rather than raising."""
        pd = self.make_pd(path=None)
        written = self.write_pd_to_string(pd, with_metadata=True)
        for letter in ("A", "B", "C", "E", "F"):
            self.assertIn(f"{letter},,", written)

    def test_to_csv_raises_on_non_paireddata(self):
        """paired_data_to_csv rejects anything that isn't a PairedData."""
        with self.assertRaises(TypeError):
            paired_data_to_csv("not a paired data", "fake.csv", True)

    # ================================================================== #
    # read_csv  (read)
    # ================================================================== #

    def test_basic_read_csv(self):
        content: str = (
            "A,,paired-data-test\n"
            "B,,berkeley\n"
            "C,,FREQ-FLOW\n"
            "E,,\n"
            "F,,Source: I made it up\n"
            "Labels,,IMAGINARY,X,Y,Z\n"
            "Units,DAYS,PPG\n"
            "Type,TIME,POINTS\n"
            "1,0,1,5,6,8\n"
            "2,1,3,5,6,9\n"
            "3,5,1,2,3,4\n"
        )
        pd: PairedData = self.read_pd_from_string(content)
        self.assertEqual(pd.labels, ['IMAGINARY', 'X', 'Y', 'Z'])
        self.assertEqual(pd.units_independent, "DAYS")
        self.assertEqual(pd.units_dependent, "PPG")
        self.assertEqual(pd.type_independent, 'TIME')
        self.assertEqual(pd.type_dependent, 'POINTS')
        self.assertEqual(pd.ordinates.tolist(), [0.0, 1.0, 5.0])
        self.assertEqual(pd.values.tolist(), [
            [1.0, 5.0, 6.0, 8.0],
            [3.0, 5.0, 6.0, 9.0],
            [1.0, 2.0, 3.0, 4.0]
        ])

    def test_read_csv_single_curve(self):
        content = (
            "Type,TIME,POINTS\n"
            "1,0,10\n"
            "2,1,20\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.ordinates.tolist(), [0.0, 1.0])
        self.assertEqual(pd.values.tolist(), [[10.0], [20.0]])
        self.assertEqual(pd.curve_count(), 1)

    def test_read_csv_data_only_no_metadata(self):
        """Data rows with no metadata rows still populate ordinates/values."""
        content = (
            "1,0,10,100\n"
            "2,1,20,200\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.ordinates.tolist(), [0.0, 1.0])
        self.assertEqual(pd.values.tolist(), [[10.0, 100.0], [20.0, 200.0]])
        self.assertEqual(pd.labels, [])
        self.assertEqual(pd.units_independent, "")

    def test_read_csv_builds_id_from_path_parts(self):
        content = (
            "A,,SITE\n"
            "B,,LOC\n"
            "C,,STAGE-FLOW\n"
            "E,,\n"
            "F,,MADEUP\n"
            "Type,STAGE,FLOW\n"
            "1,0,10\n"
        )
        pd = self.read_pd_from_string(content)
        # D is never present in a paired-data CSV, so both D and E are empty here.
        self.assertEqual(pd.id, "/SITE/LOC/STAGE-FLOW///MADEUP/")

    def test_read_csv_curve_count(self):
        content = (
            "Type,TIME,POINTS\n"
            "1,0,1,2,3\n"
            "2,1,4,5,6\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.curve_count(), 3)

    def test_read_csv_malformed_x_defaults_missing(self):
        """A non-numeric x cell falls back to the missing-value default (0.0)."""
        content = (
            "Type,TIME,POINTS\n"
            "1,not-a-number,10,100\n"
            "2,2,20,200\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.ordinates.tolist(), [DEFAULT_MISSING_VALUE, 2.0])
        self.assertEqual(pd.values.tolist(), [[10.0, 100.0], [20.0, 200.0]])

    def test_read_csv_malformed_y_defaults_missing(self):
        """A non-numeric y cell falls back to the default WITHOUT shortening the row,
        so the value matrix stays rectangular."""
        content = (
            "Type,TIME,POINTS\n"
            "1,1,bad,3\n"
            "2,2,5,6\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.values.tolist(), [[DEFAULT_MISSING_VALUE, 3.0], [5.0, 6.0]])

    def test_read_csv_empty_cells_default_missing(self):
        """Blank x and y cells become the missing-value default (0.0)."""
        content = (
            "Type,TIME,POINTS\n"
            "1,,\n"
            "2,2,\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.ordinates.tolist(), [DEFAULT_MISSING_VALUE, 2.0])
        self.assertEqual(pd.values.tolist(), [[DEFAULT_MISSING_VALUE], [DEFAULT_MISSING_VALUE]])

    def test_read_csv_skips_short_rows(self):
        """A data row with fewer than 3 columns is malformed and skipped."""
        content = (
            "Type,TIME,POINTS\n"
            "1,5\n"        # only 2 columns -> skipped
            "2,2,9\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.ordinates.tolist(), [2.0])
        self.assertEqual(pd.values.tolist(), [[9.0]])

    def test_read_csv_strips_numeric_whitespace(self):
        """Surrounding whitespace around numeric cells is stripped before parsing."""
        content = (
            "Type,TIME,POINTS\n"
            "1, 1 , 2 , 3 \n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.ordinates.tolist(), [1.0])
        self.assertEqual(pd.values.tolist(), [[2.0, 3.0]])

    def test_read_csv_labels_preserve_whitespace(self):
        """Labels are captured verbatim from row[2:] (not stripped)."""
        content = (
            "Labels,,  spacey  ,X\n"
            "Type,TIME,POINTS\n"
            "1,0,1,2\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.labels, ["  spacey  ", "X"])

    def test_read_csv_partial_units_row(self):
        """A Units row missing the dependent column leaves y_units empty, no crash."""
        content = (
            "Units,DAYS\n"
            "Type,TIME,POINTS\n"
            "1,0,10\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.units_independent, "DAYS")
        self.assertEqual(pd.units_dependent, "")

    def test_read_csv_partial_type_row(self):
        """A Type row missing the dependent column leaves y_type empty, no crash."""
        content = (
            "Type,TIME\n"
            "1,0,10\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.type_independent, "TIME")
        self.assertEqual(pd.type_dependent, "")

    def test_read_csv_units_first_column_only(self):
        """A bare 'Units' row (no values at all) is ignored gracefully."""
        content = (
            "Units\n"
            "Type,TIME,POINTS\n"
            "1,0,10\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.units_independent, "")
        self.assertEqual(pd.units_dependent, "")
        self.assertEqual(pd.ordinates.tolist(), [0.0])

    def test_read_csv_empty_file(self):
        pd = self.read_pd_from_string("")
        self.assertEqual(pd.ordinates.tolist(), [])
        self.assertEqual(pd.values.tolist(), [])
        self.assertEqual(pd.labels, [])

    def test_read_csv_blank_lines_ignored(self):
        content = (
            "Type,TIME,POINTS\n"
            "\n"
            "1,0,10\n"
            "\n"
            "2,1,20\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.ordinates.tolist(), [0.0, 1.0])
        self.assertEqual(pd.values.tolist(), [[10.0], [20.0]])

    def test_read_csv_ragged_rows_raise(self):
        """Genuinely ragged data (rows with different column counts) can't form a
        rectangular value matrix, so PairedData.create raises when numpy builds it."""
        content = (
            "Type,TIME,POINTS\n"
            "1,0,1,2\n"      # 2 y-values
            "2,1,3\n"        # 1 y-value
        )
        with self.assertRaises(ValueError):
            self.read_pd_from_string(content)

    def test_read_csv_wrong_cls_raises(self):
        """paired_data_read_csv only builds PairedData; other classes are rejected."""
        with self.assertRaises(TypeError):
            paired_data_read_csv(RegularTimeSeries, "fake.csv")

    # ================================================================== #
    # round trips  (write -> read on a real temp file)
    # ================================================================== #

    def test_round_trip_basic(self):
        path = self.test_files.create_test_file(".csv")
        pd = self.make_pd()
        pd.to_csv(path, with_metadata=True)
        result = PairedData.read_csv(path)

        self.assertEqual(result.ordinates.tolist(), [1.0, 2.0])
        self.assertEqual(result.values.tolist(), [[10.0, 100.0], [20.0, 200.0]])
        self.assertEqual(result.labels, ["L1", "L2"])
        self.assertEqual(result.units_independent, "FEET")
        self.assertEqual(result.units_dependent, "CFS")
        self.assertEqual(result.type_independent, "UNT")
        self.assertEqual(result.type_dependent, "LINEAR")
        # The D (date) part is dropped by the writer, so it comes back empty.
        self.assertEqual(result.id, "/A/B/C//E/F/")

    def test_round_trip_multiple_curves(self):
        path = self.test_files.create_test_file(".csv")
        pd = self.make_pd(
            x_values=[0.0, 1.0, 2.0],
            y_values=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]],
            labels=["a", "b", "c"],
        )
        pd.to_csv(path, with_metadata=True)
        result = PairedData.read_csv(path)

        self.assertEqual(result.curve_count(), 3)
        self.assertEqual(
            result.values.tolist(),
            [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]],
        )
        self.assertEqual(result.labels, ["a", "b", "c"])

    def test_round_trip_without_metadata(self):
        """Without metadata, units/labels/id are lost, but data and (because the
        Type row is written unconditionally) the types survive."""
        path = self.test_files.create_test_file(".csv")
        pd = self.make_pd()
        pd.to_csv(path, with_metadata=False)
        result = PairedData.read_csv(path)

        self.assertEqual(result.ordinates.tolist(), [1.0, 2.0])
        self.assertEqual(result.values.tolist(), [[10.0, 100.0], [20.0, 200.0]])
        self.assertEqual(result.labels, [])
        self.assertEqual(result.units_independent, "")
        self.assertEqual(result.units_dependent, "")
        self.assertEqual(result.id, "///////")
        # Type row is always written, so type survives the no-metadata round trip.
        self.assertEqual(result.type_independent, "UNT")
        self.assertEqual(result.type_dependent, "LINEAR")

    def test_round_trip_rounding(self):
        """Values are rounded to 4 decimals on write, and that rounded value is
        exactly what is read back."""
        path = self.test_files.create_test_file(".csv")
        pd = self.make_pd(x_values=[1.23456], y_values=[[2.34567]], labels=["a"])
        pd.to_csv(path, with_metadata=True)
        result = PairedData.read_csv(path)

        self.assertEqual(result.ordinates.tolist(), [1.2346])
        self.assertEqual(result.values.tolist(), [[2.3457]])

    def test_round_trip_negative_values(self):
        path = self.test_files.create_test_file(".csv")
        pd = self.make_pd(
            x_values=[-1.0, 0.0, 1.0],
            y_values=[[-5.5], [0.0], [5.5]],
            labels=["a"],
        )
        pd.to_csv(path, with_metadata=True)
        result = PairedData.read_csv(path)

        self.assertEqual(result.ordinates.tolist(), [-1.0, 0.0, 1.0])
        self.assertEqual(result.values.tolist(), [[-5.5], [0.0], [5.5]])

    # ================================================================== #
    # weird / adversarial edge cases
    #
    # These probe surprising inputs. Tests that DOCUMENT current behavior
    # (even when that behavior is a footgun) pass; two known bugs are pinned
    # with @unittest.expectedFailure so they stay visible until fixed.
    # ================================================================== #

    def test_read_csv_quoted_label_with_comma_round_trips(self):
        """A label containing a comma is CSV-quoted on write and comes back intact."""
        path = self.test_files.create_test_file(".csv")
        pd = self.make_pd(
            x_values=[1.0], y_values=[[2.0]], labels=["flow, cfs"],
        )
        pd.to_csv(path, with_metadata=True)
        result = PairedData.read_csv(path)
        self.assertEqual(result.labels, ["flow, cfs"])

    def test_read_csv_metadata_after_data_still_applies(self):
        """The reader is order-independent: a Units row placed AFTER the data rows
        still populates the units (nothing forces metadata to come first)."""
        content = (
            "1,0,10\n"
            "Units,DAYS,PPG\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.units_independent, "DAYS")
        self.assertEqual(pd.units_dependent, "PPG")
        self.assertEqual(pd.values.tolist(), [[10.0]])

    def test_read_csv_ignores_counter_column(self):
        """The leading index column is never validated on read - non-sequential or
        even non-numeric counters are ignored entirely (x comes from column 2)."""
        content = (
            "Type,,\n"
            "999,0,10\n"
            "hello,1,20\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.ordinates.tolist(), [0.0, 1.0])
        self.assertEqual(pd.values.tolist(), [[10.0], [20.0]])

    def test_read_csv_duplicate_units_last_wins(self):
        """When a keyword row appears twice, the last occurrence overwrites."""
        content = (
            "Units,AA,BB\n"
            "Units,CC,DD\n"
            "Type,,\n"
            "1,0,10\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.units_independent, "CC")
        self.assertEqual(pd.units_dependent, "DD")

    def test_read_csv_whitespace_only_cells_default_missing(self):
        """Cells that are only whitespace strip to empty and become the default."""
        content = (
            "Type,,\n"
            "1,   ,  \n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.ordinates.tolist(), [DEFAULT_MISSING_VALUE])
        self.assertEqual(pd.values.tolist(), [[DEFAULT_MISSING_VALUE]])

    def test_read_csv_inf_and_nan_parse_through(self):
        """float() accepts 'inf'/'nan', so these land in the array as real inf/NaN
        rather than being treated as missing. Surprising, given the missing-value
        default is 0.0 - documented here so a future change is caught."""
        content = (
            "Type,,\n"
            "1,inf,nan\n"
            "2,-inf,5\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertTrue(math.isinf(pd.ordinates[0]))
        self.assertTrue(math.isnan(pd.values[0][0]))
        self.assertTrue(math.isinf(pd.ordinates[1]) and pd.ordinates[1] < 0)

    def test_read_csv_miscased_keyword_becomes_phantom_data_row(self):
        """FOOTGUN: keyword matching is case-sensitive, so a mis-cased 'units' row
        is not recognized as metadata. It falls through to the data branch, its
        text cells fail to parse, and it is silently injected as a (0.0, [0.0])
        data point instead of raising or being ignored."""
        content = (
            "units,DAYS,PPG\n"   # lowercase -> NOT recognized as a Units row
            "Type,TIME,POINTS\n"
            "1,5,10\n"
        )
        pd = self.read_pd_from_string(content)
        # The real units were never captured...
        self.assertEqual(pd.units_independent, "")
        # ...and a bogus leading data point was manufactured from the keyword row.
        self.assertEqual(pd.ordinates.tolist(), [DEFAULT_MISSING_VALUE, 5.0])
        self.assertEqual(pd.values.tolist(), [[DEFAULT_MISSING_VALUE], [10.0]])

    def test_read_csv_extra_metadata_column_grabs_last_cell(self):
        """FOOTGUN: path parts are read via the 'last cell' convention (row[-1]),
        so a metadata row with an unexpected trailing column captures the trailing
        value instead of the intended one."""
        content = (
            "A,,SITE,EXTRA\n"    # intended A=SITE, but row[-1] is 'EXTRA'
            "Type,,\n"
            "1,0,10\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertIn("EXTRA", pd.id)
        self.assertNotIn("SITE", pd.id)

    def test_curve_count_on_dataless_read_should_be_zero(self):
        """BUG: reading a CSV with metadata but no data rows yields an empty
        PairedData, and curve_count() then does len(self.values[0]) -> IndexError.
        It should return 0. Pinned as expectedFailure until curve_count guards
        against an empty value array."""
        content = (
            "Units,DAYS,PPG\n"
            "Type,TIME,POINTS\n"
        )
        pd = self.read_pd_from_string(content)
        self.assertEqual(pd.curve_count(), 0)

    def test_to_csv_missing_value_does_not_crash(self):
        """A blank/malformed numeric cell is read back as DEFAULT_MISSING_VALUE
        (None), producing an object-dtype array. The writer must tolerate a None
        ordinate/value (write an empty cell) rather than crash trying to round it."""
        pd = self.read_pd_from_string(
            "Type,TIME,POINTS\n"
            "1,,10\n"       # blank ordinate -> None
            "2,2,20\n"
        )
        written = self.write_pd_to_string(pd, with_metadata=True)
        self.assertIn("1,,10.0", written)
        self.assertIn("2,2.0,20.0", written)

    def test_round_trip_nan_value_survives(self):
        """A NaN dependent value is written as 'nan' and read back as a real NaN
        (it is NOT collapsed into the missing-value default)."""
        path = self.test_files.create_test_file(".csv")
        pd = self.make_pd(x_values=[1.0], y_values=[[float("nan")]], labels=["a"])
        pd.to_csv(path, with_metadata=True)
        result = PairedData.read_csv(path)
        self.assertTrue(math.isnan(result.values.tolist()[0][0]))


if __name__ == "__main__":
    unittest.main()
