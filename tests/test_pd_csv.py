import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

from file_manager import FileManager

from hecdss import HecDss
from hecdss.paired_data import PairedData


class TestCSV(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

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

    # def test_temp(self):
    #     file_path: str = "./tests/data/examples-all-data-types.dss"
    #     with HecDss(file_path) as dss:
    #         data_path: str = "/paired-data-multi-column/RIVERDALE/FREQ-FLOW/MAX ANALYTICAL//1969-01 H33(MAX)/"
    #         data: PairedData = dss.get(data_path)
    #         export_path: str = "./tests/csv_testing/paired_data_test.csv"
    #         data.to_csv(export_path)

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


if __name__ == "__main__":
    unittest.main()
